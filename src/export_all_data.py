#!/usr/bin/env python3
"""
=============================================================================
BENCHSIGHT DIRECT EXPORT SCRIPT
=============================================================================
File: export_all_data.py
Author: BenchSight Team
Created: December 2025

PURPOSE:
    This script directly reads all source data (BLB_Tables.xlsx and game 
    tracking files) and exports complete, updated CSV files to the output
    directory. It bypasses the full ETL pipeline for quick data refresh.

USAGE:
    python export_all_data.py [--games GAME_IDS] [--output-dir PATH]
    
    Examples:
        python export_all_data.py                    # Export all data
        python export_all_data.py --games 18969,18977  # Specific games only
        python export_all_data.py --output-dir ./my_output  # Custom output

DATA FLOW:
    ┌─────────────────────┐     ┌─────────────────────┐
    │   BLB_Tables.xlsx   │     │  Game Tracking      │
    │   (Master Data)     │     │  Excel Files        │
    └──────────┬──────────┘     └──────────┬──────────┘
               │                           │
               ▼                           ▼
    ┌─────────────────────────────────────────────────┐
    │           EXPORT_ALL_DATA.PY                    │
    │  • Load dimensions from BLB_Tables              │
    │  • Load events/shifts from each game            │
    │  • Transform to analytics-ready format          │
    │  • Calculate derived stats                      │
    │  • Export to CSV                                │
    └──────────────────────┬──────────────────────────┘
                           │
                           ▼
    ┌─────────────────────────────────────────────────┐
    │              OUTPUT CSVs                        │
    │  • dim_player.csv      • fact_events.csv        │
    │  • dim_team.csv        • fact_shifts.csv        │
    │  • dim_schedule.csv    • fact_box_score.csv     │
    │  • dim_*.csv           • fact_*.csv             │
    └─────────────────────────────────────────────────┘

OUTPUT FILES:
    Dimension Tables (dim_*):
        - dim_player.csv      : All players with ratings, positions
        - dim_team.csv        : All teams
        - dim_schedule.csv    : Full season schedule
        - dim_period.csv      : Period definitions (1, 2, 3, OT)
        - dim_event_type.csv  : Event type lookup
        - dim_zone.csv        : Zone definitions (OZ, NZ, DZ)
        
    Fact Tables (fact_*):
        - fact_events.csv           : All events from all games
        - fact_shifts.csv           : All shifts from all games  
        - fact_event_players.csv    : Player-event mapping (long format)
        - fact_shift_players.csv    : Player-shift mapping (long format)
        - fact_box_score.csv        : Aggregated player stats per game
        - fact_game_summary.csv     : Game-level aggregates

DEPENDENCIES:
    - pandas >= 1.5.0
    - openpyxl >= 3.0.0 (for Excel reading)

=============================================================================
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import warnings

# Suppress openpyxl warnings about styles
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# =============================================================================
# IMPORTS - Check for required packages
# =============================================================================

try:
    import pandas as pd
    print(f"✓ pandas {pd.__version__} loaded")
except ImportError:
    print("✗ pandas not found. Install with: pip install pandas")
    sys.exit(1)

try:
    import openpyxl
    print(f"✓ openpyxl {openpyxl.__version__} loaded")
except ImportError:
    print("✗ openpyxl not found. Install with: pip install openpyxl")
    sys.exit(1)


# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    """
    Configuration settings for the export script.
    
    Attributes:
        PROJECT_ROOT: Base directory of the project
        DATA_DIR: Directory containing all data files
        BLB_FILE: Path to BLB_Tables.xlsx master file
        GAMES_DIR: Directory containing game tracking folders
        OUTPUT_DIR: Directory where CSVs will be written
    """
    
    # Automatically detect project root (where this script lives)
    PROJECT_ROOT = Path(__file__).parent
    
    # Data directories
    DATA_DIR = PROJECT_ROOT / 'data'
    BLB_FILE = DATA_DIR / 'BLB_Tables.xlsx'
    GAMES_DIR = DATA_DIR / 'raw' / 'games'
    OUTPUT_DIR = DATA_DIR / 'output'
    
    # Export settings
    EXPORT_TIMESTAMP = datetime.now().isoformat()
    
    # Column mappings for flexible Excel parsing
    # Maps various column name variants to standardized names
    EVENT_COLUMN_VARIANTS = {
        'event_type': ['event_type', 'event_type_', 'Type', 'type', 'EVENT_TYPE'],
        'event_index': ['event_index', 'tracking_event_index', 'idx', 'index'],
        'team': ['team', 'team_', 'event_team', 'Team'],
        'period': ['period', 'period_', 'Period'],
        'zone': ['zone', 'event_team_zone', 'Zone'],
        'success': ['success', 'event_successful', 'successful'],
        'detail_1': ['detail_1', 'event_detail', 'detail1', 'd1'],
        'detail_2': ['detail_2', 'event_detail_2', 'detail2', 'd2'],
        'clock_start': ['clock_start', 'time_start', 'start_time'],
        'clock_end': ['clock_end', 'time_end', 'end_time'],
        'player_number': ['player_number', 'player_game_number', 'jersey', 'number'],
        'player_role': ['player_role', 'role'],
        'shift_index': ['shift_index', 'shift_id'],
        'video_time': ['running_video_time', 'video_time', 'video_seconds'],
    }
    
    SHIFT_COLUMN_VARIANTS = {
        'shift_index': ['shift_index', 'shift_id', 'idx'],
        'period': ['period', 'Period'],
        'start': ['start', 'shift_start', 'start_time'],
        'end': ['end', 'shift_end', 'end_time'],
        'start_type': ['start_type', 'shift_start_type'],
        'stop_type': ['stop_type', 'shift_stop_type', 'end_type'],
    }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_column(df: pd.DataFrame, variants: List[str], default: str = None) -> Optional[str]:
    """
    Find a column in a DataFrame by checking multiple possible names.
    
    This handles the inconsistency in column naming across different
    tracking files (e.g., 'team' vs 'team_' vs 'event_team').
    
    Args:
        df: DataFrame to search
        variants: List of possible column names to check
        default: Default column name if none found
        
    Returns:
        The first matching column name, or default if none found
        
    Example:
        >>> col = get_column(df, ['team', 'team_', 'event_team'])
        >>> if col:
        ...     teams = df[col]
    """
    for variant in variants:
        if variant in df.columns:
            return variant
    return default


def safe_get(df: pd.DataFrame, variants: List[str]) -> pd.Series:
    """
    Safely get a column from DataFrame, returning empty Series if not found.
    
    Args:
        df: DataFrame to search
        variants: List of possible column names
        
    Returns:
        The column as a Series, or an empty Series if not found
    """
    col = get_column(df, variants)
    if col and col in df.columns:
        return df[col]
    return pd.Series([None] * len(df))


def parse_time_to_seconds(time_str) -> Optional[int]:
    """
    Convert a time string (MM:SS or M:SS) to total seconds.
    
    Args:
        time_str: Time in format "MM:SS" or "M:SS" or numeric seconds
        
    Returns:
        Total seconds as integer, or None if unparseable
        
    Examples:
        >>> parse_time_to_seconds("15:30")
        930
        >>> parse_time_to_seconds("5:45")
        345
        >>> parse_time_to_seconds(120)
        120
    """
    if pd.isna(time_str):
        return None
    
    # If already numeric, return as-is
    if isinstance(time_str, (int, float)):
        return int(time_str)
    
    # Parse MM:SS format
    try:
        parts = str(time_str).split(':')
        if len(parts) == 2:
            minutes, seconds = int(parts[0]), int(parts[1])
            return minutes * 60 + seconds
        elif len(parts) == 1:
            return int(float(parts[0]))
    except (ValueError, TypeError):
        pass
    
    return None


def log(message: str, level: str = "INFO"):
    """
    Print a timestamped log message.
    
    Args:
        message: The message to log
        level: Log level (INFO, WARN, ERROR, SUCCESS)
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    icons = {"INFO": "ℹ️", "WARN": "⚠️", "ERROR": "❌", "SUCCESS": "✅"}
    icon = icons.get(level, "•")
    print(f"[{timestamp}] {icon} {message}")


