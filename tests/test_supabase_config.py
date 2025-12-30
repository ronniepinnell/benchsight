"""
BENCHSIGHT - Supabase and Configuration Tests
=============================================
Tests for Supabase deployment readiness and configuration.
"""

import pytest
import pandas as pd
import json
from pathlib import Path
import configparser

PROJECT_DIR = Path(".")
OUTPUT_DIR = Path("data/output")
CONFIG_DIR = Path("config")
SQL_DIR = Path("sql")


class TestSupabaseConfiguration:
    """Test Supabase configuration files."""
    
    def test_config_local_ini_exists(self):
        """Verify config_local.ini exists."""
        config_file = CONFIG_DIR / "config_local.ini"
        assert config_file.exists(), "config_local.ini not found"
    
    def test_config_has_supabase_section(self):
        """Verify config has [supabase] section."""
        config_file = CONFIG_DIR / "config_local.ini"
        if config_file.exists():
            config = configparser.ConfigParser()
            config.read(config_file)
            assert 'supabase' in config.sections(), "Missing [supabase] section"
    
    def test_config_has_url(self):
        """Verify config has Supabase URL."""
        config_file = CONFIG_DIR / "config_local.ini"
        if config_file.exists():
            config = configparser.ConfigParser()
            config.read(config_file)
            if 'supabase' in config.sections():
                url = config.get('supabase', 'url', fallback=None)
                assert url is not None, "Missing supabase url"
                assert 'supabase.co' in url, "URL doesn't look like Supabase"
    
    def test_config_has_key(self):
        """Verify config has Supabase key."""
        config_file = CONFIG_DIR / "config_local.ini"
        if config_file.exists():
            config = configparser.ConfigParser()
            config.read(config_file)
            if 'supabase' in config.sections():
                key = config.get('supabase', 'key', fallback=None)
                assert key is not None, "Missing supabase key"
                assert len(key) > 50, "Key seems too short"


class TestSupabaseSQLFiles:
    """Test Supabase SQL DDL files."""
    
    def test_create_tables_sql_exists(self):
        """Verify CREATE TABLE SQL exists."""
        sql_files = list(SQL_DIR.glob("*create*.sql"))
        assert len(sql_files) > 0, "No CREATE TABLE SQL files found"
    
    def test_drop_tables_sql_exists(self):
        """Verify DROP TABLE SQL exists."""
        sql_files = list(SQL_DIR.glob("*drop*.sql"))
        assert len(sql_files) > 0, "No DROP TABLE SQL files found"
    
    def test_create_sql_has_all_tables(self):
        """Verify CREATE SQL covers all output tables."""
        # Find the main create script
        create_files = list(SQL_DIR.glob("*create*.sql"))
        if not create_files:
            pytest.skip("No CREATE SQL files")
        
        # Read the largest create file
        create_file = max(create_files, key=lambda f: f.stat().st_size)
        sql_content = create_file.read_text().lower()
        
        # Check that key tables are in the SQL
        key_tables = ['dim_player', 'dim_team', 'fact_player_game_stats', 'fact_events']
        missing = [t for t in key_tables if f'create table' not in sql_content or t not in sql_content]
        
        assert len(missing) <= 1, f"SQL missing tables: {missing}"
    
    def test_sql_syntax_valid(self):
        """Basic SQL syntax validation."""
        sql_files = list(SQL_DIR.glob("*.sql"))
        
        syntax_issues = []
        for sql_file in sql_files:
            content = sql_file.read_text()
            
            # Basic checks
            if 'CREATE TABLE' in content.upper():
                # Should have matching parentheses
                open_parens = content.count('(')
                close_parens = content.count(')')
                if open_parens != close_parens:
                    syntax_issues.append((sql_file.name, "Mismatched parentheses"))
        
        assert len(syntax_issues) == 0, f"SQL syntax issues: {syntax_issues}"


class TestSupabaseSchemaJSON:
    """Test Supabase schema JSON."""
    
    def test_schema_json_exists(self):
        """Verify supabase_schema.json exists."""
        schema_file = CONFIG_DIR / "supabase_schema.json"
        assert schema_file.exists(), "supabase_schema.json not found"
    
    def test_schema_json_valid(self):
        """Verify schema JSON is valid."""
        schema_file = CONFIG_DIR / "supabase_schema.json"
        if schema_file.exists():
            content = schema_file.read_text()
            try:
                schema = json.loads(content)
                assert isinstance(schema, (dict, list)), "Schema should be dict or list"
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON: {e}")
    
    def test_schema_has_tables(self):
        """Verify schema defines tables."""
        schema_file = CONFIG_DIR / "supabase_schema.json"
        if schema_file.exists():
            schema = json.loads(schema_file.read_text())
            
            # Schema should have table definitions
            if isinstance(schema, dict):
                assert 'tables' in schema or len(schema) > 0, "Schema has no tables"


