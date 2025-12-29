#!/usr/bin/env python3
"""
Flexible Stats Builder for H2H, WOWY, Line Combos, Player Pairs.

This module provides easy extensibility for adding new stats to aggregated tables.
Add new stat functions to STAT_REGISTRY to automatically include them.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Callable, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path('data/output')


# =============================================================================
# STAT REGISTRY - ADD NEW STATS HERE
# =============================================================================
# Each stat is a dict with:
#   'name': column name in output
#   'func': function(shifts_df, events_df, player_ids, game_id) -> value
#   'tables': list of tables to add this stat to ('h2h', 'wowy', 'line_combos', 'pairs')

def calc_toi_together(shifts, events, player_ids, game_id):
    """Total TOI when players are on ice together."""
    # Filter to shifts with all players present
    shift_counts = shifts.groupby('shift_index')['player_id'].apply(set)
    together_shifts = shift_counts[shift_counts.apply(lambda x: set(player_ids).issubset(x))].index
    return shifts[shifts['shift_index'].isin(together_shifts)]['shift_duration'].sum()

def calc_goals_for(shifts, events, player_ids, game_id):
    """Goals for while players on ice together."""
    shift_counts = shifts.groupby('shift_index')['player_id'].apply(set)
    together_shifts = shift_counts[shift_counts.apply(lambda x: set(player_ids).issubset(x))].index
    return shifts[shifts['shift_index'].isin(together_shifts)]['goal_for'].sum()

def calc_goals_against(shifts, events, player_ids, game_id):
    """Goals against while players on ice together."""
    shift_counts = shifts.groupby('shift_index')['player_id'].apply(set)
    together_shifts = shift_counts[shift_counts.apply(lambda x: set(player_ids).issubset(x))].index
    return shifts[shifts['shift_index'].isin(together_shifts)]['goal_against'].sum()

def calc_corsi_for(shifts, events, player_ids, game_id):
    """Corsi for (shots + blocks + misses) while together."""
    shift_counts = shifts.groupby('shift_index')['player_id'].apply(set)
    together_shifts = shift_counts[shift_counts.apply(lambda x: set(player_ids).issubset(x))].index
    together_shift_indices = together_shifts.tolist()
    
    # Get events during those shifts
    if events.empty:
        return 0
    
    venue = shifts[shifts['player_id'].isin(player_ids)]['venue'].mode()
    venue = venue.iloc[0] if len(venue) > 0 else None
    
    team_events = events[
        (events['shift_index'].isin(together_shift_indices)) &
        (events['team_venue'].str.lower() == venue)
    ]
    
    shot_events = team_events[team_events['event_type'].isin(['Shot', 'Goal'])]
    return len(shot_events.drop_duplicates('event_index'))

def calc_corsi_against(shifts, events, player_ids, game_id):
    """Corsi against while together."""
    shift_counts = shifts.groupby('shift_index')['player_id'].apply(set)
    together_shifts = shift_counts[shift_counts.apply(lambda x: set(player_ids).issubset(x))].index
    together_shift_indices = together_shifts.tolist()
    
    if events.empty:
        return 0
    
    venue = shifts[shifts['player_id'].isin(player_ids)]['venue'].mode()
    venue = venue.iloc[0] if len(venue) > 0 else None
    opp_venue = 'away' if venue == 'home' else 'home'
    
    opp_events = events[
        (events['shift_index'].isin(together_shift_indices)) &
        (events['team_venue'].str.lower() == opp_venue)
    ]
    
    shot_events = opp_events[opp_events['event_type'].isin(['Shot', 'Goal'])]
    return len(shot_events.drop_duplicates('event_index'))

def calc_ozone_pct(shifts, events, player_ids, game_id):
    """O-zone possession % while together."""
    shift_counts = shifts.groupby('shift_index')['player_id'].apply(set)
    together_shifts = shift_counts[shift_counts.apply(lambda x: set(player_ids).issubset(x))].index
    together_shift_indices = together_shifts.tolist()
    
    if events.empty or 'event_team_zone' not in events.columns:
        return None
    
    venue = shifts[shifts['player_id'].isin(player_ids)]['venue'].mode()
    venue = venue.iloc[0] if len(venue) > 0 else None
    
    team_events = events[
        (events['shift_index'].isin(together_shift_indices)) &
        (events['team_venue'].str.lower() == venue) &
        (events['event_team_zone'].notna())
    ]
    
    if len(team_events) == 0:
        return None
    
    ozone = len(team_events[team_events['event_team_zone'].str.lower() == 'o'])
    return round(ozone / len(team_events) * 100, 1)

def calc_xgf(shifts, events, player_ids, game_id):
    """Expected goals for (simplified - shots weighted by type)."""
    shift_counts = shifts.groupby('shift_index')['player_id'].apply(set)
    together_shifts = shift_counts[shift_counts.apply(lambda x: set(player_ids).issubset(x))].index
    together_shift_indices = together_shifts.tolist()
    
    if events.empty:
        return 0
    
    venue = shifts[shifts['player_id'].isin(player_ids)]['venue'].mode()
    venue = venue.iloc[0] if len(venue) > 0 else None
    
    team_events = events[
        (events['shift_index'].isin(together_shift_indices)) &
        (events['team_venue'].str.lower() == venue)
    ]
    
    # Weight shots by type (simplified xG)
    xg = 0
    shots = team_events[team_events['event_type'] == 'Shot']
    for _, shot in shots.drop_duplicates('event_index').iterrows():
        detail = str(shot.get('event_detail', '')).lower()
        if 'goal' in detail:
            xg += 1.0
        elif 'onnet' in detail:
            xg += 0.08
        elif 'blocked' in detail:
            xg += 0.02
        else:
            xg += 0.03
    
    return round(xg, 2)


# Registry of all stats to calculate
STAT_REGISTRY = [
    {'name': 'toi_together', 'func': calc_toi_together, 'tables': ['h2h', 'wowy', 'line_combos', 'pairs']},
    {'name': 'goals_for', 'func': calc_goals_for, 'tables': ['h2h', 'wowy', 'line_combos', 'pairs']},
    {'name': 'goals_against', 'func': calc_goals_against, 'tables': ['h2h', 'wowy', 'line_combos', 'pairs']},
    {'name': 'corsi_for', 'func': calc_corsi_for, 'tables': ['h2h', 'wowy', 'line_combos']},
    {'name': 'corsi_against', 'func': calc_corsi_against, 'tables': ['h2h', 'wowy', 'line_combos']},
    {'name': 'ozone_pct', 'func': calc_ozone_pct, 'tables': ['h2h', 'wowy', 'line_combos']},
    {'name': 'xgf', 'func': calc_xgf, 'tables': ['h2h', 'wowy', 'line_combos']},
]


def add_stats_to_table(table_name: str):
    """Add all registered stats to a table."""
    logger.info(f"Adding stats to {table_name}...")
    
    table_file = OUTPUT_DIR / f'fact_{table_name}.csv'
    if not table_file.exists():
        logger.warning(f"  {table_file} not found")
        return
    
    df = pd.read_csv(table_file)
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shifts_player.csv')
    events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
    
    # Normalize game_id types
    shifts['game_id'] = shifts['game_id'].astype(int)
    events['game_id'] = pd.to_numeric(events['game_id'], errors='coerce').astype('Int64')
    df['game_id'] = pd.to_numeric(df['game_id'], errors='coerce').astype('Int64')
    
    # Get player ID columns based on table type
    if table_name == 'h2h':
        player_cols = ['player_1_id', 'player_2_id']
    elif table_name == 'wowy':
        player_cols = ['player_id', 'teammate_id'] if 'teammate_id' in df.columns else ['player_1_id', 'player_2_id']
    elif table_name == 'line_combos':
        player_cols = [c for c in df.columns if c.startswith('player_') and c.endswith('_id') and 'team' not in c]
    else:
        player_cols = ['player_1_id', 'player_2_id']
    
    # Get stats for this table
    table_stats = [s for s in STAT_REGISTRY if table_name in s['tables']]
    
    # Calculate stats for each row
    for stat in table_stats:
        if stat['name'] in df.columns:
            continue  # Skip if already exists
        
        logger.info(f"  Calculating {stat['name']}...")
        
        values = []
        for _, row in df.iterrows():
            game_id = row['game_id']
            player_ids = [row[c] for c in player_cols if c in row and pd.notna(row[c])]
            
            game_shifts = shifts[shifts['game_id'] == game_id]
            game_events = events[events['game_id'] == game_id]
            
            try:
                val = stat['func'](game_shifts, game_events, player_ids, game_id)
            except Exception as e:
                val = None
            
            values.append(val)
        
        df[stat['name']] = values
    
    df.to_csv(table_file, index=False)
    logger.info(f"  ✓ {table_name}: Added {len(table_stats)} stats")


def build_player_event_chains():
    """Build table of player chains per event (both teams)."""
    logger.info("Building fact_player_event_chains...")
    
    events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
    
    # Group by game_id and event_index to get all players per event
    chains = []
    
    for (game_id, event_index), group in events.groupby(['game_id', 'event_index']):
        # Separate by team
        home_players = group[group['team_venue'].str.lower() == 'home']['player_id'].dropna().unique().tolist()
        away_players = group[group['team_venue'].str.lower() == 'away']['player_id'].dropna().unique().tolist()
        
        # Get event details from first row
        first_row = group.iloc[0]
        
        chains.append({
            'event_chain_key': f"EC{int(game_id):05d}{int(event_index):06d}",
            'game_id': game_id,
            'event_index': event_index,
            'event_key': first_row.get('event_key'),
            'event_type': first_row.get('event_type'),
            'period': first_row.get('period'),
            'home_player_count': len(home_players),
            'away_player_count': len(away_players),
            'home_player_1': home_players[0] if len(home_players) > 0 else None,
            'home_player_2': home_players[1] if len(home_players) > 1 else None,
            'home_player_3': home_players[2] if len(home_players) > 2 else None,
            'away_player_1': away_players[0] if len(away_players) > 0 else None,
            'away_player_2': away_players[1] if len(away_players) > 1 else None,
            'away_player_3': away_players[2] if len(away_players) > 2 else None,
            'home_players': ','.join(home_players),
            'away_players': ','.join(away_players),
            'running_video_time': first_row.get('running_video_time'),
            'event_running_start': first_row.get('event_running_start'),
        })
    
    df = pd.DataFrame(chains)
    df.to_csv(OUTPUT_DIR / 'fact_player_event_chains.csv', index=False)
    logger.info(f"  ✓ fact_player_event_chains: {len(df)} rows")


def main():
    """Add stats to all aggregated tables."""
    print("=" * 70)
    print("STATS BUILDER")
    print("=" * 70)
    
    # Add stats to existing tables
    for table in ['h2h', 'wowy', 'line_combos']:
        add_stats_to_table(table)
    
    # Build player event chains
    build_player_event_chains()
    
    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)
    print("\nTo add new stats, edit STAT_REGISTRY in src/stats_builder.py")


if __name__ == '__main__':
    main()
