from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pdf_summarizer"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/pdf_summarizer"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # OpenAI
    openai_api_key: str = ""

    # SendGrid
    sendgrid_api_key: str = ""
    from_email: str = "noreply@pdfsummarizer.com"

    # Frontend
    frontend_url: str = "http://localhost:5173"

    # File storage
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
