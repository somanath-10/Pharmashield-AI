from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.schemas.risk import RiskLevel


class Citation(BaseModel):
    id: str
    source_name: str
    source_url: str | None = None
    document_title: str | None = None
    section_title: str | None = None
    snippet: str
    source_type: str
    note: str | None = None


class Finding(BaseModel):
    title: str
    detail: str
    evidence_ids: list[str] = Field(default_factory=list)


class CriterionStatus(BaseModel):
    criterion: str
    status: str
    evidence: str | None = None


class AgentOutput(BaseModel):
    agent_name: str
    status: str = "completed"
    risk_level: RiskLevel
    findings: list[Finding] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    extra: dict[str, Any] = Field(default_factory=dict)
