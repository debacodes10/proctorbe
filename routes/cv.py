from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user
from models import ProctoringEvent
from services.cv_engine import analyze_frame

router = APIRouter(prefix="/cv", tags=["Computer Vision"])

@router.post("/analyze-frame")
async def analyze_frame_api(
    session_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    image_bytes = await file.read()
    events = analyze_frame(image_bytes, session_id)

    stored = []

    for event_type, severity in events:
        ev = ProctoringEvent(
            session_id=session_id,
            event_type=event_type,
            severity=severity
        )
        db.add(ev)
        stored.append(event_type)

    db.commit()

    return {
        "events_detected": stored
    }
