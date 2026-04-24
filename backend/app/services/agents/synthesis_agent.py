from __future__ import annotations

from typing import Any

from app.core.constants import PHARMACIST_REVIEW_DISCLAIMER, RISK_ORDER
from app.schemas.agent import Citation
from app.schemas.case import AgentTraceItem, CaseAnalyzeRequest, CaseAnalyzeResponse
from app.schemas.risk import RiskLevel


class SynthesisAgent:
    async def run(
        self,
        *,
        case_id: str,
        request: CaseAnalyzeRequest,
        intent: str,
        detected_intents: list[str],
        agent_outputs: dict[str, dict[str, Any]],
        memory_notes: list[dict[str, Any]],
    ) -> CaseAnalyzeResponse:
        overall_risk = self._max_risk(
            [output.get("risk_level", RiskLevel.LOW.value) for output in agent_outputs.values()]
        )
        citations = self._collect_citations(agent_outputs)
        action_plan = self._collect_actions(agent_outputs)
        summary = self._summary_text(request, agent_outputs, overall_risk, citations)
        draft_prescriber_message = agent_outputs.get("coverage", {}).get(
            "draft_prescriber_message",
            "Please review the payer requirements and submit the missing pharmacist-reviewable documentation packet.",
        )
        draft_patient_message = agent_outputs.get("authenticity", {}).get(
            "draft_patient_message",
            "Please wait for pharmacist review before changing therapy, supplier, or product source.",
        )

        trace = []
        for key, output in agent_outputs.items():
            trace.append(
                AgentTraceItem(
                    agent_name=output.get("agent_name", key),
                    status=output.get("status", "completed"),
                    risk_level=output.get("risk_level", RiskLevel.LOW.value),
                    findings=output.get("findings", []),
                    recommended_actions=output.get("recommended_actions", []),
                    citations=output.get("citations", []),
                    details={
                        item_key: item_value
                        for item_key, item_value in output.items()
                        if item_key not in {"agent_name", "status", "risk_level", "findings", "recommended_actions", "citations"}
                    },
                )
            )

        return CaseAnalyzeResponse(
            case_id=case_id,
            risk_level=overall_risk,
            intent=intent,
            detected_intents=detected_intents,
            summary=summary,
            action_plan=action_plan,
            agent_outputs=agent_outputs,
            agent_trace=trace,
            citations=citations,
            draft_prescriber_message=draft_prescriber_message,
            draft_patient_message=draft_patient_message,
            pharmacist_review_required=True,
            memory_notes=memory_notes,
        )

    @staticmethod
    def _max_risk(risk_levels: list[str]) -> RiskLevel:
        best = RiskLevel.LOW.value
        for risk in risk_levels:
            if RISK_ORDER.get(risk, 0) > RISK_ORDER.get(best, 0):
                best = risk
        return RiskLevel(best)

    @staticmethod
    def _collect_citations(agent_outputs: dict[str, dict[str, Any]]) -> list[Citation]:
        seen: dict[str, Citation] = {}
        for output in agent_outputs.values():
            for payload in output.get("citations", []):
                citation = Citation.model_validate(payload)
                seen[citation.id] = citation
        return list(seen.values())

    @staticmethod
    def _collect_actions(agent_outputs: dict[str, dict[str, Any]]) -> list[str]:
        actions: list[str] = []
        for output in agent_outputs.values():
            actions.extend(output.get("recommended_actions", []))
        actions.append(PHARMACIST_REVIEW_DISCLAIMER)
        return list(dict.fromkeys(actions))

    @staticmethod
    def _summary_text(
        request: CaseAnalyzeRequest,
        agent_outputs: dict[str, dict[str, Any]],
        overall_risk: RiskLevel,
        citations: list[Citation],
    ) -> str:
        sections = [f"Overall Risk Level: {overall_risk.value}."]
        if "shortage" in agent_outputs:
            sections.append("Shortage / Inventory Assessment: local inventory is unavailable or constrained and substitution should stay prescriber-reviewed.")
        if "coverage" in agent_outputs:
            sections.append("Coverage / Prior Authorization Assessment: payer documentation gaps or denial signals were identified and a draft prescriber request was prepared.")
        if "authenticity" in agent_outputs:
            sections.append("Authenticity / Compliance Assessment: the patient-provided product source has red flags and should not be recommended until verified through a licensed supply chain.")
        citation_note = "Evidence and citations attached." if citations else "No supporting source found. Needs pharmacist review."
        sections.append(citation_note)
        sections.append(PHARMACIST_REVIEW_DISCLAIMER)
        return " ".join(sections)
