"""Built-in agent implementations.

Imports the core agent layer (agents/) and keeps simple wrapper agents
for backward compatibility with the existing execute router.
"""

from __future__ import annotations

# Register the four core agents
from abf_agents.agents import (  # noqa: F401
    OpportunityAgent,
    DecisionAgent,
    ExecutionAgent,
    AnalyticsAgent,
)

# ── Simple wrapper agents (backward compat) ──────────────────

from abf_agents.base import BaseAgent, AgentContext, AgentResult
from abf_agents.registry import register


@register
class ContentWriterAgent(BaseAgent):
    name = "content_writer"
    agent_type = "content"
    description = "Generates product descriptions, blog posts, and marketing copy."

    async def execute(self, ctx: AgentContext) -> AgentResult:
        from abf_ai.router import route_ai_task

        content_type = ctx.payload.get("content_type", "content_generation")
        task_map = {
            "ad_copy": "ad_copy",
            "landing_page": "landing_page_copy",
            "product_description": "content_generation",
        }
        ai_task = task_map.get(content_type, "content_generation")

        result = await route_ai_task(ai_task, ctx.payload)
        return AgentResult(
            output=result.data,
            tokens_used=result.tokens_used,
            cost_cents=result.cost_cents,
        )


@register
class ResearchAnalystAgent(BaseAgent):
    name = "research_analyst"
    agent_type = "research"
    description = "Performs market research, competitor analysis, and trend identification."

    async def execute(self, ctx: AgentContext) -> AgentResult:
        from abf_ai.router import route_ai_task

        result = await route_ai_task("opportunity_scoring", {
            "opportunity": ctx.payload.get("topic", "market analysis"),
            "market_data": ctx.payload.get("market_data", ""),
            "our_strengths": ctx.payload.get("our_strengths", ""),
        })
        return AgentResult(
            output=result.data,
            tokens_used=result.tokens_used,
            cost_cents=result.cost_cents,
        )


@register
class AdsManagerAgent(BaseAgent):
    name = "ads_manager"
    agent_type = "ads"
    description = "Manages ad campaigns, optimises creative, and analyses performance."

    async def execute(self, ctx: AgentContext) -> AgentResult:
        from abf_ai.router import route_ai_task

        result = await route_ai_task("campaign_scaling", ctx.payload)
        return AgentResult(
            output=result.data,
            tokens_used=result.tokens_used,
            cost_cents=result.cost_cents,
        )


@register
class OperationsAgent(BaseAgent):
    name = "operations"
    agent_type = "operations"
    description = "Handles inventory forecasting, logistics, and operational tasks."

    async def execute(self, ctx: AgentContext) -> AgentResult:
        from abf_ai.router import route_ai_task

        result = await route_ai_task("decisioning", {
            "context": ctx.payload.get("task", "operations task"),
            "options": ctx.payload.get("options", []),
            "constraints": ctx.payload.get("constraints", ""),
        })
        return AgentResult(
            output=result.data,
            tokens_used=result.tokens_used,
            cost_cents=result.cost_cents,
        )


@register
class OutreachAgent(BaseAgent):
    name = "outreach"
    agent_type = "outreach"
    description = "Manages influencer outreach and partnership communications."

    async def execute(self, ctx: AgentContext) -> AgentResult:
        from abf_ai.router import route_ai_task

        result = await route_ai_task("content_generation", {
            "product_name": ctx.payload.get("campaign", "outreach"),
            "content_type": "outreach_strategy",
            "brand_voice": "Professional and friendly",
            "audience": "Influencers and content creators",
            "length": "200-300 words",
        })
        return AgentResult(
            output=result.data,
            tokens_used=result.tokens_used,
            cost_cents=result.cost_cents,
        )
