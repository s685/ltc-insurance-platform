"""Claims data repository with complex filtering logic."""

import logging
from typing import List, Optional, Dict, Any
from datetime import date
from snowflake.snowpark import Session
from snowflake.snowpark.functions import (
    col, avg, sum as sf_sum, count, when, 
    last_day, to_timestamp, lit
)

from app.repositories.base import BaseRepository
from app.models.domain import ClaimsTPAFeeWorksheet
from app.core.exceptions import DataNotFoundError

logger = logging.getLogger(__name__)


class ClaimsRepository(BaseRepository[ClaimsTPAFeeWorksheet]):
    """Repository for claims data access with complex business logic."""
    
    TABLE_NAME = "CLAIMS_TPA_FEE_WORKSHEET_SNAPSHOT_FACT"
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_by_id(self, claim_id: str) -> Optional[ClaimsTPAFeeWorksheet]:
        """Get claim by ID."""
        try:
            df = self.session.table(self.TABLE_NAME).filter(
                col("TPA_FEE_WORKSHEET_SNAPSHOT_FACT_ID") == claim_id
            ).limit(1)
            
            rows = df.collect()
            if not rows:
                return None
            
            return ClaimsTPAFeeWorksheet(**rows[0].as_dict())
        except Exception as e:
            logger.error(f"Error fetching claim {claim_id}: {e}")
            raise
    
    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        carrier_name: Optional[str] = None,
        report_end_dt: Optional[date] = None,
        decision_types: Optional[List[str]] = None,
        ongoing_rate_months: Optional[List[int]] = None,
        categories: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """List claims with complex filtering logic."""
        try:
            df = self.session.table(self.TABLE_NAME)
            
            # Apply core business logic filter
            # WHERE ((ONGOING_RATE_MONTH = '1' AND IS_INITIAL_DECISION_FLAG IN (0,1))
            #     OR (ONGOING_RATE_MONTH = '0' AND IS_INITIAL_DECISION_FLAG = 1)
            #     OR (ONGOING_RATE_MONTH = '2' AND IS_INITIAL_DECISION_FLAG IN (0,1)))
            
            core_filter = (
                ((col("ONGOING_RATE_MONTH") == 1) & col("IS_INITIAL_DECISION_FLAG").isin([0, 1])) |
                ((col("ONGOING_RATE_MONTH") == 0) & (col("IS_INITIAL_DECISION_FLAG") == 1)) |
                ((col("ONGOING_RATE_MONTH") == 2) & col("IS_INITIAL_DECISION_FLAG").isin([0, 1]))
            )
            df = df.filter(core_filter)
            
            # Carrier filter
            if carrier_name:
                df = df.filter(col("CARRIER_NAME") == carrier_name)
            
            # Date filter - snapshot_date = last_day(to_timestamp(report_end_dt))
            if report_end_dt:
                # Convert date to string format for Snowflake
                date_str = report_end_dt.strftime('%Y-%m-%d')
                df = df.filter(
                    col("SNAPSHOT_DATE") == last_day(to_timestamp(lit(date_str)))
                )
            
            # Decision types filter
            if decision_types:
                df = df.filter(col("DECISION").isin(decision_types))
            
            # Ongoing rate month filter (user override)
            if ongoing_rate_months:
                df = df.filter(col("ONGOING_RATE_MONTH").isin(ongoing_rate_months))
            
            # Category filter (based on facility indicators)
            if categories:
                category_filters = []
                if "Facility" in categories:
                    category_filters.append(
                        (col("INITIAL_DECISIONS_FACILITIES") > 0) |
                        (col("ONGOING_ALL_FACILITIES") > 0) |
                        (col("RETRO_ALL_FACILITIES") > 0)
                    )
                if "Home Health" in categories:
                    category_filters.append(
                        (col("INITIAL_DECISIONS_HOME_HEALTH") > 0) |
                        (col("ONGOING_HOME_HEALTH") > 0) |
                        (col("RETRO_HOME_HEALTH") > 0)
                    )
                if "Other" in categories:
                    category_filters.append(
                        (col("INITIAL_DECISIONS_ALL_OTHER") > 0) |
                        (col("ALL_OTHER") > 0) |
                        (col("RETRO_ALL_OTHER") > 0)
                    )
                
                if category_filters:
                    combined_filter = category_filters[0]
                    for f in category_filters[1:]:
                        combined_filter = combined_filter | f
                    df = df.filter(combined_filter)
            
            # Order by snapshot date descending for consistent pagination
            df = df.order_by(col("SNAPSHOT_DATE").desc())
            
            # Apply pagination - Snowpark requires ordering before offset
            if offset > 0:
                df = df.limit(limit + offset)
                rows = df.collect()[offset:]  # Skip offset rows after collection
            else:
                df = df.limit(limit)
                rows = df.collect()
            
            # Convert to list of dicts with lowercase keys
            return [
                {k.lower(): v for k, v in row.as_dict().items()}
                for row in rows
            ]
        
        except Exception as e:
            logger.error(f"Error listing claims: {e}")
            raise
    
    def count(
        self,
        carrier_name: Optional[str] = None,
        report_end_dt: Optional[date] = None,
        decision_types: Optional[List[str]] = None,
        ongoing_rate_months: Optional[List[int]] = None
    ) -> int:
        """Count claims matching filters."""
        try:
            df = self.session.table(self.TABLE_NAME)
            
            # Apply core business logic filter
            core_filter = (
                ((col("ONGOING_RATE_MONTH") == 1) & col("IS_INITIAL_DECISION_FLAG").isin([0, 1])) |
                ((col("ONGOING_RATE_MONTH") == 0) & (col("IS_INITIAL_DECISION_FLAG") == 1)) |
                ((col("ONGOING_RATE_MONTH") == 2) & col("IS_INITIAL_DECISION_FLAG").isin([0, 1]))
            )
            df = df.filter(core_filter)
            
            if carrier_name:
                df = df.filter(col("CARRIER_NAME") == carrier_name)
            
            if report_end_dt:
                date_str = report_end_dt.strftime('%Y-%m-%d')
                df = df.filter(
                    col("SNAPSHOT_DATE") == last_day(to_timestamp(lit(date_str)))
                )
            
            if decision_types:
                df = df.filter(col("DECISION").isin(decision_types))
            
            if ongoing_rate_months:
                df = df.filter(col("ONGOING_RATE_MONTH").isin(ongoing_rate_months))
            
            return df.count()
        except Exception as e:
            logger.error(f"Error counting claims: {e}")
            raise
    
    def get_summary(
        self,
        carrier_name: Optional[str] = None,
        report_end_dt: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get claims summary statistics."""
        try:
            df = self.session.table(self.TABLE_NAME)
            
            # Apply core filter
            core_filter = (
                ((col("ONGOING_RATE_MONTH") == 1) & col("IS_INITIAL_DECISION_FLAG").isin([0, 1])) |
                ((col("ONGOING_RATE_MONTH") == 0) & (col("IS_INITIAL_DECISION_FLAG") == 1)) |
                ((col("ONGOING_RATE_MONTH") == 2) & col("IS_INITIAL_DECISION_FLAG").isin([0, 1]))
            )
            df = df.filter(core_filter)
            
            if carrier_name:
                df = df.filter(col("CARRIER_NAME") == carrier_name)
            
            if report_end_dt:
                date_str = report_end_dt.strftime('%Y-%m-%d')
                df = df.filter(
                    col("SNAPSHOT_DATE") == last_day(to_timestamp(lit(date_str)))
                )
            
            # Calculate summary metrics
            summary_df = df.agg([
                count("*").alias("total_claims"),
                count(when(col("DECISION") == "Approved", 1)).alias("approved_claims"),
                count(when(col("DECISION") == "Denied", 1)).alias("denied_claims"),
                count(when(col("DECISION") == "In Assessment", 1)).alias("in_assessment_claims"),
                avg("RFB_PROCESS_TO_DECISION_TAT").alias("avg_processing_time"),
                count(when(col("RETRO_MONTHS") > 0, 1)).alias("total_retro_claims"),
                
                # By category
                sf_sum("INITIAL_DECISIONS_FACILITIES").alias("facility_initial"),
                sf_sum("ONGOING_ALL_FACILITIES").alias("facility_ongoing"),
                sf_sum("RETRO_ALL_FACILITIES").alias("facility_retro"),
                
                sf_sum("INITIAL_DECISIONS_HOME_HEALTH").alias("home_health_initial"),
                sf_sum("ONGOING_HOME_HEALTH").alias("home_health_ongoing"),
                sf_sum("RETRO_HOME_HEALTH").alias("home_health_retro"),
                
                sf_sum("INITIAL_DECISIONS_ALL_OTHER").alias("other_initial"),
                sf_sum("ALL_OTHER").alias("other_ongoing"),
                sf_sum("RETRO_ALL_OTHER").alias("other_retro"),
                
                # By ongoing rate month
                count(when(col("ONGOING_RATE_MONTH") == 0, 1)).alias("initial_decisions"),
                count(when(col("ONGOING_RATE_MONTH") == 1, 1)).alias("ongoing_decisions"),
                count(when(col("ONGOING_RATE_MONTH") == 2, 1)).alias("restoration_decisions"),
            ])
            
            result = summary_df.collect()[0].as_dict()
            
            # Convert keys to lowercase (Snowflake returns uppercase)
            result = {k.lower(): v for k, v in result.items()}
            
            # Calculate derived metrics
            total_claims = result.get("total_claims", 0) or 0
            approved_claims = result.get("approved_claims", 0) or 0
            total_retro_claims = result.get("total_retro_claims", 0) or 0
            
            if total_claims > 0:
                result["approval_rate"] = (approved_claims / total_claims * 100)
                result["retro_percentage"] = (total_retro_claims / total_claims * 100)
            else:
                result["approval_rate"] = 0
                result["retro_percentage"] = 0
            
            # Calculate category totals
            result["facility_claims"] = (
                (result.get("facility_initial", 0) or 0) + 
                (result.get("facility_ongoing", 0) or 0) + 
                (result.get("facility_retro", 0) or 0)
            )
            result["home_health_claims"] = (
                (result.get("home_health_initial", 0) or 0) + 
                (result.get("home_health_ongoing", 0) or 0) + 
                (result.get("home_health_retro", 0) or 0)
            )
            result["other_claims"] = (
                (result.get("other_initial", 0) or 0) + 
                (result.get("other_ongoing", 0) or 0) + 
                (result.get("other_retro", 0) or 0)
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Error calculating claims summary: {e}")
            raise
    
    def get_decision_breakdown(
        self,
        carrier_name: Optional[str] = None,
        report_end_dt: Optional[date] = None
    ) -> Dict[str, int]:
        """Get count of claims by decision type."""
        try:
            df = self.session.table(self.TABLE_NAME)
            
            # Apply core filter
            core_filter = (
                ((col("ONGOING_RATE_MONTH") == 1) & col("IS_INITIAL_DECISION_FLAG").isin([0, 1])) |
                ((col("ONGOING_RATE_MONTH") == 0) & (col("IS_INITIAL_DECISION_FLAG") == 1)) |
                ((col("ONGOING_RATE_MONTH") == 2) & col("IS_INITIAL_DECISION_FLAG").isin([0, 1]))
            )
            df = df.filter(core_filter)
            
            if carrier_name:
                df = df.filter(col("CARRIER_NAME") == carrier_name)
            
            if report_end_dt:
                date_str = report_end_dt.strftime('%Y-%m-%d')
                df = df.filter(
                    col("SNAPSHOT_DATE") == last_day(to_timestamp(lit(date_str)))
                )
            
            # Group by decision
            decision_df = df.group_by("DECISION").agg(
                count("*").alias("count")
            )
            
            # Collect results and convert to dict
            rows = decision_df.collect()
            result = {}
            for row in rows:
                row_dict = row.as_dict()
                # Convert keys to lowercase (Snowflake returns uppercase)
                decision = row_dict.get("DECISION") or row_dict.get("decision")
                count_val = row_dict.get("COUNT") or row_dict.get("count")
                if decision:
                    result[decision] = count_val
            return result
        
        except Exception as e:
            logger.error(f"Error getting decision breakdown: {e}")
            raise
    
    def get_retro_analysis(
        self,
        carrier_name: Optional[str] = None,
        report_end_dt: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get detailed retro claims analysis."""
        try:
            df = self.session.table(self.TABLE_NAME)
            
            # Apply core filter
            core_filter = (
                ((col("ONGOING_RATE_MONTH") == 1) & col("IS_INITIAL_DECISION_FLAG").isin([0, 1])) |
                ((col("ONGOING_RATE_MONTH") == 0) & (col("IS_INITIAL_DECISION_FLAG") == 1)) |
                ((col("ONGOING_RATE_MONTH") == 2) & col("IS_INITIAL_DECISION_FLAG").isin([0, 1]))
            )
            df = df.filter(core_filter)
            
            if carrier_name:
                df = df.filter(col("CARRIER_NAME") == carrier_name)
            
            if report_end_dt:
                date_str = report_end_dt.strftime('%Y-%m-%d')
                df = df.filter(
                    col("SNAPSHOT_DATE") == last_day(to_timestamp(lit(date_str)))
                )
            
            # Filter retro claims
            retro_df = df.filter(col("RETRO_MONTHS") > 0)
            
            # Calculate retro metrics
            retro_metrics = retro_df.agg([
                count("*").alias("total_retro_claims"),
                avg("RETRO_MONTHS").alias("avg_retro_months"),
                sf_sum("RETRO_ALL_FACILITIES").alias("total_retro_facilities"),
                sf_sum("RETRO_HOME_HEALTH").alias("total_retro_home_health"),
                sf_sum("RETRO_ALL_OTHER").alias("total_retro_other")
            ])
            
            result = retro_metrics.collect()[0].as_dict()
            
            # Convert keys to lowercase (Snowflake returns uppercase)
            result = {k.lower(): v for k, v in result.items()}
            
            # Convert Decimal to float for JSON serialization
            for key, value in result.items():
                if hasattr(value, '__float__'):  # Handles Decimal, numpy types, etc.
                    result[key] = float(value) if value is not None else 0.0
                elif value is None:
                    result[key] = 0
            
            return result
        
        except Exception as e:
            logger.error(f"Error in retro analysis: {e}")
            raise

