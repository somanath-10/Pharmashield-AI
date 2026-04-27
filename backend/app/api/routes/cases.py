"""
Case Routes — Phase 3 orchestrated analysis with specialized India intelligence agents.
"""
from __future__ import annotations
import json
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.models.domain import Case, RoleEnum, UserDocument, AgentRun, User, SellerRiskAssessment
from app.api.deps import get_current_active_user
from app.schemas.case import CaseCreateRequest, CaseRecordResponse, CaseAnalyzeResponse, DocumentUploadResponse
from app.services.agents.patient_agent import PatientAgent
from app.services.agents.pharmacist_agent import PharmacistAgent
from app.services.agents.doctor_agent import DoctorAgent
from app.services.agents.admin_agent import AdminAgent
from app.services.agents.price_agent import PriceJanAushadhiAgent
from app.services.agents.compliance_agent import PrescriptionComplianceAgent
from app.services.agents.nsq_agent import NSQSuriousAgent
from app.services.agents.seller_risk_agent import OnlineSellerRiskAgent
from app.services.agents.scheme_agent import SchemeClaimAgent
from app.services.agents.inventory_agent import InventoryBatchAgent
from app.services.rag.retriever import hybrid_retrieve
from app.services.rag.citation_verifier import build_citations
from app.services.guardrails.output_validator import validate_role_output
from app.services.audit import record_audit_log

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.post("", response_model=CaseRecordResponse)
async def create_case(
    request: CaseCreateRequest,
    current_user: User = Depends(get_current_active_user)
) -> CaseRecordResponse:
    if request.role != current_user.role and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Cannot create case for another role")

    new_case = Case(
        user_id=current_user.user_id,
        role=current_user.role if current_user.role != RoleEnum.ADMIN else request.role,
        case_type=request.case_type,
        title=request.title,
        query=request.query
    )
    await new_case.insert()
    await record_audit_log(current_user.user_id, request.role.value, "CREATE_CASE", "case", case_id=new_case.case_id)
    return CaseRecordResponse.model_validate(new_case.model_dump())


@router.get("", response_model=List[CaseRecordResponse])
async def list_cases(current_user: User = Depends(get_current_active_user)) -> List[CaseRecordResponse]:
    # In production, we'd filter cases by role, e.g., if patient, only show their cases. 
    # If admin, show all. For MVP, we filter if they are patient, doctor or pharmacist, but admin sees all.
    query = {}
    if current_user.role != RoleEnum.ADMIN:
        query["user_id"] = current_user.user_id
    cases = await Case.find(query).to_list()
    return [CaseRecordResponse.model_validate(c.model_dump()) for c in cases]


