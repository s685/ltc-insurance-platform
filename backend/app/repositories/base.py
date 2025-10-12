"""Abstract base repository with generic CRUD operations."""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar, Dict, List

from snowflake.snowpark import Session

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository for data access operations."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with Snowpark session."""
        self.session = session

    @property
    @abstractmethod
    def table_name(self) -> str:
        """Get the table name for this repository."""
        ...

    @abstractmethod
    async def find_by_id(self, id_value: str) -> Optional[T]:
        """
        Find entity by ID.

        Args:
            id_value: The ID to search for

        Returns:
            Entity if found, None otherwise
        """
        ...

    @abstractmethod
    async def find_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[T]:
        """
        Find all entities with optional filtering and pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            filters: Optional filter conditions

        Returns:
            List of entities
        """
        ...

    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities with optional filtering.

        Args:
            filters: Optional filter conditions

        Returns:
            Number of entities matching filters
        """
        ...

    def _apply_filters(
        self, df: Any, filters: Optional[Dict[str, Any]]
    ) -> Any:
        """
        Apply filters to a Snowpark DataFrame.

        Args:
            df: Snowpark DataFrame
            filters: Dictionary of column: value filters

        Returns:
            Filtered DataFrame
        """
        if not filters:
            return df

        from snowflake.snowpark.functions import col

        for column, value in filters.items():
            if value is not None:
                if isinstance(value, (list, tuple)):
                    df = df.filter(col(column).in_(value))
                else:
                    df = df.filter(col(column) == value)

        return df

