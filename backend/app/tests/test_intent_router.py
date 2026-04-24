from __future__ import annotations

import pytest

from app.schemas.case import CaseAnalyzeRequest, ProductContext
from app.services.agents.intent_router import IntentRouter


@pytest.mark.asyncio
async def test_intent_router_detects_multi_agent_case() -> None:
    request = CaseAnalyzeRequest(
        query="Ozempic out of stock and insurance denied Wegovy",
    )
    result = await IntentRouter().classify(request)
    assert result.intent == "MULTI_AGENT_CASE"
    assert "SHORTAGE" in result.detected_intents
    assert "PRIOR_AUTHORIZATION" in result.detected_intents


@pytest.mark.asyncio
async def test_intent_router_detects_authenticity_and_compounding() -> None:
    request = CaseAnalyzeRequest(
        query="Patient found generic Ozempic online with no prescription",
        product_context=ProductContext(
            supplier_name="Online supplier",
            claim_text="generic Ozempic with no prescription needed",
        ),
    )
    result = await IntentRouter().classify(request)
    assert "AUTHENTICITY" in result.detected_intents
    assert "COMPOUNDING_COMPLIANCE" in result.detected_intents
