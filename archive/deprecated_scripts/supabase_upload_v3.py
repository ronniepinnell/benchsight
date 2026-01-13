"""
BenchSight Supabase Upload Script v3
Fixed NaN handling, type conversion, and schema alignment

Usage:
    python3 src/supabase_upload_v3.py                    # Upload all tables
    python3 src/supabase_upload_v3.py --table dim_player # Single table
    python3 src/supabase_upload_v3.py --dims             # Dims only
    python3 src/supabase_upload_v3.py --facts            # Facts only
"""

import os
import sys
import configparser
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import math
import json

try:
    from supabase import create_client
except ImportError:
    print("Install supabase: pip3 install supabase --break-system-packages")
    sys.exit(1)

# Load Supabase config from config/config_local.ini
config = configparser.ConfigParser()
config_path = Path(__file__).parent.parent.parent / 'config' / 'config_local.ini'
config.read(config_path)

SUPABASE_URL = config.get('supabase', 'url', fallback="https://uuaowslhpgyiudmbvqze.supabase.co")
SUPABASE_KEY = config.get('supabase', 'service_key', fallback="")

# Data directory
DATA_DIR = "data/output"

# Table definitions with proper column types
TABLE_SCHEMA = {
    'dim_league': {
        'file': 'dim_league.csv',
        'primary_key': 'league_id',
        'int_cols': ['league_id'],
        'order': 1
    },
    'dim_season': {
        'file': 'dim_season.csv',
        'primary_key': 'season_id',
        'int_cols': ['season_id', 'league_id'],
        'order': 2
    },
    'dim_team': {
        'file': 'dim_team.csv',
        'primary_key': 'team_id',
        'int_cols': ['team_id', 'league_id'],
        'order': 3
    },
    'dim_player': {
        'file': 'dim_player.csv',
        'primary_key': 'player_id',
        'int_cols': ['player_id', 'team_id', 'jersey_number', 'skill_rating'],
        'float_cols': ['height', 'weight'],
        'order': 4
    },
    'dim_schedule': {
        'file': 'dim_schedule.csv',
        'primary_key': 'game_id',
        'int_cols': ['game_id', 'season_id', 'home_team_id', 'away_team_id', 'venue_id', 'home_score', 'away_score'],
        'order': 5
    },
    'dim_venue': {
        'file': 'dim_venue.csv',
        'primary_key': 'venue_id',
        'int_cols': ['venue_id'],
        'order': 6
    },
    'dim_video': {
        'file': 'dim_video.csv',
        'primary_key': 'video_id',
        'int_cols': ['video_id', 'game_id'],
        'order': 7
    },
    'dim_event_type': {
        'file': 'dim_event_type.csv',
        'primary_key': 'event_type_id',
        'int_cols': ['event_type_id', 'sort_order'],
        'bool_cols': ['is_shot', 'is_pass', 'is_possession', 'is_turnover', 'is_penalty', 'is_faceoff', 
                      'is_zone_play', 'is_stoppage', 'is_save', 'is_hit', 'is_rebound',
                      'credits_event_player_1', 'credits_opp_player_1', 'affects_toi_playing'],
        'order': 10
    },
    'dim_event_detail': {
        'file': 'dim_event_detail.csv',
        'primary_key': 'event_detail_id',
        'int_cols': ['event_detail_id'],
        'bool_cols': ['is_shot_on_goal', 'is_goal', 'is_miss', 'is_block', 'is_giveaway', 'is_takeaway', 
                      'is_controlled', 'is_success'],
        'order': 11
    },
    'dim_event_detail_2': {
        'file': 'dim_event_detail_2.csv',
        'primary_key': 'event_detail_2_id',
        'int_cols': ['event_detail_2_id'],
        'order': 12
    },
    'dim_play_detail': {
        'file': 'dim_play_detail.csv',
        'primary_key': 'play_detail_id',
        'int_cols': ['play_detail_id', 'points_value'],
        'bool_cols': ['is_offensive', 'is_defensive', 'is_transition', 'is_recovery', 'credits_player'],
        'order': 13
    },
    'dim_turnover_type': {
        'file': 'dim_turnover_type.csv',
        'primary_key': 'turnover_type_id',
        'int_cols': ['turnover_type_id'],
        'bool_cols': ['is_giveaway', 'is_takeaway', 'is_bad_turnover', 'is_neutral_turnover'],
        'float_cols': ['penalty_weight'],
        'order': 14
    },
    'dim_shot_type': {
        'file': 'dim_shot_type.csv',
        'primary_key': 'shot_type_id',
        'int_cols': ['shot_type_id', 'difficulty_rating'],
        'float_cols': ['avg_sh_pct'],
        'bool_cols': ['is_one_timer'],
        'order': 15
    },
    'dim_pass_type': {
        'file': 'dim_pass_type.csv',
        'primary_key': 'pass_type_id',
        'int_cols': ['pass_type_id', 'difficulty_rating'],
        'bool_cols': ['is_slot_pass', 'is_cross_ice'],
        'order': 16
    },
    'dim_net_location': {
        'file': 'dim_net_location.csv',
        'primary_key': 'net_location_id',
        'int_cols': ['net_location_id', 'difficulty_score', 'display_order'],
        'float_cols': ['x_min', 'x_max', 'y_min', 'y_max'],
        'bool_cols': ['goalie_weakness_common'],
        'order': 17
    },
    'dim_stat': {
        'file': 'dim_stat.csv',
        'primary_key': 'stat_id',
        'bool_cols': ['requires_xy', 'higher_is_better'],
        'float_cols': ['benchmark_poor', 'benchmark_avg', 'benchmark_good', 'benchmark_elite'],
        'order': 18
    },
    'dim_strength': {
        'file': 'dim_strength.csv',
        'primary_key': 'strength_id',
        'int_cols': ['strength_id'],
        'order': 20
    },
    'dim_situation': {
        'file': 'dim_situation.csv',
        'primary_key': 'situation_id',
        'int_cols': ['situation_id'],
        'order': 21
    },
    'dim_position': {
        'file': 'dim_position.csv',
        'primary_key': 'position_id',
        'int_cols': ['position_id'],
        'order': 22
    },
    'dim_zone': {
        'file': 'dim_zone.csv',
        'primary_key': 'zone_id',
        'int_cols': ['zone_id'],
        'order': 23
    },
    'dim_period': {
        'file': 'dim_period.csv',
        'primary_key': 'period_id',
        'int_cols': ['period_number', 'period_minutes'],
        'order': 24
    },
    'dim_shift_type': {
        'file': 'dim_shift_type.csv',
        'primary_key': 'shift_type_id',
        'int_cols': ['shift_type_id'],
        'order': 25
    },
    'dim_skill_tier': {
        'file': 'dim_skill_tier.csv',
        'primary_key': 'skill_tier_id',
        'int_cols': ['skill_tier_id'],
        'order': 26
    },
    'dim_player_role': {
        'file': 'dim_player_role.csv',
        'primary_key': 'role_id',
        'int_cols': ['role_id'],
        'order': 27
    },
    'dim_danger_zone': {
        'file': 'dim_danger_zone.csv',
        'primary_key': 'danger_zone_id',
        'int_cols': ['danger_zone_id'],
        'float_cols': ['xg_multiplier'],
        'order': 28
    },
    'dim_time_bucket': {
        'file': 'dim_time_bucket.csv',
        'primary_key': 'time_bucket_id',
        'int_cols': ['time_bucket_id'],
        'order': 29
    },
    'dim_rink_zone': {
        'file': 'dim_rink_zone.csv',
        'primary_key': 'rink_zone_id',
        'int_cols': [],  # rink_zone_id is text like "RC0001"
        'float_cols': ['x_min', 'x_max', 'y_min', 'y_max'],
        'order': 30
    },
    'fact_gameroster': {
        'file': 'fact_gameroster.csv',
        'primary_key': 'roster_key',
        'int_cols': ['player_id', 'game_id', 'team_id', 'jersey_number', 'skill_rating'],
        'order': 50
    },
    'fact_event_players': {
        'file': 'fact_event_players.csv',
        'primary_key': 'event_key',
        'int_cols': ['event_id', 'game_id', 'period', 'shift_id', 'sequence_id', 'play_id',
                     'event_player_1_id', 'event_player_2_id', 'event_player_3_id',
                     'event_player_4_id', 'event_player_5_id', 'event_player_6_id',
                     'opp_player_1_id', 'opp_player_2_id', 'opp_player_3_id',
                     'opp_player_4_id', 'opp_player_5_id', 'opp_player_6_id',
                     'goalie_id', 'team_id', 'video_id', 'penalty_minutes'],
        'float_cols': ['period_time_seconds', 'game_time_seconds', 'video_timestamp_start', 
                       'video_timestamp_end', 'x_coord', 'y_coord'],
        'bool_cols': ['event_successful', 'is_penalty_shot', 'is_empty_net'],
        'order': 51
    },
    'fact_events_long': {
        'file': 'fact_events_long.csv',
        'primary_key': 'event_key',
        'int_cols': ['event_id', 'game_id', 'period', 'shift_id', 'sequence_id', 'play_id',
                     'event_player_1_id', 'event_player_2_id', 'event_player_3_id',
                     'event_player_4_id', 'event_player_5_id', 'event_player_6_id',
                     'opp_player_1_id', 'opp_player_2_id', 'opp_player_3_id',
                     'opp_player_4_id', 'opp_player_5_id', 'opp_player_6_id',
                     'goalie_id', 'team_id', 'video_id', 'penalty_minutes'],
        'float_cols': ['period_time_seconds', 'game_time_seconds', 'video_timestamp_start', 
                       'video_timestamp_end', 'x_coord', 'y_coord'],
        'bool_cols': ['event_successful', 'is_penalty_shot', 'is_empty_net'],
        'order': 52
    },
    'fact_shifts': {
        'file': 'fact_shifts.csv',
        'primary_key': 'shift_key',
        'int_cols': ['shift_id', 'game_id', 'period', 'team_id', 'video_id'],
        'float_cols': ['shift_start_seconds', 'shift_end_seconds', 'shift_duration_seconds',
                       'video_timestamp_start', 'video_timestamp_end'],
        'order': 53
    },
    'fact_shift_players_tracking': {
        'file': 'fact_shift_players_tracking.csv',
        'primary_key': 'shift_player_key',
        'int_cols': ['shift_id', 'game_id', 'player_id', 'team_id', 'period'],
        'float_cols': ['shift_duration_seconds'],
        'order': 54
    },
    'fact_linked_events_tracking': {
        'file': 'fact_linked_events_tracking.csv',
        'primary_key': 'linked_event_key',
        'int_cols': ['linked_event_id', 'game_id', 'primary_event_id', 'secondary_event_id', 
                     'time_between_events'],
        'order': 55
    },
    'fact_sequences_tracking': {
        'file': 'fact_sequences_tracking.csv',
        'primary_key': 'sequence_key',
        'int_cols': ['sequence_id', 'game_id', 'period', 'team_id', 'event_count', 
                     'shot_count', 'goal_count'],
        'float_cols': ['sequence_duration', 'start_time', 'end_time'],
        'order': 56
    },
    'fact_plays_tracking': {
        'file': 'fact_plays_tracking.csv',
        'primary_key': 'play_key',
        'int_cols': ['play_id', 'game_id', 'period', 'sequence_id', 'team_id', 
                     'event_count', 'player_count'],
        'float_cols': ['play_duration', 'start_time', 'end_time'],
        'order': 57
    },
    'fact_event_coordinates': {
        'file': 'fact_event_coordinates.csv',
        'primary_key': 'coord_key',
        'int_cols': ['event_id', 'game_id'],
        'float_cols': ['x_coord', 'y_coord', 'x_normalized', 'y_normalized', 
                       'distance_to_net', 'angle_to_net'],
        'order': 58
    },
    'fact_event_players_tracking': {
        'file': 'fact_event_players_tracking.csv',
        'primary_key': 'event_player_key',
        'int_cols': ['event_id', 'game_id', 'player_id'],
        'order': 59
    },
    'fact_player_game_stats': {
        'file': 'fact_player_game_stats.csv',
        'primary_key': 'player_game_key',
        'int_cols': ['player_id', 'game_id', 'team_id', 'g', 'a', 'a1', 'a2', 'pts', 'sog', 
                     'plus_minus', 'pim', 'hits', 'blk', 'toi', 'toi_ev', 'toi_pp', 'toi_pk',
                     'shifts', 'cf', 'ca', 'ff', 'fa', 'fow', 'fol', 'pen_taken', 'pen_drawn'],
        'float_cols': ['sh_pct', 'cf_pct', 'ff_pct', 'fo_pct', 'toi_min', 'avg_shift',
                       'offensive_rating', 'defensive_rating', 'hustle_rating', 'impact_score'],
        'bool_cols': ['is_tracked'],
        'order': 60
    },
    'fact_goalie_game_stats': {
        'file': 'fact_goalie_game_stats.csv',
        'primary_key': 'goalie_game_key',
        'int_cols': ['player_id', 'game_id', 'team_id', 'toi', 'sa', 'ga', 'saves'],
        'float_cols': ['sv_pct', 'gaa', 'toi_min', 'rebound_pct', 'freeze_pct'],
        'bool_cols': ['quality_start', 'really_bad_start', 'is_tracked'],
        'order': 61
    }
}


