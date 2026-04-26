"""
Intelligence Routes — direct query endpoints for pharmacy intelligence checks.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.agents.price_agent import PriceJanAushadhiAgent
from app.services.agents.compliance_agent import PrescriptionComplianceAgent
from app.services.agents.nsq_agent import NSQSuriousAgent
from app.services.agents.seller_risk_agent import OnlineSellerRiskAgent
from app.services.agents.scheme_agent import SchemeClaimAgent
from app.services.agents.inventory_agent import InventoryBatchAgent
from app.services.audit import record_audit_log

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])


class PriceCheckRequest(BaseModel):
    drug_name: str
    composition: Optional[str] = None
    mrp: Optional[float] = None
    patient_budget_sensitive: bool = False
    user_id: str = "system"


class NSQCheckRequest(BaseModel):
    drug_name: str
    brand_name: Optional[str] = None
    manufacturer: Optional[str] = None
    batch_number: Optional[str] = None
    composition: Optional[str] = None
    user_id: str = "system"


class ScheduleCheckRequest(BaseModel):
    medicine_name: str
    composition: Optional[str] = None
    prescription_available: bool = True
    claim_text: Optional[str] = None
    user_id: str = "system"


class SchemeCheckRequest(BaseModel):
    scheme_name: Optional[str] = None
    hospitalized: bool = False
    purchase_context: str = "retail_pharmacy"
    user_id: str = "system"


class SellerRiskCheckRequest(BaseModel):
    seller_name: Optional[str] = None
    seller_type: Optional[str] = None
    claim_text: Optional[str] = None
    license_number: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturer: Optional[str] = None
    mrp: Optional[float] = None
    user_id: str = "system"


class InventoryCheckRequest(BaseModel):
    drug_name: str
    quantity_on_hand: Optional[int] = None
    batch_number: Optional[str] = None
    supplier_name: Optional[str] = None
    location_id: Optional[str] = None
    user_id: str = "system"


class JanAushadhiSearchRequest(BaseModel):
    drug_name: str
    composition: Optional[str] = None
    patient_budget_sensitive: bool = True
    user_id: str = "system"


@router.post("/price-check")
async def price_check(req: PriceCheckRequest) -> Dict[str, Any]:
    agent = PriceJanAushadhiAgent()
    result = await agent.run(req.drug_name, req.composition, req.mrp, req.patient_budget_sensitive)
    await record_audit_log(req.user_id, "API", "PRICE_CHECK", "intelligence", metadata={"drug": req.drug_name})
    return result


@router.post("/janaushadhi-search")
async def janaushadhi_search(req: JanAushadhiSearchRequest) -> Dict[str, Any]:
    agent = PriceJanAushadhiAgent()
    result = await agent.run(req.drug_name, req.composition, patient_budget_sensitive=True)
    await record_audit_log(req.user_id, "API", "JANAUSHADHI_SEARCH", "intelligence", metadata={"drug": req.drug_name})
    return result


@router.post("/nsq-check")
async def nsq_check(req: NSQCheckRequest) -> Dict[str, Any]:
    agent = NSQSuriousAgent()
    result = await agent.run(req.drug_name, req.brand_name, req.manufacturer, req.batch_number, req.composition)
    await record_audit_log(req.user_id, "API", "NSQ_CHECK", "intelligence", metadata={"drug": req.drug_name, "batch": req.batch_number})
    return result


@router.post("/schedule-check")
async def schedule_check(req: ScheduleCheckRequest) -> Dict[str, Any]:
    agent = PrescriptionComplianceAgent()
    result = await agent.run(req.medicine_name, req.composition, req.prescription_available, req.claim_text)
    await record_audit_log(req.user_id, "API", "SCHEDULE_CHECK", "intelligence", metadata={"medicine": req.medicine_name})
    return result


@router.post("/scheme-check")
async def scheme_check(req: SchemeCheckRequest) -> Dict[str, Any]:
    agent = SchemeClaimAgent()
    result = await agent.run(req.scheme_name, req.hospitalized, req.purchase_context)
    await record_audit_log(req.user_id, "API", "SCHEME_CHECK", "intelligence")
    return result


@router.post("/seller-risk-check")
async def seller_risk_check(req: SellerRiskCheckRequest) -> Dict[str, Any]:
    agent = OnlineSellerRiskAgent()
    result = await agent.run(req.seller_name, req.seller_type, req.claim_text, req.license_number, req.batch_number, req.manufacturer, req.mrp)
    await record_audit_log(req.user_id, "API", "SELLER_RISK_CHECK", "intelligence", metadata={"seller": req.seller_name})
    return result


@router.post("/inventory-check")
async def inventory_check(req: InventoryCheckRequest) -> Dict[str, Any]:
    agent = InventoryBatchAgent()
    result = await agent.run(req.drug_name, req.quantity_on_hand, req.batch_number, req.supplier_name, req.location_id)
    await record_audit_log(req.user_id, "API", "INVENTORY_CHECK", "intelligence", metadata={"drug": req.drug_name})
    return result
