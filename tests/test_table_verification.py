#!/usr/bin/env python3
"""
Tests for the Table Verification Framework.

Tests cover:
- Table existence checking
- Schema validation
- Row count thresholds
- Primary key uniqueness
- Foreign key integrity
- Goal counting verification

Usage:
    pytest tests/test_table_verification.py -v
"""

import json
import tempfile
from pathlib import Path
import pandas as pd
import pytest

from src.validation.table_verifier import (
    TableVerifier,
    VerificationResult,
    CheckResult,
    CheckLevel
)


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory with test CSVs."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def temp_manifest(tmp_path):
    """Create a temporary manifest file."""
    manifest = {
        "version": "1.0",
        "total_tables": 3,
        "tables": {
            "dim_player": {
                "type": "dimension",
                "columns": ["player_id", "player_name", "team_id"],
                "primary_key": "player_id",
                "foreign_keys": None,
                "min_rows": 1
            },
            "dim_team": {
                "type": "dimension",
                "columns": ["team_id", "team_name"],
                "primary_key": "team_id",
                "foreign_keys": None,
                "min_rows": 1
            },
            "fact_goals": {
                "type": "fact",
                "columns": ["goal_id", "player_id", "team_id", "game_id"],
                "primary_key": "goal_id",
                "foreign_keys": {
                    "player_id": "dim_player.player_id",
                    "team_id": "dim_team.team_id"
                },
                "min_rows": 0
            }
        }
    }

    manifest_path = tmp_path / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f)

    return manifest_path


class TestCheckResult:
    """Tests for CheckResult dataclass."""

    def test_passed_check_str(self):
        result = CheckResult(
            check_name="test",
            passed=True,
            level=CheckLevel.ERROR,
            message="Test passed"
        )
        assert "✓" in str(result)
        assert "test" in str(result)

    def test_failed_error_str(self):
        result = CheckResult(
            check_name="test",
            passed=False,
            level=CheckLevel.ERROR,
            message="Test failed"
        )
        assert "✗" in str(result)

    def test_failed_warning_str(self):
        result = CheckResult(
            check_name="test",
            passed=False,
            level=CheckLevel.WARNING,
            message="Test warning"
        )
        assert "⚠" in str(result)


class TestVerificationResult:
    """Tests for VerificationResult aggregation."""

    def test_empty_result_passes(self):
        result = VerificationResult()
        assert result.passed
        assert result.passed_count == 0
        assert result.failed_count == 0

    def test_all_passed(self):
        result = VerificationResult()
        result.add(CheckResult("a", True, CheckLevel.ERROR, "ok"))
        result.add(CheckResult("b", True, CheckLevel.CRITICAL, "ok"))
        assert result.passed
        assert result.passed_count == 2
        assert result.failed_count == 0

    def test_warning_does_not_fail(self):
        result = VerificationResult()
        result.add(CheckResult("a", True, CheckLevel.ERROR, "ok"))
        result.add(CheckResult("b", False, CheckLevel.WARNING, "warn"))
        assert result.passed  # Warnings don't fail overall
        assert result.failed_count == 1
        assert len(result.warnings) == 1

    def test_error_fails(self):
        result = VerificationResult()
        result.add(CheckResult("a", True, CheckLevel.ERROR, "ok"))
        result.add(CheckResult("b", False, CheckLevel.ERROR, "fail"))
        assert not result.passed
        assert len(result.errors) == 1

    def test_critical_fails(self):
        result = VerificationResult()
        result.add(CheckResult("a", False, CheckLevel.CRITICAL, "critical"))
        assert not result.passed
        assert not result.critical_passed

    def test_summary_contains_key_info(self):
        result = VerificationResult()
        result.add(CheckResult("pass", True, CheckLevel.ERROR, "ok"))
        result.add(CheckResult("fail", False, CheckLevel.ERROR, "bad"))

        summary = result.summary()
        assert "VERIFICATION SUMMARY" in summary
        assert "Passed: 1" in summary
        assert "Failed: 1" in summary
        assert "FAILED" in summary


