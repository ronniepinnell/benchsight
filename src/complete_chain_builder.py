#!/usr/bin/env python3
"""
Complete chain builder - adds play_chain, video times, and all missing FKs
to sequences, plays, linked_events tables.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path('data/output')


def build_event_lookups():
    """Build lookup dicts from events table."""
    logger.info("Building event lookups...")
    events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
    
    # Normalize types
    events['game_id'] = pd.to_numeric(events['game_id'], errors='coerce').astype('Int64')
    events['event_index'] = pd.to_numeric(events['event_index'], errors='coerce').astype('Int64')
    
    # Get unique events (first row per event_index)
    unique_events = events.drop_duplicates(['game_id', 'event_index']).copy()
    
    # Build lookups
    lookups = {}
    
    # Key lookup
    lookups['event_key'] = unique_events.set_index(
        [unique_events['game_id'], unique_events['event_index']]
    )['event_key'].to_dict()
    
    # Event type lookup
    lookups['event_type'] = unique_events.set_index(
        [unique_events['game_id'], unique_events['event_index']]
    )['event_type'].to_dict()
    
    # Video time lookup
    lookups['video_time'] = unique_events.set_index(
        [unique_events['game_id'], unique_events['event_index']]
    )['running_video_time'].to_dict()
    
    # Team venue lookup
    lookups['team_venue'] = unique_events.set_index(
        [unique_events['game_id'], unique_events['event_index']]
    )['team_venue'].to_dict()
    
    # Team ID lookup
    lookups['team_id'] = unique_events.set_index(
        [unique_events['game_id'], unique_events['event_index']]
    )['team_id'].to_dict()
    
    logger.info(f"  Built lookups for {len(unique_events)} unique events")
    return lookups, events


def build_play_chain(events_df, game_id, start_idx, end_idx):
    """Build play chain string for event range."""
    if pd.isna(start_idx) or pd.isna(end_idx):
        return None, None
    
    start_idx = int(start_idx)
    end_idx = int(end_idx)
    game_id = int(game_id)
    
    game_events = events_df[events_df['game_id'] == game_id]
    range_events = game_events[
        (game_events['event_index'] >= start_idx) & 
        (game_events['event_index'] <= end_idx)
    ].drop_duplicates('event_index').sort_values('event_index')
    
    if range_events.empty:
        return None, None
    
    # Build chain
    event_types = range_events['event_type'].tolist()
    event_indices = range_events['event_index'].astype(int).tolist()
    
    play_chain = ' > '.join([str(et) for et in event_types if pd.notna(et)])
    event_chain_indices = ','.join([str(idx) for idx in event_indices])
    
    return play_chain, event_chain_indices


def safe_lookup(lookups, key, game_id, event_idx):
    """Safely lookup a value."""
    if pd.isna(game_id) or pd.isna(event_idx):
        return None
    try:
        return lookups[key].get((int(game_id), int(event_idx)))
    except:
        return None


def process_sequences(lookups, events_df):
    """Add all missing data to sequences."""
    logger.info("Processing fact_sequences...")
    
    seq = pd.read_csv(OUTPUT_DIR / 'fact_sequences.csv')
    seq['game_id'] = pd.to_numeric(seq['game_id'], errors='coerce').astype('Int64')
    
    # Determine column names
    start_col = 'first_event' if 'first_event' in seq.columns else 'start_event_index'
    end_col = 'last_event' if 'last_event' in seq.columns else 'end_event_index'
    
    # Build chains and add data
    chains = []
    indices = []
    video_starts = []
    video_ends = []
    
    for _, row in seq.iterrows():
        game_id = row['game_id']
        start_idx = row[start_col]
        end_idx = row[end_col]
        
        chain, idx_str = build_play_chain(events_df, game_id, start_idx, end_idx)
        chains.append(chain)
        indices.append(idx_str)
        
        video_starts.append(safe_lookup(lookups, 'video_time', game_id, start_idx))
        video_ends.append(safe_lookup(lookups, 'video_time', game_id, end_idx))
    
    seq['play_chain'] = chains
    seq['event_chain_indices'] = indices
    seq['video_time_start'] = video_starts
    seq['video_time_end'] = video_ends
    
    # Ensure first/last event keys
    seq['first_event_key'] = seq.apply(
        lambda r: safe_lookup(lookups, 'event_key', r['game_id'], r[start_col]), axis=1
    )
    seq['last_event_key'] = seq.apply(
        lambda r: safe_lookup(lookups, 'event_key', r['game_id'], r[end_col]), axis=1
    )
    
    seq.to_csv(OUTPUT_DIR / 'fact_sequences.csv', index=False)
    logger.info(f"  ✓ Sequences: {seq['play_chain'].notna().sum()}/{len(seq)} chains filled")


def process_plays(lookups, events_df):
    """Add all missing data to plays."""
    logger.info("Processing fact_plays...")
    
    plays = pd.read_csv(OUTPUT_DIR / 'fact_plays.csv')
    plays['game_id'] = pd.to_numeric(plays['game_id'], errors='coerce').astype('Int64')
    
    start_col = 'first_event' if 'first_event' in plays.columns else 'start_event_index'
    end_col = 'last_event' if 'last_event' in plays.columns else 'end_event_index'
    
    chains = []
    indices = []
    video_starts = []
    video_ends = []
    
    for _, row in plays.iterrows():
        game_id = row['game_id']
        start_idx = row[start_col]
        end_idx = row[end_col]
        
        chain, idx_str = build_play_chain(events_df, game_id, start_idx, end_idx)
        chains.append(chain)
        indices.append(idx_str)
        
        video_starts.append(safe_lookup(lookups, 'video_time', game_id, start_idx))
        video_ends.append(safe_lookup(lookups, 'video_time', game_id, end_idx))
    
    plays['play_chain'] = chains
    plays['event_chain_indices'] = indices
    plays['video_time_start'] = video_starts
    plays['video_time_end'] = video_ends
    
    plays['first_event_key'] = plays.apply(
        lambda r: safe_lookup(lookups, 'event_key', r['game_id'], r[start_col]), axis=1
    )
    plays['last_event_key'] = plays.apply(
        lambda r: safe_lookup(lookups, 'event_key', r['game_id'], r[end_col]), axis=1
    )
    
    plays.to_csv(OUTPUT_DIR / 'fact_plays.csv', index=False)
    logger.info(f"  ✓ Plays: {plays['play_chain'].notna().sum()}/{len(plays)} chains filled")


def process_linked_events(lookups, events_df):
    """Add all missing data to linked_events."""
    logger.info("Processing fact_linked_events...")
    
    linked = pd.read_csv(OUTPUT_DIR / 'fact_linked_events.csv')
    linked['game_id'] = pd.to_numeric(linked['game_id'], errors='coerce').astype('Int64')
    
    # Build play chain from event columns
    chains = []
    indices = []
    
    for _, row in linked.iterrows():
        types = []
        idxs = []
        for i in range(1, 10):
            type_col = f'event_{i}_type'
            idx_col = f'event_{i}_index'
            if type_col in row and pd.notna(row.get(type_col)):
                types.append(str(row[type_col]))
            if idx_col in row and pd.notna(row.get(idx_col)):
                idxs.append(str(int(row[idx_col])))
        
        chains.append(' > '.join(types) if types else None)
        indices.append(','.join(idxs) if idxs else None)
    
    linked['play_chain'] = chains
    linked['event_chain_indices'] = indices
    
    # Add venue_id - lookup from first event
    venue_map = {'home': 'VN0001', 'away': 'VN0002', 'Home': 'VN0001', 'Away': 'VN0002'}
    
    def get_venue_id(row):
        # Try team_venue first
        if 'team_venue' in row and pd.notna(row.get('team_venue')) and str(row['team_venue']).strip():
            return venue_map.get(str(row['team_venue']).lower())
        # Fall back to event lookup
        venue = safe_lookup(lookups, 'team_venue', row['game_id'], row.get('event_1_index'))
        if venue:
            return venue_map.get(str(venue).lower())
        return None
    
    linked['venue_id'] = linked.apply(get_venue_id, axis=1)
    
    # Add video times
    linked['video_time_start'] = linked.apply(
        lambda r: safe_lookup(lookups, 'video_time', r['game_id'], r.get('event_1_index')), axis=1
    )
    
    # Find last event index
    def get_last_event_idx(row):
        for i in range(9, 0, -1):
            idx_col = f'event_{i}_index'
            if idx_col in row and pd.notna(row.get(idx_col)):
                return row[idx_col]
        return None
    
    linked['video_time_end'] = linked.apply(
        lambda r: safe_lookup(lookups, 'video_time', r['game_id'], get_last_event_idx(r)), axis=1
    )
    
    linked.to_csv(OUTPUT_DIR / 'fact_linked_events.csv', index=False)
    logger.info(f"  ✓ Linked events: {linked['play_chain'].notna().sum()}/{len(linked)} chains, {linked['venue_id'].notna().sum()}/{len(linked)} venue_id")


def process_cycles(lookups, events_df):
    """Add all missing data to cycles."""
    logger.info("Processing fact_cycle_events...")
    
    cycles = pd.read_csv(OUTPUT_DIR / 'fact_cycle_events.csv')
    cycles['game_id'] = pd.to_numeric(cycles['game_id'], errors='coerce').astype('Int64')
    
    start_col = 'cycle_start_event_index'
    end_col = 'cycle_end_event_index'
    
    chains = []
    indices = []
    video_starts = []
    video_ends = []
    
    for _, row in cycles.iterrows():
        game_id = row['game_id']
        start_idx = row.get(start_col)
        end_idx = row.get(end_col)
        
        chain, idx_str = build_play_chain(events_df, game_id, start_idx, end_idx)
        chains.append(chain)
        indices.append(idx_str)
        
        video_starts.append(safe_lookup(lookups, 'video_time', game_id, start_idx))
        video_ends.append(safe_lookup(lookups, 'video_time', game_id, end_idx))
    
    cycles['play_chain'] = chains
    cycles['event_chain_indices'] = indices
    cycles['video_time_start'] = video_starts
    cycles['video_time_end'] = video_ends
    
    cycles['first_event_key'] = cycles.apply(
        lambda r: safe_lookup(lookups, 'event_key', r['game_id'], r.get(start_col)), axis=1
    )
    cycles['last_event_key'] = cycles.apply(
        lambda r: safe_lookup(lookups, 'event_key', r['game_id'], r.get(end_col)), axis=1
    )
    
    # Add team_id
    cycles['team_id'] = cycles.apply(
        lambda r: safe_lookup(lookups, 'team_id', r['game_id'], r.get(start_col)), axis=1
    )
    
    # Add venue_id
    venue_map = {'home': 'VN0001', 'away': 'VN0002', 'Home': 'VN0001', 'Away': 'VN0002'}
    cycles['venue_id'] = cycles.apply(
        lambda r: venue_map.get(str(safe_lookup(lookups, 'team_venue', r['game_id'], r.get(start_col))).lower())
        if pd.notna(r.get(start_col)) else None, axis=1
    )
    
    cycles.to_csv(OUTPUT_DIR / 'fact_cycle_events.csv', index=False)
    logger.info(f"  ✓ Cycles: {cycles['play_chain'].notna().sum()}/{len(cycles)} chains")


def process_rushes(lookups, events_df):
    """Add all missing data to rushes."""
    logger.info("Processing fact_rush_events...")
    
    rushes = pd.read_csv(OUTPUT_DIR / 'fact_rush_events.csv')
    rushes['game_id'] = pd.to_numeric(rushes['game_id'], errors='coerce').astype('Int64')
    
    start_col = 'entry_event_index'
    end_col = 'shot_event_index'
    
    chains = []
    indices = []
    
    for _, row in rushes.iterrows():
        game_id = row['game_id']
        start_idx = row.get(start_col)
        end_idx = row.get(end_col)
        
        chain, idx_str = build_play_chain(events_df, game_id, start_idx, end_idx)
        chains.append(chain)
        indices.append(idx_str)
    
    rushes['play_chain'] = chains
    rushes['event_chain_indices'] = indices
    
    # Add venue_id
    venue_map = {'home': 'VN0001', 'away': 'VN0002', 'Home': 'VN0001', 'Away': 'VN0002'}
    rushes['venue_id'] = rushes.apply(
        lambda r: venue_map.get(str(safe_lookup(lookups, 'team_venue', r['game_id'], r.get(start_col))).lower())
        if pd.notna(r.get(start_col)) else None, axis=1
    )
    
    rushes.to_csv(OUTPUT_DIR / 'fact_rush_events.csv', index=False)
    logger.info(f"  ✓ Rushes: {rushes['play_chain'].notna().sum()}/{len(rushes)} chains")


def main():
    print("=" * 70)
    print("COMPLETE CHAIN BUILDER")
    print("=" * 70)
    
    lookups, events_df = build_event_lookups()
    
    process_sequences(lookups, events_df)
    process_plays(lookups, events_df)
    process_linked_events(lookups, events_df)
    process_cycles(lookups, events_df)
    process_rushes(lookups, events_df)
    
    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
