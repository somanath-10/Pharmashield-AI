from __future__ import annotations

import pytest

from app.schemas.case import CaseAnalyzeRequest, InventoryContext, PatientContext, ProductContext
from app.services.agents.coordinator import AgentCoordinator


@pytest.mark.asyncio
async def test_coordinator_returns_multi_agent_response(db_session) -> None:
    request = CaseAnalyzeRequest(
        query=(
            "Ozempic is out of stock, Wegovy was denied by insurance, and patient found a cheaper "
            "semaglutide supplier online claiming generic Ozempic with no prescription needed. What should pharmacy staff do?"
        ),
        drug_name="Ozempic",
        payer_name="Demo Health Plan",
        patient_context=PatientContext(
            age=52,
            diagnoses=["type 2 diabetes"],
            labs={"a1c": "8.7"},
            previous_therapies=["metformin"],
            allergies=[],
        ),
        inventory_context=InventoryContext(location_id="PHARMACY_001", quantity_on_hand=0, reorder_threshold=2),
        product_context=ProductContext(
            supplier_name="Online Semaglutide Discount Pharmacy",
            claim_text="Generic Ozempic, same active ingredient, no prescription needed",
            ndc=None,
            lot_number=None,
            manufacturer=None,
        ),
    )
    result = await AgentCoordinator(db_session).analyze_case(request)
    assert result.risk_level.value == "HIGH"
    assert "shortage" in result.agent_outputs
    assert "coverage" in result.agent_outputs
    assert "authenticity" in result.agent_outputs
    assert result.pharmacist_review_required is True
    assert result.citations
