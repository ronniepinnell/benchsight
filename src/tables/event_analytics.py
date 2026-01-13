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

OUTPUT_DIR = Path('data/output')


def save_table(df: pd.DataFrame, name: str) -> int:
    """Save table to CSV and return row count."""
    path = OUTPUT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    return len(df)


def load_table(name: str) -> pd.DataFrame:
    """Load a table from output directory."""
    path = OUTPUT_DIR / f"{name}.csv"
    if path.exists():
        return pd.read_csv(path, low_memory=False)
    return pd.DataFrame()


def create_fact_scoring_chances() -> pd.DataFrame:
    """
    Create scoring chances from shot events.
    
    A scoring chance is any shot attempt with danger level assessed.
    """
    print("\nBuilding fact_scoring_chances...")
    
    events = load_table('fact_events')
    event_players = load_table('fact_event_players')
    schedule = load_table('dim_schedule')
    
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
        
        # Danger level assessment
        # Based on event_detail_2 (shot type) and zone
        event_detail_2 = str(shot.get('event_detail_2', '')).lower()
        zone = str(shot.get('event_team_zone', '')).lower()
        
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
    return df


def create_fact_shot_danger() -> pd.DataFrame:
    """
    Create shot danger analysis with xG estimates.
    
    Uses event data to estimate shot quality without XY coordinates.
    """
    print("\nBuilding fact_shot_danger...")
    
    events = load_table('fact_events')
    schedule = load_table('dim_schedule')
    
    if len(events) == 0:
        print("  ERROR: fact_events not found!")
        return pd.DataFrame()
    
    # Filter to shots
    shots = events[events['event_type'].astype(str).str.lower().isin(['shot', 'goal'])]
    
    all_danger = []
    
    for idx, shot in shots.iterrows():
        game_id = shot['game_id']
        
        danger = {
            'shot_danger_key': f"SD_{shot['event_id']}",
            'game_id': game_id,
            'event_index': shot.get('event_id', idx),
        }
        
        # Get season_id
        if len(schedule) > 0:
            game_info = schedule[schedule['game_id'] == game_id]
            if len(game_info) > 0 and 'season_id' in game_info.columns:
                danger['season_id'] = game_info['season_id'].values[0]
        
        # Assess danger zone
        event_detail = str(shot.get('event_detail', '')).lower()
        event_detail_2 = str(shot.get('event_detail_2', '')).lower()
        zone = str(shot.get('event_team_zone', '')).lower()
        
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
        
        # Rush modifier
        rush_mod = 1.15 if 'rush' in event_detail_2 else 1.0
        
        # Rebound modifier
        rebound_mod = 1.25 if 'rebound' in event_detail_2 else 1.0
        
        # Calculate xG
        xg = base_xg * shot_type_mod * rush_mod * rebound_mod
        danger['xg'] = round(min(xg, 0.95), 3)  # Cap at 95%
        
        # Flags
        danger['is_rebound'] = 'rebound' in event_detail_2
        danger['is_rush'] = 'rush' in event_detail_2
        danger['is_one_timer'] = 'one_time' in event_detail_2 or 'onetimer' in event_detail_2
        
        # Placeholder for distance/angle (would need XY data)
        danger['shot_distance'] = None
        danger['shot_angle'] = None
        
        all_danger.append(danger)
    
    df = pd.DataFrame(all_danger)
    print(f"  Created {len(df)} shot danger records")
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
    """
    print("\nBuilding fact_possession_time...")
    
    event_players = load_table('fact_event_players')
    schedule = load_table('dim_schedule')
    
    if len(event_players) == 0:
        print("  ERROR: fact_event_players not found!")
        return pd.DataFrame()
    
    # Group by game and player
    grouped = event_players.groupby(['game_id', 'player_id'])
    
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
        
        # Count possession-related events
        # Zone entries
        entries = group[group['event_type'].astype(str).str.lower().str.contains('zone', na=False)]
        poss['zone_entries'] = len(entries[entries['event_detail'].astype(str).str.lower().str.contains('entry', na=False)])
        poss['zone_exits'] = len(entries[entries['event_detail'].astype(str).str.lower().str.contains('exit', na=False)])
        
        # Offensive zone entries
        ozone = group[group['event_team_zone'].astype(str).str.lower() == 'o']
        poss['ozone_entries'] = len(ozone[ozone['event_detail'].astype(str).str.lower().str.contains('entry', na=False)])
        
        # Defensive zone entries (bad)
        dzone = group[group['event_team_zone'].astype(str).str.lower() == 'd']
        poss['dzone_entries'] = len(dzone[dzone['event_detail'].astype(str).str.lower().str.contains('entry', na=False)])
        
        # Total possession events (passes, shots, carries)
        possession_events = group[
            group['event_type'].astype(str).str.lower().isin(['pass', 'shot', 'possession', 'deke'])
        ]
        poss['possession_events'] = len(possession_events)
        
        # Estimate possession time (very rough: 3 seconds per possession event)
        poss['estimated_possession_seconds'] = poss['possession_events'] * 3
        
        # Venue
        if 'team_venue' in group.columns:
            poss['venue'] = group['team_venue'].mode().iloc[0] if len(group['team_venue'].mode()) > 0 else None
        
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
