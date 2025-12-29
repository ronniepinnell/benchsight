#!/usr/bin/env python3
"""
BenchSight Supabase Upload Script
==================================

This script:
1. Connects to Supabase using credentials from config or environment
2. Creates tables based on CSV structure
3. Uploads all CSV data

Usage:
    python src/supabase_upload_clean.py

Prerequisites:
    1. Copy config/config_local.ini.template to config/config_local.ini
    2. Add your Supabase service key to config_local.ini
    
    OR set environment variable:
    export SUPABASE_SERVICE_KEY=your_key_here
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from configparser import ConfigParser
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "output"
CONFIG_DIR = BASE_DIR / "config"

# Supabase URL (public - safe to commit)
SUPABASE_URL = "https://uuaowslhpgyiudmbvqze.supabase.co"


def get_supabase_key():
    """Get Supabase service key from environment or config file."""
    # Try environment variable first
    key = os.environ.get('SUPABASE_SERVICE_KEY')
    if key:
        logger.info("Using Supabase key from environment variable")
        return key
    
    # Try config file
    config_file = CONFIG_DIR / "config_local.ini"
    if config_file.exists():
        config = ConfigParser()
        config.read(config_file)
        if config.has_option('supabase', 'service_key'):
            key = config.get('supabase', 'service_key')
            if key and key != 'YOUR_SERVICE_KEY_HERE':
                logger.info("Using Supabase key from config_local.ini")
                return key
    
    # No key found
    logger.error("""
    ============================================================
    SUPABASE SERVICE KEY NOT FOUND
    ============================================================
    
    Please do ONE of the following:
    
    Option 1: Environment Variable
        export SUPABASE_SERVICE_KEY=your_key_here
    
    Option 2: Config File
        1. Copy config/config_local.ini.template to config/config_local.ini
        2. Edit config_local.ini and add your service key
    
    To get your service key:
        1. Go to https://supabase.com/dashboard
        2. Select your project
        3. Go to Settings > API
        4. Copy the "service_role" key (NOT the anon key)
    ============================================================
    """)
    return None


def get_sql_type(dtype, col_name):
    """Convert pandas dtype to PostgreSQL type."""
    dtype_str = str(dtype)
    
    # Special handling for known columns
    if 'id' in col_name.lower() and 'index' not in col_name.lower():
        return 'TEXT'
    if 'date' in col_name.lower() or col_name.endswith('_at'):
        return 'TIMESTAMP'
    
    # Type mapping
    if 'int' in dtype_str:
        return 'BIGINT'
    elif 'float' in dtype_str:
        return 'DOUBLE PRECISION'
    elif 'bool' in dtype_str:
        return 'BOOLEAN'
    elif 'datetime' in dtype_str:
        return 'TIMESTAMP'
    else:
        return 'TEXT'


def generate_create_table_sql(table_name, df):
    """Generate CREATE TABLE SQL from DataFrame."""
    columns = []
    
    for col in df.columns:
        sql_type = get_sql_type(df[col].dtype, col)
        # Escape column names that might be reserved words
        safe_col = f'"{col}"' if col.lower() in ['index', 'key', 'type', 'order', 'group'] else col
        columns.append(f"    {safe_col} {sql_type}")
    
    # Add primary key if there's an obvious ID column
    pk_cols = [c for c in df.columns if c.endswith('_id') and 'game' not in c.lower()]
    
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    sql += ",\n".join(columns)
    sql += "\n);"
    
    return sql


def upload_to_supabase(supabase, table_name, df):
    """Upload DataFrame to Supabase table."""
    try:
        # Replace NaN with None for JSON compatibility
        df = df.replace({float('nan'): None, float('inf'): None, float('-inf'): None})
        
        # Convert DataFrame to list of dicts
        records = df.where(pd.notnull(df), None).to_dict('records')
        
        # Clean any remaining NaN/inf values in records
        for record in records:
            for key, value in record.items():
                if isinstance(value, float) and (pd.isna(value) or value == float('inf') or value == float('-inf')):
                    record[key] = None
        
        if not records:
            logger.warning(f"  {table_name}: No records to upload")
            return True
        
        # Upload in batches of 1000
        batch_size = 1000
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            response = supabase.table(table_name).upsert(batch).execute()
        
        logger.info(f"  ✓ {table_name}: {len(records)} rows")
        return True
        
    except Exception as e:
        logger.error(f"  ✗ {table_name}: {str(e)[:100]}")
        return False


def main():
    """Main upload function."""
    print("=" * 60)
    print("BENCHSIGHT SUPABASE UPLOAD")
    print("=" * 60)
    
    # Get credentials
    service_key = get_supabase_key()
    if not service_key:
        sys.exit(1)
    
    # Connect to Supabase
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, service_key)
        logger.info(f"Connected to Supabase: {SUPABASE_URL}")
    except ImportError:
        logger.error("Please install supabase: pip install supabase")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        sys.exit(1)
    
    # Find CSV files
    csv_files = sorted(DATA_DIR.glob("*.csv"))
    logger.info(f"Found {len(csv_files)} CSV files to upload")
    
    # Upload each file
    success = 0
    failed = 0
    
    print("\n--- Uploading Tables ---")
    for csv_file in csv_files:
        table_name = csv_file.stem
        
        try:
            df = pd.read_csv(csv_file, low_memory=False)
            
            # Clean column names (remove trailing underscores, etc.)
            df.columns = [c.rstrip('_') if c.endswith('_') and not c.endswith('__') else c for c in df.columns]
            
            if upload_to_supabase(supabase, table_name, df):
                success += 1
            else:
                failed += 1
                
        except Exception as e:
            logger.error(f"  ✗ {table_name}: {str(e)[:100]}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"UPLOAD COMPLETE: {success}/{len(csv_files)} tables")
    if failed > 0:
        print(f"Failed: {failed} tables")
    print("=" * 60)


if __name__ == "__main__":
    main()
