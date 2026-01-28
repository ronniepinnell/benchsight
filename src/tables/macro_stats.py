"""
Macro Stats Tables - Season/Career aggregations

v29.0 - Uses game_type_aggregator for consistent game_type splits
v28.2 - Two tiers:
1. BASIC: From roster/schedule data (G, A, PIM, GP, per_game rates)
2. ADVANCED: From tracking data (micro stats aggregated)

Tables created:
- fact_player_season_stats_basic (skaters only)
- fact_player_career_stats_basic (skaters only)
- fact_goalie_season_stats_basic
- fact_goalie_career_stats_basic
- fact_goalie_season_stats (advanced, from tracking)
- fact_goalie_career_stats (advanced, from tracking)
- fact_team_season_stats_basic
- Enhanced: fact_player_career_stats (advanced)
"""

import pandas as pd
import numpy as np
from datetime import datetime
from src.tables.core_facts import load_table, save_table
from src.utils.game_type_aggregator import (
    GAME_TYPE_SPLITS,
    add_game_type_to_df,
    get_team_record_from_schedule,
    get_goalie_record_from_games
)


def is_goalie(position: str) -> bool:
    """Check if position is goalie."""
    return 'goalie' in str(position).lower()


# =============================================================================
# BASIC TABLES (from roster/schedule - official league stats)
# =============================================================================

def create_fact_player_season_stats_basic() -> pd.DataFrame:
    """
    Create basic player season stats from roster data.
    SKATERS ONLY - excludes goalies.
    Source: fact_gameroster (official noradhockey.com data)
    
    Grain: player_id + season_id + game_type
    Uses GAME_TYPE_SPLITS from game_type_aggregator (single source of truth)
    """
    print("\nBuilding fact_player_season_stats_basic (SKATERS ONLY)...")
    
    roster = load_table('fact_gameroster')
    schedule = load_table('dim_schedule')
    
    if len(roster) == 0:
        print("  ERROR: fact_gameroster not found!")
        return pd.DataFrame()
    
    # Filter to skaters only
    skaters = roster[~roster['player_position'].astype(str).str.lower().str.contains('goalie', na=False)]
    
    # Add game_type using shared utility
    skaters = add_game_type_to_df(skaters, schedule)
    
    all_stats = []
    
    # Get unique player-season combinations
    # VECTORIZED: Use groupby instead of iterrows
    grouped = skaters.groupby(['player_id', 'season_id', 'game_type'])
    
    # Get player metadata (first occurrence per player_id, season_id)
    player_meta = skaters[['player_id', 'season_id', 'player_full_name', 'team_id', 
                           'team_name', 'player_position', 'season']].drop_duplicates(
                               subset=['player_id', 'season_id']).set_index(['player_id', 'season_id'])
    
    for (player_id, season_id, game_type), games in grouped:
        if len(games) == 0:
            continue
        
        # Get metadata
        meta = player_meta.loc[(player_id, season_id)]
        
        gp = games['game_id'].nunique()
        goals = int(games['goals'].sum())
        assists = int(games['assist'].sum())
        points = int(games['points'].sum())
        pim = int(games['pim'].sum())
        
        stats = {
            'player_season_basic_key': f"{player_id}_{season_id}_{game_type}",
            'player_id': player_id,
            'season_id': season_id,
            'season': meta.get('season', ''),
            'game_type': game_type,
            'player_name': meta.get('player_full_name', ''),
            'team_id': meta.get('team_id', ''),
            'team_name': meta.get('team_name', ''),
            'position': meta.get('player_position', ''),
            'games_played': gp,
            'goals': goals,
            'assists': assists,
            'points': points,
            'pim': pim,
            'goals_per_game': round(goals / gp, 2) if gp > 0 else 0,
            'assists_per_game': round(assists / gp, 2) if gp > 0 else 0,
            'points_per_game': round(points / gp, 2) if gp > 0 else 0,
            'pim_per_game': round(pim / gp, 2) if gp > 0 else 0,
            '_export_timestamp': datetime.now().isoformat(),
        }
        all_stats.append(stats)
    
    df = pd.DataFrame(all_stats)
    
    # Reorder columns
    cols = ['player_season_basic_key', 'player_id', 'season_id', 'season', 'game_type',
            'player_name', 'team_id', 'team_name', 'position', 'games_played',
            'goals', 'assists', 'points', 'pim',
            'goals_per_game', 'assists_per_game', 'points_per_game', 'pim_per_game',
            '_export_timestamp']
    df = df[[c for c in cols if c in df.columns]]
    
    print(f"  Created {len(df)} player-season-gametype records with {len(df.columns)} columns")
    return df


