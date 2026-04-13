"""OpportunityAgent — identifies and scores business opportunities.

Responsibilities:
  - Analyze product, market, or business inputs
  - Score opportunities using the AI router (opportunity_scoring)
  - Write scored opportunities as tasks to the database
  - Create follow-up tasks for high-scoring opportunities

Input payload:
  {
    "opportunity": "Description of the opportunity",
    "market_data": "Relevant market context",
    "our_strengths": "What we bring to the table"
  }

Output:
  Full opportunity_scoring result + any tasks/approvals created.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

from abf_agents.base import BaseAgent, AgentContext, AgentResult, DBOps
from abf_agents.registry import register

logger = logging.getLogger("abf_agents.opportunity")


class OpportunityInput(BaseModel):
    opportunity: str
    market_data: str = ""
    our_strengths: str = ""
    auto_create_tasks: bool = True


@register
class OpportunityAgent(BaseAgent):
    name = "opportunity"
    agent_type = "research"
    description = (
        "Analyzes product or business inputs, scores opportunities, "
        "and creates follow-up tasks for high-potential ones."
    )

    async def execute(self, ctx: AgentContext) -> AgentResult:
        from abf_ai.router import route_ai_task

        # Parse and validate input
        inp = OpportunityInput.model_validate(ctx.payload)

        # Route to opportunity_scoring via the AI router
        ai_result = await route_ai_task("opportunity_scoring", {
            "opportunity": inp.opportunity,
            "market_data": inp.market_data,
            "our_strengths": inp.our_strengths,
        })

        if not ai_result.success:
            return AgentResult(
                error=f"AI scoring failed: {ai_result.error}",
                tokens_used=ai_result.tokens_used,
                cost_cents=ai_result.cost_cents,
            )

        score = ai_result.data.get("opportunity_score", 0)
        decision = ai_result.data.get("decision", "monitor")
        tasks_created: list[str] = []
        approvals_created: list[str] = []

        # If we have DB access and auto_create_tasks is on, create follow-ups
        if ctx.db and inp.auto_create_tasks:
            ops = DBOps(ctx.db)

            if score >= 70 and decision == "pursue":
                # High-value opportunity → create research + planning tasks
                tid = ops.create_task(
                    business_id=ctx.business_id,
                    title=f"Deep-dive research: {inp.opportunity[:80]}",
                    description=f"Opportunity scored {score}/100 with decision '{decision}'. Conduct detailed feasibility analysis.",
                    priority="high",
                    assigned_agent="Research Analyst",
                    payload={
                        "source": "opportunity_agent",
                        "opportunity_score": score,
                        "original_opportunity": inp.opportunity,
                    },
                )
                tasks_created.append(tid)

                tid2 = ops.create_task(
                    business_id=ctx.business_id,
                    title=f"Draft launch plan: {inp.opportunity[:80]}",
                    description=f"Create a launch plan for this {score}-score opportunity.",
                    priority="medium",
                    assigned_agent="Operations Agent",
                    payload={"source": "opportunity_agent", "depends_on_research": tid},
                )
                tasks_created.append(tid2)

                logger.info(
                    "Opportunity scored %d (pursue) → created %d follow-up tasks",
                    score, len(tasks_created),
                )

            elif score >= 40 and decision == "monitor":
                tid = ops.create_task(
                    business_id=ctx.business_id,
                    title=f"Monitor opportunity: {inp.opportunity[:80]}",
                    description=f"Opportunity scored {score}/100. Set up monitoring and revisit in 2 weeks.",
                    priority="low",
                    assigned_agent="Research Analyst",
                    payload={"source": "opportunity_agent", "opportunity_score": score},
                )
                tasks_created.append(tid)

        return AgentResult(
            output={
                **ai_result.data,
                "tasks_created": tasks_created,
                "approvals_created": approvals_created,
            },
            tokens_used=ai_result.tokens_used,
            cost_cents=ai_result.cost_cents,
            tasks_created=tasks_created,
            approvals_created=approvals_created,
        )
