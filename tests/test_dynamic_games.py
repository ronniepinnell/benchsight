#!/usr/bin/env python3
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

    @pytest.mark.parametrize("game_id,expected_goals,home,away", [
        (18969, 7, 'Platinum', 'Velodrome'),
        (18977, 6, 'Velodrome', 'HollowBrook'),
        (18981, 3, 'Nelson', 'Velodrome'),
        (18987, 1, 'Outlaws', 'Velodrome'),
    ])
    def test_game_total_goals(self, player_stats, game_id, expected_goals, home, away):
        """Each game's total goals must match official score from noradhockey.com."""
        actual = int(player_stats[player_stats['game_id'] == game_id]['goals'].sum())
        assert actual == expected_goals, \
            f"Game {game_id} ({home} vs {away}): ETL={actual}, Official={expected_goals}"


class TestGoalieStats:
    """Test goalie stats for all games."""

    @pytest.mark.parametrize("game_id", [18969, 18977, 18981, 18987])
    def test_two_goalies_per_game(self, goalie_stats, game_id):
        """Each game must have exactly 2 goalies."""
        count = len(goalie_stats[goalie_stats['game_id'] == game_id])
        assert count == 2, f"Game {game_id} has {count} goalies, expected 2"


class TestPlayerStats:
    """Test player stat consistency."""

    @pytest.mark.parametrize("game_id", [18969, 18977, 18981, 18987])
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
        assert match_rate >= 90, \
            f"Game {game_id}: Only {match_rate:.1f}% player goals match BLB"
