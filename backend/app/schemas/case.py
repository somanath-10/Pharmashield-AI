from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field

from app.models.domain import RoleEnum, CaseTypeEnum

class CaseCreateRequest(BaseModel):
    role: RoleEnum
    case_type: CaseTypeEnum
    title: str
    query: str

class CaseRecordResponse(BaseModel):
    case_id: str
    user_id: str
    role: RoleEnum
    case_type: CaseTypeEnum
    status: str
    title: str
    query: str
    risk_level: Optional[str] = None
    final_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class CaseAnalyzeResponse(BaseModel):
    case_id: str
    status: str
    result: Dict[str, Any]

class DocumentUploadResponse(BaseModel):
    document_id: str
    file_name: str
    status: str
    extracted_text_preview: Optional[str] = None
