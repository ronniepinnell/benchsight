#!/usr/bin/env python3
"""
BenchSight Missing Dimension Tables Builder
Creates all missing dimension tables for the schema.

These are STATIC reference tables - they don't depend on game data.

Tables created:
- dim_comparison_type (6 rows)
- dim_competition_tier (4 rows)
- dim_composite_rating (8 rows)
- dim_danger_zone (4 rows)
- dim_highlight_category (10 rows)
- dim_micro_stat (22 rows)
- dim_net_location (10 rows)
- dim_pass_outcome (4 rows)
- dim_rating (5 rows)
- dim_rating_matchup (5 rows)
- dim_rink_zone (267 rows)
- dim_save_outcome (3 rows)
- dim_shift_slot (7 rows)
- dim_shot_outcome (5 rows)
- dim_stat (83 rows)
- dim_stat_category (13 rows)
- dim_stat_type (57 rows)
- dim_strength (18 rows)
- dim_terminology_mapping (84 rows)
- dim_turnover_quality (3 rows)
- dim_turnover_type (21 rows)
- dim_video_type (17 rows)
- dim_zone_outcome (6 rows)

Usage:
    from src.tables.dimension_tables import create_all_dimension_tables
    create_all_dimension_tables()
"""

import pandas as pd
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path('data/output')


def save_table(df: pd.DataFrame, name: str) -> int:
    """Save table to CSV and return row count."""
    path = OUTPUT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    return len(df)


def create_dim_comparison_type() -> pd.DataFrame:
    """Comparison types for analytics."""
    return pd.DataFrame({
        'comparison_type_id': ['CT01', 'CT02', 'CT03', 'CT04', 'CT05', 'CT06'],
        'comparison_type_code': ['h2h', 'wowy', 'vs_team', 'vs_position', 'vs_rating', 'career'],
        'comparison_type_name': ['Head to Head', 'With or Without You', 'Vs Team', 
                                  'Vs Position', 'Vs Rating Tier', 'Career Comparison'],
        'description': [
            'Direct player matchup statistics',
            'Impact when playing together vs apart',
            'Performance against specific teams',
            'Performance against position groups',
            'Performance vs rating-matched opponents',
            'Career trajectory analysis'
        ],
        'analysis_scope': ['game', 'game', 'season', 'season', 'game', 'career']
    })


def create_dim_competition_tier() -> pd.DataFrame:
    """Player competition tiers based on rating."""
    return pd.DataFrame({
        'competition_tier_id': ['TI01', 'TI02', 'TI03', 'TI04'],
        'tier_name': ['Elite', 'Above Average', 'Average', 'Below Average'],
        'min_rating': [5.0, 4.0, 3.0, 2.0],
        'max_rating': [6.0, 4.99, 3.99, 2.99]
    })


def create_dim_composite_rating() -> pd.DataFrame:
    """Composite rating definitions."""
    return pd.DataFrame({
        'rating_id': ['CR01', 'CR02', 'CR03', 'CR04', 'CR05', 'CR06', 'CR07', 'CR08'],
        'rating_code': ['off', 'def', 'twoway', 'hustle', 'impact', 'game_score', 'xg_impact', 'beer_league'],
        'rating_name': ['Offensive Rating', 'Defensive Rating', 'Two-Way Rating', 
                        'Hustle Rating', 'Impact Score', 'Game Score', 'xG Impact', 'Beer League Index'],
        'description': [
            'Points, shots, dangerous passes',
            'Takeaways, blocks, coverage',
            'Combined offensive and defensive',
            'Backchecking, pressure, battles',
            'Overall game impact',
            'NHL-style game score',
            'Expected goals differential',
            'Fun/intangibles metric'
        ],
        'scale_min': [0, 0, 0, 0, -10, -5, -2, 0],
        'scale_max': [100, 100, 100, 100, 10, 5, 2, 100]
    })


def create_dim_danger_zone() -> pd.DataFrame:
    """Shot danger zone definitions."""
    return pd.DataFrame({
        'danger_zone_id': ['DZ01', 'DZ02', 'DZ03', 'DZ04'],
        'danger_zone_code': ['high', 'medium', 'low', 'perimeter'],
        'danger_zone_name': ['High Danger', 'Medium Danger', 'Low Danger', 'Perimeter'],
        'xg_base': [0.25, 0.10, 0.05, 0.02],
        'description': [
            'Inner slot (within 10ft of crease)',
            'Slot area (between faceoff dots)',
            'Outside slot but offensive zone',
            'Blue line and beyond'
        ]
    })


