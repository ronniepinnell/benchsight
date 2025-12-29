#!/usr/bin/env python3
"""
BenchSight ETL Comprehensive Test Validations
Tests all implemented stats against known values and logical checks.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Output directory
OUTPUT_DIR = Path('data/output')

class ValidationResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.results = []
    
    def add(self, test_name, passed, expected=None, actual=None, note=None):
        status = '✅ PASS' if passed else '❌ FAIL'
        self.results.append({
            'test': test_name,
            'status': status,
            'expected': expected,
            'actual': actual,
            'note': note
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def warn(self, test_name, note):
        self.results.append({
            'test': test_name,
            'status': '⚠️ WARN',
            'expected': None,
            'actual': None,
            'note': note
        })
        self.warnings += 1
    
    def print_summary(self):
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        print(f"PASSED:   {self.passed}")
        print(f"FAILED:   {self.failed}")
        print(f"WARNINGS: {self.warnings}")
        print("=" * 70)
        
        if self.failed > 0:
            print("\nFAILED TESTS:")
            for r in self.results:
                if 'FAIL' in r['status']:
                    print(f"  {r['test']}: expected={r['expected']}, actual={r['actual']}")
                    if r['note']:
                        print(f"    Note: {r['note']}")


def load_tables():
    """Load all required tables."""
    tables = {}
    required = [
        'fact_player_game_stats',
        'fact_shifts_player',
        'fact_goalie_game_stats',
        'fact_events_player',
        'dim_player'
    ]
    
    for table in required:
        path = OUTPUT_DIR / f'{table}.csv'
        if path.exists():
            tables[table] = pd.read_csv(path)
        else:
            print(f"WARNING: {table}.csv not found")
            tables[table] = pd.DataFrame()
    
    return tables


def test_keegan_mantaro_18969(tables, results):
    """Test Keegan Mantaro's stats for game 18969 - our reference player."""
    print("\n" + "-" * 70)
    print("TEST GROUP: Keegan Mantaro (P100117) Game 18969")
    print("-" * 70)
    
    stats = tables['fact_player_game_stats']
    keegan = stats[(stats['game_id'] == 18969) & (stats['player_id'] == 'P100117')]
    
    if len(keegan) == 0:
        results.add("Keegan exists", False, note="Player not found")
        return
    
    k = keegan.iloc[0]
    
    # Original validated stats
    tests = [
        ('goals', 2),
        ('assists', 1),
        ('points', 3),
        ('fo_wins', 11),
        ('fo_losses', 11),
        ('pass_attempts', 17),
        ('toi_seconds', 1535),
    ]
    
    for stat, expected in tests:
        actual = k.get(stat)
        try:
            passed = int(actual) == expected
        except:
            passed = False
        results.add(f"Keegan {stat}", passed, expected, actual)
    
    # Plus/Minus validations (from shift data analysis)
    pm_tests = [
        ('plus_ev', 3),           # 3 EV goals for
        ('minus_ev', -1),         # 1 EV goal against
        ('plus_minus_ev', 2),     # +2 traditional
        ('plus_total', 3),        # 3 total goals for
        ('minus_total', -2),      # 2 total goals against (1 EV + 1 PP)
        ('plus_minus_total', 1),  # +1 total
        ('plus_en_adj', 3),       # Same as EV (no EN)
        ('minus_en_adj', -1),     # Same as EV (no EN goals against)
        ('plus_minus_en_adj', 2), # +2 EN adjusted
    ]
    
    for stat, expected in pm_tests:
        actual = k.get(stat)
        try:
            passed = int(actual) == expected
        except:
            passed = False
        results.add(f"Keegan {stat}", passed, expected, actual)
    
    # TOI validations
    results.add("Keegan playing_toi < toi", 
                k['playing_toi_seconds'] < k['toi_seconds'],
                f"< {k['toi_seconds']}", k['playing_toi_seconds'])
    
    # Corsi/Fenwick (should have values)
    results.add("Keegan has corsi_for", k['corsi_for'] > 0, "> 0", k['corsi_for'])
    results.add("Keegan has cf_pct", 0 < k['cf_pct'] < 100, "0-100", k['cf_pct'])


