"""
Derived Columns Calculator
==========================

Calculate derived columns from minimal input data.
Makes ETL robust for test data and tracker exports.

This module handles:
- Time columns (duration, running times, total seconds)
- Zone columns (home_team_zone, away_team_zone)
- Team columns (team_venue, team_venue_abv, player_team)
- Player role columns (role_number, role_abrev, side_of_puck)
- Strength calculation
- Play detail columns
- Pressure calculation from XY distance
"""

import pandas as pd


def calculate_derived_columns(df, log):
    """
    Calculate derived columns from minimal input data.
    Makes ETL robust for test data and tracker exports.

    IMPORTANT: This function fills in NaN values for rows that are missing data,
    even if other rows in the column have values. This handles the case where
    some games (real data) have full columns while other games (test data) don't.

    Calculates:
    - Time columns (duration, running times, total seconds)
    - Zone columns (home_team_zone, away_team_zone)
    - Team columns (team_venue, team_venue_abv, player_team)
    - Player role columns (role_number, role_abrev, side_of_puck)
    - Shift linkage (shift_index from time matching)

    Args:
        df: DataFrame to process
        log: Logger instance

    Returns:
        DataFrame with derived columns added
    """
    log.info("  Calculating derived columns from minimal input...")
    calculated = []

    # ================================================================
    # 1. TIME COLUMNS
    # ================================================================

    # Ensure time columns exist and are numeric
    for col in ['event_start_min', 'event_start_sec', 'event_end_min', 'event_end_sec',
                'time_start_total_seconds', 'time_end_total_seconds', 'duration',
                'event_running_start', 'event_running_end', 'running_video_time',
                'period_start_total_running_seconds', 'running_intermission_duration']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # time_start_total_seconds = minutes * 60 + seconds (time remaining in period)
    if 'event_start_min' in df.columns and 'event_start_sec' in df.columns:
        # Calculate for rows where it's missing
        needs_calc = df['time_start_total_seconds'].isna() if 'time_start_total_seconds' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df['event_start_min'] * 60 + df['event_start_sec']
            if 'time_start_total_seconds' not in df.columns:
                df['time_start_total_seconds'] = calc_vals
            else:
                df.loc[needs_calc, 'time_start_total_seconds'] = calc_vals[needs_calc]
            calculated.append('time_start_total_seconds')

    if 'event_end_min' in df.columns and 'event_end_sec' in df.columns:
        needs_calc = df['time_end_total_seconds'].isna() if 'time_end_total_seconds' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df['event_end_min'] * 60 + df['event_end_sec']
            if 'time_end_total_seconds' not in df.columns:
                df['time_end_total_seconds'] = calc_vals
            else:
                df.loc[needs_calc, 'time_end_total_seconds'] = calc_vals[needs_calc]
            calculated.append('time_end_total_seconds')

    # duration = start_time - end_time (because clock counts down)
    # Track inverted rows for recalculating dependent columns
    inverted_rows = pd.Series([False]*len(df), index=df.index)

    if 'time_start_total_seconds' in df.columns and 'time_end_total_seconds' in df.columns:
        # Fix inverted times: if end > start (negative duration), swap them
        if 'duration' in df.columns:
            inverted_rows = df['duration'] < 0
            if inverted_rows.any():
                # Swap start and end times for inverted rows
                start_vals = df.loc[inverted_rows, 'time_start_total_seconds'].copy()
                end_vals = df.loc[inverted_rows, 'time_end_total_seconds'].copy()
                df.loc[inverted_rows, 'time_start_total_seconds'] = end_vals
                df.loc[inverted_rows, 'time_end_total_seconds'] = start_vals
                # Also swap event_running_start/end if they exist
                if 'event_running_start' in df.columns and 'event_running_end' in df.columns:
                    run_start_vals = df.loc[inverted_rows, 'event_running_start'].copy()
                    run_end_vals = df.loc[inverted_rows, 'event_running_end'].copy()
                    df.loc[inverted_rows, 'event_running_start'] = run_end_vals
                    df.loc[inverted_rows, 'event_running_end'] = run_start_vals
                # Recalculate duration as positive
                df.loc[inverted_rows, 'duration'] = df.loc[inverted_rows, 'time_start_total_seconds'] - df.loc[inverted_rows, 'time_end_total_seconds']
                calculated.append(f'duration (fixed {inverted_rows.sum()} inverted)')

        # Calculate duration for rows that need it
        needs_calc = df['duration'].isna() if 'duration' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df['time_start_total_seconds'] - df['time_end_total_seconds']
            if 'duration' not in df.columns:
                df['duration'] = calc_vals
            else:
                df.loc[needs_calc, 'duration'] = calc_vals[needs_calc]
            calculated.append('duration')

        # Final pass: fix any remaining negative durations by swapping times
        negative_duration = (df['duration'] < 0) if 'duration' in df.columns else pd.Series([False]*len(df))
        if negative_duration.any():
            # Swap start and end times
            start_vals = df.loc[negative_duration, 'time_start_total_seconds'].copy()
            end_vals = df.loc[negative_duration, 'time_end_total_seconds'].copy()
            df.loc[negative_duration, 'time_start_total_seconds'] = end_vals
            df.loc[negative_duration, 'time_end_total_seconds'] = start_vals
            # Swap event_running_start/end if they exist
            if 'event_running_start' in df.columns and 'event_running_end' in df.columns:
                run_start = df.loc[negative_duration, 'event_running_start'].copy()
                run_end = df.loc[negative_duration, 'event_running_end'].copy()
                df.loc[negative_duration, 'event_running_start'] = run_end
                df.loc[negative_duration, 'event_running_end'] = run_start
            # Recalculate duration
            df.loc[negative_duration, 'duration'] = df.loc[negative_duration, 'time_start_total_seconds'] - df.loc[negative_duration, 'time_end_total_seconds']
            calculated.append(f'duration (final fix {negative_duration.sum()} negatives)')

    # event_running_start/end = cumulative seconds from game start
    # Period 1: 0-1200, Period 2: 1200-2400, Period 3: 2400-3600
    if 'period' in df.columns and 'time_start_total_seconds' in df.columns:
        df['period'] = pd.to_numeric(df['period'], errors='coerce').fillna(1).astype(int)

        # Calculate for rows that need it (NA) OR were inverted (need recalc)
        needs_calc = df['event_running_start'].isna() if 'event_running_start' in df.columns else pd.Series([True]*len(df))
        needs_calc = needs_calc | inverted_rows  # Include inverted rows
        if needs_calc.any():
            # Running time = (period-1)*1200 + (1200 - time_remaining)
            calc_vals = (df['period'] - 1) * 1200 + (1200 - df['time_start_total_seconds'])
            if 'event_running_start' not in df.columns:
                df['event_running_start'] = calc_vals
            else:
                df.loc[needs_calc, 'event_running_start'] = calc_vals[needs_calc]
            calculated.append('event_running_start')

        needs_calc = df['event_running_end'].isna() if 'event_running_end' in df.columns else pd.Series([True]*len(df))
        needs_calc = needs_calc | inverted_rows  # Include inverted rows
        if needs_calc.any() and 'time_end_total_seconds' in df.columns:
            calc_vals = (df['period'] - 1) * 1200 + (1200 - df['time_end_total_seconds'])
            if 'event_running_end' not in df.columns:
                df['event_running_end'] = calc_vals
            else:
                df.loc[needs_calc, 'event_running_end'] = calc_vals[needs_calc]
            calculated.append('event_running_end')

    # period_start_total_running_seconds (for video sync)
    if 'period' in df.columns:
        needs_calc = df['period_start_total_running_seconds'].isna() if 'period_start_total_running_seconds' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = (df['period'] - 1) * 1200
            if 'period_start_total_running_seconds' not in df.columns:
                df['period_start_total_running_seconds'] = calc_vals
            else:
                df.loc[needs_calc, 'period_start_total_running_seconds'] = calc_vals[needs_calc]
            calculated.append('period_start_total_running_seconds')

    # running_video_time (estimate from running_start, can be adjusted)
    if 'event_running_start' in df.columns:
        needs_calc = df['running_video_time'].isna() if 'running_video_time' in df.columns else pd.Series([True]*len(df))
        needs_calc = needs_calc | inverted_rows  # Include inverted rows
        if needs_calc.any():
            # Add ~15 min per intermission (periods 2,3 have intermissions before them)
            intermission_offset = df['period'].apply(lambda p: (p - 1) * 900 if pd.notna(p) and p > 1 else 0)
            calc_vals = df['event_running_start'] + intermission_offset
            if 'running_video_time' not in df.columns:
                df['running_video_time'] = calc_vals
            else:
                df.loc[needs_calc, 'running_video_time'] = calc_vals[needs_calc]
            calculated.append('running_video_time')

    # running_intermission_duration
    if 'period' in df.columns:
        needs_calc = df['running_intermission_duration'].isna() if 'running_intermission_duration' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df['period'].apply(lambda p: (p - 1) * 900 if pd.notna(p) and p > 1 else 0)
            if 'running_intermission_duration' not in df.columns:
                df['running_intermission_duration'] = calc_vals
            else:
                df.loc[needs_calc, 'running_intermission_duration'] = calc_vals[needs_calc]
            calculated.append('running_intermission_duration')

    # ================================================================
    # 2. TEAM/VENUE COLUMNS
    # ================================================================

    # Determine team column (could be 'team_', 'team', or derived)
    team_col = None
    for col in ['team_', 'team', 'team_venue']:
        if col in df.columns and df[col].notna().any():
            team_col = col
            break

    if team_col:
        # team_venue (home/away)
        needs_calc = df['team_venue'].isna() if 'team_venue' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df[team_col].apply(lambda x: str(x).lower() if pd.notna(x) else None)
            if 'team_venue' not in df.columns:
                df['team_venue'] = calc_vals
            else:
                df.loc[needs_calc, 'team_venue'] = calc_vals[needs_calc]
            calculated.append('team_venue')

        # team_venue_abv (H/A)
        needs_calc = df['team_venue_abv'].isna() if 'team_venue_abv' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df['team_venue'].apply(
                lambda x: 'H' if str(x).lower() == 'home' else ('A' if str(x).lower() == 'away' else None)
            )
            if 'team_venue_abv' not in df.columns:
                df['team_venue_abv'] = calc_vals
            else:
                df.loc[needs_calc, 'team_venue_abv'] = calc_vals[needs_calc]
            calculated.append('team_venue_abv')

        # player_team (actual team name)
        if 'home_team' in df.columns and 'away_team' in df.columns:
            needs_calc = df['player_team'].isna() if 'player_team' in df.columns else pd.Series([True]*len(df))
            if needs_calc.any():
                calc_vals = df.apply(
                    lambda r: r.get('home_team') if str(r.get('team_venue', '')).lower() == 'home'
                              else r.get('away_team') if str(r.get('team_venue', '')).lower() == 'away'
                              else None,
                    axis=1
                )
                if 'player_team' not in df.columns:
                    df['player_team'] = calc_vals
                else:
                    df.loc[needs_calc, 'player_team'] = calc_vals[needs_calc]
                calculated.append('player_team')

    # ================================================================
    # 3. ZONE COLUMNS
    # ================================================================

    if 'event_team_zone' in df.columns and team_col:
        zone_map = {'Offensive': 'Defensive', 'Defensive': 'Offensive', 'Neutral': 'Neutral'}

        # home_team_zone
        # Note: team_venue values are 'h' (home) and 'a' (away), not 'home'/'away'
        needs_calc = df['home_team_zone'].isna() if 'home_team_zone' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df.apply(
                lambda r: r.get('event_team_zone') if str(r.get('team_venue', '')).lower() in ('h', 'home')
                          else zone_map.get(r.get('event_team_zone'), 'Neutral'),
                axis=1
            )
            if 'home_team_zone' not in df.columns:
                df['home_team_zone'] = calc_vals
            else:
                df.loc[needs_calc, 'home_team_zone'] = calc_vals[needs_calc]
            calculated.append('home_team_zone')

        # away_team_zone (opposite of home)
        needs_calc = df['away_team_zone'].isna() if 'away_team_zone' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df['home_team_zone'].map(zone_map)
            if 'away_team_zone' not in df.columns:
                df['away_team_zone'] = calc_vals
            else:
                df.loc[needs_calc, 'away_team_zone'] = calc_vals[needs_calc]
            calculated.append('away_team_zone')

    # ================================================================
    # 4. PLAYER ROLE COLUMNS
    # ================================================================

    # Determine role column
    role_col = None
    for col in ['role_abrev_binary_', 'role_abrev_binary', 'player_role']:
        if col in df.columns and df[col].notna().any():
            role_col = col
            break

    if role_col:
        # player_role (standardized)
        needs_calc = df['player_role'].isna() if 'player_role' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df[role_col]
            if 'player_role' not in df.columns:
                df['player_role'] = calc_vals
            else:
                df.loc[needs_calc, 'player_role'] = calc_vals[needs_calc]
            calculated.append('player_role')

        # side_of_puck (event_team/opp_team)
        needs_calc = df['side_of_puck'].isna() if 'side_of_puck' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            calc_vals = df['player_role'].apply(
                lambda x: 'event_team' if pd.notna(x) and 'event' in str(x) else ('opp_team' if pd.notna(x) and 'opp' in str(x) else None)
            )
            if 'side_of_puck' not in df.columns:
                df['side_of_puck'] = calc_vals
            else:
                df.loc[needs_calc, 'side_of_puck'] = calc_vals[needs_calc]
            calculated.append('side_of_puck')

        # role_number (1, 2, 3...)
        needs_calc = df['role_number'].isna() if 'role_number' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            def extract_role_num(x):
                if pd.isna(x):
                    return 1
                parts = str(x).split('_')
                return int(parts[-1]) if parts[-1].isdigit() else 1
            calc_vals = df['player_role'].apply(extract_role_num)
            if 'role_number' not in df.columns:
                df['role_number'] = calc_vals
            else:
                df.loc[needs_calc, 'role_number'] = calc_vals[needs_calc]
            calculated.append('role_number')

        # role_abrev (E1, E2, O1, O2...)
        needs_calc = df['role_abrev'].isna() if 'role_abrev' in df.columns else pd.Series([True]*len(df))
        if needs_calc.any():
            def get_role_abrev(role):
                if pd.isna(role):
                    return None
                role_str = str(role)
                if 'event' in role_str:
                    num = role_str.split('_')[-1] if role_str.split('_')[-1].isdigit() else '1'
                    return f'E{num}'
                elif 'opp' in role_str:
                    num = role_str.split('_')[-1] if role_str.split('_')[-1].isdigit() else '1'
                    return f'O{num}'
                return None
            calc_vals = df['player_role'].apply(get_role_abrev)
            if 'role_abrev' not in df.columns:
                df['role_abrev'] = calc_vals
            else:
                df.loc[needs_calc, 'role_abrev'] = calc_vals[needs_calc]
            calculated.append('role_abrev')

    # ================================================================
    # 5. STRENGTH CALCULATION
    # ================================================================

    # If strength not provided, default to 5v5
    needs_calc = df['strength'].isna() if 'strength' in df.columns else pd.Series([True]*len(df))
    if needs_calc.any():
        if 'strength' not in df.columns:
            df['strength'] = '5v5'
        else:
            df.loc[needs_calc, 'strength'] = '5v5'
        calculated.append('strength')

    # ================================================================
    # 6. PLAY DETAIL COLUMNS
    # ================================================================

    # play_detail1 from play_detail1_ if exists
    needs_calc = df['play_detail1'].isna() if 'play_detail1' in df.columns else pd.Series([True]*len(df))
    if needs_calc.any():
        for col in ['play_detail1_', 'play_detail_1']:
            if col in df.columns and df[col].notna().any():
                calc_vals = df[col]
                if 'play_detail1' not in df.columns:
                    df['play_detail1'] = calc_vals
                else:
                    df.loc[needs_calc, 'play_detail1'] = calc_vals[needs_calc]
                calculated.append('play_detail1')
                break

    # play_detail_2 / play_detail2
    needs_calc = df['play_detail_2'].isna() if 'play_detail_2' in df.columns else pd.Series([True]*len(df))
    if needs_calc.any():
        for col in ['play_detail2_', 'play_detail2', 'play_detail_2_']:
            if col in df.columns and df[col].notna().any():
                calc_vals = df[col]
                if 'play_detail_2' not in df.columns:
                    df['play_detail_2'] = calc_vals
                else:
                    df.loc[needs_calc, 'play_detail_2'] = calc_vals[needs_calc]
                calculated.append('play_detail_2')
                break

    # play_detail_successful
    needs_calc = df['play_detail_successful'].isna() if 'play_detail_successful' in df.columns else pd.Series([True]*len(df))
    if needs_calc.any():
        for col in ['play_detail_successful_', 'play_successful_']:
            if col in df.columns and df[col].notna().any():
                calc_vals = df[col]
                if 'play_detail_successful' not in df.columns:
                    df['play_detail_successful'] = calc_vals
                else:
                    df.loc[needs_calc, 'play_detail_successful'] = calc_vals[needs_calc]
                calculated.append('play_detail_successful')
                break

    # ================================================================
    # 7. PRESSURE CALCULATION FROM XY DISTANCE
    # ================================================================
    # Calculate pressured_pressurer when opposing player is within threshold distance
    # This matches the tracker's auto-detection logic

    PRESSURE_THRESHOLD_FEET = 10  # Same as tracker default

    has_xy = ('player_x' in df.columns and df['player_x'].notna().any()) or \
             ('puck_x_start' in df.columns and df['puck_x_start'].notna().any())

    if has_xy and ('player_role' in df.columns or 'side_of_puck' in df.columns):
        # Only calculate if pressured_pressurer not already set
        needs_pressure = (df['pressured_pressurer'].isna()) if 'pressured_pressurer' in df.columns else pd.Series([True]*len(df))

        if needs_pressure.any():
            if 'pressured_pressurer' not in df.columns:
                df['pressured_pressurer'] = None

            pressure_count = 0

            # Get x/y columns
            x_col = 'player_x' if 'player_x' in df.columns and df['player_x'].notna().any() else 'puck_x_start'
            y_col = 'player_y' if 'player_y' in df.columns and df['player_y'].notna().any() else 'puck_y_start'

            # Group by event and check for pressure
            if 'event_id' in df.columns or 'tracking_event_index' in df.columns:
                group_col = 'event_id' if 'event_id' in df.columns else 'tracking_event_index'

                for event_id, group in df.groupby(group_col):
                    if len(group) < 2:
                        continue

                    # Identify event team vs opp team players
                    if 'side_of_puck' in group.columns:
                        evt_players = group[group['side_of_puck'] == 'event_team']
                        opp_players = group[group['side_of_puck'] == 'opp_team']
                    elif 'player_role' in group.columns:
                        evt_players = group[group['player_role'].str.contains('event', na=False)]
                        opp_players = group[group['player_role'].str.contains('opp', na=False)]
                    else:
                        continue

                    if len(evt_players) == 0 or len(opp_players) == 0:
                        continue

                    # For each event player, find closest opponent
                    for evt_idx, evt_row in evt_players.iterrows():
                        if pd.isna(evt_row.get(x_col)) or pd.isna(evt_row.get(y_col)):
                            continue

                        evt_x = float(evt_row[x_col])
                        evt_y = float(evt_row[y_col])

                        closest_dist = float('inf')
                        closest_opp = None

                        for opp_idx, opp_row in opp_players.iterrows():
                            if pd.isna(opp_row.get(x_col)) or pd.isna(opp_row.get(y_col)):
                                continue

                            opp_x = float(opp_row[x_col])
                            opp_y = float(opp_row[y_col])

                            # Calculate Euclidean distance
                            dist = ((evt_x - opp_x)**2 + (evt_y - opp_y)**2)**0.5

                            if dist <= PRESSURE_THRESHOLD_FEET and dist < closest_dist:
                                closest_dist = dist
                                closest_opp = opp_row.get('player_game_number')

                        # Set pressured_pressurer if within threshold
                        if closest_opp is not None and pd.isna(df.at[evt_idx, 'pressured_pressurer']):
                            df.at[evt_idx, 'pressured_pressurer'] = str(int(float(closest_opp))) if pd.notna(closest_opp) else None
                            pressure_count += 1

            if pressure_count > 0:
                calculated.append('pressured_pressurer')
                log.info(f"    Detected {pressure_count} pressure situations from XY distance")

    if calculated:
        unique_calcs = list(dict.fromkeys(calculated))  # Remove duplicates while preserving order
        log.info(f"    Calculated {len(unique_calcs)} columns: {', '.join(unique_calcs[:10])}{'...' if len(unique_calcs) > 10 else ''}")

    # ================================================================
    # 8. EVENT SUCCESS & PLAY DETAIL AUTOMATION
    # ================================================================
    # Process s/u logic and auto-derive play_details
    # See docs/reference/EVENT_SUCCESS_LOGIC.md for full specification

    try:
        from src.advanced.event_success import process_event_success
        from src.advanced.play_detail_automation import derive_all_play_details

        log.info("  Processing event success and play detail automation...")

        # Derive automated play_details first (before s/u logic)
        df = derive_all_play_details(df, config=None, log=log.info)

        # Process event success (standardize values, derive s/u, opposing pairs)
        df = process_event_success(df, config=None, log=log.info)

        log.info("    Event success and play detail automation complete")

    except ImportError as e:
        log.warning(f"    Could not import event_success modules: {e}")
    except Exception as e:
        log.warning(f"    Event success processing failed: {e}")

    return df
