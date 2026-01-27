#!/usr/bin/env python3
"""
BenchSight Shift Analytics Tables Builder
Creates H2H, WOWY, Line Combos, and Shift Quality tables.

These tables analyze shift-level data for player combinations and matchups.

Tables created:
- fact_h2h (head-to-head: players on ice together)
- fact_wowy (with-or-without-you analysis)
- fact_line_combos (forward/defense combinations)
- fact_shift_quality (per-shift quality scores)
- fact_shift_quality_logical (aggregated shift quality)

Usage:
    from src.tables.shift_analytics import create_all_shift_analytics
    create_all_shift_analytics()
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from itertools import combinations

OUTPUT_DIR = Path('data/output')


def add_names_to_table(df: pd.DataFrame) -> pd.DataFrame:
    """Add player_name and team_name columns where player_id/team_id exist."""
    if df is None or len(df) == 0:
        return df
    df = df.copy()
    dim_player = load_table('dim_player') if len(df) > 0 else None
    dim_team = load_table('dim_team') if len(df) > 0 else None
    
    # Add player names
    if dim_player is not None and len(dim_player) > 0:
        player_map = dim_player.set_index('player_id')['player_full_name'].to_dict()
        if 'player_full_name' not in dim_player.columns and 'player_name' in dim_player.columns:
            player_map = dim_player.set_index('player_id')['player_name'].to_dict()
        
        for col_map in [('player_id', 'player_name'), ('player_1_id', 'player_1_name'), 
                        ('player_2_id', 'player_2_name')]:
            id_col, name_col = col_map
            if id_col in df.columns and name_col not in df.columns:
                df[name_col] = df[id_col].map(player_map)
    
    # Add team names
    if dim_team is not None and len(dim_team) > 0:
        team_map = dim_team.set_index('team_id')['team_name'].to_dict()
        for col_map in [('team_id', 'team_name'), ('home_team_id', 'home_team_name'),
                        ('away_team_id', 'away_team_name')]:
            id_col, name_col = col_map
            if id_col in df.columns and name_col not in df.columns:
                df[name_col] = df[id_col].map(team_map)
    
    return df

def save_table(df: pd.DataFrame, name: str) -> int:
    """
    Save table to CSV and return row count. Automatically adds name columns.
    Automatically removes 100% null columns (except coordinate/danger/xy columns).
    """
    if df is not None and len(df) > 0:
        df = add_names_to_table(df)
        from src.core.base_etl import drop_all_null_columns
        df, removed_cols = drop_all_null_columns(df)
        if removed_cols:
            print(f"  {name}: Removed {len(removed_cols)} all-null columns")
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
    except Exception:
        pass
    
    # Fall back to CSV (for tables from previous runs)
    path = OUTPUT_DIR / f"{name}.csv"
    if path.exists():
        try:
            df = pd.read_csv(path, low_memory=False)
            if len(df) == 0 and required:
                print(f"  WARNING: {name} exists but is EMPTY (required dependency)")
            return df
        except Exception as e:
            if required:
                print(f"  ERROR: Failed to load {name}: {e}")
            return pd.DataFrame()
    else:
        if required:
            print(f"  WARNING: Required table {name} not found - table will be empty")
        return pd.DataFrame()


def get_players_on_shift(shift_row: pd.Series, venue: str) -> list:
    """
    Extract player numbers from a shift row for a given venue (home/away).
    
    Shift columns: home_forward_1/2/3, home_defense_1/2, home_goalie, home_xtra
    """
    players = []
    prefix = venue.lower()
    
    position_cols = [
        f'{prefix}_forward_1', f'{prefix}_forward_2', f'{prefix}_forward_3',
        f'{prefix}_defense_1', f'{prefix}_defense_2', f'{prefix}_goalie', f'{prefix}_xtra'
    ]
    
    for col in position_cols:
        if col in shift_row.index:
            val = shift_row[col]
            if pd.notna(val) and str(val) not in ['', 'nan', 'None']:
                try:
                    players.append(int(float(val)))
                except (ValueError, TypeError):
                    pass
    
    return players


def create_fact_h2h() -> pd.DataFrame:
    """
    Create head-to-head analysis: players on ice together.
    
    Uses fact_shift_players with logical_shift_number to properly count
    shifts and aggregate stats when players were on ice together.
    
    For each game, analyze which players were on ice together during the same
    logical shifts and calculate combined stats from shift_players data.
    """
    print("\nBuilding fact_h2h...")
    
    shift_players = load_table('fact_shift_players')
    schedule = load_table('dim_schedule')
    players = load_table('dim_player')
    
    if len(shift_players) == 0:
        print("  ERROR: fact_shift_players not found!")
        return pd.DataFrame()
    
    # Ensure logical_shift_number exists
    if 'logical_shift_number' not in shift_players.columns:
        print("  WARNING: logical_shift_number not found in fact_shift_players!")
        print("  Falling back to shift_index for shift counting...")
        shift_players['logical_shift_number'] = shift_players.get('shift_index', shift_players.index)
    
    all_h2h = []
    
    # Process each game
    for game_id in shift_players['game_id'].unique():
        if pd.isna(game_id) or game_id == 99999:  # Skip test game
            continue
        
        game_sp = shift_players[shift_players['game_id'] == game_id].copy()
        
        # Get season_id
        season_id = None
        if len(schedule) > 0:
            game_info = schedule[schedule['game_id'] == game_id]
            if len(game_info) > 0 and 'season_id' in game_info.columns:
                season_id = game_info['season_id'].values[0]
        
        # Process each venue (home, away)
        for venue in ['home', 'away']:
            venue_sp = game_sp[game_sp['venue'] == venue.lower()].copy()
            
            if len(venue_sp) == 0:
                continue
            
            # Group by logical_shift_number to find players on ice together
            # For each logical shift, get all players on that shift
            logical_shifts = venue_sp.groupby('logical_shift_number')
            
            # Build player pairs: (p1, p2) -> list of logical shift numbers they shared
            player_pairs = {}  # (p1, p2) -> dict of stats
            
            for logical_shift_num, shift_group in logical_shifts:
                if pd.isna(logical_shift_num):
                    continue
                
                # Get unique players on this logical shift
                players_on_shift = shift_group['player_id'].dropna().unique().tolist()
                
                if len(players_on_shift) < 2:
                    continue
                
                # Get stats for this logical shift (use first row - stats should be same for all players on same shift)
                shift_row = shift_group.iloc[0]
                
                # Use logical_shift_duration if available, else sum shift_duration
                if 'logical_shift_duration' in shift_group.columns and pd.notna(shift_row.get('logical_shift_duration')):
                    shift_duration = shift_row['logical_shift_duration']
                else:
                    # Sum all segments' duration for this logical shift (first segment only to avoid double counting)
                    first_segments = shift_group[shift_group.get('is_first_segment', pd.Series([True] * len(shift_group))) == True]
                    shift_duration = first_segments['shift_duration'].sum() if 'shift_duration' in first_segments.columns else 0
                
                # Get stats from shift_group (sum across all players, but each stat is per-shift so just use one row)
                shift_gf = int(shift_row.get('gf', 0)) if pd.notna(shift_row.get('gf')) else 0
                shift_ga = int(shift_row.get('ga', 0)) if pd.notna(shift_row.get('ga')) else 0
                shift_cf = int(shift_row.get('cf', 0)) if pd.notna(shift_row.get('cf')) else 0
                shift_ca = int(shift_row.get('ca', 0)) if pd.notna(shift_row.get('ca')) else 0
                shift_ff = int(shift_row.get('ff', 0)) if pd.notna(shift_row.get('ff')) else 0
                shift_fa = int(shift_row.get('fa', 0)) if pd.notna(shift_row.get('fa')) else 0
                
                # Create all pairs of players on this logical shift
                for p1, p2 in combinations(sorted(players_on_shift), 2):
                    # Ensure player IDs are strings for consistency
                    p1_str = str(p1)
                    p2_str = str(p2)
                    key = (p1_str, p2_str)
                    
                    if key not in player_pairs:
                        player_pairs[key] = {
                            'logical_shifts': set(),
                            'toi_together': 0,
                            'goals_for': 0,
                            'goals_against': 0,
                            'corsi_for': 0,
                            'corsi_against': 0,
                            'fenwick_for': 0,
                            'fenwick_against': 0,
                        }
                    
                    # Add this logical shift (avoid double counting same shift)
                    player_pairs[key]['logical_shifts'].add(logical_shift_num)
                    player_pairs[key]['toi_together'] += shift_duration
                    player_pairs[key]['goals_for'] += shift_gf
                    player_pairs[key]['goals_against'] += shift_ga
                    player_pairs[key]['corsi_for'] += shift_cf
                    player_pairs[key]['corsi_against'] += shift_ca
                    player_pairs[key]['fenwick_for'] += shift_ff
                    player_pairs[key]['fenwick_against'] += shift_fa
            
            # Create H2H records from aggregated pairs
            for (p1, p2), stats in player_pairs.items():
                shifts_together = len(stats['logical_shifts'])
                
                # Calculate percentages
                total_corsi = stats['corsi_for'] + stats['corsi_against']
                cf_pct = round(stats['corsi_for'] / total_corsi * 100, 2) if total_corsi > 0 else 50.0
                
                total_fenwick = stats['fenwick_for'] + stats['fenwick_against']
                ff_pct = round(stats['fenwick_for'] / total_fenwick * 100, 2) if total_fenwick > 0 else 50.0
                
                h2h = {
                    'h2h_key': f"H2H_{game_id}_{p1}_{p2}",
                    'game_id': game_id,
                    'season_id': season_id,
                    'player_1_id': p1,
                    'player_2_id': p2,
                    'venue': venue,
                    'shifts_together': shifts_together,
                    'toi_together': round(stats['toi_together'], 1),
                    'goals_for': stats['goals_for'],
                    'goals_against': stats['goals_against'],
                    'plus_minus': stats['goals_for'] - stats['goals_against'],
                    'corsi_for': stats['corsi_for'],
                    'corsi_against': stats['corsi_against'],
                    'cf_pct': cf_pct,
                    'fenwick_for': stats['fenwick_for'],
                    'fenwick_against': stats['fenwick_against'],
                    'ff_pct': ff_pct,
                }
                
                # Add player names if available
                if len(players) > 0:
                    p1_info = players[players['player_id'] == p1]
                    p2_info = players[players['player_id'] == p2]
                    if len(p1_info) > 0 and 'player_full_name' in p1_info.columns:
                        h2h['player_1_name'] = p1_info['player_full_name'].values[0]
                    if len(p2_info) > 0 and 'player_full_name' in p2_info.columns:
                        h2h['player_2_name'] = p2_info['player_full_name'].values[0]
                
                # Determine if same team (both same venue in same game)
                h2h['same_team'] = True  # By definition, players from same venue are same team
                
                all_h2h.append(h2h)
    
    df = pd.DataFrame(all_h2h)
    
    # Reorder columns for consistency
    priority_cols = ['h2h_key', 'game_id', 'season_id', 'player_1_id', 'player_1_name',
                    'player_2_id', 'player_2_name', 'same_team', 'venue',
                    'shifts_together', 'toi_together',
                    'goals_for', 'goals_against', 'plus_minus',
                    'corsi_for', 'corsi_against', 'cf_pct',
                    'fenwick_for', 'fenwick_against', 'ff_pct']
    other_cols = [c for c in df.columns if c not in priority_cols]
    df = df[[c for c in priority_cols if c in df.columns] + other_cols]
    
    print(f"  Created {len(df)} H2H records using logical shifts")
    return df


def create_fact_wowy() -> pd.DataFrame:
    """
    Create WOWY (With Or Without You) analysis.
    
    Compares player performance when together vs apart.
    Uses fact_shift_players with logical_shift_number for proper shift counting
    and to calculate real stats when players are apart.
    """
    print("\nBuilding fact_wowy...")
    
    shift_players = load_table('fact_shift_players')
    h2h = load_table('fact_h2h')  # Use H2H as base for together stats
    
    if len(h2h) == 0:
        print("  ERROR: fact_h2h not found! Run H2H first.")
        return pd.DataFrame()
    
    if len(shift_players) == 0:
        print("  ERROR: fact_shift_players not found!")
        return pd.DataFrame()
    
    # Ensure logical_shift_number exists
    if 'logical_shift_number' not in shift_players.columns:
        print("  WARNING: logical_shift_number not found in fact_shift_players!")
        print("  Falling back to shift_index for shift counting...")
        shift_players['logical_shift_number'] = shift_players.get('shift_index', shift_players.index)
    
    all_wowy = []
    
    # For each H2H pair, calculate with/without stats
    for _, row in h2h.iterrows():
        game_id = row['game_id']
        p1 = str(row['player_1_id'])
        p2 = str(row['player_2_id'])
        venue = row.get('venue', 'home').lower()
        
        # Get shift data for this game/venue
        game_sp = shift_players[
            (shift_players['game_id'] == game_id) & 
            (shift_players['venue'] == venue)
        ].copy()
        
        if len(game_sp) == 0:
            continue
        
        # Get logical shifts for each player
        p1_shifts = set(game_sp[game_sp['player_id'] == p1]['logical_shift_number'].dropna().unique())
        p2_shifts = set(game_sp[game_sp['player_id'] == p2]['logical_shift_number'].dropna().unique())
        
        # Logical shifts together (intersection)
        together_shifts = p1_shifts & p2_shifts
        
        # Logical shifts apart 
        p1_without_p2 = p1_shifts - p2_shifts
        p2_without_p1 = p2_shifts - p1_shifts
        
        # Use H2H stats for "together" (already calculated correctly)
        toi_together = row.get('toi_together', 0)
        cf_together = row.get('corsi_for', 0)
        ca_together = row.get('corsi_against', 0)
        gf_together = row.get('goals_for', 0)
        ga_together = row.get('goals_against', 0)
        cf_pct_together = row.get('cf_pct', 50.0)
        
        total_gf_together = gf_together + ga_together
        gf_pct_together = round(gf_together / total_gf_together * 100, 1) if total_gf_together > 0 else 50.0
        
        # Calculate stats for "apart" shifts from shift_players
        # Aggregate by logical shift (similar to H2H) - stats are shift-level, not player-level
        # Get all logical shifts where P1 is without P2
        p1_apart_logical_shifts = game_sp[
            game_sp['logical_shift_number'].isin(p1_without_p2)
        ].groupby('logical_shift_number')
        
        # Get all logical shifts where P2 is without P1
        p2_apart_logical_shifts = game_sp[
            game_sp['logical_shift_number'].isin(p2_without_p1)
        ].groupby('logical_shift_number')
        
        # Aggregate stats from logical shifts (use first row per logical shift for shift-level stats)
        p1_apart_cf = p1_apart_ca = p1_apart_gf = p1_apart_ga = 0
        toi_p1_without_p2 = 0
        
        for logical_shift_num, shift_group in p1_apart_logical_shifts:
            if pd.isna(logical_shift_num):
                continue
            
            # Get first row for this logical shift (shift-level stats are same for all players)
            shift_row = shift_group.iloc[0]
            
            # Use logical_shift_duration if available, else sum first segments
            if 'logical_shift_duration' in shift_group.columns and pd.notna(shift_row.get('logical_shift_duration')):
                shift_duration = shift_row['logical_shift_duration']
            else:
                # Sum first segments to avoid double-counting
                first_segments = shift_group[
                    shift_group.get('is_first_segment', pd.Series([True] * len(shift_group))) == True
                ]
                shift_duration = first_segments['shift_duration'].sum() if 'shift_duration' in first_segments.columns else 0
            
            toi_p1_without_p2 += shift_duration
            
            # Aggregate shift-level stats (same for all players on shift)
            if 'cf' in shift_row and pd.notna(shift_row.get('cf')):
                p1_apart_cf += int(shift_row['cf'])
            if 'ca' in shift_row and pd.notna(shift_row.get('ca')):
                p1_apart_ca += int(shift_row['ca'])
            if 'gf' in shift_row and pd.notna(shift_row.get('gf')):
                p1_apart_gf += int(shift_row['gf'])
            if 'ga' in shift_row and pd.notna(shift_row.get('ga')):
                p1_apart_ga += int(shift_row['ga'])
        
        p2_apart_cf = p2_apart_ca = p2_apart_gf = p2_apart_ga = 0
        toi_p2_without_p1 = 0
        
        for logical_shift_num, shift_group in p2_apart_logical_shifts:
            if pd.isna(logical_shift_num):
                continue
            
            # Get first row for this logical shift (shift-level stats are same for all players)
            shift_row = shift_group.iloc[0]
            
            # Use logical_shift_duration if available, else sum first segments
            if 'logical_shift_duration' in shift_group.columns and pd.notna(shift_row.get('logical_shift_duration')):
                shift_duration = shift_row['logical_shift_duration']
            else:
                # Sum first segments to avoid double-counting
                first_segments = shift_group[
                    shift_group.get('is_first_segment', pd.Series([True] * len(shift_group))) == True
                ]
                shift_duration = first_segments['shift_duration'].sum() if 'shift_duration' in first_segments.columns else 0
            
            toi_p2_without_p1 += shift_duration
            
            # Aggregate shift-level stats (same for all players on shift)
            if 'cf' in shift_row and pd.notna(shift_row.get('cf')):
                p2_apart_cf += int(shift_row['cf'])
            if 'ca' in shift_row and pd.notna(shift_row.get('ca')):
                p2_apart_ca += int(shift_row['ca'])
            if 'gf' in shift_row and pd.notna(shift_row.get('gf')):
                p2_apart_gf += int(shift_row['gf'])
            if 'ga' in shift_row and pd.notna(shift_row.get('ga')):
                p2_apart_ga += int(shift_row['ga'])
        
        # Total apart stats (sum of both players' apart shifts)
        cf_apart = p1_apart_cf + p2_apart_cf
        ca_apart = p1_apart_ca + p2_apart_ca
        gf_apart = p1_apart_gf + p2_apart_gf
        ga_apart = p1_apart_ga + p2_apart_ga
        
        # Calculate percentages for apart
        total_corsi_apart = cf_apart + ca_apart
        cf_pct_apart = round(cf_apart / total_corsi_apart * 100, 2) if total_corsi_apart > 0 else 50.0
        
        total_gf_apart = gf_apart + ga_apart
        gf_pct_apart = round(gf_apart / total_gf_apart * 100, 1) if total_gf_apart > 0 else 50.0
        
        # Calculate total logical shifts for each player (for reference)
        p1_total_shifts = len(p1_shifts)
        p2_total_shifts = len(p2_shifts)
        
        wowy = {
            'wowy_key': f"WOWY_{game_id}_{p1}_{p2}",
            'game_id': game_id,
            'season_id': row.get('season_id'),
            'player_1_id': p1,
            'player_2_id': p2,
            'venue': venue,
            'shifts_together': len(together_shifts),  # Logical shifts together
            'p1_total_shifts': p1_total_shifts,  # Total logical shifts for P1
            'p2_total_shifts': p2_total_shifts,  # Total logical shifts for P2
            'p1_shifts_without_p2': len(p1_without_p2),  # Logical shifts P1 without P2
            'p2_shifts_without_p1': len(p2_without_p1),  # Logical shifts P2 without P1
            'toi_together': toi_together,
            'toi_apart': round(toi_p1_without_p2 + toi_p2_without_p1, 1),
            'toi_p1_without_p2': round(toi_p1_without_p2, 1),
            'toi_p2_without_p1': round(toi_p2_without_p1, 1),
            # Together stats (from H2H)
            'cf_together': cf_together,
            'ca_together': ca_together,
            'cf_pct_together': cf_pct_together,
            'gf_together': gf_together,
            'ga_together': ga_together,
            'gf_pct_together': gf_pct_together,
            # Apart stats (calculated)
            'cf_apart': cf_apart,
            'ca_apart': ca_apart,
            'cf_pct_apart': cf_pct_apart,
            'gf_apart': gf_apart,
            'ga_apart': ga_apart,
            'gf_pct_apart': gf_pct_apart,
            # Deltas
            'cf_pct_delta': round(cf_pct_together - cf_pct_apart, 2),
            'gf_pct_delta': round(gf_pct_together - gf_pct_apart, 2),
            'relative_corsi': round(cf_pct_together - cf_pct_apart, 2),
        }
        
        all_wowy.append(wowy)
    
    df = pd.DataFrame(all_wowy)
    print(f"  Created {len(df)} WOWY records using logical shifts")
    return df


def create_fact_line_combos() -> pd.DataFrame:
    """
    Create line combination analysis.
    
    Groups forward trios and defense pairs using logical shifts.
    Uses fact_shift_players with logical_shift_number for proper shift counting
    and to get actual player_ids (not jersey numbers) and real stats.
    """
    print("\nBuilding fact_line_combos...")
    
    shift_players = load_table('fact_shift_players')
    schedule = load_table('dim_schedule')
    
    if len(shift_players) == 0:
        print("  ERROR: fact_shift_players not found!")
        return pd.DataFrame()
    
    # Ensure logical_shift_number exists
    if 'logical_shift_number' not in shift_players.columns:
        print("  WARNING: logical_shift_number not found in fact_shift_players!")
        print("  Falling back to shift_index for shift counting...")
        shift_players['logical_shift_number'] = shift_players.get('shift_index', shift_players.index)
    
    # Ensure position column exists
    if 'position' not in shift_players.columns:
        print("  WARNING: position column not found in fact_shift_players!")
        return pd.DataFrame()
    
    all_combos = []
    
    # Process each game
    for game_id in shift_players['game_id'].unique():
        if pd.isna(game_id) or game_id == 99999:
            continue
        
        game_sp = shift_players[shift_players['game_id'] == game_id].copy()
        
        # Get season_id
        season_id = None
        if len(schedule) > 0:
            game_info = schedule[schedule['game_id'] == game_id]
            if len(game_info) > 0 and 'season_id' in game_info.columns:
                season_id = game_info['season_id'].values[0]
        
        # Process each venue (home, away)
        for venue in ['home', 'away']:
            venue_sp = game_sp[game_sp['venue'] == venue.lower()].copy()
            
            if len(venue_sp) == 0:
                continue
            
            # Group by logical_shift_number to find players on same logical shift
            logical_shifts = venue_sp.groupby('logical_shift_number')
            
            # Track forward combos and defense pairs: (tuple of player_ids) -> stats
            forward_combos = {}  # tuple of forward player_ids -> stats
            defense_combos = {}  # tuple of defense player_ids -> stats
            
            for logical_shift_num, shift_group in logical_shifts:
                if pd.isna(logical_shift_num):
                    continue
                
                # Get forwards (F, LW, RW, C)
                forwards_sp = shift_group[
                    shift_group['position'].astype(str).str.upper().str.contains('F|LW|RW|C', na=False, regex=True)
                ]
                
                # Get defense (D)
                defense_sp = shift_group[
                    shift_group['position'].astype(str).str.upper().str.contains('^D$', na=False, regex=True)
                ]
                
                # Get unique player IDs (convert to int for consistency)
                forward_ids = forwards_sp['player_id'].dropna().unique().tolist()
                defense_ids = defense_sp['player_id'].dropna().unique().tolist()
                
                # Get jersey numbers (player_game_number) - store as list of ints
                forward_jerseys = forwards_sp['player_game_number'].dropna().unique().tolist()
                defense_jerseys = defense_sp['player_game_number'].dropna().unique().tolist()
                
                # Convert to ints (handle any decimals/strings)
                try:
                    forward_jerseys = sorted([int(float(j)) for j in forward_jerseys if pd.notna(j)])
                    defense_jerseys = sorted([int(float(j)) for j in defense_jerseys if pd.notna(j)])
                except (ValueError, TypeError):
                    # Skip this shift if conversion fails
                    continue
                
                # Use logical_shift_duration if available, else sum first segments
                if 'logical_shift_duration' in shift_group.columns and pd.notna(shift_group.iloc[0].get('logical_shift_duration')):
                    shift_duration = shift_group.iloc[0]['logical_shift_duration']
                else:
                    first_segments = shift_group[shift_group.get('is_first_segment', pd.Series([True] * len(shift_group))) == True]
                    shift_duration = first_segments['shift_duration'].sum() if 'shift_duration' in first_segments.columns else 0
                
                # Get stats from shift_group (use first row - stats should be same for all players on same shift)
                shift_row = shift_group.iloc[0]
                shift_gf = int(shift_row.get('gf', 0)) if pd.notna(shift_row.get('gf')) else 0
                shift_ga = int(shift_row.get('ga', 0)) if pd.notna(shift_row.get('ga')) else 0
                shift_cf = int(shift_row.get('cf', 0)) if pd.notna(shift_row.get('cf')) else 0
                shift_ca = int(shift_row.get('ca', 0)) if pd.notna(shift_row.get('ca')) else 0
                shift_ff = int(shift_row.get('ff', 0)) if pd.notna(shift_row.get('ff')) else 0
                shift_fa = int(shift_row.get('fa', 0)) if pd.notna(shift_row.get('fa')) else 0
                
                # Forward combos: need at least 2 forwards
                if len(forward_ids) >= 2:
                    # Sort player IDs for consistency
                    forward_key = tuple(sorted(forward_ids))
                    
                    if forward_key not in forward_combos:
                        forward_combos[forward_key] = {
                            'logical_shifts': set(),
                            'toi_together': 0,
                            'goals_for': 0,
                            'goals_against': 0,
                            'corsi_for': 0,
                            'corsi_against': 0,
                            'fenwick_for': 0,
                            'fenwick_against': 0,
                            'jersey_numbers': forward_jerseys,  # Keep track of jersey numbers
                        }
                    
                    # Add this logical shift (avoid double counting)
                    forward_combos[forward_key]['logical_shifts'].add(logical_shift_num)
                    forward_combos[forward_key]['toi_together'] += shift_duration
                    forward_combos[forward_key]['goals_for'] += shift_gf
                    forward_combos[forward_key]['goals_against'] += shift_ga
                    forward_combos[forward_key]['corsi_for'] += shift_cf
                    forward_combos[forward_key]['corsi_against'] += shift_ca
                    forward_combos[forward_key]['fenwick_for'] += shift_ff
                    forward_combos[forward_key]['fenwick_against'] += shift_fa
                
                # Defense combos: need at least 1 defenseman
                if len(defense_ids) >= 1:
                    # Sort player IDs for consistency
                    defense_key = tuple(sorted(defense_ids))
                    
                    if defense_key not in defense_combos:
                        defense_combos[defense_key] = {
                            'logical_shifts': set(),
                            'toi_together': 0,
                            'goals_for': 0,
                            'goals_against': 0,
                            'corsi_for': 0,
                            'corsi_against': 0,
                            'fenwick_for': 0,
                            'fenwick_against': 0,
                            'jersey_numbers': defense_jerseys,  # Keep track of jersey numbers
                        }
                    
                    # Add this logical shift (avoid double counting)
                    defense_combos[defense_key]['logical_shifts'].add(logical_shift_num)
                    defense_combos[defense_key]['toi_together'] += shift_duration
                    defense_combos[defense_key]['goals_for'] += shift_gf
                    defense_combos[defense_key]['goals_against'] += shift_ga
                    defense_combos[defense_key]['corsi_for'] += shift_cf
                    defense_combos[defense_key]['corsi_against'] += shift_ca
                    defense_combos[defense_key]['fenwick_for'] += shift_ff
                    defense_combos[defense_key]['fenwick_against'] += shift_fa
            
            # Create records for forward combos
            for forward_ids_tuple, stats in forward_combos.items():
                forward_ids_list = sorted([str(pid) for pid in forward_ids_tuple])
                shifts_together = len(stats['logical_shifts'])
                
                # Calculate percentages
                total_corsi = stats['corsi_for'] + stats['corsi_against']
                cf_pct = round(stats['corsi_for'] / total_corsi * 100, 2) if total_corsi > 0 else 50.0
                
                total_fenwick = stats['fenwick_for'] + stats['fenwick_against']
                ff_pct = round(stats['fenwick_for'] / total_fenwick * 100, 2) if total_fenwick > 0 else 50.0
                
                combo = {
                    'line_combo_key': f"LC_{game_id}_{venue}_F_{'_'.join(forward_ids_list)}",
                    'game_id': game_id,
                    'season_id': season_id,
                    'venue': venue,
                    'combo_type': 'forward',
                    # Store player IDs as list (JSON array format for storage)
                    'forward_combo': ','.join(forward_ids_list),  # Comma-separated for display
                    'forward_combo_ids': forward_ids_list,  # List format
                    # Store jersey numbers as list of ints
                    'forward_jersey_numbers': stats['jersey_numbers'],  # List of ints
                    'defense_combo': None,
                    'defense_combo_ids': None,
                    'defense_jersey_numbers': None,
                    'shifts': shifts_together,  # Logical shifts
                    'toi_together': round(stats['toi_together'], 1),
                    'goals_for': stats['goals_for'],
                    'goals_against': stats['goals_against'],
                    'plus_minus': stats['goals_for'] - stats['goals_against'],
                    'corsi_for': stats['corsi_for'],
                    'corsi_against': stats['corsi_against'],
                    'cf_pct': cf_pct,
                    'fenwick_for': stats['fenwick_for'],
                    'fenwick_against': stats['fenwick_against'],
                    'ff_pct': ff_pct,
                }
                all_combos.append(combo)
            
            # Create records for defense combos
            for defense_ids_tuple, stats in defense_combos.items():
                defense_ids_list = sorted([str(pid) for pid in defense_ids_tuple])
                shifts_together = len(stats['logical_shifts'])
                
                # Calculate percentages
                total_corsi = stats['corsi_for'] + stats['corsi_against']
                cf_pct = round(stats['corsi_for'] / total_corsi * 100, 2) if total_corsi > 0 else 50.0
                
                total_fenwick = stats['fenwick_for'] + stats['fenwick_against']
                ff_pct = round(stats['fenwick_for'] / total_fenwick * 100, 2) if total_fenwick > 0 else 50.0
                
                combo = {
                    'line_combo_key': f"LC_{game_id}_{venue}_D_{'_'.join(defense_ids_list)}",
                    'game_id': game_id,
                    'season_id': season_id,
                    'venue': venue,
                    'combo_type': 'defense',
                    'forward_combo': None,
                    'forward_combo_ids': None,
                    'forward_jersey_numbers': None,
                    # Store player IDs as list
                    'defense_combo': ','.join(defense_ids_list),  # Comma-separated for display
                    'defense_combo_ids': defense_ids_list,  # List format
                    # Store jersey numbers as list of ints
                    'defense_jersey_numbers': stats['jersey_numbers'],  # List of ints
                    'shifts': shifts_together,  # Logical shifts
                    'toi_together': round(stats['toi_together'], 1),
                    'goals_for': stats['goals_for'],
                    'goals_against': stats['goals_against'],
                    'plus_minus': stats['goals_for'] - stats['goals_against'],
                    'corsi_for': stats['corsi_for'],
                    'corsi_against': stats['corsi_against'],
                    'cf_pct': cf_pct,
                    'fenwick_for': stats['fenwick_for'],
                    'fenwick_against': stats['fenwick_against'],
                    'ff_pct': ff_pct,
                }
                all_combos.append(combo)
    
    df = pd.DataFrame(all_combos)
    
    # Convert list columns to JSON strings for CSV storage (they'll be stored as strings)
    # When loading in other systems, parse these as JSON arrays
    if len(df) > 0:
        # For CSV export, store lists as JSON strings
        for col in ['forward_combo_ids', 'defense_combo_ids', 'forward_jersey_numbers', 'defense_jersey_numbers']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: json.dumps(x) if x is not None else None)
    
    print(f"  Created {len(df)} line combo records using logical shifts")
    return df


def create_fact_shift_quality() -> pd.DataFrame:
    """
    Create per-shift quality scores.
    Aggregates on logical shifts (logical_shift_number) rather than shift_index.
    """
    print("\nBuilding fact_shift_quality...")
    
    shift_players = load_table('fact_shift_players')
    
    if len(shift_players) == 0:
        print("  ERROR: fact_shift_players not found!")
        return pd.DataFrame()
    
    # Ensure logical_shift_number exists
    if 'logical_shift_number' not in shift_players.columns:
        print("  WARNING: logical_shift_number not found in fact_shift_players!")
        print("  Falling back to shift_index for shift counting...")
        shift_players['logical_shift_number'] = shift_players.get('shift_index', shift_players.index)
    
    all_quality = []
    
    # Group by logical shift to aggregate per logical shift (not per shift_index)
    # Logical shifts represent actual shift changes where line composition changes
    for (game_id, player_id, logical_shift_num), group in shift_players.groupby(['game_id', 'player_id', 'logical_shift_number']):
        if pd.isna(player_id) or pd.isna(logical_shift_num):
            continue
        
        # Get first row from group (should all have same basic info for the same logical shift)
        sp = group.iloc[0]
        
        # Aggregate shift_duration from all rows in logical shift (sum)
        shift_duration = group['shift_duration'].sum() if 'shift_duration' in group.columns else 0
        # For other fields, take from first row
        period = sp.get('period')
        
        quality = {
            'shift_quality_key': f"SQ_{game_id}_{player_id}_{logical_shift_num}",
            'game_id': game_id,
            'player_id': player_id,
            'logical_shift_number': logical_shift_num,
            'shift_duration': shift_duration,
            'period': period,
        }
        
        # Calculate quality score based on available metrics
        # Factors: duration (optimal 40-60s), plus/minus, events
        duration = quality['shift_duration']
        
        # Duration score (optimal 40-60 seconds)
        if 40 <= duration <= 60:
            duration_score = 1.0
        elif 30 <= duration <= 80:
            duration_score = 0.7
        else:
            duration_score = 0.4
        
        # Plus/minus factor - aggregate across all rows in logical shift
        pm = group['pm_all'].sum() if 'pm_all' in group.columns else (sp.get('pm_all', 0) if pd.notna(sp.get('pm_all')) else 0)
        pm_score = 0.5 + (pm * 0.25)  # +1 pm = 0.75, -1 pm = 0.25
        pm_score = max(0, min(1, pm_score))
        
        # Combined quality score
        quality_score = (duration_score + pm_score) / 2
        
        quality['quality_score'] = round(quality_score, 2)
        
        # Quality tier
        if quality_score >= 0.8:
            quality['shift_quality'] = 'excellent'
        elif quality_score >= 0.6:
            quality['shift_quality'] = 'good'
        elif quality_score >= 0.4:
            quality['shift_quality'] = 'average'
        else:
            quality['shift_quality'] = 'poor'
        
        # Strength/situation
        quality['strength'] = sp.get('strength', '5v5')
        
        all_quality.append(quality)
    
    df = pd.DataFrame(all_quality)
    print(f"  Created {len(df)} shift quality records")
    return df


def create_fact_shift_quality_logical() -> pd.DataFrame:
    """
    Create aggregated shift quality per player per game.
    Aggregates from fact_shift_quality which now uses logical shifts.
    """
    print("\nBuilding fact_shift_quality_logical...")
    
    sq = load_table('fact_shift_quality')
    shift_players = load_table('fact_shift_players')
    players = load_table('dim_player')
    
    if len(sq) == 0:
        print("  ERROR: fact_shift_quality not found!")
        return pd.DataFrame()
    
    # Group by game and player
    grouped = sq.groupby(['game_id', 'player_id'])
    
    all_logical = []
    
    for (game_id, player_id), group in grouped:
        if pd.isna(player_id):
            continue
        
        logical = {
            'game_id': game_id,
            'player_id': player_id,
            'logical_shifts': len(group),
            'toi_seconds': group['shift_duration'].sum(),
            'avg_quality_score': round(group['quality_score'].mean(), 2),
        }
        
        # Get player name
        if len(players) > 0:
            player_info = players[players['player_id'] == player_id]
            if len(player_info) > 0 and 'player_full_name' in player_info.columns:
                logical['player_name'] = player_info['player_full_name'].values[0]
        
        # Get additional stats from shift_players
        if len(shift_players) > 0:
            player_shifts = shift_players[
                (shift_players['game_id'] == game_id) & 
                (shift_players['player_id'] == player_id)
            ]
            
            if len(player_shifts) > 0:
                logical['player_rating'] = player_shifts['player_rating'].mean() if 'player_rating' in player_shifts.columns else 4.0
                logical['avg_opp_rating'] = player_shifts['opp_avg_rating'].mean() if 'opp_avg_rating' in player_shifts.columns else 4.0
                logical['gf_all'] = player_shifts['gf_all'].sum() if 'gf_all' in player_shifts.columns else 0
                logical['ga_all'] = player_shifts['ga_all'].sum() if 'ga_all' in player_shifts.columns else 0
                logical['cf'] = player_shifts['cf'].sum() if 'cf' in player_shifts.columns else 0
                logical['ca'] = player_shifts['ca'].sum() if 'ca' in player_shifts.columns else 0
        
        logical['pm_all'] = logical.get('gf_all', 0) - logical.get('ga_all', 0)
        logical['toi_minutes'] = round(logical['toi_seconds'] / 60, 1)
        
        # CF%
        cf = logical.get('cf', 0)
        ca = logical.get('ca', 0)
        total = cf + ca
        logical['cf_pct'] = round(cf / total * 100, 1) if total > 0 else 50.0
        
        # QoC (quality of competition)
        logical['qoc'] = logical.get('avg_opp_rating', 4.0)
        
        # Performance vs expected
        rating_diff = logical.get('player_rating', 4.0) - logical.get('avg_opp_rating', 4.0)
        expected_pm = rating_diff * logical['logical_shifts'] * 0.1  # Simple model
        logical['expected_pm'] = round(expected_pm, 2)
        logical['pm_vs_expected'] = round(logical['pm_all'] - expected_pm, 2)
        
        if logical['pm_vs_expected'] > 0.5:
            logical['performance'] = 'overperform'
        elif logical['pm_vs_expected'] < -0.5:
            logical['performance'] = 'underperform'
        else:
            logical['performance'] = 'expected'
        
        all_logical.append(logical)
    
    df = pd.DataFrame(all_logical)
    print(f"  Created {len(df)} shift quality logical records")
    return df


def create_all_shift_analytics():
    """
    Create all shift analytics tables.
    
    Order matters - some tables depend on others.
    """
    print("\n" + "=" * 70)
    print("CREATING SHIFT ANALYTICS TABLES")
    print("=" * 70)
    
    results = {}
    
    # 1. H2H (base for WOWY)
    df = create_fact_h2h()
    if len(df) > 0:
        rows = save_table(df, 'fact_h2h')
        results['fact_h2h'] = rows
        print(f"  ✓ fact_h2h: {rows} rows")
    
    # 2. WOWY (uses H2H)
    df = create_fact_wowy()
    if len(df) > 0:
        rows = save_table(df, 'fact_wowy')
        results['fact_wowy'] = rows
        print(f"  ✓ fact_wowy: {rows} rows")
    
    # 3. Line combos
    df = create_fact_line_combos()
    if len(df) > 0:
        rows = save_table(df, 'fact_line_combos')
        results['fact_line_combos'] = rows
        print(f"  ✓ fact_line_combos: {rows} rows")
    
    # 4. Shift quality
    df = create_fact_shift_quality()
    if len(df) > 0:
        rows = save_table(df, 'fact_shift_quality')
        results['fact_shift_quality'] = rows
        print(f"  ✓ fact_shift_quality: {rows} rows")
    
    # 5. Shift quality logical
    df = create_fact_shift_quality_logical()
    if len(df) > 0:
        rows = save_table(df, 'fact_shift_quality_logical')
        results['fact_shift_quality_logical'] = rows
        print(f"  ✓ fact_shift_quality_logical: {rows} rows")
    
    print(f"\nCreated {len(results)} shift analytics tables")
    return results


if __name__ == "__main__":
    create_all_shift_analytics()
