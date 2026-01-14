"""Upload models for Supabase operations."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class UploadRequest(BaseModel):
    """Request model for Supabase upload."""
    tables: Optional[List[str]] = Field(None, description="Specific table names to upload")
    mode: str = Field(
        "all",
        description="Upload mode: all, dims, facts, qa, basic, tracking"
    )
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "mode": "all",
                "options": {}
            }
        }


class GenerateSchemaRequest(BaseModel):
    """Request model for schema generation."""
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)
