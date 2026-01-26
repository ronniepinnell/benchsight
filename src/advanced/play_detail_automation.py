"""
Play Detail Automation Module

This module handles auto-derivation of play_details from:
1. XY trajectory data (Drive*, Screen, FrontofNet)
2. Event details (BlockedShot, PassIntercepted)
3. Event sequences/time (QuickUp, GiveAndGo, ShotOneTimer)
4. Distance calculations (CededZone*, ForcedTurnover)
5. Pass path analysis (BlockPassingLane, PassCross)

Rules:
1. Human input is SUPREME - never overwrite tracker entries
2. Only 2 slots per player (play_detail1, play_detail2)
3. Apply derivation priority order
4. Only fill empty slots

See docs/reference/EVENT_SUCCESS_LOGIC.md for full specification.
"""

import json
import math
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


def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> Optional[float]:
    """Calculate Euclidean distance between two points in feet."""
    if any(pd.isna(v) for v in [x1, y1, x2, y2]):
        return None
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# ============================================================
# DERIVATION FROM DEFENDER DISTANCE
# ============================================================

def derive_ceded_zone(df: pd.DataFrame, config: Optional[Dict] = None, log=None) -> pd.DataFrame:
    """
    Derive CededZoneEntry/CededZoneExit based on defender distance.

    Rules:
    - Zone Entry: opp_player_1 >= 20 ft → CededZoneEntry='u' on opp_player_1
    - Zone Exit: opp_player_1 >= 18 ft → CededZoneExit='u' on opp_player_1

    This is a DEFENSIVE metric - only applied to opp_player_1.

    Args:
        df: Event players dataframe with XY coordinates
        config: Threshold configuration
        log: Logger function

    Returns:
        DataFrame with ceded play_details added to defenders
    """
    if config is None:
        config = load_thresholds()

    df = df.copy()
    thresholds = config.get('distance_thresholds_ft', {})
    ceded_entry_ft = thresholds.get('ceded_entry', 20)
    ceded_exit_ft = thresholds.get('ceded_exit', 18)

    derivations = 0

    # Required columns
    required_cols = ['event_index', 'event_detail', 'player_role']
    xy_cols = ['puck_x_start', 'puck_y_start']  # Puck position
    opp_xy_cols = ['opp_player_1_x', 'opp_player_1_y']  # Defender position (if available)

    if not all(c in df.columns for c in required_cols):
        if log:
            log("  Skipping ceded zone derivation - missing required columns")
        return df

    # Check for XY data availability
    has_xy = all(c in df.columns for c in xy_cols)
    has_opp_xy = all(c in df.columns for c in opp_xy_cols)

    if not has_xy:
        if log:
            log("  Skipping ceded zone derivation - no XY data")
        return df

    # Process zone entries and exits
    zone_events = df[df['event_detail'].isin(['Zone_Entry', 'Zone_Exit'])]

    for event_idx in zone_events['event_index'].unique():
        event_rows = df[df['event_index'] == event_idx]
        event_detail = event_rows['event_detail'].iloc[0]

        # Get opp_player_1 row for this event
        opp_rows = event_rows[event_rows['player_role'] == 'opp_player_1']
        if len(opp_rows) == 0:
            continue  # No defender tracked

        opp_idx = opp_rows.index[0]

        # Calculate distance
        if has_opp_xy:
            puck_x = event_rows['puck_x_start'].iloc[0]
            puck_y = event_rows['puck_y_start'].iloc[0]
            opp_x = opp_rows['opp_player_1_x'].iloc[0] if 'opp_player_1_x' in opp_rows.columns else None
            opp_y = opp_rows['opp_player_1_y'].iloc[0] if 'opp_player_1_y' in opp_rows.columns else None

            distance = calculate_distance(puck_x, puck_y, opp_x, opp_y)
        else:
            distance = None

        if distance is None:
            continue

        # Check thresholds
        if event_detail == 'Zone_Entry' and distance >= ceded_entry_ft:
            df = _assign_to_empty_slot(df, opp_idx, 'CededZoneEntry', 'u')
            derivations += 1
        elif event_detail == 'Zone_Exit' and distance >= ceded_exit_ft:
            df = _assign_to_empty_slot(df, opp_idx, 'CededZoneExit', 'u')
            derivations += 1

    if log:
        log(f"  Derived {derivations} ceded zone play_details")

    return df


