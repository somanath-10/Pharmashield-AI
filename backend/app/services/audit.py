"""
Audit Log Service - records important actions to PostgreSQL AuditLog table.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from sqlalchemy import select
from app.db.postgres import async_session_maker
from app.models.postgres_models import AuditLog

logger = logging.getLogger(__name__)


async def record_audit_log(
    user_id: str,
    role: str,
    action: str,
    entity_type: str,
    case_id: Optional[str] = None,
    entity_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Write an audit log entry to PostgreSQL."""
    try:
        async with async_session_maker() as session:
            log = AuditLog(
                user_id=user_id,
                role=role,
                case_id=case_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                metadata_json=metadata or {},
            )
            session.add(log)
            await session.commit()
    except Exception as e:
        logger.error(f"Failed to record audit log: {e}")


async def get_audit_logs(limit: int = 100) -> list[Dict[str, Any]]:
    """Retrieve recent audit logs."""
    try:
        async with async_session_maker() as session:
            result = await session.execute(
                select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
            )
            logs = result.scalars().all()
            return [
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "role": log.role,
                    "case_id": log.case_id,
                    "action": log.action,
                    "entity_type": log.entity_type,
                    "entity_id": log.entity_id,
                    "metadata": log.metadata_json,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in logs
            ]
    except Exception as e:
        logger.error(f"Failed to retrieve audit logs: {e}")
        return []
