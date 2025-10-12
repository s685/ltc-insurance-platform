"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import Literal, Optional, List, Dict

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Snowflake Configuration
    snowflake_account: str = Field(..., description="Snowflake account identifier")
    snowflake_user: str = Field(..., description="Snowflake username")
    snowflake_password: str = Field(..., description="Snowflake password")
    snowflake_warehouse: str = Field(..., description="Snowflake warehouse name")
    snowflake_database: str = Field(
        default="LTC_INSURANCE", description="Snowflake database name"
    )
    snowflake_schema: str = Field(
        default="ANALYTICS", description="Snowflake schema name"
    )
    snowflake_role: Optional[str] = Field(
        default=None, description="Snowflake role (optional)"
    )

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port", ge=1, le=65535)
    api_prefix: str = Field(default="/api/v1", description="API route prefix")
    api_title: str = Field(
        default="LTC Insurance Data Service", description="API title"
    )
    api_version: str = Field(default="1.0.0", description="API version")

    # Cache Configuration
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds", ge=0)
    redis_url: Optional[str] = Field(
        default=None, description="Redis URL (optional, falls back to in-memory)"
    )

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )
    log_json: bool = Field(default=False, description="Use JSON logging format")

    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:8501", "http://localhost:3000"],
        description="Allowed CORS origins",
    )
    cors_credentials: bool = Field(
        default=True, description="Allow CORS credentials"
    )
    cors_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE"], description="Allowed CORS methods"
    )
    cors_headers: List[str] = Field(default=["*"], description="Allowed CORS headers")

    # Connection Pool Settings
    max_connections: int = Field(
        default=10, description="Maximum Snowpark connections", ge=1, le=100
    )
    connection_timeout: int = Field(
        default=30, description="Connection timeout in seconds", ge=1
    )

    @field_validator("snowflake_account")
    @classmethod
    def validate_account(cls, v: str) -> str:
        """Validate Snowflake account format."""
        if not v or len(v) < 3:
            raise ValueError("Snowflake account must be at least 3 characters")
        return v.strip()

    @field_validator("api_prefix")
    @classmethod
    def validate_api_prefix(cls, v: str) -> str:
        """Ensure API prefix starts with /."""
        if not v.startswith("/"):
            return f"/{v}"
        return v

    @property
    def snowflake_connection_params(self) -> Dict[str, str]:
        """Get Snowflake connection parameters."""
        params = {
            "account": self.snowflake_account,
            "user": self.snowflake_user,
            "password": self.snowflake_password,
            "warehouse": self.snowflake_warehouse,
            "database": self.snowflake_database,
            "schema": self.snowflake_schema,
        }
        if self.snowflake_role:
            params["role"] = self.snowflake_role
        return params


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()

