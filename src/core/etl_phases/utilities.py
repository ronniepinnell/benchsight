"""
ETL Utility Functions
=====================

Common utility functions used across the ETL pipeline:
- Column dropping and cleaning
- Key validation
- Table saving
- Venue correction

These functions are used by multiple phases and table builders.
"""

import pandas as pd
import re
from pathlib import Path

# Import central table writer for Supabase integration
from src.core.table_writer import save_output_table

# Default output directory (can be overridden)
OUTPUT_DIR = Path("data/output")


def drop_underscore_columns(df):
    """
    Handle columns ending in _ (formula/helper columns).
    - If non-underscore version exists with data, drop the underscore version
    - If non-underscore version doesn't exist or is empty, rename underscore to non-underscore

    Args:
        df: DataFrame to process

    Returns:
        Tuple of (processed DataFrame, list of dropped column names)
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
    """
    Drop index and Unnamed columns.

    Args:
        df: DataFrame to process

    Returns:
        DataFrame with index and Unnamed columns removed
    """
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
    """
    Convert '1000.0' to '1000'.

    Args:
        val: Value to clean

    Returns:
        Cleaned string value or None
    """
    if pd.isna(val) or val == '' or str(val).lower() in ['nan', 'x', 'none']:
        return None
    try:
        return str(int(float(val)))
    except Exception:
        return None


def validate_key(df, key_col, table_name):
    """
    Validate a key column has no nulls and no duplicates.

    Args:
        df: DataFrame to validate
        key_col: Name of the key column
        table_name: Name of the table (for error messages)

    Returns:
        List of validation issues (empty if valid)
    """
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


def save_table(df, name, output_dir=None):
    """
    Save table to CSV and optionally upload directly to Supabase.

    Uses the central table_writer module which handles:
    1. Uploading to Supabase (if enabled) - DataFrame goes directly, no CSV read
    2. Writing to CSV (always, for local backup)

    Args:
        df: DataFrame to save
        name: Table name (without .csv extension)
        output_dir: Output directory (optional, defaults to OUTPUT_DIR)

    Returns:
        Result from save_output_table
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR
    return save_output_table(df, name, output_dir)


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
        logger.warn(f"  VENUE SWAP DETECTED - Correcting to BLB schedule")
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

        logger.info(f"      Venue corrected")

    return df
