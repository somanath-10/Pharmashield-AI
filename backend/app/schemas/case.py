from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.agent import Citation, Finding
from app.schemas.risk import RiskLevel


class PatientContext(BaseModel):
    age: int | None = None
    diagnoses: list[str] = Field(default_factory=list)
    labs: dict[str, Any] = Field(default_factory=dict)
    previous_therapies: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)


class InventoryContext(BaseModel):
    location_id: str | None = None
    quantity_on_hand: int | None = None
    reorder_threshold: int | None = None
    lot_number: str | None = None


class ProductContext(BaseModel):
    supplier_name: str | None = None
    claim_text: str | None = None
    ndc: str | None = None
    lot_number: str | None = None
    manufacturer: str | None = None


class CaseAnalyzeRequest(BaseModel):
    query: str
    drug_name: str | None = None
    payer_name: str | None = None
    patient_context: PatientContext = Field(default_factory=PatientContext)
    inventory_context: InventoryContext = Field(default_factory=InventoryContext)
    product_context: ProductContext = Field(default_factory=ProductContext)
    denial_letter_text: str | None = None


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
    draft_prescriber_message: str
    draft_patient_message: str
    pharmacist_review_required: bool = True
    memory_notes: list[dict[str, Any]] = Field(default_factory=list)


class CaseRecordResponse(CaseAnalyzeResponse):
    created_at: datetime
    updated_at: datetime


class CaseListItem(BaseModel):
    id: str
    case_type: str
    status: str
    drug_name: str | None = None
    payer_name: str | None = None
    final_risk_level: str | None = None
    created_at: datetime
    updated_at: datetime


class DashboardSummary(BaseModel):
    total_cases: int
    risk_counts: dict[str, int]
    pa_missing_evidence_counts: dict[str, int]
    shortage_cases: int
    supplier_risk_cases: int
    feedback_acceptance_rate: float


class SynthesisInput(BaseModel):
    request: CaseAnalyzeRequest
    intent: str
    detected_intents: list[str]
    agent_outputs: dict[str, dict[str, Any]]
    memory_notes: list[dict[str, Any]] = Field(default_factory=list)
