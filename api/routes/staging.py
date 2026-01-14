"""Staging endpoints for data ingestion."""
from fastapi import APIRouter, HTTPException
from typing import List
from ..models.staging import (
    UploadBLBTableRequest,
    UploadTrackingRequest,
    UpdateBLBTableRequest
)
from ..services.staging_service import staging_service
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/staging", tags=["staging"])


@router.post("/blb-tables/upload")
async def upload_blb_table(request: UploadBLBTableRequest):
    """
    Upload BLB table data to staging.
    
    This uploads data to staging tables (stage_dim_*, stage_fact_*)
    which can then be processed by ETL.
    
    **Table Names:**
    - `dim_player`, `dim_team`, `dim_league`, `dim_season`, `dim_schedule`
    - `dim_event_type`, `dim_event_detail`, `dim_play_detail`
    - `fact_gameroster`, `fact_leadership`, `fact_registration`, `fact_draft`
    """
    try:
        result = staging_service.upload_blb_table(
            table_name=request.table_name,
            data=request.data,
            replace=request.replace
        )
        logger.info(f"Uploaded {result['rows_uploaded']} rows to {result['staging_table']}")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to upload BLB table: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.put("/blb-tables/update")
async def update_blb_table(request: UpdateBLBTableRequest):
    """
    Update rows in BLB staging table.
    
    Updates rows matching the filter criteria.
    """
    try:
        result = staging_service.update_blb_table(
            table_name=request.table_name,
            filter_column=request.filter_column,
            filter_value=request.filter_value,
            updates=request.updates
        )
        logger.info(f"Updated {result['rows_updated']} rows in {result['staging_table']}")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update BLB table: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@router.get("/blb-tables/list")
async def list_blb_tables():
    """Get list of valid BLB table names."""
    tables = staging_service.get_blb_table_list()
    return {
        "tables": tables,
        "count": len(tables)
    }


@router.post("/tracking/upload")
async def upload_tracking(request: UploadTrackingRequest):
    """
    Upload tracking data (events/shifts) to staging.
    
    Data is uploaded to:
    - `stage_events_tracking` (for events)
    - `stage_shifts_tracking` (for shifts)
    
    This data can then be processed by ETL.
    """
    try:
        result = staging_service.upload_tracking_data(
            game_id=request.game_id,
            events=request.events,
            shifts=request.shifts
        )
        logger.info(f"Uploaded tracking data for game {request.game_id}: {result['events_uploaded']} events, {result['shifts_uploaded']} shifts")
        return result
    except Exception as e:
        logger.error(f"Failed to upload tracking data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/blb-tables/{table_name}/clear")
async def clear_blb_table(table_name: str, confirm: bool = False):
    """
    Clear all data from a BLB staging table.
    
    **Note:** For large tables, use SQL directly: `TRUNCATE TABLE {staging_table} CASCADE;`
    
    Requires `confirm=true` query parameter for safety.
    """
    if not confirm:
        raise HTTPException(status_code=400, detail="Must set confirm=true to clear table")
    
    staging_table = staging_service.BLB_TABLE_MAP.get(table_name)
    if not staging_table:
        raise HTTPException(status_code=404, detail=f"Unknown BLB table: {table_name}")
    
    try:
        # Upload empty data with replace=True (clears table)
        result = staging_service.upload_blb_table(
            table_name=table_name,
            data=[],
            replace=True
        )
        logger.info(f"Cleared table {staging_table}")
        return {
            "table_name": table_name,
            "staging_table": staging_table,
            "cleared": True,
            "message": "Table cleared. Use upload endpoint to add new data."
        }
    except Exception as e:
        logger.error(f"Failed to clear table: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}. Consider using SQL: TRUNCATE TABLE {staging_table} CASCADE;")
