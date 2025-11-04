"""Backend API module - REST endpoints for Mission Control"""

from fastapi import APIRouter

# Create main API router
api_router = APIRouter(prefix="/api")

# Import and register sub-routers
from backend.api import agents

# Register agent routes
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
