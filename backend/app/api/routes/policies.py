"""Policy API endpoints."""

from typing import Any, Optional, Dict, List
from datetime import datetime
from decimal import Decimal

import structlog
from fastapi import APIRouter, Depends, HTTPException, Path, Query

from ...dependencies import get_policy_repository
from ...models.schemas import PolicySchema
from ...models.domain import Policy
from ...repositories.policy_repo import PolicyRepository

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/policies", tags=["policies"])


def _domain_to_schema(policy: Policy) -> PolicySchema:
    """Convert Policy domain model to PolicySchema for API response."""
    # Extract the date parts from datetime fields
    issue_date = policy.original_effective_dt.date() if policy.original_effective_dt else None
    effective_date = policy.coverage_effective_dt.date() if policy.coverage_effective_dt else None
    termination_date = policy.policy_expiration_dt.date() if policy.policy_expiration_dt else None
    last_premium_date = policy.paid_to_date.date() if policy.paid_to_date else None
    
    return PolicySchema(
        # Core identifiers
        policy_id=policy.policy_monthly_snapshot_id,
        policy_number=str(policy.policy_id),  # Use numeric policy_id as policy_number
        
        # Status
        status=policy.claim_status_cd,
        
        # Dates
        issue_date=issue_date,
        effective_date=effective_date,
        termination_date=termination_date,
        last_premium_date=last_premium_date,
        
        # Premium and benefits
        premium_amount=policy.monthly_premium(),
        benefit_amount=policy.total_request_for_reimbursment_benefit,
        annualized_premium=policy.annualized_premium,
        
        # Insured information
        insured_name=None,  # Not available in snapshot table
        insured_age=policy.rated_age,
        insured_state=policy.insured_state,
        insured_city=policy.insured_city,
        insured_zip=policy.insured_zip,
        
        # Additional fields
        policy_residence_state=policy.policy_residence_state,
        premium_frequency=policy.premium_frequency,
        benefit_inflation=policy.benefit_inflation,
        
        # Claim information
        total_active_claims=policy.total_active_claims,
        claim_status_cd=policy.claim_status_cd,
        
        # Metadata
        carrier_name=policy.carrier_name,
        environment=policy.environment,
    )


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

    return _domain_to_schema(policy)


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
    return [_domain_to_schema(policy) for policy in policies]


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

