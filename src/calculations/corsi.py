"""
Corsi and Fenwick Calculations

Corsi = all shot attempts (SOG + blocked + missed)
Fenwick = unblocked shot attempts (SOG + missed, excludes blocked)
"""

import pandas as pd
from typing import Optional


# =============================================================================
# EVENT TYPE DETECTION
# =============================================================================

def is_sog_event(event_type: str, event_detail: str) -> bool:
    """
    Check if event is a shot on goal (SOG).
    
    SOG = shots that reached the goalie (saved or scored)
    EXCLUDES Goal_Scored to avoid double-counting.
    Only count the shot event (Shot_Goal), not the goal event (Goal_Scored).
    
    Args:
        event_type: Event type string
        event_detail: Event detail string
        
    Returns:
        True if this is a shot on goal
    """
    if event_type != 'Shot':
        return False
    
    sog_details = ['Shot_OnNetSaved', 'Shot_OnNet', 'Shot_Goal']
    return event_detail in sog_details


def is_blocked_shot(event_detail: str) -> bool:
    """
    Check if event is a blocked shot.
    
    Args:
        event_detail: Event detail string
        
    Returns:
        True if this is a blocked shot
    """
    return 'Blocked' in str(event_detail) if pd.notna(event_detail) else False


def is_missed_shot(event_detail: str) -> bool:
    """
    Check if event is a missed shot.
    
    Args:
        event_detail: Event detail string
        
    Returns:
        True if this is a missed shot
    """
    missed_details = ['Shot_Missed', 'Shot_MissedPost']
    return event_detail in missed_details if pd.notna(event_detail) else False


def is_corsi_event(event_type: str, event_detail: str) -> bool:
    """
    Check if event is a Corsi event (shot attempt).
    
    Corsi = all shot attempts (SOG + blocked + missed)
    
    Args:
        event_type: Event type string
        event_detail: Event detail string
        
    Returns:
        True if this is a Corsi event
    """
    return (
        is_sog_event(event_type, event_detail) or
        is_blocked_shot(event_detail) or
        is_missed_shot(event_detail)
    )


def is_fenwick_event(event_type: str, event_detail: str) -> bool:
    """
    Check if event is a Fenwick event (unblocked shot attempt).
    
    Fenwick = unblocked shot attempts (SOG + missed, excludes blocked)
    
    Args:
        event_type: Event type string
        event_detail: Event detail string
        
    Returns:
        True if this is a Fenwick event
    """
    return (
        is_sog_event(event_type, event_detail) or
        is_missed_shot(event_detail)
    )


# =============================================================================
# CORSI/FENWICK CALCULATIONS
# =============================================================================

def calculate_corsi_for_player(
    events_df: pd.DataFrame,
    player_id: str,
    team_id: Optional[str] = None
) -> int:
    """
    Calculate Corsi events for a player.

    Corsi = all shot attempts (SOG + blocked + missed)
    event_player_1 = primary actor (gets credit)

    Args:
        events_df: DataFrame with event data
        player_id: Player ID to calculate for
        team_id: Optional team ID filter

    Returns:
        Number of Corsi events
    """
    # Filter to player's events (event_player_1 gets credit)
    player_events = events_df[events_df['event_player_1'] == player_id]
    
    # Optional team filter
    if team_id is not None:
        player_events = player_events[player_events['team_id'] == team_id]
    
    # Filter to Corsi events
    corsi_events = player_events[
        player_events.apply(
            lambda row: is_corsi_event(row['event_type'], row['event_detail']),
            axis=1
        )
    ]
    
    return len(corsi_events)


def calculate_fenwick_for_player(
    events_df: pd.DataFrame,
    player_id: str,
    team_id: Optional[str] = None
) -> int:
    """
    Calculate Fenwick events for a player.

    Fenwick = unblocked shot attempts (SOG + missed, excludes blocked)
    event_player_1 = primary actor (gets credit)

    Args:
        events_df: DataFrame with event data
        player_id: Player ID to calculate for
        team_id: Optional team ID filter

    Returns:
        Number of Fenwick events
    """
    # Filter to player's events (event_player_1 gets credit)
    player_events = events_df[events_df['event_player_1'] == player_id]
    
    # Optional team filter
    if team_id is not None:
        player_events = player_events[player_events['team_id'] == team_id]
    
    # Filter to Fenwick events
    fenwick_events = player_events[
        player_events.apply(
            lambda row: is_fenwick_event(row['event_type'], row['event_detail']),
            axis=1
        )
    ]
    
    return len(fenwick_events)


def calculate_cf_pct(cf: int, ca: int) -> Optional[float]:
    """
    Calculate Corsi For Percentage.
    
    CF% = CF / (CF + CA) * 100
    
    Args:
        cf: Corsi For
        ca: Corsi Against
        
    Returns:
        CF% as float (0-100), or None if CF + CA = 0
    """
    total = cf + ca
    if total == 0:
        return None
    return (cf / total) * 100.0


def calculate_ff_pct(ff: int, fa: int) -> Optional[float]:
    """
    Calculate Fenwick For Percentage.
    
    FF% = FF / (FF + FA) * 100
    
    Args:
        ff: Fenwick For
        fa: Fenwick Against
        
    Returns:
        FF% as float (0-100), or None if FF + FA = 0
    """
    total = ff + fa
    if total == 0:
        return None
    return (ff / total) * 100.0
