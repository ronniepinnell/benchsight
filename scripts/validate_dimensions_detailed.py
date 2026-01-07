#!/usr/bin/env python3
"""
Comprehensive Dimension Table Validation - Column by Column Analysis

Validates each dimension table:
1. Key format consistency
2. Column completeness (nulls)
3. Data quality checks
4. FK relationship opportunities
5. Expected values that can cascade to fact tables

Version: 6.5.21
Date: January 6, 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

OUTPUT_DIR = Path('data/output')

# Expected key prefixes for each dimension
EXPECTED_KEY_PREFIXES = {
    'dim_assist_type': 'AT',
    'dim_comparison_type': 'CMP',
    'dim_competition_tier': 'CT',
    'dim_composite_rating': 'CR',
    'dim_danger_level': 'DL',
    'dim_danger_zone': 'DZ',
    'dim_event_detail': 'ED',
    'dim_event_detail_2': 'E2',
    'dim_event_type': 'ET',
    'dim_game_state': 'GS',
    'dim_giveaway_type': 'GT',
    'dim_league': None,  # Single char IDs ok
    'dim_micro_stat': 'MS',
    'dim_net_location': 'NL',
    'dim_pass_type': 'PT',
    'dim_period': 'P',
    'dim_play_detail': 'PD',
    'dim_play_detail_2': 'PD2',
    'dim_player': 'P',
    'dim_player_role': 'PR',
    'dim_position': 'PO',
    'dim_rating': 'R',
    'dim_rating_matchup': 'RM',
    'dim_rink_zone': 'RC',
    'dim_schedule': None,  # Game IDs are numeric
    'dim_season': 'N',
    'dim_shift_quality_tier': 'SQ',
    'dim_shift_slot': 'SL',
    'dim_shift_start_type': 'SST',
    'dim_shift_stop_type': 'SPT',
    'dim_shot_type': 'ST',
    'dim_situation': 'SIT',
    'dim_stat': 'MS',
    'dim_stat_category': 'SC',
    'dim_stat_type': 'MS',
    'dim_stoppage_type': 'SP',
    'dim_strength': 'STR',
    'dim_success': 'SC',
    'dim_takeaway_type': 'TA',
    'dim_team': 'N',  # Team IDs should start with N
    'dim_time_bucket': 'TB',
    'dim_turnover_quality': 'TQ',
    'dim_turnover_type': 'TO',
    'dim_venue': 'VN',
    'dim_zone': 'ZN',
    'dim_zone_entry_type': 'ZE',
    'dim_zone_exit_type': 'ZX',
}

# Tables that are lookup/mapping tables (not true dimensions)
LOOKUP_TABLES = ['dim_playerurlref', 'dim_randomnames', 'dim_terminology_mapping']

# Columns that contain expected values we could cascade to facts
CASCADE_COLUMNS = {
    'dim_pass_type': ['expected_completion_rate', 'danger_value', 'xa_modifier', 'skill_required'],
    'dim_shot_type': ['xg_modifier', 'accuracy_rating', 'power_rating', 'deception_rating', 'typical_distance'],
    'dim_giveaway_type': ['danger_level', 'xga_impact', 'turnover_quality', 'zone_context'],
    'dim_takeaway_type': ['skill_level', 'xgf_impact', 'value_weight', 'transition_potential'],
    'dim_turnover_type': ['category', 'quality', 'weight', 'zone_context', 'zone_danger_multiplier'],
    'dim_zone_entry_type': ['success_likelihood', 'danger_modifier'] if False else [],  # Check if exists
    'dim_zone_exit_type': ['success_likelihood', 'quality_modifier'] if False else [],  # Check if exists
    'dim_danger_zone': ['xg_base'],
    'dim_danger_level': ['xg_multiplier'],
    'dim_strength': ['advantage_type', 'expected_gf_rate', 'expected_ga_rate'] if False else [],
}


def validate_dimension_table(table_name):
    """Validate a single dimension table column by column."""
    path = OUTPUT_DIR / f'{table_name}.csv'
    if not path.exists():
        return None
    
    df = pd.read_csv(path)
    
    result = {
        'table_name': table_name,
        'rows': len(df),
        'columns': len(df.columns),
        'column_details': [],
        'issues': [],
        'recommendations': [],
        'cascade_opportunities': []
    }
    
    # Check if it's a lookup table
    if table_name in LOOKUP_TABLES:
        result['table_type'] = 'lookup'
    else:
        result['table_type'] = 'dimension'
    
    # Analyze each column
    for col in df.columns:
        col_info = {
            'name': col,
            'dtype': str(df[col].dtype),
            'null_count': int(df[col].isna().sum()),
            'null_pct': round(df[col].isna().sum() / len(df) * 100, 1) if len(df) > 0 else 0,
            'unique_count': int(df[col].nunique()),
            'sample_values': df[col].dropna().head(3).tolist()
        }
        result['column_details'].append(col_info)
        
        # Check for high null percentage
        if col_info['null_pct'] > 50:
            result['issues'].append(f"Column '{col}' has {col_info['null_pct']}% null values")
    
    # Check primary key (first column)
    id_col = df.columns[0]
    
    # Check for duplicates
    dup_count = df[id_col].duplicated().sum()
    if dup_count > 0:
        result['issues'].append(f"Primary key '{id_col}' has {dup_count} duplicates")
    
    # Check for nulls in PK
    null_pk = df[id_col].isna().sum()
    if null_pk > 0:
        result['issues'].append(f"Primary key '{id_col}' has {null_pk} null values")
    
    # Check key format
    expected_prefix = EXPECTED_KEY_PREFIXES.get(table_name)
    if expected_prefix and len(df) > 0:
        sample_id = str(df[id_col].iloc[0])
        if not sample_id.startswith(expected_prefix):
            result['issues'].append(f"Key format issue: expected prefix '{expected_prefix}', got '{sample_id[:5]}'")
    
    # Check for cascade opportunities
    if table_name in CASCADE_COLUMNS:
        for col in CASCADE_COLUMNS[table_name]:
            if col in df.columns:
                non_null = df[col].notna().sum()
                result['cascade_opportunities'].append({
                    'column': col,
                    'populated': non_null,
                    'total': len(df),
                    'can_cascade': non_null == len(df)
                })
    
    return result


def check_fk_relationships():
    """Check which FK relationships exist and which could be added."""
    print("\n" + "=" * 70)
    print("FK RELATIONSHIP ANALYSIS")
    print("=" * 70)
    
    # Load fact_events to check current FKs
    events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv')
    events_cols = set(events.columns)
    
    # Potential FK additions based on dimension tables
    potential_fks = {
        'danger_level_id': ('dim_danger_level', 'danger_level_id'),
        'danger_zone_id': ('dim_danger_zone', 'danger_zone_id'),
        'net_location_id': ('dim_net_location', 'net_location_id'),
        'game_state_id': ('dim_game_state', 'game_state_id'),
        'competition_tier_id': ('dim_competition_tier', 'competition_tier_id'),
        'assist_type_id': ('dim_assist_type', 'assist_type_id'),
        'turnover_quality_id': ('dim_turnover_quality', 'turnover_quality_id'),
    }
    
    print("\nCurrent FK columns in fact_events:")
    current_fks = [c for c in events_cols if c.endswith('_id') and c != 'event_id']
    for fk in sorted(current_fks):
        print(f"  ✓ {fk}")
    
    print("\nPotential FK additions:")
    for fk, (dim_table, dim_col) in potential_fks.items():
        if fk in events_cols:
            print(f"  ✓ {fk} (already exists)")
        else:
            print(f"  ○ {fk} → {dim_table}")
    
    return potential_fks


def check_cascade_values():
    """Check which dimension values can cascade to fact tables."""
    print("\n" + "=" * 70)
    print("CASCADE VALUE ANALYSIS")
    print("=" * 70)
    
    # Load fact_events
    events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv')
    
    # Check what's already cascaded
    cascaded = []
    not_cascaded = []
    
    cascade_checks = [
        ('pass_type_id', 'expected_completion_pct', 'dim_pass_type', 'expected_completion_rate'),
        ('pass_type_id', 'xa_modifier', 'dim_pass_type', 'xa_modifier'),
        ('pass_type_id', 'pass_danger_value', 'dim_pass_type', 'danger_value'),
        ('shot_type_id', 'xg_modifier', 'dim_shot_type', 'xg_modifier'),
        ('shot_type_id', 'shot_accuracy_rating', 'dim_shot_type', 'accuracy_rating'),
        ('giveaway_type_id', 'giveaway_xga_impact', 'dim_giveaway_type', 'xga_impact'),
        ('giveaway_type_id', 'giveaway_danger_level', 'dim_giveaway_type', 'danger_level'),
        ('takeaway_type_id', 'takeaway_xgf_impact', 'dim_takeaway_type', 'xgf_impact'),
        ('takeaway_type_id', 'takeaway_value_weight', 'dim_takeaway_type', 'value_weight'),
        ('turnover_type_id', 'turnover_weight', 'dim_turnover_type', 'weight'),
        ('turnover_type_id', 'turnover_zone_multiplier', 'dim_turnover_type', 'zone_danger_multiplier'),
    ]
    
    print("\nCascaded values in fact_events:")
    for fk_col, fact_col, dim_table, dim_col in cascade_checks:
        if fact_col in events.columns:
            populated = events[fact_col].notna().sum()
            print(f"  ✓ {fact_col}: {populated}/{len(events)} populated (from {dim_table}.{dim_col})")
            cascaded.append((fact_col, dim_table, dim_col))
        else:
            not_cascaded.append((fk_col, fact_col, dim_table, dim_col))
    
    print("\nNot yet cascaded (opportunities):")
    for fk_col, fact_col, dim_table, dim_col in not_cascaded:
        if fk_col in events.columns:
            print(f"  ○ {fact_col} ← {dim_table}.{dim_col} (via {fk_col})")
    
    return cascaded, not_cascaded


def main():
    print("=" * 70)
    print("COMPREHENSIVE DIMENSION TABLE VALIDATION")
    print("=" * 70)
    
    dim_files = sorted(OUTPUT_DIR.glob('dim_*.csv'))
    
    all_results = []
    issues_count = 0
    
    for f in dim_files:
        table_name = f.stem
        result = validate_dimension_table(table_name)
        if result:
            all_results.append(result)
            
            # Print summary
            status = "✓" if not result['issues'] else "⚠"
            print(f"\n{status} {table_name}")
            print(f"  Type: {result['table_type']}")
            print(f"  Rows: {result['rows']}, Columns: {result['columns']}")
            
            # Column details
            print(f"  Columns:")
            for col in result['column_details']:
                null_indicator = f" ({col['null_pct']}% null)" if col['null_pct'] > 0 else ""
                print(f"    - {col['name']}: {col['dtype']}, {col['unique_count']} unique{null_indicator}")
            
            # Issues
            if result['issues']:
                issues_count += len(result['issues'])
                print(f"  Issues:")
                for issue in result['issues']:
                    print(f"    ⚠ {issue}")
            
            # Cascade opportunities
            if result['cascade_opportunities']:
                print(f"  Cascade opportunities:")
                for opp in result['cascade_opportunities']:
                    status = "✓" if opp['can_cascade'] else "○"
                    print(f"    {status} {opp['column']}: {opp['populated']}/{opp['total']}")
    
    # FK relationship check
    check_fk_relationships()
    
    # Cascade value check
    check_cascade_values()
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total dimension tables: {len(all_results)}")
    print(f"Tables with issues: {sum(1 for r in all_results if r['issues'])}")
    print(f"Total issues found: {issues_count}")
    
    # Tables needing attention
    tables_with_issues = [r for r in all_results if r['issues']]
    if tables_with_issues:
        print("\nTables needing attention:")
        for r in tables_with_issues:
            print(f"  - {r['table_name']}: {len(r['issues'])} issues")


if __name__ == '__main__':
    main()
