from sqlalchemy.orm import Session
from models import ProctoringEvent, ExamSession

WEIGHTS = {
    "NO_FACE": 2,
    "MULTIPLE_FACES": 4,
    "LOOKING_AWAY": 2,
    "TAB_SWITCH": 3
}


def calculate_risk(session_id: int, db: Session):
    events = db.query(ProctoringEvent).filter(
        ProctoringEvent.session_id == session_id
    ).all()

    score = 0
    for e in events:
        score += WEIGHTS.get(e.event_type, 1) * e.severity

    if score < 5:
        level = "Low"
    elif score < 10:
        level = "Medium"
    else:
        level = "High"

    session = db.query(ExamSession).filter(
        ExamSession.id == session_id
    ).first()

    session.risk_score = score
    session.risk_level = level

    db.commit()

    return score, level
