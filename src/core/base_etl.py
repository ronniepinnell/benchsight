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

# Import safe CSV utilities (with fallback)
try:
    from src.core.safe_csv import safe_write_csv, safe_read_csv, CSVWriteError
    SAFE_CSV_AVAILABLE = True
except ImportError:
    SAFE_CSV_AVAILABLE = False

# ============================================================
# CONFIGURATION
# ============================================================

BLB_PATH = Path("data/BLB_Tables.xlsx")
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
                has_tracking_index = 'tracking_event_index' in events.columns
                has_enough_rows = len(events) >= 5
                
                if has_tracking_index and has_enough_rows:
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
    """Save table with safe CSV write and return stats."""
    path = OUTPUT_DIR / f"{name}.csv"
    
    if SAFE_CSV_AVAILABLE:
        try:
            safe_write_csv(df, str(path), atomic=True, validate=True)
        except CSVWriteError as e:
            log.error(f"Failed to save {name}: {e}")
            # Fallback to standard write
            df.to_csv(path, index=False)
    else:
        df.to_csv(path, index=False)
    
    return len(df), len(df.columns)

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
    if dim_season_df is not None and 'season' in df.columns:
        # Map season string to season_id
        season_map = {}
        for _, row in dim_season_df.iterrows():
            sid = row.get('season_id', '')
            # Extract year pattern from season_id (e.g., N20232024F -> 20232024)
            if sid:
                year_part = ''.join(c for c in str(sid) if c.isdigit())
                if len(year_part) == 8:
                    season_str = f"{year_part[:4]}-{year_part[4:]}"  # 2023-2024
                    season_map[year_part] = sid
                    season_map[season_str] = sid
                    season_map[year_part.replace('-', '')] = sid  # 20232024
        df['season_id'] = df['season'].astype(str).str.replace('-', '').map(season_map)
    
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
    sheet_map = {
        'dim_player': 'dim_player',
        'dim_team': 'dim_team',
        'dim_league': 'dim_league',
        'dim_season': 'dim_season',
        'dim_schedule': 'dim_schedule',
        'dim_playerurlref': 'dim_playerurlref',
        'dim_rink_zone': 'dim_rink_zone',
        'dim_randomnames': 'dim_randomnames',
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
    
    lookup = {}
    conflicts = []
    
    for _, row in gameroster_df.iterrows():
        game_id = str(row.get('game_id', ''))
        team_name = str(row.get('team_name', '')).strip()
        player_num = str(row.get('player_game_number', '')).strip()
        player_id = row.get('player_id')
        
        if game_id and player_num and pd.notna(player_id):
            # Key includes team to handle duplicate numbers
            key = (game_id, team_name, player_num)
            
            if key in lookup and lookup[key] != player_id:
                conflicts.append(f"Conflict: {key} -> {lookup[key]} vs {player_id}")
            
            lookup[key] = player_id
            
            # Also create key without team for fallback
            simple_key = (game_id, player_num)
            if simple_key not in lookup:
                lookup[simple_key] = player_id
    
    log.info(f"Built lookup with {len(lookup)} mappings")
    
    if conflicts:
        log.warn(f"Found {len(conflicts)} conflicts (duplicate numbers on different teams)")
        for c in conflicts[:5]:
            log.warn(f"  {c}")
    
    return lookup

# ============================================================
# PHASE 3: LOAD TRACKING DATA
# ============================================================

def load_tracking_data(player_lookup):
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
                
                # Filter valid rows (has tracking_event_index)
                if 'tracking_event_index' in df.columns:
                    df = df[df['tracking_event_index'].apply(
                        lambda x: pd.notna(x) and str(x).replace('.', '').replace('-', '').isdigit()
                    )]
                    log.info(f"  events: {len(df)} valid rows (by tracking_event_index)")
                
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
        
        # Generate keys using correct index columns:
        # - event_id uses event_index (sequential event counter)
        # - tracking_event_key uses tracking_event_index (can differ for zone entries, etc.)
        if 'event_index' in df.columns:
            df['event_index_clean'] = df['event_index'].apply(clean_numeric_index)
        else:
            # Fallback if event_index doesn't exist
            df['event_index_clean'] = df['tracking_event_index'].apply(clean_numeric_index)
            log.warning("  Using tracking_event_index as fallback for event_index")
        
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
    
    # 1. fact_events - one row per event
    if 'fact_event_players' in tracking_data:
        log.info("Creating fact_events...")
        tracking = tracking_data['fact_event_players']
        
        # Sort to prioritize Goal > Shot > other event types when selecting representative row
        # This ensures Goal_Scored is selected over Shot_Goal when both exist for same event_id
        event_type_priority = {'Goal': 0, 'Shot': 1, 'Faceoff': 2, 'Pass': 3, 'Possession': 4}
        tracking = tracking.copy()
        tracking['_event_type_priority'] = tracking['event_type'].map(event_type_priority).fillna(99)
        tracking = tracking.sort_values(['event_id', '_event_type_priority', 'player_role'])
        
        events = tracking.groupby('event_id', as_index=False).first()
        events = events.drop(columns=['_event_type_priority'], errors='ignore')
        
        # Select meaningful columns - use standardized names
        # Include all calculated derived columns from calculate_derived_columns
        keep_cols = ['event_id', 'game_id', 'period',
                     'event_type', 'event_detail', 'event_detail_2', 'event_successful',
                     'event_team_zone', 'shift_key', 'linked_event_key',
                     'sequence_key', 'play_key', 'event_chain_key', 'tracking_event_key',
                     'home_team', 'away_team', 'duration',
                     # Time columns (calculated)
                     'event_start_min', 'event_start_sec', 'event_end_min', 'event_end_sec',
                     'time_start_total_seconds', 'time_end_total_seconds',
                     'event_running_start', 'event_running_end',
                     'running_video_time', 'period_start_total_running_seconds',
                     'running_intermission_duration',
                     # Team columns (calculated)
                     'team_venue', 'team_venue_abv', 'player_team',
                     'home_team_zone', 'away_team_zone',
                     # Player columns (calculated)
                     'player_role', 'side_of_puck', 'role_number', 'role_abrev',
                     'player_game_number', 'strength',
                     # Play details
                     'play_detail1', 'play_detail_2', 'play_detail_successful',
                     'pressured_pressurer',
                     # XY data
                     'puck_x_start', 'puck_y_start', 'puck_x_end', 'puck_y_end',
                     'player_x', 'player_y',
                     # Flags
                     'is_goal', 'is_highlight']
        events = events[[c for c in keep_cols if c in events.columns]]
        
        # Add player ID columns from tracking data
        from src.core.key_utils import add_player_id_columns
        events = add_player_id_columns(events, tracking)
        
        # Add FK columns
        events = add_fact_events_fkeys(events, OUTPUT_DIR)
        
        # Reorder columns - keys and FKs first
        priority_cols = ['event_id', 'game_id', 'period', 'period_id',
                        'event_type', 'event_type_id', 
                        'event_detail', 'event_detail_id',
                        'event_detail_2', 'event_detail_2_id',
                        'event_successful', 'success_id',
                        'event_team_zone', 'event_zone_id',
                        'sequence_key', 'play_key', 'event_chain_key', 'tracking_event_key',
                        'shift_key', 'linked_event_key',
                        'home_team', 'home_team_id', 'away_team', 'away_team_id',
                        'duration', 'event_player_ids', 'opp_player_ids']
        other_cols = [c for c in events.columns if c not in priority_cols]
        events = events[[c for c in priority_cols if c in events.columns] + other_cols]
        
        save_table(events, 'fact_events')
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
    
    # 3. fact_shifts - one row per shift
    if 'fact_shifts' in tracking_data:
        log.info("Creating fact_shifts...")
        shifts_tracking = tracking_data['fact_shifts']
        
        shifts = shifts_tracking.drop_duplicates(subset=['shift_id'])
        
        keep_cols = ['shift_id', 'game_id', 'shift_index', 'Period',
                     'shift_start_type', 'shift_stop_type',
                     'shift_start_min', 'shift_start_sec', 'shift_end_min', 'shift_end_sec',
                     'home_team', 'away_team',
                     'home_forward_1', 'home_forward_2', 'home_forward_3',
                     'home_defense_1', 'home_defense_2', 'home_xtra', 'home_goalie',
                     'away_forward_1', 'away_forward_2', 'away_forward_3',
                     'away_defense_1', 'away_defense_2', 'away_xtra', 'away_goalie',
                     # Additional columns needed by enhance_shift_tables
                     'shift_start_total_seconds', 'shift_end_total_seconds', 'shift_duration',
                     'home_team_strength', 'away_team_strength', 'home_team_en', 'away_team_en',
                     'home_team_pk', 'home_team_pp', 'away_team_pp', 'away_team_pk',
                     'situation', 'strength', 'home_goals', 'away_goals',
                     'stoppage_time', 'home_ozone_start', 'home_ozone_end',
                     'home_dzone_start', 'home_dzone_end', 'home_nzone_start', 'home_nzone_end']
        shifts = shifts[[c for c in keep_cols if c in shifts.columns]]
        
        if 'Period' in shifts.columns:
            shifts = shifts.rename(columns={'Period': 'period'})
        
        save_table(shifts, 'fact_shifts')
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
                    
                    rows.append({
                        'shift_player_id': f"{shift['shift_id']}_{venue}_{pos}",
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
    
    # dim_event_type - from models/dimensions.py
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
    log.info(f"dim_event_type: {len(event_types)} rows")
    
    # dim_event_detail - from models/dimensions.py
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
    log.info(f"dim_event_detail: {len(event_details)} rows")
    
    # dim_event_detail_2 - build dynamically from tracking data
    _create_dim_event_detail_2()
    
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
    
    # dim_play_detail - from PLAY_DETAILS constants + tracking data
    _create_dim_play_detail()
    
    # dim_play_detail_2 - from tracking data
    _create_dim_play_detail_2()


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
    """Create dim_zone_entry_type from tracking data."""
    records = []
    tracking_path = OUTPUT_DIR / 'fact_event_players.csv'
    if tracking_path.exists():
        tracking = pd.read_csv(tracking_path, low_memory=False)
        if 'event_detail_2' in tracking.columns:
            ze_codes = tracking[tracking['event_detail_2'].astype(str).str.startswith('ZoneEntry', na=False)]['event_detail_2'].unique()
            codes = sorted(set(str(c).replace('-', '_') for c in ze_codes))
            for i, code in enumerate(codes, 1):
                records.append({
                    'zone_entry_type_id': f'ZE{i:04d}',
                    'zone_entry_type_code': code,
                    'zone_entry_type_name': code.replace('ZoneEntry_', '').replace('_', ' '),
                })
    df = pd.DataFrame(records) if records else pd.DataFrame(columns=['zone_entry_type_id', 'zone_entry_type_code', 'zone_entry_type_name'])
    save_table(df, 'dim_zone_entry_type')
    log.info(f"dim_zone_entry_type: {len(df)} rows")


def _create_dim_zone_exit_type():
    """Create dim_zone_exit_type from tracking data."""
    records = []
    tracking_path = OUTPUT_DIR / 'fact_event_players.csv'
    if tracking_path.exists():
        tracking = pd.read_csv(tracking_path, low_memory=False)
        if 'event_detail_2' in tracking.columns:
            zx_codes = tracking[tracking['event_detail_2'].astype(str).str.startswith('ZoneExit', na=False)]['event_detail_2'].unique()
            codes = sorted(set(str(c).replace('-', '_') for c in zx_codes))
            for i, code in enumerate(codes, 1):
                records.append({
                    'zone_exit_type_id': f'ZX{i:04d}',
                    'zone_exit_type_code': code,
                    'zone_exit_type_name': code.replace('ZoneExit_', '').replace('_', ' '),
                })
    df = pd.DataFrame(records) if records else pd.DataFrame(columns=['zone_exit_type_id', 'zone_exit_type_code', 'zone_exit_type_name'])
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
    """Create dim_giveaway_type from tracking data."""
    records = []
    tracking_path = OUTPUT_DIR / 'fact_event_players.csv'
    if tracking_path.exists():
        tracking = pd.read_csv(tracking_path, low_memory=False)
        if 'event_detail' in tracking.columns:
            giveaway_rows = tracking[tracking['event_type'] == 'Turnover']
            if len(giveaway_rows) > 0 and 'event_detail_2' in tracking.columns:
                codes = sorted(giveaway_rows['event_detail_2'].dropna().unique())
                for i, code in enumerate(codes, 1):
                    records.append({
                        'giveaway_type_id': f'GA{i:04d}',
                        'giveaway_type_code': str(code).replace('-', '_'),
                        'giveaway_type_name': str(code).replace('_', ' '),
                    })
    df = pd.DataFrame(records) if records else pd.DataFrame(columns=['giveaway_type_id', 'giveaway_type_code', 'giveaway_type_name'])
    save_table(df, 'dim_giveaway_type')
    log.info(f"dim_giveaway_type: {len(df)} rows")


def _create_dim_takeaway_type():
    """Create dim_takeaway_type from tracking data."""
    records = []
    tracking_path = OUTPUT_DIR / 'fact_event_players.csv'
    if tracking_path.exists():
        tracking = pd.read_csv(tracking_path, low_memory=False)
        if 'event_detail' in tracking.columns:
            # Takeaways are typically recoveries/steals
            takeaway_rows = tracking[tracking['event_detail'].astype(str).str.contains('Takeaway|Steal|Recovery', case=False, na=False)]
            if len(takeaway_rows) > 0:
                codes = sorted(takeaway_rows['event_detail'].dropna().unique())
                for i, code in enumerate(codes, 1):
                    records.append({
                        'takeaway_type_id': f'TA{i:04d}',
                        'takeaway_type_code': str(code).replace('-', '_'),
                        'takeaway_type_name': str(code).replace('_', ' '),
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
    # This adds is_goal, is_shot, etc. which are needed for sequences/plays
    enhance_events_with_flags()
    
    # Phase 5.7: Create fact_sequences (now has is_goal flag)
    create_fact_sequences()
    
    # Phase 5.8: Create fact_plays (now has is_goal flag)
    create_fact_plays()
    
    # Phase 5.10: Create derived event tables
    create_derived_event_tables()
    
    # Phase 5.11: Enhance shift tables
    enhance_shift_tables()
    
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
    
    # Load required tables
    tracking_path = OUTPUT_DIR / 'fact_event_players.csv'
    events_path = OUTPUT_DIR / 'fact_events.csv'
    
    if not tracking_path.exists() or not events_path.exists():
        log.warn("Event tables not found, skipping enhancement")
        return
    
    tracking = pd.read_csv(tracking_path, low_memory=False)
    events = pd.read_csv(events_path, low_memory=False)
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shifts.csv', low_memory=False)
    players = pd.read_csv(OUTPUT_DIR / 'dim_player.csv', low_memory=False)
    schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv', low_memory=False)
    roster = pd.read_csv(OUTPUT_DIR / 'fact_gameroster.csv', low_memory=False)
    
    log.info(f"Enhancing fact_event_players: {len(tracking)} rows, {len(tracking.columns)} cols")
    log.info(f"Enhancing fact_events: {len(events)} rows, {len(events.columns)} cols")
    
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
    # Create player+game -> position lookup
    roster_pos = {}
    for _, row in roster.iterrows():
        key = (str(row['player_id']), int(row['game_id']))
        pos = row.get('player_position')
        if pd.notna(pos):
            roster_pos[key] = pos_map.get(pos, 4)  # Default to Forward
    
    def get_position(row):
        key = (str(row['player_id']), int(row['game_id']))
        return roster_pos.get(key)
    tracking['position_id'] = tracking.apply(get_position, axis=1)
    
    # 4. shot_type_id
    log.info("  Adding shot_type_id...")
    shot_map = {}
    for _, row in shot_type.iterrows():
        code = row['shot_type_code'].replace('-', '_')
        shot_map[code] = row['shot_type_id']
    tracking['shot_type_id'] = tracking.apply(
        lambda r: shot_map.get(r['event_detail_2']) if r['event_type'] in ['Shot', 'Goal'] else None, axis=1
    )
    
    # 5. zone_entry_type_id
    log.info("  Adding zone_entry_type_id...")
    ze_map = {}
    for _, row in ze_type.iterrows():
        code = row['zone_entry_type_code'].replace('-', '_')
        ze_map[code] = row['zone_entry_type_id']
    
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
    
    # 6. zone_exit_type_id (NEW)
    log.info("  Adding zone_exit_type_id...")
    zx_map = {}
    for _, row in zx_type.iterrows():
        code = row['zone_exit_type_code'].replace('-', '_')
        zx_map[code] = row['zone_exit_type_id']
    
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
    
    # 7. stoppage_type_id (NEW)
    log.info("  Adding stoppage_type_id...")
    stoppage_map = {
        'Stoppage_Play': 'SP0010',  # OTHER
        'Stoppage_Period': 'SP0008',  # PERIOD_END
        'Stoppage_GameEnd': 'SP0008',  # PERIOD_END
        'Stoppage_Freeze': 'SP0005',  # PUCK_FROZEN
        'Stoppage_Goal': 'SP0001',  # GOAL
        'Stoppage_Offside': 'SP0002',  # OFFSIDE
        'Stoppage_Icing': 'SP0003',  # ICING
        'Stoppage_Penalty': 'SP0004',  # PENALTY
    }
    tracking['stoppage_type_id'] = tracking.apply(
        lambda r: stoppage_map.get(r['event_detail']) if r['event_type'] == 'Stoppage' else None, axis=1
    )
    
    # 8. giveaway_type_id (NEW) 
    log.info("  Adding giveaway_type_id...")
    # Map common giveaway patterns
    def get_giveaway_type(row):
        if row['event_type'] != 'Turnover':
            return None
        detail = str(row['event_detail']) if pd.notna(row['event_detail']) else ''
        if 'Giveaway' not in detail:
            return None
        play_det = str(row.get('play_detail1', '')) if pd.notna(row.get('play_detail1')) else ''
        
        if 'PassIntercepted' in play_det:
            return 'GT0007'
        elif 'PassBlocked' in play_det or 'ShotPassLane' in play_det:
            return 'GT0006'
        elif 'PassMissed' in play_det or 'Pass' in play_det:
            return 'GT0008'
        elif 'Battle' in play_det:
            return 'GT0002'
        elif 'Blocked' in play_det or 'ShotBlocked' in play_det:
            return 'GT0009'
        elif 'Clear' in play_det or 'Dump' in play_det:
            return 'GT0001'
        elif 'Misplay' in play_det:
            return 'GT0004'
        else:
            return 'GT0005'  # Other
    tracking['giveaway_type_id'] = tracking.apply(get_giveaway_type, axis=1)
    
    # 9. takeaway_type_id (NEW)
    log.info("  Adding takeaway_type_id...")
    def get_takeaway_type(row):
        if row['event_type'] != 'Turnover':
            return None
        detail = str(row['event_detail']) if pd.notna(row['event_detail']) else ''
        if 'Takeaway' not in detail:
            return None
        play_det = str(row.get('play_detail1', '')) if pd.notna(row.get('play_detail1')) else ''
        
        if 'Intercept' in play_det:
            return 'TA0002'
        elif 'PokeCheck' in play_det or 'Poke' in play_det:
            return 'TA0003'
        elif 'StickCheck' in play_det:
            return 'TA0008'
        elif 'Battle' in play_det:
            return 'TA0001'
        elif 'Recovery' in play_det or 'Retrieval' in play_det:
            return 'TA0005'
        elif 'Strip' in play_det:
            return 'TA0009'
        elif 'Forced' in play_det:
            return 'TA0004'
        else:
            return 'TA0010'  # Other
    tracking['takeaway_type_id'] = tracking.apply(get_takeaway_type, axis=1)
    
    # 10. turnover_type_id (simplified - giveaway or takeaway)
    log.info("  Adding turnover_type_id...")
    def get_to_type(row):
        if row['event_type'] != 'Turnover':
            return None
        detail = str(row['event_detail']) if pd.notna(row['event_detail']) else ''
        if 'Giveaway' in detail:
            return 'TO0007'  # Other Giveaway (general)
        elif 'Takeaway' in detail:
            return 'TO0007'  # Other (general)
        return None
    tracking['turnover_type_id'] = tracking.apply(get_to_type, axis=1)
    
    # 11. pass_type_id
    log.info("  Adding pass_type_id...")
    pass_map = {}
    for _, row in pass_type.iterrows():
        pass_map[row['pass_type_code']] = row['pass_type_id']
    tracking['pass_type_id'] = tracking.apply(
        lambda r: pass_map.get(r['event_detail_2']) if r['event_type'] == 'Pass' else None, axis=1
    )
    
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
        try:
            game_id = int(shift_key[2:7])
            shift_idx = int(shift_key[7:])
            return shift_strength.get((game_id, shift_idx), 'STR0001')
        except Exception as e:
            return None
    tracking['strength_id'] = tracking.apply(get_strength, axis=1)
    
    # 14. Drop unwanted columns
    log.info("  Dropping: role_number, role_abrev, team_venue_abv...")
    for col in ['role_number', 'role_abrev', 'team_venue_abv']:
        if col in tracking.columns:
            tracking = tracking.drop(columns=[col])
    
    # Save enhanced tracking
    tracking.to_csv(tracking_path, index=False)
    log.info(f"  ✓ fact_event_players: {len(tracking)} rows, {len(tracking.columns)} cols")
    
    # Now enhance fact_events (get first row per event from tracking)
    log.info("  Enhancing fact_events from tracking...")
    new_cols = ['player_name', 'season_id', 'position_id', 'shot_type_id', 'zone_entry_type_id', 
                'zone_exit_type_id', 'stoppage_type_id', 'giveaway_type_id', 'takeaway_type_id',
                'turnover_type_id', 'pass_type_id', 'time_bucket_id', 'strength_id']
    
    tracking_first = tracking.groupby('event_id').first().reset_index()
    for col in new_cols:
        if col in tracking_first.columns:
            col_map = dict(zip(tracking_first['event_id'], tracking_first[col]))
            events[col] = events['event_id'].map(col_map)
    
    events.to_csv(events_path, index=False)
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
        
        # Save fact_cycle_events
        cycles_df.to_csv(output_dir / 'fact_cycle_events.csv', index=False)
        log.info(f"  ✓ fact_cycle_events: {len(cycles_df)} rows")
        
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
        tracking.to_csv(output_dir / 'fact_event_players.csv', index=False)
        
        # Update events with cycle_key
        events['cycle_key'] = events['event_id'].map(event_to_cycle)
        events['is_cycle'] = events['cycle_key'].notna().astype(int)
        events.to_csv(output_dir / 'fact_events.csv', index=False)
        
        log.info(f"  ✓ Updated is_cycle flag: {tracking['is_cycle'].sum()} tracking rows, {events['is_cycle'].sum()} event rows")
    else:
        log.warning("  No cycles detected")


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
        
        # Add FKs via event_key
        for col in ['season_id', 'time_bucket_id', 'strength_id']:
            if col in event_lookup:
                pec[col] = pec['event_key'].map(event_lookup[col])
        
        pec.to_csv(pec_path, index=False)
        log.info(f"  ✓ fact_player_event_chains: {len(pec)} rows, {len(pec.columns)} cols")
    
    # 2. Enhance fact_tracking
    log.info("Enhancing fact_tracking...")
    ft_path = OUTPUT_DIR / 'fact_tracking.csv'
    if ft_path.exists():
        ft = pd.read_csv(ft_path, low_memory=False)
        
        # Add FKs via tracking_event_key
        for col in ['season_id', 'time_bucket_id', 'strength_id']:
            if col in tracking_lookup:
                ft[col] = ft['tracking_event_key'].map(tracking_lookup[col])
        
        ft.to_csv(ft_path, index=False)
        log.info(f"  ✓ fact_tracking: {len(ft)} rows, {len(ft.columns)} cols")
    
    # 3. Enhance fact_shot_chains
    log.info("Enhancing fact_shot_chains...")
    ec_path = OUTPUT_DIR / 'fact_shot_chains.csv'
    if ec_path.exists():
        ec = pd.read_csv(ec_path, low_memory=False)
        
        # Add FKs via entry_event_key
        for col in ['time_bucket_id', 'strength_id']:
            if col in event_lookup:
                ec[col] = ec['entry_event_key'].map(event_lookup[col])
        
        # Add shot_type_id via shot_event_key
        if 'shot_type_id' in event_lookup:
            ec['shot_type_id'] = ec['shot_event_key'].map(event_lookup['shot_type_id'])
        
        ec.to_csv(ec_path, index=False)
        log.info(f"  ✓ fact_shot_chains: {len(ec)} rows, {len(ec.columns)} cols")
    
    # 4. Enhance fact_linked_events
    log.info("Enhancing fact_linked_events...")
    le_path = OUTPUT_DIR / 'fact_linked_events.csv'
    if le_path.exists():
        le = pd.read_csv(le_path, low_memory=False)
        
        # Convert LE format to LV format: LE18969009001 -> LV1896909001
        def le_to_lv(le_key):
            if pd.isna(le_key):
                return None
            # LE18969009001 -> LV1896909001
            return 'LV' + le_key[2:7] + le_key[8:]
        
        le['_lv_key'] = le['linked_event_key'].apply(le_to_lv)
        
        # Create lookup by linked_event_key from tracking
        link_fks = tracking[tracking['linked_event_key'].notna()].groupby('linked_event_key').first().reset_index()
        for col in ['time_bucket_id', 'strength_id']:
            if col in link_fks.columns:
                link_map = dict(zip(link_fks['linked_event_key'], link_fks[col]))
                le[col] = le['_lv_key'].map(link_map)
        
        le = le.drop(columns=['_lv_key'], errors='ignore')
        le.to_csv(le_path, index=False)
        log.info(f"  ✓ fact_linked_events: {len(le)} rows, {len(le.columns)} cols")
    
    # 4b. Build fact_cycle_events with zone inference
    log.info("Building fact_cycle_events with zone inference...")
    _build_cycle_events(tracking, events, OUTPUT_DIR, log)
    
    # 5. Enhance fact_scoring_chances
    log.info("Enhancing fact_scoring_chances...")
    sc_path = OUTPUT_DIR / 'fact_scoring_chances.csv'
    if sc_path.exists():
        sc = pd.read_csv(sc_path, low_memory=False)
        
        # scoring_chance_key format: E18969001012 -> event_id format: EV1896901012
        # Need to map game_id + event_index to event_id
        # Create map: (game_id, event_index) -> event_id
        events['event_index_parsed'] = events['event_id'].str.extract(r'EV\d{5}(\d+)')[0].astype(int)
        event_idx_map = {}
        for _, row in events.iterrows():
            key = (row['game_id'], row['event_index_parsed'])
            event_idx_map[key] = row['event_id']
        
        # Map scoring chances to event_ids
        def get_event_id(row):
            # Parse scoring_chance_key: E18969001012 -> game=18969, index=1012
            key = row['scoring_chance_key']
            if pd.isna(key):
                return None
            try:
                game_id = int(key[1:6])
                event_idx = int(key[6:])
                return event_idx_map.get((game_id, event_idx))
            except Exception as e:
                return None
        
        sc['_event_id'] = sc.apply(get_event_id, axis=1)
        
        # Now map FKs
        for col in ['time_bucket_id', 'strength_id', 'shot_type_id']:
            if col in event_lookup:
                sc[col] = sc['_event_id'].map(event_lookup[col])
        
        # Drop temp column
        sc = sc.drop(columns=['_event_id'], errors='ignore')
        
        sc.to_csv(sc_path, index=False)
        log.info(f"  ✓ fact_scoring_chances: {len(sc)} rows, {len(sc.columns)} cols")
    
    # 6. Enhance fact_rush_events
    log.info("Enhancing fact_rush_events...")
    re_path = OUTPUT_DIR / 'fact_rush_events.csv'
    if re_path.exists():
        re = pd.read_csv(re_path, low_memory=False)
        # This is a summary table - likely already has what it needs
        log.info(f"  ✓ fact_rush_events: {len(re)} rows, {len(re.columns)} cols (no changes)")
    
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
    events['is_rush'] = (events['event_detail_2'].str.contains('Rush', na=False) | events['event_detail'].str.contains('Rush', na=False)).astype(int)
    events['is_rebound'] = (events['event_detail'].str.contains('Rebound', na=False) | events['event_detail_2'].str.contains('Rebound', na=False)).astype(int)
    # is_cycle is set by _build_cycle_events based on cycle_key - preserve if already set
    if 'cycle_key' in events.columns:
        events['is_cycle'] = events['cycle_key'].notna().astype(int)
    else:
        events['is_cycle'] = (events['event_detail'].str.contains('Cycle', na=False) | events['event_detail_2'].str.contains('Cycle', na=False)).astype(int)
    # Breakout = successful zone exit (exiting defensive zone with puck control)
    # Using event_detail='Zone_Exit' as primary indicator - covers all games consistently
    # NOTE: Some games also have play_detail1 'Breakout' annotations, but this is inconsistent
    # Legacy logic (inconsistent across games): events['event_detail'].str.contains('Breakout', na=False) | events['play_detail1'].str.contains('Breakout', na=False, case=False)
    events['is_breakout'] = (events['event_detail'] == 'Zone_Exit').astype(int)
    events['is_zone_entry'] = (events['zone_entry_type_id'].notna() | (events['event_detail'] == 'Zone_Entry')).astype(int)
    # Zone exit = event_detail contains 'Zone_Exit' (includes Zone_Exit and Zone_ExitFailed)
    events['is_zone_exit'] = events['event_detail'].str.contains('Zone_Exit', na=False).astype(int)
    events['is_shot'] = events['event_type'].isin(['Shot', 'Goal']).astype(int)
    # Goal = event_type='Goal' AND event_detail='Goal_Scored'
    # Shot_Goal is just the shot that resulted in a goal, not the goal itself
    # Faceoff_AfterGoal is the faceoff after a goal, not a goal
    events['is_goal'] = ((events['event_type'] == 'Goal') & (events['event_detail'] == 'Goal_Scored')).astype(int)
    events['is_save'] = events['event_detail'].str.startswith('Save', na=False).astype(int)
    events['is_turnover'] = (events['event_type'] == 'Turnover').astype(int)
    events['is_giveaway'] = events['giveaway_type_id'].notna().astype(int)
    events['is_takeaway'] = events['takeaway_type_id'].notna().astype(int)
    events['is_faceoff'] = (events['event_type'] == 'Faceoff').astype(int)
    events['is_penalty'] = events['event_detail'].str.contains('Penalty', na=False).astype(int)
    events['is_blocked_shot'] = events['event_detail'].str.contains('Blocked', na=False).astype(int)
    events['is_missed_shot'] = events['event_detail'].isin(['Shot_Missed', 'Shot_MissedPost']).astype(int)
    events['is_deflected'] = (events['event_detail'] == 'Shot_Deflected').astype(int)
    # Shots on goal = shots that reached the goalie (saved or scored)
    # Includes Goal_Scored, Shot_Goal, Shot_OnNetSaved, Shot_OnNet
    events['is_sog'] = events['event_detail'].isin(['Shot_OnNetSaved', 'Shot_OnNet', 'Shot_Goal', 'Goal_Scored']).astype(int)
    
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
    
    events['is_scoring_chance'] = ((events['is_shot'] == 1) | (events['is_goal'] == 1)).astype(int)
    events['is_high_danger'] = (((events['is_shot'] == 1) | (events['is_goal'] == 1)) & (
        (events['is_rebound'] == 1) | events['event_detail_2'].str.contains('Tip|OneTime|Deflect', na=False))).astype(int)
    
    # Pressure
    if 'pressured_pressurer' in first_per_event.columns:
        events['pressured_pressurer'] = events['event_id'].map(dict(zip(first_per_event['event_id'], first_per_event['pressured_pressurer'])))
        events['is_pressured'] = (events['pressured_pressurer'] == 1).astype(int)
    
    # Danger level
    def calc_danger(row):
        if row['is_shot'] != 1 and row['is_goal'] != 1:
            return None
        if row['is_high_danger'] == 1:
            return 'high'
        if row['is_rush'] == 1 or row['event_team_zone'] == 'o':
            return 'medium'
        return 'low'
    events['danger_level'] = events.apply(calc_danger, axis=1)
    events['danger_level_id'] = events['danger_level'].map({'high': 'DL01', 'medium': 'DL02', 'low': 'DL03'})
    
    # Scoring chance key
    sc_events = events[(events['is_shot'] == 1) | (events['is_goal'] == 1)].copy()
    sc_events = sc_events.reset_index(drop=True)
    sc_events['scoring_chance_key'] = 'SC' + sc_events['game_id'].astype(str) + sc_events.index.astype(str).str.zfill(4)
    events['scoring_chance_key'] = events['event_id'].map(dict(zip(sc_events['event_id'], sc_events['scoring_chance_key'])))
    
    save_table(events, 'fact_events')
    log.info(f"  ✓ fact_events: {len(events)} rows, {len(events.columns)} cols")
    log.info(f"    Flags: rush={events['is_rush'].sum()}, rebound={events['is_rebound'].sum()}, shot={events['is_shot'].sum()}, goal={events['is_goal'].sum()}")


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
    rushes['rush_outcome'] = rushes.apply(lambda r: 'goal' if r['is_goal'] == 1 else 'shot' if r['is_shot'] == 1 else 'zone_entry' if r['is_zone_entry'] == 1 else 'other', axis=1)
    save_table(rushes, 'fact_rushes')
    log.info(f"  ✓ fact_rushes: {len(rushes)} rows")
    
    # fact_breakouts - Zone exits (breakouts from defensive zone)
    # Definition: Breakout = Zone_Exit event (successful exit from defensive zone with puck control)
    # Coverage: All 4 games consistently (475 events vs 193 with old play_detail1 logic)
    breakouts = events[events['is_breakout'] == 1].copy()
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
    
    save_table(breakouts, 'fact_breakouts')
    log.info(f"  ✓ fact_breakouts: {len(breakouts)} rows")
    
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
    save_table(faceoffs, 'fact_faceoffs')
    log.info(f"  ✓ fact_faceoffs: {len(faceoffs)} rows")
    
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
    
    # Build lookups
    player_team_map = {}
    for _, r in roster.sort_values('game_id').iterrows():
        player_team_map[r['player_id']] = r['team_name']
    
    roster_lookup = {}
    for _, row in roster.iterrows():
        jersey_str = str(row['player_game_number'])
        key = (row['game_id'], row['team_name'], jersey_str)
        roster_lookup[key] = row['player_id']
    
    # Add event_team to events
    def get_event_team(row):
        player_ids = str(row['event_player_ids']).split(',')
        first_player = player_ids[0].strip() if player_ids else None
        return player_team_map.get(first_player, None)
    
    events['event_team'] = events.apply(get_event_team, axis=1)
    events['is_home_event'] = events['event_team'] == events['home_team']
    
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
    
    shift_events_map = {}
    for i, shift in shifts.iterrows():
        shift_events_map[shift['shift_id']] = get_shift_events(shift, events)
    
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
    
    shifts['shift_start_type_derived'] = [
        derive_start_type(shift_events_map[sid], shifts.loc[i, 'shift_start_type'])
        for i, sid in enumerate(shifts['shift_id'])
    ]
    shifts['shift_stop_type_derived'] = [
        derive_stop_type(shift_events_map[sid], shifts.loc[i, 'shift_stop_type'])
        for i, sid in enumerate(shifts['shift_id'])
    ]
    
    # 3. Derive zones
    def get_start_end_zones(shift_events_df):
        if shift_events_df.empty:
            return None, None
        first_zone = shift_events_df.iloc[-1]['event_team_zone']
        last_zone = shift_events_df.iloc[0]['event_team_zone']
        return first_zone, last_zone
    
    zones_data = [get_start_end_zones(shift_events_map[sid]) for sid in shifts['shift_id']]
    shifts['start_zone'] = [z[0] for z in zones_data]
    shifts['end_zone'] = [z[1] for z in zones_data]
    zone_map = {'o': 1, 'd': 2, 'n': 3}
    shifts['start_zone_id'] = shifts['start_zone'].map(zone_map)
    shifts['end_zone_id'] = shifts['end_zone'].map(zone_map)
    
    # 4. Add player IDs
    player_slots = [
        ('home', 'forward_1'), ('home', 'forward_2'), ('home', 'forward_3'),
        ('home', 'defense_1'), ('home', 'defense_2'), ('home', 'xtra'), ('home', 'goalie'),
        ('away', 'forward_1'), ('away', 'forward_2'), ('away', 'forward_3'),
        ('away', 'defense_1'), ('away', 'defense_2'), ('away', 'xtra'), ('away', 'goalie'),
    ]
    
    for venue, slot in player_slots:
        col_name = f'{venue}_{slot}'
        id_col = f'{col_name}_id'
        player_ids = []
        for i, shift in shifts.iterrows():
            jersey = shift[col_name]
            team = shift[f'{venue}_team']
            game_id = shift['game_id']
            if pd.isna(jersey) or pd.isna(team):
                player_ids.append(None)
            else:
                jersey_str = str(int(jersey))
                key = (game_id, team, jersey_str)
                player_ids.append(roster_lookup.get(key, None))
        shifts[id_col] = player_ids
    
    # 5. Plus/minus
    actual_goals = events[(events['event_detail'] == 'Shot_Goal') | (events['event_detail'] == 'Goal_Scored')].copy()
    actual_goals['scoring_team'] = actual_goals.apply(lambda r: player_team_map.get(str(r['event_player_ids']).split(',')[0].strip(), None), axis=1)
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
        mask = (goals_df['game_id'] == game_id) & \
               (goals_df['period'] == period) & \
               (goals_df['event_total_seconds'] <= start_sec) & \
               (goals_df['event_total_seconds'] >= end_sec)
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
            if is_home_goal:
                shifts.at[i, 'home_gf_all'] += 1
                shifts.at[i, 'away_ga_all'] += 1
            else:
                shifts.at[i, 'away_gf_all'] += 1
                shifts.at[i, 'home_ga_all'] += 1
            if is_ev:
                if is_home_goal:
                    shifts.at[i, 'home_gf_ev'] += 1
                    shifts.at[i, 'away_ga_ev'] += 1
                else:
                    shifts.at[i, 'away_gf_ev'] += 1
                    shifts.at[i, 'home_ga_ev'] += 1
            if is_nen:
                if is_home_goal:
                    shifts.at[i, 'home_gf_nen'] += 1
                    shifts.at[i, 'away_ga_nen'] += 1
                else:
                    shifts.at[i, 'away_gf_nen'] += 1
                    shifts.at[i, 'home_ga_nen'] += 1
            if is_home_pp:
                if is_home_goal:
                    shifts.at[i, 'home_gf_pp'] += 1
                    shifts.at[i, 'away_ga_pk'] += 1
                else:
                    shifts.at[i, 'away_gf_pk'] += 1
                    shifts.at[i, 'home_ga_pp'] += 1
            elif is_home_pk:
                if is_home_goal:
                    shifts.at[i, 'home_gf_pk'] += 1
                    shifts.at[i, 'away_ga_pp'] += 1
                else:
                    shifts.at[i, 'away_gf_pp'] += 1
                    shifts.at[i, 'home_ga_pk'] += 1
    
    for pm_type in pm_types:
        shifts[f'home_pm_{pm_type}'] = shifts[f'home_gf_{pm_type}'] - shifts[f'home_ga_{pm_type}']
        shifts[f'away_pm_{pm_type}'] = shifts[f'away_gf_{pm_type}'] - shifts[f'away_ga_{pm_type}']
    
    # 6. Shift stats
    stat_cols = ['sf', 'sa', 'shot_diff', 'cf', 'ca', 'cf_pct', 'ff', 'fa', 'ff_pct',
                 'scf', 'sca', 'hdf', 'hda', 'zone_entries', 'zone_exits',
                 'giveaways', 'takeaways', 'fo_won', 'fo_lost', 'fo_pct', 'event_count']
    for col in stat_cols:
        shifts[col] = 0 if col not in ['cf_pct', 'ff_pct', 'fo_pct'] else 0.0
    
    for i, shift in shifts.iterrows():
        shift_ev = shift_events_map[shift['shift_id']]
        if shift_ev.empty:
            continue
        shifts.at[i, 'event_count'] = len(shift_ev)
        
        sog = shift_ev[shift_ev['is_sog'] == 1]
        home_sog = sog['is_home_event'].sum()
        shifts.at[i, 'sf'] = home_sog
        shifts.at[i, 'sa'] = len(sog) - home_sog
        shifts.at[i, 'shot_diff'] = shifts.at[i, 'sf'] - shifts.at[i, 'sa']
        
        shot_attempts = shift_ev[(shift_ev['is_shot'] == 1) | (shift_ev['is_blocked_shot'] == 1) | (shift_ev['is_missed_shot'] == 1)]
        home_corsi = shot_attempts['is_home_event'].sum()
        shifts.at[i, 'cf'] = home_corsi
        shifts.at[i, 'ca'] = len(shot_attempts) - home_corsi
        total_corsi = shifts.at[i, 'cf'] + shifts.at[i, 'ca']
        shifts.at[i, 'cf_pct'] = (shifts.at[i, 'cf'] / total_corsi * 100) if total_corsi > 0 else 50.0
        
        fenwick = shift_ev[(shift_ev['is_shot'] == 1) | (shift_ev['is_missed_shot'] == 1)]
        home_fenwick = fenwick['is_home_event'].sum()
        shifts.at[i, 'ff'] = home_fenwick
        shifts.at[i, 'fa'] = len(fenwick) - home_fenwick
        total_fenwick = shifts.at[i, 'ff'] + shifts.at[i, 'fa']
        shifts.at[i, 'ff_pct'] = (shifts.at[i, 'ff'] / total_fenwick * 100) if total_fenwick > 0 else 50.0
        
        sc = shift_ev[shift_ev['is_scoring_chance'] == 1]
        shifts.at[i, 'scf'] = sc['is_home_event'].sum()
        shifts.at[i, 'sca'] = len(sc) - shifts.at[i, 'scf']
        
        hd = shift_ev[shift_ev['is_high_danger'] == 1]
        shifts.at[i, 'hdf'] = hd['is_home_event'].sum()
        shifts.at[i, 'hda'] = len(hd) - shifts.at[i, 'hdf']
        
        shifts.at[i, 'zone_entries'] = shift_ev['is_zone_entry'].sum()
        shifts.at[i, 'zone_exits'] = shift_ev['is_zone_exit'].sum()
        shifts.at[i, 'giveaways'] = shift_ev['is_giveaway'].sum()
        shifts.at[i, 'takeaways'] = shift_ev['is_takeaway'].sum()
        
        faceoffs = shift_ev[shift_ev['is_faceoff'] == 1]
        shifts.at[i, 'fo_won'] = len(faceoffs[faceoffs['event_successful'] == 's'])
        shifts.at[i, 'fo_lost'] = len(faceoffs[faceoffs['event_successful'] == 'u'])
        total_fo = shifts.at[i, 'fo_won'] + shifts.at[i, 'fo_lost']
        shifts.at[i, 'fo_pct'] = (shifts.at[i, 'fo_won'] / total_fo * 100) if total_fo > 0 else 0.0
    
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
    
    # Build position stats per player-game
    position_stats = []
    for (game_id, player_id), group in shift_players.groupby(['game_id', 'player_id']):
        if pd.isna(player_id):
            continue
        
        total_shifts = len(group)
        position_counts = {}
        
        for _, row in group.iterrows():
            pos_code = str(row.get('position', ''))
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

