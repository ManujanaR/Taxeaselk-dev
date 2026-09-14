from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    PROJECT_NAME: str = "TaxEaseLK Backend API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    HOST: str = "127.0.0.1"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # No defaults for secrets: the app refuses to start without them.
    DATABASE_URL: str
    SECRET_KEY: str
    GEMINI_API_KEY: str = ""  # optional; extraction endpoint returns 503 when unset
    GEMINI_MODEL: str = "gemini-3.8-flash"

    # Optional: store uploads in Supabase Storage instead of UPLOAD_DIR
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_BUCKET: str = "taxease-files"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_BYTES: int = 10 * 1024 * 1024


settings = Settings()
settings.UPLOAD_DIR = settings.UPLOAD_DIR.resolve()
