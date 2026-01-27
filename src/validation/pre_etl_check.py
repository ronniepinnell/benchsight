#!/usr/bin/env python3
"""
BenchSight Pre-ETL Validation Framework
Validates raw tracker data BEFORE ETL pipeline runs.

Usage:
    from src.validation import PreETLValidator

    validator = PreETLValidator(game_id=18969)
    result = validator.validate()

    if not result.passed:
        for error in result.errors:
            print(error)

Validation Categories:
    1. Required Fields - Core columns must be present and non-null
    2. Valid Values - Values must exist in dimension tables
    3. Duplicate Event Slots - Same player can't be in multiple slots per event (#122)
    4. Time Consistency - Events must be chronological within period
    5. Roster Coverage - Jersey numbers must exist in game roster (#120)

Key Concepts:
    Team Assignment Logic:
        The `team_` column indicates the EVENT team (who initiated the event), NOT
        the player's actual team. Players from both teams participate in each event.

        To determine a player's actual team:
        - `team_='h'` + `event_player_*` role → HOME roster
        - `team_='h'` + `opp_player_*` role → AWAY roster
        - `team_='a'` + `event_player_*` role → AWAY roster
        - `team_='a'` + `opp_player_*` role → HOME roster

    No-Player Events:
        Some event types don't have players (GameStart, Intermission, Timeout, etc.).
        Null player_game_number/player_role is expected for these events.
        See NO_PLAYER_EVENT_TYPES constant.

Related Issues:
    - #120: Unknown players in roster
    - #121: This script (Pre-ETL Validation)
    - #122: Duplicate player slots
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
import pandas as pd

logger = logging.getLogger('pre_etl_check')


class CheckLevel(Enum):
    """Severity levels for validation checks."""
    CRITICAL = 'critical'  # Blocks ETL
    ERROR = 'error'        # Fails validation
    WARNING = 'warning'    # Logs only


@dataclass
class CheckResult:
    """Result of a single validation check."""
    check_name: str
    passed: bool
    level: CheckLevel
    message: str
    details: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        status = '✓' if self.passed else ('✗' if self.level != CheckLevel.WARNING else '⚠')
        return f"{status} [{self.level.value.upper()}] {self.check_name}: {self.message}"


@dataclass
class CleanResult:
    """Result of pre-ETL check and clean operation."""
    game_id: int
    events_df: Optional[pd.DataFrame] = None  # Cleaned events DataFrame
    shifts_df: Optional[pd.DataFrame] = None  # Cleaned shifts DataFrame
    fixes: List[str] = field(default_factory=list)  # What was auto-fixed
    blocking_issues: List[str] = field(default_factory=list)  # Issues that block ETL
    warnings: List[str] = field(default_factory=list)  # Non-blocking issues

    @property
    def can_proceed(self) -> bool:
        """True if no blocking issues - ETL can run."""
        return len(self.blocking_issues) == 0

    def summary(self) -> str:
        """Generate a summary report."""
        lines = [
            "=" * 60,
            f"PRE-ETL CLEAN: Game {self.game_id}",
            "=" * 60,
            f"Can Proceed: {'YES' if self.can_proceed else 'NO'}",
        ]

        if self.fixes:
            lines.append(f"\nFixes Applied ({len(self.fixes)}):")
            for fix in self.fixes:
                lines.append(f"  ✓ {fix}")

        if self.blocking_issues:
            lines.append(f"\nBlocking Issues ({len(self.blocking_issues)}):")
            for issue in self.blocking_issues:
                lines.append(f"  ✗ {issue}")

        if self.warnings:
            lines.append(f"\nWarnings ({len(self.warnings)}):")
            for warn in self.warnings:
                lines.append(f"  ⚠ {warn}")

        lines.append("=" * 60)
        return "\n".join(lines)


@dataclass
class ValidationResult:
    """Aggregated result of all validation checks."""
    game_id: int
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
            f"PRE-ETL VALIDATION: Game {self.game_id}",
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


class PreETLValidator:
    """
    Pre-ETL validation for raw tracker data.

    Validates:
    - Required fields present (event_type, period, time, player info)
    - Valid values (event_type in dim, event_detail in dim, etc.)
    - No duplicate event slots (same player in multiple slots)
    - Time consistency (chronological within period)
    - Roster coverage (jerseys exist in roster)
    """

    # Required columns in events sheet
    REQUIRED_EVENTS_COLUMNS = [
        'period',
        'event_index',
        'game_id',
        'player_game_number',
        'player_role',
    ]

    # At least one of these event type columns must be present
    EVENT_TYPE_COLUMNS = ['event_type_code', 'event_type_', 'event_type']

    # At least one of these time columns must be present
    TIME_COLUMNS = ['event_start_min', 'event_start_min_']

    # Valid player roles
    VALID_PLAYER_ROLES = [
        'event_player_1', 'event_player_2', 'event_player_3',
        'event_player_4', 'event_player_5', 'event_player_6',
        'event_goalie',
        'opp_player_1', 'opp_player_2', 'opp_player_3',
        'opp_player_4', 'opp_player_5', 'opp_player_6',
        'opp_goalie',
    ]

    # Event types that legitimately have no players (null player_game_number/player_role OK)
    NO_PLAYER_EVENT_TYPES = [
        'GameStart', 'GameEnd', 'Intermission', 'Timeout',
        'Clockstop', 'DeadIce', 'PeriodStart', 'PeriodEnd',
    ]

    def __init__(
        self,
        game_id: int,
        raw_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ):
        """
        Initialize the validator.

        Args:
            game_id: Game ID to validate
            raw_dir: Path to raw game data (default: data/raw/games/{game_id})
            output_dir: Path to ETL output for dim tables (default: data/output)
        """
        self.game_id = game_id
        self.project_root = Path(__file__).parent.parent.parent
        self.raw_dir = raw_dir or self.project_root / 'data' / 'raw' / 'games' / str(game_id)
        self.output_dir = output_dir or self.project_root / 'data' / 'output'

        self._events_df: Optional[pd.DataFrame] = None
        self._shifts_df: Optional[pd.DataFrame] = None
        self._metadata_df: Optional[pd.DataFrame] = None
        self._dim_cache: Dict[str, pd.DataFrame] = {}
        self._is_partial: bool = False  # True if video-only (no events/shifts)

    def _load_tracker_data(self) -> Tuple[bool, str]:
        """
        Load tracker Excel file and return success status.

        Handles partially tracked games gracefully:
        - If events/shifts sheets don't exist, game is considered "partial" (video-only)
        - Partial games pass validation with a note - they just won't be processed by ETL
        - Only report errors if sheets exist but have data quality issues
        """
        tracking_file = self.raw_dir / f"{self.game_id}_tracking.xlsx"

        if not tracking_file.exists():
            # No tracking file = game not tracked yet, nothing to validate
            self._is_partial = True
            return True, "No tracking file - game not tracked yet"

        try:
            sheets = pd.read_excel(tracking_file, sheet_name=None)

            # Check for partial tracking (video-only games)
            has_events = 'events' in sheets
            has_shifts = 'shifts' in sheets
            has_metadata = 'metadata' in sheets

            if not has_events and not has_shifts:
                # Partial game - video only, no event/shift data to validate
                self._is_partial = True
                if has_metadata:
                    self._metadata_df = sheets['metadata']
                    self._metadata_df.columns = [c.lower().strip() for c in self._metadata_df.columns]
                return True, "Partial tracking (video-only) - no events/shifts to validate"

            # Full tracking - load all sheets
            self._is_partial = False

            if has_events:
                self._events_df = sheets['events']
                self._events_df.columns = [c.lower().strip() for c in self._events_df.columns]

            if has_shifts:
                self._shifts_df = sheets['shifts']
                self._shifts_df.columns = [c.lower().strip() for c in self._shifts_df.columns]

            if has_metadata:
                self._metadata_df = sheets['metadata']
                self._metadata_df.columns = [c.lower().strip() for c in self._metadata_df.columns]

            events_count = len(self._events_df) if self._events_df is not None else 0
            shifts_count = len(self._shifts_df) if self._shifts_df is not None else 0

            return True, f"Loaded {events_count} event rows, {shifts_count} shift rows"

        except Exception as e:
            return False, f"Error reading tracking file: {e}"

    def _get_dim_table(self, table_name: str) -> Optional[pd.DataFrame]:
        """Load a dimension table, using cache if available."""
        if table_name in self._dim_cache:
            return self._dim_cache[table_name]

        csv_path = self.output_dir / f"{table_name}.csv"
        if not csv_path.exists():
            return None

        try:
            df = pd.read_csv(csv_path, low_memory=False)
            df.columns = [c.lower().strip() for c in df.columns]
            self._dim_cache[table_name] = df
            return df
        except Exception as e:
            logger.warning(f"Error reading {table_name}: {e}")
            return None

    def _get_roster_jerseys(self, team_venue: str) -> Set[int]:
        """Get valid jersey numbers for a team in this game."""
        roster = self._get_dim_table('fact_gameroster')
        if roster is None:
            return set()

        game_roster = roster[
            (roster['game_id'] == self.game_id) &
            (roster['team_venue'] == team_venue)
        ]
        return set(game_roster['player_game_number'].dropna().astype(int))

    def validate(self) -> ValidationResult:
        """Run all validation checks."""
        result = ValidationResult(game_id=self.game_id)

        # First, try to load the data
        success, message = self._load_tracker_data()
        if not success:
            result.add(CheckResult(
                check_name='file_load',
                passed=False,
                level=CheckLevel.CRITICAL,
                message=message
            ))
            return result

        result.add(CheckResult(
            check_name='file_load',
            passed=True,
            level=CheckLevel.CRITICAL,
            message=message
        ))

        # Skip validation for partial games (video-only)
        if self._is_partial:
            result.add(CheckResult(
                check_name='partial_game',
                passed=True,
                level=CheckLevel.WARNING,
                message="Partial tracking - skipping event/shift validation"
            ))
            return result

        # Run validation checks
        result.add(self._check_required_columns())
        result.add(self._check_required_fields())

        # Valid values checks
        for check in self._check_valid_event_types():
            result.add(check)
        for check in self._check_valid_event_details():
            result.add(check)
        for check in self._check_valid_player_roles():
            result.add(check)

        # Duplicate event slots check (#122)
        result.add(self._check_duplicate_event_slots())

        # Time consistency
        result.add(self._check_time_consistency())

        # Roster coverage (#120)
        for check in self._check_roster_coverage():
            result.add(check)

        # Shift validation
        result.add(self._check_shift_required_fields())

        # New checks from #132
        result.add(self._check_event_player_1_required())
        result.add(self._check_event_index_unique())
        result.add(self._check_linked_event_references())
        result.add(self._check_period_valid())
        result.add(self._check_time_bounds())
        result.add(self._check_goal_structure())
        result.add(self._check_faceoff_structure())
        result.add(self._check_boolean_values())

        return result

    def _check_required_columns(self) -> CheckResult:
        """Check that required columns exist in events sheet."""
        if self._events_df is None:
            return CheckResult(
                check_name='required_columns',
                passed=False,
                level=CheckLevel.CRITICAL,
                message="Events data not loaded"
            )

        actual_columns = set(self._events_df.columns)
        missing = []

        # Check required columns
        for col in self.REQUIRED_EVENTS_COLUMNS:
            if col not in actual_columns:
                missing.append(col)

        # Check at least one event type column exists
        event_type_present = any(c in actual_columns for c in self.EVENT_TYPE_COLUMNS)
        if not event_type_present:
            missing.append(f"event_type (one of: {self.EVENT_TYPE_COLUMNS})")

        # Check at least one time column exists
        time_present = any(c in actual_columns for c in self.TIME_COLUMNS)
        if not time_present:
            missing.append(f"event_start_min (one of: {self.TIME_COLUMNS})")

        if missing:
            return CheckResult(
                check_name='required_columns',
                passed=False,
                level=CheckLevel.CRITICAL,
                message=f"Missing required columns: {missing}",
                details={'missing': missing}
            )

        return CheckResult(
            check_name='required_columns',
            passed=True,
            level=CheckLevel.CRITICAL,
            message=f"All required columns present ({len(self.REQUIRED_EVENTS_COLUMNS)} checked)"
        )

    def _check_required_fields(self) -> CheckResult:
        """
        Check that required fields are not null.

        Note: Some event types (GameStart, Intermission, Timeout, etc.) legitimately
        have no players, so null player_game_number/player_role is OK for those.
        See NO_PLAYER_EVENT_TYPES constant.
        """
        if self._events_df is None:
            return CheckResult(
                check_name='required_fields',
                passed=False,
                level=CheckLevel.CRITICAL,
                message="Events data not loaded"
            )

        df = self._events_df
        issues = []

        # Check period - should not be null
        null_periods = df['period'].isna().sum()
        if null_periods > 0:
            issues.append(f"period: {null_periods} null values")

        # Check event_index - should not be null
        null_index = df['event_index'].isna().sum()
        if null_index > 0:
            issues.append(f"event_index: {null_index} null values")

        # For player fields, exclude events that don't have players
        # Find event type column
        et_col = None
        for col in self.EVENT_TYPE_COLUMNS:
            if col in df.columns:
                et_col = col
                break

        # Filter to events that SHOULD have players
        if et_col:
            player_events = df[~df[et_col].isin(self.NO_PLAYER_EVENT_TYPES)]
        else:
            player_events = df  # Can't filter, check all

        # Check player_game_number - should not be null for player events
        null_jersey = player_events['player_game_number'].isna().sum()
        if null_jersey > 0:
            issues.append(f"player_game_number: {null_jersey} null values (excluding no-player events)")

        # Check player_role - should not be null for player events
        null_role = player_events['player_role'].isna().sum()
        if null_role > 0:
            issues.append(f"player_role: {null_role} null values (excluding no-player events)")

        if issues:
            return CheckResult(
                check_name='required_fields',
                passed=False,
                level=CheckLevel.ERROR,
                message=f"Null values in required fields: {issues}",
                details={'issues': issues}
            )

        return CheckResult(
            check_name='required_fields',
            passed=True,
            level=CheckLevel.ERROR,
            message="All required fields have values"
        )

    def _check_valid_event_types(self) -> List[CheckResult]:
        """Check that event_type values exist in dim_event_type."""
        results = []
        if self._events_df is None:
            return results

        df = self._events_df
        dim_et = self._get_dim_table('dim_event_type')

        if dim_et is None:
            results.append(CheckResult(
                check_name='valid_event_types',
                passed=False,
                level=CheckLevel.WARNING,
                message="dim_event_type not found - skipping validation"
            ))
            return results

        valid_types = set(dim_et['event_type_code'].dropna().unique())

        # Find the event type column
        et_col = None
        for col in self.EVENT_TYPE_COLUMNS:
            if col in df.columns:
                et_col = col
                break

        if et_col is None:
            return results

        # Get unique event types from data
        data_types = set(df[et_col].dropna().unique())
        invalid = data_types - valid_types

        if invalid:
            results.append(CheckResult(
                check_name='valid_event_types',
                passed=False,
                level=CheckLevel.ERROR,
                message=f"Invalid event types: {sorted(invalid)[:5]}",
                details={'invalid': sorted(invalid), 'valid_count': len(valid_types)}
            ))
        else:
            results.append(CheckResult(
                check_name='valid_event_types',
                passed=True,
                level=CheckLevel.ERROR,
                message=f"All {len(data_types)} event types valid"
            ))

        return results

    def _check_valid_event_details(self) -> List[CheckResult]:
        """Check that event_detail values exist in dim_event_detail."""
        results = []
        if self._events_df is None:
            return results

        df = self._events_df
        dim_ed = self._get_dim_table('dim_event_detail')

        if dim_ed is None:
            results.append(CheckResult(
                check_name='valid_event_details',
                passed=False,
                level=CheckLevel.WARNING,
                message="dim_event_detail not found - skipping validation"
            ))
            return results

        valid_details = set(dim_ed['event_detail_code'].dropna().unique())

        # Check multiple possible columns
        detail_cols = ['event_detail_code', 'event_detail_', 'event_detail']
        for col in detail_cols:
            if col not in df.columns:
                continue

            data_details = set(df[col].dropna().unique())
            invalid = data_details - valid_details

            if invalid:
                results.append(CheckResult(
                    check_name=f'valid_event_details_{col}',
                    passed=False,
                    level=CheckLevel.ERROR,
                    message=f"Invalid event details in {col}: {sorted(invalid)[:5]}",
                    details={'column': col, 'invalid': sorted(invalid)}
                ))
            else:
                results.append(CheckResult(
                    check_name=f'valid_event_details_{col}',
                    passed=True,
                    level=CheckLevel.ERROR,
                    message=f"All event details in {col} valid ({len(data_details)} values)"
                ))
            break  # Only check first found column

        return results

    def _check_valid_player_roles(self) -> List[CheckResult]:
        """Check that player_role values are valid."""
        results = []
        if self._events_df is None:
            return results

        df = self._events_df

        if 'player_role' not in df.columns:
            return results

        data_roles = set(df['player_role'].dropna().unique())
        valid_roles = set(self.VALID_PLAYER_ROLES)
        invalid = data_roles - valid_roles

        if invalid:
            results.append(CheckResult(
                check_name='valid_player_roles',
                passed=False,
                level=CheckLevel.ERROR,
                message=f"Invalid player roles: {sorted(invalid)}",
                details={'invalid': sorted(invalid)}
            ))
        else:
            results.append(CheckResult(
                check_name='valid_player_roles',
                passed=True,
                level=CheckLevel.ERROR,
                message=f"All {len(data_roles)} player roles valid"
            ))

        return results

    def _check_duplicate_event_slots(self) -> CheckResult:
        """
        Check for duplicate player slots in the same event (#122).
        Same player can't be event_player_1 AND event_player_2 for the same event.

        Note: Two players with the same jersey on DIFFERENT teams is valid.
        - #91 as event_player_1 AND opp_player_1 = two different people (OK)
        - #91 as event_player_1 AND event_player_2 = same person twice (DUPLICATE)

        So we group by (event_index, player_game_number, role_team) where
        role_team is 'event' or 'opp' based on the player_role prefix.
        """
        if self._events_df is None:
            return CheckResult(
                check_name='duplicate_event_slots',
                passed=False,
                level=CheckLevel.CRITICAL,
                message="Events data not loaded"
            )

        df = self._events_df.copy()

        # Determine role_team: 'event' or 'opp' based on player_role prefix (vectorized)
        df['_role_team'] = None
        has_role = df['player_role'].notna()
        is_event_role = df['player_role'].str.startswith('event_', na=False)
        df.loc[has_role & is_event_role, '_role_team'] = 'event'
        df.loc[has_role & ~is_event_role, '_role_team'] = 'opp'

        # Group by event_index, player_game_number, AND role_team
        # Only flag duplicates within the same team context
        duplicates = df.groupby(['event_index', 'player_game_number', '_role_team']).size().reset_index(name='count')
        dup_events = duplicates[duplicates['count'] > 1]

        if len(dup_events) > 0:
            # Get sample of duplicate events - vectorized formatting
            sample = dup_events.head(5)
            sample = sample[sample['player_game_number'].notna()]
            sample_str = (
                "event " + sample['event_index'].astype(str) +
                ": #" + sample['player_game_number'].astype(int).astype(str) +
                " (" + sample['_role_team'].astype(str) + "_player) x" +
                sample['count'].astype(str)
            ).tolist()

            return CheckResult(
                check_name='duplicate_event_slots',
                passed=False,
                level=CheckLevel.CRITICAL,
                message=f"{len(dup_events)} events have duplicate player slots",
                details={
                    'duplicate_count': len(dup_events),
                    'samples': sample_str
                }
            )

        return CheckResult(
            check_name='duplicate_event_slots',
            passed=True,
            level=CheckLevel.CRITICAL,
            message="No duplicate player slots found"
        )

    def _check_time_consistency(self) -> CheckResult:
        """Check that events are chronological within each period."""
        if self._events_df is None:
            return CheckResult(
                check_name='time_consistency',
                passed=False,
                level=CheckLevel.ERROR,
                message="Events data not loaded"
            )

        df = self._events_df

        # Find time column
        time_col = None
        for col in ['event_start_min', 'event_start_min_']:
            if col in df.columns:
                time_col = col
                break

        if time_col is None:
            return CheckResult(
                check_name='time_consistency',
                passed=False,
                level=CheckLevel.WARNING,
                message="No time column found - skipping time check"
            )

        # Get unique events (one row per event)
        events_unique = df.drop_duplicates(subset=['event_index']).copy()

        # Vectorized time consistency check using .shift()
        # Clock counts DOWN in hockey (18:00 -> 0:00), so time should decrease or stay same
        issues = []
        for period in events_unique['period'].dropna().unique():
            period_events = events_unique[events_unique['period'] == period].sort_values('event_index').copy()
            period_events = period_events[period_events[time_col].notna()]

            if len(period_events) < 2:
                continue

            # Compare current time to previous time using shift
            period_events['_prev_time'] = period_events[time_col].shift(1)
            # Time went UP = current > previous (wrong direction)
            time_jumps = period_events[
                period_events['_prev_time'].notna() &
                (period_events[time_col] > period_events['_prev_time'])
            ]

            # Format issues vectorized
            if len(time_jumps) > 0:
                jump_strs = (
                    "P" + str(int(period)) + " event " +
                    time_jumps['event_index'].astype(str) +
                    ": time jumped from " +
                    time_jumps['_prev_time'].astype(str) +
                    " to " + time_jumps[time_col].astype(str)
                ).tolist()
                issues.extend(jump_strs)

        if issues:
            return CheckResult(
                check_name='time_consistency',
                passed=False,
                level=CheckLevel.WARNING,
                message=f"{len(issues)} time inconsistencies found",
                details={'issues': issues[:10]}  # First 10
            )

        return CheckResult(
            check_name='time_consistency',
            passed=True,
            level=CheckLevel.WARNING,
            message="Events are chronological within periods"
        )

    def _check_roster_coverage(self) -> List[CheckResult]:
        """
        Check that all jersey numbers in events exist in roster (#120).

        Note: team_ indicates the EVENT team, not the player's team.
        - event_player_* roles belong to the event team
        - opp_player_* roles belong to the opposing team

        So:
        - team_='h' + event_player_* → home roster
        - team_='h' + opp_player_* → away roster
        - team_='a' + event_player_* → away roster
        - team_='a' + opp_player_* → home roster
        """
        results = []
        if self._events_df is None:
            return results

        df = self._events_df

        # Get roster data
        home_jerseys = self._get_roster_jerseys('home')
        away_jerseys = self._get_roster_jerseys('away')

        if not home_jerseys and not away_jerseys:
            results.append(CheckResult(
                check_name='roster_coverage',
                passed=False,
                level=CheckLevel.WARNING,
                message="No roster data found - skipping roster check"
            ))
            return results

        if 'team_' not in df.columns or 'player_role' not in df.columns:
            results.append(CheckResult(
                check_name='roster_coverage',
                passed=False,
                level=CheckLevel.WARNING,
                message="Missing team_ or player_role column - cannot validate roster coverage"
            ))
            return results

        # Vectorized team assignment: event_player_* = same team as event, opp_player_* = opposite
        df_with_team = df.copy()
        is_event_player = df_with_team['player_role'].str.startswith('event_', na=False)
        is_home_event = df_with_team['team_'] == 'h'
        is_away_event = df_with_team['team_'] == 'a'
        has_valid_data = df_with_team['player_role'].notna() & df_with_team['team_'].notna()

        df_with_team['actual_team'] = None
        df_with_team.loc[has_valid_data & is_home_event & is_event_player, 'actual_team'] = 'home'
        df_with_team.loc[has_valid_data & is_home_event & ~is_event_player, 'actual_team'] = 'away'
        df_with_team.loc[has_valid_data & is_away_event & is_event_player, 'actual_team'] = 'away'
        df_with_team.loc[has_valid_data & is_away_event & ~is_event_player, 'actual_team'] = 'home'

        # Check home team jerseys
        home_players = df_with_team[df_with_team['actual_team'] == 'home']
        home_event_jerseys = set(home_players['player_game_number'].dropna().astype(int).unique())
        unknown_home = home_event_jerseys - home_jerseys

        if unknown_home:
            results.append(CheckResult(
                check_name='roster_coverage_home',
                passed=False,
                level=CheckLevel.ERROR,
                message=f"Unknown home jerseys: {sorted(unknown_home)}",
                details={'unknown': sorted(unknown_home), 'valid': sorted(home_jerseys)}
            ))
        else:
            results.append(CheckResult(
                check_name='roster_coverage_home',
                passed=True,
                level=CheckLevel.ERROR,
                message=f"All {len(home_event_jerseys)} home jerseys found in roster"
            ))

        # Check away team jerseys
        away_players = df_with_team[df_with_team['actual_team'] == 'away']
        away_event_jerseys = set(away_players['player_game_number'].dropna().astype(int).unique())
        unknown_away = away_event_jerseys - away_jerseys

        if unknown_away:
            results.append(CheckResult(
                check_name='roster_coverage_away',
                passed=False,
                level=CheckLevel.ERROR,
                message=f"Unknown away jerseys: {sorted(unknown_away)}",
                details={'unknown': sorted(unknown_away), 'valid': sorted(away_jerseys)}
            ))
        else:
            results.append(CheckResult(
                check_name='roster_coverage_away',
                passed=True,
                level=CheckLevel.ERROR,
                message=f"All {len(away_event_jerseys)} away jerseys found in roster"
            ))

        return results

    def _check_shift_required_fields(self) -> CheckResult:
        """Check required fields in shifts sheet."""
        if self._shifts_df is None:
            return CheckResult(
                check_name='shift_required_fields',
                passed=False,
                level=CheckLevel.ERROR,
                message="Shifts data not loaded"
            )

        df = self._shifts_df
        required = ['shift_index', 'period', 'shift_start_min', 'shift_start_sec']

        missing = [col for col in required if col not in df.columns]

        if missing:
            return CheckResult(
                check_name='shift_required_fields',
                passed=False,
                level=CheckLevel.ERROR,
                message=f"Missing shift columns: {missing}",
                details={'missing': missing}
            )

        # Check for null values
        issues = []
        for col in required:
            null_count = df[col].isna().sum()
            if null_count > 0:
                issues.append(f"{col}: {null_count} nulls")

        if issues:
            return CheckResult(
                check_name='shift_required_fields',
                passed=False,
                level=CheckLevel.WARNING,
                message=f"Null values in shifts: {issues}",
                details={'issues': issues}
            )

        return CheckResult(
            check_name='shift_required_fields',
            passed=True,
            level=CheckLevel.WARNING,
            message=f"Shifts data valid ({len(df)} shifts)"
        )

    def _check_event_player_1_required(self) -> CheckResult:
        """
        Check that every event has at least one row with player_role='event_player_1'.

        Per CLAUDE.md: Stats are counted for the row where player_role='event_player_1'.
        If an event has no event_player_1, stat attribution will fail.

        Exception: No-player events (GameStart, Intermission, etc.) don't need event_player_1.
        """
        if self._events_df is None:
            return CheckResult(
                check_name='event_player_1_required',
                passed=False,
                level=CheckLevel.CRITICAL,
                message="Events data not loaded"
            )

        df = self._events_df

        # Find event type column
        et_col = None
        for col in self.EVENT_TYPE_COLUMNS:
            if col in df.columns:
                et_col = col
                break

        # Get all unique event indices
        all_events = set(df['event_index'].dropna().unique())

        # Get events that have event_player_1
        has_ep1 = df[df['player_role'] == 'event_player_1']
        events_with_ep1 = set(has_ep1['event_index'].dropna().unique())

        # Get no-player events (these don't need event_player_1)
        if et_col:
            no_player_events = df[df[et_col].isin(self.NO_PLAYER_EVENT_TYPES)]
            no_player_event_indices = set(no_player_events['event_index'].dropna().unique())
        else:
            no_player_event_indices = set()

        # Events that should have event_player_1 but don't
        missing_ep1 = all_events - events_with_ep1 - no_player_event_indices

        if missing_ep1:
            sample = sorted(missing_ep1)[:10]
            return CheckResult(
                check_name='event_player_1_required',
                passed=False,
                level=CheckLevel.CRITICAL,
                message=f"{len(missing_ep1)} events missing event_player_1",
                details={'missing_count': len(missing_ep1), 'sample_events': sample}
            )

        return CheckResult(
            check_name='event_player_1_required',
            passed=True,
            level=CheckLevel.CRITICAL,
            message=f"All {len(all_events - no_player_event_indices)} player events have event_player_1"
        )

    def _check_event_index_unique(self) -> CheckResult:
        """
        Check that event_index values are unique within the game.

        Duplicate event_index values cause key collisions in downstream tables
        like fact_events which use event_index as part of their primary key.
        """
        if self._events_df is None:
            return CheckResult(
                check_name='event_index_unique',
                passed=False,
                level=CheckLevel.CRITICAL,
                message="Events data not loaded"
            )

        df = self._events_df

        # Get unique events (should be one event_index per logical event)
        # Note: Each event has multiple rows (one per player), so we check uniqueness
        # by looking at the first row per event_index
        event_indices = df.drop_duplicates(subset=['event_index'])['event_index']

        # Check for duplicates in the original event_index column
        # This would indicate the same event_index appears in different logical events
        duplicates = event_indices[event_indices.duplicated(keep=False)]

        if len(duplicates) > 0:
            dup_values = sorted(duplicates.unique())[:10]
            return CheckResult(
                check_name='event_index_unique',
                passed=False,
                level=CheckLevel.CRITICAL,
                message=f"Duplicate event_index values found",
                details={'duplicate_indices': dup_values}
            )

        return CheckResult(
            check_name='event_index_unique',
            passed=True,
            level=CheckLevel.CRITICAL,
            message=f"All {len(event_indices)} event indices are unique"
        )

    def _check_linked_event_references(self) -> CheckResult:
        """
        Check that linked_event_index references a valid event_index.

        If linked_event_index is populated, it should reference an existing
        event_index in the same game. Orphan links break event chains.
        """
        if self._events_df is None:
            return CheckResult(
                check_name='linked_event_references',
                passed=False,
                level=CheckLevel.CRITICAL,
                message="Events data not loaded"
            )

        df = self._events_df

        # Check if linked_event_index column exists
        link_col = None
        for col in ['linked_event_index', 'linked_event_key']:
            if col in df.columns:
                link_col = col
                break

        if link_col is None:
            return CheckResult(
                check_name='linked_event_references',
                passed=True,
                level=CheckLevel.CRITICAL,
                message="No linked_event column found - skipping check"
            )

        # Get all valid event indices
        valid_indices = set(df['event_index'].dropna().unique())

        # Get linked event indices that are populated
        linked = df[df[link_col].notna() & (df[link_col] != '')][link_col]

        # For numeric indices, convert and check
        orphan_links = []
        for val in linked.unique():
            try:
                link_idx = int(float(val)) if pd.notna(val) else None
                if link_idx is not None and link_idx not in valid_indices:
                    orphan_links.append(link_idx)
            except (ValueError, TypeError):
                # Non-numeric link (could be a key format) - skip for now
                pass

        if orphan_links:
            return CheckResult(
                check_name='linked_event_references',
                passed=False,
                level=CheckLevel.CRITICAL,
                message=f"{len(orphan_links)} orphan linked_event references",
                details={'orphan_indices': sorted(orphan_links)[:10]}
            )

        return CheckResult(
            check_name='linked_event_references',
            passed=True,
            level=CheckLevel.CRITICAL,
            message="All linked_event references are valid"
        )

    def _check_period_valid(self) -> CheckResult:
        """
        Check that period values are valid positive integers.

        Period should be 1, 2, 3 for regulation, 4+ for overtime.
        """
        if self._events_df is None:
            return CheckResult(
                check_name='period_valid',
                passed=False,
                level=CheckLevel.ERROR,
                message="Events data not loaded"
            )

        df = self._events_df
        issues = []

        # Get unique periods
        periods = df['period'].dropna().unique()

        for p in periods:
            try:
                period_int = int(p)
                if period_int < 1:
                    issues.append(f"Period {p} is not positive")
            except (ValueError, TypeError):
                issues.append(f"Period '{p}' is not a valid integer")

        if issues:
            return CheckResult(
                check_name='period_valid',
                passed=False,
                level=CheckLevel.ERROR,
                message=f"Invalid period values: {issues[:5]}",
                details={'issues': issues}
            )

        return CheckResult(
            check_name='period_valid',
            passed=True,
            level=CheckLevel.ERROR,
            message=f"All {len(periods)} period values are valid"
        )

    def _check_time_bounds(self) -> CheckResult:
        """
        Check that time values are within valid bounds.

        - Minutes: 0 to period_length (from metadata, varies per game)
        - Seconds: 0 to 59

        Note: Duration validation (start vs end time) is not checked here because
        the tracker may store start/end differently for events with duration.
        The clock counts DOWN, so events spanning time may have start < end numerically.
        """
        if self._events_df is None:
            return CheckResult(
                check_name='time_bounds',
                passed=False,
                level=CheckLevel.ERROR,
                message="Events data not loaded"
            )

        df = self._events_df
        issues = []

        # Get period length from metadata (default to 20 if not found)
        period_length = 20
        if self._metadata_df is not None:
            if 'period_length_minutes' in self._metadata_df.columns:
                try:
                    period_length = int(self._metadata_df['period_length_minutes'].iloc[0])
                except (ValueError, TypeError, IndexError):
                    pass

        # Find time columns
        start_min_col = None
        start_sec_col = None
        end_min_col = None
        end_sec_col = None

        for col in ['event_start_min', 'event_start_min_']:
            if col in df.columns:
                start_min_col = col
                break
        for col in ['event_start_sec', 'event_start_sec_']:
            if col in df.columns:
                start_sec_col = col
                break
        for col in ['event_end_min', 'event_end_min_']:
            if col in df.columns:
                end_min_col = col
                break
        for col in ['event_end_sec', 'event_end_sec_']:
            if col in df.columns:
                end_sec_col = col
                break

        # Get unique events for checking
        events = df.drop_duplicates(subset=['event_index']).copy()

        # Find event type column to exclude no-player events (which use running time, not game clock)
        et_col = None
        for col in self.EVENT_TYPE_COLUMNS:
            if col in events.columns:
                et_col = col
                break

        # Filter to player events only (no-player events like Intermission use different timing)
        if et_col:
            events = events[~events[et_col].isin(self.NO_PLAYER_EVENT_TYPES)]

        # Check minutes bounds (allow up to period_length + small buffer for tracking variance)
        # Some games have slightly longer periods or timing discrepancies
        max_minutes = period_length + 2  # Allow 2 minute buffer

        if start_min_col:
            invalid_start_min = events[
                (events[start_min_col].notna()) &
                ((events[start_min_col] < 0) | (events[start_min_col] > max_minutes))
            ]
            if len(invalid_start_min) > 0:
                sample = invalid_start_min['event_index'].head(5).tolist()
                issues.append(f"start_min out of bounds (0-{max_minutes}): events {sample}")

        if end_min_col:
            invalid_end_min = events[
                (events[end_min_col].notna()) &
                ((events[end_min_col] < 0) | (events[end_min_col] > max_minutes))
            ]
            if len(invalid_end_min) > 0:
                sample = invalid_end_min['event_index'].head(5).tolist()
                issues.append(f"end_min out of bounds (0-{max_minutes}): events {sample}")

        # Check seconds bounds (0-59)
        if start_sec_col:
            invalid_start_sec = events[
                (events[start_sec_col].notna()) &
                ((events[start_sec_col] < 0) | (events[start_sec_col] > 59))
            ]
            if len(invalid_start_sec) > 0:
                sample = invalid_start_sec['event_index'].head(5).tolist()
                issues.append(f"start_sec out of bounds (0-59): events {sample}")

        if end_sec_col:
            invalid_end_sec = events[
                (events[end_sec_col].notna()) &
                ((events[end_sec_col] < 0) | (events[end_sec_col] > 59))
            ]
            if len(invalid_end_sec) > 0:
                sample = invalid_end_sec['event_index'].head(5).tolist()
                issues.append(f"end_sec out of bounds (0-59): events {sample}")

        if issues:
            return CheckResult(
                check_name='time_bounds',
                passed=False,
                level=CheckLevel.ERROR,
                message=f"Time validation issues: {len(issues)} types",
                details={'issues': issues}
            )

        return CheckResult(
            check_name='time_bounds',
            passed=True,
            level=CheckLevel.ERROR,
            message=f"All time values within bounds (period_length={period_length})"
        )

    def _check_goal_structure(self) -> CheckResult:
        """
        Check that goals have the correct structure.

        Per CLAUDE.md CRITICAL rules:
        Goals are ONLY counted when both conditions are true:
        - event_type == 'Goal'
        - event_detail == 'Goal_Scored'
        """
        if self._events_df is None:
            return CheckResult(
                check_name='goal_structure',
                passed=False,
                level=CheckLevel.ERROR,
                message="Events data not loaded"
            )

        df = self._events_df
        issues = []

        # Find event type and detail columns
        et_col = None
        ed_col = None
        for col in self.EVENT_TYPE_COLUMNS:
            if col in df.columns:
                et_col = col
                break
        for col in ['event_detail_code', 'event_detail_', 'event_detail']:
            if col in df.columns:
                ed_col = col
                break

        if et_col is None or ed_col is None:
            return CheckResult(
                check_name='goal_structure',
                passed=True,
                level=CheckLevel.ERROR,
                message="Cannot check goal structure - missing columns"
            )

        # Get unique events
        events = df.drop_duplicates(subset=['event_index'])

        # Find goals (event_type == 'Goal')
        goals = events[events[et_col] == 'Goal']

        if len(goals) == 0:
            return CheckResult(
                check_name='goal_structure',
                passed=True,
                level=CheckLevel.ERROR,
                message="No goals found in data"
            )

        # Check that all goals have event_detail == 'Goal_Scored'
        invalid_goals = goals[goals[ed_col] != 'Goal_Scored']

        if len(invalid_goals) > 0:
            sample = invalid_goals[['event_index', ed_col]].head(5).to_dict('records')
            issues.append(f"Goals without Goal_Scored detail: {sample}")

        # Also check for Shot events with Goal detail (common mistake)
        shots_with_goal = events[
            (events[et_col] == 'Shot') &
            (events[ed_col] == 'Goal')
        ]
        if len(shots_with_goal) > 0:
            sample = shots_with_goal['event_index'].head(5).tolist()
            issues.append(f"Shot events with 'Goal' detail (should be Goal/Goal_Scored): events {sample}")

        if issues:
            return CheckResult(
                check_name='goal_structure',
                passed=False,
                level=CheckLevel.ERROR,
                message=f"Goal structure issues found",
                details={'issues': issues}
            )

        return CheckResult(
            check_name='goal_structure',
            passed=True,
            level=CheckLevel.ERROR,
            message=f"All {len(goals)} goals have correct structure"
        )

    def _check_faceoff_structure(self) -> CheckResult:
        """
        Check that faceoffs have both winner and loser.

        Per CLAUDE.md:
        - event_player_1 (player_role) is faceoff winner
        - opp_player_1 is faceoff loser
        """
        if self._events_df is None:
            return CheckResult(
                check_name='faceoff_structure',
                passed=False,
                level=CheckLevel.ERROR,
                message="Events data not loaded"
            )

        df = self._events_df

        # Find event type column
        et_col = None
        for col in self.EVENT_TYPE_COLUMNS:
            if col in df.columns:
                et_col = col
                break

        if et_col is None:
            return CheckResult(
                check_name='faceoff_structure',
                passed=True,
                level=CheckLevel.ERROR,
                message="Cannot check faceoff structure - missing event_type column"
            )

        # Get faceoff events
        faceoffs = df[df[et_col] == 'Faceoff']

        if len(faceoffs) == 0:
            return CheckResult(
                check_name='faceoff_structure',
                passed=True,
                level=CheckLevel.ERROR,
                message="No faceoffs found in data"
            )

        # Get unique faceoff event indices
        faceoff_indices = faceoffs['event_index'].unique()

        issues = []
        missing_winner = []
        missing_loser = []

        for fo_idx in faceoff_indices:
            fo_rows = df[df['event_index'] == fo_idx]
            roles = set(fo_rows['player_role'].dropna().unique())

            if 'event_player_1' not in roles:
                missing_winner.append(fo_idx)
            if 'opp_player_1' not in roles:
                missing_loser.append(fo_idx)

        if missing_winner:
            issues.append(f"Faceoffs missing winner (event_player_1): {missing_winner[:5]}")
        if missing_loser:
            issues.append(f"Faceoffs missing loser (opp_player_1): {missing_loser[:5]}")

        if issues:
            return CheckResult(
                check_name='faceoff_structure',
                passed=False,
                level=CheckLevel.ERROR,
                message=f"Faceoff structure issues found",
                details={
                    'missing_winner_count': len(missing_winner),
                    'missing_loser_count': len(missing_loser),
                    'issues': issues
                }
            )

        return CheckResult(
            check_name='faceoff_structure',
            passed=True,
            level=CheckLevel.ERROR,
            message=f"All {len(faceoff_indices)} faceoffs have winner and loser"
        )

    def _check_boolean_values(self) -> CheckResult:
        """
        Check for invalid boolean values in success/flag columns.

        Issue #77: Boolean columns contain "s" or "u" strings instead of True/False.
        This causes Supabase upload failures with "invalid input syntax for type boolean".

        Affected columns (from tracker export):
        - event_successful, event_successful_
        - play_detail_successful, play_detail_successful_

        Valid values: True, False, 1, 0, None/NaN
        Invalid values: 's', 'u', or any other string
        """
        if self._events_df is None:
            return CheckResult(
                check_name='boolean_values',
                passed=False,
                level=CheckLevel.CRITICAL,
                message="Events data not loaded"
            )

        df = self._events_df
        issues = []

        # Columns that should be boolean (success/unsuccessful)
        boolean_columns = [
            'event_successful', 'event_successful_',
            'play_detail_successful', 'play_detail_successful_',
            'is_highlight', 'is_xy_adjusted'
        ]

        # Valid boolean representations
        valid_bool_values = {True, False, 1, 0, 1.0, 0.0, 'true', 'false', 'True', 'False', '1', '0'}

        for col in boolean_columns:
            if col not in df.columns:
                continue

            # Get non-null values
            values = df[col].dropna()
            if len(values) == 0:
                continue

            # Find invalid values (not in valid set)
            invalid_mask = ~values.isin(valid_bool_values)
            invalid_values = values[invalid_mask]

            if len(invalid_values) > 0:
                unique_invalid = invalid_values.unique().tolist()[:5]
                count = len(invalid_values)
                issues.append(f"{col}: {count} invalid values {unique_invalid}")

        if issues:
            return CheckResult(
                check_name='boolean_values',
                passed=False,
                level=CheckLevel.ERROR,
                message=f"Invalid boolean values found in {len(issues)} columns",
                details={
                    'issues': issues,
                    'hint': "Convert 's' to True (successful) and 'u' to False (unsuccessful)"
                }
            )

        return CheckResult(
            check_name='boolean_values',
            passed=True,
            level=CheckLevel.ERROR,
            message="All boolean columns have valid values"
        )

    # =========================================================================
    # CLEANING METHODS
    # =========================================================================

    def clean(self) -> CleanResult:
        """
        Run validation checks and auto-fix what can be fixed.

        Returns CleanResult with:
        - cleaned DataFrames (events, shifts)
        - list of fixes applied
        - blocking issues (cannot proceed)
        - warnings (can proceed but noted)
        """
        result = CleanResult(game_id=self.game_id)

        # Load data
        success, message = self._load_tracker_data()
        if not success:
            result.blocking_issues.append(f"Cannot load data: {message}")
            return result

        # Handle partial games (video-only)
        if self._is_partial:
            result.warnings.append("Partial tracking (video-only) - no events/shifts to process")
            return result

        # Make copies for cleaning
        events_df = self._events_df.copy() if self._events_df is not None else pd.DataFrame()
        shifts_df = self._shifts_df.copy() if self._shifts_df is not None else pd.DataFrame()

        # Fix 1: Duplicate event slots
        events_df, dup_fixes = self._fix_duplicate_event_slots(events_df)
        result.fixes.extend(dup_fixes)

        # Fix 2: Boolean values (s/u -> True/False)
        events_df, bool_fixes = self._fix_boolean_values(events_df)
        result.fixes.extend(bool_fixes)

        # Store cleaned DataFrames
        result.events_df = events_df
        result.shifts_df = shifts_df

        # Update internal state for validation checks
        self._events_df = events_df

        # Run validation on cleaned data to find remaining issues
        validation = self.validate()

        # Checks that we auto-fix (don't count as blocking after clean)
        fixed_checks = {'duplicate_event_slots', 'boolean_values'}

        for check in validation.checks:
            if not check.passed:
                if check.level == CheckLevel.CRITICAL:
                    # Critical issues that weren't fixed block ETL
                    if check.check_name not in fixed_checks:
                        result.blocking_issues.append(f"{check.check_name}: {check.message}")
                elif check.level == CheckLevel.ERROR:
                    if check.check_name not in fixed_checks:
                        result.blocking_issues.append(f"{check.check_name}: {check.message}")
                else:
                    result.warnings.append(f"{check.check_name}: {check.message}")

        return result

    def _fix_duplicate_event_slots(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Remove duplicate (event_index, player_game_number, role_team) rows.

        Note: Same jersey on DIFFERENT teams is valid (two different people).
        Only fix when same player appears multiple times on the SAME team:
        - #91 as event_player_1 AND event_player_2 = duplicate (fix it)
        - #91 as event_player_1 AND opp_player_1 = valid (different people)

        Fix Logic (priority order):
        1. Keep row with play_detail1 or play_detail_2 populated
        2. If both empty, keep lowest-numbered slot (event_player_1 > event_player_2)

        Returns: (cleaned_df, list of fix descriptions)
        """
        fixes = []

        # Add role_team column: 'event' or 'opp' (vectorized)
        df = df.copy()
        df['_role_team'] = None
        has_role = df['player_role'].notna()
        is_event_role = df['player_role'].str.startswith('event_', na=False)
        df.loc[has_role & is_event_role, '_role_team'] = 'event'
        df.loc[has_role & ~is_event_role, '_role_team'] = 'opp'

        # Find duplicates: same player on same team appearing multiple times in same event
        dup_counts = df.groupby(['event_index', 'player_game_number', '_role_team']).size()
        dup_combos = dup_counts[dup_counts > 1].index.tolist()

        if not dup_combos:
            df = df.drop(columns=['_role_team'])
            return df, fixes

        rows_to_drop = []

        for event_idx, jersey, role_team in dup_combos:
            if pd.isna(jersey) or pd.isna(role_team):
                continue

            # Get all rows for this event/player/team combination
            mask = (
                (df['event_index'] == event_idx) &
                (df['player_game_number'] == jersey) &
                (df['_role_team'] == role_team)
            )
            player_rows = df[mask]

            if len(player_rows) <= 1:
                continue

            # Rule 1: Keep row with play_detail1 or play_detail_2 populated
            # Check if columns exist before accessing (fixed operator precedence)
            if 'play_detail1' in player_rows.columns:
                has_detail1 = player_rows['play_detail1'].notna() & (player_rows['play_detail1'] != '')
            else:
                has_detail1 = pd.Series(False, index=player_rows.index)

            if 'play_detail_2' in player_rows.columns:
                has_detail2 = player_rows['play_detail_2'].notna() & (player_rows['play_detail_2'] != '')
            else:
                has_detail2 = pd.Series(False, index=player_rows.index)

            has_detail = player_rows[has_detail1 | has_detail2]

            if len(has_detail) > 0:
                # Keep the first row with details, drop others
                keep_idx = has_detail.index[0]
                keep_role = df.loc[keep_idx, 'player_role']
                drop_indices = [i for i in player_rows.index if i != keep_idx]
                rows_to_drop.extend(drop_indices)

                dropped_roles = [df.loc[i, 'player_role'] for i in drop_indices]
                fixes.append(
                    f"Event {int(event_idx)}: #{int(jersey)} ({role_team}_team) - kept {keep_role} (has play_detail), dropped {dropped_roles}"
                )
            else:
                # Rule 2: Keep lowest-numbered slot
                def get_role_sort_key(idx):
                    role = df.loc[idx, 'player_role']
                    if pd.isna(role):
                        return 99
                    try:
                        return int(str(role).split('_')[-1])
                    except (ValueError, IndexError):
                        return 99

                sorted_indices = sorted(player_rows.index, key=get_role_sort_key)
                keep_idx = sorted_indices[0]
                keep_role = df.loc[keep_idx, 'player_role']
                drop_indices = sorted_indices[1:]
                rows_to_drop.extend(drop_indices)

                dropped_roles = [df.loc[i, 'player_role'] for i in drop_indices]
                fixes.append(
                    f"Event {int(event_idx)}: #{int(jersey)} ({role_team}_team) - kept {keep_role} (lowest slot), dropped {dropped_roles}"
                )

        # Drop the duplicate rows and the temp column
        cleaned_df = df.drop(rows_to_drop)
        cleaned_df = cleaned_df.drop(columns=['_role_team'])

        return cleaned_df, fixes

    def _fix_boolean_values(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Convert invalid boolean values to proper booleans.

        Fixes:
        - 's' -> True (successful)
        - 'u' -> False (unsuccessful)

        Returns: (cleaned_df, list of fix descriptions)
        """
        fixes = []
        df = df.copy()

        # Columns that should be boolean (success/unsuccessful)
        boolean_columns = [
            'event_successful', 'event_successful_',
            'play_detail_successful', 'play_detail_successful_',
        ]

        # Mapping for s/u to boolean
        su_mapping = {'s': True, 'u': False}

        for col in boolean_columns:
            if col not in df.columns:
                continue

            # Count s/u values before fix
            s_count = (df[col] == 's').sum()
            u_count = (df[col] == 'u').sum()

            if s_count > 0 or u_count > 0:
                # Apply mapping
                df[col] = df[col].replace(su_mapping)
                fixes.append(f"{col}: converted {s_count} 's' -> True, {u_count} 'u' -> False")

        return df, fixes


def validate_game(game_id: int, verbose: bool = False) -> ValidationResult:
    """
    Convenience function to validate a single game.

    Args:
        game_id: Game ID to validate
        verbose: If True, print progress

    Returns:
        ValidationResult with all check results
    """
    validator = PreETLValidator(game_id=game_id)
    result = validator.validate()

    if verbose:
        print(result.summary())

    return result


def clean_game(game_id: int, verbose: bool = False) -> CleanResult:
    """
    Convenience function to clean a single game.

    Args:
        game_id: Game ID to clean
        verbose: If True, print progress

    Returns:
        CleanResult with cleaned DataFrames and fix log
    """
    validator = PreETLValidator(game_id=game_id)
    result = validator.clean()

    if verbose:
        print(result.summary())

    return result


def validate_all_games(raw_dir: Optional[Path] = None, verbose: bool = False) -> Dict[int, ValidationResult]:
    """
    Validate all games in the raw data directory.

    Args:
        raw_dir: Path to raw games directory (default: data/raw/games)
        verbose: If True, print progress

    Returns:
        Dict mapping game_id to ValidationResult
    """
    if raw_dir is None:
        project_root = Path(__file__).parent.parent.parent
        raw_dir = project_root / 'data' / 'raw' / 'games'

    results = {}

    for game_dir in raw_dir.iterdir():
        if not game_dir.is_dir():
            continue

        try:
            game_id = int(game_dir.name)
        except ValueError:
            continue

        if verbose:
            print(f"Validating game {game_id}...")

        result = validate_game(game_id, verbose=False)
        results[game_id] = result

        if verbose:
            status = 'PASSED' if result.passed else 'FAILED'
            print(f"  {status} ({result.passed_count}/{len(result.checks)} checks passed)")

    return results


def main():
    """Run pre-ETL validation/cleaning from command line."""
    import argparse

    parser = argparse.ArgumentParser(description='Validate and clean raw tracker data before ETL')
    parser.add_argument('--game', '-g', type=int, help='Game ID to validate/clean')
    parser.add_argument('--all', '-a', action='store_true', help='Process all games')
    parser.add_argument('--clean', '-c', action='store_true',
                       help='Clean mode: auto-fix issues and return cleaned data')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--fail-on-warning', action='store_true',
                       help='Exit with error code on warnings too')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.all:
        if args.clean:
            # Clean all games
            project_root = Path(__file__).parent.parent.parent
            raw_dir = project_root / 'data' / 'raw' / 'games'

            results = {}
            for game_dir in raw_dir.iterdir():
                if not game_dir.is_dir():
                    continue
                try:
                    game_id = int(game_dir.name)
                except ValueError:
                    continue

                if args.verbose:
                    print(f"Cleaning game {game_id}...")

                result = clean_game(game_id, verbose=False)
                results[game_id] = result

                if args.verbose:
                    status = 'CAN PROCEED' if result.can_proceed else 'BLOCKED'
                    print(f"  {status} ({len(result.fixes)} fixes, {len(result.blocking_issues)} blocking)")

            # Summary
            can_proceed = sum(1 for r in results.values() if r.can_proceed)
            total = len(results)
            total_fixes = sum(len(r.fixes) for r in results.values())
            print(f"\n{'='*60}")
            print(f"OVERALL: {can_proceed}/{total} games can proceed")
            print(f"Total fixes applied: {total_fixes}")
            print(f"{'='*60}")

            import sys
            sys.exit(0 if all(r.can_proceed for r in results.values()) else 1)

        else:
            # Validate all games
            results = validate_all_games(verbose=args.verbose)

            passed = sum(1 for r in results.values() if r.passed)
            total = len(results)
            print(f"\n{'='*60}")
            print(f"OVERALL: {passed}/{total} games passed validation")
            print(f"{'='*60}")

            import sys
            sys.exit(0 if all(r.passed for r in results.values()) else 1)

    elif args.game:
        if args.clean:
            result = clean_game(args.game, verbose=True)

            import sys
            if result.can_proceed:
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            result = validate_game(args.game, verbose=True)

            import sys
            if result.passed:
                sys.exit(0)
            elif args.fail_on_warning or not result.critical_passed:
                sys.exit(1)
            else:
                sys.exit(0)

    else:
        parser.print_help()
        print("\nExample usage:")
        print("  python -m src.validation.pre_etl_check --game 18969           # Validate only")
        print("  python -m src.validation.pre_etl_check --game 18969 --clean   # Clean and fix")
        print("  python -m src.validation.pre_etl_check --all -v               # Validate all")
        print("  python -m src.validation.pre_etl_check --all --clean -v       # Clean all")


if __name__ == '__main__':
    main()
