from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_pharmacist
from app.models.domain import (
    User, Case, BatchVerification, PrescriptionExtraction,
    PriceComplianceCheck, SubstitutionCheck, ADRReport,
    PharmacistReview, CaseStatusEnum
)
from app.services.audit import record_audit_log
from pydantic import BaseModel

router = APIRouter()

# ─── Case Validation Helper ────────────────────────────────────────────────────

async def ensure_case_exists(case_id: Optional[str]) -> Optional[Case]:
    """
    Validate that a case exists when a case_id is supplied.
    Pharmacist standalone tools (batch-check, price-check, etc.) may be run
    without a case; if a case_id is provided it MUST exist.
    """
    if not case_id:
        return None
    case = await Case.find_one(Case.case_id == case_id)
    if not case:
        raise HTTPException(
            status_code=404,
            detail=f"Case '{case_id}' not found. "
                   "Please select a case from the review queue or omit case_id for standalone tool mode."
        )
    return case


DISPENSING_STATUSES = {
    "CAN_DISPENSE": "Prescription verified and medicine is safe to dispense.",
    "NEEDS_DOCTOR_CLARIFICATION": "Prescription requires doctor confirmation before dispensing.",
    "NEEDS_PATIENT_CONFIRMATION": "Awaiting patient confirmation (e.g. allergy check, affordability).",
    "QUARANTINE_BATCH": "Batch flagged as suspicious. Do not dispense until verified.",
    "DO_NOT_DISPENSE": "Do not dispense. Prescription is invalid or medicine is unsafe.",
}

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
    case_id: Optional[str] = None
    medicine_name: str
    batch_number: str
    expiry_date: str | None = None
    manufacturer: str | None = None
    supplier: str | None = None

@router.post("/batch-check", response_model=BatchVerification)
async def perform_batch_check(req: BatchCheckReq, current_user: User = Depends(get_current_pharmacist)) -> Any:
    """Verify a batch and optionally flag it as quarantined."""
    await ensure_case_exists(req.case_id)
    # Heuristic: any batch ending in 'X' matches mock NSQ spurious dataset seed
    is_spurious = req.batch_number.upper().endswith('X')
    
    batch = BatchVerification(
        case_id=req.case_id,
        medicine_name=req.medicine_name,
        batch_number=req.batch_number,
        expiry_date=req.expiry_date,
        manufacturer=req.manufacturer,
        supplier=req.supplier,
        is_quarantined=is_spurious,
        quarantine_reason="Flagged in NSQ seed database" if is_spurious else None,
        risk_level="HIGH" if is_spurious else "LOW"
    )
    await batch.insert()
    await record_audit_log(current_user.user_id, "PHARMACIST", "PHARMACIST_BATCH_CHECK", "batch",
                           metadata={"batch_number": req.batch_number, "quarantined": is_spurious})
    return batch

class PriceCheckReq(BaseModel):
    case_id: Optional[str] = None
    medicine_name: str
    mrp: float
    charged_price: float

@router.post("/price-check", response_model=PriceComplianceCheck)
async def perform_price_check(req: PriceCheckReq, current_user: User = Depends(get_current_pharmacist)) -> Any:
    """Check for overpricing against MRP."""
    await ensure_case_exists(req.case_id)
    is_overcharged = req.charged_price > req.mrp
    
    check = PriceComplianceCheck(
        case_id=req.case_id,
        medicine_name=req.medicine_name,
        mrp=req.mrp,
        charged_price=req.charged_price,
        is_overcharged=is_overcharged
    )
    await check.insert()
    await record_audit_log(current_user.user_id, "PHARMACIST", "PHARMACIST_PRICE_CHECK", "price",
                           metadata={"medicine": req.medicine_name, "overcharged": is_overcharged})
    return check

class SubstitutionCheckReq(BaseModel):
    case_id: Optional[str] = None
    prescribed_medicine: str
    substituted_medicine: str

