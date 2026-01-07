"""
=============================================================================
DATA INTEGRITY VALIDATOR
=============================================================================
File: src/validators/data_validator.py
Created: 2024-12-30
Author: Production Hardening Sprint

PURPOSE:
    Validate data integrity AFTER loading to catch corruption, constraint
    violations, and data quality issues that slipped through.

WHAT IT VALIDATES:
    1. Primary key integrity (no nulls, no duplicates)
    2. Foreign key integrity (no orphaned records)
    3. Value ranges (non-negative stats, valid percentages)
    4. Row count verification (CSV matches DB)
    5. Referential integrity across tables
    6. Business logic rules (goals <= shots, etc.)

USAGE:
    from src.validators.data_validator import DataValidator, run_all_validations
    
    # Quick validation
    errors = run_all_validations("data/output")
    if errors:
        raise DataIntegrityError("Post-load validation failed", errors=errors)
    
    # Detailed validation
    validator = DataValidator("data/output")
    report = validator.generate_full_report()

WHY THIS EXISTS:
    Even with pre-validation, data can be corrupted by:
    - Race conditions during parallel loads
    - Partial failures leaving inconsistent state
    - Type coercion issues in the database
    - Constraint violations not caught by schema validation

=============================================================================
"""

import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json

from src.exceptions import DataIntegrityError
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    check_name: str
    table_name: str
    passed: bool
    violation_count: int = 0
    sample_violations: List[Any] = field(default_factory=list)
    message: str = ""
    severity: str = "ERROR"  # ERROR, WARNING, INFO
    
    def to_dict(self) -> Dict:
        # Convert numpy types to Python native types for JSON serialization
        def convert(obj):
            if hasattr(obj, 'item'):  # numpy scalar
                return obj.item()
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert(v) for v in obj]
            return obj
        
        return {
            "check_name": self.check_name,
            "table_name": self.table_name,
            "passed": self.passed,
            "violation_count": int(self.violation_count),
            "sample_violations": convert(self.sample_violations[:5]),
            "message": self.message,
            "severity": self.severity
        }


