"""
Agent Mission Control - FastAPI Backend Server

Main entry point for the API server.
Provides REST API for managing AI agents, pipelines, and integrations.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.config import get_settings
from backend.api import api_router

# Load configuration
settings = get_settings()

# ========================================================================
# Logging Configuration
# ========================================================================

# Remove default logger
logger.remove()

# Add console logger with color
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.logging.level,
    colorize=True
)

# Add file logger (JSON format for production)
log_dir = Path(settings.logging.path)
log_dir.mkdir(parents=True, exist_ok=True)

logger.add(
    log_dir / "api_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.logging.level,
    rotation=settings.logging.rotation,
    retention=settings.logging.retention,
    compression="zip"
)

logger.info(f"Starting {settings.system.name} v{settings.system.version}")
logger.info(f"Environment: {settings.system.environment}")
logger.info(f"API Server: {settings.api.host}:{settings.api.port}")

# ========================================================================
# FastAPI Application
# ========================================================================

app = FastAPI(
    title=settings.system.name,
    description="API for managing AI agents, pipelines, and integrations",
    version=settings.system.version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ========================================================================
# CORS Middleware
# ========================================================================

# Allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit default
        "http://localhost:3000",  # React default
        "http://127.0.0.1:8501",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================================================
# Request/Response Logging Middleware
# ========================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses"""
    start_time = datetime.now()

    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")

    try:
        response = await call_next(request)

        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()

        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Duration: {duration:.3f}s"
        )

        return response

    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path} - Error: {e}")
        raise


# ========================================================================
# Error Handlers
# ========================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.system.environment == "development" else None
        }
    )


# ========================================================================
# Root Endpoints
# ========================================================================

@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint - API information"""
    return {
        "name": settings.system.name,
        "version": settings.system.version,
        "environment": settings.system.environment,
        "status": "running",
        "docs_url": "/docs",
        "api_prefix": "/api"
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.system.version,
        "environment": settings.system.environment
    }


@app.get("/version")
async def version() -> Dict[str, Any]:
    """Version information endpoint"""
    return {
        "version": settings.system.version,
        "name": settings.system.name,
        "api_version": "v1"
    }


# ========================================================================
# API Routes
# ========================================================================

# Include all API routers
app.include_router(api_router)

logger.info("API routes registered:")
for route in app.routes:
    if hasattr(route, "methods"):
        methods = ",".join(route.methods)
        logger.info(f"  {methods: <10} {route.path}")


# ========================================================================
# Startup/Shutdown Events
# ========================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("=" * 60)
    logger.info(f"{settings.system.name} Backend Server Starting")
    logger.info("=" * 60)
    logger.info(f"Version: {settings.system.version}")
    logger.info(f"Environment: {settings.system.environment}")
    logger.info(f"Listening on: {settings.api.host}:{settings.api.port}")
    logger.info(f"Docs available at: http://{settings.api.host}:{settings.api.port}/docs")
    logger.info("=" * 60)

    # Check integrations
    logger.info("Checking integrations...")
    logger.info(f"  SuperOptiX: {'enabled' if settings.superoptix.enabled else 'disabled'}")
    logger.info(f"  VAPI: {'enabled' if settings.vapi.enabled else 'disabled'}")
    logger.info(f"  Close CRM: {'enabled' if settings.close.enabled else 'disabled'}")
    logger.info(f"  Memory (Temporal): {'enabled' if settings.memory.temporal_enabled else 'disabled'}")
    logger.info(f"  Memory (Hybrid): {'enabled' if settings.memory.hybrid_enabled else 'disabled'}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("=" * 60)
    logger.info(f"{settings.system.name} Backend Server Shutting Down")
    logger.info("=" * 60)


# ========================================================================
# Main Entry Point
# ========================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.reload,
        log_level=settings.api.log_level.lower()
    )
