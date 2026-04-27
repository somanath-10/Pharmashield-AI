from typing import List, Any, Dict, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_doctor
from app.models.domain import (
    User, Case, ADRReport, DoctorReview,
    DoctorPharmacistMessage, VerifiedPrescription, CareTeamLink
)
from app.services.audit import record_audit_log
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
    msgs = await DoctorPharmacistMessage.find(
        DoctorPharmacistMessage.receiver_id == current_user.user_id
    ).to_list()
    # Count cases where doctor has reviewed or that belong to doctor
    doctor_cases = await Case.find(Case.role == "DOCTOR").to_list()
    return DoctorDashboardResponse(
        adr_reviews_pending=len(adrs),
        pharmacist_questions=len(msgs),
        active_patients=len(set(c.user_id for c in doctor_cases))
    )

@router.get("/patients", response_model=List[Dict[str, Any]])
async def get_patients(current_user: User = Depends(get_current_doctor)) -> Any:
    """
    Get patient summaries for patients that have an ACTIVE CareTeamLink with this doctor.
    Falls back to all PATIENT cases when no links exist (dev/demo convenience).
    """
    # Check for consent-based links
    links = await CareTeamLink.find(
        {"doctor_id": current_user.user_id, "status": "ACTIVE"}
    ).to_list()

    if links:
        patient_ids = [l.patient_id for l in links]
        patient_cases = await Case.find({"user_id": {"$in": patient_ids}, "role": "PATIENT"}).to_list()
    else:
        # Demo/development fallback: show all patient cases
        patient_cases = await Case.find({"role": "PATIENT"}).to_list()

    if not patient_cases:
        return []

    patient_map: Dict[str, Dict[str, Any]] = {}
    for case in patient_cases:
        uid = case.user_id
        if uid not in patient_map:
            patient_map[uid] = {
                "patient_id": uid,
                "name": "Patient",
                "age": "—",
                "current_medicines": [],
                "cases": [],
                "recent_flags": [],
            }
        patient_map[uid]["cases"].append({
            "case_id": case.case_id,
            "title": case.title,
            "risk_level": case.risk_level,
            "status": case.status.value if hasattr(case.status, "value") else case.status,
        })
        if case.risk_level in ("HIGH", "CRITICAL"):
            patient_map[uid]["recent_flags"].append(f"High-risk case: {case.title}")

    return list(patient_map.values())

@router.get("/adr-reviews", response_model=List[ADRReport])
async def get_adr_reviews(current_user: User = Depends(get_current_doctor)) -> Any:
    """Get pending ADR reports needing doctor review."""
    return await ADRReport.find(ADRReport.status == "NEEDS_DOCTOR_REVIEW").to_list()

class ADRActionReq(BaseModel):
    action: str  # e.g., 'CONFIRMED_ADR', 'POSSIBLE_ADR', 'DISMISSED', 'URGENT_CARE'
    notes: str

@router.patch("/adr-review/{adr_id}")
async def review_adr(adr_id: str, req: ADRActionReq, current_user: User = Depends(get_current_doctor)) -> Any:
    """Review and update an ADR report status."""
    adr = await ADRReport.find_one(ADRReport.adr_id == adr_id)
    if not adr:
        raise HTTPException(status_code=404, detail="ADR Report not found")

    valid_actions = {"CONFIRMED_ADR", "POSSIBLE_ADR", "DISMISSED", "URGENT_CARE"}
    if req.action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of: {valid_actions}")

    adr.status = "REVIEWED"
    await adr.save()

    review = DoctorReview(
        case_id=adr.case_id,
        doctor_id=current_user.user_id,
        action_taken=f"ADR_{req.action}",
        notes=req.notes
    )
    await review.insert()
    await record_audit_log(current_user.user_id, "DOCTOR", "DOCTOR_ADR_REVIEW", "adr_report",
                           metadata={"adr_id": adr_id, "action": req.action})
    return adr

class EPrescriptionReq(BaseModel):
    patient_name: str
    patient_id: Optional[str] = None
    medicines: List[str]
    notes: str

@router.post("/prescription-verification")
async def generate_eprescription(req: EPrescriptionReq, current_user: User = Depends(get_current_doctor)) -> Any:
    """Generate and persist a verified e-prescription to prevent misuse."""
    from datetime import timedelta
    vp = VerifiedPrescription(
        doctor_id=current_user.user_id,
        patient_name=req.patient_name,
        patient_id=req.patient_id,
        medicine_list=req.medicines,
        notes=req.notes,
        status="ACTIVE",
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
    )
    await vp.insert()
    await record_audit_log(current_user.user_id, "DOCTOR", "DOCTOR_PRESCRIPTION_VERIFIED", "verified_prescription",
                           metadata={"verification_id": vp.verification_id, "patient": req.patient_name})
    return {
        "verification_id": vp.verification_id,
        "doctor_name": current_user.name,
        "patient": vp.patient_name,
        "medicines": vp.medicine_list,
        "status": vp.status,
        "expires_at": vp.expires_at.isoformat() if vp.expires_at else None,
    }

