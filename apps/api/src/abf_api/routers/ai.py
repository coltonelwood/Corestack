"""AI endpoints — task routing, completions, and prompt templates.

All AI calls flow through the backend. The frontend never calls
LLM providers directly. The primary entry point is POST /ai/route
which handles model selection, retries, and output validation.
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


# ── Task type literal ────────────────────────────────────────

TaskType = Literal[
    "decisioning",
    "prioritization",
    "opportunity_scoring",
    "campaign_scaling",
    "content_generation",
    "landing_page_copy",
    "ad_copy",
    "summarization",
    "classification",
]


# ── Route endpoint schemas ───────────────────────────────────

class RouteRequest(BaseModel):
    task_type: TaskType
    payload: dict[str, Any]
    business_id: str | None = None

class RouteResponse(BaseModel):
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

class RoutingInfo(BaseModel):
    task_type: str
    provider: str
    model: str
    temperature: float
    max_tokens: int
    max_retries: int
    schema_fields: list[str]


# ── Completion endpoint schemas ──────────────────────────────

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


# ═════════════════════════════════════════════════════════════
#  POST /ai/route  — THE PRIMARY ENTRY POINT
# ═════════════════════════════════════════════════════════════

@router.post("/route")
async def route_task(
    body: RouteRequest,
    db: Client = Depends(get_supabase),
):
    """Route an AI task to the correct model.

    This is the primary way to invoke AI in ABF. It:
    1. Selects the right provider and model based on task_type
    2. Builds a task-specific prompt with the output schema injected
    3. Calls the LLM with retry logic (up to 3 attempts)
    4. Validates the response against a strict Pydantic schema
    5. Returns structured JSON with cost/latency metadata

    Routing rules:
    - GPT-4o → decisioning, prioritization, opportunity_scoring, campaign_scaling
    - Claude Sonnet → content_generation, landing_page_copy, ad_copy
    - GPT-4o-mini → summarization, classification
    """
    from abf_ai.router import route_ai_task

    result = await route_ai_task(body.task_type, body.payload)

    # Audit log
    if body.business_id:
        log_event(
            db,
            actor="ai_router",
            action=f"ai_task:{body.task_type}",
            entity_type="ai",
            business_id=body.business_id,
            diff={
                "task_type": result.task_type,
                "success": result.success,
                "provider": result.provider,
                "model": result.model,
                "tokens_used": result.tokens_used,
                "cost_cents": result.cost_cents,
                "duration_ms": result.duration_ms,
                "retries": result.retries,
            },
        )

    if not result.success:
        logger.warning(
            "AI route failed: type=%s error=%s",
            body.task_type, result.error,
        )

    return ok(RouteResponse(
        task_type=result.task_type,
        success=result.success,
        data=result.data,
        error=result.error,
        provider=result.provider,
        model=result.model,
        tokens_used=result.tokens_used,
        cost_cents=result.cost_cents,
        duration_ms=result.duration_ms,
        retries=result.retries,
    ).model_dump())


# ═════════════════════════════════════════════════════════════
#  GET /ai/route/config — inspect the routing table
# ═════════════════════════════════════════════════════════════

@router.get("/route/config")
def get_routing_config():
    """Return the full routing table: which model handles which task type."""
    from abf_ai.router import ROUTING_TABLE
    from abf_ai.schemas import TASK_SCHEMAS

    configs = []
    for task_type, config in ROUTING_TABLE.items():
        schema_cls = TASK_SCHEMAS.get(task_type)
        fields = list(schema_cls.model_fields.keys()) if schema_cls else []
        configs.append(RoutingInfo(
            task_type=task_type,
            provider=config.provider.value,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            max_retries=config.max_retries,
            schema_fields=fields,
        ).model_dump())
    return ok_list(configs)


# ═════════════════════════════════════════════════════════════
#  GET /ai/route/samples — sample payloads for each task type
# ═════════════════════════════════════════════════════════════

@router.get("/route/samples")
def get_sample_payloads():
    """Return sample payloads for each task type (useful for docs/testing)."""
    from abf_ai.router import SAMPLE_PAYLOADS
    return ok(SAMPLE_PAYLOADS)


# ═════════════════════════════════════════════════════════════
#  GET /ai/route/schema/{task_type} — output schema for a task
# ═════════════════════════════════════════════════════════════

@router.get("/route/schema/{task_type}")
def get_task_schema(task_type: TaskType):
    """Return the JSON schema that the LLM output must conform to."""
    from abf_ai.schemas import TASK_SCHEMAS
    schema_cls = TASK_SCHEMAS.get(task_type)
    if schema_cls is None:
        raise ABFError(f"Unknown task type: {task_type}", code="UNKNOWN_TASK_TYPE")
    return ok(schema_cls.model_json_schema())


# ═════════════════════════════════════════════════════════════
#  Provider health checks
# ═════════════════════════════════════════════════════════════

@router.get("/health")
async def ai_health():
    """Check health of all AI providers.

    Returns connectivity status, API key presence, and latency for
    each provider. Does NOT count toward billing in mock/test mode.
    """
    from abf_ai.providers import check_provider_health, Provider

    results = {}
    for provider in Provider:
        health = await check_provider_health(provider)
        results[provider.value] = health.model_dump()

    all_ok = all(r["available"] for r in results.values())

    return ok({
        "status": "ok" if all_ok else "degraded",
        "providers": results,
    })


@router.post("/test")
async def test_ai_task(
    body: RouteRequest,
    db: Client = Depends(get_supabase),
):
    """Test an AI task with debug information.

    Same as /ai/route but includes the raw LLM response text and
    the rendered prompt for debugging. Not for production use.
    """
    from abf_ai.router import route_ai_task, ROUTING_TABLE, SYSTEM_PROMPTS
    from abf_ai.schemas import get_schema_json
    import json as _json

    config = ROUTING_TABLE.get(body.task_type)
    if not config:
        raise ABFError(f"Unknown task type: {body.task_type}", code="UNKNOWN_TASK_TYPE")

    # Show the exact prompt that will be sent
    schema_json = get_schema_json(body.task_type)
    rendered_prompt = (
        f"Task type: {body.task_type}\n\n"
        f"Input data:\n{_json.dumps(body.payload, indent=2)}\n\n"
        f"Required output JSON schema:\n{schema_json}\n\n"
        "Respond ONLY with valid JSON matching the schema above."
    )

    result = await route_ai_task(body.task_type, body.payload)

    return ok({
        "result": result.model_dump(),
        "debug": {
            "provider": config.provider.value,
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "timeout": config.timeout,
            "system_prompt": SYSTEM_PROMPTS.get(body.task_type, ""),
            "rendered_prompt_preview": rendered_prompt[:500],
            "has_fallback": config.fallback_provider is not None,
        },
    })


# ═════════════════════════════════════════════════════════════
#  Completions + templates
# ═════════════════════════════════════════════════════════════

@router.post("/completions")
async def create_completion(
    body: CompletionRequest,
    db: Client = Depends(get_supabase),
):
    """Run an ad-hoc LLM completion (no schema validation)."""
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
        raise ABFError(f"Missing template variable: {exc}", code="MISSING_VARIABLE")

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
