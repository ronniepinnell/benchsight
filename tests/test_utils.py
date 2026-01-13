"""
=============================================================================
UNIT TESTS FOR UTILITY MODULES
=============================================================================
File: tests/test_utils.py
Version: 19.12
Created: January 9, 2026

Tests for:
- src/utils/key_parser.py
- src/utils/table_manager.py
- src/utils/shared_lookups.py
- src/utils/error_handler.py
=============================================================================
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestKeyParser:
    """Tests for src/utils/key_parser.py"""
    
    def test_parse_shift_key_valid(self):
        """Valid shift keys should parse correctly."""
        from src.utils.key_parser import parse_shift_key
        
        result = parse_shift_key("SH1896900001")
        assert result is not None
        assert result.game_id == 18969
        assert result.shift_index == 1
        assert result.raw == "SH1896900001"
    
    def test_parse_shift_key_large_index(self):
        """Shift keys with large indices should work."""
        from src.utils.key_parser import parse_shift_key
        
        result = parse_shift_key("SH18969001234")
        assert result is not None
        assert result.game_id == 18969
        assert result.shift_index == 1234
    
    def test_parse_shift_key_invalid(self):
        """Invalid shift keys should return None."""
        from src.utils.key_parser import parse_shift_key
        
        assert parse_shift_key("") is None
        assert parse_shift_key(None) is None
        assert parse_shift_key("INVALID") is None
        assert parse_shift_key("EV1896900001") is None  # Wrong prefix
        assert parse_shift_key("SH") is None  # Too short
        assert parse_shift_key("SH12345") is None  # Too short
    
    def test_make_shift_key(self):
        """make_shift_key should create valid keys."""
        from src.utils.key_parser import make_shift_key
        
        assert make_shift_key(18969, 1) == "SH1896900001"
        assert make_shift_key(18969, 123) == "SH1896900123"
        assert make_shift_key(1, 1) == "SH0000100001"
    
    def test_roundtrip_shift_key(self):
        """Parsing a created key should return original values."""
        from src.utils.key_parser import parse_shift_key, make_shift_key
        
        key = make_shift_key(18969, 42)
        result = parse_shift_key(key)
        assert result.game_id == 18969
        assert result.shift_index == 42
    
    def test_parse_event_key_valid(self):
        """Valid event keys should parse correctly."""
        from src.utils.key_parser import parse_event_key
        
        result = parse_event_key("EV1896900123")
        assert result is not None
        assert result.game_id == 18969
        assert result.event_index == 123
    
    def test_parse_event_key_invalid(self):
        """Invalid event keys should return None."""
        from src.utils.key_parser import parse_event_key
        
        assert parse_event_key("") is None
        assert parse_event_key("SH1896900001") is None  # Wrong prefix
    
    def test_extract_game_id_from_key(self):
        """Should extract game_id from any key type."""
        from src.utils.key_parser import extract_game_id_from_key
        
        assert extract_game_id_from_key("SH1896900001") == 18969
        assert extract_game_id_from_key("EV1896900123") == 18969
        assert extract_game_id_from_key("SQ1897700001") == 18977
        assert extract_game_id_from_key("") is None
        assert extract_game_id_from_key("SHORT") is None
    
    def test_convert_le_to_lv_key(self):
        """LE to LV conversion should work correctly."""
        from src.utils.key_parser import convert_le_to_lv_key
        
        # LE18969009001 -> LV1896909001
        assert convert_le_to_lv_key("LE18969009001") == "LV1896909001"
        assert convert_le_to_lv_key("") is None
        assert convert_le_to_lv_key(None) is None
        assert convert_le_to_lv_key("INVALID") is None
    
    def test_make_player_key(self):
        """make_player_key should create valid keys."""
        from src.utils.key_parser import make_player_key
        
        assert make_player_key(100001) == "P100001"
        assert make_player_key(1) == "P000001"


class TestTableManager:
    """Tests for src/utils/table_manager.py"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def tm(self, temp_dir):
        """Create a TableManager with temp directory."""
        from src.utils.table_manager import TableManager
        return TableManager(output_dir=temp_dir)
    
    def test_save_and_load(self, tm, temp_dir):
        """Should save and load tables correctly."""
        df = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
        
        tm.save('test_table', df)
        
        assert (temp_dir / 'test_table.csv').exists()
        
        loaded = tm.load('test_table')
        assert len(loaded) == 3
        assert list(loaded.columns) == ['a', 'b']
    
    def test_load_caching(self, tm, temp_dir):
        """Loading should cache the result."""
        df = pd.DataFrame({'a': [1, 2, 3]})
        tm.save('test_table', df)
        
        # First load
        loaded1 = tm.load('test_table')
        # Modify the file on disk
        pd.DataFrame({'a': [4, 5, 6]}).to_csv(temp_dir / 'test_table.csv', index=False)
        # Second load should return cached version
        loaded2 = tm.load('test_table')
        
        assert loaded1['a'].tolist() == [1, 2, 3]
        assert loaded2['a'].tolist() == [1, 2, 3]  # Cached, not reloaded
    
    def test_force_reload(self, tm, temp_dir):
        """force_reload should bypass cache."""
        df = pd.DataFrame({'a': [1, 2, 3]})
        tm.save('test_table', df)
        
        tm.load('test_table')
        pd.DataFrame({'a': [4, 5, 6]}).to_csv(temp_dir / 'test_table.csv', index=False)
        
        reloaded = tm.load('test_table', force_reload=True)
        assert reloaded['a'].tolist() == [4, 5, 6]
    
    def test_mark_dirty_and_flush(self, tm, temp_dir):
        """mark_dirty and flush should work correctly."""
        df = pd.DataFrame({'a': [1, 2, 3]})
        tm.save('test_table', df)
        
        loaded = tm.load('test_table')
        loaded['b'] = [10, 20, 30]
        tm.mark_dirty('test_table', loaded)
        
        # Before flush, file shouldn't have new column
        on_disk = pd.read_csv(temp_dir / 'test_table.csv')
        assert 'b' not in on_disk.columns
        
        # After flush, it should
        tm.flush_all()
        on_disk = pd.read_csv(temp_dir / 'test_table.csv')
        assert 'b' in on_disk.columns
    
    def test_load_nonexistent(self, tm):
        """Loading nonexistent table should return None."""
        result = tm.load('nonexistent_table')
        assert result is None
    
    def test_list_tables(self, tm, temp_dir):
        """list_tables should return all CSV files."""
        pd.DataFrame({'a': [1]}).to_csv(temp_dir / 'table1.csv', index=False)
        pd.DataFrame({'a': [2]}).to_csv(temp_dir / 'table2.csv', index=False)
        
        tables = tm.list_tables()
        assert 'table1' in tables
        assert 'table2' in tables


