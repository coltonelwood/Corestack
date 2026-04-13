"""AnalyticsAgent — summarizes performance and identifies opportunities.

Responsibilities:
  - Summarize campaign and business performance from real data
  - Identify winners, losers, and anomalies
  - Recommend next actions
  - Use the AI router for summarization and decisioning

Input payload:
  {
    "analysis_type": "campaign | business | portfolio",
    "campaign_id": "...",      (for campaign analysis)
    "time_period": "weekly"    (optional)
  }

Output:
  Structured analysis with winners, losers, anomalies, and recommendations.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel

from abf_agents.base import BaseAgent, AgentContext, AgentResult, DBOps
from abf_agents.registry import register

logger = logging.getLogger("abf_agents.analytics")


class AnalyticsInput(BaseModel):
    analysis_type: str = "business"  # "campaign" | "business" | "portfolio"
    campaign_id: str | None = None
    time_period: str = "weekly"
    include_recommendations: bool = True


@register
class AnalyticsAgent(BaseAgent):
    name = "analytics"
    agent_type = "analytics"
    description = (
        "Summarizes campaign and business performance, identifies winners "
        "and losers, spots anomalies, and recommends next actions."
    )

    async def execute(self, ctx: AgentContext) -> AgentResult:
        from abf_ai.router import route_ai_task

        inp = AnalyticsInput.model_validate(ctx.payload)
        total_tokens = 0
        total_cost = 0

        # Gather data from the database if available
        data_context = await self._gather_data(ctx, inp)

        # Step 1: Summarize the data
        summary_result = await route_ai_task("summarization", {
            "text": data_context,
        })
        total_tokens += summary_result.tokens_used
        total_cost += summary_result.cost_cents

        if not summary_result.success:
            return AgentResult(
                error=f"Summarization failed: {summary_result.error}",
                tokens_used=total_tokens,
                cost_cents=total_cost,
            )

        # Step 2: Classify performance and identify anomalies
        classification_result = await route_ai_task("classification", {
            "text": f"Based on this performance summary, classify the overall health:\n\n{summary_result.data.get('summary', '')}",
            "categories": ["strong_growth", "healthy", "needs_attention", "declining", "critical"],
        })
        total_tokens += classification_result.tokens_used
        total_cost += classification_result.cost_cents

        # Step 3: Get strategic recommendations (if requested)
        recommendations = {}
        tasks_created: list[str] = []

        if inp.include_recommendations:
            rec_result = await route_ai_task("decisioning", {
                "context": f"Performance summary:\n{summary_result.data.get('summary', '')}\n\nHealth: {classification_result.data.get('label', 'unknown')}",
                "options": [
                    "Scale winning campaigns",
                    "Pause underperformers",
                    "Launch new test campaigns",
                    "Optimize existing campaigns",
                    "Reduce spend across the board",
                ],
                "constraints": "Prioritize actions with highest expected ROI. Be specific.",
            })
            total_tokens += rec_result.tokens_used
            total_cost += rec_result.cost_cents

            if rec_result.success:
                recommendations = rec_result.data

                # Create follow-up tasks for high-confidence recommendations
                if ctx.db and rec_result.data.get("confidence", 0) >= 0.7:
                    ops = DBOps(ctx.db)
                    action = rec_result.data.get("recommended_action", "Review analytics report")
                    tid = ops.create_task(
                        business_id=ctx.business_id,
                        title=f"Action: {action[:100]}",
                        description=f"Auto-generated from {inp.time_period} analytics.\nReason: {rec_result.data.get('reason', '')}",
                        priority="high" if rec_result.data.get("risk_level") in ("high", "critical") else "medium",
                        assigned_agent="Operations Agent",
                        payload={
                            "source": "analytics_agent",
                            "analysis_type": inp.analysis_type,
                            "recommendation": rec_result.data,
                        },
                    )
                    tasks_created.append(tid)

        return AgentResult(
            output={
                "analysis_type": inp.analysis_type,
                "time_period": inp.time_period,
                "summary": summary_result.data,
                "health": classification_result.data if classification_result.success else {"label": "unknown"},
                "recommendations": recommendations,
                "tasks_created": tasks_created,
            },
            tokens_used=total_tokens,
            cost_cents=total_cost,
            tasks_created=tasks_created,
        )

    async def _gather_data(self, ctx: AgentContext, inp: AnalyticsInput) -> str:
        """Build a text summary of the raw data for the AI to analyze."""
        if not ctx.db:
            # No DB — use whatever's in the payload
            return ctx.payload.get("data", ctx.payload.get("text", str(ctx.payload)))

        ops = DBOps(ctx.db)

        if inp.analysis_type == "campaign" and inp.campaign_id:
            res = ctx.db.table("campaigns").select("*").eq("id", inp.campaign_id).maybe_single().execute()
            if res.data:
                c = res.data
                return (
                    f"Campaign: {c['name']}\n"
                    f"Channel: {c['channel']}\n"
                    f"Status: {c['status']}\n"
                    f"Budget: ${c['budget_cents']/100:,.0f}\n"
                    f"Spent: ${c['spent_cents']/100:,.0f} ({c['spent_cents']*100//max(c['budget_cents'],1)}%)\n"
                    f"Impressions: {c['impressions']:,}\n"
                    f"Clicks: {c['clicks']:,}\n"
                    f"Conversions: {c['conversions']:,}\n"
                    f"CTR: {c['clicks']*100/max(c['impressions'],1):.2f}%\n"
                    f"Conv Rate: {c['conversions']*100/max(c['clicks'],1):.2f}%\n"
                    f"CPA: ${c['spent_cents']/max(c['conversions'],1)/100:.2f}\n"
                    f"Period: {c.get('start_date', '?')} to {c.get('end_date', '?')}"
                )

        elif inp.analysis_type in ("business", "portfolio"):
            campaigns = ops.get_campaigns(ctx.business_id)
            products = ops.get_products(ctx.business_id)
            business = ops.get_business(ctx.business_id)

            lines = []
            if business:
                lines.append(f"Business: {business['name']} (status: {business['status']})")

            if products:
                lines.append(f"\nProducts ({len(products)}):")
                for p in products[:10]:
                    lines.append(
                        f"  - {p['name']}: ${p['price_cents']/100:.0f}, "
                        f"sales={p['sales_count']}, inventory={p['inventory']}"
                    )

            if campaigns:
                lines.append(f"\nCampaigns ({len(campaigns)}):")
                for c in campaigns[:10]:
                    cpa = c['spent_cents'] / max(c['conversions'], 1) / 100
                    lines.append(
                        f"  - {c['name']} ({c['channel']}, {c['status']}): "
                        f"budget=${c['budget_cents']/100:,.0f}, "
                        f"spent=${c['spent_cents']/100:,.0f}, "
                        f"conv={c['conversions']}, CPA=${cpa:.2f}"
                    )

            return "\n".join(lines) if lines else "No data available for analysis."

        return "No data context available."
