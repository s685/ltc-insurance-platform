# LTC Insurance Data Service - Startup Process Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup (One-time)](#initial-setup-one-time)
3. [Daily Startup Process](#daily-startup-process)
4. [Troubleshooting](#troubleshooting)
5. [Stopping the Services](#stopping-the-services)

---

## Prerequisites

### Required Software
- ✅ Python 3.9.7 or higher
- ✅ Git (optional, for version control)
- ✅ Snowflake account with credentials
- ✅ Code editor (VS Code, PyCharm, etc.)

### Required Credentials
- Snowflake Account Identifier
- Snowflake Username
- Snowflake Password
- Snowflake Warehouse Name
- Snowflake Database Name
- Snowflake Schema Name

---

## Initial Setup (One-time)

### Step 1: Environment Setup

#### Backend Setup
```powershell
# Navigate to backend directory
cd "backend"

# Verify virtual environment exists
.\venv\Scripts\python.exe --version

# Install/Update dependencies (if needed)
.\venv\Scripts\pip.exe install -r requirements.txt
```

#### Frontend Setup
```powershell
# Navigate to frontend directory
cd "frontend"

# Install dependencies (if needed)
pip install -r requirements.txt
```

### Step 2: Configure Snowflake Credentials

1. **Create .env file** (if not exists):
   ```powershell
   cd backend
   # Copy template if .env doesn't exist
   Copy-Item env.template .env
   ```

2. **Edit the .env file**:
   ```powershell
   notepad backend\.env
   ```

3. **Update these values**:
   ```env
   # Replace with YOUR actual Snowflake credentials
   SNOWFLAKE_ACCOUNT=your_account_identifier
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_WAREHOUSE=COMPUTE_WH
   SNOWFLAKE_DATABASE=LTC_INSURANCE
   SNOWFLAKE_SCHEMA=ANALYTICS
   SNOWFLAKE_ROLE=
   ```

   **Example with real values**:
   ```env
   SNOWFLAKE_ACCOUNT=BNMBCKJ-VI07646
   SNOWFLAKE_USER=VIDYASURESH
   SNOWFLAKE_PASSWORD=YourSecurePassword123
   SNOWFLAKE_WAREHOUSE=COMPUTE_WH
   SNOWFLAKE_DATABASE=LTC_INSURANCE
   SNOWFLAKE_SCHEMA=ANALYTICS
   SNOWFLAKE_ROLE=
   ```

4. **Save and close** the file (Ctrl+S)

### Step 3: Test Snowflake Connection

```powershell
cd backend
.\venv\Scripts\python.exe test_connection.py
```

**Expected output if successful**:
```
============================================================
Testing Snowflake Connection
============================================================

Configuration loaded:
  Account: BNMBCKJ-VI07646
  User: VIDYASURESH
  Warehouse: COMPUTE_WH
  Database: LTC_INSURANCE
  Schema: ANALYTICS

Attempting to connect to Snowflake...

[SUCCESS] Connected to Snowflake!
  Timestamp: 2025-10-12 03:45:23.456
  User: VIDYASURESH
  Session ID: 12345678

[SUCCESS] Database and Schema accessible!

============================================================
Connection test completed successfully!
============================================================
```

---

## Daily Startup Process

### Method 1: Start Both Services (Recommended)

Open **TWO PowerShell windows**:

#### Window 1: Backend Server
```powershell
# Navigate to backend
cd "C:\Users\Admin\OneDrive\Documents\Data Science\backend"

# Start backend API server
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

**Backend will be available at**: http://localhost:8000
- API Documentation: http://localhost:8000/api/v1/docs
- Health Check: http://localhost:8000/health

#### Window 2: Frontend Application
```powershell
# Navigate to project root
cd "C:\Users\Admin\OneDrive\Documents\Data Science"

# Start frontend Streamlit app
streamlit run frontend/streamlit_app.py
```

**Frontend will be available at**: http://localhost:8501

---

### Method 2: Start Services Separately

#### Start Backend Only
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

#### Start Frontend Only
```powershell
cd "C:\Users\Admin\OneDrive\Documents\Data Science"
streamlit run frontend/streamlit_app.py
```

---

## Troubleshooting

### Backend Issues

#### Issue 1: Import Errors / Module Not Found
```powershell
# Clear Python cache
Get-ChildItem -Path backend\app -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force

# Reinstall dependencies
cd backend
.\venv\Scripts\pip.exe install -r requirements.txt --upgrade
```

#### Issue 2: Snowflake Connection Failed
```
Error: 250001 (08001): Incorrect username or password
```

**Solution**:
1. Verify credentials in `backend\.env`
2. Test login at: https://[YOUR_ACCOUNT].snowflakecomputing.com
3. Run connection test: `.\venv\Scripts\python.exe test_connection.py`

```
Error: Role 'ROLE_NAME' not granted to user
```

**Solution**:
1. Open `backend\.env`
2. Set `SNOWFLAKE_ROLE=` (leave empty)
3. Or use a role you have access to (e.g., `PUBLIC`)

```
Error: 404 Not Found: [account].snowflakecomputing.com
```

**Solution**:
1. Verify `SNOWFLAKE_ACCOUNT` format
2. Should be: `accountname.region` (e.g., `abc12345.us-east-1`)
3. Don't include `.snowflakecomputing.com`

#### Issue 3: Port Already in Use
```
Error: [Errno 10048] Only one usage of each socket address
```

**Solution**:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Restart backend
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

### Frontend Issues

#### Issue 1: Cannot Connect to Backend
```
ConnectionError: Cannot connect to backend at http://localhost:8000
```

**Solution**:
1. Ensure backend is running first
2. Check backend is accessible: http://localhost:8000/health
3. Verify API_BASE_URL in frontend config

#### Issue 2: Streamlit Port Already in Use
```powershell
# Streamlit uses port 8501 by default
# Use a different port if needed:
streamlit run frontend/streamlit_app.py --server.port 8502
```

---

## Stopping the Services

### Stop Backend
- Press `Ctrl+C` in the backend PowerShell window
- Or close the PowerShell window

### Stop Frontend
- Press `Ctrl+C` in the frontend PowerShell window
- Or close the Streamlit browser tab and PowerShell window

---

## Quick Command Reference

### Backend Commands
```powershell
# Navigate to backend
cd "C:\Users\Admin\OneDrive\Documents\Data Science\backend"

# Test connection
.\venv\Scripts\python.exe test_connection.py

# Start server
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000

# Install dependencies
.\venv\Scripts\pip.exe install -r requirements.txt

# Clear cache
Get-ChildItem -Path app -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force
```

### Frontend Commands
```powershell
# Navigate to project root
cd "C:\Users\Admin\OneDrive\Documents\Data Science"

# Start Streamlit
streamlit run frontend/streamlit_app.py

# Start on different port
streamlit run frontend/streamlit_app.py --server.port 8502
```

---

## Startup Checklist

### Before Starting
- [ ] Snowflake credentials configured in `backend\.env`
- [ ] Virtual environment activated or using full path to venv executables
- [ ] No other services using ports 8000 (backend) or 8501 (frontend)

### After Starting Backend
- [ ] Backend logs show "Application started"
- [ ] Health check works: http://localhost:8000/health
- [ ] API docs accessible: http://localhost:8000/api/v1/docs

### After Starting Frontend
- [ ] Streamlit opens in browser automatically
- [ ] Dashboard loads without errors
- [ ] Can connect to backend API

---

## Environment Configuration Reference

### Backend (.env)
```env
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=LTC_INSURANCE
SNOWFLAKE_SCHEMA=ANALYTICS
SNOWFLAKE_ROLE=

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1

# Cache Configuration
CACHE_ENABLED=true
CACHE_TTL=300

# Logging
LOG_LEVEL=INFO
LOG_JSON=false

# CORS
CORS_ORIGINS=["http://localhost:8501","http://localhost:3000"]
```

---

## System Requirements

### Minimum
- **OS**: Windows 10 or later
- **Python**: 3.9.7+
- **RAM**: 4GB
- **Storage**: 2GB free space

### Recommended
- **OS**: Windows 10/11
- **Python**: 3.9.7+
- **RAM**: 8GB
- **Storage**: 5GB free space
- **Network**: Stable internet connection for Snowflake

---

## Support & Documentation

### Related Documentation
- `README.md` - Project overview
- `QUICK_START.md` - Quick start guide
- `SETUP_GUIDE.md` - Detailed setup instructions
- `PYTHON39_FIXES.md` - Python 3.9 compatibility notes
- `backend/PYTHON39_FIXES.md` - Backend-specific fixes

### Useful Links
- Backend API Docs: http://localhost:8000/api/v1/docs
- Backend Health: http://localhost:8000/health
- Frontend App: http://localhost:8501
- Snowflake Docs: https://docs.snowflake.com

---

## Version History

- **v1.0** - Initial startup process documentation
- Python 3.9 compatible
- Snowflake integration tested
- Backend and frontend startup procedures documented

---

**Last Updated**: October 12, 2025

