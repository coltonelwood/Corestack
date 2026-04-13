from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.models.schemas import BusinessCreate, BusinessRead, BusinessUpdate

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.get("", response_model=list[BusinessRead])
def list_businesses(
    status: str | None = None,
    db: Client = Depends(get_supabase),
):
    q = db.table("businesses").select("*").order("created_at", desc=True)
    if status:
        q = q.eq("status", status)
    return q.execute().data


@router.get("/{business_id}", response_model=BusinessRead)
def get_business(business_id: str, db: Client = Depends(get_supabase)):
    res = db.table("businesses").select("*").eq("id", business_id).maybe_single().execute()
    if res.data is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return res.data


@router.post("", response_model=BusinessRead, status_code=201)
def create_business(body: BusinessCreate, db: Client = Depends(get_supabase)):
    data = body.model_dump(exclude_none=True)
    data["status"] = "setup"
    res = db.table("businesses").insert(data).execute()
    return res.data[0]


@router.patch("/{business_id}", response_model=BusinessRead)
def update_business(
    business_id: str,
    body: BusinessUpdate,
    db: Client = Depends(get_supabase),
):
    data = body.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    res = db.table("businesses").update(data).eq("id", business_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Business not found")
    return res.data[0]


@router.delete("/{business_id}", status_code=204)
def delete_business(business_id: str, db: Client = Depends(get_supabase)):
    db.table("businesses").delete().eq("id", business_id).execute()
