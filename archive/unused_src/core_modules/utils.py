"""
=============================================================================
ETL UTILITIES
=============================================================================
File: src/core/modules/utils.py
Version: 19.12
Created: January 9, 2026

Utility functions for data cleaning, transformation, and validation.
=============================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import re

from .config import OUTPUT_DIR, DROP_SUFFIX


def drop_underscore_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Handle columns ending in _ (formula/helper columns).
    - If non-underscore version exists with data, drop the underscore version
    - If non-underscore version doesn't exist or is empty, rename underscore to non-underscore
    
    Args:
        df: Input DataFrame
    
    Returns:
        Tuple of (DataFrame, list of dropped column names)
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


def drop_index_and_unnamed(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop index and unnamed columns.
    
    Args:
        df: Input DataFrame
    
    Returns:
        DataFrame with index/unnamed columns removed
    """
    cols_to_drop = [c for c in df.columns if c.startswith('Unnamed') or c == 'index']
    if cols_to_drop:
        return df.drop(columns=cols_to_drop, errors='ignore')
    return df


def clean_numeric_index(val) -> Optional[int]:
    """
    Clean and convert a value to integer index.
    
    Args:
        val: Value to clean
    
    Returns:
        Integer or None
    """
    if pd.isna(val):
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def normalize_string(s: str) -> str:
    """
    Normalize a string for comparison.
    
    Args:
        s: String to normalize
    
    Returns:
        Normalized string (lowercase, stripped, no extra spaces)
    """
    if pd.isna(s):
        return ''
    return str(s).strip().lower()


def normalize_team_name(team: str) -> str:
    """
    Normalize a team name for matching.
    
    Args:
        team: Team name
    
    Returns:
        Normalized team name
    """
    if pd.isna(team):
        return ''
    
    # Common normalizations
    team = str(team).strip().lower()
    team = team.replace('_', ' ')
    team = team.replace('-', ' ')
    team = ' '.join(team.split())  # Normalize whitespace
    
    return team


def safe_int(val, default: int = 0) -> int:
    """
    Safely convert a value to integer.
    
    Args:
        val: Value to convert
        default: Default value if conversion fails
    
    Returns:
        Integer value
    """
    if pd.isna(val):
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def safe_float(val, default: float = 0.0) -> float:
    """
    Safely convert a value to float.
    
    Args:
        val: Value to convert
        default: Default value if conversion fails
    
    Returns:
        Float value
    """
    if pd.isna(val):
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def validate_key(df: pd.DataFrame, key_col: str, table_name: str) -> bool:
    """
    Validate that a key column has no duplicates or nulls.
    
    Args:
        df: DataFrame to validate
        key_col: Name of the key column
        table_name: Name of the table (for logging)
    
    Returns:
        True if valid, False otherwise
    """
    if key_col not in df.columns:
        return False
    
    # Check for nulls
    null_count = df[key_col].isna().sum()
    if null_count > 0:
        print(f"WARNING: {table_name}.{key_col} has {null_count} NULL values")
        return False
    
    # Check for duplicates
    dupe_count = df[key_col].duplicated().sum()
    if dupe_count > 0:
        print(f"WARNING: {table_name}.{key_col} has {dupe_count} duplicate values")
        return False
    
    return True


def save_table(df: pd.DataFrame, name: str, output_dir: Path = None) -> Path:
    """
    Save a DataFrame to CSV.
    
    Args:
        df: DataFrame to save
        name: Table name (without .csv)
        output_dir: Output directory (default: OUTPUT_DIR)
    
    Returns:
        Path to saved file
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    path = output_dir / f"{name}.csv"
    df.to_csv(path, index=False)
    
    return path


def load_table(name: str, output_dir: Path = None) -> Optional[pd.DataFrame]:
    """
    Load a DataFrame from CSV.
    
    Args:
        name: Table name (without .csv)
        output_dir: Output directory (default: OUTPUT_DIR)
    
    Returns:
        DataFrame or None if not found
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR
    
    path = Path(output_dir) / f"{name}.csv"
    
    if not path.exists():
        return None
    
    return pd.read_csv(path, low_memory=False)


def merge_columns_if_missing(df: pd.DataFrame, source_df: pd.DataFrame, 
                             key_col: str, columns: List[str]) -> pd.DataFrame:
    """
    Add columns from source_df if they don't exist in df.
    
    Args:
        df: Target DataFrame
        source_df: Source DataFrame with columns to add
        key_col: Column to merge on
        columns: List of columns to add
    
    Returns:
        DataFrame with new columns added
    """
    missing_cols = [c for c in columns if c not in df.columns]
    
    if not missing_cols:
        return df
    
    # Only merge the columns we need
    merge_cols = [key_col] + missing_cols
    available_cols = [c for c in merge_cols if c in source_df.columns]
    
    if len(available_cols) <= 1:  # Only key col
        return df
    
    return df.merge(source_df[available_cols], on=key_col, how='left')


def fill_rate(series: pd.Series) -> float:
    """
    Calculate the fill rate of a series.
    
    Args:
        series: Pandas Series
    
    Returns:
        Fill rate as decimal (0.0 to 1.0)
    """
    if len(series) == 0:
        return 0.0
    return series.notna().sum() / len(series)


def fill_rate_pct(series: pd.Series) -> float:
    """
    Calculate the fill rate of a series as percentage.
    
    Args:
        series: Pandas Series
    
    Returns:
        Fill rate as percentage (0.0 to 100.0)
    """
    return fill_rate(series) * 100


def standardize_code(code: str) -> str:
    """
    Standardize a code/identifier.
    
    Args:
        code: Code to standardize
    
    Returns:
        Standardized code
    """
    if pd.isna(code):
        return ''
    
    code = str(code).strip().upper()
    code = re.sub(r'[^A-Z0-9_]', '_', code)
    code = re.sub(r'_+', '_', code)
    code = code.strip('_')
    
    return code


def get_period_from_seconds(total_seconds: float) -> int:
    """
    Get period number from total game seconds.
    
    Args:
        total_seconds: Total seconds from game start
    
    Returns:
        Period number (1, 2, 3, or 4 for OT)
    """
    if pd.isna(total_seconds):
        return 1
    
    if total_seconds < 1200:
        return 1
    elif total_seconds < 2400:
        return 2
    elif total_seconds < 3600:
        return 3
    else:
        return 4  # OT
