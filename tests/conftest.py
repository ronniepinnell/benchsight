"""
=============================================================================
PYTEST FIXTURES
=============================================================================
File: tests/conftest.py

PURPOSE:
    Shared fixtures for all tests.
    Database setup/teardown, sample data creation.

=============================================================================
"""

import pytest
import pandas as pd
from pathlib import Path
import sys
import os

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Use SQLite for all tests
os.environ['DB_TYPE'] = 'sqlite'


@pytest.fixture(scope='function')
def db_engine():
    """
    Provide a fresh database engine for each test.
    
    Yields:
        SQLAlchemy Engine instance.
    """
    from src.database.connection import get_engine, close_engine
    
    # Ensure clean state
    close_engine()
    
    # Create fresh engine
    engine = get_engine(db_type='sqlite')
    
    yield engine
    
    # Cleanup after test
    close_engine()


@pytest.fixture(scope='function')
def sample_player_df():
    """
    Provide sample player DataFrame for testing.
    
    Returns:
        DataFrame with sample player data.
    """
    return pd.DataFrame({
        'player_id': ['P001', 'P002', 'P003'],
        'player_full_name': ['Alice Smith', 'Bob Jones', 'Charlie Brown'],
        'random_player_full_name': ['Jane Doe', 'John Smith', 'Jim Davis'],
        'player_primary_position': ['F', 'D', 'G'],
        'current_skill_rating': [5.0, 4.0, 3.5],
        'player_hand': ['L', 'R', 'L'],
        'birth_year': [1990, 1985, 1995]
    })


@pytest.fixture(scope='function')
def sample_team_df():
    """
    Provide sample team DataFrame for testing.
    
    Returns:
        DataFrame with sample team data.
    """
    return pd.DataFrame({
        'team_id': ['T001', 'T002'],
        'team_name': ['Red Team', 'Blue Team'],
        'long_team_name': ['The Red Team', 'The Blue Team'],
        'team_cd': ['RED', 'BLU'],
        'league': ['NORAD', 'NORAD']
    })


@pytest.fixture(scope='function')
def sample_game_df():
    """
    Provide sample game schedule DataFrame.
    
    Returns:
        DataFrame with sample schedule data.
    """
    return pd.DataFrame({
        'game_id': [1001, 1002],
        'season_id': ['S2024', 'S2024'],
        'game_date': ['2024-01-15', '2024-01-22'],
        'home_team_name': ['Red Team', 'Blue Team'],
        'away_team_name': ['Blue Team', 'Red Team'],
        'home_total_goals': [3, 2],
        'away_total_goals': [2, 4],
        'game_type': ['Regular', 'Regular']
    })


@pytest.fixture(scope='function')
def sample_events_df():
    """
    Provide sample events DataFrame for testing.
    
    Returns:
        DataFrame with sample event data.
    """
    return pd.DataFrame({
        'event_index': [1, 2, 3, 4, 5],
        'shift_index': [1, 1, 1, 2, 2],
        'Type': ['Faceoff', 'Pass', 'Shot', 'Turnover', 'Shot'],
        'event_detail': ['Faceoff_Won', 'Pass_Completed', 'Goal_Scored', 
                         'Turnover_Giveaway', 'Shot_Saved'],
        'event_successful': ['s', 's', 's', 'u', 'u'],
        'period': [1, 1, 1, 1, 1],
        'event_start_min': [0, 0, 1, 2, 3],
        'event_start_sec': [0, 30, 15, 0, 30],
        'player_game_number': [10, 10, 10, 20, 10],
        'player_id': ['P001', 'P001', 'P001', 'P002', 'P001'],
        'player_role': ['event_team_player_1'] * 5
    })


@pytest.fixture(scope='function')
def sample_shifts_df():
    """
    Provide sample shifts DataFrame for testing.
    
    Returns:
        DataFrame with sample shift data.
    """
    return pd.DataFrame({
        'shift_index': [1, 2],
        'Period': [1, 1],
        'shift_start_total_seconds': [0, 300],
        'shift_end_total_seconds': [300, 600],
        'shift_duration': [300, 300],
        'situation': ['EV', 'EV'],
        'strength': ['5v5', '5v5'],
        'home_forward_1': [10, 10],
        'home_forward_2': [11, 11],
        'home_forward_3': [12, 12],
        'home_defense_1': [20, 20],
        'home_defense_2': [21, 21],
        'home_goalie': [30, 30]
    })


@pytest.fixture(scope='function')
def staged_blb_data(db_engine, sample_player_df, sample_team_df, sample_game_df):
    """
    Load sample BLB data into stage tables.
    
    Yields:
        Dictionary of table names loaded.
    """
    from src.database.table_operations import load_dataframe_to_table
    
    load_dataframe_to_table(sample_player_df, 'stg_dim_player', 'replace')
    load_dataframe_to_table(sample_team_df, 'stg_dim_team', 'replace')
    load_dataframe_to_table(sample_game_df, 'stg_dim_schedule', 'replace')
    
    yield {
        'stg_dim_player': len(sample_player_df),
        'stg_dim_team': len(sample_team_df),
        'stg_dim_schedule': len(sample_game_df)
    }


@pytest.fixture(scope='function')
def staged_game_data(db_engine, sample_events_df, sample_shifts_df):
    """
    Load sample game tracking data into stage tables.
    
    Yields:
        Dictionary of table names loaded.
    """
    from src.database.table_operations import load_dataframe_to_table
    
    game_id = 99999
    
    sample_events_df['_game_id'] = game_id
    sample_shifts_df['game_id'] = game_id
    
    load_dataframe_to_table(sample_events_df, f'stg_events_{game_id}', 'replace')
    load_dataframe_to_table(sample_shifts_df, f'stg_shifts_{game_id}', 'replace')
    
    yield {
        'game_id': game_id,
        f'stg_events_{game_id}': len(sample_events_df),
        f'stg_shifts_{game_id}': len(sample_shifts_df)
    }
