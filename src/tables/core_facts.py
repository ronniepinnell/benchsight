#!/usr/bin/env python3
"""
BenchSight Core Fact Tables Builder
Creates fact_player_game_stats, fact_team_game_stats, fact_goalie_game_stats

Version: 26.1 - Phase 3 Expansion
Changes from 25.2:
  - Linemate Analysis (8 columns): unique_linemates, top partner, chemistry score
  - Time Bucket Analysis (11 columns): early/late period performance
  - Rebound/Second Chance (7 columns): rebounds, crash net, garbage goals
  
Previous v25.2:
  - EXCLUDES goalies from fact_player_game_stats
  - Strength/Situation splits (EV/PP/PK/EN)
  - Shot Type breakdown (wrist, slap, one-timer, etc.)
  - Pass Type analysis (stretch, bank, rim, etc.)
  - Shot Assists / Playmaking metrics
  - Pressure Stats (under pressure performance)
  - Sequence Analytics (play chain involvement)
  - Competition Tier performance
  - Game State analysis (leading/trailing/close)
  - Adjusted Rating (what rating did they play like?)
  - Goalie WAR (separate model)
  - Goalie Save Type breakdown

Target: 325+ columns in fact_player_game_stats
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import math
from src.formulas.formula_applier import apply_player_stats_formulas

OUTPUT_DIR = Path('data/output')

# =============================================================================
# CONSTANTS - Single Source of Truth
# =============================================================================

def is_goal_scored(df, event_type_col='event_type', event_detail_col='event_detail'):
    """Single source of truth for goal identification."""
    return (
        (df[event_type_col].astype(str).str.lower() == 'goal') &
        (df[event_detail_col].astype(str).str.lower().str.contains('goal_scored', na=False))
    )

PRIMARY_PLAYER = 'event_player_1'
# ASSIST TRACKING: Assists tracked via play_detail1='AssistPrimary'/'AssistSecondary'
# NOT via player_role. The assister is event_player_1 on their assist event.
ASSIST_PRIMARY_DETAIL = 'assistprimary'
ASSIST_SECONDARY_DETAIL = 'assistsecondary'

# xG Model
XG_BASE_RATES = {'high_danger': 0.25, 'medium_danger': 0.08, 'low_danger': 0.03, 'default': 0.06}
XG_MODIFIERS = {'rush': 1.3, 'rebound': 1.5, 'one_timer': 1.4, 'breakaway': 2.5, 'screened': 1.2, 'deflection': 1.3}
# Shot type modifiers (for xG calculation)
SHOT_TYPE_XG_MODIFIERS = {'wrist': 1.0, 'slap': 0.95, 'snap': 1.05, 'backhand': 0.9, 'tip': 1.15, 'deflection': 1.1}

# WAR/GAR Weights
GAR_WEIGHTS = {
    'goals': 1.0, 'primary_assists': 0.7, 'secondary_assists': 0.4,
    'shots_generated': 0.015, 'xg_generated': 0.8,
    'takeaways': 0.05, 'blocked_shots': 0.02, 'defensive_zone_exits': 0.03,
    'cf_above_avg': 0.02, 'zone_entry_value': 0.04,
    'shot_assists': 0.3,  # NEW: playmaking
    'pressure_success': 0.02,  # NEW: poise under pressure
}

# Goalie WAR Weights (NEW)
GOALIE_GAR_WEIGHTS = {
    'saves_above_avg': 0.1,      # Per save above expected
    'high_danger_saves': 0.15,   # HD saves worth more
    'goals_prevented': 1.0,      # GSAx directly
    'rebound_control': 0.05,     # Freeze vs rebound
    'quality_start_bonus': 0.5,  # Bonus for QS
}

GOALS_PER_WIN = 4.5
GAMES_PER_SEASON = 20
LEAGUE_AVG_SV_PCT = 88.0

# Rating scale expectations (for adjusted rating calculation)
RATING_GAME_SCORE_MAP = {
    1: 1.0, 2: 2.3, 3: 3.5, 4: 4.7, 5: 5.9, 6: 7.1, 7: 8.3, 8: 9.5, 9: 10.7, 10: 12.0
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def save_table(df: pd.DataFrame, name: str) -> int:
    """
    Save table to CSV, automatically adding player_name and team_name columns.
    Also removes 100% null columns (except coordinate/danger/xy type columns).
    
    This ensures all tables with player_id or team_id also have corresponding name columns.
    """
    if df is not None and len(df) > 0:
        df = add_names_to_table(df)
        
        # Drop 100% null columns (except coordinate/danger/xy columns)
        from src.core.base_etl import drop_all_null_columns
        df, removed_cols = drop_all_null_columns(df)
        if removed_cols:
            print(f"  {name}: Removed {len(removed_cols)} all-null columns: {', '.join(removed_cols[:5])}{'...' if len(removed_cols) > 5 else ''}")
    
    path = OUTPUT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    return len(df)

def load_table(name: str, required: bool = False) -> pd.DataFrame:
    """
    Load a table from cache first, then from CSV.
    
    This checks the in-memory table store first (for tables created in this ETL run),
    then falls back to CSV files. This allows the ETL to work from scratch without
    relying on previously generated CSVs.
    
    Args:
        name: Table name (without .csv extension)
        required: If True, warn when table is missing (for critical dependencies)
    
    Returns:
        DataFrame with table data, or empty DataFrame if not found
    """
    # Try table store first (in-memory cache from this run)
    try:
        from src.core.table_store import get_table
        df = get_table(name, OUTPUT_DIR)
        if len(df) > 0:
            return df
        # If in store but empty, that's the actual state
        if name in get_table.__self__._table_store if hasattr(get_table, '__self__') else False:
            if required:
                print(f"  WARNING: {name} is EMPTY (required dependency)")
            return df
    except Exception:
        pass
    
    # Fall back to CSV (for tables from previous runs)
    path = OUTPUT_DIR / f"{name}.csv"
    if not path.exists():
        if required:
            print(f"  WARNING: Required table {name} not found - dependent table may be empty")
        return pd.DataFrame()
    try:
        df = pd.read_csv(path, low_memory=False)
        if len(df) == 0 and required:
            print(f"  WARNING: {name} exists but is EMPTY (required dependency)")
        return df
    except pd.errors.EmptyDataError:
        # File exists but has no data/columns
        if required:
            print(f"  WARNING: {name} exists but has no data (required dependency)")
        return pd.DataFrame()
    except Exception as e:
        # Log error but return empty DataFrame to prevent crashes
        if required:
            print(f"  ERROR: Failed to load {name}: {e}")
        import logging
        logging.getLogger('ETL').warning(f"Error loading {name}: {e}")
        return pd.DataFrame()

def add_names_to_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add player_name and team_name columns to any table that has player_id or team_id.
    
    This utility function ensures all fact tables with IDs also have corresponding name columns
    for easier reporting and analysis.
    
    Args:
        df: DataFrame that may contain player_id, team_id, or related columns
        
    Returns:
        DataFrame with name columns added where applicable
    """
    if df is None or len(df) == 0:
        return df
    
    df = df.copy()
    dim_player = None
    dim_team = None
    
    # Load dimension tables if needed
    has_player_cols = any(col in df.columns for col in ['player_id', 'player_1_id', 'player_2_id', 'event_player_1_id', 'event_player_2_id', 'opp_player_1_id', 'faceoff_winner_id', 'faceoff_loser_id'])
    has_team_cols = any(col in df.columns for col in ['team_id', 'home_team_id', 'away_team_id', 'event_team_id', 'player_team_id', 'opp_team_id'])
    
    if has_player_cols:
        dim_player = load_table('dim_player')
    
    if has_team_cols:
        dim_team = load_table('dim_team')
    
    # Add player names
    if dim_player is not None and len(dim_player) > 0:
        # Standard player_id -> player_name
        if 'player_id' in df.columns and 'player_name' not in df.columns:
            player_map = dim_player.set_index('player_id')['player_full_name'].to_dict()
            df['player_name'] = df['player_id'].map(player_map)
            # Fallback to player_name column if player_full_name doesn't exist
            if df['player_name'].isna().all() and 'player_name' in dim_player.columns:
                player_map = dim_player.set_index('player_id')['player_name'].to_dict()
                df['player_name'] = df['player_id'].map(player_map)
        
        # player_1_id -> player_1_name
        if 'player_1_id' in df.columns and 'player_1_name' not in df.columns:
            player_map = dim_player.set_index('player_id')['player_full_name'].to_dict()
            df['player_1_name'] = df['player_1_id'].map(player_map)
            if df['player_1_name'].isna().all() and 'player_name' in dim_player.columns:
                player_map = dim_player.set_index('player_id')['player_name'].to_dict()
                df['player_1_name'] = df['player_1_id'].map(player_map)
        
        # player_2_id -> player_2_name
        if 'player_2_id' in df.columns and 'player_2_name' not in df.columns:
            player_map = dim_player.set_index('player_id')['player_full_name'].to_dict()
            df['player_2_name'] = df['player_2_id'].map(player_map)
            if df['player_2_name'].isna().all() and 'player_name' in dim_player.columns:
                player_map = dim_player.set_index('player_id')['player_name'].to_dict()
                df['player_2_name'] = df['player_2_id'].map(player_map)
        
        # event_player_1_id -> event_player_1_name
        if 'event_player_1_id' in df.columns and 'event_player_1_name' not in df.columns:
            player_map = dim_player.set_index('player_id')['player_full_name'].to_dict()
            df['event_player_1_name'] = df['event_player_1_id'].map(player_map)
            if df['event_player_1_name'].isna().all() and 'player_name' in dim_player.columns:
                player_map = dim_player.set_index('player_id')['player_name'].to_dict()
                df['event_player_1_name'] = df['event_player_1_id'].map(player_map)
        
        # event_player_2_id -> event_player_2_name
        if 'event_player_2_id' in df.columns and 'event_player_2_name' not in df.columns:
            player_map = dim_player.set_index('player_id')['player_full_name'].to_dict()
            df['event_player_2_name'] = df['event_player_2_id'].map(player_map)
            if df['event_player_2_name'].isna().all() and 'player_name' in dim_player.columns:
                player_map = dim_player.set_index('player_id')['player_name'].to_dict()
                df['event_player_2_name'] = df['event_player_2_id'].map(player_map)
        
        # opp_player_1_id -> opp_player_1_name
        if 'opp_player_1_id' in df.columns and 'opp_player_1_name' not in df.columns:
            player_map = dim_player.set_index('player_id')['player_full_name'].to_dict()
            df['opp_player_1_name'] = df['opp_player_1_id'].map(player_map)
            if df['opp_player_1_name'].isna().all() and 'player_name' in dim_player.columns:
                player_map = dim_player.set_index('player_id')['player_name'].to_dict()
                df['opp_player_1_name'] = df['opp_player_1_id'].map(player_map)
        
        # faceoff_winner_id -> faceoff_winner_name
        if 'faceoff_winner_id' in df.columns and 'faceoff_winner_name' not in df.columns:
            player_map = dim_player.set_index('player_id')['player_full_name'].to_dict()
            df['faceoff_winner_name'] = df['faceoff_winner_id'].map(player_map)
            if df['faceoff_winner_name'].isna().all() and 'player_name' in dim_player.columns:
                player_map = dim_player.set_index('player_id')['player_name'].to_dict()
                df['faceoff_winner_name'] = df['faceoff_winner_id'].map(player_map)
        
        # faceoff_loser_id -> faceoff_loser_name
        if 'faceoff_loser_id' in df.columns and 'faceoff_loser_name' not in df.columns:
            player_map = dim_player.set_index('player_id')['player_full_name'].to_dict()
            df['faceoff_loser_name'] = df['faceoff_loser_id'].map(player_map)
            if df['faceoff_loser_name'].isna().all() and 'player_name' in dim_player.columns:
                player_map = dim_player.set_index('player_id')['player_name'].to_dict()
                df['faceoff_loser_name'] = df['faceoff_loser_id'].map(player_map)
    
    # Add team names
    if dim_team is not None and len(dim_team) > 0:
        # Standard team_id -> team_name
        if 'team_id' in df.columns and 'team_name' not in df.columns:
            team_map = dim_team.set_index('team_id')['team_name'].to_dict()
            df['team_name'] = df['team_id'].map(team_map)
        
        # home_team_id -> home_team_name
        if 'home_team_id' in df.columns and 'home_team_name' not in df.columns:
            team_map = dim_team.set_index('team_id')['team_name'].to_dict()
            df['home_team_name'] = df['home_team_id'].map(team_map)
        
        # away_team_id -> away_team_name
        if 'away_team_id' in df.columns and 'away_team_name' not in df.columns:
            team_map = dim_team.set_index('team_id')['team_name'].to_dict()
            df['away_team_name'] = df['away_team_id'].map(team_map)
        
        # event_team_id -> event_team_name
        if 'event_team_id' in df.columns and 'event_team_name' not in df.columns:
            team_map = dim_team.set_index('team_id')['team_name'].to_dict()
            df['event_team_name'] = df['event_team_id'].map(team_map)
        
        # player_team_id -> player_team_name
        if 'player_team_id' in df.columns and 'player_team_name' not in df.columns:
            team_map = dim_team.set_index('team_id')['team_name'].to_dict()
            df['player_team_name'] = df['player_team_id'].map(team_map)
        
        # opp_team_id -> opp_team_name
        if 'opp_team_id' in df.columns and 'opp_team_name' not in df.columns:
            team_map = dim_team.set_index('team_id')['team_name'].to_dict()
            df['opp_team_name'] = df['opp_team_id'].map(team_map)
    
    return df

def get_game_ids() -> list:
    events = load_table('fact_events')
    return sorted(events['game_id'].dropna().unique().tolist()) if len(events) > 0 else []

def get_players_in_game(game_id: int, event_players: pd.DataFrame, roster: pd.DataFrame) -> list:
    """Get all SKATER player IDs (excludes goalies)."""
    game_events = event_players[event_players['game_id'] == game_id]
    event_player_ids = game_events['player_id'].dropna().unique().tolist()
    
    game_roster = roster[roster['game_id'] == game_id]
    
    # Get all roster player IDs
    roster_player_ids = game_roster['player_id'].dropna().unique().tolist()
    
    # Get goalie player IDs to EXCLUDE
    pos_col = 'player_position' if 'player_position' in game_roster.columns else 'position'
    goalie_ids = set()
    if pos_col in game_roster.columns:
        goalies = game_roster[game_roster[pos_col].astype(str).str.lower().str.contains('goalie', na=False)]
        goalie_ids = set(goalies['player_id'].dropna().unique().tolist())
    
    # Combine event + roster players, then EXCLUDE goalies
    all_players = list(set(event_player_ids + roster_player_ids))
    skaters = [p for p in all_players if pd.notna(p) and str(p) not in ['nan', '', 'None'] and p not in goalie_ids]
    return skaters

def calculate_adjusted_rating(game_score: float) -> float:
    """
    Convert game score to equivalent skill rating.
    A player rated 4 who scores game_score=7.1 "played like a 6".
    """
    if game_score <= 0:
        return 1.0
    
    # Find closest rating match
    best_rating = 1
    min_diff = float('inf')
    
    for rating, expected_gs in RATING_GAME_SCORE_MAP.items():
        diff = abs(game_score - expected_gs)
        if diff < min_diff:
            min_diff = diff
            best_rating = rating
    
    # Interpolate for more precision
    if game_score < RATING_GAME_SCORE_MAP[1]:
        return 1.0
    elif game_score > RATING_GAME_SCORE_MAP[10]:
        return 10.0
    else:
        # Linear interpolation between ratings
        for r in range(1, 10):
            low_gs = RATING_GAME_SCORE_MAP[r]
            high_gs = RATING_GAME_SCORE_MAP[r + 1]
            if low_gs <= game_score <= high_gs:
                pct = (game_score - low_gs) / (high_gs - low_gs)
                return round(r + pct, 1)
    
    return round(best_rating, 1)

# =============================================================================
# STRENGTH/SITUATION SPLITS (NEW)
# =============================================================================

def calculate_strength_splits(player_id, game_id, event_players: pd.DataFrame,
                              shift_players: pd.DataFrame, events: pd.DataFrame) -> dict:
    """Calculate stats by game situation (EV, PP, PK, EN) with period breakdowns."""
    stats = {}
    
    # Get player's shifts by strength (use logical shifts to avoid double-counting)
    ps = shift_players[
        (shift_players['game_id'] == game_id) & 
        (shift_players['player_id'] == player_id)
    ] if len(shift_players) > 0 else pd.DataFrame()
    
    # If logical_shift_number exists, group by it to avoid double-counting
    if len(ps) > 0 and 'logical_shift_number' in ps.columns:
        # Aggregate by logical shift to get unique shifts
        logical_shifts = ps.groupby(['logical_shift_number', 'strength', 'period']).agg({
            'shift_duration': 'first',  # Duration should be same for all rows in logical shift
            'cf': 'first',  # CF/CA should be same for all rows in logical shift
            'ca': 'first',
            'gf': 'first',
            'ga': 'first',
        }).reset_index()
        ps = logical_shifts
    
    # Get player's events
    pe = event_players[
        (event_players['game_id'] == game_id) & 
        (event_players['player_id'] == player_id)
    ]
    
    # Map strengths
    strength_map = {
        'ev': ['5v5', '4v4', '3v3'],
        'pp': ['5v4', '5v3', '4v3'],
        'pk': ['4v5', '3v5', '3v4'],
        'en': ['5v6', '6v5', '4v6', '6v4'],
    }
    
    for sit, strengths in strength_map.items():
        prefix = f'{sit}_'
        
        # TOI by situation
        if len(ps) > 0 and 'strength' in ps.columns:
            sit_shifts = ps[ps['strength'].isin(strengths)]
            stats[f'{prefix}toi_seconds'] = int(sit_shifts['shift_duration'].sum()) if 'shift_duration' in sit_shifts.columns else 0
            
            # Corsi by situation - use logical shifts to avoid double-counting
            # CF/CA should be per logical shift, not per row
            if 'cf' in sit_shifts.columns and 'ca' in sit_shifts.columns:
                # Sum CF/CA from unique logical shifts only
                if 'logical_shift_number' in sit_shifts.columns:
                    # Already grouped by logical shift above
                    cf = sit_shifts['cf'].sum()
                    ca = sit_shifts['ca'].sum()
                else:
                    # Fallback: use first value per shift if grouping didn't work
                    cf = sit_shifts['cf'].sum()
                    ca = sit_shifts['ca'].sum()
                
                stats[f'{prefix}cf'] = int(cf)
                stats[f'{prefix}ca'] = int(ca)
                stats[f'{prefix}cf_pct'] = round(cf / (cf + ca) * 100, 1) if (cf + ca) > 0 else 50.0
            else:
                stats[f'{prefix}cf'] = 0
                stats[f'{prefix}ca'] = 0
                stats[f'{prefix}cf_pct'] = 50.0
            
            # Goals for/against by situation
            if f'gf_{sit}' in sit_shifts.columns:
                stats[f'{prefix}gf'] = int(sit_shifts[f'gf_{sit}'].sum())
                stats[f'{prefix}ga'] = int(sit_shifts[f'ga_{sit}'].sum()) if f'ga_{sit}' in sit_shifts.columns else 0
            else:
                stats[f'{prefix}gf'] = int(sit_shifts['gf'].sum()) if 'gf' in sit_shifts.columns else 0
                stats[f'{prefix}ga'] = int(sit_shifts['ga'].sum()) if 'ga' in sit_shifts.columns else 0
            
            # Period breakdowns for special teams (PP and PK)
            if sit in ['pp', 'pk'] and 'period' in sit_shifts.columns:
                for period in [1, 2, 3]:
                    period_shifts = sit_shifts[sit_shifts['period'] == period]
                    period_prefix = f'{prefix}p{period}_'
                    
                    stats[f'{period_prefix}toi_seconds'] = int(period_shifts['shift_duration'].sum()) if 'shift_duration' in period_shifts.columns else 0
                    
                    if 'cf' in period_shifts.columns and 'ca' in period_shifts.columns:
                        period_cf = period_shifts['cf'].sum()
                        period_ca = period_shifts['ca'].sum()
                        stats[f'{period_prefix}cf'] = int(period_cf)
                        stats[f'{period_prefix}ca'] = int(period_ca)
                        stats[f'{period_prefix}cf_pct'] = round(period_cf / (period_cf + period_ca) * 100, 1) if (period_cf + period_ca) > 0 else 50.0
                    else:
                        stats[f'{period_prefix}cf'] = 0
                        stats[f'{period_prefix}ca'] = 0
                        stats[f'{period_prefix}cf_pct'] = 50.0
                    
                    if 'gf' in period_shifts.columns:
                        stats[f'{period_prefix}gf'] = int(period_shifts['gf'].sum())
                        stats[f'{period_prefix}ga'] = int(period_shifts['ga'].sum())
                    else:
                        stats[f'{period_prefix}gf'] = 0
                        stats[f'{period_prefix}ga'] = 0
            else:
                # Initialize period columns to 0 if not PP/PK
                if sit in ['pp', 'pk']:
                    for period in [1, 2, 3]:
                        period_prefix = f'{prefix}p{period}_'
                        stats[f'{period_prefix}toi_seconds'] = 0
                        stats[f'{period_prefix}cf'] = 0
                        stats[f'{period_prefix}ca'] = 0
                        stats[f'{period_prefix}cf_pct'] = 50.0
                        stats[f'{period_prefix}gf'] = 0
                        stats[f'{period_prefix}ga'] = 0
        else:
            stats[f'{prefix}toi_seconds'] = 0
            stats[f'{prefix}cf'] = 0
            stats[f'{prefix}ca'] = 0
            stats[f'{prefix}cf_pct'] = 50.0
            stats[f'{prefix}gf'] = 0
            stats[f'{prefix}ga'] = 0
            # Initialize period columns
            if sit in ['pp', 'pk']:
                for period in [1, 2, 3]:
                    period_prefix = f'{prefix}p{period}_'
                    stats[f'{period_prefix}toi_seconds'] = 0
                    stats[f'{period_prefix}cf'] = 0
                    stats[f'{period_prefix}ca'] = 0
                    stats[f'{period_prefix}cf_pct'] = 50.0
                    stats[f'{period_prefix}gf'] = 0
                    stats[f'{period_prefix}ga'] = 0
        
        # Individual scoring by situation (from events)
        if len(pe) > 0 and 'strength' in pe.columns:
            sit_events = pe[pe['strength'].isin(strengths)]
        elif len(pe) > 0:
            # Estimate from shift overlap
            sit_events = pe  # Fallback
        else:
            sit_events = pd.DataFrame()
        
        if len(sit_events) > 0:
            # Only count where player is event_player_1
            sit_primary = sit_events[sit_events['player_role'].astype(str).str.lower() == PRIMARY_PLAYER]
            
            goals = sit_primary[is_goal_scored(sit_primary)]
            stats[f'{prefix}goals'] = len(goals)
            
            # Assists via play_detail1='AssistPrimary'/'AssistSecondary' where player is event_player_1
            if 'play_detail1' in sit_primary.columns:
                assists = sit_primary[sit_primary['play_detail1'].astype(str).str.lower().isin([ASSIST_PRIMARY_DETAIL, ASSIST_SECONDARY_DETAIL])]
                stats[f'{prefix}assists'] = len(assists)
            else:
                stats[f'{prefix}assists'] = 0
            stats[f'{prefix}points'] = stats[f'{prefix}goals'] + stats[f'{prefix}assists']
            
            shots = sit_primary[sit_primary['event_type'].astype(str).str.lower() == 'shot']
            stats[f'{prefix}shots'] = len(shots)
        else:
            stats[f'{prefix}goals'] = 0
            stats[f'{prefix}assists'] = 0
            stats[f'{prefix}points'] = 0
            stats[f'{prefix}shots'] = 0
    
    # Special teams summary
    total_toi = stats.get('ev_toi_seconds', 0) + stats.get('pp_toi_seconds', 0) + stats.get('pk_toi_seconds', 0)
    stats['pp_toi_pct'] = round(stats['pp_toi_seconds'] / total_toi * 100, 1) if total_toi > 0 else 0.0
    stats['pk_toi_pct'] = round(stats['pk_toi_seconds'] / total_toi * 100, 1) if total_toi > 0 else 0.0
    
    return stats

# =============================================================================
# SHOT TYPE ANALYSIS (NEW)
# =============================================================================

def calculate_shot_type_stats(player_id, game_id, event_players: pd.DataFrame,
                               events: pd.DataFrame) -> dict:
    """Calculate shot breakdown by type."""
    stats = {}
    
    pe = event_players[
        (event_players['game_id'] == game_id) & 
        (event_players['player_id'] == player_id) &
        (event_players['player_role'].astype(str).str.lower() == PRIMARY_PLAYER)
    ]
    
    if len(pe) == 0:
        return _get_empty_shot_type_stats()
    
    player_event_ids = pe['event_id'].unique() if 'event_id' in pe.columns else []
    game_events = events[events['game_id'] == game_id]
    
    # Get shots and goals
    player_shots = game_events[
        (game_events['event_id'].isin(player_event_ids)) &
        (game_events['event_type'].astype(str).str.lower().isin(['shot', 'goal']))
    ] if len(player_event_ids) > 0 else pd.DataFrame()
    
    if len(player_shots) == 0:
        return _get_empty_shot_type_stats()
    
    # Count by shot type (from event_detail_2)
    def count_shot_type(pattern):
        if 'event_detail_2' not in player_shots.columns:
            return 0
        return int(player_shots['event_detail_2'].astype(str).str.lower().str.contains(pattern, na=False).sum())
    
    stats['shots_wrist'] = count_shot_type(r'wrist')
    stats['shots_slap'] = count_shot_type(r'slap')
    stats['shots_snap'] = count_shot_type(r'snap')
    stats['shots_backhand'] = count_shot_type(r'backhand')
    stats['shots_one_timer'] = count_shot_type(r'onetime|one_time')
    stats['shots_tip'] = count_shot_type(r'tip')
    stats['shots_deflection'] = count_shot_type(r'deflect')
    stats['shots_wraparound'] = count_shot_type(r'wrap')
    stats['shots_poke'] = count_shot_type(r'poke')
    stats['shots_bat'] = count_shot_type(r'bat')
    
    # Goals by type
    goals = player_shots[player_shots['event_type'].astype(str).str.lower() == 'goal']
    
    def count_goal_type(pattern):
        if 'event_detail_2' not in goals.columns:
            return 0
        return int(goals['event_detail_2'].astype(str).str.lower().str.contains(pattern, na=False).sum())
    
    stats['goals_wrist'] = count_goal_type(r'wrist')
    stats['goals_one_timer'] = count_goal_type(r'onetime|one_time')
    stats['goals_tip'] = count_goal_type(r'tip|deflect')
    stats['goals_backhand'] = count_goal_type(r'backhand')
    
    # Shooting percentages by type
    stats['wrist_shot_pct'] = round(stats['goals_wrist'] / stats['shots_wrist'] * 100, 1) if stats['shots_wrist'] > 0 else 0.0
    stats['one_timer_pct'] = round(stats['goals_one_timer'] / stats['shots_one_timer'] * 100, 1) if stats['shots_one_timer'] > 0 else 0.0
    
    # Primary shot type
    shot_counts = {
        'wrist': stats['shots_wrist'],
        'slap': stats['shots_slap'],
        'snap': stats['shots_snap'],
        'backhand': stats['shots_backhand'],
        'one_timer': stats['shots_one_timer'],
    }
    stats['primary_shot_type'] = max(shot_counts, key=shot_counts.get) if any(shot_counts.values()) else 'none'
    
    # Shot variety (how many different types used)
    stats['shot_type_variety'] = sum(1 for v in shot_counts.values() if v > 0)
    
    return stats

