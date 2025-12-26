"""
=============================================================================
DATAMART: BUILD BOX SCORE
=============================================================================
File: src/pipeline/datamart/build_box_score.py

PURPOSE:
    Build the fact_box_score table in the datamart layer.

=============================================================================
"""

from pathlib import Path
from typing import Dict
import pandas as pd
import numpy as np

from src.database.connection import execute_sql, get_connection
from src.database.table_operations import (
    get_row_count, 
    table_exists,
    load_dataframe_to_table,
    read_query
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def remove_datamart_game(game_id: int) -> Dict[str, int]:
    """
    Remove all datamart data for a specific game.
    
    WHY THIS FUNCTION:
        Clean up before reprocessing.
        Allow complete game replacement.
    
    Args:
        game_id: Game to remove.
    
    Returns:
        Dictionary with rows removed per table.
    """
    results = {}
    
    # Remove from fact_box_score
    if table_exists('fact_box_score'):
        count_before = get_row_count('fact_box_score')
        execute_sql("DELETE FROM fact_box_score WHERE game_id = :game_id", {'game_id': game_id})
        count_after = get_row_count('fact_box_score')
        results['fact_box_score'] = count_before - count_after
    
    # Remove from fact_events
    if table_exists('fact_events'):
        count_before = get_row_count('fact_events')
        execute_sql("DELETE FROM fact_events WHERE game_id = :game_id", {'game_id': game_id})
        count_after = get_row_count('fact_events')
        results['fact_events'] = count_before - count_after
    
    logger.info(f"Removed datamart data for game {game_id}: {results}")
    return results

SQL_FILE = Path(__file__).parent.parent.parent / 'sql' / 'datamart' / 'build_box_score.sql'


def build_box_score_for_game(game_id: int) -> int:
    """
    Build box score for a single game and append to datamart.
    
    Args:
        game_id: Game to build box score for.
    
    Returns:
        Number of rows added to box score.
    """
    logger.info(f"Building box score for game {game_id}")
    
    # Check intermediate tables exist
    if not table_exists(f'int_events_{game_id}'):
        raise RuntimeError(f"Intermediate tables not found for game {game_id}.")
    
    # Step 1: Execute SQL to build temporary box score
    _execute_box_score_sql(game_id)
    
    # Step 2: Calculate TOI from shifts
    toi_df = _calculate_toi_from_shifts(game_id)
    
    # Step 3: Merge TOI into box score
    _merge_toi_into_box_score(game_id, toi_df)
    
    # Step 4: Add per-60 rate stats
    _add_rate_stats(game_id)
    
    # Step 5: Append to main fact_box_score table
    rows = _append_to_fact_box_score(game_id)
    
    # Step 6: Cleanup
    _cleanup_temp_tables(game_id)
    
    logger.info(f"Added {rows} rows to fact_box_score for game {game_id}")
    return rows


def _execute_box_score_sql(game_id: int) -> None:
    """Execute the box score SQL with game_id substitution."""
    if not SQL_FILE.exists():
        raise FileNotFoundError(f"SQL file not found: {SQL_FILE}")
    
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Replace :game_id with actual value
    sql_content = sql_content.replace(':game_id', str(game_id))
    
    # Execute statements
    for statement in sql_content.split(';'):
        statement = statement.strip()
        if not statement or all(l.strip().startswith('--') for l in statement.split('\n') if l.strip()):
            continue
        try:
            execute_sql(statement)
        except Exception as e:
            if 'no such table' not in str(e).lower():
                logger.warning(f"SQL warning: {e}")


def _calculate_toi_from_shifts(game_id: int) -> pd.DataFrame:
    """Calculate time on ice from shift data."""
    shifts_df = read_query(f"SELECT * FROM int_shifts_{game_id}")
    
    if len(shifts_df) == 0:
        return pd.DataFrame(columns=['player_game_number', 'toi_seconds', 'plus_minus', 'shifts'])
    
    # Player columns
    home_cols = ['home_forward_1', 'home_forward_2', 'home_forward_3',
                 'home_defense_1', 'home_defense_2', 'home_goalie']
    away_cols = ['away_forward_1', 'away_forward_2', 'away_forward_3',
                 'away_defense_1', 'away_defense_2', 'away_goalie']
    
    existing_home = [c for c in home_cols if c in shifts_df.columns]
    existing_away = [c for c in away_cols if c in shifts_df.columns]
    
    player_data = []
    
    for _, row in shifts_df.iterrows():
        shift_duration = row.get('shift_duration', 0) or 0
        
        for col in existing_home:
            player_num = row.get(col)
            if pd.notna(player_num):
                pm = (row.get('home_plus', 0) or 0) + (row.get('home_minus', 0) or 0)
                player_data.append({
                    'player_game_number': int(player_num),
                    'shift_duration': shift_duration,
                    'plus_minus': pm
                })
        
        for col in existing_away:
            player_num = row.get(col)
            if pd.notna(player_num):
                pm = (row.get('away_plus', 0) or 0) + (row.get('away_minus', 0) or 0)
                player_data.append({
                    'player_game_number': int(player_num),
                    'shift_duration': shift_duration,
                    'plus_minus': pm
                })
    
    if not player_data:
        return pd.DataFrame(columns=['player_game_number', 'toi_seconds', 'plus_minus', 'shifts'])
    
    player_df = pd.DataFrame(player_data)
    
    # Aggregate
    toi_df = player_df.groupby('player_game_number').agg({
        'shift_duration': 'sum',
        'plus_minus': 'sum'
    }).reset_index()
    
    # Add shift count
    shift_counts = player_df.groupby('player_game_number').size().reset_index(name='shifts')
    toi_df = toi_df.merge(shift_counts, on='player_game_number')
    
    toi_df.columns = ['player_game_number', 'toi_seconds', 'plus_minus', 'shifts']
    
    return toi_df


def _merge_toi_into_box_score(game_id: int, toi_df: pd.DataFrame) -> None:
    """Merge TOI data into temporary box score."""
    box_df = read_query(f"SELECT * FROM _tmp_box_score_{game_id}")
    
    # Ensure consistent types for merge key
    box_df['player_game_number'] = pd.to_numeric(box_df['player_game_number'], errors='coerce').astype('Int64')
    toi_df['player_game_number'] = pd.to_numeric(toi_df['player_game_number'], errors='coerce').astype('Int64')
    
    # Merge TOI
    box_df = box_df.merge(toi_df, on='player_game_number', how='left')
    
    # Fill missing values
    box_df['toi_seconds'] = box_df['toi_seconds'].fillna(0)
    box_df['plus_minus'] = box_df['plus_minus'].fillna(0).astype(int)
    box_df['shifts'] = box_df['shifts'].fillna(0).astype(int)
    
    # Formatted TOI
    box_df['toi_formatted'] = box_df['toi_seconds'].apply(
        lambda x: f"{int(x//60)}:{int(x%60):02d}"
    )
    
    load_dataframe_to_table(box_df, f'_tmp_box_score_{game_id}', 'replace')


def _add_rate_stats(game_id: int) -> None:
    """Add per-60 minute rate statistics."""
    execute_sql(f"""
        CREATE TABLE _tmp_box_rates_{game_id} AS
        SELECT *,
            CASE WHEN toi_seconds > 0 THEN ROUND(CAST(goals AS REAL) * 3600 / toi_seconds, 2) ELSE 0 END AS goals_per_60,
            CASE WHEN toi_seconds > 0 THEN ROUND(CAST(assists AS REAL) * 3600 / toi_seconds, 2) ELSE 0 END AS assists_per_60,
            CASE WHEN toi_seconds > 0 THEN ROUND(CAST(points AS REAL) * 3600 / toi_seconds, 2) ELSE 0 END AS points_per_60,
            CASE WHEN toi_seconds > 0 THEN ROUND(CAST(shots AS REAL) * 3600 / toi_seconds, 2) ELSE 0 END AS shots_per_60
        FROM _tmp_box_score_{game_id}
    """)
    execute_sql(f"DROP TABLE _tmp_box_score_{game_id}")
    execute_sql(f"ALTER TABLE _tmp_box_rates_{game_id} RENAME TO _tmp_box_score_{game_id}")


def _append_to_fact_box_score(game_id: int) -> int:
    """Append to main fact_box_score table."""
    game_box = read_query(f"SELECT * FROM _tmp_box_score_{game_id}")
    
    if not table_exists('fact_box_score'):
        load_dataframe_to_table(game_box, 'fact_box_score', 'replace')
        return len(game_box)
    
    existing = read_query("SELECT * FROM fact_box_score")
    existing = existing[existing['game_id'] != game_id]
    combined = pd.concat([existing, game_box], ignore_index=True)
    load_dataframe_to_table(combined, 'fact_box_score', 'replace')
    
    return len(game_box)


def _cleanup_temp_tables(game_id: int) -> None:
    """Remove temporary tables."""
    from src.database.table_operations import drop_table
    drop_table(f'_tmp_box_score_{game_id}')
