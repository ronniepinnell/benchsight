"""
TIER 1 TESTS - BLOCKING
=======================
These tests MUST pass for a delivery to be accepted.
If ANY test fails, the package is REJECTED.

Run: pytest tests/test_tier1_blocking.py -v

Tests:
- ETL produces output
- Table count matches ground truth (59)
- Goal count matches immutable facts (17)
- Critical tables exist and are not empty
- No Python syntax errors in source files
"""
import pytest
import pandas as pd
import json
import ast
from pathlib import Path
import sys

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
CONFIG_DIR = PROJECT_ROOT / "config"
SRC_DIR = PROJECT_ROOT / "src"

# Load ground truth
def load_ground_truth():
    gt_file = CONFIG_DIR / "GROUND_TRUTH.json"
    if gt_file.exists():
        with open(gt_file) as f:
            return json.load(f)
    return {}

def load_immutable_facts():
    facts_file = CONFIG_DIR / "IMMUTABLE_FACTS.json"
    if facts_file.exists():
        with open(facts_file) as f:
            return json.load(f)
    return {}


class TestETLProducesOutput:
    """Verify ETL actually produced output."""
    
    def test_output_directory_exists(self):
        """Output directory must exist."""
        assert OUTPUT_DIR.exists(), f"Output directory not found: {OUTPUT_DIR}"
    
    def test_output_has_csv_files(self):
        """Output directory must contain CSV files."""
        csvs = list(OUTPUT_DIR.glob("*.csv"))
        assert len(csvs) > 0, "No CSV files in output directory"


class TestTableCounts:
    """Verify table counts match ground truth."""
    
    def test_total_table_count(self):
        """Total table count must match ground truth."""
        ground_truth = load_ground_truth()
        expected = ground_truth.get('tables', {}).get('total', 59)
        
        actual = len(list(OUTPUT_DIR.glob("*.csv")))
        assert actual == expected, f"Table count mismatch: expected {expected}, got {actual}"
    
    def test_dimension_table_count(self):
        """Dimension table count must be correct."""
        ground_truth = load_ground_truth()
        expected = ground_truth.get('tables', {}).get('dims', 33)
        
        dims = [f for f in OUTPUT_DIR.glob("dim_*.csv")]
        actual = len(dims)
        assert actual == expected, f"Dim tables: expected {expected}, got {actual}"
    
    def test_fact_table_count(self):
        """Fact table count must be correct."""
        ground_truth = load_ground_truth()
        expected = ground_truth.get('tables', {}).get('facts', 24)
        
        facts = [f for f in OUTPUT_DIR.glob("fact_*.csv")]
        actual = len(facts)
        assert actual == expected, f"Fact tables: expected {expected}, got {actual}"
    
    def test_qa_table_count(self):
        """QA table count must be correct."""
        ground_truth = load_ground_truth()
        expected = ground_truth.get('tables', {}).get('qa', 2)
        
        qas = [f for f in OUTPUT_DIR.glob("qa_*.csv")]
        actual = len(qas)
        assert actual == expected, f"QA tables: expected {expected}, got {actual}"


