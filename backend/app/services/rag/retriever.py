from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import EvidenceChunk
from app.schemas.agent import Citation
from app.services.rag.keyword_store import KeywordStore
from app.services.rag.query_expansion import QueryExpansionService
from app.services.rag.reranker import SimpleReranker
from app.services.rag.vector_store import VectorStore


class HybridRetriever:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.query_expander = QueryExpansionService()
        self.vector_store = VectorStore()
        self.keyword_store = KeywordStore()
        self.reranker = SimpleReranker()

    def retrieve(
        self,
        db: Session,
        *,
        query: str,
        drug_name: str | None = None,
        payer_name: str | None = None,
        metadata_filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        expanded_queries = self.query_expander.expand(query, drug_name=drug_name)
        merged: dict[str, dict[str, Any]] = {}
        for candidate_query in expanded_queries:
            for chunk, score in self.vector_store.search(
                db,
                query=candidate_query,
                limit=self.settings.max_retrieved_chunks,
                filters=metadata_filters,
            ):
                self._upsert_result(merged, chunk, score, strategy="vector")
            for chunk, score in self.keyword_store.search(
                db,
                query=candidate_query,
                limit=self.settings.max_retrieved_chunks,
            ):
                if metadata_filters and not self._matches_filters(chunk, metadata_filters):
                    continue
                self._upsert_result(merged, chunk, score, strategy="keyword")
        reranked = self.reranker.rerank(
            list(merged.values()),
            query=query,
            drug_name=drug_name,
            payer_name=payer_name,
            limit=self.settings.max_reranked_chunks,
        )
        return reranked

    def citations_from_results(self, results: list[dict[str, Any]]) -> list[Citation]:
        citations: list[Citation] = []
        for result in results:
            chunk: EvidenceChunk = result["chunk"]
            citations.append(
                Citation(
                    id=chunk.id,
                    source_name=chunk.source_name,
                    source_url=chunk.source_url,
                    document_title=chunk.document_title,
                    section_title=chunk.section_title,
                    snippet=chunk.chunk_text[:280],
                    source_type=chunk.source_type,
                    note=result.get("strategy"),
                )
            )
        return citations

    @staticmethod
    def _upsert_result(
        merged: dict[str, dict[str, Any]],
        chunk: EvidenceChunk,
        score: float,
        *,
        strategy: str,
    ) -> None:
        existing = merged.get(chunk.id)
        if existing:
            existing["score"] = max(existing["score"], score)
            existing["strategies"].add(strategy)
            existing["strategy"] = "+".join(sorted(existing["strategies"]))
            return
        merged[chunk.id] = {
            "chunk": chunk,
            "score": float(score),
            "strategy": strategy,
            "strategies": {strategy},
        }

    @staticmethod
    def _matches_filters(chunk: EvidenceChunk, filters: dict[str, Any]) -> bool:
        metadata = chunk.metadata_json or {}
        return all(metadata.get(key) == value for key, value in filters.items())
