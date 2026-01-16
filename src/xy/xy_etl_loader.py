#!/usr/bin/env python3
"""
XY ETL Loader - Load XY coordinate data from separate export files.

This module loads XY data from export files (CSV/Excel) into:
- fact_player_xy_long (one row per point per player per event)
- fact_player_xy_wide (one row per player per event with x1-x10, y1-y10)
- fact_puck_xy_long (one row per point per event)
- fact_puck_xy_wide (one row per event with puck_x1-puck_x10, puck_y1-puck_y10)
- fact_shot_xy (shot location with net target XY)

INPUT:
    Separate export files with XY data (CSV or Excel):
    - player_xy_export.csv (or .xlsx)
    - puck_xy_export.csv (or .xlsx)
    - shot_xy_export.csv (or .xlsx) - optional, can also come from events

USAGE:
    from src.xy.xy_etl_loader import load_all_xy_data
    load_all_xy_data(
        player_xy_path='data/raw/xy_exports/player_xy_export.csv',
        puck_xy_path='data/raw/xy_exports/puck_xy_export.csv',
        shot_xy_path='data/raw/xy_exports/shot_xy_export.csv'
    )
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Dict, List
import logging
from src.core.table_writer import save_output_table

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path('data/output')

# Rink constants
GOAL_LINE_X = 89.0  # Distance from center to goal line
POINT_NUMBERS = list(range(1, 11))  # Points 1-10


def calculate_distance_to_net(x: float, y: float, attacking_right: bool = True) -> Optional[float]:
    """Calculate distance from point to net center."""
    if pd.isna(x) or pd.isna(y):
        return None
    
    goal_x = GOAL_LINE_X if attacking_right else -GOAL_LINE_X
    return round(np.sqrt((goal_x - x)**2 + y**2), 1)


def calculate_angle_to_net(x: float, y: float, attacking_right: bool = True) -> Optional[float]:
    """Calculate angle from point to net center (in degrees)."""
    if pd.isna(x) or pd.isna(y):
        return None
    
    goal_x = GOAL_LINE_X if attacking_right else -GOAL_LINE_X
    dx = goal_x - x
    dy = y
    
    if dx <= 0:
        return None  # Behind the goal line
    
    angle = np.degrees(np.arctan2(abs(dy), dx))
    return round(angle, 1)


def load_xy_export(file_path: Path) -> pd.DataFrame:
    """Load XY export file (CSV or Excel)."""
    if not file_path.exists():
        logger.warning(f"  XY export file not found: {file_path}")
        return pd.DataFrame()
    
    try:
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path, low_memory=False)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            logger.error(f"  Unsupported file format: {file_path.suffix}")
            return pd.DataFrame()
        
        logger.info(f"  Loaded {len(df):,} rows from {file_path.name}")
        return df
    except Exception as e:
        logger.error(f"  Error loading {file_path}: {e}")
        return pd.DataFrame()


def load_player_xy_long(player_xy_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load player XY data in long format (one row per point per player per event).
    
    Expected columns (flexible):
    - event_id (required)
    - game_id (required)
    - player_id (required)
    - player_name (optional)
    - player_role (optional)
    - point_number (required, 1-10)
    - x, y (required)
    - timestamp (optional)
    - is_stop (optional flag indicating this is the stop point)
    """
    if player_xy_path is None:
        # Try default locations
        default_paths = [
            Path('data/raw/xy_exports/player_xy_long.csv'),
            Path('data/raw/xy_exports/player_xy_export.csv'),
            Path('data/raw/xy_exports/player_xy.csv'),
        ]
        for path in default_paths:
            if path.exists():
                player_xy_path = path
                break
        
        if player_xy_path is None:
            logger.info("  No player XY export file found, skipping")
            return pd.DataFrame()
    
    df = load_xy_export(player_xy_path)
    if len(df) == 0:
        return pd.DataFrame()
    
    # Normalize column names (handle variations)
    col_mapping = {
        'event_index': 'event_id',
        'event_key': 'event_id',
        'player_key': 'player_id',
        'point_num': 'point_number',
        'point': 'point_number',
        'coord_x': 'x',
        'coord_y': 'y',
        'x_coord': 'x',
        'y_coord': 'y',
    }
    
    for old_col, new_col in col_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df[new_col] = df[old_col]
    
    # Required columns check
    required = ['event_id', 'game_id', 'player_id', 'x', 'y']
    missing = [col for col in required if col not in df.columns]
    if missing:
        logger.error(f"  Missing required columns: {missing}")
        return pd.DataFrame()
    
    # Ensure point_number exists (default to 1 if not present for single-point rows)
    if 'point_number' not in df.columns:
        # Try to infer from column names like x_1, x_2, etc.
        # For now, default to 1
        df['point_number'] = 1
        logger.warning("  point_number column not found, defaulting to 1")
    
    # Build records
    records = []
    for _, row in df.iterrows():
        event_id = str(row.get('event_id', ''))
        game_id = row.get('game_id')
        player_id = str(row.get('player_id', ''))
        point_num = int(row.get('point_number', 1))
        x = row.get('x')
        y = row.get('y')
        
        if pd.isna(x) or pd.isna(y):
            continue
        
        record = {
            'player_xy_key': f"PXL{game_id}{str(event_id)[-5:]}{str(player_id)[-4:]}{point_num:02d}",
            'event_id': event_id,
            'game_id': game_id,
            'player_id': player_id,
            'player_name': row.get('player_name'),
            'player_role': row.get('player_role'),
            'team_id': row.get('team_id'),
            'is_event_team': row.get('is_event_team'),
            'point_number': point_num,
            'x': float(x),
            'y': float(y),
            'distance_to_net': calculate_distance_to_net(float(x), float(y)),
            'angle_to_net': calculate_angle_to_net(float(x), float(y)),
            'is_stop': 1 if row.get('is_stop') == 1 or (row.get('is_stop_point') == True) else 0,
            'timestamp': row.get('timestamp'),
            '_export_timestamp': datetime.now().isoformat()
        }
        
        records.append(record)
    
    result_df = pd.DataFrame(records)
    logger.info(f"  Created {len(result_df):,} player XY long records")
    return result_df