def _get_empty_shot_type_stats():
    return {
        'shots_wrist': 0, 'shots_slap': 0, 'shots_snap': 0, 'shots_backhand': 0,
        'shots_one_timer': 0, 'shots_tip': 0, 'shots_deflection': 0,
        'shots_wraparound': 0, 'shots_poke': 0, 'shots_bat': 0,
        'goals_wrist': 0, 'goals_one_timer': 0, 'goals_tip': 0, 'goals_backhand': 0,
        'wrist_shot_pct': 0.0, 'one_timer_pct': 0.0,
        'primary_shot_type': 'none', 'shot_type_variety': 0,
    }

# =============================================================================
# PASS TYPE ANALYSIS (NEW)
# =============================================================================

def calculate_pass_type_stats(player_id, game_id, event_players: pd.DataFrame,
                               events: pd.DataFrame) -> dict:
    """Calculate pass breakdown by type."""
    stats = {}
    
    pe = event_players[
        (event_players['game_id'] == game_id) & 
        (event_players['player_id'] == player_id) &
        (event_players['player_role'].astype(str).str.lower() == PRIMARY_PLAYER)
    ]
    
    if len(pe) == 0:
        return _get_empty_pass_type_stats()
    
    player_event_ids = pe['event_id'].unique() if 'event_id' in pe.columns else []
    game_events = events[events['game_id'] == game_id]
    
    player_passes = game_events[
        (game_events['event_id'].isin(player_event_ids)) &
        (game_events['event_type'].astype(str).str.lower() == 'pass')
    ] if len(player_event_ids) > 0 else pd.DataFrame()
    
    if len(player_passes) == 0:
        return _get_empty_pass_type_stats()
    
    def count_pass_type(pattern):
        if 'event_detail_2' not in player_passes.columns:
            return 0
        return int(player_passes['event_detail_2'].astype(str).str.lower().str.contains(pattern, na=False).sum())
    
    stats['passes_forehand'] = count_pass_type(r'forehand')
    stats['passes_backhand'] = count_pass_type(r'backhand')
    stats['passes_stretch'] = count_pass_type(r'stretch')
    stats['passes_bank'] = count_pass_type(r'bank')
    stats['passes_rim'] = count_pass_type(r'rim|wrap')
    stats['passes_drop'] = count_pass_type(r'drop')
    stats['passes_lob'] = count_pass_type(r'lob')
    stats['passes_one_touch'] = count_pass_type(r'onetouch|one_touch')
    
    # Creative passes (high-skill passes)
    stats['creative_passes'] = stats['passes_stretch'] + stats['passes_bank'] + stats['passes_lob']
    
    # Completed vs attempted
    if 'event_successful' in player_passes.columns:
        completed = player_passes[player_passes['event_successful'].astype(str).str.lower().isin(['s', 'true', '1', 'yes'])]
        stats['passes_completed'] = len(completed)
    else:
        completed = player_passes[player_passes['event_detail'].astype(str).str.lower().str.contains('completed', na=False)]
        stats['passes_completed'] = len(completed)
    
    stats['passes_attempted'] = len(player_passes)
    stats['pass_completion_pct'] = round(stats['passes_completed'] / stats['passes_attempted'] * 100, 1) if stats['passes_attempted'] > 0 else 0.0
    
    # Stretch pass success rate
    stretch_passes = player_passes[player_passes['event_detail_2'].astype(str).str.lower().str.contains('stretch', na=False)] if 'event_detail_2' in player_passes.columns else pd.DataFrame()
    if len(stretch_passes) > 0 and 'event_successful' in stretch_passes.columns:
        stretch_completed = len(stretch_passes[stretch_passes['event_successful'].astype(str).str.lower().isin(['s', 'true', '1', 'yes'])])
        stats['stretch_pass_pct'] = round(stretch_completed / len(stretch_passes) * 100, 1)
    else:
        stats['stretch_pass_pct'] = 0.0
    
    # Pass diversity score
    pass_types = [stats['passes_forehand'], stats['passes_backhand'], stats['passes_stretch'],
                  stats['passes_bank'], stats['passes_rim'], stats['passes_drop']]
    stats['pass_type_diversity'] = sum(1 for p in pass_types if p > 0)
    
    return stats

def _get_empty_pass_type_stats():
    return {
        'passes_forehand': 0, 'passes_backhand': 0, 'passes_stretch': 0,
        'passes_bank': 0, 'passes_rim': 0, 'passes_drop': 0, 'passes_lob': 0, 'passes_one_touch': 0,
        'creative_passes': 0, 'passes_completed': 0, 'passes_attempted': 0,
        'pass_completion_pct': 0.0, 'stretch_pass_pct': 0.0, 'pass_type_diversity': 0,
    }

# =============================================================================
# SHOT ASSISTS / PLAYMAKING (NEW)
# =============================================================================

def calculate_playmaking_stats(player_id, game_id, event_players: pd.DataFrame,
                                events: pd.DataFrame) -> dict:
    """Calculate shot assists and playmaking metrics."""
    stats = {}
    
    pe = event_players[
        (event_players['game_id'] == game_id) & 
        (event_players['player_id'] == player_id) &
        (event_players['player_role'].astype(str).str.lower() == PRIMARY_PLAYER)
    ]
    
    if len(pe) == 0:
        return _get_empty_playmaking_stats()
    
    player_event_ids = pe['event_id'].unique() if 'event_id' in pe.columns else []
    game_events = events[events['game_id'] == game_id]
    
    player_events = game_events[game_events['event_id'].isin(player_event_ids)] if len(player_event_ids) > 0 else pd.DataFrame()
    
    if len(player_events) == 0:
        return _get_empty_playmaking_stats()
    
    # Shot assists (passes that led to shots)
    if 'is_shot_assist' in player_events.columns:
        stats['shot_assists'] = int(player_events['is_shot_assist'].sum())
    else:
        stats['shot_assists'] = 0
    
    # Goal-creating actions (passes that led to goals)
    if 'led_to_goal' in player_events.columns:
        stats['goal_creating_actions'] = int(player_events['led_to_goal'].sum())
    else:
        stats['goal_creating_actions'] = 0
    
    # Pre-shot events (is_pre_shot_event)
    if 'is_pre_shot_event' in player_events.columns:
        stats['pre_shot_touches'] = int(player_events['is_pre_shot_event'].sum())
    else:
        stats['pre_shot_touches'] = 0
    
    # Sequence involvement
    if 'sequence_key' in player_events.columns:
        player_sequences = player_events['sequence_key'].dropna().unique()
        all_sequences = game_events['sequence_key'].dropna().unique()
        stats['sequences_involved'] = len(player_sequences)
        stats['sequence_involvement_pct'] = round(len(player_sequences) / len(all_sequences) * 100, 1) if len(all_sequences) > 0 else 0.0
        
        # Sequences that led to SOG
        if 'sequence_has_sog' in player_events.columns:
            sog_sequences = player_events[player_events['sequence_has_sog'] == 1]['sequence_key'].nunique()
            stats['sog_sequences'] = sog_sequences
        else:
            stats['sog_sequences'] = 0
        
        # Sequences that led to goals
        if 'sequence_has_goal' in player_events.columns:
            goal_sequences = player_events[player_events['sequence_has_goal'] == 1]['sequence_key'].nunique()
            stats['goal_sequences'] = goal_sequences
        else:
            stats['goal_sequences'] = 0
    else:
        stats['sequences_involved'] = 0
        stats['sequence_involvement_pct'] = 0.0
        stats['sog_sequences'] = 0
        stats['goal_sequences'] = 0
    
    # Playmaking index (composite)
    stats['playmaking_index'] = round(
        stats['shot_assists'] * 1.0 +
        stats['goal_creating_actions'] * 2.0 +
        stats['pre_shot_touches'] * 0.3 +
        stats['sog_sequences'] * 0.5,
        2
    )
    
    return stats

def _get_empty_playmaking_stats():
    return {
        'shot_assists': 0, 'goal_creating_actions': 0, 'pre_shot_touches': 0,
        'sequences_involved': 0, 'sequence_involvement_pct': 0.0,
        'sog_sequences': 0, 'goal_sequences': 0, 'playmaking_index': 0.0,
    }

# =============================================================================
# PRESSURE STATS (NEW)
# =============================================================================

def calculate_pressure_stats(player_id, game_id, event_players: pd.DataFrame,
                              events: pd.DataFrame) -> dict:
    """Calculate performance under pressure."""
    stats = {}
    
    pe = event_players[
        (event_players['game_id'] == game_id) & 
        (event_players['player_id'] == player_id) &
        (event_players['player_role'].astype(str).str.lower() == PRIMARY_PLAYER)
    ]
    
    if len(pe) == 0:
        return _get_empty_pressure_stats()
    
    player_event_ids = pe['event_id'].unique() if 'event_id' in pe.columns else []
    game_events = events[events['game_id'] == game_id]
    
    player_events = game_events[game_events['event_id'].isin(player_event_ids)] if len(player_event_ids) > 0 else pd.DataFrame()
    
    if len(player_events) == 0 or 'is_pressured' not in player_events.columns:
        return _get_empty_pressure_stats()
    
    # Events under pressure
    pressured = player_events[player_events['is_pressured'] == 1]
    not_pressured = player_events[player_events['is_pressured'] == 0]
    
    stats['plays_under_pressure'] = len(pressured)
    stats['plays_not_pressured'] = len(not_pressured)
    stats['pressure_rate'] = round(len(pressured) / len(player_events) * 100, 1) if len(player_events) > 0 else 0.0
    
    # Success under pressure
    if 'event_successful' in pressured.columns and len(pressured) > 0:
        success_pressured = pressured[pressured['event_successful'].astype(str).str.lower().isin(['s', 'true', '1', 'yes'])]
        stats['pressure_success_count'] = len(success_pressured)
        stats['pressure_success_pct'] = round(len(success_pressured) / len(pressured) * 100, 1)
    else:
        stats['pressure_success_count'] = 0
        stats['pressure_success_pct'] = 0.0
    
    # Success when not pressured (for comparison)
    if 'event_successful' in not_pressured.columns and len(not_pressured) > 0:
        success_not = not_pressured[not_pressured['event_successful'].astype(str).str.lower().isin(['s', 'true', '1', 'yes'])]
        stats['unpressured_success_pct'] = round(len(success_not) / len(not_pressured) * 100, 1)
    else:
        stats['unpressured_success_pct'] = 0.0
    
    # Pressure differential (how much worse under pressure)
    stats['pressure_differential'] = round(stats['pressure_success_pct'] - stats['unpressured_success_pct'], 1)
    
    # Turnovers under pressure
    if 'is_giveaway' in pressured.columns:
        stats['pressure_giveaways'] = int(pressured['is_giveaway'].sum())
    else:
        stats['pressure_giveaways'] = 0
    
    # Poise index (positive = handles pressure well)
    stats['poise_index'] = round(
        stats['pressure_success_pct'] / 100 * 2 - 
        stats['pressure_giveaways'] * 0.1 -
        (100 - stats['pressure_success_pct']) / 100,
        2
    )
    
    return stats

def _get_empty_pressure_stats():
    return {
        'plays_under_pressure': 0, 'plays_not_pressured': 0, 'pressure_rate': 0.0,
        'pressure_success_count': 0, 'pressure_success_pct': 0.0,
        'unpressured_success_pct': 0.0, 'pressure_differential': 0.0,
        'pressure_giveaways': 0, 'poise_index': 0.0,
    }

# =============================================================================
# COMPETITION TIER STATS (NEW)
# =============================================================================

def calculate_competition_tier_stats(player_id, game_id, shift_players: pd.DataFrame) -> dict:
    """Calculate performance by competition quality tier."""
    stats = {}
    
    ps = shift_players[
        (shift_players['game_id'] == game_id) & 
        (shift_players['player_id'] == player_id)
    ] if len(shift_players) > 0 else pd.DataFrame()
    
    if len(ps) == 0 or 'competition_tier_id' not in ps.columns:
        return _get_empty_competition_stats()
    
    tiers = {'TI01': 'elite', 'TI02': 'good', 'TI03': 'avg', 'TI04': 'weak'}
    
    for tier_id, tier_name in tiers.items():
        tier_shifts = ps[ps['competition_tier_id'] == tier_id]
        prefix = f'vs_{tier_name}_'
        
        if len(tier_shifts) > 0:
            stats[f'{prefix}toi'] = int(tier_shifts['shift_duration'].sum()) if 'shift_duration' in tier_shifts.columns else 0
            
            if 'cf' in tier_shifts.columns and 'ca' in tier_shifts.columns:
                cf = tier_shifts['cf'].sum()
                ca = tier_shifts['ca'].sum()
                stats[f'{prefix}cf_pct'] = round(cf / (cf + ca) * 100, 1) if (cf + ca) > 0 else 50.0
            else:
                stats[f'{prefix}cf_pct'] = 50.0
            
            if 'gf' in tier_shifts.columns and 'ga' in tier_shifts.columns:
                stats[f'{prefix}gf'] = int(tier_shifts['gf'].sum())
                stats[f'{prefix}ga'] = int(tier_shifts['ga'].sum())
            else:
                stats[f'{prefix}gf'] = 0
                stats[f'{prefix}ga'] = 0
        else:
            stats[f'{prefix}toi'] = 0
            stats[f'{prefix}cf_pct'] = 50.0
            stats[f'{prefix}gf'] = 0
            stats[f'{prefix}ga'] = 0
    
    # Use existing adjusted stats if available
    if 'cf_pct_adj' in ps.columns:
        stats['cf_pct_adjusted'] = round(ps['cf_pct_adj'].mean(), 1) if 'cf_pct_adj' in ps.columns and pd.notna(ps['cf_pct_adj']).any() else 50.0
    else:
        stats['cf_pct_adjusted'] = 50.0
    
    if 'cf_pct_vs_expected' in ps.columns:
        stats['cf_pct_vs_expected'] = round(ps['cf_pct_vs_expected'].mean(), 1) if 'cf_pct_vs_expected' in ps.columns and pd.notna(ps['cf_pct_vs_expected']).any() else 0.0
    else:
        stats['cf_pct_vs_expected'] = 0.0
    
    return stats

def _get_empty_competition_stats():
    return {
        'vs_elite_toi': 0, 'vs_elite_cf_pct': 50.0, 'vs_elite_gf': 0, 'vs_elite_ga': 0,
        'vs_good_toi': 0, 'vs_good_cf_pct': 50.0, 'vs_good_gf': 0, 'vs_good_ga': 0,
        'vs_avg_toi': 0, 'vs_avg_cf_pct': 50.0, 'vs_avg_gf': 0, 'vs_avg_ga': 0,
        'vs_weak_toi': 0, 'vs_weak_cf_pct': 50.0, 'vs_weak_gf': 0, 'vs_weak_ga': 0,
        'cf_pct_adjusted': 50.0, 'cf_pct_vs_expected': 0.0,
    }

# =============================================================================
# GAME STATE STATS (NEW)
# =============================================================================

def calculate_game_state_stats(player_id, game_id, shift_players: pd.DataFrame,
                                events: pd.DataFrame) -> dict:
    """
    Calculate performance by game state (leading/trailing/tied).
    
    Uses game_state column from fact_shift_players which tracks score at shift start.
    
    FORMULAS:
    - leading_toi: Sum of shift_duration WHERE player is leading (home_leading + away_trailing)
    - trailing_toi: Sum of shift_duration WHERE player is trailing
    - tied_toi: Sum of shift_duration WHERE game_state='tied'
    - close_game_toi: Sum of shift_duration WHERE |score_differential| <= 1
    
    - leading_cf_pct: CF% while leading
    - trailing_cf_pct: CF% while trailing
    - tied_cf_pct: CF% while tied
    - close_game_cf_pct: CF% in close games
    
    - leading_goals: Goals scored while leading
    - trailing_goals: Goals scored while trailing
    - tied_goals: Goals scored while tied
    """
    stats = {}
    
    ps = shift_players[
        (shift_players['game_id'] == game_id) & 
        (shift_players['player_id'] == player_id)
    ] if len(shift_players) > 0 else pd.DataFrame()
    
    if len(ps) == 0 or 'game_state' not in ps.columns:
        return _get_empty_game_state_stats()
    
    # Determine player's venue (home/away)
    player_venue = ps['venue'].iloc[0] if 'venue' in ps.columns and len(ps) > 0 else None
    
    if player_venue is None:
        return _get_empty_game_state_stats()
    
    # Map game_state to player perspective
    # home_leading means home team is winning
    # For away player, home_leading = they are trailing
    def get_player_state(row):
        gs = str(row.get('game_state', 'tied'))
        if gs == 'tied':
            return 'tied'
        elif gs == 'home_leading':
            return 'leading' if row.get('venue') == 'home' else 'trailing'
        elif gs == 'home_trailing':
            return 'trailing' if row.get('venue') == 'home' else 'leading'
        return 'tied'
    
    ps = ps.copy()
    ps['player_state'] = ps.apply(get_player_state, axis=1)
    
    # Calculate TOI by game state
    if 'shift_duration' in ps.columns:
        stats['leading_toi'] = int(ps[ps['player_state'] == 'leading']['shift_duration'].sum())
        stats['trailing_toi'] = int(ps[ps['player_state'] == 'trailing']['shift_duration'].sum())
        stats['tied_toi'] = int(ps[ps['player_state'] == 'tied']['shift_duration'].sum())
        stats['close_game_toi'] = int(ps[ps['is_close_game'] == True]['shift_duration'].sum()) if 'is_close_game' in ps.columns else 0
    else:
        stats['leading_toi'] = stats['trailing_toi'] = stats['tied_toi'] = stats['close_game_toi'] = 0
    
    # Calculate CF% by game state
    def calc_cf_pct(subset):
        if len(subset) == 0 or 'cf' not in subset.columns or 'ca' not in subset.columns:
            return 50.0
        cf = subset['cf'].sum()
        ca = subset['ca'].sum()
        return round(cf / (cf + ca) * 100, 1) if (cf + ca) > 0 else 50.0
    
    stats['leading_cf_pct'] = calc_cf_pct(ps[ps['player_state'] == 'leading'])
    stats['trailing_cf_pct'] = calc_cf_pct(ps[ps['player_state'] == 'trailing'])
    stats['tied_cf_pct'] = calc_cf_pct(ps[ps['player_state'] == 'tied'])
    stats['close_game_cf_pct'] = calc_cf_pct(ps[ps['is_close_game'] == True]) if 'is_close_game' in ps.columns else 50.0
    
    # Calculate goals by game state
    if 'gf' in ps.columns:
        stats['leading_goals'] = int(ps[ps['player_state'] == 'leading']['gf'].sum())
        stats['trailing_goals'] = int(ps[ps['player_state'] == 'trailing']['gf'].sum())
        stats['tied_goals'] = int(ps[ps['player_state'] == 'tied']['gf'].sum())
    else:
        stats['leading_goals'] = stats['trailing_goals'] = stats['tied_goals'] = 0
    
    # DEFENSIVE CLUTCH STATS (P3 when leading = protecting lead)
    # Get P3 shifts when player's team is leading
    p3_shifts = ps[ps['period'] == 3] if 'period' in ps.columns else pd.DataFrame()
    p3_leading = p3_shifts[p3_shifts['player_state'] == 'leading'] if len(p3_shifts) > 0 else pd.DataFrame()
    
    # P3 Leading TOI
    stats['p3_leading_toi'] = int(p3_leading['shift_duration'].sum()) if len(p3_leading) > 0 and 'shift_duration' in p3_leading.columns else 0
    
    # P3 Leading CF/CA (defensive possession when protecting lead)
    if len(p3_leading) > 0 and 'cf' in p3_leading.columns:
        stats['p3_leading_cf'] = int(p3_leading['cf'].sum())
        stats['p3_leading_ca'] = int(p3_leading['ca'].sum())
        total = stats['p3_leading_cf'] + stats['p3_leading_ca']
        stats['p3_leading_cf_pct'] = round(stats['p3_leading_cf'] / total * 100, 1) if total > 0 else 50.0
    else:
        stats['p3_leading_cf'] = stats['p3_leading_ca'] = 0
        stats['p3_leading_cf_pct'] = 50.0
    
    # P3 Leading Goals For/Against (protect lead effectiveness)
    if len(p3_leading) > 0 and 'gf' in p3_leading.columns:
        stats['p3_leading_gf'] = int(p3_leading['gf'].sum())
        stats['p3_leading_ga'] = int(p3_leading['ga'].sum())
    else:
        stats['p3_leading_gf'] = stats['p3_leading_ga'] = 0
    
    # Defensive clutch index: CF% in P3 when leading (higher = better at protecting lead)
    # Positive defensive_clutch_diff means you controlled play while protecting lead
    stats['defensive_clutch_cf_pct'] = stats['p3_leading_cf_pct']
    stats['defensive_clutch_diff'] = round(stats['p3_leading_cf_pct'] - 50.0, 1)  # vs neutral 50%
    
    return stats

def _get_empty_game_state_stats():
    return {
        'leading_toi': 0, 'trailing_toi': 0, 'tied_toi': 0, 'close_game_toi': 0,
        'leading_cf_pct': 50.0, 'trailing_cf_pct': 50.0, 'tied_cf_pct': 50.0, 'close_game_cf_pct': 50.0,
        'leading_goals': 0, 'trailing_goals': 0, 'tied_goals': 0,
        # Defensive clutch (P3 when leading)
        'p3_leading_toi': 0, 'p3_leading_cf': 0, 'p3_leading_ca': 0, 'p3_leading_cf_pct': 50.0,
        'p3_leading_gf': 0, 'p3_leading_ga': 0,
        'defensive_clutch_cf_pct': 50.0, 'defensive_clutch_diff': 0.0,
    }

# =============================================================================
# ORIGINAL V25.1 FUNCTIONS (preserved but condensed)
# =============================================================================

def calculate_period_splits(player_id, game_id, event_players, shift_players, events=None):
    stats = {}
    pe = event_players[(event_players['game_id'] == game_id) & (event_players['player_id'] == player_id)]
    ps = shift_players[(shift_players['game_id'] == game_id) & (shift_players['player_id'] == player_id)] if len(shift_players) > 0 else pd.DataFrame()
    
    for p in [1, 2, 3]:
        prefix = f'p{p}_'
        period_events = pe[pe['period'] == p] if 'period' in pe.columns else pd.DataFrame()
        
        if len(period_events) > 0:
            # Only count where player is event_player_1
            period_primary = period_events[period_events['player_role'].astype(str).str.lower() == PRIMARY_PLAYER]
            
            goals = period_primary[is_goal_scored(period_primary)]
            stats[f'{prefix}goals'] = len(goals)
            
            # Assists via play_detail1
            if 'play_detail1' in period_primary.columns:
                assists = period_primary[period_primary['play_detail1'].astype(str).str.lower().isin([ASSIST_PRIMARY_DETAIL, ASSIST_SECONDARY_DETAIL])]
                stats[f'{prefix}assists'] = len(assists)
            else:
                stats[f'{prefix}assists'] = 0
            
            # Shot attempts (all shots - for Corsi)
            period_shots = period_primary[period_primary['event_type'].astype(str).str.lower() == 'shot']
            stats[f'{prefix}shots'] = len(period_shots)
            
            # SOG (shots on goal - reached net) + goals
            # Main SOG logic: shots containing 'onnet|saved' + goals
            if 'event_detail' in period_shots.columns:
                sog = period_shots[period_shots['event_detail'].astype(str).str.lower().str.contains('onnet|saved', na=False, regex=True)]
                stats[f'{prefix}sog'] = len(sog) + stats[f'{prefix}goals']
            else:
                stats[f'{prefix}sog'] = stats[f'{prefix}goals']
            
            stats[f'{prefix}points'] = stats[f'{prefix}goals'] + stats[f'{prefix}assists']
        else:
            stats[f'{prefix}goals'] = stats[f'{prefix}assists'] = stats[f'{prefix}shots'] = stats[f'{prefix}sog'] = stats[f'{prefix}points'] = 0
        
        if len(ps) > 0 and 'period' in ps.columns:
            stats[f'{prefix}toi_seconds'] = int(ps[ps['period'] == p]['shift_duration'].sum()) if 'shift_duration' in ps.columns else 0
        else:
            stats[f'{prefix}toi_seconds'] = 0
    
    p1p2_ppm = (stats['p1_points'] + stats['p2_points']) / ((stats['p1_toi_seconds'] + stats['p2_toi_seconds']) / 60) if (stats['p1_toi_seconds'] + stats['p2_toi_seconds']) > 0 else 0
    p3_ppm = stats['p3_points'] / (stats['p3_toi_seconds'] / 60) if stats['p3_toi_seconds'] > 0 else 0
    stats['p3_clutch_diff'] = round(p3_ppm - p1p2_ppm, 3)
    return stats

