#!/usr/bin/env python3
"""
Supabase Sync Script v6
=======================
Syncs BenchSight CSV data to Supabase PostgreSQL with flexible filtering options.

Usage:
    python supabase/sync_to_supabase.py                       # Sync all tables
    python supabase/sync_to_supabase.py --wipe                # Wipe and reload all
    python supabase/sync_to_supabase.py --dims --wipe         # Only dimension tables
    python supabase/sync_to_supabase.py --facts --wipe        # Only fact tables
    python supabase/sync_to_supabase.py --qa --wipe           # Only QA tables
    python supabase/sync_to_supabase.py --games 18977 18981   # Only specific games
    python supabase/sync_to_supabase.py --table fact_events   # Single table
    python supabase/sync_to_supabase.py --tables fact_events fact_shifts  # Multiple tables
    python supabase/sync_to_supabase.py --games 18977 --tables fact_events fact_shifts
    python supabase/sync_to_supabase.py --dry-run             # Preview only

Config:
    Reads from config/config_local.ini automatically.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import configparser
import requests
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
CONFIG_DIR = PROJECT_ROOT / "config"


def load_config():
    """Load Supabase config from config_local.ini."""
    config_file = CONFIG_DIR / "config_local.ini"
    
    if not config_file.exists():
        print(f"❌ Config file not found: {config_file}")
        print("   Create with:")
        print("   [supabase]")
        print("   url = https://your-project.supabase.co")
        print("   service_key = your-service-role-key")
        sys.exit(1)
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    if 'supabase' not in config:
        print("❌ [supabase] section not found")
        sys.exit(1)
    
    url = config.get('supabase', 'url', fallback='')
    key = config.get('supabase', 'service_key', fallback='')
    
    if not url or not key:
        print("❌ Missing url or service_key")
        sys.exit(1)
    
    return url, key


class SupabaseSync:
    """Syncs CSV data to Supabase using REST API."""
    
    def __init__(self, url: str, key: str, dry_run: bool = False, verbose: bool = True):
        self.url = url.rstrip('/')
        self.key = key
        self.dry_run = dry_run
        self.verbose = verbose
        self.headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        self.stats = {'success': 0, 'failed': 0, 'rows': 0}
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean dataframe - convert floats to ints where appropriate."""
        df = df.copy()
        
        for col in df.columns:
            if df[col].dtype == 'float64':
                non_null = df[col].dropna()
                if len(non_null) > 0:
                    try:
                        if (non_null % 1 == 0).all():
                            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                    except:
                        pass
                if df[col].dtype == 'float64':
                    df[col] = df[col].replace([float('inf'), float('-inf')], None)
        
        return df
    
    def _record_to_json(self, record: dict) -> dict:
        """Convert record to JSON-safe types."""
        clean = {}
        for k, v in record.items():
            if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
                clean[k] = None
            elif pd.isna(v):
                clean[k] = None
            elif isinstance(v, (np.integer, np.int64, np.int32)):
                clean[k] = int(v)
            elif isinstance(v, (np.floating, np.float64, np.float32)):
                clean[k] = float(v) if not (np.isnan(v) or np.isinf(v)) else None
            elif isinstance(v, np.bool_):
                clean[k] = bool(v)
            elif hasattr(v, 'item'):
                clean[k] = v.item()
            else:
                clean[k] = v
        return clean
    
    def truncate_table(self, table_name: str, first_column: str):
        """Delete all rows from a table."""
        if self.dry_run:
            return True
        delete_url = f"{self.url}/rest/v1/{table_name}?{first_column}=neq.___NEVER___"
        try:
            resp = requests.delete(delete_url, headers=self.headers)
            return resp.status_code in [200, 204]
        except:
            return True
    
    def delete_by_games(self, table_name: str, game_ids: list):
        """Delete rows for specific games only."""
        if self.dry_run or not game_ids:
            return True
        for gid in game_ids:
            delete_url = f"{self.url}/rest/v1/{table_name}?game_id=eq.{gid}"
            try:
                requests.delete(delete_url, headers=self.headers)
            except:
                pass
        return True
    
    def insert_batch(self, table_name: str, records: list) -> tuple:
        """Insert batch. Returns (success, errors)."""
        if not records:
            return (0, 0)
        
        insert_url = f"{self.url}/rest/v1/{table_name}"
        
        try:
            resp = requests.post(insert_url, headers=self.headers, json=records)
            if resp.status_code in [200, 201]:
                return (len(records), 0)
            else:
                success = errors = 0
                for rec in records:
                    try:
                        r = requests.post(insert_url, headers=self.headers, json=[rec])
                        if r.status_code in [200, 201]:
                            success += 1
                        else:
                            errors += 1
                            if errors <= 2:
                                print(f"    Error: {r.text[:80]}")
                    except:
                        errors += 1
                return (success, errors)
        except Exception as e:
            print(f"    Exception: {e}")
            return (0, len(records))
    
    def sync_table(self, table_name: str, df: pd.DataFrame, wipe: bool = False, 
                   game_ids: list = None):
        """Sync a single table with optional game filtering."""
        
        df = self._clean_dataframe(df)
        
        # Filter by game_ids if specified and column exists
        original_count = len(df)
        if game_ids and 'game_id' in df.columns:
            df = df[df['game_id'].isin(game_ids)]
        
        if self.dry_run:
            filter_info = f" (filtered from {original_count})" if game_ids and 'game_id' in df.columns else ""
            print(f"  [DRY] {table_name}: {len(df)} rows{filter_info}")
            return True
        
        if len(df) == 0:
            if self.verbose:
                print(f"  ⚠ {table_name}: No data")
            return True
        
        first_col = df.columns[0]
        
        try:
            if wipe:
                if game_ids and 'game_id' in df.columns:
                    self.delete_by_games(table_name, game_ids)
                else:
                    self.truncate_table(table_name, first_col)
            
            records = [self._record_to_json(row.to_dict()) for _, row in df.iterrows()]
            
            batch_size = 500
            total_ok = total_err = 0
            
            for i in range(0, len(records), batch_size):
                ok, err = self.insert_batch(table_name, records[i:i+batch_size])
                total_ok += ok
                total_err += err
            
            sym = "✓" if total_err == 0 else "⚠"
            err_s = f" ({total_err} err)" if total_err else ""
            filter_info = f" [games: {','.join(map(str, game_ids))}]" if game_ids and 'game_id' in df.columns else ""
            
            if self.verbose:
                print(f"  {sym} {table_name}: {total_ok} rows{err_s}{filter_info}")
            
            self.stats['rows'] += total_ok
            if total_err == 0:
                self.stats['success'] += 1
            else:
                self.stats['failed'] += 1
            
            return total_err == 0
            
        except Exception as e:
            print(f"  ❌ {table_name}: {e}")
            self.stats['failed'] += 1
            return False
    
    def get_tables(self):
        """Get tables from CSV files."""
        tables = {'dim': [], 'fact': [], 'qa': []}
        for f in sorted(OUTPUT_DIR.glob("*.csv")):
            n = f.stem
            if n.startswith('dim_'): tables['dim'].append(n)
            elif n.startswith('fact_'): tables['fact'].append(n)
            elif n.startswith('qa_'): tables['qa'].append(n)
        return tables
    
    def sync_selected(self, table_names: list = None, categories: list = None,
                     wipe: bool = False, game_ids: list = None):
        """
        Sync selected tables with various filter options.
        
        Args:
            table_names: Specific table names to sync
            categories: Categories to sync ('dim', 'fact', 'qa')
            wipe: Whether to wipe before loading
            game_ids: Filter facts by specific game IDs
        """
        all_tables = self.get_tables()
        
        # Determine which tables to sync
        tables_to_sync = []
        
        if table_names:
            # Specific tables requested
            tables_to_sync = table_names
        elif categories:
            # Specific categories requested
            for cat in categories:
                tables_to_sync.extend(all_tables.get(cat, []))
        else:
            # All tables
            for cat in ['dim', 'fact', 'qa']:
                tables_to_sync.extend(all_tables[cat])
        
        total = len(tables_to_sync)
        
        print(f"\n{'='*60}")
        print(f"URL: {self.url}")
        print(f"Tables: {total}")
        print(f"Wipe: {wipe}")
        if game_ids:
            print(f"Games: {game_ids}")
        if categories:
            print(f"Categories: {categories}")
        if table_names:
            print(f"Tables: {table_names}")
        print(f"Dry run: {self.dry_run}")
        print(f"{'='*60}\n")
        
        # Group by category for display
        for cat in ['dim', 'fact', 'qa']:
            cat_tables = [t for t in tables_to_sync if t.startswith(f'{cat}_')]
            if cat_tables:
                print(f"Syncing {cat} ({len(cat_tables)} tables)...")
                for t in cat_tables:
                    csv_path = OUTPUT_DIR / f"{t}.csv"
                    if csv_path.exists():
                        df = pd.read_csv(csv_path, low_memory=False)
                        self.sync_table(t, df, wipe, game_ids)
                    else:
                        print(f"  ⚠ {t}: CSV not found")
                print()
        
        print(f"{'='*60}")
        print(f"DONE: {self.stats['success']} success, {self.stats['failed']} failed, {self.stats['rows']:,} rows")
        print(f"{'='*60}")
        
        return self.stats['failed'] == 0