class TestTableExistence:
    """Tests for table existence checking."""

    def test_all_tables_exist(self, temp_output_dir, temp_manifest):
        # Create all expected tables
        pd.DataFrame({"player_id": [1], "player_name": ["Test"], "team_id": [1]}).to_csv(
            temp_output_dir / "dim_player.csv", index=False
        )
        pd.DataFrame({"team_id": [1], "team_name": ["Team A"]}).to_csv(
            temp_output_dir / "dim_team.csv", index=False
        )
        pd.DataFrame({"goal_id": [1], "player_id": [1], "team_id": [1], "game_id": [1]}).to_csv(
            temp_output_dir / "fact_goals.csv", index=False
        )

        verifier = TableVerifier(temp_output_dir, temp_manifest)
        result = verifier.check_table_existence()

        assert result.passed
        assert "3" in result.message  # All 3 tables exist

    def test_missing_table(self, temp_output_dir, temp_manifest):
        # Only create some tables
        pd.DataFrame({"player_id": [1], "player_name": ["Test"], "team_id": [1]}).to_csv(
            temp_output_dir / "dim_player.csv", index=False
        )

        verifier = TableVerifier(temp_output_dir, temp_manifest)
        result = verifier.check_table_existence()

        assert not result.passed
        assert result.level == CheckLevel.CRITICAL
        assert "Missing" in result.message


class TestSchemaValidation:
    """Tests for schema validation."""

    def test_valid_schema(self, temp_output_dir, temp_manifest):
        pd.DataFrame({"player_id": [1], "player_name": ["Test"], "team_id": [1]}).to_csv(
            temp_output_dir / "dim_player.csv", index=False
        )
        pd.DataFrame({"team_id": [1], "team_name": ["Team A"]}).to_csv(
            temp_output_dir / "dim_team.csv", index=False
        )
        pd.DataFrame({"goal_id": [1], "player_id": [1], "team_id": [1], "game_id": [1]}).to_csv(
            temp_output_dir / "fact_goals.csv", index=False
        )

        verifier = TableVerifier(temp_output_dir, temp_manifest)
        results = verifier.check_schemas()

        assert all(r.passed for r in results)

    def test_missing_column(self, temp_output_dir, temp_manifest):
        # Create table without required column
        pd.DataFrame({"player_id": [1], "player_name": ["Test"]}).to_csv(  # Missing team_id
            temp_output_dir / "dim_player.csv", index=False
        )

        verifier = TableVerifier(temp_output_dir, temp_manifest)
        results = verifier.check_schemas()

        player_result = [r for r in results if "dim_player" in r.check_name][0]
        assert not player_result.passed
        assert "team_id" in str(player_result.details)


class TestPrimaryKeyUniqueness:
    """Tests for primary key uniqueness checking."""

    def test_unique_keys(self, temp_output_dir, temp_manifest):
        pd.DataFrame({"player_id": [1, 2, 3], "player_name": ["A", "B", "C"], "team_id": [1, 1, 2]}).to_csv(
            temp_output_dir / "dim_player.csv", index=False
        )

        verifier = TableVerifier(temp_output_dir, temp_manifest)
        results = verifier.check_primary_keys()

        player_result = [r for r in results if "dim_player" in r.check_name][0]
        assert player_result.passed

    def test_duplicate_keys(self, temp_output_dir, temp_manifest):
        pd.DataFrame({"player_id": [1, 1, 3], "player_name": ["A", "B", "C"], "team_id": [1, 1, 2]}).to_csv(
            temp_output_dir / "dim_player.csv", index=False
        )

        verifier = TableVerifier(temp_output_dir, temp_manifest)
        results = verifier.check_primary_keys()

        player_result = [r for r in results if "dim_player" in r.check_name][0]
        assert not player_result.passed
        assert player_result.level == CheckLevel.CRITICAL


