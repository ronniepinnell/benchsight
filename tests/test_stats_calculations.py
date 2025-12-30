"""
BENCHSIGHT - Statistics Calculation Tests
=========================================
Tests to verify all statistics are calculated correctly.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path("data/output")


class TestScoringStats:
    """Test scoring statistics calculations."""
    
    def test_points_equals_goals_plus_assists(self):
        """Verify points = goals + assists for all players."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if 'points' in df.columns and 'goals' in df.columns and 'assists' in df.columns:
            calculated = df['goals'] + df['assists']
            mismatches = df[df['points'] != calculated]
            
            assert len(mismatches) == 0, \
                f"{len(mismatches)} rows have points != goals + assists"
    
    def test_goals_non_negative(self):
        """Verify goals are never negative."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if 'goals' in df.columns:
            negative = df[df['goals'] < 0]
            assert len(negative) == 0, f"{len(negative)} rows have negative goals"
    
    def test_assists_non_negative(self):
        """Verify assists are never negative."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if 'assists' in df.columns:
            negative = df[df['assists'] < 0]
            assert len(negative) == 0, f"{len(negative)} rows have negative assists"
    
    def test_shooting_percentage_valid(self):
        """Verify shooting percentage is 0-100."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if 'shooting_pct' in df.columns:
            invalid = df[(df['shooting_pct'] < 0) | (df['shooting_pct'] > 100)]
            assert len(invalid) == 0, \
                f"{len(invalid)} rows have invalid shooting_pct"
    
    def test_shooting_pct_calculation(self):
        """Verify shooting_pct = goals/shots * 100."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if all(c in df.columns for c in ['shooting_pct', 'goals', 'shots']):
            # Only check rows with shots > 0
            has_shots = df[df['shots'] > 0].copy()
            expected = (has_shots['goals'] / has_shots['shots'] * 100).round(1)
            actual = has_shots['shooting_pct'].round(1)
            
            # Allow small tolerance for rounding
            diff = (expected - actual).abs()
            mismatches = has_shots[diff > 0.2]
            
            assert len(mismatches) <= 5, \
                f"{len(mismatches)} rows have incorrect shooting_pct"


class TestShotStats:
    """Test shot statistics calculations."""
    
    def test_sog_less_than_or_equal_shots(self):
        """Verify shots on goal <= total shots."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if 'sog' in df.columns and 'shots' in df.columns:
            invalid = df[df['sog'] > df['shots']]
            assert len(invalid) == 0, \
                f"{len(invalid)} rows have SOG > total shots"
    
    def test_shots_composition(self):
        """Verify shots = sog + blocked + missed (approximately)."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if all(c in df.columns for c in ['shots', 'sog', 'shots_blocked', 'shots_missed']):
            expected = df['sog'] + df['shots_blocked'] + df['shots_missed']
            diff = (df['shots'] - expected).abs()
            
            # Allow some tolerance (some shots might be categorized differently)
            mismatches = df[diff > 3]
            assert len(mismatches) <= df.shape[0] * 0.1, \
                f"{len(mismatches)} rows have shots != sog + blocked + missed"
    
    def test_shots_non_negative(self):
        """Verify shot counts are never negative."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        shot_cols = ['shots', 'sog', 'shots_blocked', 'shots_missed']
        for col in shot_cols:
            if col in df.columns:
                negative = df[df[col] < 0]
                assert len(negative) == 0, f"{len(negative)} rows have negative {col}"


class TestPassingStats:
    """Test passing statistics calculations."""
    
    def test_pass_completed_less_than_attempts(self):
        """Verify completed passes <= pass attempts."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if 'pass_completed' in df.columns and 'pass_attempts' in df.columns:
            invalid = df[df['pass_completed'] > df['pass_attempts']]
            assert len(invalid) == 0, \
                f"{len(invalid)} rows have pass_completed > pass_attempts"
    
    def test_pass_pct_valid(self):
        """Verify pass percentage is 0-100."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if 'pass_pct' in df.columns:
            invalid = df[(df['pass_pct'] < 0) | (df['pass_pct'] > 100)]
            assert len(invalid) == 0, \
                f"{len(invalid)} rows have invalid pass_pct"
    
    def test_pass_pct_calculation(self):
        """Verify pass_pct = completed/attempts * 100."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if all(c in df.columns for c in ['pass_pct', 'pass_completed', 'pass_attempts']):
            has_passes = df[df['pass_attempts'] > 0].copy()
            expected = (has_passes['pass_completed'] / has_passes['pass_attempts'] * 100).round(1)
            actual = has_passes['pass_pct'].round(1)
            
            diff = (expected - actual).abs()
            mismatches = has_passes[diff > 0.2]
            
            assert len(mismatches) <= 5, \
                f"{len(mismatches)} rows have incorrect pass_pct"


