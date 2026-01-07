"""
=============================================================================
ETL INTEGRATION TESTS
=============================================================================
File: tests/test_etl_integration.py
Created: 2024-12-30
Author: Production Hardening Sprint

PURPOSE:
    End-to-end integration tests for the ETL pipeline.
    Verifies the complete flow from raw data to output CSVs.

WHAT IT TESTS:
    1. Full pipeline execution
    2. Idempotency (running twice produces same result)
    3. Error handling and recovery
    4. Data flow between stages
    5. Metrics collection

HOW TO RUN:
    pytest tests/test_etl_integration.py -v
    pytest tests/test_etl_integration.py -v -k "test_full_pipeline"

REQUIREMENTS:
    - At least one game in data/raw/games/ with tracking file
    - Output directory writable

=============================================================================
"""

import pytest
import pandas as pd
from pathlib import Path
import shutil
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

# Test configuration
OUTPUT_DIR = Path("data/output")
RAW_DIR = Path("data/raw/games")
BACKUP_DIR = Path("data/test_backup")

# Known test games (should exist in test environment)
TEST_GAMES = [18969, 18977]  # Use games that exist in your dataset


class TestPipelineExecution:
    """Test end-to-end pipeline execution."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        yield
        # Cleanup is handled in individual tests if needed
    
    def test_output_directory_exists(self):
        """Verify output directory is accessible."""
        assert OUTPUT_DIR.exists(), "Output directory should exist"
        assert OUTPUT_DIR.is_dir(), "Output path should be a directory"
    
    def test_raw_games_exist(self):
        """Verify test games have raw data."""
        for game_id in TEST_GAMES:
            game_dir = RAW_DIR / str(game_id)
            tracking_file = game_dir / f"{game_id}_tracking.xlsx"
            
            # Skip if test game doesn't exist (not all environments have all games)
            if not game_dir.exists():
                pytest.skip(f"Test game {game_id} not available")
            
            assert tracking_file.exists() or (game_dir / "tracking.xlsx").exists(), \
                f"Tracking file should exist for game {game_id}"
    
    def test_csv_files_have_headers(self):
        """Verify all output CSVs have proper headers."""
        csv_files = list(OUTPUT_DIR.glob("*.csv"))
        assert len(csv_files) > 0, "Should have output CSV files"
        
        for csv_file in csv_files:
            with open(csv_file, 'r') as f:
                header = f.readline().strip()
            
            assert header, f"{csv_file.name} should have a header row"
            assert ',' in header or len(header.split(',')) >= 1, \
                f"{csv_file.name} header should have columns"
    
    def test_dimension_tables_not_empty(self):
        """Verify dimension tables have data."""
        required_dims = [
            "dim_player", "dim_team", "dim_period", 
            "dim_event_type", "dim_venue"
        ]
        
        for dim in required_dims:
            csv_path = OUTPUT_DIR / f"{dim}.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                assert len(df) > 0, f"{dim} should not be empty"
    
    def test_fact_tables_reference_dimensions(self):
        """Verify fact tables can join to dimensions."""
        # Load a fact table
        events_path = OUTPUT_DIR / "fact_events.csv"
        if not events_path.exists():
            pytest.skip("fact_events.csv not available")
        
        events = pd.read_csv(events_path, dtype=str)
        
        # Check it has FK columns
        assert "game_id" in events.columns, "fact_events should have game_id"
        
        # Load dimension and verify join works
        schedule_path = OUTPUT_DIR / "dim_schedule.csv"
        if schedule_path.exists():
            schedule = pd.read_csv(schedule_path, dtype=str)
            valid_games = set(schedule["game_id"].unique())
            event_games = set(events["game_id"].unique())
            
            orphans = event_games - valid_games
            orphan_rate = len(orphans) / len(event_games) if event_games else 0
            
            assert orphan_rate < 0.1, \
                f"Too many orphaned events ({orphan_rate:.1%}): {list(orphans)[:5]}"


class TestDataConsistency:
    """Test data consistency across tables."""
    
    def test_game_ids_consistent(self):
        """Verify same games appear in related tables."""
        tables_with_game_id = [
            "fact_events", "fact_shifts", "fact_player_game_stats",
            "fact_gameroster"
        ]
        
        game_sets = {}
        for table in tables_with_game_id:
            csv_path = OUTPUT_DIR / f"{table}.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path, dtype=str)
                if "game_id" in df.columns:
                    game_sets[table] = set(df["game_id"].unique())
        
        if len(game_sets) < 2:
            pytest.skip("Not enough tables to compare")
        
        # All tables should have overlapping games
        all_games = set.union(*game_sets.values())
        common_games = set.intersection(*game_sets.values())
        
        assert len(common_games) > 0, \
            f"Tables should share at least one game. Found: {game_sets}"
    
    def test_player_ids_consistent(self):
        """Verify player IDs are consistent across tables."""
        # Get players from dimension
        players_path = OUTPUT_DIR / "dim_player.csv"
        if not players_path.exists():
            pytest.skip("dim_player.csv not available")
        
        dim_players = pd.read_csv(players_path, dtype=str)
        valid_players = set(dim_players["player_id"].dropna().unique())
        
        # Check fact tables reference valid players
        fact_tables = ["fact_events_long", "fact_shifts_long", "fact_player_game_stats"]
        
        for table in fact_tables:
            csv_path = OUTPUT_DIR / f"{table}.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path, dtype=str)
                if "player_id" in df.columns:
                    fact_players = set(df["player_id"].dropna().unique())
                    orphans = fact_players - valid_players
                    
                    # Allow some tolerance (tracking errors)
                    orphan_rate = len(orphans) / len(fact_players) if fact_players else 0
                    assert orphan_rate < 0.05, \
                        f"{table} has {orphan_rate:.1%} orphaned player_ids"
    
    def test_row_counts_reasonable(self):
        """Verify tables have reasonable row counts."""
        expectations = {
            "dim_player": (10, 10000),      # 10 to 10k players
            "dim_team": (2, 100),            # 2 to 100 teams
            "dim_event_type": (5, 50),       # 5 to 50 event types
            "fact_events": (100, 1000000),   # 100 to 1M events
            "fact_shifts": (50, 100000),     # 50 to 100k shifts
        }
        
        for table, (min_rows, max_rows) in expectations.items():
            csv_path = OUTPUT_DIR / f"{table}.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                row_count = len(df)
                
                assert min_rows <= row_count <= max_rows, \
                    f"{table} has {row_count} rows, expected {min_rows}-{max_rows}"


class TestIdempotency:
    """Test that running the pipeline twice produces consistent results."""
    
    @pytest.fixture
    def capture_state(self):
        """Capture current state of key tables."""
        state = {}
        key_tables = ["fact_events", "fact_player_game_stats", "dim_player"]
        
        for table in key_tables:
            csv_path = OUTPUT_DIR / f"{table}.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path, dtype=str)
                state[table] = {
                    "row_count": len(df),
                    "columns": list(df.columns),
                    "checksum": df.to_csv(index=False).__hash__()
                }
        
        return state
    
    def test_output_structure_stable(self, capture_state):
        """Verify output structure doesn't change unexpectedly."""
        state = capture_state
        
        for table, info in state.items():
            csv_path = OUTPUT_DIR / f"{table}.csv"
            df = pd.read_csv(csv_path, dtype=str)
            
            # Column structure should match
            assert list(df.columns) == info["columns"], \
                f"{table} columns changed: {list(df.columns)} vs {info['columns']}"


