from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.document import IngestResponse
from app.services.demo_data import DemoDataService

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.post("/demo", response_model=IngestResponse)
def ingest_demo(db: Session = Depends(get_db)) -> IngestResponse:
    created = DemoDataService().seed_demo_dataset(db)
    return IngestResponse(status="ok", message="Demo dataset seeded.", records_created=created)


@router.post("/public", response_model=IngestResponse)
async def ingest_public(db: Session = Depends(get_db)) -> IngestResponse:
    created = await DemoDataService().ingest_public_sources(db)
    return IngestResponse(status="ok", message="Public data ingest finished.", records_created=created)
