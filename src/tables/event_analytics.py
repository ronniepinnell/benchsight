#!/usr/bin/env python3
"""
BenchSight Event Analytics Tables Builder
Creates scoring chances, shot danger, and event chain tables.

These tables analyze event-level data for advanced analytics.

Tables created:
- fact_scoring_chances (shot opportunities with danger ratings)
- fact_shot_danger (shot danger zone analysis)
- fact_linked_events (connected event sequences)
- fact_event_chains (entry-to-shot chains)
- fact_rush_events (rush plays)
- fact_possession_time (possession estimates)

Usage:
    from src.tables.event_analytics import create_all_event_analytics
    create_all_event_analytics()
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple

OUTPUT_DIR = Path('data/output')

# Rink constants for XY calculations
GOAL_LINE_X = 89.0  # Distance from center to goal line (standardized to offensive half)
POINT_NUMBERS = list(range(1, 11))  # Points 1-10 for XY tracking


def save_table(df: pd.DataFrame, name: str) -> int:
    """
    Save table to CSV and return row count.
    Automatically removes 100% null columns (except coordinate/danger/xy columns).
    """
    if df is not None and len(df) > 0:
        from src.core.base_etl import drop_all_null_columns
        df, removed_cols = drop_all_null_columns(df)
        if removed_cols:
            print(f"  {name}: Removed {len(removed_cols)} all-null columns")
    path = OUTPUT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    return len(df)


def load_table(name: str) -> pd.DataFrame:
    """Load a table from output directory."""
    path = OUTPUT_DIR / f"{name}.csv"
    if path.exists():
        return pd.read_csv(path, low_memory=False)
    return pd.DataFrame()


def get_last_point(row: pd.Series, prefix: str) -> Tuple[Optional[float], Optional[float]]:
    """Get the last populated XY point (the stop/endpoint)."""
    for i in reversed(POINT_NUMBERS):
        x_col = f'{prefix}_x_{i}'
        y_col = f'{prefix}_y_{i}'
        x, y = row.get(x_col), row.get(y_col)
        if pd.notna(x) and pd.notna(y):
            return float(x), float(y)
    return None, None


def has_xy_data_for_event(event_id: str, event_players: pd.DataFrame = None) -> bool:
    """
    Check if any XY data exists for an event (puck or player).
    
    Checks multiple sources:
    1. fact_event_players (embedded XY columns)
    2. fact_player_xy_long/wide tables
    3. fact_puck_xy_long/wide tables
    """
    # Check fact_event_players first (if provided)
    if event_players is not None and len(event_players) > 0:
        event_data = event_players[event_players['event_id'] == event_id]
        if len(event_data) > 0:
            # Check for any XY columns
            puck_cols = [c for c in event_data.columns if c.startswith('puck_x_') or c.startswith('puck_y_')]
            player_cols = [c for c in event_data.columns if c.startswith('player_x_') or c.startswith('player_y_')]
            
            if puck_cols and event_data[puck_cols].notna().any().any():
                return True
            if player_cols and event_data[player_cols].notna().any().any():
                return True
    
    # Check XY tables
    player_xy_long = load_table('fact_player_xy_long')
    if len(player_xy_long) > 0:
        if len(player_xy_long[player_xy_long['event_id'] == event_id]) > 0:
            return True
    
    player_xy_wide = load_table('fact_player_xy_wide')
    if len(player_xy_wide) > 0:
        if len(player_xy_wide[player_xy_wide['event_id'] == event_id]) > 0:
            return True
    
    puck_xy_long = load_table('fact_puck_xy_long')
    if len(puck_xy_long) > 0:
        if len(puck_xy_long[puck_xy_long['event_id'] == event_id]) > 0:
            return True
    
    puck_xy_wide = load_table('fact_puck_xy_wide')
    if len(puck_xy_wide) > 0:
        if len(puck_xy_wide[puck_xy_wide['event_id'] == event_id]) > 0:
            return True
    
    return False


def get_stop_point_xy(event_id: str, event_players: pd.DataFrame = None, role: str = 'event_player_1') -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """
    Get stop point XY coordinates for puck and event_player_1.
    
    Checks multiple sources:
    1. fact_event_players (embedded XY columns) - uses last populated point
    2. fact_player_xy_wide - uses x_end/y_end or highest point_number
    3. fact_puck_xy_wide - uses puck_x_end/puck_y_end or highest point_number
    
    Returns:
        (puck_x, puck_y, player_x, player_y) - coordinates at stop point
    """
    puck_x = puck_y = player_x = player_y = None
    
    # Try fact_event_players first (if provided)
    if event_players is not None and len(event_players) > 0:
        event_data = event_players[
            (event_players['event_id'] == event_id) &
            (event_players['player_role'].astype(str).str.lower() == role.lower())
        ]
        
        if len(event_data) > 0:
            row = event_data.iloc[0]
            
            # Get puck stop point (last point)
            puck_x, puck_y = get_last_point(row, 'puck')
            
            # Get player stop point (last point)
            player_x, player_y = get_last_point(row, 'player')
    
    # If not found, try XY tables
    if player_x is None or player_y is None:
        # Try fact_player_xy_wide (has x_end, y_end or highest point)
        player_xy_wide = load_table('fact_player_xy_wide')
        if len(player_xy_wide) > 0:
            event_player_xy = player_xy_wide[
                (player_xy_wide['event_id'] == event_id) &
                (player_xy_wide.get('player_role', '').astype(str).str.lower() == role.lower())
            ]
            if len(event_player_xy) > 0:
                row = event_player_xy.iloc[0]
                # Prefer x_end/y_end if available
                if 'x_end' in row and pd.notna(row.get('x_end')):
                    player_x = float(row['x_end'])
                    player_y = float(row['y_end']) if 'y_end' in row else None
                else:
                    # Use highest point_number
                    point_count = int(row.get('point_count', 0))
                    if point_count > 0:
                        player_x = row.get(f'x_{point_count}')
                        player_y = row.get(f'y_{point_count}')
        
        # Try fact_player_xy_long as fallback (get max point_number)
        if player_x is None or player_y is None:
            player_xy_long = load_table('fact_player_xy_long')
            if len(player_xy_long) > 0:
                event_player_points = player_xy_long[
                    (player_xy_long['event_id'] == event_id) &
                    (player_xy_long.get('player_role', '').astype(str).str.lower() == role.lower())
                ]
                if len(event_player_points) > 0:
                    # Get maximum point_number (the stop point)
                    max_point = event_player_points['point_number'].max()
                    max_point_row = event_player_points[event_player_points['point_number'] == max_point].iloc[0]
                    player_x = float(max_point_row['x']) if pd.notna(max_point_row.get('x')) else None
                    player_y = float(max_point_row['y']) if pd.notna(max_point_row.get('y')) else None
    
    # Try puck XY tables if not found
    if puck_x is None or puck_y is None:
        # Try fact_puck_xy_wide
        puck_xy_wide = load_table('fact_puck_xy_wide')
        if len(puck_xy_wide) > 0:
            event_puck_xy = puck_xy_wide[puck_xy_wide['event_id'] == event_id]
            if len(event_puck_xy) > 0:
                row = event_puck_xy.iloc[0]
                # Prefer puck_x_end/puck_y_end if available
                if 'puck_x_end' in row and pd.notna(row.get('puck_x_end')):
                    puck_x = float(row['puck_x_end'])
                    puck_y = float(row['puck_y_end']) if 'puck_y_end' in row else None
                elif 'x_end' in row and pd.notna(row.get('x_end')):
                    puck_x = float(row['x_end'])
                    puck_y = float(row['y_end']) if 'y_end' in row else None
                else:
                    # Use highest point_number
                    point_count = int(row.get('point_count', 0))
                    if point_count > 0:
                        puck_x = row.get(f'puck_x_{point_count}') or row.get(f'x_{point_count}')
                        puck_y = row.get(f'puck_y_{point_count}') or row.get(f'y_{point_count}')
        
        # Try fact_puck_xy_long as fallback
        if puck_x is None or puck_y is None:
            puck_xy_long = load_table('fact_puck_xy_long')
            if len(puck_xy_long) > 0:
                event_puck_points = puck_xy_long[puck_xy_long['event_id'] == event_id]
                if len(event_puck_points) > 0:
                    # Get maximum point_number (the stop point)
                    max_point = event_puck_points['point_number'].max()
                    max_point_row = event_puck_points[event_puck_points['point_number'] == max_point].iloc[0]
                    puck_x = float(max_point_row['x']) if pd.notna(max_point_row.get('x')) else None
                    puck_y = float(max_point_row['y']) if pd.notna(max_point_row.get('y')) else None
    
    return puck_x, puck_y, player_x, player_y


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
    dy = y  # y distance from center line
    
    if dx <= 0:
        return None  # Behind the goal line
    
    angle = np.degrees(np.arctan2(abs(dy), dx))
    return round(angle, 1)


def get_rink_zone_from_xy(x: float, y: float, rink_zones: pd.DataFrame, granularity: str = 'coarse') -> Optional[dict]:
    """
    Get rink zone information from XY coordinates.
    
    Returns:
        dict with rink_zone_id, zone, danger, etc. or None
    """
    if pd.isna(x) or pd.isna(y) or len(rink_zones) == 0:
        return None
    
    # Filter to requested granularity
    zones = rink_zones[rink_zones['granularity'] == granularity].copy()
    
    for _, row in zones.iterrows():
        if (row['x_min'] <= x <= row['x_max'] and 
            row['y_min'] <= y <= row['y_max']):
            return {
                'rink_zone_id': row.get('rink_zone_id'),
                'zone': row.get('zone'),
                'danger': row.get('danger'),
                'zone_code': row.get('zone_code'),
                'zone_name': row.get('zone_name'),
            }
    
    return None


def calculate_xg_from_xy(distance: float, angle: float, 
                         shot_type: str = '', 
                         is_rush: bool = False, 
                         is_rebound: bool = False) -> float:
    """
    Calculate xG from XY-based distance and angle.
    
    Uses distance/angle formula with modifiers for shot type, rush, rebound.
    """
    if pd.isna(distance) or distance <= 0:
        return 0.02  # Default low xG if no distance
    
    # Base xG from distance (exponential decay)
    # Distance < 15ft: high danger, 15-30ft: medium, >30ft: low
    if distance < 15:
        base_xg = 0.35
    elif distance < 25:
        base_xg = 0.18
    elif distance < 35:
        base_xg = 0.10
    else:
        base_xg = 0.05
    
    # Angle adjustment (shots from wider angles have lower xG)
    if not pd.isna(angle) and angle > 0:
        angle_factor = np.cos(np.radians(angle * 0.8))
        base_xg *= max(angle_factor, 0.3)
    
    # Shot type modifiers
    shot_type_modifiers = {
        'wrist': 1.0,
        'slap': 0.9,
        'snap': 1.05,
        'backhand': 0.7,
        'deflect': 1.2,
        'tip': 1.3,
    }
    
    shot_type_mod = 1.0
    shot_type_lower = str(shot_type).lower()
    for st, mod in shot_type_modifiers.items():
        if st in shot_type_lower:
            shot_type_mod = mod
            break
    
    # Rush modifier
    rush_mod = 1.15 if is_rush else 1.0
    
    # Rebound modifier
    rebound_mod = 1.25 if is_rebound else 1.0
    
    # Calculate final xG
    xg = base_xg * shot_type_mod * rush_mod * rebound_mod
    return round(min(xg, 0.95), 3)  # Cap at 95%


def create_fact_scoring_chances() -> pd.DataFrame:
    """
    Create scoring chances from shot events.
    
    A scoring chance is any shot attempt with danger level assessed.
    Uses XY coordinates when available, falls back to heuristic model otherwise.
    """
    print("\nBuilding fact_scoring_chances...")
    
    events = load_table('fact_events')
    event_players = load_table('fact_event_players')
    schedule = load_table('dim_schedule')
    rink_zones = load_table('dim_rink_zone')
    
    if len(events) == 0:
        print("  ERROR: fact_events not found!")
        return pd.DataFrame()
    
    # Filter to shot-related events
    shots = events[events['event_type'].astype(str).str.lower().isin(['shot', 'goal'])]
    
    all_chances = []
    
    for _, shot in shots.iterrows():
        game_id = shot['game_id']
        event_id = shot['event_id']
        
        chance = {
            'scoring_chance_key': f"SC_{event_id}",
            'game_id': game_id,
            'event_id': event_id,
            'period': shot.get('period'),
        }
        
        # Get season_id
        if len(schedule) > 0:
            game_info = schedule[schedule['game_id'] == game_id]
            if len(game_info) > 0 and 'season_id' in game_info.columns:
                chance['season_id'] = game_info['season_id'].values[0]
        
        # Determine if goal
        event_detail = str(shot.get('event_detail', '')).lower()
        chance['is_goal'] = 'goal_scored' in event_detail or shot['event_type'].lower() == 'goal'
        
        # Event details
        chance['event_detail'] = shot.get('event_detail')
        chance['event_detail_2'] = shot.get('event_detail_2')
        event_detail_2 = str(shot.get('event_detail_2', '')).lower()
        zone = str(shot.get('event_team_zone', '')).lower()
        
        # Check for XY data
        has_xy = has_xy_data_for_event(event_id, event_players)
        chance['has_xy_data'] = 1 if has_xy else 0
        chance['calculation_method'] = 'xy' if has_xy else 'heuristic'
        
        # Initialize XY-based fields
        chance['shot_distance'] = None
        chance['shot_angle'] = None
        chance['shot_x'] = None
        chance['shot_y'] = None
        chance['rink_zone_id'] = None
        chance['rink_zone_code'] = None
        chance['rink_zone_name'] = None
        
        # Get stop point XY if available
        if has_xy and len(event_players) > 0:
            puck_x, puck_y, player_x, player_y = get_stop_point_xy(event_id, event_players)
            
            # Prefer player stop point (event_player_1), fall back to puck
            shot_x = player_x if player_x is not None else puck_x
            shot_y = player_y if player_y is not None else puck_y
            
            if shot_x is not None and shot_y is not None:
                chance['shot_x'] = shot_x
                chance['shot_y'] = shot_y
                
                # Calculate distance and angle (assume attacking right for shots)
                distance = calculate_distance_to_net(shot_x, shot_y, attacking_right=True)
                angle = calculate_angle_to_net(shot_x, shot_y, attacking_right=True)
                
                chance['shot_distance'] = distance
                chance['shot_angle'] = angle
                
                # Get rink zone info (use fine granularity for danger zones)
                zone_info = get_rink_zone_from_xy(shot_x, shot_y, rink_zones, granularity='fine')
                if zone_info:
                    chance['rink_zone_id'] = zone_info.get('rink_zone_id')
                    chance['rink_zone_code'] = zone_info.get('zone_code')
                    chance['rink_zone_name'] = zone_info.get('zone_name')
                    
                    # Use zone danger level if available
                    danger_from_zone = zone_info.get('danger')
                    if danger_from_zone and danger_from_zone != 'none':
                        # Map to standard danger levels
                        if danger_from_zone == 'high':
                            chance['danger_level'] = 'high'
                        elif danger_from_zone == 'medium':
                            chance['danger_level'] = 'medium'
                        elif danger_from_zone == 'low':
                            chance['danger_level'] = 'low'
                        else:
                            chance['danger_level'] = 'perimeter'
                    else:
                        # Fallback to distance-based danger
                        if distance and distance < 15:
                            chance['danger_level'] = 'high'
                        elif distance and distance < 30:
                            chance['danger_level'] = 'medium'
                        elif distance:
                            chance['danger_level'] = 'low'
                        else:
                            chance['danger_level'] = 'perimeter'
                else:
                    # Fallback to distance-based danger if no zone match
                    if distance and distance < 15:
                        chance['danger_level'] = 'high'
                    elif distance and distance < 30:
                        chance['danger_level'] = 'medium'
                    elif distance:
                        chance['danger_level'] = 'low'
                    else:
                        chance['danger_level'] = 'perimeter'
        
        # Heuristic model (when no XY data)
        if not has_xy:
            # High danger indicators
            high_danger_indicators = ['one_time', 'onetimer', 'tip', 'rebound', 'breakaway']
            medium_danger_indicators = ['slot', 'screen', 'rush']
            
            if any(ind in event_detail_2 for ind in high_danger_indicators):
                chance['danger_level'] = 'high'
            elif any(ind in event_detail_2 for ind in medium_danger_indicators):
                chance['danger_level'] = 'medium'
            elif zone == 'o':
                chance['danger_level'] = 'low'
            else:
                chance['danger_level'] = 'perimeter'
        
        # Rush and rebound flags
        chance['is_rush'] = 'rush' in event_detail_2
        chance['is_rebound'] = 'rebound' in event_detail_2
        chance['is_odd_man'] = 'oddman' in event_detail_2 or 'odd_man' in event_detail_2
        
        # Shot type
        shot_type = str(shot.get('event_detail_2', '')).replace('-', '_')
        chance['shot_type'] = shot_type
        
        # Placeholders for time context (would need event sequence analysis)
        chance['time_to_next_event'] = None
        chance['time_from_last_event'] = None
        
        all_chances.append(chance)
    
    df = pd.DataFrame(all_chances)
    print(f"  Created {len(df)} scoring chance records")
    if len(df) > 0:
        xy_count = df['has_xy_data'].sum() if 'has_xy_data' in df.columns else 0
        print(f"  {xy_count} records with XY data ({xy_count/len(df)*100:.1f}%)")
    return df


def create_fact_shot_danger() -> pd.DataFrame:
    """
    Create shot danger analysis with xG estimates.
    
    Uses XY coordinates when available for distance/angle-based xG calculation,
    falls back to heuristic model when XY data is not available.
    """
    print("\nBuilding fact_shot_danger...")
    
    events = load_table('fact_events')
    event_players = load_table('fact_event_players')
    schedule = load_table('dim_schedule')
    rink_zones = load_table('dim_rink_zone')
    
    if len(events) == 0:
        print("  ERROR: fact_events not found!")
        return pd.DataFrame()
    
    # Filter to shots
    shots = events[events['event_type'].astype(str).str.lower().isin(['shot', 'goal'])]
    
    all_danger = []
    
    for idx, shot in shots.iterrows():
        game_id = shot['game_id']
        event_id = shot.get('event_id', idx)
        
        danger = {
            'shot_danger_key': f"SD_{event_id}",
            'game_id': game_id,
            'event_index': event_id,
        }
        
        # Get season_id
        if len(schedule) > 0:
            game_info = schedule[schedule['game_id'] == game_id]
            if len(game_info) > 0 and 'season_id' in game_info.columns:
                danger['season_id'] = game_info['season_id'].values[0]
        
        # Event details
        event_detail = str(shot.get('event_detail', '')).lower()
        event_detail_2 = str(shot.get('event_detail_2', '')).lower()
        zone = str(shot.get('event_team_zone', '')).lower()
        
        # Flags
        danger['is_rebound'] = 'rebound' in event_detail_2
        danger['is_rush'] = 'rush' in event_detail_2
        danger['is_one_timer'] = 'one_time' in event_detail_2 or 'onetimer' in event_detail_2
        
        # Check for XY data
        has_xy = has_xy_data_for_event(event_id, event_players)
        danger['has_xy_data'] = 0
        danger['calculation_method'] = 'heuristic'
        
        # Initialize XY-based fields
        danger['shot_distance'] = None
        danger['shot_angle'] = None
        danger['shot_x'] = None
        danger['shot_y'] = None
        danger['rink_zone_id'] = None
        danger['rink_zone_code'] = None
        
        # Try to use XY-based calculation
        used_xy_calculation = False
        if has_xy and len(event_players) > 0:
            puck_x, puck_y, player_x, player_y = get_stop_point_xy(event_id, event_players)
            
            # Prefer player stop point (event_player_1), fall back to puck
            shot_x = player_x if player_x is not None else puck_x
            shot_y = player_y if player_y is not None else puck_y
            
            if shot_x is not None and shot_y is not None:
                danger['shot_x'] = shot_x
                danger['shot_y'] = shot_y
                
                # Calculate distance and angle (assume attacking right for shots)
                distance = calculate_distance_to_net(shot_x, shot_y, attacking_right=True)
                angle = calculate_angle_to_net(shot_x, shot_y, attacking_right=True)
                
                danger['shot_distance'] = distance
                danger['shot_angle'] = angle
                
                # Get rink zone info (use fine granularity for danger zones)
                zone_info = get_rink_zone_from_xy(shot_x, shot_y, rink_zones, granularity='fine')
                if zone_info:
                    danger['rink_zone_id'] = zone_info.get('rink_zone_id')
                    danger['rink_zone_code'] = zone_info.get('zone_code')
                    
                    # Use zone danger level
                    danger_from_zone = zone_info.get('danger')
                    if danger_from_zone and danger_from_zone != 'none':
                        danger['danger_zone'] = danger_from_zone
                    else:
                        # Fallback to distance-based danger
                        if distance and distance < 15:
                            danger['danger_zone'] = 'high'
                        elif distance and distance < 30:
                            danger['danger_zone'] = 'medium'
                        elif distance:
                            danger['danger_zone'] = 'low'
                        else:
                            danger['danger_zone'] = 'perimeter'
                else:
                    # Fallback to distance-based danger if no zone match
                    if distance and distance < 15:
                        danger['danger_zone'] = 'high'
                    elif distance and distance < 30:
                        danger['danger_zone'] = 'medium'
                    elif distance:
                        danger['danger_zone'] = 'low'
                    else:
                        danger['danger_zone'] = 'perimeter'
                
                # Calculate xG from XY distance/angle
                shot_type_str = shot.get('event_detail_2', '')
                xg = calculate_xg_from_xy(
                    distance if distance else 0,
                    angle if angle else 0,
                    shot_type=shot_type_str,
                    is_rush=danger['is_rush'],
                    is_rebound=danger['is_rebound']
                )
                danger['xg'] = xg
                
                # Mark as using XY calculation
                used_xy_calculation = True
                danger['has_xy_data'] = 1
                danger['calculation_method'] = 'xy'
        
        # Heuristic model (when no XY data or XY calculation failed)
        if not used_xy_calculation:
            # Danger zone logic
            if any(x in event_detail_2 for x in ['one_time', 'tip', 'rebound']):
                danger['danger_zone'] = 'high'
                base_xg = 0.25
            elif any(x in event_detail_2 for x in ['slot', 'screen']):
                danger['danger_zone'] = 'medium'
                base_xg = 0.12
            elif zone == 'o':
                danger['danger_zone'] = 'low'
                base_xg = 0.06
            else:
                danger['danger_zone'] = 'perimeter'
                base_xg = 0.02
            
            # Shot type modifier
            shot_type_modifiers = {
                'wrist': 1.0,
                'slap': 0.9,
                'snap': 1.05,
                'backhand': 0.7,
                'deflect': 1.2,
                'tip': 1.3,
            }
            
            shot_type_mod = 1.0
            for st, mod in shot_type_modifiers.items():
                if st in event_detail_2:
                    shot_type_mod = mod
                    break
            
            # Calculate xG (heuristic)
            xg = base_xg * shot_type_mod * (1.15 if danger['is_rush'] else 1.0) * (1.25 if danger['is_rebound'] else 1.0)
            danger['xg'] = round(min(xg, 0.95), 3)  # Cap at 95%
        
        all_danger.append(danger)
    
    df = pd.DataFrame(all_danger)
    print(f"  Created {len(df)} shot danger records")
    if len(df) > 0:
        xy_count = df['has_xy_data'].sum() if 'has_xy_data' in df.columns else 0
        print(f"  {xy_count} records with XY data ({xy_count/len(df)*100:.1f}%)")
    return df


def create_fact_linked_events() -> pd.DataFrame:
    """
    Create linked event chains (sequences of related events).
    """
    print("\nBuilding fact_linked_events...")
    
    events = load_table('fact_events')
    event_players = load_table('fact_event_players')
    
    if len(events) == 0:
        print("  ERROR: fact_events not found!")
        return pd.DataFrame()
    
    # Use event_chain_key if available
    chain_col = None
    for col in ['event_chain_key', 'linked_event_key', 'sequence_key']:
        if col in event_players.columns:
            chain_col = col
            break
    
    if chain_col is None:
        print("  No chain key column found, skipping")
        return pd.DataFrame()
    
    print(f"  Using {chain_col} for linking")
    
    # Group by chain key
    grouped = event_players.groupby(chain_col)
    
    all_linked = []
    
    for key, group in grouped:
        if pd.isna(key) or str(key) == 'nan':
            continue
        
        game_id = group['game_id'].iloc[0]
        
        linked = {
            'linked_event_key': key,
            'game_id': game_id,
            'event_count': len(group['event_id'].unique()),
        }
        
        # Get first few events in chain
        events_in_chain = group.drop_duplicates(subset=['event_id']).head(5)
        
        for i, (_, ev) in enumerate(events_in_chain.iterrows(), 1):
            linked[f'event_{i}_type'] = ev.get('event_type')
            linked[f'event_{i}_detail'] = ev.get('event_detail')
            linked[f'event_{i}_player_id'] = ev.get('player_id')
        
        # Build event chain string
        event_types = events_in_chain['event_type'].tolist()
        linked['play_chain'] = ' -> '.join(str(et) for et in event_types if pd.notna(et))
        
        all_linked.append(linked)
    
    df = pd.DataFrame(all_linked)
    print(f"  Created {len(df)} linked event records")
    return df


def create_fact_rush_events() -> pd.DataFrame:
    """
    Create rush event analysis.
    
    A rush is a quick transition from entry to shot.
    """
    print("\nBuilding fact_rush_events...")
    
    events = load_table('fact_events')
    schedule = load_table('dim_schedule')
    
    if len(events) == 0:
        print("  ERROR: fact_events not found!")
        return pd.DataFrame()
    
    all_rushes = []
    
    # Group by game
    for game_id in events['game_id'].unique():
        if game_id == 99999:
            continue
        
        game_events = events[events['game_id'] == game_id].sort_values('event_id')
        
        # Get season_id
        season_id = None
        if len(schedule) > 0:
            game_info = schedule[schedule['game_id'] == game_id]
            if len(game_info) > 0 and 'season_id' in game_info.columns:
                season_id = game_info['season_id'].values[0]
        
        # Find zone entries followed by shots within 5 events
        entry_indices = game_events[
            game_events['event_detail'].astype(str).str.lower().str.contains('zone_entry|zoneentry', na=False, regex=True)
        ].index
        
        for entry_idx in entry_indices:
            entry = game_events.loc[entry_idx]
            entry_event_id = entry['event_id']
            
            # Look at next 5 events for a shot
            entry_pos = game_events.index.get_loc(entry_idx)
            next_events = game_events.iloc[entry_pos+1:entry_pos+6]
            
            shots = next_events[next_events['event_type'].astype(str).str.lower().isin(['shot', 'goal'])]
            
            if len(shots) > 0:
                shot = shots.iloc[0]
                
                rush = {
                    'game_id': game_id,
                    'season_id': season_id,
                    'entry_event_id': entry_event_id,  # event_id string, not index
                    'shot_event_id': shot['event_id'],  # event_id string, not index
                    'events_to_shot': len(next_events[next_events.index <= shots.index[0]]),
                    'is_rush': True,
                }
                
                # Entry type
                entry_detail = str(entry.get('event_detail_2', '')).lower()
                if 'carry' in entry_detail or 'rush' in entry_detail:
                    rush['entry_type'] = 'carry'
                    rush['rush_type'] = 'controlled'
                elif 'dump' in entry_detail:
                    rush['entry_type'] = 'dump'
                    rush['rush_type'] = 'dump_chase'
                else:
                    rush['entry_type'] = 'other'
                    rush['rush_type'] = 'other'
                
                # Shot result
                shot_detail = str(shot.get('event_detail', '')).lower()
                rush['is_goal'] = 'goal_scored' in shot_detail or shot['event_type'].lower() == 'goal'
                
                all_rushes.append(rush)
    
    df = pd.DataFrame(all_rushes)
    print(f"  Created {len(df)} rush event records")
    return df


def create_fact_possession_time() -> pd.DataFrame:
    """
    Create possession time estimates per player per game.
    
    CRITICAL: Only counts events where player is event_player_1 (PRIMARY_PLAYER),
    EXCEPT for defensive/support roles which should also be counted.
    
    This ensures proper attribution while capturing defensive contributions.
    """
    PRIMARY_PLAYER = 'event_player_1'
    
    print("\nBuilding fact_possession_time...")
    
    event_players = load_table('fact_event_players')
    schedule = load_table('dim_schedule')
    roster = load_table('fact_gameroster')
    
    if len(event_players) == 0:
        print("  ERROR: fact_event_players not found!")
        return pd.DataFrame()
    
    # Filter to event_player_1 OR defender/support roles
    # Defensive/support roles might be: 'defender', 'support', 'defensive_player', etc.
    primary_mask = event_players['player_role'].astype(str).str.lower() == PRIMARY_PLAYER.lower()
    defensive_support_mask = event_players['player_role'].astype(str).str.lower().str.contains(
        r'defender|support|defensive', na=False, regex=True
    )
    
    # Include both primary players and defensive/support roles
    filtered_events = event_players[primary_mask | defensive_support_mask].copy()
    
    if len(filtered_events) == 0:
        print("  WARNING: No event_player_1 or defender/support events found!")
        return pd.DataFrame()
    
    # Group by game and player
    grouped = filtered_events.groupby(['game_id', 'player_id'])
    
    all_possession = []
    
    for (game_id, player_id), group in grouped:
        if pd.isna(player_id) or game_id == 99999:
            continue
        
        poss = {
            'possession_key': f"POSS_{game_id}_{player_id}",
            'game_id': game_id,
            'player_id': player_id,
        }
        
        # Get season_id
        if len(schedule) > 0:
            game_info = schedule[schedule['game_id'] == game_id]
            if len(game_info) > 0 and 'season_id' in game_info.columns:
                poss['season_id'] = game_info['season_id'].values[0]
        
        # Get venue and team_id from event_players or roster
        venue = None
        team_id = None
        
        # Try to get from group (event_players)
        if 'team_venue' in group.columns:
            venue_vals = group['team_venue'].dropna()
            if len(venue_vals) > 0:
                venue = venue_vals.mode().iloc[0] if len(venue_vals.mode()) > 0 else venue_vals.iloc[0]
        
        if 'player_team_id' in group.columns:
            team_vals = group['player_team_id'].dropna()
            if len(team_vals) > 0:
                team_id = team_vals.mode().iloc[0] if len(team_vals.mode()) > 0 else team_vals.iloc[0]
        
        # Fallback to roster if not found in event_players
        if (venue is None or team_id is None) and len(roster) > 0:
            player_roster = roster[
                (roster['game_id'] == game_id) &
                (roster['player_id'] == player_id)
            ]
            if len(player_roster) > 0:
                if venue is None and 'team_venue' in player_roster.columns:
                    venue_vals = player_roster['team_venue'].dropna()
                    if len(venue_vals) > 0:
                        venue = venue_vals.iloc[0]
                
                if team_id is None and 'team_id' in player_roster.columns:
                    team_vals = player_roster['team_id'].dropna()
                    if len(team_vals) > 0:
                        team_id = team_vals.iloc[0]
        
        # Map venue to full name if needed
        if venue is not None:
            venue_lower = str(venue).lower()
            if venue_lower in ['h', 'home']:
                venue = 'home'
            elif venue_lower in ['a', 'away']:
                venue = 'away'
        
        poss['venue'] = venue
        poss['team_id'] = team_id
        
        # Add venue_id if venue is available
        if venue is not None:
            venue_map = {'home': 'VEN001', 'away': 'VEN002', 'h': 'VEN001', 'a': 'VEN002'}
            poss['venue_id'] = venue_map.get(venue.lower(), None)
        else:
            poss['venue_id'] = None
        
        # Count possession-related events (only from filtered events - event_player_1 or defender/support)
        # Zone entries
        entries = group[group['event_type'].astype(str).str.lower().str.contains('zone', na=False)]
        poss['zone_entries'] = len(entries[entries['event_detail'].astype(str).str.lower().str.contains('entry', na=False)])
        poss['zone_exits'] = len(entries[entries['event_detail'].astype(str).str.lower().str.contains('exit', na=False)])
        
        # Offensive zone entries
        if 'event_team_zone' in group.columns:
            ozone = group[group['event_team_zone'].astype(str).str.lower().str.contains(r'^o|offensive', na=False, regex=True)]
            poss['ozone_entries'] = len(ozone[ozone['event_detail'].astype(str).str.lower().str.contains('entry', na=False)])
        else:
            poss['ozone_entries'] = 0
        
        # Defensive zone entries (bad)
        if 'event_team_zone' in group.columns:
            dzone = group[group['event_team_zone'].astype(str).str.lower().str.contains(r'^d|defensive', na=False, regex=True)]
            poss['dzone_entries'] = len(dzone[dzone['event_detail'].astype(str).str.lower().str.contains('entry', na=False)])
        else:
            poss['dzone_entries'] = 0
        
        # Total possession events (passes, shots, carries)
        possession_events = group[
            group['event_type'].astype(str).str.lower().isin(['pass', 'shot', 'possession', 'deke'])
        ]
        poss['possession_events'] = len(possession_events)
        
        # Estimate possession time (very rough: 3 seconds per possession event)
        poss['estimated_possession_seconds'] = poss['possession_events'] * 3
        
        all_possession.append(poss)
    
    df = pd.DataFrame(all_possession)
    print(f"  Created {len(df)} possession records")
    return df


def create_all_event_analytics():
    """
    Create all event analytics tables.
    """
    print("\n" + "=" * 70)
    print("CREATING EVENT ANALYTICS TABLES")
    print("=" * 70)
    
    results = {}
    
    # 1. Scoring chances
    df = create_fact_scoring_chances()
    if len(df) > 0:
        rows = save_table(df, 'fact_scoring_chances')
        results['fact_scoring_chances'] = rows
        print(f"  ✓ fact_scoring_chances: {rows} rows")
    
    # 2. Shot danger
    df = create_fact_shot_danger()
    if len(df) > 0:
        rows = save_table(df, 'fact_shot_danger')
        results['fact_shot_danger'] = rows
        print(f"  ✓ fact_shot_danger: {rows} rows")
    
    # 3. Linked events
    df = create_fact_linked_events()
    if len(df) > 0:
        rows = save_table(df, 'fact_linked_events')
        results['fact_linked_events'] = rows
        print(f"  ✓ fact_linked_events: {rows} rows")
    
    # 4. Rush events
    df = create_fact_rush_events()
    if len(df) > 0:
        rows = save_table(df, 'fact_rush_events')
        results['fact_rush_events'] = rows
        print(f"  ✓ fact_rush_events: {rows} rows")
    
    # 5. Possession time
    df = create_fact_possession_time()
    if len(df) > 0:
        rows = save_table(df, 'fact_possession_time')
        results['fact_possession_time'] = rows
        print(f"  ✓ fact_possession_time: {rows} rows")
    
    print(f"\nCreated {len(results)} event analytics tables")
    return results


if __name__ == "__main__":
    create_all_event_analytics()
