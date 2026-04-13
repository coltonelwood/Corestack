"""Workflow data models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class WorkflowStep(BaseModel):
    """A single step in a workflow."""

    id: str
    name: str
    agent_name: str
    payload: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)
    condition: str | None = None  # Optional expression to evaluate


class StepResult(BaseModel):
    """Result of executing a single workflow step."""

    step_id: str
    success: bool
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    tokens_used: int = 0
    cost_cents: int = 0
    duration_ms: int = 0


class Workflow(BaseModel):
    """A workflow definition with ordered steps."""

    id: str
    name: str
    description: str = ""
    business_id: str
    steps: list[WorkflowStep]

    def get_step(self, step_id: str) -> WorkflowStep | None:
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_ready_steps(self, completed: set[str]) -> list[WorkflowStep]:
        """Return steps whose dependencies are all satisfied."""
        ready = []
        for step in self.steps:
            if step.id in completed:
                continue
            if all(dep in completed for dep in step.depends_on):
                ready.append(step)
        return ready
