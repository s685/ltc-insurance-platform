@echo off
echo Starting LTC Insurance Platform - Frontend
echo ==========================================
echo.

cd frontend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

if not exist .streamlit\secrets.toml (
    echo WARNING: secrets.toml not found!
    echo Please copy .streamlit\secrets.toml.template to .streamlit\secrets.toml
    echo and configure the API_BASE_URL.
    echo.
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -q -r requirements.txt

echo.
echo Starting Streamlit frontend on http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run streamlit_app.py

