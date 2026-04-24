from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models import MemoryItem
from app.db.session import get_db

router = APIRouter(prefix="/api/memory", tags=["memory"])


@router.get("")
def list_memory(db: Session = Depends(get_db)) -> list[dict]:
    return [item.as_dict() for item in db.query(MemoryItem).order_by(MemoryItem.updated_at.desc()).all()]