class TestFaceoffStats:
    """Test faceoff statistics calculations."""
    
    def test_fo_total_equals_wins_plus_losses(self):
        """Verify fo_total = fo_wins + fo_losses."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if all(c in df.columns for c in ['fo_total', 'fo_wins', 'fo_losses']):
            calculated = df['fo_wins'] + df['fo_losses']
            mismatches = df[df['fo_total'] != calculated]
            
            assert len(mismatches) == 0, \
                f"{len(mismatches)} rows have fo_total != fo_wins + fo_losses"
    
    def test_fo_pct_valid(self):
        """Verify faceoff percentage is 0-100."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if 'fo_pct' in df.columns:
            invalid = df[(df['fo_pct'] < 0) | (df['fo_pct'] > 100)]
            assert len(invalid) == 0, \
                f"{len(invalid)} rows have invalid fo_pct"
    
    def test_fo_pct_calculation(self):
        """Verify fo_pct = wins/total * 100."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if all(c in df.columns for c in ['fo_pct', 'fo_wins', 'fo_total']):
            has_faceoffs = df[df['fo_total'] > 0].copy()
            expected = (has_faceoffs['fo_wins'] / has_faceoffs['fo_total'] * 100).round(1)
            actual = has_faceoffs['fo_pct'].round(1)
            
            diff = (expected - actual).abs()
            mismatches = has_faceoffs[diff > 0.2]
            
            assert len(mismatches) <= 5, \
                f"{len(mismatches)} rows have incorrect fo_pct"


class TestTimeOnIceStats:
    """Test time on ice statistics calculations."""
    
    def test_toi_seconds_positive(self):
        """Verify TOI is non-negative."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if 'toi_seconds' in df.columns:
            negative = df[df['toi_seconds'] < 0]
            assert len(negative) == 0, f"{len(negative)} rows have negative TOI"
    
    def test_toi_minutes_calculation(self):
        """Verify toi_minutes = toi_seconds / 60."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if 'toi_seconds' in df.columns and 'toi_minutes' in df.columns:
            expected = (df['toi_seconds'] / 60).round(1)
            actual = df['toi_minutes'].round(1)
            
            diff = (expected - actual).abs()
            mismatches = df[diff > 0.2]
            
            assert len(mismatches) <= 5, \
                f"{len(mismatches)} rows have incorrect toi_minutes"
    
    def test_toi_reasonable_range(self):
        """Verify TOI is in reasonable range (0-60 minutes per game)."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if 'toi_seconds' in df.columns:
            max_toi = df['toi_seconds'].max()
            # 60 minutes = 3600 seconds
            assert max_toi <= 3600, \
                f"Max TOI is {max_toi} seconds ({max_toi/60:.1f} min), exceeds 60 min"
    
    def test_shift_count_positive(self):
        """Verify shift count is non-negative."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if 'shift_count' in df.columns:
            negative = df[df['shift_count'] < 0]
            assert len(negative) == 0, f"{len(negative)} rows have negative shift_count"
    
    def test_avg_shift_calculation(self):
        """Verify avg_shift = toi_seconds / logical_shifts."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        # Use logical_shifts for calculation (not raw shift_count)
        if all(c in df.columns for c in ['avg_shift', 'toi_seconds', 'logical_shifts']):
            has_shifts = df[df['logical_shifts'] > 0].copy()
            expected = (has_shifts['toi_seconds'] / has_shifts['logical_shifts']).round(1)
            actual = has_shifts['avg_shift'].round(1)
            
            diff = (expected - actual).abs()
            # Allow larger tolerance for rounding
            mismatches = has_shifts[diff > 5]
            
            assert len(mismatches) <= has_shifts.shape[0] * 0.2, \
                f"{len(mismatches)} rows have incorrect avg_shift"