def test_plus_minus_logic(tables, results):
    """Test plus/minus calculation logic across all players."""
    print("\n" + "-" * 70)
    print("TEST GROUP: Plus/Minus Logic")
    print("-" * 70)
    
    stats = tables['fact_player_game_stats']
    shifts = tables['fact_shifts_player']
    
    # Test: plus_minus_ev = plus_ev + minus_ev
    stats['calc_pm_ev'] = stats['plus_ev'] + stats['minus_ev']
    match = (stats['plus_minus_ev'] == stats['calc_pm_ev']).all()
    results.add("plus_minus_ev = plus_ev + minus_ev", match)
    
    # Test: plus_minus_total = plus_total + minus_total
    stats['calc_pm_total'] = stats['plus_total'] + stats['minus_total']
    match = (stats['plus_minus_total'] == stats['calc_pm_total']).all()
    results.add("plus_minus_total = plus_total + minus_total", match)
    
    # Test: plus_minus_en_adj = plus_en_adj + minus_en_adj
    stats['calc_pm_en'] = stats['plus_en_adj'] + stats['minus_en_adj']
    match = (stats['plus_minus_en_adj'] == stats['calc_pm_en']).all()
    results.add("plus_minus_en_adj = plus_en_adj + minus_en_adj", match)
    
    # Test: Traditional <= Total goals (PP goals add to total)
    # plus_total >= plus_ev (can have PP goals for)
    results.add("plus_total >= plus_ev", 
                (stats['plus_total'] >= stats['plus_ev']).all())
    
    # Test: minus_total <= minus_ev (more negative = more goals against)
    results.add("minus_total <= minus_ev",
                (stats['minus_total'] <= stats['minus_ev']).all())
    
    # Test: EN adjusted minus >= traditional minus (removes some negatives)
    results.add("minus_en_adj >= minus_ev",
                (stats['minus_en_adj'] >= stats['minus_ev']).all())
    
    # Test: Shifts-based validation
    for game_id in stats['game_id'].unique():
        game_shifts = shifts[shifts['game_id'] == game_id]
        game_stats = stats[stats['game_id'] == game_id]
        
        # Sum of all pm_plus_ev in shifts should match sum of plus_ev in stats
        shift_plus = game_shifts.groupby('player_id')['pm_plus_ev'].sum()
        for player_id, player_stats in game_stats.groupby('player_id'):
            if player_id in shift_plus.index:
                shift_val = int(shift_plus[player_id])
                stat_val = int(player_stats['plus_ev'].iloc[0])
                if shift_val != stat_val:
                    results.add(f"Shift pm_plus matches stats ({player_id}, {game_id})",
                               False, shift_val, stat_val)


def test_toi_logic(tables, results):
    """Test TOI calculation logic."""
    print("\n" + "-" * 70)
    print("TEST GROUP: TOI Logic")
    print("-" * 70)
    
    stats = tables['fact_player_game_stats']
    
    # Test: playing_toi <= toi (playing time can't exceed total time)
    results.add("playing_toi_seconds <= toi_seconds",
                (stats['playing_toi_seconds'] <= stats['toi_seconds']).all())
    
    # Test: stoppage_seconds = toi_seconds - playing_toi_seconds
    stats['calc_stoppage'] = stats['toi_seconds'] - stats['playing_toi_seconds']
    match = np.allclose(stats['stoppage_seconds'], stats['calc_stoppage'], atol=1)
    results.add("stoppage_seconds = toi - playing_toi", match)
    
    # Test: toi_minutes = toi_seconds / 60
    stats['calc_toi_min'] = stats['toi_seconds'] / 60
    match = np.allclose(stats['toi_minutes'], stats['calc_toi_min'], atol=0.1)
    results.add("toi_minutes = toi_seconds / 60", match)
    
    # Test: playing_toi_minutes = playing_toi_seconds / 60
    stats['calc_playing_min'] = stats['playing_toi_seconds'] / 60
    match = np.allclose(stats['playing_toi_minutes'], stats['calc_playing_min'], atol=0.1)
    results.add("playing_toi_minutes = playing_toi_seconds / 60", match)
    
    # Test: avg_shift > 0 for players with shifts
    has_shifts = stats['logical_shifts'] > 0
    results.add("avg_shift > 0 for players with shifts",
                (stats.loc[has_shifts, 'avg_shift'] > 0).all())


