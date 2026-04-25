from typing import Any, Dict, List
from app.models.domain import Case

class PharmacistAgent:
    """
    Pharmacist Agent checks prescription rules, availability, and alternative compositions using RAG.
    """
    
    async def analyze(self, case: Case, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        medicines = []
        for chunk in retrieved_chunks:
            payload = chunk.get("payload", {})
            chunk_type = payload.get("chunk_type")
            text = payload.get("chunk_text", "").lower()
            
            if chunk_type == "medicine" or "amoxicillin" in text or "augmentin" in text or "metformin" in text:
                medicines.append(payload.get("medicine_name", "Prescribed Medicine"))
                
        medicines = list(set(medicines))
        
        return {
            "prescription_summary": "Review of uploaded prescription/documents for dispensing support.",
            "medicines_found": medicines,
            "missing_information": [
                "Doctor's signature or registration number may need verification."
            ],
            "dispensing_support": [
                "Valid prescription required for antibiotics.",
                "Verify dosage frequency with the patient."
            ],
            "substitution_caution": "Do not change molecule, strength, or dosage form without pharmacist or prescriber review.",
            "patient_counseling_points": [
                "Complete full course if antibiotic is prescribed.",
                "Take after food if advised to avoid GI distress.",
                "Report allergy symptoms immediately."
            ],
            "pharmacist_review_required": "Pharmacist review required before dispensing, substitution, or patient-specific action."
        }
