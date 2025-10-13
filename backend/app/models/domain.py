"""Domain models for LTC insurance entities."""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional, List, Dict


class PolicyStatus(str, Enum):
    """Policy status enumeration."""

    ACTIVE = "ACTIVE"
    LAPSED = "LAPSED"
    TERMINATED = "TERMINATED"
    PENDING = "PENDING"
    SUSPENDED = "SUSPENDED"


class PolicyType(str, Enum):
    """Policy type enumeration."""

    COMPREHENSIVE = "COMPREHENSIVE"
    FACILITY_ONLY = "FACILITY_ONLY"
    HOME_CARE = "HOME_CARE"
    HYBRID = "HYBRID"


class ClaimStatus(str, Enum):
    """Claim status enumeration."""

    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    PAID = "PAID"
    APPEALED = "APPEALED"


@dataclass(frozen=True)
class Policy:
    """LTC insurance policy from POLICY_MONTHLY_SNAPSHOT_FACT."""
    
    # Core identifiers
    policy_monthly_snapshot_id: str
    policy_dim_id: str
    policy_id: int
    policy_number: Optional[str] = None
    
    # Insured information (8 fields)
    insured_life_dim_id: Optional[str] = None
    insured_life_id: Optional[int] = None
    insured_city: Optional[str] = None
    insured_state: Optional[str] = None
    insured_zip: Optional[str] = None
    policy_residence_state: Optional[str] = None
    claimant_sex: Optional[str] = None
    rated_age: Optional[int] = None
    
    # Premium information (5 fields)
    annualized_premium: Optional[Decimal] = None
    lifetime_collected_premium: Optional[Decimal] = None
    lifetime_waiver_premium: Optional[Decimal] = None
    premium_frequency: Optional[str] = None
    offset_premium: Optional[Decimal] = None
    
    # Status and dates (10 fields)
    policy_status_dim_id: Optional[str] = None
    original_effective_dt: Optional[datetime] = None
    coverage_effective_dt: Optional[datetime] = None
    coverage_status_dt: Optional[datetime] = None
    coverage_expiration_dt: Optional[datetime] = None
    policy_expiration_dt: Optional[datetime] = None
    appn_rcv_dt: Optional[datetime] = None
    appn_sig_dt: Optional[datetime] = None
    appn_sig_state: Optional[str] = None
    paid_to_date: Optional[datetime] = None
    
    # Coverage information (5 fields)
    current_coverage_id: Optional[int] = None
    current_coverage_dim_id: Optional[str] = None
    tax_qualification_dim_id: Optional[str] = None
    benefit_inflation: Optional[str] = None
    benefit_increase: Optional[str] = None
    
    # Waiver information (3 fields)
    in_waiver_flg: Optional[str] = None
    current_waiver_effective_date: Optional[datetime] = None
    current_waiver_expiration_date: Optional[datetime] = None
    
    # Claim information (10 fields)
    latest_claim_dim_id: Optional[str] = None
    latest_claim_id: Optional[int] = None
    claim_status_cd: Optional[str] = None
    first_eob_decision_dt: Optional[datetime] = None
    latest_eob_decision_dt: Optional[datetime] = None
    latest_claim_incurred_dt: Optional[datetime] = None
    latest_claim_expiration_dt: Optional[datetime] = None
    total_active_claims: Optional[int] = None
    total_rfbs: Optional[int] = None
    total_approved_rfbs: Optional[int] = None
    total_denials: Optional[int] = None
    
    # Financial summary (3 fields)
    total_request_for_reimbursment_benefit: Optional[Decimal] = None
    total_request_for_reimbursment_admin: Optional[Decimal] = None
    total_request_for_reimbursment_pending: Optional[Decimal] = None
    
    # Metadata (3 fields)
    carrier_name: Optional[str] = None
    environment: Optional[str] = None
    policy_snapshot_date: Optional[str] = None
    
    # Helper methods
    def is_active(self) -> bool:
        return self.claim_status_cd not in ["EXPIRED", "TERMINATED", "CANCELLED"]
    
    def monthly_premium(self) -> Decimal:
        if not self.annualized_premium:
            return Decimal(0)
        return self.annualized_premium / 12
    
    def annual_premium(self) -> Decimal:
        return self.annualized_premium or Decimal(0)
    
    def has_active_claims(self) -> bool:
        return (self.total_active_claims or 0) > 0


