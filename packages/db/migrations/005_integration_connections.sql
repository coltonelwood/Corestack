-- ABF Integration Connections
-- Migration 005: Stores provider configuration and connection status.
--
-- SECURITY: This table stores credential metadata (masked keys, config).
-- Raw API secrets for system providers (OpenAI, Anthropic) stay in env vars.
-- User-managed provider secrets (Stripe, Meta, etc.) are stored here.
-- The frontend only ever sees masked values (e.g. "sk-...a1b2").

create table integration_connections (
  id              uuid primary key default uuid_generate_v4(),
  provider        text not null
                    check (provider in (
                      'openai', 'anthropic', 'stripe', 'meta_ads',
                      'google_ads', 'shopify', 'email', 'sms'
                    )),
  display_name    text not null,
  enabled         boolean not null default false,
  status          text not null default 'not_configured'
                    check (status in ('connected', 'error', 'not_configured')),
  -- Credential storage: the key value, stored server-side only.
  -- The frontend receives masked_key instead (e.g. "sk-...a1b2").
  credential_key  text,
  masked_key      text,
  -- Additional non-secret config (account IDs, regions, etc.)
  config          jsonb not null default '{}',
  -- Source: 'env' = from environment variable, 'user' = user-provided
  source          text not null default 'user'
                    check (source in ('env', 'user')),
  -- Status tracking
  last_tested_at  timestamptz,
  last_error      text,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  unique (provider)
);

create index idx_integration_connections_provider on integration_connections (provider);
create index idx_integration_connections_enabled on integration_connections (enabled);

create trigger trg_integration_connections_updated_at
  before update on integration_connections
  for each row execute function update_updated_at();
