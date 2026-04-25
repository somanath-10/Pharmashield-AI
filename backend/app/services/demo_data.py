from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import (
    Drug,
    EvidenceChunk,
    InventoryItem,
    MemoryItem,
    PriceRecord,
    JanAushadhiProduct,
    DrugScheduleRule,
    NSQAlert,
    Supplier,
    SchemeRule,
    PatientProfile,
    RedFlagSeller,
    RegulatoryGuideline,
    Pharmacist,
)
from app.services.rag.chunking import chunk_section_aware_text
from app.services.rag.vector_store import VectorStore


class DemoDataService:
    def __init__(self) -> None:
        self.vector_store = VectorStore()

    def seed_demo_dataset(self, db: Session) -> int:
        created = 0
        created += self._seed_drugs(db)
        created += self._seed_inventory(db)
        created += self._seed_prices(db)
        created += self._seed_janaushadhi(db)
        created += self._seed_schedule_rules(db)
        created += self._seed_nsq_alerts(db)
        created += self._seed_suppliers(db)
        created += self._seed_red_flags(db)
        created += self._seed_patients(db)
        created += self._seed_pharmacists(db)
        created += self._seed_guidelines(db)
        created += self._seed_scheme_rules(db)
        created += self._seed_evidence_chunks(db)
        created += self._seed_memory(db)
        db.commit()
        return created

    def _seed_drugs(self, db: Session) -> int:
        if db.query(Drug).count() > 0:
            return 0
        drugs = [
            # Antibiotics
            Drug(brand_name="Augmentin 625 Duo", generic_name="Amoxicillin + Clavulanic Acid", composition="Amoxicillin 500mg + Clavulanic Acid 125mg", dosage_form="tablet", schedule_category="Schedule H", is_prescription_required=True, manufacturer="GlaxoSmithKline"),
            Drug(brand_name="Azithral 500", generic_name="Azithromycin", composition="Azithromycin 500mg", dosage_form="tablet", schedule_category="Schedule H", is_prescription_required=True, manufacturer="Alembic"),
            
            # Anti-diabetics
            Drug(brand_name="Glycomet GP 1 Forte", generic_name="Metformin + Glimepiride", composition="Metformin 1000mg + Glimepiride 1mg", dosage_form="tablet", schedule_category="Schedule G", is_prescription_required=True, manufacturer="USV"),
            Drug(brand_name="Ozempic 0.5mg", generic_name="Semaglutide", composition="Semaglutide 0.5mg", dosage_form="injection", schedule_category="Schedule H", is_prescription_required=True, manufacturer="Novo Nordisk", is_high_risk=True),
            
            # Others
            Drug(brand_name="Calpol 650", generic_name="Paracetamol", composition="Paracetamol 650mg", dosage_form="tablet", schedule_category="Schedule H", is_prescription_required=True, manufacturer="GlaxoSmithKline"),
        ]
        db.add_all(drugs)
        db.flush()
        return len(drugs)

    def _seed_inventory(self, db: Session) -> int:
        if db.query(InventoryItem).count() > 0:
            return 0
        drugs = db.query(Drug).all()
        items = []
        for i, drug in enumerate(drugs):
            items.append(InventoryItem(
                drug_id=drug.id,
                location_id="STORE_CENTRAL_01",
                state="Maharashtra",
                quantity_on_hand=100,
                batch_number=f"B-{i}",
                expiry_date=date(2027, 1, 1),
                supplier_name="Verified Wholesaler Ltd",
            ))
        db.add_all(items)
        return len(items)

    def _seed_prices(self, db: Session) -> int:
        if db.query(PriceRecord).count() > 0:
            return 0
        records = [
            PriceRecord(generic_name="Amoxicillin + Clavulanic Acid", mrp=201.21, ceiling_price=175.50, source="NPPA"),
            PriceRecord(generic_name="Paracetamol 650mg", mrp=30.91, ceiling_price=28.50, source="NPPA"),
        ]
        db.add_all(records)
        return len(records)

    def _seed_janaushadhi(self, db: Session) -> int:
        if db.query(JanAushadhiProduct).count() > 0:
            return 0
        products = [
            JanAushadhiProduct(generic_name="Amoxicillin 500mg + Clavulanic Acid 125mg", pack_size="6 Tablets", janaushadhi_price=58.50, source="PMBJP"),
            JanAushadhiProduct(generic_name="Paracetamol 650mg", pack_size="10 Tablets", janaushadhi_price=11.00, source="PMBJP"),
        ]
        db.add_all(products)
        return len(products)

    def _seed_red_flags(self, db: Session) -> int:
        if db.query(RedFlagSeller).count() > 0:
            return 0
        sellers = [
            RedFlagSeller(seller_identifier="cheap-ozempic-india.com", identifier_type="domain", risk_category="spurious_medicines", evidence_summary="Domain flagged for selling injectable GLP-1 without prescription at 90% discount."),
            RedFlagSeller(seller_identifier="+91-9988776655", identifier_type="whatsapp", risk_category="fraud", evidence_summary="Number reported for soliciting bulk orders of Schedule X drugs via WhatsApp."),
        ]
        db.add_all(sellers)
        return len(sellers)

    def _seed_patients(self, db: Session) -> int:
        if db.query(PatientProfile).count() > 0:
            return 0
        patients = [
            PatientProfile(abha_id="12-3456-7890-1234", full_name="Rahul Sharma", age=45, chronic_diagnoses=["Type 2 Diabetes", "Hypertension"], preferred_language="Hindi"),
            PatientProfile(abha_id="55-8899-0011-2233", full_name="Anita Desai", age=62, chronic_diagnoses=["CKD Stage 3"], preferred_language="Marathi"),
        ]
        db.add_all(patients)
        return len(patients)

    def _seed_pharmacists(self, db: Session) -> int:
        if db.query(Pharmacist).count() > 0:
            return 0
        pharmacists = [
            Pharmacist(full_name="Deepak Varma", pci_registration_number="MH-123456-P", state_council="Maharashtra State Pharmacy Council", qualification="B.Pharm"),
            Pharmacist(full_name="Saritha Rao", pci_registration_number="TS-654321-P", state_council="Telangana State Pharmacy Council", qualification="M.Pharm"),
        ]
        db.add_all(pharmacists)
        return len(pharmacists)

    def _seed_guidelines(self, db: Session) -> int:
        if db.query(RegulatoryGuideline).count() > 0:
            return 0
        lines = [
            RegulatoryGuideline(issuing_authority="CDSCO", circular_number="CDSCO/2024/001", title="Guidelines for Sale of GLP-1 Receptor Agonists", summary="Mandatory prescription verification and cold-chain logging for all Semaglutide/Tirzepatide sales."),
            RegulatoryGuideline(issuing_authority="NPPA", circular_number="NPPA/MEMO/123", title="Ceiling Price Update for Metformin Combinations", summary="Metformin + Glimepiride combinations now capped under DPCO 2013 list expansion."),
        ]
        db.add_all(lines)
        return len(lines)

    def _seed_schedule_rules(self, db: Session) -> int:
        if db.query(DrugScheduleRule).count() > 0:
            return 0
        rules = [
            DrugScheduleRule(schedule_category="Schedule H1", rule_summary="Tracking needed. Record Patient & Doctor info. register for 3 years.", requires_prescription=True, requires_sales_register=True, source="CDSCO"),
        ]
        db.add_all(rules)
        return len(rules)

    def _seed_nsq_alerts(self, db: Session) -> int:
        if db.query(NSQAlert).count() > 0:
            return 0
        alerts = [
            NSQAlert(drug_name="Paracetamol", batch_number="HP88223", month="April", year=2026, failure_reason="Description failure", alert_type="NSQ", source="CDSCO"),
        ]
        db.add_all(alerts)
        return len(alerts)

    def _seed_suppliers(self, db: Session) -> int:
        if db.query(Supplier).count() > 0:
            return 0
        suppliers = [
            Supplier(supplier_name="Global Pharma Wholesale Hyderabad", seller_type="licensed_distributor", verification_status="VERIFIED", risk_score=0.01),
        ]
        db.add_all(suppliers)
        return len(suppliers)

    def _seed_scheme_rules(self, db: Session) -> int:
        if db.query(SchemeRule).count() > 0:
            return 0
        rules = [
            SchemeRule(scheme_name="Ayushman Bharat (PM-JAY)", coverage_summary="5 Lakh/family/year for hospitalization.", applies_to_retail_pharmacy=False, source="NHA"),
        ]
        db.add_all(rules)
        return len(rules)

    def _seed_memory(self, db: Session) -> int:
        if db.query(MemoryItem).count() > 0:
            return 0
        item = MemoryItem(memory_type="substitution_preference", scope="STATE", key="Maharashtra::Generic", value_json={"high_acceptance": True}, confidence=0.85)
        db.add(item)
        return 1

    def _seed_evidence_chunks(self, db: Session) -> int:
        if db.query(EvidenceChunk).count() > 0:
            return 0
        created = 0
        # Reduced logic for brevity
        return created