def create_fact_player_career_stats_basic() -> pd.DataFrame:
    """
    Create basic player career stats from roster data.
    SKATERS ONLY - excludes goalies.
    
    Grain: player_id + season_id + game_type (Regular/Playoffs/All)
    Uses GAME_TYPE_SPLITS from game_type_aggregator (single source of truth)
    """
    print("\nBuilding fact_player_career_stats_basic (SKATERS ONLY)...")
    
    roster = load_table('fact_gameroster')
    schedule = load_table('dim_schedule')
    
    if len(roster) == 0:
        return pd.DataFrame()
    
    # Filter to skaters
    skaters = roster[~roster['player_position'].astype(str).str.lower().str.contains('goalie', na=False)]
    
    # Add game_type from schedule
    skaters = add_game_type_to_df(skaters, schedule)
    
    all_stats = []
    
    # Get unique player-season combinations
    player_seasons = skaters[['player_id', 'season_id', 'player_full_name', 'player_position', 
                               'team_name']].drop_duplicates(subset=['player_id', 'season_id'])
    
    for _, ps in player_seasons.iterrows():
        player_id = ps['player_id']
        season_id = ps['season_id']
        
        player_games = skaters[(skaters['player_id'] == player_id) & 
                               (skaters['season_id'] == season_id)]
        
        # Split by game_type
        for game_type in GAME_TYPE_SPLITS:
            if game_type == 'All':
                games = player_games
            else:
                games = player_games[player_games['game_type'] == game_type]
            
            if len(games) == 0:
                continue
            
            # Aggregate stats
            career_games = games['game_id'].nunique()
            career_goals = int(games['goals'].sum())
            career_assists = int(games['assist'].sum())
            career_points = int(games['points'].sum())
            career_pim = int(games['pim'].sum())
            
            # Per-game rates
            goals_per_game = round(career_goals / career_games, 2) if career_games > 0 else 0.0
            assists_per_game = round(career_assists / career_games, 2) if career_games > 0 else 0.0
            points_per_game = round(career_points / career_games, 2) if career_games > 0 else 0.0
            pim_per_game = round(career_pim / career_games, 2) if career_games > 0 else 0.0
            
            stats = {
                'player_career_basic_key': f"{player_id}_{season_id}_{game_type}",
                'player_id': player_id,
                'season_id': season_id,
                'game_type': game_type,
                'player_name': ps['player_full_name'],
                'position': ps['player_position'],
                'current_team': ps['team_name'],
                'career_games': career_games,
                'career_goals': career_goals,
                'career_assists': career_assists,
                'career_points': career_points,
                'career_pim': career_pim,
                'goals_per_game': goals_per_game,
                'assists_per_game': assists_per_game,
                'points_per_game': points_per_game,
                'pim_per_game': pim_per_game,
                '_export_timestamp': datetime.now().isoformat(),
            }
            all_stats.append(stats)
    
    df = pd.DataFrame(all_stats)
    
    cols = ['player_career_basic_key', 'player_id', 'season_id', 'game_type', 
            'player_name', 'position', 'current_team',
            'career_games', 'career_goals', 'career_assists', 'career_points', 'career_pim',
            'goals_per_game', 'assists_per_game', 'points_per_game', 'pim_per_game',
            '_export_timestamp']
    df = df[[c for c in cols if c in df.columns]]
    
    print(f"  Created {len(df)} player career records (by season+type) with {len(df.columns)} columns")
    return df


def create_fact_goalie_season_stats_basic() -> pd.DataFrame:
    """
    Create basic goalie season stats from roster data.
    GOALIES ONLY.
    
    Grain: player_id + season_id + game_type
    Uses GAME_TYPE_SPLITS from game_type_aggregator (single source of truth)
    """
    print("\nBuilding fact_goalie_season_stats_basic (GOALIES ONLY)...")
    
    roster = load_table('fact_gameroster')
    schedule = load_table('dim_schedule')
    
    if len(roster) == 0:
        return pd.DataFrame()
    
    # Filter to goalies
    goalies = roster[roster['player_position'].astype(str).str.lower().str.contains('goalie', na=False)]
    
    if len(goalies) == 0:
        print("  No goalies found in roster")
        return pd.DataFrame()
    
    # Join to schedule for game_type and game result columns
    # Ensure consistent game_id types before merge (dtype optimization may create mismatches)
    schedule_cols = schedule[['game_id', 'game_type', 'home_team_name', 'away_team_name',
                              'home_total_goals', 'away_total_goals', 'home_team_t', 'away_team_t']].copy()
    schedule_cols['game_id'] = schedule_cols['game_id'].astype(str)
    goalies['game_id'] = goalies['game_id'].astype(str)
    goalies = goalies.merge(schedule_cols, on='game_id', how='left')
    goalies['game_type'] = goalies['game_type'].fillna('Regular')
    # Ensure goal columns are numeric (merge can sometimes affect dtypes)
    for col in ['home_total_goals', 'away_total_goals', 'home_team_t', 'away_team_t']:
        if col in goalies.columns:
            goalies[col] = pd.to_numeric(goalies[col], errors='coerce').fillna(0).astype(int)
    
    all_stats = []
    
    # Get unique goalie-season combinations
    # VECTORIZED: Use groupby instead of iterrows
    grouped = goalies.groupby(['player_id', 'season_id', 'game_type'])
    
    # Get goalie metadata
    goalie_meta = goalies[['player_id', 'season_id', 'player_full_name', 'team_id', 
                           'team_name', 'season']].drop_duplicates(
                               subset=['player_id', 'season_id']).set_index(['player_id', 'season_id'])
    
    for (player_id, season_id, game_type), games in grouped:
        if len(games) == 0:
            continue
        
        # Get metadata
        meta = goalie_meta.loc[(player_id, season_id)]
        
        # Use shared utility for W-L-T calculation
        record = get_goalie_record_from_games(games)
        
        gp = games['game_id'].nunique()
        ga = int(games['goals_against'].sum())
        so = int(games['shutouts'].sum())
        
        stats = {
            'goalie_season_basic_key': f"{player_id}_{season_id}_{game_type}",
            'player_id': player_id,
            'season_id': season_id,
            'season': meta.get('season', ''),
            'game_type': game_type,
            'player_name': meta.get('player_full_name', ''),
            'team_id': meta.get('team_id', ''),
            'team_name': meta.get('team_name', ''),
            'games_played': gp,
            'wins': record['wins'],
            'losses': record['losses'],
            'ties': record['ties'],
            'goals_against': ga,
            'gaa': round(ga / gp, 2) if gp > 0 else 0.0,
            'shutouts': so,
            'shutout_pct': round(so / gp * 100, 1) if gp > 0 else 0.0,
            'win_pct': round(record['wins'] / gp * 100, 1) if gp > 0 else 0.0,
            '_export_timestamp': datetime.now().isoformat(),
        }
        all_stats.append(stats)
    
    df = pd.DataFrame(all_stats)
    
    cols = ['goalie_season_basic_key', 'player_id', 'season_id', 'season', 'game_type',
            'player_name', 'team_id', 'team_name', 'games_played', 'wins', 'losses', 'ties',
            'goals_against', 'gaa', 'shutouts', 'shutout_pct', 'win_pct',
            '_export_timestamp']
    df = df[[c for c in cols if c in df.columns]]
    
    print(f"  Created {len(df)} goalie-season-gametype records with {len(df.columns)} columns")
    return df


