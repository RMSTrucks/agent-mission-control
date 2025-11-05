"""
Optimization API Endpoints

Provides REST API for optimizing AI agents using GEPA.
Supports async job tracking for long-running optimizations.
"""

import uuid
import asyncio
from typing import Optional, Dict
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from integrations.superoptix_client import SuperOptiXClient
from backend.models.requests import OptimizeStartRequest, EvaluateRequest
from backend.models.responses import (
    OptimizeStartResponse,
    OptimizeStatusResponse,
    OptimizeResultsResponse,
    EvaluateResponse,
    OptimizationJob,
    OptimizationMetrics,
    EvaluationResult,
    JobStatus
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# SuperOptiX client instance
_superoptix_client: Optional[SuperOptiXClient] = None

# In-memory job store (TODO: Move to database in Phase 4)
_optimization_jobs: Dict[str, OptimizationJob] = {}


def get_superoptix_client() -> SuperOptiXClient:
    """Get or create SuperOptiX client instance"""
    global _superoptix_client
    if _superoptix_client is None:
        try:
            _superoptix_client = SuperOptiXClient()
            logger.info("SuperOptiX client initialized for optimization")
        except Exception as e:
            logger.error(f"Failed to initialize SuperOptiX client: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"SuperOptiX not available: {str(e)}"
            )
    return _superoptix_client


def run_optimization_job(job_id: str, request: OptimizeStartRequest):
    """
    Run optimization job in background.

    Args:
        job_id: Unique job identifier
        request: Optimization request parameters
    """
    try:
        client = get_superoptix_client()
        job = _optimization_jobs[job_id]

        # Update job status
        job.status = JobStatus.RUNNING
        job.progress = 10.0
        job.updated_at = datetime.now()

        logger.info(f"Starting optimization job {job_id} for {request.spec_file}")

        # Run baseline evaluation if requested
        baseline_score = None
        if request.baseline_first:
            logger.info(f"Job {job_id}: Running baseline evaluation...")
            job.progress = 20.0
            job.updated_at = datetime.now()

            baseline_result = client.evaluate(
                spec_file=request.spec_file,
                baseline=True
            )

            if baseline_result.success and baseline_result.data:
                baseline_score = baseline_result.data.get("score", 0.0)
                logger.info(f"Job {job_id}: Baseline score: {baseline_score}")

        # Run optimization
        logger.info(f"Job {job_id}: Running GEPA optimization...")
        job.progress = 40.0
        job.updated_at = datetime.now()

        optimize_result = client.optimize(
            spec_file=request.spec_file,
            iterations=request.iterations,
            strategy=request.strategy
        )

        if optimize_result.success:
            job.progress = 90.0
            job.updated_at = datetime.now()

            # Parse optimization results
            optimized_score = None
            iterations_completed = request.iterations

            if optimize_result.data:
                optimized_score = optimize_result.data.get("score", 0.0)
                iterations_completed = optimize_result.data.get("iterations", request.iterations)

            # Calculate improvement
            improvement = None
            if baseline_score is not None and optimized_score is not None:
                improvement = ((optimized_score - baseline_score) / baseline_score) * 100

            # Update job with results
            job.status = JobStatus.COMPLETED
            job.progress = 100.0
            job.completed_at = datetime.now()
            job.updated_at = datetime.now()
            job.metrics = OptimizationMetrics(
                baseline_score=baseline_score,
                optimized_score=optimized_score,
                improvement=improvement,
                iterations_completed=iterations_completed
            )

            logger.info(f"Job {job_id}: Optimization completed successfully")
            logger.info(f"Job {job_id}: Baseline: {baseline_score}, Optimized: {optimized_score}, Improvement: {improvement}%")

        else:
            # Optimization failed
            job.status = JobStatus.FAILED
            job.error = optimize_result.error or "Optimization failed"
            job.updated_at = datetime.now()
            logger.error(f"Job {job_id}: Optimization failed: {job.error}")

    except Exception as e:
        # Job execution error
        logger.error(f"Job {job_id}: Exception during optimization: {e}")
        job = _optimization_jobs.get(job_id)
        if job:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.updated_at = datetime.now()


# ========================================================================
# Endpoints
# ========================================================================

@router.post("/start", response_model=OptimizeStartResponse)
async def start_optimization(request: OptimizeStartRequest, background_tasks: BackgroundTasks):
    """
    Start an async optimization job.

    Args:
        request: OptimizeStartRequest with optimization parameters
        background_tasks: FastAPI background tasks

    Returns:
        OptimizeStartResponse with job information
    """
    try:
        # Validate SuperOptiX is available
        get_superoptix_client()

        # Create job
        job_id = str(uuid.uuid4())
        now = datetime.now()

        job = OptimizationJob(
            job_id=job_id,
            spec_file=request.spec_file,
            status=JobStatus.PENDING,
            progress=0.0,
            started_at=now,
            updated_at=now
        )

        _optimization_jobs[job_id] = job

        # Schedule background task
        background_tasks.add_task(run_optimization_job, job_id, request)

        logger.info(f"Created optimization job {job_id} for {request.spec_file}")

        return OptimizeStartResponse(
            success=True,
            message=f"Optimization job started: {job_id}",
            job=job
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting optimization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{job_id}/status", response_model=OptimizeStatusResponse)
async def get_optimization_status(job_id: str):
    """
    Get the status of an optimization job.

    Args:
        job_id: Unique job identifier

    Returns:
        OptimizeStatusResponse with current job status
    """
    try:
        job = _optimization_jobs.get(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job not found: {job_id}"
            )

        return OptimizeStatusResponse(
            success=True,
            job=job
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{job_id}/results", response_model=OptimizeResultsResponse)
async def get_optimization_results(job_id: str):
    """
    Get the results of a completed optimization job.

    Args:
        job_id: Unique job identifier

    Returns:
        OptimizeResultsResponse with optimization results
    """
    try:
        job = _optimization_jobs.get(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job not found: {job_id}"
            )

        if job.status != JobStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job not completed. Current status: {job.status}"
            )

        # Build comparison data
        comparison = None
        if job.metrics:
            comparison = {
                "baseline": {
                    "score": job.metrics.baseline_score,
                    "label": "Original Agent"
                },
                "optimized": {
                    "score": job.metrics.optimized_score,
                    "label": "Optimized Agent"
                },
                "improvement": f"+{job.metrics.improvement:.1f}%" if job.metrics.improvement else "N/A"
            }

        # Generate recommendations based on results
        recommendations = []
        if job.metrics and job.metrics.improvement:
            if job.metrics.improvement > 10:
                recommendations.append("Significant improvement detected. Consider deploying optimized version.")
            elif job.metrics.improvement > 5:
                recommendations.append("Moderate improvement. Run additional tests before deployment.")
            elif job.metrics.improvement > 0:
                recommendations.append("Minor improvement. Consider running more optimization iterations.")
            else:
                recommendations.append("No improvement detected. Review baseline scenarios and optimization parameters.")

        return OptimizeResultsResponse(
            success=True,
            message=f"Optimization results for job {job_id}",
            job=job,
            optimized_spec=f"{job.spec_file}.optimized",  # TODO: Return actual path
            comparison=comparison,
            recommendations=recommendations
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/jobs")
async def list_jobs(limit: int = 50, status_filter: Optional[str] = None):
    """
    List all optimization jobs.

    Args:
        limit: Maximum number of jobs to return
        status_filter: Filter by job status (pending, running, completed, failed)

    Returns:
        List of optimization jobs
    """
    try:
        jobs = list(_optimization_jobs.values())

        # Filter by status if requested
        if status_filter:
            jobs = [job for job in jobs if job.status == status_filter]

        # Sort by started_at (most recent first)
        jobs.sort(key=lambda j: j.started_at, reverse=True)

        # Limit results
        jobs = jobs[:limit]

        return {
            "success": True,
            "jobs": jobs,
            "count": len(jobs),
            "total": len(_optimization_jobs)
        }

    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_agent(request: EvaluateRequest):
    """
    Evaluate agent performance without optimization.

    Args:
        request: EvaluateRequest with evaluation parameters

    Returns:
        EvaluateResponse with evaluation results
    """
    try:
        client = get_superoptix_client()

        logger.info(f"Evaluating {request.spec_file}")
        result = client.evaluate(
            spec_file=request.spec_file,
            baseline=request.baseline
        )

        if result.success:
            # Parse evaluation results
            overall_score = 0.0
            scenarios_passed = 0
            scenarios_failed = 0
            pass_rate = 0.0
            metrics = {}

            if result.data:
                overall_score = result.data.get("score", 0.0)
                scenarios_passed = result.data.get("passed", 0)
                scenarios_failed = result.data.get("failed", 0)
                metrics = result.data.get("metrics", {})

                total = scenarios_passed + scenarios_failed
                if total > 0:
                    pass_rate = (scenarios_passed / total) * 100

            evaluation_result = EvaluationResult(
                spec_file=request.spec_file,
                overall_score=overall_score,
                scenarios_passed=scenarios_passed,
                scenarios_failed=scenarios_failed,
                pass_rate=pass_rate,
                is_baseline=request.baseline,
                metrics=metrics
            )

            return EvaluateResponse(
                success=True,
                message=f"Evaluation completed for {request.spec_file}",
                result=evaluation_result
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Evaluation failed: {result.error}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