def clean_value(val):
    """Clean a single value - handle NaN, None, inf properly."""
    if val is None:
        return None
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
    if isinstance(val, str):
        val_lower = val.lower().strip()
        if val_lower in ('nan', 'none', '', 'null', 'na', 'n/a', '#n/a'):
            return None
        if val_lower in ('true', 'yes', '1'):
            return True
        if val_lower in ('false', 'no', '0'):
            return False
    return val


def convert_to_int(val):
    """Convert value to integer, handling floats like 1001.0."""
    if val is None:
        return None
    try:
        if isinstance(val, str):
            val = val.strip()
            if val.lower() in ('nan', 'none', '', 'null'):
                return None
            # Handle "1001.0" -> 1001
            if '.' in val:
                return int(float(val))
            return int(val)
        if isinstance(val, float):
            if math.isnan(val) or math.isinf(val):
                return None
            return int(val)
        return int(val)
    except (ValueError, TypeError):
        return None


def convert_to_float(val):
    """Convert value to float."""
    if val is None:
        return None
    try:
        if isinstance(val, str):
            val = val.strip()
            if val.lower() in ('nan', 'none', '', 'null', 'high', 'medium', 'low'):
                return None
            return float(val)
        if isinstance(val, float):
            if math.isnan(val) or math.isinf(val):
                return None
            return val
        return float(val)
    except (ValueError, TypeError):
        return None


