#!/usr/bin/env python3
"""
BenchSight Package Validation Script
Run this before creating any package!
"""

import pandas as pd
from pathlib import Path
import sys

OUTPUT_DIR = Path("data/output")

def check_tables():
    """Verify all required tables exist"""
    required = [
        'dim_player', 'dim_team', 'dim_league', 'dim_season', 'dim_schedule',
        'dim_player_role', 'dim_position', 'dim_zone', 'dim_period', 'dim_venue',
        'dim_event_type', 'dim_shift_slot', 'dim_strength', 'dim_stat_type',
        'fact_gameroster', 'fact_events', 'fact_events_long', 'fact_shifts', 
        'fact_shifts_long', 'fact_playergames',
    ]
    
    missing = []
    for t in required:
        if not (OUTPUT_DIR / f"{t}.csv").exists():
            missing.append(t)
    
    if missing:
        print(f"❌ MISSING TABLES: {missing}")
        return False
    print(f"✓ All {len(required)} required tables exist")
    return True

def check_keys():
    """Verify keys use player_id"""
    issues = []
    
    # Check fact_shifts_long
    df = pd.read_csv(OUTPUT_DIR / "fact_shifts_long.csv", dtype=str, nrows=5)
    sample_key = df['shift_player_id'].iloc[0]
    if '_P' not in sample_key:
        issues.append(f"fact_shifts_long key doesn't use player_id: {sample_key}")
    
    # Check fact_events_long
    df = pd.read_csv(OUTPUT_DIR / "fact_events_long.csv", dtype=str, nrows=5)
    sample_key = df['event_player_id'].iloc[0]
    if '_P' not in sample_key:
        issues.append(f"fact_events_long key doesn't use player_id: {sample_key}")
    
    if issues:
        for i in issues:
            print(f"❌ {i}")
        return False
    print("✓ Keys use player_id format")
    return True

def check_fks():
    """Verify FK columns exist"""
    requirements = {
        'fact_events': ['game_id', 'period_id', 'event_type_id'],
        'fact_events_long': ['event_id', 'player_id', 'period_id'],
        'fact_shifts': ['game_id', 'period_id'],
        'fact_shifts_long': ['shift_id', 'player_id', 'slot_id', 'venue_id'],
    }
    
    issues = []
    for table, fks in requirements.items():
        df = pd.read_csv(OUTPUT_DIR / f"{table}.csv", dtype=str, nrows=0)
        missing = [fk for fk in fks if fk not in df.columns]
        if missing:
            issues.append(f"{table} missing FKs: {missing}")
    
    if issues:
        for i in issues:
            print(f"❌ {i}")
        return False
    print("✓ All FK columns present")
    return True

def check_dims():
    """Verify dimension tables are complete"""
    issues = []
    
    # dim_position must have X
    df = pd.read_csv(OUTPUT_DIR / "dim_position.csv", dtype=str)
    if 'X' not in df['position_code'].values:
        issues.append("dim_position missing X (Extra Attacker)")
    
    # dim_stat_type must exist with stats
    df = pd.read_csv(OUTPUT_DIR / "dim_stat_type.csv", dtype=str)
    if len(df) < 50:
        issues.append(f"dim_stat_type only has {len(df)} stats (expected 50+)")
    
    if issues:
        for i in issues:
            print(f"❌ {i}")
        return False
    print("✓ Dimension tables complete")
    return True

def check_folders():
    """Verify required folders exist"""
    required = ['src', 'tracker', 'dashboard', 'docs', 'tests', 'data/output', 'sql']
    missing = [f for f in required if not Path(f).exists()]
    
    if missing:
        print(f"❌ MISSING FOLDERS: {missing}")
        return False
    print("✓ All required folders exist")
    return True

def main():
    print("=" * 50)
    print("BENCHSIGHT PACKAGE VALIDATION")
    print("=" * 50)
    
    checks = [
        check_folders(),
        check_tables(),
        check_keys(),
        check_fks(),
        check_dims(),
    ]
    
    print("=" * 50)
    if all(checks):
        print("✓ ALL CHECKS PASSED - Safe to package")
        return 0
    else:
        print("❌ VALIDATION FAILED - Fix issues before packaging")
        return 1

if __name__ == "__main__":
    sys.exit(main())
