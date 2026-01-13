"""
Time on Ice (TOI) Calculations

Functions for calculating time-based statistics including:
- Time on ice (TOI) in seconds and minutes
- Shift duration
- Per-60 rates
"""

import pandas as pd
from typing import Optional


# =============================================================================
# TOI CALCULATIONS
# =============================================================================

def calculate_toi_seconds(
    shift_durations: pd.Series,
    default: float = 0.0
) -> pd.Series:
    """
    Calculate total time on ice in seconds from shift durations.
    
    Args:
        shift_durations: Series of shift durations in seconds
        default: Default value for missing durations
        
    Returns:
        Series of TOI in seconds
    """
    return shift_durations.fillna(default).sum() if isinstance(shift_durations, pd.Series) else default


def calculate_toi_minutes(toi_seconds: float) -> float:
    """
    Convert TOI from seconds to minutes.
    
    Args:
        toi_seconds: Time on ice in seconds
        
    Returns:
        Time on ice in minutes (rounded to 2 decimals)
    """
    if pd.isna(toi_seconds):
        return 0.0
    
    return round(toi_seconds / 60.0, 2)


def calculate_shift_duration(
    start_time: float,
    end_time: float
) -> float:
    """
    Calculate shift duration from start and end times.
    
    Duration = start_time - end_time (clock counts down)
    
    Args:
        start_time: Shift start time (seconds)
        end_time: Shift end time (seconds)
        
    Returns:
        Shift duration in seconds (clipped to >= 0)
    """
    if pd.isna(start_time) or pd.isna(end_time):
        return 0.0
    
    duration = start_time - end_time
    return max(0.0, duration)  # Clip negative durations


# =============================================================================
# PER-60 RATES
# =============================================================================

def calculate_per_60_rate(
    stat_value: float,
    toi_minutes: float,
    default: Optional[float] = None
) -> Optional[float]:
    """
    Calculate per-60 rate for a statistic.
    
    Formula: (stat_value / toi_minutes) * 60
    
    Args:
        stat_value: Statistic value (goals, assists, etc.)
        toi_minutes: Time on ice in minutes
        default: Default value if TOI is 0 (defaults to None)
        
    Returns:
        Per-60 rate, or default/None if TOI is 0
    """
    if pd.isna(stat_value) or pd.isna(toi_minutes):
        return default
    
    if toi_minutes == 0:
        return default
    
    rate = (stat_value / toi_minutes) * 60.0
    return round(rate, 2)


def calculate_per_60_from_seconds(
    stat_value: float,
    toi_seconds: float,
    default: Optional[float] = None
) -> Optional[float]:
    """
    Calculate per-60 rate using TOI in seconds.
    
    Args:
        stat_value: Statistic value
        toi_seconds: Time on ice in seconds
        default: Default value if TOI is 0
        
    Returns:
        Per-60 rate, or default/None if TOI is 0
    """
    if pd.isna(toi_seconds) or toi_seconds == 0:
        return default
    
    toi_minutes = toi_seconds / 60.0
    return calculate_per_60_rate(stat_value, toi_minutes, default)
