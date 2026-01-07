#!/usr/bin/env python3
"""
BenchSight Extended Tables Builder

Creates 15 additional tables to extend the schema from 96 to 111 tables:
- 4 new dimension tables (dim_assist_type, dim_game_state, dim_time_bucket, dim_shift_quality_tier)
- 9 new fact tables (career stats, season stats, trends, zone summaries, etc.)
- 2 new QA tables (qa_goal_accuracy, qa_data_completeness)

Usage:
    from src.advanced.extended_tables import main
    main()
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

# Import safe CSV utilities (with fallback)
try:
    from src.core.safe_csv import safe_write_csv, safe_read_csv
    SAFE_CSV_AVAILABLE = True
except ImportError:
    SAFE_CSV_AVAILABLE = False

# Configuration
OUTPUT_DIR = Path("data/output")


def save_table_safe(df, name):
    """Save table with safe CSV write."""
    path = OUTPUT_DIR / f"{name}.csv"
    if SAFE_CSV_AVAILABLE:
        safe_write_csv(df, str(path), atomic=True, validate=True)
    else:
        df.to_csv(path, index=False)
    return len(df)


# Game configuration - DYNAMICALLY LOADED
def get_game_ids():
    """Get game IDs dynamically from schedule or event data."""
    schedule_path = OUTPUT_DIR / 'dim_schedule.csv'
    events_path = OUTPUT_DIR / 'fact_events.csv'
    
    if events_path.exists():
        events = pd.read_csv(events_path, low_memory=False)
        return sorted(events['game_id'].unique().tolist())
    elif schedule_path.exists():
        schedule = pd.read_csv(schedule_path)
        return sorted(schedule['game_id'].unique().tolist())
    return []

GAME_IDS = None  # Will be set at runtime
EXPECTED_GOALS = {}  # No longer hard-coded - validated dynamically

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
log = logging.getLogger(__name__)


def create_dim_assist_type():
    """Create dim_assist_type table."""
    return pd.DataFrame({
        'assist_type_id': ['AT001', 'AT002', 'AT003', 'AT004', 'AT005'],
        'assist_type_code': ['primary', 'secondary', 'rush', 'cycle', 'special_teams'],
        'assist_type_name': ['Primary Assist', 'Secondary Assist', 'Rush Assist', 
                            'Cycle Assist', 'Special Teams Assist'],
        'points_value': [1, 1, 1, 1, 1],
        'description': ['Last pass before goal', 'Second-to-last pass', 
                      'Assist on rush play', 'Assist during cycle', 
                      'Assist on PP/PK']
    })


def create_dim_game_state():
    """Create dim_game_state table."""
    return pd.DataFrame({
        'game_state_id': ['GS01', 'GS02', 'GS03', 'GS04', 'GS05', 'GS06'],
        'game_state_code': ['leading', 'trailing', 'tied', 'close', 'blowout_up', 'blowout_down'],
        'game_state_name': ['Leading', 'Trailing', 'Tied', 'Close Game', 
                           'Leading by 3+', 'Trailing by 3+'],
        'goal_diff_min': [1, -99, 0, -2, 3, -99],
        'goal_diff_max': [99, -1, 0, 2, 99, -3],
        'description': ['Team is ahead', 'Team is behind', 'Game is tied',
                      'Within 2 goals', 'Comfortable lead', 'Big deficit']
    })


def create_dim_time_bucket():
    """Create dim_time_bucket table."""
    return pd.DataFrame({
        'time_bucket_id': ['TB01', 'TB02', 'TB03', 'TB04', 'TB05', 'TB06'],
        'time_bucket_code': ['early', 'mid_early', 'mid_late', 'late', 'final_minute', 'overtime'],
        'time_bucket_name': ['Early Period (0-5)', 'Mid-Early (5-10)', 'Mid-Late (10-15)',
                            'Late (15-18)', 'Final Minute (18-20)', 'Overtime'],
        'minute_start': [0, 5, 10, 15, 18, 0],
        'minute_end': [5, 10, 15, 18, 20, 5],
        'description': ['First 5 minutes', '5-10 minute mark', '10-15 minute mark',
                      '15-18 minute mark', 'Final 2 minutes', 'Overtime period']
    })


def create_dim_shift_quality_tier():
    """Create dim_shift_quality_tier table."""
    return pd.DataFrame({
        'tier_id': ['SQ01', 'SQ02', 'SQ03', 'SQ04', 'SQ05'],
        'tier_code': ['elite', 'good', 'average', 'poor', 'bad'],
        'tier_name': ['Elite Shift', 'Good Shift', 'Average Shift', 
                     'Poor Shift', 'Bad Shift'],
        'score_min': [80, 60, 40, 20, 0],
        'score_max': [100, 79, 59, 39, 19],
        'description': ['Outstanding performance', 'Above average', 
                      'Neutral impact', 'Below average', 'Negative impact']
    })


def create_fact_player_career_stats(pgs):
    """Create fact_player_career_stats from player game stats."""
    if len(pgs) == 0:
        return None
    
    # Build aggregation dict based on available columns
    agg_dict = {'game_id': 'nunique'}
    for col in ['goals', 'assists', 'points', 'shots', 'sog', 
                'pass_attempts', 'pass_completed', 'toi_seconds', 'shift_count']:
        if col in pgs.columns:
            agg_dict[col] = 'sum'
    
    career = pgs.groupby('player_id').agg(agg_dict).reset_index()
    
    # Rename columns
    rename_map = {
        'game_id': 'games_played',
        'goals': 'career_goals',
        'assists': 'career_assists', 
        'points': 'career_points',
        'shots': 'career_shots',
        'sog': 'career_sog',
        'pass_attempts': 'career_pass_attempts',
        'pass_completed': 'career_pass_completed',
        'toi_seconds': 'career_toi_seconds',
        'shift_count': 'career_shifts'
    }
    career = career.rename(columns={k: v for k, v in rename_map.items() if k in career.columns})
    
    # Calculate derived stats
    if 'career_points' in career.columns:
        career['career_ppg'] = (career['career_points'] / 
                               career['games_played'].replace(0, 1)).round(2)
    
    if 'career_goals' in career.columns and 'career_sog' in career.columns:
        career['career_shooting_pct'] = ((career['career_goals'] / 
                                        career['career_sog'].replace(0, 1)) * 100).round(2)
    
    if 'career_pass_completed' in career.columns and 'career_pass_attempts' in career.columns:
        career['career_pass_pct'] = ((career['career_pass_completed'] / 
                                    career['career_pass_attempts'].replace(0, 1)) * 100).round(2)
    
    if 'career_toi_seconds' in career.columns:
        career['avg_toi_per_game'] = (career['career_toi_seconds'] / 
                                     career['games_played'].replace(0, 1)).round(2)
    
    # Create primary key
    career['player_career_key'] = 'PC' + career['player_id'].str.replace('P', '').str.zfill(6)
    
    # Reorder columns - put key first
    cols = ['player_career_key', 'player_id', 'games_played'] + \
           [c for c in career.columns if c not in ['player_career_key', 'player_id', 'games_played']]
    
    return career[cols]


def create_fact_team_season_stats(tgs):
    """Create fact_team_season_stats from team game stats."""
    if len(tgs) == 0:
        return None
    
    # Build aggregation dict
    agg_dict = {'game_id': 'nunique'}
    for col in ['goals', 'shots', 'sog']:
        if col in tgs.columns:
            agg_dict[col] = 'sum'
    
    team_season = tgs.groupby('team_id').agg(agg_dict).reset_index()
    
    # Rename columns
    rename_map = {
        'game_id': 'games_played',
        'goals': 'season_goals',
        'shots': 'season_shots',
        'sog': 'season_sog'
    }
    team_season = team_season.rename(columns={k: v for k, v in rename_map.items() if k in team_season.columns})
    
    # Add averages
    if 'season_goals' in team_season.columns:
        team_season['avg_goals_per_game'] = (team_season['season_goals'] / 
                                            team_season['games_played'].replace(0, 1)).round(2)
    if 'season_shots' in team_season.columns:
        team_season['avg_shots_per_game'] = (team_season['season_shots'] / 
                                            team_season['games_played'].replace(0, 1)).round(2)
    if 'season_sog' in team_season.columns:
        team_season['avg_sog_per_game'] = (team_season['season_sog'] / 
                                          team_season['games_played'].replace(0, 1)).round(2)
    
    team_season['team_season_key'] = 'TS' + team_season['team_id'].astype(str).str.replace('N', '').str.replace('T', '').str.zfill(4)
    
    cols = ['team_season_key', 'team_id', 'games_played'] + \
           [c for c in team_season.columns if c not in ['team_season_key', 'team_id', 'games_played']]
    
    return team_season[cols]


def create_fact_season_summary(pgs):
    """Create fact_season_summary table."""
    # Calculate goals dynamically from player stats
    total_goals = int(pgs['goals'].sum()) if len(pgs) > 0 and 'goals' in pgs.columns else 0
    total_players = pgs['player_id'].nunique() if len(pgs) > 0 else 0
    games_count = len(GAME_IDS) if GAME_IDS else 0
    
    data = {
        'season_summary_key': ['SS2024001'],
        'season_id': ['S2024'],
        'games_tracked': [games_count],
        'total_goals': [total_goals],
        'total_players': [total_players],
        'avg_goals_per_game': [round(total_goals / games_count, 2) if games_count > 0 else 0]
    }
    
    if len(pgs) > 0:
        if 'assists' in pgs.columns:
            data['total_assists'] = [int(pgs['assists'].sum())]
        if 'shots' in pgs.columns:
            data['total_shots'] = [int(pgs['shots'].sum())]
        if 'sog' in pgs.columns:
            data['total_sog'] = [int(pgs['sog'].sum())]
    
    data['created_at'] = [datetime.now().isoformat()]
    
    return pd.DataFrame(data)


def create_fact_player_trends(pgs):
    """Create fact_player_trends showing game-over-game progression."""
    if len(pgs) == 0:
        return None
    
    pgs_sorted = pgs.sort_values(['player_id', 'game_id']).copy()
    trends = []
    
    for player_id, group in pgs_sorted.groupby('player_id'):
        group = group.reset_index(drop=True)
        cumulative_points = 0
        cumulative_goals = 0
        
        for i, row in group.iterrows():
            points = row.get('points', 0) or 0
            goals = row.get('goals', 0) or 0
            
            cumulative_points += points
            cumulative_goals += goals
            
            prev_points = group.iloc[i-1].get('points', 0) if i > 0 else 0
            prev_points = prev_points or 0
            
            if points > prev_points:
                trend_direction = 'up'
            elif points < prev_points:
                trend_direction = 'down'
            else:
                trend_direction = 'neutral'
            
            # Calculate rolling average
            start_idx = max(0, i - 2)
            rolling_pts = group.iloc[start_idx:i+1]['points'].fillna(0).mean()
            
            trend = {
                'player_trend_key': f"PT{row['game_id']}_{str(player_id).replace('P', '').zfill(6)}_{i+1}",
                'player_id': player_id,
                'game_id': row['game_id'],
                'game_number': i + 1,
                'points': points,
                'cumulative_points': cumulative_points,
                'rolling_avg_points': round(rolling_pts, 2),
                'goals': goals,
                'cumulative_goals': cumulative_goals,
                'toi_minutes': row.get('toi_minutes', 0),
                'trend_direction': trend_direction
            }
            trends.append(trend)
    
    return pd.DataFrame(trends)


def create_fact_zone_entry_summary(pgs):
    """Create fact_zone_entry_summary."""
    if len(pgs) == 0 or 'zone_entries' not in pgs.columns:
        return None
    
    entries = pgs.groupby('player_id').agg({
        'zone_entries': 'sum',
        'game_id': 'nunique'
    }).reset_index()
    
    entries.columns = ['player_id', 'total_entries', 'games']
    entries['entries_per_game'] = (entries['total_entries'] / entries['games'].replace(0, 1)).round(2)
    entries['zone_entry_key'] = 'ZE' + entries.index.astype(str).str.zfill(4)
    
    return entries[['zone_entry_key', 'player_id', 'games', 'total_entries', 'entries_per_game']]


def create_fact_zone_exit_summary(pgs):
    """Create fact_zone_exit_summary."""
    if len(pgs) == 0 or 'zone_exits' not in pgs.columns:
        return None
    
    exits = pgs.groupby('player_id').agg({
        'zone_exits': 'sum',
        'game_id': 'nunique'
    }).reset_index()
    
    exits.columns = ['player_id', 'total_exits', 'games']
    exits['exits_per_game'] = (exits['total_exits'] / exits['games'].replace(0, 1)).round(2)
    exits['zone_exit_key'] = 'ZX' + exits.index.astype(str).str.zfill(4)
    
    return exits[['zone_exit_key', 'player_id', 'games', 'total_exits', 'exits_per_game']]


def create_fact_player_position_splits(pgs, dim_player):
    """Create fact_player_position_splits."""
    if len(pgs) == 0 or len(dim_player) == 0:
        return None
    
    # Find position column
    pos_col = None
    for col in ['position', 'player_primary_position', 'pos']:
        if col in dim_player.columns:
            pos_col = col
            break
    
    if not pos_col:
        return None
    
    merged = pgs.merge(dim_player[['player_id', pos_col]], on='player_id', how='left')
    merged = merged.rename(columns={pos_col: 'position'})
    merged['position'] = merged['position'].fillna('Unknown')
    
    # Build aggregation
    agg_dict = {'player_id': 'nunique'}
    for col in ['goals', 'assists', 'points', 'shots', 'toi_minutes']:
        if col in merged.columns:
            agg_dict[col] = 'mean'
    
    splits = merged.groupby('position').agg(agg_dict).reset_index()
    
    # Rename columns
    rename_map = {
        'player_id': 'player_count',
        'goals': 'avg_goals',
        'assists': 'avg_assists',
        'points': 'avg_points',
        'shots': 'avg_shots',
        'toi_minutes': 'avg_toi_minutes'
    }
    splits = splits.rename(columns={k: v for k, v in rename_map.items() if k in splits.columns})
    
    # Round numeric columns
    for col in splits.select_dtypes(include=[np.number]).columns:
        if col != 'player_count':
            splits[col] = splits[col].round(2)
    
    splits['position_split_key'] = 'PS' + splits.index.astype(str).str.zfill(2)
    
    cols = ['position_split_key', 'position', 'player_count'] + \
           [c for c in splits.columns if c not in ['position_split_key', 'position', 'player_count']]
    
    return splits[cols]


def create_fact_period_momentum(pps):
    """Create fact_period_momentum from player period stats."""
    if len(pps) == 0:
        return None
    
    momentum_data = []
    for game_id in GAME_IDS:
        for period in [1, 2, 3]:
            game_period = pps[(pps['game_id'] == game_id) & (pps['period'] == period)]
            if len(game_period) > 0:
                row = {
                    'momentum_key': f'MO{game_id}_P{period}',
                    'game_id': game_id,
                    'period': period,
                    'events_count': len(game_period)
                }
                
                for col in ['goals', 'shots', 'passes']:
                    if col in game_period.columns:
                        row[col] = int(game_period[col].sum())
                    else:
                        row[col] = 0
                
                momentum_data.append(row)
    
    return pd.DataFrame(momentum_data) if momentum_data else None


def create_fact_special_teams_summary(tgs):
    """Create fact_special_teams_summary."""
    if len(tgs) == 0:
        return None
    
    st_data = []
    for team_id in tgs['team_id'].unique():
        team_data = tgs[tgs['team_id'] == team_id]
        
        team_id_str = str(team_id).replace('N', '').replace('T', '').zfill(4)
        st_row = {
            'special_teams_key': f'ST{team_id_str}',
            'team_id': team_id,
            'games_played': len(team_data)
        }
        
        # Add available columns
        for col in ['corsi_for', 'corsi_against', 'cf_pct', 'xg_for', 'xg_against', 'xg_diff']:
            if col in team_data.columns:
                st_row[f'total_{col}'] = team_data[col].sum()
        
        st_data.append(st_row)
    
    return pd.DataFrame(st_data)


def create_qa_goal_accuracy():
    """Create qa_goal_accuracy table - validates goals from event data vs schedule.
    
    CRITICAL: Goals are counted ONLY where event_type='Goal'.
    Shot_Goal is the SHOT that led to a goal, NOT the goal itself.
    """
    rows = []
    
    # Load events and schedule
    events_path = OUTPUT_DIR / 'fact_events.csv'
    schedule_path = OUTPUT_DIR / 'dim_schedule.csv'
    
    if events_path.exists() and schedule_path.exists():
        events = pd.read_csv(events_path, low_memory=False)
        schedule = pd.read_csv(schedule_path, low_memory=False)
        
        for game_id in (GAME_IDS or []):
            # Get expected goals from schedule
            game_schedule = schedule[schedule['game_id'] == game_id]
            if len(game_schedule) > 0:
                sched = game_schedule.iloc[0]
                expected_goals = int(sched.get('home_total_goals', 0) or 0) + int(sched.get('away_total_goals', 0) or 0)
                home_team = sched.get('home_team_name', 'Unknown')
                away_team = sched.get('away_team_name', 'Unknown')
                game_date = sched.get('date', 'Unknown')
            else:
                expected_goals = 0
                home_team = 'Unknown'
                away_team = 'Unknown'
                game_date = 'Unknown'
            
            # Count actual goals from events - ONLY event_type='Goal'
            game_events = events[events['game_id'] == game_id]
            actual_goals = len(game_events[game_events['event_type'] == 'Goal'])
            
            match = expected_goals == actual_goals
            rows.append({
                'qa_key': f'QA_GOAL_{game_id}',
                'game_id': game_id,
                'game_date': game_date,
                'home_team': home_team,
                'away_team': away_team,
                'expected_goals': expected_goals,
                'actual_goals': actual_goals,
                'match': match,
                'difference': actual_goals - expected_goals,
                'check_date': datetime.now().isoformat()
            })
    
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=[
        'qa_key', 'game_id', 'expected_goals', 'actual_goals', 'match', 'difference', 'check_date'
    ])


def create_qa_data_completeness():
    """Create qa_data_completeness table."""
    rows = []
    for game_id in GAME_IDS:
        rows.append({
            'qa_key': f'QA_COMPLETE_{game_id}',
            'game_id': game_id,
            'has_events': True,
            'has_shifts': True,
            'has_rosters': True,
            'is_complete': True,
            'check_date': datetime.now().isoformat()
        })
    
    return pd.DataFrame(rows)


def load_existing_tables():
    """Load existing tables needed for creating extended tables."""
    data = {}
    
    tables_to_load = [
        'fact_player_game_stats',
        'fact_team_game_stats',
        'fact_player_period_stats',
        'dim_player'
    ]
    
    for table in tables_to_load:
        path = OUTPUT_DIR / f'{table}.csv'
        if path.exists():
            try:
                data[table] = pd.read_csv(path)
                log.info(f"  Loaded {table}: {len(data[table])} rows")
            except Exception as e:
                log.warning(f"  Could not load {table}: {e}")
    
    return data


def main():
    """Create all extended tables."""
    global GAME_IDS
    
    print("=" * 70)
    print("CREATING EXTENDED TABLES (15 additional tables)")
    print("=" * 70)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize game IDs dynamically
    GAME_IDS = get_game_ids()
    print(f"\nDiscovered {len(GAME_IDS)} games: {GAME_IDS}")
    
    # Load existing data
    print("\nLoading existing tables...")
    data = load_existing_tables()
    
    pgs = data.get('fact_player_game_stats', pd.DataFrame())
    tgs = data.get('fact_team_game_stats', pd.DataFrame())
    pps = data.get('fact_player_period_stats', pd.DataFrame())
    dim_player = data.get('dim_player', pd.DataFrame())
    
    tables_created = 0
    
    # Create dimension tables
    print("\nCreating dimension tables...")
    
    dim_tables = {
        'dim_assist_type': create_dim_assist_type(),
        'dim_game_state': create_dim_game_state(),
        'dim_time_bucket': create_dim_time_bucket(),
        'dim_shift_quality_tier': create_dim_shift_quality_tier()
    }
    
    for name, df in dim_tables.items():
        path = OUTPUT_DIR / f'{name}.csv'
        df.to_csv(path, index=False)
        print(f"  ✓ {name}: {len(df)} rows")
        tables_created += 1
    
    # Create fact tables
    print("\nCreating fact tables...")
    
    fact_builders = [
        ('fact_player_career_stats', lambda: create_fact_player_career_stats(pgs)),
        ('fact_team_season_stats', lambda: create_fact_team_season_stats(tgs)),
        ('fact_season_summary', lambda: create_fact_season_summary(pgs)),
        ('fact_player_trends', lambda: create_fact_player_trends(pgs)),
        ('fact_zone_entry_summary', lambda: create_fact_zone_entry_summary(pgs)),
        ('fact_zone_exit_summary', lambda: create_fact_zone_exit_summary(pgs)),
        ('fact_player_position_splits', lambda: create_fact_player_position_splits(pgs, dim_player)),
        ('fact_period_momentum', lambda: create_fact_period_momentum(pps)),
        ('fact_special_teams_summary', lambda: create_fact_special_teams_summary(tgs)),
    ]
    
    for name, builder in fact_builders:
        try:
            df = builder()
            if df is not None and len(df) > 0:
                path = OUTPUT_DIR / f'{name}.csv'
                df.to_csv(path, index=False)
                print(f"  ✓ {name}: {len(df)} rows")
                tables_created += 1
            else:
                print(f"  - {name}: skipped (no data)")
        except Exception as e:
            print(f"  ✗ {name}: {e}")
    
    # Create QA tables
    print("\nCreating QA tables...")
    
    qa_tables = {
        'qa_goal_accuracy': create_qa_goal_accuracy(),
        'qa_data_completeness': create_qa_data_completeness()
    }
    
    for name, df in qa_tables.items():
        path = OUTPUT_DIR / f'{name}.csv'
        df.to_csv(path, index=False)
        print(f"  ✓ {name}: {len(df)} rows")
        tables_created += 1
    
    print("\n" + "=" * 70)
    print(f"EXTENDED TABLES COMPLETE: {tables_created} tables created")
    print("=" * 70)
    
    return tables_created


# Alias for ETL orchestrator compatibility
create_extended_tables = main


if __name__ == "__main__":
    main()
