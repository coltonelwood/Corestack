"""Product Launch Workflow — the first end-to-end ABF workflow.

Steps:
  1. opportunity_analysis  — OpportunityAgent scores the launch
  2. decision_scoring      — DecisionAgent makes the go/no-go call
  3. generate_landing_page — AI router generates landing page copy
  4. generate_ad_copy      — AI router generates ad copy
  5. generate_email_copy   — AI router generates email copy
  6. generate_faq          — AI router generates FAQ
  7. create_campaign_draft — ExecutionAgent creates the campaign record
  8. risk_check            — If high-risk, create approval and pause
  9. finalize              — Mark workflow as ready-for-launch

The workflow pauses at step 8 if the campaign exceeds risk thresholds.
It resumes when the approval is granted.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

from abf_workflows.runner import PersistentWorkflowRunner, StepOutcome

logger = logging.getLogger("abf_workflows.product_launch")

WORKFLOW_TYPE = "product_launch"

# Budget threshold (in cents) above which launch requires approval
HIGH_RISK_BUDGET_THRESHOLD = 500000  # $5,000


class ProductLaunchInput(BaseModel):
    """Input for the product launch workflow."""
    product_name: str
    product_description: str = ""
    category: str = ""
    price: str = ""
    target_audience: str = ""
    brand_voice: str = "Professional and approachable"
    channel: str = "meta"
    budget_cents: int = 0
    market_data: str = ""
    our_strengths: str = ""


def get_steps(inp: ProductLaunchInput) -> list[dict[str, Any]]:
    """Return the step definitions for this workflow."""
    return [
        {
            "key": "opportunity_analysis",
            "name": "Analyze launch opportunity",
            "agent_name": "opportunity",
            "payload": {
                "opportunity": f"Launch {inp.product_name}: {inp.product_description}",
                "market_data": inp.market_data,
                "our_strengths": inp.our_strengths,
                "auto_create_tasks": False,
            },
        },
        {
            "key": "decision_scoring",
            "name": "Score go/no-go decision",
            "agent_name": "decision",
            "payload": {
                "decision_type": "launch",
                "opportunity": f"Launch {inp.product_name}: {inp.product_description}",
                "market_data": inp.market_data,
                "our_strengths": inp.our_strengths,
            },
        },
        {
            "key": "generate_landing_page",
            "name": "Generate landing page copy",
            "agent_name": None,
            "payload": {
                "ai_task": "landing_page_copy",
                "product_name": inp.product_name,
                "value_prop": inp.product_description,
                "target_audience": inp.target_audience,
                "brand_voice": inp.brand_voice,
                "price": inp.price,
            },
        },
        {
            "key": "generate_ad_copy",
            "name": "Generate ad copy",
            "agent_name": None,
            "payload": {
                "ai_task": "ad_copy",
                "product_name": inp.product_name,
                "channel": inp.channel,
                "target_audience": inp.target_audience,
                "goal": "drive purchases",
                "tone": inp.brand_voice,
                "max_headline_chars": 30,
                "max_body_chars": 90,
            },
        },
        {
            "key": "generate_email_copy",
            "name": "Generate email copy",
            "agent_name": None,
            "payload": {
                "ai_task": "content_generation",
                "product_name": inp.product_name,
                "content_type": "launch email",
                "brand_voice": inp.brand_voice,
                "audience": inp.target_audience,
                "length": "200-300 words",
            },
        },
        {
            "key": "generate_faq",
            "name": "Generate FAQ",
            "agent_name": None,
            "payload": {
                "ai_task": "content_generation",
                "product_name": inp.product_name,
                "content_type": "product FAQ",
                "brand_voice": inp.brand_voice,
                "audience": inp.target_audience,
                "length": "5 questions with answers, 300-400 words",
            },
        },
        {
            "key": "create_campaign_draft",
            "name": "Create campaign draft",
            "agent_name": "execution",
            "payload": {
                "action": "launch_campaign",
                "approved": True,  # Already approved through the workflow
                "campaign_name": f"{inp.product_name} Launch",
                "channel": inp.channel,
                "budget_cents": inp.budget_cents,
                "product_name": inp.product_name,
                "target_audience": inp.target_audience,
                "brand_voice": inp.brand_voice,
            },
        },
        {
            "key": "risk_check",
            "name": "Risk assessment and approval check",
            "agent_name": None,
            "payload": {
                "budget_cents": inp.budget_cents,
                "product_name": inp.product_name,
            },
        },
        {
            "key": "finalize",
            "name": "Mark ready for launch",
            "agent_name": None,
            "payload": {},
        },
    ]


async def step_handler(
    step_key: str,
    payload: dict[str, Any],
    db: Any,
    business_id: str,
    prior_outputs: dict[str, dict[str, Any]],
) -> StepOutcome:
    """Execute a single step of the product launch workflow."""

    if step_key == "opportunity_analysis":
        return await _run_agent("opportunity", payload, db, business_id)

    elif step_key == "decision_scoring":
        # Check if opportunity passed
        opp_output = prior_outputs.get("opportunity_analysis", {})
        opp_score = opp_output.get("opportunity_score", 0)
        opp_decision = opp_output.get("decision", "")

        if opp_score < 30 or opp_decision == "pass":
            return StepOutcome(
                success=False,
                error=f"Opportunity scored too low ({opp_score}/100, decision: {opp_decision}). Launch not recommended.",
                output={"opportunity_score": opp_score, "gate": "failed"},
            )

        return await _run_agent("decision", payload, db, business_id)

    elif step_key in ("generate_landing_page", "generate_ad_copy", "generate_email_copy", "generate_faq"):
        return await _run_ai_task(payload)

    elif step_key == "create_campaign_draft":
        return await _run_agent("execution", payload, db, business_id)

    elif step_key == "risk_check":
        return _risk_check(payload, prior_outputs, db, business_id)

    elif step_key == "finalize":
        return _finalize(prior_outputs)

    else:
        return StepOutcome(success=False, error=f"Unknown step: {step_key}")


async def _run_agent(
    agent_name: str,
    payload: dict[str, Any],
    db: Any,
    business_id: str,
) -> StepOutcome:
    """Run an agent and convert its result to a StepOutcome."""
    import abf_agents.builtin  # noqa: F401
    from abf_agents import get_agent
    from abf_agents.base import AgentContext

    agent = get_agent(agent_name)
    ctx = AgentContext(business_id=business_id, payload=payload, db=db)
    result = await agent.run(ctx)

    return StepOutcome(
        success=result.success,
        output=result.output,
        error=result.error,
        tokens_used=result.tokens_used,
        cost_cents=result.cost_cents,
        duration_ms=result.duration_ms,
    )


async def _run_ai_task(payload: dict[str, Any]) -> StepOutcome:
    """Run an AI router task directly (no agent wrapper needed)."""
    from abf_ai.router import route_ai_task

    ai_task = payload.pop("ai_task", "content_generation")
    result = await route_ai_task(ai_task, payload)

    return StepOutcome(
        success=result.success,
        output=result.data,
        error=result.error,
        tokens_used=result.tokens_used,
        cost_cents=result.cost_cents,
        duration_ms=result.duration_ms,
    )


def _risk_check(
    payload: dict[str, Any],
    prior_outputs: dict[str, dict[str, Any]],
    db: Any,
    business_id: str,
) -> StepOutcome:
    """Check if the launch exceeds risk thresholds. If so, create an approval."""
    budget = payload.get("budget_cents", 0)
    product_name = payload.get("product_name", "Product")

    decision_output = prior_outputs.get("decision_scoring", {})
    risk_level = decision_output.get("risk_level", "medium")

    needs_approval = (
        budget >= HIGH_RISK_BUDGET_THRESHOLD
        or risk_level in ("high", "critical")
    )

    if not needs_approval:
        return StepOutcome(
            success=True,
            output={"risk_check": "passed", "budget_cents": budget, "risk_level": risk_level},
        )

    # Create approval
    reason_parts = []
    if budget >= HIGH_RISK_BUDGET_THRESHOLD:
        reason_parts.append(f"budget ${budget/100:,.0f} exceeds ${HIGH_RISK_BUDGET_THRESHOLD/100:,.0f} threshold")
    if risk_level in ("high", "critical"):
        reason_parts.append(f"risk level is {risk_level}")

    reason = "; ".join(reason_parts)

    res = db.table("approvals").insert({
        "business_id": business_id,
        "type": "campaign_launch",
        "title": f"Approve product launch: {product_name}",
        "description": f"Launch requires approval: {reason}.",
        "status": "pending",
        "requested_by": "product_launch_workflow",
        "amount_cents": budget,
        "payload": {
            "workflow_context": "product_launch",
            "risk_level": risk_level,
            "reason": reason,
        },
    }).execute()

    if not res.data:
        return StepOutcome(success=False, error="Failed to create approval record")
    approval_id = res.data[0]["id"]
    logger.info("Risk check: approval required (%s) → %s", reason, approval_id)

    return StepOutcome(
        success=True,
        output={"risk_check": "approval_required", "reason": reason},
        needs_approval=True,
        approval_id=approval_id,
    )


def _finalize(prior_outputs: dict[str, dict[str, Any]]) -> StepOutcome:
    """Compile all generated assets into the final output."""
    return StepOutcome(
        success=True,
        output={
            "status": "ready_for_launch",
            "opportunity": prior_outputs.get("opportunity_analysis", {}),
            "decision": prior_outputs.get("decision_scoring", {}),
            "landing_page": prior_outputs.get("generate_landing_page", {}),
            "ad_copy": prior_outputs.get("generate_ad_copy", {}),
            "email_copy": prior_outputs.get("generate_email_copy", {}),
            "faq": prior_outputs.get("generate_faq", {}),
            "campaign": prior_outputs.get("create_campaign_draft", {}),
            "risk_check": prior_outputs.get("risk_check", {}),
        },
    )


async def trigger(db: Any, business_id: str, input_data: dict[str, Any]) -> dict[str, Any]:
    """Entry point: create a workflow_run record and start executing."""
    inp = ProductLaunchInput.model_validate(input_data)
    steps = get_steps(inp)

    # Create the workflow_run record
    res = db.table("workflow_runs").insert({
        "business_id": business_id,
        "workflow_type": WORKFLOW_TYPE,
        "name": f"Product Launch: {inp.product_name}",
        "status": "running",
        "input_payload": inp.model_dump(),
        "total_steps": len(steps),
    }).execute()
    if not res.data:
        raise ValueError("Failed to create workflow run record")
    wf_id = res.data[0]["id"]

    logger.info("Product launch workflow started: %s for %s", wf_id, inp.product_name)

    runner = PersistentWorkflowRunner(db, wf_id)
    result = await runner.run(steps, step_handler, business_id)

    return {"workflow_run_id": wf_id, **result}


async def resume(db: Any, workflow_run_id: str) -> dict[str, Any]:
    """Resume a paused workflow after approval is granted."""
    # Load the workflow run
    wf_res = db.table("workflow_runs").select("*").eq("id", workflow_run_id).maybe_single().execute()
    if not wf_res.data:
        raise ValueError(f"Workflow run not found: {workflow_run_id}")

    wf = wf_res.data
    if wf["status"] != "paused":
        raise ValueError(f"Workflow is not paused (status: {wf['status']})")

    inp = ProductLaunchInput.model_validate(wf["input_payload"])
    steps = get_steps(inp)

    # Find the paused step and check its approval
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
                # Mark step as completed
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc).isoformat()
                db.table("workflow_step_runs").update({
                    "status": "completed",
                    "output_payload": {"risk_check": "approved"},
                    "completed_at": now,
                }).eq("id", step_run["id"]).execute()

            elif approval.data and approval.data["status"] == "rejected":
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc).isoformat()
                db.table("workflow_step_runs").update({
                    "status": "failed",
                    "error_message": "Approval was rejected",
                    "completed_at": now,
                }).eq("id", step_run["id"]).execute()

                db.table("workflow_runs").update({
                    "status": "failed",
                    "error_message": "Launch approval was rejected",
                    "completed_at": now,
                }).eq("id", workflow_run_id).execute()

                return {"workflow_run_id": workflow_run_id, "status": "failed", "reason": "Approval rejected"}

            else:
                return {"workflow_run_id": workflow_run_id, "status": "paused", "reason": "Approval still pending"}

    logger.info("Resuming product launch workflow: %s", workflow_run_id)

    runner = PersistentWorkflowRunner(db, workflow_run_id)
    result = await runner.run(steps, step_handler, wf["business_id"])

    return {"workflow_run_id": workflow_run_id, **result}
