-- ABF Role-Based Access Control
-- Migration 004: User roles table.
--
-- Roles: owner, admin, operator, analyst, viewer
-- Each user gets one role per record. A user can have different roles
-- in different business contexts, but for MVP we use a single global role.

create table user_roles (
  id         uuid primary key default uuid_generate_v4(),
  user_id    uuid not null,
  role       text not null default 'viewer'
               check (role in ('owner', 'admin', 'operator', 'analyst', 'viewer')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id)
);

create index idx_user_roles_user_id on user_roles (user_id);

create trigger trg_user_roles_updated_at
  before update on user_roles
  for each row execute function update_updated_at();