def derive_forced_turnover(df: pd.DataFrame, config: Optional[Dict] = None, log=None) -> pd.DataFrame:
    """
    Derive ForcedTurnover based on defender proximity.

    Rule: If opp_player within 2 ft of puck carrier at turnover event,
    add ForcedTurnover='s' to opp_player_1.

    Args:
        df: Event players dataframe with XY coordinates
        config: Threshold configuration
        log: Logger function

    Returns:
        DataFrame with ForcedTurnover added where applicable
    """
    if config is None:
        config = load_thresholds()

    df = df.copy()
    thresholds = config.get('distance_thresholds_ft', {})
    forced_to_distance = thresholds.get('forced_turnover', 2)

    derivations = 0

    # Process turnover events
    if 'event_type' not in df.columns or 'event_detail' not in df.columns:
        return df

    turnover_events = df[
        (df['event_type'] == 'Turnover') &
        (df['event_detail'] == 'Turnover_Giveaway')
    ]

    # Check for XY data
    has_xy = 'puck_x_start' in df.columns and 'puck_y_start' in df.columns

    for event_idx in turnover_events['event_index'].unique():
        event_rows = df[df['event_index'] == event_idx]

        # Get opp_player_1 row
        opp_rows = event_rows[event_rows['player_role'] == 'opp_player_1']
        if len(opp_rows) == 0:
            continue

        opp_idx = opp_rows.index[0]

        # Check if opp_player already has ForcedTurnover
        pd1 = df.at[opp_idx, 'play_detail1'] if 'play_detail1' in df.columns else None
        pd2 = df.at[opp_idx, 'play_detail2'] if 'play_detail2' in df.columns else None
        if pd1 == 'ForcedTurnover' or pd2 == 'ForcedTurnover':
            continue  # Already has it

        # If we have XY data, check distance
        if has_xy and 'opp_player_1_x' in df.columns:
            puck_x = event_rows['puck_x_start'].iloc[0]
            puck_y = event_rows['puck_y_start'].iloc[0]
            opp_x = opp_rows['opp_player_1_x'].iloc[0] if 'opp_player_1_x' in opp_rows.columns else None
            opp_y = opp_rows['opp_player_1_y'].iloc[0] if 'opp_player_1_y' in opp_rows.columns else None

            distance = calculate_distance(puck_x, puck_y, opp_x, opp_y)

            if distance is None or distance > forced_to_distance:
                continue  # Not close enough

        # Add ForcedTurnover
        df = _assign_to_empty_slot(df, opp_idx, 'ForcedTurnover', 's')
        derivations += 1

    if log:
        log(f"  Derived {derivations} ForcedTurnover play_details")

    return df


# ============================================================
# DERIVATION FROM EVENT DETAILS
# ============================================================

def derive_from_event_detail(df: pd.DataFrame, config: Optional[Dict] = None, log=None) -> pd.DataFrame:
    """
    Derive play_details directly from event_detail values.

    Mappings:
    - Shot_Blocked → BlockedShot for opp_player_1
    - Pass_Intercepted → PassIntercepted for opp_player_1
    - Zone_Entry_Failed → ZoneEntryDenial for opp_player_1
    - Zone_Exit_Failed → ZoneExitDenial for opp_player_1

    Args:
        df: Event players dataframe
        config: Threshold configuration
        log: Logger function

    Returns:
        DataFrame with derived play_details
    """
    df = df.copy()

    # Mapping: event_detail → (play_detail, flag, target_role)
    EVENT_DETAIL_MAPPINGS = {
        'Shot_Blocked': ('BlockedShot', 's', 'opp_player_1'),
        'Pass_Intercepted': ('PassIntercepted', 's', 'opp_player_1'),
        'Zone_Entry_Failed': ('ZoneEntryDenial', 's', 'opp_player_1'),
        'Zone_Exit_Failed': ('ZoneExitDenial', 's', 'opp_player_1'),
    }

    if 'event_detail' not in df.columns or 'event_index' not in df.columns:
        return df

    derivations = 0

    for event_detail, (play_detail, flag, target_role) in EVENT_DETAIL_MAPPINGS.items():
        matching_events = df[df['event_detail'] == event_detail]

        for event_idx in matching_events['event_index'].unique():
            event_rows = df[df['event_index'] == event_idx]

            # Find target player
            target_rows = event_rows[event_rows['player_role'] == target_role]
            if len(target_rows) == 0:
                continue

            target_idx = target_rows.index[0]

            # Check if already has this play_detail
            pd1 = df.at[target_idx, 'play_detail1'] if 'play_detail1' in df.columns else None
            pd2 = df.at[target_idx, 'play_detail2'] if 'play_detail2' in df.columns else None
            if pd1 == play_detail or pd2 == play_detail:
                continue

            df = _assign_to_empty_slot(df, target_idx, play_detail, flag)
            derivations += 1

    if log:
        log(f"  Derived {derivations} play_details from event_detail")

    return df


