"""
BenchSight Test Configuration
=============================
Shared fixtures and configuration for all test modules.

ETL Wipe Behavior:
- Use --run-etl flag to run ETL with --wipe before tests
- Use @pytest.mark.needs_etl to mark tests that require fresh ETL output
- Example: pytest --run-etl tests/test_etl.py

Usage:
    pytest tests/                           # Run tests with existing output
    pytest --run-etl tests/                 # Wipe and run ETL first
    pytest --run-etl -m needs_etl tests/    # Only run ETL-dependent tests
"""

import pytest
import json
import subprocess
import sys
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


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-etl",
        action="store_true",
        default=False,
        help="Run ETL with --wipe before tests"
    )
    parser.addoption(
        "--etl-games",
        action="store",
        default=None,
        help="Specific game IDs to process (comma-separated)"
    )


def pytest_configure(config):
    """Add custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests requiring external services"
    )
    config.addinivalue_line(
        "markers", "needs_etl: marks tests that require fresh ETL output"
    )


def pytest_sessionstart(session):
    """Run ETL with --wipe at the start of the test session if requested."""
    if session.config.getoption("--run-etl"):
        print("\n" + "=" * 60)
        print("RUNNING ETL WITH --wipe BEFORE TESTS")
        print("=" * 60)

        cmd = [sys.executable, str(BASE_DIR / "run_etl.py"), "--wipe"]

        # Add specific games if provided
        games = session.config.getoption("--etl-games")
        if games:
            cmd.extend(["--games"] + games.split(","))

        result = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            capture_output=False
        )

        if result.returncode != 0:
            pytest.exit(f"ETL failed with return code {result.returncode}", returncode=1)

        print("=" * 60)
        print("ETL COMPLETE - Starting tests")
        print("=" * 60 + "\n")


@pytest.fixture(scope="session")
def etl_output(request):
    """
    Fixture that ensures ETL output exists.

    If --run-etl was passed, ETL has already run.
    Otherwise, this fixture will fail if critical tables are missing.
    """
    critical_tables = [
        "fact_events.csv",
        "fact_event_players.csv",
        "dim_player.csv",
        "dim_team.csv",
    ]

    missing = [t for t in critical_tables if not (OUTPUT_DIR / t).exists()]

    if missing and not request.config.getoption("--run-etl"):
        pytest.fail(
            f"Missing critical ETL output: {missing}. "
            f"Run with --run-etl to generate fresh output."
        )

    return OUTPUT_DIR


@pytest.fixture(scope="session")
def fresh_etl_output(request):
    """
    Fixture that REQUIRES --run-etl flag.

    Use this for tests that must have freshly generated data.
    """
    if not request.config.getoption("--run-etl"):
        pytest.skip("Test requires --run-etl flag for fresh ETL output")

    return OUTPUT_DIR
