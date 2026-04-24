from __future__ import annotations

import re

from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session

from app.db.models import EvidenceChunk


class KeywordStore:
    def search(self, db: Session, *, query: str, limit: int) -> list[tuple[EvidenceChunk, float]]:
        chunks = db.query(EvidenceChunk).all()
        if not chunks:
            return []
        tokenized_chunks = [self._tokenize(chunk.chunk_text) for chunk in chunks]
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
        bm25 = BM25Okapi(tokenized_chunks)
        scores = bm25.get_scores(query_tokens)
        ranked = sorted(zip(chunks, scores, strict=False), key=lambda item: item[1], reverse=True)
        return [(chunk, float(score)) for chunk, score in ranked[:limit] if score > 0]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"[a-zA-Z0-9\-]+", text.lower())
