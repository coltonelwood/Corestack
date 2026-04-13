"""Built-in agent implementations."""

from __future__ import annotations

from abf_agents.base import BaseAgent, AgentContext, AgentResult
from abf_agents.registry import register


@register
class ContentWriterAgent(BaseAgent):
    name = "content_writer"
    agent_type = "content"
    description = "Generates product descriptions, blog posts, and marketing copy."

    async def execute(self, ctx: AgentContext) -> AgentResult:
        from abf_ai import complete

        task_type = ctx.payload.get("task", "product_description")
        prompt = ctx.payload.get("prompt", f"Generate content for task: {task_type}")

        result = await complete(prompt)

        return AgentResult(
            success=True,
            output={"text": result.text, "task_type": task_type},
            tokens_used=result.tokens_used,
            cost_cents=result.cost_cents,
        )


@register
class ResearchAnalystAgent(BaseAgent):
    name = "research_analyst"
    agent_type = "research"
    description = "Performs market research, competitor analysis, and trend identification."

    async def execute(self, ctx: AgentContext) -> AgentResult:
        from abf_ai import complete

        topic = ctx.payload.get("topic", "market analysis")
        prompt = f"Conduct a brief research analysis on: {topic}"

        result = await complete(prompt)

        return AgentResult(
            success=True,
            output={"analysis": result.text, "topic": topic},
            tokens_used=result.tokens_used,
            cost_cents=result.cost_cents,
        )


@register
class AdsManagerAgent(BaseAgent):
    name = "ads_manager"
    agent_type = "ads"
    description = "Manages ad campaigns, optimises creative, and analyses performance."

    async def execute(self, ctx: AgentContext) -> AgentResult:
        from abf_ai import complete

        action = ctx.payload.get("action", "optimize")
        prompt = f"Ad management task — action: {action}. Provide recommendations."

        result = await complete(prompt)

        return AgentResult(
            success=True,
            output={"recommendations": result.text, "action": action},
            tokens_used=result.tokens_used,
            cost_cents=result.cost_cents,
        )


@register
class AnalyticsAgent(BaseAgent):
    name = "analytics"
    agent_type = "analytics"
    description = "Compiles KPI reports and performance dashboards."

    async def execute(self, ctx: AgentContext) -> AgentResult:
        from abf_ai import complete

        report_type = ctx.payload.get("report_type", "weekly")
        prompt = f"Generate a {report_type} performance report summary."

        result = await complete(prompt)

        return AgentResult(
            success=True,
            output={"report": result.text, "report_type": report_type},
            tokens_used=result.tokens_used,
            cost_cents=result.cost_cents,
        )


@register
class OperationsAgent(BaseAgent):
    name = "operations"
    agent_type = "operations"
    description = "Handles inventory forecasting, logistics, and operational tasks."

    async def execute(self, ctx: AgentContext) -> AgentResult:
        from abf_ai import complete

        task = ctx.payload.get("task", "inventory_forecast")
        prompt = f"Operations task: {task}. Provide analysis and recommendations."

        result = await complete(prompt)

        return AgentResult(
            success=True,
            output={"analysis": result.text, "task": task},
            tokens_used=result.tokens_used,
            cost_cents=result.cost_cents,
        )


@register
class OutreachAgent(BaseAgent):
    name = "outreach"
    agent_type = "outreach"
    description = "Manages influencer outreach and partnership communications."

    async def execute(self, ctx: AgentContext) -> AgentResult:
        from abf_ai import complete

        campaign = ctx.payload.get("campaign", "outreach")
        prompt = f"Draft an influencer outreach strategy for campaign: {campaign}"

        result = await complete(prompt)

        return AgentResult(
            success=True,
            output={"strategy": result.text, "campaign": campaign},
            tokens_used=result.tokens_used,
            cost_cents=result.cost_cents,
        )
