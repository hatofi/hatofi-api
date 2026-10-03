import os

from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./hatofi.db",
)
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "development-only-change-this-secret-key",
)
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "240"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "production").strip().lower()