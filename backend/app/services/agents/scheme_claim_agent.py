from typing import Any
from app.services.agents.base import BaseAgent
from app.schemas.case import CaseAnalyzeRequest

class SchemeClaimAgent(BaseAgent):
    async def run(self, request: CaseAnalyzeRequest, **kwargs: Any) -> dict[str, Any]:
        return {
            "agent_name": "scheme_claim_agent",
            "risk_level": "LOW",
            "findings": [
                {"title": "Retail Limitation", "detail": "Most government schemes like PM-JAY cover medications primarily during hospitalization, not at retail counters."},
                {"title": "Verification Needed", "detail": "Corporate OPD or specialized reimbursement schemes (CGHS/ESIC) require additional documentation for retail claims."}
            ],
            "required_documents": [
                "Doctor prescription",
                "Tax invoice",
                "Diagnosis proof if required",
                "Hospital documents if claim is hospital-based"
            ],
            "recommended_actions": [
                "Ask patient whether this is PM-JAY, CGHS, ESIC, corporate OPD, or reimbursement claim.",
                "Provide proper invoice and prescription copy support."
            ],
            "citations": []
        }
