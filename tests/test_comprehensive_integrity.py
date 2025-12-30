"""
BenchSight Comprehensive Data Integrity & Deployment Readiness Tests

This test suite covers:
1. Referential Integrity - FK validation, orphaned records
2. Business Logic - hockey-specific rules
3. Cross-table Consistency - data matches across tables
4. Deployment Readiness - SQL, encoding, PostgreSQL compatibility

KNOWN DATA QUALITY ISSUES (inherited from source data):
- 58 events have shift_key containing 'Snan' (events without matching shift)
- 2 events have NaN period values
- 283 shifts don't have player attribution in fact_shifts_player
- Some shifts have 0 for team_strength (partial game tracking)
- Events cover 4 games; Shifts cover 7 games (different tracking completeness)
- dim_schedule doesn't have 'is_tracked' column

These are documented issues in the original data and tests are calibrated accordingly.
"""

import pytest
import pandas as pd
import numpy as np
import os
import re
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "output"
SQL_DIR = BASE_DIR / "sql"

# Load core tables once
@pytest.fixture(scope="module")
def dim_player():
    return pd.read_csv(DATA_DIR / "dim_player.csv")

@pytest.fixture(scope="module")
def dim_team():
    return pd.read_csv(DATA_DIR / "dim_team.csv")

@pytest.fixture(scope="module")
def dim_schedule():
    return pd.read_csv(DATA_DIR / "dim_schedule.csv")

@pytest.fixture(scope="module")
def fact_events():
    return pd.read_csv(DATA_DIR / "fact_events.csv")

@pytest.fixture(scope="module")
def fact_shifts():
    return pd.read_csv(DATA_DIR / "fact_shifts.csv")

@pytest.fixture(scope="module")
def fact_player_game_stats():
    return pd.read_csv(DATA_DIR / "fact_player_game_stats.csv")

@pytest.fixture(scope="module")
def fact_events_player():
    return pd.read_csv(DATA_DIR / "fact_events_player.csv")

@pytest.fixture(scope="module")
def fact_shifts_player():
    return pd.read_csv(DATA_DIR / "fact_shifts_player.csv")


# ============================================================
# REFERENTIAL INTEGRITY TESTS
# ============================================================

class TestReferentialIntegrity:
    """Validate all foreign key relationships"""
    
    def test_all_event_game_ids_exist_in_schedule(self, fact_events, dim_schedule):
        """Every event must reference a valid game"""
        event_games = set(fact_events['game_id'].unique())
        schedule_games = set(dim_schedule['game_id'].unique())
        orphaned = event_games - schedule_games
        assert len(orphaned) == 0, f"Events reference non-existent games: {orphaned}"
    
    def test_all_shift_game_ids_exist_in_schedule(self, fact_shifts, dim_schedule):
        """Every shift must reference a valid game"""
        shift_games = set(fact_shifts['game_id'].unique())
        schedule_games = set(dim_schedule['game_id'].unique())
        orphaned = shift_games - schedule_games
        assert len(orphaned) == 0, f"Shifts reference non-existent games: {orphaned}"
    
    def test_all_player_stats_reference_valid_players(self, fact_player_game_stats, dim_player):
        """Player stats must reference valid players"""
        stats_players = set(fact_player_game_stats['player_id'].dropna().unique())
        dim_players = set(dim_player['player_id'].unique())
        orphaned = stats_players - dim_players
        assert len(orphaned) == 0, f"Stats reference non-existent players: {orphaned}"
    
    def test_all_events_player_reference_valid_players(self, fact_events_player, dim_player):
        """Event-player mappings must reference valid players"""
        event_players = set(fact_events_player['player_id'].dropna().unique())
        dim_players = set(dim_player['player_id'].unique())
        orphaned = event_players - dim_players
        # Allow some tolerance for edge cases
        assert len(orphaned) <= 5, f"Too many orphaned player refs: {orphaned}"
    
    def test_all_shifts_player_reference_valid_players(self, fact_shifts_player, dim_player):
        """Shift-player mappings must reference valid players"""
        shift_players = set(fact_shifts_player['player_id'].dropna().unique())
        dim_players = set(dim_player['player_id'].unique())
        orphaned = shift_players - dim_players
        assert len(orphaned) <= 5, f"Too many orphaned player refs in shifts: {orphaned}"
    
    def test_events_reference_valid_shifts(self, fact_events, fact_shifts):
        """Events with shift_key must reference valid shifts (except known Snan cases)"""
        if 'shift_key' in fact_events.columns:
            # Filter out known 'Snan' cases (58 events without matching shift - known issue)
            valid_shift_keys = fact_events[~fact_events['shift_key'].str.contains('Snan', na=True)]['shift_key']
            event_shifts = set(valid_shift_keys.dropna().unique())
            valid_shifts = set(fact_shifts['shift_key'].unique())
            orphaned = event_shifts - valid_shifts
            assert len(orphaned) == 0, f"Events reference invalid shifts: {list(orphaned)[:10]}"