def convert_to_bool(val):
    """Convert value to boolean."""
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        if math.isnan(val) if isinstance(val, float) else False:
            return None
        return bool(val)
    if isinstance(val, str):
        val_lower = val.lower().strip()
        if val_lower in ('true', 'yes', '1', 't', 'y'):
            return True
        if val_lower in ('false', 'no', '0', 'f', 'n'):
            return False
    return None


def clean_dataframe(df, table_name):
    """Clean dataframe for upload based on table schema."""
    schema = TABLE_SCHEMA.get(table_name, {})
    
    # Remove BOM from column names
    df.columns = [c.strip().replace('\ufeff', '').replace('#', 'num') for c in df.columns]
    
    # Get column type definitions
    int_cols = schema.get('int_cols', [])
    float_cols = schema.get('float_cols', [])
    bool_cols = schema.get('bool_cols', [])
    
    # Clean each column
    for col in df.columns:
        col_lower = col.lower()
        
        # Apply type-specific conversion
        if col in int_cols or col_lower in [c.lower() for c in int_cols]:
            df[col] = df[col].apply(convert_to_int)
        elif col in float_cols or col_lower in [c.lower() for c in float_cols]:
            df[col] = df[col].apply(convert_to_float)
        elif col in bool_cols or col_lower in [c.lower() for c in bool_cols]:
            df[col] = df[col].apply(convert_to_bool)
        else:
            # Clean general values
            df[col] = df[col].apply(clean_value)
    
    # Replace any remaining NaN with None
    df = df.replace({np.nan: None, pd.NaT: None})
    
    # Convert to native Python types
    df = df.astype(object).where(pd.notnull(df), None)
    
    return df


