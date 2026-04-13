"""Persistent workflow runner with DB-backed state.

Unlike the in-memory WorkflowEngine, this runner:
  - Persists every step to workflow_step_runs
  - Pauses the workflow when a step requires approval
  - Can be resumed after approval is granted
  - Updates workflow_runs with progress counts and totals
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any, Protocol

logger = logging.getLogger("abf_workflows.runner")


class StepHandler(Protocol):
    """Callable that executes a single workflow step."""

    async def __call__(
        self,
        step_key: str,
        payload: dict[str, Any],
        db: Any,
        business_id: str,
        prior_outputs: dict[str, dict[str, Any]],
    ) -> StepOutcome: ...


class StepOutcome:
    """Result of running a single step in the persistent runner."""

    __slots__ = (
        "success", "output", "error", "tokens_used", "cost_cents",
        "duration_ms", "needs_approval", "approval_id",
    )

    def __init__(
        self,
        *,
        success: bool = True,
        output: dict[str, Any] | None = None,
        error: str | None = None,
        tokens_used: int = 0,
        cost_cents: int = 0,
        duration_ms: int = 0,
        needs_approval: bool = False,
        approval_id: str | None = None,
    ):
        self.success = success
        self.output = output or {}
        self.error = error
        self.tokens_used = tokens_used
        self.cost_cents = cost_cents
        self.duration_ms = duration_ms
        self.needs_approval = needs_approval
        self.approval_id = approval_id


class PersistentWorkflowRunner:
    """Execute a workflow with DB-persisted state.

    Usage:
        runner = PersistentWorkflowRunner(db, workflow_run_id)
        result = await runner.run(steps, handlers)
    """

    def __init__(self, db: Any, workflow_run_id: str):
        self.db = db
        self.wf_id = workflow_run_id
        self._prior_outputs: dict[str, dict[str, Any]] = {}

    async def run(
        self,
        steps: list[dict[str, Any]],
        handler: StepHandler,
        business_id: str,
    ) -> dict[str, Any]:
        """Run steps in order. Pauses on approval, stops on failure."""
        total_tokens = 0
        total_cost = 0
        completed = 0
        failed = 0

        for step_def in steps:
            step_key = step_def["key"]
            step_name = step_def["name"]

            # Check if this step already completed (for resume scenarios)
            existing = self._get_step_run(step_key)
            if existing and existing.get("status") == "completed":
                self._prior_outputs[step_key] = existing.get("output_payload") or {}
                total_tokens += existing.get("tokens_used", 0)
                total_cost += existing.get("cost_cents", 0)
                completed += 1
                continue

            # Create or update step record
            step_run_id = self._upsert_step_run(step_key, step_name, step_def.get("agent_name"))

            # Update workflow current_step
            self._update_workflow(current_step=step_key, status="running")

            # Mark step as running
            now = datetime.now(timezone.utc).isoformat()
            self.db.table("workflow_step_runs").update({
                "status": "running",
                "input_payload": step_def.get("payload", {}),
                "started_at": now,
            }).eq("id", step_run_id).execute()

            # Execute
            start = time.perf_counter()
            try:
                outcome = await handler(
                    step_key=step_key,
                    payload=step_def.get("payload", {}),
                    db=self.db,
                    business_id=business_id,
                    prior_outputs=self._prior_outputs,
                )
            except Exception as exc:
                duration = int((time.perf_counter() - start) * 1000)
                outcome = StepOutcome(
                    success=False, error=str(exc), duration_ms=duration,
                )

            # Persist step result
            if outcome.needs_approval:
                self.db.table("workflow_step_runs").update({
                    "status": "waiting_approval",
                    "output_payload": outcome.output,
                    "approval_id": outcome.approval_id,
                    "tokens_used": outcome.tokens_used,
                    "cost_cents": outcome.cost_cents,
                    "duration_ms": outcome.duration_ms,
                }).eq("id", step_run_id).execute()

                total_tokens += outcome.tokens_used
                total_cost += outcome.cost_cents
                self._update_workflow(
                    status="paused",
                    total_tokens=total_tokens,
                    total_cost_cents=total_cost,
                    completed_steps=completed,
                )
                logger.info(
                    "Workflow %s paused at step %s (waiting approval %s)",
                    self.wf_id, step_key, outcome.approval_id,
                )
                return {
                    "status": "paused",
                    "paused_at": step_key,
                    "approval_id": outcome.approval_id,
                    "completed_steps": completed,
                    "total_tokens": total_tokens,
                    "total_cost_cents": total_cost,
                }

            elif outcome.success:
                now = datetime.now(timezone.utc).isoformat()
                self.db.table("workflow_step_runs").update({
                    "status": "completed",
                    "output_payload": outcome.output,
                    "tokens_used": outcome.tokens_used,
                    "cost_cents": outcome.cost_cents,
                    "duration_ms": outcome.duration_ms,
                    "completed_at": now,
                }).eq("id", step_run_id).execute()

                self._prior_outputs[step_key] = outcome.output
                total_tokens += outcome.tokens_used
                total_cost += outcome.cost_cents
                completed += 1

                logger.info(
                    "Workflow %s step %s completed (tokens=%d, cost=%dc)",
                    self.wf_id, step_key, outcome.tokens_used, outcome.cost_cents,
                )
            else:
                now = datetime.now(timezone.utc).isoformat()
                self.db.table("workflow_step_runs").update({
                    "status": "failed",
                    "error_message": outcome.error,
                    "tokens_used": outcome.tokens_used,
                    "cost_cents": outcome.cost_cents,
                    "duration_ms": outcome.duration_ms,
                    "completed_at": now,
                }).eq("id", step_run_id).execute()

                total_tokens += outcome.tokens_used
                total_cost += outcome.cost_cents
                failed += 1

                self._update_workflow(
                    status="failed",
                    total_tokens=total_tokens,
                    total_cost_cents=total_cost,
                    completed_steps=completed,
                    failed_steps=failed,
                    error_message=outcome.error,
                )
                logger.error(
                    "Workflow %s failed at step %s: %s",
                    self.wf_id, step_key, outcome.error,
                )
                return {
                    "status": "failed",
                    "failed_at": step_key,
                    "error": outcome.error,
                    "completed_steps": completed,
                    "total_tokens": total_tokens,
                    "total_cost_cents": total_cost,
                }

        # All steps completed
        now = datetime.now(timezone.utc).isoformat()
        self._update_workflow(
            status="completed",
            total_tokens=total_tokens,
            total_cost_cents=total_cost,
            completed_steps=completed,
            completed_at=now,
        )
        logger.info(
            "Workflow %s completed (%d steps, tokens=%d, cost=%dc)",
            self.wf_id, completed, total_tokens, total_cost,
        )
        return {
            "status": "completed",
            "completed_steps": completed,
            "total_tokens": total_tokens,
            "total_cost_cents": total_cost,
        }

    # ── DB helpers ───────────────────────────────────────────

    def _get_step_run(self, step_key: str) -> dict[str, Any] | None:
        res = (
            self.db.table("workflow_step_runs")
            .select("*")
            .eq("workflow_run_id", self.wf_id)
            .eq("step_key", step_key)
            .maybe_single()
            .execute()
        )
        return res.data

    def _upsert_step_run(self, step_key: str, step_name: str, agent_name: str | None) -> str:
        existing = self._get_step_run(step_key)
        if existing:
            return existing["id"]
        res = self.db.table("workflow_step_runs").insert({
            "workflow_run_id": self.wf_id,
            "step_key": step_key,
            "step_name": step_name,
            "agent_name": agent_name,
            "status": "pending",
        }).execute()
        if not res.data:
            raise RuntimeError(f"Failed to create step run for {step_key}")
        return res.data[0]["id"]

    def _update_workflow(self, **fields: Any) -> None:
        self.db.table("workflow_runs").update(fields).eq("id", self.wf_id).execute()
