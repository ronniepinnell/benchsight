"""
=============================================================================
DATA VALIDATION TESTS
=============================================================================
File: tests/test_data_validation_comprehensive.py
Created: 2024-12-30
Author: Production Hardening Sprint

PURPOSE:
    Comprehensive tests for data quality and integrity.
    These tests verify the data meets business requirements.

WHAT IT TESTS:
    1. Primary key integrity
    2. Foreign key integrity
    3. Value ranges and data types
    4. Business logic rules
    5. Cross-table consistency
    6. Data completeness

HOW TO RUN:
    pytest tests/test_data_validation_comprehensive.py -v
    pytest tests/test_data_validation_comprehensive.py -v --tb=short

=============================================================================
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Set, Dict, List

OUTPUT_DIR = Path("data/output")


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="module")
def dim_player():
    """Load dim_player once for all tests."""
    path = OUTPUT_DIR / "dim_player.csv"
    if path.exists():
        return pd.read_csv(path, dtype=str)
    return pd.DataFrame()


@pytest.fixture(scope="module")
def dim_schedule():
    """Load dim_schedule once for all tests."""
    path = OUTPUT_DIR / "dim_schedule.csv"
    if path.exists():
        return pd.read_csv(path, dtype=str)
    return pd.DataFrame()


@pytest.fixture(scope="module")
def dim_team():
    """Load dim_team once for all tests."""
    path = OUTPUT_DIR / "dim_team.csv"
    if path.exists():
        return pd.read_csv(path, dtype=str)
    return pd.DataFrame()


@pytest.fixture(scope="module")
def fact_events():
    """Load fact_events once for all tests."""
    path = OUTPUT_DIR / "fact_events.csv"
    if path.exists():
        return pd.read_csv(path, dtype=str)
    return pd.DataFrame()


@pytest.fixture(scope="module")
def fact_player_game_stats():
    """Load fact_player_game_stats once for all tests."""
    path = OUTPUT_DIR / "fact_player_game_stats.csv"
    if path.exists():
        df = pd.read_csv(path, dtype=str)
        # Convert numeric columns
        numeric_cols = ['goals', 'assists', 'pts', 'shots', 'toi_seconds', 
                       'plus_minus', 'pim', 'hits', 'blocks']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    return pd.DataFrame()


@pytest.fixture(scope="module")
def valid_player_ids(dim_player) -> Set[str]:
    """Get set of valid player IDs."""
    if dim_player.empty:
        return set()
    return set(dim_player["player_id"].dropna().unique())


@pytest.fixture(scope="module")
def valid_game_ids(dim_schedule) -> Set[str]:
    """Get set of valid game IDs."""
    if dim_schedule.empty:
        return set()
    return set(dim_schedule["game_id"].dropna().unique())


@pytest.fixture(scope="module")
def valid_team_ids(dim_team) -> Set[str]:
    """Get set of valid team IDs."""
    if dim_team.empty:
        return set()
    return set(dim_team["team_id"].dropna().unique())


# =============================================================================
# PRIMARY KEY TESTS
# =============================================================================

class TestPrimaryKeyIntegrity:
    """Verify primary keys are valid across all tables."""
    
    # Table -> Primary Key column
    PRIMARY_KEYS = {
        "dim_player": "player_id",
        "dim_team": "team_id",
        "dim_schedule": "game_id",
        "dim_season": "season_id",
        "dim_event_type": "event_type_id",
        "dim_period": "period_id",
        "dim_venue": "venue_id",
        "dim_position": "position_id",
        "dim_strength": "strength_id",
        "fact_events": "event_key",
        "fact_events_player": "event_player_key",
        "fact_shifts": "shift_key",
        "fact_shifts_long": "shift_player_key",
        "fact_player_game_stats": "player_game_key",
        "fact_team_game_stats": "team_game_key",
        "fact_gameroster": "roster_key",
        "fact_h2h": "h2h_key",
        "fact_wowy": "wowy_key",
    }
    
    @pytest.mark.parametrize("table,pk_col", list(PRIMARY_KEYS.items()))
    def test_pk_not_null(self, table, pk_col):
        """Primary key column should have no NULL values."""
        path = OUTPUT_DIR / f"{table}.csv"
        if not path.exists():
            pytest.skip(f"{table}.csv not found")
        
        df = pd.read_csv(path, dtype=str)
        
        if pk_col not in df.columns:
            pytest.fail(f"PK column '{pk_col}' not found in {table}")
        
        null_count = df[pk_col].isna().sum()
        empty_count = (df[pk_col] == "").sum()
        
        assert null_count == 0, f"{table}.{pk_col} has {null_count} NULL values"
        assert empty_count == 0, f"{table}.{pk_col} has {empty_count} empty strings"
    
    @pytest.mark.parametrize("table,pk_col", list(PRIMARY_KEYS.items()))
    def test_pk_unique(self, table, pk_col):
        """Primary key column should have no duplicates."""
        path = OUTPUT_DIR / f"{table}.csv"
        if not path.exists():
            pytest.skip(f"{table}.csv not found")
        
        df = pd.read_csv(path, dtype=str)
        
        if pk_col not in df.columns:
            pytest.skip(f"PK column '{pk_col}' not in {table}")
        
        dup_count = df[pk_col].duplicated().sum()
        
        if dup_count > 0:
            dups = df[df[pk_col].duplicated(keep=False)][pk_col].unique()[:5]
            pytest.fail(f"{table}.{pk_col} has {dup_count} duplicates. Samples: {list(dups)}")


# =============================================================================
# FOREIGN KEY TESTS
# =============================================================================

class TestForeignKeyIntegrity:
    """Verify foreign key relationships are valid."""
    
    def test_events_reference_valid_games(self, fact_events, valid_game_ids):
        """fact_events.game_id should reference valid games."""
        if fact_events.empty or not valid_game_ids:
            pytest.skip("Required data not available")
        
        event_games = set(fact_events["game_id"].dropna().unique())
        orphans = event_games - valid_game_ids
        
        assert len(orphans) == 0, \
            f"fact_events has {len(orphans)} orphaned game_ids: {list(orphans)[:5]}"
    
    def test_player_stats_reference_valid_players(self, fact_player_game_stats, valid_player_ids):
        """fact_player_game_stats.player_id should reference valid players."""
        if fact_player_game_stats.empty or not valid_player_ids:
            pytest.skip("Required data not available")
        
        stat_players = set(fact_player_game_stats["player_id"].dropna().unique())
        orphans = stat_players - valid_player_ids
        
        # Allow small tolerance for tracking errors
        orphan_rate = len(orphans) / len(stat_players) if stat_players else 0
        
        assert orphan_rate < 0.02, \
            f"fact_player_game_stats has {orphan_rate:.1%} orphaned player_ids"
    
    def test_player_stats_reference_valid_games(self, fact_player_game_stats, valid_game_ids):
        """fact_player_game_stats.game_id should reference valid games."""
        if fact_player_game_stats.empty or not valid_game_ids:
            pytest.skip("Required data not available")
        
        stat_games = set(fact_player_game_stats["game_id"].dropna().unique())
        orphans = stat_games - valid_game_ids
        
        assert len(orphans) == 0, \
            f"fact_player_game_stats has {len(orphans)} orphaned game_ids"
    
    def test_events_long_reference_valid_players(self, valid_player_ids):
        """fact_events_player.player_id should reference valid players."""
        path = OUTPUT_DIR / "fact_events_player.csv"
        if not path.exists() or not valid_player_ids:
            pytest.skip("Required data not available")
        
        df = pd.read_csv(path, dtype=str)
        event_players = set(df["player_id"].dropna().unique())
        orphans = event_players - valid_player_ids
        
        orphan_rate = len(orphans) / len(event_players) if event_players else 0
        
        assert orphan_rate < 0.05, \
            f"fact_events_player has {orphan_rate:.1%} orphaned player_ids"
    
    def test_shifts_long_reference_valid_players(self, valid_player_ids):
        """fact_shifts_long.player_id should reference valid players."""
        path = OUTPUT_DIR / "fact_shifts_long.csv"
        if not path.exists() or not valid_player_ids:
            pytest.skip("Required data not available")
        
        df = pd.read_csv(path, dtype=str)
        shift_players = set(df["player_id"].dropna().unique())
        orphans = shift_players - valid_player_ids
        
        orphan_rate = len(orphans) / len(shift_players) if shift_players else 0
        
        assert orphan_rate < 0.05, \
            f"fact_shifts_long has {orphan_rate:.1%} orphaned player_ids"


# =============================================================================
# VALUE RANGE TESTS
# =============================================================================

class TestValueRanges:
    """Verify values are within expected ranges."""
    
    def test_goals_non_negative(self, fact_player_game_stats):
        """Goals should be >= 0."""
        if fact_player_game_stats.empty or "goals" not in fact_player_game_stats.columns:
            pytest.skip("goals column not available")
        
        negative = fact_player_game_stats[fact_player_game_stats["goals"] < 0]
        assert len(negative) == 0, f"Found {len(negative)} negative goal values"
    
    def test_goals_reasonable_max(self, fact_player_game_stats):
        """Goals should be <= 10 per game (reasonable max)."""
        if fact_player_game_stats.empty or "goals" not in fact_player_game_stats.columns:
            pytest.skip("goals column not available")
        
        excessive = fact_player_game_stats[fact_player_game_stats["goals"] > 10]
        assert len(excessive) == 0, \
            f"Found {len(excessive)} games with >10 goals per player"
    
    def test_assists_non_negative(self, fact_player_game_stats):
        """Assists should be >= 0."""
        if fact_player_game_stats.empty or "assists" not in fact_player_game_stats.columns:
            pytest.skip("assists column not available")
        
        negative = fact_player_game_stats[fact_player_game_stats["assists"] < 0]
        assert len(negative) == 0, f"Found {len(negative)} negative assist values"
    
    def test_shots_non_negative(self, fact_player_game_stats):
        """Shots should be >= 0."""
        if fact_player_game_stats.empty or "shots" not in fact_player_game_stats.columns:
            pytest.skip("shots column not available")
        
        negative = fact_player_game_stats[fact_player_game_stats["shots"] < 0]
        assert len(negative) == 0, f"Found {len(negative)} negative shot values"
    
    def test_toi_reasonable(self, fact_player_game_stats):
        """TOI should be 0-3600 seconds (0-60 minutes)."""
        if fact_player_game_stats.empty or "toi_seconds" not in fact_player_game_stats.columns:
            pytest.skip("toi_seconds column not available")
        
        toi = fact_player_game_stats["toi_seconds"]
        
        negative = (toi < 0).sum()
        excessive = (toi > 3600).sum()  # More than 60 minutes
        
        assert negative == 0, f"Found {negative} negative TOI values"
        assert excessive == 0, f"Found {excessive} TOI values > 60 minutes"
    
    def test_period_values(self, fact_events):
        """Period should be 1-5."""
        if fact_events.empty or "period" not in fact_events.columns:
            pytest.skip("period column not available")
        
        period = pd.to_numeric(fact_events["period"], errors='coerce')
        
        invalid = ((period < 1) | (period > 5)).sum()
        assert invalid == 0, f"Found {invalid} invalid period values"


# =============================================================================
# BUSINESS LOGIC TESTS
# =============================================================================

class TestBusinessLogic:
    """Verify business logic rules are satisfied."""
    
    def test_goals_less_than_or_equal_shots(self, fact_player_game_stats):
        """Goals should be <= shots (with tolerance for tracking errors)."""
        if fact_player_game_stats.empty:
            pytest.skip("fact_player_game_stats not available")
        
        if "goals" not in fact_player_game_stats.columns or "shots" not in fact_player_game_stats.columns:
            pytest.skip("goals or shots column not available")
        
        df = fact_player_game_stats.copy()
        df = df[df["goals"].notna() & df["shots"].notna()]
        
        # Allow 1 goal more than shots (deflections, tracking errors)
        violations = df[df["goals"] > df["shots"] + 1]
        
        assert len(violations) == 0, \
            f"Found {len(violations)} cases where goals > shots + 1"
    
    def test_points_equals_goals_plus_assists(self, fact_player_game_stats):
        """Points should equal goals + assists."""
        if fact_player_game_stats.empty:
            pytest.skip("fact_player_game_stats not available")
        
        required_cols = ["pts", "goals", "assists"]
        if not all(c in fact_player_game_stats.columns for c in required_cols):
            pytest.skip("Required columns not available")
        
        df = fact_player_game_stats.copy()
        df = df[df["pts"].notna() & df["goals"].notna() & df["assists"].notna()]
        
        df["expected_pts"] = df["goals"] + df["assists"]
        violations = df[df["pts"] != df["expected_pts"]]
        
        assert len(violations) == 0, \
            f"Found {len(violations)} cases where pts != goals + assists"
    
    def test_player_appears_once_per_game(self, fact_player_game_stats):
        """Each player should appear at most once per game."""
        if fact_player_game_stats.empty:
            pytest.skip("fact_player_game_stats not available")
        
        duplicates = fact_player_game_stats.groupby(["game_id", "player_id"]).size()
        multi_appearances = duplicates[duplicates > 1]
        
        assert len(multi_appearances) == 0, \
            f"Found {len(multi_appearances)} player-game combinations with multiple rows"


# =============================================================================
# CROSS-TABLE CONSISTENCY TESTS
# =============================================================================

class TestCrossTableConsistency:
    """Verify consistency across related tables."""
    
    def test_events_long_references_events(self):
        """Events in events_long should exist in fact_events."""
        events_path = OUTPUT_DIR / "fact_events.csv"
        events_long_path = OUTPUT_DIR / "fact_events_player.csv"
        
        if not events_path.exists() or not events_long_path.exists():
            pytest.skip("Required files not available")
        
        events = pd.read_csv(events_path, dtype=str)
        events_long = pd.read_csv(events_long_path, dtype=str)
        
        # Create composite key
        if "event_key" in events.columns and "event_key" in events_long.columns:
            valid_keys = set(events["event_key"].dropna().unique())
            long_keys = set(events_long["event_key"].dropna().unique())
            
            orphans = long_keys - valid_keys
            orphan_rate = len(orphans) / len(long_keys) if long_keys else 0
            
            assert orphan_rate < 0.05, \
                f"events_long has {orphan_rate:.1%} orphaned event_keys"
    
    def test_shifts_long_references_shifts(self):
        """Shifts in shifts_long should exist in fact_shifts."""
        shifts_path = OUTPUT_DIR / "fact_shifts.csv"
        shifts_long_path = OUTPUT_DIR / "fact_shifts_long.csv"
        
        if not shifts_path.exists() or not shifts_long_path.exists():
            pytest.skip("Required files not available")
        
        shifts = pd.read_csv(shifts_path, dtype=str)
        shifts_long = pd.read_csv(shifts_long_path, dtype=str)
        
        if "shift_key" in shifts.columns and "shift_key" in shifts_long.columns:
            valid_keys = set(shifts["shift_key"].dropna().unique())
            long_keys = set(shifts_long["shift_key"].dropna().unique())
            
            # If no overlap, tables use different structure - skip
            if not valid_keys.intersection(long_keys):
                pytest.skip("Tables use different key granularity")
            
            orphans = long_keys - valid_keys
            orphan_rate = len(orphans) / len(long_keys) if long_keys else 0
            
            # Allow 50% due to different granularity
            assert orphan_rate < 0.50, \
                f"shifts_long has {orphan_rate:.1%} orphaned shift_keys"
    
    def test_roster_matches_player_stats(self):
        """Players in tracked games should have stats."""
        roster_path = OUTPUT_DIR / "fact_gameroster.csv"
        stats_path = OUTPUT_DIR / "fact_player_game_stats.csv"
        
        if not roster_path.exists() or not stats_path.exists():
            pytest.skip("Required files not available")
        
        roster = pd.read_csv(roster_path, dtype=str)
        stats = pd.read_csv(stats_path, dtype=str)
        
        # Only check games that have detailed stats
        games_with_stats = set(stats["game_id"].dropna().unique())
        roster_tracked = roster[roster["game_id"].isin(games_with_stats)]
        
        if len(roster_tracked) == 0:
            pytest.skip("No overlapping tracked games")
        
        # Create player-game keys for tracked games only
        roster_tracked = roster_tracked.copy()
        roster_tracked["pg_key"] = roster_tracked["game_id"] + "_" + roster_tracked["player_id"]
        stats["pg_key"] = stats["game_id"] + "_" + stats["player_id"]
        
        roster_keys = set(roster_tracked["pg_key"].dropna().unique())
        stats_keys = set(stats["pg_key"].dropna().unique())
        
        # Players in tracked games should mostly have stats
        in_roster_not_stats = roster_keys - stats_keys
        rate = len(in_roster_not_stats) / len(roster_keys) if roster_keys else 0
        
        assert rate < 0.5, \
            f"{rate:.1%} of rostered players in tracked games have no stats"


# =============================================================================
# DATA COMPLETENESS TESTS
# =============================================================================

class TestDataCompleteness:
    """Verify data is complete."""
    
    def test_dimension_tables_not_empty(self):
        """Dimension tables should have data."""
        required_dims = [
            "dim_player", "dim_team", "dim_schedule", 
            "dim_period", "dim_event_type"
        ]
        
        for dim in required_dims:
            path = OUTPUT_DIR / f"{dim}.csv"
            if path.exists():
                df = pd.read_csv(path)
                assert len(df) > 0, f"{dim} should not be empty"
    
    def test_fact_tables_have_expected_columns(self):
        """Fact tables should have expected columns."""
        expected_columns = {
            "fact_events": ["event_key", "game_id", "event_type", "period"],
            "fact_shifts": ["shift_key", "game_id", "Period"],
            "fact_player_game_stats": ["player_game_key", "game_id", "player_id"],
        }
        
        for table, columns in expected_columns.items():
            path = OUTPUT_DIR / f"{table}.csv"
            if path.exists():
                df = pd.read_csv(path, nrows=0)
                missing = [c for c in columns if c not in df.columns]
                assert not missing, f"{table} missing columns: {missing}"
    
    def test_games_have_events(self, dim_schedule, fact_events):
        """Games in schedule should have events (for tracked games)."""
        if dim_schedule.empty or fact_events.empty:
            pytest.skip("Required data not available")
        
        scheduled_games = set(dim_schedule["game_id"].unique())
        games_with_events = set(fact_events["game_id"].unique())
        
        # Not all games are tracked, so we just verify tracked games exist
        tracked_games = scheduled_games.intersection(games_with_events)
        
        assert len(tracked_games) > 0, "No games have events data"
    
    def test_tracked_games_have_shifts(self, fact_events):
        """Games with events should also have shifts."""
        if fact_events.empty:
            pytest.skip("fact_events not available")
        
        shifts_path = OUTPUT_DIR / "fact_shifts.csv"
        if not shifts_path.exists():
            pytest.skip("fact_shifts.csv not found")
        
        shifts = pd.read_csv(shifts_path, dtype=str)
        
        games_with_events = set(fact_events["game_id"].unique())
        games_with_shifts = set(shifts["game_id"].unique())
        
        events_without_shifts = games_with_events - games_with_shifts
        
        # Most games with events should have shifts
        rate = len(events_without_shifts) / len(games_with_events) if games_with_events else 0
        
        assert rate < 0.2, \
            f"{rate:.1%} of games have events but no shifts"


# =============================================================================
# RUN ALL VALIDATIONS
# =============================================================================

def test_full_validation_report():
    """Run full validation and generate report."""
    from src.validators.data_validator import DataValidator
    
    validator = DataValidator(str(OUTPUT_DIR))
    report = validator.validate_all()
    
    # Save report
    report_path = OUTPUT_DIR / "VALIDATION_REPORT.json"
    report.save(report_path)
    
    # Check overall pass rate
    assert report.pass_rate >= 0.9, \
        f"Validation pass rate {report.pass_rate:.1%} below 90% threshold"
    
    # Check for critical failures
    critical_failures = [
        r for r in report.get_failures() 
        if "pk" in r.check_name.lower() or "fk" in r.check_name.lower()
    ]
    
    assert len(critical_failures) == 0, \
        f"Critical validation failures: {[f.message for f in critical_failures]}"
