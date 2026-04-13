import logging

from fastapi import APIRouter, Depends
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.errors import NotFoundError
from abf_api.models.schemas import CampaignCreate, CampaignRead, CampaignUpdate
from abf_api.responses import ok, ok_list
from abf_api.services.audit import log_event

logger = logging.getLogger("abf_api.campaigns")

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("")
def list_campaigns(
    business_id: str | None = None,
    status: str | None = None,
    channel: str | None = None,
    db: Client = Depends(get_supabase),
):
    q = db.table("campaigns").select("*").order("created_at", desc=True)
    if business_id:
        q = q.eq("business_id", business_id)
    if status:
        q = q.eq("status", status)
    if channel:
        q = q.eq("channel", channel)
    return ok_list(q.execute().data)


@router.get("/{campaign_id}")
def get_campaign(campaign_id: str, db: Client = Depends(get_supabase)):
    res = db.table("campaigns").select("*").eq("id", campaign_id).maybe_single().execute()
    if res.data is None:
        raise NotFoundError("Campaign", campaign_id)
    return ok(res.data)


@router.post("", status_code=201)
def create_campaign(body: CampaignCreate, db: Client = Depends(get_supabase)):
    data = body.model_dump(exclude_none=True)
    data["status"] = "draft"
    res = db.table("campaigns").insert(data).execute()
    row = res.data[0]
    logger.info("Campaign created: %s", row["id"])
    log_event(
        db,
        actor="api",
        action="create",
        entity_type="campaign",
        entity_id=row["id"],
        business_id=row["business_id"],
        diff=data,
    )
    return ok(row)


@router.patch("/{campaign_id}")
def update_campaign(
    campaign_id: str,
    body: CampaignUpdate,
    db: Client = Depends(get_supabase),
):
    data = body.model_dump(exclude_none=True)
    if not data:
        return ok(get_campaign(campaign_id, db)["data"])
    res = db.table("campaigns").update(data).eq("id", campaign_id).execute()
    if not res.data:
        raise NotFoundError("Campaign", campaign_id)
    log_event(
        db,
        actor="api",
        action="update",
        entity_type="campaign",
        entity_id=campaign_id,
        business_id=res.data[0].get("business_id"),
        diff=data,
    )
    return ok(res.data[0])
