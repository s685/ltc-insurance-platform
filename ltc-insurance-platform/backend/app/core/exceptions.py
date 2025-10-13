"""Custom exceptions for the application."""

from typing import Any, Optional


class AppException(Exception):
    """Base exception for application errors."""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class DataNotFoundError(AppException):
    """Raised when requested data is not found."""
    pass


class SnowflakeConnectionError(AppException):
    """Raised when Snowflake connection fails."""
    pass


class CacheError(AppException):
    """Raised when cache operations fail."""
    pass


class ValidationError(AppException):
    """Raised when data validation fails."""
    pass


class ConfigurationError(AppException):
    """Raised when configuration is invalid."""
    pass

