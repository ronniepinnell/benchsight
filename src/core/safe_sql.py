#!/usr/bin/env python3
"""
Safe SQL Utilities - Prevent SQL Injection

This module provides safe SQL query building functions that validate
inputs before interpolation.

Usage:
    from src.core.safe_sql import safe_table_name, safe_game_id, safe_query

    # Validate table name
    table = safe_table_name("fact_events")  # Returns "fact_events"
    table = safe_table_name("fact_events; DROP TABLE--")  # Raises ValueError

    # Validate game ID
    gid = safe_game_id(18969)  # Returns 18969
    gid = safe_game_id("18969")  # Returns 18969
    gid = safe_game_id("abc")  # Raises ValueError

    # Build safe query
    query = safe_query("SELECT * FROM {} WHERE game_id = {}", "fact_events", 18969)
"""

import re
import logging

logger = logging.getLogger(__name__)

# Valid table name pattern: alphanumeric and underscores only
TABLE_NAME_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')

# Valid identifier pattern (for columns, etc.)
IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

# Reserved SQL keywords that should not be used as table names
SQL_RESERVED = {
    'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
    'TABLE', 'DATABASE', 'INDEX', 'WHERE', 'FROM', 'JOIN', 'AND', 'OR',
    'NOT', 'NULL', 'TRUE', 'FALSE', 'UNION', 'EXEC', 'EXECUTE', 'TRUNCATE'
}


def safe_table_name(table_name: str) -> str:
    """
    Validate and return a safe table name.
    
    Args:
        table_name: The table name to validate
        
    Returns:
        The validated table name
        
    Raises:
        ValueError: If table name is invalid or potentially malicious
    """
    if not table_name:
        raise ValueError("Table name cannot be empty")
    
    if not isinstance(table_name, str):
        raise ValueError(f"Table name must be string, got {type(table_name)}")
    
    # Remove any whitespace
    table_name = table_name.strip()
    
    # Check for SQL injection patterns
    dangerous_patterns = [';', '--', '/*', '*/', 'DROP', 'DELETE', 'INSERT', 'UPDATE', 'EXEC']
    for pattern in dangerous_patterns:
        if pattern.upper() in table_name.upper():
            raise ValueError(f"Potentially dangerous pattern in table name: {pattern}")
    
    # Validate against pattern
    if not TABLE_NAME_PATTERN.match(table_name):
        raise ValueError(f"Invalid table name format: {table_name}")
    
    # Check against reserved words (the table name itself, not prefixes)
    base_name = table_name.upper().replace('FACT_', '').replace('DIM_', '').replace('QA_', '')
    if base_name in SQL_RESERVED:
        logger.warning(f"Table name '{table_name}' contains reserved word")
    
    return table_name


def safe_game_id(game_id) -> int:
    """
    Validate and return a safe game ID.
    
    Args:
        game_id: The game ID (int or string representation)
        
    Returns:
        The validated game ID as integer
        
    Raises:
        ValueError: If game ID is invalid
    """
    if game_id is None:
        raise ValueError("Game ID cannot be None")
    
    try:
        gid = int(game_id)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid game ID: {game_id}") from e
    
    # Reasonable bounds for game IDs
    if gid < 0 or gid > 99999999:
        raise ValueError(f"Game ID out of valid range: {gid}")
    
    return gid


def safe_identifier(identifier: str) -> str:
    """
    Validate and return a safe identifier (column name, etc.).
    
    Args:
        identifier: The identifier to validate
        
    Returns:
        The validated identifier
        
    Raises:
        ValueError: If identifier is invalid
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")
    
    if not isinstance(identifier, str):
        raise ValueError(f"Identifier must be string, got {type(identifier)}")
    
    identifier = identifier.strip()
    
    if not IDENTIFIER_PATTERN.match(identifier):
        raise ValueError(f"Invalid identifier format: {identifier}")
    
    return identifier


def safe_query(template: str, *args) -> str:
    """
    Build a safe SQL query by validating all arguments.
    
    Args:
        template: SQL template with {} placeholders
        *args: Values to substitute (will be validated)
        
    Returns:
        The safe SQL query string
        
    Example:
        safe_query("SELECT * FROM {} WHERE game_id = {}", "fact_events", 18969)
        -> "SELECT * FROM fact_events WHERE game_id = 18969"
    """
    validated_args = []
    
    for arg in args:
        if isinstance(arg, str):
            # Assume it's a table or column name
            validated_args.append(safe_table_name(arg))
        elif isinstance(arg, (int, float)):
            # Numeric values are safe
            validated_args.append(arg)
        else:
            raise ValueError(f"Unsupported argument type: {type(arg)}")
    
    return template.format(*validated_args)


def quote_string(value: str) -> str:
    """
    Safely quote a string value for SQL.
    
    Args:
        value: String value to quote
        
    Returns:
        Safely quoted string
    """
    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value)}")
    
    # Escape single quotes by doubling them
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


# Validation functions for common patterns
def validate_player_id(player_id: str) -> str:
    """Validate a player ID (format: P followed by digits)."""
    if not player_id:
        raise ValueError("Player ID cannot be empty")
    
    if not re.match(r'^P\d+$', str(player_id)):
        raise ValueError(f"Invalid player ID format: {player_id}")
    
    return str(player_id)


def validate_team_id(team_id: str) -> str:
    """Validate a team ID (format: N or T followed by digits)."""
    if not team_id:
        raise ValueError("Team ID cannot be empty")
    
    if not re.match(r'^[NT]\d+$', str(team_id)):
        raise ValueError(f"Invalid team ID format: {team_id}")
    
    return str(team_id)


if __name__ == '__main__':
    # Self-test
    print("Testing safe_sql module...")
    
    # Test safe_table_name
    assert safe_table_name("fact_events") == "fact_events"
    assert safe_table_name("dim_player") == "dim_player"
    
    try:
        safe_table_name("fact_events; DROP TABLE--")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    # Test safe_game_id
    assert safe_game_id(18969) == 18969
    assert safe_game_id("18969") == 18969
    
    try:
        safe_game_id("abc")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    # Test safe_query
    query = safe_query("SELECT * FROM {} WHERE game_id = {}", "fact_events", 18969)
    assert query == "SELECT * FROM fact_events WHERE game_id = 18969"
    
    print("All tests passed!")
