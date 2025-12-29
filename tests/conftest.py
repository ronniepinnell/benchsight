"""
BenchSight Test Configuration
=============================
Shared fixtures and configuration for all test modules.
"""

import pytest
import json
import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent.parent
SCHEMA_FILE = BASE_DIR / "config" / "supabase_schema.json"
OUTPUT_DIR = BASE_DIR / "data" / "output"
CLEAN_DIR = BASE_DIR / "data" / "clean"
RAW_DIR = BASE_DIR / "data" / "raw"


@pytest.fixture(scope="session")
def base_dir():
    """Project base directory."""
    return BASE_DIR


@pytest.fixture(scope="session")
def schema():
    """Load Supabase schema (cached for session)."""
    if not SCHEMA_FILE.exists():
        pytest.skip(f"Schema file not found: {SCHEMA_FILE}")
    
    with open(SCHEMA_FILE) as f:
        data = json.load(f)
    return data.get("tables", {})


@pytest.fixture(scope="session")
def output_csvs():
    """List of CSV files in data/output."""
    return list(OUTPUT_DIR.glob("*.csv"))


@pytest.fixture(scope="session")
def clean_csvs():
    """List of CSV files in data/clean."""
    return list(CLEAN_DIR.glob("*.csv"))


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing."""
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "value": [10.5, 20.0, None]
    })


def pytest_configure(config):
    """Add custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests requiring external services"
    )
