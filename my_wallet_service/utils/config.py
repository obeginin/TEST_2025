from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl, Field
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        case_sensitive=False,
        extra="ignore",  # ignore unknown env vars like CORS_ORIGINS
    )

    # Application
    app_name: str = "Wallet Service API"
    environment: str = "development"
    debug: bool = False
    secret_key: str = Field(..., min_length=16)
    
    # Database
    #db_url: AnyUrl
    db_host: str
    db_port: str
    db_user: str
    db_password: str
    db_name: str
    db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs"
    
    # API
    api_prefix: str = "/api/v1"

    timezone: str = "Europe/Moscow"




# Global settings instance
settings = Settings()