@router.post("/substitution-check", response_model=SubstitutionCheck)
async def check_substitution(req: SubstitutionCheckReq, current_user: User = Depends(get_current_pharmacist)) -> Any:
    """Check if a generic substitution is safe (same molecule comparison)."""
    await ensure_case_exists(req.case_id)
    is_safe = req.prescribed_medicine.split()[0].lower() == req.substituted_medicine.split()[0].lower()
    
    sub = SubstitutionCheck(
        case_id=req.case_id,
        prescribed_medicine=req.prescribed_medicine,
        substituted_medicine=req.substituted_medicine,
        is_safe=is_safe,
        mismatch_reasons=[] if is_safe else ["Different active molecule suspected — consult doctor"]
    )
    await sub.insert()
    await record_audit_log(current_user.user_id, "PHARMACIST", "PHARMACIST_SUBSTITUTION_CHECK", "substitution",
                           metadata={"safe": is_safe})
    return sub

class ADRDraftReq(BaseModel):
    case_id: Optional[str] = None
    patient_age_range: str | None = None
    medicine_name: str
    batch_number: str | None = None
    reaction: str
    severity: str
    timeline: str

@router.post("/adr-draft", response_model=ADRReport)
async def create_adr_draft(req: ADRDraftReq, current_user: User = Depends(get_current_pharmacist)) -> Any:
    """Create an ADR report draft pending doctor review."""
    await ensure_case_exists(req.case_id)
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
    await record_audit_log(current_user.user_id, "PHARMACIST", "CREATE_ADR_REPORT", "adr_report",
                           metadata={"medicine": req.medicine_name, "severity": req.severity})
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
        
    case.status = CaseStatusEnum.PHARMACIST_REVIEWED
    await case.save()
    
    review = PharmacistReview(
        case_id=case_id,
        pharmacist_id=current_user.user_id,
        action_taken=req.action_taken,
        notes=req.notes
    )
    await review.insert()
    await record_audit_log(current_user.user_id, "PHARMACIST", "PHARMACIST_REVIEW_SUBMITTED", "case",
                           case_id=case_id, metadata={"action": req.action_taken})
    return review

# ─── Dispensing Decision ──────────────────────────────────────────────────────

class DispensingDecisionReq(BaseModel):
    case_id: str
    medicine_name: str
    dispensing_status: str  # One of DISPENSING_STATUSES keys
    notes: str | None = None

@router.post("/dispensing-decision")
async def record_dispensing_decision(
    req: DispensingDecisionReq,
    current_user: User = Depends(get_current_pharmacist)
) -> Any:
    """
    Record the final dispensing decision for a case.
    Status must be one of: CAN_DISPENSE | NEEDS_DOCTOR_CLARIFICATION |
    NEEDS_PATIENT_CONFIRMATION | QUARANTINE_BATCH | DO_NOT_DISPENSE
    """
    if req.dispensing_status not in DISPENSING_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {list(DISPENSING_STATUSES.keys())}"
        )

    case = await Case.find_one(Case.case_id == req.case_id)
    if case:
        # Update case status based on dispensing decision
        if req.dispensing_status == "CAN_DISPENSE":
            case.status = CaseStatusEnum.RESOLVED
        elif req.dispensing_status == "DO_NOT_DISPENSE":
            case.status = CaseStatusEnum.ESCALATED
        elif req.dispensing_status in ("NEEDS_DOCTOR_CLARIFICATION", "QUARANTINE_BATCH"):
            case.status = CaseStatusEnum.NEEDS_REVIEW
        else:
            case.status = CaseStatusEnum.PHARMACIST_REVIEWED
        await case.save()

    # Record as a PharmacistReview
    review = PharmacistReview(
        case_id=req.case_id,
        pharmacist_id=current_user.user_id,
        action_taken=req.dispensing_status,
        notes=req.notes or DISPENSING_STATUSES[req.dispensing_status],
    )
    await review.insert()
    await record_audit_log(
        current_user.user_id, "PHARMACIST", "PHARMACIST_DISPENSING_DECISION", "dispensing",
        case_id=req.case_id,
        metadata={"status": req.dispensing_status, "medicine": req.medicine_name}
    )

    return {
        "status": req.dispensing_status,
        "description": DISPENSING_STATUSES[req.dispensing_status],
        "medicine": req.medicine_name,
        "case_id": req.case_id,
    }

@router.get("/dispensing-statuses")
async def get_dispensing_statuses(current_user: User = Depends(get_current_pharmacist)):
    """Return all valid dispensing decision statuses and their descriptions."""
    return [{"status": k, "description": v} for k, v in DISPENSING_STATUSES.items()]

