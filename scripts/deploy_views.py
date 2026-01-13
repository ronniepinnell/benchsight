#!/usr/bin/env python3
"""
================================================================================
DEPLOY SQL VIEWS TO SUPABASE
================================================================================

Deploys all SQL views to Supabase. Similar to upload.py --schema but for views.

Usage:
    python scripts/deploy_views.py              # Deploy all views
    python scripts/deploy_views.py --dry-run   # Show SQL without executing
    python scripts/deploy_views.py --file X    # Deploy specific file only
    python scripts/deploy_views.py --list      # List all views
    python scripts/deploy_views.py --drop      # Drop all views first

Configuration:
    config/config_local.ini must contain:
    [supabase]
    url = https://your-project.supabase.co
    service_key = your_service_key

Version: 29.0
================================================================================
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
import configparser

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
VIEWS_DIR = PROJECT_ROOT / 'sql' / 'views'
CONFIG_FILE = PROJECT_ROOT / 'config' / 'config_local.ini'

# View file order (deploy in this sequence)
VIEW_FILE_ORDER = [
    '01_leaderboard_views.sql',
    '02_standings_views.sql',
    '03_rankings_views.sql',
    '04_summary_views.sql',
    '05_recent_views.sql',
    '06_comparison_views.sql',
    '07_detail_views.sql',
    '08_tracking_advanced_views.sql',
]


def load_config():
    """Load Supabase configuration."""
    if not CONFIG_FILE.exists():
        print(f"ERROR: Config file not found: {CONFIG_FILE}")
        print("Create config/config_local.ini with [supabase] section")
        return None, None
    
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    
    try:
        url = config.get('supabase', 'url')
        key = config.get('supabase', 'service_key')
        return url, key
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        print(f"ERROR: Missing config: {e}")
        return None, None


def get_supabase_client(url, key):
    """Create Supabase client."""
    try:
        from supabase import create_client, Client
        return create_client(url, key)
    except ImportError:
        print("ERROR: supabase-py not installed. Run: pip install supabase")
        return None


def extract_views_from_file(filepath: Path) -> list:
    """Extract individual view definitions from a SQL file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find all CREATE OR REPLACE VIEW statements
    pattern = r'(CREATE\s+OR\s+REPLACE\s+VIEW\s+\w+\s+AS\s+.*?;)'
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    
    views = []
    for match in matches:
        # Extract view name
        name_match = re.search(r'CREATE\s+OR\s+REPLACE\s+VIEW\s+(\w+)', match, re.IGNORECASE)
        if name_match:
            views.append({
                'name': name_match.group(1),
                'sql': match.strip(),
                'file': filepath.name
            })
    
    return views


def list_all_views():
    """List all views defined in SQL files."""
    all_views = []
    
    for filename in VIEW_FILE_ORDER:
        filepath = VIEWS_DIR / filename
        if filepath.exists():
            views = extract_views_from_file(filepath)
            all_views.extend(views)
    
    return all_views


def deploy_view(client, view: dict, dry_run: bool = False) -> bool:
    """Deploy a single view to Supabase."""
    if dry_run:
        print(f"  [DRY RUN] Would create: {view['name']}")
        return True
    
    try:
        # Use Supabase RPC to execute raw SQL
        # Note: This requires the execute_sql function or direct postgres access
        result = client.rpc('execute_sql', {'query': view['sql']}).execute()
        print(f"  ✓ Created: {view['name']}")
        return True
    except Exception as e:
        # Try alternative method - direct postgrest
        try:
            # For Supabase, we might need to use the SQL editor API
            # or fall back to generating a script
            print(f"  ✗ Failed: {view['name']} - {str(e)[:50]}")
            return False
        except:
            print(f"  ✗ Failed: {view['name']} - {str(e)[:50]}")
            return False


def generate_deploy_script(views: list, output_path: Path = None):
    """Generate a single SQL script with all views."""
    script_lines = [
        "-- ============================================================================",
        "-- BENCHSIGHT VIEWS - AUTO-GENERATED DEPLOY SCRIPT",
        f"-- Generated: {datetime.now().isoformat()}",
        f"-- Total Views: {len(views)}",
        "-- ============================================================================",
        "",
        "-- Run this script in Supabase SQL Editor to deploy all views",
        "",
    ]
    
    current_file = None
    for view in views:
        if view['file'] != current_file:
            script_lines.append(f"\n-- === {view['file']} ===\n")
            current_file = view['file']
        
        script_lines.append(view['sql'])
        script_lines.append("")
    
    script = "\n".join(script_lines)
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(script)
        print(f"Generated: {output_path}")
    
    return script