def create_dim_micro_stat() -> pd.DataFrame:
    """Micro-level stat definitions."""
    stats = [
        ('MS01', 'screen', 'Screen', 'offense'),
        ('MS02', 'tip', 'Tip/Deflection', 'offense'),
        ('MS03', 'one_timer', 'One Timer', 'offense'),
        ('MS04', 'deke', 'Deke', 'offense'),
        ('MS05', 'board_battle_win', 'Board Battle Win', 'battles'),
        ('MS06', 'board_battle_loss', 'Board Battle Loss', 'battles'),
        ('MS07', 'puck_recovery', 'Puck Recovery', 'possession'),
        ('MS08', 'puck_protection', 'Puck Protection', 'possession'),
        ('MS09', 'stick_check', 'Stick Check', 'defense'),
        ('MS10', 'poke_check', 'Poke Check', 'defense'),
        ('MS11', 'backcheck', 'Backcheck', 'defense'),
        ('MS12', 'shot_block', 'Shot Block', 'defense'),
        ('MS13', 'pass_intercept', 'Pass Intercept', 'defense'),
        ('MS14', 'gap_close', 'Gap Close', 'defense'),
        ('MS15', 'forecheck_pressure', 'Forecheck Pressure', 'pressure'),
        ('MS16', 'forecheck_win', 'Forecheck Win', 'pressure'),
        ('MS17', 'angling', 'Angling', 'defense'),
        ('MS18', 'box_out', 'Box Out', 'defense'),
        ('MS19', 'net_presence', 'Net Presence', 'offense'),
        ('MS20', 'give_and_go', 'Give and Go', 'offense'),
        ('MS21', 'drive', 'Drive', 'offense'),
        ('MS22', 'royal_road', 'Royal Road Pass', 'offense'),
    ]
    return pd.DataFrame(stats, columns=['micro_stat_id', 'stat_code', 'stat_name', 'category'])


def create_dim_net_location() -> pd.DataFrame:
    """Net location zones for shot placement."""
    return pd.DataFrame({
        'net_location_id': ['NL01', 'NL02', 'NL03', 'NL04', 'NL05', 
                           'NL06', 'NL07', 'NL08', 'NL09', 'NL10'],
        'net_location_code': ['glove_high', 'glove_low', 'blocker_high', 'blocker_low',
                              'five_hole', 'short_side_high', 'short_side_low',
                              'far_side_high', 'far_side_low', 'crossbar'],
        'net_location_name': ['Glove High', 'Glove Low', 'Blocker High', 'Blocker Low',
                              'Five Hole', 'Short Side High', 'Short Side Low',
                              'Far Side High', 'Far Side Low', 'Crossbar'],
        'x_pct': [0.15, 0.15, 0.85, 0.85, 0.50, 0.10, 0.10, 0.90, 0.90, 0.50],
        'y_pct': [0.75, 0.25, 0.75, 0.25, 0.15, 0.85, 0.25, 0.85, 0.25, 0.95]
    })


def create_dim_pass_outcome() -> pd.DataFrame:
    """Pass outcome types."""
    return pd.DataFrame({
        'pass_outcome_id': ['PO01', 'PO02', 'PO03', 'PO04'],
        'pass_outcome_code': ['completed', 'missed', 'intercepted', 'blocked'],
        'pass_outcome_name': ['Completed', 'Missed', 'Intercepted', 'Blocked'],
        'is_successful': [True, False, False, False]
    })


def create_dim_rating() -> pd.DataFrame:
    """Player rating values (2-6 scale)."""
    return pd.DataFrame({
        'rating_id': ['R01', 'R02', 'R03', 'R04', 'R05'],
        'rating_value': [2, 3, 4, 5, 6],
        'rating_name': ['Beginner', 'Developing', 'Average', 'Above Average', 'Elite']
    })


def create_dim_rating_matchup() -> pd.DataFrame:
    """Rating matchup advantage categories."""
    return pd.DataFrame({
        'matchup_id': ['RM01', 'RM02', 'RM03', 'RM04', 'RM05'],
        'matchup_name': ['Big Advantage', 'Slight Advantage', 'Even', 'Slight Disadvantage', 'Big Disadvantage'],
        'min_diff': [1.0, 0.25, -0.24, -0.99, -99],
        'max_diff': [99, 0.99, 0.24, -0.25, -1.0]
    })


