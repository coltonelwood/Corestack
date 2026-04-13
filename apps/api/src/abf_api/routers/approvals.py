from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.models.schemas import (
    ApprovalCreate,
    ApprovalDecision,
    ApprovalRead,
)

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=list[ApprovalRead])
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
    return q.execute().data


@router.get("/{approval_id}", response_model=ApprovalRead)
def get_approval(approval_id: str, db: Client = Depends(get_supabase)):
    res = db.table("approvals").select("*").eq("id", approval_id).maybe_single().execute()
    if res.data is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    return res.data


@router.post("", response_model=ApprovalRead, status_code=201)
def create_approval(body: ApprovalCreate, db: Client = Depends(get_supabase)):
    data = body.model_dump(exclude_none=True)
    data["status"] = "pending"
    res = db.table("approvals").insert(data).execute()
    return res.data[0]


@router.post("/{approval_id}/approve", response_model=ApprovalRead)
def approve(
    approval_id: str,
    body: ApprovalDecision,
    db: Client = Depends(get_supabase),
):
    res = (
        db.table("approvals")
        .update({
            "status": "approved",
            "reviewed_by": body.reviewed_by,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        })
        .eq("id", approval_id)
        .eq("status", "pending")
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Pending approval not found")
    return res.data[0]


@router.post("/{approval_id}/reject", response_model=ApprovalRead)
def reject(
    approval_id: str,
    body: ApprovalDecision,
    db: Client = Depends(get_supabase),
):
    res = (
        db.table("approvals")
        .update({
            "status": "rejected",
            "reviewed_by": body.reviewed_by,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        })
        .eq("id", approval_id)
        .eq("status", "pending")
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Pending approval not found")
    return res.data[0]
