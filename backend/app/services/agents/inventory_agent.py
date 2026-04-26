"""
Inventory & Batch Agent
Checks stock status, batch validity, and supplier details.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from sqlalchemy import select, or_
from app.db.postgres import async_session_maker
from app.models.postgres_models import InventoryItem, DrugMaster

logger = logging.getLogger(__name__)


class InventoryBatchAgent:
    async def run(self, drug_name: str, quantity_on_hand: Optional[int] = None, batch_number: Optional[str] = None, supplier_name: Optional[str] = None, location_id: Optional[str] = None) -> Dict[str, Any]:
        findings: List[str] = []
        actions: List[str] = []
        risk_level = "LOW"

        inventory_items = []
        try:
            async with async_session_maker() as session:
                dm_q = select(DrugMaster).where(or_(DrugMaster.brand_name.ilike(f"%{drug_name}%"), DrugMaster.generic_name.ilike(f"%{drug_name}%"))).limit(1)
                dm_res = await session.execute(dm_q)
                drug = dm_res.scalar_one_or_none()

                if drug:
                    inv_q = select(InventoryItem).where(InventoryItem.drug_id == drug.id)
                    if location_id:
                        inv_q = inv_q.where(InventoryItem.location_id == location_id)
                    inv_q = inv_q.limit(5)
                    inv_res = await session.execute(inv_q)
                    inventory_items = inv_res.scalars().all()
        except Exception as e:
            logger.error(f"InventoryAgent DB error: {e}")
            findings.append("Inventory database lookup unavailable.")

        if inventory_items:
            for item in inventory_items:
                stock = item.quantity_on_hand
                findings.append(f"Stock at {item.location_id or 'location'}: {stock} units (batch: {item.batch_number or 'N/A'})")
                if stock == 0:
                    risk_level = "MEDIUM"
                    findings.append(f"Requested brand is OUT OF STOCK.")
                    actions.append("Check same-composition alternatives from verified suppliers.")
                elif stock <= item.reorder_threshold:
                    risk_level = "LOW"
                    findings.append(f"Stock is LOW ({stock} units, reorder threshold: {item.reorder_threshold}).")
                    actions.append("Initiate reorder from licensed supplier.")
        elif quantity_on_hand == 0 or quantity_on_hand is not None and quantity_on_hand == 0:
            risk_level = "MEDIUM"
            findings.append("Requested brand is out of stock (provided by caller).")
            actions.append("Check same-composition alternatives.")
        else:
            findings.append(f"No inventory record found for '{drug_name}' in database.")
            actions.append("Manually verify stock availability.")

        if not batch_number:
            findings.append("Batch number not provided — batch verification incomplete.")
            actions.append("Request batch number, expiry date, and supplier invoice.")

        actions.append("Do not change molecule, strength, route, or dosage form without pharmacist/prescriber review.")

        return {
            "agent": "inventory_batch_agent",
            "risk_level": risk_level,
            "findings": findings,
            "actions": actions,
        }
