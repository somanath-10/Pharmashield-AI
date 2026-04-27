from typing import Any, Dict
import logging
from app.models.domain import ADRReport

logger = logging.getLogger(__name__)

class ADRAgent:
    """
    Captures side-effect report draft. Gives severity triage guidance. Avoids diagnosis.
    """
    async def process_report(self, case_id: str, medicine_name: str, reaction: str, timeline: str, batch_number: str = None, age_range: str = None) -> Dict[str, Any]:
        
        severity = "MILD"
        reaction_lower = reaction.lower()
        if any(word in reaction_lower for word in ["anaphylaxis", "breathing", "swelling", "hospital", "chest pain", "severe"]):
            severity = "SEVERE"
        elif any(word in reaction_lower for word in ["vomiting", "diarrhea", "rash", "fever"]):
            severity = "MODERATE"
            
        report = ADRReport(
            case_id=case_id,
            medicine_name=medicine_name,
            batch_number=batch_number,
            reaction=reaction,
            timeline=timeline,
            patient_age_range=age_range,
            severity=severity,
            status="DRAFT"
        )
        await report.insert()
        
        guidance = "Report logged."
        if severity == "SEVERE":
            guidance = "SEVERE reaction indicated. Please advise the patient to seek immediate medical attention or visit an emergency room."
        elif severity == "MODERATE":
            guidance = "MODERATE reaction indicated. Recommend the patient consult their prescribing doctor."
            
        return {
            "adr_id": report.adr_id,
            "severity": severity,
            "guidance": guidance
        }
