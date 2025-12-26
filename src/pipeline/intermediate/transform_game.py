"""
=============================================================================
INTERMEDIATE: TRANSFORM GAME TRACKING DATA
=============================================================================
File: src/pipeline/intermediate/transform_game.py

PURPOSE:
    Execute SQL transformations to move game data from stage to intermediate.
    Handles game-specific table naming with parameterized SQL.

=============================================================================
"""

from pathlib import Path
from typing import Dict

from src.database.connection import execute_sql
from src.database.table_operations import get_row_count, table_exists
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Path to SQL template file
SQL_FILE = Path(__file__).parent.parent.parent / 'sql' / 'intermediate' / 'transform_game.sql'


def transform_game_to_intermediate(game_id: int) -> Dict[str, int]:
    """
    Transform a game's data from stage to intermediate layer.
    
    WHY THIS FUNCTION:
        Process one game at a time.
        Handle parameterized SQL with game_id substitution.
    
    HOW IT WORKS:
        1. Read SQL template
        2. Replace :game_id placeholder with actual game ID
        3. Execute all statements
        4. Return row counts
    
    Args:
        game_id: Game identifier to transform.
    
    Returns:
        Dictionary mapping table names to row counts.
    
    Example:
        results = transform_game_to_intermediate(18969)
    """
    logger.info(f"Transforming game {game_id} to intermediate layer")
    
    # Check that stage tables exist for this game
    # WHY: Give clear error if stage step was skipped
    if not table_exists(f'stg_events_{game_id}'):
        raise RuntimeError(
            f"Stage tables not found for game {game_id}. "
            f"Run load_game_to_stage() first."
        )
    
    # Check that BLB intermediate tables exist
    # WHY: Game transformation depends on player skill ratings
    if not table_exists('int_dim_player'):
        raise RuntimeError(
            "BLB intermediate tables not found. "
            "Run transform_blb_to_intermediate() first."
        )
    
    # Read and parameterize SQL
    sql_content = _read_and_parameterize_sql(game_id)
    
    # Execute statements
    _execute_statements(sql_content)
    
    # Get row counts
    results = _get_intermediate_game_counts(game_id)
    
    for table, count in results.items():
        logger.info(f"  Created {table}: {count} rows")
    
    return results


def _read_and_parameterize_sql(game_id: int) -> str:
    """
    Read SQL file and replace game_id placeholder.
    
    WHY PARAMETERIZATION:
        Each game needs its own set of tables.
        SQL template uses :game_id as placeholder.
    
    HOW IT WORKS:
        1. Read SQL template file
        2. Replace :game_id with actual game ID
        3. Return modified SQL
    
    Args:
        game_id: Game ID to substitute.
    
    Returns:
        SQL with game_id substituted.
    """
    if not SQL_FILE.exists():
        raise FileNotFoundError(f"SQL file not found: {SQL_FILE}")
    
    # Read template
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Replace placeholder
    # WHY string replace: Simpler than parameterized query for DDL
    # Note: game_id is an integer, so SQL injection is not a risk
    sql_content = sql_content.replace(':game_id', str(game_id))
    
    return sql_content


def _execute_statements(sql_content: str) -> None:
    """
    Execute multiple SQL statements.
    
    Same logic as in transform_blb.py.
    """
    statements = sql_content.split(';')
    
    for statement in statements:
        statement = statement.strip()
        
        if not statement:
            continue
        
        lines = [l.strip() for l in statement.split('\n') if l.strip()]
        if all(l.startswith('--') for l in lines):
            continue
        
        try:
            execute_sql(statement)
        except Exception as e:
            if 'no such table' not in str(e).lower():
                logger.warning(f"SQL warning: {e}")


def _get_intermediate_game_counts(game_id: int) -> Dict[str, int]:
    """
    Get row counts for intermediate game tables.
    
    Args:
        game_id: Game identifier.
    
    Returns:
        Dictionary of table names to row counts.
    """
    tables = [
        f'int_events_{game_id}',
        f'int_event_players_{game_id}',
        f'int_shifts_{game_id}',
        f'int_game_players_{game_id}'
    ]
    
    results = {}
    
    for table in tables:
        if table_exists(table):
            results[table] = get_row_count(table)
    
    return results


def remove_intermediate_game(game_id: int) -> int:
    """
    Remove intermediate tables for a specific game.
    
    WHY THIS FUNCTION:
        Clean up before reprocessing.
        Remove incorrectly processed games.
    
    Args:
        game_id: Game to remove.
    
    Returns:
        Number of tables dropped.
    """
    from src.database.table_operations import drop_table
    
    tables = [
        f'int_events_{game_id}',
        f'int_event_players_{game_id}',
        f'int_shifts_{game_id}',
        f'int_game_players_{game_id}'
    ]
    
    dropped = 0
    for table in tables:
        if drop_table(table):
            dropped += 1
    
    logger.info(f"Removed {dropped} intermediate tables for game {game_id}")
    return dropped
