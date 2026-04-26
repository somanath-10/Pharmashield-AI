import asyncio
import logging
from app.db.postgres import init_postgres_db, get_db_session, async_session_maker
from app.models.postgres_models import (
    DrugMaster, InventoryItem, PriceRecord, JanAushadhiProduct,
    DrugScheduleRule, NSQAlert, Supplier, SchemeRule, PharmacyLocation, AuditLog
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_data():
    await init_postgres_db()
    
    async with async_session_maker() as session:
        # Seed Drug Master
        drug = DrugMaster(
            brand_name="Augmentin 625",
            generic_name="Amoxicillin + Clavulanic Acid",
            composition="Amoxicillin 500mg + Clavulanic Acid 125mg",
            strength="625mg",
            dosage_form="Tablet",
            route="Oral",
            manufacturer="GSK",
            schedule_category="H1",
            is_prescription_required=True,
            is_high_risk=False
        )
        session.add(drug)
        
        metformin = DrugMaster(
            brand_name="Glycomet 500",
            generic_name="Metformin",
            composition="Metformin 500mg",
            strength="500mg",
            dosage_form="Tablet",
            route="Oral",
            manufacturer="USV",
            schedule_category="G",
            is_prescription_required=True,
            is_high_risk=False
        )
        session.add(metformin)
        await session.flush()
        
        # Seed Inventory
        inv1 = InventoryItem(
            drug_id=drug.id,
            location_id="HYD_STORE_001",
            state="Telangana",
            quantity_on_hand=0,
            reorder_threshold=5,
            batch_number="AUG123",
            supplier_name="Licensed Distributor",
            supplier_license_number="DL-12345"
        )
        session.add(inv1)
        
        # Seed Price Record
        price = PriceRecord(
            drug_id=drug.id,
            brand_name="Augmentin 625",
            generic_name="Amoxicillin + Clavulanic Acid",
            composition="Amoxicillin 500mg + Clavulanic Acid 125mg",
            mrp=200.0,
            ceiling_price=150.0,
            source="NPPA"
        )
        session.add(price)
        
        # Seed Jan Aushadhi
        ja = JanAushadhiProduct(
            generic_name="Amoxicillin + Clavulanic Acid",
            composition="Amoxicillin 500mg + Clavulanic Acid 125mg",
            strength="625mg",
            dosage_form="Tablet",
            janaushadhi_price=60.0,
            availability_status="AVAILABLE",
            source="PMBJP"
        )
        session.add(ja)
        
        # Seed Schedule Rules
        rule = DrugScheduleRule(
            composition="Amoxicillin + Clavulanic Acid",
            schedule_category="H1",
            requires_prescription=True,
            requires_sales_register=True,
            rule_summary="Schedule H1 drug. Valid prescription required. Maintain register."
        )
        session.add(rule)
        
        # Seed NSQ Alert
        nsq = NSQAlert(
            drug_name="Paracetamol",
            brand_name="Example Para 500",
            manufacturer="Example Pharma Ltd",
            batch_number="PCT2026A",
            test_lab="CDL Kolkata",
            reporting_source="CDSCO",
            month="Jan",
            year=2026,
            failure_reason="Dissolution test failed",
            alert_type="NSQ"
        )
        session.add(nsq)
        
        # Seed Supplier Risk
        supplier = Supplier(
            supplier_name="WhatsApp Meds",
            seller_type="whatsapp_seller",
            verification_status="UNVERIFIED",
            risk_score=9.5,
            risk_reasons_json=["No license", "WhatsApp-based", "No MRP"]
        )
        session.add(supplier)
        
        # Seed Scheme Rule
        scheme = SchemeRule(
            scheme_name="PM-JAY",
            scheme_type="Govt",
            eligibility_summary="Families enrolled in Ayushman Bharat",
            coverage_summary="Rs 5 Lakh per family per year for secondary/tertiary hospitalization",
            applies_to_retail_pharmacy=False,
            applies_to_hospitalization=True
        )
        session.add(scheme)
        
        await session.commit()
        logger.info("Database seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())
