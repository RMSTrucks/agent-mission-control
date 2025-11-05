"""
VAPI API Client Wrapper

Provides Python interface to VAPI API for phone bot management.
Handles authentication, assistant management, and phone number operations.

VAPI API Documentation: https://docs.vapi.ai/api-reference

Usage:
    from integrations.vapi_client import VAPIClient

    client = VAPIClient(api_key="your_vapi_key")

    # List assistants
    assistants = client.list_assistants()

    # Create assistant
    assistant = client.create_assistant({
        "name": "REMUS",
        "voice": {"provider": "11labs", "voiceId": "..."},
        "model": {"provider": "openai", "model": "gpt-4"}
    })

    # Deploy optimized prompts
    client.deploy_agent(assistant_id, optimized_prompts)
"""

import requests
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class VAPIResponse:
    """Response from a VAPI API call"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: int = 200


class VAPIClient:
    """
    Python wrapper for VAPI API.

    Handles phone bot assistant management, configuration,
    and deployment operations.
    """

    BASE_URL = "https://api.vapi.ai"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize VAPI client.

        Args:
            api_key: VAPI API key (can also be set via VAPI_API_KEY env var)
        """
        import os
        self.api_key = api_key or os.getenv("VAPI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "VAPI API key required. Provide via parameter or VAPI_API_KEY environment variable."
            )

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

        logger.info("VAPI client initialized")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> VAPIResponse:
        """
        Make HTTP request to VAPI API.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters

        Returns:
            VAPIResponse with success status and data/error
        """
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )

            # Success
            if response.status_code < 400:
                try:
                    response_data = response.json()
                except Exception:
                    response_data = response.text

                return VAPIResponse(
                    success=True,
                    data=response_data,
                    status_code=response.status_code
                )

            # Error response
            else:
                error_msg = f"API error {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', error_msg)
                except Exception:
                    error_msg = response.text or error_msg

                return VAPIResponse(
                    success=False,
                    error=error_msg,
                    status_code=response.status_code
                )

        except requests.exceptions.ConnectionError:
            return VAPIResponse(
                success=False,
                error="Cannot connect to VAPI API",
                status_code=503
            )

        except requests.exceptions.Timeout:
            return VAPIResponse(
                success=False,
                error="Request timed out",
                status_code=408
            )

        except Exception as e:
            logger.error(f"Request failed: {e}")
            return VAPIResponse(
                success=False,
                error=str(e),
                status_code=500
            )

    # ========================================================================
    # Assistant Management
    # ========================================================================

    def list_assistants(self, limit: int = 100) -> VAPIResponse:
        """
        List all assistants.

        Args:
            limit: Maximum number of assistants to return

        Returns:
            VAPIResponse with list of assistants
        """
        return self._make_request(
            "GET",
            "/assistant",
            params={"limit": limit}
        )

    def get_assistant(self, assistant_id: str) -> VAPIResponse:
        """
        Get details for a specific assistant.

        Args:
            assistant_id: Assistant ID

        Returns:
            VAPIResponse with assistant details
        """
        return self._make_request("GET", f"/assistant/{assistant_id}")

    def create_assistant(self, config: Dict[str, Any]) -> VAPIResponse:
        """
        Create a new assistant.

        Args:
            config: Assistant configuration
                Required fields:
                - name: Assistant name
                - voice: Voice configuration
                - model: Model configuration
                Optional:
                - firstMessage: Initial greeting
                - systemPrompt: System instructions
                - functions: Available functions

        Returns:
            VAPIResponse with created assistant
        """
        return self._make_request("POST", "/assistant", data=config)

    def update_assistant(
        self,
        assistant_id: str,
        updates: Dict[str, Any]
    ) -> VAPIResponse:
        """
        Update an existing assistant.

        Args:
            assistant_id: Assistant ID
            updates: Fields to update

        Returns:
            VAPIResponse with updated assistant
        """
        return self._make_request(
            "PATCH",
            f"/assistant/{assistant_id}",
            data=updates
        )

    def delete_assistant(self, assistant_id: str) -> VAPIResponse:
        """
        Delete an assistant.

        Args:
            assistant_id: Assistant ID

        Returns:
            VAPIResponse with deletion status
        """
        return self._make_request("DELETE", f"/assistant/{assistant_id}")

    # ========================================================================
    # Deployment Operations
    # ========================================================================

    def deploy_agent(
        self,
        assistant_id: str,
        optimized_prompts: Dict[str, str],
        additional_config: Optional[Dict[str, Any]] = None
    ) -> VAPIResponse:
        """
        Deploy optimized agent prompts to a VAPI assistant.

        Args:
            assistant_id: VAPI assistant ID
            optimized_prompts: Optimized prompt configuration
                Expected keys:
                - systemPrompt: System instructions
                - firstMessage: Initial greeting
            additional_config: Additional configuration updates

        Returns:
            VAPIResponse with deployment result
        """
        updates = {
            "systemPrompt": optimized_prompts.get("systemPrompt", ""),
            "firstMessage": optimized_prompts.get("firstMessage", ""),
        }

        if additional_config:
            updates.update(additional_config)

        return self.update_assistant(assistant_id, updates)

    def rollback_agent(
        self,
        assistant_id: str,
        baseline_prompts: Dict[str, str]
    ) -> VAPIResponse:
        """
        Rollback assistant to baseline configuration.

        Args:
            assistant_id: VAPI assistant ID
            baseline_prompts: Baseline prompt configuration

        Returns:
            VAPIResponse with rollback result
        """
        return self.deploy_agent(assistant_id, baseline_prompts)

    # ========================================================================
    # Phone Number Management
    # ========================================================================

    def list_phone_numbers(self) -> VAPIResponse:
        """
        List all phone numbers.

        Returns:
            VAPIResponse with list of phone numbers
        """
        return self._make_request("GET", "/phone-number")

    def get_phone_number(self, number_id: str) -> VAPIResponse:
        """
        Get details for a specific phone number.

        Args:
            number_id: Phone number ID

        Returns:
            VAPIResponse with phone number details
        """
        return self._make_request("GET", f"/phone-number/{number_id}")

    def buy_phone_number(
        self,
        area_code: Optional[str] = None,
        name: Optional[str] = None
    ) -> VAPIResponse:
        """
        Purchase a new phone number.

        Args:
            area_code: Preferred area code
            name: Friendly name for the number

        Returns:
            VAPIResponse with purchased number details
        """
        data = {}
        if area_code:
            data["areaCode"] = area_code
        if name:
            data["name"] = name

        return self._make_request("POST", "/phone-number", data=data)

    def update_phone_number(
        self,
        number_id: str,
        assistant_id: Optional[str] = None,
        name: Optional[str] = None
    ) -> VAPIResponse:
        """
        Update phone number configuration.

        Args:
            number_id: Phone number ID
            assistant_id: Assistant to assign to this number
            name: Updated friendly name

        Returns:
            VAPIResponse with updated number
        """
        data = {}
        if assistant_id:
            data["assistantId"] = assistant_id
        if name:
            data["name"] = name

        return self._make_request(
            "PATCH",
            f"/phone-number/{number_id}",
            data=data
        )

    # ========================================================================
    # Call Management
    # ========================================================================

    def list_calls(
        self,
        assistant_id: Optional[str] = None,
        limit: int = 100
    ) -> VAPIResponse:
        """
        List call history.

        Args:
            assistant_id: Filter by assistant ID
            limit: Maximum number of calls to return

        Returns:
            VAPIResponse with call history
        """
        params = {"limit": limit}
        if assistant_id:
            params["assistantId"] = assistant_id

        return self._make_request("GET", "/call", params=params)

    def get_call(self, call_id: str) -> VAPIResponse:
        """
        Get details for a specific call.

        Args:
            call_id: Call ID

        Returns:
            VAPIResponse with call details including transcript
        """
        return self._make_request("GET", f"/call/{call_id}")

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def test_connection(self) -> bool:
        """
        Test VAPI API connection.

        Returns:
            True if connected, False otherwise
        """
        result = self.list_assistants(limit=1)
        return result.success

    def get_assistant_by_name(self, name: str) -> VAPIResponse:
        """
        Find assistant by name.

        Args:
            name: Assistant name to search for

        Returns:
            VAPIResponse with assistant or None if not found
        """
        result = self.list_assistants()

        if not result.success:
            return result

        assistants = result.data
        for assistant in assistants:
            if assistant.get("name") == name:
                return VAPIResponse(
                    success=True,
                    data=assistant,
                    status_code=200
                )

        return VAPIResponse(
            success=False,
            error=f"Assistant not found: {name}",
            status_code=404
        )


