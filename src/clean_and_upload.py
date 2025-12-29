#!/usr/bin/env python3
"""
BenchSight Data Cleaner & Supabase Uploader v4
Comprehensive solution for NaN handling, type conversion, and schema alignment
"""

import os
import sys
import json
import math
import pandas as pd
import numpy as np
from datetime import datetime

# Supabase config
SUPABASE_URL = "https://uuaowslhpgyiudmbvqze.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1YW93c2xocGd5aXVkbWJ2cXplIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQ5OTMxNTIsImV4cCI6MjA1MDU2OTE1Mn0.BOMaWU_UUBCQJT7lp5dL1p_oo6rCLvqIJXTfUCLCpac"

DATA_DIR = "data/output"
CLEAN_DIR = "data/clean"

# TABLE DEFINITIONS
TABLES = {
    'dim_league': {'file': 'dim_league.csv', 'pk': 'league_id', 'order': 1},
    'dim_season': {'file': 'dim_season.csv', 'pk': 'season_id', 'order': 2},
    'dim_team': {'file': 'dim_team.csv', 'pk': 'team_id', 'order': 3},
    'dim_venue': {'file': 'dim_venue.csv', 'pk': 'venue_id', 'order': 4},
    'dim_player': {'file': 'dim_player.csv', 'pk': 'player_id', 'order': 5},
    'dim_schedule': {'file': 'dim_schedule.csv', 'pk': 'game_id', 'order': 6},
    'dim_video': {'file': 'dim_video.csv', 'pk': 'video_id', 'order': 7},
    'dim_event_type': {'file': 'dim_event_type.csv', 'pk': 'event_type_id', 'order': 10},
    'dim_event_detail': {'file': 'dim_event_detail.csv', 'pk': 'event_detail_id', 'order': 11},
    'dim_event_detail_2': {'file': 'dim_event_detail_2.csv', 'pk': 'event_detail_2_id', 'order': 12},
    'dim_play_detail': {'file': 'dim_play_detail.csv', 'pk': 'play_detail_id', 'order': 13},
    'dim_turnover_type': {'file': 'dim_turnover_type.csv', 'pk': 'turnover_type_id', 'order': 14},
    'dim_shot_type': {'file': 'dim_shot_type.csv', 'pk': 'shot_type_id', 'order': 15},
    'dim_pass_type': {'file': 'dim_pass_type.csv', 'pk': 'pass_type_id', 'order': 16},
    'dim_net_location': {'file': 'dim_net_location.csv', 'pk': 'net_location_id', 'order': 17},
    'dim_stat': {'file': 'dim_stat.csv', 'pk': 'stat_id', 'order': 18},
    'dim_strength': {'file': 'dim_strength.csv', 'pk': 'strength_id', 'order': 20},
    'dim_situation': {'file': 'dim_situation.csv', 'pk': 'situation_id', 'order': 21},
    'dim_position': {'file': 'dim_position.csv', 'pk': 'position_id', 'order': 22},
    'dim_zone': {'file': 'dim_zone.csv', 'pk': 'zone_id', 'order': 23},
    'dim_period': {'file': 'dim_period.csv', 'pk': 'period_id', 'order': 24},
    'dim_shift_type': {'file': 'dim_shift_type.csv', 'pk': 'shift_type_id', 'order': 25},
    'dim_skill_tier': {'file': 'dim_skill_tier.csv', 'pk': 'skill_tier_id', 'order': 26},
    'dim_player_role': {'file': 'dim_player_role.csv', 'pk': 'role_id', 'order': 27},
    'dim_danger_zone': {'file': 'dim_danger_zone.csv', 'pk': 'danger_zone_id', 'order': 28},
    'dim_time_bucket': {'file': 'dim_time_bucket.csv', 'pk': 'time_bucket_id', 'order': 29},
    'dim_rinkboxcoord': {'file': 'dim_rinkboxcoord.csv', 'pk': 'box_id', 'order': 30},
    'dim_rinkcoordzones': {'file': 'dim_rinkcoordzones.csv', 'pk': 'coord_zone_id', 'order': 31},
    'fact_gameroster': {'file': 'fact_gameroster.csv', 'pk': 'roster_key', 'order': 50},
    'fact_events_tracking': {'file': 'fact_events_tracking.csv', 'pk': 'event_key', 'order': 51},
    'fact_events_long': {'file': 'fact_events_long.csv', 'pk': 'event_key', 'order': 52},
    'fact_shifts_tracking': {'file': 'fact_shifts_tracking.csv', 'pk': 'shift_key', 'order': 53},
    'fact_shift_players_tracking': {'file': 'fact_shift_players_tracking.csv', 'pk': 'shift_player_key', 'order': 54},
    'fact_linked_events_tracking': {'file': 'fact_linked_events_tracking.csv', 'pk': 'linked_event_key', 'order': 55},
    'fact_sequences_tracking': {'file': 'fact_sequences_tracking.csv', 'pk': 'sequence_key', 'order': 56},
    'fact_plays_tracking': {'file': 'fact_plays_tracking.csv', 'pk': 'play_key', 'order': 57},
    'fact_event_coordinates': {'file': 'fact_event_coordinates.csv', 'pk': 'coord_key', 'order': 58},
    'fact_event_players_tracking': {'file': 'fact_event_players_tracking.csv', 'pk': 'event_player_key', 'order': 59},
    'fact_player_game_stats': {'file': 'fact_player_game_stats.csv', 'pk': 'player_game_key', 'order': 60},
    'fact_goalie_game_stats': {'file': 'fact_goalie_game_stats.csv', 'pk': 'goalie_game_key', 'order': 61},
}

