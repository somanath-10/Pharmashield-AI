"""
Memory Store — stores and retrieves workflow preferences per pharmacy location/role.
Uses MongoDB (Beanie) for flexibility.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from beanie import Document
from pydantic import BaseModel, Field
import uuid

logger = logging.getLogger(__name__)


def uuid_str() -> str:
    return str(uuid.uuid4())


class MemoryEntry(Document):
    memory_id: str = Field(default_factory=uuid_str)
    scope: str  # PHARMACY_LOCATION, USER, SYSTEM
    role: str
    memory_type: str  # workflow_preference, correction, alert_preference
    key: str  # e.g. "HYD_STORE_001::budget_sensitive"
    value_json: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.8
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "memory_entries"


async def store_memory(scope: str, role: str, memory_type: str, key: str, value: Dict[str, Any], confidence: float = 0.8) -> MemoryEntry:
    """Upsert a memory entry."""
    existing = await MemoryEntry.find_one(MemoryEntry.key == key)
    if existing:
        existing.value_json = value
        existing.confidence = confidence
        existing.updated_at = datetime.now(timezone.utc)
        await existing.save()
        return existing
    entry = MemoryEntry(scope=scope, role=role, memory_type=memory_type, key=key, value_json=value, confidence=confidence)
    await entry.insert()
    return entry


async def retrieve_memory(key: str) -> Optional[Dict[str, Any]]:
    """Retrieve a memory entry by key."""
    entry = await MemoryEntry.find_one(MemoryEntry.key == key)
    if entry:
        return entry.value_json
    return None


async def retrieve_memories_for_scope(scope: str, role: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve all memories for a given scope+role."""
    entries = await MemoryEntry.find(MemoryEntry.scope == scope, MemoryEntry.role == role).limit(limit).to_list()
    return [{"key": e.key, "value": e.value_json, "confidence": e.confidence} for e in entries]
