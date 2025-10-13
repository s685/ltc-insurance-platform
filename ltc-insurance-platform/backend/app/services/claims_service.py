"""Claims business logic service with caching."""

import logging
from typing import List, Dict, Any, Optional
from datetime import date
from snowflake.snowpark import Session

from app.repositories.claims_repo import ClaimsRepository
from app.models.schemas import ClaimsSummary, ClaimsInsights
from app.core.cache import cached

logger = logging.getLogger(__name__)


class ClaimsService:
    """Service for claims business logic."""
    
    def __init__(self, session: Session):
        self.repo = ClaimsRepository(session)
    
    @cached(ttl=300, key_prefix="claims:list:")
    def get_claims(
        self,
        carrier_name: Optional[str] = None,
        report_end_dt: Optional[date] = None,
        decision_types: Optional[List[str]] = None,
        ongoing_rate_months: Optional[List[int]] = None,
        categories: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get claims with configurable filters."""
        logger.info(
            f"Fetching claims: carrier={carrier_name}, date={report_end_dt}, "
            f"decisions={decision_types}, limit={limit}"
        )
        
        return self.repo.list(
            limit=limit,
            offset=offset,
            carrier_name=carrier_name,
            report_end_dt=report_end_dt,
            decision_types=decision_types,
            ongoing_rate_months=ongoing_rate_months,
            categories=categories
        )
    
    def get_claim_by_id(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """Get single claim by ID."""
        logger.info(f"Fetching claim: {claim_id}")
        claim = self.repo.get_by_id(claim_id)
        return claim.model_dump() if claim else None
    
    @cached(ttl=300, key_prefix="claims:summary:")
    def get_claims_summary(
        self,
        carrier_name: Optional[str] = None,
        report_end_dt: Optional[date] = None
    ) -> ClaimsSummary:
        """Get claims summary statistics with caching."""
        logger.info(f"Calculating claims summary: carrier={carrier_name}, date={report_end_dt}")
        
        summary_data = self.repo.get_summary(
            carrier_name=carrier_name,
            report_end_dt=report_end_dt
        )
        
        return ClaimsSummary(
            total_claims=summary_data.get("total_claims", 0),
            approved_claims=summary_data.get("approved_claims", 0),
            denied_claims=summary_data.get("denied_claims", 0),
            in_assessment_claims=summary_data.get("in_assessment_claims", 0),
            approval_rate=summary_data.get("approval_rate", 0.0),
            avg_processing_time_days=summary_data.get("avg_processing_time", 0.0) or 0.0,
            total_retro_claims=summary_data.get("total_retro_claims", 0),
            retro_percentage=summary_data.get("retro_percentage", 0.0),
            facility_claims=summary_data.get("facility_claims", 0),
            home_health_claims=summary_data.get("home_health_claims", 0),
            other_claims=summary_data.get("other_claims", 0),
            initial_decisions=summary_data.get("initial_decisions", 0),
            ongoing_decisions=summary_data.get("ongoing_decisions", 0),
            restoration_decisions=summary_data.get("restoration_decisions", 0)
        )
    
    # @cached(ttl=300, key_prefix="claims:insights:")  # Temporarily disabled for debugging
    def get_claims_insights(
        self,
        carrier_name: Optional[str] = None,
        report_end_dt: Optional[date] = None
    ) -> ClaimsInsights:
        """Get detailed claims insights with all breakdowns."""
        logger.info(f"Calculating claims insights: carrier={carrier_name}, date={report_end_dt}")
        
        # Get summary
        logger.info("Step 1: Getting claims summary...")
        summary = self.get_claims_summary(carrier_name, report_end_dt)
        logger.info(f"Step 1: Summary complete - {summary.total_claims} total claims")
        
        # Get decision breakdown
        logger.info("Step 2: Getting decision breakdown...")
        decision_breakdown = self.repo.get_decision_breakdown(
            carrier_name=carrier_name,
            report_end_dt=report_end_dt
        )
        logger.info(f"Step 2: Decision breakdown complete - {decision_breakdown}")
        
        # Category breakdown
        logger.info("Step 3: Building category breakdown...")
        category_breakdown = {
            "Facility": summary.facility_claims,
            "Home Health": summary.home_health_claims,
            "Other": summary.other_claims
        }
        logger.info(f"Step 3: Category breakdown complete")
        
        # Get retro analysis
        logger.info("Step 4: Getting retro analysis...")
        retro_analysis = self.repo.get_retro_analysis(
            carrier_name=carrier_name,
            report_end_dt=report_end_dt
        )
        logger.info(f"Step 4: Retro analysis complete")
        
        # Calculate avg TAT by category (simplified)
        avg_tat_by_category = {
            "Overall": summary.avg_processing_time_days,
            "Facility": summary.avg_processing_time_days,  # Could be calculated separately
            "Home Health": summary.avg_processing_time_days,
            "Other": summary.avg_processing_time_days
        }
        
        return ClaimsInsights(
            summary=summary,
            decision_breakdown=decision_breakdown,
            category_breakdown=category_breakdown,
            avg_tat_by_category=avg_tat_by_category,
            retro_analysis=retro_analysis
        )
    
    def count_claims(
        self,
        carrier_name: Optional[str] = None,
        report_end_dt: Optional[date] = None,
        decision_types: Optional[List[str]] = None,
        ongoing_rate_months: Optional[List[int]] = None
    ) -> int:
        """Count claims matching filters."""
        return self.repo.count(
            carrier_name=carrier_name,
            report_end_dt=report_end_dt,
            decision_types=decision_types,
            ongoing_rate_months=ongoing_rate_months
        )

