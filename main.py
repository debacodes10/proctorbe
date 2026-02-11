from fastapi import FastAPI
from database import engine
from models import Base
from routes import auth as auth_routes
from routes import exams, sessions, events, admin, cv
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Online Proctoring Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://proctorfe.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_routes.router)
app.include_router(exams.router)
app.include_router(sessions.router)
app.include_router(events.router)
app.include_router(admin.router)
app.include_router(cv.router)

@app.get("/")
def root():
    return {"status": "Backend running"}
