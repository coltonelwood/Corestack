"""Agent memory layer — structured learning storage and retrieval.

Stores reusable learnings in the existing `memory` table using typed
namespaces. Each entry is keyed by (business_id, agent_name, namespace, key)
with a JSONB value that can hold any structured data.

Namespaces:
  decisions        — successful/failed decision outcomes
  campaign_patterns — winning/losing campaign patterns
  copy_angles      — high-performing creative angles
  approval_reasons — common approval rejection reasons
  market_intel     — competitor and market data
  brand_voice      — tone, style, vocabulary per business

The value field is structured for future embedding/semantic search:
  {
    "content": "...",           ← the learning (searchable text)
    "tags": ["..."],            ← for filtering
    "confidence": 0.85,         ← how confident we are in this learning
    "source": "...",            ← where this came from
    "outcome": "success|failure",
    "context": {...},           ← raw context data
    "created_by": "...",        ← which agent/workflow wrote this
  }
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger("abf_ai.memory")


# ── Namespaces ───────────────────────────────────────────────

NAMESPACE_DECISIONS = "decisions"
NAMESPACE_CAMPAIGN_PATTERNS = "campaign_patterns"
NAMESPACE_COPY_ANGLES = "copy_angles"
NAMESPACE_APPROVAL_REASONS = "approval_reasons"
NAMESPACE_MARKET_INTEL = "market_intel"
NAMESPACE_BRAND_VOICE = "brand_voice"


# ── Memory entry model ───────────────────────────────────────

class MemoryEntry(BaseModel):
    """Structured value stored in the memory table."""

    content: str = ""
    tags: list[str] = Field(default_factory=list)
    confidence: float = 0
    source: str = ""
    outcome: str = ""  # "success" | "failure" | ""
    context: dict[str, Any] = Field(default_factory=dict)
    created_by: str = ""


# ── Core functions ───────────────────────────────────────────

def save(
    db: Any,
    *,
    business_id: str,
    agent_name: str,
    namespace: str,
    key: str,
    entry: MemoryEntry,
) -> str | None:
    """Save a memory entry. Upserts on the composite key.

    Returns the memory row ID on success, None on failure.
    """
    try:
        res = db.table("memory").upsert(
            {
                "business_id": business_id,
                "agent_name": agent_name,
                "namespace": namespace,
                "key": key,
                "value": entry.model_dump(),
            },
            on_conflict="business_id,agent_name,namespace,key",
        ).execute()

        row_id = res.data[0]["id"] if res.data else None
        logger.info(
            "Memory saved: %s/%s/%s (business=%s)",
            agent_name, namespace, key, business_id[:8],
        )
        return row_id

    except Exception:
        logger.exception("Failed to save memory: %s/%s/%s", agent_name, namespace, key)
        return None


def recall(
    db: Any,
    *,
    business_id: str,
    agent_name: str,
    namespace: str,
    key: str,
) -> MemoryEntry | None:
    """Recall a single memory entry by exact key. Returns None if not found."""
    try:
        res = (
            db.table("memory")
            .select("value")
            .eq("business_id", business_id)
            .eq("agent_name", agent_name)
            .eq("namespace", namespace)
            .eq("key", key)
            .maybe_single()
            .execute()
        )
        if res.data and res.data.get("value"):
            return MemoryEntry.model_validate(res.data["value"])
        return None
    except Exception:
        logger.exception("Failed to recall memory: %s/%s/%s", agent_name, namespace, key)
        return None


def recall_namespace(
    db: Any,
    *,
    business_id: str,
    agent_name: str,
    namespace: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Recall all entries in a namespace for a business. Returns raw rows."""
    try:
        res = (
            db.table("memory")
            .select("*")
            .eq("business_id", business_id)
            .eq("agent_name", agent_name)
            .eq("namespace", namespace)
            .order("updated_at", desc=True)
            .limit(limit)
            .execute()
        )
        return res.data or []
    except Exception:
        logger.exception("Failed to recall namespace: %s/%s", agent_name, namespace)
        return []


