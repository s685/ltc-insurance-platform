"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import Dict

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.routes import analytics, claims, policies
from .config import get_settings
from .core.exceptions import DataServiceError
from .core.snowpark_session import get_session_manager
from .models.schemas import HealthCheckResponse

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if get_settings().log_json else structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler for startup and shutdown."""
    # Startup
    settings = get_settings()
    logger.info(
        "application_starting",
        database=settings.snowflake_database,
        schema=settings.snowflake_schema,
    )

    # Test database connection
    session_manager = get_session_manager()
    health = await session_manager.health_check()
    if health["status"] == "healthy":
        logger.info("database_connection_healthy", health=health)
    else:
        logger.warning("database_connection_unhealthy", health=health)

    yield

    # Shutdown
    logger.info("application_shutting_down")
    await session_manager.close_all()
    logger.info("application_shutdown_complete")


# Create FastAPI application
settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="""
    ## LTC Insurance Data Service API
    
    A production-ready data-as-a-service platform for long-term care insurance analytics.
    
    ### Features
    - **Claims Analytics**: Comprehensive claims statistics and trends
    - **Policy Metrics**: Policy performance and distribution analysis
    - **Custom Queries**: Flexible filtering and aggregation
    - **Real-time Data**: Direct connection to Snowflake data warehouse
    
    ### Architecture
    - Backend: FastAPI with Snowpark
    - Database: Snowflake
    - Caching: In-memory with optional Redis
    - Logging: Structured JSON logging
    """,
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# Global exception handler
@app.exception_handler(DataServiceError)
async def data_service_error_handler(
    request: Request, exc: DataServiceError
) -> JSONResponse:
    """Handle custom data service errors."""
    logger.error(
        "data_service_error",
        error=exc.error_code,
        message=exc.message,
        details=exc.details,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=400,
        content=exc.to_dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors."""
    logger.error(
        "unexpected_error",
        error=str(exc),
        path=request.url.path,
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": {"error_type": type(exc).__name__},
        },
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(
        "request_received",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None,
    )

    response = await call_next(request)

    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )

    return response


# Health check endpoint
@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["health"],
    summary="Health Check",
    description="Check the health status of the API and database connection.",
)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint."""
    session_manager = get_session_manager()
    health = await session_manager.health_check()
    return HealthCheckResponse(**health)


# Include routers
app.include_router(analytics.router, prefix=settings.api_prefix)
app.include_router(claims.router, prefix=settings.api_prefix)
app.include_router(policies.router, prefix=settings.api_prefix)


@app.get("/", tags=["root"])
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {
        "message": "LTC Insurance Data Service API",
        "version": settings.api_version,
        "docs": f"{settings.api_prefix}/docs",
    }

