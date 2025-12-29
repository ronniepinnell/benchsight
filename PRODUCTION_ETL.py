#!/usr/bin/env python3
"""
BENCHSIGHT PRODUCTION ETL
=========================
Schema-driven upload to Supabase with bulletproof error handling.

Usage:
    python PRODUCTION_ETL.py              # Upload all
    python PRODUCTION_ETL.py --dry-run    # Preview only
    python PRODUCTION_ETL.py --table X    # Single table
"""

import os
import sys
import json
import math
import logging
import argparse
from pathlib import Path
from datetime import datetime

import pandas as pd

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).parent
SCHEMA_FILE = BASE_DIR / "config" / "supabase_schema.json"
OUTPUT_DIR = BASE_DIR / "data" / "output"
LOG_DIR = BASE_DIR / "logs"

BATCH_SIZE = 100
MAX_RETRIES = 3
TIMEOUT = 60

# =============================================================================
# LOGGING
# =============================================================================

LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# =============================================================================
# DATA CLEANING - BULLETPROOF
# =============================================================================

def is_null(val):
    """Comprehensive null detection."""
    if val is None:
        return True
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return True
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ("", "nan", "none", "null", "na", "n/a", "#n/a", "nat",
                 "-", "--", "#value!", "#ref!", "#div/0!", "#name?", "#num!", "<na>"):
            return True
    try:
        if pd.isna(val):
            return True
    except (TypeError, ValueError):
        pass
    return False


def clean_value(val):
    """Clean value for JSON. Returns None for nulls."""
    if is_null(val):
        return None
    
    if isinstance(val, bytes):
        try:
            val = val.decode("utf-8")
        except UnicodeDecodeError:
            val = val.decode("latin-1", errors="ignore")
    
    s = str(val).strip()
    s = s.replace("\ufeff", "").replace("\x00", "")
    
    if len(s) > 10000:
        s = s[:10000]
    
    return s if s else None


def clean_dataframe(df):
    """Clean DataFrame columns."""
    df.columns = [str(c).strip().replace("\ufeff", "") for c in df.columns]
    
    drop_patterns = ["Unnamed:", "_export_timestamp", "_source_file", "level_0"]
    drop_cols = [c for c in df.columns
                 if any(p in c for p in drop_patterns) or (c.startswith("_") and c != "_id")]
    
    return df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")


def to_records(df, columns):
    """
    Convert DataFrame to records with CONSISTENT keys.
    
    CRITICAL: All records must have the same keys for Supabase batch insert.
    We include NULL values explicitly to ensure key consistency.
    """
    records = []
    for _, row in df.iterrows():
        record = {}
        for col in columns:
            if col in df.columns:
                val = clean_value(row[col])
                record[col] = val  # Include even if None!
        
        # Only skip if ALL values are None
        if any(v is not None for v in record.values()):
            records.append(record)
    
    return records


def load_csv(filepath):
    """Load CSV with encoding detection."""
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            return pd.read_csv(filepath, encoding=enc, dtype=str, low_memory=False)
        except UnicodeDecodeError:
            continue
        except Exception:
            return None
    return None


# =============================================================================
# SCHEMA
# =============================================================================

def load_schema():
    """Load schema from JSON file."""
    if not SCHEMA_FILE.exists():
        log.error(f"Schema file not found: {SCHEMA_FILE}")
        sys.exit(1)
    
    with open(SCHEMA_FILE) as f:
        data = json.load(f)
    
    schema = data.get("tables", {})
    log.info(f"Loaded schema: {len(schema)} tables")
    return schema


def filter_to_schema(df, table, schema):
    """Keep only columns that exist in schema."""
    if table not in schema:
        return df, False
    
    valid_cols = set(schema[table])
    csv_cols = set(df.columns)
    
    # Keep only valid columns
    keep = [c for c in df.columns if c in valid_cols]
    
    if not keep:
        return df, False
    
    return df[keep], True


# =============================================================================
# SUPABASE UPLOAD
# =============================================================================

def get_supabase_client():
    """Get Supabase client from environment or config."""
    try:
        from supabase import create_client
    except ImportError:
        log.error("supabase package not installed. Run: pip install supabase")
        sys.exit(1)
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    # Try importing from src/config.py first (where credentials already exist!)
    if not url or not key:
        try:
            sys.path.insert(0, str(BASE_DIR / "src"))
            from config import SUPABASE_URL, SUPABASE_KEY
            url = url or SUPABASE_URL
            key = key or SUPABASE_KEY
            log.info("Loaded credentials from src/config.py")
        except ImportError:
            pass
    
    # Try config files if still not set
    if not url or not key:
        config_files = [
            BASE_DIR / "config" / "config_local.ini",
            BASE_DIR / "config" / "config.ini",
            BASE_DIR / ".env",
        ]
        
        for config_file in config_files:
            if config_file.exists():
                if config_file.suffix == ".env":
                    with open(config_file) as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                k, v = line.split("=", 1)
                                k, v = k.strip(), v.strip().strip('"').strip("'")
                                if k == "SUPABASE_URL" and not url:
                                    url = v
                                elif k == "SUPABASE_KEY" and not key:
                                    key = v
                else:
                    import configparser
                    config = configparser.ConfigParser()
                    config.read(config_file)
                    for section in ["supabase", "database"]:
                        if config.has_section(section):
                            url = url or config.get(section, "url", fallback=None)
                            key = key or config.get(section, "key", fallback=None)
                
                if url and key:
                    log.info(f"Loaded credentials from {config_file.name}")
                    break
    
    if not url or not key:
        log.error("Supabase credentials not found!")
        log.error("Add credentials to src/config.py, config/config_local.ini, or environment variables")
        sys.exit(1)
    
    return create_client(url, key)


