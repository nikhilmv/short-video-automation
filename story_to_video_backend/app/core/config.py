from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    PIXABAY_API_KEY: Optional[str] = None
    BACKEND_BASE_URL: Optional[str] = "http://localhost:5000"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()