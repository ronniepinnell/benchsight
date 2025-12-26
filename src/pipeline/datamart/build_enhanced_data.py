"""
=============================================================================
COMPREHENSIVE DATA ENHANCEMENT MODULE
=============================================================================
File: src/pipeline/datamart/build_enhanced_data.py

PURPOSE:
    1. Standardize all keys across the system
    2. Generate XY coordinate data with FK relationships
    3. Process video reference data
    4. Link to rink coordinate dimensions

KEY FORMAT STANDARD:
    All keys follow pattern: {PREFIX}{GAME_ID:05d}{INDEX:05d}
    Total length: 12 characters (2 prefix + 5 game + 5 index)
    
    PREFIX CODES (2 characters):
        EV = Event
        SH = Shift  
        EP = Event Player
        GP = Game Player
        SQ = Sequence
        PL = Play
        LK = Linked Event
        BS = Box Score (Player Game)
        XY = XY Event Location
        XS = XY Shot Location
        VD = Video
    
    Examples:
        EV1896900001 = Event 1 from game 18969
        SH1896900025 = Shift 25 from game 18969
        XY1896900100 = XY Event 100 from game 18969
        LK1896900050 = Linked Event 50 from game 18969

COORDINATE SYSTEM:
    X: -100 to 100 (center ice = 0, goals at +/-89)
    Y: -42.5 to 42.5 (center ice = 0)
    
    Note: Using standard NHL coordinate system where:
    - Offensive zone: X > 25 (for home team attacking right)
    - Defensive zone: X < -25
    - Neutral zone: -25 <= X <= 25

=============================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from datetime import datetime
import random

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


# =============================================================================
# KEY GENERATION CONSTANTS AND FUNCTIONS
# =============================================================================

KEY_PREFIX = {
    'event': 'EV',
    'shift': 'SH',
    'event_player': 'EP',
    'game_player': 'GP',
    'sequence': 'SQ',
    'play': 'PL',
    'linked': 'LK',
    'box_score': 'BS',
    'xy_event': 'XY',
    'xy_shot': 'XS',
    'video': 'VD',
}


def generate_key(prefix: str, game_id: int, index: int) -> str:
    """
    Generate standardized key.
    
    Format: {PREFIX:2}{GAME_ID:05d}{INDEX:05d}
    Total: 12 characters
    
    Args:
        prefix: 2-character prefix code
        game_id: Game identifier (will be zero-padded to 5 digits)
        index: Row/record index (will be zero-padded to 5 digits)
    
    Returns:
        Standardized key string (12 characters)
    
    Examples:
        generate_key('EV', 18969, 1) -> 'EV1896900001'
        generate_key('SQ', 18969, 42) -> 'SQ1896900042'
    """
    return f"{prefix}{game_id:05d}{index:05d}"


def parse_key(key: str) -> Tuple[str, int, int]:
    """
    Parse a standardized key back to components.
    
    Args:
        key: Standardized key string (12 chars)
    
    Returns:
        Tuple of (prefix, game_id, index)
    """
    if not key or len(key) != 12:
        return None, None, None
    prefix = key[:2]
    game_id = int(key[2:7])
    index = int(key[7:12])
    return prefix, game_id, index


# =============================================================================
# RINK COORDINATE LOOKUP
# =============================================================================

def get_rink_box_for_coords(x: float, y: float) -> Optional[str]:
    """
    Find the rink box_id that contains the given coordinates.
    
    Args:
        x: X coordinate (-100 to 100)
        y: Y coordinate (-42.5 to 42.5)
    
    Returns:
        box_id string or None if not found
    """
    if not table_exists('stg_dim_rinkboxcoord'):
        return None
    
    # Query for matching box
    df = read_query(f"""
        SELECT box_id 
        FROM stg_dim_rinkboxcoord
        WHERE {x} >= x_min AND {x} < x_max
          AND {y} >= y_min AND {y} < y_max
        LIMIT 1
    """)
    
    if len(df) > 0:
        return df.iloc[0]['box_id']
    return None


def get_rink_zone_for_coords(x: float, y: float) -> Optional[str]:
    """
    Find the rink zone box_id that contains the given coordinates.
    
    Args:
        x: X coordinate (-100 to 100)
        y: Y coordinate (-42.5 to 42.5)
    
    Returns:
        box_id string or None if not found
    """
    if not table_exists('stg_dim_rinkcoordzones'):
        return None
    
    # Query for matching zone
    df = read_query(f"""
        SELECT box_id, danger, zone, side
        FROM stg_dim_rinkcoordzones
        WHERE {x} >= x_min AND {x} < x_max
          AND {y} >= y_min AND {y} < y_max
        LIMIT 1
    """)
    
    if len(df) > 0:
        return df.iloc[0]['box_id']
    return None


def lookup_all_rink_coords(x: float, y: float) -> Dict:
    """
    Get all rink coordinate info for a point.
    
    Returns dict with box_id, zone_id, danger, zone_name, side
    """
    result = {
        'rink_box_id': None,
        'rink_zone_id': None,
        'danger': 'LOW',
        'zone_name': 'neutral',
        'side': 'center'
    }
    
    # Try to get from rinkboxcoord
    if table_exists('stg_dim_rinkboxcoord'):
        df = read_query(f"""
            SELECT box_id, danger, zone, side
            FROM stg_dim_rinkboxcoord
            WHERE {x} >= x_min AND {x} < x_max
              AND {y} >= y_min AND {y} < y_max
            LIMIT 1
        """)
        if len(df) > 0:
            result['rink_box_id'] = df.iloc[0]['box_id']
            result['danger'] = df.iloc[0].get('danger', 'LOW')
            result['zone_name'] = df.iloc[0].get('zone', 'neutral')
            result['side'] = df.iloc[0].get('side', 'center')
    
    # Try to get from rinkcoordzones
    if table_exists('stg_dim_rinkcoordzones'):
        df = read_query(f"""
            SELECT box_id
            FROM stg_dim_rinkcoordzones
            WHERE {x} >= x_min AND {x} < x_max
              AND {y} >= y_min AND {y} < y_max
            LIMIT 1
        """)
        if len(df) > 0:
            result['rink_zone_id'] = df.iloc[0]['box_id']
    
    return result


# =============================================================================
# XY COORDINATE DATA GENERATION
# =============================================================================

def generate_xy_data_for_game(game_id: int, force: bool = False) -> Dict[str, int]:
    """
    Generate XY coordinate data for all events in a game.
    
    Creates:
        - stg_xy_events_{game_id}: All events with coordinates
        - stg_xy_shots_{game_id}: Shot events with additional metrics
        - int_xy_events_{game_id}: Transformed with FKs
        - int_xy_shots_{game_id}: Transformed with FKs
        - Updates fact_xy_events and fact_xy_shots
    
    Args:
        game_id: Game identifier
        force: If True, regenerate even if exists
    
    Returns:
        Dictionary with row counts per table
    """
    logger.info(f"Generating XY coordinate data for game {game_id}")
    
    # Check prerequisites
    if not table_exists(f'int_events_{game_id}'):
        raise RuntimeError(f"int_events_{game_id} not found. Run intermediate transform first.")
    
    # Check if already exists
    if table_exists(f'stg_xy_events_{game_id}') and not force:
        logger.info(f"XY data already exists for game {game_id}. Use force=True to regenerate.")
        return _get_xy_counts(game_id)
    
    results = {}
    
    # Load events
    events_df = read_query(f"SELECT * FROM int_events_{game_id}")
    logger.info(f"Processing {len(events_df)} events for XY generation")
    
    # Generate XY events
    xy_events_df = _create_xy_events(game_id, events_df)
    load_dataframe_to_table(xy_events_df, f'stg_xy_events_{game_id}', 'replace')
    results['stg_xy_events'] = len(xy_events_df)
    
    # Generate XY shots (subset)
    xy_shots_df = _create_xy_shots(game_id, events_df)
    if len(xy_shots_df) > 0:
        load_dataframe_to_table(xy_shots_df, f'stg_xy_shots_{game_id}', 'replace')
        results['stg_xy_shots'] = len(xy_shots_df)
    
    # Transform to intermediate
    _transform_xy_intermediate(game_id)
    results['int_xy_events'] = get_row_count(f'int_xy_events_{game_id}') if table_exists(f'int_xy_events_{game_id}') else 0
    results['int_xy_shots'] = get_row_count(f'int_xy_shots_{game_id}') if table_exists(f'int_xy_shots_{game_id}') else 0
    
    # Publish to datamart
    _publish_xy_datamart(game_id)
    
    logger.info(f"XY data generated: {results}")
    return results


def _create_xy_events(game_id: int, events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create XY coordinate data for all events.
    
    Coordinates are generated based on event_team_zone:
        O (Offensive): x in [25, 89]
        D (Defensive): x in [-89, -25]
        N (Neutral): x in [-25, 25]
    """
    np.random.seed(game_id)  # Reproducible
    
    records = []
    
    for idx, row in events_df.iterrows():
        event_index = int(row.get('event_index', 0))
        zone = str(row.get('event_team_zone', 'N')).upper()
        linked_event = row.get('linked_event_index')
        
        # Determine X range based on zone
        if zone.startswith('O'):
            x_range = (25, 89)
        elif zone.startswith('D'):
            x_range = (-89, -25)
        else:
            x_range = (-25, 25)
        
        # Generate coordinates
        x = np.random.uniform(x_range[0], x_range[1])
        y = np.random.uniform(-42, 42)
        
        # Look up rink coordinates
        rink_info = lookup_all_rink_coords(x, y)
        
        # Create linked key if linked_event exists
        linked_key = None
        if pd.notna(linked_event) and linked_event > 0:
            linked_key = generate_key('LK', game_id, int(linked_event))
        
        records.append({
            'xy_event_index': idx,
            'xy_event_key': generate_key('XY', game_id, idx),
            'event_index': event_index,
            'event_key': generate_key('EV', game_id, event_index),
            'linked_event_index': int(linked_event) if pd.notna(linked_event) else None,
            'linked_event_key': linked_key,
            'game_id': game_id,
            'x_coord': round(x, 2),
            'y_coord': round(y, 2),
            'rink_box_id': rink_info['rink_box_id'],
            'rink_zone_id': rink_info['rink_zone_id'],
            'danger': rink_info['danger'],
            'zone_name': rink_info['zone_name'],
            'side': rink_info['side'],
            '_load_timestamp': datetime.now().isoformat()
        })
    
    return pd.DataFrame(records)


