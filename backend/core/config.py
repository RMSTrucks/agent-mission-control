"""
Configuration Management

Loads settings from environment variables and provides
configuration for the FastAPI application.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # Application
    app_name: str = "Agent Mission Control API"
    app_version: str = "0.1.0"
    debug: bool = True

    # API
    api_prefix: str = "/api"
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: list = ["http://localhost:8501", "http://localhost:3000"]

    # Database
    database_url: str = "sqlite:///./data/database.db"

    # SuperOptiX
    superoptix_path: Optional[str] = None
    project_root: str = os.getcwd()

    # External APIs
    vapi_api_key: Optional[str] = None
    close_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Redis (for Celery)
    redis_url: str = "redis://localhost:6379/0"

    # Logging
    log_level: str = "INFO"
    log_file: str = "./data/logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
