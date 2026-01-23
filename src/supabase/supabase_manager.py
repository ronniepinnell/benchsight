"""
================================================================================
BENCHSIGHT SUPABASE MANAGER
================================================================================
Handles all Supabase operations: schema creation, data upload, sync.

This is the SINGLE source of truth for Supabase integration.
All other Supabase scripts should import from here.

Usage:
    from src.supabase.supabase_manager import SupabaseManager
    
    mgr = SupabaseManager()
    mgr.reset_schema()      # Drop all tables, recreate schema
    mgr.upload_all()        # Upload all data from data/output/
================================================================================
"""

import os
import sys
import configparser
import logging
import math
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SupabaseManager')


class SupabaseManager:
    """
    Manages all Supabase operations for BenchSight.

    Reads configuration via config_loader (supports BENCHSIGHT_ENV).
    """

    # Tables to skip (system tables, etc.)
    SKIP_TABLES = {'VERSION', 'TABLE_MANIFEST'}

    # Batch size for uploads
    BATCH_SIZE = 500

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize Supabase manager.

        Args:
            config_path: Path to config file (optional, uses config_loader by default)
        """
        # Use config_loader for environment-aware config
        from config.config_loader import load_config
        cfg = load_config(config_path)

        self.url = cfg.supabase_url
        self.key = cfg.supabase_service_key

        if not self.url or not self.key:
            raise ValueError("Supabase URL and service_key required in config")
        
        # Data directory
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / 'data' / 'output'
        
        # Initialize client
        self._client = None
        
        logger.info(f"SupabaseManager initialized")
        logger.info(f"  URL: {self.url}")
        logger.info(f"  Data dir: {self.data_dir}")
    
    @property
    def client(self):
        """Lazy-load Supabase client."""
        if self._client is None:
            try:
                from supabase import create_client
                self._client = create_client(self.url, self.key)
            except ImportError:
                raise ImportError("Install supabase: pip install supabase --break-system-packages")
        return self._client
    
    def _get_tables(self) -> List[str]:
        """Get list of CSV tables to upload."""
        tables = []
        for csv_file in sorted(self.data_dir.glob('*.csv')):
            name = csv_file.stem
            if name not in self.SKIP_TABLES:
                tables.append(name)
        return tables
    
    def _clean_value(self, val: Any) -> Any:
        """
        Clean a value for JSON serialization and Supabase upload.
        
        Handles: NaN, Inf, numpy types, etc.
        IMPORTANT: Converts whole-number floats to integers for BIGINT columns.
        """
        # None/null
        if val is None:
            return None
        
        # Pandas NA
        if pd.isna(val):
            return None
        
        # NumPy types
        if isinstance(val, (np.integer, np.int64, np.int32)):
            return int(val)
        if isinstance(val, (np.floating, np.float64, np.float32)):
            if np.isnan(val) or np.isinf(val):
                return None
            # Convert whole-number floats to int (e.g., 5.0 -> 5)
            if val == int(val):
                return int(val)
            return float(val)
        if isinstance(val, np.bool_):
            return bool(val)
        
        # Python float (check for nan/inf)
        if isinstance(val, float):
            if math.isnan(val) or math.isinf(val):
                return None
            # Convert whole-number floats to int (e.g., 5.0 -> 5)
            if val == int(val):
                return int(val)
            return val
        
        # Python bool - check BEFORE int (bool is subclass of int)
        if isinstance(val, bool):
            return val
        
        # Python int - pass through (iterrows converts np.int64 to int)
        if isinstance(val, int):
            return val
        
        # Strings
        if isinstance(val, str):
            # Clean empty/whitespace strings and null-like values
            stripped = val.strip()
            # Common null-like values including data codes
            null_values = ('nan', 'none', 'null', 'nat', 'n/a', 'na', '-', 'fa', 'ir', 'tbd', 'unknown')
            if stripped == '' or stripped.lower() in null_values:
                return None
            
            # Try to convert numeric strings to numbers
            # This handles cases where CSV has '2' instead of 2
            try:
                # Try integer first
                if stripped.isdigit() or (stripped.startswith('-') and stripped[1:].isdigit()):
                    return int(stripped)
                # Try float
                float_val = float(stripped)
                # If it's a whole number, return as int
                if float_val == int(float_val):
                    return int(float_val)
                return float_val
            except (ValueError, OverflowError):
                # Not a number, return as string
                return val
        
        # Everything else -> string
        return str(val)
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean a DataFrame for upload.
        
        - Lowercase column names
        - Remove spaces from column names
        """
        # Lowercase columns and remove spaces
        df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]
        
        return df
    
    def _df_to_records(self, df: pd.DataFrame) -> List[Dict]:
        """Convert DataFrame to list of clean records."""
        records = []
        for _, row in df.iterrows():
            record = {}
            for col, val in row.items():
                cleaned = self._clean_value(val)
                record[col] = cleaned
            records.append(record)
        return records
    
    def _infer_pg_type(self, series: pd.Series, col_name: str) -> str:
        """
        Infer PostgreSQL type from pandas Series by analyzing actual data.
        
        Returns appropriate PostgreSQL type based on data content.
        """
        dtype = str(series.dtype)
        
        # Get non-null values for analysis
        non_null = series.dropna()
        if len(non_null) == 0:
            return 'TEXT'  # No data to infer from
        
        # Boolean types
        if dtype == 'bool':
            return 'BOOLEAN'
        
        # Integer types - use BIGINT for safety
        if 'int' in dtype:
            return 'BIGINT'
        
        # Float types
        if 'float' in dtype:
            # Check if all values are actually integers stored as floats
            if (non_null % 1 == 0).all():
                # Check range - if small, might be an ID that got float-converted
                if non_null.max() < 2147483647 and non_null.min() > -2147483648:
                    return 'BIGINT'
            return 'DOUBLE PRECISION'
        
        # Datetime types
        if 'datetime' in dtype:
            return 'TIMESTAMPTZ'
        
        # Object type - need to analyze contents
        if dtype == 'object':
            # Sample values for analysis
            sample = non_null.head(100).astype(str)
            
            # Check for boolean-like values
            unique_lower = set(s.lower().strip() for s in sample if s.strip())
            if unique_lower and unique_lower <= {'true', 'false', '1', '0', 'yes', 'no', 't', 'f'}:
                return 'BOOLEAN'
            
            # Check for numeric values - MUST be ALL numeric to use BIGINT
            try:
                numeric_vals = pd.to_numeric(non_null.head(100), errors='coerce')
                non_null_numeric = numeric_vals.dropna()
                
                # Only use BIGINT if ALL values converted successfully (100%, not 90%)
                if len(non_null_numeric) == len(non_null.head(100)):
                    # Check if integers
                    if (non_null_numeric % 1 == 0).all():
                        return 'BIGINT'
                    return 'DOUBLE PRECISION'
            except:
                pass
            
            # Check for date-like strings
            if col_name in ('date', 'game_date', 'created_at', 'updated_at', 'timestamp'):
                return 'TIMESTAMPTZ'
            
            # Check typical ID column names
            if col_name.endswith('_id') or col_name == 'id':
                # IDs should be TEXT to handle both numeric and string IDs
                return 'TEXT'
        
        # Default to TEXT for strings and unknown types
        return 'TEXT'
    
    def generate_create_sql(self, table_name: str, df: pd.DataFrame) -> str:
        """
        Generate CREATE TABLE SQL from DataFrame with proper type inference.
        
        Args:
            table_name: Name of the table
            df: DataFrame with data
            
        Returns:
            CREATE TABLE SQL statement
        """
        columns = []
        for col in df.columns:
            pg_type = self._infer_pg_type(df[col], col)
            # Quote column names to handle reserved words and special chars
            columns.append(f'    "{col}" {pg_type}')
        
        sql = f'CREATE TABLE IF NOT EXISTS public."{table_name}" (\n'
        sql += ',\n'.join(columns)
        sql += '\n);'
        
        return sql
    
    def upload_table(self, table_name: str, df: pd.DataFrame = None) -> Tuple[int, List[str]]:
        """
        Upload a single table to Supabase.
        
        Args:
            table_name: Name of the table
            df: DataFrame to upload (if None, reads from CSV)
            
        Returns:
            Tuple of (rows_uploaded, errors)
        """
        errors = []
        
        # Load data if not provided
        if df is None:
            csv_path = self.data_dir / f'{table_name}.csv'
            if not csv_path.exists():
                return 0, [f"CSV not found: {csv_path}"]
            df = pd.read_csv(csv_path, low_memory=False)
        
        if len(df) == 0:
            logger.info(f"  SKIP {table_name}: empty")
            return 0, []
        
        # Clean DataFrame
        df = self._clean_dataframe(df)
        
        # Convert to records
        records = self._df_to_records(df)
        
        # Upload in batches
        uploaded = 0
        for i in range(0, len(records), self.BATCH_SIZE):
            batch = records[i:i + self.BATCH_SIZE]
            try:
                self.client.table(table_name).insert(batch).execute()
                uploaded += len(batch)
            except Exception as e:
                error_msg = str(e)
                # Extract meaningful error
                if 'message' in error_msg:
                    try:
                        import json
                        err_data = json.loads(error_msg.replace("'", '"'))
                        error_msg = err_data.get('message', error_msg)
                    except:
                        pass
                errors.append(f"Batch {i}: {error_msg[:100]}")
                logger.error(f"  ERROR {table_name} batch {i}: {error_msg[:100]}")
        
        if uploaded > 0:
            logger.info(f"  ✓ {table_name}: {uploaded:,} rows")
        
        return uploaded, errors
    
    def reset_schema(self) -> Dict[str, Any]:
        """
        Generate SQL to drop all tables and recreate schema from CSV files.
        
        Returns:
            Dict with results
        """
        logger.info("=" * 60)
        logger.info("GENERATING SUPABASE SCHEMA")
        logger.info("=" * 60)
        
        results = {
            'tables_created': 0,
            'errors': [],
            'type_summary': {}
        }
        
        tables = self._get_tables()
        logger.info(f"Found {len(tables)} tables to process")
        
        # Generate SQL for all tables
        sql_statements = []
        
        # First: DROP all tables
        logger.info("\nPhase 1: Generating DROP statements...")
        for table_name in tables:
            sql_statements.append(f'DROP TABLE IF EXISTS public."{table_name}" CASCADE;')
        
        # Then: CREATE all tables with proper types
        logger.info("Phase 2: Generating CREATE statements with type inference...")
        type_counts = {'TEXT': 0, 'BIGINT': 0, 'DOUBLE PRECISION': 0, 'BOOLEAN': 0, 'TIMESTAMPTZ': 0}
        
        for table_name in tables:
            csv_path = self.data_dir / f'{table_name}.csv'
            try:
                # Read full file for better type inference
                df = pd.read_csv(csv_path, low_memory=False)
                df = self._clean_dataframe(df)
                
                # Count types for summary
                for col in df.columns:
                    pg_type = self._infer_pg_type(df[col], col)
                    type_counts[pg_type] = type_counts.get(pg_type, 0) + 1
                
                create_sql = self.generate_create_sql(table_name, df)
                sql_statements.append(create_sql)
                results['tables_created'] += 1
            except Exception as e:
                results['errors'].append(f"{table_name}: {e}")
                logger.error(f"  ERROR creating schema for {table_name}: {e}")
        
        results['type_summary'] = type_counts
        
        # Write SQL to single file
        sql_file = self.base_dir / 'sql' / 'reset_supabase.sql'
        with open(sql_file, 'w') as f:
            f.write(f"-- BenchSight Supabase Schema\n")
            f.write(f"-- Generated: {datetime.now()}\n")
            f.write(f"-- Tables: {len(tables)}\n")
            f.write(f"-- Type distribution: {type_counts}\n")
            f.write("-- Run this in Supabase SQL Editor to reset schema\n\n")
            f.write('\n'.join(sql_statements))
        
        logger.info(f"\nGenerated: {sql_file}")
        logger.info(f"Tables: {results['tables_created']}")
        logger.info(f"Types: {type_counts}")
        
        return results
    
    def upload_all(self, tables: List[str] = None) -> Dict[str, Any]:
        """
        Upload all tables to Supabase.
        
        Args:
            tables: List of table names (default: all)
            
        Returns:
            Dict with results
        """
        logger.info("=" * 60)
        logger.info("UPLOADING TO SUPABASE")
        logger.info("=" * 60)
        
        if tables is None:
            tables = self._get_tables()
        
        results = {
            'tables_attempted': len(tables),
            'tables_success': 0,
            'tables_failed': 0,
            'total_rows': 0,
            'errors': {}
        }
        
        logger.info(f"Uploading {len(tables)} tables...\n")
        
        # Upload dimensions first, then facts
        dim_tables = [t for t in tables if t.startswith('dim_')]
        fact_tables = [t for t in tables if t.startswith('fact_')]
        other_tables = [t for t in tables if not t.startswith('dim_') and not t.startswith('fact_')]
        
        ordered_tables = dim_tables + fact_tables + other_tables
        
        for table_name in ordered_tables:
            rows, errors = self.upload_table(table_name)
            results['total_rows'] += rows
            
            if errors:
                results['tables_failed'] += 1
                results['errors'][table_name] = errors
            else:
                results['tables_success'] += 1
        
        logger.info("\n" + "=" * 60)
        logger.info(f"UPLOAD COMPLETE")
        logger.info(f"  Success: {results['tables_success']}/{results['tables_attempted']}")
        logger.info(f"  Failed: {results['tables_failed']}")
        logger.info(f"  Total rows: {results['total_rows']:,}")
        logger.info("=" * 60)
        
        return results


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='BenchSight Supabase Manager')
    parser.add_argument('command', choices=['schema', 'upload', 'test'],
                       help='Command to run')
    parser.add_argument('--table', type=str, help='Single table name')
    parser.add_argument('--verbose', '-v', action='store_true')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        mgr = SupabaseManager()
        
        if args.command == 'schema':
            mgr.reset_schema()
        elif args.command == 'upload':
            if args.table:
                mgr.upload_table(args.table)
            else:
                mgr.upload_all()
        elif args.command == 'test':
            # Test connection
            tables = mgr._get_tables()
            print(f"Found {len(tables)} tables")
            print(f"First 10: {tables[:10]}")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
