"""Snowpark session manager with connection pooling and lifecycle management."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Any, Optional, List, Dict

import structlog
from snowflake.snowpark import Session
from snowflake.snowpark.exceptions import SnowparkSessionException

from ..config import Settings, get_settings
from .exceptions import DatabaseConnectionError

logger = structlog.get_logger(__name__)


class SnowparkSessionManager:
    """Manages Snowpark sessions with connection pooling."""

    def __init__(self, settings: Settings) -> None:
        """Initialize session manager with settings."""
        self.settings = settings
        self._connection_params = settings.snowflake_connection_params
        self._session_pool: List[Session] = []
        self._pool_lock = asyncio.Lock()
        self._active_sessions: set[Session] = set()
        self._max_connections = settings.max_connections

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[Session]:
        """
        Get a Snowpark session from the pool.

        Yields:
            Session: Active Snowpark session

        Raises:
            DatabaseConnectionError: If connection fails
        """
        session: Optional[Session] = None
        try:
            session = await self._acquire_session()
            logger.info("session_acquired", session_id=id(session))
            yield session
        except SnowparkSessionException as e:
            logger.error("snowpark_session_error", error=str(e))
            raise DatabaseConnectionError(
                message="Failed to establish Snowpark session",
                details={"original_error": str(e)},
            ) from e
        except Exception as e:
            logger.error("unexpected_session_error", error=str(e))
            raise DatabaseConnectionError(
                message="Unexpected error with Snowpark session",
                details={"original_error": str(e)},
            ) from e
        finally:
            if session:
                await self._release_session(session)
                logger.info("session_released", session_id=id(session))

    async def _acquire_session(self) -> Session:
        """Acquire a session from the pool or create a new one."""
        async with self._pool_lock:
            # Try to reuse an existing session from the pool
            if self._session_pool:
                session = self._session_pool.pop()
                if self._is_session_valid(session):
                    self._active_sessions.add(session)
                    return session
                else:
                    # Session is invalid, close it
                    await self._close_session(session)

            # Create a new session if under the limit
            if len(self._active_sessions) < self._max_connections:
                session = await self._create_session()
                self._active_sessions.add(session)
                return session

            # Wait for a session to become available
            logger.warning(
                "session_pool_exhausted",
                active=len(self._active_sessions),
                max=self._max_connections,
            )

        # Wait and retry
        await asyncio.sleep(0.1)
        return await self._acquire_session()

    async def _release_session(self, session: Session) -> None:
        """Release a session back to the pool."""
        async with self._pool_lock:
            if session in self._active_sessions:
                self._active_sessions.remove(session)
                if self._is_session_valid(session):
                    self._session_pool.append(session)
                else:
                    await self._close_session(session)

    async def _create_session(self) -> Session:
        """Create a new Snowpark session."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            session = await loop.run_in_executor(
                None, Session.builder.configs(self._connection_params).create
            )
            logger.info("session_created", session_id=id(session))
            return session
        except Exception as e:
            logger.error("session_creation_failed", error=str(e))
            raise DatabaseConnectionError(
                message="Failed to create Snowpark session",
                details={"original_error": str(e)},
            ) from e

    def _is_session_valid(self, session: Session) -> bool:
        """Check if a session is still valid."""
        try:
            # Simple query to test connection
            session.sql("SELECT 1").collect()
            return True
        except Exception as e:
            logger.warning("session_validation_failed", error=str(e))
            return False

    async def _close_session(self, session: Session) -> None:
        """Close a Snowpark session."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, session.close)
            logger.info("session_closed", session_id=id(session))
        except Exception as e:
            logger.error("session_close_failed", error=str(e))

    async def close_all(self) -> None:
        """Close all sessions in the pool."""
        async with self._pool_lock:
            # Close active sessions
            for session in self._active_sessions.copy():
                await self._close_session(session)
            self._active_sessions.clear()

            # Close pooled sessions
            for session in self._session_pool:
                await self._close_session(session)
            self._session_pool.clear()

        logger.info("all_sessions_closed")

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Snowflake connection."""
        try:
            async with self.get_session() as session:
                result = session.sql("SELECT CURRENT_TIMESTAMP()").collect()
                return {
                    "status": "healthy",
                    "database": self.settings.snowflake_database,
                    "schema": self.settings.snowflake_schema,
                    "warehouse": self.settings.snowflake_warehouse,
                    "timestamp": str(result[0][0]),
                    "active_sessions": len(self._active_sessions),
                    "pooled_sessions": len(self._session_pool),
                }
        except Exception as e:
            logger.error("health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "active_sessions": len(self._active_sessions),
                "pooled_sessions": len(self._session_pool),
            }


@lru_cache
def get_session_manager() -> SnowparkSessionManager:
    """Get cached session manager instance."""
    settings = get_settings()
    return SnowparkSessionManager(settings)

