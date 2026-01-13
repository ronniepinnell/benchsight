#!/usr/bin/env python3
"""
BenchSight ETL - Robust Production Upload
Handles messy data, type mismatches, nulls, encoding issues
Works with existing schema_from_csvs schema
"""

import os
import sys
import math
import json
import logging
import configparser
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# =============================================================================
# CONFIGURATION - Load from config/config_local.ini
# =============================================================================
config = configparser.ConfigParser()
config_path = Path(__file__).parent.parent.parent / 'config' / 'config_local.ini'
config.read(config_path)

SUPABASE_URL = config.get('supabase', 'url', fallback="https://uuaowslhpgyiudmbvqze.supabase.co")
SUPABASE_KEY = config.get('supabase', 'service_key', fallback="")

BLB_FILE = "data/raw/BLB_TABLES.xlsx"
OUTPUT_DIR = "data/output"
BATCH_SIZE = 100
MAX_RETRIES = 3

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

# =============================================================================
# ROBUST VALUE CLEANING - HANDLES ALL EDGE CASES
# =============================================================================

def is_null(val: Any) -> bool:
    """Check if value should be treated as NULL."""
    if val is None:
        return True
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return True
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ('', 'nan', 'none', 'null', 'na', 'n/a', '#n/a', 'nat', '-', '--', 'n/a', '#value!', '#ref!', '#div/0!'):
            return True
    if pd.isna(val):
        return True
    return False


def clean_string(val: Any) -> Optional[str]:
    """Clean and convert value to string."""
    if is_null(val):
        return None
    
    # Handle bytes
    if isinstance(val, bytes):
        try:
            val = val.decode('utf-8')
        except Exception:
            val = val.decode('latin-1', errors='ignore')
    
    s = str(val).strip()
    
    # Remove BOM and control characters
    s = s.replace('\ufeff', '').replace('\x00', '')
    
    # Limit length to prevent DB issues
    if len(s) > 10000:
        s = s[:10000]
    
    return s if s else None


def clean_integer(val: Any) -> Optional[int]:
    """Clean and convert value to integer."""
    if is_null(val):
        return None
    
    try:
        # Handle string numbers
        if isinstance(val, str):
            val = val.strip().replace(',', '').replace('$', '')
            if val == '':
                return None
        
        # Handle booleans
        if isinstance(val, bool):
            return 1 if val else 0
        
        # Convert
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return None
        return int(f)
    except (ValueError, TypeError, OverflowError):
        return None


def clean_float(val: Any) -> Optional[float]:
    """Clean and convert value to float."""
    if is_null(val):
        return None
    
    try:
        if isinstance(val, str):
            val = val.strip().replace(',', '').replace('$', '').replace('%', '')
            if val == '':
                return None
        
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return None
        
        # Round to reasonable precision
        return round(f, 6)
    except (ValueError, TypeError, OverflowError):
        return None


def clean_boolean(val: Any) -> Optional[bool]:
    """Clean and convert value to boolean."""
    if is_null(val):
        return None
    
    if isinstance(val, bool):
        return val
    
    if isinstance(val, (int, float)):
        return bool(val)
    
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ('true', '1', 'yes', 'y', 't'):
            return True
        if v in ('false', '0', 'no', 'n', 'f'):
            return False
    
    return None


def clean_value(val: Any, col_name: str = '') -> Any:
    """
    Universal value cleaner - determines type from column name patterns
    and cleans accordingly. Falls back to string if unsure.
    """
    if is_null(val):
        return None
    
    col_lower = col_name.lower()
    
    # Boolean columns (is_*, has_*, *_yn, etc.)
    bool_patterns = ['is_', 'has_', '_yn', 'restricted', 'norad', 'csah', 'credits_', 'affects_', 'requires_']
    if any(p in col_lower for p in bool_patterns):
        result = clean_boolean(val)
        if result is not None:
            return result
    
    # Integer columns (common patterns)
    int_patterns = ['_id', 'game_id', 'player_id', 'team_id', 'season_id', 'goals', 'assists', 'assist', 
                    'pim', 'shutouts', '_count', '_index', 'period', 'round', 'position', 'number',
                    'birth_year', 'age', '_goals', '_pts', '_w', '_l', '_t', 'seeding', 'rating',
                    'skill_rating', 'difficulty', 'sort_order', 'display_order']
    
    # Check if it should be an integer
    if any(col_lower.endswith(p) or p in col_lower for p in int_patterns):
        # But some *_id columns are TEXT (like player_id = "P100001")
        if isinstance(val, str) and not val.replace('-', '').replace('.', '').isdigit():
            return clean_string(val)
        result = clean_integer(val)
        if result is not None:
            return result
    
    # Float columns
    float_patterns = ['_pct', 'percent', '_rate', 'x_', 'y_', '_min', '_max', '_avg', 
                      'multiplier', 'weight', 'duration', 'seconds', 'per_60']
    if any(p in col_lower for p in float_patterns):
        result = clean_float(val)
        if result is not None:
            return result
    
    # Default to string
    return clean_string(val)


