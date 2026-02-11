from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import ExamSession, Exam
from auth import get_current_user

from services.scoring import calculate_risk

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("/start")
def start_session(
    exam_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    session = ExamSession(
        user_id=user.id,
        exam_id=exam_id
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session

@router.post("/end")
def end_session(
    session_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    session = db.query(ExamSession).filter(ExamSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404)

    if session.user_id != user.id:
        raise HTTPException(status_code=403)

    session.end_time = datetime.utcnow()
    db.commit()

    score, level = calculate_risk(session_id, db)

    return {
        "message": "Session ended",
        "risk_score": score,
        "risk_level": level
    }
