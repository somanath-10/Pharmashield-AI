from typing import Any, Dict, List
from app.models.domain import Case


class PatientAgent:
    """
    Patient Agent explains prescriptions and lab reports in simple language using RAG.
    Phase 3: also incorporates price/scheme/seller intel findings into the response.
    """

    async def analyze(
        self,
        case: Case,
        retrieved_chunks: List[Dict[str, Any]],
        intel_results: List[Dict[str, Any]] | None = None,
        query: str = "",
    ) -> Dict[str, Any]:
        medicines = []
        lab_values = []
        relevant_context = []

        for chunk in retrieved_chunks:
            payload = chunk.get("payload", {})
            chunk_type = payload.get("chunk_type", "")
            text = payload.get("chunk_text", "").lower()
            
            # Simple keyword matching for relevance
            query_terms = [t.lower() for t in query.split() if len(t) > 3]
            if not query_terms or any(t in text for t in query_terms):
                relevant_context.append(payload.get("chunk_text", ""))

            if chunk_type == "medicine" or any(m in text for m in ["metformin", "amoxicillin", "augmentin", "paracetamol"]):
                medicine_name = payload.get("medicine_name") or payload.get("section_title") or "Prescribed Medicine"
                medicines.append(medicine_name)
            if chunk_type == "lab_value" or "hba1c" in text or "glucose" in text:
                lab_values.append(payload.get("test_name") or "Lab Test")

        medicines = list(set(medicines))
        lab_values = list(set(lab_values))

        # Summarise document content
        has_meds = len(medicines) > 0
        has_labs = len(lab_values) > 0
        
        # Synthesize answer from RAG chunks
        if relevant_context:
            rag_answer = f"Based on your documents: {relevant_context[0]}"
            if len(relevant_context) > 1:
                rag_answer += f" {relevant_context[1]}"
        else:
            rag_answer = "I couldn't find a specific answer in your documents. Please ensure the documents are clear and relevant to your question."

        if has_meds and has_labs:
            simple_summary = f"Your documents contain information about medicines ({', '.join(medicines[:3])}) and lab results ({', '.join(lab_values[:2])})."
        elif has_meds:
            simple_summary = f"Your documents contain information about your medicines: {', '.join(medicines[:3])}."
        elif has_labs:
            simple_summary = f"Your documents contain information about your lab tests: {', '.join(lab_values[:2])}."
        else:
            simple_summary = "Your documents were reviewed."

        # Incorporate Phase 3 intel
        affordability_note = ""
        scheme_note = ""
        seller_warning = ""
        intel_actions: List[str] = []

        for ir in (intel_results or []):
            agent = ir.get("agent", "")
            if "price" in agent or "janaushadhi" in agent:
                findings = ir.get("findings", [])
                ja_lines = [f for f in findings if "jan aushadhi" in f.lower() or "₹" in f]
                if ja_lines:
                    affordability_note = "; ".join(ja_lines[:2])
            elif "scheme" in agent:
                scheme_note = "; ".join(ir.get("findings", [])[:2])
            elif "seller" in agent:
                flags = ir.get("red_flags", [])
                if flags:
                    seller_warning = "WARNING: Online/WhatsApp seller risks detected. " + "; ".join(flags[:3])
            intel_actions.extend(ir.get("actions", []))

        return {
            "answer": rag_answer,
            "simple_summary": simple_summary,
            "medicines_found": medicines,
            "lab_values_found": lab_values,
            "affordability_guidance": affordability_note or "Ask your pharmacist about lower-cost same-composition options.",
            "scheme_guidance": scheme_note or "If you have a health scheme (PM-JAY/CGHS/ESIC), ask your pharmacist or hospital desk.",
            "seller_warning": seller_warning,
            "what_this_may_mean": "Your documents reflect your current treatment as prescribed by your doctor.",
            "warning_signs": [
                "Seek immediate medical help if you experience severe allergic reactions, difficulty breathing, or extreme side effects.",
            ],
            "questions_to_ask_doctor": [
                "Is my current medicine the most affordable option?",
                "Are my lab readings within target range?",
                "Do I need a follow-up test?",
            ],
            "safe_next_steps": [
                "Continue following your doctor's advice.",
                "Do not stop or change any medicine without consulting your doctor.",
                "Buy medicines only from a licensed pharmacy.",
            ],
            "intel_actions": intel_actions,
            "disclaimer": "This explanation is for understanding only. It is not a diagnosis or prescription. Please consult your doctor or pharmacist before making any medical decision.",
        }
