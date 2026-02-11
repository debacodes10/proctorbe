from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import ExamSession, ProctoringEvent
from auth import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/sessions")
def all_sessions(
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    return db.query(ExamSession).all()

@router.get("/sessions/{session_id}/events")
def session_events(
    session_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    return db.query(ProctoringEvent).filter(
        ProctoringEvent.session_id == session_id
    ).all()
