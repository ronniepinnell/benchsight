"""
=============================================================================
XY COORDINATE DATA LOADER - REAL DATA FORMAT
=============================================================================
File: src/pipeline/stage/load_xy_data.py

PURPOSE:
    Load actual XY coordinate data from CSV files in the xy/event_locations folder.
    Handle the real data format with player tracking, puck location, and movement.

XY DATA FORMAT:
    game_id, link_event_index, Player, X, Y, X2, Y2, X3, Y3, Distance
    
    Player values:
        - Number (e.g., 52, 49) = player's game number
        - 'p' = puck location
        - If 'team' column exists and is not blank: use for disambiguation
    
KEY GENERATION:
    - If team is blank: use game_id + linked_event_index + game_number
    - If team is not blank: use game_id + linked_event_index + game_number + team
    - For puck: use 'P' as player identifier

=============================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import math

from src.database.connection import execute_sql
from src.database.table_operations import (
    load_dataframe_to_table,
    table_exists,
    get_row_count,
    read_query,
    drop_table
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_xy_data_for_game(game_id: int, game_dir: Path) -> Dict[str, int]:
    """
    Load XY coordinate data from CSV files.
    
    Args:
        game_id: Game identifier
        game_dir: Path to game folder
    
    Returns:
        Dictionary with row counts
    """
    logger.info(f"Loading XY data for game {game_id}")
    
    results = {}
    
    # Check for event locations
    xy_dir = game_dir / 'xy' / 'event_locations'
    if xy_dir.exists():
        xy_events = _load_xy_event_locations(game_id, xy_dir)
        if len(xy_events) > 0:
            load_dataframe_to_table(xy_events, f'stg_xy_events_{game_id}', 'replace')
            results['xy_events'] = len(xy_events)
            logger.info(f"  Loaded {len(xy_events)} XY event records")
    
    # Check for shots
    shots_dir = game_dir / 'shots'
    if shots_dir.exists():
        shots = _load_shots_data(game_id, shots_dir)
        if len(shots) > 0:
            load_dataframe_to_table(shots, f'stg_xy_shots_{game_id}', 'replace')
            results['xy_shots'] = len(shots)
            logger.info(f"  Loaded {len(shots)} shot records")
    
    return results


def _load_xy_event_locations(game_id: int, xy_dir: Path) -> pd.DataFrame:
    """
    Load all XY event location CSV files and combine.
    
    Format: game_id, link_event_index, Player, X, Y, X2, Y2, X3, Y3, Distance
    """
    all_records = []
    
    for csv_file in xy_dir.glob('*.csv'):
        if csv_file.name.startswith('~') or csv_file.name.startswith('.'):
            continue
        
        try:
            df = pd.read_csv(csv_file)
            
            # Normalize column names
            df.columns = [c.lower().strip() for c in df.columns]
            
            for idx, row in df.iterrows():
                # Get player identifier
                player = str(row.get('player', '')).strip()
                is_puck = player.lower() == 'p'
                
                # Get team if exists
                team = str(row.get('team', '')).strip() if 'team' in df.columns else ''
                
                # Get linked event index
                linked_event = row.get('link_event_index') or row.get('linked_event_index')
                
                # Get coordinates
                x1 = _safe_float(row.get('x'))
                y1 = _safe_float(row.get('y'))
                x2 = _safe_float(row.get('x2'))
                y2 = _safe_float(row.get('y2'))
                x3 = _safe_float(row.get('x3'))
                y3 = _safe_float(row.get('y3'))
                
                # Get or calculate distance
                distance = _safe_float(row.get('distance'))
                if distance is None and x1 is not None and x2 is not None:
                    distance = _calculate_distance(x1, y1, x2, y2)
                
                # Calculate angle (from first position to goal at x=89)
                angle = None
                if x1 is not None and y1 is not None:
                    angle = _calculate_shot_angle(x1, y1)
                
                # Generate key
                if is_puck:
                    player_key = 'P'
                else:
                    player_key = player
                
                if team and team.lower() in ['e', 'o', 'event', 'opp']:
                    xy_key = f"XY{game_id:05d}{int(linked_event):05d}{player_key}{team[0].upper()}"
                else:
                    xy_key = f"XY{game_id:05d}{int(linked_event):05d}{player_key}"
                
                record = {
                    'xy_key': xy_key,
                    'game_id': game_id,
                    'linked_event_index': int(linked_event) if pd.notna(linked_event) else None,
                    'player': player,
                    'is_puck': 1 if is_puck else 0,
                    'team': team if team else None,
                    'x1': x1,
                    'y1': y1,
                    'x2': x2,
                    'y2': y2,
                    'x3': x3,
                    'y3': y3,
                    'distance': distance,
                    'angle': angle,
                    'source_file': csv_file.name,
                    '_load_timestamp': datetime.now().isoformat()
                }
                all_records.append(record)
                
        except Exception as e:
            logger.warning(f"Error reading {csv_file}: {e}")
    
    return pd.DataFrame(all_records) if all_records else pd.DataFrame()


def _load_shots_data(game_id: int, shots_dir: Path) -> pd.DataFrame:
    """
    Load all shots CSV files and combine.
    
    Format: event_index, X, Y
    """
    all_records = []
    
    for csv_file in shots_dir.glob('*.csv'):
        if csv_file.name.startswith('~') or csv_file.name.startswith('.'):
            continue
        
        try:
            df = pd.read_csv(csv_file)
            
            # Normalize column names
            df.columns = [c.lower().strip() for c in df.columns]
            
            for idx, row in df.iterrows():
                event_index = row.get('event_index')
                x = _safe_float(row.get('x'))
                y = _safe_float(row.get('y'))
                
                # Calculate distance and angle to goal
                distance = None
                angle = None
                if x is not None and y is not None:
                    distance = _calculate_distance(x, y, 89, 0)  # Goal at x=89, y=0
                    angle = _calculate_shot_angle(x, y)
                
                # Generate key
                shot_key = f"XS{game_id:05d}{int(event_index):05d}"
                
                record = {
                    'shot_key': shot_key,
                    'game_id': game_id,
                    'event_index': int(event_index) if pd.notna(event_index) else None,
                    'x': x,
                    'y': y,
                    'distance': distance,
                    'angle': angle,
                    'source_file': csv_file.name,
                    '_load_timestamp': datetime.now().isoformat()
                }
                all_records.append(record)
                
        except Exception as e:
            logger.warning(f"Error reading {csv_file}: {e}")
    
    return pd.DataFrame(all_records) if all_records else pd.DataFrame()


def _safe_float(val) -> Optional[float]:
    """Safely convert to float, returning None for invalid values."""
    if pd.isna(val):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points."""
    if x1 is None or y1 is None or x2 is None or y2 is None:
        return None
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def _calculate_shot_angle(x: float, y: float, goal_x: float = 89) -> float:
    """
    Calculate angle from position to center of goal.
    
    Args:
        x, y: Position coordinates
        goal_x: X position of goal line (default 89)
    
    Returns:
        Angle in degrees from the goal line
    """
    if x is None or y is None:
        return None
    
    # Distance from goal line
    dx = goal_x - abs(x)  # Handle both offensive zones
    
    # Angle from center of goal
    if dx <= 0:
        return 90.0  # Behind goal line
    
    angle = math.degrees(math.atan(abs(y) / dx))
    return round(angle, 2)


