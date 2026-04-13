"""LLM provider abstraction.

Supports OpenAI and Anthropic with a unified interface.
"""

from __future__ import annotations

import os
from enum import Enum
from typing import Any

from pydantic import BaseModel


class Provider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class CompletionResult(BaseModel):
    text: str
    provider: Provider
    model: str
    tokens_used: int
    cost_cents: int


def _estimate_cost(provider: Provider, model: str, tokens: int) -> int:
    """Rough cost estimate in cents. Refine per-model as needed."""
    rates: dict[str, float] = {
        "gpt-4o": 0.005,
        "gpt-4o-mini": 0.00015,
        "claude-sonnet-4-20250514": 0.003,
        "claude-haiku-4-5-20251001": 0.0008,
    }
    rate = rates.get(model, 0.003)
    return max(1, round(tokens * rate * 100))


async def complete(
    prompt: str,
    *,
    system: str = "You are a helpful business operations assistant.",
    provider: Provider = Provider.ANTHROPIC,
    model: str | None = None,
    max_tokens: int = 2048,
    temperature: float = 0.7,
    **kwargs: Any,
) -> CompletionResult:
    """Unified completion call across providers."""

    if provider == Provider.OPENAI:
        return await _openai_complete(
            prompt, system=system, model=model or "gpt-4o-mini",
            max_tokens=max_tokens, temperature=temperature, **kwargs,
        )
    else:
        return await _anthropic_complete(
            prompt, system=system, model=model or "claude-sonnet-4-20250514",
            max_tokens=max_tokens, temperature=temperature, **kwargs,
        )


async def _openai_complete(
    prompt: str,
    *,
    system: str,
    model: str,
    max_tokens: int,
    temperature: float,
    **kwargs: Any,
) -> CompletionResult:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
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
    tokens = response.usage.total_tokens if response.usage else 0

    return CompletionResult(
        text=text,
        provider=Provider.OPENAI,
        model=model,
        tokens_used=tokens,
        cost_cents=_estimate_cost(Provider.OPENAI, model, tokens),
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
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = await client.messages.create(
        model=model,
        system=system,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
        **kwargs,
    )
    text = response.content[0].text if response.content else ""
    tokens = response.usage.input_tokens + response.usage.output_tokens

    return CompletionResult(
        text=text,
        provider=Provider.ANTHROPIC,
        model=model,
        tokens_used=tokens,
        cost_cents=_estimate_cost(Provider.ANTHROPIC, model, tokens),
    )