def create_dim_rink_zone() -> pd.DataFrame:
    """
    Rink zone definitions at multiple granularities.
    
    Rink: 200ft x 85ft
    - x: 0-200 (goals at 11 and 189)
    - y: 0-85 (center at 42.5)
    """
    zones = []
    zone_id = 1
    
    # Coarse zones (3 zones: O, N, D)
    coarse = [
        ('CZ01', 'offensive', 'Offensive Zone', 'coarse', 125, 200, 0, 85, 'O', 'medium', 'both', 'past blue line', 'full width'),
        ('CZ02', 'neutral', 'Neutral Zone', 'coarse', 75, 125, 0, 85, 'N', 'low', 'both', 'between blue lines', 'full width'),
        ('CZ03', 'defensive', 'Defensive Zone', 'coarse', 0, 75, 0, 85, 'D', 'low', 'both', 'behind blue line', 'full width'),
    ]
    for z in coarse:
        zones.append({
            'rink_zone_id': z[0], 'zone_code': z[1], 'zone_name': z[2], 'granularity': z[3],
            'x_min': z[4], 'x_max': z[5], 'y_min': z[6], 'y_max': z[7],
            'zone': z[8], 'danger': z[9], 'side': z[10], 'x_description': z[11], 'y_description': z[12]
        })
    
    # Medium zones (9 zones: 3x3 grid)
    medium_zones = [
        # Offensive zone
        ('MZ01', 'oz_left', 'OZ Left', 125, 200, 0, 28.3, 'O', 'low', 'left'),
        ('MZ02', 'oz_center', 'OZ Center', 125, 200, 28.3, 56.7, 'O', 'medium', 'center'),
        ('MZ03', 'oz_right', 'OZ Right', 125, 200, 56.7, 85, 'O', 'low', 'right'),
        # Neutral zone
        ('MZ04', 'nz_left', 'NZ Left', 75, 125, 0, 28.3, 'N', 'low', 'left'),
        ('MZ05', 'nz_center', 'NZ Center', 75, 125, 28.3, 56.7, 'N', 'low', 'center'),
        ('MZ06', 'nz_right', 'NZ Right', 75, 125, 56.7, 85, 'N', 'low', 'right'),
        # Defensive zone
        ('MZ07', 'dz_left', 'DZ Left', 0, 75, 0, 28.3, 'D', 'low', 'left'),
        ('MZ08', 'dz_center', 'DZ Center', 0, 75, 28.3, 56.7, 'D', 'low', 'center'),
        ('MZ09', 'dz_right', 'DZ Right', 0, 75, 56.7, 85, 'D', 'low', 'right'),
    ]
    for z in medium_zones:
        zones.append({
            'rink_zone_id': z[0], 'zone_code': z[1], 'zone_name': z[2], 'granularity': 'medium',
            'x_min': z[3], 'x_max': z[4], 'y_min': z[5], 'y_max': z[6],
            'zone': z[7], 'danger': z[8], 'side': z[9], 'x_description': '', 'y_description': ''
        })
    
    # Fine zones (detailed grid - 10x10ft squares = ~170 zones)
    # For the offensive zone, we add danger-based zones
    danger_zones = [
        # High danger - inner slot
        ('FZ_HD01', 'high_danger_slot', 'High Danger Slot', 'fine', 180, 189, 32, 53, 'O', 'high', 'center', 'inner slot', 'between posts'),
        # Medium danger - slot
        ('FZ_MD01', 'med_danger_left', 'Medium Danger Left', 'fine', 169, 180, 22, 32, 'O', 'medium', 'left', 'slot', 'left side'),
        ('FZ_MD02', 'med_danger_center', 'Medium Danger Center', 'fine', 169, 180, 32, 53, 'O', 'medium', 'center', 'slot', 'center'),
        ('FZ_MD03', 'med_danger_right', 'Medium Danger Right', 'fine', 169, 180, 53, 63, 'O', 'medium', 'right', 'slot', 'right side'),
        # Low danger - outside slot
        ('FZ_LD01', 'low_danger_left_circle', 'Low Danger Left Circle', 'fine', 150, 175, 0, 22, 'O', 'low', 'left', 'circle', 'boards'),
        ('FZ_LD02', 'low_danger_right_circle', 'Low Danger Right Circle', 'fine', 150, 175, 63, 85, 'O', 'low', 'right', 'circle', 'boards'),
        ('FZ_LD03', 'low_danger_point_left', 'Low Danger Point Left', 'fine', 125, 150, 0, 30, 'O', 'low', 'left', 'point', 'boards'),
        ('FZ_LD04', 'low_danger_point_center', 'Low Danger Point Center', 'fine', 125, 150, 30, 55, 'O', 'low', 'center', 'point', 'center'),
        ('FZ_LD05', 'low_danger_point_right', 'Low Danger Point Right', 'fine', 125, 150, 55, 85, 'O', 'low', 'right', 'point', 'boards'),
    ]
    for z in danger_zones:
        zones.append({
            'rink_zone_id': z[0], 'zone_code': z[1], 'zone_name': z[2], 'granularity': z[3],
            'x_min': z[4], 'x_max': z[5], 'y_min': z[6], 'y_max': z[7],
            'zone': z[8], 'danger': z[9], 'side': z[10], 'x_description': z[11], 'y_description': z[12]
        })
    
    # Add grid zones (10ft x 10ft) for full coverage
    grid_id = 1
    for x_start in range(0, 200, 10):
        for y_start in range(0, 85, 10):
            x_end = min(x_start + 10, 200)
            y_end = min(y_start + 10, 85)
            
            # Determine zone
            if x_start >= 125:
                zone = 'O'
            elif x_start >= 75:
                zone = 'N'
            else:
                zone = 'D'
            
            # Determine side
            if y_end <= 35:
                side = 'left'
            elif y_start >= 50:
                side = 'right'
            else:
                side = 'center'
            
            # Determine danger (only for OZ)
            if zone == 'O' and x_start >= 180 and 32 <= y_start <= 53:
                danger = 'high'
            elif zone == 'O' and x_start >= 169 and 22 <= y_start <= 63:
                danger = 'medium'
            elif zone == 'O':
                danger = 'low'
            else:
                danger = 'none'
            
            zones.append({
                'rink_zone_id': f'GZ{grid_id:03d}',
                'zone_code': f'grid_{x_start}_{y_start}',
                'zone_name': f'Grid ({x_start},{y_start})',
                'granularity': 'grid',
                'x_min': x_start, 'x_max': x_end,
                'y_min': y_start, 'y_max': y_end,
                'zone': zone, 'danger': danger, 'side': side,
                'x_description': f'{x_start}-{x_end}ft',
                'y_description': f'{y_start}-{y_end}ft'
            })
            grid_id += 1
    
    return pd.DataFrame(zones)


