"""
Player Rating Calculations

Functions for calculating player ratings, quality of competition (QoC),
quality of teammates (QoT), and rating-based adjustments.
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple


# =============================================================================
# RATING CONSTANTS
# =============================================================================

# Rating scale: 2-6 (rec hockey)
RATING_MIN = 2.0
RATING_MAX = 6.0
RATING_MIDPOINT = 4.0

# Competition tier thresholds (matches dim_competition_tier)
TIER_ELITE = 5.0      # TI01: Elite (5+)
TIER_ABOVE_AVG = 4.0  # TI02: Above Average (4-5)
TIER_AVG = 3.0        # TI03: Average (3-4)
TIER_BELOW_AVG = 2.0  # TI04: Below Average (2-3)


# =============================================================================
# TEAM RATING CALCULATIONS
# =============================================================================

def calculate_team_ratings(
    player_ids: List[str],
    player_rating_map: Dict[str, float]
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Calculate average, min, and max ratings for a set of players.
    
    Args:
        player_ids: List of player IDs
        player_rating_map: Dict mapping player_id to rating
        
    Returns:
        Tuple of (avg_rating, min_rating, max_rating)
        Returns (None, None, None) if no valid ratings found
    """
    ratings = []
    for pid in player_ids:
        if pd.notna(pid) and pid in player_rating_map:
            rating = player_rating_map[pid]
            if pd.notna(rating):
                ratings.append(float(rating))
    
    if not ratings:
        return None, None, None
    
    avg_rating = round(sum(ratings) / len(ratings), 2)
    min_rating = min(ratings)
    max_rating = max(ratings)
    
    return avg_rating, min_rating, max_rating


def calculate_rating_differential(
    home_avg_rating: Optional[float],
    away_avg_rating: Optional[float]
) -> Optional[float]:
    """
    Calculate rating differential between two teams.
    
    Positive = home team has higher average rating
    Negative = away team has higher average rating
    
    Args:
        home_avg_rating: Home team average rating
        away_avg_rating: Away team average rating
        
    Returns:
        Rating differential (home - away), or None if either is missing
    """
    if pd.isna(home_avg_rating) or pd.isna(away_avg_rating):
        return None
    
    return round(home_avg_rating - away_avg_rating, 2)


# =============================================================================
# COMPETITION TIER
# =============================================================================

def get_competition_tier(opp_rating: Optional[float]) -> Optional[str]:
    """
    Get competition tier based on opponent average rating.
    
    Matches dim_competition_tier:
    - TI01: Elite (5.0+)
    - TI02: Above Average (4.0-5.0)
    - TI03: Average (3.0-4.0)
    - TI04: Below Average (2.0-3.0)
    
    Args:
        opp_rating: Opponent average rating
        
    Returns:
        Competition tier ID (TI01-TI04), or None if rating is missing
    """
    if pd.isna(opp_rating):
        return None
    
    if opp_rating >= TIER_ELITE:
        return 'TI01'  # Elite
    elif opp_rating >= TIER_ABOVE_AVG:
        return 'TI02'  # Above Average
    elif opp_rating >= TIER_AVG:
        return 'TI03'  # Average
    else:
        return 'TI04'  # Below Average


# =============================================================================
# EXPECTED PERFORMANCE CALCULATIONS
# =============================================================================

def calculate_expected_cf_pct(
    rating_differential: Optional[float],
    base_cf_pct: float = 50.0,
    rating_impact: float = 5.0
) -> Optional[float]:
    """
    Calculate expected CF% based on rating differential.
    
    Formula: base_cf_pct + (rating_differential * rating_impact)
    Each rating point = rating_impact% CF advantage
    
    Args:
        rating_differential: Player/team rating - opponent rating
        base_cf_pct: Base CF% (default 50.0)
        rating_impact: CF% change per rating point (default 5.0)
        
    Returns:
        Expected CF% (clipped to 30-70), or None if differential is missing
    """
    if pd.isna(rating_differential):
        return None
    
    expected = base_cf_pct + (rating_differential * rating_impact)
    return max(30.0, min(70.0, expected))  # Clip to reasonable bounds


def calculate_cf_pct_vs_expected(
    actual_cf_pct: Optional[float],
    expected_cf_pct: Optional[float]
) -> Optional[float]:
    """
    Calculate CF% vs expected performance.
    
    Positive = performed better than expected
    Negative = performed worse than expected
    
    Args:
        actual_cf_pct: Actual CF% achieved
        expected_cf_pct: Expected CF% based on ratings
        
    Returns:
        CF% vs expected (actual - expected), or None if either is missing
    """
    if pd.isna(actual_cf_pct) or pd.isna(expected_cf_pct):
        return None
    
    return round(actual_cf_pct - expected_cf_pct, 2)


def get_performance_category(cf_pct_vs_expected: Optional[float]) -> Optional[str]:
    """
    Categorize performance based on CF% vs expected.
    
    - Over: > 5% above expected
    - Under: < -5% below expected
    - Expected: Within 5% of expected
    
    Args:
        cf_pct_vs_expected: CF% vs expected value
        
    Returns:
        Performance category ('Over', 'Under', 'Expected'), or None
    """
    if pd.isna(cf_pct_vs_expected):
        return None
    
    if cf_pct_vs_expected > 5:
        return 'Over'
    elif cf_pct_vs_expected < -5:
        return 'Under'
    else:
        return 'Expected'


# =============================================================================
# OPPONENT MULTIPLIER
# =============================================================================

def calculate_opponent_multiplier(opp_avg_rating: Optional[float]) -> float:
    """
    Calculate opponent multiplier for adjusted stats.
    
    Formula: opp_avg_rating / RATING_MIDPOINT
    Used to adjust stats based on opponent strength.
    
    Args:
        opp_avg_rating: Opponent average rating
        
    Returns:
        Opponent multiplier (defaults to 1.0 if rating is missing)
    """
    if pd.isna(opp_avg_rating):
        return 1.0
    
    return opp_avg_rating / RATING_MIDPOINT
