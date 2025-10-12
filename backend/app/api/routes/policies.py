"""Policy API endpoints."""

from typing import Any, Optional, Dict, List

import structlog
from fastapi import APIRouter, Depends, HTTPException, Path, Query

from ...dependencies import get_policy_repository
from ...models.schemas import PolicySchema
from ...repositories.policy_repo import PolicyRepository

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get(
    "/{policy_id}",
    response_model=PolicySchema,
    summary="Get Policy by ID",
    description="Retrieve detailed information for a specific policy.",
)
async def get_policy(
    policy_id: str = Path(..., description="Policy identifier"),
    repo: PolicyRepository = Depends(get_policy_repository),
) -> PolicySchema:
    """Get policy by ID."""
    logger.info("api_get_policy", policy_id=policy_id)

    policy = await repo.find_by_id(policy_id)
    if not policy:
        raise HTTPException(
            status_code=404,
            detail={"error": "POLICY_NOT_FOUND", "message": f"Policy {policy_id} not found"},
        )

    return PolicySchema.model_validate(policy)


@router.get(
    "/",
    response_model=List[PolicySchema],
    summary="List Policies",
    description="Retrieve a list of policies with optional filtering and pagination.",
)
async def list_policies(
    limit: int = Query(100, ge=1, le=1000, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    status: Optional[str] = Query(None, description="Filter by policy status"),
    policy_type: Optional[str] = Query(None, description="Filter by policy type"),
    state: Optional[str] = Query(None, description="Filter by insured state"),
    repo: PolicyRepository = Depends(get_policy_repository),
) -> List[PolicySchema]:
    """List policies with filtering and pagination."""
    logger.info(
        "api_list_policies",
        limit=limit,
        offset=offset,
        status=status,
        policy_type=policy_type,
        state=state,
    )

    filters: Dict[str, Any] = {}
    if status:
        filters["STATUS"] = status
    if policy_type:
        filters["POLICY_TYPE"] = policy_type
    if state:
        filters["INSURED_STATE"] = state.upper()

    policies = await repo.find_all(limit=limit, offset=offset, filters=filters)
    return [PolicySchema.model_validate(policy) for policy in policies]


@router.get(
    "/count",
    response_model=Dict[str, int],
    summary="Count Policies",
    description="Get the total count of policies matching the filter criteria.",
)
async def count_policies(
    status: Optional[str] = Query(None, description="Filter by policy status"),
    policy_type: Optional[str] = Query(None, description="Filter by policy type"),
    state: Optional[str] = Query(None, description="Filter by insured state"),
    repo: PolicyRepository = Depends(get_policy_repository),
) -> Dict[str, int]:
    """Count policies matching filters."""
    logger.info(
        "api_count_policies",
        status=status,
        policy_type=policy_type,
        state=state,
    )

    filters: Dict[str, Any] = {}
    if status:
        filters["STATUS"] = status
    if policy_type:
        filters["POLICY_TYPE"] = policy_type
    if state:
        filters["INSURED_STATE"] = state.upper()

    count = await repo.count(filters=filters)
    return {"count": count}

