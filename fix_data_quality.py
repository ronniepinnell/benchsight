#!/usr/bin/env python3
"""
DATA QUALITY FIX - FINAL VERSION
================================
1. Extract game_id from _source_file for all tracking tables
2. Clean metadata columns
3. Dedupe

Run: python fix_data_quality.py
"""

import pandas as pd
from pathlib import Path
import re

CLEAN_DIR = Path("data/clean")
OUTPUT_DIR = Path("data/output")


def extract_game_id(source_file):
    """Extract game_id from '18965_tracking.xlsx' -> '18965'"""
    if pd.isna(source_file):
        return None
    match = re.match(r'^(\d+)', str(source_file))
    return match.group(1) if match else None


def fix_table(table_name, key_cols=None):
    """Fix a single table: extract game_id, remove metadata, dedupe."""
    
    clean_path = CLEAN_DIR / f"{table_name}.csv"
    output_path = OUTPUT_DIR / f"{table_name}.csv"
    
    # Try clean first, fall back to output
    if clean_path.exists():
        df = pd.read_csv(clean_path, dtype=str)
        source = "clean"
    elif output_path.exists():
        df = pd.read_csv(output_path, dtype=str)
        source = "output"
    else:
        print(f"  {table_name}: NOT FOUND")
        return
    
    original_len = len(df)
    
    # Extract game_id from _source_file if needed
    if '_source_file' in df.columns and 'game_id' in df.columns:
        null_before = df['game_id'].isna().sum()
        df['game_id'] = df.apply(
            lambda r: extract_game_id(r.get('_source_file')) if pd.isna(r.get('game_id')) else r['game_id'],
            axis=1
        )
        null_after = df['game_id'].isna().sum()
        fixed = null_before - null_after
    else:
        fixed = 0
    
    # Remove metadata columns (start with _)
    drop_cols = [c for c in df.columns if c.startswith('_')]
    df = df.drop(columns=drop_cols, errors='ignore')
    
    # Dedupe
    df = df.drop_duplicates()
    final_len = len(df)
    dups = original_len - final_len
    
    # Save
    df.to_csv(output_path, index=False)
    
    status = []
    if fixed > 0:
        status.append(f"fixed {fixed} game_ids")
    if dups > 0:
        status.append(f"removed {dups} dups")
    
    status_str = ", ".join(status) if status else "OK"
    print(f"  {table_name}: {final_len} rows ({status_str})")


def create_fact_events():
    """Create fact_events as simplified view (one row per event)."""
    
    # Load events_long
    df = pd.read_csv(OUTPUT_DIR / "fact_events_long.csv", dtype=str)
    
    # Get event-level columns only (no player info)
    event_cols = ['game_id', 'event_index', 'event_type', 'period', 'zone', 'team',
                  'success', 'detail_1', 'detail_2', 'shift_index', 'video_time',
                  'clock_start_seconds', 'clock_end_seconds']
    
    event_cols = [c for c in event_cols if c in df.columns]
    
    events = df[event_cols].drop_duplicates()
    events.to_csv(OUTPUT_DIR / "fact_events.csv", index=False)
    print(f"  fact_events: {len(events)} rows (created from events_long)")


def main():
    print("=" * 60)
    print("DATA QUALITY FIX")
    print("=" * 60)
    
    # Fix tracking tables (from clean/)
    print("\n--- TRACKING TABLES ---")
    fix_table("fact_events_tracking")
    fix_table("fact_events_long")
    fix_table("fact_shifts_tracking")
    fix_table("fact_shift_players_tracking")
    fix_table("fact_event_players_tracking")
    fix_table("fact_linked_events_tracking")
    fix_table("fact_plays_tracking")
    fix_table("fact_sequences_tracking")
    
    # Create fact_events from events_long
    print("\n--- DERIVED TABLES ---")
    create_fact_events()
    
    # Fix other fact tables
    print("\n--- OTHER FACT TABLES ---")
    for csv in sorted(OUTPUT_DIR.glob("fact_*.csv")):
        if csv.stem not in ['fact_events_tracking', 'fact_events_long', 'fact_events',
                            'fact_shifts_tracking', 'fact_shift_players_tracking',
                            'fact_event_players_tracking', 'fact_linked_events_tracking',
                            'fact_plays_tracking', 'fact_sequences_tracking']:
            fix_table(csv.stem)
    
    # Dedupe dimension tables
    print("\n--- DIMENSION TABLES ---")
    for csv in sorted(OUTPUT_DIR.glob("dim_*.csv")):
        fix_table(csv.stem)
    
    # Verify
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    for name in ['fact_events', 'fact_events_long', 'fact_events_tracking']:
        df = pd.read_csv(OUTPUT_DIR / f"{name}.csv", dtype=str)
        null_game = df['game_id'].isna().sum() if 'game_id' in df.columns else -1
        games = df['game_id'].nunique() if 'game_id' in df.columns else 0
        print(f"  {name}: {len(df)} rows, {games} games, {null_game} NULL")
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
