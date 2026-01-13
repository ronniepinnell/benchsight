"""
=============================================================================
INTEGRATION TESTS - Full Pipeline Verification
=============================================================================
File: tests/test_integration.py
Version: 19.10
Created: January 9, 2026

These tests verify the ENTIRE ETL pipeline works correctly.
Run after a fresh ETL to ensure everything is working.

Usage:
    pytest tests/test_integration.py -v
    pytest tests/test_integration.py -v --tb=short  # Shorter output
=============================================================================
"""

import pytest
import pandas as pd
import json
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'data' / 'output'
CONFIG_DIR = BASE_DIR / 'config'


class TestGoalAccuracy:
    """Goal counting is the most critical metric - it MUST be correct."""
    
    def test_total_goals_match_immutable(self):
        """Total goal count must match IMMUTABLE_FACTS."""
        immutable_path = CONFIG_DIR / 'IMMUTABLE_FACTS.json'
        assert immutable_path.exists(), "IMMUTABLE_FACTS.json not found"
        
        with open(immutable_path) as f:
            immutable = json.load(f)
        
        events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv', low_memory=False)
        goals = events[(events['event_type'] == 'Goal') & (events['event_detail'] == 'Goal_Scored')]
        
        expected = immutable.get('total_goals', 17)
        actual = len(goals)
        
        assert actual == expected, f"Goal count mismatch: expected {expected}, got {actual}"
    
    def test_per_game_goals_match_immutable(self):
        """Per-game goal counts must match IMMUTABLE_FACTS."""
        with open(CONFIG_DIR / 'IMMUTABLE_FACTS.json') as f:
            immutable = json.load(f)
        
        events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv', low_memory=False)
        goals = events[(events['event_type'] == 'Goal') & (events['event_detail'] == 'Goal_Scored')]
        
        for game_id, game_info in immutable.get('games', {}).items():
            expected = game_info.get('goals', 0) if isinstance(game_info, dict) else game_info
            actual = len(goals[goals['game_id'] == int(game_id)])
            assert actual == expected, f"Game {game_id}: expected {expected} goals, got {actual}"


class TestTableExistence:
    """All critical tables must exist with data."""
    
    @pytest.mark.parametrize("table_name", [
        'fact_events',
        'fact_event_players',
        'fact_shifts',
        'fact_shift_players',
        'fact_player_game_stats',
        'fact_gameroster',
        'dim_player',
        'dim_team',
        'dim_schedule',
    ])
    def test_critical_table_exists(self, table_name):
        """Critical tables must exist and have data."""
        path = OUTPUT_DIR / f'{table_name}.csv'
        assert path.exists(), f"{table_name} does not exist"
        
        df = pd.read_csv(path, low_memory=False)
        assert len(df) > 0, f"{table_name} is empty"
    
    def test_table_count(self):
        """Should have at least 120 tables."""
        tables = list(OUTPUT_DIR.glob('*.csv'))
        assert len(tables) >= 120, f"Only {len(tables)} tables found, expected 120+"


class TestFactEventPlayers:
    """fact_event_players is the main event-player table - verify key columns."""
    
    @pytest.fixture
    def df(self):
        return pd.read_csv(OUTPUT_DIR / 'fact_event_players.csv', low_memory=False)
    
    def test_has_required_columns(self, df):
        """Must have all required columns."""
        required = ['event_id', 'player_id', 'game_id', 'player_role', 'event_type']
        for col in required:
            assert col in df.columns, f"Missing required column: {col}"
    
    def test_has_rating_columns(self, df):
        """Must have rating columns from Phase 8."""
        rating_cols = ['player_rating', 'event_team_avg_rating', 'opp_team_avg_rating', 'rating_vs_opp']
        for col in rating_cols:
            assert col in df.columns, f"Missing rating column: {col}"
    
    def test_has_toi_columns(self, df):
        """Must have TOI columns from Phase 8."""
        assert 'player_toi' in df.columns, "Missing player_toi column"
    
    def test_rating_fill_rate(self, df):
        """Rating columns should have >90% fill rate."""
        for col in ['player_rating', 'event_team_avg_rating']:
            fill_rate = df[col].notna().sum() / len(df)
            assert fill_rate > 0.90, f"{col} fill rate too low: {fill_rate:.1%}"
    
    def test_no_duplicate_columns(self, df):
        """Should not have duplicate column names."""
        dupes = [c for c in df.columns if df.columns.tolist().count(c) > 1]
        assert len(dupes) == 0, f"Duplicate columns: {set(dupes)}"


class TestFactShiftPlayers:
    """fact_shift_players is the expanded shift table - verify it has 80+ columns."""
    
    @pytest.fixture
    def df(self):
        return pd.read_csv(OUTPUT_DIR / 'fact_shift_players.csv', low_memory=False)
    
    def test_has_expanded_columns(self, df):
        """Must have 80+ columns (v19.00 ROOT CAUSE FIX)."""
        assert len(df.columns) >= 80, f"Only {len(df.columns)} columns, expected 80+"
    
    def test_has_rating_columns(self, df):
        """Must have player rating columns."""
        rating_cols = ['player_rating', 'team_avg_rating', 'opp_avg_rating']
        for col in rating_cols:
            assert col in df.columns, f"Missing: {col}"
    
    def test_has_toi_columns(self, df):
        """Must have TOI tracking columns."""
        toi_cols = ['running_toi_game', 'logical_shift_number']
        for col in toi_cols:
            assert col in df.columns, f"Missing: {col}"
    
    def test_rating_fill_rate(self, df):
        """Rating columns should have >95% fill rate."""
        fill_rate = df['player_rating'].notna().sum() / len(df)
        assert fill_rate > 0.95, f"player_rating fill rate too low: {fill_rate:.1%}"


