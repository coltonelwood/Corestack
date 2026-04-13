from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.models.schemas import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
def list_tasks(
    business_id: str | None = None,
    status: str | None = None,
    assigned_agent: str | None = None,
    db: Client = Depends(get_supabase),
):
    q = db.table("tasks").select("*").order("created_at", desc=True)
    if business_id:
        q = q.eq("business_id", business_id)
    if status:
        q = q.eq("status", status)
    if assigned_agent:
        q = q.eq("assigned_agent", assigned_agent)
    return q.execute().data


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: str, db: Client = Depends(get_supabase)):
    res = db.table("tasks").select("*").eq("id", task_id).maybe_single().execute()
    if res.data is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return res.data


@router.post("", response_model=TaskRead, status_code=201)
def create_task(body: TaskCreate, db: Client = Depends(get_supabase)):
    data = body.model_dump(exclude_none=True)
    data["status"] = "pending"
    res = db.table("tasks").insert(data).execute()
    return res.data[0]


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: str,
    body: TaskUpdate,
    db: Client = Depends(get_supabase),
):
    data = body.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    # Auto-set completed_at when marking complete or failed
    if data.get("status") in ("completed", "failed"):
        data["completed_at"] = datetime.now(timezone.utc).isoformat()
    res = db.table("tasks").update(data).eq("id", task_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return res.data[0]
