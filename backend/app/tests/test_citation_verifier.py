from __future__ import annotations

from app.schemas.agent import Citation
from app.services.rag.citation_verifier import CitationVerifier


def test_citation_verifier_deduplicates() -> None:
    citations = [
        Citation(
            id="1",
            source_name="Demo",
            source_url="https://example.com",
            document_title="Doc",
            section_title="Section",
            snippet="Snippet",
            source_type="payer_policy",
        ),
        Citation(
            id="1",
            source_name="Demo",
            source_url="https://example.com",
            document_title="Doc",
            section_title="Section",
            snippet="Snippet",
            source_type="payer_policy",
        ),
    ]
    verified = CitationVerifier().verify(citations)
    assert len(verified) == 1
