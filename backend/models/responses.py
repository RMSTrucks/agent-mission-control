"""
Response Models for API Endpoints

Pydantic models for API responses with proper typing and documentation.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


# ========================================================================
# Enums
# ========================================================================

class JobStatus(str, Enum):
    """Status of an async job"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentStatus(str, Enum):
    """Status of an agent"""
    READY = "ready"
    COMPILING = "compiling"
    TESTING = "testing"
    OPTIMIZING = "optimizing"
    DEPLOYING = "deploying"
    ERROR = "error"
    UNKNOWN = "unknown"


# ========================================================================
# Base Response Models
# ========================================================================

class BaseResponse(BaseModel):
    """Base response model for all API responses"""
    success: bool = Field(..., description="Whether the operation succeeded")
    message: Optional[str] = Field(None, description="Human-readable message")
    error: Optional[str] = Field(None, description="Error message if failed")


# ========================================================================
# Agent Response Models
# ========================================================================

class AgentInfo(BaseModel):
    """Information about an AI agent"""
    name: str = Field(..., description="Agent name")
    status: AgentStatus = Field(..., description="Current agent status")
    description: Optional[str] = Field(None, description="Agent description")
    version: Optional[str] = Field(None, description="Agent version")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Performance metrics")


class AgentListResponse(BaseResponse):
    """Response for listing agents"""
    agents: List[AgentInfo] = Field(default_factory=list, description="List of agents")
    count: int = Field(..., description="Total number of agents")


class AgentStatusResponse(BaseResponse):
    """Response for agent status check"""
    agent: AgentInfo = Field(..., description="Agent information")


class CompileResponse(BaseResponse):
    """Response from agent compilation"""
    agent_name: str = Field(..., description="Name of compiled agent")
    output_file: Optional[str] = Field(None, description="Path to generated SuperSpec file")
    output: str = Field("", description="Compilation output")


class DeployResponse(BaseResponse):
    """Response from agent deployment"""
    agent_name: str = Field(..., description="Name of deployed agent")
    target: str = Field(..., description="Deployment target")
    deployment_id: Optional[str] = Field(None, description="Deployment identifier")


# ========================================================================
# Test Response Models
# ========================================================================

class TestScenarioResult(BaseModel):
    """Result of a single test scenario"""
    name: str = Field(..., description="Scenario name")
    status: str = Field(..., description="Pass/Fail status")
    duration: Optional[float] = Field(None, description="Execution time in seconds")
    steps_passed: int = Field(0, description="Number of steps passed")
    steps_failed: int = Field(0, description="Number of steps failed")
    error: Optional[str] = Field(None, description="Error message if failed")


class TestRunResponse(BaseResponse):
    """Response from test execution"""
    spec_file: str = Field(..., description="Tested spec file")
    total_scenarios: int = Field(0, description="Total scenarios run")
    passed: int = Field(0, description="Number of scenarios passed")
    failed: int = Field(0, description="Number of scenarios failed")
    skipped: int = Field(0, description="Number of scenarios skipped")
    pass_rate: float = Field(0.0, description="Pass rate percentage")
    duration: Optional[float] = Field(None, description="Total execution time")
    scenarios: List[TestScenarioResult] = Field(default_factory=list, description="Individual scenario results")
    output: Optional[str] = Field(None, description="Full test output")


class TestCreateResponse(BaseResponse):
    """Response from test scenario creation"""
    spec_file: str = Field(..., description="Spec file path")
    scenario_name: str = Field(..., description="Created scenario name")


# ========================================================================
# Optimization Response Models
# ========================================================================

class OptimizationMetrics(BaseModel):
    """Metrics from optimization run"""
    baseline_score: Optional[float] = Field(None, description="Baseline evaluation score")
    optimized_score: Optional[float] = Field(None, description="Optimized evaluation score")
    improvement: Optional[float] = Field(None, description="Improvement percentage")
    iterations_completed: int = Field(0, description="Iterations completed")
    best_generation: Optional[int] = Field(None, description="Generation with best result")


class OptimizationJob(BaseModel):
    """Information about an optimization job"""
    job_id: str = Field(..., description="Unique job identifier")
    spec_file: str = Field(..., description="Spec file being optimized")
    status: JobStatus = Field(..., description="Current job status")
    progress: float = Field(0.0, ge=0.0, le=100.0, description="Progress percentage")
    started_at: datetime = Field(..., description="Job start time")
    updated_at: datetime = Field(..., description="Last update time")
    completed_at: Optional[datetime] = Field(None, description="Job completion time")
    metrics: Optional[OptimizationMetrics] = Field(None, description="Optimization metrics")
    error: Optional[str] = Field(None, description="Error message if failed")


class OptimizeStartResponse(BaseResponse):
    """Response from starting optimization"""
    job: OptimizationJob = Field(..., description="Created optimization job")


class OptimizeStatusResponse(BaseResponse):
    """Response for optimization status check"""
    job: OptimizationJob = Field(..., description="Current job status")


class OptimizeResultsResponse(BaseResponse):
    """Response with optimization results"""
    job: OptimizationJob = Field(..., description="Completed job information")
    optimized_spec: Optional[str] = Field(None, description="Path to optimized spec file")
    comparison: Optional[Dict[str, Any]] = Field(None, description="Before/after comparison")
    recommendations: Optional[List[str]] = Field(None, description="Optimization recommendations")


# ========================================================================
# Evaluation Response Models
# ========================================================================

class EvaluationResult(BaseModel):
    """Result from agent evaluation"""
    spec_file: str = Field(..., description="Evaluated spec file")
    overall_score: float = Field(..., description="Overall evaluation score")
    scenarios_passed: int = Field(0, description="Scenarios passed")
    scenarios_failed: int = Field(0, description="Scenarios failed")
    pass_rate: float = Field(0.0, description="Pass rate percentage")
    is_baseline: bool = Field(False, description="Whether this is a baseline eval")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Detailed metrics")


class EvaluateResponse(BaseResponse):
    """Response from evaluation"""
    result: EvaluationResult = Field(..., description="Evaluation result")


# ========================================================================
# Health Check Response Models
# ========================================================================

class ServiceHealth(BaseModel):
    """Health status of a service"""
    name: str = Field(..., description="Service name")
    status: str = Field(..., description="Service status (healthy/unhealthy)")
    version: Optional[str] = Field(None, description="Service version")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


class HealthCheckResponse(BaseModel):
    """Response from health check"""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="API version")
    services: List[ServiceHealth] = Field(default_factory=list, description="Individual service health")
