@echo off
echo Starting LTC Insurance Platform - Backend
echo ==========================================
echo.

cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

if not exist .env (
    echo WARNING: .env file not found!
    echo Please copy env.template to .env and configure your Snowflake credentials.
    echo.
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -q -r requirements.txt

echo.
echo Starting FastAPI backend on http://localhost:8000
echo API Documentation: http://localhost:8000/api/v1/docs
echo Health Check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app.main:app --reload --port 8000

