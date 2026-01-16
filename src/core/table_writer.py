"""
================================================================================
BENCHSIGHT CENTRAL TABLE WRITER
================================================================================
ALL table output should go through this module.

This handles:
1. Writing to CSV (always)
2. Uploading to Supabase (when enabled)

Usage:
    from src.core.table_writer import save_output_table, enable_supabase, upload_all_tables
    
    # Option A: Upload as you go (during ETL)
    enable_supabase()
    save_output_table(df, 'fact_events')  # uploads immediately
    
    # Option B: Upload all at end (after ETL complete)
    upload_all_tables()  # uploads all CSVs from data/output/
================================================================================
"""

import pandas as pd
import numpy as np
import math
import logging
import configparser
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any

# Setup logging
log = logging.getLogger('TableWriter')

# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = Path("data/output")

# Supabase state
_supabase_enabled = False
_supabase_client = None
_supabase_batch_size = 500

# Track what's been uploaded this session
_uploaded_tables = set()


def enable_supabase() -> bool:
    """
    Enable direct Supabase upload.
    
    Call this BEFORE running ETL to enable uploads.
    """
    global _supabase_enabled, _supabase_client
    
    config_path = Path("config/config_local.ini")
    
    if not config_path.exists():
        log.error(f"Supabase config not found: {config_path}")
        return False
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    try:
        url = config.get('supabase', 'url')
        key = config.get('supabase', 'service_key')
        
        from supabase import create_client
        _supabase_client = create_client(url, key)
        _supabase_enabled = True
        _uploaded_tables.clear()
        log.info(f"Supabase upload ENABLED: {url}")
        return True
    except ImportError:
        log.error("Supabase package not installed. Run: pip install supabase --break-system-packages")
        return False
    except Exception as e:
        log.error(f"Failed to connect to Supabase: {e}")
        return False


def disable_supabase():
    """Disable Supabase upload."""
    global _supabase_enabled, _supabase_client
    _supabase_enabled = False
    _supabase_client = None
    log.info("Supabase upload DISABLED")


def is_supabase_enabled() -> bool:
    """Check if Supabase upload is enabled."""
    return _supabase_enabled


def get_uploaded_tables() -> set:
    """Get set of tables uploaded this session."""
    return _uploaded_tables.copy()


def _clean_value(val):
    """Clean a value for JSON/Supabase."""
    if val is None or pd.isna(val):
        return None
    if isinstance(val, (np.integer, np.int64, np.int32)):
        return int(val)
    if isinstance(val, (np.floating, np.float64, np.float32)):
        if np.isnan(val) or np.isinf(val):
            return None
        return float(val)
    if isinstance(val, np.bool_):
        return bool(val)
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
        return val
    if isinstance(val, str):
        if val.strip().lower() in ('nan', 'none', 'null', ''):
            return None
        return val
    return val


def _upload_df_to_supabase(df: pd.DataFrame, table_name: str) -> Tuple[int, List[str]]:
    """Upload DataFrame directly to Supabase."""
    global _supabase_client, _uploaded_tables
    
    if _supabase_client is None:
        return 0, ["Client not initialized"]
    
    errors = []
    
    # Clean column names
    df_clean = df.copy()
    df_clean.columns = [c.lower().strip().replace(' ', '_') for c in df_clean.columns]
    
    # Convert to records
    records = []
    for _, row in df_clean.iterrows():
        record = {col: _clean_value(val) for col, val in row.items()}
        records.append(record)
    
    if len(records) == 0:
        return 0, []
    
    # Upload in batches
    uploaded = 0
    for i in range(0, len(records), _supabase_batch_size):
        batch = records[i:i + _supabase_batch_size]
        try:
            _supabase_client.table(table_name).insert(batch).execute()
            uploaded += len(batch)
        except Exception as e:
            errors.append(f"Batch {i}: {str(e)[:80]}")
    
    if uploaded > 0:
        _uploaded_tables.add(table_name)
    
    return uploaded, errors


