from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from abf_api.config import settings
from abf_api.routers import health

app = FastAPI(
    title="Autonomous Business Factory API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
