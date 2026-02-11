# backend/config.py

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://localhost/proctoring_db"
)

JWT_SECRET = "CHANGE_THIS_IN_PROD"
JWT_ALGORITHM = "HS256"