def calculate_danger_zone_stats(player_id, game_id, event_players, events):
    pe = event_players[(event_players['game_id'] == game_id) & (event_players['player_id'] == player_id) & (event_players['player_role'].astype(str).str.lower() == PRIMARY_PLAYER)]
    empty = {'shots_high_danger': 0, 'shots_medium_danger': 0, 'shots_low_danger': 0, 'goals_high_danger': 0, 'goals_medium_danger': 0, 'goals_low_danger': 0, 'scoring_chance_shots': 0, 'scoring_chance_goals': 0, 'scoring_chance_pct': 0.0, 'avg_shot_danger': 0.0, 'high_danger_shot_pct': 0.0, 'low_danger_shot_pct': 0.0}
    
    if len(pe) == 0: return empty
    player_event_ids = pe['event_id'].unique() if 'event_id' in pe.columns else []
    player_events = events[events['event_id'].isin(player_event_ids)] if len(player_event_ids) > 0 else pd.DataFrame()
    if len(player_events) == 0: return empty
    
    shots = player_events[player_events['event_type'].astype(str).str.lower() == 'shot']
    goals = player_events[is_goal_scored(player_events)]
    
    stats = {}
    if 'danger_level' in player_events.columns:
        for level, key in [('high', 'high'), ('low', 'low')]:
            stats[f'shots_{key}_danger'] = len(shots[shots['danger_level'].astype(str).str.lower() == level])
            stats[f'goals_{key}_danger'] = len(goals[goals['danger_level'].astype(str).str.lower() == level]) if 'danger_level' in goals.columns else 0
    else:
        stats['shots_high_danger'] = stats['shots_low_danger'] = stats['goals_high_danger'] = stats['goals_low_danger'] = 0
    
    stats['shots_medium_danger'] = len(shots) - stats['shots_high_danger'] - stats['shots_low_danger']
    stats['goals_medium_danger'] = len(goals) - stats['goals_high_danger'] - stats['goals_low_danger']
    
    if 'is_scoring_chance' in player_events.columns:
        stats['scoring_chance_shots'] = len(shots[shots['is_scoring_chance'] == 1])
        stats['scoring_chance_goals'] = len(goals[goals['is_scoring_chance'] == 1]) if 'is_scoring_chance' in goals.columns else 0
        stats['scoring_chance_pct'] = round(stats['scoring_chance_goals'] / stats['scoring_chance_shots'] * 100, 1) if stats['scoring_chance_shots'] > 0 else 0.0
    else:
        stats['scoring_chance_shots'] = stats['scoring_chance_goals'] = 0
        stats['scoring_chance_pct'] = 0.0
    
    total = len(shots) + len(goals)
    stats['avg_shot_danger'] = round(((stats['shots_high_danger'] + stats['goals_high_danger']) * 3 + (stats['shots_medium_danger'] + stats['goals_medium_danger']) * 2 + (stats['shots_low_danger'] + stats['goals_low_danger'])) / total, 2) if total > 0 else 0.0
    stats['high_danger_shot_pct'] = round(stats['goals_high_danger'] / stats['shots_high_danger'] * 100, 1) if stats['shots_high_danger'] > 0 else 0.0
    stats['low_danger_shot_pct'] = round(stats['goals_low_danger'] / stats['shots_low_danger'] * 100, 1) if stats['shots_low_danger'] > 0 else 0.0
    return stats

def calculate_rush_stats(player_id, game_id, event_players, events):
    pe = event_players[(event_players['game_id'] == game_id) & (event_players['player_id'] == player_id)]
    empty = {
        # Rush involvement - is_rush is now NHL definition (controlled entry + shot ≤7s)
        'rush_shots': 0, 'rush_goals': 0, 'rush_assists': 0, 'rush_points': 0, 'rush_shot_pct': 0.0,
        'breakaway_goals': 0, 'odd_man_rushes': 0, 'rush_xg': 0.0,
        'rush_primary': 0, 'rush_support': 0, 'rush_involvement': 0, 'rush_involvement_pct': 0.0,
        'rush_primary_def': 0, 'rush_def_support': 0, 'rush_def_involvement': 0, 'rush_def_involvement_pct': 0.0,
        # Offensive success metrics (combined)
        'rush_off_success': 0, 'rush_off_success_pct': 0.0,
        'rush_off_shot_generated': 0, 'rush_off_shot_generated_pct': 0.0,
        'rush_off_goal_generated': 0, 'rush_off_goal_generated_pct': 0.0,
        'rush_off_immediate_shot': 0,
        # Offensive success by role
        'rush_primary_success': 0, 'rush_primary_success_pct': 0.0,
        'rush_primary_shot': 0, 'rush_primary_shot_pct': 0.0,
        'rush_primary_goal': 0, 'rush_primary_goal_pct': 0.0,
        'rush_support_success': 0, 'rush_support_success_pct': 0.0,
        'rush_support_shot': 0, 'rush_support_shot_pct': 0.0,
        'rush_support_goal': 0, 'rush_support_goal_pct': 0.0,
        # Defensive success metrics (combined)
        'rush_def_success': 0, 'rush_def_success_pct': 0.0,
        'rush_def_stop': 0, 'rush_def_stop_pct': 0.0,
        'rush_def_ga': 0,
        # Defensive success by role
        'rush_primary_def_success': 0, 'rush_primary_def_success_pct': 0.0,
        'rush_primary_def_stop': 0, 'rush_primary_def_stop_pct': 0.0,
        'rush_primary_def_ga': 0,
        'rush_support_def_success': 0, 'rush_support_def_success_pct': 0.0,
        'rush_support_def_stop': 0, 'rush_support_def_stop_pct': 0.0,
        'rush_support_def_ga': 0,
        # CALCULATED rush (systematic: zone entry → shot ≤10s, ≤5 events, any entry type)
        'rush_calc_off': 0, 'rush_calc_def': 0,
        'rush_calc_off_goal': 0, 'rush_calc_def_ga': 0,
    }
    if len(pe) == 0: return empty
    
    rush_col = 'is_rush' if 'is_rush' in events.columns else ('is_rush_calculated' if 'is_rush_calculated' in events.columns else None)
    if not rush_col: return empty
    
    game_events = events[events['game_id'] == game_id]
    rush_events = game_events[game_events[rush_col] == 1]
    if len(rush_events) == 0: return empty
    
    rush_event_ids = rush_events['event_id'].unique()
    pe_rush = pe[pe['event_id'].isin(rush_event_ids)]
    
    # Role breakdown on rush events
    pe_rush_primary = pe_rush[pe_rush['player_role'].astype(str).str.lower() == 'event_player_1']
    pe_rush_support = pe_rush[pe_rush['player_role'].astype(str).str.lower().str.match(r'event_player_[2-6]')]
    pe_rush_primary_def = pe_rush[pe_rush['player_role'].astype(str).str.lower() == 'opp_player_1']
    pe_rush_def_support = pe_rush[pe_rush['player_role'].astype(str).str.lower().str.match(r'opp_player_[2-6]')]
    
    stats = {}
    
    # Offensive rush stats (when player is event_player_1)
    # Rush events are zone entries - the shot/goal info is in time_to_next_sog and next_sog_result columns
    primary_rush_event_ids = pe_rush_primary['event_id'].unique() if len(pe_rush_primary) > 0 else []
    player_rush_events = rush_events[rush_events['event_id'].isin(primary_rush_event_ids)]
    
    # rush_shots = rush entries that led to a shot (time_to_next_sog is populated)
    stats['rush_shots'] = int(player_rush_events['time_to_next_sog'].notna().sum()) if 'time_to_next_sog' in player_rush_events.columns else 0
    # rush_goals = rush entries where the resulting shot was a goal
    stats['rush_goals'] = int((player_rush_events['next_sog_result'].astype(str).str.lower() == 'goal').sum()) if 'next_sog_result' in player_rush_events.columns else 0
    
    # Rush assists: play_detail1 contains assist on rush events where player is event_player_1
    pe_with_assist = pe_rush_primary[pe_rush_primary['play_detail1'].astype(str).str.lower().isin([ASSIST_PRIMARY_DETAIL, ASSIST_SECONDARY_DETAIL])] if 'play_detail1' in pe_rush_primary.columns else pd.DataFrame()
    stats['rush_assists'] = len(pe_with_assist)
    stats['rush_points'] = stats['rush_goals'] + stats['rush_assists']
    stats['rush_shot_pct'] = round(stats['rush_goals'] / stats['rush_shots'] * 100, 1) if stats['rush_shots'] > 0 else 0.0
    
    # Breakaway goals: rush goals where event_detail_2 contains 'breakaway'
    if len(player_rush_events) > 0 and 'event_detail_2' in player_rush_events.columns:
        event_detail_2_lower = player_rush_events['event_detail_2'].astype(str).str.lower()
        breakaway_mask = event_detail_2_lower.str.contains('breakaway', na=False)
        goal_mask = (player_rush_events['next_sog_result'].astype(str).str.lower() == 'goal') if 'next_sog_result' in player_rush_events.columns else pd.Series([False] * len(player_rush_events))
        stats['breakaway_goals'] = int((breakaway_mask & goal_mask).sum())
    else:
        stats['breakaway_goals'] = 0
    
    # Odd-man rushes: count rush events where event_detail_2 contains 'oddman' or 'odd_man'
    if len(player_rush_events) > 0 and 'event_detail_2' in player_rush_events.columns:
        event_detail_2_lower = player_rush_events['event_detail_2'].astype(str).str.lower()
        odd_man_mask = event_detail_2_lower.str.contains('oddman|odd_man', na=False, regex=True)
        stats['odd_man_rushes'] = int(odd_man_mask.sum())
    else:
        stats['odd_man_rushes'] = 0
    
    # Rush xG: Calculate xG for rush entries that led to shots
    # Use simplified approach: calculate xG based on rush entry context (entry is already rush, so use rush modifier)
    rush_xg_total = 0.0
    if len(player_rush_events) > 0 and 'time_to_next_sog' in player_rush_events.columns:
        # Get rush entries that led to shots
        rush_with_shots = player_rush_events[player_rush_events['time_to_next_sog'].notna()].copy()
        if len(rush_with_shots) > 0:
            # VECTORIZED: Calculate xG for all rush entries at once
            # Use default danger level for rush entries (medium danger typical for rushes)
            danger_map = rush_with_shots['danger_level'].astype(str).str.lower().map(
                lambda x: XG_BASE_RATES.get(x, XG_BASE_RATES['default'])
            ).fillna(XG_BASE_RATES['default'])
            xg = danger_map * XG_MODIFIERS['rush']  # Rush modifier (1.3x)
            
            # Apply breakaway modifier if present - VECTORIZED
            event_detail_2_col = rush_with_shots['event_detail_2'].astype(str).str.lower() if 'event_detail_2' in rush_with_shots.columns else pd.Series('', index=rush_with_shots.index)
            breakaway_mask = event_detail_2_col.str.contains('breakaway', na=False)
            xg[breakaway_mask] = xg[breakaway_mask] * XG_MODIFIERS['breakaway']  # Breakaway modifier (2.5x)
            
            rush_xg_total = xg.clip(upper=0.95).sum()
    stats['rush_xg'] = round(rush_xg_total, 2)
    
    # Rush involvement breakdown
    stats['rush_primary'] = len(pe_rush_primary)
    stats['rush_support'] = len(pe_rush_support)
    stats['rush_involvement'] = stats['rush_primary'] + stats['rush_support']
    stats['rush_involvement_pct'] = round(stats['rush_involvement'] / len(rush_events) * 100, 1) if len(rush_events) > 0 else 0.0
    
    # Defensive rush involvement breakdown
    stats['rush_primary_def'] = len(pe_rush_primary_def)
    stats['rush_def_support'] = len(pe_rush_def_support)
    stats['rush_def_involvement'] = stats['rush_primary_def'] + stats['rush_def_support']
    stats['rush_def_involvement_pct'] = round(stats['rush_def_involvement'] / len(rush_events) * 100, 1) if len(rush_events) > 0 else 0.0
    
    # Helper function for success metrics
    def calc_success_metrics(event_ids, prefix):
        if len(event_ids) == 0:
            return {f'{prefix}_success': 0, f'{prefix}_success_pct': 0.0, f'{prefix}_shot': 0, 
                    f'{prefix}_shot_pct': 0.0, f'{prefix}_goal': 0, f'{prefix}_goal_pct': 0.0}
        role_rush_events = rush_events[rush_events['event_id'].isin(event_ids)]
        if len(role_rush_events) == 0:
            return {f'{prefix}_success': 0, f'{prefix}_success_pct': 0.0, f'{prefix}_shot': 0, 
                    f'{prefix}_shot_pct': 0.0, f'{prefix}_goal': 0, f'{prefix}_goal_pct': 0.0}
        quick_shot = (role_rush_events['time_to_next_sog'].notna()) & (role_rush_events['time_to_next_sog'] <= 10)
        success = (role_rush_events['event_successful'] == True) | quick_shot
        quick_goal = (role_rush_events['time_to_next_goal'].notna()) & (role_rush_events['time_to_next_goal'] <= 15)
        n = len(role_rush_events)
        return {
            f'{prefix}_success': int(success.sum()), f'{prefix}_success_pct': round(success.sum() / n * 100, 1),
            f'{prefix}_shot': int(quick_shot.sum()), f'{prefix}_shot_pct': round(quick_shot.sum() / n * 100, 1),
            f'{prefix}_goal': int(quick_goal.sum()), f'{prefix}_goal_pct': round(quick_goal.sum() / n * 100, 1),
        }
    
    def calc_def_metrics(event_ids, prefix):
        if len(event_ids) == 0:
            return {f'{prefix}_success': 0, f'{prefix}_success_pct': 0.0, f'{prefix}_stop': 0, 
                    f'{prefix}_stop_pct': 0.0, f'{prefix}_ga': 0}
        role_rush_events = rush_events[rush_events['event_id'].isin(event_ids)]
        if len(role_rush_events) == 0:
            return {f'{prefix}_success': 0, f'{prefix}_success_pct': 0.0, f'{prefix}_stop': 0, 
                    f'{prefix}_stop_pct': 0.0, f'{prefix}_ga': 0}
        # Defensive success = no goal allowed (shot saved/missed)
        no_goal = (role_rush_events['next_sog_result'].astype(str).str.lower() != 'goal') if 'next_sog_result' in role_rush_events.columns else pd.Series([True] * len(role_rush_events))
        goal_allowed = (role_rush_events['next_sog_result'].astype(str).str.lower() == 'goal') if 'next_sog_result' in role_rush_events.columns else pd.Series([False] * len(role_rush_events))
        n = len(role_rush_events)
        return {
            f'{prefix}_success': int(no_goal.sum()), f'{prefix}_success_pct': round(no_goal.sum() / n * 100, 1),
            f'{prefix}_stop': int(no_goal.sum()), f'{prefix}_stop_pct': round(no_goal.sum() / n * 100, 1),
            f'{prefix}_ga': int(goal_allowed.sum()),
        }
    
    # ===== OFFENSIVE SUCCESS METRICS =====
    # Combined offense (all event_player roles)
    pe_rush_offense = pe_rush[pe_rush['player_role'].astype(str).str.lower().str.startswith('event_player')]
    offense_rush_event_ids = pe_rush_offense['event_id'].unique() if len(pe_rush_offense) > 0 else []
    offense_rush_events = rush_events[rush_events['event_id'].isin(offense_rush_event_ids)]
    
    if len(offense_rush_events) > 0:
        quick_shot = (offense_rush_events['time_to_next_sog'].notna()) & (offense_rush_events['time_to_next_sog'] <= 10)
        success = (offense_rush_events['event_successful'] == True) | quick_shot
        stats['rush_off_success'] = int(success.sum())
        stats['rush_off_success_pct'] = round(stats['rush_off_success'] / len(offense_rush_events) * 100, 1)
        stats['rush_off_shot_generated'] = int(quick_shot.sum())
        stats['rush_off_shot_generated_pct'] = round(stats['rush_off_shot_generated'] / len(offense_rush_events) * 100, 1)
        quick_goal = (offense_rush_events['time_to_next_goal'].notna()) & (offense_rush_events['time_to_next_goal'] <= 15)
        stats['rush_off_goal_generated'] = int(quick_goal.sum())
        stats['rush_off_goal_generated_pct'] = round(stats['rush_off_goal_generated'] / len(offense_rush_events) * 100, 1)
        if 'time_from_entry_to_shot' in offense_rush_events.columns:
            stats['rush_off_immediate_shot'] = int(offense_rush_events['time_from_entry_to_shot'].notna().sum())
    
    # Primary rusher success (event_player_1)
    stats.update(calc_success_metrics(pe_rush_primary['event_id'].unique() if len(pe_rush_primary) > 0 else [], 'rush_primary'))
    
    # Support rusher success (event_player_2-6)
    stats.update(calc_success_metrics(pe_rush_support['event_id'].unique() if len(pe_rush_support) > 0 else [], 'rush_support'))
    
    # ===== DEFENSIVE SUCCESS METRICS =====
    # Combined defense (all opp_player roles)
    # NOTE: is_rush=1 means shot ALREADY happened within 7s, so "prevent shot" is not possible
    # Defensive success = no goal allowed (shot was saved/missed)
    pe_rush_defense = pe_rush[pe_rush['player_role'].astype(str).str.lower().str.startswith('opp_player')]
    defense_rush_event_ids = pe_rush_defense['event_id'].unique() if len(pe_rush_defense) > 0 else []
    defense_rush_events = rush_events[rush_events['event_id'].isin(defense_rush_event_ids)]
    
    if len(defense_rush_events) > 0:
        # Defensive success = rush where no goal resulted (shot saved/missed)
        no_goal = (defense_rush_events['next_sog_result'].astype(str).str.lower() != 'goal') if 'next_sog_result' in defense_rush_events.columns else pd.Series([True] * len(defense_rush_events))
        stats['rush_def_success'] = int(no_goal.sum())
        stats['rush_def_success_pct'] = round(stats['rush_def_success'] / len(defense_rush_events) * 100, 1)
        # rush_def_stop = same as success (stopped the scoring chance)
        stats['rush_def_stop'] = int(no_goal.sum())
        stats['rush_def_stop_pct'] = round(stats['rush_def_stop'] / len(defense_rush_events) * 100, 1)
        # Goals allowed on rushes
        goal_allowed = (defense_rush_events['next_sog_result'].astype(str).str.lower() == 'goal') if 'next_sog_result' in defense_rush_events.columns else pd.Series([False] * len(defense_rush_events))
        stats['rush_def_ga'] = int(goal_allowed.sum())
    
    # Primary defender success (opp_player_1)
    stats.update(calc_def_metrics(pe_rush_primary_def['event_id'].unique() if len(pe_rush_primary_def) > 0 else [], 'rush_primary_def'))
    
    # Support defender success (opp_player_2-6)
    stats.update(calc_def_metrics(pe_rush_def_support['event_id'].unique() if len(pe_rush_def_support) > 0 else [], 'rush_support_def'))
    
    # ===== CALCULATED RUSH METRICS (systematic: zone entry → shot ≤5s, ≤5 events) =====
    calc_rush_col = 'is_rush_calculated' if 'is_rush_calculated' in events.columns else None
    if calc_rush_col:
        calc_rush_events = game_events[game_events[calc_rush_col] == 1]
        calc_rush_event_ids = calc_rush_events['event_id'].unique()
        pe_calc_rush = pe[pe['event_id'].isin(calc_rush_event_ids)]
        
        # Offensive involvement on calculated rushes
        pe_calc_offense = pe_calc_rush[pe_calc_rush['player_role'].astype(str).str.lower().str.startswith('event_player')]
        pe_calc_defense = pe_calc_rush[pe_calc_rush['player_role'].astype(str).str.lower().str.startswith('opp_player')]
        
        stats['rush_calc_off'] = len(pe_calc_offense['event_id'].unique()) if len(pe_calc_offense) > 0 else 0
        stats['rush_calc_def'] = len(pe_calc_defense['event_id'].unique()) if len(pe_calc_defense) > 0 else 0
        
        # Goals on calculated rushes (time_to_next_goal ≤15s)
        if stats['rush_calc_off'] > 0:
            off_event_ids = pe_calc_offense['event_id'].unique()
            off_events = calc_rush_events[calc_rush_events['event_id'].isin(off_event_ids)]
            quick_goal = (off_events['time_to_next_goal'].notna()) & (off_events['time_to_next_goal'] <= 15)
            stats['rush_calc_off_goal'] = int(quick_goal.sum())
        else:
            stats['rush_calc_off_goal'] = 0
        
        if stats['rush_calc_def'] > 0:
            def_event_ids = pe_calc_defense['event_id'].unique()
            def_events = calc_rush_events[calc_rush_events['event_id'].isin(def_event_ids)]
            quick_goal_allowed = (def_events['time_to_next_goal'].notna()) & (def_events['time_to_next_goal'] <= 15)
            stats['rush_calc_def_ga'] = int(quick_goal_allowed.sum())
        else:
            stats['rush_calc_def_ga'] = 0
    else:
        stats['rush_calc_off'] = 0
        stats['rush_calc_def'] = 0
        stats['rush_calc_off_goal'] = 0
        stats['rush_calc_def_ga'] = 0
    
    # NOTE: Main rush stats (rush_involvement, rush_off_goal_generated, etc.) now use is_rush
    # which is the NHL true rush definition (controlled entry + shot ≤7s)
    # rush_calc_* columns capture any quick attack (≤10s, ≤5 events, any entry type)
    
    return stats

def _get_empty_micro_stats():
    """Return empty dict with all micro stat keys (including s/u variants)."""
    empty = {}
    
    # List of all base micro stat names
    base_stats = [
        # Offensive
        'dekes', 'drives_middle', 'drives_wide', 'drives_corner', 'drives_net', 'drives_total',
        'cutbacks', 'delays', 'fakes', 'open_ice_dekes',
        'crash_net', 'screens', 'net_front', 'box_out',
        'give_and_go', 'second_touch', 'cycles', 'regroup', 'reverse', 'wheel', 'surf', 'quick_up', 'chip',
        'passes_cross_ice', 'passes_stretch', 'passes_breakout', 'passes_rim', 'passes_bank',
        'passes_royal_road', 'passes_slot', 'passes_behind_net', 'passes_for_tip',
        'passes_deflected', 'passes_intercepted', 'passes_missed',
        'shots_one_timer', 'shots_snap', 'shots_wrist', 'shots_slap', 'shots_tip',
        'shots_deflection', 'shots_wrap_around', 'shots_point', 'shots_attempted',
        'rushes', 'breakaways', 'odd_man_rushes',
        'controlled_entries', 'dump_ins', 'failed_entries', 'keep_ins', 'failed_keep_ins',
        # Defensive
        'poke_checks', 'stick_checks', 'zone_ent_denials', 'zone_exit_denials',
        'backchecks', 'forechecks', 'contain', 'gap_control', 'man_on_man',
        'force_wide', 'forced_dumpins', 'forced_turnovers', 'forced_missed_pass',
        'forced_missed_shot', 'forced_lost_possession', 'in_shot_pass_lane',
        'clearing_attempts', 'penalty_kill_clears',
        # Transition
        'breakouts', 'zone_exits', 'failed_exits', 'attempted_breakouts', 'attempted_clear',
        # Puck battles
        'loose_puck_wins', 'loose_puck_losses', 'puck_recoveries', 'puck_retrieval_attempts',
        'board_battles_won', 'board_battles_lost', 'puck_battles', 'puck_battles_total', 'puck_battles_lost_total',
        # Pressure
        'pressure', 'separate_from_puck', 'lost_puck', 'misplayed_puck',
        # Aggregates
        'micro_off_zone', 'micro_def_zone', 'micro_neutral_zone',
        'forecheck_intensity', 'backcheck_intensity',
        'controlled_exits', 'controlled_entries', 'transition_quality',
        'plays_successful', 'plays_unsuccessful', 'play_success_rate',
    ]
    
    # Initialize all stats with 0 or 0.0
    for stat in base_stats:
        empty[stat] = 0
        empty[f'{stat}_successful'] = 0
        empty[f'{stat}_unsuccessful'] = 0
        empty[f'{stat}_success_rate'] = 0.0
    
    # Additional calculated stats
    empty['board_battle_win_pct'] = 0.0
    empty['puck_battle_win_pct'] = 0.0
    empty['drives_total_success_rate'] = 0.0
    
    return empty


