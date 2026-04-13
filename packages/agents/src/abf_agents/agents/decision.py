"""DecisionAgent — makes strategic decisions with confidence scoring.

Responsibilities:
  - Score launch opportunities (via opportunity_scoring)
  - Evaluate campaign health (via campaign_scaling)
  - Make general strategic decisions (via decisioning)
  - Always returns structured JSON with confidence + rationale
  - Creates approval requests for high-risk decisions

Input payload:
  {
    "decision_type": "launch | scale | general",
    ... type-specific fields ...
  }

Output:
  Decision data with confidence, risk_level, and recommended_action.
"""

from __future__ import annotations

import logging

from pydantic import BaseModel

from abf_agents.base import BaseAgent, AgentContext, AgentResult, DBOps
from abf_agents.registry import register

logger = logging.getLogger("abf_agents.decision")


class DecisionInput(BaseModel):
    decision_type: str = "general"  # "launch" | "scale" | "general"
    # General decisioning
    context: str = ""
    options: list[str] | None = None
    constraints: str = ""
    # Campaign scaling
    campaign_name: str = ""
    channel: str = ""
    current_budget_cents: int = 0
    spent_cents: int = 0
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    roas: float = 0
    cpa_cents: int = 0
    days_remaining: int = 0
    # Launch
    opportunity: str = ""
    market_data: str = ""
    our_strengths: str = ""


DECISION_TYPE_TO_TASK = {
    "launch": "opportunity_scoring",
    "scale": "campaign_scaling",
    "general": "decisioning",
}


@register
class DecisionAgent(BaseAgent):
    name = "decision"
    agent_type = "research"
    description = (
        "Scores launch opportunities, evaluates campaign health, and makes "
        "strategic decisions. Returns structured JSON with confidence and rationale."
    )

    async def execute(self, ctx: AgentContext) -> AgentResult:
        from abf_ai.router import route_ai_task

        inp = DecisionInput.model_validate(ctx.payload)
        task_type = DECISION_TYPE_TO_TASK.get(inp.decision_type, "decisioning")

        # ── Recall past learnings ────────────────────────────
        memory_context = ""
        if ctx.db:
            ops = DBOps(ctx.db)
            memory_context = ops.recall_decisions(
                business_id=ctx.business_id,
                decision_type=inp.decision_type,
            )
            if inp.decision_type == "scale" and inp.channel:
                campaign_memory = ops.recall_campaign_patterns(
                    business_id=ctx.business_id,
                    channel=inp.channel,
                )
                if campaign_memory:
                    memory_context = f"{memory_context}\n\n{campaign_memory}".strip()

        # Build the right payload based on decision type
        if inp.decision_type == "scale":
            ai_payload = {
                "campaign_name": inp.campaign_name,
                "channel": inp.channel,
                "current_budget_cents": inp.current_budget_cents,
                "spent_cents": inp.spent_cents,
                "impressions": inp.impressions,
                "clicks": inp.clicks,
                "conversions": inp.conversions,
                "roas": inp.roas,
                "cpa_cents": inp.cpa_cents,
                "days_remaining": inp.days_remaining,
            }
        elif inp.decision_type == "launch":
            ai_payload = {
                "opportunity": inp.opportunity,
                "market_data": inp.market_data,
                "our_strengths": inp.our_strengths,
            }
        else:
            ai_payload = {
                "context": inp.context,
                "options": inp.options or [],
                "constraints": inp.constraints,
            }

        # Inject memory context into the AI payload
        if memory_context:
            ai_payload["prior_learnings"] = memory_context

        ai_result = await route_ai_task(task_type, ai_payload)

        if not ai_result.success:
            return AgentResult(
                error=f"AI decision failed: {ai_result.error}",
                tokens_used=ai_result.tokens_used,
                cost_cents=ai_result.cost_cents,
            )

        risk_level = ai_result.data.get("risk_level", "medium")
        confidence = ai_result.data.get("confidence", 0)
        decision = ai_result.data.get("decision", "")
        approvals_created: list[str] = []

        # High-risk decisions require human approval
        if ctx.db and risk_level in ("high", "critical"):
            ops = DBOps(ctx.db)
            aid = ops.create_approval(
                business_id=ctx.business_id,
                approval_type="campaign_launch" if inp.decision_type == "launch" else "budget_increase",
                title=f"High-risk decision requires approval: {decision[:80]}",
                description=(
                    f"Decision type: {inp.decision_type}\n"
                    f"Risk level: {risk_level}\n"
                    f"Confidence: {confidence}\n"
                    f"Reason: {ai_result.data.get('reason', '')}"
                ),
                requested_by=self.name,
                payload={
                    "source": "decision_agent",
                    "decision_data": ai_result.data,
                    "original_payload": ai_payload,
                },
            )
            approvals_created.append(aid)
            logger.info(
                "High-risk decision (risk=%s, confidence=%.2f) → approval %s",
                risk_level, confidence, aid,
            )

        # ── Save decision to memory ──────────────────────────
        if ctx.db:
            from abf_ai.memory import save_decision_outcome
            save_decision_outcome(
                ctx.db,
                business_id=ctx.business_id,
                decision_type=inp.decision_type,
                decision=decision,
                outcome="success",
                confidence=confidence,
                reason=ai_result.data.get("reason", ""),
                context=ai_payload,
                agent_name=self.name,
            )

        return AgentResult(
            output={
                "decision_type": inp.decision_type,
                "ai_task_type": task_type,
                **ai_result.data,
                "approvals_created": approvals_created,
                "memory_context_used": bool(memory_context),
            },
            tokens_used=ai_result.tokens_used,
            cost_cents=ai_result.cost_cents,
            approvals_created=approvals_created,
        )
