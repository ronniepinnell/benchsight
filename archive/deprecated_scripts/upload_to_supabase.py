#!/usr/bin/env python3
"""
BenchSight Supabase Upload - v20.7
Uses config/config_local.ini for credentials

Usage:
    python3 sql/upload_to_supabase.py              # Upload all
    python3 sql/upload_to_supabase.py --dims       # Dims only
    python3 sql/upload_to_supabase.py --facts      # Facts only
    python3 sql/upload_to_supabase.py --table X    # Single table
"""

import os
import sys
import configparser
import pandas as pd
import numpy as np
from pathlib import Path

# Load config from config_local.ini
config = configparser.ConfigParser()
config_path = Path(__file__).parent.parent / 'config' / 'config_local.ini'
config.read(config_path)

SUPABASE_URL = config.get('supabase', 'url')
SUPABASE_KEY = config.get('supabase', 'service_key')

DATA_DIR = Path("data/output")
BATCH_SIZE = int(config.get('loader', 'batch_size', fallback='500'))

print(f"Config loaded from: {config_path}")
print(f"Supabase URL: {SUPABASE_URL}")

# All tables in load order
DIM_TABLES = ['dim_assist_type', 'dim_comparison_type', 'dim_competition_tier', 'dim_composite_rating', 'dim_danger_level', 'dim_danger_zone', 'dim_event_detail', 'dim_event_detail_2', 'dim_event_type', 'dim_game_state', 'dim_giveaway_type', 'dim_league', 'dim_micro_stat', 'dim_net_location', 'dim_pass_outcome', 'dim_pass_type', 'dim_period', 'dim_play_detail', 'dim_play_detail_2', 'dim_player', 'dim_player_role', 'dim_playerurlref', 'dim_position', 'dim_randomnames', 'dim_rating', 'dim_rating_matchup', 'dim_rink_zone', 'dim_save_outcome', 'dim_schedule', 'dim_season', 'dim_shift_duration', 'dim_shift_quality_tier', 'dim_shift_slot', 'dim_shift_start_type', 'dim_shift_stop_type', 'dim_shot_outcome', 'dim_shot_type', 'dim_situation', 'dim_stat', 'dim_stat_category', 'dim_stat_type', 'dim_stoppage_type', 'dim_strength', 'dim_success', 'dim_takeaway_type', 'dim_team', 'dim_terminology_mapping', 'dim_time_bucket', 'dim_turnover_quality', 'dim_turnover_type', 'dim_venue', 'dim_zone', 'dim_zone_entry_type', 'dim_zone_exit_type', 'dim_zone_outcome']

FACT_TABLES = ['fact_breakouts', 'fact_draft', 'fact_event_chains', 'fact_event_players', 'fact_events', 'fact_faceoffs', 'fact_gameroster', 'fact_goalie_game_stats', 'fact_h2h', 'fact_head_to_head', 'fact_high_danger_chances', 'fact_leadership', 'fact_league_leaders_snapshot', 'fact_line_combos', 'fact_matchup_performance', 'fact_matchup_summary', 'fact_penalties', 'fact_period_momentum', 'fact_player_boxscore_all', 'fact_player_career_stats', 'fact_player_event_chains', 'fact_player_game_position', 'fact_player_game_stats', 'fact_player_matchups_xy', 'fact_player_micro_stats', 'fact_player_pair_stats', 'fact_player_period_stats', 'fact_player_position_splits', 'fact_player_puck_proximity', 'fact_player_qoc_summary', 'fact_player_season_stats', 'fact_player_stats_by_competition_tier', 'fact_player_stats_long', 'fact_player_trends', 'fact_player_xy_long', 'fact_player_xy_wide', 'fact_playergames', 'fact_plays', 'fact_possession_time', 'fact_puck_xy_long', 'fact_puck_xy_wide', 'fact_registration', 'fact_rush_events', 'fact_rushes', 'fact_saves', 'fact_scoring_chances', 'fact_scoring_chances_detailed', 'fact_season_summary', 'fact_sequences', 'fact_shift_players', 'fact_shift_quality', 'fact_shift_quality_logical', 'fact_shifts', 'fact_shot_danger', 'fact_shot_event', 'fact_shot_players', 'fact_shot_xy', 'fact_special_teams_summary', 'fact_suspicious_stats', 'fact_team_game_stats', 'fact_team_season_stats', 'fact_team_standings_snapshot', 'fact_team_zone_time', 'fact_tracking', 'fact_turnovers_detailed', 'fact_video', 'fact_wowy', 'fact_zone_entries', 'fact_zone_entry_summary', 'fact_zone_exit_summary', 'fact_zone_exits']

OTHER_TABLES = ['lookup_player_game_rating', 'qa_data_completeness', 'qa_goal_accuracy', 'qa_scorer_comparison', 'qa_suspicious_stats']

def clean_value(val):
    """Clean value for JSON serialization."""
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer, np.int64)):
        return int(val)
    if isinstance(val, (np.floating, np.float64)):
        if np.isnan(val) or np.isinf(val):
            return None
        return float(val)
    if isinstance(val, np.bool_):
        return bool(val)
    return str(val) if val is not None else None

def upload_table(supabase, table_name: str):
    """Upload a single table."""
    csv_path = DATA_DIR / f"{table_name}.csv"
    if not csv_path.exists():
        print(f"  SKIP: {table_name} (no CSV)")
        return 0
    
    df = pd.read_csv(csv_path, low_memory=False)
    if len(df) == 0:
        print(f"  SKIP: {table_name} (empty)")
        return 0
    
    # Clean data
    records = []
    for _, row in df.iterrows():
        record = {col: clean_value(val) for col, val in row.items()}
        records.append(record)
    
    # Upload in batches
    uploaded = 0
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i+BATCH_SIZE]
        try:
            supabase.table(table_name).upsert(batch).execute()
            uploaded += len(batch)
        except Exception as e:
            print(f"  ERROR: {table_name} batch {i}: {e}")
    
    print(f"  ✓ {table_name}: {uploaded} rows")
    return uploaded

def main():
    try:
        from supabase import create_client
    except ImportError:
        print("Install: pip install supabase --break-system-packages")
        sys.exit(1)
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Parse args
    tables_to_upload = []
    if "--dims" in sys.argv:
        tables_to_upload = DIM_TABLES
        print("Uploading DIMENSION tables only")
    elif "--facts" in sys.argv:
        tables_to_upload = FACT_TABLES
        print("Uploading FACT tables only")
    elif "--table" in sys.argv:
        idx = sys.argv.index("--table")
        if idx + 1 < len(sys.argv):
            tables_to_upload = [sys.argv[idx + 1]]
    else:
        tables_to_upload = DIM_TABLES + FACT_TABLES + OTHER_TABLES
    
    print(f"\nUploading {len(tables_to_upload)} tables to Supabase...\n")
    
    total = 0
    for table in tables_to_upload:
        total += upload_table(supabase, table)
    
    print(f"\n✅ Done! Uploaded {total:,} total rows")

if __name__ == "__main__":
    main()
