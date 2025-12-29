#!/usr/bin/env python3
"""
Add all foreign keys to fact tables.
Creates comprehensive FK relationships across all tables.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path('data/output')
RAW_DIR = Path('data/raw/games')


class FKBuilder:
    """Build foreign keys for all fact tables."""
    
    def __init__(self):
        self.dim_lookups = {}
        self._load_dim_lookups()
    
    def _load_dim_lookups(self):
        """Load all dim tables for FK lookups."""
        logger.info("Loading dimension tables...")
        
        dim_configs = {
            'period': ('dim_period', 'period_number', 'period_id'),
            'venue': ('dim_venue', 'venue_code', 'venue_id'),
            'team': ('dim_team', 'team_name', 'team_id'),
            'zone': ('dim_zone', 'zone_code', 'zone_id'),
            'strength': ('dim_strength', 'strength_code', 'strength_id'),
            'situation': ('dim_situation', 'situation_code', 'situation_id'),
            'slot': ('dim_shift_slot', 'slot_code', 'slot_id'),
            'position': ('dim_position', 'position_code', 'position_id'),
            'event_type': ('dim_event_type', 'event_type_code', 'event_type_id'),
            'event_detail': ('dim_event_detail', 'event_detail_code', 'event_detail_id'),
            'shift_start_type': ('dim_shift_start_type', 'shift_start_type_code', 'shift_start_type_id'),
            'shift_stop_type': ('dim_shift_stop_type', 'shift_stop_type_code', 'shift_stop_type_id'),
            'success': ('dim_success', 'success_code', 'success_id'),
            'zone_entry': ('dim_zone_entry_type', 'zone_entry_type_code', 'zone_entry_type_id'),
            'zone_exit': ('dim_zone_exit_type', 'zone_exit_type_code', 'zone_exit_type_id'),
            'pass': ('dim_pass_type', 'pass_type_code', 'pass_type_id'),
            'shot': ('dim_shot_type', 'shot_type_code', 'shot_type_id'),
            'turnover': ('dim_turnover_type', 'turnover_type_code', 'turnover_type_id'),
        }
        
        for name, (table, code_col, id_col) in dim_configs.items():
            try:
                df = pd.read_csv(OUTPUT_DIR / f'{table}.csv')
                # Create multiple lookups (by code, by name variations)
                self.dim_lookups[name] = {}
                
                if code_col in df.columns and id_col in df.columns:
                    # Lowercase lookup
                    self.dim_lookups[name]['code'] = df.set_index(df[code_col].str.lower())[id_col].to_dict()
                    # Original case lookup
                    self.dim_lookups[name]['code_orig'] = df.set_index(code_col)[id_col].to_dict()
                
                # Add name-based lookups if available
                name_col = code_col.replace('_code', '_name')
                if name_col in df.columns:
                    self.dim_lookups[name]['name'] = df.set_index(df[name_col].str.lower())[id_col].to_dict()
                
            except Exception as e:
                logger.warning(f"Could not load {table}: {e}")
                self.dim_lookups[name] = {'code': {}, 'code_orig': {}, 'name': {}}
    
    def _lookup_id(self, dim_name, value):
        """Look up dimension ID from value."""
        if pd.isna(value):
            return None
        
        value_str = str(value).lower().strip()
        lookups = self.dim_lookups.get(dim_name, {})
        
        # Try code lookup first
        if value_str in lookups.get('code', {}):
            return lookups['code'][value_str]
        
        # Try original case
        if str(value) in lookups.get('code_orig', {}):
            return lookups['code_orig'][str(value)]
        
        # Try name lookup
        if value_str in lookups.get('name', {}):
            return lookups['name'][value_str]
        
        return None
    
    def add_shifts_fkeys(self):
        """Add FKs to fact_shifts_player."""
        logger.info("Adding FKs to fact_shifts_player...")
        
        df = pd.read_csv(OUTPUT_DIR / 'fact_shifts_player.csv')
        
        # Period ID
        df['period_id'] = df['period'].apply(lambda x: self._lookup_id('period', x))
        
        # Venue ID  
        df['venue_id'] = df['venue'].apply(lambda x: self._lookup_id('venue', x))
        
        # Strength ID
        df['strength_id'] = df['strength'].apply(lambda x: self._lookup_id('strength', x))
        
        # Situation ID
        df['situation_id'] = df['situation'].apply(lambda x: self._lookup_id('situation', x))
        
        # Slot/Position ID
        df['slot_id'] = df['slot'].apply(lambda x: self._lookup_id('slot', x))
        
        # Team ID (need to lookup from roster or schedule)
        schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
        for game_id in df['game_id'].unique():
            game_sched = schedule[schedule['game_id'] == int(game_id)]
            if not game_sched.empty:
                home_team = game_sched.iloc[0].get('home_team_id')
                away_team = game_sched.iloc[0].get('away_team_id')
                
                mask_home = (df['game_id'] == game_id) & (df['venue'] == 'home')
                mask_away = (df['game_id'] == game_id) & (df['venue'] == 'away')
                
                df.loc[mask_home, 'team_id'] = home_team
                df.loc[mask_away, 'team_id'] = away_team
        
        # Add video time columns from raw
        for game_id in df['game_id'].unique():
            tracking_file = RAW_DIR / str(game_id) / f'{game_id}_tracking.xlsx'
            if tracking_file.exists():
                try:
                    raw_shifts = pd.read_excel(tracking_file, sheet_name='shifts')
                    video_cols = ['running_video_time', 'shift_start_running_time', 'shift_end_running_time']
                    for col in video_cols:
                        if col in raw_shifts.columns:
                            lookup = raw_shifts.set_index('shift_index')[col].to_dict()
                            mask = df['game_id'] == game_id
                            df.loc[mask, col] = df.loc[mask, 'shift_index'].map(lookup)
                except:
                    pass
        
        df.to_csv(OUTPUT_DIR / 'fact_shifts_player.csv', index=False)
        logger.info(f"  ✓ fact_shifts_player: Added FKs")
        return df
    
    def add_events_fkeys(self):
        """Add FKs to fact_events_player."""
        logger.info("Adding FKs to fact_events_player...")
        
        df = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
        
        # Period ID
        df['period_id'] = df['period'].apply(lambda x: self._lookup_id('period', x))
        
        # Venue ID
        df['venue_id'] = df['team_venue'].apply(lambda x: self._lookup_id('venue', x))
        
        # Event Type ID
        df['event_type_id'] = df['event_type'].apply(lambda x: self._lookup_id('event_type', x))
        
        # Event Detail ID
        df['event_detail_id'] = df['event_detail'].apply(lambda x: self._lookup_id('event_detail', x))
        
        # Success ID
        df['success_id'] = df['event_successful'].apply(lambda x: self._lookup_id('success', x))
        
        # Zone Entry/Exit Type IDs (for zone events)
        def get_zone_entry_id(row):
            if 'Entry' in str(row.get('event_detail', '')):
                return self._lookup_id('zone_entry', row.get('event_detail'))
            return None
        
        def get_zone_exit_id(row):
            if 'Exit' in str(row.get('event_detail', '')):
                return self._lookup_id('zone_exit', row.get('event_detail'))
            return None
        
        df['zone_entry_type_id'] = df.apply(get_zone_entry_id, axis=1)
        df['zone_exit_type_id'] = df.apply(get_zone_exit_id, axis=1)
        
        # Shot Type ID
        def get_shot_type_id(row):
            if row.get('event_type') == 'Shot':
                return self._lookup_id('shot', row.get('event_detail'))
            return None
        df['shot_type_id'] = df.apply(get_shot_type_id, axis=1)
        
        # Pass Type ID
        def get_pass_type_id(row):
            if row.get('event_type') == 'Pass':
                return self._lookup_id('pass', row.get('event_detail'))
            return None
        df['pass_type_id'] = df.apply(get_pass_type_id, axis=1)
        
        # Turnover Type ID
        def get_turnover_type_id(row):
            if row.get('event_type') == 'Turnover':
                return self._lookup_id('turnover', row.get('event_detail'))
            return None
        df['turnover_type_id'] = df.apply(get_turnover_type_id, axis=1)
        
        # Zone ID
        df['zone_id'] = df['event_team_zone'].apply(lambda x: self._lookup_id('zone', x)) if 'event_team_zone' in df.columns else None
        
        # Team ID
        schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
        for game_id in df['game_id'].unique():
            game_sched = schedule[schedule['game_id'] == int(game_id)]
            if not game_sched.empty:
                home_team = game_sched.iloc[0].get('home_team_id')
                away_team = game_sched.iloc[0].get('away_team_id')
                
                mask_home = (df['game_id'] == str(game_id)) & (df['team_venue'].str.lower() == 'home')
                mask_away = (df['game_id'] == str(game_id)) & (df['team_venue'].str.lower() == 'away')
                
                df.loc[mask_home, 'team_id'] = home_team
                df.loc[mask_away, 'team_id'] = away_team
        
        # Add zone columns from raw data
        for game_id in df['game_id'].unique():
            tracking_file = RAW_DIR / str(game_id) / f'{game_id}_tracking.xlsx'
            if tracking_file.exists():
                try:
                    raw_events = pd.read_excel(tracking_file, sheet_name='events')
                    zone_cols = ['event_team_zone', 'home_team_zone', 'away_team_zone']
                    time_cols = ['running_video_time', 'event_running_start', 'event_running_end']
                    
                    # Remove underscore columns
                    raw_events = raw_events[[c for c in raw_events.columns if not c.endswith('_')]]
                    
                    for col in zone_cols + time_cols:
                        if col in raw_events.columns:
                            # Create lookup by event_index
                            lookup = raw_events.groupby('event_index')[col].first().to_dict()
                            mask = df['game_id'] == str(game_id)
                            df.loc[mask, col] = df.loc[mask, 'event_index'].map(lookup)
                except Exception as e:
                    logger.warning(f"Error loading raw events for {game_id}: {e}")
        
        # Update zone_id after adding zone columns
        if 'event_team_zone' in df.columns:
            df['zone_id'] = df['event_team_zone'].apply(lambda x: self._lookup_id('zone', x))
        
        df.to_csv(OUTPUT_DIR / 'fact_events_player.csv', index=False)
        logger.info(f"  ✓ fact_events_player: Added FKs")
        return df
    
    def add_sequence_fkeys(self):
        """Add FKs to fact_sequences."""
        logger.info("Adding FKs to fact_sequences...")
        
        seq_file = OUTPUT_DIR / 'fact_sequences.csv'
        if not seq_file.exists():
            logger.warning("fact_sequences.csv not found")
            return
        
        df = pd.read_csv(seq_file)
        events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
        
        # Build event_key lookup
        event_keys = events.drop_duplicates(['game_id', 'event_index']).set_index(
            ['game_id', 'event_index']
        )['event_key'].to_dict()
        
        # Add first/last event keys
        df['first_event_key'] = df.apply(
            lambda r: event_keys.get((str(r['game_id']), r.get('start_event_index'))), axis=1
        )
        df['last_event_key'] = df.apply(
            lambda r: event_keys.get((str(r['game_id']), r.get('end_event_index'))), axis=1
        )
        
        # Add zone IDs
        if 'start_zone' in df.columns:
            df['start_zone_id'] = df['start_zone'].apply(lambda x: self._lookup_id('zone', x))
        if 'end_zone' in df.columns:
            df['end_zone_id'] = df['end_zone'].apply(lambda x: self._lookup_id('zone', x))
        
        # Add team ID
        schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
        if 'team' in df.columns or 'team_venue' in df.columns:
            venue_col = 'team_venue' if 'team_venue' in df.columns else 'team'
            for game_id in df['game_id'].unique():
                game_sched = schedule[schedule['game_id'] == int(game_id)]
                if not game_sched.empty:
                    home_team = game_sched.iloc[0].get('home_team_id')
                    away_team = game_sched.iloc[0].get('away_team_id')
                    
                    mask_home = (df['game_id'] == game_id) & (df[venue_col].str.lower() == 'home')
                    mask_away = (df['game_id'] == game_id) & (df[venue_col].str.lower() == 'away')
                    
                    df.loc[mask_home, 'team_id'] = home_team
                    df.loc[mask_away, 'team_id'] = away_team
        
        # Add video time columns
        df['video_time_start'] = df.apply(
            lambda r: events[(events['game_id'] == str(r['game_id'])) & 
                            (events['event_index'] == r.get('start_event_index'))]['running_video_time'].iloc[0]
            if len(events[(events['game_id'] == str(r['game_id'])) & 
                         (events['event_index'] == r.get('start_event_index'))]) > 0 else None, axis=1
        )
        
        df.to_csv(seq_file, index=False)
        logger.info(f"  ✓ fact_sequences: Added FKs")
    
    def add_rush_fkeys(self):
        """Add FKs to fact_rush_events."""
        logger.info("Adding FKs to fact_rush_events...")
        
        rush_file = OUTPUT_DIR / 'fact_rush_events.csv'
        if not rush_file.exists():
            logger.warning("fact_rush_events.csv not found")
            return
        
        df = pd.read_csv(rush_file)
        events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
        
        # Build event_key lookup
        event_keys = events.drop_duplicates(['game_id', 'event_index']).set_index(
            ['game_id', 'event_index']
        )['event_key'].to_dict()
        
        # Convert game_id to int for lookup
        df['game_id'] = pd.to_numeric(df['game_id'], errors='coerce')
        
        # Add first/last event keys - rushes use entry_event_index and shot_event_index
        df['first_event_key'] = df.apply(
            lambda r: event_keys.get((int(r['game_id']), r.get('entry_event_index'))), axis=1
        )
        df['last_event_key'] = df.apply(
            lambda r: event_keys.get((int(r['game_id']), r.get('shot_event_index'))), axis=1
        )
        
        # Add entry type ID
        df['zone_entry_type_id'] = df['entry_type'].apply(lambda x: self._lookup_id('zone_entry', x)) if 'entry_type' in df.columns else None
        
        # Add team ID
        schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
        if 'team_venue' in df.columns:
            for game_id in df['game_id'].unique():
                game_sched = schedule[schedule['game_id'] == int(game_id)]
                if not game_sched.empty:
                    home_team = game_sched.iloc[0].get('home_team_id')
                    away_team = game_sched.iloc[0].get('away_team_id')
                    
                    mask_home = (df['game_id'] == game_id) & (df['team_venue'].str.lower() == 'home')
                    mask_away = (df['game_id'] == game_id) & (df['team_venue'].str.lower() == 'away')
                    
                    df.loc[mask_home, 'team_id'] = home_team
                    df.loc[mask_away, 'team_id'] = away_team
        
        # Generate rush_key if not present
        if 'rush_key' not in df.columns:
            df['rush_key'] = df.apply(
                lambda r: f"RU{int(r['game_id']):05d}{int(r.get('entry_event_index', 0)):06d}"
                if pd.notna(r.get('entry_event_index')) else None, axis=1
            )
        
        # Add video time columns
        if 'running_video_time' in events.columns:
            events['game_id'] = pd.to_numeric(events['game_id'], errors='coerce')
            start_times = events.drop_duplicates(['game_id', 'event_index']).set_index(
                ['game_id', 'event_index']
            )['running_video_time'].to_dict()
            
            df['video_time_start'] = df.apply(
                lambda r: start_times.get((int(r['game_id']), r.get('entry_event_index'))), axis=1
            )
            df['video_time_end'] = df.apply(
                lambda r: start_times.get((int(r['game_id']), r.get('shot_event_index'))), axis=1
            )
        
        df.to_csv(rush_file, index=False)
        logger.info(f"  ✓ fact_rush_events: Added FKs")
    
    def add_cycle_fkeys(self):
        """Add FKs to fact_cycle_events."""
        logger.info("Adding FKs to fact_cycle_events...")
        
        cycle_file = OUTPUT_DIR / 'fact_cycle_events.csv'
        if not cycle_file.exists():
            logger.warning("fact_cycle_events.csv not found")
            return
        
        df = pd.read_csv(cycle_file)
        events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
        
        # Build event_key lookup
        event_keys = events.drop_duplicates(['game_id', 'event_index']).set_index(
            ['game_id', 'event_index']
        )['event_key'].to_dict()
        
        # Add first/last event keys
        df['first_event_key'] = df.apply(
            lambda r: event_keys.get((str(r['game_id']), r.get('cycle_start_event_index'))), axis=1
        )
        df['last_event_key'] = df.apply(
            lambda r: event_keys.get((str(r['game_id']), r.get('cycle_end_event_index'))), axis=1
        )
        
        # Generate cycle_key if not present
        if 'cycle_key' not in df.columns:
            df['cycle_key'] = df.apply(
                lambda r: f"CY{int(r['game_id']):05d}{int(r.get('cycle_start_event_index', 0)):06d}"
                if pd.notna(r.get('cycle_start_event_index')) else None, axis=1
            )
        
        # Add video time columns
        if 'running_video_time' in events.columns:
            start_times = events.drop_duplicates(['game_id', 'event_index']).set_index(
                ['game_id', 'event_index']
            )['running_video_time'].to_dict()
            
            df['video_time_start'] = df.apply(
                lambda r: start_times.get((str(r['game_id']), r.get('cycle_start_event_index'))), axis=1
            )
            df['video_time_end'] = df.apply(
                lambda r: start_times.get((str(r['game_id']), r.get('cycle_end_event_index'))), axis=1
            )
        
        df.to_csv(cycle_file, index=False)
        logger.info(f"  ✓ fact_cycle_events: Added FKs")
    
    def add_plays_fkeys(self):
        """Add FKs to fact_plays."""
        logger.info("Adding FKs to fact_plays...")
        
        plays_file = OUTPUT_DIR / 'fact_plays.csv'
        if not plays_file.exists():
            logger.warning("fact_plays.csv not found")
            return
        
        df = pd.read_csv(plays_file)
        events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
        
        # Build event_key lookup
        event_keys = events.drop_duplicates(['game_id', 'event_index']).set_index(
            ['game_id', 'event_index']
        )['event_key'].to_dict()
        
        # Add first/last event keys
        if 'start_event_index' in df.columns:
            df['first_event_key'] = df.apply(
                lambda r: event_keys.get((str(r['game_id']), r.get('start_event_index'))), axis=1
            )
        if 'end_event_index' in df.columns:
            df['last_event_key'] = df.apply(
                lambda r: event_keys.get((str(r['game_id']), r.get('end_event_index'))), axis=1
            )
        
        # Add zone ID
        if 'zone' in df.columns:
            df['zone_id'] = df['zone'].apply(lambda x: self._lookup_id('zone', x))
        
        # Add team ID
        schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
        if 'team_venue' in df.columns:
            for game_id in df['game_id'].unique():
                game_sched = schedule[schedule['game_id'] == int(game_id)]
                if not game_sched.empty:
                    home_team = game_sched.iloc[0].get('home_team_id')
                    away_team = game_sched.iloc[0].get('away_team_id')
                    
                    mask_home = (df['game_id'] == game_id) & (df['team_venue'].str.lower() == 'home')
                    mask_away = (df['game_id'] == game_id) & (df['team_venue'].str.lower() == 'away')
                    
                    df.loc[mask_home, 'team_id'] = home_team
                    df.loc[mask_away, 'team_id'] = away_team
        
        df.to_csv(plays_file, index=False)
        logger.info(f"  ✓ fact_plays: Added FKs")
    
    def add_chains_fkeys(self):
        """Add FKs to fact_event_chains."""
        logger.info("Adding FKs to fact_event_chains...")
        
        chains_file = OUTPUT_DIR / 'fact_event_chains.csv'
        if not chains_file.exists():
            logger.warning("fact_event_chains.csv not found")
            return
        
        df = pd.read_csv(chains_file)
        events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
        
        # Build event_key and type lookups
        event_data = events.drop_duplicates(['game_id', 'event_index']).set_index(['game_id', 'event_index'])
        
        # Add event_type_id
        if 'event_type' in df.columns:
            df['event_type_id'] = df['event_type'].apply(lambda x: self._lookup_id('event_type', x))
        
        # Add video time
        if 'running_video_time' in events.columns and 'event_index' in df.columns:
            start_times = event_data['running_video_time'].to_dict()
            df['running_video_time'] = df.apply(
                lambda r: start_times.get((str(r['game_id']), r.get('event_index'))), axis=1
            )
        
        df.to_csv(chains_file, index=False)
        logger.info(f"  ✓ fact_event_chains: Added FKs")
    
    def add_linked_events_fkeys(self):
        """Add FKs to fact_linked_events."""
        logger.info("Adding FKs to fact_linked_events...")
        
        linked_file = OUTPUT_DIR / 'fact_linked_events.csv'
        if not linked_file.exists():
            logger.warning("fact_linked_events.csv not found")
            return
        
        df = pd.read_csv(linked_file)
        events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
        
        # Build event_key lookup
        event_keys = events.drop_duplicates(['game_id', 'event_index']).set_index(
            ['game_id', 'event_index']
        )['event_key'].to_dict()
        
        # Add event_keys for each event in the chain
        for i in range(1, 10):
            idx_col = f'event_{i}_index'
            key_col = f'event_{i}_key'
            if idx_col in df.columns:
                df[key_col] = df.apply(
                    lambda r: event_keys.get((str(r['game_id']), r.get(idx_col))), axis=1
                )
        
        # Add team ID from first event
        schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
        event_teams = events.drop_duplicates(['game_id', 'event_index']).set_index(
            ['game_id', 'event_index']
        )['team_venue'].to_dict()
        
        df['team_venue'] = df.apply(
            lambda r: event_teams.get((str(r['game_id']), r.get('event_1_index'))), axis=1
        )
        
        for game_id in df['game_id'].unique():
            game_sched = schedule[schedule['game_id'] == int(game_id)]
            if not game_sched.empty:
                home_team = game_sched.iloc[0].get('home_team_id')
                away_team = game_sched.iloc[0].get('away_team_id')
                
                mask_home = (df['game_id'] == game_id) & (df['team_venue'].str.lower() == 'home')
                mask_away = (df['game_id'] == game_id) & (df['team_venue'].str.lower() == 'away')
                
                df.loc[mask_home, 'team_id'] = home_team
                df.loc[mask_away, 'team_id'] = away_team
        
        df.to_csv(linked_file, index=False)
        logger.info(f"  ✓ fact_linked_events: Added FKs")
    
    def add_h2h_fkeys(self):
        """Add FKs to fact_h2h and fact_head_to_head."""
        logger.info("Adding FKs to H2H tables...")
        
        schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
        
        for table in ['fact_h2h', 'fact_head_to_head']:
            file_path = OUTPUT_DIR / f'{table}.csv'
            if not file_path.exists():
                continue
            
            df = pd.read_csv(file_path)
            
            # Add team IDs
            for game_id in df['game_id'].unique():
                game_sched = schedule[schedule['game_id'] == int(game_id)]
                if not game_sched.empty:
                    home_team = game_sched.iloc[0].get('home_team_id')
                    away_team = game_sched.iloc[0].get('away_team_id')
                    
                    df.loc[df['game_id'] == game_id, 'home_team_id'] = home_team
                    df.loc[df['game_id'] == game_id, 'away_team_id'] = away_team
            
            # Add venue IDs
            if 'venue' in df.columns:
                df['venue_id'] = df['venue'].apply(lambda x: self._lookup_id('venue', x))
            
            df.to_csv(file_path, index=False)
            logger.info(f"  ✓ {table}: Added FKs")
    
    def add_wowy_fkeys(self):
        """Add FKs to fact_wowy."""
        logger.info("Adding FKs to fact_wowy...")
        
        wowy_file = OUTPUT_DIR / 'fact_wowy.csv'
        if not wowy_file.exists():
            return
        
        df = pd.read_csv(wowy_file)
        schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
        
        # Add team IDs
        for game_id in df['game_id'].unique():
            game_sched = schedule[schedule['game_id'] == int(game_id)]
            if not game_sched.empty:
                home_team = game_sched.iloc[0].get('home_team_id')
                away_team = game_sched.iloc[0].get('away_team_id')
                
                df.loc[df['game_id'] == game_id, 'home_team_id'] = home_team
                df.loc[df['game_id'] == game_id, 'away_team_id'] = away_team
        
        # Add venue ID
        if 'venue' in df.columns:
            df['venue_id'] = df['venue'].apply(lambda x: self._lookup_id('venue', x))
        
        df.to_csv(wowy_file, index=False)
        logger.info(f"  ✓ fact_wowy: Added FKs")
    
    def add_line_combos_fkeys(self):
        """Add FKs to fact_line_combos."""
        logger.info("Adding FKs to fact_line_combos...")
        
        combos_file = OUTPUT_DIR / 'fact_line_combos.csv'
        if not combos_file.exists():
            return
        
        df = pd.read_csv(combos_file)
        schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
        
        # Add team IDs
        for game_id in df['game_id'].unique():
            game_sched = schedule[schedule['game_id'] == int(game_id)]
            if not game_sched.empty:
                home_team = game_sched.iloc[0].get('home_team_id')
                away_team = game_sched.iloc[0].get('away_team_id')
                
                df.loc[df['game_id'] == game_id, 'home_team_id'] = home_team
                df.loc[df['game_id'] == game_id, 'away_team_id'] = away_team
        
        # Add venue ID
        if 'venue' in df.columns:
            df['venue_id'] = df['venue'].apply(lambda x: self._lookup_id('venue', x))
        
        df.to_csv(combos_file, index=False)
        logger.info(f"  ✓ fact_line_combos: Added FKs")
    
    def add_goalie_fkeys(self):
        """Add FKs to fact_goalie_game_stats."""
        logger.info("Adding FKs to fact_goalie_game_stats...")
        
        goalie_file = OUTPUT_DIR / 'fact_goalie_game_stats.csv'
        if not goalie_file.exists():
            return
        
        df = pd.read_csv(goalie_file)
        schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
        
        # Add venue ID
        df['venue_id'] = df['venue'].apply(lambda x: self._lookup_id('venue', x))
        
        # Add team ID
        for game_id in df['game_id'].unique():
            game_sched = schedule[schedule['game_id'] == int(game_id)]
            if not game_sched.empty:
                home_team = game_sched.iloc[0].get('home_team_id')
                away_team = game_sched.iloc[0].get('away_team_id')
                
                mask_home = (df['game_id'] == str(game_id)) & (df['venue'] == 'home')
                mask_away = (df['game_id'] == str(game_id)) & (df['venue'] == 'away')
                
                df.loc[mask_home, 'team_id'] = home_team
                df.loc[mask_away, 'team_id'] = away_team
        
        df.to_csv(goalie_file, index=False)
        logger.info(f"  ✓ fact_goalie_game_stats: Added FKs")
    
    def add_possession_fkeys(self):
        """Add FKs to fact_possession_time."""
        logger.info("Adding FKs to fact_possession_time...")
        
        poss_file = OUTPUT_DIR / 'fact_possession_time.csv'
        if not poss_file.exists():
            return
        
        df = pd.read_csv(poss_file)
        schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
        
        # Add venue ID
        df['venue_id'] = df['venue'].apply(lambda x: self._lookup_id('venue', x))
        
        # Add team ID
        for game_id in df['game_id'].unique():
            game_sched = schedule[schedule['game_id'] == int(game_id)]
            if not game_sched.empty:
                home_team = game_sched.iloc[0].get('home_team_id')
                away_team = game_sched.iloc[0].get('away_team_id')
                
                mask_home = (df['game_id'] == str(game_id)) & (df['venue'].str.lower() == 'home')
                mask_away = (df['game_id'] == str(game_id)) & (df['venue'].str.lower() == 'away')
                
                df.loc[mask_home, 'team_id'] = home_team
                df.loc[mask_away, 'team_id'] = away_team
        
        df.to_csv(poss_file, index=False)
        logger.info(f"  ✓ fact_possession_time: Added FKs")
    
    def build_play_chains(self):
        """Build play chain descriptions for sequence/rush/cycle tables."""
        logger.info("Building play chain descriptions...")
        
        events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
        
        # Normalize game_id to int for comparison
        events['game_id'] = pd.to_numeric(events['game_id'], errors='coerce').astype('Int64')
        
        # Group events by game_id and event_index to get unique events
        unique_events = events.drop_duplicates(['game_id', 'event_index'])
        
        # Process sequences
        seq_file = OUTPUT_DIR / 'fact_sequences.csv'
        if seq_file.exists():
            seq = pd.read_csv(seq_file)
            seq['game_id'] = pd.to_numeric(seq['game_id'], errors='coerce').astype('Int64')
            
            def get_play_chain(row):
                start_idx = row.get('start_event_index')
                end_idx = row.get('end_event_index')
                game_id = row['game_id']
                
                if pd.isna(start_idx) or pd.isna(end_idx) or pd.isna(game_id):
                    return None, None
                
                chain_events = unique_events[
                    (unique_events['game_id'] == game_id) & 
                    (unique_events['event_index'] >= start_idx) &
                    (unique_events['event_index'] <= end_idx)
                ].sort_values('event_index')
                
                if chain_events.empty:
                    return None, None
                
                types = chain_events['event_type'].tolist()
                indices = chain_events['event_index'].tolist()
                
                play_chain = ' > '.join([str(t) for t in types if pd.notna(t)])
                event_chain = ','.join([str(int(i)) for i in indices if pd.notna(i)])
                
                return play_chain, event_chain
            
            chains = seq.apply(get_play_chain, axis=1, result_type='expand')
            seq['play_chain'] = chains[0]
            seq['event_chain_indices'] = chains[1]
            seq.to_csv(seq_file, index=False)
            logger.info(f"  ✓ fact_sequences: Added play chains")
        
        # Process rushes
        rush_file = OUTPUT_DIR / 'fact_rush_events.csv'
        if rush_file.exists():
            rush = pd.read_csv(rush_file)
            rush['game_id'] = pd.to_numeric(rush['game_id'], errors='coerce').astype('Int64')
            
            def get_rush_chain(row):
                # Use entry_event_index and shot_event_index for rushes
                start_idx = row.get('entry_event_index')
                end_idx = row.get('shot_event_index')
                game_id = row['game_id']
                
                if pd.isna(start_idx) or pd.isna(end_idx) or pd.isna(game_id):
                    return None, None
                
                chain_events = unique_events[
                    (unique_events['game_id'] == game_id) & 
                    (unique_events['event_index'] >= start_idx) &
                    (unique_events['event_index'] <= end_idx)
                ].sort_values('event_index')
                
                if chain_events.empty:
                    return None, None
                
                types = chain_events['event_type'].tolist()
                indices = chain_events['event_index'].tolist()
                
                play_chain = ' > '.join([str(t) for t in types if pd.notna(t)])
                event_chain = ','.join([str(int(i)) for i in indices if pd.notna(i)])
                
                return play_chain, event_chain
            
            chains = rush.apply(get_rush_chain, axis=1, result_type='expand')
            rush['play_chain'] = chains[0]
            rush['event_chain_indices'] = chains[1]
            rush.to_csv(rush_file, index=False)
            logger.info(f"  ✓ fact_rush_events: Added play chains")
        
        # Process cycles
        cycle_file = OUTPUT_DIR / 'fact_cycle_events.csv'
        if cycle_file.exists():
            cycle = pd.read_csv(cycle_file)
            cycle['game_id'] = pd.to_numeric(cycle['game_id'], errors='coerce').astype('Int64')
            
            def get_cycle_chain(row):
                start_idx = row.get('cycle_start_event_index')
                end_idx = row.get('cycle_end_event_index')
                game_id = row['game_id']
                
                if pd.isna(start_idx) or pd.isna(end_idx) or pd.isna(game_id):
                    return None, None
                
                chain_events = unique_events[
                    (unique_events['game_id'] == game_id) & 
                    (unique_events['event_index'] >= start_idx) &
                    (unique_events['event_index'] <= end_idx)
                ].sort_values('event_index')
                
                if chain_events.empty:
                    return None, None
                
                types = chain_events['event_type'].tolist()
                indices = chain_events['event_index'].tolist()
                
                play_chain = ' > '.join([str(t) for t in types if pd.notna(t)])
                event_chain = ','.join([str(int(i)) for i in indices if pd.notna(i)])
                
                return play_chain, event_chain
            
            chains = cycle.apply(get_cycle_chain, axis=1, result_type='expand')
            cycle['play_chain'] = chains[0]
            cycle['event_chain_indices'] = chains[1]
            cycle.to_csv(cycle_file, index=False)
            logger.info(f"  ✓ fact_cycle_events: Added play chains")
    
    def run_all(self):
        """Run all FK additions."""
        print("=" * 70)
        print("ADDING ALL FOREIGN KEYS")
        print("=" * 70)
        
        # Core tables first
        self.add_events_fkeys()
        self.add_shifts_fkeys()
        
        # Derived tables
        self.add_sequence_fkeys()
        self.add_rush_fkeys()
        self.add_cycle_fkeys()
        self.add_plays_fkeys()
        self.add_chains_fkeys()
        self.add_linked_events_fkeys()
        
        # Aggregated tables
        self.add_h2h_fkeys()
        self.add_wowy_fkeys()
        self.add_line_combos_fkeys()
        self.add_goalie_fkeys()
        self.add_possession_fkeys()
        
        # Play chains
        self.build_play_chains()
        
        print("\n" + "=" * 70)
        print("FK ADDITION COMPLETE")
        print("=" * 70)


def main():
    builder = FKBuilder()
    builder.run_all()


if __name__ == '__main__':
    main()
