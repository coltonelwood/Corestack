# @abf/db

Database layer for the Autonomous Business Factory platform. Provides SQL migrations, typed Supabase clients, TypeScript types, and query helpers.

## Schema Overview

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  businesses  │──1:N──│   products   │──1:N──│  campaigns   │
│              │       │              │       │              │
│  id (uuid)   │       │  business_id │       │  business_id │
│  name        │       │  name        │       │  product_id? │
│  domain      │       │  price_cents │       │  channel     │
│  status      │       │  inventory   │       │  budget_cents│
│  metadata    │       │  sales_count │       │  spent_cents │
└──────┬───────┘       └──────────────┘       └──────────────┘
       │
       ├──1:N──┌──────────────┐       ┌──────────────┐
       │       │    tasks     │──1:N──│  agent_runs  │
       │       │              │       │              │
       │       │  business_id │       │  task_id?    │
       │       │  payload (j) │       │  business_id │
       │       │  result (j)  │       │  cost_cents  │
       │       │  priority    │       │  tokens_used │
       │       └──────────────┘       └──────────────┘
       │
       ├──1:N──┌──────────────┐
       │       │  approvals   │
       │       │              │
       │       │  business_id │
       │       │  type        │
       │       │  status      │
       │       │  amount_cents│
       │       └──────────────┘
       │
       ├──1:N──┌──────────────┐
       │       │  audit_logs  │  ← append-only (triggers prevent UPDATE/DELETE)
       │       │              │
       │       │  business_id?│
       │       │  entity_type │
       │       │  entity_id   │
       │       │  diff (json) │
       │       └──────────────┘
       │
       └──1:N──┌──────────────┐
               │   memory     │  ← agent long-term memory
               │              │
               │  business_id?│
               │  agent_name  │
               │  namespace   │
               │  key (unique)│
               │  value (json)│
               └──────────────┘
```

### Tables

| Table | Purpose | Records |
|-------|---------|---------|
| **businesses** | Top-level entities — each autonomous business | Core |
| **products** | Items sold by a business | Belongs to business |
| **campaigns** | Marketing campaigns, optionally linked to a product | Belongs to business |
| **tasks** | Work items assigned to AI agents, with JSON payload/result | Belongs to business |
| **agent_runs** | Execution log for agent invocations with cost tracking | Belongs to business, optionally to task |
| **approvals** | Human-in-the-loop approval queue | Belongs to business |
| **audit_logs** | Immutable event log (append-only, triggers prevent mutation) | References business |
| **memory** | Agent key-value store with namespaces and optional TTL | References business |

### Design Decisions

- **UUIDs** for all primary keys (generated server-side via `uuid_generate_v4()`)
- **Cents** for all monetary values (`price_cents`, `budget_cents`, etc.) to avoid floating-point issues
- **JSONB** for flexible payloads (`metadata`, `payload`, `result`, `diff`, `value`)
- **`updated_at` triggers** auto-fire on all mutable tables
- **Append-only `audit_logs`** enforced by `BEFORE UPDATE/DELETE` triggers that raise exceptions
- **Unique composite index on `memory`** (`business_id, agent_name, namespace, key`) enables upsert semantics
- **Cascading deletes** from business → products, campaigns, tasks, agent_runs, approvals, memory
- **`SET NULL` on delete** for optional FKs (campaign → product, agent_run → task, audit_log → business)

## Migrations

```bash
# Apply via Supabase CLI
supabase db push

# Or run manually in order:
psql $DATABASE_URL -f migrations/001_initial_schema.sql
psql $DATABASE_URL -f migrations/002_seed.sql
```

| File | Description |
|------|-------------|
| `001_initial_schema.sql` | All 8 tables, indexes, triggers, constraints |
| `002_seed.sql` | Realistic sample data (6 businesses, 9 products, 6 campaigns, etc.) |

## TypeScript Usage

```ts
import {
  createClient,
  createServiceClient,
  listBusinesses,
  getTaskById,
  completeAgentRun,
  upsertMemory,
  type BusinessRow,
  type TaskRow,
} from "@abf/db";

// Browser/SSR client (anon key)
const supabase = createClient();
const { data: businesses } = await listBusinesses(supabase, "active");

// Server-only client (service role)
const admin = createServiceClient();
const { data: task } = await getTaskById(admin, "some-uuid");
```

## Query Helpers

Each table has a dedicated module in `src/queries/`:

| Module | Functions |
|--------|-----------|
| `businesses` | `listBusinesses`, `getBusinessById`, `createBusiness`, `updateBusiness`, `deleteBusiness` |
| `products` | `listProducts`, `getProductById`, `createProduct`, `updateProduct`, `deleteProduct` |
| `campaigns` | `listCampaigns`, `getCampaignById`, `createCampaign`, `updateCampaign` |
| `tasks` | `listTasks`, `getTaskById`, `createTask`, `updateTask`, `completeTask`, `failTask` |
| `agent-runs` | `listAgentRuns`, `getAgentRunById`, `createAgentRun`, `updateAgentRun`, `completeAgentRun`, `failAgentRun` |
| `approvals` | `listApprovals`, `getApprovalById`, `createApproval`, `approveApproval`, `rejectApproval` |
| `audit-logs` | `listAuditLogs`, `createAuditLog` |
| `memory` | `getMemory`, `listMemory`, `upsertMemory`, `updateMemory`, `deleteMemory` |
