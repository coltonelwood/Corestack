import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.errors import NotFoundError
from abf_api.models.schemas import ApprovalCreate, ApprovalDecision, ApprovalRead
from abf_api.responses import ok, ok_list
from abf_api.services.audit import log_event

logger = logging.getLogger("abf_api.approvals")

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("")
def list_approvals(
    business_id: str | None = None,
    status: str | None = None,
    db: Client = Depends(get_supabase),
):
    q = db.table("approvals").select("*").order("created_at", desc=True)
    if business_id:
        q = q.eq("business_id", business_id)
    if status:
        q = q.eq("status", status)
    return ok_list(q.execute().data)


@router.get("/{approval_id}")
def get_approval(approval_id: str, db: Client = Depends(get_supabase)):
    res = db.table("approvals").select("*").eq("id", approval_id).maybe_single().execute()
    if res.data is None:
        raise NotFoundError("Approval", approval_id)
    return ok(res.data)


@router.post("", status_code=201)
def create_approval(body: ApprovalCreate, db: Client = Depends(get_supabase)):
    data = body.model_dump(exclude_none=True)
    data["status"] = "pending"
    res = db.table("approvals").insert(data).execute()
    row = res.data[0]
    logger.info("Approval requested: %s (%s)", row["id"], row["type"])
    log_event(
        db,
        actor=row["requested_by"],
        action="request",
        entity_type="approval",
        entity_id=row["id"],
        business_id=row["business_id"],
        diff=data,
    )
    return ok(row)


@router.post("/{approval_id}/approve")
def approve(
    approval_id: str,
    body: ApprovalDecision,
    db: Client = Depends(get_supabase),
):
    now = datetime.now(timezone.utc).isoformat()
    res = (
        db.table("approvals")
        .update({
            "status": "approved",
            "reviewed_by": body.reviewed_by,
            "reviewed_at": now,
        })
        .eq("id", approval_id)
        .eq("status", "pending")
        .execute()
    )
    if not res.data:
        raise NotFoundError("Pending approval", approval_id)
    logger.info("Approval approved: %s by %s", approval_id, body.reviewed_by)
    log_event(
        db,
        actor=body.reviewed_by,
        action="approve",
        entity_type="approval",
        entity_id=approval_id,
        business_id=res.data[0].get("business_id"),
        diff={"status": {"from": "pending", "to": "approved"}},
    )
    return ok(res.data[0])


@router.post("/{approval_id}/reject")
def reject(
    approval_id: str,
    body: ApprovalDecision,
    db: Client = Depends(get_supabase),
):
    now = datetime.now(timezone.utc).isoformat()
    res = (
        db.table("approvals")
        .update({
            "status": "rejected",
            "reviewed_by": body.reviewed_by,
            "reviewed_at": now,
        })
        .eq("id", approval_id)
        .eq("status", "pending")
        .execute()
    )
    if not res.data:
        raise NotFoundError("Pending approval", approval_id)
    logger.info("Approval rejected: %s by %s", approval_id, body.reviewed_by)
    log_event(
        db,
        actor=body.reviewed_by,
        action="reject",
        entity_type="approval",
        entity_id=approval_id,
        business_id=res.data[0].get("business_id"),
        diff={"status": {"from": "pending", "to": "rejected"}},
    )
    return ok(res.data[0])
