#!/usr/bin/env python3
"""
Enhance fact_team_game_stats with rating-adjusted metrics.

Adds:
- Opponent team average rating
- Rating-adjusted goals (gf_adj, ga_adj)
- Rating-adjusted Corsi (cf_adj, ca_adj)
- Rating advantage/disadvantage
- Expected performance based on rating differential

Version: 6.5.19
Date: January 6, 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASELINE_RATING = 4.0
OUTPUT_DIR = Path('data/output')


def enhance_team_game_stats():
    """Add rating columns to fact_team_game_stats."""
    
    print("=" * 60)
    print("Enhancing fact_team_game_stats with rating adjustments")
    print("=" * 60)
    
    # Load source tables
    tgs = pd.read_csv(OUTPUT_DIR / 'fact_team_game_stats.csv')
    pgs = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    dim_schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
    
    orig_cols = len(tgs.columns)
    print(f"\nSource: fact_team_game_stats - {len(tgs)} rows, {orig_cols} columns")
    
    # Calculate team-level ratings from player game stats
    print("\nCalculating team ratings from player data...")
    
    # Get TOI-weighted player ratings per team per game
    if 'player_rating' in pgs.columns and 'toi_seconds' in pgs.columns:
        # Need to determine team_id for each player-game
        # Load roster to get team assignments
        roster = pd.read_csv(OUTPUT_DIR / 'fact_gameroster.csv')
        
        # Merge player ratings with roster to get team
        pgs_with_team = pgs.merge(
            roster[['game_id', 'player_id', 'team_id', 'team_name']],
            on=['game_id', 'player_id'],
            how='left'
        )
        
        # TOI-weighted average rating per team per game
        team_ratings = pgs_with_team.groupby(['game_id', 'team_id']).apply(
            lambda x: np.average(x['player_rating'].dropna(), weights=x.loc[x['player_rating'].notna(), 'toi_seconds']) 
            if len(x['player_rating'].dropna()) > 0 and x.loc[x['player_rating'].notna(), 'toi_seconds'].sum() > 0
            else x['player_rating'].mean()
        ).reset_index(name='team_avg_rating_weighted')
        
        # Simple average as fallback
        team_ratings_simple = pgs_with_team.groupby(['game_id', 'team_id'])['player_rating'].mean().reset_index(name='team_avg_rating_simple')
        
        team_ratings = team_ratings.merge(team_ratings_simple, on=['game_id', 'team_id'], how='left')
        
        # Use weighted where available, simple as fallback
        team_ratings['team_avg_rating'] = team_ratings['team_avg_rating_weighted'].fillna(team_ratings['team_avg_rating_simple'])
        
        print(f"Calculated ratings for {len(team_ratings)} team-game combinations")
    
    # For each team-game, get opponent rating
    # Need to identify opponent for each team in each game
    print("\nCalculating opponent ratings...")
    
    # Get home and away teams from schedule
    schedule_info = dim_schedule[['game_id', 'home_team_id', 'away_team_id']].drop_duplicates()
    
    # Merge team ratings with schedule to get opponent
    tgs = tgs.merge(schedule_info[['game_id', 'home_team_id', 'away_team_id']], on='game_id', how='left', suffixes=('', '_sched'))
    
    # Determine if team is home or away, and get opponent
    tgs['is_home'] = tgs['team_id'] == tgs['home_team_id_sched'] if 'home_team_id_sched' in tgs.columns else tgs['team_id'] == tgs['home_team_id']
    tgs['opponent_team_id'] = np.where(
        tgs['is_home'],
        tgs.get('away_team_id_sched', tgs.get('away_team_id')),
        tgs.get('home_team_id_sched', tgs.get('home_team_id'))
    )
    
    # Clean up duplicate columns
    drop_cols = [c for c in tgs.columns if c.endswith('_sched')]
    tgs = tgs.drop(columns=drop_cols, errors='ignore')
    
    # Merge team and opponent ratings
    tgs = tgs.merge(
        team_ratings[['game_id', 'team_id', 'team_avg_rating']],
        on=['game_id', 'team_id'],
        how='left'
    )
    
    tgs = tgs.merge(
        team_ratings[['game_id', 'team_id', 'team_avg_rating']].rename(
            columns={'team_id': 'opponent_team_id', 'team_avg_rating': 'opponent_avg_rating'}
        ),
        on=['game_id', 'opponent_team_id'],
        how='left'
    )
    
    # Calculate rating-adjusted metrics
    print("\nCalculating rating-adjusted metrics...")
    
    # Rating multiplier
    tgs['rating_multiplier'] = tgs['opponent_avg_rating'] / BASELINE_RATING
    
    # Goals adjusted
    # gf_adj = goals × opp_multiplier (bonus for scoring vs good teams)
    # But for team stats, we need goals_against from opponent
    # For now, adjust our goals scored
    tgs['gf_adj'] = np.where(
        tgs['rating_multiplier'].notna(),
        tgs['goals'] * tgs['rating_multiplier'],
        tgs['goals']
    )
    
    # For goals against, we need the opponent's goals
    # Create a self-join to get opponent goals
    opponent_goals = tgs[['game_id', 'team_id', 'goals']].rename(
        columns={'team_id': 'opponent_team_id', 'goals': 'goals_against_raw'}
    )
    tgs = tgs.merge(opponent_goals, on=['game_id', 'opponent_team_id'], how='left')
    
    # Goals against adjusted (less penalty for GA vs good teams)
    tgs['ga_adj'] = np.where(
        (tgs['rating_multiplier'].notna()) & (tgs['rating_multiplier'] > 0),
        tgs['goals_against_raw'] / tgs['rating_multiplier'],
        tgs['goals_against_raw']
    )
    
    # Plus/minus adjusted
    tgs['goal_diff_raw'] = tgs['goals'] - tgs['goals_against_raw']
    tgs['goal_diff_adj'] = tgs['gf_adj'] - tgs['ga_adj']
    
    # Corsi adjusted
    if 'corsi_for' in tgs.columns and 'corsi_against' in tgs.columns:
        tgs['cf_adj'] = np.where(
            tgs['rating_multiplier'].notna(),
            tgs['corsi_for'] * tgs['rating_multiplier'],
            tgs['corsi_for']
        )
        
        tgs['ca_adj'] = np.where(
            (tgs['rating_multiplier'].notna()) & (tgs['rating_multiplier'] > 0),
            tgs['corsi_against'] / tgs['rating_multiplier'],
            tgs['corsi_against']
        )
        
        tgs['cf_pct_adj'] = np.where(
            (tgs['cf_adj'] + tgs['ca_adj']) > 0,
            tgs['cf_adj'] / (tgs['cf_adj'] + tgs['ca_adj']) * 100,
            50.0
        )
    
    # Rating advantage
    tgs['rating_advantage'] = np.where(
        tgs['team_avg_rating'].notna() & tgs['opponent_avg_rating'].notna(),
        tgs['team_avg_rating'] - tgs['opponent_avg_rating'],
        0
    )
    
    # Expected goal differential based on rating
    # Roughly: 0.5 goal advantage per 1.0 rating point
    tgs['expected_goal_diff'] = tgs['rating_advantage'] * 0.5
    
    # Performance vs expected
    tgs['goal_diff_vs_expected'] = tgs['goal_diff_raw'] - tgs['expected_goal_diff']
    
    # Performance flag
    tgs['performance_flag'] = np.where(
        tgs['goal_diff_vs_expected'] > 0.5, 'Over',
        np.where(tgs['goal_diff_vs_expected'] < -0.5, 'Under', 'Expected')
    )
    
    # Win indicator
    tgs['win'] = (tgs['goal_diff_raw'] > 0).astype(int)
    tgs['loss'] = (tgs['goal_diff_raw'] < 0).astype(int)
    tgs['tie'] = (tgs['goal_diff_raw'] == 0).astype(int)
    
    # Clean up intermediate columns
    tgs = tgs.drop(columns=['rating_multiplier'], errors='ignore')
    
    # Summary
    final_cols = len(tgs.columns)
    new_cols = final_cols - orig_cols
    
    print(f"\n{'=' * 60}")
    print("ENHANCEMENT SUMMARY")
    print(f"{'=' * 60}")
    print(f"Original columns: {orig_cols}")
    print(f"Final columns: {final_cols}")
    print(f"Net new columns: {new_cols}")
    print(f"Rows: {len(tgs)}")
    
    # New columns list
    orig_cols_list = pd.read_csv(OUTPUT_DIR / 'fact_team_game_stats.csv').columns.tolist()
    new_rating_cols = [c for c in tgs.columns if c not in orig_cols_list]
    print(f"\nNew columns added ({len(new_rating_cols)}):")
    for col in new_rating_cols:
        non_null = tgs[col].notna().sum()
        print(f"  {col}: {non_null}/{len(tgs)} populated")
    
    # Sample output
    print(f"\nSample data:")
    sample_cols = ['team_name', 'game_id', 'goals', 'goals_against_raw', 'gf_adj', 'ga_adj', 'goal_diff_adj', 'performance_flag']
    sample_cols = [c for c in sample_cols if c in tgs.columns]
    print(tgs[sample_cols].to_string(index=False))
    
    # Save
    tgs.to_csv(OUTPUT_DIR / 'fact_team_game_stats.csv', index=False)
    print(f"\n✓ Saved enhanced fact_team_game_stats.csv")
    
    return tgs


if __name__ == '__main__':
    enhance_team_game_stats()
    print("\n✓ Team game stats enhancement complete!")
