from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import EvidenceChunk
from app.db.session import get_db
from app.schemas.document import DocumentUploadResponse
from app.services.rag.chunking import chunk_section_aware_text, parse_uploaded_document
from app.services.rag.vector_store import VectorStore

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    settings = get_settings()
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    destination = settings.upload_path / file.filename
    raw_bytes = await file.read()
    destination.write_bytes(raw_bytes)
    text = parse_uploaded_document(Path(destination), file.content_type or "text/plain", raw_bytes)
    chunks = chunk_section_aware_text(
        text,
        source_type="uploaded_document",
        source_name="Uploaded document",
        source_url=None,
        document_title=file.filename,
        default_section="general",
        extra_metadata={"source": "internal_sop"},
    )
    vector_store = VectorStore()
    for payload in chunks:
        vector_store.upsert_text(db, EvidenceChunk(**payload))
    db.commit()
    return DocumentUploadResponse(
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        chunks_indexed=len(chunks),
        message="Document indexed successfully.",
    )