# Columns that MUST be integers
INTEGER_COLUMNS = {
    'player_id', 'game_id', 'team_id', 'season_id', 'league_id', 'venue_id', 'video_id',
    'event_id', 'shift_id', 'sequence_id', 'play_id', 'period', 'jersey_number',
    'event_type_id', 'event_detail_id', 'event_detail_2_id', 'play_detail_id',
    'turnover_type_id', 'shot_type_id', 'pass_type_id', 'net_location_id',
    'strength_id', 'situation_id', 'position_id', 'zone_id', 'period_id',
    'shift_type_id', 'skill_tier_id', 'role_id', 'danger_zone_id', 'time_bucket_id',
    'coord_zone_id', 'sort_order', 'display_order', 'difficulty_rating', 'difficulty_score',
    'home_team_id', 'away_team_id', 'home_score', 'away_score',
    'event_player_1_id', 'event_player_2_id', 'event_player_3_id',
    'event_player_4_id', 'event_player_5_id', 'event_player_6_id',
    'opp_player_1_id', 'opp_player_2_id', 'opp_player_3_id',
    'opp_player_4_id', 'opp_player_5_id', 'opp_player_6_id',
    'goalie_id', 'penalty_minutes', 'primary_event_id', 'secondary_event_id',
    'time_between_events', 'event_count', 'shot_count', 'goal_count', 'player_count',
    'linked_event_id', 'skill_rating', 'current_skill_rating',
    'g', 'a', 'a1', 'a2', 'pts', 'sog', 'plus_minus', 'pim', 'hits', 'blk',
    'toi', 'toi_ev', 'toi_pp', 'toi_pk', 'shifts', 'cf', 'ca', 'ff', 'fa',
    'fow', 'fol', 'pen_taken', 'pen_drawn', 'sa', 'ga', 'saves',
    'event_index', 'shift_index', 'linked_event_index', 'sequence_index', 'play_index',
    'points_value', 'goals', 'assist', 'goals_against', 'shutouts', 'games_played',
}

