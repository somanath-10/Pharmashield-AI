"""
Ingest Routes — POST endpoints to load India pharmacy intelligence data.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.postgres import async_session_maker
from app.models.postgres_models import NSQAlert, PriceRecord, JanAushadhiProduct, DrugScheduleRule, SchemeRule, InventoryItem, Supplier

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ingest", tags=["ingest"])


class NSQAlertIn(BaseModel):
    drug_name: str
    brand_name: Optional[str] = None
    composition: Optional[str] = None
    manufacturer: Optional[str] = None
    batch_number: Optional[str] = None
    test_lab: Optional[str] = None
    reporting_source: Optional[str] = None
    month: Optional[str] = None
    year: Optional[int] = None
    failure_reason: Optional[str] = None
    alert_type: str = "NSQ"
    source: str = "CDSCO"
    source_url: Optional[str] = None


class PriceRecordIn(BaseModel):
    brand_name: str
    generic_name: str
    composition: str
    strength: Optional[str] = None
    dosage_form: Optional[str] = None
    pack_size: Optional[str] = None
    mrp: float
    ceiling_price: Optional[float] = None
    source: str = "NPPA"


class JanAushadhiIn(BaseModel):
    generic_name: str
    composition: str
    strength: Optional[str] = None
    dosage_form: Optional[str] = None
    pack_size: Optional[str] = None
    janaushadhi_price: float
    availability_status: str = "AVAILABLE"
    source: str = "PMBJP"


class ScheduleRuleIn(BaseModel):
    drug_name: Optional[str] = None
    composition: str
    schedule_category: str
    requires_prescription: bool = True
    requires_sales_register: bool = False
    requires_special_storage: bool = False
    rule_summary: str
    source: str = "CDSCO"


class SchemeRuleIn(BaseModel):
    scheme_name: str
    scheme_type: str
    eligibility_summary: str
    coverage_summary: str
    applies_to_retail_pharmacy: bool = False
    applies_to_hospitalization: bool = True
    source: str = "MoHFW"


class SupplierIn(BaseModel):
    supplier_name: str
    seller_type: str
    license_number: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    verification_status: str = "UNVERIFIED"
    risk_score: float = 0.0
    risk_reasons: List[str] = []


@router.post("/cdsco-nsq")
async def ingest_nsq_alert(data: NSQAlertIn) -> Dict[str, Any]:
    async with async_session_maker() as session:
        alert = NSQAlert(**data.model_dump(exclude={"risk_reasons"}))
        session.add(alert)
        await session.commit()
        return {"status": "ingested", "id": alert.id}


@router.post("/nppa-prices")
async def ingest_price_record(data: PriceRecordIn) -> Dict[str, Any]:
    async with async_session_maker() as session:
        record = PriceRecord(**data.model_dump())
        session.add(record)
        await session.commit()
        return {"status": "ingested", "id": record.id}


@router.post("/janaushadhi-products")
async def ingest_jan_aushadhi(data: JanAushadhiIn) -> Dict[str, Any]:
    async with async_session_maker() as session:
        product = JanAushadhiProduct(**data.model_dump())
        session.add(product)
        await session.commit()
        return {"status": "ingested", "id": product.id}


@router.post("/schedule-rules")
async def ingest_schedule_rule(data: ScheduleRuleIn) -> Dict[str, Any]:
    async with async_session_maker() as session:
        rule = DrugScheduleRule(**data.model_dump())
        session.add(rule)
        await session.commit()
        return {"status": "ingested", "id": rule.id}


@router.post("/scheme-rules")
async def ingest_scheme_rule(data: SchemeRuleIn) -> Dict[str, Any]:
    async with async_session_maker() as session:
        rule = SchemeRule(**data.model_dump())
        session.add(rule)
        await session.commit()
        return {"status": "ingested", "id": rule.id}


@router.post("/suppliers")
async def ingest_supplier(data: SupplierIn) -> Dict[str, Any]:
    async with async_session_maker() as session:
        supplier = Supplier(
            supplier_name=data.supplier_name,
            seller_type=data.seller_type,
            license_number=data.license_number,
            state=data.state,
            address=data.address,
            verification_status=data.verification_status,
            risk_score=data.risk_score,
            risk_reasons_json=data.risk_reasons,
        )
        session.add(supplier)
        await session.commit()
        return {"status": "ingested", "id": supplier.id}
