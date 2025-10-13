"""Pydantic schemas for API request/response validation."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal, Optional, List, Dict

from pydantic import BaseModel, Field, field_validator

from .domain import ClaimStatus, PolicyStatus, PolicyType


class PolicySchema(BaseModel):
    """Schema for policy data - adapted for POLICY_MONTHLY_SNAPSHOT_FACT."""

    # Core identifiers
    policy_id: str = Field(..., description="Unique policy identifier")
    policy_number: Optional[str] = Field(None, description="Policy number")
    
    # Status and type (simplified for frontend)
    status: Optional[str] = Field(None, description="Current policy status")
    
    # Dates
    issue_date: Optional[date] = Field(None, description="Policy issue date")
    effective_date: Optional[date] = Field(None, description="Policy effective date")
    termination_date: Optional[date] = Field(None, description="Policy termination date")
    last_premium_date: Optional[date] = Field(None, description="Last premium payment date")
    
    # Premium and benefits
    premium_amount: Decimal = Field(default=Decimal("0"), description="Monthly premium amount", ge=0)
    benefit_amount: Optional[Decimal] = Field(None, description="Benefit amount", ge=0)
    annualized_premium: Optional[Decimal] = Field(None, description="Annual premium")
    
    # Insured information
    insured_name: Optional[str] = Field(None, description="Name of insured person")
    insured_age: Optional[int] = Field(None, description="Age of insured person", ge=0, le=120)
    insured_state: Optional[str] = Field(None, description="State of insured person")
    insured_city: Optional[str] = Field(None, description="City of insured person")
    insured_zip: Optional[str] = Field(None, description="ZIP code")
    
    # Additional fields from snapshot
    policy_residence_state: Optional[str] = Field(None, description="Policy residence state")
    premium_frequency: Optional[str] = Field(None, description="Premium frequency")
    benefit_inflation: Optional[str] = Field(None, description="Benefit inflation type")
    
    # Claim information
    total_active_claims: Optional[int] = Field(None, description="Number of active claims")
    claim_status_cd: Optional[str] = Field(None, description="Current claim status code")
    
    # Metadata
    carrier_name: Optional[str] = Field(None, description="Insurance carrier name")
    environment: Optional[str] = Field(None, description="Environment (PROD/TEST)")

    model_config = {"from_attributes": True, "use_enum_values": False}

    @field_validator("insured_state")
    @classmethod
    def validate_state(cls, v: Optional[str]) -> Optional[str]:
        """Validate state code format."""
        return v.upper() if v else None


class ClaimSchema(BaseModel):
    """Schema for claim data - adapted for CLAIMS_TPA_FEE_WORKSHEET_SNAPSHOT_FACT."""

    # Core identifiers
    claim_id: str = Field(..., description="Unique claim identifier")
    claim_number: Optional[str] = Field(None, description="Claim number (policy number)")
    policy_id: str = Field(..., description="Associated policy dimension ID")
    
    # Claimant information
    claimant_name: Optional[str] = Field(None, description="Claimant name")
    
    # Status and decision
    status: str = Field(default="PENDING", description="Current claim status/decision")
    claim_type: Optional[str] = Field(None, description="Type of claim")
    
    # Dates
    submission_date: Optional[datetime] = Field(None, description="Claim submission date (RFB entered)")
    service_start_date: Optional[date] = Field(None, description="Service start date (EOB start)")
    service_end_date: Optional[date] = Field(None, description="Service end date (EOB end)")
    approval_date: Optional[datetime] = Field(None, description="Approval/certification date")
    certification_date: Optional[date] = Field(None, description="Certification date")
    
    # Financial information (adapted from decision counts)
    claim_amount: Decimal = Field(default=Decimal("0"), description="Claim amount", ge=0)
    approved_amount: Optional[Decimal] = Field(None, description="Approved amount", ge=0)
    paid_amount: Optional[Decimal] = Field(None, description="Paid amount", ge=0)
    
    # Processing information
    processing_days: Optional[int] = Field(None, description="Processing TAT in days")
    denial_reason: Optional[str] = Field(None, description="Reason for denial")
    
    # RFB information
    rfb_id: Optional[int] = Field(None, description="Request for Benefit ID")
    rfb_reference: Optional[str] = Field(None, description="RFB reference number")
    
    # Decision metrics
    initial_decisions_facilities: Optional[int] = Field(None, description="Initial decisions for facilities")
    initial_decisions_home_health: Optional[int] = Field(None, description="Initial decisions for home health")
    ongoing_rate_month: Optional[int] = Field(None, description="Ongoing rate per month")
    
    # Provider information
    facility_name: Optional[str] = Field(None, description="Facility/provider type")
    provider_count: Optional[int] = Field(None, description="Total provider count")
    
    # Geographic information
    life_state: Optional[str] = Field(None, description="Life state")
    issue_state: Optional[str] = Field(None, description="Issue state")
    
    # Metadata
    carrier_name: Optional[str] = Field(None, description="Insurance carrier name")
    snapshot_date: Optional[date] = Field(None, description="Snapshot date")

    model_config = {"from_attributes": True, "use_enum_values": False}


class AnalyticsRequest(BaseModel):
    """Schema for analytics query requests."""

    start_date: Optional[date] = Field(None, description="Start date for analysis")
    end_date: Optional[date] = Field(None, description="End date for analysis")
    policy_types: Optional[List[PolicyType]] = Field(
        None, description="Filter by policy types"
    )
    states: Optional[List[str]] = Field(None, description="Filter by states")
    claim_statuses: Optional[List[ClaimStatus]] = Field(
        None, description="Filter by claim statuses"
    )
    min_age: Optional[int] = Field(None, description="Minimum insured age", ge=0, le=120)
    max_age: Optional[int] = Field(None, description="Maximum insured age", ge=0, le=120)
    group_by: Optional[Literal["day", "week", "month", "quarter", "year"]] = Field(
        None, description="Time grouping for trends"
    )

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: Optional[date], info: Any) -> Optional[date]:
        """Validate that end_date is after start_date."""
        if v and info.data.get("start_date") and v < info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v

    @field_validator("max_age")
    @classmethod
    def validate_age_range(cls, v: Optional[int], info: Any) -> Optional[int]:
        """Validate that max_age is greater than min_age."""
        if v and info.data.get("min_age") and v < info.data["min_age"]:
            raise ValueError("max_age must be greater than min_age")
        return v


class ClaimSummary(BaseModel):
    """Schema for claims summary analytics."""

    total_claims: int = Field(..., description="Total number of claims")
    approved_claims: int = Field(..., description="Number of approved claims")
    denied_claims: int = Field(..., description="Number of denied claims")
    pending_claims: int = Field(..., description="Number of pending claims")
    total_claim_amount: Decimal = Field(..., description="Total claimed amount")
    total_approved_amount: Decimal = Field(..., description="Total approved amount")
    total_paid_amount: Decimal = Field(..., description="Total paid amount")
    avg_processing_days: float = Field(..., description="Average processing days")
    approval_rate: float = Field(..., description="Claim approval rate", ge=0, le=1)
    avg_claim_amount: Decimal = Field(..., description="Average claim amount")


class PolicyMetrics(BaseModel):
    """Schema for policy metrics analytics."""

    total_policies: int = Field(..., description="Total number of policies")
    active_policies: int = Field(..., description="Number of active policies")
    lapsed_policies: int = Field(..., description="Number of lapsed policies")
    terminated_policies: int = Field(..., description="Number of terminated policies")
    total_premium: Decimal = Field(..., description="Total premium collected")
    avg_premium: Decimal = Field(..., description="Average premium amount")
    avg_benefit: Decimal = Field(..., description="Average benefit amount")
    avg_insured_age: float = Field(..., description="Average insured age")
    lapse_rate: float = Field(..., description="Policy lapse rate", ge=0, le=1)
    policy_type_distribution: Dict[str, int] = Field(
        ..., description="Distribution by policy type"
    )


class TrendData(BaseModel):
    """Schema for trend analysis data."""

    period: str = Field(..., description="Time period label")
    value: float = Field(..., description="Metric value for period")
    count: Optional[int] = Field(None, description="Count for period")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class AnalyticsResponse(BaseModel):
    """Schema for analytics response."""

    timestamp: datetime = Field(
        default_factory=datetime.now, description="Response timestamp"
    )
    claim_summary: Optional[ClaimSummary] = Field(None, description="Claims summary")
    policy_metrics: Optional[PolicyMetrics] = Field(None, description="Policy metrics")
    trends: List[TrendData] = Field(
        default_factory=list, description="Trend data points"
    )
    filters_applied: Dict[str, Any] = Field(
        default_factory=dict, description="Applied filters"
    )


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""

    status: Literal["healthy", "unhealthy"] = Field(..., description="Service status")
    database: Optional[str] = Field(None, description="Database name")
    schema_name: Optional[str] = Field(None, description="Schema name", alias="schema")
    warehouse: Optional[str] = Field(None, description="Warehouse name")
    timestamp: Optional[str] = Field(None, description="Database timestamp")
    active_sessions: int = Field(..., description="Number of active sessions")
    pooled_sessions: int = Field(..., description="Number of pooled sessions")
    error: Optional[str] = Field(None, description="Error message if unhealthy")
    
    model_config = {"populate_by_name": True}

