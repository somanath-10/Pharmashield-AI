from __future__ import annotations

import pytest

from app.schemas.case import CaseAnalyzeRequest, ProductContext
from app.services.agents.authenticity_agent import AuthenticityAgent


@pytest.mark.asyncio
async def test_authenticity_agent_flags_suspicious_glp1_product(db_session) -> None:
    request = CaseAnalyzeRequest(
        query="Patient found generic Ozempic online with no prescription",
        drug_name="Ozempic",
        product_context=ProductContext(
            supplier_name="Online Semaglutide Discount Pharmacy",
            claim_text="Generic Ozempic, same active ingredient, no prescription needed",
            ndc=None,
            lot_number=None,
        ),
    )
    result = await AuthenticityAgent(db_session).run(request)
    assert result["risk_level"] == "HIGH"
    assert "No NDC provided" in result["red_flags"]
    assert any("Do not recommend" in action for action in result["recommended_actions"])
