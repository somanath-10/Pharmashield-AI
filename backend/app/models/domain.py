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

class RiskLevelEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"

class CaseStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    ANALYZED = "ANALYZED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    PHARMACIST_REVIEWED = "PHARMACIST_REVIEWED"
    DOCTOR_REVIEWED = "DOCTOR_REVIEWED"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"

class User(Document):
    user_id: Indexed(str) = Field(default_factory=uuid_str)
    name: str
    email: Optional[str] = None
    hashed_password: str = "placeholder_hashed_password" # For Phase 4 compliance
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
    status: CaseStatusEnum = CaseStatusEnum.DRAFT
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

class PrescriptionExtraction(Document):
    extraction_id: Indexed(str) = Field(default_factory=uuid_str)
    case_id: Indexed(str)
    document_id: Optional[str] = None
    doctor_name: Optional[str] = None
    registration_number: Optional[str] = None
    date: Optional[str] = None
    patient_name: Optional[str] = None
    has_signature: bool = False
    is_suspicious: bool = False
    suspicion_reasons: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "prescription_extractions"

class SellerRiskAssessment(Document):
    assessment_id: Indexed(str) = Field(default_factory=uuid_str)
    case_id: Indexed(str)
    seller_name: Optional[str] = None
    seller_type: str
    license_present: bool = False
    invoice_present: bool = False
    risk_score: float = 0.0
    risk_level: RiskLevelEnum = RiskLevelEnum.UNKNOWN
    explanation: str
    next_step: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "seller_risk_assessments"

class BatchVerification(Document):
    verification_id: Indexed(str) = Field(default_factory=uuid_str)
    case_id: Optional[Indexed(str)] = None
    medicine_name: str
    batch_number: str
    expiry_date: Optional[str] = None
    manufacturer: Optional[str] = None
    supplier: Optional[str] = None
    is_quarantined: bool = False
    quarantine_reason: Optional[str] = None
    risk_level: RiskLevelEnum = RiskLevelEnum.UNKNOWN
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "batch_verifications"

class PriceComplianceCheck(Document):
    check_id: Indexed(str) = Field(default_factory=uuid_str)
    case_id: Optional[Indexed(str)] = None
    medicine_name: str
    mrp: float
    charged_price: float
    is_overcharged: bool = False
    nppa_ceiling_price: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "price_compliance_checks"

class SubstitutionCheck(Document):
    check_id: Indexed(str) = Field(default_factory=uuid_str)
    case_id: Optional[Indexed(str)] = None
    prescribed_medicine: str
    substituted_medicine: str
    is_safe: bool = False
    mismatch_reasons: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "substitution_checks"

class ADRReport(Document):
    adr_id: Indexed(str) = Field(default_factory=uuid_str)
    case_id: Optional[Indexed(str)] = None
    patient_age_range: Optional[str] = None
    medicine_name: str
    batch_number: Optional[str] = None
    reaction: str
    severity: str
    timeline: str
    status: str = "DRAFT" # DRAFT, NEEDS_DOCTOR_REVIEW, SUBMITTED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "adr_reports"

class PharmacistReview(Document):
    review_id: Indexed(str) = Field(default_factory=uuid_str)
    case_id: Indexed(str)
    pharmacist_id: Indexed(str)
    action_taken: str
    notes: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "pharmacist_reviews"

class DoctorReview(Document):
    review_id: Indexed(str) = Field(default_factory=uuid_str)
    case_id: Indexed(str)
    doctor_id: Indexed(str)
    action_taken: str
    notes: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "doctor_reviews"

class DoctorPharmacistMessage(Document):
    message_id: Indexed(str) = Field(default_factory=uuid_str)
    case_id: Indexed(str)
    sender_id: Indexed(str)
    sender_role: RoleEnum
    receiver_id: Optional[str] = None
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "doctor_pharmacist_messages"

class VerifiedPrescription(Document):
    """Stores metadata for doctor-verified e-prescriptions to prevent fake prescription misuse."""
    verification_id: Indexed(str) = Field(default_factory=uuid_str)
    doctor_id: Indexed(str)
    patient_name: str
    patient_id: Optional[str] = None
    medicine_list: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    status: str = "ACTIVE"  # ACTIVE | REVOKED | EXPIRED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

    class Settings:
        name = "verified_prescriptions"

class DataSourceSyncStatus(Document):
    """Tracks the sync state of external data adapters (NPPA, NSQ, Jan Aushadhi, etc.)."""
    source_name: Indexed(str)  # e.g. "NSQ_SPURIOUS", "NPPA_PRICE", "JAN_AUSHADHI"
    status: str = "MOCK_MODE"  # CONNECTED | MOCK_MODE | FAILED | NOT_CONNECTED
    last_synced: Optional[datetime] = None
    records_loaded: Optional[int] = None
    error_message: Optional[str] = None
    note: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "data_source_sync_status"

class CareTeamLink(Document):
    """Links a doctor to a patient with consent status. Controls which patients a doctor can view."""
    link_id: Indexed(str) = Field(default_factory=uuid_str)
    patient_id: Indexed(str)
    doctor_id: Indexed(str)
    status: str = "ACTIVE"  # ACTIVE | REVOKED | PENDING
    consent_given_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "care_team_links"
