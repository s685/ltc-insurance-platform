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
        self._table_name = "CLAIMS_TPA_FEE_WORKSHEET_SNAPSHOT_FACT"

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
                    col("TPA_FEE_WORKSHEET_SNAPSHOT_FACT_ID") == claim_id
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
        self,
        snapshot_date: Optional[date] = None,
        carrier_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get claims summary statistics for a specific monthly snapshot."""
        try:
            loop = asyncio.get_event_loop()

            def query() -> Any:
                df = self.session.table(self.table_name)

                if snapshot_date:
                    df = df.filter(col("SNAPSHOT_DATE") == snapshot_date)
                if carrier_name:
                    df = df.filter(col("CARRIER_NAME") == carrier_name)

                # Aggregate statistics - adapted for new table structure
                result = df.agg(
                    count(col("TPA_FEE_WORKSHEET_SNAPSHOT_FACT_ID")).alias("TOTAL_CLAIMS"),
                    # Calculate total decisions as a proxy for claim amount
                    sf_sum(col("ONGOING_RATE_MONTH")).alias("TOTAL_ONGOING_MONTHS"),
                    sf_sum(col("INITIAL_DECISIONS_FACILITIES") + col("INITIAL_DECISIONS_HOME_HEALTH") + col("INITIAL_DECISIONS_ALL_OTHER")).alias("TOTAL_INITIAL_DECISIONS"),
                    avg(col("ONGOING_RATE_MONTH")).alias("AVG_RATE_MONTH"),
                ).collect()

                return result[0] if result else None

            row = await loop.run_in_executor(None, query)

            if not row:
                return {}

            return {
                "total_claims": row["TOTAL_CLAIMS"] or 0,
                "total_ongoing_months": row["TOTAL_ONGOING_MONTHS"] or 0,
                "total_initial_decisions": row["TOTAL_INITIAL_DECISIONS"] or 0,
                "avg_rate_month": float(row["AVG_RATE_MONTH"] or 0),
                # Map to expected keys for backward compatibility
                "total_claim_amount": Decimal(str(row["TOTAL_ONGOING_MONTHS"] or 0)),
                "total_approved_amount": Decimal(str(row["TOTAL_INITIAL_DECISIONS"] or 0)),
                "total_paid_amount": Decimal("0"),  # Not directly available
                "avg_claim_amount": Decimal(str(row["AVG_RATE_MONTH"] or 0)),
            }
        except Exception as e:
            logger.error("get_claims_summary_failed", error=str(e))
            return {}

    async def get_claims_by_status(
        self,
        snapshot_date: Optional[date] = None,
        carrier_name: Optional[str] = None,
    ) -> Dict[str, int]:
        """Get claim counts grouped by status for a specific monthly snapshot."""
        try:
            loop = asyncio.get_event_loop()

            def query() -> Any:
                df = self.session.table(self.table_name)

                if snapshot_date:
                    df = df.filter(col("SNAPSHOT_DATE") == snapshot_date)
                if carrier_name:
                    df = df.filter(col("CARRIER_NAME") == carrier_name)

                return (
                    df.group_by("DECISION")
                    .agg(count(col("TPA_FEE_WORKSHEET_SNAPSHOT_FACT_ID")).alias("COUNT"))
                    .collect()
                )

            rows = await loop.run_in_executor(None, query)

            return {row["DECISION"]: row["COUNT"] for row in rows}
        except Exception as e:
            logger.error("get_claims_by_status_failed", error=str(e))
            return {}

    async def get_avg_processing_days(
        self,
        snapshot_date: Optional[date] = None,
        carrier_name: Optional[str] = None,
    ) -> float:
        """Calculate average processing days for a specific monthly snapshot."""
        try:
            loop = asyncio.get_event_loop()

            def query() -> Any:
                df = self.session.table(self.table_name)

                if snapshot_date:
                    df = df.filter(col("SNAPSHOT_DATE") == snapshot_date)
                if carrier_name:
                    df = df.filter(col("CARRIER_NAME") == carrier_name)

                # Use the TAT field directly instead of calculating
                df = df.filter(col("RFB_PROCESS_TO_DECISION_TAT").isNotNull())

                # Calculate average TAT
                result = df.select(
                    avg(col("RFB_PROCESS_TO_DECISION_TAT")).alias("AVG_DAYS")
                ).collect()

                return float(result[0]["AVG_DAYS"]) if result and result[0]["AVG_DAYS"] else 0.0

            return await loop.run_in_executor(None, query)
        except Exception as e:
            logger.error("get_avg_processing_days_failed", error=str(e))
            return 0.0

    def _row_to_claim(self, row: Any) -> Claim:
        """Convert Snowpark Row to Claim domain model from CLAIMS_TPA_FEE_WORKSHEET_SNAPSHOT_FACT."""
        return Claim(
            # Core identifiers
            tpa_fee_worksheet_snapshot_fact_id=str(row["TPA_FEE_WORKSHEET_SNAPSHOT_FACT_ID"]),
            policy_dim_id=str(row["POLICY_DIM_ID"]),
            policy_number=row.get("POLICY_NUMBER"),
            
            # Claimant information
            claimant_name=row.get("CLAIMANTNAME"),
            
            # Decision and dates
            decision=row.get("DECISION"),
            latest_eob_start_dt=row.get("LATEST_EOB_START_DT"),
            latest_eob_end_dt=row.get("LATEST_EOB_END_DT"),
            certification_date=row.get("CERTIFICATIONDATE"),
            
            # Rate information
            ongoing_rate_month=row.get("ONGOING_RATE_MONTH"),
            
            # Initial decisions
            initial_decisions_facilities=row.get("INITIAL_DECISIONS_FACILITIES"),
            initial_decisions_home_health=row.get("INITIAL_DECISIONS_HOME_HEALTH"),
            initial_decisions_all_other=row.get("INITIAL_DECISIONS_ALL_OTHER"),
            
            # Ongoing decisions
            ongoing_all_facilities=row.get("ONGOING_ALL_FACILITIES"),
            ongoing_home_health=row.get("ONGOING_HOME_HEALTH"),
            all_other=row.get("ALL_OTHER"),
            
            # Retro decisions
            retro_all_facilities=row.get("RETRO_ALL_FACILITIES"),
            retro_home_health=row.get("RETRO_HOME_HEALTH"),
            retro_all_other=row.get("RETRO_ALL_OTHER"),
            retro_months=row.get("RETRO_MONTHS"),
            
            # RFB information
            rfb_id=row.get("RFB_ID"),
            rfb_entered_dt=row.get("RFB_ENTERED_DT"),
            rfb_claim_form_rcpt_dt=row.get("RFB_CLAIM_FORM_RCPT_DT"),
            initial_approval_dt=row.get("INITIAL_APPROVAL_DT"),
            rfb_process_to_decision_tat=row.get("RFB_PROCESS_TO_DECISION_TAT"),
            rfb_reference=row.get("RFB_REFERENCE"),
            
            # Claim dates
            claim_incurred_dt=row.get("CLAIM_INCURRED_DT"),
            claim_expiration_dt=row.get("CLAIM_EXPIRATION_DT"),
            
            # Episode of Benefit
            episode_of_benefit_id=row.get("EPISODE_OF_BENEFIT_ID"),
            eb_creation_dt=row.get("EB_CREATION_DT"),
            first_eb_decision_dt=row.get("FIRSTEBDECISIONDT"),
            
            # Provider information
            total_eligible_provider_count=row.get("TOTAL_ELIGIBLE_PROVIDER_COUNT"),
            poc_provider_type_desc=row.get("POC_PROVIDER_TYPE_DESC"),
            eob_creation_to_decision_tat=row.get("EOB_CREATION_TO_DECISION_TAT"),
            
            # Geographic information
            life_state=row.get("LIFE_STATE"),
            issue_state=row.get("ISSUE_STATE"),
            policy_residence_state=row.get("POLICY_RESIDENCE_STATE"),
            
            # Additional metrics
            carrier_name=row.get("CARRIER_NAME"),
            claim_type_cd=row.get("CLAIM_TYPE_CD"),
            is_initial_decision_flag=row.get("IS_INITIAL_DECISION_FLAG"),
            
            # Metadata
            snapshot_date=row.get("SNAPSHOT_DATE"),
            load_date=row.get("LOAD_DATE"),
        )

