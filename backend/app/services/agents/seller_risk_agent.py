"""
Online Seller Risk Agent
Detects suspicious WhatsApp/Instagram/unlicensed online medicine sellers.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import select, or_
from app.db.postgres import async_session_maker
from app.models.postgres_models import Supplier

logger = logging.getLogger(__name__)

SUSPICIOUS_SELLER_TYPES = {
    "whatsapp_seller", "instagram_seller", "unknown_online_seller"
}

SUSPICIOUS_PHRASES = [
    "no prescription needed",
    "no prescription required",
    "generic ozempic",
    "same as original",
    "whatsapp order",
    "instagram pharmacy",
    "cheap imported injection",
    "no bill",
    "no mrp",
    "no batch",
    "research use only",
    "direct from manufacturer",
    "imported",
]


class OnlineSellerRiskAgent:
    """
    Evaluates the risk of an online/WhatsApp/Instagram medicine seller.
    """

    async def run(
        self,
        seller_name: Optional[str] = None,
        seller_type: Optional[str] = None,
        claim_text: Optional[str] = None,
        license_number: Optional[str] = None,
        batch_number: Optional[str] = None,
        manufacturer: Optional[str] = None,
        mrp: Optional[float] = None,
    ) -> Dict[str, Any]:
        red_flags: List[str] = []
        actions: List[str] = []
        risk_level = "LOW"

        # Check database for known bad sellers
        db_supplier = None
        if seller_name:
            try:
                async with async_session_maker() as session:
                    q = select(Supplier).where(
                        Supplier.supplier_name.ilike(f"%{seller_name}%")
                    ).limit(1)
                    res = await session.execute(q)
                    db_supplier = res.scalar_one_or_none()
            except Exception as e:
                logger.error(f"SellerRiskAgent DB error: {e}")

        if db_supplier:
            if db_supplier.risk_score >= 7.0:
                risk_level = "HIGH"
                red_flags.append(
                    f"Supplier '{db_supplier.supplier_name}' is flagged in database "
                    f"(risk score: {db_supplier.risk_score})."
                )
                if isinstance(db_supplier.risk_reasons_json, list):
                    red_flags.extend(db_supplier.risk_reasons_json)
                elif isinstance(db_supplier.risk_reasons_json, dict):
                    red_flags.extend(db_supplier.risk_reasons_json.get("reasons", []))
            elif db_supplier.verification_status == "UNVERIFIED":
                risk_level = "MEDIUM"
                red_flags.append(f"Supplier '{db_supplier.supplier_name}' is unverified.")

        # Seller type check
        if seller_type and seller_type in SUSPICIOUS_SELLER_TYPES:
            risk_level = "HIGH"
            red_flags.append(f"Seller type is high-risk: {seller_type}.")

        # Missing critical fields
        if not license_number:
            red_flags.append("No license number provided.")
            if risk_level not in ("HIGH",):
                risk_level = "HIGH"
        if not batch_number:
            red_flags.append("No batch number provided.")
        if not manufacturer:
            red_flags.append("No manufacturer provided.")
        if mrp is None:
            red_flags.append("No MRP provided.")

        # Suspicious claim text
        if claim_text:
            claim_lower = claim_text.lower()
            matched_phrases = [p for p in SUSPICIOUS_PHRASES if p in claim_lower]
            for phrase in matched_phrases:
                red_flags.append(f"Suspicious claim: '{phrase}'")
                risk_level = "HIGH"

        # Build actions
        if risk_level == "HIGH":
            actions += [
                "Do NOT recommend this seller to the patient.",
                "Advise patient to buy only from a licensed pharmacy.",
                "Verify license number, batch, manufacturer, expiry, MRP, and invoice before any purchase.",
            ]
        elif risk_level == "MEDIUM":
            actions += [
                "Exercise caution with this seller.",
                "Request full documentation: license, invoice, batch, MRP.",
            ]
        else:
            actions.append("Seller details appear standard. Routine verification recommended.")

        return {
            "agent": "online_seller_risk_agent",
            "risk_level": risk_level,
            "red_flags": red_flags,
            "actions": actions,
        }
