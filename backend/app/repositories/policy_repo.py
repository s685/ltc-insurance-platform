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
        self._table_name = "POLICIES"

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
                    col("POLICY_ID") == policy_id
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
                    df = df.filter(col("ISSUE_DATE") >= start_date)
                if end_date:
                    df = df.filter(col("ISSUE_DATE") <= end_date)

                # Aggregate statistics
                result = df.agg(
                    count(col("POLICY_ID")).alias("TOTAL_POLICIES"),
                    sf_sum(col("PREMIUM_AMOUNT")).alias("TOTAL_PREMIUM"),
                    avg(col("PREMIUM_AMOUNT")).alias("AVG_PREMIUM"),
                    avg(col("BENEFIT_AMOUNT")).alias("AVG_BENEFIT"),
                    avg(col("INSURED_AGE")).alias("AVG_AGE"),
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
                    df = df.filter(col("ISSUE_DATE") >= start_date)
                if end_date:
                    df = df.filter(col("ISSUE_DATE") <= end_date)

                return (
                    df.group_by("STATUS")
                    .agg(count(col("POLICY_ID")).alias("COUNT"))
                    .collect()
                )

            rows = await loop.run_in_executor(None, query)

            return {row["STATUS"]: row["COUNT"] for row in rows}
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
                    df = df.filter(col("ISSUE_DATE") >= start_date)
                if end_date:
                    df = df.filter(col("ISSUE_DATE") <= end_date)

                return (
                    df.group_by("POLICY_TYPE")
                    .agg(count(col("POLICY_ID")).alias("COUNT"))
                    .collect()
                )

            rows = await loop.run_in_executor(None, query)

            return {row["POLICY_TYPE"]: row["COUNT"] for row in rows}
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
                    df = df.filter(col("ISSUE_DATE") >= start_date)
                if end_date:
                    df = df.filter(col("ISSUE_DATE") <= end_date)

                total = df.count()
                lapsed = df.filter(col("STATUS") == PolicyStatus.LAPSED.value).count()

                return total, lapsed

            total, lapsed = await loop.run_in_executor(None, query)

            if total == 0:
                return 0.0

            return lapsed / total
        except Exception as e:
            logger.error("calculate_lapse_rate_failed", error=str(e))
            return 0.0

    def _row_to_policy(self, row: Any) -> Policy:
        """Convert Snowpark Row to Policy domain model."""
        return Policy(
            policy_id=row["POLICY_ID"],
            policy_number=row["POLICY_NUMBER"],
            policy_type=PolicyType(row["POLICY_TYPE"]),
            status=PolicyStatus(row["STATUS"]),
            issue_date=row["ISSUE_DATE"],
            effective_date=row["EFFECTIVE_DATE"],
            premium_amount=Decimal(str(row["PREMIUM_AMOUNT"])),
            benefit_amount=Decimal(str(row["BENEFIT_AMOUNT"])),
            elimination_period_days=row["ELIMINATION_PERIOD_DAYS"],
            benefit_period_months=row["BENEFIT_PERIOD_MONTHS"],
            insured_name=row["INSURED_NAME"],
            insured_age=row["INSURED_AGE"],
            insured_state=row["INSURED_STATE"],
            agent_id=row.get("AGENT_ID"),
            termination_date=row.get("TERMINATION_DATE"),
            last_premium_date=row.get("LAST_PREMIUM_DATE"),
        )

