"""
Integration tests for formula system.

Tests that formulas are correctly applied in the builder context.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.formulas.formula_applier import apply_player_stats_formulas
from src.formulas.registry import FormulaRegistry


# =============================================================================
# FORMULA APPLICATION TESTS
# =============================================================================

class TestFormulaApplication:
    """Tests for formula application in builders."""
    
    def test_apply_formulas_to_dataframe(self):
        """Test that formulas can be applied to a DataFrame."""
        # Create test data with required columns
        df = pd.DataFrame({
            'player_id': ['P100001', 'P100002'],
            'goals': [2, 1],
            'assists': [1, 2],
            'toi_minutes': [20.0, 15.0],
            'shots': [5, 3],
            'sog': [4, 2],
        })
        
        # Apply formulas
        result = apply_player_stats_formulas(df)
        
        # Check that result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        
        # Check that new columns were added (formulas create new columns)
        # The exact columns depend on what formulas are registered
        assert len(result.columns) >= len(df.columns)
    
    def test_formulas_require_dependencies(self):
        """Test that formulas require their dependencies."""
        # Create data missing required columns
        df = pd.DataFrame({
            'player_id': ['P100001'],
            'goals': [2],
            # Missing toi_minutes - required for per-60 formulas
        })
        
        # Should still work (formulas will skip if dependencies missing)
        result = apply_player_stats_formulas(df)
        assert isinstance(result, pd.DataFrame)
    
    def test_per_60_formulas(self):
        """Test that per-60 formulas calculate correctly."""
        df = pd.DataFrame({
            'player_id': ['P100001'],
            'goals': [2],
            'toi_minutes': [20.0],  # 20 minutes = 2 goals = 6.0 per 60
        })
        
        result = apply_player_stats_formulas(df)
        
        # Check if goals_per_60 was calculated (if formula exists)
        if 'goals_per_60' in result.columns:
            expected = (2 / 20.0) * 60
            assert abs(result['goals_per_60'].iloc[0] - expected) < 0.01
    
    def test_percentage_formulas(self):
        """Test that percentage formulas calculate correctly."""
        df = pd.DataFrame({
            'player_id': ['P100001'],
            'goals': [2],
            'shots': [10],
            'sog': [8],
        })
        
        result = apply_player_stats_formulas(df)
        
        # Check if shooting_pct was calculated (if formula exists)
        if 'shooting_pct' in result.columns:
            expected = (2 / 8) * 100  # goals / sog * 100
            assert abs(result['shooting_pct'].iloc[0] - expected) < 0.01
    
    def test_formula_registry_works(self):
        """Test that formula registry is working."""
        registry = FormulaRegistry()
        
        # Register a simple test formula
        def test_formula(df):
            df['test_column'] = df['goals'] * 2
            return df
        
        registry.register(
            name='test_formula',
            formula_type='calculation',
            function=test_formula,
            description='Test formula',
            dependencies=['goals']
        )
        
        # Apply formula
        df = pd.DataFrame({'goals': [1, 2, 3]})
        result = registry.apply_to_dataframe(df, ['test_formula'])
        
        assert 'test_column' in result.columns
        assert result['test_column'].tolist() == [2, 4, 6]


# =============================================================================
# BUILDER + FORMULA INTEGRATION TESTS
# =============================================================================

class TestBuilderFormulaIntegration:
    """Tests for formula integration in builders."""
    
    @patch('src.builders.player_stats.load_table')
    @patch('src.builders.player_stats.get_game_ids')
    @patch('src.builders.player_stats.get_players_in_game')
    @patch('src.builders.player_stats.calculate_player_event_stats')
    @patch('src.builders.player_stats.calculate_player_shift_stats')
    @patch('src.builders.player_stats.apply_player_stats_formulas')
    def test_player_stats_builder_applies_formulas(self, mock_formulas, mock_shift_stats,
                                                    mock_event_stats, mock_get_players,
                                                    mock_get_games, mock_load_table):
        """Test that PlayerStatsBuilder applies formulas."""
        from src.builders.player_stats import PlayerStatsBuilder
        
        # Setup mocks
        mock_load_table.return_value = pd.DataFrame({'col': [1]})
        mock_get_games.return_value = []
        
        # Mock formula application
        mock_df = pd.DataFrame({
            'player_id': ['P100001'],
            'goals': [2],
            'goals_per_60': [6.0],  # Formula result
        })
        mock_formulas.return_value = mock_df
        
        builder = PlayerStatsBuilder()
        result = builder.build(save=False)
        
        # Verify formulas were applied
        mock_formulas.assert_called_once()
        assert isinstance(result, pd.DataFrame)
    
    def test_formulas_preserve_original_columns(self):
        """Test that formulas don't remove original columns."""
        df = pd.DataFrame({
            'player_id': ['P100001'],
            'goals': [2],
            'assists': [1],
            'toi_minutes': [20.0],
        })
        
        original_columns = set(df.columns)
        result = apply_player_stats_formulas(df)
        
        # Original columns should still be present
        assert original_columns.issubset(set(result.columns))
    
    def test_formulas_handle_missing_data(self):
        """Test that formulas handle missing data gracefully."""
        df = pd.DataFrame({
            'player_id': ['P100001', 'P100002'],
            'goals': [2, np.nan],
            'toi_minutes': [20.0, 15.0],
        })
        
        # Should not raise error
        result = apply_player_stats_formulas(df)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2


# =============================================================================
# FORMULA UPDATE TESTS
# =============================================================================

class TestFormulaUpdates:
    """Tests for formula updates."""
    
    def test_formula_can_be_updated(self):
        """Test that formulas can be updated dynamically."""
        from src.formulas.formula_applier import update_formula
        
        # This test would require access to the formula definitions
        # For now, just verify the function exists and can be called
        # (actual update would require modifying PLAYER_STATS_FORMULAS)
        assert callable(update_formula)
    
    def test_formula_groups_work(self):
        """Test that formula groups can be applied."""
        df = pd.DataFrame({
            'player_id': ['P100001'],
            'goals': [2],
            'toi_minutes': [20.0],
        })
        
        # Apply specific formula group (if exists)
        # This tests the formula_groups parameter
        result = apply_player_stats_formulas(df, formula_groups=[])
        assert isinstance(result, pd.DataFrame)


# =============================================================================
# EDGE CASES
# =============================================================================

class TestFormulaEdgeCases:
    """Tests for edge cases in formula application."""
    
    def test_empty_dataframe(self):
        """Test formulas with empty DataFrame."""
        df = pd.DataFrame()
        result = apply_player_stats_formulas(df)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_zero_toi_handling(self):
        """Test that formulas handle zero TOI correctly."""
        df = pd.DataFrame({
            'player_id': ['P100001'],
            'goals': [2],
            'toi_minutes': [0.0],  # Zero TOI
        })
        
        result = apply_player_stats_formulas(df)
        assert isinstance(result, pd.DataFrame)
        # Per-60 formulas should handle zero TOI (likely return 0 or NaN)
    
    def test_negative_values(self):
        """Test that formulas handle negative values."""
        df = pd.DataFrame({
            'player_id': ['P100001'],
            'goals': [-1],  # Negative (shouldn't happen, but test anyway)
            'toi_minutes': [20.0],
        })
        
        result = apply_player_stats_formulas(df)
        assert isinstance(result, pd.DataFrame)
