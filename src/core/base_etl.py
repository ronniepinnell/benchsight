#!/usr/bin/env python3
"""
BENCHSIGHT v5.0.0 - PRODUCTION ETL
==================================

Requirements:
1. Drop ALL columns ending in _ (formula/helper columns)
2. Exclude games 18965, 18993, 19032 from event/shift tracking
3. Ensure player_id present in ALL tables with player data
4. Handle duplicate jersey numbers by using (game_id, team, player_number)
5. Bulletproof keys and integrity
6. Clean folder structure

Author: Senior Dev
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='pandas')
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# Import standardization module
from src.transformation.standardize_play_details import standardize_tracking_data

# Import key utilities
from src.core.key_utils import (
    format_key, generate_event_id, generate_shift_id,
    normalize_dataframe_codes, add_all_keys, rename_standard_columns,
    normalize_player_role, generate_sequences_and_plays, 
    add_fact_events_fkeys, add_fact_event_players_fkeys,
    generate_event_chain_key
)

# Import centralized key parser
from src.utils.key_parser import parse_shift_key, make_shift_key, convert_le_to_lv_key

# Import safe CSV utilities (with fallback)
try:
    from src.core.safe_csv import safe_write_csv, safe_read_csv, CSVWriteError
    SAFE_CSV_AVAILABLE = True
except ImportError:
    SAFE_CSV_AVAILABLE = False

# Import central table writer for Supabase integration
from src.core.table_writer import (
    save_output_table, 
    enable_supabase as enable_supabase_upload,
    disable_supabase as disable_supabase_upload,
    is_supabase_enabled
)

# Import table store for in-memory access (allows ETL to work from scratch)
try:
    from src.core.table_store import get_table as get_table_from_store
    TABLE_STORE_AVAILABLE = True
except ImportError:
    TABLE_STORE_AVAILABLE = False
    def get_table_from_store(name, output_dir=None):
        return pd.DataFrame()

# Import table builders (v29.1)
from src.builders.events import build_fact_events
from src.builders.shifts import build_fact_shifts

# ============================================================
# CONFIGURATION
# ============================================================

BLB_PATH = Path("data/raw/BLB_Tables.xlsx")
GAMES_DIR = Path("data/raw/games")
OUTPUT_DIR = Path("data/output")
LOG_FILE = Path("logs/etl_v5.log")

# Config file for excluded games (incomplete data)
EXCLUDED_GAMES_FILE = Path("config/excluded_games.txt")

def discover_games():
    """
    Dynamically discover games from data/raw/games/ folder.
    
    Returns:
        tuple: (valid_games, excluded_games)
        - valid_games: List of game IDs with complete tracking data
        - excluded_games: List of game IDs to exclude (from config or auto-detected)
    """
    # Load excluded games from config file (if exists)
    excluded = set()
    if EXCLUDED_GAMES_FILE.exists():
        with open(EXCLUDED_GAMES_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    excluded.add(line)
    
    # Discover all game folders
    all_games = []
    if GAMES_DIR.exists():
        for game_dir in sorted(GAMES_DIR.iterdir()):
            if game_dir.is_dir() and game_dir.name.isdigit():
                all_games.append(game_dir.name)
    
    # Validate each game has complete tracking data
    valid_games = []
    auto_excluded = []
    
    for game_id in all_games:
        if game_id in excluded:
            continue
            
        game_dir = GAMES_DIR / game_id
        tracking_files = list(game_dir.glob("*_tracking.xlsx"))
        tracking_files = [f for f in tracking_files if 'bkup' not in str(f).lower()]
        
        if not tracking_files:
            auto_excluded.append(game_id)
            continue
        
        # Check if tracking file has required sheets and data
        try:
            xlsx_path = tracking_files[0]
            xl = pd.ExcelFile(xlsx_path)
            
            has_events = 'events' in xl.sheet_names
            has_shifts = 'shifts' in xl.sheet_names
            
            if has_events:
                events = pd.read_excel(xlsx_path, sheet_name='events', nrows=10)
                # Accept either tracking_event_index (old format) or event_index (new tracker format)
                has_index = 'tracking_event_index' in events.columns or 'event_index' in events.columns
                has_enough_rows = len(events) >= 5
                
                if has_index and has_enough_rows:
                    valid_games.append(game_id)
                else:
                    auto_excluded.append(game_id)
            else:
                auto_excluded.append(game_id)
                
        except Exception as e:
            auto_excluded.append(game_id)
    
    return valid_games, list(excluded) + auto_excluded


def save_excluded_games(excluded_games):
    """Save excluded games to config file."""
    EXCLUDED_GAMES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EXCLUDED_GAMES_FILE, 'w') as f:
        f.write("# Excluded games (incomplete tracking data)\n")
        f.write("# Add game IDs one per line\n")
        for game_id in sorted(excluded_games):
            f.write(f"{game_id}\n")


# Will be populated by discover_games() at runtime
VALID_TRACKING_GAMES = []
EXCLUDED_GAMES = []

# ============================================================
# LOGGING
# ============================================================

class ETLLogger:
    def __init__(self):
        self.logs = []
        self.warnings = []
        self.errors = []
        self.issues = []
        
    def info(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] INFO: {msg}"
        print(entry)
        self.logs.append(entry)
    
    def warn(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] WARN: {msg}"
        print(entry)
        self.logs.append(entry)
        self.warnings.append(msg)
    
    def error(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] ERROR: {msg}"
        print(entry)
        self.logs.append(entry)
        self.errors.append(msg)
    
    def issue(self, msg):
        """Log potential data issue for user review"""
        self.issues.append(msg)
        self.warn(f"ISSUE: {msg}")
    
    def section(self, title):
        print(f"\n{'='*60}")
        print(title)
        print('='*60)
    
    def save(self, path):
        with open(path, 'w') as f:
            f.write('\n'.join(self.logs))
            if self.issues:
                f.write('\n\n=== ISSUES FOR USER REVIEW ===\n')
                for issue in self.issues:
                    f.write(f"- {issue}\n")

log = ETLLogger()

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def drop_underscore_columns(df):
    """
    Handle columns ending in _ (formula/helper columns).
    - If non-underscore version exists with data, drop the underscore version
    - If non-underscore version doesn't exist or is empty, rename underscore to non-underscore
    """
    underscore_cols = [c for c in df.columns if c.endswith('_')]
    dropped = []
    
    for col in underscore_cols:
        base = col[:-1]  # Remove trailing underscore
        
        # Check if base column exists and has data
        if base in df.columns and df[base].notna().any():
            # Base has data - drop underscore version
            df = df.drop(columns=[col])
            dropped.append(col)
        elif base not in df.columns:
            # Base doesn't exist - rename underscore to base
            df = df.rename(columns={col: base})
        else:
            # Base exists but empty - use underscore data
            df[base] = df[col].combine_first(df[base])
            df = df.drop(columns=[col])
            dropped.append(col)
    
    return df, dropped

def drop_index_and_unnamed(df):
    """Drop index and Unnamed columns"""
    drop_cols = []
    if 'index' in df.columns:
        drop_cols.append('index')
    drop_cols.extend([c for c in df.columns if 'Unnamed' in str(c)])
    return df.drop(columns=drop_cols, errors='ignore')

def drop_all_null_columns(df):
    """
    Drop columns that are 100% null (all values are null/NaN/None).
    EXCEPTS: coordinate, danger, and XY type columns (these may legitimately be null).
    
    Args:
        df: DataFrame to clean
        
    Returns:
        Tuple of (DataFrame with all-null columns removed, list of removed column names)
    """
    if len(df) == 0:
        return df, []
    
    import re
    
    # Columns to preserve even if 100% null (coordinate, danger, XY type columns)
    preserve_patterns = [
        r'x$', r'_x$', r'^x_',  # x coordinates
        r'y$', r'_y$', r'^y_',  # y coordinates
        r'coord',  # coordinate
        r'danger',  # danger zone/danger type
        r'xy',  # XY type columns
        r'target_x', r'target_y',  # target coordinates
        r'shot_x', r'shot_y',  # shot coordinates
        r'net_target',  # net target coordinates
        r'location_id$',  # location IDs (coordinate-related)
        r'zone_coord',  # zone coordinates
        r'rink_coord',  # rink coordinates
    ]
    
    # Find columns where all values are null
    null_cols = []
    for col in df.columns:
        # Skip if column matches preserve patterns
        should_preserve = any(re.search(pattern, col, re.IGNORECASE) for pattern in preserve_patterns)
        if should_preserve:
            continue
        
        # Check if all values are null/NaN/None/empty string
        if df[col].isna().all():
            null_cols.append(col)
        elif df[col].dtype == 'object':
            # For object columns, also check for empty strings and 'None'/'nan' strings
            non_null = df[col].dropna()
            if len(non_null) == 0:
                null_cols.append(col)
            elif len(non_null) > 0:
                # Check if all non-null values are empty-like
                all_empty = non_null.astype(str).str.strip().isin(['', 'None', 'nan', 'null', 'NaT']).all()
                if all_empty:
                    null_cols.append(col)
    
    if null_cols:
        df = df.drop(columns=null_cols)
    
    return df, null_cols

def clean_numeric_index(val):
    """Convert '1000.0' to '1000'"""
    if pd.isna(val) or val == '' or str(val).lower() in ['nan', 'x', 'none']:
        return None
    try:
        return str(int(float(val)))
    except Exception as e:
        return None


def calculate_derived_columns(df, log):
    """
    Calculate derived columns from minimal input data.
    Makes ETL robust for test data and tracker exports.
    
    IMPORTANT: This function fills in NaN values for rows that are missing data,
    even if other rows in the column have values. This handles the case where
    some games (real data) have full columns while other games (test data) don't.
    
    Calculates:
    - Time columns (duration, running times, total seconds)
    - Zone columns (home_team_zone, away_team_zone)
    - Team columns (team_venue, team_venue_abv, player_team)
    - Player role columns (role_number, role_abrev, side_of_puck)
    - Shift linkage (shift_index from time matching)
    """
    log.info("  Calculating derived columns from minimal input...")
    calculated = []
    
    # ================================================================
    # 1. TIME COLUMNS
    # ================================================================
    
    # Ensure time columns exist and are numeric
    for col in ['event_start_min', 'event_start_sec', 'event_end_min', 'event_end_sec',
                'time_start_total_seconds', 'time_end_total_seconds', 'duration',
                'event_running_start', 'event_running_end', 'running_video_time',
                'period_start_total_running_seconds', 'running_intermission_duration']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # time_start_total_seconds = minutes * 60 + seconds (time remaining in period)
    if 'event_start_min' in df.columns and 'event_start_sec' in df.columns:
        # Calculate for rows where it's missing
        needs_calc = df['time_start_total_seconds'].isna() if 'time_start_total_seconds' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df['event_start_min'] * 60 + df['event_start_sec']
            if 'time_start_total_seconds' not in df.columns:
                df['time_start_total_seconds'] = calc_vals
            else:
                df.loc[needs_calc, 'time_start_total_seconds'] = calc_vals[needs_calc]
            calculated.append('time_start_total_seconds')
    
    if 'event_end_min' in df.columns and 'event_end_sec' in df.columns:
        needs_calc = df['time_end_total_seconds'].isna() if 'time_end_total_seconds' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df['event_end_min'] * 60 + df['event_end_sec']
            if 'time_end_total_seconds' not in df.columns:
                df['time_end_total_seconds'] = calc_vals
            else:
                df.loc[needs_calc, 'time_end_total_seconds'] = calc_vals[needs_calc]
            calculated.append('time_end_total_seconds')
    
    # duration = start_time - end_time (because clock counts down)
    if 'time_start_total_seconds' in df.columns and 'time_end_total_seconds' in df.columns:
        needs_calc = df['duration'].isna() if 'duration' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df['time_start_total_seconds'] - df['time_end_total_seconds']
            calc_vals = calc_vals.clip(lower=0)  # Fix negative durations
            if 'duration' not in df.columns:
                df['duration'] = calc_vals
            else:
                df.loc[needs_calc, 'duration'] = calc_vals[needs_calc]
            calculated.append('duration')
    
    # event_running_start/end = cumulative seconds from game start
    # Period 1: 0-1200, Period 2: 1200-2400, Period 3: 2400-3600
    if 'period' in df.columns and 'time_start_total_seconds' in df.columns:
        df['period'] = pd.to_numeric(df['period'], errors='coerce').fillna(1).astype(int)
        
        needs_calc = df['event_running_start'].isna() if 'event_running_start' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            # Running time = (period-1)*1200 + (1200 - time_remaining)
            calc_vals = (df['period'] - 1) * 1200 + (1200 - df['time_start_total_seconds'])
            if 'event_running_start' not in df.columns:
                df['event_running_start'] = calc_vals
            else:
                df.loc[needs_calc, 'event_running_start'] = calc_vals[needs_calc]
            calculated.append('event_running_start')
        
        needs_calc = df['event_running_end'].isna() if 'event_running_end' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any() and 'time_end_total_seconds' in df.columns:
            calc_vals = (df['period'] - 1) * 1200 + (1200 - df['time_end_total_seconds'])
            if 'event_running_end' not in df.columns:
                df['event_running_end'] = calc_vals
            else:
                df.loc[needs_calc, 'event_running_end'] = calc_vals[needs_calc]
            calculated.append('event_running_end')
    
    # period_start_total_running_seconds (for video sync)
    if 'period' in df.columns:
        needs_calc = df['period_start_total_running_seconds'].isna() if 'period_start_total_running_seconds' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = (df['period'] - 1) * 1200
            if 'period_start_total_running_seconds' not in df.columns:
                df['period_start_total_running_seconds'] = calc_vals
            else:
                df.loc[needs_calc, 'period_start_total_running_seconds'] = calc_vals[needs_calc]
            calculated.append('period_start_total_running_seconds')
    
    # running_video_time (estimate from running_start, can be adjusted)
    if 'event_running_start' in df.columns:
        needs_calc = df['running_video_time'].isna() if 'running_video_time' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            # Add ~15 min per intermission (periods 2,3 have intermissions before them)
            intermission_offset = df['period'].apply(lambda p: (p - 1) * 900 if pd.notna(p) and p > 1 else 0)
            calc_vals = df['event_running_start'] + intermission_offset
            if 'running_video_time' not in df.columns:
                df['running_video_time'] = calc_vals
            else:
                df.loc[needs_calc, 'running_video_time'] = calc_vals[needs_calc]
            calculated.append('running_video_time')
    
    # running_intermission_duration
    if 'period' in df.columns:
        needs_calc = df['running_intermission_duration'].isna() if 'running_intermission_duration' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df['period'].apply(lambda p: (p - 1) * 900 if pd.notna(p) and p > 1 else 0)
            if 'running_intermission_duration' not in df.columns:
                df['running_intermission_duration'] = calc_vals
            else:
                df.loc[needs_calc, 'running_intermission_duration'] = calc_vals[needs_calc]
            calculated.append('running_intermission_duration')
    
    # ================================================================
    # 2. TEAM/VENUE COLUMNS
    # ================================================================
    
    # Determine team column (could be 'team_', 'team', or derived)
    team_col = None
    for col in ['team_', 'team', 'team_venue']:
        if col in df.columns and df[col].notna().any():
            team_col = col
            break
    
    if team_col:
        # team_venue (home/away)
        needs_calc = df['team_venue'].isna() if 'team_venue' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df[team_col].apply(lambda x: str(x).lower() if pd.notna(x) else None)
            if 'team_venue' not in df.columns:
                df['team_venue'] = calc_vals
            else:
                df.loc[needs_calc, 'team_venue'] = calc_vals[needs_calc]
            calculated.append('team_venue')
        
        # team_venue_abv (H/A)
        needs_calc = df['team_venue_abv'].isna() if 'team_venue_abv' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df['team_venue'].apply(
                lambda x: 'H' if str(x).lower() == 'home' else ('A' if str(x).lower() == 'away' else None)
            )
            if 'team_venue_abv' not in df.columns:
                df['team_venue_abv'] = calc_vals
            else:
                df.loc[needs_calc, 'team_venue_abv'] = calc_vals[needs_calc]
            calculated.append('team_venue_abv')
        
        # player_team (actual team name)
        if 'home_team' in df.columns and 'away_team' in df.columns:
            needs_calc = df['player_team'].isna() if 'player_team' in df.columns else pd.Series([True]*len(df))
            if needs_calc.any():
                calc_vals = df.apply(
                    lambda r: r.get('home_team') if str(r.get('team_venue', '')).lower() == 'home' 
                              else r.get('away_team') if str(r.get('team_venue', '')).lower() == 'away' 
                              else None, 
                    axis=1
                )
                if 'player_team' not in df.columns:
                    df['player_team'] = calc_vals
                else:
                    df.loc[needs_calc, 'player_team'] = calc_vals[needs_calc]
                calculated.append('player_team')
    
    # ================================================================
    # 3. ZONE COLUMNS
    # ================================================================
    
    if 'event_team_zone' in df.columns and team_col:
        zone_map = {'Offensive': 'Defensive', 'Defensive': 'Offensive', 'Neutral': 'Neutral'}
        
        # home_team_zone
        needs_calc = df['home_team_zone'].isna() if 'home_team_zone' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df.apply(
                lambda r: r.get('event_team_zone') if str(r.get('team_venue', '')).lower() == 'home'
                          else zone_map.get(r.get('event_team_zone'), 'Neutral'),
                axis=1
            )
            if 'home_team_zone' not in df.columns:
                df['home_team_zone'] = calc_vals
            else:
                df.loc[needs_calc, 'home_team_zone'] = calc_vals[needs_calc]
            calculated.append('home_team_zone')
        
        # away_team_zone (opposite of home)
        needs_calc = df['away_team_zone'].isna() if 'away_team_zone' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df['home_team_zone'].map(zone_map)
            if 'away_team_zone' not in df.columns:
                df['away_team_zone'] = calc_vals
            else:
                df.loc[needs_calc, 'away_team_zone'] = calc_vals[needs_calc]
            calculated.append('away_team_zone')
    
    # ================================================================
    # 4. PLAYER ROLE COLUMNS
    # ================================================================
    
    # Determine role column
    role_col = None
    for col in ['role_abrev_binary_', 'role_abrev_binary', 'player_role']:
        if col in df.columns and df[col].notna().any():
            role_col = col
            break
    
    if role_col:
        # player_role (standardized)
        needs_calc = df['player_role'].isna() if 'player_role' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df[role_col]
            if 'player_role' not in df.columns:
                df['player_role'] = calc_vals
            else:
                df.loc[needs_calc, 'player_role'] = calc_vals[needs_calc]
            calculated.append('player_role')
        
        # side_of_puck (event_team/opp_team)
        needs_calc = df['side_of_puck'].isna() if 'side_of_puck' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df['player_role'].apply(
                lambda x: 'event_team' if pd.notna(x) and 'event' in str(x) else ('opp_team' if pd.notna(x) and 'opp' in str(x) else None)
            )
            if 'side_of_puck' not in df.columns:
                df['side_of_puck'] = calc_vals
            else:
                df.loc[needs_calc, 'side_of_puck'] = calc_vals[needs_calc]
            calculated.append('side_of_puck')
        
        # role_number (1, 2, 3...)
        needs_calc = df['role_number'].isna() if 'role_number' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            def extract_role_num(x):
                if pd.isna(x):
                    return 1
                parts = str(x).split('_')
                return int(parts[-1]) if parts[-1].isdigit() else 1
            calc_vals = df['player_role'].apply(extract_role_num)
            if 'role_number' not in df.columns:
                df['role_number'] = calc_vals
            else:
                df.loc[needs_calc, 'role_number'] = calc_vals[needs_calc]
            calculated.append('role_number')
        
        # role_abrev (E1, E2, O1, O2...)
        needs_calc = df['role_abrev'].isna() if 'role_abrev' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            def get_role_abrev(role):
                if pd.isna(role):
                    return None
                role_str = str(role)
                if 'event' in role_str:
                    num = role_str.split('_')[-1] if role_str.split('_')[-1].isdigit() else '1'
                    return f'E{num}'
                elif 'opp' in role_str:
                    num = role_str.split('_')[-1] if role_str.split('_')[-1].isdigit() else '1'
                    return f'O{num}'
                return None
            calc_vals = df['player_role'].apply(get_role_abrev)
            if 'role_abrev' not in df.columns:
                df['role_abrev'] = calc_vals
            else:
                df.loc[needs_calc, 'role_abrev'] = calc_vals[needs_calc]
            calculated.append('role_abrev')
    
    # ================================================================
    # 5. STRENGTH CALCULATION
    # ================================================================
    
    # If strength not provided, default to 5v5
    needs_calc = df['strength'].isna() if 'strength' in df.columns else pd.Series([True]*len(df))
    if needs_calc.any():
        if 'strength' not in df.columns:
            df['strength'] = '5v5'
        else:
            df.loc[needs_calc, 'strength'] = '5v5'
        calculated.append('strength')
    
    # ================================================================
    # 6. PLAY DETAIL COLUMNS
    # ================================================================
    
    # play_detail1 from play_detail1_ if exists
    needs_calc = df['play_detail1'].isna() if 'play_detail1' in df.columns else pd.Series([True]*len(df))
    if needs_calc.any():
        for col in ['play_detail1_', 'play_detail_1']:
            if col in df.columns and df[col].notna().any():
                calc_vals = df[col]
                if 'play_detail1' not in df.columns:
                    df['play_detail1'] = calc_vals
                else:
                    df.loc[needs_calc, 'play_detail1'] = calc_vals[needs_calc]
                calculated.append('play_detail1')
                break
    
    # play_detail_2 / play_detail2
    needs_calc = df['play_detail_2'].isna() if 'play_detail_2' in df.columns else pd.Series([True]*len(df))
    if needs_calc.any():
        for col in ['play_detail2_', 'play_detail2', 'play_detail_2_']:
            if col in df.columns and df[col].notna().any():
                calc_vals = df[col]
                if 'play_detail_2' not in df.columns:
                    df['play_detail_2'] = calc_vals
                else:
                    df.loc[needs_calc, 'play_detail_2'] = calc_vals[needs_calc]
                calculated.append('play_detail_2')
                break
    
    # play_detail_successful
    needs_calc = df['play_detail_successful'].isna() if 'play_detail_successful' in df.columns else pd.Series([True]*len(df))
    if needs_calc.any():
        for col in ['play_detail_successful_', 'play_successful_']:
            if col in df.columns and df[col].notna().any():
                calc_vals = df[col]
                if 'play_detail_successful' not in df.columns:
                    df['play_detail_successful'] = calc_vals
                else:
                    df.loc[needs_calc, 'play_detail_successful'] = calc_vals[needs_calc]
                calculated.append('play_detail_successful')
                break
    
    # ================================================================
    # 7. PRESSURE CALCULATION FROM XY DISTANCE
    # ================================================================
    # Calculate pressured_pressurer when opposing player is within threshold distance
    # This matches the tracker's auto-detection logic
    
    PRESSURE_THRESHOLD_FEET = 10  # Same as tracker default
    
    has_xy = ('player_x' in df.columns and df['player_x'].notna().any()) or \
             ('puck_x_start' in df.columns and df['puck_x_start'].notna().any())
    
    if has_xy and ('player_role' in df.columns or 'side_of_puck' in df.columns):
        # Only calculate if pressured_pressurer not already set
        needs_pressure = (df['pressured_pressurer'].isna()) if 'pressured_pressurer' in df.columns else pd.Series([True]*len(df))
        
        if needs_pressure.any():
            if 'pressured_pressurer' not in df.columns:
                df['pressured_pressurer'] = None
            
            pressure_count = 0
            
            # Get x/y columns
            x_col = 'player_x' if 'player_x' in df.columns and df['player_x'].notna().any() else 'puck_x_start'
            y_col = 'player_y' if 'player_y' in df.columns and df['player_y'].notna().any() else 'puck_y_start'
            
            # Group by event and check for pressure
            if 'event_id' in df.columns or 'tracking_event_index' in df.columns:
                group_col = 'event_id' if 'event_id' in df.columns else 'tracking_event_index'
                
                for event_id, group in df.groupby(group_col):
                    if len(group) < 2:
                        continue
                    
                    # Identify event team vs opp team players
                    if 'side_of_puck' in group.columns:
                        evt_players = group[group['side_of_puck'] == 'event_team']
                        opp_players = group[group['side_of_puck'] == 'opp_team']
                    elif 'player_role' in group.columns:
                        evt_players = group[group['player_role'].str.contains('event', na=False)]
                        opp_players = group[group['player_role'].str.contains('opp', na=False)]
                    else:
                        continue
                    
                    if len(evt_players) == 0 or len(opp_players) == 0:
                        continue
                    
                    # For each event player, find closest opponent
                    for evt_idx, evt_row in evt_players.iterrows():
                        if pd.isna(evt_row.get(x_col)) or pd.isna(evt_row.get(y_col)):
                            continue
                        
                        evt_x = float(evt_row[x_col])
                        evt_y = float(evt_row[y_col])
                        
                        closest_dist = float('inf')
                        closest_opp = None
                        
                        for opp_idx, opp_row in opp_players.iterrows():
                            if pd.isna(opp_row.get(x_col)) or pd.isna(opp_row.get(y_col)):
                                continue
                            
                            opp_x = float(opp_row[x_col])
                            opp_y = float(opp_row[y_col])
                            
                            # Calculate Euclidean distance
                            dist = ((evt_x - opp_x)**2 + (evt_y - opp_y)**2)**0.5
                            
                            if dist <= PRESSURE_THRESHOLD_FEET and dist < closest_dist:
                                closest_dist = dist
                                closest_opp = opp_row.get('player_game_number')
                        
                        # Set pressured_pressurer if within threshold
                        if closest_opp is not None and pd.isna(df.at[evt_idx, 'pressured_pressurer']):
                            df.at[evt_idx, 'pressured_pressurer'] = str(int(float(closest_opp))) if pd.notna(closest_opp) else None
                            pressure_count += 1
            
            if pressure_count > 0:
                calculated.append('pressured_pressurer')
                log.info(f"    Detected {pressure_count} pressure situations from XY distance")
    
    if calculated:
        unique_calcs = list(dict.fromkeys(calculated))  # Remove duplicates while preserving order
        log.info(f"    Calculated {len(unique_calcs)} columns: {', '.join(unique_calcs[:10])}{'...' if len(unique_calcs) > 10 else ''}")
    
    return df


def correct_venue_from_schedule(df: pd.DataFrame, game_id: int, schedule_df: pd.DataFrame, logger) -> pd.DataFrame:
    """
    Correct home/away teams if tracking file has them swapped vs BLB schedule.
    BLB schedule is the authoritative source (NORAD data).
    
    Args:
        df: Events or shifts dataframe
        game_id: Game ID
        schedule_df: dim_schedule dataframe (authoritative)
        logger: Logger instance
    
    Returns:
        Corrected dataframe
    """
    if schedule_df is None or len(schedule_df) == 0:
        return df
    
    # Get authoritative data from schedule
    game_sched = schedule_df[schedule_df['game_id'] == int(game_id)]
    if len(game_sched) == 0:
        return df
    
    blb_home = game_sched['home_team_name'].iloc[0] if 'home_team_name' in game_sched.columns else None
    blb_away = game_sched['away_team_name'].iloc[0] if 'away_team_name' in game_sched.columns else None
    blb_home_id = game_sched['home_team_id'].iloc[0] if 'home_team_id' in game_sched.columns else None
    blb_away_id = game_sched['away_team_id'].iloc[0] if 'away_team_id' in game_sched.columns else None
    
    if not blb_home or not blb_away:
        return df
    
    # Check tracking file values
    tracking_home = df['home_team'].iloc[0] if 'home_team' in df.columns and len(df) > 0 else None
    tracking_away = df['away_team'].iloc[0] if 'away_team' in df.columns and len(df) > 0 else None
    
    if not tracking_home or not tracking_away:
        return df
    
    # Normalize for comparison (strip whitespace, case-insensitive)
    def normalize(s):
        return str(s).strip().lower() if pd.notna(s) else ''
    
    tracking_home_norm = normalize(tracking_home)
    tracking_away_norm = normalize(tracking_away)
    blb_home_norm = normalize(blb_home)
    blb_away_norm = normalize(blb_away)
    
    # Check if swapped
    is_swapped = (tracking_home_norm == blb_away_norm and tracking_away_norm == blb_home_norm)
    
    if is_swapped:
        logger.warn(f"  ⚠️  VENUE SWAP DETECTED - Correcting to BLB schedule")
        logger.warn(f"      Tracking: Home={tracking_home}, Away={tracking_away}")
        logger.warn(f"      BLB:      Home={blb_home}, Away={blb_away}")
        
        df = df.copy()
        
        # Swap team name columns
        if 'home_team' in df.columns and 'away_team' in df.columns:
            df['home_team'] = blb_home
            df['away_team'] = blb_away
        
        # Swap team ID columns
        if 'home_team_id' in df.columns and 'away_team_id' in df.columns:
            df['home_team_id'] = blb_home_id
            df['away_team_id'] = blb_away_id
        
        # Swap zone columns (home becomes away, away becomes home)
        zone_pairs = [
            ('home_team_zone', 'away_team_zone'),
        ]
        for home_col, away_col in zone_pairs:
            if home_col in df.columns and away_col in df.columns:
                df[home_col], df[away_col] = df[away_col].copy(), df[home_col].copy()
        
        # Update team_venue based on corrected home/away
        # If a player's team matches new home_team, they're Home; otherwise Away
        if 'team_venue' in df.columns and 'team' in df.columns:
            df['team_venue'] = df['team'].apply(
                lambda t: 'Home' if normalize(t) == blb_home_norm else 'Away'
            )
        
        logger.info(f"      ✓ Venue corrected")
    
    return df

def validate_key(df, key_col, table_name):
    """Validate a key column has no nulls and no duplicates"""
    issues = []
    
    if key_col not in df.columns:
        issues.append(f"{table_name}: Missing key column '{key_col}'")
        return issues
    
    null_count = df[key_col].isna().sum()
    if null_count > 0:
        issues.append(f"{table_name}.{key_col}: {null_count} NULL values")
    
    dup_count = df.duplicated(subset=[key_col]).sum()
    if dup_count > 0:
        issues.append(f"{table_name}.{key_col}: {dup_count} duplicates")
    
    return issues

def save_table(df, name):
    """Save table to CSV and optionally upload directly to Supabase.
    
    Uses the central table_writer module which handles:
    1. Uploading to Supabase (if enabled) - DataFrame goes directly, no CSV read
    2. Writing to CSV (always, for local backup)
    """
    return save_output_table(df, name, OUTPUT_DIR)

def enhance_gameroster(df, dim_season_df=None, dim_schedule_df=None):
    """Clean and enhance fact_gameroster from BLB.
    
    - Drops redundant columns (index, key, n_player_url, player_game_id, 
      team_game_id, opp_team_game_id, skill_rating)
    - Adds FK columns (season_id, venue_id, position_id)
    - Adds calculated points column
    - Position will be overridden from shifts for tracked games in Phase 5
    """
    log.info("  Enhancing fact_gameroster...")
    
    # Drop redundant columns
    drop_cols = ['index', 'key', 'n_player_url', 'player_game_id', 
                 'team_game_id', 'opp_team_game_id', 'skill_rating']
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])
    
    # Convert numeric columns
    for col in ['goals', 'assist', 'goals_against', 'pim', 'shutouts', 'games_played']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Add points (goals + assists)
    df['points'] = df['goals'] + df['assist']
    
    # Add season_id FK
    # PRIMARY: Join to dim_schedule on game_id (single source of truth)
    # FALLBACK: Map season string for any games not in schedule
    if dim_schedule_df is not None and 'game_id' in df.columns and 'game_id' in dim_schedule_df.columns:
        # Use schedule as authoritative source for season_id
        schedule_season_map = dim_schedule_df.set_index('game_id')['season_id'].to_dict()
        df['season_id'] = df['game_id'].map(schedule_season_map)
        log.info(f"    season_id from schedule: {df['season_id'].notna().sum()}/{len(df)} mapped")
    
    # FALLBACK: For any remaining nulls, try season string mapping
    if dim_season_df is not None and 'season' in df.columns:
        unmapped_mask = df['season_id'].isna() if 'season_id' in df.columns else pd.Series([True] * len(df))
        if unmapped_mask.any():
            # Build comprehensive season map
            season_map = {}
            for _, row in dim_season_df.iterrows():
                sid = row.get('season_id', '')
                season_val = str(row.get('season', ''))
                if sid:
                    # Direct season value mapping (e.g., "2025" -> "N2025S")
                    season_map[season_val] = sid
                    season_map[season_val.replace('-', '')] = sid
                    # Extract year pattern from season_id (e.g., N20232024F -> 20232024)
                    year_part = ''.join(c for c in str(sid) if c.isdigit())
                    if len(year_part) == 8:
                        season_str = f"{year_part[:4]}-{year_part[4:]}"  # 2023-2024
                        season_map[year_part] = sid
                        season_map[season_str] = sid
            # Apply fallback mapping only to unmapped rows
            fallback_ids = df.loc[unmapped_mask, 'season'].astype(str).str.replace('-', '').map(season_map)
            df.loc[unmapped_mask, 'season_id'] = fallback_ids
            log.info(f"    season_id fallback: {fallback_ids.notna().sum()} additional mapped")
    
    # Add venue_id FK based on team_venue (home/away)
    venue_map = {'home': 'VN01', 'Home': 'VN01', 'away': 'VN02', 'Away': 'VN02'}
    if 'team_venue' in df.columns:
        df['venue_id'] = df['team_venue'].map(venue_map)
    
    # Add position_id FK
    pos_id_map = {
        'Forward': 'PS0004', 'forward': 'PS0004',
        'Defense': 'PS0005', 'defense': 'PS0005',
        'Goalie': 'PS0006', 'goalie': 'PS0006',
        'Center': 'PS0001', 'center': 'PS0001',
        'Left Wing': 'PS0002', 'left wing': 'PS0002',
        'Right Wing': 'PS0003', 'right wing': 'PS0003',
    }
    if 'player_position' in df.columns:
        df['position_id'] = df['player_position'].map(pos_id_map)
    
    # Reorder columns logically
    col_order = [
        'game_id', 'player_id',
        'team_id', 'opp_team_id', 'season_id', 'venue_id', 'position_id',
        'team_name', 'opp_team_name', 'team_venue', 'date', 'season',
        'player_full_name', 'player_game_number', 'player_position',
        'goals', 'assist', 'points', 'goals_against', 'pim', 'shutouts', 'games_played',
        'sub', 'current_team'
    ]
    existing_cols = [c for c in col_order if c in df.columns]
    other_cols = [c for c in df.columns if c not in col_order]
    df = df[existing_cols + other_cols]
    
    # Deduplicate on composite key
    before = len(df)
    df = df.drop_duplicates(subset=['game_id', 'player_id'])
    if len(df) < before:
        log.info(f"    Deduped on (game_id, player_id): {before} -> {len(df)}")
    
    log.info(f"    Enhanced: {len(df)} rows, {len(df.columns)} cols")
    return df

# ============================================================
# PHASE 1: LOAD BLB TABLES
# ============================================================

def load_blb_tables():
    log.section("PHASE 1: LOAD BLB_TABLES.XLSX")
    
    xl = pd.ExcelFile(BLB_PATH)
    
    # Sheet to output name mapping
    # IMPORTANT: Load ALL reference tables from BLB_Tables.xlsx
    sheet_map = {
        # Core dimensions
        'dim_player': 'dim_player',
        'dim_team': 'dim_team',
        'dim_league': 'dim_league',
        'dim_season': 'dim_season',
        'dim_schedule': 'dim_schedule',
        'dim_playerurlref': 'dim_playerurlref',
        # dim_rink_zone is generated by code (dimension_tables.py), not loaded from BLB
        'dim_randomnames': 'dim_randomnames',
        
        # Event/Play reference tables (from BLB_Tables, NOT generated!)
        'dim_event_type': 'dim_event_type',
        'dim_event_detail': 'dim_event_detail',
        'dim_event_detail_2': 'dim_event_detail_2',
        'dim_play_detail': 'dim_play_detail',
        'dim_play_detail_2': 'dim_play_detail_2',
        
        # Fact tables
        'fact_gameroster': 'fact_gameroster',
        'fact_leadership': 'fact_leadership',
        'fact_registration': 'fact_registration',
        'fact_draft': 'fact_draft',
        # Removed: 'Fact_PlayerGames' - redundant with fact_gameroster
    }
    
    # Primary keys for each table
    primary_keys = {
        'dim_player': 'player_id',
        'dim_team': 'team_id',
        'dim_league': 'league_id',
        'dim_season': 'season_id',
        'dim_schedule': 'game_id',
        'fact_gameroster': None,  # Composite: (game_id, player_id)
        'fact_leadership': None,  # Composite key
        'fact_registration': 'player_season_registration_id',
        'fact_draft': 'player_draft_id',
    }
    
    loaded = {}
    
    for sheet, output in sheet_map.items():
        if sheet not in xl.sheet_names:
            log.warn(f"Sheet '{sheet}' not found")
            continue
        
        log.info(f"Loading {sheet}...")
        df = pd.read_excel(BLB_PATH, sheet_name=sheet, dtype=str)
        
        # Clean
        df = drop_index_and_unnamed(df)
        df, dropped = drop_underscore_columns(df)
        if dropped:
            log.info(f"  Dropped {len(dropped)} underscore columns")
        
        # Deduplicate based on primary key if exists
        pk = primary_keys.get(output)
        if pk and pk in df.columns:
            before = len(df)
            df = df.drop_duplicates(subset=[pk])
            if len(df) < before:
                log.info(f"  Deduped on {pk}: {before} -> {len(df)}")
            
            # Validate key
            issues = validate_key(df, pk, output)
            for issue in issues:
                log.error(issue)
        
        # Special handling for fact_gameroster - clean and enhance
        if output == 'fact_gameroster':
            df = enhance_gameroster(df, loaded.get('dim_season'), loaded.get('dim_schedule'))
        
        # Special handling for dim_play_detail_2 - rename columns to have _2 suffix
        # BLB sheet has: play_detail_id, play_detail_code, play_detail_name
        # We need: play_detail_2_id, play_detail_2_code, play_detail_2_name
        if output == 'dim_play_detail_2':
            rename_map = {
                'play_detail_id': 'play_detail_2_id',
                'play_detail_code': 'play_detail_2_code',
                'play_detail_name': 'play_detail_2_name',
            }
            df = df.rename(columns=rename_map)
            log.info(f"  Renamed columns for {output}: {list(rename_map.keys())}")
        
        # ============================================================
        # v23.0 CLEANUP: Remove legacy columns and filter tables
        # ============================================================
        
        # dim_player: Remove 7 CSAH-specific columns (all 100% null, legacy)
        if output == 'dim_player':
            csah_cols_to_remove = [
                'player_hand', 'player_notes', 'player_csaha',
                'player_norad_primary_number', 'player_csah_primary_number',
                'player_csah_current_team', 'player_csah_current_team_id'
            ]
            existing_to_remove = [c for c in csah_cols_to_remove if c in df.columns]
            if existing_to_remove:
                df = df.drop(columns=existing_to_remove)
                log.info(f"  Removed {len(existing_to_remove)} CSAH columns from dim_player")
        
        # dim_team: Filter to NORAD teams only, remove csah_team column
        if output == 'dim_team':
            before_count = len(df)
            if 'norad_team' in df.columns:
                df = df[df['norad_team'].astype(str).str.upper() == 'Y']
                log.info(f"  Filtered dim_team to NORAD only: {before_count} -> {len(df)} rows")
            if 'csah_team' in df.columns:
                df = df.drop(columns=['csah_team'])
                log.info(f"  Removed csah_team column from dim_team")
        
        # dim_schedule: Remove video columns and team_game_id columns
        if output == 'dim_schedule':
            schedule_cols_to_remove = [
                'home_team_game_id', 'away_team_game_id',
                'video_id', 'video_start_time', 'video_end_time', 
                'video_title', 'video_url'
            ]
            existing_to_remove = [c for c in schedule_cols_to_remove if c in df.columns]
            if existing_to_remove:
                df = df.drop(columns=existing_to_remove)
                log.info(f"  Removed {len(existing_to_remove)} video/team_game_id columns from dim_schedule")
        
        loaded[output] = df
        rows, cols = save_table(df, output)
        log.info(f"  Saved {output}: {rows:,} rows, {cols} cols")
    
    return loaded

# ============================================================
# PHASE 2: BUILD PLAYER LOOKUP
# ============================================================

def build_player_lookup(gameroster_df):
    """Build lookup for (game_id, team_name, player_number) -> player_id
    
    This handles duplicate jersey numbers across teams in same game.
    """
    log.section("PHASE 2: BUILD PLAYER LOOKUP")
    
    # VECTORIZED: Build lookup using vectorized operations
    # Filter valid rows
    valid_mask = (
        gameroster_df['game_id'].notna() & 
        gameroster_df['player_game_number'].notna() & 
        gameroster_df['player_id'].notna()
    )
    valid_df = gameroster_df[valid_mask].copy()
    
    if len(valid_df) == 0:
        log.info("No valid roster rows for lookup")
        return {}
    
    # Convert to string types for consistent keys
    valid_df['game_id_str'] = valid_df['game_id'].astype(str)
    valid_df['team_name_str'] = valid_df['team_name'].astype(str).str.strip()
    valid_df['player_num_str'] = valid_df['player_game_number'].astype(str).str.strip()
    
    # Build lookup dicts using vectorized operations
    # Key with team: (game_id, team_name, player_num) -> player_id
    valid_df['key_with_team'] = list(zip(
        valid_df['game_id_str'],
        valid_df['team_name_str'],
        valid_df['player_num_str']
    ))
    lookup = dict(zip(valid_df['key_with_team'], valid_df['player_id']))
    
    # Check for conflicts (same key mapping to different player_ids)
    conflicts = []
    key_counts = valid_df.groupby('key_with_team')['player_id'].nunique()
    conflicting_keys = key_counts[key_counts > 1].index
    if len(conflicting_keys) > 0:
        for key in conflicting_keys:
            players = valid_df[valid_df['key_with_team'] == key]['player_id'].unique()
            conflicts.append(f"Conflict: {key} -> {', '.join(map(str, players))}")
    
    # Also create key without team for fallback
    valid_df['key_simple'] = list(zip(valid_df['game_id_str'], valid_df['player_num_str']))
    simple_lookup = valid_df.drop_duplicates(subset=['key_simple'], keep='first')
    for key, player_id in zip(simple_lookup['key_simple'], simple_lookup['player_id']):
        if key not in lookup:  # Only add if not already in lookup (team key takes precedence)
            lookup[key] = player_id
    
    log.info(f"Built lookup with {len(lookup)} mappings")
    
    if conflicts:
        log.warn(f"Found {len(conflicts)} conflicts (duplicate numbers on different teams)")
        for c in conflicts[:5]:
            log.warn(f"  {c}")
    
    return lookup

# ============================================================
# PHASE 3: LOAD TRACKING DATA
# ============================================================

def load_tracking_data(player_lookup, use_parallel: bool = True):
    log.section("PHASE 3: LOAD TRACKING DATA")
    log.info(f"Valid games: {VALID_TRACKING_GAMES}")
    log.info(f"Excluded games: {EXCLUDED_GAMES}")
    
    # Load schedule for venue correction (BLB is authoritative)
    schedule_path = OUTPUT_DIR / 'dim_schedule.csv'
    schedule_df = pd.read_csv(schedule_path) if schedule_path.exists() else pd.DataFrame()
    if len(schedule_df) > 0:
        log.info(f"Loaded dim_schedule for venue validation: {len(schedule_df)} games")
    
    all_events = []
    all_shifts = []
    
    # Use parallel loading if enabled and we have multiple games
    if use_parallel and len(VALID_TRACKING_GAMES) > 2:
        try:
            from src.utils.parallel_processing import load_games_parallel
            log.info(f"Using parallel game loading ({len(VALID_TRACKING_GAMES)} games)...")
            
            # Load games in parallel (threading for I/O-bound Excel reads)
            events_list, shifts_list, errors = load_games_parallel(
                VALID_TRACKING_GAMES,
                GAMES_DIR,
                player_lookup,
                schedule_df,
                use_threading=True  # Threading better for I/O-bound Excel reads
            )
            
            all_events = events_list
            all_shifts = shifts_list
            
            if errors:
                for error in errors:
                    log.warning(f"  {error}")
            
            log.info(f"  Parallel loading complete: {len(all_events)} event sets, {len(all_shifts)} shift sets")
            
        except Exception as e:
            log.warning(f"Parallel loading failed, falling back to sequential: {e}")
            import traceback
            traceback.print_exc()
            use_parallel = False
    
    # Sequential loading (fallback or if parallel disabled)
    if not use_parallel or len(VALID_TRACKING_GAMES) <= 2:
        for game_id in VALID_TRACKING_GAMES:
            game_dir = GAMES_DIR / game_id
            if not game_dir.exists():
                log.error(f"Game directory not found: {game_dir}")
                continue
            
            # Find tracking file
            tracking_files = list(game_dir.glob("*_tracking.xlsx"))
            tracking_files = [f for f in tracking_files if 'bkup' not in str(f).lower()]
            
            if not tracking_files:
                log.error(f"No tracking file for game {game_id}")
                continue
            
            xlsx_path = tracking_files[0]
            log.info(f"\nLoading game {game_id} from {xlsx_path.name}...")
            
            try:
                xl = pd.ExcelFile(xlsx_path)
                
                # Load events
                if 'events' in xl.sheet_names:
                    df = pd.read_excel(xlsx_path, sheet_name='events', dtype=str)
                    df['game_id'] = game_id
                    
                    # Drop underscore columns
                    df, dropped = drop_underscore_columns(df)
                    log.info(f"  events: {len(df)} raw rows, dropped {len(dropped)} underscore cols")
                    
                    # Filter valid rows - accept either tracking_event_index or event_index
                    index_col = 'tracking_event_index' if 'tracking_event_index' in df.columns else 'event_index'
                    if index_col in df.columns:
                        df = df[df[index_col].apply(
                            lambda x: pd.notna(x) and str(x).replace('.', '').replace('-', '').isdigit()
                        )]
                        log.info(f"  events: {len(df)} valid rows (by {index_col})")
                    
                    # VENUE SWAP CORRECTION: Use BLB schedule as authoritative source
                    df = correct_venue_from_schedule(df, game_id, schedule_df, log)
                    
                    all_events.append(df)
                
                # Load shifts
                if 'shifts' in xl.sheet_names:
                    df = pd.read_excel(xlsx_path, sheet_name='shifts', dtype=str)
                    df['game_id'] = game_id
                    
                    df, dropped = drop_underscore_columns(df)
                    log.info(f"  shifts: {len(df)} raw rows, dropped {len(dropped)} underscore cols")
                    
                    # Filter valid rows
                    if 'shift_index' in df.columns:
                        df = df[df['shift_index'].apply(
                            lambda x: pd.notna(x) and str(x).replace('.', '').isdigit()
                        )]
                        log.info(f"  shifts: {len(df)} valid rows (by shift_index)")
                    
                    all_shifts.append(df)
                    
            except Exception as e:
                log.error(f"Error loading game {game_id}: {e}")
    
    results = {}
    
    # Process events
    if all_events:
        df = pd.concat(all_events, ignore_index=True)
        df = drop_index_and_unnamed(df)
        
        # ================================================================
        # CALCULATE DERIVED COLUMNS FROM MINIMAL INPUT
        # This makes ETL robust for test data and tracker exports
        # ================================================================
        df = calculate_derived_columns(df, log)
        
        # ================================================================
        # NORMALIZE TERMINOLOGY: Rush → Carried
        # Tracker originally used "Rush" for carried zone entries/exits
        # We normalize to "Carried" which is more accurate terminology
        # (NHL "rush" = transition attack with quick shot, not just carrying in)
        # ================================================================
        if 'event_detail_2' in df.columns:
            rush_count = df['event_detail_2'].str.contains('Rush', na=False).sum()
            df['event_detail_2'] = df['event_detail_2'].str.replace('_Rush', '_Carried', regex=False)
            df['event_detail_2'] = df['event_detail_2'].str.replace('Rush', 'Carried', regex=False)
            if rush_count > 0:
                log.info(f"  Normalized {rush_count} 'Rush' → 'Carried' in event_detail_2")
        
        # Generate keys using correct index columns:
        # - event_id uses event_index (sequential event counter)
        # - tracking_event_key uses tracking_event_index (can differ for zone entries, etc.)
        if 'event_index' in df.columns:
            df['event_index_clean'] = df['event_index'].apply(clean_numeric_index)
        else:
            # Fallback if event_index doesn't exist
            df['event_index_clean'] = df['tracking_event_index'].apply(clean_numeric_index)
            log.warn("  Using tracking_event_index as fallback for event_index")
        
        # Generate event_id from event_index (NOT tracking_event_index)
        df['event_id'] = df.apply(
            lambda r: format_key('EV', r.get('game_id'), r.get('event_index_clean')), 
            axis=1
        )
        df = df[df['event_id'].notna()]
        df = df.drop(columns=['event_index_clean'], errors='ignore')
        
        # Add all composite keys
        df = add_all_keys(df)
        
        # Normalize data (hyphens, slashes, typos)
        df = rename_standard_columns(df)
        df = normalize_dataframe_codes(df)
        
        # Normalize player_role
        if 'player_role' in df.columns:
            df['player_role'] = df['player_role'].apply(normalize_player_role)
        
        # Add is_goal flag EARLY so it's available for sequences/plays
        # Goal = event_type='Goal' AND event_detail='Goal_Scored' ONLY
        # CRITICAL: Only event_player_1 gets is_goal=1 (the scorer)
        # Other players on the same event (assists, goalie) should NOT have is_goal=1
        # Assists are in play_detail1/play_detail2, NOT event_player_2/3
        df['is_goal'] = (
            (df['event_type'] == 'Goal') & 
            (df['event_detail'] == 'Goal_Scored') &
            (df['player_role'] == 'event_player_1')
        ).astype(int)
        log.info(f"  is_goal flag: {df['is_goal'].sum()} goals identified")
        
        # Generate sequences and plays
        log.info("Generating sequences and plays...")
        df = generate_sequences_and_plays(df)
        seq_count = df['sequence_key'].notna().sum()
        play_count = df['play_key'].notna().sum()
        log.info(f"  sequence_key: {seq_count}/{len(df)}")
        log.info(f"  play_key: {play_count}/{len(df)}")
        
        # Link player_id
        df = link_player_ids(df, player_lookup, 'player_game_number', 'team_venue')
        
        # Standardize play_detail values (prefixed → simple)
        log.info("Standardizing play_detail values...")
        df = standardize_tracking_data(df, OUTPUT_DIR, normalize_to_simple=True)
        
        # Drop redundant index columns (keep only keys)
        index_cols_to_drop = [
            'event_index', 'tracking_event_index', 'linked_event_index',
            'sequence_index', 'play_index', 'shift_index', 'zone_change_index'
        ]
        dropped = [c for c in index_cols_to_drop if c in df.columns]
        df = df.drop(columns=dropped, errors='ignore')
        if dropped:
            log.info(f"  Dropped {len(dropped)} index columns (keys retained)")
        
        # Add FK columns
        log.info("Adding FK columns...")
        df = add_fact_event_players_fkeys(df, OUTPUT_DIR)
        fk_cols = [c for c in df.columns if c.endswith('_id') and c not in ['event_id', 'game_id', 'player_id']]
        log.info(f"  Added {len(fk_cols)} FK columns")
        
        # Add event_chain_key
        log.info("Adding event_chain_key...")
        df['event_chain_key'] = df.apply(generate_event_chain_key, axis=1)
        log.info(f"  event_chain_key: {df['event_chain_key'].notna().sum()}/{len(df)}")
        
        # Reorder columns - keys, FKs, then values
        key_cols = ['event_id', 'game_id', 'player_id', 'player_game_number',
                    'sequence_key', 'play_key', 'shift_key', 'linked_event_key',
                    'event_chain_key', 'tracking_event_key', 'zone_change_key']
        fk_id_cols = ['period_id', 'event_type_id', 'event_detail_id', 'event_detail_2_id',
                      'event_success_id', 'event_zone_id', 'home_zone_id', 'away_zone_id',
                      'home_team_id', 'away_team_id', 'player_team_id', 'team_venue_id',
                      'player_role_id', 'play_detail_id', 'play_detail_2_id', 'play_success_id']
        priority_cols = key_cols + fk_id_cols
        other_cols = [c for c in df.columns if c not in priority_cols]
        df = df[[c for c in priority_cols if c in df.columns] + other_cols]
        
        # v23.0: Remove unused flag columns
        unused_cols = ['event_index_flag', 'sequence_index_flag', 'play_index_flag']
        existing_unused = [c for c in unused_cols if c in df.columns]
        if existing_unused:
            df = df.drop(columns=existing_unused)
            log.info(f"  Removed {len(existing_unused)} unused flag columns: {existing_unused}")
        
        # v23.1: Remove duplicate columns
        duplicate_cols = ['team', 'Type', 'play_detail2']  # team=team_venue, Type=event_type, play_detail2=play_detail_2
        existing_dups = [c for c in duplicate_cols if c in df.columns]
        if existing_dups:
            df = df.drop(columns=existing_dups)
            log.info(f"  Removed {len(existing_dups)} duplicate columns: {existing_dups}")
        
        results['fact_event_players'] = df
        save_table(df, 'fact_event_players')
        log.info(f"\nCombined events: {len(df):,} rows, {len(df.columns)} cols, {df['game_id'].nunique()} games")
        log.info(f"  player_id linked: {df['player_id'].notna().sum()}/{len(df)}")
    
    # Process shifts
    if all_shifts:
        df = pd.concat(all_shifts, ignore_index=True)
        df = drop_index_and_unnamed(df)
        
        # Generate shift_id using standard key format
        df['shift_index'] = df['shift_index'].apply(clean_numeric_index)
        df['shift_id'] = df.apply(generate_shift_id, axis=1)
        df = df[df['shift_id'].notna()]
        
        # Reorder columns
        priority_cols = ['shift_id', 'game_id', 'shift_index']
        other_cols = [c for c in df.columns if c not in priority_cols]
        df = df[priority_cols + other_cols]
        
        results['fact_shifts'] = df
        save_table(df, 'fact_shifts')
        log.info(f"Combined shifts: {len(df):,} rows, {df['game_id'].nunique()} games")
    
    return results

def link_player_ids(df, lookup, player_col, team_col):
    """Link player_id using lookup, handling team for duplicates"""
    
    def get_player_id(row):
        game_id = str(row.get('game_id', ''))
        player_num = str(row.get(player_col, '')).strip()
        
        if not game_id or not player_num:
            return None
        
        # Try with team first (more accurate)
        team = str(row.get(team_col, '')).strip()
        if team:
            # Map venue to team name if needed
            if team.lower() in ['home', 'h']:
                team = str(row.get('home_team', '')).strip()
            elif team.lower() in ['away', 'a']:
                team = str(row.get('away_team', '')).strip()
            
            key = (game_id, team, player_num)
            if key in lookup:
                return lookup[key]
        
        # Fallback to simple lookup
        simple_key = (game_id, player_num)
        return lookup.get(simple_key)
    
    df['player_id'] = df.apply(get_player_id, axis=1)
    return df

# ============================================================
# PHASE 4: CREATE DERIVED TABLES
# ============================================================

def create_derived_tables(tracking_data, player_lookup):
    log.section("PHASE 4: CREATE DERIVED TABLES")
    
    # 1. fact_events - one row per event (v29.1: using builder)
    if 'fact_event_players' in tracking_data:
        log.info("Creating fact_events...")
        tracking = tracking_data['fact_event_players']
        
        # Use builder function (extracted for modularity and testability)
        events = build_fact_events(tracking, OUTPUT_DIR, save=True)
        
        log.info(f"  fact_events: {len(events):,} rows, {len(events.columns)} cols")
        log.info(f"  FKs: period_id={events['period_id'].notna().sum()}, event_type_id={events['event_type_id'].notna().sum()}, event_detail_id={events['event_detail_id'].notna().sum()}")
    
    # 2. fact_tracking - one row per tracking point (for XY coordinates)
    if 'fact_event_players' in tracking_data:
        log.info("Creating fact_tracking...")
        tracking = tracking_data['fact_event_players']
        
        # Get unique tracking events (one row per tracking_event_key)
        fact_tracking = tracking.groupby('tracking_event_key', as_index=False).first()
        
        # Select columns relevant for location/timing
        keep_cols = [
            'tracking_event_key',  # PK
            'game_id',
            'period',
            'period_id',
            'event_start_min',
            'event_start_sec', 
            'event_end_min',
            'event_end_sec',
            'time_start_total_seconds',
            'time_end_total_seconds',
            'running_video_time',
            'event_running_start',
            'event_running_end',
            'event_team_zone',
            'event_zone_id',
            'home_team_zone',
            'home_zone_id',
            'away_team_zone',
            'away_zone_id',
        ]
        fact_tracking = fact_tracking[[c for c in keep_cols if c in fact_tracking.columns]]
        
        # Add placeholder columns for future XY coordinates
        fact_tracking['x_coord'] = None
        fact_tracking['y_coord'] = None
        fact_tracking['rink_zone'] = None
        
        save_table(fact_tracking, 'fact_tracking')
        log.info(f"  fact_tracking: {len(fact_tracking):,} rows, {len(fact_tracking.columns)} cols")
    
    # 3. fact_shifts - one row per shift (v29.1: using builder)
    if 'fact_shifts' in tracking_data:
        log.info("Creating fact_shifts...")
        shifts_tracking = tracking_data['fact_shifts']
        
        # Use builder function (extracted for modularity and testability)
        shifts = build_fact_shifts(shifts_tracking, OUTPUT_DIR, save=True)
        
        log.info(f"  fact_shifts: {len(shifts):,} rows")
    
    # 4. fact_shift_players - one row per player per shift
    if 'fact_shifts' in tracking_data:
        log.info("Creating fact_shift_players...")
        shifts_tracking = tracking_data['fact_shifts']
        
        positions = [
            ('home_forward_1', 'home', 'F1'), ('home_forward_2', 'home', 'F2'),
            ('home_forward_3', 'home', 'F3'), ('home_defense_1', 'home', 'D1'),
            ('home_defense_2', 'home', 'D2'), ('home_goalie', 'home', 'G'),
            ('away_forward_1', 'away', 'F1'), ('away_forward_2', 'away', 'F2'),
            ('away_forward_3', 'away', 'F3'), ('away_defense_1', 'away', 'D1'),
            ('away_defense_2', 'away', 'D2'), ('away_goalie', 'away', 'G'),
        ]
        
        rows = []
        for _, shift in shifts_tracking.iterrows():
            for col, venue, pos in positions:
                if col in shift and pd.notna(shift[col]) and str(shift[col]).strip():
                    player_num = str(shift[col]).strip()
                    game_id = shift['game_id']
                    
                    # Get team name for player lookup
                    team_name = shift.get(f'{venue}_team', '')
                    
                    # Look up player_id
                    player_id = None
                    if team_name:
                        key = (game_id, str(team_name).strip(), player_num)
                        player_id = player_lookup.get(key)
                    if not player_id:
                        key = (game_id, player_num)
                        player_id = player_lookup.get(key)
                    
                    # Venue code: H (home) or A (away)
                    venue_code = 'H' if venue == 'home' else 'A'
                    shift_idx = int(shift['shift_index'])
                    pid_str = player_id if player_id else 'NULL'
                    rows.append({
                        'shift_player_id': f"SP{int(game_id):05d}{shift_idx:05d}{pid_str}",
                        'shift_id': shift['shift_id'],
                        'game_id': game_id,
                        'shift_index': shift['shift_index'],
                        'player_game_number': player_num,
                        'player_id': player_id,
                        'venue': venue,
                        'position': pos,
                        'period': shift.get('Period') or shift.get('period'),
                    })
        
        shift_players = pd.DataFrame(rows)
        shift_players = shift_players.drop_duplicates(subset=['shift_player_id'])
        
        save_table(shift_players, 'fact_shift_players')
        log.info(f"  fact_shift_players: {len(shift_players):,} rows")
        log.info(f"  player_id linked: {shift_players['player_id'].notna().sum()}/{len(shift_players)}")

# ============================================================
# PHASE 5: CREATE REFERENCE TABLES
# ============================================================

def create_reference_tables():
    log.section("PHASE 5: CREATE REFERENCE TABLES")
    
    # dim_player_role - 14 roles
    roles = []
    for i in range(1, 7):
        roles.append({
            'role_id': f'PR{i:02d}', 
            'role_code': f'event_player_{i}',
            'role_name': f'Event Player {i}',
            'role_type': 'event_team',
            'sort_order': i
        })
    roles.append({
        'role_id': 'PR07', 
        'role_code': 'event_goalie',
        'role_name': 'Event Team Goalie',
        'role_type': 'event_team',
        'sort_order': 7
    })
    for i in range(1, 7):
        roles.append({
            'role_id': f'PR{7+i:02d}',
            'role_code': f'opp_player_{i}',
            'role_name': f'Opponent Player {i}',
            'role_type': 'opp_team',
            'sort_order': 7 + i
        })
    roles.append({
        'role_id': 'PR14',
        'role_code': 'opp_goalie',
        'role_name': 'Opponent Goalie',
        'role_type': 'opp_team',
        'sort_order': 14
    })
    save_table(pd.DataFrame(roles), 'dim_player_role')
    log.info("dim_player_role: 14 rows")
    
    # dim_position
    positions = [
        {'position_id': 'POS01', 'position_code': 'C', 'position_name': 'Center', 'position_type': 'forward'},
        {'position_id': 'POS02', 'position_code': 'LW', 'position_name': 'Left Wing', 'position_type': 'forward'},
        {'position_id': 'POS03', 'position_code': 'RW', 'position_name': 'Right Wing', 'position_type': 'forward'},
        {'position_id': 'POS04', 'position_code': 'F', 'position_name': 'Forward', 'position_type': 'forward'},
        {'position_id': 'POS05', 'position_code': 'D', 'position_name': 'Defense', 'position_type': 'defense'},
        {'position_id': 'POS06', 'position_code': 'G', 'position_name': 'Goalie', 'position_type': 'goalie'},
    ]
    save_table(pd.DataFrame(positions), 'dim_position')
    log.info("dim_position: 6 rows")
    
    # dim_zone
    zones = [
        {'zone_id': 'ZN01', 'zone_code': 'O', 'zone_name': 'Offensive Zone', 'zone_abbrev': 'OZ'},
        {'zone_id': 'ZN02', 'zone_code': 'D', 'zone_name': 'Defensive Zone', 'zone_abbrev': 'DZ'},
        {'zone_id': 'ZN03', 'zone_code': 'N', 'zone_name': 'Neutral Zone', 'zone_abbrev': 'NZ'},
    ]
    save_table(pd.DataFrame(zones), 'dim_zone')
    log.info("dim_zone: 3 rows")
    
    # dim_period
    periods = [
        {'period_id': 'P01', 'period_number': 1, 'period_name': '1st Period', 'period_type': 'regulation', 'period_minutes': 18},
        {'period_id': 'P02', 'period_number': 2, 'period_name': '2nd Period', 'period_type': 'regulation', 'period_minutes': 18},
        {'period_id': 'P03', 'period_number': 3, 'period_name': '3rd Period', 'period_type': 'regulation', 'period_minutes': 18},
        {'period_id': 'P04', 'period_number': 4, 'period_name': 'Overtime', 'period_type': 'overtime', 'period_minutes': 5},
        {'period_id': 'P05', 'period_number': 5, 'period_name': 'Shootout', 'period_type': 'shootout', 'period_minutes': 0},
    ]
    save_table(pd.DataFrame(periods), 'dim_period')
    log.info("dim_period: 5 rows")
    
    # dim_venue
    venues = [
        {'venue_id': 'VN01', 'venue_code': 'home', 'venue_name': 'Home', 'venue_abbrev': 'H'},
        {'venue_id': 'VN02', 'venue_code': 'away', 'venue_name': 'Away', 'venue_abbrev': 'A'},
    ]
    save_table(pd.DataFrame(venues), 'dim_venue')
    log.info("dim_venue: 2 rows")
    
    # dim_event_type - LOADED FROM BLB_Tables.xlsx (not generated!)
    # The sheet has more comprehensive data than the hardcoded EVENT_TYPES
    if not Path(OUTPUT_DIR / 'dim_event_type.csv').exists():
        log.warn("dim_event_type not loaded from BLB - generating from hardcoded...")
        from src.models.dimensions import EVENT_TYPES
        event_types = []
        for et in EVENT_TYPES:
            event_types.append({
                'event_type_id': f"ET{et['event_type_id']:04d}",
                'event_type_code': et['event_type'],
                'event_type_name': et['event_type'].replace('_', ' '),
                'event_category': et.get('event_category', 'other'),
                'description': et.get('description', ''),
                'is_corsi': et.get('is_corsi', False),
                'is_fenwick': et.get('is_fenwick', False),
            })
        save_table(pd.DataFrame(event_types), 'dim_event_type')
        log.info(f"dim_event_type: {len(event_types)} rows (generated)")
    else:
        log.info("dim_event_type: using BLB_Tables data")
    
    # dim_event_detail - LOADED FROM BLB_Tables.xlsx (not generated!)
    if not Path(OUTPUT_DIR / 'dim_event_detail.csv').exists():
        log.warn("dim_event_detail not loaded from BLB - generating from hardcoded...")
        from src.models.dimensions import EVENT_DETAILS
        event_details = []
        for ed in EVENT_DETAILS:
            event_details.append({
                'event_detail_id': f"ED{ed['event_detail_id']:04d}",
                'event_detail_code': ed['event_detail'],
                'event_detail_name': ed['event_detail'].replace('_', ' '),
                'event_type': ed.get('event_type', ''),
                'category': ed.get('category', 'other'),
                'is_shot_on_goal': ed.get('is_shot_on_goal', False),
                'is_goal': ed.get('is_goal', False),
                'is_miss': ed.get('is_miss', False),
                'is_block': ed.get('is_block', False),
                'danger_potential': ed.get('danger_potential', 'low'),
            })
        save_table(pd.DataFrame(event_details), 'dim_event_detail')
        log.info(f"dim_event_detail: {len(event_details)} rows (generated)")
    else:
        log.info("dim_event_detail: using BLB_Tables data")
    
    # dim_event_detail_2 - LOADED FROM BLB_Tables.xlsx (not generated!)
    if not Path(OUTPUT_DIR / 'dim_event_detail_2.csv').exists():
        log.warn("dim_event_detail_2 not loaded from BLB - generating from tracking...")
        _create_dim_event_detail_2()
    else:
        log.info("dim_event_detail_2: using BLB_Tables data")
    
    # dim_success - success codes
    success_codes = [
        {'success_id': 'SC01', 'success_code': 's', 'success_name': 'Successful', 'is_successful': True},
        {'success_id': 'SC02', 'success_code': 'u', 'success_name': 'Unsuccessful', 'is_successful': False},
        {'success_id': 'SC03', 'success_code': 'n', 'success_name': 'Not Applicable', 'is_successful': None},
    ]
    save_table(pd.DataFrame(success_codes), 'dim_success')
    log.info("dim_success: 3 rows")
    
    # dim_shot_type - from models/dimensions.py
    from src.models.dimensions import SHOT_TYPES
    shot_types = []
    for st in SHOT_TYPES:
        shot_types.append({
            'shot_type_id': f"ST{st['shot_type_id']:04d}",
            'shot_type_code': st['shot_type'],
            'shot_type_name': st.get('shot_type_full', st['shot_type']),
            'description': st.get('description', ''),
        })
    save_table(pd.DataFrame(shot_types), 'dim_shot_type')
    log.info(f"dim_shot_type: {len(shot_types)} rows")
    
    # dim_pass_type - from models/dimensions.py
    from src.models.dimensions import PASS_TYPES
    pass_types = []
    for pt in PASS_TYPES:
        pass_types.append({
            'pass_type_id': f"PT{pt['pass_type_id']:04d}",
            'pass_type_code': pt['pass_type'],
            'pass_type_name': pt['pass_type'],
            'description': pt.get('description', ''),
        })
    save_table(pd.DataFrame(pass_types), 'dim_pass_type')
    log.info(f"dim_pass_type: {len(pass_types)} rows")
    
    # dim_zone_entry_type - dynamically from tracking data
    _create_dim_zone_entry_type()
    
    # dim_zone_exit_type - dynamically from tracking data
    _create_dim_zone_exit_type()
    
    # dim_stoppage_type - dynamically from tracking data
    _create_dim_stoppage_type()
    
    # dim_giveaway_type - dynamically from tracking data
    _create_dim_giveaway_type()
    
    # dim_takeaway_type - dynamically from tracking data
    _create_dim_takeaway_type()
    
    # dim_play_detail - LOADED FROM BLB_Tables.xlsx (not generated!)
    if not Path(OUTPUT_DIR / 'dim_play_detail.csv').exists():
        log.warn("dim_play_detail not loaded from BLB - generating from hardcoded...")
        _create_dim_play_detail()
    else:
        log.info("dim_play_detail: using BLB_Tables data")
    
    # dim_play_detail_2 - LOADED FROM BLB_Tables.xlsx (not generated!)
    if not Path(OUTPUT_DIR / 'dim_play_detail_2.csv').exists():
        log.warn("dim_play_detail_2 not loaded from BLB - generating from tracking...")
        _create_dim_play_detail_2()
    else:
        log.info("dim_play_detail_2: using BLB_Tables data")


def _create_dim_event_detail_2():
    """Create dim_event_detail_2 from tracking data."""
    records = []
    
    tracking_path = OUTPUT_DIR / 'fact_event_players.csv'
    if tracking_path.exists():
        tracking = pd.read_csv(tracking_path, low_memory=False)
        
        if 'event_detail_2' in tracking.columns:
            # Get unique codes
            raw_codes = tracking['event_detail_2'].dropna().unique()
            codes = sorted(set(str(c).replace('-', '_').replace('/', '_') for c in raw_codes))
            
            for i, code in enumerate(codes, 1):
                records.append({
                    'event_detail_2_id': f'ED2{i:02d}',
                    'event_detail_2_code': code,
                    'event_detail_2_name': code.replace('_', ' '),
                    'category': 'other',
                })
    
    if records:
        df = pd.DataFrame(records)
        save_table(df, 'dim_event_detail_2')
        log.info(f"dim_event_detail_2: {len(df)} rows")
    else:
        df = pd.DataFrame(columns=['event_detail_2_id', 'event_detail_2_code', 'event_detail_2_name', 'category'])
        save_table(df, 'dim_event_detail_2')
        log.info("dim_event_detail_2: 0 rows (no data)")


def _create_dim_zone_entry_type():
    """Create dim_zone_entry_type from dim_event_detail_2."""
    # Controlled entries = maintain possession (Carried, CarriedBreakaway, Pass - but not PassMiss)
    # Uncontrolled entries = give up possession (DumpIn, Chip, Clear, etc.)
    # NOTE: Tracker's "Rush" type = carried entry with speed, NOT NHL "rush" (which requires quick shot)
    
    records = []
    ed2_path = OUTPUT_DIR / 'dim_event_detail_2.csv'
    if ed2_path.exists():
        ed2 = pd.read_csv(ed2_path, low_memory=False)
        ze_codes = ed2[ed2['event_detail_2_code'].astype(str).str.startswith('ZoneEntry', na=False)]['event_detail_2_code'].unique()
        codes = sorted(set(str(c) for c in ze_codes))
        for i, code in enumerate(codes, 1):
            entry_type = code.replace('ZoneEntry_', '').replace('_', ' ').replace('/', ' ')
            # Rename "Rush" to "Carried" for clarity (tracker's Rush = carried in, not NHL rush)
            entry_type = entry_type.replace('Rush', 'Carried')
            # Controlled = Carried/Rush, CarriedBreakaway/RushBreakaway, Pass (but NOT PassMiss)
            # Handle both old ("Rush") and new ("Carried") terminology
            is_controlled = any(x in code for x in ['_Rush', '_Carried', '_Pass']) and 'Miss' not in code and 'Misplay' not in code
            records.append({
                'zone_entry_type_id': f'ZE{i:04d}',
                'zone_entry_type_code': code,
                'zone_entry_type_name': entry_type,
                'is_controlled': is_controlled,
            })
    df = pd.DataFrame(records) if records else pd.DataFrame(columns=['zone_entry_type_id', 'zone_entry_type_code', 'zone_entry_type_name', 'is_controlled'])
    save_table(df, 'dim_zone_entry_type')
    log.info(f"dim_zone_entry_type: {len(df)} rows")


def _create_dim_zone_exit_type():
    """Create dim_zone_exit_type from dim_event_detail_2."""
    # Controlled exits = maintain possession (Carried, Pass - but not PassMiss)
    # Uncontrolled exits = give up possession (Clear, Chip, Lob, etc.)
    # NOTE: Tracker's "Rush" type = carried exit with speed, NOT NHL "rush"
    
    records = []
    ed2_path = OUTPUT_DIR / 'dim_event_detail_2.csv'
    if ed2_path.exists():
        ed2 = pd.read_csv(ed2_path, low_memory=False)
        zx_codes = ed2[ed2['event_detail_2_code'].astype(str).str.startswith('ZoneExit', na=False)]['event_detail_2_code'].unique()
        codes = sorted(set(str(c) for c in zx_codes))
        for i, code in enumerate(codes, 1):
            exit_type = code.replace('ZoneExit_', '').replace('_', ' ').replace('/', ' ')
            # Rename "Rush" to "Carried" for clarity (tracker's Rush = carried out, not NHL rush)
            exit_type = exit_type.replace('Rush', 'Carried')
            # Controlled = Carried/Rush, Pass (but NOT PassMiss)
            # Handle both old ("Rush") and new ("Carried") terminology
            is_controlled = any(x in code for x in ['_Rush', '_Carried', '_Pass']) and 'Miss' not in code and 'Misplay' not in code
            records.append({
                'zone_exit_type_id': f'ZX{i:04d}',
                'zone_exit_type_code': code,
                'zone_exit_type_name': exit_type,
                'is_controlled': is_controlled,
            })
    df = pd.DataFrame(records) if records else pd.DataFrame(columns=['zone_exit_type_id', 'zone_exit_type_code', 'zone_exit_type_name', 'is_controlled'])
    save_table(df, 'dim_zone_exit_type')
    log.info(f"dim_zone_exit_type: {len(df)} rows")


def _create_dim_stoppage_type():
    """Create dim_stoppage_type from tracking data."""
    records = []
    tracking_path = OUTPUT_DIR / 'fact_event_players.csv'
    if tracking_path.exists():
        tracking = pd.read_csv(tracking_path, low_memory=False)
        if 'event_detail' in tracking.columns:
            stoppage_rows = tracking[tracking['event_type'] == 'Stoppage']
            if len(stoppage_rows) > 0:
                codes = sorted(stoppage_rows['event_detail'].dropna().unique())
                for i, code in enumerate(codes, 1):
                    records.append({
                        'stoppage_type_id': f'SP{i:04d}',
                        'stoppage_type_code': str(code).replace('-', '_'),
                        'stoppage_type_name': str(code).replace('_', ' '),
                    })
    df = pd.DataFrame(records) if records else pd.DataFrame(columns=['stoppage_type_id', 'stoppage_type_code', 'stoppage_type_name'])
    save_table(df, 'dim_stoppage_type')
    log.info(f"dim_stoppage_type: {len(df)} rows")


def _create_dim_giveaway_type():
    """Create dim_giveaway_type from dim_event_detail_2.
    
    Only includes event_detail_2 values containing 'Giveaway'.
    Adds is_bad column: True for misplays/turnovers, False for neutral (dumps, battles, shots).
    
    Neutral giveaways (is_bad=False):
    - Giveaway_AttemptedZoneClear/Dump, Giveaway_DumpInZone, Giveaway_ZoneClear/Dump
    - Giveaway_BattleLost, Giveaway_Other
    - Giveaway_ShotBlocked, Giveaway_ShotMissed
    
    Bad giveaways (is_bad=True):
    - Giveaway_Misplayed, Giveaway_PassBlocked, Giveaway_PassIntercepted
    - Giveaway_PassMissed, Giveaway_PassReceiverMissed, Giveaway_ZoneEntry/ExitMisplay
    """
    # Neutral giveaway types (not penalized as bad turnovers)
    neutral_patterns = [
        'AttemptedZoneClear', 'DumpInZone', 'ZoneClear',
        'BattleLost', 'Other', 'ShotBlocked', 'ShotMissed',
    ]
    
    records = []
    dim_path = OUTPUT_DIR / 'dim_event_detail_2.csv'
    if dim_path.exists():
        dim_ed2 = pd.read_csv(dim_path)
        # Only get event_detail_2 codes containing 'Giveaway'
        giveaway_rows = dim_ed2[dim_ed2['event_detail_2_code'].str.contains('Giveaway', case=False, na=False)]
        giveaway_codes = sorted(giveaway_rows['event_detail_2_code'].tolist())
        for i, code in enumerate(giveaway_codes, 1):
            code_str = str(code)
            # Determine if this is a bad giveaway (not matching any neutral pattern)
            is_bad = not any(pattern in code_str for pattern in neutral_patterns)
            records.append({
                'giveaway_type_id': f'GA{i:04d}',
                'giveaway_type_code': code_str.replace('-', '_'),
                'giveaway_type_name': code_str.replace('_', ' ').replace('/', ' '),
                'is_bad': is_bad,
            })
    df = pd.DataFrame(records) if records else pd.DataFrame(columns=['giveaway_type_id', 'giveaway_type_code', 'giveaway_type_name', 'is_bad'])
    save_table(df, 'dim_giveaway_type')
    log.info(f"dim_giveaway_type: {len(df)} rows ({sum(r['is_bad'] for r in records)} bad, {sum(not r['is_bad'] for r in records)} neutral)")


def _create_dim_takeaway_type():
    """Create dim_takeaway_type from dim_event_detail_2.
    
    Only includes event_detail_2 values containing 'Takeaway'.
    """
    records = []
    dim_path = OUTPUT_DIR / 'dim_event_detail_2.csv'
    if dim_path.exists():
        dim_ed2 = pd.read_csv(dim_path)
        # Only get event_detail_2 codes containing 'Takeaway'
        takeaway_rows = dim_ed2[dim_ed2['event_detail_2_code'].str.contains('Takeaway', case=False, na=False)]
        takeaway_codes = sorted(takeaway_rows['event_detail_2_code'].tolist())
        for i, code in enumerate(takeaway_codes, 1):
            code_str = str(code)
            records.append({
                'takeaway_type_id': f'TA{i:04d}',
                'takeaway_type_code': code_str.replace('-', '_'),
                'takeaway_type_name': code_str.replace('_', ' ').replace('/', ' '),
            })
    df = pd.DataFrame(records) if records else pd.DataFrame(columns=['takeaway_type_id', 'takeaway_type_code', 'takeaway_type_name'])
    save_table(df, 'dim_takeaway_type')
    log.info(f"dim_takeaway_type: {len(df)} rows")


def _standardize_code(code):
    """Standardize code: replace hyphens/slashes with underscores, fix typos."""
    if not code or pd.isna(code):
        return code
    code = str(code).replace('-', '_').replace('/', '_')
    code = code.replace('Seperate', 'Separate')  # Fix common typo
    return code


def _create_dim_play_detail():
    """Create dim_play_detail from PLAY_DETAILS constants and tracking data."""
    from src.models.dimensions import PLAY_DETAILS
    
    # Start with constants
    records = []
    for i, p in enumerate(PLAY_DETAILS, 1):
        records.append({
            'play_detail_id': f'PD{i:04d}',
            'play_detail_code': p['play_detail'],
            'play_detail_name': p['play_detail'],
            'play_category': p.get('play_category', 'other').lower(),
            'skill_level': 'Standard',
            'description': p.get('description', 'Micro-play action')
        })
    
    constant_codes = {p['play_detail'] for p in PLAY_DETAILS}
    
    # Add any additional codes from tracking data
    tracking_path = OUTPUT_DIR / 'fact_event_players.csv'
    if tracking_path.exists():
        tracking = pd.read_csv(tracking_path, low_memory=False)
        
        # Get unique play_detail1 values not in constants
        if 'play_detail1' in tracking.columns:
            tracking_codes = set(tracking['play_detail1'].dropna().unique())
            new_codes = tracking_codes - constant_codes
            
            # Filter out prefixed versions if simple version exists
            filtered_new = set()
            for code in new_codes:
                # Standardize the code first
                std_code = _standardize_code(code)
                if '_' in std_code:
                    base = std_code.split('_')[-1]
                    if base not in constant_codes and base not in filtered_new:
                        filtered_new.add(std_code)
                else:
                    filtered_new.add(std_code)
            
            next_id = len(records) + 1
            for code in sorted(filtered_new):
                # Determine category (lowercase)
                if code.startswith('Offensive'):
                    category = 'offensive'
                elif code.startswith('Defensive'):
                    category = 'defensive'
                elif 'Recovery' in code or 'Retrieval' in code or 'Retreival' in code:
                    category = 'recovery'
                else:
                    category = 'other'
                
                records.append({
                    'play_detail_id': f'PD{next_id:04d}',
                    'play_detail_code': code,
                    'play_detail_name': code,
                    'play_category': category,
                    'skill_level': 'Standard',
                    'description': 'Micro-play action from tracking data'
                })
                next_id += 1
    
    df = pd.DataFrame(records)
    save_table(df, 'dim_play_detail')
    log.info(f"dim_play_detail: {len(df)} rows")


def _create_dim_play_detail_2():
    """Create dim_play_detail_2 from tracking data."""
    records = []
    
    tracking_path = OUTPUT_DIR / 'fact_event_players.csv'
    if tracking_path.exists():
        tracking = pd.read_csv(tracking_path, low_memory=False)
        
        if 'play_detail_2' in tracking.columns:
            # Get unique codes and standardize them
            raw_codes = tracking['play_detail_2'].dropna().unique()
            codes = sorted(set(_standardize_code(c) for c in raw_codes))
            
            for i, code in enumerate(codes, 1):
                # Determine category (lowercase)
                if 'Goal' in code or 'Assist' in code:
                    category = 'scoring'
                elif 'Defensive' in code or 'Block' in code or 'Check' in code:
                    category = 'defensive'
                elif 'Offensive' in code or 'Shot' in code or 'Pass' in code:
                    category = 'offensive'
                else:
                    category = 'other'
                
                records.append({
                    'play_detail_2_id': f'PD2{i:02d}',
                    'play_detail_2_code': code,
                    'play_detail_2_name': code,
                    'play_category': category,
                    'skill_level': 'Standard',
                    'description': 'Secondary play detail from tracking'
                })
    
    if records:
        df = pd.DataFrame(records)
        save_table(df, 'dim_play_detail_2')
        log.info(f"dim_play_detail_2: {len(df)} rows")
    else:
        # Create empty table with schema
        df = pd.DataFrame(columns=['play_detail_2_id', 'play_detail_2_code', 'play_detail_2_name', 
                                   'play_category', 'skill_level', 'description'])
        save_table(df, 'dim_play_detail_2')
        log.info("dim_play_detail_2: 0 rows (no data)")


# ============================================================
# PHASE 6: COMPREHENSIVE VALIDATION
# ============================================================

def validate_all():
    log.section("PHASE 6: COMPREHENSIVE VALIDATION")
    
    all_issues = []
    
    # 1. Check all expected tables exist
    log.info("\n[1] Table existence check:")
    expected_tables = [
        'dim_player', 'dim_team', 'dim_league', 'dim_season', 'dim_schedule',
        'dim_player_role', 'dim_position', 'dim_zone', 'dim_period', 'dim_venue',
        'fact_gameroster', 'fact_events', 'fact_event_players', 'fact_tracking',
        'fact_shifts', 'fact_shift_players', 'fact_shifts',
        'fact_draft', 'fact_registration', 'fact_leadership',
    ]
    
    for table in expected_tables:
        path = OUTPUT_DIR / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            log.info(f"  ✓ {table}: {len(df):,} rows")
        else:
            log.error(f"  ✗ {table}: MISSING")
            all_issues.append(f"Missing table: {table}")
    
    # 2. Check game coverage in tracking tables
    log.info("\n[2] Game coverage (tracking tables):")
    for table in ['fact_events', 'fact_shifts', 'fact_shift_players']:
        path = OUTPUT_DIR / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            games = sorted(df['game_id'].unique().tolist())
            missing = set(VALID_TRACKING_GAMES) - set(games)
            extra = set(games) - set(VALID_TRACKING_GAMES)
            
            if missing:
                log.error(f"  ✗ {table}: missing games {missing}")
                all_issues.append(f"{table}: missing games {missing}")
            elif extra:
                log.warn(f"  ⚠ {table}: unexpected games {extra}")
            else:
                log.info(f"  ✓ {table}: all {len(VALID_TRACKING_GAMES)} games present")
    
    # 3. Primary key integrity
    log.info("\n[3] Primary key integrity:")
    key_checks = [
        ('dim_player', 'player_id'),
        ('dim_team', 'team_id'),
        ('dim_league', 'league_id'),
        ('dim_season', 'season_id'),
        ('dim_schedule', 'game_id'),
        # fact_gameroster uses composite key (game_id, player_id)
        ('fact_events', 'event_id'),
        ('fact_shifts', 'shift_id'),
        ('fact_shift_players', 'shift_player_id'),
    ]
    
    for table, pk in key_checks:
        path = OUTPUT_DIR / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            if pk in df.columns:
                nulls = df[pk].isna().sum()
                dups = df.duplicated(subset=[pk]).sum()
                sample = df[pk].dropna().iloc[0] if len(df) > 0 else ""
                
                if nulls > 0 or dups > 0:
                    log.error(f"  ✗ {table}.{pk}: {nulls} NULL, {dups} dups")
                    all_issues.append(f"{table}.{pk}: {nulls} NULL, {dups} dups")
                else:
                    log.info(f"  ✓ {table}.{pk}: {sample[:40]}")
            else:
                log.error(f"  ✗ {table}: missing column {pk}")
                all_issues.append(f"{table}: missing column {pk}")
    
    # 4. Player ID linkage
    log.info("\n[4] Player ID linkage:")
    player_tables = ['fact_event_players', 'fact_shift_players', 'fact_gameroster']
    
    for table in player_tables:
        path = OUTPUT_DIR / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            if 'player_id' in df.columns:
                linked = df['player_id'].notna().sum()
                total = len(df)
                pct = linked / total * 100 if total > 0 else 0
                
                if pct < 90:
                    log.warn(f"  ⚠ {table}: {linked:,}/{total:,} ({pct:.1f}%) - LOW")
                    log.issue(f"{table} has only {pct:.1f}% player_id linkage")
                else:
                    log.info(f"  ✓ {table}: {linked:,}/{total:,} ({pct:.1f}%)")
            else:
                log.error(f"  ✗ {table}: missing player_id column")
                all_issues.append(f"{table}: missing player_id column")
    
    # 5. No underscore columns
    log.info("\n[5] No underscore columns check:")
    for csv in OUTPUT_DIR.glob("*.csv"):
        df = pd.read_csv(csv, dtype=str, nrows=0)
        underscore_cols = [c for c in df.columns if c.endswith('_')]
        if underscore_cols:
            log.error(f"  ✗ {csv.stem}: has underscore cols {underscore_cols[:3]}")
            all_issues.append(f"{csv.stem}: has underscore columns")
        else:
            log.info(f"  ✓ {csv.stem}: clean")
    
    # 6. Referential integrity
    log.info("\n[6] Referential integrity:")
    
    # Check game_id in events exists in schedule
    schedule = pd.read_csv(OUTPUT_DIR / "dim_schedule.csv", dtype=str)
    schedule_games = set(schedule['game_id'].unique())
    
    events = pd.read_csv(OUTPUT_DIR / "fact_events.csv", dtype=str)
    event_games = set(events['game_id'].unique())
    
    missing_in_schedule = event_games - schedule_games
    if missing_in_schedule:
        log.error(f"  ✗ Events have games not in schedule: {missing_in_schedule}")
        all_issues.append(f"Games in events but not schedule: {missing_in_schedule}")
    else:
        log.info(f"  ✓ All event games exist in schedule")
    
    # Summary
    log.section("VALIDATION SUMMARY")
    
    total_rows = sum(len(pd.read_csv(f, dtype=str)) for f in OUTPUT_DIR.glob("*.csv"))
    table_count = len(list(OUTPUT_DIR.glob("*.csv")))
    
    log.info(f"Tables: {table_count}")
    log.info(f"Total rows: {total_rows:,}")
    log.info(f"Warnings: {len(log.warnings)}")
    log.info(f"Errors: {len(log.errors)}")
    log.info(f"Issues for review: {len(log.issues)}")
    
    if all_issues:
        log.error(f"\nCRITICAL ISSUES ({len(all_issues)}):")
        for issue in all_issues:
            log.error(f"  - {issue}")
        return False
    
    log.info("\n✓ ALL VALIDATIONS PASSED")
    return True

# ============================================================
# MAIN
# ============================================================

def main():
    global VALID_TRACKING_GAMES, EXCLUDED_GAMES
    
    print("="*60)
    print("BENCHSIGHT v6.5.5 - PRODUCTION ETL")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(exist_ok=True)
    
    # Discover games dynamically
    print("\nDiscovering games...")
    VALID_TRACKING_GAMES, EXCLUDED_GAMES = discover_games()
    print(f"  Valid games: {VALID_TRACKING_GAMES}")
    print(f"  Excluded games: {EXCLUDED_GAMES}")
    
    if not VALID_TRACKING_GAMES:
        print("ERROR: No valid games found!")
        return
    
    # Phase 1: Load BLB tables
    loaded = load_blb_tables()
    
    # Phase 2: Build player lookup
    player_lookup = build_player_lookup(loaded['fact_gameroster'])
    
    # Phase 3: Load tracking data (needed for dynamic dims)
    tracking_data = load_tracking_data(player_lookup)
    
    # Phase 4: Create reference tables (uses tracking data for dynamic dims)
    create_reference_tables()
    
    # Phase 5: Create derived tables (uses dim tables for FKs)
    create_derived_tables(tracking_data, player_lookup)
    
    # Phase 5.5: Enhance event tables with derived FKs
    enhance_event_tables()
    
    # Phase 5.6: Enhance derived event tables
    enhance_derived_event_tables()
    
    # Phase 5.9: Enhance events with flags (MOVED EARLIER - before sequences)
    # This adds is_goal, is_sog, is_corsi, is_fenwick, etc. which are needed for sequences/plays
    enhance_events_with_flags()
    
    # Phase 5.7: Create fact_sequences (now has is_goal flag)
    create_fact_sequences()
    
    # Phase 5.8: Create fact_plays (now has is_goal flag)
    create_fact_plays()
    
    # Phase 5.10: Create derived event tables
    create_derived_event_tables()
    
    # Phase 5.11: Enhance shift tables
    enhance_shift_tables()
    
    # Phase 5.11B: Enhance shift players (v19.00)
    enhance_shift_players()
    
    # Phase 5.12: Update roster positions from shifts
    update_roster_positions_from_shifts()
    
    # Phase 6: Validate
    valid = validate_all()
    
    # Save log
    log.save(LOG_FILE)
    
    print("\n" + "="*60)
    if valid:
        print("✓ ETL COMPLETE - ALL VALIDATIONS PASSED")
    else:
        print("✗ ETL COMPLETE - WITH ISSUES (see log)")
    print("="*60)
    
    # Print issues for user
    if log.issues:
        print("\n=== ISSUES FOR USER REVIEW ===")
        for issue in log.issues:
            print(f"  ⚠ {issue}")
    
    return 0 if valid else 1

if __name__ == "__main__":
    exit(main())

# ============================================================
# PHASE 5.5: ENHANCE EVENT TABLES
# ============================================================

def enhance_event_tables():
    """Add derived FK columns to fact_events and fact_event_players."""
    log.section("PHASE 5.5: ENHANCE EVENT TABLES")
    
    # Load required tables (from cache first, then CSV)
    tracking = get_table_from_store('fact_event_players', OUTPUT_DIR) if TABLE_STORE_AVAILABLE else pd.DataFrame()
    if len(tracking) == 0:
        tracking_path = OUTPUT_DIR / 'fact_event_players.csv'
        if tracking_path.exists():
            tracking = pd.read_csv(tracking_path, low_memory=False)
    
    events = get_table_from_store('fact_events', OUTPUT_DIR) if TABLE_STORE_AVAILABLE else pd.DataFrame()
    if len(events) == 0:
        events_path = OUTPUT_DIR / 'fact_events.csv'
        if events_path.exists():
            events = pd.read_csv(events_path, low_memory=False)
    
    if len(tracking) == 0 or len(events) == 0:
        log.warn("Event tables not found, skipping enhancement")
        return
    
    shifts = get_table_from_store('fact_shifts', OUTPUT_DIR) if TABLE_STORE_AVAILABLE else pd.DataFrame()
    if len(shifts) == 0:
        shifts_path = OUTPUT_DIR / 'fact_shifts.csv'
        if shifts_path.exists():
            shifts = pd.read_csv(shifts_path, low_memory=False)
    
    players = get_table_from_store('dim_player', OUTPUT_DIR) if TABLE_STORE_AVAILABLE else pd.DataFrame()
    if len(players) == 0:
        players_path = OUTPUT_DIR / 'dim_player.csv'
        if players_path.exists():
            players = pd.read_csv(players_path, low_memory=False)
    
    schedule = get_table_from_store('dim_schedule', OUTPUT_DIR) if TABLE_STORE_AVAILABLE else pd.DataFrame()
    if len(schedule) == 0:
        schedule_path = OUTPUT_DIR / 'dim_schedule.csv'
        if schedule_path.exists():
            schedule = pd.read_csv(schedule_path, low_memory=False)
    
    roster = get_table_from_store('fact_gameroster', OUTPUT_DIR) if TABLE_STORE_AVAILABLE else pd.DataFrame()
    if len(roster) == 0:
        roster_path = OUTPUT_DIR / 'fact_gameroster.csv'
        if roster_path.exists():
            roster = pd.read_csv(roster_path, low_memory=False)
    
    log.info(f"Enhancing fact_event_players: {len(tracking)} rows, {len(tracking.columns)} cols")
    log.info(f"Enhancing fact_events: {len(events)} rows, {len(events.columns)} cols")
    
    # 0. Add shift_id FK by matching event time to shift time ranges
    log.info("  Adding shift_id FK (matching events to shifts)...")
    
    # CRITICAL: Event times are ASCENDING (0 = period start, counting up to ~1080)
    # Shift times are DESCENDING (1080 = period start, counting down to ~0)
    # Need to convert event time to shift time format: shift_time = period_max - event_time
    
    if 'shift_start_total_seconds' in shifts.columns and 'shift_end_total_seconds' in shifts.columns:
        # Find period max time for each game/period (= period duration in countdown format)
        period_max = {}
        for _, shift in shifts.iterrows():
            key = (int(shift['game_id']), int(shift['period']))
            start = float(shift['shift_start_total_seconds']) if pd.notna(shift['shift_start_total_seconds']) else 0
            if key not in period_max or start > period_max[key]:
                period_max[key] = start
        
        # Build lookup: for each game/period, list of (shift_id, start_countdown, end_countdown)
        shift_ranges = {}
        for _, shift in shifts.iterrows():
            key = (int(shift['game_id']), int(shift['period']))
            if key not in shift_ranges:
                shift_ranges[key] = []
            shift_ranges[key].append((
                shift['shift_id'],
                float(shift['shift_start_total_seconds']) if pd.notna(shift['shift_start_total_seconds']) else 0,
                float(shift['shift_end_total_seconds']) if pd.notna(shift['shift_end_total_seconds']) else 0
            ))
        
        def find_shift_id(row):
            """Find shift_id for an event based on game, period, and time."""
            try:
                game_id = int(row['game_id'])
                period = int(row['period']) if pd.notna(row.get('period')) else 1
                
                # Get event time (elapsed format: 0 = period start)
                event_elapsed = None
                for col in ['time_start_total_seconds', 'event_total_seconds']:
                    if col in row.index and pd.notna(row.get(col)):
                        event_elapsed = float(row[col])
                        break
                
                if event_elapsed is None:
                    return None
                
                key = (game_id, period)
                if key not in shift_ranges or key not in period_max:
                    return None
                
                # Convert event elapsed time to countdown format
                # countdown = period_max - elapsed
                event_countdown = period_max[key] - event_elapsed
                
                # Find shift containing this event time
                # Shift times are countdown: start > end (start is higher number)
                # Event is in shift if: shift_end <= event_countdown <= shift_start
                for shift_id, start, end in shift_ranges[key]:
                    if end <= event_countdown <= start:
                        return shift_id
                
                return None
            except (ValueError, TypeError):
                return None
        
        # Apply to fact_event_players
        tracking['shift_id'] = tracking.apply(find_shift_id, axis=1)
        shift_fill = tracking['shift_id'].notna().sum()
        log.info(f"    fact_event_players.shift_id: {shift_fill}/{len(tracking)} ({100*shift_fill/len(tracking):.1f}%)")
        
        # Apply to fact_events
        events['shift_id'] = events.apply(find_shift_id, axis=1)
        shift_fill_ev = events['shift_id'].notna().sum()
        log.info(f"    fact_events.shift_id: {shift_fill_ev}/{len(events)} ({100*shift_fill_ev/len(events):.1f}%)")
    else:
        log.warn("    Shift time columns not found, skipping shift_id FK")
    
    # Load dimension tables for mapping
    shot_type = pd.read_csv(OUTPUT_DIR / 'dim_shot_type.csv', low_memory=False)
    ze_type = pd.read_csv(OUTPUT_DIR / 'dim_zone_entry_type.csv', low_memory=False)
    zx_type = pd.read_csv(OUTPUT_DIR / 'dim_zone_exit_type.csv', low_memory=False)
    pass_type = pd.read_csv(OUTPUT_DIR / 'dim_pass_type.csv', low_memory=False)
    stoppage_type = pd.read_csv(OUTPUT_DIR / 'dim_stoppage_type.csv', low_memory=False)
    giveaway_type = pd.read_csv(OUTPUT_DIR / 'dim_giveaway_type.csv', low_memory=False)
    takeaway_type = pd.read_csv(OUTPUT_DIR / 'dim_takeaway_type.csv', low_memory=False)
    
    # 1. player_name
    log.info("  Adding player_name...")
    player_map = dict(zip(players['player_id'], players['player_full_name']))
    tracking['player_name'] = tracking['player_id'].map(player_map)
    
    # 2. season_id (from schedule)
    log.info("  Adding season_id...")
    season_map = dict(zip(schedule['game_id'].astype(int), schedule['season_id']))
    tracking['season_id'] = tracking['game_id'].map(season_map)
    
    # 3. position_id (from roster)
    log.info("  Adding position_id...")
    # Map position names to IDs
    pos_map = {'Forward': 4, 'Defense': 5, 'Goalie': 6, 'Center': 1, 'Left Wing': 2, 'Right Wing': 3}
    # VECTORIZED: Create player+game -> position lookup
    roster_valid = roster[roster['player_position'].notna()].copy()
    roster_pos = dict(zip(
        zip(roster_valid['player_id'].astype(str), roster_valid['game_id'].astype(int)),
        roster_valid['player_position'].map(pos_map).fillna(4)  # Default to Forward if unknown
    ))
    
    def get_position(row):
        key = (str(row['player_id']), int(row['game_id']))
        return roster_pos.get(key)
    tracking['position_id'] = tracking.apply(get_position, axis=1)
    
    # 4. shot_type_id - VECTORIZED
    log.info("  Adding shot_type_id...")
    shot_type_copy = shot_type.copy()
    shot_type_copy['code_normalized'] = shot_type_copy['shot_type_code'].str.replace('-', '_')
    shot_type_copy['code_lower'] = shot_type_copy['code_normalized'].str.lower()
    shot_map = dict(zip(shot_type_copy['code_normalized'], shot_type_copy['shot_type_id']))
    shot_map.update(dict(zip(shot_type_copy['code_lower'], shot_type_copy['shot_type_id'])))
    
    def get_shot_type(row):
        if row['event_type'] not in ['Shot', 'Goal']:
            return None
        detail2 = str(row['event_detail_2']) if pd.notna(row['event_detail_2']) else ''
        # Strip prefixes: Shot_, Goal_
        for prefix in ['Shot_', 'Goal_']:
            if detail2.startswith(prefix):
                detail2 = detail2[len(prefix):]
                break
        return shot_map.get(detail2) or shot_map.get(detail2.lower())
    
    tracking['shot_type_id'] = tracking.apply(get_shot_type, axis=1)
    
    # 5. zone_entry_type_id - VECTORIZED
    log.info("  Adding zone_entry_type_id...")
    ze_type_copy = ze_type.copy()
    ze_type_copy['code_normalized'] = ze_type_copy['zone_entry_type_code'].str.replace('-', '_')
    ze_map = dict(zip(ze_type_copy['code_normalized'], ze_type_copy['zone_entry_type_id']))
    # Add aliases for Rush <-> Carried normalization
    rush_mask = ze_type_copy['code_normalized'].str.contains('Rush', na=False)
    carried_mask = ze_type_copy['code_normalized'].str.contains('Carried', na=False)
    if rush_mask.any():
        ze_map.update(dict(zip(
            ze_type_copy.loc[rush_mask, 'code_normalized'].str.replace('Rush', 'Carried'),
            ze_type_copy.loc[rush_mask, 'zone_entry_type_id']
        )))
    if carried_mask.any():
        ze_map.update(dict(zip(
            ze_type_copy.loc[carried_mask, 'code_normalized'].str.replace('Carried', 'Rush'),
            ze_type_copy.loc[carried_mask, 'zone_entry_type_id']
        )))
    
    def get_ze_type(row):
        if row['event_type'] != 'Zone_Entry_Exit':
            return None
        detail2 = str(row['event_detail_2']) if pd.notna(row['event_detail_2']) else ''
        if not detail2.startswith('ZoneEntry'):
            return None
        for key, val in ze_map.items():
            if detail2.startswith(key):
                return val
        return None
    tracking['zone_entry_type_id'] = tracking.apply(get_ze_type, axis=1)
    
    # 6. zone_exit_type_id (NEW) - VECTORIZED
    log.info("  Adding zone_exit_type_id...")
    zx_type_copy = zx_type.copy()
    zx_type_copy['code_normalized'] = zx_type_copy['zone_exit_type_code'].str.replace('-', '_')
    zx_map = dict(zip(zx_type_copy['code_normalized'], zx_type_copy['zone_exit_type_id']))
    # Add aliases for Rush <-> Carried normalization
    rush_mask = zx_type_copy['code_normalized'].str.contains('Rush', na=False)
    carried_mask = zx_type_copy['code_normalized'].str.contains('Carried', na=False)
    if rush_mask.any():
        zx_map.update(dict(zip(
            zx_type_copy.loc[rush_mask, 'code_normalized'].str.replace('Rush', 'Carried'),
            zx_type_copy.loc[rush_mask, 'zone_exit_type_id']
        )))
    if carried_mask.any():
        zx_map.update(dict(zip(
            zx_type_copy.loc[carried_mask, 'code_normalized'].str.replace('Carried', 'Rush'),
            zx_type_copy.loc[carried_mask, 'zone_exit_type_id']
        )))
    
    def get_zx_type(row):
        if row['event_type'] != 'Zone_Entry_Exit':
            return None
        detail2 = str(row['event_detail_2']) if pd.notna(row['event_detail_2']) else ''
        if not detail2.startswith('ZoneExit'):
            return None
        for key, val in zx_map.items():
            if detail2.startswith(key):
                return val
        return None
    tracking['zone_exit_type_id'] = tracking.apply(get_zx_type, axis=1)
    
    # 7. stoppage_type_id - Dynamic lookup from dim_stoppage_type
    log.info("  Adding stoppage_type_id...")
    stoppage_type_path = OUTPUT_DIR / 'dim_stoppage_type.csv'
    if stoppage_type_path.exists():
        stoppage_dim = pd.read_csv(stoppage_type_path)
        # Build mapping from code to ID
        stoppage_map = dict(zip(stoppage_dim['stoppage_type_code'], stoppage_dim['stoppage_type_id']))
    else:
        stoppage_map = {}
        log.warn("  dim_stoppage_type.csv not found - stoppage_type_id will be None")
    
    tracking['stoppage_type_id'] = tracking.apply(
        lambda r: stoppage_map.get(r['event_detail']) if r['event_type'] == 'Stoppage' else None, axis=1
    )
    
    # 8. giveaway_type_id (NEW) 
    log.info("  Adding giveaway_type_id...")
    # Dynamic lookup from dim_giveaway_type - match event_detail_2 to giveaway_type_code
    giveaway_type_path = OUTPUT_DIR / 'dim_giveaway_type.csv'
    if giveaway_type_path.exists():
        giveaway_dim = pd.read_csv(giveaway_type_path)
        # VECTORIZED: Build mapping from code to ID (handles variations like / vs _)
        giveaway_map = dict(zip(giveaway_dim['giveaway_type_code'], giveaway_dim['giveaway_type_id']))
        # Also map variations (replace / with _)
        giveaway_map.update(dict(zip(
            giveaway_dim['giveaway_type_code'].str.replace('/', '_'),
            giveaway_dim['giveaway_type_id']
        )))
    else:
        giveaway_map = {}
        log.warn("  dim_giveaway_type.csv not found - giveaway_type_id will be None")
    
    def get_giveaway_type(row):
        if row['event_type'] != 'Turnover':
            return None
        detail = str(row['event_detail']) if pd.notna(row['event_detail']) else ''
        if 'Giveaway' not in detail:
            return None
        # Use event_detail_2 to determine giveaway type
        detail2 = str(row['event_detail_2']) if pd.notna(row.get('event_detail_2')) else ''
        if detail2 in giveaway_map:
            return giveaway_map[detail2]
        # Try variations
        detail2_alt = detail2.replace('/', '_')
        if detail2_alt in giveaway_map:
            return giveaway_map[detail2_alt]
        return None
    tracking['giveaway_type_id'] = tracking.apply(get_giveaway_type, axis=1)
    
    # 9. takeaway_type_id - Dynamic lookup from dim_takeaway_type
    log.info("  Adding takeaway_type_id...")
    takeaway_type_path = OUTPUT_DIR / 'dim_takeaway_type.csv'
    if takeaway_type_path.exists():
        takeaway_dim = pd.read_csv(takeaway_type_path)
        # VECTORIZED: Build takeaway map
        takeaway_map = dict(zip(takeaway_dim['takeaway_type_code'], takeaway_dim['takeaway_type_id']))
        takeaway_map.update(dict(zip(
            takeaway_dim['takeaway_type_code'].str.replace('/', '_'),
            takeaway_dim['takeaway_type_id']
        )))
    else:
        takeaway_map = {}
        log.warn("  dim_takeaway_type.csv not found - takeaway_type_id will be None")
    
    def get_takeaway_type(row):
        if row['event_type'] != 'Turnover':
            return None
        detail = str(row['event_detail']) if pd.notna(row['event_detail']) else ''
        if 'Takeaway' not in detail:
            return None
        # Use event_detail_2 to determine takeaway type
        detail2 = str(row['event_detail_2']) if pd.notna(row.get('event_detail_2')) else ''
        if detail2 in takeaway_map:
            return takeaway_map[detail2]
        detail2_alt = detail2.replace('/', '_')
        if detail2_alt in takeaway_map:
            return takeaway_map[detail2_alt]
        return None
    tracking['takeaway_type_id'] = tracking.apply(get_takeaway_type, axis=1)
    
    # 10. turnover_type_id - NOTE: dim_turnover_type is created later in static dimensions
    # giveaway_type_id and takeaway_type_id provide more specific categorization
    log.info("  Adding turnover_type_id (placeholder - linked in post-ETL)...")
    tracking['turnover_type_id'] = None  # Will be populated if needed in post-ETL
    
    # 11. pass_type_id - VECTORIZED
    log.info("  Adding pass_type_id...")
    pass_map = dict(zip(pass_type['pass_type_code'], pass_type['pass_type_id']))
    pass_map.update(dict(zip(
        pass_type['pass_type_code'].str.lower(),
        pass_type['pass_type_id']
    )))
    
    def get_pass_type(row):
        if row['event_type'] != 'Pass':
            return None
        detail2 = str(row['event_detail_2']) if pd.notna(row['event_detail_2']) else ''
        # Strip Pass_ prefix
        if detail2.startswith('Pass_'):
            detail2 = detail2[5:]
        return pass_map.get(detail2) or pass_map.get(detail2.lower())
    
    tracking['pass_type_id'] = tracking.apply(get_pass_type, axis=1)
    
    # 12. time_bucket_id
    log.info("  Adding time_bucket_id...")
    def get_time_bucket(row):
        period = row['period']
        start_min = row.get('event_start_min')
        if pd.isna(start_min):
            return None
        if period > 3:
            return 'TB06'
        if start_min >= 15:
            return 'TB01'
        elif start_min >= 10:
            return 'TB02'
        elif start_min >= 5:
            return 'TB03'
        elif start_min >= 2:
            return 'TB04'
        else:
            return 'TB05'
    tracking['time_bucket_id'] = tracking.apply(get_time_bucket, axis=1)
    
    # 13. strength_id (from shift data)
    log.info("  Adding strength_id...")
    def count_skaters(row, prefix):
        count = 0
        for pos in ['forward_1', 'forward_2', 'forward_3', 'defense_1', 'defense_2']:
            col = f'{prefix}_{pos}'
            if col in row.index and pd.notna(row[col]):
                count += 1
        return count
    
    shift_strength = {}
    for _, row in shifts.iterrows():
        game_id = row['game_id']
        shift_idx = row['shift_index']
        home_sk = count_skaters(row, 'home')
        away_sk = count_skaters(row, 'away')
        
        strength_map = {
            (5,5): 'STR0001', (5,4): 'STR0002', (5,3): 'STR0003',
            (4,5): 'STR0004', (3,5): 'STR0005', (4,4): 'STR0006',
            (3,3): 'STR0007', (4,3): 'STR0008', (3,4): 'STR0009',
        }
        shift_strength[(game_id, shift_idx)] = strength_map.get((home_sk, away_sk), 'STR0001')
    
    def get_strength(row):
        shift_key = row.get('shift_key')
        if pd.isna(shift_key):
            return None
        parts = parse_shift_key(shift_key)
        if parts is None:
            return None
        return shift_strength.get((parts.game_id, parts.shift_index), 'STR0001')
    tracking['strength_id'] = tracking.apply(get_strength, axis=1)
    
    # Fallback: Map from strength column if strength_id is still null
    if 'strength' in tracking.columns:
        strength_direct_map = {
            '5v5': 'STR01', '5v4': 'STR02', '4v5': 'STR03', '5v3': 'STR04',
            '3v5': 'STR05', '4v4': 'STR06', '3v3': 'STR07', '4v3': 'STR08',
            '3v4': 'STR09', '6v5': 'STR10', '5v6': 'STR11', '6v4': 'STR12',
            '4v6': 'STR13', '6v3': 'STR14', '3v6': 'STR15'
        }
        strength_from_col = tracking['strength'].map(strength_direct_map)
        tracking['strength_id'] = tracking['strength_id'].fillna(strength_from_col)
    
    # 15. player_rating (from dim_player)
    log.info("  Adding player_rating...")
    player_rating_map = dict(zip(players['player_id'], players['current_skill_rating']))
    tracking['player_rating'] = tracking['player_id'].map(player_rating_map)
    
    # 14. Drop unwanted columns
    log.info("  Dropping: role_number, role_abrev, team_venue_abv...")
    for col in ['role_number', 'role_abrev', 'team_venue_abv']:
        if col in tracking.columns:
            tracking = tracking.drop(columns=[col])
    
    # Save enhanced tracking
    save_output_table(tracking, 'fact_event_players')
    log.info(f"  ✓ fact_event_players: {len(tracking)} rows, {len(tracking.columns)} cols")
    
    # Now enhance fact_events (get first row per event from tracking)
    log.info("  Enhancing fact_events from tracking...")
    new_cols = ['player_name', 'season_id', 'position_id', 'shot_type_id', 'zone_entry_type_id', 
                'zone_exit_type_id', 'stoppage_type_id', 'giveaway_type_id', 'takeaway_type_id',
                'turnover_type_id', 'pass_type_id', 'time_bucket_id', 'strength_id',
                'player_rating']
    
    tracking_first = tracking.groupby('event_id').first().reset_index()
    for col in new_cols:
        if col in tracking_first.columns:
            col_map = dict(zip(tracking_first['event_id'], tracking_first[col]))
            # Only overwrite if column doesn't exist or new value is not null
            if col not in events.columns:
                events[col] = events['event_id'].map(col_map)
            else:
                # Keep existing non-null values, fill nulls from tracking
                new_vals = events['event_id'].map(col_map)
                events[col] = events[col].fillna(new_vals)
    
    save_output_table(events, 'fact_events')
    log.info(f"  ✓ fact_events: {len(events)} rows, {len(events.columns)} cols")
    
    # Log fill rates
    log.info("  Fill rates:")
    for col in new_cols:
        if col in tracking.columns:
            fill = tracking[col].notna().sum()
            log.info(f"    {col}: {fill}/{len(tracking)} ({100*fill/len(tracking):.1f}%)")


def _build_cycle_events(tracking, events, output_dir, log):
    """
    Build fact_cycle_events using zone inference.
    
    A cycle is defined as:
    - 3+ consecutive passes by the same team in offensive zone
    - Includes Pass and Possession events
    - Ends with: Shot, Goal, Turnover, Zone exit, or possession change
    """
    teams = pd.read_csv(output_dir / 'dim_team.csv')
    team_name_to_id = dict(zip(teams['team_name'], teams['team_id']))
    
    # Get primary player rows only for detection
    primary = tracking[tracking['player_role'] == 'event_player_1'].copy()
    primary = primary.sort_values(['game_id', 'event_running_start', 'event_id']).reset_index(drop=True)
    
    all_cycles = []
    cycle_counter = 0
    
    cycle_events_types = ['Pass', 'Possession']
    cycle_enders = ['Shot', 'Goal', 'Turnover', 'Zone_Entry_Exit', 'Faceoff', 'Stoppage', 'Save']
    
    for game_id in primary['game_id'].unique():
        game_df = primary[primary['game_id'] == game_id].copy().sort_values('event_running_start').reset_index(drop=True)
        
        # Infer zones from Zone_Entry/Exit events
        team_zones = {}
        inferred_zones = []
        
        for i, row in game_df.iterrows():
            team = row['player_team']
            event_type = row['event_type']
            detail = row['event_detail']
            explicit_zone = row['event_team_zone']
            
            if pd.notna(explicit_zone) and str(explicit_zone).strip() in ['o', 'd', 'n']:
                team_zones[team] = str(explicit_zone).strip()
                inferred_zones.append(str(explicit_zone).strip())
            elif event_type == 'Zone_Entry_Exit':
                if detail in ['Zone_Entry', 'Zone_Keepin']:
                    team_zones[team] = 'o'
                    inferred_zones.append('o')
                elif detail in ['Zone_Exit']:
                    team_zones[team] = 'n'
                    inferred_zones.append('n')
                else:
                    inferred_zones.append(team_zones.get(team, 'n'))
            else:
                inferred_zones.append(team_zones.get(team, 'n'))
        
        game_df['inferred_zone'] = inferred_zones
        
        # Detect cycles
        current_cycle_events = []
        current_cycle_passes = 0
        current_team = None
        
        first_row = game_df.iloc[0] if len(game_df) > 0 else None
        
        for i, row in game_df.iterrows():
            event_type = row['event_type']
            team = row['player_team']
            zone = row['inferred_zone']
            detail = row['event_detail']
            
            if zone != 'o':
                if len(current_cycle_events) > 0 and current_cycle_passes >= 3:
                    cycle_counter += 1
                    all_cycles.append(_make_cycle_record(
                        cycle_counter, game_id, current_team, current_cycle_events,
                        current_cycle_passes, 'zone_change', team_name_to_id, first_row
                    ))
                current_cycle_events = []
                current_cycle_passes = 0
                current_team = None
                continue
            
            if event_type in cycle_events_types:
                if current_team is None or current_team == team:
                    current_cycle_events.append(row)
                    if event_type == 'Pass':
                        current_cycle_passes += 1
                    current_team = team
                else:
                    if current_cycle_passes >= 3:
                        cycle_counter += 1
                        all_cycles.append(_make_cycle_record(
                            cycle_counter, game_id, current_team, current_cycle_events,
                            current_cycle_passes, 'possession_change', team_name_to_id, first_row
                        ))
                    current_cycle_events = [row]
                    current_cycle_passes = 1 if event_type == 'Pass' else 0
                    current_team = team
                    
            elif event_type in cycle_enders:
                if current_team == team and event_type in ['Shot', 'Goal']:
                    current_cycle_events.append(row)
                
                if current_cycle_passes >= 3:
                    cycle_counter += 1
                    end_type = event_type.lower()
                    if event_type == 'Turnover':
                        end_type = 'turnover'
                    all_cycles.append(_make_cycle_record(
                        cycle_counter, game_id, current_team, current_cycle_events,
                        current_cycle_passes, end_type, team_name_to_id, first_row
                    ))
                
                current_cycle_events = []
                current_cycle_passes = 0
                current_team = None
    
    cycles_df = pd.DataFrame(all_cycles)
    
    if len(cycles_df) > 0:
        # Add period from events
        event_periods = dict(zip(events['event_id'], events['period']))
        cycles_df['period'] = cycles_df['start_event_id'].map(event_periods)
        cycles_df['period_id'] = cycles_df['period'].apply(lambda x: f'P{int(x):02d}' if pd.notna(x) else None)
        
        # Remove columns that are 100% null
        cycles_df, removed_cols = drop_all_null_columns(cycles_df)
        if removed_cols:
            log.info(f"  Removed {len(removed_cols)} all-null columns from fact_cycle_events: {removed_cols[:10]}{'...' if len(removed_cols) > 10 else ''}")
        
        # Save fact_cycle_events
        save_output_table(cycles_df, 'fact_cycle_events', output_dir)
        log.info(f"  ✓ fact_cycle_events: {len(cycles_df)} rows, {len(cycles_df.columns)} columns")
        
        # Build event_id -> cycle_key mapping
        event_to_cycle = {}
        for _, row in cycles_df.iterrows():
            cycle_key = row['cycle_key']
            event_ids = str(row['event_ids']).split(',')
            for eid in event_ids:
                event_to_cycle[eid.strip()] = cycle_key
        
        # Update tracking with cycle_key
        tracking['cycle_key'] = tracking['event_id'].map(event_to_cycle)
        tracking['is_cycle'] = tracking['cycle_key'].notna().astype(int)
        save_output_table(tracking, 'fact_event_players', output_dir)
        
        # Update events with cycle_key
        events['cycle_key'] = events['event_id'].map(event_to_cycle)
        events['is_cycle'] = events['cycle_key'].notna().astype(int)
        save_output_table(events, 'fact_events', output_dir)
        
        log.info(f"  ✓ Updated is_cycle flag: {tracking['is_cycle'].sum()} tracking rows, {events['is_cycle'].sum()} event rows")
    else:
        log.warn("  No cycles detected")


def _make_cycle_record(cycle_num, game_id, team_name, events_list, pass_count, end_type, team_map, first_row):
    """Build a cycle record dictionary."""
    event_ids = [e['event_id'] for e in events_list]
    player_ids = list(set([e['player_id'] for e in events_list if pd.notna(e.get('player_id'))]))
    
    return {
        'cycle_key': f'CY{game_id}{cycle_num:04d}',
        'game_id': game_id,
        'season_id': first_row.get('season_id') if first_row is not None else None,
        'team_id': team_map.get(team_name),
        'team_name': team_name,
        'home_team_id': first_row.get('home_team_id') if first_row is not None else None,
        'away_team_id': first_row.get('away_team_id') if first_row is not None else None,
        'pass_count': pass_count,
        'event_count': len(events_list),
        'player_count': len(player_ids),
        'start_event_id': events_list[0]['event_id'],
        'end_event_id': events_list[-1]['event_id'],
        'start_time': events_list[0]['event_running_start'],
        'end_time': events_list[-1]['event_running_start'],
        'duration_seconds': events_list[-1]['event_running_start'] - events_list[0]['event_running_start'],
        'ended_with': end_type,
        'ended_with_shot': 1 if end_type in ['shot', 'goal'] else 0,
        'ended_with_goal': 1 if end_type == 'goal' else 0,
        'event_ids': ','.join(event_ids),
        'player_ids': ','.join([str(p) for p in player_ids])
    }



def enhance_derived_event_tables():
    """Add FKs to tables derived from events (chains, tracking, linked, etc.)."""
    log.section("PHASE 5.6: ENHANCE DERIVED EVENT TABLES")
    
    # Load fact_events with new FKs for lookup
    events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv', low_memory=False)
    tracking = pd.read_csv(OUTPUT_DIR / 'fact_event_players.csv', low_memory=False)
    
    # Create lookup maps from events
    event_fks = ['season_id', 'time_bucket_id', 'strength_id', 'shot_type_id', 
                 'zone_entry_type_id', 'zone_exit_type_id', 'position_id']
    
    event_lookup = {}
    for col in event_fks:
        if col in events.columns:
            event_lookup[col] = dict(zip(events['event_id'], events[col]))
    
    # Also create lookup by tracking_event_key
    tracking_lookup = {}
    tracking_first = tracking.groupby('tracking_event_key').first().reset_index()
    for col in event_fks:
        if col in tracking_first.columns:
            tracking_lookup[col] = dict(zip(tracking_first['tracking_event_key'], tracking_first[col]))
    
    # 1. Enhance fact_player_event_chains
    log.info("Enhancing fact_player_event_chains...")
    pec_path = OUTPUT_DIR / 'fact_player_event_chains.csv'
    if pec_path.exists():
        pec = pd.read_csv(pec_path, low_memory=False)
        
        # Skip if empty or missing event_key
        if len(pec) > 0 and 'event_key' in pec.columns:
            # Add FKs via event_key
            for col in ['season_id', 'time_bucket_id', 'strength_id']:
                if col in event_lookup:
                    pec[col] = pec['event_key'].map(event_lookup[col])
            
            save_output_table(pec, 'fact_player_event_chains')
            log.info(f"  ✓ fact_player_event_chains: {len(pec)} rows, {len(pec.columns)} cols")
        else:
            log.info(f"  - fact_player_event_chains: skipped (empty or no event_key)")
    
    # 2. Enhance fact_tracking
    log.info("Enhancing fact_tracking...")
    ft_path = OUTPUT_DIR / 'fact_tracking.csv'
    if ft_path.exists():
        ft = pd.read_csv(ft_path, low_memory=False)
        
        # Add FKs via tracking_event_key
        for col in ['season_id', 'time_bucket_id', 'strength_id']:
            if col in tracking_lookup:
                ft[col] = ft['tracking_event_key'].map(tracking_lookup[col])
        
        save_output_table(ft, 'fact_tracking')
        log.info(f"  ✓ fact_tracking: {len(ft)} rows, {len(ft.columns)} cols")
    
    # NOTE: fact_shot_chains, fact_linked_events, fact_scoring_chances, fact_rush_events
    # are created later in Phase 4D/4E by event_analytics.py and shot_chain_builder.py
    # No enhancement needed here.
    
    # 3. Build fact_cycle_events with zone inference
    log.info("Building fact_cycle_events with zone inference...")
    _build_cycle_events(tracking, events, OUTPUT_DIR, log)
    
    log.info("  Done enhancing derived tables")



def create_fact_sequences():
    """Create fact_sequences aggregating events by sequence_key."""
    log.section("PHASE 5.7: CREATE FACT_SEQUENCES")
    
    events_path = OUTPUT_DIR / 'fact_events.csv'
    tracking_path = OUTPUT_DIR / 'fact_event_players.csv'
    
    if not events_path.exists():
        log.warn("fact_events not found, skipping fact_sequences")
        return
    
    events = pd.read_csv(events_path, low_memory=False)
    tracking = pd.read_csv(tracking_path, low_memory=False)
    
    log.info(f"Aggregating {len(events)} events into sequences...")
    
    events = events.sort_values(['sequence_key', 'event_id'])
    sequences = []
    
    for seq_key, grp in events.groupby('sequence_key'):
        if pd.isna(seq_key):
            continue
            
        grp = grp.sort_values('event_id')
        first = grp.iloc[0]
        last = grp.iloc[-1]
        
        # Count event types
        event_types = grp['event_type'].value_counts().to_dict()
        
        # Check for goals - use is_goal flag (only Goal + Goal_Scored)
        has_goal = grp['is_goal'].sum() > 0 if 'is_goal' in grp.columns else False
        goal_count = grp['is_goal'].sum() if 'is_goal' in grp.columns else 0
        
        # Shots - count Shot events only, not Goal events
        # Goal events are the goal record, Shot_Goal is the shot that scored
        shot_count = event_types.get('Shot', 0)
        
        # Zone entries/exits
        zone_entries = grp['zone_entry_type_id'].notna().sum()
        zone_exits = grp['zone_exit_type_id'].notna().sum()
        
        # Passes
        pass_count = event_types.get('Pass', 0)
        pass_success = grp[(grp['event_type'] == 'Pass') & (grp['event_successful'] == 's')].shape[0]
        
        # Turnovers
        turnover_count = event_types.get('Turnover', 0)
        giveaway_count = grp['giveaway_type_id'].notna().sum()
        takeaway_count = grp['takeaway_type_id'].notna().sum()
        
        # Players
        all_players = set()
        for pids in grp['event_player_ids'].dropna():
            all_players.update(str(pids).split(','))
        all_players.discard('')
        
        seq = {
            'sequence_key': seq_key,
            'sequence_id': seq_key,
            'game_id': int(first['game_id']),
            'season_id': first['season_id'],
            'period': int(first['period']),
            'period_id': first['period_id'],
            'first_event_key': first['event_id'],
            'last_event_key': last['event_id'],
            'event_count': len(grp),
            'duration_seconds': grp['duration'].sum(),
            'time_bucket_id': first['time_bucket_id'],
            'strength_id': first['strength_id'],
            'home_team': first['home_team'],
            'home_team_id': first['home_team_id'],
            'away_team': first['away_team'],
            'away_team_id': first['away_team_id'],
            'start_zone': first['event_team_zone'],
            'end_zone': last['event_team_zone'],
            'start_zone_id': first['event_zone_id'],
            'end_zone_id': last['event_zone_id'],
            'event_types': ','.join(grp['event_type'].dropna().astype(str).tolist()),
            'has_goal': has_goal,
            'goal_count': goal_count,
            'shot_count': shot_count,
            'zone_entry_count': zone_entries,
            'zone_exit_count': zone_exits,
            'pass_count': pass_count,
            'pass_success_count': pass_success,
            'pass_success_rate': pass_success / pass_count if pass_count > 0 else None,
            'turnover_count': turnover_count,
            'giveaway_count': giveaway_count,
            'takeaway_count': takeaway_count,
            'unique_player_count': len(all_players),
            'player_ids': ','.join(sorted(all_players)) if all_players else None,
        }
        sequences.append(seq)
    
    seq_df = pd.DataFrame(sequences)
    seq_df = seq_df.sort_values(['game_id', 'period', 'first_event_key'])
    
    # Add video times from tracking
    tracking_first = tracking.groupby('event_id').first().reset_index()
    video_map = dict(zip(tracking_first['event_id'], tracking_first['running_video_time']))
    video_end_map = dict(zip(tracking_first['event_id'], tracking_first['event_running_end']))
    start_min_map = dict(zip(tracking_first['event_id'], tracking_first['event_start_min']))
    start_sec_map = dict(zip(tracking_first['event_id'], tracking_first['event_start_sec']))
    
    seq_df['video_time_start'] = seq_df['first_event_key'].map(video_map)
    seq_df['video_time_end'] = seq_df['last_event_key'].map(video_end_map)
    seq_df['start_min'] = seq_df['first_event_key'].map(start_min_map)
    seq_df['start_sec'] = seq_df['first_event_key'].map(start_sec_map)
    
    # Reorder columns
    col_order = [
        'sequence_key', 'sequence_id', 'game_id', 'season_id', 'period', 'period_id',
        'first_event_key', 'last_event_key', 'event_count',
        'start_min', 'start_sec', 'duration_seconds', 'video_time_start', 'video_time_end',
        'time_bucket_id', 'strength_id',
        'home_team', 'home_team_id', 'away_team', 'away_team_id',
        'start_zone', 'end_zone', 'start_zone_id', 'end_zone_id',
        'event_types', 'has_goal', 'goal_count', 'shot_count',
        'zone_entry_count', 'zone_exit_count',
        'pass_count', 'pass_success_count', 'pass_success_rate',
        'turnover_count', 'giveaway_count', 'takeaway_count',
        'unique_player_count', 'player_ids'
    ]
    seq_df = seq_df[[c for c in col_order if c in seq_df.columns]]
    
    save_table(seq_df, 'fact_sequences')
    log.info(f"  ✓ fact_sequences: {len(seq_df)} rows, {len(seq_df.columns)} cols")
    log.info(f"    Goals: {seq_df['has_goal'].sum()}, Avg events/seq: {seq_df['event_count'].mean():.1f}")



def create_fact_plays():
    """Create fact_plays aggregating events by play_key."""
    log.section("PHASE 5.8: CREATE FACT_PLAYS")
    
    events_path = OUTPUT_DIR / 'fact_events.csv'
    tracking_path = OUTPUT_DIR / 'fact_event_players.csv'
    
    if not events_path.exists():
        log.warn("fact_events not found, skipping fact_plays")
        return
    
    events = pd.read_csv(events_path, low_memory=False)
    tracking = pd.read_csv(tracking_path, low_memory=False)
    
    log.info(f"Aggregating {len(events)} events into plays...")
    
    events = events.sort_values(['play_key', 'event_id'])
    plays = []
    
    for play_key, grp in events.groupby('play_key'):
        if pd.isna(play_key):
            continue
            
        grp = grp.sort_values('event_id')
        first = grp.iloc[0]
        last = grp.iloc[-1]
        
        event_types = grp['event_type'].value_counts().to_dict()
        # Use is_goal flag (only Goal + Goal_Scored)
        has_goal = grp['is_goal'].sum() > 0 if 'is_goal' in grp.columns else False
        goal_count = grp['is_goal'].sum() if 'is_goal' in grp.columns else 0
        has_shot = ('Shot' in event_types) or has_goal
        shot_count = event_types.get('Shot', 0)  # Don't add Goal events - they're goals, not shots
        zone_entries = grp['zone_entry_type_id'].notna().sum()
        zone_exits = grp['zone_exit_type_id'].notna().sum()
        pass_count = event_types.get('Pass', 0)
        pass_success = grp[(grp['event_type'] == 'Pass') & (grp['event_successful'] == 's')].shape[0]
        turnover_count = event_types.get('Turnover', 0)
        giveaway_count = grp['giveaway_type_id'].notna().sum()
        takeaway_count = grp['takeaway_type_id'].notna().sum()
        
        all_players = set()
        for pids in grp['event_player_ids'].dropna():
            all_players.update(str(pids).split(','))
        all_players.discard('')
        
        play = {
            'play_key': play_key, 'play_id': play_key,
            'game_id': int(first['game_id']), 'season_id': first['season_id'],
            'period': int(first['period']), 'period_id': first['period_id'],
            'sequence_key': first['sequence_key'],
            'first_event_key': first['event_id'], 'last_event_key': last['event_id'],
            'event_count': len(grp), 'duration_seconds': grp['duration'].sum(),
            'time_bucket_id': first['time_bucket_id'], 'strength_id': first['strength_id'],
            'home_team': first['home_team'], 'home_team_id': first['home_team_id'],
            'away_team': first['away_team'], 'away_team_id': first['away_team_id'],
            'start_zone': first['event_team_zone'], 'end_zone': last['event_team_zone'],
            'start_zone_id': first['event_zone_id'], 'end_zone_id': last['event_zone_id'],
            'event_types': ','.join(grp['event_type'].dropna().astype(str).tolist()),
            'has_goal': has_goal, 'goal_count': goal_count, 'has_shot': has_shot, 'shot_count': shot_count,
            'zone_entry_count': zone_entries, 'zone_exit_count': zone_exits,
            'pass_count': pass_count, 'pass_success_count': pass_success,
            'turnover_count': turnover_count, 'giveaway_count': giveaway_count,
            'takeaway_count': takeaway_count,
            'unique_player_count': len(all_players),
            'player_ids': ','.join(sorted(all_players)) if all_players else None,
        }
        plays.append(play)
    
    plays_df = pd.DataFrame(plays)
    plays_df = plays_df.sort_values(['game_id', 'period', 'first_event_key'])
    
    # Add video times from tracking
    tracking_first = tracking.groupby('event_id').first().reset_index()
    video_map = dict(zip(tracking_first['event_id'], tracking_first['running_video_time']))
    video_end_map = dict(zip(tracking_first['event_id'], tracking_first['event_running_end']))
    start_min_map = dict(zip(tracking_first['event_id'], tracking_first['event_start_min']))
    start_sec_map = dict(zip(tracking_first['event_id'], tracking_first['event_start_sec']))
    
    plays_df['video_time_start'] = plays_df['first_event_key'].map(video_map)
    plays_df['video_time_end'] = plays_df['last_event_key'].map(video_end_map)
    plays_df['start_min'] = plays_df['first_event_key'].map(start_min_map)
    plays_df['start_sec'] = plays_df['first_event_key'].map(start_sec_map)
    
    col_order = [
        'play_key', 'play_id', 'game_id', 'season_id', 'period', 'period_id', 'sequence_key',
        'first_event_key', 'last_event_key', 'event_count',
        'start_min', 'start_sec', 'duration_seconds', 'video_time_start', 'video_time_end',
        'time_bucket_id', 'strength_id',
        'home_team', 'home_team_id', 'away_team', 'away_team_id',
        'start_zone', 'end_zone', 'start_zone_id', 'end_zone_id',
        'event_types', 'has_goal', 'goal_count', 'has_shot', 'shot_count',
        'zone_entry_count', 'zone_exit_count',
        'pass_count', 'pass_success_count',
        'turnover_count', 'giveaway_count', 'takeaway_count',
        'unique_player_count', 'player_ids'
    ]
    plays_df = plays_df[[c for c in col_order if c in plays_df.columns]]
    
    save_table(plays_df, 'fact_plays')
    log.info(f"  ✓ fact_plays: {len(plays_df)} rows, {len(plays_df.columns)} cols")
    log.info(f"    Goals: {plays_df['has_goal'].sum()}, Shots: {plays_df['has_shot'].sum()}, Avg events/play: {plays_df['event_count'].mean():.1f}")



def enhance_events_with_flags():
    """Add time columns, flags, and derived keys to fact_events."""
    log.section("PHASE 5.9: ENHANCE EVENTS WITH FLAGS")
    
    events_path = OUTPUT_DIR / 'fact_events.csv'
    tracking_path = OUTPUT_DIR / 'fact_event_players.csv'
    
    if not events_path.exists():
        log.warn("fact_events not found, skipping enhancement")
        return
    
    events = pd.read_csv(events_path, low_memory=False)
    tracking = pd.read_csv(tracking_path, low_memory=False)
    
    # Get first row per event for time/context
    first_per_event = tracking[tracking['player_role'] == 'event_player_1'].copy()
    first_per_event = first_per_event.drop_duplicates(subset='event_id', keep='first')
    
    log.info(f"Enhancing {len(events)} events...")
    
    # Add time columns
    time_cols = ['event_start_min', 'event_start_sec', 'event_end_min', 'event_end_sec',
                 'running_video_time', 'event_running_start', 'event_running_end']
    for col in time_cols:
        if col in first_per_event.columns and col not in events.columns:
            events[col] = events['event_id'].map(dict(zip(first_per_event['event_id'], first_per_event[col])))
    
    # Add play_detail1
    if 'play_detail1' in first_per_event.columns:
        events['play_detail1'] = events['event_id'].map(dict(zip(first_per_event['event_id'], first_per_event['play_detail1'])))
    
    # Create flags
    events['is_rebound'] = (events['event_type'] == 'Rebound').astype(int)
    # is_cycle is set by _build_cycle_events based on cycle_key - preserve if already set
    if 'cycle_key' in events.columns:
        events['is_cycle'] = events['cycle_key'].notna().astype(int)
    else:
        events['is_cycle'] = (events['event_detail'].str.contains('Cycle', na=False) | events['event_detail_2'].str.contains('Cycle', na=False)).astype(int)
    # Breakout = successful zone exit (exiting defensive zone with puck control)
    # Using event_detail='Zone_Exit' as primary indicator - covers all games consistently
    # NOTE: Some games also have play_detail1 'Breakout' annotations, but this is inconsistent
    # Legacy logic (inconsistent across games): events['event_detail'].str.contains('Breakout', na=False) | events['play_detail1'].str.contains('Breakout', na=False, case=False)
    # Zone entry = successful zone entries only (exclude Zone_Entryfailed)
    events['is_zone_entry'] = (events['event_detail'] == 'Zone_Entry').astype(int)
    # Zone exit = successful zone exits only (exclude Zone_ExitFailed)
    events['is_zone_exit'] = (events['event_detail'] == 'Zone_Exit').astype(int)
    
    # is_controlled_entry: Zone entry with puck control (not dump-in)
    # Dynamically lookup from dim_zone_entry_type - NO HARDCODED IDs
    ze_type_path = OUTPUT_DIR / 'dim_zone_entry_type.csv'
    if not ze_type_path.exists():
        raise FileNotFoundError(f"dim_zone_entry_type.csv not found - must run dim table creation first")
    
    ze_types = pd.read_csv(ze_type_path)
    controlled_entry_ids = ze_types[ze_types['is_controlled'] == True]['zone_entry_type_id'].tolist()
    carried_entry_ids = ze_types[ze_types['zone_entry_type_name'].str.contains('Carried', na=False)]['zone_entry_type_id'].tolist()
    
    events['is_controlled_entry'] = (
        (events['is_zone_entry'] == 1) & 
        (events['zone_entry_type_id'].isin(controlled_entry_ids))
    ).astype(int)
    
    # is_carried_entry: Carried in (subset of controlled, excludes pass-in)
    events['is_carried_entry'] = (
        (events['is_zone_entry'] == 1) & 
        (events['zone_entry_type_id'].isin(carried_entry_ids))
    ).astype(int)
    
    # is_controlled_exit: Zone exit with puck control
    # Dynamically lookup from dim_zone_exit_type - NO HARDCODED IDs
    zx_type_path = OUTPUT_DIR / 'dim_zone_exit_type.csv'
    if not zx_type_path.exists():
        raise FileNotFoundError(f"dim_zone_exit_type.csv not found - must run dim table creation first")
    
    zx_types = pd.read_csv(zx_type_path)
    controlled_exit_ids = zx_types[zx_types['is_controlled'] == True]['zone_exit_type_id'].tolist()
    carried_exit_ids = zx_types[zx_types['zone_exit_type_name'].str.contains('Carried', na=False)]['zone_exit_type_id'].tolist()
    
    events['is_controlled_exit'] = (
        (events['is_zone_exit'] == 1) & 
        (events['zone_exit_type_id'].isin(controlled_exit_ids))
    ).astype(int)
    
    # is_carried_exit: Carried out (subset of controlled)
    events['is_carried_exit'] = (
        (events['is_zone_exit'] == 1) & 
        (events['zone_exit_type_id'].isin(carried_exit_ids))
    ).astype(int)
    
    # is_rush: Will be populated later as NHL true rush (controlled entry + shot ≤7s)
    # Initialize to 0, will be set in context columns section
    events['is_rush'] = 0
    
    # Goal = event_type='Goal' AND event_detail='Goal_Scored'
    # Shot_Goal is just the shot that resulted in a goal, not the goal itself
    # Faceoff_AfterGoal is the faceoff after a goal, not a goal
    events['is_goal'] = ((events['event_type'] == 'Goal') & (events['event_detail'] == 'Goal_Scored')).astype(int)
    events['is_save'] = events['event_detail'].str.startswith('Save', na=False).astype(int)
    # Shots on goal (SOG) = shots that reached the goalie (saved or scored)
    # EXCLUDES Goal_Scored to avoid double-counting (Shot_Goal + Goal_Scored are linked events)
    # Only count the shot event (Shot_Goal), not the goal event (Goal_Scored)
    events['is_sog'] = ((events['event_type'] == 'Shot') & 
                        events['event_detail'].isin(['Shot_OnNetSaved', 'Shot_OnNet', 'Shot_Goal'])).astype(int)
    events['is_turnover'] = (events['event_type'] == 'Turnover').astype(int)
    events['is_giveaway'] = events['giveaway_type_id'].notna().astype(int)
    # Bad giveaways = misplays/turnovers that hurt the team (not neutral like dumps, battles, shots)
    bad_giveaway_types = [
        'Giveaway_Misplayed', 'Giveaway_PassBlocked', 'Giveaway_PassIntercepted',
        'Giveaway_PassMissed', 'Giveaway_PassReceiverMissed', 'Giveaway_ZoneEntry_ExitMisplay',
        'Giveaway_ZoneEntry/ExitMisplay',  # handle both formats
    ]
    events['is_bad_giveaway'] = ((events['is_giveaway'] == 1) & 
                                  events['event_detail_2'].isin(bad_giveaway_types)).astype(int)
    events['is_takeaway'] = events['takeaway_type_id'].notna().astype(int)
    events['is_faceoff'] = (events['event_type'] == 'Faceoff').astype(int)
    events['is_penalty'] = (events['event_type'] == 'Penalty').astype(int)
    events['is_blocked_shot'] = events['event_detail'].str.contains('Blocked', na=False).astype(int)
    
    # Add shooter, shot_blocker, and goalie columns for shot events
    log.info("  Adding shooter, shot_blocker, and goalie columns for shot events...")
    
    # Filter to shot events (Shot or Goal event_type)
    shot_mask = events['event_type'].isin(['Shot', 'Goal'])
    
    # Initialize columns
    events['shooter_player_id'] = None
    events['shooter_name'] = None
    events['shooter_rating'] = None
    events['shot_blocker_player_id'] = None
    events['shot_blocker_name'] = None
    events['shot_blocker_rating'] = None
    events['goalie_player_id'] = None
    events['goalie_name'] = None
    events['goalie_rating'] = None
    
    if shot_mask.any():
        # Get event_player_1 data for shots (shooter)
        shot_event_ids = events[shot_mask]['event_id'].tolist()
        shooter_data = tracking[
            (tracking['event_id'].isin(shot_event_ids)) &
            (tracking['player_role'].astype(str).str.lower() == 'event_player_1')
        ].drop_duplicates(subset='event_id', keep='first')
        
        # Map shooter info (always from event_player_1 for shots)
        shooter_map_id = dict(zip(shooter_data['event_id'], shooter_data['player_id']))
        shooter_map_name = dict(zip(shooter_data['event_id'], shooter_data.get('player_name', shooter_data.get('player_full_name', None))))
        shooter_map_rating = dict(zip(shooter_data['event_id'], shooter_data.get('player_rating', None)))
        
        events.loc[shot_mask, 'shooter_player_id'] = events.loc[shot_mask, 'event_id'].map(shooter_map_id)
        events.loc[shot_mask, 'shooter_name'] = events.loc[shot_mask, 'event_id'].map(shooter_map_name)
        events.loc[shot_mask, 'shooter_rating'] = events.loc[shot_mask, 'event_id'].map(shooter_map_rating)
        
        # Get shot blocker info (opp_player_1 for blocked shots)
        blocked_mask = shot_mask & (events['is_blocked_shot'] == 1)
        if blocked_mask.any():
            blocked_event_ids = events[blocked_mask]['event_id'].tolist()
            blocker_data = tracking[
                (tracking['event_id'].isin(blocked_event_ids)) &
                (tracking['player_role'].astype(str).str.lower() == 'opp_player_1')
            ].drop_duplicates(subset='event_id', keep='first')
            
            blocker_map_id = dict(zip(blocker_data['event_id'], blocker_data['player_id']))
            blocker_map_name = dict(zip(blocker_data['event_id'], blocker_data.get('player_name', blocker_data.get('player_full_name', None))))
            blocker_map_rating = dict(zip(blocker_data['event_id'], blocker_data.get('player_rating', None)))
            
            events.loc[blocked_mask, 'shot_blocker_player_id'] = events.loc[blocked_mask, 'event_id'].map(blocker_map_id)
            events.loc[blocked_mask, 'shot_blocker_name'] = events.loc[blocked_mask, 'event_id'].map(blocker_map_name)
            events.loc[blocked_mask, 'shot_blocker_rating'] = events.loc[blocked_mask, 'event_id'].map(blocker_map_rating)
        
        # Get goalie info for shots that resulted in saves or goals
        # For shots that were saved (Shot_OnNetSaved): need to find the corresponding Save event
        # For shots that were goals (Shot_Goal): opp_player_1 is the goalie who allowed the goal
        # For actual Save events (event_type='Save'): event_player_1 is the goalie
        
        # Shots that were saved (is_sog but not goal) - goalie is on defending team (opp_player_1)
        saved_shot_mask = shot_mask & (events['is_sog'] == 1) & (events['is_goal'] == 0)
        if saved_shot_mask.any():
            saved_shot_event_ids = events[saved_shot_mask]['event_id'].tolist()
            goalie_saved_data = tracking[
                (tracking['event_id'].isin(saved_shot_event_ids)) &
                (tracking['player_role'].astype(str).str.lower() == 'opp_player_1')
            ].drop_duplicates(subset='event_id', keep='first')
            
            goalie_saved_map_id = dict(zip(goalie_saved_data['event_id'], goalie_saved_data['player_id']))
            goalie_saved_map_name = dict(zip(goalie_saved_data['event_id'], goalie_saved_data.get('player_name', goalie_saved_data.get('player_full_name', None))))
            goalie_saved_map_rating = dict(zip(goalie_saved_data['event_id'], goalie_saved_data.get('player_rating', None)))
            
            events.loc[saved_shot_mask, 'goalie_player_id'] = events.loc[saved_shot_mask, 'event_id'].map(goalie_saved_map_id)
            events.loc[saved_shot_mask, 'goalie_name'] = events.loc[saved_shot_mask, 'event_id'].map(goalie_saved_map_name)
            events.loc[saved_shot_mask, 'goalie_rating'] = events.loc[saved_shot_mask, 'event_id'].map(goalie_saved_map_rating)
        
        # Goals: opp_player_1 is the goalie who allowed the goal
        goal_mask = shot_mask & (events['is_goal'] == 1)
        if goal_mask.any():
            goal_event_ids = events[goal_mask]['event_id'].tolist()
            goalie_goal_data = tracking[
                (tracking['event_id'].isin(goal_event_ids)) &
                (tracking['player_role'].astype(str).str.lower() == 'opp_player_1')
            ].drop_duplicates(subset='event_id', keep='first')
            
            goalie_goal_map_id = dict(zip(goalie_goal_data['event_id'], goalie_goal_data['player_id']))
            goalie_goal_map_name = dict(zip(goalie_goal_data['event_id'], goalie_goal_data.get('player_name', goalie_goal_data.get('player_full_name', None))))
            goalie_goal_map_rating = dict(zip(goalie_goal_data['event_id'], goalie_goal_data.get('player_rating', None)))
            
            events.loc[goal_mask, 'goalie_player_id'] = events.loc[goal_mask, 'event_id'].map(goalie_goal_map_id)
            events.loc[goal_mask, 'goalie_name'] = events.loc[goal_mask, 'event_id'].map(goalie_goal_map_name)
            events.loc[goal_mask, 'goalie_rating'] = events.loc[goal_mask, 'event_id'].map(goalie_goal_map_rating)
        
        shot_count = shot_mask.sum()
        blocked_count = blocked_mask.sum() if blocked_mask.any() else 0
        saved_count = saved_shot_mask.sum() if saved_shot_mask.any() else 0
        goal_count = goal_mask.sum() if goal_mask.any() else 0
        log.info(f"    Added shooter/goalie/blocker info: {shot_count} shots ({blocked_count} blocked, {saved_count} saved, {goal_count} goals)")
    events['is_missed_shot'] = events['event_detail'].isin(['Shot_Missed', 'Shot_MissedPost']).astype(int)
    events['is_deflected'] = (events['event_detail'] == 'Shot_Deflected').astype(int)
    # Tipped shots (from event_detail_2)
    events['is_tipped'] = events['event_detail_2'].isin(['Shot_Tip', 'Shot_Tipped', 'Goal_Tip']).astype(int)
    # is_sog was already created earlier (before shooter/goalie columns)
    # Corsi = all shot attempts (SOG + blocked + missed)
    events['is_corsi'] = ((events['is_sog'] == 1) | 
                          (events['is_blocked_shot'] == 1) | 
                          (events['is_missed_shot'] == 1)).astype(int)
    # Fenwick = unblocked shot attempts (SOG + missed, excludes blocked)
    events['is_fenwick'] = ((events['is_sog'] == 1) | 
                            (events['is_missed_shot'] == 1)).astype(int)
    
    # shot_outcome_id - maps event_detail to dim_shot_outcome
    shot_outcome_map = {
        'Goal_Scored': 'SO01', 'Shot_Goal': 'SO01',  # goal
        'Shot_OnNetSaved': 'SO02', 'Shot_OnNet': 'SO02',  # saved
        'Shot_Blocked': 'SO03', 'Shot_BlockedSameTeam': 'SO03',  # blocked
        'Shot_Missed': 'SO04', 'Shot_MissedPost': 'SO04',  # missed
        'Shot_Deflected': 'SO05',  # deflected
    }
    events['shot_outcome_id'] = events['event_detail'].map(shot_outcome_map)
    
    # pass_outcome_id - maps event_detail to dim_pass_outcome
    pass_outcome_map = {
        'Pass_Completed': 'PO01',
        'Pass_Missed': 'PO02',
        'Pass_Deflected': 'PO03',
        'Pass_Intercepted': 'PO04',
    }
    events['pass_outcome_id'] = events['event_detail'].map(pass_outcome_map)
    
    # save_outcome_id - maps event_detail to dim_save_outcome
    save_outcome_map = {
        'Save_Rebound': 'SV01',
        'Save_Freeze': 'SV02',
        'Save_Played': 'SV03',
    }
    events['save_outcome_id'] = events['event_detail'].map(save_outcome_map)
    
    # zone_outcome_id - maps event_detail to dim_zone_outcome
    zone_outcome_map = {
        'Zone_Entry': 'ZO01',
        'Zone_Entryfailed': 'ZO02',
        'Zone_Exit': 'ZO03',
        'Zone_ExitFailed': 'ZO04',
        'Zone_Keepin': 'ZO05',
        'Zone_KeepinFailed': 'ZO06',
    }
    events['zone_outcome_id'] = events['event_detail'].map(zone_outcome_map)
    
    # is_scoring_chance and is_high_danger: DEFERRED - needs XY data for proper implementation
    # Placeholder: using is_sog | is_goal until XY-based logic is implemented
    events['is_scoring_chance'] = ((events['is_sog'] == 1) | (events['is_goal'] == 1)).astype(int)
    events['is_high_danger'] = (((events['is_sog'] == 1) | (events['is_goal'] == 1)) & (
        (events['is_rebound'] == 1) | events['event_detail_2'].str.contains('Tip|OneTime|Deflect', na=False))).astype(int)
    
    # Pressure
    if 'pressured_pressurer' in first_per_event.columns:
        events['pressured_pressurer'] = events['event_id'].map(dict(zip(first_per_event['event_id'], first_per_event['pressured_pressurer'])))
        events['is_pressured'] = (events['pressured_pressurer'] == 1).astype(int)
    
    # Danger level
    def calc_danger(row):
        if row['is_sog'] != 1 and row['is_goal'] != 1:
            return None
        if row['is_high_danger'] == 1:
            return 'high'
        if row['is_rush'] == 1 or row['event_team_zone'] == 'o':
            return 'medium'
        return 'low'
    events['danger_level'] = events.apply(calc_danger, axis=1)
    events['danger_level_id'] = events['danger_level'].map({'high': 'DL01', 'medium': 'DL02', 'low': 'DL03'})
    
    # Scoring chance key
    sc_events = events[(events['is_sog'] == 1) | (events['is_goal'] == 1)].copy()
    sc_events = sc_events.reset_index(drop=True)
    sc_events['scoring_chance_key'] = 'SC' + sc_events['game_id'].astype(str) + sc_events.index.astype(str).str.zfill(4)
    events['scoring_chance_key'] = events['event_id'].map(dict(zip(sc_events['event_id'], sc_events['scoring_chance_key'])))
    
    # ==========================================================================
    # CONTEXT COLUMNS - Previous/Next Event Relationships
    # ==========================================================================
    log.info("  Adding context columns...")
    
    # Sort by game and time (descending time = ascending chronological order for countdown clock)
    events = events.sort_values(['game_id', 'time_start_total_seconds'], ascending=[True, False]).reset_index(drop=True)
    
    # Initialize all context columns
    context_cols = [
        # Basic prev/next
        'prev_event_id', 'prev_event_type', 'prev_event_detail', 'prev_event_team', 'prev_event_same_team',
        'next_event_id', 'next_event_type', 'next_event_detail', 'next_event_team', 'next_event_same_team',
        'time_since_prev', 'time_to_next',
        # Shot context
        'time_to_next_sog', 'time_since_last_sog', 'events_to_next_sog', 'events_since_last_sog',
        'next_sog_result', 'led_to_sog', 'is_pre_shot_event', 'is_shot_assist',
        # Goal context
        'time_to_next_goal', 'time_since_last_goal', 'events_to_next_goal', 'events_since_last_goal', 'led_to_goal',
        # Zone context
        'time_since_zone_entry', 'events_since_zone_entry', 'time_since_zone_exit',
        # Sequence context
        'sequence_event_num', 'sequence_total_events', 'sequence_duration',
        'is_sequence_first', 'is_sequence_last', 'sequence_has_sog', 'sequence_has_goal', 'sequence_shot_count',
        # Possession context
        'consecutive_team_events', 'time_since_possession_change', 'events_since_possession_change',
        # Faceoff context
        'time_since_faceoff', 'events_since_faceoff',
        # Rush calculated
        'is_rush_calculated', 'time_from_entry_to_shot',
    ]
    for col in context_cols:
        events[col] = None
    
    # Process each game
    for game_id in events['game_id'].unique():
        game_mask = events['game_id'] == game_id
        game_idx = events[game_mask].index.tolist()
        
        if len(game_idx) < 2:
            continue
        
        # Get game events in chronological order (higher time_start = earlier in countdown)
        game_events = events.loc[game_idx].copy()
        
        # Track last seen events for lookback
        last_sog_idx = None
        last_sog_time = None
        last_goal_idx = None
        last_goal_time = None
        last_zone_entry_idx = None
        last_zone_entry_time = None
        last_zone_exit_idx = None
        last_zone_exit_time = None
        last_faceoff_idx = None
        last_faceoff_time = None
        last_possession_change_idx = None
        last_possession_change_time = None
        consecutive_team_count = 0
        prev_team = None
        
        # Forward pass - looking back at previous events
        for i, idx in enumerate(game_idx):
            row = events.loc[idx]
            curr_time = row['time_start_total_seconds']
            curr_team = row.get('player_team')
            
            # Previous event (i-1 in game_idx)
            if i > 0:
                prev_idx = game_idx[i - 1]
                prev_row = events.loc[prev_idx]
                events.at[idx, 'prev_event_id'] = prev_row['event_id']
                events.at[idx, 'prev_event_type'] = prev_row['event_type']
                events.at[idx, 'prev_event_detail'] = prev_row['event_detail']
                events.at[idx, 'prev_event_team'] = prev_row.get('player_team')
                events.at[idx, 'prev_event_same_team'] = 1 if prev_row.get('player_team') == curr_team else 0
                prev_time = prev_row['time_start_total_seconds']
                if pd.notna(curr_time) and pd.notna(prev_time):
                    events.at[idx, 'time_since_prev'] = prev_time - curr_time  # Countdown: prev > curr
            
            # Next event (i+1 in game_idx)
            if i < len(game_idx) - 1:
                next_idx = game_idx[i + 1]
                next_row = events.loc[next_idx]
                events.at[idx, 'next_event_id'] = next_row['event_id']
                events.at[idx, 'next_event_type'] = next_row['event_type']
                events.at[idx, 'next_event_detail'] = next_row['event_detail']
                events.at[idx, 'next_event_team'] = next_row.get('player_team')
                events.at[idx, 'next_event_same_team'] = 1 if next_row.get('player_team') == curr_team else 0
                next_time = next_row['time_start_total_seconds']
                if pd.notna(curr_time) and pd.notna(next_time):
                    events.at[idx, 'time_to_next'] = curr_time - next_time  # Countdown: curr > next
            
            # Time/events since last SOG
            if last_sog_idx is not None and pd.notna(curr_time) and pd.notna(last_sog_time):
                events.at[idx, 'time_since_last_sog'] = last_sog_time - curr_time
                events.at[idx, 'events_since_last_sog'] = i - game_idx.index(last_sog_idx)
            
            # Time/events since last goal
            if last_goal_idx is not None and pd.notna(curr_time) and pd.notna(last_goal_time):
                events.at[idx, 'time_since_last_goal'] = last_goal_time - curr_time
                events.at[idx, 'events_since_last_goal'] = i - game_idx.index(last_goal_idx)
            
            # Time/events since zone entry
            if last_zone_entry_idx is not None and pd.notna(curr_time) and pd.notna(last_zone_entry_time):
                events.at[idx, 'time_since_zone_entry'] = last_zone_entry_time - curr_time
                events.at[idx, 'events_since_zone_entry'] = i - game_idx.index(last_zone_entry_idx)
            
            # Time since zone exit
            if last_zone_exit_idx is not None and pd.notna(curr_time) and pd.notna(last_zone_exit_time):
                events.at[idx, 'time_since_zone_exit'] = last_zone_exit_time - curr_time
            
            # Time/events since faceoff
            if last_faceoff_idx is not None and pd.notna(curr_time) and pd.notna(last_faceoff_time):
                events.at[idx, 'time_since_faceoff'] = last_faceoff_time - curr_time
                events.at[idx, 'events_since_faceoff'] = i - game_idx.index(last_faceoff_idx)
            
            # Time/events since possession change
            if last_possession_change_idx is not None and pd.notna(curr_time) and pd.notna(last_possession_change_time):
                events.at[idx, 'time_since_possession_change'] = last_possession_change_time - curr_time
                events.at[idx, 'events_since_possession_change'] = i - game_idx.index(last_possession_change_idx)
            
            # Consecutive team events
            if curr_team == prev_team and pd.notna(curr_team):
                consecutive_team_count += 1
            else:
                consecutive_team_count = 1
            events.at[idx, 'consecutive_team_events'] = consecutive_team_count
            prev_team = curr_team
            
            # Update trackers
            if row.get('is_sog') == 1:
                last_sog_idx = idx
                last_sog_time = curr_time
            if row.get('is_goal') == 1:
                last_goal_idx = idx
                last_goal_time = curr_time
            if row.get('is_zone_entry') == 1:
                last_zone_entry_idx = idx
                last_zone_entry_time = curr_time
            if row.get('is_zone_exit') == 1:
                last_zone_exit_idx = idx
                last_zone_exit_time = curr_time
            if row.get('is_faceoff') == 1:
                last_faceoff_idx = idx
                last_faceoff_time = curr_time
            if row.get('is_turnover') == 1 or row.get('is_faceoff') == 1:
                last_possession_change_idx = idx
                last_possession_change_time = curr_time
        
        # Reverse pass - looking forward at next events (for time_to_next_sog, etc.)
        next_sog_idx = None
        next_sog_time = None
        next_sog_detail = None
        next_goal_idx = None
        next_goal_time = None
        
        for i in range(len(game_idx) - 1, -1, -1):
            idx = game_idx[i]
            row = events.loc[idx]
            curr_time = row['time_start_total_seconds']
            
            # Time/events to next SOG
            if next_sog_idx is not None and pd.notna(curr_time) and pd.notna(next_sog_time):
                events.at[idx, 'time_to_next_sog'] = curr_time - next_sog_time
                events_to_sog = game_idx.index(next_sog_idx) - i
                events.at[idx, 'events_to_next_sog'] = events_to_sog
                events.at[idx, 'next_sog_result'] = 'goal' if 'Goal' in str(next_sog_detail) else 'save'
                
                # Check if event led to SOG within same play (same team possession)
                curr_play_key = row.get('play_key')
                next_sog_play_key = events.loc[next_sog_idx].get('play_key')
                same_play = (pd.notna(curr_play_key) and curr_play_key == next_sog_play_key)
                
                if same_play:
                    events.at[idx, 'led_to_sog'] = 1
                    
                    # Count passes between current event and shot (within same play)
                    # Check if current event is a pass
                    is_pass = row.get('event_type') == 'Pass'
                    
                    # Count how many passes are between this event and the shot
                    pass_count = 0
                    if is_pass and events_to_sog > 0:
                        # Count passes in the events between current and shot
                        for j in range(i + 1, game_idx.index(next_sog_idx)):
                            if j < len(game_idx):
                                intermediate_idx = game_idx[j]
                                intermediate_event = events.loc[intermediate_idx]
                                # Only count if same play
                                if intermediate_event.get('play_key') == curr_play_key:
                                    if intermediate_event.get('event_type') == 'Pass':
                                        pass_count += 1
                    
                    # is_pre_shot_event: Any event within 3 events before shot in same play
                    if events_to_sog <= 3:
                        events.at[idx, 'is_pre_shot_event'] = 1
                    
                    # is_shot_assist: Pass event within same play, in offensive zone,
                    # with up to 3 passes before shot on goal
                    if is_pass:
                        # Check if in offensive zone (O, Offensive, oz, etc.)
                        event_zone = str(row.get('event_team_zone', '')).lower()
                        is_offensive_zone = (
                            event_zone.startswith('o') or 
                            'offensive' in event_zone or 
                            event_zone == 'oz'
                        )
                        
                        # Shot assist: pass in offensive zone, same play, 
                        # with <= 3 passes (including self) before shot on goal
                        total_passes_to_shot = pass_count + 1  # +1 for current pass
                        if is_offensive_zone and total_passes_to_shot <= 3:
                            events.at[idx, 'is_shot_assist'] = 1
            
            # Time/events to next goal
            if next_goal_idx is not None and pd.notna(curr_time) and pd.notna(next_goal_time):
                events.at[idx, 'time_to_next_goal'] = curr_time - next_goal_time
                events.at[idx, 'events_to_next_goal'] = game_idx.index(next_goal_idx) - i
                if row.get('sequence_key') == events.loc[next_goal_idx].get('sequence_key'):
                    events.at[idx, 'led_to_goal'] = 1
            
            # Update trackers (looking backward in time = forward in game)
            if row.get('is_sog') == 1:
                next_sog_idx = idx
                next_sog_time = curr_time
                next_sog_detail = row.get('event_detail')
            if row.get('is_goal') == 1:
                next_goal_idx = idx
                next_goal_time = curr_time
    
    # Sequence context - aggregate per sequence
    if 'sequence_key' in events.columns:
        seq_stats = events.groupby('sequence_key').agg({
            'event_id': 'count',
            'time_start_total_seconds': ['max', 'min'],
            'is_sog': 'sum',
            'is_goal': 'sum',
        }).reset_index()
        seq_stats.columns = ['sequence_key', 'seq_event_count', 'seq_time_max', 'seq_time_min', 'seq_sog_count', 'seq_goal_count']
        seq_stats['seq_duration'] = seq_stats['seq_time_max'] - seq_stats['seq_time_min']
        seq_stats['seq_has_sog'] = (seq_stats['seq_sog_count'] > 0).astype(int)
        seq_stats['seq_has_goal'] = (seq_stats['seq_goal_count'] > 0).astype(int)
        
        # Map to events
        seq_map = seq_stats.set_index('sequence_key').to_dict()
        events['sequence_total_events'] = events['sequence_key'].map(seq_map['seq_event_count'])
        events['sequence_duration'] = events['sequence_key'].map(seq_map['seq_duration'])
        events['sequence_has_sog'] = events['sequence_key'].map(seq_map['seq_has_sog'])
        events['sequence_has_goal'] = events['sequence_key'].map(seq_map['seq_has_goal'])
        events['sequence_shot_count'] = events['sequence_key'].map(seq_map['seq_sog_count'])
        
        # Event position within sequence
        events['sequence_event_num'] = events.groupby('sequence_key').cumcount() + 1
        events['is_sequence_first'] = (events['sequence_event_num'] == 1).astype(int)
        events['is_sequence_last'] = (events['sequence_event_num'] == events['sequence_total_events']).astype(int)
    
    # Rush calculation:
    # is_rush_calculated: zone entry → SOG within 10 seconds and ≤5 events (any entry type)
    # is_rush: NHL definition - controlled entry + shot within 7 seconds (true transition attack)
    zone_entries = events[events['is_zone_entry'] == 1].index
    for idx in zone_entries:
        time_to_sog = events.at[idx, 'time_to_next_sog']
        events_to_sog = events.at[idx, 'events_to_next_sog']
        is_controlled = events.at[idx, 'is_controlled_entry'] == 1
        
        if pd.notna(time_to_sog) and pd.notna(events_to_sog):
            # Calculated rush: ≤10s AND ≤5 events (any entry type)
            if time_to_sog <= 10 and events_to_sog <= 5:
                events.at[idx, 'is_rush_calculated'] = 1
                events.at[idx, 'time_from_entry_to_shot'] = time_to_sog
            
            # is_rush (NHL definition): controlled entry + shot within 7 seconds
            # This is the "attack before defense sets up" definition
            if is_controlled and time_to_sog <= 7:
                events.at[idx, 'is_rush'] = 1
    
    # Fill NaN with 0 for binary flags
    binary_flags = ['prev_event_same_team', 'next_event_same_team', 'led_to_sog', 'is_pre_shot_event', 
                    'is_shot_assist', 'led_to_goal', 'is_sequence_first', 'is_sequence_last',
                    'sequence_has_sog', 'sequence_has_goal', 'is_rush_calculated', 'is_rush',
                    'is_controlled_entry', 'is_carried_entry', 'is_controlled_exit', 'is_carried_exit']
    for col in binary_flags:
        if col in events.columns:
            events[col] = events[col].fillna(0).astype(int)
    
    log.info(f"    Context columns added: {len(context_cols)}")
    
    # Add segment numbers for events that are part of plays, sequences, chains, etc.
    log.info("  Adding segment numbers for plays, sequences, chains, and linked events...")
    
    # Initialize segment number columns
    events['play_segment_number'] = None
    events['sequence_segment_number'] = None
    events['event_chain_segment_number'] = None
    events['linked_event_segment_number'] = None
    
    # Sort events by game and time to ensure proper ordering
    events = events.sort_values(['game_id', 'time_start_total_seconds', 'event_id'])
    
    # Use event_id as key for mapping (more reliable than DataFrame index)
    if 'event_id' not in events.columns:
        log.warning("    event_id column not found, skipping segment number calculation")
    else:
        # 1. Play segment number (position within play_key)
        if 'play_key' in events.columns:
            play_segments = {}
            for play_key, grp in events.groupby('play_key'):
                if pd.notna(play_key):
                    grp_sorted = grp.sort_values(['time_start_total_seconds', 'event_id'])
                    for i, event_id in enumerate(grp_sorted['event_id'], 1):
                        play_segments[event_id] = i
            events['play_segment_number'] = events['event_id'].map(play_segments)
            play_count = events['play_segment_number'].notna().sum()
            log.info(f"    play_segment_number: {play_count} events have positions")
        
        # 2. Sequence segment number (position within sequence_key)
        if 'sequence_key' in events.columns:
            sequence_segments = {}
            for seq_key, grp in events.groupby('sequence_key'):
                if pd.notna(seq_key):
                    grp_sorted = grp.sort_values(['time_start_total_seconds', 'event_id'])
                    for i, event_id in enumerate(grp_sorted['event_id'], 1):
                        sequence_segments[event_id] = i
            events['sequence_segment_number'] = events['event_id'].map(sequence_segments)
            seq_count = events['sequence_segment_number'].notna().sum()
            log.info(f"    sequence_segment_number: {seq_count} events have positions")
        
        # 3. Event chain segment number (position within event_chain_key)
        if 'event_chain_key' in events.columns:
            chain_segments = {}
            for chain_key, grp in events.groupby('event_chain_key'):
                if pd.notna(chain_key):
                    grp_sorted = grp.sort_values(['time_start_total_seconds', 'event_id'])
                    for i, event_id in enumerate(grp_sorted['event_id'], 1):
                        chain_segments[event_id] = i
            events['event_chain_segment_number'] = events['event_id'].map(chain_segments)
            chain_count = events['event_chain_segment_number'].notna().sum()
            log.info(f"    event_chain_segment_number: {chain_count} events have positions")
        
        # 4. Linked event segment number (position within linked_event_key)
        # Check for linked_event_key or linked_event_index
        linked_key_col = None
        if 'linked_event_key' in events.columns:
            linked_key_col = 'linked_event_key'
        elif 'linked_event_index' in events.columns:
            # Generate linked_event_key from linked_event_index if needed
            events['linked_event_key'] = events.apply(
                lambda row: f"LK{int(row['game_id']):05d}{int(row['linked_event_index']):05d}" 
                if pd.notna(row.get('linked_event_index')) and pd.notna(row.get('game_id')) 
                else None, axis=1
            )
            linked_key_col = 'linked_event_key'
        
        if linked_key_col:
            linked_segments = {}
            for linked_key, grp in events.groupby(linked_key_col):
                if pd.notna(linked_key):
                    grp_sorted = grp.sort_values(['time_start_total_seconds', 'event_id'])
                    for i, event_id in enumerate(grp_sorted['event_id'], 1):
                        linked_segments[event_id] = i
            events['linked_event_segment_number'] = events['event_id'].map(linked_segments)
            linked_count = events['linked_event_segment_number'].notna().sum()
            log.info(f"    linked_event_segment_number: {linked_count} events have positions")
    
    save_table(events, 'fact_events')
    log.info(f"  ✓ fact_events: {len(events)} rows, {len(events.columns)} cols")
    log.info(f"    Flags: rush={events['is_rush'].sum()}, controlled_entry={events['is_controlled_entry'].sum()}, carried_entry={events['is_carried_entry'].sum()}, sog={events['is_sog'].sum()}")


def create_derived_event_tables():
    """Create specialized derived tables from enhanced events."""
    log.section("PHASE 5.10: CREATE DERIVED EVENT TABLES")
    
    events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv', low_memory=False)
    
    # dim_danger_level
    dim_danger = pd.DataFrame({
        'danger_level_id': ['DL01', 'DL02', 'DL03'],
        'danger_level_code': ['high', 'medium', 'low'],
        'danger_level_name': ['High Danger', 'Medium Danger', 'Low Danger'],
        'xg_multiplier': [1.5, 1.0, 0.5]
    })
    save_table(dim_danger, 'dim_danger_level')
    log.info(f"  ✓ dim_danger_level: {len(dim_danger)} rows")
    
    # fact_rushes
    rushes = events[events['is_rush'] == 1].copy()
    rushes['rush_key'] = 'RU' + rushes['game_id'].astype(str) + rushes.index.astype(str).str.zfill(4)
    # VECTORIZED: Determine rush outcome
    rushes['rush_outcome'] = np.where(rushes['is_goal'] == 1, 'goal',
                                      np.where(rushes['is_sog'] == 1, 'shot',
                                              np.where(rushes['is_zone_entry'] == 1, 'zone_entry', 'other')))
    
    # Add event_player_ids and opp_player_ids lists, plus supporting players and opp_player_1 details
    # Load fact_event_players to get all players for each rush event
    event_players_path = OUTPUT_DIR / 'fact_event_players.csv'
    
    # Load dim_player for name/rating lookups (fallback)
    dim_player_path = OUTPUT_DIR / 'dim_player.csv'
    player_name_map = {}
    player_rating_map = {}
    if dim_player_path.exists():
        try:
            dim_player_df = pd.read_csv(dim_player_path, low_memory=False)
            if 'player_id' in dim_player_df.columns:
                if 'player_full_name' in dim_player_df.columns:
                    player_name_map = dict(zip(dim_player_df['player_id'], dim_player_df['player_full_name']))
                elif 'player_name' in dim_player_df.columns:
                    player_name_map = dict(zip(dim_player_df['player_id'], dim_player_df['player_name']))
                if 'player_rating' in dim_player_df.columns:
                    player_rating_map = dict(zip(dim_player_df['player_id'], dim_player_df['player_rating']))
        except Exception as e:
            log.warning(f"  Could not load dim_player for name/rating lookup: {e}")
    
    if event_players_path.exists():
        event_players_df = pd.read_csv(event_players_path, low_memory=False)
        
        # Build lookup: event_id -> lists of player IDs and individual opp_player_1 fields
        event_player_lists = {}
        event_supporting_lists = {}  # event_player_2-6
        opp_player_lists = {}
        opp_supporting_lists = {}  # opp_player_2-6
        opp_player_1_ids = {}
        opp_player_1_names = {}
        opp_player_1_ratings = {}
        
        # Get unique event_ids from rushes
        rush_event_ids = set(rushes['event_id'].dropna().unique())
        
        # Process each rush event
        for event_id in rush_event_ids:
            # Get all players for this event
            ep_for_event = event_players_df[event_players_df['event_id'] == event_id]
            
            if len(ep_for_event) == 0:
                event_player_lists[event_id] = None
                event_supporting_lists[event_id] = None
                opp_player_lists[event_id] = None
                opp_supporting_lists[event_id] = None
                opp_player_1_ids[event_id] = None
                opp_player_1_names[event_id] = None
                opp_player_1_ratings[event_id] = None
                continue
            
            # Separate event players and opponent players by role
            ep_roles = ep_for_event[
                ep_for_event['player_role'].astype(str).str.lower().str.startswith('event_player')
            ]
            opp_roles = ep_for_event[
                ep_for_event['player_role'].astype(str).str.lower().str.startswith('opp_player')
            ]
            
            # Build event player list (event_player_1 first, then others)
            event_player_ids = []
            event_supporting_ids = []  # event_player_2 through event_player_6
            
            # Get event_player_1 first
            ep1 = ep_roles[ep_roles['player_role'].astype(str).str.lower() == 'event_player_1']
            if len(ep1) > 0 and pd.notna(ep1.iloc[0].get('player_id')):
                ep1_id = str(ep1.iloc[0]['player_id'])
                if ep1_id not in ['nan', 'None', '']:
                    event_player_ids.append(ep1_id)
            
            # Get other event players (2-6) - these are supporting players
            for role_num in range(2, 7):
                ep_role = ep_roles[ep_roles['player_role'].astype(str).str.lower() == f'event_player_{role_num}']
                if len(ep_role) > 0 and pd.notna(ep_role.iloc[0].get('player_id')):
                    pid = str(ep_role.iloc[0]['player_id'])
                    if pid not in ['nan', 'None', '']:
                        if pid not in event_player_ids:
                            event_player_ids.append(pid)
                        if pid not in event_supporting_ids:
                            event_supporting_ids.append(pid)
            
            # Build opponent player list (opp_player_1 first, then others)
            opp_player_ids = []
            opp_supporting_ids = []  # opp_player_2 through opp_player_6
            
            # Get opp_player_1 first (store separately for individual columns)
            op1 = opp_roles[opp_roles['player_role'].astype(str).str.lower() == 'opp_player_1']
            op1_id = None
            op1_name = None
            op1_rating = None
            
            if len(op1) > 0 and pd.notna(op1.iloc[0].get('player_id')):
                op1_id = str(op1.iloc[0]['player_id'])
                if op1_id not in ['nan', 'None', '']:
                    opp_player_ids.append(op1_id)
                    # Get name and rating if available (from event_players or dim_player)
                    op1_row = op1.iloc[0]
                    
                    # Try to get name from event_players first
                    if 'player_name' in op1_row.index and pd.notna(op1_row.get('player_name')):
                        op1_name = str(op1_row['player_name'])
                    elif 'player_full_name' in op1_row.index and pd.notna(op1_row.get('player_full_name')):
                        op1_name = str(op1_row['player_full_name'])
                    else:
                        # Fallback to dim_player lookup
                        op1_name = player_name_map.get(op1_id, None)
                    
                    # Try to get rating from event_players first
                    if 'player_rating' in op1_row.index and pd.notna(op1_row.get('player_rating')):
                        rating_val = op1_row['player_rating']
                        try:
                            op1_rating = float(rating_val)
                        except (ValueError, TypeError):
                            op1_rating = None
                    else:
                        # Fallback to dim_player lookup
                        op1_rating = player_rating_map.get(op1_id, None)
                        if op1_rating is not None:
                            try:
                                op1_rating = float(op1_rating)
                            except (ValueError, TypeError):
                                op1_rating = None
            
            # Get other opponent players (2-6) - these are supporting players
            for role_num in range(2, 7):
                opp_role = opp_roles[opp_roles['player_role'].astype(str).str.lower() == f'opp_player_{role_num}']
                if len(opp_role) > 0 and pd.notna(opp_role.iloc[0].get('player_id')):
                    pid = str(opp_role.iloc[0]['player_id'])
                    if pid not in ['nan', 'None', '']:
                        if pid not in opp_player_ids:
                            opp_player_ids.append(pid)
                        if pid not in opp_supporting_ids:
                            opp_supporting_ids.append(pid)
            
            # Store as comma-separated strings
            event_player_lists[event_id] = ','.join(event_player_ids) if event_player_ids else None
            event_supporting_lists[event_id] = ','.join(event_supporting_ids) if event_supporting_ids else None
            opp_player_lists[event_id] = ','.join(opp_player_ids) if opp_player_ids else None
            opp_supporting_lists[event_id] = ','.join(opp_supporting_ids) if opp_supporting_ids else None
            
            # Store opp_player_1 individual fields
            opp_player_1_ids[event_id] = op1_id
            opp_player_1_names[event_id] = op1_name
            opp_player_1_ratings[event_id] = op1_rating
        
        # Map to rushes DataFrame
        rushes['event_player_ids'] = rushes['event_id'].map(event_player_lists)
        rushes['event_supporting_player_ids'] = rushes['event_id'].map(event_supporting_lists)
        rushes['opp_player_ids'] = rushes['event_id'].map(opp_player_lists)
        rushes['opp_supporting_player_ids'] = rushes['event_id'].map(opp_supporting_lists)
        rushes['opp_player_1_id'] = rushes['event_id'].map(opp_player_1_ids)
        rushes['opp_player_1_name'] = rushes['event_id'].map(opp_player_1_names)
        rushes['opp_player_1_rating'] = rushes['event_id'].map(opp_player_1_ratings)
    else:
        log.warning("  fact_event_players.csv not found - cannot build player ID lists")
        rushes['event_player_ids'] = None
        rushes['event_supporting_player_ids'] = None
        rushes['opp_player_ids'] = None
        rushes['opp_supporting_player_ids'] = None
        rushes['opp_player_1_id'] = None
        rushes['opp_player_1_name'] = None
        rushes['opp_player_1_rating'] = None
    
    save_table(rushes, 'fact_rushes')
    log.info(f"  ✓ fact_rushes: {len(rushes)} rows")
    
    # fact_breakouts - Zone exits (breakouts from defensive zone)
    # Definition: Breakout = Zone_Exit event (successful exit from defensive zone with puck control)
    # Coverage: All 4 games consistently (475 events vs 193 with old play_detail1 logic)
    breakouts = events[events['is_zone_exit'] == 1].copy()
    breakouts['breakout_key'] = 'BO' + breakouts['game_id'].astype(str) + breakouts.index.astype(str).str.zfill(4)
    
    # FUTURE: When event_successful is consistently populated across all games,
    # uncomment below to filter to only successful breakouts:
    # breakouts_successful = breakouts[breakouts['event_successful'] == 's'].copy()
    # breakouts_unsuccessful = breakouts[breakouts['event_successful'] == 'u'].copy()
    # Currently only game 18969 has event_successful populated (72 successful, 33 unsuccessful)
    # Games 18977, 18981, 18987 have NULL event_successful values
    # See docs/KNOWN_DATA_QUALITY_ISSUES.md for details
    
    # Add breakout success indicator (will be NULL for incomplete games)
    breakouts['breakout_successful'] = breakouts['event_successful'].apply(
        lambda x: True if x == 's' else (False if x == 'u' else None)
    )
    
    # Remove columns that are 100% null
    breakouts, removed_cols = drop_all_null_columns(breakouts)
    if removed_cols:
        log.info(f"  Removed {len(removed_cols)} all-null columns from fact_breakouts: {removed_cols[:10]}{'...' if len(removed_cols) > 10 else ''}")
    
    save_table(breakouts, 'fact_breakouts')
    log.info(f"  ✓ fact_breakouts: {len(breakouts)} rows, {len(breakouts.columns)} columns")
    
    # fact_zone_entries
    zone_entries = events[events['is_zone_entry'] == 1].copy()
    zone_entries['zone_entry_key'] = 'ZN' + zone_entries['game_id'].astype(str) + zone_entries.index.astype(str).str.zfill(4)
    zone_entries['entry_method'] = zone_entries['event_detail_2'].apply(lambda x: 'rush' if pd.notna(x) and 'Rush' in str(x) else 'dump_in' if pd.notna(x) and 'Dump' in str(x) else 'other')
    save_table(zone_entries, 'fact_zone_entries')
    log.info(f"  ✓ fact_zone_entries: {len(zone_entries)} rows")
    
    # fact_zone_exits
    zone_exits = events[events['is_zone_exit'] == 1].copy()
    zone_exits['zone_exit_key'] = 'ZX' + zone_exits['game_id'].astype(str) + zone_exits.index.astype(str).str.zfill(4)
    zone_exits['exit_method'] = zone_exits['event_detail_2'].apply(lambda x: 'rush' if pd.notna(x) and 'Rush' in str(x) else 'clear' if pd.notna(x) and 'Clear' in str(x) else 'other')
    save_table(zone_exits, 'fact_zone_exits')
    log.info(f"  ✓ fact_zone_exits: {len(zone_exits)} rows")
    
    # fact_scoring_chances_detailed
    sc = events[events['is_scoring_chance'] == 1].copy()
    save_table(sc, 'fact_scoring_chances_detailed')
    log.info(f"  ✓ fact_scoring_chances_detailed: {len(sc)} rows")
    
    # fact_high_danger_chances
    hdc = events[events['is_high_danger'] == 1].copy()
    hdc['high_danger_key'] = 'HD' + hdc['game_id'].astype(str) + hdc.index.astype(str).str.zfill(4)
    save_table(hdc, 'fact_high_danger_chances')
    log.info(f"  ✓ fact_high_danger_chances: {len(hdc)} rows")
    
    # fact_saves
    saves = events[events['is_save'] == 1].copy()
    saves['save_key'] = 'SV' + saves['game_id'].astype(str) + saves.index.astype(str).str.zfill(4)
    
    # Add goalie (event_player_1) and shooter (opp_player_1) columns
    # Load fact_event_players to get player information
    event_players_path = OUTPUT_DIR / 'fact_event_players.csv'
    
    # Load dim_player for name/rating lookups (fallback)
    dim_player_path = OUTPUT_DIR / 'dim_player.csv'
    player_name_map = {}
    player_rating_map = {}
    if dim_player_path.exists():
        try:
            dim_player_df = pd.read_csv(dim_player_path, low_memory=False)
            if 'player_id' in dim_player_df.columns:
                if 'player_full_name' in dim_player_df.columns:
                    player_name_map = dict(zip(dim_player_df['player_id'], dim_player_df['player_full_name']))
                elif 'player_name' in dim_player_df.columns:
                    player_name_map = dict(zip(dim_player_df['player_id'], dim_player_df['player_name']))
                if 'player_rating' in dim_player_df.columns:
                    player_rating_map = dict(zip(dim_player_df['player_id'], dim_player_df['player_rating']))
        except Exception as e:
            log.warning(f"  Could not load dim_player for name/rating lookup: {e}")
    
    if event_players_path.exists():
        event_players_df = pd.read_csv(event_players_path, low_memory=False)
        
        # Build lookup: event_id -> goalie and shooter info
        goalie_ids = {}
        goalie_names = {}
        goalie_ratings = {}
        shooter_ids = {}
        shooter_names = {}
        shooter_ratings = {}
        
        # Get unique event_ids from saves
        save_event_ids = set(saves['event_id'].dropna().unique())
        
        # Process each save event
        for event_id in save_event_ids:
            # Get all players for this event
            ep_for_event = event_players_df[event_players_df['event_id'] == event_id]
            
            if len(ep_for_event) == 0:
                goalie_ids[event_id] = None
                goalie_names[event_id] = None
                goalie_ratings[event_id] = None
                shooter_ids[event_id] = None
                shooter_names[event_id] = None
                shooter_ratings[event_id] = None
                continue
            
            # Get event_player_1 (goalie)
            ep1 = ep_for_event[ep_for_event['player_role'].astype(str).str.lower() == 'event_player_1']
            goalie_id = None
            goalie_name = None
            goalie_rating = None
            
            if len(ep1) > 0 and pd.notna(ep1.iloc[0].get('player_id')):
                goalie_id = str(ep1.iloc[0]['player_id'])
                if goalie_id not in ['nan', 'None', '']:
                    # Get name and rating if available
                    ep1_row = ep1.iloc[0]
                    
                    # Try to get name from event_players first
                    if 'player_name' in ep1_row.index and pd.notna(ep1_row.get('player_name')):
                        goalie_name = str(ep1_row['player_name'])
                    elif 'player_full_name' in ep1_row.index and pd.notna(ep1_row.get('player_full_name')):
                        goalie_name = str(ep1_row['player_full_name'])
                    else:
                        # Fallback to dim_player lookup
                        goalie_name = player_name_map.get(goalie_id, None)
                    
                    # Try to get rating from event_players first
                    if 'player_rating' in ep1_row.index and pd.notna(ep1_row.get('player_rating')):
                        rating_val = ep1_row['player_rating']
                        try:
                            goalie_rating = float(rating_val)
                        except (ValueError, TypeError):
                            goalie_rating = None
                    else:
                        # Fallback to dim_player lookup
                        goalie_rating = player_rating_map.get(goalie_id, None)
                        if goalie_rating is not None:
                            try:
                                goalie_rating = float(goalie_rating)
                            except (ValueError, TypeError):
                                goalie_rating = None
            
            # Get opp_player_1 (shooter)
            op1 = ep_for_event[ep_for_event['player_role'].astype(str).str.lower() == 'opp_player_1']
            shooter_id = None
            shooter_name = None
            shooter_rating = None
            
            if len(op1) > 0 and pd.notna(op1.iloc[0].get('player_id')):
                shooter_id = str(op1.iloc[0]['player_id'])
                if shooter_id not in ['nan', 'None', '']:
                    # Get name and rating if available
                    op1_row = op1.iloc[0]
                    
                    # Try to get name from event_players first
                    if 'player_name' in op1_row.index and pd.notna(op1_row.get('player_name')):
                        shooter_name = str(op1_row['player_name'])
                    elif 'player_full_name' in op1_row.index and pd.notna(op1_row.get('player_full_name')):
                        shooter_name = str(op1_row['player_full_name'])
                    else:
                        # Fallback to dim_player lookup
                        shooter_name = player_name_map.get(shooter_id, None)
                    
                    # Try to get rating from event_players first
                    if 'player_rating' in op1_row.index and pd.notna(op1_row.get('player_rating')):
                        rating_val = op1_row['player_rating']
                        try:
                            shooter_rating = float(rating_val)
                        except (ValueError, TypeError):
                            shooter_rating = None
                    else:
                        # Fallback to dim_player lookup
                        shooter_rating = player_rating_map.get(shooter_id, None)
                        if shooter_rating is not None:
                            try:
                                shooter_rating = float(shooter_rating)
                            except (ValueError, TypeError):
                                shooter_rating = None
            
            # Store values
            goalie_ids[event_id] = goalie_id
            goalie_names[event_id] = goalie_name
            goalie_ratings[event_id] = goalie_rating
            shooter_ids[event_id] = shooter_id
            shooter_names[event_id] = shooter_name
            shooter_ratings[event_id] = shooter_rating
        
        # Map to saves DataFrame
        saves['goalie_player_id'] = saves['event_id'].map(goalie_ids)
        saves['goalie_name'] = saves['event_id'].map(goalie_names)
        saves['goalie_rating'] = saves['event_id'].map(goalie_ratings)
        saves['shooter_player_id'] = saves['event_id'].map(shooter_ids)
        saves['shooter_name'] = saves['event_id'].map(shooter_names)
        saves['shooter_rating'] = saves['event_id'].map(shooter_ratings)
    else:
        log.warning("  fact_event_players.csv not found - cannot build goalie/shooter columns")
        saves['goalie_player_id'] = None
        saves['goalie_name'] = None
        saves['goalie_rating'] = None
        saves['shooter_player_id'] = None
        saves['shooter_name'] = None
        saves['shooter_rating'] = None
    
    # Add context columns: cycle, rush, zone entry timing, etc.
    # Most context columns should already be in saves (from events), but ensure they're present
    context_cols = [
        'is_cycle', 'cycle_key', 'is_rush', 'is_rush_calculated',
        'is_rebound', 'is_controlled_entry', 'is_carried_entry',
        'is_zone_entry', 'is_zone_exit', 'zone_entry_type_id',
        'time_to_next_sog', 'time_since_last_sog',
        'events_to_next_sog', 'events_since_last_sog',
        'is_pre_shot_event', 'is_shot_assist',
        'play_key', 'sequence_key', 'event_chain_key'
    ]
    
    # Ensure context columns exist (they should already be in saves from events)
    for col in context_cols:
        if col not in saves.columns:
            saves[col] = None
    
    # Calculate time_from_zone_entry for saves (time from most recent zone entry to this save/shot)
    # This is the time from when the offensive team entered the zone to when the shot was saved
    log.info("  Calculating time_from_zone_entry for saves...")
    saves['time_from_zone_entry'] = None
    
    # Reload events if needed for looking back at zone entries
    events_for_lookup = events.copy() if 'events' in locals() else pd.read_csv(OUTPUT_DIR / 'fact_events.csv', low_memory=False)
    
    # Group by game to look back for zone entries
    for game_id in saves['game_id'].dropna().unique():
        game_events = events_for_lookup[events_for_lookup['game_id'] == game_id].copy()
        game_save_indices = saves[saves['game_id'] == game_id].index
        
        if len(game_events) == 0 or len(game_save_indices) == 0:
            continue
        
        # Sort events by time
        game_events = game_events.sort_values('time_start_total_seconds')
        game_events['time_start_total_seconds'] = pd.to_numeric(game_events['time_start_total_seconds'], errors='coerce')
        
        # Find zone entries in this game
        zone_entries = game_events[game_events['is_zone_entry'] == 1].copy()
        
        # Process each save in this game
        for save_idx in game_save_indices:
            save_row = saves.loc[save_idx]
            save_event_id = save_row['event_id']
            save_time = pd.to_numeric(save_row.get('time_start_total_seconds'), errors='coerce')
            
            if pd.isna(save_time) or pd.isna(save_event_id):
                continue
            
            # For saves, we want to find the zone entry by the team that took the shot
            # The save event's team_venue is the goalie's team (defending team)
            # So the shooting team is the opposite team
            goalie_team_venue = str(save_row.get('team_venue', '')).lower()
            
            # Get zone entries before this save, sorted descending (most recent first)
            prev_entries = zone_entries[
                (zone_entries['time_start_total_seconds'] < save_time) &
                (zone_entries['time_start_total_seconds'] >= save_time - 60)  # Within 60 seconds
            ].sort_values('time_start_total_seconds', ascending=False)
            
            if len(prev_entries) > 0:
                # Find entry by the shooting team (opposite of goalie's team)
                for _, entry_row in prev_entries.iterrows():
                    entry_team_venue = str(entry_row.get('team_venue', '')).lower()
                    
                    # If entry team is different from goalie team, this is the shooting team's entry
                    if entry_team_venue != goalie_team_venue and entry_team_venue in ['home', 'away']:
                        entry_time = pd.to_numeric(entry_row.get('time_start_total_seconds'), errors='coerce')
                        if pd.notna(entry_time):
                            time_diff = save_time - entry_time
                            if time_diff >= 0:  # Sanity check
                                saves.at[save_idx, 'time_from_zone_entry'] = time_diff
                                break  # Use most recent zone entry
    
    save_table(saves, 'fact_saves')
    log.info(f"  ✓ fact_saves: {len(saves)} rows")
    
    # fact_turnovers_detailed
    turnovers = events[events['is_turnover'] == 1].copy()
    turnovers['turnover_key_new'] = 'TO' + turnovers['game_id'].astype(str) + turnovers.index.astype(str).str.zfill(4)
    save_table(turnovers, 'fact_turnovers_detailed')
    log.info(f"  ✓ fact_turnovers_detailed: {len(turnovers)} rows")
    
    # fact_faceoffs
    faceoffs = events[events['is_faceoff'] == 1].copy()
    faceoffs['faceoff_key'] = 'FO' + faceoffs['game_id'].astype(str) + faceoffs.index.astype(str).str.zfill(4)
    faceoffs['faceoff_type'] = faceoffs['event_detail'].apply(lambda x: 'after_goal' if pd.notna(x) and 'AfterGoal' in str(x) else 'after_stoppage' if pd.notna(x) and 'AfterStoppage' in str(x) else 'other')
    
    # Rename player columns for clarity:
    # event_player_1 -> faceoff_winner (id, name, rating)
    # opp_player_1 -> faceoff_loser (id, name, rating)
    rename_map = {}
    
    if 'event_player_1_id' in faceoffs.columns:
        rename_map['event_player_1_id'] = 'faceoff_winner_id'
    if 'event_player_1_name' in faceoffs.columns:
        rename_map['event_player_1_name'] = 'faceoff_winner_name'
    if 'event_player_1_rating' in faceoffs.columns:
        rename_map['event_player_1_rating'] = 'faceoff_winner_rating'
    
    if 'opp_player_1_id' in faceoffs.columns:
        rename_map['opp_player_1_id'] = 'faceoff_loser_id'
    if 'opp_player_1_name' in faceoffs.columns:
        rename_map['opp_player_1_name'] = 'faceoff_loser_name'
    if 'opp_player_1_rating' in faceoffs.columns:
        rename_map['opp_player_1_rating'] = 'faceoff_loser_rating'
    
    if rename_map:
        faceoffs = faceoffs.rename(columns=rename_map)
        log.info(f"  Renamed {len(rename_map)} player columns for faceoffs")
    
    # Remove columns that are 100% null
    faceoffs, removed_cols = drop_all_null_columns(faceoffs)
    if removed_cols:
        log.info(f"  Removed {len(removed_cols)} all-null columns from fact_faceoffs: {removed_cols[:10]}{'...' if len(removed_cols) > 10 else ''}")
    
    save_table(faceoffs, 'fact_faceoffs')
    log.info(f"  ✓ fact_faceoffs: {len(faceoffs)} rows, {len(faceoffs.columns)} columns")
    
    # fact_penalties
    penalties = events[events['is_penalty'] == 1].copy()
    penalties['penalty_key'] = 'PN' + penalties['game_id'].astype(str) + penalties.index.astype(str).str.zfill(4)
    save_table(penalties, 'fact_penalties')
    log.info(f"  ✓ fact_penalties: {len(penalties)} rows")



def enhance_shift_tables():
    """Comprehensive shift enhancement with player IDs, plus/minus, and shift stats."""
    log.section("PHASE 5.11: COMPREHENSIVE SHIFT ENHANCEMENT")
    
    shifts_path = OUTPUT_DIR / 'fact_shifts.csv'
    events_path = OUTPUT_DIR / 'fact_events.csv'
    roster_path = OUTPUT_DIR / 'fact_gameroster.csv'
    
    if not shifts_path.exists():
        log.warn("fact_shifts not found, skipping")
        return
    
    shifts = pd.read_csv(shifts_path, low_memory=False)
    events = pd.read_csv(events_path, low_memory=False)
    roster = pd.read_csv(roster_path, low_memory=False)
    dim_team = pd.read_csv(OUTPUT_DIR / 'dim_team.csv', low_memory=False)
    dim_schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv', low_memory=False)
    dim_player = pd.read_csv(OUTPUT_DIR / 'dim_player.csv', low_memory=False)
    
    log.info(f"Enhancing {len(shifts)} shifts...")
    
    # Calculate total seconds for shifts (from period start, counting down)
    # In hockey, the clock counts DOWN from 20:00 (1200 seconds) to 0:00
    # So shift_start_min=18, shift_start_sec=30 means 18:30 on clock = 1200 - 18*60 - 30 = 1200 - 1110 = 90 seconds elapsed
    # But we use "total seconds remaining" which is min*60 + sec
    shifts['shift_start_total_seconds'] = shifts['shift_start_min'].fillna(0) * 60 + shifts['shift_start_sec'].fillna(0)
    shifts['shift_end_total_seconds'] = shifts['shift_end_min'].fillna(0) * 60 + shifts['shift_end_sec'].fillna(0)
    shifts['shift_duration'] = shifts['shift_start_total_seconds'] - shifts['shift_end_total_seconds']
    
    # Prep events
    events['event_total_seconds'] = events['event_start_min'] * 60 + events['event_start_sec']
    
    # Build lookups - VECTORIZED
    # player_team_map: player_id -> team_name (use last occurrence per game_id sort)
    roster_sorted = roster.sort_values('game_id')
    player_team_map = dict(zip(roster_sorted['player_id'], roster_sorted['team_name']))
    
    # roster_lookup: (game_id, team_name, jersey) -> player_id
    roster_lookup = dict(zip(
        zip(roster['game_id'], roster['team_name'], roster['player_game_number'].astype(str)),
        roster['player_id']
    ))
    
    # VECTORIZED: Add event_team to events
    if len(events) > 0 and 'event_player_ids' in events.columns:
        events['first_player'] = events['event_player_ids'].astype(str).str.split(',').str[0].str.strip()
        events['event_team'] = events['first_player'].map(player_team_map)
        events['is_home_event'] = events['event_team'] == events['home_team']
        events.drop(columns=['first_player'], inplace=True, errors='ignore')
    
    # Build shift-events mapping
    def get_shift_events(shift_row, all_events):
        game_id = shift_row['game_id']
        period = shift_row['period']
        start_sec = shift_row['shift_start_total_seconds']
        end_sec = shift_row['shift_end_total_seconds']
        if pd.isna(period) or pd.isna(start_sec) or pd.isna(end_sec):
            return pd.DataFrame()
        mask = (all_events['game_id'] == game_id) & \
               (all_events['period'] == period) & \
               (all_events['event_total_seconds'] <= start_sec) & \
               (all_events['event_total_seconds'] >= end_sec)
        return all_events[mask]
    
    # VECTORIZED: Build shift-events mapping more efficiently
    # Instead of iterating through shifts, merge events with shifts and filter
    if len(events) > 0 and len(shifts) > 0:
        # Prepare events and shifts for merge
        events_for_merge = events[['event_id', 'game_id', 'period', 'event_total_seconds']].copy()
        shifts_for_merge = shifts[['shift_id', 'game_id', 'period', 'shift_start_total_seconds', 
                                   'shift_end_total_seconds']].copy()
        shifts_for_merge = shifts_for_merge[
            shifts_for_merge['shift_start_total_seconds'].notna() & 
            shifts_for_merge['shift_end_total_seconds'].notna()
        ]
        
        # Merge on game_id and period
        events_shifts = events_for_merge.merge(
            shifts_for_merge,
            on=['game_id', 'period'],
            how='inner'
        )
        
        # Filter by time window
        time_mask = (
            (events_shifts['event_total_seconds'] <= events_shifts['shift_start_total_seconds']) &
            (events_shifts['event_total_seconds'] >= events_shifts['shift_end_total_seconds'])
        )
        events_in_shifts = events_shifts[time_mask]
        
        # Build shift_events_map using groupby (much faster than iterrows)
        shift_events_map = {}
        for shift_id, group in events_in_shifts.groupby('shift_id'):
            event_ids = group['event_id'].tolist()
            shift_events_map[shift_id] = events[events['event_id'].isin(event_ids)]
    else:
        shift_events_map = {}
    
    # 1. Basic FKs
    shifts['period_id'] = 'P' + shifts['period'].fillna(0).astype(int).astype(str).str.zfill(2)
    team_name_to_id = dict(zip(dim_team['team_name'], dim_team['team_id']))
    shifts['home_team_id'] = shifts['home_team'].map(team_name_to_id)
    shifts['away_team_id'] = shifts['away_team'].map(team_name_to_id)
    game_to_season = dict(zip(dim_schedule['game_id'], dim_schedule['season_id']))
    shifts['season_id'] = shifts['game_id'].map(game_to_season)
    
    def get_time_bucket(row):
        period = row['period']
        start_min = row['shift_start_min']
        if pd.isna(period) or pd.isna(start_min):
            return None
        if period > 3:
            return 'TB06'
        if start_min >= 15:
            return 'TB01'
        elif start_min >= 10:
            return 'TB02'
        elif start_min >= 5:
            return 'TB03'
        elif start_min >= 2:
            return 'TB04'
        else:
            return 'TB05'
    shifts['time_bucket_id'] = shifts.apply(get_time_bucket, axis=1)
    
    def map_strength_id(strength_str):
        if pd.isna(strength_str):
            return None
        strength_str = str(strength_str).split()[0]
        if 'v' in strength_str:
            parts = strength_str.split('v')
            try:
                home, away = int(parts[0]), int(parts[1])
                strength_map = {
                    (5, 5): 'STR0001', (5, 4): 'STR0002', (5, 3): 'STR0003',
                    (4, 5): 'STR0004', (3, 5): 'STR0005', (4, 4): 'STR0006',
                    (3, 3): 'STR0007', (4, 3): 'STR0008', (3, 4): 'STR0009',
                    (6, 5): 'STR0010', (5, 6): 'STR0011', (6, 4): 'STR0012',
                    (4, 6): 'STR0013', (0, 0): 'STR0016', (6, 6): 'STR0017',
                }
                return strength_map.get((home, away), None)
            except Exception as e:
                return None
        return None
    shifts['strength_id'] = shifts['strength'].apply(map_strength_id)
    
    # 2. Derive shift start/stop types
    def derive_start_type(shift_events_df, current_type):
        if pd.notna(current_type):
            return current_type
        if shift_events_df.empty:
            return 'OnTheFly'
        first_event = shift_events_df.iloc[-1]
        if first_event['is_faceoff'] == 1:
            detail = str(first_event['event_detail'])
            if 'AfterGoal' in detail:
                return 'FaceoffAfterGoal'
            elif 'AfterStoppage' in detail:
                return 'OtherFaceoff'
            elif 'GameStart' in detail:
                return 'GameStart'
            else:
                return 'OtherFaceoff'
        return 'OnTheFly'
    
    def derive_stop_type(shift_events_df, current_type):
        if pd.notna(current_type):
            return current_type
        if shift_events_df.empty:
            return 'OnTheFly'
        last_event = shift_events_df.iloc[0]
        if last_event['is_goal'] == 1:
            return 'Goal'
        elif last_event['is_penalty'] == 1:
            return 'Penalty'
        elif 'Stoppage' in str(last_event['event_type']):
            return 'Stoppage'
        return 'OnTheFly'
    
    # Use .get() to handle shifts with no events (empty DataFrame default)
    empty_events_df = pd.DataFrame()
    shifts['shift_start_type_derived'] = [
        derive_start_type(shift_events_map.get(sid, empty_events_df), shifts.loc[i, 'shift_start_type'])
        for i, sid in enumerate(shifts['shift_id'])
    ]
    shifts['shift_stop_type_derived'] = [
        derive_stop_type(shift_events_map.get(sid, empty_events_df), shifts.loc[i, 'shift_stop_type'])
        for i, sid in enumerate(shifts['shift_id'])
    ]
    
    # 3. Derive zones
    def get_start_end_zones(shift_events_df):
        if shift_events_df.empty:
            return None, None
        first_zone = shift_events_df.iloc[-1]['event_team_zone']
        last_zone = shift_events_df.iloc[0]['event_team_zone']
        return first_zone, last_zone
    
    zones_data = [get_start_end_zones(shift_events_map.get(sid, empty_events_df)) for sid in shifts['shift_id']]
    shifts['start_zone'] = [z[0] for z in zones_data]
    shifts['end_zone'] = [z[1] for z in zones_data]
    # Map zone names to zone_id (ZN01=Offensive, ZN02=Defensive, ZN03=Neutral)
    zone_map = {
        'Offensive': 'ZN01', 'offensive': 'ZN01', 'O': 'ZN01', 'o': 'ZN01',
        'Defensive': 'ZN02', 'defensive': 'ZN02', 'D': 'ZN02', 'd': 'ZN02',
        'Neutral': 'ZN03', 'neutral': 'ZN03', 'N': 'ZN03', 'n': 'ZN03',
    }
    shifts['start_zone_id'] = shifts['start_zone'].map(zone_map)
    shifts['end_zone_id'] = shifts['end_zone'].map(zone_map)
    
    # 4. Add player IDs
    player_slots = [
        ('home', 'forward_1'), ('home', 'forward_2'), ('home', 'forward_3'),
        ('home', 'defense_1'), ('home', 'defense_2'), ('home', 'xtra'), ('home', 'goalie'),
        ('away', 'forward_1'), ('away', 'forward_2'), ('away', 'forward_3'),
        ('away', 'defense_1'), ('away', 'defense_2'), ('away', 'xtra'), ('away', 'goalie'),
    ]
    
    # VECTORIZED: Map player IDs for all slots at once
    for venue, slot in player_slots:
        col_name = f'{venue}_{slot}'
        id_col = f'{col_name}_id'
        team_col = f'{venue}_team'
        
        # Create lookup keys vectorized
        shifts['_lookup_key_team'] = list(zip(
            shifts['game_id'],
            shifts[team_col].fillna(''),
            shifts[col_name].fillna('').astype(str)
        ))
        
        # Map using roster_lookup
        shifts[id_col] = shifts['_lookup_key_team'].map(roster_lookup)
        
        # Clean up temporary columns
        shifts.drop(columns=['_lookup_key_team'], inplace=True, errors='ignore')
    
    # 4.5 Add team ratings (v19.00 ROOT CAUSE FIX) - OPTIMIZED v29.2
    # Calculate avg/min/max ratings for home and away teams (excluding goalies)
    log.info("  Adding team ratings (excluding goalies)...")
    
    player_rating_map = dict(zip(dim_player['player_id'], dim_player['current_skill_rating']))
    
    # Skater position columns (exclude goalies)
    home_skater_cols = ['home_forward_1_id', 'home_forward_2_id', 'home_forward_3_id',
                        'home_defense_1_id', 'home_defense_2_id']
    away_skater_cols = ['away_forward_1_id', 'away_forward_2_id', 'away_forward_3_id',
                        'away_defense_1_id', 'away_defense_2_id']
    
    # VECTORIZED: Map player IDs to ratings for all columns at once
    for col in home_skater_cols + away_skater_cols:
        if col in shifts.columns:
            shifts[f'{col}_rating'] = shifts[col].map(player_rating_map)
    
    # Calculate home team ratings using vectorized operations
    home_rating_cols = [f'{col}_rating' for col in home_skater_cols]
    home_ratings_df = shifts[home_rating_cols].copy()
    
    # Filter out NaN values and calculate stats
    shifts['home_avg_rating'] = home_ratings_df.mean(axis=1, skipna=True).round(2)
    shifts['home_min_rating'] = home_ratings_df.min(axis=1, skipna=True)
    shifts['home_max_rating'] = home_ratings_df.max(axis=1, skipna=True)
    
    # Calculate away team ratings using vectorized operations
    away_rating_cols = [f'{col}_rating' for col in away_skater_cols]
    away_ratings_df = shifts[away_rating_cols].copy()
    
    # Filter out NaN values and calculate stats
    shifts['away_avg_rating'] = away_ratings_df.mean(axis=1, skipna=True).round(2)
    shifts['away_min_rating'] = away_ratings_df.min(axis=1, skipna=True)
    shifts['away_max_rating'] = away_ratings_df.max(axis=1, skipna=True)
    
    # Clean up temporary rating columns to save memory
    temp_rating_cols = home_rating_cols + away_rating_cols
    for col in temp_rating_cols:
        if col in shifts.columns:
            shifts.drop(columns=[col], inplace=True)
    
    # Calculate rating differential and advantage
    shifts['rating_differential'] = shifts['home_avg_rating'] - shifts['away_avg_rating']
    shifts['home_rating_advantage'] = shifts['rating_differential'] > 0
    
    # Log summary
    home_avg = shifts['home_avg_rating'].mean()
    away_avg = shifts['away_avg_rating'].mean()
    log.info(f"  Team ratings: home_avg={home_avg:.2f}, away_avg={away_avg:.2f}, differential={home_avg-away_avg:.2f}")
    
    # 5. Plus/minus
    # CRITICAL: Goals ONLY via event_type='Goal' AND event_detail='Goal_Scored' (per CODE_STANDARDS.md)
    actual_goals = events[(events['event_type'] == 'Goal') & (events['event_detail'] == 'Goal_Scored')].copy()
    
    # VECTORIZED: Extract first player ID and map to team
    if len(actual_goals) > 0:
        actual_goals['first_player'] = actual_goals['event_player_ids'].astype(str).str.split(',').str[0].str.strip()
        actual_goals['scoring_team'] = actual_goals['first_player'].map(player_team_map)
        actual_goals['is_home_goal'] = actual_goals['scoring_team'] == actual_goals['home_team']
    
    pm_types = ['all', 'ev', 'nen', 'pp', 'pk']
    for pm_type in pm_types:
        for venue in ['home', 'away']:
            shifts[f'{venue}_gf_{pm_type}'] = 0
            shifts[f'{venue}_ga_{pm_type}'] = 0
    
    def get_shift_goals(shift_row, goals_df):
        game_id = shift_row['game_id']
        period = shift_row['period']
        start_sec = shift_row['shift_start_total_seconds']
        end_sec = shift_row['shift_end_total_seconds']
        if pd.isna(period) or pd.isna(start_sec) or pd.isna(end_sec):
            return pd.DataFrame()
        # Use > for end boundary to avoid double-counting goals at exact shift boundaries
        # (goals at boundary time belong to shift starting at that time, not ending)
        mask = (goals_df['game_id'] == game_id) & \
               (goals_df['period'] == period) & \
               (goals_df['event_total_seconds'] <= start_sec) & \
               (goals_df['event_total_seconds'] > end_sec)
        return goals_df[mask]
    
    for i, shift in shifts.iterrows():
        shift_goals = get_shift_goals(shift, actual_goals)
        if shift_goals.empty:
            continue
        is_ev = str(shift.get('strength', '')) == '5v5'
        is_nen = (shift.get('home_team_en', 0) == 0) and (shift.get('away_team_en', 0) == 0)
        is_home_pp = shift.get('home_team_pp', 0) == 1
        is_home_pk = shift.get('home_team_pk', 0) == 1
        
        for _, goal in shift_goals.iterrows():
            is_home_goal = goal['is_home_goal']
            
            # FIX: Use the GOAL's strength, not the shift's strength
            # A goal at 5v5 should not be credited as PP/PK even if shift started as PP
            goal_strength = str(goal.get('strength', '')).lower()
            goal_is_ev = goal_strength in ['5v5', '4v4', '3v3']
            goal_is_pp_home = goal_strength in ['5v4', '5v3', '4v3']  # Home has more players
            goal_is_pk_home = goal_strength in ['4v5', '3v5', '3v4']  # Home has fewer players
            
            # All goals count
            if is_home_goal:
                shifts.at[i, 'home_gf_all'] += 1
                shifts.at[i, 'away_ga_all'] += 1
            else:
                shifts.at[i, 'away_gf_all'] += 1
                shifts.at[i, 'home_ga_all'] += 1
            
            # EV goals (use goal strength, not shift strength)
            if goal_is_ev:
                if is_home_goal:
                    shifts.at[i, 'home_gf_ev'] += 1
                    shifts.at[i, 'away_ga_ev'] += 1
                else:
                    shifts.at[i, 'away_gf_ev'] += 1
                    shifts.at[i, 'home_ga_ev'] += 1
            
            # Non-empty-net (still use shift status for EN)
            if is_nen:
                if is_home_goal:
                    shifts.at[i, 'home_gf_nen'] += 1
                    shifts.at[i, 'away_ga_nen'] += 1
                else:
                    shifts.at[i, 'away_gf_nen'] += 1
                    shifts.at[i, 'home_ga_nen'] += 1
            
            # PP/PK goals (use goal strength, not shift strength)
            if goal_is_pp_home:
                if is_home_goal:
                    shifts.at[i, 'home_gf_pp'] += 1
                    shifts.at[i, 'away_ga_pk'] += 1
                else:
                    shifts.at[i, 'away_gf_pk'] += 1
                    shifts.at[i, 'home_ga_pp'] += 1
            elif goal_is_pk_home:
                if is_home_goal:
                    shifts.at[i, 'home_gf_pk'] += 1
                    shifts.at[i, 'away_ga_pp'] += 1
                else:
                    shifts.at[i, 'away_gf_pp'] += 1
                    shifts.at[i, 'home_ga_pk'] += 1
    
    for pm_type in pm_types:
        shifts[f'home_pm_{pm_type}'] = shifts[f'home_gf_{pm_type}'] - shifts[f'home_ga_{pm_type}']
        shifts[f'away_pm_{pm_type}'] = shifts[f'away_gf_{pm_type}'] - shifts[f'away_ga_{pm_type}']
    
    # 5b. Game state tracking (leading/trailing/tied)
    # Calculate running score at each shift start
    log.info("  Calculating game state (leading/trailing/tied)...")
    shifts['game_state'] = 'tied'  # Default
    shifts['score_differential'] = 0  # Home perspective: positive = home leading
    
    for game_id in shifts['game_id'].unique():
        game_shifts = shifts[shifts['game_id'] == game_id].copy()
        game_goals = actual_goals[actual_goals['game_id'] == game_id].sort_values('event_total_seconds')
        
        if len(game_goals) == 0:
            # No goals in game = always tied
            continue
        
        # Build running score at each goal
        home_score = 0
        away_score = 0
        goal_scores = []  # (time, home_score, away_score)
        
        for _, goal in game_goals.iterrows():
            if goal['is_home_goal']:
                home_score += 1
            else:
                away_score += 1
            goal_scores.append((goal['event_total_seconds'], home_score, away_score))
        
        # For each shift, find score at shift start
        for idx in game_shifts.index:
            shift_start = shifts.at[idx, 'shift_start_total_seconds']
            if pd.isna(shift_start):
                continue
            
            # Find most recent goal before shift start
            h_score, a_score = 0, 0
            for goal_time, h, a in goal_scores:
                if goal_time < shift_start:
                    h_score, a_score = h, a
                else:
                    break
            
            diff = h_score - a_score
            shifts.at[idx, 'score_differential'] = diff
            
            if diff > 0:
                shifts.at[idx, 'game_state'] = 'home_leading'
            elif diff < 0:
                shifts.at[idx, 'game_state'] = 'home_trailing'
            else:
                shifts.at[idx, 'game_state'] = 'tied'
    
    # Add close game flag (within 1 goal)
    shifts['is_close_game'] = shifts['score_differential'].abs() <= 1
    
    log.info(f"  Game states: tied={len(shifts[shifts['game_state']=='tied'])}, home_leading={len(shifts[shifts['game_state']=='home_leading'])}, home_trailing={len(shifts[shifts['game_state']=='home_trailing'])}")
    
    # 6. Shift stats
    stat_cols = ['sf', 'sa', 'shot_diff', 'cf', 'ca', 'cf_pct', 'ff', 'fa', 'ff_pct',
                 'scf', 'sca', 'hdf', 'hda', 
                 'home_zone_entries', 'away_zone_entries', 'home_zone_exits', 'away_zone_exits',
                 'home_giveaways', 'away_giveaways', 'home_bad_giveaways', 'away_bad_giveaways',
                 'home_takeaways', 'away_takeaways',
                 'fo_won', 'fo_lost', 'fo_pct', 'event_count']
    for col in stat_cols:
        shifts[col] = 0 if col not in ['cf_pct', 'ff_pct', 'fo_pct'] else 0.0
    
    # VECTORIZED: Aggregate shift stats using groupby instead of iterrows
    # Build a combined DataFrame with all events and their shift_ids for efficient aggregation
    if len(shift_events_map) > 0:
        all_shift_events = []
        for shift_id, shift_ev in shift_events_map.items():
            if not shift_ev.empty:
                shift_ev_copy = shift_ev.copy()
                shift_ev_copy['_shift_id'] = shift_id
                all_shift_events.append(shift_ev_copy)
        
        if all_shift_events:
            combined_events = pd.concat(all_shift_events, ignore_index=True)
            
            # Create aggregation functions for each stat type
            def agg_shift_stats(events_df, shift_ids):
                """Aggregate stats for shifts using vectorized operations."""
                stats = {}
                
                # Event count
                event_counts = events_df.groupby('_shift_id').size()
                stats['event_count'] = shift_ids.map(event_counts).fillna(0)
                
                # SOG stats
                sog_events = events_df[events_df['is_sog'] == 1] if 'is_sog' in events_df.columns else pd.DataFrame()
                if len(sog_events) > 0:
                    home_sog = sog_events[sog_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['sf'] = shift_ids.map(home_sog).fillna(0)
                    total_sog = sog_events.groupby('_shift_id').size()
                    stats['sa'] = (shift_ids.map(total_sog).fillna(0) - stats['sf']).fillna(0)
                    stats['shot_diff'] = stats['sf'] - stats['sa']
                
                # Corsi stats
                corsi_events = events_df[events_df['is_corsi'] == 1] if 'is_corsi' in events_df.columns else pd.DataFrame()
                if len(corsi_events) > 0:
                    home_corsi = corsi_events[corsi_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['cf'] = shift_ids.map(home_corsi).fillna(0)
                    total_corsi = corsi_events.groupby('_shift_id').size()
                    stats['ca'] = (shift_ids.map(total_corsi).fillna(0) - stats['cf']).fillna(0)
                    total_corsi_sum = stats['cf'] + stats['ca']
                    stats['cf_pct'] = (stats['cf'] / total_corsi_sum * 100).where(total_corsi_sum > 0, 50.0)
                
                # Fenwick stats
                fenwick_events = events_df[events_df['is_fenwick'] == 1] if 'is_fenwick' in events_df.columns else pd.DataFrame()
                if len(fenwick_events) > 0:
                    home_fenwick = fenwick_events[fenwick_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['ff'] = shift_ids.map(home_fenwick).fillna(0)
                    total_fenwick = fenwick_events.groupby('_shift_id').size()
                    stats['fa'] = (shift_ids.map(total_fenwick).fillna(0) - stats['ff']).fillna(0)
                    total_fenwick_sum = stats['ff'] + stats['fa']
                    stats['ff_pct'] = (stats['ff'] / total_fenwick_sum * 100).where(total_fenwick_sum > 0, 50.0)
                
                # Scoring chances
                sc_events = events_df[events_df['is_scoring_chance'] == 1] if 'is_scoring_chance' in events_df.columns else pd.DataFrame()
                if len(sc_events) > 0:
                    home_sc = sc_events[sc_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['scf'] = shift_ids.map(home_sc).fillna(0)
                    total_sc = sc_events.groupby('_shift_id').size()
                    stats['sca'] = (shift_ids.map(total_sc).fillna(0) - stats['scf']).fillna(0)
                
                # High danger
                hd_events = events_df[events_df['is_high_danger'] == 1] if 'is_high_danger' in events_df.columns else pd.DataFrame()
                if len(hd_events) > 0:
                    home_hd = hd_events[hd_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['hdf'] = shift_ids.map(home_hd).fillna(0)
                    total_hd = hd_events.groupby('_shift_id').size()
                    stats['hda'] = (shift_ids.map(total_hd).fillna(0) - stats['hdf']).fillna(0)
                
                # Zone entries/exits
                ze_events = events_df[events_df['is_zone_entry'] == 1] if 'is_zone_entry' in events_df.columns else pd.DataFrame()
                if len(ze_events) > 0:
                    home_ze = ze_events[ze_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['home_zone_entries'] = shift_ids.map(home_ze).fillna(0)
                    total_ze = ze_events.groupby('_shift_id').size()
                    stats['away_zone_entries'] = (shift_ids.map(total_ze).fillna(0) - stats['home_zone_entries']).fillna(0)
                
                zx_events = events_df[events_df['is_zone_exit'] == 1] if 'is_zone_exit' in events_df.columns else pd.DataFrame()
                if len(zx_events) > 0:
                    home_zx = zx_events[zx_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['home_zone_exits'] = shift_ids.map(home_zx).fillna(0)
                    total_zx = zx_events.groupby('_shift_id').size()
                    stats['away_zone_exits'] = (shift_ids.map(total_zx).fillna(0) - stats['home_zone_exits']).fillna(0)
                
                # Giveaways/takeaways
                ga_events = events_df[events_df['is_giveaway'] == 1] if 'is_giveaway' in events_df.columns else pd.DataFrame()
                if len(ga_events) > 0:
                    home_ga = ga_events[ga_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['home_giveaways'] = shift_ids.map(home_ga).fillna(0)
                    total_ga = ga_events.groupby('_shift_id').size()
                    stats['away_giveaways'] = (shift_ids.map(total_ga).fillna(0) - stats['home_giveaways']).fillna(0)
                
                bad_ga_events = events_df[events_df['is_bad_giveaway'] == 1] if 'is_bad_giveaway' in events_df.columns else pd.DataFrame()
                if len(bad_ga_events) > 0:
                    home_bad_ga = bad_ga_events[bad_ga_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['home_bad_giveaways'] = shift_ids.map(home_bad_ga).fillna(0)
                    total_bad_ga = bad_ga_events.groupby('_shift_id').size()
                    stats['away_bad_giveaways'] = (shift_ids.map(total_bad_ga).fillna(0) - stats['home_bad_giveaways']).fillna(0)
                
                ta_events = events_df[events_df['is_takeaway'] == 1] if 'is_takeaway' in events_df.columns else pd.DataFrame()
                if len(ta_events) > 0:
                    home_ta = ta_events[ta_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['home_takeaways'] = shift_ids.map(home_ta).fillna(0)
                    total_ta = ta_events.groupby('_shift_id').size()
                    stats['away_takeaways'] = (shift_ids.map(total_ta).fillna(0) - stats['home_takeaways']).fillna(0)
                
                # Faceoffs
                fo_events = events_df[events_df['is_faceoff'] == 1] if 'is_faceoff' in events_df.columns else pd.DataFrame()
                if len(fo_events) > 0 and 'player_team' in fo_events.columns and 'home_team' in fo_events.columns:
                    home_fo_won = fo_events[fo_events['player_team'] == fo_events['home_team']].groupby('_shift_id').size()
                    stats['fo_won'] = shift_ids.map(home_fo_won).fillna(0)
                    total_fo = fo_events.groupby('_shift_id').size()
                    stats['fo_lost'] = (shift_ids.map(total_fo).fillna(0) - stats['fo_won']).fillna(0)
                    total_fo_sum = stats['fo_won'] + stats['fo_lost']
                    stats['fo_pct'] = (stats['fo_won'] / total_fo_sum * 100).where(total_fo_sum > 0, 0.0)
                
                return stats
            
            # Apply aggregations
            shift_ids = shifts['shift_id']
            aggregated_stats = agg_shift_stats(combined_events, shift_ids)
            
            # Assign to shifts DataFrame
            for col, values in aggregated_stats.items():
                shifts[col] = values
    
    # 7. Create dim tables
    start_types = shifts['shift_start_type_derived'].dropna().unique()
    dim_shift_start_type = pd.DataFrame({
        'shift_start_type_id': [f'SST{i:04d}' for i in range(1, len(start_types)+1)],
        'shift_start_type_name': start_types
    })
    save_table(dim_shift_start_type, 'dim_shift_start_type')
    
    stop_types = shifts['shift_stop_type_derived'].dropna().unique()
    dim_shift_stop_type = pd.DataFrame({
        'shift_stop_type_id': [f'SPT{i:04d}' for i in range(1, len(stop_types)+1)],
        'shift_stop_type_name': stop_types
    })
    save_table(dim_shift_stop_type, 'dim_shift_stop_type')
    
    start_map = dict(zip(dim_shift_start_type['shift_start_type_name'], dim_shift_start_type['shift_start_type_id']))
    stop_map = dict(zip(dim_shift_stop_type['shift_stop_type_name'], dim_shift_stop_type['shift_stop_type_id']))
    shifts['shift_start_type_id'] = shifts['shift_start_type_derived'].map(start_map)
    shifts['shift_stop_type_id'] = shifts['shift_stop_type_derived'].map(stop_map)
    
    situations = shifts['situation'].dropna().unique()
    dim_situation = pd.DataFrame({
        'situation_id': [f'SIT{i:04d}' for i in range(1, len(situations)+1)],
        'situation_name': situations
    })
    save_table(dim_situation, 'dim_situation')
    situation_map = dict(zip(dim_situation['situation_name'], dim_situation['situation_id']))
    shifts['situation_id'] = shifts['situation'].map(situation_map)
    
    shifts['shift_key'] = shifts['shift_id']
    
    save_table(shifts, 'fact_shifts')
    log.info(f"  ✓ fact_shifts: {len(shifts)} rows, {len(shifts.columns)} cols")
    log.info(f"  ✓ Player IDs, plus/minus (5 types), shift stats added")


# ============================================================
# PHASE 5.11B: ENHANCE SHIFT PLAYERS (v19.00 ROOT CAUSE FIX)
# ============================================================

def enhance_shift_players():
    """
    v19.00 ROOT CAUSE FIX: Expand fact_shift_players from 9 to 65+ columns.
    
    This is a TWO-PASS approach:
    - Pass 1: Pull stats from fact_shifts, calculate logical shifts
    - Pass 2: Add rating columns and adjusted stats
    
    LOGICAL SHIFT RULE: Any gap in shift_index = new logical shift
    """
    log.section("PHASE 5.11B: ENHANCE SHIFT PLAYERS (v19.00)")
    
    shift_players_path = OUTPUT_DIR / 'fact_shift_players.csv'
    shifts_path = OUTPUT_DIR / 'fact_shifts.csv'
    
    if not shift_players_path.exists() or not shifts_path.exists():
        log.warn("Required tables not found, skipping shift_players enhancement")
        return
    
    sp = pd.read_csv(shift_players_path, low_memory=False)
    shifts = pd.read_csv(shifts_path, low_memory=False)
    dim_player = pd.read_csv(OUTPUT_DIR / 'dim_player.csv', low_memory=False)
    
    log.info(f"Enhancing {len(sp)} shift-player records...")
    log.info(f"  Source: fact_shifts has {len(shifts.columns)} columns")
    
    # ========================================
    # PASS 1: Pull stats from fact_shifts
    # ========================================
    log.info("  Pass 1: Pulling stats from fact_shifts...")
    
    # VECTORIZED: Merge shift data directly instead of using lookup dict
    # This is much faster than row-by-row lookups
    shifts_for_merge = shifts.set_index('shift_id')
    
    # Columns to pull from fact_shifts (shift-level data)
    time_cols = ['shift_duration', 'shift_start_total_seconds', 'shift_end_total_seconds', 'stoppage_time']
    context_cols = ['situation', 'situation_id', 'strength', 'strength_id', 'start_zone', 'end_zone',
                    'game_state', 'score_differential', 'is_close_game']
    
    # Faceoff columns - fo_won/fo_lost are from home perspective, need venue mapping
    # (home player: fo_won = home wins, away player: fo_won = away wins)
    
    # Corsi/Fenwick/Shot columns need venue mapping (home perspective → player perspective)
    # These are stored in fact_shifts from home team's perspective, but need to be
    # flipped for away team players so their "for" = their team's events
    stat_cols_venue = ['cf', 'ca', 'cf_pct', 'ff', 'fa', 'ff_pct', 'sf', 'sa', 'shot_diff',
                       'scf', 'sca', 'hdf', 'hda']
    # Zone entry/exit and giveaway/takeaway columns (need venue mapping)
    zone_cols = ['home_zone_entries', 'away_zone_entries', 'home_zone_exits', 'away_zone_exits',
                 'home_giveaways', 'away_giveaways', 'home_bad_giveaways', 'away_bad_giveaways',
                 'home_takeaways', 'away_takeaways']
    # Faceoff columns (need venue mapping)
    fo_cols = ['fo_won', 'fo_lost', 'fo_pct']
    stat_cols_direct = ['event_count']
    
    # Rating columns from fact_shifts (team-level)
    rating_cols_shifts = ['home_avg_rating', 'home_min_rating', 'home_max_rating',
                          'away_avg_rating', 'away_min_rating', 'away_max_rating',
                          'rating_differential', 'home_rating_advantage']
    
    # FK columns
    fk_cols = ['period_id', 'season_id', 'home_team_id', 'away_team_id']
    
    # Goal columns need venue mapping
    goal_cols_home = ['home_gf_all', 'home_ga_all', 'home_gf_ev', 'home_ga_ev', 
                      'home_gf_pp', 'home_ga_pp', 'home_gf_pk', 'home_ga_pk',
                      'home_pm_all', 'home_pm_ev']
    goal_cols_away = ['away_gf_all', 'away_ga_all', 'away_gf_ev', 'away_ga_ev',
                      'away_gf_pp', 'away_ga_pp', 'away_gf_pk', 'away_ga_pk',
                      'away_pm_all', 'away_pm_ev']
    
    # Pull direct columns - include goal and stat columns for venue mapping
    all_pull_cols = time_cols + context_cols + stat_cols_direct + rating_cols_shifts + fk_cols
    # Also include goal columns and stat columns needed for venue mapping
    all_pull_cols += goal_cols_home + goal_cols_away + stat_cols_venue + zone_cols + fo_cols
    
    # Filter to only columns that actually exist in shifts_for_merge
    available_cols = [col for col in all_pull_cols if col in shifts_for_merge.columns]
    missing_cols = [col for col in all_pull_cols if col not in shifts_for_merge.columns]
    if missing_cols:
        log.warn(f"  Missing columns in fact_shifts (will be skipped): {missing_cols}")
    
    # VECTORIZED: Merge all columns at once (much faster than row-by-row lookups)
    sp = sp.merge(shifts_for_merge[available_cols], left_on='shift_id', right_index=True, how='left')
    
    # VECTORIZED: Map venue-specific goal columns using np.where
    # Create masks for home vs away
    home_mask = sp['venue'] == 'home'
    away_mask = ~home_mask
    
    # Goals for/against (mapped by venue) - VECTORIZED
    sp['gf'] = np.where(home_mask, 
                       sp['home_gf_all'].fillna(0), 
                       sp['away_gf_all'].fillna(0))
    sp['ga'] = np.where(home_mask,
                       sp['home_ga_all'].fillna(0),
                       sp['away_ga_all'].fillna(0))
    sp['pm'] = sp['gf'] - sp['ga']
    sp['gf_ev'] = np.where(home_mask,
                           sp['home_gf_ev'].fillna(0),
                           sp['away_gf_ev'].fillna(0))
    sp['ga_ev'] = np.where(home_mask,
                           sp['home_ga_ev'].fillna(0),
                           sp['away_ga_ev'].fillna(0))
    sp['gf_pp'] = np.where(home_mask,
                           sp['home_gf_pp'].fillna(0),
                           sp['away_gf_pp'].fillna(0))
    sp['ga_pp'] = np.where(home_mask,
                           sp['home_ga_pp'].fillna(0),
                           sp['away_ga_pp'].fillna(0))
    sp['gf_pk'] = np.where(home_mask,
                           sp['home_gf_pk'].fillna(0),
                           sp['away_gf_pk'].fillna(0))
    sp['ga_pk'] = np.where(home_mask,
                           sp['home_ga_pk'].fillna(0),
                           sp['away_ga_pk'].fillna(0))
    sp['pm_ev'] = np.where(home_mask,
                           sp['home_pm_ev'].fillna(0),
                           sp['away_pm_ev'].fillna(0))
    
    # Team/opponent ratings (mapped by venue) - VECTORIZED
    # Only set if rating columns exist
    if 'home_avg_rating' in sp.columns and 'away_avg_rating' in sp.columns:
        sp['team_avg_rating'] = np.where(home_mask,
                                        sp['home_avg_rating'].fillna(0),
                                        sp['away_avg_rating'].fillna(0))
        sp['opp_avg_rating'] = np.where(home_mask,
                                        sp['away_avg_rating'].fillna(0),
                                        sp['home_avg_rating'].fillna(0))
    else:
        sp['team_avg_rating'] = 0.0
        sp['opp_avg_rating'] = 0.0
    sp['team_id'] = np.where(home_mask,
                            sp['home_team_id'].fillna(''),
                            sp['away_team_id'].fillna(''))
    sp['opp_team_id'] = np.where(home_mask,
                                 sp['away_team_id'].fillna(''),
                                 sp['home_team_id'].fillna(''))
    
    # Corsi/Fenwick/Shot columns (venue-mapped: "for" = player's team, "against" = opponent)
    # fact_shifts stores from home perspective (cf = home corsi, ca = away corsi)
    # For away players, we swap: their cf = shift's ca, their ca = shift's cf
    # VECTORIZED: Use np.where with swap logic
    # IMPORTANT: Store original values before swapping to avoid overwriting
    cf_orig = sp['cf'].fillna(0)
    ca_orig = sp['ca'].fillna(0)
    ff_orig = sp['ff'].fillna(0)
    fa_orig = sp['fa'].fillna(0)
    sf_orig = sp['sf'].fillna(0)
    sa_orig = sp['sa'].fillna(0)
    scf_orig = sp['scf'].fillna(0)
    sca_orig = sp['sca'].fillna(0)
    hdf_orig = sp['hdf'].fillna(0)
    hda_orig = sp['hda'].fillna(0)
    
    # Home players: cf = cf, ca = ca (direct)
    # Away players: cf = ca, ca = cf (swapped)
    sp['cf'] = np.where(home_mask, cf_orig, ca_orig)  # Away: cf = shift's ca
    sp['ca'] = np.where(home_mask, ca_orig, cf_orig)  # Away: ca = shift's cf
    sp['ff'] = np.where(home_mask, ff_orig, fa_orig)  # Away: ff = shift's fa
    sp['fa'] = np.where(home_mask, fa_orig, ff_orig)  # Away: fa = shift's ff
    sp['sf'] = np.where(home_mask, sf_orig, sa_orig)  # Away: sf = shift's sa
    sp['sa'] = np.where(home_mask, sa_orig, sf_orig)  # Away: sa = shift's sf
    sp['scf'] = np.where(home_mask, scf_orig, sca_orig)  # Away: scf = shift's sca
    sp['sca'] = np.where(home_mask, sca_orig, scf_orig)  # Away: sca = shift's scf
    sp['hdf'] = np.where(home_mask, hdf_orig, hda_orig)  # Away: hdf = shift's hda
    sp['hda'] = np.where(home_mask, hda_orig, hdf_orig)  # Away: hda = shift's hdf
    sp['shot_diff'] = sp['sf'] - sp['sa']
    
    # Recalculate percentages (v29.1: vectorized for performance)
    total_cf = sp['cf'] + sp['ca']
    sp['cf_pct'] = (sp['cf'] / total_cf * 100).where(total_cf > 0, 50.0)
    
    total_ff = sp['ff'] + sp['fa']
    sp['ff_pct'] = (sp['ff'] / total_ff * 100).where(total_ff > 0, 50.0)
    
    # Zone entries/exits/giveaways/takeaways - venue mapped - VECTORIZED
    # Home player gets home team's events, away player gets away team's events
    # Reuse home_mask from earlier
    if 'venue' in sp.columns:
        home_mask = sp['venue'] == 'home'
        sp['zone_entries'] = np.where(home_mask, 
                                      sp['home_zone_entries'].fillna(0), 
                                      sp['away_zone_entries'].fillna(0))
        sp['zone_exits'] = np.where(home_mask,
                                    sp['home_zone_exits'].fillna(0),
                                    sp['away_zone_exits'].fillna(0))
        sp['giveaways'] = np.where(home_mask,
                                  sp['home_giveaways'].fillna(0),
                                  sp['away_giveaways'].fillna(0))
        sp['bad_giveaways'] = np.where(home_mask,
                                      sp['home_bad_giveaways'].fillna(0),
                                      sp['away_bad_giveaways'].fillna(0))
        sp['takeaways'] = np.where(home_mask,
                                  sp['home_takeaways'].fillna(0),
                                  sp['away_takeaways'].fillna(0))
        
        # Faceoffs - venue mapped (fo_won/fo_lost are from home perspective in fact_shifts)
        sp['fo_won'] = np.where(home_mask,
                               sp['fo_won'].fillna(0),
                               sp['fo_lost'].fillna(0))
        sp['fo_lost'] = np.where(home_mask,
                                sp['fo_lost'].fillna(0),
                                sp['fo_won'].fillna(0))
    # Faceoff percentage (v29.1: vectorized for performance)
    total_fo = sp['fo_won'] + sp['fo_lost']
    sp['fo_pct'] = (sp['fo_won'] / total_fo * 100).where(total_fo > 0, 0.0)
    
    # Calculate playing time
    sp['playing_time'] = sp['shift_duration'].fillna(0) - sp['stoppage_time'].fillna(0)
    sp['playing_time'] = sp['playing_time'].clip(lower=0)
    
    log.info(f"    Pulled {len(all_pull_cols)} columns from fact_shifts")
    
    # ========================================
    # PASS 1B: Calculate Logical Shifts
    # ========================================
    log.info("  Pass 1B: Calculating logical shifts...")
    
    # Rule: Any gap in shift_index = new logical shift
    sp = sp.sort_values(['game_id', 'player_id', 'shift_index'])
    
    logical_shift_nums = []
    shift_segments = []
    
    prev_game = None
    prev_player = None
    prev_idx = None
    logical_num = 0
    segment = 0
    
    for _, row in sp.iterrows():
        game_id = row['game_id']
        player_id = row['player_id']
        shift_idx = row['shift_index']
        
        # New player-game combination
        if game_id != prev_game or player_id != prev_player:
            logical_num = 1
            segment = 1
        # Same player-game, check for gap
        elif pd.notna(prev_idx) and pd.notna(shift_idx):
            if int(shift_idx) != int(prev_idx) + 1:
                # Gap detected - new logical shift
                logical_num += 1
                segment = 1
            else:
                segment += 1
        else:
            segment += 1
        
        logical_shift_nums.append(logical_num)
        shift_segments.append(segment)
        
        prev_game = game_id
        prev_player = player_id
        prev_idx = shift_idx
    
    sp['logical_shift_number'] = logical_shift_nums
    sp['shift_segment'] = shift_segments
    
    # Calculate is_first_segment and is_last_segment
    sp['is_first_segment'] = sp['shift_segment'] == 1
    
    # For is_last_segment, need to look ahead (groupby approach)
    sp['logical_key'] = sp['game_id'].astype(str) + '_' + sp['player_id'].astype(str) + '_' + sp['logical_shift_number'].astype(str)
    max_segments = sp.groupby('logical_key')['shift_segment'].transform('max')
    sp['is_last_segment'] = sp['shift_segment'] == max_segments
    
    # Calculate logical_shift_duration (sum of all segments in the logical shift)
    logical_durations = sp.groupby('logical_key')['shift_duration'].transform('sum')
    sp['logical_shift_duration'] = logical_durations
    
    # Calculate running TOI within game
    sp['running_toi_game'] = sp.groupby(['game_id', 'player_id'])['shift_duration'].cumsum()
    
    # Drop helper column
    sp = sp.drop(columns=['logical_key'])
    
    unique_logical = sp.groupby(['game_id', 'player_id'])['logical_shift_number'].max()
    log.info(f"    Logical shifts: max per player-game = {unique_logical.max()}, avg = {unique_logical.mean():.1f}")
    
    # ========================================
    # PASS 2: Add Player Ratings
    # ========================================
    log.info("  Pass 2: Adding player ratings and adjusted stats...")
    
    player_rating_map = dict(zip(dim_player['player_id'], dim_player['current_skill_rating']))
    
    # Player's own rating
    sp['player_rating'] = sp['player_id'].map(player_rating_map)
    
    # Quality of competition (opponent avg rating)
    sp['qoc_rating'] = sp['opp_avg_rating']
    
    # Quality of teammates (team avg rating excluding self)
    # Approximation: team_avg - (player_rating / 5) + adjustment
    # For simplicity, use team_avg directly (slight overestimate)
    sp['qot_rating'] = sp['team_avg_rating']
    
    # Competition tier based on opponent rating
    def get_competition_tier(opp_rating):
        if pd.isna(opp_rating):
            return None
        # Match dim_competition_tier: TI01=Elite(5+), TI02=AboveAvg(4-5), TI03=Avg(3-4), TI04=BelowAvg(2-3)
        if opp_rating >= 5.0:
            return 'TI01'  # Elite
        elif opp_rating >= 4.0:
            return 'TI02'  # Above Average
        elif opp_rating >= 3.0:
            return 'TI03'  # Average
        else:
            return 'TI04'  # Below Average
    
    sp['competition_tier_id'] = sp['opp_avg_rating'].apply(get_competition_tier)
    
    # Opponent multiplier for adjusted stats
    # Formula: opp_avg_rating / 4.0 (where 4.0 is midpoint)
    sp['opp_multiplier'] = sp['opp_avg_rating'] / 4.0
    sp['opp_multiplier'] = sp['opp_multiplier'].fillna(1.0)
    
    # ========================================
    # PASS 2B: Calculate Adjusted Stats
    # ========================================
    log.info("  Pass 2B: Calculating adjusted stats...")
    
    # Player's rating differential vs opponents
    if 'opp_avg_rating' in sp.columns:
        sp['player_rating_diff'] = sp['player_rating'] - sp['opp_avg_rating']
    else:
        sp['player_rating_diff'] = 0.0
    
    # Expected CF% based on rating differential
    # Formula: 50 + (rating_diff * 5) where each rating point = 5% CF advantage
    if 'rating_differential' in sp.columns:
        sp['expected_cf_pct'] = 50 + (sp['rating_differential'].fillna(0) * 5)
    else:
        sp['expected_cf_pct'] = 50.0
    sp['expected_cf_pct'] = sp['expected_cf_pct'].clip(30, 70)  # Cap at reasonable bounds
    
    # CF% vs expected
    sp['cf_pct_vs_expected'] = sp['cf_pct'] - sp['expected_cf_pct']
    
    # Performance flag
    def get_performance(row):
        diff = row['cf_pct_vs_expected']
        if pd.isna(diff):
            return None
        if diff > 5:
            return 'Over'
        elif diff < -5:
            return 'Under'
        else:
            return 'Expected'
    
    sp['performance'] = sp.apply(get_performance, axis=1)
    
    # Adjusted Corsi (multiply by opponent multiplier)
    sp['cf_adj'] = sp['cf'] * sp['opp_multiplier']
    sp['ca_adj'] = sp['ca'] / sp['opp_multiplier'].replace(0, 1)
    
    # Adjusted CF%
    total_adj = sp['cf_adj'] + sp['ca_adj']
    sp['cf_pct_adj'] = (sp['cf_adj'] / total_adj * 100).where(total_adj > 0, 50.0)
    
    log.info(f"    Performance distribution: Over={len(sp[sp['performance']=='Over'])}, Expected={len(sp[sp['performance']=='Expected'])}, Under={len(sp[sp['performance']=='Under'])}")
    
    # ========================================
    # Reorder columns
    # ========================================
    # Group A: Identifiers
    id_cols = ['shift_player_id', 'shift_id', 'game_id', 'shift_index', 
               'player_game_number', 'player_id', 'venue', 'position', 'period']
    
    # Group B: Time
    time_cols_out = ['shift_duration', 'shift_start_total_seconds', 'shift_end_total_seconds',
                     'stoppage_time', 'playing_time', 'running_toi_game']
    
    # Group C: Logical shifts
    logical_cols = ['logical_shift_number', 'shift_segment', 'is_first_segment', 
                    'is_last_segment', 'logical_shift_duration']
    
    # Group D: Goals (raw)
    goal_cols = ['gf', 'ga', 'pm', 'gf_ev', 'ga_ev', 'gf_pp', 'ga_pp', 'gf_pk', 'ga_pk', 'pm_ev']
    
    # Group E: Corsi/Fenwick (raw)
    corsi_cols = ['cf', 'ca', 'cf_pct', 'ff', 'fa', 'ff_pct']
    
    # Group F: Shots
    shot_cols = ['sf', 'sa', 'shot_diff']
    
    # Group G: Zone/Events
    zone_event_cols = ['zone_entries', 'zone_exits', 'giveaways', 'takeaways', 'fo_won', 'fo_lost']
    
    # Group H: Context
    context_cols_out = ['situation', 'situation_id', 'strength', 'strength_id', 'start_zone', 'end_zone']
    
    # Group I: Ratings
    rating_cols = ['player_rating', 'team_avg_rating', 'opp_avg_rating', 'rating_differential',
                   'qoc_rating', 'qot_rating', 'competition_tier_id', 'opp_multiplier', 'player_rating_diff']
    
    # Group J: Adjusted stats
    adj_cols = ['expected_cf_pct', 'cf_pct_vs_expected', 'performance', 
                'cf_adj', 'ca_adj', 'cf_pct_adj']
    
    # Group K: FKs
    fk_cols_out = ['team_id', 'opp_team_id', 'season_id', 'period_id']
    
    # Group L: Additional (from shifts)
    extra_cols = ['scf', 'sca', 'hdf', 'hda', 'event_count',
                  'home_avg_rating', 'away_avg_rating', 'home_min_rating', 'away_min_rating',
                  'home_max_rating', 'away_max_rating', 'home_rating_advantage',
                  'home_team_id', 'away_team_id']
    
    # Build ordered column list
    ordered_cols = (id_cols + time_cols_out + logical_cols + goal_cols + corsi_cols + 
                    shot_cols + zone_event_cols + context_cols_out + rating_cols + adj_cols + fk_cols_out)
    
    # Add any remaining columns
    remaining = [c for c in sp.columns if c not in ordered_cols and c not in extra_cols]
    extra_existing = [c for c in extra_cols if c in sp.columns]
    
    final_cols = ordered_cols + extra_existing + remaining
    final_cols = [c for c in final_cols if c in sp.columns]
    
    sp = sp[final_cols]
    
    # Save
    save_table(sp, 'fact_shift_players')
    log.info(f"  ✓ fact_shift_players: {len(sp)} rows, {len(sp.columns)} columns")
    log.info(f"  ✓ Enhanced from 9 to {len(sp.columns)} columns (v19.00 fix)")


# ============================================================
# PHASE 5.12: UPDATE ROSTER POSITIONS FROM SHIFTS
# ============================================================

def update_roster_positions_from_shifts():
    """Build fact_player_game_position and update fact_gameroster positions for tracked games.
    
    For tracked games, position is determined by actual shift data (slot -> position),
    which is more accurate than the BLB-sourced position that may be outdated.
    """
    log.section("PHASE 5.12: UPDATE ROSTER POSITIONS FROM SHIFTS")
    
    shift_players_path = OUTPUT_DIR / 'fact_shift_players.csv'
    roster_path = OUTPUT_DIR / 'fact_gameroster.csv'
    
    if not shift_players_path.exists():
        log.warn("fact_shift_players not found, skipping position update")
        return
    
    shift_players = pd.read_csv(shift_players_path, low_memory=False)
    roster = pd.read_csv(roster_path, low_memory=False)
    
    log.info(f"Building player game positions from {len(shift_players)} shift-player records...")
    
    # Map position code to position name
    # Position column contains: F1, F2, F3, D1, D2, G, X (extra)
    pos_to_name = {
        'F1': 'Forward', 'F2': 'Forward', 'F3': 'Forward',
        'D1': 'Defense', 'D2': 'Defense',
        'G': 'Goalie',
        'X': 'Forward',  # Extra skater is usually a forward
    }
    
    # Ensure logical_shift_number exists
    if 'logical_shift_number' not in shift_players.columns:
        log.warn("logical_shift_number not found in fact_shift_players - using shift_index")
        shift_players['logical_shift_number'] = shift_players.get('shift_index', shift_players.index)
    
    # Build position stats per player-game using LOGICAL SHIFTS
    position_stats = []
    for (game_id, player_id), group in shift_players.groupby(['game_id', 'player_id']):
        if pd.isna(player_id):
            continue
        
        # Count distinct logical shifts (not raw shift rows)
        total_shifts = group['logical_shift_number'].nunique() if 'logical_shift_number' in group.columns else len(group)
        position_counts = {}
        
        # Count position by logical shift (group by logical_shift_number to avoid double-counting segments)
        for logical_shift_num, shift_group in group.groupby('logical_shift_number'):
            # Get position from first segment of this logical shift
            first_row = shift_group.iloc[0]
            pos_code = str(first_row.get('position', ''))
            pos_name = pos_to_name.get(pos_code, 'Unknown')
            position_counts[pos_name] = position_counts.get(pos_name, 0) + 1
        
        # Find dominant position
        if position_counts:
            dominant_pos = max(position_counts, key=position_counts.get)
            dominant_pct = position_counts[dominant_pos] / total_shifts * 100
        else:
            dominant_pos = 'Unknown'
            dominant_pct = 0
        
        position_stats.append({
            'game_id': game_id,
            'player_id': player_id,
            'total_shifts': total_shifts,
            'dominant_position': dominant_pos,
            'dominant_position_pct': round(dominant_pct, 1),
            'forward_shifts': position_counts.get('Forward', 0),
            'defense_shifts': position_counts.get('Defense', 0),
            'goalie_shifts': position_counts.get('Goalie', 0),
        })
    
    # Save fact_player_game_position
    pgp = pd.DataFrame(position_stats)
    save_table(pgp, 'fact_player_game_position')
    log.info(f"  ✓ fact_player_game_position: {len(pgp)} rows")
    
    # Update fact_gameroster positions for tracked games
    if len(pgp) > 0:
        pgp_lookup = pgp.set_index(['game_id', 'player_id'])
        tracked_games = set(pgp['game_id'].unique())
        
        # Position ID mapping
        pos_id_map = {
            'Forward': 'PS0004',
            'Defense': 'PS0005',
            'Goalie': 'PS0006',
        }
        
        updates = 0
        for i, row in roster.iterrows():
            key = (row['game_id'], row['player_id'])
            if row['game_id'] in tracked_games and key in pgp_lookup.index:
                new_pos = pgp_lookup.loc[key, 'dominant_position']
                if new_pos != 'Unknown' and new_pos != row['player_position']:
                    roster.at[i, 'player_position'] = new_pos
                    roster.at[i, 'position_id'] = pos_id_map.get(new_pos)
                    updates += 1
        
        if updates > 0:
            save_table(roster, 'fact_gameroster')
            log.info(f"  ✓ Updated {updates} positions in fact_gameroster from shift data")
        else:
            log.info(f"  No position updates needed")
    
    # Log players with mixed positions
    multi_pos = pgp[pgp['dominant_position_pct'] < 90]
    if len(multi_pos) > 0:
        log.info(f"  Players with <90% dominant position: {len(multi_pos)}")

