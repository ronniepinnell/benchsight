"""
=============================================================================
TABLE OPERATIONS
=============================================================================
File: src/database/table_operations.py

PURPOSE:
    CRUD operations for database tables.
    Load DataFrames, read tables, check existence, drop tables.

NAMING CONVENTION:
    Tables use prefixes to indicate their ETL layer:
    - stg_*  : Stage layer (raw data)
    - int_*  : Intermediate layer (cleaned/enriched)
    - (none) : Datamart layer (final analytical tables)

=============================================================================
"""

import pandas as pd
from src.core.safe_sql import safe_table_name
from typing import List, Optional
from datetime import datetime

from sqlalchemy import text, inspect

from src.database.connection import get_engine, get_connection
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_dataframe_to_table(
    df: pd.DataFrame, 
    table_name: str, 
    if_exists: str = 'replace'
) -> int:
    """
    Load a pandas DataFrame into a database table.
    
    WHY THIS FUNCTION:
        Central place for all DataFrame-to-table loading.
        Ensures consistent logging and error handling.
    
    HOW IT WORKS:
        1. Get database engine
        2. Use pandas to_sql() for efficient bulk insert
        3. Log the operation with row count
        4. Return row count for verification
    
    Args:
        df: DataFrame to load into the database.
            Column names become table column names.
        table_name: Name of target table (e.g., 'stg_events').
            Will be created if doesn't exist.
        if_exists: How to handle existing table:
            - 'replace': Drop and recreate (default)
            - 'append': Add rows to existing table
            - 'fail': Raise error if table exists
    
    Returns:
        Number of rows loaded (for verification).
    
    Example:
        df = pd.DataFrame({'id': [1, 2], 'name': ['A', 'B']})
        rows = load_dataframe_to_table(df, 'stg_players', 'replace')
        print(f"Loaded {rows} rows")
    """
    # Get the SQLAlchemy engine
    engine = get_engine()
    
    # Use pandas to_sql for efficient loading
    # WHY to_sql(): Handles type inference, bulk inserts, table creation
    # WHY index=False: Don't add pandas index as a column
    df.to_sql(
        name=table_name,      # Target table name
        con=engine,           # Database connection
        if_exists=if_exists,  # Replace/append/fail
        index=False           # Don't include DataFrame index
    )
    
    # Log the operation
    # WHY log: Audit trail for debugging and monitoring
    logger.info(f"Loaded {len(df)} rows into {table_name}")
    
    return len(df)


def read_table(table_name: str) -> pd.DataFrame:
    """
    Read entire table into a pandas DataFrame.
    
    WHY THIS FUNCTION:
        Clean interface for reading tables.
        Consistent error handling.
    
    HOW IT WORKS:
        1. Get database engine
        2. Use pandas read_sql_table()
        3. Return DataFrame with all rows and columns
    
    Args:
        table_name: Name of table to read.
    
    Returns:
        DataFrame containing all table data.
    
    Raises:
        ValueError: If table doesn't exist.
    
    Example:
        df = read_table('stg_events')
        print(f"Read {len(df)} rows")
    """
    # Check if table exists first
    # WHY: Give better error message than SQLAlchemy's default
    if not table_exists(table_name):
        raise ValueError(f"Table '{table_name}' does not exist")
    
    # Get engine and read table
    engine = get_engine()
    
    # WHY read_sql_table: More efficient than SELECT * for full table
    return pd.read_sql_table(table_name, engine)


def read_query(sql: str, params: dict = None) -> pd.DataFrame:
    """
    Execute SQL query and return results as DataFrame.
    
    WHY THIS FUNCTION:
        For complex queries that can't use read_table().
        Supports parameterized queries for safety.
    
    HOW IT WORKS:
        1. Open database connection
        2. Execute SQL with pandas read_sql()
        3. Return results as DataFrame
    
    Args:
        sql: SQL SELECT statement.
        params: Optional parameters for query.
    
    Returns:
        DataFrame with query results.
    
    Example:
        df = read_query(
            "SELECT * FROM players WHERE skill > :min_skill",
            {'min_skill': 4}
        )
    """
    with get_connection() as conn:
        # WHY text(): Wraps SQL for parameter binding
        return pd.read_sql(text(sql), conn, params=params)


