"""Type-safe HTTP client for backend API."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional, Dict, List

import httpx
import streamlit as st
from pydantic import BaseModel, Field
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class ClaimSchema(BaseModel):
    """Schema for claim data - adapted for new table structure."""

    claim_id: str
    claim_number: Optional[str] = None
    policy_id: str
    status: str = "PENDING"
    claim_type: Optional[str] = None
    submission_date: Optional[datetime] = None
    service_start_date: Optional[date] = None
    service_end_date: Optional[date] = None
    claim_amount: Decimal = Decimal("0")
    approved_amount: Optional[Decimal] = None
    paid_amount: Optional[Decimal] = None
    denial_reason: Optional[str] = None
    approval_date: Optional[datetime] = None
    payment_date: Optional[datetime] = None
    reviewer_id: Optional[str] = None
    facility_name: Optional[str] = None
    diagnosis_codes: List[str] = Field(default_factory=list)
    # New fields from snapshot table
    claimant_name: Optional[str] = None
    processing_days: Optional[int] = None
    rfb_id: Optional[int] = None
    carrier_name: Optional[str] = None


class PolicySchema(BaseModel):
    """Schema for policy data - adapted for new table structure."""

    policy_id: str
    policy_number: Optional[str] = None
    policy_type: Optional[str] = None  # May not be available
    status: Optional[str] = None
    issue_date: Optional[date] = None
    effective_date: Optional[date] = None
    premium_amount: Decimal = Decimal("0")
    benefit_amount: Optional[Decimal] = None
    elimination_period_days: Optional[int] = None
    benefit_period_months: Optional[int] = None
    insured_name: Optional[str] = None
    insured_age: Optional[int] = None
    insured_state: Optional[str] = None
    agent_id: Optional[str] = None
    termination_date: Optional[date] = None
    last_premium_date: Optional[date] = None
    # New fields from snapshot table
    annualized_premium: Optional[Decimal] = None
    insured_city: Optional[str] = None
    insured_zip: Optional[str] = None
    policy_residence_state: Optional[str] = None
    premium_frequency: Optional[str] = None
    benefit_inflation: Optional[str] = None
    total_active_claims: Optional[int] = None
    carrier_name: Optional[str] = None


class ClaimSummary(BaseModel):
    """Schema for claims summary."""

    total_claims: int
    approved_claims: int
    denied_claims: int
    pending_claims: int
    total_claim_amount: Decimal
    total_approved_amount: Decimal
    total_paid_amount: Decimal
    avg_processing_days: float
    approval_rate: float
    avg_claim_amount: Decimal


class PolicyMetrics(BaseModel):
    """Schema for policy metrics."""

    total_policies: int
    active_policies: int
    lapsed_policies: int
    terminated_policies: int
    total_premium: Decimal
    avg_premium: Decimal
    avg_benefit: Decimal
    avg_insured_age: float
    lapse_rate: float
    policy_type_distribution: Dict[str, int]


class AnalyticsResponse(BaseModel):
    """Schema for analytics response."""

    timestamp: datetime
    claim_summary: Optional[ClaimSummary] = None
    policy_metrics: Optional[PolicyMetrics] = None
    trends: List[Dict[str, Any]] = Field(default_factory=list)
    filters_applied: Dict[str, Any] = Field(default_factory=dict)


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""

    status: str
    database: Optional[str] = None
    schema: Optional[str] = None
    warehouse: Optional[str] = None
    timestamp: Optional[str] = None
    active_sessions: int
    pooled_sessions: int
    error: Optional[str] = None


class APIClient:
    """Type-safe HTTP client for LTC Insurance Data Service API."""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 30.0):
        """
        Initialize API client.

        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._sync_client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                follow_redirects=True,
            )
        return self._sync_client

    def close(self) -> None:
        """Close HTTP client."""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.RequestError),
    )
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON request body

        Returns:
            Response data as dictionary

        Raises:
            httpx.HTTPStatusError: If response status is not successful
        """
        try:
            response = self.client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json_data,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json() if e.response.text else {"error": str(e)}
            st.error(f"API Error: {error_detail.get('message', str(e))}")
            raise
        except httpx.RequestError as e:
            st.error(f"Connection Error: {str(e)}")
            raise

    # Health Check

    def health_check(self) -> HealthCheckResponse:
        """Check API health status."""
        data = self._request("GET", "/health")
        return HealthCheckResponse(**data)

    # Analytics Endpoints

    def get_claims_summary(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> ClaimSummary:
        """Get claims summary analytics."""
        params = {}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        data = self._request("GET", "/api/v1/analytics/claims-summary", params=params)
        return ClaimSummary(**data)

    def get_policy_metrics(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> PolicyMetrics:
        """Get policy metrics analytics."""
        params = {}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        data = self._request("GET", "/api/v1/analytics/policy-metrics", params=params)
        return PolicyMetrics(**data)

    def get_comprehensive_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        policy_types: Optional[List[str]] = None,
        states: Optional[List[str]] = None,
    ) -> AnalyticsResponse:
        """Get comprehensive analytics with custom filters."""
        request_data = {}
        if start_date:
            request_data["start_date"] = start_date.isoformat()
        if end_date:
            request_data["end_date"] = end_date.isoformat()
        if policy_types:
            request_data["policy_types"] = policy_types
        if states:
            request_data["states"] = states

        data = self._request("POST", "/api/v1/analytics/custom-query", json_data=request_data)
        return AnalyticsResponse(**data)

    # Claims Endpoints

    def get_claim(self, claim_id: str) -> ClaimSchema:
        """Get claim by ID."""
        data = self._request("GET", f"/api/v1/claims/{claim_id}")
        return ClaimSchema(**data)

    def list_claims(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[str] = None,
        policy_id: Optional[str] = None,
    ) -> List[ClaimSchema]:
        """List claims with filtering."""
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if policy_id:
            params["policy_id"] = policy_id

        data = self._request("GET", "/api/v1/claims/", params=params)
        return [ClaimSchema(**item) for item in data]

    # Policy Endpoints

    def get_policy(self, policy_id: str) -> PolicySchema:
        """Get policy by ID."""
        data = self._request("GET", f"/api/v1/policies/{policy_id}")
        return PolicySchema(**data)

    def list_policies(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[str] = None,
        policy_type: Optional[str] = None,
        state: Optional[str] = None,
    ) -> List[PolicySchema]:
        """List policies with filtering."""
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if policy_type:
            params["policy_type"] = policy_type
        if state:
            params["state"] = state

        data = self._request("GET", "/api/v1/policies/", params=params)
        return [PolicySchema(**item) for item in data]


@st.cache(allow_output_mutation=True)
def get_api_client() -> APIClient:
    """Get cached API client instance."""
    return APIClient()

