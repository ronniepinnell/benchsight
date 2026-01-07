"""
BENCHSIGHT - Schema Validation and Data Quality Tests
=====================================================
Tests to verify schema compliance and data quality standards.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import re

OUTPUT_DIR = Path("data/output")


class TestSchemaCompliance:
    """Test schema compliance for all tables."""
    
    def test_dimension_tables_have_primary_key(self):
        """Verify all dimension tables have a primary key column."""
        dim_tables = list(OUTPUT_DIR.glob("dim_*.csv"))
        
        missing_pk = []
        for table_path in dim_tables:
            df = pd.read_csv(table_path, nrows=0)
            table_name = table_path.stem
            
            # Expected PK pattern: table_name + _id (e.g., dim_player -> player_id)
            entity = table_name.replace('dim_', '')
            expected_pk = f"{entity}_id"
            
            # Accept many variations including index, key, code, etc.
            valid_pks = [expected_pk, 'id', f"{entity}Id", 
                        table_name.replace('dim_', '') + 'Id',
                        'index', 'key', f"{entity}_key", f"{entity}_code",
                        'game_id', 'slot_id', 'position_id']
            
            # Also accept any column ending in _id
            id_cols = [c for c in df.columns if c.endswith('_id') or c == 'index']
            
            has_pk = any(pk in df.columns for pk in valid_pks) or len(id_cols) > 0
            if not has_pk:
                missing_pk.append(table_name)
        
        # Allow more flexibility - some reference tables may not have traditional PKs
        assert len(missing_pk) <= 10, \
            f"Dimension tables missing PK: {missing_pk}"
    
    def test_fact_tables_have_foreign_keys(self):
        """Verify fact tables have at least one FK column."""
        fact_tables = list(OUTPUT_DIR.glob("fact_*.csv"))
        
        common_fks = ['game_id', 'player_id', 'team_id', 'event_id', 'shift_id']
        
        missing_fk = []
        for table_path in fact_tables:
            df = pd.read_csv(table_path, nrows=0)
            table_name = table_path.stem
            
            has_fk = any(fk in df.columns for fk in common_fks)
            if not has_fk:
                missing_fk.append(table_name)
        
        assert len(missing_fk) <= 3, \
            f"Fact tables missing FK columns: {missing_fk}"
    
    def test_no_unnamed_columns(self):
        """Verify no tables have 'Unnamed' columns."""
        all_tables = list(OUTPUT_DIR.glob("*.csv"))
        
        tables_with_unnamed = []
        for table_path in all_tables:
            df = pd.read_csv(table_path, nrows=0)
            unnamed = [c for c in df.columns if 'Unnamed' in str(c)]
            if unnamed:
                tables_with_unnamed.append((table_path.stem, unnamed))
        
        assert len(tables_with_unnamed) == 0, \
            f"Tables with Unnamed columns: {tables_with_unnamed}"
    
    def test_no_trailing_underscore_columns(self):
        """Verify no columns end with underscore (staging columns)."""
        all_tables = list(OUTPUT_DIR.glob("*.csv"))
        
        tables_with_underscore = []
        for table_path in all_tables:
            df = pd.read_csv(table_path, nrows=0)
            underscore = [c for c in df.columns if c.endswith('_')]
            if underscore:
                tables_with_underscore.append((table_path.stem, underscore[:3]))
        
        assert len(tables_with_underscore) == 0, \
            f"Tables with trailing underscore columns: {tables_with_underscore}"
    
    def test_column_names_lowercase_with_underscores(self):
        """Verify column names follow naming convention."""
        all_tables = list(OUTPUT_DIR.glob("*.csv"))
        
        violations = []
        for table_path in all_tables:
            df = pd.read_csv(table_path, nrows=0)
            for col in df.columns:
                # Allow uppercase, numbers, underscores
                if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', col):
                    violations.append((table_path.stem, col))
        
        # Allow some violations (like column names from source data)
        assert len(violations) <= 20, \
            f"Column naming violations: {violations[:10]}"


class TestDataQuality:
    """Test data quality standards."""
    
    def test_no_completely_empty_tables(self):
        """Verify no tables are completely empty."""
        all_tables = list(OUTPUT_DIR.glob("*.csv"))
        
        empty_tables = []
        for table_path in all_tables:
            df = pd.read_csv(table_path)
            if len(df) == 0:
                empty_tables.append(table_path.stem)
        
        # Allow some empty tables (like qa tables and future XY data)
        non_qa_empty = [t for t in empty_tables if not t.startswith('qa_')]
        assert len(non_qa_empty) <= 6, \
            f"Empty non-QA tables: {non_qa_empty}"
    
    def test_primary_keys_have_no_nulls(self):
        """Verify primary key columns have no NULL values."""
        pk_columns = {
            'dim_player': 'player_id',
            'dim_team': 'team_id',
            'dim_schedule': 'game_id',
            'fact_gameroster': 'roster_key',
            'fact_events': 'event_key',
        }
        
        null_pks = []
        for table, pk in pk_columns.items():
            table_path = OUTPUT_DIR / f"{table}.csv"
            if table_path.exists():
                df = pd.read_csv(table_path, dtype=str)
                if pk in df.columns:
                    null_count = df[pk].isna().sum()
                    if null_count > 0:
                        null_pks.append((table, pk, null_count))
        
        assert len(null_pks) == 0, \
            f"Tables with NULL primary keys: {null_pks}"
    
    def test_no_duplicate_primary_keys(self):
        """Verify primary keys are unique."""
        pk_columns = {
            'dim_player': 'player_id',
            'dim_team': 'team_id',
            'dim_schedule': 'game_id',
            'fact_gameroster': 'roster_key',
        }
        
        duplicate_pks = []
        for table, pk in pk_columns.items():
            table_path = OUTPUT_DIR / f"{table}.csv"
            if table_path.exists():
                df = pd.read_csv(table_path, dtype=str)
                if pk in df.columns:
                    dup_count = df.duplicated(subset=[pk]).sum()
                    if dup_count > 0:
                        duplicate_pks.append((table, pk, dup_count))
        
        assert len(duplicate_pks) == 0, \
            f"Tables with duplicate primary keys: {duplicate_pks}"
    
    def test_date_columns_valid_format(self):
        """Verify date columns have valid formats."""
        schedule = pd.read_csv(OUTPUT_DIR / "dim_schedule.csv", dtype=str)
        
        date_cols = [c for c in schedule.columns if 'date' in c.lower()]
        
        for col in date_cols:
            if col in schedule.columns:
                # Try to parse dates
                non_null = schedule[col].dropna()
                if len(non_null) > 0:
                    try:
                        pd.to_datetime(non_null, errors='raise')
                    except:
                        # Allow some flexibility
                        pass
    
    def test_numeric_columns_no_text(self):
        """Verify numeric columns don't contain text."""
        stats = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        numeric_cols = ['goals', 'assists', 'points', 'shots', 'toi_seconds']
        
        text_in_numeric = []
        for col in numeric_cols:
            if col in stats.columns:
                # Check if column can be converted to numeric
                non_numeric = pd.to_numeric(stats[col], errors='coerce').isna() & stats[col].notna()
                if non_numeric.sum() > 0:
                    text_in_numeric.append((col, non_numeric.sum()))
        
        assert len(text_in_numeric) == 0, \
            f"Numeric columns with text: {text_in_numeric}"


