"""
Goal Counting Calculations

CRITICAL: This is the SINGLE SOURCE OF TRUTH for goal counting.
All goal counting throughout the codebase MUST use these functions.

Rules:
- Goals ONLY via: event_type='Goal' AND event_detail='Goal_Scored'
- Shot_Goal = the shot attempt, NOT the goal itself
- event_player_1 = Primary actor (scorer)
"""

import pandas as pd
from typing import Optional


# =============================================================================
# GOAL FILTER - SINGLE SOURCE OF TRUTH
# =============================================================================

def get_goal_filter(events_df: pd.DataFrame) -> pd.Series:
    """
    Get boolean filter for goal events.
    
    CRITICAL: This is THE canonical way to filter goals.
    Goals ONLY via: event_type='Goal' AND event_detail='Goal_Scored'
    
    Args:
        events_df: DataFrame with event_type and event_detail columns
        
    Returns:
        Boolean Series where True indicates a goal event
    """
    return (
        (events_df['event_type'] == 'Goal') & 
        (events_df['event_detail'] == 'Goal_Scored')
    )


def is_goal_scored(event_type: str, event_detail: str) -> bool:
    """
    Check if an event represents a scored goal.
    
    Args:
        event_type: Event type string
        event_detail: Event detail string
        
    Returns:
        True if this is a scored goal event
    """
    return event_type == 'Goal' and event_detail == 'Goal_Scored'


def filter_goals(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter events DataFrame to only goal events.
    
    Uses the canonical goal filter (single source of truth).
    
    Args:
        events_df: DataFrame with event_type and event_detail columns
        
    Returns:
        DataFrame containing only goal events
    """
    goal_filter = get_goal_filter(events_df)
    return events_df[goal_filter].copy()


def count_goals_for_player(
    events_df: pd.DataFrame,
    player_id: str,
    team_id: Optional[str] = None
) -> int:
    """
    Count goals scored by a specific player.
    
    Uses event_player_1 as the scorer (primary actor).
    
    Args:
        events_df: DataFrame with event data
        player_id: Player ID to count goals for
        team_id: Optional team ID filter
        
    Returns:
        Number of goals scored by the player
    """
    goals = filter_goals(events_df)
    
    # Filter by player (event_player_1 is the scorer)
    player_goals = goals[goals['event_player_1'] == player_id]
    
    # Optional team filter
    if team_id is not None:
        player_goals = player_goals[player_goals['team_id'] == team_id]
    
    return len(player_goals)


def count_goals_for_team(
    events_df: pd.DataFrame,
    team_id: str
) -> int:
    """
    Count goals scored by a specific team.
    
    Args:
        events_df: DataFrame with event data
        team_id: Team ID to count goals for
        
    Returns:
        Number of goals scored by the team
    """
    goals = filter_goals(events_df)
    team_goals = goals[goals['team_id'] == team_id]
    return len(team_goals)


def get_goal_assists(goals_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract assist information from goal events.
    
    Assists are tracked via play_detail1 on ASSIST events linked to goals.
    The assister is event_player_1 on their pass/shot event.
    
    Args:
        goals_df: DataFrame of goal events
        
    Returns:
        DataFrame with assist information
    """
    # This would need to join with linked events
    # For now, return empty - implement when needed
    return pd.DataFrame()
