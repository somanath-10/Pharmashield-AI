from __future__ import annotations

import pytest

from app.schemas.case import CaseAnalyzeRequest, InventoryContext
from app.services.agents.shortage_agent import ShortageAgent


@pytest.mark.asyncio
async def test_shortage_agent_flags_inventory_issue(db_session) -> None:
    request = CaseAnalyzeRequest(
        query="Ozempic is out of stock",
        drug_name="Ozempic",
        inventory_context=InventoryContext(location_id="PHARMACY_001", quantity_on_hand=0),
    )
    result = await ShortageAgent(db_session).run(request)
    assert result["risk_level"] in {"MEDIUM", "HIGH"}
    assert any(finding["title"] == "Inventory unavailable" for finding in result["findings"])
    assert any("Contact prescriber" in action for action in result["recommended_actions"])
