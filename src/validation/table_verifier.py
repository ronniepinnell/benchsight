#!/usr/bin/env python3
"""
BenchSight Table Verification Framework
Comprehensive validation of ETL output tables.

Usage:
    from src.validation import TableVerifier

    verifier = TableVerifier()
    result = verifier.verify_all()

    if not result.passed:
        for error in result.errors:
            print(error)

Verification Levels:
    CRITICAL - Table existence, PK uniqueness (stops ETL)
    ERROR - Schema mismatch, FK violations (fails validation)
    WARNING - Low row counts (logs only)
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import pandas as pd

logger = logging.getLogger('table_verifier')


class CheckLevel(Enum):
    """Severity levels for verification checks."""
    CRITICAL = 'critical'  # Stops ETL
    ERROR = 'error'        # Fails validation
    WARNING = 'warning'    # Logs only


@dataclass
class CheckResult:
    """Result of a single verification check."""
    check_name: str
    passed: bool
    level: CheckLevel
    message: str
    details: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        status = '✓' if self.passed else ('✗' if self.level != CheckLevel.WARNING else '⚠')
        return f"{status} [{self.check_name}] {self.message}"


@dataclass
class VerificationResult:
    """Aggregated result of all verification checks."""
    checks: List[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """True if no CRITICAL or ERROR checks failed."""
        return not any(
            not c.passed and c.level in (CheckLevel.CRITICAL, CheckLevel.ERROR)
            for c in self.checks
        )

    @property
    def critical_passed(self) -> bool:
        """True if no CRITICAL checks failed."""
        return not any(
            not c.passed and c.level == CheckLevel.CRITICAL
            for c in self.checks
        )

    @property
    def errors(self) -> List[CheckResult]:
        """All failed checks at ERROR or CRITICAL level."""
        return [c for c in self.checks if not c.passed and c.level != CheckLevel.WARNING]

    @property
    def warnings(self) -> List[CheckResult]:
        """All failed checks at WARNING level."""
        return [c for c in self.checks if not c.passed and c.level == CheckLevel.WARNING]

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for c in self.checks if not c.passed)

    def add(self, result: CheckResult):
        self.checks.append(result)

    def summary(self) -> str:
        """Generate a summary report."""
        lines = [
            "=" * 60,
            "TABLE VERIFICATION SUMMARY",
            "=" * 60,
            f"Total Checks: {len(self.checks)}",
            f"Passed: {self.passed_count}",
            f"Failed: {self.failed_count}",
            f"Overall: {'PASSED' if self.passed else 'FAILED'}",
            "=" * 60,
        ]

        if self.errors:
            lines.append("\nCRITICAL/ERROR Issues:")
            for check in self.errors:
                lines.append(f"  {check}")

        if self.warnings:
            lines.append("\nWarnings:")
            for check in self.warnings:
                lines.append(f"  {check}")

        return "\n".join(lines)


class TableVerifier:
    """
    Comprehensive table verification for BenchSight ETL output.

    Validates:
    - Table existence (all expected tables present)
    - Schema correctness (required columns exist)
    - Row count thresholds (minimum expected rows)
    - Primary key uniqueness (no duplicates)
    - Foreign key integrity (all references valid)
    """

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        manifest_path: Optional[Path] = None
    ):
        """
        Initialize the verifier.

        Args:
            output_dir: Path to ETL output CSVs (default: data/output)
            manifest_path: Path to table manifest (default: config/table_manifest.json)
        """
        self.project_root = Path(__file__).parent.parent.parent
        self.output_dir = output_dir or self.project_root / 'data' / 'output'
        self.manifest_path = manifest_path or self.project_root / 'config' / 'table_manifest.json'
        self.manifest = self._load_manifest()
        self._table_cache: Dict[str, pd.DataFrame] = {}

    def _load_manifest(self) -> Dict:
        """Load the table manifest."""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Table manifest not found: {self.manifest_path}")

        with open(self.manifest_path) as f:
            return json.load(f)

    def _get_table(self, table_name: str) -> Optional[pd.DataFrame]:
        """Load a table, using cache if available."""
        if table_name in self._table_cache:
            return self._table_cache[table_name]

        csv_path = self.output_dir / f"{table_name}.csv"
        if not csv_path.exists():
            return None

        try:
            df = pd.read_csv(csv_path, low_memory=False)
            df.columns = [c.lower().strip() for c in df.columns]
            self._table_cache[table_name] = df
            return df
        except Exception as e:
            logger.warning(f"Error reading {table_name}: {e}")
            return None

    def verify_all(self) -> VerificationResult:
        """Run all verification checks."""
        result = VerificationResult()

        # Run checks in order of severity
        result.add(self.check_table_existence())

        # Schema checks for each table
        schema_results = self.check_schemas()
        for check in schema_results:
            result.add(check)

        # Row count checks
        row_results = self.check_row_counts()
        for check in row_results:
            result.add(check)

        # Primary key uniqueness
        pk_results = self.check_primary_keys()
        for check in pk_results:
            result.add(check)

        # Foreign key integrity
        fk_results = self.check_foreign_keys()
        for check in fk_results:
            result.add(check)

        return result

    def check_table_existence(self) -> CheckResult:
        """Verify all expected tables exist as CSV files."""
        expected_tables = set(self.manifest['tables'].keys())
        existing_files = {f.stem for f in self.output_dir.glob('*.csv')}

        missing = expected_tables - existing_files
        extra = existing_files - expected_tables

        if missing:
            return CheckResult(
                check_name='table_existence',
                passed=False,
                level=CheckLevel.CRITICAL,
                message=f"Missing {len(missing)} tables: {sorted(missing)[:5]}{'...' if len(missing) > 5 else ''}",
                details={'missing': sorted(missing), 'extra': sorted(extra)}
            )

        message = f"All {len(expected_tables)} expected tables exist"
        if extra:
            message += f" (+{len(extra)} extra tables)"

        return CheckResult(
            check_name='table_existence',
            passed=True,
            level=CheckLevel.CRITICAL,
            message=message,
            details={'expected': len(expected_tables), 'found': len(existing_files), 'extra': sorted(extra)}
        )

    def check_schemas(self) -> List[CheckResult]:
        """Verify each table has required columns."""
        results = []

        for table_name, table_spec in self.manifest['tables'].items():
            expected_columns = [c.lower() for c in table_spec.get('columns', [])]

            if not expected_columns:
                # Table has no expected schema (empty/placeholder)
                continue

            df = self._get_table(table_name)
            if df is None:
                # Table doesn't exist - handled by existence check
                continue

            actual_columns = set(df.columns)
            expected_set = set(expected_columns)

            missing_cols = expected_set - actual_columns

            if missing_cols:
                results.append(CheckResult(
                    check_name=f'schema_{table_name}',
                    passed=False,
                    level=CheckLevel.ERROR,
                    message=f"{table_name}: missing columns {sorted(missing_cols)[:3]}",
                    details={'missing': sorted(missing_cols)}
                ))
            else:
                results.append(CheckResult(
                    check_name=f'schema_{table_name}',
                    passed=True,
                    level=CheckLevel.ERROR,
                    message=f"{table_name}: schema valid ({len(expected_columns)} columns)"
                ))

        return results

    def check_row_counts(self) -> List[CheckResult]:
        """Verify tables meet minimum row count thresholds."""
        results = []

        for table_name, table_spec in self.manifest['tables'].items():
            min_rows = table_spec.get('min_rows', 0)
            allow_empty = table_spec.get('allow_empty', False)

            df = self._get_table(table_name)
            actual_rows = len(df) if df is not None else 0

            if actual_rows < min_rows and not allow_empty:
                results.append(CheckResult(
                    check_name=f'row_count_{table_name}',
                    passed=False,
                    level=CheckLevel.WARNING,
                    message=f"{table_name}: {actual_rows} rows (expected >= {min_rows})",
                    details={'actual': actual_rows, 'expected': min_rows}
                ))
            elif actual_rows == 0 and not allow_empty:
                results.append(CheckResult(
                    check_name=f'row_count_{table_name}',
                    passed=False,
                    level=CheckLevel.WARNING,
                    message=f"{table_name}: empty table",
                    details={'actual': 0}
                ))

        return results

    def check_primary_keys(self) -> List[CheckResult]:
        """Verify primary key uniqueness in all tables."""
        results = []

        for table_name, table_spec in self.manifest['tables'].items():
            pk = table_spec.get('primary_key')
            if not pk or table_spec.get('skip_pk_check', False):
                continue

            pk = pk.lower()
            df = self._get_table(table_name)
            if df is None or len(df) == 0:
                continue

            if pk not in df.columns:
                # Schema issue - handled elsewhere
                continue

            # Check for duplicates
            duplicates = df[pk].duplicated().sum()

            if duplicates > 0:
                # Get sample of duplicate values
                dup_values = df[df[pk].duplicated(keep=False)][pk].unique()[:5]
                results.append(CheckResult(
                    check_name=f'pk_unique_{table_name}',
                    passed=False,
                    level=CheckLevel.CRITICAL,
                    message=f"{table_name}.{pk}: {duplicates} duplicate keys",
                    details={'duplicates': duplicates, 'sample_values': list(dup_values)}
                ))
            else:
                results.append(CheckResult(
                    check_name=f'pk_unique_{table_name}',
                    passed=True,
                    level=CheckLevel.CRITICAL,
                    message=f"{table_name}.{pk}: unique ({len(df)} rows)"
                ))

        return results

    def check_foreign_keys(self) -> List[CheckResult]:
        """Verify all foreign key values exist in parent tables."""
        results = []

        for table_name, table_spec in self.manifest['tables'].items():
            fks = table_spec.get('foreign_keys')
            if not fks:
                continue

            df = self._get_table(table_name)
            if df is None or len(df) == 0:
                continue

            for fk_col, ref in fks.items():
                fk_col = fk_col.lower()

                if fk_col not in df.columns:
                    continue

                # Parse reference: "parent_table.column"
                parts = ref.split('.')
                if len(parts) != 2:
                    continue

                parent_table, parent_col = parts
                parent_col = parent_col.lower()
                parent_df = self._get_table(parent_table)

                if parent_df is None:
                    results.append(CheckResult(
                        check_name=f'fk_{table_name}_{fk_col}',
                        passed=False,
                        level=CheckLevel.ERROR,
                        message=f"{table_name}.{fk_col}: parent table {parent_table} not found"
                    ))
                    continue

                if parent_col not in parent_df.columns:
                    results.append(CheckResult(
                        check_name=f'fk_{table_name}_{fk_col}',
                        passed=False,
                        level=CheckLevel.ERROR,
                        message=f"{table_name}.{fk_col}: parent column {parent_table}.{parent_col} not found"
                    ))
                    continue

                # Get valid parent values
                valid_values = set(parent_df[parent_col].dropna().unique())

                # Get child values (excluding nulls and common null markers)
                child_values = df[fk_col].dropna()
                null_markers = {0, -1, '', 'null', 'none', 'nan'}
                child_set = set(v for v in child_values.unique()
                               if str(v).lower() not in [str(m) for m in null_markers])

                # Find orphans
                orphans = child_set - valid_values

                if orphans:
                    orphan_sample = list(orphans)[:5]
                    results.append(CheckResult(
                        check_name=f'fk_{table_name}_{fk_col}',
                        passed=False,
                        level=CheckLevel.ERROR,
                        message=f"{table_name}.{fk_col}: {len(orphans)} orphan values referencing {parent_table}",
                        details={'orphan_count': len(orphans), 'sample': orphan_sample}
                    ))
                else:
                    results.append(CheckResult(
                        check_name=f'fk_{table_name}_{fk_col}',
                        passed=True,
                        level=CheckLevel.ERROR,
                        message=f"{table_name}.{fk_col} -> {parent_table}.{parent_col}: valid"
                    ))

        return results

    def check_goal_counts(self) -> CheckResult:
        """
        Special check: Verify goal counting follows the correct rule.

        Goals are ONLY counted when:
            event_type == 'Goal' AND event_detail == 'Goal_Scored'
        """
        events = self._get_table('fact_events')
        if events is None:
            return CheckResult(
                check_name='goal_counting',
                passed=False,
                level=CheckLevel.CRITICAL,
                message="fact_events table not found"
            )

        # Count goals using the correct rule (exact match per CLAUDE.md)
        goal_mask = (
            (events['event_type'].astype(str) == 'Goal') &
            (events['event_detail'].astype(str) == 'Goal_Scored')
        )
        goal_count = goal_mask.sum()

        # Check player stats match
        stats = self._get_table('fact_player_game_stats')
        if stats is not None and 'goals' in stats.columns:
            stats_goals = stats['goals'].sum()

            if stats_goals != goal_count:
                return CheckResult(
                    check_name='goal_counting',
                    passed=False,
                    level=CheckLevel.ERROR,
                    message=f"Goal count mismatch: events={goal_count}, player_stats={stats_goals}",
                    details={'events_goals': goal_count, 'stats_goals': int(stats_goals)}
                )

        return CheckResult(
            check_name='goal_counting',
            passed=True,
            level=CheckLevel.ERROR,
            message=f"Goal counting verified: {goal_count} goals"
        )


def main():
    """Run table verification from command line."""
    import argparse

    parser = argparse.ArgumentParser(description='Verify BenchSight ETL tables')
    parser.add_argument('--output-dir', type=Path, help='Path to output CSVs')
    parser.add_argument('--manifest', type=Path, help='Path to table manifest')
    parser.add_argument('--check', choices=['existence', 'schemas', 'rows', 'pks', 'fks', 'goals'],
                        help='Run specific check only')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    verifier = TableVerifier(
        output_dir=args.output_dir,
        manifest_path=args.manifest
    )

    if args.check:
        # Run specific check
        if args.check == 'existence':
            result = VerificationResult()
            result.add(verifier.check_table_existence())
        elif args.check == 'schemas':
            result = VerificationResult()
            for r in verifier.check_schemas():
                result.add(r)
        elif args.check == 'rows':
            result = VerificationResult()
            for r in verifier.check_row_counts():
                result.add(r)
        elif args.check == 'pks':
            result = VerificationResult()
            for r in verifier.check_primary_keys():
                result.add(r)
        elif args.check == 'fks':
            result = VerificationResult()
            for r in verifier.check_foreign_keys():
                result.add(r)
        elif args.check == 'goals':
            result = VerificationResult()
            result.add(verifier.check_goal_counts())
    else:
        # Run all checks
        result = verifier.verify_all()
        # Also add goal check
        result.add(verifier.check_goal_counts())

    print(result.summary())

    # Exit with appropriate code
    import sys
    sys.exit(0 if result.passed else 1)


if __name__ == '__main__':
    main()
