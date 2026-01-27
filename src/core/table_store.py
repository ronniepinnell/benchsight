"""
Global table store for ETL pipeline.

This allows phases to access tables created in earlier phases without reading from CSV.
This makes the ETL work from scratch even after a wipe.
"""

from pathlib import Path
from typing import Dict, Optional
import pandas as pd

# Global store for tables created during this ETL run
_table_store: Dict[str, pd.DataFrame] = {}


def store_table(name: str, df: pd.DataFrame) -> None:
    """
    Store a table in the global cache.
    
    This should be called whenever a table is created/saved during ETL.
    """
    _table_store[name] = df.copy() if df is not None else pd.DataFrame()


def get_table(name: str, output_dir: Optional[Path] = None) -> pd.DataFrame:
    """
    Get a table from cache first, then from CSV if not in cache.
    
    This is the function that should be used instead of directly reading CSV.
    It checks the in-memory cache first (for tables created in this run),
    then falls back to CSV (for tables that exist from previous runs or were
    created by other processes).
    
    Args:
        name: Table name (without .csv extension)
        output_dir: Directory to look for CSV files (default: data/output)
    
    Returns:
        DataFrame with table data, or empty DataFrame if not found
    """
    # First check cache (tables created in this run)
    if name in _table_store:
        return _table_store[name].copy()
    
    # Fall back to CSV (for tables from previous runs or external processes)
    if output_dir is None:
        output_dir = Path(__file__).parent.parent.parent / 'data' / 'output'
    
    path = output_dir / f'{name}.csv'
    if path.exists():
        try:
            df = pd.read_csv(path, low_memory=False)
            # Also cache it for future use in this run
            _table_store[name] = df
            return df
        except Exception as e:
            return pd.DataFrame()
    
    return pd.DataFrame()


def clear_store() -> None:
    """Clear the table store (useful for testing or between runs)."""
    _table_store.clear()


def get_store_size() -> int:
    """Get number of tables in store."""
    return len(_table_store)


def list_stored_tables() -> list:
    """List all table names in store."""
    return list(_table_store.keys())
