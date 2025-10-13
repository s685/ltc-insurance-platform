"""Domain models matching Snowflake table structures."""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class PolicyMonthlySnapshot(BaseModel):
    """Domain model for POLICY_MONTHLY_SNAPSHOT_FACT table."""
    
    policy_monthly_snapshot_id: Optional[str] = None
    policy_dim_id: Optional[str] = None
    policy_id: Optional[int] = None
    insured_life_dim_id: Optional[str] = None
    insured_life_id: Optional[int] = None
    insured_city: Optional[str] = None
    insured_state: Optional[str] = None
    insured_zip: Optional[str] = None
    policy_residence_state: Optional[str] = None
    paf_relationship_dim_id: Optional[str] = None
    member_life_dim_id: Optional[str] = None
    member_life_id: Optional[int] = None
    grp_dim_id: Optional[str] = None
    annualized_premium: Optional[float] = None
    lifetime_collected_premium: Optional[float] = None
    lifetime_waiver_premium: Optional[float] = None
    premium_frequency: Optional[str] = None
    offset_premium: Optional[float] = None
    policy_status_dim_id: Optional[str] = None
    current_coverage_id: Optional[int] = None
    current_coverage_dim_id: Optional[str] = None
    original_effective_dt_id: Optional[str] = None
    original_effective_dt: Optional[datetime] = None
    coverage_effective_dt_id: Optional[str] = None
    coverage_effective_dt: Optional[datetime] = None
    coverage_status_dt_id: Optional[str] = None
    coverage_status_dt: Optional[datetime] = None
    coverage_expiration_dt_id: Optional[str] = None
    coverage_expiration_dt: Optional[datetime] = None
    policy_expiration_dt_id: Optional[str] = None
    policy_expiration_dt: Optional[datetime] = None
    appn_rcv_dt_id: Optional[str] = None
    appn_rcv_dt: Optional[datetime] = None
    appn_sig_dt_id: Optional[str] = None
    appn_sig_dt: Optional[datetime] = None
    appn_sig_state: Optional[str] = None
    current_waiver_effective_date_id: Optional[str] = None
    current_waiver_effective_date: Optional[datetime] = None
    current_waiver_expiration_date_id: Optional[str] = None
    current_waiver_expiration_date: Optional[datetime] = None
    in_waiver_flg: Optional[str] = None
    in_waiver_desc: Optional[str] = None
    current_nonforfeiture_effective_date_id: Optional[str] = None
    current_nonforfeiture_effective_date: Optional[datetime] = None
    current_nonforfeiture_expiration_date_id: Optional[str] = None
    current_nonforfeiture_expiration_date: Optional[datetime] = None
    in_nonforfeiture_flg: Optional[str] = None
    in_nonforfeiture_desc: Optional[str] = None
    current_survivorship_effective_date_id: Optional[str] = None
    current_survivorship_effective_date: Optional[datetime] = None
    current_survivorship_expiration_date_id: Optional[str] = None
    current_survivorship_expiration_date: Optional[datetime] = None
    survivorship_flg: Optional[str] = None
    survivorship_desc: Optional[str] = None
    paid_to_date_id: Optional[str] = None
    paid_to_date: Optional[datetime] = None
    latest_claim_dim_id: Optional[str] = None
    latest_claim_id: Optional[int] = None
    rated_age: Optional[int] = None
    rated_date: Optional[datetime] = None
    tax_qualification_dim_id: Optional[str] = None
    benefit_inflation: Optional[str] = None
    benefit_increase: Optional[str] = None
    first_eob_decision_dt: Optional[datetime] = None
    first_eob_decision_dt_id: Optional[str] = None
    latest_eob_decision_dt: Optional[datetime] = None
    latest_eob_decision_dt_id: Optional[str] = None
    latest_claim_incurred_dt: Optional[datetime] = None
    latest_claim_incurred_dt_id: Optional[str] = None
    latest_claim_expiration_dt: Optional[datetime] = None
    latest_claim_expiration_dt_id: Optional[str] = None
    claim_status_cd: Optional[str] = None
    claimant_sex: Optional[str] = None
    claim_paid_dt: Optional[datetime] = None
    claim_paid_dt_id: Optional[str] = None
    total_request_for_reimbursment_benefit: Optional[float] = None
    total_request_for_reimbursment_admin: Optional[float] = None
    total_request_for_reimbursment_pending: Optional[float] = None
    total_request_for_reimbursment_requested_amount: Optional[float] = None
    total_request_for_reimbursment_unpaid_amount: Optional[float] = None
    disabling_event_icd_dim_id: Optional[str] = None
    primary_diagnosis_icd_dim_id: Optional[str] = None
    total_active_claims: Optional[int] = None
    total_rfbs: Optional[int] = None
    total_approved_rfbs: Optional[int] = None
    total_denials: Optional[int] = None
    carrier_name: Optional[str] = None
    environment: Optional[str] = None
    policy_snapshot_date: Optional[str] = None
    
    class Config:
        from_attributes = True


class ClaimsTPAFeeWorksheet(BaseModel):
    """Domain model for CLAIMS_TPA_FEE_WORKSHEET_SNAPSHOT_FACT table."""
    
    tpa_fee_worksheet_snapshot_fact_id: Optional[str] = None
    policy_dim_id: Optional[str] = None
    claimantname: Optional[str] = None
    policy_number: Optional[str] = None
    decision: Optional[str] = None
    latest_eob_start_dt: Optional[date] = None
    latest_eob_end_dt: Optional[date] = None
    certificationdate: Optional[date] = None
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
    claim_incurred_dt: Optional[date] = None
    claim_expiration_dt: Optional[date] = None
    episode_of_benefit_id: Optional[int] = None
    eb_creation_dt: Optional[date] = None
    firstebdecisiondt: Optional[date] = None
    eb_reassessment_dt: Optional[date] = None
    total_eligible_provider_count: Optional[int] = None
    pending_provider_count: Optional[int] = None
    ineligible_provider_count: Optional[int] = None
    informal_provider_count: Optional[int] = None
    poc_provider_id: Optional[int] = None
    ppsd_start_dt: Optional[date] = None
    ppsd_end_dt: Optional[date] = None
    poc_provider_type_desc: Optional[str] = None
    eob_creation_to_decision_tat: Optional[int] = None
    life_state: Optional[str] = None
    issue_state: Optional[str] = None
    policy_residence_state: Optional[str] = None
    snapshot_date: Optional[date] = None
    load_date: Optional[datetime] = None
    carrier_name: Optional[str] = None
    claim_type_cd: Optional[int] = None
    decision_excluding_pre_authorization_facility_only: Optional[int] = None
    decision_excluding_pre_authorization_alf: Optional[int] = None
    decision_excluding_pre_authorization_all_other_policies: Optional[int] = None
    closed_pre_authorization_no_decision: Optional[int] = None
    closed_pre_authorization_approval: Optional[int] = None
    closed_pre_authorization_denial: Optional[int] = None
    co_med_dir_review_initial: Optional[int] = None
    co_med_dir_review_appeal: Optional[int] = None
    restoration_of_benefits: Optional[int] = None
    is_initial_decision_flag: Optional[int] = None
    
    class Config:
        from_attributes = True

