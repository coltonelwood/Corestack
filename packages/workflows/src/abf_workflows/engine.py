"""Workflow execution engine.

Runs workflow steps in dependency order, passing results between steps.
"""

from __future__ import annotations

import asyncio
from typing import Any

from abf_agents import get_agent
from abf_agents.base import AgentContext
from abf_workflows.models import Workflow, StepResult


class WorkflowEngine:
    """Execute a workflow by resolving the step DAG and running agents."""

    def __init__(self, workflow: Workflow):
        self.workflow = workflow
        self.results: dict[str, StepResult] = {}
        self.completed: set[str] = set()

    async def run(self) -> list[StepResult]:
        """Execute all steps in dependency order.

        Steps with satisfied dependencies run concurrently.
        """
        while True:
            ready = self.workflow.get_ready_steps(self.completed)
            if not ready:
                break

            tasks = [self._run_step(step) for step in ready]
            step_results = await asyncio.gather(*tasks)

            for result in step_results:
                self.results[result.step_id] = result
                self.completed.add(result.step_id)

                # Stop workflow on failure (fail-fast)
                if not result.success:
                    return list(self.results.values())

        return list(self.results.values())

    async def _run_step(self, step: Any) -> StepResult:
        """Execute a single workflow step via its assigned agent."""
        try:
            agent = get_agent(step.agent_name)
        except KeyError as exc:
            return StepResult(
                step_id=step.id,
                success=False,
                error=str(exc),
            )

        # Merge outputs from dependency steps into the payload
        merged_payload = dict(step.payload)
        for dep_id in step.depends_on:
            dep_result = self.results.get(dep_id)
            if dep_result and dep_result.success:
                merged_payload[f"dep_{dep_id}"] = dep_result.output

        ctx = AgentContext(
            business_id=self.workflow.business_id,
            payload=merged_payload,
        )

        result = await agent.run(ctx)

        return StepResult(
            step_id=step.id,
            success=result.success,
            output=result.output,
            error=result.error,
            tokens_used=result.tokens_used,
            cost_cents=result.cost_cents,
            duration_ms=result.duration_ms,
        )
