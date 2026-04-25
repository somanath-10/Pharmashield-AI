from enum import Enum
from typing import Any, List, Optional
from datetime import datetime, timezone
import uuid

from beanie import Document, Indexed
from pydantic import BaseModel, Field

def uuid_str() -> str:
    return str(uuid.uuid4())

class RoleEnum(str, Enum):
    PATIENT = "PATIENT"
    PHARMACIST = "PHARMACIST"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"

class CaseTypeEnum(str, Enum):
    PATIENT_REPORT_EXPLANATION = "PATIENT_REPORT_EXPLANATION"
    PATIENT_PRESCRIPTION_EXPLANATION = "PATIENT_PRESCRIPTION_EXPLANATION"
    PHARMACIST_DISPENSING_CHECK = "PHARMACIST_DISPENSING_CHECK"
    PHARMACIST_SUBSTITUTION_CHECK = "PHARMACIST_SUBSTITUTION_CHECK"
    DOCTOR_CASE_SUMMARY = "DOCTOR_CASE_SUMMARY"
    ADMIN_REVIEW = "ADMIN_REVIEW"

class DocumentTypeEnum(str, Enum):
    PRESCRIPTION = "PRESCRIPTION"
    LAB_REPORT = "LAB_REPORT"
    DISCHARGE_SUMMARY = "DISCHARGE_SUMMARY"
    INVOICE = "INVOICE"
    MEDICINE_PHOTO = "MEDICINE_PHOTO"
    PHARMACY_SOP = "PHARMACY_SOP"
    OTHER = "OTHER"

class FlagEnum(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"

class User(Document):
    user_id: Indexed(str) = Field(default_factory=uuid_str)
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: RoleEnum
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"

class Case(Document):
    case_id: Indexed(str) = Field(default_factory=uuid_str)
    user_id: Indexed(str)
    role: RoleEnum
    case_type: CaseTypeEnum
    status: str = "OPEN"
    title: str
    query: str
    risk_level: Optional[str] = None
    final_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "cases"

class UserDocument(Document):
    document_id: Indexed(str) = Field(default_factory=uuid_str)
    case_id: Indexed(str)
    user_id: Indexed(str)
    document_type: DocumentTypeEnum
    file_name: str
    file_url: Optional[str] = None
    file_path: Optional[str] = None
    mime_type: Optional[str] = None
    text_content: Optional[str] = None
    metadata_json: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "documents"

class DocumentChunk(Document):
    chunk_id: Indexed(str) = Field(default_factory=uuid_str)
    document_id: Indexed(str)
    case_id: Indexed(str)
    chunk_text: str
    chunk_type: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    metadata_json: dict = Field(default_factory=dict)
    qdrant_point_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "document_chunks"

class ExtractedMedicine(Document):
    medicine_id: Indexed(str) = Field(default_factory=uuid_str)
    case_id: Indexed(str)
    document_id: Optional[str] = None
    medicine_name: str
    composition: Optional[str] = None
    strength: Optional[str] = None
    dosage_form: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    instructions: Optional[str] = None
    confidence: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "extracted_medicines"

class ExtractedLabValue(Document):
    lab_value_id: Indexed(str) = Field(default_factory=uuid_str)
    case_id: Indexed(str)
    document_id: Optional[str] = None
    test_name: str
    test_value: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    flag: FlagEnum = FlagEnum.UNKNOWN
    confidence: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "extracted_lab_values"

class AgentRun(Document):
    run_id: Indexed(str) = Field(default_factory=uuid_str)
    case_id: Indexed(str)
    agent_name: str
    role: str
    input_json: dict = Field(default_factory=dict)
    output_json: dict = Field(default_factory=dict)
    status: str = "COMPLETED"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "agent_runs"

class Feedback(Document):
    feedback_id: Indexed(str) = Field(default_factory=uuid_str)
    case_id: Indexed(str)
    user_id: Indexed(str)
    role: str
    rating: int
    feedback_text: str
    correction_text: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "feedback"

class Citation(Document):
    citation_id: Indexed(str) = Field(default_factory=uuid_str)
    case_id: Indexed(str)
    agent_run_id: Optional[str] = None
    chunk_id: Indexed(str)
    document_id: Indexed(str)
    claim_text: Optional[str] = None
    source_snippet: str
    page_number: Optional[int] = None
    document_name: Optional[str] = None
    section_title: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "citations"
