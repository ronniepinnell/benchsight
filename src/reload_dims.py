"""
Reload Dimension Tables
Reloads dimension tables from BLB_Tables.xlsx to Supabase.
TRUNCATES and reloads - use for static/semi-static tables.

Usage:
    python3 src/reload_dims.py                    # List available tables
    python3 src/reload_dims.py dim_player         # Reload single table
    python3 src/reload_dims.py dim_team dim_player # Reload multiple
    python3 src/reload_dims.py --all              # Reload ALL dims (careful!)
"""

import sys
import os
import pandas as pd
import numpy as np

try:
    from supabase import create_client
except ImportError:
    print("Install supabase: pip3 install supabase")
    sys.exit(1)

# Config
SUPABASE_URL = "https://uuaowslhpgyiudmbvqze.supabase.co"
SUPABASE_KEY = "sb_publishable_t1lIOebbbCjAu_YBKc8tLg_B_zH_l73"
BLB_FILE = "data/BLB_Tables.xlsx"

# Mapping: supabase table -> BLB sheet name or CSV file
DIM_TABLES = {
    'dim_player': 'dim_player',
    'dim_team': 'dim_team',
    'dim_schedule': 'dim_schedule',
    'dim_season': 'dim_season',
    'dim_league': 'dim_league',
    'dim_position': 'dim_position',
    'dim_event_type': 'dim_event_type',
    'dim_event_detail': 'dim_event_detail',
    'dim_play_detail': 'dim_play_detail',
    'dim_strength': 'dim_strength',
    'dim_situation': 'dim_situation',
    'dim_zone': 'dim_zone',
    'dim_period': 'dim_period',
    'dim_venue': 'dim_venue',
    'dim_shot_type': 'dim_shot_type',
    'dim_pass_type': 'dim_pass_type',
    'dim_shift_type': 'dim_shift_type',
    'dim_skill_tier': 'dim_skill_tier',
    'dim_player_role': 'dim_player_role',
    'dim_danger_zone': 'dim_danger_zone',
    'dim_time_bucket': 'dim_time_bucket',
    'dim_rinkboxcoord': 'dim_rinkboxcoord',
    'dim_rinkcoordzones': 'dim_rinkcoordzones',
    'dim_stat': 'dim_stat',
    'dim_net_location': 'dim_net_location',
}


def clean_value(v):
    """Clean a single value."""
    if v is None:
        return None
    if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
        return None
    if pd.isna(v):
        return None
    if isinstance(v, str) and v.lower() in ('nan', 'none', 'null', ''):
        return None
    return v


def clean_record(record):
    """Clean all values in a record."""
    return {k.lower().lstrip('\ufeff'): clean_value(v) for k, v in record.items()}


def reload_table(supabase, table_name, sheet_name):
    """Reload a single dimension table."""
    print(f"\nReloading {table_name} from sheet/file '{sheet_name}'...")
    
    try:
        # First try CSV file in data/output
        csv_path = f"data/output/{sheet_name}.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path, low_memory=False)
            print(f"  Loaded from CSV: {csv_path}")
        else:
            # Fall back to Excel
            df = pd.read_excel(BLB_FILE, sheet_name=sheet_name)
            print(f"  Loaded from Excel sheet: {sheet_name}")
        
        print(f"  Found {len(df)} rows")
        
        if len(df) == 0:
            print(f"  WARNING: Sheet is empty")
            return 0
        
        # Clean records
        records = [clean_record(r) for r in df.to_dict(orient='records')]
        
        # Delete existing data
        print(f"  Deleting existing rows...")
        try:
            # Supabase requires a filter for delete, use a always-true condition
            supabase.table(table_name).delete().neq('id', -999999).execute()
        except:
            # Try alternate approach for tables without 'id'
            try:
                supabase.table(table_name).delete().gte('index', -999999).execute()
            except:
                print(f"  WARNING: Could not delete existing rows - table may have duplicates")
        
        # Insert new data in batches
        print(f"  Inserting {len(records)} rows...")
        batch_size = 100
        total = 0
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            try:
                supabase.table(table_name).insert(batch).execute()
                total += len(batch)
            except Exception as e:
                print(f"  ERROR batch {i//batch_size + 1}: {e}")
                # Try one by one
                for rec in batch:
                    try:
                        supabase.table(table_name).insert(rec).execute()
                        total += 1
                    except:
                        pass
        
        print(f"  ✓ {table_name}: {total} rows loaded")
        return total
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return 0


def main():
    if len(sys.argv) < 2:
        print("Reload Dimension Tables from BLB_Tables.xlsx")
        print("=" * 50)
        print("\nAvailable tables:")
        for table in sorted(DIM_TABLES.keys()):
            print(f"  - {table}")
        print("\nUsage:")
        print("  python3 src/reload_dims.py dim_player         # Single table")
        print("  python3 src/reload_dims.py dim_team dim_player # Multiple tables")
        print("  python3 src/reload_dims.py --all              # ALL tables (careful!)")
        sys.exit(0)
    
    # Parse arguments
    if '--all' in sys.argv:
        tables_to_reload = list(DIM_TABLES.keys())
        print("WARNING: This will reload ALL dimension tables!")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
    else:
        tables_to_reload = [t for t in sys.argv[1:] if t in DIM_TABLES]
        invalid = [t for t in sys.argv[1:] if t not in DIM_TABLES and not t.startswith('-')]
        if invalid:
            print(f"Unknown tables: {invalid}")
            print(f"Valid tables: {list(DIM_TABLES.keys())}")
            sys.exit(1)
    
    if not tables_to_reload:
        print("No valid tables specified")
        sys.exit(1)
    
    print("=" * 50)
    print("RELOAD DIMENSION TABLES")
    print("=" * 50)
    print(f"Tables to reload: {tables_to_reload}")
    
    # Connect
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Reload each table
    total_rows = 0
    for table in tables_to_reload:
        sheet = DIM_TABLES[table]
        rows = reload_table(supabase, table, sheet)
        total_rows += rows
    
    print("\n" + "=" * 50)
    print(f"COMPLETE: {total_rows} total rows loaded")
    print("=" * 50)


if __name__ == "__main__":
    main()
