from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import MemoryItem, PharmacyCase
from app.schemas.case import CaseAnalyzeRequest
from app.schemas.feedback import FeedbackRequest
from app.services.memory.policy import MemoryPolicy


class MemoryStore:
    def __init__(self) -> None:
        self.policy = MemoryPolicy()

    def get_relevant_memory(self, db: Session, request: CaseAnalyzeRequest) -> list[dict]:
        matches: list[dict] = []
        for scope, key in self.policy.scopes_for_request(request):
            items = (
                db.query(MemoryItem)
                .filter(MemoryItem.scope == scope)
                .filter(MemoryItem.key.ilike(f"%{key}%"))
                .order_by(MemoryItem.confidence.desc())
                .all()
            )
            matches.extend(item.as_dict() for item in items)
        return matches

    def create_feedback_memory(
        self,
        db: Session,
        *,
        case: PharmacyCase,
        feedback: FeedbackRequest,
    ) -> MemoryItem | None:
        if not feedback.correction_text:
            return None
        key = "global"
        scope = "GLOBAL"
        memory_type = "pharmacist_correction"
        value_json = {"correction_text": feedback.correction_text}
        if feedback.agent_name == "coverage_agent" and case.payer_name:
            scope = "PAYER"
            key = f"{case.payer_name}::{case.drug_name or 'unknown'}"
            memory_type = "payer_requirement"
            value_json = {
                "common_missing_docs": self._extract_document_hints(feedback.correction_text),
                "correction_text": feedback.correction_text,
            }
        elif feedback.agent_name == "authenticity_agent":
            scope = "SUPPLIER"
            key = case.case_input_json.get("product_context", {}).get("supplier_name") or "unknown_supplier"
            memory_type = "supplier_risk_note"
        elif feedback.agent_name == "shortage_agent" and case.drug_name:
            scope = "DRUG"
            key = case.drug_name
            memory_type = "substitution_pattern"
        item = MemoryItem(
            memory_type=memory_type,
            scope=scope,
            key=key,
            value_json=value_json,
            confidence=0.8,
        )
        db.add(item)
        return item

    @staticmethod
    def _extract_document_hints(text: str) -> list[str]:
        hints = []
        normalized = text.lower()
        for token in ("bmi", "a1c", "chart notes", "metformin", "lifestyle", "diagnosis"):
            if token in normalized:
                hints.append(token.upper() if token == "a1c" else token)
        return hints or ["Needs pharmacist review"]
