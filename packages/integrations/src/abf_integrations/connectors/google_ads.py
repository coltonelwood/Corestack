"""Google Ads connector — campaign management integration.

Mock mode simulates realistic Google Ads API responses.
"""

from __future__ import annotations

import uuid
from typing import Any

from abf_integrations.base import BaseConnector, ConnectorConfig


class GoogleAdsConnector(BaseConnector):
    name = "google_ads"
    service = "google"

    def __init__(self, config: ConnectorConfig | None = None):
        super().__init__(config)

    SUPPORTED_ACTIONS = {
        "create_campaign", "update_campaign", "pause_campaign",
        "update_budget", "get_performance", "test_connection",
    }

    REQUIRED_FIELDS: dict[str, list[str]] = {
        "create_campaign": ["name", "budget_cents"],
        "update_budget": ["campaign_external_id", "new_budget_cents"],
        "pause_campaign": ["campaign_external_id"],
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
        if action == "create_campaign":
            return {
                "campaign_external_id": f"gads_{uuid.uuid4().hex[:12]}",
                "name": params.get("name"),
                "status": "PAUSED",
                "budget_cents": params.get("budget_cents", 0),
                "platform": "google",
                "mode": "mock",
            }
        if action == "update_budget":
            return {
                "campaign_external_id": params["campaign_external_id"],
                "new_budget_cents": params["new_budget_cents"],
                "mode": "mock",
            }
        if action == "pause_campaign":
            return {
                "campaign_external_id": params["campaign_external_id"],
                "new_status": "PAUSED",
                "mode": "mock",
            }
        return {"action": action, "mode": "mock"}

    async def _execute_live(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(f"Live mode for Google Ads {action} not yet implemented.")
