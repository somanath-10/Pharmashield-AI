from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_pharmacist
from app.models.domain import User, Case, BatchVerification, PrescriptionExtraction, PriceComplianceCheck, SubstitutionCheck, ADRReport, PharmacistReview
from pydantic import BaseModel

router = APIRouter()

class PharmacistDashboardResponse(BaseModel):
    pending_verifications: int
    high_risk_cases: int
    quarantined_batches: int

@router.get("/dashboard", response_model=PharmacistDashboardResponse)
async def get_pharmacist_dashboard(current_user: User = Depends(get_current_pharmacist)) -> Any:
    """Get aggregate metrics for the pharmacist."""
    cases = await Case.find(Case.status == "NEEDS_REVIEW").to_list()
    batches = await BatchVerification.find(BatchVerification.is_quarantined == True).to_list()
    
    return PharmacistDashboardResponse(
        pending_verifications=len(cases),
        high_risk_cases=len([c for c in cases if c.risk_level in ["HIGH", "CRITICAL"]]),
        quarantined_batches=len(batches)
    )

@router.get("/review-queue", response_model=List[Case])
async def get_review_queue(current_user: User = Depends(get_current_pharmacist)) -> Any:
    """List cases pending pharmacist action."""
    return await Case.find(Case.status == "NEEDS_REVIEW").to_list()

class BatchCheckReq(BaseModel):
    case_id: str
    medicine_name: str
    batch_number: str
    expiry_date: str | None = None
    manufacturer: str | None = None
    supplier: str | None = None

@router.post("/batch-check", response_model=BatchVerification)
async def perform_batch_check(req: BatchCheckReq, current_user: User = Depends(get_current_pharmacist)) -> Any:
    """Verify a batch and optionally flag it as quarantined."""
    # Mock behavior: Any batch ending in 'X' is flagged spurious
    is_spurious = req.batch_number.upper().endswith('X')
    
    batch = BatchVerification(
        case_id=req.case_id,
        medicine_name=req.medicine_name,
        batch_number=req.batch_number,
        expiry_date=req.expiry_date,
        manufacturer=req.manufacturer,
        supplier=req.supplier,
        is_quarantined=is_spurious,
        quarantine_reason="NSQ Database Match" if is_spurious else None,
        risk_level="HIGH" if is_spurious else "LOW"
    )
    await batch.insert()
    return batch

class PriceCheckReq(BaseModel):
    case_id: str
    medicine_name: str
    mrp: float
    charged_price: float

@router.post("/price-check", response_model=PriceComplianceCheck)
async def perform_price_check(req: PriceCheckReq, current_user: User = Depends(get_current_pharmacist)) -> Any:
    """Check for overpricing."""
    is_overcharged = req.charged_price > req.mrp
    
    check = PriceComplianceCheck(
        case_id=req.case_id,
        medicine_name=req.medicine_name,
        mrp=req.mrp,
        charged_price=req.charged_price,
        is_overcharged=is_overcharged
    )
    await check.insert()
    return check

class SubstitutionCheckReq(BaseModel):
    case_id: str
    prescribed_medicine: str
    substituted_medicine: str

@router.post("/substitution-check", response_model=SubstitutionCheck)
async def check_substitution(req: SubstitutionCheckReq, current_user: User = Depends(get_current_pharmacist)) -> Any:
    """Check if generic substitution is safe."""
    # Mocking behavior
    is_safe = req.prescribed_medicine.split()[0].lower() == req.substituted_medicine.split()[0].lower()
    
    sub = SubstitutionCheck(
        case_id=req.case_id,
        prescribed_medicine=req.prescribed_medicine,
        substituted_medicine=req.substituted_medicine,
        is_safe=is_safe,
        mismatch_reasons=[] if is_safe else ["Different active molecule suspected"]
    )
    await sub.insert()
    return sub

class ADRDraftReq(BaseModel):
    case_id: str
    patient_age_range: str | None = None
    medicine_name: str
    batch_number: str | None = None
    reaction: str
    severity: str
    timeline: str

@router.post("/adr-draft", response_model=ADRReport)
async def create_adr_draft(req: ADRDraftReq, current_user: User = Depends(get_current_pharmacist)) -> Any:
    """Create an ADR report draft pending doctor review."""
    adr = ADRReport(
        case_id=req.case_id,
        patient_age_range=req.patient_age_range,
        medicine_name=req.medicine_name,
        batch_number=req.batch_number,
        reaction=req.reaction,
        severity=req.severity,
        timeline=req.timeline,
        status="NEEDS_DOCTOR_REVIEW"
    )
    await adr.insert()
    return adr

class ReviewReq(BaseModel):
    case_id: str
    action_taken: str
    notes: str

@router.patch("/reviews/{case_id}", response_model=PharmacistReview)
async def submit_review(case_id: str, req: ReviewReq, current_user: User = Depends(get_current_pharmacist)) -> Any:
    """Submit a formal pharmacist review for a case."""
    case = await Case.find_one(Case.case_id == case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    case.status = "PHARMACIST_REVIEWED"
    await case.save()
    
    review = PharmacistReview(
        case_id=case_id,
        pharmacist_id=current_user.user_id,
        action_taken=req.action_taken,
        notes=req.notes
    )
    await review.insert()
    return review
