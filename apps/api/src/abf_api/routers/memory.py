"""Memory endpoints — browse and manage agent learnings."""

import logging
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from supabase import Client

from abf_api.deps.supabase import get_supabase
from abf_api.responses import ok, ok_list

logger = logging.getLogger("abf_api.memory")

router = APIRouter(prefix="/memory", tags=["memory"])


class MemoryWriteRequest(BaseModel):
    business_id: str
    agent_name: str
    namespace: str
    key: str
    content: str
    tags: list[str] = Field(default_factory=list)
    confidence: float = 0.5
    source: str = "manual"
    outcome: str = ""


@router.get("")
def list_memory(
    business_id: str | None = None,
    agent_name: str | None = None,
    namespace: str | None = None,
    limit: int = 50,
    db: Client = Depends(get_supabase),
):
    """List memory entries with optional filters."""
    q = db.table("memory").select("*").order("updated_at", desc=True).limit(limit)
    if business_id:
        q = q.eq("business_id", business_id)
    if agent_name:
        q = q.eq("agent_name", agent_name)
    if namespace:
        q = q.eq("namespace", namespace)
    return ok_list(q.execute().data)


@router.get("/namespaces")
def list_namespaces():
    """List the standard memory namespaces."""
    from abf_ai.memory import (
        NAMESPACE_DECISIONS,
        NAMESPACE_CAMPAIGN_PATTERNS,
        NAMESPACE_COPY_ANGLES,
        NAMESPACE_APPROVAL_REASONS,
        NAMESPACE_MARKET_INTEL,
        NAMESPACE_BRAND_VOICE,
    )
    return ok_list([
        {"namespace": NAMESPACE_DECISIONS, "description": "Successful and failed decision outcomes"},
        {"namespace": NAMESPACE_CAMPAIGN_PATTERNS, "description": "Winning and losing campaign patterns"},
        {"namespace": NAMESPACE_COPY_ANGLES, "description": "High-performing creative angles"},
        {"namespace": NAMESPACE_APPROVAL_REASONS, "description": "Common approval rejection reasons"},
        {"namespace": NAMESPACE_MARKET_INTEL, "description": "Competitor and market data"},
        {"namespace": NAMESPACE_BRAND_VOICE, "description": "Tone, style, vocabulary per business"},
    ])


@router.post("", status_code=201)
def write_memory(
    body: MemoryWriteRequest,
    db: Client = Depends(get_supabase),
):
    """Manually write a memory entry."""
    from abf_ai.memory import save, MemoryEntry

    entry = MemoryEntry(
        content=body.content,
        tags=body.tags,
        confidence=body.confidence,
        source=body.source,
        outcome=body.outcome,
        created_by="api",
    )

    row_id = save(
        db,
        business_id=body.business_id,
        agent_name=body.agent_name,
        namespace=body.namespace,
        key=body.key,
        entry=entry,
    )

    if row_id is None:
        return ok({"saved": False, "error": "Failed to save memory entry"})

    return ok({"saved": True, "id": row_id})


@router.get("/{business_id}/summary")
def memory_summary(
    business_id: str,
    db: Client = Depends(get_supabase),
):
    """Get a summary of all memory entries for a business."""
    res = (
        db.table("memory")
        .select("agent_name, namespace")
        .eq("business_id", business_id)
        .execute()
    )
    rows = res.data or []

    # Count by namespace
    by_namespace: dict[str, int] = {}
    by_agent: dict[str, int] = {}
    for row in rows:
        ns = row.get("namespace", "default")
        agent = row.get("agent_name", "unknown")
        by_namespace[ns] = by_namespace.get(ns, 0) + 1
        by_agent[agent] = by_agent.get(agent, 0) + 1

    return ok({
        "business_id": business_id,
        "total_entries": len(rows),
        "by_namespace": by_namespace,
        "by_agent": by_agent,
    })
