"""
Testing API Endpoints

Handles BDD test execution and evaluation workflows.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from integrations.superoptix_client import SuperOptiXClient
from backend.models import (
    RunTestsRequest,
    EvaluateAgentRequest,
    TestResultResponse,
    EvaluationResponse
)

router = APIRouter(prefix="/tests", tags=["tests"])

# Initialize SuperOptiX client
try:
    superoptix = SuperOptiXClient()
except Exception as e:
    print(f"WARNING: SuperOptiX client initialization failed: {e}")
    superoptix = None


@router.post("/run", response_model=TestResultResponse)
async def run_tests(request: RunTestsRequest):
    """
    Run BDD tests on a SuperSpec file.

    Args:
        request: Test configuration including spec file and scenario

    Returns:
        Test results with pass/fail statistics
    """
    if not superoptix:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SuperOptiX not available"
        )

    try:
        # Run tests using SuperOptiX
        result = superoptix.run_tests(
            spec_file=request.spec_file,
            scenario=request.scenario,
            verbose=request.verbose
        )

        if result.success:
            # Parse test results
            data = result.data or {}

            total = data.get('total_scenarios', 0)
            passed = data.get('passed', 0)
            failed = data.get('failed', 0)
            pass_rate = (passed / total * 100) if total > 0 else 0.0

            return TestResultResponse(
                success=True,
                spec_file=request.spec_file,
                total_scenarios=total,
                passed=passed,
                failed=failed,
                pass_rate=pass_rate,
                duration_seconds=data.get('duration', 0.0),
                results=data
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Test execution failed: {result.error}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test error: {str(e)}"
        )


@router.post("/evaluate/{agent_id}", response_model=EvaluationResponse)
async def evaluate_agent(agent_id: str, request: EvaluateAgentRequest):
    """
    Run evaluation on an agent.

    Args:
        agent_id: Agent identifier
        request: Evaluation configuration

    Returns:
        Evaluation results with metrics
    """
    if not superoptix:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SuperOptiX not available"
        )

    try:
        # TODO: Get agent's SuperSpec file path from database
        spec_file = f"{agent_id}.yaml"  # Placeholder

        # Run evaluation using SuperOptiX
        result = superoptix.evaluate(
            spec_file=spec_file,
            baseline=request.baseline
        )

        if result.success:
            data = result.data or {}

            # TODO: Save evaluation to database
            evaluation_id = 1  # Placeholder

            return EvaluationResponse(
                evaluation_id=evaluation_id,
                agent_id=agent_id,
                pass_rate=data.get('pass_rate', 0.0),
                avg_confidence=data.get('avg_confidence', 0.0),
                is_baseline=request.baseline,
                is_optimized=False,
                results=data
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Evaluation failed: {result.error}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation error: {str(e)}"
        )


@router.get("/evaluate/{agent_id}/history", response_model=List[EvaluationResponse])
async def get_evaluation_history(agent_id: str, limit: int = 100):
    """
    Get evaluation history for an agent.

    Args:
        agent_id: Agent identifier
        limit: Maximum number of results

    Returns:
        List of evaluation results
    """
    # TODO: Get from database
    return []


@router.get("/evaluate/{agent_id}/latest", response_model=EvaluationResponse)
async def get_latest_evaluation(agent_id: str):
    """
    Get latest evaluation for an agent.

    Args:
        agent_id: Agent identifier

    Returns:
        Latest evaluation result
    """
    # TODO: Get from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No evaluations found for this agent"
    )