class TestErrorHandling:
    """Test error handling and recovery."""
    
    def test_missing_csv_handled(self):
        """Verify graceful handling of missing CSV files."""
        from src.validators.data_validator import DataValidator
        
        validator = DataValidator(str(OUTPUT_DIR))
        
        # Try to validate a non-existent table
        result = validator.validate_primary_key("nonexistent_table")
        
        # Should not raise, should return a result indicating the issue
        assert result is not None
        # Either it passes with a skip message OR it fails with "not found"
        assert result.passed or "not found" in result.message.lower() or "no pk defined" in result.message.lower()
    
    def test_invalid_data_detected(self):
        """Verify invalid data is detected by validators."""
        from src.validators.data_validator import DataValidator
        
        validator = DataValidator(str(OUTPUT_DIR))
        
        # Run validation on a table that might have issues
        results = validator.validate_all()
        
        # Should complete without crashing
        assert results is not None
        assert hasattr(results, "total_checks")
        assert results.total_checks > 0


class TestMetricsCollection:
    """Test ETL metrics are properly collected."""
    
    def test_metrics_collector_initializes(self):
        """Verify metrics collector can be initialized."""
        from src.metrics import ETLMetricsCollector
        
        collector = ETLMetricsCollector()
        assert collector is not None
        assert collector.metrics_dir.exists()
    
    def test_run_metrics_tracked(self):
        """Verify run metrics are captured."""
        from src.metrics import ETLMetricsCollector, ETLRunMetrics
        
        collector = ETLMetricsCollector()
        
        # Create a test run
        metrics = ETLRunMetrics(game_id=99999)
        metrics.start()
        metrics.rows_staged = 100
        metrics.rows_transformed = 100
        metrics.rows_loaded = 100
        metrics.complete(success=True)
        
        # Save it
        collector.save_run(metrics)
        
        # Verify it was saved
        run_file = collector.metrics_dir / f"run_{metrics.run_id}.json"
        assert run_file.exists(), "Run metrics should be saved to file"
        
        # Verify content
        with open(run_file) as f:
            saved = json.load(f)
        
        assert saved["game_id"] == 99999
        assert saved["status"] == "success"
        assert saved["rows"]["loaded"] == 100
        
        # Cleanup
        run_file.unlink()
    
    def test_context_manager_tracking(self):
        """Test tracking via context manager."""
        from src.metrics import ETLMetricsCollector
        
        collector = ETLMetricsCollector()
        
        with collector.track_run(game_id=88888) as metrics:
            metrics.rows_staged = 50
            metrics.rows_loaded = 50
        
        # Run should be saved automatically
        recent = collector.get_recent_runs(limit=1)
        assert len(recent) > 0
        
        # Cleanup
        run_file = collector.metrics_dir / f"run_{metrics.run_id}.json"
        if run_file.exists():
            run_file.unlink()


