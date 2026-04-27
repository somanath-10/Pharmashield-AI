from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional, Any, Dict

from app.models.domain import UserDocument, DocumentTypeEnum, Case
from app.services.documents.validator import validate_document_upload
from app.services.documents.parser import extract_text_from_file
from app.api.deps import get_current_active_user
from app.models.domain import User
from app.services.rag.ingestion import ingest_document

router = APIRouter(prefix="/api/cases", tags=["documents"])

@router.post("/{case_id}/documents")
async def upload_real_document(
    case_id: str, 
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    # 1. Verify case
    target_case = await Case.find_one(Case.case_id == case_id)
    if not target_case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if target_case.user_id != current_user.user_id and current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to upload to this case")
        
    # 2. Validate file
    validate_document_upload(file)
    
    # 3. Extract text
    try:
        text = await extract_text_from_file(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse document: {str(e)}")
        
    # 4. Save initial document record
    doc = UserDocument(
        case_id=case_id,
        user_id=target_case.user_id,
        document_type=DocumentTypeEnum.OTHER, # will be updated by classifier
        file_name=file.filename,
        mime_type=file.content_type,
    )
    await doc.insert()
    
    # 5. RAG Ingestion pipeline
    result = await ingest_document(doc, text)
    return result
