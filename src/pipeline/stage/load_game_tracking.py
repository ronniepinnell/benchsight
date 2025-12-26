"""
=============================================================================
STAGE: LOAD GAME TRACKING DATA
=============================================================================
File: src/pipeline/stage/load_game_tracking.py

PURPOSE:
    Load game tracking Excel files into the STAGE layer.
    Each game gets its own set of stage tables.

TABLES CREATED (per game):
    - stg_events_{game_id}    : All event rows from events sheet
    - stg_shifts_{game_id}    : All shift rows from shifts sheet

WHY GAME-SPECIFIC TABLES:
    - Process games independently
    - Easy to reprocess single game
    - Clear data lineage
    - Later consolidated in intermediate layer

=============================================================================
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from src.database.table_operations import (
    load_dataframe_to_table,
    table_exists,
    drop_table
)
from src.database.connection import execute_sql
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_game_to_stage(
    game_id: int,
    tracking_file: Path,
    force_reload: bool = False
) -> Dict[str, int]:
    """
    Load a single game's tracking data to stage layer.
    
    WHY THIS FUNCTION:
        Process one game at a time.
        Keep games isolated for easy reprocessing.
    
    HOW IT WORKS:
        1. Check if game already staged (unless force_reload)
        2. Read events sheet from tracking file
        3. Read shifts sheet from tracking file
        4. Load each into game-specific stage tables
        5. Record metadata
    
    Args:
        game_id: Unique game identifier (e.g., 18969).
        tracking_file: Path to {game_id}_tracking.xlsx file.
        force_reload: If True, reload even if already staged.
    
    Returns:
        Dictionary with table names and row counts.
        Example: {'stg_events_18969': 3596, 'stg_shifts_18969': 98}
    
    Example:
        results = load_game_to_stage(
            18969, 
            Path('data/raw/games/18969/18969_tracking.xlsx')
        )
    """
    logger.info(f"Staging game {game_id} from {tracking_file}")
    
    # Check if already staged
    # WHY: Avoid redundant processing
    events_table = f'stg_events_{game_id}'
    shifts_table = f'stg_shifts_{game_id}'
    
    if not force_reload and table_exists(events_table):
        logger.info(f"Game {game_id} already staged. Use force_reload=True to refresh.")
        return _get_staged_game_counts(game_id)
    
    # Validate file exists
    if not tracking_file.exists():
        raise FileNotFoundError(f"Tracking file not found: {tracking_file}")
    
    # Open Excel file
    xlsx = pd.ExcelFile(tracking_file)
    
    results = {}
    
    # Load events sheet
    # WHY 'events': Standard sheet name for event data
    if 'events' in xlsx.sheet_names:
        events_df = pd.read_excel(xlsx, sheet_name='events')
        
        # Add game_id column for later consolidation
        # WHY: Link events back to their source game
        events_df['_game_id'] = game_id
        
        # Add load timestamp
        # WHY: Track when this data was loaded
        events_df['_load_timestamp'] = datetime.now().isoformat()
        
        row_count = load_dataframe_to_table(events_df, events_table, 'replace')
        results[events_table] = row_count
        logger.info(f"  Staged events: {row_count} rows")
    else:
        logger.warning(f"No 'events' sheet found in {tracking_file}")
    
    # Load shifts sheet
    # WHY 'shifts': Standard sheet name for shift data
    if 'shifts' in xlsx.sheet_names:
        shifts_df = pd.read_excel(xlsx, sheet_name='shifts')
        
        # Add metadata columns
        shifts_df['_game_id'] = game_id
        shifts_df['_load_timestamp'] = datetime.now().isoformat()
        
        row_count = load_dataframe_to_table(shifts_df, shifts_table, 'replace')
        results[shifts_table] = row_count
        logger.info(f"  Staged shifts: {row_count} rows")
    else:
        logger.warning(f"No 'shifts' sheet found in {tracking_file}")
    
    # Record metadata
    _record_game_load_metadata(game_id, tracking_file, results)
    
    return results


def load_xy_to_stage(
    game_id: int,
    xy_dir: Path
) -> Dict[str, int]:
    """
    Load XY coordinate data from subfolder to stage layer.
    
    WHY SEPARATE FUNCTION:
        XY data is optional and comes from different source.
        Multiple CSV files need to be combined.
    
    HOW IT WORKS:
        1. Find event_locations subfolder
        2. Read all CSV files in subfolder
        3. Combine into single DataFrame
        4. Load as stg_xy_events_{game_id}
        5. Repeat for shot_locations
    
    Args:
        game_id: Game identifier.
        xy_dir: Path to xy folder for this game.
    
    Returns:
        Dictionary with table names and row counts.
    """
    logger.info(f"Staging XY data for game {game_id}")
    
    results = {}
    
    # Load event locations
    # WHY subfolder: Multiple CSV files (one per period)
    event_loc_dir = xy_dir / 'event_locations'
    if event_loc_dir.exists():
        combined_df = _combine_csv_files(event_loc_dir)
        
        if len(combined_df) > 0:
            # Add game_id for linking
            combined_df['_game_id'] = game_id
            
            table_name = f'stg_xy_events_{game_id}'
            row_count = load_dataframe_to_table(combined_df, table_name, 'replace')
            results[table_name] = row_count
            logger.info(f"  Staged XY events: {row_count} rows")
    
    # Load shot locations
    shot_loc_dir = xy_dir / 'shot_locations'
    if shot_loc_dir.exists():
        combined_df = _combine_csv_files(shot_loc_dir)
        
        if len(combined_df) > 0:
            combined_df['_game_id'] = game_id
            
            table_name = f'stg_xy_shots_{game_id}'
            row_count = load_dataframe_to_table(combined_df, table_name, 'replace')
            results[table_name] = row_count
            logger.info(f"  Staged XY shots: {row_count} rows")
    
    return results


def _combine_csv_files(folder: Path) -> pd.DataFrame:
    """
    Combine all CSV files in a folder into one DataFrame.
    
    WHY COMBINE:
        XY data may be split across multiple files (one per period).
        Need single DataFrame for processing.
    
    HOW IT WORKS:
        1. Find all .csv files in folder
        2. Read each into DataFrame
        3. Add source filename column
        4. Concatenate all together
    
    Args:
        folder: Path to folder containing CSV files.
    
    Returns:
        Combined DataFrame, or empty DataFrame if no files.
    """
    all_dfs = []
    
    # Find all CSV files
    # WHY glob: Find files matching pattern
    csv_files = list(folder.glob('*.csv'))
    
    for csv_file in csv_files:
        # Skip hidden/temp files
        # WHY startswith: Excel temp files start with ~
        if csv_file.name.startswith('~'):
            continue
        
        # Read the file
        df = pd.read_csv(csv_file)
        
        # Track source file
        # WHY _source_file: Know which file each row came from
        df['_source_file'] = csv_file.name
        
        all_dfs.append(df)
    
    # Combine all DataFrames
    if all_dfs:
        # WHY ignore_index: Create new sequential index
        return pd.concat(all_dfs, ignore_index=True)
    else:
        return pd.DataFrame()


def _get_staged_game_counts(game_id: int) -> Dict[str, int]:
    """
    Get row counts for already-staged game tables.
    
    Returns:
        Dictionary of table names to row counts.
    """
    from src.database.table_operations import get_row_count
    
    results = {}
    
    # Check events table
    events_table = f'stg_events_{game_id}'
    if table_exists(events_table):
        results[events_table] = get_row_count(events_table)
    
    # Check shifts table
    shifts_table = f'stg_shifts_{game_id}'
    if table_exists(shifts_table):
        results[shifts_table] = get_row_count(shifts_table)
    
    return results


def _record_game_load_metadata(
    game_id: int,
    tracking_file: Path,
    results: Dict[str, int]
) -> None:
    """
    Record metadata about this game load.
    
    WHY METADATA:
        Track when each game was loaded.
        Know source files used.
    """
    execute_sql("""
        CREATE TABLE IF NOT EXISTS _game_load_metadata (
            load_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            load_timestamp TEXT NOT NULL,
            source_file TEXT NOT NULL,
            events_rows INTEGER,
            shifts_rows INTEGER
        )
    """)
    
    execute_sql("""
        INSERT INTO _game_load_metadata 
        (game_id, load_timestamp, source_file, events_rows, shifts_rows)
        VALUES (:game_id, :timestamp, :source, :events, :shifts)
    """, {
        'game_id': game_id,
        'timestamp': datetime.now().isoformat(),
        'source': str(tracking_file),
        'events': results.get(f'stg_events_{game_id}', 0),
        'shifts': results.get(f'stg_shifts_{game_id}', 0)
    })


def remove_staged_game(game_id: int) -> int:
    """
    Remove all staged data for a specific game.
    
    WHY THIS FUNCTION:
        Clean up before reprocessing.
        Remove incorrectly loaded games.
    
    Args:
        game_id: Game to remove.
    
    Returns:
        Number of tables dropped.
    """
    tables_dropped = 0
    
    # Drop events table
    if drop_table(f'stg_events_{game_id}'):
        tables_dropped += 1
    
    # Drop shifts table
    if drop_table(f'stg_shifts_{game_id}'):
        tables_dropped += 1
    
    # Drop XY tables if exist
    if drop_table(f'stg_xy_events_{game_id}'):
        tables_dropped += 1
    if drop_table(f'stg_xy_shots_{game_id}'):
        tables_dropped += 1
    
    logger.info(f"Removed {tables_dropped} staged tables for game {game_id}")
    return tables_dropped