# Columns that should remain floats
FLOAT_COLUMNS = {
    'x_coord', 'y_coord', 'x_min', 'x_max', 'y_min', 'y_max', 'center_x', 'center_y',
    'x_normalized', 'y_normalized', 'distance_to_net', 'angle_to_net',
    'xg_multiplier', 'penalty_weight', 'avg_sh_pct',
    'period_time_seconds', 'game_time_seconds', 'video_timestamp_start', 'video_timestamp_end',
    'shift_start_seconds', 'shift_end_seconds', 'shift_duration_seconds',
    'sequence_duration', 'play_duration', 'start_time', 'end_time',
    'sh_pct', 'cf_pct', 'ff_pct', 'fo_pct', 'toi_min', 'avg_shift',
    'benchmark_poor', 'benchmark_avg', 'benchmark_good', 'benchmark_elite',
}

# Columns that should be boolean
BOOLEAN_COLUMNS = {
    'is_shot', 'is_pass', 'is_possession', 'is_turnover', 'is_penalty', 'is_faceoff',
    'is_zone_play', 'is_stoppage', 'is_save', 'is_hit', 'is_rebound',
    'credits_event_player_1', 'credits_opp_player_1', 'affects_toi_playing',
    'is_shot_on_goal', 'is_goal', 'is_miss', 'is_block', 'is_giveaway', 'is_takeaway',
    'is_controlled', 'is_success', 'is_offensive', 'is_defensive', 'is_transition',
    'is_recovery', 'credits_player', 'is_bad_turnover', 'is_neutral_turnover',
    'is_one_timer', 'is_slot_pass', 'is_cross_ice', 'goalie_weakness_common',
    'requires_xy', 'higher_is_better', 'is_power_play', 'is_penalty_kill', 'is_even_strength',
    'event_successful', 'is_penalty_shot', 'is_empty_net', 'is_tracked',
}

# Columns to drop
DROP_COLUMNS = {'index', 'Unnamed: 0', 'level_0'}


def is_nan(val):
    """Check if value is NaN/None/empty."""
    if val is None:
        return True
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return True
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ('nan', 'none', '', 'null', 'na', 'n/a', '#n/a', 'nat'):
            return True
    try:
        if pd.isna(val):
            return True
    except:
        pass
    return False


def to_int_safe(val):
    """Convert to int safely."""
    if is_nan(val):
        return None
    try:
        if isinstance(val, str):
            val = val.strip()
            if '.' in val:
                return int(float(val))
            return int(val)
        return int(float(val))
    except:
        return None


def to_float_safe(val):
    """Convert to float safely."""
    if is_nan(val):
        return None
    try:
        if isinstance(val, str):
            val = val.strip()
            if val.lower() in ('high', 'medium', 'low', 'true', 'false'):
                return None
        return float(val)
    except:
        return None


def to_bool_safe(val):
    """Convert to bool safely."""
    if is_nan(val):
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ('true', 'yes', '1', 't', 'y'):
            return True
        if v in ('false', 'no', '0', 'f', 'n'):
            return False
    return None


def clean_dataframe(df, table_name):
    """Clean dataframe with proper type conversions."""
    # Clean column names
    df.columns = [c.strip().replace('\ufeff', '').replace('#', 'num') for c in df.columns]
    
    # Drop problematic columns
    for col in list(df.columns):
        if col in DROP_COLUMNS or col.lower() in [c.lower() for c in DROP_COLUMNS]:
            df = df.drop(columns=[col])
    
    # Process each column by type
    int_cols_lower = {c.lower() for c in INTEGER_COLUMNS}
    float_cols_lower = {c.lower() for c in FLOAT_COLUMNS}
    bool_cols_lower = {c.lower() for c in BOOLEAN_COLUMNS}
    
    for col in df.columns:
        col_lower = col.lower()
        
        if col_lower in int_cols_lower:
            df[col] = df[col].apply(to_int_safe)
        elif col_lower in float_cols_lower:
            df[col] = df[col].apply(to_float_safe)
        elif col_lower in bool_cols_lower:
            df[col] = df[col].apply(to_bool_safe)
        else:
            # String columns - clean NaN
            df[col] = df[col].apply(lambda x: None if is_nan(x) else (str(x).strip() if x is not None else None))
    
    return df


