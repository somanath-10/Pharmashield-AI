from __future__ import annotations

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    filename: str
    content_type: str
    chunks_indexed: int
    message: str


class IngestResponse(BaseModel):
    status: str
    message: str
    records_created: int = 0