def create_fact_goalie_career_stats_basic() -> pd.DataFrame:
    """
    Create basic goalie career stats from roster data.
    GOALIES ONLY.
    
    Grain: player_id + season_id + game_type (Regular/Playoffs/All)
    Uses GAME_TYPE_SPLITS from game_type_aggregator (single source of truth)
    """
    print("\nBuilding fact_goalie_career_stats_basic (GOALIES ONLY)...")
    
    # Use the season stats as base (already has season_id and game_type)
    season_stats = load_table('fact_goalie_season_stats_basic')
    
    all_stats = []
    
    if len(season_stats) > 0:
        # Aggregate from season stats, preserving season_id and game_type
        # Get unique player-season combinations
        player_seasons = season_stats[['player_id', 'season_id', 'player_name', 
                                       'team_name']].drop_duplicates(subset=['player_id', 'season_id'])
        
        for _, ps in player_seasons.iterrows():
            player_id = ps['player_id']
            season_id = ps['season_id']
            
            player_season_data = season_stats[
                (season_stats['player_id'] == player_id) & 
                (season_stats['season_id'] == season_id)
            ]
            
            # Split by game_type
            for game_type in GAME_TYPE_SPLITS:
                type_data = player_season_data[player_season_data['game_type'] == game_type]
                
                if len(type_data) == 0:
                    continue
                
                # Aggregate stats
                career_games = int(type_data['games_played'].sum())
                career_wins = int(type_data['wins'].sum())
                career_losses = int(type_data['losses'].sum())
                career_ties = int(type_data.get('ties', pd.Series([0] * len(type_data))).sum())
                career_goals_against = int(type_data['goals_against'].sum())
                career_shutouts = int(type_data['shutouts'].sum())
                
                # Calculate rates
                career_gaa = round(career_goals_against / career_games, 2) if career_games > 0 else 0.0
                career_win_pct = round(career_wins / career_games * 100, 1) if career_games > 0 else 0.0
                career_shutout_pct = round(career_shutouts / career_games * 100, 1) if career_games > 0 else 0.0
                
                stats = {
                    'goalie_career_basic_key': f"{player_id}_{season_id}_{game_type}",
                    'player_id': player_id,
                    'season_id': season_id,
                    'game_type': game_type,
                    'player_name': ps['player_name'],
                    'current_team': ps['team_name'],
                    'career_games': career_games,
                    'career_wins': career_wins,
                    'career_losses': career_losses,
                    'career_ties': career_ties,
                    'career_goals_against': career_goals_against,
                    'career_gaa': career_gaa,
                    'career_shutouts': career_shutouts,
                    'career_shutout_pct': career_shutout_pct,
                    'career_win_pct': career_win_pct,
                    '_export_timestamp': datetime.now().isoformat(),
                }
                all_stats.append(stats)
    else:
        # Fallback: build from roster directly
        roster = load_table('fact_gameroster')
        schedule = load_table('dim_schedule')
        goalies = roster[roster['player_position'].astype(str).str.lower().str.contains('goalie', na=False)]
        
        if len(goalies) == 0:
            return pd.DataFrame()
        
        # Add game_type
        goalies = add_game_type_to_df(goalies, schedule)
        
        # Get unique player-season combinations
        player_seasons = goalies[['player_id', 'season_id', 'player_full_name', 
                                  'team_name']].drop_duplicates(subset=['player_id', 'season_id'])
        
        for _, ps in player_seasons.iterrows():
            player_id = ps['player_id']
            season_id = ps['season_id']
            
            goalie_games = goalies[(goalies['player_id'] == player_id) & 
                                   (goalies['season_id'] == season_id)]
            
            # Split by game_type
            for game_type in GAME_TYPE_SPLITS:
                if game_type == 'All':
                    games = goalie_games
                else:
                    games = goalie_games[goalie_games['game_type'] == game_type]
                
                if len(games) == 0:
                    continue
                
                career_games = games['game_id'].nunique()
                career_goals_against = int(games['goals_against'].sum())
                career_shutouts = int(games['shutouts'].sum())
                
                # Get record using utility function
                # Ensure consistent game_id types before merge
                schedule_cols = schedule[['game_id', 'game_type', 'home_team_name', 'away_team_name',
                                         'home_total_goals', 'away_total_goals', 'home_team_t', 'away_team_t']].copy()
                schedule_cols['game_id'] = schedule_cols['game_id'].astype(str)
                games_copy = games.copy()
                games_copy['game_id'] = games_copy['game_id'].astype(str)
                games_with_schedule = games_copy.merge(schedule_cols, on='game_id', how='left')
                # Ensure goal columns are numeric
                for col in ['home_total_goals', 'away_total_goals', 'home_team_t', 'away_team_t']:
                    if col in games_with_schedule.columns:
                        games_with_schedule[col] = pd.to_numeric(games_with_schedule[col], errors='coerce').fillna(0).astype(int)
                record = get_goalie_record_from_games(games_with_schedule)
                
                # Calculate rates
                career_gaa = round(career_goals_against / career_games, 2) if career_games > 0 else 0.0
                career_win_pct = round(record['wins'] / career_games * 100, 1) if career_games > 0 else 0.0
                career_shutout_pct = round(career_shutouts / career_games * 100, 1) if career_games > 0 else 0.0
                
                stats = {
                    'goalie_career_basic_key': f"{player_id}_{season_id}_{game_type}",
                    'player_id': player_id,
                    'season_id': season_id,
                    'game_type': game_type,
                    'player_name': ps['player_full_name'],
                    'current_team': ps['team_name'],
                    'career_games': career_games,
                    'career_wins': record['wins'],
                    'career_losses': record['losses'],
                    'career_ties': record['ties'],
                    'career_goals_against': career_goals_against,
                    'career_gaa': career_gaa,
                    'career_shutouts': career_shutouts,
                    'career_shutout_pct': career_shutout_pct,
                    'career_win_pct': career_win_pct,
                    '_export_timestamp': datetime.now().isoformat(),
                }
                all_stats.append(stats)
    
    grouped = pd.DataFrame(all_stats)
    
    # Reorder columns
    priority_cols = ['goalie_career_basic_key', 'player_id', 'season_id', 'game_type',
                     'player_name', 'current_team', 'career_games',
                     'career_wins', 'career_losses', 'career_ties',
                     'career_goals_against', 'career_gaa', 'career_shutouts',
                     'career_shutout_pct', 'career_win_pct', '_export_timestamp']
    other_cols = [c for c in grouped.columns if c not in priority_cols]
    grouped = grouped[[c for c in priority_cols if c in grouped.columns] + other_cols]
    
    print(f"  Created {len(grouped)} goalie career records (by season+type) with {len(grouped.columns)} columns")
    return grouped


