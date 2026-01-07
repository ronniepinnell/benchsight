"""
=============================================================================
EVENT TIME & TOI CONTEXT ENHANCEMENT
=============================================================================
File: src/advanced/event_time_context.py
Version: 11.01
Created: January 7, 2026

Adds time-to-event columns and player TOI context to event tables:
- time_to_next_event, time_from_last_event
- time_to_next_goal_for/against, time_from_last_goal_for/against
- time_to_next_stoppage, time_from_last_stoppage
- event_player_1_toi through event_player_6_toi
- opp_player_1_toi through opp_player_6_toi
- team_on_ice_toi_avg/min/max, opp_on_ice_toi_avg/min/max

Total: 26 new columns
=============================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent.parent / 'data' / 'output'


def calculate_time_to_events(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate time-to-event columns for each event.
    
    Adds columns:
    - time_to_next_event: Seconds until next event
    - time_from_last_event: Seconds since last event
    - time_to_next_goal_for: Seconds until team's next goal (-1 if none)
    - time_to_next_goal_against: Seconds until opponent's next goal (-1 if none)
    - time_from_last_goal_for: Seconds since team's last goal (-1 if none)
    - time_from_last_goal_against: Seconds since opponent's last goal (-1 if none)
    - time_to_next_stoppage: Seconds until next stoppage (-1 if none)
    - time_from_last_stoppage: Seconds since last stoppage (-1 if none)
    
    Args:
        events_df: DataFrame with events (must have time_start_total_seconds, game_id)
    
    Returns:
        DataFrame with new time columns added
    """
    logger.info("Calculating time-to-event columns...")
    
    df = events_df.copy()
    
    # Ensure we have the time column - use time_start_total_seconds
    time_col = 'time_start_total_seconds'
    if time_col not in df.columns:
        logger.warning(f"Column {time_col} not found. Checking for alternatives...")
        # Try alternative column names
        for alt in ['event_running_start', 'running_video_time']:
            if alt in df.columns:
                time_col = alt
                logger.info(f"Using {time_col} as time column")
                break
        else:
            logger.error("No time column found. Skipping time calculations.")
            return df
    
    # Convert time column to numeric
    df[time_col] = pd.to_numeric(df[time_col], errors='coerce')
    
    # Initialize new columns with -1 (no event found)
    time_cols = [
        'time_to_next_event', 'time_from_last_event',
        'time_to_next_goal_for', 'time_to_next_goal_against',
        'time_from_last_goal_for', 'time_from_last_goal_against',
        'time_to_next_stoppage', 'time_from_last_stoppage'
    ]
    for col in time_cols:
        df[col] = -1.0
    
    # Process each game separately
    for game_id in df['game_id'].unique():
        game_mask = df['game_id'] == game_id
        game_df = df[game_mask].sort_values(time_col).copy()
        game_indices = game_df.index
        
        if len(game_df) == 0:
            continue
        
        times = game_df[time_col].values
        
        # Time to/from adjacent events (simple shift)
        next_times = np.roll(times, -1)
        prev_times = np.roll(times, 1)
        
        # Calculate basic time differences
        time_to_next = next_times - times
        time_from_last = times - prev_times
        
        # Set first/last event appropriately
        time_from_last[0] = -1
        time_to_next[-1] = -1
        
        df.loc[game_indices, 'time_to_next_event'] = time_to_next
        df.loc[game_indices, 'time_from_last_event'] = time_from_last
        
        # Get goal events (event_type='Goal' AND event_detail='Goal_Scored')
        # Or use is_goal flag if available
        if 'is_goal' in game_df.columns:
            goal_mask = game_df['is_goal'] == 1
        elif 'event_type' in game_df.columns and 'event_detail' in game_df.columns:
            goal_mask = (game_df['event_type'] == 'Goal') & (game_df['event_detail'] == 'Goal_Scored')
        else:
            goal_mask = pd.Series([False] * len(game_df), index=game_df.index)
        
        # Get team information for goal attribution
        team_col = None
        for tc in ['player_team', 'team_venue', 'home_team']:
            if tc in game_df.columns:
                team_col = tc
                break
        
        # Calculate goal time columns
        if goal_mask.any() and team_col:
            goal_times = game_df.loc[goal_mask, time_col].values
            goal_teams = game_df.loc[goal_mask, team_col].values
            goal_indices_arr = np.where(goal_mask)[0]
            
            for i, (idx, row) in enumerate(game_df.iterrows()):
                current_time = row[time_col]
                current_team = row.get(team_col, None)
                
                if pd.isna(current_time) or pd.isna(current_team):
                    continue
                
                # Find next/last goal for current team (goal_for)
                for_goals = [(t, gi) for t, tm, gi in zip(goal_times, goal_teams, goal_indices_arr) 
                             if tm == current_team]
                
                # Find next/last goal against (opponent goals)
                against_goals = [(t, gi) for t, tm, gi in zip(goal_times, goal_teams, goal_indices_arr) 
                                 if tm != current_team]
                
                # Time to next goal for
                next_for = [t for t, gi in for_goals if t > current_time]
                if next_for:
                    df.loc[idx, 'time_to_next_goal_for'] = min(next_for) - current_time
                
                # Time from last goal for
                last_for = [t for t, gi in for_goals if t < current_time]
                if last_for:
                    df.loc[idx, 'time_from_last_goal_for'] = current_time - max(last_for)
                
                # Time to next goal against
                next_against = [t for t, gi in against_goals if t > current_time]
                if next_against:
                    df.loc[idx, 'time_to_next_goal_against'] = min(next_against) - current_time
                
                # Time from last goal against
                last_against = [t for t, gi in against_goals if t < current_time]
                if last_against:
                    df.loc[idx, 'time_from_last_goal_against'] = current_time - max(last_against)
        
        # Get stoppage events
        if 'event_type' in game_df.columns:
            stoppage_mask = game_df['event_type'] == 'Stoppage'
            if stoppage_mask.any():
                stoppage_times = game_df.loc[stoppage_mask, time_col].values
                
                for i, (idx, row) in enumerate(game_df.iterrows()):
                    current_time = row[time_col]
                    if pd.isna(current_time):
                        continue
                    
                    # Time to next stoppage
                    next_stoppages = [t for t in stoppage_times if t > current_time]
                    if next_stoppages:
                        df.loc[idx, 'time_to_next_stoppage'] = min(next_stoppages) - current_time
                    
                    # Time from last stoppage
                    last_stoppages = [t for t in stoppage_times if t < current_time]
                    if last_stoppages:
                        df.loc[idx, 'time_from_last_stoppage'] = current_time - max(last_stoppages)
    
    logger.info(f"  Added 8 time-to-event columns")
    return df


