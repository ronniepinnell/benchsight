"""
ETL Validation Module
=====================

Comprehensive validation of ETL output:
- Table existence checks
- Game coverage validation
- Primary key integrity
- Player ID linkage
- No underscore columns
- Referential integrity
"""

import pandas as pd
from pathlib import Path


def validate_all(output_dir=None, valid_tracking_games=None, log=None):
    """
    Comprehensive validation of ETL output.

    Args:
        output_dir: Path to output directory (default: data/output)
        valid_tracking_games: List of valid game IDs to check coverage against
        log: Logger instance

    Returns:
        True if all validations pass, False otherwise
    """
    if output_dir is None:
        output_dir = Path("data/output")
    else:
        output_dir = Path(output_dir)

    if valid_tracking_games is None:
        valid_tracking_games = []

    # Create a simple logger if none provided
    if log is None:
        class SimpleLogger:
            def __init__(self):
                self.warnings = []
                self.errors = []
                self.issues = []

            def info(self, msg):
                print(f"INFO: {msg}")

            def warn(self, msg):
                print(f"WARN: {msg}")
                self.warnings.append(msg)

            def error(self, msg):
                print(f"ERROR: {msg}")
                self.errors.append(msg)

            def issue(self, msg):
                self.issues.append(msg)
                self.warn(f"ISSUE: {msg}")

            def section(self, title):
                print(f"\n{'='*60}")
                print(title)
                print('='*60)

        log = SimpleLogger()

    log.section("PHASE 6: COMPREHENSIVE VALIDATION")

    all_issues = []

    # 1. Check all expected tables exist
    log.info("\n[1] Table existence check:")
    expected_tables = [
        'dim_player', 'dim_team', 'dim_league', 'dim_season', 'dim_schedule',
        'dim_player_role', 'dim_position', 'dim_zone', 'dim_period', 'dim_venue',
        'fact_gameroster', 'fact_events', 'fact_event_players', 'fact_tracking',
        'fact_shifts', 'fact_shift_players', 'fact_shifts',
        'fact_draft', 'fact_registration', 'fact_leadership',
    ]

    for table in expected_tables:
        path = output_dir / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            log.info(f"  {table}: {len(df):,} rows")
        else:
            log.error(f"  {table}: MISSING")
            all_issues.append(f"Missing table: {table}")

    # 2. Check game coverage in tracking tables
    log.info("\n[2] Game coverage (tracking tables):")
    for table in ['fact_events', 'fact_shifts', 'fact_shift_players']:
        path = output_dir / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            games = sorted(df['game_id'].unique().tolist())
            missing = set(valid_tracking_games) - set(games)
            extra = set(games) - set(valid_tracking_games)

            if missing:
                log.error(f"  {table}: missing games {missing}")
                all_issues.append(f"{table}: missing games {missing}")
            elif extra:
                log.warn(f"  {table}: unexpected games {extra}")
            else:
                log.info(f"  {table}: all {len(valid_tracking_games)} games present")

    # 3. Primary key integrity
    log.info("\n[3] Primary key integrity:")
    key_checks = [
        ('dim_player', 'player_id'),
        ('dim_team', 'team_id'),
        ('dim_league', 'league_id'),
        ('dim_season', 'season_id'),
        ('dim_schedule', 'game_id'),
        # fact_gameroster uses composite key (game_id, player_id)
        ('fact_events', 'event_id'),
        ('fact_shifts', 'shift_id'),
        ('fact_shift_players', 'shift_player_id'),
    ]

    for table, pk in key_checks:
        path = output_dir / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            if pk in df.columns:
                nulls = df[pk].isna().sum()
                dups = df.duplicated(subset=[pk]).sum()
                sample = df[pk].dropna().iloc[0] if len(df) > 0 else ""

                if nulls > 0 or dups > 0:
                    log.error(f"  {table}.{pk}: {nulls} NULL, {dups} dups")
                    all_issues.append(f"{table}.{pk}: {nulls} NULL, {dups} dups")
                else:
                    log.info(f"  {table}.{pk}: {sample[:40]}")
            else:
                log.error(f"  {table}: missing column {pk}")
                all_issues.append(f"{table}: missing column {pk}")

    # 4. Player ID linkage
    log.info("\n[4] Player ID linkage:")
    player_tables = ['fact_event_players', 'fact_shift_players', 'fact_gameroster']

    for table in player_tables:
        path = output_dir / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            if 'player_id' in df.columns:
                linked = df['player_id'].notna().sum()
                total = len(df)
                pct = linked / total * 100 if total > 0 else 0

                if pct < 90:
                    log.warn(f"  {table}: {linked:,}/{total:,} ({pct:.1f}%) - LOW")
                    log.issue(f"{table} has only {pct:.1f}% player_id linkage")
                else:
                    log.info(f"  {table}: {linked:,}/{total:,} ({pct:.1f}%)")
            else:
                log.error(f"  {table}: missing player_id column")
                all_issues.append(f"{table}: missing player_id column")

    # 5. No underscore columns
    log.info("\n[5] No underscore columns check:")
    for csv in output_dir.glob("*.csv"):
        try:
            # Check if file is empty or has no columns
            file_size = csv.stat().st_size
            if file_size == 0:
                log.warn(f"  {csv.stem}: empty file (0 bytes)")
                continue

            df = pd.read_csv(csv, dtype=str, nrows=0)

            # Handle case where file has no columns (empty DataFrame)
            if len(df.columns) == 0:
                log.warn(f"  {csv.stem}: no columns in file")
                continue

            underscore_cols = [c for c in df.columns if c.endswith('_')]
            if underscore_cols:
                log.error(f"  {csv.stem}: has underscore cols {underscore_cols[:3]}")
                all_issues.append(f"{csv.stem}: has underscore columns")
            else:
                log.info(f"  {csv.stem}: clean")
        except pd.errors.EmptyDataError:
            log.warn(f"  {csv.stem}: empty file (no columns)")
        except Exception as e:
            log.warn(f"  {csv.stem}: error reading file: {e}")

    # 6. Referential integrity
    log.info("\n[6] Referential integrity:")

    # Check game_id in events exists in schedule
    schedule_path = output_dir / "dim_schedule.csv"
    events_path = output_dir / "fact_events.csv"

    if schedule_path.exists() and events_path.exists():
        schedule = pd.read_csv(schedule_path, dtype=str)
        schedule_games = set(schedule['game_id'].unique())

        events = pd.read_csv(events_path, dtype=str)
        event_games = set(events['game_id'].unique())

        missing_in_schedule = event_games - schedule_games
        if missing_in_schedule:
            log.error(f"  Events have games not in schedule: {missing_in_schedule}")
            all_issues.append(f"Games in events but not schedule: {missing_in_schedule}")
        else:
            log.info(f"  All event games exist in schedule")

    # Summary
    log.section("VALIDATION SUMMARY")

    total_rows = sum(len(pd.read_csv(f, dtype=str)) for f in output_dir.glob("*.csv"))
    table_count = len(list(output_dir.glob("*.csv")))

    log.info(f"Tables: {table_count}")
    log.info(f"Total rows: {total_rows:,}")
    log.info(f"Warnings: {len(log.warnings)}")
    log.info(f"Errors: {len(log.errors)}")
    log.info(f"Issues for review: {len(log.issues)}")

    if all_issues:
        log.error(f"\nCRITICAL ISSUES ({len(all_issues)}):")
        for issue in all_issues:
            log.error(f"  - {issue}")
        return False

    log.info("\n ALL VALIDATIONS PASSED")
    return True
