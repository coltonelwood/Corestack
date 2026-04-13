"""Structured API response models.

All endpoints return a consistent JSON envelope:
  { "ok": true, "data": ... }
  { "ok": true, "data": [...], "count": N }
  { "ok": false, "error": { "code": "...", "message": "..." } }
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    ok: bool = True
    data: T


class ListResponse(BaseModel, Generic[T]):
    ok: bool = True
    data: list[T]
    count: int


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    ok: bool = False
    error: ErrorDetail


def ok(data: Any) -> dict:
    """Wrap a single item in the standard response envelope."""
    return {"ok": True, "data": data}


def ok_list(data: list, count: int | None = None) -> dict:
    """Wrap a list in the standard response envelope."""
    return {"ok": True, "data": data, "count": count if count is not None else len(data)}
