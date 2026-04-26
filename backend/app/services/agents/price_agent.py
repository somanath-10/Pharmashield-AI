"""
Price & Jan Aushadhi Agent
Checks MRP, NPPA ceiling price, and Jan Aushadhi availability for budget-sensitive patients.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import select, or_
from app.db.postgres import async_session_maker
from app.models.postgres_models import PriceRecord, JanAushadhiProduct, DrugMaster

logger = logging.getLogger(__name__)


class PriceJanAushadhiAgent:
    """
    Checks MRP, NPPA reference, same-composition alternatives, and Jan Aushadhi availability.
    """

    async def run(
        self,
        drug_name: str,
        composition: Optional[str] = None,
        mrp: Optional[float] = None,
        patient_budget_sensitive: bool = False,
    ) -> Dict[str, Any]:
        findings: List[str] = []
        actions: List[str] = []
        risk_level = "LOW"

        # Search price records
        price_records = []
        ja_products = []
        drug_master_matches = []

        try:
            async with async_session_maker() as session:
                # Search PriceRecord
                price_q = select(PriceRecord).where(
                    or_(
                        PriceRecord.brand_name.ilike(f"%{drug_name}%"),
                        PriceRecord.generic_name.ilike(f"%{drug_name}%"),
                        PriceRecord.composition.ilike(f"%{composition or drug_name}%"),
                    )
                ).limit(5)
                pr = await session.execute(price_q)
                price_records = pr.scalars().all()

                # Search JanAushadhi
                ja_q = select(JanAushadhiProduct).where(
                    or_(
                        JanAushadhiProduct.generic_name.ilike(f"%{drug_name}%"),
                        JanAushadhiProduct.composition.ilike(f"%{composition or drug_name}%"),
                    )
                ).limit(5)
                jr = await session.execute(ja_q)
                ja_products = jr.scalars().all()

                # Search DrugMaster for same composition
                dm_q = select(DrugMaster).where(
                    or_(
                        DrugMaster.generic_name.ilike(f"%{drug_name}%"),
                        DrugMaster.composition.ilike(f"%{composition or drug_name}%"),
                    )
                ).limit(5)
                dr = await session.execute(dm_q)
                drug_master_matches = dr.scalars().all()

        except Exception as e:
            logger.error(f"PriceAgent DB error: {e}")
            findings.append("Database lookup unavailable; providing guidance based on policy rules.")

        # Analyze results
        if patient_budget_sensitive:
            findings.append("Patient is marked as budget-sensitive.")
            findings.append("Check same-composition generic options and verify MRP using NPPA/Pharma Sahi Daam reference.")
            actions.append("Show lower-cost same-composition options if available.")
            actions.append("Do not substitute without pharmacist/prescriber review where required.")

        if price_records:
            for pr_rec in price_records[:2]:
                findings.append(
                    f"Price record found: {pr_rec.brand_name} — MRP ₹{pr_rec.mrp}"
                    + (f", NPPA ceiling ₹{pr_rec.ceiling_price}" if pr_rec.ceiling_price else "")
                )
                if mrp and pr_rec.ceiling_price and mrp > pr_rec.ceiling_price:
                    findings.append(
                        f"WARNING: Provided MRP (₹{mrp}) exceeds NPPA ceiling price (₹{pr_rec.ceiling_price})."
                    )
                    risk_level = "HIGH"
                    actions.append("Verify MRP with NPPA/Pharma Sahi Daam before dispensing.")
        else:
            findings.append("No price record found in database for this medicine.")
            actions.append("Manually verify MRP using NPPA Pharma Sahi Daam (pharmadost.nic.in).")

        if ja_products:
            for ja in ja_products[:2]:
                findings.append(
                    f"Jan Aushadhi alternative found: {ja.generic_name} — "
                    f"₹{ja.janaushadhi_price} ({ja.availability_status})"
                )
            actions.append("Inform patient about Jan Aushadhi Kendra availability if clinically appropriate.")
        else:
            findings.append("No Jan Aushadhi product match found in database.")
            actions.append("Check PMBJP portal (janaushadhi.gov.in) for availability.")

        if drug_master_matches:
            alternatives = [
                f"{d.brand_name} ({d.generic_name}, {d.strength})"
                for d in drug_master_matches
                if d.brand_name.lower() not in drug_name.lower()
            ]
            if alternatives:
                findings.append(f"Same-composition alternatives in database: {', '.join(alternatives[:3])}")

        return {
            "agent": "price_janaushadhi_agent",
            "risk_level": risk_level,
            "findings": findings,
            "actions": actions,
        }