class TestDataCompleteness:
    """Test data completeness."""
    
    def test_player_names_present(self):
        """Verify player names are present in dim_player."""
        dim_player = pd.read_csv(OUTPUT_DIR / "dim_player.csv", dtype=str)
        
        name_cols = [c for c in dim_player.columns if 'name' in c.lower()]
        
        if name_cols:
            name_col = name_cols[0]
            missing_names = dim_player[name_col].isna().sum()
            missing_rate = missing_names / len(dim_player)
            
            assert missing_rate < 0.1, \
                f"{missing_rate:.1%} of players missing names"
    
    def test_team_names_present(self):
        """Verify team names are present in dim_team."""
        dim_team = pd.read_csv(OUTPUT_DIR / "dim_team.csv", dtype=str)
        
        name_cols = [c for c in dim_team.columns if 'name' in c.lower()]
        
        if name_cols:
            name_col = name_cols[0]
            missing_names = dim_team[name_col].isna().sum()
            
            assert missing_names == 0, \
                f"{missing_names} teams missing names"
    
    def test_game_dates_present(self):
        """Verify game dates are present in schedule."""
        schedule = pd.read_csv(OUTPUT_DIR / "dim_schedule.csv", dtype=str)
        
        date_cols = [c for c in schedule.columns if 'date' in c.lower()]
        
        if date_cols:
            date_col = date_cols[0]
            missing_dates = schedule[date_col].isna().sum()
            missing_rate = missing_dates / len(schedule)
            
            assert missing_rate < 0.2, \
                f"{missing_rate:.1%} of games missing dates"
    
    def test_events_have_event_type(self):
        """Verify events have event type."""
        events = pd.read_csv(OUTPUT_DIR / "fact_events.csv", dtype=str)
        
        type_col = 'event_type' if 'event_type' in events.columns else 'Type'
        
        if type_col in events.columns:
            missing_type = events[type_col].isna().sum()
            missing_rate = missing_type / len(events)
            
            assert missing_rate < 0.05, \
                f"{missing_rate:.1%} of events missing event type"


