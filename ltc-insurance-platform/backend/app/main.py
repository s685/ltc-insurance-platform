"""FastAPI main application."""

import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.snowpark_session import session_manager
from app.core.exceptions import AppException
from app.models.schemas import HealthResponse, ErrorResponse
from app.api.routes import policies, claims, analytics

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting LTC Insurance Data Service Platform")
    logger.info(f"Connecting to Snowflake: {settings.snowflake_account}")
    
    # Test database connection
    try:
        session = session_manager.get_session()
        logger.info("Snowflake connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Snowflake: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    session_manager.close_session()


# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="Production-ready data-as-a-service platform for LTC insurance analytics",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle application-specific exceptions."""
    logger.error(f"Application error: {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.message,
            details=exc.details,
            timestamp=datetime.now()
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            details=str(exc) if settings.log_level == "DEBUG" else None,
            timestamp=datetime.now()
        ).model_dump()
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    database_connected = False
    try:
        session = session_manager.get_session()
        session.sql("SELECT 1").collect()
        database_connected = True
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
    
    return HealthResponse(
        status="healthy" if database_connected else "degraded",
        timestamp=datetime.now(),
        database_connected=database_connected,
        cache_enabled=settings.cache_enabled,
        version=settings.version
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "service": settings.project_name,
        "version": settings.version,
        "status": "running",
        "docs": f"{settings.api_prefix}/docs",
        "health": "/health"
    }


# Include routers
app.include_router(policies.router, prefix=settings.api_prefix)
app.include_router(claims.router, prefix=settings.api_prefix)
app.include_router(analytics.router, prefix=settings.api_prefix)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )

