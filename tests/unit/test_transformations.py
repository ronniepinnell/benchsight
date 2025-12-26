"""
=============================================================================
UNIT TESTS: TRANSFORMATION MODULE
=============================================================================
File: tests/unit/test_transformations.py

PURPOSE:
    Test intermediate and datamart transformation functions.
    Verify SQL transformations execute correctly.

USAGE:
    pytest tests/unit/test_transformations.py -v

=============================================================================
"""

import pytest
import pandas as pd
from pathlib import Path
import sys
import os

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ['DB_TYPE'] = 'sqlite'


class TestBLBTransformations:
    """
    Test BLB stage to intermediate transformations.
    
    WHY THESE TESTS:
        - Verify SQL executes without errors
        - Test data enrichment
        - Ensure correct table creation
    """
    
    def setup_method(self):
        """Setup test data."""
        from src.database.connection import close_engine, get_engine
        from src.database.table_operations import load_dataframe_to_table
        
        close_engine()
        get_engine(db_type='sqlite')
        
        # Create minimal stage tables for testing
        players = pd.DataFrame({
            'player_id': ['P1', 'P2'],
            'player_full_name': ['Alice Smith', 'Bob Jones'],
            'random_player_full_name': ['Jane Doe', 'John Doe'],
            'player_primary_position': ['F', 'D'],
            'current_skill_rating': [4.5, 3.5],
            'player_hand': ['L', 'R'],
            'birth_year': [1990, 1985]
        })
        load_dataframe_to_table(players, 'stg_dim_player', 'replace')
        
        teams = pd.DataFrame({
            'team_id': ['T1', 'T2'],
            'team_name': ['Reds', 'Blues'],
            'long_team_name': ['Red Team', 'Blue Team'],
            'team_cd': ['RED', 'BLU'],
            'norad_team': [True, False],
            'csah_team': [False, True],
            'league_id': ['L1', 'L1'],
            'league': ['NORAD', 'NORAD'],
            'team_color1': ['red', 'blue'],
            'team_color2': ['white', 'white']
        })
        load_dataframe_to_table(teams, 'stg_dim_team', 'replace')
        
        schedule = pd.DataFrame({
            'game_id': [1001, 1002],
            'season': ['2024', '2024'],
            'season_id': ['S2024', 'S2024'],
            'date': ['2024-01-15', '2024-01-22'],  # Match actual BLB column name
            'home_team_name': ['Reds', 'Blues'],
            'away_team_name': ['Blues', 'Reds'],
            'home_team_id': ['T1', 'T2'],
            'away_team_id': ['T2', 'T1'],
            'game_type': ['Regular', 'Regular'],
            'playoff_round': [None, None],  # Add required column
            'home_total_goals': [3, 2],
            'away_total_goals': [2, 4]
        })
        load_dataframe_to_table(schedule, 'stg_dim_schedule', 'replace')
        
        roster = pd.DataFrame({
            'game_id': [1001, 1001, 1002],
            'player_id': ['P1', 'P2', 'P1'],
            'player_game_number': [10, 20, 10],
            'player_full_name': ['Alice Smith', 'Bob Jones', 'Alice Smith'],
            'team_name': ['Reds', 'Reds', 'Blues'],
            'opp_team_name': ['Blues', 'Blues', 'Reds'],
            'team_venue': ['home', 'home', 'away'],
            'player_position': ['F', 'D', 'F'],
            'goals': [1, 0, 2],
            'assist': [2, 1, 0],  # Match actual BLB column name
            'pim': [0, 2, 0],     # Match actual BLB column name
            'goals_against': [0, 0, 0],
            'sub': [False, False, False]  # Match actual column name
        })
        load_dataframe_to_table(roster, 'stg_fact_gameroster', 'replace')
    
    def test_transform_blb_creates_int_tables(self):
        """Test that BLB transformation creates intermediate tables."""
        from src.pipeline.intermediate.transform_blb import transform_blb_to_intermediate
        from src.database.table_operations import table_exists
        
        results = transform_blb_to_intermediate()
        
        # Should create intermediate tables
        assert 'int_dim_player' in results
        assert 'int_dim_team' in results
        assert 'int_dim_schedule' in results
        assert 'int_fact_gameroster' in results
    
    def test_player_skill_rating_defaulted(self):
        """Test that missing skill ratings get default value."""
        from src.database.table_operations import load_dataframe_to_table, read_table
        from src.pipeline.intermediate.transform_blb import transform_blb_to_intermediate
        
        # Add player with no skill rating
        players = pd.DataFrame({
            'player_id': ['P3'],
            'player_full_name': ['No Skill'],
            'random_player_full_name': [None],
            'player_primary_position': [None],
            'current_skill_rating': [None],
            'player_hand': [None],
            'birth_year': [None]
        })
        load_dataframe_to_table(players, 'stg_dim_player', 'append')
        
        transform_blb_to_intermediate()
        
        result = read_table('int_dim_player')
        p3 = result[result['player_id'] == 'P3']
        
        # Should have default skill rating of 4.0
        assert len(p3) == 1
        assert p3['skill_rating'].iloc[0] == 4.0
    
    def test_schedule_winner_calculated(self):
        """Test that winner is correctly calculated."""
        from src.pipeline.intermediate.transform_blb import transform_blb_to_intermediate
        from src.database.table_operations import read_table
        
        transform_blb_to_intermediate()
        
        schedule = read_table('int_dim_schedule')
        
        # Game 1001: Reds 3, Blues 2 -> Reds win
        game1 = schedule[schedule['game_id'] == 1001]
        assert game1['winner'].iloc[0] == 'Reds'
        
        # Game 1002: Blues 2, Reds 4 -> Reds win (away)
        game2 = schedule[schedule['game_id'] == 1002]
        assert game2['winner'].iloc[0] == 'Reds'
    
    def test_gameroster_enriched_with_skill(self):
        """Test that gameroster is enriched with skill ratings."""
        from src.pipeline.intermediate.transform_blb import transform_blb_to_intermediate
        from src.database.table_operations import read_table
        
        transform_blb_to_intermediate()
        
        roster = read_table('int_fact_gameroster')
        
        # P1 has skill 4.5
        p1_rows = roster[roster['player_id'] == 'P1']
        assert all(p1_rows['skill_rating'] == 4.5)
        
        # P2 has skill 3.5
        p2_rows = roster[roster['player_id'] == 'P2']
        assert all(p2_rows['skill_rating'] == 3.5)
    
    def test_points_calculated(self):
        """Test that points (goals + assists) is calculated."""
        from src.pipeline.intermediate.transform_blb import transform_blb_to_intermediate
        from src.database.table_operations import read_table
        
        transform_blb_to_intermediate()
        
        roster = read_table('int_fact_gameroster')
        
        # P1 in game 1001: 1 goal + 2 assists = 3 points
        p1_g1 = roster[(roster['player_id'] == 'P1') & (roster['game_id'] == 1001)]
        assert p1_g1['points'].iloc[0] == 3


