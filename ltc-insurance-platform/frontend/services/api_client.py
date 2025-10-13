"""Type-safe API client with retry logic and error handling."""

import logging
from typing import Optional, Dict, Any, List
from datetime import date
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class APIClient:
    """Type-safe API client for LTC Insurance backend."""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_prefix = "/api/v1"
        self.timeout = timeout
        
        # Configure session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _build_url(self, endpoint: str) -> str:
        """Build full API URL."""
        return f"{self.base_url}{self.api_prefix}{endpoint}"
    
    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response."""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            if response.status_code == 404:
                return None
            raise Exception(f"API Error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            raise
    
    # Health Check
    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    # Policy Endpoints
    def get_policies(
        self,
        carrier_name: Optional[str] = None,
        snapshot_date: Optional[str] = None,
        policy_status: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get list of policies."""
        params = {
            "limit": limit,
            "offset": offset
        }
        if carrier_name:
            params["carrier_name"] = carrier_name
        if snapshot_date:
            params["snapshot_date"] = snapshot_date
        if policy_status:
            params["policy_status"] = policy_status
        if state:
            params["state"] = state
        
        response = self.session.get(
            self._build_url("/policies/"),
            params=params,
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def get_policy(self, policy_id: int) -> Optional[Dict[str, Any]]:
        """Get policy by ID."""
        response = self.session.get(
            self._build_url(f"/policies/{policy_id}"),
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def get_policy_metrics(
        self,
        carrier_name: Optional[str] = None,
        snapshot_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get policy metrics."""
        params = {}
        if carrier_name:
            params["carrier_name"] = carrier_name
        if snapshot_date:
            params["snapshot_date"] = snapshot_date
        
        response = self.session.get(
            self._build_url("/policies/metrics/summary"),
            params=params,
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    # Claims Endpoints
    def get_claims(
        self,
        carrier_name: Optional[str] = None,
        report_end_dt: Optional[date] = None,
        decision_types: Optional[List[str]] = None,
        ongoing_rate_months: Optional[List[int]] = None,
        categories: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get list of claims."""
        params = {
            "limit": limit,
            "offset": offset
        }
        if carrier_name:
            params["carrier_name"] = carrier_name
        if report_end_dt:
            params["report_end_dt"] = report_end_dt.isoformat()
        if decision_types:
            params["decision_types"] = ",".join(decision_types)
        if ongoing_rate_months:
            params["ongoing_rate_months"] = ",".join(map(str, ongoing_rate_months))
        if categories:
            params["categories"] = ",".join(categories)
        
        response = self.session.get(
            self._build_url("/claims/"),
            params=params,
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def get_claim(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """Get claim by ID."""
        response = self.session.get(
            self._build_url(f"/claims/{claim_id}"),
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def get_claims_summary(
        self,
        carrier_name: Optional[str] = None,
        report_end_dt: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get claims summary."""
        params = {}
        if carrier_name:
            params["carrier_name"] = carrier_name
        if report_end_dt:
            params["report_end_dt"] = report_end_dt.isoformat()
        
        response = self.session.get(
            self._build_url("/claims/summary/statistics"),
            params=params,
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def get_claims_insights(
        self,
        carrier_name: Optional[str] = None,
        report_end_dt: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get detailed claims insights."""
        params = {}
        if carrier_name:
            params["carrier_name"] = carrier_name
        if report_end_dt:
            params["report_end_dt"] = report_end_dt.isoformat()
        
        response = self.session.get(
            self._build_url("/claims/insights/detailed"),
            params=params,
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    # Analytics Endpoints
    def get_policy_insights(
        self,
        carrier_name: Optional[str] = None,
        snapshot_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get policy insights."""
        params = {}
        if carrier_name:
            params["carrier_name"] = carrier_name
        if snapshot_date:
            params["snapshot_date"] = snapshot_date
        
        response = self.session.get(
            self._build_url("/analytics/policy-insights"),
            params=params,
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def get_combined_dashboard(
        self,
        carrier_name: Optional[str] = None,
        snapshot_date: Optional[str] = None,
        report_end_dt: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get combined dashboard data."""
        params = {}
        if carrier_name:
            params["carrier_name"] = carrier_name
        if snapshot_date:
            params["snapshot_date"] = snapshot_date
        if report_end_dt:
            params["report_end_dt"] = report_end_dt.isoformat()
        
        response = self.session.get(
            self._build_url("/analytics/combined-dashboard"),
            params=params,
            timeout=self.timeout
        )
        return self._handle_response(response)

