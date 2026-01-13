"""
=============================================================================
LEAGUE STATS PROCESSOR
=============================================================================
File: src/transformation/league_stats_processor.py

PURPOSE:
    Process games that don't have manual tracking data, using only the
    basic stats from fact_gameroster (BLB league-provided data).

WHEN TO USE:
    - No tracking file exists for the game
    - User chooses "League Stats Only" mode
    - Batch processing games where tracking isn't available

OUTPUT:
    Creates a simplified box score with:
    - Basic identity columns
    - Scoring stats (G, A, P)
    - Plus/minus
    - Penalty minutes
    - Skill ratings
    - is_tracked = False flag

ANALYSIS AVAILABLE FOR NON-TRACKED GAMES:
    - Season totals (goals, assists, points)
    - Team records with/without player
    - Goalie performance vs opponents
    - Lineup skill comparisons
    - Trends over time

ANALYSIS NOT AVAILABLE:
    - Event-level data (shots, passes, turnovers)
    - Shift-level data
    - XY coordinates / shot maps
    - Micro-stats (stick checks, dekes, etc.)
    - Corsi/Fenwick

=============================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List, Tuple

from src.utils.logger import get_logger

logger = get_logger(__name__)


class LeagueStatsProcessor:
    """
    Process games using only league-provided stats from fact_gameroster.
    
    This processor creates simplified box scores for games where manual
    tracking data is not available.
    
    Attributes:
        blb_tables: Dictionary of BLB master tables
    """
    
    def __init__(self, blb_tables: Dict[str, pd.DataFrame]):
        """
        Initialize the processor.
        
        Args:
            blb_tables: Dictionary with BLB tables, must include:
                - fact_gameroster: Game roster with basic stats
                - dim_player: Player master data
                - dim_schedule: Game schedule
                - dim_team: Team info
        """
        self.blb_tables = blb_tables
        
        # Validate required tables
        required = ['fact_gameroster', 'dim_player', 'dim_schedule']
        for table in required:
            if table not in blb_tables:
                raise ValueError(f"Missing required BLB table: {table}")
        
        self.gameroster = blb_tables['fact_gameroster']
        self.players = blb_tables['dim_player']
        self.schedule = blb_tables['dim_schedule']
        
        logger.info("LeagueStatsProcessor initialized")
    
    def get_available_games(self) -> List[int]:
        """
        Get list of all game_ids in fact_gameroster.
        
        Returns:
            List of game IDs
        """
        return self.gameroster['game_id'].unique().tolist()
    
    def check_game_exists(self, game_id: int) -> bool:
        """
        Check if a game exists in the league data.
        
        Args:
            game_id: Game identifier
        
        Returns:
            True if game exists in fact_gameroster
        """
        return game_id in self.gameroster['game_id'].values
    
    def get_game_info(self, game_id: int) -> Optional[Dict]:
        """
        Get basic game information.
        
        Args:
            game_id: Game identifier
        
        Returns:
            Dict with game info or None
        """
        if not self.check_game_exists(game_id):
            return None
        
        game_data = self.gameroster[self.gameroster['game_id'] == game_id].iloc[0]
        
        # Try to get schedule info
        schedule_info = self.schedule[self.schedule['game_id'] == game_id]
        
        return {
            'game_id': game_id,
            'home_team': game_data.get('home_team', 'Unknown'),
            'away_team': game_data.get('away_team', 'Unknown'),
            'game_date': schedule_info['game_date'].iloc[0] if len(schedule_info) > 0 else None,
            'player_count': len(self.gameroster[self.gameroster['game_id'] == game_id]),
        }
    
    def process_game(self, game_id: int) -> Dict[str, pd.DataFrame]:
        """
        Process a single game using league stats only.
        
        Args:
            game_id: Game identifier
        
        Returns:
            Dictionary with:
            - fact_box_score_tracking: Simplified box score
            - dim_game_players_tracking: Player info for game
        """
        if not self.check_game_exists(game_id):
            logger.error(f"Game {game_id} not found in fact_gameroster")
            return {}
        
        # Get roster for this game
        game_roster = self.gameroster[self.gameroster['game_id'] == game_id].copy()
        logger.info(f"Processing game {game_id}: {len(game_roster)} players")
        
        # Build dim_game_players
        dim_game_players = self._build_game_players(game_roster)
        
        # Build simplified box score
        fact_box_score = self._build_box_score(game_roster)
        
        return {
            'fact_box_score_tracking': fact_box_score,
            'dim_game_players_tracking': dim_game_players,
        }
    
    def _build_game_players(self, game_roster: pd.DataFrame) -> pd.DataFrame:
        """Build dim_game_players from roster data."""
        
        # Get columns that exist
        columns_to_use = []
        column_mapping = {
            'game_id': 'game_id',
            'player_game_number': 'player_game_number',
            'player_id': 'player_id',
            'player_full_name': 'player_full_name',
            'team_name': 'player_team',
            'team_venue': 'player_venue',
            'player_position': 'position',
            'skill_rating': 'skill_rating',
        }
        
        result = pd.DataFrame()
        for src, dst in column_mapping.items():
            if src in game_roster.columns:
                result[dst] = game_roster[src]
        
        # Create player_game_key
        result['player_game_key'] = result.apply(
            lambda r: f"{r['game_id']}_{int(r['player_game_number'])}" 
            if pd.notna(r.get('player_game_number')) else None,
            axis=1
        )
        
        # Add display name from dim_player
        if 'random_player_full_name' in self.players.columns:
            name_lookup = self.players.set_index('player_id')['random_player_full_name'].to_dict()
            result['display_name'] = result['player_id'].map(name_lookup)
        
        return result
    
    def _build_box_score(self, game_roster: pd.DataFrame) -> pd.DataFrame:
        """Build simplified box score from league stats."""
        
        box = game_roster.copy()
        
        # Ensure required columns exist
        required_cols = {
            'game_id': 0,
            'player_game_number': None,
            'player_id': None,
            'goals': 0,
            'assists': 0,
        }
        
        for col, default in required_cols.items():
            if col not in box.columns:
                box[col] = default
        
        # Create player_game_key
        box['player_game_key'] = box.apply(
            lambda r: f"{r['game_id']}_{int(r['player_game_number'])}" 
            if pd.notna(r.get('player_game_number')) else None,
            axis=1
        )
        
        # Rename columns to match tracked game format
        rename_map = {
            'team_name': 'player_team',
            'team_venue': 'player_venue',
            'player_position': 'position',
        }
        for old, new in rename_map.items():
            if old in box.columns and new not in box.columns:
                box[new] = box[old]
        
        # Calculate points
        box['goals'] = pd.to_numeric(box.get('goals', 0), errors='coerce').fillna(0).astype(int)
        box['assists'] = pd.to_numeric(box.get('assists', 0), errors='coerce').fillna(0).astype(int)
        box['points'] = box['goals'] + box['assists']
        
        # Add plus_minus if available
        if 'plus_minus' not in box.columns:
            box['plus_minus'] = 0
        
        # Add penalty minutes if available  
        if 'penalty_minutes' not in box.columns and 'pim' in box.columns:
            box['penalty_minutes'] = box['pim']
        elif 'penalty_minutes' not in box.columns:
            box['penalty_minutes'] = 0
        
        # Mark as NOT tracked
        box['is_tracked'] = False
        
        # Add skill rating if not present
        if 'skill_rating' not in box.columns:
            skill_lookup = self.players.set_index('player_id')['current_skill_rating'].to_dict()
            box['skill_rating'] = box['player_id'].map(skill_lookup).fillna(4)
        
        # Add display name
        if 'random_player_full_name' in self.players.columns:
            name_lookup = self.players.set_index('player_id')['random_player_full_name'].to_dict()
            box['display_name'] = box['player_id'].map(name_lookup)
        
        # Select final columns (only those that exist)
        final_columns = [
            'player_game_key', 'game_id', 'player_game_number', 'player_id',
            'player_full_name', 'display_name', 'player_team', 'player_venue',
            'position', 'skill_rating',
            'goals', 'assists', 'points', 'plus_minus', 'penalty_minutes',
            'is_tracked'
        ]
        
        # Add any additional columns from gameroster that might be useful
        for col in ['goals_against', 'saves', 'shots_against']:
            if col in box.columns:
                final_columns.append(col)
        
        # Filter to columns that exist
        existing_cols = [c for c in final_columns if c in box.columns]
        result = box[existing_cols].copy()
        
        logger.info(f"Created box score with {len(result)} players, {len(existing_cols)} columns")
        return result
    
    def process_multiple_games(self, game_ids: List[int]) -> Dict[str, pd.DataFrame]:
        """
        Process multiple games at once.
        
        Args:
            game_ids: List of game identifiers
        
        Returns:
            Combined DataFrames for all games
        """
        all_box_scores = []
        all_game_players = []
        
        for game_id in game_ids:
            result = self.process_game(game_id)
            if result:
                if 'fact_box_score_tracking' in result:
                    all_box_scores.append(result['fact_box_score_tracking'])
                if 'dim_game_players_tracking' in result:
                    all_game_players.append(result['dim_game_players_tracking'])
        
        combined = {}
        
        if all_box_scores:
            combined['fact_box_score_tracking'] = pd.concat(all_box_scores, ignore_index=True)
        
        if all_game_players:
            combined['dim_game_players_tracking'] = pd.concat(all_game_players, ignore_index=True)
        
        return combined
    
    def get_season_totals(self, season_id: int = None) -> pd.DataFrame:
        """
        Get season totals for all players.
        
        Args:
            season_id: Optional season filter
        
        Returns:
            DataFrame with season totals per player
        """
        df = self.gameroster.copy()
        
        # Filter by season if provided
        if season_id and 'season_id' in df.columns:
            df = df[df['season_id'] == season_id]
        
        # Aggregate
        agg_cols = {
            'game_id': 'count',
            'goals': 'sum',
            'assists': 'sum',
            'plus_minus': 'sum',
        }
        
        # Filter to columns that exist
        agg_cols = {k: v for k, v in agg_cols.items() if k in df.columns}
        
        totals = df.groupby('player_id').agg(agg_cols).reset_index()
        totals.columns = ['player_id', 'games_played', 'goals', 'assists', 'plus_minus']
        
        totals['points'] = totals['goals'] + totals['assists']
        totals['points_per_game'] = (totals['points'] / totals['games_played']).round(2)
        
        # Add player info
        totals = totals.merge(
            self.players[['player_id', 'player_full_name', 'current_skill_rating']],
            on='player_id',
            how='left'
        )
        
        return totals.sort_values('points', ascending=False)
    
    def get_team_with_without(self, player_id: int, team_name: str) -> Dict:
        """
        Get team performance with and without a specific player.
        
        Args:
            player_id: Player to analyze
            team_name: Team to analyze
        
        Returns:
            Dict with performance metrics
        """
        # Get all games for this team
        team_games = self.gameroster[
            self.gameroster['team_name'] == team_name
        ]['game_id'].unique()
        
        # Get games where player played
        player_games = self.gameroster[
            (self.gameroster['player_id'] == player_id) &
            (self.gameroster['team_name'] == team_name)
        ]['game_id'].unique()
        
        # Games without player
        without_games = set(team_games) - set(player_games)
        
        def calc_stats(game_ids):
            if not game_ids:
                return {'games': 0, 'goals': 0, 'goals_against': 0}
            
            df = self.gameroster[
                (self.gameroster['game_id'].isin(game_ids)) &
                (self.gameroster['team_name'] == team_name)
            ]
            
            return {
                'games': len(game_ids),
                'goals': df['goals'].sum() if 'goals' in df.columns else 0,
                'goals_against': df.get('goals_against', pd.Series([0])).sum(),
            }
        
        with_stats = calc_stats(player_games)
        without_stats = calc_stats(without_games)
        
        return {
            'player_id': player_id,
            'team': team_name,
            'with_player': with_stats,
            'without_player': without_stats,
            'goals_per_game_with': with_stats['goals'] / max(with_stats['games'], 1),
            'goals_per_game_without': without_stats['goals'] / max(without_stats['games'], 1),
        }
    
    def get_goalie_vs_opponents(self, goalie_id: int) -> pd.DataFrame:
        """
        Get goalie performance vs different opponents.
        
        Args:
            goalie_id: Goalie player_id
        
        Returns:
            DataFrame with performance by opponent
        """
        goalie_games = self.gameroster[
            (self.gameroster['player_id'] == goalie_id) &
            (self.gameroster['player_position'].isin(['G', 'Goalie', 'goalie']))
        ].copy()
        
        if 'opp_team_name' not in goalie_games.columns:
            # Try to derive opponent from schedule
            logger.warning("opp_team_name not in gameroster, cannot calculate vs opponents")
            return pd.DataFrame()
        
        # Aggregate by opponent
        stats = goalie_games.groupby('opp_team_name').agg({
            'game_id': 'count',
            'goals_against': 'sum' if 'goals_against' in goalie_games.columns else 'count',
            'saves': 'sum' if 'saves' in goalie_games.columns else 'count',
        }).reset_index()
        
        stats.columns = ['opponent', 'games', 'goals_against', 'saves']
        
        # Calculate save %
        stats['shots_against'] = stats['saves'] + stats['goals_against']
        stats['save_pct'] = (stats['saves'] / stats['shots_against']).round(3)
        stats['gaa'] = (stats['goals_against'] / stats['games']).round(2)
        
        return stats.sort_values('games', ascending=False)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_league_stats_box_score(blb_tables: Dict[str, pd.DataFrame], 
                                   game_id: int) -> pd.DataFrame:
    """
    Convenience function to create a box score from league stats.
    
    Args:
        blb_tables: BLB table dictionary
        game_id: Game to process
    
    Returns:
        Box score DataFrame
    """
    processor = LeagueStatsProcessor(blb_tables)
    result = processor.process_game(game_id)
    return result.get('fact_box_score_tracking', pd.DataFrame())