def drop_all_views(client, views: list, dry_run: bool = False):
    """Drop all views (in reverse order to handle dependencies)."""
    print("\nDropping existing views...")
    
    for view in reversed(views):
        drop_sql = f"DROP VIEW IF EXISTS {view['name']} CASCADE;"
        if dry_run:
            print(f"  [DRY RUN] Would drop: {view['name']}")
        else:
            try:
                client.rpc('execute_sql', {'query': drop_sql}).execute()
                print(f"  ✓ Dropped: {view['name']}")
            except Exception as e:
                print(f"  ✗ Failed to drop: {view['name']}")


def main():
    parser = argparse.ArgumentParser(
        description='Deploy SQL views to Supabase',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/deploy_views.py                  Deploy all views
  python scripts/deploy_views.py --dry-run       Show what would be deployed
  python scripts/deploy_views.py --list          List all views
  python scripts/deploy_views.py --generate      Generate combined SQL script
  python scripts/deploy_views.py --drop          Drop all views first
  python scripts/deploy_views.py --file 02_standings_views.sql   Deploy one file
        """
    )
    
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be deployed without deploying')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List all views')
    parser.add_argument('--generate', '-g', action='store_true',
                        help='Generate combined SQL script (99_DEPLOY_ALL_VIEWS.sql)')
    parser.add_argument('--drop', action='store_true',
                        help='Drop all views before deploying')
    parser.add_argument('--file', '-f', type=str,
                        help='Deploy specific SQL file only')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    # List all views
    print("=" * 70)
    print("BENCHSIGHT VIEW DEPLOYMENT")
    print("=" * 70)
    
    views = list_all_views()
    print(f"\nFound {len(views)} views in {len(VIEW_FILE_ORDER)} files")
    
    if args.list:
        print("\nViews by file:")
        current_file = None
        for view in views:
            if view['file'] != current_file:
                print(f"\n  {view['file']}:")
                current_file = view['file']
            print(f"    - {view['name']}")
        return
    
    if args.generate:
        output_path = VIEWS_DIR / '99_DEPLOY_ALL_VIEWS.sql'
        generate_deploy_script(views, output_path)
        print("\nTo deploy, run this SQL in Supabase SQL Editor")
        return
    
    # Filter to specific file if requested
    if args.file:
        views = [v for v in views if v['file'] == args.file]
        if not views:
            print(f"ERROR: No views found in {args.file}")
            return
        print(f"Filtered to {len(views)} views from {args.file}")
    
    if args.dry_run:
        print("\n[DRY RUN MODE - No changes will be made]\n")
        for view in views:
            print(f"  Would create: {view['name']} (from {view['file']})")
        
        print(f"\n{len(views)} views would be deployed")
        print("\nTo generate SQL script: python scripts/deploy_views.py --generate")
        return
    
    # Load Supabase config
    url, key = load_config()
    if not url or not key:
        print("\nCannot connect to Supabase. Generating SQL script instead...")
        output_path = VIEWS_DIR / '99_DEPLOY_ALL_VIEWS.sql'
        generate_deploy_script(views, output_path)
        print(f"\nRun this SQL in Supabase SQL Editor: {output_path}")
        return
    
    # Connect to Supabase
    client = get_supabase_client(url, key)
    if not client:
        return
    
    # Drop existing views if requested
    if args.drop:
        drop_all_views(client, views, args.dry_run)
    
    # Deploy views
    print("\nDeploying views...")
    success = 0
    failed = 0
    
    for view in views:
        if deploy_view(client, view, args.dry_run):
            success += 1
        else:
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"DEPLOYMENT COMPLETE: {success} succeeded, {failed} failed")
    print("=" * 70)
    
    if failed > 0:
        print("\nNote: If deployment failed, generate SQL and run in Supabase SQL Editor:")
        print("  python scripts/deploy_views.py --generate")


if __name__ == '__main__':
    main()