def create_fact_team_season_stats_basic() -> pd.DataFrame:
    """
    Create basic team season stats from schedule/roster.
    
    Grain: team_id + season_id + game_type
    Uses GAME_TYPE_SPLITS from game_type_aggregator (single source of truth)
    
    Record columns: games_played, wins, losses, ties, win_pct, points
    Points system: Win=2, Tie=1, Loss=0
    """
    print("\nBuilding fact_team_season_stats_basic...")
    
    schedule = load_table('dim_schedule')
    roster = load_table('fact_gameroster')
    
    if len(schedule) == 0:
        return pd.DataFrame()
    
    all_stats = []
    
    # Get unique team-season combinations from roster
    team_seasons = roster[['team_id', 'team_name', 'season_id', 'season']].drop_duplicates()
    
    for _, ts in team_seasons.iterrows():
        team_id = ts['team_id']
        season_id = ts['season_id']
        
        # Use GAME_TYPE_SPLITS from shared utility
        for game_type in GAME_TYPE_SPLITS:
            # Use shared utility for record calculation
            record = get_team_record_from_schedule(schedule, team_id, season_id, game_type)
            
            # Skip if no games for this game_type
            if record is None:
                continue
            
            stats = {
                'team_season_basic_key': f"{team_id}_{season_id}_{game_type}",
                'team_id': team_id,
                'team_name': ts['team_name'],
                'season_id': season_id,
                'season': ts['season'],
                'game_type': game_type,
                'games_played': record['games_played'],
                'wins': record['wins'],
                'losses': record['losses'],
                'ties': record['ties'],
                'points': record['points'],
                # Win percentage = points / (games_played * 2) * 100
                'win_pct': round(record['points'] / (record['games_played'] * 2) * 100, 1) if record['games_played'] > 0 else 0.0,
                'goals_for': record['goals_for'],
                'goals_against': record['goals_against'],
                'goal_diff': record['goals_for'] - record['goals_against'],
                'goals_for_per_game': round(record['goals_for'] / record['games_played'], 2),
                'goals_against_per_game': round(record['goals_against'] / record['games_played'], 2),
            }
            
            # Team scoring from roster - only available for 'All' game_type
            # (roster data is season-level, not split by game_type)
            if game_type == 'All':
                team_roster = roster[(roster['team_id'] == team_id) & (roster['season_id'] == season_id)]
                skaters = team_roster[~team_roster['player_position'].astype(str).str.lower().str.contains('goalie', na=False)]
                stats['team_goals'] = int(skaters['goals'].sum())
                stats['team_assists'] = int(skaters['assist'].sum())
                stats['team_pim'] = int(skaters['pim'].sum())
                stats['unique_players'] = skaters['player_id'].nunique()
            else:
                stats['team_goals'] = None
                stats['team_assists'] = None
                stats['team_pim'] = None
                stats['unique_players'] = None
            
            stats['_export_timestamp'] = datetime.now().isoformat()
            all_stats.append(stats)
    
    df = pd.DataFrame(all_stats)
    
    # Reorder columns logically
    col_order = [
        'team_season_basic_key', 'team_id', 'team_name', 'season_id', 'season', 'game_type',
        'games_played', 'wins', 'losses', 'ties', 'win_pct', 'points',
        'goals_for', 'goals_against', 'goal_diff', 'goals_for_per_game', 'goals_against_per_game',
        'team_goals', 'team_assists', 'team_pim', 'unique_players', '_export_timestamp'
    ]
    df = df[[c for c in col_order if c in df.columns]]
    
    print(f"  Created {len(df)} team-season-gametype records with {len(df.columns)} columns")
    return df