# =============================================================================
# DATA LOADING
# =============================================================================

def load_excel_safe(filepath: str, sheet_name: str) -> Optional[pd.DataFrame]:
    """Load Excel sheet with multiple encoding attempts."""
    try:
        df = pd.read_excel(filepath, sheet_name=sheet_name, dtype=str)
        return df
    except Exception as e:
        logger.warning(f"Failed to load {sheet_name}: {e}")
        return None


def load_csv_safe(filepath: str) -> Optional[pd.DataFrame]:
    """Load CSV with multiple encoding attempts."""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for enc in encodings:
        try:
            df = pd.read_csv(filepath, encoding=enc, dtype=str, low_memory=False)
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.warning(f"Failed to load {filepath} with {enc}: {e}")
            continue
    
    logger.error(f"Could not load {filepath} with any encoding")
    return None


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean DataFrame column names and remove junk columns."""
    # Clean column names
    df.columns = [str(c).strip().replace('\ufeff', '') for c in df.columns]
    
    # Drop index columns and unnamed columns
    drop_cols = [c for c in df.columns if c.lower() in ('index', 'unnamed: 0', 'level_0') 
                 or c.startswith('Unnamed:') or c.startswith('_')]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')
    
    return df


def transform_records(df: pd.DataFrame) -> List[Dict]:
    """Transform DataFrame to list of cleaned records."""
    records = []
    
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            val = row[col]
            cleaned = clean_value(val, col)
            if cleaned is not None:
                record[col] = cleaned
        
        # Only include non-empty records
        if record:
            records.append(record)
    
    return records


# =============================================================================
# SUPABASE UPLOAD WITH RETRY
# =============================================================================

def upload_batch(table_name: str, records: List[Dict], retry: int = 0) -> tuple:
    """Upload a batch with retry logic."""
    if not records:
        return 0, []
    
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    
    try:
        resp = requests.post(url, headers=HEADERS, json=records, timeout=60)
        
        if resp.status_code in [200, 201]:
            return len(records), []
        
        # Handle specific errors
        error_text = resp.text[:300]
        
        # If column not found, log and skip
        if 'Could not find' in error_text:
            logger.warning(f"Schema mismatch: {error_text}")
            return 0, [error_text]
        
        # If type error, try to fix and retry
        if 'invalid input syntax' in error_text and retry < MAX_RETRIES:
            logger.warning(f"Type error, retrying with string conversion: {error_text}")
            # Convert all values to strings and retry
            string_records = [{k: str(v) if v is not None else None for k, v in r.items()} for r in records]
            return upload_batch(table_name, string_records, retry + 1)
        
        return 0, [f"{resp.status_code}: {error_text}"]
        
    except requests.exceptions.Timeout:
        if retry < MAX_RETRIES:
            logger.warning(f"Timeout, retrying... (attempt {retry + 1})")
            return upload_batch(table_name, records, retry + 1)
        return 0, ["Timeout after retries"]
    
    except Exception as e:
        return 0, [str(e)[:200]]


def upload_table(table_name: str, records: List[Dict]) -> tuple:
    """Upload all records for a table in batches."""
    if not records:
        return 0, []
    
    total_uploaded = 0
    all_errors = []
    
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        uploaded, errors = upload_batch(table_name, batch)
        total_uploaded += uploaded
        all_errors.extend(errors)
        
        # Progress indicator for large tables
        if len(records) > 1000 and i % 1000 == 0:
            logger.info(f"  Progress: {i}/{len(records)}")
    
    return total_uploaded, all_errors


# =============================================================================
# TABLE MAPPINGS - Excel sheet to DB table
# =============================================================================

# Maps Excel sheet names to Supabase table names
EXCEL_TO_TABLE = {
    'dim_league': 'dim_league',
    'dim_season': 'dim_season', 
    'dim_team': 'dim_team',
    'dim_player': 'dim_player',
    'dim_schedule': 'dim_schedule',
    'dim_rink_zone': 'dim_rink_zone',
    'dim_rink_zone': 'dim_rink_zone',
    'dim_playerurlref': 'dim_playerurlref',
    'dim_randomnames': 'dim_randomnames',
    'fact_gameroster': 'fact_gameroster',
    'fact_leadership': 'fact_leadership',
    'fact_registration': 'fact_registration',
    'fact_draft': 'fact_draft',
    'Fact_PlayerGames': 'fact_playergames',
}

# Column renames (Excel column -> DB column) if needed
COLUMN_RENAMES = {
    'fact_playergames': {
        'ID': 'game_type_id',
        'Date': 'game_date', 
        'Type': 'game_type',
        'Team': 'team',
        'Opp': 'opp',
        '#': 'jersey_number',
        'Player': 'player',
        'Position': 'position',
        'GP': 'gp',
        'G': 'goals',
        'A': 'assists',
        'GA': 'goals_against',
        'PIM': 'pim',
        'SO': 'shutouts',
        'Rank': 'skill_rank',
        'ID2': 'id2',
        'ID3': 'id3',
        'Season': 'season',
        'SeasonPlayerID': 'season_player_id'
    }
}


# =============================================================================
# MAIN ETL
# =============================================================================

def run_etl(source: str = 'excel', upload: bool = True):
    """
    Run ETL pipeline.
    
    Args:
        source: 'excel' to load from BLB_Tables.xlsx, 'csv' to load from data/output CSVs
        upload: Whether to upload to Supabase
    """
    print("=" * 70)
    print("BENCHSIGHT ETL - PRODUCTION UPLOAD")
    print("=" * 70)
    
    # Test connection
    if upload:
        print("\nTesting Supabase connection...")
        try:
            resp = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                print(f"ERROR: Connection failed ({resp.status_code})")
                return
            print("✓ Connected")
        except Exception as e:
            print(f"ERROR: {e}")
            return
    
    total_uploaded = 0
    total_errors = []
    
    if source == 'excel':
        # Load from Excel
        print(f"\nLoading from {BLB_FILE}...")
        
        if not os.path.exists(BLB_FILE):
            print(f"ERROR: {BLB_FILE} not found")
            return
        
        xlsx = pd.ExcelFile(BLB_FILE)
        print(f"Found sheets: {xlsx.sheet_names}")
        
        for sheet_name in xlsx.sheet_names:
            table_name = EXCEL_TO_TABLE.get(sheet_name, sheet_name.lower())
            
            print(f"\n{table_name}...")
            
            # Load
            df = load_excel_safe(BLB_FILE, sheet_name)
            if df is None or len(df) == 0:
                print("  SKIP: empty or failed to load")
                continue
            
            # Clean
            df = clean_dataframe(df)
            
            # Rename columns if needed
            if table_name in COLUMN_RENAMES:
                df = df.rename(columns=COLUMN_RENAMES[table_name])
            
            # Transform
            records = transform_records(df)
            print(f"  Loaded: {len(records)} records")
            
            # Upload
            if upload and records:
                uploaded, errors = upload_table(table_name, records)
                print(f"  Uploaded: {uploaded} rows")
                if errors:
                    for e in errors[:2]:
                        print(f"  ERROR: {e}")
                total_uploaded += uploaded
                total_errors.extend(errors)
    
    else:
        # Load from CSVs
        print(f"\nLoading from {OUTPUT_DIR}/*.csv...")
        
        csv_files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.csv')])
        
        for filename in csv_files:
            table_name = filename.replace('.csv', '')
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            print(f"\n{table_name}...")
            
            # Load
            df = load_csv_safe(filepath)
            if df is None or len(df) == 0:
                print("  SKIP: empty or failed to load")
                continue
            
            # Clean
            df = clean_dataframe(df)
            
            # Transform  
            records = transform_records(df)
            print(f"  Loaded: {len(records)} records")
            
            # Upload
            if upload and records:
                uploaded, errors = upload_table(table_name, records)
                print(f"  Uploaded: {uploaded} rows")
                if errors:
                    for e in errors[:2]:
                        print(f"  ERROR: {e}")
                total_uploaded += uploaded
                total_errors.extend(errors)
    
    print(f"\n{'=' * 70}")
    print(f"COMPLETE: {total_uploaded} rows uploaded")
    if total_errors:
        print(f"ERRORS: {len(total_errors)} (see above)")
    print("=" * 70)


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='BenchSight ETL Upload')
    parser.add_argument('--source', choices=['excel', 'csv'], default='csv',
                        help='Data source: excel (BLB_Tables.xlsx) or csv (data/output/)')
    parser.add_argument('--no-upload', action='store_true',
                        help='Skip uploading, just transform')
    parser.add_argument('--table', type=str,
                        help='Upload single table only')
    
    args = parser.parse_args()
    
    run_etl(source=args.source, upload=not args.no_upload)