# ─── Doctor-Pharmacist Messaging ─────────────────────────────────────────────

class MessageReplyReq(BaseModel):
    message: str

@router.get("/messages", response_model=List[DoctorPharmacistMessage])
async def get_messages(current_user: User = Depends(get_current_doctor)) -> Any:
    """Get pharmacist questions addressed to this doctor."""
    return await DoctorPharmacistMessage.find(
        DoctorPharmacistMessage.receiver_id == current_user.user_id
    ).to_list()

@router.post("/messages/{message_id}/reply")
async def reply_to_message(
    message_id: str,
    req: MessageReplyReq,
    current_user: User = Depends(get_current_doctor)
) -> Any:
    """Reply to a pharmacist question."""
    original = await DoctorPharmacistMessage.find_one(
        DoctorPharmacistMessage.message_id == message_id
    )
    if not original:
        raise HTTPException(status_code=404, detail="Message not found")

    reply = DoctorPharmacistMessage(
        case_id=original.case_id,
        sender_id=current_user.user_id,
        sender_role="DOCTOR",
        receiver_id=original.sender_id,
        message=req.message,
    )
    await reply.insert()
    await record_audit_log(current_user.user_id, "DOCTOR", "DOCTOR_PHARMACIST_REPLY", "message",
                           metadata={"original_message_id": message_id})
    return {"status": "sent", "reply_id": reply.message_id}

# ─── Substitution Decision ────────────────────────────────────────────────────

class SubstitutionDecisionReq(BaseModel):
    case_id: str
    prescribed_medicine: str
    proposed_substitution: str
    decision: str  # APPROVED | REJECTED | NEEDS_MONITORING
    reason: str

@router.post("/substitution-decision")
async def substitution_decision(
    req: SubstitutionDecisionReq,
    current_user: User = Depends(get_current_doctor)
) -> Any:
    """Doctor approves or rejects a pharmacist-proposed substitution."""
    valid_decisions = {"APPROVED", "REJECTED", "NEEDS_MONITORING"}
    if req.decision not in valid_decisions:
        raise HTTPException(status_code=400, detail=f"Decision must be one of: {valid_decisions}")

    review = DoctorReview(
        case_id=req.case_id,
        doctor_id=current_user.user_id,
        action_taken=f"SUBSTITUTION_{req.decision}",
        notes=f"Prescribed: {req.prescribed_medicine} → Proposed: {req.proposed_substitution}. Reason: {req.reason}",
    )
    await review.insert()
    await record_audit_log(current_user.user_id, "DOCTOR", "DOCTOR_SUBSTITUTION_DECISION", "substitution",
                           metadata={"case_id": req.case_id, "decision": req.decision})
    return {
        "status": "recorded",
        "decision": req.decision,
        "prescribed": req.prescribed_medicine,
        "proposed": req.proposed_substitution,
        "reason": req.reason,
    }

# ─── Care Team Links (Doctor-Patient Consent) ─────────────────────────────────

class CareTeamLinkReq(BaseModel):
    patient_id: str

@router.post("/care-team-links")
async def create_care_team_link(
    req: CareTeamLinkReq,
    current_user: User = Depends(get_current_doctor)
) -> Any:
    """Link a patient to this doctor (requires patient consent in full flow)."""
    existing = await CareTeamLink.find_one(
        {"doctor_id": current_user.user_id, "patient_id": req.patient_id, "status": "ACTIVE"}
    )
    if existing:
        return {"link_id": existing.link_id, "status": "ALREADY_LINKED"}

    link = CareTeamLink(
        patient_id=req.patient_id,
        doctor_id=current_user.user_id,
        status="ACTIVE",
        consent_given_at=datetime.now(timezone.utc),
    )
    await link.insert()
    await record_audit_log(current_user.user_id, "DOCTOR", "CARE_TEAM_LINK_CREATED", "care_team",
                           metadata={"patient_id": req.patient_id})
    return {"link_id": link.link_id, "status": "ACTIVE"}

@router.get("/care-team-links")
async def get_care_team_links(current_user: User = Depends(get_current_doctor)) -> Any:
    """List all patients linked to this doctor."""
    links = await CareTeamLink.find(
        {"doctor_id": current_user.user_id, "status": "ACTIVE"}
    ).to_list()
    return [{"link_id": l.link_id, "patient_id": l.patient_id, "status": l.status} for l in links]

@router.delete("/care-team-links/{patient_id}")
async def revoke_care_team_link(
    patient_id: str,
    current_user: User = Depends(get_current_doctor)
) -> Any:
    """Revoke a doctor-patient link."""
    link = await CareTeamLink.find_one(
        {"doctor_id": current_user.user_id, "patient_id": patient_id, "status": "ACTIVE"}
    )
    if not link:
        raise HTTPException(status_code=404, detail="Care team link not found")
    link.status = "REVOKED"
    link.updated_at = datetime.now(timezone.utc)
    await link.save()
    await record_audit_log(current_user.user_id, "DOCTOR", "CARE_TEAM_LINK_REVOKED", "care_team",
                           metadata={"patient_id": patient_id})
    return {"status": "REVOKED"}
