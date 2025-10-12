"""Tests for analytics service."""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from app.models.domain import ClaimStatus, PolicyStatus
from app.models.schemas import AnalyticsRequest, ClaimSummary, PolicyMetrics
from app.services.analytics_service import AnalyticsService


@pytest.fixture
def mock_claims_repo():
    """Create mock claims repository."""
    repo = MagicMock()
    repo.get_claims_summary = AsyncMock(return_value={
        "total_claims": 100,
        "total_claim_amount": Decimal("500000.00"),
        "total_approved_amount": Decimal("450000.00"),
        "total_paid_amount": Decimal("400000.00"),
        "avg_claim_amount": Decimal("5000.00"),
    })
    repo.get_claims_by_status = AsyncMock(return_value={
        ClaimStatus.APPROVED.value: 70,
        ClaimStatus.DENIED.value: 10,
        ClaimStatus.SUBMITTED.value: 15,
        ClaimStatus.UNDER_REVIEW.value: 5,
    })
    repo.get_avg_processing_days = AsyncMock(return_value=15.5)
    return repo


@pytest.fixture
def mock_policy_repo():
    """Create mock policy repository."""
    repo = MagicMock()
    repo.get_policy_metrics = AsyncMock(return_value={
        "total_policies": 500,
        "total_premium": Decimal("250000.00"),
        "avg_premium": Decimal("500.00"),
        "avg_benefit": Decimal("150.00"),
        "avg_insured_age": 72.5,
    })
    repo.get_policies_by_status = AsyncMock(return_value={
        PolicyStatus.ACTIVE.value: 450,
        PolicyStatus.LAPSED.value: 30,
        PolicyStatus.TERMINATED.value: 20,
    })
    repo.get_policies_by_type = AsyncMock(return_value={
        "COMPREHENSIVE": 300,
        "FACILITY_ONLY": 100,
        "HOME_CARE": 100,
    })
    repo.calculate_lapse_rate = AsyncMock(return_value=0.06)
    return repo


@pytest.fixture
def analytics_service(mock_claims_repo, mock_policy_repo):
    """Create analytics service with mocked repositories."""
    return AnalyticsService(mock_claims_repo, mock_policy_repo)


@pytest.mark.asyncio
async def test_get_claims_summary(analytics_service):
    """Test claims summary generation."""
    summary = await analytics_service.get_claims_summary(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31)
    )
    
    assert isinstance(summary, ClaimSummary)
    assert summary.total_claims == 100
    assert summary.approved_claims == 70
    assert summary.denied_claims == 10
    assert summary.pending_claims == 20
    assert summary.approval_rate == 0.7


@pytest.mark.asyncio
async def test_get_policy_metrics(analytics_service):
    """Test policy metrics generation."""
    metrics = await analytics_service.get_policy_metrics(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31)
    )
    
    assert isinstance(metrics, PolicyMetrics)
    assert metrics.total_policies == 500
    assert metrics.active_policies == 450
    assert metrics.lapsed_policies == 30
    assert metrics.lapse_rate == 0.06


@pytest.mark.asyncio
async def test_comprehensive_analytics(analytics_service):
    """Test comprehensive analytics generation."""
    request = AnalyticsRequest(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31)
    )
    
    response = await analytics_service.get_comprehensive_analytics(request)
    
    assert response.claim_summary is not None
    assert response.policy_metrics is not None
    assert isinstance(response.filters_applied, dict)

