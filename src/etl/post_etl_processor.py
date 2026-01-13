#!/usr/bin/env python3
"""
BENCHSIGHT UNIFIED POST-ETL PROCESSOR
=====================================

This script runs AFTER base_etl.py and handles all enhancements in the correct order.
It is designed to be:
- DYNAMIC: Works for any games in the data
- IDEMPOTENT: Can be run multiple times safely
- INTEGRATED: All enhancements in one place, correct order

Run Order:
1. base_etl.py (main ETL)
2. post_etl_processor.py (this script)

Enhancements Applied:
1. Fix dimension key formats (position, player_role, venue, zone, play_detail_2)
2. Update FK references in all fact tables
3. Add game_state_id (based on goal differential)
4. Add competition_tier_id (based on player ratings)
5. Add cascade columns (expected values from dimensions)
6. Create/update fact_player_season_stats
7. Enhance fact_team_game_stats with ratings

Version: 6.5.22
Date: January 6, 2026
Author: BenchSight ETL Team
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from src.core.table_writer import save_output_table

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path('data/output')

# ============================================================
# DIMENSION KEY FORMAT DEFINITIONS
# ============================================================
# Format: (old_format_check, new_prefix, digits)
# If old_format_check is None, it's already correct

DIMENSION_KEY_FORMATS = {
    'dim_position': ('position_id', lambda x: not str(x).startswith('PO'), 'PO', 2),
    'dim_player_role': ('role_id', lambda x: not str(x).startswith('PR'), 'PR', 2),
    'dim_venue': ('venue_id', lambda x: not str(x).startswith('VN'), 'VN', 2),
    'dim_zone': ('zone_id', lambda x: not str(x).startswith('ZN'), 'ZN', 2),
    'dim_play_detail_2': ('play_detail_2_id', lambda x: 'PD2_' in str(x), None, None),  # Special handling
}

# Fact tables and their FK columns to update
FK_COLUMNS_MAP = {
    'position_id': ['fact_events', 'fact_event_players', 'fact_player_game_stats', 'fact_gameroster'],
    'player_role_id': ['fact_event_players'],
    'venue_id': ['fact_team_game_stats'],
    'team_venue_id': ['fact_event_players'],
    'zone_id': ['fact_shifts'],
    'event_zone_id': ['fact_events', 'fact_event_players'],
    'home_zone_id': ['fact_event_players'],
    'away_zone_id': ['fact_event_players'],
    'play_detail_2_id': ['fact_event_players'],
}

# ============================================================
# GAME STATE DEFINITIONS
# ============================================================
GAME_STATES = {
    'GS01': {'code': 'TIED', 'name': 'Tied', 'goal_diff_min': 0, 'goal_diff_max': 0},
    'GS02': {'code': 'LEAD_1', 'name': 'Leading by 1', 'goal_diff_min': 1, 'goal_diff_max': 1},
    'GS03': {'code': 'LEAD_2', 'name': 'Leading by 2', 'goal_diff_min': 2, 'goal_diff_max': 2},
    'GS04': {'code': 'LEAD_3P', 'name': 'Leading by 3+', 'goal_diff_min': 3, 'goal_diff_max': 99},
    'GS05': {'code': 'TRAIL_1', 'name': 'Trailing by 1', 'goal_diff_min': -1, 'goal_diff_max': -1},
    'GS06': {'code': 'TRAIL_2P', 'name': 'Trailing by 2+', 'goal_diff_min': -99, 'goal_diff_max': -2},
}

# ============================================================
# COMPETITION TIER DEFINITIONS (based on average player rating)
# ============================================================
COMPETITION_TIERS = {
    'CT01': {'name': 'Elite', 'min_rating': 5.5, 'max_rating': 7.0},
    'CT02': {'name': 'High', 'min_rating': 4.5, 'max_rating': 5.49},
    'CT03': {'name': 'Medium', 'min_rating': 3.5, 'max_rating': 4.49},
    'CT04': {'name': 'Low', 'min_rating': 2.0, 'max_rating': 3.49},
}

# ============================================================
# CASCADE COLUMN DEFINITIONS
# ============================================================
CASCADE_DEFINITIONS = {
    # From dim_pass_type
    'pass_type_id': {
        'expected_completion_pct': 'expected_completion_rate',
        'pass_danger_value': 'danger_value',
        'xa_modifier': 'xa_modifier',
    },
    # From dim_shot_type
    'shot_type_id': {
        'xg_modifier': 'xg_modifier',
        'shot_accuracy_rating': 'accuracy_rating',
    },
    # From dim_giveaway_type
    'giveaway_type_id': {
        'giveaway_xga_impact': 'xga_impact',
        'giveaway_danger_level': 'danger_level',
    },
    # From dim_takeaway_type
    'takeaway_type_id': {
        'takeaway_xgf_impact': 'xgf_impact',
        'takeaway_value_weight': 'value_weight',
    },
    # From dim_turnover_type
    'turnover_type_id': {
        'turnover_weight': 'weight',
        'turnover_zone_multiplier': 'zone_danger_multiplier',
        'turnover_category': 'category',
    },
    # From dim_zone_entry_type
    'zone_entry_type_id': {
        'zone_entry_success_rate': 'expected_success_rate',
        'zone_entry_goal_mult': 'goal_prob_multiplier',
        'zone_entry_control': 'control_level',
    },
    # From dim_zone_exit_type
    'zone_exit_type_id': {
        'zone_exit_possession_pct': 'possession_retained_pct',
        'zone_exit_entry_pct': 'leads_to_entry_pct',
        'zone_exit_value': 'offensive_value_weight',
        'zone_exit_control': 'control_level',
    },
}


def fix_dimension_key_format(dim_name: str, id_col: str, needs_fix_func, prefix: str, digits: int) -> Dict[str, str]:
    """Fix dimension key format and return mapping of old->new IDs."""
    path = OUTPUT_DIR / f'{dim_name}.csv'
    if not path.exists():
        return {}
    
    df = pd.read_csv(path)
    
    # Check if any need fixing
    needs_fix = df[id_col].apply(needs_fix_func)
    if not needs_fix.any():
        return {}
    
    # Create mapping
    id_map = {}
    
    if dim_name == 'dim_play_detail_2':
        # Special handling - remove underscore
        for idx, row in df.iterrows():
            old_id = str(row[id_col])
            new_id = old_id.replace('PD2_', 'PD2')
            id_map[old_id] = new_id
            df.at[idx, id_col] = new_id
    else:
        # Standard numeric -> prefix format
        for idx, row in df.iterrows():
            old_id = str(row[id_col])
            if needs_fix_func(old_id):
                try:
                    num = int(float(old_id))
                    new_id = f'{prefix}{num:0{digits}d}'
                    id_map[old_id] = new_id
                    df.at[idx, id_col] = new_id
                except ValueError:
                    pass
    
    if id_map:
        save_output_table(df, path.stem, path.parent)
        logger.info(f"Fixed {len(id_map)} keys in {dim_name}")
    
    return id_map


def update_fk_in_fact_table(table_name: str, fk_col: str, id_map: Dict[str, str]) -> int:
    """Update FK column in a fact table using ID mapping."""
    if not id_map:
        return 0
    
    path = OUTPUT_DIR / f'{table_name}.csv'
    if not path.exists():
        return 0
    
    df = pd.read_csv(path, low_memory=False)
    if fk_col not in df.columns:
        return 0
    
    # Expand id_map to include float versions (e.g., "1" -> also map "1.0")
    expanded_map = dict(id_map)
    for old_id, new_id in id_map.items():
        try:
            # Add float string version
            float_ver = f"{float(old_id)}"
            expanded_map[float_ver] = new_id
            # Add integer version
            int_ver = str(int(float(old_id)))
            expanded_map[int_ver] = new_id
        except (ValueError, TypeError):
            pass
    
    # Special handling for venue_id format mismatch (VN0001 -> VN01)
    if fk_col == 'venue_id':
        expanded_map['VN0001'] = 'VN01'
        expanded_map['VN0002'] = 'VN02'
        expanded_map['VN0003'] = 'VN03'
    
    # Special handling for zone_id format mismatch
    if 'zone_id' in fk_col:
        for i in range(1, 10):
            expanded_map[f'ZN000{i}'] = f'ZN0{i}'
            expanded_map[f'ZN00{i}'] = f'ZN0{i}'
    
    # Apply mapping
    original = df[fk_col].astype(str)
    df[fk_col] = original.map(lambda x: expanded_map.get(x, x))
    
    changes = (original != df[fk_col].astype(str)).sum()
    if changes > 0:
        save_output_table(df, path.stem, path.parent)
    
    return changes


def calculate_game_state_id(home_score: int, away_score: int, is_home_team: bool) -> str:
    """
    Calculate game_state_id based on goal differential from team's perspective.
    
    Args:
        home_score: Home team goals
        away_score: Away team goals
        is_home_team: True if calculating for home team
    
    Returns:
        Game state ID (GS01-GS06)
    """
    if is_home_team:
        diff = home_score - away_score
    else:
        diff = away_score - home_score
    
    for gs_id, gs_def in GAME_STATES.items():
        if gs_def['goal_diff_min'] <= diff <= gs_def['goal_diff_max']:
            return gs_id
    
    return 'GS01'  # Default to tied


def calculate_competition_tier_id(avg_opp_rating: float) -> str:
    """
    Calculate competition_tier_id based on average opponent rating.
    
    Args:
        avg_opp_rating: Average rating of opponents
    
    Returns:
        Competition tier ID (CT01-CT04)
    """
    if pd.isna(avg_opp_rating):
        return 'CT03'  # Default to Medium
    
    for ct_id, ct_def in COMPETITION_TIERS.items():
        if ct_def['min_rating'] <= avg_opp_rating <= ct_def['max_rating']:
            return ct_id
    
    return 'CT03'  # Default to Medium


def add_game_state_to_events():
    """Add game_state_id to fact_events based on running score."""
    logger.info("Adding game_state_id to fact_events...")
    
    events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv')
    
    if 'game_state_id' in events.columns and events['game_state_id'].notna().sum() > len(events) * 0.5:
        logger.info("  game_state_id already populated")
        return
    
    # Need to derive scoring_team_id from tracking data for goals
    # For Goal_Scored events, event_player_1 is the scorer
    tracking = pd.read_csv(OUTPUT_DIR / 'fact_event_players.csv', low_memory=False)
    
    # Get scoring team for goals (from Goal_Scored row, event_player_1)
    goal_scorers = tracking[
        (tracking['event_type'] == 'Goal') & 
        (tracking['event_detail'] == 'Goal_Scored') &
        (tracking['player_role'] == 'event_player_1')
    ][['event_id', 'player_team_id']].drop_duplicates()
    goal_scorers.columns = ['event_id', 'scoring_team_id']
    
    events = events.merge(goal_scorers, on='event_id', how='left')
    
    # Sort chronologically by period and time, NOT by event_id
    # event_id order doesn't match chronological order when tracking has multiple sources
    sort_cols = ['game_id', 'period']
    if 'event_start_min' in events.columns:
        sort_cols.append('event_start_min')
    if 'event_start_sec' in events.columns:
        sort_cols.append('event_start_sec')
    events = events.sort_values(sort_cols)
    
    # Initialize game_state_id
    if 'game_state_id' not in events.columns:
        events['game_state_id'] = None
    
    # Calculate running score per game
    for game_id in events['game_id'].unique():
        game_mask = events['game_id'] == game_id
        game_events = events.loc[game_mask]
        
        home_team = game_events['home_team_id'].iloc[0]
        away_team = game_events['away_team_id'].iloc[0]
        
        home_score = 0
        away_score = 0
        
        for idx in game_events.index:
            event = events.loc[idx]
            
            # Calculate game state BEFORE this event (from home team perspective)
            diff = home_score - away_score
            
            if diff == 0:
                gs_id = 'GS01'  # Tied
            elif diff == 1:
                gs_id = 'GS02'  # Leading by 1
            elif diff == 2:
                gs_id = 'GS03'  # Leading by 2
            elif diff >= 3:
                gs_id = 'GS04'  # Leading by 3+
            elif diff == -1:
                gs_id = 'GS05'  # Trailing by 1
            else:  # diff <= -2
                gs_id = 'GS06'  # Trailing by 2+
            
            events.loc[idx, 'game_state_id'] = gs_id
            
            # Check if this is a goal and update score
            is_goal = event.get('is_goal', 0) == 1
            
            if is_goal:
                scoring_team = event.get('scoring_team_id')
                if scoring_team == home_team:
                    home_score += 1
                elif scoring_team == away_team:
                    away_score += 1
    
    # Remove temporary column if we added it
    if 'scoring_team_id' in events.columns:
        events = events.drop(columns=['scoring_team_id'])
    
    save_output_table(events, 'fact_events', OUTPUT_DIR)
    populated = events['game_state_id'].notna().sum()
    logger.info(f"  Added game_state_id: {populated}/{len(events)} populated")


def add_competition_tier_to_events():
    """Add competition_tier_id to fact_events based on opponent ratings."""
    logger.info("Adding competition_tier_id to fact_events...")
    
    events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv')
    
    if 'competition_tier_id' in events.columns:
        if events['competition_tier_id'].notna().sum() > len(events) * 0.5:
            logger.info("  competition_tier_id already populated")
            return
    
    # Get average opponent rating per game from team_game_stats
    tgs_path = OUTPUT_DIR / 'fact_team_game_stats.csv'
    if tgs_path.exists():
        tgs = pd.read_csv(tgs_path)
        
        # Check for opp_rating column
        opp_rating_col = None
        for col in ['opp_avg_rating', 'avg_opp_rating', 'qoc_rating']:
            if col in tgs.columns:
                opp_rating_col = col
                break
        
        if opp_rating_col:
            # Map game_id + venue to opp rating
            game_ratings = tgs[['game_id', 'venue', opp_rating_col]].copy()
            game_ratings.columns = ['game_id', 'venue', 'opp_rating']
            
            # Calculate tier based on opponent rating
            def get_tier(rating):
                if pd.isna(rating):
                    return 'CT03'  # Medium
                if rating >= 5.5:
                    return 'CT01'  # Elite
                elif rating >= 4.5:
                    return 'CT02'  # High
                elif rating >= 3.5:
                    return 'CT03'  # Medium
                else:
                    return 'CT04'  # Low
            
            game_ratings['competition_tier_id'] = game_ratings['opp_rating'].apply(get_tier)
            
            # Merge - use home team's perspective for simplicity
            home_ratings = game_ratings[game_ratings['venue'] == 'Home'][['game_id', 'competition_tier_id']]
            events = events.merge(home_ratings, on='game_id', how='left', suffixes=('_old', ''))
            
            # Remove old column if exists
            if 'competition_tier_id_old' in events.columns:
                events = events.drop(columns=['competition_tier_id_old'])
            
            # Fill missing with default
            events['competition_tier_id'] = events['competition_tier_id'].fillna('CT03')
            
            save_output_table(events, 'fact_events', OUTPUT_DIR)
            populated = events['competition_tier_id'].notna().sum()
            logger.info(f"  Added competition_tier_id: {populated}/{len(events)} populated")
            return
    
    # Fallback - use average event_team_rating if available
    if 'opp_team_rating_avg' in events.columns:
        def get_tier(rating):
            if pd.isna(rating):
                return 'CT03'
            if rating >= 5.5:
                return 'CT01'
            elif rating >= 4.5:
                return 'CT02'
            elif rating >= 3.5:
                return 'CT03'
            else:
                return 'CT04'
        
        events['competition_tier_id'] = events['opp_team_rating_avg'].apply(get_tier)
        save_output_table(events, 'fact_events', OUTPUT_DIR)
        populated = events['competition_tier_id'].notna().sum()
        logger.info(f"  Added competition_tier_id: {populated}/{len(events)} populated")
    else:
        events['competition_tier_id'] = 'CT03'  # Default
        save_output_table(events, 'fact_events', OUTPUT_DIR)
        logger.info("  Added competition_tier_id: default CT03 (no rating data)")


def add_turnover_quality_id():
    """Add turnover_quality_id based on giveaway/takeaway type."""
    logger.info("Adding turnover_quality_id to fact_events...")
    
    events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv')
    
    if 'turnover_quality_id' in events.columns:
        if events['turnover_quality_id'].notna().sum() > 0:
            logger.info("  turnover_quality_id already populated")
            return
    
    # Load giveaway types for quality mapping
    giveaway_types = pd.read_csv(OUTPUT_DIR / 'dim_giveaway_type.csv')
    
    quality_map = {
        'bad': 'TQ0001',
        'neutral': 'TQ0002',
        'good': 'TQ0003',
    }
    
    # Check if turnover_quality column exists
    if 'turnover_quality' not in giveaway_types.columns:
        # Create default quality based on giveaway type name
        def infer_quality(name):
            name_lower = str(name).lower()
            if 'interc' in name_lower or 'steal' in name_lower:
                return 'bad'  # Bad for the player who lost it
            elif 'clear' in name_lower or 'dump' in name_lower:
                return 'neutral'
            else:
                return 'neutral'
        giveaway_types['turnover_quality'] = giveaway_types['giveaway_type_name'].apply(infer_quality)
    
    giveaway_quality = dict(zip(
        giveaway_types['giveaway_type_id'],
        giveaway_types['turnover_quality'].map(quality_map)
    ))
    
    events['turnover_quality_id'] = None
    
    # Map from giveaway type
    mask = events['giveaway_type_id'].notna()
    events.loc[mask, 'turnover_quality_id'] = events.loc[mask, 'giveaway_type_id'].map(giveaway_quality)
    
    # Takeaways are good quality
    mask = events['takeaway_type_id'].notna() & events['turnover_quality_id'].isna()
    events.loc[mask, 'turnover_quality_id'] = 'TQ0003'
    
    save_output_table(events, 'fact_events', OUTPUT_DIR)
    populated = events['turnover_quality_id'].notna().sum()
    logger.info(f"  Added turnover_quality_id: {populated}/{len(events)} populated")


def add_cascade_columns(table_name: str = 'fact_events'):
    """Add cascade columns from dimension tables."""
    logger.info(f"Adding cascade columns to {table_name}...")
    
    path = OUTPUT_DIR / f'{table_name}.csv'
    if not path.exists():
        return
    
    df = pd.read_csv(path, low_memory=False)
    
    added_cols = []
    
    for fk_col, col_mappings in CASCADE_DEFINITIONS.items():
        if fk_col not in df.columns:
            continue
        
        # Determine dimension table name from FK column
        dim_name = 'dim_' + fk_col.replace('_id', '').replace('_type', '_type')
        dim_path = OUTPUT_DIR / f'{dim_name}.csv'
        
        if not dim_path.exists():
            continue
        
        dim_df = pd.read_csv(dim_path)
        
        for new_col, dim_col in col_mappings.items():
            if new_col in df.columns:
                continue
            
            if dim_col not in dim_df.columns:
                continue
            
            # Create mapping
            mapping = dict(zip(dim_df[fk_col], dim_df[dim_col]))
            df[new_col] = df[fk_col].map(mapping)
            added_cols.append(new_col)
    
    if added_cols:
        save_output_table(df, path.stem, path.parent)
        logger.info(f"  Added {len(added_cols)} cascade columns")


def propagate_to_tracking():
    """Propagate new columns from fact_events to fact_event_players."""
    logger.info("Propagating columns to fact_event_players...")
    
    events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv')
    tracking = pd.read_csv(OUTPUT_DIR / 'fact_event_players.csv', low_memory=False)
    
    # Columns to propagate
    cols_to_check = [
        'game_state_id', 'competition_tier_id', 'turnover_quality_id',
        'expected_completion_pct', 'pass_danger_value', 'xa_modifier',
        'xg_modifier', 'shot_accuracy_rating',
        'giveaway_xga_impact', 'giveaway_danger_level',
        'takeaway_xgf_impact', 'takeaway_value_weight',
        'turnover_weight', 'turnover_zone_multiplier', 'turnover_category',
        'zone_entry_success_rate', 'zone_entry_goal_mult', 'zone_entry_control',
        'zone_exit_possession_pct', 'zone_exit_entry_pct', 'zone_exit_value', 'zone_exit_control',
    ]
    
    cols_to_add = [c for c in cols_to_check if c in events.columns and c not in tracking.columns]
    
    if cols_to_add:
        events_subset = events[['event_id'] + cols_to_add].drop_duplicates()
        tracking = tracking.merge(events_subset, on='event_id', how='left')
        save_output_table(tracking, 'fact_event_players', OUTPUT_DIR)
        logger.info(f"  Propagated {len(cols_to_add)} columns")


def main():
    """Main entry point for post-ETL processing."""
    logger.info("=" * 60)
    logger.info("BENCHSIGHT POST-ETL PROCESSOR v6.5.22")
    logger.info("=" * 60)
    
    # Step 1: Fix dimension key formats
    logger.info("\n[1/6] Fixing dimension key formats...")
    all_id_maps = {}
    
    for dim_name, (id_col, needs_fix_func, prefix, digits) in DIMENSION_KEY_FORMATS.items():
        id_map = fix_dimension_key_format(dim_name, id_col, needs_fix_func, prefix, digits)
        if id_map:
            all_id_maps[dim_name] = (id_col, id_map)
    
    # Step 2: Update FK references
    logger.info("\n[2/6] Updating FK references in fact tables...")
    for fk_col, tables in FK_COLUMNS_MAP.items():
        # Find which dimension this FK relates to
        for dim_name, (id_col, id_map) in all_id_maps.items():
            if id_col == fk_col or id_col.replace('_id', '') in fk_col:
                for table in tables:
                    changes = update_fk_in_fact_table(table, fk_col, id_map)
                    if changes > 0:
                        logger.info(f"  Updated {changes} rows in {table}.{fk_col}")
    
    # Step 3: Add game_state_id
    logger.info("\n[3/6] Adding game_state_id...")
    add_game_state_to_events()
    
    # Step 4: Add competition_tier_id
    logger.info("\n[4/6] Adding competition_tier_id...")
    add_competition_tier_to_events()
    
    # Step 5: Add turnover_quality_id and cascade columns
    logger.info("\n[5/6] Adding cascade columns...")
    add_turnover_quality_id()
    add_cascade_columns('fact_events')
    
    # Also add to derived tables
    derived_tables = [
        'fact_zone_entries', 'fact_zone_exits', 'fact_turnovers_detailed',
        'fact_rushes', 'fact_breakouts', 'fact_scoring_chances_detailed'
    ]
    for table in derived_tables:
        if (OUTPUT_DIR / f'{table}.csv').exists():
            add_cascade_columns(table)
    
    # Step 6: Propagate to tracking
    logger.info("\n[6/6] Propagating to tracking tables...")
    propagate_to_tracking()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("POST-ETL PROCESSING COMPLETE")
    logger.info("=" * 60)
    
    # Verify
    events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv')
    logger.info(f"\nfact_events: {len(events)} rows, {len(events.columns)} columns")
    logger.info(f"  game_state_id: {events['game_state_id'].notna().sum()} populated")
    logger.info(f"  competition_tier_id: {events['competition_tier_id'].notna().sum()} populated")


if __name__ == '__main__':
    main()
