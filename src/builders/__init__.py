"""
BenchSight Table Builders Module

Extracted table building logic for better organization and testability.

This module contains functions to build core fact tables (events, shifts, etc.)
extracted from base_etl.py for better maintainability.
"""

from src.builders.events import build_fact_events
from src.builders.shifts import build_fact_shifts
from src.builders.player_stats import build_fact_player_game_stats, PlayerStatsBuilder
from src.builders.team_stats import build_fact_team_game_stats, TeamStatsBuilder
from src.builders.goalie_stats import build_fact_goalie_game_stats, GoalieStatsBuilder

__all__ = [
    'build_fact_events',
    'build_fact_shifts',
    'build_fact_player_game_stats',
    'build_fact_team_game_stats',
    'build_fact_goalie_game_stats',
    'PlayerStatsBuilder',
    'TeamStatsBuilder',
    'GoalieStatsBuilder',
]
