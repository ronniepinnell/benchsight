#!/usr/bin/env python3
"""
================================================================================
BENCHSIGHT ETL - SINGLE SOURCE OF TRUTH
================================================================================

THIS IS THE ONLY FILE YOU SHOULD RUN FOR ETL.

Creates 128 tables including:
- 55 dimension tables (dim_*)
- 65 fact tables (fact_*)
- 4 QA tables (qa_*)
- 1 lookup table

Usage:
    python run_etl.py              # Full ETL (~80 seconds, 128 tables)
    python run_etl.py --wipe       # CLEAN SLATE: Delete all output then run ETL
    python run_etl.py --validate   # Check all tables exist
    python run_etl.py --status     # Show current status

IMPORTANT: Use --wipe when:
- Starting fresh after code changes
- Debugging table issues
- Ensuring no orphan tables exist

After running, verify with:
    python scripts/bs_detector_v2.py    # Must show 16 goals, 128 tables

Version: 22.1
Date: January 10, 2026

See docs/CODEBASE_GUIDE.md for complete documentation.
================================================================================
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import traceback

# Ensure we can import from src
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Paths
OUTPUT_DIR = PROJECT_ROOT / 'data' / 'output'
EXPECTED_TABLE_COUNT = 138  # Minimum required (v28.3: 142-3 deprecated = 139)


def log(msg, level="INFO"):
    """Simple logging."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {msg}")


def log_phase(phase_num, phase_name):
    """Log phase header."""
    print()
    print("=" * 70)
    print(f"PHASE {phase_num}: {phase_name}")
    print("=" * 70)


def count_tables():
    """Count CSV files in output."""
    return len(list(OUTPUT_DIR.glob('*.csv')))


def table_exists(name):
    """Check if table exists."""
    return (OUTPUT_DIR / f"{name}.csv").exists()


