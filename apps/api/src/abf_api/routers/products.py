from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.models.schemas import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
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
    return q.execute().data


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: str, db: Client = Depends(get_supabase)):
    res = db.table("products").select("*").eq("id", product_id).maybe_single().execute()
    if res.data is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return res.data


@router.post("", response_model=ProductRead, status_code=201)
def create_product(body: ProductCreate, db: Client = Depends(get_supabase)):
    data = body.model_dump(exclude_none=True)
    data["status"] = "draft"
    res = db.table("products").insert(data).execute()
    return res.data[0]


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: str,
    body: ProductUpdate,
    db: Client = Depends(get_supabase),
):
    data = body.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    res = db.table("products").update(data).eq("id", product_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Product not found")
    return res.data[0]


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: str, db: Client = Depends(get_supabase)):
    db.table("products").delete().eq("id", product_id).execute()
