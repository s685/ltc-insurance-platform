"""Analytics API endpoints."""

import logging
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from snowflake.snowpark import Session

from app.dependencies import get_db_session
from app.services.analytics_service import AnalyticsService
from app.models.schemas import (
    PolicyMetrics,
    PolicyInsights,
    CombinedDashboard
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/policy-insights", response_model=PolicyInsights)
async def get_policy_insights(
    carrier_name: Optional[str] = Query(None),
    snapshot_date: Optional[str] = Query(None),
    session: Session = Depends(get_db_session)
):
    """Get comprehensive policy insights."""
    try:
        service = AnalyticsService(session)
        insights = service.get_policy_insights(
            carrier_name=carrier_name,
            snapshot_date=snapshot_date
        )
        return insights
    except Exception as e:
        logger.error(f"Error calculating policy insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policy-metrics", response_model=PolicyMetrics)
async def get_policy_metrics(
    carrier_name: Optional[str] = Query(None),
    snapshot_date: Optional[str] = Query(None),
    session: Session = Depends(get_db_session)
):
    """Get policy metrics."""
    try:
        service = AnalyticsService(session)
        metrics = service.get_policy_metrics(
            carrier_name=carrier_name,
            snapshot_date=snapshot_date
        )
        return metrics
    except Exception as e:
        logger.error(f"Error calculating policy metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/combined-dashboard", response_model=CombinedDashboard)
async def get_combined_dashboard(
    carrier_name: Optional[str] = Query(None),
    snapshot_date: Optional[str] = Query(None),
    report_end_dt: Optional[date] = Query(None),
    session: Session = Depends(get_db_session)
):
    """Get combined dashboard data for policies and claims."""
    try:
        service = AnalyticsService(session)
        dashboard = service.get_combined_dashboard(
            carrier_name=carrier_name,
            snapshot_date=snapshot_date,
            report_end_dt=report_end_dt
        )
        return dashboard
    except Exception as e:
        logger.error(f"Error generating combined dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

