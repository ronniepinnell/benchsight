"""
Sequence and Play Index Auto-Generator for BenchSight

SEQUENCE: Complete possession chain, multi-zone, multi-team
- New sequence starts on: Faceoff, Goal, Period change, Stoppage, GameStart
- Purpose: Track possession chains (e.g., how often does turnover lead to opponent goal?)

PLAY: Single-zone, single-team possession segment  
- New play starts on: Zone change, Possession change (takeaway/giveaway)
- Purpose: Analyze within-zone play patterns

Author: Claude
Date: 2024-12-28
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional


# =============================================================================
# TRIGGER DEFINITIONS
# =============================================================================

# SEQUENCE = From one possession change to the next
# A sequence tracks what happens after a turnover until the next turnover
# Use case: "How often does player X turn it over and opponent scores?"
#
# SEQUENCE starts on:
# - Turnover (giveaway/takeaway) - NEW sequence for recovering team
# - Faceoff - winner gets new sequence
# - Period change
# - Stoppage (resets play)

SEQUENCE_START_EVENTS = {
    'Faceoff',      # Faceoff = new sequence
    'Turnover',     # Turnover = new sequence for recovering team
    'GameStart',    # Game start
    'Stoppage',     # Whistle = sequence break
    'Intermission', # Period break
}

SEQUENCE_START_DETAILS = {
    'Faceoff_GameStart',
    'Faceoff_PeriodStart', 
    'Faceoff_AfterGoal',
    'Faceoff_AfterStoppage',
    'Faceoff_AfterPenalty',
    'Turnover_Giveaway',
    'Turnover_Takeaway',
    'Stoppage_Play',
}

# Goal ENDS sequence (goal is last event of that sequence)
SEQUENCE_END_EVENTS = {
    'Goal',
}

SEQUENCE_END_DETAILS = {
    'Goal_Scored',
    'Shot_Goal',
}

# Events that indicate POSSESSION CHANGE (for play boundaries)
POSSESSION_CHANGE_EVENTS = {
    'Turnover',     # Any turnover
}

POSSESSION_CHANGE_DETAILS = {
    'Turnover_Giveaway',
    'Turnover_Takeaway', 
    'Pass_Intercepted',
}


def generate_sequence_play_indexes(events_df: pd.DataFrame, game_id: int = None) -> pd.DataFrame:
    """
    Auto-generate sequence_index and play_index for events.
    
    Args:
        events_df: DataFrame with events (one row per player per event OR one row per event)
        game_id: Optional game_id for logging
        
    Returns:
        DataFrame with generated sequence_index_auto and play_index_auto columns
    """
    
    df = events_df.copy()
    
    # Get unique events (header level - one row per event_index)
    event_cols = ['event_index', 'period', 'Type', 'event_detail', 'event_team_zone', 
                  'team_venue', 'zone_change_index']
    available_cols = [c for c in event_cols if c in df.columns]
    
    # Handle case where data is long format (multiple rows per event)
    if 'player_role' in df.columns:
        # Long format - dedupe to get header
        header = df.drop_duplicates('event_index')[available_cols].copy()
    else:
        header = df[available_cols].copy()
    
    header = header.sort_values('event_index').reset_index(drop=True)
    
    # Initialize indexes
    header['sequence_index_auto'] = 0
    header['play_index_auto'] = 0
    
    current_sequence = 1
    current_play = 1
    prev_zone = None
    prev_team = None
    prev_period = None
    
    for idx, row in header.iterrows():
        event_type = row.get('Type', '')
        event_detail = row.get('event_detail', '')
        zone = row.get('event_team_zone', '')
        team = row.get('team_venue', '')
        period = row.get('period', 1)
        
        # =================================================================
        # SEQUENCE LOGIC: New sequence on major game events
        # Goal ENDS a sequence (assigned to current), next event starts new
        # =================================================================
        new_sequence = False
        end_sequence = False
        
        # Period change = new sequence
        if prev_period is not None and period != prev_period:
            new_sequence = True
            
        # Sequence start events (Faceoff, Stoppage, GameStart)
        if event_type in SEQUENCE_START_EVENTS:
            new_sequence = True
            
        # Sequence start details
        if event_detail in SEQUENCE_START_DETAILS:
            new_sequence = True
        
        # Goal ENDS sequence (this event is last of current sequence)
        if event_type in SEQUENCE_END_EVENTS or event_detail in SEQUENCE_END_DETAILS:
            end_sequence = True
            
        if new_sequence:
            current_sequence += 1
            current_play += 1  # New sequence = new play too
            
        # =================================================================
        # PLAY LOGIC: New play on zone change or possession change
        # Turnover = new play only (not new sequence)
        # =================================================================
        new_play = False
        
        if not new_sequence:  # Don't double-increment
            # Zone change = new play
            if prev_zone is not None and zone != prev_zone and pd.notna(zone):
                new_play = True
                
            # Possession change = new play (Turnover only breaks plays, not sequences)
            if event_type in POSSESSION_CHANGE_EVENTS:
                new_play = True
            if event_detail in POSSESSION_CHANGE_DETAILS:
                new_play = True
                
            # Team change (if tracking) = new play
            if prev_team is not None and team != prev_team and pd.notna(team):
                new_play = True
                
            if new_play:
                current_play += 1
        
        # Assign indexes
        header.loc[idx, 'sequence_index_auto'] = current_sequence
        header.loc[idx, 'play_index_auto'] = current_play
        
        # If this event ends a sequence, next non-faceoff event would be anomaly
        # but faceoff will handle it
        if end_sequence:
            # Mark that sequence should end after this event
            # Next event will get same sequence unless it's a sequence start
            pass
        
        # Update previous values
        prev_zone = zone if pd.notna(zone) else prev_zone
        prev_team = team if pd.notna(team) else prev_team
        prev_period = period
    
    # Merge back to original dataframe
    merge_cols = ['event_index', 'sequence_index_auto', 'play_index_auto']
    result = df.merge(header[merge_cols], on='event_index', how='left')
    
    return result


def analyze_sequences(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build fact_sequences summary table from auto-generated sequence indexes.
    
    Returns DataFrame with one row per sequence containing:
    - sequence_id
    - game_id  
    - first_event_index, last_event_index
    - event_count
    - start_team, end_team
    - start_zone, end_zone
    - has_goal (bool)
    - duration_seconds
    """
    
    df = events_df.copy()
    
    if 'sequence_index_auto' not in df.columns:
        df = generate_sequence_play_indexes(df)
    
    # Get header-level events
    if 'player_role' in df.columns:
        header = df.drop_duplicates('event_index').copy()
    else:
        header = df.copy()
    
    # Group by sequence
    sequences = header.groupby('sequence_index_auto').agg({
        'event_index': ['min', 'max', 'count'],
        'game_id': 'first',
        'team_venue': ['first', 'last'],
        'event_team_zone': ['first', 'last'],
        'Type': lambda x: 'Goal' in x.values,
        'time_start_total_seconds': 'min',
        'time_end_total_seconds': 'max',
    }).reset_index()
    
    # Flatten column names
    sequences.columns = [
        'sequence_index', 'first_event', 'last_event', 'event_count',
        'game_id', 'start_team', 'end_team', 'start_zone', 'end_zone',
        'has_goal', 'start_seconds', 'end_seconds'
    ]
    
    # Calculate duration
    sequences['duration_seconds'] = sequences['end_seconds'] - sequences['start_seconds']
    
    # Create sequence_id
    if 'game_id' in sequences.columns:
        sequences['sequence_id'] = sequences.apply(
            lambda r: f"SQ{int(r['game_id']):05d}{int(r['sequence_index']):05d}" 
            if pd.notna(r['game_id']) else None, axis=1
        )
    
    return sequences


