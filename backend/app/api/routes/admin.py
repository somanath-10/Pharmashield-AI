"""
Admin Analytics Route — aggregated case and risk analytics for the admin dashboard.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from app.models.domain import (
    Case, Feedback, AgentRun, User, RoleEnum, RiskLevelEnum, CaseStatusEnum, 
    DataSourceSyncStatus, ADRReport, BatchVerification, PriceComplianceCheck,
    SellerRiskAssessment
)
from app.api.deps import get_current_admin
from app.services.audit import get_audit_logs

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/analytics")
async def get_analytics(current_user: User = Depends(get_current_admin)) -> Dict[str, Any]:
    """Aggregated analytics for admin dashboard."""
    all_cases = await Case.find_all().to_list()
    total = len(all_cases)
    patient_cases = sum(1 for c in all_cases if c.role.value == "PATIENT")
    doctor_cases = sum(1 for c in all_cases if c.role.value == "DOCTOR")
    pharmacist_cases = sum(1 for c in all_cases if c.role.value == "PHARMACIST")
    admin_cases = sum(1 for c in all_cases if c.role.value == "ADMIN")

    high_risk = sum(1 for c in all_cases if c.risk_level in ("HIGH", "CRITICAL"))
    medium_risk = sum(1 for c in all_cases if c.risk_level == "MEDIUM")

    # Agent-run breakdown
    all_runs = await AgentRun.find_all().to_list()
    agent_counts: Dict[str, int] = {}
    for run in all_runs:
        agents = run.input_json.get("agents_run", [run.agent_name])
        for ag in agents:
            agent_counts[ag] = agent_counts.get(ag, 0) + 1

    # Intelligence metrics from domain models
    nsq_matches = await BatchVerification.find(BatchVerification.is_quarantined == True).count()
    online_seller_risk = await SellerRiskAssessment.find(SellerRiskAssessment.risk_level.in_(["HIGH", "CRITICAL"])).count()
    compliance_warnings = agent_counts.get("prescription_compliance_agent", 0)
    affordability_requests = await PriceComplianceCheck.find(PriceComplianceCheck.is_overcharged == True).count()

    # Feedback
    all_feedback = await Feedback.find_all().to_list()
    avg_rating = (sum(f.rating for f in all_feedback) / len(all_feedback)) if all_feedback else None

    audit_logs = await get_audit_logs(limit=20)

    return {
        "total_cases": total,
        "patient_cases": patient_cases,
        "doctor_cases": doctor_cases,
        "pharmacist_cases": pharmacist_cases,
        "admin_cases": admin_cases,
        "high_risk_cases": high_risk,
        "medium_risk_cases": medium_risk,
        "nsq_matches": nsq_matches,
        "online_seller_risk_cases": online_seller_risk,
        "prescription_compliance_warnings": compliance_warnings,
        "affordability_requests": affordability_requests,
        "agent_run_breakdown": agent_counts,
        "average_feedback_rating": avg_rating,
        "recent_audit_logs": audit_logs[:10],
    }


@router.get("/audit-logs")
async def get_audit_log_entries(limit: int = 50, current_user: User = Depends(get_current_admin)) -> Dict[str, Any]:
    logs = await get_audit_logs(limit=limit)
    return {"count": len(logs), "logs": logs}


@router.get("/risk-queues")
async def get_risk_queues(current_user: User = Depends(get_current_admin)) -> Dict[str, Any]:
    """Return grouped risk queues for the admin command centre."""
    all_cases = await Case.find_all().to_list()

    def _serialize(c: Case) -> Dict[str, Any]:
        return {
            "case_id": c.case_id,
            "title": c.title,
            "risk_level": c.risk_level,
            "status": c.status.value if hasattr(c.status, "value") else c.status,
            "role": c.role.value,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }

    high_risk_raw = [c for c in all_cases if c.risk_level in ("HIGH", "CRITICAL")]
    needs_review_raw = [c for c in all_cases if c.status == CaseStatusEnum.NEEDS_REVIEW]
    pharmacist_reviewed_raw = [c for c in all_cases if c.status == CaseStatusEnum.PHARMACIST_REVIEWED]
    escalated_raw = [c for c in all_cases if c.status == CaseStatusEnum.ESCALATED]

    # Deduplicate: if a case is in multiple queues (e.g. HIGH risk and NEEDS_REVIEW), prioritize status-based queues
    high_risk_ids = {c.case_id for c in high_risk_raw}
    status_case_ids = {c.case_id for c in needs_review_raw + pharmacist_reviewed_raw + escalated_raw}
    
    # Only show in high_risk if NOT in a status-specific queue
    high_risk = [_serialize(c) for c in high_risk_raw if c.case_id not in status_case_ids]
    needs_review = [_serialize(c) for c in needs_review_raw]
    pharmacist_reviewed = [_serialize(c) for c in pharmacist_reviewed_raw]
    escalated = [_serialize(c) for c in escalated_raw]

    # Fetch real counts for the other queues
    adr_pending = await ADRReport.find(ADRReport.status == "NEEDS_DOCTOR_REVIEW").count()
    batch_quarantine = await BatchVerification.find(BatchVerification.is_quarantined == True).count()
    price_issues = await PriceComplianceCheck.find(PriceComplianceCheck.is_overcharged == True).count()

    return {
        "high_risk_cases": high_risk,
        "needs_review": needs_review,
        "pharmacist_reviewed": pharmacist_reviewed,
        "escalated": escalated,
        "adr_pending_count": adr_pending,
        "batch_quarantine_count": batch_quarantine,
        "price_issues_count": price_issues,
    }


@router.get("/analytics/batches")
async def get_batch_analytics(current_user: User = Depends(get_current_admin)) -> Dict[str, Any]:
    """Batch-level analytics from real verification records."""
    all_verifications = await BatchVerification.find_all().to_list()
    quarantined = [v for v in all_verifications if v.is_quarantined]
    
    # Group by manufacturer
    mfr_counts: Dict[str, int] = {}
    for v in quarantined:
        mfr = v.manufacturer or "Unknown"
        mfr_counts[mfr] = mfr_counts.get(mfr, 0) + 1

    return {
        "total_checked": len(all_verifications),
        "total_quarantined": len(quarantined),
        "high_risk": sum(1 for v in all_verifications if v.risk_level == RiskLevelEnum.HIGH),
        "by_manufacturer": mfr_counts,
        "flagged_batches": [v.batch_number for v in quarantined],
    }


@router.get("/analytics/sellers")
async def get_seller_analytics(current_user: User = Depends(get_current_admin)) -> Dict[str, Any]:
    """Seller-level risk analytics from real assessments."""
    all_assessments = await SellerRiskAssessment.find_all().to_list()
    high_risk = [a for a in all_assessments if a.risk_level in ("HIGH", "CRITICAL")]
    
    return {
        "total_seller_checks": len(all_assessments),
        "high_risk_count": len(high_risk),
        "flagged_sellers": list(set(a.seller_name for a in high_risk if a.seller_name)),
    }


@router.get("/analytics/prices")
async def get_price_analytics(current_user: User = Depends(get_current_admin)) -> Dict[str, Any]:
    """Price compliance analytics from real check records."""
    all_checks = await PriceComplianceCheck.find_all().to_list()
    overcharged = [c for c in all_checks if c.is_overcharged]
    return {
        "total_price_checks": len(all_checks),
        "overcharged_count": len(overcharged),
        "affordability_flags": len(overcharged), # Simplification for demo
    }


@router.get("/adr-monitoring")
async def get_adr_monitoring(current_user: User = Depends(get_current_admin)) -> Dict[str, Any]:
    """ADR report monitoring summary and report list."""
    all_adrs = await ADRReport.find_all().to_list()
    
    return {
        "summary": {
            "total_adr_reports": len(all_adrs),
            "pending_doctor_review": sum(1 for a in all_adrs if a.status == "NEEDS_DOCTOR_REVIEW"),
            "reviewed": sum(1 for a in all_adrs if a.status == "REVIEWED"),
        },
        "reports": [
            {
                "adr_id": a.adr_id,
                "medicine_name": a.medicine_name,
                "reaction": a.reaction,
                "severity": a.severity,
                "timeline": a.timeline,
                "status": a.status,
                "batch_number": a.batch_number,
                "patient_age_range": a.patient_age_range,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in all_adrs
        ]
    }


@router.get("/data-sources")
async def get_data_sources(current_user: User = Depends(get_current_admin)) -> List[Dict[str, Any]]:
    """Status of external data source adapters, backed by DataSourceSyncStatus model."""
    # Ensure seed records exist for known sources
    SEED_SOURCES = [
        {"source_name": "NSQ_SPURIOUS", "status": "MOCK_MODE", "note": "Seed data active. Connect CDSCO API for live data."},
        {"source_name": "NPPA_PRICE", "status": "MOCK_MODE", "note": "Mock price adapter active. Connect NPPA portal for live data."},
        {"source_name": "JAN_AUSHADHI", "status": "MOCK_MODE", "note": "Static seed list active. Connect Jan Aushadhi API for live updates."},
        {"source_name": "PVPI_ADR", "status": "NOT_CONNECTED", "note": "Pending external integration with PvPI/CDSCO."},
        {"source_name": "QDRANT_VECTOR_STORE", "status": "MEMORY_MODE", "note": "Running in-memory. Set QDRANT_URL to a persistent instance for production."},
    ]
    for seed in SEED_SOURCES:
        existing = await DataSourceSyncStatus.find_one(DataSourceSyncStatus.source_name == seed["source_name"])
        if not existing:
            await DataSourceSyncStatus(**seed).insert()

    all_sources = await DataSourceSyncStatus.find_all().to_list()
    return [
        {
            "source_name": s.source_name,
            "status": s.status,
            "last_synced": s.last_synced.isoformat() if s.last_synced else None,
            "records_loaded": s.records_loaded,
            "note": s.note,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        }
        for s in all_sources
    ]


@router.get("/model-quality")
async def get_model_quality(current_user: User = Depends(get_current_admin)) -> Dict[str, Any]:
    """AI model quality telemetry from feedback and agent runs."""
    all_runs = await AgentRun.find_all().to_list()
    all_feedback = await Feedback.find_all().to_list()

    total_runs = len(all_runs)
    avg_rating = (sum(f.rating for f in all_feedback) / len(all_feedback)) if all_feedback else None
    low_confidence = sum(1 for f in all_feedback if f.rating and f.rating <= 2)

    return {
        "total_ai_analyses": total_runs,
        "total_human_feedback": len(all_feedback),
        "average_feedback_rating": round(avg_rating, 2) if avg_rating else None,
        "low_confidence_flags": low_confidence,
        "agent_breakdown": {
            name: count for name, count in
            _count_agents(all_runs).items()
        },
        "note": "False positive / negative tracking requires pharmacist correction workflow (Phase 5).",
    }


def _count_agents(runs: list) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for run in runs:
        for ag in run.input_json.get("agents_run", [run.agent_name]):
            counts[ag] = counts.get(ag, 0) + 1
    return counts
