"""Base agent class and execution context.

Every agent inherits from BaseAgent and implements `execute()`.
The base class provides:
  - Structured context (AgentContext) with optional DB client
  - Automatic timing and error capture via `run()`
  - A clean AgentResult with cost/token metadata
  - A DBOps helper for writing to agent_runs, tasks, and approvals
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger("abf_agents")


class AgentContext(BaseModel):
    """Runtime context passed to every agent execution."""

    business_id: str
    task_id: str | None = None
    run_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)

    # Optional — set when the agent needs to write to the database.
    # Uses Any to avoid importing supabase at module level.
    db: Any = Field(default=None, exclude=True)

    model_config = {"arbitrary_types_allowed": True}


class AgentResult(BaseModel):
    """Standardised result from an agent execution."""

    success: bool = False
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    tokens_used: int = 0
    cost_cents: int = 0
    duration_ms: int = 0
    tasks_created: list[str] = Field(default_factory=list)
    approvals_created: list[str] = Field(default_factory=list)


class BaseAgent(ABC):
    """Abstract base class for all ABF agents.

    Subclass this and implement `execute` to create a new agent type.
    The `run()` wrapper handles timing, error capture, run logging,
    and result normalisation.
    """

    name: str = "base"
    agent_type: str = "operations"
    description: str = ""

    async def run(self, ctx: AgentContext) -> AgentResult:
        """Execute the agent with timing, error handling, and run logging."""
        start = time.perf_counter()

        # Record the run as "running" in agent_runs if we have DB access
        run_id = ctx.run_id
        if ctx.db and not run_id:
            run_id = self._start_run(ctx)
            ctx.run_id = run_id

        try:
            result = await self.execute(ctx)
            result.duration_ms = int((time.perf_counter() - start) * 1000)
            result.success = True

            logger.info(
                "%s succeeded: tokens=%d cost=%dc duration=%dms tasks_created=%d",
                self.name, result.tokens_used, result.cost_cents,
                result.duration_ms, len(result.tasks_created),
            )

            # Update run record on success
            if ctx.db and run_id:
                self._finish_run(ctx.db, run_id, result)

            return result

        except Exception as exc:
            duration = int((time.perf_counter() - start) * 1000)
            logger.error("%s failed after %dms: %s", self.name, duration, exc)

            result = AgentResult(
                success=False,
                error=str(exc),
                duration_ms=duration,
            )

            # Update run record on failure
            if ctx.db and run_id:
                self._finish_run(ctx.db, run_id, result)

            return result

    @abstractmethod
    async def execute(self, ctx: AgentContext) -> AgentResult:
        """Implement the agent's core logic. Called by `run()`."""
        ...

    # ── Database helpers ─────────────────────────────────────

    def _start_run(self, ctx: AgentContext) -> str:
        """Insert an agent_runs record with status=running. Returns the run ID."""
        try:
            res = ctx.db.table("agent_runs").insert({
                "business_id": ctx.business_id,
                "task_id": ctx.task_id,
                "agent_name": self.name,
                "agent_type": self.agent_type,
                "status": "running",
                "input_payload": ctx.payload,
            }).execute()
            return res.data[0]["id"]
        except Exception:
            logger.exception("Failed to create agent_runs record")
            return ""

    def _finish_run(self, db: Any, run_id: str, result: AgentResult) -> None:
        """Update the agent_runs record with final status and metrics."""
        try:
            now = datetime.now(timezone.utc).isoformat()
            db.table("agent_runs").update({
                "status": "completed" if result.success else "failed",
                "output_payload": result.output,
                "error_message": result.error,
                "tokens_used": result.tokens_used,
                "cost_cents": result.cost_cents,
                "duration_ms": result.duration_ms,
                "completed_at": now,
            }).eq("id", run_id).execute()
        except Exception:
            logger.exception("Failed to update agent_runs record %s", run_id)


class DBOps:
    """Database operations helper for agents.

    Agents should use this instead of calling db.table() directly.
    This keeps the DB interaction surface small and testable.
    """

    def __init__(self, db: Any):
        self._db = db

    def create_task(
        self,
        *,
        business_id: str,
        title: str,
        description: str | None = None,
        priority: str = "medium",
        assigned_agent: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> str:
        """Insert a task and return its ID."""
        res = self._db.table("tasks").insert({
            "business_id": business_id,
            "title": title,
            "description": description,
            "priority": priority,
            "assigned_agent": assigned_agent,
            "status": "pending",
            "payload": payload or {},
        }).execute()
        if not res.data:
            raise RuntimeError(f"Failed to create task: {title}")
        task_id = res.data[0]["id"]
        logger.info("Task created: %s — %s", task_id, title)
        return task_id

    def create_approval(
        self,
        *,
        business_id: str,
        approval_type: str,
        title: str,
        description: str | None = None,
        requested_by: str,
        amount_cents: int | None = None,
        payload: dict[str, Any] | None = None,
    ) -> str:
        """Insert an approval request and return its ID."""
        res = self._db.table("approvals").insert({
            "business_id": business_id,
            "type": approval_type,
            "title": title,
            "description": description,
            "status": "pending",
            "requested_by": requested_by,
            "amount_cents": amount_cents,
            "payload": payload or {},
        }).execute()
        if not res.data:
            raise RuntimeError(f"Failed to create approval: {title}")
        approval_id = res.data[0]["id"]
        logger.info("Approval created: %s — %s", approval_id, title)
        return approval_id

    def update_task_status(
        self, task_id: str, status: str, result: dict[str, Any] | None = None
    ) -> None:
        """Update a task's status and optionally its result."""
        data: dict[str, Any] = {"status": status}
        if result is not None:
            data["result"] = result
        if status in ("completed", "failed"):
            data["completed_at"] = datetime.now(timezone.utc).isoformat()
        self._db.table("tasks").update(data).eq("id", task_id).execute()

    def get_business(self, business_id: str) -> dict[str, Any] | None:
        """Fetch a business by ID."""
        res = self._db.table("businesses").select("*").eq("id", business_id).maybe_single().execute()
        return res.data

    def get_campaigns(self, business_id: str) -> list[dict[str, Any]]:
        """Fetch all campaigns for a business."""
        res = self._db.table("campaigns").select("*").eq("business_id", business_id).execute()
        return res.data or []

    def get_products(self, business_id: str) -> list[dict[str, Any]]:
        """Fetch all products for a business."""
        res = self._db.table("products").select("*").eq("business_id", business_id).execute()
        return res.data or []

    # ── Memory helpers ───────────────────────────────────────

    def save_memory(
        self,
        *,
        business_id: str,
        agent_name: str,
        namespace: str,
        key: str,
        entry: Any,
    ) -> str | None:
        """Save a memory entry via abf_ai.memory.save."""
        from abf_ai.memory import save
        return save(
            self._db,
            business_id=business_id,
            agent_name=agent_name,
            namespace=namespace,
            key=key,
            entry=entry,
        )

    def recall_decisions(self, *, business_id: str, decision_type: str) -> str:
        """Recall past decisions formatted for AI prompt injection."""
        from abf_ai.memory import recall_relevant_decisions
        return recall_relevant_decisions(
            self._db, business_id=business_id, decision_type=decision_type,
        )

    def recall_campaign_patterns(
        self, *, business_id: str, channel: str | None = None,
    ) -> str:
        """Recall campaign patterns formatted for AI prompt injection."""
        from abf_ai.memory import recall_campaign_patterns
        return recall_campaign_patterns(
            self._db, business_id=business_id, channel=channel,
        )
