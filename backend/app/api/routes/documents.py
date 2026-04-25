from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.models.domain import UserDocument, DocumentTypeEnum, Case
from app.schemas.case import DocumentUploadResponse

router = APIRouter(prefix="/api/cases", tags=["documents"])

class MockUploadRequest(BaseModel):
    document_type: DocumentTypeEnum
    file_name: str
    mock_extracted_text: str

@router.post("/{case_id}/documents", response_model=DocumentUploadResponse)
async def upload_mock_document(case_id: str, request: MockUploadRequest) -> DocumentUploadResponse:
    # 1. Verify case
    target_case = await Case.find_one(Case.case_id == case_id)
    if not target_case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    # 2. Save document record
    doc = UserDocument(
        case_id=case_id,
        user_id=target_case.user_id,
        document_type=request.document_type,
        file_name=request.file_name,
        text_content=request.mock_extracted_text
    )
    await doc.insert()
    
    return DocumentUploadResponse(
        document_id=doc.document_id,
        file_name=doc.file_name,
        status="MOCK_UPLOADED",
        extracted_text_preview=doc.text_content[:100] + "..." if doc.text_content else None
    )
