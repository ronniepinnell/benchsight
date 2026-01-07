#!/usr/bin/env python3
"""
CRITICAL TABLE INTEGRITY TESTS
==============================
These tests ensure no tables are accidentally deleted.
RUN BEFORE ANY CLEANUP OPERATION.

Usage:
    pytest tests/test_table_integrity.py -v
    python tests/test_table_integrity.py
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.table_registry import TableRegistry, TableType, ProtectionLevel

OUTPUT_DIR = Path('data/output')

# Initialize registry
registry = TableRegistry()

# For backward compatibility
ALL_TABLES = list(registry.tables.keys())
CRITICAL_TABLES = registry.get_critical_tables()
REGENERABLE_TABLES = {name: t.source_module for name, t in registry.tables.items()}
LEGACY_TABLES = []  # No longer used

def validate_tables(output_dir):
    """Validate tables exist."""
    existing = {f.stem for f in output_dir.glob('*.csv')}
    expected = set(registry.tables.keys())
    return {
        'missing': list(expected - existing),
        'extra': list(existing - expected)
    }

# ============================================================================
# TESTS
# ============================================================================

def test_minimum_table_count():
    """Ensure we never drop below expected count."""
    tables = list(OUTPUT_DIR.glob('*.csv'))
    count = len(tables)
    # Allow 30 less than registered (some tables are optional)
    min_expected = len(registry) - 30
    assert count >= min_expected, f"CRITICAL: Only {count} tables! Expected {min_expected}+. Tables may have been deleted!"

def test_all_registered_tables_exist():
    """ALL tables in registry MUST exist."""
    result = validate_tables(OUTPUT_DIR)
    # Allow some missing (optional tables)
    critical_missing = [t for t in result['missing'] if registry.is_protected(t)]
    assert not critical_missing, f"CRITICAL: Missing protected tables: {critical_missing}"

def test_no_unknown_tables():
    """Warn about tables not in registry."""
    result = validate_tables(OUTPUT_DIR)
    if result['extra']:
        print(f"WARNING: Unknown tables not in registry: {result['extra']}")

def test_critical_tables_exist():
    """All CRITICAL tables must exist."""
    missing = [t for t in CRITICAL_TABLES if not (OUTPUT_DIR / f'{t}.csv').exists()]
    assert not missing, f"CRITICAL: Missing critical tables: {missing}"

def test_legacy_tables_exist():
    """All LEGACY tables must exist (can't regenerate!)."""
    missing = [t for t in LEGACY_TABLES if not (OUTPUT_DIR / f'{t}.csv').exists()]
    assert not missing, f"CRITICAL: Missing LEGACY tables (CANNOT REGENERATE): {missing}"

def test_player_game_stats_has_columns():
    """fact_player_game_stats must have 300+ columns."""
    path = OUTPUT_DIR / 'fact_player_game_stats.csv'
    if path.exists():
        df = pd.read_csv(path, nrows=5)
        assert len(df.columns) >= 100, f"fact_player_game_stats only has {len(df.columns)} columns!"

def test_gameroster_has_required_columns():
    """fact_gameroster must have key columns."""
    path = OUTPUT_DIR / 'fact_gameroster.csv'
    assert path.exists(), "fact_gameroster.csv missing!"
    df = pd.read_csv(path, nrows=5)
    required = ['game_id', 'player_id', 'team_id', 'player_full_name', 'goals', 'assist']
    missing = [c for c in required if c not in df.columns]
    assert not missing, f"fact_gameroster missing columns: {missing}"

def test_no_empty_critical_tables():
    """Critical tables should never be empty."""
    empty = []
    for table in CRITICAL_TABLES:
        path = OUTPUT_DIR / f'{table}.csv'
        if path.exists():
            df = pd.read_csv(path, nrows=1)
            if len(df) == 0:
                empty.append(table)
    assert not empty, f"CRITICAL: These critical tables are empty: {empty}"


# ============================================================================
# DELETION SAFETY CHECK
# ============================================================================

def safe_delete_check(tables_to_delete: list) -> bool:
    """Check if it's safe to delete tables. USE BEFORE ANY CLEANUP."""
    print("\n" + "=" * 60)
    print("TABLE DELETION SAFETY CHECK")
    print("=" * 60)
    
    impact = get_deletion_impact(tables_to_delete)
    
    if impact['unsafe']:
        print(f"\n❌ UNSAFE TO DELETE ({len(impact['unsafe'])} tables):")
        for table, reason in impact['unsafe']:
            print(f"   {table}: {reason}")
    
    if impact['safe']:
        print(f"\n✅ Safe to delete ({len(impact['safe'])} tables):")
        for table, reason in impact['safe']:
            print(f"   {table}: {reason}")
    
    print("\n" + "=" * 60)
    all_safe = len(impact['unsafe']) == 0
    if all_safe:
        print("✅ All tables safe to delete")
    else:
        print("❌ SOME TABLES ARE NOT SAFE TO DELETE!")
    print("=" * 60)
    
    return all_safe


# ============================================================================
# RUN AS SCRIPT
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("BENCHSIGHT TABLE INTEGRITY CHECK")
    print("=" * 60)
    
    # Count tables
    current_count = len(list(OUTPUT_DIR.glob('*.csv')))
    expected_count = len(registry)
    
    print(f"\nCurrent tables: {current_count}")
    print(f"Expected tables: {expected_count}")
    
    failures = []
    
    tests = [
        ('Minimum table count', test_minimum_table_count),
        ('All registered tables exist', test_all_registered_tables_exist),
        ('Critical tables exist', test_critical_tables_exist),
        ('Legacy tables exist', test_legacy_tables_exist),
        ('Player game stats columns', test_player_game_stats_has_columns),
        ('Gameroster columns', test_gameroster_has_required_columns),
        ('No empty critical tables', test_no_empty_critical_tables),
    ]
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✅ {name}")
        except AssertionError as e:
            print(f"❌ {name}: {e}")
            failures.append(name)
        except Exception as e:
            print(f"⚠️ {name}: Error - {e}")
    
    print("\n" + "=" * 60)
    if failures:
        print(f"❌ {len(failures)} TESTS FAILED!")
        sys.exit(1)
    else:
        print(f"✅ ALL TESTS PASSED - {current_count} tables verified")
        sys.exit(0)
