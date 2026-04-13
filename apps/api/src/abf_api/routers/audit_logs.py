from fastapi import APIRouter, Depends
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.models.schemas import AuditLogCreate, AuditLogRead

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=list[AuditLogRead])
def list_audit_logs(
    business_id: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    limit: int = 50,
    db: Client = Depends(get_supabase),
):
    q = db.table("audit_logs").select("*").order("created_at", desc=True).limit(limit)
    if business_id:
        q = q.eq("business_id", business_id)
    if entity_type:
        q = q.eq("entity_type", entity_type)
    if entity_id:
        q = q.eq("entity_id", entity_id)
    return q.execute().data


@router.post("", response_model=AuditLogRead, status_code=201)
def create_audit_log(body: AuditLogCreate, db: Client = Depends(get_supabase)):
    data = body.model_dump(exclude_none=True)
    res = db.table("audit_logs").insert(data).execute()
    return res.data[0]