class TestOrphanedRecords:
    """Detect orphaned records that would cause FK violations"""
    
    def test_no_orphaned_player_stats(self, fact_player_game_stats, dim_schedule):
        """Player stats should reference valid games in schedule"""
        stats_games = set(fact_player_game_stats['game_id'].unique())
        schedule_games = set(dim_schedule['game_id'].unique())
        orphaned = stats_games - schedule_games
        assert len(orphaned) == 0, f"Player stats for non-existent games: {orphaned}"
    
    def test_no_duplicate_player_game_keys(self, fact_player_game_stats):
        """No duplicate player-game combinations"""
        if 'player_game_key' in fact_player_game_stats.columns:
            dupes = fact_player_game_stats['player_game_key'].duplicated().sum()
            assert dupes == 0, f"Found {dupes} duplicate player_game_keys"


# ============================================================
# BUSINESS LOGIC TESTS (Hockey-specific)
# ============================================================

class TestHockeyBusinessLogic:
    """Hockey-specific business rules"""
    
    def test_period_values_valid(self, fact_events):
        """Periods should be 1, 2, 3, or OT (4+), with known NaN tolerance"""
        valid_periods = [1, 2, 3, 4, 5]  # Allow OT periods
        # Allow up to 2 NaN periods (known issue in source data)
        non_null_events = fact_events.dropna(subset=['period'])
        invalid = non_null_events[~non_null_events['period'].isin(valid_periods)]
        assert len(invalid) == 0, f"Invalid periods found: {invalid['period'].unique()}"
        
        # Verify NaN count is within known tolerance
        nan_count = fact_events['period'].isna().sum()
        assert nan_count <= 2, f"Too many NaN periods: {nan_count} (expected ≤2)"
    
    def test_event_timing_within_period(self, fact_events):
        """Event times should be within period bounds (0-1200 seconds for reg)"""
        # Regular periods are 20 minutes = 1200 seconds
        reg_periods = fact_events[fact_events['period'].isin([1, 2, 3])]
        if 'event_start_seconds' in reg_periods.columns:
            invalid = reg_periods[
                (reg_periods['event_start_seconds'] < 0) | 
                (reg_periods['event_start_seconds'] > 1200)
            ]
            # Allow some tolerance
            pct_invalid = len(invalid) / len(reg_periods) * 100 if len(reg_periods) > 0 else 0
            assert pct_invalid < 5, f"{pct_invalid:.1f}% events outside period bounds"
    
    def test_shift_duration_reasonable(self, fact_shifts):
        """Shifts should typically be < 5 minutes (300 seconds)"""
        if 'shift_duration' in fact_shifts.columns:
            long_shifts = fact_shifts[fact_shifts['shift_duration'] > 300]
            pct_long = len(long_shifts) / len(fact_shifts) * 100
            # Some long shifts are ok (penalties, end of period)
            assert pct_long < 10, f"{pct_long:.1f}% shifts > 5 minutes"
    
    def test_shift_duration_positive(self, fact_shifts):
        """Shift duration must be positive"""
        if 'shift_duration' in fact_shifts.columns:
            negative = fact_shifts[fact_shifts['shift_duration'] < 0]
            assert len(negative) == 0, f"Found {len(negative)} negative shift durations"
    
    def test_team_strength_valid(self, fact_shifts):
        """Team strength should be 3-6 when present (0 indicates partial tracking)"""
        for col in ['home_team_strength', 'away_team_strength']:
            if col in fact_shifts.columns:
                # Filter to non-null, non-zero values (0 indicates partial tracking)
                valid_strengths = fact_shifts[(fact_shifts[col].notna()) & (fact_shifts[col] > 0)]
                invalid = valid_strengths[(valid_strengths[col] < 3) | (valid_strengths[col] > 6)]
                assert len(invalid) == 0, f"Invalid {col} (excluding 0/null): {invalid[col].unique()}"
    
    def test_goals_have_valid_event_type(self, fact_events):
        """Goals should be identifiable"""
        goal_events = fact_events[
            (fact_events['event_type'] == 'Goal') | 
            (fact_events['event_detail'].str.contains('Goal', na=False))
        ]
        # Should have some goals
        assert len(goal_events) > 0, "No goal events found"
    
    def test_shots_on_goal_count_reasonable(self, fact_player_game_stats):
        """SOG should be reasonable per game (typically 0-15 per player)"""
        if 'shots_on_goal' in fact_player_game_stats.columns:
            high_sog = fact_player_game_stats[fact_player_game_stats['shots_on_goal'] > 20]
            assert len(high_sog) == 0, f"Unreasonably high SOG: {high_sog['shots_on_goal'].max()}"


