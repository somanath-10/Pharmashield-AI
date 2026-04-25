from typing import Any
from app.services.agents.base import BaseAgent
from app.schemas.case import CaseAnalyzeRequest

class OnlineSellerRiskAgent(BaseAgent):
    async def run(self, request: CaseAnalyzeRequest, **kwargs: Any) -> dict[str, Any]:
        return {
            "agent_name": "online_seller_risk_agent",
            "risk_level": "HIGH",
            "red_flags": [
                "Claim says no prescription needed.",
                "No license number provided.",
                "No batch number provided.",
                "No manufacturer provided."
            ],
            "recommended_actions": [
                "Do not recommend unverified online seller.",
                "Advise patient to buy only from licensed pharmacy.",
                "Verify license, batch, manufacturer, expiry, and invoice before considering product."
            ],
            "citations": []
        }