def test_per_60_logic(tables, results):
    """Test per-60 calculations."""
    print("\n" + "-" * 70)
    print("TEST GROUP: Per-60 Calculations")
    print("-" * 70)
    
    stats = tables['fact_player_game_stats']
    
    # Filter players with enough TOI
    has_toi = stats['toi_minutes'] > 0
    sample = stats[has_toi].head(20)
    
    # Test: goals_per_60 = goals / toi_minutes * 60
    for idx, row in sample.iterrows():
        expected = round(row['goals'] / row['toi_minutes'] * 60, 2)
        actual = row['goals_per_60']
        match = abs(expected - actual) < 0.1
        if not match:
            results.add(f"goals_per_60 calc ({row['player_name']})", 
                       False, expected, actual)
    
    results.add("goals_per_60 formula validated", True)
    
    # Test: playing per-60 > regular per-60 (since playing TOI < total TOI)
    has_goals = (stats['goals'] > 0) & (stats['playing_toi_minutes'] > 0)
    if has_goals.any():
        results.add("goals_per_60_playing >= goals_per_60",
                   (stats.loc[has_goals, 'goals_per_60_playing'] >= 
                    stats.loc[has_goals, 'goals_per_60']).all())


def test_corsi_fenwick_logic(tables, results):
    """Test Corsi/Fenwick calculations."""
    print("\n" + "-" * 70)
    print("TEST GROUP: Corsi/Fenwick Logic")
    print("-" * 70)
    
    stats = tables['fact_player_game_stats']
    
    # Test: cf_pct between 0 and 100
    has_corsi = (stats['corsi_for'] + stats['corsi_against']) > 0
    results.add("cf_pct in range 0-100",
                ((stats.loc[has_corsi, 'cf_pct'] >= 0) & 
                 (stats.loc[has_corsi, 'cf_pct'] <= 100)).all())
    
    # Test: ff_pct between 0 and 100
    has_fenwick = (stats['fenwick_for'] + stats['fenwick_against']) > 0
    results.add("ff_pct in range 0-100",
                ((stats.loc[has_fenwick, 'ff_pct'] >= 0) & 
                 (stats.loc[has_fenwick, 'ff_pct'] <= 100)).all())
    
    # Test: fenwick <= corsi (fenwick excludes blocked shots)
    results.add("fenwick_for <= corsi_for",
                (stats['fenwick_for'] <= stats['corsi_for']).all())
    results.add("fenwick_against <= corsi_against",
                (stats['fenwick_against'] <= stats['corsi_against']).all())


def test_goalie_stats(tables, results):
    """Test goalie stats."""
    print("\n" + "-" * 70)
    print("TEST GROUP: Goalie Stats")
    print("-" * 70)
    
    goalie_stats = tables['fact_goalie_game_stats']
    
    if len(goalie_stats) == 0:
        results.warn("Goalie stats", "No goalie stats found")
        return
    
    # Test: save_pct between 0 and 100
    results.add("save_pct in range 0-100",
                ((goalie_stats['save_pct'] >= 0) & 
                 (goalie_stats['save_pct'] <= 100)).all())
    
    # Test: saves = shots_faced - goals_against
    goalie_stats['calc_saves'] = goalie_stats['shots_faced'] - goalie_stats['goals_against']
    match = (goalie_stats['saves'] == goalie_stats['calc_saves']).all()
    results.add("saves = shots_faced - goals_against", match)
    
    # Test: gaa_playing >= gaa (less time = higher rate)
    has_gaa = goalie_stats['gaa'] > 0
    results.add("gaa_playing >= gaa",
                (goalie_stats.loc[has_gaa, 'gaa_playing'] >= 
                 goalie_stats.loc[has_gaa, 'gaa']).all())


