#!/usr/bin/env python3
"""
Comprehensive fixes for BenchSight ETL:
1. Shift counts use logical_shift_number
2. Video table from video_times files
3. Video time columns in shifts/events
4. Team/Player possession time table
5. Goalie stats for both teams
6. Foreign keys in fact tables
7. Sequence/play/chain keys
8. Linked events table
9. Min/max video times in aggregated tables
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

RAW_DIR = Path('data/raw/games')
OUTPUT_DIR = Path('data/output')
TRACKED_GAMES = ['18969', '18977', '18981', '18987']


def generate_key(game_id, index, prefix='E'):
    """Generate a key."""
    if pd.isna(index):
        return None
    return f"{prefix}{int(game_id):05d}{int(index):06d}"


def build_fact_video():
    """Build fact_video from video_times files."""
    logger.info("Building fact_video...")
    
    all_videos = []
    for game_dir in RAW_DIR.iterdir():
        if not game_dir.is_dir():
            continue
        video_file = game_dir / f'{game_dir.name}_video_times.xlsx'
        if video_file.exists():
            try:
                df = pd.read_excel(video_file)
                df['game_id'] = game_dir.name
                # Generate key
                df['video_key'] = df.apply(
                    lambda r: f"V{int(r['game_id']):05d}{int(r.get('Index', 0)):03d}", axis=1
                )
                all_videos.append(df)
            except Exception as e:
                logger.warning(f"Error loading video for {game_dir.name}: {e}")
    
    if all_videos:
        df = pd.concat(all_videos, ignore_index=True)
        # Reorder columns
        cols = ['video_key', 'game_id'] + [c for c in df.columns if c not in ['video_key', 'game_id']]
        df = df[cols]
        df.to_csv(OUTPUT_DIR / 'fact_video.csv', index=False)
        logger.info(f"  ✓ fact_video: {len(df)} rows")
        return df
    return pd.DataFrame()


def build_fact_possession_time(events_file):
    """Build team and player possession time by zone."""
    logger.info("Building fact_possession_time...")
    
    events = pd.read_csv(events_file, low_memory=False)
    
    # Get possession events (zone entries, exits, and duration-based events)
    possession_rows = []
    
    for game_id in events['game_id'].unique():
        game_events = events[events['game_id'] == game_id]
        
        # Player-level possession stats
        for player_id in game_events['player_id'].dropna().unique():
            player_events = game_events[game_events['player_id'] == player_id]
            primary_events = player_events[player_events['player_role'] == 'event_team_player_1']
            
            # Get venue
            venue = primary_events['team_venue'].mode()
            venue = venue.iloc[0] if len(venue) > 0 else 'unknown'
            
            # Zone entries
            entries = primary_events[primary_events['event_detail'].str.contains('Entry', na=False)]
            exits = primary_events[primary_events['event_detail'].str.contains('Exit', na=False)]
            
            # Possession events
            poss_events = primary_events[primary_events['event_type'] == 'Possession']
            
            # Calculate possession time estimate from duration column
            if 'duration' in primary_events.columns:
                total_duration = pd.to_numeric(primary_events['duration'], errors='coerce').sum()
            else:
                total_duration = 0
            
            possession_rows.append({
                'possession_key': f"PO{int(game_id):05d}{abs(hash(player_id)) % 100000:05d}",
                'game_id': game_id,
                'player_id': player_id,
                'venue': venue,
                'zone_entries': len(entries),
                'zone_exits': len(exits),
                'ozone_entries': len(entries[entries['event_team_zone'].str.lower() == 'o']) if 'event_team_zone' in entries.columns else 0,
                'dzone_entries': len(entries[entries['event_team_zone'].str.lower() == 'd']) if 'event_team_zone' in entries.columns else 0,
                'possession_events': len(poss_events),
                'estimated_possession_seconds': total_duration,
            })
    
    if possession_rows:
        df = pd.DataFrame(possession_rows)
        df.to_csv(OUTPUT_DIR / 'fact_possession_time.csv', index=False)
        logger.info(f"  ✓ fact_possession_time: {len(df)} rows")
        return df
    return pd.DataFrame()


def fix_goalie_stats():
    """Fix goalie stats to include both teams."""
    logger.info("Fixing fact_goalie_game_stats...")
    
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shifts_player.csv')
    events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
    
    # Normalize game_id types
    events['game_id'] = events['game_id'].astype(str)
    shifts['game_id'] = shifts['game_id'].astype(str)
    
    # Get all goalies from shifts
    goalies = shifts[shifts['slot'] == 'goalie']
    
    goalie_stats = []
    for (game_id, player_id), group in goalies.groupby(['game_id', 'player_id']):
        venue = group['venue'].iloc[0]
        player_name = group['player_name'].iloc[0] if 'player_name' in group.columns else None
        
        # TOI
        toi_seconds = group['shift_duration'].sum()
        playing_seconds = toi_seconds - group['stoppage_time'].sum() if 'stoppage_time' in group.columns else toi_seconds
        
        # Goals against - count unique shifts with goal_against = 1
        goals_against = len(group[group['goal_against'] == 1].drop_duplicates('shift_index'))
        
        # Get saves from events - Save events where this goalie is event_team_player_1
        game_events = events[events['game_id'] == str(game_id)]
        
        # Save events for this goalie
        save_events = game_events[
            (game_events['player_id'] == player_id) &
            (game_events['event_type'] == 'Save') &
            (game_events['player_role'] == 'event_team_player_1')
        ]
        saves = len(save_events.drop_duplicates('event_index'))
        
        # Calculate shots faced from saves + goals against
        shots_faced = saves + goals_against
        
        goalie_stats.append({
            'goalie_game_key': f"GG{int(game_id):05d}{abs(hash(player_id)) % 100000:05d}",
            'game_id': game_id,
            'player_id': player_id,
            'player_name': player_name,
            'venue': venue,
            'saves': saves,
            'goals_against': goals_against,
            'toi_seconds': toi_seconds,
            'toi_minutes': round(toi_seconds / 60, 1) if toi_seconds else 0,
            'playing_toi_seconds': playing_seconds,
            'playing_toi_minutes': round(playing_seconds / 60, 1) if playing_seconds else 0,
            'stoppage_seconds': toi_seconds - playing_seconds,
            'shots_faced': shots_faced,
            'save_pct': round(saves / shots_faced * 100, 1) if shots_faced > 0 else 0,
            'gaa': round(goals_against / (toi_seconds / 60) * 60, 2) if toi_seconds > 0 else 0,
            'gaa_playing': round(goals_against / (playing_seconds / 60) * 60, 2) if playing_seconds > 0 else 0,
        })
    
    if goalie_stats:
        df = pd.DataFrame(goalie_stats)
        df.to_csv(OUTPUT_DIR / 'fact_goalie_game_stats.csv', index=False)
        logger.info(f"  ✓ fact_goalie_game_stats: {len(df)} rows")
        return df
    return pd.DataFrame()


def build_fact_linked_events():
    """Build linked events table (wide format)."""
    logger.info("Building fact_linked_events...")
    
    events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
    
    # Get events with linked_event_index
    linked = events[events['linked_event_index'].notna()].copy()
    
    if linked.empty:
        logger.info("  No linked events found")
        return pd.DataFrame()
    
    # Group linked events
    linked_groups = []
    for (game_id, link_idx), group in linked.groupby(['game_id', 'linked_event_index']):
        # Get all events in this chain
        chain_events = events[
            (events['game_id'] == game_id) & 
            (events['event_index'].isin([link_idx] + group['event_index'].tolist()))
        ]
        
        # Get unique events
        unique_events = chain_events.drop_duplicates('event_index').sort_values('event_index')
        
        if len(unique_events) < 2:
            continue
        
        # Create wide record
        record = {
            'linked_event_key': f"LE{int(game_id):05d}{int(link_idx):06d}",
            'game_id': game_id,
            'primary_event_index': int(link_idx),
            'event_count': len(unique_events),
        }
        
        for i, (_, evt) in enumerate(unique_events.iterrows(), 1):
            record[f'event_{i}_index'] = evt['event_index']
            record[f'event_{i}_type'] = evt.get('event_type')
            record[f'event_{i}_detail'] = evt.get('event_detail')
            record[f'event_{i}_player_id'] = evt.get('player_id')
        
        linked_groups.append(record)
    
    if linked_groups:
        df = pd.DataFrame(linked_groups)
        df.to_csv(OUTPUT_DIR / 'fact_linked_events.csv', index=False)
        logger.info(f"  ✓ fact_linked_events: {len(df)} rows")
        return df
    return pd.DataFrame()


def add_video_time_columns_to_shifts():
    """Add video time columns to fact_shifts_player."""
    logger.info("Adding video time columns to shifts...")
    
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shifts_player.csv')
    
    # Load raw shift data to get video columns
    for game_id in shifts['game_id'].unique():
        tracking_file = RAW_DIR / str(game_id) / f'{game_id}_tracking.xlsx'
        if tracking_file.exists():
            try:
                raw_shifts = pd.read_excel(tracking_file, sheet_name='shifts')
                
                # Create lookup by shift_index
                video_cols = ['running_video_time', 'shift_start_running_time', 'shift_end_running_time']
                for col in video_cols:
                    if col in raw_shifts.columns:
                        lookup = raw_shifts.set_index('shift_index')[col].to_dict()
                        mask = shifts['game_id'] == game_id
                        shifts.loc[mask, col] = shifts.loc[mask, 'shift_index'].map(lookup)
            except Exception as e:
                logger.warning(f"Error loading shifts for {game_id}: {e}")
    
    shifts.to_csv(OUTPUT_DIR / 'fact_shifts_player.csv', index=False)
    logger.info(f"  ✓ Added video columns to fact_shifts_player")
    return shifts


def add_video_time_aggregates():
    """Add min/max video time columns to aggregated tables."""
    logger.info("Adding video time aggregates...")
    
    # Load events and shifts
    events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
    
    # Ensure numeric columns
    for col in ['running_video_time', 'event_running_start', 'event_running_end']:
        if col in events.columns:
            events[col] = pd.to_numeric(events[col], errors='coerce')
    
    # Add to player game stats
    stats_file = OUTPUT_DIR / 'fact_player_game_stats.csv'
    if stats_file.exists():
        stats = pd.read_csv(stats_file)
        
        # Calculate min/max per player-game
        for (game_id, player_id), group in events.groupby(['game_id', 'player_id']):
            mask = (stats['game_id'] == game_id) & (stats['player_id'] == player_id)
            if mask.any():
                if 'running_video_time' in group.columns:
                    stats.loc[mask, 'video_time_min'] = group['running_video_time'].min()
                    stats.loc[mask, 'video_time_max'] = group['running_video_time'].max()
                if 'event_running_start' in group.columns:
                    stats.loc[mask, 'event_start_min'] = group['event_running_start'].min()
                    stats.loc[mask, 'event_end_max'] = group['event_running_end'].max()
        
        stats.to_csv(stats_file, index=False)
        logger.info(f"  ✓ Added video aggregates to fact_player_game_stats")


def add_strength_fk():
    """Add strength_id foreign key to tables."""
    logger.info("Adding strength_id FK...")
    
    # Load dim_strength
    strength = pd.read_csv(OUTPUT_DIR / 'dim_strength.csv')
    strength_map = strength.set_index('strength_code')['strength_id'].to_dict()
    
    # Update shifts
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shifts_player.csv')
    shifts['strength_id'] = shifts['strength'].map(strength_map)
    shifts.to_csv(OUTPUT_DIR / 'fact_shifts_player.csv', index=False)
    
    # Update events if strength column exists
    events_file = OUTPUT_DIR / 'fact_events_player.csv'
    events = pd.read_csv(events_file, low_memory=False)
    if 'strength' in events.columns:
        events['strength_id'] = events['strength'].map(strength_map)
        events.to_csv(events_file, index=False)
    
    logger.info(f"  ✓ Added strength_id FK")


def fix_sequence_play_keys():
    """Add proper keys to sequence/play/chain tables."""
    logger.info("Fixing sequence/play/chain keys...")
    
    events = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv', low_memory=False)
    
    # Build event_key lookup
    event_keys = events.set_index(['game_id', 'event_index'])['event_key'].drop_duplicates().to_dict()
    
    # Fix fact_sequences
    seq_file = OUTPUT_DIR / 'fact_sequences.csv'
    if seq_file.exists():
        seq = pd.read_csv(seq_file)
        if 'sequence_index' in seq.columns and 'game_id' in seq.columns:
            seq['sequence_key'] = seq.apply(
                lambda r: f"SQ{int(r['game_id']):05d}{int(r['sequence_index']):06d}" 
                if pd.notna(r.get('sequence_index')) else None, axis=1
            )
            # Add first_event_key
            if 'start_event_index' in seq.columns:
                seq['first_event_key'] = seq.apply(
                    lambda r: event_keys.get((str(r['game_id']), r['start_event_index'])), axis=1
                )
            seq.to_csv(seq_file, index=False)
            logger.info(f"  ✓ Fixed fact_sequences keys")
    
    # Fix fact_plays
    plays_file = OUTPUT_DIR / 'fact_plays.csv'
    if plays_file.exists():
        plays = pd.read_csv(plays_file)
        if 'play_index' in plays.columns and 'game_id' in plays.columns:
            plays['play_key'] = plays.apply(
                lambda r: f"PL{int(r['game_id']):05d}{int(r['play_index']):06d}"
                if pd.notna(r.get('play_index')) else None, axis=1
            )
            plays.to_csv(plays_file, index=False)
            logger.info(f"  ✓ Fixed fact_plays keys")
    
    # Fix fact_event_chains
    chains_file = OUTPUT_DIR / 'fact_event_chains.csv'
    if chains_file.exists():
        chains = pd.read_csv(chains_file)
        # Check if chain_key already exists and is valid
        if 'chain_key' not in chains.columns or chains['chain_key'].isna().all():
            if 'game_id' in chains.columns:
                chains['chain_key'] = chains.apply(
                    lambda r: f"CH{int(r['game_id']):05d}{int(r.get('start_event_index', r.get('event_index', 0))):06d}"
                    if pd.notna(r.get('game_id')) and pd.notna(r.get('start_event_index', r.get('event_index'))) else None, 
                    axis=1
                )
        # Add event_key reference
        if 'event_index' in chains.columns and 'game_id' in chains.columns:
            chains['event_key'] = chains.apply(
                lambda r: event_keys.get((str(r['game_id']), r['event_index'])) if pd.notna(r.get('event_index')) else None, 
                axis=1
            )
        chains.to_csv(chains_file, index=False)
        logger.info(f"  ✓ Fixed fact_event_chains keys")


def update_dim_strength():
    """Update dim_strength with all strength values from shifts."""
    logger.info("Updating dim_strength...")
    
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shifts_player.csv')
    strength = pd.read_csv(OUTPUT_DIR / 'dim_strength.csv')
    
    # Get all unique strength values
    shift_strengths = set(shifts['strength'].dropna().unique())
    existing = set(strength['strength_code'])
    
    # Find missing
    missing = shift_strengths - existing
    
    if missing:
        new_rows = []
        for i, s in enumerate(sorted(missing), len(strength) + 1):
            new_rows.append({
                'strength_id': f'STR{i:04d}',
                'strength_code': s,
                'strength_name': s,
                'situation_type': 'en' if 'EN' in s else 'special',
                'xg_multiplier': 1.0,
                'description': f'Auto-added: {s}',
                'avg_toi_pct': 0.01
            })
        
        strength = pd.concat([strength, pd.DataFrame(new_rows)], ignore_index=True)
        strength.to_csv(OUTPUT_DIR / 'dim_strength.csv', index=False)
        logger.info(f"  ✓ Added {len(new_rows)} strength values: {list(missing)}")
    else:
        logger.info("  No new strength values needed")
    
    return strength


def main():
    """Run all fixes."""
    print("=" * 70)
    print("COMPREHENSIVE ETL FIXES")
    print("=" * 70)
    
    # 1. Build video table
    build_fact_video()
    
    # 2. Add video columns to shifts
    add_video_time_columns_to_shifts()
    
    # 3. Fix goalie stats (both teams)
    fix_goalie_stats()
    
    # 4. Build possession time table
    events_file = OUTPUT_DIR / 'fact_events_player.csv'
    if events_file.exists():
        build_fact_possession_time(events_file)
    
    # 5. Build linked events table
    build_fact_linked_events()
    
    # 6. Update dim_strength with missing values
    update_dim_strength()
    
    # 7. Add strength_id FK
    add_strength_fk()
    
    # 8. Fix sequence/play/chain keys
    fix_sequence_play_keys()
    
    # 9. Add video time aggregates
    add_video_time_aggregates()
    
    print("\n" + "=" * 70)
    print("FIXES COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
