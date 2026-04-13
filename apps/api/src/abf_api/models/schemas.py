"""Pydantic schemas for all ABF domain models.

Naming convention:
  - FooRead   — returned from GET endpoints
  - FooCreate — accepted by POST endpoints
  - FooUpdate — accepted by PATCH endpoints
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# ── Businesses ───────────────────────────────────────────────

class BusinessCreate(BaseModel):
    name: str
    domain: str | None = None
    description: str | None = None

class BusinessUpdate(BaseModel):
    name: str | None = None
    domain: str | None = None
    description: str | None = None
    status: Literal["active", "paused", "setup", "archived"] | None = None

class BusinessRead(BaseModel):
    id: str
    name: str
    domain: str | None
    description: str | None
    status: str
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


# ── Products ─────────────────────────────────────────────────

class ProductCreate(BaseModel):
    business_id: str
    name: str
    description: str | None = None
    category: str | None = None
    price_cents: int = 0
    cost_cents: int = 0
    inventory: int = 0

class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    price_cents: int | None = None
    cost_cents: int | None = None
    status: Literal["active", "draft", "archived"] | None = None
    inventory: int | None = None

class ProductRead(BaseModel):
    id: str
    business_id: str
    name: str
    description: str | None
    category: str | None
    price_cents: int
    cost_cents: int
    status: str
    inventory: int
    sales_count: int
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


# ── Campaigns ────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    business_id: str
    name: str
    channel: Literal["google", "meta", "tiktok", "email", "linkedin", "other"]
    budget_cents: int = 0
    product_id: str | None = None
    start_date: str | None = None
    end_date: str | None = None

class CampaignUpdate(BaseModel):
    name: str | None = None
    channel: Literal["google", "meta", "tiktok", "email", "linkedin", "other"] | None = None
    status: Literal["active", "paused", "completed", "draft"] | None = None
    budget_cents: int | None = None
    spent_cents: int | None = None
    impressions: int | None = None
    clicks: int | None = None
    conversions: int | None = None
    start_date: str | None = None
    end_date: str | None = None

class CampaignRead(BaseModel):
    id: str
    business_id: str
    product_id: str | None
    name: str
    channel: str
    status: str
    budget_cents: int
    spent_cents: int
    impressions: int
    clicks: int
    conversions: int
    start_date: str | None
    end_date: str | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


# ── Tasks ────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    business_id: str
    title: str
    description: str | None = None
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    assigned_agent: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: Literal["pending", "in_progress", "completed", "failed", "cancelled"] | None = None
    priority: Literal["low", "medium", "high", "critical"] | None = None
    assigned_agent: str | None = None
    payload: dict[str, Any] | None = None
    result: dict[str, Any] | None = None

class TaskRead(BaseModel):
    id: str
    business_id: str
    title: str
    description: str | None
    status: str
    priority: str
    assigned_agent: str | None
    payload: dict[str, Any]
    result: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


# ── Agent Runs ───────────────────────────────────────────────

class AgentRunCreate(BaseModel):
    business_id: str
    agent_name: str
    agent_type: Literal["research", "content", "ads", "analytics", "outreach", "operations"]
    task_id: str | None = None
    input_payload: dict[str, Any] = Field(default_factory=dict)

class AgentRunUpdate(BaseModel):
    status: Literal["queued", "running", "completed", "failed"] | None = None
    duration_ms: int | None = None
    tokens_used: int | None = None
    cost_cents: int | None = None
    output_payload: dict[str, Any] | None = None
    error_message: str | None = None

class AgentRunRead(BaseModel):
    id: str
    task_id: str | None
    business_id: str
    agent_name: str
    agent_type: str
    status: str
    duration_ms: int | None
    tokens_used: int
    cost_cents: int
    input_payload: dict[str, Any]
    output_payload: dict[str, Any] | None
    error_message: str | None
    started_at: datetime
    completed_at: datetime | None


# ── Approvals ────────────────────────────────────────────────

class ApprovalCreate(BaseModel):
    business_id: str
    type: Literal["campaign_launch", "budget_increase", "content_publish", "product_listing", "price_change", "other"]
    title: str
    description: str | None = None
    requested_by: str
    amount_cents: int | None = None
    payload: dict[str, Any] = Field(default_factory=dict)

class ApprovalDecision(BaseModel):
    reviewed_by: str

class ApprovalRead(BaseModel):
    id: str
    business_id: str
    type: str
    title: str
    description: str | None
    status: str
    requested_by: str
    reviewed_by: str | None
    amount_cents: int | None
    payload: dict[str, Any]
    created_at: datetime
    reviewed_at: datetime | None


# ── Audit Logs ───────────────────────────────────────────────

class AuditLogCreate(BaseModel):
    business_id: str | None = None
    actor: str
    action: str
    entity_type: str
    entity_id: str | None = None
    diff: dict[str, Any] | None = None

class AuditLogRead(BaseModel):
    id: str
    business_id: str | None
    actor: str
    action: str
    entity_type: str
    entity_id: str | None
    diff: dict[str, Any] | None
    metadata: dict[str, Any]
    created_at: datetime
