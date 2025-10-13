"""Policy repository for policy data access operations."""

import asyncio
from datetime import date
from decimal import Decimal
from typing import Any, Optional, List, Dict

import structlog
from snowflake.snowpark import Session
from snowflake.snowpark.functions import avg, col, count, sum as sf_sum

from ..models.domain import Policy, PolicyStatus, PolicyType
from .base import BaseRepository

logger = structlog.get_logger(__name__)


class PolicyRepository(BaseRepository[Policy]):
    """Repository for policy data access."""

    def __init__(self, session: Session) -> None:
        """Initialize policy repository."""
        super().__init__(session)
        self._table_name = "POLICY_MONTHLY_SNAPSHOT_FACT"

    @property
    def table_name(self) -> str:
        """Get policies table name."""
        return self._table_name

    async def find_by_id(self, policy_id: str) -> Optional[Policy]:
        """Find policy by ID."""
        try:
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None,
                lambda: self.session.table(self.table_name).filter(
                    col("POLICY_MONTHLY_SNAPSHOT_ID") == policy_id
                ),
            )
            rows = await loop.run_in_executor(None, df.collect)

            if not rows:
                return None

            return self._row_to_policy(rows[0])
        except Exception as e:
            logger.error("find_policy_by_id_failed", policy_id=policy_id, error=str(e))
            return None

    async def find_all(
        self,
        limit: Optional[int] = 100,
        offset: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Policy]:
        """Find all policies with filtering and pagination."""
        try:
            loop = asyncio.get_event_loop()

            def query() -> Any:
                df = self.session.table(self.table_name)
                df = self._apply_filters(df, filters)

                if offset:
                    df = df.offset(offset)
                if limit:
                    df = df.limit(limit)

                return df.collect()

            rows = await loop.run_in_executor(None, query)
            return [self._row_to_policy(row) for row in rows]
        except Exception as e:
            logger.error("find_all_policies_failed", error=str(e))
            return []

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count policies with optional filtering."""
        try:
            loop = asyncio.get_event_loop()

            def query() -> int:
                df = self.session.table(self.table_name)
                df = self._apply_filters(df, filters)
                return df.count()

            return await loop.run_in_executor(None, query)
        except Exception as e:
            logger.error("count_policies_failed", error=str(e))
            return 0

    async def get_policy_metrics(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get policy metrics and statistics."""
        try:
            loop = asyncio.get_event_loop()

            def query() -> Any:
                df = self.session.table(self.table_name)

                if start_date:
                    df = df.filter(col("ORIGINAL_EFFECTIVE_DT") >= start_date)
                if end_date:
                    df = df.filter(col("ORIGINAL_EFFECTIVE_DT") <= end_date)

                # Aggregate statistics - adapted for new table structure
                result = df.agg(
                    count(col("POLICY_MONTHLY_SNAPSHOT_ID")).alias("TOTAL_POLICIES"),
                    sf_sum(col("ANNUALIZED_PREMIUM")).alias("TOTAL_PREMIUM"),
                    avg(col("ANNUALIZED_PREMIUM")).alias("AVG_PREMIUM"),
                    avg(col("TOTAL_REQUEST_FOR_REIMBURSMENT_BENEFIT")).alias("AVG_BENEFIT"),
                    avg(col("RATED_AGE")).alias("AVG_AGE"),
                ).collect()

                return result[0] if result else None

            row = await loop.run_in_executor(None, query)

            if not row:
                return {}

            return {
                "total_policies": row["TOTAL_POLICIES"] or 0,
                "total_premium": Decimal(str(row["TOTAL_PREMIUM"] or 0)),
                "avg_premium": Decimal(str(row["AVG_PREMIUM"] or 0)),
                "avg_benefit": Decimal(str(row["AVG_BENEFIT"] or 0)),
                "avg_insured_age": float(row["AVG_AGE"] or 0),
            }
        except Exception as e:
            logger.error("get_policy_metrics_failed", error=str(e))
            return {}

    async def get_policies_by_status(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> Dict[str, int]:
        """Get policy counts grouped by status."""
        try:
            loop = asyncio.get_event_loop()

            def query() -> Any:
                df = self.session.table(self.table_name)

                if start_date:
                    df = df.filter(col("ORIGINAL_EFFECTIVE_DT") >= start_date)
                if end_date:
                    df = df.filter(col("ORIGINAL_EFFECTIVE_DT") <= end_date)

                return (
                    df.group_by("CLAIM_STATUS_CD")
                    .agg(count(col("POLICY_MONTHLY_SNAPSHOT_ID")).alias("COUNT"))
                    .collect()
                )

            rows = await loop.run_in_executor(None, query)

            return {row["CLAIM_STATUS_CD"]: row["COUNT"] for row in rows if row["CLAIM_STATUS_CD"]}
        except Exception as e:
            logger.error("get_policies_by_status_failed", error=str(e))
            return {}

    async def get_policies_by_type(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> Dict[str, int]:
        """Get policy counts grouped by type."""
        try:
            loop = asyncio.get_event_loop()

            def query() -> Any:
                df = self.session.table(self.table_name)

                if start_date:
                    df = df.filter(col("ORIGINAL_EFFECTIVE_DT") >= start_date)
                if end_date:
                    df = df.filter(col("ORIGINAL_EFFECTIVE_DT") <= end_date)

                # Use BENEFIT_INFLATION as a proxy for policy type
                return (
                    df.group_by("BENEFIT_INFLATION")
                    .agg(count(col("POLICY_MONTHLY_SNAPSHOT_ID")).alias("COUNT"))
                    .collect()
                )

            rows = await loop.run_in_executor(None, query)

            return {row["BENEFIT_INFLATION"] or "UNKNOWN": row["COUNT"] for row in rows}
        except Exception as e:
            logger.error("get_policies_by_type_failed", error=str(e))
            return {}

    async def calculate_lapse_rate(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> float:
        """Calculate policy lapse rate."""
        try:
            loop = asyncio.get_event_loop()

            def query() -> tuple[int, int]:
                df = self.session.table(self.table_name)

                if start_date:
                    df = df.filter(col("ORIGINAL_EFFECTIVE_DT") >= start_date)
                if end_date:
                    df = df.filter(col("ORIGINAL_EFFECTIVE_DT") <= end_date)

                total = df.count()
                # Count policies with expiration dates as "lapsed"
                lapsed = df.filter(col("POLICY_EXPIRATION_DT").isNotNull()).count()

                return total, lapsed

            total, lapsed = await loop.run_in_executor(None, query)

            if total == 0:
                return 0.0

            return lapsed / total
        except Exception as e:
            logger.error("calculate_lapse_rate_failed", error=str(e))
            return 0.0

    def _row_to_policy(self, row: Any) -> Policy:
        """Convert Snowpark Row to Policy domain model from POLICY_MONTHLY_SNAPSHOT_FACT."""
        # Helper function to safely convert to Decimal
        def to_decimal(value: Any) -> Optional[Decimal]:
            if value is None:
                return None
            return Decimal(str(value))
        
        return Policy(
            # Core identifiers
            policy_monthly_snapshot_id=str(row["POLICY_MONTHLY_SNAPSHOT_ID"]),
            policy_dim_id=str(row["POLICY_DIM_ID"]),
            policy_id=int(row["POLICY_ID"]),
            
            # Insured information
            insured_life_dim_id=row.get("INSURED_LIFE_DIM_ID"),
            insured_life_id=row.get("INSURED_LIFE_ID"),
            insured_city=row.get("INSURED_CITY"),
            insured_state=row.get("INSURED_STATE"),
            insured_zip=row.get("INSURED_ZIP"),
            policy_residence_state=row.get("POLICY_RESIDENCE_STATE"),
            claimant_sex=row.get("CLAIMANT_SEX"),
            rated_age=row.get("RATED_AGE"),
            
            # Premium information
            annualized_premium=to_decimal(row.get("ANNUALIZED_PREMIUM")),
            lifetime_collected_premium=to_decimal(row.get("LIFETIME_COLLECTED_PREMIUM")),
            lifetime_waiver_premium=to_decimal(row.get("LIFETIME_WAIVER_PREMIUM")),
            premium_frequency=row.get("PREMIUM_FREQUENCY"),
            offset_premium=to_decimal(row.get("OFFSET_PREMIUM")),
            
            # Status and dates
            policy_status_dim_id=row.get("POLICY_STATUS_DIM_ID"),
            original_effective_dt=row.get("ORIGINAL_EFFECTIVE_DT"),
            coverage_effective_dt=row.get("COVERAGE_EFFECTIVE_DT"),
            coverage_status_dt=row.get("COVERAGE_STATUS_DT"),
            coverage_expiration_dt=row.get("COVERAGE_EXPIRATION_DT"),
            policy_expiration_dt=row.get("POLICY_EXPIRATION_DT"),
            appn_rcv_dt=row.get("APPN_RCV_DT"),
            appn_sig_dt=row.get("APPN_SIG_DT"),
            appn_sig_state=row.get("APPN_SIG_STATE"),
            paid_to_date=row.get("PAID_TO_DATE"),
            
            # Coverage information
            current_coverage_id=row.get("CURRENT_COVERAGE_ID"),
            current_coverage_dim_id=row.get("CURRENT_COVERAGE_DIM_ID"),
            tax_qualification_dim_id=row.get("TAX_QUALIFICATION_DIM_ID"),
            benefit_inflation=row.get("BENEFIT_INFLATION"),
            benefit_increase=row.get("BENEFIT_INCREASE"),
            
            # Waiver information
            in_waiver_flg=row.get("IN_WAIVER_FLG"),
            current_waiver_effective_date=row.get("CURRENT_WAIVER_EFFECTIVE_DATE"),
            current_waiver_expiration_date=row.get("CURRENT_WAIVER_EXPIRATION_DATE"),
            
            # Claim information
            latest_claim_dim_id=row.get("LATEST_CLAIM_DIM_ID"),
            latest_claim_id=row.get("LATEST_CLAIM_ID"),
            claim_status_cd=row.get("CLAIM_STATUS_CD"),
            first_eob_decision_dt=row.get("FIRST_EOB_DECISION_DT"),
            latest_eob_decision_dt=row.get("LATEST_EOB_DECISION_DT"),
            latest_claim_incurred_dt=row.get("LATEST_CLAIM_INCURRED_DT"),
            latest_claim_expiration_dt=row.get("LATEST_CLAIM_EXPIRATION_DT"),
            total_active_claims=row.get("TOTAL_ACTIVE_CLAIMS"),
            total_rfbs=row.get("TOTAL_RFBS"),
            total_approved_rfbs=row.get("TOTAL_APPROVED_RFBS"),
            total_denials=row.get("TOTAL_DENIALS"),
            
            # Financial summary
            total_request_for_reimbursment_benefit=to_decimal(row.get("TOTAL_REQUEST_FOR_REIMBURSMENT_BENEFIT")),
            total_request_for_reimbursment_admin=to_decimal(row.get("TOTAL_REQUEST_FOR_REIMBURSMENT_ADMIN")),
            total_request_for_reimbursment_pending=to_decimal(row.get("TOTAL_REQUEST_FOR_REIMBURSMENT_PENDING")),
            
            # Metadata
            carrier_name=row.get("CARRIER_NAME"),
            environment=row.get("ENVIRONMENT"),
            policy_snapshot_date=row.get("POLICY_SNAPSHOT_DATE"),
        )

