"""ExecutionAgent — converts approved decisions into actionable tasks.

Responsibilities:
  - Take an approved action and break it into backend workflow tasks
  - Never execute high-risk actions without a prior approval
  - Prepare payloads for downstream integrations
  - Use the AI router for content/copy generation when needed

Input payload:
  {
    "action": "launch_campaign | create_product | scale_budget | generate_content",
    "approved": true,
    "approval_id": "...",
    ... action-specific fields ...
  }

Output:
  List of tasks created, integration payloads prepared, any approvals requested.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

from abf_agents.base import BaseAgent, AgentContext, AgentResult, DBOps
from abf_agents.registry import register

logger = logging.getLogger("abf_agents.execution")

# Actions that require a prior approval before execution
HIGH_RISK_ACTIONS = {"launch_campaign", "scale_budget"}


class ExecutionInput(BaseModel):
    action: str
    approved: bool = False
    approval_id: str | None = None
    # Action-specific fields (varies by action)
    campaign_name: str = ""
    channel: str = ""
    budget_cents: int = 0
    budget_change_pct: float = 0
    product_name: str = ""
    content_type: str = ""
    target_audience: str = ""
    brand_voice: str = ""
    integration_target: str = ""  # e.g. "shopify", "meta", "stripe"
    extra: dict[str, Any] = Field(default_factory=dict)


@register
class ExecutionAgent(BaseAgent):
    name = "execution"
    agent_type = "operations"
    description = (
        "Converts approved decisions into backend workflow tasks. "
        "Never executes high-risk actions without approval. "
        "Prepares integration payloads for downstream services."
    )

    async def execute(self, ctx: AgentContext) -> AgentResult:
        inp = ExecutionInput.model_validate(ctx.payload)
        tasks_created: list[str] = []
        approvals_created: list[str] = []
        integration_payloads: list[dict[str, Any]] = []

        # Guard: high-risk actions require approval
        if inp.action in HIGH_RISK_ACTIONS and not inp.approved:
            if ctx.db:
                ops = DBOps(ctx.db)
                aid = ops.create_approval(
                    business_id=ctx.business_id,
                    approval_type="campaign_launch" if inp.action == "launch_campaign" else "budget_increase",
                    title=f"Approval required: {inp.action}",
                    description=f"Action '{inp.action}' requires human approval before execution.",
                    requested_by=self.name,
                    amount_cents=inp.budget_cents or None,
                    payload=inp.model_dump(),
                )
                approvals_created.append(aid)

            return AgentResult(
                output={
                    "status": "approval_required",
                    "action": inp.action,
                    "message": f"Action '{inp.action}' is high-risk and requires approval before execution.",
                    "approvals_created": approvals_created,
                },
                approvals_created=approvals_created,
            )

        # Dispatch to the appropriate action handler
        handler = self._get_handler(inp.action)
        if handler is None:
            return AgentResult(
                error=f"Unknown action: {inp.action}",
            )

        return await handler(ctx, inp, tasks_created, approvals_created, integration_payloads)

    def _get_handler(self, action: str):
        handlers = {
            "launch_campaign": self._launch_campaign,
            "create_product": self._create_product,
            "scale_budget": self._scale_budget,
            "generate_content": self._generate_content,
        }
        return handlers.get(action)

    async def _launch_campaign(
        self, ctx: AgentContext, inp: ExecutionInput,
        tasks: list, approvals: list, integrations: list,
    ) -> AgentResult:
        """Break a campaign launch into subtasks."""
        if not ctx.db:
            return AgentResult(error="DB access required for campaign launch")

        ops = DBOps(ctx.db)

        # 1. Generate ad copy
        t1 = ops.create_task(
            business_id=ctx.business_id,
            title=f"Generate ad copy for {inp.campaign_name}",
            priority="high",
            assigned_agent="Content Writer",
            payload={
                "source": "execution_agent",
                "content_type": "ad_copy",
                "campaign_name": inp.campaign_name,
                "channel": inp.channel,
                "target_audience": inp.target_audience,
            },
        )
        tasks.append(t1)

        # 2. Set up tracking
        t2 = ops.create_task(
            business_id=ctx.business_id,
            title=f"Set up conversion tracking for {inp.campaign_name}",
            priority="high",
            assigned_agent="Ads Manager",
            payload={"source": "execution_agent", "channel": inp.channel},
        )
        tasks.append(t2)

        # 3. Prepare integration payload
        integration_payload = {
            "integration": inp.integration_target or inp.channel,
            "action": "create_campaign",
            "params": {
                "name": inp.campaign_name,
                "channel": inp.channel,
                "budget_cents": inp.budget_cents,
                "status": "draft",
            },
        }
        integrations.append(integration_payload)

        return AgentResult(
            output={
                "status": "tasks_created",
                "action": inp.action,
                "tasks_created": tasks,
                "integration_payloads": integrations,
                "message": f"Campaign launch broken into {len(tasks)} tasks.",
            },
            tasks_created=tasks,
        )

    async def _create_product(
        self, ctx: AgentContext, inp: ExecutionInput,
        tasks: list, approvals: list, integrations: list,
    ) -> AgentResult:
        """Break a product creation into subtasks."""
        if not ctx.db:
            return AgentResult(error="DB access required for product creation")

        ops = DBOps(ctx.db)

        # Generate product description
        t1 = ops.create_task(
            business_id=ctx.business_id,
            title=f"Generate product description for {inp.product_name}",
            priority="medium",
            assigned_agent="Content Writer",
            payload={
                "source": "execution_agent",
                "content_type": "product_description",
                "product_name": inp.product_name,
                "brand_voice": inp.brand_voice,
                "target_audience": inp.target_audience,
            },
        )
        tasks.append(t1)

        # Prepare listing payload
        integration_payload = {
            "integration": inp.integration_target or "shopify",
            "action": "create_product",
            "params": {
                "name": inp.product_name,
                "status": "draft",
            },
        }
        integrations.append(integration_payload)

        # Create approval for listing
        aid = ops.create_approval(
            business_id=ctx.business_id,
            approval_type="product_listing",
            title=f"Approve product listing: {inp.product_name}",
            description="Product copy and listing data are ready for review.",
            requested_by=self.name,
            payload={"product_name": inp.product_name},
        )
        approvals.append(aid)

        return AgentResult(
            output={
                "status": "tasks_created",
                "action": inp.action,
                "tasks_created": tasks,
                "approvals_created": approvals,
                "integration_payloads": integrations,
            },
            tasks_created=tasks,
            approvals_created=approvals,
        )

    async def _scale_budget(
        self, ctx: AgentContext, inp: ExecutionInput,
        tasks: list, approvals: list, integrations: list,
    ) -> AgentResult:
        """Prepare a budget scaling payload for the ad platform."""
        integration_payload = {
            "integration": inp.integration_target or inp.channel,
            "action": "update_budget",
            "params": {
                "campaign_name": inp.campaign_name,
                "budget_change_pct": inp.budget_change_pct,
                "new_budget_cents": int(inp.budget_cents * (1 + inp.budget_change_pct / 100)),
            },
        }
        integrations.append(integration_payload)

        return AgentResult(
            output={
                "status": "ready_to_execute",
                "action": inp.action,
                "integration_payloads": integrations,
                "message": f"Budget scaling payload prepared ({inp.budget_change_pct:+.0f}%).",
            },
        )

    async def _generate_content(
        self, ctx: AgentContext, inp: ExecutionInput,
        tasks: list, approvals: list, integrations: list,
    ) -> AgentResult:
        """Generate content via the AI router."""
        from abf_ai.router import route_ai_task

        content_type_map = {
            "ad_copy": "ad_copy",
            "landing_page": "landing_page_copy",
            "product_description": "content_generation",
        }
        ai_task = content_type_map.get(inp.content_type, "content_generation")

        ai_result = await route_ai_task(ai_task, {
            "product_name": inp.product_name or "Product",
            "brand_voice": inp.brand_voice or "Professional",
            "audience": inp.target_audience or "General",
            "channel": inp.channel or "web",
            "content_type": inp.content_type,
            "goal": "drive conversions",
            "tone": inp.brand_voice or "professional",
            "value_prop": inp.extra.get("value_prop", ""),
            "target_audience": inp.target_audience or "General",
            "price": inp.extra.get("price", ""),
            "length": inp.extra.get("length", "150-200 words"),
            "category": inp.extra.get("category", ""),
            "max_headline_chars": 30,
            "max_body_chars": 90,
        })

        return AgentResult(
            output={
                "status": "content_generated" if ai_result.success else "content_failed",
                "action": inp.action,
                "content_type": inp.content_type,
                "content": ai_result.data if ai_result.success else None,
                "error": ai_result.error,
            },
            tokens_used=ai_result.tokens_used,
            cost_cents=ai_result.cost_cents,
        )