class TestForeignKeyIntegrity:
    """Tests for foreign key validation."""

    def test_valid_foreign_keys(self, temp_output_dir, temp_manifest):
        pd.DataFrame({"player_id": [1, 2], "player_name": ["A", "B"], "team_id": [1, 2]}).to_csv(
            temp_output_dir / "dim_player.csv", index=False
        )
        pd.DataFrame({"team_id": [1, 2], "team_name": ["Team A", "Team B"]}).to_csv(
            temp_output_dir / "dim_team.csv", index=False
        )
        pd.DataFrame({"goal_id": [1], "player_id": [1], "team_id": [1], "game_id": [100]}).to_csv(
            temp_output_dir / "fact_goals.csv", index=False
        )

        verifier = TableVerifier(temp_output_dir, temp_manifest)
        results = verifier.check_foreign_keys()

        assert all(r.passed for r in results)

    def test_orphan_foreign_key(self, temp_output_dir, temp_manifest):
        pd.DataFrame({"player_id": [1], "player_name": ["A"], "team_id": [1]}).to_csv(
            temp_output_dir / "dim_player.csv", index=False
        )
        pd.DataFrame({"team_id": [1], "team_name": ["Team A"]}).to_csv(
            temp_output_dir / "dim_team.csv", index=False
        )
        pd.DataFrame({"goal_id": [1], "player_id": [999], "team_id": [1], "game_id": [100]}).to_csv(  # player_id 999 doesn't exist
            temp_output_dir / "fact_goals.csv", index=False
        )

        verifier = TableVerifier(temp_output_dir, temp_manifest)
        results = verifier.check_foreign_keys()

        player_fk = [r for r in results if "player_id" in r.check_name][0]
        assert not player_fk.passed
        assert player_fk.level == CheckLevel.ERROR


class TestRowCounts:
    """Tests for row count validation."""

    def test_sufficient_rows(self, temp_output_dir, temp_manifest):
        pd.DataFrame({"player_id": [1, 2], "player_name": ["A", "B"], "team_id": [1, 2]}).to_csv(
            temp_output_dir / "dim_player.csv", index=False
        )

        verifier = TableVerifier(temp_output_dir, temp_manifest)
        results = verifier.check_row_counts()

        # Should not report issues for tables meeting min_rows
        assert not any("dim_player" in r.check_name for r in results if not r.passed)

    def test_empty_table_warning(self, temp_output_dir, temp_manifest):
        # Create empty table
        pd.DataFrame({"player_id": [], "player_name": [], "team_id": []}).to_csv(
            temp_output_dir / "dim_player.csv", index=False
        )

        verifier = TableVerifier(temp_output_dir, temp_manifest)
        results = verifier.check_row_counts()

        player_result = [r for r in results if "dim_player" in r.check_name]
        assert len(player_result) == 1
        assert not player_result[0].passed
        assert player_result[0].level == CheckLevel.WARNING


class TestVerifyAll:
    """Tests for full verification workflow."""

    def test_verify_all_passes(self, temp_output_dir, temp_manifest):
        pd.DataFrame({"player_id": [1, 2], "player_name": ["A", "B"], "team_id": [1, 2]}).to_csv(
            temp_output_dir / "dim_player.csv", index=False
        )
        pd.DataFrame({"team_id": [1, 2], "team_name": ["Team A", "Team B"]}).to_csv(
            temp_output_dir / "dim_team.csv", index=False
        )
        pd.DataFrame({"goal_id": [1], "player_id": [1], "team_id": [1], "game_id": [100]}).to_csv(
            temp_output_dir / "fact_goals.csv", index=False
        )

        verifier = TableVerifier(temp_output_dir, temp_manifest)
        result = verifier.verify_all()

        assert result.passed
        assert result.passed_count > 0

    def test_verify_all_with_issues(self, temp_output_dir, temp_manifest):
        # Create tables with issues
        pd.DataFrame({"player_id": [1, 1], "player_name": ["A", "B"], "team_id": [1, 2]}).to_csv(  # Duplicate PK
            temp_output_dir / "dim_player.csv", index=False
        )
        pd.DataFrame({"team_id": [1], "team_name": ["Team A"]}).to_csv(
            temp_output_dir / "dim_team.csv", index=False
        )
        pd.DataFrame({"goal_id": [1], "player_id": [999], "team_id": [1], "game_id": [100]}).to_csv(  # Orphan FK
            temp_output_dir / "fact_goals.csv", index=False
        )

        verifier = TableVerifier(temp_output_dir, temp_manifest)
        result = verifier.verify_all()

        assert not result.passed
        assert len(result.errors) > 0


class TestGoalCounting:
    """Tests for goal counting verification."""

    def test_goal_counting_no_events(self, temp_output_dir, temp_manifest):
        verifier = TableVerifier(temp_output_dir, temp_manifest)
        result = verifier.check_goal_counts()

        assert not result.passed
        assert "not found" in result.message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
