#!/usr/bin/env python3
"""
BenchSight Game Status & Suspicious Stats Generator
====================================================
Creates two fact tables for monitoring data quality:
1. fact_game_status - Detailed status for each game (completeness, coverage, etc.)
2. fact_suspicious_stats - Consolidated table of all flagged stats

Also implements:
- Dynamic position assignment from shift data
- Dim multiplier integration check

Run: python scripts/build_qa_facts.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import os
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

OUTPUT_DIR = Path('data/output')
GAMES_DIR = Path('data/raw/games')

# ============================================================================
# THRESHOLDS FOR OUTLIER DETECTION
# ============================================================================
THRESHOLDS = {
    'goals_per_game': 5,
    'assists_per_game': 6,
    'toi_max_seconds_skater': 2400,
    'toi_max_seconds_goalie': 3600,
    'toi_min_seconds': 60,
    'plus_minus_extreme': 6,
    'shots_per_game': 20,
    'cf_pct_extreme_low': 15,
    'cf_pct_extreme_high': 85,
    'zscore_threshold': 3,
}


# ============================================================================
# FACT_GAME_STATUS - Detailed status for each game
# ============================================================================
def build_game_status():
    """Build fact_game_status with completeness metrics."""
    print("\nBuilding fact_game_status...")
    
    schedule = pd.read_csv(OUTPUT_DIR / 'dim_schedule.csv')
    
    # Get loaded game stats
    pgs_file = OUTPUT_DIR / 'fact_player_game_stats.csv'
    pgs = pd.read_csv(pgs_file) if pgs_file.exists() else pd.DataFrame()
    loaded_games = set(pgs['game_id'].unique()) if len(pgs) > 0 else set()
    
    events_file = OUTPUT_DIR / 'fact_event_players.csv'
    events = pd.read_csv(events_file) if events_file.exists() else pd.DataFrame()
    
    shifts_file = OUTPUT_DIR / 'fact_shift_players.csv'
    shifts = pd.read_csv(shifts_file) if shifts_file.exists() else pd.DataFrame()
    
    status_rows = []
    
    for _, game_row in schedule.iterrows():
        game_id = game_row['game_id']
        
        row = {
            'game_id': game_id,
            'game_date': game_row.get('date'),
            'home_team': game_row.get('home_team_name'),
            'away_team': game_row.get('away_team_name'),
            'official_home_goals': game_row.get('home_total_goals'),
            'official_away_goals': game_row.get('away_total_goals'),
            'official_total_goals': int(game_row.get('home_total_goals', 0) or 0) + int(game_row.get('away_total_goals', 0) or 0),
            'game_url': game_row.get('game_url'),
        }
        
        # Check tracking file
        tracking_file = GAMES_DIR / str(game_id) / f"{game_id}_tracking.xlsx"
        
        if not tracking_file.exists():
            row.update({
                'tracking_status': 'NO_FILE',
                'tracking_pct': 0.0,
                'events_row_count': 0,
                'shifts_row_count': 0,
                'player_id_fill_pct': 0.0,
                'goal_events': 0,
                'periods_covered': '',
                'tracking_start_period': None,
                'tracking_start_time': None,
                'tracking_end_period': None,
                'tracking_end_time': None,
                'is_loaded': False,
                'goals_in_stats': 0,
                'goal_match': None,
                'player_count': 0,
                'issues': 'No tracking file'
            })
        else:
            try:
                raw_events = pd.read_excel(tracking_file, sheet_name='events')
                raw_shifts = pd.read_excel(tracking_file, sheet_name='shifts')
                
                # Calculate fill rates
                player_fill = raw_events['player_id'].notna().sum() / len(raw_events) * 100 if len(raw_events) > 0 else 0
                type_fill = raw_events['Type'].notna().sum() / len(raw_events) * 100 if len(raw_events) > 0 else 0
                
                # Determine status
                if player_fill > 50:
                    status = 'COMPLETE'
                elif player_fill > 10:
                    status = 'PARTIAL'
                else:
                    status = 'TEMPLATE'
                
                # Count goals
                goal_count = raw_events[raw_events['Type'] == 'Goal']['event_index'].nunique() if 'Type' in raw_events.columns else 0
                
                # Get time range
                tracked_events = raw_events[raw_events['Type'].notna()]
                if len(tracked_events) > 0 and 'period' in tracked_events.columns:
                    periods = sorted([int(p) for p in tracked_events['period'].dropna().unique() if pd.notna(p)])
                    periods_str = ','.join(map(str, periods))
                    
                    # Find start/end times
                    first_event = tracked_events.iloc[0]
                    last_event = tracked_events.iloc[-1]
                    
                    start_period = first_event.get('period')
                    start_min = first_event.get('event_start_min', first_event.get('event_start_min_'))
                    start_sec = first_event.get('event_start_sec', first_event.get('event_start_sec_'))
                    
                    end_period = last_event.get('period')
                    end_min = last_event.get('event_end_min', last_event.get('event_end_min_'))
                    end_sec = last_event.get('event_end_sec', last_event.get('event_end_sec_'))
                    
                    start_time = f"{int(start_min or 0)}:{int(start_sec or 0):02d}" if pd.notna(start_min) else None
                    end_time = f"{int(end_min or 0)}:{int(end_sec or 0):02d}" if pd.notna(end_min) else None
                else:
                    periods_str = ''
                    start_period = None
                    start_time = None
                    end_period = None
                    end_time = None
                
                # Check if loaded
                is_loaded = int(game_id) in loaded_games
                goals_in_stats = int(pgs[pgs['game_id'] == int(game_id)]['goals'].sum()) if is_loaded else 0
                goal_match = goals_in_stats == row['official_total_goals'] if is_loaded else None
                player_count = len(pgs[pgs['game_id'] == int(game_id)]) if is_loaded else 0
                
                # Identify issues
                issues = []
                if status == 'TEMPLATE':
                    issues.append('Template only - not tracked')
                elif status == 'PARTIAL':
                    issues.append(f'Partial tracking ({player_fill:.0f}%)')
                if is_loaded and not goal_match:
                    issues.append(f'Goal mismatch: {goals_in_stats} vs {row["official_total_goals"]}')
                
                # Check for missing assists
                if is_loaded:
                    game_stats = pgs[pgs['game_id'] == int(game_id)]
                    if game_stats['goals'].sum() > 2 and game_stats['assists'].sum() == 0:
                        issues.append('No assists tracked')
                
                row.update({
                    'tracking_status': status,
                    'tracking_pct': round(player_fill, 1),
                    'events_row_count': len(raw_events),
                    'shifts_row_count': len(raw_shifts),
                    'player_id_fill_pct': round(player_fill, 1),
                    'goal_events': goal_count,
                    'periods_covered': periods_str,
                    'tracking_start_period': start_period,
                    'tracking_start_time': start_time,
                    'tracking_end_period': end_period,
                    'tracking_end_time': end_time,
                    'is_loaded': is_loaded,
                    'goals_in_stats': goals_in_stats,
                    'goal_match': goal_match,
                    'player_count': player_count,
                    'issues': '; '.join(issues) if issues else None
                })
                
            except Exception as e:
                # Check if game was actually loaded by ETL despite file read error
                # This handles cases where file might have been fixed or ETL succeeded
                game_events_count = len(events[events['game_id'] == int(game_id)]) if len(events) > 0 else 0
                game_shifts_count = len(shifts[shifts['game_id'] == int(game_id)]) if len(shifts) > 0 else 0
                is_loaded = int(game_id) in loaded_games
                goals_in_stats = int(pgs[pgs['game_id'] == int(game_id)]['goals'].sum()) if is_loaded else 0
                goal_match = goals_in_stats == row['official_total_goals'] if is_loaded else None
                player_count = len(pgs[pgs['game_id'] == int(game_id)]) if is_loaded else 0
                
                # Determine status based on whether data exists despite file error
                if is_loaded and (game_events_count > 0 or game_shifts_count > 0):
                    # File read failed but ETL successfully processed it
                    # Try to determine status from loaded data
                    if game_events_count > 100:  # Reasonable threshold for complete game
                        status = 'COMPLETE'
                    elif game_events_count > 20:
                        status = 'PARTIAL'
                    else:
                        status = 'TEMPLATE'
                    
                    # Try to get info from loaded data
                    game_events_df = events[events['game_id'] == int(game_id)] if len(events) > 0 else pd.DataFrame()
                    if len(game_events_df) > 0 and 'period' in game_events_df.columns:
                        periods = sorted([int(p) for p in game_events_df['period'].dropna().unique() if pd.notna(p)])
                        periods_str = ','.join(map(str, periods))
                    else:
                        periods_str = ''
                    
                    issues = [f'File read error (ETL succeeded): {str(e)[:100]}']
                    if not goal_match and is_loaded:
                        issues.append(f'Goal mismatch: {goals_in_stats} vs {row["official_total_goals"]}')
                else:
                    # File read failed and no data in output tables
                    status = 'ERROR'
                    periods_str = ''
                    issues = [f'Error reading file: {str(e)[:200]}']
                
                row.update({
                    'tracking_status': status,
                    'tracking_pct': 0.0 if not is_loaded else 100.0,  # If loaded, assume complete
                    'events_row_count': game_events_count,
                    'shifts_row_count': game_shifts_count,
                    'player_id_fill_pct': 0.0,
                    'goal_events': 0,
                    'periods_covered': periods_str,
                    'tracking_start_period': None,
                    'tracking_start_time': None,
                    'tracking_end_period': None,
                    'tracking_end_time': None,
                    'is_loaded': is_loaded,
                    'goals_in_stats': goals_in_stats,
                    'goal_match': goal_match,
                    'player_count': player_count,
                    'issues': '; '.join(issues) if issues else None
                })
        
        status_rows.append(row)
    
    df = pd.DataFrame(status_rows)
    df.to_csv(OUTPUT_DIR / 'fact_game_status.csv', index=False)
    print(f"  ✓ fact_game_status: {len(df)} games")
    
    # Summary
    loaded = df[df['is_loaded'] == True]
    templates = df[df['tracking_status'] == 'TEMPLATE']
    complete = df[df['tracking_status'] == 'COMPLETE']
    
    print(f"\n  Summary:")
    print(f"    Total games in schedule: {len(df)}")
    print(f"    Loaded in ETL: {len(loaded)}")
    print(f"    Complete tracking: {len(complete)}")
    print(f"    Template only: {len(templates)}")
    print(f"    Goal matches: {df['goal_match'].sum()} / {len(loaded)}")
    
    return df


# ============================================================================
# FACT_SUSPICIOUS_STATS - Consolidated suspicious stats table
# ============================================================================
def build_suspicious_stats():
    """Build fact_suspicious_stats with all flagged values."""
    print("\nBuilding fact_suspicious_stats...")
    
    pgs_file = OUTPUT_DIR / 'fact_player_game_stats.csv'
    if not pgs_file.exists():
        print("  ⚠️ fact_player_game_stats.csv not found")
        return pd.DataFrame()
    
    pgs = pd.read_csv(pgs_file)
    players = pd.read_csv(OUTPUT_DIR / 'dim_player.csv') if (OUTPUT_DIR / 'dim_player.csv').exists() else pd.DataFrame()
    
    # Position lookup
    position_lookup = {}
    if len(players) > 0 and 'player_id' in players.columns:
        for _, p in players.iterrows():
            position_lookup[p['player_id']] = p.get('player_primary_position', '')
    
    suspicious = []
    
    for _, row in pgs.iterrows():
        game_id = row['game_id']
        player_id = row.get('player_id')
        player_name = row.get('player_name', 'Unknown')
        
        # Determine if goalie
        position = position_lookup.get(player_id, '')
        is_goalie = position in ['Goalie', 'G', 'goalie']
        toi_max = THRESHOLDS['toi_max_seconds_goalie'] if is_goalie else THRESHOLDS['toi_max_seconds_skater']
        
        # Check thresholds
        checks = [
            ('goals', row['goals'], THRESHOLDS['goals_per_game'], '>', 'HIGH'),
            ('assists', row['assists'], THRESHOLDS['assists_per_game'], '>', 'HIGH'),
            ('toi_seconds', row['toi_seconds'], toi_max, '>', 'HIGH'),
            ('toi_seconds', row['toi_seconds'], THRESHOLDS['toi_min_seconds'], '<', 'LOW'),
            ('shots', row.get('shots', 0), THRESHOLDS['shots_per_game'], '>', 'HIGH'),
            ('cf_pct', row.get('cf_pct', 50), THRESHOLDS['cf_pct_extreme_low'], '<', 'LOW'),
            ('cf_pct', row.get('cf_pct', 50), THRESHOLDS['cf_pct_extreme_high'], '>', 'HIGH'),
        ]
        
        for stat, value, threshold, direction, flag_type in checks:
            if pd.isna(value):
                continue
            
            is_outlier = (direction == '>' and value > threshold) or \
                         (direction == '<' and value < threshold)
            
            if is_outlier:
                suspicious.append({
                    'game_id': game_id,
                    'player_id': player_id,
                    'player_name': player_name,
                    'position': position,
                    'stat_name': stat,
                    'stat_value': value,
                    'threshold': threshold,
                    'threshold_direction': direction,
                    'flag_type': flag_type,
                    'severity': 'WARNING',
                    'category': 'THRESHOLD_EXCEEDED',
                    'note': f'{stat}={value} exceeds {direction}{threshold}',
                    'resolved': False,
                    'created_at': datetime.now().isoformat()
                })
        
        # Check plus/minus extremes
        for pm_col in ['plus_minus_ev', 'plus_minus_total']:
            if pm_col in row and pd.notna(row[pm_col]):
                pm = row[pm_col]
                if abs(pm) > THRESHOLDS['plus_minus_extreme']:
                    suspicious.append({
                        'game_id': game_id,
                        'player_id': player_id,
                        'player_name': player_name,
                        'position': position,
                        'stat_name': pm_col,
                        'stat_value': pm,
                        'threshold': THRESHOLDS['plus_minus_extreme'],
                        'threshold_direction': '±',
                        'flag_type': 'EXTREME',
                        'severity': 'INFO',
                        'category': 'EXTREME_VALUE',
                        'note': f'Extreme +/- of {pm}',
                        'resolved': False,
                        'created_at': datetime.now().isoformat()
                    })
    
    # Add z-score outliers
    numeric_cols = ['goals', 'assists', 'toi_seconds', 'shots', 'corsi_for']
    for col in numeric_cols:
        if col in pgs.columns:
            values = pgs[col].dropna()
            if len(values) > 10:
                mean = values.mean()
                std = values.std()
                if std > 0:
                    for idx, row in pgs.iterrows():
                        if pd.notna(row[col]):
                            zscore = (row[col] - mean) / std
                            if abs(zscore) > THRESHOLDS['zscore_threshold']:
                                suspicious.append({
                                    'game_id': row['game_id'],
                                    'player_id': row.get('player_id'),
                                    'player_name': row.get('player_name', 'Unknown'),
                                    'position': position_lookup.get(row.get('player_id'), ''),
                                    'stat_name': col,
                                    'stat_value': row[col],
                                    'threshold': THRESHOLDS['zscore_threshold'],
                                    'threshold_direction': 'z>',
                                    'flag_type': 'ZSCORE',
                                    'severity': 'INFO',
                                    'category': 'STATISTICAL_OUTLIER',
                                    'note': f'Z-score={zscore:.2f} exceeds {THRESHOLDS["zscore_threshold"]}',
                                    'resolved': False,
                                    'created_at': datetime.now().isoformat()
                                })
    
    df = pd.DataFrame(suspicious)
    if len(df) > 0:
        # Deduplicate (same player+game+stat)
        df = df.drop_duplicates(subset=['game_id', 'player_id', 'stat_name', 'category'])
    
    df.to_csv(OUTPUT_DIR / 'fact_suspicious_stats.csv', index=False)
    print(f"  ✓ fact_suspicious_stats: {len(df)} entries")
    
    if len(df) > 0:
        print(f"\n  Summary by category:")
        print(df.groupby('category').size().to_string())
    
    return df


# ============================================================================
# DYNAMIC POSITION ASSIGNMENT FROM SHIFTS
# ============================================================================
def assign_positions_from_shifts():
    """Assign player positions based on shift data (largest % of shifts)."""
    print("\nAssigning dynamic positions from shift data...")
    
    shifts_file = OUTPUT_DIR / 'fact_shift_players.csv'
    if not shifts_file.exists():
        print("  ⚠️ fact_shift_players.csv not found")
        return
    
    shifts = pd.read_csv(shifts_file)
    
    # Use 'position' column if 'slot' doesn't exist
    pos_col = 'slot' if 'slot' in shifts.columns else 'position'
    if pos_col not in shifts.columns:
        print("  ⚠️ Neither 'slot' nor 'position' column found in shifts - cannot determine position")
        return
    
    # Slot/position to position mapping (using actual slot values from data)
    slot_to_position = {
        # New format (F1, D1, G, etc.)
        'F1': 'Forward', 'F2': 'Forward', 'F3': 'Forward',
        'D1': 'Defense', 'D2': 'Defense',
        'G': 'Goalie', 'X': 'Extra',
        # Old format
        'forward_1': 'Forward', 'forward_2': 'Forward', 'forward_3': 'Forward',
        'defense_1': 'Defense', 'defense_2': 'Defense',
        'goalie': 'Goalie',
        'xtra': 'Extra',  # Extra attacker situations
        # Fallbacks
        'LW': 'Forward', 'C': 'Forward', 'RW': 'Forward',
        'LD': 'Defense', 'RD': 'Defense',
        'F': 'Forward', 'D': 'Defense'
    }
    
    # Ensure logical_shift_number exists
    if 'logical_shift_number' not in shifts.columns:
        print("  ⚠️ logical_shift_number not found - using shift_index for counting")
        shifts['logical_shift_number'] = shifts.get('shift_index', shifts.index)
    
    # Calculate position % per player per game using LOGICAL SHIFTS
    position_stats = []
    
    for (game_id, player_id), group in shifts.groupby(['game_id', 'player_id']):
        if pd.isna(player_id):
            continue
        
        # Count distinct logical shifts (not raw rows)
        total_shifts = group['logical_shift_number'].nunique() if 'logical_shift_number' in group.columns else len(group)
        
        # Count position by logical shift (group by logical_shift_number first, then get position)
        position_counts = {}
        
        # Group by logical shift to avoid double-counting segments
        for logical_shift_num, shift_group in group.groupby('logical_shift_number'):
            # Get position from first segment of this logical shift
            first_shift = shift_group.iloc[0]
            slot = first_shift.get(pos_col, '')
            pos = slot_to_position.get(slot, 'Unknown')
            position_counts[pos] = position_counts.get(pos, 0) + 1
        
        # Find dominant position
        if position_counts:
            dominant_pos = max(position_counts, key=position_counts.get)
            dominant_pct = position_counts[dominant_pos] / total_shifts * 100
        else:
            dominant_pos = 'Unknown'
            dominant_pct = 0
        
        position_stats.append({
            'game_id': game_id,
            'player_id': player_id,
            'total_shifts': total_shifts,
            'dominant_position': dominant_pos,
            'dominant_position_pct': round(dominant_pct, 1),
            'forward_shifts': position_counts.get('Forward', 0),
            'defense_shifts': position_counts.get('Defense', 0),
            'goalie_shifts': position_counts.get('Goalie', 0),
        })
    
    df = pd.DataFrame(position_stats)
    df.to_csv(OUTPUT_DIR / 'fact_player_game_position.csv', index=False)
    print(f"  ✓ fact_player_game_position: {len(df)} player-game records")
    
    # Show players who play multiple positions
    multi_pos = df[df['dominant_position_pct'] < 90]
    if len(multi_pos) > 0:
        print(f"\n  Players with <90% dominant position: {len(multi_pos)}")
        for _, row in multi_pos.head(5).iterrows():
            print(f"    {row['player_id']} game {row['game_id']}: {row['dominant_position']} ({row['dominant_position_pct']:.0f}%)")
    
    return df


# ============================================================================
# CHECK DIM MULTIPLIERS USAGE
# ============================================================================
def check_dim_multipliers():
    """Check if dim table multipliers are being used in stats calculations."""
    print("\nChecking dim table multipliers usage...")
    
    # Check for multiplier/weight columns in dim tables
    dim_files = list(OUTPUT_DIR.glob('dim_*.csv'))
    
    multiplier_cols = []
    for f in dim_files:
        df = pd.read_csv(f)
        for col in df.columns:
            if any(word in col.lower() for word in ['multiplier', 'weight', 'factor', 'coefficient', 'skill', 'rating']):
                multiplier_cols.append((f.name, col, df[col].dtype))
    
    print(f"\n  Dim tables with multiplier/weight columns:")
    if multiplier_cols:
        for table, col, dtype in multiplier_cols:
            print(f"    {table}: {col} ({dtype})")
    else:
        print("    None found")
    
    # Check if these are used in fact tables
    print("\n  Integration status:")
    
    # Check dim_composite_rating
    composite_file = OUTPUT_DIR / 'dim_composite_rating.csv'
    if composite_file.exists():
        composite = pd.read_csv(composite_file)
        print(f"    ✓ dim_composite_rating exists with {len(composite.columns)} columns")
        weight_cols = [c for c in composite.columns if 'weight' in c.lower()]
        if weight_cols:
            print(f"      Weight columns: {weight_cols}")
    
    # Check if skill_rating is used
    pgs_file = OUTPUT_DIR / 'fact_player_game_stats.csv'
    if pgs_file.exists():
        pgs = pd.read_csv(pgs_file)
        rating_cols = [c for c in pgs.columns if 'rating' in c.lower() or 'skill' in c.lower()]
        if rating_cols:
            print(f"    ✓ Rating columns in fact_player_game_stats: {rating_cols}")
        else:
            print(f"    ⚠️ No rating columns found in fact_player_game_stats")
    
    return multiplier_cols


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("=" * 70)
    print("BUILDING QA FACT TABLES")
    print("=" * 70)
    
    game_status = build_game_status()
    suspicious = build_suspicious_stats()
    positions = assign_positions_from_shifts()
    multipliers = check_dim_multipliers()
    
    print("\n" + "=" * 70)
    print("QA FACT TABLES COMPLETE")
    print("=" * 70)
    print("\nNew tables created:")
    print("  - fact_game_status.csv (game completeness/coverage)")
    print("  - fact_suspicious_stats.csv (flagged outliers)")
    print("  - fact_player_game_position.csv (dynamic positions)")


if __name__ == '__main__':
    main()