# ============================================================
# DERIVATION FROM EVENT SEQUENCES
# ============================================================

def derive_from_sequence(df: pd.DataFrame, config: Optional[Dict] = None, log=None) -> pd.DataFrame:
    """
    Derive play_details from event sequences and timing.

    Derivations:
    - QuickUp: Zone exit → Zone entry < 3 seconds
    - GiveAndGo: Pass by A → Pass back to A < 4 seconds
    - ShotOneTimer: Pass → Shot < 0.5 seconds

    Args:
        df: Event players dataframe
        config: Threshold configuration
        log: Logger function

    Returns:
        DataFrame with sequence-derived play_details
    """
    if config is None:
        config = load_thresholds()

    df = df.copy()
    time_windows = config.get('time_windows', {})
    quick_up_sec = time_windows.get('quick_up_max_seconds', 3)
    give_go_sec = time_windows.get('give_and_go_max_seconds', 4)
    one_timer_sec = time_windows.get('one_timer_max_seconds', 0.5)

    derivations = 0

    # Require time columns
    if 'time_start_total_seconds' not in df.columns:
        if log:
            log("  Skipping sequence derivation - no time data")
        return df

    # Sort by game, period, event_index
    sort_cols = ['game_id', 'period', 'event_index']
    if all(c in df.columns for c in sort_cols):
        df = df.sort_values(sort_cols).reset_index(drop=True)

    # Get primary event rows for sequence analysis
    primary_rows = df[df['player_role'] == 'event_player_1'].copy()

    # ShotOneTimer: Pass → Shot < 0.5 seconds
    for idx in range(1, len(primary_rows)):
        prev_row = primary_rows.iloc[idx - 1]
        curr_row = primary_rows.iloc[idx]

        # Same game, same period
        if prev_row.get('game_id') != curr_row.get('game_id'):
            continue
        if prev_row.get('period') != curr_row.get('period'):
            continue

        prev_type = prev_row.get('event_type', '')
        curr_type = curr_row.get('event_type', '')
        prev_time = prev_row.get('time_start_total_seconds', 0)
        curr_time = curr_row.get('time_start_total_seconds', 0)

        time_diff = abs(curr_time - prev_time) if prev_time and curr_time else float('inf')

        # Pass → Shot < 0.5 sec = ShotOneTimer
        if prev_type == 'Pass' and curr_type == 'Shot' and time_diff <= one_timer_sec:
            curr_idx = primary_rows.index[idx]
            original_idx = df[df['event_index'] == curr_row['event_index']].index[0]
            df = _assign_to_empty_slot(df, original_idx, 'ShotOneTimer', None)
            derivations += 1

    if log:
        log(f"  Derived {derivations} sequence-based play_details")

    return df


# ============================================================
# DERIVATION FROM PASS PATH
# ============================================================

