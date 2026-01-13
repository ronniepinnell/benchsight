#!/usr/bin/env python3
"""
BenchSight Table Validation Script
Performs field-level validation on all Tier 1 tables.

Usage: python scripts/validate_tables.py
"""

import pandas as pd
import os
from datetime import datetime

OUTPUT_DIR = 'data/output'

def validate_dim_player():
    """Validate dim_player table"""
    df = pd.read_csv(f'{OUTPUT_DIR}/dim_player.csv')
    results = {
        'table': 'dim_player',
        'rows': len(df),
        'status': 'VALID',
        'issues': []
    }
    
    # Check unique player_id
    if df['player_id'].nunique() != len(df):
        results['issues'].append('Duplicate player_ids found')
        results['status'] = 'INVALID'
    
    # Check null names
    if df['player_first_name'].isnull().any() or df['player_last_name'].isnull().any():
        results['issues'].append('Null player names found')
        results['status'] = 'WARNING'
    
    # Check position values
    valid_positions = ['Forward', 'Defense', 'Goalie']
    invalid_pos = df[~df['player_primary_position'].isin(valid_positions)]
    if len(invalid_pos) > 0:
        results['issues'].append(f'{len(invalid_pos)} invalid positions')
        results['status'] = 'WARNING'
    
    return results

def validate_dim_team():
    """Validate dim_team table"""
    df = pd.read_csv(f'{OUTPUT_DIR}/dim_team.csv')
    results = {
        'table': 'dim_team',
        'rows': len(df),
        'status': 'VALID',
        'issues': []
    }
    
    if df['team_id'].nunique() != len(df):
        results['issues'].append('Duplicate team_ids found')
        results['status'] = 'INVALID'
    
    return results

def validate_dim_schedule():
    """Validate dim_schedule table"""
    df = pd.read_csv(f'{OUTPUT_DIR}/dim_schedule.csv')
    results = {
        'table': 'dim_schedule',
        'rows': len(df),
        'status': 'VALID',
        'issues': []
    }
    
    # Check same team playing itself
    same_team = df[df['home_team_id'] == df['away_team_id']]
    if len(same_team) > 0:
        results['issues'].append(f'{len(same_team)} games with same home/away team')
        results['status'] = 'INVALID'
    
    # Check negative goals
    if (df['home_total_goals'] < 0).any() or (df['away_total_goals'] < 0).any():
        results['issues'].append('Negative goal values found')
        results['status'] = 'INVALID'
    
    return results

