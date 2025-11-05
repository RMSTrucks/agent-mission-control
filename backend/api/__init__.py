"""Backend API module - REST endpoints for Mission Control"""

from fastapi import APIRouter

# Create main API router
api_router = APIRouter(prefix="/api")

# Import and register sub-routers
from backend.api import agents, tests, optimize

# Register agent routes
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])

# Register testing routes
api_router.include_router(tests.router, prefix="/tests", tags=["tests"])

# Register optimization routes
api_router.include_router(optimize.router, prefix="/optimize", tags=["optimize"])