def main():
    import argparse
    p = argparse.ArgumentParser(
        description='Sync BenchSight data to Supabase',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --wipe                          Wipe and reload all tables
  %(prog)s --dims --wipe                   Only dimension tables
  %(prog)s --facts --wipe                  Only fact tables  
  %(prog)s --qa --wipe                     Only QA tables
  %(prog)s --games 18977 18981 --wipe      Only data for specific games
  %(prog)s --table fact_events --wipe      Single table
  %(prog)s --tables fact_events fact_shifts --wipe   Multiple tables
  %(prog)s --games 18977 --tables fact_events       Game + table filter
  %(prog)s --dry-run                       Preview without changes
        """
    )
    
    # Table selection
    p.add_argument('--table', help='Sync single table')
    p.add_argument('--tables', nargs='+', help='Sync multiple specific tables')
    
    # Category selection
    p.add_argument('--dims', action='store_true', help='Only dimension tables')
    p.add_argument('--facts', action='store_true', help='Only fact tables')
    p.add_argument('--qa', action='store_true', help='Only QA tables')
    
    # Game filtering
    p.add_argument('--games', nargs='+', type=int, help='Only specific game IDs')
    
    # Options
    p.add_argument('--wipe', action='store_true', help='Wipe before loading')
    p.add_argument('--dry-run', action='store_true', help='Preview only')
    p.add_argument('--quiet', action='store_true', help='Less output')
    
    args = p.parse_args()
    
    url, key = load_config()
    print(f"✓ Config loaded")
    
    syncer = SupabaseSync(url, key, dry_run=args.dry_run, verbose=not args.quiet)
    
    # Determine tables and categories
    table_names = None
    categories = None
    
    if args.table:
        table_names = [args.table]
    elif args.tables:
        table_names = args.tables
    elif args.dims or args.facts or args.qa:
        categories = []
        if args.dims: categories.append('dim')
        if args.facts: categories.append('fact')
        if args.qa: categories.append('qa')
    
    success = syncer.sync_selected(
        table_names=table_names,
        categories=categories,
        wipe=args.wipe,
        game_ids=args.games
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
