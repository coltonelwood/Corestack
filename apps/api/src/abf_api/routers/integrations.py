"""Integration endpoints — connections, dispatch, and testing."""

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


# ── Schemas ──────────────────────────────────────────────────

class ConnectionUpdateRequest(BaseModel):
    provider: str
    credential_key: str | None = None
    config: dict[str, Any] | None = None
    enabled: bool | None = None

class DispatchRequest(BaseModel):
    integration: str
    action: str
    params: dict[str, Any] = Field(default_factory=dict)
    business_id: str | None = None

class BatchDispatchRequest(BaseModel):
    payloads: list[DispatchRequest]
    business_id: str | None = None

class TestConnectionRequest(BaseModel):
    provider: str


# ═══════════════════════════════════════════════════════════
#  Connection management
# ═══════════════════════════════════════════════════════════

@router.get("/connections")
def list_connections(db: Client = Depends(get_supabase)):
    """List all integration connections with masked credentials.

    Raw secrets are NEVER included in the response.
    """
    from abf_api.services.credentials import get_all_connections
    connections = get_all_connections(db)
    return ok_list(connections)


@router.put("/connections")
def update_connection(
    body: ConnectionUpdateRequest,
    db: Client = Depends(get_supabase),
):
    """Create or update an integration connection.

    For user-managed providers, pass credential_key to store the secret.
    For env-managed providers (openai, anthropic), only config is updatable.
    The response never includes the raw credential — only masked_key.
    """
    from abf_api.services.credentials import upsert_connection

    try:
        result = upsert_connection(
            db,
            provider=body.provider,
            credential_key=body.credential_key,
            config=body.config,
            enabled=body.enabled,
        )
    except ValueError as exc:
        raise ABFError(str(exc), code="UNKNOWN_PROVIDER")

    log_event(
        db,
        actor="api",
        action="integration_update",
        entity_type="integration",
        diff={"provider": body.provider, "enabled": body.enabled, "config_updated": body.config is not None},
    )

    return ok(result)


@router.post("/connections/test")
async def test_connection(
    body: TestConnectionRequest,
    db: Client = Depends(get_supabase),
):
    """Test connectivity to a provider and update its status."""
    from abf_integrations.dispatcher import get_connector
    from abf_api.services.credentials import mark_test_result

    try:
        connector = get_connector(body.provider)
    except ValueError as exc:
        raise ABFError(str(exc), code="UNKNOWN_INTEGRATION")

    result = await connector.test_connection()

    mark_test_result(db, body.provider, result.success, result.error)

    log_event(
        db,
        actor="api",
        action="integration_test",
        entity_type="integration",
        diff={"provider": body.provider, "success": result.success, "error": result.error},
    )

    return ok({
        "provider": body.provider,
        "success": result.success,
        "error": result.error,
        "mode": result.mode,
    })


@router.delete("/connections/{provider}")
def disable_connection(provider: str, db: Client = Depends(get_supabase)):
    """Disable an integration and clear its credential."""
    db.table("integration_connections").update({
        "enabled": False,
        "credential_key": None,
        "masked_key": "",
        "status": "not_configured",
    }).eq("provider", provider).execute()

    log_event(
        db,
        actor="api",
        action="integration_disable",
        entity_type="integration",
        diff={"provider": provider},
    )

    return ok({"provider": provider, "status": "disabled"})


# ═══════════════════════════════════════════════════════════
#  Dispatch and list (existing)
# ═══════════════════════════════════════════════════════════

@router.get("")
def list_integrations():
    """List all available integration connectors."""
    from abf_integrations.dispatcher import list_connectors
    connectors = list_connectors()
    return ok_list(connectors)


@router.post("/dispatch")
async def dispatch_integration(
    body: DispatchRequest,
    db: Client = Depends(get_supabase),
):
    """Dispatch a single integration action."""
    from abf_integrations.dispatcher import dispatch

    audit_cb = partial(log_event, db, business_id=body.business_id) if body.business_id else None

    result = await dispatch(
        {"integration": body.integration, "action": body.action, "params": body.params},
        audit_cb=audit_cb,
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
