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
        created += self._seed_scheme_rules(db)
        created += self._seed_evidence_chunks(db)
        created += self._seed_memory(db)
        db.commit()
        return created

    def _seed_drugs(self, db: Session) -> int:
        if db.query(Drug).count() > 0:
            return 0
        drugs = [
            Drug(brand_name="Augmentin 625", generic_name="Amoxicillin + Clavulanic Acid", composition="Amoxicillin 500mg + Clavulanic Acid 125mg", dosage_form="tablet", schedule_category="Schedule H", is_prescription_required=True, manufacturer="GSK"),
            Drug(brand_name="Calpol 500", generic_name="Paracetamol", composition="Paracetamol 500mg", dosage_form="tablet", schedule_category="OTC", is_prescription_required=False, manufacturer="GSK"),
            Drug(brand_name="Glycomet GP1", generic_name="Metformin + Glimepiride", composition="Metformin 500mg + Glimepiride 1mg", dosage_form="tablet", schedule_category="Schedule G", is_prescription_required=True, manufacturer="USV"),
            Drug(brand_name="Ozempic", generic_name="Semaglutide", composition="Semaglutide 0.5mg/0.25mg", dosage_form="injection", schedule_category="Schedule H", is_prescription_required=True, manufacturer="Novo Nordisk", is_high_risk=True),
            Drug(brand_name="Alprazolam 0.5", generic_name="Alprazolam", composition="Alprazolam 0.5mg", dosage_form="tablet", schedule_category="Schedule X", is_prescription_required=True, manufacturer="Various", is_high_risk=True),
        ]
        db.add_all(drugs)
        db.flush()
        return len(drugs)

    def _seed_inventory(self, db: Session) -> int:
        if db.query(InventoryItem).count() > 0:
            return 0
        augmentin = db.query(Drug).filter(Drug.brand_name == "Augmentin 625").first()
        items = [
            InventoryItem(
                drug_id=augmentin.id if augmentin else None,
                location_id="PHARMACY_MUMBAI_01",
                state="Maharashtra",
                quantity_on_hand=50,
                reorder_threshold=10,
                batch_number="AUG12345",
                expiry_date=date(2027, 12, 31),
                supplier_name="Licensed Pharma Distributor",
            )
        ]
        db.add_all(items)
        return len(items)

    def _seed_prices(self, db: Session) -> int:
        if db.query(PriceRecord).count() > 0:
            return 0
        records = [
            PriceRecord(generic_name="Amoxicillin + Clavulanic Acid", brand_name="Augmentin 625", mrp=220.50, ceiling_price=180.00, source="NPPA", last_checked_at=datetime.now(timezone.utc)),
            PriceRecord(generic_name="Paracetamol", brand_name="Calpol 500", mrp=32.00, ceiling_price=30.00, source="NPPA", last_checked_at=datetime.now(timezone.utc)),
        ]
        db.add_all(records)
        return len(records)

    def _seed_janaushadhi(self, db: Session) -> int:
        if db.query(JanAushadhiProduct).count() > 0:
            return 0
        products = [
            JanAushadhiProduct(generic_name="Amoxicillin 500mg + Clavulanic Acid 125mg", composition="Same as Augmentin 625", pack_size="6 Tablets", janaushadhi_price=60.00, availability_status="Available", source="PMBJP"),
            JanAushadhiProduct(generic_name="Paracetamol 500mg", composition="Paracetamol 500mg", pack_size="10 Tablets", janaushadhi_price=10.00, availability_status="Available", source="PMBJP"),
        ]
        db.add_all(products)
        return len(products)

    def _seed_schedule_rules(self, db: Session) -> int:
        if db.query(DrugScheduleRule).count() > 0:
            return 0
        rules = [
            DrugScheduleRule(schedule_category="Schedule H", rule_summary="Prescription-only medicine. Requires valid prescription from Registered Medical Practitioner.", requires_prescription=True, source="CDSCO"),
            DrugScheduleRule(schedule_category="Schedule H1", rule_summary="Strict control. Requires separate register with patient and doctor details. Supply restricted.", requires_prescription=True, requires_sales_register=True, source="CDSCO"),
            DrugScheduleRule(schedule_category="Schedule X", rule_summary="Narcotic/Psychotropic. Requires triplicate prescription. Special storage and reporting mandatory.", requires_prescription=True, requires_sales_register=True, requires_special_storage=True, source="CDSCO"),
        ]
        db.add_all(rules)
        return len(rules)

    def _seed_nsq_alerts(self, db: Session) -> int:
        if db.query(NSQAlert).count() > 0:
            return 0
        alerts = [
            NSQAlert(drug_name="Paracetamol", brand_name="Demo-Par-500", manufacturer="Fake Pharma Ltd", batch_number="B123", month="April", year=2026, failure_reason="Dissolution failure", alert_type="NSQ", source="CDSCO"),
            NSQAlert(drug_name="Semaglutide", brand_name="Ozempic Generic", manufacturer="Unknown", batch_number="OZ999", month="March", year=2026, failure_reason="Suspected Spurious - No Active Ingredient", alert_type="SPURIOUS", source="CDSCO"),
        ]
        db.add_all(alerts)
        return len(alerts)

    def _seed_suppliers(self, db: Session) -> int:
        if db.query(Supplier).count() > 0:
            return 0
        suppliers = [
            Supplier(supplier_name="Cheap Semaglutide India", seller_type="unknown_online_seller", risk_score=0.9, risk_reasons_json={"missing_license": True, "claims_no_prescription": True}),
            Supplier(supplier_name="Licensed Pharma Distributor", seller_type="licensed_distributor", license_number="DL-12345/2020", state="Maharashtra", risk_score=0.05),
        ]
        db.add_all(suppliers)
        return len(suppliers)

    def _seed_scheme_rules(self, db: Session) -> int:
        if db.query(SchemeRule).count() > 0:
            return 0
        rules = [
            SchemeRule(scheme_name="PM-JAY (Ayushman Bharat)", scheme_type="Government", eligibility_summary="Families in SECC database.", coverage_summary="Up to 5 Lakh per year for hospitalization. Medicine included in hospital package.", applies_to_retail_pharmacy=False, applies_to_hospitalization=True, source="Government of India"),
            SchemeRule(scheme_name="CGHS", scheme_type="Government", eligibility_summary="Central Government employees and pensioners.", coverage_summary="Cashless at empanelled providers or reimbursement for retail purchase.", applies_to_retail_pharmacy=True, applies_to_hospitalization=True, source="Ministry of Health"),
        ]
        db.add_all(rules)
        return len(rules)

    def _seed_memory(self, db: Session) -> int:
        if db.query(MemoryItem).count() > 0:
            return 0
        item = MemoryItem(
            memory_type="substitution_preference",
            scope="GLOBAL",
            key="Augmentin::Preference",
            value_json={"janaushadhi_preferred_if_budget_limited": True},
            confidence=0.9,
        )
        db.add(item)
        return 1

    def _seed_evidence_chunks(self, db: Session) -> int:
        if db.query(EvidenceChunk).count() > 0:
            return 0
        payloads: list[dict[str, Any]] = []
        
        # CDSCO NSQ Guidance
        payloads.extend(chunk_section_aware_text(
            "CDSCO NSQ GUIDANCE:\nMonthly NSQ lists published by CDSCO alert pharmacies to batches failing quality tests. "
            "Pharmacies must quarantine matched batches immediately and inform State Licensing Authorities.",
            source_type="regulatory", source_name="CDSCO", document_title="NSQ Handling SOP"
        ))
        
        # Schedule H1/X Guidance
        payloads.extend(chunk_section_aware_text(
            "SCHEDULE H1 COMPLIANCE:\nRetailers must maintain a separate register for Schedule H1 drugs. "
            "Details like Patient Name, Doctor Name, Date, and Quantity must be logged and kept for 3 years.",
            source_type="regulatory", source_name="Drugs and Cosmetics Act", document_title="Schedule H1 Rules"
        ))
        
        # Jan Aushadhi Guidance
        payloads.extend(chunk_section_aware_text(
            "JAN AUSHADHI SUBSTITUTION:\nPMBJP medicines are high-quality generics tested at NABL labs. "
            "They are commonly 50-80% cheaper than premium brands. Pharmacists can suggest them as affordable options.",
            source_type="affordability", source_name="PMBJP", document_title="Pharmacist Guide to PMBJP"
        ))

        created = 0
        for payload in payloads:
            chunk = EvidenceChunk(**payload)
            self.vector_store.upsert_text(db, chunk)
            created += 1
        return created
