"""
Unit tests for calculation functions.

These tests verify the core calculation logic extracted from base_etl.py.
"""

import pytest
import pandas as pd
import numpy as np
from src.calculations import (
    # Goals
    is_goal_scored,
    filter_goals,
    count_goals_for_player,
    get_goal_filter,
    # Corsi
    is_corsi_event,
    is_fenwick_event,
    is_sog_event,
    calculate_cf_pct,
    calculate_ff_pct,
    # Ratings
    calculate_team_ratings,
    calculate_rating_differential,
    get_competition_tier,
    calculate_expected_cf_pct,
    calculate_cf_pct_vs_expected,
    # Time
    calculate_toi_minutes,
    calculate_shift_duration,
    calculate_per_60_rate,
)


# =============================================================================
# GOAL CALCULATIONS TESTS
# =============================================================================

class TestGoalCalculations:
    """Tests for goal counting functions."""
    
    def test_is_goal_scored_correct(self):
        """Test goal detection with correct event type and detail."""
        assert is_goal_scored('Goal', 'Goal_Scored') == True
    
    def test_is_goal_scored_wrong_type(self):
        """Test goal detection with wrong event type."""
        assert is_goal_scored('Shot', 'Goal_Scored') == False
    
    def test_is_goal_scored_wrong_detail(self):
        """Test goal detection with wrong event detail."""
        assert is_goal_scored('Goal', 'Shot_Goal') == False
    
    def test_get_goal_filter(self):
        """Test goal filter creation."""
        events = pd.DataFrame({
            'event_type': ['Goal', 'Shot', 'Goal', 'Pass'],
            'event_detail': ['Goal_Scored', 'Shot_OnNet', 'Shot_Goal', 'Pass_Completed']
        })
        
        filter_mask = get_goal_filter(events)
        assert filter_mask.sum() == 1
        assert filter_mask.iloc[0] == True  # First Goal/Goal_Scored
    
    def test_filter_goals(self):
        """Test filtering events to only goals."""
        events = pd.DataFrame({
            'event_type': ['Goal', 'Shot', 'Goal', 'Pass'],
            'event_detail': ['Goal_Scored', 'Shot_OnNet', 'Shot_Goal', 'Pass_Completed'],
            'event_player_1': ['P1', 'P2', 'P1', 'P3']
        })
        
        goals = filter_goals(events)
        assert len(goals) == 1
        assert goals.iloc[0]['event_type'] == 'Goal'
        assert goals.iloc[0]['event_detail'] == 'Goal_Scored'
    
    def test_count_goals_for_player(self):
        """Test counting goals for a specific player."""
        events = pd.DataFrame({
            'event_type': ['Goal', 'Goal', 'Goal', 'Shot'],
            'event_detail': ['Goal_Scored', 'Goal_Scored', 'Shot_Goal', 'Shot_OnNet'],
            'event_player_1': ['P1', 'P2', 'P1', 'P1'],
            'team_id': ['T1', 'T1', 'T1', 'T1']
        })
        
        # P1 should have 2 goals (first and third are Goal_Scored)
        count = count_goals_for_player(events, 'P1')
        assert count == 2
        
        # P2 should have 1 goal
        count = count_goals_for_player(events, 'P2')
        assert count == 1


# =============================================================================
# CORSI CALCULATIONS TESTS
# =============================================================================

class TestCorsiCalculations:
    """Tests for Corsi and Fenwick calculations."""
    
    def test_is_sog_event(self):
        """Test SOG event detection."""
        assert is_sog_event('Shot', 'Shot_OnNetSaved') == True
        assert is_sog_event('Shot', 'Shot_OnNet') == True
        assert is_sog_event('Shot', 'Shot_Goal') == True
        assert is_sog_event('Shot', 'Shot_Missed') == False
        assert is_sog_event('Goal', 'Goal_Scored') == False
    
    def test_is_corsi_event(self):
        """Test Corsi event detection."""
        # SOG is Corsi
        assert is_corsi_event('Shot', 'Shot_OnNet') == True
        # Blocked shot is Corsi
        assert is_corsi_event('Shot', 'Shot_Blocked') == True
        # Missed shot is Corsi
        assert is_corsi_event('Shot', 'Shot_Missed') == True
        # Pass is not Corsi
        assert is_corsi_event('Pass', 'Pass_Completed') == False
    
    def test_is_fenwick_event(self):
        """Test Fenwick event detection."""
        # SOG is Fenwick
        assert is_fenwick_event('Shot', 'Shot_OnNet') == True
        # Missed shot is Fenwick
        assert is_fenwick_event('Shot', 'Shot_Missed') == True
        # Blocked shot is NOT Fenwick
        assert is_fenwick_event('Shot', 'Shot_Blocked') == False
    
    def test_calculate_cf_pct(self):
        """Test CF% calculation."""
        # 50% CF
        assert calculate_cf_pct(10, 10) == 50.0
        # 100% CF
        assert calculate_cf_pct(10, 0) == 100.0
        # 0% CF
        assert calculate_cf_pct(0, 10) == 0.0
        # None when both are 0
        assert calculate_cf_pct(0, 0) is None
    
    def test_calculate_ff_pct(self):
        """Test FF% calculation."""
        # 50% FF
        assert calculate_ff_pct(10, 10) == 50.0
        # 100% FF
        assert calculate_ff_pct(10, 0) == 100.0
        # None when both are 0
        assert calculate_ff_pct(0, 0) is None