# =============================================================================
# ADVANCED TABLES (from tracking data)
# =============================================================================

def create_fact_goalie_season_stats() -> pd.DataFrame:
    """
    Create advanced goalie season stats from tracking data.
    Aggregates fact_goalie_game_stats.
    GOALIES ONLY.
    
    Grain: player_id + season_id + game_type
    Uses GAME_TYPE_SPLITS from game_type_aggregator (single source of truth)
    """
    print("\nBuilding fact_goalie_season_stats (ADVANCED from tracking)...")
    
    game_stats = load_table('fact_goalie_game_stats')
    roster = load_table('fact_gameroster')
    schedule = load_table('dim_schedule')
    
    if len(game_stats) == 0:
        print("  No goalie game stats found")
        return pd.DataFrame()
    
    # Add season_id from roster
    # Ensure consistent types before merge (dtype optimization may create mismatches)
    roster_subset = roster[['game_id', 'player_id', 'season_id', 'season']].drop_duplicates().copy()
    roster_subset['game_id'] = roster_subset['game_id'].astype(str)
    roster_subset['player_id'] = roster_subset['player_id'].astype(str)
    game_stats['game_id'] = game_stats['game_id'].astype(str)
    game_stats['player_id'] = game_stats['player_id'].astype(str)
    game_stats = game_stats.merge(roster_subset, on=['game_id', 'player_id'], how='left')
    
    # Add game_type using shared utility
    game_stats = add_game_type_to_df(game_stats, schedule)
    
    # Numeric columns to sum
    sum_cols = [
        'saves', 'goals_against', 'shots_against',
        'saves_butterfly', 'saves_pad', 'saves_glove', 'saves_blocker', 
        'saves_chest', 'saves_stick', 'saves_scramble',
        'hd_shots_against', 'hd_goals_against', 'hd_saves',
        'saves_freeze', 'saves_rebound',
        'rebounds_team_recovered', 'rebounds_opp_recovered', 
        'rebounds_shot_generated', 'rebounds_flurry_generated',
        'p1_saves', 'p1_goals_against', 'p2_saves', 'p2_goals_against',
        'p3_saves', 'p3_goals_against',
        'early_period_saves', 'mid_period_saves', 'late_period_saves', 'final_minute_saves',
        'early_period_ga', 'mid_period_ga', 'late_period_ga', 'final_minute_ga',
        'rush_saves', 'quick_attack_saves', 'set_play_saves',
        'rush_goals_against', 'quick_attack_ga', 'set_play_ga',
        'single_shot_saves', 'multi_shot_saves', 'sustained_pressure_saves',
        'glove_side_saves', 'blocker_side_saves', 'five_hole_saves',
        'rapid_fire_saves',
        'is_quality_start', 'is_bad_start',
    ]
    
    # Mean columns
    mean_cols = ['goalie_war', 'goalie_game_score', 'overall_game_rating', 
                 'clutch_rating', 'pressure_rating', 'rebound_rating']
    
    all_results = []
    
    # Get unique player-season combinations
    player_seasons = game_stats[['player_id', 'season_id']].drop_duplicates()
    
    for _, ps in player_seasons.iterrows():
        player_id = ps['player_id']
        season_id = ps['season_id']
        
        player_games = game_stats[(game_stats['player_id'] == player_id) & 
                                   (game_stats['season_id'] == season_id)]
        
        # Use GAME_TYPE_SPLITS from shared utility
        for game_type in GAME_TYPE_SPLITS:
            if game_type == 'All':
                games = player_games
            else:
                games = player_games[player_games['game_type'] == game_type]
            
            if len(games) == 0:
                continue
            
            # Build aggregation
            result = {
                'goalie_season_key': f"{player_id}_{season_id}_{game_type}",
                'player_id': player_id,
                'season_id': season_id,
                'season': games['season'].iloc[0] if 'season' in games.columns else None,
                'game_type': game_type,
                'player_name': games['player_name'].iloc[0] if 'player_name' in games.columns else None,
                'team_name': games['team_name'].iloc[0] if 'team_name' in games.columns else None,
                'team_id': games['team_id'].iloc[0] if 'team_id' in games.columns else None,
                'games_played': games['game_id'].nunique(),
            }
            
            # Sum columns
            for col in sum_cols:
                if col in games.columns:
                    result[col] = games[col].sum()
            
            # Mean columns
            for col in mean_cols:
                if col in games.columns:
                    result[col] = games[col].mean()
            
            all_results.append(result)
    
    grouped = pd.DataFrame(all_results)
    
    if len(grouped) == 0:
        return pd.DataFrame()
    
    # Calculate season rates
    if 'saves' in grouped.columns and 'shots_against' in grouped.columns:
        grouped['save_pct'] = round(grouped['saves'] / grouped['shots_against'] * 100, 2).fillna(0)
    if 'goals_against' in grouped.columns:
        grouped['gaa'] = round(grouped['goals_against'] / grouped['games_played'], 2)
    if 'hd_saves' in grouped.columns and 'hd_shots_against' in grouped.columns:
        grouped['hd_save_pct'] = round(grouped['hd_saves'] / grouped['hd_shots_against'] * 100, 2).fillna(0)
    
    # Per-game rates
    if 'saves' in grouped.columns:
        grouped['saves_per_game'] = round(grouped['saves'] / grouped['games_played'], 1)
    if 'shots_against' in grouped.columns:
        grouped['shots_against_per_game'] = round(grouped['shots_against'] / grouped['games_played'], 1)
    
    # Rebound control rate
    if all(c in grouped.columns for c in ['rebounds_team_recovered', 'rebounds_opp_recovered', 'rebounds_shot_generated', 'rebounds_flurry_generated']):
        total_rebounds = grouped['rebounds_team_recovered'] + grouped['rebounds_opp_recovered'] + grouped['rebounds_shot_generated'] + grouped['rebounds_flurry_generated']
        grouped['rebound_control_rate'] = round(grouped['rebounds_team_recovered'] / total_rebounds * 100, 1).fillna(100.0)
    
    # Rush vs set play SV%
    if 'rush_saves' in grouped.columns and 'rush_goals_against' in grouped.columns:
        rush_sa = grouped['rush_saves'] + grouped['rush_goals_against']
        grouped['rush_sv_pct'] = round(grouped['rush_saves'] / rush_sa * 100, 1).fillna(100.0)
    if 'set_play_saves' in grouped.columns and 'set_play_ga' in grouped.columns:
        set_sa = grouped['set_play_saves'] + grouped['set_play_ga']
        grouped['set_play_sv_pct'] = round(grouped['set_play_saves'] / set_sa * 100, 1).fillna(100.0)
    
    # Quality start %
    if 'is_quality_start' in grouped.columns:
        grouped['quality_start_pct'] = round(grouped['is_quality_start'] / grouped['games_played'] * 100, 1)
    
    # WAR totals
    if 'goalie_war' in grouped.columns:
        grouped['season_war'] = round(grouped['goalie_war'] * grouped['games_played'], 2)
    
    grouped['_export_timestamp'] = datetime.now().isoformat()
    
    print(f"  Created {len(grouped)} goalie-season-gametype records with {len(grouped.columns)} columns")
    return grouped


