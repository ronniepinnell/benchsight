#!/usr/bin/env python3
"""
BenchSight ALL TABLES Loader

Loads ALL CSV files from data/output to Supabase.
This replaces the limited 12-table loader.

Usage:
    python scripts/load_all_tables.py                    # Load all tables
    python scripts/load_all_tables.py --upsert           # Upsert mode (handle duplicates)
    python scripts/load_all_tables.py --dry-run          # Preview only
    python scripts/load_all_tables.py --table dim_player # Single table
"""

import os
import sys
import csv
import time
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from supabase import create_client, Client
except ImportError:
    print("ERROR: Install supabase: pip install supabase")
    sys.exit(1)

# Load config
try:
    from config.config_loader import load_config
    cfg = load_config()
    SUPABASE_URL = cfg.supabase_url
    SUPABASE_KEY = cfg.supabase_service_key
    DATA_DIR = cfg.data_dir
except:
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
    DATA_DIR = Path(__file__).parent.parent / "data" / "output"

# Load order - dimensions first, then facts
def get_load_order():
    """Get all CSV files in proper load order"""
    csv_files = list(Path(DATA_DIR).glob("*.csv"))
    
    dims = sorted([f.stem for f in csv_files if f.stem.startswith('dim_')])
    facts = sorted([f.stem for f in csv_files if f.stem.startswith('fact_')])
    other = sorted([f.stem for f in csv_files if not f.stem.startswith('dim_') and not f.stem.startswith('fact_')])
    
    return dims + facts + other

def read_csv(filepath):
    """Read CSV and clean values"""
    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned = {}
            for k, v in row.items():
                if v == '' or v == 'nan' or v == 'NaN' or v == 'None':
                    cleaned[k] = None
                elif v.lower() == 'true':
                    cleaned[k] = True
                elif v.lower() == 'false':
                    cleaned[k] = False
                else:
                    try:
                        if '.' in v:
                            cleaned[k] = float(v)
                        else:
                            cleaned[k] = int(v)
                    except (ValueError, TypeError):
                        cleaned[k] = v
                records.append(cleaned)
    return records

def load_table(supabase, table_name, operation='upsert', dry_run=False):
    """Load a single table"""
    csv_path = Path(DATA_DIR) / f"{table_name}.csv"
    
    if not csv_path.exists():
        return {'status': 'skipped', 'reason': 'CSV not found'}
    
    # Read CSV
    try:
        records = read_csv(csv_path)
    except Exception as e:
        return {'status': 'error', 'reason': str(e)}
    
    if not records:
        return {'status': 'skipped', 'reason': 'Empty CSV'}
    
    if dry_run:
        return {'status': 'dry_run', 'rows': len(records)}
    
    # Delete existing data first (for replace)
    if operation == 'replace':
        try:
            # Find a column to delete by
            first_col = list(records[0].keys())[0]
            supabase.table(table_name).delete().neq(first_col, '__IMPOSSIBLE_VALUE__').execute()
        except Exception as e:
            print(f"    Warning: Could not delete existing data: {e}")
    
    # Load in batches
    batch_size = 500
    total_loaded = 0
    errors = []
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            if operation == 'upsert':
                supabase.table(table_name).upsert(batch).execute()
            else:
                supabase.table(table_name).insert(batch).execute()
            total_loaded += len(batch)
        except Exception as e:
            errors.append(str(e))
            # Try inserting one by one for problematic batches
            for record in batch:
                try:
                    if operation == 'upsert':
                        supabase.table(table_name).upsert([record]).execute()
                    else:
                        supabase.table(table_name).insert([record]).execute()
                    total_loaded += 1
                except:
                    pass
    
    return {
        'status': 'success' if not errors else 'partial',
        'rows': total_loaded,
        'errors': errors[:3] if errors else None
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Load ALL tables to Supabase')
    parser.add_argument('--upsert', action='store_true', help='Use upsert (handles duplicates)')
    parser.add_argument('--dry-run', action='store_true', help='Preview only')
    parser.add_argument('--table', help='Load single table')
    parser.add_argument('--skip-dims', action='store_true', help='Skip dimension tables')
    args = parser.parse_args()
    
    operation = 'upsert' if args.upsert else 'replace'
    
    if not SUPABASE_KEY:
        print("ERROR: Supabase credentials not configured")
        sys.exit(1)
    
    # Connect
    print("Connecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get tables
    if args.table:
        tables = [args.table]
    else:
        tables = get_load_order()
        if args.skip_dims:
            tables = [t for t in tables if not t.startswith('dim_')]
    
    print(f"\n{'='*60}")
    print(f"LOADING {len(tables)} TABLES ({operation})")
    print(f"{'='*60}\n")
    
    # Load each table
    results = {}
    total_rows = 0
    success_count = 0
    
    start_time = time.time()
    
    for i, table in enumerate(tables, 1):
        print(f"[{i:2}/{len(tables)}] {table}...", end=' ', flush=True)
        
        result = load_table(supabase, table, operation, args.dry_run)
        results[table] = result
        
        if result['status'] in ['success', 'partial', 'dry_run']:
            rows = result.get('rows', 0)
            total_rows += rows
            success_count += 1
            status_icon = '✓' if result['status'] == 'success' else '⚠' if result['status'] == 'partial' else '○'
            print(f"{status_icon} {rows} rows")
        else:
            print(f"✗ {result.get('reason', 'Failed')}")
    
    duration = time.time() - start_time
    
    # Summary
    print(f"\n{'='*60}")
    print(f"COMPLETE")
    print(f"{'='*60}")
    print(f"Tables: {success_count}/{len(tables)}")
    print(f"Total Rows: {total_rows:,}")
    print(f"Duration: {duration:.1f}s")
    
    # Show failures
    failures = [t for t, r in results.items() if r['status'] not in ['success', 'partial', 'dry_run', 'skipped']]
    if failures:
        print(f"\nFailed tables: {failures}")

if __name__ == '__main__':
    main()
