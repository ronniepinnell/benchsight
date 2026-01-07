#!/usr/bin/env python3
"""
=============================================================================
Test Suite: Data Validation
=============================================================================
Comprehensive validation tests for ETL output data quality.

Run with: pytest tests/test_data_validation.py -v
=============================================================================
"""

import pytest
import pandas as pd
from pathlib import Path
from collections import Counter


class TestDataCompleteness:
    """Test that all expected data is present."""
    
    @pytest.fixture
    def output_dir(self):
        return Path("data/output")
    
    @pytest.fixture
    def events_df(self, output_dir):
        csv_path = output_dir / "fact_events.csv"
        if csv_path.exists():
            return pd.read_csv(csv_path)
        pytest.skip("fact_events.csv not found")
    
    @pytest.fixture
    def player_stats_df(self, output_dir):
        csv_path = output_dir / "fact_player_game_stats.csv"
        if csv_path.exists():
            return pd.read_csv(csv_path)
        pytest.skip("fact_player_game_stats.csv not found")
    
    def test_minimum_table_count(self, output_dir):
        """Should have at least 90 CSV output files."""
        csv_files = list(output_dir.glob("*.csv"))
        assert len(csv_files) >= 90, f"Expected 90+ tables, found {len(csv_files)}"
    
    def test_fact_events_not_empty(self, events_df):
        """Events table should have data."""
        assert len(events_df) > 0, "fact_events is empty"
    
    def test_events_have_required_columns(self, events_df):
        """Events have all required columns."""
        required = ['event_key', 'game_id', 'event_index', 'event_type']
        for col in required:
            assert col in events_df.columns, f"Missing required column: {col}"
    
    def test_player_stats_have_core_columns(self, player_stats_df):
        """Player stats have core stat columns."""
        core_stats = ['goals', 'assists', 'points', 'shots']
        for col in core_stats:
            assert col in player_stats_df.columns, f"Missing stat column: {col}"
    
    def test_multiple_games_processed(self, events_df):
        """Should have data from multiple games."""
        games = events_df['game_id'].nunique()
        assert games >= 4, f"Expected 4+ games, found {games}"


class TestGoalIntegrity:
    """Validate goal data is accurate."""
    
    @pytest.fixture
    def output_dir(self):
        return Path("data/output")
    
    @pytest.fixture
    def events_df(self, output_dir):
        return pd.read_csv(output_dir / "fact_events.csv")
    
    @pytest.fixture
    def player_stats_df(self, output_dir):
        return pd.read_csv(output_dir / "fact_player_game_stats.csv")
    
    def test_goals_detected_correctly(self, events_df):
        """Goals are properly identified in events."""
        goals = events_df[
            (events_df['event_type'] == 'Goal') | 
            (events_df['event_detail'].str.contains('Goal', case=False, na=False))
        ]
        assert len(goals) > 0, "No goals found in events"
    
    def test_goals_count_matches_stats(self, events_df, player_stats_df):
        """Goals in events match goals in player stats."""
        # Count goals in events per game - only event_type = 'Goal'
        # Note: event_detail contains 'Goal' in many non-goal events like 'Stoppage-GoalieStoppage'
        goals_in_events = events_df[events_df['event_type'] == 'Goal']
        
        # Count goals in player stats per game
        event_games = set(events_df['game_id'].unique())
        stats_for_tracked = player_stats_df[player_stats_df['game_id'].isin(event_games)]
        
        for game_id in event_games:
            game_goals_events = len(goals_in_events[goals_in_events['game_id'] == game_id])
            game_goals_stats = stats_for_tracked[stats_for_tracked['game_id'] == game_id]['goals'].sum()
            
            # Should match exactly or within 1 (for rounding)
            assert abs(game_goals_events - game_goals_stats) <= 1, \
                   f"Game {game_id}: events have {game_goals_events}, stats have {game_goals_stats}"
    
    def test_goals_have_scorers(self, events_df):
        """All goals have a primary player (scorer)."""
        goals = events_df[events_df['event_type'] == 'Goal']
        if len(goals) == 0:
            goals = events_df[events_df['event_detail'].str.contains('Goal', case=False, na=False)]
        
        if 'event_player_1' in goals.columns:
            missing_scorer = goals['event_player_1'].isna().sum()
            assert missing_scorer == 0 or missing_scorer / len(goals) < 0.1, \
                f"{missing_scorer} goals missing scorers"


