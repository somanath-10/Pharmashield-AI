from typing import List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.models.domain import Feedback, Case, User
from app.api.deps import get_current_active_user

router = APIRouter(prefix="/api/cases", tags=["feedback"])

class FeedbackSubmitRequest(BaseModel):
    rating: int
    feedback_text: str
    correction_text: str | None = None

class FeedbackResponse(BaseModel):
    feedback_id: str
    status: str

@router.post("/{case_id}/feedback", response_model=FeedbackResponse)
async def submit_feedback(case_id: str, request: FeedbackSubmitRequest, current_user: User = Depends(get_current_active_user)) -> FeedbackResponse:
    target_case = await Case.find_one(Case.case_id == case_id)
    if not target_case:
        raise HTTPException(status_code=404, detail="Case not found")

    feedback = Feedback(
        case_id=case_id,
        user_id=target_case.user_id,
        role=target_case.role.value,
        rating=request.rating,
        feedback_text=request.feedback_text,
        correction_text=request.correction_text,
    )
    await feedback.insert()

    return FeedbackResponse(
        feedback_id=feedback.feedback_id,
        status="SUBMITTED"
    )
