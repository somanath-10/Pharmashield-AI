from __future__ import annotations

from app.schemas.agent import Citation


class CitationVerifier:
    def verify(self, citations: list[Citation]) -> list[Citation]:
        deduped: dict[str, Citation] = {}
        for citation in citations:
            deduped[citation.id] = citation
        return list(deduped.values())

    def missing_support_note(self) -> str:
        return "No supporting source found. Needs pharmacist review."