def df_to_records(df):
    """Convert dataframe to list of records with proper None handling."""
    records = []
    for _, row in df.iterrows():
        record = {}
        for col, val in row.items():
            # Final cleanup
            if pd.isna(val) or val is pd.NaT:
                record[col] = None
            elif isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                record[col] = None
            elif isinstance(val, np.integer):
                record[col] = int(val)
            elif isinstance(val, np.floating):
                if math.isnan(val) or math.isinf(val):
                    record[col] = None
                else:
                    record[col] = float(val)
            elif isinstance(val, np.bool_):
                record[col] = bool(val)
            else:
                record[col] = val
        records.append(record)
    return records


def upload_table(supabase, table_name, df, batch_size=500):
    """Upload a single table to Supabase."""
    if len(df) == 0:
        print(f"  SKIP: {table_name} is empty")
        return 0
    
    # Clean the dataframe
    df = clean_dataframe(df, table_name)
    
    # Convert to records
    records = df_to_records(df)
    
    # Upload in batches
    total_uploaded = 0
    errors = []
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        try:
            result = supabase.table(table_name).upsert(batch).execute()
            total_uploaded += len(batch)
        except Exception as e:
            error_msg = str(e)
            # Try to extract JSON error
            try:
                import json
                if hasattr(e, 'message'):
                    error_msg = e.message
                elif 'message' in str(e):
                    error_msg = str(e)
            except Exception:
                pass
            errors.append(f"batch {batch_num}: {error_msg[:100]}")
    
    if errors:
        for err in errors[:3]:  # Show first 3 errors
            print(f"  ERROR {err}")
        if len(errors) > 3:
            print(f"  ... and {len(errors) - 3} more errors")
    
    print(f"  ✓ {table_name}: {total_uploaded}/{len(records)} rows")
    return total_uploaded


