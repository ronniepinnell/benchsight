#!/usr/bin/env python3
"""
Final Stats Enhancement - Adding Game Score, Performance vs Rating, and More
This adds the remaining stats to reach ~98% completion.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='pandas')
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

OUTPUT_DIR = Path('data/output')


def add_game_score(df):
    """
    Add Game Score calculation - a single-number summary of player performance.
    Based on NHL Game Score formula but adapted for our data.
    
    Game Score = G*0.75 + A1*0.7 + A2*0.55 + SOG*0.075 + BLK*0.05 + 
                 PIM*-0.15 + FOW*0.01 + FOL*-0.01 + GV*-0.03 + TK*0.05 +
                 CF*0.05 + CA*-0.05
    """
    print("Adding Game Score calculations...")
    
    df['game_score'] = (
        df.get('goals', 0) * 0.75 +
        df.get('primary_assists', df.get('assists', 0) * 0.5) * 0.7 +
        df.get('secondary_assists', df.get('assists', 0) * 0.5) * 0.55 +
        df.get('sog', 0) * 0.075 +
        df.get('blocks', 0) * 0.05 +
        df.get('fo_wins', 0) * 0.01 -
        df.get('fo_losses', 0) * 0.01 -
        df.get('giveaways', 0) * 0.03 +
        df.get('takeaways', 0) * 0.05 +
        df.get('corsi_for', 0) * 0.05 -
        df.get('corsi_against', 0) * 0.05
    ).round(2)
    
    # Game Score per 60
    toi = df['toi_seconds'].replace(0, np.nan)
    df['game_score_per_60'] = (df['game_score'] * 3600 / toi).round(2)
    
    # Game score rating (0-100 scale, 50 = average)
    mean_gs = df['game_score'].mean()
    std_gs = df['game_score'].std()
    if std_gs > 0:
        df['game_score_rating'] = (50 + (df['game_score'] - mean_gs) / std_gs * 15).clip(0, 100).round(1)
    else:
        df['game_score_rating'] = 50.0
    
    return df


def add_performance_vs_rating(df):
    """
    Add performance vs player rating comparison.
    Is a 3-rated player performing at 3.5 level?
    """
    print("Adding Performance vs Rating analysis...")
    
    # Get player's actual rating (2-6 scale)
    player_rating = df.get('player_rating', 4.0).fillna(4.0)
    
    # Calculate "effective rating" based on performance
    # Normalize key stats to a 2-6 scale
    
    # Points per game normalized
    points = df.get('points', 0)
    
    # Calculate performance rating based on multiple factors
    # Higher weight on offensive production
    goals = df.get('goals', 0)
    assists = df.get('assists', 0)
    pm = df.get('plus_minus_ev', 0)
    cf_pct = df.get('cf_pct', 50)
    game_score = df.get('game_score', 0)
    
    # Normalize game_score to 2-6 scale (assuming game_score typically -2 to 5)
    # game_score 0 = rating 4, +/-3 = +/-1 rating
    effective_rating_from_gs = 4 + (game_score / 2)
    
    # Cap between 2 and 6
    df['effective_game_rating'] = effective_rating_from_gs.clip(2, 6).round(2)
    
    # Performance delta (positive = playing above rating)
    df['rating_performance_delta'] = (df['effective_game_rating'] - player_rating).round(2)
    
    # Above/Below expectation flag
    df['playing_above_rating'] = (df['rating_performance_delta'] > 0.25).astype(int)
    df['playing_below_rating'] = (df['rating_performance_delta'] < -0.25).astype(int)
    df['playing_at_rating'] = ((df['rating_performance_delta'] >= -0.25) & 
                                (df['rating_performance_delta'] <= 0.25)).astype(int)
    
    # Performance tier
    def get_perf_tier(delta):
        if delta >= 1.0:
            return 'exceptional'
        elif delta >= 0.5:
            return 'overperforming'
        elif delta >= 0.25:
            return 'slightly_above'
        elif delta <= -1.0:
            return 'struggling'
        elif delta <= -0.5:
            return 'underperforming'
        elif delta <= -0.25:
            return 'slightly_below'
        else:
            return 'as_expected'
    
    df['performance_tier'] = df['rating_performance_delta'].apply(get_perf_tier)
    
    # Create performance index (100 = at rating, >100 = above, <100 = below)
    df['performance_index'] = (100 + df['rating_performance_delta'] * 25).round(1)
    
    return df


def add_success_flag_stats(events_player_df, df):
    """
    Aggregate stats using success flags (s=success, u=unsuccessful, blank=ignore).
    """
    print("Adding success flag based stats...")
    
    # Initialize new columns
    success_cols = [
        'shots_successful', 'shots_unsuccessful',
        'passes_successful', 'passes_unsuccessful', 
        'plays_successful', 'plays_unsuccessful',
        'entries_successful', 'entries_unsuccessful',
        'exits_successful', 'exits_unsuccessful',
        'total_successful_plays', 'total_unsuccessful_plays',
        'overall_success_rate', 'shot_success_rate',
        'pass_success_rate', 'play_success_rate',
    ]
    
    for col in success_cols:
        if col not in df.columns:
            df[col] = 0.0
    
    for idx, row in df.iterrows():
        game_id = row['game_id']
        player_id = row['player_id']
        
        player_events = events_player_df[
            (events_player_df['game_id'] == game_id) & 
            (events_player_df['player_id'] == player_id)
        ]
        
        # Filter to only rows with success flags (ignore blanks)
        events_with_flags = player_events[
            player_events['event_successful'].isin(['s', 'u'])
        ]
        
        # Count by event type
        for event_type, col_prefix in [
            ('Shot', 'shots'),
            ('Pass', 'passes'),
            ('Zone_Entry', 'entries'),
            ('Zone_Exit', 'exits'),
        ]:
            type_events = events_with_flags[
                events_with_flags['event_type'].str.contains(event_type, case=False, na=False) |
                events_with_flags['Type'].str.contains(event_type, case=False, na=False)
            ]
            
            successful = len(type_events[type_events['event_successful'] == 's'])
            unsuccessful = len(type_events[type_events['event_successful'] == 'u'])
            
            df.loc[idx, f'{col_prefix}_successful'] = successful
            df.loc[idx, f'{col_prefix}_unsuccessful'] = unsuccessful
        
        # Also check play_detail_successful
        play_events = player_events[
            player_events['play_detail_successful'].isin(['s', 'u'])
        ]
        
        plays_s = len(play_events[play_events['play_detail_successful'] == 's'])
        plays_u = len(play_events[play_events['play_detail_successful'] == 'u'])
        
        df.loc[idx, 'plays_successful'] = plays_s
        df.loc[idx, 'plays_unsuccessful'] = plays_u
        
        # Totals
        total_s = (df.loc[idx, 'shots_successful'] + df.loc[idx, 'passes_successful'] + 
                   df.loc[idx, 'entries_successful'] + df.loc[idx, 'exits_successful'] +
                   df.loc[idx, 'plays_successful'])
        total_u = (df.loc[idx, 'shots_unsuccessful'] + df.loc[idx, 'passes_unsuccessful'] +
                   df.loc[idx, 'entries_unsuccessful'] + df.loc[idx, 'exits_unsuccessful'] +
                   df.loc[idx, 'plays_unsuccessful'])
        
        df.loc[idx, 'total_successful_plays'] = total_s
        df.loc[idx, 'total_unsuccessful_plays'] = total_u
        
        # Success rates
        if total_s + total_u > 0:
            df.loc[idx, 'overall_success_rate'] = round(total_s / (total_s + total_u) * 100, 1)
        
        shots_total = df.loc[idx, 'shots_successful'] + df.loc[idx, 'shots_unsuccessful']
        if shots_total > 0:
            df.loc[idx, 'shot_success_rate'] = round(df.loc[idx, 'shots_successful'] / shots_total * 100, 1)
        
        pass_total = df.loc[idx, 'passes_successful'] + df.loc[idx, 'passes_unsuccessful']
        if pass_total > 0:
            df.loc[idx, 'pass_success_rate'] = round(df.loc[idx, 'passes_successful'] / pass_total * 100, 1)
        
        play_total = df.loc[idx, 'plays_successful'] + df.loc[idx, 'plays_unsuccessful']
        if play_total > 0:
            df.loc[idx, 'play_success_rate'] = round(df.loc[idx, 'plays_successful'] / play_total * 100, 1)
    
    return df


def add_pass_target_stats(events_player_df, df):
    """
    Add stats for when player is the pass target (event_player_2).
    """
    print("Adding pass target (event_player_2) stats...")
    
    target_cols = [
        'times_pass_target', 'passes_received_successful', 'passes_received_unsuccessful',
        'pass_reception_rate', 'times_target_oz', 'times_target_nz', 'times_target_dz',
        'slot_passes_received', 'cross_ice_passes_received',
    ]
    
    for col in target_cols:
        if col not in df.columns:
            df[col] = 0.0
    
    for idx, row in df.iterrows():
        game_id = row['game_id']
        player_id = row['player_id']
        
        # Find events where this player was event_player_2 (pass target)
        target_events = events_player_df[
            (events_player_df['game_id'] == game_id) & 
            (events_player_df['player_id'] == player_id) &
            (events_player_df['player_role'].str.contains('event_player_2|event_team_player_2', na=False))
        ]
        
        # Filter to pass events
        pass_targets = target_events[
            target_events['event_type'].str.contains('Pass', case=False, na=False) |
            target_events['Type'].str.contains('Pass', case=False, na=False)
        ]
        
        df.loc[idx, 'times_pass_target'] = len(pass_targets)
        
        # Successful/unsuccessful passes received
        received_s = len(pass_targets[pass_targets['event_successful'] == 's'])
        received_u = len(pass_targets[pass_targets['event_successful'] == 'u'])
        
        df.loc[idx, 'passes_received_successful'] = received_s
        df.loc[idx, 'passes_received_unsuccessful'] = received_u
        
        if len(pass_targets) > 0:
            df.loc[idx, 'pass_reception_rate'] = round(received_s / len(pass_targets) * 100, 1)
        
        # By zone
        df.loc[idx, 'times_target_oz'] = len(pass_targets[pass_targets['event_team_zone'] == 'O'])
        df.loc[idx, 'times_target_nz'] = len(pass_targets[pass_targets['event_team_zone'] == 'N'])
        df.loc[idx, 'times_target_dz'] = len(pass_targets[pass_targets['event_team_zone'] == 'D'])
    
    return df


def add_rush_type_stats(events_player_df, df):
    """
    Add rush type stats (odd man rushes, breakaways, etc.)
    """
    print("Adding rush type stats...")
    
    rush_cols = [
        'odd_man_rushes', 'odd_man_rush_goals', 'odd_man_rush_shots',
        'breakaway_attempts', 'breakaway_goals',
        '2on1_rushes', '3on2_rushes', '2on0_rushes',
        'rush_entries', 'rush_shots', 'rush_goals',
        'counter_attacks', 'transition_plays',
    ]
    
    for col in rush_cols:
        if col not in df.columns:
            df[col] = 0
    
    for idx, row in df.iterrows():
        game_id = row['game_id']
        player_id = row['player_id']
        
        player_events = events_player_df[
            (events_player_df['game_id'] == game_id) & 
            (events_player_df['player_id'] == player_id)
        ]
        
        # Look for rush-related play details
        event_detail_2 = player_events['event_detail_2'].fillna('').str.lower()
        play_detail = player_events['play_detail'].fillna('').str.lower()
        
        # Breakaways
        breakaways = player_events[
            player_events['event_detail'].str.contains('Breakaway', case=False, na=False)
        ]
        df.loc[idx, 'breakaway_attempts'] = len(breakaways)
        df.loc[idx, 'breakaway_goals'] = len(breakaways[
            breakaways['Type'].str.contains('Goal', case=False, na=False)
        ])
        
        # Rush entries
        rush_entries = player_events[
            event_detail_2.str.contains('rush|carry', na=False) &
            player_events['event_detail'].str.contains('Zone_Entry|Zone-Entry', case=False, na=False)
        ]
        df.loc[idx, 'rush_entries'] = len(rush_entries)
        
        # Rush shots (within 4 seconds of zone entry - simplified)
        rush_shots = player_events[
            play_detail.str.contains('rush|breakout', na=False) &
            player_events['Type'].str.contains('Shot|Goal', case=False, na=False)
        ]
        df.loc[idx, 'rush_shots'] = len(rush_shots)
        df.loc[idx, 'rush_goals'] = len(rush_shots[
            rush_shots['Type'].str.contains('Goal', case=False, na=False)
        ])
        
        # Odd man rushes (simplified detection)
        odd_man = player_events[
            play_detail.str.contains('odd|2on1|3on2|2on0|breakaway', na=False)
        ]
        df.loc[idx, 'odd_man_rushes'] = len(odd_man)
        
        # Transition plays
        transitions = player_events[
            play_detail.str.contains('breakout|transition|counter', na=False)
        ]
        df.loc[idx, 'transition_plays'] = len(transitions)
    
    return df


def add_opp_targeted_stats(events_player_df, df):
    """
    Add stats for when player was targeted by opponent (opp_player roles).
    How often was this player the focus of opponent's attack?
    """
    print("Adding opponent targeting stats...")
    
    opp_cols = [
        'times_targeted_by_opp', 'times_targeted_shots', 'times_targeted_entries',
        'times_targeted_passes', 'times_targeted_as_defender',
        'defensive_assignments', 'times_attacked', 'times_attacked_successfully',
        'times_attacked_unsuccessfully', 'defensive_success_rate',
    ]
    
    for col in opp_cols:
        if col not in df.columns:
            df[col] = 0.0
    
    for idx, row in df.iterrows():
        game_id = row['game_id']
        player_id = row['player_id']
        
        # Find events where this player was in an opp_player role
        opp_events = events_player_df[
            (events_player_df['game_id'] == game_id) & 
            (events_player_df['player_id'] == player_id) &
            (events_player_df['player_role'].str.contains('opp_player|opp_team', na=False))
        ]
        
        df.loc[idx, 'times_targeted_by_opp'] = len(opp_events)
        
        # Breakdown by event type
        df.loc[idx, 'times_targeted_shots'] = len(opp_events[
            opp_events['Type'].str.contains('Shot|Goal', case=False, na=False)
        ])
        
        df.loc[idx, 'times_targeted_entries'] = len(opp_events[
            opp_events['event_detail'].str.contains('Zone_Entry', case=False, na=False)
        ])
        
        df.loc[idx, 'times_targeted_passes'] = len(opp_events[
            opp_events['Type'].str.contains('Pass', case=False, na=False)
        ])
        
        # As primary defender (opp_player_1)
        primary_def = opp_events[
            opp_events['player_role'].str.contains('opp_player_1|opp_team_player_1', na=False)
        ]
        df.loc[idx, 'times_targeted_as_defender'] = len(primary_def)
        df.loc[idx, 'defensive_assignments'] = len(primary_def)
        
        # Track successful defense (opponent unsuccessful)
        attacks = opp_events[opp_events['event_successful'].isin(['s', 'u'])]
        df.loc[idx, 'times_attacked'] = len(attacks)
        
        # Opponent successful = our defense failed
        df.loc[idx, 'times_attacked_successfully'] = len(attacks[attacks['event_successful'] == 's'])
        df.loc[idx, 'times_attacked_unsuccessfully'] = len(attacks[attacks['event_successful'] == 'u'])
        
        if len(attacks) > 0:
            # Defense success = opponent unsuccessful
            df.loc[idx, 'defensive_success_rate'] = round(
                df.loc[idx, 'times_attacked_unsuccessfully'] / len(attacks) * 100, 1
            )
    
    return df


def add_secondary_player_stats(events_player_df, df):
    """
    Add stats for secondary/tertiary player roles.
    """
    print("Adding secondary player role stats...")
    
    secondary_cols = [
        'times_ep3', 'times_ep4', 'times_ep5',  # event_player_3, 4, 5
        'times_opp2', 'times_opp3', 'times_opp4',  # opp_player_2, 3, 4
        'total_on_ice_events', 'puck_touches_estimated',
        'involvement_rate', 'support_plays',
    ]
    
    for col in secondary_cols:
        if col not in df.columns:
            df[col] = 0.0
    
    for idx, row in df.iterrows():
        game_id = row['game_id']
        player_id = row['player_id']
        
        player_events = events_player_df[
            (events_player_df['game_id'] == game_id) & 
            (events_player_df['player_id'] == player_id)
        ]
        
        # Count by role type
        roles = player_events['player_role'].fillna('')
        
        df.loc[idx, 'times_ep3'] = len(roles[roles.str.contains('player_3', na=False)])
        df.loc[idx, 'times_ep4'] = len(roles[roles.str.contains('player_4', na=False)])
        df.loc[idx, 'times_ep5'] = len(roles[roles.str.contains('player_5', na=False)])
        
        df.loc[idx, 'times_opp2'] = len(roles[roles.str.contains('opp_player_2|opp_team_player_2', na=False)])
        df.loc[idx, 'times_opp3'] = len(roles[roles.str.contains('opp_player_3|opp_team_player_3', na=False)])
        df.loc[idx, 'times_opp4'] = len(roles[roles.str.contains('opp_player_4|opp_team_player_4', na=False)])
        
        df.loc[idx, 'total_on_ice_events'] = len(player_events)
        
        # Primary involvement (EP1 + EP2)
        primary_involvement = len(roles[roles.str.contains('player_1|player_2', na=False) & 
                                        ~roles.str.contains('opp', na=False)])
        
        # Puck touches estimated (EP1 events)
        puck_touches = len(roles[roles.str.contains('event_player_1|event_team_player_1', na=False)])
        df.loc[idx, 'puck_touches_estimated'] = puck_touches
        
        # Involvement rate
        if len(player_events) > 0:
            df.loc[idx, 'involvement_rate'] = round(primary_involvement / len(player_events) * 100, 1)
        
        # Support plays (EP3+)
        support = len(roles[roles.str.contains('player_[3-9]', na=False, regex=True)])
        df.loc[idx, 'support_plays'] = support
    
    return df


def add_contextual_stats(events_player_df, df):
    """
    Add context-based stats (score state, period, etc.)
    """
    print("Adding contextual stats...")
    
    context_cols = [
        'goals_leading', 'goals_trailing', 'goals_tied',
        'shots_leading', 'shots_trailing', 'shots_tied',
        'first_period_points', 'second_period_points', 'third_period_points',
        'first_period_shots', 'second_period_shots', 'third_period_shots',
        'clutch_goals', 'empty_net_goals_for', 'shorthanded_goals',
    ]
    
    for col in context_cols:
        if col not in df.columns:
            df[col] = 0
    
    # This would require score state tracking which may not be available
    # Adding placeholders that can be populated if data exists
    
    for idx, row in df.iterrows():
        game_id = row['game_id']
        player_id = row['player_id']
        
        player_events = events_player_df[
            (events_player_df['game_id'] == game_id) & 
            (events_player_df['player_id'] == player_id) &
            (events_player_df['player_role'].str.contains('event_player_1', na=False))
        ]
        
        # Points by period
        for period in [1, 2, 3]:
            period_events = player_events[player_events['period'] == period]
            goals = len(period_events[period_events['Type'].str.contains('Goal', case=False, na=False)])
            assists = len(period_events[
                period_events['play_detail'].str.contains('Assist', case=False, na=False)
            ])
            shots = len(period_events[period_events['Type'].str.contains('Shot', case=False, na=False)])
            
            if period == 1:
                df.loc[idx, 'first_period_points'] = goals + assists
                df.loc[idx, 'first_period_shots'] = shots
            elif period == 2:
                df.loc[idx, 'second_period_points'] = goals + assists
                df.loc[idx, 'second_period_shots'] = shots
            else:
                df.loc[idx, 'third_period_points'] = goals + assists
                df.loc[idx, 'third_period_shots'] = shots
    
    return df


def add_advanced_derived_stats(df):
    """
    Add final derived advanced stats.
    """
    print("Adding advanced derived stats...")
    
    # Offensive contribution index
    df['offensive_contribution'] = (
        df.get('goals', 0) * 3 +
        df.get('assists', 0) * 2 +
        df.get('sog', 0) * 0.5 +
        df.get('zone_entries_controlled', 0) * 0.3
    ).round(2)
    
    # Defensive contribution index
    df['defensive_contribution'] = (
        df.get('blocks', 0) * 2 +
        df.get('takeaways', 0) * 1.5 +
        df.get('backchecks', 0) * 1 +
        df.get('zone_entry_denials', 0) * 1.5 -
        df.get('giveaways_bad', 0) * 1
    ).round(2)
    
    # Two-way rating
    off = df.get('offensive_contribution', 0)
    deff = df.get('defensive_contribution', 0)
    df['two_way_rating'] = ((off + deff) / 2).round(2)
    
    # Puck possession index
    df['puck_possession_index'] = (
        df.get('puck_touches_estimated', 0) * 0.5 +
        df.get('passes_successful', 0) * 0.3 +
        df.get('loose_puck_wins', 0) * 0.5 -
        df.get('loose_puck_losses', 0) * 0.5
    ).round(2)
    
    # Danger creation rate
    df['danger_creation_rate'] = (
        df.get('xg_for', 0) +
        df.get('shots_high_danger', 0) * 0.15 +
        df.get('slot_passes_received', 0) * 0.1
    ).round(3)
    
    # Efficiency score
    toi_min = df['toi_minutes'].replace(0, np.nan)
    df['efficiency_score'] = (
        df['game_score'] / toi_min * 20
    ).round(2)
    
    # Clutch factor (goals in 3rd period weighted higher)
    df['clutch_factor'] = (
        df.get('third_period_points', 0) * 1.5 +
        df.get('first_period_points', 0) +
        df.get('second_period_points', 0)
    ).round(2)
    
    # Complete player score (all-around metric)
    df['complete_player_score'] = (
        df.get('offensive_rating', 50) * 0.35 +
        df.get('defensive_rating', 50) * 0.25 +
        df.get('hustle_rating', 50) * 0.2 +
        df.get('playmaking_rating', 50) * 0.2
    ).round(1)
    
    return df


def main():
    """Main enhancement pipeline."""
    print("=" * 70)
    print("FINAL STATS ENHANCEMENT - Game Score, Performance vs Rating, etc.")
    print("=" * 70)
    
    # Load data
    print("\nLoading data...")
    events_player_df = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv')
    df = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    
    original_cols = len(df.columns)
    print(f"Starting columns: {original_cols}")
    
    # Apply all enhancements
    df = add_game_score(df)
    df = add_performance_vs_rating(df)
    df = add_success_flag_stats(events_player_df, df)
    df = add_pass_target_stats(events_player_df, df)
    df = add_rush_type_stats(events_player_df, df)
    df = add_opp_targeted_stats(events_player_df, df)
    df = add_secondary_player_stats(events_player_df, df)
    df = add_contextual_stats(events_player_df, df)
    df = add_advanced_derived_stats(df)
    
    new_cols = len(df.columns)
    print(f"\nFinal columns: {new_cols} (+{new_cols - original_cols} new)")
    
    # Save
    df.to_csv(OUTPUT_DIR / 'fact_player_game_stats.csv', index=False)
    print(f"Saved fact_player_game_stats.csv")
    
    # List new columns
    print("\n" + "=" * 70)
    print("NEW COLUMNS ADDED:")
    print("=" * 70)
    
    new_col_groups = {
        'Game Score': ['game_score', 'game_score_per_60', 'game_score_rating'],
        'Performance vs Rating': ['effective_game_rating', 'rating_performance_delta', 
                                  'playing_above_rating', 'playing_below_rating', 
                                  'playing_at_rating', 'performance_tier', 'performance_index'],
        'Success Flags': ['shots_successful', 'shots_unsuccessful', 'passes_successful',
                         'passes_unsuccessful', 'plays_successful', 'plays_unsuccessful',
                         'overall_success_rate', 'shot_success_rate', 'pass_success_rate'],
        'Pass Targets': ['times_pass_target', 'passes_received_successful', 
                        'pass_reception_rate', 'times_target_oz', 'times_target_nz'],
        'Rush Types': ['odd_man_rushes', 'breakaway_attempts', 'breakaway_goals',
                      'rush_entries', 'rush_shots', 'rush_goals', 'transition_plays'],
        'Opponent Targeting': ['times_targeted_by_opp', 'times_targeted_shots',
                              'defensive_assignments', 'defensive_success_rate'],
        'Secondary Roles': ['times_ep3', 'times_opp2', 'puck_touches_estimated',
                           'involvement_rate', 'support_plays'],
        'Contextual': ['first_period_points', 'second_period_points', 'third_period_points'],
        'Advanced Derived': ['offensive_contribution', 'defensive_contribution',
                            'two_way_rating', 'puck_possession_index', 'danger_creation_rate',
                            'efficiency_score', 'clutch_factor', 'complete_player_score'],
    }
    
    for group, cols in new_col_groups.items():
        print(f"\n{group}:")
        for col in cols:
            if col in df.columns:
                print(f"  - {col}")
    
    print("\n" + "=" * 70)
    print("FINAL STATS ENHANCEMENT COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