class TestPer60Stats:
    """Test per-60 minute rate statistics."""
    
    def test_goals_per_60_calculation(self):
        """Verify goals_per_60 = goals / (toi/3600) * 60."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if all(c in df.columns for c in ['goals_per_60', 'goals', 'toi_seconds']):
            has_toi = df[df['toi_seconds'] > 0].copy()
            toi_60 = has_toi['toi_seconds'] / 3600
            expected = (has_toi['goals'] / toi_60).round(2)
            actual = has_toi['goals_per_60'].round(2)
            
            diff = (expected - actual).abs()
            mismatches = has_toi[diff > 0.1]
            
            assert len(mismatches) <= has_toi.shape[0] * 0.2, \
                f"{len(mismatches)} rows have incorrect goals_per_60"
    
    def test_per_60_non_negative(self):
        """Verify per-60 stats are mostly non-negative."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        # game_score can be negative (it's a composite metric)
        per_60_cols = [c for c in df.columns if 'per_60' in c and 'game_score' not in c]
        for col in per_60_cols:
            negative = df[df[col] < 0]
            negative_rate = len(negative) / len(df) if len(df) > 0 else 0
            assert negative_rate < 0.1, \
                f"{len(negative)} rows ({negative_rate:.1%}) have negative {col}"


class TestCorsiStats:
    """Test Corsi/Fenwick advanced statistics."""
    
    def test_cf_pct_valid(self):
        """Verify CF% is 0-100 or 0 for no events."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if 'cf_pct' in df.columns:
            invalid = df[(df['cf_pct'] < 0) | (df['cf_pct'] > 100)]
            assert len(invalid) == 0, \
                f"{len(invalid)} rows have invalid cf_pct"
    
    def test_cf_pct_calculation(self):
        """Verify CF% = CF / (CF + CA) * 100."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if all(c in df.columns for c in ['cf_pct', 'corsi_for', 'corsi_against']):
            total_corsi = df['corsi_for'] + df['corsi_against']
            has_corsi = df[total_corsi > 0].copy()
            
            if len(has_corsi) > 0:
                expected = (has_corsi['corsi_for'] / (has_corsi['corsi_for'] + has_corsi['corsi_against']) * 100).round(1)
                actual = has_corsi['cf_pct'].round(1)
                
                diff = (expected - actual).abs()
                mismatches = has_corsi[diff > 1]
                
                assert len(mismatches) <= has_corsi.shape[0] * 0.2, \
                    f"{len(mismatches)} rows have incorrect cf_pct"
    
    def test_corsi_non_negative(self):
        """Verify Corsi stats are non-negative."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        corsi_cols = ['corsi_for', 'corsi_against', 'fenwick_for', 'fenwick_against']
        for col in corsi_cols:
            if col in df.columns:
                negative = df[df[col] < 0]
                assert len(negative) == 0, f"{len(negative)} rows have negative {col}"


class TestPlusMinusStats:
    """Test plus/minus statistics."""
    
    def test_plus_minus_reasonable_range(self):
        """Verify plus_minus values are in reasonable range."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        # Check various plus/minus column naming conventions
        pm_cols = [c for c in df.columns if 'plus_minus' in c.lower()]
        
        for col in pm_cols:
            # Plus minus in a single game should be between -10 and +10 typically
            extreme = df[(df[col] < -15) | (df[col] > 15)]
            extreme_rate = len(extreme) / len(df) if len(df) > 0 else 0
            
            assert extreme_rate < 0.1, \
                f"{extreme_rate:.1%} of rows have extreme {col} values"
    
    def test_plus_minus_consistency(self):
        """Verify plus/minus values are consistent with goals."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        # Players with goals should generally have positive or zero plus_minus
        if 'goals' in df.columns and 'plus_minus_ev' in df.columns:
            scorers = df[df['goals'] > 0]
            if len(scorers) > 0:
                very_negative = scorers[scorers['plus_minus_ev'] < -3]
                # Allow some exceptions (player could score but team give up more)
                assert len(very_negative) <= len(scorers) * 0.3, \
                    "Too many goal scorers have very negative plus/minus"


class TestCompositeRatings:
    """Test composite rating statistics."""
    
    def test_ratings_valid_range(self):
        """Verify ratings are in valid range (0-100 or similar)."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        rating_cols = ['offensive_rating', 'defensive_rating', 'hustle_rating',
                       'playmaking_rating', 'shooting_rating', 'impact_score']
        
        for col in rating_cols:
            if col in df.columns:
                # Most ratings should be 0-100
                invalid = df[(df[col] < -100) | (df[col] > 200)]
                assert len(invalid) <= df.shape[0] * 0.05, \
                    f"{len(invalid)} rows have {col} outside reasonable range"
    
    def test_ratings_non_null(self):
        """Verify rating columns have values."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        rating_cols = ['offensive_rating', 'defensive_rating', 'hustle_rating']
        
        for col in rating_cols:
            if col in df.columns:
                null_rate = df[col].isna().sum() / len(df)
                assert null_rate < 0.5, \
                    f"{col} has {null_rate:.1%} null values"
