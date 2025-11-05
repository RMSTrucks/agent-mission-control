"""
API Response Models

Pydantic models for consistent response formatting.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class StatusEnum(str, Enum):
    """Agent status enumeration"""
    LIVE = "live"
    DEV = "dev"
    OPTIMIZING = "optimizing"
    ERROR = "error"
    UNKNOWN = "unknown"


class OptimizationStatusEnum(str, Enum):
    """Optimization job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    version: str = Field(..., description="API version")


class AgentResponse(BaseModel):
    """Agent details response"""
    id: str = Field(..., description="Agent identifier")
    name: str = Field(..., description="Agent name")
    type: str = Field(..., description="Agent type")
    status: StatusEnum = Field(..., description="Current status")
    description: Optional[str] = Field(None, description="Agent description")
    superspec_path: Optional[str] = Field(None, description="SuperSpec file path")
    vapi_assistant_id: Optional[str] = Field(None, description="VAPI assistant ID")
    success_rate: float = Field(0.0, description="Success rate percentage")
    total_runs: int = Field(0, description="Total execution count")
    avg_latency_ms: float = Field(0.0, description="Average latency in ms")
    last_run: Optional[str] = Field(None, description="Last execution timestamp")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")


class CompileResponse(BaseModel):
    """Agent compilation response"""
    success: bool = Field(..., description="Compilation success status")
    agent_name: str = Field(..., description="Agent name")
    output_path: Optional[str] = Field(None, description="Output file path")
    message: str = Field(..., description="Status message")
    errors: Optional[List[str]] = Field(None, description="Compilation errors")


class TestResultResponse(BaseModel):
    """Test execution response"""
    success: bool = Field(..., description="Test success status")
    spec_file: str = Field(..., description="Tested spec file")
    total_scenarios: int = Field(0, description="Total scenarios")
    passed: int = Field(0, description="Passed scenarios")
    failed: int = Field(0, description="Failed scenarios")
    pass_rate: float = Field(0.0, description="Pass rate percentage")
    duration_seconds: float = Field(0.0, description="Test duration")
    results: Optional[Dict[str, Any]] = Field(None, description="Detailed results")


class EvaluationResponse(BaseModel):
    """Agent evaluation response"""
    evaluation_id: int = Field(..., description="Evaluation ID")
    agent_id: str = Field(..., description="Agent identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Evaluation timestamp")
    pass_rate: float = Field(..., description="Pass rate percentage")
    avg_confidence: float = Field(..., description="Average confidence score")
    is_baseline: bool = Field(False, description="Is baseline evaluation")
    is_optimized: bool = Field(False, description="Is optimized evaluation")
    results: Optional[Dict[str, Any]] = Field(None, description="Detailed results")


class OptimizationJobResponse(BaseModel):
    """Optimization job details"""
    job_id: str = Field(..., description="Job identifier")
    agent_id: str = Field(..., description="Agent being optimized")
    status: OptimizationStatusEnum = Field(..., description="Job status")
    optimizer: str = Field(..., description="Optimization strategy")
    iterations: int = Field(..., description="Total iterations")
    current_iteration: int = Field(0, description="Current iteration")
    started_at: datetime = Field(default_factory=datetime.now, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    elapsed_seconds: float = Field(0.0, description="Elapsed time")
    best_score: float = Field(0.0, description="Best score achieved")
    baseline_score: Optional[float] = Field(None, description="Baseline score")
    improvement_pct: Optional[float] = Field(None, description="Improvement percentage")
    iteration_history: List[float] = Field(default_factory=list, description="Score history")
    logs: List[str] = Field(default_factory=list, description="Job logs")


class OptimizationResultResponse(BaseModel):
    """Optimization results"""
    job_id: str = Field(..., description="Job identifier")
    agent_id: str = Field(..., description="Agent identifier")
    success: bool = Field(..., description="Optimization success")
    baseline_score: float = Field(..., description="Baseline score")
    optimized_score: float = Field(..., description="Optimized score")
    improvement_pct: float = Field(..., description="Improvement percentage")
    duration_minutes: float = Field(..., description="Total duration")
    iterations_completed: int = Field(..., description="Iterations completed")
    best_prompts: Optional[Dict[str, str]] = Field(None, description="Optimized prompts")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Additional metrics")


class SystemStatusResponse(BaseModel):
    """System status response"""
    status: str = Field(..., description="Overall system status")
    backend_online: bool = Field(True, description="Backend availability")
    superoptix_available: bool = Field(..., description="SuperOptiX availability")
    database_connected: bool = Field(..., description="Database connection")
    timestamp: datetime = Field(default_factory=datetime.now, description="Status timestamp")


class SystemMetricsResponse(BaseModel):
    """System metrics response"""
    total_agents: int = Field(0, description="Total agents")
    active_optimizations: int = Field(0, description="Active optimizations")
    evaluations_today: int = Field(0, description="Evaluations today")
    avg_success_rate: float = Field(0.0, description="Average success rate")
    avg_latency_ms: float = Field(0.0, description="Average latency")
    agents_delta: int = Field(0, description="Agent count change")
    opt_delta: int = Field(0, description="Optimization count change")
    eval_delta: int = Field(0, description="Evaluation count change")
    success_rate_delta: float = Field(0.0, description="Success rate change")
    latency_delta: float = Field(0.0, description="Latency change")


class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
