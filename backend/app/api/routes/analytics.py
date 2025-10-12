"""Analytics API endpoints."""

from typing import Optional
from datetime import date

import structlog
from fastapi import APIRouter, Depends, Query

from ...dependencies import get_analytics_service
from ...models.schemas import (
    AnalyticsRequest,
    AnalyticsResponse,
    ClaimSummary,
    PolicyMetrics,
)
from ...services.analytics_service import AnalyticsService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/claims-summary",
    response_model=ClaimSummary,
    summary="Get Claims Summary",
    description="Retrieve aggregated claims statistics including approval rates, processing times, and amounts.",
)
async def get_claims_summary(
    start_date: Optional[date] = Query(None, description="Start date for analysis"),
    end_date: Optional[date] = Query(None, description="End date for analysis"),
    service: AnalyticsService = Depends(get_analytics_service),
) -> ClaimSummary:
    """Get claims summary analytics."""
    logger.info("api_claims_summary", start_date=start_date, end_date=end_date)
    return await service.get_claims_summary(start_date, end_date)


@router.get(
    "/policy-metrics",
    response_model=PolicyMetrics,
    summary="Get Policy Metrics",
    description="Retrieve policy statistics including active policies, lapse rates, and premium information.",
)
async def get_policy_metrics(
    start_date: Optional[date] = Query(None, description="Start date for analysis"),
    end_date: Optional[date] = Query(None, description="End date for analysis"),
    service: AnalyticsService = Depends(get_analytics_service),
) -> PolicyMetrics:
    """Get policy metrics analytics."""
    logger.info("api_policy_metrics", start_date=start_date, end_date=end_date)
    return await service.get_policy_metrics(start_date, end_date)


@router.post(
    "/custom-query",
    response_model=AnalyticsResponse,
    summary="Custom Analytics Query",
    description="Execute a custom analytics query with advanced filtering options.",
)
async def custom_analytics_query(
    request: AnalyticsRequest,
    service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsResponse:
    """Execute custom analytics query with filters."""
    logger.info("api_custom_analytics", request=request.model_dump())
    return await service.get_comprehensive_analytics(request)


@router.get(
    "/trends",
    response_model=AnalyticsResponse,
    summary="Get Analytics Trends",
    description="Retrieve trend data for claims and policies over time.",
)
async def get_analytics_trends(
    start_date: date = Query(..., description="Start date for trends"),
    end_date: date = Query(..., description="End date for trends"),
    group_by: str = Query(
        "month", description="Time grouping (day, week, month, quarter, year)"
    ),
    service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsResponse:
    """Get analytics trends over time."""
    logger.info(
        "api_trends",
        start_date=start_date,
        end_date=end_date,
        group_by=group_by,
    )

    request = AnalyticsRequest(
        start_date=start_date,
        end_date=end_date,
        group_by=group_by,  # type: ignore
    )

    return await service.get_comprehensive_analytics(request)

