#!/usr/bin/env python3
"""
BENCHSIGHT v5.0.0 - UPLOAD TO SUPABASE
======================================
"""

import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, 'src')
from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client

OUTPUT_DIR = Path("data/output")
BATCH_SIZE = 500

def main():
    print("=" * 60)
    print("BENCHSIGHT v5.0.0 - UPLOAD TO SUPABASE")
    print("=" * 60)
    
    # Connect
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"Connected to Supabase")
    
    # Order: dims first, then facts
    csvs = sorted(OUTPUT_DIR.glob("dim_*.csv")) + sorted(OUTPUT_DIR.glob("fact_*.csv"))
    
    total = 0
    errors = []
    
    for csv in csvs:
        table = csv.stem
        df = pd.read_csv(csv, dtype=str)
        
        if len(df) == 0:
            print(f"  {table}: empty, skipping")
            continue
        
        # Delete existing data
        try:
            client.table(table).delete().neq('id', -999).execute()
        except:
            pass
        
        # Upload in batches
        records = df.replace({pd.NA: None, 'nan': None, '': None}).to_dict('records')
        
        success = True
        for i in range(0, len(records), BATCH_SIZE):
            batch = records[i:i+BATCH_SIZE]
            try:
                client.table(table).insert(batch).execute()
            except Exception as e:
                print(f"  ERROR {table}: {e}")
                errors.append((table, str(e)))
                success = False
                break
        
        if success:
            total += len(df)
            print(f"  ✓ {table}: {len(df):,} rows")
    
    print(f"\nTotal: {total:,} rows uploaded")
    if errors:
        print(f"Errors: {len(errors)}")
        for t, e in errors:
            print(f"  - {t}: {e[:50]}")

if __name__ == "__main__":
    main()