@dataclass(frozen=True)
class Claim:
    """LTC insurance claim from CLAIMS_TPA_FEE_WORKSHEET_SNAPSHOT_FACT."""
    
    # Core identifiers
    tpa_fee_worksheet_snapshot_fact_id: str
    policy_dim_id: str
    policy_number: Optional[str] = None
    claimant_name: Optional[str] = None
    
    # Decision and dates
    decision: Optional[str] = None
    latest_eob_start_dt: Optional[date] = None
    latest_eob_end_dt: Optional[date] = None
    certification_date: Optional[date] = None
    
    # Rate and decision metrics (13 fields)
    ongoing_rate_month: Optional[int] = None
    initial_decisions_facilities: Optional[int] = None
    initial_decisions_home_health: Optional[int] = None
    initial_decisions_all_other: Optional[int] = None
    ongoing_all_facilities: Optional[int] = None
    ongoing_home_health: Optional[int] = None
    all_other: Optional[int] = None
    retro_all_facilities: Optional[int] = None
    retro_home_health: Optional[int] = None
    retro_all_other: Optional[int] = None
    retro_months: Optional[int] = None
    
    # RFB information (11 fields)
    rfb_id: Optional[int] = None
    rfb_entered_dt: Optional[date] = None
    rfb_claim_form_rcpt_dt: Optional[date] = None
    initial_approval_dt: Optional[date] = None
    rfb_initial_inquiry_dt: Optional[date] = None
    rfb_claim_packet_sent_dt: Optional[date] = None
    rfb_statistical_start_dt: Optional[date] = None
    rfb_statistical_end_dt: Optional[date] = None
    rfb_process_to_decision_tat: Optional[int] = None
    rfb_reference: Optional[str] = None
    initial_to_packet_tat: Optional[int] = None
    
    # Claim dates
    claim_incurred_dt: Optional[date] = None
    claim_expiration_dt: Optional[date] = None
    
    # Episode of Benefit (4 fields)
    episode_of_benefit_id: Optional[int] = None
    eb_creation_dt: Optional[date] = None
    first_eb_decision_dt: Optional[date] = None
    eb_reassessment_dt: Optional[date] = None
    
    # Provider information (9 fields)
    total_eligible_provider_count: Optional[int] = None
    pending_provider_count: Optional[int] = None
    ineligible_provider_count: Optional[int] = None
    informal_provider_count: Optional[int] = None
    poc_provider_id: Optional[int] = None
    ppsd_start_dt: Optional[date] = None
    ppsd_end_dt: Optional[date] = None
    poc_provider_type_desc: Optional[str] = None
    eob_creation_to_decision_tat: Optional[int] = None
    
    # Geographic information
    life_state: Optional[str] = None
    issue_state: Optional[str] = None
    policy_residence_state: Optional[str] = None
    
    # Additional metrics (12 fields)
    carrier_name: Optional[str] = None
    claim_type_cd: Optional[int] = None
    decision_excluding_pre_auth_facility_only: Optional[int] = None
    decision_excluding_pre_auth_alf: Optional[int] = None
    decision_excluding_pre_auth_all_other: Optional[int] = None
    closed_pre_auth_no_decision: Optional[int] = None
    closed_pre_auth_approval: Optional[int] = None
    closed_pre_auth_denial: Optional[int] = None
    co_med_dir_review_initial: Optional[int] = None
    co_med_dir_review_appeal: Optional[int] = None
    restoration_of_benefits: Optional[int] = None
    is_initial_decision_flag: Optional[int] = None
    
    # Metadata
    snapshot_date: Optional[date] = None
    load_date: Optional[datetime] = None
    
    # Helper methods
    def is_approved(self) -> bool:
        return self.decision and "APPROV" in self.decision.upper()
    
    def is_denied(self) -> bool:
        return self.decision and "DENI" in self.decision.upper()
    
    def is_pending(self) -> bool:
        return self.decision and "PEND" in self.decision.upper()
    
    def processing_days(self) -> int:
        return self.rfb_process_to_decision_tat or 0
    
    def service_duration_days(self) -> int:
        if not self.latest_eob_start_dt or not self.latest_eob_end_dt:
            return 0
        return (self.latest_eob_end_dt - self.latest_eob_start_dt).days
    
    def total_decisions(self) -> int:
        total = 0
        total += self.initial_decisions_facilities or 0
        total += self.initial_decisions_home_health or 0
        total += self.initial_decisions_all_other or 0
        total += self.ongoing_all_facilities or 0
        total += self.ongoing_home_health or 0
        total += self.all_other or 0
        return total
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.tpa_fee_worksheet_snapshot_fact_id,
            "policy_number": self.policy_number,
            "claimant_name": self.claimant_name,
            "decision": self.decision,
            "certification_date": self.certification_date.isoformat() if self.certification_date else None,
            "rfb_process_to_decision_tat": self.rfb_process_to_decision_tat,
            "total_decisions": self.total_decisions(),
            "is_approved": self.is_approved(),
            "is_denied": self.is_denied(),
        }

