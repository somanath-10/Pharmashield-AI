from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.orm import Session

from app.schemas.case import CaseAnalyzeRequest
from app.services.rag.retriever import HybridRetriever


class BaseAgent(ABC):
    def __init__(self, db: Session, retriever: HybridRetriever | None = None) -> None:
        self.db = db
        self.retriever = retriever or HybridRetriever()

    @abstractmethod
    async def run(self, request: CaseAnalyzeRequest, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError
