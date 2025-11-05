"""
Request Models for API Endpoints

Pydantic models for validating incoming API requests.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ========================================================================
# Agent Request Models
# ========================================================================

class CompileRequest(BaseModel):
    """Request to compile an agent to SuperSpec format"""
    agent_name: str = Field(..., description="Name of the agent to compile")
    output_dir: Optional[str] = Field(None, description="Optional output directory")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_name": "REMUS",
                "output_dir": "specs/"
            }
        }


class DeployRequest(BaseModel):
    """Request to deploy an agent"""
    agent_name: str = Field(..., description="Name of agent to deploy")
    target: Optional[str] = Field(None, description="Deployment target (e.g., 'vapi', 'vocode')")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_name": "REMUS",
                "target": "vapi"
            }
        }


# ========================================================================
# Test Request Models
# ========================================================================

class TestRunRequest(BaseModel):
    """Request to run BDD tests"""
    spec_file: str = Field(..., description="Path to SuperSpec YAML file")
    scenario: Optional[str] = Field(None, description="Specific scenario to run")
    verbose: bool = Field(False, description="Enable verbose output")
    tags: Optional[List[str]] = Field(None, description="Filter scenarios by tags")

    class Config:
        json_schema_extra = {
            "example": {
                "spec_file": "agents/remus.yaml",
                "scenario": "handle_customer_inquiry",
                "verbose": True,
                "tags": ["critical", "smoke"]
            }
        }


class TestCreateRequest(BaseModel):
    """Request to create a new test scenario"""
    spec_file: str = Field(..., description="Path to SuperSpec file")
    scenario_name: str = Field(..., description="Name of the scenario")
    description: Optional[str] = Field(None, description="Scenario description")
    steps: Optional[List[str]] = Field(None, description="Test steps")

    class Config:
        json_schema_extra = {
            "example": {
                "spec_file": "agents/remus.yaml",
                "scenario_name": "test_price_quote",
                "description": "Test agent's ability to provide accurate price quotes",
                "steps": [
                    "Given a customer asks for a price quote",
                    "When the agent processes the request",
                    "Then it should provide accurate pricing"
                ]
            }
        }


# ========================================================================
# Optimization Request Models
# ========================================================================

class OptimizeStartRequest(BaseModel):
    """Request to start agent optimization"""
    spec_file: str = Field(..., description="Path to SuperSpec YAML file")
    iterations: int = Field(10, ge=1, le=100, description="Number of optimization iterations")
    strategy: str = Field("gepa", description="Optimization strategy")
    auto_level: Optional[str] = Field(None, description="Auto-optimization level (minimal, light, medium, heavy)")
    baseline_first: bool = Field(True, description="Run baseline evaluation before optimization")

    class Config:
        json_schema_extra = {
            "example": {
                "spec_file": "agents/remus.yaml",
                "iterations": 15,
                "strategy": "gepa",
                "auto_level": "medium",
                "baseline_first": True
            }
        }


class OptimizeConfigRequest(BaseModel):
    """Request to configure optimization parameters"""
    population_size: Optional[int] = Field(None, ge=2, le=100, description="GEPA population size")
    mutation_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Mutation rate")
    crossover_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Crossover rate")
    elite_size: Optional[int] = Field(None, ge=1, description="Number of elite individuals")

    class Config:
        json_schema_extra = {
            "example": {
                "population_size": 20,
                "mutation_rate": 0.1,
                "crossover_rate": 0.7,
                "elite_size": 2
            }
        }


# ========================================================================
# Evaluation Request Models
# ========================================================================

class EvaluateRequest(BaseModel):
    """Request to evaluate agent performance"""
    spec_file: str = Field(..., description="Path to SuperSpec file")
    baseline: bool = Field(False, description="Run as baseline evaluation")
    scenarios: Optional[List[str]] = Field(None, description="Specific scenarios to evaluate")

    class Config:
        json_schema_extra = {
            "example": {
                "spec_file": "agents/remus.yaml",
                "baseline": True,
                "scenarios": ["greeting", "price_quote", "schedule_pickup"]
            }
        }
