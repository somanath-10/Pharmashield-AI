"""
Prescription Compliance Agent
Checks Schedule H/H1/X rules and whether a valid prescription is available.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import select, or_
from app.db.postgres import async_session_maker
from app.models.postgres_models import DrugScheduleRule, DrugMaster

logger = logging.getLogger(__name__)

HIGH_RISK_SCHEDULES = {"H1", "X"}
PRESCRIPTION_REQUIRED_SCHEDULES = {"H", "H1", "X"}


class PrescriptionComplianceAgent:
    """
    Evaluates Schedule H/H1/X compliance rules for a medicine before dispensing.
    """

    async def run(
        self,
        medicine_name: str,
        composition: Optional[str] = None,
        prescription_available: bool = True,
        claim_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        findings: List[str] = []
        actions: List[str] = []
        risk_level = "LOW"

        schedule_rules = []
        drug_master_entry = None

        try:
            async with async_session_maker() as session:
                # Check DrugScheduleRule
                rule_q = select(DrugScheduleRule).where(
                    or_(
                        DrugScheduleRule.drug_name.ilike(f"%{medicine_name}%"),
                        DrugScheduleRule.composition.ilike(f"%{composition or medicine_name}%"),
                    )
                ).limit(5)
                res = await session.execute(rule_q)
                schedule_rules = res.scalars().all()

                # Check DrugMaster
                dm_q = select(DrugMaster).where(
                    or_(
                        DrugMaster.brand_name.ilike(f"%{medicine_name}%"),
                        DrugMaster.generic_name.ilike(f"%{medicine_name}%"),
                        DrugMaster.composition.ilike(f"%{composition or medicine_name}%"),
                    )
                ).limit(1)
                dm_res = await session.execute(dm_q)
                drug_master_entry = dm_res.scalar_one_or_none()

        except Exception as e:
            logger.error(f"ComplianceAgent DB error: {e}")
            findings.append("Database lookup unavailable; applying default Schedule H caution.")

        # Determine schedule
        schedule = None
        if drug_master_entry:
            schedule = drug_master_entry.schedule_category
        if schedule_rules:
            schedule = schedule or schedule_rules[0].schedule_category
            for rule in schedule_rules:
                findings.append(f"Schedule rule: {rule.rule_summary}")

        if schedule:
            findings.append(f"Medicine is classified under Schedule {schedule}.")
            if schedule in PRESCRIPTION_REQUIRED_SCHEDULES:
                if not prescription_available:
                    # No prescription — HIGH for H1/X, MEDIUM for H
                    risk_level = "HIGH" if schedule in HIGH_RISK_SCHEDULES else "MEDIUM"
                    findings.append("Prescription is NOT available.")
                    findings.append(
                        f"Schedule {schedule} medicines REQUIRE a valid prescription before dispensing."
                    )
                    actions.append(
                        f"Do not dispense Schedule {schedule} medicine without a valid prescription."
                    )
                    actions.append("Escalate to registered pharmacist immediately.")
                else:
                    # Prescription present — MEDIUM for H1/X (verification still needed), LOW for H
                    risk_level = "MEDIUM" if schedule in HIGH_RISK_SCHEDULES else "LOW"
                    findings.append("Prescription is available — verify validity, date, doctor details.")
                    actions.append("Check prescription date, doctor registration number, and patient details.")
        else:
            findings.append(f"Schedule classification for '{medicine_name}' not found in database.")
            findings.append("Treating as prescription-required as a precautionary measure.")
            if not prescription_available:
                risk_level = "MEDIUM"
                actions.append("Verify prescription requirement before dispensing.")

        # Check suspicious claims
        suspicious_phrases = [
            "no prescription needed",
            "no prescription required",
            "otc",
            "over the counter",
        ]
        if claim_text:
            claim_lower = claim_text.lower()
            for phrase in suspicious_phrases:
                if phrase in claim_lower:
                    findings.append(f"Suspicious claim detected: '{claim_text}'")
                    risk_level = "HIGH"
                    actions.append(
                        "This claim contradicts Schedule rules. Do not dispense without verification."
                    )
                    break

        if not actions:
            actions.append("Standard dispensing check completed. Pharmacist review recommended.")

        return {
            "agent": "prescription_compliance_agent",
            "risk_level": risk_level,
            "schedule": schedule,
            "prescription_available": prescription_available,
            "findings": findings,
            "actions": actions,
        }