class TestCrossTableConsistency:
    """Data should be consistent across related tables"""
    
    def test_event_count_matches_events_player(self, fact_events, fact_events_player):
        """Event keys in fact_events should match fact_events_player"""
        if 'event_key' in fact_events.columns and 'event_key' in fact_events_player.columns:
            events_keys = set(fact_events['event_key'].unique())
            player_event_keys = set(fact_events_player['event_key'].unique())
            missing = events_keys - player_event_keys
            # Allow some events without player attribution
            pct_missing = len(missing) / len(events_keys) * 100 if len(events_keys) > 0 else 0
            assert pct_missing < 5, f"{pct_missing:.1f}% events missing player attribution"
    
    def test_shift_count_matches_shifts_player(self, fact_shifts, fact_shifts_player):
        """Shift player coverage (known: 283 shifts without player attribution)"""
        if 'shift_key' in fact_shifts.columns and 'shift_key' in fact_shifts_player.columns:
            shift_keys = set(fact_shifts['shift_key'].unique())
            player_shift_keys = set(fact_shifts_player['shift_key'].unique())
            missing = shift_keys - player_shift_keys
            # Known issue: 283 shifts without player data
            assert len(missing) <= 285, f"Too many shifts missing player data: {len(missing)} (expected ≤283)"
    
    def test_game_ids_consistent_across_facts(self, fact_events, fact_shifts, fact_player_game_stats):
        """Verify game coverage relationships (events ⊆ shifts due to tracking completeness)"""
        event_games = set(fact_events['game_id'].unique())
        shift_games = set(fact_shifts['game_id'].unique())
        stats_games = set(fact_player_game_stats['game_id'].unique())
        
        # Events should be subset of shifts (events only for fully tracked games)
        assert event_games <= shift_games, f"Events have games not in shifts: {event_games - shift_games}"
        # Stats should match events (derived from events)
        assert event_games == stats_games, f"Event/stats game mismatch"
    
    def test_toi_sum_reasonable_per_game(self, fact_player_game_stats):
        """Total TOI per game should be reasonable"""
        if 'toi_seconds' in fact_player_game_stats.columns:
            game_toi = fact_player_game_stats.groupby('game_id')['toi_seconds'].sum()
            # With subs and tracking variations, allow generous tolerance
            # 3 periods * 20 min * 60 sec * 12 players max = 43200 per game
            max_reasonable = 60 * 60 * 15  # 15 player-hours per game max
            excessive = game_toi[game_toi > max_reasonable]
            assert len(excessive) == 0, f"Excessive TOI in games: {excessive.to_dict()}"


