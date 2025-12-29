"""
Schema Compliance Tests
=======================
Validates that CSVs match Supabase schema before upload.

Run: pytest tests/test_schema_compliance.py -v
"""

import pytest
import pandas as pd
from pathlib import Path


class TestSchemaFileValidity:
    """Verify schema file is valid and complete."""
    
    def test_schema_file_exists(self, base_dir):
        """Schema file must exist."""
        schema_file = base_dir / "config" / "supabase_schema.json"
        assert schema_file.exists(), f"Missing: {schema_file}"
    
    def test_schema_has_tables(self, schema):
        """Schema must define tables."""
        assert len(schema) >= 40, f"Only {len(schema)} tables (expected 40+)"
    
    def test_schema_tables_have_columns(self, schema):
        """Each table must have columns defined."""
        empty_tables = [t for t, cols in schema.items() if not cols]
        assert not empty_tables, f"Tables without columns: {empty_tables}"
    
    @pytest.mark.parametrize("table", [
        "dim_player", "dim_team", "dim_schedule", "dim_league",
        "fact_gameroster", "fact_events_tracking"
    ])
    def test_core_tables_in_schema(self, schema, table):
        """Core tables must exist in schema."""
        assert table in schema, f"Core table missing: {table}"


class TestColumnCompliance:
    """Verify CSV columns match schema."""
    
    def test_no_extra_columns_in_csvs(self, schema, output_csvs):
        """CSVs must not have columns outside schema."""
        errors = []
        
        for csv_path in output_csvs:
            table = csv_path.stem
            if table not in schema:
                continue
            
            df = pd.read_csv(csv_path, nrows=0, dtype=str)
            extra = set(df.columns) - set(schema[table])
            
            if extra:
                errors.append(f"{table}: {sorted(extra)}")
        
        assert not errors, f"Extra columns found:\n" + "\n".join(errors)
    
    def test_no_metadata_columns(self, output_csvs):
        """No CSV should have metadata columns."""
        forbidden = {"_export_timestamp", "_source_file", "Unnamed: 0", "index", "level_0"}
        errors = []
        
        for csv_path in output_csvs:
            df = pd.read_csv(csv_path, nrows=0, dtype=str)
            found = set(df.columns) & forbidden
            if found:
                errors.append(f"{csv_path.stem}: {found}")
        
        assert not errors, f"Metadata columns found:\n" + "\n".join(errors)
    
    def test_no_underscore_prefix_columns(self, output_csvs):
        """No CSV should have columns starting with underscore."""
        errors = []
        
        for csv_path in output_csvs:
            df = pd.read_csv(csv_path, nrows=0, dtype=str)
            underscore = [c for c in df.columns if c.startswith("_")]
            if underscore:
                errors.append(f"{csv_path.stem}: {underscore}")
        
        assert not errors, f"Underscore columns found:\n" + "\n".join(errors)


class TestDataIntegrity:
    """Verify data structure integrity."""
    
    def test_events_tracking_has_game_id(self, base_dir):
        """fact_events_tracking should have valid game_ids."""
        csv_path = base_dir / "data" / "output" / "fact_events_tracking.csv"
        if not csv_path.exists():
            pytest.skip("fact_events_tracking.csv not found")
        
        df = pd.read_csv(csv_path, dtype=str)
        null_game = df['game_id'].isna().sum()
        assert null_game == 0, f"{null_game} rows have NULL game_id"
    
    def test_events_long_has_player_column(self, base_dir):
        """fact_events_long should have player_number."""
        csv_path = base_dir / "data" / "output" / "fact_events_long.csv"
        if not csv_path.exists():
            pytest.skip("fact_events_long.csv not found")
        
        df = pd.read_csv(csv_path, nrows=0, dtype=str)
        assert "player_number" in df.columns
    
    def test_events_has_fewer_rows_than_long(self, base_dir):
        """fact_events (unique events) should have fewer rows than fact_events_long (per player)."""
        events = base_dir / "data" / "output" / "fact_events.csv"
        long = base_dir / "data" / "output" / "fact_events_long.csv"
        
        if not events.exists() or not long.exists():
            pytest.skip("Events files not found")
        
        e_rows = len(pd.read_csv(events))
        l_rows = len(pd.read_csv(long))
        
        assert e_rows <= l_rows, f"events ({e_rows}) > long ({l_rows})"


class TestCoreDataExists:
    """Verify core data files exist and have content."""
    
    @pytest.mark.parametrize("table", [
        "dim_league", "dim_season", "dim_team", "dim_player",
        "dim_schedule", "fact_gameroster"
    ])
    def test_core_csv_exists(self, base_dir, table):
        """Core CSVs must exist."""
        csv_path = base_dir / "data" / "output" / f"{table}.csv"
        assert csv_path.exists(), f"Missing: {table}.csv"
    
    @pytest.mark.parametrize("table", [
        "dim_league", "dim_team", "dim_player", "dim_schedule"
    ])
    def test_core_csv_not_empty(self, base_dir, table):
        """Core CSVs must have data."""
        csv_path = base_dir / "data" / "output" / f"{table}.csv"
        if not csv_path.exists():
            pytest.skip(f"{table}.csv not found")
        
        df = pd.read_csv(csv_path)
        assert len(df) > 0, f"{table}.csv is empty"


class TestSpecificTables:
    """Table-specific validation tests."""
    
    def test_gameroster_has_assist_singular(self, base_dir):
        """fact_gameroster should have 'assist' not 'assists'."""
        csv_path = base_dir / "data" / "output" / "fact_gameroster.csv"
        if not csv_path.exists():
            pytest.skip("fact_gameroster.csv not found")
        
        df = pd.read_csv(csv_path, nrows=0, dtype=str)
        assert "assist" in df.columns, "Missing 'assist' column"
        assert "assists" not in df.columns, "Has 'assists' instead of 'assist'"
    
    def test_events_tracking_has_type_capital(self, base_dir):
        """fact_events_tracking should have 'Type' (capital T)."""
        csv_path = base_dir / "data" / "output" / "fact_events_tracking.csv"
        if not csv_path.exists():
            pytest.skip("fact_events_tracking.csv not found")
        
        df = pd.read_csv(csv_path, nrows=0, dtype=str)
        assert "Type" in df.columns, "Missing 'Type' column"
        assert "event_type" not in df.columns, "Has 'event_type' instead of 'Type'"
    
    def test_playergames_has_original_columns(self, base_dir):
        """fact_playergames should have original Excel column names."""
        csv_path = base_dir / "data" / "output" / "fact_playergames.csv"
        if not csv_path.exists():
            pytest.skip("fact_playergames.csv not found")
        
        df = pd.read_csv(csv_path, nrows=0, dtype=str)
        expected = ["ID", "Date", "Type", "Team", "G", "A", "Season"]
        
        for col in expected:
            assert col in df.columns, f"Missing column: {col}"


class TestUploadReadiness:
    """Final validation before upload."""
    
    def test_all_csvs_uploadable(self, schema, output_csvs):
        """All schema-matched CSVs should be uploadable."""
        errors = []
        
        for csv_path in output_csvs:
            table = csv_path.stem
            if table not in schema:
                continue
            
            try:
                df = pd.read_csv(csv_path, dtype=str, nrows=10)
                extra = set(df.columns) - set(schema[table])
                
                if extra:
                    errors.append(f"{table}: extra columns {extra}")
                    
            except Exception as e:
                errors.append(f"{table}: {str(e)[:50]}")
        
        assert not errors, f"Upload errors:\n" + "\n".join(errors)