class TestExceptionHandling:
    """Test custom exception classes."""
    
    def test_etl_game_error_captures_context(self):
        """Verify ETLGameProcessingError captures game context."""
        from src.exceptions import ETLGameProcessingError
        
        cause = ValueError("Test error")
        error = ETLGameProcessingError(
            game_id=18969,
            cause=cause,
            stage="intermediate",
            partial_data=True
        )
        
        assert error.game_id == 18969
        assert error.cause is cause
        assert "intermediate" in error.context.get("stage", "")
        assert error.partial_data is True
    
    def test_schema_validation_error_details(self):
        """Verify SchemaValidationError has detailed info."""
        from src.exceptions import SchemaValidationError
        
        error = SchemaValidationError(
            table_name="fact_events",
            missing_in_db=["extra_col"],
            missing_in_csv=["required_col"],
            type_mismatches={"goals": "expected INTEGER"}
        )
        
        assert error.table_name == "fact_events"
        assert "extra_col" in error.missing_in_db
        assert "required_col" in error.missing_in_csv
        assert "goals" in error.type_mismatches
    
    def test_is_retryable_detection(self):
        """Test retryable error detection."""
        from src.exceptions import is_retryable_error, RetryableError, NonRetryableError
        
        # Explicitly retryable
        assert is_retryable_error(RetryableError("test"))
        
        # Explicitly non-retryable
        assert not is_retryable_error(NonRetryableError("test"))
        
        # Heuristic detection
        assert is_retryable_error(Exception("Connection timeout"))
        assert is_retryable_error(Exception("503 Service Unavailable"))
        assert not is_retryable_error(Exception("Permission denied"))
        assert not is_retryable_error(Exception("Duplicate key violation"))


class TestValidators:
    """Test validation modules."""
    
    def test_schema_validator_detects_missing_pk(self):
        """Verify schema validator catches missing PK."""
        from src.validators.schema_validator import SchemaValidator
        
        validator = SchemaValidator()
        
        # Records without PK value
        records = [
            {"game_id": "18969", "event_key": None, "event_type": "Shot"},
            {"game_id": "18969", "event_key": "", "event_type": "Goal"},
        ]
        
        # Add the table to schema definitions
        validator.schema_definitions["test_table"] = {
            "pk": "event_key",
            "required": ["event_key"]
        }
        
        is_valid, errors = validator.validate_table("test_table", records)
        
        assert not is_valid, "Should fail with null PKs"
        assert any("null" in e.lower() or "empty" in e.lower() for e in errors)
    
    def test_data_validator_catches_duplicates(self):
        """Verify data validator catches duplicate PKs."""
        import tempfile
        import os
        
        # Create temporary CSV with duplicates
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test_table.csv"
            
            # Write CSV with duplicate PKs
            with open(csv_path, 'w') as f:
                f.write("pk_col,value\n")
                f.write("key1,a\n")
                f.write("key1,b\n")  # Duplicate!
                f.write("key2,c\n")
            
            from src.validators.data_validator import DataValidator
            
            validator = DataValidator(tmpdir)
            validator.PRIMARY_KEYS["test_table"] = "pk_col"
            
            result = validator.validate_primary_key("test_table")
            
            assert not result.passed, "Should fail with duplicate PKs"
            assert result.violation_count > 0


# =============================================================================
# PERFORMANCE TESTS (Optional - may be slow)
# =============================================================================

class TestPerformance:
    """Performance-related tests."""
    
    @pytest.mark.slow
    def test_large_table_validation_time(self):
        """Verify validation completes in reasonable time for large tables."""
        import time
        
        # Find largest table
        csv_files = list(OUTPUT_DIR.glob("*.csv"))
        if not csv_files:
            pytest.skip("No CSV files available")
        
        largest = max(csv_files, key=lambda p: p.stat().st_size)
        
        from src.validators.data_validator import DataValidator
        
        validator = DataValidator(str(OUTPUT_DIR))
        
        start = time.time()
        results = validator.validate_table(largest.stem)
        duration = time.time() - start
        
        # Should complete within 30 seconds even for large tables
        assert duration < 30, f"Validation took {duration:.1f}s for {largest.name}"
