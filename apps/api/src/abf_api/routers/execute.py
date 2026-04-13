"""Agent execution endpoint.

Accepts a task, runs the appropriate agent, and records the result
in both the agent_runs and tasks tables.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from supabase import Client

from abf_api.deps.supabase import get_supabase

router = APIRouter(prefix="/execute", tags=["execute"])


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


@router.post("", response_model=ExecuteResponse)
async def execute_task(body: ExecuteRequest, db: Client = Depends(get_supabase)):
    # Load the task
    task_res = db.table("tasks").select("*").eq("id", body.task_id).maybe_single().execute()
    if task_res.data is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_res.data
    agent_name = task.get("assigned_agent")
    if not agent_name:
        raise HTTPException(status_code=400, detail="Task has no assigned agent")

    # Map display names to registry keys
    agent_key_map: dict[str, str] = {
        "Content Writer": "content_writer",
        "Research Analyst": "research_analyst",
        "Ads Manager": "ads_manager",
        "Analytics Agent": "analytics",
        "Operations Agent": "operations",
        "Outreach Agent": "outreach",
    }
    agent_key = agent_key_map.get(agent_name, agent_name)

    # Import agents (registers built-in agents on first import)
    import abf_agents.builtin  # noqa: F401
    from abf_agents import get_agent
    from abf_agents.base import AgentContext

    try:
        agent = get_agent(agent_key)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Unknown agent: {agent_name}")

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
    run_id = run_res.data[0]["id"]

    # Execute
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
    task_update = {
        "status": "completed" if result.success else "failed",
        "result": result.output if result.success else {"error": result.error},
        "completed_at": now,
    }
    db.table("tasks").update(task_update).eq("id", body.task_id).execute()

    return ExecuteResponse(
        run_id=run_id,
        success=result.success,
        output=result.output if result.success else None,
        error=result.error,
        tokens_used=result.tokens_used,
        cost_cents=result.cost_cents,
        duration_ms=result.duration_ms,
    )
