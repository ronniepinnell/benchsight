"""
Unit Tests for Goalie Calculation Functions

Tests the extracted goalie calculation functions from src/calculations/goalie_calculations.py

Version: 29.7
"""

import pytest
import pandas as pd
import numpy as np
from src.calculations.goalie_calculations import (
    calculate_goalie_core_stats,
    calculate_goalie_save_types,
    calculate_goalie_high_danger,
    calculate_goalie_rebound_control,
    calculate_goalie_period_splits,
    calculate_goalie_time_buckets,
    calculate_goalie_shot_context,
    calculate_goalie_pressure_handling,
    calculate_goalie_quality_indicators,
    calculate_goalie_composites,
    calculate_goalie_war,
)


class TestGoalieCoreStats:
    """Test core goalie statistics calculation."""
    
    def test_basic_core_stats(self):
        """Test basic core stats calculation."""
        saves = pd.DataFrame({'event_id': ['E1', 'E2', 'E3']})
        goals = pd.DataFrame({'event_id': ['G1', 'G2']})
        
        stats = calculate_goalie_core_stats(saves, goals)
        
        assert stats['saves'] == 3
        assert stats['goals_against'] == 2
        assert stats['shots_against'] == 5
        assert stats['save_pct'] == 60.0
    
    def test_perfect_save_pct(self):
        """Test perfect save percentage (no goals)."""
        saves = pd.DataFrame({'event_id': ['E1', 'E2', 'E3']})
        goals = pd.DataFrame({'event_id': []})
        
        stats = calculate_goalie_core_stats(saves, goals)
        
        assert stats['saves'] == 3
        assert stats['goals_against'] == 0
        assert stats['save_pct'] == 100.0
    
    def test_empty_data(self):
        """Test with empty data."""
        saves = pd.DataFrame({'event_id': []})
        goals = pd.DataFrame({'event_id': []})
        
        stats = calculate_goalie_core_stats(saves, goals)
        
        assert stats['saves'] == 0
        assert stats['goals_against'] == 0
        assert stats['shots_against'] == 0
        assert stats['save_pct'] == 100.0  # Default for zero shots


class TestGoalieSaveTypes:
    """Test save type breakdown calculation."""
    
    def test_save_types_detection(self):
        """Test save type detection from event_detail_2."""
        saves = pd.DataFrame({
            'event_id': ['E1', 'E2', 'E3', 'E4'],
            'event_detail_2': ['Save_Glove', 'Save_Butterfly', 'Save_Pad', 'Save_Block']
        })
        
        stats = calculate_goalie_save_types(saves)
        
        assert stats['saves_glove'] == 1
        assert stats['saves_butterfly'] == 1
        assert stats['saves_pad'] == 1
        assert stats['saves_blocker'] == 0  # 'Block' not 'blocker'
    
    def test_missing_column(self):
        """Test with missing event_detail_2 column."""
        saves = pd.DataFrame({'event_id': ['E1', 'E2']})
        
        stats = calculate_goalie_save_types(saves)
        
        assert stats['saves_glove'] == 0
        assert stats['saves_butterfly'] == 0
        assert stats['saves_pad'] == 0


class TestGoalieHighDanger:
    """Test high danger statistics calculation."""
    
    def test_high_danger_detection(self):
        """Test high danger shot detection."""
        opp_shots = pd.DataFrame({
            'event_type': ['Shot', 'Goal', 'Shot', 'Goal'],
            'danger_level': ['High', 'High', 'Medium', 'High']
        })
        
        stats = calculate_goalie_high_danger(opp_shots)
        
        assert stats['hd_shots_against'] == 3
        assert stats['hd_goals_against'] == 2
        assert stats['hd_saves'] == 1
        assert stats['hd_save_pct'] == pytest.approx(33.3, abs=0.1)
    
    def test_missing_danger_level(self):
        """Test with missing danger_level column."""
        opp_shots = pd.DataFrame({
            'event_type': ['Shot', 'Goal']
        })
        
        stats = calculate_goalie_high_danger(opp_shots)
        
        assert stats['hd_shots_against'] == 0
        assert stats['hd_goals_against'] == 0
        assert stats['hd_saves'] == 0
        assert stats['hd_save_pct'] == 100.0


