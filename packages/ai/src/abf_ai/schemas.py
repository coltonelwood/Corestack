"""Strict output schemas for every AI task type.

Each schema defines the exact JSON structure the LLM must return.
High-impact tasks (decisioning, prioritization, opportunity_scoring,
campaign_scaling) enforce decision/confidence/reason/risk_level fields.

Schemas serve double duty:
  1. Injected into the prompt so the LLM knows the output format
  2. Used by Pydantic to validate the parsed response
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ── High-impact decision schemas ─────────────────────────────

class DecisionOutput(BaseModel):
    """Standard output for decisioning tasks."""
    decision: str = Field(description="The recommended decision")
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")
    reason: str = Field(description="Explanation of the reasoning")
    risk_level: str = Field(description="low | medium | high | critical")
    recommended_action: str = Field(description="Concrete next step to take")
    alternatives: list[str] = Field(default_factory=list, description="Other options considered")


class PrioritizationOutput(BaseModel):
    """Standard output for prioritization tasks."""
    ranked_items: list[PrioritizedItem] = Field(description="Items ranked by priority")
    decision: str = Field(description="Summary of the prioritization rationale")
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(description="Why this ordering was chosen")
    risk_level: str
    recommended_action: str


class PrioritizedItem(BaseModel):
    id: str = Field(description="Identifier for the item")
    rank: int = Field(ge=1)
    label: str = Field(description="Item name or title")
    score: float = Field(ge=0, le=100, description="Priority score 0-100")
    rationale: str = Field(description="Why this item got this rank")


# Rebuild PrioritizationOutput now that PrioritizedItem is defined
PrioritizationOutput.model_rebuild()


class OpportunityScoringOutput(BaseModel):
    """Standard output for opportunity scoring tasks."""
    opportunity_score: float = Field(ge=0, le=100, description="Score 0-100")
    decision: str = Field(description="pursue | monitor | pass")
    confidence: float = Field(ge=0, le=1)
    reason: str
    risk_level: str
    recommended_action: str
    factors: list[ScoringFactor] = Field(default_factory=list)


class ScoringFactor(BaseModel):
    name: str
    weight: float = Field(ge=0, le=1)
    score: float = Field(ge=0, le=100)
    note: str = ""


OpportunityScoringOutput.model_rebuild()


class CampaignScalingOutput(BaseModel):
    """Standard output for campaign scaling tasks."""
    decision: str = Field(description="scale_up | maintain | scale_down | pause")
    confidence: float = Field(ge=0, le=1)
    reason: str
    risk_level: str
    recommended_action: str
    recommended_budget_change_pct: float = Field(description="e.g. 50 for +50%, -30 for -30%")
    projected_roas: float | None = Field(default=None, description="Projected return on ad spend")
    key_metrics: dict[str, Any] = Field(default_factory=dict)


# ── Content generation schemas ───────────────────────────────

class ContentGenerationOutput(BaseModel):
    """Output for general content generation."""
    content: str = Field(description="The generated content")
    word_count: int = Field(ge=0)
    tone: str = Field(description="Detected or applied tone")
    seo_keywords: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list, description="Improvement suggestions")


class LandingPageCopyOutput(BaseModel):
    """Output for landing page copy."""
    headline: str
    subheadline: str
    hero_body: str = Field(description="Main hero section copy")
    cta_text: str = Field(description="Call to action button text")
    benefit_points: list[str] = Field(min_length=3)
    social_proof_suggestion: str = ""
    meta_title: str = Field(max_length=60)
    meta_description: str = Field(max_length=160)


class AdCopyOutput(BaseModel):
    """Output for ad copy generation."""
    headlines: list[AdVariant] = Field(min_length=1)
    body_variants: list[AdVariant] = Field(min_length=1)
    cta: str
    target_audience_note: str = ""


class AdVariant(BaseModel):
    text: str
    character_count: int
    angle: str = Field(description="Creative angle: benefit | urgency | social_proof | curiosity")


AdCopyOutput.model_rebuild()


# ── Utility schemas ──────────────────────────────────────────

class SummarizationOutput(BaseModel):
    """Output for summarization tasks."""
    summary: str
    key_points: list[str] = Field(min_length=1)
    word_count: int = Field(ge=0)
    original_length_estimate: int = Field(ge=0, description="Estimated source word count")


class ClassificationOutput(BaseModel):
    """Output for classification tasks."""
    label: str = Field(description="Primary classification label")
    confidence: float = Field(ge=0, le=1)
    secondary_labels: list[str] = Field(default_factory=list)
    reasoning: str = Field(description="Why this classification was chosen")


# ── Registry ─────────────────────────────────────────────────

TASK_SCHEMAS: dict[str, type[BaseModel]] = {
    "decisioning": DecisionOutput,
    "prioritization": PrioritizationOutput,
    "opportunity_scoring": OpportunityScoringOutput,
    "campaign_scaling": CampaignScalingOutput,
    "content_generation": ContentGenerationOutput,
    "landing_page_copy": LandingPageCopyOutput,
    "ad_copy": AdCopyOutput,
    "summarization": SummarizationOutput,
    "classification": ClassificationOutput,
}


def get_schema_json(task_type: str) -> str:
    """Return the JSON schema string for a task type, used in prompts."""
    schema_cls = TASK_SCHEMAS.get(task_type)
    if schema_cls is None:
        raise ValueError(f"Unknown task type: {task_type}")
    import json
    return json.dumps(schema_cls.model_json_schema(), indent=2)
