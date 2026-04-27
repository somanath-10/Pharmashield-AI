"""
Admin Analytics Route — aggregated case and risk analytics for the admin dashboard.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from app.models.domain import Case, Feedback, AgentRun, User, RoleEnum, RiskLevelEnum, CaseStatusEnum
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

    nsq_matches = agent_counts.get("nsq_spurious_agent", 0)
    online_seller_risk = agent_counts.get("online_seller_risk_agent", 0)
    compliance_warnings = agent_counts.get("prescription_compliance_agent", 0)
    affordability_requests = agent_counts.get("price_janaushadhi_agent", 0)

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

    high_risk = [_serialize(c) for c in all_cases if c.risk_level in ("HIGH", "CRITICAL")]
    needs_review = [_serialize(c) for c in all_cases if hasattr(c.status, "value") and c.status == CaseStatusEnum.NEEDS_REVIEW]
    pending_pharmacist = [_serialize(c) for c in all_cases if hasattr(c.status, "value") and c.status == CaseStatusEnum.PHARMACIST_REVIEWED]
    escalated = [_serialize(c) for c in all_cases if hasattr(c.status, "value") and c.status == CaseStatusEnum.ESCALATED]

    return {
        "high_risk_cases": high_risk,
        "needs_review": needs_review,
        "pending_pharmacist_review": pending_pharmacist,
        "escalated": escalated,
        "adr_pending": [],   # Populated when ADRReport model is extended
        "batch_quarantine": [],  # Populated when BatchVerification model is extended
        "price_issues": [],      # Populated when PriceComplianceCheck model is extended
    }


@router.get("/analytics/batches")
async def get_batch_analytics(current_user: User = Depends(get_current_admin)) -> Dict[str, Any]:
    """Batch-level analytics aggregated from case metadata."""
    all_runs = await AgentRun.find_all().to_list()
    nsq_cases = [r for r in all_runs if "nsq_spurious_agent" in r.input_json.get("agents_run", [])]
    return {
        "total_batch_checks": len(nsq_cases),
        "flagged_batches": [
            r.output_json.get("batch_number", "Unknown")
            for r in nsq_cases
            if r.output_json.get("risk_level") in ("HIGH", "CRITICAL")
        ],
        # TODO: Connect to BatchVerification documents when model is seeded
        "note": "Batch analytics shown from agent run history. Seed BatchVerification records for full detail.",
    }


@router.get("/analytics/sellers")
async def get_seller_analytics(current_user: User = Depends(get_current_admin)) -> Dict[str, Any]:
    """Seller-level risk analytics."""
    all_runs = await AgentRun.find_all().to_list()
    seller_cases = [r for r in all_runs if "online_seller_risk_agent" in r.input_json.get("agents_run", [])]
    return {
        "total_seller_risk_checks": len(seller_cases),
        "high_risk_seller_cases": sum(
            1 for r in seller_cases if r.output_json.get("risk_level") in ("HIGH", "CRITICAL")
        ),
        "note": "Seller analytics from agent run history. SellerRiskAssessment model seeding pending.",
    }


@router.get("/analytics/prices")
async def get_price_analytics(current_user: User = Depends(get_current_admin)) -> Dict[str, Any]:
    """Price compliance analytics."""
    all_runs = await AgentRun.find_all().to_list()
    price_cases = [r for r in all_runs if "price_janaushadhi_agent" in r.input_json.get("agents_run", [])]
    return {
        "total_price_checks": len(price_cases),
        "affordability_flags": sum(
            1 for r in price_cases if r.output_json.get("risk_level") in ("MEDIUM", "HIGH", "CRITICAL")
        ),
        "note": "Price analytics sourced from agent run history. NPPA adapter integration pending.",
    }


@router.get("/adr-monitoring")
async def get_adr_monitoring(current_user: User = Depends(get_current_admin)) -> Dict[str, Any]:
    """ADR report monitoring summary."""
    # TODO: Query ADRReport documents when pharmacist ADR draft workflow populates them
    return {
        "total_adr_drafts": 0,
        "pending_doctor_review": 0,
        "submitted_externally": 0,
        "note": "ADR monitoring active. Pharmacist ADR drafts will appear here when submitted.",
    }


@router.get("/data-sources")
async def get_data_sources(current_user: User = Depends(get_current_admin)) -> List[Dict[str, Any]]:
    """Status of external data source adapters."""
    return [
        {"name": "NSQ / Spurious Drug Dataset", "status": "MOCK_MODE", "last_synced": None, "note": "Seed data active. Connect CDSCO API for live data."},
        {"name": "NPPA / DPCO Price Dataset", "status": "MOCK_MODE", "last_synced": None, "note": "Mock price adapter active. Connect NPPA portal for live data."},
        {"name": "Jan Aushadhi Generic Directory", "status": "MOCK_MODE", "last_synced": None, "note": "Static seed list active. Connect Jan Aushadhi API for live updates."},
        {"name": "PvPI / ADR Reports (CDSCO)", "status": "NOT_CONNECTED", "last_synced": None, "note": "Pending external integration."},
        {"name": "Qdrant Vector Store", "status": "MEMORY_MODE", "last_synced": None, "note": "Running in-memory. Connect a persistent Qdrant instance for production."},
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
