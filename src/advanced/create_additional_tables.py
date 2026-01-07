#!/usr/bin/env python3
"""
Additional Table Creation Script
Creates more wide/long tables for comprehensive Supabase deployment.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='pandas')
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# Import safe CSV utilities (with fallback)
try:
    from src.core.safe_csv import safe_write_csv, safe_read_csv
    SAFE_CSV_AVAILABLE = True
except ImportError:
    SAFE_CSV_AVAILABLE = False

OUTPUT_DIR = Path('data/output')


def save_table_safe(df, name):
    """Save table with safe CSV write."""
    path = OUTPUT_DIR / f"{name}.csv"
    if SAFE_CSV_AVAILABLE:
        safe_write_csv(df, str(path), atomic=True, validate=True)
    else:
        df.to_csv(path, index=False)
    return len(df)


def create_fact_player_stats_long():
    """Create long-format player stats (one row per player-game-stat)."""
    print("Creating fact_player_stats_long...")
    
    player_stats = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    
    # Columns to pivot (all numeric stat columns)
    id_cols = ['player_game_key', 'game_id', 'player_id', 'player_name']
    
    # Get all stat columns (numeric only)
    stat_cols = [c for c in player_stats.columns if c not in id_cols]
    
    records = []
    for idx, row in player_stats.iterrows():
        for stat_col in stat_cols:
            value = row[stat_col]
            if pd.notna(value) and value != 0:
                records.append({
                    'player_stat_key': f"{row['player_game_key']}_{stat_col}",
                    'player_game_key': row['player_game_key'],
                    'game_id': row['game_id'],
                    'player_id': row['player_id'],
                    'stat_name': stat_col,
                    'stat_value': value,
                })
    
    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_DIR / 'fact_player_stats_long.csv', index=False)
    print(f"  Created fact_player_stats_long.csv ({len(df)} rows)")
    return df


def create_fact_team_game_stats_enhanced():
    """Enhance team game stats with more metrics."""
    print("Enhancing fact_team_game_stats...")
    
    team_stats = pd.read_csv(OUTPUT_DIR / 'fact_team_game_stats.csv')
    player_stats = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    
    # Aggregate player stats to team level
    new_cols = [
        'total_shots', 'total_sog', 'total_passes', 'total_pass_completed',
        'team_pass_pct', 'total_zone_entries', 'total_zone_exits',
        'controlled_entries', 'controlled_exits', 'entry_control_pct',
        'total_giveaways', 'total_takeaways', 'turnover_diff',
        'total_blocks', 'total_hits', 'total_fo_wins', 'total_fo_losses', 'fo_pct',
        'corsi_for', 'corsi_against', 'cf_pct',
        'xg_for', 'xg_against', 'xg_diff',
        'avg_player_rating', 'total_dekes', 'total_screens',
        'offensive_rating_avg', 'defensive_rating_avg', 'hustle_rating_avg',
    ]
    
    for col in new_cols:
        if col not in team_stats.columns:
            team_stats[col] = 0.0
    
    # Group player stats by game and team
    for idx, row in team_stats.iterrows():
        game_id = row['game_id']
        team_id = row.get('team_id', '')
        
        # Find players on this team in this game
        team_players = player_stats[player_stats['game_id'] == game_id]
        
        if len(team_players) > 0:
            team_stats.loc[idx, 'total_shots'] = team_players['shots'].sum()
            team_stats.loc[idx, 'total_sog'] = team_players['sog'].sum()
            team_stats.loc[idx, 'total_passes'] = team_players['pass_attempts'].sum()
            team_stats.loc[idx, 'total_pass_completed'] = team_players['pass_completed'].sum()
            
            if team_stats.loc[idx, 'total_passes'] > 0:
                team_stats.loc[idx, 'team_pass_pct'] = round(
                    team_stats.loc[idx, 'total_pass_completed'] / team_stats.loc[idx, 'total_passes'] * 100, 1
                )
            
            team_stats.loc[idx, 'total_zone_entries'] = team_players['zone_entries'].sum()
            team_stats.loc[idx, 'total_zone_exits'] = team_players['zone_exits'].sum()
            
            if 'zone_entries_controlled' in team_players.columns:
                team_stats.loc[idx, 'controlled_entries'] = team_players['zone_entries_controlled'].sum()
            if 'zone_exits_controlled' in team_players.columns:
                team_stats.loc[idx, 'controlled_exits'] = team_players['zone_exits_controlled'].sum()
            
            team_stats.loc[idx, 'total_giveaways'] = team_players['giveaways'].sum()
            team_stats.loc[idx, 'total_takeaways'] = team_players['takeaways'].sum()
            team_stats.loc[idx, 'turnover_diff'] = (
                team_stats.loc[idx, 'total_takeaways'] - team_stats.loc[idx, 'total_giveaways']
            )
            
            team_stats.loc[idx, 'total_blocks'] = team_players['blocks'].sum()
            team_stats.loc[idx, 'total_hits'] = team_players['hits'].sum()
            team_stats.loc[idx, 'total_fo_wins'] = team_players['fo_wins'].sum()
            team_stats.loc[idx, 'total_fo_losses'] = team_players['fo_losses'].sum()
            
            fo_total = team_stats.loc[idx, 'total_fo_wins'] + team_stats.loc[idx, 'total_fo_losses']
            if fo_total > 0:
                team_stats.loc[idx, 'fo_pct'] = round(
                    team_stats.loc[idx, 'total_fo_wins'] / fo_total * 100, 1
                )
            
            team_stats.loc[idx, 'corsi_for'] = team_players['corsi_for'].sum()
            team_stats.loc[idx, 'corsi_against'] = team_players['corsi_against'].sum()
            
            cf_total = team_stats.loc[idx, 'corsi_for'] + team_stats.loc[idx, 'corsi_against']
            if cf_total > 0:
                team_stats.loc[idx, 'cf_pct'] = round(
                    team_stats.loc[idx, 'corsi_for'] / cf_total * 100, 1
                )
            
            if 'xg_for' in team_players.columns:
                team_stats.loc[idx, 'xg_for'] = round(team_players['xg_for'].sum(), 2)
            
            if 'player_rating' in team_players.columns:
                team_stats.loc[idx, 'avg_player_rating'] = round(team_players['player_rating'].mean(), 2)
            
            if 'deke_attempts' in team_players.columns:
                team_stats.loc[idx, 'total_dekes'] = team_players['deke_attempts'].sum()
            if 'screens' in team_players.columns:
                team_stats.loc[idx, 'total_screens'] = team_players['screens'].sum()
            
            # Average ratings
            for rating in ['offensive_rating', 'defensive_rating', 'hustle_rating']:
                if rating in team_players.columns:
                    team_stats.loc[idx, f'{rating}_avg'] = round(team_players[rating].mean(), 1)
    
    team_stats.to_csv(OUTPUT_DIR / 'fact_team_game_stats.csv', index=False)
    print(f"  Enhanced fact_team_game_stats.csv ({len(team_stats.columns)} columns)")
    return team_stats


def create_fact_line_combos_enhanced():
    """Enhance line combos with more metrics."""
    print("Enhancing fact_line_combos...")
    
    line_combos = pd.read_csv(OUTPUT_DIR / 'fact_line_combos.csv')
    
    new_cols = [
        'fenwick_for', 'fenwick_against', 'ff_pct',
        'xg_against', 'xg_diff', 'xg_pct',
        'zone_entries', 'zone_exits', 'controlled_entry_pct',
        'giveaways', 'takeaways', 'turnover_diff',
        'avg_player_rating', 'opp_avg_rating', 'rating_diff',
        'pdo', 'sh_pct', 'sv_pct',
        'goals_per_60', 'goals_against_per_60',
        'cf_per_60', 'ca_per_60',
    ]
    
    for col in new_cols:
        if col not in line_combos.columns:
            line_combos[col] = 0.0
    
    for idx, row in line_combos.iterrows():
        toi = row.get('toi_together', 0)
        cf = row.get('corsi_for', 0)
        ca = row.get('corsi_against', 0)
        gf = row.get('goals_for', 0)
        ga = row.get('goals_against', 0)
        
        # Fenwick (assume same as Corsi for now)
        line_combos.loc[idx, 'fenwick_for'] = cf
        line_combos.loc[idx, 'fenwick_against'] = ca
        
        ff_total = cf + ca
        if ff_total > 0:
            line_combos.loc[idx, 'ff_pct'] = round(cf / ff_total * 100, 1)
        
        # xG diff
        xgf = row.get('xgf', 0)
        xga = xgf * 0.9  # Estimate
        line_combos.loc[idx, 'xg_against'] = xga
        line_combos.loc[idx, 'xg_diff'] = round(xgf - xga, 2)
        
        if xgf + xga > 0:
            line_combos.loc[idx, 'xg_pct'] = round(xgf / (xgf + xga) * 100, 1)
        
        # Per-60 rates
        if toi > 0:
            line_combos.loc[idx, 'goals_per_60'] = round(gf * 3600 / toi, 2)
            line_combos.loc[idx, 'goals_against_per_60'] = round(ga * 3600 / toi, 2)
            line_combos.loc[idx, 'cf_per_60'] = round(cf * 3600 / toi, 2)
            line_combos.loc[idx, 'ca_per_60'] = round(ca * 3600 / toi, 2)
        
        # PDO
        if cf > 0 and ca > 0:
            sh_pct = (gf / cf) * 100 if cf > 0 else 0
            sv_pct = (1 - ga / ca) * 100 if ca > 0 else 100
            line_combos.loc[idx, 'sh_pct'] = round(sh_pct, 1)
            line_combos.loc[idx, 'sv_pct'] = round(sv_pct, 1)
            line_combos.loc[idx, 'pdo'] = round(sh_pct + sv_pct, 1)
    
    line_combos.to_csv(OUTPUT_DIR / 'fact_line_combos.csv', index=False)
    print(f"  Enhanced fact_line_combos.csv ({len(line_combos.columns)} columns)")
    return line_combos


def create_fact_matchup_summary():
    """Create matchup summary table combining H2H and WOWY insights."""
    print("Creating fact_matchup_summary...")
    
    h2h = pd.read_csv(OUTPUT_DIR / 'fact_h2h.csv')
    wowy = pd.read_csv(OUTPUT_DIR / 'fact_wowy.csv')
    
    # Merge H2H and WOWY
    matchup = h2h.merge(
        wowy[['game_id', 'player_1_id', 'player_2_id', 
              'p1_shifts_without_p2', 'p2_shifts_without_p1',
              'cf_pct_together', 'cf_pct_apart', 'cf_pct_delta']],
        on=['game_id', 'player_1_id', 'player_2_id'],
        how='left'
    )
    
    matchup['matchup_key'] = matchup.apply(
        lambda x: f"{x['game_id']}_{x['player_1_id']}_{x['player_2_id']}", axis=1
    )
    
    # Calculate synergy score
    matchup['synergy_score'] = matchup['cf_pct_delta'].fillna(0)
    matchup['is_positive_synergy'] = (matchup['synergy_score'] > 0).astype(int)
    
    matchup.to_csv(OUTPUT_DIR / 'fact_matchup_summary.csv', index=False)
    print(f"  Created fact_matchup_summary.csv ({len(matchup)} rows)")
    return matchup


def create_fact_shift_quality():
    """Create shift quality analysis table."""
    print("Creating fact_shift_quality...")
    
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shift_players.csv')
    
    records = []
    for idx, row in shifts.iterrows():
        duration = row.get('shift_duration', 0)
        
        # Classify shift quality
        if duration < 30:
            quality = 'short'
            quality_score = 70
        elif duration < 45:
            quality = 'optimal'
            quality_score = 100
        elif duration < 60:
            quality = 'good'
            quality_score = 90
        elif duration < 90:
            quality = 'long'
            quality_score = 70
        else:
            quality = 'exhausted'
            quality_score = 40
        
        records.append({
            'shift_quality_key': f"{row.get('shift_key', idx)}",
            'game_id': row.get('game_id'),
            'player_id': row.get('player_id'),
            'shift_index': row.get('shift_index'),
            'shift_duration': duration,
            'shift_quality': quality,
            'quality_score': quality_score,
            'period': row.get('period'),
            'strength': row.get('strength'),
            'situation': row.get('situation'),
        })
    
    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_DIR / 'fact_shift_quality.csv', index=False)
    print(f"  Created fact_shift_quality.csv ({len(df)} rows)")
    return df


def create_fact_zone_time_enhanced():
    """Enhance zone time table with more detail."""
    print("Enhancing fact_team_zone_time...")
    
    try:
        zone_time = pd.read_csv(OUTPUT_DIR / 'fact_team_zone_time.csv')
    except (FileNotFoundError, pd.errors.EmptyDataError):
        print("  fact_team_zone_time.csv not found, skipping")
        return pd.DataFrame()
    
    # Add additional columns if not present
    new_cols = ['oz_dominance', 'dz_pressure', 'territorial_index']
    for col in new_cols:
        if col not in zone_time.columns:
            zone_time[col] = 0.0
    
    # Calculate derived metrics
    for idx, row in zone_time.iterrows():
        oz_pct = row.get('ozone_pct', 0)
        dz_pct = row.get('dzone_pct', 0)
        
        # OZ dominance (positive = more offensive)
        zone_time.loc[idx, 'oz_dominance'] = round(oz_pct - dz_pct, 1)
        
        # Territorial index (0-100 scale, 50 = neutral)
        zone_time.loc[idx, 'territorial_index'] = round(50 + (oz_pct - dz_pct) / 2, 1)
    
    zone_time.to_csv(OUTPUT_DIR / 'fact_team_zone_time.csv', index=False)
    print(f"  Enhanced fact_team_zone_time.csv ({len(zone_time.columns)} columns)")
    return zone_time


def create_fact_scoring_chances():
    """Create scoring chances table from events."""
    print("Creating fact_scoring_chances...")
    
    events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv')
    
    # Define scoring chance criteria
    scoring_chances = events[events['event_type'].isin(['Shot', 'Goal'])].copy()
    
    scoring_chances['scoring_chance_key'] = 'SC' + scoring_chances['game_id'].astype(str) + '_' + scoring_chances['event_id'].astype(str)
    scoring_chances['is_goal'] = (scoring_chances['event_type'] == 'Goal').astype(int)
    
    # Determine danger level (will be enhanced with XY data)
    def get_danger(row):
        detail = str(row.get('event_detail', ''))
        if 'Rebound' in detail or 'Tip' in detail:
            return 'high'
        elif 'Blocked' in detail or 'Missed' in detail:
            return 'low'
        else:
            return 'medium'
    
    scoring_chances['danger_level'] = scoring_chances.apply(get_danger, axis=1)
    scoring_chances['is_rebound'] = scoring_chances['event_detail'].str.contains('Rebound', na=False).astype(int)
    scoring_chances['is_rush'] = 0  # Will be calculated from sequences
    scoring_chances['is_odd_man'] = 0  # Requires more context
    
    # Select columns
    cols = ['scoring_chance_key', 'game_id', 'event_id', 'period', 
            'is_goal', 'danger_level', 'is_rebound', 'is_rush', 'is_odd_man',
            'event_detail', 'event_detail_2']
    
    scoring_chances = scoring_chances[[c for c in cols if c in scoring_chances.columns]]
    scoring_chances.to_csv(OUTPUT_DIR / 'fact_scoring_chances.csv', index=False)
    print(f"  Created fact_scoring_chances.csv ({len(scoring_chances)} rows)")
    return scoring_chances


def create_dim_stat_category():
    """Create dimension table for stat categories."""
    print("Creating dim_stat_category...")
    
    categories = [
        {'stat_category_id': 'SC001', 'category_code': 'counting', 'category_name': 'Counting Stats', 
         'description': 'Basic counting statistics (G, A, SOG, etc.)'},
        {'stat_category_id': 'SC002', 'category_code': 'time', 'category_name': 'Time Stats',
         'description': 'Time on ice and shift metrics'},
        {'stat_category_id': 'SC003', 'category_code': 'percentage', 'category_name': 'Percentage Stats',
         'description': 'Rate and percentage metrics (SH%, FO%, etc.)'},
        {'stat_category_id': 'SC004', 'category_code': 'per_60', 'category_name': 'Per-60 Rates',
         'description': 'Statistics normalized to per 60 minutes'},
        {'stat_category_id': 'SC005', 'category_code': 'possession', 'category_name': 'Possession Stats',
         'description': 'Corsi, Fenwick, zone time'},
        {'stat_category_id': 'SC006', 'category_code': 'micro', 'category_name': 'Micro Stats',
         'description': 'Detailed play-by-play actions'},
        {'stat_category_id': 'SC007', 'category_code': 'transition', 'category_name': 'Transition Stats',
         'description': 'Zone entries, exits, breakouts'},
        {'stat_category_id': 'SC008', 'category_code': 'defender', 'category_name': 'Defender Stats',
         'description': 'Statistics from defensive perspective'},
        {'stat_category_id': 'SC009', 'category_code': 'rating', 'category_name': 'Rating Adjusted',
         'description': 'Stats adjusted for opponent/teammate quality'},
        {'stat_category_id': 'SC010', 'category_code': 'composite', 'category_name': 'Composite Ratings',
         'description': 'Combined metrics (OFF, DEF, WAR)'},
        {'stat_category_id': 'SC011', 'category_code': 'xg', 'category_name': 'Expected Goals',
         'description': 'xG model outputs'},
        {'stat_category_id': 'SC012', 'category_code': 'goalie', 'category_name': 'Goalie Stats',
         'description': 'Goaltender specific metrics'},
        {'stat_category_id': 'SC013', 'category_code': 'beer_league', 'category_name': 'Beer League',
         'description': 'Recreational hockey specific metrics'},
    ]
    
    df = pd.DataFrame(categories)
    df.to_csv(OUTPUT_DIR / 'dim_stat_category.csv', index=False)
    print(f"  Created dim_stat_category.csv")
    return df


def create_dim_micro_stat():
    """Create dimension table for micro stats."""
    print("Creating dim_micro_stat...")
    
    micro_stats = [
        # Offensive
        {'micro_stat_id': 'MS001', 'stat_code': 'deke_attempts', 'stat_name': 'Deke Attempts', 'category': 'offensive'},
        {'micro_stat_id': 'MS002', 'stat_code': 'dekes_successful', 'stat_name': 'Successful Dekes', 'category': 'offensive'},
        {'micro_stat_id': 'MS003', 'stat_code': 'screens', 'stat_name': 'Screens', 'category': 'offensive'},
        {'micro_stat_id': 'MS004', 'stat_code': 'crash_net', 'stat_name': 'Crash Net', 'category': 'offensive'},
        {'micro_stat_id': 'MS005', 'stat_code': 'drives_middle', 'stat_name': 'Drives Middle', 'category': 'offensive'},
        {'micro_stat_id': 'MS006', 'stat_code': 'drives_wide', 'stat_name': 'Drives Wide', 'category': 'offensive'},
        {'micro_stat_id': 'MS007', 'stat_code': 'cycle_plays', 'stat_name': 'Cycle Plays', 'category': 'offensive'},
        {'micro_stat_id': 'MS008', 'stat_code': 'tip_attempts', 'stat_name': 'Tip/Deflection Attempts', 'category': 'offensive'},
        # Defensive
        {'micro_stat_id': 'MS010', 'stat_code': 'backchecks', 'stat_name': 'Backchecks', 'category': 'defensive'},
        {'micro_stat_id': 'MS011', 'stat_code': 'poke_checks', 'stat_name': 'Poke Checks', 'category': 'defensive'},
        {'micro_stat_id': 'MS012', 'stat_code': 'stick_checks', 'stat_name': 'Stick Checks', 'category': 'defensive'},
        {'micro_stat_id': 'MS013', 'stat_code': 'blocked_shots_play', 'stat_name': 'Shot Blocks (Play)', 'category': 'defensive'},
        {'micro_stat_id': 'MS014', 'stat_code': 'in_lane', 'stat_name': 'In Passing Lane', 'category': 'defensive'},
        {'micro_stat_id': 'MS015', 'stat_code': 'separate_from_puck', 'stat_name': 'Separate from Puck', 'category': 'defensive'},
        # Transition
        {'micro_stat_id': 'MS020', 'stat_code': 'breakouts', 'stat_name': 'Breakouts', 'category': 'transition'},
        {'micro_stat_id': 'MS021', 'stat_code': 'forechecks', 'stat_name': 'Forechecks', 'category': 'transition'},
        {'micro_stat_id': 'MS022', 'stat_code': 'dump_and_chase', 'stat_name': 'Dump and Chase', 'category': 'transition'},
        {'micro_stat_id': 'MS023', 'stat_code': 'zone_entry_denials', 'stat_name': 'Zone Entry Denials', 'category': 'transition'},
        {'micro_stat_id': 'MS024', 'stat_code': 'zone_exit_denials', 'stat_name': 'Zone Exit Denials', 'category': 'transition'},
        # Puck battles
        {'micro_stat_id': 'MS030', 'stat_code': 'loose_puck_wins', 'stat_name': 'Loose Puck Wins', 'category': 'battles'},
        {'micro_stat_id': 'MS031', 'stat_code': 'loose_puck_losses', 'stat_name': 'Loose Puck Losses', 'category': 'battles'},
        {'micro_stat_id': 'MS032', 'stat_code': 'puck_recoveries', 'stat_name': 'Puck Recoveries', 'category': 'battles'},
    ]
    
    df = pd.DataFrame(micro_stats)
    df.to_csv(OUTPUT_DIR / 'dim_micro_stat.csv', index=False)
    print(f"  Created dim_micro_stat.csv")
    return df


def create_fact_player_micro_stats():
    """Create dedicated micro stats table in long format."""
    print("Creating fact_player_micro_stats...")
    
    player_stats = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    
    # Micro stat columns
    micro_cols = [
        'deke_attempts', 'dekes_successful', 'screens', 'crash_net',
        'drives_middle', 'drives_wide', 'drives_corner', 'drives_net',
        'cycle_plays', 'tip_attempts', 'backchecks', 'poke_checks',
        'stick_checks', 'blocked_shots_play', 'in_lane', 'separate_from_puck',
        'breakouts', 'forechecks', 'dump_and_chase', 'zone_entry_denials',
        'zone_exit_denials', 'loose_puck_wins', 'loose_puck_losses',
        'puck_recoveries', 'puck_retrievals', 'box_outs', 'give_and_go',
        'quick_ups', 'cutbacks', 'pressures',
    ]
    
    records = []
    for idx, row in player_stats.iterrows():
        for col in micro_cols:
            if col in player_stats.columns:
                value = row.get(col, 0)
                if pd.notna(value) and value > 0:
                    records.append({
                        'micro_stat_key': f"{row['player_game_key']}_{col}",
                        'player_game_key': row['player_game_key'],
                        'game_id': row['game_id'],
                        'player_id': row['player_id'],
                        'micro_stat': col,
                        'count': int(value),
                    })
    
    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_DIR / 'fact_player_micro_stats.csv', index=False)
    print(f"  Created fact_player_micro_stats.csv ({len(df)} rows)")
    return df


def main():
    """Create all additional tables."""
    print("=" * 70)
    print("CREATING ADDITIONAL COMPREHENSIVE TABLES")
    print("=" * 70)
    
    # Long-format tables
    create_fact_player_stats_long()
    
    # Enhanced existing tables
    create_fact_team_game_stats_enhanced()
    create_fact_line_combos_enhanced()
    create_fact_zone_time_enhanced()
    
    # New analysis tables
    create_fact_matchup_summary()
    create_fact_shift_quality()
    create_fact_scoring_chances()
    create_fact_player_micro_stats()
    
    # New dimension tables
    create_dim_stat_category()
    create_dim_micro_stat()
    
    print("\n" + "=" * 70)
    print("ADDITIONAL TABLES COMPLETE")
    print("=" * 70)
    
    # Count all tables
    dim_tables = list(OUTPUT_DIR.glob('dim_*.csv'))
    fact_tables = list(OUTPUT_DIR.glob('fact_*.csv'))
    
    print(f"\nTotal Tables: {len(dim_tables) + len(fact_tables)}")
    print(f"  - Dimension tables: {len(dim_tables)}")
    print(f"  - Fact tables: {len(fact_tables)}")


if __name__ == '__main__':
    main()
