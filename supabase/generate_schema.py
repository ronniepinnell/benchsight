#!/usr/bin/env python3
"""
Supabase Schema Generator
=========================
Generates PostgreSQL DDL for all BenchSight tables based on actual CSV schemas.

Usage:
    python supabase/generate_schema.py              # Generate schema.sql
    python supabase/generate_schema.py --preview    # Preview without saving
"""

import pandas as pd
from pathlib import Path
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
CONFIG_DIR = PROJECT_ROOT / "config"
SUPABASE_DIR = PROJECT_ROOT / "supabase"


def infer_postgres_type(series: pd.Series, col_name: str) -> str:
    """Infer PostgreSQL type from pandas series."""
    dtype = str(series.dtype)
    
    # Check column name patterns first
    col_lower = col_name.lower()
    
    # ID columns
    if col_lower.endswith('_id') or col_lower == 'id':
        # Check if numeric
        if dtype.startswith('int') or dtype.startswith('float'):
            if series.dropna().apply(lambda x: x == int(x) if pd.notna(x) else True).all():
                return 'BIGINT'
        return 'TEXT'
    
    # Boolean patterns
    if col_lower.startswith('is_') or col_lower.startswith('has_'):
        return 'BOOLEAN'
    
    # Percentage/rate columns
    if col_lower.endswith('_pct') or col_lower.endswith('_rate') or col_lower.endswith('_percentage'):
        return 'DECIMAL(10,4)'
    
    # Count columns
    if col_lower.endswith('_count') or col_lower.endswith('_total'):
        return 'INTEGER'
    
    # Duration/time columns
    if 'duration' in col_lower or col_lower == 'toi' or col_lower.endswith('_toi'):
        return 'INTEGER'  # Seconds
    
    # Coordinate columns
    if col_lower in ('x_coord', 'y_coord', 'x', 'y'):
        return 'DECIMAL(8,2)'
    
    # Timestamp columns
    if col_lower.endswith('_at') or col_lower in ('created_at', 'updated_at', 'timestamp'):
        return 'TIMESTAMPTZ'
    
    # Now check dtype
    if dtype == 'bool':
        return 'BOOLEAN'
    elif dtype.startswith('int'):
        max_val = series.max() if len(series.dropna()) > 0 else 0
        if max_val > 2147483647:
            return 'BIGINT'
        return 'INTEGER'
    elif dtype.startswith('float'):
        # Check if actually integer
        if series.dropna().apply(lambda x: x == int(x) if pd.notna(x) else True).all():
            return 'INTEGER'
        return 'DECIMAL(12,4)'
    elif dtype == 'object':
        # Check string lengths
        if len(series.dropna()) > 0:
            max_len = series.dropna().astype(str).str.len().max()
            if max_len <= 50:
                return 'VARCHAR(100)'
            elif max_len <= 255:
                return 'VARCHAR(500)'
            else:
                return 'TEXT'
        return 'TEXT'
    else:
        return 'TEXT'


def generate_table_ddl(table_name: str, df: pd.DataFrame) -> str:
    """Generate CREATE TABLE statement for a table."""
    columns = []
    
    for col in df.columns:
        pg_type = infer_postgres_type(df[col], col)
        columns.append(f'    "{col}" {pg_type}')
    
    # Add primary key hint based on table type
    pk_col = None
    if f'{table_name.replace("dim_", "").replace("fact_", "")}_id' in df.columns:
        pk_col = f'{table_name.replace("dim_", "").replace("fact_", "")}_id'
    elif 'id' in df.columns:
        pk_col = 'id'
    elif table_name.startswith('dim_') and len(df.columns) > 0:
        # First column is usually the ID for dims
        first_col = df.columns[0]
        if first_col.endswith('_id'):
            pk_col = first_col
    
    ddl = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n'
    ddl += ',\n'.join(columns)
    ddl += '\n);\n'
    
    # Add index on common lookup columns
    indexes = []
    if 'game_id' in df.columns:
        indexes.append(f'CREATE INDEX IF NOT EXISTS idx_{table_name}_game_id ON "{table_name}" ("game_id");')
    if 'player_id' in df.columns:
        indexes.append(f'CREATE INDEX IF NOT EXISTS idx_{table_name}_player_id ON "{table_name}" ("player_id");')
    if 'team_id' in df.columns:
        indexes.append(f'CREATE INDEX IF NOT EXISTS idx_{table_name}_team_id ON "{table_name}" ("team_id");')
    if 'event_type' in df.columns:
        indexes.append(f'CREATE INDEX IF NOT EXISTS idx_{table_name}_event_type ON "{table_name}" ("event_type");')
    
    if indexes:
        ddl += '\n' + '\n'.join(indexes) + '\n'
    
    return ddl


