"""Base connector interface for all third-party integrations.

Every external service (Shopify, Stripe, Meta Ads, etc.) should
subclass BaseConnector. The backend's service layer calls connectors;
models and routers never touch external APIs directly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ConnectorResult(BaseModel):
    """Standardised result from any connector call."""

    success: bool
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    raw_response: dict[str, Any] | None = None


class BaseConnector(ABC):
    """Abstract base for external service connectors."""

    name: str = "base"
    service: str = "unknown"

    @abstractmethod
    async def test_connection(self) -> ConnectorResult:
        """Verify credentials and connectivity."""
        ...

    @abstractmethod
    async def execute(self, action: str, params: dict[str, Any]) -> ConnectorResult:
        """Execute a named action with the given parameters."""
        ...
