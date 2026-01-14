"""ETL endpoints."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from ..models.job import TriggerETLRequest, JobResponse, JobStatus
from ..services.job_manager import job_manager
from ..services.etl_service import etl_service
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/etl", tags=["etl"])


@router.post("/trigger", response_model=JobResponse, status_code=202)
async def trigger_etl(request: TriggerETLRequest, background_tasks: BackgroundTasks):
    """
    Trigger an ETL job.
    
    Modes:
    - `full`: Run full ETL (all games)
    - `incremental`: Run incremental ETL (new games only - not yet implemented)
    - `single`: Run ETL for specific game IDs
    """
    # Validate mode
    if request.mode not in ["full", "incremental", "single", "test"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode: {request.mode}. Must be 'full', 'incremental', 'single', or 'test'"
        )
    
    # Validate single mode
    if request.mode == "single" and not request.game_ids:
        raise HTTPException(
            status_code=400,
            detail="game_ids required for single mode"
        )
    
    # Validate source
    if request.source and request.source not in ["excel", "supabase"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source: {request.source}. Must be 'excel' or 'supabase'"
        )
    
    # Merge all options including source and exclude_game_ids
    options = request.options or {}
    if request.source:
        options["source"] = request.source
    if request.exclude_game_ids:
        options["exclude_game_ids"] = request.exclude_game_ids
    
    # Create job
    job_id = job_manager.create_job(
        mode=request.mode,
        game_ids=request.game_ids,
        options=options
    )
    
    # Start ETL in background
    etl_service.run_etl_async(
        job_id=job_id,
        mode=request.mode,
        game_ids=request.game_ids,
        options=options
    )
    
    # Return job info
    job = job_manager.get_job(job_id)
    logger.info(f"Triggered ETL job {job_id} (mode: {request.mode})")
    return job


@router.get("/status/{job_id}", response_model=JobResponse)
async def get_etl_status(job_id: str):
    """Get status of an ETL job."""
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return job


@router.get("/history", response_model=list[JobResponse])
async def get_etl_history(limit: int = 10, status: Optional[JobStatus] = None):
    """
    Get ETL job history.
    
    Args:
        limit: Maximum number of jobs to return (default: 10)
        status: Filter by status (optional)
    """
    jobs = job_manager.list_jobs(limit=limit, status=status)
    return jobs


@router.post("/cancel/{job_id}", response_model=JobResponse)
async def cancel_etl_job(job_id: str):
    """Cancel a running ETL job."""
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if job.status not in [JobStatus.QUEUED, JobStatus.RUNNING]:
        raise HTTPException(
            status_code=400,
            detail=f"Job {job_id} cannot be cancelled (status: {job.status})"
        )
    
    success = job_manager.cancel_job(job_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to cancel job")
    
    logger.info(f"Cancelled ETL job {job_id}")
    job = job_manager.get_job(job_id)
    return job
