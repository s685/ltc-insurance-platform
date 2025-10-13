# Table Migration Guide

## Overview
This document describes the migration from simple CLAIMS and POLICIES tables to the comprehensive Snowflake snapshot tables.

## New Tables

### 1. CLAIMS_TPA_FEE_WORKSHEET_SNAPSHOT_FACT
Replaces: `CLAIMS`

**Key Fields Mapping:**
- `TPA_FEE_WORKSHEET_SNAPSHOT_FACT_ID` → Primary identifier (was `CLAIM_ID`)
- `POLICY_DIM_ID` → Links to policy (was `POLICY_ID`)
- `CLAIMANTNAME` → Claimant information
- `DECISION` → Claim decision status
- `RFB_PROCESS_TO_DECISION_TAT` → Processing time (was calculated)
- `CERTIFICATION_DATE` → Important date (was `APPROVAL_DATE`)

### 2. POLICY_MONTHLY_SNAPSHOT_FACT
Replaces: `POLICIES`

**Key Fields Mapping:**
- `POLICY_MONTHLY_SNAPSHOT_ID` → Primary identifier
- `POLICY_DIM_ID` → Policy dimension key
- `POLICY_ID` → Actual policy ID (numeric)
- `ANNUALIZED_PREMIUM` → Annual premium amount
- `INSURED_STATE` → State information
- `TOTAL_ACTIVE_CLAIMS` → Active claims count
- `CLAIM_STATUS_CD` → Current claim status

## Updated Domain Models

The domain models in `backend/app/models/domain.py` have been updated to include all fields from the new tables while maintaining compatibility with existing analytics logic.

### Key Changes:

**Policy Model:**
- Added 50+ fields from POLICY_MONTHLY_SNAPSHOT_FACT
- Maintained core methods: `is_active()`, `monthly_premium()`, `annual_premium()`
- New method: `has_active_claims()`

**Claim Model:**
- Added 60+ fields from CLAIMS_TPA_FEE_WORKSHEET_SNAPSHOT_FACT
- Maintained core methods: `is_approved()`, `is_denied()`, `processing_days()`
- New method: `total_decisions()`

## Repository Updates

### ClaimsRepository
- Table name: `CLAIMS_TPA_FEE_WORKSHEET_SNAPSHOT_FACT`
- Updated column mappings in `_row_to_claim()`
- Filter columns updated

### PolicyRepository
- Table name: `POLICY_MONTHLY_SNAPSHOT_FACT`
- Updated column mappings in `_row_to_policy()`
- Filter columns updated

## Analytics Compatibility

The analytics service continues to work with the new tables because:
1. Core business logic methods are preserved
2. Aggregation queries adapted to new column names
3. Status determination logic updated for new decision values

## Frontend Compatibility

No changes required to frontend components. The API schemas abstract the table structure changes.

## Testing Required

After migration, test the following:

1. **Health Check**: Verify database connection
   ```bash
   curl http://localhost:8000/health
   ```

2. **Claims Summary**: Check aggregation works
   ```bash
   curl http://localhost:8000/api/v1/analytics/claims-summary
   ```

3. **Policy Metrics**: Verify policy aggregations
   ```bash
   curl http://localhost:8000/api/v1/analytics/policy-metrics
   ```

4. **List Operations**: Test pagination
   ```bash
   curl http://localhost:8000/api/v1/claims/?limit=10
   curl http://localhost:8000/api/v1/policies/?limit=10
   ```

## Rollback Plan

If issues occur:
1. Revert domain models to previous version
2. Restore original table names in repositories
3. Restart backend service

## Performance Considerations

The new tables are much larger with many more columns. Consider:
1. **Query Optimization**: Only SELECT needed columns
2. **Indexing**: Ensure POLICY_DIM_ID and date columns are indexed
3. **Partitioning**: Use SNAPSHOT_DATE for partitioning
4. **Caching**: Increase cache TTL for expensive aggregations

## Column Name Standardization

### Claims Table Column Mapping
```
OLD → NEW
=========================================
CLAIM_ID → TPA_FEE_WORKSHEET_SNAPSHOT_FACT_ID
POLICY_ID → POLICY_DIM_ID  
CLAIM_NUMBER → (use POLICY_NUMBER)
STATUS → DECISION
SUBMISSION_DATE → RFB_ENTERED_DT
APPROVAL_DATE → CERTIFICATION_DATE
CLAIM_AMOUNT → (calculated from decisions)
```

### Policy Table Column Mapping
```
OLD → NEW
=========================================
POLICY_ID → POLICY_ID (numeric, not PK)
POLICY_NUMBER → (not in snapshot, may need join)
STATUS → CLAIM_STATUS_CD
ISSUE_DATE → ORIGINAL_EFFECTIVE_DT
PREMIUM_AMOUNT → ANNUALIZED_PREMIUM / 12
INSURED_AGE → RATED_AGE
INSURED_STATE → INSURED_STATE
```

## Migration Steps

1. ✅ Update domain models
2. ✅ Update repository table names  
3. ⏳ Update column mappings in `_row_to_claim()` - **IN PROGRESS**
4. ⏳ Update column mappings in `_row_to_policy()` - **IN PROGRESS**
5. ⏳ Update filter column names
6. ⏳ Update aggregation queries
7. ⏳ Test all endpoints
8. ⏳ Update configuration (if needed)
9. ⏳ Deploy and monitor

## Support

For issues or questions:
- Review CODE_REVIEW_SUMMARY.md
- Check PRODUCTION_GUIDE.md for deployment
- Monitor application logs for errors

