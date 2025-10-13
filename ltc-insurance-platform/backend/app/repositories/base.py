"""Abstract base repository for data access."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any
from snowflake.snowpark import Session

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository with common data access patterns."""
    
    def __init__(self, session: Session):
        self.session = session
    
    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def list(self, limit: int = 100, offset: int = 0, **filters) -> List[T]:
        """List entities with optional filtering."""
        pass
    
    @abstractmethod
    def count(self, **filters) -> int:
        """Count entities matching filters."""
        pass
    
    def _execute_query(self, query: str, params: Optional[dict] = None) -> List[dict]:
        """Execute a SQL query and return results as list of dicts."""
        # Use Snowpark's native collect() instead of to_pandas()
        rows = self.session.sql(query).collect()
        
        # Convert Row objects to list of dicts with lowercase keys and JSON-safe types
        result = []
        for row in rows:
            row_dict = {}
            for k, v in row.as_dict().items():
                # Convert Decimals and other numeric types to native Python types
                if hasattr(v, '__float__') and not isinstance(v, bool):
                    row_dict[k.lower()] = float(v) if v is not None else 0.0
                elif v is None:
                    row_dict[k.lower()] = None
                else:
                    row_dict[k.lower()] = v
            result.append(row_dict)
        return result

