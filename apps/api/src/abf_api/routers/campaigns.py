from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.models.schemas import CampaignCreate, CampaignRead, CampaignUpdate

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=list[CampaignRead])
def list_campaigns(
    business_id: str | None = None,
    status: str | None = None,
    db: Client = Depends(get_supabase),
):
    q = db.table("campaigns").select("*").order("created_at", desc=True)
    if business_id:
        q = q.eq("business_id", business_id)
    if status:
        q = q.eq("status", status)
    return q.execute().data


@router.get("/{campaign_id}", response_model=CampaignRead)
def get_campaign(campaign_id: str, db: Client = Depends(get_supabase)):
    res = db.table("campaigns").select("*").eq("id", campaign_id).maybe_single().execute()
    if res.data is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return res.data


@router.post("", response_model=CampaignRead, status_code=201)
def create_campaign(body: CampaignCreate, db: Client = Depends(get_supabase)):
    data = body.model_dump(exclude_none=True)
    data["status"] = "draft"
    res = db.table("campaigns").insert(data).execute()
    return res.data[0]


@router.patch("/{campaign_id}", response_model=CampaignRead)
def update_campaign(
    campaign_id: str,
    body: CampaignUpdate,
    db: Client = Depends(get_supabase),
):
    data = body.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    res = db.table("campaigns").update(data).eq("id", campaign_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return res.data[0]