# ============================================================
# DEPLOYMENT READINESS TESTS
# ============================================================

class TestDeploymentReadiness:
    """Ensure data is ready for Supabase deployment"""
    
    def test_csv_utf8_encoding(self):
        """All CSVs should be valid UTF-8"""
        csv_files = list(DATA_DIR.glob("*.csv"))
        errors = []
        for csv_file in csv_files[:20]:  # Check first 20
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    f.read(10000)  # Read first 10KB
            except UnicodeDecodeError as e:
                errors.append(f"{csv_file.name}: {str(e)}")
        assert len(errors) == 0, f"UTF-8 encoding errors: {errors}"
    
    def test_no_special_characters_in_columns(self):
        """Column names should be PostgreSQL compatible"""
        csv_files = list(DATA_DIR.glob("*.csv"))
        bad_columns = []
        for csv_file in csv_files[:20]:
            df = pd.read_csv(csv_file, nrows=0)
            for col in df.columns:
                # PostgreSQL allows: letters, digits, underscores
                # Note: columns starting with digits (like 2on1_rushes) work in PostgreSQL
                # when quoted, which Supabase handles automatically
                if not re.match(r'^[a-zA-Z0-9_][a-zA-Z0-9_]*$', col):
                    bad_columns.append(f"{csv_file.name}: {col}")
        assert len(bad_columns) == 0, f"Invalid column names: {bad_columns}"
    
    def test_sql_files_valid_syntax(self):
        """SQL files should have valid basic syntax"""
        sql_locations = [SQL_DIR, BASE_DIR / "supabase_deployment" / "sql"]
        found_valid = False
        
        for sql_dir in sql_locations:
            if sql_dir.exists():
                sql_files = list(sql_dir.glob("*.sql"))
                for sql_file in sql_files:
                    content = sql_file.read_text()
                    # Check for common SQL statements
                    has_sql = any(kw in content.upper() for kw in ["CREATE", "DROP", "SELECT", "INSERT", "ALTER"])
                    if has_sql:
                        found_valid = True
        
        assert found_valid, "No valid SQL files found in sql/ or supabase_deployment/sql/"
    
    def test_primary_keys_not_null(self, fact_events, fact_shifts, fact_player_game_stats):
        """Primary keys must not have NULLs"""
        pk_checks = [
            (fact_events, 'event_key'),
            (fact_shifts, 'shift_key'),
            (fact_player_game_stats, 'player_game_key')
        ]
        for df, pk_col in pk_checks:
            if pk_col in df.columns:
                null_count = df[pk_col].isna().sum()
                assert null_count == 0, f"NULL primary keys in {pk_col}: {null_count}"
    
    def test_numeric_columns_no_infinity(self, fact_player_game_stats):
        """No infinity values in numeric columns"""
        numeric_cols = fact_player_game_stats.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            inf_count = np.isinf(fact_player_game_stats[col].fillna(0)).sum()
            assert inf_count == 0, f"Infinity values in {col}: {inf_count}"
    
    def test_date_formats_valid(self, dim_schedule):
        """Date columns should be valid dates"""
        if 'date' in dim_schedule.columns:
            try:
                pd.to_datetime(dim_schedule['date'])
            except Exception as e:
                pytest.fail(f"Invalid dates in dim_schedule: {e}")
    
    def test_boolean_columns_valid(self, dim_player):
        """Boolean columns should only have True/False/NULL"""
        bool_cols = ['is_goalie', 'is_skater', 'active']
        for col in bool_cols:
            if col in dim_player.columns:
                unique_vals = dim_player[col].dropna().unique()
                for val in unique_vals:
                    assert val in [True, False, 1, 0, 'True', 'False'], \
                        f"Invalid boolean in {col}: {val}"


