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
from pathlib import Path
from itertools import combinations

OUTPUT_DIR = Path('data/output')


def save_table(df: pd.DataFrame, name: str) -> int:
    """Save table to CSV and return row count."""
    path = OUTPUT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    return len(df)


def load_table(name: str) -> pd.DataFrame:
    """Load a table from output directory."""
    path = OUTPUT_DIR / f"{name}.csv"
    if path.exists():
        return pd.read_csv(path, low_memory=False)
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
    
    For each game, analyze which players were on ice together and
    calculate combined stats.
    """
    print("\nBuilding fact_h2h...")
    
    shifts = load_table('fact_shifts')
    shift_players = load_table('fact_shift_players')
    schedule = load_table('dim_schedule')
    
    if len(shifts) == 0:
        print("  ERROR: fact_shifts not found!")
        return pd.DataFrame()
    
    all_h2h = []
    
    for game_id in shifts['game_id'].unique():
        if game_id == 99999:  # Skip test game
            continue
        
        game_shifts = shifts[shifts['game_id'] == game_id]
        
        # Get season_id
        season_id = None
        if len(schedule) > 0:
            game_info = schedule[schedule['game_id'] == game_id]
            if len(game_info) > 0 and 'season_id' in game_info.columns:
                season_id = game_info['season_id'].values[0]
        
        # Process each venue (home, away)
        for venue in ['home', 'away']:
            # Build player pairs for this venue
            player_pairs = {}  # (p1, p2) -> list of shift data
            
            for _, shift in game_shifts.iterrows():
                players = get_players_on_shift(shift, venue)
                
                if len(players) < 2:
                    continue
                
                # Get shift stats
                shift_data = {
                    'duration': shift.get('shift_duration', 0),
                    'gf': 0,  # Would need to calculate from events
                    'ga': 0,
                }
                
                # Create all pairs
                for p1, p2 in combinations(sorted(players), 2):
                    key = (p1, p2)
                    if key not in player_pairs:
                        player_pairs[key] = []
                    player_pairs[key].append(shift_data)
            
            # Aggregate to H2H records
            for (p1, p2), shift_list in player_pairs.items():
                shifts_together = len(shift_list)
                toi_together = sum(s['duration'] for s in shift_list)
                
                h2h = {
                    'h2h_key': f"H2H_{game_id}_{p1}_{p2}",
                    'game_id': game_id,
                    'season_id': season_id,
                    'player_1_id': p1,
                    'player_2_id': p2,
                    'venue': venue,
                    'shifts_together': shifts_together,
                    'toi_together': toi_together,
                    'goals_for': sum(s['gf'] for s in shift_list),
                    'goals_against': sum(s['ga'] for s in shift_list),
                }
                
                h2h['plus_minus'] = h2h['goals_for'] - h2h['goals_against']
                
                # Corsi placeholders (would need event-level analysis)
                h2h['corsi_for'] = 0
                h2h['corsi_against'] = 0
                h2h['cf_pct'] = 50.0
                
                all_h2h.append(h2h)
    
    df = pd.DataFrame(all_h2h)
    print(f"  Created {len(df)} H2H records")
    return df


def create_fact_wowy() -> pd.DataFrame:
    """
    Create WOWY (With Or Without You) analysis.
    
    Compares player performance when together vs apart.
    """
    print("\nBuilding fact_wowy...")
    
    shifts = load_table('fact_shifts')
    h2h = load_table('fact_h2h')  # Use H2H as base
    
    if len(h2h) == 0:
        print("  ERROR: fact_h2h not found! Run H2H first.")
        return pd.DataFrame()
    
    if len(shifts) == 0:
        print("  ERROR: fact_shifts not found!")
        return pd.DataFrame()
    
    all_wowy = []
    
    # Build a mapping of player -> shifts for each game/venue
    def get_player_shifts(game_id, venue, player_cols):
        """Get all shifts containing a specific player."""
        game_shifts = shifts[(shifts['game_id'] == game_id)]
        player_shift_map = {}  # player_id -> set of shift_ids
        
        for _, shift in game_shifts.iterrows():
            for col in player_cols:
                if col in shift.index:
                    pid = shift[col]
                    if pd.notna(pid) and str(pid) not in ['', 'nan', 'None']:
                        if pid not in player_shift_map:
                            player_shift_map[pid] = set()
                        player_shift_map[pid].add(shift.get('shift_id', shift.name))
        
        return player_shift_map
    
    # For each H2H pair, calculate with/without stats
    for _, row in h2h.iterrows():
        game_id = row['game_id']
        p1 = row['player_1_id']
        p2 = row['player_2_id']
        venue = row.get('venue', 'home')
        
        # Get player columns for this venue
        player_cols = [f'{venue}_forward_1', f'{venue}_forward_2', f'{venue}_forward_3',
                       f'{venue}_defense_1', f'{venue}_defense_2', f'{venue}_goalie']
        
        # Get shift IDs for each player
        player_shift_map = get_player_shifts(game_id, venue, player_cols)
        
        p1_shifts = player_shift_map.get(p1, set())
        p2_shifts = player_shift_map.get(p2, set())
        
        # Shifts together (intersection)
        together_shifts = p1_shifts & p2_shifts
        
        # Shifts apart 
        p1_without_p2 = p1_shifts - p2_shifts
        p2_without_p1 = p2_shifts - p1_shifts
        
        # Get shift durations
        game_shifts = shifts[shifts['game_id'] == game_id]
        duration_col = 'shift_duration' if 'shift_duration' in game_shifts.columns else None
        
        toi_together = 0
        toi_p1_without_p2 = 0
        toi_p2_without_p1 = 0
        
        if duration_col:
            for _, shift in game_shifts.iterrows():
                shift_id = shift.get('shift_id', shift.name)
                duration = shift.get(duration_col, 0) or 0
                
                if shift_id in together_shifts:
                    toi_together += duration
                if shift_id in p1_without_p2:
                    toi_p1_without_p2 += duration
                if shift_id in p2_without_p1:
                    toi_p2_without_p1 += duration
        
        wowy = {
            'wowy_key': f"WOWY_{game_id}_{p1}_{p2}",
            'game_id': game_id,
            'season_id': row.get('season_id'),
            'player_1_id': p1,
            'player_2_id': p2,
            'venue': venue,
            'shifts_together': len(together_shifts),
            'toi_together': toi_together,
            'p1_shifts_without_p2': len(p1_without_p2),
            'p2_shifts_without_p1': len(p2_without_p1),
            'toi_apart': toi_p1_without_p2 + toi_p2_without_p1,
            'toi_p1_without_p2': toi_p1_without_p2,
            'toi_p2_without_p1': toi_p2_without_p1,
        }
        
        # CF% together vs apart
        wowy['cf_pct_together'] = row.get('cf_pct', 50.0)
        # Calculate CF% apart based on individual performance when not together
        # For simplicity, use 50% as baseline when apart (neutral performance)
        wowy['cf_pct_apart'] = 50.0 if wowy['toi_apart'] == 0 else 50.0  # Would need event-level analysis for true value
        wowy['cf_pct_delta'] = wowy['cf_pct_together'] - wowy['cf_pct_apart']
        
        # GF% together vs apart
        gf = row.get('goals_for', 0)
        ga = row.get('goals_against', 0)
        total = gf + ga
        wowy['gf_pct_together'] = round(gf / total * 100, 1) if total > 0 else 50.0
        wowy['gf_pct_apart'] = 50.0  # Would need event-level analysis for true value
        wowy['gf_pct_delta'] = wowy['gf_pct_together'] - wowy['gf_pct_apart']
        
        # Relative metrics
        wowy['relative_corsi'] = wowy['cf_pct_delta']
        
        all_wowy.append(wowy)
    
    df = pd.DataFrame(all_wowy)
    print(f"  Created {len(df)} WOWY records")
    return df


def create_fact_line_combos() -> pd.DataFrame:
    """
    Create line combination analysis.
    
    Groups forward trios and defense pairs.
    """
    print("\nBuilding fact_line_combos...")
    
    shifts = load_table('fact_shifts')
    schedule = load_table('dim_schedule')
    
    if len(shifts) == 0:
        print("  ERROR: fact_shifts not found!")
        return pd.DataFrame()
    
    all_combos = []
    
    for game_id in shifts['game_id'].unique():
        if game_id == 99999:
            continue
        
        game_shifts = shifts[shifts['game_id'] == game_id]
        
        # Get season_id
        season_id = None
        if len(schedule) > 0:
            game_info = schedule[schedule['game_id'] == game_id]
            if len(game_info) > 0 and 'season_id' in game_info.columns:
                season_id = game_info['season_id'].values[0]
        
        for venue in ['home', 'away']:
            # Track unique forward combos and defense pairs
            forward_combos = {}  # tuple of 3 forwards -> stats
            defense_combos = {}  # tuple of 2 defense -> stats
            
            for _, shift in game_shifts.iterrows():
                # Get forwards
                f1 = shift.get(f'{venue}_forward_1')
                f2 = shift.get(f'{venue}_forward_2')
                f3 = shift.get(f'{venue}_forward_3')
                
                forwards = tuple(sorted([f for f in [f1, f2, f3] if pd.notna(f) and str(f) != 'nan']))
                
                if len(forwards) >= 2:  # At least 2 forwards
                    if forwards not in forward_combos:
                        forward_combos[forwards] = {'shifts': 0, 'toi': 0}
                    forward_combos[forwards]['shifts'] += 1
                    forward_combos[forwards]['toi'] += shift.get('shift_duration', 0)
                
                # Get defense
                d1 = shift.get(f'{venue}_defense_1')
                d2 = shift.get(f'{venue}_defense_2')
                
                defense = tuple(sorted([d for d in [d1, d2] if pd.notna(d) and str(d) != 'nan']))
                
                if len(defense) >= 1:
                    if defense not in defense_combos:
                        defense_combos[defense] = {'shifts': 0, 'toi': 0}
                    defense_combos[defense]['shifts'] += 1
                    defense_combos[defense]['toi'] += shift.get('shift_duration', 0)
            
            # Create records for forward combos
            for forwards, stats in forward_combos.items():
                combo = {
                    'line_combo_key': f"LC_{game_id}_{venue}_F_{'_'.join(str(f) for f in forwards)}",
                    'game_id': game_id,
                    'season_id': season_id,
                    'venue': venue,
                    'combo_type': 'forward',
                    'forward_combo': ','.join(str(f) for f in forwards),
                    'defense_combo': None,
                    'shifts': stats['shifts'],
                    'toi_together': stats['toi'],
                    # Placeholder stats
                    'goals_for': 0,
                    'goals_against': 0,
                    'corsi_for': 0,
                    'corsi_against': 0,
                }
                all_combos.append(combo)
            
            # Create records for defense combos
            for defense, stats in defense_combos.items():
                combo = {
                    'line_combo_key': f"LC_{game_id}_{venue}_D_{'_'.join(str(d) for d in defense)}",
                    'game_id': game_id,
                    'season_id': season_id,
                    'venue': venue,
                    'combo_type': 'defense',
                    'forward_combo': None,
                    'defense_combo': ','.join(str(d) for d in defense),
                    'shifts': stats['shifts'],
                    'toi_together': stats['toi'],
                    # Placeholder stats
                    'goals_for': 0,
                    'goals_against': 0,
                    'corsi_for': 0,
                    'corsi_against': 0,
                }
                all_combos.append(combo)
    
    df = pd.DataFrame(all_combos)
    print(f"  Created {len(df)} line combo records")
    return df


def create_fact_shift_quality() -> pd.DataFrame:
    """
    Create per-shift quality scores.
    """
    print("\nBuilding fact_shift_quality...")
    
    shift_players = load_table('fact_shift_players')
    
    if len(shift_players) == 0:
        print("  ERROR: fact_shift_players not found!")
        return pd.DataFrame()
    
    all_quality = []
    
    for _, sp in shift_players.iterrows():
        game_id = sp.get('game_id')
        player_id = sp.get('player_id')
        shift_index = sp.get('shift_index')
        
        if pd.isna(player_id):
            continue
        
        quality = {
            'shift_quality_key': f"SQ_{game_id}_{player_id}_{shift_index}",
            'game_id': game_id,
            'player_id': player_id,
            'shift_index': shift_index,
            'shift_duration': sp.get('shift_duration', 0),
            'period': sp.get('period'),
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
        
        # Plus/minus factor
        pm = sp.get('pm_all', 0) if pd.notna(sp.get('pm_all')) else 0
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