def transform_xy_to_intermediate(game_id: int) -> Dict[str, int]:
    """
    Transform XY stage data to intermediate with FK lookups.
    
    Args:
        game_id: Game identifier
    
    Returns:
        Dictionary with row counts
    """
    logger.info(f"Transforming XY data for game {game_id}")
    results = {}
    
    # Transform XY events
    if table_exists(f'stg_xy_events_{game_id}'):
        drop_table(f'int_xy_events_{game_id}')
        
        # Join with events to get event details and player info
        execute_sql(f"""
            CREATE TABLE int_xy_events_{game_id} AS
            SELECT
                xy.xy_key,
                xy.game_id,
                xy.linked_event_index,
                'LK' || printf('%05d', xy.game_id) || printf('%05d', xy.linked_event_index) AS linked_event_key,
                xy.player AS player_game_number,
                xy.is_puck,
                xy.team,
                xy.x1, xy.y1, xy.x2, xy.y2, xy.x3, xy.y3,
                xy.distance,
                xy.angle,
                e.event_type,
                e.event_detail,
                e.period,
                e.time_total_seconds,
                gp.player_id,
                CASE 
                    WHEN xy.x1 >= 25 THEN 'O'
                    WHEN xy.x1 <= -25 THEN 'D'
                    ELSE 'N'
                END AS zone,
                rb.box_id AS rink_box_id,
                rb.danger AS rink_danger,
                rz.box_id AS rink_zone_id,
                xy.source_file,
                datetime('now') AS _processed_timestamp
            FROM stg_xy_events_{game_id} xy
            LEFT JOIN int_events_{game_id} e 
                ON xy.linked_event_index = e.linked_event_index
                OR xy.linked_event_index = e.event_index
            LEFT JOIN int_game_players_{game_id} gp 
                ON CAST(xy.player AS TEXT) = CAST(gp.player_game_number AS TEXT)
            LEFT JOIN stg_dim_rinkboxcoord rb
                ON xy.x1 >= rb.x_min AND xy.x1 < rb.x_max
                AND xy.y1 >= rb.y_min AND xy.y1 < rb.y_max
            LEFT JOIN stg_dim_rinkcoordzones rz
                ON xy.x1 >= rz.x_min AND xy.x1 < rz.x_max
                AND xy.y1 >= rz.y_min AND xy.y1 < rz.y_max
        """)
        
        results['int_xy_events'] = get_row_count(f'int_xy_events_{game_id}')
    
    # Transform shots
    if table_exists(f'stg_xy_shots_{game_id}'):
        drop_table(f'int_xy_shots_{game_id}')
        
        execute_sql(f"""
            CREATE TABLE int_xy_shots_{game_id} AS
            SELECT
                s.shot_key,
                s.game_id,
                s.event_index,
                'EV' || printf('%05d', s.game_id) || printf('%05d', s.event_index) AS event_key,
                s.x, s.y,
                s.distance,
                s.angle,
                e.event_type,
                e.event_detail,
                e.period,
                e.time_total_seconds,
                CASE WHEN LOWER(e.event_type) LIKE '%goal%' THEN 1 ELSE 0 END AS is_goal,
                rb.box_id AS rink_box_id,
                rb.danger AS rink_danger,
                rz.box_id AS rink_zone_id,
                s.source_file,
                datetime('now') AS _processed_timestamp
            FROM stg_xy_shots_{game_id} s
            LEFT JOIN int_events_{game_id} e 
                ON s.event_index = e.event_index
            LEFT JOIN stg_dim_rinkboxcoord rb
                ON s.x >= rb.x_min AND s.x < rb.x_max
                AND s.y >= rb.y_min AND s.y < rb.y_max
            LEFT JOIN stg_dim_rinkcoordzones rz
                ON s.x >= rz.x_min AND s.x < rz.x_max
                AND s.y >= rz.y_min AND s.y < rz.y_max
        """)
        
        results['int_xy_shots'] = get_row_count(f'int_xy_shots_{game_id}')
    
    return results