def generate_full_schema():
    """Generate complete schema for all tables."""
    csv_files = sorted(OUTPUT_DIR.glob("*.csv"))
    
    # Load metadata for comments
    metadata_file = CONFIG_DIR / "TABLE_METADATA.json"
    metadata = {}
    if metadata_file.exists():
        with open(metadata_file) as f:
            metadata = json.load(f)
    
    schema = f"""-- BenchSight Supabase Schema
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
-- Tables: {len(csv_files)}
--
-- To apply:
--   1. Go to Supabase SQL Editor
--   2. Paste this entire file
--   3. Run

-- ============================================================
-- DROP EXISTING TABLES (for clean rebuild)
-- ============================================================
-- Uncomment the following line to drop all tables first:
-- DROP SCHEMA public CASCADE; CREATE SCHEMA public;

"""
    
    # Group tables
    dims = [f for f in csv_files if f.stem.startswith('dim_')]
    facts = [f for f in csv_files if f.stem.startswith('fact_')]
    qas = [f for f in csv_files if f.stem.startswith('qa_')]
    
    # Generate dimension tables first (for foreign key references)
    schema += "\n-- ============================================================\n"
    schema += f"-- DIMENSION TABLES ({len(dims)})\n"
    schema += "-- ============================================================\n\n"
    
    for csv_path in dims:
        table_name = csv_path.stem
        df = pd.read_csv(csv_path)
        
        # Add comment with description
        table_info = metadata.get('tables', {}).get(table_name, {})
        if table_info.get('description'):
            schema += f"-- {table_info['description']}\n"
        
        schema += generate_table_ddl(table_name, df)
        schema += "\n"
    
    # Generate fact tables
    schema += "\n-- ============================================================\n"
    schema += f"-- FACT TABLES ({len(facts)})\n"
    schema += "-- ============================================================\n\n"
    
    for csv_path in facts:
        table_name = csv_path.stem
        df = pd.read_csv(csv_path)
        
        table_info = metadata.get('tables', {}).get(table_name, {})
        if table_info.get('description'):
            schema += f"-- {table_info['description']}\n"
        
        schema += generate_table_ddl(table_name, df)
        schema += "\n"
    
    # Generate QA tables
    schema += "\n-- ============================================================\n"
    schema += f"-- QA TABLES ({len(qas)})\n"
    schema += "-- ============================================================\n\n"
    
    for csv_path in qas:
        table_name = csv_path.stem
        df = pd.read_csv(csv_path)
        
        table_info = metadata.get('tables', {}).get(table_name, {})
        if table_info.get('description'):
            schema += f"-- {table_info['description']}\n"
        
        schema += generate_table_ddl(table_name, df)
        schema += "\n"
    
    # Add useful views
    schema += """
-- ============================================================
-- USEFUL VIEWS
-- ============================================================

-- Goals with scorer and assists
CREATE OR REPLACE VIEW v_goals AS
SELECT 
    e.game_id,
    e.period,
    e.event_index,
    e.event_id,
    e.player_name as scorer,
    e.event_detail,
    e.event_team_zone as zone
FROM fact_events e
WHERE e.event_type = 'Goal' 
  AND e.event_detail = 'Goal_Scored';

-- Player game stats summary
CREATE OR REPLACE VIEW v_player_game_summary AS
SELECT 
    ep.game_id,
    ep.player_id,
    ep.player_name,
    COUNT(*) FILTER (WHERE ep.event_type = 'Goal' AND ep.player_role = 'event_player_1') as goals,
    COUNT(*) FILTER (WHERE ep.event_type = 'Goal' AND ep.player_role = 'event_player_2') as primary_assists,
    COUNT(*) FILTER (WHERE ep.event_type = 'Goal' AND ep.player_role = 'event_player_3') as secondary_assists,
    COUNT(*) FILTER (WHERE ep.event_type = 'Shot' AND ep.player_role = 'event_player_1') as shots
FROM fact_event_players ep
GROUP BY ep.game_id, ep.player_id, ep.player_name;

-- Game summary
CREATE OR REPLACE VIEW v_game_summary AS
SELECT 
    e.game_id,
    e.home_team,
    e.away_team,
    COUNT(*) FILTER (WHERE e.event_type = 'Goal' AND e.event_detail = 'Goal_Scored') as total_goals,
    COUNT(*) FILTER (WHERE e.event_type = 'Shot') as total_shots,
    COUNT(DISTINCT e.period) as periods_played
FROM fact_events e
GROUP BY e.game_id, e.home_team, e.away_team;
"""
    
    return schema, len(csv_files)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate Supabase Schema')
    parser.add_argument('--preview', action='store_true', help='Preview without saving')
    args = parser.parse_args()
    
    print("Generating Supabase schema...")
    schema, table_count = generate_full_schema()
    
    if args.preview:
        print(schema[:3000])
        print(f"\n... ({len(schema)} chars total)")
    else:
        output_path = SUPABASE_DIR / "schema.sql"
        with open(output_path, 'w') as f:
            f.write(schema)
        print(f"✓ Generated {output_path}")
        print(f"  Tables: {table_count}")
        print(f"  Size: {len(schema):,} chars")


if __name__ == '__main__':
    main()
