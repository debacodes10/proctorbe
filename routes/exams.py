from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import Exam
from auth import require_admin

from typing import Optional

router = APIRouter(prefix="/exams", tags=["Exams"])

@router.post("/")
def create_exam(
    title: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    exam = Exam(
        title=title,
        start_time=start_time,
        end_time=end_time
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam

@router.get("/")
def list_exams(db: Session = Depends(get_db)):
    return db.query(Exam).all()