def recall_by_tags(
    db: Any,
    *,
    business_id: str,
    namespace: str,
    tags: list[str],
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Recall entries that contain any of the given tags.

    Uses JSONB containment to filter by tags within the value field.
    """
    try:
        res = (
            db.table("memory")
            .select("*")
            .eq("business_id", business_id)
            .eq("namespace", namespace)
            .order("updated_at", desc=True)
            .limit(limit)
            .execute()
        )
        # Filter client-side for tag matches (simple approach — upgrade to
        # Postgres JSONB operators when query volume warrants it)
        rows = res.data or []
        matched = []
        tag_set = set(tags)
        for row in rows:
            value = row.get("value", {})
            row_tags = set(value.get("tags", []))
            if row_tags & tag_set:
                matched.append(row)
        return matched[:limit]
    except Exception:
        logger.exception("Failed to recall by tags: %s/%s", namespace, tags)
        return []


def build_context_string(entries: list[dict[str, Any]], max_entries: int = 5) -> str:
    """Convert memory entries into a text block for injection into AI prompts.

    This is the bridge between stored memory and the AI router — call this
    before sending a prompt, and include the result in the AI payload.
    """
    if not entries:
        return ""

    lines = ["Relevant learnings from past experience:"]
    for entry in entries[:max_entries]:
        value = entry.get("value", {})
        content = value.get("content", "")
        outcome = value.get("outcome", "")
        confidence = value.get("confidence", 0)
        tags = value.get("tags", [])

        if not content:
            continue

        prefix = ""
        if outcome == "success":
            prefix = "[SUCCESS] "
        elif outcome == "failure":
            prefix = "[FAILURE] "

        tag_str = f" (tags: {', '.join(tags)})" if tags else ""
        conf_str = f" [confidence: {confidence:.0%}]" if confidence else ""

        lines.append(f"  - {prefix}{content}{tag_str}{conf_str}")

    return "\n".join(lines) if len(lines) > 1 else ""


# ── High-level helpers for common patterns ───────────────────

def save_decision_outcome(
    db: Any,
    *,
    business_id: str,
    decision_type: str,
    decision: str,
    outcome: str,
    confidence: float,
    reason: str,
    context: dict[str, Any] | None = None,
    agent_name: str = "decision",
) -> str | None:
    """Save a decision outcome to the decisions namespace."""
    now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    key = f"{decision_type}:{decision}:{now}"

    return save(
        db,
        business_id=business_id,
        agent_name=agent_name,
        namespace=NAMESPACE_DECISIONS,
        key=key,
        entry=MemoryEntry(
            content=f"{decision_type} decision '{decision}': {reason}",
            tags=[decision_type, decision, outcome],
            confidence=confidence,
            source=f"decision_agent:{decision_type}",
            outcome=outcome,
            context=context or {},
            created_by=agent_name,
        ),
    )


def save_campaign_pattern(
    db: Any,
    *,
    business_id: str,
    campaign_name: str,
    channel: str,
    decision: str,
    roas: float,
    cpa_cents: int,
    confidence: float,
    reason: str,
) -> str | None:
    """Save a winning or losing campaign pattern."""
    outcome = "success" if decision in ("scale", "scale_up", "hold", "maintain") else "failure"
    now = datetime.now(timezone.utc).strftime("%Y%m%d")
    key = f"{channel}:{campaign_name[:40]}:{now}"

    return save(
        db,
        business_id=business_id,
        agent_name="campaign_optimization",
        namespace=NAMESPACE_CAMPAIGN_PATTERNS,
        key=key,
        entry=MemoryEntry(
            content=f"Campaign '{campaign_name}' ({channel}): {decision} — {reason}",
            tags=[channel, decision, f"roas_{int(roas)}x", outcome],
            confidence=confidence,
            source="campaign_optimization_workflow",
            outcome=outcome,
            context={
                "campaign_name": campaign_name,
                "channel": channel,
                "roas": roas,
                "cpa_cents": cpa_cents,
            },
            created_by="campaign_optimization",
        ),
    )


def save_approval_rejection(
    db: Any,
    *,
    business_id: str,
    approval_type: str,
    title: str,
    reason: str,
) -> str | None:
    """Save an approval rejection pattern for future reference."""
    now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    key = f"{approval_type}:rejected:{now}"

    return save(
        db,
        business_id=business_id,
        agent_name="approval_system",
        namespace=NAMESPACE_APPROVAL_REASONS,
        key=key,
        entry=MemoryEntry(
            content=f"Rejected {approval_type}: {title} — {reason}",
            tags=[approval_type, "rejected"],
            confidence=1.0,
            source="approval_system",
            outcome="failure",
            context={"title": title, "approval_type": approval_type},
            created_by="approval_system",
        ),
    )


def save_copy_angle(
    db: Any,
    *,
    business_id: str,
    content_type: str,
    angle: str,
    performance_note: str = "",
    tags: list[str] | None = None,
) -> str | None:
    """Save a successful copy angle for reuse."""
    now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    key = f"{content_type}:{now}"

    return save(
        db,
        business_id=business_id,
        agent_name="content_writer",
        namespace=NAMESPACE_COPY_ANGLES,
        key=key,
        entry=MemoryEntry(
            content=angle,
            tags=[content_type, *(tags or [])],
            confidence=0.7,
            source="content_generation",
            outcome="success",
            context={"performance_note": performance_note},
            created_by="content_writer",
        ),
    )


def recall_relevant_decisions(
    db: Any,
    *,
    business_id: str,
    decision_type: str,
    limit: int = 5,
) -> str:
    """Recall past decisions of a given type and format for AI prompt injection."""
    entries = recall_namespace(
        db,
        business_id=business_id,
        agent_name="decision",
        namespace=NAMESPACE_DECISIONS,
        limit=limit,
    )

    # Filter to matching decision type
    filtered = [
        e for e in entries
        if decision_type in (e.get("value", {}).get("tags", []))
    ]

    return build_context_string(filtered or entries[:3])


def recall_campaign_patterns(
    db: Any,
    *,
    business_id: str,
    channel: str | None = None,
    limit: int = 5,
) -> str:
    """Recall campaign patterns for a channel and format for AI prompt injection."""
    entries = recall_namespace(
        db,
        business_id=business_id,
        agent_name="campaign_optimization",
        namespace=NAMESPACE_CAMPAIGN_PATTERNS,
        limit=limit * 2,
    )

    if channel:
        filtered = [
            e for e in entries
            if channel in (e.get("value", {}).get("tags", []))
        ]
        entries = filtered or entries

    return build_context_string(entries[:limit])
