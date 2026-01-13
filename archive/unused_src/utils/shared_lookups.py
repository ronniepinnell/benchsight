"""
=============================================================================
SHARED LOOKUPS - Common Data Structures Used Across ETL
=============================================================================
File: src/utils/shared_lookups.py
Version: 19.12
Created: January 9, 2026

Provides cached access to commonly-used lookup dictionaries.
Eliminates duplicate creation of the same lookups in multiple places.

Usage:
    from src.utils.shared_lookups import get_player_rating_map, get_team_lookup
    
    rating_map = get_player_rating_map()
    player_rating = rating_map.get('P100001', 5.0)
=============================================================================
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

# Default output directory
OUTPUT_DIR = Path(__file__).parent.parent.parent / 'data' / 'output'


class LookupCache:
    """
    Singleton cache for commonly-used lookup dictionaries.
    
    Prevents loading the same data multiple times during ETL.
    """
    
    _instance = None
    _cache: Dict[str, dict] = {}
    _output_dir: Path = OUTPUT_DIR
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._cache = {}
        return cls._instance
    
    def set_output_dir(self, path: Path):
        """Set the output directory and clear cache."""
        self._output_dir = path
        self._cache.clear()
    
    def clear(self):
        """Clear all cached lookups."""
        self._cache.clear()
        logger.debug("LookupCache cleared")
    
    def get_player_rating_map(self) -> Dict[str, float]:
        """
        Get player_id -> current_skill_rating mapping.
        
        Returns:
            Dict mapping player_id to rating (default 5.0)
        """
        if 'player_rating_map' not in self._cache:
            path = self._output_dir / 'dim_player.csv'
            if path.exists():
                df = pd.read_csv(path, low_memory=False)
                self._cache['player_rating_map'] = dict(
                    zip(df['player_id'], df['current_skill_rating'].fillna(5.0))
                )
                logger.debug(f"Loaded player_rating_map: {len(self._cache['player_rating_map'])} players")
            else:
                logger.warning("dim_player.csv not found, returning empty map")
                self._cache['player_rating_map'] = {}
        
        return self._cache['player_rating_map']
    
    def get_team_lookup(self) -> Dict[str, str]:
        """
        Get team_name -> team_id mapping.
        
        Returns:
            Dict mapping team names (lowercase) to team_id
        """
        if 'team_lookup' not in self._cache:
            path = self._output_dir / 'dim_team.csv'
            if path.exists():
                df = pd.read_csv(path)
                self._cache['team_lookup'] = {
                    str(name).lower().strip(): tid 
                    for name, tid in zip(df['team_name'], df['team_id'])
                }
                logger.debug(f"Loaded team_lookup: {len(self._cache['team_lookup'])} teams")
            else:
                self._cache['team_lookup'] = {}
        
        return self._cache['team_lookup']
    
    def get_player_name_map(self) -> Dict[str, str]:
        """
        Get player_id -> player_full_name mapping.
        """
        if 'player_name_map' not in self._cache:
            path = self._output_dir / 'dim_player.csv'
            if path.exists():
                df = pd.read_csv(path, low_memory=False)
                self._cache['player_name_map'] = dict(
                    zip(df['player_id'], df['player_full_name'])
                )
            else:
                self._cache['player_name_map'] = {}
        
        return self._cache['player_name_map']
    
    def get_player_position_map(self) -> Dict[str, str]:
        """
        Get player_id -> position_id mapping.
        """
        if 'player_position_map' not in self._cache:
            path = self._output_dir / 'dim_player.csv'
            if path.exists():
                df = pd.read_csv(path, low_memory=False)
                self._cache['player_position_map'] = dict(
                    zip(df['player_id'], df['position_id'])
                )
            else:
                self._cache['player_position_map'] = {}
        
        return self._cache['player_position_map']
    
    def get_game_teams(self) -> Dict[int, Dict[str, str]]:
        """
        Get game_id -> {home_team, away_team} mapping.
        """
        if 'game_teams' not in self._cache:
            path = self._output_dir / 'dim_schedule.csv'
            if path.exists():
                df = pd.read_csv(path)
                self._cache['game_teams'] = {}
                for _, row in df.iterrows():
                    self._cache['game_teams'][int(row['game_id'])] = {
                        'home_team': str(row.get('home_team', '')).lower(),
                        'away_team': str(row.get('away_team', '')).lower(),
                        'home_team_id': row.get('home_team_id'),
                        'away_team_id': row.get('away_team_id'),
                    }
            else:
                self._cache['game_teams'] = {}
        
        return self._cache['game_teams']


# Global instance
_lookup_cache: Optional[LookupCache] = None


def get_lookup_cache() -> LookupCache:
    """Get the global LookupCache instance."""
    global _lookup_cache
    if _lookup_cache is None:
        _lookup_cache = LookupCache()
    return _lookup_cache


# Convenience functions
def get_player_rating_map() -> Dict[str, float]:
    """Get player_id -> rating mapping."""
    return get_lookup_cache().get_player_rating_map()


def get_player_name_map() -> Dict[str, str]:
    """Get player_id -> name mapping."""
    return get_lookup_cache().get_player_name_map()


def get_team_lookup() -> Dict[str, str]:
    """Get team_name -> team_id mapping."""
    return get_lookup_cache().get_team_lookup()


def get_game_teams() -> Dict[int, Dict[str, str]]:
    """Get game_id -> team info mapping."""
    return get_lookup_cache().get_game_teams()


def clear_lookup_cache():
    """Clear all cached lookups."""
    get_lookup_cache().clear()
