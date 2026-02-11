# ProctorBE - Online Proctoring Backend

A FastAPI backend for online exam proctoring with:
- JWT-based authentication
- Exam and session management
- Proctoring event logging
- Risk scoring
- Computer-vision frame analysis hooks

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT (`python-jose`)
- Password hashing (`passlib[bcrypt]`)
- OpenCV + MediaPipe (for `/cv/analyze-frame`)

## Project Structure

```text
.
├── main.py
├── config.py
├── database.py
├── models.py
├── schemas.py
├── auth.py
├── routes/
│   ├── auth.py
│   ├── exams.py
│   ├── sessions.py
│   ├── events.py
│   ├── admin.py
│   └── cv.py
└── services/
    ├── scoring.py
    └── cv_engine.py
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv python-jose passlib[bcrypt] python-multipart email-validator opencv-python mediapipe numpy
```

3. Set environment variables (recommended in `.env`):

```env
DATABASE_URL=postgresql://localhost/proctoring_db
JWT_SECRET=CHANGE_THIS_IN_PROD
```

4. Run the server:

```bash
uvicorn main:app --reload
```

5. Open API docs:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Authentication

- Register with `/auth/register`.
- Login with `/auth/login` to receive a bearer token.
- Send token in requests:

```http
Authorization: Bearer <access_token>
```

## API Reference

Base URL: `http://127.0.0.1:8000`

### Health

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | No | Health/status check |

### Authentication (`/auth`)

| Method | Endpoint | Auth | Body / Form | Description |
|---|---|---|---|---|
| POST | `/auth/register` | No | JSON: `email`, `password`, `role` (`student` or `admin`) | Create user |
| POST | `/auth/login` | No | Form: `username` (email), `password` | Get JWT token |

Example register body:

```json
{
  "email": "student@example.com",
  "password": "strong-password",
  "role": "student"
}
```

### Exams (`/exams`)

| Method | Endpoint | Auth | Params | Description |
|---|---|---|---|---|
| POST | `/exams/` | Admin | Query: `title`, optional `start_time`, optional `end_time` | Create exam |
| GET | `/exams/` | No | - | List all exams |

### Sessions (`/sessions`)

| Method | Endpoint | Auth | Params | Description |
|---|---|---|---|---|
| POST | `/sessions/start` | Student/Admin | Query: `exam_id` | Start exam session |
| POST | `/sessions/end` | Session owner | Query: `session_id` | End session and compute risk |

`/sessions/end` response includes:
- `risk_score` (numeric total)
- `risk_level` (`Low`, `Medium`, `High`)

### Proctoring Events (`/events`)

| Method | Endpoint | Auth | Params | Description |
|---|---|---|---|---|
| POST | `/events/` | Session owner | Query: `session_id`, `event_type`, `severity` | Log event for a session |

### Admin (`/admin`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/admin/sessions` | Admin | List all sessions |
| GET | `/admin/sessions/{session_id}/events` | Admin | List events for a session |

### Computer Vision (`/cv`)

| Method | Endpoint | Auth | Input | Description |
|---|---|---|---|---|
| POST | `/cv/analyze-frame` | Logged-in user | Multipart: `file` + query `session_id` | Analyze one frame and store detected events |

Detected event types can include:
- `NO_FRAME_RECEIVED`
- `INVALID_IMAGE`
- `NO_FACE`
- `MULTIPLE_FACES`
- `LOOKING_AWAY`

## Risk Scoring

Current event weights:
- `NO_FACE`: 2
- `MULTIPLE_FACES`: 4
- `LOOKING_AWAY`: 2
- `TAB_SWITCH`: 3
- Unknown event type defaults to weight `1`

Risk levels:
- `Low`: score `< 5`
- `Medium`: score `< 10`
- `High`: score `>= 10`

## Notes

- CORS currently allows `http://localhost:3000`.
- Database tables are auto-created on app startup (`Base.metadata.create_all`).
- `JWT_SECRET` falls back to a default if env var is missing; set a secure value in production.
- `postgres://` database URLs are normalized to `postgresql://` for SQLAlchemy compatibility.

## Deploy On Render

Use these settings in Render Web Service:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Runtime: Python `3.11.11` (also defined in `runtime.txt`)

Required environment variables:
- `DATABASE_URL` (from Render PostgreSQL)
- `JWT_SECRET` (long random secret)

Recommended:
- `PYTHON_VERSION=3.11.11` in Render env vars

## Render Build Troubleshooting

If build fails, check Render logs for one of these common signatures:

1. `No matching distribution found for mediapipe`
   - Cause: wrong Python version (usually 3.12/3.13).
   - Fix: use Python 3.11.11 (`runtime.txt` + `PYTHON_VERSION`).

2. `Failed building wheel for ...` (OpenCV-related)
   - Cause: GUI OpenCV package in headless Linux.
   - Fix: use `opencv-python-headless` (already set in `requirements.txt`).

3. App starts but crashes with DB URL errors
   - Cause: `postgres://` URL format.
   - Fix: URL normalization is now handled in `config.py`.
