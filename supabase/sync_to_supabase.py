#!/usr/bin/env python3
"""
Supabase Sync Script v5
=======================
Syncs BenchSight CSV data to Supabase PostgreSQL.

Usage:
    python supabase/sync_to_supabase.py                       # Sync all tables
    python supabase/sync_to_supabase.py --table fact_events   # Sync specific table
    python supabase/sync_to_supabase.py --wipe                # Wipe and reload all
    python supabase/sync_to_supabase.py --dims                # Only dimension tables
    python supabase/sync_to_supabase.py --facts               # Only fact tables
    python supabase/sync_to_supabase.py --games 18977 18981   # Only specific game data

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
        print("❌ [supabase] section not found")
        sys.exit(1)
    
    url = config.get('supabase', 'url', fallback='')
    key = config.get('supabase', 'service_key', fallback='')
    
    if not url or not key:
        print("❌ Missing url or service_key")
        sys.exit(1)
    
    print(f"✓ Config loaded")
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
        """Clean dataframe - convert floats to ints where appropriate."""
        df = df.copy()
        
        for col in df.columns:
            if df[col].dtype == 'float64':
                non_null = df[col].dropna()
                if len(non_null) > 0:
                    # Round first, then check if whole numbers
                    rounded = non_null.round()
                    try:
                        # Convert to nullable Int64
                        df[col] = df[col].round().astype('Int64')
                    except:
                        # Keep as float but replace inf
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
        """Delete all rows."""
        if self.dry_run:
            return True
        delete_url = f"{self.url}/rest/v1/{table_name}?{first_column}=neq.___NEVER___"
        try:
            resp = requests.delete(delete_url, headers=self.headers)
            return resp.status_code in [200, 204]
        except:
            return True
    
    def delete_by_games(self, table_name: str, game_ids: list):
        """Delete rows for specific games."""
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
    
    def sync_table(self, table_name: str, df: pd.DataFrame, wipe: bool = False, game_ids: list = None):
        """Sync a single table."""
        if self.dry_run:
            print(f"  [DRY] {table_name}: {len(df)} rows")
            return True
        
        df = self._clean_dataframe(df)
        
        # Filter by game_ids if specified
        if game_ids and 'game_id' in df.columns:
            df = df[df['game_id'].isin(game_ids)]
        
        if len(df) == 0:
            print(f"  ⚠ {table_name}: No data")
            return True
        
        first_col = df.columns[0]
        
        try:
            if wipe:
                if game_ids and 'game_id' in df.columns:
                    self.delete_by_games(table_name, game_ids)
                else:
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
    
    def sync_all(self, wipe: bool = False, dims_only: bool = False, 
                 facts_only: bool = False, game_ids: list = None):
        """Sync tables with various options."""
        tables = self.get_tables()
        
        # Determine which categories to sync
        cats_to_sync = []
        if dims_only:
            cats_to_sync = ['dim']
        elif facts_only:
            cats_to_sync = ['fact', 'qa']
        else:
            cats_to_sync = ['dim', 'fact', 'qa']
        
        total = sum(len(tables[c]) for c in cats_to_sync)
        
        print(f"\n{'='*60}")
        print(f"URL: {self.url}")
        print(f"Tables: {total}")
        print(f"Wipe: {wipe}")
        if game_ids:
            print(f"Games: {game_ids}")
        print(f"{'='*60}\n")
        
        ok = fail = 0
        
        for cat in cats_to_sync:
            print(f"Syncing {cat}...")
            for t in tables[cat]:
                df = pd.read_csv(OUTPUT_DIR / f"{t}.csv")
                if self.sync_table(t, df, wipe, game_ids):
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
    p = argparse.ArgumentParser(description='Sync BenchSight data to Supabase')
    p.add_argument('--table', help='Sync specific table')
    p.add_argument('--wipe', action='store_true', help='Wipe before loading')
    p.add_argument('--dry-run', action='store_true', help='Preview only')
    p.add_argument('--dims', action='store_true', help='Only dimension tables')
    p.add_argument('--facts', action='store_true', help='Only fact tables')
    p.add_argument('--games', nargs='+', type=int, help='Only specific game IDs')
    args = p.parse_args()
    
    url, key = load_config()
    s = SupabaseSync(url, key, dry_run=args.dry_run)
    
    if args.table:
        csv = OUTPUT_DIR / f"{args.table}.csv"
        if not csv.exists():
            print(f"❌ Not found: {csv}")
            sys.exit(1)
        ok = s.sync_table(args.table, pd.read_csv(csv), args.wipe, args.games)
    else:
        ok = s.sync_all(wipe=args.wipe, dims_only=args.dims, 
                       facts_only=args.facts, game_ids=args.games)
    
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
