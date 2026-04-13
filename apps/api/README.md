# @abf/api

The FastAPI backend for Autonomous Business Factory.

## Development

```bash
# From the monorepo root
pnpm dev:api

# Or directly
cd apps/api
pip install -e ".[dev]"
uvicorn abf_api.main:app --reload --port 8000
```

Runs on [http://localhost:8000](http://localhost:8000). API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

## Environment Variables

Copy `.env.example` to `.env` and fill in your credentials.

## Structure

```
src/abf_api/
  main.py       → FastAPI app entry point
  config.py     → Settings via pydantic-settings
  routers/
    health.py   → Health check endpoint
```

## Testing

```bash
pytest
```
