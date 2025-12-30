#!/usr/bin/env python3
"""
Fix dimension tables to match fact table values and create proper FK mappings.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path('data/output')


def update_dim_period():
    """Update dim_period to match fact values."""
    logger.info("Updating dim_period...")
    
    df = pd.read_csv(OUTPUT_DIR / 'dim_period.csv')
    
    # Add numeric versions for matching
    period_map = {
        '1': 'P0001', '2': 'P0002', '3': 'P0003', 
        'OT': 'P0004', 'SO': 'P0005',
        '1.0': 'P0001', '2.0': 'P0002', '3.0': 'P0003',
        1: 'P0001', 2: 'P0002', 3: 'P0003', 4: 'P0004', 5: 'P0005',
        1.0: 'P0001', 2.0: 'P0002', 3.0: 'P0003', 4.0: 'P0004', 5.0: 'P0005',
    }
    
    df.to_csv(OUTPUT_DIR / 'dim_period.csv', index=False)
    return period_map


def update_dim_event_type():
    """Update dim_event_type with actual event types from facts."""
    logger.info("Updating dim_event_type...")
    
    events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
    actual_types = events['event_type'].dropna().unique()
    
    # Build new dim table
    rows = []
    for i, et in enumerate(sorted(actual_types), 1):
        rows.append({
            'event_type_id': f'ET{i:04d}',
            'event_type_code': et,
            'event_type_name': et.replace('_', ' '),
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / 'dim_event_type.csv', index=False)
    logger.info(f"  Updated with {len(rows)} event types")
    return df.set_index('event_type_code')['event_type_id'].to_dict()


def update_dim_event_detail():
    """Update dim_event_detail with actual details from facts."""
    logger.info("Updating dim_event_detail...")
    
    events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
    actual_details = events['event_detail'].dropna().unique()
    
    rows = []
    for i, ed in enumerate(sorted(actual_details), 1):
        rows.append({
            'event_detail_id': f'ED{i:04d}',
            'event_detail_code': ed,
            'event_detail_name': ed.replace('_', ' '),
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / 'dim_event_detail.csv', index=False)
    logger.info(f"  Updated with {len(rows)} event details")
    return df.set_index('event_detail_code')['event_detail_id'].to_dict()


def update_dim_shift_slot():
    """Update dim_shift_slot with actual slots from facts."""
    logger.info("Updating dim_shift_slot...")
    
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shifts_player.csv')
    actual_slots = shifts['slot'].dropna().unique()
    
    rows = []
    for i, slot in enumerate(sorted(actual_slots), 1):
        rows.append({
            'slot_id': f'SL{i:04d}',
            'slot_code': slot,
            'slot_name': slot.replace('_', ' ').title(),
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / 'dim_shift_slot.csv', index=False)
    logger.info(f"  Updated with {len(rows)} slots")
    return df.set_index('slot_code')['slot_id'].to_dict()


def update_dim_situation():
    """Update dim_situation with actual situations from facts."""
    logger.info("Updating dim_situation...")
    
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shifts_player.csv')
    actual_situations = shifts['situation'].dropna().unique()
    
    rows = []
    for i, sit in enumerate(sorted(actual_situations), 1):
        rows.append({
            'situation_id': f'SIT{i:04d}',
            'situation_code': sit,
            'situation_name': sit,
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / 'dim_situation.csv', index=False)
    logger.info(f"  Updated with {len(rows)} situations")
    return df.set_index('situation_code')['situation_id'].to_dict()


def update_dim_success():
    """Update dim_success with actual success values."""
    logger.info("Updating dim_success...")
    
    rows = [
        {'success_id': 'SC0001', 'success_code': 's', 'success_name': 'Successful'},
        {'success_id': 'SC0002', 'success_code': 'u', 'success_name': 'Unsuccessful'},
        {'success_id': 'SC0003', 'success_code': 'S', 'success_name': 'Successful'},
        {'success_id': 'SC0004', 'success_code': 'U', 'success_name': 'Unsuccessful'},
        {'success_id': 'SC0005', 'success_code': '1', 'success_name': 'True'},
        {'success_id': 'SC0006', 'success_code': '0', 'success_name': 'False'},
    ]
    
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / 'dim_success.csv', index=False)
    return {r['success_code']: r['success_id'] for r in rows}


def apply_all_fks():
    """Apply all FK mappings to fact tables."""
    logger.info("\nApplying FKs to fact tables...")
    
    # Get updated mappings
    period_map = update_dim_period()
    event_type_map = update_dim_event_type()
    event_detail_map = update_dim_event_detail()
    slot_map = update_dim_shift_slot()
    situation_map = update_dim_situation()
    success_map = update_dim_success()
    
    # Load schedule for team IDs
    schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
    
    def get_team_id(game_id, venue):
        """Get team_id from schedule."""
        game_sched = schedule[schedule['game_id'] == int(game_id)]
        if game_sched.empty:
            return None
        if str(venue).lower() == 'home':
            return game_sched.iloc[0].get('home_team_id')
        else:
            return game_sched.iloc[0].get('away_team_id')
    
    # Venue mapping
    venue_map = {'home': 'VN0001', 'away': 'VN0002', 'Home': 'VN0001', 'Away': 'VN0002'}
    
    # Period mapping function
    def map_period(val):
        if pd.isna(val):
            return None
        # Try various formats
        for key in [val, str(val), int(val) if not pd.isna(val) else None, float(val) if not pd.isna(val) else None]:
            if key in period_map:
                return period_map[key]
        return None
    
    # ===== FACT_EVENTS_PLAYER =====
    logger.info("  Processing fact_events_player...")
    events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
    
    events['period_id'] = events['period'].apply(map_period)
    events['event_type_id'] = events['event_type'].map(event_type_map)
    events['event_detail_id'] = events['event_detail'].map(event_detail_map)
    events['success_id'] = events['event_successful'].map(success_map)
    events['venue_id'] = events['team_venue'].str.lower().map(venue_map)
    
    # Team ID
    events['team_id'] = events.apply(
        lambda r: get_team_id(r['game_id'], r['team_venue']), axis=1
    )
    
    # Shot/Pass/Turnover type IDs from event_detail
    def get_shot_type_id(row):
        if row.get('event_type') == 'Shot' and pd.notna(row.get('event_detail')):
            return event_detail_map.get(row['event_detail'])
        return None
    
    def get_pass_type_id(row):
        if row.get('event_type') == 'Pass' and pd.notna(row.get('event_detail')):
            return event_detail_map.get(row['event_detail'])
        return None
    
    def get_turnover_type_id(row):
        if row.get('event_type') == 'Turnover' and pd.notna(row.get('event_detail')):
            return event_detail_map.get(row['event_detail'])
        return None
    
    events['shot_type_id'] = events.apply(get_shot_type_id, axis=1)
    events['pass_type_id'] = events.apply(get_pass_type_id, axis=1)
    events['turnover_type_id'] = events.apply(get_turnover_type_id, axis=1)
    
    events.to_csv(OUTPUT_DIR / 'fact_events_player.csv', index=False)
    
    # ===== FACT_SHIFTS_PLAYER =====
    logger.info("  Processing fact_shifts_player...")
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shifts_player.csv')
    
    shifts['period_id'] = shifts['period'].apply(map_period)
    shifts['slot_id'] = shifts['slot'].map(slot_map)
    shifts['situation_id'] = shifts['situation'].map(situation_map)
    shifts['venue_id'] = shifts['venue'].str.lower().map(venue_map)
    
    # Team ID already done - verify
    if shifts['team_id'].isna().all():
        shifts['team_id'] = shifts.apply(
            lambda r: get_team_id(r['game_id'], r['venue']), axis=1
        )
    
    shifts.to_csv(OUTPUT_DIR / 'fact_shifts_player.csv', index=False)
    
    # ===== DERIVED TABLES =====
    # Build event key lookup - filter out NaN values first
    events_for_lookup = events[events['event_index'].notna() & events['game_id'].notna()].copy()
    events_for_lookup['game_id_int'] = events_for_lookup['game_id'].astype(int)
    events_for_lookup['event_index_int'] = events_for_lookup['event_index'].astype(int)
    
    event_keys = events_for_lookup.drop_duplicates(['game_id_int', 'event_index_int']).set_index(
        ['game_id_int', 'event_index_int']
    )['event_key'].to_dict()
    
    video_times = events_for_lookup.drop_duplicates(['game_id_int', 'event_index_int']).set_index(
        ['game_id_int', 'event_index_int']
    )['running_video_time'].to_dict()
    
    def safe_event_key_lookup(game_id, event_index):
        """Safely lookup event key."""
        if pd.isna(game_id) or pd.isna(event_index):
            return None
        return event_keys.get((int(game_id), int(event_index)))
    
    def safe_video_time_lookup(game_id, event_index):
        """Safely lookup video time."""
        if pd.isna(game_id) or pd.isna(event_index):
            return None
        return video_times.get((int(game_id), int(event_index)))
    
    # Build team lookup from events
    events_team_lookup = events_for_lookup.drop_duplicates(['game_id_int', 'event_index_int']).set_index(
        ['game_id_int', 'event_index_int']
    )['team_id'].to_dict()
    
    # Sequences
    if (OUTPUT_DIR / 'fact_sequences.csv').exists():
        logger.info("  Processing fact_sequences...")
        seq = pd.read_csv(OUTPUT_DIR / 'fact_sequences.csv')
        
        # Use 'first_event' and 'last_event' columns
        first_col = 'start_event_index' if 'start_event_index' in seq.columns else 'first_event'
        last_col = 'end_event_index' if 'end_event_index' in seq.columns else 'last_event'
        
        seq['first_event_key'] = seq.apply(
            lambda r: safe_event_key_lookup(r['game_id'], r.get(first_col)), axis=1
        )
        seq['last_event_key'] = seq.apply(
            lambda r: safe_event_key_lookup(r['game_id'], r.get(last_col)), axis=1
        )
        seq['team_id'] = seq.apply(
            lambda r: get_team_id(r['game_id'], r.get('team_venue', r.get('venue', r.get('start_team')))), axis=1
        )
        seq.to_csv(OUTPUT_DIR / 'fact_sequences.csv', index=False)
    
    # Plays
    if (OUTPUT_DIR / 'fact_plays.csv').exists():
        logger.info("  Processing fact_plays...")
        plays = pd.read_csv(OUTPUT_DIR / 'fact_plays.csv')
        
        # Use 'first_event' and 'last_event' columns
        first_col = 'start_event_index' if 'start_event_index' in plays.columns else 'first_event'
        last_col = 'end_event_index' if 'end_event_index' in plays.columns else 'last_event'
        
        if first_col in plays.columns:
            plays['first_event_key'] = plays.apply(
                lambda r: safe_event_key_lookup(r['game_id'], r.get(first_col)), axis=1
            )
        if last_col in plays.columns:
            plays['last_event_key'] = plays.apply(
                lambda r: safe_event_key_lookup(r['game_id'], r.get(last_col)), axis=1
            )
        plays['team_id'] = plays.apply(
            lambda r: get_team_id(r['game_id'], r.get('team_venue', r.get('venue', r.get('team')))), axis=1
        )
        plays.to_csv(OUTPUT_DIR / 'fact_plays.csv', index=False)
    
    # Cycles
    if (OUTPUT_DIR / 'fact_cycle_events.csv').exists():
        logger.info("  Processing fact_cycle_events...")
        cycles = pd.read_csv(OUTPUT_DIR / 'fact_cycle_events.csv')
        cycles['first_event_key'] = cycles.apply(
            lambda r: safe_event_key_lookup(r['game_id'], r.get('cycle_start_event_index')), axis=1
        )
        cycles['last_event_key'] = cycles.apply(
            lambda r: safe_event_key_lookup(r['game_id'], r.get('cycle_end_event_index')), axis=1
        )
        cycles['video_time_start'] = cycles.apply(
            lambda r: safe_video_time_lookup(r['game_id'], r.get('cycle_start_event_index')), axis=1
        )
        cycles['video_time_end'] = cycles.apply(
            lambda r: safe_video_time_lookup(r['game_id'], r.get('cycle_end_event_index')), axis=1
        )
        cycles.to_csv(OUTPUT_DIR / 'fact_cycle_events.csv', index=False)
    
    # Linked events
    if (OUTPUT_DIR / 'fact_linked_events.csv').exists():
        logger.info("  Processing fact_linked_events...")
        linked = pd.read_csv(OUTPUT_DIR / 'fact_linked_events.csv')
        
        # Add event keys for each event in chain
        for i in range(1, 10):
            idx_col = f'event_{i}_index'
            key_col = f'event_{i}_key'
            if idx_col in linked.columns:
                linked[key_col] = linked.apply(
                    lambda r, ic=idx_col: safe_event_key_lookup(r['game_id'], r.get(ic)), axis=1
                )
        
        # Get team from first event (use already defined events_team_lookup)
        def get_linked_team(row):
            if pd.isna(row.get('game_id')) or pd.isna(row.get('event_1_index')):
                return None
            return events_team_lookup.get((int(row['game_id']), int(row['event_1_index'])))
        
        linked['team_id'] = linked.apply(get_linked_team, axis=1)
        linked.to_csv(OUTPUT_DIR / 'fact_linked_events.csv', index=False)
    
    # H2H - add venue_id
    if (OUTPUT_DIR / 'fact_h2h.csv').exists():
        logger.info("  Processing fact_h2h...")
        h2h = pd.read_csv(OUTPUT_DIR / 'fact_h2h.csv')
        if 'venue' in h2h.columns:
            h2h['venue_id'] = h2h['venue'].str.lower().map(venue_map)
        h2h.to_csv(OUTPUT_DIR / 'fact_h2h.csv', index=False)
    
    # Rush events - add team_id and rush_key
    if (OUTPUT_DIR / 'fact_rush_events.csv').exists():
        logger.info("  Processing fact_rush_events...")
        rushes = pd.read_csv(OUTPUT_DIR / 'fact_rush_events.csv')
        
        # Generate rush_key
        rushes['rush_key'] = rushes.apply(
            lambda r: f"RU{int(r['game_id']):05d}{int(r['entry_event_index']):06d}"
            if pd.notna(r.get('entry_event_index')) else None, axis=1
        )
        
        # Get team from entry event
        if 'team_venue' in rushes.columns:
            rushes['team_id'] = rushes.apply(
                lambda r: get_team_id(r['game_id'], r['team_venue']), axis=1
            )
        elif 'entry_event_index' in rushes.columns:
            # Look up team from event
            rushes['team_id'] = rushes.apply(
                lambda r: events_team_lookup.get((int(r['game_id']), int(r['entry_event_index'])))
                if pd.notna(r.get('entry_event_index')) else None, axis=1
            )
        rushes.to_csv(OUTPUT_DIR / 'fact_rush_events.csv', index=False)
    
    # Goalie stats - team_id
    if (OUTPUT_DIR / 'fact_goalie_game_stats.csv').exists():
        logger.info("  Processing fact_goalie_game_stats...")
        goalie = pd.read_csv(OUTPUT_DIR / 'fact_goalie_game_stats.csv')
        goalie['team_id'] = goalie.apply(
            lambda r: get_team_id(r['game_id'], r['venue']), axis=1
        )
        goalie.to_csv(OUTPUT_DIR / 'fact_goalie_game_stats.csv', index=False)
    
    # Possession time - team_id
    if (OUTPUT_DIR / 'fact_possession_time.csv').exists():
        logger.info("  Processing fact_possession_time...")
        poss = pd.read_csv(OUTPUT_DIR / 'fact_possession_time.csv')
        poss['team_id'] = poss.apply(
            lambda r: get_team_id(r['game_id'], r['venue']), axis=1
        )
        poss.to_csv(OUTPUT_DIR / 'fact_possession_time.csv', index=False)
    
    logger.info("\nFK application complete!")


def main():
    print("=" * 70)
    print("FIXING DIMENSION MAPPINGS AND APPLYING FKs")
    print("=" * 70)
    
    apply_all_fks()
    
    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
