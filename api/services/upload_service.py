"""Upload service for Supabase operations."""
import sys
import subprocess
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any
from ..models.job import JobStatus
from ..services.job_manager import job_manager
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

# Get project root (parent of api/)
PROJECT_ROOT = Path(__file__).parent.parent.parent
UPLOAD_SCRIPT = PROJECT_ROOT / "upload.py"


class UploadService:
    """Service for uploading data to Supabase."""
    
    def __init__(self):
        """Initialize upload service."""
        if not UPLOAD_SCRIPT.exists():
            raise FileNotFoundError(f"Upload script not found: {UPLOAD_SCRIPT}")
        logger.info(f"UploadService initialized (script: {UPLOAD_SCRIPT})")
    
    def generate_schema_async(self, job_id: str) -> None:
        """Generate Supabase schema SQL asynchronously."""
        thread = threading.Thread(
            target=self._generate_schema_sync,
            args=(job_id,),
            daemon=True
        )
        thread.start()
    
    def _generate_schema_sync(self, job_id: str) -> None:
        """Generate schema SQL synchronously."""
        try:
            job_manager.update_job(
                job_id=job_id,
                status=JobStatus.RUNNING,
                progress=0,
                current_step="Generating schema SQL..."
            )
            
            # Import and use SupabaseManager directly
            sys.path.insert(0, str(PROJECT_ROOT))
            from src.supabase.supabase_manager import SupabaseManager
            
            mgr = SupabaseManager()
            result = mgr.reset_schema()
            
            job_manager.update_job(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                progress=100,
                current_step=f"Schema generated: {result['tables_created']} tables",
                completed=True
            )
            
            logger.info(f"Schema generation job {job_id} completed: {result['tables_created']} tables")
        
        except Exception as e:
            job_manager.update_job(
                job_id=job_id,
                status=JobStatus.FAILED,
                progress=50,
                current_step="Schema generation failed",
                error=str(e),
                completed=True
            )
            logger.error(f"Schema generation job {job_id} failed: {e}", exc_info=True)
    
    def upload_async(
        self,
        job_id: str,
        tables: Optional[List[str]] = None,
        mode: str = "all",
        options: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Upload tables to Supabase asynchronously.
        
        Args:
            job_id: Job ID for tracking
            tables: Optional list of specific table names
            mode: Upload mode (all, dims, facts, qa, basic, tracking)
            options: Optional upload options
        """
        options = options or {}
        
        thread = threading.Thread(
            target=self._upload_sync,
            args=(job_id, tables, mode, options),
            daemon=True
        )
        thread.start()
    
    def _upload_sync(
        self,
        job_id: str,
        tables: Optional[List[str]],
        mode: str,
        options: Optional[Dict[str, Any]]
    ) -> None:
        """Upload tables synchronously."""
        options = options or {}
        
        try:
            job_manager.update_job(
                job_id=job_id,
                status=JobStatus.RUNNING,
                progress=0,
                current_step="Starting Supabase upload..."
            )
            
            # Build command
            cmd = [sys.executable, str(UPLOAD_SCRIPT)]
            
            if tables:
                cmd.extend(["--tables"] + tables)
            elif mode == "dims":
                cmd.append("--dims")
            elif mode == "facts":
                cmd.append("--facts")
            elif mode == "qa":
                cmd.append("--qa")
            elif mode == "basic":
                cmd.append("--basic")
            elif mode == "tracking":
                cmd.append("--tracking")
            # else: upload all (no extra args)
            
            # Add cleanup flag if requested
            if options.get("clean", False):
                cmd.append("--clean")
            
            job_manager.update_job(
                job_id=job_id,
                progress=10,
                current_step="Uploading tables to Supabase..."
            )
            
            logger.info(f"Running upload: {' '.join(cmd)}")
            
            # Run upload
            result = subprocess.run(
                cmd,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                job_manager.update_job(
                    job_id=job_id,
                    status=JobStatus.COMPLETED,
                    progress=100,
                    current_step="Upload completed successfully",
                    completed=True
                )
                logger.info(f"Upload job {job_id} completed successfully")
            else:
                error_msg = result.stderr or "Upload failed with unknown error"
                job_manager.update_job(
                    job_id=job_id,
                    status=JobStatus.FAILED,
                    progress=50,
                    current_step="Upload failed",
                    error=error_msg[:500],  # Limit error message length
                    completed=True
                )
                logger.error(f"Upload job {job_id} failed: {error_msg[:200]}")
        
        except subprocess.TimeoutExpired:
            job_manager.update_job(
                job_id=job_id,
                status=JobStatus.FAILED,
                progress=50,
                current_step="Upload timed out",
                error="Upload job exceeded 1 hour timeout",
                completed=True
            )
            logger.error(f"Upload job {job_id} timed out")
        
        except Exception as e:
            job_manager.update_job(
                job_id=job_id,
                status=JobStatus.FAILED,
                progress=0,
                current_step="Upload error",
                error=str(e),
                completed=True
            )
            logger.error(f"Upload job {job_id} error: {e}", exc_info=True)


# Global upload service instance
upload_service = UploadService()
