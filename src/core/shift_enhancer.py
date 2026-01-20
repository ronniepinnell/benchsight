#!/usr/bin/env python3
"""
Shift Enhancement Module
========================

This module handles all shift table enhancements, including:
- Adding foreign keys and derived columns to fact_shifts
- Enhancing fact_shift_players with comprehensive stats
- Calculating plus/minus and shift-level metrics

Extracted from base_etl.py for better modularity.
"""

import pandas as pd
import numpy as np
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
def enhance_shift_tables():
    """Comprehensive shift enhancement with player IDs, plus/minus, and shift stats."""
    from src.core.base_etl import enhance_shift_tables as _enhance_shift_tables
    return _enhance_shift_tables()


def enhance_shift_players():
    """v19.00 ROOT CAUSE FIX: Expand fact_shift_players from 9 to 65+ columns."""
    from src.core.base_etl import enhance_shift_players as _enhance_shift_players
    return _enhance_shift_players()


def update_roster_positions_from_shifts():
    """Build fact_player_game_position and update fact_gameroster positions for tracked games."""
    from src.core.base_etl import update_roster_positions_from_shifts as _update_roster_positions
    return _update_roster_positions()
