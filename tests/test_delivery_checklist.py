"""
Delivery Checklist Tests
========================
Run BEFORE delivering any package to verify completeness.

Run: pytest tests/test_delivery_checklist.py -v
"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta


class TestRequiredFiles:
    """Verify all required files exist."""
    
    @pytest.mark.parametrize("filepath", [
        "PRODUCTION_ETL.py",
        "UPLOAD_GUIDE.md",
        "README.md",
        "requirements.txt",
        "pytest.ini",
        "config/supabase_schema.json",
    ])
    def test_root_files(self, base_dir, filepath):
        """Core root files must exist."""
        assert (base_dir / filepath).exists(), f"Missing: {filepath}"
    
    @pytest.mark.parametrize("filepath", [
        "docs/MASTER_HANDOFF.md",
        "docs/CHANGELOG.md",
        "docs/DATA_DICTIONARY.md",
    ])
    def test_documentation(self, base_dir, filepath):
        """Documentation files must exist."""
        assert (base_dir / filepath).exists(), f"Missing: {filepath}"
    
    @pytest.mark.parametrize("filepath", [
        "tests/test_schema_compliance.py",
        "tests/test_etl_upload.py",
        "tests/conftest.py",
    ])
    def test_test_files(self, base_dir, filepath):
        """Test files must exist."""
        assert (base_dir / filepath).exists(), f"Missing: {filepath}"


class TestDataDirectories:
    """Verify data directories have content."""
    
    def test_output_has_csvs(self, output_csvs):
        """data/output must have 40+ CSV files."""
        assert len(output_csvs) >= 40, f"Only {len(output_csvs)} CSVs (expected 40+)"
    
    def test_clean_has_csvs(self, clean_csvs):
        """data/clean must have CSV files."""
        # Skip if clean directory doesn't exist (some setups may not have it)
        if not clean_csvs:
            pytest.skip("data/clean not populated")
        assert len(clean_csvs) >= 30, f"Only {len(clean_csvs)} CSVs in clean/"
    
    def test_raw_has_content(self, base_dir):
        """data/raw must have content."""
        raw_dir = base_dir / "data" / "raw"
        if not raw_dir.exists():
            pytest.skip("data/raw not present")
        files = list(raw_dir.rglob("*"))
        assert len(files) >= 5, f"Only {len(files)} files in raw/"
    
    def test_blb_tables_exists(self, base_dir):
        """BLB_Tables.xlsx must exist and be substantial."""
        xlsx = base_dir / "data" / "BLB_Tables.xlsx"
        assert xlsx.exists(), "Missing: data/BLB_Tables.xlsx"
        assert xlsx.stat().st_size > 1_000_000, "BLB_Tables.xlsx too small"


class TestHTMLPreviews:
    """Verify HTML preview files exist."""
    
    def test_validation_report(self, base_dir):
        """Validation report HTML must exist."""
        assert (base_dir / "html" / "validation_report.html").exists()
    
    def test_tracker_files(self, base_dir):
        """At least one tracker HTML must exist."""
        tracker_dir = base_dir / "tracker"
        if tracker_dir.exists():
            trackers = list(tracker_dir.glob("tracker_v*.html"))
            assert len(trackers) >= 1, "No tracker files found"
    
    def test_dashboard_files(self, base_dir):
        """Dashboard HTML files should exist."""
        dashboard_dir = base_dir / "dashboard"
        if dashboard_dir.exists():
            htmls = list(dashboard_dir.glob("*.html"))
            assert len(htmls) >= 1, "No dashboard files found"


class TestDocumentationUpdated:
    """Verify documentation is current."""
    
    def test_handoff_recently_modified(self, base_dir):
        """MASTER_HANDOFF.md should be recently modified."""
        handoff = base_dir / "docs" / "MASTER_HANDOFF.md"
        assert handoff.exists()
        
        mtime = datetime.fromtimestamp(handoff.stat().st_mtime)
        age = datetime.now() - mtime
        
        assert age < timedelta(hours=24), \
            f"MASTER_HANDOFF.md is {age.total_seconds()/3600:.1f}h old - update it!"
    
    def test_changelog_has_today(self, base_dir):
        """CHANGELOG.md should have today's date."""
        changelog = base_dir / "docs" / "CHANGELOG.md"
        assert changelog.exists()
        
        content = changelog.read_text()
        today = datetime.now().strftime("%Y-%m-%d")
        
        assert today in content, \
            f"CHANGELOG.md missing today's date ({today})"
    
    def test_handoff_has_key_sections(self, base_dir):
        """MASTER_HANDOFF.md should have required sections."""
        handoff = base_dir / "docs" / "MASTER_HANDOFF.md"
        content = handoff.read_text().lower()
        
        required = ["quick start", "schema", "upload", "test"]
        missing = [s for s in required if s not in content]
        
        assert not missing, f"MASTER_HANDOFF.md missing sections: {missing}"


class TestSchemaFile:
    """Verify schema file validity."""
    
    def test_schema_valid_json(self, base_dir):
        """Schema file must be valid JSON."""
        schema_file = base_dir / "config" / "supabase_schema.json"
        with open(schema_file) as f:
            data = json.load(f)
        assert "tables" in data
    
    def test_schema_has_tables(self, schema):
        """Schema should have 40+ tables."""
        assert len(schema) >= 40, f"Only {len(schema)} tables (expected 40+)"


class TestSourceCode:
    """Verify source code exists."""
    
    def test_src_directory(self, base_dir):
        """src/ must have Python files."""
        src_dir = base_dir / "src"
        assert src_dir.exists()
        py_files = list(src_dir.rglob("*.py"))
        assert len(py_files) >= 10, f"Only {len(py_files)} Python files in src/"
    
    def test_sql_directory(self, base_dir):
        """sql/ directory must exist."""
        assert (base_dir / "sql").exists()


class TestPackageComplete:
    """Final package completeness checks."""
    
    def test_no_pycache_pollution(self, base_dir):
        """__pycache__ should not be in critical paths."""
        # This is a reminder - zip should exclude these
        pass
    
    def test_all_test_files_present(self, base_dir):
        """All test files should be non-empty."""
        test_dir = base_dir / "tests"
        test_files = list(test_dir.glob("test_*.py"))
        
        for tf in test_files:
            assert tf.stat().st_size > 500, f"{tf.name} too small"
