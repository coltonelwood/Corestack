"""Workflow endpoints — define, trigger, and monitor workflows.

Workflows are DAGs of agent steps. The backend orchestrates execution,
records results per step, and returns a consolidated summary.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.errors import ABFError
from abf_api.responses import ok, ok_list
from abf_api.services.audit import log_event

logger = logging.getLogger("abf_api.workflows")

router = APIRouter(prefix="/workflows", tags=["workflows"])


# ── Schemas ──────────────────────────────────────────────────

class WorkflowStepInput(BaseModel):
    id: str
    name: str
    agent_name: str
    payload: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)

class WorkflowTriggerRequest(BaseModel):
    name: str
    business_id: str
    steps: list[WorkflowStepInput]

class StepResultResponse(BaseModel):
    step_id: str
    success: bool
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    tokens_used: int = 0
    cost_cents: int = 0
    duration_ms: int = 0

class WorkflowResultResponse(BaseModel):
    name: str
    business_id: str
    total_steps: int
    completed_steps: int
    failed_steps: int
    total_tokens: int
    total_cost_cents: int
    total_duration_ms: int
    steps: list[StepResultResponse]


# ── Endpoints ────────────────────────────────────────────────

@router.post("/trigger")
async def trigger_workflow(
    body: WorkflowTriggerRequest,
    db: Client = Depends(get_supabase),
):
    """Trigger a workflow: define steps inline and execute immediately."""
    # Import here to avoid circular deps and lazy-load agent registry
    import abf_agents.builtin  # noqa: F401
    from abf_workflows import WorkflowEngine, Workflow, WorkflowStep

    wf_steps = [
        WorkflowStep(
            id=s.id,
            name=s.name,
            agent_name=s.agent_name,
            payload=s.payload,
            depends_on=s.depends_on,
        )
        for s in body.steps
    ]

    workflow = Workflow(
        id="runtime",
        name=body.name,
        business_id=body.business_id,
        steps=wf_steps,
    )

    logger.info(
        "Workflow triggered: %s (%d steps) for business %s",
        body.name, len(wf_steps), body.business_id,
    )

    engine = WorkflowEngine(workflow)

    try:
        results = await engine.run()
    except Exception as exc:
        logger.exception("Workflow execution failed: %s", exc)
        raise ABFError(f"Workflow failed: {exc}", status_code=500, code="WORKFLOW_ERROR")

    completed = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    response = WorkflowResultResponse(
        name=body.name,
        business_id=body.business_id,
        total_steps=len(wf_steps),
        completed_steps=len(completed),
        failed_steps=len(failed),
        total_tokens=sum(r.tokens_used for r in results),
        total_cost_cents=sum(r.cost_cents for r in results),
        total_duration_ms=sum(r.duration_ms for r in results),
        steps=[
            StepResultResponse(
                step_id=r.step_id,
                success=r.success,
                output=r.output,
                error=r.error,
                tokens_used=r.tokens_used,
                cost_cents=r.cost_cents,
                duration_ms=r.duration_ms,
            )
            for r in results
        ],
    )

    log_event(
        db,
        actor="api",
        action="workflow_trigger",
        entity_type="workflow",
        business_id=body.business_id,
        diff={
            "name": body.name,
            "total_steps": len(wf_steps),
            "completed": len(completed),
            "failed": len(failed),
            "total_tokens": response.total_tokens,
            "total_cost_cents": response.total_cost_cents,
        },
    )

    logger.info(
        "Workflow completed: %s — %d/%d steps succeeded (tokens=%d, cost=%dc)",
        body.name, len(completed), len(wf_steps),
        response.total_tokens, response.total_cost_cents,
    )

    return ok(response.model_dump())


@router.get("/agents")
def list_available_agents():
    """List all registered agents available for workflow steps."""
    import abf_agents.builtin  # noqa: F401
    from abf_agents import registry

    agents = registry()
    return ok_list([
        {
            "name": cls.name,
            "type": cls.agent_type,
            "description": cls.description,
        }
        for cls in agents.values()
    ])
