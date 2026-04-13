-- ABF Workflow Persistence
-- Migration 003: Tables for tracking workflow runs with pause/resume support.

-- ============================================================
-- workflow_runs — top-level workflow execution records
-- ============================================================

create table workflow_runs (
  id              uuid primary key default uuid_generate_v4(),
  business_id     uuid not null references businesses (id) on delete cascade,
  workflow_type   text not null,
  name            text not null,
  status          text not null default 'running'
                    check (status in ('running', 'paused', 'completed', 'failed', 'cancelled')),
  input_payload   jsonb not null default '{}',
  output_payload  jsonb,
  current_step    text,
  total_steps     integer not null default 0,
  completed_steps integer not null default 0,
  failed_steps    integer not null default 0,
  total_tokens    integer not null default 0,
  total_cost_cents integer not null default 0,
  error_message   text,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  completed_at    timestamptz
);

create index idx_workflow_runs_business on workflow_runs (business_id);
create index idx_workflow_runs_status on workflow_runs (status);
create index idx_workflow_runs_type on workflow_runs (workflow_type);

-- ============================================================
-- workflow_step_runs — per-step execution records
-- ============================================================

create table workflow_step_runs (
  id              uuid primary key default uuid_generate_v4(),
  workflow_run_id uuid not null references workflow_runs (id) on delete cascade,
  step_key        text not null,
  step_name       text not null,
  status          text not null default 'pending'
                    check (status in ('pending', 'running', 'completed', 'failed', 'skipped', 'waiting_approval')),
  agent_name      text,
  input_payload   jsonb not null default '{}',
  output_payload  jsonb,
  error_message   text,
  approval_id     text,
  tokens_used     integer not null default 0,
  cost_cents      integer not null default 0,
  duration_ms     integer not null default 0,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  started_at      timestamptz,
  completed_at    timestamptz
);

create index idx_step_runs_workflow on workflow_step_runs (workflow_run_id);
create index idx_step_runs_status on workflow_step_runs (status);

-- ── Updated_at triggers ─────────────────────────────────────

create trigger trg_workflow_runs_updated_at
  before update on workflow_runs
  for each row execute function update_updated_at();

create trigger trg_workflow_step_runs_updated_at
  before update on workflow_step_runs
  for each row execute function update_updated_at();
