from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from app.core.constants import SECTION_PRIORITY, SOURCE_PRIORITY, drug_aliases
from app.db.models import EvidenceChunk


class RetrievalResult(dict):
    pass


class SimpleReranker:
    def rerank(
        self,
        results: list[dict[str, Any]],
        *,
        query: str,
        drug_name: str | None = None,
        payer_name: str | None = None,
        limit: int = 8,
    ) -> list[dict[str, Any]]:
        query_terms = set(re.findall(r"[a-zA-Z0-9\-]+", query.lower()))
        aliases = set(drug_aliases(drug_name))
        payer_name_normalized = (payer_name or "").lower()
        reranked: list[dict[str, Any]] = []
        for result in results:
            chunk: EvidenceChunk = result["chunk"]
            chunk_terms = set(re.findall(r"[a-zA-Z0-9\-]+", chunk.chunk_text.lower()))
            lexical_overlap = len(query_terms & chunk_terms) / max(len(query_terms), 1)
            metadata = chunk.metadata_json or {}
            source_score = SOURCE_PRIORITY.get(str(metadata.get("source", metadata.get("source_type", ""))).lower(), 1.0)
            section = str(chunk.section_title or metadata.get("section") or "").lower()
            section_score = SECTION_PRIORITY.get(section, 1.0)
            exact_drug = 1.5 if aliases and any(alias in chunk.chunk_text.lower() for alias in aliases) else 0.0
            exact_payer = 1.5 if payer_name_normalized and payer_name_normalized in chunk.chunk_text.lower() else 0.0
            recency = self._recency_score(metadata.get("effective_date") or metadata.get("last_updated"))
            result["score"] = round(
                result.get("score", 0.0)
                + lexical_overlap
                + source_score
                + section_score
                + exact_drug
                + exact_payer
                + recency,
                4,
            )
            reranked.append(result)
        reranked.sort(key=lambda item: item["score"], reverse=True)
        return reranked[:limit]

    @staticmethod
    def _recency_score(raw_value: Any) -> float:
        if not raw_value:
            return 0.0
        if isinstance(raw_value, str):
            try:
                parsed = datetime.fromisoformat(raw_value)
            except ValueError:
                return 0.0
        elif isinstance(raw_value, datetime):
            parsed = raw_value
        else:
            return 0.0
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        age_days = max((datetime.now(timezone.utc) - parsed).days, 0)
        return max(0.0, 1.0 - min(age_days / 365, 1.0))
