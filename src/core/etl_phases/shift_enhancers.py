"""
Shift Enhancement Module
========================

Contains functions for enhancing shift tables with derived columns and stats.

Functions:
- enhance_shift_tables: Add player IDs, plus/minus, and shift stats
- enhance_shift_players: Expand fact_shift_players with comprehensive stats
- update_roster_positions_from_shifts: Update positions based on shift data
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Import table writer for saving
from src.core.table_writer import save_output_table

# Import utilities
from .utilities import drop_all_null_columns


def enhance_shift_tables(output_dir: Path, log, save_table_func=None):
    """Comprehensive shift enhancement with player IDs, plus/minus, and shift stats.

    Args:
        output_dir: Path to output directory
        log: ETLLogger instance
        save_table_func: Function to save tables (optional, uses save_output_table if not provided)
    """
    log.section("PHASE 5.11: COMPREHENSIVE SHIFT ENHANCEMENT")

    if save_table_func is None:
        save_table_func = lambda df, name: save_output_table(df, name, output_dir)

    shifts_path = output_dir / 'fact_shifts.csv'
    events_path = output_dir / 'fact_events.csv'
    roster_path = output_dir / 'fact_gameroster.csv'

    if not shifts_path.exists():
        log.warn("fact_shifts not found, skipping")
        return

    shifts = pd.read_csv(shifts_path, low_memory=False)
    events = pd.read_csv(events_path, low_memory=False)
    roster = pd.read_csv(roster_path, low_memory=False)
    dim_team = pd.read_csv(output_dir / 'dim_team.csv', low_memory=False)
    dim_schedule = pd.read_csv(output_dir / 'dim_schedule.csv', low_memory=False)
    dim_player = pd.read_csv(output_dir / 'dim_player.csv', low_memory=False)

    log.info(f"Enhancing {len(shifts)} shifts...")

    # Fix EN convention (#177): strength/situation should indicate who HAS empty net
    # The EN flags are correct (based on goalie presence), but strength/situation labels are backwards
    if 'home_team_en' in shifts.columns and 'away_team_en' in shifts.columns:
        home_en_mask = shifts['home_team_en'] == 1
        away_en_mask = shifts['away_team_en'] == 1

        # Correct strength: ENH = home has empty net, ENA = away has empty net
        shifts.loc[home_en_mask, 'strength'] = 'ENH'
        shifts.loc[away_en_mask, 'strength'] = 'ENA'

        # Correct situation: home_en = home has empty net, away_en = away has empty net
        shifts.loc[home_en_mask, 'situation'] = 'home_en'
        shifts.loc[away_en_mask, 'situation'] = 'away_en'

        en_corrected = home_en_mask.sum() + away_en_mask.sum()
        if en_corrected > 0:
            log.info(f"  Corrected {en_corrected} EN shift labels (strength/situation)")

    # Calculate total seconds for shifts (from period start, counting down)
    shifts['shift_start_total_seconds'] = shifts['shift_start_min'].fillna(0) * 60 + shifts['shift_start_sec'].fillna(0)
    shifts['shift_end_total_seconds'] = shifts['shift_end_min'].fillna(0) * 60 + shifts['shift_end_sec'].fillna(0)
    shifts['shift_duration'] = shifts['shift_start_total_seconds'] - shifts['shift_end_total_seconds']

    # Prep events
    events['event_total_seconds'] = events['event_start_min'] * 60 + events['event_start_sec']

    # Build lookups - VECTORIZED
    roster_sorted = roster.sort_values('game_id')
    player_team_map = dict(zip(roster_sorted['player_id'], roster_sorted['team_name']))

    # roster_lookup: (game_id, team_name, jersey) -> player_id
    roster_lookup = dict(zip(
        zip(roster['game_id'], roster['team_name'], roster['player_game_number'].astype(str)),
        roster['player_id']
    ))

    # VECTORIZED: Add event_team to events
    if len(events) > 0 and 'event_player_ids' in events.columns:
        events['first_player'] = events['event_player_ids'].astype(str).str.split(',').str[0].str.strip()
        events['event_team'] = events['first_player'].map(player_team_map)
        events['is_home_event'] = events['event_team'] == events['home_team']
        events.drop(columns=['first_player'], inplace=True, errors='ignore')

    # Build shift-events mapping
    def get_shift_events(shift_row, all_events):
        game_id = shift_row['game_id']
        period = shift_row['period']
        start_sec = shift_row['shift_start_total_seconds']
        end_sec = shift_row['shift_end_total_seconds']
        if pd.isna(period) or pd.isna(start_sec) or pd.isna(end_sec):
            return pd.DataFrame()
        mask = (all_events['game_id'] == game_id) & \
               (all_events['period'] == period) & \
               (all_events['event_total_seconds'] <= start_sec) & \
               (all_events['event_total_seconds'] >= end_sec)
        return all_events[mask]

    # VECTORIZED: Build shift-events mapping more efficiently
    if len(events) > 0 and len(shifts) > 0:
        events_for_merge = events[['event_id', 'game_id', 'period', 'event_total_seconds']].copy()
        shifts_for_merge = shifts[['shift_id', 'game_id', 'period', 'shift_start_total_seconds',
                                   'shift_end_total_seconds']].copy()
        shifts_for_merge = shifts_for_merge[
            shifts_for_merge['shift_start_total_seconds'].notna() &
            shifts_for_merge['shift_end_total_seconds'].notna()
        ]

        events_shifts = events_for_merge.merge(
            shifts_for_merge,
            on=['game_id', 'period'],
            how='inner'
        )

        time_mask = (
            (events_shifts['event_total_seconds'] <= events_shifts['shift_start_total_seconds']) &
            (events_shifts['event_total_seconds'] >= events_shifts['shift_end_total_seconds'])
        )
        events_in_shifts = events_shifts[time_mask]

        shift_events_map = {}
        for shift_id, group in events_in_shifts.groupby('shift_id'):
            event_ids = group['event_id'].tolist()
            shift_events_map[shift_id] = events[events['event_id'].isin(event_ids)]
    else:
        shift_events_map = {}

    # 1. Basic FKs
    shifts['period_id'] = 'P' + shifts['period'].fillna(0).astype(int).astype(str).str.zfill(2)
    team_name_to_id = dict(zip(dim_team['team_name'], dim_team['team_id']))
    shifts['home_team_id'] = shifts['home_team'].map(team_name_to_id)
    shifts['away_team_id'] = shifts['away_team'].map(team_name_to_id)
    game_to_season = dict(zip(dim_schedule['game_id'], dim_schedule['season_id']))
    shifts['season_id'] = shifts['game_id'].map(game_to_season)

    def get_time_bucket(row):
        period = row['period']
        start_min = row['shift_start_min']
        if pd.isna(period) or pd.isna(start_min):
            return None
        if period > 3:
            return 'TB06'
        if start_min >= 15:
            return 'TB01'
        elif start_min >= 10:
            return 'TB02'
        elif start_min >= 5:
            return 'TB03'
        elif start_min >= 2:
            return 'TB04'
        else:
            return 'TB05'
    shifts['time_bucket_id'] = shifts.apply(get_time_bucket, axis=1)

    def map_strength_id(strength_str):
        if pd.isna(strength_str):
            return None
        strength_str = str(strength_str).split()[0]
        if 'v' in strength_str:
            parts = strength_str.split('v')
            try:
                home, away = int(parts[0]), int(parts[1])
                strength_map = {
                    (5, 5): 'STR0001', (5, 4): 'STR0002', (5, 3): 'STR0003',
                    (4, 5): 'STR0004', (3, 5): 'STR0005', (4, 4): 'STR0006',
                    (3, 3): 'STR0007', (4, 3): 'STR0008', (3, 4): 'STR0009',
                    (6, 5): 'STR0010', (5, 6): 'STR0011', (6, 4): 'STR0012',
                    (4, 6): 'STR0013', (0, 0): 'STR0016', (6, 6): 'STR0017',
                }
                return strength_map.get((home, away), None)
            except Exception:
                return None
        return None
    shifts['strength_id'] = shifts['strength'].apply(map_strength_id)

    # 2. Derive shift start/stop types
    def derive_start_type(shift_events_df, current_type):
        if pd.notna(current_type):
            return current_type
        if shift_events_df.empty:
            return 'OnTheFly'
        first_event = shift_events_df.iloc[-1]
        if first_event['is_faceoff'] == 1:
            detail = str(first_event['event_detail'])
            if 'AfterGoal' in detail:
                return 'FaceoffAfterGoal'
            elif 'AfterStoppage' in detail:
                return 'OtherFaceoff'
            elif 'GameStart' in detail:
                return 'GameStart'
            else:
                return 'OtherFaceoff'
        return 'OnTheFly'

    def derive_stop_type(shift_events_df, current_type):
        if pd.notna(current_type):
            return current_type
        if shift_events_df.empty:
            return 'OnTheFly'
        last_event = shift_events_df.iloc[0]
        if last_event['is_goal'] == 1:
            return 'Goal'
        elif last_event['is_penalty'] == 1:
            return 'Penalty'
        elif 'Stoppage' in str(last_event['event_type']):
            return 'Stoppage'
        return 'OnTheFly'

    empty_events_df = pd.DataFrame()
    shifts['shift_start_type_derived'] = [
        derive_start_type(shift_events_map.get(sid, empty_events_df), shifts.loc[i, 'shift_start_type'])
        for i, sid in enumerate(shifts['shift_id'])
    ]
    shifts['shift_stop_type_derived'] = [
        derive_stop_type(shift_events_map.get(sid, empty_events_df), shifts.loc[i, 'shift_stop_type'])
        for i, sid in enumerate(shifts['shift_id'])
    ]

    # 3. Derive zones
    def get_start_end_zones(shift_events_df):
        if shift_events_df.empty:
            return None, None
        first_zone = shift_events_df.iloc[-1]['event_team_zone']
        last_zone = shift_events_df.iloc[0]['event_team_zone']
        return first_zone, last_zone

    zones_data = [get_start_end_zones(shift_events_map.get(sid, empty_events_df)) for sid in shifts['shift_id']]
    shifts['start_zone'] = [z[0] for z in zones_data]
    shifts['end_zone'] = [z[1] for z in zones_data]

    zone_map = {
        'Offensive': 'ZN01', 'offensive': 'ZN01', 'O': 'ZN01', 'o': 'ZN01',
        'Defensive': 'ZN02', 'defensive': 'ZN02', 'D': 'ZN02', 'd': 'ZN02',
        'Neutral': 'ZN03', 'neutral': 'ZN03', 'N': 'ZN03', 'n': 'ZN03',
    }
    shifts['start_zone_id'] = shifts['start_zone'].map(zone_map)
    shifts['end_zone_id'] = shifts['end_zone'].map(zone_map)

    # 4. Add player IDs
    player_slots = [
        ('home', 'forward_1'), ('home', 'forward_2'), ('home', 'forward_3'),
        ('home', 'defense_1'), ('home', 'defense_2'), ('home', 'xtra'), ('home', 'goalie'),
        ('away', 'forward_1'), ('away', 'forward_2'), ('away', 'forward_3'),
        ('away', 'defense_1'), ('away', 'defense_2'), ('away', 'xtra'), ('away', 'goalie'),
    ]

    for venue, slot in player_slots:
        col_name = f'{venue}_{slot}'
        id_col = f'{col_name}_id'
        team_col = f'{venue}_team'

        # Convert jersey numbers to clean strings (27.0 -> '27') for lookup
        jersey_str = shifts[col_name].fillna('').astype(str).str.replace(r'\.0$', '', regex=True)
        shifts['_lookup_key_team'] = list(zip(
            shifts['game_id'],
            shifts[team_col].fillna(''),
            jersey_str
        ))
        shifts[id_col] = shifts['_lookup_key_team'].map(roster_lookup)
        shifts.drop(columns=['_lookup_key_team'], inplace=True, errors='ignore')

    # 4.5 Add team ratings
    log.info("  Adding team ratings (excluding goalies)...")

    player_rating_map = dict(zip(dim_player['player_id'], dim_player['current_skill_rating']))

    home_skater_cols = ['home_forward_1_id', 'home_forward_2_id', 'home_forward_3_id',
                        'home_defense_1_id', 'home_defense_2_id']
    away_skater_cols = ['away_forward_1_id', 'away_forward_2_id', 'away_forward_3_id',
                        'away_defense_1_id', 'away_defense_2_id']

    for col in home_skater_cols + away_skater_cols:
        if col in shifts.columns:
            shifts[f'{col}_rating'] = shifts[col].map(player_rating_map)

    home_rating_cols = [f'{col}_rating' for col in home_skater_cols]
    home_ratings_df = shifts[home_rating_cols].copy()

    shifts['home_avg_rating'] = home_ratings_df.mean(axis=1, skipna=True).round(2)
    shifts['home_min_rating'] = home_ratings_df.min(axis=1, skipna=True)
    shifts['home_max_rating'] = home_ratings_df.max(axis=1, skipna=True)

    away_rating_cols = [f'{col}_rating' for col in away_skater_cols]
    away_ratings_df = shifts[away_rating_cols].copy()

    shifts['away_avg_rating'] = away_ratings_df.mean(axis=1, skipna=True).round(2)
    shifts['away_min_rating'] = away_ratings_df.min(axis=1, skipna=True)
    shifts['away_max_rating'] = away_ratings_df.max(axis=1, skipna=True)

    # Clean up temporary rating columns
    temp_rating_cols = home_rating_cols + away_rating_cols
    for col in temp_rating_cols:
        if col in shifts.columns:
            shifts.drop(columns=[col], inplace=True)

    shifts['rating_differential'] = shifts['home_avg_rating'] - shifts['away_avg_rating']
    shifts['home_rating_advantage'] = shifts['rating_differential'] > 0

    home_avg = shifts['home_avg_rating'].mean()
    away_avg = shifts['away_avg_rating'].mean()
    log.info(f"  Team ratings: home_avg={home_avg:.2f}, away_avg={away_avg:.2f}, differential={home_avg-away_avg:.2f}")

    # 5. Plus/minus
    actual_goals = events[(events['event_type'] == 'Goal') & (events['event_detail'] == 'Goal_Scored')].copy()

    if len(actual_goals) > 0:
        actual_goals['first_player'] = actual_goals['event_player_ids'].astype(str).str.split(',').str[0].str.strip()
        actual_goals['scoring_team'] = actual_goals['first_player'].map(player_team_map)
        actual_goals['is_home_goal'] = actual_goals['scoring_team'] == actual_goals['home_team']

    pm_types = ['all', 'ev', 'nen', 'pp', 'pk']
    for pm_type in pm_types:
        for venue in ['home', 'away']:
            shifts[f'{venue}_gf_{pm_type}'] = 0
            shifts[f'{venue}_ga_{pm_type}'] = 0

    def get_shift_goals(shift_row, goals_df):
        game_id = shift_row['game_id']
        period = shift_row['period']
        start_sec = shift_row['shift_start_total_seconds']
        end_sec = shift_row['shift_end_total_seconds']
        if pd.isna(period) or pd.isna(start_sec) or pd.isna(end_sec):
            return pd.DataFrame()
        mask = (goals_df['game_id'] == game_id) & \
               (goals_df['period'] == period) & \
               (goals_df['event_total_seconds'] <= start_sec) & \
               (goals_df['event_total_seconds'] > end_sec)
        return goals_df[mask]

    for i, shift in shifts.iterrows():
        shift_goals = get_shift_goals(shift, actual_goals)
        if shift_goals.empty:
            continue
        is_ev = str(shift.get('strength', '')) == '5v5'
        is_nen = (shift.get('home_team_en', 0) == 0) and (shift.get('away_team_en', 0) == 0)

        for _, goal in shift_goals.iterrows():
            is_home_goal = goal['is_home_goal']

            goal_strength = str(goal.get('strength', '')).lower()
            goal_is_ev = goal_strength in ['5v5', '4v4', '3v3']
            goal_is_pp_home = goal_strength in ['5v4', '5v3', '4v3']
            goal_is_pk_home = goal_strength in ['4v5', '3v5', '3v4']

            if is_home_goal:
                shifts.at[i, 'home_gf_all'] += 1
                shifts.at[i, 'away_ga_all'] += 1
            else:
                shifts.at[i, 'away_gf_all'] += 1
                shifts.at[i, 'home_ga_all'] += 1

            if goal_is_ev:
                if is_home_goal:
                    shifts.at[i, 'home_gf_ev'] += 1
                    shifts.at[i, 'away_ga_ev'] += 1
                else:
                    shifts.at[i, 'away_gf_ev'] += 1
                    shifts.at[i, 'home_ga_ev'] += 1

            if is_nen:
                if is_home_goal:
                    shifts.at[i, 'home_gf_nen'] += 1
                    shifts.at[i, 'away_ga_nen'] += 1
                else:
                    shifts.at[i, 'away_gf_nen'] += 1
                    shifts.at[i, 'home_ga_nen'] += 1

            if goal_is_pp_home:
                if is_home_goal:
                    shifts.at[i, 'home_gf_pp'] += 1
                    shifts.at[i, 'away_ga_pk'] += 1
                else:
                    shifts.at[i, 'away_gf_pk'] += 1
                    shifts.at[i, 'home_ga_pp'] += 1
            elif goal_is_pk_home:
                if is_home_goal:
                    shifts.at[i, 'home_gf_pk'] += 1
                    shifts.at[i, 'away_ga_pp'] += 1
                else:
                    shifts.at[i, 'away_gf_pp'] += 1
                    shifts.at[i, 'home_ga_pk'] += 1

    for pm_type in pm_types:
        shifts[f'home_pm_{pm_type}'] = shifts[f'home_gf_{pm_type}'] - shifts[f'home_ga_{pm_type}']
        shifts[f'away_pm_{pm_type}'] = shifts[f'away_gf_{pm_type}'] - shifts[f'away_ga_{pm_type}']

    # 5b. Game state tracking
    log.info("  Calculating game state (leading/trailing/tied)...")
    shifts['game_state'] = 'tied'
    shifts['score_differential'] = 0

    for game_id in shifts['game_id'].unique():
        game_shifts = shifts[shifts['game_id'] == game_id].copy()
        # Sort goals DESCENDING by event_total_seconds (countdown format: higher = earlier in period)
        game_goals = actual_goals[actual_goals['game_id'] == game_id].sort_values('event_total_seconds', ascending=False)

        if len(game_goals) == 0:
            continue

        home_score = 0
        away_score = 0
        goal_scores = []

        # Build cumulative scores in chronological order (earliest goals first)
        for _, goal in game_goals.iterrows():
            if goal['is_home_goal']:
                home_score += 1
            else:
                away_score += 1
            goal_scores.append((goal['event_total_seconds'], home_score, away_score))

        for idx in game_shifts.index:
            shift_start = shifts.at[idx, 'shift_start_total_seconds']
            if pd.isna(shift_start):
                continue

            h_score, a_score = 0, 0
            # Countdown format: goal happened before shift if goal_time > shift_start
            # (higher clock value = earlier in period)
            for goal_time, h, a in goal_scores:
                if goal_time > shift_start:
                    h_score, a_score = h, a
                else:
                    break

            diff = h_score - a_score
            shifts.at[idx, 'score_differential'] = diff

            if diff > 0:
                shifts.at[idx, 'game_state'] = 'home_leading'
            elif diff < 0:
                shifts.at[idx, 'game_state'] = 'home_trailing'
            else:
                shifts.at[idx, 'game_state'] = 'tied'

    shifts['is_close_game'] = shifts['score_differential'].abs() <= 1

    log.info(f"  Game states: tied={len(shifts[shifts['game_state']=='tied'])}, home_leading={len(shifts[shifts['game_state']=='home_leading'])}, home_trailing={len(shifts[shifts['game_state']=='home_trailing'])}")

    # 6. Shift stats
    stat_cols = ['sf', 'sa', 'shot_diff', 'cf', 'ca', 'cf_pct', 'ff', 'fa', 'ff_pct',
                 'scf', 'sca', 'hdf', 'hda',
                 'home_zone_entries', 'away_zone_entries', 'home_zone_exits', 'away_zone_exits',
                 'home_giveaways', 'away_giveaways', 'home_bad_giveaways', 'away_bad_giveaways',
                 'home_takeaways', 'away_takeaways',
                 'home_fo_won', 'away_fo_won', 'event_count']
    for col in stat_cols:
        shifts[col] = 0 if col not in ['cf_pct', 'ff_pct'] else 0.0

    # VECTORIZED: Aggregate shift stats using groupby
    if len(shift_events_map) > 0:
        all_shift_events = []
        for shift_id, shift_ev in shift_events_map.items():
            if not shift_ev.empty:
                shift_ev_copy = shift_ev.copy()
                shift_ev_copy['_shift_id'] = shift_id
                all_shift_events.append(shift_ev_copy)

        if all_shift_events:
            combined_events = pd.concat(all_shift_events, ignore_index=True)

            def agg_shift_stats(events_df, shift_ids):
                """Aggregate stats for shifts using vectorized operations."""
                stats = {}

                event_counts = events_df.groupby('_shift_id').size()
                stats['event_count'] = shift_ids.map(event_counts).fillna(0)

                sog_events = events_df[events_df['is_sog'] == 1] if 'is_sog' in events_df.columns else pd.DataFrame()
                if len(sog_events) > 0:
                    home_sog = sog_events[sog_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['sf'] = shift_ids.map(home_sog).fillna(0)
                    total_sog = sog_events.groupby('_shift_id').size()
                    stats['sa'] = (shift_ids.map(total_sog).fillna(0) - stats['sf']).fillna(0)
                    stats['shot_diff'] = stats['sf'] - stats['sa']

                corsi_events = events_df[events_df['is_corsi'] == 1] if 'is_corsi' in events_df.columns else pd.DataFrame()
                if len(corsi_events) > 0:
                    home_corsi = corsi_events[corsi_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['cf'] = shift_ids.map(home_corsi).fillna(0)
                    total_corsi = corsi_events.groupby('_shift_id').size()
                    stats['ca'] = (shift_ids.map(total_corsi).fillna(0) - stats['cf']).fillna(0)
                    total_corsi_sum = stats['cf'] + stats['ca']
                    stats['cf_pct'] = (stats['cf'] / total_corsi_sum * 100).where(total_corsi_sum > 0, 50.0)

                fenwick_events = events_df[events_df['is_fenwick'] == 1] if 'is_fenwick' in events_df.columns else pd.DataFrame()
                if len(fenwick_events) > 0:
                    home_fenwick = fenwick_events[fenwick_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['ff'] = shift_ids.map(home_fenwick).fillna(0)
                    total_fenwick = fenwick_events.groupby('_shift_id').size()
                    stats['fa'] = (shift_ids.map(total_fenwick).fillna(0) - stats['ff']).fillna(0)
                    total_fenwick_sum = stats['ff'] + stats['fa']
                    stats['ff_pct'] = (stats['ff'] / total_fenwick_sum * 100).where(total_fenwick_sum > 0, 50.0)

                sc_events = events_df[events_df['is_scoring_chance'] == 1] if 'is_scoring_chance' in events_df.columns else pd.DataFrame()
                if len(sc_events) > 0:
                    home_sc = sc_events[sc_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['scf'] = shift_ids.map(home_sc).fillna(0)
                    total_sc = sc_events.groupby('_shift_id').size()
                    stats['sca'] = (shift_ids.map(total_sc).fillna(0) - stats['scf']).fillna(0)

                hd_events = events_df[events_df['is_high_danger'] == 1] if 'is_high_danger' in events_df.columns else pd.DataFrame()
                if len(hd_events) > 0:
                    home_hd = hd_events[hd_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['hdf'] = shift_ids.map(home_hd).fillna(0)
                    total_hd = hd_events.groupby('_shift_id').size()
                    stats['hda'] = (shift_ids.map(total_hd).fillna(0) - stats['hdf']).fillna(0)

                ze_events = events_df[events_df['is_zone_entry'] == 1] if 'is_zone_entry' in events_df.columns else pd.DataFrame()
                if len(ze_events) > 0:
                    home_ze = ze_events[ze_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['home_zone_entries'] = shift_ids.map(home_ze).fillna(0)
                    total_ze = ze_events.groupby('_shift_id').size()
                    stats['away_zone_entries'] = (shift_ids.map(total_ze).fillna(0) - stats['home_zone_entries']).fillna(0)

                zx_events = events_df[events_df['is_zone_exit'] == 1] if 'is_zone_exit' in events_df.columns else pd.DataFrame()
                if len(zx_events) > 0:
                    home_zx = zx_events[zx_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['home_zone_exits'] = shift_ids.map(home_zx).fillna(0)
                    total_zx = zx_events.groupby('_shift_id').size()
                    stats['away_zone_exits'] = (shift_ids.map(total_zx).fillna(0) - stats['home_zone_exits']).fillna(0)

                ga_events = events_df[events_df['is_giveaway'] == 1] if 'is_giveaway' in events_df.columns else pd.DataFrame()
                if len(ga_events) > 0:
                    home_ga = ga_events[ga_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['home_giveaways'] = shift_ids.map(home_ga).fillna(0)
                    total_ga = ga_events.groupby('_shift_id').size()
                    stats['away_giveaways'] = (shift_ids.map(total_ga).fillna(0) - stats['home_giveaways']).fillna(0)

                bad_ga_events = events_df[events_df['is_bad_giveaway'] == 1] if 'is_bad_giveaway' in events_df.columns else pd.DataFrame()
                if len(bad_ga_events) > 0:
                    home_bad_ga = bad_ga_events[bad_ga_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['home_bad_giveaways'] = shift_ids.map(home_bad_ga).fillna(0)
                    total_bad_ga = bad_ga_events.groupby('_shift_id').size()
                    stats['away_bad_giveaways'] = (shift_ids.map(total_bad_ga).fillna(0) - stats['home_bad_giveaways']).fillna(0)

                ta_events = events_df[events_df['is_takeaway'] == 1] if 'is_takeaway' in events_df.columns else pd.DataFrame()
                if len(ta_events) > 0:
                    home_ta = ta_events[ta_events['is_home_event'] == 1].groupby('_shift_id').size()
                    stats['home_takeaways'] = shift_ids.map(home_ta).fillna(0)
                    total_ta = ta_events.groupby('_shift_id').size()
                    stats['away_takeaways'] = (shift_ids.map(total_ta).fillna(0) - stats['home_takeaways']).fillna(0)

                fo_events = events_df[events_df['is_faceoff'] == 1] if 'is_faceoff' in events_df.columns else pd.DataFrame()
                if len(fo_events) > 0 and 'player_team' in fo_events.columns and 'home_team' in fo_events.columns:
                    home_fo_wins = fo_events[fo_events['player_team'] == fo_events['home_team']].groupby('_shift_id').size()
                    stats['home_fo_won'] = shift_ids.map(home_fo_wins).fillna(0)
                    total_fo = fo_events.groupby('_shift_id').size()
                    stats['away_fo_won'] = (shift_ids.map(total_fo).fillna(0) - stats['home_fo_won']).fillna(0)

                return stats

            shift_ids = shifts['shift_id']
            aggregated_stats = agg_shift_stats(combined_events, shift_ids)

            for col, values in aggregated_stats.items():
                shifts[col] = values

    # 7. Create dim tables
    start_types = shifts['shift_start_type_derived'].dropna().unique()
    dim_shift_start_type = pd.DataFrame({
        'shift_start_type_id': [f'SST{i:04d}' for i in range(1, len(start_types)+1)],
        'shift_start_type_name': start_types
    })
    save_table_func(dim_shift_start_type, 'dim_shift_start_type')

    stop_types = shifts['shift_stop_type_derived'].dropna().unique()
    dim_shift_stop_type = pd.DataFrame({
        'shift_stop_type_id': [f'SPT{i:04d}' for i in range(1, len(stop_types)+1)],
        'shift_stop_type_name': stop_types
    })
    save_table_func(dim_shift_stop_type, 'dim_shift_stop_type')

    start_map = dict(zip(dim_shift_start_type['shift_start_type_name'], dim_shift_start_type['shift_start_type_id']))
    stop_map = dict(zip(dim_shift_stop_type['shift_stop_type_name'], dim_shift_stop_type['shift_stop_type_id']))
    shifts['shift_start_type_id'] = shifts['shift_start_type_derived'].map(start_map)
    shifts['shift_stop_type_id'] = shifts['shift_stop_type_derived'].map(stop_map)

    situations = shifts['situation'].dropna().unique()
    dim_situation = pd.DataFrame({
        'situation_id': [f'SIT{i:04d}' for i in range(1, len(situations)+1)],
        'situation_name': situations
    })
    save_table_func(dim_situation, 'dim_situation')
    situation_map = dict(zip(dim_situation['situation_name'], dim_situation['situation_id']))
    shifts['situation_id'] = shifts['situation'].map(situation_map)

    shifts['shift_key'] = shifts['shift_id']

    save_table_func(shifts, 'fact_shifts')
    log.info(f"  ✓ fact_shifts: {len(shifts)} rows, {len(shifts.columns)} cols")
    log.info(f"  ✓ Player IDs, plus/minus (5 types), shift stats added")


def enhance_shift_players(output_dir: Path, log, save_table_func=None):
    """
    v19.00 ROOT CAUSE FIX: Expand fact_shift_players from 9 to 65+ columns.

    This is a TWO-PASS approach:
    - Pass 1: Pull stats from fact_shifts, calculate logical shifts
    - Pass 2: Add rating columns and adjusted stats

    LOGICAL SHIFT RULE: Any gap in shift_index = new logical shift

    Args:
        output_dir: Path to output directory
        log: ETLLogger instance
        save_table_func: Function to save tables (optional)
    """
    log.section("PHASE 5.11B: ENHANCE SHIFT PLAYERS (v19.00)")

    if save_table_func is None:
        save_table_func = lambda df, name: save_output_table(df, name, output_dir)

    shift_players_path = output_dir / 'fact_shift_players.csv'
    shifts_path = output_dir / 'fact_shifts.csv'

    if not shift_players_path.exists() or not shifts_path.exists():
        log.warn("Required tables not found, skipping shift_players enhancement")
        return

    sp = pd.read_csv(shift_players_path, low_memory=False)
    shifts = pd.read_csv(shifts_path, low_memory=False)
    dim_player = pd.read_csv(output_dir / 'dim_player.csv', low_memory=False)

    log.info(f"Enhancing {len(sp)} shift-player records...")
    log.info(f"  Source: fact_shifts has {len(shifts.columns)} columns")

    # ========================================
    # PASS 1: Pull stats from fact_shifts
    # ========================================
    log.info("  Pass 1: Pulling stats from fact_shifts...")

    shifts_for_merge = shifts.set_index('shift_id')

    time_cols = ['shift_duration', 'shift_start_total_seconds', 'shift_end_total_seconds', 'stoppage_time']
    context_cols = ['situation', 'situation_id', 'strength', 'strength_id', 'start_zone', 'end_zone',
                    'game_state', 'score_differential', 'is_close_game']

    stat_cols_venue = ['cf', 'ca', 'cf_pct', 'ff', 'fa', 'ff_pct', 'sf', 'sa', 'shot_diff',
                       'scf', 'sca', 'hdf', 'hda']
    zone_cols = ['home_zone_entries', 'away_zone_entries', 'home_zone_exits', 'away_zone_exits',
                 'home_giveaways', 'away_giveaways', 'home_bad_giveaways', 'away_bad_giveaways',
                 'home_takeaways', 'away_takeaways']
    fo_cols = ['home_fo_won', 'away_fo_won']
    stat_cols_direct = ['event_count']

    rating_cols_shifts = ['home_avg_rating', 'home_min_rating', 'home_max_rating',
                          'away_avg_rating', 'away_min_rating', 'away_max_rating',
                          'rating_differential', 'home_rating_advantage']

    fk_cols = ['period_id', 'season_id', 'home_team_id', 'away_team_id']

    goal_cols_home = ['home_gf_all', 'home_ga_all', 'home_gf_ev', 'home_ga_ev',
                      'home_gf_pp', 'home_ga_pp', 'home_gf_pk', 'home_ga_pk',
                      'home_pm_all', 'home_pm_ev']
    goal_cols_away = ['away_gf_all', 'away_ga_all', 'away_gf_ev', 'away_ga_ev',
                      'away_gf_pp', 'away_ga_pp', 'away_gf_pk', 'away_ga_pk',
                      'away_pm_all', 'away_pm_ev']

    all_pull_cols = time_cols + context_cols + stat_cols_direct + rating_cols_shifts + fk_cols
    all_pull_cols += goal_cols_home + goal_cols_away + stat_cols_venue + zone_cols + fo_cols

    available_cols = [col for col in all_pull_cols if col in shifts_for_merge.columns]
    missing_cols = [col for col in all_pull_cols if col not in shifts_for_merge.columns]
    if missing_cols:
        log.warn(f"  Missing columns in fact_shifts (will be skipped): {missing_cols}")

    sp = sp.merge(shifts_for_merge[available_cols], left_on='shift_id', right_index=True, how='left')

    home_mask = sp['venue'] == 'home'

    # Goals for/against (mapped by venue) - VECTORIZED
    sp['gf'] = np.where(home_mask,
                        sp['home_gf_all'].fillna(0),
                        sp['away_gf_all'].fillna(0))
    sp['ga'] = np.where(home_mask,
                        sp['home_ga_all'].fillna(0),
                        sp['away_ga_all'].fillna(0))
    sp['pm'] = sp['gf'] - sp['ga']
    sp['gf_ev'] = np.where(home_mask,
                           sp['home_gf_ev'].fillna(0),
                           sp['away_gf_ev'].fillna(0))
    sp['ga_ev'] = np.where(home_mask,
                           sp['home_ga_ev'].fillna(0),
                           sp['away_ga_ev'].fillna(0))
    sp['gf_pp'] = np.where(home_mask,
                           sp['home_gf_pp'].fillna(0),
                           sp['away_gf_pp'].fillna(0))
    sp['ga_pp'] = np.where(home_mask,
                           sp['home_ga_pp'].fillna(0),
                           sp['away_ga_pp'].fillna(0))
    sp['gf_pk'] = np.where(home_mask,
                           sp['home_gf_pk'].fillna(0),
                           sp['away_gf_pk'].fillna(0))
    sp['ga_pk'] = np.where(home_mask,
                           sp['home_ga_pk'].fillna(0),
                           sp['away_ga_pk'].fillna(0))
    sp['pm_ev'] = np.where(home_mask,
                           sp['home_pm_ev'].fillna(0),
                           sp['away_pm_ev'].fillna(0))

    # Team/opponent ratings (mapped by venue) - VECTORIZED
    if 'home_avg_rating' in sp.columns and 'away_avg_rating' in sp.columns:
        sp['team_avg_rating'] = np.where(home_mask,
                                         sp['home_avg_rating'].fillna(0),
                                         sp['away_avg_rating'].fillna(0))
        sp['opp_avg_rating'] = np.where(home_mask,
                                        sp['away_avg_rating'].fillna(0),
                                        sp['home_avg_rating'].fillna(0))
    else:
        sp['team_avg_rating'] = 0.0
        sp['opp_avg_rating'] = 0.0
    sp['team_id'] = np.where(home_mask,
                             sp['home_team_id'].fillna(''),
                             sp['away_team_id'].fillna(''))
    sp['opp_team_id'] = np.where(home_mask,
                                 sp['away_team_id'].fillna(''),
                                 sp['home_team_id'].fillna(''))

    # Corsi/Fenwick/Shot columns (venue-mapped)
    cf_orig = sp['cf'].fillna(0)
    ca_orig = sp['ca'].fillna(0)
    ff_orig = sp['ff'].fillna(0)
    fa_orig = sp['fa'].fillna(0)
    sf_orig = sp['sf'].fillna(0)
    sa_orig = sp['sa'].fillna(0)
    scf_orig = sp['scf'].fillna(0)
    sca_orig = sp['sca'].fillna(0)
    hdf_orig = sp['hdf'].fillna(0)
    hda_orig = sp['hda'].fillna(0)

    sp['cf'] = np.where(home_mask, cf_orig, ca_orig)
    sp['ca'] = np.where(home_mask, ca_orig, cf_orig)
    sp['ff'] = np.where(home_mask, ff_orig, fa_orig)
    sp['fa'] = np.where(home_mask, fa_orig, ff_orig)
    sp['sf'] = np.where(home_mask, sf_orig, sa_orig)
    sp['sa'] = np.where(home_mask, sa_orig, sf_orig)
    sp['scf'] = np.where(home_mask, scf_orig, sca_orig)
    sp['sca'] = np.where(home_mask, sca_orig, scf_orig)
    sp['hdf'] = np.where(home_mask, hdf_orig, hda_orig)
    sp['hda'] = np.where(home_mask, hda_orig, hdf_orig)
    sp['shot_diff'] = sp['sf'] - sp['sa']

    # Recalculate percentages
    total_cf = sp['cf'] + sp['ca']
    sp['cf_pct'] = (sp['cf'] / total_cf * 100).where(total_cf > 0, 50.0)

    total_ff = sp['ff'] + sp['fa']
    sp['ff_pct'] = (sp['ff'] / total_ff * 100).where(total_ff > 0, 50.0)

    # Zone entries/exits/giveaways/takeaways - venue mapped
    if 'venue' in sp.columns:
        sp['zone_entries'] = np.where(home_mask,
                                      sp['home_zone_entries'].fillna(0),
                                      sp['away_zone_entries'].fillna(0))
        sp['zone_exits'] = np.where(home_mask,
                                    sp['home_zone_exits'].fillna(0),
                                    sp['away_zone_exits'].fillna(0))
        sp['giveaways'] = np.where(home_mask,
                                   sp['home_giveaways'].fillna(0),
                                   sp['away_giveaways'].fillna(0))
        sp['bad_giveaways'] = np.where(home_mask,
                                       sp['home_bad_giveaways'].fillna(0),
                                       sp['away_bad_giveaways'].fillna(0))
        sp['takeaways'] = np.where(home_mask,
                                   sp['home_takeaways'].fillna(0),
                                   sp['away_takeaways'].fillna(0))

        # Player perspective: fo_won = your team's wins, fo_lost = opponent's wins
        home_fo = sp['home_fo_won'].fillna(0)
        away_fo = sp['away_fo_won'].fillna(0)
        sp['fo_won'] = np.where(home_mask, home_fo, away_fo)
        sp['fo_lost'] = np.where(home_mask, away_fo, home_fo)

    sp['playing_time'] = sp['shift_duration'].fillna(0) - sp['stoppage_time'].fillna(0)
    sp['playing_time'] = sp['playing_time'].clip(lower=0)

    log.info(f"    Pulled {len(all_pull_cols)} columns from fact_shifts")

    # ========================================
    # PASS 1B: Calculate Logical Shifts
    # ========================================
    log.info("  Pass 1B: Calculating logical shifts...")

    sp = sp.sort_values(['game_id', 'player_id', 'shift_index'])

    logical_shift_nums = []
    shift_segments = []

    prev_game = None
    prev_player = None
    prev_idx = None
    logical_num = 0
    segment = 0

    for _, row in sp.iterrows():
        game_id = row['game_id']
        player_id = row['player_id']
        shift_idx = row['shift_index']

        if game_id != prev_game or player_id != prev_player:
            logical_num = 1
            segment = 1
        elif pd.notna(prev_idx) and pd.notna(shift_idx):
            if int(shift_idx) != int(prev_idx) + 1:
                logical_num += 1
                segment = 1
            else:
                segment += 1
        else:
            segment += 1

        logical_shift_nums.append(logical_num)
        shift_segments.append(segment)

        prev_game = game_id
        prev_player = player_id
        prev_idx = shift_idx

    sp['logical_shift_number'] = logical_shift_nums
    sp['shift_segment'] = shift_segments

    sp['is_first_segment'] = sp['shift_segment'] == 1

    sp['logical_key'] = sp['game_id'].astype(str) + '_' + sp['player_id'].astype(str) + '_' + sp['logical_shift_number'].astype(str)
    max_segments = sp.groupby('logical_key')['shift_segment'].transform('max')
    sp['is_last_segment'] = sp['shift_segment'] == max_segments

    logical_durations = sp.groupby('logical_key')['shift_duration'].transform('sum')
    sp['logical_shift_duration'] = logical_durations

    sp['running_toi_game'] = sp.groupby(['game_id', 'player_id'])['shift_duration'].cumsum()

    sp = sp.drop(columns=['logical_key'])

    unique_logical = sp.groupby(['game_id', 'player_id'])['logical_shift_number'].max()
    log.info(f"    Logical shifts: max per player-game = {unique_logical.max()}, avg = {unique_logical.mean():.1f}")

    # ========================================
    # PASS 2: Add Player Ratings
    # ========================================
    log.info("  Pass 2: Adding player ratings and adjusted stats...")

    player_rating_map = dict(zip(dim_player['player_id'], dim_player['current_skill_rating']))

    sp['player_rating'] = sp['player_id'].map(player_rating_map)
    sp['qoc_rating'] = sp['opp_avg_rating']
    sp['qot_rating'] = sp['team_avg_rating']

    def get_competition_tier(opp_rating):
        if pd.isna(opp_rating):
            return None
        if opp_rating >= 5.0:
            return 'TI01'
        elif opp_rating >= 4.0:
            return 'TI02'
        elif opp_rating >= 3.0:
            return 'TI03'
        else:
            return 'TI04'

    sp['competition_tier_id'] = sp['opp_avg_rating'].apply(get_competition_tier)

    sp['opp_multiplier'] = sp['opp_avg_rating'] / 4.0
    sp['opp_multiplier'] = sp['opp_multiplier'].fillna(1.0)

    # ========================================
    # PASS 2B: Calculate Adjusted Stats
    # ========================================
    log.info("  Pass 2B: Calculating adjusted stats...")

    if 'opp_avg_rating' in sp.columns:
        sp['player_rating_diff'] = sp['player_rating'] - sp['opp_avg_rating']
    else:
        sp['player_rating_diff'] = 0.0

    if 'rating_differential' in sp.columns:
        sp['expected_cf_pct'] = 50 + (sp['rating_differential'].fillna(0) * 5)
    else:
        sp['expected_cf_pct'] = 50.0
    sp['expected_cf_pct'] = sp['expected_cf_pct'].clip(30, 70)

    sp['cf_pct_vs_expected'] = sp['cf_pct'] - sp['expected_cf_pct']

    sp['performance'] = pd.cut(
        sp['cf_pct_vs_expected'],
        bins=[-np.inf, -5, 5, np.inf],
        labels=['Under', 'Expected', 'Over'],
        include_lowest=True
    )
    sp['performance'] = sp['performance'].astype(str).replace('nan', None)

    sp['cf_adj'] = sp['cf'] * sp['opp_multiplier']
    sp['ca_adj'] = sp['ca'] / sp['opp_multiplier'].replace(0, 1)

    total_adj = sp['cf_adj'] + sp['ca_adj']
    sp['cf_pct_adj'] = (sp['cf_adj'] / total_adj * 100).where(total_adj > 0, 50.0)

    log.info(f"    Performance distribution: Over={len(sp[sp['performance']=='Over'])}, Expected={len(sp[sp['performance']=='Expected'])}, Under={len(sp[sp['performance']=='Under'])}")

    # ========================================
    # Reorder columns
    # ========================================
    id_cols = ['shift_player_id', 'shift_id', 'game_id', 'shift_index',
               'player_game_number', 'player_id', 'venue', 'position', 'period']

    time_cols_out = ['shift_duration', 'shift_start_total_seconds', 'shift_end_total_seconds',
                     'stoppage_time', 'playing_time', 'running_toi_game']

    logical_cols = ['logical_shift_number', 'shift_segment', 'is_first_segment',
                    'is_last_segment', 'logical_shift_duration']

    goal_cols = ['gf', 'ga', 'pm', 'gf_ev', 'ga_ev', 'gf_pp', 'ga_pp', 'gf_pk', 'ga_pk', 'pm_ev']

    corsi_cols = ['cf', 'ca', 'cf_pct', 'ff', 'fa', 'ff_pct']

    shot_cols = ['sf', 'sa', 'shot_diff']

    zone_event_cols = ['zone_entries', 'zone_exits', 'giveaways', 'takeaways', 'fo_won', 'fo_lost']

    context_cols_out = ['situation', 'situation_id', 'strength', 'strength_id', 'start_zone', 'end_zone']

    rating_cols = ['player_rating', 'team_avg_rating', 'opp_avg_rating', 'rating_differential',
                   'qoc_rating', 'qot_rating', 'competition_tier_id', 'opp_multiplier', 'player_rating_diff']

    adj_cols = ['expected_cf_pct', 'cf_pct_vs_expected', 'performance',
                'cf_adj', 'ca_adj', 'cf_pct_adj']

    fk_cols_out = ['team_id', 'opp_team_id', 'season_id', 'period_id']

    extra_cols = ['scf', 'sca', 'hdf', 'hda', 'event_count',
                  'home_avg_rating', 'away_avg_rating', 'home_min_rating', 'away_min_rating',
                  'home_max_rating', 'away_max_rating', 'home_rating_advantage',
                  'home_team_id', 'away_team_id']

    ordered_cols = (id_cols + time_cols_out + logical_cols + goal_cols + corsi_cols +
                    shot_cols + zone_event_cols + context_cols_out + rating_cols + adj_cols + fk_cols_out)

    remaining = [c for c in sp.columns if c not in ordered_cols and c not in extra_cols]
    extra_existing = [c for c in extra_cols if c in sp.columns]

    final_cols = ordered_cols + extra_existing + remaining
    final_cols = [c for c in final_cols if c in sp.columns]

    sp = sp[final_cols]

    save_table_func(sp, 'fact_shift_players')
    log.info(f"  ✓ fact_shift_players: {len(sp)} rows, {len(sp.columns)} columns")
    log.info(f"  ✓ Enhanced from 9 to {len(sp.columns)} columns (v19.00 fix)")


def update_roster_positions_from_shifts(output_dir: Path, log, save_table_func=None):
    """Build fact_player_game_position and update fact_gameroster positions for tracked games.

    For tracked games, position is determined by actual shift data (slot -> position),
    which is more accurate than the BLB-sourced position that may be outdated.

    Args:
        output_dir: Path to output directory
        log: ETLLogger instance
        save_table_func: Function to save tables (optional)
    """
    log.section("PHASE 5.12: UPDATE ROSTER POSITIONS FROM SHIFTS")

    if save_table_func is None:
        save_table_func = lambda df, name: save_output_table(df, name, output_dir)

    shift_players_path = output_dir / 'fact_shift_players.csv'
    roster_path = output_dir / 'fact_gameroster.csv'

    if not shift_players_path.exists():
        log.warn("fact_shift_players not found, skipping position update")
        return

    shift_players = pd.read_csv(shift_players_path, low_memory=False)
    roster = pd.read_csv(roster_path, low_memory=False)

    log.info(f"Building player game positions from {len(shift_players)} shift-player records...")

    pos_to_name = {
        'F1': 'Forward', 'F2': 'Forward', 'F3': 'Forward',
        'D1': 'Defense', 'D2': 'Defense',
        'G': 'Goalie',
        'X': 'Forward',
    }

    if 'logical_shift_number' not in shift_players.columns:
        log.warn("logical_shift_number not found in fact_shift_players - using shift_index")
        shift_players['logical_shift_number'] = shift_players.get('shift_index', shift_players.index)

    position_stats = []
    for (game_id, player_id), group in shift_players.groupby(['game_id', 'player_id']):
        if pd.isna(player_id):
            continue

        total_shifts = group['logical_shift_number'].nunique() if 'logical_shift_number' in group.columns else len(group)
        position_counts = {}

        for logical_shift_num, shift_group in group.groupby('logical_shift_number'):
            first_row = shift_group.iloc[0]
            pos_code = str(first_row.get('position', ''))
            pos_name = pos_to_name.get(pos_code, 'Unknown')
            position_counts[pos_name] = position_counts.get(pos_name, 0) + 1

        if position_counts:
            dominant_pos = max(position_counts, key=position_counts.get)
            dominant_pct = position_counts[dominant_pos] / total_shifts * 100
        else:
            dominant_pos = 'Unknown'
            dominant_pct = 0

        position_stats.append({
            'game_id': game_id,
            'player_id': player_id,
            'total_shifts': total_shifts,
            'dominant_position': dominant_pos,
            'dominant_position_pct': round(dominant_pct, 1),
            'forward_shifts': position_counts.get('Forward', 0),
            'defense_shifts': position_counts.get('Defense', 0),
            'goalie_shifts': position_counts.get('Goalie', 0),
        })

    pgp = pd.DataFrame(position_stats)
    save_table_func(pgp, 'fact_player_game_position')
    log.info(f"  ✓ fact_player_game_position: {len(pgp)} rows")

    if len(pgp) > 0:
        pgp_lookup = pgp.set_index(['game_id', 'player_id'])
        tracked_games = set(pgp['game_id'].unique())

        pos_id_map = {
            'Forward': 'PS0004',
            'Defense': 'PS0005',
            'Goalie': 'PS0006',
        }

        updates = 0
        for i, row in roster.iterrows():
            key = (row['game_id'], row['player_id'])
            if row['game_id'] in tracked_games and key in pgp_lookup.index:
                new_pos = pgp_lookup.loc[key, 'dominant_position']
                if new_pos != 'Unknown' and new_pos != row['player_position']:
                    roster.at[i, 'player_position'] = new_pos
                    roster.at[i, 'position_id'] = pos_id_map.get(new_pos)
                    updates += 1

        if updates > 0:
            save_table_func(roster, 'fact_gameroster')
            log.info(f"  ✓ Updated {updates} positions in fact_gameroster from shift data")
        else:
            log.info(f"  No position updates needed")

    multi_pos = pgp[pgp['dominant_position_pct'] < 90]
    if len(multi_pos) > 0:
        log.info(f"  Players with <90% dominant position: {len(multi_pos)}")
