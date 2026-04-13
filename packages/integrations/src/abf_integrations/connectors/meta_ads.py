"""Meta Ads connector — campaign management integration.

Mock mode simulates realistic Meta Ads API responses.
Live mode will use the Marketing API (to be implemented).
"""

from __future__ import annotations

import uuid
from typing import Any

from abf_integrations.base import BaseConnector, ConnectorConfig


class MetaAdsConnector(BaseConnector):
    name = "meta_ads"
    service = "meta"

    def __init__(self, config: ConnectorConfig | None = None):
        super().__init__(config)
        self._access_token = (self.config.credentials.get("access_token") or "")
        self._ad_account_id = (self.config.credentials.get("ad_account_id") or "")

    SUPPORTED_ACTIONS = {
        "create_campaign", "update_campaign", "pause_campaign",
        "update_budget", "get_insights", "test_connection",
    }

    REQUIRED_FIELDS: dict[str, list[str]] = {
        "create_campaign": ["name", "channel", "budget_cents"],
        "update_campaign": ["campaign_external_id"],
        "pause_campaign": ["campaign_external_id"],
        "update_budget": ["campaign_external_id", "new_budget_cents"],
        "get_insights": ["campaign_external_id"],
    }

    def validate_params(self, action: str, params: dict[str, Any]) -> str | None:
        if action not in self.SUPPORTED_ACTIONS:
            return f"Unsupported action: {action}. Available: {sorted(self.SUPPORTED_ACTIONS)}"
        required = self.REQUIRED_FIELDS.get(action, [])
        missing = [f for f in required if f not in params or params[f] is None]
        if missing:
            return f"Missing required fields for {action}: {missing}"
        return None

    # ── Mock implementations ──────────────────��──────────────

    async def _execute_mock(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        handlers = {
            "create_campaign": self._mock_create_campaign,
            "update_campaign": self._mock_update_campaign,
            "pause_campaign": self._mock_pause_campaign,
            "update_budget": self._mock_update_budget,
            "get_insights": self._mock_get_insights,
            "test_connection": self._mock_test_connection,
        }
        handler = handlers.get(action)
        if handler is None:
            return {"error": f"No mock for action: {action}"}
        return await handler(params)

    async def _mock_test_connection(self, params: dict[str, Any]) -> dict[str, Any]:
        return {"connected": True, "ad_account_id": self._ad_account_id or "act_mock_123", "mode": "mock"}

    async def _mock_create_campaign(self, params: dict[str, Any]) -> dict[str, Any]:
        campaign_id = f"meta_camp_{uuid.uuid4().hex[:12]}"
        return {
            "campaign_external_id": campaign_id,
            "name": params.get("name"),
            "status": "PAUSED",
            "daily_budget_cents": params.get("budget_cents", 0),
            "objective": "CONVERSIONS",
            "platform": "meta",
            "mode": "mock",
        }

    async def _mock_update_campaign(self, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "campaign_external_id": params["campaign_external_id"],
            "updated_fields": [k for k in params if k != "campaign_external_id"],
            "status": "updated",
            "mode": "mock",
        }

    async def _mock_pause_campaign(self, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "campaign_external_id": params["campaign_external_id"],
            "previous_status": "ACTIVE",
            "new_status": "PAUSED",
            "mode": "mock",
        }

    async def _mock_update_budget(self, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "campaign_external_id": params["campaign_external_id"],
            "previous_budget_cents": params.get("current_budget_cents", 0),
            "new_budget_cents": params["new_budget_cents"],
            "change_pct": params.get("budget_change_pct", 0),
            "mode": "mock",
        }

    async def _mock_get_insights(self, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "campaign_external_id": params["campaign_external_id"],
            "impressions": 125000,
            "clicks": 3400,
            "conversions": 210,
            "spend_cents": 78500,
            "ctr": 2.72,
            "cpc_cents": 23,
            "cpa_cents": 374,
            "roas": 3.8,
            "mode": "mock",
        }

    # ── Live implementations (stubs) ─────────��───────────────

    async def _execute_live(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(
            f"Live mode for Meta Ads {action} is not yet implemented. "
            f"Use mock mode or implement the Marketing API call."
        )
