from typing import List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_doctor
from app.models.domain import User, Case, ADRReport, DoctorReview, DoctorPharmacistMessage
from pydantic import BaseModel
import uuid

router = APIRouter()

class DoctorDashboardResponse(BaseModel):
    adr_reviews_pending: int
    pharmacist_questions: int
    active_patients: int

@router.get("/dashboard", response_model=DoctorDashboardResponse)
async def get_doctor_dashboard(current_user: User = Depends(get_current_doctor)) -> Any:
    """Get aggregate metrics for the doctor."""
    adrs = await ADRReport.find(ADRReport.status == "NEEDS_DOCTOR_REVIEW").to_list()
    # Mock active patients
    return DoctorDashboardResponse(
        adr_reviews_pending=len(adrs),
        pharmacist_questions=0,
        active_patients=12
    )

@router.get("/patients", response_model=List[Dict[str, Any]])
async def get_patients(current_user: User = Depends(get_current_doctor)) -> Any:
    """Get a list of patient clinical summaries."""
    # Since we don't have a formal patient mapping directly to doctors in the MVP, 
    # we'll return mock structured patient summaries.
    return [
        {
            "patient_id": "P-001",
            "name": "Arun Kumar",
            "age": 45,
            "current_medicines": ["Metformin 500mg", "Atorvastatin 10mg"],
            "recent_flags": ["Possible mild ADR reported"]
        },
        {
            "patient_id": "P-002",
            "name": "Priya Singh",
            "age": 32,
            "current_medicines": ["Thyroxine 50mcg"],
            "recent_flags": []
        }
    ]

@router.get("/adr-reviews", response_model=List[ADRReport])
async def get_adr_reviews(current_user: User = Depends(get_current_doctor)) -> Any:
    """Get pending ADR reports needing doctor review."""
    return await ADRReport.find(ADRReport.status == "NEEDS_DOCTOR_REVIEW").to_list()

class ADRActionReq(BaseModel):
    action: str # e.g., 'CONFIRMED_ADR', 'DISMISSED'
    notes: str

@router.patch("/adr-review/{adr_id}")
async def review_adr(adr_id: str, req: ADRActionReq, current_user: User = Depends(get_current_doctor)) -> Any:
    """Review and update an ADR report status."""
    adr = await ADRReport.find_one(ADRReport.adr_id == adr_id)
    if not adr:
        raise HTTPException(status_code=404, detail="ADR Report not found")
        
    adr.status = "REVIEWED"
    await adr.save()
    
    review = DoctorReview(
        case_id=adr.case_id,
        doctor_id=current_user.user_id,
        action_taken=f"ADR_{req.action}",
        notes=req.notes
    )
    await review.insert()
    return adr

class EPrescriptionReq(BaseModel):
    patient_name: str
    medicines: List[str]
    notes: str

@router.post("/prescription-verification")
async def generate_eprescription(req: EPrescriptionReq, current_user: User = Depends(get_current_doctor)) -> Any:
    """Generate a verified e-prescription scaffold to prevent misuse."""
    verification_id = f"RX-VERIFY-{str(uuid.uuid4())[:8].upper()}"
    return {
        "verification_id": verification_id,
        "doctor_name": current_user.name,
        "patient": req.patient_name,
        "medicines": req.medicines,
        "status": "VERIFIED_ACTIVE"
    }
