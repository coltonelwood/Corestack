"""Role-based access control dependencies for FastAPI.

Usage in routers:
    from abf_api.deps.rbac import require_permission

    @router.post("")
    def create_business(
        body: BusinessCreate,
        _user: Any = Depends(require_permission("businesses:write")),
        db: Client = Depends(get_supabase),
    ):
        ...

The dependency extracts the user from the JWT, looks up their role
in the user_roles table, and checks against the permission map
from @abf/core.
"""

import logging
from typing import Any

from fastapi import Depends, HTTPException, Request
from supabase import Client

from abf_api.deps.supabase import get_supabase

logger = logging.getLogger("abf_api.rbac")

# Permission map mirrored from packages/core/src/rbac.ts.
# Kept in sync manually — the TypeScript module is the source of truth.
ROLE_PERMISSIONS: dict[str, set[str]] = {
    "owner": {
        "businesses:read", "businesses:write",
        "products:read", "products:write",
        "campaigns:read", "campaigns:write",
        "tasks:read", "tasks:write",
        "agent_runs:read",
        "workflows:read", "workflows:execute",
        "approvals:read", "approvals:decide",
        "ai:read", "ai:execute",
        "integrations:read", "integrations:manage", "integrations:dispatch",
        "settings:read", "settings:write",
        "audit_logs:read",
        "memory:read", "memory:write",
    },
    "admin": {
        "businesses:read", "businesses:write",
        "products:read", "products:write",
        "campaigns:read", "campaigns:write",
        "tasks:read", "tasks:write",
        "agent_runs:read",
        "workflows:read", "workflows:execute",
        "approvals:read", "approvals:decide",
        "ai:read", "ai:execute",
        "integrations:read", "integrations:manage", "integrations:dispatch",
        "settings:read", "settings:write",
        "audit_logs:read",
        "memory:read", "memory:write",
    },
    "operator": {
        "businesses:read",
        "products:read", "products:write",
        "campaigns:read", "campaigns:write",
        "tasks:read", "tasks:write",
        "agent_runs:read",
        "workflows:read", "workflows:execute",
        "approvals:read",
        "ai:read", "ai:execute",
        "integrations:read", "integrations:dispatch",
        "settings:read",
        "audit_logs:read",
        "memory:read",
    },
    "analyst": {
        "businesses:read",
        "products:read",
        "campaigns:read",
        "tasks:read",
        "agent_runs:read",
        "workflows:read",
        "approvals:read",
        "ai:read",
        "integrations:read",
        "audit_logs:read",
        "memory:read",
    },
    "viewer": {
        "businesses:read",
        "products:read",
        "campaigns:read",
        "tasks:read",
        "agent_runs:read",
        "workflows:read",
    },
}

DEFAULT_ROLE = "viewer"


async def get_user_role(request: Request, db: Client = Depends(get_supabase)) -> dict[str, Any]:
    """Extract user from JWT and resolve their role from user_roles table.

    Returns {"user_id": str, "role": str} or raises 401.
    """
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = auth_header.removeprefix("Bearer ")

    try:
        res = db.auth.get_user(token)
        if res.user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = res.user.id

    # Look up role
    role_res = (
        db.table("user_roles")
        .select("role")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )

    role = DEFAULT_ROLE
    if role_res.data:
        role = role_res.data.get("role", DEFAULT_ROLE)

    return {"user_id": user_id, "role": role, "email": res.user.email}


def require_permission(permission: str):
    """FastAPI dependency factory: require a specific permission.

    Usage: Depends(require_permission("approvals:decide"))
    """
    async def check(
        user_ctx: dict[str, Any] = Depends(get_user_role),
    ) -> dict[str, Any]:
        role = user_ctx["role"]
        permissions = ROLE_PERMISSIONS.get(role, set())

        if permission not in permissions:
            logger.warning(
                "Permission denied: user=%s role=%s needs=%s",
                user_ctx.get("user_id", "?"), role, permission,
            )
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {permission}",
            )

        return user_ctx

    return check


def require_any_permission(*permissions: str):
    """FastAPI dependency: require ANY of the listed permissions."""
    async def check(
        user_ctx: dict[str, Any] = Depends(get_user_role),
    ) -> dict[str, Any]:
        role = user_ctx["role"]
        role_perms = ROLE_PERMISSIONS.get(role, set())

        if not any(p in role_perms for p in permissions):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required one of: {', '.join(permissions)}",
            )

        return user_ctx

    return check
