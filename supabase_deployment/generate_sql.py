#!/usr/bin/env python3
"""
Generate CREATE TABLE SQL statements from CSV files.
Analyzes actual data to infer appropriate data types.
"""

import csv
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration
DATA_DIR = Path("/home/claude/benchsight_project/data/output")
OUTPUT_DIR = Path("/home/claude/benchsight_project/supabase_deployment/sql")

# Primary key definitions for each table
PRIMARY_KEYS = {
    "dim_player": "player_id",
    "dim_team": "team_id",
    "dim_schedule": "game_id",
    "fact_events": "event_key",
    "fact_events_player": "event_player_key",
    "fact_shifts": "shift_key",
    "fact_shifts_player": "shift_player_key",
    "fact_player_game_stats": "player_game_key",
    "fact_team_game_stats": "team_game_key",
    "fact_goalie_game_stats": "goalie_game_key",
    "fact_h2h": "h2h_key",
    "fact_wowy": "wowy_key",
}

# Foreign key definitions: column -> (referenced_table, referenced_column)
FOREIGN_KEYS = {
    "fact_events": {
        "game_id": ("dim_schedule", "game_id"),
        "shift_key": ("fact_shifts", "shift_key"),
    },
    "fact_events_player": {
        "event_key": ("fact_events", "event_key"),
        "game_id": ("dim_schedule", "game_id"),
        "player_id": ("dim_player", "player_id"),
    },
    "fact_shifts": {
        "game_id": ("dim_schedule", "game_id"),
    },
    "fact_shifts_player": {
        "shift_key": ("fact_shifts", "shift_key"),
        "game_id": ("dim_schedule", "game_id"),
        "player_id": ("dim_player", "player_id"),
    },
    "fact_player_game_stats": {
        "game_id": ("dim_schedule", "game_id"),
        "player_id": ("dim_player", "player_id"),
    },
    "fact_team_game_stats": {
        "game_id": ("dim_schedule", "game_id"),
        "team_id": ("dim_team", "team_id"),
    },
    "fact_goalie_game_stats": {
        "game_id": ("dim_schedule", "game_id"),
        "player_id": ("dim_player", "player_id"),
    },
    "fact_h2h": {
        "game_id": ("dim_schedule", "game_id"),
        "player_1_id": ("dim_player", "player_id"),
        "player_2_id": ("dim_player", "player_id"),
    },
    "fact_wowy": {
        "game_id": ("dim_schedule", "game_id"),
        "player_1_id": ("dim_player", "player_id"),
        "player_2_id": ("dim_player", "player_id"),
    },
}


