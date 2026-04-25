from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.agent import Citation, Finding
from app.schemas.risk import RiskLevel


class PrescriptionContext(BaseModel):
    prescription_available: bool = False
    doctor_name: str | None = None
    prescription_date: str | None = None


class InventoryContext(BaseModel):
    quantity_on_hand: int | None = None
    same_molecule_available: bool = False
    location_id: str | None = None


class SchemeContext(BaseModel):
    pmjay_eligible: bool | None = None
    hospitalized: bool | None = None
    corporate_opd: bool | None = None


class PatientContext(BaseModel):
    condition: str | None = None
    budget_sensitive: bool = False
    scheme_context: SchemeContext = Field(default_factory=SchemeContext)


class ProductContext(BaseModel):
    seller_type: str | None = None
    seller_name: str | None = None
    claim_text: str | None = None
    batch_number: str | None = None
    manufacturer: str | None = None
    license_number: str | None = None
    mrp: float | None = None
    expiry_date: str | None = None


class CaseAnalyzeRequest(BaseModel):
    query: str
    drug_name: str | None = None
    brand_name: str | None = None
    location_state: str | None = None
    prescription_context: PrescriptionContext = Field(default_factory=PrescriptionContext)
    inventory_context: InventoryContext = Field(default_factory=InventoryContext)
    patient_context: PatientContext = Field(default_factory=PatientContext)
    product_context: ProductContext = Field(default_factory=ProductContext)


class AgentTraceItem(BaseModel):
    agent_name: str
    status: str
    risk_level: RiskLevel
    findings: list[Finding] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class CaseAnalyzeResponse(BaseModel):
    case_id: str
    risk_level: RiskLevel
    intent: str
    detected_intents: list[str] = Field(default_factory=list)
    summary: str
    action_plan: list[str] = Field(default_factory=list)
    agent_outputs: dict[str, dict[str, Any]] = Field(default_factory=dict)
    agent_trace: list[AgentTraceItem] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    draft_prescriber_message: str | None = None
    draft_patient_message: str | None = None
    pharmacist_review_required: bool = True
    mandatory_disclaimer: str = "Pharmacist review required before clinical, dispensing, substitution, or patient-specific action."
    memory_notes: list[dict[str, Any]] = Field(default_factory=list)


class CaseRecordResponse(CaseAnalyzeResponse):
    created_at: datetime
    updated_at: datetime


class CaseListItem(BaseModel):
    id: str
    case_type: str
    status: str
    drug_name: str | None = None
    brand_name: str | None = None
    location_state: str | None = None
    final_risk_level: str | None = None
    created_at: datetime
    updated_at: datetime


class DashboardSummary(BaseModel):
    total_cases: int
    risk_counts: dict[str, int]
    compliance_issues: dict[str, int]
    shortage_cases: int
    supplier_risk_cases: int
    feedback_acceptance_rate: float


class SynthesisInput(BaseModel):
    request: CaseAnalyzeRequest
    intent: str
    detected_intents: list[str]
    agent_outputs: dict[str, dict[str, Any]]
    memory_notes: list[dict[str, Any]] = Field(default_factory=list)
