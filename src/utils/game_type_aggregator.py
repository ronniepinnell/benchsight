"""
================================================================================
GAME TYPE AGGREGATOR - SINGLE SOURCE OF TRUTH
================================================================================

This module provides the canonical implementation for splitting season-level
aggregations by game_type (Regular, Playoffs, All).

ALL season stats tables MUST use these utilities to ensure consistency.

Tables using this module:
- fact_team_season_stats_basic
- fact_player_season_stats_basic  
- fact_goalie_season_stats_basic
- fact_team_season_stats
- fact_player_season_stats
- fact_goalie_season_stats

Usage:
    from src.utils.game_type_aggregator import (
        GAME_TYPE_SPLITS,
        add_game_type_to_df,
        aggregate_with_game_type
    )

Version: 29.0
Date: January 13, 2026
================================================================================
"""

import pandas as pd
from typing import Callable, Dict, List, Any, Optional
from pathlib import Path

# =============================================================================
# CONSTANTS - SINGLE SOURCE OF TRUTH
# =============================================================================

# The three game_type values produced by all season stats tables
GAME_TYPE_SPLITS = ['Regular', 'Playoffs', 'All']

# Column name in dim_schedule
GAME_TYPE_COLUMN = 'game_type'

# Default game_type when schedule join fails
DEFAULT_GAME_TYPE = 'Regular'


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def load_schedule() -> pd.DataFrame:
    """Load dim_schedule from output directory."""
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'output'
    path = output_dir / 'dim_schedule.csv'
    if path.exists():
        return pd.read_csv(path, low_memory=False)
    return pd.DataFrame()


def add_game_type_to_df(
    df: pd.DataFrame,
    schedule: Optional[pd.DataFrame] = None,
    game_id_col: str = 'game_id'
) -> pd.DataFrame:
    """
    Add game_type column to a DataFrame by joining to schedule.

    Parameters:
        df: DataFrame with game_id column
        schedule: Optional pre-loaded schedule (loads if None)
        game_id_col: Name of game_id column in df

    Returns:
        DataFrame with game_type column added
    """
    if schedule is None:
        schedule = load_schedule()

    if len(schedule) == 0 or game_id_col not in df.columns:
        df['game_type'] = DEFAULT_GAME_TYPE
        return df

    # Only merge the columns we need
    schedule_cols = [game_id_col, GAME_TYPE_COLUMN] if GAME_TYPE_COLUMN in schedule.columns else [game_id_col]

    if GAME_TYPE_COLUMN not in schedule.columns:
        df['game_type'] = DEFAULT_GAME_TYPE
        return df

    # Ensure consistent game_id types before merge (dtype optimization may create int16 vs object mismatches)
    schedule_subset = schedule[[game_id_col, GAME_TYPE_COLUMN]].drop_duplicates().copy()
    schedule_subset[game_id_col] = schedule_subset[game_id_col].astype(str)
    df[game_id_col] = df[game_id_col].astype(str)

    df = df.merge(
        schedule_subset,
        on=game_id_col,
        how='left'
    )
    df['game_type'] = df['game_type'].fillna(DEFAULT_GAME_TYPE)

    return df


def aggregate_with_game_type(
    df: pd.DataFrame,
    group_cols: List[str],
    agg_func: Callable[[pd.DataFrame], Dict[str, Any]],
    key_col: str,
    key_template: str,
    schedule: Optional[pd.DataFrame] = None,
    game_id_col: str = 'game_id'
) -> pd.DataFrame:
    """
    Aggregate a DataFrame with game_type splits (Regular, Playoffs, All).
    
    This is the canonical function for creating season-level aggregations
    with game_type grain. All season stats tables should use this.
    
    Parameters:
        df: Source DataFrame with game-level data
        group_cols: Columns to group by (e.g., ['player_id', 'season_id'])
        agg_func: Function that takes a filtered DataFrame and returns a dict of stats
        key_col: Name of the primary key column to create
        key_template: Template for key like '{player_id}_{season_id}_{game_type}'
        schedule: Optional pre-loaded schedule
        game_id_col: Name of game_id column
    
    Returns:
        DataFrame with one row per group per game_type
    
    Example:
        def calc_stats(games_df):
            return {
                'games_played': len(games_df),
                'goals': games_df['goals'].sum(),
            }
        
        result = aggregate_with_game_type(
            df=player_games,
            group_cols=['player_id', 'season_id'],
            agg_func=calc_stats,
            key_col='player_season_key',
            key_template='{player_id}_{season_id}_{game_type}'
        )
    """
    # Add game_type if not present
    if 'game_type' not in df.columns:
        df = add_game_type_to_df(df, schedule, game_id_col)
    
    all_results = []
    
    # Get unique combinations of group columns
    unique_groups = df[group_cols].drop_duplicates()
    
    for _, group_row in unique_groups.iterrows():
        # Build filter for this group
        mask = pd.Series(True, index=df.index)
        for col in group_cols:
            mask &= (df[col] == group_row[col])
        
        group_df = df[mask]
        
        for game_type in GAME_TYPE_SPLITS:
            # Filter by game_type
            if game_type == 'All':
                filtered_df = group_df
            else:
                filtered_df = group_df[group_df['game_type'] == game_type]
            
            # Skip if no data for this game_type
            if len(filtered_df) == 0:
                continue
            
            # Calculate stats using provided function
            stats = agg_func(filtered_df)
            
            # Add group columns and game_type
            for col in group_cols:
                stats[col] = group_row[col]
            stats['game_type'] = game_type
            
            # Build key
            key_values = {col: group_row[col] for col in group_cols}
            key_values['game_type'] = game_type
            stats[key_col] = key_template.format(**key_values)
            
            all_results.append(stats)
    
    return pd.DataFrame(all_results)


