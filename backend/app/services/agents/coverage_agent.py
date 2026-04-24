from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.constants import BRAND_TO_GENERIC
from app.schemas.agent import Citation, CriterionStatus, Finding
from app.schemas.case import CaseAnalyzeRequest
from app.schemas.risk import RiskLevel
from app.services.agents.base import BaseAgent
from app.services.data_connectors.mock_payer_policy import MockPayerPolicyConnector


class CoverageAgent(BaseAgent):
    def __init__(self, db: Session) -> None:
        super().__init__(db)
        self.policy_connector = MockPayerPolicyConnector()

    async def run(self, request: CaseAnalyzeRequest, **kwargs: Any) -> dict[str, Any]:
        policy_drug = self._infer_target_drug(request)
        policy = self.policy_connector.find_policy(request.payer_name, policy_drug)
        findings: list[Finding] = []
        citations: list[Citation] = []
        criteria_status: list[CriterionStatus] = []
        missing_evidence: list[str] = []
        recommended_actions: list[str] = []
        draft_appeal_letter = ""

        case_citation = Citation(
            id="case-data::patient-context",
            source_name="Provided case data",
            source_url=None,
            document_title="Case input",
            section_title="patient_context",
            snippet=str(request.patient_context.model_dump())[:280],
            source_type="case_data",
            note="Based on provided case data",
        )
        citations.append(case_citation)

        retrieval_results = self.retriever.retrieve(
            self.db,
            query=f"{request.query} prior authorization coverage criteria {policy_drug or request.drug_name or ''}",
            drug_name=policy_drug or request.drug_name,
            payer_name=request.payer_name,
            metadata_filters={"source_type": "payer_policy"} if request.payer_name else None,
        )
        citations.extend(self.retriever.citations_from_results(retrieval_results))

        if policy:
            policy_citation = Citation(
                id=f"payer-policy::{policy['payer_name']}::{policy['drug_name']}",
                source_name=policy["source"],
                source_url=policy["source_url"],
                document_title=policy["policy_title"],
                section_title="approval_criteria",
                snippet=policy["criteria_text"][:280],
                source_type="payer_policy",
            )
            citations.append(policy_citation)
            criteria_status = self._evaluate_policy(policy, request)
            missing_evidence = [
                item.criterion for item in criteria_status if item.status == "missing"
            ]
            if missing_evidence:
                findings.append(
                    Finding(
                        title="Missing prior authorization evidence",
                        detail="The case does not yet include all payer-required documentation.",
                        evidence_ids=[policy_citation.id, case_citation.id],
                    )
                )
            recommended_actions = [
                f"Request {criterion.lower()} from prescriber." for criterion in missing_evidence
            ]
            if any("A1c" in criterion for criterion in missing_evidence):
                recommended_actions.append("Attach the latest A1c documentation.")
            if any("Metformin" in criterion for criterion in missing_evidence):
                recommended_actions.append("Include metformin trial, failure, or intolerance history.")
            if any("Prescriber chart notes" in criterion for criterion in missing_evidence):
                recommended_actions.append("Request chart notes from prescriber.")
            if not missing_evidence:
                recommended_actions.append("Prepare a complete PA packet and submit for payer review.")
            if "denied" in request.query.lower():
                findings.append(
                    Finding(
                        title="Coverage denial mentioned in case",
                        detail="Query indicates the requested or alternate GLP-1 medication was denied by insurance.",
                        evidence_ids=[case_citation.id],
                    )
                )
            draft_appeal_letter = self._draft_appeal_letter(policy, request, criteria_status)
        else:
            findings.append(
                Finding(
                    title="No payer policy found",
                    detail="No supporting source found for payer-specific coverage criteria. Needs pharmacist review.",
                    evidence_ids=[case_citation.id],
                )
            )
            recommended_actions.append("Obtain the latest payer coverage policy before submitting or appealing.")

        risk_level = self._risk_level(request, missing_evidence)
        prescriber_message = self._draft_prescriber_message(request, policy_drug or request.drug_name, missing_evidence)

        return {
            "agent_name": "coverage_agent",
            "status": "completed",
            "risk_level": risk_level.value,
            "pa_likely_required": True,
            "criteria_status": [item.model_dump() for item in criteria_status],
            "missing_evidence": missing_evidence,
            "findings": [item.model_dump() for item in findings],
            "recommended_actions": list(dict.fromkeys(recommended_actions)),
            "draft_prescriber_message": prescriber_message,
            "draft_appeal_letter": draft_appeal_letter,
            "citations": [citation.model_dump() for citation in citations],
        }

    def _infer_target_drug(self, request: CaseAnalyzeRequest) -> str | None:
        query = request.query.lower()
        denied_targets = []
        for brand_name in BRAND_TO_GENERIC:
            if brand_name in query and "denied" in query:
                denied_targets.append(brand_name.title())
        if denied_targets:
            # Prefer the first explicitly denied drug in the query.
            return denied_targets[0]
        return request.drug_name

    def _evaluate_policy(self, policy: dict[str, Any], request: CaseAnalyzeRequest) -> list[CriterionStatus]:
        diagnoses = [item.lower() for item in request.patient_context.diagnoses]
        labs = {key.lower(): value for key, value in request.patient_context.labs.items()}
        previous_therapies = [item.lower() for item in request.patient_context.previous_therapies]

        output: list[CriterionStatus] = []
        for criterion in policy.get("criteria", []):
            normalized = criterion.lower()
            if "type 2 diabetes" in normalized:
                met = any("type 2 diabetes" in diagnosis for diagnosis in diagnoses)
                output.append(CriterionStatus(criterion=criterion, status="met" if met else "missing", evidence="patient_context.diagnoses" if met else None))
            elif "a1c" in normalized:
                met = "a1c" in labs
                output.append(CriterionStatus(criterion=criterion, status="met" if met else "missing", evidence="patient_context.labs.a1c" if met else None))
            elif "metformin" in normalized:
                met = any("metformin" in therapy for therapy in previous_therapies)
                output.append(CriterionStatus(criterion=criterion, status="met" if met else "missing", evidence="patient_context.previous_therapies" if met else None))
            elif "obesity" in normalized or "overweight" in normalized:
                met = any(term in " ".join(diagnoses) for term in ("obesity", "overweight"))
                output.append(CriterionStatus(criterion=criterion, status="met" if met else "missing", evidence="patient_context.diagnoses" if met else None))
            elif "bmi" in normalized:
                met = "bmi" in labs
                output.append(CriterionStatus(criterion=criterion, status="met" if met else "missing", evidence="patient_context.labs.bmi" if met else None))
            elif "lifestyle" in normalized:
                met = any("lifestyle" in therapy or "diet" in therapy for therapy in previous_therapies)
                output.append(CriterionStatus(criterion=criterion, status="met" if met else "missing", evidence="patient_context.previous_therapies" if met else None))
            elif "chart notes" in normalized:
                chart_notes = request.patient_context.labs.get("chart_notes") or request.patient_context.labs.get("prescriber_chart_notes")
                met = bool(chart_notes)
                output.append(CriterionStatus(criterion=criterion, status="met" if met else "missing", evidence="patient_context.labs.chart_notes" if met else None))
            else:
                output.append(CriterionStatus(criterion=criterion, status="unknown", evidence=None))
        return output

    @staticmethod
    def _risk_level(request: CaseAnalyzeRequest, missing_evidence: list[str]) -> RiskLevel:
        if "denied" in request.query.lower() or missing_evidence:
            return RiskLevel.HIGH
        if request.payer_name:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    @staticmethod
    def _draft_prescriber_message(
        request: CaseAnalyzeRequest,
        policy_drug: str | None,
        missing_evidence: list[str],
    ) -> str:
        target = policy_drug or request.drug_name or "the GLP-1 medication"
        missing_line = ", ".join(item.lower() for item in missing_evidence) if missing_evidence else "supporting documentation"
        return (
            f"We are preparing a payer review for {target}. Please send {missing_line}, along with the "
            "most recent chart notes and treatment history so the pharmacy can assemble a pharmacist-reviewable PA or appeal packet."
        )

    @staticmethod
    def _draft_appeal_letter(
        policy: dict[str, Any],
        request: CaseAnalyzeRequest,
        criteria_status: list[CriterionStatus],
    ) -> str:
        met = [item.criterion for item in criteria_status if item.status == "met"]
        missing = [item.criterion for item in criteria_status if item.status == "missing"]
        return (
            f"Draft appeal for {policy['drug_name']} under {policy['payer_name']}: "
            f"documented case data supports {', '.join(met) if met else 'partial criteria'}, "
            f"while the following items still need confirmation or attachment: {', '.join(missing) if missing else 'none identified'}."
        )
