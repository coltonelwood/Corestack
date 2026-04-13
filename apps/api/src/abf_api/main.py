from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from abf_api.config import settings
from abf_api.routers import (
    health,
    businesses,
    products,
    campaigns,
    tasks,
    agent_runs,
    approvals,
    audit_logs,
    execute,
)

app = FastAPI(
    title="Autonomous Business Factory API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(businesses.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(agent_runs.router, prefix="/api")
app.include_router(approvals.router, prefix="/api")
app.include_router(audit_logs.router, prefix="/api")
app.include_router(execute.router, prefix="/api")
