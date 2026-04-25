from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, utcnow


def uuid_str() -> str:
    return str(uuid.uuid4())


class Drug(TimestampMixin, Base):
    __tablename__ = "drugs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    brand_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    generic_name: Mapped[str] = mapped_column(String(255), index=True)
    composition: Mapped[str | None] = mapped_column(String(255), nullable=True)
    strength: Mapped[str | None] = mapped_column(String(100), nullable=True)
    dosage_form: Mapped[str | None] = mapped_column(String(100), nullable=True)
    route: Mapped[str | None] = mapped_column(String(100), nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    schedule_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_prescription_required: Mapped[bool] = mapped_column(Boolean, default=False)
    is_high_risk: Mapped[bool] = mapped_column(Boolean, default=False)


class InventoryItem(TimestampMixin, Base):
    __tablename__ = "inventory_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    drug_id: Mapped[str | None] = mapped_column(ForeignKey("drugs.id"), nullable=True)
    location_id: Mapped[str] = mapped_column(String(255), index=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    quantity_on_hand: Mapped[int] = mapped_column(Integer, default=0)
    reorder_threshold: Mapped[int | None] = mapped_column(Integer, nullable=True)
    batch_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    supplier_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    supplier_license_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    purchase_invoice_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    drug: Mapped[Drug | None] = relationship()


class PriceRecord(TimestampMixin, Base):
    __tablename__ = "price_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    drug_id: Mapped[str | None] = mapped_column(ForeignKey("drugs.id"), nullable=True)
    brand_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    generic_name: Mapped[str] = mapped_column(String(255), index=True)
    composition: Mapped[str | None] = mapped_column(String(255), nullable=True)
    strength: Mapped[str | None] = mapped_column(String(100), nullable=True)
    dosage_form: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mrp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ceiling_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class JanAushadhiProduct(TimestampMixin, Base):
    __tablename__ = "janaushadhi_products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    generic_name: Mapped[str] = mapped_column(String(255), index=True)
    composition: Mapped[str | None] = mapped_column(String(255), nullable=True)
    strength: Mapped[str | None] = mapped_column(String(100), nullable=True)
    dosage_form: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pack_size: Mapped[str | None] = mapped_column(String(100), nullable=True)
    janaushadhi_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    availability_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DrugScheduleRule(TimestampMixin, Base):
    __tablename__ = "drug_schedule_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    schedule_category: Mapped[str] = mapped_column(String(100), index=True)
    drug_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    composition: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rule_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    requires_prescription: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_sales_register: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_special_storage: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)


class NSQAlert(TimestampMixin, Base):
    __tablename__ = "nsq_alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    drug_name: Mapped[str] = mapped_column(String(255), index=True)
    brand_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    composition: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    batch_number: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    test_lab: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reporting_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    month: Mapped[str | None] = mapped_column(String(50), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    alert_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_payload_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class Supplier(TimestampMixin, Base):
    __tablename__ = "suppliers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    supplier_name: Mapped[str] = mapped_column(String(255), index=True)
    seller_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    license_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_reasons_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class SchemeRule(TimestampMixin, Base):
    __tablename__ = "scheme_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    scheme_name: Mapped[str] = mapped_column(String(255), index=True)
    scheme_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    eligibility_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    coverage_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_documents_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    applies_to_retail_pharmacy: Mapped[bool] = mapped_column(Boolean, default=False)
    applies_to_hospitalization: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)


class PharmacyCase(TimestampMixin, Base):
    __tablename__ = "pharmacy_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    case_type: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(100), default="pending")
    patient_hash: Mapped[str] = mapped_column(String(64), index=True)
    drug_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    brand_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location_state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    case_input_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    final_risk_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    final_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    pharmacist_review_required: Mapped[bool] = mapped_column(Boolean, default=True)

    agent_runs: Mapped[list[AgentRun]] = relationship(back_populates="case")
    feedback_items: Mapped[list[Feedback]] = relationship(back_populates="case")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    case_id: Mapped[str] = mapped_column(ForeignKey("pharmacy_cases.id"), index=True)
    agent_name: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    input_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    output_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    case: Mapped[PharmacyCase] = relationship(back_populates="agent_runs")


class EvidenceChunk(TimestampMixin, Base):
    __tablename__ = "evidence_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    source_type: Mapped[str] = mapped_column(String(255), index=True)
    source_name: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    document_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    section_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    chunk_text: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    embedding_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    case_id: Mapped[str] = mapped_column(ForeignKey("pharmacy_cases.id"), index=True)
    agent_name: Mapped[str] = mapped_column(String(255))
    user_role: Mapped[str] = mapped_column(String(255), default="pharmacist")
    rating: Mapped[int] = mapped_column(Integer)
    feedback_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    correction_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    case: Mapped[PharmacyCase] = relationship(back_populates="feedback_items")


class MemoryItem(TimestampMixin, Base):
    __tablename__ = "memory_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    memory_type: Mapped[str] = mapped_column(String(255), index=True)
    scope: Mapped[str] = mapped_column(String(255), index=True)
    key: Mapped[str] = mapped_column(String(255), index=True)
    value_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
