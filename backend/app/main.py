from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.cases import router as cases_router
from app.api.routes.documents import router as documents_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.health import router as health_router
from app.api.routes.ingest import router as ingest_router
from app.api.routes.memory import router as memory_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    init_db()
    yield


settings = get_settings()
app = FastAPI(title="PharmaShield AI", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(cases_router)
app.include_router(documents_router)
app.include_router(ingest_router)
app.include_router(feedback_router)
app.include_router(memory_router)
