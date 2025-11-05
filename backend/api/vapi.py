"""
VAPI API Endpoints

Handles VAPI phone bot management, assistant configuration,
and deployment operations.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from integrations.vapi_client import VAPIClient, check_vapi_available

router = APIRouter(prefix="/vapi", tags=["vapi"])

# Initialize VAPI client
vapi_client: Optional[VAPIClient] = None

try:
    vapi_client = VAPIClient()
    print("INFO: VAPI client initialized")
except Exception as e:
    print(f"WARNING: VAPI client initialization failed: {e}")
    print("INFO: Set VAPI_API_KEY environment variable to enable VAPI integration")


# ========================================================================
# Request Models
# ========================================================================

class CreateAssistantRequest(BaseModel):
    """Request to create a VAPI assistant"""
    name: str = Field(..., description="Assistant name")
    voice: Dict[str, Any] = Field(..., description="Voice configuration")
    model: Dict[str, Any] = Field(..., description="Model configuration")
    first_message: Optional[str] = Field(None, description="Initial greeting")
    system_prompt: Optional[str] = Field(None, description="System instructions")
    functions: Optional[List[Dict[str, Any]]] = Field(None, description="Available functions")


class UpdateAssistantRequest(BaseModel):
    """Request to update a VAPI assistant"""
    name: Optional[str] = Field(None, description="Updated name")
    voice: Optional[Dict[str, Any]] = Field(None, description="Updated voice config")
    model: Optional[Dict[str, Any]] = Field(None, description="Updated model config")
    first_message: Optional[str] = Field(None, description="Updated greeting")
    system_prompt: Optional[str] = Field(None, description="Updated instructions")


class DeployAgentRequest(BaseModel):
    """Request to deploy optimized agent to VAPI"""
    assistant_id: str = Field(..., description="VAPI assistant ID")
    system_prompt: str = Field(..., description="Optimized system prompt")
    first_message: Optional[str] = Field(None, description="Optimized first message")
    additional_config: Optional[Dict[str, Any]] = Field(None, description="Additional config")


class AssignPhoneNumberRequest(BaseModel):
    """Request to assign phone number to assistant"""
    assistant_id: str = Field(..., description="Assistant ID")
    name: Optional[str] = Field(None, description="Friendly name")


# ========================================================================
# Helper Functions
# ========================================================================

def ensure_vapi_available():
    """Check if VAPI client is available, raise error if not"""
    if not vapi_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VAPI not configured. Set VAPI_API_KEY environment variable."
        )


# ========================================================================
# Assistant Endpoints
# ========================================================================

@router.get("/assistants")
async def list_assistants(limit: int = 100):
    """
    List all VAPI assistants.

    Args:
        limit: Maximum number of assistants to return

    Returns:
        List of assistants with their configurations
    """
    ensure_vapi_available()

    result = vapi_client.list_assistants(limit=limit)

    if result.success:
        return {
            "success": True,
            "assistants": result.data,
            "count": len(result.data)
        }
    else:
        raise HTTPException(
            status_code=result.status_code,
            detail=result.error
        )


@router.get("/assistants/{assistant_id}")
async def get_assistant(assistant_id: str):
    """
    Get details for a specific assistant.

    Args:
        assistant_id: VAPI assistant ID

    Returns:
        Assistant configuration and status
    """
    ensure_vapi_available()

    result = vapi_client.get_assistant(assistant_id)

    if result.success:
        return {
            "success": True,
            "assistant": result.data
        }
    else:
        raise HTTPException(
            status_code=result.status_code,
            detail=result.error
        )


@router.post("/assistants", status_code=status.HTTP_201_CREATED)
async def create_assistant(request: CreateAssistantRequest):
    """
    Create a new VAPI assistant.

    Args:
        request: Assistant configuration

    Returns:
        Created assistant details
    """
    ensure_vapi_available()

    # Build configuration
    config = {
        "name": request.name,
        "voice": request.voice,
        "model": request.model
    }

    if request.first_message:
        config["firstMessage"] = request.first_message
    if request.system_prompt:
        config["systemPrompt"] = request.system_prompt
    if request.functions:
        config["functions"] = request.functions

    result = vapi_client.create_assistant(config)

    if result.success:
        return {
            "success": True,
            "assistant": result.data,
            "message": "Assistant created successfully"
        }
    else:
        raise HTTPException(
            status_code=result.status_code,
            detail=result.error
        )


@router.patch("/assistants/{assistant_id}")
async def update_assistant(assistant_id: str, request: UpdateAssistantRequest):
    """
    Update an existing VAPI assistant.

    Args:
        assistant_id: VAPI assistant ID
        request: Fields to update

    Returns:
        Updated assistant details
    """
    ensure_vapi_available()

    # Build updates
    updates = {}
    if request.name:
        updates["name"] = request.name
    if request.voice:
        updates["voice"] = request.voice
    if request.model:
        updates["model"] = request.model
    if request.first_message is not None:
        updates["firstMessage"] = request.first_message
    if request.system_prompt is not None:
        updates["systemPrompt"] = request.system_prompt

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    result = vapi_client.update_assistant(assistant_id, updates)

    if result.success:
        return {
            "success": True,
            "assistant": result.data,
            "message": "Assistant updated successfully"
        }
    else:
        raise HTTPException(
            status_code=result.status_code,
            detail=result.error
        )


@router.delete("/assistants/{assistant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assistant(assistant_id: str):
    """
    Delete a VAPI assistant.

    Args:
        assistant_id: VAPI assistant ID
    """
    ensure_vapi_available()

    result = vapi_client.delete_assistant(assistant_id)

    if not result.success:
        raise HTTPException(
            status_code=result.status_code,
            detail=result.error
        )


# ========================================================================
# Deployment Endpoints
# ========================================================================

@router.post("/deploy")
async def deploy_agent(request: DeployAgentRequest):
    """
    Deploy optimized agent to VAPI assistant.

    This updates the assistant's prompts with optimized versions
    from the GEPA optimization process.

    Args:
        request: Deployment configuration with optimized prompts

    Returns:
        Deployment result
    """
    ensure_vapi_available()

    # Build optimized prompts
    optimized_prompts = {
        "systemPrompt": request.system_prompt
    }

    if request.first_message:
        optimized_prompts["firstMessage"] = request.first_message

    # Deploy to VAPI
    result = vapi_client.deploy_agent(
        assistant_id=request.assistant_id,
        optimized_prompts=optimized_prompts,
        additional_config=request.additional_config
    )

    if result.success:
        return {
            "success": True,
            "assistant": result.data,
            "message": f"Agent deployed successfully to assistant {request.assistant_id}"
        }
    else:
        raise HTTPException(
            status_code=result.status_code,
            detail=result.error
        )


@router.post("/deploy/{agent_id}")
async def deploy_agent_by_id(agent_id: str):
    """
    Deploy latest optimized version of an agent to VAPI.

    This is a convenience endpoint that:
    1. Gets the latest optimized prompts for the agent
    2. Finds the corresponding VAPI assistant
    3. Deploys the optimized prompts

    Args:
        agent_id: Agent identifier

    Returns:
        Deployment result
    """
    ensure_vapi_available()

    # TODO: Get latest optimized prompts from database
    # TODO: Get VAPI assistant ID for this agent
    # For now, return not implemented

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Automatic deployment by agent ID not yet implemented. Use /deploy endpoint with explicit assistant_id and prompts."
    )


# ========================================================================
# Phone Number Endpoints
# ========================================================================

@router.get("/phone-numbers")
async def list_phone_numbers():
    """
    List all phone numbers.

    Returns:
        List of phone numbers with their assignments
    """
    ensure_vapi_available()

    result = vapi_client.list_phone_numbers()

    if result.success:
        return {
            "success": True,
            "phone_numbers": result.data,
            "count": len(result.data)
        }
    else:
        raise HTTPException(
            status_code=result.status_code,
            detail=result.error
        )


@router.get("/phone-numbers/{number_id}")
async def get_phone_number(number_id: str):
    """
    Get details for a specific phone number.

    Args:
        number_id: Phone number ID

    Returns:
        Phone number details and assignment
    """
    ensure_vapi_available()

    result = vapi_client.get_phone_number(number_id)

    if result.success:
        return {
            "success": True,
            "phone_number": result.data
        }
    else:
        raise HTTPException(
            status_code=result.status_code,
            detail=result.error
        )


@router.post("/phone-numbers/{number_id}/assign")
async def assign_phone_number(number_id: str, request: AssignPhoneNumberRequest):
    """
    Assign phone number to an assistant.

    Args:
        number_id: Phone number ID
        request: Assignment configuration

    Returns:
        Updated phone number details
    """
    ensure_vapi_available()

    result = vapi_client.update_phone_number(
        number_id=number_id,
        assistant_id=request.assistant_id,
        name=request.name
    )

    if result.success:
        return {
            "success": True,
            "phone_number": result.data,
            "message": f"Phone number assigned to assistant {request.assistant_id}"
        }
    else:
        raise HTTPException(
            status_code=result.status_code,
            detail=result.error
        )


# ========================================================================
# Call History Endpoints
# ========================================================================

@router.get("/calls")
async def list_calls(assistant_id: Optional[str] = None, limit: int = 100):
    """
    List call history.

    Args:
        assistant_id: Filter by assistant ID
        limit: Maximum number of calls

    Returns:
        List of calls with details
    """
    ensure_vapi_available()

    result = vapi_client.list_calls(assistant_id=assistant_id, limit=limit)

    if result.success:
        return {
            "success": True,
            "calls": result.data,
            "count": len(result.data)
        }
    else:
        raise HTTPException(
            status_code=result.status_code,
            detail=result.error
        )


@router.get("/calls/{call_id}")
async def get_call(call_id: str):
    """
    Get details for a specific call including transcript.

    Args:
        call_id: Call ID

    Returns:
        Call details with transcript
    """
    ensure_vapi_available()

    result = vapi_client.get_call(call_id)

    if result.success:
        return {
            "success": True,
            "call": result.data
        }
    else:
        raise HTTPException(
            status_code=result.status_code,
            detail=result.error
        )


# ========================================================================
# Status Endpoints
# ========================================================================

@router.get("/status")
async def get_vapi_status():
    """
    Get VAPI connection status.

    Returns:
        VAPI availability and configuration status
    """
    if not vapi_client:
        return {
            "success": False,
            "connected": False,
            "error": "VAPI not configured. Set VAPI_API_KEY environment variable."
        }

    connected = vapi_client.test_connection()

    return {
        "success": connected,
        "connected": connected,
        "api_url": vapi_client.BASE_URL,
        "message": "VAPI is connected" if connected else "VAPI connection failed"
    }
