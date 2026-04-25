from typing import Any
from app.services.agents.base import BaseAgent
from app.schemas.case import CaseAnalyzeRequest

class AvailabilityAgent(BaseAgent):
    async def run(self, request: CaseAnalyzeRequest, **kwargs: Any) -> dict[str, Any]:
        return {
            "agent_name": "availability_agent",
            "risk_level": "MEDIUM",
            "findings": [
                {"title": "Stock Shortage", "detail": "Current stock is zero for the requested medicine at this location."}
            ],
            "recommended_actions": [
                "Check same composition, same strength, same dosage form alternatives.",
                "Confirm substitution policy before dispensing.",
                "Contact doctor if molecule, dose, route, or dosage form changes."
            ],
            "citations": []
        }
