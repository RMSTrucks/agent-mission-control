"""
API Models

Pydantic models for request validation and response formatting.
"""

from .requests import (
    CompileAgentRequest,
    RunTestsRequest,
    StartOptimizationRequest,
    EvaluateAgentRequest,
    CreateAgentRequest,
    UpdateAgentRequest,
    ExecuteAgentRequest,
    SearchMemoryRequest
)

from .responses import (
    HealthResponse,
    AgentResponse,
    CompileResponse,
    TestResultResponse,
    EvaluationResponse,
    OptimizationJobResponse,
    OptimizationResultResponse,
    SystemStatusResponse,
    SystemMetricsResponse,
    ErrorResponse,
    StatusEnum,
    OptimizationStatusEnum
)

__all__ = [
    # Requests
    'CompileAgentRequest',
    'RunTestsRequest',
    'StartOptimizationRequest',
    'EvaluateAgentRequest',
    'CreateAgentRequest',
    'UpdateAgentRequest',
    'ExecuteAgentRequest',
    'SearchMemoryRequest',
    # Responses
    'HealthResponse',
    'AgentResponse',
    'CompileResponse',
    'TestResultResponse',
    'EvaluationResponse',
    'OptimizationJobResponse',
    'OptimizationResultResponse',
    'SystemStatusResponse',
    'SystemMetricsResponse',
    'ErrorResponse',
    'StatusEnum',
    'OptimizationStatusEnum',
]
