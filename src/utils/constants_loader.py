"""
Analytics Constants Loader
Loads constants from config/analytics_constants.yaml
"""
import yaml
from pathlib import Path
from typing import Dict, Any

_CONSTANTS_CACHE = None

def load_analytics_constants() -> Dict[str, Any]:
    """
    Load analytics constants from config file.

    Returns:
        Dictionary with xg_model, gar_weights, league_constants, etc.
    """
    global _CONSTANTS_CACHE

    if _CONSTANTS_CACHE is not None:
        return _CONSTANTS_CACHE

    config_path = Path("config/analytics_constants.yaml")

    if not config_path.exists():
        # Fallback to hardcoded defaults if config doesn't exist
        return _get_default_constants()

    try:
        with open(config_path, 'r') as f:
            _CONSTANTS_CACHE = yaml.safe_load(f)
        return _CONSTANTS_CACHE
    except Exception as e:
        print(f"WARNING: Failed to load analytics constants from {config_path}: {e}")
        print("  Falling back to hardcoded defaults")
        return _get_default_constants()


def _get_default_constants() -> Dict[str, Any]:
    """Fallback hardcoded constants if config file doesn't exist."""
    return {
        'xg_model': {
            'base_rates': {'high_danger': 0.25, 'medium_danger': 0.08, 'low_danger': 0.03, 'default': 0.06},
            'modifiers': {'rush': 1.3, 'rebound': 1.5, 'one_timer': 1.4, 'breakaway': 2.5, 'screened': 1.2, 'deflection': 1.3},
            'shot_type_modifiers': {'wrist': 1.0, 'slap': 0.95, 'snap': 1.05, 'backhand': 0.9, 'tip': 1.15, 'deflection': 1.1}
        },
        'gar_weights': {
            'player': {
                'goals': 1.0, 'primary_assists': 0.7, 'secondary_assists': 0.4,
                'shots_generated': 0.015, 'xg_generated': 0.8,
                'takeaways': 0.05, 'blocked_shots': 0.02, 'defensive_zone_exits': 0.03,
                'cf_above_avg': 0.02, 'zone_entry_value': 0.04,
                'shot_assists': 0.3, 'pressure_success': 0.02
            },
            'goalie': {
                'saves_above_avg': 0.1, 'high_danger_saves': 0.15, 'goals_prevented': 1.0,
                'rebound_control': 0.05, 'quality_start_bonus': 0.5
            }
        },
        'league_constants': {
            'goals_per_win': 4.5,
            'games_per_season': 20,
            'avg_save_pct': 88.0
        },
        'rating_game_score_map': {
            1: 1.0, 2: 2.3, 3: 3.5, 4: 4.7, 5: 5.9,
            6: 7.1, 7: 8.3, 8: 9.5, 9: 10.7, 10: 12.0
        }
    }


# Convenience accessors
def get_xg_base_rates() -> Dict[str, float]:
    """Get xG base rates by danger zone."""
    constants = load_analytics_constants()
    return constants.get('xg_model', {}).get('base_rates', {})


def get_xg_modifiers() -> Dict[str, float]:
    """Get xG situation modifiers."""
    constants = load_analytics_constants()
    return constants.get('xg_model', {}).get('modifiers', {})


def get_shot_type_xg_modifiers() -> Dict[str, float]:
    """Get xG modifiers by shot type."""
    constants = load_analytics_constants()
    return constants.get('xg_model', {}).get('shot_type_modifiers', {})


def get_gar_weights(player_type: str = 'player') -> Dict[str, float]:
    """
    Get GAR/WAR weights.

    Args:
        player_type: 'player' or 'goalie'
    """
    constants = load_analytics_constants()
    return constants.get('gar_weights', {}).get(player_type, {})


def get_league_constants() -> Dict[str, float]:
    """Get league-wide constants (goals_per_win, etc.)."""
    constants = load_analytics_constants()
    return constants.get('league_constants', {})


def get_rating_game_score_map() -> Dict[int, float]:
    """Get rating-to-game-score mapping."""
    constants = load_analytics_constants()
    return constants.get('rating_game_score_map', {})
