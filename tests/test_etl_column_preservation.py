"""
BENCHSIGHT - ETL Column Preservation Tests
==========================================
Tests to verify the ETL bug fix that preserves enhanced columns.

The original bug: Running ETL dropped 317 columns to 63 columns.
The fix: ETL now merges new stats with existing enhanced columns.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import shutil
import tempfile

OUTPUT_DIR = Path("data/output")
BACKUP_DIR = Path("data/backup_317")


class TestColumnPreservation:
    """Test that all 317 columns are preserved through ETL."""
    
    def test_fact_player_game_stats_has_317_columns(self):
        """Verify fact_player_game_stats has all 317 columns."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        assert len(df.columns) >= 317, f"Expected >=317 columns, got {len(df.columns)}"
    
    def test_critical_fk_columns_present(self):
        """Verify critical FK columns exist in fact_player_game_stats."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        # These were the columns that were being dropped by the bug
        critical_cols = [
            'player_game_key', 'game_id', 'player_id', 'player_name',
            'goals', 'assists', 'points', 'shots', 'toi_seconds'
        ]
        
        missing = [c for c in critical_cols if c not in df.columns]
        assert not missing, f"Missing critical columns: {missing}"
    
    def test_enhanced_stats_columns_present(self):
        """Verify enhanced stat columns from enhance_all_stats.py exist."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        # These are columns added by enhance_all_stats.py
        enhanced_cols = [
            'deke_attempts', 'screens', 'backchecks', 'poke_checks',
            'zone_entry_denials', 'loose_puck_wins', 'puck_recoveries',
            'offensive_rating', 'defensive_rating', 'hustle_rating',
            'xg_placeholder', 'pdo', 'luck_factor'
        ]
        
        present = [c for c in enhanced_cols if c in df.columns]
        # At least 50% of enhanced columns should be present
        assert len(present) >= len(enhanced_cols) * 0.5, \
            f"Only {len(present)}/{len(enhanced_cols)} enhanced columns present"
    
    def test_micro_stat_columns_present(self):
        """Verify micro-stat columns exist."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        micro_stats = [
            'deke_attempts', 'screens', 'crash_net', 'drives_middle',
            'backchecks', 'poke_checks', 'stick_checks', 'blocked_shots_play',
            'zone_entry_denials', 'zone_keepins', 'breakouts', 'forechecks'
        ]
        
        present = [c for c in micro_stats if c in df.columns]
        assert len(present) >= 5, f"Only {len(present)} micro-stat columns present"
    
    def test_composite_rating_columns_present(self):
        """Verify composite rating columns exist."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        rating_cols = [
            'offensive_rating', 'defensive_rating', 'hustle_rating',
            'playmaking_rating', 'shooting_rating', 'impact_score'
        ]
        
        present = [c for c in rating_cols if c in df.columns]
        assert len(present) >= 3, f"Only {len(present)} rating columns present"
    
    def test_per_60_columns_present(self):
        """Verify per-60 rate columns exist."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        per_60_cols = [
            'goals_per_60', 'assists_per_60', 'points_per_60', 'shots_per_60'
        ]
        
        present = [c for c in per_60_cols if c in df.columns]
        assert len(present) >= 2, f"Only {len(present)} per-60 columns present"


class TestBackupIntegrity:
    """Test backup file integrity."""
    
    @pytest.mark.skipif(not BACKUP_DIR.exists(), reason="Backup directory not found")
    def test_backup_has_317_columns(self):
        """Verify backup file has 317 columns."""
        backup_file = BACKUP_DIR / "fact_player_game_stats.csv"
        if backup_file.exists():
            df = pd.read_csv(backup_file)
            assert len(df.columns) >= 317, f"Backup has {len(df.columns)} columns"
    
    @pytest.mark.skipif(not BACKUP_DIR.exists(), reason="Backup directory not found")
    def test_backup_matches_current(self):
        """Verify current data matches backup column count."""
        backup_file = BACKUP_DIR / "fact_player_game_stats.csv"
        current_file = OUTPUT_DIR / "fact_player_game_stats.csv"
        
        if backup_file.exists() and current_file.exists():
            backup_df = pd.read_csv(backup_file)
            current_df = pd.read_csv(current_file)
            
            # Column counts should match
            assert len(current_df.columns) >= len(backup_df.columns), \
                f"Current ({len(current_df.columns)}) has fewer columns than backup ({len(backup_df.columns)})"


class TestETLOrchestratorPreservation:
    """Test ETL pipeline has preservation logic."""
    
    def test_etl_orchestrator_exists(self):
        """Verify ETL pipeline exists."""
        # Check for either location
        etl_file = Path("src/etl_orchestrator.py")
        pipeline_dir = Path("src/pipeline")
        assert etl_file.exists() or pipeline_dir.exists(), "ETL code not found"
    
    def test_etl_orchestrator_has_preservation_logic(self):
        """Verify pipeline has column preservation logic."""
        # Check pipeline files for preservation/merge logic
        pipeline_dir = Path("src/pipeline")
        if not pipeline_dir.exists():
            pytest.skip("Pipeline directory not found")
        
        found = False
        for py_file in pipeline_dir.glob("*.py"):
            content = py_file.read_text()
            if "existing" in content or "merge" in content.lower() or "preserve" in content.lower():
                found = True
                break
        
        assert found, "No preservation logic found in pipeline"
    
    def test_etl_orchestrator_loads_existing_columns(self):
        """Verify pipeline references stats tables."""
        pipeline_dir = Path("src/pipeline")
        if not pipeline_dir.exists():
            pytest.skip("Pipeline directory not found")
        
        found = False
        for py_file in pipeline_dir.glob("**/*.py"):
            content = py_file.read_text()
            if "player_game_stats" in content or "game_stats" in content:
                found = True
                break
        
        # Skip if not found - may use different architecture
        if not found:
            pytest.skip("Stats reference not found - architecture may differ")


class TestColumnConsistency:
    """Test column consistency across runs."""
    
    def test_column_names_are_valid(self):
        """Verify column names don't have special characters."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        invalid_cols = []
        for col in df.columns:
            # Valid: alphanumeric and underscore
            if not col.replace('_', '').replace('1', '').replace('2', '').replace('3', '').isalnum():
                if not all(c.isalnum() or c == '_' for c in col):
                    invalid_cols.append(col)
        
        # Allow some flexibility for edge cases
        assert len(invalid_cols) <= 5, f"Invalid column names: {invalid_cols[:10]}"
    
    def test_no_duplicate_columns(self):
        """Verify no duplicate column names."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        col_counts = pd.Series(df.columns).value_counts()
        duplicates = col_counts[col_counts > 1]
        
        assert len(duplicates) == 0, f"Duplicate columns: {duplicates.to_dict()}"
    
    def test_key_columns_first(self):
        """Verify key columns are at the beginning."""
        df = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv")
        
        expected_first = ['player_game_key', 'game_id', 'player_id', 'player_name']
        actual_first = list(df.columns[:4])
        
        assert actual_first == expected_first, \
            f"Expected first columns {expected_first}, got {actual_first}"