def _create_xy_shots(game_id: int, events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create XY coordinate data for shot events.
    
    Shots are in offensive zone with additional metrics:
        - shot_distance: Distance to goal
        - shot_angle: Angle to goal
    """
    np.random.seed(game_id + 1000)
    
    # Filter shot events
    shot_keywords = ['shot', 'goal', 'save', 'miss', 'block']
    shot_mask = events_df['event_type'].str.lower().apply(
        lambda x: any(kw in str(x).lower() for kw in shot_keywords)
    )
    shot_events = events_df[shot_mask]
    
    if len(shot_events) == 0:
        return pd.DataFrame()
    
    records = []
    goal_x = 89  # Goal line position
    
    for idx, (orig_idx, row) in enumerate(shot_events.iterrows()):
        event_index = int(row.get('event_index', 0))
        linked_event = row.get('linked_event_index')
        
        # Shots cluster near the goal
        x = np.random.uniform(50, 88)  # In offensive zone
        y = np.random.normal(0, 15)  # Centered distribution
        y = np.clip(y, -42, 42)
        
        # Calculate shot metrics
        shot_distance = np.sqrt((goal_x - x)**2 + y**2)
        shot_angle = np.degrees(np.arctan2(abs(y), goal_x - x))
        
        # Is this a goal?
        is_goal = 1 if 'goal' in str(row.get('event_type', '')).lower() else 0
        
        # Rink lookup
        rink_info = lookup_all_rink_coords(x, y)
        
        # Linked key
        linked_key = None
        if pd.notna(linked_event) and linked_event > 0:
            linked_key = generate_key('LK', game_id, int(linked_event))
        
        records.append({
            'xy_shot_index': idx,
            'xy_shot_key': generate_key('XS', game_id, idx),
            'event_index': event_index,
            'event_key': generate_key('EV', game_id, event_index),
            'linked_event_index': int(linked_event) if pd.notna(linked_event) else None,
            'linked_event_key': linked_key,
            'game_id': game_id,
            'x_coord': round(x, 2),
            'y_coord': round(y, 2),
            'shot_distance': round(shot_distance, 2),
            'shot_angle': round(shot_angle, 2),
            'is_goal': is_goal,
            'rink_box_id': rink_info['rink_box_id'],
            'rink_zone_id': rink_info['rink_zone_id'],
            'danger': rink_info['danger'],
            '_load_timestamp': datetime.now().isoformat()
        })
    
    return pd.DataFrame(records)


def _transform_xy_intermediate(game_id: int) -> None:
    """Transform XY data to intermediate layer with FK joins."""
    
    # int_xy_events
    drop_table(f'int_xy_events_{game_id}')
    execute_sql(f"""
        CREATE TABLE int_xy_events_{game_id} AS
        SELECT
            xy.xy_event_index,
            xy.xy_event_key,
            xy.event_index,
            xy.event_key,
            xy.linked_event_index,
            xy.linked_event_key,
            xy.game_id,
            xy.x_coord,
            xy.y_coord,
            xy.rink_box_id,
            xy.rink_zone_id,
            xy.danger,
            xy.zone_name,
            xy.side,
            e.event_type,
            e.event_detail,
            e.period,
            e.time_total_seconds,
            datetime('now') AS _processed_timestamp
        FROM stg_xy_events_{game_id} xy
        LEFT JOIN int_events_{game_id} e 
            ON xy.event_index = e.event_index
    """)
    
    # int_xy_shots
    if table_exists(f'stg_xy_shots_{game_id}'):
        drop_table(f'int_xy_shots_{game_id}')
        execute_sql(f"""
            CREATE TABLE int_xy_shots_{game_id} AS
            SELECT
                xy.xy_shot_index,
                xy.xy_shot_key,
                xy.event_index,
                xy.event_key,
                xy.linked_event_index,
                xy.linked_event_key,
                xy.game_id,
                xy.x_coord,
                xy.y_coord,
                xy.shot_distance,
                xy.shot_angle,
                xy.is_goal,
                xy.rink_box_id,
                xy.rink_zone_id,
                xy.danger,
                e.event_type,
                e.event_detail,
                e.period,
                e.time_total_seconds,
                datetime('now') AS _processed_timestamp
            FROM stg_xy_shots_{game_id} xy
            LEFT JOIN int_events_{game_id} e 
                ON xy.event_index = e.event_index
        """)


def _publish_xy_datamart(game_id: int) -> None:
    """Publish XY data to datamart fact tables."""
    
    # Create fact_xy_events if not exists
    execute_sql("""
        CREATE TABLE IF NOT EXISTS fact_xy_events (
            xy_event_key TEXT PRIMARY KEY,
            xy_event_index INTEGER NOT NULL,
            event_key TEXT,
            event_index INTEGER,
            linked_event_index INTEGER,
            linked_event_key TEXT,
            game_id INTEGER NOT NULL,
            x_coord REAL,
            y_coord REAL,
            rink_box_id TEXT,
            rink_zone_id TEXT,
            danger TEXT,
            zone_name TEXT,
            side TEXT,
            event_type TEXT,
            event_detail TEXT,
            period INTEGER,
            time_total_seconds REAL,
            _processed_timestamp TEXT
        )
    """)
    
    # Delete existing for this game
    execute_sql("DELETE FROM fact_xy_events WHERE game_id = :gid", {'gid': game_id})
    
    # Insert from intermediate with explicit column mapping
    if table_exists(f'int_xy_events_{game_id}'):
        execute_sql(f"""
            INSERT INTO fact_xy_events (
                xy_event_key, xy_event_index, event_key, event_index,
                linked_event_index, linked_event_key, game_id,
                x_coord, y_coord, rink_box_id, rink_zone_id,
                danger, zone_name, side, event_type, event_detail,
                period, time_total_seconds, _processed_timestamp
            )
            SELECT 
                xy_event_key, xy_event_index, event_key, event_index,
                linked_event_index, linked_event_key, game_id,
                x_coord, y_coord, rink_box_id, rink_zone_id,
                danger, zone_name, side, event_type, event_detail,
                period, time_total_seconds, _processed_timestamp
            FROM int_xy_events_{game_id}
        """)
    
    # Create fact_xy_shots if not exists
    execute_sql("""
        CREATE TABLE IF NOT EXISTS fact_xy_shots (
            xy_shot_key TEXT PRIMARY KEY,
            xy_shot_index INTEGER NOT NULL,
            event_key TEXT,
            event_index INTEGER,
            linked_event_index INTEGER,
            linked_event_key TEXT,
            game_id INTEGER NOT NULL,
            x_coord REAL,
            y_coord REAL,
            shot_distance REAL,
            shot_angle REAL,
            is_goal INTEGER,
            rink_box_id TEXT,
            rink_zone_id TEXT,
            danger TEXT,
            event_type TEXT,
            event_detail TEXT,
            period INTEGER,
            time_total_seconds REAL,
            _processed_timestamp TEXT
        )
    """)
    
    # Delete existing for this game
    execute_sql("DELETE FROM fact_xy_shots WHERE game_id = :gid", {'gid': game_id})
    
    # Insert from intermediate with explicit column mapping
    if table_exists(f'int_xy_shots_{game_id}'):
        execute_sql(f"""
            INSERT INTO fact_xy_shots (
                xy_shot_key, xy_shot_index, event_key, event_index,
                linked_event_index, linked_event_key, game_id,
                x_coord, y_coord, shot_distance, shot_angle, is_goal,
                rink_box_id, rink_zone_id, danger,
                event_type, event_detail, period, time_total_seconds,
                _processed_timestamp
            )
            SELECT 
                xy_shot_key, xy_shot_index, event_key, event_index,
                linked_event_index, linked_event_key, game_id,
                x_coord, y_coord, shot_distance, shot_angle, is_goal,
                rink_box_id, rink_zone_id, danger,
                event_type, event_detail, period, time_total_seconds,
                _processed_timestamp
            FROM int_xy_shots_{game_id}
        """)


def _get_xy_counts(game_id: int) -> Dict[str, int]:
    """Get row counts for existing XY tables."""
    counts = {}
    for table in [f'stg_xy_events_{game_id}', f'stg_xy_shots_{game_id}',
                  f'int_xy_events_{game_id}', f'int_xy_shots_{game_id}']:
        if table_exists(table):
            counts[table.replace(f'_{game_id}', '')] = get_row_count(table)
    return counts


# =============================================================================
# VIDEO DATA GENERATION
# =============================================================================

def generate_video_data_for_game(game_id: int) -> Dict[str, int]:
    """
    Generate mock video reference data for a game.
    
    Creates video records for:
        - Main game video
        - Period highlights
        - Goal clips
    
    Args:
        game_id: Game identifier
    
    Returns:
        Dictionary with row counts
    """
    logger.info(f"Generating video data for game {game_id}")
    
    records = []
    video_idx = 0
    
    # Main game video
    records.append({
        'video_index': video_idx,
        'video_key': generate_key('VD', game_id, video_idx),
        'game_id': game_id,
        'video_type': 'full_game',
        'video_category': 'main',
        'url_primary': f'https://video.example.com/games/{game_id}/full',
        'url_backup': f'https://backup.example.com/games/{game_id}/full',
        'url_embed': f'https://embed.example.com/v/{game_id}',
        'video_id': f'VID_{game_id}_FULL',
        'extension': 'mp4',
        'description': f'Full game video for game {game_id}',
        'duration_seconds': 7200,  # 2 hours
        'start_offset': 0,
        '_load_timestamp': datetime.now().isoformat()
    })
    video_idx += 1
    
    # Period videos
    for period in [1, 2, 3]:
        records.append({
            'video_index': video_idx,
            'video_key': generate_key('VD', game_id, video_idx),
            'game_id': game_id,
            'video_type': 'period',
            'video_category': f'period_{period}',
            'url_primary': f'https://video.example.com/games/{game_id}/p{period}',
            'url_backup': f'https://backup.example.com/games/{game_id}/p{period}',
            'url_embed': f'https://embed.example.com/v/{game_id}_p{period}',
            'video_id': f'VID_{game_id}_P{period}',
            'extension': 'mp4',
            'description': f'Period {period} video for game {game_id}',
            'duration_seconds': 1500,  # 25 min per period
            'start_offset': (period - 1) * 1500,
            '_load_timestamp': datetime.now().isoformat()
        })
        video_idx += 1
    
    # Goal clips (get goal events from the game)
    if table_exists(f'int_events_{game_id}'):
        goals_df = read_query(f"""
            SELECT event_index, period, time_total_seconds
            FROM int_events_{game_id}
            WHERE LOWER(event_type) LIKE '%goal%'
        """)
        
        for _, goal in goals_df.iterrows():
            records.append({
                'video_index': video_idx,
                'video_key': generate_key('VD', game_id, video_idx),
                'game_id': game_id,
                'video_type': 'highlight',
                'video_category': 'goal',
                'url_primary': f'https://video.example.com/games/{game_id}/goal/{goal["event_index"]}',
                'url_backup': None,
                'url_embed': f'https://embed.example.com/v/{game_id}_g{goal["event_index"]}',
                'video_id': f'VID_{game_id}_GOAL_{goal["event_index"]}',
                'extension': 'mp4',
                'description': f'Goal clip - Period {goal["period"]}',
                'duration_seconds': 30,
                'start_offset': int(goal.get('time_total_seconds', 0)),
                'event_index': int(goal['event_index']),
                'event_key': generate_key('EV', game_id, int(goal['event_index'])),
                '_load_timestamp': datetime.now().isoformat()
            })
            video_idx += 1
    
    # Create DataFrame and load
    video_df = pd.DataFrame(records)
    
    # Stage
    load_dataframe_to_table(video_df, f'stg_video_{game_id}', 'replace')
    
    # Intermediate (same data with processed timestamp)
    video_df['_processed_timestamp'] = datetime.now().isoformat()
    load_dataframe_to_table(video_df, f'int_video_{game_id}', 'replace')
    
    # Datamart
    _publish_video_datamart(game_id, video_df)
    
    logger.info(f"Generated {len(video_df)} video records for game {game_id}")
    return {'video_records': len(video_df)}


def _publish_video_datamart(game_id: int, video_df: pd.DataFrame) -> None:
    """Publish video data to datamart."""
    
    # Create dim_video if not exists
    execute_sql("""
        CREATE TABLE IF NOT EXISTS dim_video (
            video_key TEXT PRIMARY KEY,
            video_index INTEGER NOT NULL,
            game_id INTEGER NOT NULL,
            video_type TEXT,
            video_category TEXT,
            url_primary TEXT,
            url_backup TEXT,
            url_embed TEXT,
            video_id TEXT,
            extension TEXT,
            description TEXT,
            duration_seconds INTEGER,
            start_offset INTEGER,
            event_index INTEGER,
            event_key TEXT,
            _load_timestamp TEXT,
            _processed_timestamp TEXT
        )
    """)
    
    # Delete existing for this game
    execute_sql("DELETE FROM dim_video WHERE game_id = :gid", {'gid': game_id})
    
    # Insert
    load_dataframe_to_table(video_df, 'dim_video', 'append')


# =============================================================================
# RINK DIMENSION PUBLISHING
# =============================================================================

def publish_rink_dimensions() -> Dict[str, int]:
    """
    Publish rink coordinate dimensions to datamart.
    
    Creates:
        - dim_rink_box: Box coordinates with PK
        - dim_rink_zone: Detailed zone coordinates with PK
    
    Returns:
        Dictionary with row counts
    """
    logger.info("Publishing rink dimensions to datamart")
    results = {}
    
    # dim_rink_box from stg_dim_rinkboxcoord
    if table_exists('stg_dim_rinkboxcoord'):
        execute_sql("DROP TABLE IF EXISTS dim_rink_box")
        execute_sql("""
            CREATE TABLE dim_rink_box (
                box_id TEXT PRIMARY KEY,
                box_id_rev TEXT,
                x_min REAL,
                x_max REAL,
                y_min REAL,
                y_max REAL,
                area REAL,
                x_description TEXT,
                y_description TEXT,
                danger TEXT,
                zone TEXT,
                side TEXT,
                _processed_timestamp TEXT
            )
        """)
        execute_sql("""
            INSERT INTO dim_rink_box
            SELECT 
                box_id,
                box_id_rev,
                x_min, x_max, y_min, y_max,
                area,
                x_description, y_description,
                danger, zone, side,
                datetime('now')
            FROM stg_dim_rinkboxcoord
        """)
        results['dim_rink_box'] = get_row_count('dim_rink_box')
    
    # dim_rink_zone from stg_dim_rinkcoordzones
    if table_exists('stg_dim_rinkcoordzones'):
        execute_sql("DROP TABLE IF EXISTS dim_rink_zone")
        execute_sql("""
            CREATE TABLE dim_rink_zone (
                box_id TEXT PRIMARY KEY,
                box_id_rev TEXT,
                x_min REAL,
                x_max REAL,
                y_min REAL,
                y_max REAL,
                y_description TEXT,
                x_description TEXT,
                danger TEXT,
                slot TEXT,
                zone TEXT,
                side TEXT,
                dotside TEXT,
                depth TEXT,
                _processed_timestamp TEXT
            )
        """)
        execute_sql("""
            INSERT INTO dim_rink_zone
            SELECT 
                box_id,
                box_id_rev,
                x_min, x_max, y_min, y_max,
                y_description, x_description,
                danger, slot, zone, side, dotside, depth,
                datetime('now')
            FROM stg_dim_rinkcoordzones
        """)
        results['dim_rink_zone'] = get_row_count('dim_rink_zone')
    
    logger.info(f"Published rink dimensions: {results}")
    return results


# =============================================================================
# FULL ENHANCED PROCESSING
# =============================================================================

def process_game_enhanced(game_id: int, force: bool = False) -> Dict:
    """
    Full enhanced processing for a game including XY and video data.
    
    Args:
        game_id: Game identifier
        force: Force regeneration even if data exists
    
    Returns:
        Dictionary with all results
    """
    logger.info(f"=" * 60)
    logger.info(f"ENHANCED PROCESSING FOR GAME {game_id}")
    logger.info(f"=" * 60)
    
    results = {
        'game_id': game_id,
        'timestamp': datetime.now().isoformat()
    }
    
    # Ensure rink dimensions are published
    results['rink_dims'] = publish_rink_dimensions()
    
    # Generate XY data
    results['xy_data'] = generate_xy_data_for_game(game_id, force=force)
    
    # Generate video data
    results['video_data'] = generate_video_data_for_game(game_id)
    
    logger.info(f"Enhanced processing complete: {results}")
    return results
