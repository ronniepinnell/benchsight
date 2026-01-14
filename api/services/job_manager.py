"""Job manager for tracking ETL jobs (MVP: in-memory)."""
import uuid
from datetime import datetime
from typing import Dict, Optional
from ..models.job import JobStatus, JobResponse
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class JobManager:
    """Simple in-memory job manager (MVP)."""
    
    def __init__(self):
        """Initialize job manager."""
        self._jobs: Dict[str, JobResponse] = {}
        logger.info("JobManager initialized (in-memory)")
    
    def create_job(self, mode: str, game_ids: Optional[list] = None, options: Optional[dict] = None) -> str:
        """
        Create a new job.
        
        Args:
            mode: ETL mode (full, incremental, single)
            game_ids: Optional list of game IDs
            options: Optional ETL options
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())[:8]
        
        job = JobResponse(
            job_id=job_id,
            status=JobStatus.QUEUED,
            progress=0,
            current_step="Queued",
            created_at=datetime.now()
        )
        
        self._jobs[job_id] = job
        logger.info(f"Created job {job_id} (mode: {mode})")
        return job_id
    
    def get_job(self, job_id: str) -> Optional[JobResponse]:
        """Get job by ID."""
        return self._jobs.get(job_id)
    
    def update_job(
        self,
        job_id: str,
        status: Optional[JobStatus] = None,
        progress: Optional[int] = None,
        current_step: Optional[str] = None,
        tables_created: Optional[int] = None,
        error: Optional[str] = None,
        completed: bool = False
    ) -> bool:
        """
        Update job status.
        
        Returns:
            True if job exists and was updated
        """
        job = self._jobs.get(job_id)
        if not job:
            logger.warning(f"Job {job_id} not found")
            return False
        
        if status:
            job.status = status
        
        if progress is not None:
            job.progress = progress
        
        if current_step:
            job.current_step = current_step
        
        if tables_created is not None:
            job.tables_created = tables_created
        
        if error:
            job.errors.append(error)
            if not job.status == JobStatus.FAILED:
                job.status = JobStatus.FAILED
        
        if completed:
            job.completed_at = datetime.now()
            if not job.status == JobStatus.FAILED:
                job.status = JobStatus.COMPLETED
                job.progress = 100
        
        # Set started_at when status becomes RUNNING
        if status == JobStatus.RUNNING and not job.started_at:
            job.started_at = datetime.now()
        
        logger.debug(f"Updated job {job_id}: status={job.status}, progress={job.progress}%")
        return True
    
    def list_jobs(self, limit: int = 10, status: Optional[JobStatus] = None) -> list[JobResponse]:
        """List recent jobs."""
        jobs = list(self._jobs.values())
        
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        # Sort by created_at (newest first)
        jobs.sort(key=lambda x: x.created_at, reverse=True)
        
        return jobs[:limit]
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job."""
        job = self._jobs.get(job_id)
        if not job:
            return False
        
        if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            return False  # Can't cancel finished jobs
        
        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.now()
        logger.info(f"Cancelled job {job_id}")
        return True


# Global job manager instance
job_manager = JobManager()