def create_dim_save_outcome() -> pd.DataFrame:
    """Save outcome types."""
    return pd.DataFrame({
        'save_outcome_id': ['SO01', 'SO02', 'SO03'],
        'save_outcome_code': ['rebound', 'freeze', 'deflect'],
        'save_outcome_name': ['Rebound', 'Freeze', 'Deflect'],
        'causes_stoppage': [False, True, False]
    })


def create_dim_shift_slot() -> pd.DataFrame:
    """Shift position slots."""
    return pd.DataFrame({
        'slot_id': ['SL01', 'SL02', 'SL03', 'SL04', 'SL05', 'SL06', 'SL07'],
        'slot_code': ['F1', 'F2', 'F3', 'D1', 'D2', 'G', 'X'],
        'slot_name': ['Forward 1', 'Forward 2', 'Forward 3', 'Defense 1', 'Defense 2', 'Goalie', 'Extra']
    })


def create_dim_shot_outcome() -> pd.DataFrame:
    """Shot outcome definitions."""
    return pd.DataFrame({
        'shot_outcome_id': ['SH01', 'SH02', 'SH03', 'SH04', 'SH05'],
        'shot_outcome_code': ['goal', 'save', 'block', 'miss', 'post'],
        'shot_outcome_name': ['Goal', 'Save', 'Blocked', 'Missed', 'Post/Crossbar'],
        'is_goal': [True, False, False, False, False],
        'is_save': [False, True, False, False, False],
        'is_block': [False, False, True, False, False],
        'is_miss': [False, False, False, True, True],
        'xg_multiplier': [1.0, 0.0, 0.0, 0.0, 0.0]
    })


