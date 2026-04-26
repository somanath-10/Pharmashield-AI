from typing import Any, Dict, List
from app.models.domain import Case


class PharmacistAgent:
    """
    Pharmacist Agent checks prescription rules, availability, and alternatives using RAG.
    Phase 3: incorporates compliance, NSQ, price, seller, and inventory intel.
    """

    async def analyze(
        self,
        case: Case,
        retrieved_chunks: List[Dict[str, Any]],
        intel_results: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        medicines = []
        for chunk in retrieved_chunks:
            payload = chunk.get("payload", {})
            chunk_type = payload.get("chunk_type", "")
            text = payload.get("chunk_text", "").lower()
            if chunk_type == "medicine" or any(m in text for m in ["amoxicillin", "augmentin", "metformin", "paracetamol"]):
                name = payload.get("medicine_name") or payload.get("section_title") or "Prescribed Medicine"
                medicines.append(name)

        medicines = list(set(medicines))

        # Aggregate intel findings
        compliance_warnings: List[str] = []
        nsq_warnings: List[str] = []
        stock_status: List[str] = []
        price_guidance: List[str] = []
        seller_risk: List[str] = []
        all_actions: List[str] = []
        overall_risk = "LOW"
        risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}

        for ir in (intel_results or []):
            agent = ir.get("agent", "")
            rl = ir.get("risk_level", "LOW")
            if risk_order.get(rl, 0) > risk_order.get(overall_risk, 0):
                overall_risk = rl
            all_actions.extend(ir.get("actions", []))

            if "compliance" in agent:
                compliance_warnings.extend(ir.get("findings", []))
            elif "nsq" in agent:
                nsq_warnings.extend(ir.get("findings", []))
            elif "inventory" in agent:
                stock_status.extend(ir.get("findings", []))
            elif "price" in agent or "janaushadhi" in agent:
                price_guidance.extend(ir.get("findings", []))
            elif "seller" in agent:
                seller_risk.extend(ir.get("red_flags", ir.get("findings", [])))

        return {
            "prescription_summary": "Review of case documents for dispensing support.",
            "medicines_found": medicines,
            "compliance_warnings": compliance_warnings or ["Verify prescription validity before dispensing."],
            "nsq_batch_status": nsq_warnings or ["No NSQ alerts found for provided details."],
            "stock_status": stock_status or ["Stock status not available — check manually."],
            "price_and_generic_guidance": price_guidance or ["Verify MRP with NPPA Pharma Sahi Daam."],
            "online_seller_risk": seller_risk or [],
            "substitution_caution": "Do not change molecule, strength, route, or dosage form without pharmacist or prescriber review.",
            "patient_counseling_points": [
                "Complete the full antibiotic course if prescribed.",
                "Take medicines as directed — with or without food as specified.",
                "Report allergy symptoms immediately.",
                "Buy only from licensed pharmacy; avoid unverified online sellers.",
            ],
            "action_plan": list(dict.fromkeys(all_actions)),  # deduplicated
            "intel_risk_level": overall_risk,
            "pharmacist_review_required": "Pharmacist review required before dispensing, substitution, or patient-specific action.",
        }
