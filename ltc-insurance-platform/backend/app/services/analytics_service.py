"""Analytics and combined insights service."""

import logging
from typing import Optional
from datetime import date, datetime
from snowflake.snowpark import Session

from app.repositories.policy_repo import PolicyRepository
from app.services.claims_service import ClaimsService
from app.models.schemas import (
    PolicyMetrics,
    PolicyInsights,
    CombinedDashboard
)
from app.core.cache import cached

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics and combined insights."""
    
    def __init__(self, session: Session):
        self.policy_repo = PolicyRepository(session)
        self.claims_service = ClaimsService(session)
    
    @cached(ttl=300, key_prefix="analytics:policy_metrics:")
    def get_policy_metrics(
        self,
        carrier_name: Optional[str] = None,
        snapshot_date: Optional[str] = None
    ) -> PolicyMetrics:
        """Get policy metrics with caching."""
        logger.info(f"Calculating policy metrics: carrier={carrier_name}, date={snapshot_date}")
        
        metrics_data = self.policy_repo.get_metrics(
            carrier_name=carrier_name,
            snapshot_date=snapshot_date
        )
        
        return PolicyMetrics(
            total_policies=metrics_data.get("total_policies", 0),
            active_policies=metrics_data.get("active_policies", 0),
            in_forfeiture_policies=metrics_data.get("in_forfeiture_policies", 0),
            in_waiver_policies=metrics_data.get("in_waiver_policies", 0),
            avg_premium=metrics_data.get("avg_premium", 0.0) or 0.0,
            total_premium_revenue=metrics_data.get("total_premium_revenue", 0.0) or 0.0,
            avg_insured_age=metrics_data.get("avg_insured_age", 0.0) or 0.0,
            lapse_rate=metrics_data.get("lapse_rate", 0.0),
            policies_with_claims=metrics_data.get("policies_with_claims", 0),
            avg_claims_per_policy=metrics_data.get("avg_claims_per_policy", 0.0)
        )
    
    @cached(ttl=300, key_prefix="analytics:policy_insights:")
    def get_policy_insights(
        self,
        carrier_name: Optional[str] = None,
        snapshot_date: Optional[str] = None
    ) -> PolicyInsights:
        """Get detailed policy insights."""
        logger.info(f"Calculating policy insights: carrier={carrier_name}, date={snapshot_date}")
        
        # Get metrics
        metrics = self.get_policy_metrics(carrier_name, snapshot_date)
        
        # Get state distribution
        state_distribution = self.policy_repo.get_state_distribution(
            carrier_name=carrier_name,
            snapshot_date=snapshot_date
        )
        
        # Get premium by state
        premium_by_state = self.policy_repo.get_premium_by_state(
            carrier_name=carrier_name,
            snapshot_date=snapshot_date
        )
        
        # Waiver breakdown
        waiver_breakdown = {
            "In Waiver": metrics.in_waiver_policies,
            "Not In Waiver": metrics.total_policies - metrics.in_waiver_policies
        }
        
        # Status distribution (simplified)
        status_distribution = {
            "Active": metrics.active_policies,
            "Lapsed": metrics.total_policies - metrics.active_policies
        }
        
        return PolicyInsights(
            metrics=metrics,
            state_distribution=state_distribution,
            premium_by_state=premium_by_state,
            waiver_breakdown=waiver_breakdown,
            status_distribution=status_distribution
        )
    
    @cached(ttl=300, key_prefix="analytics:combined_dashboard:")
    def get_combined_dashboard(
        self,
        carrier_name: Optional[str] = None,
        snapshot_date: Optional[str] = None,
        report_end_dt: Optional[date] = None
    ) -> CombinedDashboard:
        """Get combined dashboard data for both policies and claims."""
        logger.info(
            f"Generating combined dashboard: carrier={carrier_name}, "
            f"policy_date={snapshot_date}, claims_date={report_end_dt}"
        )
        
        # Get policy metrics
        policy_metrics = self.get_policy_metrics(
            carrier_name=carrier_name,
            snapshot_date=snapshot_date
        )
        
        # Get claims summary
        claims_summary = self.claims_service.get_claims_summary(
            carrier_name=carrier_name,
            report_end_dt=report_end_dt
        )
        
        return CombinedDashboard(
            policy_metrics=policy_metrics,
            claims_summary=claims_summary,
            timestamp=datetime.now()
        )

