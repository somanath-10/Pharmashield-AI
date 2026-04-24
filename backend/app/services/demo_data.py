from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import (
    Drug,
    EvidenceChunk,
    InventoryItem,
    MemoryItem,
    PayerPolicy,
    RecallEvent,
    ShortageEvent,
)
from app.services.data_connectors.dailymed import DailyMedConnector
from app.services.data_connectors.mock_payer_policy import MockPayerPolicyConnector
from app.services.data_connectors.openfda_enforcement import OpenFDAEnforcementConnector
from app.services.data_connectors.openfda_shortages import OpenFDAShortagesConnector
from app.services.rag.chunking import chunk_section_aware_text
from app.services.rag.vector_store import VectorStore


class DemoDataService:
    def __init__(self) -> None:
        self.policy_connector = MockPayerPolicyConnector()
        self.vector_store = VectorStore()
        self.shortage_connector = OpenFDAShortagesConnector()
        self.enforcement_connector = OpenFDAEnforcementConnector()
        self.dailymed_connector = DailyMedConnector()

    def seed_demo_dataset(self, db: Session) -> int:
        created = 0
        created += self._seed_drugs(db)
        created += self._seed_inventory(db)
        created += self._seed_shortages(db)
        created += self._seed_recalls(db)
        created += self._seed_policies(db)
        created += self._seed_evidence_chunks(db)
        created += self._seed_memory(db)
        db.commit()
        return created

    async def ingest_public_sources(self, db: Session) -> int:
        created = 0
        for drug_name in ("semaglutide", "tirzepatide"):
            try:
                shortages = await self.shortage_connector.search(drug_name=drug_name, limit=3)
            except Exception:
                shortages = []
            for payload in shortages:
                if not self._shortage_exists(db, payload["drug_name"], payload.get("status")):
                    db.add(ShortageEvent(**payload))
                    created += 1

            try:
                recalls = await self.enforcement_connector.search(product_description=drug_name, limit=3)
            except Exception:
                recalls = []
            for payload in recalls:
                if not self._recall_exists(db, payload["drug_name"], payload.get("reason_for_recall")):
                    db.add(RecallEvent(**payload))
                    created += 1

            try:
                spls = await self.dailymed_connector.search_spls(drug_name)
            except Exception:
                spls = []
            if spls:
                created += self._store_dailymed_stub(db, drug_name, spls[0])
        db.commit()
        return created

    def _seed_drugs(self, db: Session) -> int:
        if db.query(Drug).count() > 0:
            return 0
        drugs = [
            Drug(brand_name="Ozempic", generic_name="semaglutide", active_ingredient="semaglutide", dosage_form="injection", route="subcutaneous", manufacturer="Novo Nordisk"),
            Drug(brand_name="Wegovy", generic_name="semaglutide", active_ingredient="semaglutide", dosage_form="injection", route="subcutaneous", manufacturer="Novo Nordisk"),
            Drug(brand_name="Rybelsus", generic_name="semaglutide", active_ingredient="semaglutide", dosage_form="tablet", route="oral", manufacturer="Novo Nordisk"),
            Drug(brand_name="Mounjaro", generic_name="tirzepatide", active_ingredient="tirzepatide", dosage_form="injection", route="subcutaneous", manufacturer="Eli Lilly"),
            Drug(brand_name="Zepbound", generic_name="tirzepatide", active_ingredient="tirzepatide", dosage_form="injection", route="subcutaneous", manufacturer="Eli Lilly"),
        ]
        db.add_all(drugs)
        db.flush()
        return len(drugs)

    def _seed_inventory(self, db: Session) -> int:
        if db.query(InventoryItem).count() > 0:
            return 0
        ozempic = db.query(Drug).filter(Drug.brand_name == "Ozempic").first()
        items = [
            InventoryItem(
                drug_id=ozempic.id if ozempic else None,
                location_id="PHARMACY_001",
                quantity_on_hand=0,
                reorder_threshold=2,
                supplier_name="Primary Wholesaler",
            )
        ]
        db.add_all(items)
        return len(items)

    def _seed_shortages(self, db: Session) -> int:
        if db.query(ShortageEvent).count() > 0:
            return 0
        events = [
            ShortageEvent(
                drug_name="Ozempic",
                generic_name="semaglutide",
                status="current_or_reported",
                reason="Intermittent wholesaler allocation pressure and sustained demand across GLP-1 channels.",
                therapeutic_category="GLP-1",
                source="openFDA",
                source_url="https://api.fda.gov/drug/shortages.json",
                initial_posting_date=datetime(2026, 1, 15, tzinfo=timezone.utc),
                last_updated=datetime(2026, 4, 12, tzinfo=timezone.utc),
                raw_payload_json={"demo": True},
            ),
            ShortageEvent(
                drug_name="semaglutide",
                generic_name="semaglutide",
                status="current_or_reported",
                reason="Supply remains variable; pharmacies should confirm inventory before scheduling fills.",
                therapeutic_category="GLP-1",
                source="openFDA",
                source_url="https://api.fda.gov/drug/shortages.json",
                initial_posting_date=datetime(2026, 2, 2, tzinfo=timezone.utc),
                last_updated=datetime(2026, 4, 20, tzinfo=timezone.utc),
                raw_payload_json={"demo": True},
            ),
        ]
        db.add_all(events)
        return len(events)

    def _seed_recalls(self, db: Session) -> int:
        if db.query(RecallEvent).count() > 0:
            return 0
        recalls = [
            RecallEvent(
                drug_name="semaglutide online products",
                classification="Class II",
                reason_for_recall="Unapproved semaglutide-labeled online products lacked complete supply-chain verification.",
                recalling_firm="Example Internet Fulfillment LLC",
                distribution_pattern="Nationwide internet sales",
                product_description="Semaglutide online vial marketed as generic Ozempic",
                code_info="Lot information unavailable",
                source="openFDA",
                source_url="https://api.fda.gov/drug/enforcement.json",
                raw_payload_json={"demo": True},
            )
        ]
        db.add_all(recalls)
        return len(recalls)

    def _seed_policies(self, db: Session) -> int:
        if db.query(PayerPolicy).count() > 0:
            return 0
        policies = []
        for policy in self.policy_connector.policies():
            policies.append(
                PayerPolicy(
                    payer_name=policy["payer_name"],
                    therapy_area=policy["therapy_area"],
                    drug_name=policy["drug_name"],
                    policy_title=policy["policy_title"],
                    criteria_text=policy["criteria_text"],
                    effective_date=policy["effective_date"],
                    source=policy["source"],
                    source_url=policy["source_url"],
                )
            )
        db.add_all(policies)
        return len(policies)

    def _seed_memory(self, db: Session) -> int:
        if db.query(MemoryItem).count() > 0:
            return 0
        item = MemoryItem(
            memory_type="payer_requirement",
            scope="PAYER",
            key="Demo Health Plan::GLP-1",
            value_json={"common_missing_docs": ["BMI", "A1c", "chart notes", "metformin trial"]},
            confidence=0.8,
        )
        db.add(item)
        return 1

    def _seed_evidence_chunks(self, db: Session) -> int:
        if db.query(EvidenceChunk).count() > 0:
            return 0
        payloads: list[dict[str, Any]] = []
        payloads.extend(
            chunk_section_aware_text(
                (
                    "SHORTAGE STATUS:\nOzempic and semaglutide availability remains variable. Pharmacies should confirm stock, "
                    "use prescriber-reviewed substitution workflows, and maintain follow-up lists for patients awaiting GLP-1 therapy."
                ),
                source_type="shortage",
                source_name="openFDA",
                source_url="https://api.fda.gov/drug/shortages.json",
                document_title="GLP-1 Shortage Snapshot",
                default_section="shortage_status",
                extra_metadata={
                    "source": "openFDA",
                    "drug_name": "semaglutide",
                    "status": "current_or_reported",
                    "last_updated": "2026-04-20T00:00:00+00:00",
                },
            )
        )
        for policy in self.policy_connector.policies():
            payloads.extend(
                chunk_section_aware_text(
                    f"APPROVAL CRITERIA:\n{policy['criteria_text']}\nDENIAL REASONS:\n{' ; '.join(policy['denial_reasons'])}",
                    source_type="payer_policy",
                    source_name=policy["source"],
                    source_url=policy["source_url"],
                    document_title=policy["policy_title"],
                    default_section="approval_criteria",
                    extra_metadata={
                        "source": "payer_policy",
                        "payer_name": policy["payer_name"],
                        "drug_name": policy["drug_name"],
                        "effective_date": policy["effective_date"].isoformat(),
                    },
                )
            )
        payloads.extend(
            chunk_section_aware_text(
                (
                    "UNSAFE CLAIMS:\nProducts marketed as 'generic Ozempic', 'no prescription needed', or "
                    "'FDA-approved compounded semaglutide' should be treated as verification red flags until a regulated supply chain is confirmed.\n"
                    "PATIENT COUNSELING:\nDirect patients to licensed pharmacies and prescriber-supervised therapy pathways."
                ),
                source_type="compliance",
                source_name="PharmaShield Demo Compliance Notes",
                source_url="https://example.local/compliance/glp1",
                document_title="GLP-1 Compliance Guardrails",
                default_section="unsafe_claims",
                extra_metadata={
                    "source": "general_note",
                    "topic": "GLP-1 compounding",
                },
            )
        )
        payloads.extend(
            chunk_section_aware_text(
                (
                    "WARNINGS AND PRECAUTIONS:\nSubstitution among GLP-1 products should not be treated as automatic interchange. "
                    "Route, formulation, indication, and payer criteria require pharmacist and prescriber review.\n"
                    "PATIENT COUNSELING:\nUse regulated supply channels and confirm product identifiers before dispensing."
                ),
                source_type="drug_label",
                source_name="DailyMed",
                source_url="https://dailymed.nlm.nih.gov",
                document_title="Semaglutide Label Highlights",
                default_section="warnings_and_precautions",
                extra_metadata={
                    "source": "dailymed",
                    "drug_name": "semaglutide",
                    "section": "warnings_and_precautions",
                },
            )
        )
        created = 0
        for payload in payloads:
            chunk = EvidenceChunk(**payload)
            self.vector_store.upsert_text(db, chunk)
            created += 1
        return created

    @staticmethod
    def _shortage_exists(db: Session, drug_name: str, status: str | None) -> bool:
        return (
            db.query(ShortageEvent)
            .filter(ShortageEvent.drug_name == drug_name)
            .filter(ShortageEvent.status == status)
            .first()
            is not None
        )

    @staticmethod
    def _recall_exists(db: Session, drug_name: str, reason: str | None) -> bool:
        return (
            db.query(RecallEvent)
            .filter(RecallEvent.drug_name == drug_name)
            .filter(RecallEvent.reason_for_recall == reason)
            .first()
            is not None
        )

    def _store_dailymed_stub(self, db: Session, drug_name: str, spl: dict[str, Any]) -> int:
        title = spl.get("title") or f"{drug_name} label"
        chunk = EvidenceChunk(
            source_type="drug_label",
            source_name="DailyMed",
            source_url="https://dailymed.nlm.nih.gov",
            document_title=title,
            section_title="warnings_and_precautions",
            chunk_text=f"DailyMed label metadata available for {drug_name}: {title}",
            metadata_json={
                "source": "dailymed",
                "drug_name": drug_name,
                "section": "warnings_and_precautions",
                "last_updated": date.today().isoformat(),
            },
        )
        self.vector_store.upsert_text(db, chunk)
        return 1
