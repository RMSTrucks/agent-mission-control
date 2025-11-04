"""
Agent Management API Endpoints

Provides REST API for managing AI agents through SuperOptiX.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging
import sys
from pathlib import Path

# Add project root to path so we can import integrations
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from integrations.superoptix_client import SuperOptiXClient, CommandResult

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize SuperOptiX client (will be lazy-loaded)
_superoptix_client: Optional[SuperOptiXClient] = None


def get_superoptix_client() -> SuperOptiXClient:
    """Get or create SuperOptiX client instance"""
    global _superoptix_client
    if _superoptix_client is None:
        try:
            _superoptix_client = SuperOptiXClient()
            logger.info("SuperOptiX client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SuperOptiX client: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"SuperOptiX not available: {str(e)}"
            )
    return _superoptix_client


# ========================================================================
# Request/Response Models
# ========================================================================

class AgentInfo(BaseModel):
    """Information about an AI agent"""
    name: str
    status: str
    description: Optional[str] = None


class AgentListResponse(BaseModel):
    """Response for listing agents"""
    success: bool
    agents: List[AgentInfo]
    count: int


class CompileRequest(BaseModel):
    """Request to compile an agent"""
    agent_name: str
    output_dir: Optional[str] = None


class CompileResponse(BaseModel):
    """Response from agent compilation"""
    success: bool
    agent_name: str
    output: str
    error: Optional[str] = None


class OptimizeRequest(BaseModel):
    """Request to optimize an agent"""
    spec_file: str
    iterations: int = 10
    strategy: str = "gepa"


class OptimizeResponse(BaseModel):
    """Response from agent optimization"""
    success: bool
    output: str
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class TestRequest(BaseModel):
    """Request to run tests"""
    spec_file: str
    scenario: Optional[str] = None
    verbose: bool = False


class TestResponse(BaseModel):
    """Response from test execution"""
    success: bool
    output: str
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class HealthCheckResponse(BaseModel):
    """Response from SuperOptiX health check"""
    installed: bool
    version: Optional[str] = None
    path: Optional[str] = None
    error: Optional[str] = None


# ========================================================================
# Endpoints
# ========================================================================

@router.get("/list", response_model=AgentListResponse)
async def list_agents():
    """
    List all available agents.

    Returns:
        AgentListResponse with list of agents
    """
    try:
        client = get_superoptix_client()
        result = client.list_agents()

        if result.success:
            # Parse agent list from output
            # For now, return a simple response
            # TODO: Parse actual agent data when SuperOptiX list command is available
            agents = []
            if result.data:
                # If we got JSON data, use it
                agents_data = result.data.get("agents", [])
                agents = [
                    AgentInfo(
                        name=agent.get("name", "unknown"),
                        status=agent.get("status", "unknown"),
                        description=agent.get("description")
                    )
                    for agent in agents_data
                ]
            else:
                # Parse from text output
                # This is a placeholder until we know the actual format
                logger.warning("No structured data from list_agents, using placeholder")
                agents = [
                    AgentInfo(
                        name="REMUS",
                        status="ready",
                        description="RMS Trucks main phone bot"
                    ),
                    AgentInfo(
                        name="GENESIS",
                        status="ready",
                        description="Genesis Trucking phone bot"
                    ),
                    AgentInfo(
                        name="SCOUT",
                        status="development",
                        description="New agent in development"
                    )
                ]

            return AgentListResponse(
                success=True,
                agents=agents,
                count=len(agents)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list agents: {result.error}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/compile", response_model=CompileResponse)
async def compile_agent(request: CompileRequest):
    """
    Compile an agent to SuperSpec format.

    Args:
        request: CompileRequest with agent name

    Returns:
        CompileResponse with compilation result
    """
    try:
        client = get_superoptix_client()
        result = client.compile_agent(request.agent_name, request.output_dir)

        return CompileResponse(
            success=result.success,
            agent_name=request.agent_name,
            output=result.output,
            error=result.error
        )

    except Exception as e:
        logger.error(f"Error compiling agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_agent(request: OptimizeRequest):
    """
    Optimize an agent using GEPA.

    Args:
        request: OptimizeRequest with spec file and options

    Returns:
        OptimizeResponse with optimization results
    """
    try:
        client = get_superoptix_client()
        result = client.optimize(
            spec_file=request.spec_file,
            iterations=request.iterations,
            strategy=request.strategy
        )

        return OptimizeResponse(
            success=result.success,
            output=result.output,
            error=result.error,
            data=result.data
        )

    except Exception as e:
        logger.error(f"Error optimizing agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/test", response_model=TestResponse)
async def test_agent(request: TestRequest):
    """
    Run BDD tests on an agent.

    Args:
        request: TestRequest with spec file and options

    Returns:
        TestResponse with test results
    """
    try:
        client = get_superoptix_client()
        result = client.run_tests(
            spec_file=request.spec_file,
            scenario=request.scenario,
            verbose=request.verbose
        )

        return TestResponse(
            success=result.success,
            output=result.output,
            error=result.error,
            data=result.data
        )

    except Exception as e:
        logger.error(f"Error testing agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/health", response_model=HealthCheckResponse)
async def check_superoptix_health():
    """
    Check SuperOptiX installation and health.

    Returns:
        HealthCheckResponse with installation status
    """
    try:
        client = get_superoptix_client()
        health = client.check_installation()

        return HealthCheckResponse(
            installed=health["installed"],
            version=health.get("version"),
            path=health.get("path"),
            error=health.get("error")
        )

    except Exception as e:
        logger.error(f"Error checking SuperOptiX health: {e}")
        return HealthCheckResponse(
            installed=False,
            error=str(e)
        )