def df_to_records(df):
    """Convert to list of dicts ensuring no NaN in output."""
    records = []
    
    for idx, row in df.iterrows():
        record = {}
        for col in df.columns:
            val = row[col]
            
            # Final NaN check
            if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
                record[col] = None
            elif isinstance(val, (np.integer, np.int64, np.int32)):
                record[col] = int(val)
            elif isinstance(val, (np.floating, np.float64, np.float32)):
                record[col] = None if (math.isnan(val) or math.isinf(val)) else float(val)
            elif isinstance(val, np.bool_):
                record[col] = bool(val)
            elif pd.isna(val):
                record[col] = None
            else:
                record[col] = val
        
        records.append(record)
    
    return records


def upload_to_supabase(supabase, table_name, records, batch_size=250):
    """Upload records to Supabase."""
    if not records:
        return 0
    
    # Final JSON safety check
    try:
        json.dumps(records[:10])  # Test first 10
    except ValueError as e:
        print(f"  JSON ERROR: {e}")
        # Fix any remaining NaN
        for rec in records:
            for k, v in rec.items():
                if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                    rec[k] = None
    
    total = 0
    errors = []
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        
        try:
            result = supabase.table(table_name).upsert(batch).execute()
            total += len(batch)
        except Exception as e:
            errors.append(str(e)[:80])
    
    if errors:
        for err in errors[:3]:
            print(f"  ERROR: {err}")
    
    return total


def clean_all():
    """Clean all CSVs."""
    os.makedirs(CLEAN_DIR, exist_ok=True)
    
    print("\n" + "="*60)
    print("CLEANING CSV FILES")
    print("="*60)
    
    for table_name, config in sorted(TABLES.items(), key=lambda x: x[1]['order']):
        src = os.path.join(DATA_DIR, config['file'])
        dst = os.path.join(CLEAN_DIR, config['file'])
        
        if not os.path.exists(src):
            continue
        
        print(f"\nCleaning {table_name}...")
        
        try:
            df = pd.read_csv(src, encoding='utf-8', low_memory=False)
        except:
            try:
                df = pd.read_csv(src, encoding='latin-1', low_memory=False)
            except Exception as e:
                print(f"  ERROR: {e}")
                continue
        
        df = clean_dataframe(df, table_name)
        df.to_csv(dst, index=False)
        print(f"  ✓ {len(df)} rows")
    
    print("\n" + "="*60)


def upload_all():
    """Upload all tables."""
    try:
        from supabase import create_client
    except ImportError:
        print("Install: pip3 install supabase --break-system-packages")
        return
    
    print("\n" + "="*60)
    print("UPLOADING TO SUPABASE")
    print("="*60)
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Connected to Supabase")
    
    use_dir = CLEAN_DIR if os.path.exists(CLEAN_DIR) else DATA_DIR
    
    single = None
    if '--table' in sys.argv:
        idx = sys.argv.index('--table')
        if idx + 1 < len(sys.argv):
            single = sys.argv[idx + 1]
    
    total = 0
    
    for table_name, config in sorted(TABLES.items(), key=lambda x: x[1]['order']):
        if single and table_name != single:
            continue
        
        filepath = os.path.join(use_dir, config['file'])
        if not os.path.exists(filepath):
            continue
        
        print(f"\nUploading {table_name}...")
        
        try:
            df = pd.read_csv(filepath, low_memory=False)
            df = clean_dataframe(df, table_name)
            records = df_to_records(df)
            uploaded = upload_to_supabase(supabase, table_name, records)
            print(f"  ✓ {uploaded}/{len(records)} rows")
            total += uploaded
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print(f"\n{'='*60}")
    print(f"COMPLETE: {total} total rows")


def main():
    if '--clean-only' in sys.argv:
        clean_all()
    elif '--upload-only' in sys.argv:
        upload_all()
    else:
        clean_all()
        upload_all()


if __name__ == "__main__":
    main()
