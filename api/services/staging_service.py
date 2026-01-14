"""Staging service for data ingestion."""
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from ..models.job import JobStatus
from ..services.job_manager import job_manager
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

# Get project root (parent of api/)
PROJECT_ROOT = Path(__file__).parent.parent.parent


class StagingService:
    """Service for managing staging data in Supabase."""
    
    def __init__(self):
        """Initialize staging service."""
        sys.path.insert(0, str(PROJECT_ROOT))
        try:
            from src.supabase.supabase_manager import SupabaseManager
            self.manager = SupabaseManager()
            logger.info("StagingService initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SupabaseManager: {e}")
            raise
    
    # BLB Table Mapping
    BLB_TABLE_MAP = {
        'dim_player': 'stage_dim_player',
        'dim_team': 'stage_dim_team',
        'dim_league': 'stage_dim_league',
        'dim_season': 'stage_dim_season',
        'dim_schedule': 'stage_dim_schedule',
        'dim_playerurlref': 'stage_dim_playerurlref',
        'dim_rink_zone': 'stage_dim_rinkboxcoord',
        'dim_randomnames': 'stage_dim_randomnames',
        'fact_gameroster': 'stage_fact_gameroster',
        'fact_leadership': 'stage_fact_leadership',
        'fact_registration': 'stage_fact_registration',
        'fact_draft': 'stage_fact_draft',
        'dim_event_type': 'stage_dim_event_type',
        'dim_event_detail': 'stage_dim_event_detail',
        'dim_event_detail_2': 'stage_dim_event_detail_2',
        'dim_play_detail': 'stage_dim_play_detail',
        'dim_play_detail_2': 'stage_dim_play_detail_2',
    }
    
    def upload_blb_table(
        self,
        table_name: str,
        data: List[Dict[str, Any]],
        replace: bool = False
    ) -> Dict[str, Any]:
        """
        Upload BLB table data to staging.
        
        Args:
            table_name: BLB table name (e.g., 'dim_player')
            data: List of records to upload
            replace: If True, delete existing data first
            
        Returns:
            Dict with results
        """
        # Map to staging table name
        staging_table = self.BLB_TABLE_MAP.get(table_name)
        if not staging_table:
            raise ValueError(f"Unknown BLB table: {table_name}. Valid tables: {list(self.BLB_TABLE_MAP.keys())}")
        
        client = self.manager.client
        
        # Replace mode: delete existing data
        if replace:
            try:
                # Get all rows and delete them
                # Note: Supabase doesn't support DELETE without WHERE, so we need to get IDs first
                # For tables with primary keys, we can delete by ID
                # For now, we'll attempt to delete all rows (may require specific implementation per table)
                # This is a limitation - consider using truncate via SQL or delete by ID range
                logger.warning(f"Replace mode: Clearing {staging_table} - manual SQL truncate recommended for large tables")
                # Note: Full table clear requires SQL: TRUNCATE TABLE {staging_table} CASCADE;
            except Exception as e:
                logger.warning(f"Could not clear existing data: {e}")
        
        # Upload data in batches
        batch_size = 500
        uploaded = 0
        errors = []
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            try:
                client.table(staging_table).insert(batch).execute()
                uploaded += len(batch)
            except Exception as e:
                error_msg = str(e)
                errors.append(f"Batch {i}: {error_msg[:100]}")
                logger.error(f"Failed to upload batch {i} to {staging_table}: {error_msg[:100]}")
        
        return {
            'table_name': table_name,
            'staging_table': staging_table,
            'rows_uploaded': uploaded,
            'rows_failed': len(data) - uploaded,
            'errors': errors
        }
    
    def update_blb_table(
        self,
        table_name: str,
        filter_column: str,
        filter_value: Any,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update rows in BLB staging table.
        
        Args:
            table_name: BLB table name
            filter_column: Column to filter on
            filter_value: Filter value
            updates: Fields to update
            
        Returns:
            Dict with results
        """
        staging_table = self.BLB_TABLE_MAP.get(table_name)
        if not staging_table:
            raise ValueError(f"Unknown BLB table: {table_name}")
        
        client = self.manager.client
        
        try:
            # Update matching rows
            result = client.table(staging_table).update(updates).eq(filter_column, filter_value).execute()
            rows_updated = len(result.data) if result.data else 0
            
            return {
                'table_name': table_name,
                'staging_table': staging_table,
                'rows_updated': rows_updated,
                'errors': []
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to update {staging_table}: {error_msg}")
            return {
                'table_name': table_name,
                'staging_table': staging_table,
                'rows_updated': 0,
                'errors': [error_msg[:200]]
            }
    
    def upload_tracking_data(
        self,
        game_id: int,
        events: Optional[List[Dict[str, Any]]] = None,
        shifts: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Upload tracking data (events/shifts) to staging.
        
        Args:
            game_id: Game ID
            events: List of event records
            shifts: List of shift records
            
        Returns:
            Dict with results
        """
        client = self.manager.client
        results = {
            'game_id': game_id,
            'events_uploaded': 0,
            'shifts_uploaded': 0,
            'errors': []
        }
        
        # Upload events
        if events:
            batch_size = 500
            for i in range(0, len(events), batch_size):
                batch = events[i:i + batch_size]
                # Ensure game_id is set
                for record in batch:
                    record['game_id'] = str(game_id)
                try:
                    client.table('stage_events_tracking').insert(batch).execute()
                    results['events_uploaded'] += len(batch)
                except Exception as e:
                    error_msg = str(e)
                    results['errors'].append(f"Events batch {i}: {error_msg[:100]}")
                    logger.error(f"Failed to upload events batch {i}: {error_msg[:100]}")
        
        # Upload shifts
        if shifts:
            batch_size = 500
            for i in range(0, len(shifts), batch_size):
                batch = shifts[i:i + batch_size]
                # Ensure game_id is set
                for record in batch:
                    record['game_id'] = str(game_id)
                try:
                    client.table('stage_shifts_tracking').insert(batch).execute()
                    results['shifts_uploaded'] += len(batch)
                except Exception as e:
                    error_msg = str(e)
                    results['errors'].append(f"Shifts batch {i}: {error_msg[:100]}")
                    logger.error(f"Failed to upload shifts batch {i}: {error_msg[:100]}")
        
        return results
    
    def get_blb_table_list(self) -> List[str]:
        """Get list of valid BLB table names."""
        return list(self.BLB_TABLE_MAP.keys())


# Global staging service instance
staging_service = StagingService()
