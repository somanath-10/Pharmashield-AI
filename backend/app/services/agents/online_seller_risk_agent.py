from typing import Any
from app.services.agents.base import BaseAgent
from app.schemas.case import CaseAnalyzeRequest

class OnlineSellerRiskAgent(BaseAgent):
    async def run(self, request: CaseAnalyzeRequest, **kwargs: Any) -> dict[str, Any]:
        return {
            "agent_name": "online_seller_risk_agent",
            "risk_level": "HIGH",
            "findings": [
                {"title": "Unverified Source", "detail": "Online sellers without a valid physical address or license are considered high-risk."},
                {"title": "Missing Prescription", "detail": "Any claim of 'no prescription needed' for Schedule H/X drugs is a legal red flag."}
            ],
            "recommended_actions": [
                "Do not recommend unverified online seller.",
                "Advise patient to buy only from licensed pharmacy.",
                "Verify license, batch, manufacturer, expiry, and invoice before considering product."
            ],
            "citations": []
        }
