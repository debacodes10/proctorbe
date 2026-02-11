from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import ProctoringEvent, ExamSession
from auth import get_current_user

router = APIRouter(prefix="/events", tags=["Proctoring Events"])

@router.post("/")
def log_event(
    session_id: int,
    event_type: str,
    severity: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    session = db.query(ExamSession).filter(ExamSession.id == session_id).first()
    if not session or session.user_id != user.id:
        return {"error": "Invalid session"}

    event = ProctoringEvent(
        session_id=session_id,
        event_type=event_type,
        severity=severity
    )

    db.add(event)
    db.commit()

    return {"message": "Event logged"}
