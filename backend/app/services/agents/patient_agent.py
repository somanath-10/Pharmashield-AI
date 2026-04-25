from typing import Any, Dict
from app.models.domain import Case

class PatientAgent:
    """
    Patient Agent explains prescriptions and lab reports in simple language.
    It strictly adheres to safety disclaimers and avoids diagnosing.
    """
    
    async def analyze(self, case: Case, context_text: str) -> Dict[str, Any]:
        # MVP Mock Extraction Logic
        medicines = []
        lab_values = []
        
        text_lower = context_text.lower()
        if "metformin" in text_lower:
            medicines.append({
                "name": "Metformin",
                "purpose": "Commonly used for blood sugar control.",
                "instruction": "Take it only as written by your doctor. Do not change the dose yourself."
            })
        if "amoxicillin" in text_lower or "augmentin" in text_lower:
            medicines.append({
                "name": "Amoxicillin / Augmentin",
                "purpose": "Antibiotic used to treat bacterial infections.",
                "instruction": "Complete the full course even if you feel better."
            })
            
        if "hba1c" in text_lower or "8.2" in text_lower:
            lab_values.append({
                "test": "HbA1c",
                "value": "8.2%",
                "explanation": "This is a blood sugar control marker. Your doctor should review whether your current treatment plan needs adjustment."
            })

        has_meds = len(medicines) > 0
        has_labs = len(lab_values) > 0
        
        summary = "Your uploaded documents mention "
        if has_meds and has_labs:
            summary += "diabetes-related treatment and a blood sugar marker called HbA1c."
        elif has_meds:
            summary += "prescribed medicines."
        elif has_labs:
            summary += "lab test results."
        else:
            summary += "general health information."

        return {
            "summary": summary,
            "medicines_found": medicines,
            "lab_values_found": lab_values,
            "warning_signs": [
                "Seek medical help if you have severe weakness, confusion, fainting, breathing difficulty, or very high/low sugar symptoms."
            ],
            "questions_to_ask_doctor": [
                "What should be my target levels?",
                "Should I change diet or exercise plan?",
                "How long should I continue this medicine?",
                "When should I repeat the test?"
            ],
            "disclaimer": "This explanation is for understanding only. It is not a diagnosis or prescription. Please consult your doctor or pharmacist before making any medical decision."
        }
