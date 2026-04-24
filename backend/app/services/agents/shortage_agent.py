from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.constants import drug_aliases
from app.db.models import RecallEvent, ShortageEvent
from app.schemas.agent import Citation, Finding
from app.schemas.case import CaseAnalyzeRequest
from app.schemas.risk import RiskLevel
from app.services.agents.base import BaseAgent
from app.services.data_connectors.openfda_shortages import OpenFDAShortagesConnector


class ShortageAgent(BaseAgent):
    def __init__(self, db: Session) -> None:
        super().__init__(db)
        self.settings = get_settings()
        self.connector = OpenFDAShortagesConnector()

    async def run(self, request: CaseAnalyzeRequest, **kwargs: Any) -> dict[str, Any]:
        aliases = drug_aliases(request.drug_name)
        findings: list[Finding] = []
        recommended_actions: list[str] = []
        citations: list[Citation] = []
        local_shortages = self._matching_shortages(aliases)
        local_recalls = self._matching_recalls(aliases)

        case_citation = Citation(
            id="case-data::inventory",
            source_name="Provided case data",
            source_url=None,
            document_title="Case input",
            section_title="inventory_context",
            snippet=f"Quantity on hand: {request.inventory_context.quantity_on_hand}",
            source_type="case_data",
            note="Based on provided case data",
        )
        citations.append(case_citation)

        qoh = request.inventory_context.quantity_on_hand
        if qoh is not None and qoh <= 0:
            findings.append(
                Finding(
                    title="Inventory unavailable",
                    detail="Current quantity is 0 for requested product.",
                    evidence_ids=[case_citation.id],
                )
            )
            recommended_actions.extend(
                [
                    "Check therapeutically appropriate alternatives.",
                    "Contact prescriber before changing drug, dose, or formulation.",
                    "Add patient to shortage follow-up list.",
                ]
            )

        for event in local_shortages:
            citation = Citation(
                id=f"shortage::{event.id}",
                source_name=event.source,
                source_url=event.source_url,
                document_title=event.drug_name,
                section_title="shortage_status",
                snippet=event.reason or event.status or "Shortage event found.",
                source_type="shortage",
            )
            citations.append(citation)
            findings.append(
                Finding(
                    title=f"Shortage signal for {event.drug_name}",
                    detail=f"{event.status or 'Current or reported'} shortage noted. {event.reason or ''}".strip(),
                    evidence_ids=[citation.id],
                )
            )

        live_results = []
        if self.settings.enable_live_public_apis and request.drug_name:
            try:
                live_results = await self.connector.search(drug_name=request.drug_name, limit=3)
            except Exception:
                live_results = []
        for payload in live_results:
            snippet = payload.get("reason") or payload.get("status") or "openFDA shortage signal."
            citation = Citation(
                id=f"openfda-shortage::{payload.get('drug_name', 'unknown')}",
                source_name="openFDA",
                source_url=payload.get("source_url"),
                document_title=payload.get("drug_name"),
                section_title="shortage_status",
                snippet=snippet[:280],
                source_type="shortage",
            )
            citations.append(citation)

        recall_risk = RiskLevel.LOW
        for recall in local_recalls:
            if request.product_context.lot_number and recall.code_info and request.product_context.lot_number.lower() in recall.code_info.lower():
                recall_risk = RiskLevel.CRITICAL
            citation = Citation(
                id=f"recall::{recall.id}",
                source_name=recall.source,
                source_url=recall.source_url,
                document_title=recall.drug_name,
                section_title="recall",
                snippet=(recall.reason_for_recall or recall.product_description or "Recall matched")[:280],
                source_type="recall",
            )
            citations.append(citation)
            findings.append(
                Finding(
                    title=f"Recall history found for {recall.drug_name}",
                    detail=(recall.reason_for_recall or "Recall data available. Needs pharmacist review."),
                    evidence_ids=[citation.id],
                )
            )

        retrieval_results = self.retriever.retrieve(
            self.db,
            query=f"{request.query} shortage inventory substitution",
            drug_name=request.drug_name,
        )
        citations.extend(self.retriever.citations_from_results(retrieval_results))

        risk_level = self._resolve_risk_level(
            qoh=qoh,
            has_shortage=bool(local_shortages or live_results),
            has_recall=bool(local_recalls),
            recall_risk=recall_risk,
        )
        if risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL}:
            recommended_actions.append("Escalate substitution questions to pharmacist and prescriber review.")
        recommended_actions = list(dict.fromkeys(recommended_actions))

        return {
            "agent_name": "shortage_agent",
            "status": "completed",
            "risk_level": risk_level.value,
            "findings": [item.model_dump() for item in findings],
            "recommended_actions": recommended_actions,
            "citations": [citation.model_dump() for citation in citations],
            "inventory_available": (qoh or 0) > 0,
        }

    def _matching_shortages(self, aliases: list[str]) -> list[ShortageEvent]:
        if not aliases:
            return []
        events = self.db.query(ShortageEvent).all()
        return [
            event
            for event in events
            if event.drug_name.lower() in aliases or (event.generic_name or "").lower() in aliases
        ]

    def _matching_recalls(self, aliases: list[str]) -> list[RecallEvent]:
        if not aliases:
            return []
        events = self.db.query(RecallEvent).all()
        return [event for event in events if any(alias in event.drug_name.lower() for alias in aliases)]

    @staticmethod
    def _resolve_risk_level(
        *,
        qoh: int | None,
        has_shortage: bool,
        has_recall: bool,
        recall_risk: RiskLevel,
    ) -> RiskLevel:
        if recall_risk == RiskLevel.CRITICAL:
            return RiskLevel.CRITICAL
        if has_recall and qoh == 0:
            return RiskLevel.HIGH
        if has_shortage or qoh == 0:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