def load_csv(filepath):
    """Load CSV with proper encoding handling."""
    try:
        # Try UTF-8 first
        df = pd.read_csv(filepath, encoding='utf-8', low_memory=False)
    except UnicodeDecodeError:
        # Fall back to latin-1
        df = pd.read_csv(filepath, encoding='latin-1', low_memory=False)
    
    # Clean column names
    df.columns = [c.strip().replace('\ufeff', '') for c in df.columns]
    
    return df


def main():
    print("=" * 60)
    print("BENCHSIGHT SUPABASE UPLOAD v3")
    print("=" * 60)
    
    # Parse args
    single_table = None
    dims_only = '--dims' in sys.argv
    facts_only = '--facts' in sys.argv
    
    if '--table' in sys.argv:
        idx = sys.argv.index('--table')
        if idx + 1 < len(sys.argv):
            single_table = sys.argv[idx + 1]
    
    # Connect to Supabase
    print("\nConnecting to Supabase...")
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("  ✓ Connected")
    except Exception as e:
        print(f"  ERROR: {e}")
        return
    
    # Sort tables by order
    sorted_tables = sorted(TABLE_SCHEMA.items(), key=lambda x: x[1].get('order', 999))
    
    total_uploaded = 0
    
    for table_name, schema in sorted_tables:
        # Filter by args
        if single_table and table_name != single_table:
            continue
        if dims_only and not table_name.startswith('dim_'):
            continue
        if facts_only and not table_name.startswith('fact_'):
            continue
        
        filename = schema.get('file')
        filepath = os.path.join(DATA_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"\nSkipping {table_name}: {filename} not found")
            continue
        
        print(f"\nUploading {table_name}...")
        
        try:
            df = load_csv(filepath)
            uploaded = upload_table(supabase, table_name, df)
            total_uploaded += uploaded
        except Exception as e:
            print(f"  ERROR loading {filename}: {e}")
    
    print("\n" + "=" * 60)
    print(f"COMPLETE: {total_uploaded} total rows uploaded")
    print("=" * 60)


if __name__ == "__main__":
    main()
