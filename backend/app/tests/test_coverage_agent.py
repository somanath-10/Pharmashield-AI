from __future__ import annotations

import pytest

from app.schemas.case import CaseAnalyzeRequest, PatientContext
from app.services.agents.coverage_agent import CoverageAgent


@pytest.mark.asyncio
async def test_coverage_agent_detects_missing_chart_notes(db_session) -> None:
    request = CaseAnalyzeRequest(
        query="Need prior authorization support for Ozempic",
        drug_name="Ozempic",
        payer_name="Demo Health Plan",
        patient_context=PatientContext(
            diagnoses=["type 2 diabetes"],
            labs={"a1c": "8.7"},
            previous_therapies=["metformin"],
        ),
    )
    result = await CoverageAgent(db_session).run(request)
    assert result["risk_level"] == "HIGH"
    assert any(item["criterion"] == "Prescriber chart notes" and item["status"] == "missing" for item in result["criteria_status"])
    assert result["draft_appeal_letter"]
