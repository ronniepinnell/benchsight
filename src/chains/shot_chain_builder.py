#!/usr/bin/env python3
"""
Shot Chain Builder - Creates fact_shot_chains table.

Tracks zone_entry → shot chains with enhanced metrics.

Version: 8.0.2
Date: January 6, 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path('data/output')


def build_shot_chains():
    """
    Build fact_shot_chains from fact_events.
    
    A shot chain is: Zone_Entry → [events...] → Shot/Goal
    """
    logger.info("Building fact_shot_chains...")
    
    # Load source data
    events_path = OUTPUT_DIR / 'fact_events.csv'
    if not events_path.exists():
        logger.warning("fact_events.csv not found, skipping shot chains")
        return None
    
    events = pd.read_csv(events_path, low_memory=False)
    
    # Zone entries - only actual entries (not exits/keepins)
    zone_entries = events[
        (events['event_detail'].str.contains('Zone_Entry', case=False, na=False)) &
        (~events['event_detail'].str.contains('failed', case=False, na=False))
    ].copy()
    
    # Shots - any shot attempt including goals
    shots = events[
        (events['is_sog'] == 1) | 
        (events['is_goal'] == 1) |
        (events['event_type'] == 'Shot') |
        (events['event_type'] == 'Goal')
    ].copy()
    
    logger.info(f"  Zone entries: {len(zone_entries)}, Shots/Goals: {len(shots)}")
    
    if zone_entries.empty or shots.empty:
        logger.warning("No zone entries or shots found")
        return None
    
    chains = []
    chain_counter = 0
    
    # Process each game
    for game_id in events['game_id'].unique():
        game_events = events[events['game_id'] == game_id].sort_values('event_running_start')
        game_entries = zone_entries[zone_entries['game_id'] == game_id].copy()
        game_shots = shots[shots['game_id'] == game_id].sort_values('event_running_start')
        
        if game_entries.empty or game_shots.empty:
            continue
        
        # For each zone entry, find the next shot
        for idx, entry in game_entries.iterrows():
            entry_time = entry['event_running_start']
            if pd.isna(entry_time):
                continue
            
            # Find next shot after this entry (within 60 sec)
            candidate_shots = game_shots[
                (game_shots['event_running_start'] > entry_time) &
                (game_shots['event_running_start'] <= entry_time + 60)
            ]
            
            if candidate_shots.empty:
                continue
            
            shot = candidate_shots.iloc[0]
            shot_time = shot['event_running_start']
            time_to_shot = shot_time - entry_time
            
            # Events in the chain
            chain_events = game_events[
                (game_events['event_running_start'] >= entry_time) &
                (game_events['event_running_start'] <= shot_time)
            ]
            
            events_to_shot = len(chain_events)
            pass_count = len(chain_events[chain_events['event_type'] == 'Pass'])
            
            # Get unique players
            player_ids = set()
            for val in chain_events['event_player_ids'].dropna():
                if isinstance(val, str):
                    player_ids.update(val.split(','))
            touch_count = len(player_ids)
            
            # Build chain description
            event_types_chain = ' > '.join(chain_events['event_type'].dropna().tolist())
            event_details_chain = ' > '.join(chain_events['event_detail'].dropna().astype(str).tolist())
            
            # Shot result and goal flag
            is_goal = shot.get('is_goal', 0) == 1
            shot_result = 'Goal' if is_goal else shot.get('event_detail', 'Unknown')
            
            # Entry type
            entry_type = entry.get('event_detail_2')
            if pd.isna(entry_type) or entry_type == '':
                entry_type = entry.get('event_detail', 'ZoneEntry-Unknown')
            
            # Player info
            entry_player_id = str(entry['event_player_ids']).split(',')[0] if pd.notna(entry.get('event_player_ids')) else None
            entry_player_name = entry.get('player_name')
            shot_player_id = str(shot['event_player_ids']).split(',')[0] if pd.notna(shot.get('event_player_ids')) else None
            shot_player_name = shot.get('player_name')
            
            # Team info
            team_id = entry.get('home_team_id') if entry.get('event_team_zone') == 'o' else entry.get('away_team_id')
            team_name = entry.get('home_team') if entry.get('event_team_zone') == 'o' else entry.get('away_team')
            
            # Build chain record
            chain_counter += 1
            chain_id = f"CH{game_id}{chain_counter:05d}"
            
            chain = {
                'chain_id': chain_id,
                'game_id': game_id,
                'season_id': entry.get('season_id'),
                'period': entry.get('period'),
                'entry_event_key': entry.get('event_id'),
                'shot_event_key': shot.get('event_id'),
                'time_to_shot': round(time_to_shot, 1),
                'pass_count': pass_count,
                'events_to_shot': events_to_shot,
                'touch_count': touch_count,
                'entry_type': entry_type,
                'shot_result': shot_result,
                'is_goal': is_goal,
                'team_id': team_id,
                'team_name': team_name,
                'home_team_id': entry.get('home_team_id'),
                'away_team_id': entry.get('away_team_id'),
                'home_team_name': entry.get('home_team'),
                'away_team_name': entry.get('away_team'),
                'event_types_chain': event_types_chain,
                'event_details_chain': event_details_chain,
                'entry_player_id': entry_player_id,
                'entry_player_name': entry_player_name,
                'shot_player_id': shot_player_id,
                'shot_player_name': shot_player_name,
                'sequence_key': entry.get('sequence_key'),
                'play_key': entry.get('play_key'),
                'zone_id': entry.get('event_zone_id'),
                'zone_entry_type_id': entry.get('zone_entry_type_id'),
                'shot_result_detail_id': shot.get('event_detail_id'),
                'time_bucket_id': entry.get('time_bucket_id'),
                'strength_id': entry.get('strength_id'),
                'shot_type_id': shot.get('shot_type_id'),
            }
            chains.append(chain)
    
    if not chains:
        logger.warning("No shot chains found")
        return None
    
    df = pd.DataFrame(chains)
    df = df.sort_values(['game_id', 'chain_id']).reset_index(drop=True)
    
    # Save
    output_path = OUTPUT_DIR / 'fact_shot_chains.csv'
    df.to_csv(output_path, index=False)
    
    logger.info(f"  ✓ fact_shot_chains: {len(df)} rows, {len(df.columns)} cols")
    logger.info(f"    Games: {df['game_id'].nunique()}")
    logger.info(f"    Goals: {df['is_goal'].sum()}")
    logger.info(f"    Avg time_to_shot: {df['time_to_shot'].mean():.1f}s")
    logger.info(f"    Avg pass_count: {df['pass_count'].mean():.1f}")
    
    return df


def main():
    """Entry point."""
    build_shot_chains()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
