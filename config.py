import os
from dotenv import load_dotenv

load_dotenv()

def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


DATABASE_URL = _require_env("DATABASE_URL")

# Render can provide postgres:// URLs; SQLAlchemy expects postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

JWT_SECRET = _require_env("JWT_SECRET")
JWT_ALGORITHM = "HS256"
