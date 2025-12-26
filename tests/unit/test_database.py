"""
=============================================================================
UNIT TESTS: DATABASE MODULE
=============================================================================
File: tests/unit/test_database.py

PURPOSE:
    Test database connection and table operations.
    Uses SQLite in-memory database for fast testing.

USAGE:
    pytest tests/unit/test_database.py -v

=============================================================================
"""

import pytest
import pandas as pd
from pathlib import Path
import sys
import os

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set environment to use SQLite for testing
os.environ['DB_TYPE'] = 'sqlite'


class TestDatabaseConnection:
    """
    Test database connection functionality.
    
    WHY THESE TESTS:
        - Verify connection can be established
        - Ensure context manager works correctly
        - Test both SQLite and PostgreSQL connection strings
    """
    
    def setup_method(self):
        """Reset engine before each test."""
        from src.database.connection import close_engine
        close_engine()
    
    def test_get_engine_creates_engine(self):
        """Test that get_engine creates a valid engine."""
        from src.database.connection import get_engine
        
        engine = get_engine(db_type='sqlite')
        
        # Verify engine is created
        assert engine is not None
        # Verify it's a SQLAlchemy engine
        assert hasattr(engine, 'connect')
    
    def test_get_engine_singleton(self):
        """Test that get_engine returns same instance."""
        from src.database.connection import get_engine
        
        engine1 = get_engine(db_type='sqlite')
        engine2 = get_engine()
        
        # Should be same instance
        assert engine1 is engine2
    
    def test_get_connection_context_manager(self):
        """Test connection context manager."""
        from src.database.connection import get_connection, get_engine
        from sqlalchemy import text
        
        get_engine(db_type='sqlite')
        
        with get_connection() as conn:
            # Connection should be valid
            result = conn.execute(text("SELECT 1 AS test"))
            row = result.fetchone()
            assert row[0] == 1
    
    def test_execute_sql(self):
        """Test SQL execution."""
        from src.database.connection import execute_sql, get_connection, get_engine
        from sqlalchemy import text
        
        get_engine(db_type='sqlite')
        
        # Create a test table
        execute_sql("CREATE TABLE IF NOT EXISTS test_exec (id INTEGER, name TEXT)")
        
        # Insert data
        execute_sql("INSERT INTO test_exec VALUES (1, 'test')")
        
        # Verify data
        with get_connection() as conn:
            result = conn.execute(text("SELECT * FROM test_exec"))
            rows = result.fetchall()
            assert len(rows) == 1
            assert rows[0][0] == 1
            assert rows[0][1] == 'test'
        
        # Cleanup
        execute_sql("DROP TABLE test_exec")
    
    def test_execute_sql_with_params(self):
        """Test parameterized SQL execution."""
        from src.database.connection import execute_sql, get_connection, get_engine
        from sqlalchemy import text
        
        get_engine(db_type='sqlite')
        
        execute_sql("CREATE TABLE IF NOT EXISTS test_params (id INTEGER, name TEXT)")
        execute_sql(
            "INSERT INTO test_params VALUES (:id, :name)",
            {'id': 42, 'name': 'parameterized'}
        )
        
        with get_connection() as conn:
            result = conn.execute(text("SELECT * FROM test_params WHERE id = 42"))
            row = result.fetchone()
            assert row[1] == 'parameterized'
        
        execute_sql("DROP TABLE test_params")
    
    def test_postgres_connection_string(self):
        """Test PostgreSQL connection string builder."""
        from src.database.connection import _build_postgres_connection_string
        
        conn_str = _build_postgres_connection_string(
            host='testhost',
            port='5433',
            database='testdb',
            user='testuser',
            password='testpass'
        )
        
        assert 'postgresql://' in conn_str
        assert 'testhost' in conn_str
        assert '5433' in conn_str
        assert 'testdb' in conn_str
        assert 'testuser' in conn_str
        assert 'testpass' in conn_str
    
    def test_sqlite_connection_string(self):
        """Test SQLite connection string builder."""
        from src.database.connection import _build_sqlite_connection_string
        
        conn_str = _build_sqlite_connection_string()
        
        assert 'sqlite:///' in conn_str
        assert 'hockey_analytics.db' in conn_str
    
    def test_close_engine(self):
        """Test engine cleanup."""
        from src.database.connection import get_engine, close_engine
        import src.database.connection as conn_module
        
        get_engine(db_type='sqlite')
        assert conn_module._engine is not None
        
        close_engine()
        assert conn_module._engine is None
    
    def test_test_connection(self):
        """Test the connection test function."""
        from src.database.connection import test_connection, get_engine
        
        get_engine(db_type='sqlite')
        
        result = test_connection()
        assert result is True


