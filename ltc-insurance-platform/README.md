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
│  ┌──────────────┐  ┌──────────────┐                         │
│  │   POLICIES   │  │    CLAIMS    │                         │
│  └──────────────┘  └──────────────┘                         │
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
- ✅ **Redis Caching** with fallback to memory cache
- ✅ **Structured Logging** with configurable output
- ✅ **Error Handling** with custom exceptions
- ✅ **OpenAPI Documentation** auto-generated
- ✅ **CORS Support** for frontend integration

### Frontend (Streamlit)
- ✅ **Interactive Dashboards** for claims and policy analytics
- ✅ **Real-time Data** from Snowflake via API
- ✅ **Advanced Visualizations** using Plotly
- ✅ **Type-safe API Client** with retry logic
- ✅ **Configurable Filters** for flexible analysis
- ✅ **KPI Cards** for key metrics
- ✅ **Data Tables** with export functionality
- ✅ **Responsive Design** with multi-column layouts

## 📁 Project Structure

```
ltc-insurance-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── config.py                  # Settings with pydantic-settings
│   │   ├── dependencies.py            # Dependency injection setup
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── analytics.py       # Analytics endpoints
│   │   │       ├── claims.py          # Claims data endpoints
│   │   │       └── policies.py        # Policy endpoints
│   │   ├── core/
│   │   │   ├── snowpark_session.py    # Snowpark session manager
│   │   │   ├── cache.py               # Caching utilities
│   │   │   └── exceptions.py          # Custom exceptions
│   │   ├── models/
│   │   │   ├── schemas.py             # Pydantic API models
│   │   │   └── domain.py              # Domain models
│   │   ├── repositories/
│   │   │   ├── base.py                # Abstract base repository
│   │   │   ├── claims_repo.py         # Claims repository
│   │   │   └── policy_repo.py         # Policy repository
│   │   └── services/
│   │       ├── analytics_service.py   # Analytics business logic
│   │       └── claims_service.py      # Claims business logic
│   ├── requirements.txt
│   └── env.template                    # Environment variables template
├── frontend/
│   ├── streamlit_app.py               # Main Streamlit application
│   ├── components/
│   │   ├── claims_dashboard.py        # Claims dashboard UI
│   │   └── policy_analytics.py        # Policy analytics UI
│   ├── services/
│   │   └── api_client.py              # Type-safe API client
│   ├── utils/
│   │   └── formatters.py              # Data formatting utilities
│   ├── .streamlit/
│   │   ├── config.toml                # Streamlit configuration
│   │   └── secrets.toml.template      # Secrets template
│   └── requirements.txt
├── sql_scripts/
│   ├── 01_create_tables.sql           # Table creation script
│   └── 02_insert_sample_data.sql      # Sample data script
├── README.md
└── .gitignore
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.9 or higher** (3.10+ recommended)
- **Snowflake account** with LTC insurance database
- **Redis** (optional, for distributed caching)

### Redis Setup (Recommended)

Choose one of the following options:

**Option 1: Docker (Recommended)**
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

**Option 2: Memurai (Windows-native)**
- Download from https://www.memurai.com/
- Install the community edition
- Start Memurai service

**Option 3: WSL2 + Redis**
```bash
# In WSL2
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

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
   REDIS_URL=redis://localhost:6379
   REDIS_ENABLED=true
   ```

5. **Setup Snowflake database** (if not already done)
   
   Run the SQL scripts in Snowflake:
   ```bash
   # In Snowflake, run these scripts:
   # 1. sql_scripts/01_create_tables.sql
   # 2. sql_scripts/02_insert_sample_data.sql
   ```

6. **Run the backend API**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```
   
   Or:
   ```bash
   python app/main.py
   ```
   
   The API will be available at: http://localhost:8000

7. **Access API documentation**
   - Swagger UI: http://localhost:8000/api/v1/docs
   - ReDoc: http://localhost:8000/api/v1/redoc
   - Health Check: http://localhost:8000/health

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

4. **Configure Streamlit secrets**
   
   Create `.streamlit/secrets.toml` from template:
   ```bash
   cp .streamlit/secrets.toml.template .streamlit/secrets.toml
   ```
   
   Edit `.streamlit/secrets.toml`:
   ```toml
   API_BASE_URL = "http://localhost:8000"
   ```

5. **Run Streamlit application**
   ```bash
   streamlit run streamlit_app.py
   ```
   
   The application will open in your browser at: http://localhost:8501

## 📊 Database Schema

The application uses two main tables in Snowflake:

### POLICY_MONTHLY_SNAPSHOT_FACT
Contains policy information including:
- Policy identifiers and status
- Premium details (annualized, collected, waiver)
- Insured life information
- Waiver and nonforfeiture status
- Active claims count
- Geographic information

**Key Filters:**
- `CARRIER_NAME`: Filter by insurance carrier
- `POLICY_SNAPSHOT_DATE`: Filter by snapshot date
- `INSURED_STATE`: Filter by state

