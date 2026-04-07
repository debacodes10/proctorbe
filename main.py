import os
import time
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_db_init() -> None:
    retries = int(os.getenv("DB_CONNECT_RETRIES", "5"))
    delay_seconds = float(os.getenv("DB_CONNECT_RETRY_DELAY", "2"))
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(delay_seconds)
                continue

    raise RuntimeError(
        "Database connection failed during startup. Verify DATABASE_URL and SSL settings "
        "(Render usually needs sslmode=require)."
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
