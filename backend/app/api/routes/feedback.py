from typing import List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.models.domain import Feedback, Case, User, RoleEnum
from app.api.deps import get_current_active_user
from app.services.audit import record_audit_log

router = APIRouter(prefix="/api/cases", tags=["feedback"])

class FeedbackSubmitRequest(BaseModel):
    rating: int
    feedback_text: str
    correction_text: str | None = None

class FeedbackResponse(BaseModel):
    feedback_id: str
    status: str

@router.post("/{case_id}/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    case_id: str,
    request: FeedbackSubmitRequest,
    current_user: User = Depends(get_current_active_user),
) -> FeedbackResponse:
    target_case = await Case.find_one(Case.case_id == case_id)
    if not target_case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Ownership check: only the case owner or an admin may submit feedback
    if target_case.user_id != current_user.user_id and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to submit feedback for this case")

    if not (1 <= request.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    feedback = Feedback(
        case_id=case_id,
        user_id=current_user.user_id,       # ← real submitter, not case owner
        role=current_user.role.value,        # ← real submitter role
        rating=request.rating,
        feedback_text=request.feedback_text,
        correction_text=request.correction_text,
    )
    await feedback.insert()
    await record_audit_log(
        current_user.user_id, current_user.role.value, "SUBMIT_FEEDBACK", "case",
        case_id=case_id, metadata={"rating": request.rating}
    )

    return FeedbackResponse(feedback_id=feedback.feedback_id, status="SUBMITTED")
