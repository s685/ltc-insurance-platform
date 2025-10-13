"""API request and response schemas."""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Request Models
class ClaimsFilterRequest(BaseModel):
    """Filter parameters for claims queries."""
    
    carrier_name: Optional[str] = Field(None, description="Carrier name filter")
    report_end_dt: Optional[date] = Field(None, description="Report end date for snapshot")
    decision_types: Optional[List[str]] = Field(
        None,
        description="Filter by decision types (In Assessment, Approved, Denied, etc.)"
    )
    ongoing_rate_months: Optional[List[int]] = Field(
        None,
        description="Filter by ongoing rate month (0=Initial, 1=Ongoing, 2=Restoration)"
    )
    categories: Optional[List[str]] = Field(
        None,
        description="Filter by category (Facility, Home Health, Other)"
    )
    limit: int = Field(100, ge=1, le=1000, description="Maximum records to return")
    offset: int = Field(0, ge=0, description="Number of records to skip")


class PolicyFilterRequest(BaseModel):
    """Filter parameters for policy queries."""
    
    carrier_name: Optional[str] = Field(None, description="Carrier name filter")
    snapshot_date: Optional[str] = Field(None, description="Snapshot date filter")
    policy_status: Optional[str] = Field(None, description="Policy status filter")
    state: Optional[str] = Field(None, description="State filter")
    limit: int = Field(100, ge=1, le=1000, description="Maximum records to return")
    offset: int = Field(0, ge=0, description="Number of records to skip")


# Response Models
class PolicyResponse(BaseModel):
    """Policy data response."""
    
    policy_id: Optional[int]
    policy_number: Optional[str] = None
    carrier_name: Optional[str]
    insured_state: Optional[str]
    policy_residence_state: Optional[str]
    annualized_premium: Optional[float]
    lifetime_collected_premium: Optional[float]
    premium_frequency: Optional[str]
    original_effective_dt: Optional[datetime]
    policy_expiration_dt: Optional[datetime]
    in_waiver_flg: Optional[str]
    in_nonforfeiture_flg: Optional[str]
    rated_age: Optional[int]
    total_active_claims: Optional[int]
    total_rfbs: Optional[int]
    total_approved_rfbs: Optional[int]
    total_denials: Optional[int]
    policy_snapshot_date: Optional[str]


class ClaimResponse(BaseModel):
    """Claim data response."""
    
    tpa_fee_worksheet_snapshot_fact_id: Optional[str]
    policy_number: Optional[str]
    claimantname: Optional[str]
    decision: Optional[str]
    certificationdate: Optional[date]
    ongoing_rate_month: Optional[int]
    is_initial_decision_flag: Optional[int]
    carrier_name: Optional[str]
    snapshot_date: Optional[date]
    rfb_process_to_decision_tat: Optional[int]
    eob_creation_to_decision_tat: Optional[int]
    
    # Facility metrics
    initial_decisions_facilities: Optional[int]
    ongoing_all_facilities: Optional[int]
    retro_all_facilities: Optional[int]
    
    # Home Health metrics
    initial_decisions_home_health: Optional[int]
    ongoing_home_health: Optional[int]
    retro_home_health: Optional[int]
    
    # Other metrics
    initial_decisions_all_other: Optional[int]
    all_other: Optional[int]
    retro_all_other: Optional[int]
    
    retro_months: Optional[int]
    poc_provider_type_desc: Optional[str]


class PolicyMetrics(BaseModel):
    """Policy analytics metrics."""
    
    total_policies: int
    active_policies: int
    in_forfeiture_policies: int
    in_waiver_policies: int
    avg_premium: float
    total_premium_revenue: float
    avg_insured_age: float
    lapse_rate: float
    policies_with_claims: int
    avg_claims_per_policy: float


class ClaimsSummary(BaseModel):
    """Claims summary statistics."""
    
    total_claims: int
    approved_claims: int
    denied_claims: int
    in_assessment_claims: int
    approval_rate: float
    avg_processing_time_days: float
    total_retro_claims: int
    retro_percentage: float
    
    # By category
    facility_claims: int
    home_health_claims: int
    other_claims: int
    
    # By ongoing rate month
    initial_decisions: int
    ongoing_decisions: int
    restoration_decisions: int


class ClaimsInsights(BaseModel):
    """Detailed claims insights."""
    
    summary: ClaimsSummary
    decision_breakdown: Dict[str, int]
    category_breakdown: Dict[str, int]
    avg_tat_by_category: Dict[str, float]
    retro_analysis: Dict[str, Any]


class PolicyInsights(BaseModel):
    """Detailed policy insights."""
    
    metrics: PolicyMetrics
    state_distribution: Dict[str, int]
    premium_by_state: Dict[str, float]
    waiver_breakdown: Dict[str, int]
    status_distribution: Dict[str, int]


class CombinedDashboard(BaseModel):
    """Combined dashboard data."""
    
    policy_metrics: PolicyMetrics
    claims_summary: ClaimsSummary
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    timestamp: datetime
    database_connected: bool
    cache_enabled: bool
    version: str


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str
    message: str
    details: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)