class TestTableOperations:
    """
    Test table CRUD operations.
    
    WHY THESE TESTS:
        - Verify DataFrame loading works
        - Test table existence checks
        - Test layer-based table filtering
    """
    
    def setup_method(self):
        """Setup test database."""
        from src.database.connection import get_engine, close_engine
        close_engine()
        get_engine(db_type='sqlite')
    
    def test_load_dataframe_to_table(self):
        """Test loading DataFrame to table."""
        from src.database.table_operations import load_dataframe_to_table, table_exists
        
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie']
        })
        
        row_count = load_dataframe_to_table(df, 'test_load', 'replace')
        
        assert row_count == 3
        assert table_exists('test_load')
    
    def test_read_table(self):
        """Test reading table to DataFrame."""
        from src.database.table_operations import load_dataframe_to_table, read_table
        
        df = pd.DataFrame({'x': [1, 2], 'y': ['a', 'b']})
        load_dataframe_to_table(df, 'test_read', 'replace')
        
        result = read_table('test_read')
        
        assert len(result) == 2
        assert 'x' in result.columns
        assert 'y' in result.columns
    
    def test_table_exists(self):
        """Test table existence check."""
        from src.database.table_operations import table_exists, load_dataframe_to_table
        
        # Non-existent table
        assert table_exists('nonexistent_table_xyz') is False
        
        # Create table
        df = pd.DataFrame({'col': [1]})
        load_dataframe_to_table(df, 'exists_test', 'replace')
        
        assert table_exists('exists_test') is True
    
    def test_get_tables_by_layer(self):
        """Test filtering tables by layer."""
        from src.database.table_operations import (
            load_dataframe_to_table, 
            get_tables_by_layer
        )
        
        df = pd.DataFrame({'col': [1]})
        
        # Create tables in different layers
        load_dataframe_to_table(df, 'stg_test_layer', 'replace')
        load_dataframe_to_table(df, 'int_test_layer', 'replace')
        load_dataframe_to_table(df, 'dm_test_layer', 'replace')
        
        stage_tables = get_tables_by_layer('stage')
        int_tables = get_tables_by_layer('intermediate')
        
        assert 'stg_test_layer' in stage_tables
        assert 'int_test_layer' in int_tables
    
    def test_drop_table(self):
        """Test dropping a table."""
        from src.database.table_operations import (
            load_dataframe_to_table,
            drop_table,
            table_exists
        )
        
        df = pd.DataFrame({'col': [1]})
        load_dataframe_to_table(df, 'drop_test', 'replace')
        
        assert table_exists('drop_test') is True
        
        result = drop_table('drop_test')
        
        assert result is True
        assert table_exists('drop_test') is False
    
    def test_get_row_count(self):
        """Test getting row count."""
        from src.database.table_operations import (
            load_dataframe_to_table,
            get_row_count
        )
        
        df = pd.DataFrame({'col': range(100)})
        load_dataframe_to_table(df, 'count_test', 'replace')
        
        count = get_row_count('count_test')
        
        assert count == 100
    
    def test_clear_layer(self):
        """Test clearing all tables in a layer."""
        from src.database.table_operations import (
            load_dataframe_to_table,
            clear_layer,
            table_exists
        )
        
        df = pd.DataFrame({'col': [1]})
        load_dataframe_to_table(df, 'stg_clear_1', 'replace')
        load_dataframe_to_table(df, 'stg_clear_2', 'replace')
        
        cleared = clear_layer('stage')
        
        assert cleared >= 2
        assert table_exists('stg_clear_1') is False
        assert table_exists('stg_clear_2') is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
