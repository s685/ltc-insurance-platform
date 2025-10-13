# Production Deployment Guide

## Pre-Deployment Checklist

### ✅ Code Quality
- [x] All temporary/test files removed
- [x] Debug code cleaned up
- [x] Exception handlers enabled
- [x] Caching enabled
- [x] Proper logging configured
- [x] Type hints throughout codebase
- [x] No TODO/FIXME comments

### ✅ Security
- [x] No hardcoded credentials
- [x] `.env` file in `.gitignore`
- [x] Secrets template files provided
- [x] CORS origins properly configured
- [x] Input validation with Pydantic

### ✅ Configuration
- [x] Environment templates provided
- [x] All required env vars documented
- [x] Default values set appropriately
- [x] Connection pooling configured

### ✅ Documentation
- [x] README.md comprehensive
- [x] QUICK_START.md guide available
- [x] SQL scripts provided
- [x] API documentation auto-generated

## Production Environment Setup

### 1. Backend Configuration

**Update `backend/.env` for production:**

```env
# Production Snowflake
SNOWFLAKE_ACCOUNT=your_prod_account
SNOWFLAKE_USER=your_prod_user
SNOWFLAKE_PASSWORD=your_secure_password
SNOWFLAKE_WAREHOUSE=PROD_WH
SNOWFLAKE_DATABASE=LTC_INSURANCE
SNOWFLAKE_SCHEMA=ANALYTICS
SNOWFLAKE_ROLE=ANALYTICS_ROLE

# Production API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
LOG_JSON=true

# Production Cache (Redis recommended)
CACHE_ENABLED=true
CACHE_TTL=300
REDIS_URL=redis://your-redis-host:6379
REDIS_ENABLED=true

# CORS (Update with your frontend domain)
CORS_ORIGINS=["https://your-streamlit-domain.com"]
CORS_ALLOW_CREDENTIALS=true

# Connection Pool (adjust based on load)
MAX_POOL_CONNECTIONS=10
```

### 2. Frontend Configuration

**Update `frontend/.streamlit/secrets.toml` for production:**

```toml
API_BASE_URL = "https://your-api-domain.com"
```

**Update `frontend/.streamlit/config.toml` for production:**

```toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#00CC96"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

### 3. Database Setup

**Run in production Snowflake:**

```sql
-- 1. Create database and schema
CREATE DATABASE IF NOT EXISTS LTC_INSURANCE;
CREATE SCHEMA IF NOT EXISTS LTC_INSURANCE.ANALYTICS;

-- 2. Run table creation scripts
-- Execute: sql_scripts/01_create_tables.sql

-- 3. Grant permissions
GRANT USAGE ON DATABASE LTC_INSURANCE TO ROLE ANALYTICS_ROLE;
GRANT USAGE ON SCHEMA LTC_INSURANCE.ANALYTICS TO ROLE ANALYTICS_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA LTC_INSURANCE.ANALYTICS TO ROLE ANALYTICS_ROLE;
```

### 4. Redis Setup (Recommended)

**Option 1: Managed Redis (AWS ElastiCache, Azure Cache, etc.)**
- Provision managed Redis instance
- Update `REDIS_URL` in backend `.env`
- Ensure network connectivity

**Option 2: Self-hosted Redis**
```bash
docker run -d \
  --name redis-prod \
  -p 6379:6379 \
  -v redis-data:/data \
  redis:latest redis-server --appendonly yes
```

### 5. Deployment Options

#### Option A: Docker Deployment (Recommended)

**Create `backend/Dockerfile`:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Create `frontend/Dockerfile`:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Create `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    depends_on:
      - redis
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
    restart: unless-stopped

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
```

#### Option B: Cloud Platform Deployment

**AWS (ECS/Fargate):**
1. Push Docker images to ECR
2. Create ECS task definitions
3. Configure ALB for routing
4. Set environment variables in ECS

**Azure (Container Apps):**
1. Push to Azure Container Registry
2. Create Container Apps for backend/frontend
3. Configure ingress rules
4. Set environment variables in portal

**GCP (Cloud Run):**
1. Push to Container Registry
2. Deploy to Cloud Run services
3. Configure service networking
4. Set environment variables

#### Option C: VM Deployment

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

**Frontend:**
```bash
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

