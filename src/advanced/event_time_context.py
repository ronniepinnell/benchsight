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
from src.core.table_writer import save_output_table

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_shift_toi_at_event(events_df: pd.DataFrame, shift_players_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate shift-based TOI for fact_event_players.
    
    For each player-event row, calculates:
    - player_toi: Time from current shift start to event time (in seconds)
    - team_on_ice_toi_avg/min/max: Aggregate of all teammates on ice (excl goalies)
    - opp_on_ice_toi_avg/min/max: Aggregate of all opponents on ice (excl goalies)
    
    Args:
        events_df: fact_event_players with game_id, player_id, team_venue, time_start_total_seconds
        shift_players_df: fact_shift_players with player shifts and timing
    
    Returns:
        DataFrame with TOI columns added
    """
    logger.info("Calculating shift-based TOI at event time...")
    
    df = events_df.copy()
    
    # Initialize columns
    df['player_toi'] = np.nan
    df['team_on_ice_toi_avg'] = np.nan
    df['team_on_ice_toi_min'] = np.nan
    df['team_on_ice_toi_max'] = np.nan
    df['opp_on_ice_toi_avg'] = np.nan
    df['opp_on_ice_toi_min'] = np.nan
    df['opp_on_ice_toi_max'] = np.nan
    
    # Required columns check
    required = ['game_id', 'time_start_total_seconds']
    if not all(c in df.columns for c in required):
        logger.warning(f"Missing required columns for TOI: {required}")
        return df
    
    sp = shift_players_df.copy()
    
    # Exclude goalies from shift data for aggregates
    sp_skaters = sp[sp['position'] != 'G'].copy()
    
    # Pre-build lookup: (game_id, period) -> list of (player_id, venue, shift_start, shift_end)
    # Include period if available for more accurate matching
    logger.info("  Building shift lookup by game (and period if available)...")
    shift_lookup = {}
    has_period = 'period' in sp_skaters.columns
    
    if has_period:
        # More precise: group by game_id and period
        for (game_id, period), group in sp_skaters.groupby(['game_id', 'period']):
            key = (int(game_id), int(period))
            shift_lookup[key] = group[['player_id', 'venue', 'shift_start_total_seconds', 'shift_end_total_seconds']].values.tolist()
    else:
        # Fallback: group by game_id only
        for game_id, group in sp_skaters.groupby('game_id'):
            shift_lookup[int(game_id)] = group[['player_id', 'venue', 'shift_start_total_seconds', 'shift_end_total_seconds']].values.tolist()
    
    # Process each unique game + event_time combination
    logger.info("  Processing events...")
    event_group_cols = ['game_id', 'event_id', 'time_start_total_seconds', 'team_venue']
    if 'period' in df.columns:
        event_group_cols.append('period')
    unique_events = df[event_group_cols].drop_duplicates()
    
    event_toi_cache = {}  # (game_id, event_time, team_venue) -> {player_id: toi, team_agg, opp_agg}
    
    for _, evt in unique_events.iterrows():
        game_id = int(evt['game_id'])
        event_time = evt['time_start_total_seconds']
        event_team_venue = evt['team_venue']
        event_period = int(evt['period']) if 'period' in evt and pd.notna(evt['period']) else None
        
        if pd.isna(event_time):
            continue
        
        # Get lookup key based on whether we have period info
        if has_period and event_period is not None:
            lookup_key = (game_id, event_period)
        else:
            lookup_key = game_id
        
        if lookup_key not in shift_lookup:
            continue
        
        cache_key = (game_id, event_time, event_team_venue, event_period) if event_period is not None else (game_id, event_time, event_team_venue)
        if cache_key in event_toi_cache:
            continue
        
        # Find all players on ice at this event time
        shifts = shift_lookup[lookup_key]
        players_on_ice = {}  # player_id -> {'toi': x, 'venue': v, 'shift_end': e}
        
        for player_id, venue, shift_start, shift_end in shifts:
            # Determine time format: if shift_start > shift_end, it's countdown; else elapsed
            # Countdown: shift_start (high, e.g. 1080) >= event_time >= shift_end (low, e.g. 0)
            # Elapsed: shift_start (low, e.g. 0) <= event_time <= shift_end (high, e.g. 1080)
            is_countdown = shift_start > shift_end if pd.notna(shift_start) and pd.notna(shift_end) else True
            
            player_in_shift = False
            if is_countdown:
                # Countdown format: shift_start >= event_time >= shift_end
                if shift_start >= event_time >= shift_end:
                    player_in_shift = True
                    # TOI = time from shift start to event time (shift_start - event_time in countdown)
                    toi = shift_start - event_time
            else:
                # Elapsed format: shift_start <= event_time <= shift_end
                if shift_start <= event_time <= shift_end:
                    player_in_shift = True
                    # TOI = time from shift start to event time (event_time - shift_start in elapsed)
                    toi = event_time - shift_start
            
            if player_in_shift:
                # If player already found, keep the shift with end closest to event
                if player_id not in players_on_ice:
                    players_on_ice[player_id] = {'toi': toi, 'venue': venue, 'shift_end': shift_end}
                else:
                    # Compare which shift end is closer to event time to handle overlapping shifts
                    if is_countdown:
                        current_dist = abs(event_time - shift_end)
                        existing_dist = abs(event_time - players_on_ice[player_id]['shift_end'])
                    else:
                        current_dist = abs(event_time - shift_end)
                        existing_dist = abs(event_time - players_on_ice[player_id]['shift_end'])
                    
                    if current_dist < existing_dist:
                        players_on_ice[player_id] = {'toi': toi, 'venue': venue, 'shift_end': shift_end}
        
        # Split by team vs opp
        team_venue_full = 'away' if event_team_venue == 'a' else 'home'
        team_tois = [p['toi'] for pid, p in players_on_ice.items() if p['venue'] == team_venue_full]
        opp_tois = [p['toi'] for pid, p in players_on_ice.items() if p['venue'] != team_venue_full]
        
        # Calculate aggregates
        result = {'players': {pid: p['toi'] for pid, p in players_on_ice.items()}}
        
        if team_tois:
            result['team_avg'] = np.mean(team_tois)
            result['team_min'] = np.min(team_tois)
            result['team_max'] = np.max(team_tois)
        
        if opp_tois:
            result['opp_avg'] = np.mean(opp_tois)
            result['opp_min'] = np.min(opp_tois)
            result['opp_max'] = np.max(opp_tois)
        
        event_toi_cache[cache_key] = result
    
    # Apply to dataframe
    logger.info("  Applying TOI values...")
    for idx, row in df.iterrows():
        game_id = int(row['game_id'])
        event_time = row['time_start_total_seconds']
        team_venue = row['team_venue']
        event_period = int(row['period']) if 'period' in row and pd.notna(row.get('period')) else None
        
        # Build cache key (same logic as above)
        if has_period and event_period is not None:
            cache_key = (game_id, event_time, team_venue, event_period)
        else:
            cache_key = (game_id, event_time, team_venue)
        
        if cache_key not in event_toi_cache:
            continue
        
        result = event_toi_cache[cache_key]
        
        # Player TOI
        player_id = row.get('player_id')
        if pd.notna(player_id) and player_id in result['players']:
            df.at[idx, 'player_toi'] = result['players'][player_id]
        
        # Team aggregates
        if 'team_avg' in result:
            df.at[idx, 'team_on_ice_toi_avg'] = result['team_avg']
            df.at[idx, 'team_on_ice_toi_min'] = result['team_min']
            df.at[idx, 'team_on_ice_toi_max'] = result['team_max']
        
        # Opp aggregates
        if 'opp_avg' in result:
            df.at[idx, 'opp_on_ice_toi_avg'] = result['opp_avg']
            df.at[idx, 'opp_on_ice_toi_min'] = result['opp_min']
            df.at[idx, 'opp_on_ice_toi_max'] = result['opp_max']
    
    # Calculate fill rates
    player_toi_fill = df['player_toi'].notna().sum() / len(df) * 100
    team_toi_fill = df['team_on_ice_toi_avg'].notna().sum() / len(df) * 100
    opp_toi_fill = df['opp_on_ice_toi_avg'].notna().sum() / len(df) * 100
    
    logger.info(f"  player_toi: {player_toi_fill:.1f}% populated")
    logger.info(f"  team_on_ice_toi: {team_toi_fill:.1f}% populated")
    logger.info(f"  opp_on_ice_toi: {opp_toi_fill:.1f}% populated")
    
    return df


def calculate_shift_ratings_at_event(events_df: pd.DataFrame, shift_players_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate shift-based ratings for fact_event_players.
    
    For each player-event row, calculates:
    - event_team_avg_rating: Avg rating of teammates on ice (excl goalies)
    - opp_team_avg_rating: Avg rating of opponents on ice (excl goalies)
    - rating_vs_opp: player_rating - opp_team_avg_rating
    
    Args:
        events_df: fact_event_players with game_id, player_id, team_venue, time_start_total_seconds, player_rating
        shift_players_df: fact_shift_players with player shifts, timing, and player_rating
    
    Returns:
        DataFrame with rating columns added
    """
    logger.info("Calculating shift-based ratings at event time...")
    
    df = events_df.copy()
    
    # Initialize rating columns
    df['event_team_avg_rating'] = np.nan
    df['opp_team_avg_rating'] = np.nan
    df['rating_vs_opp'] = np.nan
    
    # Required columns check
    required = ['game_id', 'time_start_total_seconds']
    if not all(c in df.columns for c in required):
        logger.warning(f"Missing required columns for ratings: {required}")
        return df
    
    sp = shift_players_df.copy()
    
    # Check if player_rating is available
    if 'player_rating' not in sp.columns:
        logger.warning("player_rating not in shift_players - skipping rating calculation")
        return df
    
    # Exclude goalies from shift data for aggregates
    sp_skaters = sp[sp['position'] != 'G'].copy()
    
    # Pre-build lookup: game_id -> list of (player_id, venue, shift_start, shift_end, rating)
    logger.info("  Building shift-rating lookup by game...")
    shift_lookup = {}
    for game_id, group in sp_skaters.groupby('game_id'):
        shift_lookup[game_id] = group[['player_id', 'venue', 'shift_start_total_seconds', 'shift_end_total_seconds', 'player_rating']].values.tolist()
    
    # Process each unique game + event_time combination
    logger.info("  Processing events...")
    unique_events = df[['game_id', 'event_id', 'time_start_total_seconds', 'team_venue']].drop_duplicates()
    
    event_rating_cache = {}  # (game_id, event_time, team_venue) -> {team_avg, opp_avg}
    
    for _, evt in unique_events.iterrows():
        game_id = evt['game_id']
        event_time = evt['time_start_total_seconds']
        event_team_venue = evt['team_venue']
        
        if pd.isna(event_time) or game_id not in shift_lookup:
            continue
        
        cache_key = (game_id, event_time, event_team_venue)
        if cache_key in event_rating_cache:
            continue
        
        # Find all players on ice at this event time
        shifts = shift_lookup[game_id]
        players_on_ice = {}  # player_id -> {'rating': r, 'venue': v, 'shift_end': e}
        
        for player_id, venue, shift_start, shift_end, rating in shifts:
            # Countdown clock: shift_start >= event_time >= shift_end
            if shift_start >= event_time >= shift_end:
                # If player already found, keep the shift with end closest to event
                if player_id not in players_on_ice or (event_time - shift_end) < (event_time - players_on_ice[player_id]['shift_end']):
                    players_on_ice[player_id] = {'rating': rating, 'venue': venue, 'shift_end': shift_end}
        
        # Split by team vs opp
        team_venue_full = 'away' if event_team_venue == 'a' else 'home'
        team_ratings = [p['rating'] for pid, p in players_on_ice.items() if p['venue'] == team_venue_full and pd.notna(p['rating'])]
        opp_ratings = [p['rating'] for pid, p in players_on_ice.items() if p['venue'] != team_venue_full and pd.notna(p['rating'])]
        
        # Calculate aggregates
        result = {}
        if team_ratings:
            result['team_avg'] = np.mean(team_ratings)
        if opp_ratings:
            result['opp_avg'] = np.mean(opp_ratings)
        
        event_rating_cache[cache_key] = result
    
    # Apply to dataframe
    logger.info("  Applying rating values...")
    for idx, row in df.iterrows():
        cache_key = (row['game_id'], row['time_start_total_seconds'], row['team_venue'])
        if cache_key not in event_rating_cache:
            continue
        
        result = event_rating_cache[cache_key]
        
        # Team avg rating
        if 'team_avg' in result:
            df.at[idx, 'event_team_avg_rating'] = result['team_avg']
        
        # Opp avg rating
        if 'opp_avg' in result:
            df.at[idx, 'opp_team_avg_rating'] = result['opp_avg']
            
            # Calculate rating_vs_opp if player has rating
            player_rating = row.get('player_rating')
            if pd.notna(player_rating):
                df.at[idx, 'rating_vs_opp'] = player_rating - result['opp_avg']
    
    # Calculate fill rates
    team_fill = df['event_team_avg_rating'].notna().sum() / len(df) * 100
    opp_fill = df['opp_team_avg_rating'].notna().sum() / len(df) * 100
    vs_fill = df['rating_vs_opp'].notna().sum() / len(df) * 100
    
    logger.info(f"  event_team_avg_rating: {team_fill:.1f}% populated")
    logger.info(f"  opp_team_avg_rating: {opp_fill:.1f}% populated")
    logger.info(f"  rating_vs_opp: {vs_fill:.1f}% populated")
    
    return df


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
    
    # Check if shifts_player_df already has timing columns (no merge needed)
    timing_cols = ['shift_start_total_seconds', 'shift_end_total_seconds']
    has_timing_cols = all(c in shifts_player_df.columns for c in timing_cols)
    
    if has_timing_cols:
        # fact_shift_players already has timing - use directly
        shifts_combined = shifts_player_df.copy()
        logger.info("  Using timing columns already in shift_players")
    elif shifts_tracking_df is not None and len(shifts_tracking_df) > 0:
        # Need to merge with shifts to get timing
        # Note: fact_shift_players uses shift_id, fact_shifts uses shift_id and shift_key
        merge_col = 'shift_id' if 'shift_id' in shifts_player_df.columns else 'shift_key'
        tracking_merge_col = 'shift_id' if 'shift_id' in shifts_tracking_df.columns else 'shift_key'
        
        available_timing = [c for c in timing_cols if c in shifts_tracking_df.columns]
        
        if not available_timing:
            logger.warning("No timing columns found in shifts_tracking_df")
            return df
        
        shifts_combined = shifts_player_df.merge(
            shifts_tracking_df[[tracking_merge_col, 'game_id'] + available_timing],
            left_on=[merge_col, 'game_id'],
            right_on=[tracking_merge_col, 'game_id'],
            how='left'
        )
    else:
        logger.warning("No shifts_tracking_df provided and no timing in shifts_player")
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


def calculate_rating_context(events_df: pd.DataFrame, shifts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add team rating context to events based on shift data.
    
    Adds columns:
    - event_team_avg_rating: Avg rating of event player's team on ice
    - opp_team_avg_rating: Avg rating of opponent team on ice
    - rating_vs_opp: player_rating minus opp_team_avg_rating
    
    Args:
        events_df: DataFrame with events (needs shift_key, player_rating, event_team/team_name)
        shifts_df: DataFrame with shifts (needs home_avg_rating, away_avg_rating, home_team)
    
    Returns:
        DataFrame with rating context columns added
    """
    logger.info("Calculating rating context from shift data...")
    
    df = events_df.copy()
    
    # Check if we have required columns
    if 'home_avg_rating' not in shifts_df.columns:
        logger.warning("home_avg_rating not in shifts - skipping rating context")
        df['event_team_avg_rating'] = np.nan
        df['opp_team_avg_rating'] = np.nan
        df['rating_vs_opp'] = np.nan
        return df
    
    if 'shift_key' not in df.columns:
        logger.info("shift_key not in events - rating context will be added later")
        df['event_team_avg_rating'] = np.nan
        df['opp_team_avg_rating'] = np.nan
        df['rating_vs_opp'] = np.nan
        return df
    
    # Build shift rating lookup: (game_id, shift_index) -> {ratings}
    shift_rating_lookup = {}
    for _, row in shifts_df.iterrows():
        key = (int(row['game_id']), int(row['shift_index']))
        shift_rating_lookup[key] = {
            'home_avg_rating': row.get('home_avg_rating'),
            'away_avg_rating': row.get('away_avg_rating'),
            'home_team': str(row.get('home_team', '')).strip().lower(),
            'away_team': str(row.get('away_team', '')).strip().lower(),
        }
    
    logger.info(f"  Built rating lookup with {len(shift_rating_lookup)} shifts")
    
    # Import centralized key parser
    from src.utils.key_parser import parse_shift_key as _parse_shift_key
    
    def parse_shift_key(shift_key):
        """Parse shift_key using centralized utility."""
        result = _parse_shift_key(shift_key)
        if result is None:
            return None, None
        return result.game_id, result.shift_index
    
    # Get event team from available columns
    def get_event_team(row):
        for col in ['event_team', 'team_name', 'player_team']:
            if col in row.index and pd.notna(row[col]):
                return str(row[col]).strip().lower()
        return None
    
    # Calculate ratings for each event
    event_team_ratings = []
    opp_team_ratings = []
    
    for _, row in df.iterrows():
        game_id, shift_idx = parse_shift_key(row.get('shift_key'))
        
        if game_id is None or (game_id, shift_idx) not in shift_rating_lookup:
            event_team_ratings.append(np.nan)
            opp_team_ratings.append(np.nan)
            continue
        
        shift_data = shift_rating_lookup[(game_id, shift_idx)]
        event_team = get_event_team(row)
        home_team = shift_data['home_team']
        
        # Determine if event team is home or away
        if event_team and home_team:
            if event_team in home_team or home_team in event_team:
                # Event team is home
                event_team_ratings.append(shift_data['home_avg_rating'])
                opp_team_ratings.append(shift_data['away_avg_rating'])
            else:
                # Event team is away
                event_team_ratings.append(shift_data['away_avg_rating'])
                opp_team_ratings.append(shift_data['home_avg_rating'])
        else:
            # Can't determine, use home as default
            event_team_ratings.append(shift_data['home_avg_rating'])
            opp_team_ratings.append(shift_data['away_avg_rating'])
    
    df['event_team_avg_rating'] = event_team_ratings
    df['opp_team_avg_rating'] = opp_team_ratings
    
    # Calculate rating vs opponent
    if 'player_rating' in df.columns:
        df['rating_vs_opp'] = df['player_rating'] - df['opp_team_avg_rating']
    else:
        df['rating_vs_opp'] = np.nan
    
    # Log fill rates
    for col in ['event_team_avg_rating', 'opp_team_avg_rating', 'rating_vs_opp']:
        fill = df[col].notna().sum()
        pct = 100 * fill / len(df) if len(df) > 0 else 0
        logger.info(f"  {col}: {fill}/{len(df)} ({pct:.1f}%)")
    
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
    # v23.1: Simplified TOI columns - removed unused event_player_2-6_toi, opp_player_2-6_toi
    toi_cols = ['player_toi', 'team_on_ice_toi_avg', 'team_on_ice_toi_min', 'team_on_ice_toi_max',
                 'opp_on_ice_toi_avg', 'opp_on_ice_toi_min', 'opp_on_ice_toi_max']
    all_new_cols = time_cols + toi_cols
    
    # ========================================
    # 0. ADD SHIFT_ID FK TO EVENTS
    # ========================================
    # Links each event to the shift it occurred during
    # CRITICAL: Event times are ASCENDING (0 = period start), shift times are DESCENDING (1080 = period start)
    logger.info("\n--- Adding shift_id FK ---")
    
    if len(shifts_tracking) > 0 and 'shift_start_total_seconds' in shifts_tracking.columns:
        # Find period max time for each game/period
        period_max = {}
        for _, shift in shifts_tracking.iterrows():
            try:
                key = (int(shift['game_id']), int(shift['period']))
                start = float(shift['shift_start_total_seconds']) if pd.notna(shift['shift_start_total_seconds']) else 0
                if key not in period_max or start > period_max[key]:
                    period_max[key] = start
            except (ValueError, TypeError):
                continue
        
        # Build shift lookup
        shift_ranges = {}
        for _, shift in shifts_tracking.iterrows():
            try:
                key = (int(shift['game_id']), int(shift['period']))
                if key not in shift_ranges:
                    shift_ranges[key] = []
                shift_ranges[key].append((
                    shift['shift_id'],
                    float(shift['shift_start_total_seconds']) if pd.notna(shift['shift_start_total_seconds']) else 0,
                    float(shift['shift_end_total_seconds']) if pd.notna(shift['shift_end_total_seconds']) else 0
                ))
            except (ValueError, TypeError):
                continue
        
        def find_shift_id(row):
            """Find shift_id for an event based on game, period, and time."""
            try:
                game_id = int(row['game_id'])
                period = int(row['period']) if pd.notna(row.get('period')) else 1
                
                # Get event time (elapsed format: 0 = period start)
                event_elapsed = row.get('time_start_total_seconds')
                if pd.isna(event_elapsed):
                    return None
                event_elapsed = float(event_elapsed)
                
                key = (game_id, period)
                if key not in shift_ranges or key not in period_max:
                    return None
                
                # Convert elapsed to countdown: countdown = period_max - elapsed
                event_countdown = period_max[key] - event_elapsed
                
                # Find shift where shift_end <= event_countdown <= shift_start
                for shift_id, start, end in shift_ranges[key]:
                    if end <= event_countdown <= start:
                        return shift_id
                
                return None
            except (ValueError, TypeError):
                return None
        
        # Apply to fact_event_players
        events_tracking['shift_id'] = events_tracking.apply(find_shift_id, axis=1)
        shift_fill = events_tracking['shift_id'].notna().sum()
        logger.info(f"  fact_event_players.shift_id: {shift_fill}/{len(events_tracking)} ({100*shift_fill/len(events_tracking):.1f}%)")
    else:
        logger.warning("  Shift time columns not found, skipping shift_id FK")
    
    # ========================================
    # 1. ENHANCE fact_event_players (single player per row)
    # ========================================
    logger.info("\n--- Enhancing fact_event_players ---")
    events_tracking = calculate_time_to_events(events_tracking)
    
    # v23.1: Use new shift-based TOI calculation
    if len(shifts_player) > 0:
        events_tracking = calculate_shift_toi_at_event(events_tracking, shifts_player)
    
    # Remove old unused TOI columns if they exist
    old_toi_cols = [f'event_player_{i}_toi' for i in range(1, 7)] + [f'opp_player_{i}_toi' for i in range(1, 7)]
    existing_old_cols = [c for c in old_toi_cols if c in events_tracking.columns]
    if existing_old_cols:
        events_tracking = events_tracking.drop(columns=existing_old_cols)
        logger.info(f"  Removed {len(existing_old_cols)} unused TOI columns")
    
    # Note: Team TOI aggregates are now calculated in calculate_shift_toi_at_event
    
    # v23.1: Add rating context from shift_player data (same pattern as TOI)
    if len(shifts_player) > 0:
        events_tracking = calculate_shift_ratings_at_event(events_tracking, shifts_player)
    
    # Save enhanced fact_event_players
    save_output_table(events_tracking, 'fact_event_players', OUTPUT_DIR)
    results['fact_event_players'] = len(events_tracking)
    logger.info(f"Saved fact_event_players: {len(events_tracking)} rows, {len(events_tracking.columns)} cols")
    
    # ========================================
    # 2. ENHANCE fact_events (has comma-separated player IDs - calculate TOI directly)
    # ========================================
    try:
        events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv', low_memory=False)
        logger.info(f"\n--- Enhancing fact_events ---")
        logger.info(f"Loaded: {len(events)} rows")
        
        # Add shift_id FK from events_tracking (already calculated)
        if 'shift_id' in events_tracking.columns:
            shift_id_map = events_tracking.groupby('event_id')['shift_id'].first().to_dict()
            events['shift_id'] = events['event_id'].map(shift_id_map)
            shift_fill = events['shift_id'].notna().sum()
            logger.info(f"  fact_events.shift_id: {shift_fill}/{len(events)} ({100*shift_fill/len(events):.1f}%)")
        
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
        
        # v23.2: Add rating columns from fact_event_players (already calculated)
        # Get first row per event from tracking which has the ratings
        if 'event_team_avg_rating' in events_tracking.columns:
            rating_cols = ['event_team_avg_rating', 'opp_team_avg_rating', 'rating_vs_opp']
            existing_rating_cols = [c for c in rating_cols if c in events_tracking.columns]
            if existing_rating_cols:
                rating_context = events_tracking.groupby('event_id')[existing_rating_cols].first().reset_index()
                events = events.merge(rating_context, on='event_id', how='left', suffixes=('', '_new'))
                # Handle potential column conflicts
                for col in existing_rating_cols:
                    if f'{col}_new' in events.columns:
                        events[col] = events[col].fillna(events[f'{col}_new'])
                        events = events.drop(columns=[f'{col}_new'])
                logger.info(f"Added rating columns from fact_event_players: {existing_rating_cols}")
        else:
            # Fallback: empty columns
            for col in ['event_team_avg_rating', 'opp_team_avg_rating', 'rating_vs_opp']:
                if col not in events.columns:
                    events[col] = np.nan
        
        # v23.2: Remove unused/empty columns from fact_events
        remove_cols = [
            'team_venue_abv',  # Unused abbreviation
            'player_toi',  # Player-level metric, not for event-level
        ]
        existing_remove = [c for c in remove_cols if c in events.columns]
        if existing_remove:
            events = events.drop(columns=existing_remove)
            logger.info(f"Removed unused columns: {existing_remove}")
        
        save_output_table(events, 'fact_events', OUTPUT_DIR)
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
