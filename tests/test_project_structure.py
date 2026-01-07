"""
Tests for project structure and deployment readiness.
Verifies all required files and configurations exist.
"""
import pytest
from pathlib import Path
import configparser


class TestProjectStructure:
    """Test core project structure."""
    
    def test_readme_exists(self):
        """README.md exists."""
        assert Path("README.md").exists()
    
    def test_handoff_exists(self):
        """HANDOFF.md exists."""
        assert Path("HANDOFF.md").exists()
    
    def test_requirements_exists(self):
        """requirements.txt exists."""
        assert Path("requirements.txt").exists()
    
    def test_gitignore_exists(self):
        """.gitignore exists."""
        assert Path(".gitignore").exists()


class TestConfigFiles:
    """Test configuration files."""
    
    def test_config_template_exists(self):
        """Config template exists."""
        assert Path("config/config_local.ini.template").exists()
    
    def test_config_template_has_supabase_section(self):
        """Config template has supabase section."""
        content = Path("config/config_local.ini.template").read_text()
        assert "[supabase]" in content
        assert "url" in content
        assert "service_key" in content


class TestSQLFiles:
    """Test SQL files."""
    
    def test_create_tables_exists(self):
        """create_all_tables.sql exists."""
        assert Path("sql/create_all_tables.sql").exists()
    
    def test_drop_tables_exists(self):
        """drop_all_tables.sql exists."""
        assert Path("sql/drop_all_tables.sql").exists()
    
    def test_truncate_exists(self):
        """truncate_all_data.sql exists."""
        assert Path("sql/truncate_all_data.sql").exists()
    
    def test_create_has_111_tables(self):
        """CREATE TABLE count matches expected."""
        content = Path("sql/create_all_tables.sql").read_text()
        count = content.count("CREATE TABLE IF NOT EXISTS")
        assert count == 111, f"Expected 111 tables, found {count}"


class TestScripts:
    """Test deployment scripts."""
    
    def test_deploy_script_exists(self):
        """deploy_supabase.py exists."""
        assert Path("scripts/deploy_supabase.py").exists()
    
    def test_schema_script_exists(self):
        """supabase_schema.py exists."""
        assert Path("scripts/supabase_schema.py").exists()
    
    def test_verify_script_exists(self):
        """verify_delivery.py exists."""
        assert Path("scripts/verify_delivery.py").exists()


class TestDataOutput:
    """Test data output files."""
    
    def test_output_dir_exists(self):
        """data/output directory exists."""
        assert Path("data/output").exists()
    
    def test_csv_count(self):
        """Expected number of CSV files."""
        csv_files = list(Path("data/output").glob("*.csv"))
        assert len(csv_files) == 111, f"Expected 111 CSVs, found {len(csv_files)}"
    
    def test_key_tables_exist(self):
        """Key tables exist."""
        required = [
            "dim_player", "dim_team", "dim_game", "dim_schedule",
            "fact_events", "fact_events_player", "fact_gameroster"
        ]
        for table in required:
            assert Path(f"data/output/{table}.csv").exists(), f"Missing {table}"


class TestDocumentation:
    """Test documentation files."""
    
    def test_table_inventory_exists(self):
        """TABLE_INVENTORY.csv exists."""
        assert Path("docs/TABLE_INVENTORY.csv").exists()
    
    def test_data_dictionary_exists(self):
        """DATA_DICTIONARY_ALL_COLUMNS.csv exists."""
        assert Path("docs/DATA_DICTIONARY_ALL_COLUMNS.csv").exists()
    
    def test_deployment_guide_exists(self):
        """SUPABASE_DEPLOYMENT_GUIDE.md exists."""
        assert Path("docs/SUPABASE_DEPLOYMENT_GUIDE.md").exists()


class TestETLPipeline:
    """Test ETL pipeline structure."""
    
    def test_main_exists(self):
        """src/main.py exists."""
        assert Path("src/main.py").exists()
    
    def test_pipeline_dir_exists(self):
        """src/pipeline directory exists."""
        assert Path("src/pipeline").exists()
    
    def test_orchestrator_exists(self):
        """Pipeline orchestrator exists."""
        assert Path("src/pipeline/orchestrator.py").exists()