@dataclass
class ValidationReport:
    """Complete validation report for all tables."""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    warning_checks: int = 0
    results: List[ValidationResult] = field(default_factory=list)
    
    @property
    def pass_rate(self) -> float:
        if self.total_checks == 0:
            return 1.0
        return self.passed_checks / self.total_checks
    
    @property
    def is_valid(self) -> bool:
        """True if no ERROR-level failures."""
        return all(
            r.passed or r.severity != "ERROR" 
            for r in self.results
        )
    
    def add_result(self, result: ValidationResult):
        self.results.append(result)
        self.total_checks += 1
        if result.passed:
            self.passed_checks += 1
        elif result.severity == "WARNING":
            self.warning_checks += 1
        else:
            self.failed_checks += 1
    
    def get_failures(self) -> List[ValidationResult]:
        return [r for r in self.results if not r.passed and r.severity == "ERROR"]
    
    def get_warnings(self) -> List[ValidationResult]:
        return [r for r in self.results if not r.passed and r.severity == "WARNING"]
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "summary": {
                "total_checks": self.total_checks,
                "passed": self.passed_checks,
                "failed": self.failed_checks,
                "warnings": self.warning_checks,
                "pass_rate": f"{self.pass_rate:.1%}"
            },
            "is_valid": self.is_valid,
            "failures": [r.to_dict() for r in self.get_failures()],
            "warnings": [r.to_dict() for r in self.get_warnings()]
        }
    
    def save(self, output_path: Path):
        """Save report to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Validation report saved to {output_path}")


class DataValidator:
    """
    Comprehensive data integrity validator.
    
    Runs a suite of validation checks against CSV files in the output directory.
    Can also validate against a live database.
    
    Attributes:
        data_dir: Path to directory containing CSV files
        report: ValidationReport accumulating all results
    """
    
    # Primary key definitions for each table
    PRIMARY_KEYS = {
        "fact_events": "event_key",
        "fact_events_long": "event_player_key",
        "fact_events_player": "event_player_key",
        "fact_events_tracking": "event_tracking_key",
        "fact_shifts": "shift_key",
        "fact_shifts_long": "shift_player_key",
        "fact_shifts_player": "shift_player_key",
        "fact_shifts_tracking": "shift_tracking_key",
        "fact_player_game_stats": "player_game_key",
        "fact_team_game_stats": "team_game_key",
        "fact_goalie_game_stats": "player_game_key",  # Uses player_game_key as PK
        "fact_player_period_stats": "player_period_key",
        "fact_player_stats_long": "player_stat_key",
        "fact_player_boxscore_all": "boxscore_key",
        "fact_gameroster": "roster_key",
        "fact_head_to_head": "matchup_key",
        "fact_h2h": "h2h_key",
        "fact_wowy": "wowy_key",
        "fact_line_combos": "combo_key",  # Actual column name
        "fact_shift_quality": "shift_quality_key",
        "dim_player": "player_id",
        "dim_team": "team_id",
        "dim_schedule": "game_id",
        "dim_season": "season_id",
        "dim_event_type": "event_type_id",
        "dim_period": "period_id",
        "dim_venue": "venue_id",
        "dim_position": "position_id",
        "dim_strength": "strength_id",
    }
    
    # Foreign key relationships: {table: [(fk_column, parent_table, parent_pk)]}
    FOREIGN_KEYS = {
        "fact_events": [
            ("game_id", "dim_schedule", "game_id"),
            ("period_id", "dim_period", "period_id"),
            ("event_type_id", "dim_event_type", "event_type_id"),
        ],
        "fact_events_long": [
            ("game_id", "dim_schedule", "game_id"),
            ("player_id", "dim_player", "player_id"),
        ],
        "fact_shifts": [
            ("game_id", "dim_schedule", "game_id"),
        ],
        "fact_shifts_long": [
            ("game_id", "dim_schedule", "game_id"),
            ("player_id", "dim_player", "player_id"),
        ],
        "fact_player_game_stats": [
            ("game_id", "dim_schedule", "game_id"),
            ("player_id", "dim_player", "player_id"),
        ],
        "fact_gameroster": [
            ("game_id", "dim_schedule", "game_id"),
            ("player_id", "dim_player", "player_id"),
        ],
    }
    
    # Value range validations: {table: [(column, min, max, severity)]}
    VALUE_RANGES = {
        "fact_player_game_stats": [
            ("goals", 0, 20, "ERROR"),
            ("assists", 0, 20, "ERROR"),
            ("shots", 0, 50, "ERROR"),
            ("toi_seconds", 0, 3600, "WARNING"),  # Max 60 min
            ("plus_minus", -20, 20, "WARNING"),
        ],
        "fact_events": [
            ("period", 1, 5, "ERROR"),  # Periods 1-3 + OT
            ("event_index", 0, 10000, "ERROR"),
        ],
        "fact_shifts": [
            ("period", 1, 5, "ERROR"),
            ("shift_index", 0, 500, "ERROR"),
        ],
    }
    
    # Business logic rules: {table: [(check_name, lambda df -> bool_series, severity)]}
    BUSINESS_RULES = {
        "fact_player_game_stats": [
            ("goals_lte_shots", lambda df: df["goals"].fillna(0) <= df["shots"].fillna(0) + 1, "WARNING"),
            ("assists_reasonable", lambda df: df["assists"].fillna(0) <= 10, "WARNING"),
            ("points_equals_goals_plus_assists", 
             lambda df: (df["pts"].fillna(0) == df["goals"].fillna(0) + df["assists"].fillna(0)) | df["pts"].isna(), 
             "ERROR"),
        ],
    }
    
    def __init__(self, data_dir: str = "data/output"):
        """
        Initialize the validator.
        
        Args:
            data_dir: Path to directory containing CSV files
        """
        self.data_dir = Path(data_dir)
        self.report = ValidationReport()
        self._table_cache: Dict[str, pd.DataFrame] = {}
    
    def _load_table(self, table_name: str) -> Optional[pd.DataFrame]:
        """Load a table from CSV, with caching."""
        if table_name in self._table_cache:
            return self._table_cache[table_name]
        
        csv_path = self.data_dir / f"{table_name}.csv"
        if not csv_path.exists():
            return None
        
        df = pd.read_csv(csv_path, dtype=str)
        self._table_cache[table_name] = df
        return df
    
    def validate_primary_key(self, table_name: str) -> ValidationResult:
        """
        Validate primary key has no nulls and no duplicates.
        
        Args:
            table_name: Name of the table to validate
        
        Returns:
            ValidationResult with details of any violations
        """
        pk_column = self.PRIMARY_KEYS.get(table_name)
        if not pk_column:
            return ValidationResult(
                check_name="pk_integrity",
                table_name=table_name,
                passed=True,
                message=f"No PK defined for {table_name}, skipping"
            )
        
        df = self._load_table(table_name)
        if df is None:
            return ValidationResult(
                check_name="pk_integrity",
                table_name=table_name,
                passed=False,
                message=f"Table {table_name} not found",
                severity="WARNING"
            )
        
        if pk_column not in df.columns:
            return ValidationResult(
                check_name="pk_integrity",
                table_name=table_name,
                passed=False,
                message=f"PK column {pk_column} not found in {table_name}",
                severity="ERROR"
            )
        
        violations = []
        
        # Check for nulls
        null_count = df[pk_column].isna().sum()
        if null_count > 0:
            violations.append(f"{null_count} null values")
        
        # Check for empty strings
        empty_count = (df[pk_column] == "").sum()
        if empty_count > 0:
            violations.append(f"{empty_count} empty strings")
        
        # Check for duplicates
        dup_count = df[pk_column].duplicated().sum()
        if dup_count > 0:
            dup_values = df[df[pk_column].duplicated(keep=False)][pk_column].unique()[:5]
            violations.append(f"{dup_count} duplicates (samples: {list(dup_values)})")
        
        if violations:
            return ValidationResult(
                check_name="pk_integrity",
                table_name=table_name,
                passed=False,
                violation_count=null_count + empty_count + dup_count,
                sample_violations=violations,
                message=f"PK {pk_column}: {', '.join(violations)}",
                severity="ERROR"
            )
        
        return ValidationResult(
            check_name="pk_integrity",
            table_name=table_name,
            passed=True,
            message=f"PK {pk_column} valid ({len(df)} rows)"
        )
    
    def validate_foreign_keys(self, table_name: str) -> List[ValidationResult]:
        """
        Validate all foreign key relationships for a table.
        
        Args:
            table_name: Name of the table to validate
        
        Returns:
            List of ValidationResults, one per FK relationship
        """
        results = []
        fk_definitions = self.FOREIGN_KEYS.get(table_name, [])
        
        if not fk_definitions:
            return results
        
        df = self._load_table(table_name)
        if df is None:
            return results
        
        for fk_column, parent_table, parent_pk in fk_definitions:
            parent_df = self._load_table(parent_table)
            
            if parent_df is None:
                results.append(ValidationResult(
                    check_name=f"fk_{fk_column}",
                    table_name=table_name,
                    passed=False,
                    message=f"Parent table {parent_table} not found",
                    severity="WARNING"
                ))
                continue
            
            if fk_column not in df.columns:
                results.append(ValidationResult(
                    check_name=f"fk_{fk_column}",
                    table_name=table_name,
                    passed=True,
                    message=f"FK column {fk_column} not in table, skipping"
                ))
                continue
            
            if parent_pk not in parent_df.columns:
                results.append(ValidationResult(
                    check_name=f"fk_{fk_column}",
                    table_name=table_name,
                    passed=False,
                    message=f"Parent PK {parent_pk} not found in {parent_table}",
                    severity="ERROR"
                ))
                continue
            
            # Find orphaned records
            valid_values = set(parent_df[parent_pk].dropna().unique())
            child_values = df[fk_column].dropna()
            orphans = child_values[~child_values.isin(valid_values)]
            
            if len(orphans) > 0:
                orphan_samples = orphans.unique()[:5].tolist()
                results.append(ValidationResult(
                    check_name=f"fk_{fk_column}",
                    table_name=table_name,
                    passed=False,
                    violation_count=len(orphans),
                    sample_violations=orphan_samples,
                    message=f"FK {fk_column} -> {parent_table}: {len(orphans)} orphaned records",
                    severity="ERROR"
                ))
            else:
                results.append(ValidationResult(
                    check_name=f"fk_{fk_column}",
                    table_name=table_name,
                    passed=True,
                    message=f"FK {fk_column} -> {parent_table}: valid"
                ))
        
        return results
    
    def validate_value_ranges(self, table_name: str) -> List[ValidationResult]:
        """
        Validate numeric columns are within expected ranges.
        
        Args:
            table_name: Name of the table to validate
        
        Returns:
            List of ValidationResults, one per range check
        """
        results = []
        range_checks = self.VALUE_RANGES.get(table_name, [])
        
        if not range_checks:
            return results
        
        df = self._load_table(table_name)
        if df is None:
            return results
        
        for column, min_val, max_val, severity in range_checks:
            if column not in df.columns:
                continue
            
            # Convert to numeric
            numeric_col = pd.to_numeric(df[column], errors='coerce')
            
            # Find out of range values
            below_min = numeric_col < min_val
            above_max = numeric_col > max_val
            out_of_range = below_min | above_max
            
            violation_count = out_of_range.sum()
            
            if violation_count > 0:
                sample_values = df[out_of_range][column].head(5).tolist()
                results.append(ValidationResult(
                    check_name=f"range_{column}",
                    table_name=table_name,
                    passed=False,
                    violation_count=violation_count,
                    sample_violations=sample_values,
                    message=f"Column {column}: {violation_count} values outside [{min_val}, {max_val}]",
                    severity=severity
                ))
            else:
                results.append(ValidationResult(
                    check_name=f"range_{column}",
                    table_name=table_name,
                    passed=True,
                    message=f"Column {column}: all values in [{min_val}, {max_val}]"
                ))
        
        return results
    
    def validate_business_rules(self, table_name: str) -> List[ValidationResult]:
        """
        Validate business logic rules.
        
        Args:
            table_name: Name of the table to validate
        
        Returns:
            List of ValidationResults, one per rule
        """
        results = []
        rules = self.BUSINESS_RULES.get(table_name, [])
        
        if not rules:
            return results
        
        df = self._load_table(table_name)
        if df is None:
            return results
        
        # Convert numeric columns
        numeric_cols = ["goals", "assists", "pts", "shots", "toi_seconds"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        for rule_name, check_func, severity in rules:
            try:
                valid_mask = check_func(df)
                violation_count = (~valid_mask).sum()
                
                if violation_count > 0:
                    # Get sample violations
                    violations_df = df[~valid_mask].head(5)
                    samples = violations_df.to_dict('records')
                    
                    results.append(ValidationResult(
                        check_name=f"rule_{rule_name}",
                        table_name=table_name,
                        passed=False,
                        violation_count=violation_count,
                        sample_violations=samples,
                        message=f"Business rule '{rule_name}' violated by {violation_count} rows",
                        severity=severity
                    ))
                else:
                    results.append(ValidationResult(
                        check_name=f"rule_{rule_name}",
                        table_name=table_name,
                        passed=True,
                        message=f"Business rule '{rule_name}' passed"
                    ))
            except Exception as e:
                results.append(ValidationResult(
                    check_name=f"rule_{rule_name}",
                    table_name=table_name,
                    passed=False,
                    message=f"Error checking rule '{rule_name}': {e}",
                    severity="WARNING"
                ))
        
        return results
    
    def validate_row_counts(self, expected_counts: Dict[str, int]) -> List[ValidationResult]:
        """
        Validate row counts match expected values.
        
        Args:
            expected_counts: Dict of {table_name: expected_row_count}
        
        Returns:
            List of ValidationResults
        """
        results = []
        
        for table_name, expected in expected_counts.items():
            df = self._load_table(table_name)
            
            if df is None:
                results.append(ValidationResult(
                    check_name="row_count",
                    table_name=table_name,
                    passed=False,
                    message=f"Table not found, expected {expected} rows",
                    severity="ERROR"
                ))
                continue
            
            actual = len(df)
            if actual != expected:
                results.append(ValidationResult(
                    check_name="row_count",
                    table_name=table_name,
                    passed=False,
                    violation_count=abs(actual - expected),
                    message=f"Row count mismatch: expected {expected}, got {actual}",
                    severity="ERROR"
                ))
            else:
                results.append(ValidationResult(
                    check_name="row_count",
                    table_name=table_name,
                    passed=True,
                    message=f"Row count matches: {actual}"
                ))
        
        return results
    
    def validate_table(self, table_name: str) -> List[ValidationResult]:
        """
        Run all validations for a single table.
        
        Args:
            table_name: Name of the table to validate
        
        Returns:
            List of all ValidationResults for the table
        """
        results = []
        
        # Primary key
        results.append(self.validate_primary_key(table_name))
        
        # Foreign keys
        results.extend(self.validate_foreign_keys(table_name))
        
        # Value ranges
        results.extend(self.validate_value_ranges(table_name))
        
        # Business rules
        results.extend(self.validate_business_rules(table_name))
        
        return results
    
    def validate_all(self) -> ValidationReport:
        """
        Run all validations on all tables.
        
        Returns:
            Complete ValidationReport
        """
        self.report = ValidationReport()
        self._table_cache.clear()
        
        # Get all CSV files
        csv_files = list(self.data_dir.glob("*.csv"))
        table_names = [f.stem for f in csv_files]
        
        logger.info(f"Validating {len(table_names)} tables...")
        
        for table_name in sorted(table_names):
            results = self.validate_table(table_name)
            for result in results:
                self.report.add_result(result)
        
        # Log summary
        logger.info(
            f"Validation complete: {self.report.passed_checks}/{self.report.total_checks} passed "
            f"({self.report.pass_rate:.1%}), {self.report.failed_checks} failures, "
            f"{self.report.warning_checks} warnings"
        )
        
        return self.report
    
    def generate_full_report(self, output_path: Path = None) -> ValidationReport:
        """
        Generate and optionally save a full validation report.
        
        Args:
            output_path: Optional path to save JSON report
        
        Returns:
            ValidationReport
        """
        report = self.validate_all()
        
        if output_path:
            report.save(output_path)
        
        return report


def run_all_validations(data_dir: str = "data/output") -> List[str]:
    """
    Convenience function to run all validations and return error messages.
    
    Args:
        data_dir: Path to output directory
    
    Returns:
        List of error messages (empty if all passed)
    
    Raises:
        DataIntegrityError: If validation fails and raise_on_failure is True
    """
    validator = DataValidator(data_dir)
    report = validator.validate_all()
    
    errors = []
    for failure in report.get_failures():
        errors.append(f"{failure.table_name}.{failure.check_name}: {failure.message}")
    
    return errors


def validate_after_load(table_name: str, expected_row_count: int = None,
                        data_dir: str = "data/output") -> Tuple[bool, List[str]]:
    """
    Validate a specific table after loading.
    
    Args:
        table_name: Name of the table to validate
        expected_row_count: Optional expected row count
        data_dir: Path to output directory
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    validator = DataValidator(data_dir)
    results = validator.validate_table(table_name)
    
    if expected_row_count is not None:
        count_results = validator.validate_row_counts({table_name: expected_row_count})
        results.extend(count_results)
    
    errors = [r.message for r in results if not r.passed and r.severity == "ERROR"]
    return len(errors) == 0, errors
