"""
=============================================================================
ETL CORE MODULES
=============================================================================
Package: src/core/modules
Version: 19.12
Created: January 9, 2026

Refactored ETL modules providing:
- Centralized configuration
- Consistent logging
- Utility functions
- Single-write table management
=============================================================================
"""

from .config import (
    # Paths
    BASE_DIR, DATA_DIR, CONFIG_DIR,
    BLB_PATH, GAMES_DIR, RAW_DIR,
    OUTPUT_DIR, DOCS_DIR,
    GAME_CONFIG_PATH, IMMUTABLE_FACTS_PATH, VERSION_PATH,
    
    # Constants
    EXCLUDED_GAMES,
    PK_PREFIXES,
    TIME_BUCKETS,
    STRENGTH_MAP,
    
    # Version
    ETL_VERSION, ETL_NAME,
)

from .logger import (
    ETLLogger,
    get_logger,
    reset_logger,
)

from .utils import (
    drop_underscore_columns,
    drop_index_and_unnamed,
    clean_numeric_index,
    normalize_string,
    normalize_team_name,
    safe_int,
    safe_float,
    validate_key,
    save_table,
    load_table,
    merge_columns_if_missing,
    fill_rate,
    fill_rate_pct,
    standardize_code,
    get_period_from_seconds,
)

from .table_writer import (
    TableWriter,
    SingleWriteETL,
)

__all__ = [
    # Config
    'BASE_DIR', 'DATA_DIR', 'CONFIG_DIR',
    'BLB_PATH', 'GAMES_DIR', 'RAW_DIR',
    'OUTPUT_DIR', 'DOCS_DIR',
    'GAME_CONFIG_PATH', 'IMMUTABLE_FACTS_PATH', 'VERSION_PATH',
    'EXCLUDED_GAMES',
    'PK_PREFIXES',
    'TIME_BUCKETS',
    'STRENGTH_MAP',
    'ETL_VERSION', 'ETL_NAME',
    
    # Logger
    'ETLLogger', 'get_logger', 'reset_logger',
    
    # Utils
    'drop_underscore_columns', 'drop_index_and_unnamed',
    'clean_numeric_index', 'normalize_string', 'normalize_team_name',
    'safe_int', 'safe_float', 'validate_key',
    'save_table', 'load_table', 'merge_columns_if_missing',
    'fill_rate', 'fill_rate_pct', 'standardize_code',
    'get_period_from_seconds',
    
    # Table Writer
    'TableWriter', 'SingleWriteETL',
]