class TestForeignKeyIntegrity:
    """Foreign key relationships must be valid."""
    
    def test_player_ids_valid(self):
        """All player_ids in fact tables must exist in dim_player."""
        dim_player = pd.read_csv(OUTPUT_DIR / 'dim_player.csv')
        valid_players = set(dim_player['player_id'].unique())
        
        for table_name in ['fact_event_players', 'fact_shift_players', 'fact_player_game_stats']:
            df = pd.read_csv(OUTPUT_DIR / f'{table_name}.csv', low_memory=False)
            if 'player_id' not in df.columns:
                continue
            
            orphans = set(df['player_id'].dropna().unique()) - valid_players
            assert len(orphans) == 0, f"{table_name} has orphan player_ids: {list(orphans)[:5]}"
    
    def test_game_ids_valid(self):
        """All game_ids in fact tables must exist in dim_schedule."""
        schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
        valid_games = set(schedule['game_id'].astype(int).unique())
        
        for table_name in ['fact_events', 'fact_shifts']:
            df = pd.read_csv(OUTPUT_DIR / f'{table_name}.csv', low_memory=False)
            if 'game_id' not in df.columns:
                continue
            
            orphans = set(df['game_id'].dropna().astype(int).unique()) - valid_games
            assert len(orphans) == 0, f"{table_name} has orphan game_ids: {orphans}"


class TestPreviouslyEmptyTables:
    """Tables that were empty in v19.06 should now have data."""
    
    def test_fact_player_qoc_summary_has_data(self):
        """fact_player_qoc_summary should have 105 rows."""
        df = pd.read_csv(OUTPUT_DIR / 'fact_player_qoc_summary.csv')
        assert len(df) >= 100, f"fact_player_qoc_summary only has {len(df)} rows"
    
    def test_lookup_player_game_rating_has_data(self):
        """lookup_player_game_rating should have 105 rows."""
        df = pd.read_csv(OUTPUT_DIR / 'lookup_player_game_rating.csv')
        assert len(df) >= 100, f"lookup_player_game_rating only has {len(df)} rows"


class TestDataConsistency:
    """Cross-table data consistency checks."""
    
    def test_every_event_has_players(self):
        """Every event should have at least one player."""
        events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv', low_memory=False)
        event_players = pd.read_csv(OUTPUT_DIR / 'fact_event_players.csv', low_memory=False)
        
        events_with_players = set(event_players['event_id'].unique())
        events_without = set(events['event_id'].unique()) - events_with_players
        
        # Allow up to 10% without players (some events like period start may not have players)
        pct_without = len(events_without) / len(events)
        assert pct_without < 0.10, f"{pct_without:.1%} of events have no players"
    
    def test_shift_player_counts(self):
        """Each shift should have 2-14 players."""
        shift_players = pd.read_csv(OUTPUT_DIR / 'fact_shift_players.csv', low_memory=False)
        
        counts = shift_players.groupby(['game_id', 'shift_index']).size()
        
        assert counts.min() >= 2, f"Some shifts have only {counts.min()} players"
        assert counts.max() <= 14, f"Some shifts have {counts.max()} players (max should be 14)"


class TestKeyParsing:
    """Test that key parsing utilities work correctly."""
    
    def test_parse_shift_key(self):
        """parse_shift_key should correctly parse shift keys."""
        from src.utils.key_parser import parse_shift_key
        
        result = parse_shift_key("SH1896900001")
        assert result is not None
        assert result.game_id == 18969
        assert result.shift_index == 1
        
        # Invalid keys should return None
        assert parse_shift_key("") is None
        assert parse_shift_key("INVALID") is None
        assert parse_shift_key(None) is None
    
    def test_make_shift_key(self):
        """make_shift_key should create valid shift keys."""
        from src.utils.key_parser import make_shift_key
        
        key = make_shift_key(18969, 1)
        assert key == "SH1896900001"


class TestNoRegressions:
    """Ensure we haven't broken anything from previous versions."""
    
    def test_fact_shifts_has_rating_columns(self):
        """fact_shifts should have team rating columns (v19.00 ROOT CAUSE FIX)."""
        shifts = pd.read_csv(OUTPUT_DIR / 'fact_shifts.csv', low_memory=False)
        
        for col in ['home_avg_rating', 'away_avg_rating', 'rating_differential']:
            assert col in shifts.columns, f"Missing v19.00 column: {col}"
    
    def test_empty_tables_are_xy_placeholders(self):
        """Only XY placeholder tables should be empty."""
        allowed_empty = {
            'fact_player_xy_long', 'fact_player_xy_wide',
            'fact_puck_xy_long', 'fact_puck_xy_wide',
            'fact_shot_xy', 'fact_video'
        }
        
        empty_tables = []
        for f in OUTPUT_DIR.glob('*.csv'):
            df = pd.read_csv(f)
            if len(df) == 0:
                empty_tables.append(f.stem)
        
        unexpected_empty = set(empty_tables) - allowed_empty
        assert len(unexpected_empty) == 0, f"Unexpected empty tables: {unexpected_empty}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
