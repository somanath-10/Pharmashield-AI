from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import EvidenceChunk
from app.services.rag.embeddings import DeterministicEmbeddingService


class VectorStore:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.embeddings = DeterministicEmbeddingService()

    def upsert_text(self, db: Session, chunk: EvidenceChunk) -> EvidenceChunk:
        if not chunk.id:
            chunk.id = str(uuid.uuid4())
        vector = self.embeddings.embed_text(chunk.chunk_text)
        metadata = dict(chunk.metadata_json or {})
        metadata["embedding_vector"] = vector
        chunk.metadata_json = metadata
        chunk.embedding_id = chunk.embedding_id or f"emb::{chunk.id}"
        db.add(chunk)
        return chunk

    def search(
        self,
        db: Session,
        *,
        query: str,
        limit: int,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[EvidenceChunk, float]]:
        query_vector = self.embeddings.embed_text(query)
        chunks = db.query(EvidenceChunk).all()
        if filters:
            chunks = [
                chunk
                for chunk in chunks
                if all((chunk.metadata_json or {}).get(key) == value for key, value in filters.items())
            ]
        scored: list[tuple[EvidenceChunk, float]] = []
        for chunk in chunks:
            vector = (chunk.metadata_json or {}).get("embedding_vector", [])
            score = self.embeddings.cosine_similarity(query_vector, vector)
            if score > 0:
                scored.append((chunk, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:limit]
