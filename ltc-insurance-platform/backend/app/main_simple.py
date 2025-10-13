"""Simplified FastAPI main application that we know works."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Import routers
from app.api.routes import policies, claims, analytics
from app.config import settings

# Create FastAPI application - minimal config
app = FastAPI(
    title="LTC Insurance Data Service",
    version="1.0.0",
    description="LTC Insurance Analytics Platform"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Simplified for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Root
@app.get("/")
def root():
    """Root endpoint."""
    return {
        "service": "LTC Insurance Data Service",
        "status": "running",
        "docs": "/api/v1/docs"
    }

# Include routers
app.include_router(claims.router, prefix="/api/v1")
app.include_router(policies.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

