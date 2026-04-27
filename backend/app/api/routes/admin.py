"""
Admin Analytics Route — aggregated case and risk analytics for the admin dashboard.
"""
from __future__ import annotations
import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends
from app.models.domain import Case, Feedback, AgentRun, User
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
