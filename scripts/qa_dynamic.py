#!/usr/bin/env python3
"""
BenchSight Dynamic QA Suite
============================
Scalable validation that grows with data.

Features:
1. Dynamic game verification from dim_schedule (no hardcoding)
2. Outlier detection with configurable thresholds
3. Aggregation validation (player stats → team → game)
4. Suspicious stats logging to CSV
5. Historical comparison for regression detection

Run: python scripts/qa_dynamic.py
Output: data/output/qa_suspicious_stats.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

OUTPUT_DIR = Path('data/output')
QA_LOG_FILE = OUTPUT_DIR / 'qa_suspicious_stats.csv'

# ============================================================================
# CONFIGURATION - Thresholds for outlier detection
# ============================================================================
THRESHOLDS = {
    # Per-game thresholds for SKATERS (flag if exceeded)
    'goals_per_game': 5,           # Flag player with >5 goals in one game
    'assists_per_game': 6,         # Flag player with >6 assists in one game
    'toi_max_seconds_skater': 2400, # Flag skater if TOI > 40 minutes
    'toi_max_seconds_goalie': 3600, # Flag goalie if TOI > 60 minutes (full game)
    'toi_min_seconds': 60,          # Flag if TOI < 1 minute (data issue?)
    'plus_minus_extreme': 6,        # Flag if +/- > +6 or < -6
    'shots_per_game': 20,           # Flag if >20 shots
    'cf_pct_extreme_low': 15,       # Flag if CF% < 15%
    'cf_pct_extreme_high': 85,      # Flag if CF% > 85%
    
    # Aggregation tolerance (% difference allowed)
    'agg_tolerance_pct': 5,        # Allow 5% variance in aggregations
    
    # Statistical thresholds
    'zscore_threshold': 3,         # Flag values > 3 standard deviations
}

# Goalie identifiers (positions that play full game)
GOALIE_POSITIONS = ['Goalie', 'G', 'goalie']

# Known data issues - cleared when source data is fixed
KNOWN_ISSUES = {
    # 18977 was fixed - Galen Wood now correctly credited as scorer on event 1368
}


class SuspiciousStatsLog:
    """Track and log suspicious statistics for review."""
    
    def __init__(self):
        self.entries = []
    
    def add(self, game_id: int, category: str, stat: str, 
            player_id: str = None, player_name: str = None,
            value: float = None, expected: float = None,
            severity: str = 'WARNING', note: str = None):
        self.entries.append({
            'timestamp': datetime.now().isoformat(),
            'game_id': game_id,
            'player_id': player_id,
            'player_name': player_name,
            'category': category,
            'stat': stat,
            'value': value,
            'expected': expected,
            'severity': severity,
            'note': note,
            'resolved': False
        })
    
    def save(self, path: Path = QA_LOG_FILE):
        if self.entries:
            df = pd.DataFrame(self.entries)
            # Append to existing log if it exists
            if path.exists():
                existing = pd.read_csv(path)
                df = pd.concat([existing, df], ignore_index=True)
            df.to_csv(path, index=False)
            print(f"\n📋 Suspicious stats logged to: {path}")
            return len(self.entries)
        return 0
    
    def summary(self):
        if not self.entries:
            return "No suspicious stats detected."
        
        by_severity = {}
        for e in self.entries:
            sev = e['severity']
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        return f"Suspicious stats: " + ", ".join(f"{k}: {v}" for k, v in by_severity.items())


class DynamicQA:
    """Dynamic QA that scales with data."""
    
    def __init__(self):
        self.tables = {}
        self.schedule = None
        self.log = SuspiciousStatsLog()
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def load_tables(self):
        """Load all required tables."""
        required = [
            'fact_player_game_stats',
            'fact_shifts_player',
            'fact_events_player',
            'fact_events',
            'fact_team_game_stats',
            'fact_goalie_game_stats',
            'dim_player',
            'dim_schedule',
        ]
        
        for table in required:
            path = OUTPUT_DIR / f'{table}.csv'
            if path.exists():
                self.tables[table] = pd.read_csv(path)
            else:
                self.tables[table] = pd.DataFrame()
        
        self.schedule = self.tables.get('dim_schedule', pd.DataFrame())
        return len(self.tables)
    
    def get_official_score(self, game_id: int) -> Optional[Tuple[int, int, int]]:
        """Get official score from dim_schedule."""
        if self.schedule is None or len(self.schedule) == 0:
            return None
        
        game = self.schedule[self.schedule['game_id'] == game_id]
        if len(game) == 0:
            return None
        
        row = game.iloc[0]
        home = int(row['home_total_goals']) if pd.notna(row['home_total_goals']) else 0
        away = int(row['away_total_goals']) if pd.notna(row['away_total_goals']) else 0
        return (home, away, home + away)
    
    def validate_goals_vs_schedule(self):
        """Validate goal counts against dim_schedule (official source)."""
        print("\n" + "=" * 70)
        print("GOAL VERIFICATION (vs dim_schedule)")
        print("=" * 70)
        
        pgs = self.tables['fact_player_game_stats']
        loaded_games = pgs['game_id'].unique()
        
        for game_id in sorted(loaded_games):
            game = pgs[pgs['game_id'] == game_id]
            our_goals = int(game['goals'].sum())
            
            official = self.get_official_score(game_id)
            if official is None:
                print(f"  ⚠️ Game {game_id}: Not in dim_schedule")
                self.warnings += 1
                continue
            
            home, away, expected = official
            diff = abs(our_goals - expected)
            
            # Check if this is a known issue
            if game_id in KNOWN_ISSUES:
                known = KNOWN_ISSUES[game_id]
                if diff <= known['expected_diff']:
                    print(f"  ⚠️ Game {game_id}: {our_goals}/{expected} goals (KNOWN: {known['issue']})")
                    self.warnings += 1
                    continue
            
            if diff == 0:
                print(f"  ✅ Game {game_id}: {our_goals} goals ✓")
                self.passed += 1
            else:
                print(f"  ❌ Game {game_id}: {our_goals} goals (expected {expected}, diff={diff})")
                self.failed += 1
                self.log.add(
                    game_id=game_id,
                    category='GOAL_MISMATCH',
                    stat='total_goals',
                    value=our_goals,
                    expected=expected,
                    severity='CRITICAL',
                    note=f"Difference of {diff} goals vs official score"
                )
    
    def validate_aggregations(self):
        """Validate player stats sum to team/game totals."""
        print("\n" + "=" * 70)
        print("AGGREGATION VALIDATION (Player → Team → Game)")
        print("=" * 70)
        
        pgs = self.tables['fact_player_game_stats']
        team_stats = self.tables.get('fact_team_game_stats', pd.DataFrame())
        
        for game_id in sorted(pgs['game_id'].unique()):
            game = pgs[pgs['game_id'] == game_id]
            
            # Sum player goals
            player_goals = int(game['goals'].sum())
            player_assists = int(game['assists'].sum())
            player_shots = int(game['shots'].sum())
            
            # Get team stats if available
            if len(team_stats) > 0:
                game_team = team_stats[team_stats['game_id'] == game_id]
                if len(game_team) > 0:
                    team_goals = int(game_team['goals'].sum())
                    
                    if player_goals != team_goals:
                        self.log.add(
                            game_id=game_id,
                            category='AGGREGATION',
                            stat='goals',
                            value=player_goals,
                            expected=team_goals,
                            severity='WARNING',
                            note=f"Player sum ({player_goals}) != Team sum ({team_goals})"
                        )
            
            # Validate internal consistency
            for _, row in game.iterrows():
                # Points should equal goals + assists
                if row['points'] != row['goals'] + row['assists']:
                    self.log.add(
                        game_id=game_id,
                        player_id=row['player_id'],
                        player_name=row.get('player_name'),
                        category='MATH_ERROR',
                        stat='points',
                        value=row['points'],
                        expected=row['goals'] + row['assists'],
                        severity='ERROR'
                    )
        
        print(f"  Checked {len(pgs['game_id'].unique())} games for aggregation consistency")
        self.passed += 1
    
    def detect_outliers(self):
        """Detect statistical outliers using thresholds and z-scores."""
        print("\n" + "=" * 70)
        print("OUTLIER DETECTION")
        print("=" * 70)
        
        pgs = self.tables['fact_player_game_stats']
        players = self.tables.get('dim_player', pd.DataFrame())
        
        # Build position lookup
        position_lookup = {}
        if len(players) > 0 and 'player_id' in players.columns:
            for _, p in players.iterrows():
                pos = p.get('player_primary_position', '')
                position_lookup[p['player_id']] = pos
        
        outlier_count = 0
        
        for _, row in pgs.iterrows():
            game_id = row['game_id']
            player_id = row.get('player_id')
            player_name = row.get('player_name', 'Unknown')
            
            # Determine if goalie
            position = position_lookup.get(player_id, '')
            is_goalie = position in GOALIE_POSITIONS
            
            # Use appropriate TOI threshold
            toi_max = THRESHOLDS['toi_max_seconds_goalie'] if is_goalie else THRESHOLDS['toi_max_seconds_skater']
            
            # Check absolute thresholds
            checks = [
                ('goals', row['goals'], THRESHOLDS['goals_per_game'], '>'),
                ('assists', row['assists'], THRESHOLDS['assists_per_game'], '>'),
                ('toi_seconds', row['toi_seconds'], toi_max, '>'),
                ('toi_seconds', row['toi_seconds'], THRESHOLDS['toi_min_seconds'], '<'),
                ('shots', row.get('shots', 0), THRESHOLDS['shots_per_game'], '>'),
                ('cf_pct', row.get('cf_pct', 50), THRESHOLDS['cf_pct_extreme_low'], '<'),
                ('cf_pct', row.get('cf_pct', 50), THRESHOLDS['cf_pct_extreme_high'], '>'),
            ]
            
            for stat, value, threshold, direction in checks:
                if pd.isna(value):
                    continue
                
                is_outlier = (direction == '>' and value > threshold) or \
                             (direction == '<' and value < threshold)
                
                if is_outlier:
                    outlier_count += 1
                    self.log.add(
                        game_id=game_id,
                        player_id=player_id,
                        player_name=player_name,
                        category='OUTLIER',
                        stat=stat,
                        value=value,
                        expected=f"{direction}{threshold}",
                        severity='WARNING',
                        note=f"Value {value} exceeds threshold ({direction}{threshold})"
                    )
            
            # Check plus/minus extremes
            for pm_col in ['plus_minus_ev', 'plus_minus_total']:
                if pm_col in row and pd.notna(row[pm_col]):
                    pm = row[pm_col]
                    if abs(pm) > THRESHOLDS['plus_minus_extreme']:
                        outlier_count += 1
                        self.log.add(
                            game_id=game_id,
                            player_id=player_id,
                            player_name=player_name,
                            category='OUTLIER',
                            stat=pm_col,
                            value=pm,
                            expected=f"±{THRESHOLDS['plus_minus_extreme']}",
                            severity='INFO',
                            note=f"Extreme +/- of {pm}"
                        )
        
        # Z-score analysis for numeric columns
        numeric_cols = ['goals', 'assists', 'toi_seconds', 'shots', 'corsi_for']
        for col in numeric_cols:
            if col in pgs.columns:
                values = pgs[col].dropna()
                if len(values) > 10:  # Need enough data for z-score
                    mean = values.mean()
                    std = values.std()
                    if std > 0:
                        zscores = (values - mean) / std
                        extreme = zscores.abs() > THRESHOLDS['zscore_threshold']
                        extreme_count = extreme.sum()
                        if extreme_count > 0:
                            print(f"  ⚠️ {col}: {extreme_count} values > {THRESHOLDS['zscore_threshold']} std devs")
        
        print(f"  Found {outlier_count} threshold-based outliers")
        if outlier_count > 0:
            self.warnings += outlier_count
    
    def validate_data_integrity(self):
        """Core data integrity checks."""
        print("\n" + "=" * 70)
        print("DATA INTEGRITY")
        print("=" * 70)
        
        pgs = self.tables['fact_player_game_stats']
        
        # No nulls in critical columns
        critical = ['player_id', 'game_id', 'goals', 'assists', 'toi_seconds']
        for col in critical:
            nulls = pgs[col].isna().sum()
            if nulls > 0:
                print(f"  ❌ {col}: {nulls} nulls")
                self.failed += 1
            else:
                print(f"  ✅ {col}: no nulls")
                self.passed += 1
        
        # No duplicates
        dups = pgs.duplicated(subset=['player_id', 'game_id']).sum()
        if dups > 0:
            print(f"  ❌ Duplicate player-game records: {dups}")
            self.failed += 1
        else:
            print(f"  ✅ No duplicate player-game records")
            self.passed += 1
        
        # Percentages in range
        for col in ['cf_pct', 'ff_pct', 'fo_pct']:
            if col in pgs.columns:
                out_of_range = ((pgs[col] < 0) | (pgs[col] > 100)).sum()
                if out_of_range > 0:
                    print(f"  ❌ {col}: {out_of_range} values outside 0-100")
                    self.failed += 1
                else:
                    print(f"  ✅ {col}: all in 0-100 range")
                    self.passed += 1
    
    def validate_cross_table(self):
        """Validate consistency across tables."""
        print("\n" + "=" * 70)
        print("CROSS-TABLE CONSISTENCY")
        print("=" * 70)
        
        pgs = self.tables['fact_player_game_stats']
        players = self.tables['dim_player']
        
        # FK integrity
        player_ids_dim = set(players['player_id'].dropna())
        player_ids_fact = set(pgs['player_id'].dropna())
        orphans = player_ids_fact - player_ids_dim
        
        if len(orphans) > 0:
            print(f"  ❌ Orphan player_ids: {len(orphans)}")
            for pid in list(orphans)[:5]:
                self.log.add(
                    game_id=0,
                    player_id=pid,
                    category='FK_ORPHAN',
                    stat='player_id',
                    severity='ERROR',
                    note=f"Player {pid} not in dim_player"
                )
            self.failed += 1
        else:
            print(f"  ✅ All player_ids exist in dim_player")
            self.passed += 1
    
    def check_incomplete_games(self):
        """Identify games with potential data quality issues."""
        print("\n" + "=" * 70)
        print("INCOMPLETE GAME DETECTION")
        print("=" * 70)
        
        pgs = self.tables['fact_player_game_stats']
        events = self.tables['fact_events_player']
        shifts = self.tables['fact_shifts_player']
        
        # Check loaded games
        for game_id in sorted(pgs['game_id'].unique()):
            issues = []
            
            game_stats = pgs[pgs['game_id'] == game_id]
            game_events = events[events['game_id'] == game_id] if len(events) > 0 else pd.DataFrame()
            game_shifts = shifts[shifts['game_id'] == game_id] if len(shifts) > 0 else pd.DataFrame()
            
            # Check player count (typical game has 20-30 players)
            player_count = len(game_stats)
            if player_count < 15:
                issues.append(f"Low player count ({player_count})")
            
            # Check event count (typical game has 500+ events)
            event_count = len(game_events)
            if event_count < 200:
                issues.append(f"Low event count ({event_count})")
            
            # Check shift count
            shift_count = len(game_shifts)
            if shift_count < 100:
                issues.append(f"Low shift count ({shift_count})")
            
            # Check for missing assists (all zeros might indicate tracking gap)
            total_assists = game_stats['assists'].sum()
            total_goals = game_stats['goals'].sum()
            if total_goals > 2 and total_assists == 0:
                issues.append(f"No assists tracked ({total_goals} goals, 0 assists)")
            
            if issues:
                print(f"  ⚠️ Game {game_id}: {', '.join(issues)}")
                self.log.add(
                    game_id=game_id,
                    category='INCOMPLETE_GAME',
                    stat='data_quality',
                    severity='WARNING',
                    note='; '.join(issues)
                )
                self.warnings += 1
            else:
                print(f"  ✅ Game {game_id}: Complete")
                self.passed += 1
        
        # Check for untracked games in schedule that have tracking folders
        self.check_untracked_games()
    
    def check_untracked_games(self):
        """Identify games with tracking folders but no actual tracked data."""
        from pathlib import Path
        import os
        
        games_dir = Path('data/raw/games')
        if not games_dir.exists():
            return
        
        pgs = self.tables['fact_player_game_stats']
        loaded_games = set(pgs['game_id'].unique())
        
        print("\n  Untracked Games (have folder but no data):")
        
        for game_folder in sorted(os.listdir(games_dir)):
            try:
                game_id = int(game_folder)
            except ValueError:
                continue
            
            if game_id in loaded_games:
                continue
            
            tracking_file = games_dir / game_folder / f"{game_folder}_tracking.xlsx"
            if tracking_file.exists():
                # Quick check if it's a template or actual data
                try:
                    import pandas as pd
                    events = pd.read_excel(tracking_file, sheet_name='events')
                    player_fill = events['player_id'].notna().sum() / len(events) * 100 if len(events) > 0 else 0
                    
                    if player_fill < 10:
                        # Get game info from schedule
                        game_info = self.schedule[self.schedule['game_id'] == game_id]
                        if len(game_info) > 0:
                            row = game_info.iloc[0]
                            print(f"    📋 Game {game_id}: {row['home_team_name']} vs {row['away_team_name']} - TEMPLATE ONLY ({player_fill:.0f}% tracked)")
                        else:
                            print(f"    📋 Game {game_id}: TEMPLATE ONLY ({player_fill:.0f}% tracked)")
                        
                        self.log.add(
                            game_id=game_id,
                            category='UNTRACKED_GAME',
                            stat='tracking_completeness',
                            value=player_fill,
                            severity='INFO',
                            note='Tracking template exists but not filled in'
                        )
                except Exception:
                    pass
    
    def generate_summary_report(self):
        """Generate final summary."""
        print("\n" + "=" * 70)
        print("QA SUMMARY")
        print("=" * 70)
        print(f"  ✅ Passed:   {self.passed}")
        print(f"  ❌ Failed:   {self.failed}")
        print(f"  ⚠️ Warnings: {self.warnings}")
        print("=" * 70)
        
        # Save suspicious stats log
        entries_saved = self.log.save()
        if entries_saved > 0:
            print(f"\n📋 {entries_saved} suspicious stats logged for review")
            print(f"   Review: {QA_LOG_FILE}")
        
        return self.failed == 0
    
    def run_all(self):
        """Run all validations."""
        print("=" * 70)
        print("BENCHSIGHT DYNAMIC QA SUITE")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        print("\nLoading tables...")
        self.load_tables()
        
        # Run validations
        self.validate_goals_vs_schedule()
        self.validate_aggregations()
        self.detect_outliers()
        self.validate_data_integrity()
        self.validate_cross_table()
        self.check_incomplete_games()
        
        return self.generate_summary_report()


def main():
    qa = DynamicQA()
    success = qa.run_all()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