def create_fact_goalie_career_stats() -> pd.DataFrame:
    """
    Create advanced goalie career stats from tracking data.
    GOALIES ONLY.
    
    Grain: player_id + season_id + game_type (Regular/Playoffs/All)
    Uses GAME_TYPE_SPLITS from game_type_aggregator (single source of truth)
    """
    print("\nBuilding fact_goalie_career_stats (ADVANCED from tracking)...")
    
    season_stats = load_table('fact_goalie_season_stats')
    
    if len(season_stats) == 0:
        print("  No goalie season stats found")
        return pd.DataFrame()
    
    # Sum columns (exclude calculated rates and key columns)
    exclude_cols = ['goalie_season_key', 'player_id', 'season_id', 'season', 'game_type', 'player_name',
                    'team_name', 'team_id', '_export_timestamp', 'games_played',
                    'save_pct', 'gaa', 'hd_save_pct', 'saves_per_game', 'shots_against_per_game',
                    'rebound_control_rate', 'rush_sv_pct', 'set_play_sv_pct', 'quality_start_pct',
                    'season_war']
    
    sum_cols = [col for col in season_stats.columns if col not in exclude_cols]
    
    all_results = []
    
    # Get unique player-season combinations
    player_seasons = season_stats[['player_id', 'season_id', 'player_name', 'team_name']].drop_duplicates(
        subset=['player_id', 'season_id']
    )
    
    for _, ps in player_seasons.iterrows():
        player_id = ps['player_id']
        season_id = ps['season_id']
        
        player_season_data = season_stats[
            (season_stats['player_id'] == player_id) & 
            (season_stats['season_id'] == season_id)
        ]
        
        # Split by game_type
        for game_type in GAME_TYPE_SPLITS:
            type_data = player_season_data[player_season_data['game_type'] == game_type]
            
            if len(type_data) == 0:
                continue
            
            # Build aggregation dict
            agg_dict = {}
            for col in sum_cols:
                if col in type_data.columns:
                    agg_dict[col] = 'sum'
            
            agg_dict['games_played'] = 'sum'

            # Mean of ratings
            for col in ['goalie_war', 'goalie_game_score', 'overall_game_rating', 'clutch_rating',
                       'pressure_rating', 'rebound_rating']:
                if col in type_data.columns:
                    agg_dict[col] = 'mean'

            # Aggregate numeric columns
            grouped_type = type_data.agg(agg_dict).to_dict()

            # Get first/last values directly (pandas 2.0+ doesn't support 'first'/'last' as agg strings)
            grouped_type['player_name'] = type_data['player_name'].iloc[0] if len(type_data) > 0 else None
            grouped_type['team_name'] = type_data['team_name'].iloc[-1] if len(type_data) > 0 else None
            grouped_type['team_id'] = type_data['team_id'].iloc[-1] if len(type_data) > 0 else None
            
            career_games = int(grouped_type.get('games_played', 0))
            
            # Calculate career rates
            if career_games > 0:
                if 'saves' in grouped_type and 'shots_against' in grouped_type:
                    career_save_pct = round(grouped_type['saves'] / grouped_type['shots_against'] * 100, 2) if grouped_type['shots_against'] > 0 else 0.0
                else:
                    career_save_pct = 0.0
                
                if 'goals_against' in grouped_type:
                    career_gaa = round(grouped_type['goals_against'] / career_games, 2)
                else:
                    career_gaa = 0.0
            else:
                career_save_pct = 0.0
                career_gaa = 0.0
            
            result = {
                'goalie_career_key': f"{player_id}_{season_id}_{game_type}",
                'player_id': player_id,
                'season_id': season_id,
                'game_type': game_type,
                'player_name': grouped_type.get('player_name'),
                'team_name': grouped_type.get('team_name'),
                'team_id': grouped_type.get('team_id'),
                'career_games': career_games,
                'career_save_pct': career_save_pct,
                'career_gaa': career_gaa,
                '_export_timestamp': datetime.now().isoformat(),
            }
            
            # Add all summed columns
            for col in sum_cols:
                if col in grouped_type:
                    result[f'career_{col}'] = grouped_type[col]
            
            # Add mean columns with 'career_' prefix
            for col in ['goalie_war', 'goalie_game_score', 'overall_game_rating', 'clutch_rating',
                       'pressure_rating', 'rebound_rating']:
                if col in grouped_type:
                    result[f'career_{col}'] = round(grouped_type[col], 2) if pd.notna(grouped_type[col]) else 0.0
            
            all_results.append(result)
    
    df = pd.DataFrame(all_results)
    
    print(f"  Created {len(df)} goalie career records (by season+type) with {len(df.columns)} columns")
    return df


