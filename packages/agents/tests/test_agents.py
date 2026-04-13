"""Tests for the ABF agent layer.

These tests verify agent structure, registration, input validation,
and the execution flow — without calling real LLM providers.
They mock `route_ai_task` to return deterministic results.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

# Import triggers all @register decorators
import abf_agents.builtin  # noqa: F401
from abf_agents import get_agent, registry, AgentContext, AgentResult
from abf_agents.base import DBOps


# ── Registry tests ───────────────────────────────────────────

class TestRegistry:
    def test_core_agents_registered(self):
        agents = registry()
        assert "opportunity" in agents
        assert "decision" in agents
        assert "execution" in agents
        assert "analytics" in agents

    def test_compat_agents_registered(self):
        agents = registry()
        assert "content_writer" in agents
        assert "research_analyst" in agents
        assert "ads_manager" in agents
        assert "operations" in agents
        assert "outreach" in agents

    def test_get_agent_returns_instance(self):
        agent = get_agent("opportunity")
        assert agent.name == "opportunity"
        assert agent.agent_type == "research"

    def test_get_agent_unknown_raises(self):
        with pytest.raises(KeyError, match="Unknown agent"):
            get_agent("nonexistent_agent")


# ── Mock helper ──────────────────────────────────────────────

def _mock_ai_result(data: dict | None = None, success: bool = True):
    """Create a mock TaskResult from route_ai_task."""
    from abf_ai.router import TaskResult
    return TaskResult(
        task_type="test",
        success=success,
        data=data or {
            "decision": "proceed",
            "confidence": 0.85,
            "reason": "Strong market signals",
            "risk_level": "medium",
            "recommended_action": "Launch pilot",
            "opportunity_score": 78,
            "alternatives": [],
            "summary": "Test summary",
            "key_points": ["Point 1"],
            "word_count": 50,
            "original_length_estimate": 200,
            "label": "healthy",
            "secondary_labels": [],
            "reasoning": "Good metrics",
        },
        provider="openai",
        model="gpt-4o",
        tokens_used=500,
        cost_cents=3,
    )


# ── OpportunityAgent tests ───────────────────────────────────

class TestOpportunityAgent:
    @patch("abf_agents.agents.opportunity.route_ai_task", new_callable=AsyncMock)
    def test_execute_success(self, mock_route):
        mock_route.return_value = _mock_ai_result()

        agent = get_agent("opportunity")
        ctx = AgentContext(
            business_id="biz-001",
            payload={
                "opportunity": "Launch men's skincare line",
                "market_data": "$6.2B market, 9% YoY growth",
                "our_strengths": "Strong DTC brand",
            },
        )

        result = asyncio.get_event_loop().run_until_complete(agent.run(ctx))

        assert result.success is True
        assert "opportunity_score" in result.output
        assert result.tokens_used == 500
        assert result.cost_cents == 3
        mock_route.assert_called_once()

    @patch("abf_agents.agents.opportunity.route_ai_task", new_callable=AsyncMock)
    def test_execute_failure(self, mock_route):
        mock_route.return_value = _mock_ai_result(success=False)
        mock_route.return_value.error = "API timeout"

        agent = get_agent("opportunity")
        ctx = AgentContext(
            business_id="biz-001",
            payload={"opportunity": "Test"},
        )

        result = asyncio.get_event_loop().run_until_complete(agent.run(ctx))

        assert result.success is False
        assert "AI scoring failed" in (result.error or "")


# ── DecisionAgent tests ──────────────────────────────────────

class TestDecisionAgent:
    @patch("abf_agents.agents.decision.route_ai_task", new_callable=AsyncMock)
    def test_general_decision(self, mock_route):
        mock_route.return_value = _mock_ai_result({
            "decision": "Add premium bundle",
            "confidence": 0.82,
            "reason": "Higher margin, differentiates from competitor",
            "risk_level": "low",
            "recommended_action": "Create 3 bundle options by Friday",
            "alternatives": ["Match price", "Increase ads"],
        })

        agent = get_agent("decision")
        ctx = AgentContext(
            business_id="biz-001",
            payload={
                "decision_type": "general",
                "context": "Competitor launched at 20% lower price",
                "options": ["Match price", "Add bundle", "Increase ads"],
            },
        )

        result = asyncio.get_event_loop().run_until_complete(agent.run(ctx))

        assert result.success is True
        assert result.output["decision"] == "Add premium bundle"
        assert result.output["confidence"] == 0.82
        assert result.output["decision_type"] == "general"

    @patch("abf_agents.agents.decision.route_ai_task", new_callable=AsyncMock)
    def test_campaign_scaling_decision(self, mock_route):
        mock_route.return_value = _mock_ai_result({
            "decision": "scale_up",
            "confidence": 0.9,
            "reason": "ROAS well above threshold",
            "risk_level": "low",
            "recommended_action": "Increase budget by 50%",
            "recommended_budget_change_pct": 50,
            "projected_roas": 3.8,
            "key_metrics": {},
        })

        agent = get_agent("decision")
        ctx = AgentContext(
            business_id="biz-001",
            payload={
                "decision_type": "scale",
                "campaign_name": "Spring Glow",
                "channel": "meta",
                "roas": 4.2,
                "current_budget_cents": 1500000,
            },
        )

        result = asyncio.get_event_loop().run_until_complete(agent.run(ctx))

        assert result.success is True
        assert result.output["decision"] == "scale_up"
        assert result.output["ai_task_type"] == "campaign_scaling"


# ── ExecutionAgent tests ─────────────────────────────────────

class TestExecutionAgent:
    def test_high_risk_without_approval_blocked(self):
        """High-risk actions without approval should be blocked."""
        agent = get_agent("execution")
        ctx = AgentContext(
            business_id="biz-001",
            payload={
                "action": "launch_campaign",
                "approved": False,
                "campaign_name": "Test Campaign",
            },
        )

        result = asyncio.get_event_loop().run_until_complete(agent.run(ctx))

        assert result.success is True
        assert result.output["status"] == "approval_required"

    def test_unknown_action(self):
        agent = get_agent("execution")
        ctx = AgentContext(
            business_id="biz-001",
            payload={"action": "nonexistent_action"},
        )

        result = asyncio.get_event_loop().run_until_complete(agent.run(ctx))

        assert result.success is False
        assert "Unknown action" in (result.error or "")

    @patch("abf_agents.agents.execution.route_ai_task", new_callable=AsyncMock)
    def test_generate_content(self, mock_route):
        mock_route.return_value = _mock_ai_result({
            "content": "Amazing product description...",
            "word_count": 180,
            "tone": "premium",
            "seo_keywords": ["skincare", "serum"],
            "suggestions": [],
        })

        agent = get_agent("execution")
        ctx = AgentContext(
            business_id="biz-001",
            payload={
                "action": "generate_content",
                "content_type": "product_description",
                "product_name": "Vitamin C Serum",
                "brand_voice": "Premium",
            },
        )

        result = asyncio.get_event_loop().run_until_complete(agent.run(ctx))

        assert result.success is True
        assert result.output["status"] == "content_generated"
        assert result.tokens_used == 500


# ── AnalyticsAgent tests ─────────────────────────────────────

class TestAnalyticsAgent:
    @patch("abf_agents.agents.analytics.route_ai_task", new_callable=AsyncMock)
    def test_business_analysis(self, mock_route):
        # Mock three sequential AI calls (summarize, classify, recommend)
        mock_route.side_effect = [
            _mock_ai_result({
                "summary": "Revenue grew 23% QoQ.",
                "key_points": ["Revenue up", "CPA improving"],
                "word_count": 50,
                "original_length_estimate": 200,
            }),
            _mock_ai_result({
                "label": "strong_growth",
                "confidence": 0.88,
                "secondary_labels": ["healthy"],
                "reasoning": "Revenue and efficiency both improving",
            }),
            _mock_ai_result({
                "decision": "Scale winning campaigns",
                "confidence": 0.82,
                "reason": "Strong ROAS across channels",
                "risk_level": "low",
                "recommended_action": "Increase Meta budget by 30%",
                "alternatives": [],
            }),
        ]

        agent = get_agent("analytics")
        ctx = AgentContext(
            business_id="biz-001",
            payload={
                "analysis_type": "business",
                "time_period": "weekly",
            },
        )

        result = asyncio.get_event_loop().run_until_complete(agent.run(ctx))

        assert result.success is True
        assert "summary" in result.output
        assert "health" in result.output
        assert "recommendations" in result.output
        assert result.tokens_used == 1500  # 500 * 3 calls
        assert result.cost_cents == 9  # 3 * 3 calls
        assert mock_route.call_count == 3


# ── Base class tests ─────────────────────────────────────────

class TestBaseAgent:
    def test_agent_result_defaults(self):
        result = AgentResult()
        assert result.success is False
        assert result.output == {}
        assert result.error is None
        assert result.tasks_created == []
        assert result.approvals_created == []

    def test_agent_context_db_optional(self):
        ctx = AgentContext(business_id="biz-001", payload={"key": "value"})
        assert ctx.db is None
        assert ctx.business_id == "biz-001"

    def test_agent_context_with_db(self):
        ctx = AgentContext(business_id="biz-001", db="mock_db")
        assert ctx.db == "mock_db"
