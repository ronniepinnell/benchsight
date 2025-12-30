"""
Tests for Supabase configuration and deployment readiness.
Updated to match current project structure.
"""
import pytest
from pathlib import Path
import configparser


class TestSupabaseConfiguration:
    """Test Supabase configuration files."""
    
    def test_config_local_example_exists(self):
        """Verify config example exists."""
        assert Path("config/config_local.ini.example").exists()
    
    def test_config_has_key(self):
        """Check config has required keys (if exists)."""
        config_path = Path("config/config_local.ini")
        if config_path.exists():
            config = configparser.ConfigParser()
            config.read(config_path)
            assert "supabase" in config.sections()


class TestSupabaseSQLFiles:
    """Test SQL files exist."""
    
    def test_create_tables_sql_exists(self):
        """Verify CREATE_ALL_TABLES.sql exists."""
        assert Path("sql/01_CREATE_ALL_TABLES.sql").exists()
    
    def test_type_fixes_sql_exists(self):
        """Verify TYPE_FIXES.sql exists."""
        assert Path("sql/02_TYPE_FIXES.sql").exists()


class TestSupabaseLoaderScript:
    """Test loader script exists."""
    
    def test_flexible_loader_exists(self):
        """Verify flexible_loader.py exists."""
        assert Path("scripts/flexible_loader.py").exists()


class TestRequiredScripts:
    """Test required scripts exist."""
    
    def test_main_py_exists(self):
        """Verify main.py exists."""
        assert Path("src/main.py").exists()
    
    def test_run_scripts_exist(self):
        """Verify run scripts exist."""
        assert Path("run_etl.sh").exists() or Path("run_deploy.sh").exists()


class TestDocumentation:
    """Test documentation exists."""
    
    def test_readme_exists(self):
        """Verify README.md exists."""
        assert Path("README.md").exists()
    
    def test_deployment_guide_exists(self):
        """Verify DEPLOYMENT_GUIDE.md exists."""
        assert Path("docs/DEPLOYMENT_GUIDE.md").exists()
    
    def test_stats_reference_exists(self):
        """Verify STATS_REFERENCE_COMPLETE.md exists."""
        assert Path("docs/STATS_REFERENCE_COMPLETE.md").exists()
    
    def test_data_dictionary_exists(self):
        """Verify DATA_DICTIONARY.md exists."""
        assert Path("docs/DATA_DICTIONARY.md").exists()
    
    def test_handoffs_exist(self):
        """Verify handoff docs exist."""
        assert Path("docs/handoffs").exists()
        handoffs = list(Path("docs/handoffs").glob("*.md"))
        assert len(handoffs) >= 3


class TestDataOutput:
    """Test data output files."""
    
    def test_output_dir_exists(self):
        """Verify data/output directory exists."""
        assert Path("data/output").exists()
    
    def test_csv_files_exist(self):
        """Verify CSV files exist."""
        csv_files = list(Path("data/output").glob("*.csv"))
        assert len(csv_files) >= 90  # Should have 96


class TestHTMLDocs:
    """Test HTML documentation."""
    
    def test_html_docs_exist(self):
        """Verify HTML docs exist."""
        html_dir = Path("docs/html_docs")
        if html_dir.exists():
            html_files = list(html_dir.glob("*.html"))
            assert len(html_files) >= 5
