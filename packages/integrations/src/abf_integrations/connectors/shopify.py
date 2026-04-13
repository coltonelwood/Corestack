"""Shopify connector — e-commerce integration.

Mock mode simulates realistic Shopify Admin API responses.
"""

from __future__ import annotations

import uuid
from typing import Any

from abf_integrations.base import BaseConnector, ConnectorConfig


class ShopifyConnector(BaseConnector):
    name = "shopify"
    service = "shopify"

    def __init__(self, config: ConnectorConfig | None = None):
        super().__init__(config)

    SUPPORTED_ACTIONS = {
        "create_product", "update_product", "update_inventory",
        "list_products", "test_connection",
    }

    REQUIRED_FIELDS: dict[str, list[str]] = {
        "create_product": ["name"],
        "update_product": ["product_external_id"],
        "update_inventory": ["product_external_id", "quantity"],
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
            return {"connected": True, "shop": "mock-shop.myshopify.com", "mode": "mock"}
        if action == "create_product":
            return {
                "product_external_id": f"shopify_prod_{uuid.uuid4().hex[:12]}",
                "name": params.get("name"),
                "status": "draft",
                "mode": "mock",
            }
        if action == "update_inventory":
            return {
                "product_external_id": params["product_external_id"],
                "new_quantity": params["quantity"],
                "mode": "mock",
            }
        if action == "list_products":
            return {"products": [], "total": 0, "mode": "mock"}
        return {"action": action, "mode": "mock"}

    async def _execute_live(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(f"Live mode for Shopify {action} not yet implemented.")
