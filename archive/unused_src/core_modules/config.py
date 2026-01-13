"""
=============================================================================
ETL CONFIGURATION
=============================================================================
File: src/core/modules/config.py
Version: 19.12
Created: January 9, 2026

Centralized configuration for the BenchSight ETL pipeline.
All paths, constants, and settings should be defined here.
=============================================================================
"""

from pathlib import Path

# ============================================================
# PATHS
# ============================================================

# Base directories
BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"

# Input paths
BLB_PATH = DATA_DIR / "BLB_Tables.xlsx"
GAMES_DIR = DATA_DIR / "raw" / "games"
RAW_DIR = DATA_DIR / "raw"

# Output paths
OUTPUT_DIR = DATA_DIR / "output"
DOCS_DIR = BASE_DIR / "docs"

# Config files
GAME_CONFIG_PATH = CONFIG_DIR / "game_config.json"
IMMUTABLE_FACTS_PATH = CONFIG_DIR / "IMMUTABLE_FACTS.json"
VERSION_PATH = CONFIG_DIR / "VERSION.json"

# ============================================================
# EXCLUDED GAMES
# ============================================================

# Games that should be excluded from event/shift tracking
# (they exist in BLB but have incomplete tracking data)
EXCLUDED_GAMES = {18965, 18993, 19032}

# ============================================================
# TABLE PREFIXES
# ============================================================

# Primary key prefixes for dimension tables
PK_PREFIXES = {
    'dim_player': 'P',
    'dim_team': 'TM',
    'dim_schedule': 'G',
    'dim_season': 'S',
    'dim_event_type': 'ET',
    'dim_event_detail': 'ED',
    'dim_event_detail_2': 'ED2_',
    'dim_zone': 'Z',
    'dim_period': 'PER',
    'dim_strength': 'STR',
    'dim_venue': 'VEN',
    'dim_position': 'POS',
    'dim_time_bucket': 'TB',
    'dim_danger_level': 'DL',
    'dim_shot_type': 'SHOT',
    'dim_zone_entry_type': 'ZE',
    'dim_zone_exit_type': 'ZX',
    'dim_stoppage_type': 'STOP',
    'dim_giveaway_type': 'GA',
    'dim_takeaway_type': 'TA',
    'dim_turnover_type': 'TO',
    'dim_pass_type': 'PASS',
    'dim_play_detail': 'PD',
    'dim_play_detail_2': 'PD2_',
}

# ============================================================
# COLUMN MAPPINGS
# ============================================================

# Standard column renames
COLUMN_RENAMES = {
    'game_date_time': 'game_date',
    'game_time': 'game_date',
}

# Columns to always drop (formula/helper columns ending in _)
DROP_SUFFIX = '_'

# ============================================================
# TIME BUCKETS
# ============================================================

TIME_BUCKETS = {
    'TB0001': (0, 300, 'P1_Early'),
    'TB0002': (300, 600, 'P1_Mid'),
    'TB0003': (600, 900, 'P1_Late'),
    'TB0004': (900, 1000, 'P1_Final'),
    'TB0005': (1000, 1050, 'P1_LastMin'),
    'TB0006': (1050, 1200, 'P1_Clutch'),
    'TB0007': (1200, 1500, 'P2_Early'),
    'TB0008': (1500, 1800, 'P2_Mid'),
    'TB0009': (1800, 2100, 'P2_Late'),
    'TB0010': (2100, 2200, 'P2_Final'),
    'TB0011': (2200, 2250, 'P2_LastMin'),
    'TB0012': (2250, 2400, 'P2_Clutch'),
    'TB0013': (2400, 2700, 'P3_Early'),
    'TB0014': (2700, 3000, 'P3_Mid'),
    'TB0015': (3000, 3300, 'P3_Late'),
    'TB0016': (3300, 3400, 'P3_Final'),
    'TB0017': (3400, 3450, 'P3_LastMin'),
    'TB0018': (3450, 3600, 'P3_Clutch'),
    'TB0019': (3600, 99999, 'OT'),
}

# ============================================================
# STRENGTH MAPPINGS
# ============================================================

STRENGTH_MAP = {
    (5, 5): 'STR0001',  # 5v5
    (5, 4): 'STR0002',  # PP
    (4, 5): 'STR0003',  # PK
    (4, 4): 'STR0004',  # 4v4
    (3, 5): 'STR0005',  # 3v5
    (4, 3): 'STR0006',  # 4v3 PP
    (3, 3): 'STR0007',  # 3v3
    (5, 3): 'STR0008',  # 5v3 PP
    (3, 4): 'STR0009',  # 3v4 PK
}

# ============================================================
# VALIDATION THRESHOLDS
# ============================================================

# Maximum acceptable NULL rate for critical columns
MAX_NULL_RATE = 0.01  # 1%

# Minimum rows expected in critical tables
MIN_ROWS = {
    'dim_player': 100,
    'dim_team': 10,
    'fact_events': 1000,
    'fact_shifts': 100,
}

# ============================================================
# VERSION INFO
# ============================================================

ETL_VERSION = "19.12"
ETL_NAME = "BenchSight ETL"
