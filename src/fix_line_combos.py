#!/usr/bin/env python3
"""
Fix Line Combo Stats - BenchSight

This script rebuilds fact_line_combos with proper stats calculation.

The previous implementation only counted shifts. This version calculates:
- toi_together: Total time on ice when combo is together (seconds)
- goals_for: Goals scored while combo on ice
- goals_against: Goals allowed while combo on ice  
- corsi_for: Shot attempts for (shots + blocks + misses)
- corsi_against: Shot attempts against
- xgf: Expected goals for (simplified model)
- plus_minus: GF - GA
- shifts: Number of shift segments together

Author: BenchSight ETL
Date: December 2024
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path('data/output')


def parse_combo_players(combo_str: str) -> Set[str]:
    """Parse player IDs from a combo string like 'P100001_P100064_P100132'."""
    if pd.isna(combo_str) or combo_str == '':
        return set()
    return set(combo_str.split('_'))


def get_shifts_for_combo(
    shifts: pd.DataFrame,
    game_id: int,
    venue: str,
    forward_combo: str,
    defense_combo: str
) -> pd.DataFrame:
    """Get all shift_index values where this exact combo was on ice together."""
    
    forward_players = parse_combo_players(forward_combo)
    defense_players = parse_combo_players(defense_combo)
    all_combo_players = forward_players | defense_players
    
    if not all_combo_players:
        return pd.DataFrame()
    
    # Filter to game and venue
    game_shifts = shifts[(shifts['game_id'] == game_id) & (shifts['venue'] == venue)]
    
    if game_shifts.empty:
        return pd.DataFrame()
    
    # Find shift_index values where ALL combo players are present
    shift_player_sets = game_shifts.groupby('shift_index')['player_id'].apply(set)
    
    # A shift matches if all combo players are in the shift
    matching_shifts = shift_player_sets[
        shift_player_sets.apply(lambda x: all_combo_players.issubset(x))
    ].index.tolist()
    
    return game_shifts[game_shifts['shift_index'].isin(matching_shifts)]


def calculate_combo_stats(
    shifts: pd.DataFrame,
    events: pd.DataFrame,
    game_id: int,
    venue: str,
    forward_combo: str,
    defense_combo: str
) -> Dict:
    """Calculate all stats for a line combo."""
    
    combo_shifts = get_shifts_for_combo(shifts, game_id, venue, forward_combo, defense_combo)
    
    if combo_shifts.empty:
        return {
            'toi_together': 0,
            'goals_for': 0,
            'goals_against': 0,
            'corsi_for': 0,
            'corsi_against': 0,
            'xgf': 0.0,
            'plus_minus': 0,
            'shifts': 0
        }
    
    # Get unique shift indices for this combo
    combo_shift_indices = combo_shifts['shift_index'].unique().tolist()
    
    # TOI: Sum shift_duration for first player (all players same duration per shift)
    toi = combo_shifts.groupby('shift_index')['shift_duration'].first().sum()
    
    # Goals: Sum from shifts (already tracked per shift)
    # Use first player per shift to avoid double counting
    shift_stats = combo_shifts.groupby('shift_index').first()
    gf = int(shift_stats['goal_for'].sum())
    ga = int(shift_stats['goal_against'].sum())
    
    # Shifts count
    shifts_count = len(combo_shift_indices)
    
    # Corsi and xG from events
    corsi_for = 0
    corsi_against = 0
    xgf = 0.0
    
    if not events.empty and 'shift_index' in events.columns:
        # Get events during combo shifts
        combo_events = events[
            (events['game_id'] == game_id) & 
            (events['shift_index'].isin(combo_shift_indices))
        ]
        
        if not combo_events.empty:
            opp_venue = 'away' if venue == 'home' else 'home'
            
            # Corsi For: Our team's shot attempts
            team_shot_events = combo_events[
                (combo_events['team_venue'].str.lower() == venue) &
                (combo_events['event_type'].isin(['Shot', 'Goal']))
            ]
            corsi_for = len(team_shot_events.drop_duplicates('event_index'))
            
            # Corsi Against: Opponent's shot attempts
            opp_shot_events = combo_events[
                (combo_events['team_venue'].str.lower() == opp_venue) &
                (combo_events['event_type'].isin(['Shot', 'Goal']))
            ]
            corsi_against = len(opp_shot_events.drop_duplicates('event_index'))
            
            # xG: Simplified model based on shot type
            for _, shot in team_shot_events.drop_duplicates('event_index').iterrows():
                detail = str(shot.get('event_detail', '')).lower()
                if 'goal' in detail:
                    xgf += 1.0
                elif 'onnet' in detail:
                    xgf += 0.08
                elif 'blocked' in detail:
                    xgf += 0.02
                else:
                    xgf += 0.05  # Generic shot
    
    return {
        'toi_together': int(toi),
        'goals_for': gf,
        'goals_against': ga,
        'corsi_for': corsi_for,
        'corsi_against': corsi_against,
        'xgf': round(xgf, 2),
        'plus_minus': gf - ga,
        'shifts': shifts_count
    }


def rebuild_line_combos():
    """Rebuild fact_line_combos with proper stats."""
    
    logger.info("=" * 60)
    logger.info("REBUILDING LINE COMBO STATS")
    logger.info("=" * 60)
    
    # Load current line combos (has the combo groupings)
    combos_file = OUTPUT_DIR / 'fact_line_combos.csv'
    shifts_file = OUTPUT_DIR / 'fact_shifts_player.csv'
    events_file = OUTPUT_DIR / 'fact_events_player.csv'
    
    if not combos_file.exists():
        logger.error(f"fact_line_combos.csv not found at {combos_file}")
        return
    
    if not shifts_file.exists():
        logger.error(f"fact_shifts_player.csv not found")
        return
    
    # Load data
    combos = pd.read_csv(combos_file)
    shifts = pd.read_csv(shifts_file)
    events = pd.read_csv(events_file, low_memory=False) if events_file.exists() else pd.DataFrame()
    
    # Normalize types
    shifts['game_id'] = shifts['game_id'].astype(int)
    combos['game_id'] = combos['game_id'].astype(int)
    if not events.empty:
        events['game_id'] = pd.to_numeric(events['game_id'], errors='coerce').fillna(0).astype(int)
        if 'shift_index' in events.columns:
            events['shift_index'] = pd.to_numeric(events['shift_index'], errors='coerce')
    
    logger.info(f"Loaded {len(combos)} line combos to process")
    logger.info(f"Loaded {len(shifts)} shift records")
    logger.info(f"Loaded {len(events)} event records")
    
    # Calculate stats for each combo
    results = []
    
    for idx, row in combos.iterrows():
        if idx % 50 == 0:
            logger.info(f"  Processing combo {idx + 1}/{len(combos)}...")
        
        stats = calculate_combo_stats(
            shifts=shifts,
            events=events,
            game_id=row['game_id'],
            venue=row['venue'],
            forward_combo=row['forward_combo'],
            defense_combo=row['defense_combo']
        )
        
        result = {
            'game_id': row['game_id'],
            'venue': row['venue'],
            'forward_combo': row['forward_combo'],
            'defense_combo': row['defense_combo'],
            **stats,
            'home_team_id': row.get('home_team_id'),
            'away_team_id': row.get('away_team_id'),
            'venue_id': row.get('venue_id')
        }
        results.append(result)
    
    # Create output dataframe
    df = pd.DataFrame(results)
    
    # Sort by game_id, venue, TOI (descending)
    df = df.sort_values(['game_id', 'venue', 'toi_together'], ascending=[True, True, False])
    
    # Reorder columns
    col_order = [
        'game_id', 'venue', 'forward_combo', 'defense_combo',
        'shifts', 'toi_together', 'goals_for', 'goals_against', 'plus_minus',
        'corsi_for', 'corsi_against', 'xgf',
        'home_team_id', 'away_team_id', 'venue_id'
    ]
    df = df[[c for c in col_order if c in df.columns]]
    
    # Save
    df.to_csv(combos_file, index=False)
    
    logger.info(f"\n✓ Rebuilt fact_line_combos with {len(df)} rows")
    logger.info(f"  Columns: {list(df.columns)}")
    
    # Show sample
    logger.info("\nSample output (top 5 by TOI):")
    sample = df.nlargest(5, 'toi_together')[['game_id', 'venue', 'forward_combo', 'shifts', 'toi_together', 'goals_for', 'goals_against', 'plus_minus']]
    print(sample.to_string(index=False))
    
    # Summary stats
    logger.info(f"\nStats Summary:")
    logger.info(f"  Total TOI: {df['toi_together'].sum():,} seconds ({df['toi_together'].sum() / 60:.1f} minutes)")
    logger.info(f"  Total GF: {df['goals_for'].sum()}")
    logger.info(f"  Total GA: {df['goals_against'].sum()}")
    logger.info(f"  Total CF: {df['corsi_for'].sum()}")
    logger.info(f"  Total CA: {df['corsi_against'].sum()}")
    
    return df


if __name__ == '__main__':
    rebuild_line_combos()