def calculate_micro_stats(player_id, game_id, event_players, events):
    """
    Calculate comprehensive micro stats from play_detail1/2 AND event_detail/event_detail_2.
    
    EXPANDED v31.0:
    - Checks BOTH play_detail columns (play_detail1, play_detail_2) AND event_detail columns (event_detail, event_detail_2)
    - Only counts events where player is event_player_1
    - Adds successful/unsuccessful variants for each stat
    - Significantly expanded list of microstats
    
    CRITICAL: Uses DISTINCT counting by linked_event_index_flag to avoid double-counting.
    Each event should only be counted once even if pattern appears in multiple columns.
    """
    pe = event_players[(event_players['game_id'] == game_id) & (event_players['player_id'] == player_id) & (event_players['player_role'].astype(str).str.lower() == PRIMARY_PLAYER)]
    
    # Initialize empty dict with all possible micro stats (including s/u variants)
    empty = {}
    # Will populate this below with all stats
    
    if len(pe) == 0: 
        # Return empty dict with all required keys
        return _get_empty_micro_stats()
    
    player_event_ids = pe['event_id'].unique() if 'event_id' in pe.columns else []
    game_events = events[events['game_id'] == game_id]
    player_events = game_events[game_events['event_id'].isin(player_event_ids)] if len(player_event_ids) > 0 else pd.DataFrame()
    if len(player_events) == 0: 
        return _get_empty_micro_stats()
    
    def count_distinct_with_success(pattern, exclude_pattern=None):
        """
        Count DISTINCT events matching pattern in play_detail1, play_detail_2, event_detail, OR event_detail_2.
        Returns: (total_count, successful_count, unsuccessful_count)
        Uses linked_event_index_flag for deduplication if available.
        """
        matching_events = pd.DataFrame()
        
        # Check all 4 columns: play_detail1, play_detail_2, event_detail, event_detail_2
        detail_cols = ['play_detail1', 'play_detail_2', 'event_detail', 'event_detail_2']
        
        for col in detail_cols:
            if col not in player_events.columns:
                continue
            
            # Find rows matching the pattern
            mask = player_events[col].astype(str).str.lower().str.contains(pattern, na=False, regex=True)
            
            # Exclude defensive/negative variants if specified
            if exclude_pattern:
                exclude_mask = player_events[col].astype(str).str.lower().str.contains(exclude_pattern, na=False, regex=True)
                mask = mask & ~exclude_mask
            
            matches = player_events[mask]
            if len(matches) > 0:
                matching_events = pd.concat([matching_events, matches])
        
        if len(matching_events) == 0:
            return (0, 0, 0)
        
        # Deduplicate: use linked_event_index_flag if available, otherwise event_id
        if 'linked_event_index_flag' in matching_events.columns:
            # Split into linked and unlinked
            linked = matching_events[matching_events['linked_event_index_flag'].notna()]
            unlinked = matching_events[matching_events['linked_event_index_flag'].isna()]
            
            # Get distinct linked events (by linked_event_index_flag) and unlinked (by event_id)
            distinct_linked_flags = []
            distinct_unlinked_ids = []
            
            if len(linked) > 0:
                distinct_linked_flags = linked['linked_event_index_flag'].unique().tolist()
                linked_events = linked[linked['linked_event_index_flag'].isin(distinct_linked_flags)].drop_duplicates(subset='linked_event_index_flag')
            else:
                linked_events = pd.DataFrame()
            
            if len(unlinked) > 0:
                distinct_unlinked_ids = unlinked['event_id'].unique().tolist()
                unlinked_events = unlinked[unlinked['event_id'].isin(distinct_unlinked_ids)].drop_duplicates(subset='event_id')
            else:
                unlinked_events = pd.DataFrame()
            
            # Combine for success counting
            all_distinct = pd.concat([linked_events, unlinked_events]) if len(linked_events) > 0 or len(unlinked_events) > 0 else pd.DataFrame()
            distinct_count = len(distinct_linked_flags) + len(distinct_unlinked_ids)
        else:
            # Fallback: dedupe by event_id
            all_distinct = matching_events.drop_duplicates(subset='event_id')
            distinct_count = all_distinct['event_id'].nunique() if len(all_distinct) > 0 else 0
        
        # Count successful/unsuccessful
        if len(all_distinct) > 0 and 'play_detail_successful' in all_distinct.columns:
            successful = int((all_distinct['play_detail_successful'].astype(str).str.lower() == 's').sum())
            unsuccessful = int((all_distinct['play_detail_successful'].astype(str).str.lower() == 'u').sum())
        elif len(all_distinct) > 0 and 'event_successful' in all_distinct.columns:
            # Fallback to event_successful if play_detail_successful not available
            successful = int((all_distinct['event_successful'].astype(str).str.lower().isin(['s', '1', 'true', 'yes'])).sum())
            unsuccessful = int((all_distinct['event_successful'].astype(str).str.lower().isin(['u', '0', 'false', 'no'])).sum())
        else:
            successful = 0
            unsuccessful = 0
        
        return (distinct_count, successful, unsuccessful)
    
    # Helper to add stat with s/u breakdown
    def add_stat_with_success(base_name, pattern, exclude_pattern=None):
        """Add a stat with total, successful, and unsuccessful counts."""
        total, successful, unsuccessful = count_distinct_with_success(pattern, exclude_pattern)
        stats[f'{base_name}'] = total
        stats[f'{base_name}_successful'] = successful
        stats[f'{base_name}_unsuccessful'] = unsuccessful
        if total > 0:
            stats[f'{base_name}_success_rate'] = round(successful / total * 100, 1)
        else:
            stats[f'{base_name}_success_rate'] = 0.0
    
    stats = {}
    
    # ============================================================================
    # OFFENSIVE MICRO STATS (with s/u breakdown)
    # ============================================================================
    
    # Puck skills
    add_stat_with_success('dekes', r'deke', exclude_pattern=r'beatdeke|stoppeddeke')
    add_stat_with_success('drives_middle', r'drivemiddle|drivenetmiddle')
    add_stat_with_success('drives_wide', r'drivewide')
    add_stat_with_success('drives_corner', r'drivecorner')
    add_stat_with_success('drives_net', r'drivenet')
    add_stat_with_success('cutbacks', r'cutback')
    add_stat_with_success('delays', r'delay')
    add_stat_with_success('fakes', r'fake|fakeshot')
    add_stat_with_success('open_ice_dekes', r'openicedeke|open.?ice.?deke')
    
    # Net presence
    add_stat_with_success('crash_net', r'crashnet|crash.?net')
    add_stat_with_success('screens', r'screen')
    add_stat_with_success('net_front', r'netfront|front.?net')
    add_stat_with_success('box_out', r'boxout|box.?out')
    
    # Passing plays
    add_stat_with_success('give_and_go', r'giveandgo|give.?and.?go')
    add_stat_with_success('second_touch', r'secondtouch|second.?touch')
    add_stat_with_success('cycles', r'cycle')
    add_stat_with_success('regroup', r'regroup')
    add_stat_with_success('reverse', r'reverse')
    add_stat_with_success('wheel', r'wheel')
    add_stat_with_success('surf', r'surf')
    add_stat_with_success('quick_up', r'quickup|quick.?up')
    add_stat_with_success('chip', r'chip')
    
    # Pass types
    add_stat_with_success('passes_cross_ice', r'cross.?ice|crossice')
    add_stat_with_success('passes_stretch', r'stretch')
    add_stat_with_success('passes_breakout', r'breakout')
    add_stat_with_success('passes_rim', r'rim|rimaround|rim.?around')
    add_stat_with_success('passes_bank', r'bank|bankpass')
    add_stat_with_success('passes_royal_road', r'royalroad|royal.?road')
    add_stat_with_success('passes_slot', r'slot|slotpass')
    add_stat_with_success('passes_behind_net', r'behindnet|behind.?net')
    add_stat_with_success('passes_for_tip', r'passfortip|pass.?for.?tip')
    add_stat_with_success('passes_deflected', r'passdeflected|pass.?deflected')
    add_stat_with_success('passes_intercepted', r'passintercepted|pass.?intercepted')
    add_stat_with_success('passes_missed', r'passmissed|receiver.?missed')
    
    # Shot types
    add_stat_with_success('shots_one_timer', r'one.?timer|onetimer|one.?time')
    add_stat_with_success('shots_snap', r'snap|snapshot')
    add_stat_with_success('shots_wrist', r'wrist|wristshot')
    add_stat_with_success('shots_slap', r'slap|slapshot')
    add_stat_with_success('shots_tip', r'tip|tipped|shot.?tip')
    add_stat_with_success('shots_deflection', r'deflect|deflection|deflectedshot')
    add_stat_with_success('shots_wrap_around', r'wrap|wraparound')
    add_stat_with_success('shots_point', r'pointshot|point.?shot')
    add_stat_with_success('shots_attempted', r'attemptedshot')
    
    # Rush plays
    add_stat_with_success('rushes', r'rush|endtoendrush')
    add_stat_with_success('breakaways', r'breakaway')
    add_stat_with_success('odd_man_rushes', r'oddman|odd.?man')
    
    # Zone entries
    add_stat_with_success('controlled_entries', r'controlledentry|entry.*controlled|carry.*entry')
    add_stat_with_success('dump_ins', r'dumpin|dumpchase|dump.?and.?chase')
    add_stat_with_success('failed_entries', r'entry.*fail|failedentry|entryfailed')
    add_stat_with_success('keep_ins', r'keepin|zone.?keepin|zonekeepin')
    add_stat_with_success('failed_keep_ins', r'keepin.*fail|keepinfailed')
    
    # ============================================================================
    # DEFENSIVE MICRO STATS (with s/u breakdown)
    # ============================================================================
    
    add_stat_with_success('poke_checks', r'pokecheck|poke.?check')
    add_stat_with_success('stick_checks', r'stickcheck|stick.?check')
    add_stat_with_success('zone_ent_denials', r'zoneentrydenial|zone.?entry.?denial|cededzoneentry')
    add_stat_with_success('zone_exit_denials', r'zoneexitdenial|zone.?exit.?denial|cededzoneexit')
    add_stat_with_success('backchecks', r'backcheck|back.?check')
    add_stat_with_success('forechecks', r'forecheck|fore.?check')
    add_stat_with_success('contain', r'contain')
    add_stat_with_success('gap_control', r'gapcontrol|gap.?control')
    add_stat_with_success('man_on_man', r'manonman|man.?on.?man')
    add_stat_with_success('force_wide', r'forcewide|force.?wide')
    add_stat_with_success('forced_dumpins', r'forceddumpin|forced.?dumpin')
    add_stat_with_success('forced_turnovers', r'forcedturnover|forced.?turnover')
    add_stat_with_success('forced_missed_pass', r'forcedmissedpass|forced.?missed.?pass')
    add_stat_with_success('forced_missed_shot', r'forcedmissedshot|forced.?missed.?shot')
    add_stat_with_success('forced_lost_possession', r'forcedlostpossession|forced.?lost.?possession')
    add_stat_with_success('in_shot_pass_lane', r'inshotpasslane|in.?shot.?pass.?lane')
    add_stat_with_success('clearing_attempts', r'clearingattempt|clearing.?attempt')
    add_stat_with_success('penalty_kill_clears', r'penaltykillclear|penalty.?kill.?clear')
    
    # ============================================================================
    # TRANSITION MICRO STATS (with s/u breakdown)
    # ============================================================================
    
    add_stat_with_success('breakouts', r'breakout')
    add_stat_with_success('zone_exits', r'zoneexit')
    add_stat_with_success('failed_exits', r'exit.*fail|failedexit|exitfailed')
    add_stat_with_success('attempted_breakouts', r'attemptedbreakout|attempted.?breakout')
    add_stat_with_success('attempted_clear', r'attemptedbreakoutclear|attempted.?clear')
    
    # ============================================================================
    # PUCK BATTLE MICRO STATS (with s/u breakdown)
    # ============================================================================
    
    add_stat_with_success('loose_puck_wins', r'loosepuck.*won|battlewon|loosepuckbattlewon')
    add_stat_with_success('loose_puck_losses', r'loosepuck.*lost|battlelost|loosepuckbattlelost')
    add_stat_with_success('puck_recoveries', r'puckrecovery|puckretrieval|puck.?recovery')
    add_stat_with_success('puck_retrieval_attempts', r'puckrecoveryretreivalattemptedclear|retrieval.*attempt')
    add_stat_with_success('board_battles_won', r'board.*won|battle.*won')
    add_stat_with_success('board_battles_lost', r'board.*lost|battle.*lost')
    add_stat_with_success('puck_battles', r'loosepuckbattle|boardbattle')
    
    # ============================================================================
    # PRESSURE/INTENSITY MICRO STATS (with s/u breakdown)
    # ============================================================================
    
    add_stat_with_success('pressure', r'pressure|under.?pressure')
    add_stat_with_success('separate_from_puck', r'separatefrompuck|seperatefrompuck')
    add_stat_with_success('lost_puck', r'lostpuck')
    add_stat_with_success('misplayed_puck', r'misplayedpuck|misplay')
    
    # ============================================================================
    # AGGREGATES AND CALCULATED STATS
    # ============================================================================
    
    stats['drives_total'] = stats.get('drives_middle', 0) + stats.get('drives_wide', 0) + stats.get('drives_corner', 0) + stats.get('drives_net', 0)
    stats['drives_total_successful'] = stats.get('drives_middle_successful', 0) + stats.get('drives_wide_successful', 0) + stats.get('drives_corner_successful', 0) + stats.get('drives_net_successful', 0)
    stats['drives_total_unsuccessful'] = stats.get('drives_middle_unsuccessful', 0) + stats.get('drives_wide_unsuccessful', 0) + stats.get('drives_corner_unsuccessful', 0) + stats.get('drives_net_unsuccessful', 0)
    if stats['drives_total'] > 0:
        stats['drives_total_success_rate'] = round(stats['drives_total_successful'] / stats['drives_total'] * 100, 1)
    else:
        stats['drives_total_success_rate'] = 0.0
    
    stats['puck_battles_total'] = stats.get('loose_puck_wins', 0) + stats.get('puck_recoveries', 0) + stats.get('board_battles_won', 0)
    stats['puck_battles_lost_total'] = stats.get('loose_puck_losses', 0) + stats.get('board_battles_lost', 0)
    total_battles = stats['puck_battles_total'] + stats['puck_battles_lost_total']
    stats['puck_battle_win_pct'] = round(stats['puck_battles_total'] / total_battles * 100, 1) if total_battles > 0 else 0.0
    
    total_board_battles = stats.get('board_battles_won', 0) + stats.get('board_battles_lost', 0)
    stats['board_battle_win_pct'] = round(stats.get('board_battles_won', 0) / total_board_battles * 100, 1) if total_board_battles > 0 else 0.0
    
    # ============================================================================
    # ZONE-SPECIFIC MICRO STATS (counts from all 4 columns by zone)
    # ============================================================================
    if 'rink_zone' in player_events.columns or 'event_team_zone' in player_events.columns:
        zone_col = 'rink_zone' if 'rink_zone' in player_events.columns else 'event_team_zone'
        
        off_zone_events = player_events[player_events[zone_col].astype(str).str.lower().str.contains(r'^o|offensive|oz', na=False, regex=True)]
        def_zone_events = player_events[player_events[zone_col].astype(str).str.lower().str.contains(r'^d|defensive|dz', na=False, regex=True)]
        neutral_zone_events = player_events[player_events[zone_col].astype(str).str.lower().str.contains(r'^n|neutral|nz', na=False, regex=True)]
        
        # Count micro plays in each zone using all 4 detail columns
        detail_cols = ['play_detail1', 'play_detail_2', 'event_detail', 'event_detail_2']
        micro_patterns = r'deke|drive|cycle|cutback|delay|crashnet|screen|giveandgo'
        
        for zone_name, zone_df in [('micro_off_zone', off_zone_events), ('micro_def_zone', def_zone_events), ('micro_neutral_zone', neutral_zone_events)]:
            count = 0
            for col in detail_cols:
                if col in zone_df.columns:
                    matches = zone_df[zone_df[col].astype(str).str.lower().str.contains(micro_patterns, na=False, regex=True)]
                    count += matches['event_id'].nunique()
            stats[zone_name] = count
    
    # ============================================================================
    # INTENSITY METRICS
    # ============================================================================
    stats['forecheck_intensity'] = stats.get('forechecks', 0)
    stats['backcheck_intensity'] = stats.get('backchecks', 0)
    
    # ============================================================================
    # TRANSITION QUALITY (will be populated from zone stats in advanced_micro_stats)
    # ============================================================================
    stats['controlled_exits'] = stats.get('controlled_exits', 0)  # Will be updated from zone_stats
    stats['controlled_entries'] = stats.get('controlled_entries', 0)  # Will be updated from zone_stats
    stats['transition_quality'] = 0.0  # Calculated in advanced_micro_stats
    
    # ============================================================================
    # OVERALL PLAY SUCCESS TRACKING
    # ============================================================================
    if 'play_detail_successful' in player_events.columns or 'event_successful' in player_events.columns:
        success_col = 'play_detail_successful' if 'play_detail_successful' in player_events.columns else 'event_successful'
        stats['plays_successful'] = int((player_events[success_col].astype(str).str.lower().isin(['s', '1', 'true', 'yes'])).sum())
        stats['plays_unsuccessful'] = int((player_events[success_col].astype(str).str.lower().isin(['u', '0', 'false', 'no'])).sum())
        total = stats['plays_successful'] + stats['plays_unsuccessful']
        stats['play_success_rate'] = round(stats['plays_successful'] / total * 100, 1) if total > 0 else 0.0
    else:
        stats['plays_successful'] = stats['plays_unsuccessful'] = 0
        stats['play_success_rate'] = 0.0
    
    return stats

def calculate_advanced_micro_stats(player_id, game_id, event_players, events, micro_stats=None, zone_stats=None):
    """
    Calculate advanced composite metrics from micro stats and other data.
    
    Creates composite indices that combine multiple micro stats:
    - Possession Quality Index: Measures quality of puck possession plays
    - Transition Efficiency: Measures effectiveness in zone transitions
    - Pressure Index: Measures performance under pressure
    - Offensive Creativity Index: Measures variety and effectiveness of offensive plays
    - Defensive Activity Index: Measures defensive engagement
    - Playmaking Quality: Measures quality of passing and playmaking
    
    Args:
        player_id: Player ID
        game_id: Game ID
        event_players: Event players DataFrame
        events: Events DataFrame
        micro_stats: Optional pre-calculated micro stats dict (if None, will calculate)
        zone_stats: Optional zone entry/exit stats dict
    
    Returns:
        Dict with advanced composite metrics
    """
    # If micro_stats not provided, calculate them
    if micro_stats is None:
        micro_stats = calculate_micro_stats(player_id, game_id, event_players, events)
    
    # Get zone stats if not provided
    if zone_stats is None:
        zone_entry_types = load_table('dim_zone_entry_type')
        zone_exit_types = load_table('dim_zone_exit_type')
        zone_stats = calculate_zone_entry_exit_stats(player_id, game_id, event_players, zone_entry_types, zone_exit_types, events)
    
    # Ensure zone_stats has all expected keys with defaults
    if not isinstance(zone_stats, dict):
        zone_stats = {}
    zone_stats = {
        'zone_entries': zone_stats.get('zone_entries', 0),
        'zone_exits': zone_stats.get('zone_exits', 0),
        'zone_ent_controlled': zone_stats.get('zone_ent_controlled', 0),
        'zone_ext_controlled': zone_stats.get('zone_ext_controlled', 0),
        **zone_stats  # Keep any other keys
    }
    
    # Get TOI for rate calculations
    # Try to get from shift stats, but handle gracefully if not available
    shifts = load_table('fact_shifts')
    shift_players = load_table('fact_shift_players')
    toi_minutes = 0.1  # Default to avoid division by zero
    
    if len(shifts) > 0 and len(shift_players) > 0:
        try:
            shift_stats = calculate_player_shift_stats(player_id, game_id, shifts, shift_players)
            toi_minutes = shift_stats.get('toi_minutes', 0.1)
        except:
            # If calculation fails, use default
            toi_minutes = 0.1
    
    stats = {}
    
    # 1. POSSESSION QUALITY INDEX
    # Combines: cycles, give_and_go, second_touch, controlled entries, controlled exits
    possession_plays = (
        micro_stats.get('cycles', 0) +
        micro_stats.get('give_and_go', 0) +
        micro_stats.get('second_touch', 0) +
        zone_stats.get('zone_ent_controlled', 0) +
        zone_stats.get('zone_ext_controlled', 0)
    )
    possession_success = micro_stats.get('plays_successful', 0)
    total_plays = possession_success + micro_stats.get('plays_unsuccessful', 0)
    possession_success_rate = (possession_success / total_plays * 100) if total_plays > 0 else 0
    
    # Normalize to 0-100 scale (weighted by success rate)
    stats['possession_quality_index'] = round(
        (possession_plays / max(toi_minutes, 0.1) * 10) * (possession_success_rate / 100), 1
    ) if possession_plays > 0 else 0.0
    
    # 2. TRANSITION EFFICIENCY
    # Combines: controlled entries, controlled exits, breakouts, dump_ins
    controlled_transitions = (
        zone_stats.get('zone_ent_controlled', 0) +
        zone_stats.get('zone_ext_controlled', 0) +
        micro_stats.get('breakouts', 0)
    )
    total_transitions = (
        zone_stats.get('zone_entries', 0) +
        zone_stats.get('zone_exits', 0) +
        micro_stats.get('dump_ins', 0) +
        micro_stats.get('breakouts', 0)
    )
    stats['transition_efficiency'] = round(
        (controlled_transitions / total_transitions * 100) if total_transitions > 0 else 0.0, 1
    )
    stats['transition_efficiency_rate'] = round(
        controlled_transitions / max(toi_minutes, 0.1) * 60, 1
    )
    
    # 3. PRESSURE INDEX
    # Combines: pressure plays, pressure success rate, forecheck/backcheck intensity
    pressure_plays = micro_stats.get('pressure_plays', 0)
    pressure_success_rate = micro_stats.get('pressure_success_rate', 0)
    defensive_pressure = (
        micro_stats.get('forechecks', 0) +
        micro_stats.get('backchecks', 0) +
        micro_stats.get('zone_ent_denials', 0)
    )
    
    # Weighted index: pressure success + defensive engagement
    stats['pressure_index'] = round(
        (pressure_success_rate * 0.6) + (min(defensive_pressure / max(toi_minutes, 0.1) * 5, 40) * 0.4), 1
    )
    
    # 4. OFFENSIVE CREATIVITY INDEX
    # Combines: variety of offensive plays (dekes, drives, cutbacks, delays, etc.)
    creative_plays = (
        micro_stats.get('dekes', 0) +
        micro_stats.get('drives_total', 0) +
        micro_stats.get('cutbacks', 0) +
        micro_stats.get('delays', 0) +
        micro_stats.get('give_and_go', 0) +
        micro_stats.get('passes_royal_road', 0) +
        micro_stats.get('passes_cross_ice', 0)
    )
    creative_success = micro_stats.get('plays_successful', 0)
    
    # Variety score (unique play types) + success rate
    unique_play_types = sum([
        1 if micro_stats.get('dekes', 0) > 0 else 0,
        1 if micro_stats.get('drives_total', 0) > 0 else 0,
        1 if micro_stats.get('cutbacks', 0) > 0 else 0,
        1 if micro_stats.get('delays', 0) > 0 else 0,
        1 if micro_stats.get('give_and_go', 0) > 0 else 0,
        1 if micro_stats.get('passes_royal_road', 0) > 0 else 0,
        1 if micro_stats.get('passes_cross_ice', 0) > 0 else 0,
    ])
    
    stats['offensive_creativity_index'] = round(
        (unique_play_types * 10) + (creative_success / max(toi_minutes, 0.1) * 2), 1
    )
    
    # 5. DEFENSIVE ACTIVITY INDEX
    # Combines: defensive micro stats (poke checks, stick checks, denials, backchecks, forechecks)
    defensive_actions = (
        micro_stats.get('poke_checks', 0) +
        micro_stats.get('stick_checks', 0) +
        micro_stats.get('zone_ent_denials', 0) +
        micro_stats.get('backchecks', 0) +
        micro_stats.get('forechecks', 0)
    )
    stats['defensive_activity_index'] = round(
        defensive_actions / max(toi_minutes, 0.1) * 60, 1
    )
    
    # 6. PLAYMAKING QUALITY
    # Combines: pass types, shot assists, give_and_go
    playmaking_plays = (
        micro_stats.get('passes_royal_road', 0) +
        micro_stats.get('passes_cross_ice', 0) +
        micro_stats.get('passes_slot', 0) +
        micro_stats.get('give_and_go', 0)
    )
    
    # Get shot assists from event stats if available
    pe = event_players[(event_players['game_id'] == game_id) & (event_players['player_id'] == player_id)]
    shot_assists = 0
    if len(pe) > 0 and 'play_detail1' in pe.columns:
        shot_assists = len(pe[pe['play_detail1'].astype(str).str.lower().str.contains(r'shot.?assist|assist.*shot', na=False, regex=True)])
    
    stats['playmaking_quality'] = round(
        (playmaking_plays + shot_assists) / max(toi_minutes, 0.1) * 60, 1
    )
    
    # 7. NET FRONT PRESENCE
    # Combines: crash_net, screens, tips
    net_front_plays = (
        micro_stats.get('crash_net', 0) +
        micro_stats.get('screens', 0) +
        micro_stats.get('shots_tip', 0) +
        micro_stats.get('shots_deflection', 0)
    )
    stats['net_front_presence'] = round(
        net_front_plays / max(toi_minutes, 0.1) * 60, 1
    )
    
    # 8. PUCK BATTLE EFFICIENCY
    # Combines: puck battle wins vs losses
    puck_battles_won = (
        micro_stats.get('loose_puck_wins', 0) +
        micro_stats.get('board_battles_won', 0) +
        micro_stats.get('puck_recoveries', 0)
    )
    puck_battles_total = (
        puck_battles_won +
        micro_stats.get('board_battles_lost', 0)
    )
    stats['puck_battle_win_pct'] = round(
        (puck_battles_won / puck_battles_total * 100) if puck_battles_total > 0 else 0.0, 1
    )
    stats['puck_battles_per_60'] = round(
        puck_battles_total / max(toi_minutes, 0.1) * 60, 1
    )
    
    return stats

def apply_flurry_adjustment_to_shots(shot_data: list) -> dict:
    """
    Apply probabilistic flurry adjustment to xG values.
    
    Groups shots into sequences (within 3 seconds) and applies
    the formula: P(AtLeastOneGoal) = 1 - ∏(1 - xG_i)
    
    Args:
        shot_data: List of dicts with keys: 'time', 'xg_value'
    
    Returns:
        Dict with: xg_raw, xg_flurry_adjusted, xg_flurry_adjustment, shot_sequences_count
    """
    if len(shot_data) == 0:
        return {'xg_raw': 0.0, 'xg_flurry_adjusted': 0.0, 'xg_flurry_adjustment': 0.0, 'shot_sequences_count': 0}
    
    # Sort by time
    shot_data = sorted(shot_data, key=lambda x: x.get('time', 0))
    
    # Group into sequences (shots within 3 seconds)
    sequences = []
    current_sequence = []
    
    for shot in shot_data:
        if len(current_sequence) == 0:
            current_sequence.append(shot)
        else:
            last_shot_time = current_sequence[-1].get('time', 0)
            time_diff = shot.get('time', 0) - last_shot_time
            
            # Within 3 seconds = same sequence
            if time_diff <= 3.0:
                current_sequence.append(shot)
            else:
                # Start new sequence
                sequences.append(current_sequence)
                current_sequence = [shot]
    
    if len(current_sequence) > 0:
        sequences.append(current_sequence)
    
    # Calculate adjusted xG for each sequence
    xg_raw = sum(s.get('xg_value', 0) for s in shot_data)
    xg_adjusted = 0.0
    
    for sequence in sequences:
        if len(sequence) == 1:
            # Single shot: no adjustment needed
            xg_adjusted += sequence[0].get('xg_value', 0)
        else:
            # Multiple shots: apply flurry adjustment
            xg_values = [s.get('xg_value', 0) for s in sequence]
            prob_no_goal = 1.0
            for xg in xg_values:
                prob_no_goal *= (1.0 - xg)
            xg_flurry = 1.0 - prob_no_goal
            xg_adjusted += min(xg_flurry, 0.99)
    
    return {
        'xg_raw': round(xg_raw, 3),
        'xg_flurry_adjusted': round(xg_adjusted, 3),
        'xg_flurry_adjustment': round(xg_raw - xg_adjusted, 3),
        'shot_sequences_count': len(sequences)
    }

