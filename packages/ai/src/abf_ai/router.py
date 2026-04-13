"""AI task router — routes tasks to the right model with strict output validation.

Usage:
    from abf_ai.router import route_ai_task
    result = await route_ai_task("decisioning", {"context": "...", "options": [...]})

Routing rules:
  GPT-4o      → decisioning, prioritization, opportunity_scoring, campaign_scaling
  Claude      → content_generation, landing_page_copy, ad_copy
  Cheap model → summarization, classification

Every call:
  1. Resolves provider + model from the routing table
  2. Builds a task-specific prompt with the output schema injected
  3. Calls the LLM with retry logic (up to 3 attempts)
  4. Extracts JSON from the response
  5. Validates against the Pydantic schema
  6. Returns a structured TaskResult with cost/latency metadata
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from abf_ai.providers import Provider, CompletionResult, complete
from abf_ai.schemas import TASK_SCHEMAS, get_schema_json

logger = logging.getLogger("abf_ai.router")


# ── Routing table ────────────────────────────────────────────

class RouteConfig(BaseModel):
    """Configuration for how a task type gets routed to a model."""
    provider: Provider
    model: str
    temperature: float = 0.4
    max_tokens: int = 2048
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 60.0
    fallback_provider: Provider | None = None
    fallback_model: str | None = None


# The table. Change a model by editing one line.
ROUTING_TABLE: dict[str, RouteConfig] = {
    # GPT handles analytical / decisioning tasks
    "decisioning": RouteConfig(
        provider=Provider.OPENAI, model="gpt-4o", temperature=0.2, max_tokens=1500,
    ),
    "prioritization": RouteConfig(
        provider=Provider.OPENAI, model="gpt-4o", temperature=0.2, max_tokens=2048,
    ),
    "opportunity_scoring": RouteConfig(
        provider=Provider.OPENAI, model="gpt-4o", temperature=0.2, max_tokens=1500,
    ),
    "campaign_scaling": RouteConfig(
        provider=Provider.OPENAI, model="gpt-4o", temperature=0.3, max_tokens=1500,
    ),
    # Claude handles creative / content tasks
    "content_generation": RouteConfig(
        provider=Provider.ANTHROPIC, model="claude-sonnet-4-20250514", temperature=0.7, max_tokens=3000,
    ),
    "landing_page_copy": RouteConfig(
        provider=Provider.ANTHROPIC, model="claude-sonnet-4-20250514", temperature=0.6, max_tokens=2500,
    ),
    "ad_copy": RouteConfig(
        provider=Provider.ANTHROPIC, model="claude-sonnet-4-20250514", temperature=0.7, max_tokens=2000,
    ),
    # Cheap helper for utility tasks
    "summarization": RouteConfig(
        provider=Provider.OPENAI, model="gpt-4o-mini", temperature=0.3, max_tokens=1500,
    ),
    "classification": RouteConfig(
        provider=Provider.OPENAI, model="gpt-4o-mini", temperature=0.1, max_tokens=1000,
    ),
}


# ── System prompts per task type ─────────────────────────────

SYSTEM_PROMPTS: dict[str, str] = {
    "decisioning": (
        "You are a senior business strategist. Analyze the situation and make a "
        "clear recommendation. Be direct. Quantify risk. Always provide a concrete "
        "next step. Your output MUST be valid JSON matching the schema below."
    ),
    "prioritization": (
        "You are an operations expert who excels at ranking work by impact and "
        "urgency. Score each item objectively. Explain your rationale concisely. "
        "Your output MUST be valid JSON matching the schema below."
    ),
    "opportunity_scoring": (
        "You are a market analyst who scores business opportunities on a 0-100 scale. "
        "Consider market size, competition, timing, and resource requirements. "
        "Your output MUST be valid JSON matching the schema below."
    ),
    "campaign_scaling": (
        "You are a performance marketing expert. Analyze campaign metrics and "
        "recommend whether to scale up, maintain, scale down, or pause. "
        "Base decisions on ROAS, CPA trends, and budget utilization. "
        "Your output MUST be valid JSON matching the schema below."
    ),
    "content_generation": (
        "You are an expert content writer for e-commerce and DTC brands. "
        "Write compelling, on-brand content that converts. "
        "Your output MUST be valid JSON matching the schema below."
    ),
    "landing_page_copy": (
        "You are a conversion copywriter specializing in landing pages. "
        "Write punchy headlines, clear benefit-driven copy, and strong CTAs. "
        "Your output MUST be valid JSON matching the schema below."
    ),
    "ad_copy": (
        "You are a performance marketing copywriter. Write short, high-impact "
        "ad copy optimized for clicks and conversions. Respect character limits. "
        "Your output MUST be valid JSON matching the schema below."
    ),
    "summarization": (
        "You are a concise analyst. Summarize the input into key points. "
        "Be factual, no fluff. Your output MUST be valid JSON matching the schema below."
    ),
    "classification": (
        "You are a classification engine. Categorize the input into the most "
        "appropriate label. Explain your reasoning briefly. "
        "Your output MUST be valid JSON matching the schema below."
    ),
}


# ── Sample payloads (for docs / testing) ─────────────────────

SAMPLE_PAYLOADS: dict[str, dict[str, Any]] = {
    "decisioning": {
        "context": "Our top product's conversion rate dropped 18% after a competitor launched a similar product at 20% lower price.",
        "options": ["Match competitor price", "Add premium bundle", "Increase ad spend", "Launch loyalty program"],
        "constraints": "Q1 budget is fixed. Cannot reduce margin below 40%.",
    },
    "prioritization": {
        "items": [
            {"id": "task-1", "label": "Fix checkout abandonment bug", "effort": "small", "impact": "high"},
            {"id": "task-2", "label": "Launch TikTok campaign", "effort": "medium", "impact": "medium"},
            {"id": "task-3", "label": "Redesign product page", "effort": "large", "impact": "high"},
            {"id": "task-4", "label": "Email welcome sequence", "effort": "small", "impact": "medium"},
        ],
    },
    "opportunity_scoring": {
        "opportunity": "Launch a men's skincare line targeting 25-40 year olds",
        "market_data": "US men's skincare market is $6.2B, growing 9% YoY. Top 3 competitors hold 35% share.",
        "our_strengths": "Strong DTC brand, existing female customer base with 30% male gift purchasers",
    },
    "campaign_scaling": {
        "campaign_name": "Spring Glow Collection Launch",
        "channel": "meta",
        "current_budget_cents": 1500000,
        "spent_cents": 1124000,
        "impressions": 842000,
        "clicks": 23800,
        "conversions": 1420,
        "roas": 4.2,
        "cpa_cents": 792,
        "days_remaining": 12,
    },
    "content_generation": {
        "product_name": "Vitamin C Radiance Serum",
        "brand_voice": "Premium, science-backed, approachable",
        "audience": "Women 25-45 interested in skincare",
        "content_type": "product_description",
        "length": "150-200 words",
    },
    "landing_page_copy": {
        "product_name": "Hyaluronic Moisture Cream",
        "value_prop": "Deep hydration that lasts 72 hours",
        "target_audience": "Women 30-50 with dry skin concerns",
        "brand_voice": "Clinical yet warm",
        "price": "$38",
    },
    "ad_copy": {
        "product_name": "Pre-Workout Ignite",
        "channel": "tiktok",
        "target_audience": "Men 18-35 into fitness",
        "goal": "drive purchases",
        "tone": "energetic, bold",
        "max_headline_chars": 30,
        "max_body_chars": 90,
    },
    "summarization": {
        "text": "Quarterly business review for NovaBright Skincare. Revenue grew 23% QoQ to $284,500. Ad spend was $67,200 with a blended ROAS of 4.2x. Top performing channel was Meta with 1,420 conversions. TikTok showed promise with 2,340 conversions but at higher CPA. Three new products launched with an average sell-through rate of 68% in first 30 days. Customer retention rate improved from 31% to 38% after implementing the email welcome sequence. Main risk: inventory levels on Vitamin C Serum are projected to run out in 14 days at current velocity.",
    },
    "classification": {
        "text": "Customer emailed: 'I ordered the serum 5 days ago and it still hasn't shipped. This is ridiculous. I want a refund.'",
        "categories": ["shipping_issue", "refund_request", "product_complaint", "general_inquiry", "positive_feedback"],
    },
}


# ── Result model ─────────────────────────────────────────────

class TaskResult(BaseModel):
    """Returned by route_ai_task for every call."""
    task_type: str
    success: bool
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    provider: str = ""
    model: str = ""
    tokens_used: int = 0
    cost_cents: int = 0
    duration_ms: int = 0
    retries: int = 0


# ── JSON extraction ──────────────────────────────────────────

_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```")


def _extract_json(text: str) -> dict[str, Any]:
    """Extract JSON from LLM output, handling markdown code blocks."""
    # Try direct parse first
    stripped = text.strip()
    if stripped.startswith("{"):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            pass

    # Try extracting from code block
    match = _JSON_BLOCK_RE.search(text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Last resort: find first { ... } in text
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    start = -1

    raise ValueError("Could not extract valid JSON from LLM response")


# ── Core router function ────────────────────────────────────

async def route_ai_task(
    task_type: str,
    payload: dict[str, Any],
) -> TaskResult:
    """Route an AI task to the correct model, validate output, return structured result.

    Args:
        task_type: One of the 9 supported task types.
        payload: Task-specific input data (see SAMPLE_PAYLOADS for examples).

    Returns:
        TaskResult with validated data, cost, latency, and retry count.
    """
    if task_type not in ROUTING_TABLE:
        return TaskResult(
            task_type=task_type,
            success=False,
            error=f"Unknown task type: {task_type!r}. Available: {list(ROUTING_TABLE)}",
        )

    config = ROUTING_TABLE[task_type]
    system_prompt = SYSTEM_PROMPTS[task_type]
    schema_json = get_schema_json(task_type)
    schema_cls = TASK_SCHEMAS[task_type]

    # Build the user prompt
    user_prompt = (
        f"Task type: {task_type}\n\n"
        f"Input data:\n{json.dumps(payload, indent=2)}\n\n"
        f"Required output JSON schema:\n{schema_json}\n\n"
        "Respond ONLY with valid JSON matching the schema above. No markdown, no explanation outside the JSON."
    )

    start_time = time.perf_counter()
    last_error: str | None = None
    completion: CompletionResult | None = None
    attempts = 0

    for attempt in range(config.max_retries):
        attempts = attempt + 1
        try:
            if config.fallback_provider and attempt == config.max_retries - 1:
                # Last attempt: use fallback provider if configured
                from abf_ai.providers import complete_with_fallback
                completion = await complete_with_fallback(
                    user_prompt,
                    system=system_prompt,
                    primary=config.provider,
                    fallback=config.fallback_provider,
                    model=config.model,
                    fallback_model=config.fallback_model,
                    max_tokens=config.max_tokens,
                    temperature=config.temperature,
                    timeout=config.timeout,
                )
            else:
                completion = await complete(
                    user_prompt,
                    system=system_prompt,
                    provider=config.provider,
                    model=config.model,
                    max_tokens=config.max_tokens,
                    temperature=config.temperature,
                    timeout=config.timeout,
                )

            # Extract and validate JSON
            raw_data = _extract_json(completion.text)
            validated = schema_cls.model_validate(raw_data)

            duration_ms = int((time.perf_counter() - start_time) * 1000)

            logger.info(
                "AI task succeeded: type=%s provider=%s model=%s tokens=%d cost=%dc duration=%dms retries=%d",
                task_type, config.provider.value, config.model,
                completion.tokens_used, completion.cost_cents,
                duration_ms, attempt,
            )

            return TaskResult(
                task_type=task_type,
                success=True,
                data=validated.model_dump(),
                provider=config.provider.value,
                model=config.model,
                tokens_used=completion.tokens_used,
                cost_cents=completion.cost_cents,
                duration_ms=duration_ms,
                retries=attempt,
            )

        except (json.JSONDecodeError, ValueError) as exc:
            last_error = f"JSON extraction failed: {exc}"
            logger.warning(
                "AI task retry %d/%d (JSON parse): type=%s error=%s",
                attempt + 1, config.max_retries, task_type, last_error,
            )
        except ValidationError as exc:
            last_error = f"Schema validation failed: {exc.error_count()} errors — {exc.errors()[0]['msg']}"
            logger.warning(
                "AI task retry %d/%d (validation): type=%s error=%s",
                attempt + 1, config.max_retries, task_type, last_error,
            )
        except asyncio.TimeoutError:
            last_error = f"Timeout after {config.timeout}s"
            logger.warning(
                "AI task retry %d/%d (timeout): type=%s",
                attempt + 1, config.max_retries, task_type,
            )
        except Exception as exc:
            last_error = f"Provider error: {exc}"
            logger.warning(
                "AI task retry %d/%d (provider): type=%s error=%s",
                attempt + 1, config.max_retries, task_type, last_error,
            )

        # Exponential backoff between retries
        if attempt < config.max_retries - 1:
            delay = config.retry_delay * (2 ** attempt)
            await asyncio.sleep(delay)

    # All retries exhausted
    duration_ms = int((time.perf_counter() - start_time) * 1000)
    logger.error(
        "AI task failed after %d attempts: type=%s error=%s duration=%dms",
        attempts, task_type, last_error, duration_ms,
    )

    return TaskResult(
        task_type=task_type,
        success=False,
        error=last_error,
        provider=config.provider.value,
        model=config.model,
        tokens_used=completion.tokens_used if completion else 0,
        cost_cents=completion.cost_cents if completion else 0,
        duration_ms=duration_ms,
        retries=attempts,
    )
