"""Integration credential management service.

Security model:
  - System providers (OpenAI, Anthropic): credentials from env vars only.
    The DB row tracks status but credential_key is null.
  - User providers (Stripe, Meta, etc.): credentials stored in the DB.
    The frontend only sees masked_key (e.g. "sk-...a1b2").

The frontend NEVER receives raw credential values.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from supabase import Client

from abf_api.config import settings

logger = logging.getLogger("abf_api.credentials")

# Providers whose credentials come from env vars, not user input
ENV_PROVIDERS = {"openai", "anthropic"}

# Map provider → env var name for system providers
ENV_KEY_MAP = {
    "openai": "openai_api_key",
    "anthropic": "anthropic_api_key",
}

# Provider metadata (display names, descriptions, categories)
PROVIDER_CATALOG = [
    {
        "provider": "openai",
        "display_name": "OpenAI",
        "category": "ai",
        "description": "GPT models for decisioning, prioritization, and analysis.",
        "source": "env",
    },
    {
        "provider": "anthropic",
        "display_name": "Anthropic",
        "category": "ai",
        "description": "Claude models for content generation and creative tasks.",
        "source": "env",
    },
    {
        "provider": "stripe",
        "display_name": "Stripe",
        "category": "payments",
        "description": "Payment processing, refunds, and revenue tracking.",
        "source": "user",
    },
    {
        "provider": "meta_ads",
        "display_name": "Meta Ads",
        "category": "advertising",
        "description": "Facebook and Instagram campaign management.",
        "source": "user",
    },
    {
        "provider": "google_ads",
        "display_name": "Google Ads",
        "category": "advertising",
        "description": "Google search and display campaign management.",
        "source": "user",
    },
    {
        "provider": "shopify",
        "display_name": "Shopify",
        "category": "ecommerce",
        "description": "E-commerce storefront and product management.",
        "source": "user",
    },
    {
        "provider": "email",
        "display_name": "Email Provider",
        "category": "messaging",
        "description": "Transactional and marketing email delivery.",
        "source": "user",
    },
    {
        "provider": "sms",
        "display_name": "SMS Provider",
        "category": "messaging",
        "description": "SMS notifications and marketing messages.",
        "source": "user",
    },
]


def mask_key(key: str | None) -> str:
    """Mask a credential key for safe frontend display."""
    if not key:
        return ""
    if len(key) <= 8:
        return "***"
    prefix = key[:3]
    suffix = key[-4:]
    return f"{prefix}...{suffix}"


def get_env_credential(provider: str) -> str:
    """Get a system provider's credential from environment variables."""
    attr = ENV_KEY_MAP.get(provider, "")
    return getattr(settings, attr, "") if attr else ""


def get_all_connections(db: Client) -> list[dict[str, Any]]:
    """Get all integration connections with safe (masked) output.

    Merges the provider catalog with DB state. Env-sourced providers
    show status based on whether the env var is set.
    """
    # Load existing DB rows
    res = db.table("integration_connections").select("*").execute()
    db_rows = {row["provider"]: row for row in (res.data or [])}

    connections = []
    for provider_info in PROVIDER_CATALOG:
        provider = provider_info["provider"]
        db_row = db_rows.get(provider)

        if provider in ENV_PROVIDERS:
            # System provider — check env var
            has_key = bool(get_env_credential(provider))
            connections.append({
                "provider": provider,
                "display_name": provider_info["display_name"],
                "category": provider_info["category"],
                "description": provider_info["description"],
                "source": "env",
                "enabled": has_key,
                "status": "connected" if has_key else "not_configured",
                "has_credential": has_key,
                "masked_key": mask_key(get_env_credential(provider)) if has_key else "",
                "config": db_row.get("config", {}) if db_row else {},
                "last_tested_at": db_row.get("last_tested_at") if db_row else None,
                "last_error": db_row.get("last_error") if db_row else None,
            })
        else:
            # User provider — check DB
            if db_row:
                connections.append({
                    "provider": provider,
                    "display_name": provider_info["display_name"],
                    "category": provider_info["category"],
                    "description": provider_info["description"],
                    "source": "user",
                    "enabled": db_row.get("enabled", False),
                    "status": db_row.get("status", "not_configured"),
                    "has_credential": bool(db_row.get("credential_key")),
                    "masked_key": db_row.get("masked_key", ""),
                    "config": db_row.get("config", {}),
                    "last_tested_at": db_row.get("last_tested_at"),
                    "last_error": db_row.get("last_error"),
                })
            else:
                connections.append({
                    "provider": provider,
                    "display_name": provider_info["display_name"],
                    "category": provider_info["category"],
                    "description": provider_info["description"],
                    "source": "user",
                    "enabled": False,
                    "status": "not_configured",
                    "has_credential": False,
                    "masked_key": "",
                    "config": {},
                    "last_tested_at": None,
                    "last_error": None,
                })

    return connections


def upsert_connection(
    db: Client,
    *,
    provider: str,
    credential_key: str | None = None,
    config: dict[str, Any] | None = None,
    enabled: bool | None = None,
) -> dict[str, Any]:
    """Create or update an integration connection.

    For user providers: stores the credential_key and its masked version.
    For env providers: only updates config and enabled state.
    """
    provider_info = next((p for p in PROVIDER_CATALOG if p["provider"] == provider), None)
    if not provider_info:
        raise ValueError(f"Unknown provider: {provider}")

    data: dict[str, Any] = {
        "provider": provider,
        "display_name": provider_info["display_name"],
        "source": provider_info["source"],
    }

    if provider in ENV_PROVIDERS:
        # Don't store credentials for env providers
        has_key = bool(get_env_credential(provider))
        data["enabled"] = has_key
        data["status"] = "connected" if has_key else "not_configured"
        data["masked_key"] = mask_key(get_env_credential(provider)) if has_key else ""
    else:
        if credential_key is not None:
            data["credential_key"] = credential_key
            data["masked_key"] = mask_key(credential_key)
            data["status"] = "not_configured"  # Needs test to become "connected"

        if enabled is not None:
            data["enabled"] = enabled

    if config is not None:
        data["config"] = config

    res = db.table("integration_connections").upsert(
        data, on_conflict="provider"
    ).execute()

    row = res.data[0] if res.data else data

    # Never return the raw credential
    safe = {**row}
    safe.pop("credential_key", None)

    logger.info("Integration connection updated: %s", provider)
    return safe


def mark_test_result(
    db: Client,
    provider: str,
    success: bool,
    error: str | None = None,
) -> None:
    """Update the connection status after a test."""
    now = datetime.now(timezone.utc).isoformat()
    db.table("integration_connections").upsert({
        "provider": provider,
        "display_name": next(
            (p["display_name"] for p in PROVIDER_CATALOG if p["provider"] == provider),
            provider,
        ),
        "status": "connected" if success else "error",
        "last_tested_at": now,
        "last_error": error,
        "source": "env" if provider in ENV_PROVIDERS else "user",
    }, on_conflict="provider").execute()


def get_credential_for_dispatch(db: Client, provider: str) -> str:
    """Get the raw credential for a provider. Backend-only — never expose to frontend.

    Checks env vars first (for system providers), then DB.
    """
    if provider in ENV_PROVIDERS:
        return get_env_credential(provider)

    res = (
        db.table("integration_connections")
        .select("credential_key, enabled")
        .eq("provider", provider)
        .maybe_single()
        .execute()
    )

    if not res.data:
        return ""
    if not res.data.get("enabled"):
        return ""
    return res.data.get("credential_key", "") or ""
