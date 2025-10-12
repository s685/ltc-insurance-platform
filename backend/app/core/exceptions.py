"""Custom exception classes for the application."""

from typing import Any, Optional, Dict


class DataServiceError(Exception):
    """Base exception for all data service errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize exception with message and optional details."""
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class DatabaseConnectionError(DataServiceError):
    """Exception raised when database connection fails."""

    def __init__(
        self, message: str = "Failed to connect to database", **kwargs: Any
    ) -> None:
        """Initialize database connection error."""
        super().__init__(message, error_code="DB_CONNECTION_ERROR", **kwargs)


class InvalidQueryError(DataServiceError):
    """Exception raised when query is invalid."""

    def __init__(
        self, message: str = "Invalid query parameters", **kwargs: Any
    ) -> None:
        """Initialize invalid query error."""
        super().__init__(message, error_code="INVALID_QUERY", **kwargs)


class ResourceNotFoundError(DataServiceError):
    """Exception raised when requested resource is not found."""

    def __init__(
        self, message: str = "Requested resource not found", **kwargs: Any
    ) -> None:
        """Initialize resource not found error."""
        super().__init__(message, error_code="RESOURCE_NOT_FOUND", **kwargs)


class CacheError(DataServiceError):
    """Exception raised when cache operations fail."""

    def __init__(self, message: str = "Cache operation failed", **kwargs: Any) -> None:
        """Initialize cache error."""
        super().__init__(message, error_code="CACHE_ERROR", **kwargs)


class ValidationError(DataServiceError):
    """Exception raised when data validation fails."""

    def __init__(
        self, message: str = "Data validation failed", **kwargs: Any
    ) -> None:
        """Initialize validation error."""
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)

