from __future__ import annotations

from sqlalchemy.orm import Session

from app.schemas.case import CaseAnalyzeRequest
from app.services.memory.store import MemoryStore


class MemoryAgent:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.store = MemoryStore()

    async def retrieve_relevant_memory(self, request: CaseAnalyzeRequest) -> list[dict]:
        return self.store.get_relevant_memory(self.db, request)