def save_output_table(df: pd.DataFrame, table_name: str, output_dir: Optional[Path] = None, optimize_dtypes: bool = True) -> Tuple[int, int]:
    """
    Save a table to CSV and optionally upload to Supabase.
    
    This is the SINGLE function all ETL modules should use to save output tables.
    
    Args:
        df: DataFrame to save
        table_name: Name of the table (without .csv extension)
        output_dir: Optional output directory (default: data/output)
        optimize_dtypes: Whether to optimize data types before saving (default: True)
    
    Returns:
        Tuple of (row_count, column_count)
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Optimize data types (v29.6)
    if optimize_dtypes and len(df) > 0:
        try:
            from src.utils.data_type_optimizer import optimize_dataframe_dtypes
            df = optimize_dataframe_dtypes(df, categorical_threshold=10, optimize_floats=True)
        except Exception as e:
            # Don't fail if optimization fails - just log and continue
            log.debug(f"  Data type optimization skipped for {table_name}: {e}")
    
    # Drop 100% null columns (except coordinate/danger/xy columns) for fact tables
    if table_name.startswith('fact_') and len(df) > 0:
        try:
            from src.core.base_etl import drop_all_null_columns
            df, removed_cols = drop_all_null_columns(df)
            if removed_cols:
                log.info(f"  {table_name}: Removed {len(removed_cols)} all-null columns")
        except Exception as e:
            log.debug(f"  Null column removal skipped for {table_name}: {e}")
    
    # Upload to Supabase FIRST (if enabled)
    if _supabase_enabled and _supabase_client is not None:
        rows_uploaded, errors = _upload_df_to_supabase(df, table_name)
        if errors:
            log.warning(f"  Supabase {table_name}: {rows_uploaded} rows, {len(errors)} errors")
            for err in errors[:2]:
                log.warning(f"    {err}")
        elif rows_uploaded > 0:
            log.info(f"  Supabase: {table_name} - {rows_uploaded} rows")
    
    # Then save to CSV (always)
    csv_path = output_dir / f"{table_name}.csv"
    df.to_csv(csv_path, index=False)
    
    return len(df), len(df.columns)


def upload_all_tables(output_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Upload ALL tables from output directory to Supabase.
    
    This is meant to be called AFTER the full ETL is complete,
    to upload the final state of all tables.
    
    Args:
        output_dir: Directory containing CSVs (default: data/output)
    
    Returns:
        Dict with upload results
    """
    global _supabase_client
    
    if output_dir is None:
        output_dir = OUTPUT_DIR
    output_dir = Path(output_dir)
    
    if not _supabase_enabled or _supabase_client is None:
        if not enable_supabase():
            return {'success': False, 'error': 'Could not enable Supabase'}
    
    results = {
        'tables_attempted': 0,
        'tables_success': 0,
        'tables_failed': 0,
        'total_rows': 0,
        'errors': {}
    }
    
    csv_files = sorted(output_dir.glob('*.csv'))
    results['tables_attempted'] = len(csv_files)
    
    log.info(f"Uploading {len(csv_files)} tables to Supabase...")
    
    for csv_path in csv_files:
        table_name = csv_path.stem
        
        try:
            df = pd.read_csv(csv_path, low_memory=False)
            
            if len(df) == 0:
                log.info(f"  SKIP {table_name}: empty")
                results['tables_success'] += 1
                continue
            
            rows, errors = _upload_df_to_supabase(df, table_name)
            results['total_rows'] += rows
            
            if errors:
                results['tables_failed'] += 1
                results['errors'][table_name] = errors
                log.warning(f"  FAIL {table_name}: {len(errors)} errors")
            else:
                results['tables_success'] += 1
                log.info(f"  OK {table_name}: {rows} rows")
                
        except Exception as e:
            results['tables_failed'] += 1
            results['errors'][table_name] = [str(e)]
            log.error(f"  ERROR {table_name}: {e}")
    
    log.info(f"Upload complete: {results['tables_success']}/{results['tables_attempted']} tables, {results['total_rows']} rows")
    
    return results
