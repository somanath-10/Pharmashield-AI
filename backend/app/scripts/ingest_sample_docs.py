from __future__ import annotations

from app.db.models import EvidenceChunk
from app.db.session import SessionLocal, init_db
from app.services.rag.chunking import chunk_section_aware_text
from app.services.rag.vector_store import VectorStore


def main() -> None:
    init_db()
    sample_text = (
        "APPROVAL CRITERIA:\nHospital GLP-1 workflow requires diagnosis confirmation, payer documentation, and pharmacist review.\n"
        "SHORTAGE STATUS:\nIf local stock is depleted, staff should document inventory, place the patient on follow-up, and contact the prescriber before any non-equivalent switch.\n"
        "PATIENT COUNSELING:\nDo not recommend products lacking verified NDC, lot, or licensed distribution."
    )
    chunks = chunk_section_aware_text(
        sample_text,
        source_type="internal_policy",
        source_name="Sample SOP",
        source_url=None,
        document_title="Synthetic Pharmacy SOP",
        default_section="general",
        extra_metadata={"source": "internal_sop"},
    )
    with SessionLocal() as db:
        vector_store = VectorStore()
        for payload in chunks:
            vector_store.upsert_text(db, EvidenceChunk(**payload))
        db.commit()
    print(f"Indexed sample documents. Chunks created: {len(chunks)}")


if __name__ == "__main__":
    main()
