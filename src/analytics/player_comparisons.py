"""
=============================================================================
HEAD-TO-HEAD & WITH/WITHOUT ANALYSIS MODULE
=============================================================================
File: src/analytics/player_comparisons.py

PURPOSE:
    Analyze player performance:
    - Head-to-head comparisons (when players face each other)
    - With/without analysis (performance with/without teammates)
    - Corsi/Fenwick on-ice metrics

=============================================================================
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

from src.database.table_operations import read_query, table_exists

from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_player_shifts(game_id: int) -> pd.DataFrame:
    """
    Get shift-level data with all players on ice.
    """
    if not table_exists(f'int_shifts_{game_id}'):
        return pd.DataFrame()
    
    return read_query(f"""
        SELECT 
            shift_index,
            shift_key,
            period,
            shift_start_total_seconds,
            shift_end_total_seconds,
            shift_duration,
            situation,
            strength,
            home_forward_1, home_forward_2, home_forward_3,
            home_defense_1, home_defense_2, home_goalie,
            away_forward_1, away_forward_2, away_forward_3,
            away_defense_1, away_defense_2, away_goalie,
            home_goals, away_goals,
            home_plus, home_minus, away_plus, away_minus
        FROM int_shifts_{game_id}
    """)


def get_events_during_shift(game_id: int, shift_start: float, shift_end: float) -> pd.DataFrame:
    """
    Get all events that occurred during a shift.
    """
    if not table_exists(f'int_events_{game_id}'):
        return pd.DataFrame()
    
    return read_query(f"""
        SELECT *
        FROM int_events_{game_id}
        WHERE time_total_seconds >= {shift_start}
          AND time_total_seconds < {shift_end}
    """)


def find_shared_ice_time(player1_game_num: int, player2_game_num: int, game_id: int) -> pd.DataFrame:
    """
    Find all shifts where two players were on ice together.
    
    Args:
        player1_game_num: First player's game number
        player2_game_num: Second player's game number
        game_id: Game identifier
    
    Returns:
        DataFrame of shifts where both players were on ice
    """
    shifts = get_player_shifts(game_id)
    if len(shifts) == 0:
        return pd.DataFrame()
    
    # All player columns
    player_cols = [
        'home_forward_1', 'home_forward_2', 'home_forward_3',
        'home_defense_1', 'home_defense_2', 'home_goalie',
        'away_forward_1', 'away_forward_2', 'away_forward_3',
        'away_defense_1', 'away_defense_2', 'away_goalie'
    ]
    
    # Find shifts with player 1
    p1_mask = False
    for col in player_cols:
        if col in shifts.columns:
            p1_mask = p1_mask | (shifts[col] == player1_game_num)
    
    # Find shifts with player 2
    p2_mask = False
    for col in player_cols:
        if col in shifts.columns:
            p2_mask = p2_mask | (shifts[col] == player2_game_num)
    
    # Combined
    shared_shifts = shifts[p1_mask & p2_mask].copy()
    shared_shifts['shared_toi'] = shared_shifts['shift_duration']
    
    return shared_shifts


def head_to_head_analysis(
    player1_id: int, 
    player2_id: int, 
    game_id: int = None
) -> Dict:
    """
    Analyze head-to-head performance between two players.
    
    Args:
        player1_id: First player's ID
        player2_id: Second player's ID
        game_id: Optional specific game (otherwise all games)
    
    Returns:
        Dictionary with head-to-head stats
    """
    logger.info(f"Calculating head-to-head: {player1_id} vs {player2_id}")
    
    result = {
        'player1_id': player1_id,
        'player2_id': player2_id,
        'total_shared_toi': 0,
        'player1_stats': {},
        'player2_stats': {}
    }
    
    # Get player game numbers from box scores
    if table_exists('fact_box_score'):
        games_query = "SELECT DISTINCT game_id FROM fact_box_score"
        if game_id:
            games_query += f" WHERE game_id = {game_id}"
        
        games = read_query(games_query)
        
        for _, game_row in games.iterrows():
            gid = game_row['game_id']
            
            # Get player numbers for this game
            p1_query = f"""
                SELECT player_game_number 
                FROM fact_box_score 
                WHERE game_id = {gid} AND player_id = {player1_id}
            """
            p1_data = read_query(p1_query)
            
            p2_query = f"""
                SELECT player_game_number 
                FROM fact_box_score 
                WHERE game_id = {gid} AND player_id = {player2_id}
            """
            p2_data = read_query(p2_query)
            
            if len(p1_data) > 0 and len(p2_data) > 0:
                p1_num = p1_data.iloc[0]['player_game_number']
                p2_num = p2_data.iloc[0]['player_game_number']
                
                # Find shared ice time
                shared = find_shared_ice_time(int(p1_num), int(p2_num), gid)
                result['total_shared_toi'] += shared['shared_toi'].sum() if len(shared) > 0 else 0
    
    return result


def with_without_analysis(
    target_player_id: int,
    teammate_id: int,
    game_id: int = None
) -> Dict:
    """
    Analyze target player's performance with and without a teammate.
    
    Args:
        target_player_id: Player to analyze
        teammate_id: Teammate to compare with/without
        game_id: Optional specific game
    
    Returns:
        Dictionary with with/without stats
    """
    logger.info(f"Calculating with/without: {target_player_id} with/without {teammate_id}")
    
    result = {
        'target_player_id': target_player_id,
        'teammate_id': teammate_id,
        'with_teammate': {
            'toi': 0,
            'goals_for': 0,
            'goals_against': 0,
            'shots_for': 0,
            'shots_against': 0
        },
        'without_teammate': {
            'toi': 0,
            'goals_for': 0,
            'goals_against': 0,
            'shots_for': 0,
            'shots_against': 0
        }
    }
    
    # Would need shift-level event aggregation
    # This is a placeholder for the full implementation
    
    return result


def calculate_on_ice_stats(player_game_num: int, game_id: int) -> Dict:
    """
    Calculate on-ice statistics for a player.
    
    Returns Corsi, Fenwick, goals for/against, etc.
    """
    result = {
        'toi': 0,
        'corsi_for': 0,
        'corsi_against': 0,
        'corsi_pct': 0.0,
        'fenwick_for': 0,
        'fenwick_against': 0,
        'fenwick_pct': 0.0,
        'goals_for': 0,
        'goals_against': 0
    }
    
    shifts = get_player_shifts(game_id)
    if len(shifts) == 0:
        return result
    
    # Player columns for home and away
    home_cols = ['home_forward_1', 'home_forward_2', 'home_forward_3',
                 'home_defense_1', 'home_defense_2']
    away_cols = ['away_forward_1', 'away_forward_2', 'away_forward_3',
                 'away_defense_1', 'away_defense_2']
    
    # Find shifts where player was on ice
    is_home = False
    player_mask = False
    
    for col in home_cols:
        if col in shifts.columns:
            mask = shifts[col] == player_game_num
            if mask.any():
                player_mask = player_mask | mask
                is_home = True
    
    for col in away_cols:
        if col in shifts.columns:
            mask = shifts[col] == player_game_num
            if mask.any():
                player_mask = player_mask | mask
    
    player_shifts = shifts[player_mask]
    
    if len(player_shifts) == 0:
        return result
    
    result['toi'] = player_shifts['shift_duration'].sum()
    
    # Goals for/against based on which team
    if is_home:
        result['goals_for'] = player_shifts['home_plus'].sum() if 'home_plus' in player_shifts.columns else 0
        result['goals_against'] = player_shifts['home_minus'].sum() if 'home_minus' in player_shifts.columns else 0
    else:
        result['goals_for'] = player_shifts['away_plus'].sum() if 'away_plus' in player_shifts.columns else 0
        result['goals_against'] = player_shifts['away_minus'].sum() if 'away_minus' in player_shifts.columns else 0
    
    return result


def get_player_comparison_summary(player1_id: int, player2_id: int) -> pd.DataFrame:
    """
    Get a summary comparison of two players across all games.
    """
    query = f"""
        SELECT 
            player_id,
            SUM(goals) as total_goals,
            SUM(assists) as total_assists,
            SUM(points) as total_points,
            SUM(shots) as total_shots,
            SUM(toi_seconds) as total_toi,
            COUNT(*) as games_played,
            AVG(goals) as avg_goals,
            AVG(points) as avg_points
        FROM fact_box_score
        WHERE player_id IN ({player1_id}, {player2_id})
        GROUP BY player_id
    """
    
    return read_query(query)
