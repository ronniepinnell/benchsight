#!/usr/bin/env python3
"""
Generate Supabase migration SQL from ETL output changes.

Usage:
    python scripts/generate_migration.py "description of changes"

This compares current CSV headers against the last known schema snapshot
and generates ALTER TABLE statements for new/changed columns.
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

# Paths
OUTPUT_DIR = Path("data/output")
MIGRATIONS_DIR = Path("supabase/migrations")
SCHEMA_SNAPSHOT = Path("config/schema_snapshot.json")

# Type mapping from pandas to PostgreSQL
DTYPE_MAP = {
    'int64': 'BIGINT',
    'float64': 'DOUBLE PRECISION',
    'object': 'TEXT',
    'bool': 'BOOLEAN',
    'datetime64[ns]': 'TIMESTAMP',
}

def get_csv_schema(csv_path: Path) -> dict:
    """Get column names and inferred types from CSV."""
    df = pd.read_csv(csv_path, nrows=100)
    schema = {}
    for col in df.columns:
        # Lowercase column names (Supabase convention)
        col_lower = col.lower()
        dtype = str(df[col].dtype)
        pg_type = DTYPE_MAP.get(dtype, 'TEXT')
        schema[col_lower] = pg_type
    return schema

def load_schema_snapshot() -> dict:
    """Load the last known schema snapshot."""
    if SCHEMA_SNAPSHOT.exists():
        with open(SCHEMA_SNAPSHOT) as f:
            return json.load(f)
    return {}

def save_schema_snapshot(schema: dict):
    """Save current schema as snapshot."""
    with open(SCHEMA_SNAPSHOT, 'w') as f:
        json.dump(schema, f, indent=2)

def generate_migration_sql(old_schema: dict, new_schema: dict) -> list:
    """Generate ALTER statements for schema differences."""
    statements = []

    for table_name, new_columns in new_schema.items():
        old_columns = old_schema.get(table_name, {})

        # New table
        if not old_columns:
            cols = ", ".join([f'"{col}" {dtype}' for col, dtype in new_columns.items()])
            statements.append(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({cols});')
            continue

        # New columns
        for col, dtype in new_columns.items():
            if col not in old_columns:
                statements.append(
                    f'ALTER TABLE "{table_name}" ADD COLUMN IF NOT EXISTS "{col}" {dtype};'
                )

        # Removed columns (commented out - don't auto-drop)
        for col in old_columns:
            if col not in new_columns:
                statements.append(
                    f'-- REMOVED: ALTER TABLE "{table_name}" DROP COLUMN "{col}";'
                )

    return statements

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_migration.py 'description'")
        sys.exit(1)

    description = sys.argv[1].lower().replace(' ', '_').replace('-', '_')
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Load old schema
    old_schema = load_schema_snapshot()

    # Build new schema from CSVs
    new_schema = {}
    csv_files = list(OUTPUT_DIR.glob("*.csv"))

    print(f"Scanning {len(csv_files)} CSV files...")

    for csv_path in csv_files:
        table_name = csv_path.stem  # filename without extension
        try:
            new_schema[table_name] = get_csv_schema(csv_path)
        except Exception as e:
            print(f"  Warning: Could not read {csv_path.name}: {e}")

    # Generate migration
    statements = generate_migration_sql(old_schema, new_schema)

    if not statements:
        print("No schema changes detected.")
        return

    # Write migration file
    migration_name = f"{timestamp}_{description}.sql"
    migration_path = MIGRATIONS_DIR / migration_name

    content = f"""-- Migration: {description}
-- Generated: {datetime.now().isoformat()}
-- Changes detected: {len(statements)}

"""
    content += "\n".join(statements)

    with open(migration_path, 'w') as f:
        f.write(content)

    print(f"\nGenerated migration: {migration_path}")
    print(f"  {len(statements)} changes detected")
    print("\nReview the migration, then apply with:")
    print(f"  supabase db push")
    print("  OR run manually in Supabase SQL Editor")

    # Update snapshot
    save_schema_snapshot(new_schema)
    print(f"\nSchema snapshot updated: {SCHEMA_SNAPSHOT}")

if __name__ == "__main__":
    main()
