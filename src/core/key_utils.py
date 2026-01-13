#!/usr/bin/env python3
"""
BENCHSIGHT - Key Formatting and Data Normalization
===================================================

Central module for all key generation and data normalization.
Used by base_etl.py and etl_unified.py to ensure consistency.

Key Format Standard:
    {PREFIX}{game_id}{index:05d}
    
    Examples:
    - EV1896901000 (event)
    - SH1896900001 (shift)
    - LV1896909001 (linked event)
    - SQ1896905001 (sequence)
    - PL1896906001 (play)
    - ZC1896900001 (zone change)

Data Normalization:
    - Replace hyphens (-) with underscores (_)
    - Replace slashes (/) with underscores (_)
    - Fix common typos (Seperate -> Separate)
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict


# =============================================================================
# KEY PREFIXES
# =============================================================================

KEY_PREFIXES = {
    'event': 'EV',
    'tracking_event': 'TV',
    'linked_event': 'LV',
    'shift': 'SH',
    'sequence': 'SQ',
    'play': 'PL',
    'zone_change': 'ZC',
    'event_player': 'EP',
    'goalie_game': 'GK',
}


# =============================================================================
# KEY FORMATTING
# =============================================================================

def format_key(prefix: str, game_id, index) -> Optional[str]:
    """
    Create standardized key format: {prefix}{gameid}{index:05d}
    
    Args:
        prefix: 2-letter key prefix (e.g., 'EV', 'SH')
        game_id: Game identifier (int or string)
        index: Event/shift/etc index (int, float, or string)
    
    Returns:
        Formatted key string or None if inputs invalid
    
    Examples:
        format_key('EV', 18969, 1000) -> 'EV1896901000'
        format_key('SH', '18969', '1') -> 'SH1896900001'
        format_key('EV', None, 1000) -> None
    """
    if pd.isna(game_id) or pd.isna(index):
        return None
    try:
        game_id_int = int(game_id)
        index_int = int(float(index))
        return f"{prefix}{game_id_int}{index_int:05d}"
    except (ValueError, TypeError):
        return None


def generate_event_id(row) -> Optional[str]:
    """Generate event_id from row with game_id and event_index."""
    return format_key('EV', row.get('game_id'), row.get('event_index'))


def generate_shift_id(row) -> Optional[str]:
    """Generate shift_id from row with game_id and shift_index."""
    return format_key('SH', row.get('game_id'), row.get('shift_index'))


def generate_tracking_event_key(row) -> Optional[str]:
    """Generate tracking_event_key from row."""
    return format_key('TV', row.get('game_id'), row.get('tracking_event_index'))


def generate_linked_event_key(row) -> Optional[str]:
    """Generate linked_event_key from row."""
    return format_key('LV', row.get('game_id'), row.get('linked_event_index'))


def generate_sequence_key(row) -> Optional[str]:
    """Generate sequence_key from row."""
    return format_key('SQ', row.get('game_id'), row.get('sequence_index'))


def generate_play_key(row) -> Optional[str]:
    """Generate play_key from row."""
    return format_key('PL', row.get('game_id'), row.get('play_index'))


def generate_shift_key(row) -> Optional[str]:
    """Generate shift_key from row (for linking, not PK)."""
    return format_key('SH', row.get('game_id'), row.get('shift_index'))


def generate_zone_change_key(row) -> Optional[str]:
    """Generate zone_change_key from row."""
    return format_key('ZC', row.get('game_id'), row.get('zone_change_index'))


# =============================================================================
# DATA NORMALIZATION
# =============================================================================

def normalize_code(value) -> Optional[str]:
    """
    Normalize a code value for dimension lookup.
    
    - Replace hyphens with underscores
    - Replace slashes with underscores
    - Fix common typos
    
    Args:
        value: String value to normalize
    
    Returns:
        Normalized string or None if input is null
    """
    if pd.isna(value):
        return None
    
    value = str(value)
    
    # Replace separators
    value = value.replace('-', '_')
    value = value.replace('/', '_')
    
    # Fix common typos
    value = value.replace('Seperate', 'Separate')
    
    return value


def normalize_dataframe_codes(df: pd.DataFrame, columns: list = None) -> pd.DataFrame:
    """
    Normalize code columns in a dataframe.
    
    Args:
        df: DataFrame to normalize
        columns: List of columns to normalize (default: auto-detect detail columns)
    
    Returns:
        DataFrame with normalized columns
    """
    if columns is None:
        # Auto-detect columns that typically need normalization
        columns = [c for c in df.columns if any(x in c.lower() for x in 
                   ['detail', 'type', 'play_detail', 'event_detail', 'event_type'])]
    
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(normalize_code)
    
    return df


# =============================================================================
# PLAYER ID AGGREGATION
# =============================================================================

def build_event_player_lookup(tracking_df: pd.DataFrame) -> Dict[str, Dict[str, str]]:
    """
    Build lookup of event_id -> player IDs from tracking data.
    
    Uses player_role to classify (works with string or ID):
    - event_player_1 through event_player_6, event_goalie: event team players
    - opp_player_1 through opp_player_6, opp_goalie: opponent team players
    
    Also supports player_role_id numeric format:
    - role_id 1-7: event team players
    - role_id 8-14: opponent team players
    
    Args:
        tracking_df: fact_event_players dataframe with event_id, player_id, and player_role or player_role_id
    
    Returns:
        Dict with 'event' and 'opp' sub-dicts mapping event_id -> comma-separated player IDs
    """
    if tracking_df is None or tracking_df.empty:
        return {'event': {}, 'opp': {}}
    
    if 'event_id' not in tracking_df.columns or 'player_id' not in tracking_df.columns:
        return {'event': {}, 'opp': {}}
    
    # Determine which column to use for role classification
    has_role_id = 'player_role_id' in tracking_df.columns and tracking_df['player_role_id'].notna().any()
    has_role_str = 'player_role' in tracking_df.columns and tracking_df['player_role'].notna().any()
    
    if not has_role_id and not has_role_str:
        return {'event': {}, 'opp': {}}
    
    # Filter to rows with player data
    player_data = tracking_df[tracking_df['player_id'].notna()].copy()
    
    if player_data.empty:
        return {'event': {}, 'opp': {}}
    
    # Classify by role
    def is_event_team(row):
        if has_role_id and pd.notna(row.get('player_role_id')):
            role_id = str(row['player_role_id'])
            # Handle both numeric (1-7) and PR format (PR01-PR07)
            if role_id.startswith('PR'):
                num = int(role_id[2:])
                return 1 <= num <= 7
            else:
                return 1 <= float(role_id) <= 7
        if has_role_str and pd.notna(row.get('player_role')):
            role = str(row['player_role']).lower()
            return role.startswith('event_player') or role == 'event_goalie'
        return False
    
    def is_opp_team(row):
        if has_role_id and pd.notna(row.get('player_role_id')):
            role_id = str(row['player_role_id'])
            # Handle both numeric (8-14) and PR format (PR08-PR14)
            if role_id.startswith('PR'):
                num = int(role_id[2:])
                return 8 <= num <= 14
            else:
                return 8 <= float(role_id) <= 14
        if has_role_str and pd.notna(row.get('player_role')):
            role = str(row['player_role']).lower()
            return role.startswith('opp_player') or role == 'opp_goalie'
        return False
    
    player_data['is_event_team'] = player_data.apply(is_event_team, axis=1)
    player_data['is_opp_team'] = player_data.apply(is_opp_team, axis=1)
    
    # Build lookups
    event_players = {}
    opp_players = {}
    
    for event_id, group in player_data.groupby('event_id'):
        # Event team players (sorted for consistency)
        event_team = group[group['is_event_team']]['player_id'].dropna().unique()
        if len(event_team) > 0:
            event_players[event_id] = ','.join(sorted(event_team))
        
        # Opponent team players
        opp_team = group[group['is_opp_team']]['player_id'].dropna().unique()
        if len(opp_team) > 0:
            opp_players[event_id] = ','.join(sorted(opp_team))
    
    return {'event': event_players, 'opp': opp_players}


def add_player_id_columns(events_df: pd.DataFrame, tracking_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add event_player_ids and opp_player_ids columns to events dataframe.
    
    Args:
        events_df: fact_events dataframe
        tracking_df: fact_event_players dataframe
    
    Returns:
        events_df with new columns added
    """
    lookup = build_event_player_lookup(tracking_df)
    
    events_df['event_player_ids'] = events_df['event_id'].map(lookup.get('event', {}))
    events_df['opp_player_ids'] = events_df['event_id'].map(lookup.get('opp', {}))
    
    return events_df