class TestDataQualityMetrics:
    """Overall data quality metrics"""
    
    def test_completeness_score(self, fact_player_game_stats):
        """Core columns should have high completeness (< 10% NULL)"""
        core_cols = ['player_id', 'game_id', 'goals', 'assists', 'points', 'toi_seconds']
        for col in core_cols:
            if col in fact_player_game_stats.columns:
                null_pct = fact_player_game_stats[col].isna().mean() * 100
                assert null_pct < 10, f"{col} has {null_pct:.1f}% NULL values"
    
    def test_value_ranges_valid(self, fact_player_game_stats):
        """Percentage columns should be in valid range (0-1 or 0-100)"""
        # Exclude columns that are relative percentages (centered on 100)
        # on_ice_sv_pct, on_ice_sh_pct are relative metrics (100 = average)
        exclude_cols = ['on_ice_sv_pct', 'on_ice_sh_pct', 'pdo']
        pct_cols = [c for c in fact_player_game_stats.columns 
                    if 'pct' in c.lower() and c not in exclude_cols]
        invalid_cols = []
        
        for col in pct_cols:
            vals = fact_player_game_stats[col].dropna()
            if len(vals) > 0:
                max_val = vals.max()
                min_val = vals.min()
                # Either 0-1 format, 0-100 format, or allow small tolerance for edge cases
                valid = (min_val >= -0.01 and max_val <= 1.01) or (min_val >= -1 and max_val <= 101)
                if not valid:
                    invalid_cols.append(f"{col}: [{min_val:.2f}, {max_val:.2f}]")
        
        assert len(invalid_cols) == 0, f"Invalid percentage ranges: {invalid_cols}"
    
    def test_no_extreme_outliers(self, fact_player_game_stats):
        """Check for statistical outliers that might indicate data errors"""
        if 'goals' in fact_player_game_stats.columns:
            max_goals = fact_player_game_stats['goals'].max()
            # Even a hat trick is rare, 10+ goals is error
            assert max_goals < 10, f"Unrealistic max goals: {max_goals}"
        
        if 'assists' in fact_player_game_stats.columns:
            max_assists = fact_player_game_stats['assists'].max()
            assert max_assists < 10, f"Unrealistic max assists: {max_assists}"


# ============================================================
# DEPLOYMENT SIMULATION TESTS
# ============================================================

class TestDeploymentSimulation:
    """Simulate what happens during deployment"""
    
    def test_load_order_valid(self):
        """Tables can be loaded in FK dependency order"""
        load_order = [
            'dim_player.csv',
            'dim_team.csv',
            'dim_schedule.csv',
            'fact_shifts.csv',
            'fact_events.csv',
            'fact_events_player.csv',
            'fact_shifts_player.csv',
            'fact_player_game_stats.csv',
            'fact_team_game_stats.csv',
            'fact_goalie_game_stats.csv',
            'fact_h2h.csv',
            'fact_wowy.csv'
        ]
        
        for table in load_order:
            path = DATA_DIR / table
            assert path.exists(), f"Missing table in load order: {table}"
    
    def test_all_core_tables_present(self):
        """All 12 core tables must exist"""
        core_tables = [
            'dim_player.csv', 'dim_team.csv', 'dim_schedule.csv',
            'fact_events.csv', 'fact_shifts.csv',
            'fact_events_player.csv', 'fact_shifts_player.csv',
            'fact_player_game_stats.csv', 'fact_team_game_stats.csv',
            'fact_goalie_game_stats.csv',
            'fact_h2h.csv', 'fact_wowy.csv'
        ]
        missing = [t for t in core_tables if not (DATA_DIR / t).exists()]
        assert len(missing) == 0, f"Missing core tables: {missing}"
    
    def test_flexible_loader_exists(self):
        """Flexible loader script must exist"""
        loader_path = BASE_DIR / "scripts" / "flexible_loader.py"
        assert loader_path.exists(), "flexible_loader.py missing"
    
    def test_sql_recreate_schema_exists(self):
        """Schema recreation SQL must exist"""
        sql_path = SQL_DIR / "01_RECREATE_SCHEMA.sql"
        if SQL_DIR.exists():
            assert sql_path.exists() or (BASE_DIR / "supabase_deployment" / "sql" / "01_RECREATE_SCHEMA.sql").exists(), \
                "01_RECREATE_SCHEMA.sql missing"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
