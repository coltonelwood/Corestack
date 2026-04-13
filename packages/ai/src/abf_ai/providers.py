"""LLM provider clients with timeouts, retries, health checks, and structured logging.

Supports OpenAI and Anthropic. Clients are created once and reused.
Cost estimates use per-model input/output token rates.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from enum import Enum
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger("abf_ai.providers")

DEFAULT_TIMEOUT = 60.0  # seconds


# ── Models ────────���──────────────────────────────────────────

class Provider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class CompletionResult(BaseModel):
    text: str
    provider: Provider
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    tokens_used: int = 0
    cost_cents: int = 0
    duration_ms: int = 0


class ProviderHealth(BaseModel):
    provider: str
    available: bool
    has_key: bool
    error: str | None = None
    latency_ms: int = 0


# ── Cost estimation ──────────���───────────────────────────────
# Rates are per 1M tokens. Costs computed as: (input * in_rate + output * out_rate) / 1_000_000 * 100 cents

_COST_RATES: dict[str, tuple[float, float]] = {
    # (input_per_1M_usd, output_per_1M_usd)
    "gpt-4o":                     (2.50, 10.00),
    "gpt-4o-mini":                (0.15,  0.60),
    "claude-sonnet-4-20250514":   (3.00, 15.00),
    "claude-haiku-4-5-20251001":  (0.80,  4.00),
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> int:
    """Estimate cost in cents based on per-model token rates."""
    rates = _COST_RATES.get(model, (3.00, 15.00))
    cost_usd = (input_tokens * rates[0] + output_tokens * rates[1]) / 1_000_000
    return max(1, round(cost_usd * 100))


# ── Client singletons ────────────��──────────────────────────

_openai_client = None
_anthropic_client = None


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        from openai import AsyncOpenAI
        _openai_client = AsyncOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            timeout=DEFAULT_TIMEOUT,
        )
    return _openai_client


def _get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is None:
        from anthropic import AsyncAnthropic
        _anthropic_client = AsyncAnthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            timeout=DEFAULT_TIMEOUT,
        )
    return _anthropic_client


# ─��� Unified completion ────────────���──────────────────────────

async def complete(
    prompt: str,
    *,
    system: str = "You are a helpful business operations assistant.",
    provider: Provider = Provider.ANTHROPIC,
    model: str | None = None,
    max_tokens: int = 2048,
    temperature: float = 0.7,
    timeout: float = DEFAULT_TIMEOUT,
    **kwargs: Any,
) -> CompletionResult:
    """Unified completion call with timeout and structured logging."""

    start = time.perf_counter()

    if provider == Provider.OPENAI:
        resolved_model = model or os.environ.get("ABF_OPENAI_MODEL", "gpt-4o-mini")
        result = await asyncio.wait_for(
            _openai_complete(prompt, system=system, model=resolved_model,
                             max_tokens=max_tokens, temperature=temperature, **kwargs),
            timeout=timeout,
        )
    else:
        resolved_model = model or os.environ.get("ABF_ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        result = await asyncio.wait_for(
            _anthropic_complete(prompt, system=system, model=resolved_model,
                                max_tokens=max_tokens, temperature=temperature, **kwargs),
            timeout=timeout,
        )

    result.duration_ms = int((time.perf_counter() - start) * 1000)

    logger.info(
        "LLM call: provider=%s model=%s in=%d out=%d total=%d cost=%dc duration=%dms",
        result.provider.value, result.model,
        result.input_tokens, result.output_tokens, result.tokens_used,
        result.cost_cents, result.duration_ms,
    )

    return result


async def complete_with_fallback(
    prompt: str,
    *,
    system: str = "You are a helpful business operations assistant.",
    primary: Provider = Provider.ANTHROPIC,
    fallback: Provider = Provider.OPENAI,
    model: str | None = None,
    fallback_model: str | None = None,
    max_tokens: int = 2048,
    temperature: float = 0.7,
    timeout: float = DEFAULT_TIMEOUT,
) -> CompletionResult:
    """Try primary provider first, fall back to the other on failure."""
    try:
        return await complete(
            prompt, system=system, provider=primary, model=model,
            max_tokens=max_tokens, temperature=temperature, timeout=timeout,
        )
    except Exception as exc:
        logger.warning(
            "Primary provider %s failed, falling back to %s: %s",
            primary.value, fallback.value, exc,
        )
        return await complete(
            prompt, system=system, provider=fallback, model=fallback_model,
            max_tokens=max_tokens, temperature=temperature, timeout=timeout,
        )


# ── Provider implementations ────────────────────────────────

async def _openai_complete(
    prompt: str,
    *,
    system: str,
    model: str,
    max_tokens: int,
    temperature: float,
    **kwargs: Any,
) -> CompletionResult:
    client = _get_openai_client()
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
        **kwargs,
    )
    text = response.choices[0].message.content or ""
    input_tok = response.usage.prompt_tokens if response.usage else 0
    output_tok = response.usage.completion_tokens if response.usage else 0
    total = input_tok + output_tok

    return CompletionResult(
        text=text,
        provider=Provider.OPENAI,
        model=model,
        input_tokens=input_tok,
        output_tokens=output_tok,
        tokens_used=total,
        cost_cents=estimate_cost(model, input_tok, output_tok),
    )


async def _anthropic_complete(
    prompt: str,
    *,
    system: str,
    model: str,
    max_tokens: int,
    temperature: float,
    **kwargs: Any,
) -> CompletionResult:
    client = _get_anthropic_client()
    response = await client.messages.create(
        model=model,
        system=system,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
        **kwargs,
    )
    text = response.content[0].text if response.content else ""
    input_tok = response.usage.input_tokens
    output_tok = response.usage.output_tokens
    total = input_tok + output_tok

    return CompletionResult(
        text=text,
        provider=Provider.ANTHROPIC,
        model=model,
        input_tokens=input_tok,
        output_tokens=output_tok,
        tokens_used=total,
        cost_cents=estimate_cost(model, input_tok, output_tok),
    )


# ── Health checks ────────────────────────────────────────────

async def check_provider_health(provider: Provider) -> ProviderHealth:
    """Quick health check — sends a minimal prompt to verify connectivity."""
    has_key = bool(os.environ.get(
        "OPENAI_API_KEY" if provider == Provider.OPENAI else "ANTHROPIC_API_KEY"
    ))

    if not has_key:
        return ProviderHealth(
            provider=provider.value,
            available=False,
            has_key=False,
            error="API key not configured",
        )

    start = time.perf_counter()
    try:
        result = await complete(
            "Respond with exactly: ok",
            system="You are a health check endpoint. Respond with exactly one word: ok",
            provider=provider,
            max_tokens=5,
            temperature=0,
            timeout=10.0,
        )
        latency = int((time.perf_counter() - start) * 1000)
        return ProviderHealth(
            provider=provider.value,
            available=True,
            has_key=True,
            latency_ms=latency,
        )
    except Exception as exc:
        latency = int((time.perf_counter() - start) * 1000)
        return ProviderHealth(
            provider=provider.value,
            available=False,
            has_key=True,
            error=str(exc),
            latency_ms=latency,
        )