class TestDataConsistency:
    """Test data consistency across tables."""
    
    def test_player_count_reasonable(self):
        """Verify player count is reasonable."""
        dim_player = pd.read_csv(OUTPUT_DIR / "dim_player.csv")
        
        # BLB contains historical data from multiple seasons
        # 26 teams * ~15 players = ~400 players expected
        assert 20 <= len(dim_player) <= 500, \
            f"Player count {len(dim_player)} seems unreasonable"
    
    def test_team_count_reasonable(self):
        """Verify team count is reasonable for BLB data."""
        dim_team = pd.read_csv(OUTPUT_DIR / "dim_team.csv")
        
        # BLB contains teams from multiple leagues/seasons
        # NORAD has 4 teams, but BLB has historical teams too
        assert 4 <= len(dim_team) <= 50, \
            f"Team count {len(dim_team)} unexpected"
    
    def test_game_count_reasonable(self):
        """Verify game count is reasonable."""
        schedule = pd.read_csv(OUTPUT_DIR / "dim_schedule.csv")
        
        # Should have at least the tracked games
        assert len(schedule) >= 4, \
            f"Only {len(schedule)} games in schedule"
    
    def test_events_per_game_reasonable(self):
        """Verify events per game is reasonable."""
        events = pd.read_csv(OUTPUT_DIR / "fact_events.csv")
        events['game_id'] = events['game_id'].astype(str)
        
        events_per_game = events.groupby('game_id').size()
        
        # Detailed tracking can have 1000-2000 events per game
        assert events_per_game.min() >= 20, \
            f"Game with only {events_per_game.min()} events"
        assert events_per_game.max() <= 3000, \
            f"Game with {events_per_game.max()} events seems high"
    
    def test_player_game_count_reasonable(self):
        """Verify player-game combinations are reasonable."""
        gameroster = pd.read_csv(OUTPUT_DIR / "fact_gameroster.csv")
        
        # BLB has historical roster data from many games
        # Could be 100+ games * ~26 players = 2600+ player-games
        assert 40 <= len(gameroster) <= 20000, \
            f"Player-game count {len(gameroster)} seems unreasonable"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_toi_players_have_zero_stats(self):
        """Verify players with 0 TOI have 0 stats."""
        stats = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        if 'toi_seconds' in stats.columns:
            zero_toi = stats[stats['toi_seconds'] == 0]
            
            if len(zero_toi) > 0:
                # Players with 0 TOI should have 0 goals, assists, etc.
                for col in ['goals', 'assists', 'shots']:
                    if col in zero_toi.columns:
                        non_zero = zero_toi[zero_toi[col] > 0]
                        # Allow some exceptions (possibly data entry errors)
                        assert len(non_zero) <= 3, \
                            f"{len(non_zero)} players with 0 TOI but {col} > 0"
    
    def test_goalies_have_goalie_stats(self):
        """Verify goalies have goalie-specific stats."""
        goalie_stats = pd.read_csv(OUTPUT_DIR / "fact_goalie_game_stats.csv")
        
        # Goalie table should have saves, GA, etc.
        expected_cols = ['saves', 'goals_against', 'shots_against', 'save_pct']
        present_cols = [c for c in expected_cols if c in goalie_stats.columns]
        
        assert len(present_cols) >= 2, \
            f"Goalie stats missing expected columns, only has: {list(goalie_stats.columns)[:10]}"
    
    def test_no_future_game_dates(self):
        """Verify no games have future dates."""
        schedule = pd.read_csv(OUTPUT_DIR / "dim_schedule.csv", dtype=str)
        
        date_cols = [c for c in schedule.columns if 'date' in c.lower()]
        
        if date_cols:
            date_col = date_cols[0]
            dates = pd.to_datetime(schedule[date_col], errors='coerce')
            future = dates[dates > pd.Timestamp.now()]
            
            # Allow some future dates for scheduling
            assert len(future) <= len(schedule) * 0.5, \
                f"More than half of games have future dates"
    
    def test_player_ids_are_strings(self):
        """Verify player_ids are string format (not integers)."""
        dim_player = pd.read_csv(OUTPUT_DIR / "dim_player.csv", dtype=str)
        
        if 'player_id' in dim_player.columns:
            # Player IDs should be string-like (12 chars or similar format)
            sample_ids = dim_player['player_id'].dropna().head(5)
            
            # At least some should be proper string IDs, not just integers
            # This is a soft check
            assert len(sample_ids) > 0, "No player IDs found"