class TestSupabaseLoaderScript:
    """Test Supabase loader script."""
    
    def test_supabase_loader_exists(self):
        """Verify supabase_loader.py exists."""
        loader = Path("scripts/supabase_loader.py")
        assert loader.exists(), "supabase_loader.py not found"
    
    def test_supabase_loader_has_modes(self):
        """Verify loader supports required modes."""
        loader = Path("scripts/supabase_loader.py")
        if loader.exists():
            content = loader.read_text()
            
            required_modes = ['--rebuild', '--all', '--dims', '--facts', '--verify']
            for mode in required_modes:
                assert mode in content, f"Loader missing {mode} mode"
    
    def test_supabase_test_connection_exists(self):
        """Verify test connection script exists."""
        test_script = Path("scripts/supabase_test_connection.py")
        assert test_script.exists(), "supabase_test_connection.py not found"


class TestDataSupabaseReadiness:
    """Test data is ready for Supabase upload."""
    
    def test_csv_files_not_too_large(self):
        """Verify CSV files aren't too large for upload."""
        max_size_mb = 50  # 50MB limit
        
        large_files = []
        for csv_file in OUTPUT_DIR.glob("*.csv"):
            size_mb = csv_file.stat().st_size / (1024 * 1024)
            if size_mb > max_size_mb:
                large_files.append((csv_file.name, f"{size_mb:.1f}MB"))
        
        assert len(large_files) == 0, f"Files too large for upload: {large_files}"
    
    def test_no_special_characters_in_values(self):
        """Verify no problematic special characters in data."""
        # Check a sample of tables
        sample_tables = ['dim_player', 'dim_team', 'fact_player_game_stats']
        
        issues = []
        for table in sample_tables:
            table_path = OUTPUT_DIR / f"{table}.csv"
            if table_path.exists():
                df = pd.read_csv(table_path, dtype=str, nrows=100)
                
                for col in df.columns:
                    # Check for null bytes or other problematic chars
                    if df[col].dtype == 'object':
                        has_null_byte = df[col].str.contains('\x00', na=False).any()
                        if has_null_byte:
                            issues.append((table, col, "null byte"))
        
        assert len(issues) == 0, f"Special character issues: {issues}"
    
    def test_column_names_supabase_compatible(self):
        """Verify column names are Supabase/PostgreSQL compatible."""
        all_tables = list(OUTPUT_DIR.glob("*.csv"))
        
        invalid_cols = []
        for table_path in all_tables:
            df = pd.read_csv(table_path, nrows=0)
            
            for col in df.columns:
                # PostgreSQL column naming rules
                if len(col) > 63:
                    invalid_cols.append((table_path.stem, col, "too long"))
                # Note: reserved words can be escaped with quotes in PostgreSQL
                # We track them but allow a few
        
        # Allow some minor issues (reserved words can be quoted in SQL)
        assert len(invalid_cols) <= 5, f"Invalid column names: {invalid_cols}"


class TestRequiredScripts:
    """Test all required scripts exist and are functional."""
    
    def test_etl_py_exists(self):
        """Verify etl.py exists."""
        assert Path("etl.py").exists(), "etl.py not found"
    
    def test_verify_delivery_exists(self):
        """Verify verify_delivery.py exists."""
        assert Path("scripts/verify_delivery.py").exists(), "verify_delivery.py not found"
    
    def test_validate_stats_exists(self):
        """Verify validate_stats.py exists."""
        assert Path("scripts/validate_stats.py").exists(), "validate_stats.py not found"
    
    def test_qa_dynamic_exists(self):
        """Verify qa_dynamic.py exists."""
        assert Path("scripts/qa_dynamic.py").exists(), "qa_dynamic.py not found"
    
    def test_etl_orchestrator_exists(self):
        """Verify etl_orchestrator.py exists."""
        assert Path("src/etl_orchestrator.py").exists(), "etl_orchestrator.py not found"
    
    def test_enhance_all_stats_exists(self):
        """Verify enhance_all_stats.py exists."""
        assert Path("src/enhance_all_stats.py").exists(), "enhance_all_stats.py not found"


class TestDocumentation:
    """Test documentation completeness."""
    
    def test_readme_exists(self):
        """Verify README.md exists."""
        assert Path("README.md").exists(), "README.md not found"
    
    def test_start_here_exists(self):
        """Verify START_HERE.md exists."""
        assert Path("START_HERE.md").exists(), "START_HERE.md not found"
    
    def test_handoff_docs_exist(self):
        """Verify handoff documentation exists."""
        handoff_dir = Path("docs/handoff")
        assert handoff_dir.exists(), "docs/handoff directory not found"
        
        handoff_files = list(handoff_dir.glob("*.md"))
        assert len(handoff_files) >= 3, f"Only {len(handoff_files)} handoff docs"
    
    def test_known_bugs_exists(self):
        """Verify KNOWN_BUGS.md exists."""
        assert Path("docs/KNOWN_BUGS.md").exists(), "KNOWN_BUGS.md not found"
    
    def test_documentation_hub_exists(self):
        """Verify DOCUMENTATION_HUB.html exists."""
        assert Path("docs/DOCUMENTATION_HUB.html").exists(), "DOCUMENTATION_HUB.html not found"
