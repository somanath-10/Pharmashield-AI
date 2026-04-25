from typing import Any
from app.services.agents.base import BaseAgent
from app.schemas.case import CaseAnalyzeRequest

class NSQSpuriousAgent(BaseAgent):
    async def run(self, request: CaseAnalyzeRequest, **kwargs: Any) -> dict[str, Any]:
        return {
            "agent_name": "nsq_spurious_agent",
            "risk_level": "HIGH",
            "findings": [
                "No batch number provided.",
                "No manufacturer provided.",
                "Product cannot be checked against NSQ/spurious alerts."
            ],
            "recommended_actions": [
                "Do not recommend product until batch, manufacturer, expiry, and source are verified.",
                "Check CDSCO/state drug alerts.",
                "Use licensed supply chain only."
            ],
            "citations": []
        }
