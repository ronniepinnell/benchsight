"""Health check endpoints."""
from fastapi import APIRouter
from datetime import datetime
from pathlib import Path
from ..config import API_VERSION, PROJECT_ROOT
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": API_VERSION,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/status")
async def status():
    """Detailed status endpoint."""
    # Check if ETL script exists
    etl_script = PROJECT_ROOT / "run_etl.py"
    etl_available = etl_script.exists()
    
    # Check if output directory exists
    output_dir = PROJECT_ROOT / "data" / "output"
    output_dir_exists = output_dir.exists()
    
    return {
        "status": "healthy",
        "version": API_VERSION,
        "timestamp": datetime.now().isoformat(),
        "system": {
            "etl_script_available": etl_available,
            "output_directory_exists": output_dir_exists,
            "project_root": str(PROJECT_ROOT)
        }
    }
