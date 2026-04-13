import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from supabase import Client

from abf_api.config import settings
from abf_api.deps.supabase import get_supabase

logger = logging.getLogger("abf_api.health")

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": "0.2.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.environment,
    }


@router.get("/health/ready")
def readiness_check(db: Client = Depends(get_supabase)):
    """Deep health check — verifies Supabase connectivity."""
    checks: dict = {}

    try:
        db.table("businesses").select("id").limit(1).execute()
        checks["database"] = "ok"
    except Exception as exc:
        logger.warning("Database health check failed: %s", exc)
        checks["database"] = "error"

    all_ok = all(v == "ok" for v in checks.values())

    return {
        "status": "ok" if all_ok else "degraded",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
