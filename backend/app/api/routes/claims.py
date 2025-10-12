"""Claims API endpoints."""

from typing import Any, Optional, Dict, List

import structlog
from fastapi import APIRouter, Depends, HTTPException, Path, Query

from ...dependencies import get_claims_service
from ...core.exceptions import ResourceNotFoundError
from ...models.schemas import ClaimSchema
from ...services.claims_service import ClaimsService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/claims", tags=["claims"])


@router.get(
    "/{claim_id}",
    response_model=ClaimSchema,
    summary="Get Claim by ID",
    description="Retrieve detailed information for a specific claim.",
)
async def get_claim(
    claim_id: str = Path(..., description="Claim identifier"),
    service: ClaimsService = Depends(get_claims_service),
) -> ClaimSchema:
    """Get claim by ID."""
    logger.info("api_get_claim", claim_id=claim_id)

    try:
        return await service.get_claim_by_id(claim_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.to_dict())


@router.get(
    "/",
    response_model=List[ClaimSchema],
    summary="List Claims",
    description="Retrieve a list of claims with optional filtering and pagination.",
)
async def list_claims(
    limit: int = Query(100, ge=1, le=1000, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    status: Optional[str] = Query(None, description="Filter by claim status"),
    policy_id: Optional[str] = Query(None, description="Filter by policy ID"),
    service: ClaimsService = Depends(get_claims_service),
) -> List[ClaimSchema]:
    """List claims with filtering and pagination."""
    logger.info(
        "api_list_claims",
        limit=limit,
        offset=offset,
        status=status,
        policy_id=policy_id,
    )

    filters: Dict[str, Any] = {}
    if status:
        filters["STATUS"] = status
    if policy_id:
        filters["POLICY_ID"] = policy_id

    return await service.get_claims(limit=limit, offset=offset, filters=filters)


@router.get(
    "/count",
    response_model=Dict[str, int],
    summary="Count Claims",
    description="Get the total count of claims matching the filter criteria.",
)
async def count_claims(
    status: Optional[str] = Query(None, description="Filter by claim status"),
    policy_id: Optional[str] = Query(None, description="Filter by policy ID"),
    service: ClaimsService = Depends(get_claims_service),
) -> Dict[str, int]:
    """Count claims matching filters."""
    logger.info("api_count_claims", status=status, policy_id=policy_id)

    filters: Dict[str, Any] = {}
    if status:
        filters["STATUS"] = status
    if policy_id:
        filters["POLICY_ID"] = policy_id

    count = await service.count_claims(filters=filters)
    return {"count": count}

