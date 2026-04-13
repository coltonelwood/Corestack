"""Audit log service.

Provides a simple function to record audit events.
All mutations in routers should call this after successful writes.
"""

import logging
from typing import Any

from supabase import Client

logger = logging.getLogger("abf_api.audit")


def log_event(
    db: Client,
    *,
    actor: str,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    business_id: str | None = None,
    diff: dict[str, Any] | None = None,
) -> None:
    """Insert an audit log entry. Errors are logged but never raised."""
    try:
        db.table("audit_logs").insert({
            "actor": actor,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "business_id": business_id,
            "diff": diff,
        }).execute()
    except Exception:
        logger.exception(
            "Failed to write audit log: %s %s %s",
            action, entity_type, entity_id,
        )
