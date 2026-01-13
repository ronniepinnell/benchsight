"""
Shift Table Builder

Functions to build fact_shifts table from tracking data.
"""

import pandas as pd
from pathlib import Path
from src.core.table_writer import save_output_table


def build_fact_shifts(
    shifts_tracking_df: pd.DataFrame,
    output_dir: Path,
    save: bool = True
) -> pd.DataFrame:
    """
    Build fact_shifts table from tracking data.
    
    Creates one row per shift by removing duplicates.
    
    Args:
        shifts_tracking_df: DataFrame from shifts tracking data
        output_dir: Path to output directory
        save: Whether to save the table (default: True)
        
    Returns:
        DataFrame with fact_shifts data
    """
    shifts = shifts_tracking_df.drop_duplicates(subset=['shift_id'])
    
    # Select meaningful columns
    keep_cols = [
        'shift_id', 'game_id', 'shift_index', 'Period',
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
        'home_dzone_start', 'home_dzone_end', 'home_nzone_start', 'home_nzone_end'
    ]
    
    shifts = shifts[[c for c in keep_cols if c in shifts.columns]]
    
    # Rename Period to period for consistency
    if 'Period' in shifts.columns:
        shifts = shifts.rename(columns={'Period': 'period'})
    
    if save:
        save_output_table(shifts, 'fact_shifts', output_dir)
    
    return shifts