def get_team_record_from_schedule(
    schedule: pd.DataFrame,
    team_id: str,
    season_id: str,
    game_type: str = 'All'
) -> Dict[str, Any]:
    """
    Calculate team record (W-L-T) from schedule for a specific team/season/game_type.

    Uses schedule columns: home_team_id, away_team_id, home_total_goals,
    away_total_goals, home_team_t, away_team_t

    Returns:
        Dict with games_played, wins, losses, ties, points, goals_for, goals_against
    """
    # Ensure goal columns are numeric (dtype optimization may create categoricals)
    schedule = schedule.copy()
    for col in ['home_total_goals', 'away_total_goals', 'home_team_t', 'away_team_t']:
        if col in schedule.columns:
            schedule[col] = pd.to_numeric(schedule[col], errors='coerce').fillna(0)

    # Ensure ID columns are strings for consistent comparison
    schedule['home_team_id'] = schedule['home_team_id'].astype(str)
    schedule['away_team_id'] = schedule['away_team_id'].astype(str)
    schedule['season_id'] = schedule['season_id'].astype(str)
    team_id = str(team_id)
    season_id = str(season_id)

    # Filter to team's games in this season
    home_mask = (schedule['home_team_id'] == team_id) & (schedule['season_id'] == season_id)
    away_mask = (schedule['away_team_id'] == team_id) & (schedule['season_id'] == season_id)
    
    # Apply game_type filter
    if game_type != 'All' and 'game_type' in schedule.columns:
        home_mask &= (schedule['game_type'] == game_type)
        away_mask &= (schedule['game_type'] == game_type)
    
    home_games = schedule[home_mask]
    away_games = schedule[away_mask]
    
    games_played = len(home_games) + len(away_games)
    
    if games_played == 0:
        return None
    
    # Wins
    home_wins = len(home_games[home_games['home_total_goals'] > home_games['away_total_goals']])
    away_wins = len(away_games[away_games['away_total_goals'] > away_games['home_total_goals']])
    wins = home_wins + away_wins
    
    # Ties (from schedule tie columns)
    home_ties = int(home_games['home_team_t'].sum()) if 'home_team_t' in home_games.columns else 0
    away_ties = int(away_games['away_team_t'].sum()) if 'away_team_t' in away_games.columns else 0
    ties = home_ties + away_ties
    
    # Losses
    losses = games_played - wins - ties
    
    # Goals
    home_gf = home_games['home_total_goals'].sum()
    away_gf = away_games['away_total_goals'].sum()
    home_ga = home_games['away_total_goals'].sum()
    away_ga = away_games['home_total_goals'].sum()
    
    return {
        'games_played': games_played,
        'wins': wins,
        'losses': losses,
        'ties': ties,
        'points': wins * 2 + ties * 1,  # W=2, T=1, L=0
        'goals_for': int(home_gf + away_gf),
        'goals_against': int(home_ga + away_ga),
    }


def get_goalie_record_from_games(
    games: pd.DataFrame,
    team_name_col: str = 'team_name'
) -> Dict[str, int]:
    """
    Calculate goalie W-L-T from game data with schedule info joined.
    
    Expects columns: team_name, home_team_name, away_team_name, 
    home_total_goals, away_total_goals, home_team_t, away_team_t
    
    Returns:
        Dict with wins, losses, ties
    """
    wins, losses, ties = 0, 0, 0
    
    for _, g in games.iterrows():
        team = g[team_name_col]
        
        if team == g.get('home_team_name'):
            if g['home_total_goals'] > g['away_total_goals']:
                wins += 1
            elif g['home_total_goals'] < g['away_total_goals']:
                losses += 1
            elif pd.notna(g.get('home_team_t')) and g['home_team_t'] > 0:
                ties += 1
            else:
                losses += 1
        elif team == g.get('away_team_name'):
            if g['away_total_goals'] > g['home_total_goals']:
                wins += 1
            elif g['away_total_goals'] < g['home_total_goals']:
                losses += 1
            elif pd.notna(g.get('away_team_t')) and g['away_team_t'] > 0:
                ties += 1
            else:
                losses += 1
    
    return {'wins': wins, 'losses': losses, 'ties': ties}
