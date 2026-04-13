# Autonomous Business Factory (ABF)

An autonomous business operations platform that orchestrates AI agents, workflows, and integrations to automate complex business processes.

## Architecture

```
apps/
  dashboard/       Next.js 14 frontend (App Router, TypeScript, Tailwind, shadcn/ui)
  api/             FastAPI backend (Python 3.11+)

packages/
  core/            Shared TypeScript types
  db/              Supabase client, types, query helpers, SQL migrations
  ai/              LLM provider abstraction, AI task router, memory layer
  agents/          Agent framework: Opportunity, Decision, Execution, Analytics
  workflows/       Persistent workflow engine (Product Launch, Campaign Optimization)
  integrations/    External service connectors (Meta Ads, Google Ads, Shopify, Stripe)
```

## Tech Stack

| Layer       | Technology                                       |
|-------------|--------------------------------------------------|
| Frontend    | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui  |
| Backend     | FastAPI, Python 3.11+, Pydantic                  |
| Database    | Supabase (Postgres)                              |
| Auth        | Supabase Auth                                    |
| AI          | OpenAI (GPT-4o), Anthropic (Claude Sonnet)       |
| Deployment  | Vercel (frontend), Railway/Render (backend)       |

---

## Local Development Setup

### Prerequisites

- **Node.js** 20+ and **pnpm** 9+
- **Python** 3.11+
- A **Supabase** project (free tier works)

### 1. Clone and install

```bash
git clone <repo-url> && cd Corestack

# Frontend dependencies
pnpm install

# Python dependencies (use a virtual environment)
python -m venv .venv && source .venv/bin/activate
pip install -e "apps/api[dev]"
pip install -e "packages/ai[dev]"
pip install -e "packages/agents[dev]"
pip install -e "packages/workflows[dev]"
pip install -e "packages/integrations[dev]"
```

### 2. Set up Supabase

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run the migrations in order:
   ```
   packages/db/migrations/001_initial_schema.sql
   packages/db/migrations/002_seed.sql
   packages/db/migrations/003_workflow_runs.sql
   ```
3. Copy your project credentials from **Settings > API**:
   - Project URL
   - `anon` public key
   - `service_role` secret key

### 3. Configure environment variables

```bash
# Frontend
cp apps/dashboard/.env.example apps/dashboard/.env.local

# Backend
cp apps/api/.env.example apps/api/.env
```

Edit both files and fill in your Supabase credentials and AI provider keys.

### 4. Start development servers

```bash
# Terminal 1: Dashboard (http://localhost:3000)
pnpm dev

# Terminal 2: API (http://localhost:8000)
pnpm dev:api
```

The API docs are at [http://localhost:8000/docs](http://localhost:8000/docs).

### 5. Create a user

1. Go to your Supabase dashboard > **Authentication > Users**
2. Click **Add User** and create an email/password user
3. Log in at [http://localhost:3000/login](http://localhost:3000/login)

---

## Deployment

### Frontend on Vercel

1. Push your repo to GitHub
2. Go to [vercel.com](https://vercel.com) and import the repository
3. Set the **Root Directory** to `apps/dashboard`
4. Set the **Framework Preset** to `Next.js`
5. Add environment variables:

   | Variable | Value |
   |----------|-------|
   | `NEXT_PUBLIC_SUPABASE_URL` | Your Supabase project URL |
   | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Your Supabase anon key |

6. Deploy

### Backend on Railway

1. Go to [railway.app](https://railway.app) and create a new project
2. Connect your GitHub repo
3. Railway auto-detects the `Dockerfile` at the repo root
5. Add environment variables:

   | Variable | Value |
   |----------|-------|
   | `SUPABASE_URL` | Your Supabase project URL |
   | `SUPABASE_SERVICE_ROLE_KEY` | Your Supabase service role key |
   | `SUPABASE_ANON_KEY` | Your Supabase anon key |
   | `OPENAI_API_KEY` | Your OpenAI key |
   | `ANTHROPIC_API_KEY` | Your Anthropic key |
   | `CORS_ORIGINS` | Your Vercel domain (e.g. `https://abf.vercel.app`) |
   | `ENVIRONMENT` | `production` |
   | `LOG_LEVEL` | `INFO` |

6. Deploy

### Backend on Render (alternative)

1. Go to [render.com](https://render.com) > create **Web Service**
2. Connect repo, set root directory to `apps/api`
3. **Build Command**: `pip install .`
4. **Start Command**: `uvicorn abf_api.main:app --host 0.0.0.0 --port $PORT`
5. Add the same environment variables as Railway
6. Deploy

### Supabase

Your Supabase project handles Postgres, Auth, and Storage. After deploying, update your Vercel frontend's Supabase URL and the backend's CORS_ORIGINS to match your production domains.

---

## Project Scripts

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start the Next.js dashboard (port 3000) |
| `pnpm dev:api` | Start the FastAPI server (port 8000) |
| `pnpm build` | Build all TypeScript packages |
| `pnpm lint` | Lint TypeScript packages |
| `pnpm typecheck` | Type-check TypeScript packages |

---

## API Endpoints

| Group | Path | Description |
|-------|------|-------------|
| Health | `GET /health` | Status, version, environment |
| Health | `GET /health/ready` | Deep check with DB connectivity |
| Businesses | `/api/businesses` | Full CRUD |
| Products | `/api/products` | Full CRUD |
| Campaigns | `/api/campaigns` | CRUD + channel filter |
| Tasks | `/api/tasks` | CRUD + agent/status filter |
| Agent Runs | `/api/agent-runs` | Execution history |
| Approvals | `/api/approvals` | List, create, approve, reject |
| Audit Logs | `/api/audit-logs` | Append-only event log |
| Execute | `POST /api/execute` | Run agent on task |
| AI Route | `POST /api/ai/route` | Route task to correct LLM |
| Workflows | `POST /api/workflows/product-launch` | Product launch pipeline |
| Workflows | `POST /api/workflows/campaign-optimization` | Campaign optimization |
| Integrations | `POST /api/integrations/dispatch` | Dispatch integration action |
| Memory | `/api/memory` | Agent learning storage |

---

## License

Private — All rights reserved.
