from datetime import datetime, timezone
import uuid
from typing import Optional

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.postgres import Base

def generate_uuid():
    return str(uuid.uuid4())

class DrugMaster(Base):
    __tablename__ = "drug_master"

    id = Column(String, primary_key=True, default=generate_uuid)
    brand_name = Column(String, index=True)
    generic_name = Column(String, index=True)
    composition = Column(String, index=True)
    strength = Column(String)
    dosage_form = Column(String)
    route = Column(String)
    manufacturer = Column(String, index=True)
    schedule_category = Column(String)
    is_prescription_required = Column(Boolean, default=False)
    is_high_risk = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    drug_id = Column(String, ForeignKey("drug_master.id"))
    location_id = Column(String, index=True)
    state = Column(String)
    quantity_on_hand = Column(Integer, default=0)
    reorder_threshold = Column(Integer, default=10)
    batch_number = Column(String, index=True)
    expiry_date = Column(DateTime)
    supplier_name = Column(String)
    supplier_license_number = Column(String)
    purchase_invoice_number = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class PriceRecord(Base):
    __tablename__ = "price_records"

    id = Column(String, primary_key=True, default=generate_uuid)
    drug_id = Column(String, ForeignKey("drug_master.id"), nullable=True)
    brand_name = Column(String, index=True)
    generic_name = Column(String, index=True)
    composition = Column(String, index=True)
    strength = Column(String)
    dosage_form = Column(String)
    pack_size = Column(String)
    mrp = Column(Float)
    ceiling_price = Column(Float, nullable=True)
    source = Column(String)
    source_url = Column(String, nullable=True)
    last_checked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class JanAushadhiProduct(Base):
    __tablename__ = "jan_aushadhi_products"

    id = Column(String, primary_key=True, default=generate_uuid)
    generic_name = Column(String, index=True)
    composition = Column(String, index=True)
    strength = Column(String)
    dosage_form = Column(String)
    pack_size = Column(String)
    janaushadhi_price = Column(Float)
    availability_status = Column(String)
    source = Column(String)
    source_url = Column(String, nullable=True)
    last_checked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class DrugScheduleRule(Base):
    __tablename__ = "drug_schedule_rules"

    id = Column(String, primary_key=True, default=generate_uuid)
    drug_name = Column(String, index=True, nullable=True)
    composition = Column(String, index=True)
    schedule_category = Column(String)
    requires_prescription = Column(Boolean, default=False)
    requires_sales_register = Column(Boolean, default=False)
    requires_special_storage = Column(Boolean, default=False)
    rule_summary = Column(String)
    source = Column(String)
    source_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class NSQAlert(Base):
    __tablename__ = "nsq_alerts"

    id = Column(String, primary_key=True, default=generate_uuid)
    drug_name = Column(String, index=True)
    brand_name = Column(String, index=True)
    composition = Column(String)
    manufacturer = Column(String, index=True)
    batch_number = Column(String, index=True)
    test_lab = Column(String)
    reporting_source = Column(String)
    month = Column(String)
    year = Column(Integer)
    failure_reason = Column(String)
    alert_type = Column(String) # NSQ, SPURIOUS, RECALL, QUALITY_ALERT
    source = Column(String)
    source_url = Column(String, nullable=True)
    raw_payload_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(String, primary_key=True, default=generate_uuid)
    supplier_name = Column(String, index=True)
    seller_type = Column(String)
    license_number = Column(String, index=True, nullable=True)
    state = Column(String)
    address = Column(String, nullable=True)
    verification_status = Column(String)
    risk_score = Column(Float, default=0.0)
    risk_reasons_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class SchemeRule(Base):
    __tablename__ = "scheme_rules"

    id = Column(String, primary_key=True, default=generate_uuid)
    scheme_name = Column(String, index=True)
    scheme_type = Column(String)
    eligibility_summary = Column(String)
    coverage_summary = Column(String)
    required_documents_json = Column(JSON, default=dict)
    applies_to_retail_pharmacy = Column(Boolean, default=False)
    applies_to_hospitalization = Column(Boolean, default=False)
    source = Column(String)
    source_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class PharmacyLocation(Base):
    __tablename__ = "pharmacy_locations"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)
    owner_user_id = Column(String, index=True)
    state = Column(String)
    city = Column(String)
    address = Column(String)
    license_number = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, index=True)
    role = Column(String)
    case_id = Column(String, index=True, nullable=True)
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(String, nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
