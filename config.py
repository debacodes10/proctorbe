import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from dotenv import load_dotenv

load_dotenv()

def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

def _parse_origins(raw: str) -> list[str]:
    origins = []
    for part in raw.split(","):
        origin = part.strip().rstrip("/")
        if origin:
            origins.append(origin)
    return origins

def _normalize_database_url(raw_url: str) -> str:
    # Render can provide postgres:// URLs; SQLAlchemy expects postgresql://
    db_url = raw_url
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # Render Postgres requires SSL. Auto-add sslmode=require if missing.
    # This preserves existing query params and avoids overriding explicit sslmode.
    if os.getenv("RENDER", "").lower() == "true" and db_url.startswith("postgresql://"):
        parts = urlsplit(db_url)
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        if "sslmode" not in query:
            query["sslmode"] = "require"
            db_url = urlunsplit(
                (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
            )

    return db_url

DATABASE_URL = _normalize_database_url(_require_env("DATABASE_URL"))

JWT_SECRET = _require_env("JWT_SECRET")
JWT_ALGORITHM = "HS256"

CORS_ORIGINS = _parse_origins(
    os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,https://proctorfe.vercel.app",
    )
)
