"""
Backend API Client for Mission Control UI

Provides clean interface to FastAPI backend endpoints.
Handles connection errors, retries, and response parsing.

Usage:
    client = APIClient("http://localhost:8000")
    agents = client.list_agents()
    if agents:
        for agent in agents:
            print(agent['name'])
"""

import requests
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Response from an API call"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: int = 200


class APIClient:
    """
    Client for Mission Control backend API.

    Handles all communication with FastAPI backend including:
    - Agent management
    - Optimization workflows
    - System status
    - Error handling and retries
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize API client.

        Args:
            base_url: Base URL of FastAPI backend
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

        logger.info(f"API Client initialized: {self.base_url}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retries: int = 0
    ) -> APIResponse:
        """
        Make HTTP request with error handling and retries.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            retries: Current retry count

        Returns:
            APIResponse with success status and data/error
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )

            # Success
            if response.status_code < 400:
                try:
                    response_data = response.json()
                except Exception:
                    response_data = response.text

                return APIResponse(
                    success=True,
                    data=response_data,
                    status_code=response.status_code
                )

            # Error response from server
            else:
                error_msg = f"API error {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', error_msg)
                except Exception:
                    error_msg = response.text or error_msg

                return APIResponse(
                    success=False,
                    error=error_msg,
                    status_code=response.status_code
                )

        except requests.exceptions.ConnectionError:
            # Backend not available - retry if possible
            if retries < self.max_retries:
                time.sleep(1 * (retries + 1))  # Exponential backoff
                return self._make_request(method, endpoint, data, params, retries + 1)

            return APIResponse(
                success=False,
                error="Cannot connect to backend. Is the server running?",
                status_code=503
            )

        except requests.exceptions.Timeout:
            return APIResponse(
                success=False,
                error=f"Request timed out after {self.timeout} seconds",
                status_code=408
            )

        except Exception as e:
            logger.error(f"Request failed: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                status_code=500
            )

    # ========================================================================
    # System Endpoints
    # ========================================================================

    def health_check(self) -> APIResponse:
        """Check if backend is running and healthy"""
        return self._make_request("GET", "/health")

    def get_system_status(self) -> APIResponse:
        """Get overall system health and status"""
        return self._make_request("GET", "/api/system/status")

    def get_system_metrics(self) -> APIResponse:
        """Get system performance metrics"""
        return self._make_request("GET", "/api/system/metrics")

    # ========================================================================
    # Agent Endpoints
    # ========================================================================

    def list_agents(self) -> APIResponse:
        """List all agents"""
        return self._make_request("GET", "/api/agents")

    def get_agent(self, agent_id: str) -> APIResponse:
        """
        Get details for a specific agent.

        Args:
            agent_id: Agent identifier

        Returns:
            APIResponse with agent details
        """
        return self._make_request("GET", f"/api/agents/{agent_id}")

    def compile_agent(self, agent_id: str) -> APIResponse:
        """
        Compile agent to SuperSpec format.

        Args:
            agent_id: Agent identifier

        Returns:
            APIResponse with compilation result
        """
        return self._make_request("POST", f"/api/agents/{agent_id}/compile")

    def get_agent_status(self, agent_id: str) -> APIResponse:
        """
        Get current status of an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            APIResponse with agent status
        """
        return self._make_request("GET", f"/api/agents/{agent_id}/status")

    # ========================================================================
    # Evaluation Endpoints
    # ========================================================================

    def evaluate_agent(
        self,
        agent_id: str,
        baseline: bool = False
    ) -> APIResponse:
        """
        Run evaluation on an agent.

        Args:
            agent_id: Agent identifier
            baseline: Mark as baseline evaluation

        Returns:
            APIResponse with evaluation results
        """
        return self._make_request(
            "POST",
            f"/api/evaluate/{agent_id}",
            data={"baseline": baseline}
        )

    def get_evaluation_history(self, agent_id: str) -> APIResponse:
        """
        Get evaluation history for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            APIResponse with evaluation history
        """
        return self._make_request("GET", f"/api/evaluate/{agent_id}/history")

    def get_latest_evaluation(self, agent_id: str) -> APIResponse:
        """
        Get latest evaluation results for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            APIResponse with latest evaluation
        """
        return self._make_request("GET", f"/api/evaluate/{agent_id}/latest")

    # ========================================================================
    # Optimization Endpoints
    # ========================================================================

    def start_optimization(
        self,
        agent_id: str,
        optimizer: str = "gepa",
        iterations: int = 10,
        params: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """
        Start optimization for an agent.

        Args:
            agent_id: Agent identifier
            optimizer: Optimization strategy (default: "gepa")
            iterations: Number of iterations
            params: Additional optimization parameters

        Returns:
            APIResponse with optimization job details
        """
        data = {
            "optimizer": optimizer,
            "iterations": iterations,
            "params": params or {}
        }
        return self._make_request("POST", f"/api/optimize/{agent_id}", data=data)

    def get_optimization_status(self, agent_id: str) -> APIResponse:
        """
        Get current optimization status for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            APIResponse with optimization progress
        """
        return self._make_request("GET", f"/api/optimize/{agent_id}/status")

    def get_optimization_history(self, agent_id: str) -> APIResponse:
        """
        Get optimization history for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            APIResponse with optimization history
        """
        return self._make_request("GET", f"/api/optimize/{agent_id}/history")

    def deploy_optimized(self, agent_id: str) -> APIResponse:
        """
        Deploy optimized version of agent.

        Args:
            agent_id: Agent identifier

        Returns:
            APIResponse with deployment result
        """
        return self._make_request("POST", f"/api/optimize/{agent_id}/deploy")

    def rollback_agent(self, agent_id: str) -> APIResponse:
        """
        Rollback agent to baseline version.

        Args:
            agent_id: Agent identifier

        Returns:
            APIResponse with rollback result
        """
        return self._make_request("POST", f"/api/optimize/{agent_id}/rollback")

    # ========================================================================
    # Execution Endpoints
    # ========================================================================

    def execute_agent(
        self,
        agent_id: str,
        inputs: Dict[str, Any]
    ) -> APIResponse:
        """
        Execute an agent with given inputs.

        Args:
            agent_id: Agent identifier
            inputs: Input data for agent execution

        Returns:
            APIResponse with execution results
        """
        return self._make_request(
            "POST",
            f"/api/execute/{agent_id}",
            data=inputs
        )

    def get_execution_history(self, agent_id: str, limit: int = 100) -> APIResponse:
        """
        Get execution history for an agent.

        Args:
            agent_id: Agent identifier
            limit: Maximum number of records to return

        Returns:
            APIResponse with execution history
        """
        return self._make_request(
            "GET",
            f"/api/execute/{agent_id}/history",
            params={"limit": limit}
        )

    # ========================================================================
    # Memory Endpoints
    # ========================================================================

    def get_temporal_memory(self) -> APIResponse:
        """Get temporal memory data"""
        return self._make_request("GET", "/api/memory/temporal")

    def get_hybrid_intelligence(self) -> APIResponse:
        """Get hybrid intelligence data"""
        return self._make_request("GET", "/api/memory/hybrid")

    def sync_memory(self) -> APIResponse:
        """Sync memory from all sources"""
        return self._make_request("POST", "/api/memory/sync")

    def search_memory(self, query: str) -> APIResponse:
        """
        Search across all memory systems.

        Args:
            query: Search query

        Returns:
            APIResponse with search results
        """
        return self._make_request(
            "POST",
            "/api/memory/search",
            data={"query": query}
        )

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def is_connected(self) -> bool:
        """
        Quick check if backend is accessible.

        Returns:
            True if backend is responding, False otherwise
        """
        response = self.health_check()
        return response.success

    def get_backend_info(self) -> Dict[str, Any]:
        """
        Get information about backend connection.

        Returns:
            Dict with backend info
        """
        connected = self.is_connected()
        return {
            "base_url": self.base_url,
            "connected": connected,
            "timeout": self.timeout,
            "max_retries": self.max_retries
        }


# ========================================================================
# Convenience Functions
# ========================================================================

def create_client(base_url: str = "http://localhost:8000") -> APIClient:
    """
    Create an API client instance.

    Args:
        base_url: Base URL of backend

    Returns:
        Configured APIClient
    """
    return APIClient(base_url=base_url)


# ========================================================================
# Module-level test
# ========================================================================

if __name__ == "__main__":
    # Test the client
    print("Testing API Client...")

    client = create_client()
    print(f"\nClient Info: {client.get_backend_info()}")

    print("\nChecking health...")
    health = client.health_check()
    if health.success:
        print("SUCCESS: Backend is running!")
        print(f"Response: {health.data}")
    else:
        print(f"ERROR: {health.error}")
