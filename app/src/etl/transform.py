"""
BenchSight ETL - Transform Module
Transforms raw data through Stage → Intermediate → Mart layers
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BenchSightTransformer:
    """Transform BenchSight data through ETL layers"""
    
    def __init__(self, master_tables: dict):
        self.master_tables = master_tables
        self.dim_player = master_tables.get('dim_player', pd.DataFrame())
        self.dim_team = master_tables.get('dim_team', pd.DataFrame())
        self.dim_schedule = master_tables.get('dim_schedule', pd.DataFrame())
        
    # ==========================================
    # STAGE LAYER - Light cleansing
    # ==========================================
    
    def stage_events(self, events_df: pd.DataFrame, game_id: int) -> pd.DataFrame:
        """Stage layer: Clean events data"""
        if events_df is None or events_df.empty:
            return pd.DataFrame()
            
        df = events_df.copy()
        df['game_id'] = game_id
        
        # Standardize column names
        col_mapping = {
            'event_index_flag': 'event_index',
            'sequence_index_flag': 'sequence_index',
            'play_index_flag': 'play_index',
            'event_type': 'event_type',
            'event_detail': 'event_detail_1',
            'event_detail_2': 'event_detail_2',
            'event_successful': 'event_successful',
            'play_detail1': 'play_detail_1',
            'play_detail2': 'play_detail_2',
            'event_start_min': 'event_start_min',
            'event_start_sec': 'event_start_sec',
            'event_end_min': 'event_end_min',
            'event_end_sec': 'event_end_sec',
            'player_game_number': 'player_number',
            'event_team_zone': 'event_zone'
        }
        
        for old, new in col_mapping.items():
            if old in df.columns and new not in df.columns:
                df = df.rename(columns={old: new})
                
        # Calculate running seconds
        if 'event_start_min' in df.columns and 'event_start_sec' in df.columns:
            df['event_start_running_sec'] = (
                pd.to_numeric(df['event_start_min'], errors='coerce').fillna(0) * 60 +
                pd.to_numeric(df['event_start_sec'], errors='coerce').fillna(0)
            )
            
        if 'event_end_min' in df.columns and 'event_end_sec' in df.columns:
            df['event_end_running_sec'] = (
                pd.to_numeric(df['event_end_min'], errors='coerce').fillna(0) * 60 +
                pd.to_numeric(df['event_end_sec'], errors='coerce').fillna(0)
            )
            
        # Calculate duration
        if 'event_start_running_sec' in df.columns and 'event_end_running_sec' in df.columns:
            df['event_duration_sec'] = df['event_end_running_sec'] - df['event_start_running_sec']
            df['event_duration_sec'] = df['event_duration_sec'].clip(lower=0)
            
        # Add metadata
        df['etl_loaded_at'] = datetime.now()
        df['source_layer'] = 'stage'
        
        return df
    
    def stage_shifts(self, shifts_df: pd.DataFrame, game_id: int) -> pd.DataFrame:
        """Stage layer: Clean shifts data"""
        if shifts_df is None or shifts_df.empty:
            return pd.DataFrame()
            
        df = shifts_df.copy()
        df['game_id'] = game_id
        
        # Add metadata
        df['etl_loaded_at'] = datetime.now()
        df['source_layer'] = 'stage'
        
        return df
    
    def stage_video_times(self, video_df: pd.DataFrame, game_id: int) -> pd.DataFrame:
        """Stage layer: Clean video times data"""
        if video_df is None or video_df.empty:
            return pd.DataFrame()
            
        df = video_df.copy()
        df['game_id'] = game_id
        df['etl_loaded_at'] = datetime.now()
        
        return df
    
    # ==========================================
    # INTERMEDIATE LAYER - Business logic
    # ==========================================
    
    def int_events_enriched(self, stg_events: pd.DataFrame) -> pd.DataFrame:
        """Intermediate layer: Enrich events with sequences and play chains"""
        if stg_events.empty:
            return pd.DataFrame()
            
        df = stg_events.copy()
        
        # Generate sequence/play indices if not present
        if 'sequence_index' not in df.columns or df['sequence_index'].isna().all():
            df = self._generate_sequence_index(df)
            
        if 'play_index' not in df.columns or df['play_index'].isna().all():
            df = self._generate_play_index(df)
            
        # Classify event categories
        df['event_category'] = df['event_type'].apply(self._classify_event_category)
        
        # Flag scoring events
        df['is_goal'] = df['event_detail_1'].str.lower().str.contains('goal', na=False)
        df['is_shot'] = df['event_type'].str.lower().isin(['shot', 'shot_on_goal', 'sog'])
        df['is_save'] = df['event_type'].str.lower().str.contains('save', na=False)
        
        # Flag possession events
        df['is_turnover'] = df['event_type'].str.lower().str.contains('turnover|giveaway|takeaway', na=False)
        df['is_zone_entry'] = df['event_type'].str.lower().str.contains('zone_entry|entry', na=False)
        df['is_zone_exit'] = df['event_type'].str.lower().str.contains('zone_exit|exit', na=False)
        
        # Classify turnovers (true giveaways vs dumps)
        df['is_true_giveaway'] = self._classify_true_giveaway(df)
        df['is_takeaway'] = df['event_type'].str.lower().str.contains('takeaway', na=False)
        
        # Add layer metadata
        df['source_layer'] = 'intermediate'
        
        return df
    
    def _generate_sequence_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate sequence index based on time gaps and possession changes"""
        df = df.sort_values(['game_id', 'event_start_running_sec'])
        
        # New sequence when:
        # 1. Time gap > 5 seconds
        # 2. Possession change (faceoff, turnover)
        
        sequence_idx = 1
        indices = []
        
        prev_time = 0
        for idx, row in df.iterrows():
            curr_time = row.get('event_start_running_sec', 0) or 0
            event_type = str(row.get('event_type', '')).lower()
            
            # Check for sequence break
            time_gap = curr_time - prev_time
            is_faceoff = 'faceoff' in event_type
            
            if time_gap > 5 or is_faceoff:
                sequence_idx += 1
                
            indices.append(sequence_idx)
            prev_time = curr_time
            
        df['sequence_index'] = indices
        return df
    
    def _generate_play_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate play index within sequences"""
        df = df.sort_values(['game_id', 'sequence_index', 'event_start_running_sec'])
        
        play_idx = 1
        indices = []
        
        prev_seq = 0
        for idx, row in df.iterrows():
            curr_seq = row.get('sequence_index', 0) or 0
            
            if curr_seq != prev_seq:
                play_idx = 1
            else:
                play_idx += 1
                
            indices.append(play_idx)
            prev_seq = curr_seq
            
        df['play_index'] = indices
        return df
    
    def _classify_event_category(self, event_type: str) -> str:
        """Classify event into category"""
        if pd.isna(event_type):
            return 'unknown'
            
        event_lower = str(event_type).lower()
        
        if any(x in event_lower for x in ['shot', 'goal', 'save', 'block']):
            return 'shooting'
        elif any(x in event_lower for x in ['pass', 'reception']):
            return 'passing'
        elif any(x in event_lower for x in ['faceoff', 'fo_']):
            return 'faceoff'
        elif any(x in event_lower for x in ['zone_entry', 'entry']):
            return 'zone_entry'
        elif any(x in event_lower for x in ['zone_exit', 'exit']):
            return 'zone_exit'
        elif any(x in event_lower for x in ['turnover', 'giveaway', 'takeaway']):
            return 'turnover'
        elif any(x in event_lower for x in ['hit', 'check']):
            return 'physical'
        elif any(x in event_lower for x in ['penalty']):
            return 'penalty'
        else:
            return 'other'
    
    def _classify_true_giveaway(self, df: pd.DataFrame) -> pd.Series:
        """
        Classify true giveaways (misplays) vs tactical dumps
        True giveaway = misplay, bad pass, lost puck
        NOT giveaway = dump-in, dump-out, clear (tactical)
        """
        result = pd.Series(False, index=df.index)
        
        for idx, row in df.iterrows():
            event_type = str(row.get('event_type', '')).lower()
            event_detail = str(row.get('event_detail_1', '')).lower()
            play_detail = str(row.get('play_detail_1', '')).lower()
            
            is_turnover = 'turnover' in event_type or 'giveaway' in event_type
            is_dump = any(x in event_detail for x in ['dump', 'clear', 'chip'])
            is_dump_play = any(x in play_detail for x in ['dump', 'clear', 'chip'])
            
            # True giveaway if turnover but NOT a dump/clear
            result[idx] = is_turnover and not is_dump and not is_dump_play
            
        return result
    
    def int_possession_chains(self, int_events: pd.DataFrame) -> pd.DataFrame:
        """Build possession chains from events"""
        if int_events.empty:
            return pd.DataFrame()
            
        chains = []
        
        for game_id in int_events['game_id'].unique():
            game_events = int_events[int_events['game_id'] == game_id]
            
            for seq_idx in game_events['sequence_index'].unique():
                seq_events = game_events[game_events['sequence_index'] == seq_idx]
                
                chain = {
                    'game_id': game_id,
                    'sequence_index': seq_idx,
                    'event_count': len(seq_events),
                    'has_shot': seq_events['is_shot'].any(),
                    'has_goal': seq_events['is_goal'].any(),
                    'has_zone_entry': seq_events['is_zone_entry'].any(),
                    'start_time': seq_events['event_start_running_sec'].min(),
                    'end_time': seq_events['event_end_running_sec'].max(),
                    'duration_sec': (
                        seq_events['event_end_running_sec'].max() - 
                        seq_events['event_start_running_sec'].min()
                    ) if not seq_events.empty else 0
                }
                chains.append(chain)
                
        return pd.DataFrame(chains)
    
    # ==========================================
    # MART LAYER - Analytics-ready
    # ==========================================
    
    def mart_fact_playbyplay(self, int_events: pd.DataFrame, game_info: dict = None) -> pd.DataFrame:
        """Mart layer: Play-by-play fact table"""
        if int_events.empty:
            return pd.DataFrame()
            
        df = int_events.copy()
        
        # Add game info if available
        if game_info:
            for key, value in game_info.items():
                if key not in df.columns:
                    df[key] = value
                    
        # Select final columns
        mart_cols = [
            'game_id', 'sequence_index', 'play_index', 'event_index',
            'event_start_running_sec', 'event_end_running_sec', 'event_duration_sec',
            'event_type', 'event_detail_1', 'event_detail_2',
            'event_successful', 'play_detail_1', 'play_detail_2',
            'player_number', 'event_zone', 'event_category',
            'is_goal', 'is_shot', 'is_save', 'is_turnover',
            'is_zone_entry', 'is_zone_exit', 'is_true_giveaway', 'is_takeaway'
        ]
        
        # Only keep columns that exist
        mart_cols = [c for c in mart_cols if c in df.columns]
        
        df = df[mart_cols].copy()
        df['source_layer'] = 'mart'
        
        return df
    
    def mart_player_game_stats(self, int_events: pd.DataFrame, int_shifts: pd.DataFrame = None) -> pd.DataFrame:
        """Mart layer: Player game statistics"""
        if int_events.empty:
            return pd.DataFrame()
            
        stats = []
        
        for game_id in int_events['game_id'].unique():
            game_events = int_events[int_events['game_id'] == game_id]
            
            # Get unique players
            players = game_events['player_number'].dropna().unique()
            
            for player_num in players:
                player_events = game_events[game_events['player_number'] == player_num]
                
                stat_row = {
                    'game_id': game_id,
                    'player_number': player_num,
                    # Basic stats
                    'goals': player_events['is_goal'].sum(),
                    'shots': player_events['is_shot'].sum(),
                    'shots_on_goal': len(player_events[
                        (player_events['is_shot']) & 
                        (player_events['event_detail_1'].str.lower().str.contains('on_goal|goal', na=False))
                    ]),
                    # Advanced stats
                    'zone_entries': player_events['is_zone_entry'].sum(),
                    'zone_exits': player_events['is_zone_exit'].sum(),
                    'true_giveaways': player_events['is_true_giveaway'].sum(),
                    'takeaways': player_events['is_takeaway'].sum(),
                    # Possession time
                    'possession_time_sec': player_events['event_duration_sec'].sum(),
                    # Event counts
                    'total_events': len(player_events)
                }
                stats.append(stat_row)
                
        return pd.DataFrame(stats)
    
    def mart_team_game_stats(self, int_events: pd.DataFrame, game_info: dict = None) -> pd.DataFrame:
        """Mart layer: Team game statistics"""
        if int_events.empty:
            return pd.DataFrame()
            
        # Aggregate by game
        game_stats = int_events.groupby('game_id').agg({
            'is_goal': 'sum',
            'is_shot': 'sum',
            'is_zone_entry': 'sum',
            'is_zone_exit': 'sum',
            'is_true_giveaway': 'sum',
            'is_takeaway': 'sum',
            'event_duration_sec': 'sum',
            'sequence_index': 'nunique'
        }).reset_index()
        
        game_stats.columns = [
            'game_id', 'total_goals', 'total_shots', 
            'zone_entries', 'zone_exits', 'giveaways', 'takeaways',
            'total_possession_time_sec', 'total_sequences'
        ]
        
        return game_stats


class StatisticsCalculator:
    """Calculate advanced and micro statistics"""
    
    @staticmethod
    def calc_corsi(events: pd.DataFrame, player_on_ice: bool = True) -> dict:
        """Calculate Corsi For/Against"""
        shot_attempts = events[events['event_category'] == 'shooting']
        
        cf = len(shot_attempts[shot_attempts['is_for_team']])
        ca = len(shot_attempts[~shot_attempts['is_for_team']])
        
        cf_pct = cf / (cf + ca) * 100 if (cf + ca) > 0 else 0
        
        return {'CF': cf, 'CA': ca, 'CF%': cf_pct}
    
    @staticmethod
    def calc_fenwick(events: pd.DataFrame) -> dict:
        """Calculate Fenwick (unblocked shot attempts)"""
        unblocked = events[
            (events['event_category'] == 'shooting') & 
            (~events['event_detail_1'].str.lower().str.contains('block', na=False))
        ]
        
        ff = len(unblocked[unblocked['is_for_team']])
        fa = len(unblocked[~unblocked['is_for_team']])
        
        ff_pct = ff / (ff + fa) * 100 if (ff + fa) > 0 else 0
        
        return {'FF': ff, 'FA': fa, 'FF%': ff_pct}
    
    @staticmethod
    def calc_possession_time(events: pd.DataFrame) -> dict:
        """Calculate possession time metrics"""
        total_time = events['event_duration_sec'].sum()
        
        oz_time = events[events['event_zone'] == 'OZ']['event_duration_sec'].sum()
        dz_time = events[events['event_zone'] == 'DZ']['event_duration_sec'].sum()
        nz_time = events[events['event_zone'] == 'NZ']['event_duration_sec'].sum()
        
        return {
            'total_possession_sec': total_time,
            'oz_time_sec': oz_time,
            'dz_time_sec': dz_time,
            'nz_time_sec': nz_time,
            'oz_pct': oz_time / total_time * 100 if total_time > 0 else 0
        }
    
    @staticmethod
    def calc_zone_entry_success(events: pd.DataFrame) -> dict:
        """Calculate zone entry success rates"""
        entries = events[events['is_zone_entry']]
        
        if entries.empty:
            return {'entries': 0, 'success_rate': 0, 'controlled_pct': 0}
            
        successful = entries[entries['event_successful'] == True]
        controlled = entries[entries['event_detail_1'].str.lower().str.contains('controlled|carry', na=False)]
        
        return {
            'entries': len(entries),
            'successful_entries': len(successful),
            'success_rate': len(successful) / len(entries) * 100 if len(entries) > 0 else 0,
            'controlled_entries': len(controlled),
            'controlled_pct': len(controlled) / len(entries) * 100 if len(entries) > 0 else 0
        }
    
    @staticmethod
    def calc_rating_adjusted_stats(events: pd.DataFrame, player_ratings: dict, opp_ratings: dict) -> dict:
        """Calculate rating-adjusted statistics"""
        # This would need on-ice player data
        # Placeholder for rating context calculations
        avg_opp_rating = np.mean(list(opp_ratings.values())) if opp_ratings else 0
        avg_team_rating = np.mean(list(player_ratings.values())) if player_ratings else 0
        
        rating_diff = avg_team_rating - avg_opp_rating
        
        return {
            'avg_opponent_rating': avg_opp_rating,
            'avg_teammate_rating': avg_team_rating,
            'rating_differential': rating_diff,
            'quality_of_competition': avg_opp_rating
        }


def main():
    """Test transforms"""
    from extract import BenchSightExtractor
    
    extractor = BenchSightExtractor()
    master = extractor.extract_master_tables()
    
    transformer = BenchSightTransformer(master)
    
    # Test with one game
    game_ids = extractor.get_game_ids()
    if game_ids:
        game_data = extractor.extract_game_tracking(game_ids[0])
        
        # Stage
        stg_events = transformer.stage_events(game_data['events'], game_ids[0])
        print(f"Stage events: {len(stg_events)} rows")
        
        # Intermediate
        int_events = transformer.int_events_enriched(stg_events)
        print(f"Intermediate events: {len(int_events)} rows")
        
        # Mart
        mart_pbp = transformer.mart_fact_playbyplay(int_events)
        print(f"Mart play-by-play: {len(mart_pbp)} rows")
        

if __name__ == '__main__':
    main()