### CLAIMS_TPA_FEE_WORKSHEET_SNAPSHOT_FACT
Contains claims processing information including:
- Claim identifiers and status
- Decision types (Approved, Denied, In Assessment, etc.)
- Processing times (TAT metrics)
- Category breakdown (Facility, Home Health, Other)
- Retroactive claim indicators
- Ongoing rate month (Initial=0, Ongoing=1, Restoration=2)

**Key Filters:**
- `CARRIER_NAME`: Filter by insurance carrier
- `SNAPSHOT_DATE`: Filter by snapshot date
- `DECISION`: Filter by decision type
- `ONGOING_RATE_MONTH`: Filter by decision category

**Business Logic:**
The claims filtering implements specific business rules:
```sql
WHERE (
  (ONGOING_RATE_MONTH = 1 AND IS_INITIAL_DECISION_FLAG IN (0,1))
  OR (ONGOING_RATE_MONTH = 0 AND IS_INITIAL_DECISION_FLAG = 1)
  OR (ONGOING_RATE_MONTH = 2 AND IS_INITIAL_DECISION_FLAG IN (0,1))
)
```

## 🎯 API Endpoints

### Analytics
- `GET /api/v1/analytics/policy-insights` - Get comprehensive policy insights
- `GET /api/v1/analytics/policy-metrics` - Get policy metrics
- `GET /api/v1/analytics/combined-dashboard` - Get combined dashboard data

### Claims
- `GET /api/v1/claims/{claim_id}` - Get claim by ID
- `GET /api/v1/claims/` - List claims with filtering
- `GET /api/v1/claims/summary/statistics` - Get claims summary
- `GET /api/v1/claims/insights/detailed` - Get detailed insights
- `GET /api/v1/claims/count/total` - Count claims

### Policies
- `GET /api/v1/policies/{policy_id}` - Get policy by ID
- `GET /api/v1/policies/` - List policies with filtering
- `GET /api/v1/policies/metrics/summary` - Get policy metrics
- `GET /api/v1/policies/count/total` - Count policies

### Health
- `GET /health` - Health check endpoint

## 📈 Dashboard Features

### Claims Dashboard
- **Total Claims** - Overall claim count
- **Approval Rate** - Percentage of approved claims
- **Average Processing Time** - TAT in days
- **Retro Claims %** - Percentage of retroactive claims
- **Decision Distribution** - Pie chart of decisions
- **Category Breakdown** - Bar chart by category
- **Ongoing Rate Analysis** - Initial vs Ongoing vs Restoration
- **Retro Analysis** - Detailed retroactive claims analysis
- **Recent Claims Table** - Downloadable data table

### Policy Dashboard
- **Total Policies** - Overall policy count
- **Active Policies** - Currently active policies
- **Lapse Rate** - Percentage of lapsed policies
- **Average Premium** - Average annualized premium
- **Total Premium Revenue** - Sum of all premiums
- **Average Insured Age** - Average age of insured lives
- **Waiver Status** - Policies in/not in waiver
- **Forfeiture Status** - Nonforfeiture tracking
- **State Distribution** - Policies by state (top 10)
- **Premium by State** - Revenue by state (top 10)
- **Recent Policies Table** - Downloadable data table

## 🔧 Configuration

### Backend Configuration (`.env`)

```env
# Snowflake
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=LTC_INSURANCE
SNOWFLAKE_SCHEMA=ANALYTICS

# API
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1

# Cache
CACHE_ENABLED=true
CACHE_TTL=300
REDIS_URL=redis://localhost:6379
REDIS_ENABLED=true

# Logging
LOG_LEVEL=INFO
LOG_JSON=false

# CORS
CORS_ORIGINS=["http://localhost:8501"]
```

### Frontend Configuration (`.streamlit/secrets.toml`)

```toml
API_BASE_URL = "http://localhost:8000"
```

## 🐛 Troubleshooting

### Backend Issues

**Connection Error**
- Verify Snowflake credentials in `.env`
- Check network connectivity
- Ensure warehouse is running

**Redis Connection Failed**
- Application will fallback to memory cache
- Check Redis is running: `redis-cli ping`
- Verify REDIS_URL in `.env`

**Import Errors**
- Verify virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend Issues

**API Connection Failed**
- Ensure backend is running on port 8000
- Check `API_BASE_URL` in `.streamlit/secrets.toml`
- Verify CORS settings in backend

**Slow Dashboard Loading**
- Check Redis caching is enabled
- Reduce date range filter
- Check Snowflake query performance

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
2. Add data fetching logic using API client
3. Create visualizations with Plotly
4. Add navigation in `streamlit_app.py`

## 📚 Technology Stack

### Backend
- **FastAPI** - Modern web framework
- **Snowpark** - Snowflake Python SDK
- **Redis** - In-memory caching
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Frontend
- **Streamlit** - Web framework
- **Plotly** - Interactive visualizations
- **Pandas** - Data manipulation
- **Requests** - HTTP client

### Database
- **Snowflake** - Cloud data warehouse

## 📄 License

Proprietary - Internal Use Only

## 🤝 Support

For questions or contributions, please contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: October 2024

*Built with ❤️ using FastAPI, Snowpark, and Streamlit*

