from __future__ import annotations

from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    case_id: str
    agent_name: str
    rating: int
    feedback_text: str | None = None
    correction_text: str | None = None
    user_role: str = "pharmacist"


class FeedbackResponse(BaseModel):
    status: str
    feedback_id: str