def create_dim_stat() -> pd.DataFrame:
    """Comprehensive stat definitions with metadata."""
    stats = [
        # Scoring
        ('ST001', 'goals', 'Goals', 'scoring', 'Goals scored', 'count', 'all', True, 0.5, 0.3, 0.5, 0),
        ('ST002', 'assists', 'Assists', 'scoring', 'Primary + secondary assists', 'count', 'all', True, 0.6, 0.4, 0.8, 0),
        ('ST003', 'points', 'Points', 'scoring', 'Goals + assists', 'G + A', 'all', True, 1.0, 0.7, 1.2, 0),
        ('ST004', 'primary_assists', 'Primary Assists', 'scoring', 'Last pass before goal', 'count', 'all', True, 0.4, 0.25, 0.5, 0),
        ('ST005', 'secondary_assists', 'Secondary Assists', 'scoring', 'Second-to-last pass', 'count', 'all', True, 0.2, 0.15, 0.3, 0),
        # Shooting
        ('ST010', 'shots', 'Shots', 'shooting', 'Total shot attempts', 'count', 'all', True, 3.0, 2.5, 4.0, 0),
        ('ST011', 'sog', 'Shots on Goal', 'shooting', 'Shots that reach goalie', 'count', 'all', True, 2.0, 1.8, 3.0, 0),
        ('ST012', 'shots_blocked', 'Shots Blocked', 'shooting', 'Shots blocked by opponent', 'count', 'all', True, 0.5, 0.4, 0.8, 0),
        ('ST013', 'shots_missed', 'Shots Missed', 'shooting', 'Shots that miss net', 'count', 'all', True, 0.5, 0.3, 0.6, 0),
        ('ST014', 'shooting_pct', 'Shooting %', 'shooting', 'Goals / SOG', 'G / SOG * 100', 'all', True, 15, 10, 20, 0),
        # Passing
        ('ST020', 'pass_attempts', 'Pass Attempts', 'passing', 'Total passes attempted', 'count', 'all', True, 25, 20, 35, 0),
        ('ST021', 'pass_completed', 'Passes Completed', 'passing', 'Successful passes', 'count', 'all', True, 20, 16, 28, 0),
        ('ST022', 'pass_pct', 'Pass %', 'passing', 'Completion rate', 'comp / att * 100', 'all', True, 85, 75, 90, 50),
        ('ST023', 'dangerous_passes', 'Dangerous Passes', 'passing', 'Passes leading to chances', 'count', 'all', True, 3, 2, 5, 0),
        # Faceoffs
        ('ST030', 'fo_wins', 'Faceoff Wins', 'faceoffs', 'Faceoffs won', 'count', 'center', True, 8, 6, 12, 0),
        ('ST031', 'fo_losses', 'Faceoff Losses', 'faceoffs', 'Faceoffs lost', 'count', 'center', True, 8, 6, 12, 0),
        ('ST032', 'fo_pct', 'Faceoff %', 'faceoffs', 'Win rate', 'wins / total * 100', 'center', True, 55, 45, 60, 40),
        # Possession
        ('ST040', 'zone_entries', 'Zone Entries', 'possession', 'Offensive zone entries', 'count', 'all', True, 4, 3, 6, 0),
        ('ST041', 'zone_exits', 'Zone Exits', 'possession', 'Defensive zone exits', 'count', 'all', True, 4, 3, 6, 0),
        ('ST042', 'controlled_entries', 'Controlled Entries', 'possession', 'Entries with control', 'count', 'all', True, 2, 1.5, 3, 0),
        ('ST043', 'controlled_exits', 'Controlled Exits', 'possession', 'Exits with control', 'count', 'all', True, 2, 1.5, 3, 0),
        # Turnovers
        ('ST050', 'giveaways', 'Giveaways', 'turnovers', 'Turnovers committed', 'count', 'all', True, 2, 1.5, 3, 0),
        ('ST051', 'takeaways', 'Takeaways', 'turnovers', 'Turnovers forced', 'count', 'all', True, 1.5, 1, 2.5, 0),
        ('ST052', 'turnover_diff', 'Turnover Diff', 'turnovers', 'Takeaways - giveaways', 'TA - GA', 'all', True, 0, -1, 1, -5),
        # Defense
        ('ST060', 'blocks', 'Blocks', 'defense', 'Shots blocked', 'count', 'defense', True, 2, 1.5, 3.5, 0),
        ('ST061', 'hits', 'Hits', 'defense', 'Body checks', 'count', 'all', True, 2, 1, 4, 0),
        # Time
        ('ST070', 'toi_seconds', 'TOI (sec)', 'time', 'Time on ice in seconds', 'sum', 'all', True, 900, 600, 1200, 0),
        ('ST071', 'toi_minutes', 'TOI (min)', 'time', 'Time on ice in minutes', 'sum / 60', 'all', True, 15, 10, 20, 0),
        ('ST072', 'shift_count', 'Shifts', 'time', 'Number of shifts', 'count', 'all', True, 15, 12, 20, 0),
        ('ST073', 'avg_shift', 'Avg Shift', 'time', 'Average shift length', 'TOI / shifts', 'all', True, 60, 45, 75, 0),
        # Advanced
        ('ST080', 'corsi_for', 'Corsi For', 'advanced', 'Shot attempts for', 'count', 'all', True, 8, 6, 12, 0),
        ('ST081', 'corsi_against', 'Corsi Against', 'advanced', 'Shot attempts against', 'count', 'all', True, 8, 6, 12, 0),
        ('ST082', 'cf_pct', 'CF%', 'advanced', 'Corsi for %', 'CF / (CF+CA) * 100', 'all', True, 55, 45, 60, 40),
        ('ST083', 'fenwick_for', 'Fenwick For', 'advanced', 'Unblocked attempts for', 'count', 'all', True, 6, 5, 9, 0),
        ('ST084', 'fenwick_against', 'Fenwick Against', 'advanced', 'Unblocked attempts against', 'count', 'all', True, 6, 5, 9, 0),
        ('ST085', 'ff_pct', 'FF%', 'advanced', 'Fenwick for %', 'FF / (FF+FA) * 100', 'all', True, 55, 45, 60, 40),
        ('ST086', 'xgf', 'xGF', 'advanced', 'Expected goals for', 'sum xG', 'all', False, 1.5, 1.0, 2.5, 0),
        ('ST087', 'xga', 'xGA', 'advanced', 'Expected goals against', 'sum xG', 'all', False, 1.5, 1.0, 2.5, 0),
        ('ST088', 'plus_minus', '+/-', 'advanced', 'Plus minus', 'GF - GA on ice', 'all', True, 0.5, 0, 1, -3),
    ]
    
    columns = ['stat_id', 'stat_code', 'stat_name', 'category', 'description', 'formula', 
               'player_role', 'computable_now', 'benchmark_elite', 'nhl_avg_per_game', 
               'nhl_elite_threshold', 'nhl_min_threshold']
    return pd.DataFrame(stats, columns=columns)


def create_dim_stat_category() -> pd.DataFrame:
    """Stat category groupings."""
    return pd.DataFrame({
        'stat_category_id': ['SC01', 'SC02', 'SC03', 'SC04', 'SC05', 'SC06', 'SC07', 
                            'SC08', 'SC09', 'SC10', 'SC11', 'SC12', 'SC13'],
        'category_code': ['scoring', 'shooting', 'passing', 'faceoffs', 'possession', 
                         'turnovers', 'defense', 'time', 'advanced', 'micro', 
                         'rating', 'special_teams', 'goalie'],
        'category_name': ['Scoring', 'Shooting', 'Passing', 'Faceoffs', 'Possession',
                         'Turnovers', 'Defense', 'Time on Ice', 'Advanced Stats', 
                         'Micro Stats', 'Ratings', 'Special Teams', 'Goaltending'],
        'description': [
            'Goals, assists, points',
            'Shots, accuracy, danger',
            'Pass attempts, completion, quality',
            'Faceoff wins, losses, percentage',
            'Zone entries, exits, control',
            'Giveaways, takeaways, differential',
            'Blocks, hits, defensive plays',
            'Ice time, shifts, averages',
            'Corsi, Fenwick, expected goals',
            'Detailed play-by-play actions',
            'Performance ratings and scores',
            'Power play and penalty kill',
            'Saves, goals against, save %'
        ]
    })