# =============================================================================
# COLUMN TRANSFORMATIONS
# =============================================================================

def add_all_keys(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all composite keys to a tracking dataframe.
    
    Adds: event_id, tracking_event_key, linked_event_key, sequence_key, 
          play_key, shift_key, zone_change_key
    
    Requires: game_id and respective index columns
    """
    # Primary event ID
    if 'tracking_event_index' in df.columns or 'event_index' in df.columns:
        if 'event_index' not in df.columns:
            df['event_index'] = df['tracking_event_index']
        df['event_id'] = df.apply(generate_event_id, axis=1)
    
    # Tracking event key - use tracking_event_index if available, else fall back to event_index
    if 'tracking_event_index' in df.columns:
        df['tracking_event_key'] = df.apply(generate_tracking_event_key, axis=1)
    elif 'event_index' in df.columns:
        # Fallback: use event_index to generate tracking_event_key
        df['tracking_event_key'] = df.apply(
            lambda row: format_key('TV', row.get('game_id'), row.get('event_index')), axis=1
        )
    
    # Linked event key
    if 'linked_event_index' in df.columns:
        df['linked_event_key'] = df.apply(generate_linked_event_key, axis=1)
    
    # Sequence key
    if 'sequence_index' in df.columns:
        df['sequence_key'] = df.apply(generate_sequence_key, axis=1)
    
    # Play key
    if 'play_index' in df.columns:
        df['play_key'] = df.apply(generate_play_key, axis=1)
    
    # Shift key (for linking)
    if 'shift_index' in df.columns:
        df['shift_key'] = df.apply(generate_shift_key, axis=1)
    
    # Zone change key
    if 'zone_change_index' in df.columns:
        df['zone_change_key'] = df.apply(generate_zone_change_key, axis=1)
    
    return df


def rename_standard_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename columns to standard names.
    """
    renames = {
        'Type': 'event_type',
        'detail_1': 'event_detail',
        'detail_2': 'event_detail_2',
        'success': 'event_successful',
    }
    
    for old, new in renames.items():
        if old in df.columns and new not in df.columns:
            df = df.rename(columns={old: new})
    
    return df


def normalize_player_role(value) -> Optional[str]:
    """
    Normalize player_role to match dim_player_role.role_code.
    
    event_team_player_1 -> event_player_1
    opp_team_player_1 -> opp_player_1
    """
    if pd.isna(value):
        return None
    value = str(value).strip()
    value = value.replace('_team_', '_')
    return value


# =============================================================================
# SEQUENCE AND PLAY GENERATION
# =============================================================================

# Events that END a sequence (whistle/stoppage)
SEQUENCE_END_EVENTS = ['Stoppage', 'Goal', 'Penalty', 'GameEnd', 'Intermission', 'DeadIce', 'Timeout', 'Clockstop']

# Events/details that END a play (possession change or zone change)
PLAY_END_DETAILS = [
    # Possession changes
    'Turnover_Giveaway', 'Turnover_Takeaway',
    # Zone transitions  
    'Zone_Entry', 'Zone_Exit',
    'Zone_Entryfailed', 'Zone_ExitFailed',
]


def generate_sequences_and_plays(df: pd.DataFrame) -> pd.DataFrame:
    """
    Auto-generate sequence_key and play_key for tracking data.
    
    SEQUENCE: Continuous stretch of play between whistles.
    - Starts: After stoppage (on faceoff or first event after whistle)
    - Ends: On stoppage events (Goal, Penalty, Stoppage, etc.)
    
    PLAY: One possession stretch within a zone (sub-unit of sequence).
    - Ends: On possession change (turnover) or zone transition (entry/exit)
    
    Args:
        df: DataFrame with event_type, event_detail, game_id columns
        
    Returns:
        DataFrame with sequence_key and play_key populated
    """
    if df is None or df.empty:
        return df
    
    # Ensure we have required columns
    required = ['game_id', 'event_type']
    if not all(c in df.columns for c in required):
        return df
    
    # Sort by game and event order
    df = df.copy()
    sort_cols = ['game_id']
    if 'tracking_event_index' in df.columns:
        sort_cols.append('tracking_event_index')
    
    df = df.sort_values(sort_cols)
    
    # First, build sequence/play assignments at the EVENT level (deduplicated)
    # Get unique events
    event_cols = ['game_id', 'event_type', 'event_detail']
    if 'tracking_event_index' in df.columns:
        event_cols.append('tracking_event_index')
    elif 'event_id' in df.columns:
        event_cols.append('event_id')
    
    events = df[event_cols].drop_duplicates()
    events = events.sort_values(sort_cols)
    
    # Build lookup: event -> (sequence_num, play_num)
    event_assignments = {}
    
    for game_id in events['game_id'].unique():
        game_events = events[events['game_id'] == game_id]
        
        sequence_num = 0
        play_num = 0
        in_sequence = False
        
        for _, row in game_events.iterrows():
            event_type = str(row['event_type']) if pd.notna(row['event_type']) else ''
            event_detail = str(row['event_detail']) if pd.notna(row['event_detail']) else ''
            
            # Get event key for lookup
            if 'tracking_event_index' in row:
                event_key = (game_id, row['tracking_event_index'])
            else:
                event_key = (game_id, row.get('event_id'))
            
            # Check if this event ENDS a sequence
            is_sequence_end = event_type in SEQUENCE_END_EVENTS
            
            # Check if this event ENDS a play (within sequence)
            is_play_end = event_detail in PLAY_END_DETAILS
            
            # Check if this is a faceoff (starts new sequence)
            is_faceoff = event_type == 'Faceoff' or event_detail.startswith('Faceoff')
            
            # Sequence logic
            if is_faceoff:
                sequence_num += 1
                play_num = 1
                in_sequence = True
            elif not in_sequence and event_type not in ['GameStart', 'Intermission', '']:
                # Start sequence on first real event if not already in one
                sequence_num += 1
                play_num = 1
                in_sequence = True
            
            if in_sequence:
                event_assignments[event_key] = (sequence_num, play_num)
                
                if is_sequence_end:
                    in_sequence = False
                elif is_play_end:
                    play_num += 1
    
    # Apply assignments to all rows
    def get_sequence(row):
        game_id = row['game_id']
        if 'tracking_event_index' in row and pd.notna(row.get('tracking_event_index')):
            key = (game_id, row['tracking_event_index'])
        elif 'event_id' in row:
            key = (game_id, row.get('event_id'))
        else:
            return None, None
        return event_assignments.get(key, (None, None))
    
    df['_seq_play'] = df.apply(get_sequence, axis=1)
    df['sequence_num'] = df['_seq_play'].apply(lambda x: x[0] if x else None)
    df['play_num'] = df['_seq_play'].apply(lambda x: x[1] if x else None)
    df = df.drop(columns=['_seq_play'])
    
    # Generate keys from sequence/play numbers
    df['sequence_key'] = df.apply(
        lambda r: format_key('SQ', r['game_id'], int(r['sequence_num'])) 
                  if pd.notna(r.get('sequence_num')) else None,
        axis=1
    )
    
    # Play key: unique within game (sequence * 100 + play_num)
    df['play_key'] = df.apply(
        lambda r: format_key('PL', r['game_id'], int(r['sequence_num'] or 0) * 100 + int(r['play_num'] or 0))
                  if pd.notna(r.get('sequence_num')) and pd.notna(r.get('play_num')) else None,
        axis=1
    )
    
    # Drop temporary columns
    df = df.drop(columns=['sequence_num', 'play_num'], errors='ignore')
    
    return df


# =============================================================================
# FK POPULATION FOR FACT_EVENTS
# =============================================================================

def add_fact_events_fkeys(df: pd.DataFrame, output_dir) -> pd.DataFrame:
    """
    Add foreign key columns to fact_events.
    
    Adds:
    - period_id → dim_period
    - event_type_id → dim_event_type
    - event_detail_id → dim_event_detail
    - event_detail_2_id → dim_event_detail_2
    - success_id → dim_success
    - event_zone_id → dim_zone
    - home_team_id → dim_team
    - away_team_id → dim_team
    
    Args:
        df: fact_events DataFrame
        output_dir: Path to output directory with dim tables
        
    Returns:
        DataFrame with FK columns added
    """
    from pathlib import Path
    output_dir = Path(output_dir)
    
    # Build lookups from dim tables
    lookups = {}
    
    # dim_period: period number -> period_id
    try:
        dim = pd.read_csv(output_dir / 'dim_period.csv', dtype=str)
        # Period 1 -> P01, etc
        lookups['period'] = {str(i): f"P{i:02d}" for i in range(1, 6)}
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['period'] = {}
    
    # dim_event_type: event_type_code -> event_type_id
    try:
        dim = pd.read_csv(output_dir / 'dim_event_type.csv', dtype=str)
        lookups['event_type'] = dict(zip(dim['event_type_code'], dim['event_type_id']))
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['event_type'] = {}
    
    # dim_event_detail: event_detail_code -> event_detail_id
    try:
        dim = pd.read_csv(output_dir / 'dim_event_detail.csv', dtype=str)
        lookups['event_detail'] = dict(zip(dim['event_detail_code'], dim['event_detail_id']))
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['event_detail'] = {}
    
    # dim_event_detail_2: event_detail_2_code -> event_detail_2_id
    try:
        dim = pd.read_csv(output_dir / 'dim_event_detail_2.csv', dtype=str)
        lookups['event_detail_2'] = dict(zip(dim['event_detail_2_code'], dim['event_detail_2_id']))
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['event_detail_2'] = {}
    
    # dim_success: success_code -> success_id
    # Also build mapping for True/False values
    try:
        dim = pd.read_csv(output_dir / 'dim_success.csv', dtype=str)
        lookups['success'] = dict(zip(dim['success_code'], dim['success_id']))
        # Add boolean mappings: True -> SC01 (Successful), False -> SC02 (Unsuccessful)
        lookups['success_bool'] = {True: 'SC01', 'True': 'SC01', False: 'SC02', 'False': 'SC02'}
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['success'] = {}
        lookups['success_bool'] = {}
    
    # dim_zone: zone_code -> zone_id (uppercase)
    # Also build mapping for full names
    try:
        dim = pd.read_csv(output_dir / 'dim_zone.csv', dtype=str)
        lookups['zone'] = dict(zip(dim['zone_code'].str.upper(), dim['zone_id']))
        # Also add lowercase
        lookups['zone'].update({k.lower(): v for k, v in lookups['zone'].items()})
        # Add full name mappings: Offensive -> ZN01, Defensive -> ZN02, Neutral -> ZN03
        name_to_code = {'Offensive': 'O', 'Defensive': 'D', 'Neutral': 'N'}
        for name, code in name_to_code.items():
            if code.upper() in lookups['zone']:
                lookups['zone'][name] = lookups['zone'][code.upper()]
                lookups['zone'][name.lower()] = lookups['zone'][code.upper()]
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['zone'] = {}
    
    # dim_team: team_name -> team_id
    try:
        dim = pd.read_csv(output_dir / 'dim_team.csv', dtype=str)
        lookups['team'] = dict(zip(dim['team_name'], dim['team_id']))
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['team'] = {}
    
    # Apply lookups
    df = df.copy()
    
    # period_id
    if 'period' in df.columns and lookups['period']:
        df['period_id'] = df['period'].astype(str).map(lookups['period'])
    
    # event_type_id
    if 'event_type' in df.columns and lookups['event_type']:
        df['event_type_id'] = df['event_type'].map(lookups['event_type'])
    
    # event_detail_id
    if 'event_detail' in df.columns and lookups['event_detail']:
        df['event_detail_id'] = df['event_detail'].map(lookups['event_detail'])
    
    # event_detail_2_id
    if 'event_detail_2' in df.columns and lookups['event_detail_2']:
        df['event_detail_2_id'] = df['event_detail_2'].map(lookups['event_detail_2'])
    
    # success_id - map True/False to SC01/SC02
    if 'event_successful' in df.columns and lookups.get('success_bool'):
        def map_success(val):
            if pd.isna(val):
                return None
            return lookups['success_bool'].get(val) or lookups['success_bool'].get(str(val))
        df['success_id'] = df['event_successful'].apply(map_success)
    
    # event_zone_id
    if 'event_team_zone' in df.columns and lookups['zone']:
        df['event_zone_id'] = df['event_team_zone'].map(lookups['zone'])
    
    # strength_id - map '5v5' -> 'STR01', etc.
    if 'strength' in df.columns:
        try:
            dim = pd.read_csv(output_dir / 'dim_strength.csv', dtype=str)
            strength_map = dict(zip(dim['strength_code'], dim['strength_id']))
            df['strength_id'] = df['strength'].map(strength_map)
        except (ValueError, TypeError, KeyError, FileNotFoundError):
            pass
    
    # home_team_id
    if 'home_team' in df.columns and lookups['team']:
        df['home_team_id'] = df['home_team'].map(lookups['team'])
    
    # away_team_id
    if 'away_team' in df.columns and lookups['team']:
        df['away_team_id'] = df['away_team'].map(lookups['team'])
    
    return df


def add_fact_event_players_fkeys(df: pd.DataFrame, output_dir) -> pd.DataFrame:
    """
    Add foreign key columns to fact_event_players.
    
    Adds FK columns for all dimensional attributes.
    
    Args:
        df: fact_event_players DataFrame
        output_dir: Path to output directory with dim tables
        
    Returns:
        DataFrame with FK columns added
    """
    from pathlib import Path
    output_dir = Path(output_dir)
    
    df = df.copy()
    lookups = {}
    
    # Load all dim tables and build lookups
    
    # dim_period: period number -> period_id
    lookups['period'] = {str(i): f"P{i:02d}" for i in range(1, 6)}
    
    # dim_event_type: event_type_code -> event_type_id
    try:
        dim = pd.read_csv(output_dir / 'dim_event_type.csv', dtype=str)
        lookups['event_type'] = dict(zip(dim['event_type_code'], dim['event_type_id']))
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['event_type'] = {}
    
    # dim_event_detail: event_detail_code -> event_detail_id
    try:
        dim = pd.read_csv(output_dir / 'dim_event_detail.csv', dtype=str)
        lookups['event_detail'] = dict(zip(dim['event_detail_code'], dim['event_detail_id']))
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['event_detail'] = {}
    
    # dim_event_detail_2: event_detail_2_code -> event_detail_2_id
    try:
        dim = pd.read_csv(output_dir / 'dim_event_detail_2.csv', dtype=str)
        lookups['event_detail_2'] = dict(zip(dim['event_detail_2_code'], dim['event_detail_2_id']))
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['event_detail_2'] = {}
    
    # dim_success: success_code -> success_id
    try:
        dim = pd.read_csv(output_dir / 'dim_success.csv', dtype=str)
        lookups['success'] = dict(zip(dim['success_code'], dim['success_id']))
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['success'] = {}
    
    # dim_zone: zone_code -> zone_id (handle both upper and lower case)
    try:
        dim = pd.read_csv(output_dir / 'dim_zone.csv', dtype=str)
        lookups['zone'] = dict(zip(dim['zone_code'].str.upper(), dim['zone_id']))
        lookups['zone'].update({k.lower(): v for k, v in lookups['zone'].items()})
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['zone'] = {}
    
    # dim_team: team_name -> team_id
    try:
        dim = pd.read_csv(output_dir / 'dim_team.csv', dtype=str)
        lookups['team'] = dict(zip(dim['team_name'], dim['team_id']))
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['team'] = {}
    
    # dim_venue: venue_code -> venue_id
    try:
        dim = pd.read_csv(output_dir / 'dim_venue.csv', dtype=str)
        # Build lookup from both code and name columns
        lookups['venue'] = {}
        for _, row in dim.iterrows():
            vid = row['venue_id']
            # Add all possible variations
            if pd.notna(row.get('venue_code')):
                lookups['venue'][row['venue_code']] = vid
                lookups['venue'][row['venue_code'].lower()] = vid
                lookups['venue'][row['venue_code'].capitalize()] = vid
            if pd.notna(row.get('venue_name')):
                lookups['venue'][row['venue_name']] = vid
                lookups['venue'][row['venue_name'].lower()] = vid
                lookups['venue'][row['venue_name'].capitalize()] = vid
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['venue'] = {}
    
    # dim_player_role: role_code -> role_id
    try:
        dim = pd.read_csv(output_dir / 'dim_player_role.csv', dtype=str)
        lookups['player_role'] = dict(zip(dim['role_code'], dim['role_id']))
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['player_role'] = {}
    
    # dim_play_detail: play_detail_code -> play_detail_id
    try:
        dim = pd.read_csv(output_dir / 'dim_play_detail.csv', dtype=str)
        lookups['play_detail'] = dict(zip(dim['play_detail_code'], dim['play_detail_id']))
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['play_detail'] = {}
    
    # dim_play_detail_2: play_detail_2_code -> play_detail_2_id
    try:
        dim = pd.read_csv(output_dir / 'dim_play_detail_2.csv', dtype=str)
        lookups['play_detail_2'] = dict(zip(dim['play_detail_2_code'], dim['play_detail_2_id']))
    except (ValueError, TypeError, KeyError, FileNotFoundError):
        lookups['play_detail_2'] = {}
    
    # Apply lookups
    
    # period_id
    if 'period' in df.columns and lookups['period']:
        df['period_id'] = df['period'].astype(str).map(lookups['period'])
    
    # event_type_id
    if 'event_type' in df.columns and lookups['event_type']:
        df['event_type_id'] = df['event_type'].map(lookups['event_type'])
    
    # event_detail_id
    if 'event_detail' in df.columns and lookups['event_detail']:
        df['event_detail_id'] = df['event_detail'].map(lookups['event_detail'])
    
    # event_detail_2_id
    if 'event_detail_2' in df.columns and lookups['event_detail_2']:
        df['event_detail_2_id'] = df['event_detail_2'].map(lookups['event_detail_2'])
    
    # event_success_id
    if 'event_successful' in df.columns and lookups['success']:
        df['event_success_id'] = df['event_successful'].map(lookups['success'])
    
    # event_zone_id
    if 'event_team_zone' in df.columns and lookups['zone']:
        df['event_zone_id'] = df['event_team_zone'].map(lookups['zone'])
    
    # home_zone_id
    if 'home_team_zone' in df.columns and lookups['zone']:
        df['home_zone_id'] = df['home_team_zone'].map(lookups['zone'])
    
    # away_zone_id
    if 'away_team_zone' in df.columns and lookups['zone']:
        df['away_zone_id'] = df['away_team_zone'].map(lookups['zone'])
    
    # home_team_id
    if 'home_team' in df.columns and lookups['team']:
        df['home_team_id'] = df['home_team'].map(lookups['team'])
    
    # away_team_id
    if 'away_team' in df.columns and lookups['team']:
        df['away_team_id'] = df['away_team'].map(lookups['team'])
    
    # Derive player_team from team_venue if not populated
    if 'team_venue' in df.columns and 'home_team' in df.columns and 'away_team' in df.columns:
        if 'player_team' not in df.columns or df['player_team'].isna().all():
            df['player_team'] = df.apply(
                lambda r: r['home_team'] if r['team_venue'] == 'h' else r['away_team'], 
                axis=1
            )
    
    # player_team_id
    if 'player_team' in df.columns and lookups['team']:
        df['player_team_id'] = df['player_team'].map(lookups['team'])
    
    # team_venue_id
    if 'team_venue' in df.columns and lookups['venue']:
        df['team_venue_id'] = df['team_venue'].map(lookups['venue'])
    
    # player_role_id
    if 'player_role' in df.columns and lookups['player_role']:
        df['player_role_id'] = df['player_role'].map(lookups['player_role'])
    
    # play_detail_id
    if 'play_detail1' in df.columns and lookups['play_detail']:
        df['play_detail_id'] = df['play_detail1'].map(lookups['play_detail'])
    
    # play_detail_2_id
    if 'play_detail_2' in df.columns and lookups['play_detail_2']:
        df['play_detail_2_id'] = df['play_detail_2'].map(lookups['play_detail_2'])
    
    # play_success_id
    if 'play_detail_successful' in df.columns and lookups['success']:
        df['play_success_id'] = df['play_detail_successful'].map(lookups['success'])
    
    return df


def generate_event_chain_key(row) -> str:
    """
    Generate event_chain_key from game_id and event index.
    Format: EC{game_id}{event_index:06d}
    Example: EC18969001000
    """
    game_id = row.get('game_id')
    
    # Try to extract event_index from event_id or tracking_event_index
    event_index = None
    
    # From event_id (format: EV1896901000)
    if pd.notna(row.get('event_id')):
        event_id = str(row['event_id'])
        if event_id.startswith('EV'):
            try:
                # Extract last 5 digits as event_index
                event_index = int(event_id[-5:])
            except (ValueError, TypeError, KeyError, FileNotFoundError):
                pass
    
    # Fallback to tracking_event_index
    if event_index is None and pd.notna(row.get('tracking_event_index')):
        try:
            event_index = int(float(row['tracking_event_index']))
        except (ValueError, TypeError, KeyError, FileNotFoundError):
            pass
    
    if game_id is None or event_index is None:
        return None
    
    return f"EC{game_id}{event_index:06d}"
