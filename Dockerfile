FROM python:3.11-slim

WORKDIR /app

# Copy dependency manifests first for layer caching
COPY apps/api/pyproject.toml ./apps/api/
COPY packages/ai/pyproject.toml ./packages/ai/
COPY packages/agents/pyproject.toml ./packages/agents/
COPY packages/workflows/pyproject.toml ./packages/workflows/
COPY packages/integrations/pyproject.toml ./packages/integrations/

# Copy source
COPY apps/api/src ./apps/api/src
COPY packages/ai/src ./packages/ai/src
COPY packages/agents/src ./packages/agents/src
COPY packages/workflows/src ./packages/workflows/src
COPY packages/integrations/src ./packages/integrations/src

# Install all packages
RUN pip install --no-cache-dir \
    ./packages/ai \
    ./packages/agents \
    ./packages/workflows \
    ./packages/integrations \
    ./apps/api

EXPOSE 8000

# Use shell form so $PORT is evaluated at runtime (Railway/Render set PORT)
CMD uvicorn abf_api.main:app --host 0.0.0.0 --port ${PORT:-8000}
