#!/usr/bin/env python3
"""
================================================================================
XY TABLE BUILDER - Spatial Analytics for BenchSight
================================================================================

This module builds XY coordinate tables and spatial relationship analytics from
the embedded XY columns in fact_event_players.

INPUT:
    fact_event_players.csv with columns:
    - puck_x_1..puck_x_10, puck_y_1..puck_y_10
    - player_x_1..player_x_10, player_y_1..player_y_10

OUTPUT TABLES:
    Core XY Tables:
    - fact_puck_xy_wide     (1 row per event)
    - fact_puck_xy_long     (1 row per point per event)
    - fact_player_xy_wide   (1 row per player per event)
    - fact_player_xy_long   (1 row per point per player per event)
    
    Spatial Relationship Tables:
    - fact_player_matchups_xy     (all event_player vs opp_player pairs)
    - fact_player_puck_proximity  (each player's distance to puck)
    
    Shot Analytics Tables:
    - fact_shot_event      (shot context - 1 row per shot)
    - fact_shot_players    (all players on ice per shot)

USAGE:
    from src.xy.xy_table_builder import build_all_xy_tables
    build_all_xy_tables()

================================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List
import logging
from src.core.table_writer import save_output_table

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path('data/output')

# Rink constants
GOAL_LINE_X = 89.0  # Distance from center to goal line
NET_WIDTH = 6.0     # Width of net opening
NET_HEIGHT = 4.0    # Height of net

# Point columns (1-10)
POINT_NUMBERS = list(range(1, 11))


def load_event_players() -> pd.DataFrame:
    """Load fact_event_players with XY columns."""
    path = OUTPUT_DIR / 'fact_event_players.csv'
    if not path.exists():
        logger.error(f"fact_event_players.csv not found at {path}")
        return pd.DataFrame()
    
    df = pd.read_csv(path, low_memory=False)
    logger.info(f"Loaded fact_event_players: {len(df):,} rows, {len(df.columns)} cols")
    return df


def load_fact_events() -> pd.DataFrame:
    """Load fact_events for event-level context."""
    path = OUTPUT_DIR / 'fact_events.csv'
    if not path.exists():
        logger.error(f"fact_events.csv not found at {path}")
        return pd.DataFrame()
    
    df = pd.read_csv(path, low_memory=False)
    logger.info(f"Loaded fact_events: {len(df):,} rows")
    return df


def get_xy_columns(df: pd.DataFrame) -> Tuple[List[str], List[str]]:
    """Get lists of puck and player XY columns."""
    puck_cols = sorted([c for c in df.columns if c.startswith('puck_x_') or c.startswith('puck_y_')])
    player_cols = sorted([c for c in df.columns if c.startswith('player_x_') or c.startswith('player_y_')])
    return puck_cols, player_cols


def has_xy_data(df: pd.DataFrame) -> bool:
    """Check if dataframe has any XY data."""
    puck_cols, player_cols = get_xy_columns(df)
    if not puck_cols and not player_cols:
        return False
    return df[puck_cols + player_cols].notna().any().any()


def count_populated_points(row: pd.Series, prefix: str) -> int:
    """Count how many XY points are populated (1-10) for a given prefix."""
    count = 0
    for i in POINT_NUMBERS:
        x_col = f'{prefix}_x_{i}'
        y_col = f'{prefix}_y_{i}'
        if pd.notna(row.get(x_col)) and pd.notna(row.get(y_col)):
            count = i  # Keep track of highest populated point
    return count


def get_last_point(row: pd.Series, prefix: str) -> Tuple[Optional[float], Optional[float]]:
    """Get the last populated XY point (the endpoint)."""
    for i in reversed(POINT_NUMBERS):
        x_col = f'{prefix}_x_{i}'
        y_col = f'{prefix}_y_{i}'
        x, y = row.get(x_col), row.get(y_col)
        if pd.notna(x) and pd.notna(y):
            return float(x), float(y)
    return None, None


def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> Optional[float]:
    """Calculate Euclidean distance between two points."""
    if any(pd.isna(v) for v in [x1, y1, x2, y2]):
        return None
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def calculate_angle_to_net(x: float, y: float, attacking_right: bool = True) -> Optional[float]:
    """Calculate angle from point to net center (in degrees)."""
    if pd.isna(x) or pd.isna(y):
        return None
    
    goal_x = GOAL_LINE_X if attacking_right else -GOAL_LINE_X
    dx = goal_x - x
    dy = y  # y distance from center line
    
    if dx <= 0:
        return None  # Behind the goal line
    
    angle = np.degrees(np.arctan2(abs(dy), dx))
    return round(angle, 1)


def calculate_distance_to_net(x: float, y: float, attacking_right: bool = True) -> Optional[float]:
    """Calculate distance from point to net center."""
    if pd.isna(x) or pd.isna(y):
        return None
    
    goal_x = GOAL_LINE_X if attacking_right else -GOAL_LINE_X
    return round(np.sqrt((goal_x - x)**2 + y**2), 1)


# =============================================================================
# PUCK XY TABLES
# =============================================================================

def build_fact_puck_xy_wide(event_players: pd.DataFrame) -> pd.DataFrame:
    """
    Build fact_puck_xy_wide - one row per event with all puck positions.
    
    Puck position is the same for all players in an event, so we dedupe.
    """
    logger.info("Building fact_puck_xy_wide...")
    
    puck_cols, _ = get_xy_columns(event_players)
    if not puck_cols:
        logger.warning("  No puck XY columns found")
        return pd.DataFrame()
    
    # Filter to rows with puck data
    has_puck = event_players[puck_cols].notna().any(axis=1)
    puck_data = event_players[has_puck].copy()
    
    if len(puck_data) == 0:
        logger.info("  No puck XY data found")
        return pd.DataFrame()
    
    # Dedupe by event_id (puck is same for all players in event)
    key_cols = ['event_id', 'game_id', 'period', 'event_type', 'event_detail']
    key_cols = [c for c in key_cols if c in puck_data.columns]
    
    puck_wide = puck_data.groupby('event_id').first().reset_index()
    
    # Build output columns
    records = []
    for _, row in puck_wide.iterrows():
        record = {
            'puck_xy_key': f"PKW{row.get('game_id', '')}{str(row.get('event_id', ''))[-5:]}",
            'event_id': row['event_id'],
            'game_id': row.get('game_id'),
            'period': row.get('period'),
            'event_type': row.get('event_type'),
            'event_detail': row.get('event_detail'),
            'point_count': count_populated_points(row, 'puck'),
        }
        
        # Add x_1 through x_10, y_1 through y_10
        for i in POINT_NUMBERS:
            record[f'x_{i}'] = row.get(f'puck_x_{i}')
            record[f'y_{i}'] = row.get(f'puck_y_{i}')
        
        # Calculate derived fields
        x_start, y_start = row.get('puck_x_1'), row.get('puck_y_1')
        x_end, y_end = get_last_point(row, 'puck')
        
        record['x_start'] = x_start
        record['y_start'] = y_start
        record['x_end'] = x_end
        record['y_end'] = y_end
        record['distance_traveled'] = calculate_distance(x_start, y_start, x_end, y_end) if x_end else None
        
        record['_export_timestamp'] = datetime.now().isoformat()
        records.append(record)
    
    df = pd.DataFrame(records)
    save_output_table(df, 'fact_puck_xy_wide', OUTPUT_DIR)
    logger.info(f"  ✓ fact_puck_xy_wide: {len(df)} rows")
    return df


def build_fact_puck_xy_long(event_players: pd.DataFrame) -> pd.DataFrame:
    """
    Build fact_puck_xy_long - one row per point per event.
    
    Unpivots puck_x_1..10, puck_y_1..10 into long format.
    """
    logger.info("Building fact_puck_xy_long...")
    
    puck_cols, _ = get_xy_columns(event_players)
    if not puck_cols:
        return pd.DataFrame()
    
    # Filter and dedupe by event
    has_puck = event_players[puck_cols].notna().any(axis=1)
    puck_data = event_players[has_puck].groupby('event_id').first().reset_index()
    
    if len(puck_data) == 0:
        logger.info("  No puck XY data found")
        return pd.DataFrame()
    
    records = []
    for _, row in puck_data.iterrows():
        event_id = row['event_id'] if 'event_id' in row.index else None
        game_id = row['game_id'] if 'game_id' in row.index else None
        
        if not event_id:
            continue
            
        for i in POINT_NUMBERS:
            x_col = f'puck_x_{i}'
            y_col = f'puck_y_{i}'
            
            if x_col not in row.index or y_col not in row.index:
                continue
                
            x = row[x_col]
            y = row[y_col]
            
            if pd.notna(x) and pd.notna(y):
                try:
                    x_float = float(x)
                    y_float = float(y)
                except (ValueError, TypeError):
                    continue
                    
                records.append({
                    'puck_xy_key': f"PKL{game_id or ''}{str(event_id)[-5:]}{i:02d}",
                    'event_id': event_id,
                    'game_id': game_id,
                    'point_number': i,
                    'x': x_float,
                    'y': y_float,
                    'distance_to_net': calculate_distance_to_net(x_float, y_float),
                    'angle_to_net': calculate_angle_to_net(x_float, y_float),
                    '_export_timestamp': datetime.now().isoformat()
                })
    
    df = pd.DataFrame(records)
    if len(df) > 0:
        # Save directly to ensure it's saved even if save_output_table skips empty
        df.to_csv(OUTPUT_DIR / 'fact_puck_xy_long.csv', index=False)
        logger.info(f"  ✓ fact_puck_xy_long: {len(df)} rows (saved directly)")
    else:
        logger.info("  ⚠ fact_puck_xy_long: 0 rows (no data found)")
    return df


# =============================================================================
# PLAYER XY TABLES
# =============================================================================

def build_fact_player_xy_wide(event_players: pd.DataFrame) -> pd.DataFrame:
    """
    Build fact_player_xy_wide - one row per player per event.
    """
    logger.info("Building fact_player_xy_wide...")
    
    _, player_cols = get_xy_columns(event_players)
    if not player_cols:
        return pd.DataFrame()
    
    # Filter to rows with player XY data
    has_player_xy = event_players[player_cols].notna().any(axis=1)
    player_data = event_players[has_player_xy].copy()
    
    if len(player_data) == 0:
        logger.info("  No player XY data found")
        return pd.DataFrame()
    
    records = []
    for _, row in player_data.iterrows():
        record = {
            'player_xy_key': f"PXW{row.get('game_id', '')}{str(row.get('event_id', ''))[-5:]}{str(row.get('player_id', ''))[-4:]}",
            'event_id': row.get('event_id'),
            'game_id': row.get('game_id'),
            'player_id': row.get('player_id'),
            'player_name': row.get('player_name'),
            'player_role': row.get('player_role'),
            'team_id': row.get('team_id'),
            'is_event_team': 'event_player' in str(row.get('player_role', '')),
            'point_count': count_populated_points(row, 'player'),
        }
        
        # Add all point columns
        for i in POINT_NUMBERS:
            record[f'x_{i}'] = row.get(f'player_x_{i}')
            record[f'y_{i}'] = row.get(f'player_y_{i}')
        
        # Derived fields
        x_start, y_start = row.get('player_x_1'), row.get('player_y_1')
        x_end, y_end = get_last_point(row, 'player')
        
        record['x_start'] = x_start
        record['y_start'] = y_start
        record['x_end'] = x_end
        record['y_end'] = y_end
        record['distance_traveled'] = calculate_distance(x_start, y_start, x_end, y_end) if x_end else None
        record['distance_to_net_start'] = calculate_distance_to_net(x_start, y_start) if pd.notna(x_start) else None
        record['distance_to_net_end'] = calculate_distance_to_net(x_end, y_end) if x_end else None
        
        record['_export_timestamp'] = datetime.now().isoformat()
        records.append(record)
    
    df = pd.DataFrame(records)
    save_output_table(df, 'fact_player_xy_wide', OUTPUT_DIR)
    logger.info(f"  ✓ fact_player_xy_wide: {len(df)} rows")
    return df


def build_fact_player_xy_long(event_players: pd.DataFrame) -> pd.DataFrame:
    """
    Build fact_player_xy_long - one row per point per player per event.
    """
    logger.info("Building fact_player_xy_long...")
    
    _, player_cols = get_xy_columns(event_players)
    if not player_cols:
        return pd.DataFrame()
    
    has_player_xy = event_players[player_cols].notna().any(axis=1)
    player_data = event_players[has_player_xy].copy()
    
    if len(player_data) == 0:
        logger.info("  No player XY data found")
        return pd.DataFrame()
    
    records = []
    for _, row in player_data.iterrows():
        event_id = row['event_id'] if 'event_id' in row.index else None
        game_id = row['game_id'] if 'game_id' in row.index else None
        player_id = row['player_id'] if 'player_id' in row.index else None
        
        if not event_id or not player_id:
            continue
            
        for i in POINT_NUMBERS:
            x_col = f'player_x_{i}'
            y_col = f'player_y_{i}'
            
            if x_col not in row.index or y_col not in row.index:
                continue
                
            x = row[x_col]
            y = row[y_col]
            
            if pd.notna(x) and pd.notna(y):
                try:
                    x_float = float(x)
                    y_float = float(y)
                except (ValueError, TypeError):
                    continue
                    
                records.append({
                    'player_xy_key': f"PXL{game_id or ''}{str(event_id)[-5:]}{str(player_id)[-4:]}{i:02d}",
                    'event_id': event_id,
                    'game_id': game_id,
                    'player_id': player_id,
                    'player_name': row['player_name'] if 'player_name' in row.index else None,
                    'player_role': row['player_role'] if 'player_role' in row.index else None,
                    'is_event_team': 'event_player' in str(row.get('player_role', '')),
                    'point_number': i,
                    'x': x_float,
                    'y': y_float,
                    'distance_to_net': calculate_distance_to_net(x_float, y_float),
                    'angle_to_net': calculate_angle_to_net(x_float, y_float),
                    '_export_timestamp': datetime.now().isoformat()
                })
    
    df = pd.DataFrame(records)
    if len(df) > 0:
        # Save directly to ensure it's saved even if save_output_table skips empty
        df.to_csv(OUTPUT_DIR / 'fact_player_xy_long.csv', index=False)
        logger.info(f"  ✓ fact_player_xy_long: {len(df)} rows (saved directly)")
    else:
        logger.info("  ⚠ fact_player_xy_long: 0 rows (no data found)")
    return df


# =============================================================================
# SPATIAL RELATIONSHIP TABLES
# =============================================================================

def build_fact_player_puck_proximity(event_players: pd.DataFrame) -> pd.DataFrame:
    """
    Build fact_player_puck_proximity - each player's distance to puck.
    
    Uses the END position of each point interval (last populated point).
    """
    logger.info("Building fact_player_puck_proximity...")
    
    puck_cols, player_cols = get_xy_columns(event_players)
    if not puck_cols or not player_cols:
        return pd.DataFrame()
    
    # Need both puck and player data
    has_both = (event_players[puck_cols].notna().any(axis=1) & 
                event_players[player_cols].notna().any(axis=1))
    data = event_players[has_both].copy()
    
    if len(data) == 0:
        logger.info("  No combined puck+player XY data found")
        return pd.DataFrame()
    
    records = []
    for _, row in data.iterrows():
        # Get puck end position (from deduped event data - use first player's puck data)
        puck_x_end, puck_y_end = get_last_point(row, 'puck')
        player_x_end, player_y_end = get_last_point(row, 'player')
        
        if puck_x_end is None or player_x_end is None:
            continue
        
        distance = calculate_distance(player_x_end, player_y_end, puck_x_end, puck_y_end)
        
        records.append({
            'proximity_key': f"PPX{row.get('game_id', '')}{str(row.get('event_id', ''))[-5:]}{str(row.get('player_id', ''))[-4:]}",
            'event_id': row.get('event_id'),
            'game_id': row.get('game_id'),
            'player_id': row.get('player_id'),
            'player_name': row.get('player_name'),
            'player_role': row.get('player_role'),
            'is_event_team': 'event_player' in str(row.get('player_role', '')),
            'player_x': player_x_end,
            'player_y': player_y_end,
            'puck_x': puck_x_end,
            'puck_y': puck_y_end,
            'distance_to_puck': distance,
            'is_puck_carrier': distance < 5.0 if distance else None,  # Within 5 feet
            'is_pressuring': distance < 10.0 if distance else None,   # Within 10 feet
            '_export_timestamp': datetime.now().isoformat()
        })
    
    df = pd.DataFrame(records)
    save_output_table(df, 'fact_player_puck_proximity', OUTPUT_DIR)
    logger.info(f"  ✓ fact_player_puck_proximity: {len(df)} rows")
    return df


def build_fact_player_matchups_xy(event_players: pd.DataFrame) -> pd.DataFrame:
    """
    Build fact_player_matchups_xy - all event_player vs opp_player combinations.
    
    Calculates gap distance, closing speed, angles, etc.
    """
    logger.info("Building fact_player_matchups_xy...")
    
    _, player_cols = get_xy_columns(event_players)
    if not player_cols:
        return pd.DataFrame()
    
    # Get rows with player XY
    has_xy = event_players[player_cols].notna().any(axis=1)
    data = event_players[has_xy].copy()
    
    if len(data) == 0:
        logger.info("  No player XY data found")
        return pd.DataFrame()
    
    records = []
    
    # Group by event to find matchups within each event
    for event_id, event_group in data.groupby('event_id'):
        # Split into event players and opponent players
        event_players_df = event_group[event_group['player_role'].str.contains('event_player', na=False)]
        opp_players_df = event_group[event_group['player_role'].str.contains('opp_player', na=False)]
        
        if len(event_players_df) == 0 or len(opp_players_df) == 0:
            continue
        
        # Create all combinations
        for _, ep in event_players_df.iterrows():
            ep_x_start, ep_y_start = ep.get('player_x_1'), ep.get('player_y_1')
            ep_x_end, ep_y_end = get_last_point(ep, 'player')
            
            if ep_x_end is None:
                continue
            
            for _, op in opp_players_df.iterrows():
                op_x_start, op_y_start = op.get('player_x_1'), op.get('player_y_1')
                op_x_end, op_y_end = get_last_point(op, 'player')
                
                if op_x_end is None:
                    continue
                
                # Calculate distances
                distance_start = calculate_distance(ep_x_start, ep_y_start, op_x_start, op_y_start)
                distance_end = calculate_distance(ep_x_end, ep_y_end, op_x_end, op_y_end)
                distance_change = (distance_end - distance_start) if distance_start and distance_end else None
                
                records.append({
                    'matchup_key': f"MXY{ep.get('game_id', '')}{str(event_id)[-5:]}{str(ep.get('player_id', ''))[-4:]}{str(op.get('player_id', ''))[-4:]}",
                    'event_id': event_id,
                    'game_id': ep.get('game_id'),
                    
                    # Event player info
                    'event_player_id': ep.get('player_id'),
                    'event_player_name': ep.get('player_name'),
                    'event_player_role': ep.get('player_role'),
                    'event_player_x_start': ep_x_start,
                    'event_player_y_start': ep_y_start,
                    'event_player_x_end': ep_x_end,
                    'event_player_y_end': ep_y_end,
                    
                    # Opponent player info
                    'opp_player_id': op.get('player_id'),
                    'opp_player_name': op.get('player_name'),
                    'opp_player_role': op.get('player_role'),
                    'opp_player_x_start': op_x_start,
                    'opp_player_y_start': op_y_start,
                    'opp_player_x_end': op_x_end,
                    'opp_player_y_end': op_y_end,
                    
                    # Spatial metrics
                    'distance_start': distance_start,
                    'distance_end': distance_end,
                    'distance_change': distance_change,  # Negative = closing gap
                    'is_closing': distance_change < 0 if distance_change else None,
                    'gap_rating': 'tight' if (distance_end and distance_end < 10) else 
                                 ('medium' if (distance_end and distance_end < 20) else 'loose'),
                    
                    '_export_timestamp': datetime.now().isoformat()
                })
    
    df = pd.DataFrame(records)
    save_output_table(df, 'fact_player_matchups_xy', OUTPUT_DIR)
    logger.info(f"  ✓ fact_player_matchups_xy: {len(df)} rows")
    return df


# =============================================================================
# SHOT ANALYTICS TABLES
# =============================================================================

def build_fact_shot_event(event_players: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """
    Build fact_shot_event - shot-specific analytics.
    
    One row per shot/goal event with shooter position, distance, angle,
    and aggregate screen metrics.
    """
    logger.info("Building fact_shot_event...")
    
    _, player_cols = get_xy_columns(event_players)
    
    # Filter to shots and goals
    shot_events = events[events['event_type'].isin(['Shot', 'Goal'])].copy()
    
    if len(shot_events) == 0:
        logger.info("  No shot/goal events found")
        return pd.DataFrame()
    
    records = []
    for _, event in shot_events.iterrows():
        event_id = event['event_id']
        
        # Get the shooter (event_player_1 for shots/goals)
        shooter_data = event_players[
            (event_players['event_id'] == event_id) & 
            (event_players['player_role'] == 'event_player_1')
        ]
        
        if len(shooter_data) == 0:
            continue
        
        shooter = shooter_data.iloc[0]
        
        # Get shooter end position (where shot was taken)
        shot_x, shot_y = get_last_point(shooter, 'player')
        
        # Calculate screen metrics for all players in this shot event
        event_group = event_players[event_players['event_id'] == event_id]
        
        friendly_screen_score = 0.0
        own_team_screen_score = 0.0
        screen_count = 0
        
        if shot_x is not None:
            for _, player in event_group.iterrows():
                if player.get('player_role') == 'event_player_1':  # Skip shooter
                    continue
                    
                player_x, player_y = get_last_point(player, 'player')
                is_shooter_team = 'event_player' in str(player.get('player_role', ''))
                
                screen_data = calculate_screen_score(
                    player_x, player_y,
                    shot_x, shot_y,
                    is_shooter_team=is_shooter_team
                )
                
                if screen_data['screen_score'] > 0.1:
                    screen_count += 1
                    if is_shooter_team:
                        friendly_screen_score += screen_data['screen_score']
                    else:
                        own_team_screen_score += screen_data['screen_score']
        
        total_screen_score = friendly_screen_score + own_team_screen_score
        is_screened = total_screen_score > 0.2
        
        record = {
            'shot_event_key': f"SHE{event.get('game_id', '')}{str(event_id)[-5:]}",
            'event_id': event_id,
            'game_id': event.get('game_id'),
            'period': event.get('period'),
            'event_type': event.get('event_type'),
            'event_detail': event.get('event_detail'),
            'is_goal': event.get('event_type') == 'Goal',
            
            # Shooter info
            'shooter_player_id': shooter.get('player_id'),
            'shooter_name': shooter.get('player_name'),
            'shooter_team_id': shooter.get('team_id'),
            
            # Shot location
            'shot_x': shot_x,
            'shot_y': shot_y,
            'shot_distance': calculate_distance_to_net(shot_x, shot_y) if shot_x else None,
            'shot_angle': calculate_angle_to_net(shot_x, shot_y) if shot_x else None,
            
            # Screen metrics (aggregate)
            'friendly_screen_score': round(friendly_screen_score, 3),
            'own_team_screen_score': round(own_team_screen_score, 3),
            'total_screen_score': round(total_screen_score, 3),
            'screen_count': screen_count,
            'is_screened': is_screened,
            
            # Net target location (when available)
            'net_target_x': None,
            'net_target_y': None,
            'net_location_id': None,
            
            '_export_timestamp': datetime.now().isoformat()
        }
        records.append(record)
    
    df = pd.DataFrame(records)
    save_output_table(df, 'fact_shot_event', OUTPUT_DIR)
    logger.info(f"  ✓ fact_shot_event: {len(df)} rows")
    return df


def calculate_screen_score(
    player_x: float, player_y: float,
    shooter_x: float, shooter_y: float,
    goalie_x: float = GOAL_LINE_X, goalie_y: float = 0.0,
    is_shooter_team: bool = True
) -> dict:
    """
    Calculate screen quality score based on goalie vision obstruction.
    
    Screen scoring factors:
    - Distance from goalie (closer = higher score, harder to see around)
    - Angular coverage (how many degrees of goalie's FOV blocked)
    - Position in vision cone (between goalie and shooter)
    - Distance from shot path (perpendicular distance to puck trajectory)
    
    Returns dict with:
    - is_in_vision_cone: bool
    - is_in_puck_path: bool  
    - distance_to_goalie: float
    - distance_to_shot_path: float
    - angular_coverage_degrees: float
    - distance_factor: float (1.0 at crease, decays with distance)
    - screen_score: float (composite score 0-1)
    """
    result = {
        'is_in_vision_cone': False,
        'is_in_puck_path': False,
        'distance_to_goalie': None,
        'distance_to_shot_path': None,
        'angular_coverage_degrees': None,
        'distance_factor': None,
        'screen_score': 0.0
    }
    
    if any(pd.isna(v) for v in [player_x, player_y, shooter_x, shooter_y]):
        return result
    
    # Distance from player to goalie (net center)
    dist_to_goalie = np.sqrt((GOAL_LINE_X - player_x)**2 + player_y**2)
    result['distance_to_goalie'] = round(dist_to_goalie, 1)
    
    # Distance from shooter to goalie
    dist_shooter_to_goalie = np.sqrt((GOAL_LINE_X - shooter_x)**2 + shooter_y**2)
    
    # Player must be between shooter and net to be a screen
    if dist_to_goalie >= dist_shooter_to_goalie:
        return result  # Player is behind shooter, not screening
    
    # Calculate perpendicular distance to shot path (line from shooter to net center)
    # Using point-to-line distance formula
    # Line from shooter (x1,y1) to goal (x2,y2), point (x0,y0)
    x0, y0 = player_x, player_y
    x1, y1 = shooter_x, shooter_y
    x2, y2 = GOAL_LINE_X, 0.0  # Net center
    
    # Distance to line formula
    numerator = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1)
    denominator = np.sqrt((y2-y1)**2 + (x2-x1)**2)
    dist_to_shot_path = numerator / denominator if denominator > 0 else 0
    result['distance_to_shot_path'] = round(dist_to_shot_path, 1)
    
    # Is player in the puck path? (within ~3 feet of shot line)
    result['is_in_puck_path'] = dist_to_shot_path < 3.0
    
    # Vision cone check - is player in the goalie's view toward shooter?
    # Angle from goalie to shooter
    angle_to_shooter = np.degrees(np.arctan2(shooter_y, GOAL_LINE_X - shooter_x))
    # Angle from goalie to player
    angle_to_player = np.degrees(np.arctan2(player_y, GOAL_LINE_X - player_x))
    # Difference
    angle_diff = abs(angle_to_shooter - angle_to_player)
    
    # Within 20 degrees of shooter line = in vision cone
    result['is_in_vision_cone'] = angle_diff < 20
    
    # Angular coverage - how wide does player appear to goalie?
    # Assume player is ~2 feet wide
    player_width = 2.0
    angular_coverage = np.degrees(2 * np.arctan(player_width / (2 * max(dist_to_goalie, 1))))
    result['angular_coverage_degrees'] = round(angular_coverage, 1)
    
    # Distance factor - closer to goalie = harder to see around
    # 1.0 at 5 feet, decays to 0.1 at 30 feet
    if dist_to_goalie < 5:
        distance_factor = 1.0
    elif dist_to_goalie > 30:
        distance_factor = 0.1
    else:
        distance_factor = 1.0 - (dist_to_goalie - 5) / 30
    result['distance_factor'] = round(distance_factor, 2)
    
    # Composite screen score (only if in vision cone and close enough)
    if result['is_in_vision_cone'] and dist_to_goalie < 25:
        # Base score from angular coverage (normalized to ~0-1 range)
        base_score = min(angular_coverage / 15.0, 1.0)
        
        # Multiply by distance factor
        screen_score = base_score * distance_factor
        
        # Bonus for being in direct puck path
        if result['is_in_puck_path']:
            screen_score *= 1.5
        
        # Cap at 1.0
        result['screen_score'] = round(min(screen_score, 1.0), 3)
    
    return result


def build_fact_shot_players(event_players: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """
    Build fact_shot_players - all players on ice per shot.
    
    Includes position, distance to shooter, screen analysis, etc.
    """
    logger.info("Building fact_shot_players...")
    
    puck_cols, player_cols = get_xy_columns(event_players)
    
    # Filter to shots and goals
    shot_event_ids = events[events['event_type'].isin(['Shot', 'Goal'])]['event_id'].tolist()
    
    if not shot_event_ids:
        logger.info("  No shot/goal events found")
        return pd.DataFrame()
    
    # Get all players involved in shot events
    shot_players = event_players[event_players['event_id'].isin(shot_event_ids)].copy()
    
    if len(shot_players) == 0:
        return pd.DataFrame()
    
    records = []
    for event_id in shot_event_ids:
        event_group = shot_players[shot_players['event_id'] == event_id]
        
        if len(event_group) == 0:
            continue
        
        # Get shooter position
        shooter_row = event_group[event_group['player_role'] == 'event_player_1']
        if len(shooter_row) == 0:
            continue
        
        shooter = shooter_row.iloc[0]
        shooter_x, shooter_y = get_last_point(shooter, 'player')
        
        # Get puck position
        puck_x, puck_y = get_last_point(shooter, 'puck')
        
        for _, player in event_group.iterrows():
            player_x, player_y = get_last_point(player, 'player')
            
            is_shooter = player.get('player_role') == 'event_player_1'
            is_shooter_team = 'event_player' in str(player.get('player_role', ''))
            
            # Calculate spatial relationships
            distance_to_shooter = calculate_distance(player_x, player_y, shooter_x, shooter_y) if (player_x and shooter_x) else None
            distance_to_puck = calculate_distance(player_x, player_y, puck_x, puck_y) if (player_x and puck_x) else None
            distance_to_net = calculate_distance_to_net(player_x, player_y) if player_x else None
            
            # Enhanced screen analysis
            screen_data = calculate_screen_score(
                player_x, player_y, 
                shooter_x, shooter_y,
                is_shooter_team=is_shooter_team
            ) if (player_x and shooter_x and not is_shooter) else {
                'is_in_vision_cone': False,
                'is_in_puck_path': False,
                'distance_to_goalie': None,
                'distance_to_shot_path': None,
                'angular_coverage_degrees': None,
                'distance_factor': None,
                'screen_score': 0.0
            }
            
            # Determine screen type based on score
            is_screening = screen_data['screen_score'] > 0.1
            if is_screening:
                screen_type = 'friendly' if is_shooter_team else 'own_goal_risk'
            else:
                screen_type = 'none'
            
            records.append({
                'shot_player_key': f"SHP{player.get('game_id', '')}{str(event_id)[-5:]}{str(player.get('player_id', ''))[-4:]}",
                'event_id': event_id,
                'game_id': player.get('game_id'),
                
                # Player info
                'player_id': player.get('player_id'),
                'player_name': player.get('player_name'),
                'player_role': player.get('player_role'),
                'is_shooter_team': is_shooter_team,
                'is_shooter': is_shooter,
                
                # Position
                'player_x': player_x,
                'player_y': player_y,
                
                # Spatial to shooter
                'distance_to_shooter': distance_to_shooter,
                'distance_to_puck': distance_to_puck,
                'distance_to_net': distance_to_net,
                
                # Enhanced screen analysis
                'is_in_vision_cone': screen_data['is_in_vision_cone'],
                'is_in_puck_path': screen_data['is_in_puck_path'],
                'distance_to_goalie': screen_data['distance_to_goalie'],
                'distance_to_shot_path': screen_data['distance_to_shot_path'],
                'angular_coverage_degrees': screen_data['angular_coverage_degrees'],
                'distance_factor': screen_data['distance_factor'],
                'screen_score': screen_data['screen_score'],
                'is_screening': is_screening,
                'screen_type': screen_type,
                
                '_export_timestamp': datetime.now().isoformat()
            })
    
    df = pd.DataFrame(records)
    save_output_table(df, 'fact_shot_players', OUTPUT_DIR)
    logger.info(f"  ✓ fact_shot_players: {len(df)} rows")
    return df


# =============================================================================
# MAIN BUILDER
# =============================================================================

def build_all_xy_tables() -> dict:
    """
    Build all XY and spatial analytics tables.
    
    Returns:
        Dictionary with table names and row counts
    """
    print()
    print("=" * 70)
    print("XY TABLE BUILDER - Spatial Analytics")
    print("=" * 70)
    
    # Load source data
    event_players = load_event_players()
    events = load_fact_events()
    
    if len(event_players) == 0:
        logger.error("Cannot build XY tables - no source data")
        return {}
    
    # Check for XY data
    if not has_xy_data(event_players):
        logger.warning("No XY data found in fact_event_players")
        logger.info("Creating empty schema tables...")
        # Create empty tables with proper schema
        from src.xy.xy_tables import (
            create_fact_puck_xy_wide, create_fact_puck_xy_long,
            create_fact_player_xy_wide, create_fact_player_xy_long,
            create_fact_shot_xy
        )
        create_fact_puck_xy_wide()
        create_fact_puck_xy_long()
        create_fact_player_xy_wide()
        create_fact_player_xy_long()
        create_fact_shot_xy()
        return {'status': 'empty_schemas_created'}
    
    results = {}
    
    # Build core XY tables
    logger.info("\n--- Core XY Tables ---")
    results['fact_puck_xy_wide'] = len(build_fact_puck_xy_wide(event_players))
    results['fact_puck_xy_long'] = len(build_fact_puck_xy_long(event_players))
    results['fact_player_xy_wide'] = len(build_fact_player_xy_wide(event_players))
    results['fact_player_xy_long'] = len(build_fact_player_xy_long(event_players))
    
    # Build spatial relationship tables
    logger.info("\n--- Spatial Relationship Tables ---")
    results['fact_player_puck_proximity'] = len(build_fact_player_puck_proximity(event_players))
    results['fact_player_matchups_xy'] = len(build_fact_player_matchups_xy(event_players))
    
    # Build shot analytics tables
    logger.info("\n--- Shot Analytics Tables ---")
    results['fact_shot_event'] = len(build_fact_shot_event(event_players, events))
    results['fact_shot_players'] = len(build_fact_shot_players(event_players, events))
    
    print()
    print("=" * 70)
    print("XY TABLE BUILDER COMPLETE")
    print("=" * 70)
    total_rows = sum(results.values())
    print(f"Tables created: {len(results)}")
    print(f"Total rows: {total_rows:,}")
    
    return results


if __name__ == '__main__':
    build_all_xy_tables()
