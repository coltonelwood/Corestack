import logging

from fastapi import APIRouter, Depends
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.errors import NotFoundError
from abf_api.models.schemas import ProductCreate, ProductRead, ProductUpdate
from abf_api.responses import ok, ok_list
from abf_api.services.audit import log_event

logger = logging.getLogger("abf_api.products")

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
def list_products(
    business_id: str | None = None,
    status: str | None = None,
    db: Client = Depends(get_supabase),
):
    q = db.table("products").select("*").order("created_at", desc=True)
    if business_id:
        q = q.eq("business_id", business_id)
    if status:
        q = q.eq("status", status)
    return ok_list(q.execute().data)


@router.get("/{product_id}")
def get_product(product_id: str, db: Client = Depends(get_supabase)):
    res = db.table("products").select("*").eq("id", product_id).maybe_single().execute()
    if res.data is None:
        raise NotFoundError("Product", product_id)
    return ok(res.data)


@router.post("", status_code=201)
def create_product(body: ProductCreate, db: Client = Depends(get_supabase)):
    data = body.model_dump(exclude_none=True)
    data["status"] = "draft"
    res = db.table("products").insert(data).execute()
    row = res.data[0]
    logger.info("Product created: %s", row["id"])
    log_event(
        db,
        actor="api",
        action="create",
        entity_type="product",
        entity_id=row["id"],
        business_id=row["business_id"],
        diff=data,
    )
    return ok(row)


@router.patch("/{product_id}")
def update_product(
    product_id: str,
    body: ProductUpdate,
    db: Client = Depends(get_supabase),
):
    data = body.model_dump(exclude_none=True)
    if not data:
        return ok(get_product(product_id, db)["data"])
    res = db.table("products").update(data).eq("id", product_id).execute()
    if not res.data:
        raise NotFoundError("Product", product_id)
    log_event(
        db,
        actor="api",
        action="update",
        entity_type="product",
        entity_id=product_id,
        business_id=res.data[0].get("business_id"),
        diff=data,
    )
    return ok(res.data[0])


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: str, db: Client = Depends(get_supabase)):
    db.table("products").delete().eq("id", product_id).execute()
    log_event(db, actor="api", action="delete", entity_type="product", entity_id=product_id)
