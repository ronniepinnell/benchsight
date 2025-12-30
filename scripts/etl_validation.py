#!/usr/bin/env python3
"""
BenchSight ETL Validation & Error Tracking
==========================================

This module provides:
1. Goal/Assist detection from tracking data
2. Validation against noradhockey.com and BLB
3. Error tracking and reporting
4. Dynamic test generation for all games

Author: BenchSight
Date: December 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import json

OUTPUT_DIR = Path('data/output')
RAW_DIR = Path('data/raw/games')


@dataclass
class ValidationError:
    """Represents a validation error or warning."""
    game_id: int
    severity: str  # CRITICAL, ERROR, WARNING, INFO
    category: str  # GOALS, ASSISTS, ROSTER, SHIFTS, etc.
    message: str
    expected: Optional[str] = None
    actual: Optional[str] = None
    player: Optional[str] = None
    
    def to_dict(self):
        return {
            'game_id': self.game_id,
            'severity': self.severity,
            'category': self.category,
            'message': self.message,
            'expected': self.expected,
            'actual': self.actual,
            'player': self.player,
        }


class ETLValidator:
    """Validates ETL output against ground truth sources."""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.load_data()
    
    def load_data(self):
        """Load all data sources."""
        # Ground truth
        self.schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
        self.roster_blb = pd.read_csv(OUTPUT_DIR / 'fact_gameroster.csv')
        
        # ETL outputs
        self.player_stats = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
        self.events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv')
        self.events_player = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv')
        self.goalie_stats = pd.read_csv(OUTPUT_DIR / 'fact_goalie_game_stats.csv')
        
        # Get tracked games
        self.tracked_games = self.player_stats['game_id'].unique().tolist()
    
    def add_error(self, error: ValidationError):
        """Add error to list."""
        self.errors.append(error)
        
        # Print immediately for visibility
        icon = {'CRITICAL': '🚨', 'ERROR': '❌', 'WARNING': '⚠️', 'INFO': 'ℹ️'}.get(error.severity, '•')
        print(f"  {icon} [{error.category}] {error.message}")
    
    def validate_game_goals(self, game_id: int) -> Tuple[int, int]:
        """
        Validate goal count for a game against official score.
        
        Returns: (expected_goals, actual_goals)
        """
        # Get official score from schedule (noradhockey.com)
        game = self.schedule[self.schedule['game_id'] == game_id]
        if len(game) == 0:
            self.add_error(ValidationError(
                game_id=game_id,
                severity='ERROR',
                category='GOALS',
                message=f'Game {game_id} not found in schedule'
            ))
            return (0, 0)
        
        game = game.iloc[0]
        expected = int(game['home_total_goals'] + game['away_total_goals'])
        
        # Get ETL goal count
        game_stats = self.player_stats[self.player_stats['game_id'] == game_id]
        actual = int(game_stats['goals'].sum())
        
        if expected != actual:
            self.add_error(ValidationError(
                game_id=game_id,
                severity='CRITICAL',
                category='GOALS',
                message=f'Goal count mismatch',
                expected=str(expected),
                actual=str(actual)
            ))
        
        return (expected, actual)
    
    def validate_player_goals(self, game_id: int) -> List[Dict]:
        """
        Validate individual player goals against BLB.
        
        Returns: List of mismatches
        """
        mismatches = []
        
        blb_game = self.roster_blb[self.roster_blb['game_id'] == game_id]
        etl_game = self.player_stats[self.player_stats['game_id'] == game_id]
        
        for _, blb_row in blb_game.iterrows():
            player_id = blb_row['player_id']
            player_name = blb_row.get('player_full_name', player_id)
            expected = int(blb_row['goals']) if pd.notna(blb_row['goals']) else 0
            
            etl_row = etl_game[etl_game['player_id'] == player_id]
            actual = int(etl_row['goals'].iloc[0]) if len(etl_row) > 0 else 0
            
            if expected != actual:
                mismatches.append({
                    'player': player_name,
                    'expected': expected,
                    'actual': actual,
                })
                
                # Only add as error if significant (not just off by 1)
                severity = 'ERROR' if abs(expected - actual) > 1 else 'WARNING'
                self.add_error(ValidationError(
                    game_id=game_id,
                    severity=severity,
                    category='PLAYER_GOALS',
                    message=f'Goal mismatch for {player_name}',
                    expected=str(expected),
                    actual=str(actual),
                    player=player_name
                ))
        
        return mismatches
    
    def validate_player_assists(self, game_id: int) -> List[Dict]:
        """
        Validate individual player assists against BLB.
        
        Returns: List of mismatches
        """
        mismatches = []
        
        blb_game = self.roster_blb[self.roster_blb['game_id'] == game_id]
        etl_game = self.player_stats[self.player_stats['game_id'] == game_id]
        
        for _, blb_row in blb_game.iterrows():
            player_id = blb_row['player_id']
            player_name = blb_row.get('player_full_name', player_id)
            expected = int(blb_row['assist']) if pd.notna(blb_row['assist']) else 0
            
            etl_row = etl_game[etl_game['player_id'] == player_id]
            actual = int(etl_row['assists'].iloc[0]) if len(etl_row) > 0 and 'assists' in etl_row.columns else 0
            
            if expected != actual:
                mismatches.append({
                    'player': player_name,
                    'expected': expected,
                    'actual': actual,
                })
                
                # Assists often have tracking gaps, so use WARNING
                severity = 'WARNING' if expected > actual else 'INFO'
                self.add_error(ValidationError(
                    game_id=game_id,
                    severity=severity,
                    category='PLAYER_ASSISTS',
                    message=f'Assist mismatch for {player_name}',
                    expected=str(expected),
                    actual=str(actual),
                    player=player_name
                ))
        
        return mismatches
    
    def validate_goalie_stats(self, game_id: int):
        """Validate goalie stats for a game."""
        game_goalies = self.goalie_stats[self.goalie_stats['game_id'] == game_id]
        
        if len(game_goalies) != 2:
            self.add_error(ValidationError(
                game_id=game_id,
                severity='ERROR',
                category='GOALIE',
                message=f'Expected 2 goalies, found {len(game_goalies)}'
            ))
        
        # Check for empty net goals (goalie shouldn't be penalized)
        # This requires checking shift data for empty net situations
        # TODO: Implement empty net detection
    
    def detect_empty_net_goals(self, game_id: int) -> List[int]:
        """
        Detect goals scored when opposing goalie was pulled.
        
        Returns: List of event_indices that were empty net goals
        """
        empty_net_goals = []
        
        # Get shifts for this game
        shifts_path = OUTPUT_DIR / 'fact_shifts.csv'
        if not shifts_path.exists():
            return empty_net_goals
        
        shifts = pd.read_csv(shifts_path)
        game_shifts = shifts[shifts['game_id'] == game_id]
        
        # Get goal events
        game_events = self.events[self.events['game_id'] == game_id]
        goals = game_events[game_events['event_type'] == 'Goal']
        
        for _, goal in goals.iterrows():
            shift_index = goal.get('shift_index')
            if pd.isna(shift_index):
                continue
            
            # Check if opposing goalie was on ice during this shift
            shift = game_shifts[game_shifts['shift_index'] == shift_index]
            if len(shift) == 0:
                continue
            
            shift = shift.iloc[0]
            scoring_team = goal.get('team_venue', '')
            
            # If home team scored, check away goalie
            # If away team scored, check home goalie
            if scoring_team == 'home':
                goalie_col = 'away_goalie'
            else:
                goalie_col = 'home_goalie'
            
            if goalie_col in shift and (pd.isna(shift[goalie_col]) or shift[goalie_col] == 0):
                empty_net_goals.append(goal['event_index'])
                self.add_error(ValidationError(
                    game_id=game_id,
                    severity='INFO',
                    category='EMPTY_NET',
                    message=f'Empty net goal detected (event {goal["event_index"]})'
                ))
        
        return empty_net_goals
    
    def validate_all_games(self):
        """Run validation on all tracked games."""
        print("=" * 60)
        print("ETL VALIDATION REPORT")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Games to validate: {self.tracked_games}")
        print()
        
        summary = {
            'games_validated': 0,
            'goals_correct': 0,
            'goals_mismatch': 0,
            'player_goal_errors': 0,
            'player_assist_errors': 0,
            'critical_errors': 0,
            'warnings': 0,
        }
        
        for game_id in self.tracked_games:
            print(f"\n--- Game {game_id} ---")
            summary['games_validated'] += 1
            
            # Validate goals
            expected, actual = self.validate_game_goals(game_id)
            if expected == actual:
                print(f"  ✅ Goals: {actual} (matches official)")
                summary['goals_correct'] += 1
            else:
                summary['goals_mismatch'] += 1
            
            # Validate player goals
            goal_mismatches = self.validate_player_goals(game_id)
            summary['player_goal_errors'] += len(goal_mismatches)
            
            # Validate player assists
            assist_mismatches = self.validate_player_assists(game_id)
            summary['player_assist_errors'] += len(assist_mismatches)
            
            # Validate goalie stats
            self.validate_goalie_stats(game_id)
            
            # Detect empty net goals
            self.detect_empty_net_goals(game_id)
        
        # Count error severities
        summary['critical_errors'] = sum(1 for e in self.errors if e.severity == 'CRITICAL')
        summary['warnings'] = sum(1 for e in self.errors if e.severity == 'WARNING')
        
        return summary
    
    def generate_report(self) -> Dict:
        """Generate validation report."""
        summary = self.validate_all_games()
        
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Games Validated: {summary['games_validated']}")
        print(f"Goals Correct: {summary['goals_correct']}/{summary['games_validated']}")
        print(f"Player Goal Mismatches: {summary['player_goal_errors']}")
        print(f"Player Assist Mismatches: {summary['player_assist_errors']}")
        print(f"Critical Errors: {summary['critical_errors']}")
        print(f"Warnings: {summary['warnings']}")
        
        if summary['critical_errors'] > 0:
            print("\n🚨 CRITICAL ERRORS DETECTED - Review required!")
        
        # Save report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'errors': [e.to_dict() for e in self.errors],
            'tracked_games': self.tracked_games,
        }
        
        report_path = OUTPUT_DIR / 'ETL_VALIDATION_REPORT.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to: {report_path}")
        
        return report


class GoalAssistDetector:
    """
    Detects goals and assists from raw tracking data.
    
    Goal Detection:
    - event_type = 'Goal'
    - event_detail = 'Goal_Scored'
    - Verified by preceding Shot event with event_detail = 'Shot_Goal'
    
    Assist Detection:
    - play_detail1 contains 'AssistPrimary' or 'AssistSecondary'
    - play_detail_2 contains 'AssistSecondary'
    - Linked to Goal event via linked_event_index or same shift
    """
    
    def __init__(self, events_df: pd.DataFrame):
        self.events = events_df
    
    def find_goals(self) -> pd.DataFrame:
        """Find all goals in events data."""
        # Primary method: event_type = 'Goal'
        goals = self.events[self.events['event_type'] == 'Goal'].copy()
        
        # Verify with event_detail
        if 'event_detail' in self.events.columns:
            # Also check for Shot_Goal events
            shot_goals = self.events[self.events['event_detail'] == 'Shot_Goal']
            
            # These should align - if not, flag potential issue
            if len(goals) != len(shot_goals):
                print(f"  ⚠️ Goal event count ({len(goals)}) differs from Shot_Goal count ({len(shot_goals)})")
        
        return goals
    
    def find_assists(self) -> pd.DataFrame:
        """Find all assists in events data."""
        assists = []
        
        # Check play_detail1 for assists
        if 'play_detail1' in self.events.columns:
            primary = self.events[
                self.events['play_detail1'].str.contains('AssistPrimary', na=False, case=False)
            ].copy()
            primary['assist_type'] = 'primary'
            assists.append(primary)
            
            secondary_pd1 = self.events[
                self.events['play_detail1'].str.contains('AssistSecondary', na=False, case=False)
            ].copy()
            secondary_pd1['assist_type'] = 'secondary'
            assists.append(secondary_pd1)
        
        # Check play_detail_2 for secondary assists
        if 'play_detail_2' in self.events.columns:
            secondary_pd2 = self.events[
                self.events['play_detail_2'].str.contains('AssistSecondary', na=False, case=False)
            ].copy()
            secondary_pd2['assist_type'] = 'secondary'
            assists.append(secondary_pd2)
        
        if assists:
            return pd.concat(assists, ignore_index=True)
        return pd.DataFrame()
    
    def get_goal_scorer(self, goal_event: pd.Series) -> Optional[str]:
        """Get the scorer for a goal event."""
        # The scorer is the primary actor (event_team_player_1)
        if 'player_role' in goal_event:
            if goal_event['player_role'] == 'event_team_player_1':
                return goal_event.get('player_id') or goal_event.get('player_game_number')
        return goal_event.get('player_game_number')


def fix_player_game_position():
    """Fix player_game_position to use logical_shifts instead of raw shifts."""
    print("Fixing player_game_position to use logical_shifts...")
    
    pgp = pd.read_csv(OUTPUT_DIR / 'fact_player_game_position.csv')
    
    # Check if already fixed (has logical_shifts column)
    if 'logical_shifts' in pgp.columns and 'total_shifts' not in pgp.columns:
        print("  ✅ Already using logical_shifts")
        return pgp
    
    player_stats = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    
    # Create lookup for logical shifts
    logical_lookup = player_stats.set_index(['game_id', 'player_id'])['logical_shifts'].to_dict()
    
    # Update total_shifts to use logical_shifts
    col_name = 'logical_shifts' if 'logical_shifts' in pgp.columns else 'total_shifts'
    
    for idx, row in pgp.iterrows():
        key = (row['game_id'], row['player_id'])
        logical = logical_lookup.get(key, row.get(col_name, 10))
        
        # Scale position shifts proportionally
        current_total = row.get(col_name, 10) or 10
        if current_total > 0:
            scale = logical / current_total
            pgp.loc[idx, col_name] = int(logical)
            if 'forward_shifts' in pgp.columns:
                pgp.loc[idx, 'forward_shifts'] = int(row.get('forward_shifts', 0) * scale)
            if 'defense_shifts' in pgp.columns:
                pgp.loc[idx, 'defense_shifts'] = int(row.get('defense_shifts', 0) * scale)
            if 'goalie_shifts' in pgp.columns:
                pgp.loc[idx, 'goalie_shifts'] = int(row.get('goalie_shifts', 0) * scale)
    
    # Rename column for clarity if needed
    if 'total_shifts' in pgp.columns:
        pgp = pgp.rename(columns={'total_shifts': 'logical_shifts'})
    
    pgp.to_csv(OUTPUT_DIR / 'fact_player_game_position.csv', index=False)
    print(f"  ✅ Updated fact_player_game_position.csv")
    
    return pgp


def generate_dynamic_tests(tracked_games: List[int]):
    """Generate pytest tests for all tracked games."""
    print("Generating dynamic tests for all games...")
    
    # Load ground truth
    schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
    roster = pd.read_csv(OUTPUT_DIR / 'fact_gameroster.csv')
    
    test_code = '''#!/usr/bin/env python3
"""
BenchSight Dynamic Game Tests
=============================
Auto-generated tests for all tracked games.
Validates against noradhockey.com and BLB.