def calculate_player_toi_at_event(events_df: pd.DataFrame, 
                                   shifts_player_df: pd.DataFrame,
                                   shifts_tracking_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Calculate each player's cumulative TOI at the time of each event.
    
    For each event, looks up which shift each player is in and calculates:
    - Cumulative TOI from previous shifts
    - Plus time elapsed within current shift up to the event timestamp
    
    Handles two formats:
    1. fact_events: Has event_player_ids/opp_player_ids as comma-separated strings
    2. fact_event_players: Has single player_id column (one row per player per event)
    
    Adds columns:
    - event_player_1_toi through event_player_6_toi
    - opp_player_1_toi through opp_player_6_toi
    - (For tracking table: also adds player_toi for the single player)
    
    Args:
        events_df: DataFrame with events (needs time_start_total_seconds, player columns)
        shifts_player_df: DataFrame with player-level shift data (player_id, shift_key, cumulative_duration)
        shifts_tracking_df: DataFrame with shift timing (shift_key, shift_start_total_seconds, shift_end_total_seconds)
    
    Returns:
        DataFrame with player TOI columns added
    """
    logger.info("Calculating player TOI at event time...")
    
    df = events_df.copy()
    
    # Initialize TOI columns for event_player_1-6 and opp_player_1-6
    for i in range(1, 7):
        df[f'event_player_{i}_toi'] = np.nan
        df[f'opp_player_{i}_toi'] = np.nan
    
    # Also add a single player_toi column for tracking table format
    df['player_toi'] = np.nan
    
    # Determine which format we're dealing with
    has_comma_separated = 'event_player_ids' in df.columns
    has_single_player = 'player_id' in df.columns and not has_comma_separated
    
    # Check for required columns in events
    time_col = 'time_start_total_seconds'
    if time_col not in df.columns:
        for alt in ['event_running_start', 'running_video_time']:
            if alt in df.columns:
                time_col = alt
                break
        else:
            logger.warning("No time column found for TOI calculation")
            return df
    
    # If we have shifts_tracking_df, join it with shifts_player_df to get timing
    if shifts_tracking_df is not None and len(shifts_tracking_df) > 0:
        # Join to get shift timing for each player-shift
        shifts_combined = shifts_player_df.merge(
            shifts_tracking_df[['shift_key', 'game_id', 'shift_start_total_seconds', 'shift_end_total_seconds']],
            on=['shift_key', 'game_id'],
            how='left'
        )
    else:
        shifts_combined = shifts_player_df.copy()
        logger.warning("No shifts_tracking_df provided, TOI calculation will be limited")
        return df
    
    # Check we have required timing columns
    shift_start_col = 'shift_start_total_seconds'
    shift_end_col = 'shift_end_total_seconds'
    
    if shift_start_col not in shifts_combined.columns or shift_end_col not in shifts_combined.columns:
        logger.warning("Shift timing columns not found after merge. Skipping TOI calculation.")
        return df
    
    # Build player TOI lookup per game
    # For each game and player, we need the list of shifts with their times and durations
    for game_id in df['game_id'].unique():
        game_events = df[df['game_id'] == game_id]
        game_shifts = shifts_combined[shifts_combined['game_id'] == int(game_id)].copy()
        
        if len(game_shifts) == 0:
            continue
        
        # Build player shift lookup: {player_id: [(start, end, duration, cumulative_before), ...]}
        player_shifts = {}
        
        # Get unique players from shifts
        if 'player_id' in game_shifts.columns:
            for player_id in game_shifts['player_id'].dropna().unique():
                player_data = game_shifts[game_shifts['player_id'] == player_id].sort_values(shift_start_col)
                shifts_list = []
                cumulative = 0
                
                for _, shift in player_data.iterrows():
                    start = shift.get(shift_start_col, 0)
                    end = shift.get(shift_end_col, start)
                    duration = shift.get('shift_duration', end - start if pd.notna(end) and pd.notna(start) else 0)
                    
                    if pd.notna(duration):
                        duration = float(duration)
                    else:
                        duration = 0
                    
                    if pd.notna(start) and pd.notna(end):
                        shifts_list.append({
                            'start': float(start),
                            'end': float(end),
                            'duration': duration,
                            'cumulative_before': cumulative
                        })
                        cumulative += duration
                
                player_shifts[str(player_id)] = shifts_list
        
        logger.info(f"  Game {game_id}: Built TOI lookup for {len(player_shifts)} players")
        
        # Now calculate TOI for each event
        for idx, event in game_events.iterrows():
            event_time = event.get(time_col)
            if pd.isna(event_time):
                continue
            event_time = float(event_time)
            
            if has_comma_separated:
                # Format 1: Comma-separated player IDs (fact_events)
                event_player_ids_str = event.get('event_player_ids', '')
                if pd.notna(event_player_ids_str) and event_player_ids_str:
                    event_player_list = [p.strip() for p in str(event_player_ids_str).split(',') if p.strip()]
                else:
                    event_player_list = []
                
                # Calculate TOI for each event player (up to 6)
                for i, player_id in enumerate(event_player_list[:6], 1):
                    if player_id in player_shifts:
                        toi = _calculate_toi_at_time(player_shifts[player_id], event_time)
                        df.loc[idx, f'event_player_{i}_toi'] = toi
                
                # Get opponent player IDs
                opp_player_ids_str = event.get('opp_player_ids', '')
                if pd.notna(opp_player_ids_str) and opp_player_ids_str:
                    opp_player_list = [p.strip() for p in str(opp_player_ids_str).split(',') if p.strip()]
                else:
                    opp_player_list = []
                
                # Calculate TOI for each opp player (up to 6)
                for i, player_id in enumerate(opp_player_list[:6], 1):
                    if player_id in player_shifts:
                        toi = _calculate_toi_at_time(player_shifts[player_id], event_time)
                        df.loc[idx, f'opp_player_{i}_toi'] = toi
            
            elif has_single_player:
                # Format 2: Single player_id column (fact_event_players)
                player_id = event.get('player_id')
                if pd.notna(player_id):
                    player_id = str(player_id)
                    if player_id in player_shifts:
                        toi = _calculate_toi_at_time(player_shifts[player_id], event_time)
                        df.loc[idx, 'player_toi'] = toi
                        
                        # Also store in event_player_1_toi for consistency
                        # Check if this is an event_player or opp_player
                        player_role = event.get('player_role', '')
                        if pd.notna(player_role):
                            if 'event_player' in str(player_role):
                                df.loc[idx, 'event_player_1_toi'] = toi
                            elif 'opp_player' in str(player_role):
                                df.loc[idx, 'opp_player_1_toi'] = toi
    
    logger.info(f"  Added player TOI columns")
    return df


def _calculate_toi_at_time(shifts_list: list, event_time: float) -> float:
    """
    Calculate cumulative TOI up to a specific event time.
    
    Args:
        shifts_list: List of shift dicts with start, end, duration, cumulative_before
        event_time: Time of the event in game seconds
    
    Returns:
        Cumulative TOI in seconds at event_time
    """
    if not shifts_list:
        return 0.0
    
    for shift in shifts_list:
        # If event is during this shift
        if shift['start'] <= event_time <= shift['end']:
            # TOI = all previous shifts + time elapsed in current shift
            time_in_shift = event_time - shift['start']
            return shift['cumulative_before'] + time_in_shift
        
        # If event is after this shift ends
        elif event_time > shift['end']:
            continue
        
        # If event is before this shift starts
        else:
            return shift['cumulative_before']
    
    # If we're past all shifts, return total TOI
    last_shift = shifts_list[-1]
    return last_shift['cumulative_before'] + last_shift['duration']


def calculate_team_toi_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate team-level TOI aggregates at each event.
    
    Uses the individual player TOI columns to calculate:
    - team_on_ice_toi_avg: Average TOI of event_player_1-6
    - team_on_ice_toi_min: Min TOI of event_player_1-6
    - team_on_ice_toi_max: Max TOI of event_player_1-6
    - opp_on_ice_toi_avg: Average TOI of opp_player_1-6
    - opp_on_ice_toi_min: Min TOI of opp_player_1-6
    - opp_on_ice_toi_max: Max TOI of opp_player_1-6
    
    Args:
        df: DataFrame with event_player_X_toi and opp_player_X_toi columns
    
    Returns:
        DataFrame with team TOI aggregate columns added
    """
    logger.info("Calculating team TOI aggregates...")
    
    # Team player TOI columns
    team_cols = [f'event_player_{i}_toi' for i in range(1, 7)]
    opp_cols = [f'opp_player_{i}_toi' for i in range(1, 7)]
    
    # Filter to columns that exist
    team_cols = [c for c in team_cols if c in df.columns]
    opp_cols = [c for c in opp_cols if c in df.columns]
    
    if team_cols:
        team_toi = df[team_cols]
        df['team_on_ice_toi_avg'] = team_toi.mean(axis=1, skipna=True)
        df['team_on_ice_toi_min'] = team_toi.min(axis=1, skipna=True)
        df['team_on_ice_toi_max'] = team_toi.max(axis=1, skipna=True)
    else:
        df['team_on_ice_toi_avg'] = np.nan
        df['team_on_ice_toi_min'] = np.nan
        df['team_on_ice_toi_max'] = np.nan
    
    if opp_cols:
        opp_toi = df[opp_cols]
        df['opp_on_ice_toi_avg'] = opp_toi.mean(axis=1, skipna=True)
        df['opp_on_ice_toi_min'] = opp_toi.min(axis=1, skipna=True)
        df['opp_on_ice_toi_max'] = opp_toi.max(axis=1, skipna=True)
    else:
        df['opp_on_ice_toi_avg'] = np.nan
        df['opp_on_ice_toi_min'] = np.nan
        df['opp_on_ice_toi_max'] = np.nan
    
    logger.info(f"  Added 6 team TOI aggregate columns")
    return df


def enhance_event_tables() -> Dict[str, int]:
    """
    Main function to enhance all event tables with time and TOI context.
    
    Enhances:
    - fact_event_players
    - fact_event_players
    - fact_events
    
    Returns:
        Dictionary of table names to row counts
    """
    logger.info("=" * 60)
    logger.info("ENHANCING EVENT TABLES WITH TIME & TOI CONTEXT")
    logger.info("=" * 60)
    
    results = {}
    
    # Load required tables
    try:
        events_tracking = pd.read_csv(OUTPUT_DIR / 'fact_event_players.csv', low_memory=False)
        logger.info(f"Loaded fact_event_players: {len(events_tracking)} rows")
    except FileNotFoundError:
        logger.error("fact_event_players.csv not found")
        return results
    
    try:
        shifts_tracking = pd.read_csv(OUTPUT_DIR / 'fact_shifts.csv', low_memory=False)
        logger.info(f"Loaded fact_shifts: {len(shifts_tracking)} rows")
    except FileNotFoundError:
        logger.warning("fact_shifts.csv not found, TOI calculations will be limited")
        shifts_tracking = pd.DataFrame()
    
    try:
        shifts_player = pd.read_csv(OUTPUT_DIR / 'fact_shift_players.csv', low_memory=False)
        logger.info(f"Loaded fact_shift_players: {len(shifts_player)} rows")
    except FileNotFoundError:
        logger.warning("fact_shift_players.csv not found")
        shifts_player = pd.DataFrame()
    
    # Define all new columns for reference
    time_cols = [
        'time_to_next_event', 'time_from_last_event',
        'time_to_next_goal_for', 'time_to_next_goal_against',
        'time_from_last_goal_for', 'time_from_last_goal_against',
        'time_to_next_stoppage', 'time_from_last_stoppage',
    ]
    toi_cols = [f'event_player_{i}_toi' for i in range(1, 7)]
    toi_cols += [f'opp_player_{i}_toi' for i in range(1, 7)]
    toi_cols += ['player_toi', 'team_on_ice_toi_avg', 'team_on_ice_toi_min', 'team_on_ice_toi_max',
                 'opp_on_ice_toi_avg', 'opp_on_ice_toi_min', 'opp_on_ice_toi_max']
    all_new_cols = time_cols + toi_cols
    
    # ========================================
    # 1. ENHANCE fact_event_players (single player per row)
    # ========================================
    logger.info("\n--- Enhancing fact_event_players ---")
    events_tracking = calculate_time_to_events(events_tracking)
    
    if len(shifts_player) > 0 and len(shifts_tracking) > 0:
        events_tracking = calculate_player_toi_at_event(events_tracking, shifts_player, shifts_tracking)
    
    events_tracking = calculate_team_toi_aggregates(events_tracking)
    
    # Save enhanced fact_event_players
    events_tracking.to_csv(OUTPUT_DIR / 'fact_event_players.csv', index=False)
    results['fact_event_players'] = len(events_tracking)
    logger.info(f"Saved fact_event_players: {len(events_tracking)} rows, {len(events_tracking.columns)} cols")
    
    # ========================================
    # 2. ENHANCE fact_events (has comma-separated player IDs - calculate TOI directly)
    # ========================================
    try:
        events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv', low_memory=False)
        logger.info(f"\n--- Enhancing fact_events ---")
        logger.info(f"Loaded: {len(events)} rows")
        
        # First, add team columns from tracking data if not present
        # (needed for goal_for/goal_against calculations)
        if 'player_team' not in events.columns and 'event_id' in events_tracking.columns:
            # Get first row per event from tracking to get team info
            team_context = events_tracking.groupby('event_id').first().reset_index()
            team_cols_to_add = ['event_id']
            for col in ['player_team', 'team_venue', 'player_team_id', 'team_venue_id']:
                if col in team_context.columns:
                    team_cols_to_add.append(col)
            
            if len(team_cols_to_add) > 1:
                events = events.merge(team_context[team_cols_to_add], on='event_id', how='left')
                logger.info(f"Added team columns from tracking: {team_cols_to_add[1:]}")
        
        # Calculate time-to-event columns directly on events
        events = calculate_time_to_events(events)
        
        # Calculate player TOI (uses comma-separated player IDs in event_player_ids/opp_player_ids)
        if len(shifts_player) > 0 and len(shifts_tracking) > 0:
            events = calculate_player_toi_at_event(events, shifts_player, shifts_tracking)
        
        # Calculate team aggregates
        events = calculate_team_toi_aggregates(events)
        
        events.to_csv(OUTPUT_DIR / 'fact_events.csv', index=False)
        results['fact_events'] = len(events)
        logger.info(f"Saved fact_events: {len(events)} rows, {len(events.columns)} cols")
        
    except FileNotFoundError:
        logger.warning("fact_events.csv not found")
        events = None
    
    logger.info("\n" + "=" * 60)
    logger.info("EVENT TIME & TOI ENHANCEMENT COMPLETE")
    logger.info(f"Tables enhanced: {list(results.keys())}")
    logger.info("=" * 60)
    
    return results


if __name__ == '__main__':
    enhance_event_tables()
