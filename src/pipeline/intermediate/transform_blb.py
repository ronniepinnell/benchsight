"""
=============================================================================
INTERMEDIATE: TRANSFORM BLB TABLES
=============================================================================
File: src/pipeline/intermediate/transform_blb.py

PURPOSE:
    Execute SQL transformations to move BLB data from stage to intermediate.
    This is a thin Python wrapper around SQL transformations.

WHY SQL:
    - Transformations are declarative and readable
    - Efficient set-based operations
    - Easy to modify without Python knowledge
    - Standard language for data transformation

=============================================================================
"""

from pathlib import Path
from typing import Dict

from src.database.connection import execute_sql, get_connection
from src.database.table_operations import get_row_count, table_exists
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Path to SQL file
# WHY relative to this file: Works regardless of working directory
SQL_FILE = Path(__file__).parent.parent.parent / 'sql' / 'intermediate' / 'transform_blb.sql'


def transform_blb_to_intermediate() -> Dict[str, int]:
    """
    Transform BLB tables from stage to intermediate layer.
    
    WHY THIS FUNCTION:
        Single entry point for BLB transformation.
        Executes SQL file with all transformations.
    
    HOW IT WORKS:
        1. Read SQL file
        2. Split into individual statements
        3. Execute each statement
        4. Return row counts for verification
    
    Returns:
        Dictionary mapping table names to row counts.
        Example: {'int_dim_player': 335, 'int_dim_team': 26}
    
    Example:
        results = transform_blb_to_intermediate()
        print(f"Created {len(results)} intermediate tables")
    """
    logger.info("Transforming BLB tables to intermediate layer")
    
    # Check that stage tables exist
    # WHY: Give clear error if stage step was skipped
    if not table_exists('stg_dim_player'):
        raise RuntimeError(
            "Stage tables not found. Run stage_blb_tables() first."
        )
    
    # Read SQL file
    # WHY external file: SQL is easier to read/edit separately
    sql_content = _read_sql_file(SQL_FILE)
    
    # Execute all statements
    # WHY execute_statements: Handles multi-statement SQL
    _execute_statements(sql_content)
    
    # Get row counts for verification
    results = _get_intermediate_blb_counts()
    
    # Log results
    for table, count in results.items():
        logger.info(f"  Created {table}: {count} rows")
    
    return results


def _read_sql_file(file_path: Path) -> str:
    """
    Read SQL file contents.
    
    WHY SEPARATE FUNCTION:
        - Clear error message if file not found
        - Could add caching in future
    
    Args:
        file_path: Path to SQL file.
    
    Returns:
        SQL file contents as string.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"SQL file not found: {file_path}")
    
    # Read with UTF-8 encoding
    # WHY utf-8: Standard encoding for SQL files
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def _execute_statements(sql_content: str) -> None:
    """
    Execute multiple SQL statements from a string.
    
    WHY THIS FUNCTION:
        SQLite can't execute multiple statements in one call.
        Need to split and execute individually.
    
    HOW IT WORKS:
        1. Split on semicolons
        2. Skip empty statements and comments
        3. Execute each statement
    
    Args:
        sql_content: String containing multiple SQL statements.
    """
    # Split on semicolons
    # WHY split: SQLite executes one statement at a time
    statements = sql_content.split(';')
    
    for statement in statements:
        # Clean up whitespace
        statement = statement.strip()
        
        # Skip empty statements
        if not statement:
            continue
        
        # Skip pure comment lines
        # WHY: Comments starting with -- are not executable
        lines = [l.strip() for l in statement.split('\n') if l.strip()]
        if all(l.startswith('--') for l in lines):
            continue
        
        # Execute the statement
        try:
            execute_sql(statement)
        except Exception as e:
            # Log but don't fail on non-critical errors
            # WHY: Some statements (like DROP IF EXISTS) may "fail" safely
            if 'no such table' not in str(e).lower():
                logger.warning(f"SQL warning: {e}")


def _get_intermediate_blb_counts() -> Dict[str, int]:
    """
    Get row counts for intermediate BLB tables.
    
    WHY THIS FUNCTION:
        Verify transformations worked.
        Return consistent response format.
    
    Returns:
        Dictionary of table names to row counts.
    """
    # List of expected intermediate tables
    # WHY explicit list: Know exactly what tables to check
    expected_tables = [
        'int_dim_player',
        'int_dim_team',
        'int_dim_schedule',
        'int_fact_gameroster'
    ]
    
    results = {}
    
    for table in expected_tables:
        if table_exists(table):
            results[table] = get_row_count(table)
    
    return results
