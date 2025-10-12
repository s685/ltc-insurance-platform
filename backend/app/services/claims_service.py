"""Claims service for claim-specific business logic."""

from typing import Any, Dict, Optional, List

import structlog

from ..core.cache import cache_result
from ..core.exceptions import ResourceNotFoundError
from ..models.domain import Claim
from ..models.schemas import ClaimSchema
from ..repositories.claims_repo import ClaimsRepository

logger = structlog.get_logger(__name__)


class ClaimsService:
    """Service for claims business operations."""

    def __init__(self, claims_repo: ClaimsRepository) -> None:
        """Initialize claims service with repository."""
        self.claims_repo = claims_repo

    @cache_result(ttl=60, key_prefix="claim:by_id")
    async def get_claim_by_id(self, claim_id: str) -> ClaimSchema:
        """
        Get claim by ID.

        Args:
            claim_id: Claim identifier

        Returns:
            ClaimSchema

        Raises:
            ResourceNotFoundError: If claim not found
        """
        logger.info("fetching_claim", claim_id=claim_id)

        claim = await self.claims_repo.find_by_id(claim_id)
        if not claim:
            raise ResourceNotFoundError(
                message=f"Claim {claim_id} not found",
                details={"claim_id": claim_id},
            )

        return self._domain_to_schema(claim)

    async def get_claims(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ClaimSchema]:
        """
        Get claims with pagination and filtering.

        Args:
            limit: Maximum results to return
            offset: Number of results to skip
            filters: Optional filter criteria

        Returns:
            List of ClaimSchema
        """
        logger.info("fetching_claims", limit=limit, offset=offset, filters=filters)

        claims = await self.claims_repo.find_all(
            limit=limit, offset=offset, filters=filters
        )

        return [self._domain_to_schema(claim) for claim in claims]

    async def count_claims(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count claims matching filters.

        Args:
            filters: Optional filter criteria

        Returns:
            Number of matching claims
        """
        return await self.claims_repo.count(filters=filters)

    def _domain_to_schema(self, claim: Claim) -> ClaimSchema:
        """Convert domain model to API schema."""
        return ClaimSchema(
            claim_id=claim.claim_id,
            claim_number=claim.claim_number,
            policy_id=claim.policy_id,
            status=claim.status,
            claim_type=claim.claim_type,
            submission_date=claim.submission_date,
            service_start_date=claim.service_start_date,
            service_end_date=claim.service_end_date,
            claim_amount=claim.claim_amount,
            approved_amount=claim.approved_amount,
            paid_amount=claim.paid_amount,
            denial_reason=claim.denial_reason,
            approval_date=claim.approval_date,
            payment_date=claim.payment_date,
            reviewer_id=claim.reviewer_id,
            facility_name=claim.facility_name,
            diagnosis_codes=claim.diagnosis_codes,
        )

