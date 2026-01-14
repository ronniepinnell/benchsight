"""Staging models for data ingestion."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class UploadBLBTableRequest(BaseModel):
    """Request model for uploading BLB table to staging."""
    table_name: str = Field(..., description="BLB table name (e.g., 'dim_player', 'dim_team')")
    data: List[Dict[str, Any]] = Field(..., description="Table data as list of records")
    replace: bool = Field(False, description="Replace existing data (default: append)")

    class Config:
        json_schema_extra = {
            "example": {
                "table_name": "dim_player",
                "data": [
                    {"player_id": "P001", "first_name": "John", "last_name": "Doe"},
                    {"player_id": "P002", "first_name": "Jane", "last_name": "Smith"}
                ],
                "replace": False
            }
        }


class UploadTrackingRequest(BaseModel):
    """Request model for uploading tracking data."""
    game_id: int = Field(..., description="Game ID")
    events: Optional[List[Dict[str, Any]]] = Field(None, description="Event data")
    shifts: Optional[List[Dict[str, Any]]] = Field(None, description="Shift data")

    class Config:
        json_schema_extra = {
            "example": {
                "game_id": 18969,
                "events": [
                    {"tracking_event_index": "1", "period": "1", "Type": "Shot", "event_detail": "Wrist"}
                ],
                "shifts": [
                    {"shift_index": "1", "Period": "1", "shift_start_type": "Faceoff"}
                ]
            }
        }


class UpdateBLBTableRequest(BaseModel):
    """Request model for updating BLB table rows."""
    table_name: str = Field(..., description="BLB table name")
    filter_column: str = Field(..., description="Column to filter on (e.g., 'player_id')")
    filter_value: Any = Field(..., description="Filter value")
    updates: Dict[str, Any] = Field(..., description="Fields to update")

    class Config:
        json_schema_extra = {
            "example": {
                "table_name": "dim_player",
                "filter_column": "player_id",
                "filter_value": "P001",
                "updates": {"first_name": "Johnny", "current_skill_rating": 85}
            }
        }
