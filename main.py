import os
import time
import logging
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from database import engine
from models import Base
from routes import auth as auth_routes
from routes import exams, sessions, events, admin, cv
from fastapi.middleware.cors import CORSMiddleware
from config import CORS_ORIGINS

app = FastAPI(title="Online Proctoring Backend")
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_db_init() -> None:
    retries = int(os.getenv("DB_CONNECT_RETRIES", "20"))
    delay_seconds = float(os.getenv("DB_CONNECT_RETRY_DELAY", "2"))
    max_delay_seconds = float(os.getenv("DB_CONNECT_MAX_RETRY_DELAY", "10"))
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            Base.metadata.create_all(bind=engine)
            logger.info("Database connectivity check passed on attempt %s/%s", attempt, retries)
            return
        except OperationalError as exc:
            last_error = exc
            logger.warning(
                "Database startup check failed on attempt %s/%s: %s",
                attempt,
                retries,
                repr(exc),
            )
            if attempt < retries:
                time.sleep(delay_seconds)
                delay_seconds = min(delay_seconds * 1.5, max_delay_seconds)
                continue

    raise RuntimeError(
        "Database connection failed during startup after "
        f"{retries} attempts. Last error: {last_error!r}"
    ) from last_error

app.include_router(auth_routes.router)
app.include_router(exams.router)
app.include_router(sessions.router)
app.include_router(events.router)
app.include_router(admin.router)
app.include_router(cv.router)

@app.get("/")
def root():
    return {"status": "Backend running"}
