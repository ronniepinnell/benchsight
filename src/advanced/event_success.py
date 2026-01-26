"""
Event Success/Unsuccessful (s/u) Logic Module

This module handles:
1. Standardizing s/u values to lowercase 's' or 'u'
2. Deriving event-level success from context
3. Deriving play-level success (inheritance + overrides)
4. Auto-deriving opposing player play_details
5. Managing play_detail slots (2 max, human input supreme)

See docs/reference/EVENT_SUCCESS_LOGIC.md for full specification.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any


def load_thresholds(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load threshold configuration from JSON file."""
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / 'config' / 'etl_thresholds.json'

    with open(config_path, 'r') as f:
        return json.load(f)


# ============================================================
# VALUE STANDARDIZATION
# ============================================================

def standardize_success_flag(value, config: Optional[Dict] = None) -> Optional[str]:
    """
    Standardize success flag values to lowercase 's' or 'u'.

    Args:
        value: Raw value (could be TRUE, 1, 's', 'S', etc.)
        config: Optional config dict with mappings

    Returns:
        's', 'u', or None
    """
    if pd.isna(value) or value == '' or value is None:
        return None

    val_str = str(value).lower().strip()

    # Default mappings if no config provided
    if config is None:
        successful = ['s', 'true', '1', 'success', 'successful']
        unsuccessful = ['u', 'false', '0', 'unsuccessful', 'fail', 'failed']
    else:
        mappings = config.get('success_value_mappings', {})
        successful = mappings.get('successful', ['s', 'true', '1'])
        unsuccessful = mappings.get('unsuccessful', ['u', 'false', '0'])

    if val_str in successful:
        return 's'
    elif val_str in unsuccessful:
        return 'u'
    else:
        return None  # Invalid value


def standardize_success_columns(df: pd.DataFrame, config: Optional[Dict] = None) -> pd.DataFrame:
    """
    Standardize all success-related columns in dataframe.

    Columns affected: event_successful, play_detail1_s, play_detail2_s
    """
    df = df.copy()

    success_columns = ['event_successful', 'play_detail1_s', 'play_detail2_s']

    for col in success_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: standardize_success_flag(x, config))

    return df


# ============================================================
# EVENT-LEVEL SUCCESS DERIVATION
# ============================================================

# Events that get explicit s/u flags
EVENT_SUCCESS_RULES = {
    # (event_type, event_detail): flag or 'context'
    ('Pass', 'Pass_Completed'): 'context',
    ('Pass', 'Pass_Missed'): 'u',
    ('Pass', 'Pass_Intercepted'): 'u',
    ('Pass', 'Pass_Deflected'): 'context',
    ('Zone', 'Zone_Entry'): 'context',
    ('Zone', 'Zone_Entry_Failed'): 'u',
    ('Zone', 'Zone_Exit'): 'context',
    ('Zone', 'Zone_Exit_Failed'): 'u',
    ('Zone', 'Zone_Keepin'): 'context',
    ('Zone', 'Zone_Keepin_Failed'): 'u',
    ('Turnover', 'Turnover_Giveaway'): 'u',
    ('Turnover', 'Turnover_Takeaway'): 'context',
}

# Events that should NOT have s/u flags (leave blank)
NO_FLAG_EVENTS = {
    'Goal', 'Shot', 'Faceoff', 'Save', 'Rebound', 'Stoppage',
    'Penalty', 'Possession', 'LoosePuck', 'DeadIce', 'Intermission',
    'GameStart', 'GameEnd', 'Clockstop', 'Timeout'
}


def derive_event_success(df: pd.DataFrame, config: Optional[Dict] = None, log=None) -> pd.DataFrame:
    """
    Derive event_successful for events that need context-based evaluation.

    Logic:
    - Direct flags: Apply immediately based on event_detail
    - Context-based: Look ahead at next events to determine success

    Args:
        df: Event players dataframe
        config: Threshold configuration
        log: Logger function

    Returns:
        DataFrame with event_successful populated
    """
    if config is None:
        config = load_thresholds()

    df = df.copy()

    # Ensure column exists
    if 'event_successful' not in df.columns:
        df['event_successful'] = None

    # First, standardize any existing values
    df = standardize_success_columns(df, config)

    # Get time windows from config
    context_window = config.get('time_windows', {}).get('context_window_seconds', 3)
    look_ahead_pass = config.get('look_ahead_events', {}).get('pass', 2)
    look_ahead_entry = config.get('look_ahead_events', {}).get('zone_entry', 5)
    look_ahead_exit = config.get('look_ahead_events', {}).get('zone_exit', 3)

    # Sort by game, period, event_index for proper sequencing
    sort_cols = ['game_id', 'period', 'event_index']
    if all(c in df.columns for c in sort_cols):
        df = df.sort_values(sort_cols).reset_index(drop=True)

    # Apply direct flags first (non-context based)
    for (event_type, event_detail), flag in EVENT_SUCCESS_RULES.items():
        if flag != 'context':
            mask = (
                (df['event_type'] == event_type) &
                (df['event_detail'] == event_detail) &
                df['event_successful'].isna()
            )
            df.loc[mask, 'event_successful'] = flag

    # Context-based derivation for remaining events
    df = _derive_context_based_success(df, config)

    if log:
        derived_count = df['event_successful'].notna().sum()
        log(f"  Derived event_successful for {derived_count} rows")

    return df