# =============================================================================
# RATING CALCULATIONS TESTS
# =============================================================================

class TestRatingCalculations:
    """Tests for rating calculations."""
    
    def test_calculate_team_ratings(self):
        """Test team rating calculation."""
        player_rating_map = {
            'P1': 5.0,
            'P2': 4.0,
            'P3': 3.0,
        }
        
        avg, min_r, max_r = calculate_team_ratings(['P1', 'P2', 'P3'], player_rating_map)
        assert avg == 4.0
        assert min_r == 3.0
        assert max_r == 5.0
    
    def test_calculate_team_ratings_missing_players(self):
        """Test team rating with missing players."""
        player_rating_map = {'P1': 5.0}
        
        avg, min_r, max_r = calculate_team_ratings(['P1', 'P999'], player_rating_map)
        assert avg == 5.0
        assert min_r == 5.0
        assert max_r == 5.0
    
    def test_calculate_team_ratings_no_valid_ratings(self):
        """Test team rating with no valid ratings."""
        player_rating_map = {}
        
        avg, min_r, max_r = calculate_team_ratings(['P999'], player_rating_map)
        assert avg is None
        assert min_r is None
        assert max_r is None
    
    def test_calculate_rating_differential(self):
        """Test rating differential calculation."""
        diff = calculate_rating_differential(5.0, 4.0)
        assert diff == 1.0
        
        diff = calculate_rating_differential(4.0, 5.0)
        assert diff == -1.0
    
    def test_calculate_rating_differential_missing(self):
        """Test rating differential with missing values."""
        assert calculate_rating_differential(None, 4.0) is None
        assert calculate_rating_differential(5.0, None) is None
    
    def test_get_competition_tier(self):
        """Test competition tier assignment."""
        assert get_competition_tier(5.5) == 'TI01'  # Elite
        assert get_competition_tier(4.5) == 'TI02'  # Above Average
        assert get_competition_tier(3.5) == 'TI03'  # Average
        assert get_competition_tier(2.5) == 'TI04'  # Below Average
        assert get_competition_tier(None) is None
    
    def test_calculate_expected_cf_pct(self):
        """Test expected CF% calculation."""
        # Rating advantage of 1.0 should give +5% CF
        expected = calculate_expected_cf_pct(1.0)
        assert expected == 55.0
        
        # Rating disadvantage of -1.0 should give -5% CF
        expected = calculate_expected_cf_pct(-1.0)
        assert expected == 45.0
    
    def test_calculate_expected_cf_pct_clipping(self):
        """Test expected CF% clipping to bounds."""
        # Very large advantage should clip to 70%
        expected = calculate_expected_cf_pct(10.0)
        assert expected == 70.0
        
        # Very large disadvantage should clip to 30%
        expected = calculate_expected_cf_pct(-10.0)
        assert expected == 30.0
    
    def test_calculate_cf_pct_vs_expected(self):
        """Test CF% vs expected calculation."""
        # Performed 5% better than expected
        diff = calculate_cf_pct_vs_expected(55.0, 50.0)
        assert diff == 5.0
        
        # Performed 5% worse than expected
        diff = calculate_cf_pct_vs_expected(45.0, 50.0)
        assert diff == -5.0


# =============================================================================
# TIME CALCULATIONS TESTS
# =============================================================================

class TestTimeCalculations:
    """Tests for time-based calculations."""
    
    def test_calculate_toi_minutes(self):
        """Test TOI conversion from seconds to minutes."""
        assert calculate_toi_minutes(120) == 2.0
        assert calculate_toi_minutes(90) == 1.5
        assert calculate_toi_minutes(0) == 0.0
    
    def test_calculate_toi_minutes_rounding(self):
        """Test TOI minutes rounding."""
        # 125 seconds = 2.083... minutes, should round to 2.08
        result = calculate_toi_minutes(125)
        assert result == 2.08
    
    def test_calculate_shift_duration(self):
        """Test shift duration calculation."""
        # Clock counts down: start=120, end=90, duration=30
        assert calculate_shift_duration(120, 90) == 30.0
        
        # Negative duration should clip to 0
        assert calculate_shift_duration(90, 120) == 0.0
    
    def test_calculate_per_60_rate(self):
        """Test per-60 rate calculation."""
        # 2 goals in 1 minute = 120 per 60
        rate = calculate_per_60_rate(2, 1.0)
        assert rate == 120.0
        
        # 1 goal in 2 minutes = 30 per 60
        rate = calculate_per_60_rate(1, 2.0)
        assert rate == 30.0
    
    def test_calculate_per_60_rate_zero_toi(self):
        """Test per-60 rate with zero TOI."""
        rate = calculate_per_60_rate(5, 0.0)
        assert rate is None
        
        rate = calculate_per_60_rate(5, 0.0, default=0.0)
        assert rate == 0.0
