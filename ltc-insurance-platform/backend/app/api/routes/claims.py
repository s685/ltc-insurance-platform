"""Claims API endpoints."""

import logging
from typing import List, Dict, Any, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from snowflake.snowpark import Session

from app.dependencies import get_db_session
from app.services.claims_service import ClaimsService
from app.models.schemas import (
    ClaimResponse,
    ClaimsSummary,
    ClaimsInsights,
    ClaimsFilterRequest
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/claims", tags=["Claims"])


@router.get("/{claim_id}", response_model=Dict[str, Any])
async def get_claim(
    claim_id: str,
    session: Session = Depends(get_db_session)
):
    """Get claim by ID."""
    try:
        service = ClaimsService(session)
        claim = service.get_claim_by_id(claim_id)
        
        if not claim:
            raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
        
        return claim
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching claim {claim_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[Dict[str, Any]])
async def list_claims(
    carrier_name: Optional[str] = Query(None, description="Filter by carrier name"),
    report_end_dt: Optional[date] = Query(None, description="Report end date"),
    decision_types: Optional[str] = Query(
        None,
        description="Comma-separated decision types (e.g., 'Approved,Denied')"
    ),
    ongoing_rate_months: Optional[str] = Query(
        None,
        description="Comma-separated ongoing rate months (e.g., '0,1,2')"
    ),
    categories: Optional[str] = Query(
        None,
        description="Comma-separated categories (e.g., 'Facility,Home Health')"
    ),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_db_session)
):
    """List claims with configurable filters."""
    try:
        # Parse comma-separated parameters
        decision_types_list = decision_types.split(',') if decision_types else None
        ongoing_months_list = [int(x) for x in ongoing_rate_months.split(',')] if ongoing_rate_months else None
        categories_list = categories.split(',') if categories else None
        
        service = ClaimsService(session)
        claims = service.get_claims(
            carrier_name=carrier_name,
            report_end_dt=report_end_dt,
            decision_types=decision_types_list,
            ongoing_rate_months=ongoing_months_list,
            categories=categories_list,
            limit=limit,
            offset=offset
        )
        return claims
    except Exception as e:
        logger.error(f"Error listing claims: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/statistics", response_model=ClaimsSummary)
async def get_claims_summary(
    carrier_name: Optional[str] = Query(None),
    report_end_dt: Optional[date] = Query(None),
    session: Session = Depends(get_db_session)
):
    """Get claims summary statistics."""
    try:
        service = ClaimsService(session)
        summary = service.get_claims_summary(
            carrier_name=carrier_name,
            report_end_dt=report_end_dt
        )
        return summary
    except Exception as e:
        logger.error(f"Error calculating claims summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/detailed")
def get_claims_insights(
    carrier_name: Optional[str] = Query(None),
    report_end_dt: Optional[date] = Query(None),
    session: Session = Depends(get_db_session)
):
    """Get detailed claims insights with all breakdowns."""
    try:
        # Build insights directly without using service layer to avoid any caching/serialization issues
        from app.repositories.claims_repo import ClaimsRepository
        from app.models.schemas import ClaimsSummary, ClaimsInsights
        from decimal import Decimal
        
        repo = ClaimsRepository(session)
        
        # Get summary data
        summary_data = repo.get_summary(carrier_name=carrier_name, report_end_dt=report_end_dt)
        summary = ClaimsSummary(**summary_data)
        
        # Get decision breakdown
        decision_breakdown = repo.get_decision_breakdown(carrier_name=carrier_name, report_end_dt=report_end_dt)
        
        # Category breakdown
        category_breakdown = {
            "Facility": summary.facility_claims,
            "Home Health": summary.home_health_claims,
            "Other": summary.other_claims
        }
        
        # Get retro analysis
        retro_analysis = repo.get_retro_analysis(carrier_name=carrier_name, report_end_dt=report_end_dt)
        
        # Convert any Decimal values to float in retro_analysis
        retro_analysis_clean = {}
        for k, v in retro_analysis.items():
            if isinstance(v, Decimal):
                retro_analysis_clean[k] = float(v)
            else:
                retro_analysis_clean[k] = v
        
        # AVG TAT by category
        avg_tat_by_category = {
            "Overall": summary.avg_processing_time_days,
            "Facility": summary.avg_processing_time_days,
            "Home Health": summary.avg_processing_time_days,
            "Other": summary.avg_processing_time_days
        }
        
        # Build insights object
        insights = ClaimsInsights(
            summary=summary,
            decision_breakdown=decision_breakdown,
            category_breakdown=category_breakdown,
            avg_tat_by_category=avg_tat_by_category,
            retro_analysis=retro_analysis_clean
        )
        
        return insights.model_dump()
        
    except Exception as e:
        logger.error(f"Error calculating claims insights: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/count/total", response_model=Dict[str, int])
async def count_claims(
    carrier_name: Optional[str] = Query(None),
    report_end_dt: Optional[date] = Query(None),
    decision_types: Optional[str] = Query(None),
    ongoing_rate_months: Optional[str] = Query(None),
    session: Session = Depends(get_db_session)
):
    """Count claims matching filters."""
    try:
        # Parse comma-separated parameters
        decision_types_list = decision_types.split(',') if decision_types else None
        ongoing_months_list = [int(x) for x in ongoing_rate_months.split(',')] if ongoing_rate_months else None
        
        service = ClaimsService(session)
        count = service.count_claims(
            carrier_name=carrier_name,
            report_end_dt=report_end_dt,
            decision_types=decision_types_list,
            ongoing_rate_months=ongoing_months_list
        )
        return {"count": count}
    except Exception as e:
        logger.error(f"Error counting claims: {e}")
        raise HTTPException(status_code=500, detail=str(e))

