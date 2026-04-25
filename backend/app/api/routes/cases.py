import json
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException

from app.models.domain import Case, RoleEnum, UserDocument, AgentRun
from app.schemas.case import (
    CaseCreateRequest,
    CaseRecordResponse,
    CaseAnalyzeResponse,
    DocumentUploadResponse
)
from app.services.agents.patient_agent import PatientAgent
from app.services.agents.pharmacist_agent import PharmacistAgent
from app.services.agents.doctor_agent import DoctorAgent
from app.services.agents.admin_agent import AdminAgent

router = APIRouter(prefix="/api/cases", tags=["cases"])

@router.post("", response_model=CaseRecordResponse)
async def create_case(request: CaseCreateRequest) -> CaseRecordResponse:
    # Dummy user_id for MVP
    new_case = Case(
        user_id="mock_user_123",
        role=request.role,
        case_type=request.case_type,
        title=request.title,
        query=request.query
    )
    await new_case.insert()
    return CaseRecordResponse.model_validate(new_case.model_dump())

@router.get("", response_model=List[CaseRecordResponse])
async def list_cases() -> List[CaseRecordResponse]:
    cases = await Case.find_all().to_list()
    return [CaseRecordResponse.model_validate(c.model_dump()) for c in cases]

@router.get("/{case_id}", response_model=CaseRecordResponse)
async def get_case(case_id: str) -> CaseRecordResponse:
    case = await Case.find_one(Case.case_id == case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseRecordResponse.model_validate(case.model_dump())

from app.services.rag.retriever import hybrid_retrieve
from app.services.rag.citation_verifier import build_citations
from app.services.guardrails.output_validator import validate_role_output
from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    role: str

@router.post("/{case_id}/search")
async def search_documents(case_id: str, request: SearchRequest):
    target_case = await Case.find_one(Case.case_id == case_id)
    if not target_case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    chunks = await hybrid_retrieve(request.query, case_id, request.role)
    citations = build_citations(chunks)
    return {"results": citations}

@router.post("/{case_id}/analyze")
async def analyze_case(case_id: str) -> Dict[str, Any]: # Changed return type for dynamic dict
    target_case = await Case.find_one(Case.case_id == case_id)
    if not target_case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # 1. Retrieve RAG chunks based on case query
    retrieved_chunks = await hybrid_retrieve(target_case.query, case_id, target_case.role.value)
    
    # 2. Build citations
    citations = build_citations(retrieved_chunks)
    
    result_data = {}
    
    if target_case.role == RoleEnum.PATIENT:
        agent = PatientAgent()
        result_data = await agent.analyze(target_case, retrieved_chunks)
    elif target_case.role == RoleEnum.PHARMACIST:
        agent = PharmacistAgent()
        result_data = await agent.analyze(target_case, retrieved_chunks)
    elif target_case.role == RoleEnum.DOCTOR:
        agent = DoctorAgent()
        result_data = await agent.analyze(target_case, retrieved_chunks)
    else:
        raise HTTPException(status_code=400, detail="Unknown role workflow")
        
    # 3. Apply Guardrails
    result_data = validate_role_output(target_case.role.value, result_data)
    
    # Create the AgentRun trace
    run = AgentRun(
        case_id=case_id,
        agent_name=f"{target_case.role.value}_AGENT",
        role=target_case.role.value,
        input_json={"query": target_case.query},
        output_json=result_data
    )
    await run.insert()
    
    # Update the final case
    target_case.status = "COMPLETED"
    target_case.final_summary = json.dumps(result_data)
    await target_case.save()
    
    return {
        "case_id": case_id,
        "role": target_case.role.value,
        "status": "COMPLETED",
        "answer": result_data,
        "citations": citations
    }
