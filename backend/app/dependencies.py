"""Dependency injection for FastAPI."""

from collections.abc import AsyncIterator

from fastapi import Depends
from snowflake.snowpark import Session

from .core.snowpark_session import SnowparkSessionManager, get_session_manager
from .repositories.claims_repo import ClaimsRepository
from .repositories.policy_repo import PolicyRepository
from .services.analytics_service import AnalyticsService
from .services.claims_service import ClaimsService


async def get_snowpark_session(
    manager: SnowparkSessionManager = Depends(get_session_manager),
) -> AsyncIterator[Session]:
    """
    Dependency to get Snowpark session.

    Yields:
        Active Snowpark session
    """
    async with manager.get_session() as session:
        yield session


async def get_claims_repository(
    session: Session = Depends(get_snowpark_session),
) -> ClaimsRepository:
    """
    Dependency to get claims repository.

    Args:
        session: Snowpark session

    Returns:
        ClaimsRepository instance
    """
    return ClaimsRepository(session)


async def get_policy_repository(
    session: Session = Depends(get_snowpark_session),
) -> PolicyRepository:
    """
    Dependency to get policy repository.

    Args:
        session: Snowpark session

    Returns:
        PolicyRepository instance
    """
    return PolicyRepository(session)


async def get_analytics_service(
    claims_repo: ClaimsRepository = Depends(get_claims_repository),
    policy_repo: PolicyRepository = Depends(get_policy_repository),
) -> AnalyticsService:
    """
    Dependency to get analytics service.

    Args:
        claims_repo: Claims repository
        policy_repo: Policy repository

    Returns:
        AnalyticsService instance
    """
    return AnalyticsService(claims_repo, policy_repo)


async def get_claims_service(
    claims_repo: ClaimsRepository = Depends(get_claims_repository),
) -> ClaimsService:
    """
    Dependency to get claims service.

    Args:
        claims_repo: Claims repository

    Returns:
        ClaimsService instance
    """
    return ClaimsService(claims_repo)

