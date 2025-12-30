#!/usr/bin/env python3
"""
BenchSight Ground Truth Test Suite
===================================

These tests validate ETL output against authoritative ground truth:
- dim_schedule (noradhockey.com official scores)
- fact_gameroster (BLB league database)

Run with: pytest tests/test_ground_truth.py -v
"""

import pytest
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path('data/output')
TRACKED_GAMES = [18969, 18977, 18981, 18987]


@pytest.fixture(scope='module')
def schedule():
    return pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')


@pytest.fixture(scope='module')
def roster_blb():
    return pd.read_csv(OUTPUT_DIR / 'fact_gameroster.csv')


@pytest.fixture(scope='module')
def player_stats():
    return pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')


@pytest.fixture(scope='module')
def goalie_stats():
    return pd.read_csv(OUTPUT_DIR / 'fact_goalie_game_stats.csv')


class TestGameScoresMatchOfficial:
    """Validate game totals match noradhockey.com official scores."""
    
    @pytest.mark.parametrize("game_id", TRACKED_GAMES)
    def test_game_total_goals_match(self, schedule, player_stats, game_id):
        """Each game's total goals must match official score."""
        # Official from schedule (noradhockey.com)
        game = schedule[schedule['game_id'] == game_id].iloc[0]
        expected = int(game['home_total_goals'] + game['away_total_goals'])
        
        # ETL output
        actual = int(player_stats[player_stats['game_id'] == game_id]['goals'].sum())
        
        assert actual == expected, \
            f"Game {game_id}: ETL={actual} goals, Official={expected} goals"
    
    def test_total_goals_all_games(self, schedule, player_stats):
        """Sum of all goals must match sum of official scores."""
        expected = sum(
            schedule[schedule['game_id'] == g].iloc[0]['home_total_goals'] +
            schedule[schedule['game_id'] == g].iloc[0]['away_total_goals']
            for g in TRACKED_GAMES
        )
        actual = player_stats[player_stats['game_id'].isin(TRACKED_GAMES)]['goals'].sum()
        
        assert int(actual) == int(expected), \
            f"Total goals: ETL={int(actual)}, Official={int(expected)}"


class TestPlayerGoalsMatchBLB:
    """Validate player goals match BLB league database."""
    
    def test_player_goals_match_rate(self, roster_blb, player_stats):
        """At least 95% of player goals should match BLB."""
        mismatches = 0
        total = 0
        
        for game_id in TRACKED_GAMES:
            blb = roster_blb[roster_blb['game_id'] == game_id]
            etl = player_stats[player_stats['game_id'] == game_id]
            
            for _, blb_row in blb.iterrows():
                player_id = blb_row['player_id']
                expected = int(blb_row['goals']) if pd.notna(blb_row['goals']) else 0
                
                etl_row = etl[etl['player_id'] == player_id]
                actual = int(etl_row['goals'].iloc[0]) if len(etl_row) > 0 else 0
                
                total += 1
                if expected != actual:
                    mismatches += 1
        
        match_rate = (total - mismatches) / total * 100
        assert match_rate >= 95, \
            f"Only {match_rate:.1f}% of player goals match BLB (need 95%+)"


