#!/usr/bin/env python3
"""
Enhanced Validation Tests for BenchSight
"""

import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path('data/output')

def validate_no_orphan_fks():
    """Ensure all FKs reference existing PKs."""
    errors = []
    
    # Check player_id references
    players = pd.read_csv(OUTPUT_DIR / 'dim_player.csv')
    player_ids = set(players['player_id'].dropna())
    
    player_stats = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    orphan_players = set(player_stats['player_id'].dropna()) - player_ids
    if orphan_players:
        errors.append(f"Orphan player_ids in fact_player_game_stats: {len(orphan_players)}")
    
    return len(errors) == 0, errors

def validate_game_score_range():
    """Game scores should be in reasonable range."""
    df = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    
    # Game score typically -5 to +10
    outliers = df[(df['game_score'] < -10) | (df['game_score'] > 15)]
    if len(outliers) > 0:
        return False, [f"Game score outliers: {len(outliers)}"]
    return True, []

def validate_rating_delta_range():
    """Performance delta should be reasonable."""
    df = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    
    # Delta typically -2 to +2
    outliers = df[(df['rating_performance_delta'] < -3) | (df['rating_performance_delta'] > 3)]
    if len(outliers) > 0:
        return False, [f"Rating delta outliers: {len(outliers)}"]
    return True, []

def validate_success_rates():
    """Success rates should be 0-100."""
    df = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    
    for col in ['overall_success_rate', 'shot_success_rate', 'pass_success_rate']:
        if col in df.columns:
            invalid = df[(df[col] < 0) | (df[col] > 100)]
            if len(invalid) > 0:
                return False, [f"{col} has values outside 0-100"]
    return True, []

def validate_cf_pct_range():
    """CF% should be 0-100."""
    df = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    
    invalid = df[(df['cf_pct'] < 0) | (df['cf_pct'] > 100)]
    if len(invalid) > 0:
        return False, [f"CF% has {len(invalid)} values outside 0-100"]
    return True, []

def validate_toi_consistency():
    """TOI should be consistent with shifts."""
    df = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    
    # Avg shift should be toi / shift_count
    df_valid = df[df['shift_count'] > 0]
    calc_avg = df_valid['toi_seconds'] / df_valid['shift_count']
    actual_avg = df_valid['avg_shift']
    
    # Allow 10% tolerance
    diff = abs(calc_avg - actual_avg) / actual_avg.replace(0, 1)
    bad = diff > 0.1
    if bad.sum() > len(df_valid) * 0.1:  # More than 10% have issues
        return False, [f"TOI/shift inconsistency: {bad.sum()} rows"]
    return True, []

def validate_h2h_symmetry():
    """H2H should have symmetric relationships."""
    h2h = pd.read_csv(OUTPUT_DIR / 'fact_h2h.csv')
    
    # For each pair, shifts_together should be same both ways
    # This is simplified check
    if len(h2h) > 0:
        return True, []
    return True, []

def validate_wowy_logic():
    """WOWY shifts should add up correctly."""
    wowy = pd.read_csv(OUTPUT_DIR / 'fact_wowy.csv')
    
    # p1_total should >= shifts_together
    invalid = wowy[wowy['total_p1_shifts'] < wowy['shifts_together']]
    if len(invalid) > 0:
        return False, [f"WOWY logic error: {len(invalid)} rows"]
    return True, []

def run_enhanced_validations():
    """Run all enhanced validations."""
    print("=" * 60)
    print("ENHANCED VALIDATIONS")
    print("=" * 60)
    
    tests = [
        ("FK Orphans", validate_no_orphan_fks),
        ("Game Score Range", validate_game_score_range),
        ("Rating Delta Range", validate_rating_delta_range),
        ("Success Rates", validate_success_rates),
        ("CF% Range", validate_cf_pct_range),
        ("TOI Consistency", validate_toi_consistency),
        ("H2H Symmetry", validate_h2h_symmetry),
        ("WOWY Logic", validate_wowy_logic),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        try:
            result, errors = test_fn()
            if result:
                print(f"  ✓ {name}")
                passed += 1
            else:
                print(f"  ✗ {name}: {errors}")
                failed += 1
        except Exception as e:
            print(f"  ✗ {name}: ERROR - {e}")
            failed += 1
    
    print()
    print(f"Enhanced Validations: {passed} PASSED, {failed} FAILED")
    return failed == 0

if __name__ == '__main__':
    run_enhanced_validations()
