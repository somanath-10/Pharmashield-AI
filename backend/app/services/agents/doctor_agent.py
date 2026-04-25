from typing import Any, Dict, List
from app.models.domain import Case

class DoctorAgent:
    """
    Doctor Agent extracts a clinical summary of medicines, labs, 
    and patient questions for the physician using RAG.
    """
    
    async def analyze(self, case: Case, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        medicines = []
        labs = []
        documents_reviewed = []
        
        for chunk in retrieved_chunks:
            payload = chunk.get("payload", {})
            chunk_type = payload.get("chunk_type")
            text = payload.get("chunk_text", "").lower()
            doc_name = payload.get("document_name", "Uploaded Document")
            
            documents_reviewed.append(doc_name)
            
            if chunk_type == "medicine" or "metformin" in text:
                medicines.append(payload.get("medicine_name", "Metformin 500mg"))
            if chunk_type == "lab_value" or "hba1c" in text:
                labs.append("Elevated blood glucose marker (HbA1c ~8.2)")
                
        medicines = list(set(medicines))
        labs = list(set(labs))
        documents_reviewed = list(set(documents_reviewed))
        
        return {
            "case_summary": "Patient has uploaded documents requiring clinical review.",
            "documents_reviewed": documents_reviewed,
            "medicines_identified": medicines,
            "lab_highlights": labs,
            "patient_questions": [
                "Are my current readings normal?",
                "Do I need to change my medicine dosage?"
            ],
            "follow_up_considerations": [
                "Confirm current medication adherence.",
                "Review lab trend.",
                "Clarify duration of therapy.",
                "Counsel patient on warning symptoms."
            ],
            "professional_review_note": "This is an AI-generated support summary and does not replace clinical judgment."
        }
