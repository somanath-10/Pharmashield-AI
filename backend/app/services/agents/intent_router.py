from __future__ import annotations

from dataclasses import dataclass, field

from app.schemas.case import CaseAnalyzeRequest

@dataclass
class IntentClassification:
    intent: str
    detected_intents: list[str]
    selected_agents: list[str] = field(default_factory=list)

class IntentRouter:
    async def classify(self, request: CaseAnalyzeRequest) -> IntentClassification:
        query = request.query.lower()
        intents: set[str] = set()

        if any(term in query for term in ["stock not available", "out of stock", "unavailable", "shortage", "not getting", "not in stock"]):
            intents.add("AVAILABILITY")

        if any(term in query for term in ["substitute", "alternative", "same molecule", "same composition", "generic"]):
            intents.add("SUBSTITUTION")

        if any(term in query for term in ["costly", "cheaper", "low price", "mrp", "price", "affordable"]):
            intents.add("PRICE_AFFORDABILITY")

        if any(term in query for term in ["jan aushadhi", "pmbjp", "government generic"]):
            intents.add("JAN_AUSHADHI")

        if any(term in query for term in ["without prescription", "prescription not available", "schedule h", "schedule h1", "schedule x", "dispensing", "rules"]):
            intents.add("PRESCRIPTION_COMPLIANCE")
            intents.add("SCHEDULED_DRUG")

        if any(term in query for term in ["fake", "counterfeit", "spurious", "nsq", "quality fail", "batch", "expiry"]):
            intents.add("NSQ_SPURIOUS")

        if any(term in query for term in ["online seller", "whatsapp", "instagram", "no prescription online", "cheap online", "buy online"]):
            intents.add("ONLINE_SELLER_RISK")

        if any(term in query for term in ["pm-jay", "ayushman", "cghs", "esic", "corporate opd", "reimbursement", "claim", "hospital cashless"]):
            intents.add("SCHEME_CLAIM")
            intents.add("REIMBURSEMENT")

        primary_intents = intents.copy()
        for i in ["SCHEDULED_DRUG", "REIMBURSEMENT"]:
            primary_intents.discard(i)

        if len(primary_intents) > 1:
            top_level = "MULTI_AGENT_CASE"
        elif len(primary_intents) == 1:
            top_level = list(primary_intents)[0]
        else:
            top_level = "GENERAL"

        selected_agents = []
        if "AVAILABILITY" in intents or "SUBSTITUTION" in intents:
            selected_agents.append("availability_agent")
        if "PRICE_AFFORDABILITY" in intents or "JAN_AUSHADHI" in intents:
            selected_agents.append("price_janaushadhi_agent")
        if "PRESCRIPTION_COMPLIANCE" in intents or "SCHEDULED_DRUG" in intents:
            selected_agents.append("prescription_compliance_agent")
        if "NSQ_SPURIOUS" in intents or "RECALL" in intents:
            selected_agents.append("nsq_spurious_agent")
        if "SCHEME_CLAIM" in intents or "REIMBURSEMENT" in intents:
            selected_agents.append("scheme_claim_agent")
        if "ONLINE_SELLER_RISK" in intents:
            selected_agents.append("online_seller_risk_agent")

        if not selected_agents:
            selected_agents.append("synthesis_agent")

        return IntentClassification(
            intent=top_level,
            detected_intents=sorted(list(intents)) if intents else ["GENERAL"],
            selected_agents=selected_agents,
        )
