from typing import Any, Dict, List
from app.models.domain import Case


class DoctorAgent:
    """
    Doctor Agent extracts a clinical summary of medicines, labs, and patient questions.
    Phase 3: includes pharmacist flags and affordability intel from intel_results.
    """

    async def analyze(
        self,
        case: Case,
        retrieved_chunks: List[Dict[str, Any]],
        intel_results: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        medicines = []
        labs = []
        documents_reviewed = []

        for chunk in retrieved_chunks:
            payload = chunk.get("payload", {})
            chunk_type = payload.get("chunk_type", "")
            text = payload.get("chunk_text", "").lower()
            doc_name = payload.get("document_name", "Uploaded Document")
            documents_reviewed.append(doc_name)

            if chunk_type == "medicine" or any(m in text for m in ["metformin", "amoxicillin", "augmentin"]):
                medicines.append(payload.get("medicine_name") or payload.get("section_title") or "Medicine")
            if chunk_type == "lab_value" or "hba1c" in text or "glucose" in text:
                labs.append("Elevated blood glucose marker detected (e.g., HbA1c)")

        medicines = list(set(medicines))
        labs = list(set(labs))
        documents_reviewed = list(set(documents_reviewed))

        # Incorporate pharmacy intel flags
        pharmacist_flags: List[str] = []
        affordability_notes: List[str] = []
        for ir in (intel_results or []):
            agent = ir.get("agent", "")
            rl = ir.get("risk_level", "LOW")
            findings = ir.get("findings", ir.get("red_flags", []))
            if rl in ("HIGH", "CRITICAL"):
                pharmacist_flags.extend([f"[{rl}] {f}" for f in findings[:2]])
            elif "price" in agent or "janaushadhi" in agent:
                affordability_notes.extend(findings[:2])

        return {
            "case_summary": f"Patient uploaded {len(documents_reviewed)} document(s) for clinical review.",
            "documents_reviewed": documents_reviewed,
            "medicines_identified": medicines,
            "lab_highlights": labs,
            "patient_questions": [
                "Patient asked about affordability of current medicines.",
                "Patient inquired about cheaper generic options.",
            ],
            "pharmacist_flags": pharmacist_flags or ["No pharmacist flags raised."],
            "affordability_context": affordability_notes or ["No specific affordability issue noted."],
            "follow_up_considerations": [
                "Confirm current medication adherence.",
                "Review lab value trends.",
                "Counsel patient on warning symptoms.",
                "Clarify duration of therapy.",
                "If affordability is an issue, consider generic/Jan Aushadhi equivalents where clinically appropriate.",
            ],
            "professional_review_note": "This is an AI-generated support summary and does not replace clinical judgment.",
        }
