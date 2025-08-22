from pydantic_settings import BaseSettings
from pydantic import AnyUrl, field_validator
from typing import List, Optional
from pathlib import Path
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "InfoRUN API"
    environment: str = "development"
    debug: bool = False
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8  # 8 hours
    
    # Database
    database_url: AnyUrl
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    database_pool_recycle: int = 1800
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    # File Uploads
    upload_image_dir: Path = Path("uploads/images")
    upload_solution_dir: Path = Path("uploads/solutions")
    upload_files_dir: Path = Path("uploads/files")
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_logs: str = "app_logs"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Email
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("upload_image_dir", "upload_solution_dir", "upload_files_dir", mode="before")
    @classmethod
    def create_upload_dirs(cls, v):
        if isinstance(v, (str, Path)):
            path = Path(v)
            path.mkdir(parents=True, exist_ok=True)
            return path
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