def _derive_context_based_success(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    Derive success for context-dependent events by looking at subsequent events.
    """
    context_window = config.get('time_windows', {}).get('context_window_seconds', 3)

    # Get unique games for processing
    if 'game_id' not in df.columns:
        return df

    # Process each game separately to maintain context
    for game_id in df['game_id'].unique():
        game_mask = df['game_id'] == game_id

        for period in df.loc[game_mask, 'period'].unique():
            period_mask = game_mask & (df['period'] == period)
            period_df = df.loc[period_mask].copy()

            # Get primary event rows (event_player_1) for next-event lookup
            primary_rows = period_df[period_df['player_role'] == 'event_player_1']

            for idx in period_df.index:
                row = period_df.loc[idx]

                # Skip if already has value or not a context event
                if pd.notna(row.get('event_successful')):
                    continue

                event_type = row.get('event_type', '')
                event_detail = row.get('event_detail', '')

                # Check if this needs context evaluation
                rule = EVENT_SUCCESS_RULES.get((event_type, event_detail))
                if rule != 'context':
                    continue

                # Find next event
                current_event_idx = row.get('event_index', 0)
                current_team = row.get('team_', '')
                current_time = row.get('time_start_total_seconds', 0)

                next_events = primary_rows[
                    (primary_rows['event_index'] > current_event_idx)
                ]

                if len(next_events) == 0:
                    continue  # End of period, can't determine

                next_event = next_events.iloc[0]
                next_team = next_event.get('team_', '')
                next_event_type = next_event.get('event_type', '')
                next_time = next_event.get('time_start_total_seconds', 0)

                # Time check (within context window)
                time_diff = abs(next_time - current_time) if current_time and next_time else 0

                # Success logic: same team maintained possession, no turnover
                same_team = next_team == current_team
                not_turnover = next_event_type != 'Turnover'
                within_window = time_diff <= context_window or time_diff == 0

                if same_team and not_turnover:
                    df.at[idx, 'event_successful'] = 's'
                elif not same_team or next_event_type == 'Turnover':
                    df.at[idx, 'event_successful'] = 'u'

    return df


# ============================================================
# PLAY-LEVEL SUCCESS (play_detail1_s, play_detail2_s)
# ============================================================

# Play details that get explicit flags (override event flag)
PLAY_DETAIL_FLAGS = {
    # Defensive success (when caused turnover)
    'StickCheck': 's',  # Only if caused turnover, else blank
    'PokeCheck': 's',
    'Pressure': 's',
    'ForcedTurnover': 's',
    'ForcedMissedPass': 's',
    'ForcedMissedShot': 's',
    'ForcedLostPossession': 's',

    # Beat moves (always 'u' for defender who was beat)
    'BeatWide': 'u',
    'BeatMiddle': 'u',
    'BeatSpeed': 'u',
    'BeatFake': 'u',
    'BeatDeke': 'u',

    # Receiver failures
    'ReceiverMissed': 'u',
    'ReceiverBobbled': 'u',

    # Puck outcomes
    'LostPuck': 'u',
    'SeparateFromPuck': 'u',
    'LoosePuckBattleWon': 's',
    'LoosePuckBattleLost': 'u',

    # Stopped moves (success for defender)
    'StoppedDeke': 's',

    # Ceded zone (always 'u' for defender)
    'CededZoneEntry': 'u',
    'CededZoneExit': 'u',
}

# Defensive play_details that only get 's' if they caused a turnover
CONDITIONAL_DEFENSIVE_SUCCESS = {'StickCheck', 'PokeCheck', 'Pressure'}


def derive_play_detail_success(df: pd.DataFrame, config: Optional[Dict] = None, log=None) -> pd.DataFrame:
    """
    Derive play_detail success flags.

    Rules:
    1. event_player_1's play_details inherit event's s/u flag
    2. Explicit overrides for specific play_details (see PLAY_DETAIL_FLAGS)
    3. Defensive actions only get 's' if they caused turnover

    Args:
        df: Event players dataframe with event_successful populated
        config: Threshold configuration
        log: Logger function

    Returns:
        DataFrame with play_detail1_s, play_detail2_s populated
    """
    df = df.copy()

    # Ensure columns exist
    for col in ['play_detail1_s', 'play_detail2_s']:
        if col not in df.columns:
            df[col] = None

    # Process each play_detail column
    for pd_col, flag_col in [('play_detail1', 'play_detail1_s'), ('play_detail2', 'play_detail2_s')]:
        if pd_col not in df.columns:
            continue

        for idx in df.index:
            # Skip if already has a value (human input)
            if pd.notna(df.at[idx, flag_col]):
                continue

            play_detail = df.at[idx, pd_col]
            if pd.isna(play_detail) or play_detail == '':
                continue

            player_role = df.at[idx, 'player_role'] if 'player_role' in df.columns else ''
            event_flag = df.at[idx, 'event_successful'] if 'event_successful' in df.columns else None
            event_type = df.at[idx, 'event_type'] if 'event_type' in df.columns else ''

            # Check for explicit override
            if play_detail in PLAY_DETAIL_FLAGS:
                # Conditional defensive success check
                if play_detail in CONDITIONAL_DEFENSIVE_SUCCESS:
                    # Only 's' if this event is a turnover (defensive success)
                    if event_type == 'Turnover':
                        df.at[idx, flag_col] = 's'
                    # Otherwise leave blank
                else:
                    df.at[idx, flag_col] = PLAY_DETAIL_FLAGS[play_detail]

            # Inheritance rule: event_player_1 inherits event flag
            elif player_role == 'event_player_1' and pd.notna(event_flag):
                df.at[idx, flag_col] = event_flag

    if log:
        pd1_count = df['play_detail1_s'].notna().sum()
        pd2_count = df['play_detail2_s'].notna().sum()
        log(f"  Derived play_detail flags: pd1={pd1_count}, pd2={pd2_count}")

    return df


# ============================================================
# AUTO-DERIVATION PAIRS (Offensive <-> Defensive)
# ============================================================

# Offensive action → Defensive result
OFFENSIVE_TO_DEFENSIVE = {
    ('Deke', 's'): ('opp_player_1', 'BeatDeke', 'u'),
    ('Deke', 'u'): ('opp_player_1', 'StoppedDeke', 's'),
    ('BeatWide', 's'): ('opp_player_1', 'BeatWide', 'u'),
    ('BeatMiddle', 's'): ('opp_player_1', 'BeatMiddle', 'u'),
    ('BeatSpeed', 's'): ('opp_player_1', 'BeatSpeed', 'u'),
    ('BeatFake', 's'): ('opp_player_1', 'BeatFake', 'u'),
    ('OpenIceDeke', 's'): ('opp_player_1', 'BeatDeke', 'u'),
    ('OpenIceDeke', 'u'): ('opp_player_1', 'StoppedDeke', 's'),
}

# Defensive action → Offensive result
DEFENSIVE_TO_OFFENSIVE = {
    ('StickCheck', 's'): ('event_player_1', 'LostPuck', 'u'),
    ('PokeCheck', 's'): ('event_player_1', 'SeparateFromPuck', 'u'),
    ('StickLift', 's'): ('event_player_1', 'LostPuck', 'u'),
    ('ForcedTurnover', 's'): ('event_player_1', 'LostPuck', 'u'),
}

# Puck battle pairs
BATTLE_PAIRS = {
    ('LoosePuckBattleWon', 's'): ('opponent', 'LoosePuckBattleLost', 'u'),
    ('LoosePuckBattleLost', 'u'): ('opponent', 'LoosePuckBattleWon', 's'),
}

# Derivation priority (lower = higher priority)
DERIVATION_PRIORITY = {
    'ForcedTurnover': 1,
    'ForcedMissedPass': 1,
    'ForcedLostPossession': 1,
    'BeatDeke': 2,
    'StoppedDeke': 2,
    'BeatWide': 2,
    'BeatMiddle': 2,
    'BeatSpeed': 2,
    'BeatFake': 2,
    'LoosePuckBattleWon': 3,
    'LoosePuckBattleLost': 3,
    'CededZoneEntry': 4,
    'CededZoneExit': 4,
    'BlockPassingLane': 5,
    'InShotPassLane': 5,
    'LostPuck': 6,
    'SeparateFromPuck': 6,
    'ReceiverCompleted': 7,
}


def derive_opposing_play_details(df: pd.DataFrame, config: Optional[Dict] = None, log=None) -> pd.DataFrame:
    """
    Auto-derive opposing player's play_details based on primary player's action.

    Example: If event_player_1 has Deke='s', add BeatDeke='u' to opp_player_1

    Rules:
    1. Only derive if target player exists in event
    2. Never overwrite existing play_details (human input supreme)
    3. Only fill empty slots (max 2)
    4. Use priority order for multiple derivations

    Args:
        df: Event players dataframe
        config: Threshold configuration
        log: Logger function

    Returns:
        DataFrame with derived opposing play_details
    """
    df = df.copy()

    # Group by event_index to process each event
    if 'event_index' not in df.columns:
        return df

    derivations_made = 0

    for event_idx in df['event_index'].unique():
        event_rows = df[df['event_index'] == event_idx]

        # Collect all derivations for this event
        derivations = []  # List of (target_idx, play_detail, flag, priority)

        for idx, row in event_rows.iterrows():
            player_role = row.get('player_role', '')

            # Check each play_detail column
            for pd_col, flag_col in [('play_detail1', 'play_detail1_s'), ('play_detail2', 'play_detail2_s')]:
                if pd_col not in df.columns:
                    continue

                play_detail = row.get(pd_col)
                flag = row.get(flag_col)

                if pd.isna(play_detail) or play_detail == '':
                    continue

                # Check for derivation mapping
                key = (play_detail, flag) if pd.notna(flag) else None

                # Try offensive → defensive
                if player_role.startswith('event_player') and key in OFFENSIVE_TO_DEFENSIVE:
                    target_role, derived_pd, derived_flag = OFFENSIVE_TO_DEFENSIVE[key]
                    priority = DERIVATION_PRIORITY.get(derived_pd, 99)

                    # Find target player
                    target_rows = event_rows[event_rows['player_role'] == target_role]
                    if len(target_rows) > 0:
                        target_idx = target_rows.index[0]
                        derivations.append((target_idx, derived_pd, derived_flag, priority))

                # Try defensive → offensive
                elif player_role.startswith('opp_player') and key in DEFENSIVE_TO_OFFENSIVE:
                    target_role, derived_pd, derived_flag = DEFENSIVE_TO_OFFENSIVE[key]
                    priority = DERIVATION_PRIORITY.get(derived_pd, 99)

                    # Find target player
                    target_rows = event_rows[event_rows['player_role'] == target_role]
                    if len(target_rows) > 0:
                        target_idx = target_rows.index[0]
                        derivations.append((target_idx, derived_pd, derived_flag, priority))

        # Sort by priority and apply
        derivations.sort(key=lambda x: x[3])

        for target_idx, derived_pd, derived_flag, _ in derivations:
            # Apply using slot management
            df = _assign_to_empty_slot(df, target_idx, derived_pd, derived_flag)
            derivations_made += 1

    if log:
        log(f"  Auto-derived {derivations_made} opposing play_details")

    return df


def _assign_to_empty_slot(df: pd.DataFrame, idx: int, play_detail: str, flag: str) -> pd.DataFrame:
    """
    Assign a derived play_detail to an empty slot.

    Rules:
    1. Never overwrite existing values (human input supreme)
    2. Only 2 slots available
    3. Fill play_detail1 first, then play_detail2
    """
    pd1 = df.at[idx, 'play_detail1'] if 'play_detail1' in df.columns else None
    pd2 = df.at[idx, 'play_detail2'] if 'play_detail2' in df.columns else None

    # Check if already exists
    if pd1 == play_detail or pd2 == play_detail:
        return df  # Already has this play_detail

    # Find empty slot
    if pd.isna(pd1) or pd1 == '':
        df.at[idx, 'play_detail1'] = play_detail
        if 'play_detail1_s' in df.columns:
            df.at[idx, 'play_detail1_s'] = flag
    elif pd.isna(pd2) or pd2 == '':
        df.at[idx, 'play_detail2'] = play_detail
        if 'play_detail2_s' in df.columns:
            df.at[idx, 'play_detail2_s'] = flag
    # Else: both slots full, don't add

    return df


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def process_event_success(df: pd.DataFrame, config: Optional[Dict] = None, log=None) -> pd.DataFrame:
    """
    Main entry point for all event success processing.

    Runs in order:
    1. Standardize existing s/u values
    2. Derive event-level success
    3. Derive opposing play_details
    4. Derive play-level success

    Args:
        df: Event players dataframe
        config: Optional config dict (loads from file if not provided)
        log: Optional logger function

    Returns:
        DataFrame with all success fields populated
    """
    if config is None:
        config = load_thresholds()

    if log:
        log("Processing event success logic...")

    # Step 1: Standardize values
    df = standardize_success_columns(df, config)

    # Step 2: Derive event-level success
    df = derive_event_success(df, config, log)

    # Step 3: Derive opposing play_details
    df = derive_opposing_play_details(df, config, log)

    # Step 4: Derive play-level success
    df = derive_play_detail_success(df, config, log)

    return df