def table_exists(table_name: str) -> bool:
    """
    Check if a table exists in the database.
    
    WHY THIS FUNCTION:
        Avoid errors when dropping non-existent tables.
        Check before loading to decide replace vs append.
    
    HOW IT WORKS:
        1. Get SQLAlchemy inspector (metadata reader)
        2. Get list of all table names
        3. Check if target table is in list
    
    Args:
        table_name: Name of table to check.
    
    Returns:
        True if table exists, False otherwise.
    """
    # Get engine and create inspector
    engine = get_engine()
    
    # WHY inspect(): SQLAlchemy's way to read database metadata
    inspector = inspect(engine)
    
    # Get all table names and check membership
    return table_name in inspector.get_table_names()


def get_all_tables() -> List[str]:
    """
    Get list of all tables in the database.
    
    WHY THIS FUNCTION:
        For status reporting and cleanup operations.
    
    Returns:
        List of table names.
    """
    engine = get_engine()
    inspector = inspect(engine)
    
    # Filter out internal metadata tables (start with _)
    tables = inspector.get_table_names()
    return [t for t in tables if not t.startswith('_')]


def get_tables_by_layer(layer: str) -> List[str]:
    """
    Get tables belonging to a specific ETL layer.
    
    WHY THIS FUNCTION:
        Process or clear specific layers independently.
    
    HOW IT WORKS:
        Uses table name prefixes to identify layer:
        - stg_* for stage
        - int_* for intermediate
        - no prefix for datamart
    
    Args:
        layer: One of 'stage', 'intermediate', 'datamart', 'all'.
    
    Returns:
        List of table names in that layer.
    """
    all_tables = get_all_tables()
    
    if layer == 'stage':
        # Stage tables start with stg_
        return [t for t in all_tables if t.startswith('stg_')]
    
    elif layer == 'intermediate':
        # Intermediate tables start with int_
        return [t for t in all_tables if t.startswith('int_')]
    
    elif layer == 'datamart':
        # Datamart tables have no prefix (not stg_ or int_)
        return [t for t in all_tables 
                if not t.startswith('stg_') and not t.startswith('int_')]
    
    elif layer == 'all':
        return all_tables
    
    else:
        raise ValueError(f"Unknown layer: {layer}. Use 'stage', 'intermediate', 'datamart', or 'all'")


def drop_table(table_name: str) -> bool:
    """
    Drop a table if it exists.
    
    WHY THIS FUNCTION:
        Clean removal of tables during development or reset.
    
    HOW IT WORKS:
        1. Check if table exists
        2. If yes, execute DROP TABLE
        3. Return whether table was dropped
    
    Args:
        table_name: Name of table to drop.
    
    Returns:
        True if table was dropped, False if it didn't exist.
    """
    if not table_exists(table_name):
        logger.debug(f"Table {table_name} doesn't exist, nothing to drop")
        return False
    
    with get_connection() as conn:
        # WHY IF EXISTS: Prevents error if table was deleted between check and drop
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
    
    logger.info(f"Dropped table: {table_name}")
    return True


def clear_layer(layer: str) -> int:
    """
    Drop all tables in a specific ETL layer.
    
    WHY THIS FUNCTION:
        Reset a layer to reprocess data.
        Clean up during development.
    
    Args:
        layer: 'stage', 'intermediate', or 'datamart'.
    
    Returns:
        Number of tables dropped.
    """
    tables = get_tables_by_layer(layer)
    
    for table in tables:
        drop_table(table)
    
    logger.info(f"Cleared {len(tables)} tables from {layer} layer")
    return len(tables)


def get_row_count(table_name: str) -> int:
    """
    Get number of rows in a table.
    
    WHY THIS FUNCTION:
        Quick count without loading full table.
        For status reporting and validation.
    
    Args:
        table_name: Name of table.
    
    Returns:
        Number of rows.
    """
    if not table_exists(table_name):
        return 0
    
    with get_connection() as conn:
        # WHY COUNT(*): Most efficient way to count rows
        # Validate table name to prevent SQL injection
        validated_table = safe_table_name(table_name)
        result = conn.execute(text(f"SELECT COUNT(*) FROM {validated_table}"))
        return result.scalar()
