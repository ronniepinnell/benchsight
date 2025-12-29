#!/usr/bin/env python3
"""
Rebuild all fact tables with proper primary/foreign keys and normalization.
Creates star schema compliant tables.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path('data/output')
RAW_DIR = Path('data/raw/games')


def generate_key(game_id, index, prefix='E'):
    """Generate a 12-character key: E{game_id:05d}{index:06d}"""
    if pd.isna(index):
        return None
    return f"{prefix}{int(game_id):05d}{int(index):06d}"


def rebuild_fact_events(games):
    """
    Build fact_events (wide) - one row per unique event.
    Columns:
    - event_key (PK)
    - game_id, period, event_index
    - event_type_id (FK), zone_id (FK), venue_id (FK)
    - All event attributes (no underscore columns)
    """
    logger.info("Building fact_events (wide)...")
    
    all_events = []
    
    for game_id in games:
        tracking_file = RAW_DIR / game_id / f'{game_id}_tracking.xlsx'
        if not tracking_file.exists():
            continue
        
        try:
            events = pd.read_excel(tracking_file, sheet_name='events')
        except:
            continue
        
        # Remove columns ending with underscore (staging columns)
        clean_cols = [c for c in events.columns if not c.endswith('_')]
        events = events[clean_cols]
        
        # Get unique events (one row per event_index)
        if 'event_index' not in events.columns:
            continue
        
        # Filter out rows without event_index
        events = events[events['event_index'].notna()]
        if len(events) == 0:
            continue
            
        # Group by event_index to get unique events (take first player's row for event-level data)
        event_cols = [c for c in events.columns if c not in ['player_role', 'role_number', 'player_id', 'player_team', 'player_game_number']]
        unique_events = events.drop_duplicates(subset=['event_index'], keep='first')[event_cols].copy()
        
        # Normalize event_type column
        if 'Type' in unique_events.columns and 'event_type' not in unique_events.columns:
            unique_events['event_type'] = unique_events['Type']
        
        # Generate event_key
        unique_events['event_key'] = unique_events['event_index'].apply(
            lambda x: generate_key(game_id, x, 'E')
        )
        
        # Add foreign keys
        unique_events['game_id'] = int(game_id)
        
        # Map to dimension IDs (simplified - use string matching)
        # In production, these would join to dim tables
        
        all_events.append(unique_events)
    
    if not all_events:
        return pd.DataFrame()
    
    df = pd.concat(all_events, ignore_index=True)
    
    # Reorder columns - keys first
    key_cols = ['event_key', 'game_id', 'period', 'event_index', 'linked_event_index', 
                'sequence_index', 'play_index']
    other_cols = [c for c in df.columns if c not in key_cols]
    df = df[[c for c in key_cols if c in df.columns] + other_cols]
    
    logger.info(f"  fact_events: {len(df)} rows, {len(df.columns)} cols")
    return df


def rebuild_fact_events_long(games):
    """
    Build fact_events_long - one row per player per event.
    Columns:
    - event_player_key (PK)
    - event_key (FK to fact_events)
    - player_id (FK to dim_player)
    - game_id, event_index
    - player_role, role_number
    """
    logger.info("Building fact_events_long (player-level)...")
    
    all_records = []
    
    for game_id in games:
        tracking_file = RAW_DIR / game_id / f'{game_id}_tracking.xlsx'
        if not tracking_file.exists():
            continue
        
        try:
            events = pd.read_excel(tracking_file, sheet_name='events')
        except:
            continue
        
        # Remove columns ending with underscore
        clean_cols = [c for c in events.columns if not c.endswith('_')]
        events = events[clean_cols]
        
        if 'event_index' not in events.columns:
            continue
        
        # Filter out rows without event_index
        events = events[events['event_index'].notna()]
        
        # Keep only player-level columns
        player_cols = ['event_index', 'player_role', 'role_number', 'player_id', 
                      'player_game_number', 'player_team', 'period', 
                      'event_detail', 'event_detail_2', 'event_successful',
                      'play_detail1', 'play_detail_2', 'play_detail_successful',
                      'team_venue', 'side_of_puck']
        
        # Add event_type (might be 'Type' in raw data)
        if 'Type' in events.columns:
            events['event_type'] = events['Type']
        if 'event_type' in events.columns:
            player_cols.append('event_type')
        
        # Add play_detail (alias for play_detail1)
        if 'play_detail1' in events.columns:
            events['play_detail'] = events['play_detail1']
            player_cols.append('play_detail')
            
        player_cols = [c for c in player_cols if c in events.columns]
        
        player_events = events[player_cols].copy()
        
        # Remove rows without player_id
        player_events = player_events[player_events['player_id'].notna()]
        
        if len(player_events) == 0:
            continue
        
        # Add player_name from dim_player if available
        try:
            dim_player = pd.read_csv(OUTPUT_DIR / 'dim_player.csv')
            player_names = dim_player.set_index('player_id')['player_full_name'].to_dict()
            player_events['player_name'] = player_events['player_id'].map(player_names)
        except:
            player_events['player_name'] = None
        
        # Generate keys
        player_events['game_id'] = int(game_id)
        player_events['event_key'] = player_events['event_index'].apply(
            lambda x: generate_key(game_id, x, 'E')
        )
        
        # Generate event_player_key using row index
        player_events = player_events.reset_index(drop=True)
        player_events['event_player_key'] = player_events.apply(
            lambda r: generate_key(game_id, int(r['event_index']) * 10 + int(r.get('role_number', 0) or 0), 'P'), axis=1
        )
        
        all_records.append(player_events)
    
    if not all_records:
        return pd.DataFrame()
    
    df = pd.concat(all_records, ignore_index=True)
    
    # Reorder columns - keys first
    key_cols = ['event_player_key', 'event_key', 'game_id', 'player_id', 'player_name', 
                'event_index', 'player_role', 'role_number', 'event_type']
    other_cols = [c for c in df.columns if c not in key_cols]
    df = df[[c for c in key_cols if c in df.columns] + other_cols]
    
    logger.info(f"  fact_events_long: {len(df)} rows, {len(df.columns)} cols")
    return df


def rebuild_fact_shifts(games):
    """
    Build fact_shifts (wide) - one row per shift.
    """
    logger.info("Building fact_shifts (wide)...")
    
    all_shifts = []
    
    for game_id in games:
        tracking_file = RAW_DIR / game_id / f'{game_id}_tracking.xlsx'
        if not tracking_file.exists():
            continue
        
        try:
            shifts = pd.read_excel(tracking_file, sheet_name='shifts')
        except:
            continue
        
        if 'shift_index' not in shifts.columns:
            continue
        
        # Generate shift_key
        shifts['shift_key'] = shifts['shift_index'].apply(
            lambda x: generate_key(game_id, x, 'S')
        )
        shifts['game_id'] = int(game_id)
        
        all_shifts.append(shifts)
    
    if not all_shifts:
        return pd.DataFrame()
    
    df = pd.concat(all_shifts, ignore_index=True)
    
    # Reorder columns
    key_cols = ['shift_key', 'game_id', 'shift_index', 'Period']
    other_cols = [c for c in df.columns if c not in key_cols]
    df = df[[c for c in key_cols if c in df.columns] + other_cols]
    
    logger.info(f"  fact_shifts: {len(df)} rows, {len(df.columns)} cols")
    return df


def rebuild_fact_shifts_long(games):
    """
    Build fact_shifts_long - one row per player per shift.
    Uses existing logic from etl_orchestrator but adds proper keys.
    """
    logger.info("Building fact_shifts_long (player-level)...")
    
    player_cols = {
        'home': ['home_forward_1', 'home_forward_2', 'home_forward_3',
                 'home_defense_1', 'home_defense_2', 'home_xtra', 'home_goalie'],
        'away': ['away_forward_1', 'away_forward_2', 'away_forward_3',
                 'away_defense_1', 'away_defense_2', 'away_xtra', 'away_goalie']
    }
    
    all_records = []
    
    for game_id in games:
        tracking_file = RAW_DIR / game_id / f'{game_id}_tracking.xlsx'
        if not tracking_file.exists():
            continue
        
        try:
            shifts = pd.read_excel(tracking_file, sheet_name='shifts')
            roster = pd.read_excel(tracking_file, sheet_name='game_rosters', header=1)
        except:
            continue
        
        # Build player lookup from roster
        player_lookup = {}
        for _, row in roster.iterrows():
            num = row.get('player_game_number')
            pid = row.get('player_id')
            venue = str(row.get('team_venue', '')).lower()
            # Normalize venue to 'home'/'away'
            if venue in ['h', 'home']:
                venue = 'home'
            elif venue in ['a', 'away']:
                venue = 'away'
            if pd.notna(num) and pd.notna(pid):
                player_lookup[(int(num), venue)] = {
                    'player_id': pid,
                    'player_name': row.get('player_full_name', ''),
                    'position': row.get('player_position', '')
                }
        
        for idx, shift in shifts.iterrows():
            shift_index = shift.get('shift_index')
            if pd.isna(shift_index):
                continue
            
            shift_key = generate_key(game_id, shift_index, 'S')
            
            # Detect goals
            stop_type = str(shift.get('shift_stop_type', '')).strip().lower()
            home_goal = 1 if stop_type == 'home goal' else 0
            away_goal = 1 if stop_type == 'away goal' else 0
            
            for venue, cols in player_cols.items():
                for col in cols:
                    if col in shift and pd.notna(shift[col]):
                        player_num = int(shift[col])
                        slot = col.replace('home_', '').replace('away_', '')
                        
                        # Lookup player
                        player_info = player_lookup.get((player_num, venue), {})
                        
                        # Generate shift_player_key
                        slot_num = {'forward_1': 1, 'forward_2': 2, 'forward_3': 3,
                                   'defense_1': 4, 'defense_2': 5, 'xtra': 6, 'goalie': 7}.get(slot, 0)
                        venue_num = 0 if venue == 'home' else 1
                        shift_player_key = generate_key(
                            game_id, 
                            int(shift_index) * 100 + venue_num * 10 + slot_num, 
                            'L'
                        )
                        
                        # Plus/minus from source
                        pm_plus_col = f'{venue}_team_plus'
                        pm_minus_col = f'{venue}_team_minus'
                        pm_plus = float(shift.get(pm_plus_col, 0) or 0)
                        pm_minus = float(shift.get(pm_minus_col, 0) or 0)
                        
                        # EN flags
                        team_en_col = f'{venue}_team_en'
                        opp_venue = 'away' if venue == 'home' else 'home'
                        opp_en_col = f'{opp_venue}_team_en'
                        team_en = float(shift.get(team_en_col, 0) or 0)
                        opp_en = float(shift.get(opp_en_col, 0) or 0)
                        
                        # Duration calculations
                        shift_dur = float(shift.get('shift_duration', 0) or 0)
                        stop_time = float(shift.get('stoppage_time', 0) or 0)
                        playing_dur = shift_dur - stop_time
                        
                        all_records.append({
                            'shift_player_key': shift_player_key,
                            'shift_key': shift_key,
                            'game_id': int(game_id),
                            'shift_index': int(shift_index),
                            'player_number': player_num,
                            'player_id': player_info.get('player_id'),
                            'player_name': player_info.get('player_name'),
                            'venue': venue,
                            'slot': slot,
                            'period': shift.get('Period', shift.get('period')),
                            'shift_duration': shift_dur,
                            'playing_duration': playing_dur,
                            'situation': shift.get('situation'),
                            'strength': shift.get('strength'),
                            'stoppage_time': stop_time,
                            'pm_plus_ev': pm_plus,
                            'pm_minus_ev': pm_minus,
                            'goal_for': home_goal if venue == 'home' else away_goal,
                            'goal_against': away_goal if venue == 'home' else home_goal,
                            'team_en': team_en,
                            'opp_en': opp_en,
                        })
    
    if not all_records:
        return pd.DataFrame()
    
    df = pd.DataFrame(all_records)
    
    # Calculate logical_shift_number per player per game
    # A new logical shift starts when shift_index has a gap OR period changes
    df = df.sort_values(['game_id', 'player_id', 'shift_index'])
    
    def calc_logical_shifts(group):
        group = group.copy()
        logical_shift = 1
        logical_shifts = [logical_shift]
        prev_idx = None
        prev_period = None
        
        for i, row in list(group.iterrows())[1:]:
            curr_idx = row['shift_index']
            curr_period = row['period']
            
            # New logical shift if gap in shift_index > 1 OR period changed
            if prev_idx is not None:
                if curr_idx - prev_idx > 1 or curr_period != prev_period:
                    logical_shift += 1
            
            logical_shifts.append(logical_shift)
            prev_idx = curr_idx
            prev_period = curr_period
        
        group['logical_shift_number'] = logical_shifts
        return group
    
    df = df.groupby(['game_id', 'player_id'], group_keys=False).apply(calc_logical_shifts)
    
    logger.info(f"  fact_shifts_long: {len(df)} rows, {len(df.columns)} cols")
    return df


def rebuild_fact_team_zone_time(games):
    """
    Build fact_team_zone_time with CORRECT per-team zone calculations.
    Zone is relative to TEAM perspective:
    - OZone = offensive zone for that team
    - DZone = defensive zone for that team
    """
    logger.info("Building fact_team_zone_time (corrected)...")
    
    all_records = []
    
    for game_id in games:
        tracking_file = RAW_DIR / game_id / f'{game_id}_tracking.xlsx'
        if not tracking_file.exists():
            continue
        
        try:
            events = pd.read_excel(tracking_file, sheet_name='events')
        except:
            continue
        
        # Need home_team_zone and away_team_zone columns
        if 'home_team_zone' not in events.columns or 'away_team_zone' not in events.columns:
            # Try to derive from event_team_zone and team_venue
            if 'event_team_zone' in events.columns and 'team_venue' in events.columns:
                def get_home_zone(row):
                    zone = str(row.get('event_team_zone', '')).lower()
                    venue = str(row.get('team_venue', '')).lower()
                    if venue in ['home', 'h']:
                        return zone
                    else:
                        # Flip for away team events
                        if zone == 'o':
                            return 'd'
                        elif zone == 'd':
                            return 'o'
                        return zone
                
                def get_away_zone(row):
                    zone = str(row.get('event_team_zone', '')).lower()
                    venue = str(row.get('team_venue', '')).lower()
                    if venue in ['away', 'a']:
                        return zone
                    else:
                        # Flip for home team events
                        if zone == 'o':
                            return 'd'
                        elif zone == 'd':
                            return 'o'
                        return zone
                
                events['home_team_zone'] = events.apply(get_home_zone, axis=1)
                events['away_team_zone'] = events.apply(get_away_zone, axis=1)
        
        # Normalize zone values to lowercase
        events['home_team_zone'] = events['home_team_zone'].str.lower()
        events['away_team_zone'] = events['away_team_zone'].str.lower()
        
        # Count events per zone for HOME team
        home_ozone = len(events[events['home_team_zone'] == 'o'])
        home_dzone = len(events[events['home_team_zone'] == 'd'])
        home_nzone = len(events[events['home_team_zone'] == 'n'])
        home_total = home_ozone + home_dzone + home_nzone
        
        # Count events per zone for AWAY team
        away_ozone = len(events[events['away_team_zone'] == 'o'])
        away_dzone = len(events[events['away_team_zone'] == 'd'])
        away_nzone = len(events[events['away_team_zone'] == 'n'])
        away_total = away_ozone + away_dzone + away_nzone
        
        # Home record
        all_records.append({
            'zone_time_key': generate_key(game_id, 1, 'Z'),
            'game_id': int(game_id),
            'venue': 'home',
            'ozone_events': home_ozone,
            'dzone_events': home_dzone,
            'nzone_events': home_nzone,
            'total_events': home_total,
            'ozone_pct': round(home_ozone / home_total * 100, 1) if home_total > 0 else 0,
            'dzone_pct': round(home_dzone / home_total * 100, 1) if home_total > 0 else 0,
            'nzone_pct': round(home_nzone / home_total * 100, 1) if home_total > 0 else 0,
        })
        
        # Away record
        all_records.append({
            'zone_time_key': generate_key(game_id, 2, 'Z'),
            'game_id': int(game_id),
            'venue': 'away',
            'ozone_events': away_ozone,
            'dzone_events': away_dzone,
            'nzone_events': away_nzone,
            'total_events': away_total,
            'ozone_pct': round(away_ozone / away_total * 100, 1) if away_total > 0 else 0,
            'dzone_pct': round(away_dzone / away_total * 100, 1) if away_total > 0 else 0,
            'nzone_pct': round(away_nzone / away_total * 100, 1) if away_total > 0 else 0,
        })
    
    df = pd.DataFrame(all_records)
    logger.info(f"  fact_team_zone_time: {len(df)} rows")
    return df


def main():
    """Rebuild all tables with proper keys."""
    print("=" * 70)
    print("REBUILDING TABLES WITH PROPER KEYS")
    print("=" * 70)
    
    # Get available games
    games = [d.name for d in RAW_DIR.iterdir() if d.is_dir() and (d / f'{d.name}_tracking.xlsx').exists()]
    print(f"\nGames found: {games}")
    
    # Rebuild each table
    fact_events = rebuild_fact_events(games)
    fact_events_long = rebuild_fact_events_long(games)
    fact_shifts = rebuild_fact_shifts(games)
    fact_shifts_long = rebuild_fact_shifts_long(games)
    fact_team_zone = rebuild_fact_team_zone_time(games)
    
    # Save tables
    print("\nSaving tables...")
    fact_events.to_csv(OUTPUT_DIR / 'fact_events.csv', index=False)
    fact_events_long.to_csv(OUTPUT_DIR / 'fact_events_long.csv', index=False)
    fact_shifts.to_csv(OUTPUT_DIR / 'fact_shifts.csv', index=False)
    fact_shifts_long.to_csv(OUTPUT_DIR / 'fact_shifts_long.csv', index=False)
    fact_team_zone.to_csv(OUTPUT_DIR / 'fact_team_zone_time.csv', index=False)
    
    # Also update fact_events_player (keep for backward compatibility but clean it)
    fact_events_long.to_csv(OUTPUT_DIR / 'fact_events_player.csv', index=False)
    fact_shifts_long.to_csv(OUTPUT_DIR / 'fact_shifts_player.csv', index=False)
    
    print("\n" + "=" * 70)
    print("REBUILD COMPLETE")
    print("=" * 70)
    print(f"fact_events:        {len(fact_events)} rows")
    print(f"fact_events_long:   {len(fact_events_long)} rows")
    print(f"fact_shifts:        {len(fact_shifts)} rows")
    print(f"fact_shifts_long:   {len(fact_shifts_long)} rows")
    print(f"fact_team_zone_time: {len(fact_team_zone)} rows")


if __name__ == '__main__':
    main()