class TestGameTransformations:
    """
    Test game tracking transformations.
    
    WHY THESE TESTS:
        - Verify event/shift transformation
        - Test composite key generation
        - Ensure player enrichment works
    """
    
    def setup_method(self):
        """Setup test data."""
        from src.database.connection import close_engine, get_engine
        from src.database.table_operations import load_dataframe_to_table
        
        close_engine()
        get_engine(db_type='sqlite')
        
        # Create required intermediate tables first
        players = pd.DataFrame({
            'player_id': ['P1'],
            'player_full_name': ['Test Player'],
            'display_name': ['Anon Player'],
            'primary_position': ['F'],
            'skill_rating': [4.5],
            'player_hand': ['L'],
            'birth_year': [1990],
            'is_norad': [True],
            'is_csaha': [False],
            'norad_team_id': ['T1'],
            'csaha_team_id': [None],
            'player_url': [None],
            'player_image': [None],
            '_processed_timestamp': ['2024-01-01']
        })
        load_dataframe_to_table(players, 'int_dim_player', 'replace')
        
        roster = pd.DataFrame({
            'game_id': [12345],
            'player_id': ['P1'],
            'player_game_number': [10],
            'player_game_key': ['12345_10'],
            'player_full_name': ['Test Player'],
            'display_name': ['Anon Player'],
            'team_name': ['Reds'],
            'team_venue': ['home'],
            'player_position': ['F'],
            'goals': [1],
            'assists': [2],
            'points': [3],
            'skill_rating': [4.5],
            '_processed_timestamp': ['2024-01-01']
        })
        load_dataframe_to_table(roster, 'int_fact_gameroster', 'replace')
        
        # Create stage game tables
        events = pd.DataFrame({
            'event_index': [1, 2, 3],
            'shift_index': [1, 1, 2],
            'Type': ['Shot', 'Pass', 'Shot'],
            'event_detail': ['Goal_Scored', 'Pass_Completed', 'Shot_Missed'],
            'event_detail_2': [None, None, None],
            'event_successful': ['s', 's', 'u'],
            'period': [1, 1, 2],
            'event_start_min': [5, 6, 10],
            'event_start_sec': [30, 0, 15],
            'time_start_total_seconds': [330, 360, 1215],
            'duration': [0.5, 0.3, 0.4],
            'event_team_zone': ['OZ', 'NZ', 'OZ'],
            'player_game_number': [10, 10, 10],
            'player_id': ['P1', 'P1', 'P1'],
            'player_team': ['Reds', 'Reds', 'Reds'],
            'player_role': ['event_team_player_1', 'event_team_player_1', 'event_team_player_1'],
            'play_detail1': [None, None, None],
            'play_detail_2': [None, None, None],
            'play_detail_successful': [None, None, None],
            'linked_event_index': [None, None, None],
            'sequence_index': [1, 2, 3],
            'play_index': [1, 1, 2]
        })
        load_dataframe_to_table(events, 'stg_events_12345', 'replace')
        
        shifts = pd.DataFrame({
            'shift_index': [1, 2],
            'Period': [1, 2],
            'shift_start_total_seconds': [0, 1200],
            'shift_end_total_seconds': [600, 1500],
            'shift_duration': [600, 300],
            'shift_start_type': ['Faceoff', 'Faceoff'],
            'shift_stop_type': ['Whistle', 'Whistle'],
            'situation': ['EV', 'EV'],
            'strength': ['5v5', '5v5'],
            'home_team_strength': [5, 5],
            'away_team_strength': [5, 5],
            'home_goals': [0, 1],
            'away_goals': [0, 0],
            'home_team_plus': [0, 1],
            'home_team_minus': [0, 0],
            'away_team_plus': [0, 0],
            'away_team_minus': [0, 1],
            'home_forward_1': [10, 10],
            'home_forward_2': [11, 11],
            'home_forward_3': [12, 12],
            'home_defense_1': [20, 20],
            'home_defense_2': [21, 21],
            'home_goalie': [30, 30],
            'away_forward_1': [40, 40],
            'away_forward_2': [41, 41],
            'away_forward_3': [42, 42],
            'away_defense_1': [50, 50],
            'away_defense_2': [51, 51],
            'away_goalie': [60, 60]
        })
        load_dataframe_to_table(shifts, 'stg_shifts_12345', 'replace')
    
    def test_transform_game_creates_int_tables(self):
        """Test that game transformation creates intermediate tables."""
        from src.pipeline.intermediate.transform_game import transform_game_to_intermediate
        from src.database.table_operations import table_exists
        
        results = transform_game_to_intermediate(12345)
        
        assert table_exists('int_events_12345')
        assert table_exists('int_shifts_12345')
    
    def test_event_key_generated(self):
        """Test that event keys are generated correctly."""
        from src.pipeline.intermediate.transform_game import transform_game_to_intermediate
        from src.database.table_operations import read_table
        
        transform_game_to_intermediate(12345)
        
        events = read_table('int_events_12345')
        
        # Keys should be game_id + event_index
        assert '12345_1' in events['event_key'].values
        assert '12345_2' in events['event_key'].values


