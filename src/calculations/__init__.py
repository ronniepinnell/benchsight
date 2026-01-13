"""
Calculation Functions Module

Centralized location for all calculation functions used in ETL.
Organized by domain (goalie, player, team, etc.)

Version: 29.7

Note: Goalie calculations module will be added in future refactoring.
For now, goalie calculations remain in src/tables/core_facts.py
"""

# Import existing calculation functions
from src.calculations.corsi import (
    calculate_cf_pct,
    calculate_ff_pct,
    calculate_corsi_for_player,
    calculate_fenwick_for_player,
)

from src.calculations.time import (
    calculate_per_60_rate,
    calculate_toi_seconds,
    calculate_toi_minutes,
    calculate_shift_duration,
    calculate_per_60_from_seconds,
)

from src.calculations.ratings import (
    calculate_team_ratings,
    calculate_rating_differential,
    calculate_expected_cf_pct,
    calculate_cf_pct_vs_expected,
    calculate_opponent_multiplier,
)

from src.calculations.goals import (
    get_goal_filter,
    is_goal_scored,
)

# Goalie calculations (v29.7)
from src.calculations.goalie_calculations import (
    calculate_goalie_core_stats,
    calculate_goalie_save_types,
    calculate_goalie_high_danger,
    calculate_goalie_rebound_control,
    calculate_goalie_period_splits,
    calculate_goalie_time_buckets,
    calculate_goalie_shot_context,
    calculate_goalie_pressure_handling,
    calculate_goalie_quality_indicators,
    calculate_goalie_composites,
    calculate_goalie_war,
)

__all__ = [
    # Corsi/Fenwick
    'calculate_cf_pct',
    'calculate_ff_pct',
    'calculate_corsi_for_player',
    'calculate_fenwick_for_player',
    # Time/TOI
    'calculate_per_60_rate',
    'calculate_toi_seconds',
    'calculate_toi_minutes',
    'calculate_shift_duration',
    'calculate_per_60_from_seconds',
    # Ratings
    'calculate_team_ratings',
    'calculate_rating_differential',
    'calculate_expected_cf_pct',
    'calculate_cf_pct_vs_expected',
    'calculate_opponent_multiplier',
    # Goals
    'get_goal_filter',
    'is_goal_scored',
    # Goalie calculations (v29.7)
    'calculate_goalie_core_stats',
    'calculate_goalie_save_types',
    'calculate_goalie_high_danger',
    'calculate_goalie_rebound_control',
    'calculate_goalie_period_splits',
    'calculate_goalie_time_buckets',
    'calculate_goalie_shot_context',
    'calculate_goalie_pressure_handling',
    'calculate_goalie_quality_indicators',
    'calculate_goalie_composites',
    'calculate_goalie_war',
]
