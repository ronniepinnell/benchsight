#!/usr/bin/env python3
"""
Data Loader Module
==================

This module handles all data loading operations, including:
- Loading BLB tables from Excel
- Loading tracking data from game files
- Building player lookups

Extracted from base_etl.py for better modularity.
"""

import pandas as pd
from pathlib import Path

# Import utilities
from src.core.table_writer import save_output_table

# Import table store for in-memory access
try:
    from src.core.table_store import get_table as get_table_from_store
    TABLE_STORE_AVAILABLE = True
except ImportError:
    TABLE_STORE_AVAILABLE = False
    def get_table_from_store(name, output_dir=None):
        return pd.DataFrame()


# Import from base_etl for now (will be fully extracted later)
# This allows incremental refactoring while maintaining functionality
def load_blb_tables():
    """Load all BLB tables from Excel file."""
    from src.core.base_etl import load_blb_tables as _load_blb_tables
    return _load_blb_tables()


def load_tracking_data(player_lookup, use_parallel: bool = True):
    """Load tracking data from game files."""
    from src.core.base_etl import load_tracking_data as _load_tracking_data
    return _load_tracking_data(player_lookup, use_parallel)


def build_player_lookup(gameroster_df):
    """Build lookup for (game_id, team_name, player_number) -> player_id."""
    from src.core.base_etl import build_player_lookup as _build_player_lookup
    return _build_player_lookup(gameroster_df)
