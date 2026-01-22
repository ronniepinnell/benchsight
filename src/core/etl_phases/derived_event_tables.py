"""
Derived Event Tables Module
===========================

Contains functions for creating derived tables from events data.

Functions:
- create_fact_sequences: Aggregate events by sequence_key
- create_fact_plays: Aggregate events by play_key
- create_derived_event_tables: Create specialized derived tables from enhanced events
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Import table writer for saving
from src.core.table_writer import save_output_table

# Import utilities
from .utilities import drop_all_null_columns


def create_fact_sequences(output_dir: Path, log, save_table_func=None):
    """Create fact_sequences aggregating events by sequence_key.

    Args:
        output_dir: Path to output directory
        log: ETLLogger instance
        save_table_func: Function to save tables (optional)
    """
    log.section("PHASE 5.7: CREATE FACT_SEQUENCES")

    if save_table_func is None:
        save_table_func = lambda df, name: save_output_table(df, name, output_dir)

    events_path = output_dir / 'fact_events.csv'
    tracking_path = output_dir / 'fact_event_players.csv'

    if not events_path.exists():
        log.warn("fact_events not found, skipping fact_sequences")
        return

    events = pd.read_csv(events_path, low_memory=False)
    tracking = pd.read_csv(tracking_path, low_memory=False)

    log.info(f"Aggregating {len(events)} events into sequences...")

    events = events.sort_values(['sequence_key', 'event_id'])
    sequences = []

    for seq_key, grp in events.groupby('sequence_key'):
        if pd.isna(seq_key):
            continue

        grp = grp.sort_values('event_id')
        first = grp.iloc[0]
        last = grp.iloc[-1]

        # Count event types
        event_types = grp['event_type'].value_counts().to_dict()

        # Check for goals - use is_goal flag (only Goal + Goal_Scored)
        has_goal = grp['is_goal'].sum() > 0 if 'is_goal' in grp.columns else False
        goal_count = grp['is_goal'].sum() if 'is_goal' in grp.columns else 0

        # Shots - count Shot events only, not Goal events
        shot_count = event_types.get('Shot', 0)

        # Zone entries/exits
        zone_entries = grp['zone_entry_type_id'].notna().sum()
        zone_exits = grp['zone_exit_type_id'].notna().sum()

        # Passes
        pass_count = event_types.get('Pass', 0)
        pass_success = grp[(grp['event_type'] == 'Pass') & (grp['event_successful'] == 's')].shape[0]

        # Turnovers
        turnover_count = event_types.get('Turnover', 0)
        giveaway_count = grp['giveaway_type_id'].notna().sum()
        takeaway_count = grp['takeaway_type_id'].notna().sum()

        # Players
        all_players = set()
        for pids in grp['event_player_ids'].dropna():
            all_players.update(str(pids).split(','))
        all_players.discard('')

        seq = {
            'sequence_key': seq_key,
            'sequence_id': seq_key,
            'game_id': int(first['game_id']),
            'season_id': first.get('season_id') if 'season_id' in first.index else None,
            'period': int(first['period']),
            'period_id': first.get('period_id') if 'period_id' in first.index else None,
            'first_event_key': first['event_id'],
            'last_event_key': last['event_id'],
            'event_count': len(grp),
            'duration_seconds': grp['duration'].sum(),
            'time_bucket_id': first['time_bucket_id'],
            'strength_id': first['strength_id'],
            'home_team': first['home_team'],
            'home_team_id': first['home_team_id'],
            'away_team': first['away_team'],
            'away_team_id': first['away_team_id'],
            'start_zone': first['event_team_zone'],
            'end_zone': last['event_team_zone'],
            'start_zone_id': first['event_zone_id'],
            'end_zone_id': last['event_zone_id'],
            'event_types': ','.join(grp['event_type'].dropna().astype(str).tolist()),
            'has_goal': has_goal,
            'goal_count': goal_count,
            'shot_count': shot_count,
            'zone_entry_count': zone_entries,
            'zone_exit_count': zone_exits,
            'pass_count': pass_count,
            'pass_success_count': pass_success,
            'pass_success_rate': pass_success / pass_count if pass_count > 0 else None,
            'turnover_count': turnover_count,
            'giveaway_count': giveaway_count,
            'takeaway_count': takeaway_count,
            'unique_player_count': len(all_players),
            'player_ids': ','.join(sorted(all_players)) if all_players else None,
        }
        sequences.append(seq)

    seq_df = pd.DataFrame(sequences)
    seq_df = seq_df.sort_values(['game_id', 'period', 'first_event_key'])

    # Add video times from tracking
    tracking_first = tracking.groupby('event_id').first().reset_index()
    video_map = dict(zip(tracking_first['event_id'], tracking_first['running_video_time']))
    video_end_map = dict(zip(tracking_first['event_id'], tracking_first['event_running_end']))
    start_min_map = dict(zip(tracking_first['event_id'], tracking_first['event_start_min']))
    start_sec_map = dict(zip(tracking_first['event_id'], tracking_first['event_start_sec']))

    seq_df['video_time_start'] = seq_df['first_event_key'].map(video_map)
    seq_df['video_time_end'] = seq_df['last_event_key'].map(video_end_map)
    seq_df['start_min'] = seq_df['first_event_key'].map(start_min_map)
    seq_df['start_sec'] = seq_df['first_event_key'].map(start_sec_map)

    # Reorder columns
    col_order = [
        'sequence_key', 'sequence_id', 'game_id', 'season_id', 'period', 'period_id',
        'first_event_key', 'last_event_key', 'event_count',
        'start_min', 'start_sec', 'duration_seconds', 'video_time_start', 'video_time_end',
        'time_bucket_id', 'strength_id',
        'home_team', 'home_team_id', 'away_team', 'away_team_id',
        'start_zone', 'end_zone', 'start_zone_id', 'end_zone_id',
        'event_types', 'has_goal', 'goal_count', 'shot_count',
        'zone_entry_count', 'zone_exit_count',
        'pass_count', 'pass_success_count', 'pass_success_rate',
        'turnover_count', 'giveaway_count', 'takeaway_count',
        'unique_player_count', 'player_ids'
    ]
    seq_df = seq_df[[c for c in col_order if c in seq_df.columns]]

    save_table_func(seq_df, 'fact_sequences')
    log.info(f"  ✓ fact_sequences: {len(seq_df)} rows, {len(seq_df.columns)} cols")
    log.info(f"    Goals: {seq_df['has_goal'].sum()}, Avg events/seq: {seq_df['event_count'].mean():.1f}")


def create_fact_plays(output_dir: Path, log, save_table_func=None):
    """Create fact_plays aggregating events by play_key.

    Args:
        output_dir: Path to output directory
        log: ETLLogger instance
        save_table_func: Function to save tables (optional)
    """
    log.section("PHASE 5.8: CREATE FACT_PLAYS")

    if save_table_func is None:
        save_table_func = lambda df, name: save_output_table(df, name, output_dir)

    events_path = output_dir / 'fact_events.csv'
    tracking_path = output_dir / 'fact_event_players.csv'

    if not events_path.exists():
        log.warn("fact_events not found, skipping fact_plays")
        return

    events = pd.read_csv(events_path, low_memory=False)
    tracking = pd.read_csv(tracking_path, low_memory=False)

    # Ensure season_id exists in events (fallback from schedule if missing)
    if 'season_id' not in events.columns or events['season_id'].isna().all():
        log.info("  Adding season_id from schedule (fallback)...")
        schedule_path = output_dir / 'dim_schedule.csv'
        if schedule_path.exists():
            schedule = pd.read_csv(schedule_path, low_memory=False)
            season_map = dict(zip(schedule['game_id'].astype(int), schedule['season_id']))
            events['season_id'] = events['game_id'].astype(int).map(season_map)
            log.info(f"    season_id added: {events['season_id'].notna().sum()}/{len(events)} mapped")

    log.info(f"Aggregating {len(events)} events into plays...")

    events = events.sort_values(['play_key', 'event_id'])
    plays = []

    for play_key, grp in events.groupby('play_key'):
        if pd.isna(play_key):
            continue

        grp = grp.sort_values('event_id')
        first = grp.iloc[0]
        last = grp.iloc[-1]

        event_types = grp['event_type'].value_counts().to_dict()
        has_goal = grp['is_goal'].sum() > 0 if 'is_goal' in grp.columns else False
        goal_count = grp['is_goal'].sum() if 'is_goal' in grp.columns else 0
        has_shot = ('Shot' in event_types) or has_goal
        shot_count = event_types.get('Shot', 0)
        zone_entries = grp['zone_entry_type_id'].notna().sum()
        zone_exits = grp['zone_exit_type_id'].notna().sum()
        pass_count = event_types.get('Pass', 0)
        pass_success = grp[(grp['event_type'] == 'Pass') & (grp['event_successful'] == 's')].shape[0]
        turnover_count = event_types.get('Turnover', 0)
        giveaway_count = grp['giveaway_type_id'].notna().sum()
        takeaway_count = grp['takeaway_type_id'].notna().sum()

        all_players = set()
        for pids in grp['event_player_ids'].dropna():
            all_players.update(str(pids).split(','))
        all_players.discard('')

        play = {
            'play_key': play_key, 'play_id': play_key,
            'game_id': int(first['game_id']), 'season_id': first.get('season_id') if 'season_id' in first.index else None,
            'period': int(first['period']), 'period_id': first.get('period_id') if 'period_id' in first.index else None,
            'sequence_key': first['sequence_key'],
            'first_event_key': first['event_id'], 'last_event_key': last['event_id'],
            'event_count': len(grp), 'duration_seconds': grp['duration'].sum(),
            'time_bucket_id': first['time_bucket_id'], 'strength_id': first['strength_id'],
            'home_team': first['home_team'], 'home_team_id': first['home_team_id'],
            'away_team': first['away_team'], 'away_team_id': first['away_team_id'],
            'start_zone': first['event_team_zone'], 'end_zone': last['event_team_zone'],
            'start_zone_id': first['event_zone_id'], 'end_zone_id': last['event_zone_id'],
            'event_types': ','.join(grp['event_type'].dropna().astype(str).tolist()),
            'has_goal': has_goal, 'goal_count': goal_count, 'has_shot': has_shot, 'shot_count': shot_count,
            'zone_entry_count': zone_entries, 'zone_exit_count': zone_exits,
            'pass_count': pass_count, 'pass_success_count': pass_success,
            'turnover_count': turnover_count, 'giveaway_count': giveaway_count,
            'takeaway_count': takeaway_count,
            'unique_player_count': len(all_players),
            'player_ids': ','.join(sorted(all_players)) if all_players else None,
        }
        plays.append(play)

    plays_df = pd.DataFrame(plays)
    plays_df = plays_df.sort_values(['game_id', 'period', 'first_event_key'])

    # Add video times from tracking
    tracking_first = tracking.groupby('event_id').first().reset_index()
    video_map = dict(zip(tracking_first['event_id'], tracking_first['running_video_time']))
    video_end_map = dict(zip(tracking_first['event_id'], tracking_first['event_running_end']))
    start_min_map = dict(zip(tracking_first['event_id'], tracking_first['event_start_min']))
    start_sec_map = dict(zip(tracking_first['event_id'], tracking_first['event_start_sec']))

    plays_df['video_time_start'] = plays_df['first_event_key'].map(video_map)
    plays_df['video_time_end'] = plays_df['last_event_key'].map(video_end_map)
    plays_df['start_min'] = plays_df['first_event_key'].map(start_min_map)
    plays_df['start_sec'] = plays_df['first_event_key'].map(start_sec_map)

    col_order = [
        'play_key', 'play_id', 'game_id', 'season_id', 'period', 'period_id', 'sequence_key',
        'first_event_key', 'last_event_key', 'event_count',
        'start_min', 'start_sec', 'duration_seconds', 'video_time_start', 'video_time_end',
        'time_bucket_id', 'strength_id',
        'home_team', 'home_team_id', 'away_team', 'away_team_id',
        'start_zone', 'end_zone', 'start_zone_id', 'end_zone_id',
        'event_types', 'has_goal', 'goal_count', 'has_shot', 'shot_count',
        'zone_entry_count', 'zone_exit_count',
        'pass_count', 'pass_success_count',
        'turnover_count', 'giveaway_count', 'takeaway_count',
        'unique_player_count', 'player_ids'
    ]
    plays_df = plays_df[[c for c in col_order if c in plays_df.columns]]

    save_table_func(plays_df, 'fact_plays')
    log.info(f"  ✓ fact_plays: {len(plays_df)} rows, {len(plays_df.columns)} cols")
    log.info(f"    Goals: {plays_df['has_goal'].sum()}, Shots: {plays_df['has_shot'].sum()}, Avg events/play: {plays_df['event_count'].mean():.1f}")


def create_derived_event_tables(output_dir: Path, log, save_table_func=None):
    """Create specialized derived tables from enhanced events.

    Args:
        output_dir: Path to output directory
        log: ETLLogger instance
        save_table_func: Function to save tables (optional)
    """
    log.section("PHASE 5.10: CREATE DERIVED EVENT TABLES")

    if save_table_func is None:
        save_table_func = lambda df, name: save_output_table(df, name, output_dir)

    events = pd.read_csv(output_dir / 'fact_events.csv', low_memory=False)

    # dim_danger_level
    dim_danger = pd.DataFrame({
        'danger_level_id': ['DL01', 'DL02', 'DL03'],
        'danger_level_code': ['high', 'medium', 'low'],
        'danger_level_name': ['High Danger', 'Medium Danger', 'Low Danger'],
        'xg_multiplier': [1.5, 1.0, 0.5]
    })
    save_table_func(dim_danger, 'dim_danger_level')
    log.info(f"  ✓ dim_danger_level: {len(dim_danger)} rows")

    # fact_rushes
    rushes = events[events['is_rush'] == 1].copy()
    rushes['rush_key'] = 'RU' + rushes['game_id'].astype(str) + rushes.index.astype(str).str.zfill(4)
    rushes['rush_outcome'] = np.where(rushes['is_goal'] == 1, 'goal',
                                      np.where(rushes['is_sog'] == 1, 'shot',
                                              np.where(rushes['is_zone_entry'] == 1, 'zone_entry', 'other')))

    # Add event_player_ids and opp_player_ids lists
    event_players_path = output_dir / 'fact_event_players.csv'
    dim_player_path = output_dir / 'dim_player.csv'
    player_name_map = {}
    player_rating_map = {}

    if dim_player_path.exists():
        try:
            dim_player_df = pd.read_csv(dim_player_path, low_memory=False)
            if 'player_id' in dim_player_df.columns:
                if 'player_full_name' in dim_player_df.columns:
                    player_name_map = dict(zip(dim_player_df['player_id'], dim_player_df['player_full_name']))
                elif 'player_name' in dim_player_df.columns:
                    player_name_map = dict(zip(dim_player_df['player_id'], dim_player_df['player_name']))
                if 'player_rating' in dim_player_df.columns:
                    player_rating_map = dict(zip(dim_player_df['player_id'], dim_player_df['player_rating']))
        except Exception as e:
            log.warn(f"  Could not load dim_player for name/rating lookup: {e}")

    if event_players_path.exists():
        event_players_df = pd.read_csv(event_players_path, low_memory=False)
        rushes = _add_player_ids_to_events(rushes, event_players_df, player_name_map, player_rating_map)
    else:
        log.warn("  fact_event_players.csv not found - cannot build player ID lists")
        rushes['event_player_ids'] = None
        rushes['event_supporting_player_ids'] = None
        rushes['opp_player_ids'] = None
        rushes['opp_supporting_player_ids'] = None
        rushes['opp_player_1_id'] = None
        rushes['opp_player_1_name'] = None
        rushes['opp_player_1_rating'] = None

    save_table_func(rushes, 'fact_rushes')
    log.info(f"  ✓ fact_rushes: {len(rushes)} rows")

    # fact_breakouts
    breakouts = events[events['is_zone_exit'] == 1].copy()
    breakouts['breakout_key'] = 'BO' + breakouts['game_id'].astype(str) + breakouts.index.astype(str).str.zfill(4)
    breakouts['breakout_successful'] = breakouts['event_successful'].apply(
        lambda x: True if x == 's' else (False if x == 'u' else None)
    )
    breakouts, removed_cols = drop_all_null_columns(breakouts)
    if removed_cols:
        log.info(f"  Removed {len(removed_cols)} all-null columns from fact_breakouts: {removed_cols[:10]}{'...' if len(removed_cols) > 10 else ''}")
    save_table_func(breakouts, 'fact_breakouts')
    log.info(f"  ✓ fact_breakouts: {len(breakouts)} rows, {len(breakouts.columns)} columns")

    # fact_zone_entries
    zone_entries = events[events['is_zone_entry'] == 1].copy()
    zone_entries['zone_entry_key'] = 'ZN' + zone_entries['game_id'].astype(str) + zone_entries.index.astype(str).str.zfill(4)
    zone_entries['entry_method'] = zone_entries['event_detail_2'].apply(lambda x: 'rush' if pd.notna(x) and 'Rush' in str(x) else 'dump_in' if pd.notna(x) and 'Dump' in str(x) else 'other')
    save_table_func(zone_entries, 'fact_zone_entries')
    log.info(f"  ✓ fact_zone_entries: {len(zone_entries)} rows")

    # fact_zone_exits
    zone_exits = events[events['is_zone_exit'] == 1].copy()
    zone_exits['zone_exit_key'] = 'ZX' + zone_exits['game_id'].astype(str) + zone_exits.index.astype(str).str.zfill(4)
    zone_exits['exit_method'] = zone_exits['event_detail_2'].apply(lambda x: 'rush' if pd.notna(x) and 'Rush' in str(x) else 'clear' if pd.notna(x) and 'Clear' in str(x) else 'other')
    save_table_func(zone_exits, 'fact_zone_exits')
    log.info(f"  ✓ fact_zone_exits: {len(zone_exits)} rows")

    # fact_scoring_chances_detailed
    sc = events[events['is_scoring_chance'] == 1].copy()
    save_table_func(sc, 'fact_scoring_chances_detailed')
    log.info(f"  ✓ fact_scoring_chances_detailed: {len(sc)} rows")

    # fact_high_danger_chances
    hdc = events[events['is_high_danger'] == 1].copy()
    hdc['high_danger_key'] = 'HD' + hdc['game_id'].astype(str) + hdc.index.astype(str).str.zfill(4)
    save_table_func(hdc, 'fact_high_danger_chances')
    log.info(f"  ✓ fact_high_danger_chances: {len(hdc)} rows")

    # fact_saves
    saves = events[events['is_save'] == 1].copy()
    saves['save_key'] = 'SV' + saves['game_id'].astype(str) + saves.index.astype(str).str.zfill(4)

    if event_players_path.exists():
        saves = _add_goalie_shooter_to_saves(saves, event_players_df, player_name_map, player_rating_map, log)
    else:
        log.warn("  fact_event_players.csv not found - cannot build goalie/shooter columns")
        saves['goalie_player_id'] = None
        saves['goalie_name'] = None
        saves['goalie_rating'] = None
        saves['shooter_player_id'] = None
        saves['shooter_name'] = None
        saves['shooter_rating'] = None

    # Add context columns
    context_cols = [
        'is_cycle', 'cycle_key', 'is_rush', 'is_rush_calculated',
        'is_rebound', 'is_controlled_entry', 'is_carried_entry',
        'is_zone_entry', 'is_zone_exit', 'zone_entry_type_id',
        'time_to_next_sog', 'time_since_last_sog',
        'events_to_next_sog', 'events_since_last_sog',
        'is_pre_shot_event', 'is_shot_assist',
        'play_key', 'sequence_key', 'event_chain_key'
    ]
    for col in context_cols:
        if col not in saves.columns:
            saves[col] = None

    # Calculate time_from_zone_entry for saves
    log.info("  Calculating time_from_zone_entry for saves...")
    saves['time_from_zone_entry'] = None
    events_for_lookup = events.copy()

    for game_id in saves['game_id'].dropna().unique():
        game_events = events_for_lookup[events_for_lookup['game_id'] == game_id].copy()
        game_save_indices = saves[saves['game_id'] == game_id].index

        if len(game_events) == 0 or len(game_save_indices) == 0:
            continue

        game_events = game_events.sort_values('time_start_total_seconds')
        game_events['time_start_total_seconds'] = pd.to_numeric(game_events['time_start_total_seconds'], errors='coerce')
        zone_entries_df = game_events[game_events['is_zone_entry'] == 1].copy()

        for save_idx in game_save_indices:
            save_row = saves.loc[save_idx]
            save_time = pd.to_numeric(save_row.get('time_start_total_seconds'), errors='coerce')

            if pd.isna(save_time):
                continue

            goalie_team_venue = str(save_row.get('team_venue', '')).lower()
            prev_entries = zone_entries_df[
                (zone_entries_df['time_start_total_seconds'] < save_time) &
                (zone_entries_df['time_start_total_seconds'] >= save_time - 60)
            ].sort_values('time_start_total_seconds', ascending=False)

            if len(prev_entries) > 0:
                # Vectorized: filter to valid opposing team entries and take first
                prev_entries_copy = prev_entries.copy()
                prev_entries_copy['team_venue_lower'] = prev_entries_copy['team_venue'].astype(str).str.lower()
                valid_entries = prev_entries_copy[
                    (prev_entries_copy['team_venue_lower'] != goalie_team_venue) &
                    (prev_entries_copy['team_venue_lower'].isin(['home', 'away'])) &
                    (prev_entries_copy['time_start_total_seconds'].notna())
                ]
                if len(valid_entries) > 0:
                    entry_time = valid_entries.iloc[0]['time_start_total_seconds']
                    time_diff = save_time - entry_time
                    if time_diff >= 0:
                        saves.at[save_idx, 'time_from_zone_entry'] = time_diff

    save_table_func(saves, 'fact_saves')
    log.info(f"  ✓ fact_saves: {len(saves)} rows")

    # fact_turnovers_detailed
    turnovers = events[events['is_turnover'] == 1].copy()
    turnovers['turnover_key_new'] = 'TO' + turnovers['game_id'].astype(str) + turnovers.index.astype(str).str.zfill(4)
    save_table_func(turnovers, 'fact_turnovers_detailed')
    log.info(f"  ✓ fact_turnovers_detailed: {len(turnovers)} rows")

    # fact_faceoffs
    faceoffs = events[events['is_faceoff'] == 1].copy()
    faceoffs['faceoff_key'] = 'FO' + faceoffs['game_id'].astype(str) + faceoffs.index.astype(str).str.zfill(4)
    faceoffs['faceoff_type'] = faceoffs['event_detail'].apply(lambda x: 'after_goal' if pd.notna(x) and 'AfterGoal' in str(x) else 'after_stoppage' if pd.notna(x) and 'AfterStoppage' in str(x) else 'other')

    rename_map = {}
    if 'event_player_1_id' in faceoffs.columns:
        rename_map['event_player_1_id'] = 'faceoff_winner_id'
    if 'event_player_1_name' in faceoffs.columns:
        rename_map['event_player_1_name'] = 'faceoff_winner_name'
    if 'event_player_1_rating' in faceoffs.columns:
        rename_map['event_player_1_rating'] = 'faceoff_winner_rating'
    if 'opp_player_1_id' in faceoffs.columns:
        rename_map['opp_player_1_id'] = 'faceoff_loser_id'
    if 'opp_player_1_name' in faceoffs.columns:
        rename_map['opp_player_1_name'] = 'faceoff_loser_name'
    if 'opp_player_1_rating' in faceoffs.columns:
        rename_map['opp_player_1_rating'] = 'faceoff_loser_rating'

    if rename_map:
        faceoffs = faceoffs.rename(columns=rename_map)
        log.info(f"  Renamed {len(rename_map)} player columns for faceoffs")

    faceoffs, removed_cols = drop_all_null_columns(faceoffs)
    if removed_cols:
        log.info(f"  Removed {len(removed_cols)} all-null columns from fact_faceoffs: {removed_cols[:10]}{'...' if len(removed_cols) > 10 else ''}")

    save_table_func(faceoffs, 'fact_faceoffs')
    log.info(f"  ✓ fact_faceoffs: {len(faceoffs)} rows, {len(faceoffs.columns)} columns")

    # fact_penalties
    penalties = events[events['is_penalty'] == 1].copy()
    penalties['penalty_key'] = 'PN' + penalties['game_id'].astype(str) + penalties.index.astype(str).str.zfill(4)
    save_table_func(penalties, 'fact_penalties')
    log.info(f"  ✓ fact_penalties: {len(penalties)} rows")


def _add_player_ids_to_events(df, event_players_df, player_name_map, player_rating_map):
    """Add player ID lists to an events dataframe."""
    event_player_lists = {}
    event_supporting_lists = {}
    opp_player_lists = {}
    opp_supporting_lists = {}
    opp_player_1_ids = {}
    opp_player_1_names = {}
    opp_player_1_ratings = {}

    event_ids = set(df['event_id'].dropna().unique())

    for event_id in event_ids:
        ep_for_event = event_players_df[event_players_df['event_id'] == event_id]

        if len(ep_for_event) == 0:
            event_player_lists[event_id] = None
            event_supporting_lists[event_id] = None
            opp_player_lists[event_id] = None
            opp_supporting_lists[event_id] = None
            opp_player_1_ids[event_id] = None
            opp_player_1_names[event_id] = None
            opp_player_1_ratings[event_id] = None
            continue

        ep_roles = ep_for_event[
            ep_for_event['player_role'].astype(str).str.lower().str.startswith('event_player')
        ]
        opp_roles = ep_for_event[
            ep_for_event['player_role'].astype(str).str.lower().str.startswith('opp_player')
        ]

        event_player_ids = []
        event_supporting_ids = []

        ep1 = ep_roles[ep_roles['player_role'].astype(str).str.lower() == 'event_player_1']
        if len(ep1) > 0 and pd.notna(ep1.iloc[0].get('player_id')):
            ep1_id = str(ep1.iloc[0]['player_id'])
            if ep1_id not in ['nan', 'None', '']:
                event_player_ids.append(ep1_id)

        for role_num in range(2, 7):
            ep_role = ep_roles[ep_roles['player_role'].astype(str).str.lower() == f'event_player_{role_num}']
            if len(ep_role) > 0 and pd.notna(ep_role.iloc[0].get('player_id')):
                pid = str(ep_role.iloc[0]['player_id'])
                if pid not in ['nan', 'None', '']:
                    if pid not in event_player_ids:
                        event_player_ids.append(pid)
                    if pid not in event_supporting_ids:
                        event_supporting_ids.append(pid)

        opp_player_ids_list = []
        opp_supporting_ids_list = []
        op1_id = None
        op1_name = None
        op1_rating = None

        op1 = opp_roles[opp_roles['player_role'].astype(str).str.lower() == 'opp_player_1']
        if len(op1) > 0 and pd.notna(op1.iloc[0].get('player_id')):
            op1_id = str(op1.iloc[0]['player_id'])
            if op1_id not in ['nan', 'None', '']:
                opp_player_ids_list.append(op1_id)
                op1_row = op1.iloc[0]
                if 'player_name' in op1_row.index and pd.notna(op1_row.get('player_name')):
                    op1_name = str(op1_row['player_name'])
                elif 'player_full_name' in op1_row.index and pd.notna(op1_row.get('player_full_name')):
                    op1_name = str(op1_row['player_full_name'])
                else:
                    op1_name = player_name_map.get(op1_id, None)
                if 'player_rating' in op1_row.index and pd.notna(op1_row.get('player_rating')):
                    try:
                        op1_rating = float(op1_row['player_rating'])
                    except (ValueError, TypeError):
                        op1_rating = None
                else:
                    op1_rating = player_rating_map.get(op1_id, None)
                    if op1_rating is not None:
                        try:
                            op1_rating = float(op1_rating)
                        except (ValueError, TypeError):
                            op1_rating = None

        for role_num in range(2, 7):
            opp_role = opp_roles[opp_roles['player_role'].astype(str).str.lower() == f'opp_player_{role_num}']
            if len(opp_role) > 0 and pd.notna(opp_role.iloc[0].get('player_id')):
                pid = str(opp_role.iloc[0]['player_id'])
                if pid not in ['nan', 'None', '']:
                    if pid not in opp_player_ids_list:
                        opp_player_ids_list.append(pid)
                    if pid not in opp_supporting_ids_list:
                        opp_supporting_ids_list.append(pid)

        event_player_lists[event_id] = ','.join(event_player_ids) if event_player_ids else None
        event_supporting_lists[event_id] = ','.join(event_supporting_ids) if event_supporting_ids else None
        opp_player_lists[event_id] = ','.join(opp_player_ids_list) if opp_player_ids_list else None
        opp_supporting_lists[event_id] = ','.join(opp_supporting_ids_list) if opp_supporting_ids_list else None
        opp_player_1_ids[event_id] = op1_id
        opp_player_1_names[event_id] = op1_name
        opp_player_1_ratings[event_id] = op1_rating

    df['event_player_ids'] = df['event_id'].map(event_player_lists)
    df['event_supporting_player_ids'] = df['event_id'].map(event_supporting_lists)
    df['opp_player_ids'] = df['event_id'].map(opp_player_lists)
    df['opp_supporting_player_ids'] = df['event_id'].map(opp_supporting_lists)
    df['opp_player_1_id'] = df['event_id'].map(opp_player_1_ids)
    df['opp_player_1_name'] = df['event_id'].map(opp_player_1_names)
    df['opp_player_1_rating'] = df['event_id'].map(opp_player_1_ratings)

    return df


def _add_goalie_shooter_to_saves(saves, event_players_df, player_name_map, player_rating_map, log):
    """Add goalie and shooter columns to saves dataframe."""
    goalie_ids = {}
    goalie_names = {}
    goalie_ratings = {}
    shooter_ids = {}
    shooter_names = {}
    shooter_ratings = {}

    save_event_ids = set(saves['event_id'].dropna().unique())

    for event_id in save_event_ids:
        ep_for_event = event_players_df[event_players_df['event_id'] == event_id]

        if len(ep_for_event) == 0:
            goalie_ids[event_id] = None
            goalie_names[event_id] = None
            goalie_ratings[event_id] = None
            shooter_ids[event_id] = None
            shooter_names[event_id] = None
            shooter_ratings[event_id] = None
            continue

        # Goalie (event_player_1)
        ep1 = ep_for_event[ep_for_event['player_role'].astype(str).str.lower() == 'event_player_1']
        goalie_id = None
        goalie_name = None
        goalie_rating = None

        if len(ep1) > 0 and pd.notna(ep1.iloc[0].get('player_id')):
            goalie_id = str(ep1.iloc[0]['player_id'])
            if goalie_id not in ['nan', 'None', '']:
                ep1_row = ep1.iloc[0]
                if 'player_name' in ep1_row.index and pd.notna(ep1_row.get('player_name')):
                    goalie_name = str(ep1_row['player_name'])
                elif 'player_full_name' in ep1_row.index and pd.notna(ep1_row.get('player_full_name')):
                    goalie_name = str(ep1_row['player_full_name'])
                else:
                    goalie_name = player_name_map.get(goalie_id, None)
                if 'player_rating' in ep1_row.index and pd.notna(ep1_row.get('player_rating')):
                    try:
                        goalie_rating = float(ep1_row['player_rating'])
                    except (ValueError, TypeError):
                        goalie_rating = None
                else:
                    goalie_rating = player_rating_map.get(goalie_id, None)
                    if goalie_rating is not None:
                        try:
                            goalie_rating = float(goalie_rating)
                        except (ValueError, TypeError):
                            goalie_rating = None

        # Shooter (opp_player_1)
        op1 = ep_for_event[ep_for_event['player_role'].astype(str).str.lower() == 'opp_player_1']
        shooter_id = None
        shooter_name = None
        shooter_rating = None

        if len(op1) > 0 and pd.notna(op1.iloc[0].get('player_id')):
            shooter_id = str(op1.iloc[0]['player_id'])
            if shooter_id not in ['nan', 'None', '']:
                op1_row = op1.iloc[0]
                if 'player_name' in op1_row.index and pd.notna(op1_row.get('player_name')):
                    shooter_name = str(op1_row['player_name'])
                elif 'player_full_name' in op1_row.index and pd.notna(op1_row.get('player_full_name')):
                    shooter_name = str(op1_row['player_full_name'])
                else:
                    shooter_name = player_name_map.get(shooter_id, None)
                if 'player_rating' in op1_row.index and pd.notna(op1_row.get('player_rating')):
                    try:
                        shooter_rating = float(op1_row['player_rating'])
                    except (ValueError, TypeError):
                        shooter_rating = None
                else:
                    shooter_rating = player_rating_map.get(shooter_id, None)
                    if shooter_rating is not None:
                        try:
                            shooter_rating = float(shooter_rating)
                        except (ValueError, TypeError):
                            shooter_rating = None

        goalie_ids[event_id] = goalie_id
        goalie_names[event_id] = goalie_name
        goalie_ratings[event_id] = goalie_rating
        shooter_ids[event_id] = shooter_id
        shooter_names[event_id] = shooter_name
        shooter_ratings[event_id] = shooter_rating

    saves['goalie_player_id'] = saves['event_id'].map(goalie_ids)
    saves['goalie_name'] = saves['event_id'].map(goalie_names)
    saves['goalie_rating'] = saves['event_id'].map(goalie_ratings)
    saves['shooter_player_id'] = saves['event_id'].map(shooter_ids)
    saves['shooter_name'] = saves['event_id'].map(shooter_names)
    saves['shooter_rating'] = saves['event_id'].map(shooter_ratings)

    return saves