def create_dim_stat_type() -> pd.DataFrame:
    """Stat type definitions (count, rate, percentage, etc.)."""
    types = [
        ('STY01', 'count', 'counting', 'game', True, 'Raw count of events'),
        ('STY02', 'rate_60', 'rate', 'game', True, 'Per 60 minutes rate'),
        ('STY03', 'percentage', 'rate', 'game', True, 'Success rate %'),
        ('STY04', 'differential', 'delta', 'game', True, 'For minus against'),
        ('STY05', 'cumulative', 'counting', 'season', True, 'Season total'),
        ('STY06', 'average', 'rate', 'season', True, 'Per game average'),
        ('STY07', 'xg_based', 'advanced', 'game', False, 'Requires XY data'),
        ('STY08', 'rating', 'composite', 'game', True, 'Calculated rating'),
    ]
    return pd.DataFrame(types, columns=['stat_id', 'stat_name', 'stat_category', 
                                        'stat_level', 'computable_now', 'description'])


def create_dim_strength() -> pd.DataFrame:
    """Game strength/situation definitions."""
    strengths = [
        ('STR01', '5v5', '5 on 5', 'even', 1.0, 'Even strength', 0.75),
        ('STR02', '5v4', '5 on 4', 'pp', 1.3, 'Power play', 0.08),
        ('STR03', '4v5', '4 on 5', 'pk', 0.7, 'Penalty kill', 0.08),
        ('STR04', '5v3', '5 on 3', 'pp', 1.6, 'Double minor PP', 0.02),
        ('STR05', '3v5', '3 on 5', 'pk', 0.5, 'Double minor PK', 0.02),
        ('STR06', '4v4', '4 on 4', 'even', 1.1, 'Four on four', 0.03),
        ('STR07', '3v3', '3 on 3', 'even', 1.2, 'Three on three', 0.01),
        ('STR08', '4v3', '4 on 3', 'pp', 1.4, 'PP advantage', 0.01),
        ('STR09', '3v4', '3 on 4', 'pk', 0.6, 'PK disadvantage', 0.01),
        ('STR10', '6v5', '6 on 5', 'en', 1.4, 'Empty net pull', 0.02),
        ('STR11', '5v6', '5 on 6', 'en_d', 0.8, 'Defending empty net', 0.02),
        ('STR12', '6v4', '6 on 4', 'en_pp', 1.5, 'EN + PP', 0.01),
        ('STR13', '4v6', '4 on 6', 'en_pk', 0.6, 'EN + PK', 0.01),
        ('STR14', '6v3', '6 on 3', 'en_pp', 1.7, 'EN + double PP', 0.005),
        ('STR15', '3v6', '3 on 6', 'en_pk', 0.4, 'EN + double PK', 0.005),
        ('STR16', 'all', 'All Situations', 'all', 1.0, 'Combined', 1.0),
        ('STR17', 'ev', 'Even Strength', 'ev', 1.0, '5v5 + 4v4 + 3v3', 0.79),
        ('STR18', 'pp_all', 'All Power Play', 'pp', 1.0, 'All PP situations', 0.12),
    ]
    columns = ['strength_id', 'strength_code', 'strength_name', 'situation_type', 
               'xg_multiplier', 'description', 'avg_toi_pct']
    return pd.DataFrame(strengths, columns=columns)


def create_dim_terminology_mapping() -> pd.DataFrame:
    """Map old terminology to new standardized terms."""
    mappings = [
        # Event types
        ('event_type', 'Shot', 'Shot', 'exact'),
        ('event_type', 'Pass', 'Pass', 'exact'),
        ('event_type', 'Faceoff', 'Faceoff', 'exact'),
        ('event_type', 'Zone_Entry_Exit', 'Zone_Entry_Exit', 'exact'),
        ('event_type', 'Turnover', 'Turnover', 'exact'),
        ('event_type', 'Save', 'Save', 'exact'),
        ('event_type', 'Goal', 'Goal', 'exact'),
        # Shot details
        ('event_detail', 'Shot_OnNet', 'Shot_OnNetSaved', 'contains'),
        ('event_detail', 'Shot_Goal', 'Goal_Scored', 'contains'),
        ('event_detail', 'Shot_Missed', 'Shot_Missed', 'exact'),
        ('event_detail', 'Shot_Blocked', 'Shot_Blocked', 'exact'),
        # Zones
        ('zone', 'o', 'O', 'exact'),
        ('zone', 'd', 'D', 'exact'),
        ('zone', 'n', 'N', 'exact'),
        ('zone', 'offensive', 'O', 'contains'),
        ('zone', 'defensive', 'D', 'contains'),
        ('zone', 'neutral', 'N', 'contains'),
        # Positions
        ('position', 'F', 'Forward', 'exact'),
        ('position', 'D', 'Defense', 'exact'),
        ('position', 'G', 'Goalie', 'exact'),
        ('position', 'C', 'Center', 'exact'),
        ('position', 'LW', 'Left Wing', 'exact'),
        ('position', 'RW', 'Right Wing', 'exact'),
    ]
    columns = ['dimension', 'old_value', 'new_value', 'match_type']
    return pd.DataFrame(mappings, columns=columns)


