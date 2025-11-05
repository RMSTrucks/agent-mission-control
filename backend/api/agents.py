"""
Agent Management API Endpoints

Provides REST API for managing AI agents through SuperOptiX.
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
import logging
import sys
from pathlib import Path

# Add project root to path so we can import integrations
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from integrations.superoptix_client import SuperOptiXClient
from backend.models.requests import CompileRequest, DeployRequest
from backend.models.responses import (
    AgentListResponse,
    AgentStatusResponse,
    CompileResponse,
    DeployResponse,
    HealthCheckResponse,
    ServiceHealth,
    AgentInfo,
    AgentStatus
)

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
            agents = []
            if result.data:
                # If we got JSON data, use it
                agents_data = result.data.get("agents", [])
                agents = [
                    AgentInfo(
                        name=agent.get("name", "unknown"),
                        status=AgentStatus(agent.get("status", "unknown")),
                        description=agent.get("description"),
                        version=agent.get("version"),
                        last_updated=agent.get("last_updated")
                    )
                    for agent in agents_data
                ]
            else:
                # Placeholder agents until SuperOptiX list command is available
                logger.warning("No structured data from list_agents, using placeholder")
                agents = [
                    AgentInfo(
                        name="REMUS",
                        status=AgentStatus.READY,
                        description="RMS Trucks main phone bot",
                        version="1.0.0"
                    ),
                    AgentInfo(
                        name="GENESIS",
                        status=AgentStatus.READY,
                        description="Genesis Trucking phone bot",
                        version="1.0.0"
                    ),
                    AgentInfo(
                        name="SCOUT",
                        status=AgentStatus.READY,
                        description="New agent in development",
                        version="0.1.0"
                    )
                ]

            return AgentListResponse(
                success=True,
                message=f"Found {len(agents)} agents",
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


@router.get("/{agent_name}/status", response_model=AgentStatusResponse)
async def get_agent_status(agent_name: str):
    """
    Get status of a specific agent.

    Args:
        agent_name: Name of the agent

    Returns:
        AgentStatusResponse with agent information
    """
    try:
        # TODO: Implement actual agent status retrieval from SuperOptiX
        # For now, return mock data
        logger.info(f"Getting status for agent: {agent_name}")

        # Mock agent data
        agent = AgentInfo(
            name=agent_name,
            status=AgentStatus.READY,
            description=f"{agent_name} AI agent",
            version="1.0.0",
            last_updated=datetime.now()
        )

        return AgentStatusResponse(
            success=True,
            message=f"Agent {agent_name} status retrieved",
            agent=agent
        )

    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
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

        output_file = None
        if result.success and request.output_dir:
            output_file = f"{request.output_dir}/{request.agent_name}.yaml"

        return CompileResponse(
            success=result.success,
            message=f"Agent {request.agent_name} compiled successfully" if result.success else "Compilation failed",
            agent_name=request.agent_name,
            output_file=output_file,
            output=result.output,
            error=result.error
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error compiling agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/deploy", response_model=DeployResponse)
async def deploy_agent(request: DeployRequest):
    """
    Deploy an agent to a target platform.

    Args:
        request: DeployRequest with agent name and target

    Returns:
        DeployResponse with deployment result
    """
    try:
        client = get_superoptix_client()
        result = client.deploy_agent(request.agent_name, request.target)

        return DeployResponse(
            success=result.success,
            message=f"Agent {request.agent_name} deployed to {request.target}" if result.success else "Deployment failed",
            agent_name=request.agent_name,
            target=request.target or "default",
            deployment_id=f"deploy-{request.agent_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            error=result.error
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deploying agent: {e}")
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

        service = ServiceHealth(
            name="SuperOptiX",
            status="healthy" if health["installed"] else "unhealthy",
            version=health.get("version"),
            details={
                "path": health.get("path"),
                "installed": health["installed"]
            }
        )

        return HealthCheckResponse(
            status="healthy" if health["installed"] else "unhealthy",
            timestamp=datetime.now(),
            version="0.1.0",
            services=[service]
        )

    except Exception as e:
        logger.error(f"Error checking SuperOptiX health: {e}")
        service = ServiceHealth(
            name="SuperOptiX",
            status="unhealthy",
            details={"error": str(e)}
        )
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            version="0.1.0",
            services=[service]
        )