def calculate_xg_stats(player_id, game_id, event_players, events):
    pe = event_players[(event_players['game_id'] == game_id) & (event_players['player_id'] == player_id)]
    empty = {'xg_for': 0.0, 'xg_raw': 0.0, 'xg_flurry_adjustment': 0.0, 'shot_sequences_count': 0, 'goals_actual': 0, 'goals_above_expected': 0.0, 'xg_per_shot': 0.0, 'shots_for_xg': 0, 'finishing_skill': 0.0}
    if len(pe) == 0: return empty
    
    pe_primary = pe[pe['player_role'].astype(str).str.lower() == PRIMARY_PLAYER]
    player_event_ids = pe_primary['event_id'].unique() if 'event_id' in pe_primary.columns else []
    game_events = events[events['game_id'] == game_id]
    player_shots = game_events[(game_events['event_id'].isin(player_event_ids)) & (game_events['event_type'].astype(str).str.lower().isin(['shot', 'goal']))] if len(player_event_ids) > 0 else pd.DataFrame()
    if len(player_shots) == 0: return empty
    
    # Calculate raw xG for each shot (with shot type modifiers)
    # VECTORIZED: Calculate xG for all shots at once
    if len(player_shots) == 0:
        goals_total = 0
        shot_data = []
    else:
        # Count goals
        goals_total = 0
        if 'is_goal' in player_shots.columns:
            goals_total = player_shots['is_goal'].sum()
        elif 'event_type' in player_shots.columns and 'event_detail' in player_shots.columns:
            goals_total = (
                (player_shots['event_type'].astype(str).str.lower() == 'goal') &
                (player_shots['event_detail'].astype(str).str.lower().str.contains('goal_scored', na=False))
            ).sum()
        
        # Map danger levels to base xG rates
        danger_map = player_shots['danger_level'].astype(str).str.lower().map(
            lambda x: XG_BASE_RATES.get(x, XG_BASE_RATES['default'])
        ).fillna(XG_BASE_RATES['default'])
        
        # Apply rush modifier
        rush_multiplier = player_shots['is_rush'].fillna(0).replace({1: XG_MODIFIERS['rush'], 0: 1.0})
        xg_base = danger_map * rush_multiplier
        
        # Apply shot type modifier (from event_detail_2) - VECTORIZED
        shot_type_modifier = pd.Series(1.0, index=player_shots.index)
        event_detail_2_col = player_shots['event_detail_2'].astype(str).str.lower() if 'event_detail_2' in player_shots.columns else pd.Series('', index=player_shots.index)
        for shot_type, modifier in SHOT_TYPE_XG_MODIFIERS.items():
            mask = event_detail_2_col.str.contains(shot_type.lower(), na=False)
            shot_type_modifier[mask] = modifier
        
        xg = xg_base * shot_type_modifier
        xg = xg.clip(upper=0.95)  # Cap at 0.95
        
        # Build shot_data list
        shot_time_col = player_shots.get('time_start_total_seconds', pd.Series(0, index=player_shots.index))
        shot_data = [
            {'time': float(time), 'xg_value': float(xg_val)}
            for time, xg_val in zip(shot_time_col.fillna(0), xg)
        ]
    
    # Apply flurry adjustment
    flurry_result = apply_flurry_adjustment_to_shots(shot_data)
    
    return {
        'xg_raw': flurry_result['xg_raw'],
        'xg_for': flurry_result['xg_flurry_adjusted'],  # Keep existing name (now flurry-adjusted)
        'xg_flurry_adjustment': flurry_result['xg_flurry_adjustment'],
        'shot_sequences_count': flurry_result['shot_sequences_count'],
        'goals_actual': goals_total,
        'goals_above_expected': round(goals_total - flurry_result['xg_flurry_adjusted'], 2),
        'xg_per_shot': round(flurry_result['xg_flurry_adjusted'] / len(player_shots), 3) if len(player_shots) > 0 else 0.0,
        'shots_for_xg': len(player_shots),
        'finishing_skill': round(goals_total / flurry_result['xg_flurry_adjusted'], 2) if flurry_result['xg_flurry_adjusted'] > 0 else 0.0,
    }

def calculate_war_stats(stats):
    off_gar = stats.get('goals', 0) * GAR_WEIGHTS['goals'] + stats.get('primary_assists', 0) * GAR_WEIGHTS['primary_assists'] + stats.get('secondary_assists', 0) * GAR_WEIGHTS['secondary_assists'] + stats.get('sog', 0) * GAR_WEIGHTS['shots_generated'] + stats.get('xg_for', 0) * GAR_WEIGHTS['xg_generated'] + stats.get('shot_assists', 0) * GAR_WEIGHTS['shot_assists']
    def_gar = stats.get('takeaways', 0) * GAR_WEIGHTS['takeaways'] + stats.get('blocks', 0) * GAR_WEIGHTS['blocked_shots'] + stats.get('zone_ext_controlled', 0) * GAR_WEIGHTS['defensive_zone_exits']
    poss_gar = (stats.get('cf_pct', 50.0) - 50.0) / 100 * GAR_WEIGHTS['cf_above_avg'] * stats.get('toi_seconds', 0) / 3600 * 60
    trans_gar = stats.get('zone_ent_controlled', 0) * GAR_WEIGHTS['zone_entry_value']
    poise_gar = stats.get('pressure_success_count', 0) * GAR_WEIGHTS['pressure_success']
    total = off_gar + def_gar + poss_gar + trans_gar + poise_gar
    return {'gar_offense': round(off_gar, 2), 'gar_defense': round(def_gar, 2), 'gar_possession': round(poss_gar, 2), 'gar_transition': round(trans_gar, 2), 'gar_poise': round(poise_gar, 2), 'gar_total': round(total, 2), 'war': round(total / GOALS_PER_WIN, 2), 'war_pace': round(total / GOALS_PER_WIN * GAMES_PER_SEASON, 2)}

def calculate_game_score(stats):
    """
    Calculate game score with offensive/defensive breakdown and calculated rating.
    
    FORMULAS (documented for transparency):
    
    OFFENSIVE COMPONENTS:
    - gs_scoring = goals * 1.0 + primary_assists * 0.8 + secondary_assists * 0.5
    - gs_shots = sog * 0.1 + shots_high_danger * 0.15
    - gs_playmaking = zone_ent_controlled * 0.08 + second_touch * 0.02 + shot_assists * 0.15
    
    DEFENSIVE COMPONENTS:
    - gs_defense = takeaways * 0.15 + blocks * 0.08 + poke_checks * 0.05
    - gs_hustle = backchecks * 0.1 + forechecks * 0.08 + puck_battles_total * 0.03
    
    NEUTRAL COMPONENTS:
    - gs_faceoffs = (fo_wins - fo_losses) * 0.03
    - gs_poise = poise_index * 0.2
    - gs_penalties = giveaways * -0.08
    
    AGGREGATES:
    - offensive_game_score = gs_scoring + gs_shots + gs_playmaking
    - defensive_game_score = gs_defense + gs_hustle - (giveaways * 0.08)
    - game_score_raw = all components summed
    - game_score = 2.0 + game_score_raw (baseline shift for 2-10 scale)
    
    CALCULATED RATING (2-6 scale):
    Based on game_score, maps performance to a 2-6 rating:
    - game_score < 2.5 → rating 2
    - game_score 2.5-3.5 → rating 3
    - game_score 3.5-5.0 → rating 4
    - game_score 5.0-7.0 → rating 5
    - game_score > 7.0 → rating 6
    """
    # Offensive components
    scoring = stats.get('goals', 0) * 1.0 + stats.get('primary_assists', 0) * 0.8 + stats.get('secondary_assists', 0) * 0.5
    shots = stats.get('sog', 0) * 0.1 + stats.get('shots_high_danger', 0) * 0.15
    playmaking = stats.get('zone_ent_controlled', 0) * 0.08 + stats.get('second_touch', 0) * 0.02 + stats.get('shot_assists', 0) * 0.15
    
    # Defensive components
    defense = stats.get('takeaways', 0) * 0.15 + stats.get('blocks', 0) * 0.08 + stats.get('poke_checks', 0) * 0.05
    hustle = stats.get('backchecks', 0) * 0.1 + stats.get('forechecks', 0) * 0.08 + stats.get('puck_battles_total', 0) * 0.03
    
    # Neutral components
    faceoffs = (stats.get('fo_wins', 0) - stats.get('fo_losses', 0)) * 0.03 if (stats.get('fo_wins', 0) + stats.get('fo_losses', 0)) > 0 else 0
    poise = stats.get('poise_index', 0) * 0.2
    penalties = stats.get('giveaways', 0) * -0.08
    
    # Aggregate scores
    offensive_gs = scoring + shots + playmaking
    defensive_gs = defense + hustle - (stats.get('giveaways', 0) * 0.08)  # Giveaways hurt defense
    
    raw = scoring + shots + playmaking + defense + faceoffs + hustle + poise + penalties
    game_score = 2.0 + raw
    toi = stats.get('toi_seconds', 0)
    
    # Calculated rating (2-6 scale based on game_score)
    # These thresholds map game_score to expected rating level
    if game_score < 2.5:
        calculated_rating = 2.0
    elif game_score < 3.5:
        # Linear interpolation between 2-3
        calculated_rating = 2.0 + (game_score - 2.5) / 1.0
    elif game_score < 5.0:
        # Linear interpolation between 3-4
        calculated_rating = 3.0 + (game_score - 3.5) / 1.5
    elif game_score < 7.0:
        # Linear interpolation between 4-5
        calculated_rating = 4.0 + (game_score - 5.0) / 2.0
    else:
        # Linear interpolation between 5-6
        calculated_rating = 5.0 + min((game_score - 7.0) / 3.0, 1.0)
    
    # Cap at 2-6 range
    calculated_rating = max(2.0, min(6.0, calculated_rating))
    
    return {
        'game_score_raw': round(raw, 2),
        'game_score': round(game_score, 2),
        'game_score_per_60': round(game_score * 3600 / toi, 2) if toi > 0 else 0.0,
        'gs_scoring': round(scoring, 2),
        'gs_shots': round(shots, 2),
        'gs_playmaking': round(playmaking, 2),
        'gs_defense': round(defense, 2),
        'gs_hustle': round(hustle, 2),
        'offensive_game_score': round(offensive_gs, 2),
        'defensive_game_score': round(defensive_gs, 2),
        'calculated_rating': round(calculated_rating, 1),
    }

def calculate_performance_vs_rating(stats, player_rating=None):
    """
    Compare player's performance to their rating.
    
    FORMULAS:
    - expected_game_score: Maps player rating to expected game score using RATING_GAME_SCORE_MAP
    - performance_index = (actual_game_score / expected_game_score) * 100
    - adjusted_rating: What rating did they play like? (from calculate_adjusted_rating)
    - rating_delta = adjusted_rating - actual_rating (positive = played above rating)
    - calculated_rating: Direct 2-6 scale from game_score (from calculate_game_score)
    - rating_differential = calculated_rating - player_rating (positive = outperformed)
    
    PERFORMANCE TIERS:
    - Elite: performance_index >= 130
    - Above Expected: 110-130
    - As Expected: 90-110
    - Below Expected: 70-90
    - Struggling: < 70
    """
    rating = player_rating if player_rating and not pd.isna(player_rating) and player_rating > 0 else stats.get('player_rating', 4.0)
    if rating == 0: rating = 4.0
    
    expected_gs = RATING_GAME_SCORE_MAP.get(int(round(rating)), 4.7)
    actual_gs = stats.get('game_score', 2.0)
    perf_idx = round(actual_gs / expected_gs * 100, 1) if expected_gs > 0 else 100.0
    
    # Adjusted rating - what rating did they play like? (legacy method)
    adjusted_rating = calculate_adjusted_rating(actual_gs)
    rating_delta = round(adjusted_rating - rating, 1)
    
    # NEW: calculated_rating comparison
    calculated_rating = stats.get('calculated_rating', 4.0)
    rating_differential = round(calculated_rating - rating, 1)
    
    if perf_idx >= 130: tier = 'Elite'
    elif perf_idx >= 110: tier = 'Above Expected'
    elif perf_idx >= 90: tier = 'As Expected'
    elif perf_idx >= 70: tier = 'Below Expected'
    else: tier = 'Struggling'
    
    qoc = stats.get('qoc_rating', 4.0)
    adj_factor = 1.0 + (qoc - rating) * 0.1
    
    return {
        'skill_rating': round(rating, 1),
        'expected_game_score': round(expected_gs, 2),
        'game_score_vs_expected': round(actual_gs - expected_gs, 2),
        'performance_index': perf_idx,
        'performance_tier': tier,
        'adjusted_rating': adjusted_rating,
        'rating_delta': rating_delta,  # positive = played above rating (legacy)
        'rating_vs_competition': round(rating - qoc, 2),
        'adjusted_performance_index': round(perf_idx * adj_factor, 1),
        'rating_differential': rating_differential,  # NEW: calculated_rating - player_rating
    }

def calculate_rate_stats(stats):
    toi = stats.get('toi_seconds', 0)
    if toi > 60:
        m = 3600 / toi
        for col, src in [('goals_per_60', 'goals'), ('assists_per_60', 'assists'), ('points_per_60', 'points'), ('sog_per_60', 'sog'), ('xg_per_60', 'xg_for'), ('shot_assists_per_60', 'shot_assists')]:
            stats[col] = round(stats.get(src, 0) * m, 2)
    else:
        for col in ['goals_per_60', 'assists_per_60', 'points_per_60', 'sog_per_60', 'xg_per_60', 'shot_assists_per_60']:
            stats[col] = 0.0
    return stats

def calculate_relative_stats(stats):
    cf, ff = stats.get('cf_pct', 50.0), stats.get('ff_pct', 50.0)
    gf, ga = stats.get('plus_total', 0), stats.get('minus_total', 0)
    gf_pct = gf / (gf + ga) * 100 if (gf + ga) > 0 else 50.0
    return {'cf_pct_rel': round(cf - 50, 1), 'ff_pct_rel': round(ff - 50, 1), 'gf_pct': round(gf_pct, 1), 'gf_pct_rel': round(gf_pct - 50, 1)}

def calculate_ratings_adjusted_stats(player_id, game_id, shift_players, stats):
    """
    Calculate ratings-adjusted stats (goals_adj, points_adj, xg_adj).
    
    Adjusts player production metrics based on quality of competition (opp_avg_rating).
    Uses opp_multiplier = opp_avg_rating / 4.0 (where 4.0 is league average).
    
    FORMULAS:
    - goals_adj = goals * (4.0 / opp_avg_rating) - normalizes to league average competition
    - points_adj = points * (4.0 / opp_avg_rating)
    - xg_adj = xg_for * (4.0 / opp_avg_rating)
    
    This answers: "How many goals/points/xG would this player have against average competition?"
    """
    ps = shift_players[
        (shift_players['game_id'] == game_id) & 
        (shift_players['player_id'] == player_id)
    ] if len(shift_players) > 0 else pd.DataFrame()
    
    empty = {
        'goals_adj': 0.0, 'points_adj': 0.0, 'xg_adj': 0.0,
        'avg_opp_rating': 4.0, 'adj_multiplier': 1.0
    }
    
    if len(ps) == 0 or 'opp_avg_rating' not in ps.columns:
        return empty
    
    # Calculate weighted average opp_avg_rating (weighted by shift_duration)
    if 'shift_duration' in ps.columns:
        weighted_sum = (ps['opp_avg_rating'].fillna(4.0) * ps['shift_duration'].fillna(0)).sum()
        total_toi = ps['shift_duration'].fillna(0).sum()
        avg_opp_rating = weighted_sum / total_toi if total_toi > 0 else 4.0
    else:
        avg_opp_rating = ps['opp_avg_rating'].fillna(4.0).mean()
    
    # Adjustment multiplier: normalize to league average (4.0)
    adj_multiplier = 4.0 / avg_opp_rating if avg_opp_rating > 0 else 1.0
    
    # Get base stats
    goals = stats.get('goals', 0)
    points = stats.get('points', 0)
    xg_for = stats.get('xg_for', 0.0)
    
    return {
        'goals_adj': round(goals * adj_multiplier, 2),
        'points_adj': round(points * adj_multiplier, 2),
        'xg_adj': round(xg_for * adj_multiplier, 2),
        'avg_opp_rating': round(avg_opp_rating, 2),
        'adj_multiplier': round(adj_multiplier, 3)
    }

def calculate_advanced_shift_stats(player_id, game_id, shift_players):
    ps = shift_players[(shift_players['game_id'] == game_id) & (shift_players['player_id'] == player_id)] if len(shift_players) > 0 else pd.DataFrame()
    empty = {'fenwick_for': 0, 'fenwick_against': 0, 'ff_pct': 50.0, 'on_ice_sh_pct': 0.0, 'on_ice_sv_pct': 100.0, 'pdo': 100.0, 'qoc_rating': 4.0, 'qot_rating': 4.0, 'zone_starts_oz': 0, 'zone_starts_nz': 0, 'zone_starts_dz': 0, 'zone_starts_oz_pct': 0.0, 'zone_starts_dz_pct': 0.0, 'plus_total': 0, 'minus_total': 0, 'plus_minus_total': 0, 'scoring_chances_for': 0, 'scoring_chances_against': 0, 'sc_pct': 50.0, 'high_danger_for': 0, 'high_danger_against': 0, 'hd_pct': 50.0}
    if len(ps) == 0: return empty
    
    stats = {}
    # Fenwick
    if 'ff' in ps.columns:
        stats['fenwick_for'], stats['fenwick_against'] = int(ps['ff'].sum()), int(ps['fa'].sum())
        total = stats['fenwick_for'] + stats['fenwick_against']
        stats['ff_pct'] = round(stats['fenwick_for'] / total * 100, 1) if total > 0 else 50.0
    else:
        stats['fenwick_for'] = stats['fenwick_against'] = 0
        stats['ff_pct'] = 50.0
    
    # PDO
    gf, ga = ps['gf'].sum() if 'gf' in ps.columns else 0, ps['ga'].sum() if 'ga' in ps.columns else 0
    sf, sa = ps['sf'].sum() if 'sf' in ps.columns else 0, ps['sa'].sum() if 'sa' in ps.columns else 0
    stats['on_ice_sh_pct'] = round(gf / sf * 100, 1) if sf > 0 else 0.0
    stats['on_ice_sv_pct'] = round((sa - ga) / sa * 100, 1) if sa > 0 else 100.0
    stats['pdo'] = round(stats['on_ice_sh_pct'] + stats['on_ice_sv_pct'], 1)
    
    # QoC/QoT
    for col in ['qoc_rating', 'qot_rating']:
        if col in ps.columns and 'shift_duration' in ps.columns:
            dur = ps['shift_duration'].fillna(0)
            stats[col] = round((ps[col].fillna(4.0) * dur).sum() / dur.sum(), 2) if dur.sum() > 0 else 4.0
        else:
            stats[col] = 4.0
    
    # Zone starts
    if 'start_zone' in ps.columns:
        zc = ps['start_zone'].value_counts()
        stats['zone_starts_oz'], stats['zone_starts_nz'], stats['zone_starts_dz'] = int(zc.get('Offensive', 0)), int(zc.get('Neutral', 0)), int(zc.get('Defensive', 0))
        total = stats['zone_starts_oz'] + stats['zone_starts_nz'] + stats['zone_starts_dz']
        stats['zone_starts_oz_pct'] = round(stats['zone_starts_oz'] / total * 100, 1) if total > 0 else 0.0
        stats['zone_starts_dz_pct'] = round(stats['zone_starts_dz'] / total * 100, 1) if total > 0 else 0.0
    else:
        stats['zone_starts_oz'] = stats['zone_starts_nz'] = stats['zone_starts_dz'] = 0
        stats['zone_starts_oz_pct'] = stats['zone_starts_dz_pct'] = 0.0
    
    stats['plus_total'], stats['minus_total'] = int(gf), int(ga)
    stats['plus_minus_total'] = stats['plus_total'] - stats['minus_total']
    
    for cols, keys in [(('scf', 'sca'), ('scoring_chances_for', 'scoring_chances_against', 'sc_pct')), (('hdf', 'hda'), ('high_danger_for', 'high_danger_against', 'hd_pct'))]:
        if cols[0] in ps.columns:
            stats[keys[0]], stats[keys[1]] = int(ps[cols[0]].sum()), int(ps[cols[1]].sum())
            total = stats[keys[0]] + stats[keys[1]]
            stats[keys[2]] = round(stats[keys[0]] / total * 100, 1) if total > 0 else 50.0
        else:
            stats[keys[0]] = stats[keys[1]] = 0
            stats[keys[2]] = 50.0
    return stats

def calculate_zone_entry_exit_stats(player_id, game_id, event_players, zone_entry_types, zone_exit_types, events=None):
    # ONLY count for event_player_1 - they get credit for the zone entry/exit
    pe = event_players[(event_players['game_id'] == game_id) & (event_players['player_id'] == player_id)]
    pe_primary = pe[pe['player_role'].astype(str).str.lower() == PRIMARY_PLAYER]
    
    empty = {
        'zone_ent_total': 0, 'zone_ent_controlled': 0, 'zone_ent_uncontrolled': 0, 
        'zone_ent_control_pct': 0.0,
        'zone_ent_successful': 0, 'zone_ent_success_pct': 0.0,
        'zone_ent_controlled_successful': 0, 'zone_ent_controlled_success_pct': 0.0,
        'zone_ent_uncontrolled_successful': 0, 'zone_ent_uncontrolled_success_pct': 0.0,
        # NEW: Shot/goal generation by control type
        'zone_ent_shot_generated': 0, 'zone_ent_shot_generated_pct': 0.0,
        'zone_ent_controlled_shot': 0, 'zone_ent_controlled_shot_pct': 0.0,
        'zone_ent_uncontrolled_shot': 0, 'zone_ent_uncontrolled_shot_pct': 0.0,
        'zone_ent_goal_generated': 0, 'zone_ent_goal_generated_pct': 0.0,
        'zone_ent_controlled_goal': 0, 'zone_ent_controlled_goal_pct': 0.0,
        'zone_ent_uncontrolled_goal': 0, 'zone_ent_uncontrolled_goal_pct': 0.0,
        'zone_ext_total': 0, 'zone_ext_controlled': 0, 'zone_ext_uncontrolled': 0, 
        'zone_ext_control_pct': 0.0,
        'zone_ext_successful': 0, 'zone_ext_success_pct': 0.0,
        'zone_ext_controlled_successful': 0, 'zone_ext_controlled_success_pct': 0.0,
        'zone_ext_uncontrolled_successful': 0, 'zone_ext_uncontrolled_success_pct': 0.0,
        # NEW: Shot/goal generation for exits
        'zone_ext_shot_generated': 0, 'zone_ext_shot_generated_pct': 0.0,
        'zone_ext_controlled_shot': 0, 'zone_ext_controlled_shot_pct': 0.0,
        'zone_ext_uncontrolled_shot': 0, 'zone_ext_uncontrolled_shot_pct': 0.0,
        'zone_ext_goal_generated': 0, 'zone_ext_goal_generated_pct': 0.0,
        'zone_ext_controlled_goal': 0, 'zone_ext_controlled_goal_pct': 0.0,
        'zone_ext_uncontrolled_goal': 0, 'zone_ext_uncontrolled_goal_pct': 0.0,
    }
    if len(pe_primary) == 0: return empty
    
    # Get events df for time_to_next_sog/time_to_next_goal lookups
    game_events = events[(events['game_id'] == game_id)] if events is not None and len(events) > 0 else pd.DataFrame()
    
    stats = {}
    zone_events = pe_primary[pe_primary['event_type'].astype(str).str.lower().str.contains('zone', na=False)] if 'event_type' in pe_primary.columns else pd.DataFrame()
    
    for direction, prefix in [('entry', 'zone_ent'), ('exit', 'zone_ext')]:
        if 'event_detail' in pe_primary.columns:
            zone_dir_events = zone_events[zone_events['event_detail'].astype(str).str.lower().str.contains(direction, na=False) & ~zone_events['event_detail'].astype(str).str.lower().str.contains('failed', na=False)]
        else:
            zone_dir_events = pd.DataFrame()
        
        total = len(zone_dir_events)
        stats[f'{prefix}_total'] = total
        
        # Determine controlled vs uncontrolled
        type_col = f'zone_{direction}_type_id'
        types_df = zone_entry_types if direction == 'entry' else zone_exit_types
        
        controlled_events = pd.DataFrame()
        uncontrolled_events = pd.DataFrame()
        
        if len(zone_dir_events) > 0 and type_col in zone_dir_events.columns and len(types_df) > 0:
            # Ensure consistent types for merge
            zone_dir_events_copy = zone_dir_events.copy()
            zone_dir_events_copy[type_col] = zone_dir_events_copy[type_col].astype(str)
            types_df_copy = types_df[[type_col, 'is_controlled']].copy()
            types_df_copy[type_col] = types_df_copy[type_col].astype(str)
            merged = zone_dir_events_copy.merge(types_df_copy, on=type_col, how='left')
            controlled_events = merged[merged['is_controlled'] == True]
            uncontrolled_events = merged[merged['is_controlled'] != True]
        else:
            uncontrolled_events = zone_dir_events
        
        controlled = len(controlled_events)
        uncontrolled = len(uncontrolled_events)
        
        stats[f'{prefix}_controlled'] = controlled
        stats[f'{prefix}_uncontrolled'] = uncontrolled
        stats[f'{prefix}_control_pct'] = round(controlled / total * 100, 1) if total > 0 else 0.0
        
        # Success rates (event_successful == True)
        if 'event_successful' in zone_dir_events.columns:
            total_successful = len(zone_dir_events[zone_dir_events['event_successful'] == True])
            controlled_successful = len(controlled_events[controlled_events['event_successful'] == True]) if len(controlled_events) > 0 else 0
            uncontrolled_successful = len(uncontrolled_events[uncontrolled_events['event_successful'] == True]) if len(uncontrolled_events) > 0 else 0
        else:
            total_successful = controlled_successful = uncontrolled_successful = 0
        
        stats[f'{prefix}_successful'] = total_successful
        stats[f'{prefix}_success_pct'] = round(total_successful / total * 100, 1) if total > 0 else 0.0
        stats[f'{prefix}_controlled_successful'] = controlled_successful
        stats[f'{prefix}_controlled_success_pct'] = round(controlled_successful / controlled * 100, 1) if controlled > 0 else 0.0
        stats[f'{prefix}_uncontrolled_successful'] = uncontrolled_successful
        stats[f'{prefix}_uncontrolled_success_pct'] = round(uncontrolled_successful / uncontrolled * 100, 1) if uncontrolled > 0 else 0.0
        
        # ===== NEW: Shot/Goal Generation by Control Type =====
        # Need to look up time_to_next_sog and time_to_next_goal from events table
        if len(game_events) > 0 and len(zone_dir_events) > 0:
            event_ids = zone_dir_events['event_id'].unique()
            event_data = game_events[game_events['event_id'].isin(event_ids)]
            
            def count_with_shot(event_df, threshold=10):
                if len(event_df) == 0 or 'event_id' not in event_df.columns:
                    return 0
                merged = event_df.merge(event_data[['event_id', 'time_to_next_sog']], on='event_id', how='left')
                return int(((merged['time_to_next_sog'].notna()) & (merged['time_to_next_sog'] <= threshold)).sum())
            
            def count_with_goal(event_df, threshold=15):
                if len(event_df) == 0 or 'event_id' not in event_df.columns:
                    return 0
                merged = event_df.merge(event_data[['event_id', 'time_to_next_goal']], on='event_id', how='left')
                return int(((merged['time_to_next_goal'].notna()) & (merged['time_to_next_goal'] <= threshold)).sum())
            
            # Total shot/goal generation
            stats[f'{prefix}_shot_generated'] = count_with_shot(zone_dir_events)
            stats[f'{prefix}_shot_generated_pct'] = round(stats[f'{prefix}_shot_generated'] / total * 100, 1) if total > 0 else 0.0
            stats[f'{prefix}_goal_generated'] = count_with_goal(zone_dir_events)
            stats[f'{prefix}_goal_generated_pct'] = round(stats[f'{prefix}_goal_generated'] / total * 100, 1) if total > 0 else 0.0
            
            # Controlled shot/goal generation
            stats[f'{prefix}_controlled_shot'] = count_with_shot(controlled_events)
            stats[f'{prefix}_controlled_shot_pct'] = round(stats[f'{prefix}_controlled_shot'] / controlled * 100, 1) if controlled > 0 else 0.0
            stats[f'{prefix}_controlled_goal'] = count_with_goal(controlled_events)
            stats[f'{prefix}_controlled_goal_pct'] = round(stats[f'{prefix}_controlled_goal'] / controlled * 100, 1) if controlled > 0 else 0.0
            
            # Uncontrolled shot/goal generation
            stats[f'{prefix}_uncontrolled_shot'] = count_with_shot(uncontrolled_events)
            stats[f'{prefix}_uncontrolled_shot_pct'] = round(stats[f'{prefix}_uncontrolled_shot'] / uncontrolled * 100, 1) if uncontrolled > 0 else 0.0
            stats[f'{prefix}_uncontrolled_goal'] = count_with_goal(uncontrolled_events)
            stats[f'{prefix}_uncontrolled_goal_pct'] = round(stats[f'{prefix}_uncontrolled_goal'] / uncontrolled * 100, 1) if uncontrolled > 0 else 0.0
    
    return stats