### 6. Monitoring & Logging

**Setup Application Monitoring:**
- Configure structured logging (set `LOG_JSON=true`)
- Ship logs to centralized system (ELK, Splunk, CloudWatch)
- Monitor API response times
- Track cache hit rates
- Monitor Snowflake query performance

**Health Checks:**
- Backend: `GET /health`
- Check database connectivity
- Monitor Redis connectivity

**Metrics to Track:**
- API request rate
- Error rate
- Average response time
- Cache hit/miss ratio
- Database query time
- Active connections

### 7. Security Hardening

**API Security:**
- Use HTTPS only in production
- Implement rate limiting
- Add API authentication (OAuth2, JWT)
- Enable request size limits
- Configure timeout settings

**Snowflake Security:**
- Use service account with minimal permissions
- Rotate credentials regularly
- Enable MFA on accounts
- Use network policies
- Enable query auditing

**Network Security:**
- Use VPC/VNet for isolation
- Configure security groups/NSGs
- Use private endpoints where possible
- Enable firewall rules

### 8. Performance Optimization

**Backend:**
- Increase connection pool size based on load
- Tune cache TTL values
- Enable Snowflake result caching
- Use database indexes appropriately

**Frontend:**
- Enable Streamlit caching
- Optimize Plotly chart rendering
- Lazy load data tables
- Implement pagination for large datasets

**Database:**
- Create appropriate indexes
- Partition large tables
- Use clustering keys
- Enable query result caching

### 9. Backup & Disaster Recovery

**Code:**
- Regular Git backups
- Tag releases
- Maintain staging environment

**Database:**
- Snowflake Time Travel enabled
- Regular snapshots
- Test restore procedures

**Configuration:**
- Backup environment variables
- Document all settings
- Version control configuration

### 10. Post-Deployment Verification

**Smoke Tests:**
```bash
# Backend health check
curl https://your-api-domain.com/health

# Test policy endpoint
curl https://your-api-domain.com/api/v1/policies/?limit=1

# Test claims endpoint
curl https://your-api-domain.com/api/v1/claims/?limit=1

# Frontend access
# Open browser: https://your-streamlit-domain.com
```

**Functional Tests:**
- [ ] Homepage loads successfully
- [ ] Claims dashboard displays data
- [ ] Policy dashboard displays data
- [ ] Filters work correctly
- [ ] Data exports work
- [ ] Charts render properly
- [ ] API documentation accessible

## Maintenance

### Regular Tasks
- **Daily:** Monitor logs and error rates
- **Weekly:** Review performance metrics
- **Monthly:** Update dependencies
- **Quarterly:** Rotate credentials

### Scaling
- **Horizontal:** Add more API instances behind load balancer
- **Vertical:** Increase instance sizes
- **Database:** Scale Snowflake warehouse
- **Cache:** Use Redis cluster

## Rollback Procedure

If issues occur after deployment:

1. **Code Rollback:**
   ```bash
   git revert <commit-hash>
   # Or: git checkout <previous-tag>
   ```

2. **Database Rollback:**
   ```sql
   -- Use Snowflake Time Travel
   SELECT * FROM TABLE_NAME AT(OFFSET => -3600); -- 1 hour ago
   ```

3. **Infrastructure Rollback:**
   - Revert to previous Docker image
   - Restore previous configuration

## Support & Troubleshooting

### Common Production Issues

**High Memory Usage:**
- Check cache size
- Review connection pool settings
- Monitor Snowflake query complexity

**Slow API Responses:**
- Check Snowflake warehouse size
- Review query efficiency
- Verify cache is working
- Check network latency

**Connection Errors:**
- Verify credentials
- Check network connectivity
- Review firewall rules
- Check connection pool exhaustion

### Getting Help
- Review application logs
- Check Snowflake query history
- Monitor system resources
- Review API documentation

## Success Criteria

✅ **Deployment is successful when:**
- All endpoints return expected results
- Dashboards load without errors
- Response times are acceptable (<2s)
- Error rate is minimal (<1%)
- Monitoring is active
- Logs are being collected
- Backups are configured

---

**Last Updated:** October 2024  
**Version:** 1.0.0

