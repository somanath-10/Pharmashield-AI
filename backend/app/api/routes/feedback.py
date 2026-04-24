from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import Feedback, PharmacyCase
from app.db.session import get_db
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services.memory.store import MemoryStore

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)) -> FeedbackResponse:
    case = db.query(PharmacyCase).filter(PharmacyCase.id == request.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    feedback = Feedback(
        case_id=request.case_id,
        agent_name=request.agent_name,
        user_role=request.user_role,
        rating=request.rating,
        feedback_text=request.feedback_text,
        correction_text=request.correction_text,
    )
    db.add(feedback)
    MemoryStore().create_feedback_memory(db, case=case, feedback=request)
    db.commit()
    db.refresh(feedback)
    return FeedbackResponse(status="ok", feedback_id=feedback.id)
