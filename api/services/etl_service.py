"""ETL service wrapper for running ETL jobs."""
import os
import sys
import subprocess
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from ..models.job import JobStatus
from ..services.job_manager import job_manager
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

# Get project root (parent of api/)
PROJECT_ROOT = Path(__file__).parent.parent.parent


class ETLService:
    """Service for running ETL jobs."""
    
    def __init__(self):
        """Initialize ETL service."""
        self.etl_script = PROJECT_ROOT / "run_etl.py"
        if not self.etl_script.exists():
            raise FileNotFoundError(f"ETL script not found: {self.etl_script}")
        logger.info(f"ETLService initialized (script: {self.etl_script})")
    
    def run_etl_async(
        self,
        job_id: str,
        mode: str,
        game_ids: Optional[List[int]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Run ETL asynchronously in a background thread.
        
        Args:
            job_id: Job ID for tracking
            mode: ETL mode (full, incremental, single)
            game_ids: Optional list of game IDs (for single mode)
            options: Optional ETL options
        """
        options = options or {}
        
        # Update job status to running
        job_manager.update_job(
            job_id=job_id,
            status=JobStatus.RUNNING,
            progress=0,
            current_step="Starting ETL..."
        )
        
        # Run ETL in background thread
        thread = threading.Thread(
            target=self._run_etl_sync,
            args=(job_id, mode, game_ids, options),
            daemon=True
        )
        thread.start()
    
    def _run_etl_sync(
        self,
        job_id: str,
        mode: str,
        game_ids: Optional[List[int]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> None:
        """Run ETL synchronously (called from background thread)."""
        options = options or {}
        
        try:
            # Build command
            cmd = [sys.executable, str(self.etl_script)]
            
            if mode == "full":
                # Full ETL - no extra args needed
                pass
            elif mode == "incremental":
                # Incremental - process only new games (future enhancement)
                logger.warning("Incremental mode not yet implemented, running full ETL")
            # Handle game IDs
            if game_ids:
                if mode == "single":
                    # Single mode requires game_ids
                    cmd.extend(["--games"] + [str(gid) for gid in game_ids])
                else:
                    # Allow multiple games in full/incremental mode too
                    cmd.extend(["--games"] + [str(gid) for gid in game_ids])
            elif mode == "single":
                raise ValueError("game_ids required for single mode")
            
            # Handle exclude games
            exclude_game_ids = options.get("exclude_game_ids") or []
            if exclude_game_ids:
                cmd.extend(["--exclude-games"] + [str(gid) for gid in exclude_game_ids])
            
            # Handle data source (if supabase, set environment variable)
            source = options.get("source", "excel")
            if source == "supabase":
                # Set environment variable to use Supabase source
                os.environ['BENCHSIGHT_SOURCE'] = 'supabase'
                logger.info("Using Supabase staging tables as data source")
            
            if options.get("wipe", False):
                cmd.append("--wipe")
            
            # Update progress
            job_manager.update_job(
                job_id=job_id,
                progress=10,
                current_step="Running ETL pipeline..."
            )
            
            logger.info(f"Running ETL: {' '.join(cmd)}")
            
            # Run ETL
            result = subprocess.run(
                cmd,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            # Check result
            if result.returncode == 0:
                # ETL succeeded
                job_manager.update_job(
                    job_id=job_id,
                    progress=85,
                    current_step="ETL completed successfully"
                )
                
                # Optionally regenerate schema
                if options.get("regenerate_schema", False):
                    logger.info(f"Regenerating schema after ETL for job {job_id}")
                    job_manager.update_job(
                        job_id=job_id,
                        progress=87,
                        current_step="ETL complete, generating schema SQL..."
                    )
                    # Generate schema in new thread
                    from ..services.upload_service import upload_service
                    schema_job_id = job_id + "_schema"
                    upload_service.generate_schema_async(schema_job_id)
                    # Note: Schema generation runs separately, user needs to run SQL manually
                
                # Optionally upload to Supabase
                if options.get("upload_to_supabase", False):
                    logger.info(f"Starting Supabase upload after ETL for job {job_id}")
                    job_manager.update_job(
                        job_id=job_id,
                        progress=95,
                        current_step="ETL complete, starting Supabase upload..."
                    )
                    # Trigger upload in new thread
                    from ..services.upload_service import upload_service
                    upload_service.upload_async(
                        job_id=job_id + "_upload",  # New job ID for upload
                        tables=None,
                        mode="all",
                        options={}
                    )
                    # Keep ETL job as completed, upload has separate job
                    job_manager.update_job(
                        job_id=job_id,
                        status=JobStatus.COMPLETED,
                        progress=100,
                        current_step="ETL completed, upload started",
                        completed=True
                    )
                else:
                    # No upload - mark ETL as complete
                    job_manager.update_job(
                        job_id=job_id,
                        status=JobStatus.COMPLETED,
                        progress=100,
                        current_step="ETL completed successfully",
                        completed=True
                    )
                
                logger.info(f"ETL job {job_id} completed successfully")
            else:
                # Failure
                error_msg = result.stderr or "ETL failed with unknown error"
                job_manager.update_job(
                    job_id=job_id,
                    status=JobStatus.FAILED,
                    progress=50,
                    current_step="ETL failed",
                    error=error_msg,
                    completed=True
                )
                logger.error(f"ETL job {job_id} failed: {error_msg}")
        
        except subprocess.TimeoutExpired:
            job_manager.update_job(
                job_id=job_id,
                status=JobStatus.FAILED,
                progress=50,
                current_step="ETL timed out",
                error="ETL job exceeded 1 hour timeout",
                completed=True
            )
            logger.error(f"ETL job {job_id} timed out")
        
        except Exception as e:
            job_manager.update_job(
                job_id=job_id,
                status=JobStatus.FAILED,
                progress=0,
                current_step="ETL error",
                error=str(e),
                completed=True
            )
            logger.error(f"ETL job {job_id} error: {e}", exc_info=True)


# Global ETL service instance
etl_service = ETLService()