def create_dim_turnover_quality() -> pd.DataFrame:
    """Turnover quality categories."""
    return pd.DataFrame({
        'turnover_quality_id': ['TQ01', 'TQ02', 'TQ03'],
        'turnover_quality_code': ['good', 'neutral', 'bad'],
        'turnover_quality_name': ['Good Turnover', 'Neutral Turnover', 'Bad Turnover'],
        'description': [
            'Defensive zone, low danger',
            'Neutral zone or forced error',
            'Offensive zone or high danger area'
        ],
        'counts_against': [False, True, True]
    })


def create_dim_turnover_type() -> pd.DataFrame:
    """Detailed turnover type definitions."""
    turnovers = [
        # Giveaways
        ('TO01', 'giveaway_pass_intercept', 'Pass Intercepted', 'giveaway', 'bad', 1.0, 'Pass picked off', 'any', 1.0, 'Pass_Intercepted'),
        ('TO02', 'giveaway_bad_pass', 'Bad Pass', 'giveaway', 'bad', 1.0, 'Pass to nobody', 'any', 1.0, 'Pass_Missed'),
        ('TO03', 'giveaway_puck_lost', 'Puck Lost', 'giveaway', 'neutral', 0.8, 'Lost possession', 'any', 1.0, 'PuckLost'),
        ('TO04', 'giveaway_forced', 'Forced Turnover', 'giveaway', 'neutral', 0.6, 'Under pressure', 'any', 0.8, 'Forced'),
        ('TO05', 'giveaway_zone_clear_fail', 'Failed Clear', 'giveaway', 'bad', 1.2, 'Defensive zone', 'D', 1.5, 'ZoneClear_Fail'),
        ('TO06', 'giveaway_dump_fail', 'Failed Dump', 'giveaway', 'neutral', 0.5, 'Dump and no chase', 'any', 0.5, 'DumpIn_Fail'),
        # Takeaways
        ('TO10', 'takeaway_stick_check', 'Stick Check', 'takeaway', 'good', 1.0, 'Poke or lift', 'any', 1.0, 'StickCheck'),
        ('TO11', 'takeaway_intercept', 'Interception', 'takeaway', 'good', 1.2, 'Read the play', 'any', 1.0, 'Intercept'),
        ('TO12', 'takeaway_body_check', 'Body Check', 'takeaway', 'good', 1.0, 'Physical separation', 'any', 1.0, 'BodyCheck'),
        ('TO13', 'takeaway_forecheck', 'Forecheck Win', 'takeaway', 'good', 1.1, 'Won on forecheck', 'O', 1.2, 'Forecheck'),
        ('TO14', 'takeaway_backcheck', 'Backcheck Win', 'takeaway', 'good', 1.1, 'Won on backcheck', 'D', 1.2, 'Backcheck'),
        ('TO15', 'takeaway_battle', 'Battle Win', 'takeaway', 'good', 0.9, 'Won puck battle', 'any', 1.0, 'BattleWin'),
    ]
    columns = ['turnover_type_id', 'turnover_type_code', 'turnover_type_name', 'category', 
               'quality', 'weight', 'description', 'zone_context', 'zone_danger_multiplier', 'old_equiv']
    return pd.DataFrame(turnovers, columns=columns)


def create_dim_video_type() -> pd.DataFrame:
    """
    Video type dimension table.
    
    Defines all possible video types (Full_Ice, Broadcast, Highlights, etc.)
    with descriptions and metadata.
    """
    video_types = [
        # (video_type_id, video_type_code, video_type_name, description, is_primary, sort_order, use_for_highlights)
        ('VT0001', 'Full_Ice', 'Full Ice', 'Full ice camera view of entire game', True, 1, True),
        ('VT0002', 'Broadcast', 'Broadcast', 'Television/streaming broadcast feed', True, 2, False),
        ('VT0003', 'Highlights', 'Highlights', 'Compilation of game highlights', False, 3, False),
        ('VT0004', 'Goalie', 'Goalie Camera', 'Goalie camera view', False, 4, False),
        ('VT0005', 'Overhead', 'Overhead', 'Overhead camera view', False, 5, False),
        ('VT0006', 'Wide', 'Wide Angle', 'Wide angle camera view', False, 6, False),
        ('VT0007', 'Tight', 'Tight Shot', 'Tight/close-up camera view', False, 7, False),
        ('VT0008', 'Replay', 'Replay', 'Replay/instant replay footage', False, 8, False),
        ('VT0009', 'Other', 'Other', 'Other video type', False, 9, False),
        ('VT0010', 'Goalie_Home', 'Goalie Camera (Home)', 'Goalie camera view from home end', False, 10, False),
        ('VT0011', 'Goalie_Away', 'Goalie Camera (Away)', 'Goalie camera view from away end', False, 11, False),
        ('VT0012', 'Overhead_Home', 'Overhead (Home)', 'Overhead camera view from home end', False, 12, False),
        ('VT0013', 'Overhead_Away', 'Overhead (Away)', 'Overhead camera view from away end', False, 13, False),
        ('VT0014', 'Wide_Home', 'Wide Angle (Home)', 'Wide angle camera view from home end', False, 14, False),
        ('VT0015', 'Wide_Away', 'Wide Angle (Away)', 'Wide angle camera view from away end', False, 15, False),
        ('VT0016', 'Other_Home', 'Other (Home)', 'Other video type from home end', False, 16, False),
        ('VT0017', 'Other_Away', 'Other (Away)', 'Other video type from away end', False, 17, False),
    ]
    
    df = pd.DataFrame(video_types, columns=[
        'video_type_id',
        'video_type_code',
        'video_type_name',
        'description',
        'is_primary',
        'sort_order',
        'use_for_highlights'
    ])
    
    return df