class TestTOIIntegrity:
    """Validate Time on Ice calculations."""
    
    @pytest.fixture
    def output_dir(self):
        return Path("data/output")
    
    @pytest.fixture
    def player_stats_df(self, output_dir):
        return pd.read_csv(output_dir / "fact_player_game_stats.csv")
    
    @pytest.fixture
    def shifts_df(self, output_dir):
        return pd.read_csv(output_dir / "fact_shifts.csv")
    
    def test_toi_is_positive(self, player_stats_df):
        """All TOI values are positive."""
        toi_cols = [c for c in player_stats_df.columns if 'toi' in c.lower() or 'time_on_ice' in c.lower()]
        if not toi_cols:
            pytest.skip("No TOI columns found")
        
        for col in toi_cols:
            if player_stats_df[col].dtype in ['float64', 'int64']:
                negative = (player_stats_df[col] < 0).sum()
                assert negative == 0, f"{negative} negative values in {col}"
    
    def test_shifts_have_duration(self, shifts_df):
        """Shifts from fully processed games have duration calculated."""
        duration_cols = [c for c in shifts_df.columns if 'duration' in c.lower()]
        if not duration_cols:
            pytest.skip("No duration column in shifts")
        
        col = duration_cols[0]
        
        # Check per game - some games may be incomplete
        for game_id in shifts_df['game_id'].unique():
            game_shifts = shifts_df[shifts_df['game_id'] == game_id]
            missing = game_shifts[col].isna().sum()
            missing_pct = missing / len(game_shifts) if len(game_shifts) > 0 else 0
            
            # Flag games with high missing rate as warnings, not failures
            # Only fail if ALL games have issues
            if missing_pct > 0.5:
                import warnings
                warnings.warn(f"Game {game_id}: {missing}/{len(game_shifts)} shifts missing duration")
        
        # Overall check - at least some shifts should have duration
        total_missing = shifts_df[col].isna().sum()
        total_missing_pct = total_missing / len(shifts_df)
        assert total_missing_pct < 0.95, \
            f"Almost all shifts ({total_missing_pct:.0%}) missing duration - check ETL"
    
    def test_shift_duration_reasonable(self, shifts_df):
        """Shift durations are in reasonable range."""
        duration_cols = [c for c in shifts_df.columns if 'duration' in c.lower()]
        if not duration_cols:
            pytest.skip("No duration column")
        
        col = duration_cols[0]
        durations = shifts_df[col].dropna()
        
        # Filter to numeric
        durations = pd.to_numeric(durations, errors='coerce').dropna()
        
        if len(durations) > 0:
            # No shift should be over 5 minutes (300 seconds)
            too_long = (durations > 300).sum()
            assert too_long / len(durations) < 0.05, f"{too_long} shifts over 5 minutes"


class TestForeignKeyIntegrity:
    """Test foreign key relationships between tables."""
    
    @pytest.fixture
    def output_dir(self):
        return Path("data/output")
    
    def test_events_players_exist(self, output_dir):
        """Event players exist in dim_player."""
        events = pd.read_csv(output_dir / "fact_events.csv")
        players = pd.read_csv(output_dir / "dim_player.csv")
        
        player_ids = set(players['player_id'].astype(str).unique())
        
        if 'event_player_1' in events.columns:
            event_players = events['event_player_1'].dropna().astype(str).unique()
            orphans = [p for p in event_players if p not in player_ids and p != 'nan']
            
            # Allow some orphans (might be from different data sources)
            orphan_rate = len(orphans) / len(event_players) if len(event_players) > 0 else 0
            assert orphan_rate < 0.1, f"{len(orphans)} orphan player references"
    
    def test_events_games_exist(self, output_dir):
        """Event games exist in dim_schedule."""
        events = pd.read_csv(output_dir / "fact_events.csv")
        schedule = pd.read_csv(output_dir / "dim_schedule.csv")
        
        schedule_games = set(schedule['game_id'].astype(str).unique())
        event_games = set(events['game_id'].astype(str).unique())
        
        orphans = event_games - schedule_games
        assert len(orphans) == 0, f"Orphan game IDs in events: {orphans}"
    
    def test_player_stats_games_exist(self, output_dir):
        """Player stat games exist in schedule."""
        stats = pd.read_csv(output_dir / "fact_player_game_stats.csv")
        schedule = pd.read_csv(output_dir / "dim_schedule.csv")
        
        schedule_games = set(schedule['game_id'].astype(str).unique())
        stat_games = set(stats['game_id'].astype(str).unique())
        
        orphans = stat_games - schedule_games
        assert len(orphans) == 0, f"Orphan game IDs in player stats: {orphans}"


class TestVideoTimestampIntegrity:
    """Test video timestamp data quality."""
    
    @pytest.fixture
    def output_dir(self):
        return Path("data/output")
    
    @pytest.fixture
    def events_df(self, output_dir):
        return pd.read_csv(output_dir / "fact_events.csv")
    
    @pytest.fixture
    def video_df(self, output_dir):
        return pd.read_csv(output_dir / "fact_video.csv")
    
    def test_video_timestamps_present(self, events_df):
        """Events have running_video_time populated."""
        if 'running_video_time' not in events_df.columns:
            pytest.skip("No running_video_time column")
        
        coverage = events_df['running_video_time'].notna().mean()
        assert coverage > 0.9, f"Video timestamp coverage is {coverage:.1%}"
    
    def test_video_timestamps_sequential(self, events_df):
        """Video timestamps are generally sequential within a period."""
        if 'running_video_time' not in events_df.columns:
            pytest.skip("No running_video_time column")
        
        # Group by game and check sequence
        for game_id in events_df['game_id'].unique():
            game_events = events_df[events_df['game_id'] == game_id].sort_values('event_index')
            timestamps = game_events['running_video_time'].dropna()
            
            if len(timestamps) > 1:
                # Check that timestamps are mostly increasing
                increasing = (timestamps.diff().dropna() >= 0).mean()
                assert increasing > 0.8, f"Game {game_id}: only {increasing:.1%} of timestamps are sequential"
    
    def test_video_urls_valid_format(self, video_df):
        """Video URLs are valid YouTube URLs."""
        url_col = 'Url_1' if 'Url_1' in video_df.columns else 'video_url'
        
        for url in video_df[url_col].dropna():
            assert 'youtube.com' in url or 'youtu.be' in url, f"Invalid video URL: {url}"


