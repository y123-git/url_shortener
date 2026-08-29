"""
Configuration Management
"""

import os
import sys
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite://" if "pytest" in sys.modules else "sqlite:///./url_shortener.db"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:8000,http://localhost:3000"
    ).split(",")
    
    # Performance
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
    MAX_URL_LENGTH: int = int(os.getenv("MAX_URL_LENGTH", "2048"))
    RATE_LIMIT: int = int(os.getenv("RATE_LIMIT", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
    
    # Security
    JWT_EXPIRATION: int = int(os.getenv("JWT_EXPIRATION", "3600"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()