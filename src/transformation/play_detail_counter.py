"""
=============================================================================
PLAY DETAIL COUNTER WITH LINKED EVENT DEDUPLICATION
=============================================================================
File: src/transformation/play_detail_counter.py

PURPOSE:
    Count play_detail1 and play_detail_2 values for box scores, properly
    handling linked events to avoid double-counting.

PROBLEM:
    When events are linked (via linked_event_index), the same play_detail
    may appear on multiple events in the chain. For example:
    
    Event 1 (Pass): player 9, play_detail1 = "PassIntercepted"
    Event 2 (Turnover): player 9, play_detail1 = "PassIntercepted"
    
    Both events are linked. Without deduplication, "PassIntercepted" would
    count as 2 for player 9, but it should only count as 1.

SOLUTION:
    1. Group events by linked_event_index (or treat unlinked as their own group)
    2. For each player in each chain, get DISTINCT play_detail values
    3. Count distinct values only

USAGE:
    from src.transformation.play_detail_counter import PlayDetailCounter
    
    counter = PlayDetailCounter(event_players_df, events_df)
    counts = counter.count_play_details_for_player(player_game_number=45)
    # Returns: {'StickCheck': 3, 'Deke': 2, ...}

=============================================================================
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from collections import defaultdict


class PlayDetailCounter:
    """
    Count play details with proper linked event deduplication.
    
    This class ensures that when the same play_detail appears on multiple
    events within a linked chain, it's only counted once per player.
    
    Attributes:
        event_players_df: DataFrame with event-player associations
        events_df: DataFrame with event data (including linked_event_index)
    """
    
    def __init__(self, event_players_df: pd.DataFrame, events_df: pd.DataFrame):
        """
        Initialize the counter.
        
        Args:
            event_players_df: Must have columns:
                - event_index
                - player_game_number
                - play_detail1
                - play_detail_2 (optional)
            events_df: Must have columns:
                - event_index
                - linked_event_index (can be NaN for unlinked events)
        """
        self.event_players_df = event_players_df.copy()
        self.events_df = events_df.copy()
        
        # Merge linked_event_index into event_players
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare data by merging linked_event_index."""
        # Get linked_event_index for each event
        linked_lookup = self.events_df[['event_index', 'linked_event_index']].drop_duplicates()
        
        # Merge into event_players
        self.event_players_df = self.event_players_df.merge(
            linked_lookup, 
            on='event_index', 
            how='left'
        )
        
        # For unlinked events, use event_index as the "chain" identifier
        # This ensures each unlinked event is its own group
        self.event_players_df['chain_id'] = self.event_players_df.apply(
            lambda r: r['linked_event_index'] if pd.notna(r['linked_event_index']) 
                      else f"single_{r['event_index']}",
            axis=1
        )
    
    def count_play_details_for_player(self, player_game_number: int) -> Dict[str, int]:
        """
        Count distinct play_detail values for a specific player.
        
        This counts each play_detail only once per linked chain.
        
        Args:
            player_game_number: Player to count for
        
        Returns:
            Dictionary mapping play_detail to count
        """
        # Filter to this player
        player_data = self.event_players_df[
            self.event_players_df['player_game_number'] == player_game_number
        ]
        
        counts = defaultdict(int)
        
        # Count play_detail1 (distinct per chain)
        if 'play_detail1' in player_data.columns:
            # Group by chain_id and get distinct play_detail1 values
            distinct_pd1 = player_data[player_data['play_detail1'].notna()].groupby(
                ['chain_id', 'play_detail1']
            ).size().reset_index(name='_count')
            
            # Count each distinct (chain, play_detail) as 1
            for detail in distinct_pd1['play_detail1'].unique():
                counts[detail] = len(distinct_pd1[distinct_pd1['play_detail1'] == detail])
        
        # Count play_detail_2 (distinct per chain)
        if 'play_detail_2' in player_data.columns:
            distinct_pd2 = player_data[player_data['play_detail_2'].notna()].groupby(
                ['chain_id', 'play_detail_2']
            ).size().reset_index(name='_count')
            
            for detail in distinct_pd2['play_detail_2'].unique():
                # Add to existing count (play_detail_2 might have different values)
                counts[f"{detail}_detail2"] = len(distinct_pd2[distinct_pd2['play_detail_2'] == detail])
        
        return dict(counts)
    
    def count_all_players(self) -> pd.DataFrame:
        """
        Count play details for all players.
        
        Returns:
            DataFrame with player_game_number and columns for each play_detail
        """
        players = self.event_players_df['player_game_number'].dropna().unique()
        
        results = []
        for player in players:
            counts = self.count_play_details_for_player(player)
            counts['player_game_number'] = player
            results.append(counts)
        
        return pd.DataFrame(results).fillna(0)
    
    def get_deduplicated_counts(self, play_details: List[str]) -> pd.DataFrame:
        """
        Get deduplicated counts for specific play_detail values.
        
        Args:
            play_details: List of play_detail1 values to count
        
        Returns:
            DataFrame with player_game_number and count columns
        """
        results = []
        
        players = self.event_players_df['player_game_number'].dropna().unique()
        
        for player in players:
            player_data = self.event_players_df[
                self.event_players_df['player_game_number'] == player
            ]
            
            row = {'player_game_number': player}
            
            for detail in play_details:
                # Count distinct chains where this player has this play_detail
                if 'play_detail1' in player_data.columns:
                    matching = player_data[player_data['play_detail1'] == detail]
                    # Count unique chains
                    row[detail] = matching['chain_id'].nunique()
                else:
                    row[detail] = 0
            
            results.append(row)
        
        return pd.DataFrame(results)


def count_play_details_deduplicated(event_players_df: pd.DataFrame, 
                                     events_df: pd.DataFrame,
                                     play_details: List[str]) -> pd.DataFrame:
    """
    Convenience function to count play details with deduplication.
    
    Args:
        event_players_df: Event-player data
        events_df: Event data with linked_event_index
        play_details: List of play_detail1 values to count
    
    Returns:
        DataFrame with deduplicated counts per player
    """
    counter = PlayDetailCounter(event_players_df, events_df)
    return counter.get_deduplicated_counts(play_details)