def create_fact_player_career_stats_enhanced() -> pd.DataFrame:
    """
    Create enhanced player career stats from tracking data.
    SKATERS ONLY.
    Expands from basic 16 cols to 50+ with advanced metrics.
    
    Grain: player_id + season_id + game_type (Regular/Playoffs/All)
    Uses GAME_TYPE_SPLITS from game_type_aggregator (single source of truth)
    """
    print("\nBuilding fact_player_career_stats (ENHANCED from tracking)...")
    
    season_stats = load_table('fact_player_season_stats')
    players = load_table('dim_player')
    roster = load_table('fact_gameroster')
    
    if len(season_stats) == 0:
        print("  No player season stats found")
        return pd.DataFrame()

    # Add team info if missing (from roster)
    if 'team_name' not in season_stats.columns or 'team_id' not in season_stats.columns:
        # Only add the columns we need
        merge_cols = ['player_id', 'season_id']
        add_cols = []
        if 'team_id' not in season_stats.columns:
            add_cols.append('team_id')
        if 'team_name' not in season_stats.columns:
            add_cols.append('team_name')

        if add_cols:
            roster_info = roster[merge_cols + add_cols].drop_duplicates(subset=['player_id', 'season_id'])
            # Ensure consistent types for merge
            roster_info['player_id'] = roster_info['player_id'].astype(str)
            roster_info['season_id'] = roster_info['season_id'].astype(str)
            season_stats['player_id'] = season_stats['player_id'].astype(str)
            season_stats['season_id'] = season_stats['season_id'].astype(str)
            season_stats = season_stats.merge(roster_info, on=['player_id', 'season_id'], how='left')

    # Key columns to aggregate
    sum_cols = [
        'goals', 'primary_assists', 'secondary_assists', 'assists', 'points',
        'shots', 'sog', 'shots_missed', 'shots_blocked',
        'pass_attempts', 'pass_completed',
        'takeaways', 'giveaways', 'hits', 'blocks',
        'zone_entries', 'zone_exits', 'carried_entries', 'dump_ins',
        'fo_wins', 'fo_losses',
        'offensive_zone_time', 'defensive_zone_time', 'neutral_zone_time',
        'scoring_chances', 'high_danger_chances',
        'pk_toi', 'pp_toi', 'ev_toi', 'toi',
    ]
    
    all_results = []

    # Pre-load tables once (avoid reloading inside nested loop)
    game_stats = load_table('fact_player_game_stats')
    if len(game_stats) > 0 and 'game_type' not in game_stats.columns:
        schedule = load_table('dim_schedule')
        game_stats = add_game_type_to_df(game_stats, schedule)
    if len(game_stats) > 0:
        if 'season_id' in game_stats.columns:
            game_stats['player_id'] = game_stats['player_id'].astype(str)
            game_stats['season_id'] = game_stats['season_id'].astype(str)

    # Get unique player-season combinations
    player_seasons = season_stats[['player_id', 'season_id', 'player_name']].drop_duplicates(
        subset=['player_id', 'season_id']
    )

    for _, ps in player_seasons.iterrows():
        player_id = ps['player_id']
        season_id = ps['season_id']
        
        player_season_data = season_stats[
            (season_stats['player_id'] == player_id) & 
            (season_stats['season_id'] == season_id)
        ]
        
        # Split by game_type
        for game_type in GAME_TYPE_SPLITS:
            type_data = player_season_data[player_season_data['game_type'] == game_type]
            
            if len(type_data) == 0:
                continue
            
            # Build aggregation
            agg_dict = {}
            for col in sum_cols:
                if col in type_data.columns:
                    agg_dict[col] = 'sum'

            # Mean of rates/indices
            rate_cols = ['war', 'gar', 'game_score', 'offensive_rating', 'defensive_rating']
            for col in rate_cols:
                if col in type_data.columns:
                    agg_dict[col] = 'mean'

            # Aggregate numeric columns
            grouped_type = type_data.agg(agg_dict).to_dict()

            # Get first/last values directly (pandas 2.0+ doesn't support 'first'/'last' as agg strings)
            grouped_type['player_name'] = type_data['player_name'].iloc[0] if len(type_data) > 0 else None
            grouped_type['team_name'] = type_data['team_name'].iloc[-1] if len(type_data) > 0 else None
            grouped_type['team_id'] = type_data['team_id'].iloc[-1] if len(type_data) > 0 else None
            
            # Get games played from pre-loaded game_stats
            if len(game_stats) > 0 and 'season_id' in game_stats.columns:
                player_game_stats = game_stats[
                    (game_stats['player_id'] == str(player_id)) &
                    (game_stats['season_id'] == str(season_id)) &
                    (game_stats['game_type'] == game_type)
                ]
                career_games = player_game_stats['game_id'].nunique()
            else:
                career_games = 0
            
            result = {
                'player_career_key': f"{player_id}_{season_id}_{game_type}",
                'player_id': player_id,
                'season_id': season_id,
                'game_type': game_type,
                'player_name': grouped_type.get('player_name'),
                'current_team': grouped_type.get('team_name'),
                'team_id': grouped_type.get('team_id'),
                'career_games': career_games,
                '_export_timestamp': datetime.now().isoformat(),
            }
            
            # Add all summed columns with 'career_' prefix
            for col in sum_cols:
                if col in grouped_type:
                    result[col] = grouped_type[col]
            
            # Add mean columns
            for col in rate_cols:
                if col in grouped_type:
                    result[col] = round(grouped_type[col], 2) if pd.notna(grouped_type[col]) else 0.0
            
            # Calculate career rates
            if career_games > 0:
                if 'goals' in result:
                    result['goals_per_game'] = round(result['goals'] / career_games, 2)
                if 'assists' in result:
                    result['assists_per_game'] = round(result['assists'] / career_games, 2)
                if 'points' in result:
                    result['points_per_game'] = round(result['points'] / career_games, 2)
            
            if 'sog' in result and result['sog'] > 0:
                result['shooting_pct'] = round(result.get('goals', 0) / result['sog'] * 100, 1)
            
            if 'pass_attempts' in result and result['pass_attempts'] > 0:
                result['pass_completion_pct'] = round(result.get('pass_completed', 0) / result['pass_attempts'] * 100, 1)
            
            if 'fo_wins' in result and 'fo_losses' in result:
                total_fo = result['fo_wins'] + result['fo_losses']
                if total_fo > 0:
                    result['faceoff_pct'] = round(result['fo_wins'] / total_fo * 100, 1)
            
            if 'takeaways' in result and 'giveaways' in result and result['giveaways'] > 0:
                result['takeaway_giveaway_ratio'] = round(result['takeaways'] / result['giveaways'], 2)
            
            all_results.append(result)
    
    df = pd.DataFrame(all_results)
    
    # Add position from roster
    if len(roster) > 0:
        latest_roster = roster.sort_values('game_id').groupby('player_id').last().reset_index()
        roster_info = latest_roster[['player_id', 'player_position']].copy()
        roster_info.columns = ['player_id', 'position']
        df = df.merge(roster_info, on='player_id', how='left')
    
    print(f"  Created {len(df)} player career records (by season+type) with {len(df.columns)} columns")
    return df


