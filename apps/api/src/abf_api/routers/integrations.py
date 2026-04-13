"""Integration endpoints — dispatch, test, and list connectors."""

import logging
from typing import Any
from functools import partial

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.errors import ABFError
from abf_api.responses import ok, ok_list
from abf_api.services.audit import log_event

logger = logging.getLogger("abf_api.integrations")

router = APIRouter(prefix="/integrations", tags=["integrations"])


class DispatchRequest(BaseModel):
    integration: str
    action: str
    params: dict[str, Any] = Field(default_factory=dict)
    business_id: str | None = None

class BatchDispatchRequest(BaseModel):
    payloads: list[DispatchRequest]
    business_id: str | None = None

class TestConnectionRequest(BaseModel):
    integration: str


@router.post("/dispatch")
async def dispatch_integration(
    body: DispatchRequest,
    db: Client = Depends(get_supabase),
):
    """Dispatch a single integration action.

    All integration calls flow through this endpoint. The dispatcher
    validates the payload, routes to the correct connector, retries
    on failure, and logs everything.
    """
    from abf_integrations.dispatcher import dispatch

    audit_cb = partial(log_event, db, business_id=body.business_id) if body.business_id else None

    result = await dispatch(
        {"integration": body.integration, "action": body.action, "params": body.params},
        audit_cb=audit_cb,
    )

    if not result.success:
        logger.warning(
            "Integration dispatch failed: %s.%s → %s",
            body.integration, body.action, result.error,
        )

    return ok(result.model_dump())


@router.post("/dispatch/batch")
async def dispatch_batch(
    body: BatchDispatchRequest,
    db: Client = Depends(get_supabase),
):
    """Dispatch multiple integration actions in sequence."""
    from abf_integrations.dispatcher import dispatch

    audit_cb = partial(log_event, db, business_id=body.business_id) if body.business_id else None

    results = []
    for payload in body.payloads:
        result = await dispatch(
            {"integration": payload.integration, "action": payload.action, "params": payload.params},
            audit_cb=audit_cb,
        )
        results.append(result.model_dump())

    succeeded = sum(1 for r in results if r["success"])
    failed = len(results) - succeeded

    return ok({
        "total": len(results),
        "succeeded": succeeded,
        "failed": failed,
        "results": results,
    })


@router.post("/test")
async def test_connection(body: TestConnectionRequest):
    """Test connectivity to an integration service."""
    from abf_integrations.dispatcher import get_connector

    try:
        connector = get_connector(body.integration)
    except ValueError as exc:
        raise ABFError(str(exc), code="UNKNOWN_INTEGRATION")

    result = await connector.test_connection()
    return ok(result.model_dump())


@router.get("")
def list_integrations():
    """List all available integration connectors."""
    from abf_integrations.dispatcher import list_connectors

    connectors = list_connectors()
    return ok_list(connectors)
