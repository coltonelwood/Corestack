-- ABF Initial Schema
-- Migration 001: Core tables for Autonomous Business Factory
--
-- Run against Supabase Postgres via the SQL Editor or CLI:
--   supabase db push
--
-- All tables use UUID primary keys, timestamptz for timestamps,
-- and follow a consistent pattern: id, domain columns, created_at, updated_at.

-- ============================================================
-- Extensions
-- ============================================================

create extension if not exists "uuid-ossp";

-- ============================================================
-- 1. businesses
-- ============================================================

create table businesses (
  id          uuid primary key default uuid_generate_v4(),
  name        text not null,
  domain      text,
  description text,
  status      text not null default 'setup'
                check (status in ('active', 'paused', 'setup', 'archived')),
  metadata    jsonb not null default '{}',
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

create index idx_businesses_status on businesses (status);

-- ============================================================
-- 2. products
-- ============================================================

create table products (
  id           uuid primary key default uuid_generate_v4(),
  business_id  uuid not null references businesses (id) on delete cascade,
  name         text not null,
  description  text,
  category     text,
  price_cents  integer not null default 0,
  cost_cents   integer not null default 0,
  status       text not null default 'draft'
                 check (status in ('active', 'draft', 'archived')),
  inventory    integer not null default 0,
  sales_count  integer not null default 0,
  metadata     jsonb not null default '{}',
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

create index idx_products_business_id on products (business_id);
create index idx_products_status on products (status);

-- ============================================================
-- 3. campaigns
-- ============================================================

create table campaigns (
  id            uuid primary key default uuid_generate_v4(),
  business_id   uuid not null references businesses (id) on delete cascade,
  product_id    uuid references products (id) on delete set null,
  name          text not null,
  channel       text not null
                  check (channel in ('google', 'meta', 'tiktok', 'email', 'linkedin', 'other')),
  status        text not null default 'draft'
                  check (status in ('active', 'paused', 'completed', 'draft')),
  budget_cents  integer not null default 0,
  spent_cents   integer not null default 0,
  impressions   bigint not null default 0,
  clicks        integer not null default 0,
  conversions   integer not null default 0,
  start_date    date,
  end_date      date,
  metadata      jsonb not null default '{}',
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create index idx_campaigns_business_id on campaigns (business_id);
create index idx_campaigns_product_id on campaigns (product_id);
create index idx_campaigns_status on campaigns (status);
create index idx_campaigns_channel on campaigns (channel);

-- ============================================================
-- 4. tasks
-- ============================================================

create table tasks (
  id             uuid primary key default uuid_generate_v4(),
  business_id    uuid not null references businesses (id) on delete cascade,
  title          text not null,
  description    text,
  status         text not null default 'pending'
                   check (status in ('pending', 'in_progress', 'completed', 'failed', 'cancelled')),
  priority       text not null default 'medium'
                   check (priority in ('low', 'medium', 'high', 'critical')),
  assigned_agent text,
  payload        jsonb not null default '{}',
  result         jsonb,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now(),
  completed_at   timestamptz
);

create index idx_tasks_business_id on tasks (business_id);
create index idx_tasks_status on tasks (status);
create index idx_tasks_priority on tasks (priority);
create index idx_tasks_assigned_agent on tasks (assigned_agent);

-- ============================================================
-- 5. agent_runs
-- ============================================================

create table agent_runs (
  id               uuid primary key default uuid_generate_v4(),
  task_id          uuid references tasks (id) on delete set null,
  business_id      uuid not null references businesses (id) on delete cascade,
  agent_name       text not null,
  agent_type       text not null
                     check (agent_type in ('research', 'content', 'ads', 'analytics', 'outreach', 'operations')),
  status           text not null default 'queued'
                     check (status in ('queued', 'running', 'completed', 'failed')),
  duration_ms      integer,
  tokens_used      integer not null default 0,
  cost_cents       integer not null default 0,
  input_payload    jsonb not null default '{}',
  output_payload   jsonb,
  error_message    text,
  started_at       timestamptz not null default now(),
  completed_at     timestamptz
);

create index idx_agent_runs_business_id on agent_runs (business_id);
create index idx_agent_runs_task_id on agent_runs (task_id);
create index idx_agent_runs_status on agent_runs (status);
create index idx_agent_runs_agent_type on agent_runs (agent_type);
create index idx_agent_runs_started_at on agent_runs (started_at desc);

-- ============================================================
-- 6. approvals
-- ============================================================

create table approvals (
  id             uuid primary key default uuid_generate_v4(),
  business_id    uuid not null references businesses (id) on delete cascade,
  type           text not null
                   check (type in ('campaign_launch', 'budget_increase', 'content_publish',
                                   'product_listing', 'price_change', 'other')),
  title          text not null,
  description    text,
  status         text not null default 'pending'
                   check (status in ('pending', 'approved', 'rejected')),
  requested_by   text not null,
  reviewed_by    text,
  amount_cents   integer,
  payload        jsonb not null default '{}',
  created_at     timestamptz not null default now(),
  reviewed_at    timestamptz
);

create index idx_approvals_business_id on approvals (business_id);
create index idx_approvals_status on approvals (status);
create index idx_approvals_type on approvals (type);

-- ============================================================
-- 7. audit_logs  (append-only)
-- ============================================================

create table audit_logs (
  id           uuid primary key default uuid_generate_v4(),
  business_id  uuid references businesses (id) on delete set null,
  actor        text not null,
  action       text not null,
  entity_type  text not null,
  entity_id    uuid,
  diff         jsonb,
  metadata     jsonb not null default '{}',
  created_at   timestamptz not null default now()
);

-- No updated_at — audit logs are immutable.
create index idx_audit_logs_business_id on audit_logs (business_id);
create index idx_audit_logs_entity on audit_logs (entity_type, entity_id);
create index idx_audit_logs_created_at on audit_logs (created_at desc);
create index idx_audit_logs_actor on audit_logs (actor);

-- Protect against updates and deletes on audit_logs.
create or replace function prevent_audit_mutation()
returns trigger as $$
begin
  raise exception 'audit_logs is append-only: % not allowed', tg_op;
end;
$$ language plpgsql;

create trigger trg_audit_logs_no_update
  before update on audit_logs
  for each row execute function prevent_audit_mutation();

create trigger trg_audit_logs_no_delete
  before delete on audit_logs
  for each row execute function prevent_audit_mutation();

-- ============================================================
-- 8. memory  (agent long-term memory / knowledge store)
-- ============================================================

create table memory (
  id           uuid primary key default uuid_generate_v4(),
  business_id  uuid references businesses (id) on delete cascade,
  agent_name   text not null,
  namespace    text not null default 'default',
  key          text not null,
  value        jsonb not null,
  expires_at   timestamptz,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

create unique index idx_memory_lookup
  on memory (business_id, agent_name, namespace, key);
create index idx_memory_agent on memory (agent_name, namespace);
create index idx_memory_expires on memory (expires_at)
  where expires_at is not null;

-- ============================================================
-- Shared: updated_at trigger
-- ============================================================

create or replace function update_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

-- Apply to all mutable tables (not audit_logs).
create trigger trg_businesses_updated_at
  before update on businesses
  for each row execute function update_updated_at();

create trigger trg_products_updated_at
  before update on products
  for each row execute function update_updated_at();

create trigger trg_campaigns_updated_at
  before update on campaigns
  for each row execute function update_updated_at();

create trigger trg_tasks_updated_at
  before update on tasks
  for each row execute function update_updated_at();

create trigger trg_agent_runs_updated_at
  before update on agent_runs
  for each row execute function update_updated_at();

create trigger trg_memory_updated_at
  before update on memory
  for each row execute function update_updated_at();