def publish_xy_to_datamart(game_id: int) -> Dict[str, int]:
    """
    Publish XY data to datamart fact tables.
    
    Args:
        game_id: Game identifier
    
    Returns:
        Dictionary with row counts
    """
    results = {}
    
    # Create fact_xy_events if needed
    execute_sql("""
        CREATE TABLE IF NOT EXISTS fact_xy_events (
            xy_key TEXT PRIMARY KEY,
            game_id INTEGER NOT NULL,
            linked_event_index INTEGER,
            linked_event_key TEXT,
            player_game_number TEXT,
            player_id INTEGER,
            is_puck INTEGER,
            team TEXT,
            x1 REAL, y1 REAL, x2 REAL, y2 REAL, x3 REAL, y3 REAL,
            distance REAL,
            angle REAL,
            event_type TEXT,
            event_detail TEXT,
            period INTEGER,
            time_total_seconds REAL,
            zone TEXT,
            rink_box_id TEXT,
            rink_danger TEXT,
            rink_zone_id TEXT,
            source_file TEXT,
            _processed_timestamp TEXT
        )
    """)
    
    # Delete existing
    execute_sql("DELETE FROM fact_xy_events WHERE game_id = :gid", {'gid': game_id})
    
    # Insert
    if table_exists(f'int_xy_events_{game_id}'):
        execute_sql(f"""
            INSERT INTO fact_xy_events
            SELECT * FROM int_xy_events_{game_id}
        """)
        results['fact_xy_events'] = get_row_count('fact_xy_events')
    
    # Create fact_xy_shots if needed
    execute_sql("""
        CREATE TABLE IF NOT EXISTS fact_xy_shots (
            shot_key TEXT PRIMARY KEY,
            game_id INTEGER NOT NULL,
            event_index INTEGER,
            event_key TEXT,
            x REAL, y REAL,
            distance REAL,
            angle REAL,
            event_type TEXT,
            event_detail TEXT,
            period INTEGER,
            time_total_seconds REAL,
            is_goal INTEGER,
            rink_box_id TEXT,
            rink_danger TEXT,
            rink_zone_id TEXT,
            source_file TEXT,
            _processed_timestamp TEXT
        )
    """)
    
    # Delete existing
    execute_sql("DELETE FROM fact_xy_shots WHERE game_id = :gid", {'gid': game_id})
    
    # Insert
    if table_exists(f'int_xy_shots_{game_id}'):
        execute_sql(f"""
            INSERT INTO fact_xy_shots
            SELECT * FROM int_xy_shots_{game_id}
        """)
        results['fact_xy_shots'] = get_row_count('fact_xy_shots')
    
    return results
