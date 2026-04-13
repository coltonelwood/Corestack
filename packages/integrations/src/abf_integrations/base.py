"""Base integration infrastructure.

Every external service connector inherits from BaseConnector.
Key design rules:
  - Models and routers never call connectors directly
  - The backend validates payloads before calling execute()
  - Every call is logged via the audit callback
  - Failed calls are retried with exponential backoff
  - Mock mode lets the system simulate actions safely
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from pydantic import BaseModel, Field

logger = logging.getLogger("abf_integrations")


class IntegrationMode(str, Enum):
    MOCK = "mock"
    LIVE = "live"


class ExecutionResult(BaseModel):
    """Structured result from every integration call."""

    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    success: bool
    action: str
    connector: str
    mode: IntegrationMode
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    retries: int = 0
    duration_ms: int = 0
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ConnectorConfig(BaseModel):
    """Configuration for a connector instance."""

    mode: IntegrationMode = IntegrationMode.MOCK
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout_seconds: float = 30.0
    credentials: dict[str, str] = Field(default_factory=dict)


# Type for the optional audit callback
AuditCallback = Callable[..., None] | None


class BaseConnector(ABC):
    """Abstract base for all external service connectors.

    Subclass and implement:
      - _execute_live(action, params) — real API call
      - _execute_mock(action, params) — simulated response
      - validate_params(action, params) — payload validation
    """

    name: str = "base"
    service: str = "unknown"

    def __init__(self, config: ConnectorConfig | None = None):
        self.config = config or ConnectorConfig()

    @property
    def mode(self) -> IntegrationMode:
        return self.config.mode

    @property
    def is_mock(self) -> bool:
        return self.config.mode == IntegrationMode.MOCK

    # ── Public API ──────────────────────────────���────────────

    async def execute(
        self,
        action: str,
        params: dict[str, Any],
        *,
        audit_cb: AuditCallback = None,
    ) -> ExecutionResult:
        """Execute an action with validation, retries, and logging.

        This is the only method external code should call.
        """
        # Validate
        validation_error = self.validate_params(action, params)
        if validation_error:
            result = ExecutionResult(
                success=False,
                action=action,
                connector=self.name,
                mode=self.config.mode,
                error=f"Validation failed: {validation_error}",
            )
            self._log_result(result, audit_cb)
            return result

        # Execute with retries
        last_error: str | None = None
        retries = 0
        start = time.perf_counter()

        for attempt in range(self.config.max_retries):
            retries = attempt
            start = time.perf_counter()

            try:
                if self.is_mock:
                    data = await self._execute_mock(action, params)
                else:
                    data = await asyncio.wait_for(
                        self._execute_live(action, params),
                        timeout=self.config.timeout_seconds,
                    )

                duration = int((time.perf_counter() - start) * 1000)

                result = ExecutionResult(
                    success=True,
                    action=action,
                    connector=self.name,
                    mode=self.config.mode,
                    data=data,
                    retries=attempt,
                    duration_ms=duration,
                )
                self._log_result(result, audit_cb)
                return result

            except asyncio.TimeoutError:
                last_error = f"Timeout after {self.config.timeout_seconds}s"
                logger.warning(
                    "%s.%s attempt %d/%d timed out",
                    self.name, action, attempt + 1, self.config.max_retries,
                )
            except Exception as exc:
                last_error = str(exc)
                logger.warning(
                    "%s.%s attempt %d/%d failed: %s",
                    self.name, action, attempt + 1, self.config.max_retries, exc,
                )

            # Backoff before retry
            if attempt < self.config.max_retries - 1:
                delay = self.config.retry_delay * (2**attempt)
                await asyncio.sleep(delay)

        # All retries exhausted
        duration = int((time.perf_counter() - start) * 1000)
        result = ExecutionResult(
            success=False,
            action=action,
            connector=self.name,
            mode=self.config.mode,
            error=last_error,
            retries=retries,
            duration_ms=duration,
        )
        self._log_result(result, audit_cb)
        return result

    async def test_connection(self) -> ExecutionResult:
        """Verify credentials and connectivity."""
        return await self.execute("test_connection", {})

    # ── Override these ───────────────────────────────────────

    def validate_params(self, action: str, params: dict[str, Any]) -> str | None:
        """Return an error string if params are invalid, None if OK.

        Override in subclasses for action-specific validation.
        """
        return None

    @abstractmethod
    async def _execute_live(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """Real API call. Override in subclasses."""
        ...

    @abstractmethod
    async def _execute_mock(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """Simulated response. Override in subclasses."""
        ...

    # ── Internal ───────────────────────────────────────────���─

    def _log_result(self, result: ExecutionResult, audit_cb: AuditCallback) -> None:
        status = "succeeded" if result.success else "failed"
        logger.info(
            "Integration %s.%s %s (mode=%s, retries=%d, duration=%dms)",
            result.connector, result.action, status,
            result.mode.value, result.retries, result.duration_ms,
        )

        if audit_cb:
            try:
                audit_cb(
                    actor=f"integration:{self.name}",
                    action=f"integration:{result.action}",
                    entity_type="integration",
                    diff={
                        "connector": result.connector,
                        "action": result.action,
                        "mode": result.mode.value,
                        "success": result.success,
                        "error": result.error,
                        "retries": result.retries,
                        "duration_ms": result.duration_ms,
                        "execution_id": result.execution_id,
                    },
                )
            except Exception:
                logger.exception("Failed to write integration audit log")