class TestGoaliePeriodSplits:
    """Test period split calculations."""
    
    def test_period_splits(self):
        """Test period-by-period statistics."""
        saves = pd.DataFrame({
            'event_id': ['E1', 'E2', 'E3', 'E4'],
            'period': [1, 1, 2, 3]
        })
        goals = pd.DataFrame({
            'event_id': ['G1', 'G2'],
            'period': [1, 2]
        })
        
        stats = calculate_goalie_period_splits(saves, goals)
        
        assert stats['p1_saves'] == 2
        assert stats['p1_goals_against'] == 1
        assert stats['p1_shots_against'] == 3
        assert stats['p1_sv_pct'] == pytest.approx(66.7, abs=0.1)
        
        assert stats['p2_saves'] == 1
        assert stats['p2_goals_against'] == 1
        assert stats['p2_sv_pct'] == 50.0
        
        assert stats['p3_saves'] == 1
        assert stats['p3_goals_against'] == 0
        assert stats['p3_sv_pct'] == 100.0
    
    def test_best_worst_period(self):
        """Test best/worst period identification."""
        saves = pd.DataFrame({
            'event_id': ['E1', 'E2', 'E3'],
            'period': [1, 2, 3]
        })
        goals = pd.DataFrame({
            'event_id': ['G1', 'G2'],
            'period': [1, 2]
        })
        
        stats = calculate_goalie_period_splits(saves, goals)
        
        assert stats['best_period'] == 3  # 100% save pct (1 save, 0 goals)
        # Period 1 and 2 both have 50% save pct (1 save, 1 goal each)
        # Function picks first one found, so worst_period could be 1 or 2
        assert stats['worst_period'] in [1, 2]  # Both have 50% save pct


class TestGoalieWAR:
    """Test goalie WAR calculation."""
    
    def test_war_calculation(self):
        """Test WAR calculation with typical stats."""
        stats = {
            'goals_saved_above_avg': 2.0,
            'hd_saves': 5,
            'is_quality_start': 1,
            'saves_freeze': 10,
            'saves': 20
        }
        
        war_stats = calculate_goalie_war(stats)
        
        assert 'goalie_gar_total' in war_stats
        assert 'goalie_war' in war_stats
        assert war_stats['goalie_gar_gsaa'] == 2.0
        assert war_stats['goalie_gar_hd_bonus'] > 0
        assert war_stats['goalie_gar_qs_bonus'] > 0
    
    def test_war_with_zero_saves(self):
        """Test WAR with zero saves (edge case)."""
        stats = {
            'goals_saved_above_avg': 0,
            'hd_saves': 0,
            'is_quality_start': 0,
            'saves_freeze': 0,
            'saves': 0
        }
        
        war_stats = calculate_goalie_war(stats)
        
        assert war_stats['goalie_gar_total'] == 0.0
        assert war_stats['goalie_war'] == 0.0


class TestGoalieQualityIndicators:
    """Test quality indicator calculations."""
    
    def test_quality_start(self):
        """Test quality start detection."""
        stats = {
            'save_pct': 92.0,
            'goals_against': 3,
            'shots_against': 30
        }
        
        result = calculate_goalie_quality_indicators(stats)
        
        assert result['is_quality_start'] == 1
        assert 'expected_goals_against' in result
        assert 'goals_saved_above_avg' in result
    
    def test_bad_start(self):
        """Test bad start detection."""
        stats = {
            'save_pct': 80.0,
            'goals_against': 5,
            'shots_against': 25
        }
        
        result = calculate_goalie_quality_indicators(stats)
        
        assert result['is_bad_start'] == 1


class TestGoalieComposites:
    """Test composite rating calculations."""
    
    def test_composite_ratings(self):
        """Test composite rating calculations."""
        stats = {
            'saves': 25,
            'goals_against': 2,
            'save_pct': 92.6,
            'hd_saves': 5,
            'p3_sv_pct': 95.0,
            'late_period_sv_pct': 94.0,
            'final_minute_sv_pct': 100.0,
            'period_consistency': 2.5,
            'freeze_pct': 80.0,
            'rebound_control_rate': 75.0,
            'rebound_danger_rate': 20.0,
            'saves_glove': 8,
            'saves_blocker': 7,
            'saves_chest': 5,
            'goalie_gsax': 1.5
        }
        
        result = calculate_goalie_composites(stats)
        
        assert 'goalie_game_score' in result
        assert 'goalie_gax' in result
        assert 'goalie_gsax' in result
        assert 'clutch_rating' in result
        assert 'consistency_rating' in result
        assert 'pressure_rating' in result
        assert 'rebound_rating' in result
        assert 'positioning_rating' in result
        assert 'overall_game_rating' in result
        assert 'win_probability_added' in result
        
        # Check ranges
        assert 1.0 <= result['overall_game_rating'] <= 10.0
        assert result['clutch_rating'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
