#!/usr/bin/env python3
"""
Schema Snapshot System
======================
Tracks table schemas over time to detect unintended column changes.

Usage:
    python scripts/utilities/schema_snapshot.py --generate   # Create snapshot from current output
    python scripts/utilities/schema_snapshot.py --compare    # Compare current to snapshot
    python scripts/utilities/schema_snapshot.py --update     # Update snapshot to current

The snapshot tracks:
- Column names for each table
- Column count
- Minimum expected row count

Changes are flagged as:
- WARN: Columns added (usually OK)
- FAIL: Columns removed (potential breaking change)
- WARN: Column count changed significantly
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import sys

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
CONFIG_DIR = PROJECT_ROOT / "config"
SNAPSHOT_FILE = CONFIG_DIR / "SCHEMA_SNAPSHOT.json"

# Critical tables that must maintain schema
CRITICAL_TABLES = [
    'fact_events',
    'fact_event_players',
    'fact_shifts',
    'fact_shift_players',
    'fact_gameroster',
    'fact_player_game_stats',
    'dim_player',
    'dim_team',
    'dim_game',
]


def generate_snapshot():
    """Generate schema snapshot from current output."""
    print("Generating schema snapshot...")
    
    snapshot = {
        '_generated': datetime.now().isoformat(),
        '_description': 'Schema snapshot for regression detection',
        'tables': {}
    }
    
    csv_files = sorted(OUTPUT_DIR.glob("*.csv"))
    
    for csv_path in csv_files:
        table_name = csv_path.stem
        
        try:
            df = pd.read_csv(csv_path, nrows=10)  # Just need columns
            full_df = pd.read_csv(csv_path)  # For row count
            
            snapshot['tables'][table_name] = {
                'columns': list(df.columns),
                'column_count': len(df.columns),
                'row_count': len(full_df),
                'row_count_min': max(1, len(full_df) // 2),  # Min is half current
                'critical': table_name in CRITICAL_TABLES
            }
            
            print(f"  ✓ {table_name}: {len(df.columns)} columns, {len(full_df)} rows")
            
        except Exception as e:
            print(f"  ✗ {table_name}: Error - {e}")
    
    # Save snapshot
    with open(SNAPSHOT_FILE, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"\nSnapshot saved to {SNAPSHOT_FILE}")
    print(f"Tables: {len(snapshot['tables'])}")
    return snapshot


def compare_to_snapshot():
    """Compare current output to snapshot."""
    print("Comparing current output to schema snapshot...")
    
    if not SNAPSHOT_FILE.exists():
        print("  ⚠ No snapshot found. Run --generate first.")
        return True, []
    
    with open(SNAPSHOT_FILE) as f:
        snapshot = json.load(f)
    
    failures = []
    warnings = []
    
    # Check each table in snapshot
    for table_name, expected in snapshot.get('tables', {}).items():
        csv_path = OUTPUT_DIR / f"{table_name}.csv"
        
        if not csv_path.exists():
            if expected.get('critical', False):
                failures.append(f"MISSING: {table_name} (critical table)")
            else:
                warnings.append(f"MISSING: {table_name}")
            continue
        
        try:
            df = pd.read_csv(csv_path, nrows=10)
            full_df = pd.read_csv(csv_path)
            
            current_cols = set(df.columns)
            expected_cols = set(expected.get('columns', []))
            
            # Check for removed columns (FAIL for critical)
            removed = expected_cols - current_cols
            if removed:
                msg = f"{table_name}: Columns removed: {removed}"
                if expected.get('critical', False):
                    failures.append(msg)
                else:
                    warnings.append(msg)
            
            # Check for added columns (WARN)
            added = current_cols - expected_cols
            if added:
                warnings.append(f"{table_name}: Columns added: {added}")
            
            # Check row count (WARN if dropped significantly)
            min_rows = expected.get('row_count_min', 1)
            if len(full_df) < min_rows:
                warnings.append(
                    f"{table_name}: Row count dropped ({len(full_df)} < {min_rows} min)"
                )
            
        except Exception as e:
            warnings.append(f"{table_name}: Error reading - {e}")
    
    # Check for new tables not in snapshot
    current_tables = set(p.stem for p in OUTPUT_DIR.glob("*.csv"))
    snapshot_tables = set(snapshot.get('tables', {}).keys())
    new_tables = current_tables - snapshot_tables
    
    if new_tables:
        warnings.append(f"New tables not in snapshot: {new_tables}")
    
    # Report results
    print("\n" + "="*60)
    
    if failures:
        print("\n❌ FAILURES (blocking):")
        for f in failures:
            print(f"  • {f}")
    
    if warnings:
        print("\n⚠️  WARNINGS:")
        for w in warnings:
            print(f"  • {w}")
    
    if not failures and not warnings:
        print("\n✅ Schema matches snapshot perfectly!")
    
    print("="*60)
    
    return len(failures) == 0, warnings


def update_snapshot():
    """Update snapshot to match current output."""
    print("Updating schema snapshot to current output...")
    
    # Generate new snapshot
    generate_snapshot()
    
    print("\n✅ Snapshot updated")


def main():
    parser = argparse.ArgumentParser(description='Schema Snapshot System')
    parser.add_argument('--generate', action='store_true', 
                        help='Generate snapshot from current output')
    parser.add_argument('--compare', action='store_true',
                        help='Compare current output to snapshot')
    parser.add_argument('--update', action='store_true',
                        help='Update snapshot to current output')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON (for pre_delivery.py)')
    
    args = parser.parse_args()
    
    if args.generate:
        generate_snapshot()
    elif args.compare:
        passed, warnings = compare_to_snapshot()
        if args.json:
            print(json.dumps({'passed': passed, 'warnings': warnings}))
        sys.exit(0 if passed else 1)
    elif args.update:
        update_snapshot()
    else:
        # Default: compare
        passed, warnings = compare_to_snapshot()
        sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
