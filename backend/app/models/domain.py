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
    """Domain model for LTC insurance policy."""

    policy_id: str
    policy_number: str
    policy_type: PolicyType
    status: PolicyStatus
    issue_date: date
    effective_date: date
    premium_amount: Decimal
    benefit_amount: Decimal
    elimination_period_days: int
    benefit_period_months: int
    insured_name: str
    insured_age: int
    insured_state: str
    agent_id: Optional[str] = None
    termination_date: Optional[date] = None
    last_premium_date: Optional[date] = None

    def is_active(self) -> bool:
        """Check if policy is currently active."""
        return self.status == PolicyStatus.ACTIVE

    def days_since_issue(self, as_of_date: Optional[date] = None) -> int:
        """Calculate days since policy issue."""
        target_date = as_of_date or date.today()
        return (target_date - self.issue_date).days

    def monthly_premium(self) -> Decimal:
        """Get monthly premium amount."""
        return self.premium_amount

    def annual_premium(self) -> Decimal:
        """Calculate annual premium."""
        return self.premium_amount * 12

    def coverage_ratio(self) -> float:
        """Calculate coverage ratio (benefit/premium)."""
        if self.premium_amount == 0:
            return 0.0
        return float(self.benefit_amount / self.premium_amount)


@dataclass(frozen=True)
class Claim:
    """Domain model for LTC insurance claim."""

    claim_id: str
    claim_number: str
    policy_id: str
    status: ClaimStatus
    claim_type: str
    submission_date: datetime
    service_start_date: date
    service_end_date: Optional[date]
    claim_amount: Decimal
    approved_amount: Optional[Decimal]
    paid_amount: Optional[Decimal]
    denial_reason: Optional[str] = None
    approval_date: Optional[datetime] = None
    payment_date: Optional[datetime] = None
    reviewer_id: Optional[str] = None
    facility_name: Optional[str] = None
    diagnosis_codes: List[str] = field(default_factory=list)

    def is_approved(self) -> bool:
        """Check if claim is approved."""
        return self.status == ClaimStatus.APPROVED

    def is_paid(self) -> bool:
        """Check if claim is paid."""
        return self.status == ClaimStatus.PAID

    def processing_days(self, as_of_date: Optional[datetime] = None) -> int:
        """Calculate days in processing."""
        target_date = as_of_date or datetime.now()
        if self.approval_date:
            return (self.approval_date - self.submission_date).days
        return (target_date - self.submission_date).days

    def approval_rate(self) -> float:
        """Calculate approval rate (approved/requested)."""
        if not self.approved_amount or self.claim_amount == 0:
            return 0.0
        return float(self.approved_amount / self.claim_amount)

    def service_duration_days(self) -> int:
        """Calculate service duration in days."""
        end_date = self.service_end_date or date.today()
        return (end_date - self.service_start_date).days

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "claim_id": self.claim_id,
            "claim_number": self.claim_number,
            "policy_id": self.policy_id,
            "status": self.status.value,
            "claim_type": self.claim_type,
            "submission_date": self.submission_date.isoformat(),
            "service_start_date": self.service_start_date.isoformat(),
            "service_end_date": (
                self.service_end_date.isoformat() if self.service_end_date else None
            ),
            "claim_amount": float(self.claim_amount),
            "approved_amount": (
                float(self.approved_amount) if self.approved_amount else None
            ),
            "paid_amount": float(self.paid_amount) if self.paid_amount else None,
            "denial_reason": self.denial_reason,
            "processing_days": self.processing_days(),
        }

