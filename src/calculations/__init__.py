"""
BenchSight Calculations Module

Extracted calculation functions for testability and reusability.

This module contains pure calculation functions extracted from base_etl.py
to make them testable and reusable across the codebase.
"""

from src.calculations.corsi import (
    calculate_corsi_for_player,
    calculate_fenwick_for_player,
    calculate_cf_pct,
    calculate_ff_pct,
    is_corsi_event,
    is_fenwick_event,
    is_sog_event
)

from src.calculations.goals import (
    is_goal_scored,
    filter_goals,
    count_goals_for_player,
    get_goal_filter
)

from src.calculations.ratings import (
    calculate_team_ratings,
    calculate_rating_differential,
    get_competition_tier,
    calculate_expected_cf_pct,
    calculate_cf_pct_vs_expected
)

from src.calculations.time import (
    calculate_toi_seconds,
    calculate_toi_minutes,
    calculate_shift_duration,
    calculate_per_60_rate
)

__all__ = [
    # Corsi
    'calculate_corsi_for_player',
    'calculate_fenwick_for_player',
    'calculate_cf_pct',
    'calculate_ff_pct',
    'is_corsi_event',
    'is_fenwick_event',
    'is_sog_event',
    # Goals
    'is_goal_scored',
    'filter_goals',
    'count_goals_for_player',
    'get_goal_filter',
    # Ratings
    'calculate_team_ratings',
    'calculate_rating_differential',
    'get_competition_tier',
    'calculate_expected_cf_pct',
    'calculate_cf_pct_vs_expected',
    # Time
    'calculate_toi_seconds',
    'calculate_toi_minutes',
    'calculate_shift_duration',
    'calculate_per_60_rate',
]
