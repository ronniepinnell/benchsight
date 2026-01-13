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
    player_seasons = skaters[['player_id', 'season_id', 'player_full_name', 'team_id', 
                               'team_name', 'player_position', 'season']].drop_duplicates(
                                   subset=['player_id', 'season_id'])
    
    for _, ps in player_seasons.iterrows():
        player_id = ps['player_id']
        season_id = ps['season_id']
        
        player_games = skaters[(skaters['player_id'] == player_id) & 
                               (skaters['season_id'] == season_id)]
        
        # Use GAME_TYPE_SPLITS from shared utility
        for game_type in GAME_TYPE_SPLITS:
            if game_type == 'All':
                games = player_games
            else:
                games = player_games[player_games['game_type'] == game_type]
            
            if len(games) == 0:
                continue
            
            gp = games['game_id'].nunique()
            goals = int(games['goals'].sum())
            assists = int(games['assist'].sum())
            points = int(games['points'].sum())
            pim = int(games['pim'].sum())
            
            stats = {
                'player_season_basic_key': f"{player_id}_{season_id}_{game_type}",
                'player_id': player_id,
                'season_id': season_id,
                'season': ps['season'],
                'game_type': game_type,
                'player_name': ps['player_full_name'],
                'team_id': ps['team_id'],
                'team_name': ps['team_name'],
                'position': ps['player_position'],
                'games_played': gp,
                'goals': goals,
                'assists': assists,
                'points': points,
                'pim': pim,
                'goals_per_game': round(goals / gp, 2),
                'assists_per_game': round(assists / gp, 2),
                'points_per_game': round(points / gp, 2),
                'pim_per_game': round(pim / gp, 2),
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
    """
    print("\nBuilding fact_player_career_stats_basic (SKATERS ONLY)...")
    
    roster = load_table('fact_gameroster')
    
    if len(roster) == 0:
        return pd.DataFrame()
    
    # Filter to skaters
    skaters = roster[~roster['player_position'].astype(str).str.lower().str.contains('goalie', na=False)]
    
    # Group by player (all seasons)
    grouped = skaters.groupby('player_id').agg({
        'game_id': 'nunique',
        'season_id': 'nunique',
        'goals': 'sum',
        'assist': 'sum',
        'points': 'sum',
        'pim': 'sum',
        'player_full_name': 'first',
        'player_position': 'first',
        'team_name': 'last',  # Most recent team
    }).reset_index()
    
    grouped.columns = ['player_id', 'career_games', 'seasons_played', 'career_goals', 
                       'career_assists', 'career_points', 'career_pim',
                       'player_name', 'position', 'current_team']
    
    # Per-game rates
    grouped['goals_per_game'] = round(grouped['career_goals'] / grouped['career_games'], 2)
    grouped['assists_per_game'] = round(grouped['career_assists'] / grouped['career_games'], 2)
    grouped['points_per_game'] = round(grouped['career_points'] / grouped['career_games'], 2)
    grouped['pim_per_game'] = round(grouped['career_pim'] / grouped['career_games'], 2)
    
    grouped['player_career_basic_key'] = grouped['player_id'] + '_career'
    grouped['_export_timestamp'] = datetime.now().isoformat()
    
    cols = ['player_career_basic_key', 'player_id', 'player_name', 'position', 'current_team',
            'seasons_played', 'career_games', 'career_goals', 'career_assists', 'career_points', 'career_pim',
            'goals_per_game', 'assists_per_game', 'points_per_game', 'pim_per_game',
            '_export_timestamp']
    grouped = grouped[[c for c in cols if c in grouped.columns]]
    
    print(f"  Created {len(grouped)} player career records with {len(grouped.columns)} columns")
    return grouped


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
    goalies = goalies.merge(
        schedule[['game_id', 'game_type', 'home_team_name', 'away_team_name', 
                  'home_total_goals', 'away_total_goals', 'home_team_t', 'away_team_t']],
        on='game_id',
        how='left'
    )
    goalies['game_type'] = goalies['game_type'].fillna('Regular')
    
    all_stats = []
    
    # Get unique goalie-season combinations
    goalie_seasons = goalies[['player_id', 'season_id', 'player_full_name', 'team_id', 
                               'team_name', 'season']].drop_duplicates(subset=['player_id', 'season_id'])
    
    for _, gs in goalie_seasons.iterrows():
        player_id = gs['player_id']
        season_id = gs['season_id']
        
        goalie_games = goalies[(goalies['player_id'] == player_id) & 
                                (goalies['season_id'] == season_id)]
        
        # Use GAME_TYPE_SPLITS from shared utility
        for game_type in GAME_TYPE_SPLITS:
            if game_type == 'All':
                games = goalie_games
            else:
                games = goalie_games[goalie_games['game_type'] == game_type]
            
            if len(games) == 0:
                continue
            
            # Use shared utility for W-L-T calculation
            record = get_goalie_record_from_games(games)
            
            gp = games['game_id'].nunique()
            ga = int(games['goals_against'].sum())
            so = int(games['shutouts'].sum())
            
            stats = {
                'goalie_season_basic_key': f"{player_id}_{season_id}_{game_type}",
                'player_id': player_id,
                'season_id': season_id,
                'season': gs['season'],
                'game_type': game_type,
                'player_name': gs['player_full_name'],
                'team_id': gs['team_id'],
                'team_name': gs['team_name'],
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
    """
    print("\nBuilding fact_goalie_career_stats_basic (GOALIES ONLY)...")
    
    # Use the season stats as base
    season_stats = load_table('fact_goalie_season_stats_basic')
    
    if len(season_stats) == 0:
        # Try to build from roster directly
        roster = load_table('fact_gameroster')
        goalies = roster[roster['player_position'].astype(str).str.lower().str.contains('goalie', na=False)]
        
        if len(goalies) == 0:
            return pd.DataFrame()
        
        grouped = goalies.groupby('player_id').agg({
            'game_id': 'nunique',
            'season_id': 'nunique',
            'goals_against': 'sum',
            'shutouts': 'sum',
            'player_full_name': 'first',
            'team_name': 'last',
        }).reset_index()
        
        grouped.columns = ['player_id', 'career_games', 'seasons_played', 'career_goals_against',
                           'career_shutouts', 'player_name', 'current_team']
    else:
        # Aggregate from season stats
        grouped = season_stats.groupby('player_id').agg({
            'games_played': 'sum',
            'season_id': 'nunique',
            'wins': 'sum',
            'losses': 'sum',
            'goals_against': 'sum',
            'shutouts': 'sum',
            'player_name': 'first',
            'team_name': 'last',
        }).reset_index()
        
        grouped.columns = ['player_id', 'career_games', 'seasons_played', 'career_wins',
                           'career_losses', 'career_goals_against', 'career_shutouts',
                           'player_name', 'current_team']
    
    # Calculate career rates
    grouped['career_gaa'] = round(grouped['career_goals_against'] / grouped['career_games'], 2)
    grouped['career_win_pct'] = round(grouped.get('career_wins', 0) / grouped['career_games'] * 100, 1) if 'career_wins' in grouped.columns else 0.0
    grouped['career_shutout_pct'] = round(grouped['career_shutouts'] / grouped['career_games'] * 100, 1)
    
    grouped['goalie_career_basic_key'] = grouped['player_id'] + '_career'
    grouped['_export_timestamp'] = datetime.now().isoformat()
    
    print(f"  Created {len(grouped)} goalie career records with {len(grouped.columns)} columns")
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
    game_stats = game_stats.merge(
        roster[['game_id', 'player_id', 'season_id', 'season']].drop_duplicates(),
        on=['game_id', 'player_id'],
        how='left'
    )
    
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
    """
    print("\nBuilding fact_goalie_career_stats (ADVANCED from tracking)...")
    
    season_stats = load_table('fact_goalie_season_stats')
    
    if len(season_stats) == 0:
        print("  No goalie season stats found")
        return pd.DataFrame()
    
    # Sum columns
    sum_cols = [col for col in season_stats.columns if col not in 
                ['goalie_season_key', 'player_id', 'season_id', 'season', 'player_name',
                 'team_name', 'team_id', '_export_timestamp', 'games_played',
                 'save_pct', 'gaa', 'hd_save_pct', 'saves_per_game', 'shots_against_per_game',
                 'rebound_control_rate', 'rush_sv_pct', 'set_play_sv_pct', 'quality_start_pct',
                 'goalie_war', 'goalie_game_score', 'overall_game_rating', 'clutch_rating',
                 'pressure_rating', 'rebound_rating']]
    
    agg_dict = {col: 'sum' for col in sum_cols if col in season_stats.columns}
    agg_dict['games_played'] = 'sum'
    agg_dict['season_id'] = 'nunique'
    agg_dict['player_name'] = 'first'
    agg_dict['team_name'] = 'last'
    
    # Mean of ratings
    for col in ['goalie_war', 'goalie_game_score', 'overall_game_rating', 'clutch_rating']:
        if col in season_stats.columns:
            agg_dict[col] = 'mean'
    
    grouped = season_stats.groupby('player_id').agg(agg_dict).reset_index()
    grouped.rename(columns={'season_id': 'seasons_played', 'games_played': 'career_games'}, inplace=True)
    
    # Calculate career rates
    grouped['career_save_pct'] = round(grouped['saves'] / grouped['shots_against'] * 100, 2)
    grouped['career_gaa'] = round(grouped['goals_against'] / grouped['career_games'], 2)
    
    grouped['goalie_career_key'] = grouped['player_id'] + '_career'
    grouped['_export_timestamp'] = datetime.now().isoformat()
    
    print(f"  Created {len(grouped)} goalie career records with {len(grouped.columns)} columns")
    return grouped


def create_fact_player_career_stats_enhanced() -> pd.DataFrame:
    """
    Create enhanced player career stats from tracking data.
    SKATERS ONLY.
    Expands from basic 16 cols to 50+ with advanced metrics.
    """
    print("\nBuilding fact_player_career_stats (ENHANCED from tracking)...")
    
    season_stats = load_table('fact_player_season_stats')
    players = load_table('dim_player')
    roster = load_table('fact_gameroster')
    
    if len(season_stats) == 0:
        print("  No player season stats found")
        return pd.DataFrame()
    
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
    
    agg_dict = {}
    for col in sum_cols:
        if col in season_stats.columns:
            agg_dict[col] = 'sum'
    
    agg_dict['season_id'] = 'nunique'
    
    # Mean of rates/indices
    rate_cols = ['war', 'gar', 'game_score', 'offensive_rating', 'defensive_rating']
    for col in rate_cols:
        if col in season_stats.columns:
            agg_dict[col] = 'mean'
    
    grouped = season_stats.groupby('player_id').agg(agg_dict).reset_index()
    grouped.rename(columns={'season_id': 'seasons_played'}, inplace=True)
    
    # Add games played from game_stats
    game_stats = load_table('fact_player_game_stats')
    if len(game_stats) > 0:
        games_by_player = game_stats.groupby('player_id')['game_id'].nunique().reset_index()
        games_by_player.columns = ['player_id', 'career_games']
        grouped = grouped.merge(games_by_player, on='player_id', how='left')
        grouped['career_games'] = grouped['career_games'].fillna(0).astype(int)
    else:
        grouped['career_games'] = grouped['seasons_played']
    
    # Add player info from dim_player
    if len(players) > 0:
        player_info = players[['player_id', 'player_full_name']].drop_duplicates()
        grouped = grouped.merge(player_info, on='player_id', how='left')
        grouped.rename(columns={'player_full_name': 'player_name'}, inplace=True)
    
    # Add position and team from roster
    if len(roster) > 0:
        latest_roster = roster.sort_values('game_id').groupby('player_id').last().reset_index()
        roster_info = latest_roster[['player_id', 'player_position', 'team_name']].copy()
        roster_info.columns = ['player_id', 'position', 'current_team']
        grouped = grouped.merge(roster_info, on='player_id', how='left')
    
    # Calculate career rates
    if 'goals' in grouped.columns and 'career_games' in grouped.columns:
        grouped['goals_per_game'] = round(grouped['goals'] / grouped['career_games'].replace(0, 1), 2)
        grouped['assists_per_game'] = round(grouped['assists'] / grouped['career_games'].replace(0, 1), 2) if 'assists' in grouped.columns else 0.0
        grouped['points_per_game'] = round(grouped['points'] / grouped['career_games'].replace(0, 1), 2) if 'points' in grouped.columns else 0.0
    
    if 'sog' in grouped.columns:
        grouped['shooting_pct'] = round(grouped['goals'] / grouped['sog'].replace(0, 1) * 100, 1)
    
    if 'pass_attempts' in grouped.columns:
        grouped['pass_completion_pct'] = round(grouped['pass_completed'] / grouped['pass_attempts'].replace(0, 1) * 100, 1)
    
    if 'fo_wins' in grouped.columns and 'fo_losses' in grouped.columns:
        total_fo = grouped['fo_wins'] + grouped['fo_losses']
        grouped['faceoff_pct'] = round(grouped['fo_wins'] / total_fo.replace(0, 1) * 100, 1)
    
    if 'takeaways' in grouped.columns and 'giveaways' in grouped.columns:
        grouped['takeaway_giveaway_ratio'] = round(grouped['takeaways'] / grouped['giveaways'].replace(0, 1), 2)
    
    grouped['player_career_key'] = grouped['player_id'] + '_career'
    grouped['_export_timestamp'] = datetime.now().isoformat()
    
    print(f"  Created {len(grouped)} player career records with {len(grouped.columns)} columns")
    return grouped


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
