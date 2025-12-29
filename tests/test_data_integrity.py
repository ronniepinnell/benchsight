"""
BENCHSIGHT v5.0.0 - Comprehensive Data Integrity Tests
======================================================
"""

import pytest
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path("data/output")

VALID_TRACKING_GAMES = ['18969', '18977', '18981', '18987', '18991']
EXCLUDED_GAMES = ['18965', '18993', '19032']


class TestTableExistence:
    """Verify all required tables exist"""
    
    REQUIRED_TABLES = [
        # Dimensions
        'dim_player', 'dim_team', 'dim_league', 'dim_season', 'dim_schedule',
        'dim_player_role', 'dim_position', 'dim_zone', 'dim_period', 'dim_venue',
        'dim_playerurlref', 'dim_rinkboxcoord', 'dim_rinkcoordzones', 'dim_randomnames',
        'dim_event_type', 'dim_shift_slot', 'dim_strength',
        # Facts
        'fact_gameroster', 'fact_events', 'fact_events_long', 'fact_events_tracking',
        'fact_shifts', 'fact_shifts_long', 'fact_shifts_tracking',
        'fact_playergames', 'fact_draft', 'fact_registration', 'fact_leadership',
    ]
    
    @pytest.mark.parametrize("table", REQUIRED_TABLES)
    def test_table_exists(self, table):
        path = OUTPUT_DIR / f"{table}.csv"
        assert path.exists(), f"Missing table: {table}"


class TestPrimaryKeyIntegrity:
    """Verify primary keys have no nulls and no duplicates"""
    
    PRIMARY_KEYS = [
        ('dim_player', 'player_id'),
        ('dim_team', 'team_id'),
        ('dim_schedule', 'game_id'),
        ('dim_event_type', 'event_type_id'),
        ('dim_shift_slot', 'slot_id'),
        ('dim_position', 'position_id'),
        ('dim_strength', 'strength_id'),
        ('dim_period', 'period_id'),
        ('dim_venue', 'venue_id'),
        ('dim_zone', 'zone_id'),
        ('fact_gameroster', 'player_game_id'),
        ('fact_events', 'event_id'),
        ('fact_events_long', 'event_player_id'),
        ('fact_shifts', 'shift_id'),
        ('fact_shifts_long', 'shift_player_id'),
    ]
    
    @pytest.mark.parametrize("table,pk", PRIMARY_KEYS)
    def test_pk_no_nulls(self, table, pk):
        path = OUTPUT_DIR / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            if pk in df.columns:
                null_count = df[pk].isna().sum()
                assert null_count == 0, f"{table}.{pk} has {null_count} NULL values"
    
    @pytest.mark.parametrize("table,pk", PRIMARY_KEYS)
    def test_pk_no_duplicates(self, table, pk):
        path = OUTPUT_DIR / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            if pk in df.columns:
                dup_count = df.duplicated(subset=[pk]).sum()
                assert dup_count == 0, f"{table}.{pk} has {dup_count} duplicates"


class TestForeignKeyPresence:
    """Verify FK columns exist in fact tables"""
    
    FK_REQUIREMENTS = [
        ('fact_events', ['game_id', 'period_id', 'event_type_id']),
        ('fact_events_long', ['event_id', 'game_id', 'player_id', 'period_id', 'event_type_id']),
        ('fact_shifts', ['game_id', 'period_id']),
        ('fact_shifts_long', ['shift_id', 'game_id', 'player_id', 'slot_id', 'venue_id', 'period_id']),
        ('fact_gameroster', ['game_id', 'player_id', 'team_id']),
    ]
    
    @pytest.mark.parametrize("table,fks", FK_REQUIREMENTS)
    def test_fk_columns_exist(self, table, fks):
        path = OUTPUT_DIR / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str, nrows=0)
            missing = [fk for fk in fks if fk not in df.columns]
            assert not missing, f"{table} missing FK columns: {missing}"


