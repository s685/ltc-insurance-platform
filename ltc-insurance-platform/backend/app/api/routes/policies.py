"""Policy API endpoints."""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from snowflake.snowpark import Session

from app.dependencies import get_db_session
from app.repositories.policy_repo import PolicyRepository
from app.models.schemas import PolicyResponse, PolicyFilterRequest, ErrorResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/policies", tags=["Policies"])


@router.get("/{policy_id}", response_model=Dict[str, Any])
async def get_policy(
    policy_id: int,
    session: Session = Depends(get_db_session)
):
    """Get policy by ID."""
    try:
        repo = PolicyRepository(session)
        policy = repo.get_by_id(policy_id)
        
        if not policy:
            raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
        
        return policy.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching policy {policy_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[Dict[str, Any]])
async def list_policies(
    carrier_name: str = Query(None, description="Filter by carrier name"),
    snapshot_date: str = Query(None, description="Filter by snapshot date"),
    policy_status: str = Query(None, description="Filter by policy status"),
    state: str = Query(None, description="Filter by state"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_db_session)
):
    """List policies with optional filters."""
    try:
        repo = PolicyRepository(session)
        policies = repo.list(
            limit=limit,
            offset=offset,
            carrier_name=carrier_name,
            snapshot_date=snapshot_date,
            policy_status=policy_status,
            state=state
        )
        return policies
    except Exception as e:
        logger.error(f"Error listing policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/count/total", response_model=Dict[str, int])
async def count_policies(
    carrier_name: str = Query(None),
    snapshot_date: str = Query(None),
    policy_status: str = Query(None),
    state: str = Query(None),
    session: Session = Depends(get_db_session)
):
    """Count policies matching filters."""
    try:
        repo = PolicyRepository(session)
        count = repo.count(
            carrier_name=carrier_name,
            snapshot_date=snapshot_date,
            policy_status=policy_status,
            state=state
        )
        return {"count": count}
    except Exception as e:
        logger.error(f"Error counting policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/summary", response_model=Dict[str, Any])
async def get_policy_metrics(
    carrier_name: str = Query(None),
    snapshot_date: str = Query(None),
    session: Session = Depends(get_db_session)
):
    """Get aggregated policy metrics."""
    try:
        repo = PolicyRepository(session)
        metrics = repo.get_metrics(
            carrier_name=carrier_name,
            snapshot_date=snapshot_date
        )
        return metrics
    except Exception as e:
        logger.error(f"Error calculating policy metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