class TestInternalConsistency:
    """Validate stats are internally consistent."""
    
    def test_points_equals_goals_plus_assists(self, player_stats):
        """Points must equal goals + assists for all rows."""
        if 'points' not in player_stats.columns:
            pytest.skip("No points column")
        
        calculated = player_stats['goals'] + player_stats['assists']
        actual = player_stats['points']
        mismatches = (calculated != actual).sum()
        
        assert mismatches == 0, f"{mismatches} rows have incorrect points"
    
    def test_zone_entry_control_pct_valid(self, player_stats):
        """Zone entry control % must be 0-100."""
        if 'zone_entry_control_pct' not in player_stats.columns:
            pytest.skip("No zone_entry_control_pct column")
        
        invalid = (
            (player_stats['zone_entry_control_pct'] < 0) |
            (player_stats['zone_entry_control_pct'] > 100)
        ).sum()
        
        assert invalid == 0, f"{invalid} rows have invalid zone_entry_control_pct"
    
    def test_logical_shifts_reasonable(self, player_stats):
        """Logical shifts should be 3-25 per player per game."""
        if 'logical_shifts' not in player_stats.columns:
            pytest.skip("No logical_shifts column")
        
        # Allow goalies to have different patterns
        skaters = player_stats[player_stats['logical_shifts'] > 0]
        
        unreasonable = (
            (skaters['logical_shifts'] < 2) |
            (skaters['logical_shifts'] > 30)
        ).sum()
        
        # Allow 5% outliers
        assert unreasonable <= len(skaters) * 0.05, \
            f"{unreasonable} players have unreasonable shift counts"
    
    def test_players_with_shifts_have_toi(self, player_stats):
        """Players with shifts must have TOI > 0."""
        has_shifts = player_stats[player_stats['logical_shifts'] > 0]
        zero_toi = has_shifts[has_shifts['toi_seconds'] <= 0]
        
        assert len(zero_toi) == 0, \
            f"{len(zero_toi)} players have shifts but no TOI"


class TestGoalieStats:
    """Validate goalie statistics."""
    
    @pytest.mark.parametrize("game_id", TRACKED_GAMES)
    def test_two_goalies_per_game(self, goalie_stats, game_id):
        """Each game must have exactly 2 goalies."""
        count = len(goalie_stats[goalie_stats['game_id'] == game_id])
        assert count == 2, f"Game {game_id} has {count} goalies, expected 2"
    
    def test_save_pct_valid(self, goalie_stats):
        """Save % must be 0-100."""
        if 'save_pct' not in goalie_stats.columns:
            pytest.skip("No save_pct column")
        
        invalid = (
            (goalie_stats['save_pct'] < 0) |
            (goalie_stats['save_pct'] > 100)
        ).sum()
        
        assert invalid == 0, f"{invalid} goalies have invalid save_pct"
    
    def test_saves_goals_against_positive(self, goalie_stats):
        """Saves and goals_against must be non-negative."""
        negative_saves = (goalie_stats['saves'] < 0).sum()
        negative_ga = (goalie_stats['goals_against'] < 0).sum()
        
        assert negative_saves == 0, f"{negative_saves} goalies have negative saves"
        assert negative_ga == 0, f"{negative_ga} goalies have negative GA"


class TestPrimaryActorRule:
    """Validate stats follow primary actor rule."""
    
    def test_zone_entries_reasonable(self, player_stats):
        """Zone entries per player per game should be ≤ 20."""
        if 'zone_entries' not in player_stats.columns:
            pytest.skip("No zone_entries column")
        
        high = player_stats[player_stats['zone_entries'] > 20]
        assert len(high) == 0, \
            f"{len(high)} players have > 20 zone entries (primary actor bug?)"
    
    def test_shots_reasonable(self, player_stats):
        """Shots per player per game should be ≤ 30."""
        if 'shots' not in player_stats.columns:
            pytest.skip("No shots column")
        
        high = player_stats[player_stats['shots'] > 30]
        assert len(high) == 0, \
            f"{len(high)} players have > 30 shots (primary actor bug?)"


class TestDataCompleteness:
    """Validate all expected data is present."""
    
    @pytest.mark.parametrize("game_id", TRACKED_GAMES)
    def test_all_roster_players_have_stats(self, roster_blb, player_stats, game_id):
        """Every player in roster should have stats row."""
        roster_players = set(roster_blb[roster_blb['game_id'] == game_id]['player_id'])
        stats_players = set(player_stats[player_stats['game_id'] == game_id]['player_id'])
        
        missing = roster_players - stats_players
        # Allow small number of missing (subs who didn't play)
        assert len(missing) <= 3, \
            f"Game {game_id}: {len(missing)} roster players missing from stats"