def infer_data_type(column_name: str, values: List[str]) -> str:
    """Infer PostgreSQL data type from column name and sample values."""
    
    # Filter out empty/null values
    non_empty = [v for v in values if v and v.strip() and v.lower() != 'nan']
    
    if not non_empty:
        return "TEXT"
    
    # Column name patterns
    col_lower = column_name.lower()
    
    # Primary/Foreign keys
    if col_lower.endswith('_key'):
        return "VARCHAR(50)"
    if col_lower.endswith('_id') and col_lower not in ['game_id', 'season_id', 'period_id', 'venue_id', 'event_type_id', 'event_detail_id', 'event_detail_2_id', 'success_id', 'play_detail_success_id', 'zone_id', 'play_detail_id', 'play_detail_2_id', 'role_id', 'strength_id', 'situation_id', 'slot_id', 'shift_start_type_id', 'shift_stop_type_id']:
        return "VARCHAR(20)"
    
    # ID fields that should be integers
    if col_lower in ['game_id', 'season_id', 'period_id', 'venue_id', 'event_type_id', 'event_detail_id', 'event_detail_2_id', 'success_id', 'play_detail_success_id', 'zone_id', 'play_detail_id', 'play_detail_2_id', 'role_id', 'strength_id', 'situation_id', 'slot_id', 'shift_start_type_id', 'shift_stop_type_id']:
        return "INTEGER"
    
    # Percentage columns
    if col_lower.endswith('_pct') or col_lower.endswith('_rate') or 'pct' in col_lower:
        return "DECIMAL(10,4)"
    
    # Time/duration columns
    if 'seconds' in col_lower or 'duration' in col_lower:
        return "INTEGER"
    if col_lower.endswith('_min') or col_lower.endswith('_sec'):
        return "INTEGER"
    
    # Count columns (various stats)
    count_patterns = ['goals', 'assists', 'points', 'shots', 'saves', 'hits', 'blocks', 
                     'wins', 'losses', 'entries', 'exits', 'giveaways', 'takeaways',
                     'shift_count', 'logical_shifts', 'total_', '_count', 'attempts']
    if any(p in col_lower for p in count_patterns):
        # Check if values are actually integers
        try:
            for v in non_empty[:50]:
                float_val = float(v)
                if float_val != int(float_val) and float_val not in [float('inf'), float('-inf')]:
                    return "DECIMAL(12,4)"
            return "INTEGER"
        except (ValueError, OverflowError):
            pass
    
    # Index columns
    if 'index' in col_lower:
        return "INTEGER"
    
    # Boolean patterns
    if col_lower.startswith('is_') or col_lower.endswith('_en') or col_lower.startswith('empty_net'):
        return "BOOLEAN"
    
    # Date columns
    if 'date' in col_lower:
        return "DATE"
    
    # URL columns
    if 'url' in col_lower:
        return "TEXT"
    
    # Name columns
    if 'name' in col_lower:
        return "VARCHAR(200)"
    
    # Try to infer from actual values
    try:
        # Check if all are integers
        all_int = True
        all_float = True
        max_len = 0
        
        for v in non_empty[:100]:
            max_len = max(max_len, len(v))
            try:
                int_val = int(float(v))
                if str(int_val) != v.split('.')[0].lstrip('-'):
                    all_int = False
            except (ValueError, OverflowError):
                all_int = False
                all_float = False
            
            try:
                float(v)
            except (ValueError, OverflowError):
                all_float = False
        
        if all_int:
            return "INTEGER"
        if all_float:
            return "DECIMAL(15,6)"
        
        # String - choose appropriate size
        if max_len <= 10:
            return "VARCHAR(20)"
        elif max_len <= 50:
            return "VARCHAR(100)"
        elif max_len <= 200:
            return "VARCHAR(500)"
        else:
            return "TEXT"
            
    except Exception:
        return "TEXT"


def read_csv_sample(filepath: Path, sample_size: int = 100) -> Tuple[List[str], List[List[str]]]:
    """Read CSV headers and sample rows."""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = []
        for i, row in enumerate(reader):
            if i >= sample_size:
                break
            rows.append(row)
    return headers, rows


def generate_create_table(table_name: str, filepath: Path) -> str:
    """Generate CREATE TABLE statement for a table."""
    headers, rows = read_csv_sample(filepath, sample_size=200)
    
    # Transpose rows to get column values
    column_values: Dict[str, List[str]] = {h: [] for h in headers}
    for row in rows:
        for i, val in enumerate(row):
            if i < len(headers):
                column_values[headers[i]].append(val)
    
    # Generate column definitions
    columns = []
    pk = PRIMARY_KEYS.get(table_name)
    
    for header in headers:
        dtype = infer_data_type(header, column_values[header])
        
        col_def = f"    {header} {dtype}"
        
        if header == pk:
            col_def += " PRIMARY KEY"
        
        columns.append(col_def)
    
    sql = f"-- {table_name}: {len(headers)} columns\n"
    sql += f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    sql += ",\n".join(columns)
    sql += "\n);\n"
    
    return sql


def generate_foreign_keys_sql(table_name: str) -> str:
    """Generate ALTER TABLE statements for foreign keys."""
    if table_name not in FOREIGN_KEYS:
        return ""
    
    sqls = []
    for col, (ref_table, ref_col) in FOREIGN_KEYS[table_name].items():
        fk_name = f"fk_{table_name}_{col}"
        sql = f"""ALTER TABLE {table_name} 
    ADD CONSTRAINT {fk_name} 
    FOREIGN KEY ({col}) REFERENCES {ref_table}({ref_col})
    ON DELETE SET NULL;"""
        sqls.append(sql)
    
    return "\n\n".join(sqls)


def generate_indexes_sql(table_name: str, headers: List[str]) -> str:
    """Generate CREATE INDEX statements."""
    indexes = []
    
    # Index on game_id for all tables that have it
    if 'game_id' in headers:
        indexes.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_game_id ON {table_name}(game_id);")
    
    # Index on player_id for relevant tables
    if 'player_id' in headers:
        indexes.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_player_id ON {table_name}(player_id);")
    
    # Index on team_id for relevant tables
    if 'team_id' in headers:
        indexes.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_team_id ON {table_name}(team_id);")
    
    # Index on event_key for event tables
    if 'event_key' in headers and table_name != 'fact_events':
        indexes.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_event_key ON {table_name}(event_key);")
    
    # Index on shift_key for shift tables
    if 'shift_key' in headers and table_name != 'fact_shifts':
        indexes.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_shift_key ON {table_name}(shift_key);")
    
    # Index on event_type for events
    if 'event_type' in headers:
        indexes.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_event_type ON {table_name}(event_type);")
    
    # Index on period
    if 'period' in headers:
        indexes.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_period ON {table_name}(period);")
    
    return "\n".join(indexes)