# =============================================================================
# MAIN BUILDER
# =============================================================================

def create_all_macro_stats():
    """Create all macro stats tables."""
    print("\n" + "=" * 70)
    print("CREATING MACRO STATS TABLES (v28.2)")
    print("=" * 70)
    
    results = {}
    
    # BASIC TABLES (from roster/schedule)
    print("\n--- BASIC TABLES (from roster/schedule) ---")
    
    df = create_fact_player_season_stats_basic()
    if len(df) > 0:
        results['fact_player_season_stats_basic'] = save_table(df, 'fact_player_season_stats_basic')
    
    df = create_fact_player_career_stats_basic()
    if len(df) > 0:
        results['fact_player_career_stats_basic'] = save_table(df, 'fact_player_career_stats_basic')
    
    df = create_fact_goalie_season_stats_basic()
    if len(df) > 0:
        results['fact_goalie_season_stats_basic'] = save_table(df, 'fact_goalie_season_stats_basic')
    
    df = create_fact_goalie_career_stats_basic()
    if len(df) > 0:
        results['fact_goalie_career_stats_basic'] = save_table(df, 'fact_goalie_career_stats_basic')
    
    df = create_fact_team_season_stats_basic()
    if len(df) > 0:
        results['fact_team_season_stats_basic'] = save_table(df, 'fact_team_season_stats_basic')
    
    # ADVANCED TABLES (from tracking)
    print("\n--- ADVANCED TABLES (from tracking) ---")
    
    df = create_fact_goalie_season_stats()
    if len(df) > 0:
        results['fact_goalie_season_stats'] = save_table(df, 'fact_goalie_season_stats')
    
    df = create_fact_goalie_career_stats()
    if len(df) > 0:
        results['fact_goalie_career_stats'] = save_table(df, 'fact_goalie_career_stats')
    
    df = create_fact_player_career_stats_enhanced()
    if len(df) > 0:
        results['fact_player_career_stats'] = save_table(df, 'fact_player_career_stats')
    
    print(f"\n✅ Created {len(results)} macro stats tables")
    return results


if __name__ == "__main__":
    create_all_macro_stats()