def validate_fact_events():
    """Validate fact_events table"""
    df = pd.read_csv(f'{OUTPUT_DIR}/fact_events.csv')
    schedule = pd.read_csv(f'{OUTPUT_DIR}/dim_schedule.csv')
    
    results = {
        'table': 'fact_events',
        'rows': len(df),
        'status': 'VALID',
        'issues': []
    }
    
    # Check goal counting
    goals = df[(df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')]
    
    # Cross-check with schedule for tracked games
    tracked_games = df['game_id'].unique()
    for game_id in tracked_games:
        event_goals = len(goals[goals['game_id'] == game_id])
        sched = schedule[schedule['game_id'] == game_id]
        if len(sched) > 0:
            sched_goals = sched.iloc[0]['home_total_goals'] + sched.iloc[0]['away_total_goals']
            if event_goals != sched_goals:
                results['issues'].append(f'Game {game_id}: {event_goals} goals in events vs {sched_goals} in schedule')
                results['status'] = 'WARNING'
    
    # Check is_goal flag
    if 'is_goal' in df.columns:
        is_goal_count = (df['is_goal'] == True).sum()
        if is_goal_count != len(goals):
            results['issues'].append(f'is_goal flag mismatch: {is_goal_count} vs {len(goals)} Goal/Goal_Scored')
            results['status'] = 'WARNING'
    
    return results

def validate_fact_player_game_stats():
    """Validate fact_player_game_stats table"""
    df = pd.read_csv(f'{OUTPUT_DIR}/fact_player_game_stats.csv')
    events = pd.read_csv(f'{OUTPUT_DIR}/fact_events.csv')
    
    results = {
        'table': 'fact_player_game_stats',
        'rows': len(df),
        'status': 'VALID',
        'issues': []
    }
    
    # Check points calculation
    df['calc_points'] = df['goals'] + df['assists']
    points_mismatch = df[df['points'] != df['calc_points']]
    if len(points_mismatch) > 0:
        results['issues'].append(f'{len(points_mismatch)} rows with points != goals + assists')
        results['status'] = 'INVALID'
    
    # Cross-check goals with fact_events
    goals_in_events = events[(events['event_type'] == 'Goal') & (events['event_detail'] == 'Goal_Scored')]
    for game_id in df['game_id'].unique():
        stats_goals = df[df['game_id'] == game_id]['goals'].sum()
        event_goals = len(goals_in_events[goals_in_events['game_id'] == game_id])
        if stats_goals != event_goals:
            results['issues'].append(f'Game {game_id}: {stats_goals} goals in stats vs {event_goals} in events')
            results['status'] = 'WARNING'
    
    return results

def validate_fact_goalie_game_stats():
    """Validate fact_goalie_game_stats table"""
    df = pd.read_csv(f'{OUTPUT_DIR}/fact_goalie_game_stats.csv')
    players = pd.read_csv(f'{OUTPUT_DIR}/dim_player.csv')
    
    results = {
        'table': 'fact_goalie_game_stats',
        'rows': len(df),
        'status': 'VALID',
        'issues': []
    }
    
    # Check all players are goalies
    goalies = players[players['player_primary_position'] == 'Goalie']['player_id'].tolist()
    non_goalies = df[~df['player_id'].isin(goalies)]
    if len(non_goalies) > 0:
        results['issues'].append(f'{len(non_goalies)} non-goalie players in goalie stats')
        results['status'] = 'WARNING'
    
    # Check shots_against = saves + goals_against
    df['calc_sa'] = df['saves'] + df['goals_against']
    sa_mismatch = df[df['shots_against'] != df['calc_sa']]
    if len(sa_mismatch) > 0:
        results['issues'].append(f'{len(sa_mismatch)} rows with shots_against != saves + goals_against')
        results['status'] = 'INVALID'
    
    # Check for duplicate stats (both goalies having same stats)
    for game_id in df['game_id'].unique():
        game_df = df[df['game_id'] == game_id]
        if len(game_df) == 2:
            if game_df.iloc[0]['goals_against'] == game_df.iloc[1]['goals_against']:
                results['issues'].append(f'Game {game_id}: Both goalies have identical stats (likely bug)')
                results['status'] = 'WARNING'
    
    return results

def run_all_validations():
    """Run all table validations"""
    print("=" * 60)
    print("BENCHSIGHT TABLE VALIDATION REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    validators = [
        validate_dim_player,
        validate_dim_team,
        validate_dim_schedule,
        validate_fact_events,
        validate_fact_player_game_stats,
        validate_fact_goalie_game_stats,
    ]
    
    all_results = []
    for validator in validators:
        result = validator()
        all_results.append(result)
        
        status_icon = '✅' if result['status'] == 'VALID' else '⚠️' if result['status'] == 'WARNING' else '❌'
        print(f"\n{status_icon} {result['table']}: {result['status']} ({result['rows']} rows)")
        
        if result['issues']:
            for issue in result['issues']:
                print(f"   - {issue}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    valid = sum(1 for r in all_results if r['status'] == 'VALID')
    warning = sum(1 for r in all_results if r['status'] == 'WARNING')
    invalid = sum(1 for r in all_results if r['status'] == 'INVALID')
    
    print(f"Valid:   {valid}")
    print(f"Warning: {warning}")
    print(f"Invalid: {invalid}")
    
    return all_results

if __name__ == '__main__':
    run_all_validations()
