"""Job models for ETL API."""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job status values."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TriggerETLRequest(BaseModel):
    """Request model for triggering ETL."""
    mode: str = Field(..., description="ETL mode: full, incremental, single, or test")
    game_ids: Optional[List[int]] = Field(None, description="Specific game IDs (for single mode or multiple games)")
    exclude_game_ids: Optional[List[int]] = Field(None, description="Game IDs to exclude from processing")
    source: Optional[str] = Field("excel", description="Data source: 'excel' (local files) or 'supabase' (staging tables)")
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="ETL options: wipe, validate, etc."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "mode": "full",
                "game_ids": [18969, 18977],
                "exclude_game_ids": [99999],
                "source": "excel",
                "options": {
                    "wipe": False,
                    "validate": True
                }
            }
        }


class JobResponse(BaseModel):
    """Response model for job status."""
    job_id: str
    status: JobStatus
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage")
    current_step: Optional[str] = None
    tables_created: Optional[int] = None
    errors: List[str] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "abc123",
                "status": "running",
                "progress": 45,
                "current_step": "Building fact tables",
                "tables_created": 52,
                "errors": [],
                "started_at": "2026-01-13T10:00:00Z",
                "completed_at": None,
                "created_at": "2026-01-13T10:00:00Z"
            }
        }
