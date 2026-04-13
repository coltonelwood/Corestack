"""Shopify connector — placeholder for e-commerce integration.

This is a scaffold. Implement methods as the Shopify integration
is built out.
"""

from __future__ import annotations

from typing import Any

from abf_integrations.base import BaseConnector, ConnectorResult


class ShopifyConnector(BaseConnector):
    name = "shopify"
    service = "shopify"

    def __init__(self, shop_url: str, access_token: str):
        self.shop_url = shop_url
        self.access_token = access_token

    async def test_connection(self) -> ConnectorResult:
        # TODO: GET /admin/api/2024-01/shop.json
        return ConnectorResult(
            success=True,
            data={"shop_url": self.shop_url, "status": "placeholder"},
        )

    async def execute(self, action: str, params: dict[str, Any]) -> ConnectorResult:
        actions = {
            "list_products": self._list_products,
            "create_product": self._create_product,
            "update_inventory": self._update_inventory,
        }
        handler = actions.get(action)
        if handler is None:
            return ConnectorResult(
                success=False,
                error=f"Unknown Shopify action: {action}",
            )
        return await handler(params)

    async def _list_products(self, params: dict[str, Any]) -> ConnectorResult:
        # TODO: Implement Shopify product listing
        return ConnectorResult(success=True, data={"products": [], "source": "placeholder"})

    async def _create_product(self, params: dict[str, Any]) -> ConnectorResult:
        # TODO: Implement Shopify product creation
        return ConnectorResult(success=True, data={"product_id": None, "source": "placeholder"})

    async def _update_inventory(self, params: dict[str, Any]) -> ConnectorResult:
        # TODO: Implement Shopify inventory update
        return ConnectorResult(success=True, data={"updated": False, "source": "placeholder"})
