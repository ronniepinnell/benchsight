"""
=============================================================================
DATAMART: BUILD EVENTS
=============================================================================
File: src/pipeline/datamart/build_events.py

PURPOSE:
    Build fact_events table in datamart from intermediate data.

=============================================================================
"""

import pandas as pd
from typing import Dict

from src.database.connection import execute_sql
from src.database.table_operations import (
    table_exists, 
    get_row_count,
    read_query,
    load_dataframe_to_table
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def build_events_for_game(game_id: int) -> int:
    """
    Build and append events to fact_events table.
    
    Args:
        game_id: Game identifier.
    
    Returns:
        Number of rows added.
    """
    logger.info(f"Building events for game {game_id}")
    
    # Check intermediate exists
    if not table_exists(f'int_events_{game_id}'):
        logger.warning(f"No intermediate events for game {game_id}")
        return 0
    
    # Read intermediate events
    events_df = read_query(f"SELECT * FROM int_events_{game_id}")
    
    if not table_exists('fact_events'):
        # First game - create table
        load_dataframe_to_table(events_df, 'fact_events', 'replace')
        return len(events_df)
    
    # Append to existing
    existing = read_query("SELECT * FROM fact_events")
    
    # Remove existing rows for this game
    existing = existing[existing['game_id'] != game_id]
    
    # Combine
    combined = pd.concat([existing, events_df], ignore_index=True)
    
    load_dataframe_to_table(combined, 'fact_events', 'replace')
    
    logger.info(f"Added {len(events_df)} events for game {game_id}")
    return len(events_df)
