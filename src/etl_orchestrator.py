#!/usr/bin/env python3
"""
BenchSight ETL Orchestrator
Flexible pipeline for processing hockey tracking data.

Usage:
    # Full rebuild
    python -m src.etl_orchestrator --all
    
    # Just dimensions
    python -m src.etl_orchestrator --dims
    
    # Just facts
    python -m src.etl_orchestrator --facts
    
    # Specific tables
    python -m src.etl_orchestrator --tables fact_events,fact_shifts
    
    # Specific games
    python -m src.etl_orchestrator --games 18969,18977
    
    # Append mode (don't overwrite)
    python -m src.etl_orchestrator --games 19999 --append
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_DIR = DATA_DIR / "output"
BLB_FILE = DATA_DIR / "BLB_Tables.xlsx"  # Note: in data/, not data/raw/

# All tables
DIM_TABLES = [
    # From BLB_Tables.xlsx
    'dim_player', 'dim_team', 'dim_season', 'dim_league', 'dim_schedule',
    'dim_playerurlref', 'dim_randomnames', 'dim_rinkboxcoord', 'dim_rinkcoordzones',
    # Static/derived dimensions
    'dim_position', 'dim_venue', 'dim_zone',
    'dim_event_type', 'dim_event_detail', 'dim_event_detail_2',
    'dim_zone_entry_type', 'dim_zone_exit_type', 'dim_play_detail', 'dim_play_detail_2',
    'dim_player_role', 'dim_situation', 'dim_strength', 'dim_period', 'dim_skill_tier',
    'dim_comparison_type', 'dim_composite_rating', 'dim_danger_zone',
    'dim_giveaway_type', 'dim_highlight_subtype', 'dim_highlight_type',
    'dim_micro_stat', 'dim_net_location', 'dim_pass_type',
    'dim_shift_slot', 'dim_shift_start_type', 'dim_shift_stop_type',
    'dim_shot_type', 'dim_stat', 'dim_stat_category', 'dim_stat_type',
    'dim_stoppage_type', 'dim_success', 'dim_takeaway_type',
    'dim_terminology_mapping', 'dim_turnover_quality', 'dim_turnover_type',
    'dim_game', 'dim_rink_coord'
]

FACT_TABLES = [
    'fact_gameroster', 'fact_events', 'fact_events_player', 'fact_shifts_player',
    'fact_player_game_stats', 'fact_goalie_game_stats',
    'fact_team_game_stats', 'fact_event_chains', 'fact_team_zone_time',
    'fact_h2h', 'fact_wowy', 'fact_line_combos', 'fact_rush_cycle_flags'
]

# Tracked games (excluding incomplete: 18965, 18991, 18993, 19032, 18955)
# 18955 has no tracking file
TRACKED_GAMES = ['18969', '18977', '18981', '18987']


class ETLOrchestrator:
    """Flexible ETL orchestrator for BenchSight."""
    
    def __init__(self, output_dir=OUTPUT_DIR, mode='overwrite'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.mode = mode  # 'overwrite' or 'append'
        self.stats = {'processed': 0, 'errors': 0, 'tables': []}
        
    def run(self, tables=None, games=None, dims_only=False, facts_only=False):
        """
        Run the ETL pipeline.
        
        Args:
            tables: List of specific tables to process
            games: List of specific game IDs to process
            dims_only: Only process dimension tables
            facts_only: Only process fact tables
        """
        start_time = datetime.now()
        logger.info(f"=" * 60)
        logger.info(f"BenchSight ETL Orchestrator")
        logger.info(f"Mode: {self.mode}")
        logger.info(f"=" * 60)
        
        # Determine what to process
        if tables:
            tables_to_process = tables
        elif dims_only:
            tables_to_process = DIM_TABLES
        elif facts_only:
            tables_to_process = FACT_TABLES
        else:
            tables_to_process = DIM_TABLES + FACT_TABLES
        
        games_to_process = games if games else TRACKED_GAMES
        
        logger.info(f"Tables: {len(tables_to_process)}")
        logger.info(f"Games: {games_to_process}")
        
        # Process dimensions first
        dim_tables = [t for t in tables_to_process if t.startswith('dim_')]
        if dim_tables:
            self._process_dimensions(dim_tables)
        
        # Process facts
        fact_tables = [t for t in tables_to_process if t.startswith('fact_')]
        if fact_tables:
            self._process_facts(fact_tables, games_to_process)
        
        # Summary
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"\n{'=' * 60}")
        logger.info(f"ETL Complete in {elapsed:.1f}s")
        logger.info(f"Processed: {self.stats['processed']} tables")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info(f"{'=' * 60}")
        
        return self.stats
    
    def _process_dimensions(self, tables):
        """Process dimension tables from BLB_Tables.xlsx."""
        logger.info("\n--- Processing Dimensions ---")
        
        if not BLB_FILE.exists():
            logger.error(f"BLB_Tables.xlsx not found at {BLB_FILE}")
            return
        
        blb = pd.ExcelFile(BLB_FILE)
        
        for table in tables:
            try:
                # Sheet names in BLB match table names (dim_player, dim_team, etc.)
                # Also check for the exact table name in sheets
                if table in blb.sheet_names:
                    df = pd.read_excel(blb, table)
                    self._save_table(table, df)
                else:
                    # Try without prefix for legacy sheets
                    sheet_name = table.replace('dim_', '')
                    if sheet_name in blb.sheet_names:
                        df = pd.read_excel(blb, sheet_name)
                        self._save_table(table, df)
                    else:
                        logger.debug(f"Sheet for {table} not found in BLB - may be derived from tracking")
            except Exception as e:
                logger.error(f"Error processing {table}: {e}")
                self.stats['errors'] += 1
    
    def _process_facts(self, tables, games):
        """Process fact tables from game tracking files."""
        logger.info("\n--- Processing Facts ---")
        
        for table in tables:
            try:
                if table == 'fact_events':
                    self._build_fact_events(games)
                elif table == 'fact_events_player':
                    self._build_fact_events_player(games)
                elif table == 'fact_shifts_player':
                    self._build_fact_shifts_player(games)
                elif table == 'fact_player_game_stats':
                    self._build_fact_player_game_stats(games)
                elif table == 'fact_goalie_game_stats':
                    self._build_fact_goalie_game_stats(games)
                elif table == 'fact_team_game_stats':
                    self._build_fact_team_game_stats(games)
                elif table == 'fact_event_chains':
                    self._build_fact_event_chains(games)
                elif table == 'fact_team_zone_time':
                    self._build_fact_team_zone_time(games)
                elif table == 'fact_h2h':
                    self._build_fact_h2h(games)
                elif table == 'fact_wowy':
                    self._build_fact_wowy(games)
                elif table == 'fact_line_combos':
                    self._build_fact_line_combos(games)
                elif table == 'fact_rush_cycle_flags':
                    self._add_rush_cycle_flags(games)
                elif table == 'fact_gameroster':
                    self._build_fact_gameroster()
                else:
                    logger.warning(f"No builder for {table}")
            except Exception as e:
                logger.error(f"Error processing {table}: {e}")
                self.stats['errors'] += 1
    
    def _build_fact_gameroster(self):
        """Load fact_gameroster from BLB_Tables.xlsx."""
        try:
            df = pd.read_excel(BLB_FILE, 'fact_gameroster')
            self._save_table('fact_gameroster', df)
            logger.info(f"  ✓ fact_gameroster: {len(df)} rows")
        except Exception as e:
            logger.error(f"Error loading fact_gameroster: {e}")
    
    def _build_fact_events(self, games):
        """Build fact_events (wide) from tracking files - one row per unique event."""
        all_events = []
        
        for game_id in games:
            tracking_file = RAW_DIR / "games" / game_id / f"{game_id}_tracking.xlsx"
            if tracking_file.exists():
                try:
                    events = pd.read_excel(tracking_file, 'events')
                    events['game_id'] = game_id
                    all_events.append(events)
                except Exception as e:
                    logger.warning(f"Error loading events for game {game_id}: {e}")
        
        if all_events:
            df = pd.concat(all_events, ignore_index=True)
            
            # Remove columns ending with underscore (staging columns)
            clean_cols = [c for c in df.columns if not c.endswith('_')]
            df = df[clean_cols]
            
            # Remove player-specific columns from wide table
            player_cols = ['player_role', 'role_number', 'player_id', 'player_team', 'player_game_number']
            event_cols = [c for c in df.columns if c not in player_cols]
            df = df[event_cols]
            
            # Deduplicate by event_index (events have multiple player rows)
            df_dedup = df.drop_duplicates(subset=['game_id', 'event_index'])
            
            # Normalize event_type
            if 'Type' in df_dedup.columns and 'event_type' not in df_dedup.columns:
                df_dedup['event_type'] = df_dedup['Type']
            
            # Add event_key - handle NaN
            def make_event_key(r):
                if pd.isna(r.get('event_index')):
                    return None
                return f"E{int(r['game_id']):05d}{int(r['event_index']):06d}"
            
            df_dedup = df_dedup.copy()
            df_dedup['event_key'] = df_dedup.apply(make_event_key, axis=1)
            
            # Reorder columns - keys first
            key_cols = ['event_key', 'game_id', 'period', 'event_index', 'linked_event_index',
                        'sequence_index', 'play_index', 'event_type']
            other_cols = [c for c in df_dedup.columns if c not in key_cols]
            df_dedup = df_dedup[[c for c in key_cols if c in df_dedup.columns] + other_cols]
            
            self._save_table('fact_events', df_dedup)
    
    def _build_fact_events_player(self, games):
        """Build fact_events_player (one row per player per event)."""
        all_events = []
        
        for game_id in games:
            tracking_file = RAW_DIR / "games" / game_id / f"{game_id}_tracking.xlsx"
            if tracking_file.exists():
                try:
                    events = pd.read_excel(tracking_file, 'events')
                    events['game_id'] = game_id
                    all_events.append(events)
                except Exception as e:
                    logger.warning(f"Error loading events for game {game_id}: {e}")
        
        if all_events:
            df = pd.concat(all_events, ignore_index=True)
            
            # Remove columns ending with underscore (staging columns)
            clean_cols = [c for c in df.columns if not c.endswith('_')]
            df = df[clean_cols]
            
            # Normalize column names
            df = self._normalize_event_columns(df)
            
            # Add keys - handle NaN values
            def make_event_key(r):
                if pd.isna(r.get('event_index')):
                    return None
                return f"E{int(r['game_id']):05d}{int(r['event_index']):06d}"
            
            def make_event_player_key(r):
                if pd.isna(r.get('event_index')):
                    return None
                role_num = r.get('role_number', 0)
                role_num = 0 if pd.isna(role_num) else int(role_num)
                return f"P{int(r['game_id']):05d}{int(r['event_index']):05d}{role_num:01d}"
            
            df['event_key'] = df.apply(make_event_key, axis=1)
            df['event_player_key'] = df.apply(make_event_player_key, axis=1)
            
            # Reorder columns - keys first
            key_cols = ['event_player_key', 'event_key', 'game_id', 'player_id', 'event_index', 
                        'player_role', 'role_number', 'period', 'event_type']
            other_cols = [c for c in df.columns if c not in key_cols]
            df = df[[c for c in key_cols if c in df.columns] + other_cols]
            
            # Keep all rows (one per player per event) - don't deduplicate
            self._save_table('fact_events_player', df)
    
    def _normalize_event_columns(self, df):
        """Standardize column names for events."""
        # Map raw column names to standard names
        column_map = {
            'Type': 'event_type',
            'event_type_': 'event_type',
            'event_detail_': 'event_detail_raw',
            'event_detail_2_': 'event_detail_2_raw',
            'event_successful_': 'event_successful_raw',
            'play_detail1_': 'play_detail_1_raw',
            'play_detail2_': 'play_detail_2_raw',
        }
        
        for old, new in column_map.items():
            if old in df.columns and new not in df.columns:
                df[new] = df[old]
        
        # Ensure event_type exists
        if 'event_type' not in df.columns and 'Type' in df.columns:
            df['event_type'] = df['Type']
        
        # Add player_name from roster lookup (or extract from player_id)
        if 'player_name' not in df.columns:
            # Try to get from roster
            roster_file = self.output_dir / "fact_gameroster.csv"
            if roster_file.exists():
                roster = pd.read_csv(roster_file, dtype=str)
                player_lookup = roster.set_index('player_id')['player_full_name'].to_dict()
                df['player_name'] = df['player_id'].map(player_lookup)
            else:
                df['player_name'] = df['player_id']  # Fallback
        
        # Standardize play_detail columns
        if 'play_detail' not in df.columns:
            if 'play_detail1' in df.columns:
                df['play_detail'] = df['play_detail1']
            elif 'play_detail1_' in df.columns:
                df['play_detail'] = df['play_detail1_']
        
        return df
    
    def _build_fact_shifts_player(self, games):
        """Build fact_shifts_player with logical shift tracking."""
        all_shifts = []
        
        # Load roster for player_id lookup
        roster_file = self.output_dir / "fact_gameroster.csv"
        roster = None
        if roster_file.exists():
            roster = pd.read_csv(roster_file, dtype={'game_id': str, 'player_game_number': str, 'player_id': str})
            roster['game_id'] = roster['game_id'].astype(str)
        
        for game_id in games:
            tracking_file = RAW_DIR / "games" / game_id / f"{game_id}_tracking.xlsx"
            if tracking_file.exists():
                try:
                    shifts = pd.read_excel(tracking_file, 'shifts')
                    shifts['game_id'] = int(game_id)
                    
                    # Unpivot to player-level
                    player_shifts = self._unpivot_shifts(shifts, game_id)
                    
                    # Enrich with player_id and player_name from roster
                    if roster is not None:
                        player_shifts = self._enrich_shifts_with_roster(player_shifts, roster, game_id)
                    
                    # Add logical shift tracking
                    player_shifts = self._add_logical_shifts(player_shifts)
                    
                    all_shifts.append(player_shifts)
                except Exception as e:
                    logger.warning(f"Error loading shifts for game {game_id}: {e}")
        
        if all_shifts:
            df = pd.concat(all_shifts, ignore_index=True)
            self._save_table('fact_shifts_player', df)
    
    def _enrich_shifts_with_roster(self, shifts, roster, game_id):
        """Add player_id and player_name from roster."""
        # Create lookup from roster
        game_roster = roster[roster['game_id'] == str(game_id)].copy()
        
        if game_roster.empty:
            logger.warning(f"No roster found for game {game_id}")
            shifts['player_id'] = None
            shifts['player_name'] = None
            return shifts
        
        # Known venue swaps (tracking file has home/away backwards)
        VENUE_SWAP_GAMES = ['18987']
        
        # Map venue to team_venue format
        game_roster['venue'] = game_roster['team_venue'].str.lower()
        game_roster['player_number'] = game_roster['player_game_number'].astype(str)
        
        # Create lookup dict: (venue, player_number) -> (player_id, player_name)
        lookup = {}
        for _, row in game_roster.iterrows():
            roster_venue = row['venue']
            
            # Handle venue swap for known games
            if str(game_id) in VENUE_SWAP_GAMES:
                roster_venue = 'away' if roster_venue == 'home' else 'home'
            
            key = (roster_venue, str(int(float(row['player_number']))) if row['player_number'] else None)
            lookup[key] = (row['player_id'], row['player_full_name'])
        
        # Apply lookup
        player_ids = []
        player_names = []
        for _, shift in shifts.iterrows():
            key = (shift['venue'], str(int(shift['player_number'])) if pd.notna(shift['player_number']) else None)
            if key in lookup:
                player_ids.append(lookup[key][0])
                player_names.append(lookup[key][1])
            else:
                player_ids.append(None)
                player_names.append(None)
        
        shifts['player_id'] = player_ids
        shifts['player_name'] = player_names
        
        return shifts
        
        if all_shifts:
            df = pd.concat(all_shifts, ignore_index=True)
            self._save_table('fact_shifts_player', df)
    
    def _unpivot_shifts(self, shifts, game_id):
        """Unpivot shifts from wide to player-level."""
        player_cols = {
            'home': ['home_forward_1', 'home_forward_2', 'home_forward_3',
                     'home_defense_1', 'home_defense_2', 'home_xtra', 'home_goalie'],
            'away': ['away_forward_1', 'away_forward_2', 'away_forward_3',
                     'away_defense_1', 'away_defense_2', 'away_xtra', 'away_goalie']
        }
        
        rows = []
        
        for idx, shift in shifts.iterrows():
            # Detect goal from shift_stop_type (exact match to avoid "Home Goalie" matching)
            stop_type = str(shift.get('shift_stop_type', '')).strip().lower()
            home_goal_this_shift = 1 if stop_type == 'home goal' else 0
            away_goal_this_shift = 1 if stop_type == 'away goal' else 0
            
            for venue, cols in player_cols.items():
                for col in cols:
                    if col in shift and pd.notna(shift[col]):
                        player_num = shift[col]
                        slot = col.replace('home_', '').replace('away_', '')
                        
                        # Get plus/minus values for this venue from source
                        if venue == 'home':
                            pm_plus_ev = float(shift.get('home_team_plus', 0) or 0)
                            pm_minus_ev = float(shift.get('home_team_minus', 0) or 0)
                            team_en = float(shift.get('home_team_en', 0) or 0)
                            opp_en = float(shift.get('away_team_en', 0) or 0)
                            team_pp = float(shift.get('home_team_pp', 0) or 0)
                            team_pk = float(shift.get('home_team_pk', 0) or 0)
                            goal_for_this_shift = home_goal_this_shift
                            goal_against_this_shift = away_goal_this_shift
                        else:
                            pm_plus_ev = float(shift.get('away_team_plus', 0) or 0)
                            pm_minus_ev = float(shift.get('away_team_minus', 0) or 0)
                            team_en = float(shift.get('away_team_en', 0) or 0)
                            opp_en = float(shift.get('home_team_en', 0) or 0)
                            team_pp = float(shift.get('away_team_pp', 0) or 0)
                            team_pk = float(shift.get('away_team_pk', 0) or 0)
                            goal_for_this_shift = away_goal_this_shift
                            goal_against_this_shift = home_goal_this_shift
                        
                        # Generate keys
                        shift_key = f"S{int(game_id):05d}{int(shift['shift_index']):06d}"
                        slot_num = {'forward_1': 1, 'forward_2': 2, 'forward_3': 3,
                                   'defense_1': 4, 'defense_2': 5, 'xtra': 6, 'goalie': 7}.get(slot, 0)
                        venue_num = 0 if venue == 'home' else 1
                        shift_player_key = f"L{int(game_id):05d}{int(shift['shift_index']):04d}{venue_num}{slot_num}"
                        
                        rows.append({
                            'shift_player_key': shift_player_key,
                            'shift_key': shift_key,
                            'game_id': int(game_id),
                            'shift_index': shift['shift_index'],
                            'player_number': int(player_num),
                            'venue': venue,
                            'slot': slot,
                            'period': shift.get('Period', shift.get('period')),
                            'shift_duration': shift.get('shift_duration'),
                            'situation': shift.get('situation'),
                            'strength': shift.get('strength'),
                            'stoppage_time': shift.get('stoppage_time', 0),
                            # Traditional +/- from source (EV only - excludes PP goals)
                            'pm_plus_ev': pm_plus_ev,
                            'pm_minus_ev': pm_minus_ev,
                            # All goals from shift_stop_type (for total +/-)
                            'goal_for': goal_for_this_shift,
                            'goal_against': goal_against_this_shift,
                            # Situation flags
                            'team_en': team_en,
                            'opp_en': opp_en,
                            'team_pp': team_pp,
                            'team_pk': team_pk,
                        })
        
        return pd.DataFrame(rows)
    
    def _add_logical_shifts(self, df):
        """Add logical shift tracking columns."""
        if df.empty:
            return df
        
        # Sort by game, player, shift_index
        df = df.sort_values(['game_id', 'player_number', 'venue', 'shift_index'])
        
        # Calculate logical shifts per player
        result = []
        for (game_id, player_num, venue), group in df.groupby(['game_id', 'player_number', 'venue']):
            group = group.copy()
            group = group.sort_values('shift_index')
            
            logical_shift = 1
            segment = 1
            prev_idx = None
            prev_period = None
            
            logical_shifts = []
            segments = []
            cumulative_dur = []
            running_dur = 0
            logical_dur = 0
            
            for _, row in group.iterrows():
                curr_idx = row['shift_index']
                curr_period = row['period']
                
                # Check if new logical shift
                if prev_idx is not None:
                    if curr_idx != prev_idx + 1 or curr_period != prev_period:
                        logical_shift += 1
                        segment = 1
                        logical_dur = 0
                    else:
                        segment += 1
                
                logical_shifts.append(logical_shift)
                segments.append(segment)
                
                dur = row['shift_duration'] if pd.notna(row['shift_duration']) else 0
                logical_dur += dur
                running_dur += dur
                cumulative_dur.append(logical_dur)
                
                prev_idx = curr_idx
                prev_period = curr_period
            
            group['logical_shift_number'] = logical_shifts
            group['shift_segment'] = segments
            group['cumulative_shift_duration'] = cumulative_dur
            group['running_toi'] = group['shift_duration'].cumsum()
            
            # Playing duration
            stoppage = group['stoppage_time'].fillna(0)
            group['playing_duration'] = group['shift_duration'] - stoppage
            group['running_playing_toi'] = group['playing_duration'].cumsum()
            
            result.append(group)
        
        return pd.concat(result, ignore_index=True) if result else df
    
    def _build_fact_player_game_stats(self, games):
        """Build player game stats using VALIDATED counting rules.
        
        IMPORTANT: This method now preserves existing enhanced columns!
        If fact_player_game_stats.csv already exists with additional columns
        (e.g., from enhance_all_stats.py), those columns will be preserved.
        """
        logger.info("Building fact_player_game_stats with validated rules...")
        
        # Load events
        events_file = self.output_dir / "fact_events_player.csv"
        shifts_file = self.output_dir / "fact_shifts_player.csv"
        
        if not events_file.exists() or not shifts_file.exists():
            logger.error("Required files not found - run full ETL first")
            return
        
        events = pd.read_csv(events_file, dtype=str)
        shifts = pd.read_csv(shifts_file)
        
        # Load dim_player for skill ratings
        player_file = self.output_dir / "dim_player.csv"
        player_ratings = {}
        if player_file.exists():
            dim_player = pd.read_csv(player_file, dtype=str)
            # Check for rating column (could be current_skill_rating or player_rating)
            rating_col = None
            for col in ['current_skill_rating', 'player_rating', 'skill_rating']:
                if col in dim_player.columns:
                    rating_col = col
                    break
            if rating_col:
                player_ratings = dim_player.set_index('player_id')[rating_col].to_dict()
        
        # =================================================================
        # BUG FIX: Load existing enhanced columns to preserve them
        # =================================================================
        existing_file = self.output_dir / "fact_player_game_stats.csv"
        existing_enhanced_cols = {}
        existing_df = None
        if existing_file.exists():
            try:
                existing_df = pd.read_csv(existing_file)
                existing_col_count = len(existing_df.columns)
                logger.info(f"  Found existing fact_player_game_stats with {existing_col_count} columns")
                if existing_col_count > 100:  # Has enhanced columns
                    logger.info(f"  Will preserve {existing_col_count} enhanced columns")
            except Exception as e:
                logger.warning(f"  Could not load existing file: {e}")
                existing_df = None
        
        if games != TRACKED_GAMES:
            events = events[events['game_id'].isin(games)]
            shifts = shifts[shifts['game_id'].isin([int(g) for g in games])]
        
        # Get unique player-game combinations
        player_games = events.groupby(['game_id', 'player_id', 'player_name']).size().reset_index()[['game_id', 'player_id', 'player_name']]
        
        stats_rows = []
        for _, row in player_games.iterrows():
            game_id = row['game_id']
            player_id = row['player_id']
            player_name = row['player_name']
            
            player_events = events[(events['game_id'] == game_id) & (events['player_id'] == player_id)]
            player_shifts = shifts[(shifts['game_id'] == int(game_id)) & (shifts['player_id'] == player_id)]
            
            # Get ALL game events and shifts for Corsi/plus-minus calculations
            all_game_events = events[events['game_id'] == game_id]
            all_game_shifts = shifts[shifts['game_id'] == int(game_id)]
            
            stats = self._calculate_player_stats(player_events, player_shifts, 
                                                  all_game_events, all_game_shifts,
                                                  player_id, player_ratings)
            stats['game_id'] = game_id
            stats['player_id'] = player_id
            stats['player_name'] = player_name
            # Generate player_game_key (PG + game_id + player_id hash)
            stats['player_game_key'] = f"PG{int(game_id):05d}{abs(hash(player_id)) % 100000:05d}"
            stats_rows.append(stats)
        
        if stats_rows:
            df = pd.DataFrame(stats_rows)
            
            # =================================================================
            # BUG FIX: Merge with existing enhanced columns
            # =================================================================
            if existing_df is not None and len(existing_df.columns) > len(df.columns):
                logger.info(f"  Merging: new {len(df.columns)} cols with existing {len(existing_df.columns)} cols")
                
                # Identify columns that exist in existing_df but not in new df
                new_cols = set(df.columns)
                enhanced_cols = [c for c in existing_df.columns if c not in new_cols]
                
                if enhanced_cols:
                    # Convert game_id to same type for merge
                    existing_df['game_id'] = existing_df['game_id'].astype(str)
                    df['game_id'] = df['game_id'].astype(str)
                    
                    # Merge on player_game_key (preferred) or game_id + player_id
                    merge_cols = ['player_game_key'] if 'player_game_key' in existing_df.columns else ['game_id', 'player_id']
                    
                    # Get just the enhanced columns + merge keys from existing
                    enhanced_subset = existing_df[merge_cols + enhanced_cols].copy()
                    
                    # Merge
                    df = df.merge(enhanced_subset, on=merge_cols, how='left')
                    logger.info(f"  Preserved {len(enhanced_cols)} enhanced columns, total: {len(df.columns)}")
            
            # Reorder columns - keys first
            key_cols = ['player_game_key', 'game_id', 'player_id', 'player_name']
            other_cols = [c for c in df.columns if c not in key_cols]
            df = df[key_cols + other_cols]
            
            logger.info(f"  Final column count: {len(df.columns)}")
            self._save_table('fact_player_game_stats', df)
    
    def _calculate_player_stats(self, events, shifts, all_game_events=None, all_game_shifts=None, 
                                  player_id=None, player_ratings=None):
        """Calculate all stats using validated rules."""
        stats = {}
        
        # SCORING (validated rules)
        stats['goals'] = len(events[(events['event_type'] == 'Goal') & 
                                    (events['player_role'] == 'event_team_player_1')])
        stats['assists'] = len(events[events['play_detail'].str.contains('Assist', na=False)])
        stats['points'] = stats['goals'] + stats['assists']
        
        # SHOTS
        shots = events[(events['event_type'] == 'Shot') & (events['player_role'] == 'event_team_player_1')]
        stats['shots'] = len(shots)
        stats['sog'] = len(shots[shots['event_detail'].str.contains('OnNet|Goal', na=False, regex=True)])
        stats['shots_blocked'] = len(shots[shots['event_detail'].str.contains('Blocked', na=False) & 
                                           ~shots['event_detail'].str.contains('SameTeam', na=False)])
        stats['shots_missed'] = len(shots[shots['event_detail'].str.contains('Missed', na=False)])
        stats['shooting_pct'] = round(stats['goals'] / stats['shots'] * 100, 1) if stats['shots'] > 0 else 0
        
        # PASSING
        passes = events[(events['event_type'] == 'Pass') & (events['player_role'] == 'event_team_player_1')]
        stats['pass_attempts'] = len(passes)
        stats['pass_completed'] = len(passes[passes['event_detail'] == 'Pass_Completed'])
        stats['pass_pct'] = round(stats['pass_completed'] / stats['pass_attempts'] * 100, 1) if stats['pass_attempts'] > 0 else 0
        
        # FACEOFFS
        stats['fo_wins'] = len(events[(events['event_type'] == 'Faceoff') & 
                                      (events['player_role'] == 'event_team_player_1')])
        stats['fo_losses'] = len(events[(events['event_type'] == 'Faceoff') & 
                                        (events['player_role'] == 'opp_team_player_1')])
        stats['fo_total'] = stats['fo_wins'] + stats['fo_losses']
        stats['fo_pct'] = round(stats['fo_wins'] / stats['fo_total'] * 100, 1) if stats['fo_total'] > 0 else 0
        
        # ZONE PLAY
        stats['zone_entries'] = len(events[(events['event_detail'].str.contains('Entry', na=False)) & 
                                           (events['player_role'] == 'event_team_player_1')])
        stats['zone_exits'] = len(events[(events['event_detail'].str.contains('Exit', na=False)) & 
                                         (events['player_role'] == 'event_team_player_1')])
        
        # TURNOVERS
        stats['giveaways'] = len(events[(events['event_detail'].str.contains('Giveaway', na=False)) & 
                                        (events['player_role'] == 'event_team_player_1')])
        stats['takeaways'] = len(events[(events['event_detail'].str.contains('Takeaway', na=False)) & 
                                        (events['player_role'] == 'event_team_player_1')])
        
        # TIME ON ICE
        if not shifts.empty:
            stats['toi_seconds'] = shifts['shift_duration'].sum()
            stats['toi_minutes'] = round(stats['toi_seconds'] / 60, 1)
            # Playing TOI = TOI minus stoppage time
            if 'playing_duration' in shifts.columns:
                stats['playing_toi_seconds'] = shifts['playing_duration'].sum()
            else:
                stoppage = shifts['stoppage_time'].sum() if 'stoppage_time' in shifts.columns else 0
                stats['playing_toi_seconds'] = stats['toi_seconds'] - stoppage
            stats['playing_toi_minutes'] = round(stats['playing_toi_seconds'] / 60, 1)
            stats['stoppage_seconds'] = stats['toi_seconds'] - stats['playing_toi_seconds']
            
            stats['shift_count'] = len(shifts)
            stats['logical_shifts'] = shifts['logical_shift_number'].max() if 'logical_shift_number' in shifts.columns else stats['shift_count']
            stats['avg_shift'] = round(stats['toi_seconds'] / stats['logical_shifts'], 1) if stats['logical_shifts'] > 0 else 0
            stats['avg_playing_shift'] = round(stats['playing_toi_seconds'] / stats['logical_shifts'], 1) if stats['logical_shifts'] > 0 else 0
        else:
            stats['toi_seconds'] = 0
            stats['toi_minutes'] = 0
            stats['playing_toi_seconds'] = 0
            stats['playing_toi_minutes'] = 0
            stats['stoppage_seconds'] = 0
            stats['shift_count'] = 0
            stats['logical_shifts'] = 0
            stats['avg_shift'] = 0
            stats['avg_playing_shift'] = 0
        
        # PER-60 RATES (per 60 minutes of ice time)
        toi_60 = stats['toi_seconds'] / 3600 if stats['toi_seconds'] > 0 else 0
        playing_toi_60 = stats['playing_toi_seconds'] / 3600 if stats['playing_toi_seconds'] > 0 else 0
        
        # Standard per-60 (based on total TOI)
        stats['goals_per_60'] = round(stats['goals'] / toi_60, 2) if toi_60 > 0 else 0
        stats['assists_per_60'] = round(stats['assists'] / toi_60, 2) if toi_60 > 0 else 0
        stats['points_per_60'] = round(stats['points'] / toi_60, 2) if toi_60 > 0 else 0
        stats['shots_per_60'] = round(stats['shots'] / toi_60, 2) if toi_60 > 0 else 0
        
        # Playing per-60 (based on playing TOI - excludes stoppages)
        stats['goals_per_60_playing'] = round(stats['goals'] / playing_toi_60, 2) if playing_toi_60 > 0 else 0
        stats['assists_per_60_playing'] = round(stats['assists'] / playing_toi_60, 2) if playing_toi_60 > 0 else 0
        stats['points_per_60_playing'] = round(stats['points'] / playing_toi_60, 2) if playing_toi_60 > 0 else 0
        stats['shots_per_60_playing'] = round(stats['shots'] / playing_toi_60, 2) if playing_toi_60 > 0 else 0
        
        # DEFENSIVE STATS
        stats['blocks'] = len(events[events['play_detail'].str.contains('Block', na=False)])
        stats['hits'] = len(events[(events['event_type'] == 'Hit') & 
                                   (events['player_role'] == 'event_team_player_1')])
        
        # PUCK BATTLES
        stats['puck_battles'] = len(events[(events['event_type'] == 'LoosePuck')])
        stats['puck_battle_wins'] = len(events[(events['event_type'] == 'LoosePuck') & 
                                               (events['player_role'] == 'event_team_player_1')])
        
        # POSSESSION STATS
        stats['retrievals'] = len(events[(events['event_detail'].str.contains('Retrieval|Recovery', na=False, regex=True)) & 
                                         (events['player_role'] == 'event_team_player_1')])
        
        # =================================================================
        # CORSI / FENWICK / PLUS-MINUS (require all game data)
        # =================================================================
        stats['corsi_for'] = 0
        stats['corsi_against'] = 0
        stats['fenwick_for'] = 0
        stats['fenwick_against'] = 0
        stats['cf_pct'] = 0
        stats['ff_pct'] = 0
        stats['opp_avg_rating'] = 0
        stats['skill_diff'] = 0
        
        # Plus/Minus: 3 versions x 3 columns = 9 columns
        # 1. Traditional (EV only)
        stats['plus_ev'] = 0
        stats['minus_ev'] = 0
        stats['plus_minus_ev'] = 0
        # 2. Total (all goals)
        stats['plus_total'] = 0
        stats['minus_total'] = 0
        stats['plus_minus_total'] = 0
        # 3. EN Adjusted
        stats['plus_en_adj'] = 0
        stats['minus_en_adj'] = 0
        stats['plus_minus_en_adj'] = 0
        
        if all_game_events is not None and all_game_shifts is not None and not shifts.empty:
            # Get player's team venue (normalize to lowercase)
            player_venue = shifts['venue'].iloc[0].lower() if 'venue' in shifts.columns else None
            
            if player_venue:
                opp_venue = 'away' if player_venue == 'home' else 'home'
                
                # Get shift indexes when player was on ice
                player_shift_indexes = set(shifts['shift_index'].unique())
                
                # Filter events to those during player's shifts
                if 'shift_index' in all_game_events.columns:
                    # Convert shift_index to int for matching
                    all_game_events_copy = all_game_events.copy()
                    all_game_events_copy['shift_index_int'] = pd.to_numeric(all_game_events_copy['shift_index'], errors='coerce')
                    on_ice_events = all_game_events_copy[
                        all_game_events_copy['shift_index_int'].isin(player_shift_indexes)
                    ]
                else:
                    on_ice_events = all_game_events  # Fallback: use all events
                
                if len(on_ice_events) > 0:
                    # Normalize team_venue to lowercase for comparison
                    on_ice_events = on_ice_events.copy()
                    on_ice_events['team_venue_lower'] = on_ice_events['team_venue'].str.lower()
                    
                    # CORSI: All shot attempts (shots + goals)
                    shot_events = on_ice_events[on_ice_events['event_type'].isin(['Shot', 'Goal'])]
                    
                    # For team: shots by player's team
                    team_shots = shot_events[shot_events['team_venue_lower'] == player_venue]
                    opp_shots = shot_events[shot_events['team_venue_lower'] == opp_venue]
                    
                    stats['corsi_for'] = len(team_shots.drop_duplicates(subset=['event_index']) if 'event_index' in team_shots.columns else team_shots)
                    stats['corsi_against'] = len(opp_shots.drop_duplicates(subset=['event_index']) if 'event_index' in opp_shots.columns else opp_shots)
                    
                    # FENWICK: Corsi minus blocked shots (need to deduplicate!)
                    team_blocked_events = team_shots[team_shots['event_detail'].str.contains('Blocked', na=False)]
                    opp_blocked_events = opp_shots[opp_shots['event_detail'].str.contains('Blocked', na=False)]
                    
                    team_blocked = len(team_blocked_events.drop_duplicates(subset=['event_index'])) if 'event_index' in team_blocked_events.columns else len(team_blocked_events)
                    opp_blocked = len(opp_blocked_events.drop_duplicates(subset=['event_index'])) if 'event_index' in opp_blocked_events.columns else len(opp_blocked_events)
                    
                    stats['fenwick_for'] = stats['corsi_for'] - team_blocked
                    stats['fenwick_against'] = stats['corsi_against'] - opp_blocked
                    
                    # CF% and FF%
                    corsi_total = stats['corsi_for'] + stats['corsi_against']
                    fenwick_total = stats['fenwick_for'] + stats['fenwick_against']
                    stats['cf_pct'] = round(stats['corsi_for'] / corsi_total * 100, 1) if corsi_total > 0 else 50.0
                    stats['ff_pct'] = round(stats['fenwick_for'] / fenwick_total * 100, 1) if fenwick_total > 0 else 50.0
                
                # =================================================================
                # PLUS/MINUS - Three versions, 3 columns each (9 total)
                # Traditional: EV only (from pm_plus_ev/pm_minus_ev)
                # Total: All goals (from goal_for/goal_against via shift_stop_type)
                # EN Adj: Traditional but no minus for EN goals against (when my team has empty net)
                # =================================================================
                
                # 1. Traditional +/- (EV only) - directly from source pm values
                ev_plus = shifts['pm_plus_ev'].sum()
                ev_minus = shifts['pm_minus_ev'].sum()  # Already negative in source
                stats['plus_ev'] = int(ev_plus)
                stats['minus_ev'] = int(ev_minus)
                stats['plus_minus_ev'] = stats['plus_ev'] + stats['minus_ev']
                
                # 2. Total +/- (all goals from shift_stop_type)
                total_gf = shifts['goal_for'].sum()
                total_ga = shifts['goal_against'].sum()
                stats['plus_total'] = int(total_gf)
                stats['minus_total'] = -int(total_ga)  # Store as negative
                stats['plus_minus_total'] = stats['plus_total'] + stats['minus_total']
                
                # 3. EN Adjusted +/- (Traditional but no minus when MY team has empty net)
                # team_en=1 means player's team pulled their goalie
                # If opponent scores when team_en=1, no minus charged
                if 'team_en' in shifts.columns:
                    en_ga = shifts[(shifts['pm_minus_ev'] < 0) & (shifts['team_en'] == 1)]['pm_minus_ev'].sum()
                    stats['plus_en_adj'] = stats['plus_ev']  # Same as traditional
                    stats['minus_en_adj'] = int(ev_minus - en_ga)  # Remove EN goals against
                    stats['plus_minus_en_adj'] = stats['plus_en_adj'] + stats['minus_en_adj']
                else:
                    stats['plus_en_adj'] = stats['plus_ev']
                    stats['minus_en_adj'] = stats['minus_ev']
                    stats['plus_minus_en_adj'] = stats['plus_minus_ev']
                
                # SKILL DIFFERENTIAL
                if player_ratings and player_id:
                    try:
                        player_rating = float(player_ratings.get(player_id, 5.0))
                    except (ValueError, TypeError):
                        player_rating = 5.0
                    
                    stats['player_rating'] = player_rating
                    
                    # Get opponents on ice during player's shifts
                    opp_on_ice = all_game_shifts[
                        (all_game_shifts['shift_index'].isin(player_shift_indexes)) &
                        (all_game_shifts['venue'] == opp_venue)
                    ]['player_id'].unique()
                    
                    if len(opp_on_ice) > 0:
                        opp_ratings = []
                        for opp_id in opp_on_ice:
                            try:
                                opp_r = float(player_ratings.get(opp_id, 5.0))
                                opp_ratings.append(opp_r)
                            except (ValueError, TypeError):
                                opp_ratings.append(5.0)
                        
                        stats['opp_avg_rating'] = round(sum(opp_ratings) / len(opp_ratings), 2) if opp_ratings else 5.0
                        stats['skill_diff'] = round(player_rating - stats['opp_avg_rating'], 2)
                    else:
                        stats['opp_avg_rating'] = 5.0
                        stats['skill_diff'] = 0
                else:
                    stats['player_rating'] = 5.0
        
        return stats
    
    def _build_fact_goalie_game_stats(self, games):
        """Build goalie game stats."""
        logger.info("Building fact_goalie_game_stats...")
        
        events_file = self.output_dir / "fact_events_player.csv"
        shifts_file = self.output_dir / "fact_shifts_player.csv"
        
        if not events_file.exists():
            logger.error("fact_events_player.csv not found")
            return
        
        events = pd.read_csv(events_file, dtype=str)
        shifts = pd.read_csv(shifts_file)
        
        # Find goalies from shifts
        goalies = shifts[shifts['slot'] == 'goalie'][['game_id', 'player_number', 'venue']].drop_duplicates()
        
        stats_rows = []
        for _, goalie in goalies.iterrows():
            game_id = str(goalie['game_id'])
            
            # Find player_id from events
            goalie_events = events[(events['game_id'] == game_id) & 
                                   (events['event_type'] == 'Save') &
                                   (events['player_role'] == 'event_team_player_1')]
            
            if goalie_events.empty:
                continue
            
            player_id = goalie_events['player_id'].iloc[0]
            player_name = goalie_events['player_name'].iloc[0]
            
            ge = events[(events['game_id'] == game_id) & (events['player_id'] == player_id)]
            # Fix: Filter goalie shifts by player_id, not just slot
            gs = shifts[(shifts['game_id'] == int(game_id)) & (shifts['player_id'] == player_id)]
            
            # Calculate TOI stats
            toi_seconds = gs['shift_duration'].sum() if not gs.empty else 0
            if 'playing_duration' in gs.columns and not gs.empty:
                playing_toi_seconds = gs['playing_duration'].sum()
            else:
                stoppage = gs['stoppage_time'].sum() if 'stoppage_time' in gs.columns and not gs.empty else 0
                playing_toi_seconds = toi_seconds - stoppage
            
            stats = {
                'game_id': game_id,
                'player_id': player_id,
                'player_name': player_name,
                'saves': len(ge[(ge['event_type'] == 'Save') & (ge['player_role'] == 'event_team_player_1')]),
                'goals_against': len(ge[(ge['event_type'] == 'Goal') & (ge['player_role'] == 'opp_team_player_1')]),
                'toi_seconds': toi_seconds,
                'toi_minutes': round(toi_seconds / 60, 1),
                'playing_toi_seconds': playing_toi_seconds,
                'playing_toi_minutes': round(playing_toi_seconds / 60, 1),
                'stoppage_seconds': toi_seconds - playing_toi_seconds,
            }
            stats['shots_faced'] = stats['saves'] + stats['goals_against']
            stats['save_pct'] = round(stats['saves'] / stats['shots_faced'] * 100, 1) if stats['shots_faced'] > 0 else 0
            stats['gaa'] = round((stats['goals_against'] / stats['toi_minutes']) * 60, 2) if stats['toi_minutes'] > 0 else 0
            # GAA based on playing time only
            stats['gaa_playing'] = round((stats['goals_against'] / stats['playing_toi_minutes']) * 60, 2) if stats['playing_toi_minutes'] > 0 else 0
            
            # Generate goalie_game_key
            stats['goalie_game_key'] = f"GG{int(stats['game_id']):05d}{abs(hash(player_id)) % 100000:05d}"
            
            stats_rows.append(stats)
        
        if stats_rows:
            df = pd.DataFrame(stats_rows)
            # Fix: Deduplicate by game_id + player_id (same goalie found from both venue slots)
            df = df.drop_duplicates(subset=['game_id', 'player_id'])
            # Reorder columns - keys first
            key_cols = ['goalie_game_key', 'game_id', 'player_id', 'player_name']
            other_cols = [c for c in df.columns if c not in key_cols]
            df = df[key_cols + other_cols]
            self._save_table('fact_goalie_game_stats', df)
    
    def _build_fact_team_game_stats(self, games):
        """Build team game stats by aggregating player stats."""
        logger.info("Building fact_team_game_stats...")
        
        player_stats_file = self.output_dir / "fact_player_game_stats.csv"
        events_file = self.output_dir / "fact_events_player.csv"
        
        if not player_stats_file.exists() or not events_file.exists():
            logger.error("Required files not found - run player stats first")
            return
        
        player_stats = pd.read_csv(player_stats_file)
        events = pd.read_csv(events_file, dtype=str)
        
        team_rows = []
        for game_id in games:
            game_events = events[events['game_id'] == str(game_id)]
            
            if game_events.empty:
                continue
            
            for venue in ['Home', 'Away']:
                # Get player_ids for this venue using team_venue column
                venue_events = game_events[game_events['team_venue'] == venue]
                team_player_ids = venue_events['player_id'].dropna().unique()
                
                if len(team_player_ids) == 0:
                    continue
                
                # Calculate stats directly from events for this team
                team_ev = venue_events[venue_events['player_role'] == 'event_team_player_1']
                
                stats = {
                    'game_id': game_id,
                    'venue': venue,
                    'goals': len(team_ev[team_ev['event_type'] == 'Goal']),
                    'shots': len(team_ev[team_ev['event_type'] == 'Shot']),
                    'fo_wins': len(team_ev[team_ev['event_type'] == 'Faceoff']),
                    'giveaways': len(team_ev[team_ev['event_detail'].str.contains('Giveaway', na=False)]),
                    'takeaways': len(team_ev[team_ev['event_detail'].str.contains('Takeaway', na=False)]),
                    'zone_entries': len(team_ev[team_ev['event_detail'].str.contains('Entry', na=False)]),
                    'zone_exits': len(team_ev[team_ev['event_detail'].str.contains('Exit', na=False)]),
                    'pass_attempts': len(team_ev[team_ev['event_type'] == 'Pass']),
                    'pass_completed': len(team_ev[(team_ev['event_type'] == 'Pass') & 
                                                   (team_ev['event_detail'] == 'Pass_Completed')]),
                }
                
                # Get faceoff losses (where player was opp_team_player_1)
                opp_venue = 'Away' if venue == 'Home' else 'Home'
                opp_events = game_events[game_events['team_venue'] == opp_venue]
                stats['fo_losses'] = len(opp_events[(opp_events['event_type'] == 'Faceoff') & 
                                                     (opp_events['player_role'] == 'event_team_player_1')])
                
                # SOG from shots with OnNet
                shots = team_ev[team_ev['event_type'] == 'Shot']
                stats['sog'] = len(shots[shots['event_detail'].str.contains('OnNet|Goal', na=False, regex=True)])
                
                # Derived stats
                stats['fo_total'] = stats['fo_wins'] + stats['fo_losses']
                stats['fo_pct'] = round(stats['fo_wins'] / stats['fo_total'] * 100, 1) if stats['fo_total'] > 0 else 0
                stats['pass_pct'] = round(stats['pass_completed'] / stats['pass_attempts'] * 100, 1) if stats['pass_attempts'] > 0 else 0
                stats['shooting_pct'] = round(stats['goals'] / stats['shots'] * 100, 1) if stats['shots'] > 0 else 0
                
                # Generate team_game_key
                venue_code = 1 if venue == 'Home' else 2
                stats['team_game_key'] = f"TG{int(game_id):05d}{venue_code:05d}"
                
                team_rows.append(stats)
        
        if team_rows:
            df = pd.DataFrame(team_rows)
            # Reorder columns - keys first
            key_cols = ['team_game_key', 'game_id', 'venue']
            other_cols = [c for c in df.columns if c not in key_cols]
            df = df[key_cols + other_cols]
            self._save_table('fact_team_game_stats', df)
    
    def _build_fact_event_chains(self, games):
        """Build event chains for xG model input.
        Tracks zone_entry → shot → goal sequences with timing.
        """
        logger.info("Building fact_event_chains...")
        
        events_file = self.output_dir / "fact_events.csv"
        if not events_file.exists():
            logger.error("fact_events.csv not found")
            return
        
        events = pd.read_csv(events_file, dtype=str)
        chain_rows = []
        
        # Handle column name variations
        type_col = 'Type' if 'Type' in events.columns else 'event_type'
        detail_col = 'event_detail' if 'event_detail' in events.columns else 'event_detail_'
        
        for game_id in games:
            game_events = events[events['game_id'] == str(game_id)].copy()
            if game_events.empty:
                continue
            
            game_events['event_index'] = pd.to_numeric(game_events['event_index'], errors='coerce')
            game_events = game_events.sort_values('event_index')
            
            # Find zone entries
            zone_entries = game_events[game_events[detail_col].str.contains('Entry', na=False)]
            
            for _, entry in zone_entries.iterrows():
                entry_idx = entry['event_index']
                if pd.isna(entry_idx):
                    continue
                    
                # Look for shots within 10 events
                window = game_events[(game_events['event_index'] > entry_idx) & 
                                     (game_events['event_index'] <= entry_idx + 10)]
                
                shots = window[window[type_col].isin(['Shot', 'Goal'])]
                if shots.empty:
                    continue
                
                first_shot = shots.iloc[0]
                is_goal = first_shot[type_col] == 'Goal' or 'Goal' in str(first_shot.get(detail_col, ''))
                
                chain = {
                    'chain_id': f"CH{game_id}{int(entry_idx):05d}",
                    'game_id': game_id,
                    'entry_event_index': int(entry_idx),
                    'shot_event_index': int(first_shot['event_index']),
                    'events_to_shot': int(first_shot['event_index'] - entry_idx),
                    'entry_type': entry.get('event_detail_2', entry.get(detail_col, '')),
                    'shot_result': 'Goal' if is_goal else first_shot.get(detail_col, 'Shot'),
                    'is_goal': is_goal,
                    'zone': entry.get('event_team_zone', ''),
                    'sequence_id': entry.get('sequence_id', entry.get('sequence_index', '')),
                }
                chain_rows.append(chain)
        
        if chain_rows:
            df = pd.DataFrame(chain_rows)
            self._save_table('fact_event_chains', df)
    
    def _build_fact_team_zone_time(self, games):
        """Build zone time per team per game - zones are relative to each team's perspective."""
        logger.info("Building fact_team_zone_time...")
        
        events_file = self.output_dir / "fact_events_player.csv"
        if not events_file.exists():
            events_file = self.output_dir / "fact_events.csv"
        if not events_file.exists():
            logger.error("Events file not found")
            return
        
        events = pd.read_csv(events_file, dtype=str, low_memory=False)
        zone_rows = []
        
        for game_id in games:
            game_events = events[events['game_id'] == str(game_id)].copy()
            if game_events.empty:
                continue
            
            # Normalize zone columns to lowercase
            for col in ['home_team_zone', 'away_team_zone', 'event_team_zone']:
                if col in game_events.columns:
                    game_events[col] = game_events[col].str.lower()
            
            # HOME team zone calculation
            if 'home_team_zone' in game_events.columns:
                home_o = len(game_events[game_events['home_team_zone'] == 'o'])
                home_d = len(game_events[game_events['home_team_zone'] == 'd'])
                home_n = len(game_events[game_events['home_team_zone'] == 'n'])
            else:
                # Derive from event_team_zone and team_venue
                home_events = game_events[game_events['team_venue'].str.lower() == 'home']
                away_events = game_events[game_events['team_venue'].str.lower() == 'away']
                
                # For home: home events in O are O, away events in O are D (flipped)
                home_o = len(home_events[home_events['event_team_zone'] == 'o']) + len(away_events[away_events['event_team_zone'] == 'd'])
                home_d = len(home_events[home_events['event_team_zone'] == 'd']) + len(away_events[away_events['event_team_zone'] == 'o'])
                home_n = len(home_events[home_events['event_team_zone'] == 'n']) + len(away_events[away_events['event_team_zone'] == 'n'])
            
            home_total = home_o + home_d + home_n
            
            # AWAY team zone calculation  
            if 'away_team_zone' in game_events.columns:
                away_o = len(game_events[game_events['away_team_zone'] == 'o'])
                away_d = len(game_events[game_events['away_team_zone'] == 'd'])
                away_n = len(game_events[game_events['away_team_zone'] == 'n'])
            else:
                # Derive - flipped from home
                away_o = home_d
                away_d = home_o
                away_n = home_n
            
            away_total = away_o + away_d + away_n
            
            # Home record
            zone_rows.append({
                'zone_time_key': f"Z{int(game_id):05d}000001",
                'game_id': game_id,
                'venue': 'home',
                'ozone_events': home_o,
                'dzone_events': home_d,
                'nzone_events': home_n,
                'total_events': home_total,
                'ozone_pct': round(home_o / home_total * 100, 1) if home_total > 0 else 0,
                'dzone_pct': round(home_d / home_total * 100, 1) if home_total > 0 else 0,
                'nzone_pct': round(home_n / home_total * 100, 1) if home_total > 0 else 0,
            })
            
            # Away record
            zone_rows.append({
                'zone_time_key': f"Z{int(game_id):05d}000002",
                'game_id': game_id,
                'venue': 'away',
                'ozone_events': away_o,
                'dzone_events': away_d,
                'nzone_events': away_n,
                'total_events': away_total,
                'ozone_pct': round(away_o / away_total * 100, 1) if away_total > 0 else 0,
                'dzone_pct': round(away_d / away_total * 100, 1) if away_total > 0 else 0,
                'nzone_pct': round(away_n / away_total * 100, 1) if away_total > 0 else 0,
            })
        
        if zone_rows:
            df = pd.DataFrame(zone_rows)
            self._save_table('fact_team_zone_time', df)
    
    def _build_fact_h2h(self, games):
        """Build head-to-head player matchup stats."""
        logger.info("Building fact_h2h...")
        
        shifts_file = self.output_dir / "fact_shifts_player.csv"
        events_file = self.output_dir / "fact_events_player.csv"
        
        if not shifts_file.exists() or not events_file.exists():
            logger.error("Required files not found")
            return
        
        shifts = pd.read_csv(shifts_file)
        events = pd.read_csv(events_file, dtype=str)
        
        h2h_rows = []
        
        for game_id in games:
            game_shifts = shifts[shifts['game_id'] == int(game_id)]
            game_events = events[events['game_id'] == str(game_id)]
            
            if game_shifts.empty:
                continue
            
            # Get unique shift indexes
            shift_indexes = game_shifts['shift_index'].unique()
            
            for shift_idx in shift_indexes:
                shift_players = game_shifts[game_shifts['shift_index'] == shift_idx]
                home_players = shift_players[shift_players['venue'] == 'home']['player_id'].tolist()
                away_players = shift_players[shift_players['venue'] == 'away']['player_id'].tolist()
                
                # Create H2H matchups
                for hp in home_players:
                    for ap in away_players:
                        if pd.isna(hp) or pd.isna(ap):
                            continue
                        h2h_rows.append({
                            'game_id': game_id,
                            'shift_index': shift_idx,
                            'player_1_id': hp,
                            'player_1_venue': 'home',
                            'player_2_id': ap,
                            'player_2_venue': 'away',
                        })
        
        if h2h_rows:
            df = pd.DataFrame(h2h_rows)
            # Aggregate by player pair
            h2h_agg = df.groupby(['game_id', 'player_1_id', 'player_2_id']).agg({
                'shift_index': 'count'
            }).reset_index()
            h2h_agg.columns = ['game_id', 'player_1_id', 'player_2_id', 'shifts_together']
            self._save_table('fact_h2h', h2h_agg)
    
    def _build_fact_wowy(self, games):
        """Build with/without you analysis."""
        logger.info("Building fact_wowy...")
        
        shifts_file = self.output_dir / "fact_shifts_player.csv"
        player_stats_file = self.output_dir / "fact_player_game_stats.csv"
        
        if not shifts_file.exists() or not player_stats_file.exists():
            logger.error("Required files not found")
            return
        
        shifts = pd.read_csv(shifts_file)
        player_stats = pd.read_csv(player_stats_file)
        
        wowy_rows = []
        
        for game_id in games:
            game_shifts = shifts[shifts['game_id'] == int(game_id)]
            game_stats = player_stats[player_stats['game_id'].astype(str) == str(game_id)]
            
            if game_shifts.empty or game_stats.empty:
                continue
            
            # Get all player pairs from same team
            home_players = game_shifts[game_shifts['venue'] == 'home']['player_id'].unique()
            away_players = game_shifts[game_shifts['venue'] == 'away']['player_id'].unique()
            
            for venue, players in [('home', home_players), ('away', away_players)]:
                players = [p for p in players if pd.notna(p)]
                for i, p1 in enumerate(players):
                    for p2 in players[i+1:]:
                        # Count shifts together
                        p1_shifts = set(game_shifts[game_shifts['player_id'] == p1]['shift_index'])
                        p2_shifts = set(game_shifts[game_shifts['player_id'] == p2]['shift_index'])
                        together = len(p1_shifts & p2_shifts)
                        p1_without = len(p1_shifts - p2_shifts)
                        p2_without = len(p2_shifts - p1_shifts)
                        
                        wowy_rows.append({
                            'game_id': game_id,
                            'player_1_id': p1,
                            'player_2_id': p2,
                            'venue': venue,
                            'shifts_together': together,
                            'p1_shifts_without_p2': p1_without,
                            'p2_shifts_without_p1': p2_without,
                            'total_p1_shifts': len(p1_shifts),
                            'total_p2_shifts': len(p2_shifts),
                        })
        
        if wowy_rows:
            df = pd.DataFrame(wowy_rows)
            self._save_table('fact_wowy', df)
    
    def _build_fact_line_combos(self, games):
        """Build line combination analysis."""
        logger.info("Building fact_line_combos...")
        
        shifts_file = self.output_dir / "fact_shifts_player.csv"
        
        if not shifts_file.exists():
            logger.error("fact_shifts_player.csv not found")
            return
        
        shifts = pd.read_csv(shifts_file)
        combo_rows = []
        
        for game_id in games:
            game_shifts = shifts[shifts['game_id'] == int(game_id)]
            
            if game_shifts.empty:
                continue
            
            # Group by shift_index to find line combinations
            for shift_idx in game_shifts['shift_index'].unique():
                shift_players = game_shifts[game_shifts['shift_index'] == shift_idx]
                
                for venue in ['home', 'away']:
                    venue_players = shift_players[shift_players['venue'] == venue]
                    
                    forwards = venue_players[venue_players['slot'].str.contains('forward', na=False)]['player_id'].tolist()
                    defense = venue_players[venue_players['slot'].str.contains('defense', na=False)]['player_id'].tolist()
                    
                    if len(forwards) >= 2:
                        # Create forward combo key (sorted for consistency)
                        fwd_key = '_'.join(sorted([str(f) for f in forwards if pd.notna(f)]))
                        def_key = '_'.join(sorted([str(d) for d in defense if pd.notna(d)]))
                        
                        combo_rows.append({
                            'game_id': game_id,
                            'shift_index': shift_idx,
                            'venue': venue,
                            'forward_combo': fwd_key,
                            'defense_combo': def_key,
                            'num_forwards': len([f for f in forwards if pd.notna(f)]),
                            'num_defense': len([d for d in defense if pd.notna(d)]),
                        })
        
        if combo_rows:
            df = pd.DataFrame(combo_rows)
            # Aggregate by combo
            combo_agg = df.groupby(['game_id', 'venue', 'forward_combo', 'defense_combo']).agg({
                'shift_index': 'count'
            }).reset_index()
            combo_agg.columns = ['game_id', 'venue', 'forward_combo', 'defense_combo', 'shifts']
            combo_agg = combo_agg.sort_values(['game_id', 'venue', 'shifts'], ascending=[True, True, False])
            self._save_table('fact_line_combos', combo_agg)
    
    def _add_rush_cycle_flags(self, games):
        """Add rush and cycle detection flags to events.
        
        RUSH: Zone entry followed by shot within 5 events (same team)
        - Types: breakaway, odd_man_2v1, odd_man_3v2, even_2v2, even_3v3
        
        CYCLE: 3+ consecutive o-zone passes without zone exit
        """
        logger.info("Building fact_rush_cycle_flags...")
        
        events_file = self.output_dir / "fact_events.csv"
        shifts_file = self.output_dir / "fact_shifts_player.csv"
        
        if not events_file.exists():
            logger.error("fact_events.csv not found")
            return
        
        events = pd.read_csv(events_file, dtype=str)
        shifts = pd.read_csv(shifts_file) if shifts_file.exists() else None
        
        # Handle column name variations
        type_col = 'Type' if 'Type' in events.columns else 'event_type'
        detail_col = 'event_detail' if 'event_detail' in events.columns else 'event_detail_'
        
        rush_rows = []
        cycle_rows = []
        
        for game_id in games:
            game_events = events[events['game_id'] == str(game_id)].copy()
            if game_events.empty:
                continue
            
            game_events['event_index'] = pd.to_numeric(game_events['event_index'], errors='coerce')
            game_events = game_events.sort_values('event_index').reset_index(drop=True)
            
            game_shifts = shifts[shifts['game_id'] == int(game_id)] if shifts is not None else None
            
            # ===============================
            # RUSH DETECTION
            # ===============================
            zone_entries = game_events[game_events[detail_col].str.contains('Entry', na=False)]
            
            for idx, entry in zone_entries.iterrows():
                entry_idx = entry['event_index']
                entry_venue = entry.get('team_venue', entry.get('team_venue_', ''))
                
                if pd.isna(entry_idx):
                    continue
                
                # Look for shots within 5 events by SAME team
                window = game_events[(game_events['event_index'] > entry_idx) & 
                                     (game_events['event_index'] <= entry_idx + 5)]
                
                # Filter to same team's shots
                team_shots = window[(window[type_col].isin(['Shot', 'Goal'])) & 
                                    (window.get('team_venue', window.get('team_venue_', '')) == entry_venue)]
                
                if team_shots.empty:
                    continue
                
                first_shot = team_shots.iloc[0]
                events_to_shot = int(first_shot['event_index'] - entry_idx)
                
                # Determine rush type based on skater counts
                rush_type = 'rush'  # Default
                
                if game_shifts is not None and 'shift_index' in entry.index:
                    try:
                        shift_idx = int(entry.get('shift_index', 0))
                        shift_players = game_shifts[game_shifts['shift_index'] == shift_idx]
                        
                        if not shift_players.empty:
                            # Count skaters (non-goalies) per team
                            home_skaters = len(shift_players[(shift_players['venue'] == 'home') & 
                                                             (~shift_players['slot'].str.contains('goalie', na=False))])
                            away_skaters = len(shift_players[(shift_players['venue'] == 'away') & 
                                                             (~shift_players['slot'].str.contains('goalie', na=False))])
                            
                            attacking_venue = entry_venue.lower() if entry_venue else 'home'
                            if attacking_venue == 'home':
                                att_skaters, def_skaters = home_skaters, away_skaters
                            else:
                                att_skaters, def_skaters = away_skaters, home_skaters
                            
                            # Classify rush type
                            if att_skaters == 1 and def_skaters == 0:
                                rush_type = 'breakaway'
                            elif att_skaters == 2 and def_skaters == 1:
                                rush_type = 'odd_man_2v1'
                            elif att_skaters == 3 and def_skaters == 2:
                                rush_type = 'odd_man_3v2'
                            elif att_skaters == 2 and def_skaters == 2:
                                rush_type = 'even_2v2'
                            elif att_skaters == 3 and def_skaters == 3:
                                rush_type = 'even_3v3'
                            elif att_skaters > def_skaters:
                                rush_type = f'odd_man_{att_skaters}v{def_skaters}'
                            else:
                                rush_type = f'even_{att_skaters}v{def_skaters}'
                    except (KeyError, TypeError, ValueError) as e:
                        pass  # Use default rush_type if determination fails
                
                is_goal = first_shot[type_col] == 'Goal' or 'Goal' in str(first_shot.get(detail_col, ''))
                
                rush_rows.append({
                    'game_id': game_id,
                    'entry_event_index': int(entry_idx),
                    'shot_event_index': int(first_shot['event_index']),
                    'events_to_shot': events_to_shot,
                    'is_rush': True,
                    'rush_type': rush_type,
                    'is_goal': is_goal,
                    'entry_type': entry.get('event_detail_2', entry.get(detail_col, '')),
                })
            
            # ===============================
            # CYCLE DETECTION
            # ===============================
            # Find sequences of 3+ consecutive o-zone passes
            game_events_list = game_events.to_dict('records')
            i = 0
            
            while i < len(game_events_list) - 2:
                event = game_events_list[i]
                
                # Check if this is an o-zone pass
                is_ozone = event.get('event_team_zone', event.get('home_team_zone', '')) == 'o'
                is_pass = event.get(type_col, '') == 'Pass'
                
                if is_ozone and is_pass:
                    # Count consecutive o-zone passes
                    pass_count = 1
                    j = i + 1
                    cycle_start_idx = event.get('event_index')
                    
                    while j < len(game_events_list):
                        next_event = game_events_list[j]
                        next_is_ozone = next_event.get('event_team_zone', next_event.get('home_team_zone', '')) == 'o'
                        next_is_pass = next_event.get(type_col, '') == 'Pass'
                        next_is_exit = 'Exit' in str(next_event.get(detail_col, ''))
                        
                        if next_is_exit:
                            break  # Zone exit ends potential cycle
                        
                        if next_is_ozone and next_is_pass:
                            pass_count += 1
                            j += 1
                        elif next_event.get(type_col, '') in ['Shot', 'Goal', 'Turnover', 'Stoppage']:
                            break  # These events end the cycle
                        else:
                            j += 1  # Skip non-pass events but continue looking
                            if j - i > 10:  # Max window
                                break
                    
                    if pass_count >= 3:
                        cycle_rows.append({
                            'game_id': game_id,
                            'cycle_start_event_index': int(cycle_start_idx) if pd.notna(cycle_start_idx) else i,
                            'cycle_end_event_index': int(game_events_list[j-1].get('event_index', j-1)),
                            'pass_count': pass_count,
                            'is_cycle': True,
                        })
                        i = j  # Skip to end of cycle
                    else:
                        i += 1
                else:
                    i += 1
        
        # Save rush flags
        if rush_rows:
            rush_df = pd.DataFrame(rush_rows)
            self._save_table('fact_rush_events', rush_df)
        else:
            logger.info("  No rush events detected")
        
        # Save cycle flags  
        if cycle_rows:
            cycle_df = pd.DataFrame(cycle_rows)
            self._save_table('fact_cycle_events', cycle_df)
        else:
            logger.info("  No cycle events detected")
        
        # Summary
        logger.info(f"  ✓ fact_rush_cycle_flags: {len(rush_rows)} rushes, {len(cycle_rows)} cycles")
    
    def _save_table(self, table_name, df):
        """Save table to CSV."""
        output_path = self.output_dir / f"{table_name}.csv"
        
        if self.mode == 'append' and output_path.exists():
            existing = pd.read_csv(output_path)
            df = pd.concat([existing, df], ignore_index=True).drop_duplicates()
        
        df.to_csv(output_path, index=False)
        logger.info(f"  ✓ {table_name}: {len(df)} rows")
        self.stats['processed'] += 1
        self.stats['tables'].append(table_name)


def main():
    parser = argparse.ArgumentParser(description='BenchSight ETL Orchestrator')
    parser.add_argument('--all', action='store_true', help='Process all tables and games')
    parser.add_argument('--dims', action='store_true', help='Process only dimension tables')
    parser.add_argument('--facts', action='store_true', help='Process only fact tables')
    parser.add_argument('--tables', type=str, help='Comma-separated list of tables')
    parser.add_argument('--games', type=str, help='Comma-separated list of game IDs')
    parser.add_argument('--append', action='store_true', help='Append mode (default: overwrite)')
    parser.add_argument('--output', type=str, default=str(OUTPUT_DIR), help='Output directory')
    
    args = parser.parse_args()
    
    # Parse arguments
    tables = args.tables.split(',') if args.tables else None
    games = args.games.split(',') if args.games else None
    mode = 'append' if args.append else 'overwrite'
    
    # Run ETL
    orchestrator = ETLOrchestrator(output_dir=args.output, mode=mode)
    orchestrator.run(
        tables=tables,
        games=games,
        dims_only=args.dims,
        facts_only=args.facts
    )


if __name__ == '__main__':
    main()