def calculate_possession_time_by_zone(player_id, game_id, event_players, events):
    """
    Calculate possession time by zone for a player in a game.
    
    Possession is defined as:
    Events where player is event_player_1 AND:
    - event_type = 'Possession' OR event_type = 'Zone_Entry_Exit'
    - AND event_detail contains 'rush' or 'carry' (case-insensitive)
    
    Returns duration (in seconds) by zone (offensive, defensive, neutral).
    
    Args:
        player_id: Player ID
        game_id: Game ID
        event_players: Event players DataFrame
        events: Events DataFrame
    
    Returns:
        Dict with possession time by zone (in seconds)
    """
    pe = event_players[(event_players['game_id'] == game_id) & 
                       (event_players['player_id'] == player_id)]
    
    empty = {
        'possession_time_offensive_zone': 0,
        'possession_time_defensive_zone': 0,
        'possession_time_neutral_zone': 0,
        'possession_time_o': 0,
        'possession_time_d': 0,
        'possession_time_n': 0,
        'possession_time_total': 0,
        'possession_events_count': 0
    }
    
    if len(pe) == 0:
        return empty
    
    # Filter to event_player_1 (PRIMARY_PLAYER)
    pe_primary = pe[pe['player_role'].astype(str).str.lower() == PRIMARY_PLAYER]
    
    if len(pe_primary) == 0:
        return empty
    
    # Identify possession events based on new requirements:
    # event_type = 'Possession' OR 'Zone_Entry_Exit'
    # AND event_detail contains 'rush' or 'carry'
    event_type_mask = pe_primary['event_type'].astype(str).str.lower().isin(['possession', 'zone_entry_exit'])
    
    # Check event_detail for rush or carry (case-insensitive)
    event_detail_mask = pd.Series([False] * len(pe_primary), index=pe_primary.index)
    if 'event_detail' in pe_primary.columns:
        event_detail_str = pe_primary['event_detail'].astype(str).str.lower()
        event_detail_mask = event_detail_str.str.contains('rush', na=False, regex=False) | \
                           event_detail_str.str.contains('carry', na=False, regex=False)
    
    # Combine filters: event_type match AND event_detail contains rush/carry
    possession_events_pe = pe_primary[event_type_mask & event_detail_mask]
    
    # Get possession event IDs
    possession_event_ids = []
    if len(possession_events_pe) > 0 and 'event_id' in possession_events_pe.columns:
        possession_event_ids = possession_events_pe['event_id'].dropna().unique().tolist()
    
    possession_event_ids = list(set([e for e in possession_event_ids if pd.notna(e)]))  # Deduplicate and remove NaN
    
    if len(possession_event_ids) == 0:
        return empty
    
    # Get events data for duration and zone
    game_events = events[(events['game_id'] == game_id)] if events is not None and len(events) > 0 else pd.DataFrame()
    
    if len(game_events) == 0:
        return empty
    
    # Match event_id (use same pattern as other functions)
    possession_events = game_events[game_events['event_id'].isin(possession_event_ids)]
    
    if len(possession_events) == 0:
        return empty
    
    # Calculate duration (prefer duration column, fallback to calculated)
    if 'duration' in possession_events.columns:
        possession_events['event_duration'] = possession_events['duration'].fillna(0).astype(float)
    elif 'time_start_total_seconds' in possession_events.columns and 'time_end_total_seconds' in possession_events.columns:
        possession_events['event_duration'] = (
            possession_events['time_start_total_seconds'].fillna(0) - 
            possession_events['time_end_total_seconds'].fillna(0)
        ).clip(lower=0).astype(float)
    else:
        # No duration available - return count only
        return {
            'possession_time_offensive_zone': 0,
            'possession_time_defensive_zone': 0,
            'possession_time_neutral_zone': 0,
            'possession_time_o': 0,
            'possession_time_d': 0,
            'possession_time_n': 0,
            'possession_time_total': 0,
            'possession_events_count': len(possession_events)
        }
    
    # Get zone column
    zone_col = 'event_team_zone' if 'event_team_zone' in possession_events.columns else None
    
    if zone_col is None:
        # No zone information - return totals only
        total_duration = int(possession_events['event_duration'].sum())
        return {
            'possession_time_offensive_zone': 0,
            'possession_time_defensive_zone': 0,
            'possession_time_neutral_zone': 0,
            'possession_time_o': 0,
            'possession_time_d': 0,
            'possession_time_n': 0,
            'possession_time_total': total_duration,
            'possession_events_count': len(possession_events)
        }
    
    # Group by zone and sum duration
    # Handle various zone formats: 'offensive'/'oz'/'off'/'o', 'defensive'/'dz'/'def'/'d', 'neutral'/'nz'/'n'
    zone_stats = {}
    zone_patterns = {
        'offensive': ['offensive', 'oz', 'off', 'o'],
        'defensive': ['defensive', 'dz', 'def', 'd'],
        'neutral': ['neutral', 'nz', 'n']
    }
    
    for key, patterns in zone_patterns.items():
        # Create mask for any pattern matching this zone
        zone_mask = pd.Series([False] * len(possession_events), index=possession_events.index)
        zone_str = possession_events[zone_col].astype(str).str.lower()
        for pattern in patterns:
            # For single letters, check exact match or starts with for longer values
            # For longer patterns, check if zone starts with or equals the pattern
            if len(pattern) == 1:
                # Single letter: exact match OR longer word starting with it
                pattern_mask = (zone_str == pattern) | (zone_str.str.startswith(pattern, na=False))
            else:
                # Multi-character: starts with pattern or equals pattern
                pattern_mask = (zone_str.str.startswith(pattern, na=False)) | (zone_str == pattern)
            zone_mask = zone_mask | pattern_mask
        
        zone_duration = int(possession_events[zone_mask]['event_duration'].sum())
        zone_stats[f'possession_time_{key}_zone'] = zone_duration
        # Also add shortened column names (o, d, n)
        if key == 'offensive':
            zone_stats['possession_time_o'] = zone_duration
        elif key == 'defensive':
            zone_stats['possession_time_d'] = zone_duration
        elif key == 'neutral':
            zone_stats['possession_time_n'] = zone_duration
    
    # Total
    total_duration = int(possession_events['event_duration'].sum())
    zone_stats['possession_time_total'] = total_duration
    zone_stats['possession_events_count'] = len(possession_events)
    
    # Additional metrics: averages and ratios
    if zone_stats['possession_events_count'] > 0:
        zone_stats['avg_possession_duration'] = round(total_duration / zone_stats['possession_events_count'], 2)
    else:
        zone_stats['avg_possession_duration'] = 0.0
    
    # Zone ratios (OZ/DZ ratio)
    if zone_stats['possession_time_defensive_zone'] > 0:
        zone_stats['possession_oz_dz_ratio'] = round(
            zone_stats['possession_time_offensive_zone'] / zone_stats['possession_time_defensive_zone'], 
            2
        )
    else:
        zone_stats['possession_oz_dz_ratio'] = 0.0
    
    # Zone time percentages (what % of possession time is in each zone)
    if total_duration > 0:
        zone_stats['possession_time_offensive_zone_pct'] = round(
            zone_stats['possession_time_offensive_zone'] / total_duration * 100, 
            1
        )
        zone_stats['possession_time_defensive_zone_pct'] = round(
            zone_stats['possession_time_defensive_zone'] / total_duration * 100, 
            1
        )
        zone_stats['possession_time_neutral_zone_pct'] = round(
            zone_stats['possession_time_neutral_zone'] / total_duration * 100, 
            1
        )
    else:
        zone_stats['possession_time_offensive_zone_pct'] = 0.0
        zone_stats['possession_time_defensive_zone_pct'] = 0.0
        zone_stats['possession_time_neutral_zone_pct'] = 0.0
    
    return zone_stats

def calculate_faceoff_zone_stats(player_id, game_id, event_players):
    pe = event_players[(event_players['game_id'] == game_id) & (event_players['player_id'] == player_id)]
    empty = {'fo_wins_oz': 0, 'fo_wins_nz': 0, 'fo_wins_dz': 0, 'fo_losses_oz': 0, 'fo_losses_nz': 0, 'fo_losses_dz': 0, 'fo_pct_oz': 0.0, 'fo_pct_nz': 0.0, 'fo_pct_dz': 0.0}
    if len(pe) == 0: return empty
    
    faceoffs = pe[pe['event_type'].astype(str).str.lower() == 'faceoff'] if 'event_type' in pe.columns else pd.DataFrame()
    if len(faceoffs) == 0: return empty
    
    # FO Win = player is event_player_1, FO Loss = player is opp_player_1
    fo_wins = faceoffs[faceoffs['player_role'].astype(str).str.lower() == PRIMARY_PLAYER]
    fo_losses = faceoffs[faceoffs['player_role'].astype(str).str.lower() == 'opp_player_1']
    
    stats = {}
    zone_col = 'event_team_zone' if 'event_team_zone' in faceoffs.columns else None
    if zone_col:
        for zone, abbr in [('offensive', 'oz'), ('neutral', 'nz'), ('defensive', 'dz')]:
            wins = len(fo_wins[fo_wins[zone_col].astype(str).str.lower().str.contains(zone, na=False)])
            losses = len(fo_losses[fo_losses[zone_col].astype(str).str.lower().str.contains(zone, na=False)])
            stats[f'fo_wins_{abbr}'], stats[f'fo_losses_{abbr}'] = wins, losses
            stats[f'fo_pct_{abbr}'] = round(wins / (wins + losses) * 100, 1) if (wins + losses) > 0 else 0.0
    else:
        for abbr in ['oz', 'nz', 'dz']:
            stats[f'fo_wins_{abbr}'] = stats[f'fo_losses_{abbr}'] = 0
            stats[f'fo_pct_{abbr}'] = 0.0
    return stats

def calculate_wdbe_faceoffs(player_id, game_id, event_players, events):
    """
    Calculate Win Direction Based Events (WDBE) for faceoffs.
    
    Values faceoffs by where puck goes (direction) and win type (clean vs scrum).
    
    Returns:
        Dict with WDBE metrics
    """
    pe = event_players[(event_players['game_id'] == game_id) & 
                       (event_players['player_id'] == player_id)]
    
    empty = {
        'faceoffs_clean_wins': 0,
        'faceoffs_scrum_wins': 0,
        'faceoffs_wdbe_value': 0.0,
        'faceoff_wdbe_rate': 0.0
    }
    
    if len(pe) == 0:
        return empty
    
    # Get faceoff events where player is event_player_1 (winner)
    pe_primary = pe[pe['player_role'].astype(str).str.lower() == PRIMARY_PLAYER]
    faceoff_wins = pe_primary[pe_primary['event_type'].astype(str).str.lower() == 'faceoff']
    
    if len(faceoff_wins) == 0:
        return empty
    
    # WDBE weights (to be calibrated with historical data)
    WDBE_WEIGHTS = {
        'clean_forward': 0.12,   # Clean win, forward direction
        'clean_back': 0.15,      # Clean win, back direction (more valuable)
        'clean_neutral': 0.08,   # Clean win, neutral
        'scrum_forward': 0.06,   # Scrum win, forward
        'scrum_back': 0.08,      # Scrum win, back
        'scrum_neutral': 0.04,   # Scrum win, neutral
    }
    
    clean_wins = 0
    scrum_wins = 0
    wdbe_total = 0.0
    
    # Get faceoff events for context
    faceoff_event_ids = faceoff_wins['event_id'].unique() if 'event_id' in faceoff_wins.columns else []
    if len(faceoff_event_ids) == 0 or events is None or len(events) == 0:
        return empty
    
    faceoff_events = events[(events['game_id'] == game_id) & 
                           (events['event_id'].isin(faceoff_event_ids))]
    
    for _, faceoff in faceoff_wins.iterrows():
        event_id = faceoff['event_id']
        faceoff_event = faceoff_events[faceoff_events['event_id'] == event_id]
        
        if len(faceoff_event) == 0:
            continue
        
        event_row = faceoff_event.iloc[0]
        
        # Classify win type
        play_detail1 = str(event_row.get('play_detail1', '')).lower()
        play_detail_2 = str(event_row.get('play_detail_2', '')).lower()
        play_detail = f"{play_detail1} {play_detail_2}"
        is_clean = any(term in play_detail for term in 
                      ['clean', 'direct', 'straight', 'won clean'])
        
        # Classify direction (simplified - can be enhanced with XY)
        direction = 'neutral'  # Default
        event_detail = str(event_row.get('event_detail', '')).lower()
        if 'forward' in event_detail or 'ahead' in event_detail:
            direction = 'forward'
        elif 'back' in event_detail or 'behind' in event_detail:
            direction = 'back'
        
        # Count wins
        if is_clean:
            clean_wins += 1
            wdbe_key = f'clean_{direction}'
        else:
            scrum_wins += 1
            wdbe_key = f'scrum_{direction}'
        
        # Add WDBE value
        wdbe_total += WDBE_WEIGHTS.get(wdbe_key, 0.06)
    
    total_wins = clean_wins + scrum_wins
    return {
        'faceoffs_clean_wins': clean_wins,
        'faceoffs_scrum_wins': scrum_wins,
        'faceoffs_wdbe_value': round(wdbe_total, 2),
        'faceoff_wdbe_rate': round(wdbe_total / total_wins, 3) if total_wins > 0 else 0.0
    }

def calculate_player_event_stats(player_id, game_id, event_players, events=None):
    pe = event_players[(event_players['game_id'] == game_id) & (event_players['player_id'] == player_id)]
    if len(pe) == 0: return {}
    
    # CRITICAL: Only event_player_1 gets credit for shots, passes, etc.
    pe_primary = pe[pe['player_role'].astype(str).str.lower() == PRIMARY_PLAYER]
    
    stats = {}
    # Goals: event_player_1 on goal events
    goals = pe_primary[is_goal_scored(pe_primary)]
    stats['goals'] = len(goals)
    
    # Assists: Tracked via play_detail1='AssistPrimary'/'AssistSecondary' on the PASS/SHOT event
    # The player who made the assist pass is event_player_1 on that event
    if 'play_detail1' in pe_primary.columns:
        stats['primary_assists'] = len(pe_primary[pe_primary['play_detail1'].astype(str).str.lower() == 'assistprimary'])
        stats['secondary_assists'] = len(pe_primary[pe_primary['play_detail1'].astype(str).str.lower() == 'assistsecondary'])
    else:
        stats['primary_assists'] = 0
        stats['secondary_assists'] = 0
    stats['assists'] = stats['primary_assists'] + stats['secondary_assists']
    stats['points'] = stats['goals'] + stats['assists']
    
    # Shots: Only count where player is event_player_1
    shots = pe_primary[pe_primary['event_type'].astype(str).str.lower() == 'shot']
    stats['shots'] = len(shots)
    sog = shots[shots['event_detail'].astype(str).str.lower().str.contains('onnet|saved', na=False, regex=True)]
    stats['sog'] = len(sog) + stats['goals']
    stats['shooting_pct'] = round(stats['goals'] / stats['sog'] * 100, 1) if stats['sog'] > 0 else 0.0
    
    # Passes: Only count where player is event_player_1
    passes = pe_primary[pe_primary['event_type'].astype(str).str.lower() == 'pass']
    stats['pass_attempts'] = len(passes)
    stats['pass_completed'] = len(passes[passes['event_detail'].astype(str).str.lower().str.contains('completed', na=False)])
    stats['pass_pct'] = round(stats['pass_completed'] / stats['pass_attempts'] * 100, 1) if stats['pass_attempts'] > 0 else 0.0
    
    # Faceoffs: event_player_1 = winner, opp_player_1 = loser
    # FO wins: player is event_player_1 on faceoff events
    faceoffs_won = pe_primary[pe_primary['event_type'].astype(str).str.lower() == 'faceoff']
    stats['fo_wins'] = len(faceoffs_won)
    # FO losses: player is opp_player_1 on faceoff events
    pe_opp = pe[pe['player_role'].astype(str).str.lower() == 'opp_player_1']
    faceoffs_lost = pe_opp[pe_opp['event_type'].astype(str).str.lower() == 'faceoff']
    stats['fo_losses'] = len(faceoffs_lost)
    stats['fo_total'] = stats['fo_wins'] + stats['fo_losses']
    stats['fo_pct'] = round(stats['fo_wins'] / stats['fo_total'] * 100, 1) if stats['fo_total'] > 0 else 0.0
    
    # Turnovers: Only count where player is event_player_1
    turnovers = pe_primary[pe_primary['event_type'].astype(str).str.lower() == 'turnover']
    giveaway_events = turnovers[turnovers['event_detail'].astype(str).str.lower().str.contains('giveaway', na=False)]
    stats['giveaways'] = len(giveaway_events)
    stats['takeaways'] = len(turnovers[turnovers['event_detail'].astype(str).str.lower().str.contains('takeaway', na=False)])
    stats['turnover_diff'] = stats['takeaways'] - stats['giveaways']
    
    # Bad giveaways: Use is_bad_giveaway flag from events table
    stats['bad_giveaways'] = 0
    if events is not None and len(giveaway_events) > 0 and 'is_bad_giveaway' in events.columns:
        giveaway_event_ids = giveaway_events['event_id'].unique()
        bad_events = events[(events['event_id'].isin(giveaway_event_ids)) & (events['is_bad_giveaway'] == 1)]
        stats['bad_giveaways'] = len(bad_events)
    stats['bad_turnover_diff'] = stats['takeaways'] - stats['bad_giveaways']
    
    # Blocks: play_detail1='BlockedShot', use DISTINCT by linked_event to avoid double-counting
    # For linked events, same play_detail can appear on multiple rows - count once per linked group
    stats['blocks'] = 0
    if 'play_detail1' in pe.columns:
        blocks_df = pe[pe['play_detail1'].astype(str).str.lower().str.contains('blockedshot', na=False)]
        if len(blocks_df) > 0:
            if 'linked_event_index_flag' in blocks_df.columns:
                # For rows with linked_event_index_flag, count unique flags
                # For rows without (NaN), count each row
                linked = blocks_df[blocks_df['linked_event_index_flag'].notna()]
                unlinked = blocks_df[blocks_df['linked_event_index_flag'].isna()]
                stats['blocks'] = linked['linked_event_index_flag'].nunique() + len(unlinked)
            else:
                stats['blocks'] = len(blocks_df)
    
    # Hits (non-hitting league, will be 0)
    stats['hits'] = len(pe_primary[pe_primary['event_type'].astype(str).str.lower() == 'hit'])
    
    # DEFENSIVE ROLE METRICS
    # When player is opp_player_1 = primary defender on opponent's event
    pe_opp_primary = pe[pe['player_role'].astype(str).str.lower() == 'opp_player_1']
    pe_opp_support = pe[pe['player_role'].astype(str).str.lower().str.match(r'opp_player_[2-6]')]
    
    stats['primary_def_events'] = len(pe_opp_primary)
    stats['support_def_events'] = len(pe_opp_support)
    stats['def_involvement'] = stats['primary_def_events'] + stats['support_def_events']
    
    # Primary defender on specific event types
    stats['primary_def_shots'] = len(pe_opp_primary[pe_opp_primary['event_type'].astype(str).str.lower() == 'shot'])
    stats['primary_def_goals_against'] = len(pe_opp_primary[is_goal_scored(pe_opp_primary)])
    stats['primary_def_passes'] = len(pe_opp_primary[pe_opp_primary['event_type'].astype(str).str.lower() == 'pass'])
    return stats

def calculate_player_shift_stats(player_id, game_id, shifts, shift_players):
    ps = shift_players[(shift_players['game_id'] == game_id) & (shift_players['player_id'] == player_id)] if len(shift_players) > 0 and 'player_id' in shift_players.columns else pd.DataFrame()
    empty = {
        'toi_seconds': 0, 'toi_minutes': 0.0, 'shift_count': 0, 'avg_shift': 0.0,
        'plus_ev': 0, 'minus_ev': 0, 'plus_minus_ev': 0,
        'corsi_for': 0, 'corsi_against': 0, 'cf_pct': 50.0,
        'player_rating': 4.0, 'team_avg_rating': 4.0, 'opp_avg_rating': 4.0,
        'team_rating_diff': 0.0, 'rating_diff': 0.0,
        'team_min_rating_avg': 4.0, 'team_max_rating_avg': 4.0,
        'opp_min_rating_avg': 4.0, 'opp_max_rating_avg': 4.0,
        'min_rating_diff': 0.0, 'max_rating_diff': 0.0
    }
    if len(ps) == 0: return empty
    
    stats = {}
    stats['toi_seconds'] = int(ps['shift_duration'].sum()) if 'shift_duration' in ps.columns else 0
    stats['toi_minutes'] = round(stats['toi_seconds'] / 60, 1)
    
    # LOGICAL SHIFT COUNT: Count distinct logical_shift_number, not raw shift rows
    if 'logical_shift_number' in ps.columns:
        stats['shift_count'] = ps['logical_shift_number'].nunique()
    else:
        stats['shift_count'] = len(ps)  # Fallback to raw count if logical not available
    stats['avg_shift'] = round(stats['toi_seconds'] / stats['shift_count'], 1) if stats['shift_count'] > 0 else 0.0
    
    stats['plus_ev'] = int(ps['gf_ev'].sum()) if 'gf_ev' in ps.columns else int(ps['gf'].sum()) if 'gf' in ps.columns else 0
    stats['minus_ev'] = int(ps['ga_ev'].sum()) if 'ga_ev' in ps.columns else int(ps['ga'].sum()) if 'ga' in ps.columns else 0
    stats['plus_minus_ev'] = stats['plus_ev'] - stats['minus_ev']
    
    if 'cf' in ps.columns:
        stats['corsi_for'], stats['corsi_against'] = int(ps['cf'].sum()), int(ps['ca'].sum())
        total = stats['corsi_for'] + stats['corsi_against']
        stats['cf_pct'] = round(stats['corsi_for'] / total * 100, 1) if total > 0 else 50.0
    else:
        stats['corsi_for'] = stats['corsi_against'] = 0
        stats['cf_pct'] = 50.0
    
    # Player's own rating
    stats['player_rating'] = round(ps['player_rating'].mean(), 2) if 'player_rating' in ps.columns and pd.notna(ps['player_rating']).any() else 4.0
    
    # Team avg rating (teammates on ice, excluding goalies - already computed in shift data)
    stats['team_avg_rating'] = round(ps['team_avg_rating'].mean(), 2) if 'team_avg_rating' in ps.columns and pd.notna(ps['team_avg_rating']).any() else 4.0
    
    # Opponent avg rating
    stats['opp_avg_rating'] = round(ps['opp_avg_rating'].mean(), 2) if 'opp_avg_rating' in ps.columns and pd.notna(ps['opp_avg_rating']).any() else 4.0
    
    # Team rating diff: opp_avg - team_avg (positive = facing tougher team)
    stats['team_rating_diff'] = round(stats['opp_avg_rating'] - stats['team_avg_rating'], 2)
    
    # Personal rating diff: opp_avg - player_rating (positive = facing tougher competition personally)
    stats['rating_diff'] = round(stats['opp_avg_rating'] - stats['player_rating'], 2)
    
    # Min/Max ratings by venue (need to figure out team vs opp based on player's venue)
    venue = ps['venue'].iloc[0] if 'venue' in ps.columns and len(ps) > 0 else None
    
    if venue == 'home':
        team_min_col, team_max_col = 'home_min_rating', 'home_max_rating'
        opp_min_col, opp_max_col = 'away_min_rating', 'away_max_rating'
    else:  # away or unknown
        team_min_col, team_max_col = 'away_min_rating', 'away_max_rating'
        opp_min_col, opp_max_col = 'home_min_rating', 'home_max_rating'
    
    # Use pd.notna() to safely check for non-null values
    stats['team_min_rating_avg'] = round(ps[team_min_col].mean(), 2) if team_min_col in ps.columns and pd.notna(ps[team_min_col]).any() else 4.0
    stats['team_max_rating_avg'] = round(ps[team_max_col].mean(), 2) if team_max_col in ps.columns and pd.notna(ps[team_max_col]).any() else 4.0
    stats['opp_min_rating_avg'] = round(ps[opp_min_col].mean(), 2) if opp_min_col in ps.columns and pd.notna(ps[opp_min_col]).any() else 4.0
    stats['opp_max_rating_avg'] = round(ps[opp_max_col].mean(), 2) if opp_max_col in ps.columns and pd.notna(ps[opp_max_col]).any() else 4.0
    
    # Min/Max rating diffs (opp - team, positive = opp has better min/max)
    stats['min_rating_diff'] = round(stats['opp_min_rating_avg'] - stats['team_min_rating_avg'], 2)
    stats['max_rating_diff'] = round(stats['opp_max_rating_avg'] - stats['team_max_rating_avg'], 2)
    
    return stats