class TestErrorHandler:
    """Tests for src/utils/error_handler.py"""
    
    def test_safe_execute_success(self):
        """safe_execute should return function result on success."""
        from src.utils.error_handler import safe_execute
        
        @safe_execute(default_return=-1)
        def add(a, b):
            return a + b
        
        assert add(2, 3) == 5
    
    def test_safe_execute_failure(self):
        """safe_execute should return default on failure."""
        from src.utils.error_handler import safe_execute
        
        @safe_execute(default_return=-1, log_errors=False)
        def fail():
            raise ValueError("test error")
        
        assert fail() == -1
    
    def test_safe_execute_reraise(self):
        """safe_execute with reraise=True should re-raise."""
        from src.utils.error_handler import safe_execute
        
        @safe_execute(default_return=-1, reraise=True, log_errors=False)
        def fail():
            raise ValueError("test error")
        
        with pytest.raises(ValueError):
            fail()
    
    def test_error_context_success(self):
        """error_context should pass through on success."""
        from src.utils.error_handler import error_context
        
        result = None
        with error_context("test operation"):
            result = 42
        
        assert result == 42
    
    def test_error_context_failure(self):
        """error_context should re-raise with context."""
        from src.utils.error_handler import error_context
        
        with pytest.raises(ValueError):
            with error_context("test operation", table="test_table"):
                raise ValueError("inner error")
    
    def test_validate_dataframe_success(self):
        """validate_dataframe should pass valid dataframes."""
        from src.utils.error_handler import validate_dataframe
        
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        validate_dataframe(df, required_columns=['a', 'b'], min_rows=2)
    
    def test_validate_dataframe_missing_columns(self):
        """validate_dataframe should fail on missing columns."""
        from src.utils.error_handler import validate_dataframe, ColumnMismatchError
        
        df = pd.DataFrame({'a': [1, 2, 3]})
        
        with pytest.raises(ColumnMismatchError):
            validate_dataframe(df, required_columns=['a', 'b', 'c'])
    
    def test_validate_dataframe_too_few_rows(self):
        """validate_dataframe should fail on too few rows."""
        from src.utils.error_handler import validate_dataframe, DataValidationError
        
        df = pd.DataFrame({'a': [1, 2, 3]})
        
        with pytest.raises(DataValidationError):
            validate_dataframe(df, min_rows=10)
    
    def test_etl_error_formatting(self):
        """ETLError should format nicely."""
        from src.utils.error_handler import ETLError
        
        error = ETLError("Something went wrong", phase="Phase 1", table="fact_events")
        assert "Something went wrong" in str(error)
        assert "Phase 1" in str(error)
        assert "fact_events" in str(error)


