"""Campaign Optimization Workflow.

Analyzes a running campaign and produces a concrete recommendation:
scale, hold, pause, or kill — with confidence, rationale, and guardrails.

Steps:
  1. pull_metrics       — Load campaign data from the database
  2. analyze_metrics    — Compute derived KPIs (CTR, conv rate, CPA, ROAS, burn rate)
  3. ai_decision        — DecisionAgent scores: scale | hold | pause | kill
  4. guardrail_check    — Validate decision against hard thresholds
  5. apply_or_approve   — Low-risk auto-applies; high-risk creates approval
  6. log_recommendation — Write audit log with full context

Thresholds (editable in GUARDRAILS):
  - ROAS < 1.0     → force kill
  - ROAS < 1.5     → force pause
  - Budget increase > 50% → requires approval
  - Budget increase > 25% on campaigns < 7 days old → requires approval
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel

from abf_workflows.runner import PersistentWorkflowRunner, StepOutcome

logger = logging.getLogger("abf_workflows.campaign_optimization")

WORKFLOW_TYPE = "campaign_optimization"


# ── Guardrail thresholds ─────────────────────────────────────

class Guardrails(BaseModel):
    min_roas_kill: float = 1.0
    min_roas_pause: float = 1.5
    min_roas_scale: float = 2.0
    max_budget_increase_pct_auto: float = 25.0
    max_budget_increase_pct_young_campaign: float = 25.0
    young_campaign_days: int = 7
    min_conversions_for_decision: int = 10
    max_cpa_multiple_vs_target: float = 2.0

GUARDRAILS = Guardrails()


# ── Input schema ─────────────────────────────────────────────

class CampaignOptInput(BaseModel):
    campaign_id: str
    target_cpa_cents: int = 0
    target_roas: float = 0


# ── Step definitions ─────────────────────────────────────────

def get_steps(inp: CampaignOptInput) -> list[dict[str, Any]]:
    return [
        {
            "key": "pull_metrics",
            "name": "Pull campaign metrics",
            "agent_name": None,
            "payload": {"campaign_id": inp.campaign_id},
        },
        {
            "key": "analyze_metrics",
            "name": "Compute derived KPIs",
            "agent_name": None,
            "payload": {
                "target_cpa_cents": inp.target_cpa_cents,
                "target_roas": inp.target_roas,
            },
        },
        {
            "key": "ai_decision",
            "name": "AI decision: scale / hold / pause / kill",
            "agent_name": "decision",
            "payload": {"decision_type": "scale"},
        },
        {
            "key": "guardrail_check",
            "name": "Validate against guardrails",
            "agent_name": None,
            "payload": {},
        },
        {
            "key": "apply_or_approve",
            "name": "Apply recommendation or request approval",
            "agent_name": None,
            "payload": {},
        },
        {
            "key": "log_recommendation",
            "name": "Log recommendation to audit trail",
            "agent_name": None,
            "payload": {},
        },
    ]


# ── Step handler ─────────────────────────────────────────────

async def step_handler(
    step_key: str,
    payload: dict[str, Any],
    db: Any,
    business_id: str,
    prior_outputs: dict[str, dict[str, Any]],
) -> StepOutcome:

    if step_key == "pull_metrics":
        return _pull_metrics(payload, db)

    elif step_key == "analyze_metrics":
        return _analyze_metrics(payload, prior_outputs)

    elif step_key == "ai_decision":
        return await _ai_decision(prior_outputs, db, business_id)

    elif step_key == "guardrail_check":
        return _guardrail_check(prior_outputs)

    elif step_key == "apply_or_approve":
        return _apply_or_approve(prior_outputs, db, business_id)

    elif step_key == "log_recommendation":
        return _log_recommendation(prior_outputs, db, business_id)

    return StepOutcome(success=False, error=f"Unknown step: {step_key}")


# ── Step implementations ─────────────────────────────────────

def _pull_metrics(payload: dict[str, Any], db: Any) -> StepOutcome:
    """Load campaign row from the database."""
    campaign_id = payload.get("campaign_id")
    if not campaign_id:
        return StepOutcome(success=False, error="campaign_id is required")

    res = db.table("campaigns").select("*").eq("id", campaign_id).maybe_single().execute()
    if not res.data:
        return StepOutcome(success=False, error=f"Campaign not found: {campaign_id}")

    c = res.data

    # Also pull the business name
    biz = db.table("businesses").select("name").eq("id", c["business_id"]).maybe_single().execute()

    return StepOutcome(
        success=True,
        output={
            "campaign_id": c["id"],
            "campaign_name": c["name"],
            "business_id": c["business_id"],
            "business_name": (biz.data or {}).get("name", ""),
            "channel": c["channel"],
            "status": c["status"],
            "budget_cents": c["budget_cents"],
            "spent_cents": c["spent_cents"],
            "impressions": c["impressions"],
            "clicks": c["clicks"],
            "conversions": c["conversions"],
            "start_date": c.get("start_date"),
            "end_date": c.get("end_date"),
        },
    )


def _analyze_metrics(
    payload: dict[str, Any],
    prior_outputs: dict[str, dict[str, Any]],
) -> StepOutcome:
    """Compute derived KPIs from raw metrics."""
    metrics = prior_outputs.get("pull_metrics", {})
    if not metrics:
        return StepOutcome(success=False, error="No metrics from pull_metrics step")

    impressions = metrics.get("impressions", 0)
    clicks = metrics.get("clicks", 0)
    conversions = metrics.get("conversions", 0)
    spent = metrics.get("spent_cents", 0)
    budget = metrics.get("budget_cents", 1)

    ctr = (clicks / max(impressions, 1)) * 100
    conv_rate = (conversions / max(clicks, 1)) * 100
    cpa_cents = spent // max(conversions, 1)
    roas = (conversions * 5000) / max(spent, 1)  # Assume $50 AOV for ROAS estimate
    budget_utilization = (spent / max(budget, 1)) * 100
    remaining_budget_cents = budget - spent

    # Days analysis
    start = metrics.get("start_date")
    end = metrics.get("end_date")
    days_running = 0
    if start:
        from datetime import date
        try:
            start_d = date.fromisoformat(str(start))
            end_d = date.fromisoformat(str(end)) if end else date.today()
            days_running = max((date.today() - start_d).days, 1)
        except (ValueError, TypeError):
            days_running = 1

    target_cpa = payload.get("target_cpa_cents", 0)
    target_roas = payload.get("target_roas", 0)

    analysis = {
        **metrics,
        "ctr_pct": round(ctr, 2),
        "conv_rate_pct": round(conv_rate, 2),
        "cpa_cents": cpa_cents,
        "roas": round(roas, 2),
        "budget_utilization_pct": round(budget_utilization, 1),
        "remaining_budget_cents": remaining_budget_cents,
        "days_running": days_running,
        "target_cpa_cents": target_cpa,
        "target_roas": target_roas,
        "has_sufficient_data": conversions >= GUARDRAILS.min_conversions_for_decision,
    }

    return StepOutcome(success=True, output=analysis)


async def _ai_decision(
    prior_outputs: dict[str, dict[str, Any]],
    db: Any,
    business_id: str,
) -> StepOutcome:
    """Ask the DecisionAgent for a scale/hold/pause/kill recommendation."""
    analysis = prior_outputs.get("analyze_metrics", {})
    if not analysis:
        return StepOutcome(success=False, error="No analysis data available")

    import abf_agents.builtin  # noqa: F401
    from abf_agents import get_agent
    from abf_agents.base import AgentContext

    agent = get_agent("decision")
    ctx = AgentContext(
        business_id=business_id,
        db=db,
        payload={
            "decision_type": "scale",
            "campaign_name": analysis.get("campaign_name", ""),
            "channel": analysis.get("channel", ""),
            "current_budget_cents": analysis.get("budget_cents", 0),
            "spent_cents": analysis.get("spent_cents", 0),
            "impressions": analysis.get("impressions", 0),
            "clicks": analysis.get("clicks", 0),
            "conversions": analysis.get("conversions", 0),
            "roas": analysis.get("roas", 0),
            "cpa_cents": analysis.get("cpa_cents", 0),
            "days_remaining": max(0, 30 - analysis.get("days_running", 0)),
        },
    )

    result = await agent.run(ctx)

    if not result.success:
        return StepOutcome(
            success=False,
            error=f"AI decision failed: {result.error}",
            tokens_used=result.tokens_used,
            cost_cents=result.cost_cents,
            duration_ms=result.duration_ms,
        )

    return StepOutcome(
        success=True,
        output={
            "decision": result.output.get("decision", "hold"),
            "confidence": result.output.get("confidence", 0),
            "reason": result.output.get("reason", ""),
            "risk_level": result.output.get("risk_level", "medium"),
            "recommended_action": result.output.get("recommended_action", ""),
            "recommended_budget_change_pct": result.output.get("recommended_budget_change_pct", 0),
            "projected_roas": result.output.get("projected_roas"),
            "key_metrics": result.output.get("key_metrics", {}),
        },
        tokens_used=result.tokens_used,
        cost_cents=result.cost_cents,
        duration_ms=result.duration_ms,
    )


def _guardrail_check(prior_outputs: dict[str, dict[str, Any]]) -> StepOutcome:
    """Apply hard thresholds that override the AI decision if needed."""
    analysis = prior_outputs.get("analyze_metrics", {})
    ai_decision = prior_outputs.get("ai_decision", {})

    roas = analysis.get("roas", 0)
    conversions = analysis.get("conversions", 0)
    decision = ai_decision.get("decision", "hold")
    budget_change = ai_decision.get("recommended_budget_change_pct", 0)
    days_running = analysis.get("days_running", 0)
    confidence = ai_decision.get("confidence", 0)

    overrides: list[str] = []
    final_decision = decision

    # Hard override: force kill on very low ROAS
    if roas < GUARDRAILS.min_roas_kill and conversions >= GUARDRAILS.min_conversions_for_decision:
        final_decision = "kill"
        overrides.append(f"ROAS {roas:.2f} < {GUARDRAILS.min_roas_kill} kill threshold")

    # Hard override: force pause on low ROAS
    elif roas < GUARDRAILS.min_roas_pause and conversions >= GUARDRAILS.min_conversions_for_decision:
        if final_decision in ("scale", "hold"):
            final_decision = "pause"
            overrides.append(f"ROAS {roas:.2f} < {GUARDRAILS.min_roas_pause} pause threshold")

    # Prevent scaling with insufficient ROAS
    if final_decision == "scale" and roas < GUARDRAILS.min_roas_scale:
        final_decision = "hold"
        overrides.append(f"ROAS {roas:.2f} < {GUARDRAILS.min_roas_scale} scale threshold — downgraded to hold")

    # Insufficient data guard
    if not analysis.get("has_sufficient_data") and final_decision in ("scale", "kill"):
        final_decision = "hold"
        overrides.append(f"Only {conversions} conversions — insufficient data to {decision}")

    # Determine if approval needed for budget changes
    needs_approval = False
    approval_reason = ""

    if final_decision == "scale" and budget_change > 0:
        if budget_change > GUARDRAILS.max_budget_increase_pct_auto:
            needs_approval = True
            approval_reason = f"Budget increase {budget_change:.0f}% exceeds {GUARDRAILS.max_budget_increase_pct_auto:.0f}% auto-approve limit"
        elif (
            days_running < GUARDRAILS.young_campaign_days
            and budget_change > GUARDRAILS.max_budget_increase_pct_young_campaign
        ):
            needs_approval = True
            approval_reason = f"Campaign is only {days_running}d old — budget increase needs approval"

    # Low confidence override
    if confidence < 0.5 and final_decision == "scale":
        final_decision = "hold"
        overrides.append(f"Confidence {confidence:.2f} too low to scale — downgraded to hold")

    return StepOutcome(
        success=True,
        output={
            "original_decision": decision,
            "final_decision": final_decision,
            "overrides": overrides,
            "needs_approval": needs_approval,
            "approval_reason": approval_reason,
            "guardrails_applied": {
                "min_roas_kill": GUARDRAILS.min_roas_kill,
                "min_roas_pause": GUARDRAILS.min_roas_pause,
                "min_roas_scale": GUARDRAILS.min_roas_scale,
                "max_budget_increase_pct_auto": GUARDRAILS.max_budget_increase_pct_auto,
            },
        },
    )


def _apply_or_approve(
    prior_outputs: dict[str, dict[str, Any]],
    db: Any,
    business_id: str,
) -> StepOutcome:
    """Either auto-apply the recommendation or create an approval request."""
    guardrail = prior_outputs.get("guardrail_check", {})
    ai_decision = prior_outputs.get("ai_decision", {})
    analysis = prior_outputs.get("analyze_metrics", {})

    final_decision = guardrail.get("final_decision", "hold")
    needs_approval = guardrail.get("needs_approval", False)
    approval_reason = guardrail.get("approval_reason", "")
    campaign_id = analysis.get("campaign_id")
    campaign_name = analysis.get("campaign_name", "Campaign")
    budget_change = ai_decision.get("recommended_budget_change_pct", 0)

    recommendation = {
        "campaign_id": campaign_id,
        "campaign_name": campaign_name,
        "decision": final_decision,
        "confidence": ai_decision.get("confidence", 0),
        "reason": ai_decision.get("reason", ""),
        "risk_level": ai_decision.get("risk_level", "medium"),
        "recommended_action": ai_decision.get("recommended_action", ""),
        "recommended_budget_change_pct": budget_change,
        "overrides": guardrail.get("overrides", []),
    }

    if needs_approval:
        res = db.table("approvals").insert({
            "business_id": business_id,
            "type": "budget_increase",
            "title": f"Campaign optimization: {final_decision} — {campaign_name}",
            "description": approval_reason,
            "status": "pending",
            "requested_by": "campaign_optimization_workflow",
            "amount_cents": int(analysis.get("budget_cents", 0) * budget_change / 100) if budget_change > 0 else None,
            "payload": recommendation,
        }).execute()

        approval_id = res.data[0]["id"]
        logger.info("Optimization requires approval: %s → %s", campaign_name, approval_id)

        return StepOutcome(
            success=True,
            output={**recommendation, "status": "pending_approval", "approval_id": approval_id},
            needs_approval=True,
            approval_id=approval_id,
        )

    # Auto-apply: update campaign metadata with recommendation
    db.table("campaigns").update({
        "metadata": {"last_optimization": recommendation},
    }).eq("id", campaign_id).execute()

    logger.info(
        "Optimization auto-applied: %s → %s (confidence=%.2f)",
        campaign_name, final_decision, recommendation["confidence"],
    )

    return StepOutcome(
        success=True,
        output={**recommendation, "status": "applied"},
    )


def _log_recommendation(
    prior_outputs: dict[str, dict[str, Any]],
    db: Any,
    business_id: str,
) -> StepOutcome:
    """Write the recommendation to audit_logs and save to memory."""
    apply_result = prior_outputs.get("apply_or_approve", {})
    analysis = prior_outputs.get("analyze_metrics", {})

    # Audit log
    try:
        db.table("audit_logs").insert({
            "business_id": business_id,
            "actor": "campaign_optimization_workflow",
            "action": f"campaign_recommendation:{apply_result.get('decision', 'unknown')}",
            "entity_type": "campaign",
            "entity_id": analysis.get("campaign_id"),
            "diff": {
                "decision": apply_result.get("decision"),
                "confidence": apply_result.get("confidence"),
                "reason": apply_result.get("reason"),
                "risk_level": apply_result.get("risk_level"),
                "overrides": apply_result.get("overrides", []),
                "status": apply_result.get("status"),
                "roas": analysis.get("roas"),
                "cpa_cents": analysis.get("cpa_cents"),
                "budget_utilization_pct": analysis.get("budget_utilization_pct"),
            },
        }).execute()
    except Exception:
        logger.exception("Failed to log campaign recommendation")

    # Save campaign pattern to memory for future decisions
    from abf_ai.memory import save_campaign_pattern
    save_campaign_pattern(
        db,
        business_id=business_id,
        campaign_name=analysis.get("campaign_name", ""),
        channel=analysis.get("channel", ""),
        decision=apply_result.get("decision", "hold"),
        roas=analysis.get("roas", 0),
        cpa_cents=analysis.get("cpa_cents", 0),
        confidence=apply_result.get("confidence", 0),
        reason=apply_result.get("reason", ""),
    )

    return StepOutcome(
        success=True,
        output={"logged": True, "memory_saved": True, "recommendation": apply_result},
    )


# ── Entry points ─────────────────────────────────────────────

async def trigger(db: Any, business_id: str, input_data: dict[str, Any]) -> dict[str, Any]:
    inp = CampaignOptInput.model_validate(input_data)
    steps = get_steps(inp)

    res = db.table("workflow_runs").insert({
        "business_id": business_id,
        "workflow_type": WORKFLOW_TYPE,
        "name": f"Campaign Optimization: {inp.campaign_id[:8]}",
        "status": "running",
        "input_payload": inp.model_dump(),
        "total_steps": len(steps),
    }).execute()
    wf_id = res.data[0]["id"]

    logger.info("Campaign optimization started: %s for campaign %s", wf_id, inp.campaign_id)

    runner = PersistentWorkflowRunner(db, wf_id)
    result = await runner.run(steps, step_handler, business_id)

    return {"workflow_run_id": wf_id, **result}


async def resume(db: Any, workflow_run_id: str) -> dict[str, Any]:
    wf_res = db.table("workflow_runs").select("*").eq("id", workflow_run_id).maybe_single().execute()
    if not wf_res.data:
        raise ValueError(f"Workflow run not found: {workflow_run_id}")

    wf = wf_res.data
    if wf["status"] != "paused":
        raise ValueError(f"Workflow is not paused (status: {wf['status']})")

    inp = CampaignOptInput.model_validate(wf["input_payload"])
    steps = get_steps(inp)

    # Check approval status on paused steps
    step_runs = (
        db.table("workflow_step_runs")
        .select("*")
        .eq("workflow_run_id", workflow_run_id)
        .eq("status", "waiting_approval")
        .execute()
    )

    for step_run in (step_runs.data or []):
        approval_id = step_run.get("approval_id")
        if approval_id:
            approval = db.table("approvals").select("status").eq("id", approval_id).maybe_single().execute()
            if approval.data and approval.data["status"] == "approved":
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc).isoformat()
                db.table("workflow_step_runs").update({
                    "status": "completed",
                    "output_payload": {
                        **(step_run.get("output_payload") or {}),
                        "status": "approved",
                    },
                    "completed_at": now,
                }).eq("id", step_run["id"]).execute()

            elif approval.data and approval.data["status"] == "rejected":
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc).isoformat()
                db.table("workflow_step_runs").update({
                    "status": "failed",
                    "error_message": "Budget increase approval was rejected",
                    "completed_at": now,
                }).eq("id", step_run["id"]).execute()
                db.table("workflow_runs").update({
                    "status": "failed",
                    "error_message": "Budget increase approval was rejected",
                    "completed_at": now,
                }).eq("id", workflow_run_id).execute()
                return {"workflow_run_id": workflow_run_id, "status": "failed", "reason": "Approval rejected"}
            else:
                return {"workflow_run_id": workflow_run_id, "status": "paused", "reason": "Approval still pending"}

    runner = PersistentWorkflowRunner(db, workflow_run_id)
    result = await runner.run(steps, step_handler, wf["business_id"])
    return {"workflow_run_id": workflow_run_id, **result}
