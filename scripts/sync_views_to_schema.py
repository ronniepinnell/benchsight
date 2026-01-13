#!/usr/bin/env python3
"""
================================================================================
SYNC SQL VIEWS TO TABLE SCHEMA
================================================================================

This script ensures SQL views stay in sync with table schema changes.
Run after adding/removing columns from fact/dim tables.

What it does:
1. Scans all CSVs in data/output/ to get current column names
2. Parses existing SQL view definitions
3. Identifies views that reference tables with changed columns
4. Generates updated view SQL with correct column references

Usage:
    python scripts/sync_views_to_schema.py              # Check for drift
    python scripts/sync_views_to_schema.py --fix       # Update view files
    python scripts/sync_views_to_schema.py --table X   # Check specific table

Version: 29.0
================================================================================
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'data' / 'output'
VIEWS_DIR = PROJECT_ROOT / 'sql' / 'views'


def get_table_columns(table_name: str) -> list:
    """Get column names from a table's CSV file."""
    csv_path = OUTPUT_DIR / f'{table_name}.csv'
    if not csv_path.exists():
        return []
    
    with open(csv_path, 'r') as f:
        header = f.readline().strip()
    
    return [col.strip() for col in header.split(',')]


def get_all_table_schemas() -> dict:
    """Get schemas for all tables."""
    schemas = {}
    for csv_file in OUTPUT_DIR.glob('*.csv'):
        table_name = csv_file.stem
        schemas[table_name] = get_table_columns(table_name)
    return schemas


def parse_view_file(view_path: Path) -> list:
    """Parse a SQL view file and extract view definitions."""
    views = []
    
    with open(view_path, 'r') as f:
        content = f.read()
    
    # Find all CREATE OR REPLACE VIEW statements
    pattern = r'CREATE\s+OR\s+REPLACE\s+VIEW\s+(\w+)\s+AS\s+(.*?);'
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    
    for view_name, view_body in matches:
        # Extract table references from FROM/JOIN clauses
        table_refs = re.findall(r'FROM\s+(\w+)|JOIN\s+(\w+)', view_body, re.IGNORECASE)
        tables = [t[0] or t[1] for t in table_refs]
        
        # Extract column references
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', view_body, re.DOTALL | re.IGNORECASE)
        if select_match:
            select_clause = select_match.group(1)
            # Extract column names (handle aliases)
            columns = []
            for col in select_clause.split(','):
                col = col.strip()
                # Handle "table.column AS alias" or just "column"
                if ' AS ' in col.upper():
                    col = col.split(' AS ')[0].strip()
                if '.' in col:
                    col = col.split('.')[-1].strip()
                columns.append(col)
        else:
            columns = []
        
        views.append({
            'name': view_name,
            'tables': list(set(tables)),
            'columns': columns,
            'body': view_body,
            'file': view_path
        })
    
    return views


def check_view_column_validity(view: dict, schemas: dict) -> dict:
    """Check if view columns exist in referenced tables."""
    issues = {
        'missing_columns': [],
        'missing_tables': [],
        'valid': True
    }
    
    for table in view['tables']:
        if table not in schemas:
            issues['missing_tables'].append(table)
            issues['valid'] = False
            continue
        
        table_cols = schemas[table]
        for col in view['columns']:
            # Skip wildcards and aggregates
            if col in ('*', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN'):
                continue
            # Check if column exists in any referenced table
            found = False
            for t in view['tables']:
                if t in schemas and col in schemas[t]:
                    found = True
                    break
            if not found and col not in ['1', '2', '3']:  # Skip literals
                issues['missing_columns'].append(col)
                issues['valid'] = False
    
    return issues


def scan_all_views() -> list:
    """Scan all view files and return view definitions."""
    all_views = []
    
    if not VIEWS_DIR.exists():
        print(f"Views directory not found: {VIEWS_DIR}")
        return []
    
    for sql_file in VIEWS_DIR.glob('*.sql'):
        if sql_file.name.startswith('99_'):  # Skip deploy-all file
            continue
        views = parse_view_file(sql_file)
        all_views.extend(views)
    
    return all_views


def generate_view_report(views: list, schemas: dict) -> str:
    """Generate a report of view health."""
    report = []
    report.append("=" * 70)
    report.append("SQL VIEW SCHEMA SYNC REPORT")
    report.append(f"Generated: {datetime.now().isoformat()}")
    report.append("=" * 70)
    report.append("")
    
    issues_found = 0
    
    for view in views:
        issues = check_view_column_validity(view, schemas)
        
        if not issues['valid']:
            issues_found += 1
            report.append(f"❌ VIEW: {view['name']}")
            report.append(f"   File: {view['file'].name}")
            report.append(f"   Tables: {', '.join(view['tables'])}")
            
            if issues['missing_tables']:
                report.append(f"   Missing tables: {', '.join(issues['missing_tables'])}")
            if issues['missing_columns']:
                report.append(f"   Missing columns: {', '.join(issues['missing_columns'][:10])}")
                if len(issues['missing_columns']) > 10:
                    report.append(f"      ... and {len(issues['missing_columns']) - 10} more")
            report.append("")
    
    if issues_found == 0:
        report.append("✅ All views are in sync with table schemas!")
    else:
        report.append(f"Found {issues_found} views with potential issues")
    
    report.append("")
    report.append("=" * 70)
    
    return "\n".join(report)


def list_table_columns(table_name: str):
    """List all columns for a specific table."""
    cols = get_table_columns(table_name)
    if not cols:
        print(f"Table not found: {table_name}")
        return
    
    print(f"\n{table_name} ({len(cols)} columns):")
    print("-" * 50)
    for i, col in enumerate(cols, 1):
        print(f"  {i:3d}. {col}")


def generate_select_star_replacement(table_name: str) -> str:
    """Generate explicit column list to replace SELECT *."""
    cols = get_table_columns(table_name)
    if not cols:
        return f"-- Table {table_name} not found"
    
    # Filter out internal columns
    visible_cols = [c for c in cols if not c.startswith('_')]
    
    return ",\n    ".join(visible_cols)


def main():
    parser = argparse.ArgumentParser(description='Sync SQL views with table schemas')
    parser.add_argument('--fix', action='store_true', help='Auto-fix view files')
    parser.add_argument('--table', type=str, help='Check specific table')
    parser.add_argument('--columns', type=str, help='List columns for table')
    parser.add_argument('--select', type=str, help='Generate SELECT column list for table')
    
    args = parser.parse_args()
    
    if args.columns:
        list_table_columns(args.columns)
        return
    
    if args.select:
        print(f"\n-- SELECT columns for {args.select}:")
        print(generate_select_star_replacement(args.select))
        return
    
    print("Loading table schemas...")
    schemas = get_all_table_schemas()
    print(f"Found {len(schemas)} tables")
    
    print("Scanning SQL views...")
    views = scan_all_views()
    print(f"Found {len(views)} view definitions")
    
    if args.table:
        # Filter to views that reference this table
        views = [v for v in views if args.table in v['tables']]
        print(f"Filtered to {len(views)} views referencing {args.table}")
    
    report = generate_view_report(views, schemas)
    print(report)
    
    if args.fix:
        print("\n⚠️  Auto-fix not yet implemented. Manual review required.")
        print("Use --columns TABLE to see available columns")
        print("Use --select TABLE to generate column list")


if __name__ == '__main__':
    main()
