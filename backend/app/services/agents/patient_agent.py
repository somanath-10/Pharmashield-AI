from typing import Any, Dict, List
from app.models.domain import Case

class PatientAgent:
    """
    Patient Agent explains prescriptions and lab reports in simple language using RAG.
    """
    
    async def analyze(self, case: Case, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        medicines = []
        lab_values = []
        
        # Simple mock RAG processing
        for chunk in retrieved_chunks:
            payload = chunk.get("payload", {})
            chunk_type = payload.get("chunk_type")
            text = payload.get("chunk_text", "").lower()
            
            if chunk_type == "medicine" or "metformin" in text or "amoxicillin" in text:
                medicines.append(payload.get("medicine_name", "Prescribed Medicine"))
            if chunk_type == "lab_value" or "hba1c" in text:
                lab_values.append(payload.get("test_name", "Lab Test"))
                
        has_meds = len(medicines) > 0
        has_labs = len(lab_values) > 0
        
        simple_summary = "Based on your uploaded documents, we found "
        if has_meds and has_labs:
            simple_summary += "information about medicines and lab test results."
        elif has_meds:
            simple_summary += "information about your medicines."
        elif has_labs:
            simple_summary += "information about your lab tests."
        else:
            simple_summary += "general health information."
            
        return {
            "simple_summary": simple_summary,
            "medicines_found": list(set(medicines)),
            "lab_values_found": list(set(lab_values)),
            "what_this_may_mean": "The documents indicate your current treatment or health status as prescribed by your doctor.",
            "warning_signs": [
                "Seek medical help if you experience severe side effects or unexpected symptoms."
            ],
            "questions_to_ask_doctor": [
                "Are my current readings normal?",
                "Do I need to change my medicine dosage?"
            ],
            "safe_next_steps": [
                "Continue following your doctor's advice.",
                "Do not stop or change any medicines without consulting your doctor."
            ],
            "disclaimer": "This explanation is for understanding only. It is not a diagnosis or prescription. Please consult your doctor or pharmacist before making any medical decision."
        }
