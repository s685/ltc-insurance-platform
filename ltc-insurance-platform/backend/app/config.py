"""Application configuration using Pydantic settings."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Snowflake Configuration
    snowflake_account: str
    snowflake_user: str
    snowflake_password: str
    snowflake_warehouse: str
    snowflake_database: str = "LTC_INSURANCE"
    snowflake_schema: str = "ANALYTICS"
    snowflake_role: str = "ACCOUNTADMIN"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    project_name: str = "LTC Insurance Data Service"
    version: str = "1.0.0"
    
    # Cache Configuration
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes default
    redis_url: str = "redis://localhost:6379"
    redis_enabled: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_json: bool = False
    
    # CORS
    cors_origins: List[str] = ["http://localhost:8501", "http://localhost:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Connection Pool
    max_pool_connections: int = 5
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()

