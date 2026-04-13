"""Stripe connector — payment integration.

Mock mode simulates realistic Stripe API responses.
"""

from __future__ import annotations

import uuid
from typing import Any

from abf_integrations.base import BaseConnector, ConnectorConfig


class StripeConnector(BaseConnector):
    name = "stripe"
    service = "stripe"

    def __init__(self, config: ConnectorConfig | None = None):
        super().__init__(config)

    SUPPORTED_ACTIONS = {"get_balance", "list_charges", "create_refund", "test_connection"}

    REQUIRED_FIELDS: dict[str, list[str]] = {
        "create_refund": ["charge_id", "amount_cents"],
    }

    def validate_params(self, action: str, params: dict[str, Any]) -> str | None:
        if action not in self.SUPPORTED_ACTIONS:
            return f"Unsupported action: {action}"
        required = self.REQUIRED_FIELDS.get(action, [])
        missing = [f for f in required if f not in params or params[f] is None]
        if missing:
            return f"Missing required fields for {action}: {missing}"
        return None

    async def _execute_mock(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        if action == "test_connection":
            return {"connected": True, "mode": "mock"}
        if action == "get_balance":
            return {"available_cents": 2845000, "pending_cents": 48200, "currency": "usd", "mode": "mock"}
        if action == "list_charges":
            return {"charges": [], "has_more": False, "mode": "mock"}
        if action == "create_refund":
            return {
                "refund_id": f"re_{uuid.uuid4().hex[:16]}",
                "charge_id": params["charge_id"],
                "amount_cents": params["amount_cents"],
                "status": "succeeded",
                "mode": "mock",
            }
        return {"action": action, "mode": "mock"}

    async def _execute_live(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(f"Live mode for Stripe {action} not yet implemented.")
