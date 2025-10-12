"""Analytics service for LTC insurance business logic."""

from typing import Any, Optional, Dict, List
import asyncio
from datetime import date
from decimal import Decimal

import structlog

from ..core.cache import cache_result
from ..models.domain import ClaimStatus, PolicyStatus
from ..models.schemas import (
    AnalyticsRequest,
    AnalyticsResponse,
    ClaimSummary,
    PolicyMetrics,
)
from ..repositories.claims_repo import ClaimsRepository
from ..repositories.policy_repo import PolicyRepository

logger = structlog.get_logger(__name__)


class AnalyticsService:
    """Service for analytics and reporting operations."""

    def __init__(
        self, claims_repo: ClaimsRepository, policy_repo: PolicyRepository
    ) -> None:
        """Initialize analytics service with repositories."""
        self.claims_repo = claims_repo
        self.policy_repo = policy_repo

    @cache_result(ttl=300, key_prefix="analytics:summary")
    async def get_comprehensive_analytics(
        self, request: AnalyticsRequest
    ) -> AnalyticsResponse:
        """
        Get comprehensive analytics including claims and policy metrics.

        Args:
            request: Analytics request with filters

        Returns:
            AnalyticsResponse with all metrics
        """
        logger.info("generating_comprehensive_analytics", filters=request.model_dump())

        # Run claims and policy analytics concurrently
        claims_task = asyncio.create_task(
            self.get_claims_summary(request.start_date, request.end_date)
        )
        policy_task = asyncio.create_task(
            self.get_policy_metrics(request.start_date, request.end_date)
        )

        claim_summary, policy_metrics = await asyncio.gather(claims_task, policy_task)

        return AnalyticsResponse(
            claim_summary=claim_summary,
            policy_metrics=policy_metrics,
            filters_applied=request.model_dump(exclude_none=True),
        )

    @cache_result(ttl=300, key_prefix="analytics:claims")
    async def get_claims_summary(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> ClaimSummary:
        """
        Get claims summary analytics.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            ClaimSummary with aggregated metrics
        """
        logger.info("generating_claims_summary", start_date=start_date, end_date=end_date)

        # Run multiple queries concurrently
        summary_task = asyncio.create_task(
            self.claims_repo.get_claims_summary(start_date, end_date)
        )
        by_status_task = asyncio.create_task(
            self.claims_repo.get_claims_by_status(start_date, end_date)
        )
        processing_days_task = asyncio.create_task(
            self.claims_repo.get_avg_processing_days(start_date, end_date)
        )

        summary, by_status, avg_processing_days = await asyncio.gather(
            summary_task, by_status_task, processing_days_task
        )

        # Extract counts by status
        approved_count = by_status.get(ClaimStatus.APPROVED.value, 0) + by_status.get(
            ClaimStatus.PAID.value, 0
        )
        denied_count = by_status.get(ClaimStatus.DENIED.value, 0)
        pending_count = (
            by_status.get(ClaimStatus.SUBMITTED.value, 0)
            + by_status.get(ClaimStatus.UNDER_REVIEW.value, 0)
        )

        total_claims = summary.get("total_claims", 0)
        total_claim_amount = summary.get("total_claim_amount", Decimal(0))
        total_approved_amount = summary.get("total_approved_amount", Decimal(0))

        # Calculate approval rate
        approval_rate = (
            approved_count / total_claims if total_claims > 0 else 0.0
        )

        return ClaimSummary(
            total_claims=total_claims,
            approved_claims=approved_count,
            denied_claims=denied_count,
            pending_claims=pending_count,
            total_claim_amount=total_claim_amount,
            total_approved_amount=total_approved_amount,
            total_paid_amount=summary.get("total_paid_amount", Decimal(0)),
            avg_processing_days=avg_processing_days,
            approval_rate=approval_rate,
            avg_claim_amount=summary.get("avg_claim_amount", Decimal(0)),
        )

    @cache_result(ttl=300, key_prefix="analytics:policies")
    async def get_policy_metrics(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> PolicyMetrics:
        """
        Get policy metrics analytics.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            PolicyMetrics with aggregated metrics
        """
        logger.info("generating_policy_metrics", start_date=start_date, end_date=end_date)

        # Run multiple queries concurrently
        metrics_task = asyncio.create_task(
            self.policy_repo.get_policy_metrics(start_date, end_date)
        )
        by_status_task = asyncio.create_task(
            self.policy_repo.get_policies_by_status(start_date, end_date)
        )
        by_type_task = asyncio.create_task(
            self.policy_repo.get_policies_by_type(start_date, end_date)
        )
        lapse_rate_task = asyncio.create_task(
            self.policy_repo.calculate_lapse_rate(start_date, end_date)
        )

        metrics, by_status, by_type, lapse_rate = await asyncio.gather(
            metrics_task, by_status_task, by_type_task, lapse_rate_task
        )

        # Extract counts by status
        active_count = by_status.get(PolicyStatus.ACTIVE.value, 0)
        lapsed_count = by_status.get(PolicyStatus.LAPSED.value, 0)
        terminated_count = by_status.get(PolicyStatus.TERMINATED.value, 0)

        return PolicyMetrics(
            total_policies=metrics.get("total_policies", 0),
            active_policies=active_count,
            lapsed_policies=lapsed_count,
            terminated_policies=terminated_count,
            total_premium=metrics.get("total_premium", Decimal(0)),
            avg_premium=metrics.get("avg_premium", Decimal(0)),
            avg_benefit=metrics.get("avg_benefit", Decimal(0)),
            avg_insured_age=metrics.get("avg_insured_age", 0.0),
            lapse_rate=lapse_rate,
            policy_type_distribution=by_type,
        )

    async def get_claim_approval_rate_by_type(
        self, policy_type: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Calculate claim approval rates by policy type.

        Args:
            policy_type: Optional policy type filter

        Returns:
            Dictionary mapping policy types to approval rates
        """
        logger.info("calculating_approval_rates", policy_type=policy_type)
        
        # This would join claims and policies tables
        # Simplified implementation for now
        return {"COMPREHENSIVE": 0.85, "FACILITY_ONLY": 0.78, "HOME_CARE": 0.82}

    async def get_cost_trends(
        self, start_date: date, end_date: date, group_by: str = "month"
    ) -> List[Dict[str, Any]]:
        """
        Get cost trends over time.

        Args:
            start_date: Start date for trends
            end_date: End date for trends
            group_by: Time grouping (day, week, month, quarter, year)

        Returns:
            List of trend data points
        """
        logger.info(
            "calculating_cost_trends",
            start_date=start_date,
            end_date=end_date,
            group_by=group_by,
        )

        # Placeholder for trend calculation
        # Would use Snowpark's window functions and date grouping
        return []

