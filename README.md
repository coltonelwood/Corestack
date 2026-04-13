# Autonomous Business Factory (ABF)

An autonomous business operations platform that orchestrates AI agents, workflows, and integrations to automate complex business processes.

## Architecture

```
apps/
  dashboard/       → Next.js 14 web UI (App Router, TypeScript, Tailwind, shadcn/ui)
  api/             → FastAPI backend (Python)

packages/
  core/            → Shared TypeScript types and utilities
  ai/              → AI/ML models and prompt management (Python)
  db/              → Supabase database client and types (TypeScript)
  agents/          → Autonomous agent definitions and orchestration (Python)
  integrations/    → Third-party service connectors (Python)
  workflows/       → Workflow engine and definitions (Python)
```

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| Backend    | FastAPI, Python 3.11+               |
| Database   | Supabase Postgres                   |
| Auth       | Supabase Auth                       |
| Storage    | Supabase Storage                    |

## Getting Started

### Prerequisites

- Node.js 20+
- Python 3.11+
- pnpm 9+

### Setup

```bash
# Install frontend dependencies
pnpm install

# Install Python dependencies
cd apps/api && pip install -e ".[dev]" && cd ../..
cd packages/ai && pip install -e ".[dev]" && cd ../..
cd packages/agents && pip install -e ".[dev]" && cd ../..
cd packages/integrations && pip install -e ".[dev]" && cd ../..
cd packages/workflows && pip install -e ".[dev]" && cd ../..

# Copy environment variables
cp .env.example .env.local
cp apps/dashboard/.env.example apps/dashboard/.env.local
cp apps/api/.env.example apps/api/.env

# Start development
pnpm dev          # Dashboard on :3000
pnpm dev:api      # API on :8000
```

## Development Scripts

| Command           | Description                        |
|-------------------|------------------------------------|
| `pnpm dev`        | Start the Next.js dashboard        |
| `pnpm dev:api`    | Start the FastAPI server           |
| `pnpm build`      | Build all TypeScript packages      |
| `pnpm lint`       | Lint all TypeScript packages       |
| `pnpm typecheck`  | Type-check all TypeScript packages |

## Project Structure

Each package has its own README with detailed documentation. See the individual directories for more information.

## License

Private — All rights reserved.
