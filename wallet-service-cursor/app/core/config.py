from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl, Field, field_validator
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",  # ignore unknown env vars like CORS_ORIGINS
    )

    # Application
    app_name: str = "Wallet Service API"
    environment: str = "development"
    debug: bool = False
    # Secret key must be provided via environment (e.g., SECRET_KEY in .env)
    secret_key: str = Field(..., min_length=16)
    
    # Database
    database_url: AnyUrl
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    database_pool_recycle: int = 1800
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = "logs"
    
    # API
    api_prefix: str = "/api/v1"




# Global settings instance
settings = Settings()
