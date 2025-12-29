#!/usr/bin/env python3
"""
BenchSight Supabase Setup Script
Run this locally to create tables and upload data.

Prerequisites:
    pip install supabase pandas

Usage:
    python supabase_setup.py
"""

import os
import sys
import pandas as pd
from pathlib import Path
from supabase import create_client, Client
import json
import time

# Configuration
SUPABASE_URL = "https://uuaowslhpgyiudmbvqze.supabase.co"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1YW93c2xocGd5aXVkbWJ2cXplIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2Njg1NDk4NywiZXhwIjoyMDgyNDMwOTg3fQ.BV5d03x9Hv83XZsveGdU7k7D7gAZ7Yi1tqNB7DeDkrM"

OUTPUT_DIR = Path("data/output")


def create_tables(supabase: Client):
    """Create all tables using SQL file"""
    print("\n=== STEP 1: CREATE TABLES ===")
    print("Please run the SQL in sql/create_tables.sql in the Supabase SQL Editor")
    print("URL: https://supabase.com/dashboard/project/uuaowslhpgyiudmbvqze/sql/new")
    print("\nPress Enter after you've created the tables...")
    input()


def upload_data(supabase: Client):
    """Upload all CSV data to Supabase"""
    print("\n=== STEP 2: UPLOAD DATA ===")
    
    # Get all CSV files
    csv_files = sorted(OUTPUT_DIR.glob("*.csv"))
    print(f"Found {len(csv_files)} tables to upload")
    
    # Upload order: dimensions first, then facts
    dims = [f for f in csv_files if f.stem.startswith('dim_')]
    facts = [f for f in csv_files if f.stem.startswith('fact_')]
    upload_order = dims + facts
    
    success = 0
    failed = []
    
    for csv_file in upload_order:
        table = csv_file.stem
        
        # Read CSV
        df = pd.read_csv(csv_file, dtype=str)
        
        if len(df) == 0:
            print(f"  {table}: SKIP (empty)")
            continue
        
        # Replace NaN with None
        df = df.where(pd.notna(df), None)
        records = df.to_dict(orient='records')
        
        # Clean records
        clean_records = []
        for rec in records:
            clean_rec = {k: v for k, v in rec.items() if v is not None}
            clean_records.append(clean_rec)
        
        try:
            # Delete existing data
            supabase.table(table).delete().neq('*', 'impossible_value').execute()
            
            # Upload in batches
            batch_size = 500
            for i in range(0, len(clean_records), batch_size):
                batch = clean_records[i:i+batch_size]
                supabase.table(table).upsert(batch).execute()
            
            print(f"  {table}: {len(clean_records)} rows ✓")
            success += 1
            
        except Exception as e:
            print(f"  {table}: FAILED - {str(e)[:60]}")
            failed.append((table, str(e)))
        
        time.sleep(0.1)
    
    print(f"\n=== UPLOAD COMPLETE: {success}/{len(upload_order)} tables ===")
    if failed:
        print(f"\nFailed tables ({len(failed)}):")
        for t, err in failed[:10]:
            print(f"  {t}: {err[:60]}")


def verify_upload(supabase: Client):
    """Verify the upload by checking row counts"""
    print("\n=== STEP 3: VERIFY UPLOAD ===")
    
    csv_files = sorted(OUTPUT_DIR.glob("*.csv"))
    
    print("\nTable Row Counts:")
    for csv_file in list(csv_files)[:10]:  # Check first 10
        table = csv_file.stem
        try:
            result = supabase.table(table).select("*", count="exact").limit(1).execute()
            db_count = result.count
            csv_count = len(pd.read_csv(csv_file))
            status = "✓" if db_count == csv_count else f"MISMATCH (CSV: {csv_count})"
            print(f"  {table}: {db_count} {status}")
        except Exception as e:
            print(f"  {table}: ERROR - {str(e)[:40]}")
    
    print("\n... (and more)")


def main():
    print("=" * 60)
    print("BENCHSIGHT SUPABASE SETUP")
    print("=" * 60)
    print(f"\nSupabase URL: {SUPABASE_URL}")
    print(f"Data directory: {OUTPUT_DIR}")
    
    # Check output directory
    if not OUTPUT_DIR.exists():
        print(f"\nERROR: {OUTPUT_DIR} not found!")
        print("Make sure you're running from the project root directory.")
        sys.exit(1)
    
    # Initialize Supabase client
    print("\nConnecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SERVICE_KEY)
    print("Connected!")
    
    # Steps
    create_tables(supabase)
    upload_data(supabase)
    verify_upload(supabase)
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