def clear_table(client, table):
    """Delete all rows from table."""
    try:
        # Supabase requires a filter for delete, use a always-true condition
        client.table(table).delete().neq("id", -999999).execute()
        return True
    except Exception as e:
        # Try alternate approach - some tables may not have 'id'
        try:
            client.table(table).delete().gte("id", 0).execute()
            return True
        except:
            pass
        try:
            # Last resort - delete with any column
            client.table(table).delete().not_.is_("id", "null").execute()
            return True
        except Exception as e2:
            log.warning(f"  Could not clear {table}: {str(e2)[:50]}")
            return False


def upload_table(client, table, records, dry_run=False, clear_first=True):
    """Upload records to table with batching and retries."""
    if not records:
        return 0, 0
    
    if dry_run:
        return len(records), 0
    
    # Clear existing data first
    if clear_first:
        if clear_table(client, table):
            log.info(f"  Cleared existing data")
    
    uploaded = 0
    errors = 0
    
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        
        for attempt in range(MAX_RETRIES):
            try:
                result = client.table(table).insert(batch).execute()
                uploaded += len(batch)
                
                if len(records) > 2000 and (i + BATCH_SIZE) % 2000 == 0:
                    log.info(f"    {table}: {i + BATCH_SIZE}/{len(records)}")
                
                break
                
            except Exception as e:
                error_msg = str(e)
                if attempt < MAX_RETRIES - 1:
                    continue
                else:
                    log.error(f"  {table} ERROR: {error_msg[:100]}")
                    errors += len(batch)
    
    return uploaded, errors


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="BenchSight Production ETL")
    parser.add_argument("--dry-run", action="store_true", help="Preview without uploading")
    parser.add_argument("--table", help="Upload single table")
    parser.add_argument("--validate", action="store_true", help="Validate only")
    parser.add_argument("--no-clear", action="store_true", help="Don't clear tables before upload (append mode)")
    args = parser.parse_args()
    
    print("=" * 70)
    print("BENCHSIGHT PRODUCTION ETL")
    print("=" * 70)
    
    # Load schema
    schema = load_schema()
    
    # Get Supabase client (unless dry run)
    client = None
    if not args.dry_run and not args.validate:
        log.info("Testing Supabase connection...")
        client = get_supabase_client()
        try:
            client.table("dim_league").select("*").limit(1).execute()
            log.info("✓ Connected")
        except Exception as e:
            log.error(f"Connection failed: {e}")
            sys.exit(1)
    
    log.info(f"\nMode: {'DRY RUN' if args.dry_run else 'VALIDATE' if args.validate else 'UPLOAD'}")
    if not args.dry_run and not args.validate:
        log.info(f"Clear tables first: {'NO (append)' if args.no_clear else 'YES (replace)'}")
    
    # Find CSVs
    csv_files = sorted(OUTPUT_DIR.glob("*.csv"))
    if args.table:
        csv_files = [f for f in csv_files if f.stem == args.table]
    
    log.info(f"Found {len(csv_files)} CSV files")
    
    total_uploaded = 0
    total_errors = 0
    tables_processed = 0
    tables_skipped = 0
    
    for csv_path in csv_files:
        table = csv_path.stem
        
        # Load CSV
        df = load_csv(csv_path)
        if df is None:
            log.warning(f"{table}: SKIP (load failed)")
            tables_skipped += 1
            continue
        
        # Clean
        df = clean_dataframe(df)
        
        # Skip if not in schema
        if table not in schema:
            log.info(f"{table}: SKIP (not in schema)")
            tables_skipped += 1
            continue
        
        # Filter to schema columns
        df, valid = filter_to_schema(df, table, schema)
        if not valid:
            log.warning(f"{table}: SKIP (no valid columns)")
            tables_skipped += 1
            continue
        
        # Skip empty
        if len(df) == 0:
            log.info(f"{table}: SKIP (empty)")
            tables_skipped += 1
            continue
        
        # Convert to records WITH CONSISTENT KEYS
        schema_cols = schema[table]
        csv_cols = [c for c in schema_cols if c in df.columns]
        records = to_records(df, csv_cols)
        
        if not records:
            log.info(f"{table}: SKIP (no valid records)")
            tables_skipped += 1
            continue
        
        log.info(f"{table}: {len(records)} records, {len(csv_cols)} columns")
        
        if args.validate:
            tables_processed += 1
            continue
        
        # Upload
        clear_first = not args.no_clear
        uploaded, errors = upload_table(client, table, records, args.dry_run, clear_first)
        
        if not args.dry_run:
            if errors == 0:
                log.info(f"  ✓ {uploaded} rows")
            # Errors already logged in upload_table
        
        total_uploaded += uploaded
        total_errors += errors
        tables_processed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    log.info(f"Tables processed: {tables_processed}")
    log.info(f"Tables skipped:   {tables_skipped}")
    log.info(f"Rows {'would upload' if args.dry_run else 'uploaded'}: {total_uploaded}")
    if total_errors > 0:
        log.info(f"Errors: {total_errors}")
    log.info(f"Log: {log_file}")
    print("=" * 70)
    
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
