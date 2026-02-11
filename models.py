# backend/models.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "student" or "admin"
    created_at = Column(DateTime, server_default=func.now())

    sessions = relationship("ExamSession", back_populates="user")


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)

    sessions = relationship("ExamSession", back_populates="exam")


class ExamSession(Base):
    __tablename__ = "exam_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exam_id = Column(Integer, ForeignKey("exams.id"))
    start_time = Column(DateTime, server_default=func.now())
    end_time = Column(DateTime)
    risk_score = Column(Integer, default=0)
    risk_level = Column(String, default="Low")

    user = relationship("User", back_populates="sessions")
    exam = relationship("Exam", back_populates="sessions")
    events = relationship("ProctoringEvent", back_populates="session")


class ProctoringEvent(Base):
    __tablename__ = "proctoring_events"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"))
    event_type = Column(String)
    severity = Column(Integer)
    timestamp = Column(DateTime, server_default=func.now())
    snapshot_path = Column(String, nullable=True)

    session = relationship("ExamSession", back_populates="events")
