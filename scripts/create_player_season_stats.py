#!/usr/bin/env python3
"""
Create fact_player_season_stats - Season-level player aggregations with ratings.

Aggregates from fact_player_game_stats to provide:
- Traditional stats (goals, assists, points, etc.)
- Plus/minus by situation (all, EV, EN-adjusted)
- Rating-adjusted stats (gf_adj, ga_adj, pm_adj, etc.)
- Competition metrics (avg QoC, QoT, opponent rating)
- Per-game and per-60 rates
- Performance trends

Version: 6.5.19
Date: January 6, 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path('data/output')


def create_player_season_stats():
    """Create season-level player statistics."""
    
    print("=" * 60)
    print("Creating fact_player_season_stats")
    print("=" * 60)
    
    # Load source data
    pgs = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    dim_player = pd.read_csv(OUTPUT_DIR / 'dim_player.csv')
    
    print(f"\nSource: fact_player_game_stats - {len(pgs)} rows")
    print(f"Unique players: {pgs['player_id'].nunique()}")
    print(f"Unique seasons: {pgs['season_id'].nunique()}")
    
    # Define aggregation rules
    # Sum columns (counting stats)
    sum_cols = [
        # Traditional
        'goals', 'assists', 'points', 'shots', 'sog', 
        'shots_blocked', 'shots_missed',
        'pass_attempts', 'pass_completed',
        'fo_wins', 'fo_losses', 'fo_total',
        'zone_entries', 'zone_exits', 'giveaways', 'takeaways',
        # Time
        'toi_seconds', 'playing_toi_seconds', 'stoppage_seconds',
        'shift_count', 'logical_shifts',
        # Corsi/Fenwick
        'corsi_for', 'corsi_against', 'fenwick_for', 'fenwick_against',
        # Other
        'blocks', 'hits', 'puck_battles', 'puck_battle_wins', 'retrievals',
        # Plus/minus components (if available)
        'plus_ev', 'minus_ev', 'plus_total', 'minus_total',
        'plus_en_adj', 'minus_en_adj',
        # Shift-based
        'gf_all_shift', 'ga_all_shift',
        'cf_shift', 'ca_shift',
        # Adjusted
        'gf_adj', 'ga_adj', 'cf_adj', 'ca_adj',
    ]
    
    # Mean columns (ratings/averages - TOI-weighted where possible)
    mean_cols = [
        'player_rating', 'avg_opp_rating_precise',
        'qoc_precise', 'qoc_rating', 'qot_rating',
        'avg_shift_quality_score',
    ]
    
    # Build aggregation dictionary
    agg_dict = {'game_id': 'count'}  # games_played
    agg_dict['game_id'] = 'count'
    
    for col in sum_cols:
        if col in pgs.columns:
            agg_dict[col] = 'sum'
    
    for col in mean_cols:
        if col in pgs.columns:
            agg_dict[col] = 'mean'
    
    # Performance flag counts
    if 'performance_flag' in pgs.columns:
        # Count games by performance
        pgs['games_over'] = (pgs['performance_flag'] == 'Over').astype(int)
        pgs['games_under'] = (pgs['performance_flag'] == 'Under').astype(int)
        pgs['games_expected'] = (pgs['performance_flag'] == 'Expected').astype(int)
        agg_dict['games_over'] = 'sum'
        agg_dict['games_under'] = 'sum'
        agg_dict['games_expected'] = 'sum'
    
    # Expected performance
    if 'expected_pm' in pgs.columns:
        agg_dict['expected_pm'] = 'sum'
    if 'pm_vs_expected' in pgs.columns:
        agg_dict['pm_vs_expected'] = 'sum'
    
    # Get first team for each player-season (assume primary team)
    def get_primary_team(x):
        return x.mode().iloc[0] if len(x.mode()) > 0 else x.iloc[0]
    
    # Group by player and season
    grouped = pgs.groupby(['player_id', 'season_id'])
    
    # Aggregate
    season_stats = grouped.agg(agg_dict).reset_index()
    
    # Rename game count
    season_stats = season_stats.rename(columns={'game_id': 'games_played'})
    
    # Get player names and primary team
    player_info = pgs.groupby(['player_id', 'season_id']).agg({
        'player_name': 'first'
    }).reset_index()
    
    season_stats = season_stats.merge(player_info, on=['player_id', 'season_id'], how='left')
    
    # Calculate derived metrics
    print("\nCalculating derived metrics...")
    
    # Time conversions
    season_stats['toi_minutes'] = season_stats['toi_seconds'] / 60
    season_stats['toi_per_game_seconds'] = season_stats['toi_seconds'] / season_stats['games_played']
    season_stats['toi_per_game_minutes'] = season_stats['toi_per_game_seconds'] / 60
    
    # Traditional plus/minus
    if 'plus_total' in season_stats.columns and 'minus_total' in season_stats.columns:
        season_stats['plus_minus_total'] = season_stats['plus_total'] - season_stats['minus_total']
    
    if 'plus_ev' in season_stats.columns and 'minus_ev' in season_stats.columns:
        season_stats['plus_minus_ev'] = season_stats['plus_ev'] - season_stats['minus_ev']
    
    if 'plus_en_adj' in season_stats.columns and 'minus_en_adj' in season_stats.columns:
        season_stats['plus_minus_en_adj'] = season_stats['plus_en_adj'] - season_stats['minus_en_adj']
    
    # Shift-based plus/minus
    if 'gf_all_shift' in season_stats.columns and 'ga_all_shift' in season_stats.columns:
        season_stats['pm_all_shift'] = season_stats['gf_all_shift'] - season_stats['ga_all_shift']
    
    # Rating-adjusted plus/minus
    if 'gf_adj' in season_stats.columns and 'ga_adj' in season_stats.columns:
        season_stats['pm_adj'] = season_stats['gf_adj'] - season_stats['ga_adj']
    
    # Percentages
    # Shooting percentage
    season_stats['shooting_pct'] = np.where(
        season_stats['shots'] > 0,
        season_stats['goals'] / season_stats['shots'] * 100,
        0
    )
    
    # Pass completion
    if 'pass_attempts' in season_stats.columns:
        season_stats['pass_pct'] = np.where(
            season_stats['pass_attempts'] > 0,
            season_stats['pass_completed'] / season_stats['pass_attempts'] * 100,
            0
        )
    
    # Faceoff percentage
    if 'fo_total' in season_stats.columns:
        season_stats['fo_pct'] = np.where(
            season_stats['fo_total'] > 0,
            season_stats['fo_wins'] / season_stats['fo_total'] * 100,
            0
        )
    
    # Corsi/Fenwick percentages
    if 'corsi_for' in season_stats.columns:
        total_corsi = season_stats['corsi_for'] + season_stats['corsi_against']
        season_stats['cf_pct'] = np.where(
            total_corsi > 0,
            season_stats['corsi_for'] / total_corsi * 100,
            50.0
        )
    
    if 'fenwick_for' in season_stats.columns:
        total_fenwick = season_stats['fenwick_for'] + season_stats['fenwick_against']
        season_stats['ff_pct'] = np.where(
            total_fenwick > 0,
            season_stats['fenwick_for'] / total_fenwick * 100,
            50.0
        )
    
    # Adjusted Corsi percentage
    if 'cf_adj' in season_stats.columns:
        total_cf_adj = season_stats['cf_adj'] + season_stats['ca_adj']
        season_stats['cf_pct_adj'] = np.where(
            total_cf_adj > 0,
            season_stats['cf_adj'] / total_cf_adj * 100,
            50.0
        )
    
    # Rating advantage
    if 'player_rating' in season_stats.columns and 'avg_opp_rating_precise' in season_stats.columns:
        season_stats['avg_rating_advantage'] = season_stats['player_rating'] - season_stats['avg_opp_rating_precise']
    
    # Per-game rates
    gp = season_stats['games_played']
    season_stats['goals_per_game'] = season_stats['goals'] / gp
    season_stats['assists_per_game'] = season_stats['assists'] / gp
    season_stats['points_per_game'] = season_stats['points'] / gp
    season_stats['shots_per_game'] = season_stats['shots'] / gp
    
    if 'pm_adj' in season_stats.columns:
        season_stats['pm_adj_per_game'] = season_stats['pm_adj'] / gp
    
    # Per-60 rates
    toi_hours = season_stats['toi_seconds'] / 3600
    
    per_60_stats = ['goals', 'assists', 'points', 'shots', 'corsi_for', 'corsi_against']
    if 'gf_adj' in season_stats.columns:
        per_60_stats.extend(['gf_adj', 'ga_adj', 'pm_adj', 'cf_adj', 'ca_adj'])
    
    for stat in per_60_stats:
        if stat in season_stats.columns:
            season_stats[f'{stat}_per_60'] = np.where(
                toi_hours > 0,
                season_stats[stat] / toi_hours,
                0
            )
    
    # Performance trend
    if 'games_over' in season_stats.columns:
        season_stats['over_pct'] = season_stats['games_over'] / season_stats['games_played'] * 100
        season_stats['under_pct'] = season_stats['games_under'] / season_stats['games_played'] * 100
    
    # Primary key
    season_stats['player_season_key'] = 'PS' + season_stats['season_id'].astype(str) + '_' + season_stats['player_id'].astype(str)
    
    # Reorder columns - put keys first
    key_cols = ['player_season_key', 'player_id', 'season_id', 'player_name', 'games_played']
    other_cols = [c for c in season_stats.columns if c not in key_cols]
    season_stats = season_stats[key_cols + other_cols]
    
    # Summary
    print(f"\n{'=' * 60}")
    print("SEASON STATS SUMMARY")
    print(f"{'=' * 60}")
    print(f"Rows: {len(season_stats)} (unique player-seasons)")
    print(f"Columns: {len(season_stats.columns)}")
    
    # Print column groups
    print(f"\nColumn categories:")
    rating_cols = [c for c in season_stats.columns if 'rating' in c.lower() or 'qoc' in c.lower() or 'qot' in c.lower()]
    adj_cols = [c for c in season_stats.columns if '_adj' in c.lower()]
    per_60_cols = [c for c in season_stats.columns if 'per_60' in c.lower()]
    print(f"  Rating/Competition: {len(rating_cols)}")
    print(f"  Adjusted stats: {len(adj_cols)}")
    print(f"  Per-60 rates: {len(per_60_cols)}")
    
    # Sample output
    print(f"\nSample data (top 5 by points):")
    sample_cols = ['player_name', 'games_played', 'goals', 'assists', 'points', 'pm_adj', 'cf_pct_adj']
    sample_cols = [c for c in sample_cols if c in season_stats.columns]
    print(season_stats.nlargest(5, 'points')[sample_cols].to_string(index=False))
    
    # Save
    output_path = OUTPUT_DIR / 'fact_player_season_stats.csv'
    season_stats.to_csv(output_path, index=False)
    print(f"\n✓ Saved {output_path}")
    
    return season_stats


if __name__ == '__main__':
    create_player_season_stats()
    print("\n✓ fact_player_season_stats created!")
