"""
API Request Models

Pydantic models for request validation and documentation.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class CompileAgentRequest(BaseModel):
    """Request to compile an agent"""
    agent_name: str = Field(..., description="Name of the agent to compile")
    output_dir: Optional[str] = Field(None, description="Output directory for compiled agent")


class RunTestsRequest(BaseModel):
    """Request to run tests on an agent"""
    spec_file: str = Field(..., description="Path to SuperSpec YAML file")
    scenario: Optional[str] = Field(None, description="Specific scenario to run")
    verbose: bool = Field(False, description="Verbose output")


class StartOptimizationRequest(BaseModel):
    """Request to start agent optimization"""
    agent_id: str = Field(..., description="Agent identifier")
    optimizer: str = Field("gepa", description="Optimization strategy (gepa, mipro, grid_search)")
    iterations: int = Field(10, ge=1, le=100, description="Number of optimization iterations")
    params: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional optimization parameters"
    )


class EvaluateAgentRequest(BaseModel):
    """Request to evaluate an agent"""
    agent_id: str = Field(..., description="Agent identifier")
    baseline: bool = Field(False, description="Mark as baseline evaluation")


class CreateAgentRequest(BaseModel):
    """Request to create a new agent"""
    name: str = Field(..., description="Agent name")
    type: str = Field(..., description="Agent type (phone_bot, webhook, standalone)")
    description: Optional[str] = Field(None, description="Agent description")
    superspec_path: Optional[str] = Field(None, description="Path to SuperSpec file")
    vapi_assistant_id: Optional[str] = Field(None, description="VAPI assistant ID")


class UpdateAgentRequest(BaseModel):
    """Request to update an agent"""
    name: Optional[str] = Field(None, description="Updated agent name")
    type: Optional[str] = Field(None, description="Updated agent type")
    description: Optional[str] = Field(None, description="Updated description")
    status: Optional[str] = Field(None, description="Updated status")
    superspec_path: Optional[str] = Field(None, description="Updated SuperSpec path")
    vapi_assistant_id: Optional[str] = Field(None, description="Updated VAPI ID")


class ExecuteAgentRequest(BaseModel):
    """Request to execute an agent"""
    agent_id: str = Field(..., description="Agent identifier")
    inputs: Dict[str, Any] = Field(..., description="Input data for execution")


class SearchMemoryRequest(BaseModel):
    """Request to search memory systems"""
    query: str = Field(..., description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Maximum results")
