"""
Optimization API Endpoints

Handles GEPA optimization workflows, progress tracking, and results.
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import List, Dict, Any
from datetime import datetime
import sys
from pathlib import Path
import uuid

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from integrations.superoptix_client import SuperOptiXClient
from backend.models import (
    StartOptimizationRequest,
    OptimizationJobResponse,
    OptimizationResultResponse,
    OptimizationStatusEnum
)

router = APIRouter(prefix="/optimize", tags=["optimize"])

# Initialize SuperOptiX client
try:
    superoptix = SuperOptiXClient()
except Exception as e:
    print(f"WARNING: SuperOptiX client initialization failed: {e}")
    superoptix = None

# In-memory storage for optimization jobs (TODO: move to database)
optimization_jobs: Dict[str, Dict[str, Any]] = {}


async def run_optimization_background(
    job_id: str,
    agent_id: str,
    spec_file: str,
    iterations: int,
    strategy: str,
    params: Dict[str, Any]
):
    """
    Background task to run optimization.

    Updates job status and stores results in optimization_jobs dict.
    """
    try:
        # Update job status to running
        optimization_jobs[job_id]["status"] = OptimizationStatusEnum.RUNNING
        optimization_jobs[job_id]["started_at"] = datetime.now()

        # Run optimization using SuperOptiX
        result = superoptix.optimize(
            spec_file=spec_file,
            iterations=iterations,
            strategy=strategy
        )

        if result.success:
            # Update job with results
            optimization_jobs[job_id]["status"] = OptimizationStatusEnum.COMPLETED
            optimization_jobs[job_id]["completed_at"] = datetime.now()
            optimization_jobs[job_id]["current_iteration"] = iterations

            # Parse results
            data = result.data or {}
            optimization_jobs[job_id]["best_score"] = data.get("best_score", 0.0)
            optimization_jobs[job_id]["baseline_score"] = data.get("baseline_score", 0.0)

            if data.get("baseline_score"):
                improvement = data["best_score"] - data["baseline_score"]
                optimization_jobs[job_id]["improvement_pct"] = improvement

            optimization_jobs[job_id]["iteration_history"] = data.get("history", [])
            optimization_jobs[job_id]["logs"].append(f"Optimization completed successfully")

        else:
            # Optimization failed
            optimization_jobs[job_id]["status"] = OptimizationStatusEnum.FAILED
            optimization_jobs[job_id]["completed_at"] = datetime.now()
            optimization_jobs[job_id]["logs"].append(f"ERROR: {result.error}")

    except Exception as e:
        # Handle errors
        optimization_jobs[job_id]["status"] = OptimizationStatusEnum.FAILED
        optimization_jobs[job_id]["completed_at"] = datetime.now()
        optimization_jobs[job_id]["logs"].append(f"ERROR: {str(e)}")


@router.post("/{agent_id}", response_model=OptimizationJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_optimization(
    agent_id: str,
    request: StartOptimizationRequest,
    background_tasks: BackgroundTasks
):
    """
    Start an optimization job for an agent.

    Args:
        agent_id: Agent identifier
        request: Optimization configuration
        background_tasks: FastAPI background tasks

    Returns:
        Optimization job details with job_id for tracking
    """
    if not superoptix:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SuperOptiX not available"
        )

    try:
        # Generate job ID
        job_id = f"opt_{agent_id}_{uuid.uuid4().hex[:8]}"

        # TODO: Get agent's SuperSpec file from database
        spec_file = f"{agent_id}.yaml"  # Placeholder

        # Create job record
        job = {
            "job_id": job_id,
            "agent_id": agent_id,
            "status": OptimizationStatusEnum.PENDING,
            "optimizer": request.optimizer,
            "iterations": request.iterations,
            "current_iteration": 0,
            "started_at": None,
            "completed_at": None,
            "elapsed_seconds": 0.0,
            "best_score": 0.0,
            "baseline_score": None,
            "improvement_pct": None,
            "iteration_history": [],
            "logs": [f"Optimization job created: {job_id}"]
        }

        optimization_jobs[job_id] = job

        # Start optimization in background
        background_tasks.add_task(
            run_optimization_background,
            job_id=job_id,
            agent_id=agent_id,
            spec_file=spec_file,
            iterations=request.iterations,
            strategy=request.optimizer,
            params=request.params
        )

        # Return job details
        return OptimizationJobResponse(
            job_id=job_id,
            agent_id=agent_id,
            status=OptimizationStatusEnum.PENDING,
            optimizer=request.optimizer,
            iterations=request.iterations,
            current_iteration=0,
            logs=[f"Optimization started in background"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start optimization: {str(e)}"
        )


@router.get("/{agent_id}/status", response_model=OptimizationJobResponse)
async def get_optimization_status(agent_id: str):
    """
    Get status of the latest optimization job for an agent.

    Args:
        agent_id: Agent identifier

    Returns:
        Current optimization job status and progress
    """
    # Find latest job for this agent
    agent_jobs = [
        job for job in optimization_jobs.values()
        if job["agent_id"] == agent_id
    ]

    if not agent_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No optimization jobs found for agent: {agent_id}"
        )

    # Get most recent job
    latest_job = max(agent_jobs, key=lambda j: j.get("started_at") or datetime.min)

    # Calculate elapsed time
    if latest_job["started_at"]:
        elapsed = (datetime.now() - latest_job["started_at"]).total_seconds()
        latest_job["elapsed_seconds"] = elapsed

    return OptimizationJobResponse(**latest_job)


@router.get("/{agent_id}/history", response_model=List[OptimizationJobResponse])
async def get_optimization_history(agent_id: str, limit: int = 10):
    """
    Get optimization history for an agent.

    Args:
        agent_id: Agent identifier
        limit: Maximum number of results

    Returns:
        List of optimization jobs
    """
    # Filter jobs for this agent
    agent_jobs = [
        OptimizationJobResponse(**job)
        for job in optimization_jobs.values()
        if job["agent_id"] == agent_id
    ]

    # Sort by start time (most recent first)
    agent_jobs.sort(
        key=lambda j: j.started_at or datetime.min,
        reverse=True
    )

    return agent_jobs[:limit]


@router.get("/{agent_id}/results", response_model=OptimizationResultResponse)
async def get_optimization_results(agent_id: str):
    """
    Get results of the latest completed optimization.

    Args:
        agent_id: Agent identifier

    Returns:
        Optimization results with comparison metrics
    """
    # Find latest completed job for this agent
    completed_jobs = [
        job for job in optimization_jobs.values()
        if job["agent_id"] == agent_id
        and job["status"] == OptimizationStatusEnum.COMPLETED
    ]

    if not completed_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No completed optimizations found for agent: {agent_id}"
        )

    # Get most recent completed job
    latest_job = max(completed_jobs, key=lambda j: j["completed_at"])

    # Calculate duration
    duration = 0.0
    if latest_job["started_at"] and latest_job["completed_at"]:
        duration = (latest_job["completed_at"] - latest_job["started_at"]).total_seconds() / 60.0

    return OptimizationResultResponse(
        job_id=latest_job["job_id"],
        agent_id=agent_id,
        success=True,
        baseline_score=latest_job.get("baseline_score", 0.0),
        optimized_score=latest_job.get("best_score", 0.0),
        improvement_pct=latest_job.get("improvement_pct", 0.0),
        duration_minutes=duration,
        iterations_completed=latest_job["iterations"],
        best_prompts=None,  # TODO: Store and return optimized prompts
        metrics=None
    )


@router.post("/{agent_id}/deploy")
async def deploy_optimized(agent_id: str):
    """
    Deploy optimized version of agent.

    Args:
        agent_id: Agent identifier

    Returns:
        Deployment status
    """
    # TODO: Implement deployment
    # 1. Get latest optimized version
    # 2. Update VAPI assistant with new prompts
    # 3. Update agent status to 'live'
    # 4. Create deployment record

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Deployment not yet implemented"
    )


@router.post("/{agent_id}/rollback")
async def rollback_agent(agent_id: str):
    """
    Rollback agent to baseline version.

    Args:
        agent_id: Agent identifier

    Returns:
        Rollback status
    """
    # TODO: Implement rollback
    # 1. Get baseline version
    # 2. Update VAPI assistant with baseline prompts
    # 3. Update agent status
    # 4. Create rollback record

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Rollback not yet implemented"
    )
