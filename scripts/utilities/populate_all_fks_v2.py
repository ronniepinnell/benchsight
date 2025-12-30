#!/usr/bin/env python3
"""
Comprehensive Foreign Key Population Script v2 - BenchSight

Populates ALL missing foreign keys across ALL fact tables.
Uses dimension tables' potential_values and old_equiv columns for fuzzy matching.

Author: BenchSight ETL
Date: December 2024
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path('data/output')


# =============================================================================
# COMPLETE FK MAPPING DEFINITIONS
# =============================================================================

FK_MAPPINGS = {
    # =========================================================================
    # PERIOD
    # =========================================================================
    'period': {
        'dim_table': 'dim_period',
        'dim_pk': 'period_id',
        'match_cols': ['period_number', 'period_name'],
        'fk_col': 'period_id'
    },
    'Period': {
        'dim_table': 'dim_period',
        'dim_pk': 'period_id',
        'match_cols': ['period_number', 'period_name'],
        'fk_col': 'period_id'
    },
    
    # =========================================================================
    # VENUE
    # =========================================================================
    'venue': {
        'dim_table': 'dim_venue',
        'dim_pk': 'venue_id',
        'match_cols': ['venue_code', 'venue_name', 'venue_abbrev'],
        'fk_col': 'venue_id'
    },
    'team_venue': {
        'dim_table': 'dim_venue',
        'dim_pk': 'venue_id',
        'match_cols': ['venue_code', 'venue_name', 'venue_abbrev'],
        'fk_col': 'venue_id'
    },
    'player_1_venue': {
        'dim_table': 'dim_venue',
        'dim_pk': 'venue_id',
        'match_cols': ['venue_code', 'venue_name', 'venue_abbrev'],
        'fk_col': 'player_1_venue_id'
    },
    'player_2_venue': {
        'dim_table': 'dim_venue',
        'dim_pk': 'venue_id',
        'match_cols': ['venue_code', 'venue_name', 'venue_abbrev'],
        'fk_col': 'player_2_venue_id'
    },
    
    # =========================================================================
    # EVENT TYPE
    # =========================================================================
    'event_type': {
        'dim_table': 'dim_event_type',
        'dim_pk': 'event_type_id',
        'match_cols': ['event_type_code', 'event_type_name'],
        'fk_col': 'event_type_id'
    },
    'Type': {
        'dim_table': 'dim_event_type',
        'dim_pk': 'event_type_id',
        'match_cols': ['event_type_code', 'event_type_name'],
        'fk_col': 'event_type_id'
    },
    'event_1_type': {
        'dim_table': 'dim_event_type',
        'dim_pk': 'event_type_id',
        'match_cols': ['event_type_code', 'event_type_name'],
        'fk_col': 'event_1_type_id'
    },
    'event_2_type': {
        'dim_table': 'dim_event_type',
        'dim_pk': 'event_type_id',
        'match_cols': ['event_type_code', 'event_type_name'],
        'fk_col': 'event_2_type_id'
    },
    'event_3_type': {
        'dim_table': 'dim_event_type',
        'dim_pk': 'event_type_id',
        'match_cols': ['event_type_code', 'event_type_name'],
        'fk_col': 'event_3_type_id'
    },
    'event_4_type': {
        'dim_table': 'dim_event_type',
        'dim_pk': 'event_type_id',
        'match_cols': ['event_type_code', 'event_type_name'],
        'fk_col': 'event_4_type_id'
    },
    'event_5_type': {
        'dim_table': 'dim_event_type',
        'dim_pk': 'event_type_id',
        'match_cols': ['event_type_code', 'event_type_name'],
        'fk_col': 'event_5_type_id'
    },
    
    # =========================================================================
    # EVENT DETAIL
    # =========================================================================
    'event_detail': {
        'dim_table': 'dim_event_detail',
        'dim_pk': 'event_detail_id',
        'match_cols': ['event_detail_code', 'event_detail_name'],
        'fk_col': 'event_detail_id'
    },
    'event_1_detail': {
        'dim_table': 'dim_event_detail',
        'dim_pk': 'event_detail_id',
        'match_cols': ['event_detail_code', 'event_detail_name'],
        'fk_col': 'event_1_detail_id'
    },
    'event_2_detail': {
        'dim_table': 'dim_event_detail',
        'dim_pk': 'event_detail_id',
        'match_cols': ['event_detail_code', 'event_detail_name'],
        'fk_col': 'event_2_detail_id'
    },
    'event_3_detail': {
        'dim_table': 'dim_event_detail',
        'dim_pk': 'event_detail_id',
        'match_cols': ['event_detail_code', 'event_detail_name'],
        'fk_col': 'event_3_detail_id'
    },
    'event_4_detail': {
        'dim_table': 'dim_event_detail',
        'dim_pk': 'event_detail_id',
        'match_cols': ['event_detail_code', 'event_detail_name'],
        'fk_col': 'event_4_detail_id'
    },
    'event_5_detail': {
        'dim_table': 'dim_event_detail',
        'dim_pk': 'event_detail_id',
        'match_cols': ['event_detail_code', 'event_detail_name'],
        'fk_col': 'event_5_detail_id'
    },
    
    # =========================================================================
    # EVENT DETAIL 2
    # =========================================================================
    'event_detail_2': {
        'dim_table': 'dim_event_detail_2',
        'dim_pk': 'event_detail_2_id',
        'match_cols': ['event_detail_2_code', 'event_detail_2_name'],
        'fk_col': 'event_detail_2_id'
    },
    
    # =========================================================================
    # SUCCESS
    # =========================================================================
    'event_successful': {
        'dim_table': 'dim_success',
        'dim_pk': 'success_id',
        'match_cols': ['success_code', 'success_name', 'potential_values'],
        'fk_col': 'success_id'
    },
    'play_detail_successful': {
        'dim_table': 'dim_success',
        'dim_pk': 'success_id',
        'match_cols': ['success_code', 'success_name', 'potential_values'],
        'fk_col': 'play_detail_success_id'
    },
    
    # =========================================================================
    # ZONE
    # =========================================================================
    'zone': {
        'dim_table': 'dim_zone',
        'dim_pk': 'zone_id',
        'match_cols': ['zone_code', 'zone_name', 'zone_abbrev'],
        'fk_col': 'zone_id'
    },
    'event_team_zone': {
        'dim_table': 'dim_zone',
        'dim_pk': 'zone_id',
        'match_cols': ['zone_code', 'zone_name', 'zone_abbrev'],
        'fk_col': 'zone_id'
    },
    'start_zone': {
        'dim_table': 'dim_zone',
        'dim_pk': 'zone_id',
        'match_cols': ['zone_code', 'zone_name', 'zone_abbrev'],
        'fk_col': 'start_zone_id'
    },
    'end_zone': {
        'dim_table': 'dim_zone',
        'dim_pk': 'zone_id',
        'match_cols': ['zone_code', 'zone_name', 'zone_abbrev'],
        'fk_col': 'end_zone_id'
    },
    
    # =========================================================================
    # PLAY DETAIL
    # =========================================================================
    'play_detail': {
        'dim_table': 'dim_play_detail',
        'dim_pk': 'play_detail_id',
        'match_cols': ['play_detail_code', 'play_detail_name'],
        'fk_col': 'play_detail_id'
    },
    'play_detail1': {
        'dim_table': 'dim_play_detail',
        'dim_pk': 'play_detail_id',
        'match_cols': ['play_detail_code', 'play_detail_name'],
        'fk_col': 'play_detail_id'
    },
    'play_detail_2': {
        'dim_table': 'dim_play_detail_2',
        'dim_pk': 'play_detail_2_id',
        'match_cols': ['play_detail_2_code', 'play_detail_2_name'],
        'fk_col': 'play_detail_2_id'
    },
    
    # =========================================================================
    # PLAYER ROLE
    # =========================================================================
    'player_role': {
        'dim_table': 'dim_player_role',
        'dim_pk': 'role_id',
        'match_cols': ['role_code', 'role_name', 'potential_values'],
        'fk_col': 'role_id'
    },
    
    # =========================================================================
    # STRENGTH / SITUATION
    # =========================================================================
    'strength': {
        'dim_table': 'dim_strength',
        'dim_pk': 'strength_id',
        'match_cols': ['strength_code', 'strength_name'],
        'fk_col': 'strength_id'
    },
    'situation': {
        'dim_table': 'dim_situation',
        'dim_pk': 'situation_id',
        'match_cols': ['situation_code', 'situation_name'],
        'fk_col': 'situation_id'
    },
    
    # =========================================================================
    # SHIFT START/STOP TYPE
    # =========================================================================
    'shift_start_type': {
        'dim_table': 'dim_shift_start_type',
        'dim_pk': 'shift_start_type_id',
        'match_cols': ['shift_start_type_code', 'shift_start_type_name', 'old_equiv'],
        'fk_col': 'shift_start_type_id'
    },
    'shift_stop_type': {
        'dim_table': 'dim_shift_stop_type',
        'dim_pk': 'shift_stop_type_id',
        'match_cols': ['shift_stop_type_code', 'shift_stop_type_name', 'old_equiv'],
        'fk_col': 'shift_stop_type_id'
    },
    
    # =========================================================================
    # SLOT
    # =========================================================================
    'slot': {
        'dim_table': 'dim_shift_slot',
        'dim_pk': 'slot_id',
        'match_cols': ['slot_code', 'slot_name'],
        'fk_col': 'slot_id'
    },
    
    # =========================================================================
    # POSITION
    # =========================================================================
    'player_position': {
        'dim_table': 'dim_position',
        'dim_pk': 'position_id',
        'match_cols': ['position_code', 'position_name'],
        'fk_col': 'position_id'
    },
    'position': {
        'dim_table': 'dim_position',
        'dim_pk': 'position_id',
        'match_cols': ['position_code', 'position_name'],
        'fk_col': 'position_id'
    },
    'Position': {
        'dim_table': 'dim_position',
        'dim_pk': 'position_id',
        'match_cols': ['position_code', 'position_name'],
        'fk_col': 'position_id'
    },
    
    # =========================================================================
    # ZONE ENTRY/EXIT TYPE
    # =========================================================================
    'entry_type': {
        'dim_table': 'dim_zone_entry_type',
        'dim_pk': 'zone_entry_type_id',
        'match_cols': ['zone_entry_type_code', 'zone_entry_type_name'],
        'fk_col': 'zone_entry_type_id'
    },
    
    # =========================================================================
    # SHOT TYPE
    # =========================================================================
    'shot_type': {
        'dim_table': 'dim_shot_type',
        'dim_pk': 'shot_type_id',
        'match_cols': ['shot_type_code', 'shot_type_name'],
        'fk_col': 'shot_type_id'
    },
    'shot_result': {
        'dim_table': 'dim_shot_type',
        'dim_pk': 'shot_type_id',
        'match_cols': ['shot_type_code', 'shot_type_name'],
        'fk_col': 'shot_result_type_id'
    },
    
    # =========================================================================
    # RUSH TYPE
    # =========================================================================
    'rush_type': {
        'dim_table': 'dim_zone_entry_type',
        'dim_pk': 'zone_entry_type_id',
        'match_cols': ['zone_entry_type_code', 'zone_entry_type_name'],
        'fk_col': 'rush_type_id'
    },
    
    # =========================================================================
    # TEAM
    # =========================================================================
    'team': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team', 'long_team_name'],
        'fk_col': 'team_id'
    },
    'team_name': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team', 'long_team_name'],
        'fk_col': 'team_id'
    },
    'home_team': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team', 'long_team_name'],
        'fk_col': 'home_team_id'
    },
    'away_team': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team', 'long_team_name'],
        'fk_col': 'away_team_id'
    },
    'start_team': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team', 'long_team_name'],
        'fk_col': 'start_team_id'
    },
    'end_team': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team', 'long_team_name'],
        'fk_col': 'end_team_id'
    },
    'opp_team_name': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team', 'long_team_name'],
        'fk_col': 'opp_team_id'
    },
    'Team': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team', 'long_team_name'],
        'fk_col': 'team_id'
    },
    'Opp': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team', 'long_team_name'],
        'fk_col': 'opp_team_id'
    },
    'player_team': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team', 'long_team_name'],
        'fk_col': 'player_team_id'
    },
    'drafted_team_name': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team', 'long_team_name'],
        'fk_col': 'drafted_team_id'
    },
    
    # =========================================================================
    # SEASON
    # =========================================================================
    'season': {
        'dim_table': 'dim_season',
        'dim_pk': 'season_id',
        'match_cols': ['season'],
        'fk_col': 'season_id'
    },
    'Season': {
        'dim_table': 'dim_season',
        'dim_pk': 'season_id',
        'match_cols': ['season'],
        'fk_col': 'season_id'
    },
    
    # =========================================================================
    # NET LOCATION
    # =========================================================================
    'net_location': {
        'dim_table': 'dim_net_location',
        'dim_pk': 'net_location_id',
        'match_cols': ['net_location_code', 'net_location_name'],
        'fk_col': 'net_location_id'
    },
    
    # =========================================================================
    # STOPPAGE TYPE
    # =========================================================================
    'stoppage': {
        'dim_table': 'dim_stoppage_type',
        'dim_pk': 'stoppage_type_id',
        'match_cols': ['stoppage_type_code', 'stoppage_type_name'],
        'fk_col': 'stoppage_type_id'
    },
    
    # =========================================================================
    # TURNOVER TYPE
    # =========================================================================
    'turnover_type': {
        'dim_table': 'dim_turnover_type',
        'dim_pk': 'turnover_type_id',
        'match_cols': ['turnover_type_code', 'turnover_type_name'],
        'fk_col': 'turnover_type_id'
    },
    
    # =========================================================================
    # GIVEAWAY TYPE
    # =========================================================================
    'giveaway_type': {
        'dim_table': 'dim_giveaway_type',
        'dim_pk': 'giveaway_type_id',
        'match_cols': ['giveaway_type_code', 'giveaway_type_name'],
        'fk_col': 'giveaway_type_id'
    },
    
    # =========================================================================
    # TAKEAWAY TYPE
    # =========================================================================
    'takeaway_type': {
        'dim_table': 'dim_takeaway_type',
        'dim_pk': 'takeaway_type_id',
        'match_cols': ['takeaway_type_code', 'takeaway_type_name'],
        'fk_col': 'takeaway_type_id'
    },
    
    # =========================================================================
    # PASS TYPE
    # =========================================================================
    'pass_type': {
        'dim_table': 'dim_pass_type',
        'dim_pk': 'pass_type_id',
        'match_cols': ['pass_type_code', 'pass_type_name'],
        'fk_col': 'pass_type_id'
    },
    
    # =========================================================================
    # LEAGUE
    # =========================================================================
    'league': {
        'dim_table': 'dim_league',
        'dim_pk': 'league_id',
        'match_cols': ['league'],
        'fk_col': 'league_id'
    },
}


class ComprehensiveFKPopulator:
    """Populates foreign keys across all tables with fuzzy matching."""
    
    def __init__(self):
        self.dim_cache = {}
        self.match_cache = {}
        self.stats = {'populated': 0, 'tables_processed': 0, 'new_fks': 0}
        self.unmapped_values = {}
        
    def load_dimension(self, dim_name: str) -> pd.DataFrame:
        """Load and cache a dimension table."""
        if dim_name not in self.dim_cache:
            path = OUTPUT_DIR / f'{dim_name}.csv'
            if path.exists():
                self.dim_cache[dim_name] = pd.read_csv(path)
            else:
                logger.warning(f"Dimension table not found: {dim_name}")
                self.dim_cache[dim_name] = pd.DataFrame()
        return self.dim_cache[dim_name]
    
    def build_match_dict(self, dim_name: str, pk_col: str, match_cols: List[str]) -> Dict[str, str]:
        """Build a dictionary mapping various values to the FK with comprehensive fuzzy matching."""
        cache_key = f"{dim_name}_{pk_col}"
        if cache_key in self.match_cache:
            return self.match_cache[cache_key]
        
        dim = self.load_dimension(dim_name)
        if dim.empty:
            return {}
        
        match_dict = {}
        
        for _, row in dim.iterrows():
            pk_value = row[pk_col]
            
            for col in match_cols:
                if col not in dim.columns or pd.isna(row[col]):
                    continue
                    
                val = str(row[col]).strip()
                
                # Handle comma-separated values (potential_values, old_equiv)
                if col in ['potential_values', 'old_equiv']:
                    for v in val.split(','):
                        v = v.strip()
                        if v:
                            self._add_variations(match_dict, v, pk_value)
                else:
                    self._add_variations(match_dict, val, pk_value)
        
        self.match_cache[cache_key] = match_dict
        return match_dict
    
    def _add_variations(self, match_dict: Dict, value: str, pk_value: str):
        """Add all variations of a value to the match dictionary."""
        variations = [
            value,
            value.lower(),
            value.upper(),
            value.replace(' ', '_'),
            value.replace(' ', '_').lower(),
            value.replace('_', ' '),
            value.replace('_', ' ').lower(),
            value.replace(' ', ''),
            value.replace(' ', '').lower(),
            value.replace('-', '_'),
            value.replace('-', ' '),
            value.replace(':', ''),
            value.replace(': ', '_'),
        ]
        
        for v in variations:
            if v and v not in match_dict:
                match_dict[v] = pk_value
    
    def lookup_fk(self, value: any, mapping: Dict, track_unmapped: bool = True) -> Optional[str]:
        """Look up a foreign key value using fuzzy matching."""
        if pd.isna(value):
            return None
        
        val_str = str(value).strip()
        if not val_str:
            return None
            
        dim_name = mapping['dim_table']
        pk_col = mapping['dim_pk']
        match_cols = mapping['match_cols']
        
        match_dict = self.build_match_dict(dim_name, pk_col, match_cols)
        
        if not match_dict:
            return None
        
        # Try various transformations
        attempts = [
            val_str,
            val_str.lower(),
            val_str.upper(),
            val_str.replace(' ', '_'),
            val_str.replace(' ', '_').lower(),
            val_str.replace('_', ' '),
            val_str.replace('_', ' ').lower(),
            val_str.replace(' ', ''),
            val_str.replace(' ', '').lower(),
        ]
        
        for attempt in attempts:
            if attempt in match_dict:
                return match_dict[attempt]
        
        # Special handling for periods (numeric)
        if mapping['dim_table'] == 'dim_period':
            try:
                period_num = int(float(val_str))
                for attempt in [str(period_num), f'P{period_num}', f'Period {period_num}']:
                    if attempt in match_dict or attempt.lower() in match_dict:
                        return match_dict.get(attempt) or match_dict.get(attempt.lower())
            except (ValueError, TypeError):
                pass
        
        # Track unmapped values for debugging
        if track_unmapped and val_str:
            key = f"{dim_name}:{mapping['fk_col']}"
            if key not in self.unmapped_values:
                self.unmapped_values[key] = set()
            self.unmapped_values[key].add(val_str)
        
        return None
    
    def populate_fks_for_table(self, table_name: str):
        """Populate all possible FKs for a single table."""
        path = OUTPUT_DIR / f'{table_name}.csv'
        if not path.exists():
            return
        
        logger.info(f"\nProcessing {table_name}...")
        df = pd.read_csv(path, low_memory=False)
        original_cols = set(df.columns)
        changes = []
        
        for source_col, mapping in FK_MAPPINGS.items():
            if source_col not in df.columns:
                continue
            
            fk_col = mapping['fk_col']
            
            # Check if FK column exists
            if fk_col in df.columns:
                # Fill null values only
                null_mask = df[fk_col].isna()
                null_count = null_mask.sum()
                
                if null_count > 0:
                    df.loc[null_mask, fk_col] = df.loc[null_mask, source_col].apply(
                        lambda x: self.lookup_fk(x, mapping)
                    )
                    new_fill = df[fk_col].notna().sum()
                    if new_fill > (len(df) - null_count):
                        filled = new_fill - (len(df) - null_count)
                        changes.append(f"  {fk_col}: +{filled} filled")
                        self.stats['populated'] += filled
            else:
                # Create new FK column
                df[fk_col] = df[source_col].apply(lambda x: self.lookup_fk(x, mapping))
                fill_rate = df[fk_col].notna().sum()
                total = len(df)
                pct = fill_rate / total * 100 if total > 0 else 0
                
                if fill_rate > 0:
                    changes.append(f"  + {fk_col}: {fill_rate}/{total} ({pct:.1f}%)")
                    self.stats['populated'] += fill_rate
                    self.stats['new_fks'] += 1
        
        # Save if changes were made
        if changes or set(df.columns) != original_cols:
            df.to_csv(path, index=False)
            for change in changes:
                logger.info(change)
        else:
            logger.info("  No changes needed")
        
        self.stats['tables_processed'] += 1
    
    def populate_all(self):
        """Populate FKs for all fact tables."""
        logger.info("=" * 70)
        logger.info("COMPREHENSIVE FK POPULATION v2")
        logger.info("=" * 70)
        
        # Process all fact tables
        fact_files = sorted(OUTPUT_DIR.glob('fact_*.csv'))
        
        for fact_file in fact_files:
            table_name = fact_file.stem
            self.populate_fks_for_table(table_name)
        
        # Report unmapped values
        if self.unmapped_values:
            logger.info("\n" + "=" * 70)
            logger.info("UNMAPPED VALUES (sample)")
            logger.info("=" * 70)
            for key, values in sorted(self.unmapped_values.items()):
                sample = list(values)[:5]
                logger.info(f"  {key}: {sample}")
        
        logger.info("\n" + "=" * 70)
        logger.info("FK POPULATION COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Tables processed: {self.stats['tables_processed']}")
        logger.info(f"FKs populated: {self.stats['populated']}")
        logger.info(f"New FK columns: {self.stats['new_fks']}")


def add_team_fks_from_schedule():
    """Add team FKs using game schedule data."""
    logger.info("\n--- Adding Team FKs from Schedule ---")
    
    schedule_path = OUTPUT_DIR / 'dim_schedule.csv'
    if not schedule_path.exists():
        logger.warning("dim_schedule.csv not found")
        return
    
    schedule = pd.read_csv(schedule_path)
    
    # Build game -> team mapping
    game_home_team = {}
    game_away_team = {}
    
    for _, row in schedule.iterrows():
        game_id = row['game_id']
        if pd.notna(row.get('home_team_id')):
            game_home_team[game_id] = row['home_team_id']
        if pd.notna(row.get('away_team_id')):
            game_away_team[game_id] = row['away_team_id']
    
    # Tables that need home/away team IDs based on game_id
    fact_tables = [
        'fact_h2h', 'fact_wowy', 'fact_line_combos', 'fact_head_to_head',
        'fact_player_game_stats', 'fact_goalie_game_stats', 'fact_team_game_stats',
        'fact_player_pair_stats', 'fact_sequences', 'fact_plays', 
        'fact_event_chains', 'fact_rush_events', 'fact_cycle_events',
        'fact_player_event_chains', 'fact_linked_events', 'fact_possession_time',
        'fact_team_zone_time'
    ]
    
    for table_name in fact_tables:
        path = OUTPUT_DIR / f'{table_name}.csv'
        if not path.exists():
            continue
        
        df = pd.read_csv(path, low_memory=False)
        changed = False
        
        if 'game_id' in df.columns:
            # Add home_team_id
            if 'home_team_id' not in df.columns:
                df['home_team_id'] = df['game_id'].map(game_home_team)
                fill = df['home_team_id'].notna().sum()
                logger.info(f"  {table_name}.home_team_id: {fill}/{len(df)}")
                changed = True
            elif df['home_team_id'].isna().all():
                df['home_team_id'] = df['game_id'].map(game_home_team)
                changed = True
            
            # Add away_team_id
            if 'away_team_id' not in df.columns:
                df['away_team_id'] = df['game_id'].map(game_away_team)
                fill = df['away_team_id'].notna().sum()
                logger.info(f"  {table_name}.away_team_id: {fill}/{len(df)}")
                changed = True
            elif df['away_team_id'].isna().all():
                df['away_team_id'] = df['game_id'].map(game_away_team)
                changed = True
        
        if changed:
            df.to_csv(path, index=False)


def add_team_id_by_venue():
    """Add team_id based on venue and game context."""
    logger.info("\n--- Adding Team ID by Venue ---")
    
    schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
    
    # Build mappings
    game_teams = {}
    for _, row in schedule.iterrows():
        game_id = row['game_id']
        game_teams[game_id] = {
            'home': row.get('home_team_id'),
            'away': row.get('away_team_id')
        }
    
    # Tables with venue and game_id but might be missing team_id
    tables = [
        'fact_shifts_player', 'fact_shifts_long', 'fact_possession_time',
        'fact_goalie_game_stats', 'fact_team_game_stats', 'fact_team_zone_time',
        'fact_line_combos'
    ]
    
    for table_name in tables:
        path = OUTPUT_DIR / f'{table_name}.csv'
        if not path.exists():
            continue
        
        df = pd.read_csv(path, low_memory=False)
        
        if 'game_id' in df.columns and 'venue' in df.columns:
            if 'team_id' not in df.columns or df['team_id'].isna().any():
                def get_team_id(row):
                    game_id = row.get('game_id')
                    venue = str(row.get('venue', '')).lower()
                    if pd.isna(game_id) or game_id not in game_teams:
                        return None
                    return game_teams[game_id].get(venue)
                
                df['team_id'] = df.apply(get_team_id, axis=1)
                fill = df['team_id'].notna().sum()
                logger.info(f"  {table_name}.team_id: {fill}/{len(df)}")
                df.to_csv(path, index=False)


def add_missing_dim_entries():
    """Add missing entries to dimension tables based on tracking data."""
    logger.info("\n--- Adding Missing Dimension Entries ---")
    
    # Check for missing shift_start_type values
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shifts.csv')
    sst = pd.read_csv(OUTPUT_DIR / 'dim_shift_start_type.csv')
    
    existing_codes = set(sst['old_equiv'].dropna().tolist())
    existing_codes.update(sst['shift_start_type_code'].dropna().tolist())
    existing_codes.update(sst['shift_start_type_name'].dropna().tolist())
    
    tracking_values = set(shifts['shift_start_type'].dropna().unique())
    missing = tracking_values - existing_codes - {'', 'nan', 'NaN'}
    
    if missing:
        logger.info(f"  Missing shift_start_type values: {missing}")
        # Add missing entries
        next_id = len(sst) + 1
        for val in missing:
            new_entry = {
                'shift_start_type_id': f'SS{next_id:04d}',
                'shift_start_type_code': val.upper().replace(' ', '_'),
                'shift_start_type_name': val,
                'start_category': 'other',
                'description': f'Auto-added from tracking data',
                'energy_factor': 1.0,
                'old_equiv': val
            }
            sst = pd.concat([sst, pd.DataFrame([new_entry])], ignore_index=True)
            next_id += 1
        
        sst.to_csv(OUTPUT_DIR / 'dim_shift_start_type.csv', index=False)
        logger.info(f"  Added {len(missing)} entries to dim_shift_start_type")


def main():
    """Run comprehensive FK population."""
    
    # First, add any missing dimension entries
    add_missing_dim_entries()
    
    # Run the main populator
    populator = ComprehensiveFKPopulator()
    populator.populate_all()
    
    # Add team FKs from schedule
    add_team_fks_from_schedule()
    
    # Add team_id by venue
    add_team_id_by_venue()
    
    logger.info("\n" + "=" * 70)
    logger.info("ALL FK POPULATION COMPLETE")
    logger.info("=" * 70)


if __name__ == '__main__':
    main()