def run_full_etl():
    """
    Run the complete ETL pipeline.
    
    This is THE function that creates all tables.
    """
    start_time = datetime.now()
    
    print()
    print("=" * 70)
    print("BENCHSIGHT ETL v12.02 - FULL RUN")
    print(f"Started: {start_time.isoformat()}")
    print("=" * 70)
    
    # Ensure output dir exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    errors = []
    
    # =========================================================================
    # PHASE 1 & 2 & 3: Base ETL (BLB data + Tracking + Derived tables)
    # =========================================================================
    log_phase(1, "BASE ETL (BLB + Tracking + Derived Tables)")
    try:
        from src.core.base_etl import main as run_base_etl
        run_base_etl()
        log(f"Base ETL complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"Base ETL: {e}")
        log(f"Base ETL FAILED: {e}", "ERROR")
        traceback.print_exc()
        return False  # Can't continue without base
    
    # =========================================================================
    # PHASE 3B: Static Dimension Tables
    # =========================================================================
    log_phase("3B", "STATIC DIMENSION TABLES")
    try:
        from src.tables.dimension_tables import create_all_dimension_tables
        create_all_dimension_tables()
        log(f"Dimension tables complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"Dimension tables: {e}")
        log(f"Dimension tables FAILED: {e}", "ERROR")
    
    # =========================================================================
    # PHASE 4: Core Player Stats
    # =========================================================================
    log_phase(4, "CORE PLAYER STATS")
    try:
        from src.tables.core_facts import create_all_core_facts
        create_all_core_facts()
        log(f"Player stats complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"Player stats: {e}")
        log(f"Player stats FAILED: {e}", "ERROR")
    
    # =========================================================================
    # PHASE 4B: Shift Analytics (H2H, WOWY, Line Combos, Shift Quality)
    # =========================================================================
    log_phase("4B", "SHIFT ANALYTICS")
    try:
        from src.tables.shift_analytics import create_all_shift_analytics
        create_all_shift_analytics()
        log(f"Shift analytics complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"Shift analytics: {e}")
        log(f"Shift analytics FAILED: {e}", "ERROR")
    
    # =========================================================================
    # PHASE 4C: Remaining Fact Tables
    # =========================================================================
    log_phase("4C", "REMAINING FACT TABLES")
    try:
        from src.tables.remaining_facts import build_remaining_tables
        build_remaining_tables(verbose=True)
        log(f"Remaining tables complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"Remaining tables: {e}")
        log(f"Remaining tables FAILED: {e}", "ERROR")
    
    # =========================================================================
    # PHASE 4D: Event Analytics (Rush Events, Shot Chains, Linked Events)
    # =========================================================================
    log_phase("4D", "EVENT ANALYTICS")
    try:
        from src.tables.event_analytics import create_all_event_analytics
        create_all_event_analytics()
        log(f"Event analytics complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"Event analytics: {e}")
        log(f"Event analytics FAILED: {e}", "ERROR")
    
    # =========================================================================
    # PHASE 4E: Shot Chain Builder
    # =========================================================================
    log_phase("4E", "SHOT CHAINS")
    try:
        from src.chains.shot_chain_builder import build_shot_chains
        result = build_shot_chains()
        if result is not None:
            log(f"Shot chains complete: {count_tables()} tables")
        else:
            log("Shot chains: No chains built (check source data)")
    except Exception as e:
        errors.append(f"Shot chains: {e}")
        log(f"Shot chains FAILED: {e}", "ERROR")
    
    # =========================================================================
    # PHASE 5: Add Foreign Keys & Create Additional Tables
    # =========================================================================
    log_phase(5, "FOREIGN KEYS & ADDITIONAL TABLES")
    try:
        from src.core.add_all_fkeys import main as add_fkeys
        add_fkeys()
        log(f"Foreign keys complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"Foreign keys: {e}")
        log(f"Foreign keys FAILED: {e}", "ERROR")
    
    # =========================================================================
    # PHASE 6: Extended Tables
    # =========================================================================
    log_phase(6, "EXTENDED TABLES")
    try:
        from src.advanced.extended_tables import create_extended_tables
        create_extended_tables()
        log(f"Extended tables complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"Extended tables: {e}")
        log(f"Extended tables FAILED: {e}", "ERROR")
    
    # =========================================================================
    # PHASE 7: Post Processing
    # =========================================================================
    log_phase(7, "POST PROCESSING")
    try:
        from src.etl.post_etl_processor import main as post_process
        post_process()
        log(f"Post processing complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"Post processing: {e}")
        log(f"Post processing FAILED: {e}", "WARN")
    
    # =========================================================================
    # PHASE 8: Event Time Context
    # =========================================================================
    log_phase(8, "EVENT TIME CONTEXT")
    try:
        from src.advanced.event_time_context import enhance_event_tables
        enhance_event_tables()
        log(f"Event time context complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"Event time context: {e}")
        log(f"Event time context FAILED: {e}", "WARN")
    
    # =========================================================================
    # PHASE 9: QA Tables (BEFORE v11 - creates fact_game_status)
    # =========================================================================
    log_phase(9, "QA TABLES")
    try:
        from src.qa.build_qa_facts import main as build_qa
        build_qa()
        log(f"QA tables complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"QA tables: {e}")
        log(f"QA tables FAILED: {e}", "WARN")
    
    # =========================================================================
    # PHASE 10: V11 Enhancements (AFTER QA - uses fact_game_status)
    # =========================================================================
    log_phase(10, "V11 ENHANCEMENTS")
    try:
        from src.advanced.v11_enhancements import run_all_enhancements
        run_all_enhancements()
        log(f"V11 enhancements complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"V11 enhancements: {e}")
        log(f"V11 enhancements FAILED: {e}", "WARN")
    
    # =========================================================================
    # PHASE 10B: XY Tables & Spatial Analytics
    # =========================================================================
    log_phase("10B", "XY TABLES & SPATIAL ANALYTICS")
    try:
        from src.xy.xy_table_builder import build_all_xy_tables
        build_all_xy_tables()
        log(f"XY tables complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"XY tables: {e}")
        log(f"XY tables FAILED: {e}", "WARN")
    
    # =========================================================================
    # PHASE 11: MACRO STATS (Season/Career Aggregations)
    # =========================================================================
    log_phase("11", "MACRO STATS (Basic & Advanced)")
    try:
        from src.tables.macro_stats import create_all_macro_stats
        create_all_macro_stats()
        log(f"Macro stats complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"Macro stats: {e}")
        log(f"Macro stats FAILED: {e}", "WARN")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    final_count = count_tables()
    
    print()
    print("=" * 70)
    print("ETL COMPLETE")
    print("=" * 70)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Tables created: {final_count}")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nErrors encountered:")
        for err in errors:
            print(f"  - {err}")
    
    if final_count < EXPECTED_TABLE_COUNT:
        print(f"\n⚠️  WARNING: Only {final_count} tables created, expected {EXPECTED_TABLE_COUNT}+")
        return False
    
    print(f"\n✓ ETL successful: {final_count} tables created")
    return True




def validate():
    """Validate all tables exist."""
    count = count_tables()
    print(f"\nTable count: {count}")
    
    critical = [
        'fact_events', 'fact_event_players', 'fact_shifts', 
        'fact_shift_players',
        'dim_player', 'dim_team', 'dim_schedule',
    ]
    
    print("\nCritical tables:")
    missing = []
    for t in critical:
        exists = table_exists(t)
        status = "✓" if exists else "✗ MISSING"
        print(f"  {status} {t}")
        if not exists:
            missing.append(t)
    
    if missing:
        print(f"\n❌ VALIDATION FAILED: Missing {len(missing)} critical tables")
        return False
    
    if count < EXPECTED_TABLE_COUNT:
        print(f"\n⚠️  WARNING: Only {count} tables, expected {EXPECTED_TABLE_COUNT}+")
        return False
    
    print(f"\n✓ VALIDATION PASSED: {count} tables present")
    return True


def status():
    """Show current status."""
    count = count_tables()
    print(f"\nBenchSight ETL Status")
    print(f"=" * 40)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Tables present: {count}")
    print(f"Expected minimum: {EXPECTED_TABLE_COUNT}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='BenchSight ETL - Single Source of Truth',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_etl.py                     Full ETL (all games, all tables)
  python run_etl.py --wipe              Clean slate then full ETL
  python run_etl.py --list-games        List available game IDs
  python run_etl.py --games 18969 18977 Process only specific games
  python run_etl.py --validate          Validate tables exist
  python run_etl.py --status            Show current status

This is THE ONLY file you should run for ETL.
        """
    )
    
    # Action modes
    parser.add_argument('--validate', action='store_true', 
                        help='Validate tables exist')
    parser.add_argument('--status', action='store_true', 
                        help='Show current status')
    parser.add_argument('--list-games', action='store_true',
                        help='List available game IDs')
    
    # ETL options
    parser.add_argument('--wipe', '--clean', action='store_true', dest='wipe',
                        help='Delete ALL output CSVs before running ETL')
    parser.add_argument('--games', '-g', nargs='+', type=int,
                        help='Process only specific game IDs')
    parser.add_argument('--exclude-games', nargs='+', type=int,
                        help='Exclude specific game IDs')
    
    args = parser.parse_args()
    
    # List games mode
    if args.list_games:
        games_dir = PROJECT_ROOT / 'data' / 'raw' / 'games'
        print("\nAvailable Games:")
        print("=" * 50)
        game_ids = sorted([d.name for d in games_dir.iterdir() if d.is_dir() and d.name.isdigit()])
        for gid in game_ids:
            tracking = games_dir / gid / f"{gid}_tracking.xlsx"
            status = "✓" if tracking.exists() else "✗ no tracking file"
            print(f"  {gid} {status}")
        print(f"\nTotal: {len(game_ids)} games")
        
        # Check excluded games
        excluded_file = PROJECT_ROOT / 'config' / 'excluded_games.txt'
        if excluded_file.exists():
            excluded = [l.strip() for l in excluded_file.read_text().splitlines() 
                       if l.strip() and not l.startswith('#')]
            if excluded:
                print(f"\nExcluded games (in config/excluded_games.txt):")
                for gid in excluded:
                    print(f"  {gid}")
        sys.exit(0)
    
    if args.validate:
        success = validate()
        sys.exit(0 if success else 1)
    elif args.status:
        status()
        sys.exit(0)
    else:
        # Handle game filtering
        if args.games or args.exclude_games:
            # Set environment variables for game filtering
            if args.games:
                os.environ['BENCHSIGHT_GAMES'] = ','.join(str(g) for g in args.games)
                print(f"Processing only games: {args.games}")
            if args.exclude_games:
                os.environ['BENCHSIGHT_EXCLUDE_GAMES'] = ','.join(str(g) for g in args.exclude_games)
                print(f"Excluding games: {args.exclude_games}")
        
        # Handle wipe option
        if args.wipe:
            print("=" * 70)
            print("WIPE MODE: Deleting all existing output files...")
            print("=" * 70)
            print("⚠️  WARNING: This will delete ALL tables, including dependencies.")
            print("   Later ETL phases depend on tables created in earlier phases.")
            print("   If dependencies are missing, some tables may be created empty.")
            print()
            csv_files = list(OUTPUT_DIR.glob('*.csv'))
            if csv_files:
                for f in csv_files:
                    f.unlink()
                print(f"Deleted {len(csv_files)} CSV files from {OUTPUT_DIR}")
                print()
                print("✓ Wipe complete. Running full ETL to rebuild all tables...")
            else:
                print("No CSV files to delete")
            print()
        
        success = run_full_etl()
        sys.exit(0 if success else 1)