# =============================================================================
# PHASE 3: LINEMATE, TIME BUCKET, REBOUND ANALYSIS
# =============================================================================

def calculate_linemate_stats(player_id, game_id, shift_players, players_df=None):
    """
    Phase 3: Linemate analysis - tracks player partnerships using fact_shift_players.
    Identifies unique linemates, top partner by TOI, chemistry score (CF% with regular linemates).
    """
    empty = {
        'unique_linemates': 0,
        'top_linemate_player_id': None,
        'top_linemate_toi_together': 0,
        'top_line_cf_pct': 50.0,
        'chemistry_score': 0.0,
        'd_partner_player_id': None,
        'd_partner_toi_together': 0,
        'line_consistency_pct': 0.0,
    }
    
    if len(shift_players) == 0 or 'shift_id' not in shift_players.columns:
        return empty
    
    # Get all shifts for this player in this game
    player_shifts = shift_players[(shift_players['game_id'] == game_id) & (shift_players['player_id'] == player_id)]
    if len(player_shifts) == 0:
        return empty
    
    # Get player's team and position
    player_team = player_shifts['team_id'].iloc[0] if 'team_id' in player_shifts.columns else None
    player_pos = player_shifts['position'].iloc[0] if 'position' in player_shifts.columns else 'F'
    is_defenseman = str(player_pos).upper().startswith('D')  # D, D1, D2, Defense, etc.
    
    # Get all shift_ids for this player
    player_shift_ids = player_shifts['shift_id'].unique()
    
    # Find all teammates on those same shifts (same team, same shift)
    teammates_on_shifts = shift_players[
        (shift_players['shift_id'].isin(player_shift_ids)) & 
        (shift_players['player_id'] != player_id)
    ]
    
    # Filter to same team only
    if player_team is not None and 'team_id' in teammates_on_shifts.columns:
        teammates_on_shifts = teammates_on_shifts[teammates_on_shifts['team_id'] == player_team]
    
    if len(teammates_on_shifts) == 0:
        return empty
    
    # Exclude goalies from linemates
    if 'position' in teammates_on_shifts.columns:
        teammates_on_shifts = teammates_on_shifts[~teammates_on_shifts['position'].astype(str).str.lower().str.contains('goalie', na=False)]
    
    if len(teammates_on_shifts) == 0:
        return empty
    
    # Count unique linemates
    unique_linemates = teammates_on_shifts['player_id'].nunique()
    
    # Calculate TOI with each linemate
    linemate_toi = {}
    linemate_cf = {}
    linemate_ca = {}
    
    for _, tm in teammates_on_shifts.iterrows():
        tm_id = tm['player_id']
        duration = tm.get('shift_duration', 0) or 0
        cf = tm.get('cf', 0) or 0
        ca = tm.get('ca', 0) or 0
        
        if tm_id not in linemate_toi:
            linemate_toi[tm_id] = 0
            linemate_cf[tm_id] = 0
            linemate_ca[tm_id] = 0
        
        linemate_toi[tm_id] += duration
        linemate_cf[tm_id] += cf
        linemate_ca[tm_id] += ca
    
    if not linemate_toi:
        return empty
    
    # Find top linemate by TOI
    top_linemate = max(linemate_toi.items(), key=lambda x: x[1])
    top_linemate_id = top_linemate[0]
    top_linemate_toi = int(top_linemate[1])
    
    # Calculate CF% with top linemate
    top_cf = linemate_cf.get(top_linemate_id, 0)
    top_ca = linemate_ca.get(top_linemate_id, 0)
    top_line_cf_pct = round(top_cf / (top_cf + top_ca) * 100, 1) if (top_cf + top_ca) > 0 else 50.0
    
    # Chemistry score: deviation from 50% (neutral)
    chemistry_score = round(top_line_cf_pct - 50.0, 1)
    
    # D-partner analysis (for defensemen only)
    d_partner_id = None
    d_partner_toi = 0
    
    if is_defenseman and 'position' in teammates_on_shifts.columns:
        d_teammates = teammates_on_shifts[teammates_on_shifts['position'].astype(str).str.upper().str.startswith('D')]
        if len(d_teammates) > 0:
            d_linemate_toi = {}
            for _, tm in d_teammates.iterrows():
                tm_id = tm['player_id']
                duration = tm.get('shift_duration', 0) or 0
                d_linemate_toi[tm_id] = d_linemate_toi.get(tm_id, 0) + duration
            
            if d_linemate_toi:
                top_d = max(d_linemate_toi.items(), key=lambda x: x[1])
                d_partner_id = top_d[0]
                d_partner_toi = int(top_d[1])
    
    # Line consistency: % of shifts with same top 2 linemates
    top_2_linemates = sorted(linemate_toi.items(), key=lambda x: x[1], reverse=True)[:2]
    top_2_ids = set([x[0] for x in top_2_linemates])
    
    shifts_with_top_2 = 0
    total_shifts = len(player_shift_ids)
    
    for shift_id in player_shift_ids:
        shift_teammates = teammates_on_shifts[teammates_on_shifts['shift_id'] == shift_id]['player_id'].unique()
        if len(set(shift_teammates) & top_2_ids) >= 2:
            shifts_with_top_2 += 1
    
    line_consistency = round(shifts_with_top_2 / total_shifts * 100, 1) if total_shifts > 0 else 0.0
    
    return {
        'unique_linemates': unique_linemates,
        'top_linemate_player_id': top_linemate_id,
        'top_linemate_toi_together': top_linemate_toi,
        'top_line_cf_pct': top_line_cf_pct,
        'chemistry_score': chemistry_score,
        'd_partner_player_id': d_partner_id,
        'd_partner_toi_together': d_partner_toi,
        'line_consistency_pct': line_consistency,
    }


def calculate_time_bucket_stats(player_id, game_id, event_players, events, shift_players=None):
    """
    Phase 3: Time bucket analysis - performance by period timing.
    
    FORMULAS:
    - Early period = first 10 minutes (time_bucket_id in TB01, TB02)
    - Late period = last 5 minutes (time_bucket_id in TB04, TB05)
    
    - early_period_cf = sum(cf) for shifts in early time buckets
    - early_period_ca = sum(ca) for shifts in early time buckets
    - early_period_cf_pct = early_period_cf / (early_period_cf + early_period_ca) * 100
    
    - late_period_cf = sum(cf) for shifts in late time buckets
    - late_period_ca = sum(ca) for shifts in late time buckets  
    - late_period_cf_pct = late_period_cf / (late_period_cf + late_period_ca) * 100
    """
    empty = {
        'early_period_goals': 0,
        'early_period_assists': 0,
        'early_period_points': 0,
        'early_period_shots': 0,
        'early_period_cf': 0,
        'early_period_ca': 0,
        'early_period_cf_pct': 50.0,
        'late_period_goals': 0,
        'late_period_assists': 0,
        'late_period_points': 0,
        'late_period_shots': 0,
        'late_period_cf': 0,
        'late_period_ca': 0,
        'late_period_cf_pct': 50.0,
        'first_goal_involvement': 0,
    }
    
    if len(event_players) == 0 or len(events) == 0:
        return empty
    
    # Get player's events in this game
    pe = event_players[(event_players['game_id'] == game_id) & (event_players['player_id'] == player_id)]
    if len(pe) == 0:
        return empty
    
    player_event_ids = pe['event_id'].unique() if 'event_id' in pe.columns else []
    game_events = events[events['game_id'] == game_id]
    player_events = game_events[game_events['event_id'].isin(player_event_ids)] if len(player_event_ids) > 0 else pd.DataFrame()
    
    if len(player_events) == 0 or 'time_bucket_id' not in player_events.columns:
        return empty
    
    stats = {}
    
    # Early period = TB01, TB02 (first 8-10 minutes)
    early_events = player_events[player_events['time_bucket_id'].isin(['TB01', 'TB02'])]
    # Late period = TB04, TB05 (last 5 minutes)
    late_events = player_events[player_events['time_bucket_id'].isin(['TB04', 'TB05'])]
    
    # Early period stats
    early_pe = pe[pe['event_id'].isin(early_events['event_id'].unique())] if len(early_events) > 0 else pd.DataFrame()
    stats['early_period_goals'] = len(early_pe[(early_pe['player_role'].astype(str).str.lower() == PRIMARY_PLAYER) & is_goal_scored(early_pe)]) if len(early_pe) > 0 else 0
    stats['early_period_assists'] = len(early_pe[early_pe['player_role'].astype(str).str.lower().str.contains('event_player_2|event_player_3', na=False, regex=True) & is_goal_scored(early_pe)]) if len(early_pe) > 0 else 0
    stats['early_period_points'] = stats['early_period_goals'] + stats['early_period_assists']
    stats['early_period_shots'] = len(early_events[early_events['event_type'].astype(str).str.lower().isin(['shot', 'goal'])])
    
    # Late period stats
    late_pe = pe[pe['event_id'].isin(late_events['event_id'].unique())] if len(late_events) > 0 else pd.DataFrame()
    stats['late_period_goals'] = len(late_pe[(late_pe['player_role'].astype(str).str.lower() == PRIMARY_PLAYER) & is_goal_scored(late_pe)]) if len(late_pe) > 0 else 0
    stats['late_period_assists'] = len(late_pe[late_pe['player_role'].astype(str).str.lower().str.contains('event_player_2|event_player_3', na=False, regex=True) & is_goal_scored(late_pe)]) if len(late_pe) > 0 else 0
    stats['late_period_points'] = stats['late_period_goals'] + stats['late_period_assists']
    stats['late_period_shots'] = len(late_events[late_events['event_type'].astype(str).str.lower().isin(['shot', 'goal'])])
    
    # CF/CA from shift_players (properly implemented)
    # Determine early/late based on shift timing within period
    stats['early_period_cf'] = 0
    stats['early_period_ca'] = 0
    stats['late_period_cf'] = 0
    stats['late_period_ca'] = 0
    
    if shift_players is not None and len(shift_players) > 0:
        ps = shift_players[(shift_players['game_id'] == game_id) & (shift_players['player_id'] == player_id)]
        
        if len(ps) > 0 and 'shift_start_total_seconds' in ps.columns:
            # Each period is ~20 min (1200 sec) in a standard game
            # Early = first 10 min = 600 sec from period start
            # Late = last 5 min = 300 sec before period end
            
            for period in [1, 2, 3]:
                period_shifts = ps[ps['period'] == period]
                if len(period_shifts) == 0:
                    continue
                
                # Get time range for this period
                period_start = period_shifts['shift_start_total_seconds'].max()  # Start of period (highest time)
                period_end = period_shifts['shift_end_total_seconds'].min()  # End of period (lowest time)
                
                period_duration = period_start - period_end if period_start > period_end else 0
                early_threshold = period_start - (period_duration * 0.5)  # First 50% = early
                late_threshold = period_end + (period_duration * 0.25)  # Last 25% = late
                
                # Early shifts (shift starts in first half of period)
                early_shifts = period_shifts[period_shifts['shift_start_total_seconds'] >= early_threshold]
                if len(early_shifts) > 0 and 'cf' in early_shifts.columns:
                    stats['early_period_cf'] += int(early_shifts['cf'].sum())
                    stats['early_period_ca'] += int(early_shifts['ca'].sum())
                
                # Late shifts (shift ends in last quarter of period)
                late_shifts = period_shifts[period_shifts['shift_end_total_seconds'] <= late_threshold]
                if len(late_shifts) > 0 and 'cf' in late_shifts.columns:
                    stats['late_period_cf'] += int(late_shifts['cf'].sum())
                    stats['late_period_ca'] += int(late_shifts['ca'].sum())
    
    # Calculate CF%
    early_total = stats['early_period_cf'] + stats['early_period_ca']
    stats['early_period_cf_pct'] = round(stats['early_period_cf'] / early_total * 100, 1) if early_total > 0 else 50.0
    
    late_total = stats['late_period_cf'] + stats['late_period_ca']
    stats['late_period_cf_pct'] = round(stats['late_period_cf'] / late_total * 100, 1) if late_total > 0 else 50.0
    
    # First goal involvement - was player involved in first goal of game?
    all_game_goals = game_events[is_goal_scored(game_events)]
    if len(all_game_goals) > 0:
        first_goal = all_game_goals.nsmallest(1, 'time_start_total_seconds') if 'time_start_total_seconds' in all_game_goals.columns else all_game_goals.head(1)
        first_goal_id = first_goal['event_id'].iloc[0] if len(first_goal) > 0 else None
        
        if first_goal_id:
            player_in_first = pe[pe['event_id'] == first_goal_id]
            stats['first_goal_involvement'] = 1 if len(player_in_first) > 0 else 0
        else:
            stats['first_goal_involvement'] = 0
    else:
        stats['first_goal_involvement'] = 0
    
    return stats


def calculate_rebound_stats(player_id, game_id, event_players, events):
    """
    Phase 3: Rebound/second chance tracking.
    
    DEFINITION: A rebound shot is a shot where prev_event_type='Rebound'.
    This means the shot followed a goalie save that created a rebound.
    """
    empty = {
        'rebound_recoveries': 0,
        'rebound_shots': 0,
        'rebound_goals': 0,
        'rebound_shot_pct': 0.0,
        'crash_net_attempts': 0,
        'crash_net_success': 0,
        'garbage_goals': 0,
    }
    
    if len(event_players) == 0 or len(events) == 0:
        return empty
    
    # Get player's events in this game
    pe = event_players[(event_players['game_id'] == game_id) & (event_players['player_id'] == player_id)]
    if len(pe) == 0:
        return empty
    
    pe_primary = pe[pe['player_role'].astype(str).str.lower() == PRIMARY_PLAYER]
    player_event_ids = pe_primary['event_id'].unique() if 'event_id' in pe_primary.columns else []
    game_events = events[events['game_id'] == game_id]
    player_events = game_events[game_events['event_id'].isin(player_event_ids)] if len(player_event_ids) > 0 else pd.DataFrame()
    
    if len(player_events) == 0:
        return empty
    
    stats = {}
    
    # Rebound recoveries (is_rebound=1 and player is primary)
    if 'is_rebound' in player_events.columns:
        stats['rebound_recoveries'] = int((player_events['is_rebound'] == 1).sum())
    else:
        stats['rebound_recoveries'] = 0
    
    # Rebound shots: shots where prev_event_type='Rebound'
    # This is the correct definition - shots that follow a rebound event
    rebound_shots = 0
    rebound_goals = 0
    
    if 'prev_event_type' in player_events.columns:
        # Shots that follow a rebound (goalie save that bounced)
        shots_after_rebound = player_events[
            (player_events['event_type'].astype(str).str.lower() == 'shot') &
            (player_events['prev_event_type'].astype(str).str.lower() == 'rebound')
        ]
        rebound_shots = len(shots_after_rebound)
        rebound_goals = len(shots_after_rebound[is_goal_scored(shots_after_rebound)])
        
        # Also check goals that follow rebounds (goal events, not shot events)
        goals_after_rebound = player_events[
            is_goal_scored(player_events) &
            (player_events['prev_event_type'].astype(str).str.lower() == 'rebound')
        ]
        # Add goals that weren't counted as shots
        rebound_goals = max(rebound_goals, len(goals_after_rebound))
    
    stats['rebound_shots'] = rebound_shots
    stats['rebound_goals'] = rebound_goals
    stats['rebound_shot_pct'] = round(rebound_goals / rebound_shots * 100, 1) if rebound_shots > 0 else 0.0
    
    # Crash net attempts from play_detail
    if 'play_detail1' in player_events.columns or 'play_detail_2' in player_events.columns:
        crash_net = 0
        for col in ['play_detail1', 'play_detail_2']:
            if col in player_events.columns:
                crash_net += player_events[col].astype(str).str.lower().str.contains('crashnet', na=False).sum()
        stats['crash_net_attempts'] = int(crash_net)
    else:
        stats['crash_net_attempts'] = 0
    
    # Crash net success (crash net that led to shot/goal)
    stats['crash_net_success'] = 0  # Would need sequence analysis
    
    # Garbage goals (from event_detail_2 patterns)
    if 'event_detail_2' in player_events.columns:
        player_goals = player_events[is_goal_scored(player_events)]
        garbage = player_goals['event_detail_2'].astype(str).str.lower().str.contains('scramble|rebound|deflection|tip', na=False, regex=True).sum()
        stats['garbage_goals'] = int(garbage)
    else:
        stats['garbage_goals'] = 0
    
    return stats


# =============================================================================
# GOALIE WAR (NEW)
# =============================================================================

def calculate_goalie_war(stats: dict) -> dict:
    """Calculate goalie-specific WAR."""
    # Goals Saved Above Average (main component)
    gsaa = stats.get('goals_saved_above_avg', 0)
    
    # High danger save bonus
    hd_saves = stats.get('hd_saves', 0)
    hd_bonus = hd_saves * GOALIE_GAR_WEIGHTS['high_danger_saves']
    
    # Quality start bonus
    qs_bonus = GOALIE_GAR_WEIGHTS['quality_start_bonus'] if stats.get('is_quality_start', 0) == 1 else 0
    
    # Rebound control (freeze vs rebound)
    freezes = stats.get('saves_freeze', 0)
    total_saves = stats.get('saves', 0)
    rebound_control = (freezes / total_saves) * GOALIE_GAR_WEIGHTS['rebound_control'] * total_saves if total_saves > 0 else 0
    
    # Total GAR
    gar_total = gsaa * GOALIE_GAR_WEIGHTS['goals_prevented'] + hd_bonus + qs_bonus + rebound_control
    
    return {
        'goalie_gar_gsaa': round(gsaa, 2),
        'goalie_gar_hd_bonus': round(hd_bonus, 2),
        'goalie_gar_qs_bonus': round(qs_bonus, 2),
        'goalie_gar_rebound': round(rebound_control, 2),
        'goalie_gar_total': round(gar_total, 2),
        'goalie_war': round(gar_total / GOALS_PER_WIN, 2),
        'goalie_war_pace': round(gar_total / GOALS_PER_WIN * GAMES_PER_SEASON, 2),
    }

# =============================================================================
# MAIN BUILDERS
# =============================================================================

def create_fact_player_game_stats() -> pd.DataFrame:
    """
    Create fact_player_game_stats - SKATERS ONLY (excludes goalies).
    
    v29.4: Now uses PlayerStatsBuilder for better organization and testability.
    """
    from src.builders.player_stats import build_fact_player_game_stats
    return build_fact_player_game_stats(save=False)  # Save handled by create_all_core_facts


def create_fact_team_game_stats() -> pd.DataFrame:
    """
    Create fact_team_game_stats.
    
    v29.4: Now uses TeamStatsBuilder for better organization and testability.
    """
    from src.builders.team_stats import build_fact_team_game_stats
    return build_fact_team_game_stats(save=False)  # Save handled by create_all_core_facts


def create_fact_goalie_game_stats() -> pd.DataFrame:
    """
    Create fact_goalie_game_stats.
    
    v29.4: Now uses GoalieStatsBuilder for better organization and testability.
    """
    from src.builders.goalie_stats import build_fact_goalie_game_stats
    return build_fact_goalie_game_stats(save=False)  # Save handled by create_all_core_facts


