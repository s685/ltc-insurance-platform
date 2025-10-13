#!/bin/bash

echo "Starting LTC Insurance Platform - Backend"
echo "=========================================="
echo ""

cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please copy env.template to .env and configure your Snowflake credentials."
    echo ""
    exit 1
fi

echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Starting FastAPI backend on http://localhost:8000"
echo "API Documentation: http://localhost:8000/api/v1/docs"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn app.main:app --reload --port 8000

