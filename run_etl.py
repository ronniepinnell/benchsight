#!/usr/bin/env python3
"""
================================================================================
BENCHSIGHT ETL - SINGLE SOURCE OF TRUTH
================================================================================

THIS IS THE ONLY FILE YOU SHOULD RUN FOR ETL.

WARNING: This ETL currently creates ~70 tables from scratch, NOT 130.
The full 130 tables were built incrementally over 12 sessions.
To get all 130 tables, restore from backup:
    cp data/output_backup_v12.01/*.csv data/output/

Usage:
    python run_etl.py              # Full ETL (creates ~70 tables)
    python run_etl.py --validate   # Check all tables exist
    python run_etl.py --status     # Show current status

Version: 12.03
Date: January 7, 2026
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
EXPECTED_TABLE_COUNT = 100  # Minimum required


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
    # PHASE 4: Core Player Stats
    # =========================================================================
    log_phase(4, "CORE PLAYER STATS")
    try:
        from src.core.build_player_stats import main as build_player_stats
        build_player_stats()
        log(f"Player stats complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"Player stats: {e}")
        log(f"Player stats FAILED: {e}", "ERROR")
    
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
    # PHASE 9: V11 Enhancements
    # =========================================================================
    log_phase(9, "V11 ENHANCEMENTS")
    try:
        from src.advanced.v11_enhancements import run_all_enhancements
        run_all_enhancements()
        log(f"V11 enhancements complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"V11 enhancements: {e}")
        log(f"V11 enhancements FAILED: {e}", "WARN")
    
    # =========================================================================
    # PHASE 10: QA Tables
    # =========================================================================
    log_phase(10, "QA TABLES")
    try:
        from src.qa.build_qa_facts import main as build_qa
        build_qa()
        log(f"QA tables complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"QA tables: {e}")
        log(f"QA tables FAILED: {e}", "WARN")
    
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
        epilog='This is THE ONLY file you should run for ETL.'
    )
    parser.add_argument('--validate', action='store_true', help='Validate tables exist')
    parser.add_argument('--status', action='store_true', help='Show current status')
    
    args = parser.parse_args()
    
    if args.validate:
        success = validate()
        sys.exit(0 if success else 1)
    elif args.status:
        status()
        sys.exit(0)
    else:
        success = run_full_etl()
        sys.exit(0 if success else 1)
