"""
Event Enhancement Module
========================

Contains functions for enhancing event tables with derived FKs and flags.

Functions:
- enhance_event_tables: Add derived FK columns to fact_events and fact_event_players
- enhance_derived_event_tables: Add FKs to tables derived from events
- enhance_events_with_flags: Add time columns, flags, and derived keys to fact_events
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Import key utilities
from src.utils.key_parser import parse_shift_key

# Import table writer for saving
from src.core.table_writer import save_output_table

# Import safe CSV reader
from src.core.safe_csv import safe_read_csv

# Import utilities
from .utilities import drop_all_null_columns


def enhance_event_tables(output_dir: Path, log, table_store_available: bool = False, get_table_from_store=None):
    """Add derived FK columns to fact_events and fact_event_players.

    Args:
        output_dir: Path to output directory
        log: ETLLogger instance
        table_store_available: Whether table store is available
        get_table_from_store: Function to get table from store
    """
    log.section("PHASE 5.5: ENHANCE EVENT TABLES")

    # Load required tables (from cache first, then CSV)
    tracking = get_table_from_store('fact_event_players', output_dir) if table_store_available and get_table_from_store else pd.DataFrame()
    if len(tracking) == 0:
        tracking_path = output_dir / 'fact_event_players.csv'
        if tracking_path.exists():
            tracking = safe_read_csv(tracking_path)

    events = get_table_from_store('fact_events', output_dir) if table_store_available and get_table_from_store else pd.DataFrame()
    if len(events) == 0:
        events_path = output_dir / 'fact_events.csv'
        if events_path.exists():
            events = safe_read_csv(events_path)

    if len(tracking) == 0 or len(events) == 0:
        log.warn("Event tables not found, skipping enhancement")
        return

    shifts = get_table_from_store('fact_shifts', output_dir) if table_store_available and get_table_from_store else pd.DataFrame()
    if len(shifts) == 0:
        shifts_path = output_dir / 'fact_shifts.csv'
        if shifts_path.exists():
            shifts = safe_read_csv(shifts_path)

    players = get_table_from_store('dim_player', output_dir) if table_store_available and get_table_from_store else pd.DataFrame()
    if len(players) == 0:
        players_path = output_dir / 'dim_player.csv'
        if players_path.exists():
            players = safe_read_csv(players_path)

    schedule = get_table_from_store('dim_schedule', output_dir) if table_store_available and get_table_from_store else pd.DataFrame()
    if len(schedule) == 0:
        schedule_path = output_dir / 'dim_schedule.csv'
        if schedule_path.exists():
            schedule = safe_read_csv(schedule_path)

    roster = get_table_from_store('fact_gameroster', output_dir) if table_store_available and get_table_from_store else pd.DataFrame()
    if len(roster) == 0:
        roster_path = output_dir / 'fact_gameroster.csv'
        if roster_path.exists():
            roster = safe_read_csv(roster_path)

    log.info(f"Enhancing fact_event_players: {len(tracking)} rows, {len(tracking.columns)} cols")
    log.info(f"Enhancing fact_events: {len(events)} rows, {len(events.columns)} cols")

    # 0. Add shift_id FK by matching event time to shift time ranges
    log.info("  Adding shift_id FK (matching events to shifts)...")

    # CRITICAL: Event times are ASCENDING (0 = period start, counting up to ~1080)
    # Shift times are DESCENDING (1080 = period start, counting down to ~0)
    # Need to convert event time to shift time format: shift_time = period_max - event_time

    if 'shift_start_total_seconds' in shifts.columns and 'shift_end_total_seconds' in shifts.columns:
        # Find period max time for each game/period (= period duration in countdown format)
        # VECTORIZED: Use groupby instead of iterrows
        shifts_clean = shifts[['game_id', 'period', 'shift_start_total_seconds']].copy()
        shifts_clean['game_id'] = shifts_clean['game_id'].astype(int)
        shifts_clean['period'] = shifts_clean['period'].astype(int)
        shifts_clean['shift_start_total_seconds'] = pd.to_numeric(shifts_clean['shift_start_total_seconds'], errors='coerce').fillna(0)
        period_max = shifts_clean.groupby(['game_id', 'period'])['shift_start_total_seconds'].max().to_dict()

        # Build lookup: for each game/period, list of (shift_id, start_countdown, end_countdown)
        # VECTORIZED: Use groupby.apply instead of iterrows
        shifts_for_ranges = shifts[['game_id', 'period', 'shift_id', 'shift_start_total_seconds', 'shift_end_total_seconds']].copy()
        shifts_for_ranges['game_id'] = shifts_for_ranges['game_id'].astype(int)
        shifts_for_ranges['period'] = shifts_for_ranges['period'].astype(int)
        shifts_for_ranges['shift_start_total_seconds'] = pd.to_numeric(shifts_for_ranges['shift_start_total_seconds'], errors='coerce').fillna(0)
        shifts_for_ranges['shift_end_total_seconds'] = pd.to_numeric(shifts_for_ranges['shift_end_total_seconds'], errors='coerce').fillna(0)

        def build_shift_ranges(group):
            return list(zip(group['shift_id'].values,
                           group['shift_start_total_seconds'].values,
                           group['shift_end_total_seconds'].values))

        shift_ranges_dict = shifts_for_ranges.groupby(['game_id', 'period']).apply(build_shift_ranges).to_dict()
        shift_ranges = {(int(k[0]), int(k[1])): v for k, v in shift_ranges_dict.items()}

        def find_shift_id(row):
            """Find shift_id for an event based on game, period, and time."""
            try:
                game_id = int(row['game_id'])
                period = int(row['period']) if pd.notna(row.get('period')) else 1

                # Get event time (elapsed format: 0 = period start)
                event_elapsed = None
                for col in ['time_start_total_seconds', 'event_total_seconds']:
                    if col in row.index and pd.notna(row.get(col)):
                        event_elapsed = float(row[col])
                        break

                if event_elapsed is None:
                    return None

                key = (game_id, period)
                if key not in shift_ranges or key not in period_max:
                    return None

                # Convert event elapsed time to countdown format
                # countdown = period_max - elapsed
                event_countdown = period_max[key] - event_elapsed

                # Find shift containing this event time
                # Shift times are countdown: start > end (start is higher number)
                # Event is in shift if: shift_end <= event_countdown <= shift_start
                for shift_id, start, end in shift_ranges[key]:
                    if end <= event_countdown <= start:
                        return shift_id

                return None
            except (ValueError, TypeError):
                return None

        # Apply to fact_event_players
        tracking['shift_id'] = tracking.apply(find_shift_id, axis=1)
        shift_fill = tracking['shift_id'].notna().sum()
        log.info(f"    fact_event_players.shift_id: {shift_fill}/{len(tracking)} ({100*shift_fill/len(tracking):.1f}%)")

        # Apply to fact_events
        events['shift_id'] = events.apply(find_shift_id, axis=1)
        shift_fill_ev = events['shift_id'].notna().sum()
        log.info(f"    fact_events.shift_id: {shift_fill_ev}/{len(events)} ({100*shift_fill_ev/len(events):.1f}%)")

        # Copy shift_id to shift_key (shift_id IS the shift_key format: 'SH1896900001')
        tracking['shift_key'] = tracking['shift_id']
        events['shift_key'] = events['shift_id']
        log.info(f"    shift_key populated from shift_id")
    else:
        log.warn("    Shift time columns not found, skipping shift_id FK")

    # Load dimension tables for mapping
    shot_type = safe_read_csv(output_dir / 'dim_shot_type.csv')
    ze_type = safe_read_csv(output_dir / 'dim_zone_entry_type.csv')
    zx_type = safe_read_csv(output_dir / 'dim_zone_exit_type.csv')
    pass_type = safe_read_csv(output_dir / 'dim_pass_type.csv')
    stoppage_type = safe_read_csv(output_dir / 'dim_stoppage_type.csv')
    giveaway_type = safe_read_csv(output_dir / 'dim_giveaway_type.csv')
    takeaway_type = safe_read_csv(output_dir / 'dim_takeaway_type.csv')

    # 1. player_name
    log.info("  Adding player_name...")
    player_map = dict(zip(players['player_id'], players['player_full_name']))
    tracking['player_name'] = tracking['player_id'].map(player_map)

    # 2. season_id (from schedule)
    log.info("  Adding season_id...")
    season_map = dict(zip(schedule['game_id'].astype(int), schedule['season_id']))
    tracking['season_id'] = tracking['game_id'].map(season_map)

    # 3. position_id (from roster)
    log.info("  Adding position_id...")
    # Map position names to IDs
    pos_map = {'Forward': 4, 'Defense': 5, 'Goalie': 6, 'Center': 1, 'Left Wing': 2, 'Right Wing': 3}
    # VECTORIZED: Create player+game -> position lookup
    roster_valid = roster[roster['player_position'].notna()].copy()
    roster_pos = dict(zip(
        zip(roster_valid['player_id'].astype(str), roster_valid['game_id'].astype(int)),
        roster_valid['player_position'].map(pos_map).fillna(4)  # Default to Forward if unknown
    ))

    def get_position(row):
        key = (str(row['player_id']), int(row['game_id']))
        return roster_pos.get(key)
    tracking['position_id'] = tracking.apply(get_position, axis=1)

    # 4. shot_type_id - VECTORIZED
    log.info("  Adding shot_type_id...")
    shot_type_copy = shot_type.copy()
    shot_type_copy['code_normalized'] = shot_type_copy['shot_type_code'].str.replace('-', '_')
    shot_type_copy['code_lower'] = shot_type_copy['code_normalized'].str.lower()
    shot_map = dict(zip(shot_type_copy['code_normalized'], shot_type_copy['shot_type_id']))
    shot_map.update(dict(zip(shot_type_copy['code_lower'], shot_type_copy['shot_type_id'])))

    def get_shot_type(row):
        if row['event_type'] not in ['Shot', 'Goal']:
            return None
        detail2 = str(row['event_detail_2']) if pd.notna(row['event_detail_2']) else ''
        # Strip prefixes: Shot_, Goal_
        for prefix in ['Shot_', 'Goal_']:
            if detail2.startswith(prefix):
                detail2 = detail2[len(prefix):]
                break
        return shot_map.get(detail2) or shot_map.get(detail2.lower())

    tracking['shot_type_id'] = tracking.apply(get_shot_type, axis=1)

    # 5. zone_entry_type_id - VECTORIZED
    log.info("  Adding zone_entry_type_id...")
    ze_type_copy = ze_type.copy()
    ze_type_copy['code_normalized'] = ze_type_copy['zone_entry_type_code'].str.replace('-', '_')
    ze_map = dict(zip(ze_type_copy['code_normalized'], ze_type_copy['zone_entry_type_id']))
    # Add aliases for Rush <-> Carried normalization
    rush_mask = ze_type_copy['code_normalized'].str.contains('Rush', na=False)
    carried_mask = ze_type_copy['code_normalized'].str.contains('Carried', na=False)
    if rush_mask.any():
        ze_map.update(dict(zip(
            ze_type_copy.loc[rush_mask, 'code_normalized'].str.replace('Rush', 'Carried'),
            ze_type_copy.loc[rush_mask, 'zone_entry_type_id']
        )))
    if carried_mask.any():
        ze_map.update(dict(zip(
            ze_type_copy.loc[carried_mask, 'code_normalized'].str.replace('Carried', 'Rush'),
            ze_type_copy.loc[carried_mask, 'zone_entry_type_id']
        )))

    def get_ze_type(row):
        if row['event_type'] != 'Zone_Entry_Exit':
            return None
        detail2 = str(row['event_detail_2']) if pd.notna(row['event_detail_2']) else ''
        if not detail2.startswith('ZoneEntry'):
            return None
        for key, val in ze_map.items():
            if detail2.startswith(key):
                return val
        return None
    tracking['zone_entry_type_id'] = tracking.apply(get_ze_type, axis=1)

    # 6. zone_exit_type_id (NEW) - VECTORIZED
    log.info("  Adding zone_exit_type_id...")
    zx_type_copy = zx_type.copy()
    zx_type_copy['code_normalized'] = zx_type_copy['zone_exit_type_code'].str.replace('-', '_')
    zx_map = dict(zip(zx_type_copy['code_normalized'], zx_type_copy['zone_exit_type_id']))
    # Add aliases for Rush <-> Carried normalization
    rush_mask = zx_type_copy['code_normalized'].str.contains('Rush', na=False)
    carried_mask = zx_type_copy['code_normalized'].str.contains('Carried', na=False)
    if rush_mask.any():
        zx_map.update(dict(zip(
            zx_type_copy.loc[rush_mask, 'code_normalized'].str.replace('Rush', 'Carried'),
            zx_type_copy.loc[rush_mask, 'zone_exit_type_id']
        )))
    if carried_mask.any():
        zx_map.update(dict(zip(
            zx_type_copy.loc[carried_mask, 'code_normalized'].str.replace('Carried', 'Rush'),
            zx_type_copy.loc[carried_mask, 'zone_exit_type_id']
        )))

    def get_zx_type(row):
        if row['event_type'] != 'Zone_Entry_Exit':
            return None
        detail2 = str(row['event_detail_2']) if pd.notna(row['event_detail_2']) else ''
        if not detail2.startswith('ZoneExit'):
            return None
        for key, val in zx_map.items():
            if detail2.startswith(key):
                return val
        return None
    tracking['zone_exit_type_id'] = tracking.apply(get_zx_type, axis=1)

    # 7. stoppage_type_id - Dynamic lookup from dim_stoppage_type
    log.info("  Adding stoppage_type_id...")
    stoppage_type_path = output_dir / 'dim_stoppage_type.csv'
    if stoppage_type_path.exists():
        stoppage_dim = safe_read_csv(stoppage_type_path)
        # Build mapping from code to ID
        stoppage_map = dict(zip(stoppage_dim['stoppage_type_code'], stoppage_dim['stoppage_type_id']))
    else:
        stoppage_map = {}
        log.warn("  dim_stoppage_type.csv not found - stoppage_type_id will be None")

    tracking['stoppage_type_id'] = tracking.apply(
        lambda r: stoppage_map.get(r['event_detail']) if r['event_type'] == 'Stoppage' else None, axis=1
    )

    # 8. giveaway_type_id (NEW)
    log.info("  Adding giveaway_type_id...")
    # Dynamic lookup from dim_giveaway_type - match event_detail_2 to giveaway_type_code
    giveaway_type_path = output_dir / 'dim_giveaway_type.csv'
    if giveaway_type_path.exists():
        giveaway_dim = safe_read_csv(giveaway_type_path)
        # VECTORIZED: Build mapping from code to ID (handles variations like / vs _)
        giveaway_map = dict(zip(giveaway_dim['giveaway_type_code'], giveaway_dim['giveaway_type_id']))
        # Also map variations (replace / with _)
        giveaway_map.update(dict(zip(
            giveaway_dim['giveaway_type_code'].str.replace('/', '_'),
            giveaway_dim['giveaway_type_id']
        )))
    else:
        giveaway_map = {}
        log.warn("  dim_giveaway_type.csv not found - giveaway_type_id will be None")

    def get_giveaway_type(row):
        if row['event_type'] != 'Turnover':
            return None
        detail = str(row['event_detail']) if pd.notna(row['event_detail']) else ''
        if 'Giveaway' not in detail:
            return None
        # Use event_detail_2 to determine giveaway type
        detail2 = str(row['event_detail_2']) if pd.notna(row.get('event_detail_2')) else ''
        if detail2 in giveaway_map:
            return giveaway_map[detail2]
        # Try variations
        detail2_alt = detail2.replace('/', '_')
        if detail2_alt in giveaway_map:
            return giveaway_map[detail2_alt]
        return None
    tracking['giveaway_type_id'] = tracking.apply(get_giveaway_type, axis=1)

    # 9. takeaway_type_id - Dynamic lookup from dim_takeaway_type
    log.info("  Adding takeaway_type_id...")
    takeaway_type_path = output_dir / 'dim_takeaway_type.csv'
    if takeaway_type_path.exists():
        takeaway_dim = safe_read_csv(takeaway_type_path)
        # VECTORIZED: Build takeaway map
        takeaway_map = dict(zip(takeaway_dim['takeaway_type_code'], takeaway_dim['takeaway_type_id']))
        takeaway_map.update(dict(zip(
            takeaway_dim['takeaway_type_code'].str.replace('/', '_'),
            takeaway_dim['takeaway_type_id']
        )))
    else:
        takeaway_map = {}
        log.warn("  dim_takeaway_type.csv not found - takeaway_type_id will be None")

    def get_takeaway_type(row):
        if row['event_type'] != 'Turnover':
            return None
        detail = str(row['event_detail']) if pd.notna(row['event_detail']) else ''
        if 'Takeaway' not in detail:
            return None
        # Use event_detail_2 to determine takeaway type
        detail2 = str(row['event_detail_2']) if pd.notna(row.get('event_detail_2')) else ''
        if detail2 in takeaway_map:
            return takeaway_map[detail2]
        detail2_alt = detail2.replace('/', '_')
        if detail2_alt in takeaway_map:
            return takeaway_map[detail2_alt]
        return None
    tracking['takeaway_type_id'] = tracking.apply(get_takeaway_type, axis=1)

    # 10. turnover_type_id - NOTE: dim_turnover_type is created later in static dimensions
    # giveaway_type_id and takeaway_type_id provide more specific categorization
    log.info("  Adding turnover_type_id (placeholder - linked in post-ETL)...")
    tracking['turnover_type_id'] = None  # Will be populated if needed in post-ETL

    # 11. pass_type_id - VECTORIZED
    log.info("  Adding pass_type_id...")
    pass_map = dict(zip(pass_type['pass_type_code'], pass_type['pass_type_id']))
    pass_map.update(dict(zip(
        pass_type['pass_type_code'].str.lower(),
        pass_type['pass_type_id']
    )))

    def get_pass_type(row):
        if row['event_type'] != 'Pass':
            return None
        detail2 = str(row['event_detail_2']) if pd.notna(row['event_detail_2']) else ''
        # Strip Pass_ prefix
        if detail2.startswith('Pass_'):
            detail2 = detail2[5:]
        return pass_map.get(detail2) or pass_map.get(detail2.lower())

    tracking['pass_type_id'] = tracking.apply(get_pass_type, axis=1)

    # 12. time_bucket_id
    log.info("  Adding time_bucket_id...")
    def get_time_bucket(row):
        period = row['period']
        start_min = row.get('event_start_min')
        if pd.isna(start_min):
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
    tracking['time_bucket_id'] = tracking.apply(get_time_bucket, axis=1)

    # 13. strength_id (from shift data)
    log.info("  Adding strength_id...")
    def count_skaters(row, prefix):
        count = 0
        for pos in ['forward_1', 'forward_2', 'forward_3', 'defense_1', 'defense_2']:
            col = f'{prefix}_{pos}'
            if col in row.index and pd.notna(row[col]):
                count += 1
        return count

    # VECTORIZED: Calculate skater counts for all shifts at once
    def count_skaters_vectorized(df, prefix):
        """Count skaters for all rows at once."""
        positions = ['forward_1', 'forward_2', 'forward_3', 'defense_1', 'defense_2']
        count = pd.Series(0, index=df.index)
        for pos in positions:
            col = f'{prefix}_{pos}'
            if col in df.columns:
                count += df[col].notna().astype(int)
        return count

    if len(shifts) > 0:
        home_sk = count_skaters_vectorized(shifts, 'home')
        away_sk = count_skaters_vectorized(shifts, 'away')

        strength_map = {
            (5,5): 'STR0001', (5,4): 'STR0002', (5,3): 'STR0003',
            (4,5): 'STR0004', (3,5): 'STR0005', (4,4): 'STR0006',
            (3,3): 'STR0007', (4,3): 'STR0008', (3,4): 'STR0009',
        }

        # Create tuples and map
        strength_tuples = list(zip(home_sk, away_sk))
        shift_strength_values = [strength_map.get(t, 'STR0001') for t in strength_tuples]
        shift_strength = dict(zip(
            zip(shifts['game_id'], shifts['shift_index']),
            shift_strength_values
        ))
    else:
        shift_strength = {}

    def get_strength(row):
        shift_key = row.get('shift_key')
        if pd.isna(shift_key):
            return None
        parts = parse_shift_key(shift_key)
        if parts is None:
            return None
        return shift_strength.get((parts.game_id, parts.shift_index), 'STR0001')
    tracking['strength_id'] = tracking.apply(get_strength, axis=1)

    # Fallback: Map from strength column if strength_id is still null
    if 'strength' in tracking.columns:
        strength_direct_map = {
            '5v5': 'STR01', '5v4': 'STR02', '4v5': 'STR03', '5v3': 'STR04',
            '3v5': 'STR05', '4v4': 'STR06', '3v3': 'STR07', '4v3': 'STR08',
            '3v4': 'STR09', '6v5': 'STR10', '5v6': 'STR11', '6v4': 'STR12',
            '4v6': 'STR13', '6v3': 'STR14', '3v6': 'STR15'
        }
        strength_from_col = tracking['strength'].map(strength_direct_map)
        tracking['strength_id'] = tracking['strength_id'].fillna(strength_from_col)

    # 15. player_rating (from dim_player)
    log.info("  Adding player_rating...")
    player_rating_map = dict(zip(players['player_id'], players['current_skill_rating']))
    tracking['player_rating'] = tracking['player_id'].map(player_rating_map)

    # 14. Drop unwanted columns
    log.info("  Dropping: role_number, role_abrev, team_venue_abv...")
    for col in ['role_number', 'role_abrev', 'team_venue_abv']:
        if col in tracking.columns:
            tracking = tracking.drop(columns=[col])

    # Save enhanced tracking
    save_output_table(tracking, 'fact_event_players', output_dir)
    log.info(f"  fact_event_players: {len(tracking)} rows, {len(tracking.columns)} cols")

    # Now enhance fact_events (get first row per event from tracking)
    log.info("  Enhancing fact_events from tracking...")
    new_cols = ['player_name', 'season_id', 'position_id', 'shot_type_id', 'zone_entry_type_id',
                'zone_exit_type_id', 'stoppage_type_id', 'giveaway_type_id', 'takeaway_type_id',
                'turnover_type_id', 'pass_type_id', 'time_bucket_id', 'strength_id',
                'player_rating']

    tracking_first = tracking.groupby('event_id').first().reset_index()
    for col in new_cols:
        if col in tracking_first.columns:
            col_map = dict(zip(tracking_first['event_id'], tracking_first[col]))
            # Only overwrite if column doesn't exist or new value is not null
            if col not in events.columns:
                events[col] = events['event_id'].map(col_map)
            else:
                # Keep existing non-null values, fill nulls from tracking
                new_vals = events['event_id'].map(col_map)
                events[col] = events[col].fillna(new_vals)

    save_output_table(events, 'fact_events', output_dir)
    log.info(f"  fact_events: {len(events)} rows, {len(events.columns)} cols")

    # Log fill rates
    log.info("  Fill rates:")
    for col in new_cols:
        if col in tracking.columns:
            fill = tracking[col].notna().sum()
            log.info(f"    {col}: {fill}/{len(tracking)} ({100*fill/len(tracking):.1f}%)")


def _build_cycle_events(tracking, events, output_dir, log):
    """
    Build fact_cycle_events using zone inference.

    A cycle is defined as:
    - 3+ consecutive passes by the same team in offensive zone
    - Includes Pass and Possession events
    - Ends with: Shot, Goal, Turnover, Zone exit, or possession change
    """
    teams = safe_read_csv(output_dir / 'dim_team.csv')
    team_name_to_id = dict(zip(teams['team_name'], teams['team_id']))

    # Get primary player rows only for detection
    primary = tracking[tracking['player_role'] == 'event_player_1'].copy()
    primary = primary.sort_values(['game_id', 'event_running_start', 'event_id']).reset_index(drop=True)

    all_cycles = []
    cycle_counter = 0

    cycle_events_types = ['Pass', 'Possession']
    cycle_enders = ['Shot', 'Goal', 'Turnover', 'Zone_Entry_Exit', 'Faceoff', 'Stoppage', 'Save']

    for game_id in primary['game_id'].unique():
        game_df = primary[primary['game_id'] == game_id].copy().sort_values('event_running_start').reset_index(drop=True)

        # Infer zones from Zone_Entry/Exit events
        team_zones = {}
        inferred_zones = []

        for i, row in game_df.iterrows():
            team = row['player_team']
            event_type = row['event_type']
            detail = row['event_detail']
            explicit_zone = row['event_team_zone']

            if pd.notna(explicit_zone) and str(explicit_zone).strip() in ['o', 'd', 'n']:
                team_zones[team] = str(explicit_zone).strip()
                inferred_zones.append(str(explicit_zone).strip())
            elif event_type == 'Zone_Entry_Exit':
                if detail in ['Zone_Entry', 'Zone_Keepin']:
                    team_zones[team] = 'o'
                    inferred_zones.append('o')
                elif detail in ['Zone_Exit']:
                    team_zones[team] = 'n'
                    inferred_zones.append('n')
                else:
                    inferred_zones.append(team_zones.get(team, 'n'))
            else:
                inferred_zones.append(team_zones.get(team, 'n'))

        game_df['inferred_zone'] = inferred_zones

        # Detect cycles
        current_cycle_events = []
        current_cycle_passes = 0
        current_team = None

        first_row = game_df.iloc[0] if len(game_df) > 0 else None

        for i, row in game_df.iterrows():
            event_type = row['event_type']
            team = row['player_team']
            zone = row['inferred_zone']
            detail = row['event_detail']

            if zone != 'o':
                if len(current_cycle_events) > 0 and current_cycle_passes >= 3:
                    cycle_counter += 1
                    all_cycles.append(_make_cycle_record(
                        cycle_counter, game_id, current_team, current_cycle_events,
                        current_cycle_passes, 'zone_change', team_name_to_id, first_row
                    ))
                current_cycle_events = []
                current_cycle_passes = 0
                current_team = None
                continue

            if event_type in cycle_events_types:
                if current_team is None or current_team == team:
                    current_cycle_events.append(row)
                    if event_type == 'Pass':
                        current_cycle_passes += 1
                    current_team = team
                else:
                    if current_cycle_passes >= 3:
                        cycle_counter += 1
                        all_cycles.append(_make_cycle_record(
                            cycle_counter, game_id, current_team, current_cycle_events,
                            current_cycle_passes, 'possession_change', team_name_to_id, first_row
                        ))
                    current_cycle_events = [row]
                    current_cycle_passes = 1 if event_type == 'Pass' else 0
                    current_team = team

            elif event_type in cycle_enders:
                if current_team == team and event_type in ['Shot', 'Goal']:
                    current_cycle_events.append(row)

                if current_cycle_passes >= 3:
                    cycle_counter += 1
                    end_type = event_type.lower()
                    if event_type == 'Turnover':
                        end_type = 'turnover'
                    all_cycles.append(_make_cycle_record(
                        cycle_counter, game_id, current_team, current_cycle_events,
                        current_cycle_passes, end_type, team_name_to_id, first_row
                    ))

                current_cycle_events = []
                current_cycle_passes = 0
                current_team = None

    cycles_df = pd.DataFrame(all_cycles)

    if len(cycles_df) > 0:
        # Add period from events
        event_periods = dict(zip(events['event_id'], events['period']))
        cycles_df['period'] = cycles_df['start_event_id'].map(event_periods)
        cycles_df['period_id'] = cycles_df['period'].apply(lambda x: f'P{int(x):02d}' if pd.notna(x) else None)

        # Remove columns that are 100% null
        cycles_df, removed_cols = drop_all_null_columns(cycles_df)
        if removed_cols:
            log.info(f"  Removed {len(removed_cols)} all-null columns from fact_cycle_events: {removed_cols[:10]}{'...' if len(removed_cols) > 10 else ''}")

        # Save fact_cycle_events
        save_output_table(cycles_df, 'fact_cycle_events', output_dir)
        log.info(f"  fact_cycle_events: {len(cycles_df)} rows, {len(cycles_df.columns)} columns")

        # Build event_id -> cycle_key mapping (vectorized)
        cycle_events = cycles_df[['cycle_key', 'event_ids']].copy()
        cycle_events['event_ids'] = cycle_events['event_ids'].astype(str).str.split(',')
        cycle_events = cycle_events.explode('event_ids')
        cycle_events['event_ids'] = cycle_events['event_ids'].str.strip()
        event_to_cycle = dict(zip(cycle_events['event_ids'], cycle_events['cycle_key']))

        # Update tracking with cycle_key
        tracking['cycle_key'] = tracking['event_id'].map(event_to_cycle)
        tracking['is_cycle'] = tracking['cycle_key'].notna().astype(int)
        save_output_table(tracking, 'fact_event_players', output_dir)

        # Update events with cycle_key
        events['cycle_key'] = events['event_id'].map(event_to_cycle)
        events['is_cycle'] = events['cycle_key'].notna().astype(int)
        save_output_table(events, 'fact_events', output_dir)

        log.info(f"  Updated is_cycle flag: {tracking['is_cycle'].sum()} tracking rows, {events['is_cycle'].sum()} event rows")
    else:
        log.warn("  No cycles detected")


def _make_cycle_record(cycle_num, game_id, team_name, events_list, pass_count, end_type, team_map, first_row):
    """Build a cycle record dictionary."""
    event_ids = [e['event_id'] for e in events_list]
    player_ids = list(set([e['player_id'] for e in events_list if pd.notna(e.get('player_id'))]))

    return {
        'cycle_key': f'CY{game_id}{cycle_num:04d}',
        'game_id': game_id,
        'season_id': first_row.get('season_id') if first_row is not None else None,
        'team_id': team_map.get(team_name),
        'team_name': team_name,
        'home_team_id': first_row.get('home_team_id') if first_row is not None else None,
        'away_team_id': first_row.get('away_team_id') if first_row is not None else None,
        'pass_count': pass_count,
        'event_count': len(events_list),
        'player_count': len(player_ids),
        'start_event_id': events_list[0]['event_id'],
        'end_event_id': events_list[-1]['event_id'],
        'start_time': events_list[0]['event_running_start'],
        'end_time': events_list[-1]['event_running_start'],
        'duration_seconds': events_list[-1]['event_running_start'] - events_list[0]['event_running_start'],
        'ended_with': end_type,
        'ended_with_shot': 1 if end_type in ['shot', 'goal'] else 0,
        'ended_with_goal': 1 if end_type == 'goal' else 0,
        'event_ids': ','.join(event_ids),
        'player_ids': ','.join([str(p) for p in player_ids])
    }


def enhance_derived_event_tables(output_dir: Path, log):
    """Add FKs to tables derived from events (chains, tracking, linked, etc.).

    Args:
        output_dir: Path to output directory
        log: ETLLogger instance
    """
    log.section("PHASE 5.6: ENHANCE DERIVED EVENT TABLES")

    # Load fact_events with new FKs for lookup
    events = safe_read_csv(output_dir / 'fact_events.csv')
    tracking = safe_read_csv(output_dir / 'fact_event_players.csv')

    # Create lookup maps from events
    event_fks = ['season_id', 'time_bucket_id', 'strength_id', 'shot_type_id',
                 'zone_entry_type_id', 'zone_exit_type_id', 'position_id']

    event_lookup = {}
    for col in event_fks:
        if col in events.columns:
            event_lookup[col] = dict(zip(events['event_id'], events[col]))

    # Also create lookup by tracking_event_key
    tracking_lookup = {}
    tracking_first = tracking.groupby('tracking_event_key').first().reset_index()
    for col in event_fks:
        if col in tracking_first.columns:
            tracking_lookup[col] = dict(zip(tracking_first['tracking_event_key'], tracking_first[col]))

    # 1. Enhance fact_player_event_chains
    log.info("Enhancing fact_player_event_chains...")
    pec_path = output_dir / 'fact_player_event_chains.csv'
    if pec_path.exists():
        pec = safe_read_csv(pec_path)

        # Skip if empty or missing event_key
        if len(pec) > 0 and 'event_key' in pec.columns:
            # Add FKs via event_key
            for col in ['season_id', 'time_bucket_id', 'strength_id']:
                if col in event_lookup:
                    pec[col] = pec['event_key'].map(event_lookup[col])

            save_output_table(pec, 'fact_player_event_chains', output_dir)
            log.info(f"  fact_player_event_chains: {len(pec)} rows, {len(pec.columns)} cols")
        else:
            log.info(f"  - fact_player_event_chains: skipped (empty or no event_key)")

    # 2. Enhance fact_tracking
    log.info("Enhancing fact_tracking...")
    ft_path = output_dir / 'fact_tracking.csv'
    if ft_path.exists():
        ft = safe_read_csv(ft_path)

        # Add FKs via tracking_event_key
        for col in ['season_id', 'time_bucket_id', 'strength_id']:
            if col in tracking_lookup:
                ft[col] = ft['tracking_event_key'].map(tracking_lookup[col])

        save_output_table(ft, 'fact_tracking', output_dir)
        log.info(f"  fact_tracking: {len(ft)} rows, {len(ft.columns)} cols")

    # NOTE: fact_shot_chains, fact_linked_events, fact_scoring_chances, fact_rush_events
    # are created later in Phase 4D/4E by event_analytics.py and shot_chain_builder.py
    # No enhancement needed here.

    # 3. Build fact_cycle_events with zone inference
    log.info("Building fact_cycle_events with zone inference...")
    _build_cycle_events(tracking, events, output_dir, log)

    log.info("  Done enhancing derived tables")


def enhance_events_with_flags(output_dir: Path, log, save_table_func=None):
    """Add time columns, flags, and derived keys to fact_events.

    Args:
        output_dir: Path to output directory
        log: ETLLogger instance
        save_table_func: Function to save tables (optional, uses save_output_table if not provided)
    """
    log.section("PHASE 5.9: ENHANCE EVENTS WITH FLAGS")

    if save_table_func is None:
        save_table_func = lambda df, name: save_output_table(df, name, output_dir)

    events_path = output_dir / 'fact_events.csv'
    tracking_path = output_dir / 'fact_event_players.csv'

    if not events_path.exists():
        log.warn("fact_events not found, skipping enhancement")
        return

    events = safe_read_csv(events_path)
    tracking = safe_read_csv(tracking_path)

    # Get first row per event for time/context
    first_per_event = tracking[tracking['player_role'] == 'event_player_1'].copy()
    first_per_event = first_per_event.drop_duplicates(subset='event_id', keep='first')

    log.info(f"Enhancing {len(events)} events...")

    # Add time columns
    time_cols = ['event_start_min', 'event_start_sec', 'event_end_min', 'event_end_sec',
                 'running_video_time', 'event_running_start', 'event_running_end']
    for col in time_cols:
        if col in first_per_event.columns and col not in events.columns:
            events[col] = events['event_id'].map(dict(zip(first_per_event['event_id'], first_per_event[col])))

    # Add play_detail1
    if 'play_detail1' in first_per_event.columns:
        events['play_detail1'] = events['event_id'].map(dict(zip(first_per_event['event_id'], first_per_event['play_detail1'])))

    # Create flags
    events['is_rebound'] = (events['event_type'] == 'Rebound').astype(int)
    # is_cycle is set by _build_cycle_events based on cycle_key - preserve if already set
    if 'cycle_key' in events.columns:
        events['is_cycle'] = events['cycle_key'].notna().astype(int)
    else:
        events['is_cycle'] = (events['event_detail'].str.contains('Cycle', na=False) | events['event_detail_2'].str.contains('Cycle', na=False)).astype(int)
    # Breakout = successful zone exit (exiting defensive zone with puck control)
    # Using event_detail='Zone_Exit' as primary indicator - covers all games consistently
    # NOTE: Some games also have play_detail1 'Breakout' annotations, but this is inconsistent
    # Legacy logic (inconsistent across games): events['event_detail'].str.contains('Breakout', na=False) | events['play_detail1'].str.contains('Breakout', na=False, case=False)
    # Zone entry = successful zone entries only (exclude Zone_Entry_Failed)
    events['is_zone_entry'] = (events['event_detail'] == 'Zone_Entry').astype(int)
    # Zone exit = successful zone exits only (exclude Zone_Exit_Failed)
    events['is_zone_exit'] = (events['event_detail'] == 'Zone_Exit').astype(int)

    # is_controlled_entry: Zone entry with puck control (not dump-in)
    # Dynamically lookup from dim_zone_entry_type - NO HARDCODED IDs
    ze_type_path = output_dir / 'dim_zone_entry_type.csv'
    if not ze_type_path.exists():
        raise FileNotFoundError(f"dim_zone_entry_type.csv not found - must run dim table creation first")

    ze_types = safe_read_csv(ze_type_path)
    controlled_entry_ids = ze_types[ze_types['is_controlled'] == True]['zone_entry_type_id'].tolist()
    carried_entry_ids = ze_types[ze_types['zone_entry_type_name'].str.contains('Carried', na=False)]['zone_entry_type_id'].tolist()

    events['is_controlled_entry'] = (
        (events['is_zone_entry'] == 1) &
        (events['zone_entry_type_id'].isin(controlled_entry_ids))
    ).astype(int)

    # is_carried_entry: Carried in (subset of controlled, excludes pass-in)
    events['is_carried_entry'] = (
        (events['is_zone_entry'] == 1) &
        (events['zone_entry_type_id'].isin(carried_entry_ids))
    ).astype(int)

    # is_controlled_exit: Zone exit with puck control
    # Dynamically lookup from dim_zone_exit_type - NO HARDCODED IDs
    zx_type_path = output_dir / 'dim_zone_exit_type.csv'
    if not zx_type_path.exists():
        raise FileNotFoundError(f"dim_zone_exit_type.csv not found - must run dim table creation first")

    zx_types = safe_read_csv(zx_type_path)
    controlled_exit_ids = zx_types[zx_types['is_controlled'] == True]['zone_exit_type_id'].tolist()
    carried_exit_ids = zx_types[zx_types['zone_exit_type_name'].str.contains('Carried', na=False)]['zone_exit_type_id'].tolist()

    events['is_controlled_exit'] = (
        (events['is_zone_exit'] == 1) &
        (events['zone_exit_type_id'].isin(controlled_exit_ids))
    ).astype(int)

    # is_carried_exit: Carried out (subset of controlled)
    events['is_carried_exit'] = (
        (events['is_zone_exit'] == 1) &
        (events['zone_exit_type_id'].isin(carried_exit_ids))
    ).astype(int)

    # is_rush: Will be populated later as NHL true rush (controlled entry + shot ≤7s)
    # Initialize to 0, will be set in context columns section
    events['is_rush'] = 0

    # Goal = event_type='Goal' AND event_detail='Goal_Scored'
    # Shot_Goal is just the shot that resulted in a goal, not the goal itself
    # Faceoff_AfterGoal is the faceoff after a goal, not a goal
    events['is_goal'] = ((events['event_type'] == 'Goal') & (events['event_detail'] == 'Goal_Scored')).astype(int)
    events['is_save'] = events['event_detail'].str.startswith('Save', na=False).astype(int)
    # Shots on goal (SOG) = shots that reached the goalie (saved or scored)
    # EXCLUDES Goal_Scored to avoid double-counting (Shot_Goal + Goal_Scored are linked events)
    # Only count the shot event (Shot_Goal), not the goal event (Goal_Scored)
    events['is_sog'] = ((events['event_type'] == 'Shot') &
                        events['event_detail'].isin(['Shot_OnNetSaved', 'Shot_OnNet', 'Shot_Goal'])).astype(int)
    events['is_turnover'] = (events['event_type'] == 'Turnover').astype(int)
    events['is_giveaway'] = events['giveaway_type_id'].notna().astype(int)
    # Bad giveaways = misplays/turnovers that hurt the team (not neutral like dumps, battles, shots)
    bad_giveaway_types = [
        'Giveaway_Misplayed', 'Giveaway_PassBlocked', 'Giveaway_PassIntercepted',
        'Giveaway_PassMissed', 'Giveaway_PassReceiverMissed', 'Giveaway_ZoneEntry_ExitMisplay',
        'Giveaway_ZoneEntry/ExitMisplay',  # handle both formats
    ]
    events['is_bad_giveaway'] = ((events['is_giveaway'] == 1) &
                                  events['event_detail_2'].isin(bad_giveaway_types)).astype(int)
    events['is_takeaway'] = events['takeaway_type_id'].notna().astype(int)
    events['is_faceoff'] = (events['event_type'] == 'Faceoff').astype(int)
    events['is_penalty'] = (events['event_type'] == 'Penalty').astype(int)
    events['is_blocked_shot'] = events['event_detail'].str.contains('Blocked', na=False).astype(int)

    # Add shooter, shot_blocker, and goalie columns for shot events
    log.info("  Adding shooter, shot_blocker, and goalie columns for shot events...")

    # Filter to shot events (Shot or Goal event_type)
    shot_mask = events['event_type'].isin(['Shot', 'Goal'])

    # Initialize columns
    events['shooter_player_id'] = None
    events['shooter_name'] = None
    events['shooter_rating'] = None
    events['shot_blocker_player_id'] = None
    events['shot_blocker_name'] = None
    events['shot_blocker_rating'] = None
    events['goalie_player_id'] = None
    events['goalie_name'] = None
    events['goalie_rating'] = None

    if shot_mask.any():
        # Get event_player_1 data for shots (shooter)
        shot_event_ids = events[shot_mask]['event_id'].tolist()
        shooter_data = tracking[
            (tracking['event_id'].isin(shot_event_ids)) &
            (tracking['player_role'].astype(str).str.lower() == 'event_player_1')
        ].drop_duplicates(subset='event_id', keep='first')

        # Map shooter info (always from event_player_1 for shots)
        shooter_map_id = dict(zip(shooter_data['event_id'], shooter_data['player_id']))
        shooter_map_name = dict(zip(shooter_data['event_id'], shooter_data.get('player_name', shooter_data.get('player_full_name', None))))
        shooter_map_rating = dict(zip(shooter_data['event_id'], shooter_data.get('player_rating', None)))

        events.loc[shot_mask, 'shooter_player_id'] = events.loc[shot_mask, 'event_id'].map(shooter_map_id)
        events.loc[shot_mask, 'shooter_name'] = events.loc[shot_mask, 'event_id'].map(shooter_map_name)
        events.loc[shot_mask, 'shooter_rating'] = events.loc[shot_mask, 'event_id'].map(shooter_map_rating)

        # Get shot blocker info (opp_player_1 for blocked shots)
        blocked_mask = shot_mask & (events['is_blocked_shot'] == 1)
        if blocked_mask.any():
            blocked_event_ids = events[blocked_mask]['event_id'].tolist()
            blocker_data = tracking[
                (tracking['event_id'].isin(blocked_event_ids)) &
                (tracking['player_role'].astype(str).str.lower() == 'opp_player_1')
            ].drop_duplicates(subset='event_id', keep='first')

            blocker_map_id = dict(zip(blocker_data['event_id'], blocker_data['player_id']))
            blocker_map_name = dict(zip(blocker_data['event_id'], blocker_data.get('player_name', blocker_data.get('player_full_name', None))))
            blocker_map_rating = dict(zip(blocker_data['event_id'], blocker_data.get('player_rating', None)))

            events.loc[blocked_mask, 'shot_blocker_player_id'] = events.loc[blocked_mask, 'event_id'].map(blocker_map_id)
            events.loc[blocked_mask, 'shot_blocker_name'] = events.loc[blocked_mask, 'event_id'].map(blocker_map_name)
            events.loc[blocked_mask, 'shot_blocker_rating'] = events.loc[blocked_mask, 'event_id'].map(blocker_map_rating)

        # Get goalie info for shots that resulted in saves or goals
        # For shots that were saved (Shot_OnNetSaved): need to find the corresponding Save event
        # For shots that were goals (Shot_Goal): opp_player_1 is the goalie who allowed the goal
        # For actual Save events (event_type='Save'): event_player_1 is the goalie

        # Shots that were saved (is_sog but not goal) - goalie is on defending team (opp_player_1)
        saved_shot_mask = shot_mask & (events['is_sog'] == 1) & (events['is_goal'] == 0)
        if saved_shot_mask.any():
            saved_shot_event_ids = events[saved_shot_mask]['event_id'].tolist()
            goalie_saved_data = tracking[
                (tracking['event_id'].isin(saved_shot_event_ids)) &
                (tracking['player_role'].astype(str).str.lower() == 'opp_player_1')
            ].drop_duplicates(subset='event_id', keep='first')

            goalie_saved_map_id = dict(zip(goalie_saved_data['event_id'], goalie_saved_data['player_id']))
            goalie_saved_map_name = dict(zip(goalie_saved_data['event_id'], goalie_saved_data.get('player_name', goalie_saved_data.get('player_full_name', None))))
            goalie_saved_map_rating = dict(zip(goalie_saved_data['event_id'], goalie_saved_data.get('player_rating', None)))

            events.loc[saved_shot_mask, 'goalie_player_id'] = events.loc[saved_shot_mask, 'event_id'].map(goalie_saved_map_id)
            events.loc[saved_shot_mask, 'goalie_name'] = events.loc[saved_shot_mask, 'event_id'].map(goalie_saved_map_name)
            events.loc[saved_shot_mask, 'goalie_rating'] = events.loc[saved_shot_mask, 'event_id'].map(goalie_saved_map_rating)

        # Goals: opp_player_1 is the goalie who allowed the goal
        goal_mask = shot_mask & (events['is_goal'] == 1)
        if goal_mask.any():
            goal_event_ids = events[goal_mask]['event_id'].tolist()
            goalie_goal_data = tracking[
                (tracking['event_id'].isin(goal_event_ids)) &
                (tracking['player_role'].astype(str).str.lower() == 'opp_player_1')
            ].drop_duplicates(subset='event_id', keep='first')

            goalie_goal_map_id = dict(zip(goalie_goal_data['event_id'], goalie_goal_data['player_id']))
            goalie_goal_map_name = dict(zip(goalie_goal_data['event_id'], goalie_goal_data.get('player_name', goalie_goal_data.get('player_full_name', None))))
            goalie_goal_map_rating = dict(zip(goalie_goal_data['event_id'], goalie_goal_data.get('player_rating', None)))

            events.loc[goal_mask, 'goalie_player_id'] = events.loc[goal_mask, 'event_id'].map(goalie_goal_map_id)
            events.loc[goal_mask, 'goalie_name'] = events.loc[goal_mask, 'event_id'].map(goalie_goal_map_name)
            events.loc[goal_mask, 'goalie_rating'] = events.loc[goal_mask, 'event_id'].map(goalie_goal_map_rating)

        shot_count = shot_mask.sum()
        blocked_count = blocked_mask.sum() if blocked_mask.any() else 0
        saved_count = saved_shot_mask.sum() if saved_shot_mask.any() else 0
        goal_count = goal_mask.sum() if goal_mask.any() else 0
        log.info(f"    Added shooter/goalie/blocker info: {shot_count} shots ({blocked_count} blocked, {saved_count} saved, {goal_count} goals)")
    events['is_missed_shot'] = events['event_detail'].isin(['Shot_Missed', 'Shot_MissedPost']).astype(int)
    events['is_deflected'] = (events['event_detail'] == 'Shot_Deflected').astype(int)
    # Tipped shots (from event_detail_2)
    events['is_tipped'] = events['event_detail_2'].isin(['Shot_Tip', 'Shot_Tipped', 'Goal_Tip']).astype(int)
    # is_sog was already created earlier (before shooter/goalie columns)
    # Corsi = all shot attempts (SOG + blocked + missed)
    events['is_corsi'] = ((events['is_sog'] == 1) |
                          (events['is_blocked_shot'] == 1) |
                          (events['is_missed_shot'] == 1)).astype(int)
    # Fenwick = unblocked shot attempts (SOG + missed, excludes blocked)
    events['is_fenwick'] = ((events['is_sog'] == 1) |
                            (events['is_missed_shot'] == 1)).astype(int)

    # shot_outcome_id - maps event_detail to dim_shot_outcome
    shot_outcome_map = {
        'Goal_Scored': 'SO01', 'Shot_Goal': 'SO01',  # goal
        'Shot_OnNetSaved': 'SO02', 'Shot_OnNet': 'SO02',  # saved
        'Shot_Blocked': 'SO03', 'Shot_BlockedSameTeam': 'SO03',  # blocked
        'Shot_Missed': 'SO04', 'Shot_MissedPost': 'SO04',  # missed
        'Shot_Deflected': 'SO05',  # deflected
    }
    events['shot_outcome_id'] = events['event_detail'].map(shot_outcome_map)

    # pass_outcome_id - maps event_detail to dim_pass_outcome
    pass_outcome_map = {
        'Pass_Completed': 'PO01',
        'Pass_Missed': 'PO02',
        'Pass_Deflected': 'PO03',
        'Pass_Intercepted': 'PO04',
    }
    events['pass_outcome_id'] = events['event_detail'].map(pass_outcome_map)

    # save_outcome_id - maps event_detail to dim_save_outcome
    save_outcome_map = {
        'Save_Rebound': 'SV01',
        'Save_Freeze': 'SV02',
        'Save_Played': 'SV03',
    }
    events['save_outcome_id'] = events['event_detail'].map(save_outcome_map)

    # zone_outcome_id - maps event_detail to dim_zone_outcome
    # Note: Values must match actual event_detail values in tracker data
    zone_outcome_map = {
        'Zone_Entry': 'ZO01',
        'Zone_Entry_Failed': 'ZO02',
        'Zone_Exit': 'ZO03',
        'Zone_Exit_Failed': 'ZO04',
        'Zone_Keepin': 'ZO05',
        'Zone_Keepin_Failed': 'ZO06',
    }
    events['zone_outcome_id'] = events['event_detail'].map(zone_outcome_map)

    # is_scoring_chance and is_high_danger: DEFERRED - needs XY data for proper implementation
    # Placeholder: using is_sog | is_goal until XY-based logic is implemented
    events['is_scoring_chance'] = ((events['is_sog'] == 1) | (events['is_goal'] == 1)).astype(int)
    events['is_high_danger'] = (((events['is_sog'] == 1) | (events['is_goal'] == 1)) & (
        (events['is_rebound'] == 1) | events['event_detail_2'].str.contains('Tip|OneTime|Deflect', na=False))).astype(int)

    # Pressure
    if 'pressured_pressurer' in first_per_event.columns:
        events['pressured_pressurer'] = events['event_id'].map(dict(zip(first_per_event['event_id'], first_per_event['pressured_pressurer'])))
        events['is_pressured'] = (events['pressured_pressurer'] == 1).astype(int)

    # Danger level
    def calc_danger(row):
        if row['is_sog'] != 1 and row['is_goal'] != 1:
            return None
        if row['is_high_danger'] == 1:
            return 'high'
        if row['is_rush'] == 1 or row['event_team_zone'] == 'o':
            return 'medium'
        return 'low'
    events['danger_level'] = events.apply(calc_danger, axis=1)
    events['danger_level_id'] = events['danger_level'].map({'high': 'DL01', 'medium': 'DL02', 'low': 'DL03'})

    # Scoring chance key
    sc_events = events[(events['is_sog'] == 1) | (events['is_goal'] == 1)].copy()
    sc_events = sc_events.reset_index(drop=True)
    sc_events['scoring_chance_key'] = 'SC' + sc_events['game_id'].astype(str) + sc_events.index.astype(str).str.zfill(4)
    events['scoring_chance_key'] = events['event_id'].map(dict(zip(sc_events['event_id'], sc_events['scoring_chance_key'])))

    # ==========================================================================
    # CONTEXT COLUMNS - Previous/Next Event Relationships
    # ==========================================================================
    log.info("  Adding context columns...")

    # Sort by game and time (descending time = ascending chronological order for countdown clock)
    events = events.sort_values(['game_id', 'time_start_total_seconds'], ascending=[True, False]).reset_index(drop=True)

    # Initialize all context columns
    context_cols = [
        # Basic prev/next
        'prev_event_id', 'prev_event_type', 'prev_event_detail', 'prev_event_team', 'prev_event_same_team',
        'next_event_id', 'next_event_type', 'next_event_detail', 'next_event_team', 'next_event_same_team',
        'time_since_prev', 'time_to_next',
        # Shot context
        'time_to_next_sog', 'time_since_last_sog', 'events_to_next_sog', 'events_since_last_sog',
        'next_sog_result', 'led_to_sog', 'is_pre_shot_event', 'is_shot_assist',
        # Goal context
        'time_to_next_goal', 'time_since_last_goal', 'events_to_next_goal', 'events_since_last_goal', 'led_to_goal',
        # Zone context
        'time_since_zone_entry', 'events_since_zone_entry', 'time_since_zone_exit',
        # Sequence context
        'sequence_event_num', 'sequence_total_events', 'sequence_duration',
        'is_sequence_first', 'is_sequence_last', 'sequence_has_sog', 'sequence_has_goal', 'sequence_shot_count',
        # Possession context
        'consecutive_team_events', 'time_since_possession_change', 'events_since_possession_change',
        # Faceoff context
        'time_since_faceoff', 'events_since_faceoff',
        # Rush calculated
        'is_rush_calculated', 'time_from_entry_to_shot',
    ]
    for col in context_cols:
        events[col] = None

    # Process each game
    for game_id in events['game_id'].unique():
        game_mask = events['game_id'] == game_id
        game_idx = events[game_mask].index.tolist()

        if len(game_idx) < 2:
            continue

        # Get game events in chronological order (higher time_start = earlier in countdown)
        game_events = events.loc[game_idx].copy()

        # Track last seen events for lookback
        last_sog_idx = None
        last_sog_time = None
        last_goal_idx = None
        last_goal_time = None
        last_zone_entry_idx = None
        last_zone_entry_time = None
        last_zone_exit_idx = None
        last_zone_exit_time = None
        last_faceoff_idx = None
        last_faceoff_time = None
        last_possession_change_idx = None
        last_possession_change_time = None
        consecutive_team_count = 0
        prev_team = None

        # Forward pass - looking back at previous events
        for i, idx in enumerate(game_idx):
            row = events.loc[idx]
            curr_time = row['time_start_total_seconds']
            curr_team = row.get('player_team')

            # Previous event (i-1 in game_idx)
            if i > 0:
                prev_idx = game_idx[i - 1]
                prev_row = events.loc[prev_idx]
                events.at[idx, 'prev_event_id'] = prev_row['event_id']
                events.at[idx, 'prev_event_type'] = prev_row['event_type']
                events.at[idx, 'prev_event_detail'] = prev_row['event_detail']
                events.at[idx, 'prev_event_team'] = prev_row.get('player_team')
                events.at[idx, 'prev_event_same_team'] = 1 if prev_row.get('player_team') == curr_team else 0
                prev_time = prev_row['time_start_total_seconds']
                if pd.notna(curr_time) and pd.notna(prev_time):
                    events.at[idx, 'time_since_prev'] = prev_time - curr_time  # Countdown: prev > curr

            # Next event (i+1 in game_idx)
            if i < len(game_idx) - 1:
                next_idx = game_idx[i + 1]
                next_row = events.loc[next_idx]
                events.at[idx, 'next_event_id'] = next_row['event_id']
                events.at[idx, 'next_event_type'] = next_row['event_type']
                events.at[idx, 'next_event_detail'] = next_row['event_detail']
                events.at[idx, 'next_event_team'] = next_row.get('player_team')
                events.at[idx, 'next_event_same_team'] = 1 if next_row.get('player_team') == curr_team else 0
                next_time = next_row['time_start_total_seconds']
                if pd.notna(curr_time) and pd.notna(next_time):
                    events.at[idx, 'time_to_next'] = curr_time - next_time  # Countdown: curr > next

            # Time/events since last SOG
            if last_sog_idx is not None and pd.notna(curr_time) and pd.notna(last_sog_time):
                events.at[idx, 'time_since_last_sog'] = last_sog_time - curr_time
                events.at[idx, 'events_since_last_sog'] = i - game_idx.index(last_sog_idx)

            # Time/events since last goal
            if last_goal_idx is not None and pd.notna(curr_time) and pd.notna(last_goal_time):
                events.at[idx, 'time_since_last_goal'] = last_goal_time - curr_time
                events.at[idx, 'events_since_last_goal'] = i - game_idx.index(last_goal_idx)

            # Time/events since zone entry
            if last_zone_entry_idx is not None and pd.notna(curr_time) and pd.notna(last_zone_entry_time):
                events.at[idx, 'time_since_zone_entry'] = last_zone_entry_time - curr_time
                events.at[idx, 'events_since_zone_entry'] = i - game_idx.index(last_zone_entry_idx)

            # Time since zone exit
            if last_zone_exit_idx is not None and pd.notna(curr_time) and pd.notna(last_zone_exit_time):
                events.at[idx, 'time_since_zone_exit'] = last_zone_exit_time - curr_time

            # Time/events since faceoff
            if last_faceoff_idx is not None and pd.notna(curr_time) and pd.notna(last_faceoff_time):
                events.at[idx, 'time_since_faceoff'] = last_faceoff_time - curr_time
                events.at[idx, 'events_since_faceoff'] = i - game_idx.index(last_faceoff_idx)

            # Time/events since possession change
            if last_possession_change_idx is not None and pd.notna(curr_time) and pd.notna(last_possession_change_time):
                events.at[idx, 'time_since_possession_change'] = last_possession_change_time - curr_time
                events.at[idx, 'events_since_possession_change'] = i - game_idx.index(last_possession_change_idx)

            # Consecutive team events
            if curr_team == prev_team and pd.notna(curr_team):
                consecutive_team_count += 1
            else:
                consecutive_team_count = 1
            events.at[idx, 'consecutive_team_events'] = consecutive_team_count
            prev_team = curr_team

            # Update trackers
            if row.get('is_sog') == 1:
                last_sog_idx = idx
                last_sog_time = curr_time
            if row.get('is_goal') == 1:
                last_goal_idx = idx
                last_goal_time = curr_time
            if row.get('is_zone_entry') == 1:
                last_zone_entry_idx = idx
                last_zone_entry_time = curr_time
            if row.get('is_zone_exit') == 1:
                last_zone_exit_idx = idx
                last_zone_exit_time = curr_time
            if row.get('is_faceoff') == 1:
                last_faceoff_idx = idx
                last_faceoff_time = curr_time
            if row.get('is_turnover') == 1 or row.get('is_faceoff') == 1:
                last_possession_change_idx = idx
                last_possession_change_time = curr_time

        # Reverse pass - looking forward at next events (for time_to_next_sog, etc.)
        next_sog_idx = None
        next_sog_time = None
        next_sog_detail = None
        next_goal_idx = None
        next_goal_time = None

        for i in range(len(game_idx) - 1, -1, -1):
            idx = game_idx[i]
            row = events.loc[idx]
            curr_time = row['time_start_total_seconds']

            # Time/events to next SOG
            if next_sog_idx is not None and pd.notna(curr_time) and pd.notna(next_sog_time):
                events.at[idx, 'time_to_next_sog'] = curr_time - next_sog_time
                events_to_sog = game_idx.index(next_sog_idx) - i
                events.at[idx, 'events_to_next_sog'] = events_to_sog
                events.at[idx, 'next_sog_result'] = 'goal' if 'Goal' in str(next_sog_detail) else 'save'

                # Check if event led to SOG within same play (same team possession)
                curr_play_key = row.get('play_key')
                next_sog_play_key = events.loc[next_sog_idx].get('play_key')
                same_play = (pd.notna(curr_play_key) and curr_play_key == next_sog_play_key)

                if same_play:
                    events.at[idx, 'led_to_sog'] = 1

                    # Count passes between current event and shot (within same play)
                    # Check if current event is a pass
                    is_pass = row.get('event_type') == 'Pass'

                    # Count how many passes are between this event and the shot
                    pass_count = 0
                    if is_pass and events_to_sog > 0:
                        # Count passes in the events between current and shot
                        for j in range(i + 1, game_idx.index(next_sog_idx)):
                            if j < len(game_idx):
                                intermediate_idx = game_idx[j]
                                intermediate_event = events.loc[intermediate_idx]
                                # Only count if same play
                                if intermediate_event.get('play_key') == curr_play_key:
                                    if intermediate_event.get('event_type') == 'Pass':
                                        pass_count += 1

                    # is_pre_shot_event: Any event within 3 events before shot in same play
                    if events_to_sog <= 3:
                        events.at[idx, 'is_pre_shot_event'] = 1

                    # is_shot_assist: Pass event within same play, in offensive zone,
                    # with up to 3 passes before shot on goal
                    if is_pass:
                        # Check if in offensive zone (O, Offensive, oz, etc.)
                        event_zone = str(row.get('event_team_zone', '')).lower()
                        is_offensive_zone = (
                            event_zone.startswith('o') or
                            'offensive' in event_zone or
                            event_zone == 'oz'
                        )

                        # Shot assist: pass in offensive zone, same play,
                        # with <= 3 passes (including self) before shot on goal
                        total_passes_to_shot = pass_count + 1  # +1 for current pass
                        if is_offensive_zone and total_passes_to_shot <= 3:
                            events.at[idx, 'is_shot_assist'] = 1

            # Time/events to next goal
            if next_goal_idx is not None and pd.notna(curr_time) and pd.notna(next_goal_time):
                events.at[idx, 'time_to_next_goal'] = curr_time - next_goal_time
                events.at[idx, 'events_to_next_goal'] = game_idx.index(next_goal_idx) - i
                if row.get('sequence_key') == events.loc[next_goal_idx].get('sequence_key'):
                    events.at[idx, 'led_to_goal'] = 1

            # Update trackers (looking backward in time = forward in game)
            if row.get('is_sog') == 1:
                next_sog_idx = idx
                next_sog_time = curr_time
                next_sog_detail = row.get('event_detail')
            if row.get('is_goal') == 1:
                next_goal_idx = idx
                next_goal_time = curr_time

    # Sequence context - aggregate per sequence
    if 'sequence_key' in events.columns:
        seq_stats = events.groupby('sequence_key').agg({
            'event_id': 'count',
            'time_start_total_seconds': ['max', 'min'],
            'is_sog': 'sum',
            'is_goal': 'sum',
        }).reset_index()
        seq_stats.columns = ['sequence_key', 'seq_event_count', 'seq_time_max', 'seq_time_min', 'seq_sog_count', 'seq_goal_count']
        seq_stats['seq_duration'] = seq_stats['seq_time_max'] - seq_stats['seq_time_min']
        seq_stats['seq_has_sog'] = (seq_stats['seq_sog_count'] > 0).astype(int)
        seq_stats['seq_has_goal'] = (seq_stats['seq_goal_count'] > 0).astype(int)

        # Map to events
        seq_map = seq_stats.set_index('sequence_key').to_dict()
        events['sequence_total_events'] = events['sequence_key'].map(seq_map['seq_event_count'])
        events['sequence_duration'] = events['sequence_key'].map(seq_map['seq_duration'])
        events['sequence_has_sog'] = events['sequence_key'].map(seq_map['seq_has_sog'])
        events['sequence_has_goal'] = events['sequence_key'].map(seq_map['seq_has_goal'])
        events['sequence_shot_count'] = events['sequence_key'].map(seq_map['seq_sog_count'])

        # Event position within sequence
        events['sequence_event_num'] = events.groupby('sequence_key').cumcount() + 1
        events['is_sequence_first'] = (events['sequence_event_num'] == 1).astype(int)
        events['is_sequence_last'] = (events['sequence_event_num'] == events['sequence_total_events']).astype(int)

    # Rush calculation:
    # is_rush_calculated: zone entry -> SOG within 10 seconds and <=5 events (any entry type)
    # is_rush: NHL definition - controlled entry + shot within 7 seconds (true transition attack)
    zone_entries = events[events['is_zone_entry'] == 1].index
    for idx in zone_entries:
        time_to_sog = events.at[idx, 'time_to_next_sog']
        events_to_sog = events.at[idx, 'events_to_next_sog']
        is_controlled = events.at[idx, 'is_controlled_entry'] == 1

        if pd.notna(time_to_sog) and pd.notna(events_to_sog):
            # Calculated rush: <=10s AND <=5 events (any entry type)
            if time_to_sog <= 10 and events_to_sog <= 5:
                events.at[idx, 'is_rush_calculated'] = 1
                events.at[idx, 'time_from_entry_to_shot'] = time_to_sog

            # is_rush (NHL definition): controlled entry + shot within 7 seconds
            # This is the "attack before defense sets up" definition
            if is_controlled and time_to_sog <= 7:
                events.at[idx, 'is_rush'] = 1

    # Fill NaN with 0 for binary flags
    binary_flags = ['prev_event_same_team', 'next_event_same_team', 'led_to_sog', 'is_pre_shot_event',
                    'is_shot_assist', 'led_to_goal', 'is_sequence_first', 'is_sequence_last',
                    'sequence_has_sog', 'sequence_has_goal', 'is_rush_calculated', 'is_rush',
                    'is_controlled_entry', 'is_carried_entry', 'is_controlled_exit', 'is_carried_exit']
    for col in binary_flags:
        if col in events.columns:
            events[col] = events[col].fillna(0).astype(int)

    log.info(f"    Context columns added: {len(context_cols)}")

    # Add segment numbers for events that are part of plays, sequences, chains, etc.
    log.info("  Adding segment numbers for plays, sequences, chains, and linked events...")

    # Initialize segment number columns
    events['play_segment_number'] = None
    events['sequence_segment_number'] = None
    events['linked_event_segment_number'] = None

    # Sort events by game and time to ensure proper ordering
    events = events.sort_values(['game_id', 'time_start_total_seconds', 'event_id'])

    # Use event_id as key for mapping (more reliable than DataFrame index)
    if 'event_id' not in events.columns:
        log.warning("    event_id column not found, skipping segment number calculation")
    else:
        # 1. Play segment number (position within play_key)
        if 'play_key' in events.columns:
            play_segments = {}
            for play_key, grp in events.groupby('play_key'):
                if pd.notna(play_key):
                    grp_sorted = grp.sort_values(['time_start_total_seconds', 'event_id'])
                    for i, event_id in enumerate(grp_sorted['event_id'], 1):
                        play_segments[event_id] = i
            events['play_segment_number'] = events['event_id'].map(play_segments)
            play_count = events['play_segment_number'].notna().sum()
            log.info(f"    play_segment_number: {play_count} events have positions")

        # 2. Sequence segment number (position within sequence_key)
        if 'sequence_key' in events.columns:
            sequence_segments = {}
            for seq_key, grp in events.groupby('sequence_key'):
                if pd.notna(seq_key):
                    grp_sorted = grp.sort_values(['time_start_total_seconds', 'event_id'])
                    for i, event_id in enumerate(grp_sorted['event_id'], 1):
                        sequence_segments[event_id] = i
            events['sequence_segment_number'] = events['event_id'].map(sequence_segments)
            seq_count = events['sequence_segment_number'].notna().sum()
            log.info(f"    sequence_segment_number: {seq_count} events have positions")

        # 3. Linked event segment number (position within linked_event_key)
        # Check for linked_event_key or linked_event_index
        linked_key_col = None
        if 'linked_event_key' in events.columns:
            linked_key_col = 'linked_event_key'
        elif 'linked_event_index' in events.columns:
            # Generate linked_event_key from linked_event_index if needed
            events['linked_event_key'] = events.apply(
                lambda row: f"LK{int(row['game_id']):05d}{int(row['linked_event_index']):05d}"
                if pd.notna(row.get('linked_event_index')) and pd.notna(row.get('game_id'))
                else None, axis=1
            )
            linked_key_col = 'linked_event_key'

        if linked_key_col:
            linked_segments = {}
            for linked_key, grp in events.groupby(linked_key_col):
                if pd.notna(linked_key):
                    grp_sorted = grp.sort_values(['time_start_total_seconds', 'event_id'])
                    for i, event_id in enumerate(grp_sorted['event_id'], 1):
                        linked_segments[event_id] = i
            events['linked_event_segment_number'] = events['event_id'].map(linked_segments)
            linked_count = events['linked_event_segment_number'].notna().sum()
            log.info(f"    linked_event_segment_number: {linked_count} events have positions")

    save_table_func(events, 'fact_events')
    log.info(f"  fact_events: {len(events)} rows, {len(events.columns)} cols")
    log.info(f"    Flags: rush={events['is_rush'].sum()}, controlled_entry={events['is_controlled_entry'].sum()}, carried_entry={events['is_carried_entry'].sum()}, sog={events['is_sog'].sum()}")
