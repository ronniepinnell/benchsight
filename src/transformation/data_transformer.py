"""
=============================================================================
DATA TRANSFORMER
=============================================================================
File: src/transformation/data_transformer.py

Main transformation logic for converting raw tracking data into star schema.
=============================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from collections import defaultdict

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataTransformer:
    """
    Transform raw tracking data into star schema tables.
    
    This class handles:
    - Event transformation with composite keys
    - Shift transformation with player aggregates
    - Box score generation with micro-stats
    - Linked event deduplication
    - Skill rating integration
    """
    
    def __init__(self, config, blb_tables: Dict[str, pd.DataFrame]):
        """
        Initialize transformer.
        
        Args:
            config: Configuration object
            blb_tables: Dictionary of BLB master tables
        """
        self.config = config
        self.blb_tables = blb_tables
        
        # Build lookups
        self.skill_lookup = {}
        if 'dim_player' in blb_tables:
            self.skill_lookup = blb_tables['dim_player'].set_index('player_id')['current_skill_rating'].to_dict()
        
        self.name_lookup = {}
        if 'dim_player' in blb_tables and 'random_player_full_name' in blb_tables['dim_player'].columns:
            self.name_lookup = blb_tables['dim_player'].set_index('player_id')['random_player_full_name'].to_dict()
        
        logger.info("DataTransformer initialized")
    
    def transform_game(self, game_id: int, events_df: pd.DataFrame, 
                       shifts_df: pd.DataFrame, game_roster: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Transform a complete game.
        
        Args:
            game_id: Game identifier
            events_df: Raw events data
            shifts_df: Raw shifts data
            game_roster: Roster from fact_gameroster
        
        Returns:
            Dictionary with all transformed tables
        """
        logger.info(f"Transforming game {game_id}")
        
        # Clean events
        events_clean = self._clean_events(events_df)
        
        # Build dimension: game players
        dim_game_players = self._build_game_players(game_id, game_roster, events_clean)
        
        # Build fact: events
        fact_events = self._build_fact_events(game_id, events_clean)
        
        # Build fact: event players
        fact_event_players = self._build_fact_event_players(game_id, events_clean)
        
        # Build fact: shifts
        fact_shifts = self._build_fact_shifts(game_id, shifts_df, fact_events)
        
        # Build fact: shift players
        fact_shift_players = self._build_fact_shift_players(game_id, shifts_df)
        
        # Build fact: box score
        fact_box_score = self._build_box_score(
            game_id, dim_game_players, fact_events, fact_event_players,
            fact_shifts, fact_shift_players, events_clean
        )
        
        # Build event chains
        fact_linked_events = self._build_linked_events(game_id, events_clean)
        fact_sequences = self._build_sequences(game_id, events_clean)
        fact_plays = self._build_plays(game_id, events_clean)
        
        return {
            'dim_game_players_tracking': dim_game_players,
            'fact_event_players': fact_events,
            'fact_event_players_tracking': fact_event_players,
            'fact_shifts': fact_shifts,
            'fact_shift_players_tracking': fact_shift_players,
            'fact_box_score_tracking': fact_box_score,
            'fact_linked_events_tracking': fact_linked_events,
            'fact_sequences_tracking': fact_sequences,
            'fact_plays_tracking': fact_plays,
        }
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _safe_key(self, game_id: int, idx) -> Optional[str]:
        """Create safe composite key."""
        if pd.isna(idx):
            return None
        return f"{game_id}_{int(idx)}"
    
    def _clean_events(self, events_df: pd.DataFrame) -> pd.DataFrame:
        """Clean events data by removing underscore columns."""
        underscore_cols = [c for c in events_df.columns if c.endswith('_')]
        return events_df.drop(columns=underscore_cols, errors='ignore')
    
    # =========================================================================
    # DIMENSION BUILDERS
    # =========================================================================
    
    def _build_game_players(self, game_id: int, game_roster: pd.DataFrame,
                            events_clean: pd.DataFrame) -> pd.DataFrame:
        """Build dim_game_players from roster or events."""
        
        if len(game_roster) > 0:
            # Use roster from fact_gameroster
            cols = ['game_id', 'player_game_number', 'player_id', 'player_full_name',
                    'team_name', 'team_venue', 'player_position', 'skill_rating']
            available = [c for c in cols if c in game_roster.columns]
            
            dim = game_roster[available].copy()
            dim = dim.rename(columns={
                'team_name': 'player_team',
                'team_venue': 'player_venue',
                'player_position': 'position'
            })
        else:
            # Build from events
            player_data = events_clean[['player_game_number', 'player_id', 'player_team']].drop_duplicates()
            player_data = player_data[player_data['player_game_number'].notna()]
            
            dim = player_data.copy()
            dim['game_id'] = game_id
            dim['skill_rating'] = dim['player_id'].map(self.skill_lookup).fillna(4.0)
        
        # Create key
        dim['player_game_key'] = dim.apply(
            lambda r: self._safe_key(game_id, r.get('player_game_number')), axis=1
        )
        
        # Add display name
        if 'player_id' in dim.columns:
            dim['display_name'] = dim['player_id'].map(self.name_lookup)
        
        return dim
    
    # =========================================================================
    # FACT BUILDERS
    # =========================================================================
    
    def _build_fact_events(self, game_id: int, events_clean: pd.DataFrame) -> pd.DataFrame:
        """Build fact_events table."""
        
        # Select header columns
        header_cols = [
            'event_index', 'shift_index', 'linked_event_index', 'sequence_index', 'play_index',
            'Type', 'event_detail', 'event_detail_2', 'event_successful',
            'period', 'event_start_min', 'event_start_sec', 
            'time_start_total_seconds', 'time_end_total_seconds', 'duration',
            'event_team_zone'
        ]
        available = [c for c in header_cols if c in events_clean.columns]
        
        fact = events_clean[available].drop_duplicates(subset=['event_index'])
        
        # Add event team
        event_teams = events_clean[events_clean['player_role'] == 'event_team_player_1'][
            ['event_index', 'player_team']
        ].drop_duplicates()
        event_teams = event_teams.rename(columns={'player_team': 'event_team'})
        fact = fact.merge(event_teams, on='event_index', how='left')
        
        # Create keys
        fact['event_key'] = fact['event_index'].apply(lambda x: self._safe_key(game_id, x))
        fact['shift_key'] = fact['shift_index'].apply(lambda x: self._safe_key(game_id, x))
        fact['game_id'] = game_id
        
        # Time bucket
        if 'event_start_min' in fact.columns:
            fact['time_bucket_id'] = fact['event_start_min'].apply(
                lambda m: min(int(m // 5) + 1, 4) if pd.notna(m) else None
            )
        
        # Primary player skill
        primary = events_clean[events_clean['player_role'] == 'event_team_player_1'][
            ['event_index', 'player_game_number', 'player_id']
        ].drop_duplicates(subset=['event_index'])
        primary['event_player_1_skill'] = primary['player_id'].map(self.skill_lookup)
        fact = fact.merge(
            primary[['event_index', 'player_game_number', 'event_player_1_skill']],
            on='event_index', how='left'
        )
        
        # ML features
        fact = fact.sort_values('event_index').reset_index(drop=True)
        fact['prev_event_type'] = fact['Type'].shift(1)
        fact['next_event_type'] = fact['Type'].shift(-1)
        fact['is_goal'] = (fact['event_detail'] == 'Goal_Scored').astype(int)
        
        # Events to next goal
        goal_indices = fact[fact['event_detail'] == 'Goal_Scored']['event_index'].tolist()
        
        def events_to_goal(idx):
            if pd.isna(idx):
                return None
            future = [g for g in goal_indices if g > idx]
            if future:
                return len(fact[(fact['event_index'] > idx) & (fact['event_index'] <= min(future))])
            return None
        
        fact['events_to_next_goal'] = fact['event_index'].apply(events_to_goal)
        fact['is_goal_sequence'] = fact['events_to_next_goal'].apply(
            lambda x: 1 if pd.notna(x) and x <= 5 else 0
        )
        
        return fact
    
    def _build_fact_event_players(self, game_id: int, events_clean: pd.DataFrame) -> pd.DataFrame:
        """Build fact_event_players bridge table."""
        
        cols = ['event_index', 'player_game_number', 'player_id', 'player_team',
                'player_role', 'role_number', 'play_detail1', 'play_detail_2', 'play_detail_successful']
        available = [c for c in cols if c in events_clean.columns]
        
        fact = events_clean[available].copy()
        fact = fact[fact['player_game_number'].notna()]
        
        # Keys
        fact['event_key'] = fact['event_index'].apply(lambda x: self._safe_key(game_id, x))
        fact['event_player_key'] = fact.apply(
            lambda r: f"{game_id}_{int(r['event_index'])}_{int(r['player_game_number'])}"
            if pd.notna(r['event_index']) and pd.notna(r['player_game_number']) else None,
            axis=1
        )
        fact['player_game_key'] = fact['player_game_number'].apply(lambda x: self._safe_key(game_id, x))
        fact['game_id'] = game_id
        
        # Skill and flags
        fact['skill_rating'] = fact['player_id'].map(self.skill_lookup)
        fact['is_primary_player'] = (fact['player_role'] == 'event_team_player_1').astype(int)
        fact['is_event_team'] = fact['player_role'].str.contains('event_team', na=False).astype(int)
        fact['is_opp_team'] = fact['player_role'].str.contains('opp_team', na=False).astype(int)
        
        return fact
    
    def _build_fact_shifts(self, game_id: int, shifts_df: pd.DataFrame,
                           fact_events: pd.DataFrame) -> pd.DataFrame:
        """Build fact_shifts with per-shift aggregates."""
        
        cols = ['shift_index', 'Period', 'shift_start_total_seconds', 'shift_end_total_seconds',
                'shift_duration', 'shift_start_type', 'shift_stop_type',
                'situation', 'strength', 'home_team_strength', 'away_team_strength',
                'home_goals', 'away_goals', 'home_team_plus', 'home_team_minus',
                'away_team_plus', 'away_team_minus']
        available = [c for c in cols if c in shifts_df.columns]
        
        fact = shifts_df[available].copy()
        fact['shift_key'] = fact['shift_index'].apply(lambda x: self._safe_key(game_id, x))
        fact['game_id'] = game_id
        
        # Per-shift event counts
        for shift_idx in fact['shift_index'].unique():
            shift_events = fact_events[fact_events['shift_index'] == shift_idx]
            mask = fact['shift_index'] == shift_idx
            
            fact.loc[mask, 'shift_shots'] = len(shift_events[shift_events['Type'] == 'Shot'])
            fact.loc[mask, 'shift_passes'] = len(shift_events[shift_events['Type'] == 'Pass'])
            fact.loc[mask, 'shift_turnovers'] = len(shift_events[shift_events['Type'] == 'Turnover'])
            fact.loc[mask, 'shift_goals'] = len(shift_events[shift_events['event_detail'] == 'Goal_Scored'])
        
        return fact
    
    def _build_fact_shift_players(self, game_id: int, shifts_df: pd.DataFrame) -> pd.DataFrame:
        """Build fact_shift_players bridge table."""
        
        # Player columns
        player_cols = [c for c in shifts_df.columns 
                       if any(x in c for x in ['forward', 'defense', 'goalie']) 
                       and 'strength' not in c]
        
        id_vars = ['shift_index', 'shift_duration', 'home_team_plus', 'home_team_minus',
                   'away_team_plus', 'away_team_minus']
        id_vars = [c for c in id_vars if c in shifts_df.columns]
        
        fact = shifts_df[id_vars + player_cols].melt(
            id_vars=id_vars,
            value_vars=player_cols,
            var_name='position_slot',
            value_name='player_game_number'
        )
        
        fact = fact[fact['player_game_number'].notna()]
        
        # Venue and position
        fact['player_venue'] = fact['position_slot'].apply(
            lambda x: 'home' if x.startswith('home') else 'away'
        )
        fact['position_type'] = fact['position_slot'].apply(
            lambda x: x.split('_')[1] if '_' in x else 'unknown'
        )
        
        # Plus/minus
        def calc_pm(row):
            if row['player_venue'] == 'home':
                return int(row.get('home_team_plus', 0) or 0) + int(row.get('home_team_minus', 0) or 0)
            else:
                return int(row.get('away_team_plus', 0) or 0) + int(row.get('away_team_minus', 0) or 0)
        
        fact['plus_minus'] = fact.apply(calc_pm, axis=1)
        
        # Keys
        fact['shift_key'] = fact['shift_index'].apply(lambda x: self._safe_key(game_id, x))
        fact['shift_player_key'] = fact.apply(
            lambda r: f"{game_id}_{int(r['shift_index'])}_{int(r['player_game_number'])}"
            if pd.notna(r['shift_index']) and pd.notna(r['player_game_number']) else None,
            axis=1
        )
        fact['player_game_key'] = fact['player_game_number'].apply(lambda x: self._safe_key(game_id, x))
        fact['game_id'] = game_id
        
        return fact
    
    def _build_box_score(self, game_id: int, dim_game_players: pd.DataFrame,
                         fact_events: pd.DataFrame, fact_event_players: pd.DataFrame,
                         fact_shifts: pd.DataFrame, fact_shift_players: pd.DataFrame,
                         events_clean: pd.DataFrame) -> pd.DataFrame:
        """Build comprehensive box score."""
        
        # Start with player base
        box = dim_game_players.copy()
        box['game_id'] = game_id
        
        # Primary events for counting
        primary = fact_event_players[fact_event_players['is_primary_player'] == 1].merge(
            fact_events[['event_index', 'Type', 'event_detail', 'event_successful', 'duration']],
            on='event_index'
        )
        
        # ICE TIME
        toi = fact_shift_players.groupby('player_game_number').agg({
            'shift_duration': 'sum',
            'plus_minus': 'sum',
            'shift_index': 'count'
        }).reset_index()
        toi.columns = ['player_game_number', 'toi_seconds', 'plus_minus', 'shifts']
        box = box.merge(toi, on='player_game_number', how='left')
        box['toi_seconds'] = box['toi_seconds'].fillna(0)
        box['toi_formatted'] = box['toi_seconds'].apply(lambda x: f"{int(x//60)}:{int(x%60):02d}")
        
        # SCORING
        goals = primary[primary['event_detail'] == 'Goal_Scored'].groupby('player_game_number').size()
        box['goals'] = box['player_game_number'].map(goals).fillna(0).astype(int)
        
        # Assists - use str.contains to catch variations like 'AssistPrimary' or 'OffensivePlay_Pass-AssistPrimary'
        assists_p = fact_event_players[fact_event_players['play_detail1'].astype(str).str.contains('AssistPrimary', na=False)].groupby('player_game_number').size()
        box['assists_primary'] = box['player_game_number'].map(assists_p).fillna(0).astype(int)
        
        assists_s = fact_event_players[fact_event_players['play_detail1'].astype(str).str.contains('AssistSecondary', na=False)].groupby('player_game_number').size()
        box['assists_secondary'] = box['player_game_number'].map(assists_s).fillna(0).astype(int)
        
        box['assists'] = box['assists_primary'] + box['assists_secondary']
        box['points'] = box['goals'] + box['assists']
        
        # SHOOTING
        shots = primary[primary['Type'] == 'Shot'].groupby('player_game_number').size()
        box['shots'] = box['player_game_number'].map(shots).fillna(0).astype(int)
        
        sog_details = ['Shot_OnNetSaved', 'Shot_Goal', 'Shot_TippedOnNetSaved']
        sog = primary[primary['event_detail'].isin(sog_details)].groupby('player_game_number').size()
        box['shots_on_goal'] = box['player_game_number'].map(sog).fillna(0).astype(int)
        
        box['shooting_pct'] = np.where(
            box['shots_on_goal'] > 0,
            (box['goals'] / box['shots_on_goal'] * 100).round(1),
            0
        )
        
        # PASSING
        passes = primary[primary['Type'] == 'Pass'].groupby('player_game_number').size()
        box['passes'] = box['player_game_number'].map(passes).fillna(0).astype(int)
        
        pass_comp = primary[primary['event_detail'] == 'Pass_Completed'].groupby('player_game_number').size()
        box['passes_completed'] = box['player_game_number'].map(pass_comp).fillna(0).astype(int)
        
        box['pass_pct'] = np.where(
            box['passes'] > 0,
            (box['passes_completed'] / box['passes'] * 100).round(1),
            0
        )
        
        # TURNOVERS
        giveaways = primary[primary['event_detail'] == 'Turnover_Giveaway'].groupby('player_game_number').size()
        box['giveaways'] = box['player_game_number'].map(giveaways).fillna(0).astype(int)
        
        takeaways = primary[primary['event_detail'] == 'Turnover_Takeaway'].groupby('player_game_number').size()
        box['takeaways'] = box['player_game_number'].map(takeaways).fillna(0).astype(int)
        
        box['turnover_differential'] = box['takeaways'] - box['giveaways']
        
        # FACEOFFS
        faceoffs = primary[primary['Type'] == 'Faceoff'].groupby('player_game_number').size()
        box['faceoffs'] = box['player_game_number'].map(faceoffs).fillna(0).astype(int)
        
        fo_wins = primary[(primary['Type'] == 'Faceoff') & (primary['event_successful'] == 's')].groupby('player_game_number').size()
        box['faceoff_wins'] = box['player_game_number'].map(fo_wins).fillna(0).astype(int)
        
        box['faceoff_pct'] = np.where(
            box['faceoffs'] > 0,
            (box['faceoff_wins'] / box['faceoffs'] * 100).round(1),
            0
        )
        
        # ZONE PLAY
        zone_events = primary[primary['Type'] == 'Zone_Entry_Exit']
        entries = zone_events[zone_events['event_detail'].str.contains('Entry', na=False)].groupby('player_game_number').size()
        box['zone_entries'] = box['player_game_number'].map(entries).fillna(0).astype(int)
        
        exits = zone_events[zone_events['event_detail'].str.contains('Exit', na=False)].groupby('player_game_number').size()
        box['zone_exits'] = box['player_game_number'].map(exits).fillna(0).astype(int)
        
        # MICRO-STATS (with deduplication)
        box = self._add_deduplicated_play_details(box, fact_event_players, fact_events)
        
        # SAVES (goalies)
        saves = primary[primary['Type'] == 'Save'].groupby('player_game_number').size()
        box['saves'] = box['player_game_number'].map(saves).fillna(0).astype(int)
        
        # PER-60 RATES
        for stat in ['goals', 'assists', 'points', 'shots']:
            box[f'{stat}_per_60'] = np.where(
                box['toi_seconds'] > 0,
                (box[stat] / (box['toi_seconds'] / 3600)).round(2),
                0
            )
        
        # Mark as tracked
        box['is_tracked'] = True
        
        box = box.fillna(0)
        return box.sort_values(['player_team', 'player_game_number']).reset_index(drop=True)
    
    def _add_deduplicated_play_details(self, box: pd.DataFrame, 
                                        fact_event_players: pd.DataFrame,
                                        fact_events: pd.DataFrame) -> pd.DataFrame:
        """Add play_detail counts with linked event deduplication."""
        
        # Merge linked_event_index into event_players
        ep = fact_event_players.merge(
            fact_events[['event_index', 'linked_event_index']].drop_duplicates(),
            on='event_index',
            how='left'
        )
        
        # Create chain ID
        ep['chain_id'] = ep.apply(
            lambda r: r['linked_event_index'] if pd.notna(r['linked_event_index'])
                      else f"single_{r['event_index']}",
            axis=1
        )
        
        # Play details to count
        play_details = [
            'StickCheck', 'PokeCheck', 'BlockedShot', 'Backcheck', 'InShotPassLane',
            'Deke', 'BeatDeke', 'Screen', 'DumpAndChase', 'Tip', 'OneTimer',
            'PuckRecovery', 'BoardBattleWin', 'BoardBattleLoss', 'SecondTouch'
        ]
        
        for detail in play_details:
            if 'play_detail1' not in ep.columns:
                continue
            
            # Count distinct chains per player
            matching = ep[ep['play_detail1'] == detail]
            counts = matching.groupby('player_game_number')['chain_id'].nunique()
            
            col_name = detail.lower()
            box[col_name] = box['player_game_number'].map(counts).fillna(0).astype(int)
        
        return box
    
    # =========================================================================
    # EVENT CHAIN BUILDERS
    # =========================================================================
    
    def _build_linked_events(self, game_id: int, events_clean: pd.DataFrame) -> pd.DataFrame:
        """Build fact_linked_events for shot sequences etc."""
        
        linked = events_clean[events_clean['linked_event_index'].notna()]
        
        if len(linked) == 0:
            return pd.DataFrame()
        
        chains = linked.groupby('linked_event_index').agg({
            'event_index': ['min', 'max', 'count', list],
            'Type': lambda x: list(x.unique())
        }).reset_index()
        
        chains.columns = ['linked_event_index', 'first_event', 'last_event', 
                          'event_count', 'event_indices', 'event_types']
        
        def get_chain_type(types):
            if 'Shot' in types and 'Save' in types:
                return 'shot_sequence'
            elif 'Zone_Entry_Exit' in types:
                return 'zone_transition'
            return 'other'
        
        chains['chain_type'] = chains['event_types'].apply(get_chain_type)
        chains['chain_id'] = chains['linked_event_index'].apply(
            lambda x: f"{game_id}_link_{int(x)}" if pd.notna(x) else None
        )
        chains['game_id'] = game_id
        chains['event_indices'] = chains['event_indices'].apply(str)
        chains['event_types'] = chains['event_types'].apply(str)
        
        return chains
    
    def _build_sequences(self, game_id: int, events_clean: pd.DataFrame) -> pd.DataFrame:
        """Build fact_sequences for possession sequences."""
        
        if 'sequence_index' not in events_clean.columns:
            return pd.DataFrame()
        
        seq_events = events_clean[events_clean['sequence_index'].notna()]
        
        if len(seq_events) == 0:
            return pd.DataFrame()
        
        seqs = seq_events.groupby('sequence_index').agg({
            'event_index': ['min', 'max', 'count'],
            'Type': lambda x: list(x),
            'shift_index': 'first'
        }).reset_index()
        
        seqs.columns = ['sequence_index', 'first_event', 'last_event', 
                        'event_count', 'event_types', 'shift_index']
        
        seqs['sequence_key'] = seqs['sequence_index'].apply(
            lambda x: f"{game_id}_seq_{int(x)}" if pd.notna(x) else None
        )
        seqs['game_id'] = game_id
        seqs['event_types'] = seqs['event_types'].apply(str)
        
        return seqs
    
    def _build_plays(self, game_id: int, events_clean: pd.DataFrame) -> pd.DataFrame:
        """Build fact_plays for play-level groupings."""
        
        if 'play_index' not in events_clean.columns:
            return pd.DataFrame()
        
        play_events = events_clean[events_clean['play_index'].notna()]
        
        if len(play_events) == 0:
            return pd.DataFrame()
        
        plays = play_events.groupby('play_index').agg({
            'event_index': ['min', 'max', 'count'],
            'Type': lambda x: list(x)
        }).reset_index()
        
        plays.columns = ['play_index', 'first_event', 'last_event', 
                         'event_count', 'event_types']
        
        plays['play_key'] = plays['play_index'].apply(
            lambda x: f"{game_id}_play_{int(x)}" if pd.notna(x) else None
        )
        plays['game_id'] = game_id
        plays['event_types'] = plays['event_types'].apply(str)
        
        return plays
