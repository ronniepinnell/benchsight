"""
=============================================================================
DATAMART: PUBLISH DIMENSIONS
=============================================================================
File: src/pipeline/datamart/publish_dimensions.py

PURPOSE:
    Publish intermediate dimension tables to the datamart layer.
    Creates final analytical tables for Power BI consumption.

=============================================================================
"""

from pathlib import Path
from typing import Dict
from datetime import datetime

from src.database.connection import execute_sql, get_connection
from src.database.table_operations import (
    table_exists,
    get_row_count,
    load_dataframe_to_table,
    read_table,
    read_query
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def publish_blb_to_datamart() -> Dict[str, int]:
    """
    Publish BLB intermediate tables to datamart.
    
    WHY THIS FUNCTION:
        - Copy cleaned data to final layer
        - Add any final transformations
        - Make data available for Power BI
    
    Returns:
        Dictionary of table names and row counts.
    """
    logger.info("Publishing BLB tables to datamart")
    
    # Mapping: intermediate table -> datamart table
    table_map = {
        'int_dim_player': 'dim_player',
        'int_dim_team': 'dim_team',
        'int_dim_schedule': 'dim_schedule',
        'int_dim_dates': 'dim_dates',
        'int_dim_seconds': 'dim_seconds',
        'int_fact_gameroster': 'fact_gameroster'
    }
    
    results = {}
    
    for int_table, dm_table in table_map.items():
        if not table_exists(int_table):
            logger.warning(f"Source table {int_table} not found, skipping")
            continue
        
        try:
            # Read from intermediate
            df = read_table(int_table)
            
            # Add updated timestamp
            df['_updated_timestamp'] = datetime.now().isoformat()
            
            # Write to datamart
            row_count = load_dataframe_to_table(df, dm_table, if_exists='replace')
            results[dm_table] = row_count
            logger.info(f"  Published {dm_table}: {row_count} rows")
            
        except Exception as e:
            logger.error(f"Failed to publish {dm_table}: {e}")
    
    return results


def publish_static_dimensions() -> Dict[str, int]:
    """
    Create static dimension tables that don't come from source data.
    
    WHY STATIC DIMENSIONS:
        - Provide reference data for filtering
        - Standardize categorical values
        - Enable consistent reporting
    
    Returns:
        Dictionary of table names and row counts.
    """
    logger.info("Creating static dimension tables")
    
    results = {}
    timestamp = datetime.now().isoformat()
    
    # DIM_PERIOD
    execute_sql("DROP TABLE IF EXISTS dim_period")
    execute_sql("""
        CREATE TABLE dim_period (
            period_id INTEGER PRIMARY KEY,
            period_name TEXT,
            period_abbr TEXT,
            is_overtime INTEGER DEFAULT 0,
            is_shootout INTEGER DEFAULT 0,
            sort_order INTEGER,
            _updated_timestamp TEXT
        )
    """)
    execute_sql(f"""
        INSERT INTO dim_period VALUES
            (1, 'First Period', '1st', 0, 0, 1, '{timestamp}'),
            (2, 'Second Period', '2nd', 0, 0, 2, '{timestamp}'),
            (3, 'Third Period', '3rd', 0, 0, 3, '{timestamp}'),
            (4, 'Overtime', 'OT', 1, 0, 4, '{timestamp}'),
            (5, 'Shootout', 'SO', 0, 1, 5, '{timestamp}')
    """)
    results['dim_period'] = 5
    
    # DIM_EVENT_TYPE
    execute_sql("DROP TABLE IF EXISTS dim_event_type")
    execute_sql("""
        CREATE TABLE dim_event_type (
            event_type TEXT PRIMARY KEY,
            event_category TEXT,
            is_shot INTEGER DEFAULT 0,
            is_possession INTEGER DEFAULT 0,
            is_turnover INTEGER DEFAULT 0,
            is_penalty INTEGER DEFAULT 0,
            sort_order INTEGER,
            _updated_timestamp TEXT
        )
    """)
    execute_sql(f"""
        INSERT INTO dim_event_type VALUES
            ('Shot', 'Offense', 1, 1, 0, 0, 1, '{timestamp}'),
            ('Pass', 'Offense', 0, 1, 0, 0, 2, '{timestamp}'),
            ('Turnover', 'Defense', 0, 0, 1, 0, 3, '{timestamp}'),
            ('Faceoff', 'Neutral', 0, 0, 0, 0, 4, '{timestamp}'),
            ('Zone_Entry_Exit', 'Transition', 0, 1, 0, 0, 5, '{timestamp}'),
            ('Save', 'Goaltending', 0, 0, 0, 0, 6, '{timestamp}'),
            ('Penalty', 'Discipline', 0, 0, 0, 1, 7, '{timestamp}')
    """)
    results['dim_event_type'] = 7
    
    # DIM_STRENGTH
    execute_sql("DROP TABLE IF EXISTS dim_strength")
    execute_sql("""
        CREATE TABLE dim_strength (
            strength TEXT PRIMARY KEY,
            home_players INTEGER,
            away_players INTEGER,
            is_even INTEGER DEFAULT 0,
            is_powerplay INTEGER DEFAULT 0,
            is_shorthanded INTEGER DEFAULT 0,
            description TEXT,
            _updated_timestamp TEXT
        )
    """)
    execute_sql(f"""
        INSERT INTO dim_strength VALUES
            ('5v5', 5, 5, 1, 0, 0, 'Even Strength', '{timestamp}'),
            ('5v4', 5, 4, 0, 1, 0, 'Home Power Play', '{timestamp}'),
            ('4v5', 4, 5, 0, 0, 1, 'Home Shorthanded', '{timestamp}'),
            ('5v3', 5, 3, 0, 1, 0, 'Home 5-on-3 PP', '{timestamp}'),
            ('3v5', 3, 5, 0, 0, 1, 'Home 3-on-5 SH', '{timestamp}'),
            ('4v4', 4, 4, 1, 0, 0, '4-on-4', '{timestamp}'),
            ('4v3', 4, 3, 0, 1, 0, 'Home 4-on-3 PP', '{timestamp}'),
            ('3v4', 3, 4, 0, 0, 1, 'Home 3-on-4 SH', '{timestamp}'),
            ('3v3', 3, 3, 1, 0, 0, '3-on-3 Overtime', '{timestamp}')
    """)
    results['dim_strength'] = 9
    
    # DIM_POSITION
    execute_sql("DROP TABLE IF EXISTS dim_position")
    execute_sql("""
        CREATE TABLE dim_position (
            position_code TEXT PRIMARY KEY,
            position_name TEXT,
            position_type TEXT,
            is_forward INTEGER DEFAULT 0,
            is_defense INTEGER DEFAULT 0,
            is_goalie INTEGER DEFAULT 0,
            _updated_timestamp TEXT
        )
    """)
    execute_sql(f"""
        INSERT INTO dim_position VALUES
            ('C', 'Center', 'Forward', 1, 0, 0, '{timestamp}'),
            ('LW', 'Left Wing', 'Forward', 1, 0, 0, '{timestamp}'),
            ('RW', 'Right Wing', 'Forward', 1, 0, 0, '{timestamp}'),
            ('F', 'Forward', 'Forward', 1, 0, 0, '{timestamp}'),
            ('D', 'Defense', 'Defense', 0, 1, 0, '{timestamp}'),
            ('LD', 'Left Defense', 'Defense', 0, 1, 0, '{timestamp}'),
            ('RD', 'Right Defense', 'Defense', 0, 1, 0, '{timestamp}'),
            ('G', 'Goalie', 'Goalie', 0, 0, 1, '{timestamp}')
    """)
    results['dim_position'] = 8
    
    # DIM_SKILL_TIER
    execute_sql("DROP TABLE IF EXISTS dim_skill_tier")
    execute_sql("""
        CREATE TABLE dim_skill_tier (
            tier_id INTEGER PRIMARY KEY,
            tier_name TEXT,
            min_rating REAL,
            max_rating REAL,
            description TEXT,
            _updated_timestamp TEXT
        )
    """)
    execute_sql(f"""
        INSERT INTO dim_skill_tier VALUES
            (1, 'Elite', 5.5, 6.0, 'Top-tier players', '{timestamp}'),
            (2, 'Advanced', 4.5, 5.4, 'Strong players', '{timestamp}'),
            (3, 'Intermediate', 3.5, 4.4, 'Average skilled', '{timestamp}'),
            (4, 'Developing', 2.5, 3.4, 'Building skills', '{timestamp}'),
            (5, 'Beginner', 2.0, 2.4, 'New players', '{timestamp}')
    """)
    results['dim_skill_tier'] = 5
    
    # DIM_VENUE
    execute_sql("DROP TABLE IF EXISTS dim_venue")
    execute_sql("""
        CREATE TABLE dim_venue (
            venue_code TEXT PRIMARY KEY,
            venue_name TEXT,
            is_home INTEGER DEFAULT 0,
            is_away INTEGER DEFAULT 0,
            _updated_timestamp TEXT
        )
    """)
    execute_sql(f"""
        INSERT INTO dim_venue VALUES
            ('home', 'Home', 1, 0, '{timestamp}'),
            ('away', 'Away', 0, 1, '{timestamp}')
    """)
    results['dim_venue'] = 2
    
    # DIM_ZONE
    execute_sql("DROP TABLE IF EXISTS dim_zone")
    execute_sql("""
        CREATE TABLE dim_zone (
            zone_code TEXT PRIMARY KEY,
            zone_name TEXT,
            is_offensive INTEGER DEFAULT 0,
            is_defensive INTEGER DEFAULT 0,
            is_neutral INTEGER DEFAULT 0,
            _updated_timestamp TEXT
        )
    """)
    execute_sql(f"""
        INSERT INTO dim_zone VALUES
            ('OZ', 'Offensive Zone', 1, 0, 0, '{timestamp}'),
            ('DZ', 'Defensive Zone', 0, 1, 0, '{timestamp}'),
            ('NZ', 'Neutral Zone', 0, 0, 1, '{timestamp}')
    """)
    results['dim_zone'] = 3
    
    logger.info(f"Created {len(results)} static dimension tables")
    return results


def transform_supplementary_dimensions() -> Dict[str, int]:
    """
    Transform dim_dates and dim_seconds from stage to intermediate.
    
    Returns:
        Dictionary of table names and row counts.
    """
    logger.info("Transforming supplementary dimensions")
    
    sql_file = Path(__file__).parent.parent.parent / 'sql' / 'intermediate' / 'transform_dimensions.sql'
    
    if not sql_file.exists():
        logger.warning(f"SQL file not found: {sql_file}")
        return {}
    
    with open(sql_file, 'r') as f:
        sql_content = f.read()
    
    results = {}
    
    # Execute SQL statements
    for statement in sql_content.split(';'):
        statement = statement.strip()
        if not statement or statement.startswith('--'):
            continue
        
        # Skip comment-only blocks
        lines = [l.strip() for l in statement.split('\n') if l.strip()]
        if all(l.startswith('--') for l in lines):
            continue
        
        try:
            execute_sql(statement)
        except Exception as e:
            if 'no such table' not in str(e).lower():
                logger.warning(f"SQL warning: {e}")
    
    # Get row counts
    for table in ['int_dim_dates', 'int_dim_seconds']:
        if table_exists(table):
            results[table] = get_row_count(table)
            logger.info(f"  Created {table}: {results[table]} rows")
    
    return results
