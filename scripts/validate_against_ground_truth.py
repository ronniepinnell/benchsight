#!/usr/bin/env python3
"""
BenchSight Ground Truth Validation Framework
=============================================

This script validates ETL output against TWO authoritative ground truth sources:

1. dim_schedule - Official game scores from noradhockey.com
2. fact_gameroster - Official player stats from BLB league database

VALIDATION APPROACH:
- Every stat that exists in ground truth is validated
- Discrepancies are flagged with severity levels
- A validation report is generated

Author: BenchSight
Date: December 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json

OUTPUT_DIR = Path('data/output')
TRACKED_GAMES = [18969, 18977, 18981, 18987]


class ValidationResult:
    def __init__(self, name, passed, expected, actual, severity='ERROR', details=''):
        self.name = name
        self.passed = passed
        self.expected = expected
        self.actual = actual
        self.severity = severity  # ERROR, WARNING, INFO
        self.details = details
    
    def __repr__(self):
        status = '✅' if self.passed else '❌'
        return f"{status} {self.name}: expected={self.expected}, actual={self.actual}"


class GroundTruthValidator:
    """Validates ETL output against ground truth sources."""
    
    def __init__(self):
        self.results = []
        self.load_data()
    
    def load_data(self):
        """Load all data sources."""
        print("Loading data sources...")
        
        # Ground truth sources
        self.schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
        self.roster_blb = pd.read_csv(OUTPUT_DIR / 'fact_gameroster.csv')
        
        # ETL outputs to validate
        self.player_stats = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
        self.events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv')
        self.team_stats = pd.read_csv(OUTPUT_DIR / 'fact_team_game_stats.csv')
        self.goalie_stats = pd.read_csv(OUTPUT_DIR / 'fact_goalie_game_stats.csv')
        
        # Filter to tracked games
        self.schedule_tracked = self.schedule[self.schedule['game_id'].isin(TRACKED_GAMES)]
        self.roster_tracked = self.roster_blb[self.roster_blb['game_id'].isin(TRACKED_GAMES)]
        self.player_stats_tracked = self.player_stats[self.player_stats['game_id'].isin(TRACKED_GAMES)]
        self.events_tracked = self.events[self.events['game_id'].isin(TRACKED_GAMES)]
        
        print(f"  Schedule: {len(self.schedule_tracked)} games")
        print(f"  Roster: {len(self.roster_tracked)} player-games")
        print(f"  Player Stats: {len(self.player_stats_tracked)} rows")
        print(f"  Events: {len(self.events_tracked)} events")
    
    def validate_game_scores(self):
        """Validate total goals match official scores."""
        print("\n" + "=" * 60)
        print("VALIDATING GAME SCORES (vs noradhockey.com)")
        print("=" * 60)
        
        for game_id in TRACKED_GAMES:
            # Ground truth from schedule
            game = self.schedule[self.schedule['game_id'] == game_id].iloc[0]
            expected_total = int(game['home_total_goals'] + game['away_total_goals'])
            expected_home = int(game['home_total_goals'])
            expected_away = int(game['away_total_goals'])
            home_team = game['home_team_name']
            away_team = game['away_team_name']
            
            # ETL output
            game_stats = self.player_stats[self.player_stats['game_id'] == game_id]
            actual_total = int(game_stats['goals'].sum())
            
            # Team breakdown (need to match players to teams)
            game_roster = self.roster_tracked[self.roster_tracked['game_id'] == game_id]
            
            result = ValidationResult(
                name=f"Game {game_id} Total Goals",
                passed=(expected_total == actual_total),
                expected=expected_total,
                actual=actual_total,
                severity='ERROR' if expected_total != actual_total else 'INFO',
                details=f"{home_team} {expected_home} - {away_team} {expected_away}"
            )
            self.results.append(result)
            print(result)
    
    def validate_player_goals(self):
        """Validate individual player goals match BLB."""
        print("\n" + "=" * 60)
        print("VALIDATING PLAYER GOALS (vs BLB roster)")
        print("=" * 60)
        
        mismatches = []
        matches = 0
        
        for game_id in TRACKED_GAMES:
            # Ground truth from BLB roster
            blb_game = self.roster_tracked[self.roster_tracked['game_id'] == game_id]
            
            # ETL output
            etl_game = self.player_stats_tracked[self.player_stats_tracked['game_id'] == game_id]
            
            for _, blb_row in blb_game.iterrows():
                player_id = blb_row['player_id']
                expected_goals = int(blb_row['goals']) if pd.notna(blb_row['goals']) else 0
                
                etl_row = etl_game[etl_game['player_id'] == player_id]
                if len(etl_row) > 0:
                    actual_goals = int(etl_row['goals'].iloc[0])
                else:
                    actual_goals = 0  # Player not in ETL output
                
                if expected_goals != actual_goals:
                    mismatches.append({
                        'game_id': game_id,
                        'player': blb_row.get('player_full_name', player_id),
                        'expected': expected_goals,
                        'actual': actual_goals,
                    })
                else:
                    matches += 1
        
        result = ValidationResult(
            name="Player Goals Match BLB",
            passed=(len(mismatches) == 0),
            expected=f"{matches + len(mismatches)} players",
            actual=f"{matches} match, {len(mismatches)} mismatch",
            severity='ERROR' if len(mismatches) > 0 else 'INFO'
        )
        self.results.append(result)
        print(result)
        
        if mismatches:
            print("  Mismatches:")
            for m in mismatches[:10]:
                print(f"    Game {m['game_id']}: {m['player']} expected={m['expected']}, actual={m['actual']}")
    
    def validate_player_assists(self):
        """Validate individual player assists match BLB."""
        print("\n" + "=" * 60)
        print("VALIDATING PLAYER ASSISTS (vs BLB roster)")
        print("=" * 60)
        
        mismatches = []
        matches = 0
        
        for game_id in TRACKED_GAMES:
            blb_game = self.roster_tracked[self.roster_tracked['game_id'] == game_id]
            etl_game = self.player_stats_tracked[self.player_stats_tracked['game_id'] == game_id]
            
            for _, blb_row in blb_game.iterrows():
                player_id = blb_row['player_id']
                expected = int(blb_row['assist']) if pd.notna(blb_row['assist']) else 0
                
                etl_row = etl_game[etl_game['player_id'] == player_id]
                if len(etl_row) > 0 and 'assists' in etl_row.columns:
                    actual = int(etl_row['assists'].iloc[0])
                else:
                    actual = 0
                
                if expected != actual:
                    mismatches.append({
                        'game_id': game_id,
                        'player': blb_row.get('player_full_name', player_id),
                        'expected': expected,
                        'actual': actual,
                    })
                else:
                    matches += 1
        
        result = ValidationResult(
            name="Player Assists Match BLB",
            passed=(len(mismatches) == 0),
            expected=f"{matches + len(mismatches)} players",
            actual=f"{matches} match, {len(mismatches)} mismatch",
            severity='ERROR' if len(mismatches) > 0 else 'INFO'
        )
        self.results.append(result)
        print(result)
        
        if mismatches:
            print("  Mismatches:")
            for m in mismatches[:10]:
                print(f"    Game {m['game_id']}: {m['player']} expected={m['expected']}, actual={m['actual']}")
    
    def validate_internal_consistency(self):
        """Validate internal consistency of stats."""
        print("\n" + "=" * 60)
        print("VALIDATING INTERNAL CONSISTENCY")
        print("=" * 60)
        
        # Points = Goals + Assists
        if 'points' in self.player_stats.columns:
            calculated = self.player_stats['goals'] + self.player_stats['assists']
            actual = self.player_stats['points']
            mismatches = (calculated != actual).sum()
            
            result = ValidationResult(
                name="Points = Goals + Assists",
                passed=(mismatches == 0),
                expected="All rows match",
                actual=f"{mismatches} mismatches",
                severity='ERROR' if mismatches > 0 else 'INFO'
            )
            self.results.append(result)
            print(result)
        
        # Zone entry control % ≤ 100
        if 'zone_entry_control_pct' in self.player_stats.columns:
            over_100 = (self.player_stats['zone_entry_control_pct'] > 100).sum()
            
            result = ValidationResult(
                name="Zone Entry Control % ≤ 100",
                passed=(over_100 == 0),
                expected="0 rows > 100%",
                actual=f"{over_100} rows > 100%",
                severity='ERROR' if over_100 > 0 else 'INFO'
            )
            self.results.append(result)
            print(result)
        
        # Logical shifts are reasonable (5-20 per game)
        if 'logical_shifts' in self.player_stats.columns:
            unreasonable = ((self.player_stats['logical_shifts'] < 3) | 
                           (self.player_stats['logical_shifts'] > 25)).sum()
            
            # Exclude goalies who may have different shift patterns
            result = ValidationResult(
                name="Logical Shifts Reasonable (3-25)",
                passed=(unreasonable <= 5),  # Allow some outliers
                expected="Most players 3-25 shifts",
                actual=f"{unreasonable} outliers",
                severity='WARNING' if unreasonable > 5 else 'INFO'
            )
            self.results.append(result)
            print(result)
        
        # TOI > 0 for non-zero shift players
        if all(c in self.player_stats.columns for c in ['toi_seconds', 'logical_shifts']):
            zero_toi = self.player_stats[
                (self.player_stats['logical_shifts'] > 0) & 
                (self.player_stats['toi_seconds'] == 0)
            ]
            
            result = ValidationResult(
                name="Players with shifts have TOI",
                passed=(len(zero_toi) == 0),
                expected="0 violations",
                actual=f"{len(zero_toi)} violations",
                severity='ERROR' if len(zero_toi) > 0 else 'INFO'
            )
            self.results.append(result)
            print(result)
    
    def validate_event_player_counts(self):
        """Validate event counts are reasonable."""
        print("\n" + "=" * 60)
        print("VALIDATING EVENT COUNTS")
        print("=" * 60)
        
        events_per_game = self.events_tracked.groupby('game_id').size()
        
        # Events per game should be 500-3000 for detailed tracking
        for game_id in TRACKED_GAMES:
            count = events_per_game.get(game_id, 0)
            reasonable = 300 <= count <= 3000
            
            result = ValidationResult(
                name=f"Game {game_id} Event Count",
                passed=reasonable,
                expected="300-3000 events",
                actual=f"{count} events",
                severity='WARNING' if not reasonable else 'INFO'
            )
            self.results.append(result)
            print(result)
    
    def validate_goalie_stats(self):
        """Validate goalie stats."""
        print("\n" + "=" * 60)
        print("VALIDATING GOALIE STATS")
        print("=" * 60)
        
        # 2 goalies per game
        goalies_per_game = self.goalie_stats.groupby('game_id').size()
        
        for game_id in TRACKED_GAMES:
            count = goalies_per_game.get(game_id, 0)
            
            result = ValidationResult(
                name=f"Game {game_id} Goalie Count",
                passed=(count == 2),
                expected=2,
                actual=count,
                severity='ERROR' if count != 2 else 'INFO'
            )
            self.results.append(result)
            print(result)
        
        # Save % reasonable (70-100%)
        if 'save_pct' in self.goalie_stats.columns:
            unreasonable = (
                (self.goalie_stats['save_pct'] < 70) | 
                (self.goalie_stats['save_pct'] > 100)
            ).sum()
            
            result = ValidationResult(
                name="Goalie Save % Reasonable (70-100)",
                passed=(unreasonable == 0),
                expected="All 70-100%",
                actual=f"{unreasonable} outliers",
                severity='WARNING' if unreasonable > 0 else 'INFO'
            )
            self.results.append(result)
            print(result)
    
    def validate_primary_actor_rule(self):
        """Validate that stats are only counted for primary actor."""
        print("\n" + "=" * 60)
        print("VALIDATING PRIMARY ACTOR RULE")
        print("=" * 60)
        
        # Spot check: zone entries should be reasonable (0-15 per player per game)
        if 'zone_entries' in self.player_stats.columns:
            high_entries = self.player_stats[self.player_stats['zone_entries'] > 20]
            
            result = ValidationResult(
                name="Zone Entries per Player Reasonable",
                passed=(len(high_entries) == 0),
                expected="All ≤ 20 per game",
                actual=f"{len(high_entries)} players > 20",
                severity='WARNING' if len(high_entries) > 0 else 'INFO'
            )
            self.results.append(result)
            print(result)
        
        # Shot counts reasonable (0-30 per player per game)
        if 'shots' in self.player_stats.columns:
            high_shots = self.player_stats[self.player_stats['shots'] > 30]
            
            result = ValidationResult(
                name="Shots per Player Reasonable",
                passed=(len(high_shots) == 0),
                expected="All ≤ 30 per game",
                actual=f"{len(high_shots)} players > 30",
                severity='WARNING' if len(high_shots) > 0 else 'INFO'
            )
            self.results.append(result)
            print(result)
    
    def generate_report(self):
        """Generate validation report."""
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        errors = sum(1 for r in self.results if not r.passed and r.severity == 'ERROR')
        warnings = sum(1 for r in self.results if not r.passed and r.severity == 'WARNING')
        
        print(f"\nTotal Checks: {len(self.results)}")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"      Errors: {errors}")
        print(f"      Warnings: {warnings}")
        
        pass_rate = passed / len(self.results) * 100 if self.results else 0
        print(f"\nPass Rate: {pass_rate:.1f}%")
        
        if errors > 0:
            print("\n⚠️  CRITICAL: There are validation ERRORS that need attention!")
        
        # Save report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': len(self.results),
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'warnings': warnings,
                'pass_rate': float(pass_rate),
            },
            'results': [
                {
                    'name': r.name,
                    'passed': bool(r.passed),
                    'expected': str(r.expected),
                    'actual': str(r.actual),
                    'severity': r.severity,
                    'details': r.details,
                }
                for r in self.results
            ]
        }
        
        report_path = OUTPUT_DIR / 'VALIDATION_REPORT.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to: {report_path}")
        
        return report
    
    def run_all_validations(self):
        """Run all validations."""
        print("=" * 60)
        print("BENCHSIGHT GROUND TRUTH VALIDATION")
        print("=" * 60)
        print(f"Validating against {len(TRACKED_GAMES)} tracked games")
        print(f"Ground Truth Sources:")
        print("  1. dim_schedule (noradhockey.com official scores)")
        print("  2. fact_gameroster (BLB league database)")
        
        self.validate_game_scores()
        self.validate_player_goals()
        self.validate_player_assists()
        self.validate_internal_consistency()
        self.validate_event_player_counts()
        self.validate_goalie_stats()
        self.validate_primary_actor_rule()
        
        return self.generate_report()


def main():
    validator = GroundTruthValidator()
    report = validator.run_all_validations()
    
    # Return exit code based on errors
    errors = report['summary']['errors']
    return 1 if errors > 0 else 0


if __name__ == '__main__':
    exit(main())
