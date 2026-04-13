import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.errors import NotFoundError
from abf_api.models.schemas import TaskCreate, TaskRead, TaskUpdate
from abf_api.responses import ok, ok_list
from abf_api.services.audit import log_event

logger = logging.getLogger("abf_api.tasks")

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("")
def list_tasks(
    business_id: str | None = None,
    status: str | None = None,
    assigned_agent: str | None = None,
    priority: str | None = None,
    db: Client = Depends(get_supabase),
):
    q = db.table("tasks").select("*").order("created_at", desc=True)
    if business_id:
        q = q.eq("business_id", business_id)
    if status:
        q = q.eq("status", status)
    if assigned_agent:
        q = q.eq("assigned_agent", assigned_agent)
    if priority:
        q = q.eq("priority", priority)
    return ok_list(q.execute().data)


@router.get("/{task_id}")
def get_task(task_id: str, db: Client = Depends(get_supabase)):
    res = db.table("tasks").select("*").eq("id", task_id).maybe_single().execute()
    if res.data is None:
        raise NotFoundError("Task", task_id)
    return ok(res.data)


@router.post("", status_code=201)
def create_task(body: TaskCreate, db: Client = Depends(get_supabase)):
    data = body.model_dump(exclude_none=True)
    data["status"] = "pending"
    res = db.table("tasks").insert(data).execute()
    row = res.data[0]
    logger.info("Task created: %s (agent=%s)", row["id"], row.get("assigned_agent"))
    log_event(
        db,
        actor="api",
        action="create",
        entity_type="task",
        entity_id=row["id"],
        business_id=row["business_id"],
        diff=data,
    )
    return ok(row)


@router.patch("/{task_id}")
def update_task(
    task_id: str,
    body: TaskUpdate,
    db: Client = Depends(get_supabase),
):
    data = body.model_dump(exclude_none=True)
    if not data:
        return ok(get_task(task_id, db)["data"])
    # Auto-set completed_at when marking complete or failed
    if data.get("status") in ("completed", "failed"):
        data["completed_at"] = datetime.now(timezone.utc).isoformat()
    res = db.table("tasks").update(data).eq("id", task_id).execute()
    if not res.data:
        raise NotFoundError("Task", task_id)
    log_event(
        db,
        actor="api",
        action="update",
        entity_type="task",
        entity_id=task_id,
        business_id=res.data[0].get("business_id"),
        diff=data,
    )
    return ok(res.data[0])
