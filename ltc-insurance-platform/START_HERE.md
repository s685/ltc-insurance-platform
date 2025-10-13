# 🚀 START HERE - LTC Insurance Platform

## Welcome! Your Platform is Ready

This is a complete, production-ready LTC Insurance Data Service Platform built with FastAPI, Snowpark, and Streamlit.

## ⚡ Quick Start (3 Steps)

### Step 1: Setup Backend (5 minutes)

```bash
cd backend
cp env.template .env
# Edit .env with your Snowflake credentials
```

### Step 2: Setup Snowflake (5 minutes)

Run these SQL scripts in Snowflake:
1. `sql_scripts/01_create_tables.sql`
2. `sql_scripts/02_insert_sample_data.sql`

### Step 3: Run the Platform (1 minute)

**Windows:**
```bash
# Terminal 1
start_backend.bat

# Terminal 2
start_frontend.bat
```

**Linux/Mac:**
```bash
# Terminal 1
./start_backend.sh

# Terminal 2
./start_frontend.sh
```

## 🌐 Access Your Dashboards

- **Frontend:** http://localhost:8501
- **API Docs:** http://localhost:8000/api/v1/docs
- **Health Check:** http://localhost:8000/health

## 📊 What You Can Do

### Claims Analytics Dashboard
- Track approval and denial rates
- Monitor processing times (TAT)
- Analyze retroactive claims
- Filter by decision types, categories, ongoing rate months
- Export data to CSV

### Policy Analytics Dashboard
- Monitor active policies and lapse rates
- Analyze premium revenue
- Track waiver and forfeiture status
- View geographic distribution
- Export data to CSV

## 📖 Documentation

- **README.md** - Full documentation
- **QUICK_START.md** - Detailed setup guide
- **PROJECT_SUMMARY.md** - Technical details
- **IMPLEMENTATION_COMPLETE.md** - Feature checklist

## ⚙️ Optional: Redis Setup

For better performance, install Redis:

**Docker (Recommended):**
```bash
docker run -d -p 6379:6379 --name redis redis
```

If Redis is not available, the app automatically uses memory cache.

## 🧪 Test with Sample Data

The platform includes sample data:
- 4 policies from different carriers
- 4 claims with various statuses

Use these filters to see the sample data:
- **Carrier Name:** `Acme Insurance Co`
- **Dates:** `2024-10-31`

## 🆘 Need Help?

1. Check `QUICK_START.md` for detailed instructions
2. Review `README.md` for comprehensive documentation
3. Visit http://localhost:8000/api/v1/docs for API documentation
4. Check console logs for error messages

## ✅ Verification Checklist

Before running:
- [ ] Snowflake credentials configured in backend/.env
- [ ] SQL scripts run in Snowflake
- [ ] Redis installed (optional)
- [ ] Python 3.9+ installed
- [ ] Virtual environment activated

## 🎯 What's Included

✅ FastAPI backend with 15+ REST endpoints  
✅ Streamlit frontend with interactive dashboards  
✅ Snowflake integration via Snowpark  
✅ Redis caching (optional)  
✅ Complex business logic implementation  
✅ Sample data for testing  
✅ Complete documentation  
✅ Startup scripts  

## 🚀 You're Ready!

Just run the startup scripts and access http://localhost:8501 to begin exploring your LTC insurance data!

---

**Questions?** Check the documentation files or the API docs.

**Version:** 1.0.0 | **Status:** ✅ Production Ready