class TestGameCoverage:
    """Verify correct games in tracking tables"""
    
    TRACKING_TABLES = ['fact_events', 'fact_shifts', 'fact_events_long', 'fact_shifts_long']
    
    @pytest.mark.parametrize("table", TRACKING_TABLES)
    def test_valid_games_present(self, table):
        path = OUTPUT_DIR / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            games = set(df['game_id'].unique())
            missing = set(VALID_TRACKING_GAMES) - games
            assert not missing, f"{table} missing games: {missing}"
    
    @pytest.mark.parametrize("table", TRACKING_TABLES)
    def test_excluded_games_not_present(self, table):
        path = OUTPUT_DIR / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            games = set(df['game_id'].unique())
            unexpected = games.intersection(set(EXCLUDED_GAMES))
            assert not unexpected, f"{table} has excluded games: {unexpected}"


class TestPlayerIdLinkage:
    """Verify player_id linkage"""
    
    PLAYER_TABLES = [
        ('fact_events_long', 0.95),
        ('fact_shifts_long', 0.95),
        ('fact_gameroster', 0.99),
    ]
    
    @pytest.mark.parametrize("table,threshold", PLAYER_TABLES)
    def test_player_id_linkage_rate(self, table, threshold):
        path = OUTPUT_DIR / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            if 'player_id' in df.columns:
                linked = df['player_id'].notna().sum()
                total = len(df)
                rate = linked / total if total > 0 else 0
                assert rate >= threshold, f"{table} player_id linkage {rate:.1%} < {threshold:.0%}"


class TestDimensionTables:
    """Verify dimension tables are complete"""
    
    def test_dim_position_has_extra_attacker(self):
        df = pd.read_csv(OUTPUT_DIR / "dim_position.csv", dtype=str)
        codes = df['position_code'].tolist()
        assert 'X' in codes, "dim_position missing X (Extra Attacker)"
    
    def test_dim_shift_slot_has_7_slots(self):
        df = pd.read_csv(OUTPUT_DIR / "dim_shift_slot.csv", dtype=str)
        assert len(df) == 7, f"Expected 7 shift slots, got {len(df)}"
    
    def test_dim_strength_exists(self):
        df = pd.read_csv(OUTPUT_DIR / "dim_strength.csv", dtype=str)
        assert len(df) >= 5, f"Expected at least 5 strength situations"
    
    def test_dim_event_type_from_data(self):
        df = pd.read_csv(OUTPUT_DIR / "dim_event_type.csv", dtype=str)
        assert len(df) > 0, "dim_event_type should have event types"


class TestNoUnderscoreColumns:
    """Verify no columns ending in _"""
    
    @pytest.fixture
    def all_tables(self):
        return [f.stem for f in OUTPUT_DIR.glob("*.csv")]
    
    def test_no_underscore_columns(self, all_tables):
        issues = []
        for table in all_tables:
            df = pd.read_csv(OUTPUT_DIR / f"{table}.csv", dtype=str, nrows=0)
            underscore_cols = [c for c in df.columns if c.endswith('_')]
            if underscore_cols:
                issues.append(f"{table}: {underscore_cols[:3]}")
        assert not issues, f"Tables with underscore columns: {issues}"


class TestWideVsLongRelationship:
    """Verify wide/long table relationships"""
    
    def test_events_long_references_events(self):
        events = pd.read_csv(OUTPUT_DIR / "fact_events.csv", dtype=str)
        events_long = pd.read_csv(OUTPUT_DIR / "fact_events_long.csv", dtype=str)
        
        event_ids = set(events['event_id'].unique())
        long_event_ids = set(events_long['event_id'].unique())
        
        missing = long_event_ids - event_ids
        assert not missing, f"fact_events_long has event_ids not in fact_events"
    
    def test_shifts_long_references_shifts(self):
        shifts = pd.read_csv(OUTPUT_DIR / "fact_shifts.csv", dtype=str)
        shifts_long = pd.read_csv(OUTPUT_DIR / "fact_shifts_long.csv", dtype=str)
        
        shift_ids = set(shifts['shift_id'].unique())
        long_shift_ids = set(shifts_long['shift_id'].unique())
        
        missing = long_shift_ids - shift_ids
        assert not missing, f"fact_shifts_long has shift_ids not in fact_shifts"
