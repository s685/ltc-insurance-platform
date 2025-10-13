"""Dependency injection functions for FastAPI."""

from typing import Generator
from snowflake.snowpark import Session

from app.core.snowpark_session import get_snowpark_session


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency to provide Snowpark session."""
    session = get_snowpark_session()
    try:
        yield session
    finally:
        # Session is managed by the session manager (kept alive for reuse)
        pass

