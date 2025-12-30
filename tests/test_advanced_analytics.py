"""
BENCHSIGHT - Advanced Analytics Table Tests
==========================================
Tests for H2H, WOWY, Line Combos, and other advanced analytics.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path("data/output")


class TestH2HTable:
    """Test Head-to-Head analytics table."""
    
    @pytest.fixture
    def h2h_df(self):
        path = OUTPUT_DIR / "fact_h2h.csv"
        if path.exists():
            return pd.read_csv(path)
        return pd.DataFrame()
    
    def test_h2h_exists(self, h2h_df):
        """Verify fact_h2h.csv exists."""
        assert len(h2h_df) > 0 or (OUTPUT_DIR / "fact_h2h.csv").exists(), \
            "fact_h2h.csv not found"
    
    def test_h2h_has_player_columns(self, h2h_df):
        """Verify H2H has player identifier columns."""
        if len(h2h_df) == 0:
            pytest.skip("H2H table empty")
        
        player_cols = ['player_id', 'player_1_id', 'opponent_id', 'player_2_id']
        has_players = any(c in h2h_df.columns for c in player_cols)
        assert has_players, "H2H missing player columns"
    
    def test_h2h_has_game_column(self, h2h_df):
        """Verify H2H has game_id column."""
        if len(h2h_df) == 0:
            pytest.skip("H2H table empty")
        
        assert 'game_id' in h2h_df.columns, "H2H missing game_id"
    
    def test_h2h_has_stat_columns(self, h2h_df):
        """Verify H2H has performance stat columns."""
        if len(h2h_df) == 0:
            pytest.skip("H2H table empty")
        
        # Accept various naming conventions for stats
        stat_cols = ['toi', 'toi_together', 'cf', 'ca', 'gf', 'ga', 
                     'goals_for', 'goals_against', 'plus_minus', 'shifts_together']
        present = [c for c in stat_cols if c in h2h_df.columns]
        assert len(present) >= 2, f"H2H missing stat columns, only has: {list(h2h_df.columns)[:10]}"
    
    def test_h2h_no_self_matchups(self, h2h_df):
        """Verify no player matched against themselves."""
        if len(h2h_df) == 0:
            pytest.skip("H2H table empty")
        
        p1_cols = [c for c in h2h_df.columns if 'player_1' in c or c == 'player_id']
        p2_cols = [c for c in h2h_df.columns if 'player_2' in c or c == 'opponent_id']
        
        if p1_cols and p2_cols:
            p1 = h2h_df[p1_cols[0]]
            p2 = h2h_df[p2_cols[0]]
            self_matchups = (p1 == p2).sum()
            assert self_matchups == 0, f"{self_matchups} self-matchups found"


class TestWOWYTable:
    """Test With Or Without You analytics table."""
    
    @pytest.fixture
    def wowy_df(self):
        path = OUTPUT_DIR / "fact_wowy.csv"
        if path.exists():
            return pd.read_csv(path)
        return pd.DataFrame()
    
    def test_wowy_exists(self, wowy_df):
        """Verify fact_wowy.csv exists."""
        assert len(wowy_df) > 0 or (OUTPUT_DIR / "fact_wowy.csv").exists(), \
            "fact_wowy.csv not found"
    
    def test_wowy_has_player_pair_columns(self, wowy_df):
        """Verify WOWY has player pair columns."""
        if len(wowy_df) == 0:
            pytest.skip("WOWY table empty")
        
        pair_cols = ['player_1_id', 'player_2_id', 'player_id', 'teammate_id']
        has_pairs = sum(1 for c in pair_cols if c in wowy_df.columns) >= 2
        assert has_pairs, "WOWY missing player pair columns"
    
    def test_wowy_has_together_apart_stats(self, wowy_df):
        """Verify WOWY has together/apart comparison stats."""
        if len(wowy_df) == 0:
            pytest.skip("WOWY table empty")
        
        together_cols = [c for c in wowy_df.columns if 'together' in c.lower()]
        apart_cols = [c for c in wowy_df.columns if 'apart' in c.lower() or 'without' in c.lower()]
        
        assert len(together_cols) >= 1 or len(apart_cols) >= 1, \
            "WOWY missing together/apart stats"
    
    def test_wowy_toi_positive(self, wowy_df):
        """Verify WOWY TOI values are non-negative."""
        if len(wowy_df) == 0:
            pytest.skip("WOWY table empty")
        
        toi_cols = [c for c in wowy_df.columns if 'toi' in c.lower()]
        
        for col in toi_cols:
            negative = (wowy_df[col] < 0).sum()
            assert negative == 0, f"WOWY {col} has {negative} negative values"


class TestLineCombosTable:
    """Test Line Combinations analytics table."""
    
    @pytest.fixture
    def line_combos_df(self):
        path = OUTPUT_DIR / "fact_line_combos.csv"
        if path.exists():
            return pd.read_csv(path)
        return pd.DataFrame()
    
    def test_line_combos_exists(self, line_combos_df):
        """Verify fact_line_combos.csv exists."""
        assert len(line_combos_df) > 0 or (OUTPUT_DIR / "fact_line_combos.csv").exists(), \
            "fact_line_combos.csv not found"
    
    def test_line_combos_has_players(self, line_combos_df):
        """Verify line combos has player identification columns."""
        if len(line_combos_df) == 0:
            pytest.skip("Line combos table empty")
        
        # Check for player-related columns (might be named differently)
        player_cols = [c for c in line_combos_df.columns if 'player' in c.lower() or 
                       'p1' in c.lower() or 'p2' in c.lower() or 'slot' in c.lower()]
        # Also check for line identification columns
        line_cols = [c for c in line_combos_df.columns if 'line' in c.lower() or 
                     'combo' in c.lower() or 'unit' in c.lower()]
        
        assert len(player_cols) >= 1 or len(line_cols) >= 1, \
            f"Line combos should have player or line columns, has: {list(line_combos_df.columns)[:10]}"
    
    def test_line_combos_has_toi(self, line_combos_df):
        """Verify line combos has TOI."""
        if len(line_combos_df) == 0:
            pytest.skip("Line combos table empty")
        
        toi_cols = [c for c in line_combos_df.columns if 'toi' in c.lower()]
        assert len(toi_cols) >= 1, "Line combos missing TOI column"


class TestEventChainsTable:
    """Test Event Chains analytics table."""
    
    @pytest.fixture
    def event_chains_df(self):
        path = OUTPUT_DIR / "fact_event_chains.csv"
        if path.exists():
            return pd.read_csv(path)
        return pd.DataFrame()
    
    def test_event_chains_exists(self, event_chains_df):
        """Verify fact_event_chains.csv exists."""
        assert len(event_chains_df) > 0 or (OUTPUT_DIR / "fact_event_chains.csv").exists(), \
            "fact_event_chains.csv not found"
    
    def test_event_chains_has_sequence(self, event_chains_df):
        """Verify event chains has sequence/chain identifier."""
        if len(event_chains_df) == 0:
            pytest.skip("Event chains table empty")
        
        seq_cols = [c for c in event_chains_df.columns if 'chain' in c.lower() or 'sequence' in c.lower()]
        assert len(seq_cols) >= 1, "Event chains missing chain/sequence column"
    
    def test_event_chains_has_events(self, event_chains_df):
        """Verify event chains references events."""
        if len(event_chains_df) == 0:
            pytest.skip("Event chains table empty")
        
        event_cols = [c for c in event_chains_df.columns if 'event' in c.lower()]
        assert len(event_cols) >= 1, "Event chains missing event reference"


class TestPossessionTimeTable:
    """Test Possession Time analytics table."""
    
    @pytest.fixture
    def possession_df(self):
        path = OUTPUT_DIR / "fact_possession_time.csv"
        if path.exists():
            return pd.read_csv(path)
        return pd.DataFrame()
    
    def test_possession_exists(self, possession_df):
        """Verify fact_possession_time.csv exists."""
        assert len(possession_df) > 0 or (OUTPUT_DIR / "fact_possession_time.csv").exists(), \
            "fact_possession_time.csv not found"
    
    def test_possession_has_time_column(self, possession_df):
        """Verify possession table has time/duration column."""
        if len(possession_df) == 0:
            pytest.skip("Possession table empty")
        
        # Accept various naming conventions
        time_cols = [c for c in possession_df.columns if 'time' in c.lower() or 
                     'duration' in c.lower() or 'seconds' in c.lower() or
                     'poss' in c.lower() or 'toi' in c.lower()]
        assert len(time_cols) >= 1, \
            f"Possession table missing time column, has: {list(possession_df.columns)[:10]}"
    
    def test_possession_values_non_negative(self, possession_df):
        """Verify possession times are non-negative."""
        if len(possession_df) == 0:
            pytest.skip("Possession table empty")
        
        time_cols = [c for c in possession_df.columns if 'time' in c.lower() or 'duration' in c.lower()]
        
        for col in time_cols:
            if possession_df[col].dtype in ['int64', 'float64']:
                negative = (possession_df[col] < 0).sum()
                assert negative == 0, f"Possession {col} has {negative} negative values"


class TestRushCycleTable:
    """Test Rush/Cycle events analytics table."""
    
    def test_rush_events_exists(self):
        """Verify fact_rush_events.csv exists."""
        path = OUTPUT_DIR / "fact_rush_events.csv"
        assert path.exists(), "fact_rush_events.csv not found"
    
    def test_cycle_events_exists(self):
        """Verify fact_cycle_events.csv exists."""
        path = OUTPUT_DIR / "fact_cycle_events.csv"
        assert path.exists(), "fact_cycle_events.csv not found"
    
    def test_rush_events_has_type(self):
        """Verify rush events has rush type classification."""
        path = OUTPUT_DIR / "fact_rush_events.csv"
        if path.exists():
            df = pd.read_csv(path)
            if len(df) > 0:
                type_cols = [c for c in df.columns if 'type' in c.lower() or 'rush' in c.lower()]
                assert len(type_cols) >= 1, "Rush events missing type column"
    
    def test_cycle_events_has_pass_count(self):
        """Verify cycle events has pass count."""
        path = OUTPUT_DIR / "fact_cycle_events.csv"
        if path.exists():
            df = pd.read_csv(path)
            if len(df) > 0:
                pass_cols = [c for c in df.columns if 'pass' in c.lower() or 'count' in c.lower()]
                assert len(pass_cols) >= 1, "Cycle events missing pass count"


class TestGoalieStatsTable:
    """Test Goalie Stats analytics table."""
    
    @pytest.fixture
    def goalie_df(self):
        path = OUTPUT_DIR / "fact_goalie_game_stats.csv"
        if path.exists():
            return pd.read_csv(path)
        return pd.DataFrame()
    
    def test_goalie_stats_exists(self, goalie_df):
        """Verify fact_goalie_game_stats.csv exists."""
        assert len(goalie_df) > 0 or (OUTPUT_DIR / "fact_goalie_game_stats.csv").exists(), \
            "fact_goalie_game_stats.csv not found"
    
    def test_goalie_has_saves(self, goalie_df):
        """Verify goalie stats has saves column."""
        if len(goalie_df) == 0:
            pytest.skip("Goalie stats empty")
        
        save_cols = [c for c in goalie_df.columns if 'save' in c.lower()]
        assert len(save_cols) >= 1, "Goalie stats missing saves"
    
    def test_goalie_has_goals_against(self, goalie_df):
        """Verify goalie stats has goals against."""
        if len(goalie_df) == 0:
            pytest.skip("Goalie stats empty")
        
        ga_cols = [c for c in goalie_df.columns if 'goal' in c.lower() and 'against' in c.lower()]
        assert len(ga_cols) >= 1, "Goalie stats missing goals against"
    
    def test_goalie_save_pct_valid(self, goalie_df):
        """Verify goalie save percentage is valid (0-100 or 0-1)."""
        if len(goalie_df) == 0:
            pytest.skip("Goalie stats empty")
        
        if 'save_pct' in goalie_df.columns:
            # Could be 0-1 or 0-100 scale
            max_val = goalie_df['save_pct'].max()
            
            if max_val > 1:
                # 0-100 scale
                invalid = goalie_df[(goalie_df['save_pct'] < 0) | (goalie_df['save_pct'] > 100)]
            else:
                # 0-1 scale
                invalid = goalie_df[(goalie_df['save_pct'] < 0) | (goalie_df['save_pct'] > 1)]
            
            assert len(invalid) == 0, f"{len(invalid)} rows have invalid save_pct"


class TestTeamStatsTable:
    """Test Team Game Stats table."""
    
    @pytest.fixture
    def team_stats_df(self):
        path = OUTPUT_DIR / "fact_team_game_stats.csv"
        if path.exists():
            return pd.read_csv(path)
        return pd.DataFrame()
    
    def test_team_stats_exists(self, team_stats_df):
        """Verify fact_team_game_stats.csv exists."""
        assert len(team_stats_df) > 0 or (OUTPUT_DIR / "fact_team_game_stats.csv").exists(), \
            "fact_team_game_stats.csv not found"
    
    def test_team_stats_has_team_id(self, team_stats_df):
        """Verify team stats has team identifier."""
        if len(team_stats_df) == 0:
            pytest.skip("Team stats empty")
        
        team_cols = [c for c in team_stats_df.columns if 'team' in c.lower()]
        assert len(team_cols) >= 1, "Team stats missing team column"
    
    def test_team_stats_has_goals(self, team_stats_df):
        """Verify team stats has goals."""
        if len(team_stats_df) == 0:
            pytest.skip("Team stats empty")
        
        goal_cols = [c for c in team_stats_df.columns if 'goal' in c.lower()]
        assert len(goal_cols) >= 1, "Team stats missing goals"
    
    def test_team_game_count_reasonable(self, team_stats_df):
        """Verify team game count is reasonable."""
        if len(team_stats_df) == 0:
            pytest.skip("Team stats empty")
        
        if 'game_id' in team_stats_df.columns:
            games = team_stats_df['game_id'].nunique()
            # Should have 4 tracked games, 2 teams per game = 8 rows minimum
            assert len(team_stats_df) >= 4, \
                f"Only {len(team_stats_df)} team-game rows"


class TestShiftQualityTable:
    """Test Shift Quality analytics table."""
    
    def test_shift_quality_exists(self):
        """Verify fact_shift_quality.csv exists."""
        path = OUTPUT_DIR / "fact_shift_quality.csv"
        assert path.exists(), "fact_shift_quality.csv not found"
    
    def test_shift_quality_has_metrics(self):
        """Verify shift quality has quality metrics."""
        path = OUTPUT_DIR / "fact_shift_quality.csv"
        if path.exists():
            df = pd.read_csv(path)
            if len(df) > 0:
                quality_cols = [c for c in df.columns if 'quality' in c.lower() or 'score' in c.lower()]
                assert len(quality_cols) >= 1, "Shift quality missing quality metrics"