def main():
    """Main function to generate all SQL files."""
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Tables in load order
    tables = [
        # Dimensions (no dependencies)
        ("dim_player", "dim_player.csv"),
        ("dim_team", "dim_team.csv"),
        ("dim_schedule", "dim_schedule.csv"),
        # Facts (with dependencies)
        ("fact_shifts", "fact_shifts.csv"),
        ("fact_events", "fact_events.csv"),
        ("fact_events_player", "fact_events_player.csv"),
        ("fact_shifts_player", "fact_shifts_player.csv"),
        ("fact_player_game_stats", "fact_player_game_stats.csv"),
        ("fact_team_game_stats", "fact_team_game_stats.csv"),
        ("fact_goalie_game_stats", "fact_goalie_game_stats.csv"),
        ("fact_h2h", "fact_h2h.csv"),
        ("fact_wowy", "fact_wowy.csv"),
    ]
    
    # Generate drop tables
    drop_sql = "-- Drop all tables in reverse dependency order\n"
    for table_name, _ in reversed(tables):
        drop_sql += f"DROP TABLE IF EXISTS {table_name} CASCADE;\n"
    
    with open(OUTPUT_DIR / "00_drop_all_tables.sql", 'w') as f:
        f.write(drop_sql)
    print("Generated: 00_drop_all_tables.sql")
    
    # Generate dimension tables
    dim_sql = "-- Dimension Tables\n-- No foreign key dependencies\n\n"
    for table_name, csv_file in tables[:3]:
        filepath = DATA_DIR / csv_file
        if filepath.exists():
            dim_sql += generate_create_table(table_name, filepath)
            dim_sql += "\n"
    
    with open(OUTPUT_DIR / "01_create_dim_tables.sql", 'w') as f:
        f.write(dim_sql)
    print("Generated: 01_create_dim_tables.sql")
    
    # Generate fact tables
    fact_sql = "-- Fact Tables\n-- Load after dimension tables\n\n"
    for table_name, csv_file in tables[3:]:
        filepath = DATA_DIR / csv_file
        if filepath.exists():
            fact_sql += generate_create_table(table_name, filepath)
            fact_sql += "\n"
    
    with open(OUTPUT_DIR / "02_create_fact_tables.sql", 'w') as f:
        f.write(fact_sql)
    print("Generated: 02_create_fact_tables.sql")
    
    # Generate indexes
    index_sql = "-- Indexes for query performance\n\n"
    for table_name, csv_file in tables:
        filepath = DATA_DIR / csv_file
        if filepath.exists():
            headers, _ = read_csv_sample(filepath, sample_size=1)
            idx = generate_indexes_sql(table_name, headers)
            if idx:
                index_sql += f"-- {table_name}\n{idx}\n\n"
    
    with open(OUTPUT_DIR / "03_create_indexes.sql", 'w') as f:
        f.write(index_sql)
    print("Generated: 03_create_indexes.sql")
    
    # Generate foreign keys
    fk_sql = "-- Foreign Key Constraints\n-- Run AFTER data is loaded\n\n"
    for table_name, _ in tables:
        fk = generate_foreign_keys_sql(table_name)
        if fk:
            fk_sql += f"-- {table_name}\n{fk}\n\n"
    
    with open(OUTPUT_DIR / "04_add_foreign_keys.sql", 'w') as f:
        f.write(fk_sql)
    print("Generated: 04_add_foreign_keys.sql")
    
    # Copy existing validation SQL
    print("\nAll SQL files generated successfully!")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for table_name, csv_file in tables:
        filepath = DATA_DIR / csv_file
        if filepath.exists():
            headers, rows = read_csv_sample(filepath, sample_size=1)
            with open(filepath) as f:
                row_count = sum(1 for _ in f) - 1
            print(f"{table_name}: {len(headers)} columns, {row_count} rows")


if __name__ == "__main__":
    main()
