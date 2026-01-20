#!/usr/bin/env python3
"""
Event Enhancement Module
=========================

This module handles all event table enhancements, including:
- Adding foreign keys to fact_events and fact_event_players
- Creating derived event tables (sequences, plays, cycles)
- Adding flags and context columns to events
- Building specialized event tables (rushes, breakouts, saves, etc.)

Extracted from base_etl.py for better modularity.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Import utilities
from src.core.table_writer import save_output_table
from src.utils.key_parser import parse_shift_key

# Import table store for in-memory access
try:
    from src.core.table_store import get_table as get_table_from_store
    TABLE_STORE_AVAILABLE = True
except ImportError:
    TABLE_STORE_AVAILABLE = False
    def get_table_from_store(name, output_dir=None):
        return pd.DataFrame()


def drop_all_null_columns(df):
    """
    Drop columns that are 100% null (all values are null/NaN/None).
    EXCEPTS: coordinate, danger, and XY type columns (these may legitimately be null).
    
    Args:
        df: DataFrame to clean
        
    Returns:
        Tuple of (DataFrame with all-null columns removed, list of removed column names)
    """
    if len(df) == 0:
        return df, []
    
    import re
    
    # Columns to preserve even if 100% null (coordinate, danger, XY type columns)
    preserve_patterns = [
        r'x$', r'_x$', r'^x_',  # x coordinates
        r'y$', r'_y$', r'^y_',  # y coordinates
        r'coord',  # coordinate
        r'danger',  # danger zone/danger type
        r'xy',  # XY type columns
        r'target_x', r'target_y',  # target coordinates
        r'shot_x', r'shot_y',  # shot coordinates
        r'net_target',  # net target coordinates
        r'location_id$',  # location IDs (coordinate-related)
        r'zone_coord',  # zone coordinates
        r'rink_coord',  # rink coordinates
    ]
    
    # Find columns where all values are null
    null_cols = []
    for col in df.columns:
        # Skip if column matches preserve patterns
        should_preserve = any(re.search(pattern, col, re.IGNORECASE) for pattern in preserve_patterns)
        if should_preserve:
            continue
            
        # Check if all values are null/NaN/None/empty string
        if df[col].isna().all():
            null_cols.append(col)
        elif df[col].dtype == 'object':
            # For object columns, also check for empty strings and 'None'/'nan' strings
            non_null = df[col].dropna()
            if len(non_null) == 0:
                null_cols.append(col)
            elif len(non_null) > 0:
                # Check if all non-null values are empty-like
                all_empty = non_null.astype(str).str.strip().isin(['', 'None', 'nan', 'null', 'NaT']).all()
                if all_empty:
                    null_cols.append(col)
    
    if null_cols:
        df = df.drop(columns=null_cols)
    
    return df, null_cols


def save_table(df, name, output_dir=None):
    """
    Save a DataFrame to CSV (legacy function for compatibility).
    
    Note: Prefer save_output_table() for new code.
    """
    if output_dir is None:
        from src.core.base_etl import OUTPUT_DIR
        output_dir = OUTPUT_DIR
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    path = output_dir / f"{name}.csv"
    df.to_csv(path, index=False)
    
    return path


def _make_cycle_record(cycle_num, game_id, team_name, events_list, pass_count, end_type, team_map, first_row):
    """Build a cycle record dictionary."""
    event_ids = [e['event_id'] for e in events_list]
    player_ids = list(set([e['player_id'] for e in events_list if pd.notna(e.get('player_id'))]))
    
    return {
        'cycle_key': f'CY{game_id}{cycle_num:04d}',
        'game_id': game_id,
        'season_id': first_row.get('season_id') if first_row is not None else None,
        'team_id': team_map.get(team_name),
        'team_name': team_name,
        'home_team_id': first_row.get('home_team_id') if first_row is not None else None,
        'away_team_id': first_row.get('away_team_id') if first_row is not None else None,
        'pass_count': pass_count,
        'event_count': len(events_list),
        'player_count': len(player_ids),
        'start_event_id': events_list[0]['event_id'],
        'end_event_id': events_list[-1]['event_id'],
        'start_time': events_list[0]['event_running_start'],
        'end_time': events_list[-1]['event_running_start'],
        'duration_seconds': events_list[-1]['event_running_start'] - events_list[0]['event_running_start'],
        'ended_with': end_type,
        'ended_with_shot': 1 if end_type in ['shot', 'goal'] else 0,
        'ended_with_goal': 1 if end_type == 'goal' else 0,
        'event_ids': ','.join(event_ids),
        'player_ids': ','.join([str(p) for p in player_ids])
    }