Generated: {timestamp}
"""

import pytest
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path('data/output')


@pytest.fixture(scope='module')
def schedule():
    return pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')


@pytest.fixture(scope='module')
def roster():
    return pd.read_csv(OUTPUT_DIR / 'fact_gameroster.csv')


@pytest.fixture(scope='module')
def player_stats():
    return pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')


@pytest.fixture(scope='module')
def goalie_stats():
    return pd.read_csv(OUTPUT_DIR / 'fact_goalie_game_stats.csv')


class TestGameScores:
    """Test that all game scores match noradhockey.com official scores."""

'''
    
    # Add parametrized test for each game
    game_params = []
    for game_id in tracked_games:
        game = schedule[schedule['game_id'] == game_id]
        if len(game) > 0:
            game = game.iloc[0]
            total = int(game['home_total_goals'] + game['away_total_goals'])
            home = game['home_team_name']
            away = game['away_team_name']
            game_params.append(f"        ({game_id}, {total}, '{home}', '{away}'),")
    
    test_code += '''    @pytest.mark.parametrize("game_id,expected_goals,home,away", [
{params}
    ])
    def test_game_total_goals(self, player_stats, game_id, expected_goals, home, away):
        """Each game's total goals must match official score from noradhockey.com."""
        actual = int(player_stats[player_stats['game_id'] == game_id]['goals'].sum())
        assert actual == expected_goals, \\
            f"Game {{game_id}} ({{home}} vs {{away}}): ETL={{actual}}, Official={{expected_goals}}"


