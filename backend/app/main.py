from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.cases import router as cases_router
from app.api.routes.documents import router as documents_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.health import router as health_router
from app.api.routes.doctor import router as doctor_router
from app.api.routes.ingest import router as ingest_router
from app.api.routes.intelligence import router as intelligence_router
from app.api.routes.patient import router as patient_router
from app.api.routes.pharmacist import router as pharmacist_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.mongodb import init_db
from app.db.postgres import init_postgres_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    if settings.app_env != "test":
        await init_db()
        await init_postgres_db()
    yield


settings = get_settings()
app = FastAPI(title="PharmaShield AI", version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(cases_router)
app.include_router(documents_router)
app.include_router(feedback_router)
app.include_router(ingest_router)
app.include_router(intelligence_router)
app.include_router(doctor_router, prefix="/api/doctor", tags=["doctor"])
app.include_router(patient_router, prefix="/api/patient", tags=["patient"])
app.include_router(pharmacist_router, prefix="/api/pharmacist", tags=["pharmacist"])
app.include_router(admin_router)
