"""Agent execution endpoint.

Accepts a task, runs the appropriate agent, and records the result
in both the agent_runs and tasks tables. This is the primary way
to trigger agent work — all execution flows through here.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.errors import NotFoundError, ABFError
from abf_api.responses import ok
from abf_api.services.audit import log_event

logger = logging.getLogger("abf_api.execute")

router = APIRouter(prefix="/execute", tags=["execute"])

# Map dashboard display names → registry keys
AGENT_KEY_MAP: dict[str, str] = {
    "Content Writer": "content_writer",
    "Research Analyst": "research_analyst",
    "Ads Manager": "ads_manager",
    "Analytics Agent": "analytics",
    "Operations Agent": "operations",
    "Outreach Agent": "outreach",
    # Core agent layer
    "Opportunity Agent": "opportunity",
    "Decision Agent": "decision",
    "Execution Agent": "execution",
}


class ExecuteRequest(BaseModel):
    task_id: str


class ExecuteResponse(BaseModel):
    run_id: str
    success: bool
    output: dict | None = None
    error: str | None = None
    tokens_used: int = 0
    cost_cents: int = 0
    duration_ms: int = 0


@router.post("")
async def execute_task(body: ExecuteRequest, db: Client = Depends(get_supabase)):
    # Load the task
    task_res = db.table("tasks").select("*").eq("id", body.task_id).maybe_single().execute()
    if task_res.data is None:
        raise NotFoundError("Task", body.task_id)

    task = task_res.data
    agent_name = task.get("assigned_agent")
    if not agent_name:
        raise ABFError("Task has no assigned agent", code="NO_AGENT")

    agent_key = AGENT_KEY_MAP.get(agent_name, agent_name)

    # Import agents (registers built-in agents on first import)
    import abf_agents.builtin  # noqa: F401
    from abf_agents import get_agent
    from abf_agents.base import AgentContext

    try:
        agent = get_agent(agent_key)
    except KeyError:
        raise ABFError(f"Unknown agent: {agent_name}", code="UNKNOWN_AGENT")

    logger.info(
        "Executing task %s via agent %s for business %s",
        body.task_id, agent_name, task["business_id"],
    )

    # Mark task as in-progress
    db.table("tasks").update({"status": "in_progress"}).eq("id", body.task_id).execute()

    # Create agent run record
    run_data = {
        "business_id": task["business_id"],
        "task_id": body.task_id,
        "agent_name": agent_name,
        "agent_type": agent.agent_type,
        "status": "running",
        "input_payload": task.get("payload", {}),
    }
    run_res = db.table("agent_runs").insert(run_data).execute()
    if not run_res.data:
        raise ABFError("Failed to create agent run record", status_code=500, code="DB_ERROR")
    run_id = run_res.data[0]["id"]

    # Execute the agent
    ctx = AgentContext(
        business_id=task["business_id"],
        task_id=body.task_id,
        run_id=run_id,
        payload=task.get("payload", {}),
    )
    result = await agent.run(ctx)

    now = datetime.now(timezone.utc).isoformat()

    # Update agent run
    db.table("agent_runs").update({
        "status": "completed" if result.success else "failed",
        "output_payload": result.output,
        "error_message": result.error,
        "tokens_used": result.tokens_used,
        "cost_cents": result.cost_cents,
        "duration_ms": result.duration_ms,
        "completed_at": now,
    }).eq("id", run_id).execute()

    # Update task
    db.table("tasks").update({
        "status": "completed" if result.success else "failed",
        "result": result.output if result.success else {"error": result.error},
        "completed_at": now,
    }).eq("id", body.task_id).execute()

    # Audit log
    log_event(
        db,
        actor=agent_name,
        action="execute",
        entity_type="task",
        entity_id=body.task_id,
        business_id=task["business_id"],
        diff={
            "run_id": run_id,
            "success": result.success,
            "tokens_used": result.tokens_used,
            "cost_cents": result.cost_cents,
            "duration_ms": result.duration_ms,
        },
    )

    status_word = "succeeded" if result.success else "failed"
    logger.info(
        "Task %s %s (run=%s, tokens=%d, cost=%dc, duration=%dms)",
        body.task_id, status_word, run_id,
        result.tokens_used, result.cost_cents, result.duration_ms,
    )

    return ok(ExecuteResponse(
        run_id=run_id,
        success=result.success,
        output=result.output if result.success else None,
        error=result.error,
        tokens_used=result.tokens_used,
        cost_cents=result.cost_cents,
        duration_ms=result.duration_ms,
    ).model_dump())
