"""
Unit tests for table builders.

Tests the builder classes extracted in v29.4:
- PlayerStatsBuilder
- TeamStatsBuilder
- GoalieStatsBuilder
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

from src.builders.player_stats import PlayerStatsBuilder
from src.builders.team_stats import TeamStatsBuilder
from src.builders.goalie_stats import GoalieStatsBuilder


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_data():
    """Create mock data for testing."""
    return {
        'event_players': pd.DataFrame({
            'event_id': ['E1', 'E2', 'E3'],
            'game_id': [18969, 18969, 18969],
            'player_id': ['P100001', 'P100001', 'P100002'],
            'event_type': ['Goal', 'Shot', 'Pass'],
            'event_detail': ['Goal_Scored', 'Shot_OnNet', 'Pass_Completed'],
        }),
        'events': pd.DataFrame({
            'event_id': ['E1', 'E2', 'E3'],
            'game_id': [18969, 18969, 18969],
            'event_type': ['Goal', 'Shot', 'Pass'],
        }),
        'shifts': pd.DataFrame({
            'shift_id': ['SH1', 'SH2'],
            'game_id': [18969, 18969],
            'shift_duration': [60, 45],
        }),
        'shift_players': pd.DataFrame({
            'shift_id': ['SH1', 'SH2'],
            'game_id': [18969, 18969],
            'player_id': ['P100001', 'P100001'],
            'toi_seconds': [60, 45],
        }),
        'roster': pd.DataFrame({
            'game_id': [18969, 18969],
            'player_id': ['P100001', 'P100002'],
            'team_id': ['T1', 'T2'],
            'team_name': ['Team1', 'Team2'],
            'player_position': ['Forward', 'Defense'],
        }),
        'players': pd.DataFrame({
            'player_id': ['P100001', 'P100002'],
            'player_full_name': ['Player One', 'Player Two'],
        }),
        'schedule': pd.DataFrame({
            'game_id': [18969],
            'season_id': ['S2024'],
        }),
        'zone_entry_types': pd.DataFrame({
            'zone_entry_type_id': ['ZE01'],
            'zone_entry_type_name': ['Carried'],
        }),
        'zone_exit_types': pd.DataFrame({
            'zone_exit_type_id': ['ZX01'],
            'zone_exit_type_name': ['Carried'],
        }),
        'registration': pd.DataFrame({
            'player_id': ['P100001', 'P100002'],
            'skill_rating': [4.5, 3.8],
        }),
    }


# =============================================================================
# PLAYER STATS BUILDER TESTS
# =============================================================================

class TestPlayerStatsBuilder:
    """Tests for PlayerStatsBuilder."""
    
    def test_init(self, temp_output_dir):
        """Test builder initialization."""
        builder = PlayerStatsBuilder(output_dir=temp_output_dir)
        assert builder.output_dir == temp_output_dir
    
    def test_init_default_output_dir(self):
        """Test builder initialization with default output dir."""
        builder = PlayerStatsBuilder()
        assert builder.output_dir is not None
    
    @patch('src.builders.player_stats.load_table')
    def test_load_data(self, mock_load_table, temp_output_dir):
        """Test data loading."""
        mock_load_table.return_value = pd.DataFrame()
        builder = PlayerStatsBuilder(output_dir=temp_output_dir)
        data = builder.load_data()
        
        assert isinstance(data, dict)
        assert 'event_players' in data
        assert 'events' in data
        assert 'shifts' in data
        assert 'shift_players' in data
        assert 'roster' in data
        assert 'players' in data
        assert 'schedule' in data
        assert 'zone_entry_types' in data
        assert 'zone_exit_types' in data
        assert 'registration' in data
    
    def test_validate_data_empty_event_players(self, temp_output_dir):
        """Test validation fails when event_players is empty."""
        builder = PlayerStatsBuilder(output_dir=temp_output_dir)
        data = {'event_players': pd.DataFrame()}
        
        assert builder.validate_data(data) == False
    
    def test_validate_data_valid(self, temp_output_dir):
        """Test validation passes with valid data."""
        builder = PlayerStatsBuilder(output_dir=temp_output_dir)
        data = {'event_players': pd.DataFrame({'col': [1, 2, 3]})}
        
        assert builder.validate_data(data) == True
    
    @patch('src.builders.player_stats.calculate_player_event_stats')
    @patch('src.builders.player_stats.calculate_player_shift_stats')
    @patch('src.builders.player_stats.calculate_advanced_shift_stats')
    @patch('src.builders.player_stats.calculate_zone_entry_exit_stats')
    @patch('src.builders.player_stats.calculate_faceoff_zone_stats')
    @patch('src.builders.player_stats.calculate_period_splits')
    @patch('src.builders.player_stats.calculate_danger_zone_stats')
    @patch('src.builders.player_stats.calculate_rush_stats')
    @patch('src.builders.player_stats.calculate_micro_stats')
    @patch('src.builders.player_stats.calculate_xg_stats')
    @patch('src.builders.player_stats.calculate_strength_splits')
    @patch('src.builders.player_stats.calculate_shot_type_stats')
    @patch('src.builders.player_stats.calculate_pass_type_stats')
    @patch('src.builders.player_stats.calculate_playmaking_stats')
    @patch('src.builders.player_stats.calculate_pressure_stats')
    @patch('src.builders.player_stats.calculate_competition_tier_stats')
    @patch('src.builders.player_stats.calculate_game_state_stats')
    @patch('src.builders.player_stats.calculate_linemate_stats')
    @patch('src.builders.player_stats.calculate_time_bucket_stats')
    @patch('src.builders.player_stats.calculate_rebound_stats')
    @patch('src.builders.player_stats.calculate_game_score')
    @patch('src.builders.player_stats.calculate_war_stats')
    @patch('src.builders.player_stats.calculate_performance_vs_rating')
    @patch('src.builders.player_stats.calculate_relative_stats')
    def test_build_player_stats(self, mock_relative, mock_perf, mock_war, mock_score,
                                 mock_rebound, mock_time, mock_linemate, mock_state,
                                 mock_comp, mock_pressure, mock_playmaking, mock_pass,
                                 mock_shot, mock_strength, mock_xg, mock_micro,
                                 mock_rush, mock_danger, mock_period, mock_faceoff,
                                 mock_zone, mock_advanced, mock_shift, mock_event,
                                 temp_output_dir, mock_data):
        """Test building player stats for a single player."""
        # Setup all calculation mocks to return empty dicts
        for mock_func in [mock_event, mock_shift, mock_advanced, mock_zone, mock_faceoff,
                         mock_period, mock_danger, mock_rush, mock_micro, mock_xg,
                         mock_strength, mock_shot, mock_pass, mock_playmaking, mock_pressure,
                         mock_comp, mock_state, mock_linemate, mock_time, mock_rebound,
                         mock_score, mock_war, mock_perf, mock_relative]:
            mock_func.return_value = {}
        
        builder = PlayerStatsBuilder(output_dir=temp_output_dir)
        stats = builder.build_player_stats('P100001', 18969, mock_data)
        
        assert isinstance(stats, dict)
        assert 'player_id' in stats
        assert 'game_id' in stats
        assert stats['player_id'] == 'P100001'
        assert stats['game_id'] == 18969
    
    @patch('src.builders.player_stats.load_table')
    @patch('src.builders.player_stats.get_game_ids')
    @patch('src.builders.player_stats.get_players_in_game')
    @patch('src.builders.player_stats.apply_player_stats_formulas')
    @patch('src.builders.player_stats.save_output_table')
    def test_build_empty_data(self, mock_save, mock_formulas, mock_get_players,
                              mock_get_games, mock_load_table, temp_output_dir):
        """Test build with empty data returns empty DataFrame."""
        mock_load_table.return_value = pd.DataFrame()
        mock_get_games.return_value = []
        
        builder = PlayerStatsBuilder(output_dir=temp_output_dir)
        result = builder.build(save=False)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


# =============================================================================
# TEAM STATS BUILDER TESTS
# =============================================================================

class TestTeamStatsBuilder:
    """Tests for TeamStatsBuilder."""
    
    def test_init(self, temp_output_dir):
        """Test builder initialization."""
        builder = TeamStatsBuilder(output_dir=temp_output_dir)
        assert builder.output_dir == temp_output_dir
    
    @patch('src.builders.team_stats.load_table')
    @patch('src.builders.team_stats.save_output_table')
    def test_build_with_data(self, mock_save, mock_load_table, temp_output_dir):
        """Test building team stats with valid data."""
        # Mock player game stats
        player_stats = pd.DataFrame({
            'game_id': [18969, 18969, 18970],
            'team_id': ['T1', 'T1', 'T2'],
            'team_name': ['Team1', 'Team1', 'Team2'],
            'goals': [2, 1, 3],
            'assists': [1, 2, 1],
            'points': [3, 3, 4],
            'shots': [5, 3, 7],
            'sog': [4, 2, 6],
            'corsi_for': [10, 8, 12],
            'corsi_against': [8, 10, 9],
        })
        
        schedule = pd.DataFrame({
            'game_id': [18969, 18970],
            'season_id': ['S2024', 'S2024'],
        })
        
        mock_load_table.side_effect = lambda name: {
            'fact_player_game_stats': player_stats,
            'dim_schedule': schedule,
        }.get(name, pd.DataFrame())
        
        builder = TeamStatsBuilder(output_dir=temp_output_dir)
        result = builder.build(save=False)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'team_id' in result.columns
        assert 'game_id' in result.columns
        assert 'goals' in result.columns
    
    @patch('src.builders.team_stats.load_table')
    def test_build_empty_player_stats(self, mock_load_table, temp_output_dir):
        """Test build with empty player stats returns empty DataFrame."""
        mock_load_table.return_value = pd.DataFrame()
        
        builder = TeamStatsBuilder(output_dir=temp_output_dir)
        result = builder.build(save=False)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    @patch('src.builders.team_stats.load_table')
    @patch('src.builders.team_stats.save_output_table')
    def test_aggregation_logic(self, mock_save, mock_load_table, temp_output_dir):
        """Test that team stats correctly aggregate player stats."""
        player_stats = pd.DataFrame({
            'game_id': [18969, 18969],
            'team_id': ['T1', 'T1'],
            'team_name': ['Team1', 'Team1'],
            'goals': [2, 1],
            'assists': [1, 2],
            'corsi_for': [10, 8],
            'corsi_against': [8, 10],
        })
        
        schedule = pd.DataFrame({
            'game_id': [18969],
            'season_id': ['S2024'],
        })
        
        mock_load_table.side_effect = lambda name: {
            'fact_player_game_stats': player_stats,
            'dim_schedule': schedule,
        }.get(name, pd.DataFrame())
        
        builder = TeamStatsBuilder(output_dir=temp_output_dir)
        result = builder.build(save=False)
        
        # Check aggregation
        team_row = result[result['team_id'] == 'T1'].iloc[0]
        assert team_row['goals'] == 3  # 2 + 1
        assert team_row['assists'] == 3  # 1 + 2
        assert team_row['corsi_for'] == 18  # 10 + 8


# =============================================================================
# GOALIE STATS BUILDER TESTS
# =============================================================================

class TestGoalieStatsBuilder:
    """Tests for GoalieStatsBuilder."""
    
    def test_init(self, temp_output_dir):
        """Test builder initialization."""
        builder = GoalieStatsBuilder(output_dir=temp_output_dir)
        assert builder.output_dir == temp_output_dir
    
    @patch('src.builders.goalie_stats._create_fact_goalie_game_stats_original')
    @patch('src.builders.goalie_stats.save_output_table')
    def test_build_delegates_to_original(self, mock_save, mock_original, temp_output_dir):
        """Test that build delegates to original function."""
        mock_df = pd.DataFrame({
            'goalie_game_key': ['GK1'],
            'game_id': [18969],
            'player_id': ['P100001'],
        })
        mock_original.return_value = mock_df
        
        builder = GoalieStatsBuilder(output_dir=temp_output_dir)
        result = builder.build(save=False)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        mock_original.assert_called_once()


# =============================================================================
# CONVENIENCE FUNCTION TESTS
# =============================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    @patch('src.builders.player_stats.PlayerStatsBuilder')
    def test_build_fact_player_game_stats(self, mock_builder_class):
        """Test convenience function for player stats."""
        from src.builders.player_stats import build_fact_player_game_stats
        
        mock_builder = Mock()
        mock_builder.build.return_value = pd.DataFrame()
        mock_builder_class.return_value = mock_builder
        
        result = build_fact_player_game_stats()
        
        assert isinstance(result, pd.DataFrame)
        mock_builder.build.assert_called_once_with(save=True)
    
    @patch('src.builders.team_stats.TeamStatsBuilder')
    def test_build_fact_team_game_stats(self, mock_builder_class):
        """Test convenience function for team stats."""
        from src.builders.team_stats import build_fact_team_game_stats
        
        mock_builder = Mock()
        mock_builder.build.return_value = pd.DataFrame()
        mock_builder_class.return_value = mock_builder
        
        result = build_fact_team_game_stats()
        
        assert isinstance(result, pd.DataFrame)
        mock_builder.build.assert_called_once_with(save=True)
    
    @patch('src.builders.goalie_stats.GoalieStatsBuilder')
    def test_build_fact_goalie_game_stats(self, mock_builder_class):
        """Test convenience function for goalie stats."""
        from src.builders.goalie_stats import build_fact_goalie_game_stats
        
        mock_builder = Mock()
        mock_builder.build.return_value = pd.DataFrame()
        mock_builder_class.return_value = mock_builder
        
        result = build_fact_goalie_game_stats()
        
        assert isinstance(result, pd.DataFrame)
        mock_builder.build.assert_called_once_with(save=True)
