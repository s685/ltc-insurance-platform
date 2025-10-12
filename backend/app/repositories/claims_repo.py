"""Claims repository for claim data access operations."""

import asyncio
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional, List, Dict

import structlog
from snowflake.snowpark import Session
from snowflake.snowpark.functions import avg, col, count, sum as sf_sum

from ..models.domain import Claim, ClaimStatus
from .base import BaseRepository

logger = structlog.get_logger(__name__)


class ClaimsRepository(BaseRepository[Claim]):
    """Repository for claim data access."""

    def __init__(self, session: Session) -> None:
        """Initialize claims repository."""
        super().__init__(session)
        self._table_name = "CLAIMS"

    @property
    def table_name(self) -> str:
        """Get claims table name."""
        return self._table_name

    async def find_by_id(self, claim_id: str) -> Optional[Claim]:
        """Find claim by ID."""
        try:
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None,
                lambda: self.session.table(self.table_name).filter(
                    col("CLAIM_ID") == claim_id
                ),
            )
            rows = await loop.run_in_executor(None, df.collect)

            if not rows:
                return None

            return self._row_to_claim(rows[0])
        except Exception as e:
            logger.error("find_claim_by_id_failed", claim_id=claim_id, error=str(e))
            return None

    async def find_all(
        self,
        limit: Optional[int] = 100,
        offset: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Claim]:
        """Find all claims with filtering and pagination."""
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
            return [self._row_to_claim(row) for row in rows]
        except Exception as e:
            logger.error("find_all_claims_failed", error=str(e))
            return []

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count claims with optional filtering."""
        try:
            loop = asyncio.get_event_loop()

            def query() -> int:
                df = self.session.table(self.table_name)
                df = self._apply_filters(df, filters)
                return df.count()

            return await loop.run_in_executor(None, query)
        except Exception as e:
            logger.error("count_claims_failed", error=str(e))
            return 0

    async def get_claims_summary(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get claims summary statistics."""
        try:
            loop = asyncio.get_event_loop()

            def query() -> Any:
                df = self.session.table(self.table_name)

                if start_date:
                    df = df.filter(col("SUBMISSION_DATE") >= start_date)
                if end_date:
                    df = df.filter(col("SUBMISSION_DATE") <= end_date)

                # Aggregate statistics
                result = df.agg(
                    count(col("CLAIM_ID")).alias("TOTAL_CLAIMS"),
                    sf_sum(col("CLAIM_AMOUNT")).alias("TOTAL_CLAIM_AMOUNT"),
                    sf_sum(col("APPROVED_AMOUNT")).alias("TOTAL_APPROVED_AMOUNT"),
                    sf_sum(col("PAID_AMOUNT")).alias("TOTAL_PAID_AMOUNT"),
                    avg(col("CLAIM_AMOUNT")).alias("AVG_CLAIM_AMOUNT"),
                ).collect()

                return result[0] if result else None

            row = await loop.run_in_executor(None, query)

            if not row:
                return {}

            return {
                "total_claims": row["TOTAL_CLAIMS"] or 0,
                "total_claim_amount": Decimal(str(row["TOTAL_CLAIM_AMOUNT"] or 0)),
                "total_approved_amount": Decimal(
                    str(row["TOTAL_APPROVED_AMOUNT"] or 0)
                ),
                "total_paid_amount": Decimal(str(row["TOTAL_PAID_AMOUNT"] or 0)),
                "avg_claim_amount": Decimal(str(row["AVG_CLAIM_AMOUNT"] or 0)),
            }
        except Exception as e:
            logger.error("get_claims_summary_failed", error=str(e))
            return {}

    async def get_claims_by_status(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> Dict[str, int]:
        """Get claim counts grouped by status."""
        try:
            loop = asyncio.get_event_loop()

            def query() -> Any:
                df = self.session.table(self.table_name)

                if start_date:
                    df = df.filter(col("SUBMISSION_DATE") >= start_date)
                if end_date:
                    df = df.filter(col("SUBMISSION_DATE") <= end_date)

                return (
                    df.group_by("STATUS")
                    .agg(count(col("CLAIM_ID")).alias("COUNT"))
                    .collect()
                )

            rows = await loop.run_in_executor(None, query)

            return {row["STATUS"]: row["COUNT"] for row in rows}
        except Exception as e:
            logger.error("get_claims_by_status_failed", error=str(e))
            return {}

    async def get_avg_processing_days(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> float:
        """Calculate average processing days for approved claims."""
        try:
            loop = asyncio.get_event_loop()

            def query() -> Any:
                df = self.session.table(self.table_name)

                if start_date:
                    df = df.filter(col("SUBMISSION_DATE") >= start_date)
                if end_date:
                    df = df.filter(col("SUBMISSION_DATE") <= end_date)

                # Filter to approved claims with approval dates
                df = df.filter(
                    (col("STATUS") == ClaimStatus.APPROVED.value)
                    | (col("STATUS") == ClaimStatus.PAID.value)
                )
                df = df.filter(col("APPROVAL_DATE").isNotNull())

                # Calculate days difference
                result = df.select(
                    avg(
                        col("APPROVAL_DATE").cast("date")
                        - col("SUBMISSION_DATE").cast("date")
                    ).alias("AVG_DAYS")
                ).collect()

                return result[0]["AVG_DAYS"] if result and result[0]["AVG_DAYS"] else 0

            return await loop.run_in_executor(None, query)
        except Exception as e:
            logger.error("get_avg_processing_days_failed", error=str(e))
            return 0.0

    def _row_to_claim(self, row: Any) -> Claim:
        """Convert Snowpark Row to Claim domain model."""
        return Claim(
            claim_id=row["CLAIM_ID"],
            claim_number=row["CLAIM_NUMBER"],
            policy_id=row["POLICY_ID"],
            status=ClaimStatus(row["STATUS"]),
            claim_type=row["CLAIM_TYPE"],
            submission_date=row["SUBMISSION_DATE"],
            service_start_date=row["SERVICE_START_DATE"],
            service_end_date=row.get("SERVICE_END_DATE"),
            claim_amount=Decimal(str(row["CLAIM_AMOUNT"])),
            approved_amount=(
                Decimal(str(row["APPROVED_AMOUNT"]))
                if row.get("APPROVED_AMOUNT")
                else None
            ),
            paid_amount=(
                Decimal(str(row["PAID_AMOUNT"])) if row.get("PAID_AMOUNT") else None
            ),
            denial_reason=row.get("DENIAL_REASON"),
            approval_date=row.get("APPROVAL_DATE"),
            payment_date=row.get("PAYMENT_DATE"),
            reviewer_id=row.get("REVIEWER_ID"),
            facility_name=row.get("FACILITY_NAME"),
            diagnosis_codes=row.get("DIAGNOSIS_CODES", "").split(",")
            if row.get("DIAGNOSIS_CODES")
            else [],
        )

