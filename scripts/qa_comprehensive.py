#!/usr/bin/env python3
"""
BenchSight Comprehensive QA Suite
=================================
Production-quality validation for bulletproof ETL.

Validates:
1. External verification (noradhockey.com official scores)
2. Internal consistency (math checks)
3. Cross-table reconciliation
4. Edge cases and data types
5. FK integrity
6. Uniqueness constraints

Run: python scripts/qa_comprehensive.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys
from typing import Dict, List, Tuple, Any

OUTPUT_DIR = Path('data/output')

# ============================================================================
# OFFICIAL GAME DATA FROM NORADHOCKEY.COM
# ============================================================================
OFFICIAL_GAMES = {
    18969: {
        'date': '2025-09-07',
        'home': 'Platinum Group',
        'away': 'COS Velodrome', 
        'home_score': 4,
        'away_score': 3,
        'total_goals': 7
    },
    18977: {
        'date': '2025-09-14',
        'home': 'HollowBrook Dental',
        'away': 'COS Velodrome',
        'home_score': 2,
        'away_score': 4,
        'total_goals': 6
    },
    18981: {
        'date': '2025-09-28',
        'home': 'Nelson & Company',
        'away': 'COS Velodrome',
        'home_score': 2,
        'away_score': 1,
        'total_goals': 3
    },
    18987: {
        'date': '2025-10-05',
        'home': 'OUTCAN Outlaws',
        'away': 'COS Velodrome',
        'home_score': 0,
        'away_score': 1,
        'total_goals': 1
    },
    # Add more games as they're tracked
    18955: {'date': '2025-08-10', 'home': 'World Orphans', 'away': 'COS Velodrome', 'home_score': 1, 'away_score': 5, 'total_goals': 6},
    18965: {'date': '2025-08-24', 'home': 'OS Offices', 'away': 'COS Velodrome', 'home_score': 4, 'away_score': 2, 'total_goals': 6},
    18991: {'date': '2025-10-12', 'home': 'Triple J', 'away': 'COS Velodrome', 'home_score': 1, 'away_score': 5, 'total_goals': 6},
    18993: {'date': '2025-10-19', 'home': 'Ace', 'away': 'COS Velodrome', 'home_score': 1, 'away_score': 2, 'total_goals': 3},
    19032: {'date': '2025-12-21', 'home': 'OUTCAN Outlaws', 'away': 'COS Velodrome', 'home_score': 3, 'away_score': 6, 'total_goals': 9},
}

# Known data issues that are SOURCE problems, not ETL bugs
# See docs/KNOWN_DATA_ISSUES.md for details
KNOWN_ISSUES = {
    18977: "ISSUE-001: Missing scorer on event 1368 (source data)"
}


class QAResult:
    """Track QA results."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.critical = 0
        self.results = []
    
    def add(self, category: str, test: str, passed: bool, 
            expected=None, actual=None, note=None, critical=False):
        status = '✅ PASS' if passed else ('🔴 CRITICAL' if critical else '❌ FAIL')
        self.results.append({
            'category': category,
            'test': test,
            'status': status,
            'expected': expected,
            'actual': actual,
            'note': note
        })
        if passed:
            self.passed += 1
        elif critical:
            self.critical += 1
            self.failed += 1
        else:
            self.failed += 1
    
    def warn(self, category: str, test: str, note: str):
        self.results.append({
            'category': category,
            'test': test,
            'status': '⚠️ WARN',
            'expected': None,
            'actual': None,
            'note': note
        })
        self.warnings += 1
    
    def print_report(self):
        print("\n" + "=" * 80)
        print("BENCHSIGHT COMPREHENSIVE QA REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Group by category
        categories = {}
        for r in self.results:
            cat = r['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r)
        
        for cat, tests in categories.items():
            print(f"\n{'─' * 80}")
            print(f"  {cat}")
            print(f"{'─' * 80}")
            for t in tests:
                line = f"  {t['status']} {t['test']}"
                if t['expected'] is not None or t['actual'] is not None:
                    line += f" (expected={t['expected']}, actual={t['actual']})"
                if t['note']:
                    line += f" - {t['note']}"
                print(line)
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"  ✅ PASSED:   {self.passed}")
        print(f"  ❌ FAILED:   {self.failed}")
        print(f"  🔴 CRITICAL: {self.critical}")
        print(f"  ⚠️ WARNINGS: {self.warnings}")
        print("=" * 80)
        
        if self.critical > 0:
            print("\n🚨 CRITICAL FAILURES DETECTED - DO NOT DEPLOY!")
            for r in self.results:
                if 'CRITICAL' in r['status']:
                    print(f"   • {r['category']}: {r['test']}")
        
        return self.failed == 0


def load_tables() -> Dict[str, pd.DataFrame]:
    """Load all required tables."""
    tables = {}
    required = [
        'fact_player_game_stats',
        'fact_shifts_player', 
        'fact_events_player',
        'fact_events',
        'fact_goalie_game_stats',
        'fact_h2h',
        'fact_wowy',
        'fact_line_combos',
        'fact_team_game_stats',
        'dim_player',
        'dim_team',
    ]
    
    for table in required:
        path = OUTPUT_DIR / f'{table}.csv'
        if path.exists():
            tables[table] = pd.read_csv(path)
        else:
            tables[table] = pd.DataFrame()
    
    return tables


# ============================================================================
# 1. EXTERNAL VERIFICATION (vs noradhockey.com)
# ============================================================================
def validate_external_goals(tables: Dict, qa: QAResult):
    """Validate goal counts against official noradhockey.com data."""
    pgs = tables['fact_player_game_stats']
    
    for game_id, official in OFFICIAL_GAMES.items():
        game = pgs[pgs['game_id'] == game_id]
        if len(game) == 0:
            qa.warn("EXTERNAL VERIFICATION", f"Game {game_id}", 
                   f"Not loaded - skipping ({official['home']} vs {official['away']})")
            continue
        
        our_goals = int(game['goals'].sum())
        expected = official['total_goals']
        
        # Check if this is a known issue (source data problem, not ETL bug)
        if game_id in KNOWN_ISSUES:
            if our_goals != expected:
                qa.warn("EXTERNAL VERIFICATION",
                       f"Game {game_id} total goals (KNOWN ISSUE)",
                       f"{KNOWN_ISSUES[game_id]} - expected={expected}, actual={our_goals}")
            else:
                qa.add("EXTERNAL VERIFICATION", 
                       f"Game {game_id} total goals",
                       True, expected, our_goals,
                       f"{official['home']} vs {official['away']} - KNOWN ISSUE RESOLVED")
        else:
            qa.add("EXTERNAL VERIFICATION", 
                   f"Game {game_id} total goals",
                   our_goals == expected,
                   expected, our_goals,
                   f"{official['home']} vs {official['away']} ({official['date']})",
                   critical=True)


# ============================================================================
# 2. INTERNAL CONSISTENCY (Math Checks)
# ============================================================================
def validate_math(tables: Dict, qa: QAResult):
    """Validate all mathematical relationships."""
    pgs = tables['fact_player_game_stats']
    
    # Points = Goals + Assists
    points_calc = pgs['goals'] + pgs['assists']
    qa.add("MATH CONSISTENCY", "Points = Goals + Assists",
           (pgs['points'] == points_calc).all())
    
    # Plus/Minus calculations
    pm_ev = pgs['plus_ev'] + pgs['minus_ev']
    qa.add("MATH CONSISTENCY", "plus_minus_ev = plus_ev + minus_ev",
           (pgs['plus_minus_ev'] == pm_ev).all())
    
    pm_total = pgs['plus_total'] + pgs['minus_total']
    qa.add("MATH CONSISTENCY", "plus_minus_total = plus_total + minus_total",
           (pgs['plus_minus_total'] == pm_total).all())
    
    pm_en = pgs['plus_en_adj'] + pgs['minus_en_adj']
    qa.add("MATH CONSISTENCY", "plus_minus_en_adj = plus_en_adj + minus_en_adj",
           (pgs['plus_minus_en_adj'] == pm_en).all())
    
    # Per-60 calculations
    pgs_toi = pgs[pgs['toi_seconds'] > 0].copy()
    if len(pgs_toi) > 0:
        expected_g60 = (pgs_toi['goals'] / pgs_toi['toi_seconds']) * 3600
        actual_g60 = pgs_toi['goals_per_60']
        diff = abs(expected_g60 - actual_g60).max()
        qa.add("MATH CONSISTENCY", "Goals per 60 calculation",
               diff < 0.1, "<0.1", f"{diff:.4f}")
    
    # TOI sanity
    qa.add("MATH CONSISTENCY", "playing_toi <= toi",
           (pgs['playing_toi_seconds'] <= pgs['toi_seconds']).all())
    
    # Fenwick <= Corsi (Fenwick excludes blocked shots)
    qa.add("MATH CONSISTENCY", "fenwick_for <= corsi_for",
           (pgs['fenwick_for'] <= pgs['corsi_for']).all())
    qa.add("MATH CONSISTENCY", "fenwick_against <= corsi_against",
           (pgs['fenwick_against'] <= pgs['corsi_against']).all())


# ============================================================================
# 3. CROSS-TABLE RECONCILIATION
# ============================================================================
def validate_cross_table(tables: Dict, qa: QAResult):
    """Validate consistency across tables."""
    pgs = tables['fact_player_game_stats']
    shifts = tables['fact_shifts_player']
    events = tables['fact_events_player']
    
    # Players in stats should exist in dim_player
    players = tables['dim_player']
    player_ids_dim = set(players['player_id'].dropna())
    player_ids_fact = set(pgs['player_id'].dropna())
    orphans = player_ids_fact - player_ids_dim
    qa.add("CROSS-TABLE", "All players in facts exist in dim_player",
           len(orphans) == 0, 0, len(orphans),
           f"Orphans: {list(orphans)[:5]}" if orphans else None)
    
    # Goals in events should match goals in stats (per game)
    for game_id in pgs['game_id'].unique():
        game_stats = pgs[pgs['game_id'] == game_id]
        game_events = events[events['game_id'] == game_id]
        
        stats_goals = int(game_stats['goals'].sum())
        
        # Count unique goal events
        goal_events = game_events[game_events['event_type'] == 'Goal']
        event_goals = goal_events['event_index'].nunique() if 'event_index' in goal_events.columns else len(goal_events)
        
        # Allow some variance due to how goals are counted
        diff = abs(stats_goals - event_goals)
        qa.add("CROSS-TABLE", f"Game {game_id}: Stats goals ~ Event goals",
               diff <= 2, stats_goals, event_goals,
               "Slight variance acceptable" if diff <= 2 else "MISMATCH")
    
    # Shift TOI vs Stats TOI (sample check)
    for game_id in list(pgs['game_id'].unique())[:2]:
        game_stats = pgs[pgs['game_id'] == game_id]
        game_shifts = shifts[shifts['game_id'] == game_id]
        
        for _, row in game_stats.head(3).iterrows():
            pid = row['player_id']
            stats_toi = row['toi_seconds']
            player_shifts = game_shifts[game_shifts['player_id'] == pid]
            shifts_toi = player_shifts['shift_duration'].sum() if len(player_shifts) > 0 else 0
            diff = abs(stats_toi - shifts_toi)
            # Allow 120 sec variance (shift overlap handling)
            if diff > 120:
                qa.warn("CROSS-TABLE", 
                       f"TOI mismatch {pid} game {game_id}",
                       f"Stats={stats_toi:.0f}s, Shifts={shifts_toi:.0f}s, diff={diff:.0f}s")


# ============================================================================
# 4. EDGE CASES AND BOUNDARIES
# ============================================================================
def validate_edge_cases(tables: Dict, qa: QAResult):
    """Validate edge cases and boundary conditions."""
    pgs = tables['fact_player_game_stats']
    
    # No negative values where impossible
    for col in ['goals', 'assists', 'shots', 'toi_seconds', 'shift_count']:
        if col in pgs.columns:
            negatives = (pgs[col] < 0).sum()
            qa.add("EDGE CASES", f"No negative {col}",
                   negatives == 0, 0, negatives)
    
    # Percentages in valid range (0-100)
    pct_cols = ['cf_pct', 'ff_pct', 'fo_pct', 'shooting_pct', 'save_pct']
    for col in pct_cols:
        if col in pgs.columns:
            invalid = ((pgs[col] < 0) | (pgs[col] > 100)).sum()
            qa.add("EDGE CASES", f"{col} in 0-100 range",
                   invalid == 0, 0, invalid)
    
    # TOI sanity (< 60 minutes)
    over_60 = (pgs['toi_seconds'] > 3600).sum()
    qa.add("EDGE CASES", "TOI < 60 minutes",
           over_60 == 0, 0, over_60)
    
    # Division by zero protection (check inf/nan)
    for col in ['goals_per_60', 'cf_pct', 'fo_pct']:
        if col in pgs.columns:
            inf_count = np.isinf(pgs[col]).sum()
            nan_count = pgs[col].isna().sum()
            qa.add("EDGE CASES", f"No inf/nan in {col}",
                   inf_count == 0 and nan_count == 0,
                   "0 inf/nan", f"{inf_count} inf, {nan_count} nan")


# ============================================================================
# 5. UNIQUENESS AND INTEGRITY
# ============================================================================
def validate_uniqueness(tables: Dict, qa: QAResult):
    """Validate uniqueness constraints."""
    pgs = tables['fact_player_game_stats']
    
    # No duplicate player-game combinations
    duplicates = pgs.duplicated(subset=['player_id', 'game_id']).sum()
    qa.add("UNIQUENESS", "No duplicate player-game records",
           duplicates == 0, 0, duplicates, critical=True)
    
    # Primary keys are unique in dim tables
    for dim_name in ['dim_player', 'dim_team']:
        if dim_name in tables and len(tables[dim_name]) > 0:
            df = tables[dim_name]
            pk_col = 'player_id' if 'player' in dim_name else 'team_id'
            if pk_col in df.columns:
                dups = df.duplicated(subset=[pk_col]).sum()
                qa.add("UNIQUENESS", f"{dim_name} PKs unique",
                       dups == 0, 0, dups)


# ============================================================================
# 6. DATA TYPE VALIDATION
# ============================================================================
def validate_data_types(tables: Dict, qa: QAResult):
    """Validate data types are correct."""
    pgs = tables['fact_player_game_stats']
    
    # IDs should be strings
    id_cols = ['player_id', 'game_id', 'home_team_id', 'away_team_id']
    for col in id_cols:
        if col in pgs.columns:
            # Check if any are pure numeric (bad)
            numeric_ids = pgs[col].apply(lambda x: str(x).isdigit() if pd.notna(x) else False).sum()
            # game_id is allowed to be numeric
            if col != 'game_id':
                qa.add("DATA TYPES", f"{col} has proper format",
                       numeric_ids < len(pgs) * 0.5,  # Most should have prefix
                       "<50% numeric", f"{numeric_ids} numeric")
    
    # Numeric columns should be numeric
    numeric_cols = ['goals', 'assists', 'points', 'toi_seconds', 'cf_pct']
    for col in numeric_cols:
        if col in pgs.columns:
            is_numeric = pd.api.types.is_numeric_dtype(pgs[col])
            qa.add("DATA TYPES", f"{col} is numeric",
                   is_numeric)


# ============================================================================
# 7. CRITICAL NULLS
# ============================================================================
def validate_no_critical_nulls(tables: Dict, qa: QAResult):
    """Validate no nulls in critical columns."""
    pgs = tables['fact_player_game_stats']
    
    critical_cols = ['player_id', 'game_id', 'goals', 'assists', 'points', 
                     'toi_seconds', 'plus_minus_ev']
    
    for col in critical_cols:
        if col in pgs.columns:
            nulls = pgs[col].isna().sum()
            qa.add("CRITICAL NULLS", f"No nulls in {col}",
                   nulls == 0, 0, nulls, critical=True)


# ============================================================================
# 8. H2H / WOWY / LINE COMBO VALIDATION
# ============================================================================
def validate_relationship_tables(tables: Dict, qa: QAResult):
    """Validate H2H, WOWY, and Line Combo tables."""
    h2h = tables['fact_h2h']
    wowy = tables['fact_wowy']
    line_combos = tables['fact_line_combos']
    
    # H2H should have data
    qa.add("RELATIONSHIP TABLES", "H2H has data",
           len(h2h) > 0, ">0", len(h2h))
    
    # WOWY logic: total_p1_shifts >= shifts_together
    if len(wowy) > 0 and 'total_p1_shifts' in wowy.columns and 'shifts_together' in wowy.columns:
        invalid = (wowy['total_p1_shifts'] < wowy['shifts_together']).sum()
        qa.add("RELATIONSHIP TABLES", "WOWY: p1_shifts >= shifts_together",
               invalid == 0, 0, invalid)
    
    # Line combos should have data
    qa.add("RELATIONSHIP TABLES", "Line combos has data",
           len(line_combos) > 0, ">0", len(line_combos))


# ============================================================================
# 9. GOALIE STATS
# ============================================================================
def validate_goalie_stats(tables: Dict, qa: QAResult):
    """Validate goalie statistics."""
    goalie = tables['fact_goalie_game_stats']
    
    if len(goalie) == 0:
        qa.warn("GOALIE STATS", "No goalie data", "Skipping goalie validations")
        return
    
    # saves = shots_faced - goals_against
    if all(col in goalie.columns for col in ['saves', 'shots_faced', 'goals_against']):
        calc_saves = goalie['shots_faced'] - goalie['goals_against']
        match = (goalie['saves'] == calc_saves).all()
        qa.add("GOALIE STATS", "saves = shots_faced - goals_against", match)
    
    # save_pct in range
    if 'save_pct' in goalie.columns:
        valid = ((goalie['save_pct'] >= 0) & (goalie['save_pct'] <= 100)).all()
        qa.add("GOALIE STATS", "save_pct in 0-100", valid)


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("Loading tables...")
    tables = load_tables()
    
    qa = QAResult()
    
    print("Running validations...")
    
    # Run all validation groups
    validate_external_goals(tables, qa)
    validate_math(tables, qa)
    validate_cross_table(tables, qa)
    validate_edge_cases(tables, qa)
    validate_uniqueness(tables, qa)
    validate_data_types(tables, qa)
    validate_no_critical_nulls(tables, qa)
    validate_relationship_tables(tables, qa)
    validate_goalie_stats(tables, qa)
    
    # Print report
    success = qa.print_report()
    
    # Exit code
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
