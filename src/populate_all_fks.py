#!/usr/bin/env python3
"""
Comprehensive Foreign Key Population Script - BenchSight

This script populates ALL missing foreign keys across ALL fact tables.
It uses dimension tables' potential_values and old_equiv columns for fuzzy matching.

Author: BenchSight ETL
Date: December 2024
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path('data/output')


# =============================================================================
# FK MAPPING DEFINITIONS
# =============================================================================
# Maps source columns to dimension tables and their FK columns

FK_MAPPINGS = {
    # Period mappings
    'period': {
        'dim_table': 'dim_period',
        'dim_pk': 'period_id',
        'match_cols': ['period_number', 'period_name'],
        'fk_col': 'period_id'
    },
    
    # Venue mappings  
    'venue': {
        'dim_table': 'dim_venue',
        'dim_pk': 'venue_id',
        'match_cols': ['venue_code', 'venue_name'],
        'fk_col': 'venue_id'
    },
    'team_venue': {
        'dim_table': 'dim_venue',
        'dim_pk': 'venue_id', 
        'match_cols': ['venue_code', 'venue_name'],
        'fk_col': 'venue_id'
    },
    
    # Event type mappings
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
    
    # Event detail mappings
    'event_detail': {
        'dim_table': 'dim_event_detail',
        'dim_pk': 'event_detail_id',
        'match_cols': ['event_detail_code', 'event_detail_name'],
        'fk_col': 'event_detail_id'
    },
    'event_detail_2': {
        'dim_table': 'dim_event_detail_2',
        'dim_pk': 'event_detail_2_id',
        'match_cols': ['event_detail_2_code', 'event_detail_2_name'],
        'fk_col': 'event_detail_2_id'
    },
    
    # Success mappings
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
    
    # Zone mappings
    'event_team_zone': {
        'dim_table': 'dim_zone',
        'dim_pk': 'zone_id',
        'match_cols': ['zone_code', 'zone_name', 'zone_abbrev'],
        'fk_col': 'zone_id'
    },
    'zone': {
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
    
    # Play detail mappings
    'play_detail1': {
        'dim_table': 'dim_play_detail',
        'dim_pk': 'play_detail_id',
        'match_cols': ['play_detail_code', 'play_detail_name'],
        'fk_col': 'play_detail_id'
    },
    'play_detail': {
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
    
    # Player role mappings
    'player_role': {
        'dim_table': 'dim_player_role',
        'dim_pk': 'role_id',
        'match_cols': ['role_code', 'role_name', 'potential_values'],
        'fk_col': 'role_id'
    },
    
    # Strength/Situation mappings
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
    
    # Shift start/stop type mappings
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
    
    # Slot mappings
    'slot': {
        'dim_table': 'dim_shift_slot',
        'dim_pk': 'slot_id',
        'match_cols': ['slot_code', 'slot_name'],
        'fk_col': 'slot_id'
    },
    
    # Position mappings
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
    
    # Zone entry/exit type mappings
    'entry_type': {
        'dim_table': 'dim_zone_entry_type',
        'dim_pk': 'zone_entry_type_id',
        'match_cols': ['zone_entry_type_code', 'zone_entry_type_name'],
        'fk_col': 'zone_entry_type_id'
    },
    
    # Shot type mappings
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
    
    # Stoppage type
    'stoppage': {
        'dim_table': 'dim_stoppage_type',
        'dim_pk': 'stoppage_type_id',
        'match_cols': ['stoppage_type_code', 'stoppage_type_name'],
        'fk_col': 'stoppage_type_id'
    },
    
    # Team mappings
    'team': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team'],
        'fk_col': 'team_id'
    },
    'home_team': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team'],
        'fk_col': 'home_team_id'
    },
    'away_team': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team'],
        'fk_col': 'away_team_id'
    },
    'start_team': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team'],
        'fk_col': 'start_team_id'
    },
    'end_team': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team'],
        'fk_col': 'end_team_id'
    },
    'team_name': {
        'dim_table': 'dim_team',
        'dim_pk': 'team_id',
        'match_cols': ['team_name', 'norad_team'],
        'fk_col': 'team_id'
    },
    
    # Season mappings
    'season': {
        'dim_table': 'dim_season',
        'dim_pk': 'season_id',
        'match_cols': ['season'],
        'fk_col': 'season_id'
    },
    
    # Comparison type
    'comparison_type': {
        'dim_table': 'dim_comparison_type',
        'dim_pk': 'comparison_type_id',
        'match_cols': ['comparison_type_code', 'comparison_type_name'],
        'fk_col': 'comparison_type_id'
    },
    
    # Net location
    'net_location': {
        'dim_table': 'dim_net_location',
        'dim_pk': 'net_location_id',
        'match_cols': ['net_location_code', 'net_location_name'],
        'fk_col': 'net_location_id'
    },
    
    # Rink coordinate
    'rink_coord': {
        'dim_table': 'dim_rink_coord',
        'dim_pk': 'rink_coord_id',
        'match_cols': ['rink_coord_code', 'rink_coord_name'],
        'fk_col': 'rink_coord_id'
    },
}


class FKPopulator:
    """Populates foreign keys across all tables."""
    
    def __init__(self):
        self.dim_cache = {}
        self.match_cache = {}
        self.stats = {'populated': 0, 'failed': 0, 'tables_processed': 0}
        
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
        """Build a dictionary mapping various values to the FK."""
        cache_key = f"{dim_name}_{pk_col}"
        if cache_key in self.match_cache:
            return self.match_cache[cache_key]
        
        dim = self.load_dimension(dim_name)
        if dim.empty:
            return {}
        
        match_dict = {}
        
        for _, row in dim.iterrows():
            pk_value = row[pk_col]
            
            # Add direct matches for all match columns
            for col in match_cols:
                if col in dim.columns and pd.notna(row[col]):
                    val = str(row[col]).strip()
                    
                    # Handle potential_values and old_equiv (comma-separated)
                    if col in ['potential_values', 'old_equiv']:
                        for v in val.split(','):
                            v = v.strip()
                            if v:
                                match_dict[v.lower()] = pk_value
                                match_dict[v] = pk_value
                                # Also try variations
                                match_dict[v.replace(' ', '')] = pk_value
                                match_dict[v.replace(' ', '').lower()] = pk_value
                                match_dict[v.replace('_', ' ')] = pk_value
                                match_dict[v.replace('_', ' ').lower()] = pk_value
                                match_dict[v.replace(' ', '_')] = pk_value
                                match_dict[v.replace(' ', '_').lower()] = pk_value
                    else:
                        match_dict[val.lower()] = pk_value
                        match_dict[val] = pk_value
                        # Add underscore/space variations
                        match_dict[val.replace(' ', '_').lower()] = pk_value
                        match_dict[val.replace('_', ' ').lower()] = pk_value
                        match_dict[val.replace(' ', '')] = pk_value
                        match_dict[val.replace(' ', '').lower()] = pk_value
        
        self.match_cache[cache_key] = match_dict
        return match_dict
    
    def lookup_fk(self, value: any, mapping: Dict) -> Optional[str]:
        """Look up a foreign key value using fuzzy matching."""
        if pd.isna(value):
            return None
        
        val_str = str(value).strip()
        dim_name = mapping['dim_table']
        pk_col = mapping['dim_pk']
        match_cols = mapping['match_cols']
        
        match_dict = self.build_match_dict(dim_name, pk_col, match_cols)
        
        if not match_dict:
            return None
        
        # Try exact match
        if val_str in match_dict:
            return match_dict[val_str]
        
        # Try lowercase
        if val_str.lower() in match_dict:
            return match_dict[val_str.lower()]
        
        # Try with underscores replaced
        val_underscore = val_str.replace(' ', '_')
        if val_underscore in match_dict:
            return match_dict[val_underscore]
        if val_underscore.lower() in match_dict:
            return match_dict[val_underscore.lower()]
        
        # Try with spaces replaced
        val_spaces = val_str.replace('_', ' ')
        if val_spaces in match_dict:
            return match_dict[val_spaces]
        if val_spaces.lower() in match_dict:
            return match_dict[val_spaces.lower()]
        
        # Try numeric conversion for periods
        if mapping['dim_table'] == 'dim_period':
            try:
                period_num = int(float(val_str))
                if str(period_num) in match_dict:
                    return match_dict[str(period_num)]
            except:
                pass
        
        return None
    
    def populate_fks_for_table(self, table_name: str):
        """Populate all possible FKs for a single table."""
        path = OUTPUT_DIR / f'{table_name}.csv'
        if not path.exists():
            return
        
        logger.info(f"\nProcessing {table_name}...")
        df = pd.read_csv(path, low_memory=False)
        original_cols = list(df.columns)
        changes = []
        
        for source_col, mapping in FK_MAPPINGS.items():
            if source_col not in df.columns:
                continue
            
            fk_col = mapping['fk_col']
            
            # Skip if FK column already exists and is populated
            if fk_col in df.columns:
                existing_fill = df[fk_col].notna().sum()
                if existing_fill > 0:
                    # Still try to fill nulls
                    null_mask = df[fk_col].isna()
                    if null_mask.sum() > 0:
                        df.loc[null_mask, fk_col] = df.loc[null_mask, source_col].apply(
                            lambda x: self.lookup_fk(x, mapping)
                        )
                        new_fill = df[fk_col].notna().sum()
                        if new_fill > existing_fill:
                            changes.append(f"  {fk_col}: {existing_fill} -> {new_fill}")
                    continue
            
            # Create new FK column
            df[fk_col] = df[source_col].apply(lambda x: self.lookup_fk(x, mapping))
            fill_rate = df[fk_col].notna().sum()
            total = len(df)
            pct = fill_rate / total * 100 if total > 0 else 0
            
            if fill_rate > 0:
                changes.append(f"  + {fk_col}: {fill_rate}/{total} ({pct:.1f}%)")
                self.stats['populated'] += fill_rate
        
        # Save if changes were made
        if changes:
            # Reorder columns - put FK columns after their source columns
            df.to_csv(path, index=False)
            logger.info(f"  Changes:")
            for change in changes:
                logger.info(change)
        else:
            logger.info(f"  No changes needed")
        
        self.stats['tables_processed'] += 1
    
    def populate_all(self):
        """Populate FKs for all fact tables."""
        logger.info("=" * 70)
        logger.info("COMPREHENSIVE FK POPULATION")
        logger.info("=" * 70)
        
        # Process all fact tables
        fact_files = sorted(OUTPUT_DIR.glob('fact_*.csv'))
        
        for fact_file in fact_files:
            table_name = fact_file.stem
            self.populate_fks_for_table(table_name)
        
        logger.info("\n" + "=" * 70)
        logger.info("FK POPULATION COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Tables processed: {self.stats['tables_processed']}")
        logger.info(f"FKs populated: {self.stats['populated']}")


def add_team_fks():
    """Add team FKs to tables that have team name columns but no team_id."""
    logger.info("\n--- Adding Team FKs ---")
    
    teams = pd.read_csv(OUTPUT_DIR / 'dim_team.csv')
    team_lookup = {}
    for _, row in teams.iterrows():
        if pd.notna(row.get('team_name')):
            team_lookup[str(row['team_name']).lower()] = row['team_id']
        if pd.notna(row.get('norad_team')):
            team_lookup[str(row['norad_team']).lower()] = row['team_id']
    
    # Tables with team_name but potentially missing team_id
    team_tables = [
        ('fact_player_boxscore_all', ['team_name', 'opp_team_name'], ['team_id', 'opp_team_id']),
        ('fact_team_standings_snapshot', ['team_name'], ['team_id']),
        ('fact_league_leaders_snapshot', ['team_name'], ['team_id']),
        ('fact_team_game_stats', ['venue'], ['team_id']),  # Special case - need game context
    ]
    
    for table_name, src_cols, fk_cols in team_tables:
        path = OUTPUT_DIR / f'{table_name}.csv'
        if not path.exists():
            continue
        
        df = pd.read_csv(path, low_memory=False)
        changed = False
        
        for src_col, fk_col in zip(src_cols, fk_cols):
            if src_col in df.columns and fk_col not in df.columns:
                df[fk_col] = df[src_col].apply(
                    lambda x: team_lookup.get(str(x).lower()) if pd.notna(x) else None
                )
                fill = df[fk_col].notna().sum()
                logger.info(f"  {table_name}.{fk_col}: {fill}/{len(df)}")
                changed = True
        
        if changed:
            df.to_csv(path, index=False)


def add_schedule_fks():
    """Add schedule/game related FKs."""
    logger.info("\n--- Adding Schedule FKs ---")
    
    schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
    
    # Build game -> team mapping
    game_home_team = {}
    game_away_team = {}
    game_venue = {}
    
    for _, row in schedule.iterrows():
        game_id = row['game_id']
        if pd.notna(row.get('home_team_id')):
            game_home_team[game_id] = row['home_team_id']
        if pd.notna(row.get('away_team_id')):
            game_away_team[game_id] = row['away_team_id']
    
    # Add to tables with game_id
    fact_tables_needing_teams = [
        'fact_h2h', 'fact_wowy', 'fact_line_combos', 'fact_head_to_head',
        'fact_player_game_stats', 'fact_goalie_game_stats', 'fact_team_game_stats'
    ]
    
    for table_name in fact_tables_needing_teams:
        path = OUTPUT_DIR / f'{table_name}.csv'
        if not path.exists():
            continue
        
        df = pd.read_csv(path, low_memory=False)
        changed = False
        
        if 'game_id' in df.columns:
            if 'home_team_id' not in df.columns or df['home_team_id'].isna().all():
                df['home_team_id'] = df['game_id'].map(game_home_team)
                changed = True
            if 'away_team_id' not in df.columns or df['away_team_id'].isna().all():
                df['away_team_id'] = df['game_id'].map(game_away_team)
                changed = True
        
        if changed:
            df.to_csv(path, index=False)
            logger.info(f"  {table_name}: Added home/away team IDs")


def main():
    """Run comprehensive FK population."""
    
    # First, run the main populator
    populator = FKPopulator()
    populator.populate_all()
    
    # Then add special FK mappings
    add_team_fks()
    add_schedule_fks()
    
    logger.info("\n" + "=" * 70)
    logger.info("ALL FK POPULATION COMPLETE")
    logger.info("=" * 70)


if __name__ == '__main__':
    main()