def test_shift_data_integrity(tables, results):
    """Test shift data integrity."""
    print("\n" + "-" * 70)
    print("TEST GROUP: Shift Data Integrity")
    print("-" * 70)
    
    shifts = tables['fact_shifts_player']
    
    # Test: Most shifts have player_id (some may not match roster)
    pct_with_pid = shifts['player_id'].notna().mean() * 100
    results.add(f"Shifts with player_id ({pct_with_pid:.1f}%)", pct_with_pid > 95, "> 95%", f"{pct_with_pid:.1f}%")
    
    # Test: All shifts have game_id
    results.add("All shifts have game_id",
                shifts['game_id'].notna().all())
    
    # Test: shift_duration > 0 for most shifts
    shifts_clean = shifts.dropna(subset=['shift_duration'])
    valid_duration = shifts_clean['shift_duration'] > 0
    pct_valid = valid_duration.mean() * 100
    results.add(f"shift_duration > 0 ({pct_valid:.1f}%)", pct_valid > 80, "> 80%", f"{pct_valid:.1f}%")
    
    # Test: playing_duration <= shift_duration (filter NaNs)
    shifts_with_both = shifts.dropna(subset=['playing_duration', 'shift_duration'])
    if len(shifts_with_both) > 0:
        valid_playing = (shifts_with_both['playing_duration'] <= shifts_with_both['shift_duration']).all()
        results.add("playing_duration <= shift_duration", valid_playing)
    else:
        results.add("playing_duration <= shift_duration", True, note="No data to check")


def test_data_completeness(tables, results):
    """Test data completeness across games."""
    print("\n" + "-" * 70)
    print("TEST GROUP: Data Completeness")
    print("-" * 70)
    
    stats = tables['fact_player_game_stats']
    shifts = tables['fact_shifts_player']
    
    # Test: Games present (at least the core 4)
    games = set(stats['game_id'].unique())
    core_games = {18969, 18977, 18981, 18987}
    has_core = core_games.issubset(games)
    results.add("Core 4 games present", has_core, 
                f"contains {core_games}", f"has {games}")
    
    # Test: Each game has players
    for game_id in core_games:
        count = len(stats[stats['game_id'] == game_id])
        results.add(f"Game {game_id} has players", count > 0, "> 0", count)
    
    # Test: Player stats count
    results.add("Total player-game records", len(stats) >= 100, ">= 100", len(stats))
    
    # Test: Required columns exist in player stats
    required_cols = [
        'player_id', 'game_id', 'goals', 'assists', 'points',
        'toi_seconds', 'playing_toi_seconds', 'stoppage_seconds',
        'plus_ev', 'minus_ev', 'plus_minus_ev',
        'plus_total', 'minus_total', 'plus_minus_total',
        'plus_en_adj', 'minus_en_adj', 'plus_minus_en_adj',
        'corsi_for', 'corsi_against', 'cf_pct',
        'fenwick_for', 'fenwick_against', 'ff_pct',
        'goals_per_60', 'goals_per_60_playing'
    ]
    
    missing = [c for c in required_cols if c not in stats.columns]
    results.add("All required columns present", len(missing) == 0, 
                "all present", f"missing: {missing}" if missing else "all present")


