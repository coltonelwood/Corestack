"""Workflow endpoints — trigger, monitor, resume workflows.

Provides both the generic workflow trigger (inline steps) and the
specific product launch workflow with persistent DB-backed state.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.errors import ABFError, NotFoundError
from abf_api.responses import ok, ok_list
from abf_api.services.audit import log_event

logger = logging.getLogger("abf_api.workflows")

router = APIRouter(prefix="/workflows", tags=["workflows"])


# ── Schemas ──────────────────────────────────────────────────

class ProductLaunchRequest(BaseModel):
    business_id: str
    product_name: str
    product_description: str = ""
    category: str = ""
    price: str = ""
    target_audience: str = ""
    brand_voice: str = "Professional and approachable"
    channel: str = "meta"
    budget_cents: int = 0
    market_data: str = ""
    our_strengths: str = ""

class CampaignOptRequest(BaseModel):
    business_id: str
    campaign_id: str
    target_cpa_cents: int = 0
    target_roas: float = 0

class ResumeRequest(BaseModel):
    workflow_run_id: str

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


# ═══════════════════════════════════════════════════════════
#  Product Launch Workflow
# ═══════════════════════════════════════════════════════════

@router.post("/product-launch")
async def trigger_product_launch(
    body: ProductLaunchRequest,
    db: Client = Depends(get_supabase),
):
    """Trigger the full product launch workflow.

    Steps: opportunity analysis → decision scoring → generate 4 content assets
    → create campaign draft → risk check (may pause for approval) → finalize.
    """
    from abf_workflows.definitions.product_launch import trigger

    try:
        result = await trigger(db, body.business_id, body.model_dump())
    except Exception as exc:
        logger.exception("Product launch workflow failed: %s", exc)
        raise ABFError(f"Workflow failed: {exc}", status_code=500, code="WORKFLOW_ERROR")

    log_event(
        db,
        actor="api",
        action="workflow_trigger",
        entity_type="workflow",
        entity_id=result.get("workflow_run_id"),
        business_id=body.business_id,
        diff={
            "type": "product_launch",
            "product_name": body.product_name,
            "status": result.get("status"),
        },
    )

    return ok(result)


@router.post("/campaign-optimization")
async def trigger_campaign_optimization(
    body: CampaignOptRequest,
    db: Client = Depends(get_supabase),
):
    """Optimize a running campaign.

    Pulls metrics → analyzes KPIs → AI decides scale/hold/pause/kill
    → validates against guardrails → auto-applies or creates approval.
    """
    from abf_workflows.definitions.campaign_optimization import trigger

    try:
        result = await trigger(db, body.business_id, body.model_dump())
    except Exception as exc:
        logger.exception("Campaign optimization workflow failed: %s", exc)
        raise ABFError(f"Workflow failed: {exc}", status_code=500, code="WORKFLOW_ERROR")

    log_event(
        db,
        actor="api",
        action="workflow_trigger",
        entity_type="workflow",
        entity_id=result.get("workflow_run_id"),
        business_id=body.business_id,
        diff={
            "type": "campaign_optimization",
            "campaign_id": body.campaign_id,
            "status": result.get("status"),
        },
    )

    return ok(result)


@router.post("/resume")
async def resume_workflow(
    body: ResumeRequest,
    db: Client = Depends(get_supabase),
):
    """Resume a paused workflow after its approval has been granted."""
    wf = db.table("workflow_runs").select("workflow_type").eq("id", body.workflow_run_id).maybe_single().execute()
    if not wf.data:
        raise NotFoundError("Workflow run", body.workflow_run_id)

    wf_type = wf.data["workflow_type"]
    resume_fn = None

    if wf_type == "product_launch":
        from abf_workflows.definitions.product_launch import resume
        resume_fn = resume
    elif wf_type == "campaign_optimization":
        from abf_workflows.definitions.campaign_optimization import resume
        resume_fn = resume
    else:
        raise ABFError(f"Unsupported workflow type: {wf_type}", code="UNKNOWN_WORKFLOW")

    try:
        result = await resume_fn(db, body.workflow_run_id)
    except ValueError as exc:
        raise ABFError(str(exc), code="WORKFLOW_RESUME_ERROR")
    except Exception as exc:
        logger.exception("Workflow resume failed: %s", exc)
        raise ABFError(f"Resume failed: {exc}", status_code=500, code="WORKFLOW_ERROR")

    log_event(
        db,
        actor="api",
        action="workflow_resume",
        entity_type="workflow",
        entity_id=body.workflow_run_id,
        diff={"status": result.get("status")},
    )

    return ok(result)


# ═══════════════════════════════════════════════════════════
#  Workflow status and listing
# ═══════════════════════════════════════════════════════════

@router.get("")
def list_workflow_runs(
    business_id: str | None = None,
    status: str | None = None,
    workflow_type: str | None = None,
    db: Client = Depends(get_supabase),
):
    """List all workflow runs with optional filters."""
    q = db.table("workflow_runs").select("*").order("created_at", desc=True)
    if business_id:
        q = q.eq("business_id", business_id)
    if status:
        q = q.eq("status", status)
    if workflow_type:
        q = q.eq("workflow_type", workflow_type)
    return ok_list(q.execute().data)


@router.get("/{workflow_run_id}")
def get_workflow_run(workflow_run_id: str, db: Client = Depends(get_supabase)):
    """Get a workflow run with all its step details."""
    wf = db.table("workflow_runs").select("*").eq("id", workflow_run_id).maybe_single().execute()
    if not wf.data:
        raise NotFoundError("Workflow run", workflow_run_id)

    steps = (
        db.table("workflow_step_runs")
        .select("*")
        .eq("workflow_run_id", workflow_run_id)
        .order("created_at")
        .execute()
    )

    return ok({
        **wf.data,
        "steps": steps.data or [],
    })


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


# ═══════════════════════════════════════════════════════════
#  Generic inline workflow trigger (existing)
# ═══════════════════════════════════════════════════════════

@router.post("/trigger")
async def trigger_inline_workflow(
    body: WorkflowTriggerRequest,
    db: Client = Depends(get_supabase),
):
    """Trigger a generic workflow with inline step definitions."""
    import abf_agents.builtin  # noqa: F401
    from abf_workflows import WorkflowEngine, Workflow, WorkflowStep

    wf_steps = [
        WorkflowStep(
            id=s.id, name=s.name, agent_name=s.agent_name,
            payload=s.payload, depends_on=s.depends_on,
        )
        for s in body.steps
    ]

    workflow = Workflow(
        id="runtime", name=body.name,
        business_id=body.business_id, steps=wf_steps,
    )

    engine = WorkflowEngine(workflow)

    try:
        results = await engine.run()
    except Exception as exc:
        logger.exception("Inline workflow failed: %s", exc)
        raise ABFError(f"Workflow failed: {exc}", status_code=500, code="WORKFLOW_ERROR")

    completed = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    return ok({
        "name": body.name,
        "total_steps": len(wf_steps),
        "completed_steps": len(completed),
        "failed_steps": len(failed),
        "total_tokens": sum(r.tokens_used for r in results),
        "total_cost_cents": sum(r.cost_cents for r in results),
        "steps": [
            {
                "step_id": r.step_id,
                "success": r.success,
                "output": r.output,
                "error": r.error,
                "tokens_used": r.tokens_used,
                "cost_cents": r.cost_cents,
                "duration_ms": r.duration_ms,
            }
            for r in results
        ],
    })
