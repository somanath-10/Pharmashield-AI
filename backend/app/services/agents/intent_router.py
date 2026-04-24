from __future__ import annotations

from dataclasses import dataclass, field

from app.core.constants import AUTHENTICITY_TERMS, PA_TERMS, RECALL_TERMS, SHORTAGE_TERMS
from app.schemas.case import CaseAnalyzeRequest
from app.schemas.risk import IntentLabel


@dataclass
class IntentClassification:
    intent: str
    detected_intents: list[str]
    selected_agents: list[str] = field(default_factory=list)


class IntentRouter:
    async def classify(self, request: CaseAnalyzeRequest) -> IntentClassification:
        query = request.query.lower()
        intents: set[str] = set()

        if any(term in query for term in SHORTAGE_TERMS):
            intents.update({IntentLabel.SHORTAGE.value, IntentLabel.SUBSTITUTION.value})
        if any(term in query for term in RECALL_TERMS):
            intents.add(IntentLabel.RECALL.value)
        if any(term in query for term in PA_TERMS):
            intents.update(
                {
                    IntentLabel.PRIOR_AUTHORIZATION.value,
                    IntentLabel.DENIAL_APPEAL.value,
                    IntentLabel.FORMULARY_ACCESS.value,
                }
            )
        suspicious_text = " ".join(
            filter(
                None,
                [
                    request.product_context.supplier_name,
                    request.product_context.claim_text,
                    request.query,
                ],
            )
        ).lower()
        if any(term in suspicious_text for term in AUTHENTICITY_TERMS):
            intents.update(
                {
                    IntentLabel.AUTHENTICITY.value,
                    IntentLabel.COMPOUNDING_COMPLIANCE.value,
                    IntentLabel.PATIENT_COUNSELING.value,
                }
            )

        core_intents = {
            IntentLabel.SHORTAGE.value,
            IntentLabel.RECALL.value,
            IntentLabel.PRIOR_AUTHORIZATION.value,
            IntentLabel.AUTHENTICITY.value,
            IntentLabel.COMPOUNDING_COMPLIANCE.value,
        }
        matched_core = [intent for intent in intents if intent in core_intents]
        if len(matched_core) > 1:
            top_level = IntentLabel.MULTI_AGENT_CASE.value
        elif matched_core:
            top_level = matched_core[0]
        else:
            top_level = IntentLabel.GENERAL.value

        selected_agents = []
        if any(intent in intents for intent in {IntentLabel.SHORTAGE.value, IntentLabel.RECALL.value, IntentLabel.SUBSTITUTION.value}):
            selected_agents.append("shortage_agent")
        if any(intent in intents for intent in {IntentLabel.PRIOR_AUTHORIZATION.value, IntentLabel.DENIAL_APPEAL.value, IntentLabel.FORMULARY_ACCESS.value}):
            selected_agents.append("coverage_agent")
        if any(intent in intents for intent in {IntentLabel.AUTHENTICITY.value, IntentLabel.COMPOUNDING_COMPLIANCE.value, IntentLabel.PATIENT_COUNSELING.value}):
            selected_agents.append("authenticity_agent")

        if not selected_agents:
            selected_agents.append("synthesis_agent")

        return IntentClassification(
            intent=top_level,
            detected_intents=sorted(intents) if intents else [IntentLabel.GENERAL.value],
            selected_agents=selected_agents,
        )
