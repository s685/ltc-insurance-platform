# Quick Start Guide - LTC Insurance Platform

## Fastest Way to Get Started

### 1. Start Redis (5 minutes)

**Windows (Docker):**
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

**Or skip Redis** - The app will use memory cache instead.

### 2. Setup Backend (10 minutes)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Create .env from template
copy env.template .env
# Edit .env with your Snowflake credentials

# Run backend
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Setup Snowflake Database (5 minutes)

In Snowflake, run these scripts:
1. `sql_scripts/01_create_tables.sql`
2. `sql_scripts/02_insert_sample_data.sql`

### 4. Setup Frontend (5 minutes)

```bash
cd frontend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Create secrets file
mkdir .streamlit
echo 'API_BASE_URL = "http://localhost:8000"' > .streamlit/secrets.toml

# Run frontend
streamlit run streamlit_app.py
```

### 5. Access the Application

- **Frontend Dashboard:** http://localhost:8501
- **Backend API Docs:** http://localhost:8000/api/v1/docs
- **Health Check:** http://localhost:8000/health

## Test with Sample Data

The sample data includes:
- **4 Policies** (Acme Insurance Co, Beta Health Insurance, Gamma Long Term Care)
- **4 Claims** (Various decision types, categories, and statuses)

Use these filters in the dashboards:
- **Carrier Name:** `Acme Insurance Co`
- **Snapshot Date:** `2024-10-31`
- **Report End Date:** `2024-10-31`

## Common Issues

**Backend won't start:**
- Check Snowflake credentials in `.env`
- Ensure Redis is running (or set `REDIS_ENABLED=false`)

**Frontend can't connect:**
- Verify backend is running on port 8000
- Check `.streamlit/secrets.toml` has correct API URL

**No data showing:**
- Ensure you ran the SQL scripts in Snowflake
- Verify carrier name and dates match sample data

## Next Steps

1. **Explore Dashboards:**
   - Claims Analytics: Track approvals, denials, processing times
   - Policy Analytics: Monitor active policies, premiums, lapse rates

2. **Load Your Data:**
   - Replace sample data with your actual LTC insurance data
   - Update carrier names and dates in filters

3. **Customize:**
   - Add new visualizations in `frontend/components/`
   - Add new endpoints in `backend/app/api/routes/`
   - Modify business logic in `backend/app/services/`

## Getting Help

- Check `README.md` for detailed documentation
- Review API docs at http://localhost:8000/api/v1/docs
- Check logs for error messages

---

**Estimated Total Setup Time:** 25-30 minutes

