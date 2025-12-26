"""
=============================================================================
STAGE: LOAD DIMENSION TABLES
=============================================================================
File: src/pipeline/stage/load_dimensions.py

PURPOSE:
    Load supplementary dimension tables:
    - dim_dates: Calendar date dimension from CSV
    - dim_seconds: Generated time dimension for game analysis

=============================================================================
"""

import pandas as pd
from pathlib import Path
from typing import Dict
from datetime import datetime

from src.database.table_operations import (
    load_dataframe_to_table,
    table_exists,
    get_row_count
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_dim_dates(
    dates_file: Path = None,
    force_reload: bool = False
) -> Dict[str, int]:
    """
    Load dim_dates from CSV into stage layer.
    
    WHY THIS TABLE:
        Standard date dimension for time-based analysis.
        Enables filtering by day of week, month, quarter, etc.
        Links to game dates for trend analysis.
    
    Args:
        dates_file: Path to dim_dates.csv file.
        force_reload: If True, reload even if already staged.
    
    Returns:
        Dictionary with table name and row count.
    """
    logger.info("Loading dim_dates to stage")
    
    table_name = 'stg_dim_dates'
    
    # Check if already loaded
    if not force_reload and table_exists(table_name):
        count = get_row_count(table_name)
        logger.info(f"dim_dates already staged: {count} rows")
        return {table_name: count}
    
    # Find file if not specified
    if dates_file is None:
        dates_file = Path(__file__).parent.parent.parent.parent / 'data' / 'raw' / 'dim_dates.csv'
    
    if not dates_file.exists():
        logger.warning(f"dim_dates.csv not found at {dates_file}")
        return {table_name: 0}
    
    # Read CSV
    df = pd.read_csv(dates_file)
    
    # Clean column names (lowercase, remove spaces)
    df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]
    
    # Add metadata
    df['_load_timestamp'] = datetime.now().isoformat()
    df['_source_file'] = str(dates_file.name)
    
    # Load to database
    row_count = load_dataframe_to_table(df, table_name, if_exists='replace')
    
    logger.info(f"Staged dim_dates: {row_count} rows")
    return {table_name: row_count}


def generate_dim_seconds(
    periods: int = 5,
    period_length_minutes: int = 20,
    ot_period_length_minutes: int = 10,
    force_reload: bool = False
) -> Dict[str, int]:
    """
    Generate dim_seconds table for game time analysis.
    
    WHY THIS TABLE:
        - Track events by exact second in game
        - Enable time-remaining calculations
        - Support period-specific filtering
        - Power time-series visualizations
    
    STRUCTURE:
        For each second in each period:
        - time_key: Unique identifier (period * 100000 + total_seconds)
        - period: 1, 2, 3, OT1, OT2, etc.
        - minute_in_period: 0-19 (or 0-9 for OT)
        - second_in_minute: 0-59
        - total_seconds_in_period: 0-1199 (or 0-599 for OT)
        - time_elapsed_game: Cumulative seconds from game start
        - time_remaining_period: Countdown from period end
        - time_remaining_game: Countdown from regulation end
        - formatted times (MM:SS format)
    
    Args:
        periods: Number of periods (3 regulation + OT periods).
        period_length_minutes: Length of regulation period in minutes (default 20).
        ot_period_length_minutes: Length of OT period in minutes (default 10).
        force_reload: If True, regenerate even if exists.
    
    Returns:
        Dictionary with table name and row count.
    """
    logger.info("Generating dim_seconds")
    
    table_name = 'stg_dim_seconds'
    
    # Check if already exists
    if not force_reload and table_exists(table_name):
        count = get_row_count(table_name)
        logger.info(f"dim_seconds already exists: {count} rows")
        return {table_name: count}
    
    rows = []
    cumulative_seconds = 0
    regulation_total = 3 * period_length_minutes * 60  # Total regulation seconds
    
    for period in range(1, periods + 1):
        # Determine period length
        if period <= 3:
            period_length_sec = period_length_minutes * 60
            period_name = str(period)
            period_type = 'Regulation'
        else:
            period_length_sec = ot_period_length_minutes * 60
            ot_num = period - 3
            period_name = f'OT{ot_num}' if ot_num > 1 else 'OT'
            period_type = 'Overtime'
        
        # Generate each second in the period
        for sec_in_period in range(period_length_sec):
            minute_in_period = sec_in_period // 60
            second_in_minute = sec_in_period % 60
            
            # Time remaining calculations
            time_remaining_period = period_length_sec - sec_in_period - 1
            time_remaining_reg = max(0, regulation_total - cumulative_seconds - sec_in_period - 1)
            
            # Formatted times
            elapsed_formatted = f"{minute_in_period}:{second_in_minute:02d}"
            remaining_period_min = time_remaining_period // 60
            remaining_period_sec = time_remaining_period % 60
            remaining_formatted = f"{remaining_period_min}:{remaining_period_sec:02d}"
            
            # Game time formatted (total elapsed)
            total_elapsed = cumulative_seconds + sec_in_period
            game_min = total_elapsed // 60
            game_sec = total_elapsed % 60
            game_time_formatted = f"{game_min}:{game_sec:02d}"
            
            rows.append({
                # Primary key (period * 100000 to allow for 1200+ seconds per period)
                'time_key': period * 100000 + sec_in_period,
                
                # Period info
                'period': period,
                'period_name': period_name,
                'period_type': period_type,
                
                # Time within period (ascending - clock up)
                'minute_in_period': minute_in_period,
                'second_in_minute': second_in_minute,
                'total_seconds_in_period': sec_in_period,
                'time_elapsed_period_formatted': elapsed_formatted,
                
                # Time remaining in period (descending - clock down)
                'time_remaining_period_seconds': time_remaining_period,
                'time_remaining_period_formatted': remaining_formatted,
                'minute_remaining_period': remaining_period_min,
                'second_remaining_minute': remaining_period_sec,
                
                # Game-level time (cumulative)
                'time_elapsed_game_seconds': total_elapsed,
                'time_elapsed_game_formatted': game_time_formatted,
                'time_remaining_regulation_seconds': time_remaining_reg,
                
                # Useful flags
                'is_first_minute': minute_in_period == 0,
                'is_last_minute': minute_in_period == (period_length_sec // 60 - 1),
                'is_regulation': period <= 3,
                'is_overtime': period > 3,
                
                # Metadata
                '_load_timestamp': datetime.now().isoformat()
            })
        
        cumulative_seconds += period_length_sec
    
    df = pd.DataFrame(rows)
    
    # Load to database
    row_count = load_dataframe_to_table(df, table_name, if_exists='replace')
    
    logger.info(f"Generated dim_seconds: {row_count} rows")
    return {table_name: row_count}


def load_all_supplementary_dimensions(force_reload: bool = False) -> Dict[str, int]:
    """
    Load all supplementary dimension tables.
    
    Args:
        force_reload: If True, reload all tables.
    
    Returns:
        Dictionary with all table names and row counts.
    """
    results = {}
    
    # Load dim_dates
    dates_result = load_dim_dates(force_reload=force_reload)
    results.update(dates_result)
    
    # Generate dim_seconds
    seconds_result = generate_dim_seconds(force_reload=force_reload)
    results.update(seconds_result)
    
    return results
