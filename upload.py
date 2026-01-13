#!/usr/bin/env python3
"""
================================================================================
BENCHSIGHT SUPABASE UPLOAD
================================================================================
Uploads CSV data from data/output/ to Supabase.

PREREQUISITES:
    1. Run ETL first: python run_etl.py
    2. Schema exists in Supabase (run sql/reset_supabase.sql in SQL Editor)

USAGE:
    python upload.py                        # Upload all tables
    python upload.py --tables dim_player dim_team   # Upload specific tables
    python upload.py --pattern "fact_player*"       # Upload tables matching pattern
    python upload.py --dims                 # Upload dimension tables only
    python upload.py --facts                # Upload fact tables only
    python upload.py --qa                   # Upload QA/lookup tables only
    python upload.py --basic                # Upload _basic stats tables only
    python upload.py --schema               # Generate schema SQL only
    python upload.py --list                 # List all available tables
    python upload.py --verify               # Verify upload counts

CONFIGURATION:
    config/config_local.ini must contain:
    [supabase]
    url = https://your-project.supabase.co
    service_key = your_service_key

================================================================================
Version: 28.3
Updated: 2026-01-12
================================================================================
"""

import sys
import argparse
import logging
import fnmatch
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('upload')


def main():
    parser = argparse.ArgumentParser(
        description='Upload BenchSight data to Supabase',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python upload.py                              Upload all 139 tables
  python upload.py --tables dim_player dim_team Upload specific tables
  python upload.py --pattern "fact_player*"     Upload matching pattern
  python upload.py --pattern "*_basic"          Upload all _basic tables
  python upload.py --dims                       Upload dimension tables (dim_*)
  python upload.py --facts                      Upload fact tables (fact_*)
  python upload.py --qa                         Upload QA tables (qa_*, lookup_*)
  python upload.py --basic                      Upload basic stats tables (*_basic)
  python upload.py --schema                     Generate SQL schema only
  python upload.py --list                       List all available tables
  python upload.py --list --dims                List dimension tables only
  python upload.py --verify                     Verify data after upload
        """
    )
    
    # Table selection arguments
    parser.add_argument('--tables', '-t', nargs='+', 
                        help='Upload specific tables by name')
    parser.add_argument('--pattern', '-p', type=str,
                        help='Upload tables matching pattern (e.g., "fact_player*")')
    parser.add_argument('--dims', action='store_true',
                        help='Upload dimension tables only (dim_*)')
    parser.add_argument('--facts', action='store_true',
                        help='Upload fact tables only (fact_*)')
    parser.add_argument('--qa', action='store_true',
                        help='Upload QA/lookup tables only (qa_*, lookup_*)')
    parser.add_argument('--basic', action='store_true',
                        help='Upload basic stats tables only (*_basic)')
    parser.add_argument('--tracking', action='store_true',
                        help='Upload tracking-derived tables (game stats, events, shifts)')
    
    # Action arguments
    parser.add_argument('--schema', action='store_true',
                        help='Generate schema SQL only (no upload)')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List available tables (no upload)')
    parser.add_argument('--verify', action='store_true',
                        help='Verify upload by checking row counts')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be uploaded without uploading')
    
    # Other options
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Import manager
    try:
        from src.supabase.supabase_manager import SupabaseManager
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure you're in the benchsight directory")
        sys.exit(1)
    
    # Initialize manager
    try:
        mgr = SupabaseManager()
    except FileNotFoundError as e:
        logger.error(f"Config not found: {e}")
        logger.error("Create config/config_local.ini with Supabase credentials")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Config error: {e}")
        sys.exit(1)
    
    # Get all available tables
    all_tables = sorted(mgr._get_tables())
    
    # List mode
    if args.list:
        print("=" * 60)
        print("AVAILABLE TABLES")
        print("=" * 60)
        
        # Apply filters for listing
        tables_to_show = filter_tables(all_tables, args)
        
        # Group by prefix
        dims = [t for t in tables_to_show if t.startswith('dim_')]
        facts = [t for t in tables_to_show if t.startswith('fact_')]
        qa = [t for t in tables_to_show if t.startswith('qa_') or t.startswith('lookup_')]
        
        if dims:
            print(f"\nDimension Tables ({len(dims)}):")
            for t in dims:
                print(f"  {t}")
        
        if facts:
            print(f"\nFact Tables ({len(facts)}):")
            for t in facts:
                print(f"  {t}")
        
        if qa:
            print(f"\nQA/Lookup Tables ({len(qa)}):")
            for t in qa:
                print(f"  {t}")
        
        print(f"\nTotal: {len(tables_to_show)} tables")
        return
    
    print("=" * 60)
    print("BENCHSIGHT SUPABASE UPLOAD")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Schema only mode
    if args.schema:
        print("Generating schema SQL...")
        results = mgr.reset_schema()
        print(f"\nGenerated sql/reset_supabase.sql")
        print(f"Tables: {results['tables_created']}")
        print(f"\nNext steps:")
        print("  1. Open Supabase SQL Editor")
        print("  2. Paste contents of sql/reset_supabase.sql")
        print("  3. Execute")
        print("  4. Run: python upload.py")
        return
    
    # Determine which tables to upload
    tables = filter_tables(all_tables, args)
    
    if not tables:
        print("No tables matched the criteria.")
        print("Use --list to see available tables.")
        sys.exit(1)
    
    print(f"Tables to upload: {len(tables)}")
    
    # Dry run mode
    if args.dry_run:
        print("\n[DRY RUN] Would upload these tables:")
        for t in tables:
            print(f"  {t}")
        print(f"\nTotal: {len(tables)} tables")
        return
    
    print()
    
    # Upload
    results = mgr.upload_all(tables)
    
    # Summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Success: {results['tables_success']}/{results['tables_attempted']}")
    print(f"Failed:  {results['tables_failed']}")
    print(f"Rows:    {results['total_rows']:,}")
    
    if results['errors']:
        print(f"\nErrors ({len(results['errors'])} tables):")
        for table, errs in results['errors'].items():
            print(f"  {table}: {errs[0][:50]}...")
    
    # Verify mode
    if args.verify:
        print()
        print("=" * 60)
        print("VERIFICATION")
        print("=" * 60)
        # TODO: Query Supabase for row counts and compare
        print("Verification not yet implemented")
    
    print()
    if results['tables_failed'] == 0:
        print("✓ Upload complete!")
    else:
        print(f"⚠ Upload completed with {results['tables_failed']} failures")
        sys.exit(1)


def filter_tables(all_tables: list, args) -> list:
    """Filter tables based on command line arguments."""
    
    # If specific tables requested
    if args.tables:
        missing = [t for t in args.tables if t not in all_tables]
        if missing:
            logger.warning(f"Tables not found: {missing}")
        return [t for t in args.tables if t in all_tables]
    
    # If pattern requested
    if args.pattern:
        return [t for t in all_tables if fnmatch.fnmatch(t, args.pattern)]
    
    # Category filters (can be combined)
    filtered = set()
    any_filter = False
    
    if args.dims:
        any_filter = True
        filtered.update(t for t in all_tables if t.startswith('dim_'))
    
    if args.facts:
        any_filter = True
        filtered.update(t for t in all_tables if t.startswith('fact_'))
    
    if args.qa:
        any_filter = True
        filtered.update(t for t in all_tables if t.startswith('qa_') or t.startswith('lookup_'))
    
    if args.basic:
        any_filter = True
        filtered.update(t for t in all_tables if t.endswith('_basic'))
    
    if args.tracking:
        any_filter = True
        tracking_patterns = [
            'fact_player_game_stats', 'fact_goalie_game_stats', 'fact_team_game_stats',
            'fact_events', 'fact_event_players', 'fact_shifts', 'fact_shift_players',
            'fact_tracking', 'fact_saves', 'fact_faceoffs', 'fact_penalties'
        ]
        filtered.update(t for t in all_tables if t in tracking_patterns)
    
    if any_filter:
        return sorted(filtered)
    
    # No filter = all tables
    return all_tables


if __name__ == '__main__':
    main()
