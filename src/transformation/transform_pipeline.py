"""
=============================================================================
TRANSFORMATION PIPELINE
=============================================================================
File: src/transformation/transform_pipeline.py

PURPOSE:
    Orchestrate all data transformations:
    1. Events → fact_events, fact_event_players
    2. Shifts → fact_shifts, fact_shift_players
    3. Generate comprehensive box scores
    4. Build event chains (linked, sequence, play)

STAR SCHEMA DESIGN:
    Dimension Tables:
    - dim_game_players: Players in this game
    
    Fact Tables:
    - fact_events: Event headers
    - fact_event_players: Player-event bridge
    - fact_shifts: Shift headers
    - fact_shift_players: Player-shift bridge
    - fact_box_score: Aggregated player stats
    - fact_linked_events: Shot→Save→Rebound chains
    - fact_sequences: Zone entry→shot chains
    - fact_plays: Play-level chains
=============================================================================
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)

class TransformPipeline:
    """Main transformation pipeline."""
    
    def __init__(self, raw_data: Dict, game_id: int, blb_data: Dict, config):
        """Initialize transformer."""
        self.events_df = raw_data.get('events', pd.DataFrame())
        self.shifts_df = raw_data.get('shifts', pd.DataFrame())
        self.game_id = game_id
        self.blb_data = blb_data
        self.config = config
        
        # Get skill lookup
        self.skill_lookup = {}
        if 'dim_player' in blb_data:
            self.skill_lookup = blb_data['dim_player'].set_index('player_id')['current_skill_rating'].to_dict()
        
        # Get game metadata
        self.home_team = self.shifts_df['home_team'].iloc[0] if len(self.shifts_df) > 0 else ''
        self.away_team = self.shifts_df['away_team'].iloc[0] if len(self.shifts_df) > 0 else ''
        
        logger.info(f"TransformPipeline initialized for game {game_id}")
    
    def transform_all(self) -> Dict[str, pd.DataFrame]:
        """Run all transformations."""
        results = {}
        
        # 1. Transform events
        print("    → Transforming events...")
        results['dim_game_players'] = self._create_dim_game_players()
        results['fact_events'] = self._create_fact_events()
        results['fact_event_players'] = self._create_fact_event_players()
        
        # 2. Transform shifts
        print("    → Transforming shifts...")
        results['fact_shifts'] = self._create_fact_shifts()
        results['fact_shift_players'] = self._create_fact_shift_players()
        
        # 3. Build event chains
        print("    → Building event chains...")
        results['fact_linked_events'] = self._create_linked_events()
        results['fact_sequences'] = self._create_sequences()
        results['fact_plays'] = self._create_plays()
        
        # 4. Build box scores
        print("    → Building box scores...")
        results['fact_box_score'] = self._create_box_score(results)
        
        logger.info(f"Transformation complete: {len(results)} tables")
        return results
    
    def _create_dim_game_players(self) -> pd.DataFrame:
        """Create player dimension table."""
        # Extract unique players from events
        players = self.events_df[['player_game_number', 'player_id', 'player_team']].drop_duplicates()
        players = players[players['player_game_number'].notna() & (players['player_game_number'] != 0)]
        
        # Add venue
        players['player_venue'] = players['player_team'].apply(
            lambda x: 'home' if x == self.home_team else 'away'
        )
        
        # Add position from shifts
        positions = self._get_player_positions()
        players = players.merge(positions, on='player_game_number', how='left')
        
        # Add skill rating
        players['skill_rating'] = players['player_id'].map(self.skill_lookup)
        players['skill_rating'] = players['skill_rating'].fillna(self.config.processing.default_skill_rating)
        
        # Add keys
        players['player_game_key'] = players['player_game_number'].apply(
            lambda x: f"{self.game_id}_{int(x)}"
        )
        players['game_id'] = self.game_id
        
        # Add display name if available
        if 'dim_player' in self.blb_data:
            name_lookup = self.blb_data['dim_player'].set_index('player_id')[['player_full_name', 'random_player_full_name']].to_dict('index')
            players['player_full_name'] = players['player_id'].map(lambda x: name_lookup.get(x, {}).get('player_full_name', ''))
            players['display_name'] = players['player_id'].map(lambda x: name_lookup.get(x, {}).get('random_player_full_name', ''))
        
        return players.reset_index(drop=True)
    
    def _get_player_positions(self) -> pd.DataFrame:
        """Extract player positions from shifts."""
        positions = []
        
        pos_cols = ['home_forward_1', 'home_forward_2', 'home_forward_3',
                   'home_defense_1', 'home_defense_2', 'home_goalie',
                   'away_forward_1', 'away_forward_2', 'away_forward_3',
                   'away_defense_1', 'away_defense_2', 'away_goalie']
        
        for col in pos_cols:
            if col in self.shifts_df.columns:
                pos = 'forward' if 'forward' in col else ('defense' if 'defense' in col else 'goalie')
                for p in self.shifts_df[col].dropna().unique():
                    positions.append({'player_game_number': p, 'position': pos})
        
        if not positions:
            return pd.DataFrame(columns=['player_game_number', 'position'])
        
        pos_df = pd.DataFrame(positions)
        return pos_df.groupby('player_game_number')['position'].agg(
            lambda x: x.value_counts().index[0]
        ).reset_index()
    
    def _create_fact_events(self) -> pd.DataFrame:
        """Create events fact table."""
        # Remove underscore columns
        events = self.events_df.copy()
        underscore_cols = [c for c in events.columns if c.endswith('_')]
        events = events.drop(columns=underscore_cols, errors='ignore')
        
        # Get header columns
        header_cols = [
            'event_index', 'shift_index', 'linked_event_index', 'sequence_index', 'play_index',
            'Type', 'event_detail', 'event_detail_2', 'event_successful',
            'period', 'event_start_min', 'event_start_sec', 'event_end_min', 'event_end_sec',
            'time_start_total_seconds', 'time_end_total_seconds', 'duration',
            'event_running_start', 'event_running_end',
            'event_team_zone', 'home_team_zone', 'away_team_zone',
            'pressured_pressurer', 'side_of_puck'
        ]
        
        available_cols = [c for c in header_cols if c in events.columns]
        fact_events = events[available_cols].drop_duplicates(subset=['event_index'])
        
        # Add event team
        event_teams = events[events['player_role'] == 'event_team_player_1'][
            ['event_index', 'player_team']
        ].drop_duplicates().rename(columns={'player_team': 'event_team'})
        fact_events = fact_events.merge(event_teams, on='event_index', how='left')
        
        # Add keys
        fact_events['event_key'] = fact_events['event_index'].apply(lambda x: f"{self.game_id}_{int(x)}")
        fact_events['shift_key'] = fact_events['shift_index'].apply(
            lambda x: f"{self.game_id}_{int(x)}" if pd.notna(x) else None
        )
        fact_events['game_id'] = self.game_id
        
        # Add skill columns
        fact_events = self._add_event_skill_columns(fact_events)
        
        # Add ML features
        fact_events = self._add_ml_features(fact_events)
        
        return fact_events.sort_values('event_index').reset_index(drop=True)
    
    def _add_event_skill_columns(self, events: pd.DataFrame) -> pd.DataFrame:
        """Add skill context to events."""
        # Get primary players
        primary = self.events_df[self.events_df['player_role'] == 'event_team_player_1'][
            ['event_index', 'player_game_number', 'player_id']
        ].drop_duplicates(subset=['event_index'])
        primary['event_player_1_skill'] = primary['player_id'].map(self.skill_lookup)
        
        # Get opponent players
        opp = self.events_df[self.events_df['player_role'] == 'opp_team_player_1'][
            ['event_index', 'player_game_number', 'player_id']
        ].drop_duplicates(subset=['event_index'])
        opp = opp.rename(columns={
            'player_game_number': 'opp_player_1_number',
            'player_id': 'opp_player_1_id'
        })
        opp['opp_player_1_skill'] = opp['opp_player_1_id'].map(self.skill_lookup)
        
        events = events.merge(
            primary[['event_index', 'player_game_number', 'event_player_1_skill']],
            on='event_index', how='left'
        )
        events = events.merge(
            opp[['event_index', 'opp_player_1_number', 'opp_player_1_skill']],
            on='event_index', how='left'
        )
        
        # Skill differential
        events['player_skill_differential'] = events['event_player_1_skill'] - events['opp_player_1_skill']
        
        return events
    
    def _add_ml_features(self, events: pd.DataFrame) -> pd.DataFrame:
        """Add ML features for prediction models."""
        events = events.sort_values('event_index').reset_index(drop=True)
        
        # Lead/lag events
        events['prev_event_type'] = events['Type'].shift(1)
        events['next_event_type'] = events['Type'].shift(-1)
        events['prev_event_detail'] = events['event_detail'].shift(1)
        events['next_event_detail'] = events['event_detail'].shift(-1)
        
        # Time deltas
        events['time_since_prev'] = (
            events['time_start_total_seconds'] - events['time_start_total_seconds'].shift(1)
        ).abs()
        
        # Goal proximity
        goal_indices = events[events['event_detail'] == 'Goal_Scored']['event_index'].tolist()
        events['is_goal'] = (events['event_detail'] == 'Goal_Scored').astype(int)
        
        def events_to_next_goal(idx):
            future = [g for g in goal_indices if g > idx]
            if future:
                return len(events[(events['event_index'] > idx) & (events['event_index'] <= min(future))])
            return None
        
        events['events_to_next_goal'] = events['event_index'].apply(events_to_next_goal)
        events['is_goal_sequence'] = (events['events_to_next_goal'] <= 5).fillna(False).astype(int)
        
        # Event type counts
        for etype in ['Shot', 'Pass', 'Faceoff', 'Turnover']:
            col = f"{etype.lower()}_number"
            events[col] = None
            mask = events['Type'] == etype
            events.loc[mask, col] = range(1, mask.sum() + 1)
        
        return events
    
    def _create_fact_event_players(self) -> pd.DataFrame:
        """Create event-player bridge table."""
        cols = [
            'event_index', 'player_game_number', 'player_id', 'player_team',
            'player_role', 'role_number',
            'play_detail1', 'play_detail_2', 'play_detail_successful'
        ]
        
        available = [c for c in cols if c in self.events_df.columns]
        event_players = self.events_df[available].copy()
        event_players = event_players[event_players['player_game_number'].notna()]
        
        # Add keys
        event_players['event_key'] = event_players['event_index'].apply(lambda x: f"{self.game_id}_{int(x)}")
        event_players['event_player_key'] = event_players.apply(
            lambda r: f"{self.game_id}_{int(r['event_index'])}_{int(r['player_game_number'])}", axis=1
        )
        event_players['player_game_key'] = event_players['player_game_number'].apply(
            lambda x: f"{self.game_id}_{int(x)}"
        )
        event_players['game_id'] = self.game_id
        
        # Add skill
        event_players['skill_rating'] = event_players['player_id'].map(self.skill_lookup)
        
        # Add flags
        event_players['is_primary_player'] = (event_players['player_role'] == 'event_team_player_1').astype(int)
        event_players['is_event_team'] = event_players['player_role'].str.contains('event_team', na=False).astype(int)
        event_players['is_opp_team'] = event_players['player_role'].str.contains('opp_team', na=False).astype(int)
        
        return event_players.reset_index(drop=True)
    
    def _create_fact_shifts(self) -> pd.DataFrame:
        """Create shifts fact table."""
        cols = [
            'shift_index', 'Period',
            'shift_start_min', 'shift_start_sec', 'shift_end_min', 'shift_end_sec',
            'shift_start_total_seconds', 'shift_end_total_seconds', 'shift_duration',
            'shift_start_running_time', 'shift_end_running_time',
            'shift_start_type', 'shift_stop_type', 'stoppage_time',
            'situation', 'strength',
            'home_team_strength', 'away_team_strength',
            'home_team_en', 'away_team_en',
            'home_team_pk', 'home_team_pp', 'away_team_pk', 'away_team_pp',
            'home_ozone_start', 'home_ozone_end', 'home_dzone_start', 'home_dzone_end',
            'home_goals', 'away_goals',
            'home_team_plus', 'home_team_minus', 'away_team_plus', 'away_team_minus'
        ]
        
        available = [c for c in cols if c in self.shifts_df.columns]
        fact_shifts = self.shifts_df[available].copy()
        
        # Add keys
        fact_shifts['shift_key'] = fact_shifts['shift_index'].apply(lambda x: f"{self.game_id}_{int(x)}")
        fact_shifts['game_id'] = self.game_id
        
        # Add skill aggregates per shift
        fact_shifts = self._add_shift_skill_aggregates(fact_shifts)
        
        return fact_shifts.reset_index(drop=True)
    
    def _add_shift_skill_aggregates(self, shifts: pd.DataFrame) -> pd.DataFrame:
        """Add team skill aggregates to shifts."""
        # Get player skill lookup by game number
        player_skills = self.events_df[['player_game_number', 'player_id']].drop_duplicates()
        player_skills['skill'] = player_skills['player_id'].map(self.skill_lookup)
        player_skills['skill'] = player_skills['skill'].fillna(4)
        skill_by_number = player_skills.set_index('player_game_number')['skill'].to_dict()
        
        home_cols = ['home_forward_1', 'home_forward_2', 'home_forward_3', 'home_defense_1', 'home_defense_2', 'home_goalie']
        away_cols = ['away_forward_1', 'away_forward_2', 'away_forward_3', 'away_defense_1', 'away_defense_2', 'away_goalie']
        
        def calc_team_skill(row, cols):
            players = [row.get(c) for c in cols if c in row.index and pd.notna(row.get(c))]
            skills = [skill_by_number.get(p, 4) for p in players]
            return np.mean(skills) if skills else 4
        
        shifts['home_skill_avg'] = shifts.apply(lambda r: calc_team_skill(r, home_cols), axis=1)
        shifts['away_skill_avg'] = shifts.apply(lambda r: calc_team_skill(r, away_cols), axis=1)
        shifts['skill_differential'] = shifts['home_skill_avg'] - shifts['away_skill_avg']
        
        return shifts
    
    def _create_fact_shift_players(self) -> pd.DataFrame:
        """Create shift-player bridge table."""
        player_cols = [c for c in self.shifts_df.columns if any(x in c for x in 
                      ['forward', 'defense', 'goalie']) and 'strength' not in c]
        
        id_vars = ['shift_index', 'shift_duration', 
                   'home_team_plus', 'home_team_minus', 'away_team_plus', 'away_team_minus']
        id_vars = [c for c in id_vars if c in self.shifts_df.columns]
        
        shift_players = self.shifts_df[id_vars + player_cols].melt(
            id_vars=id_vars,
            value_vars=player_cols,
            var_name='position_slot',
            value_name='player_game_number'
        )
        
        shift_players = shift_players[shift_players['player_game_number'].notna()]
        
        # Add venue and position
        shift_players['player_venue'] = shift_players['position_slot'].apply(
            lambda x: 'home' if x.startswith('home') else 'away'
        )
        shift_players['position_type'] = shift_players['position_slot'].apply(
            lambda x: x.split('_')[1] if '_' in x else 'unknown'
        )
        
        # Add plus/minus
        shift_players['plus_minus'] = shift_players.apply(
            lambda r: (r.get('home_team_plus', 0) or 0) + (r.get('home_team_minus', 0) or 0)
                     if r['player_venue'] == 'home'
                     else (r.get('away_team_plus', 0) or 0) + (r.get('away_team_minus', 0) or 0),
            axis=1
        )
        
        # Add keys
        shift_players['shift_key'] = shift_players['shift_index'].apply(lambda x: f"{self.game_id}_{int(x)}")
        shift_players['shift_player_key'] = shift_players.apply(
            lambda r: f"{self.game_id}_{int(r['shift_index'])}_{int(r['player_game_number'])}", axis=1
        )
        shift_players['player_game_key'] = shift_players['player_game_number'].apply(
            lambda x: f"{self.game_id}_{int(x)}"
        )
        shift_players['game_id'] = self.game_id
        
        # Add skill
        player_skills = self.events_df[['player_game_number', 'player_id']].drop_duplicates()
        player_skills['skill_rating'] = player_skills['player_id'].map(self.skill_lookup)
        shift_players = shift_players.merge(
            player_skills[['player_game_number', 'skill_rating']],
            on='player_game_number', how='left'
        )
        
        return shift_players.reset_index(drop=True)
    
    def _create_linked_events(self) -> pd.DataFrame:
        """Create linked events chain table (shot→save→rebound)."""
        events = self.events_df[self.events_df['linked_event_index'].notna()].copy()
        
        chains = events.groupby('linked_event_index').agg({
            'event_index': ['min', 'max', 'count', list],
            'Type': lambda x: list(x.unique()),
            'event_detail': lambda x: list(x.unique())
        }).reset_index()
        
        chains.columns = ['linked_event_index', 'first_event', 'last_event', 
                         'event_count', 'event_indices', 'event_types', 'event_details']
        
        # Add chain type
        def get_chain_type(types):
            if 'Shot' in types and 'Save' in types:
                return 'shot_sequence'
            elif 'Pass' in types and 'Turnover' in types:
                return 'turnover_sequence'
            elif 'Zone_Entry_Exit' in types:
                return 'zone_transition'
            return 'other'
        
        chains['chain_type'] = chains['event_types'].apply(get_chain_type)
        chains['chain_id'] = chains['linked_event_index'].apply(lambda x: f"{self.game_id}_link_{int(x)}")
        chains['game_id'] = self.game_id
        
        # Convert lists to strings
        chains['event_indices'] = chains['event_indices'].apply(str)
        chains['event_types'] = chains['event_types'].apply(str)
        chains['event_details'] = chains['event_details'].apply(str)
        
        return chains
    
    def _create_sequences(self) -> pd.DataFrame:
        """Create sequence table (possession chains)."""
        events = self.events_df[self.events_df['sequence_index'].notna()].copy()
        
        if len(events) == 0:
            return pd.DataFrame()
        
        sequences = events.groupby('sequence_index').agg({
            'event_index': ['min', 'max', 'count'],
            'Type': lambda x: list(x),
            'event_detail': lambda x: list(x),
            'shift_index': 'first'
        }).reset_index()
        
        sequences.columns = ['sequence_index', 'first_event', 'last_event',
                            'event_count', 'event_types', 'event_details', 'shift_index']
        
        sequences['sequence_key'] = sequences['sequence_index'].apply(lambda x: f"{self.game_id}_seq_{int(x)}")
        sequences['game_id'] = self.game_id
        
        # Convert lists to strings
        sequences['event_types'] = sequences['event_types'].apply(str)
        sequences['event_details'] = sequences['event_details'].apply(str)
        
        return sequences
    
    def _create_plays(self) -> pd.DataFrame:
        """Create plays table (sub-sequence plays)."""
        events = self.events_df[self.events_df['play_index'].notna()].copy()
        
        if len(events) == 0:
            return pd.DataFrame()
        
        plays = events.groupby('play_index').agg({
            'event_index': ['min', 'max', 'count'],
            'Type': lambda x: list(x),
            'event_detail': lambda x: list(x)
        }).reset_index()
        
        plays.columns = ['play_index', 'first_event', 'last_event',
                        'event_count', 'event_types', 'event_details']
        
        plays['play_key'] = plays['play_index'].apply(lambda x: f"{self.game_id}_play_{int(x)}")
        plays['game_id'] = self.game_id
        
        plays['event_types'] = plays['event_types'].apply(str)
        plays['event_details'] = plays['event_details'].apply(str)
        
        return plays
    
    def _create_box_score(self, results: Dict) -> pd.DataFrame:
        """Create comprehensive box score."""
        players = results['dim_game_players'].copy()
        event_players = results['fact_event_players']
        shift_players = results['fact_shift_players']
        events = results['fact_events']
        
        # Start with player info
        box = players[['player_game_key', 'player_game_number', 'player_id',
                       'player_team', 'player_venue', 'position', 'skill_rating',
                       'player_full_name', 'display_name']].copy()
        box['game_id'] = self.game_id
        
        # Merge with primary events
        primary = event_players[event_players['is_primary_player'] == 1].merge(
            events[['event_index', 'Type', 'event_detail', 'event_successful', 'duration']],
            on='event_index'
        )
        
        # =================================================================
        # ICE TIME
        # =================================================================
        toi = shift_players.groupby('player_game_number').agg({
            'shift_duration': 'sum',
            'plus_minus': 'sum',
            'shift_index': 'count'
        }).reset_index()
        toi.columns = ['player_game_number', 'toi_seconds', 'plus_minus', 'shifts']
        box = box.merge(toi, on='player_game_number', how='left')
        box['toi_formatted'] = box['toi_seconds'].apply(
            lambda x: f"{int(x//60)}:{int(x%60):02d}" if pd.notna(x) else "0:00"
        )
        
        # =================================================================
        # SCORING
        # =================================================================
        goals = primary[primary['event_detail'] == 'Goal_Scored'].groupby('player_game_number').size()
        box['goals'] = box['player_game_number'].map(goals).fillna(0).astype(int)
        
        # Assists from play_detail1
        assists_p = event_players[event_players['play_detail1'] == 'AssistPrimary'].groupby('player_game_number').size()
        box['assists_primary'] = box['player_game_number'].map(assists_p).fillna(0).astype(int)
        
        assists_s = event_players[event_players['play_detail1'] == 'AssistSecondary'].groupby('player_game_number').size()
        box['assists_secondary'] = box['player_game_number'].map(assists_s).fillna(0).astype(int)
        
        box['assists'] = box['assists_primary'] + box['assists_secondary']
        box['points'] = box['goals'] + box['assists']
        
        # =================================================================
        # SHOOTING
        # =================================================================
        shots = primary[primary['Type'] == 'Shot'].groupby('player_game_number').size()
        box['shots'] = box['player_game_number'].map(shots).fillna(0).astype(int)
        
        sog_details = ['Shot_OnNetSaved', 'Shot_Goal', 'Shot_TippedOnNetSaved', 'Shot_DeflectedOnNetSaved']
        sog = primary[primary['event_detail'].isin(sog_details)].groupby('player_game_number').size()
        box['shots_on_goal'] = box['player_game_number'].map(sog).fillna(0).astype(int)
        
        missed = primary[primary['event_detail'].str.contains('Missed', na=False)].groupby('player_game_number').size()
        box['shots_missed'] = box['player_game_number'].map(missed).fillna(0).astype(int)
        
        blocked = primary[primary['event_detail'].str.contains('Blocked', na=False)].groupby('player_game_number').size()
        box['shots_blocked'] = box['player_game_number'].map(blocked).fillna(0).astype(int)
        
        box['shooting_pct'] = (box['goals'] / box['shots_on_goal'].replace(0, np.nan) * 100).round(1).fillna(0)
        
        # Shot success
        shots_s = primary[(primary['Type'] == 'Shot') & (primary['event_successful'] == 's')].groupby('player_game_number').size()
        shots_u = primary[(primary['Type'] == 'Shot') & (primary['event_successful'] == 'u')].groupby('player_game_number').size()
        box['shots_successful'] = box['player_game_number'].map(shots_s).fillna(0).astype(int)
        box['shots_unsuccessful'] = box['player_game_number'].map(shots_u).fillna(0).astype(int)
        
        # =================================================================
        # PASSING
        # =================================================================
        passes = primary[primary['Type'] == 'Pass'].groupby('player_game_number').size()
        box['passes'] = box['player_game_number'].map(passes).fillna(0).astype(int)
        
        pass_comp = primary[primary['event_detail'] == 'Pass_Completed'].groupby('player_game_number').size()
        box['passes_completed'] = box['player_game_number'].map(pass_comp).fillna(0).astype(int)
        
        pass_fail = primary[primary['event_detail'].isin(['Pass_Missed', 'Pass_Intercepted'])].groupby('player_game_number').size()
        box['passes_failed'] = box['player_game_number'].map(pass_fail).fillna(0).astype(int)
        
        box['pass_pct'] = (box['passes_completed'] / box['passes'].replace(0, np.nan) * 100).round(1).fillna(0)
        
        # Pass target (event_player_2 on passes)
        pass_target = event_players[
            (event_players['player_role'] == 'event_team_player_2')
        ].merge(events[events['Type'] == 'Pass'][['event_index']], on='event_index')
        pass_target_counts = pass_target.groupby('player_game_number').size()
        box['times_pass_target'] = box['player_game_number'].map(pass_target_counts).fillna(0).astype(int)
        
        # =================================================================
        # TURNOVERS
        # =================================================================
        giveaways = primary[primary['event_detail'] == 'Turnover_Giveaway'].groupby('player_game_number').size()
        box['giveaways'] = box['player_game_number'].map(giveaways).fillna(0).astype(int)
        
        takeaways = primary[primary['event_detail'] == 'Turnover_Takeaway'].groupby('player_game_number').size()
        box['takeaways'] = box['player_game_number'].map(takeaways).fillna(0).astype(int)
        
        box['turnover_differential'] = box['takeaways'] - box['giveaways']
        
        # =================================================================
        # FACEOFFS
        # =================================================================
        faceoffs = primary[primary['Type'] == 'Faceoff'].groupby('player_game_number').size()
        box['faceoffs'] = box['player_game_number'].map(faceoffs).fillna(0).astype(int)
        
        fo_wins = primary[(primary['Type'] == 'Faceoff') & (primary['event_successful'] == 's')].groupby('player_game_number').size()
        box['faceoff_wins'] = box['player_game_number'].map(fo_wins).fillna(0).astype(int)
        
        box['faceoff_pct'] = (box['faceoff_wins'] / box['faceoffs'].replace(0, np.nan) * 100).round(1).fillna(0)
        
        # =================================================================
        # ZONE PLAY
        # =================================================================
        zone_events = primary[primary['Type'] == 'Zone_Entry_Exit']
        
        entries = zone_events[zone_events['event_detail'].str.contains('Entry', na=False)].groupby('player_game_number').size()
        box['zone_entries'] = box['player_game_number'].map(entries).fillna(0).astype(int)
        
        entry_success = zone_events[
            (zone_events['event_detail'].str.contains('Entry', na=False)) &
            (zone_events['event_successful'] == 's')
        ].groupby('player_game_number').size()
        box['zone_entries_successful'] = box['player_game_number'].map(entry_success).fillna(0).astype(int)
        
        exits = zone_events[zone_events['event_detail'].str.contains('Exit', na=False)].groupby('player_game_number').size()
        box['zone_exits'] = box['player_game_number'].map(exits).fillna(0).astype(int)
        
        # Zone entry denials (as opp_team_player_1)
        zone_denial_events = events[events['Type'] == 'Zone_Entry_Exit']
        opp_on_entries = event_players[
            (event_players['is_opp_team'] == 1) &
            (event_players['event_index'].isin(zone_denial_events['event_index']))
        ].groupby('player_game_number').size()
        box['zone_entry_targets'] = box['player_game_number'].map(opp_on_entries).fillna(0).astype(int)
        
        # =================================================================
        # POSSESSION
        # =================================================================
        possessions = primary[primary['Type'] == 'Possession'].groupby('player_game_number').size()
        box['possessions'] = box['player_game_number'].map(possessions).fillna(0).astype(int)
        
        poss_time = primary[primary['Type'] == 'Possession'].groupby('player_game_number')['duration'].sum()
        box['possession_time'] = box['player_game_number'].map(poss_time).fillna(0).astype(int)
        
        # =================================================================
        # PLAY DETAILS (MICRO-STATS)
        # =================================================================
        play_details = event_players['play_detail1'].dropna()
        
        # Defensive plays
        for detail, col in [
            ('StickCheck', 'stick_checks'),
            ('PokeCheck', 'poke_checks'),
            ('BlockedShot', 'blocked_shots_play'),
            ('InShotPassLane', 'in_shot_pass_lane'),
            ('SeparateFromPuck', 'separate_from_puck'),
            ('Backcheck', 'backchecks'),
            ('ZoneEntryDenial', 'zone_entry_denials'),
            ('ZoneExitDenial', 'zone_exit_denials'),
        ]:
            counts = event_players[event_players['play_detail1'] == detail].groupby('player_game_number').size()
            box[col] = box['player_game_number'].map(counts).fillna(0).astype(int)
        
        # Offensive plays
        for detail, col in [
            ('Deke', 'dekes'),
            ('BeatDeke', 'dekes_successful'),
            ('Screen', 'screens'),
            ('DumpAndChase', 'dump_and_chase'),
        ]:
            counts = event_players[event_players['play_detail1'] == detail].groupby('player_game_number').size()
            box[col] = box['player_game_number'].map(counts).fillna(0).astype(int)
        
        # Drive attempts
        drive_details = ['DriveMiddle', 'DriveWide', 'DriveCorner', 'DriveNetMiddle']
        drives = event_players[event_players['play_detail1'].isin(drive_details)].groupby('player_game_number').size()
        box['drives'] = box['player_game_number'].map(drives).fillna(0).astype(int)
        
        beat_details = ['BeatMiddle', 'BeatWide']
        beats = event_players[event_players['play_detail1'].isin(beat_details)].groupby('player_game_number').size()
        box['drives_successful'] = box['player_game_number'].map(beats).fillna(0).astype(int)
        
        # Breakouts
        breakout_details = ['Breakout', 'AttemptedBreakOutPass', 'AttemptedBreakOutRush']
        breakouts = event_players[event_players['play_detail1'].isin(breakout_details)].groupby('player_game_number').size()
        box['breakouts'] = box['player_game_number'].map(breakouts).fillna(0).astype(int)
        
        # Puck recoveries
        recovery_mask = event_players['play_detail1'].str.contains('Recovery|Retrieval', na=False, case=False)
        recoveries = event_players[recovery_mask].groupby('player_game_number').size()
        box['puck_recoveries'] = box['player_game_number'].map(recoveries).fillna(0).astype(int)
        
        # =================================================================
        # GOALIE STATS
        # =================================================================
        saves = primary[primary['Type'] == 'Save'].groupby('player_game_number').size()
        box['saves'] = box['player_game_number'].map(saves).fillna(0).astype(int)
        
        # Goals against (opponent scored while goalie on ice)
        # This is complex - simplified version
        opp_events = event_players[event_players['is_opp_team'] == 1].merge(
            events[events['event_detail'] == 'Goal_Scored'][['event_index']],
            on='event_index'
        )
        ga = opp_events.groupby('player_game_number').size()
        box['goals_against'] = box['player_game_number'].map(ga).fillna(0).astype(int)
        
        box['save_pct'] = (box['saves'] / (box['saves'] + box['goals_against']).replace(0, np.nan) * 100).round(1).fillna(0)
        
        # =================================================================
        # SKILL CONTEXT
        # =================================================================
        # Average opponent skill faced
        opp_skill = shift_players.merge(
            results['fact_shifts'][['shift_index', 'home_skill_avg', 'away_skill_avg']],
            left_on='shift_index', right_on='shift_index'
        )
        opp_skill['opp_skill'] = opp_skill.apply(
            lambda r: r['away_skill_avg'] if r['player_venue'] == 'home' else r['home_skill_avg'],
            axis=1
        )
        avg_opp_skill = opp_skill.groupby('player_game_number')['opp_skill'].mean()
        box['avg_opp_skill_faced'] = box['player_game_number'].map(avg_opp_skill).round(2).fillna(4)
        
        box['skill_vs_opponents'] = (box['skill_rating'] - box['avg_opp_skill_faced']).round(2)
        
        # =================================================================
        # PER-60 RATES
        # =================================================================
        for stat in ['goals', 'assists', 'points', 'shots', 'shots_on_goal']:
            box[f'{stat}_per_60'] = (box[stat] / (box['toi_seconds'] / 3600)).round(2).fillna(0)
        
        # =================================================================
        # CORSI / FENWICK (on-ice shot differentials)
        # =================================================================
        # Simplified: count shots for/against while on ice
        # This requires matching shifts to events
        
        # Fill NaN values
        box = box.fillna(0)
        
        return box.sort_values(['player_team', 'player_game_number']).reset_index(drop=True)
