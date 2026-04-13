import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.errors import NotFoundError
from abf_api.models.schemas import AgentRunCreate, AgentRunRead, AgentRunUpdate
from abf_api.responses import ok, ok_list

logger = logging.getLogger("abf_api.agent_runs")

router = APIRouter(prefix="/agent-runs", tags=["agent-runs"])


@router.get("")
def list_agent_runs(
    business_id: str | None = None,
    status: str | None = None,
    agent_type: str | None = None,
    db: Client = Depends(get_supabase),
):
    q = db.table("agent_runs").select("*").order("started_at", desc=True)
    if business_id:
        q = q.eq("business_id", business_id)
    if status:
        q = q.eq("status", status)
    if agent_type:
        q = q.eq("agent_type", agent_type)
    return ok_list(q.execute().data)


@router.get("/{run_id}")
def get_agent_run(run_id: str, db: Client = Depends(get_supabase)):
    res = db.table("agent_runs").select("*").eq("id", run_id).maybe_single().execute()
    if res.data is None:
        raise NotFoundError("AgentRun", run_id)
    return ok(res.data)


@router.post("", status_code=201)
def create_agent_run(body: AgentRunCreate, db: Client = Depends(get_supabase)):
    data = body.model_dump(exclude_none=True)
    data["status"] = "queued"
    res = db.table("agent_runs").insert(data).execute()
    return ok(res.data[0])


@router.patch("/{run_id}")
def update_agent_run(
    run_id: str,
    body: AgentRunUpdate,
    db: Client = Depends(get_supabase),
):
    data = body.model_dump(exclude_none=True)
    if not data:
        return ok(get_agent_run(run_id, db)["data"])
    if data.get("status") in ("completed", "failed"):
        data["completed_at"] = datetime.now(timezone.utc).isoformat()
    res = db.table("agent_runs").update(data).eq("id", run_id).execute()
    if not res.data:
        raise NotFoundError("AgentRun", run_id)
    return ok(res.data[0])