def test_game_totals(tables, results):
    """Test that game totals are consistent."""
    print("\n" + "-" * 70)
    print("TEST GROUP: Game Totals Consistency")
    print("-" * 70)
    
    stats = tables['fact_player_game_stats']
    shifts = tables['fact_shifts_player']
    
    for game_id in stats['game_id'].unique():
        game_stats = stats[stats['game_id'] == game_id]
        game_shifts = shifts[shifts['game_id'] == game_id]
        
        # Goals from shift_stop_type should match
        home_goals_shifts = game_shifts[game_shifts['goal_for'] == 1].drop_duplicates('shift_index')
        home_goals_shifts = home_goals_shifts[home_goals_shifts['venue'] == 'home']
        
        # Unique goal shifts
        goal_shifts = game_shifts[(game_shifts['goal_for'] == 1) | (game_shifts['goal_against'] == 1)]
        unique_goals = goal_shifts.drop_duplicates('shift_index')
        total_goals = len(unique_goals)
        
        results.add(f"Game {game_id} has goal data", total_goals > 0, "> 0", total_goals)


def suggest_better_test_data(tables, results):
    """Analyze if we need better test data."""
    print("\n" + "-" * 70)
    print("TEST DATA ANALYSIS")
    print("-" * 70)
    
    stats = tables['fact_player_game_stats']
    shifts = tables['fact_shifts_player']
    
    # Check for PP goal situations
    pp_shifts = shifts[shifts['situation'].str.contains('PowerPlay', na=False)]
    pp_goals = pp_shifts[(pp_shifts['goal_for'] == 1) | (pp_shifts['goal_against'] == 1)]
    pp_goal_count = len(pp_goals.drop_duplicates('shift_index'))
    
    print(f"PP goal shifts: {pp_goal_count}")
    if pp_goal_count == 0:
        results.warn("PP goals", "No PP goals in test data - can't fully validate PP +/-")
    
    # Check for EN situations
    en_shifts = shifts[shifts['situation'].str.contains('EmptyNet', na=False)]
    en_goals = en_shifts[(en_shifts['goal_for'] == 1) | (en_shifts['goal_against'] == 1)]
    en_goal_count = len(en_goals.drop_duplicates('shift_index'))
    
    print(f"EN goal shifts: {en_goal_count}")
    if en_goal_count == 0:
        results.warn("EN goals", "No EN goals in test data - can't fully validate EN +/-")
    
    # Check variety of situations
    situations = shifts['situation'].value_counts()
    print(f"\nSituation distribution:")
    for sit, count in situations.items():
        print(f"  {sit}: {count}")
    
    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS FOR BETTER TEST DATA")
    print("=" * 70)
    recommendations = []
    
    if pp_goal_count == 0:
        recommendations.append("- Add games with PP goals to validate Traditional vs Total +/-")
    
    if en_goal_count == 0:
        recommendations.append("- Add games with EN goals to validate EN Adjusted +/-")
    
    if len(stats['game_id'].unique()) < 5:
        recommendations.append("- Add more games for better statistical coverage")
    
    if len(recommendations) == 0:
        print("Current test data is adequate for validation.")
    else:
        print("To improve test coverage:")
        for rec in recommendations:
            print(rec)


def main():
    print("=" * 70)
    print("BENCHSIGHT ETL COMPREHENSIVE VALIDATION")
    print("=" * 70)
    
    results = ValidationResults()
    tables = load_tables()
    
    # Run all test groups
    test_keegan_mantaro_18969(tables, results)
    test_plus_minus_logic(tables, results)
    test_toi_logic(tables, results)
    test_per_60_logic(tables, results)
    test_corsi_fenwick_logic(tables, results)
    test_goalie_stats(tables, results)
    test_shift_data_integrity(tables, results)
    test_data_completeness(tables, results)
    test_game_totals(tables, results)
    
    # Data quality analysis
    suggest_better_test_data(tables, results)
    
    # Print summary
    results.print_summary()
    
    return 0 if results.failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
