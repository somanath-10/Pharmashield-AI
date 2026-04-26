"""
Scheme / Claim Agent
Explains PM-JAY, CGHS, ESIC, and other health scheme applicability.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from app.db.postgres import async_session_maker
from app.models.postgres_models import SchemeRule

logger = logging.getLogger(__name__)


class SchemeClaimAgent:
    async def run(self, scheme_name: Optional[str] = None, hospitalized: bool = False, purchase_context: str = "retail_pharmacy") -> Dict[str, Any]:
        findings: List[str] = []
        actions: List[str] = []

        scheme_rules = []
        try:
            async with async_session_maker() as session:
                q = select(SchemeRule).where(SchemeRule.scheme_name.ilike(f"%{scheme_name or ''}%")).limit(3) if scheme_name else select(SchemeRule).limit(5)
                res = await session.execute(q)
                scheme_rules = res.scalars().all()
        except Exception as e:
            logger.error(f"SchemeAgent DB error: {e}")

        if scheme_rules:
            for rule in scheme_rules:
                findings.append(f"{rule.scheme_name}: {rule.coverage_summary}")
                if purchase_context == "retail_pharmacy" and not rule.applies_to_retail_pharmacy:
                    findings.append(f"{rule.scheme_name} primarily covers hospitalization at empanelled hospitals, not retail pharmacy purchases.")
                    actions.append(f"Ask patient to verify {rule.scheme_name} coverage at their empanelled hospital desk.")
                elif hospitalized and rule.applies_to_hospitalization:
                    findings.append(f"{rule.scheme_name} may apply. Eligibility: {rule.eligibility_summary}")
                    actions.append(f"Patient should present {rule.scheme_name} card at the hospital insurance desk.")
        else:
            findings.append("PM-JAY provides Rs 5 lakh/family/year for hospitalization at empanelled hospitals — not retail OPD purchases.")
            findings.append("CGHS covers Central Govt employees. ESIC covers insured workers. Corporate OPD varies by employer.")

        if purchase_context == "retail_pharmacy":
            actions.append("Patient should retain prescription and invoice for any reimbursement claim.")
            actions.append("Check with HR/employer or scheme desk for OPD reimbursement eligibility.")

        return {
            "agent": "scheme_claim_agent",
            "risk_level": "LOW",
            "hospitalized": hospitalized,
            "purchase_context": purchase_context,
            "findings": findings,
            "actions": actions,
        }
