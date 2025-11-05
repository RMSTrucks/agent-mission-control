"""
Testing API Endpoints

Provides REST API for running BDD tests on AI agents.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from integrations.superoptix_client import SuperOptiXClient
from backend.models.requests import TestRunRequest, TestCreateRequest
from backend.models.responses import TestRunResponse, TestCreateResponse, TestScenarioResult

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# SuperOptiX client instance
_superoptix_client: Optional[SuperOptiXClient] = None


def get_superoptix_client() -> SuperOptiXClient:
    """Get or create SuperOptiX client instance"""
    global _superoptix_client
    if _superoptix_client is None:
        try:
            _superoptix_client = SuperOptiXClient()
            logger.info("SuperOptiX client initialized for testing")
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

@router.post("/run", response_model=TestRunResponse)
async def run_tests(request: TestRunRequest):
    """
    Run BDD tests on a SuperSpec file.

    Args:
        request: TestRunRequest with spec file and options

    Returns:
        TestRunResponse with test results
    """
    try:
        client = get_superoptix_client()

        logger.info(f"Running tests on {request.spec_file}")
        result = client.run_tests(
            spec_file=request.spec_file,
            scenario=request.scenario,
            verbose=request.verbose
        )

        if result.success:
            # Parse test results
            scenarios = []
            total_scenarios = 0
            passed = 0
            failed = 0
            pass_rate = 0.0

            if result.data:
                # If we got JSON data, parse it
                total_scenarios = result.data.get("total_scenarios", 0)
                passed = result.data.get("passed", 0)
                failed = result.data.get("failed", 0)

                if total_scenarios > 0:
                    pass_rate = (passed / total_scenarios) * 100

                # Parse individual scenarios
                for scenario in result.data.get("scenarios", []):
                    scenarios.append(TestScenarioResult(
                        name=scenario.get("name", "unknown"),
                        status=scenario.get("status", "unknown"),
                        duration=scenario.get("duration"),
                        steps_passed=scenario.get("steps_passed", 0),
                        steps_failed=scenario.get("steps_failed", 0),
                        error=scenario.get("error")
                    ))
            else:
                # Parse from text output (basic parsing)
                logger.warning("No structured test data, using output text")
                # TODO: Implement text parsing when we know the format
                total_scenarios = 1
                passed = 1 if result.success else 0
                failed = 0 if result.success else 1
                pass_rate = 100.0 if result.success else 0.0

            return TestRunResponse(
                success=True,
                message=f"Tests completed on {request.spec_file}",
                spec_file=request.spec_file,
                total_scenarios=total_scenarios,
                passed=passed,
                failed=failed,
                skipped=0,
                pass_rate=pass_rate,
                scenarios=scenarios,
                output=result.output
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Tests failed: {result.error}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/create", response_model=TestCreateResponse)
async def create_test(request: TestCreateRequest):
    """
    Create a new test scenario.

    Args:
        request: TestCreateRequest with scenario details

    Returns:
        TestCreateResponse with creation result
    """
    try:
        client = get_superoptix_client()

        logger.info(f"Creating test scenario '{request.scenario_name}' in {request.spec_file}")
        result = client.create_test(
            spec_file=request.spec_file,
            scenario_name=request.scenario_name,
            description=request.description
        )

        if result.success:
            return TestCreateResponse(
                success=True,
                message=f"Test scenario '{request.scenario_name}' created successfully",
                spec_file=request.spec_file,
                scenario_name=request.scenario_name
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create test: {result.error}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/scenarios/{spec_file:path}")
async def list_scenarios(spec_file: str):
    """
    List all test scenarios in a spec file.

    Args:
        spec_file: Path to SuperSpec file

    Returns:
        List of test scenarios
    """
    try:
        # TODO: Implement scenario listing when SuperOptiX supports it
        # For now, return placeholder
        return {
            "success": True,
            "spec_file": spec_file,
            "scenarios": [],
            "message": "Scenario listing not yet implemented"
        }

    except Exception as e:
        logger.error(f"Error listing scenarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
