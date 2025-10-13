"""Policy data repository."""

import logging
from typing import List, Optional, Dict, Any
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, avg, sum as sf_sum, count, when

from app.repositories.base import BaseRepository
from app.models.domain import PolicyMonthlySnapshot
from app.core.exceptions import DataNotFoundError

logger = logging.getLogger(__name__)


class PolicyRepository(BaseRepository[PolicyMonthlySnapshot]):
    """Repository for policy data access."""
    
    TABLE_NAME = "POLICY_MONTHLY_SNAPSHOT_FACT"
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_by_id(self, policy_id: int) -> Optional[PolicyMonthlySnapshot]:
        """Get policy by ID."""
        try:
            df = self.session.table(self.TABLE_NAME).filter(
                col("POLICY_ID") == policy_id
            ).limit(1)
            
            rows = df.collect()
            if not rows:
                return None
            
            return PolicyMonthlySnapshot(**rows[0].as_dict())
        except Exception as e:
            logger.error(f"Error fetching policy {policy_id}: {e}")
            raise
    
    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        carrier_name: Optional[str] = None,
        snapshot_date: Optional[str] = None,
        policy_status: Optional[str] = None,
        state: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List policies with filters."""
        try:
            df = self.session.table(self.TABLE_NAME)
            
            # Apply filters
            if carrier_name:
                df = df.filter(col("CARRIER_NAME") == carrier_name)
            
            if snapshot_date:
                df = df.filter(col("POLICY_SNAPSHOT_DATE") == snapshot_date)
            
            if policy_status:
                df = df.filter(col("POLICY_STATUS_DIM_ID") == policy_status)
            
            if state:
                df = df.filter(
                    (col("INSURED_STATE") == state) | 
                    (col("POLICY_RESIDENCE_STATE") == state)
                )
            
            # Select relevant columns
            df = df.select(
                col("POLICY_ID"),
                col("POLICY_DIM_ID"),
                col("CARRIER_NAME"),
                col("INSURED_STATE"),
                col("POLICY_RESIDENCE_STATE"),
                col("ANNUALIZED_PREMIUM"),
                col("LIFETIME_COLLECTED_PREMIUM"),
                col("PREMIUM_FREQUENCY"),
                col("ORIGINAL_EFFECTIVE_DT"),
                col("POLICY_EXPIRATION_DT"),
                col("IN_WAIVER_FLG"),
                col("IN_NONFORFEITURE_FLG"),
                col("RATED_AGE"),
                col("TOTAL_ACTIVE_CLAIMS"),
                col("TOTAL_RFBS"),
                col("TOTAL_APPROVED_RFBS"),
                col("TOTAL_DENIALS"),
                col("POLICY_SNAPSHOT_DATE")
            )
            
            # Order by snapshot date descending for consistent pagination
            df = df.order_by(col("POLICY_SNAPSHOT_DATE").desc())
            
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
            logger.error(f"Error listing policies: {e}")
            raise
    
    def count(
        self,
        carrier_name: Optional[str] = None,
        snapshot_date: Optional[str] = None,
        policy_status: Optional[str] = None,
        state: Optional[str] = None
    ) -> int:
        """Count policies matching filters."""
        try:
            df = self.session.table(self.TABLE_NAME)
            
            # Apply same filters as list
            if carrier_name:
                df = df.filter(col("CARRIER_NAME") == carrier_name)
            if snapshot_date:
                df = df.filter(col("POLICY_SNAPSHOT_DATE") == snapshot_date)
            if policy_status:
                df = df.filter(col("POLICY_STATUS_DIM_ID") == policy_status)
            if state:
                df = df.filter(
                    (col("INSURED_STATE") == state) | 
                    (col("POLICY_RESIDENCE_STATE") == state)
                )
            
            return df.count()
        except Exception as e:
            logger.error(f"Error counting policies: {e}")
            raise
    
    def get_metrics(
        self,
        carrier_name: Optional[str] = None,
        snapshot_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get aggregated policy metrics."""
        try:
            df = self.session.table(self.TABLE_NAME)
            
            # Apply filters
            if carrier_name:
                df = df.filter(col("CARRIER_NAME") == carrier_name)
            if snapshot_date:
                df = df.filter(col("POLICY_SNAPSHOT_DATE") == snapshot_date)
            
            # Calculate metrics
            metrics_df = df.agg([
                count("POLICY_ID").alias("total_policies"),
                count(
                    when(col("POLICY_EXPIRATION_DT").isNull(), col("POLICY_ID"))
                ).alias("active_policies"),
                count(
                    when(col("IN_NONFORFEITURE_FLG") == "Yes", col("POLICY_ID"))
                ).alias("in_forfeiture_policies"),
                count(
                    when(col("IN_WAIVER_FLG") == "Yes", col("POLICY_ID"))
                ).alias("in_waiver_policies"),
                avg("ANNUALIZED_PREMIUM").alias("avg_premium"),
                sf_sum("ANNUALIZED_PREMIUM").alias("total_premium_revenue"),
                avg("RATED_AGE").alias("avg_insured_age"),
                count(
                    when(col("TOTAL_ACTIVE_CLAIMS") > 0, col("POLICY_ID"))
                ).alias("policies_with_claims"),
                sf_sum("TOTAL_ACTIVE_CLAIMS").alias("total_claims_count")
            ])
            
            result = metrics_df.collect()[0].as_dict()
            
            # Convert keys to lowercase (Snowflake returns uppercase)
            result = {k.lower(): v for k, v in result.items()}
            
            # Calculate derived metrics
            total_policies = result.get("total_policies", 0) or 0
            active_policies = result.get("active_policies", 0) or 0
            total_claims_count = result.get("total_claims_count", 0) or 0
            
            if total_policies > 0:
                result["lapse_rate"] = (
                    (total_policies - active_policies) / total_policies * 100
                )
                result["avg_claims_per_policy"] = (
                    total_claims_count / total_policies if total_claims_count else 0
                )
            else:
                result["lapse_rate"] = 0
                result["avg_claims_per_policy"] = 0
            
            return result
        
        except Exception as e:
            logger.error(f"Error calculating policy metrics: {e}")
            raise
    
    def get_state_distribution(
        self,
        carrier_name: Optional[str] = None,
        snapshot_date: Optional[str] = None
    ) -> Dict[str, int]:
        """Get policy count by state."""
        try:
            df = self.session.table(self.TABLE_NAME)
            
            if carrier_name:
                df = df.filter(col("CARRIER_NAME") == carrier_name)
            if snapshot_date:
                df = df.filter(col("POLICY_SNAPSHOT_DATE") == snapshot_date)
            
            # Group by state
            state_df = df.group_by("INSURED_STATE").agg(
                count("POLICY_ID").alias("count")
            ).sort(col("count").desc()).limit(10)
            
            # Collect results and convert to dict
            rows = state_df.collect()
            result = {}
            for row in rows:
                row_dict = row.as_dict()
                state = row_dict.get("INSURED_STATE") or row_dict.get("insured_state")
                count_val = row_dict.get("COUNT") or row_dict.get("count")
                if state:
                    result[state] = count_val
            return result
        
        except Exception as e:
            logger.error(f"Error getting state distribution: {e}")
            raise
    
    def get_premium_by_state(
        self,
        carrier_name: Optional[str] = None,
        snapshot_date: Optional[str] = None
    ) -> Dict[str, float]:
        """Get total premium revenue by state."""
        try:
            df = self.session.table(self.TABLE_NAME)
            
            if carrier_name:
                df = df.filter(col("CARRIER_NAME") == carrier_name)
            if snapshot_date:
                df = df.filter(col("POLICY_SNAPSHOT_DATE") == snapshot_date)
            
            # Group by state
            premium_df = df.group_by("INSURED_STATE").agg(
                sf_sum("ANNUALIZED_PREMIUM").alias("total_premium")
            ).sort(col("total_premium").desc()).limit(10)
            
            # Collect results and convert to dict
            rows = premium_df.collect()
            result = {}
            for row in rows:
                row_dict = row.as_dict()
                state = row_dict.get("INSURED_STATE") or row_dict.get("insured_state")
                premium = row_dict.get("TOTAL_PREMIUM") or row_dict.get("total_premium")
                if state:
                    result[state] = premium
            return result
        
        except Exception as e:
            logger.error(f"Error getting premium by state: {e}")
            raise

