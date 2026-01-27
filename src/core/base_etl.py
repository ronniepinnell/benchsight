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
    add_fact_events_fkeys, add_fact_event_players_fkeys
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
# MODULARIZED ETL PHASES (v6.7.0)
# ============================================================
# Import functions from extracted modules - called directly in main()
from src.core.etl_phases.utilities import (
    drop_underscore_columns,
    drop_index_and_unnamed,
    drop_all_null_columns,
    clean_numeric_index,
    validate_key,
    save_table,
    correct_venue_from_schedule,
)
from src.core.etl_phases.derived_columns import calculate_derived_columns
from src.core.etl_phases.validation import validate_all
from src.core.etl_phases.reference_tables import create_reference_tables
from src.core.etl_phases.event_enhancers import (
    enhance_event_tables,
    enhance_events_with_flags,
    enhance_derived_event_tables,
)
from src.core.etl_phases.shift_enhancers import (
    enhance_shift_tables,
    enhance_shift_players,
    update_roster_positions_from_shifts,
)
from src.core.etl_phases.derived_event_tables import (
    create_derived_event_tables,
    create_fact_sequences,
    create_fact_plays,
)

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
            # VECTORIZED: Use vectorized operations instead of iterrows
            season_map = {}
            if len(dim_season_df) > 0:
                # Direct season value mappings
                season_map.update(dict(zip(dim_season_df['season'].astype(str), dim_season_df['season_id'])))
                season_map.update(dict(zip(dim_season_df['season'].astype(str).str.replace('-', ''), dim_season_df['season_id'])))
                
                # Extract year patterns from season_id (e.g., N20232024F -> 20232024)
                season_ids_str = dim_season_df['season_id'].astype(str)
                year_parts = season_ids_str.str.replace(r'\D', '', regex=True)
                mask_8digits = year_parts.str.len() == 8
                if mask_8digits.any():
                    year_parts_8 = year_parts[mask_8digits]
                    season_ids_8 = dim_season_df.loc[mask_8digits, 'season_id']
                    season_map.update(dict(zip(year_parts_8, season_ids_8)))
                    # Add formatted versions (2023-2024)
                    season_strs = year_parts_8.str[:4] + '-' + year_parts_8.str[4:]
                    season_map.update(dict(zip(season_strs, season_ids_8)))
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

            # Convert date to date-only string to prevent timezone issues in dashboard
            # (midnight UTC dates display as previous day in US Mountain Time)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
                log.info(f"  Converted date column to date-only format (YYYY-MM-DD)")
        
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
        
        # Reorder columns - keys, FKs, then values
        key_cols = ['event_id', 'game_id', 'player_id', 'player_game_number',
                    'sequence_key', 'play_key', 'shift_key', 'linked_event_key',
                    'tracking_event_key', 'zone_change_key']
        fk_id_cols = ['period_id', 'event_type_id', 'event_detail_id', 'event_detail_2_id',
                      'event_success_id', 'event_zone_id', 'home_zone_id', 'away_zone_id',
                      'home_team_id', 'away_team_id', 'player_team_id', 'team_venue_id',
                      'player_role_id', 'play_detail_id', 'play_detail_2_id', 'play_success_id']
        priority_cols = key_cols + fk_id_cols
        other_cols = [c for c in df.columns if c not in priority_cols]
        df = df[[c for c in priority_cols if c in df.columns] + other_cols]
        
        # v23.0: Remove unused flag columns (redundant index systems)
        unused_cols = [
            'event_index_flag', 'sequence_index_flag', 'play_index_flag',
            'assist_to_goal_index_flag', 'assist_primary_event_index_flag',
            'assist_secondary_event_index_flag', 'linked_event_index_flag'
        ]
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
    """Link player_id using lookup, handling team for duplicates.

    For opp_player roles, uses the OPPOSITE team since team_venue represents
    which team has possession, not which team the player is on.
    """

    def get_player_id(row):
        game_id = str(row.get('game_id', ''))
        player_num = str(row.get(player_col, '')).strip()

        if not game_id or not player_num:
            return None

        # Try with team first (more accurate)
        team = str(row.get(team_col, '')).strip()
        if team:
            # Check if this is an opp_player role - they're on the OPPOSITE team
            player_role = str(row.get('player_role', '')).strip()
            is_opp_player = player_role.startswith('opp_')

            # Map venue to team name, flipping for opp_player roles
            if team.lower() in ['home', 'h']:
                if is_opp_player:
                    team = str(row.get('away_team', '')).strip()  # Opposite team
                else:
                    team = str(row.get('home_team', '')).strip()
            elif team.lower() in ['away', 'a']:
                if is_opp_player:
                    team = str(row.get('home_team', '')).strip()  # Opposite team
                else:
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
    from src.core.data_loader import load_blb_tables, build_player_lookup, load_tracking_data
    loaded = load_blb_tables()
    
    # Phase 2: Build player lookup
    player_lookup = build_player_lookup(loaded['fact_gameroster'])
    
    # Phase 3: Load tracking data (needed for dynamic dims)
    tracking_data = load_tracking_data(player_lookup)
    
    # Phase 4: Create reference tables (uses tracking data for dynamic dims)
    create_reference_tables(OUTPUT_DIR, log, save_output_table)

    # Phase 5: Create derived tables (uses dim tables for FKs)
    create_derived_tables(tracking_data, player_lookup)

    # Phase 5.5: Enhance event tables with derived FKs
    enhance_event_tables(
        OUTPUT_DIR, log,
        table_store_available=TABLE_STORE_AVAILABLE,
        get_table_from_store=get_table_from_store if TABLE_STORE_AVAILABLE else None
    )

    # Phase 5.6: Enhance derived event tables
    enhance_derived_event_tables(OUTPUT_DIR, log)

    # Phase 5.9: Enhance events with flags (before sequences)
    enhance_events_with_flags(OUTPUT_DIR, log, save_output_table)

    # Phase 5.7: Create fact_sequences (now has is_goal flag)
    create_fact_sequences(OUTPUT_DIR, log, save_output_table)

    # Phase 5.8: Create fact_plays (now has is_goal flag)
    create_fact_plays(OUTPUT_DIR, log, save_output_table)

    # Phase 5.10: Create derived event tables
    create_derived_event_tables(OUTPUT_DIR, log, save_output_table)

    # Phase 5.11: Enhance shift tables
    enhance_shift_tables(OUTPUT_DIR, log, save_output_table)

    # Phase 5.11B: Enhance shift players (v19.00)
    enhance_shift_players(OUTPUT_DIR, log, save_output_table)

    # Phase 5.12: Update roster positions from shifts
    update_roster_positions_from_shifts(OUTPUT_DIR, log, save_output_table)

    # Phase 6: Validate
    valid = validate_all(OUTPUT_DIR, VALID_TRACKING_GAMES, log)
    
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
