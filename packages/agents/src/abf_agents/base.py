"""Base agent class and execution context."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    """Runtime context passed to every agent execution."""

    business_id: str
    task_id: str | None = None
    run_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel):
    """Standardised result from an agent execution."""

    success: bool
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    tokens_used: int = 0
    cost_cents: int = 0
    duration_ms: int = 0


class BaseAgent(ABC):
    """Abstract base class for all ABF agents.

    Subclass this and implement `execute` to create a new agent type.
    The runner handles timing, error capture, and result normalisation.
    """

    name: str = "base"
    agent_type: str = "operations"
    description: str = ""

    async def run(self, ctx: AgentContext) -> AgentResult:
        """Execute the agent with timing and error handling."""
        start = time.perf_counter()
        try:
            result = await self.execute(ctx)
            result.duration_ms = int((time.perf_counter() - start) * 1000)
            result.success = True
            return result
        except Exception as exc:
            duration = int((time.perf_counter() - start) * 1000)
            return AgentResult(
                success=False,
                error=str(exc),
                duration_ms=duration,
            )

    @abstractmethod
    async def execute(self, ctx: AgentContext) -> AgentResult:
        """Implement the agent's core logic. Called by `run`."""
        ...
