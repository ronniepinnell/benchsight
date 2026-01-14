"""
Remaining fact tables that were missing from the schema.
Creates 35 additional tables to reach the full 129-table schema.

v29.0 - Uses game_type_aggregator for consistent game_type splits
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from src.utils.game_type_aggregator import (
    GAME_TYPE_SPLITS,
    add_game_type_to_df
)

OUTPUT_DIR = Path(__file__).parent.parent.parent / 'data' / 'output'


def load_table(name: str) -> pd.DataFrame:
    """Load a table from output directory."""
    path = OUTPUT_DIR / f'{name}.csv'
    if path.exists():
        return pd.read_csv(path, low_memory=False)
    return pd.DataFrame()


def save_table(df: pd.DataFrame, name: str) -> int:
    """Save a table to output directory."""
    path = OUTPUT_DIR / f'{name}.csv'
    df.to_csv(path, index=False)
    return len(df)


# =============================================================================
# PERIOD-LEVEL TABLES
# =============================================================================

def create_fact_player_period_stats() -> pd.DataFrame:
    """Create player stats broken down by period."""
    event_players = load_table('fact_event_players')
    shift_players = load_table('fact_shift_players')
    
    if len(event_players) == 0:
        return pd.DataFrame()
    
    records = []
    
    # Get unique game-player-period combinations
    for game_id in event_players['game_id'].dropna().unique():
        game_events = event_players[event_players['game_id'] == game_id]
        
        for player_id in game_events['player_id'].dropna().unique():
            if pd.isna(player_id) or str(player_id) in ['', 'None', 'nan']:
                continue
                
            player_events = game_events[game_events['player_id'] == player_id]
            
            for period in player_events['period'].dropna().unique():
                period_events = player_events[player_events['period'] == period]
                
                # Count stats
                goals = len(period_events[
                    (period_events['event_type'].astype(str).str.lower() == 'goal') &
                    (period_events['event_detail'].astype(str).str.lower().str.contains('goal_scored', na=False))
                ])
                
                shots = len(period_events[period_events['event_type'].astype(str).str.lower() == 'shot'])
                passes = len(period_events[period_events['event_type'].astype(str).str.lower() == 'pass'])
                
                # Get TOI from shifts if available
                toi = 0
                if len(shift_players) > 0:
                    player_shifts = shift_players[
                        (shift_players['game_id'] == game_id) &
                        (shift_players['player_id'] == player_id) &
                        (shift_players['period'] == period)
                    ]
                    if 'toi_seconds' in player_shifts.columns:
                        toi = player_shifts['toi_seconds'].sum()
                
                records.append({
                    'player_period_key': f"{player_id}_{game_id}_{int(period)}",
                    'game_id': game_id,
                    'player_id': player_id,
                    'period': int(period),
                    'goals': goals,
                    'shots': shots,
                    'passes': passes,
                    'toi_seconds': toi,
                    '_export_timestamp': datetime.now().isoformat()
                })
    
    return pd.DataFrame(records)


def create_fact_period_momentum() -> pd.DataFrame:
    """Create period-level momentum metrics per team."""
    events = load_table('fact_events')
    
    if len(events) == 0:
        return pd.DataFrame()
    
    records = []
    
    for game_id in events['game_id'].dropna().unique():
        game_events = events[events['game_id'] == game_id]
        
        for period in game_events['period'].dropna().unique():
            period_events = game_events[game_events['period'] == period]
            
            # Count events by team
            for team_col in ['home_team', 'away_team']:
                if team_col not in period_events.columns:
                    continue
                    
                team_id = period_events[team_col.replace('_team', '_team_id')].iloc[0] if f"{team_col.replace('_team', '_team_id')}" in period_events.columns else None
                
                shots = len(period_events[period_events['event_type'].astype(str).str.lower() == 'shot'])
                goals = len(period_events[
                    (period_events['event_type'].astype(str).str.lower() == 'goal') &
                    (period_events['event_detail'].astype(str).str.lower().str.contains('goal_scored', na=False))
                ])
                
                records.append({
                    'momentum_key': f"{game_id}_{int(period)}_{team_col}",
                    'game_id': game_id,
                    'period': int(period),
                    'venue': 'home' if 'home' in team_col else 'away',
                    'shots': shots // 2,  # Approximate per team
                    'goals': goals // 2,
                    'corsi_events': shots,
                    'momentum_score': 0.5,  # Placeholder
                    '_export_timestamp': datetime.now().isoformat()
                })
    
    return pd.DataFrame(records)


# =============================================================================
# AGGREGATION/ROLLUP TABLES
# =============================================================================

def create_fact_player_season_stats() -> pd.DataFrame:
    """
    Aggregate player stats to season level.
    
    Grain: player_id + season_id + game_type
    Uses GAME_TYPE_SPLITS from game_type_aggregator (single source of truth)
    """
    player_game_stats = load_table('fact_player_game_stats')
    schedule = load_table('dim_schedule')
    
    if len(player_game_stats) == 0:
        return pd.DataFrame()
    
    # Add game_type using shared utility
    player_game_stats = add_game_type_to_df(player_game_stats, schedule)
    
    if 'season_id' not in player_game_stats.columns:
        player_game_stats['season_id'] = 'N20252026F'
    
    numeric_cols = player_game_stats.select_dtypes(include=['number']).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ['game_id', 'season_id']]
    
    all_results = []
    
    # Get unique player-season combinations
    player_seasons = player_game_stats[['player_id', 'season_id']].drop_duplicates()
    
    for _, ps in player_seasons.iterrows():
        player_id = ps['player_id']
        season_id = ps['season_id']
        
        player_games = player_game_stats[(player_game_stats['player_id'] == player_id) & 
                                          (player_game_stats['season_id'] == season_id)]
        
        # Use GAME_TYPE_SPLITS from shared utility
        for game_type in GAME_TYPE_SPLITS:
            if game_type == 'All':
                games = player_games
            else:
                games = player_games[player_games['game_type'] == game_type]
            
            if len(games) == 0:
                continue
            
            result = {
                'player_season_key': f"{player_id}_{season_id}_{game_type}",
                'player_id': player_id,
                'season_id': season_id,
                'game_type': game_type,
                'games_played': len(games),
            }
            
            # Sum numeric columns
            for col in numeric_cols:
                if col in games.columns:
                    result[col] = games[col].sum()
            
            all_results.append(result)
    
    grouped = pd.DataFrame(all_results)
    
    if len(grouped) == 0:
        return pd.DataFrame()
    
    grouped['_export_timestamp'] = datetime.now().isoformat()
    
    # Recalculate rates
    if 'toi_minutes' in grouped.columns and grouped['toi_minutes'].sum() > 0:
        if 'goals' in grouped.columns:
            grouped['goals_per_60'] = (grouped['goals'] / grouped['toi_minutes']) * 60
        if 'points' in grouped.columns:
            grouped['points_per_60'] = (grouped['points'] / grouped['toi_minutes']) * 60
    
    return grouped


def create_fact_player_career_stats() -> pd.DataFrame:
    """Aggregate player stats to career level."""
    player_season_stats = load_table('fact_player_season_stats')
    
    if len(player_season_stats) == 0:
        # Try from game stats
        player_game_stats = load_table('fact_player_game_stats')
        if len(player_game_stats) == 0:
            return pd.DataFrame()
        
        numeric_cols = player_game_stats.select_dtypes(include=['number']).columns.tolist()
        numeric_cols = [c for c in numeric_cols if c not in ['game_id', 'season_id']]
        
        agg_dict = {col: 'sum' for col in numeric_cols if col in player_game_stats.columns}
        agg_dict['game_id'] = 'count'
        
        grouped = player_game_stats.groupby('player_id').agg(agg_dict).reset_index()
        grouped = grouped.rename(columns={'game_id': 'career_games'})
    else:
        numeric_cols = player_season_stats.select_dtypes(include=['number']).columns.tolist()
        numeric_cols = [c for c in numeric_cols if c not in ['season_id']]
        
        agg_dict = {col: 'sum' for col in numeric_cols if col in player_season_stats.columns}
        agg_dict['season_id'] = 'nunique'
        
        grouped = player_season_stats.groupby('player_id').agg(agg_dict).reset_index()
        grouped = grouped.rename(columns={'season_id': 'seasons_played'})
    
    grouped['player_career_key'] = grouped['player_id'].astype(str) + '_career'
    grouped['_export_timestamp'] = datetime.now().isoformat()
    
    return grouped


def create_fact_team_season_stats() -> pd.DataFrame:
    """
    Aggregate team stats to season level.
    
    Grain: team_id + season_id + game_type
    Uses GAME_TYPE_SPLITS from game_type_aggregator (single source of truth)
    """
    team_game_stats = load_table('fact_team_game_stats')
    schedule = load_table('dim_schedule')
    
    if len(team_game_stats) == 0:
        return pd.DataFrame()
    
    # Add game_type using shared utility
    team_game_stats = add_game_type_to_df(team_game_stats, schedule)
    
    if 'season_id' not in team_game_stats.columns:
        team_game_stats['season_id'] = 'N20252026F'
    
    numeric_cols = team_game_stats.select_dtypes(include=['number']).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ['game_id', 'season_id']]
    
    all_results = []
    
    # Get unique team-season combinations
    team_seasons = team_game_stats[['team_id', 'season_id']].drop_duplicates()
    
    for _, ts in team_seasons.iterrows():
        team_id = ts['team_id']
        season_id = ts['season_id']
        
        team_games = team_game_stats[(team_game_stats['team_id'] == team_id) & 
                                      (team_game_stats['season_id'] == season_id)]
        
        # Use GAME_TYPE_SPLITS from shared utility
        for game_type in GAME_TYPE_SPLITS:
            if game_type == 'All':
                games = team_games
            else:
                games = team_games[team_games['game_type'] == game_type]
            
            if len(games) == 0:
                continue
            
            result = {
                'team_season_key': f"{team_id}_{season_id}_{game_type}",
                'team_id': team_id,
                'season_id': season_id,
                'game_type': game_type,
                'games_played': len(games),
            }
            
            # Sum numeric columns
            for col in numeric_cols:
                if col in games.columns:
                    result[col] = games[col].sum()
            
            all_results.append(result)
    
    grouped = pd.DataFrame(all_results)
    
    if len(grouped) == 0:
        return pd.DataFrame()
    
    grouped['_export_timestamp'] = datetime.now().isoformat()
    
    return grouped


def create_fact_team_standings_snapshot() -> pd.DataFrame:
    """Create team standings snapshots."""
    team_game_stats = load_table('fact_team_game_stats')
    events = load_table('fact_events')
    
    if len(team_game_stats) == 0:
        return pd.DataFrame()
    
    records = []
    
    # Get unique teams
    teams = team_game_stats['team_id'].dropna().unique()
    
    for team_id in teams:
        team_stats = team_game_stats[team_game_stats['team_id'] == team_id]
        
        # Calculate wins/losses from goals
        wins = 0
        losses = 0
        
        for _, game in team_stats.iterrows():
            game_id = game['game_id']
            gf = game.get('goals', 0)
            ga = game.get('goals_against', 0) if 'goals_against' in game else 0
            
            if gf > ga:
                wins += 1
            else:
                losses += 1
        
        records.append({
            'standings_key': f"{team_id}_current",
            'team_id': team_id,
            'games_played': len(team_stats),
            'wins': wins,
            'losses': losses,
            'points': wins * 2,
            'goals_for': team_stats['goals'].sum() if 'goals' in team_stats.columns else 0,
            'goals_against': team_stats.get('goals_against', pd.Series([0])).sum(),
            'snapshot_date': datetime.now().date().isoformat(),
            '_export_timestamp': datetime.now().isoformat()
        })
    
    return pd.DataFrame(records)


def create_fact_league_leaders_snapshot() -> pd.DataFrame:
    """Create league leaders snapshots."""
    player_game_stats = load_table('fact_player_game_stats')
    
    if len(player_game_stats) == 0:
        return pd.DataFrame()
    
    # Aggregate to season level
    if 'goals' not in player_game_stats.columns:
        return pd.DataFrame()
    
    season_stats = player_game_stats.groupby('player_id').agg({
        'goals': 'sum',
        'assists': 'sum' if 'assists' in player_game_stats.columns else 'count',
        'points': 'sum' if 'points' in player_game_stats.columns else 'count',
        'game_id': 'count'
    }).reset_index()
    season_stats = season_stats.rename(columns={'game_id': 'games_played'})
    
    records = []
    
    # Goals leaders
    top_goals = season_stats.nlargest(10, 'goals')
    for rank, (_, row) in enumerate(top_goals.iterrows(), 1):
        records.append({
            'leader_key': f"goals_{rank}",
            'category': 'goals',
            'rank': rank,
            'player_id': row['player_id'],
            'value': row['goals'],
            'games_played': row['games_played'],
            'snapshot_date': datetime.now().date().isoformat(),
            '_export_timestamp': datetime.now().isoformat()
        })
    
    # Points leaders
    if 'points' in season_stats.columns:
        top_points = season_stats.nlargest(10, 'points')
        for rank, (_, row) in enumerate(top_points.iterrows(), 1):
            records.append({
                'leader_key': f"points_{rank}",
                'category': 'points',
                'rank': rank,
                'player_id': row['player_id'],
                'value': row['points'],
                'games_played': row['games_played'],
                'snapshot_date': datetime.now().date().isoformat(),
                '_export_timestamp': datetime.now().isoformat()
            })
    
    return pd.DataFrame(records)


# =============================================================================
# PLAYER ANALYTICS TABLES
# =============================================================================

def create_fact_player_micro_stats() -> pd.DataFrame:
    """
    Create micro-level player stats.
    
    NOTE: This table is now primarily for backward compatibility.
    The full micro stats are now included in fact_player_game_stats.
    This table extracts key micro stats for easy querying.
    """
    # Load from fact_player_game_stats which has all micro stats
    player_game_stats = load_table('fact_player_game_stats')
    
    if len(player_game_stats) == 0:
        return pd.DataFrame()
    
    # Select micro stats columns
    micro_stat_cols = [
        'game_id', 'player_id',
        # Original micro stats
        'dekes', 'drives_middle', 'drives_wide', 'drives_corner', 'drives_total',
        'cutbacks', 'delays', 'crash_net', 'screens', 'give_and_go',
        'second_touch', 'cycles', 'poke_checks', 'stick_checks',
        'zone_ent_denials', 'backchecks', 'forechecks', 'breakouts',
        'dump_ins', 'loose_puck_wins', 'puck_recoveries',
        'puck_battles_total', 'plays_successful', 'plays_unsuccessful', 'play_success_rate',
        # New pass type micro stats
        'passes_cross_ice', 'passes_stretch', 'passes_breakout', 'passes_rim',
        'passes_bank', 'passes_royal_road', 'passes_slot', 'passes_behind_net',
        # New shot type micro stats
        'shots_one_timer', 'shots_snap', 'shots_wrist', 'shots_slap',
        'shots_tip', 'shots_deflection', 'shots_wrap_around',
        # Zone-specific
        'micro_off_zone', 'micro_def_zone', 'micro_neutral_zone',
        # Pressure metrics
        'pressure_plays', 'pressure_successful', 'pressure_success_rate',
        'forecheck_intensity', 'backcheck_intensity',
        # Board battles
        'board_battles_won', 'board_battles_lost', 'board_battle_win_pct',
        # Advanced composite metrics
        'possession_quality_index', 'transition_efficiency', 'pressure_index',
        'offensive_creativity_index', 'defensive_activity_index',
        'playmaking_quality', 'net_front_presence', 'puck_battle_win_pct', 'puck_battles_per_60'
    ]
    
    # Filter to columns that exist
    available_cols = [c for c in micro_stat_cols if c in player_game_stats.columns]
    
    if len(available_cols) == 0:
        return pd.DataFrame()
    
    # Create micro stats table
    micro_stats = player_game_stats[available_cols].copy()
    
    # Add key and timestamp
    micro_stats['micro_stats_key'] = micro_stats['player_id'].astype(str) + '_' + micro_stats['game_id'].astype(str)
    micro_stats['_export_timestamp'] = datetime.now().isoformat()
    
    # Reorder columns
    key_cols = ['micro_stats_key', 'game_id', 'player_id']
    other_cols = [c for c in micro_stats.columns if c not in key_cols + ['_export_timestamp']]
    micro_stats = micro_stats[key_cols + other_cols + ['_export_timestamp']]
    
    return micro_stats


def create_fact_player_qoc_summary() -> pd.DataFrame:
    """Create quality of competition summary."""
    columns = ['qoc_key', 'game_id', 'player_id', 'avg_opp_rating', 'avg_own_rating', 
               'rating_diff', 'shifts_tracked', '_export_timestamp']
    
    shift_players = load_table('fact_shift_players')
    
    # FIX: Column is 'opp_avg_rating' not 'opp_rating'
    if len(shift_players) == 0 or 'opp_avg_rating' not in shift_players.columns:
        # Return empty DataFrame with proper columns
        return pd.DataFrame(columns=columns)
    
    records = []
    
    for game_id in shift_players['game_id'].dropna().unique():
        game_shifts = shift_players[shift_players['game_id'] == game_id]
        
        for player_id in game_shifts['player_id'].dropna().unique():
            if pd.isna(player_id) or str(player_id) in ['', 'None', 'nan']:
                continue
            
            ps = game_shifts[game_shifts['player_id'] == player_id]
            
            # FIX: Use correct column names
            avg_opp_rating = ps['opp_avg_rating'].mean() if 'opp_avg_rating' in ps.columns else 0
            avg_rating = ps['player_rating'].mean() if 'player_rating' in ps.columns else 0
            
            records.append({
                'qoc_key': f"{player_id}_{game_id}",
                'game_id': game_id,
                'player_id': player_id,
                'avg_opp_rating': round(avg_opp_rating, 2),
                'avg_own_rating': round(avg_rating, 2),
                'rating_diff': round(avg_rating - avg_opp_rating, 2),
                'shifts_tracked': len(ps),
                '_export_timestamp': datetime.now().isoformat()
            })
    
    return pd.DataFrame(records) if records else pd.DataFrame(columns=columns)


def create_fact_player_position_splits() -> pd.DataFrame:
    """Create position-based splits for players."""
    player_game_stats = load_table('fact_player_game_stats')
    roster = load_table('fact_gameroster')
    
    if len(player_game_stats) == 0:
        return pd.DataFrame()
    
    # Join with roster to get positions
    if len(roster) > 0 and 'position' in roster.columns:
        merged = player_game_stats.merge(
            roster[['player_id', 'game_id', 'position']],
            on=['player_id', 'game_id'],
            how='left'
        )
    else:
        merged = player_game_stats.copy()
        merged['position'] = 'Unknown'
    
    # Group by player and position
    numeric_cols = merged.select_dtypes(include=['number']).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ['game_id']]
    
    agg_dict = {col: 'sum' for col in numeric_cols if col in merged.columns}
    agg_dict['game_id'] = 'count'
    
    grouped = merged.groupby(['player_id', 'position']).agg(agg_dict).reset_index()
    grouped = grouped.rename(columns={'game_id': 'games_at_position'})
    
    grouped['split_key'] = grouped['player_id'].astype(str) + '_' + grouped['position'].astype(str)
    grouped['_export_timestamp'] = datetime.now().isoformat()
    
    return grouped


def create_fact_player_trends() -> pd.DataFrame:
    """Create player performance trends over time."""
    player_game_stats = load_table('fact_player_game_stats')
    schedule = load_table('dim_schedule')
    
    if len(player_game_stats) == 0:
        return pd.DataFrame()
    
    # Join with schedule for dates
    if len(schedule) > 0 and 'game_date' in schedule.columns:
        merged = player_game_stats.merge(
            schedule[['game_id', 'game_date']],
            on='game_id',
            how='left'
        )
        merged = merged.sort_values(['player_id', 'game_date'])
    else:
        merged = player_game_stats.copy()
        merged['game_date'] = None
    
    records = []
    
    for player_id in merged['player_id'].dropna().unique():
        player_games = merged[merged['player_id'] == player_id].copy()
        
        if len(player_games) < 2:
            continue
        
        # Calculate rolling averages
        if 'points' in player_games.columns:
            player_games['points_3g_avg'] = player_games['points'].rolling(3, min_periods=1).mean()
        if 'goals' in player_games.columns:
            player_games['goals_3g_avg'] = player_games['goals'].rolling(3, min_periods=1).mean()
        
        for _, row in player_games.iterrows():
            records.append({
                'trend_key': f"{player_id}_{row['game_id']}",
                'player_id': player_id,
                'game_id': row['game_id'],
                'game_date': row.get('game_date'),
                'points_3g_avg': row.get('points_3g_avg', 0),
                'goals_3g_avg': row.get('goals_3g_avg', 0),
                'trend_direction': 'stable',  # Placeholder
                '_export_timestamp': datetime.now().isoformat()
            })
    
    return pd.DataFrame(records)


def create_fact_player_stats_long() -> pd.DataFrame:
    """Create long-format player stats (one row per stat per player-game)."""
    player_game_stats = load_table('fact_player_game_stats')
    
    if len(player_game_stats) == 0:
        return pd.DataFrame()
    
    # Stats to unpivot
    stat_cols = ['goals', 'assists', 'points', 'shots', 'sog', 'passes', 'faceoffs_won', 
                 'faceoffs_lost', 'turnovers', 'takeaways', 'giveaways', 'blocks', 'hits',
                 'toi_seconds', 'toi_minutes']
    stat_cols = [c for c in stat_cols if c in player_game_stats.columns]
    
    if not stat_cols:
        return pd.DataFrame()
    
    id_vars = ['player_game_key', 'game_id', 'player_id']
    id_vars = [c for c in id_vars if c in player_game_stats.columns]
    
    long_df = player_game_stats.melt(
        id_vars=id_vars,
        value_vars=stat_cols,
        var_name='stat_code',
        value_name='stat_value'
    )
    
    long_df['stat_long_key'] = long_df['player_game_key'].astype(str) + '_' + long_df['stat_code']
    long_df['_export_timestamp'] = datetime.now().isoformat()
    
    return long_df


def create_fact_player_stats_by_competition_tier() -> pd.DataFrame:
    """Create player stats split by competition tier."""
    player_game_stats = load_table('fact_player_game_stats')
    shift_players = load_table('fact_shift_players')
    
    if len(player_game_stats) == 0:
        return pd.DataFrame()
    
    # Get avg opponent rating per game
    if len(shift_players) > 0 and 'opp_rating' in shift_players.columns:
        opp_ratings = shift_players.groupby(['game_id', 'player_id'])['opp_rating'].mean().reset_index()
        opp_ratings = opp_ratings.rename(columns={'opp_rating': 'avg_opp_rating'})
        
        merged = player_game_stats.merge(opp_ratings, on=['game_id', 'player_id'], how='left')
    else:
        merged = player_game_stats.copy()
        merged['avg_opp_rating'] = 4.0  # Default
    
    # Assign tiers
    def get_tier(rating):
        if pd.isna(rating):
            return 'Unknown'
        if rating >= 5.0:
            return 'Elite'
        elif rating >= 4.0:
            return 'Above Average'
        elif rating >= 3.0:
            return 'Average'
        else:
            return 'Below Average'
    
    merged['competition_tier'] = merged['avg_opp_rating'].apply(get_tier)
    
    # Group by player and tier
    numeric_cols = merged.select_dtypes(include=['number']).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ['game_id', 'avg_opp_rating']]
    
    agg_dict = {col: 'sum' for col in numeric_cols if col in merged.columns}
    agg_dict['game_id'] = 'count'
    
    grouped = merged.groupby(['player_id', 'competition_tier']).agg(agg_dict).reset_index()
    grouped = grouped.rename(columns={'game_id': 'games_vs_tier'})
    
    grouped['tier_key'] = grouped['player_id'].astype(str) + '_' + grouped['competition_tier']
    grouped['_export_timestamp'] = datetime.now().isoformat()
    
    return grouped


def create_fact_player_pair_stats() -> pd.DataFrame:
    """Create stats for player pairs (similar to H2H but with more detail)."""
    h2h = load_table('fact_h2h')
    
    if len(h2h) == 0:
        return pd.DataFrame()
    
    # Rename columns to match expected schema
    h2h = h2h.copy()
    h2h['pair_key'] = h2h.get('h2h_key', h2h.index.astype(str))
    h2h['_export_timestamp'] = datetime.now().isoformat()
    
    return h2h


def create_fact_player_boxscore_all() -> pd.DataFrame:
    """Create comprehensive boxscore with all players for each game."""
    player_game_stats = load_table('fact_player_game_stats')
    
    if len(player_game_stats) == 0:
        return pd.DataFrame()
    
    # This is essentially the same as player_game_stats but formatted for display
    boxscore = player_game_stats.copy()
    boxscore['boxscore_key'] = boxscore['player_game_key'] if 'player_game_key' in boxscore.columns else boxscore.index.astype(str)
    boxscore['_export_timestamp'] = datetime.now().isoformat()
    
    return boxscore


def create_fact_playergames() -> pd.DataFrame:
    """Create player-game linking table."""
    roster = load_table('fact_gameroster')
    
    if len(roster) == 0:
        return pd.DataFrame()
    
    df = roster[['player_id', 'game_id']].drop_duplicates().copy()
    df['playergame_key'] = df['player_id'].astype(str) + '_' + df['game_id'].astype(str)
    df['_export_timestamp'] = datetime.now().isoformat()
    
    return df


# =============================================================================
# EVENT CHAIN TABLES
# =============================================================================

def create_fact_event_chains() -> pd.DataFrame:
    """Create event chain analysis."""
    linked_events = load_table('fact_linked_events')
    
    if len(linked_events) == 0:
        # Build from scratch
        event_players = load_table('fact_event_players')
        if len(event_players) == 0:
            return pd.DataFrame()
        
        records = []
        
        for game_id in event_players['game_id'].dropna().unique():
            game_events = event_players[event_players['game_id'] == game_id].sort_values('event_id')
            
            # Group consecutive events into chains
            chain_id = 0
            prev_time = None
            
            for idx, row in game_events.iterrows():
                curr_time = row.get('time_start_total_seconds', 0)
                
                # New chain if > 5 seconds gap
                if prev_time is None or abs(curr_time - prev_time) > 5:
                    chain_id += 1
                
                records.append({
                    'chain_key': f"{game_id}_{chain_id}",
                    'game_id': game_id,
                    'chain_id': chain_id,
                    'event_id': row.get('event_id'),
                    'event_type': row.get('event_type'),
                    'event_detail': row.get('event_detail'),
                    'player_id': row.get('player_id'),
                    'sequence_position': len([r for r in records if r.get('chain_id') == chain_id]),
                    '_export_timestamp': datetime.now().isoformat()
                })
                
                prev_time = curr_time
        
        return pd.DataFrame(records)
    
    # Transform linked_events to chains format
    chains = linked_events.copy()
    chains = chains.rename(columns={'linked_event_key': 'chain_key'})
    return chains


def create_fact_player_event_chains() -> pd.DataFrame:
    """Create player-level event chain analysis."""
    columns = ['player_chain_key', 'player_id', 'game_id', 'chains_involved', 
               'events_in_chains', '_export_timestamp']
    
    event_chains = load_table('fact_event_chains')
    
    if len(event_chains) == 0:
        return pd.DataFrame(columns=columns)
    
    # Group by player and chain
    if 'player_id' not in event_chains.columns:
        return pd.DataFrame(columns=columns)
    
    # Filter out empty player_ids
    valid_chains = event_chains[event_chains['player_id'].notna() & 
                                 (event_chains['player_id'].astype(str) != '') &
                                 (event_chains['player_id'].astype(str) != 'nan')]
    
    if len(valid_chains) == 0:
        return pd.DataFrame(columns=columns)
    
    grouped = valid_chains.groupby(['player_id', 'game_id']).agg({
        'chain_key': 'nunique',
        'event_id': 'count'
    }).reset_index()
    
    grouped = grouped.rename(columns={
        'chain_key': 'chains_involved',
        'event_id': 'events_in_chains'
    })
    
    grouped['player_chain_key'] = grouped['player_id'].astype(str) + '_' + grouped['game_id'].astype(str)
    grouped['_export_timestamp'] = datetime.now().isoformat()
    
    return grouped


# =============================================================================
# ZONE ANALYSIS TABLES
# =============================================================================

def create_fact_zone_entry_summary() -> pd.DataFrame:
    """Create zone entry summary stats."""
    event_players = load_table('fact_event_players')
    
    if len(event_players) == 0:
        return pd.DataFrame()
    
    # Filter to zone entries
    zone_events = event_players[
        event_players['event_type'].astype(str).str.lower().str.contains('zone', na=False)
    ]
    
    if len(zone_events) == 0:
        return pd.DataFrame()
    
    records = []
    
    for game_id in zone_events['game_id'].dropna().unique():
        game_zones = zone_events[zone_events['game_id'] == game_id]
        
        for player_id in game_zones['player_id'].dropna().unique():
            if pd.isna(player_id) or str(player_id) in ['', 'None', 'nan']:
                continue
            
            pz = game_zones[game_zones['player_id'] == player_id]
            ed = pz['event_detail'].astype(str).str.lower()
            
            records.append({
                'zone_entry_key': f"{player_id}_{game_id}",
                'game_id': game_id,
                'player_id': player_id,
                'total_entries': len(pz),
                'controlled_entries': ed.str.contains('carry|control', na=False).sum(),
                'dump_entries': ed.str.contains('dump', na=False).sum(),
                'failed_entries': ed.str.contains('fail|turnover', na=False).sum(),
                'entry_success_rate': 0.0,  # Calculate below
                '_export_timestamp': datetime.now().isoformat()
            })
    
    df = pd.DataFrame(records)
    if len(df) > 0:
        total = df['controlled_entries'] + df['dump_entries'] + df['failed_entries']
        df['entry_success_rate'] = ((df['controlled_entries'] + df['dump_entries']) / total.replace(0, 1)).round(3)
    
    return df


def create_fact_zone_exit_summary() -> pd.DataFrame:
    """Create zone exit summary stats."""
    event_players = load_table('fact_event_players')
    
    if len(event_players) == 0:
        return pd.DataFrame()
    
    # Filter to zone exits
    zone_events = event_players[
        event_players['event_type'].astype(str).str.lower().str.contains('zone', na=False)
    ]
    
    if len(zone_events) == 0:
        return pd.DataFrame()
    
    records = []
    
    for game_id in zone_events['game_id'].dropna().unique():
        game_zones = zone_events[zone_events['game_id'] == game_id]
        
        for player_id in game_zones['player_id'].dropna().unique():
            if pd.isna(player_id) or str(player_id) in ['', 'None', 'nan']:
                continue
            
            pz = game_zones[game_zones['player_id'] == player_id]
            ed = pz['event_detail'].astype(str).str.lower()
            
            records.append({
                'zone_exit_key': f"{player_id}_{game_id}",
                'game_id': game_id,
                'player_id': player_id,
                'total_exits': len(pz),
                'controlled_exits': ed.str.contains('carry|pass|control', na=False).sum(),
                'clear_exits': ed.str.contains('clear|dump', na=False).sum(),
                'failed_exits': ed.str.contains('fail|turnover', na=False).sum(),
                'exit_success_rate': 0.0,
                '_export_timestamp': datetime.now().isoformat()
            })
    
    df = pd.DataFrame(records)
    if len(df) > 0:
        total = df['controlled_exits'] + df['clear_exits'] + df['failed_exits']
        df['exit_success_rate'] = ((df['controlled_exits'] + df['clear_exits']) / total.replace(0, 1)).round(3)
    
    return df


def create_fact_team_zone_time() -> pd.DataFrame:
    """Create team zone time analysis."""
    events = load_table('fact_events')
    
    if len(events) == 0:
        return pd.DataFrame()
    
    records = []
    
    for game_id in events['game_id'].dropna().unique():
        game_events = events[events['game_id'] == game_id]
        
        # Count events by zone
        if 'event_team_zone' in game_events.columns:
            zone_counts = game_events['event_team_zone'].value_counts().to_dict()
        else:
            zone_counts = {'offensive': 0, 'neutral': 0, 'defensive': 0}
        
        total = sum(zone_counts.values()) or 1
        
        for venue in ['home', 'away']:
            records.append({
                'zone_time_key': f"{game_id}_{venue}",
                'game_id': game_id,
                'venue': venue,
                'offensive_zone_events': zone_counts.get('offensive', 0) // 2,
                'neutral_zone_events': zone_counts.get('neutral', 0) // 2,
                'defensive_zone_events': zone_counts.get('defensive', 0) // 2,
                'oz_pct': round(zone_counts.get('offensive', 0) / total, 3),
                '_export_timestamp': datetime.now().isoformat()
            })
    
    return pd.DataFrame(records)


# =============================================================================
# MATCHUP TABLES
# =============================================================================

def create_fact_matchup_summary() -> pd.DataFrame:
    """Create matchup summary stats."""
    h2h = load_table('fact_h2h')
    
    if len(h2h) == 0:
        return pd.DataFrame()
    
    # Aggregate H2H to matchup level
    h2h = h2h.copy()
    h2h['matchup_key'] = h2h.get('h2h_key', h2h.index.astype(str))
    h2h['_export_timestamp'] = datetime.now().isoformat()
    
    return h2h


def create_fact_matchup_performance() -> pd.DataFrame:
    """Create matchup performance analysis."""
    h2h = load_table('fact_h2h')
    wowy = load_table('fact_wowy')
    
    if len(h2h) == 0:
        return pd.DataFrame()
    
    # Join H2H with WOWY
    if len(wowy) > 0:
        merged = h2h.merge(wowy, on=['game_id', 'player_1_id', 'player_2_id'], how='left', suffixes=('', '_wowy'))
    else:
        merged = h2h.copy()
    
    merged['performance_key'] = merged.get('h2h_key', merged.index.astype(str)) + '_perf'
    merged['_export_timestamp'] = datetime.now().isoformat()
    
    return merged


def create_fact_head_to_head() -> pd.DataFrame:
    """Alias for fact_h2h with different column names."""
    h2h = load_table('fact_h2h')
    
    if len(h2h) == 0:
        return pd.DataFrame()
    
    df = h2h.copy()
    df = df.rename(columns={'h2h_key': 'head_to_head_key'})
    df['_export_timestamp'] = datetime.now().isoformat()
    
    return df


# =============================================================================
# SPECIAL TEAMS TABLE
# =============================================================================

def create_fact_special_teams_summary() -> pd.DataFrame:
    """Create special teams summary stats."""
    shift_players = load_table('fact_shift_players')
    
    if len(shift_players) == 0:
        return pd.DataFrame()
    
    records = []
    
    for game_id in shift_players['game_id'].dropna().unique():
        game_shifts = shift_players[shift_players['game_id'] == game_id]
        
        for player_id in game_shifts['player_id'].dropna().unique():
            if pd.isna(player_id) or str(player_id) in ['', 'None', 'nan']:
                continue
            
            ps = game_shifts[game_shifts['player_id'] == player_id]
            
            # Filter by strength situation
            if 'strength' in ps.columns:
                pp_shifts = ps[ps['strength'].astype(str).str.contains('5v4|6v5|5v3', na=False)]
                pk_shifts = ps[ps['strength'].astype(str).str.contains('4v5|5v6|3v5', na=False)]
                ev_shifts = ps[ps['strength'].astype(str).str.contains('5v5|4v4|3v3', na=False)]
            else:
                pp_shifts = pd.DataFrame()
                pk_shifts = pd.DataFrame()
                ev_shifts = ps
            
            records.append({
                'special_teams_key': f"{player_id}_{game_id}",
                'game_id': game_id,
                'player_id': player_id,
                'pp_toi': pp_shifts['toi_seconds'].sum() if 'toi_seconds' in pp_shifts.columns else 0,
                'pk_toi': pk_shifts['toi_seconds'].sum() if 'toi_seconds' in pk_shifts.columns else 0,
                'ev_toi': ev_shifts['toi_seconds'].sum() if 'toi_seconds' in ev_shifts.columns else 0,
                'pp_shifts': len(pp_shifts),
                'pk_shifts': len(pk_shifts),
                '_export_timestamp': datetime.now().isoformat()
            })
    
    return pd.DataFrame(records)


# =============================================================================
# XY PLACEHOLDER TABLES (need XY data)
# =============================================================================

def create_fact_player_xy_long() -> pd.DataFrame:
    """Placeholder for player XY coordinates in long format."""
    return pd.DataFrame(columns=[
        'xy_key', 'game_id', 'event_id', 'player_id', 'x', 'y', 
        'zone', 'timestamp', '_export_timestamp'
    ])


def create_fact_player_xy_wide() -> pd.DataFrame:
    """Placeholder for player XY coordinates in wide format."""
    return pd.DataFrame(columns=[
        'xy_key', 'game_id', 'event_id',
        'home_f1_x', 'home_f1_y', 'home_f2_x', 'home_f2_y', 'home_f3_x', 'home_f3_y',
        'home_d1_x', 'home_d1_y', 'home_d2_x', 'home_d2_y', 'home_g_x', 'home_g_y',
        'away_f1_x', 'away_f1_y', 'away_f2_x', 'away_f2_y', 'away_f3_x', 'away_f3_y',
        'away_d1_x', 'away_d1_y', 'away_d2_x', 'away_d2_y', 'away_g_x', 'away_g_y',
        '_export_timestamp'
    ])


def create_fact_puck_xy_long() -> pd.DataFrame:
    """Placeholder for puck XY coordinates in long format."""
    return pd.DataFrame(columns=[
        'puck_xy_key', 'game_id', 'event_id', 'x', 'y', 
        'zone', 'timestamp', '_export_timestamp'
    ])


def create_fact_puck_xy_wide() -> pd.DataFrame:
    """Placeholder for puck XY coordinates in wide format."""
    return pd.DataFrame(columns=[
        'puck_xy_key', 'game_id', 'event_id',
        'puck_x_start', 'puck_y_start', 'puck_x_end', 'puck_y_end',
        '_export_timestamp'
    ])


def create_fact_shot_xy() -> pd.DataFrame:
    """Placeholder for shot XY coordinates."""
    return pd.DataFrame(columns=[
        'shot_xy_key', 'game_id', 'event_id', 'player_id',
        'shot_x', 'shot_y', 'target_x', 'target_y',
        'distance', 'angle', 'danger_zone',
        '_export_timestamp'
    ])


def create_fact_highlights() -> pd.DataFrame:
    """
    Create fact_highlights table from highlighted events.
    
    Links fact_events (where is_highlight = 1) to fact_video via game_id.
    Each highlight has:
    - Primary key: highlight_key (H{game_id}{event_id})
    - Foreign keys: event_id (→ fact_events), video_key (→ fact_video), game_id
    - Video timing: start_time, end_time in video
    - Description: auto-generated from event details
    """
    events = load_table('fact_events')
    videos = load_table('fact_video')
    
    if len(events) == 0:
        return pd.DataFrame(columns=[
            'highlight_key', 'event_id', 'game_id', 'video_key', 'video_url', 'highlight_category_id',
            'period', 'event_type', 'event_detail',
            'video_start_time', 'video_end_time', 'duration_seconds',
            'event_time_display', 'description',
            'event_player_1', 'event_player_2', 'team_id',
            '_export_timestamp'
        ])
    
    # Filter for highlights
    highlights = events[events.get('is_highlight', pd.Series([0] * len(events))) == 1].copy()
    
    if len(highlights) == 0:
        return pd.DataFrame(columns=[
            'highlight_key', 'event_id', 'game_id', 'video_key', 'video_url', 'highlight_category_id',
            'period', 'event_type', 'event_detail',
            'video_start_time', 'video_end_time', 'duration_seconds',
            'event_time_display', 'description',
            'event_player_1', 'event_player_2', 'team_id',
            '_export_timestamp'
        ])
    
    # Merge with video data to get video_key
    if len(videos) > 0:
        # Get primary video for each game (prefer Full_Ice, then first available)
        videos['is_primary'] = videos.get('video_type', '').str.contains('Full_Ice', case=False, na=False)
        primary_videos = videos.sort_values('is_primary', ascending=False).drop_duplicates('game_id', keep='first')
        video_lookup = dict(zip(primary_videos['game_id'].astype(str), primary_videos['video_key']))
    else:
        video_lookup = {}
    
    records = []
    
    for idx, row in highlights.iterrows():
        game_id = str(row.get('game_id', ''))
        event_id = str(row.get('event_id', ''))
        
        if not game_id or not event_id:
            continue
        
        # Generate highlight_key (primary key)
        highlight_key = f"H{game_id}{event_id.replace('EV', '').replace('E', '')}"
        
        # Get video_key (foreign key to fact_video)
        video_key = video_lookup.get(game_id, '')
        
        # Extract video timing
        video_start_time = row.get('running_video_time', '')
        duration = row.get('duration', 0)
        try:
            duration_seconds = int(float(str(duration))) if pd.notna(duration) else 10  # Default 10 sec for highlights
        except:
            duration_seconds = 10
        
        video_end_time = ''
        if pd.notna(video_start_time) and video_start_time != '':
            try:
                start_sec = int(float(str(video_start_time)))
                video_end_time = str(start_sec + duration_seconds)
            except:
                pass
        
        # Event details
        period = row.get('period', '')
        event_type = str(row.get('event_type', ''))
        event_detail = str(row.get('event_detail', ''))
        
        # Create description
        event_time_min = row.get('event_start_min', '')
        event_time_sec = row.get('event_start_sec', '')
        if pd.notna(event_time_min) and pd.notna(event_time_sec):
            event_time_display = f"P{period} {int(event_time_min)}:{int(event_time_sec):02d}"
        else:
            event_time_display = f"P{period}"
        
        # Determine highlight category based on event type
        highlight_category_id = None
        try:
            dim_highlight_category = load_table('dim_highlight_category')
            if len(dim_highlight_category) > 0:
                # Map event types to highlight categories
                event_to_category = {
                    'Goal': 'Goal',
                    'Save': 'Save',
                    'Hit': 'Hit',
                    'Fight': 'Fight',
                    'Breakaway': 'Breakaway',
                    'Penalty_Shot': 'Penalty_Shot',
                }
                category_code = event_to_category.get(event_type, 'Other')
                match = dim_highlight_category[
                    dim_highlight_category['highlight_category_code'] == category_code
                ]
                if len(match) > 0:
                    highlight_category_id = match.iloc[0]['highlight_category_id']
        except:
            pass
        
        # If no match, default to Other
        if not highlight_category_id:
            highlight_category_id = 'HC0010'  # Other
        
        # Build description from event details
        description_parts = []
        if event_type:
            description_parts.append(event_type)
        if event_detail and event_detail.lower() not in ['nan', 'none', '']:
            description_parts.append(event_detail)
        
        # Add player info if available
        player_1 = row.get('event_player_1', '')
        player_2 = row.get('event_player_2', '')
        
        if pd.notna(player_1) and str(player_1).strip():
            description_parts.append(f"by {str(player_1).strip()}")
        if pd.notna(player_2) and str(player_2).strip():
            description_parts.append(f"assist {str(player_2).strip()}")
        
        description = ' - '.join(description_parts) if description_parts else f"{event_type} highlight"
        
        # Team info
        team_id = row.get('team_id', '')
        if pd.isna(team_id) or str(team_id).strip() == '':
            team_id = row.get('event_team_id', '')
        
        # Extract video URL from event (each highlight has its own YouTube link)
        video_url = None
        url_columns = ['video_url', 'highlight_video_url', 'youtube_url', 'video_link', 'url']
        for col in url_columns:
            if col in row.index:
                val = row.get(col)
                if pd.notna(val) and str(val).strip():
                    video_url = str(val).strip()
                    break
        
        records.append({
            'highlight_key': highlight_key,
            'event_id': event_id,  # FK to fact_events
            'game_id': game_id,  # FK to dim_schedule
            'video_key': video_key if video_key else '',  # FK to fact_video (optional, for full game videos)
            'video_url': video_url if video_url else '',  # Direct YouTube link for this highlight
            'highlight_category_id': highlight_category_id,  # FK to dim_highlight_category
            'period': str(period) if pd.notna(period) else '',
            'event_type': event_type,
            'event_detail': event_detail,
            'video_start_time': str(video_start_time) if pd.notna(video_start_time) else '',
            'video_end_time': video_end_time,
            'duration_seconds': str(duration_seconds),
            'event_time_display': event_time_display,
            'description': description,
            'event_player_1': str(player_1) if pd.notna(player_1) else '',
            'event_player_2': str(player_2) if pd.notna(player_2) else '',
            'team_id': str(team_id) if pd.notna(team_id) else '',
            '_export_timestamp': datetime.now().isoformat()
        })
    
    if records:
        df_result = pd.DataFrame(records)
        print(f"Created fact_highlights: {len(df_result)} highlights from {len(highlights)} highlighted events")
        return df_result
    else:
        return pd.DataFrame(columns=[
            'highlight_key', 'event_id', 'game_id', 'video_key', 'video_url', 'highlight_category_id',
            'period', 'event_type', 'event_detail',
            'video_start_time', 'video_end_time', 'duration_seconds',
            'event_time_display', 'description',
            'event_player_1', 'event_player_2', 'team_id',
            '_export_timestamp'
        ])


def create_fact_video() -> pd.DataFrame:
    """
    Create fact_video table from video Excel files in game directories.
    
    Scans data/raw/games/{game_id}/ for video Excel files and extracts:
    - Video URLs
    - Period start times (P1, P2, P3)
    - Video duration
    - Other video metadata
    """
    GAMES_DIR = Path(__file__).parent.parent.parent / 'data' / 'raw' / 'games'
    
    if not GAMES_DIR.exists():
        return pd.DataFrame(columns=[
            'video_key', 'game_id', 'video_type_id', 'video_type', 'video_description',
            'video_url', 'duration_seconds',
            'period_1_start', 'period_2_start', 'period_3_start',
            '_export_timestamp'
        ])
    
    records = []
    games_processed = 0
    games_with_video = 0
    
    # Discover all game directories
    for game_dir in sorted(GAMES_DIR.iterdir()):
        if not game_dir.is_dir() or not game_dir.name.isdigit():
            continue
        
        game_id = game_dir.name
        games_processed += 1
        
        # Look for video Excel files
        # Common patterns: *_video.xlsx, video.xlsx, video_times.xlsx
        video_files = []
        for pattern in ['*_video.xlsx', 'video.xlsx', 'video_times.xlsx', '*video*.xlsx']:
            video_files.extend(list(game_dir.glob(pattern)))
        
        # Also check if tracking file has a video sheet
        tracking_files = list(game_dir.glob("*_tracking.xlsx"))
        for tracking_file in tracking_files:
            if 'bkup' in str(tracking_file).lower():
                continue
            try:
                xl = pd.ExcelFile(tracking_file)
                if 'video' in xl.sheet_names or 'video_times' in xl.sheet_names:
                    video_files.append(tracking_file)
            except:
                pass
        
        if not video_files:
            continue
        
        games_with_video += 1
        
        # Process each video file
        for video_file in video_files:
            try:
                xl = pd.ExcelFile(video_file)
                
                # Try common sheet names
                video_sheet = None
                for sheet_name in ['video', 'video_times', 'Video', 'Video_Times', 'VIDEO']:
                    if sheet_name in xl.sheet_names:
                        video_sheet = sheet_name
                        break
                
                # If no video sheet, try first sheet
                if not video_sheet and len(xl.sheet_names) > 0:
                    video_sheet = xl.sheet_names[0]
                
                if not video_sheet:
                    continue
                
                # Read video data
                df = pd.read_excel(video_file, sheet_name=video_sheet, dtype=str)
                
                # Normalize column names (case-insensitive, handle spaces/underscores)
                df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('-', '_')
                
                # Try to find game_id in data if not already set
                if 'game_id' in df.columns:
                    game_ids = df['game_id'].dropna().unique()
                    if len(game_ids) > 0:
                        # Use first non-null game_id, or keep directory game_id
                        game_id_from_data = str(game_ids[0]).strip()
                        if game_id_from_data and game_id_from_data.isdigit():
                            game_id = game_id_from_data
                
                # Extract video data - handle multiple rows (one per video type or single row)
                for idx, row in df.iterrows():
                    # Generate video_key and extract video type
                    video_type = None
                    video_type_id = None
                    if 'video_type' in df.columns:
                        video_type = str(row.get('video_type', '')).strip()
                    if not video_type or video_type.lower() in ['nan', 'none', '']:
                        video_type = 'Full_Ice'  # Default
                    
                    # Map video_type to video_type_id (lookup from dim_video_type)
                    # Try to load dim_video_type if available
                    try:
                        dim_video_type = load_table('dim_video_type')
                        if len(dim_video_type) > 0:
                            # Match by code (case-insensitive)
                            match = dim_video_type[
                                dim_video_type['video_type_code'].str.upper() == video_type.upper()
                            ]
                            if len(match) > 0:
                                video_type_id = match.iloc[0]['video_type_id']
                    except:
                        pass
                    
                    # If no match found, default to Full_Ice (VT0001)
                    if not video_type_id:
                        video_type_id = 'VT0001'  # Default to Full_Ice
                    
                    # Extract video description
                    video_description = None
                    desc_cols = ['description', 'video_description', 'desc', 'notes', 'comment']
                    for col in desc_cols:
                        if col in df.columns:
                            val = row.get(col)
                            if pd.notna(val) and str(val).strip():
                                video_description = str(val).strip()
                                break
                    
                    # If no description, create one from video type
                    if not video_description:
                        video_type_descriptions = {
                            'Full_Ice': 'Full ice camera view of entire game',
                            'Broadcast': 'Broadcast/television feed of the game',
                            'Highlights': 'Compilation of game highlights',
                            'Goalie': 'Goalie camera view',
                            'Overhead': 'Overhead camera view',
                            'Other': 'Other video type'
                        }
                        video_description = video_type_descriptions.get(video_type, f'{video_type} video')
                    
                    video_key = f"V{game_id}{video_type[:4].upper()}"
                    
                    # Extract video URL - try multiple column variations
                    video_url = None
                    url_columns = ['url_1', 'url', 'video_url', 'youtube_url', 'url1', 'video_link']
                    for col in url_columns:
                        if col in df.columns:
                            val = row.get(col)
                            if pd.notna(val) and str(val).strip():
                                video_url = str(val).strip()
                                break
                    
                    # Extract duration
                    duration_seconds = None
                    duration_cols = ['duration_seconds', 'duration', 'video_duration', 'total_duration', 'length_seconds']
                    for col in duration_cols:
                        if col in df.columns:
                            val = row.get(col)
                            if pd.notna(val):
                                try:
                                    duration_seconds = str(int(float(str(val))))
                                except:
                                    duration_seconds = str(val).strip()
                                break
                    
                    # Extract period start times
                    period_1_start = None
                    period_2_start = None
                    period_3_start = None
                    
                    # Try various column name patterns
                    p1_cols = ['period_1_start', 'p1_start', 'period1_start', 'period_1', 'p1', 'period1']
                    p2_cols = ['period_2_start', 'p2_start', 'period2_start', 'period_2', 'p2', 'period2']
                    p3_cols = ['period_3_start', 'p3_start', 'period3_start', 'period_3', 'p3', 'period3']
                    
                    for col in p1_cols:
                        if col in df.columns:
                            val = row.get(col)
                            if pd.notna(val):
                                try:
                                    period_1_start = str(int(float(str(val))))
                                except:
                                    period_1_start = str(val).strip()
                                break
                    
                    for col in p2_cols:
                        if col in df.columns:
                            val = row.get(col)
                            if pd.notna(val):
                                try:
                                    period_2_start = str(int(float(str(val))))
                                except:
                                    period_2_start = str(val).strip()
                                break
                    
                    for col in p3_cols:
                        if col in df.columns:
                            val = row.get(col)
                            if pd.notna(val):
                                try:
                                    period_3_start = str(int(float(str(val))))
                                except:
                                    period_3_start = str(val).strip()
                                break
                    
                    # Only create record if we have at least a video URL or period start times
                    if video_url or period_1_start or period_2_start or period_3_start:
                        records.append({
                            'video_key': video_key,
                            'game_id': str(game_id),
                            'video_type_id': video_type_id,  # FK to dim_video_type
                            'video_type': video_type,  # Keep for backward compatibility
                            'video_description': video_description,
                            'video_url': video_url if video_url else '',
                            'duration_seconds': duration_seconds if duration_seconds else '',
                            'period_1_start': period_1_start if period_1_start else '',
                            'period_2_start': period_2_start if period_2_start else '',
                            'period_3_start': period_3_start if period_3_start else '',
                            '_export_timestamp': datetime.now().isoformat()
                        })
            
            except Exception as e:
                # Log error but continue processing other files
                print(f"Warning: Error processing video file {video_file} for game {game_id}: {e}")
                continue
    
    if records:
        df_result = pd.DataFrame(records)
        # Deduplicate by video_key (keep first occurrence)
        df_result = df_result.drop_duplicates(subset=['video_key'], keep='first')
        print(f"Created fact_video: {len(df_result)} records from {games_with_video} games (out of {games_processed} total games)")
        return df_result
    else:
        print(f"No video data found in {games_processed} games")
        return pd.DataFrame(columns=[
            'video_key', 'game_id', 'video_type', 'video_description',
            'video_url', 'duration_seconds',
            'period_1_start', 'period_2_start', 'period_3_start',
            '_export_timestamp'
        ])


# =============================================================================
# QA TABLES
# =============================================================================

def create_qa_scorer_comparison() -> pd.DataFrame:
    """Create QA table comparing scorer stats."""
    player_game_stats = load_table('fact_player_game_stats')
    events = load_table('fact_events')
    
    if len(player_game_stats) == 0 or len(events) == 0:
        return pd.DataFrame()
    
    records = []
    
    for game_id in events['game_id'].dropna().unique():
        # Goals from events
        game_events = events[events['game_id'] == game_id]
        event_goals = len(game_events[
            (game_events['event_type'].astype(str).str.lower() == 'goal') &
            (game_events['event_detail'].astype(str).str.lower().str.contains('goal_scored', na=False))
        ])
        
        # Goals from player stats
        game_stats = player_game_stats[player_game_stats['game_id'] == game_id]
        stats_goals = game_stats['goals'].sum() if 'goals' in game_stats.columns else 0
        
        records.append({
            'comparison_key': f"{game_id}_goals",
            'game_id': game_id,
            'metric': 'goals',
            'events_value': event_goals,
            'stats_value': stats_goals,
            'match': event_goals == stats_goals,
            'difference': abs(event_goals - stats_goals),
            '_export_timestamp': datetime.now().isoformat()
        })
    
    return pd.DataFrame(records)


def create_qa_suspicious_stats() -> pd.DataFrame:
    """Create QA table flagging suspicious statistics."""
    player_game_stats = load_table('fact_player_game_stats')
    
    if len(player_game_stats) == 0:
        return pd.DataFrame()
    
    records = []
    
    for _, row in player_game_stats.iterrows():
        flags = []
        
        # Check for suspicious values
        goals = row.get('goals', 0)
        shots = row.get('shots', 0)
        toi = row.get('toi_minutes', 0)
        
        if goals > 5:
            flags.append('high_goals')
        if shots > 20:
            flags.append('high_shots')
        if goals > 0 and shots == 0:
            flags.append('goals_without_shots')
        if toi > 60:
            flags.append('excessive_toi')
        if toi == 0 and (goals > 0 or shots > 0):
            flags.append('stats_without_toi')
        
        if flags:
            records.append({
                'suspicious_key': f"{row.get('player_game_key', '')}",
                'game_id': row.get('game_id'),
                'player_id': row.get('player_id'),
                'flags': ','.join(flags),
                'goals': goals,
                'shots': shots,
                'toi_minutes': toi,
                '_export_timestamp': datetime.now().isoformat()
            })
    
    return pd.DataFrame(records)


def create_fact_suspicious_stats() -> pd.DataFrame:
    """Alias for qa_suspicious_stats in fact table format."""
    return create_qa_suspicious_stats()


# =============================================================================
# LOOKUP TABLE
# =============================================================================

def create_lookup_player_game_rating() -> pd.DataFrame:
    """Create player-game rating lookup."""
    columns = ['lookup_key', 'game_id', 'player_id', 'avg_rating', 'avg_opp_rating', '_export_timestamp']
    
    shift_players = load_table('fact_shift_players')
    
    if len(shift_players) == 0:
        return pd.DataFrame(columns=columns)
    
    # FIX: Column is 'player_rating' not 'rating'
    if 'player_rating' not in shift_players.columns:
        return pd.DataFrame(columns=columns)
    
    # FIX: Use correct column names
    agg_dict = {'player_rating': 'mean'}
    if 'opp_avg_rating' in shift_players.columns:
        agg_dict['opp_avg_rating'] = 'mean'
    
    grouped = shift_players.groupby(['game_id', 'player_id']).agg(agg_dict).reset_index()
    
    grouped = grouped.rename(columns={
        'player_rating': 'avg_rating',
        'opp_avg_rating': 'avg_opp_rating'
    })
    
    # Add avg_opp_rating if not present
    if 'avg_opp_rating' not in grouped.columns:
        grouped['avg_opp_rating'] = 0
    
    grouped['lookup_key'] = grouped['player_id'].astype(str) + '_' + grouped['game_id'].astype(str)
    grouped['_export_timestamp'] = datetime.now().isoformat()
    
    return grouped


# =============================================================================
# MAIN BUILDER
# =============================================================================

def build_remaining_tables(verbose: bool = True) -> dict:
    """Build all remaining tables."""
    results = {
        'tables_created': [],
        'total_rows': 0,
        'errors': []
    }
    
    # All remaining table builders
    builders = [
        # Period-level
        ('fact_player_period_stats', create_fact_player_period_stats),
        ('fact_period_momentum', create_fact_period_momentum),
        
        # Aggregation/rollup
        ('fact_player_season_stats', create_fact_player_season_stats),
        ('fact_player_career_stats', create_fact_player_career_stats),
        ('fact_team_season_stats', create_fact_team_season_stats),
        # DEPRECATED - replaced by views (v28.3):
        # ('fact_team_standings_snapshot', create_fact_team_standings_snapshot),
        # ('fact_league_leaders_snapshot', create_fact_league_leaders_snapshot),
        
        # Player analytics
        ('fact_player_micro_stats', create_fact_player_micro_stats),
        ('fact_player_qoc_summary', create_fact_player_qoc_summary),
        ('fact_player_position_splits', create_fact_player_position_splits),
        ('fact_player_trends', create_fact_player_trends),
        ('fact_player_stats_long', create_fact_player_stats_long),
        ('fact_player_stats_by_competition_tier', create_fact_player_stats_by_competition_tier),
        ('fact_player_pair_stats', create_fact_player_pair_stats),
        ('fact_player_boxscore_all', create_fact_player_boxscore_all),
        ('fact_playergames', create_fact_playergames),
        
        # Event chains
        ('fact_event_chains', create_fact_event_chains),
        ('fact_player_event_chains', create_fact_player_event_chains),
        
        # Zone analysis
        ('fact_zone_entry_summary', create_fact_zone_entry_summary),
        ('fact_zone_exit_summary', create_fact_zone_exit_summary),
        ('fact_team_zone_time', create_fact_team_zone_time),
        
        # Matchups
        ('fact_matchup_summary', create_fact_matchup_summary),
        ('fact_matchup_performance', create_fact_matchup_performance),
        ('fact_head_to_head', create_fact_head_to_head),
        
        # Special teams
        ('fact_special_teams_summary', create_fact_special_teams_summary),
        
        # XY placeholders
        ('fact_player_xy_long', create_fact_player_xy_long),
        ('fact_player_xy_wide', create_fact_player_xy_wide),
        ('fact_puck_xy_long', create_fact_puck_xy_long),
        ('fact_puck_xy_wide', create_fact_puck_xy_wide),
        ('fact_shot_xy', create_fact_shot_xy),
        ('fact_video', create_fact_video),
        ('fact_highlights', create_fact_highlights),
        
        # QA
        ('qa_scorer_comparison', create_qa_scorer_comparison),
        ('qa_suspicious_stats', create_qa_suspicious_stats),
        ('fact_suspicious_stats', create_fact_suspicious_stats),
        
        # Lookup
        ('lookup_player_game_rating', create_lookup_player_game_rating),
    ]
    
    if verbose:
        print("\n" + "=" * 70)
        print("BUILDING REMAINING TABLES")
        print("=" * 70)
    
    for table_name, builder_func in builders:
        try:
            if verbose:
                print(f"\nBuilding {table_name}...", end=' ')
            
            df = builder_func()
            rows = save_table(df, table_name)
            
            results['tables_created'].append(table_name)
            results['total_rows'] += rows
            
            if verbose:
                print(f"✓ {rows} rows")
                
        except Exception as e:
            error_msg = f"{table_name}: {str(e)}"
            results['errors'].append(error_msg)
            if verbose:
                print(f"✗ ERROR: {e}")
    
    if verbose:
        print("\n" + "=" * 70)
        print(f"Created {len(results['tables_created'])} additional tables")
        print(f"Total rows: {results['total_rows']:,}")
        if results['errors']:
            print(f"Errors: {len(results['errors'])}")
        print("=" * 70)
    
    return results


if __name__ == '__main__':
    build_remaining_tables(verbose=True)