def analyze_plays(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build fact_plays summary table from auto-generated play indexes.
    
    Returns DataFrame with one row per play containing:
    - play_id
    - game_id
    - sequence_id (parent sequence)
    - first_event_index, last_event_index
    - event_count
    - team
    - zone
    - has_shot (bool)
    - duration_seconds
    """
    
    df = events_df.copy()
    
    if 'play_index_auto' not in df.columns:
        df = generate_sequence_play_indexes(df)
    
    # Get header-level events
    if 'player_role' in df.columns:
        header = df.drop_duplicates('event_index').copy()
    else:
        header = df.copy()
    
    # Group by play
    plays = header.groupby('play_index_auto').agg({
        'event_index': ['min', 'max', 'count'],
        'game_id': 'first',
        'sequence_index_auto': 'first',
        'team_venue': 'first',
        'event_team_zone': 'first',
        'Type': lambda x: 'Shot' in x.values or 'Goal' in x.values,
        'time_start_total_seconds': 'min',
        'time_end_total_seconds': 'max',
    }).reset_index()
    
    # Flatten column names
    plays.columns = [
        'play_index', 'first_event', 'last_event', 'event_count',
        'game_id', 'sequence_index', 'team', 'zone',
        'has_shot', 'start_seconds', 'end_seconds'
    ]
    
    # Calculate duration
    plays['duration_seconds'] = plays['end_seconds'] - plays['start_seconds']
    
    # Create play_id
    if 'game_id' in plays.columns:
        plays['play_id'] = plays.apply(
            lambda r: f"PL{int(r['game_id']):05d}{int(r['play_index']):05d}"
            if pd.notna(r['game_id']) else None, axis=1
        )
        plays['sequence_id'] = plays.apply(
            lambda r: f"SQ{int(r['game_id']):05d}{int(r['sequence_index']):05d}"
            if pd.notna(r['game_id']) and pd.notna(r['sequence_index']) else None, axis=1
        )
    
    return plays


def compare_with_manual(events_df: pd.DataFrame) -> dict:
    """
    Compare auto-generated indexes with manual indexes (if present).
    
    Returns comparison stats.
    """
    
    df = events_df.copy()
    
    if 'sequence_index_auto' not in df.columns:
        df = generate_sequence_play_indexes(df)
    
    results = {
        'auto_sequence_count': df['sequence_index_auto'].max(),
        'auto_play_count': df['play_index_auto'].max(),
    }
    
    if 'sequence_index' in df.columns:
        manual_seq = df['sequence_index'].dropna()
        results['manual_sequence_count'] = len(manual_seq.unique()) if len(manual_seq) > 0 else 0
        
    if 'play_index' in df.columns:
        manual_play = df['play_index'].dropna()
        results['manual_play_count'] = len(manual_play.unique()) if len(manual_play) > 0 else 0
    
    return results


# =============================================================================
# MAIN - Test with sample game
# =============================================================================

if __name__ == "__main__":
    import sys
    
    # Find project root
    project_root = Path(__file__).parent.parent
    
    # Test with game 18969
    tracking_file = project_root / "data/raw/games/18969/18969_tracking.xlsx"
    
    if not tracking_file.exists():
        print(f"Tracking file not found: {tracking_file}")
        sys.exit(1)
    
    print("=" * 70)
    print("SEQUENCE/PLAY AUTO-GENERATOR TEST")
    print("=" * 70)
    
    # Load events
    events = pd.read_excel(tracking_file, 'events')
    print(f"\nLoaded {len(events)} event rows from game 18969")
    
    # Generate indexes
    events_with_indexes = generate_sequence_play_indexes(events, game_id=18969)
    
    # Compare with manual
    comparison = compare_with_manual(events_with_indexes)
    print(f"\n=== COMPARISON ===")
    for k, v in comparison.items():
        print(f"  {k}: {v}")
    
    # Build summary tables
    sequences = analyze_sequences(events_with_indexes)
    plays = analyze_plays(events_with_indexes)
    
    print(f"\n=== GENERATED TABLES ===")
    print(f"  fact_sequences: {len(sequences)} rows")
    print(f"  fact_plays: {len(plays)} rows")
    
    # Show sample sequences
    print(f"\n=== SAMPLE SEQUENCES (first 10) ===")
    display_cols = ['sequence_id', 'event_count', 'start_team', 'end_team', 
                    'start_zone', 'end_zone', 'has_goal', 'duration_seconds']
    available = [c for c in display_cols if c in sequences.columns]
    print(sequences[available].head(10).to_string())
    
    # Show sample plays
    print(f"\n=== SAMPLE PLAYS (first 15) ===")
    display_cols = ['play_id', 'sequence_id', 'event_count', 'team', 'zone', 
                    'has_shot', 'duration_seconds']
    available = [c for c in display_cols if c in plays.columns]
    print(plays[available].head(15).to_string())
    
    # Show sequences with goals
    print(f"\n=== SEQUENCES WITH GOALS ===")
    goal_seqs = sequences[sequences['has_goal'] == True]
    print(f"  {len(goal_seqs)} sequences resulted in goals")
    if len(goal_seqs) > 0:
        seq_cols = ['sequence_id', 'event_count', 'start_team', 'end_team', 
                    'start_zone', 'end_zone', 'has_goal', 'duration_seconds']
        avail_seq = [c for c in seq_cols if c in goal_seqs.columns]
        print(goal_seqs[avail_seq].to_string())
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
