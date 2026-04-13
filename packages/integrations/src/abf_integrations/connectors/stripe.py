"""Stripe connector — placeholder for payment integration."""

from __future__ import annotations

from typing import Any

from abf_integrations.base import BaseConnector, ConnectorResult


class StripeConnector(BaseConnector):
    name = "stripe"
    service = "stripe"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def test_connection(self) -> ConnectorResult:
        # TODO: GET /v1/balance
        return ConnectorResult(success=True, data={"status": "placeholder"})

    async def execute(self, action: str, params: dict[str, Any]) -> ConnectorResult:
        actions = {
            "get_balance": self._get_balance,
            "list_charges": self._list_charges,
        }
        handler = actions.get(action)
        if handler is None:
            return ConnectorResult(success=False, error=f"Unknown Stripe action: {action}")
        return await handler(params)

    async def _get_balance(self, params: dict[str, Any]) -> ConnectorResult:
        # TODO: Implement Stripe balance retrieval
        return ConnectorResult(success=True, data={"balance_cents": 0, "source": "placeholder"})

    async def _list_charges(self, params: dict[str, Any]) -> ConnectorResult:
        # TODO: Implement Stripe charge listing
        return ConnectorResult(success=True, data={"charges": [], "source": "placeholder"})
