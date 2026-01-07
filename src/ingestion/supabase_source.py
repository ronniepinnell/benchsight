#!/usr/bin/env python3
"""
BENCHSIGHT - Supabase Data Source
=================================

Provides the same interface as Excel reads but pulls from Supabase tables.

This module allows the ETL to read source data from Supabase instead of Excel files.
The schema in Supabase should mirror the Excel structure.

Usage:
    from src.ingestion.supabase_source import SupabaseSource
    
    source = SupabaseSource()
    
    # Load BLB tables (replaces reading from BLB_Tables.xlsx)
    blb_tables = source.load_blb_tables()
    
    # Load tracking data for a game (replaces reading from {game_id}_tracking.xlsx)
    events, shifts = source.load_tracking_data(game_id='18969')

Required Supabase Tables:
    Stage tables (raw data mirrors Excel):
        - stage_dim_player
        - stage_dim_team
        - stage_dim_league
        - stage_dim_season
        - stage_dim_schedule
        - stage_dim_playerurlref
        - stage_dim_rink_zone
        - stage_dim_rink_zone
        - stage_dim_randomnames
        - stage_fact_gameroster
        - stage_fact_leadership
        - stage_fact_registration
        - stage_fact_draft
        - stage_fact_playergames
        - stage_events_tracking (contains game_id column)
        - stage_shifts_tracking (contains game_id column)

Configuration:
    Set environment variables or use config/config.ini:
        SUPABASE_URL=https://your-project.supabase.co
        SUPABASE_KEY=your-service-role-key
"""

import os
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from configparser import ConfigParser

# Try to import supabase client
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Warning: supabase-py not installed. Run: pip install supabase")


