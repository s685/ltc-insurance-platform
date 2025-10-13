"""Snowpark session manager with connection pooling."""

import logging
from contextlib import contextmanager
from typing import Generator, Optional
from snowflake.snowpark import Session
from snowflake.snowpark.exceptions import SnowparkSessionException

from app.config import settings
from app.core.exceptions import SnowflakeConnectionError

logger = logging.getLogger(__name__)


class SnowparkSessionManager:
    """Manages Snowpark sessions with connection pooling."""
    
    def __init__(self):
        self._session: Optional[Session] = None
        self._connection_params = {
            "account": settings.snowflake_account,
            "user": settings.snowflake_user,
            "password": settings.snowflake_password,
            "warehouse": settings.snowflake_warehouse,
            "database": settings.snowflake_database,
            "schema": settings.snowflake_schema,
            "role": settings.snowflake_role,
        }
    
    def get_session(self) -> Session:
        """Get or create a Snowpark session."""
        try:
            if self._session is None or not self._is_session_active():
                logger.info("Creating new Snowpark session")
                self._session = Session.builder.configs(self._connection_params).create()
                logger.info("Snowpark session created successfully")
            return self._session
        except Exception as e:
            logger.error(f"Failed to create Snowpark session: {e}")
            raise SnowflakeConnectionError(
                message="Failed to connect to Snowflake",
                details=str(e)
            )
    
    def _is_session_active(self) -> bool:
        """Check if the current session is active."""
        if self._session is None:
            return False
        try:
            # Try a simple query to check connection
            self._session.sql("SELECT 1").collect()
            return True
        except (SnowparkSessionException, Exception):
            return False
    
    def close_session(self):
        """Close the current Snowpark session."""
        if self._session is not None:
            try:
                self._session.close()
                logger.info("Snowpark session closed")
            except Exception as e:
                logger.warning(f"Error closing Snowpark session: {e}")
            finally:
                self._session = None
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Context manager for Snowpark sessions."""
        session = self.get_session()
        try:
            yield session
        except Exception as e:
            logger.error(f"Error during session operation: {e}")
            raise
        finally:
            # Keep session alive for reuse (connection pooling)
            pass


# Global session manager instance
session_manager = SnowparkSessionManager()


def get_snowpark_session() -> Session:
    """Dependency function to get Snowpark session."""
    return session_manager.get_session()

