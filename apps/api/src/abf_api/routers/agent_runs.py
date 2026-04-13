from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.models.schemas import AgentRunCreate, AgentRunRead, AgentRunUpdate

router = APIRouter(prefix="/agent-runs", tags=["agent-runs"])


@router.get("", response_model=list[AgentRunRead])
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
    return q.execute().data


@router.get("/{run_id}", response_model=AgentRunRead)
def get_agent_run(run_id: str, db: Client = Depends(get_supabase)):
    res = db.table("agent_runs").select("*").eq("id", run_id).maybe_single().execute()
    if res.data is None:
        raise HTTPException(status_code=404, detail="Agent run not found")
    return res.data


@router.post("", response_model=AgentRunRead, status_code=201)
def create_agent_run(body: AgentRunCreate, db: Client = Depends(get_supabase)):
    data = body.model_dump(exclude_none=True)
    data["status"] = "queued"
    res = db.table("agent_runs").insert(data).execute()
    return res.data[0]


@router.patch("/{run_id}", response_model=AgentRunRead)
def update_agent_run(
    run_id: str,
    body: AgentRunUpdate,
    db: Client = Depends(get_supabase),
):
    data = body.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    if data.get("status") in ("completed", "failed"):
        data["completed_at"] = datetime.now(timezone.utc).isoformat()
    res = db.table("agent_runs").update(data).eq("id", run_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Agent run not found")
    return res.data[0]