def load_player_xy_wide(player_xy_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load player XY data in wide format (one row per player per event with x1-x10, y1-y10).
    
    Expected columns (flexible):
    - event_id, game_id, player_id (required)
    - x_1, y_1, x_2, y_2, ... x_10, y_10 (or x1, y1, etc.)
    - player_name, player_role, team_id (optional)
    - point_count (optional, number of points populated)
    """
    if player_xy_path is None:
        # Try default locations
        default_paths = [
            Path('data/raw/xy_exports/player_xy_wide.csv'),
            Path('data/raw/xy_exports/player_xy_export.csv'),
            Path('data/raw/xy_exports/player_xy.csv'),
        ]
        for path in default_paths:
            if path.exists():
                player_xy_path = path
                break
        
        if player_xy_path is None:
            logger.info("  No player XY export file found, skipping")
            return pd.DataFrame()
    
    df = load_xy_export(player_xy_path)
    if len(df) == 0:
        return pd.DataFrame()
    
    # Normalize column names
    col_mapping = {
        'event_index': 'event_id',
        'event_key': 'event_id',
        'player_key': 'player_id',
    }
    
    for old_col, new_col in col_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df[new_col] = df[old_col]
    
    # Required columns
    if 'event_id' not in df.columns or 'game_id' not in df.columns or 'player_id' not in df.columns:
        logger.error("  Missing required columns: event_id, game_id, player_id")
        return pd.DataFrame()
    
    # Build records
    records = []
    for _, row in df.iterrows():
        event_id = str(row.get('event_id', ''))
        game_id = row.get('game_id')
        player_id = str(row.get('player_id', ''))
        
        record = {
            'player_xy_key': f"PXW{game_id}{str(event_id)[-5:]}{str(player_id)[-4:]}",
            'event_id': event_id,
            'game_id': game_id,
            'player_id': player_id,
            'player_name': row.get('player_name'),
            'player_role': row.get('player_role'),
            'team_id': row.get('team_id'),
            'is_event_team': row.get('is_event_team'),
            'point_count': 0,
        }
        
        # Extract x1-x10, y1-y10 (handle variations like x_1, x1, etc.)
        populated_points = 0
        for i in POINT_NUMBERS:
            # Try multiple column name variations
            x_col = None
            y_col = None
            
            for variant in [f'x_{i}', f'x{i}', f'player_x_{i}', f'px_{i}']:
                if variant in df.columns:
                    x_col = variant
                    break
            
            for variant in [f'y_{i}', f'y{i}', f'player_y_{i}', f'py_{i}']:
                if variant in df.columns:
                    y_col = variant
                    break
            
            x_val = row.get(x_col) if x_col else None
            y_val = row.get(y_col) if y_col else None
            
            record[f'x_{i}'] = float(x_val) if pd.notna(x_val) else None
            record[f'y_{i}'] = float(y_val) if pd.notna(y_val) else None
            
            if pd.notna(x_val) and pd.notna(y_val):
                populated_points = i  # Track highest populated point
        
        record['point_count'] = populated_points
        
        # Get start and end points
        if populated_points > 0:
            record['x_start'] = record.get('x_1')
            record['y_start'] = record.get('y_1')
            record['x_end'] = record.get(f'x_{populated_points}')
            record['y_end'] = record.get(f'y_{populated_points}')
            
            # Calculate distances
            if record['x_start'] and record['x_end']:
                record['distance_traveled'] = np.sqrt(
                    (record['x_end'] - record['x_start'])**2 + 
                    (record['y_end'] - record['y_start'])**2
                )
            else:
                record['distance_traveled'] = None
            
            record['distance_to_net_start'] = calculate_distance_to_net(record['x_start'], record['y_start'])
            record['distance_to_net_end'] = calculate_distance_to_net(record['x_end'], record['y_end'])
        else:
            record['x_start'] = None
            record['y_start'] = None
            record['x_end'] = None
            record['y_end'] = None
            record['distance_traveled'] = None
            record['distance_to_net_start'] = None
            record['distance_to_net_end'] = None
        
        record['_export_timestamp'] = datetime.now().isoformat()
        records.append(record)
    
    result_df = pd.DataFrame(records)
    logger.info(f"  Created {len(result_df):,} player XY wide records")
    return result_df


def load_puck_xy_long(puck_xy_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load puck XY data in long format (one row per point per event).
    
    Expected columns:
    - event_id, game_id (required)
    - point_number (required, 1-10)
    - x, y (required)
    - is_stop (optional flag)
    """
    if puck_xy_path is None:
        default_paths = [
            Path('data/raw/xy_exports/puck_xy_long.csv'),
            Path('data/raw/xy_exports/puck_xy_export.csv'),
            Path('data/raw/xy_exports/puck_xy.csv'),
        ]
        for path in default_paths:
            if path.exists():
                puck_xy_path = path
                break
        
        if puck_xy_path is None:
            logger.info("  No puck XY export file found, skipping")
            return pd.DataFrame()
    
    df = load_xy_export(puck_xy_path)
    if len(df) == 0:
        return pd.DataFrame()
    
    # Normalize column names
    col_mapping = {
        'event_index': 'event_id',
        'event_key': 'event_id',
        'point_num': 'point_number',
        'coord_x': 'x',
        'coord_y': 'y',
        'puck_x': 'x',
        'puck_y': 'y',
    }
    
    for old_col, new_col in col_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df[new_col] = df[old_col]
    
    required = ['event_id', 'game_id', 'x', 'y']
    missing = [col for col in required if col not in df.columns]
    if missing:
        logger.error(f"  Missing required columns: {missing}")
        return pd.DataFrame()
    
    if 'point_number' not in df.columns:
        df['point_number'] = 1
    
    records = []
    for _, row in df.iterrows():
        event_id = str(row.get('event_id', ''))
        game_id = row.get('game_id')
        point_num = int(row.get('point_number', 1))
        x = row.get('x')
        y = row.get('y')
        
        if pd.isna(x) or pd.isna(y):
            continue
        
        record = {
            'puck_xy_key': f"PKL{game_id}{str(event_id)[-5:]}{point_num:02d}",
            'event_id': event_id,
            'game_id': game_id,
            'point_number': point_num,
            'x': float(x),
            'y': float(y),
            'distance_to_net': calculate_distance_to_net(float(x), float(y)),
            'angle_to_net': calculate_angle_to_net(float(x), float(y)),
            'is_stop': 1 if row.get('is_stop') == 1 or (row.get('is_stop_point') == True) else 0,
            'timestamp': row.get('timestamp'),
            '_export_timestamp': datetime.now().isoformat()
        }
        
        records.append(record)
    
    result_df = pd.DataFrame(records)
    logger.info(f"  Created {len(result_df):,} puck XY long records")
    return result_df


def load_puck_xy_wide(puck_xy_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load puck XY data in wide format (one row per event with puck_x1-puck_x10, puck_y1-puck_y10).
    
    Expected columns:
    - event_id, game_id (required)
    - puck_x_1, puck_y_1, ... puck_x_10, puck_y_10 (or variations)
    """
    if puck_xy_path is None:
        default_paths = [
            Path('data/raw/xy_exports/puck_xy_wide.csv'),
            Path('data/raw/xy_exports/puck_xy_export.csv'),
            Path('data/raw/xy_exports/puck_xy.csv'),
        ]
        for path in default_paths:
            if path.exists():
                puck_xy_path = path
                break
        
        if puck_xy_path is None:
            logger.info("  No puck XY export file found, skipping")
            return pd.DataFrame()
    
    df = load_xy_export(puck_xy_path)
    if len(df) == 0:
        return pd.DataFrame()
    
    # Normalize column names
    col_mapping = {
        'event_index': 'event_id',
        'event_key': 'event_id',
    }
    
    for old_col, new_col in col_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df[new_col] = df[old_col]
    
    if 'event_id' not in df.columns or 'game_id' not in df.columns:
        logger.error("  Missing required columns: event_id, game_id")
        return pd.DataFrame()
    
    records = []
    for _, row in df.iterrows():
        event_id = str(row.get('event_id', ''))
        game_id = row.get('game_id')
        
        record = {
            'puck_xy_key': f"PKW{game_id}{str(event_id)[-5:]}",
            'event_id': event_id,
            'game_id': game_id,
            'point_count': 0,
        }
        
        populated_points = 0
        for i in POINT_NUMBERS:
            # Try multiple column name variations
            x_col = None
            y_col = None
            
            for variant in [f'puck_x_{i}', f'puck_x{i}', f'x_{i}', f'x{i}']:
                if variant in df.columns:
                    x_col = variant
                    break
            
            for variant in [f'puck_y_{i}', f'puck_y{i}', f'y_{i}', f'y{i}']:
                if variant in df.columns:
                    y_col = variant
                    break
            
            x_val = row.get(x_col) if x_col else None
            y_val = row.get(y_col) if y_col else None
            
            record[f'puck_x_{i}'] = float(x_val) if pd.notna(x_val) else None
            record[f'puck_y_{i}'] = float(y_val) if pd.notna(y_val) else None
            
            if pd.notna(x_val) and pd.notna(y_val):
                populated_points = i
        
        record['point_count'] = populated_points
        
        # Get start and end points
        if populated_points > 0:
            record['puck_x_start'] = record.get('puck_x_1')
            record['puck_y_start'] = record.get('puck_y_1')
            record['puck_x_end'] = record.get(f'puck_x_{populated_points}')
            record['puck_y_end'] = record.get(f'puck_y_{populated_points}')
            
            if record['puck_x_start'] and record['puck_x_end']:
                record['distance_traveled'] = np.sqrt(
                    (record['puck_x_end'] - record['puck_x_start'])**2 + 
                    (record['puck_y_end'] - record['puck_y_start'])**2
                )
            else:
                record['distance_traveled'] = None
        else:
            record['puck_x_start'] = None
            record['puck_y_start'] = None
            record['puck_x_end'] = None
            record['puck_y_end'] = None
            record['distance_traveled'] = None
        
        record['_export_timestamp'] = datetime.now().isoformat()
        records.append(record)
    
    result_df = pd.DataFrame(records)
    logger.info(f"  Created {len(result_df):,} puck XY wide records")
    return result_df


def load_shot_xy(shot_xy_path: Optional[Path] = None, events: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Load shot XY data including net target location.
    
    Expected columns:
    - event_id, game_id, player_id (required)
    - shot_x, shot_y (required - where shot was taken from)
    - target_x, target_y (optional - net target location)
    - net_x, net_y (alternative to target_x/y)
    - net_location_id (optional - FK to dim_net_location)
    """
    # Load from export file if provided
    if shot_xy_path:
        df = load_xy_export(shot_xy_path)
    else:
        # Try default locations
        default_paths = [
            Path('data/raw/xy_exports/shot_xy_export.csv'),
            Path('data/raw/xy_exports/shot_xy.csv'),
        ]
        df = pd.DataFrame()
        for path in default_paths:
            if path.exists():
                df = load_xy_export(path)
                break
    
    # Also check events table for net_xy data
    if events is not None and len(events) > 0:
        shot_events = events[events['event_type'].isin(['Shot', 'Goal'])]
        if len(shot_events) > 0 and 'net_x' in shot_events.columns:
            # Merge with export data
            if len(df) > 0:
                df = pd.concat([df, shot_events[['event_id', 'game_id', 'net_x', 'net_y']]], ignore_index=True)
            else:
                df = shot_events[['event_id', 'game_id', 'net_x', 'net_y']].copy()
    
    if len(df) == 0:
        logger.info("  No shot XY data found")
        return pd.DataFrame()
    
    # Normalize column names
    col_mapping = {
        'event_index': 'event_id',
        'event_key': 'event_id',
        'player_key': 'player_id',
        'shooter_x': 'shot_x',
        'shooter_y': 'shot_y',
        'net_x': 'target_x',
        'net_y': 'target_y',
    }
    
    for old_col, new_col in col_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df[new_col] = df[old_col]
    
    required = ['event_id', 'game_id']
    missing = [col for col in required if col not in df.columns]
    if missing:
        logger.error(f"  Missing required columns: {missing}")
        return pd.DataFrame()
    
    records = []
    for _, row in df.iterrows():
        event_id = str(row.get('event_id', ''))
        game_id = row.get('game_id')
        player_id = str(row.get('player_id', ''))
        shot_x = row.get('shot_x')
        shot_y = row.get('shot_y')
        target_x = row.get('target_x')
        target_y = row.get('target_y')
        
        if pd.isna(shot_x) or pd.isna(shot_y):
            continue
        
        # Calculate distance and angle
        distance = calculate_distance_to_net(float(shot_x), float(shot_y))
        angle = calculate_angle_to_net(float(shot_x), float(shot_y))
        
        # Determine danger zone from distance
        if distance:
            if distance < 15:
                danger_zone = 'high'
            elif distance < 30:
                danger_zone = 'medium'
            else:
                danger_zone = 'low'
        else:
            danger_zone = None
        
        record = {
            'shot_xy_key': f"SXY{game_id}{str(event_id)[-5:]}",
            'game_id': game_id,
            'event_id': event_id,
            'player_id': player_id,
            'shot_x': float(shot_x),
            'shot_y': float(shot_y),
            'target_x': float(target_x) if pd.notna(target_x) else None,
            'target_y': float(target_y) if pd.notna(target_y) else None,
            'distance': distance,
            'angle': angle,
            'danger_zone': danger_zone,
            'net_location_id': row.get('net_location_id'),
            '_export_timestamp': datetime.now().isoformat()
        }
        
        records.append(record)
    
    result_df = pd.DataFrame(records)
    logger.info(f"  Created {len(result_df):,} shot XY records")
    return result_df


def load_all_xy_data(
    player_xy_path: Optional[Path] = None,
    puck_xy_path: Optional[Path] = None,
    shot_xy_path: Optional[Path] = None,
    events: Optional[pd.DataFrame] = None
) -> Dict[str, int]:
    """
    Load all XY data from export files and save to output tables.
    
    Returns:
        Dictionary with table names and row counts
    """
    logger.info("\n" + "=" * 70)
    logger.info("XY ETL LOADER - Loading XY data from exports")
    logger.info("=" * 70)
    
    results = {}
    
    # Load player XY
    logger.info("\n--- Player XY Tables ---")
    player_long = load_player_xy_long(player_xy_path)
    if len(player_long) > 0:
        save_output_table(player_long, 'fact_player_xy_long', OUTPUT_DIR)
        results['fact_player_xy_long'] = len(player_long)
    
    player_wide = load_player_xy_wide(player_xy_path)
    if len(player_wide) > 0:
        save_output_table(player_wide, 'fact_player_xy_wide', OUTPUT_DIR)
        results['fact_player_xy_wide'] = len(player_wide)
    
    # Load puck XY
    logger.info("\n--- Puck XY Tables ---")
    puck_long = load_puck_xy_long(puck_xy_path)
    if len(puck_long) > 0:
        save_output_table(puck_long, 'fact_puck_xy_long', OUTPUT_DIR)
        results['fact_puck_xy_long'] = len(puck_long)
    
    puck_wide = load_puck_xy_wide(puck_xy_path)
    if len(puck_wide) > 0:
        save_output_table(puck_wide, 'fact_puck_xy_wide', OUTPUT_DIR)
        results['fact_puck_xy_wide'] = len(puck_wide)
    
    # Load shot XY
    logger.info("\n--- Shot XY Table ---")
    shot_xy = load_shot_xy(shot_xy_path, events)
    if len(shot_xy) > 0:
        save_output_table(shot_xy, 'fact_shot_xy', OUTPUT_DIR)
        results['fact_shot_xy'] = len(shot_xy)
    
    logger.info("\n" + "=" * 70)
    logger.info("XY ETL LOADER COMPLETE")
    logger.info("=" * 70)
    total_rows = sum(results.values())
    logger.info(f"Tables created: {len(results)}")
    logger.info(f"Total rows: {total_rows:,}")
    
    return results


if __name__ == '__main__':
    load_all_xy_data()