def create_dim_highlight_category() -> pd.DataFrame:
    """
    Highlight category dimension table.
    
    Categorizes highlights by type/importance for filtering and organization.
    Highlights can be linked to event types, but this provides additional categorization.
    """
    categories = [
        # (highlight_category_id, highlight_category_code, highlight_category_name, description, priority, icon)
        ('HC0001', 'Goal', 'Goal', 'Goals scored', 1, '🏒'),
        ('HC0002', 'Save', 'Save', 'Outstanding saves', 2, '🥅'),
        ('HC0003', 'Hit', 'Hit', 'Big hits/body checks', 3, '💥'),
        ('HC0004', 'Fight', 'Fight', 'Fights', 4, '👊'),
        ('HC0005', 'Breakaway', 'Breakaway', 'Breakaway chances', 5, '⚡'),
        ('HC0006', 'Penalty_Shot', 'Penalty Shot', 'Penalty shots', 6, '🎯'),
        ('HC0007', 'Sequence', 'Sequence', 'Multi-event sequences', 7, '🔄'),
        ('HC0008', 'Momentum', 'Momentum Shift', 'Momentum-changing plays', 8, '📈'),
        ('HC0009', 'Skill', 'Skill Play', 'Exceptional skill displays', 9, '⭐'),
        ('HC0010', 'Other', 'Other', 'Other highlights', 10, '📹'),
    ]
    
    df = pd.DataFrame(categories, columns=[
        'highlight_category_id',
        'highlight_category_code',
        'highlight_category_name',
        'description',
        'priority',
        'icon'
    ])
    
    return df


def create_dim_zone_outcome() -> pd.DataFrame:
    """Zone entry/exit outcome types."""
    return pd.DataFrame({
        'zone_outcome_id': ['ZO01', 'ZO02', 'ZO03', 'ZO04', 'ZO05', 'ZO06'],
        'zone_outcome_code': ['controlled_entry', 'dump_entry', 'failed_entry',
                              'controlled_exit', 'clear_exit', 'failed_exit'],
        'zone_outcome_name': ['Controlled Entry', 'Dump & Chase', 'Failed Entry',
                              'Controlled Exit', 'Clear', 'Failed Exit'],
        'is_controlled': [True, False, False, True, False, False],
        'zone_type': ['entry', 'entry', 'entry', 'exit', 'exit', 'exit']
    })


def create_all_dimension_tables():
    """
    Create ALL missing dimension tables.
    
    Returns:
        dict: Table name -> row count
    """
    print("\n" + "=" * 70)
    print("CREATING MISSING DIMENSION TABLES")
    print("=" * 70)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    tables = {
        'dim_comparison_type': create_dim_comparison_type,
        'dim_competition_tier': create_dim_competition_tier,
        'dim_composite_rating': create_dim_composite_rating,
        'dim_danger_zone': create_dim_danger_zone,
        'dim_micro_stat': create_dim_micro_stat,
        'dim_net_location': create_dim_net_location,
        'dim_pass_outcome': create_dim_pass_outcome,
        'dim_rating': create_dim_rating,
        'dim_rating_matchup': create_dim_rating_matchup,
        'dim_rink_zone': create_dim_rink_zone,
        'dim_save_outcome': create_dim_save_outcome,
        'dim_shift_slot': create_dim_shift_slot,
        'dim_shot_outcome': create_dim_shot_outcome,
        'dim_stat': create_dim_stat,
        'dim_stat_category': create_dim_stat_category,
        'dim_stat_type': create_dim_stat_type,
        'dim_strength': create_dim_strength,
        'dim_terminology_mapping': create_dim_terminology_mapping,
        'dim_turnover_quality': create_dim_turnover_quality,
        'dim_turnover_type': create_dim_turnover_type,
        'dim_video_type': create_dim_video_type,
        'dim_highlight_category': create_dim_highlight_category,
        'dim_zone_outcome': create_dim_zone_outcome,
    }
    
    results = {}
    for name, builder in tables.items():
        try:
            df = builder()
            rows = save_table(df, name)
            results[name] = rows
            print(f"  ✓ {name}: {rows} rows")
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            results[name] = 0
    
    print(f"\nCreated {len([r for r in results.values() if r > 0])} dimension tables")
    return results


if __name__ == "__main__":
    create_all_dimension_tables()