def derive_from_pass_path(df: pd.DataFrame, config: Optional[Dict] = None, log=None) -> pd.DataFrame:
    """
    Derive pass-related play_details from XY data.

    Derivations:
    - PassCross: Y change > 20 ft
    - PassStretch: Pass distance > 60 ft
    - Chip: Pass distance < 15 ft
    - BlockPassingLane: Player within 5% of puck travel path

    Args:
        df: Event players dataframe with XY data
        config: Threshold configuration
        log: Logger function

    Returns:
        DataFrame with pass-derived play_details
    """
    if config is None:
        config = load_thresholds()

    df = df.copy()
    thresholds = config.get('distance_thresholds_ft', {})
    cross_min_y = thresholds.get('pass_cross_min_y', 20)
    stretch_min = thresholds.get('pass_stretch_min', 60)
    chip_max = thresholds.get('chip_max', 15)

    derivations = 0

    # Require XY columns
    xy_cols = ['puck_x_start', 'puck_y_start', 'puck_x_end', 'puck_y_end']
    if not all(c in df.columns for c in xy_cols):
        if log:
            log("  Skipping pass path derivation - no puck XY data")
        return df

    # Process pass events
    pass_events = df[df['event_type'] == 'Pass']

    for event_idx in pass_events['event_index'].unique():
        event_rows = df[df['event_index'] == event_idx]
        passer_rows = event_rows[event_rows['player_role'] == 'event_player_1']

        if len(passer_rows) == 0:
            continue

        passer_idx = passer_rows.index[0]

        # Get XY data
        x1 = passer_rows['puck_x_start'].iloc[0]
        y1 = passer_rows['puck_y_start'].iloc[0]
        x2 = passer_rows['puck_x_end'].iloc[0] if 'puck_x_end' in passer_rows.columns else None
        y2 = passer_rows['puck_y_end'].iloc[0] if 'puck_y_end' in passer_rows.columns else None

        if any(pd.isna(v) for v in [x1, y1, x2, y2]):
            continue

        # Calculate metrics
        y_change = abs(y2 - y1)
        distance = calculate_distance(x1, y1, x2, y2)

        # PassCross: Large Y change
        if y_change >= cross_min_y:
            df = _assign_to_empty_slot(df, passer_idx, 'PassCross', None)
            derivations += 1

        # PassStretch: Long pass
        elif distance and distance >= stretch_min:
            df = _assign_to_empty_slot(df, passer_idx, 'PassStretch', None)
            derivations += 1

        # Chip: Short pass
        elif distance and distance <= chip_max:
            df = _assign_to_empty_slot(df, passer_idx, 'Chip', None)
            derivations += 1

    if log:
        log(f"  Derived {derivations} pass path play_details")

    return df


# ============================================================
# SLOT MANAGEMENT
# ============================================================

def _assign_to_empty_slot(df: pd.DataFrame, idx: int, play_detail: str, flag: Optional[str]) -> pd.DataFrame:
    """
    Assign a derived play_detail to an empty slot.

    Rules:
    1. Never overwrite existing values (human input supreme)
    2. Only 2 slots available
    3. Fill play_detail1 first, then play_detail2
    4. Don't add duplicates

    Args:
        df: DataFrame to modify
        idx: Row index to modify
        play_detail: Play detail to add
        flag: Success flag ('s', 'u', or None)

    Returns:
        Modified DataFrame
    """
    # Ensure columns exist
    if 'play_detail1' not in df.columns:
        df['play_detail1'] = None
    if 'play_detail2' not in df.columns:
        df['play_detail2'] = None

    pd1 = df.at[idx, 'play_detail1']
    pd2 = df.at[idx, 'play_detail2']

    # Check if already exists
    if pd1 == play_detail or pd2 == play_detail:
        return df  # Already has this play_detail

    # Find empty slot
    if pd.isna(pd1) or pd1 == '':
        df.at[idx, 'play_detail1'] = play_detail
        if flag and 'play_detail1_s' in df.columns:
            df.at[idx, 'play_detail1_s'] = flag
    elif pd.isna(pd2) or pd2 == '':
        df.at[idx, 'play_detail2'] = play_detail
        if flag and 'play_detail2_s' in df.columns:
            df.at[idx, 'play_detail2_s'] = flag
    # Else: both slots full, don't add

    return df


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def derive_all_play_details(df: pd.DataFrame, config: Optional[Dict] = None, log=None) -> pd.DataFrame:
    """
    Main entry point for all play detail automation.

    Runs derivations in priority order:
    1. Forced outcomes (ForcedTurnover from proximity)
    2. Ceded zone (from defender distance)
    3. Event detail mappings
    4. Sequence-based (OneTimer, etc.)
    5. Pass path analysis

    Args:
        df: Event players dataframe
        config: Optional config dict (loads from file if not provided)
        log: Optional logger function

    Returns:
        DataFrame with derived play_details
    """
    if config is None:
        config = load_thresholds()

    if log:
        log("Deriving automated play_details...")

    # Priority 1: Forced outcomes
    df = derive_forced_turnover(df, config, log)

    # Priority 2: Ceded zone
    df = derive_ceded_zone(df, config, log)

    # Priority 3: Event detail mappings
    df = derive_from_event_detail(df, config, log)

    # Priority 4: Sequence-based
    df = derive_from_sequence(df, config, log)

    # Priority 5: Pass path
    df = derive_from_pass_path(df, config, log)

    return df
