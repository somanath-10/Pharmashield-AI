from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_patient
from app.models.domain import User, Case, ADRReport, RoleEnum
from pydantic import BaseModel, Field

router = APIRouter()

class ADRReportCreate(BaseModel):
    case_id: str
    medicine_name: str
    batch_number: str | None = None
    reaction: str
    severity: str
    timeline: str
    patient_age_range: str | None = None

class PatientDashboardResponse(BaseModel):
    active_cases: int
    adr_reports: int
    adherence_status: str

@router.get("/dashboard", response_model=PatientDashboardResponse)
async def get_patient_dashboard(current_user: User = Depends(get_current_patient)) -> Any:
    """Get the patient's dashboard metrics."""
    cases = await Case.find(Case.user_id == current_user.user_id).to_list()
    adr_reports = await ADRReport.find(ADRReport.case_id.in_([c.case_id for c in cases])).to_list()
    
    return PatientDashboardResponse(
        active_cases=len([c for c in cases if c.status != "RESOLVED"]),
        adr_reports=len(adr_reports),
        adherence_status="On track"
    )

@router.get("/cases", response_model=List[Case])
async def list_patient_cases(current_user: User = Depends(get_current_patient)) -> Any:
    """Get all cases belonging to the patient."""
    cases = await Case.find(Case.user_id == current_user.user_id).to_list()
    return cases

@router.post("/side-effect-report", response_model=ADRReport)
async def report_side_effect(
    report_in: ADRReportCreate,
    current_user: User = Depends(get_current_patient)
) -> Any:
    """Create a new side effect (ADR) report."""
    case = await Case.find_one(Case.case_id == report_in.case_id, Case.user_id == current_user.user_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found or not owned by user.")
        
    adr = ADRReport(
        case_id=report_in.case_id,
        medicine_name=report_in.medicine_name,
        batch_number=report_in.batch_number,
        reaction=report_in.reaction,
        severity=report_in.severity,
        timeline=report_in.timeline,
        patient_age_range=report_in.patient_age_range,
        status="NEEDS_DOCTOR_REVIEW"
    )
    await adr.insert()
    return adr

@router.get("/affordability/{case_id}")
async def get_affordability(
    case_id: str,
    current_user: User = Depends(get_current_patient)
) -> Any:
    """Retrieve affordability options for medicines in a case."""
    case = await Case.find_one(Case.case_id == case_id, Case.user_id == current_user.user_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    # Mocking generic alternatives for Phase 2 
    return {
        "case_id": case_id,
        "recommendation": "Ask pharmacist for generic equivalent.",
        "alternatives": [
            {"brand": "Jan Aushadhi Generic", "estimated_savings": "70%"},
            {"brand": "Generic A", "estimated_savings": "40%"}
        ]
    }
