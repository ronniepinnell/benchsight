#!/usr/bin/env python3
"""
Generate Supabase CREATE TABLE SQL from CSV files.

This script reads all CSV files in data/output and generates:
1. sql/01_create_tables_generated.sql - CREATE TABLE statements
2. Prints summary of tables and columns

Usage:
    python src/generate_schema.py
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "output"
SQL_DIR = BASE_DIR / "sql"


def get_sql_type(dtype, col_name, sample_values):
    """Convert pandas dtype to PostgreSQL type with smarter inference."""
    dtype_str = str(dtype).lower()
    col_lower = col_name.lower()
    
    # ID columns are always TEXT
    if col_lower.endswith('_id') or col_lower == 'id':
        return 'TEXT'
    
    # Date/time columns
    if 'date' in col_lower or col_lower.endswith('_at') or 'timestamp' in col_lower:
        return 'TIMESTAMP'
    
    # Boolean patterns
    if col_lower.startswith('is_') or col_lower.startswith('has_'):
        return 'BOOLEAN'
    
    # Numeric types
    if 'int' in dtype_str:
        return 'BIGINT'
    elif 'float' in dtype_str:
        return 'DOUBLE PRECISION'
    elif 'bool' in dtype_str:
        return 'BOOLEAN'
    elif 'datetime' in dtype_str:
        return 'TIMESTAMP'
    
    # Check if numeric values stored as object
    if dtype_str == 'object' and len(sample_values) > 0:
        try:
            # Try to convert to numeric
            numeric_vals = pd.to_numeric(sample_values.dropna().head(10), errors='coerce')
            if numeric_vals.notna().all():
                if (numeric_vals == numeric_vals.astype(int)).all():
                    return 'BIGINT'
                return 'DOUBLE PRECISION'
        except Exception:
            pass
    
    return 'TEXT'


def escape_column_name(name):
    """Escape PostgreSQL reserved words."""
    reserved = {'index', 'key', 'type', 'order', 'group', 'user', 'table', 
                'column', 'constraint', 'primary', 'foreign', 'check', 'default',
                'null', 'not', 'and', 'or', 'true', 'false', 'between', 'like'}
    
    if name.lower() in reserved or not name[0].isalpha():
        return f'"{name}"'
    return name


def generate_create_sql(table_name, df):
    """Generate CREATE TABLE SQL for a DataFrame."""
    lines = [f"CREATE TABLE IF NOT EXISTS {table_name} ("]
    
    col_defs = []
    for col in df.columns:
        sql_type = get_sql_type(df[col].dtype, col, df[col])
        safe_col = escape_column_name(col)
        col_defs.append(f"    {safe_col} {sql_type}")
    
    lines.append(",\n".join(col_defs))
    lines.append(");")
    
    return "\n".join(lines)


def main():
    """Generate SQL schema from CSV files."""
    logger.info("=" * 60)
    logger.info("GENERATING SUPABASE SCHEMA FROM CSV FILES")
    logger.info("=" * 60)
    
    csv_files = sorted(DATA_DIR.glob("*.csv"))
    logger.info(f"Found {len(csv_files)} CSV files\n")
    
    # Separate dims and facts
    dims = [f for f in csv_files if f.stem.startswith('dim_')]
    facts = [f for f in csv_files if f.stem.startswith('fact_')]
    others = [f for f in csv_files if not f.stem.startswith('dim_') and not f.stem.startswith('fact_')]
    
    # Generate SQL
    sql_lines = [
        "-- ============================================================",
        "-- BENCHSIGHT - CREATE ALL TABLES",
        "-- ============================================================",
        "-- Auto-generated from CSV files",
        f"-- Tables: {len(dims)} dimensions, {len(facts)} facts",
        "-- ============================================================",
        ""
    ]
    
    # Dimensions first
    sql_lines.append("-- ============================================================")
    sql_lines.append("-- DIMENSION TABLES")
    sql_lines.append("-- ============================================================")
    sql_lines.append("")
    
    for csv_file in dims:
        df = pd.read_csv(csv_file, nrows=100, low_memory=False)
        sql = generate_create_sql(csv_file.stem, df)
        sql_lines.append(sql)
        sql_lines.append("")
        logger.info(f"  {csv_file.stem}: {len(df.columns)} columns")
    
    # Facts
    sql_lines.append("")
    sql_lines.append("-- ============================================================")
    sql_lines.append("-- FACT TABLES")
    sql_lines.append("-- ============================================================")
    sql_lines.append("")
    
    for csv_file in facts:
        df = pd.read_csv(csv_file, nrows=100, low_memory=False)
        sql = generate_create_sql(csv_file.stem, df)
        sql_lines.append(sql)
        sql_lines.append("")
        logger.info(f"  {csv_file.stem}: {len(df.columns)} columns")
    
    # Others
    if others:
        sql_lines.append("")
        sql_lines.append("-- ============================================================")
        sql_lines.append("-- OTHER TABLES")
        sql_lines.append("-- ============================================================")
        sql_lines.append("")
        
        for csv_file in others:
            df = pd.read_csv(csv_file, nrows=100, low_memory=False)
            sql = generate_create_sql(csv_file.stem, df)
            sql_lines.append(sql)
            sql_lines.append("")
            logger.info(f"  {csv_file.stem}: {len(df.columns)} columns")
    
    # Write SQL file
    output_file = SQL_DIR / "01_create_tables_generated.sql"
    with open(output_file, 'w') as f:
        f.write("\n".join(sql_lines))
    
    logger.info(f"\n✓ Generated: {output_file}")
    logger.info(f"  Dimensions: {len(dims)}")
    logger.info(f"  Facts: {len(facts)}")
    logger.info(f"  Total: {len(csv_files)}")


if __name__ == "__main__":
    main()
