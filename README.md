# LTC Insurance Data Service Platform

A production-ready data-as-a-service platform for long-term care insurance analytics using FastAPI, Snowpark, and Streamlit.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  (Interactive Dashboards & Visualizations)                   │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Services   │  │ Repositories │  │    Models    │      │
│  │  (Business   │◄─┤   (Data      │◄─┤  (Schemas &  │      │
│  │   Logic)     │  │   Access)    │  │   Domain)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                                 │
│         └──────────────────┼─────────────────────────►      │
│                            ▼                                 │
│                    Snowpark Session                          │
│                     (Connection Pool)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Snowflake Data Warehouse                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   POLICIES   │  │    CLAIMS    │  │  ANALYTICS   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Features

### Backend (FastAPI + Snowpark)
- ✅ **RESTful API** with comprehensive endpoints for claims and policy analytics
- ✅ **Snowpark Integration** with connection pooling and session management
- ✅ **Repository Pattern** for clean data access layer
- ✅ **Service Layer** with business logic separation
- ✅ **Dependency Injection** using FastAPI's DI system
- ✅ **Type Safety** with Pydantic models and full type hints
- ✅ **Async/Await** for concurrent database operations
- ✅ **Caching Layer** with in-memory and Redis support
- ✅ **Structured Logging** with JSON output option
- ✅ **Error Handling** with custom exceptions
- ✅ **OpenAPI Documentation** auto-generated
- ✅ **CORS Support** for frontend integration

### Frontend (Streamlit)
- ✅ **Interactive Dashboards** for claims and policy analytics
- ✅ **Real-time Data** from Snowflake via API
- ✅ **Advanced Visualizations** using Plotly
- ✅ **Type-safe API Client** with retry logic
- ✅ **Date Range Filters** for flexible analysis
- ✅ **KPI Cards** for key metrics
- ✅ **Data Tables** with color-coded status
- ✅ **Responsive Design** with multi-column layouts

## 📁 Project Structure

```
ltc-data-service/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── config.py                  # Settings with pydantic-settings
│   │   ├── dependencies.py            # Dependency injection setup
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── analytics.py      # Analytics endpoints
│   │   │   │   ├── claims.py         # Claims data endpoints
│   │   │   │   └── policies.py       # Policy endpoints
│   │   ├── core/
│   │   │   ├── snowpark_session.py   # Snowpark session manager
│   │   │   ├── cache.py              # Caching utilities
│   │   │   └── exceptions.py         # Custom exceptions
│   │   ├── models/
│   │   │   ├── schemas.py            # Pydantic API models
│   │   │   └── domain.py             # Domain models
│   │   ├── repositories/
│   │   │   ├── base.py               # Abstract base repository
│   │   │   ├── claims_repo.py        # Claims repository
│   │   │   └── policy_repo.py        # Policy repository
│   │   └── services/
│   │       ├── analytics_service.py  # Analytics business logic
│   │       └── claims_service.py     # Claims business logic
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_analytics.py
│   ├── requirements.txt
│   └── env.template                   # Environment variables template
├── frontend/
│   ├── streamlit_app.py              # Main Streamlit application
│   ├── components/
│   │   ├── claims_dashboard.py       # Claims dashboard UI
│   │   ├── policy_analytics.py       # Policy analytics UI
│   │   └── visualizations.py         # Reusable chart components
│   ├── services/
│   │   └── api_client.py             # Type-safe API client
│   ├── utils/
│   │   └── formatters.py             # Data formatting utilities
│   └── requirements.txt
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.9 or higher** (3.10+ recommended)
- Snowflake account with LTC insurance data
- (Optional) Redis for distributed caching

> **Note**: The application is compatible with Python 3.9+. Python 3.10+ is recommended for optimal performance.

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Copy `env.template` to `.env` and update with your Snowflake credentials:
   
   ```bash
   cp env.template .env
   ```
   
   Edit `.env`:
   ```env
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_USER=your_user
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_DATABASE=LTC_INSURANCE
   SNOWFLAKE_SCHEMA=ANALYTICS
   ```

5. **Run the backend API**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   
   The API will be available at: http://localhost:8000

6. **Access API documentation**
   - Swagger UI: http://localhost:8000/api/v1/docs
   - ReDoc: http://localhost:8000/api/v1/redoc

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Create virtual environment (or use the same one)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Streamlit application**
   ```bash
   streamlit run streamlit_app.py
   ```
   
   The application will open in your browser at: http://localhost:8501

## 📊 Snowflake Database Schema

The application expects the following tables in Snowflake:

### POLICIES Table
```sql
CREATE TABLE POLICIES (
    POLICY_ID VARCHAR PRIMARY KEY,
    POLICY_NUMBER VARCHAR NOT NULL,
    POLICY_TYPE VARCHAR NOT NULL,  -- COMPREHENSIVE, FACILITY_ONLY, HOME_CARE, HYBRID
    STATUS VARCHAR NOT NULL,        -- ACTIVE, LAPSED, TERMINATED, PENDING, SUSPENDED
    ISSUE_DATE DATE NOT NULL,
    EFFECTIVE_DATE DATE NOT NULL,
    PREMIUM_AMOUNT DECIMAL(10,2) NOT NULL,
    BENEFIT_AMOUNT DECIMAL(10,2) NOT NULL,
    ELIMINATION_PERIOD_DAYS INT NOT NULL,
    BENEFIT_PERIOD_MONTHS INT NOT NULL,
    INSURED_NAME VARCHAR NOT NULL,
    INSURED_AGE INT NOT NULL,
    INSURED_STATE VARCHAR(2) NOT NULL,
    AGENT_ID VARCHAR,
    TERMINATION_DATE DATE,
    LAST_PREMIUM_DATE DATE
);
```

### CLAIMS Table
```sql
CREATE TABLE CLAIMS (
    CLAIM_ID VARCHAR PRIMARY KEY,
    CLAIM_NUMBER VARCHAR NOT NULL,
    POLICY_ID VARCHAR NOT NULL,
    STATUS VARCHAR NOT NULL,        -- SUBMITTED, UNDER_REVIEW, APPROVED, DENIED, PAID, APPEALED
    CLAIM_TYPE VARCHAR NOT NULL,
    SUBMISSION_DATE TIMESTAMP NOT NULL,
    SERVICE_START_DATE DATE NOT NULL,
    SERVICE_END_DATE DATE,
    CLAIM_AMOUNT DECIMAL(10,2) NOT NULL,
    APPROVED_AMOUNT DECIMAL(10,2),
    PAID_AMOUNT DECIMAL(10,2),
    DENIAL_REASON VARCHAR,
    APPROVAL_DATE TIMESTAMP,
    PAYMENT_DATE TIMESTAMP,
    REVIEWER_ID VARCHAR,
    FACILITY_NAME VARCHAR,
    DIAGNOSIS_CODES VARCHAR,
    FOREIGN KEY (POLICY_ID) REFERENCES POLICIES(POLICY_ID)
);
```

## 🔧 Configuration

### Backend Configuration

Edit `.env` file or set environment variables:

```env
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=LTC_INSURANCE
SNOWFLAKE_SCHEMA=ANALYTICS

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1

