"""Upload endpoints for Supabase operations."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from ..models.job import JobResponse, JobStatus
from ..models.upload import UploadRequest, GenerateSchemaRequest
from ..services.job_manager import job_manager
from ..services.upload_service import upload_service
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/to-supabase", response_model=JobResponse, status_code=202)
async def upload_to_supabase(request: UploadRequest, background_tasks: BackgroundTasks):
    """
    Upload tables to Supabase.
    
    Modes:
    - `all`: Upload all tables
    - `dims`: Upload dimension tables only
    - `facts`: Upload fact tables only
    - `qa`: Upload QA/lookup tables only
    - `basic`: Upload basic stats tables only
    - `tracking`: Upload tracking-derived tables only
    """
    # Validate mode
    valid_modes = ["all", "dims", "facts", "qa", "basic", "tracking"]
    if request.mode not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode: {request.mode}. Must be one of {valid_modes}"
        )
    
    # Create job
    job_id = job_manager.create_job(
        mode=f"upload_{request.mode}",
        game_ids=None,
        options=request.options
    )
    
    # Start upload in background
    upload_service.upload_async(
        job_id=job_id,
        tables=request.tables,
        mode=request.mode,
        options=request.options
    )
    
    job = job_manager.get_job(job_id)
    logger.info(f"Triggered upload job {job_id} (mode: {request.mode})")
    return job


@router.post("/generate-schema", response_model=JobResponse, status_code=202)
async def generate_schema(request: GenerateSchemaRequest, background_tasks: BackgroundTasks):
    """
    Generate Supabase schema SQL.
    
    Creates/updates sql/reset_supabase.sql with DROP and CREATE TABLE statements.
    """
    # Create job
    job_id = job_manager.create_job(
        mode="generate_schema",
        game_ids=None,
        options=request.options
    )
    
    # Start schema generation in background
    upload_service.generate_schema_async(job_id)
    
    job = job_manager.get_job(job_id)
    logger.info(f"Triggered schema generation job {job_id}")
    return job


@router.get("/status/{job_id}", response_model=JobResponse)
async def get_upload_status(job_id: str):
    """Get status of an upload job."""
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return job
