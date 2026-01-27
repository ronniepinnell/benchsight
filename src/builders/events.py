"""
Event Table Builder

Functions to build fact_events table from tracking data.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from src.core.key_utils import add_fact_events_fkeys, add_player_id_columns
from src.core.table_writer import save_output_table


def build_fact_events(
    tracking_df: pd.DataFrame,
    output_dir: Path,
    save: bool = True
) -> pd.DataFrame:
    """
    Build fact_events table from tracking data.
    
    Creates one row per event by selecting the representative row from
    fact_event_players. Prioritizes Goal > Shot > other event types.
    
    Args:
        tracking_df: DataFrame from fact_event_players (tracking data)
        output_dir: Path to output directory (for FK lookups)
        save: Whether to save the table (default: True)
        
    Returns:
        DataFrame with fact_events data
    """
    # Sort to prioritize Goal > Shot > other event types
    # This ensures Goal_Scored is selected over Shot_Goal when both exist
    event_type_priority = {
        'Goal': 0,
        'Shot': 1,
        'Faceoff': 2,
        'Pass': 3,
        'Possession': 4
    }
    
    tracking = tracking_df.copy()
    tracking['_event_type_priority'] = tracking['event_type'].map(
        event_type_priority
    ).fillna(99)
    
    tracking = tracking.sort_values([
        'event_id',
        '_event_type_priority',
        'player_role'
    ])
    
    # Group by event_id and take first row (highest priority)
    events = tracking.groupby('event_id', as_index=False).first()
    events = events.drop(columns=['_event_type_priority'], errors='ignore')
    
    # Select meaningful columns
    keep_cols = [
        'event_id', 'game_id', 'period',
        'event_type', 'event_detail', 'event_detail_2', 'event_successful',
        'event_team_zone', 'shift_key', 'linked_event_key',
        'sequence_key', 'play_key', 'tracking_event_key',
        'home_team', 'away_team', 'duration',
        # Time columns (calculated)
        'event_start_min', 'event_start_sec', 'event_end_min', 'event_end_sec',
        'time_start_total_seconds', 'time_end_total_seconds',
        'event_running_start', 'event_running_end',
        'running_video_time', 'period_start_total_running_seconds',
        'running_intermission_duration',
        # Team columns (calculated)
        'team_venue', 'team_venue_abv', 'player_team',
        'home_team_zone', 'away_team_zone',
        # Player columns (calculated)
        'player_role', 'side_of_puck', 'role_number', 'role_abrev',
        'player_game_number', 'strength',
        # Play details
        'play_detail1', 'play_detail_2', 'play_detail_successful',
        'pressured_pressurer',
        # XY data
        'puck_x_start', 'puck_y_start', 'puck_x_end', 'puck_y_end',
        'net_x', 'net_y',
        'player_x', 'player_y',
        # Flags
        'is_goal', 'is_highlight'
    ]
    
    events = events[[c for c in keep_cols if c in events.columns]]
    
    # Add player ID columns from tracking data
    events = add_player_id_columns(events, tracking)
    
    # Add FK columns
    events = add_fact_events_fkeys(events, output_dir)
    
    # Reorder columns - keys and FKs first
    priority_cols = [
        'event_id', 'game_id', 'period', 'period_id',
        'event_type', 'event_type_id',
        'event_detail', 'event_detail_id',
        'event_detail_2', 'event_detail_2_id',
        'event_successful', 'success_id',
        'event_team_zone', 'event_zone_id',
        'sequence_key', 'play_key', 'tracking_event_key',
        'shift_key', 'linked_event_key',
        'home_team', 'home_team_id', 'away_team', 'away_team_id',
        'duration', 'event_player_ids', 'opp_player_ids',
        # Individual player columns
        'event_player_1_id', 'event_player_1_name', 'event_player_1_rating',
        'event_player_2_id', 'event_player_2_name', 'event_player_2_rating',
        'opp_player_1_id', 'opp_player_1_name', 'opp_player_1_rating'
    ]
    other_cols = [c for c in events.columns if c not in priority_cols]
    events = events[[c for c in priority_cols if c in events.columns] + other_cols]
    
    if save:
        save_output_table(events, 'fact_events', output_dir)
    
    return events


def get_event_type_priority() -> Dict[str, int]:
    """
    Get event type priority mapping for selecting representative event rows.
    
    Lower numbers = higher priority.
    Goal events are highest priority to ensure Goal_Scored is selected over Shot_Goal.
    
    Returns:
        Dict mapping event_type to priority (lower = higher priority)
    """
    return {
        'Goal': 0,
        'Shot': 1,
        'Faceoff': 2,
        'Pass': 3,
        'Possession': 4
    }
