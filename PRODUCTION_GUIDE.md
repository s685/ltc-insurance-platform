# LTC Insurance Data Service - Production Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Environment Setup](#environment-setup)
4. [Configuration](#configuration)
5. [Security](#security)
6. [Performance Optimization](#performance-optimization)
7. [Deployment Steps](#deployment-steps)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance](#maintenance)

---

## Overview

The LTC Insurance Data Service is a production-ready data-as-a-service platform built with:
- **Backend**: FastAPI + Snowflake Snowpark
- **Frontend**: Streamlit
- **Python Version**: 3.9+
- **Architecture**: Microservices with repository pattern

---

## Pre-Deployment Checklist

### Code Quality
- ✅ All Python 3.9 compatibility issues resolved
- ✅ No linter errors
- ✅ Type hints standardized (using `List`, `Dict`, `Optional` from typing)
- ✅ Error handling implemented throughout
- ✅ Logging configured with structlog
- ✅ API documentation available (OpenAPI/Swagger)

### Testing
- [ ] Unit tests executed and passing
- [ ] Integration tests with Snowflake completed
- [ ] Load testing performed
- [ ] Security testing completed
- [ ] API endpoints tested with valid/invalid data

### Infrastructure
- [ ] Snowflake account configured
- [ ] Database and schema created
- [ ] Required tables exist (CLAIMS, POLICIES)
- [ ] Network connectivity verified
- [ ] SSL/TLS certificates ready

###Security
- [ ] Environment variables secured
- [ ] Snowflake credentials rotated
- [ ] CORS origins configured
- [ ] Rate limiting implemented
- [ ] Input validation verified

---

## Environment Setup

### System Requirements

**Production Server**:
- OS: Linux (Ubuntu 20.04+ recommended) or Windows Server
- CPU: Minimum 4 cores (8+ cores recommended)
- RAM: Minimum 8GB (16GB+ recommended)
- Storage: Minimum 20GB SSD
- Python: 3.9 or 3.10

### Python Environment

```bash
# Create virtual environment
python3.9 -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

cd ../frontend
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_USER=production_user
SNOWFLAKE_PASSWORD=your_secure_password
SNOWFLAKE_WAREHOUSE=LTC_WH
SNOWFLAKE_DATABASE=LTC_INSURANCE
SNOWFLAKE_SCHEMA=ANALYTICS
SNOWFLAKE_ROLE=LTC_APP_ROLE

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1
API_TITLE=LTC Insurance Data Service
API_VERSION=1.0.0

# Cache Configuration
CACHE_ENABLED=true
CACHE_TTL=300
REDIS_URL=redis://localhost:6379/0  # Optional

# Logging Configuration
LOG_LEVEL=INFO
LOG_JSON=true

# CORS Configuration
CORS_ORIGINS=["https://your-domain.com","https://www.your-domain.com"]
CORS_CREDENTIALS=true
CORS_METHODS=["GET","POST","PUT","DELETE"]
CORS_HEADERS=["*"]

# Connection Pool Settings
MAX_CONNECTIONS=20
CONNECTION_TIMEOUT=30
```

---

## Configuration

### Backend Configuration

**File**: `backend/app/config.py`

Key settings:
- `max_connections`: Set based on expected concurrent users (10-50 for production)
- `cache_ttl`: Adjust based on data freshness requirements (300-3600 seconds)
- `log_level`: Use `INFO` or `WARNING` in production (avoid `DEBUG`)
- `log_json`: Set to `true` for structured logging

### Frontend Configuration

**Port Configuration**:
```bash
# Default: 8501
streamlit run frontend/streamlit_app.py --server.port 8501
```

**Server Settings** (`.streamlit/config.toml`):
```toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
```

---

## Security

### Best Practices

1. **Credentials Management**
   - Never commit `.env` files
   - Use secret management systems (AWS Secrets Manager, Azure Key Vault)
   - Rotate passwords regularly (every 90 days)
   - Use strong passwords (16+ characters, mixed case, numbers, symbols)

2. **Network Security**
   - Use HTTPS/TLS for all connections
   - Configure firewall rules
   - Implement VPN for database access
   - Restrict Snowflake IP allowlists

3. **Application Security**
   - Enable CORS only for trusted domains
   - Implement rate limiting (nginx, API gateway)
   - Validate all inputs
   - Sanitize error messages (don't expose internal details)
   - Keep dependencies updated

4. **Database Security**
   - Use least-privilege principle for database roles
   - Enable Snowflake MFA
   - Audit database access logs
   - Encrypt data at rest and in transit

### Snowflake Security Setup

```sql
-- Create dedicated role for application
CREATE ROLE LTC_APP_ROLE;

-- Grant minimal required permissions
GRANT USAGE ON WAREHOUSE LTC_WH TO ROLE LTC_APP_ROLE;
GRANT USAGE ON DATABASE LTC_INSURANCE TO ROLE LTC_APP_ROLE;
GRANT USAGE ON SCHEMA LTC_INSURANCE.ANALYTICS TO ROLE LTC_APP_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA LTC_INSURANCE.ANALYTICS TO ROLE LTC_APP_ROLE;

-- Create service account
CREATE USER ltc_service_user PASSWORD='your_secure_password' 
DEFAULT_ROLE=LTC_APP_ROLE MUST_CHANGE_PASSWORD=FALSE;

-- Grant role to user
GRANT ROLE LTC_APP_ROLE TO USER ltc_service_user;
```

---

## Performance Optimization

### Backend Optimizations

1. **Connection Pooling**
   - Configured in `snowpark_session.py`
   - Default: 10 connections (adjust based on load)
   - Monitor pool exhaustion in logs

2. **Caching Strategy**
   - Claims summary: 5 minutes (300s)
   - Policy metrics: 5 minutes (300s)
   - Individual claims: 1 minute (60s)
   - Consider Redis for distributed caching

3. **Query Optimization**
   - Use Snowpark's lazy evaluation
   - Minimize data transfer
   - Add appropriate filters early
   - Use column projection

4. **Async Operations**
   - All I/O operations are async
   - Concurrent query execution where applicable
   - Non-blocking request handling

### Snowflake Optimizations

1. **Warehouse Sizing**
   - Start with SMALL warehouse
   - Scale up based on query performance
   - Consider auto-suspend (5 minutes idle)

2. **Clustering Keys**
   ```sql
   -- Example for CLAIMS table
   ALTER TABLE CLAIMS CLUSTER BY (SUBMISSION_DATE, STATUS);
   
   -- Example for POLICIES table
   ALTER TABLE POLICIES CLUSTER BY (ISSUE_DATE, STATUS);
   ```

3. **Materialized Views**
   ```sql
   -- Create materialized view for frequently accessed aggregations
   CREATE MATERIALIZED VIEW MV_CLAIMS_DAILY_SUMMARY AS
   SELECT 
       DATE_TRUNC('DAY', SUBMISSION_DATE) AS SUBMISSION_DAY,
       STATUS,
       COUNT(*) AS CLAIM_COUNT,
       SUM(CLAIM_AMOUNT) AS TOTAL_AMOUNT
   FROM CLAIMS
   GROUP BY DATE_TRUNC('DAY', SUBMISSION_DATE), STATUS;
   ```

### Frontend Optimizations

1. **Caching**
   - API client uses Streamlit cache
   - Cache TTL aligned with backend
   - Clear cache on data updates

2. **Data Loading**
   - Use pagination for large datasets
   - Limit default results to 50-100 rows
   - Implement lazy loading for dashboards

3. **Rendering**
   - Minimize re-renders
   - Use st.spinner for loading states
   - Optimize Plotly chart configurations

---

## Deployment Steps

### Option 1: Traditional Server Deployment

**1. Prepare Server**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9
sudo apt install python3.9 python3.9-venv -y

# Install system dependencies
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y
```

**2. Deploy Backend**
```bash
# Clone/copy application
cd /opt
sudo mkdir ltc-service
sudo chown $USER:$USER ltc-service
cd ltc-service

# Setup Python environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
cp env.template .env
nano .env  # Edit with production values

# Test backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**3. Setup Systemd Service (Linux)**

Create `/etc/systemd/system/ltc-backend.service`:
```ini
[Unit]
Description=LTC Insurance Backend API
After=network.target

[Service]
Type=simple
User=ltcuser
WorkingDirectory=/opt/ltc-service/backend
Environment="PATH=/opt/ltc-service/venv/bin"
ExecStart=/opt/ltc-service/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ltc-backend
sudo systemctl start ltc-backend
sudo systemctl status ltc-backend
```

**4. Deploy Frontend**
```bash
# Setup frontend service
cd /opt/ltc-service/frontend
pip install -r requirements.txt

# Test frontend
streamlit run streamlit_app.py --server.port 8501
```

Create `/etc/systemd/system/ltc-frontend.service`:
```ini
[Unit]
Description=LTC Insurance Frontend Dashboard
After=network.target ltc-backend.service

[Service]
Type=simple
User=ltcuser
WorkingDirectory=/opt/ltc-service/frontend
Environment="PATH=/opt/ltc-service/venv/bin"
ExecStart=/opt/ltc-service/venv/bin/streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ltc-frontend
sudo systemctl start ltc-frontend
sudo systemctl status ltc-frontend
```

**5. Configure Reverse Proxy (Nginx)**

Install Nginx:
```bash
sudo apt install nginx -y
```

Create `/etc/nginx/sites-available/ltc-service`:
```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend Dashboard
server {
    listen 80;
    server_name dashboard.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    location /_stcore/stream {
        proxy_pass http://localhost:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

Enable and reload:
```bash
sudo ln -s /etc/nginx/sites-available/ltc-service /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**6. Setup SSL/TLS (Let's Encrypt)**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.yourdomain.com -d dashboard.yourdomain.com
```

### Option 2: Docker Deployment

**Backend Dockerfile** (`backend/Dockerfile`):
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app ./app

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Frontend Dockerfile** (`frontend/Dockerfile`):
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Run application
CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

**Docker Compose** (`docker-compose.yml`):
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
    restart: always
    environment:
      - BACKEND_URL=http://backend:8000

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - backend
      - frontend
    restart: always
```

Deploy:
```bash
docker-compose up -d
docker-compose logs -f
```

### Option 3: Cloud Deployment

**AWS (EC2 + ECS/EKS)**:
- Use t3.medium or larger instances
- Configure Auto Scaling Groups
- Use Application Load Balancer
- Store secrets in AWS Secrets Manager
- Enable CloudWatch logging

**Azure (App Service)**:
- Deploy backend as Azure App Service (Python)
- Deploy frontend as separate App Service
- Use Azure Key Vault for secrets
- Configure Application Insights
- Enable auto-scaling

**Google Cloud (Cloud Run)**:
- Containerize both services
- Deploy to Cloud Run
- Use Secret Manager
- Configure Cloud Load Balancing
- Enable Cloud Logging

---

## Monitoring and Logging

### Application Monitoring

**Health Check Endpoint**:
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "database": "LTC_INSURANCE",
  "schema": "ANALYTICS",
  "warehouse": "LTC_WH",
  "timestamp": "2024-01-01T12:00:00",
  "active_sessions": 3,
  "pooled_sessions": 7
}
```

### Logging

**Backend Logs**:
- Structured JSON logging (if LOG_JSON=true)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log rotation recommended (use logrotate)

**Log Locations**:
```bash
# Systemd services
sudo journalctl -u ltc-backend -f
sudo journalctl -u ltc-frontend -f

# Docker
docker logs ltc-backend -f
docker logs ltc-frontend -f
```

**Key Metrics to Monitor**:
- API response times
- Database query times
- Error rates
- Connection pool utilization
- Cache hit rates
- Memory usage
- CPU usage

### Recommended Tools

1. **Application Performance Monitoring**:
   - New Relic
   - DataDog
   - Application Insights

2. **Log Management**:
   - ELK Stack (Elasticsearch, Logstash, Kibana)
   - Splunk
   - CloudWatch Logs

3. **Infrastructure Monitoring**:
   - Prometheus + Grafana
   - Nagios
   - Zabbix

---

## Troubleshooting

### Common Issues

**1. Snowflake Connection Failures**
```
Error: Failed to connect to database
```
**Solutions**:
- Verify credentials in `.env`
- Check Snowflake account status
- Verify network connectivity
- Check IP allowlist in Snowflake
- Ensure warehouse is running

**2. High Memory Usage**
```
Error: Out of memory
```
**Solutions**:
- Reduce `MAX_CONNECTIONS`
- Implement pagination
- Clear cache more frequently
- Increase server RAM
- Check for memory leaks

**3. Slow Query Performance**
```
Warning: Query timeout
```
**Solutions**:
- Add clustering keys
- Optimize WHERE clauses
- Reduce data volume
- Scale up warehouse
- Use materialized views

**4. API Timeout Errors**
```
Error: Request timeout
```
**Solutions**:
- Increase `CONNECTION_TIMEOUT`
- Optimize queries
- Check network latency
- Review cache strategy
- Scale infrastructure

### Debug Mode

Enable debug logging:
```bash
# In .env
LOG_LEVEL=DEBUG
```

Run backend in debug mode:
```bash
uvicorn app.main:app --reload --log-level debug
```

---

## Maintenance

### Regular Tasks

**Daily**:
- Monitor error logs
- Check system resources
- Verify backup completion
- Review slow queries

**Weekly**:
- Analyze performance metrics
- Review security logs
- Check dependency updates
- Test backup restoration

**Monthly**:
- Rotate credentials
- Update dependencies
- Review access logs
- Capacity planning review
- Security audit

### Backup Strategy

**Database**:
```sql
-- Snowflake Time Travel (up to 90 days)
SELECT * FROM CLAIMS AT(TIMESTAMP => DATEADD(day, -1, CURRENT_TIMESTAMP()));

-- Create backup table
CREATE TABLE CLAIMS_BACKUP CLONE CLAIMS;
```

**Application**:
- Version control (Git)
- Configuration backups
- Environment variable backups (encrypted)

### Update Procedure

1. **Test in Staging**
   - Deploy to staging environment
   - Run full test suite
   - Load test
   - Security scan

2. **Schedule Maintenance Window**
   - Notify users
   - Choose low-traffic period
   - Have rollback plan ready

3. **Deploy**
   ```bash
   # Backup current version
   git tag production-backup-$(date +%Y%m%d)
   
   # Pull latest code
   git pull origin main
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Restart services
   sudo systemctl restart ltc-backend
   sudo systemctl restart ltc-frontend
   ```

4. **Verify**
   - Check health endpoint
   - Test key functionality
   - Monitor logs for errors
   - Verify metrics

5. **Rollback (if needed)**
   ```bash
   git checkout production-backup-YYYYMMDD
   pip install -r requirements.txt
   sudo systemctl restart ltc-backend
   sudo systemctl restart ltc-frontend
   ```

### Disaster Recovery

**RTO (Recovery Time Objective)**: 1 hour  
**RPO (Recovery Point Objective)**: 15 minutes

**Recovery Steps**:
1. Notify stakeholders
2. Assess damage
3. Restore from backup
4. Verify data integrity
5. Test functionality
6. Resume operations
7. Post-mortem analysis

---

## Contact and Support

**Technical Support**: [support@yourcompany.com]  
**Emergency Contact**: [on-call@yourcompany.com]  
**Documentation**: [https://docs.yourcompany.com]

---

## Appendix

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| SNOWFLAKE_ACCOUNT | Yes | - | Snowflake account identifier |
| SNOWFLAKE_USER | Yes | - | Snowflake username |
| SNOWFLAKE_PASSWORD | Yes | - | Snowflake password |
| SNOWFLAKE_WAREHOUSE | Yes | - | Snowflake warehouse name |
| SNOWFLAKE_DATABASE | No | LTC_INSURANCE | Database name |
| SNOWFLAKE_SCHEMA | No | ANALYTICS | Schema name |
| SNOWFLAKE_ROLE | No | None | Snowflake role (uses default if not set) |
| API_HOST | No | 0.0.0.0 | API host address |
| API_PORT | No | 8000 | API port |
| API_PREFIX | No | /api/v1 | API route prefix |
| CACHE_ENABLED | No | true | Enable caching |
| CACHE_TTL | No | 300 | Cache TTL in seconds |
| LOG_LEVEL | No | INFO | Logging level |
| LOG_JSON | No | false | Use JSON logging |
| MAX_CONNECTIONS | No | 10 | Max Snowpark connections |
| CONNECTION_TIMEOUT | No | 30 | Connection timeout in seconds |

### API Endpoints Reference

**Health Check**:
- `GET /health` - Check API and database health

**Analytics**:
- `GET /api/v1/analytics/claims-summary` - Get claims summary
- `GET /api/v1/analytics/policy-metrics` - Get policy metrics
- `POST /api/v1/analytics/custom-query` - Execute custom analytics

**Claims**:
- `GET /api/v1/claims/{claim_id}` - Get claim by ID
- `GET /api/v1/claims/` - List claims
- `GET /api/v1/claims/count` - Count claims

**Policies**:
- `GET /api/v1/policies/{policy_id}` - Get policy by ID
- `GET /api/v1/policies/` - List policies
- `GET /api/v1/policies/count` - Count policies

### Performance Benchmarks

**Expected Response Times** (95th percentile):
- Health check: < 100ms
- Claims summary: < 500ms
- Policy metrics: < 500ms
- Individual claim/policy: < 200ms
- List operations (100 items): < 1s

**Throughput**:
- API requests: 100+ req/s
- Concurrent users: 50-100
- Database connections: 10-20 active

---

**Version**: 1.0.0  
**Last Updated**: 2024-10-12  
**Maintained By**: Development Team

