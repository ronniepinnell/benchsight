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
    'dim_player', 'dim_team', 'dim_season', 'dim_position', 'dim_venue',
    'dim_event_type', 'dim_event_detail', 'dim_event_detail_2',
    'dim_zone_entry_type', 'dim_zone_exit_type', 'dim_play_detail',
    'dim_player_role', 'dim_situation', 'dim_strength', 'dim_period'
]

FACT_TABLES = [
    'fact_events', 'fact_events_player', 'fact_shifts_player',
    'fact_gameroster', 'fact_player_game_stats', 'fact_goalie_game_stats',
    'fact_team_game_stats'
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
                elif table == 'fact_gameroster':
                    logger.info(f"Skipping {table} - sourced from NORAD website")
                else:
                    logger.warning(f"No builder for {table}")
            except Exception as e:
                logger.error(f"Error processing {table}: {e}")
                self.stats['errors'] += 1
    
    def _build_fact_events(self, games):
        """Build fact_events from tracking files."""
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
            # Deduplicate by event_index (events have multiple player rows)
            df_dedup = df.drop_duplicates(subset=['game_id', 'event_index'])
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
            
            # Normalize column names
            df = self._normalize_event_columns(df)
            
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
        for _, shift in shifts.iterrows():
            for venue, cols in player_cols.items():
                for col in cols:
                    if col in shift and pd.notna(shift[col]):
                        player_num = shift[col]
                        slot = col.replace('home_', '').replace('away_', '')
                        rows.append({
                            'game_id': int(game_id),
                            'shift_index': shift['shift_index'],
                            'player_number': int(player_num),
                            'venue': venue,
                            'slot': slot,
                            'period': shift.get('Period', shift.get('period')),
                            'shift_duration': shift.get('shift_duration'),
                            'situation': shift.get('situation'),
                            'strength': shift.get('strength'),
                            'stoppage_time': shift.get('stoppage_time', 0)
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
        """Build player game stats using VALIDATED counting rules."""
        logger.info("Building fact_player_game_stats with validated rules...")
        
        # Load events
        events_file = self.output_dir / "fact_events_player.csv"
        shifts_file = self.output_dir / "fact_shifts_player.csv"
        
        if not events_file.exists() or not shifts_file.exists():
            logger.error("Required files not found - run full ETL first")
            return
        
        events = pd.read_csv(events_file, dtype=str)
        shifts = pd.read_csv(shifts_file)
        
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
            # Fix: Match on player_id directly, not player_number (jersey)
            player_shifts = shifts[(shifts['game_id'] == int(game_id)) & (shifts['player_id'] == player_id)]
            
            stats = self._calculate_player_stats(player_events, player_shifts)
            stats['game_id'] = game_id
            stats['player_id'] = player_id
            stats['player_name'] = player_name
            stats_rows.append(stats)
        
        if stats_rows:
            df = pd.DataFrame(stats_rows)
            self._save_table('fact_player_game_stats', df)
    
    def _calculate_player_stats(self, events, shifts):
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
            stats['shift_count'] = len(shifts)
            stats['logical_shifts'] = shifts['logical_shift_number'].max() if 'logical_shift_number' in shifts.columns else stats['shift_count']
            stats['avg_shift'] = round(stats['toi_seconds'] / stats['logical_shifts'], 1) if stats['logical_shifts'] > 0 else 0
        else:
            stats['toi_seconds'] = 0
            stats['toi_minutes'] = 0
            stats['shift_count'] = 0
            stats['logical_shifts'] = 0
            stats['avg_shift'] = 0
        
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
            
            stats = {
                'game_id': game_id,
                'player_id': player_id,
                'player_name': player_name,
                'saves': len(ge[(ge['event_type'] == 'Save') & (ge['player_role'] == 'event_team_player_1')]),
                'goals_against': len(ge[(ge['event_type'] == 'Goal') & (ge['player_role'] == 'opp_team_player_1')]),
                'toi_minutes': round(gs['shift_duration'].sum() / 60, 1) if not gs.empty else 0
            }
            stats['shots_faced'] = stats['saves'] + stats['goals_against']
            stats['save_pct'] = round(stats['saves'] / stats['shots_faced'] * 100, 1) if stats['shots_faced'] > 0 else 0
            stats['gaa'] = round((stats['goals_against'] / stats['toi_minutes']) * 60, 2) if stats['toi_minutes'] > 0 else 0
            
            stats_rows.append(stats)
        
        if stats_rows:
            df = pd.DataFrame(stats_rows)
            self._save_table('fact_goalie_game_stats', df)
    
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
