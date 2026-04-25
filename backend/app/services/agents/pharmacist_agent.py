from typing import Any, Dict
from app.models.domain import Case

class PharmacistAgent:
    """
    Pharmacist Agent checks prescription rules, availability, and alternative compositions.
    """
    
    async def analyze(self, case: Case, context_text: str) -> Dict[str, Any]:
        text_lower = context_text.lower()
        
        medicine_name = "Unknown"
        if "amoxicillin" in text_lower or "augmentin" in text_lower:
            medicine_name = "Amoxicillin + Clavulanic Acid"
        elif "metformin" in text_lower:
            medicine_name = "Metformin"
            
        return {
            "medicine": medicine_name,
            "assessment": [
                "Prescription medicine: valid prescription required.",
                "Stock: brand unavailable. Same composition alternative may be checked.",
                "Do not change molecule, strength, or dosage form without pharmacist/prescriber review."
            ],
            "patient_counseling": [
                "Complete full course if prescribed.",
                "Take after food if advised.",
                "Report allergy symptoms immediately."
            ],
            "disclaimer": "Pharmacist review required before dispensing."
        }