class TestGoalieStats:
    """Test goalie stats for all games."""

'''.format(params='\n'.join(game_params), timestamp=datetime.now().isoformat())

    # Add goalie tests
    goalie_params = ', '.join(str(g) for g in tracked_games)
    test_code += f'''    @pytest.mark.parametrize("game_id", [{goalie_params}])
    def test_two_goalies_per_game(self, goalie_stats, game_id):
        """Each game must have exactly 2 goalies."""
        count = len(goalie_stats[goalie_stats['game_id'] == game_id])
        assert count == 2, f"Game {{game_id}} has {{count}} goalies, expected 2"


class TestPlayerStats:
    """Test player stat consistency."""

    @pytest.mark.parametrize("game_id", [{goalie_params}])
    def test_player_goals_match_rate(self, roster, player_stats, game_id):
        """At least 90% of player goals should match BLB."""
        blb = roster[roster['game_id'] == game_id]
        etl = player_stats[player_stats['game_id'] == game_id]
        
        matches = 0
        total = 0
        
        for _, row in blb.iterrows():
            expected = int(row['goals']) if pd.notna(row['goals']) else 0
            etl_row = etl[etl['player_id'] == row['player_id']]
            actual = int(etl_row['goals'].iloc[0]) if len(etl_row) > 0 else 0
            
            total += 1
            if expected == actual:
                matches += 1
        
        match_rate = matches / total * 100 if total > 0 else 0
        assert match_rate >= 90, \\
            f"Game {{game_id}}: Only {{match_rate:.1f}}% player goals match BLB"
'''
    
    # Write test file
    test_path = Path('tests/test_dynamic_games.py')
    with open(test_path, 'w') as f:
        f.write(test_code)
    
    print(f"  ✅ Generated {test_path} with tests for {len(tracked_games)} games")
    
    return test_path


def main():
    """Run validation and fixes."""
    print("=" * 60)
    print("BENCHSIGHT ETL VALIDATION & ERROR TRACKING")
    print("=" * 60)
    
    # Fix player_game_position
    fix_player_game_position()
    
    # Run validation
    validator = ETLValidator()
    report = validator.generate_report()
    
    # Generate dynamic tests
    generate_dynamic_tests(validator.tracked_games)
    
    # Return exit code based on critical errors
    return 1 if report['summary']['critical_errors'] > 0 else 0


if __name__ == '__main__':
    exit(main())
