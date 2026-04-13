"""AI endpoints — completions and prompt template management.

All AI calls flow through the backend. The frontend never calls
LLM providers directly.
"""

import logging
from typing import Any, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.errors import ABFError
from abf_api.responses import ok, ok_list
from abf_api.services.audit import log_event

logger = logging.getLogger("abf_api.ai")

router = APIRouter(prefix="/ai", tags=["ai"])


# ── Schemas ──────────────────────────────────────────────────

class CompletionRequest(BaseModel):
    prompt: str
    system: str = "You are a helpful business operations assistant."
    provider: Literal["openai", "anthropic"] = "anthropic"
    model: str | None = None
    max_tokens: int = 2048
    temperature: float = 0.7
    business_id: str | None = None

class CompletionResponse(BaseModel):
    text: str
    provider: str
    model: str
    tokens_used: int
    cost_cents: int

class TemplateRenderRequest(BaseModel):
    template_name: str
    variables: dict[str, str] = Field(default_factory=dict)
    provider: Literal["openai", "anthropic"] = "anthropic"
    model: str | None = None
    business_id: str | None = None

class TemplateInfo(BaseModel):
    name: str
    description: str
    system: str
    template: str


# ── Endpoints ────────────────────────────────────────────────

@router.post("/completions")
async def create_completion(
    body: CompletionRequest,
    db: Client = Depends(get_supabase),
):
    """Run an ad-hoc LLM completion. All AI calls flow through this endpoint."""
    from abf_ai.providers import complete, Provider

    try:
        provider = Provider(body.provider)
        result = await complete(
            body.prompt,
            system=body.system,
            provider=provider,
            model=body.model,
            max_tokens=body.max_tokens,
            temperature=body.temperature,
        )
    except Exception as exc:
        logger.error("AI completion failed: %s", exc)
        raise ABFError(f"AI completion failed: {exc}", status_code=502, code="AI_ERROR")

    logger.info(
        "AI completion: provider=%s model=%s tokens=%d cost=%dc",
        result.provider, result.model, result.tokens_used, result.cost_cents,
    )

    if body.business_id:
        log_event(
            db,
            actor="api",
            action="ai_completion",
            entity_type="ai",
            business_id=body.business_id,
            diff={
                "provider": result.provider,
                "model": result.model,
                "tokens_used": result.tokens_used,
                "cost_cents": result.cost_cents,
            },
        )

    return ok(CompletionResponse(
        text=result.text,
        provider=result.provider,
        model=result.model,
        tokens_used=result.tokens_used,
        cost_cents=result.cost_cents,
    ).model_dump())


@router.get("/templates")
def list_templates():
    """List all available prompt templates."""
    from abf_ai.prompts import TEMPLATES

    templates = [
        TemplateInfo(
            name=t.name,
            description=t.description,
            system=t.system,
            template=t.template,
        )
        for t in TEMPLATES.values()
    ]
    return ok_list([t.model_dump() for t in templates])


@router.post("/templates/render")
async def render_template(
    body: TemplateRenderRequest,
    db: Client = Depends(get_supabase),
):
    """Render a prompt template with variables and run it through the LLM."""
    from abf_ai.prompts import TEMPLATES
    from abf_ai.providers import complete, Provider

    template = TEMPLATES.get(body.template_name)
    if template is None:
        raise ABFError(
            f"Unknown template: {body.template_name}. Available: {list(TEMPLATES.keys())}",
            code="UNKNOWN_TEMPLATE",
        )

    try:
        rendered = template.render(**body.variables)
    except KeyError as exc:
        raise ABFError(
            f"Missing template variable: {exc}",
            code="MISSING_VARIABLE",
        )

    try:
        provider = Provider(body.provider)
        result = await complete(
            rendered,
            system=template.system,
            provider=provider,
            model=body.model,
        )
    except Exception as exc:
        logger.error("Template render completion failed: %s", exc)
        raise ABFError(f"AI completion failed: {exc}", status_code=502, code="AI_ERROR")

    logger.info(
        "Template rendered: %s (tokens=%d, cost=%dc)",
        body.template_name, result.tokens_used, result.cost_cents,
    )

    if body.business_id:
        log_event(
            db,
            actor="api",
            action="ai_template",
            entity_type="ai",
            business_id=body.business_id,
            diff={"template": body.template_name, "variables": body.variables},
        )

    return ok({
        "template": body.template_name,
        "rendered_prompt": rendered,
        "completion": CompletionResponse(
            text=result.text,
            provider=result.provider,
            model=result.model,
            tokens_used=result.tokens_used,
            cost_cents=result.cost_cents,
        ).model_dump(),
    })
