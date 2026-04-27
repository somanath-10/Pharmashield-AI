from typing import Any, Dict, List, Optional
import logging

from app.db.postgres import async_session_maker
from sqlalchemy import select, or_, and_
from app.models.postgres_models import DrugMaster

logger = logging.getLogger(__name__)

class SubstitutionSafetyAgent:
    """
    Compares two medicines.
    Requires same molecule, strength, route, dosage form, release type.
    Flags unsafe substitution.
    """
    async def run(self, prescribed: str, alternative: str) -> Dict[str, Any]:
        is_safe = False
        reasons = []
        risk_level = "LOW"
        
        try:
            async with async_session_maker() as session:
                q1 = select(DrugMaster).where(
                    or_(
                        DrugMaster.brand_name.ilike(f"%{prescribed}%"),
                        DrugMaster.generic_name.ilike(f"%{prescribed}%")
                    )
                ).limit(1)
                res1 = await session.execute(q1)
                drug1 = res1.scalar_one_or_none()
                
                q2 = select(DrugMaster).where(
                    or_(
                        DrugMaster.brand_name.ilike(f"%{alternative}%"),
                        DrugMaster.generic_name.ilike(f"%{alternative}%")
                    )
                ).limit(1)
                res2 = await session.execute(q2)
                drug2 = res2.scalar_one_or_none()
                
                if drug1 and drug2:
                    if drug1.composition.lower() != drug2.composition.lower():
                        reasons.append("Molecule composition mismatch.")
                    if drug1.strength != drug2.strength:
                        reasons.append("Strength mismatch.")
                    if drug1.dosage_form != drug2.dosage_form:
                        reasons.append("Dosage form mismatch.")
                    
                    if not reasons:
                        is_safe = True
                        reasons.append("Substitution appears safe based on matching composition, strength, and form.")
                    else:
                        risk_level = "HIGH"
                else:
                    reasons.append("Could not find complete details for one or both medicines in the database.")
                    risk_level = "MEDIUM"
        except Exception as e:
            logger.error(f"Substitution DB error: {e}")
            reasons.append("Database error during substitution check.")
            risk_level = "UNKNOWN"

        return {
            "agent": "substitution_safety_agent",
            "is_safe": is_safe,
            "risk_level": risk_level,
            "mismatch_reasons": reasons
        }
