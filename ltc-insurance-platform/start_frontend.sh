#!/bin/bash

echo "Starting LTC Insurance Platform - Frontend"
echo "=========================================="
echo ""

cd frontend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "WARNING: secrets.toml not found!"
    echo "Please copy .streamlit/secrets.toml.template to .streamlit/secrets.toml"
    echo "and configure the API_BASE_URL."
    echo ""
    exit 1
fi

echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Starting Streamlit frontend on http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run streamlit_app.py