def _create_fact_goalie_game_stats_original() -> pd.DataFrame:
    """Create fact_goalie_game_stats with comprehensive advanced goalie metrics.
    
    v28.1 - EXPANDED with ~90 columns including:
    - Rebound control advanced (12 cols)
    - Period splits (15 cols)
    - Time bucket / clutch (12 cols)
    - Shot context / rush vs set play (12 cols)
    - Pressure / sequence handling (10 cols)
    - Body location / technique (10 cols)
    - Workload metrics (10 cols)
    - Advanced composites (10 cols)
    """
    print("\nBuilding fact_goalie_game_stats (v28.1 - ADVANCED GOALIE ANALYTICS)...")
    
    events = load_table('fact_events')
    roster = load_table('fact_gameroster')
    players = load_table('dim_player')
    
    # Try to load fact_saves for detailed save-level data
    try:
        fact_saves = load_table('fact_saves')
        has_fact_saves = len(fact_saves) > 0
    except:
        fact_saves = pd.DataFrame()
        has_fact_saves = False
    
    if len(events) == 0:
        print("  ERROR: fact_events not found!")
        return pd.DataFrame()
    
    tracked_game_ids = events['game_id'].dropna().unique().tolist()
    roster_tracked = roster[roster['game_id'].isin(tracked_game_ids)]
    
    pos_col = 'player_position' if 'player_position' in roster_tracked.columns else 'position'
    if pos_col not in roster_tracked.columns:
        print("  No position column found")
        return pd.DataFrame()
    
    goalies = roster_tracked[roster_tracked[pos_col].astype(str).str.lower().str.contains('goalie', na=False)]
    
    if len(goalies) == 0:
        print("  No goalies found")
        return pd.DataFrame()
    
    all_stats = []
    
    for _, goalie in goalies.iterrows():
        game_id = goalie['game_id']
        player_id = goalie['player_id']
        
        stats = {
            'goalie_game_key': f"GK{game_id}{player_id}",
            'game_id': game_id,
            'player_id': player_id,
            '_export_timestamp': datetime.now().isoformat(),
        }
        
        if len(players) > 0:
            player_info = players[players['player_id'] == player_id]
            stats['player_name'] = player_info['player_full_name'].values[0] if len(player_info) > 0 else ''
        
        stats['team_name'] = goalie.get('team_name', '')
        stats['team_id'] = goalie.get('team_id', '')
        
        game_events = events[events['game_id'] == game_id]
        
        goalie_team_id = goalie.get('team_id')
        home_team_id = game_events['home_team_id'].iloc[0] if len(game_events) > 0 and 'home_team_id' in game_events.columns else None
        is_home = (str(goalie_team_id) == str(home_team_id)) if goalie_team_id and home_team_id else None
        stats['is_home'] = is_home
        
        all_saves_events = game_events[game_events['event_type'].astype(str).str.lower() == 'save']
        all_goals = game_events[is_goal_scored(game_events)]
        all_rebounds = game_events[game_events['event_type'].astype(str).str.lower() == 'rebound']
        
        if is_home is not None and 'team_venue' in game_events.columns:
            goalie_venue = 'h' if is_home else 'a'
            opp_venue = 'a' if is_home else 'h'
            
            # Get this goalie's saves
            goalie_saves = all_saves_events[all_saves_events['team_venue'].astype(str).str.lower() == goalie_venue]
            goalie_goals_against = all_goals[all_goals['team_venue'].astype(str).str.lower() == opp_venue]
            
            # Also get detailed saves from fact_saves if available
            if has_fact_saves:
                detailed_saves = fact_saves[(fact_saves['game_id'] == game_id) & 
                                           (fact_saves['team_venue'].astype(str).str.lower() == goalie_venue)]
            else:
                detailed_saves = goalie_saves
            
            # ================================================================
            # CORE STATS
            # ================================================================
            stats['saves'] = len(goalie_saves)
            stats['goals_against'] = len(goalie_goals_against)
            stats['shots_against'] = stats['saves'] + stats['goals_against']
            stats['save_pct'] = round(stats['saves'] / stats['shots_against'] * 100, 1) if stats['shots_against'] > 0 else 100.0
            
            # ================================================================
            # SAVE TYPE BREAKDOWN (existing)
            # ================================================================
            if 'event_detail_2' in goalie_saves.columns:
                save_types = goalie_saves['event_detail_2'].astype(str).str.lower()
                stats['saves_butterfly'] = len(save_types[save_types.str.contains('butterfly', na=False)])
                stats['saves_pad'] = len(save_types[save_types.str.contains('pad', na=False)])
                stats['saves_glove'] = len(save_types[save_types.str.contains('glove', na=False)])
                stats['saves_blocker'] = len(save_types[save_types.str.contains('blocker', na=False)])
                stats['saves_chest'] = len(save_types[save_types.str.contains('chest|shoulder', na=False)])
                stats['saves_stick'] = len(save_types[save_types.str.contains('stick', na=False)])
                stats['saves_scramble'] = len(save_types[save_types.str.contains('scramble', na=False)])
            else:
                for st in ['saves_butterfly', 'saves_pad', 'saves_glove', 'saves_blocker', 'saves_chest', 'saves_stick', 'saves_scramble']:
                    stats[st] = 0
            
            # ================================================================
            # HIGH DANGER SAVES (existing)
            # ================================================================
            opp_shots = game_events[(game_events['team_venue'].astype(str).str.lower() == opp_venue) & 
                                   (game_events['event_type'].astype(str).str.lower().isin(['shot', 'goal']))]
            if 'danger_level' in opp_shots.columns:
                hd = opp_shots[opp_shots['danger_level'].astype(str).str.lower() == 'high']
                hd_goals = len(hd[hd['event_type'].astype(str).str.lower() == 'goal'])
                stats['hd_shots_against'] = len(hd)
                stats['hd_goals_against'] = hd_goals
                stats['hd_saves'] = len(hd) - hd_goals
                stats['hd_save_pct'] = round(stats['hd_saves'] / len(hd) * 100, 1) if len(hd) > 0 else 100.0
            else:
                stats['hd_shots_against'] = stats['hd_goals_against'] = stats['hd_saves'] = 0
                stats['hd_save_pct'] = 100.0
            
            # ================================================================
            # CATEGORY 1: REBOUND CONTROL ADVANCED (12 columns)
            # ================================================================
            # Use event_detail to get freeze vs rebound from saves
            if 'event_detail' in goalie_saves.columns:
                save_details = goalie_saves['event_detail'].astype(str)
                stats['saves_freeze'] = len(save_details[save_details.str.contains('Freeze', na=False, case=False)])
                stats['saves_rebound'] = len(save_details[save_details.str.contains('Rebound', na=False, case=False)])
            else:
                stats['saves_freeze'] = stats.get('saves_glove', 0) + stats.get('saves_chest', 0)
                stats['saves_rebound'] = stats['saves'] - stats['saves_freeze']
            
            stats['freeze_pct'] = round(stats['saves_freeze'] / stats['saves'] * 100, 1) if stats['saves'] > 0 else 0.0
            stats['rebound_rate'] = round(stats['saves_rebound'] / stats['saves'] * 100, 1) if stats['saves'] > 0 else 0.0
            
            # Analyze rebound outcomes from Rebound events
            # v28.1 FIX: Link rebounds to specific goalies via prev_event_id -> Save events
            if 'prev_event_id' in all_rebounds.columns and 'event_id' in goalie_saves.columns:
                # Get the event_ids of this goalie's saves
                goalie_save_ids = set(goalie_saves['event_id'].astype(str).tolist())
                # Filter rebounds to those that followed THIS goalie's saves
                goalie_rebounds = all_rebounds[all_rebounds['prev_event_id'].astype(str).isin(goalie_save_ids)]
            else:
                # Fallback: Use all rebounds (game-level, less accurate)
                goalie_rebounds = all_rebounds
            
            if 'event_detail' in goalie_rebounds.columns and len(goalie_rebounds) > 0:
                rebound_details = goalie_rebounds['event_detail'].astype(str)
                stats['rebounds_team_recovered'] = len(rebound_details[rebound_details.str.contains('TeamRecovered', na=False)])
                stats['rebounds_opp_recovered'] = len(rebound_details[rebound_details.str.contains('OppTeamRecovered', na=False)])
                stats['rebounds_shot_generated'] = len(rebound_details[rebound_details.str.contains('ShotGenerated', na=False)])
                stats['rebounds_flurry_generated'] = len(rebound_details[rebound_details.str.contains('Flurry', na=False)])
            else:
                stats['rebounds_team_recovered'] = stats['rebounds_opp_recovered'] = 0
                stats['rebounds_shot_generated'] = stats['rebounds_flurry_generated'] = 0
            
            total_rebounds = stats['rebounds_team_recovered'] + stats['rebounds_opp_recovered'] + stats['rebounds_shot_generated'] + stats['rebounds_flurry_generated']
            stats['rebound_control_rate'] = round(stats['rebounds_team_recovered'] / total_rebounds * 100, 1) if total_rebounds > 0 else 100.0
            stats['rebound_danger_rate'] = round((stats['rebounds_shot_generated'] + stats['rebounds_flurry_generated']) / total_rebounds * 100, 1) if total_rebounds > 0 else 0.0
            
            # Second chance analysis (shots/goals after rebounds)
            stats['second_chance_shots_against'] = stats['rebounds_shot_generated'] + stats['rebounds_flurry_generated']
            # For goals, we'd need to track which goals came after rebounds - estimate as 0 for now
            stats['second_chance_goals_against'] = 0  # Would need sequence analysis
            stats['second_chance_sv_pct'] = 100.0 if stats['second_chance_shots_against'] == 0 else round((stats['second_chance_shots_against'] - stats['second_chance_goals_against']) / stats['second_chance_shots_against'] * 100, 1)
            
            stats['dangerous_rebound_pct'] = stats['rebound_danger_rate']
            
            # ================================================================
            # CATEGORY 2: PERIOD SPLITS (15 columns)
            # ================================================================
            for period in [1, 2, 3]:
                p_saves = len(goalie_saves[goalie_saves['period'] == period])
                p_ga = len(goalie_goals_against[goalie_goals_against['period'] == period])
                p_sa = p_saves + p_ga
                p_sv_pct = round(p_saves / p_sa * 100, 1) if p_sa > 0 else 100.0
                
                stats[f'p{period}_saves'] = p_saves
                stats[f'p{period}_goals_against'] = p_ga
                stats[f'p{period}_shots_against'] = p_sa
                stats[f'p{period}_sv_pct'] = p_sv_pct
            
            # Best/worst period
            period_sv_pcts = {1: stats['p1_sv_pct'], 2: stats['p2_sv_pct'], 3: stats['p3_sv_pct']}
            period_sas = {1: stats['p1_shots_against'], 2: stats['p2_shots_against'], 3: stats['p3_shots_against']}
            
            # Only consider periods with shots
            active_periods = {p: sv for p, sv in period_sv_pcts.items() if period_sas[p] > 0}
            if active_periods:
                stats['best_period'] = max(active_periods, key=active_periods.get)
                stats['worst_period'] = min(active_periods, key=active_periods.get)
                sv_pct_values = list(active_periods.values())
                stats['period_consistency'] = round(np.std(sv_pct_values), 2) if len(sv_pct_values) > 1 else 0.0
            else:
                stats['best_period'] = stats['worst_period'] = 0
                stats['period_consistency'] = 0.0
            
            # ================================================================
            # CATEGORY 3: TIME BUCKET / CLUTCH (12 columns)
            # ================================================================
            if 'time_bucket_id' in detailed_saves.columns:
                # TB01 = early (0-5), TB02/TB03 = mid (5-15), TB04/TB05 = late (15-20)
                early_saves = detailed_saves[detailed_saves['time_bucket_id'] == 'TB01']
                mid_saves = detailed_saves[detailed_saves['time_bucket_id'].isin(['TB02', 'TB03'])]
                late_saves = detailed_saves[detailed_saves['time_bucket_id'].isin(['TB04', 'TB05'])]
                final_min_saves = detailed_saves[detailed_saves['time_bucket_id'] == 'TB05']
                
                stats['early_period_saves'] = len(early_saves)
                stats['mid_period_saves'] = len(mid_saves)
                stats['late_period_saves'] = len(late_saves)
                stats['final_minute_saves'] = len(final_min_saves)
            else:
                stats['early_period_saves'] = stats['mid_period_saves'] = stats['late_period_saves'] = stats['final_minute_saves'] = 0
            
            # For GA by time bucket, use goals_against events
            if 'time_bucket_id' in goalie_goals_against.columns:
                stats['early_period_ga'] = len(goalie_goals_against[goalie_goals_against['time_bucket_id'] == 'TB01'])
                stats['mid_period_ga'] = len(goalie_goals_against[goalie_goals_against['time_bucket_id'].isin(['TB02', 'TB03'])])
                stats['late_period_ga'] = len(goalie_goals_against[goalie_goals_against['time_bucket_id'].isin(['TB04', 'TB05'])])
                stats['final_minute_ga'] = len(goalie_goals_against[goalie_goals_against['time_bucket_id'] == 'TB05'])
            else:
                stats['early_period_ga'] = stats['mid_period_ga'] = stats['late_period_ga'] = stats['final_minute_ga'] = 0
            
            # Calculate SV% for each time bucket
            for bucket in ['early_period', 'mid_period', 'late_period', 'final_minute']:
                sv = stats[f'{bucket}_saves']
                ga = stats[f'{bucket}_ga']
                sa = sv + ga
                stats[f'{bucket}_sv_pct'] = round(sv / sa * 100, 1) if sa > 0 else 100.0
            
            # ================================================================
            # CATEGORY 4: SHOT CONTEXT - RUSH VS SET PLAY (12 columns)
            # ================================================================
            if 'time_since_zone_entry' in detailed_saves.columns:
                tsze = detailed_saves['time_since_zone_entry'].fillna(999)
                rush_saves_df = detailed_saves[tsze < 5]
                quick_attack_df = detailed_saves[(tsze >= 5) & (tsze < 10)]
                set_play_df = detailed_saves[tsze >= 10]
                
                stats['rush_saves'] = len(rush_saves_df)
                stats['quick_attack_saves'] = len(quick_attack_df)
                stats['set_play_saves'] = len(set_play_df)
                stats['avg_time_from_entry'] = round(detailed_saves['time_since_zone_entry'].mean(), 1) if len(detailed_saves) > 0 else 0.0
            else:
                stats['rush_saves'] = stats['quick_attack_saves'] = stats['set_play_saves'] = 0
                stats['avg_time_from_entry'] = 0.0
            
            # GA by shot context - NOW USING ACTUAL DATA (time_since_zone_entry on goals)
            if 'time_since_zone_entry' in goalie_goals_against.columns:
                ga_tsze = goalie_goals_against['time_since_zone_entry'].fillna(999)
                stats['rush_goals_against'] = len(goalie_goals_against[ga_tsze < 5])
                stats['quick_attack_ga'] = len(goalie_goals_against[(ga_tsze >= 5) & (ga_tsze < 10)])
                stats['set_play_ga'] = len(goalie_goals_against[ga_tsze >= 10])
            else:
                stats['rush_goals_against'] = 0
                stats['quick_attack_ga'] = 0
                stats['set_play_ga'] = 0
            
            # SV% by context - NOW CALCULATED WITH REAL GA DATA
            rush_sa = stats['rush_saves'] + stats['rush_goals_against']
            quick_sa = stats['quick_attack_saves'] + stats['quick_attack_ga']
            set_sa = stats['set_play_saves'] + stats['set_play_ga']
            
            stats['rush_sv_pct'] = round(stats['rush_saves'] / rush_sa * 100, 1) if rush_sa > 0 else 100.0
            stats['quick_attack_sv_pct'] = round(stats['quick_attack_saves'] / quick_sa * 100, 1) if quick_sa > 0 else 100.0
            stats['set_play_sv_pct'] = round(stats['set_play_saves'] / set_sa * 100, 1) if set_sa > 0 else 100.0
            
            stats['rush_pct_of_shots'] = round((stats['rush_saves'] + stats['rush_goals_against']) / stats['shots_against'] * 100, 1) if stats['shots_against'] > 0 else 0.0
            stats['transition_defense_rating'] = round(stats['rush_sv_pct'] - stats['set_play_sv_pct'], 1)
            
            # ================================================================
            # CATEGORY 5: PRESSURE / SEQUENCE HANDLING (10 columns)
            # ================================================================
            if 'sequence_shot_count' in detailed_saves.columns:
                seq_counts = detailed_saves['sequence_shot_count'].fillna(0)
                single_shot = detailed_saves[seq_counts <= 1]
                multi_shot = detailed_saves[seq_counts >= 2]
                sustained = detailed_saves[seq_counts >= 4]
                
                stats['single_shot_saves'] = len(single_shot)
                stats['multi_shot_saves'] = len(multi_shot)
                stats['sustained_pressure_saves'] = len(sustained)
                stats['max_sequence_faced'] = int(seq_counts.max()) if len(seq_counts) > 0 else 0
                stats['avg_sequence_length'] = round(seq_counts.mean(), 1) if len(seq_counts) > 0 else 0.0
            else:
                stats['single_shot_saves'] = stats['saves']
                stats['multi_shot_saves'] = 0
                stats['sustained_pressure_saves'] = 0
                stats['max_sequence_faced'] = 1
                stats['avg_sequence_length'] = 1.0
            
            # SV% under pressure - NOW USING ACTUAL SEQUENCE DATA FROM GOALS
            if 'sequence_shot_count' in goalie_goals_against.columns:
                ga_seq = goalie_goals_against['sequence_shot_count'].fillna(0)
                multi_shot_ga = len(goalie_goals_against[ga_seq >= 2])
                sustained_ga = len(goalie_goals_against[ga_seq >= 4])
            else:
                multi_shot_ga = 0
                sustained_ga = 0
            
            multi_shot_sa = stats['multi_shot_saves'] + multi_shot_ga
            sustained_sa = stats['sustained_pressure_saves'] + sustained_ga
            
            stats['multi_shot_sv_pct'] = round(stats['multi_shot_saves'] / multi_shot_sa * 100, 1) if multi_shot_sa > 0 else 100.0
            stats['sustained_pressure_sv_pct'] = round(stats['sustained_pressure_saves'] / sustained_sa * 100, 1) if sustained_sa > 0 else 100.0
            
            # Sequence survival (% of sequences with 0 GA)
            stats['sequence_survival_rate'] = round((stats['saves'] - stats['goals_against']) / stats['saves'] * 100, 1) if stats['saves'] > 0 else 100.0
            stats['pressure_handling_index'] = round((stats['multi_shot_sv_pct'] + stats['sustained_pressure_sv_pct']) / 2, 1)
            
            # ================================================================
            # CATEGORY 6: BODY LOCATION / TECHNIQUE (10 columns)
            # ================================================================
            # Glove side = Save_Glove + Save_LeftPad
            stats['glove_side_saves'] = stats.get('saves_glove', 0) + len(goalie_saves[goalie_saves['event_detail_2'].astype(str).str.contains('LeftPad', na=False, case=False)]) if 'event_detail_2' in goalie_saves.columns else 0
            stats['blocker_side_saves'] = stats.get('saves_blocker', 0) + len(goalie_saves[goalie_saves['event_detail_2'].astype(str).str.contains('RightPad', na=False, case=False)]) if 'event_detail_2' in goalie_saves.columns else 0
            stats['five_hole_saves'] = stats.get('saves_butterfly', 0) + stats.get('saves_scramble', 0)
            
            # GA by location (would need goal-level data)
            stats['glove_side_ga'] = 0
            stats['blocker_side_ga'] = 0
            stats['five_hole_ga'] = 0
            
            # SV% by location
            stats['glove_side_sv_pct'] = round(stats['glove_side_saves'] / (stats['glove_side_saves'] + stats['glove_side_ga']) * 100, 1) if (stats['glove_side_saves'] + stats['glove_side_ga']) > 0 else 100.0
            stats['blocker_side_sv_pct'] = round(stats['blocker_side_saves'] / (stats['blocker_side_saves'] + stats['blocker_side_ga']) * 100, 1) if (stats['blocker_side_saves'] + stats['blocker_side_ga']) > 0 else 100.0
            stats['five_hole_sv_pct'] = round(stats['five_hole_saves'] / (stats['five_hole_saves'] + stats['five_hole_ga']) * 100, 1) if (stats['five_hole_saves'] + stats['five_hole_ga']) > 0 else 100.0
            
            stats['side_preference_ratio'] = round(stats['glove_side_saves'] / stats['blocker_side_saves'], 2) if stats['blocker_side_saves'] > 0 else 1.0
            
            # ================================================================
            # CATEGORY 7: WORKLOAD METRICS (10 columns)
            # ================================================================
            stats['shots_per_period'] = round(stats['shots_against'] / 3, 1)
            stats['saves_per_period'] = round(stats['saves'] / 3, 1)
            stats['max_shots_in_period'] = max(stats['p1_shots_against'], stats['p2_shots_against'], stats['p3_shots_against'])
            
            # Shot volume variance
            period_shots = [stats['p1_shots_against'], stats['p2_shots_against'], stats['p3_shots_against']]
            stats['shot_volume_variance'] = round(np.std(period_shots), 2) if sum(period_shots) > 0 else 0.0
            
            # Time between shots analysis
            if 'time_since_last_sog' in detailed_saves.columns:
                time_gaps = detailed_saves['time_since_last_sog'].dropna()
                stats['time_between_shots_avg'] = round(time_gaps.mean(), 1) if len(time_gaps) > 0 else 0.0
                stats['time_between_shots_min'] = round(time_gaps.min(), 1) if len(time_gaps) > 0 else 0.0
                stats['rapid_fire_saves'] = len(time_gaps[time_gaps < 3])
            else:
                stats['time_between_shots_avg'] = 0.0
                stats['time_between_shots_min'] = 0.0
                stats['rapid_fire_saves'] = 0
            
            # Consecutive saves (estimate based on GA distribution)
            stats['consecutive_saves_max'] = stats['saves'] // max(1, stats['goals_against']) if stats['goals_against'] > 0 else stats['saves']
            
            # Workload index (composite)
            stats['workload_index'] = round(stats['shots_against'] * (1 + stats['shot_volume_variance'] / 10), 1)
            
            # Fatigue-adjusted GSAA (penalize high workload slightly)
            fatigue_factor = 1.0 - (stats['shots_against'] - 20) * 0.005 if stats['shots_against'] > 20 else 1.0
            stats['fatigue_adjusted_gsaa'] = round(stats.get('goals_saved_above_avg', 0) * fatigue_factor, 2)
            
            # ================================================================
            # QUALITY INDICATORS (existing, enhanced)
            # ================================================================
            stats['is_quality_start'] = 1 if (stats['save_pct'] >= 91.7 or stats['goals_against'] <= 2) else 0
            stats['is_bad_start'] = 1 if stats['save_pct'] < 85.0 else 0
            
            # GSAx (existing)
            expected = stats['shots_against'] * (1 - LEAGUE_AVG_SV_PCT / 100)
            stats['expected_goals_against'] = round(expected, 2)
            stats['goals_saved_above_avg'] = round(expected - stats['goals_against'], 2)
            
            # ================================================================
            # CATEGORY 8: ADVANCED COMPOSITES (10 columns)
            # ================================================================
            # Goalie Game Score (inspired by Dom Luszczyszyn)
            # Base: saves * 0.1 - GA * 0.75 + shutout bonus
            shutout_bonus = 2.0 if stats['goals_against'] == 0 else 0.0
            stats['goalie_game_score'] = round(stats['saves'] * 0.1 - stats['goals_against'] * 0.75 + shutout_bonus + stats['hd_saves'] * 0.2, 2)
            
            # Simple xG model: rush shots worth more, HD shots worth more
            rush_xg = stats['rush_saves'] * 0.15 + stats['rush_goals_against'] * 1.0
            set_xg = stats['set_play_saves'] * 0.08 + stats['set_play_ga'] * 1.0
            hd_xg = stats['hd_shots_against'] * 0.25
            stats['goalie_gax'] = round(rush_xg + set_xg + hd_xg * 0.5, 2)  # Expected GA
            stats['goalie_gsax'] = round(stats['goalie_gax'] - stats['goals_against'], 2)  # Goals Saved Above Expected
            
            # Clutch rating (P3 + late period performance weighted)
            stats['clutch_rating'] = round((stats['p3_sv_pct'] * 0.4 + stats['late_period_sv_pct'] * 0.3 + stats['final_minute_sv_pct'] * 0.3), 1)
            
            # Consistency rating (inverse of variance)
            stats['consistency_rating'] = round(100 - stats['period_consistency'] * 2, 1)
            
            # Pressure rating
            stats['pressure_rating'] = stats['pressure_handling_index']
            
            # Rebound rating
            stats['rebound_rating'] = round(stats['freeze_pct'] * 0.4 + stats['rebound_control_rate'] * 0.4 + (100 - stats['rebound_danger_rate']) * 0.2, 1)
            
            # Positioning rating (based on save technique distribution - more controlled = better)
            controlled_saves = stats.get('saves_glove', 0) + stats.get('saves_blocker', 0) + stats.get('saves_chest', 0)
            stats['positioning_rating'] = round(controlled_saves / stats['saves'] * 100, 1) if stats['saves'] > 0 else 50.0
            
            # Overall game rating (1-10 scale)
            raw_rating = (stats['save_pct'] - 80) / 4  # 80% = 0, 100% = 5
            raw_rating += stats['goalie_gsax'] * 0.5  # GSAX bonus
            raw_rating += shutout_bonus * 0.5
            stats['overall_game_rating'] = round(max(1, min(10, raw_rating + 5)), 1)  # Scale to 1-10
            
            # Win probability added (simplified)
            stats['win_probability_added'] = round(stats['goals_saved_above_avg'] * 0.05, 3)
            
            # ================================================================
            # GOALIE WAR (existing, updated)
            # ================================================================
            war_stats = calculate_goalie_war(stats)
            stats.update(war_stats)
            
        else:
            # Fallback for missing venue data
            stats['saves'] = len(all_saves_events) // 2
            stats['goals_against'] = len(all_goals) // 2
            stats['shots_against'] = stats['saves'] + stats['goals_against']
            stats['save_pct'] = round(stats['saves'] / stats['shots_against'] * 100, 1) if stats['shots_against'] > 0 else 100.0
            
            # Set all advanced stats to defaults
            for col in ['saves_butterfly', 'saves_pad', 'saves_glove', 'saves_blocker', 'saves_chest', 'saves_stick', 'saves_scramble']:
                stats[col] = 0
            for col in ['hd_shots_against', 'hd_goals_against', 'hd_saves']:
                stats[col] = 0
            stats['hd_save_pct'] = 100.0
            
            # Rebound control defaults
            stats['saves_freeze'] = stats['saves_rebound'] = 0
            stats['freeze_pct'] = stats['rebound_rate'] = 0.0
            stats['rebounds_team_recovered'] = stats['rebounds_opp_recovered'] = 0
            stats['rebounds_shot_generated'] = stats['rebounds_flurry_generated'] = 0
            stats['rebound_control_rate'] = 100.0
            stats['rebound_danger_rate'] = 0.0
            stats['second_chance_shots_against'] = stats['second_chance_goals_against'] = 0
            stats['second_chance_sv_pct'] = 100.0
            stats['dangerous_rebound_pct'] = 0.0
            
            # Period splits defaults
            for p in [1, 2, 3]:
                stats[f'p{p}_saves'] = stats[f'p{p}_goals_against'] = stats[f'p{p}_shots_against'] = 0
                stats[f'p{p}_sv_pct'] = 100.0
            stats['best_period'] = stats['worst_period'] = 0
            stats['period_consistency'] = 0.0
            
            # Time bucket defaults
            for tb in ['early_period', 'mid_period', 'late_period', 'final_minute']:
                stats[f'{tb}_saves'] = stats[f'{tb}_ga'] = 0
                stats[f'{tb}_sv_pct'] = 100.0
            
            # Shot context defaults
            stats['rush_saves'] = stats['quick_attack_saves'] = stats['set_play_saves'] = 0
            stats['rush_goals_against'] = stats['quick_attack_ga'] = stats['set_play_ga'] = 0
            stats['rush_sv_pct'] = stats['quick_attack_sv_pct'] = stats['set_play_sv_pct'] = 100.0
            stats['avg_time_from_entry'] = 0.0
            stats['rush_pct_of_shots'] = 0.0
            stats['transition_defense_rating'] = 0.0
            
            # Pressure defaults
            stats['single_shot_saves'] = stats['saves']
            stats['multi_shot_saves'] = stats['sustained_pressure_saves'] = 0
            stats['multi_shot_sv_pct'] = stats['sustained_pressure_sv_pct'] = 100.0
            stats['max_sequence_faced'] = 1
            stats['avg_sequence_length'] = 1.0
            stats['sequence_survival_rate'] = 100.0
            stats['pressure_handling_index'] = 100.0
            
            # Body location defaults
            stats['glove_side_saves'] = stats['blocker_side_saves'] = stats['five_hole_saves'] = 0
            stats['glove_side_ga'] = stats['blocker_side_ga'] = stats['five_hole_ga'] = 0
            stats['glove_side_sv_pct'] = stats['blocker_side_sv_pct'] = stats['five_hole_sv_pct'] = 100.0
            stats['side_preference_ratio'] = 1.0
            
            # Workload defaults
            stats['shots_per_period'] = stats['saves_per_period'] = 0.0
            stats['max_shots_in_period'] = 0
            stats['shot_volume_variance'] = 0.0
            stats['time_between_shots_avg'] = stats['time_between_shots_min'] = 0.0
            stats['rapid_fire_saves'] = 0
            stats['consecutive_saves_max'] = 0
            stats['workload_index'] = 0.0
            stats['fatigue_adjusted_gsaa'] = 0.0
            
            # Quality indicators
            stats['is_quality_start'] = 0
            stats['is_bad_start'] = 0
            stats['expected_goals_against'] = 0.0
            stats['goals_saved_above_avg'] = 0.0
            
            # Composites defaults
            stats['goalie_game_score'] = 0.0
            stats['goalie_gax'] = stats['goalie_gsax'] = 0.0
            stats['clutch_rating'] = 50.0
            stats['consistency_rating'] = 50.0
            stats['pressure_rating'] = 50.0
            stats['rebound_rating'] = 50.0
            stats['positioning_rating'] = 50.0
            stats['overall_game_rating'] = 5.0
            stats['win_probability_added'] = 0.0
            
            war_stats = calculate_goalie_war(stats)
            stats.update(war_stats)
        
        all_stats.append(stats)
    
    df = pd.DataFrame(all_stats)
    print(f"  Created {len(df)} goalie-game records with {len(df.columns)} columns")
    return df


def create_all_core_facts():
    """Create all core fact tables."""
    print("\n" + "=" * 70)
    print("CREATING CORE FACT TABLES (v26.1 - Phase 3 Expansion)")
    print("=" * 70)
    
    results = {}
    
    df = create_fact_player_game_stats()
    if len(df) > 0:
        results['fact_player_game_stats'] = save_table(df, 'fact_player_game_stats')
        print(f"  ✓ fact_player_game_stats: {results['fact_player_game_stats']} rows, {len(df.columns)} cols")
    
    df = create_fact_team_game_stats()
    if len(df) > 0:
        results['fact_team_game_stats'] = save_table(df, 'fact_team_game_stats')
        print(f"  ✓ fact_team_game_stats: {results['fact_team_game_stats']} rows")
    
    df = create_fact_goalie_game_stats()
    if len(df) > 0:
        results['fact_goalie_game_stats'] = save_table(df, 'fact_goalie_game_stats')
        print(f"  ✓ fact_goalie_game_stats: {results['fact_goalie_game_stats']} rows, {len(df.columns)} cols")
    
    print(f"\n✅ Created {len(results)} core fact tables")
    return results


if __name__ == "__main__":
    create_all_core_facts()