# Cache Configuration
CACHE_ENABLED=true
CACHE_TTL=300
REDIS_URL=redis://localhost:6379  # Optional

# Logging
LOG_LEVEL=INFO
LOG_JSON=false

# CORS
CORS_ORIGINS=["http://localhost:8501"]
```

### Frontend Configuration

The frontend is configured to connect to the backend at `http://localhost:8000` by default. To change this, modify the `base_url` parameter when creating the `APIClient` in `streamlit_app.py`.

## 🎯 API Endpoints

### Analytics
- `GET /api/v1/analytics/claims-summary` - Get claims summary statistics
- `GET /api/v1/analytics/policy-metrics` - Get policy metrics
- `POST /api/v1/analytics/custom-query` - Execute custom analytics query
- `GET /api/v1/analytics/trends` - Get trend data

### Claims
- `GET /api/v1/claims/{claim_id}` - Get claim by ID
- `GET /api/v1/claims/` - List claims with filtering
- `GET /api/v1/claims/count` - Count claims

### Policies
- `GET /api/v1/policies/{policy_id}` - Get policy by ID
- `GET /api/v1/policies/` - List policies with filtering
- `GET /api/v1/policies/count` - Count policies

### Health
- `GET /health` - Health check endpoint

## 🧪 Testing

Run backend tests:

```bash
cd backend
pytest tests/
```

## 📈 Advanced Python Features Used

- **Type Hints**: Full type coverage with mypy compatibility
- **Async/Await**: Concurrent database operations
- **Context Managers**: Resource management for Snowpark sessions
- **Decorators**: Caching, logging, retry logic
- **Generic Types**: Type-safe repository pattern
- **Pydantic Models**: Data validation and serialization
- **Dependency Injection**: FastAPI DI system
- **Structured Logging**: JSON logging with structlog
- **Connection Pooling**: Efficient Snowpark session management

## 🔒 Security Features

- Input validation with Pydantic
- Parameterized queries to prevent SQL injection
- Environment-based configuration
- CORS configuration
- Error message sanitization

## 🎨 UI Features

### Claims Dashboard
- Total claims and approval rates
- Average processing time
- Claims distribution by status
- Amount comparison charts
- Recent claims table with status highlighting

### Policy Analytics Dashboard
- Active policy metrics
- Lapse rate gauge
- Policy type distribution
- Premium revenue analysis
- Coverage ratio insights
- Recent policies table

## 📝 Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Document functions with docstrings
- Keep functions focused and small

### Adding New Endpoints

1. Define Pydantic schema in `models/schemas.py`
2. Add repository method in appropriate repository
3. Implement business logic in service layer
4. Create route in `api/routes/`
5. Register router in `main.py`

### Adding New Dashboards

1. Create component in `frontend/components/`
2. Add data fetching logic
3. Create visualizations
4. Add navigation in sidebar

## 🐛 Troubleshooting

### Backend Issues

**Connection Error**
- Verify Snowflake credentials in `.env`
- Check network connectivity
- Ensure warehouse is running

**Import Errors**
- Verify virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend Issues

**API Connection Failed**
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify API base URL in frontend

**Slow Dashboard Loading**
- Enable caching in backend
- Reduce date range filter
- Check Snowflake query performance

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Snowflake Snowpark Documentation](https://docs.snowflake.com/en/developer-guide/snowpark/python/index.html)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)

## 📄 License

Proprietary - Internal Use Only

## 🤝 Contributing

For questions or contributions, please contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: October 2024