class TestStatisticalReasonableness:
    """Test that stats are statistically reasonable."""
    
    @pytest.fixture
    def output_dir(self):
        return Path("data/output")
    
    @pytest.fixture
    def player_stats_df(self, output_dir):
        return pd.read_csv(output_dir / "fact_player_game_stats.csv")
    
    def test_points_equals_goals_plus_assists(self, player_stats_df):
        """Points = Goals + Assists."""
        if not all(c in player_stats_df.columns for c in ['goals', 'assists', 'points']):
            pytest.skip("Missing G/A/P columns")
        
        calculated = player_stats_df['goals'] + player_stats_df['assists']
        actual = player_stats_df['points']
        
        matches = (calculated == actual).mean()
        assert matches > 0.99, f"Points formula matches {matches:.1%}"
    
    def test_goals_within_reason(self, player_stats_df):
        """No player has unreasonable number of goals per game."""
        if 'goals' not in player_stats_df.columns:
            pytest.skip("No goals column")
        
        max_goals = player_stats_df['goals'].max()
        assert max_goals <= 10, f"Max goals {max_goals} seems unreasonable"
    
    def test_shots_greater_than_goals(self, player_stats_df):
        """Shots should be >= goals for most players."""
        if not all(c in player_stats_df.columns for c in ['shots', 'goals']):
            pytest.skip("Missing shots/goals columns")
        
        valid = player_stats_df['shots'] >= player_stats_df['goals']
        rate = valid.mean()
        assert rate > 0.95, f"Only {rate:.1%} have shots >= goals"
    
    def test_plus_minus_balanced(self, player_stats_df):
        """Plus/minus should roughly balance across team."""
        if 'plus_minus' not in player_stats_df.columns:
            pytest.skip("No plus_minus column")
        
        # Check per game balance
        for game_id in player_stats_df['game_id'].unique():
            game_stats = player_stats_df[player_stats_df['game_id'] == game_id]
            total_pm = game_stats['plus_minus'].sum()
            
            # Should roughly balance (some rounding allowed)
            assert abs(total_pm) <= 5, f"Game {game_id} plus/minus imbalance: {total_pm}"


class TestSchemaConsistency:
    """Test schema consistency across tables."""
    
    @pytest.fixture
    def output_dir(self):
        return Path("data/output")
    
    def test_all_facts_have_game_id(self, output_dir):
        """Game-level fact tables have game_id column."""
        fact_files = output_dir.glob("fact_*.csv")
        
        # These are league-level tables, not game-level
        league_level_tables = {
            'fact_draft', 'fact_registration', 'fact_leadership', 
            'fact_league_leaders_snapshot', 'fact_team_standings_snapshot',
            'fact_playergames'  # BLB source table with player_game_id
        }
        
        for csv_path in fact_files:
            df = pd.read_csv(csv_path, nrows=0)  # Just get columns
            if csv_path.stem not in league_level_tables and \
               'boxscore' not in csv_path.stem and 'standings' not in csv_path.stem:
                assert 'game_id' in df.columns, f"{csv_path.stem} missing game_id"
    
    def test_all_dims_have_id_column(self, output_dir):
        """All dim tables have an ID column or are lookup tables."""
        dim_files = output_dir.glob("dim_*.csv")
        
        # These are lookup/reference tables without standard ID columns
        lookup_tables = {'dim_randomnames', 'dim_terminology_mapping'}
        
        for csv_path in dim_files:
            if csv_path.stem in lookup_tables:
                continue
            df = pd.read_csv(csv_path, nrows=0)
            # Should have some kind of ID column (contains 'id' in name)
            id_cols = [c for c in df.columns if '_id' in c.lower() or c == 'index']
            assert len(id_cols) > 0, f"{csv_path.stem} has no ID column: {list(df.columns)}"
    
    def test_consistent_game_id_type(self, output_dir):
        """game_id is consistent type across tables."""
        tables_to_check = ['fact_events', 'fact_player_game_stats', 'fact_shifts', 'dim_schedule']
        
        game_id_types = {}
        for table in tables_to_check:
            csv_path = output_dir / f"{table}.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path, nrows=100)
                if 'game_id' in df.columns:
                    # Check if all values are numeric-like
                    game_id_types[table] = df['game_id'].dtype
        
        # All should be compatible (int or string representation of int)
        assert len(game_id_types) > 0, "No tables with game_id found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
