import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from abf_api.config import settings
from abf_api.logging import setup_logging
from abf_api.errors import register_error_handlers
from abf_api.routers import (
    health,
    businesses,
    products,
    campaigns,
    memory as memory_router,
    tasks,
    agent_runs,
    approvals,
    audit_logs,
    execute,
    ai,
    workflows,
    integrations,
)

logger = logging.getLogger("abf_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info(
        "ABF API starting (env=%s, log_level=%s)",
        settings.environment,
        settings.log_level,
    )
    yield
    logger.info("ABF API shutting down")


app = FastAPI(
    title="Autonomous Business Factory API",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = round((time.perf_counter() - start) * 1000, 1)

    if not request.url.path.startswith("/health"):
        logger.info(
            "%s %s → %s (%sms)",
            request.method,
            request.url.path,
            response.status_code,
            duration,
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration,
            },
        )
    return response


# ── Error handlers ───────────────────────────────────────────

register_error_handlers(app)

# ── Routers ──────────────────────────────────────────────────

app.include_router(health.router)
app.include_router(businesses.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(agent_runs.router, prefix="/api")
app.include_router(approvals.router, prefix="/api")
app.include_router(audit_logs.router, prefix="/api")
app.include_router(execute.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(workflows.router, prefix="/api")
app.include_router(integrations.router, prefix="/api")
app.include_router(memory_router.router, prefix="/api")