class TestSharedLookups:
    """Tests for src/utils/shared_lookups.py"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temp directory with test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create dim_player.csv
            pd.DataFrame({
                'player_id': ['P100001', 'P100002', 'P100003'],
                'player_full_name': ['Alice', 'Bob', 'Charlie'],
                'current_skill_rating': [7.5, 5.0, 8.2],
                'position_id': ['POS001', 'POS002', 'POS001']
            }).to_csv(tmpdir / 'dim_player.csv', index=False)
            
            # Create dim_team.csv
            pd.DataFrame({
                'team_id': ['TM001', 'TM002'],
                'team_name': ['Hawks', 'Eagles']
            }).to_csv(tmpdir / 'dim_team.csv', index=False)
            
            yield tmpdir
    
    def test_get_player_rating_map(self, temp_output_dir):
        """Should return player ratings."""
        from src.utils.shared_lookups import LookupCache
        
        cache = LookupCache()
        cache._output_dir = temp_output_dir
        cache.clear()
        
        ratings = cache.get_player_rating_map()
        
        assert ratings['P100001'] == 7.5
        assert ratings['P100002'] == 5.0
        assert ratings['P100003'] == 8.2
    
    def test_get_team_lookup(self, temp_output_dir):
        """Should return team lookups."""
        from src.utils.shared_lookups import LookupCache
        
        cache = LookupCache()
        cache._output_dir = temp_output_dir
        cache.clear()
        
        teams = cache.get_team_lookup()
        
        assert teams['hawks'] == 'TM001'
        assert teams['eagles'] == 'TM002'
    
    def test_caching(self, temp_output_dir):
        """Lookups should be cached."""
        from src.utils.shared_lookups import LookupCache
        
        cache = LookupCache()
        cache._output_dir = temp_output_dir
        cache.clear()
        
        ratings1 = cache.get_player_rating_map()
        ratings2 = cache.get_player_rating_map()
        
        # Should be the same object (cached)
        assert ratings1 is ratings2
    
    def test_clear_cache(self, temp_output_dir):
        """clear() should reset the cache."""
        from src.utils.shared_lookups import LookupCache
        
        cache = LookupCache()
        cache._output_dir = temp_output_dir
        cache.clear()
        
        ratings1 = cache.get_player_rating_map()
        cache.clear()
        ratings2 = cache.get_player_rating_map()
        
        # Should be different objects after clear
        assert ratings1 is not ratings2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
