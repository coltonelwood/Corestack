"""Integration dispatcher — routes payloads to the correct connector.

This is the single entry point for all integration calls.
The ExecutionAgent and workflows produce integration payloads;
the dispatcher validates and routes them.

Usage:
    from abf_integrations.dispatcher import dispatch

    result = await dispatch({
        "integration": "meta",
        "action": "create_campaign",
        "params": {"name": "Spring Launch", "budget_cents": 500000},
    })
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

from abf_integrations.base import (
    BaseConnector,
    ConnectorConfig,
    ExecutionResult,
    IntegrationMode,
    AuditCallback,
)
from abf_integrations.connectors.meta_ads import MetaAdsConnector
from abf_integrations.connectors.google_ads import GoogleAdsConnector
from abf_integrations.connectors.shopify import ShopifyConnector
from abf_integrations.connectors.stripe import StripeConnector

logger = logging.getLogger("abf_integrations.dispatcher")


class IntegrationPayload(BaseModel):
    """Standard payload shape produced by agents and workflows."""

    integration: str
    action: str
    params: dict[str, Any] = Field(default_factory=dict)


# ── Connector registry ───────────────────────────────────────

# Channel names map to connector keys (e.g. "meta" → "meta_ads")
CHANNEL_MAP: dict[str, str] = {
    "meta": "meta_ads",
    "facebook": "meta_ads",
    "google": "google_ads",
    "tiktok": "meta_ads",  # TikTok uses Meta connector as placeholder
    "shopify": "shopify",
    "stripe": "stripe",
}

CONNECTOR_CLASSES: dict[str, type[BaseConnector]] = {
    "meta_ads": MetaAdsConnector,
    "google_ads": GoogleAdsConnector,
    "shopify": ShopifyConnector,
    "stripe": StripeConnector,
}

# Cache of instantiated connectors
_instances: dict[str, BaseConnector] = {}


def get_connector(
    name: str,
    config: ConnectorConfig | None = None,
) -> BaseConnector:
    """Get or create a connector instance by name."""
    key = CHANNEL_MAP.get(name, name)

    if key not in _instances or config is not None:
        cls = CONNECTOR_CLASSES.get(key)
        if cls is None:
            raise ValueError(
                f"Unknown integration: {name!r}. "
                f"Available: {sorted(set(CHANNEL_MAP) | set(CONNECTOR_CLASSES))}"
            )
        _instances[key] = cls(config or ConnectorConfig())

    return _instances[key]


def list_connectors() -> list[dict[str, str]]:
    """Return metadata about all available connectors."""
    seen = set()
    result = []
    for cls in CONNECTOR_CLASSES.values():
        if cls.name not in seen:
            seen.add(cls.name)
            result.append({
                "name": cls.name,
                "service": cls.service,
            })
    return result


# ── Dispatch function ──────────────��─────────────────────────

async def dispatch(
    payload: dict[str, Any] | IntegrationPayload,
    *,
    audit_cb: AuditCallback = None,
    config: ConnectorConfig | None = None,
) -> ExecutionResult:
    """Route an integration payload to the correct connector.

    This is the main function the backend calls. It:
      1. Parses the payload
      2. Resolves the connector
      3. Calls execute() with retries and logging
      4. Returns a structured ExecutionResult
    """
    if isinstance(payload, dict):
        payload = IntegrationPayload.model_validate(payload)

    try:
        connector = get_connector(payload.integration, config)
    except ValueError as exc:
        return ExecutionResult(
            success=False,
            action=payload.action,
            connector=payload.integration,
            mode=IntegrationMode.MOCK,
            error=str(exc),
        )

    logger.info(
        "Dispatching %s.%s (mode=%s)",
        connector.name, payload.action, connector.mode.value,
    )

    return await connector.execute(
        payload.action,
        payload.params,
        audit_cb=audit_cb,
    )


async def dispatch_batch(
    payloads: list[dict[str, Any]],
    *,
    audit_cb: AuditCallback = None,
    config: ConnectorConfig | None = None,
) -> list[ExecutionResult]:
    """Dispatch multiple integration payloads and return all results."""
    results = []
    for p in payloads:
        result = await dispatch(p, audit_cb=audit_cb, config=config)
        results.append(result)
    return results