class TestBoxScoreBuilder:
    """
    Test box score generation.
    
    WHY THESE TESTS:
        - Verify stat aggregation
        - Test TOI calculation
        - Ensure per-60 rates are correct
    """
    
    def setup_method(self):
        """Setup test data."""
        from src.database.connection import close_engine, get_engine
        from src.database.table_operations import load_dataframe_to_table
        
        close_engine()
        get_engine(db_type='sqlite')
        
        # Create game players
        game_players = pd.DataFrame({
            'player_game_number': [10, 20],
            'player_id': ['P1', 'P2'],
            'player_game_key': ['99999_10', '99999_20'],
            'player_full_name': ['Alice', 'Bob'],
            'display_name': ['Anon1', 'Anon2'],
            'player_team': ['Reds', 'Reds'],
            'player_venue': ['home', 'home'],
            'position': ['F', 'D'],
            'skill_rating': [4.5, 3.5],
            'game_id': [99999, 99999],
            '_processed_timestamp': ['2024-01-01', '2024-01-01']
        })
        load_dataframe_to_table(game_players, 'int_game_players_99999', 'replace')
        
        # Create events
        events = pd.DataFrame({
            'event_index': [1, 2],
            'event_key': ['99999_1', '99999_2'],
            'shift_key': ['99999_1', '99999_1'],
            'event_type': ['Shot', 'Pass'],
            'event_detail': ['Goal_Scored', 'Pass_Completed'],
            'event_detail_2': [None, None],
            'event_successful': ['s', 's'],
            'period': [1, 1],
            'event_start_min': [5, 6],
            'event_start_sec': [0, 0],
            'time_total_seconds': [300, 360],
            'duration': [0.5, 0.3],
            'event_team_zone': ['OZ', 'NZ'],
            'game_id': [99999, 99999],
            'linked_event_index': [None, None],
            'sequence_index': [1, 2],
            'play_index': [1, 1],
            '_processed_timestamp': ['2024-01-01', '2024-01-01']
        })
        load_dataframe_to_table(events, 'int_events_99999', 'replace')
        
        # Create event players
        event_players = pd.DataFrame({
            'event_index': [1, 2],
            'event_key': ['99999_1', '99999_2'],
            'player_game_number': [10, 10],
            'player_id': ['P1', 'P1'],
            'player_team': ['Reds', 'Reds'],
            'player_game_key': ['99999_10', '99999_10'],
            'player_role': ['event_team_player_1', 'event_team_player_1'],
            'play_detail1': [None, None],
            'play_detail_2': [None, None],
            'play_detail_successful': [None, None],
            'is_primary_player': [1, 1],
            'is_event_team': [1, 1],
            'event_player_key': ['99999_1_10', '99999_2_10'],
            'game_id': [99999, 99999],
            '_processed_timestamp': ['2024-01-01', '2024-01-01']
        })
        load_dataframe_to_table(event_players, 'int_event_players_99999', 'replace')
        
        # Create shifts
        shifts = pd.DataFrame({
            'shift_index': [1],
            'shift_key': ['99999_1'],
            'period': [1],
            'shift_start_total_seconds': [0],
            'shift_end_total_seconds': [600],
            'shift_duration': [600],
            'shift_start_type': ['Faceoff'],
            'shift_stop_type': ['Whistle'],
            'situation': ['EV'],
            'strength': ['5v5'],
            'home_strength': [5],
            'away_strength': [5],
            'home_goals': [1],
            'away_goals': [0],
            'home_plus': [1],
            'home_minus': [0],
            'away_plus': [0],
            'away_minus': [1],
            'home_forward_1': [10],
            'home_forward_2': [11],
            'home_forward_3': [12],
            'home_defense_1': [20],
            'home_defense_2': [21],
            'home_goalie': [30],
            'away_forward_1': [40],
            'away_forward_2': [41],
            'away_forward_3': [42],
            'away_defense_1': [50],
            'away_defense_2': [51],
            'away_goalie': [60],
            'game_id': [99999],
            '_processed_timestamp': ['2024-01-01']
        })
        load_dataframe_to_table(shifts, 'int_shifts_99999', 'replace')
    
    def test_build_box_score_creates_table(self):
        """Test that box score is created."""
        from src.pipeline.datamart.build_box_score import build_box_score_for_game
        from src.database.table_operations import table_exists
        
        rows = build_box_score_for_game(99999)
        
        assert rows > 0
        assert table_exists('fact_box_score')
    
    def test_box_score_has_correct_stats(self):
        """Test that stats are aggregated correctly."""
        from src.pipeline.datamart.build_box_score import build_box_score_for_game
        from src.database.table_operations import read_table
        
        build_box_score_for_game(99999)
        
        box = read_table('fact_box_score')
        p1 = box[box['player_game_number'] == 10]
        
        # P1 had 1 goal (event_detail = 'Goal_Scored')
        assert p1['goals'].iloc[0] == 1
        
        # P1 had 2 events (1 shot, 1 pass)
        assert p1['shots'].iloc[0] >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
