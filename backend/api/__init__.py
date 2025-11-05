"""
API Routes

FastAPI router modules for different API endpoints.
"""

from .agents import router as agents_router
from .tests import router as tests_router
from .optimize import router as optimize_router

__all__ = ['agents_router', 'tests_router', 'optimize_router']