# ========================================================================
# Convenience Functions
# ========================================================================

def create_vapi_client(api_key: Optional[str] = None) -> VAPIClient:
    """
    Create a VAPI client instance.

    Args:
        api_key: VAPI API key

    Returns:
        Configured VAPIClient
    """
    return VAPIClient(api_key=api_key)


def check_vapi_available(api_key: Optional[str] = None) -> bool:
    """
    Quick check if VAPI is accessible.

    Args:
        api_key: VAPI API key

    Returns:
        True if VAPI is available, False otherwise
    """
    try:
        client = create_vapi_client(api_key)
        return client.test_connection()
    except Exception as e:
        logger.error(f"VAPI check failed: {e}")
        return False


# ========================================================================
# Module-level test
# ========================================================================

if __name__ == "__main__":
    import os

    print("Testing VAPI Client...")

    api_key = os.getenv("VAPI_API_KEY")
    if not api_key:
        print("\nERROR: VAPI_API_KEY environment variable not set")
        print("Set it with: export VAPI_API_KEY=your_key_here")
        exit(1)

    try:
        client = create_vapi_client(api_key)
        print(f"\nClient created successfully")

        print("\nTesting connection...")
        if client.test_connection():
            print("SUCCESS: Connected to VAPI API")

            print("\nListing assistants...")
            result = client.list_assistants(limit=5)
            if result.success:
                print(f"Found {len(result.data)} assistants:")
                for assistant in result.data[:5]:
                    print(f"  - {assistant.get('name')} (ID: {assistant.get('id')})")
            else:
                print(f"ERROR: {result.error}")
        else:
            print("ERROR: Could not connect to VAPI API")

    except Exception as e:
        print(f"\nERROR: {e}")
