#!/usr/bin/env python3
"""
================================================================================
BENCHSIGHT VALIDATION
================================================================================
Validates ETL output, data integrity, and project structure.

USAGE:
    python validate.py              # Full validation
    python validate.py --quick      # Quick check (counts only)
    python validate.py --tables     # Validate table structure
    python validate.py --data       # Validate data integrity
    python validate.py --goals      # Validate goal counts
    python validate.py --manifest   # Comprehensive table verification (manifest-based)
    python validate.py --full       # Run all checks including comprehensive verification

================================================================================
Version: 22.0
Updated: 2026-01-22
================================================================================
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('validate')


# =============================================================================
# EXPECTED VALUES (Ground Truth)
# =============================================================================
EXPECTED = {
    'tables': 145,
    'dim_tables': 57,
    'fact_tables': 83,
    'qa_tables': 4,
    'lookup_tables': 1,
    'goals': 17,
    'goals_tracked': 16,  # Due to raw data issue
    'games': [18969, 18977, 18981, 18987],
    'goal_rule': "event_type='Goal' AND event_detail='Goal_Scored'"
}


class Validator:
    """BenchSight data validator."""
    
    def __init__(self, base_dir: Path = None):
        if base_dir is None:
            base_dir = Path(__file__).parent
        self.base_dir = base_dir
        self.data_dir = base_dir / 'data' / 'output'
        self.errors = []
        self.warnings = []
        self.passed = 0
        self.failed = 0
    
    def check(self, condition: bool, message: str, critical: bool = True):
        """Record a check result."""
        if condition:
            self.passed += 1
            print(f"  ✓ {message}")
        else:
            self.failed += 1
            if critical:
                self.errors.append(message)
                print(f"  ✗ {message}")
            else:
                self.warnings.append(message)
                print(f"  ⚠ {message}")
        return condition
    
    def validate_table_counts(self) -> bool:
        """Validate expected number of tables exist."""
        print("\n[TABLE COUNTS]")
        
        csv_files = list(self.data_dir.glob('*.csv'))
        total = len(csv_files)
        dims = len([f for f in csv_files if f.stem.startswith('dim_')])
        facts = len([f for f in csv_files if f.stem.startswith('fact_')])
        qas = len([f for f in csv_files if f.stem.startswith('qa_')])
        
        self.check(total >= EXPECTED['tables'], 
                   f"Total tables: {total} (expected {EXPECTED['tables']})")
        self.check(dims >= EXPECTED['dim_tables'], 
                   f"Dim tables: {dims} (expected {EXPECTED['dim_tables']})", critical=False)
        self.check(facts >= EXPECTED['fact_tables'], 
                   f"Fact tables: {facts} (expected {EXPECTED['fact_tables']})", critical=False)
        
        return self.failed == 0
    
    def validate_goals(self) -> bool:
        """Validate goal counts using correct rule."""
        print("\n[GOAL VALIDATION]")
        print(f"  Rule: {EXPECTED['goal_rule']}")
        
        events_path = self.data_dir / 'fact_events.csv'
        if not events_path.exists():
            self.check(False, "fact_events.csv not found")
            return False
        
        df = pd.read_csv(events_path)
        
        # Normalize column names
        df.columns = [c.lower().strip() for c in df.columns]
        
        # Count goals using CORRECT rule
        goals_mask = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')
        goal_count = goals_mask.sum()
        
        self.check(goal_count >= EXPECTED['goals_tracked'],
                   f"Goals found: {goal_count} (expected {EXPECTED['goals_tracked']}+)")
        
        # Check for common mistakes
        if 'shot_goal' in df['event_detail'].str.lower().values:
            shot_goals = (df['event_detail'].str.lower() == 'shot_goal').sum()
            print(f"  ⚠ Found {shot_goals} Shot_Goal events (these are shots, not goals)")
        
        # Goals by game
        print("\n  Goals by game:")
        for game_id in EXPECTED['games']:
            game_goals = ((df['game_id'] == game_id) & goals_mask).sum()
            print(f"    Game {game_id}: {game_goals} goals")
        
        return True
    
    def validate_player_stats(self) -> bool:
        """Validate player stats match events."""
        print("\n[PLAYER STATS VALIDATION]")
        
        stats_path = self.data_dir / 'fact_player_game_stats.csv'
        events_path = self.data_dir / 'fact_events.csv'
        
        if not stats_path.exists():
            self.check(False, "fact_player_game_stats.csv not found")
            return False
        
        stats_df = pd.read_csv(stats_path)
        events_df = pd.read_csv(events_path)
        
        # Normalize columns
        stats_df.columns = [c.lower().strip() for c in stats_df.columns]
        events_df.columns = [c.lower().strip() for c in events_df.columns]
        
        # Total goals in stats
        if 'goals' in stats_df.columns:
            stats_goals = stats_df['goals'].sum()
            
            # Total goals in events
            events_goals = ((events_df['event_type'] == 'Goal') & 
                           (events_df['event_detail'] == 'Goal_Scored')).sum()
            
            self.check(stats_goals == events_goals,
                       f"Stats goals ({stats_goals}) matches events ({events_goals})")
        else:
            self.check(False, "'goals' column not found in player stats")
        
        return True
    
    def validate_foreign_keys(self) -> bool:
        """Validate foreign key relationships."""
        print("\n[FOREIGN KEY VALIDATION]")
        
        # Check dim_player exists and has data
        dim_player_path = self.data_dir / 'dim_player.csv'
        if not dim_player_path.exists():
            self.check(False, "dim_player.csv not found")
            return False
        
        dim_player = pd.read_csv(dim_player_path)
        dim_player.columns = [c.lower().strip() for c in dim_player.columns]
        
        self.check(len(dim_player) > 0, f"dim_player has {len(dim_player)} rows")
        
        # Check fact_events references valid players
        events_path = self.data_dir / 'fact_events.csv'
        if events_path.exists():
            events = pd.read_csv(events_path)
            events.columns = [c.lower().strip() for c in events.columns]
            
            if 'player_id' in events.columns and 'player_id' in dim_player.columns:
                valid_players = set(dim_player['player_id'].dropna())
                event_players = set(events['player_id'].dropna())
                orphans = event_players - valid_players - {0, -1}  # Exclude null markers
                
                self.check(len(orphans) == 0,
                           f"All event player_ids valid ({len(orphans)} orphans)", critical=False)
        
        return True
    
    def validate_required_columns(self) -> bool:
        """Validate key tables have required columns."""
        print("\n[REQUIRED COLUMNS]")
        
        required = {
            'fact_events': ['event_id', 'game_id', 'event_type', 'event_detail', 'period'],
            'fact_player_game_stats': ['player_game_key', 'player_id', 'game_id', 'goals', 'assists'],
            'dim_player': ['player_id', 'player_full_name'],
            'dim_schedule': ['game_id', 'date', 'home_team_name', 'away_team_name'],
        }
        
        for table, columns in required.items():
            path = self.data_dir / f'{table}.csv'
            if not path.exists():
                self.check(False, f"{table}.csv exists")
                continue
            
            df = pd.read_csv(path, nrows=1)
            df.columns = [c.lower().strip() for c in df.columns]
            
            missing = [c for c in columns if c not in df.columns]
            self.check(len(missing) == 0,
                       f"{table} has required columns (missing: {missing})" if missing 
                       else f"{table} has all required columns")
        
        return True
    
    def quick_check(self) -> bool:
        """Quick sanity check - just counts."""
        print("\n[QUICK CHECK]")
        
        csv_files = list(self.data_dir.glob('*.csv'))
        print(f"  Tables: {len(csv_files)}")
        
        events_path = self.data_dir / 'fact_events.csv'
        if events_path.exists():
            df = pd.read_csv(events_path)
            df.columns = [c.lower().strip() for c in df.columns]
            goals = ((df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')).sum()
            print(f"  Goals: {goals}")
            games = df['game_id'].nunique()
            print(f"  Games: {games}")
        
        return True
    
    def run_all(self) -> bool:
        """Run all validations."""
        self.validate_table_counts()
        self.validate_goals()
        self.validate_player_stats()
        self.validate_foreign_keys()
        self.validate_required_columns()
        return self.failed == 0


def run_comprehensive_verification():
    """Run comprehensive table verification using manifest."""
    from src.validation import TableVerifier

    print("\n[COMPREHENSIVE TABLE VERIFICATION]")
    print("Using manifest: config/table_manifest.json")

    try:
        verifier = TableVerifier()
        result = verifier.verify_all()
        result.add(verifier.check_goal_counts())

        print(result.summary())
        return result.passed
    except FileNotFoundError as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Validate BenchSight ETL output',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--quick', action='store_true',
                        help='Quick check (counts only)')
    parser.add_argument('--tables', action='store_true',
                        help='Validate table counts')
    parser.add_argument('--goals', action='store_true',
                        help='Validate goal counts')
    parser.add_argument('--data', action='store_true',
                        help='Validate data integrity')
    parser.add_argument('--manifest', action='store_true',
                        help='Comprehensive table verification (manifest-based)')
    parser.add_argument('--full', action='store_true',
                        help='Run all checks including comprehensive verification')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    print("=" * 60)
    print("BENCHSIGHT VALIDATION")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Comprehensive manifest-based verification
    if args.manifest:
        passed = run_comprehensive_verification()
        sys.exit(0 if passed else 1)

    validator = Validator()

    if args.quick:
        validator.quick_check()
    elif args.tables:
        validator.validate_table_counts()
    elif args.goals:
        validator.validate_goals()
    elif args.data:
        validator.validate_player_stats()
        validator.validate_foreign_keys()
    elif args.full:
        # Run legacy validation + comprehensive verification
        validator.run_all()
        comprehensive_passed = run_comprehensive_verification()
        if not comprehensive_passed:
            validator.failed += 1
    else:
        # Run legacy validation
        validator.run_all()

    # Summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Passed:   {validator.passed}")
    print(f"Failed:   {validator.failed}")
    print(f"Warnings: {len(validator.warnings)}")

    if validator.errors:
        print(f"\nCritical Errors:")
        for err in validator.errors:
            print(f"  ✗ {err}")

    if validator.warnings:
        print(f"\nWarnings:")
        for warn in validator.warnings:
            print(f"  ⚠ {warn}")

    print()
    if validator.failed == 0:
        print("✓ All validations passed!")
        sys.exit(0)
    else:
        print(f"✗ {validator.failed} validation(s) failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