@router.get("/{case_id}", response_model=CaseRecordResponse)
async def get_case(case_id: str, current_user: User = Depends(get_current_active_user)) -> CaseRecordResponse:
    case = await Case.find_one(Case.case_id == case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case.user_id != current_user.user_id and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    return CaseRecordResponse.model_validate(case.model_dump())


class SearchRequest(BaseModel):
    query: str
    role: str


@router.post("/{case_id}/search")
async def search_documents(case_id: str, request: SearchRequest, current_user: User = Depends(get_current_active_user)):
    target_case = await Case.find_one(Case.case_id == case_id)
    if not target_case:
        raise HTTPException(status_code=404, detail="Case not found")
    if target_case.user_id != current_user.user_id and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    chunks = await hybrid_retrieve(request.query, case_id, request.role)
    citations = build_citations(chunks)
    return {"results": citations}


class AnalyzeRequest(BaseModel):
    role: Optional[str] = None
    question: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@router.post("/{case_id}/analyze")
async def analyze_case(case_id: str, request: Optional[AnalyzeRequest] = None, current_user: User = Depends(get_current_active_user)) -> Dict[str, Any]:
    target_case = await Case.find_one(Case.case_id == case_id)
    if not target_case:
        raise HTTPException(status_code=404, detail="Case not found")
    if target_case.user_id != current_user.user_id and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    ctx = (request.context or {}) if request else {}
    query = (request.question or target_case.query) if request else target_case.query

    # 1. Retrieve RAG chunks
    retrieved_chunks = await hybrid_retrieve(query, case_id, target_case.role.value)
    citations = build_citations(retrieved_chunks)

    # 2. Run specialized India intelligence agents based on context flags
    intel_results: List[Dict[str, Any]] = []
    agents_run: List[str] = []
    overall_risk = "LOW"

    risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}

    def escalate_risk(current: str, new: str) -> str:
        return new if risk_order.get(new, 0) > risk_order.get(current, 0) else current

    drug_name = ctx.get("drug_name", "")

    # --- Price / Jan Aushadhi Agent ---
    if ctx.get("budget_sensitive") or "cheaper" in query.lower() or "generic" in query.lower() or "jan aushadhi" in query.lower():
        price_agent = PriceJanAushadhiAgent()
        price_result = await price_agent.run(
            drug_name=drug_name,
            composition=ctx.get("composition"),
            mrp=ctx.get("mrp"),
            patient_budget_sensitive=ctx.get("budget_sensitive", False),
        )
        intel_results.append(price_result)
        agents_run.append("price_janaushadhi_agent")
        overall_risk = escalate_risk(overall_risk, price_result["risk_level"])

    # --- Prescription Compliance Agent ---
    if drug_name or "prescription" in query.lower() or "schedule" in query.lower() or "dispense" in query.lower():
        compliance_agent = PrescriptionComplianceAgent()
        compliance_result = await compliance_agent.run(
            medicine_name=drug_name,
            composition=ctx.get("composition"),
            prescription_available=ctx.get("prescription_available", True),
            claim_text=ctx.get("claim_text"),
        )
        intel_results.append(compliance_result)
        agents_run.append("prescription_compliance_agent")
        overall_risk = escalate_risk(overall_risk, compliance_result["risk_level"])

    # --- NSQ / Spurious Agent ---
    if ctx.get("batch_number") or ctx.get("manufacturer") or "nsq" in query.lower() or "batch" in query.lower() or "spurious" in query.lower():
        nsq_agent = NSQSuriousAgent()
        nsq_result = await nsq_agent.run(
            drug_name=drug_name,
            brand_name=ctx.get("brand_name"),
            manufacturer=ctx.get("manufacturer"),
            batch_number=ctx.get("batch_number"),
            composition=ctx.get("composition"),
        )
        intel_results.append(nsq_result)
        agents_run.append("nsq_spurious_agent")
        overall_risk = escalate_risk(overall_risk, nsq_result["risk_level"])

    # --- Online Seller Risk Agent ---
    if ctx.get("seller_type") or "whatsapp" in query.lower() or "online" in query.lower() or "instagram" in query.lower():
        seller_agent = OnlineSellerRiskAgent()
        seller_result = await seller_agent.run(
            seller_name=ctx.get("seller_name"),
            seller_type=ctx.get("seller_type"),
            claim_text=ctx.get("claim_text"),
            license_number=ctx.get("license_number"),
            batch_number=ctx.get("batch_number"),
            manufacturer=ctx.get("manufacturer"),
            mrp=ctx.get("mrp"),
        )
        intel_results.append(seller_result)
        agents_run.append("online_seller_risk_agent")
        overall_risk = escalate_risk(overall_risk, seller_result["risk_level"])
        
        # Persist assessment for admin analytics
        assessment = SellerRiskAssessment(
            case_id=case_id,
            seller_name=ctx.get("seller_name"),
            seller_type=ctx.get("seller_type") or "Unknown",
            license_present=ctx.get("license_number") is not None,
            invoice_present=ctx.get("invoice_present", False),
            risk_score=seller_result.get("risk_score", 0.0),
            risk_level=seller_result["risk_level"],
            explanation=seller_result.get("explanation", "Seller risk check performed."),
            next_step=seller_result.get("next_step", "Verify documentation.")
        )
        await assessment.insert()

    # --- Scheme / Claim Agent ---
    if "ayushman" in query.lower() or "pm-jay" in query.lower() or "cghs" in query.lower() or "esic" in query.lower() or ctx.get("scheme_name"):
        scheme_agent = SchemeClaimAgent()
        scheme_result = await scheme_agent.run(
            scheme_name=ctx.get("scheme_name"),
            hospitalized=ctx.get("hospitalized", False),
            purchase_context=ctx.get("purchase_context", "retail_pharmacy"),
        )
        intel_results.append(scheme_result)
        agents_run.append("scheme_claim_agent")

    # --- Inventory & Batch Agent ---
    if drug_name and (ctx.get("quantity_on_hand") is not None or "stock" in query.lower() or "available" in query.lower()):
        inv_agent = InventoryBatchAgent()
        inv_result = await inv_agent.run(
            drug_name=drug_name,
            quantity_on_hand=ctx.get("quantity_on_hand"),
            batch_number=ctx.get("batch_number"),
            supplier_name=ctx.get("supplier_name"),
            location_id=ctx.get("location_id"),
        )
        intel_results.append(inv_result)
        agents_run.append("inventory_batch_agent")
        overall_risk = escalate_risk(overall_risk, inv_result["risk_level"])

    # 3. Role-based agent synthesis
    result_data: Dict[str, Any] = {}
    role_agent_name = f"{target_case.role.value}_AGENT"

    if target_case.role == RoleEnum.PATIENT:
        agent = PatientAgent()
        result_data = await agent.analyze(target_case, retrieved_chunks, intel_results, query=query)
    elif target_case.role == RoleEnum.PHARMACIST:
        agent = PharmacistAgent()
        result_data = await agent.analyze(target_case, retrieved_chunks, intel_results, query=query)
    elif target_case.role == RoleEnum.DOCTOR:
        agent = DoctorAgent()
        result_data = await agent.analyze(target_case, retrieved_chunks, intel_results)
    elif target_case.role == RoleEnum.ADMIN:
        agent = AdminAgent()
        result_data = await agent.analyze(target_case, retrieved_chunks)
    else:
        raise HTTPException(status_code=400, detail="Unknown role")

    # 4. Merge intelligence results into response
    action_plan: List[str] = []
    intel_findings: List[str] = []
    for ir in intel_results:
        intel_findings.extend(ir.get("findings", ir.get("red_flags", [])))
        action_plan.extend(ir.get("actions", []))

    # 5. Guardrails
    result_data = validate_role_output(target_case.role.value, result_data)

    # 6. Persist
    run = AgentRun(
        case_id=case_id,
        agent_name=role_agent_name,
        role=target_case.role.value,
        input_json={"query": query, "agents_run": agents_run},
        output_json={**result_data, "intel_results": intel_results},
    )
    await run.insert()

    from app.models.domain import CaseStatusEnum
    if overall_risk in ("HIGH", "CRITICAL"):
        target_case.status = CaseStatusEnum.NEEDS_REVIEW
    else:
        target_case.status = CaseStatusEnum.ANALYZED
    target_case.risk_level = overall_risk
    target_case.final_summary = json.dumps(result_data)
    await target_case.save()

    await record_audit_log(
        target_case.user_id, target_case.role.value, "ANALYZE_CASE", "case",
        case_id=case_id, metadata={"agents_run": agents_run, "risk_level": overall_risk}
    )

    # Mandatory disclaimer per role
    disclaimers = {
        "PATIENT": "This explanation is for understanding only. It is not a diagnosis or prescription. Please consult your doctor or pharmacist before making any medical decision.",
        "PHARMACIST": "Pharmacist review required before dispensing, substitution, or patient-specific action.",
        "DOCTOR": "This is an AI-generated support summary and does not replace clinical judgment.",
        "ADMIN": "Analytics and risk data shown are AI-generated. Verify with clinical and regulatory teams.",
    }

    return {
        "case_id": case_id,
        "role": target_case.role.value,
        "risk_level": overall_risk,
        "status": target_case.status.value,
        "agents_run": agents_run,
        "answer": result_data,
        "intel_findings": intel_findings,
        "action_plan": action_plan,
        "citations": citations,
        "mandatory_disclaimer": disclaimers.get(target_case.role.value, ""),
    }
