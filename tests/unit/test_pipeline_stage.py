"""
=============================================================================
UNIT TESTS: PIPELINE STAGE MODULE
=============================================================================
File: tests/unit/test_pipeline_stage.py

PURPOSE:
    Test stage layer loading functions.
    Verify BLB and game data loading works correctly.

USAGE:
    pytest tests/unit/test_pipeline_stage.py -v

=============================================================================
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ['DB_TYPE'] = 'sqlite'


class TestLoadBLBTables:
    """
    Test BLB table loading functionality.
    
    WHY THESE TESTS:
        - Verify Excel reading works
        - Test table naming conventions
        - Ensure metadata is recorded
    """
    
    def setup_method(self):
        """Reset database before each test."""
        from src.database.connection import close_engine, get_engine
        close_engine()
        get_engine(db_type='sqlite')
    
    @patch('src.pipeline.stage.load_blb_tables.pd.ExcelFile')
    def test_load_blb_creates_stg_tables(self, mock_excel):
        """Test that BLB loading creates stg_ prefixed tables."""
        from src.pipeline.stage.load_blb_tables import load_blb_to_stage
        from src.database.table_operations import table_exists
        
        # Mock Excel file with test data
        mock_excel.return_value.sheet_names = ['dim_player', 'dim_team']
        
        # Mock read_excel to return test DataFrames
        with patch('pandas.read_excel') as mock_read:
            mock_read.side_effect = [
                pd.DataFrame({'player_id': ['P1'], 'name': ['Test']}),
                pd.DataFrame({'team_id': ['T1'], 'name': ['Team']})
            ]
            
            # Create a temp file path
            with patch.object(Path, 'exists', return_value=True):
                results = load_blb_to_stage(Path('fake/BLB.xlsx'), force_reload=True)
        
        # Verify stg_ prefix tables were created
        assert 'stg_dim_player' in results
        assert 'stg_dim_team' in results
    
    def test_clean_stage_data_removes_index(self):
        """Test that cleaning removes pandas index column."""
        from src.pipeline.stage.load_blb_tables import _clean_stage_data
        
        df = pd.DataFrame({
            'index': [0, 1, 2],
            'name': ['A', 'B', 'C']
        })
        
        cleaned = _clean_stage_data(df)
        
        assert 'index' not in cleaned.columns
        assert 'name' in cleaned.columns
    
    def test_clean_stage_data_removes_unnamed(self):
        """Test that cleaning removes Unnamed columns."""
        from src.pipeline.stage.load_blb_tables import _clean_stage_data
        
        df = pd.DataFrame({
            'name': ['A', 'B'],
            'Unnamed: 0': [1, 2],
            'Unnamed: 5': [3, 4]
        })
        
        cleaned = _clean_stage_data(df)
        
        assert 'name' in cleaned.columns
        assert 'Unnamed: 0' not in cleaned.columns
        assert 'Unnamed: 5' not in cleaned.columns
    
    def test_get_last_blb_load_info(self):
        """Test retrieving last load info."""
        from src.pipeline.stage.load_blb_tables import (
            get_last_blb_load_info,
            _record_blb_load_metadata
        )
        
        # Record some metadata
        _record_blb_load_metadata(
            Path('test/BLB.xlsx'),
            {'stg_dim_player': 10, 'stg_dim_team': 5}
        )
        
        info = get_last_blb_load_info()
        
        assert info is not None
        assert info['tables_loaded'] == 2
        assert info['total_rows'] == 15


class TestLoadGameTracking:
    """
    Test game tracking data loading.
    
    WHY THESE TESTS:
        - Verify game data loads correctly
        - Test game-specific table naming
        - Ensure proper handling of events and shifts
    """
    
    def setup_method(self):
        """Reset database before each test."""
        from src.database.connection import close_engine, get_engine
        close_engine()
        get_engine(db_type='sqlite')
    
    @patch('src.pipeline.stage.load_game_tracking.pd.ExcelFile')
    def test_load_game_creates_game_specific_tables(self, mock_excel):
        """Test that game loading creates game-specific tables."""
        from src.pipeline.stage.load_game_tracking import load_game_to_stage
        
        mock_excel.return_value.sheet_names = ['events', 'shifts']
        
        with patch('pandas.read_excel') as mock_read:
            mock_read.side_effect = [
                pd.DataFrame({'event_index': [1, 2], 'Type': ['Shot', 'Pass']}),
                pd.DataFrame({'shift_index': [1], 'Period': [1]})
            ]
            
            with patch.object(Path, 'exists', return_value=True):
                results = load_game_to_stage(
                    game_id=99999,
                    tracking_file=Path('fake/99999_tracking.xlsx'),
                    force_reload=True
                )
        
        # Verify game-specific tables
        assert 'stg_events_99999' in results
        assert 'stg_shifts_99999' in results
    
    def test_combine_csv_files(self):
        """Test combining multiple CSV files."""
        from src.pipeline.stage.load_game_tracking import _combine_csv_files
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create test CSV files
            pd.DataFrame({'x': [1, 2]}).to_csv(tmppath / 'file1.csv', index=False)
            pd.DataFrame({'x': [3, 4]}).to_csv(tmppath / 'file2.csv', index=False)
            
            result = _combine_csv_files(tmppath)
            
            assert len(result) == 4
            assert '_source_file' in result.columns
    
    def test_remove_staged_game(self):
        """Test removing staged game data."""
        from src.pipeline.stage.load_game_tracking import remove_staged_game
        from src.database.table_operations import load_dataframe_to_table, table_exists
        
        # Create test tables
        df = pd.DataFrame({'col': [1]})
        load_dataframe_to_table(df, 'stg_events_12345', 'replace')
        load_dataframe_to_table(df, 'stg_shifts_12345', 'replace')
        
        # Remove them
        dropped = remove_staged_game(12345)
        
        assert dropped >= 2
        assert table_exists('stg_events_12345') is False
        assert table_exists('stg_shifts_12345') is False


class TestLoadVideoTimes:
    """
    Test video metadata loading.
    
    WHY THESE TESTS:
        - Verify video file parsing
        - Test extraction from schedule
        - Ensure proper table creation
    """
    
    def setup_method(self):
        """Reset database before each test."""
        from src.database.connection import close_engine, get_engine
        close_engine()
        get_engine(db_type='sqlite')
    
    def test_clean_video_data(self):
        """Test video data cleaning."""
        from src.pipeline.stage.load_video_times import _clean_video_data
        
        df = pd.DataFrame({
            'Index': [1],
            'Key': ['v1'],
            'Game_ID': [18969],
            'Video_Type': ['full_game']
        })
        
        cleaned = _clean_video_data(df)
        
        # Column names should be lowercase
        assert 'game_id' in cleaned.columns or 'video_type' in cleaned.columns
    
    def test_get_video_for_game(self):
        """Test retrieving video for specific game."""
        from src.pipeline.stage.load_video_times import get_video_for_game
        from src.database.table_operations import load_dataframe_to_table
        
        # Create test video data
        df = pd.DataFrame({
            'game_id': [100, 100, 200],
            'video_key': ['v1', 'v2', 'v3'],
            'video_type': ['full', 'highlights', 'full']
        })
        load_dataframe_to_table(df, 'stg_dim_video', 'replace')
        
        result = get_video_for_game(100)
        
        assert len(result) == 2
        assert all(result['game_id'] == 100)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
