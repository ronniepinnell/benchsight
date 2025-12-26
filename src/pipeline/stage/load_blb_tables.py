"""
=============================================================================
STAGE: LOAD BLB TABLES
=============================================================================
File: src/pipeline/stage/load_blb_tables.py

PURPOSE:
    Load BLB_Tables.xlsx into the STAGE layer of the database.
    Raw data with minimal transformation.

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
from src.database.connection import execute_sql
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_blb_to_stage(
    blb_file: Path,
    force_reload: bool = False
) -> Dict[str, int]:
    """
    Load all BLB tables from Excel into stage layer.
    
    Args:
        blb_file: Path to BLB_Tables.xlsx file.
        force_reload: If True, reload even if already staged.
    
    Returns:
        Dictionary mapping table names to row counts.
    """
    logger.info(f"Loading BLB tables from {blb_file}")
    
    # Check if already loaded
    if not force_reload and _check_blb_already_staged():
        logger.info("BLB tables already staged. Use force_reload=True to refresh.")
        return _get_staged_blb_counts()
    
    # Validate file exists
    if not blb_file.exists():
        raise FileNotFoundError(f"BLB file not found: {blb_file}")
    
    # Open Excel file
    xlsx = pd.ExcelFile(blb_file)
    
    results = {}
    
    # Process each sheet
    for sheet_name in xlsx.sheet_names:
        df = pd.read_excel(xlsx, sheet_name=sheet_name)
        
        # Clean the data
        df = _clean_stage_data(df)
        
        # Convert table name
        table_name = 'stg_' + sheet_name.lower().replace(' ', '_')
        
        # Load into database
        row_count = load_dataframe_to_table(df, table_name, if_exists='replace')
        
        results[table_name] = row_count
        logger.info(f"  Staged {table_name}: {row_count} rows")
    
    # Record metadata
    _record_blb_load_metadata(blb_file, results)
    
    logger.info(f"Staged {len(results)} BLB tables")
    return results


def _clean_stage_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Minimal cleaning for stage data.
    
    WHY:
        - SQLite can't handle datetime.time objects
        - Remove pandas-added index column
        - Remove unnamed columns
    
    Args:
        df: Raw DataFrame from Excel.
    
    Returns:
        Cleaned DataFrame.
    """
    # Remove 'index' column if it's just row numbers (0, 1, 2, ...)
    # WHY: Pandas adds index when reading Excel, we don't need it as a column
    if 'index' in df.columns:
        # Check if values are sequential starting from 0
        if list(df['index']) == list(range(len(df))):
            df = df.drop(columns=['index'])
    
    # Remove 'Unnamed' columns
    unnamed_cols = [c for c in df.columns if 'Unnamed' in str(c)]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)
    
    # Convert datetime/time columns to strings
    # WHY: SQLite doesn't support Python datetime.time objects
    for col in df.columns:
        if df[col].dtype == 'object':
            # Check if column contains time objects
            sample = df[col].dropna().head(1)
            if len(sample) > 0:
                val = sample.iloc[0]
                if hasattr(val, 'strftime'):
                    # Convert to string
                    df[col] = df[col].apply(
                        lambda x: x.strftime('%H:%M:%S') if hasattr(x, 'strftime') else str(x) if pd.notna(x) else None
                    )
        # Handle timedelta columns
        if pd.api.types.is_timedelta64_dtype(df[col]):
            df[col] = df[col].apply(
                lambda x: str(x) if pd.notna(x) else None
            )
        # Handle datetime columns
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].apply(
                lambda x: x.isoformat() if pd.notna(x) else None
            )
    
    return df


def _check_blb_already_staged() -> bool:
    """Check if BLB tables have already been staged."""
    key_tables = ['stg_dim_player', 'stg_dim_team', 'stg_fact_gameroster']
    return all(table_exists(t) for t in key_tables)


def _get_staged_blb_counts() -> Dict[str, int]:
    """Get row counts for already-staged BLB tables."""
    from src.database.table_operations import get_tables_by_layer
    
    result = {}
    stage_tables = get_tables_by_layer('stage')
    
    for table in stage_tables:
        if table.startswith('stg_dim_') or table.startswith('stg_fact_'):
            result[table] = get_row_count(table)
    
    return result


def _record_blb_load_metadata(blb_file: Path, results: Dict[str, int]) -> None:
    """Record metadata about this BLB load."""
    execute_sql("""
        CREATE TABLE IF NOT EXISTS _blb_load_metadata (
            load_id INTEGER PRIMARY KEY AUTOINCREMENT,
            load_timestamp TEXT NOT NULL,
            source_file TEXT NOT NULL,
            tables_loaded INTEGER NOT NULL,
            total_rows INTEGER NOT NULL
        )
    """)
    
    execute_sql("""
        INSERT INTO _blb_load_metadata 
        (load_timestamp, source_file, tables_loaded, total_rows)
        VALUES (:timestamp, :source, :tables, :rows)
    """, {
        'timestamp': datetime.now().isoformat(),
        'source': str(blb_file),
        'tables': len(results),
        'rows': sum(results.values())
    })


def get_last_blb_load_info() -> Dict:
    """Get information about the last BLB load."""
    from src.database.table_operations import table_exists
    from src.database.connection import get_connection
    from sqlalchemy import text
    
    if not table_exists('_blb_load_metadata'):
        return None
    
    with get_connection() as conn:
        result = conn.execute(text("""
            SELECT load_timestamp, source_file, tables_loaded, total_rows
            FROM _blb_load_metadata
            ORDER BY load_id DESC
            LIMIT 1
        """))
        row = result.fetchone()
        
        if row:
            return {
                'load_timestamp': row[0],
                'source_file': row[1],
                'tables_loaded': row[2],
                'total_rows': row[3]
            }
    
    return None
