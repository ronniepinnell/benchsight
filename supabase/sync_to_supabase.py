#!/usr/bin/env python3
"""
Supabase Sync Script v4
=======================
Syncs BenchSight CSV data to Supabase PostgreSQL.

Usage:
    python supabase/sync_to_supabase.py                       # Sync all tables
    python supabase/sync_to_supabase.py --table fact_events   # Sync specific table
    python supabase/sync_to_supabase.py --wipe                # Wipe and reload all

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

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
CONFIG_DIR = PROJECT_ROOT / "config"


def load_config():
    """Load Supabase config from config_local.ini."""
    config_file = CONFIG_DIR / "config_local.ini"
    
    if not config_file.exists():
        print(f"❌ Config file not found: {config_file}")
        sys.exit(1)
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    if 'supabase' not in config:
        print("❌ [supabase] section not found in config_local.ini")
        sys.exit(1)
    
    url = config.get('supabase', 'url', fallback='')
    key = config.get('supabase', 'service_key', fallback='')
    
    if not url or not key:
        print("❌ Missing url or service_key in config_local.ini")
        sys.exit(1)
    
    print(f"✓ Loaded config from {config_file}")
    return url, key


class SupabaseSync:
    """Syncs CSV data to Supabase using REST API."""
    
    def __init__(self, url: str, key: str, dry_run: bool = False):
        self.url = url.rstrip('/')
        self.key = key
        self.dry_run = dry_run
        self.headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean dataframe - convert float columns that are actually ints."""
        df = df.copy()
        
        for col in df.columns:
            if df[col].dtype == 'float64':
                # Check if all non-null values are whole numbers
                non_null = df[col].dropna()
                if len(non_null) > 0:
                    try:
                        # Check if they're all whole numbers
                        if (non_null % 1 == 0).all():
                            # Convert to nullable Int64
                            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                    except:
                        pass
                    
                # Replace inf with None for remaining floats
                if df[col].dtype == 'float64':
                    df[col] = df[col].replace([float('inf'), float('-inf')], None)
        
        return df
    
    def _record_to_json(self, record: dict) -> dict:
        """Convert a record to JSON-safe types."""
        clean = {}
        for k, v in record.items():
            if v is None:
                clean[k] = None
            elif pd.isna(v):
                clean[k] = None
            elif isinstance(v, (np.integer, np.int64, np.int32)):
                clean[k] = int(v)
            elif isinstance(v, (np.floating, np.float64, np.float32)):
                if np.isnan(v) or np.isinf(v):
                    clean[k] = None
                else:
                    clean[k] = float(v)
            elif isinstance(v, np.bool_):
                clean[k] = bool(v)
            elif hasattr(v, 'item'):  # numpy scalar
                clean[k] = v.item()
            else:
                clean[k] = v
        return clean
    
    def truncate_table(self, table_name: str, first_column: str):
        """Delete all rows."""
        if self.dry_run:
            return True
        
        delete_url = f"{self.url}/rest/v1/{table_name}?{first_column}=neq.___NEVER___"
        try:
            resp = requests.delete(delete_url, headers=self.headers)
            return resp.status_code in [200, 204]
        except:
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
                # Single insert to find bad records
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
    
    def sync_table(self, table_name: str, df: pd.DataFrame, wipe: bool = False):
        """Sync a single table."""
        if self.dry_run:
            print(f"  [DRY] {table_name}: {len(df)} rows")
            return True
        
        df = self._clean_dataframe(df)
        
        if len(df) == 0:
            print(f"  ⚠ {table_name}: No data")
            return True
        
        first_col = df.columns[0]
        
        try:
            if wipe:
                self.truncate_table(table_name, first_col)
            
            # Convert to JSON-safe records
            records = [self._record_to_json(row.to_dict()) for _, row in df.iterrows()]
            
            # Batch insert
            batch_size = 500
            total_ok = total_err = 0
            
            for i in range(0, len(records), batch_size):
                ok, err = self.insert_batch(table_name, records[i:i+batch_size])
                total_ok += ok
                total_err += err
            
            sym = "✓" if total_err == 0 else "⚠"
            err_s = f" ({total_err} err)" if total_err else ""
            print(f"  {sym} {table_name}: {total_ok} rows{err_s}")
            return total_err == 0
            
        except Exception as e:
            print(f"  ❌ {table_name}: {e}")
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
    
    def sync_all(self, wipe: bool = False):
        """Sync all tables."""
        tables = self.get_tables()
        total = sum(len(v) for v in tables.values())
        
        print(f"\n{'='*60}")
        print(f"URL: {self.url}")
        print(f"Tables: {total}")
        print(f"Wipe: {wipe}")
        print(f"{'='*60}\n")
        
        ok = fail = 0
        
        for cat in ['dim', 'fact', 'qa']:
            print(f"Syncing {cat}...")
            for t in tables[cat]:
                df = pd.read_csv(OUTPUT_DIR / f"{t}.csv")
                if self.sync_table(t, df, wipe):
                    ok += 1
                else:
                    fail += 1
            print()
        
        print(f"{'='*60}")
        print(f"DONE: {ok} success, {fail} failed")
        print(f"{'='*60}")
        return fail == 0


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--table')
    p.add_argument('--wipe', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    
    url, key = load_config()
    s = SupabaseSync(url, key, dry_run=args.dry_run)
    
    if args.table:
        csv = OUTPUT_DIR / f"{args.table}.csv"
        if not csv.exists():
            print(f"❌ Not found: {csv}")
            sys.exit(1)
        ok = s.sync_table(args.table, pd.read_csv(csv), args.wipe)
    else:
        ok = s.sync_all(wipe=args.wipe)
    
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
