from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import Feedback, PharmacyCase
from app.db.session import get_db
from app.schemas.case import (
    CaseAnalyzeRequest,
    CaseAnalyzeResponse,
    CaseListItem,
    CaseRecordResponse,
    DashboardSummary,
)
from app.services.agents.coordinator import AgentCoordinator

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.post("/analyze", response_model=CaseAnalyzeResponse)
async def analyze_case(request: CaseAnalyzeRequest, db: Session = Depends(get_db)) -> CaseAnalyzeResponse:
    coordinator = AgentCoordinator(db)
    return await coordinator.analyze_case(request)


@router.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    cases = db.query(PharmacyCase).all()
    feedback_items = db.query(Feedback).all()
    risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    compliance_issues: dict[str, int] = {}
    shortage_cases = 0
    supplier_risk_cases = 0
    for case in cases:
        if case.final_risk_level in risk_counts:
            risk_counts[case.final_risk_level] += 1
        if case.final_answer:
            payload = json.loads(case.final_answer)
            comp = payload.get("agent_outputs", {}).get("prescription_compliance", {})
            for item in comp.get("findings", []):
                compliance_issues[item] = compliance_issues.get(item, 0) + 1
            if payload.get("agent_outputs", {}).get("availability"):
                shortage_cases += 1
            osr = payload.get("agent_outputs", {}).get("online_seller_risk", {})
            if osr and osr.get("red_flags"):
                supplier_risk_cases += 1
    acceptance_rate = (
        sum(1 for feedback in feedback_items if feedback.rating >= 4) / len(feedback_items)
        if feedback_items
        else 0.0
    )
    return DashboardSummary(
        total_cases=len(cases),
        risk_counts=risk_counts,
        compliance_issues=compliance_issues,
        shortage_cases=shortage_cases,
        supplier_risk_cases=supplier_risk_cases,
        feedback_acceptance_rate=round(acceptance_rate, 2),
    )


@router.get("", response_model=list[CaseListItem])
def list_cases(db: Session = Depends(get_db)) -> list[CaseListItem]:
    cases = db.query(PharmacyCase).order_by(PharmacyCase.created_at.desc()).all()
    return [CaseListItem.model_validate(case.as_dict()) for case in cases]


@router.get("/{case_id}", response_model=CaseRecordResponse)
def get_case(case_id: str, db: Session = Depends(get_db)) -> CaseRecordResponse:
    case = db.query(PharmacyCase).filter(PharmacyCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if not case.final_answer:
        raise HTTPException(status_code=409, detail="Case analysis not completed")
    payload = json.loads(case.final_answer)
    payload["created_at"] = case.created_at
    payload["updated_at"] = case.updated_at
    return CaseRecordResponse.model_validate(payload)
