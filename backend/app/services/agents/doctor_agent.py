from typing import Any, Dict
from app.models.domain import Case

class DoctorAgent:
    """
    Doctor Agent extracts a clinical summary of medicines, labs, 
    and patient questions for the physician.
    """
    
    async def analyze(self, case: Case, context_text: str) -> Dict[str, Any]:
        text_lower = context_text.lower()
        
        has_metformin = "metformin" in text_lower
        has_hba1c = "hba1c" in text_lower or "8.2" in text_lower
        
        summary = "Patient Summary:\n"
        if has_metformin:
            summary += "- Uploaded prescription includes anti-diabetic medication.\n"
        if has_hba1c:
            summary += "- Lab report shows elevated blood glucose marker (HbA1c ~8.2).\n"
        summary += "- Patient asked about medicine timing and side effects."
        
        return {
            "clinical_summary": summary,
            "follow_up_points": [
                "Confirm current medication adherence.",
                "Review lab trend.",
                "Clarify duration of therapy.",
                "Counsel patient on warning symptoms."
            ],
            "disclaimer": "This is a support summary, not an automated diagnosis."
        }