class SupabaseSource:
    """
    Data source that reads from Supabase instead of Excel files.
    
    Provides the same interface as Excel reads for seamless switching.
    """
    
    # Mapping of BLB sheet names to Supabase table names
    BLB_TABLE_MAP = {
        'dim_player': 'stage_dim_player',
        'dim_team': 'stage_dim_team',
        'dim_league': 'stage_dim_league',
        'dim_season': 'stage_dim_season',
        'dim_schedule': 'stage_dim_schedule',
        'dim_playerurlref': 'stage_dim_playerurlref',
        'dim_rink_zone': 'stage_dim_rink_zone',
        'dim_rink_zone': 'stage_dim_rink_zone',
        'dim_randomnames': 'stage_dim_randomnames',
        'fact_gameroster': 'stage_fact_gameroster',
        'fact_leadership': 'stage_fact_leadership',
        'fact_registration': 'stage_fact_registration',
        'fact_draft': 'stage_fact_draft',
        'fact_playergames': 'stage_fact_playergames',
    }
    
    # Tracking tables
    EVENTS_TABLE = 'stage_events_tracking'
    SHIFTS_TABLE = 'stage_shifts_tracking'
    
    def __init__(self, url: str = None, key: str = None, config_path: str = None):
        """
        Initialize Supabase connection.
        
        Args:
            url: Supabase project URL (or set SUPABASE_URL env var)
            key: Supabase service role key (or set SUPABASE_KEY env var)
            config_path: Path to config.ini file
        """
        if not SUPABASE_AVAILABLE:
            raise ImportError("supabase-py is required. Install with: pip install supabase")
        
        # Load from config file if provided
        if config_path:
            config = ConfigParser()
            config.read(config_path)
            url = url or config.get('supabase', 'url', fallback=None)
            key = key or config.get('supabase', 'key', fallback=None)
        
        # Fall back to environment variables
        self.url = url or os.environ.get('SUPABASE_URL')
        self.key = key or os.environ.get('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError(
                "Supabase credentials required. Set SUPABASE_URL and SUPABASE_KEY "
                "environment variables, or pass url/key to constructor, or provide config_path."
            )
        
        self.client: Client = create_client(self.url, self.key)
        self._test_connection()
    
    def _test_connection(self):
        """Test the Supabase connection."""
        try:
            # Try to query a simple table
            self.client.table('stage_dim_league').select('*').limit(1).execute()
            print("✓ Supabase connection successful")
        except Exception as e:
            print(f"⚠ Supabase connection test failed: {e}")
    
    def _read_table(self, table_name: str, filters: Dict = None, limit: int = None) -> pd.DataFrame:
        """
        Read a table from Supabase into a DataFrame.
        
        Args:
            table_name: Name of the Supabase table
            filters: Optional dict of column=value filters
            limit: Optional row limit
            
        Returns:
            DataFrame with table data
        """
        try:
            query = self.client.table(table_name).select('*')
            
            # Apply filters
            if filters:
                for col, val in filters.items():
                    if isinstance(val, list):
                        query = query.in_(col, val)
                    else:
                        query = query.eq(col, val)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            response = query.execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error reading {table_name}: {e}")
            return pd.DataFrame()
    
    def _read_table_paginated(self, table_name: str, filters: Dict = None, 
                              page_size: int = 1000) -> pd.DataFrame:
        """
        Read a large table with pagination.
        
        Args:
            table_name: Name of the Supabase table
            filters: Optional dict of column=value filters
            page_size: Rows per page (default 1000)
            
        Returns:
            DataFrame with all table data
        """
        all_data = []
        offset = 0
        
        while True:
            try:
                query = self.client.table(table_name).select('*')
                
                if filters:
                    for col, val in filters.items():
                        if isinstance(val, list):
                            query = query.in_(col, val)
                        else:
                            query = query.eq(col, val)
                
                query = query.range(offset, offset + page_size - 1)
                response = query.execute()
                
                if not response.data:
                    break
                
                all_data.extend(response.data)
                
                if len(response.data) < page_size:
                    break
                
                offset += page_size
                
            except Exception as e:
                print(f"Error reading {table_name} at offset {offset}: {e}")
                break
        
        return pd.DataFrame(all_data) if all_data else pd.DataFrame()
    
    def load_blb_tables(self) -> Dict[str, pd.DataFrame]:
        """
        Load all BLB tables from Supabase.
        
        This replaces reading from BLB_Tables.xlsx.
        
        Returns:
            Dict mapping table names to DataFrames
        """
        print("Loading BLB tables from Supabase...")
        loaded = {}
        
        for output_name, supabase_table in self.BLB_TABLE_MAP.items():
            print(f"  Loading {output_name} from {supabase_table}...")
            
            df = self._read_table_paginated(supabase_table)
            
            if df.empty:
                print(f"    ⚠ No data found in {supabase_table}")
                continue
            
            # Convert all columns to string (matching Excel behavior)
            df = df.astype(str)
            df = df.replace('None', pd.NA).replace('nan', pd.NA)
            
            loaded[output_name] = df
            print(f"    ✓ {output_name}: {len(df):,} rows")
        
        return loaded
    
    def load_tracking_data(self, game_id: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load tracking data for a specific game from Supabase.
        
        This replaces reading from {game_id}_tracking.xlsx.
        
        Args:
            game_id: The game ID to load
            
        Returns:
            Tuple of (events_df, shifts_df)
        """
        print(f"Loading tracking data for game {game_id} from Supabase...")
        
        # Load events
        events_df = self._read_table_paginated(
            self.EVENTS_TABLE, 
            filters={'game_id': str(game_id)}
        )
        
        if not events_df.empty:
            events_df = events_df.astype(str)
            events_df = events_df.replace('None', pd.NA).replace('nan', pd.NA)
            print(f"  ✓ Events: {len(events_df):,} rows")
        else:
            print(f"  ⚠ No events found for game {game_id}")
        
        # Load shifts
        shifts_df = self._read_table_paginated(
            self.SHIFTS_TABLE,
            filters={'game_id': str(game_id)}
        )
        
        if not shifts_df.empty:
            shifts_df = shifts_df.astype(str)
            shifts_df = shifts_df.replace('None', pd.NA).replace('nan', pd.NA)
            print(f"  ✓ Shifts: {len(shifts_df):,} rows")
        else:
            print(f"  ⚠ No shifts found for game {game_id}")
        
        return events_df, shifts_df
    
    def load_all_tracking_data(self, game_ids: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load tracking data for multiple games.
        
        Args:
            game_ids: List of game IDs to load
            
        Returns:
            Tuple of (combined_events_df, combined_shifts_df)
        """
        print(f"Loading tracking data for {len(game_ids)} games from Supabase...")
        
        # Load all events for these games
        events_df = self._read_table_paginated(
            self.EVENTS_TABLE,
            filters={'game_id': game_ids}
        )
        
        if not events_df.empty:
            events_df = events_df.astype(str)
            events_df = events_df.replace('None', pd.NA).replace('nan', pd.NA)
            print(f"  ✓ Events: {len(events_df):,} rows, {events_df['game_id'].nunique()} games")
        
        # Load all shifts for these games
        shifts_df = self._read_table_paginated(
            self.SHIFTS_TABLE,
            filters={'game_id': game_ids}
        )
        
        if not shifts_df.empty:
            shifts_df = shifts_df.astype(str)
            shifts_df = shifts_df.replace('None', pd.NA).replace('nan', pd.NA)
            print(f"  ✓ Shifts: {len(shifts_df):,} rows, {shifts_df['game_id'].nunique()} games")
        
        return events_df, shifts_df
    
    def get_available_games(self) -> List[str]:
        """
        Get list of game IDs that have tracking data in Supabase.
        
        Returns:
            List of game IDs
        """
        try:
            # Query distinct game_ids from events table
            response = self.client.table(self.EVENTS_TABLE).select('game_id').execute()
            
            if response.data:
                game_ids = list(set(row['game_id'] for row in response.data if row.get('game_id')))
                return sorted(game_ids)
            return []
            
        except Exception as e:
            print(f"Error getting available games: {e}")
            return []
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in Supabase."""
        try:
            self.client.table(table_name).select('*').limit(1).execute()
            return True
        except Exception:
            return False
    
    def get_table_count(self, table_name: str) -> int:
        """Get row count for a table."""
        try:
            response = self.client.table(table_name).select('*', count='exact').limit(0).execute()
            return response.count or 0
        except Exception:
            return 0


# ============================================================
# HELPER FUNCTIONS FOR ETL INTEGRATION
# ============================================================

def create_source(source_type: str = 'excel', **kwargs):
    """
    Factory function to create the appropriate data source.
    
    Args:
        source_type: 'excel' or 'supabase'
        **kwargs: Additional arguments for the source
        
    Returns:
        Data source instance
    """
    if source_type == 'supabase':
        return SupabaseSource(**kwargs)
    else:
        # Return None to indicate using default Excel behavior
        return None


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    # Test Supabase connection and data loading
    import sys
    
    print("=" * 60)
    print("SUPABASE DATA SOURCE TEST")
    print("=" * 60)
    
    # Check for credentials
    if not os.environ.get('SUPABASE_URL') or not os.environ.get('SUPABASE_KEY'):
        print("\nSet SUPABASE_URL and SUPABASE_KEY environment variables to test.")
        print("\nExample:")
        print("  export SUPABASE_URL='https://your-project.supabase.co'")
        print("  export SUPABASE_KEY='your-service-role-key'")
        sys.exit(1)
    
    try:
        source = SupabaseSource()
        
        # Test loading BLB tables
        print("\n--- Testing BLB Tables ---")
        blb_tables = source.load_blb_tables()
        
        for name, df in blb_tables.items():
            print(f"  {name}: {len(df)} rows, {len(df.columns)} cols")
        
        # Test getting available games
        print("\n--- Available Games ---")
        games = source.get_available_games()
        print(f"  Games with tracking data: {games}")
        
        # Test loading tracking data
        if games:
            print(f"\n--- Loading Tracking for Game {games[0]} ---")
            events, shifts = source.load_tracking_data(games[0])
            print(f"  Events: {len(events)} rows")
            print(f"  Shifts: {len(shifts)} rows")
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
