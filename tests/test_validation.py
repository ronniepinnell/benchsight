"""
Tests for data validation.
Updated to match current project structure.
"""
import pytest
from pathlib import Path
import pandas as pd


class TestDataOutputFiles:
    """Test that data output files exist and are valid."""
    
    def test_output_directory_exists(self):
        """Check output directory exists."""
        assert Path("data/output").exists()
    
    def test_dimension_tables_exist(self):
        """Check dimension tables exist."""
        dim_files = list(Path("data/output").glob("dim_*.csv"))
        assert len(dim_files) >= 40
    
    def test_fact_tables_exist(self):
        """Check fact tables exist."""
        fact_files = list(Path("data/output").glob("fact_*.csv"))
        assert len(fact_files) >= 45
    
    def test_player_game_stats_has_data(self):
        """Check main stats table has data."""
        path = Path("data/output/fact_player_game_stats.csv")
        if path.exists():
            df = pd.read_csv(path)
            assert len(df) > 0
            assert len(df.columns) >= 300  # Should have 317 columns


class TestDataIntegrity:
    """Test data integrity."""
    
    def test_dim_player_has_data(self):
        """Check player dimension has data."""
        path = Path("data/output/dim_player.csv")
        if path.exists():
            df = pd.read_csv(path)
            assert len(df) > 0
    
    def test_dim_team_has_data(self):
        """Check team dimension has data."""
        path = Path("data/output/dim_team.csv")
        if path.exists():
            df = pd.read_csv(path)
            assert len(df) > 0
