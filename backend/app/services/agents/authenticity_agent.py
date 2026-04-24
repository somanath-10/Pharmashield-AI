from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.constants import SUSPICIOUS_PRODUCT_CLAIMS
from app.db.models import RecallEvent
from app.schemas.agent import Citation, Finding
from app.schemas.case import CaseAnalyzeRequest
from app.schemas.risk import RiskLevel
from app.services.agents.base import BaseAgent


class AuthenticityAgent(BaseAgent):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    async def run(self, request: CaseAnalyzeRequest, **kwargs: Any) -> dict[str, Any]:
        product = request.product_context
        combined_text = " ".join(
            filter(None, [product.supplier_name, product.claim_text, request.query])
        ).lower()
        red_flags: list[str] = []
        citations: list[Citation] = [
            Citation(
                id="case-data::product-context",
                source_name="Provided case data",
                source_url=None,
                document_title="Case input",
                section_title="product_context",
                snippet=str(product.model_dump())[:280],
                source_type="case_data",
                note="Based on provided case data",
            )
        ]
        findings: list[Finding] = []

        for suspicious_claim in SUSPICIOUS_PRODUCT_CLAIMS:
            if suspicious_claim in combined_text:
                red_flags.append(f"Claim includes '{suspicious_claim}'")
        if not product.ndc:
            red_flags.append("No NDC provided")
        if not product.lot_number:
            red_flags.append("No lot number provided")
        if product.supplier_name and "discount" in product.supplier_name.lower():
            red_flags.append("Supplier name suggests discount or nonstandard online channel")

        recall_matches = self._matching_recalls(request.drug_name or "")
        recall_lot_match = False
        for recall in recall_matches:
            if product.lot_number and recall.code_info and product.lot_number.lower() in recall.code_info.lower():
                recall_lot_match = True
            citations.append(
                Citation(
                    id=f"recall::{recall.id}",
                    source_name=recall.source,
                    source_url=recall.source_url,
                    document_title=recall.drug_name,
                    section_title="recall",
                    snippet=(recall.reason_for_recall or recall.product_description or "Recall data available")[:280],
                    source_type="recall",
                )
            )

        retrieval_results = self.retriever.retrieve(
            self.db,
            query=f"{request.query} GLP-1 compliance counterfeit compounded semaglutide supplier verification",
            drug_name=request.drug_name,
        )
        citations.extend(self.retriever.citations_from_results(retrieval_results))

        if red_flags:
            findings.append(
                Finding(
                    title="Suspicious product marketing or documentation gaps",
                    detail="Multiple red flags suggest the product may be unverified, noncompliant, or unsafe to recommend without verification.",
                    evidence_ids=[citation.id for citation in citations[:2]],
                )
            )
        risk_level = self._risk_level(red_flags, recall_lot_match)
        recommended_actions = [
            "Do not recommend or dispense the product until verified.",
            "Verify supplier license, NDC, lot, manufacturer, and authorized distribution channel.",
            "Counsel patient to use a licensed pharmacy and prescriber-supervised medication.",
        ]
        if recall_lot_match:
            recommended_actions.insert(0, "Quarantine the affected product and follow recall workflow immediately.")
        patient_message = (
            "The product source you found has warning signs, including unsupported marketing claims or missing product identifiers. "
            "Please do not use or purchase it until the pharmacy and prescriber verify a regulated supply chain option."
        )

        return {
            "agent_name": "authenticity_agent",
            "status": "completed",
            "risk_level": risk_level.value,
            "authenticity_risk": "SUSPICIOUS" if red_flags else "LOW_CONCERN",
            "compliance_risk": (
                "POSSIBLE_UNAPPROVED_OR_NONCOMPLIANT_PRODUCT" if red_flags else "NO_MAJOR_SIGNAL_FOUND"
            ),
            "red_flags": red_flags,
            "findings": [item.model_dump() for item in findings],
            "recommended_actions": recommended_actions,
            "draft_patient_message": patient_message,
            "citations": [citation.model_dump() for citation in citations],
        }

    def _matching_recalls(self, drug_name: str) -> list[RecallEvent]:
        if not drug_name:
            return []
        lowered = drug_name.lower()
        return [
            recall
            for recall in self.db.query(RecallEvent).all()
            if lowered in recall.drug_name.lower() or lowered in (recall.product_description or "").lower()
        ]

    @staticmethod
    def _risk_level(red_flags: list[str], recall_lot_match: bool) -> RiskLevel:
        if recall_lot_match:
            return RiskLevel.CRITICAL
        if red_flags and any("no prescription needed" in flag.lower() or "generic ozempic" in flag.lower() for flag in red_flags):
            return RiskLevel.HIGH
        if red_flags:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
