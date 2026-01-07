"""
Comprehensive integrity tests.
Updated to match current project structure.
"""
import pytest
from pathlib import Path


class TestDeploymentReadiness:
    """Test deployment readiness."""
    
    def test_sql_create_tables_exists(self):
        """Check SQL create tables exists."""
        assert Path("sql/create_all_tables.sql").exists()
    
    def test_deploy_script_exists(self):
        """Check deploy script exists."""
        assert Path("scripts/deploy_supabase.py").exists()
    
    def test_config_template_exists(self):
        """Check config template exists."""
        assert Path("config/config_local.ini.template").exists()


class TestProjectStructure:
    """Test project structure."""
    
    def test_src_exists(self):
        """Check src directory exists."""
        assert Path("src").exists()
    
    def test_data_exists(self):
        """Check data directory exists."""
        assert Path("data").exists()
    
    def test_docs_exists(self):
        """Check docs directory exists."""
        assert Path("docs").exists()
