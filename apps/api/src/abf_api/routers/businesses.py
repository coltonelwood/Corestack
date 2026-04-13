import logging

from fastapi import APIRouter, Depends
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.errors import NotFoundError
from abf_api.models.schemas import BusinessCreate, BusinessRead, BusinessUpdate
from abf_api.responses import ok, ok_list
from abf_api.services.audit import log_event

logger = logging.getLogger("abf_api.businesses")

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.get("")
def list_businesses(
    status: str | None = None,
    db: Client = Depends(get_supabase),
):
    q = db.table("businesses").select("*").order("created_at", desc=True)
    if status:
        q = q.eq("status", status)
    return ok_list(q.execute().data)


@router.get("/{business_id}")
def get_business(business_id: str, db: Client = Depends(get_supabase)):
    res = db.table("businesses").select("*").eq("id", business_id).maybe_single().execute()
    if res.data is None:
        raise NotFoundError("Business", business_id)
    return ok(res.data)


@router.post("", status_code=201)
def create_business(body: BusinessCreate, db: Client = Depends(get_supabase)):
    data = body.model_dump(exclude_none=True)
    data["status"] = "setup"
    res = db.table("businesses").insert(data).execute()
    row = res.data[0]
    logger.info("Business created: %s", row["id"])
    log_event(
        db, actor="api", action="create", entity_type="business",
        entity_id=row["id"], business_id=row["id"], diff=data,
    )
    return ok(row)


@router.patch("/{business_id}")
def update_business(
    business_id: str,
    body: BusinessUpdate,
    db: Client = Depends(get_supabase),
):
    data = body.model_dump(exclude_none=True)
    if not data:
        return get_business(business_id, db)
    res = db.table("businesses").update(data).eq("id", business_id).execute()
    if not res.data:
        raise NotFoundError("Business", business_id)
    log_event(
        db, actor="api", action="update", entity_type="business",
        entity_id=business_id, business_id=business_id, diff=data,
    )
    return ok(res.data[0])


@router.delete("/{business_id}", status_code=204)
def delete_business(business_id: str, db: Client = Depends(get_supabase)):
    db.table("businesses").delete().eq("id", business_id).execute()
    log_event(
        db, actor="api", action="delete", entity_type="business",
        entity_id=business_id, business_id=business_id,
    )