class TestGoalCounts:
    """Verify goal counts match immutable facts (verified against noradhockey.com)."""
    
    @pytest.fixture
    def fact_events(self):
        """Load fact_events.csv."""
        events_file = OUTPUT_DIR / "fact_events.csv"
        if not events_file.exists():
            pytest.fail("fact_events.csv not found")
        return pd.read_csv(events_file)
    
    def test_total_goal_count(self, fact_events):
        """Total goals must match immutable facts."""
        immutable = load_immutable_facts()
        expected = immutable.get('total_goals', 17)
        
        # CRITICAL: Goal counting rule
        # event_type='Goal' AND event_detail='Goal_Scored'
        # Shot_Goal is the SHOT, not the goal!
        goals = fact_events[
            (fact_events['event_type'] == 'Goal') & 
            (fact_events['event_detail'] == 'Goal_Scored')
        ]
        actual = len(goals)
        
        assert actual == expected, (
            f"Goal count mismatch: expected {expected}, got {actual}\n"
            f"Rule: event_type='Goal' AND event_detail='Goal_Scored'"
        )
    
    def test_game_18969_goals(self, fact_events):
        """Game 18969 (Sep 7) should have 7 goals (Platinum 4-3 Velodrome)."""
        goals = fact_events[
            (fact_events['game_id'] == 18969) &
            (fact_events['event_type'] == 'Goal') & 
            (fact_events['event_detail'] == 'Goal_Scored')
        ]
        assert len(goals) == 7, f"Game 18969: expected 7 goals, got {len(goals)}"
    
    def test_game_18977_goals(self, fact_events):
        """Game 18977 (Sep 14) should have 6 goals (HollowBrook 2-4 Velodrome)."""
        goals = fact_events[
            (fact_events['game_id'] == 18977) &
            (fact_events['event_type'] == 'Goal') & 
            (fact_events['event_detail'] == 'Goal_Scored')
        ]
        assert len(goals) == 6, f"Game 18977: expected 6 goals, got {len(goals)}"
    
    def test_game_18981_goals(self, fact_events):
        """Game 18981 (Sep 28) should have 3 goals (Nelson 2-1 Velodrome)."""
        goals = fact_events[
            (fact_events['game_id'] == 18981) &
            (fact_events['event_type'] == 'Goal') & 
            (fact_events['event_detail'] == 'Goal_Scored')
        ]
        assert len(goals) == 3, f"Game 18981: expected 3 goals, got {len(goals)}"
    
    def test_game_18987_goals(self, fact_events):
        """Game 18987 (Oct 5) should have 1 goal (Outlaws 0-1 Velodrome)."""
        goals = fact_events[
            (fact_events['game_id'] == 18987) &
            (fact_events['event_type'] == 'Goal') & 
            (fact_events['event_detail'] == 'Goal_Scored')
        ]
        assert len(goals) == 1, f"Game 18987: expected 1 goal, got {len(goals)}"


class TestCriticalTablesExist:
    """Verify critical tables exist and are not empty."""
    
    # NOTE: These must match actual ETL output
    # Run: ls data/output/*.csv to verify
    CRITICAL_TABLES = [
        'fact_events',
        'fact_event_players', 
        'fact_shifts',
        'fact_shift_players',
        'fact_gameroster',
        'dim_player',
        'dim_team',
        'dim_event_type',
    ]
    
    @pytest.mark.parametrize("table", CRITICAL_TABLES)
    def test_critical_table_exists(self, table):
        """Critical table must exist."""
        table_path = OUTPUT_DIR / f"{table}.csv"
        assert table_path.exists(), f"Critical table missing: {table}"
    
    @pytest.mark.parametrize("table", CRITICAL_TABLES)
    def test_critical_table_not_empty(self, table):
        """Critical table must not be empty."""
        table_path = OUTPUT_DIR / f"{table}.csv"
        if table_path.exists():
            df = pd.read_csv(table_path)
            assert len(df) > 0, f"Critical table is empty: {table}"


class TestSourceCodeValid:
    """Verify source code has no syntax errors."""
    
    def get_python_files(self):
        """Get all Python files in src/."""
        return list(SRC_DIR.rglob("*.py"))
    
    def test_source_files_parse(self):
        """All source files must be valid Python syntax."""
        errors = []
        for py_file in self.get_python_files():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                ast.parse(source)
            except SyntaxError as e:
                errors.append(f"{py_file.name}: {e}")
        
        if errors:
            pytest.fail(f"Syntax errors found:\n" + "\n".join(errors))
    
    def test_test_files_parse(self):
        """All test files must be valid Python syntax."""
        test_dir = PROJECT_ROOT / "tests"
        errors = []
        for py_file in test_dir.glob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                ast.parse(source)
            except SyntaxError as e:
                errors.append(f"{py_file.name}: {e}")
        
        if errors:
            pytest.fail(f"Syntax errors in tests:\n" + "\n".join(errors))


class TestVersionConsistency:
    """Verify version files are consistent."""
    
    def test_version_json_exists(self):
        """VERSION.json must exist."""
        version_file = CONFIG_DIR / "VERSION.json"
        assert version_file.exists(), "config/VERSION.json not found"
    
    def test_immutable_facts_exists(self):
        """IMMUTABLE_FACTS.json must exist."""
        facts_file = CONFIG_DIR / "IMMUTABLE_FACTS.json"
        assert facts_file.exists(), "config/IMMUTABLE_FACTS.json not found"
    
    def test_ground_truth_exists(self):
        """GROUND_TRUTH.json must exist."""
        gt_file = CONFIG_DIR / "GROUND_TRUTH.json"
        assert gt_file.exists(), "config/GROUND_TRUTH.json not found"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
