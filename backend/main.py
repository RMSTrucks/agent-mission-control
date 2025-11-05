"""
Agent Mission Control - Backend API

FastAPI application for managing AI agent pipelines.
Provides REST API for agent management, testing, and optimization.

Run with:
    uvicorn main:app --reload
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from backend.core import settings
from backend.api import agents_router, tests_router, optimize_router, vapi_router
from backend.models import (
    HealthResponse,
    SystemStatusResponse,
    SystemMetricsResponse,
    ErrorResponse
)
from integrations.superoptix_client import check_superoptix_installed
from integrations.vapi_client import check_vapi_available

# ========================================================================
# FastAPI Application
# ========================================================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Agent Pipeline Management System",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ========================================================================
# CORS Middleware
# ========================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================================================
# Exception Handlers
# ========================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTPException",
            message=exc.detail,
            detail=str(exc)
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            detail=str(exc)
        ).model_dump()
    )

# ========================================================================
# Root & Health Endpoints
# ========================================================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "online",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns basic health status and API version.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.app_version
    )

# ========================================================================
# System Endpoints
# ========================================================================

@app.get("/api/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """
    Get overall system status.

    Checks availability of SuperOptiX and database connectivity.
    """
    # Check SuperOptiX
    superoptix_available = check_superoptix_installed()

    # TODO: Check database connection
    database_connected = True  # Placeholder

    overall_status = "healthy" if superoptix_available and database_connected else "degraded"

    return SystemStatusResponse(
        status=overall_status,
        backend_online=True,
        superoptix_available=superoptix_available,
        database_connected=database_connected,
        timestamp=datetime.now()
    )


@app.get("/api/system/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics():
    """
    Get system performance metrics.

    Returns aggregated metrics across all agents and operations.
    """
    # TODO: Get actual metrics from database
    # For now, return placeholder data

    return SystemMetricsResponse(
        total_agents=0,
        active_optimizations=0,
        evaluations_today=0,
        avg_success_rate=0.0,
        avg_latency_ms=0.0,
        agents_delta=0,
        opt_delta=0,
        eval_delta=0,
        success_rate_delta=0.0,
        latency_delta=0.0
    )

# ========================================================================
# Include API Routers
# ========================================================================

app.include_router(agents_router, prefix="/api")
app.include_router(tests_router, prefix="/api")
app.include_router(optimize_router, prefix="/api")
app.include_router(vapi_router, prefix="/api")

# ========================================================================
# Startup & Shutdown Events
# ========================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Debug mode: {settings.debug}")
    print(f"CORS origins: {settings.cors_origins}")

    # Check SuperOptiX availability
    if check_superoptix_installed():
        print("SUCCESS: SuperOptiX is available")
    else:
        print("WARNING: SuperOptiX is not installed or not working")

    # Check VAPI availability
    if check_vapi_available():
        print("SUCCESS: VAPI is connected")
    else:
        print("WARNING: VAPI is not configured (set VAPI_API_KEY environment variable)")

    # TODO: Initialize database
    # TODO: Connect to Redis (for Celery)
    # TODO: Check Close CRM connection


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    print(f"Shutting down {settings.app_name}")

    # TODO: Close database connections
    # TODO: Close Redis connections
    # TODO: Cleanup background tasks

# ========================================================================
# Development Server
# ========================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