# =============================================================================
# DATA LOADING FUNCTIONS
# =============================================================================

def load_blb_tables(blb_path: Path) -> Dict[str, pd.DataFrame]:
    """
    Load all sheets from BLB_Tables.xlsx master file.
    
    The BLB_Tables.xlsx file contains master data for the league:
        - dim_player: Player roster with IDs, names, ratings
        - dim_team: Team information
        - dim_schedule: Season schedule with game IDs
        - fact_gameroster: Which players played in which games
        - Various other dimension and fact tables
    
    Args:
        blb_path: Path to BLB_Tables.xlsx
        
    Returns:
        Dictionary mapping sheet names to DataFrames
        
    Raises:
        FileNotFoundError: If BLB_Tables.xlsx doesn't exist
    """
    log(f"Loading BLB_Tables from {blb_path}")
    
    if not blb_path.exists():
        raise FileNotFoundError(f"BLB_Tables.xlsx not found at {blb_path}")
    
    # Load all sheets
    xl = pd.ExcelFile(blb_path)
    tables = {}
    
    for sheet_name in xl.sheet_names:
        try:
            df = pd.read_excel(xl, sheet_name=sheet_name)
            tables[sheet_name] = df
            log(f"  Loaded {sheet_name}: {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            log(f"  Failed to load {sheet_name}: {e}", "WARN")
    
    return tables


def find_tracking_file(game_dir: Path) -> Optional[Path]:
    """
    Find the tracking Excel file within a game directory.
    
    Tracking files follow naming patterns like:
        - {game_id}_tracking.xlsx
        - _tracking.xlsx
        - tracking.xlsx
    
    Args:
        game_dir: Path to the game directory (e.g., data/raw/games/18969/)
        
    Returns:
        Path to the tracking file, or None if not found
    """
    # Try common patterns
    patterns = [
        f"{game_dir.name}_tracking.xlsx",
        "_tracking.xlsx",
        "tracking.xlsx",
        "*tracking*.xlsx"
    ]
    
    for pattern in patterns:
        matches = list(game_dir.glob(pattern))
        # Filter out temp files (start with ~$)
        matches = [m for m in matches if not m.name.startswith('~$')]
        if matches:
            return matches[0]
    
    return None


def load_game_tracking(game_dir: Path) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Load events, shifts, and roster from a game tracking file.
    
    Each tracking Excel file contains multiple sheets:
        - events: All tracked events (passes, shots, faceoffs, etc.)
        - shifts: Line changes and on-ice personnel
        - game_rosters: Players who participated in the game
    
    Args:
        game_dir: Path to the game directory
        
    Returns:
        Tuple of (events_df, shifts_df, roster_df), any may be None
    """
    tracking_file = find_tracking_file(game_dir)
    
    if not tracking_file:
        log(f"  No tracking file found in {game_dir.name}", "WARN")
        return None, None, None
    
    log(f"  Loading {tracking_file.name}")
    
    try:
        xl = pd.ExcelFile(tracking_file)
        
        # Load events sheet
        events_df = None
        for sheet in ['events', 'Events', 'EVENTS']:
            if sheet in xl.sheet_names:
                events_df = pd.read_excel(xl, sheet_name=sheet)
                break
        
        # Load shifts sheet
        shifts_df = None
        for sheet in ['shifts', 'Shifts', 'SHIFTS']:
            if sheet in xl.sheet_names:
                shifts_df = pd.read_excel(xl, sheet_name=sheet)
                break
        
        # Load roster sheet
        roster_df = None
        for sheet in ['game_rosters', 'roster', 'Roster', 'game_roster']:
            if sheet in xl.sheet_names:
                roster_df = pd.read_excel(xl, sheet_name=sheet)
                break
        
        return events_df, shifts_df, roster_df
        
    except Exception as e:
        log(f"  Error loading {tracking_file.name}: {e}", "ERROR")
        return None, None, None


# =============================================================================
# DATA TRANSFORMATION FUNCTIONS
# =============================================================================

def standardize_events(events_df: pd.DataFrame, game_id: str) -> pd.DataFrame:
    """
    Standardize event data from various column naming conventions.
    
    Different tracking files may use different column names. This function
    maps them all to a consistent schema.
    
    Standard Schema:
        - game_id: Unique game identifier
        - event_index: Event sequence number within game
        - event_type: Type of event (Shot, Pass, Faceoff, etc.)
        - period: Game period (1, 2, 3, OT)
        - clock_start: Time when event started (seconds)
        - clock_end: Time when event ended (seconds)
        - zone: Ice zone (OZ, NZ, DZ)
        - team: Team that initiated the event (home/away)
        - success: Whether event was successful (1/0)
        - detail_1: Primary detail (shot type, pass type, etc.)
        - detail_2: Secondary detail
        - shift_index: Associated shift
        - player_number: Jersey number of primary player
        - player_role: Role in event (evt_1, evt_2, opp_1, etc.)
    
    Args:
        events_df: Raw events DataFrame from Excel
        game_id: Game identifier to add
        
    Returns:
        Standardized DataFrame
    """
    if events_df is None or len(events_df) == 0:
        return pd.DataFrame()
    
    cv = Config.EVENT_COLUMN_VARIANTS
    
    # Build standardized DataFrame
    std_df = pd.DataFrame()
    std_df['game_id'] = game_id
    std_df['event_index'] = safe_get(events_df, cv['event_index'])
    std_df['event_type'] = safe_get(events_df, cv['event_type'])
    std_df['period'] = safe_get(events_df, cv['period'])
    std_df['zone'] = safe_get(events_df, cv['zone'])
    std_df['team'] = safe_get(events_df, cv['team'])
    std_df['success'] = safe_get(events_df, cv['success'])
    std_df['detail_1'] = safe_get(events_df, cv['detail_1'])
    std_df['detail_2'] = safe_get(events_df, cv['detail_2'])
    std_df['shift_index'] = safe_get(events_df, cv['shift_index'])
    std_df['player_number'] = safe_get(events_df, cv['player_number'])
    std_df['player_role'] = safe_get(events_df, cv['player_role'])
    std_df['video_time'] = safe_get(events_df, cv['video_time'])
    
    # Parse clock times to seconds
    clock_start_col = get_column(events_df, cv['clock_start'])
    clock_end_col = get_column(events_df, cv['clock_end'])
    
    if clock_start_col:
        std_df['clock_start_seconds'] = events_df[clock_start_col].apply(parse_time_to_seconds)
    else:
        std_df['clock_start_seconds'] = None
        
    if clock_end_col:
        std_df['clock_end_seconds'] = events_df[clock_end_col].apply(parse_time_to_seconds)
    else:
        std_df['clock_end_seconds'] = None
    
    # Add processing metadata
    std_df['_source_file'] = f"{game_id}_tracking.xlsx"
    std_df['_export_timestamp'] = Config.EXPORT_TIMESTAMP
    
    return std_df


def standardize_shifts(shifts_df: pd.DataFrame, game_id: str) -> pd.DataFrame:
    """
    Standardize shift data from various column naming conventions.
    
    Standard Schema:
        - game_id: Unique game identifier
        - shift_index: Shift sequence number
        - period: Game period
        - start_seconds: Shift start time in seconds
        - end_seconds: Shift end time in seconds
        - duration_seconds: Shift length
        - start_type: How shift started (faceoff, on-the-fly)
        - stop_type: How shift ended (whistle, change)
        - home_f1 through home_g: Home player jersey numbers
        - away_f1 through away_g: Away player jersey numbers
    
    Args:
        shifts_df: Raw shifts DataFrame from Excel
        game_id: Game identifier to add
        
    Returns:
        Standardized DataFrame
    """
    if shifts_df is None or len(shifts_df) == 0:
        return pd.DataFrame()
    
    cv = Config.SHIFT_COLUMN_VARIANTS
    
    # Build standardized DataFrame
    std_df = pd.DataFrame()
    std_df['game_id'] = game_id
    std_df['shift_index'] = safe_get(shifts_df, cv['shift_index'])
    std_df['period'] = safe_get(shifts_df, cv['period'])
    std_df['start_type'] = safe_get(shifts_df, cv['start_type'])
    std_df['stop_type'] = safe_get(shifts_df, cv['stop_type'])
    
    # Parse times
    start_col = get_column(shifts_df, cv['start'])
    end_col = get_column(shifts_df, cv['end'])
    
    if start_col:
        std_df['start_seconds'] = shifts_df[start_col].apply(parse_time_to_seconds)
    if end_col:
        std_df['end_seconds'] = shifts_df[end_col].apply(parse_time_to_seconds)
    
    # Calculate duration
    if 'start_seconds' in std_df.columns and 'end_seconds' in std_df.columns:
        std_df['duration_seconds'] = std_df['end_seconds'] - std_df['start_seconds']
    
    # Player slots - look for home_f1, home_f2, etc.
    for team in ['home', 'away']:
        for pos in ['f1', 'f2', 'f3', 'd1', 'd2', 'g', 'x']:
            col_name = f"{team}_{pos}"
            variants = [col_name, col_name.upper(), f"{team.upper()}_{pos.upper()}"]
            std_df[col_name] = safe_get(shifts_df, variants)
    
    # Add metadata
    std_df['_source_file'] = f"{game_id}_tracking.xlsx"
    std_df['_export_timestamp'] = Config.EXPORT_TIMESTAMP
    
    return std_df


def pivot_events_to_wide(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert long-format events (one row per player) to wide format (one row per event).
    
    The tracking files store events in "long" format where each player involved
    in an event gets their own row. This function pivots to "wide" format where
    each event is a single row with columns for each player role.
    
    Long format (input):
        event_index | player_number | player_role
        1           | 17            | evt_1
        1           | 9             | evt_2
        1           | 22            | opp_1
        
    Wide format (output):
        event_index | evt_1_number | evt_2_number | opp_1_number
        1           | 17           | 9            | 22
    
    Args:
        events_df: Long-format events DataFrame
        
    Returns:
        Wide-format events DataFrame (one row per event)
    """
    if events_df is None or len(events_df) == 0:
        return pd.DataFrame()
    
    # Identify the grouping columns (everything except player-specific)
    group_cols = [c for c in events_df.columns 
                  if c not in ['player_number', 'player_role', 'play_detail1', 'play_detail2']]
    
    # Get unique events
    events_wide = events_df[group_cols].drop_duplicates(subset=['game_id', 'event_index'])
    
    # Pivot player data
    if 'player_role' in events_df.columns and 'player_number' in events_df.columns:
        player_pivot = events_df.pivot_table(
            index=['game_id', 'event_index'],
            columns='player_role',
            values='player_number',
            aggfunc='first'
        ).reset_index()
        
        # Rename pivot columns
        player_pivot.columns = [f"{c}_number" if c not in ['game_id', 'event_index'] else c 
                                for c in player_pivot.columns]
        
        # Merge back
        events_wide = events_wide.merge(player_pivot, on=['game_id', 'event_index'], how='left')
    
    return events_wide


def calculate_box_score(events_df: pd.DataFrame, shifts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate player box score statistics from events and shifts.
    
    Computes standard hockey statistics for each player in each game:
        - Goals (G): Shots that scored
        - Assists (A): Primary and secondary assists  
        - Points (PTS): G + A
        - Shots on Goal (SOG): Shots that reached the goalie
        - Plus/Minus (+/-): Goals for minus goals against while on ice
        - Time on Ice (TOI): Total seconds played
        - Penalty Minutes (PIM): Minutes in penalty box
    
    Args:
        events_df: Standardized events DataFrame
        shifts_df: Standardized shifts DataFrame
        
    Returns:
        Box score DataFrame with one row per player per game
    """
    if events_df is None or len(events_df) == 0:
        return pd.DataFrame()
    
    box_scores = []
    
    for game_id in events_df['game_id'].unique():
        game_events = events_df[events_df['game_id'] == game_id]
        game_shifts = shifts_df[shifts_df['game_id'] == game_id] if shifts_df is not None else None
        
        # Get all players in this game
        players = game_events['player_number'].dropna().unique()
        
        for player_num in players:
            player_events = game_events[game_events['player_number'] == player_num]
            
            # Calculate stats
            goals = len(player_events[
                (player_events['event_type'].isin(['Shot', 'SHOT'])) & 
                (player_events['success'] == 1) &
                (player_events['player_role'].isin(['evt_1', 'shooter']))
            ])
            
            shots = len(player_events[
                (player_events['event_type'].isin(['Shot', 'SHOT'])) &
                (player_events['player_role'].isin(['evt_1', 'shooter']))
            ])
            
            # Primary assists (evt_2 on goals)
            primary_assists = len(player_events[
                (player_events['event_type'].isin(['Shot', 'SHOT'])) &
                (player_events['success'] == 1) &
                (player_events['player_role'] == 'evt_2')
            ])
            
            # Secondary assists (evt_3 on goals)
            secondary_assists = len(player_events[
                (player_events['event_type'].isin(['Shot', 'SHOT'])) &
                (player_events['success'] == 1) &
                (player_events['player_role'] == 'evt_3')
            ])
            
            assists = primary_assists + secondary_assists
            points = goals + assists
            
            # Calculate TOI from shifts
            toi_seconds = 0
            if game_shifts is not None and len(game_shifts) > 0:
                for _, shift in game_shifts.iterrows():
                    # Check if player was in this shift
                    for col in ['home_f1', 'home_f2', 'home_f3', 'home_d1', 'home_d2',
                               'away_f1', 'away_f2', 'away_f3', 'away_d1', 'away_d2']:
                        if col in shift and shift[col] == player_num:
                            if pd.notna(shift.get('duration_seconds')):
                                toi_seconds += shift['duration_seconds']
                            break
            
            box_scores.append({
                'game_id': game_id,
                'player_number': player_num,
                'goals': goals,
                'assists': assists,
                'points': points,
                'shots': shots,
                'primary_assists': primary_assists,
                'secondary_assists': secondary_assists,
                'toi_seconds': toi_seconds,
                'toi_minutes': round(toi_seconds / 60, 2) if toi_seconds else 0
            })
    
    return pd.DataFrame(box_scores)


# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

def export_dataframe(df: pd.DataFrame, output_path: Path, name: str):
    """
    Export a DataFrame to CSV with logging.
    
    Args:
        df: DataFrame to export
        output_path: Directory to write to
        name: Filename (without .csv extension)
    """
    if df is None or len(df) == 0:
        log(f"  Skipping {name}.csv (empty)", "WARN")
        return
    
    filepath = output_path / f"{name}.csv"
    df.to_csv(filepath, index=False)
    log(f"  Exported {name}.csv: {len(df)} rows")


def run_export(games: Optional[List[str]] = None, output_dir: Optional[Path] = None):
    """
    Main export function - loads all data and exports to CSV.
    
    This is the primary entry point for the export process. It:
    1. Loads dimension tables from BLB_Tables.xlsx
    2. Finds and loads all game tracking files
    3. Standardizes the data formats
    4. Calculates derived statistics
    5. Exports everything to CSV
    
    Args:
        games: Optional list of game IDs to process (None = all games)
        output_dir: Optional output directory (None = default)
    """
    log("=" * 60)
    log("BENCHSIGHT DATA EXPORT")
    log("=" * 60)
    
    # Setup paths
    output_path = output_dir or Config.OUTPUT_DIR
    output_path.mkdir(parents=True, exist_ok=True)
    
    # ==========================================================================
    # STEP 1: Load BLB_Tables (master dimension data)
    # ==========================================================================
    log("\n[STEP 1] Loading BLB_Tables...")
    try:
        blb_tables = load_blb_tables(Config.BLB_FILE)
    except FileNotFoundError as e:
        log(str(e), "ERROR")
        return
    
    # ==========================================================================
    # STEP 2: Export dimension tables from BLB_Tables
    # ==========================================================================
    log("\n[STEP 2] Exporting dimension tables...")
    
    # Map BLB sheet names to output file names
    dim_mappings = {
        'dim_player': 'dim_player',
        'dim_team': 'dim_team', 
        'dim_schedule': 'dim_schedule',
        'dim_season': 'dim_season',
        'dim_venue': 'dim_venue',
        'dim_position': 'dim_position',
        'dim_event_type': 'dim_event_type',
        'dim_zone': 'dim_zone',
        'dim_strength': 'dim_strength',
        'dim_period': 'dim_period',
        'dim_shot_type': 'dim_shot_type',
        'dim_pass_type': 'dim_pass_type',
        'dim_danger_zone': 'dim_danger_zone',
        'dim_skill_tier': 'dim_skill_tier',
        'dim_play_detail': 'dim_play_detail',
        'dim_event_detail': 'dim_event_detail',
    }
    
    for blb_name, output_name in dim_mappings.items():
        if blb_name in blb_tables:
            export_dataframe(blb_tables[blb_name], output_path, output_name)
    
    # ==========================================================================
    # STEP 3: Find and load all game tracking files
    # ==========================================================================
    log("\n[STEP 3] Loading game tracking data...")
    
    all_events = []
    all_shifts = []
    all_rosters = []
    
    # Find all game directories
    if not Config.GAMES_DIR.exists():
        log(f"Games directory not found: {Config.GAMES_DIR}", "ERROR")
        return
    
    game_dirs = sorted([d for d in Config.GAMES_DIR.iterdir() 
                        if d.is_dir() and d.name.isdigit()])
    
    # Filter to specific games if requested
    if games:
        game_dirs = [d for d in game_dirs if d.name in games]
    
    log(f"  Found {len(game_dirs)} game directories")
    
    for game_dir in game_dirs:
        game_id = game_dir.name
        log(f"\n  Processing game {game_id}...")
        
        events_df, shifts_df, roster_df = load_game_tracking(game_dir)
        
        if events_df is not None and len(events_df) > 0:
            std_events = standardize_events(events_df, game_id)
            all_events.append(std_events)
            log(f"    Events: {len(std_events)} rows")
        
        if shifts_df is not None and len(shifts_df) > 0:
            std_shifts = standardize_shifts(shifts_df, game_id)
            all_shifts.append(std_shifts)
            log(f"    Shifts: {len(std_shifts)} rows")
        
        if roster_df is not None and len(roster_df) > 0:
            roster_df['game_id'] = game_id
            all_rosters.append(roster_df)
            log(f"    Roster: {len(roster_df)} rows")
    
    # ==========================================================================
    # STEP 4: Combine and export fact tables
    # ==========================================================================
    log("\n[STEP 4] Combining and exporting fact tables...")
    
    # Combine all events
    if all_events:
        combined_events = pd.concat(all_events, ignore_index=True)
        log(f"  Total events: {len(combined_events)} rows from {len(all_events)} games")
        
        # Export long format (one row per player per event)
        export_dataframe(combined_events, output_path, 'fact_events_long')
        
        # Export wide format (one row per event)
        events_wide = pivot_events_to_wide(combined_events)
        export_dataframe(events_wide, output_path, 'fact_events')
    else:
        combined_events = pd.DataFrame()
        log("  No events to export", "WARN")
    
    # Combine all shifts
    if all_shifts:
        combined_shifts = pd.concat(all_shifts, ignore_index=True)
        log(f"  Total shifts: {len(combined_shifts)} rows from {len(all_shifts)} games")
        export_dataframe(combined_shifts, output_path, 'fact_shifts')
    else:
        combined_shifts = pd.DataFrame()
        log("  No shifts to export", "WARN")
    
    # Combine all rosters
    if all_rosters:
        combined_rosters = pd.concat(all_rosters, ignore_index=True)
        export_dataframe(combined_rosters, output_path, 'fact_game_rosters')
    
    # ==========================================================================
    # STEP 5: Calculate and export derived tables
    # ==========================================================================
    log("\n[STEP 5] Calculating derived statistics...")
    
    # Box scores
    if len(combined_events) > 0:
        box_scores = calculate_box_score(combined_events, combined_shifts)
        export_dataframe(box_scores, output_path, 'fact_box_score_calculated')
        log(f"  Box scores: {len(box_scores)} player-game rows")
    
    # Game summary
    if len(combined_events) > 0:
        game_summary = combined_events.groupby('game_id').agg({
            'event_index': 'count',
            'event_type': lambda x: x.value_counts().to_dict()
        }).reset_index()
        game_summary.columns = ['game_id', 'total_events', 'event_breakdown']
        
        if len(combined_shifts) > 0:
            shift_counts = combined_shifts.groupby('game_id').size().reset_index(name='total_shifts')
            game_summary = game_summary.merge(shift_counts, on='game_id', how='left')
        
        export_dataframe(game_summary, output_path, 'fact_game_summary')
    
    # ==========================================================================
    # STEP 6: Export existing fact tables from BLB_Tables
    # ==========================================================================
    log("\n[STEP 6] Exporting BLB fact tables...")
    
    fact_mappings = {
        'fact_gameroster': 'fact_gameroster_blb',
        'fact_box_score': 'fact_box_score_blb',
        'fact_draft': 'fact_draft',
        'fact_registration': 'fact_registration',
        'fact_leadership': 'fact_leadership',
    }
    
    for blb_name, output_name in fact_mappings.items():
        if blb_name in blb_tables:
            export_dataframe(blb_tables[blb_name], output_path, output_name)
    
    # ==========================================================================
    # COMPLETE
    # ==========================================================================
    log("\n" + "=" * 60)
    log("EXPORT COMPLETE", "SUCCESS")
    log(f"Output directory: {output_path}")
    log(f"Total files: {len(list(output_path.glob('*.csv')))}")
    log("=" * 60)


# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================

def main():
    """
    Command line entry point.
    
    Usage:
        python export_all_data.py                     # Export all
        python export_all_data.py --games 18969,18977 # Specific games
        python export_all_data.py --output-dir ./out  # Custom output
    """
    parser = argparse.ArgumentParser(
        description='Export BenchSight data to CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python export_all_data.py                     Export all games
  python export_all_data.py --games 18969       Export single game
  python export_all_data.py --games 18969,18977 Export multiple games
  python export_all_data.py --output-dir ./out  Custom output directory
        """
    )
    
    parser.add_argument(
        '--games', 
        type=str, 
        default=None,
        help='Comma-separated list of game IDs to export (default: all)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for CSV files (default: data/output/)'
    )
    
    args = parser.parse_args()
    
    # Parse game list
    games = None
    if args.games:
        games = [g.strip() for g in args.games.split(',')]
    
    # Parse output directory
    output_dir = None
    if args.output_dir:
        output_dir = Path(args.output_dir)
    
    # Run export
    run_export(games=games, output_dir=output_dir)


if __name__ == '__main__':
    main()
