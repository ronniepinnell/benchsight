#!/usr/bin/env python3
"""
=============================================================================
BENCHSIGHT ETL UNIT TESTS
=============================================================================
Run with: python -m pytest tests/test_etl.py -v
=============================================================================
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

OUTPUT_DIR = Path("data/output")
RAW_DIR = Path("data/raw/games")

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def player_stats():
    """Load fact_player_game_stats."""
    return pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")

@pytest.fixture
def events():
    """Load fact_events."""
    return pd.read_csv(OUTPUT_DIR / "fact_events.csv")

@pytest.fixture
def shifts():
    """Load fact_shifts."""
    return pd.read_csv(OUTPUT_DIR / "fact_shifts.csv")

@pytest.fixture
def roster():
    """Load fact_game_roster."""
    return pd.read_csv(OUTPUT_DIR / "fact_game_roster.csv")

@pytest.fixture
def dim_player():
    """Load dim_player."""
    return pd.read_csv(OUTPUT_DIR / "dim_player.csv")


# =============================================================================
# GOAL ACCURACY TESTS (CRITICAL)
# =============================================================================

class TestGoalAccuracy:
    """Critical tests for goal counts matching official data."""
    
    OFFICIAL_GOALS = {
        '18969': {'total': 7},   # Platinum 4, Velodrome 3
        '18977': {'total': 6},   # Velodrome 4, HollowBrook 2
        '18981': {'total': 3},   # Nelson 2, Velodrome 1
        '18987': {'total': 1},   # Outlaws 0, Velodrome 1
    }
    
    def test_game_18969_goals(self, player_stats):
        """Game 18969: Platinum 4, Velodrome 3 = 7 total."""
        game = player_stats[player_stats['game_id'].astype(str) == '18969']
        total = game['goals'].sum()
        assert total == 7, f"Expected 7 goals, got {total}"
    
    def test_game_18977_goals(self, player_stats):
        """Game 18977: Velodrome 4, HollowBrook 2 = 6 total."""
        game = player_stats[player_stats['game_id'].astype(str) == '18977']
        total = game['goals'].sum()
        assert total == 6, f"Expected 6 goals, got {total}"
    
    def test_game_18981_goals(self, player_stats):
        """Game 18981: Nelson 2, Velodrome 1 = 3 total."""
        game = player_stats[player_stats['game_id'].astype(str) == '18981']
        total = game['goals'].sum()
        assert total == 3, f"Expected 3 goals, got {total}"
    
    def test_game_18987_goals(self, player_stats):
        """Game 18987: Outlaws 0, Velodrome 1 = 1 total."""
        game = player_stats[player_stats['game_id'].astype(str) == '18987']
        total = game['goals'].sum()
        assert total == 1, f"Expected 1 goal, got {total}"
    
    def test_total_goals_all_games(self, player_stats):
        """Total goals across all 4 tracked games should be 17."""
        tracked = ['18969', '18977', '18981', '18987']
        total = player_stats[player_stats['game_id'].astype(str).isin(tracked)]['goals'].sum()
        assert total == 17, f"Expected 17 total goals, got {total}"


# =============================================================================
# DATA INTEGRITY TESTS
# =============================================================================

class TestDataIntegrity:
    """Tests for data integrity and consistency."""
    
    def test_no_null_player_ids(self, player_stats):
        """player_id should never be NULL."""
        null_count = player_stats['player_id'].isna().sum()
        assert null_count == 0, f"Found {null_count} NULL player_ids"
    
    def test_no_null_game_ids(self, player_stats):
        """game_id should never be NULL."""
        null_count = player_stats['game_id'].isna().sum()
        assert null_count == 0, f"Found {null_count} NULL game_ids"
    
    def test_no_duplicate_player_games(self, player_stats):
        """Each player should appear once per game."""
        dupes = player_stats.duplicated(subset=['game_id', 'player_id']).sum()
        assert dupes == 0, f"Found {dupes} duplicate player-game rows"
    
    def test_no_negative_goals(self, player_stats):
        """Goals should never be negative."""
        neg = (player_stats['goals'] < 0).sum()
        assert neg == 0, f"Found {neg} rows with negative goals"
    
    def test_no_negative_assists(self, player_stats):
        """Assists should never be negative."""
        neg = (player_stats['assists'] < 0).sum()
        assert neg == 0, f"Found {neg} rows with negative assists"
    
    def test_points_equals_goals_plus_assists(self, player_stats):
        """Points should equal goals + assists."""
        if 'points' in player_stats.columns:
            calculated = player_stats['goals'] + player_stats['assists']
            mismatch = (player_stats['points'] != calculated).sum()
            assert mismatch == 0, f"Found {mismatch} rows where points != goals + assists"


# =============================================================================
# SCHEMA TESTS
# =============================================================================

class TestSchemas:
    """Tests for required columns and data types."""
    
    def test_player_stats_columns(self, player_stats):
        """fact_player_game_stats should have required columns."""
        required = ['player_game_key', 'game_id', 'player_id', 'player_name', 'goals', 'assists']
        missing = [c for c in required if c not in player_stats.columns]
        assert len(missing) == 0, f"Missing columns: {missing}"
    
    def test_player_stats_enhanced_columns(self, player_stats):
        """fact_player_game_stats should have 300+ columns (enhanced stats)."""
        col_count = len(player_stats.columns)
        assert col_count >= 300, f"Only {col_count} columns, expected 300+ (enhanced stats lost?)"
    
    def test_events_columns(self, events):
        """fact_events should have required columns."""
        required = ['event_key', 'game_id', 'event_index', 'event_type', 'period']
        missing = [c for c in required if c not in events.columns]
        assert len(missing) == 0, f"Missing columns: {missing}"
    
    def test_roster_columns(self, roster):
        """fact_game_roster should have required columns."""
        required = ['roster_key', 'game_id', 'player_id', 'team_id']
        missing = [c for c in required if c not in roster.columns]
        assert len(missing) == 0, f"Missing columns: {missing}"


# =============================================================================
# ROW COUNT TESTS
# =============================================================================

class TestRowCounts:
    """Tests for expected row counts."""
    
    def test_player_stats_row_count(self, player_stats):
        """Should have ~107 player-game rows (4 games × ~27 players)."""
        count = len(player_stats)
        assert 100 <= count <= 150, f"Unexpected row count: {count}"
    
    def test_events_row_count(self, events):
        """Should have ~5800 events (4 games × ~1450 events)."""
        count = len(events)
        assert 5000 <= count <= 7000, f"Unexpected event count: {count}"
    
    def test_four_tracked_games(self, player_stats):
        """Should have exactly 4 tracked games."""
        games = player_stats['game_id'].astype(str).unique()
        tracked = ['18969', '18977', '18981', '18987']
        for g in tracked:
            assert g in games, f"Missing game {g}"


# =============================================================================
# EVENT VALIDATION TESTS
# =============================================================================

class TestEvents:
    """Tests for event data."""
    
    def test_goals_have_event_type(self, events):
        """Goal events should be properly typed."""
        goal_types = ['Goal', 'Shot Goal', 'Goal Scored']
        # At least some goals should exist
        goal_events = events[events['event_type'].isin(goal_types)]
        assert len(goal_events) > 0, "No goal events found"
    
    def test_event_periods_valid(self, events):
        """Period should be 1, 2, 3, or OT."""
        if 'period' in events.columns:
            # Handle both numeric and string periods
            valid_periods = ['1', '2', '3', 'OT', 'OT1', 'OT2', '1.0', '2.0', '3.0', 'nan']
            periods = events['period'].astype(str)
            invalid = events[~periods.isin(valid_periods)]
            assert len(invalid) == 0, f"Found {len(invalid)} events with invalid periods"
    
    def test_event_indices_sequential(self, events):
        """Event indices should be mostly sequential per game."""
        for game_id in events['game_id'].unique():
            game_events = events[events['game_id'] == game_id]
            if 'event_index' in game_events.columns:
                indices = sorted(game_events['event_index'].unique())
                gaps = 0
                for i in range(1, len(indices)):
                    if indices[i] - indices[i-1] > 10:  # Allow small gaps
                        gaps += 1
                assert gaps < 5, f"Game {game_id} has too many gaps in event indices"


# =============================================================================
# REFERENTIAL INTEGRITY TESTS
# =============================================================================

class TestReferentialIntegrity:
    """Tests for foreign key relationships."""
    
    def test_player_ids_in_dim_player(self, player_stats, dim_player):
        """All player_ids in stats should exist in dim_player."""
        stats_players = set(player_stats['player_id'].dropna().unique())
        dim_players = set(dim_player['player_id'].dropna().unique())
        orphans = stats_players - dim_players
        # Allow some orphans (subs, etc) but not too many
        orphan_pct = len(orphans) / len(stats_players) * 100 if stats_players else 0
        assert orphan_pct < 10, f"{orphan_pct:.1f}% orphan player_ids"


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
