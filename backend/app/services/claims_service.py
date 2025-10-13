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
        """Convert domain model to API schema - adapted for new table structure."""
        # Convert datetime to datetime if needed
        submission_dt = None
        if claim.rfb_entered_dt:
            from datetime import datetime as dt
            if isinstance(claim.rfb_entered_dt, dt):
                submission_dt = claim.rfb_entered_dt
            else:
                submission_dt = dt.combine(claim.rfb_entered_dt, dt.min.time())
        
        approval_dt = None
        if claim.certification_date:
            from datetime import datetime as dt
            approval_dt = dt.combine(claim.certification_date, dt.min.time())
        
        # Calculate claim amount from decision counts
        total_decisions = claim.total_decisions()
        claim_amount = Decimal(str(claim.ongoing_rate_month or 0))
        
        return ClaimSchema(
            # Core identifiers
            claim_id=claim.tpa_fee_worksheet_snapshot_fact_id,
            claim_number=claim.policy_number,
            policy_id=claim.policy_dim_id,
            
            # Claimant information
            claimant_name=claim.claimant_name,
            
            # Status and decision
            status=claim.decision or "PENDING",
            claim_type=str(claim.claim_type_cd) if claim.claim_type_cd else None,
            
            # Dates
            submission_date=submission_dt,
            service_start_date=claim.latest_eob_start_dt,
            service_end_date=claim.latest_eob_end_dt,
            approval_date=approval_dt,
            certification_date=claim.certification_date,
            
            # Financial information
            claim_amount=claim_amount,
            approved_amount=Decimal(str(claim.initial_decisions_facilities or 0)) if claim.is_approved() else None,
            paid_amount=None,  # Not available in new structure
            
            # Processing information
            processing_days=claim.rfb_process_to_decision_tat,
            denial_reason=None if claim.is_approved() else claim.decision,
            
            # RFB information
            rfb_id=claim.rfb_id,
            rfb_reference=claim.rfb_reference,
            
            # Decision metrics
            initial_decisions_facilities=claim.initial_decisions_facilities,
            initial_decisions_home_health=claim.initial_decisions_home_health,
            ongoing_rate_month=claim.ongoing_rate_month,
            
            # Provider information
            facility_name=claim.poc_provider_type_desc,
            provider_count=claim.total_eligible_provider_count,
            
            # Geographic information
            life_state=claim.life_state,
            issue_state=claim.issue_state,
            
            # Metadata
            carrier_name=claim.carrier_name,
            snapshot_date=claim.snapshot_date,
        )

