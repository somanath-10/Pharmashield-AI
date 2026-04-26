"""
NSQ / Spurious Alert Agent
Validates a medicine batch against CDSCO NSQ/spurious alert records.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import select, or_, and_
from app.db.postgres import async_session_maker
from app.models.postgres_models import NSQAlert

logger = logging.getLogger(__name__)


class NSQSuriousAgent:
    """
    Checks drug name, brand, manufacturer, and batch against CDSCO NSQ records.
    """

    async def run(
        self,
        drug_name: str,
        brand_name: Optional[str] = None,
        manufacturer: Optional[str] = None,
        batch_number: Optional[str] = None,
        composition: Optional[str] = None,
    ) -> Dict[str, Any]:
        findings: List[str] = []
        actions: List[str] = []
        risk_level = "LOW"
        matched_alerts = []

        missing_fields = []
        if not batch_number:
            missing_fields.append("batch number")
        if not manufacturer:
            missing_fields.append("manufacturer")

        try:
            async with async_session_maker() as session:
                # Try exact match on batch + manufacturer first
                if batch_number and manufacturer:
                    exact_q = select(NSQAlert).where(
                        and_(
                            NSQAlert.batch_number.ilike(f"%{batch_number}%"),
                            NSQAlert.manufacturer.ilike(f"%{manufacturer}%"),
                        )
                    ).limit(5)
                    res = await session.execute(exact_q)
                    matched_alerts = res.scalars().all()

                # If no exact match, try drug name / brand
                if not matched_alerts:
                    name_q = select(NSQAlert).where(
                        or_(
                            NSQAlert.drug_name.ilike(f"%{drug_name}%"),
                            NSQAlert.brand_name.ilike(f"%{brand_name or drug_name}%"),
                            NSQAlert.composition.ilike(f"%{composition or drug_name}%"),
                        )
                    ).limit(5)
                    res2 = await session.execute(name_q)
                    matched_alerts = res2.scalars().all()

        except Exception as e:
            logger.error(f"NSQAgent DB error: {e}")
            findings.append("Database lookup unavailable for NSQ check.")
            risk_level = "MEDIUM"

        if matched_alerts:
            if batch_number and manufacturer:
                # Check if any of the matches are exact batch+manufacturer matches
                exact_matches = [
                    a for a in matched_alerts
                    if batch_number.lower() in (a.batch_number or "").lower()
                    and manufacturer.lower() in (a.manufacturer or "").lower()
                ]
                if exact_matches:
                    risk_level = "CRITICAL"
                    for alert in exact_matches:
                        findings.append(
                            f"EXACT NSQ MATCH: {alert.drug_name} | Batch {alert.batch_number} | "
                            f"Mfr: {alert.manufacturer} | Reason: {alert.failure_reason} | "
                            f"Source: {alert.reporting_source} ({alert.month} {alert.year})"
                        )
                    actions += [
                        "Do NOT dispense this batch.",
                        "Quarantine stock immediately.",
                        "Notify pharmacist and admin.",
                        "Record alert match in audit log.",
                    ]
                else:
                    risk_level = "MEDIUM"
                    for alert in matched_alerts[:2]:
                        findings.append(
                            f"Related NSQ alert found for {alert.drug_name}: {alert.failure_reason} "
                            f"({alert.month} {alert.year})"
                        )
                    actions.append("Exact batch not matched but similar alerts exist — verify carefully.")
            else:
                risk_level = "MEDIUM"
                for alert in matched_alerts[:2]:
                    findings.append(
                        f"NSQ alert for {alert.drug_name}: {alert.failure_reason} ({alert.month} {alert.year})"
                    )
                actions.append("Verify batch and manufacturer against NSQ records before dispensing.")
        else:
            findings.append("No NSQ/spurious alert found for the provided details.")

        # Missing field warnings
        if missing_fields:
            if risk_level == "LOW":
                risk_level = "MEDIUM"
            for f in missing_fields:
                findings.append(f"WARNING: {f.capitalize()} is missing — NSQ verification is incomplete.")
            actions.append(
                "Request batch number, manufacturer, expiry date, invoice, and source before dispensing."
            )

        return {
            "agent": "nsq_spurious_agent",
            "risk_level": risk_level,
            "findings": findings,
            "actions": actions,
            "alerts_found": len(matched_alerts),
        }
