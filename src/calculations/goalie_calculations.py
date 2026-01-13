"""
Goalie Calculation Functions

Extracted goalie calculation logic from core_facts.py for better organization,
testability, and maintainability.

Version: 29.7
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional

# Constants (should match core_facts.py)
LEAGUE_AVG_SV_PCT = 88.0
GOALS_PER_WIN = 4.5
GAMES_PER_SEASON = 20

GOALIE_GAR_WEIGHTS = {
    'goals_prevented': 1.0,
    'high_danger_saves': 0.15,
    'quality_start_bonus': 0.5,
    'rebound_control': 0.1,
}


def calculate_goalie_core_stats(
    goalie_saves: pd.DataFrame,
    goalie_goals_against: pd.DataFrame
) -> Dict:
    """
    Calculate core goalie statistics (saves, goals_against, save_pct).
    
    Args:
        goalie_saves: DataFrame of save events for this goalie
        goalie_goals_against: DataFrame of goal events against this goalie
        
    Returns:
        Dict with core stats: saves, goals_against, shots_against, save_pct
    """
    stats = {}
    stats['saves'] = len(goalie_saves)
    stats['goals_against'] = len(goalie_goals_against)
    stats['shots_against'] = stats['saves'] + stats['goals_against']
    stats['save_pct'] = round(stats['saves'] / stats['shots_against'] * 100, 1) if stats['shots_against'] > 0 else 100.0
    
    return stats


def calculate_goalie_save_types(goalie_saves: pd.DataFrame) -> Dict:
    """
    Calculate save type breakdown (butterfly, pad, glove, blocker, etc.).
    
    Args:
        goalie_saves: DataFrame of save events with event_detail_2 column
        
    Returns:
        Dict with save type counts
    """
    stats = {}
    
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
    
    return stats


def calculate_goalie_high_danger(
    opp_shots: pd.DataFrame
) -> Dict:
    """
    Calculate high danger save statistics.
    
    Args:
        opp_shots: DataFrame of opponent shot/goal events
        
    Returns:
        Dict with hd_shots_against, hd_goals_against, hd_saves, hd_save_pct
    """
    stats = {}
    
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
    
    return stats


def calculate_goalie_rebound_control(
    goalie_saves: pd.DataFrame,
    all_rebounds: pd.DataFrame,
    stats: Dict
) -> Dict:
    """
    Calculate rebound control advanced statistics.
    
    Args:
        goalie_saves: DataFrame of save events
        all_rebounds: DataFrame of rebound events
        stats: Existing stats dict (will be updated)
        
    Returns:
        Dict with rebound control stats
    """
    # Freeze vs rebound from saves
    if 'event_detail' in goalie_saves.columns:
        save_details = goalie_saves['event_detail'].astype(str)
        stats['saves_freeze'] = len(save_details[save_details.str.contains('Freeze', na=False, case=False)])
        stats['saves_rebound'] = len(save_details[save_details.str.contains('Rebound', na=False, case=False)])
    else:
        stats['saves_freeze'] = stats.get('saves_glove', 0) + stats.get('saves_chest', 0)
        stats['saves_rebound'] = stats['saves'] - stats['saves_freeze']
    
    stats['freeze_pct'] = round(stats['saves_freeze'] / stats['saves'] * 100, 1) if stats['saves'] > 0 else 0.0
    stats['rebound_rate'] = round(stats['saves_rebound'] / stats['saves'] * 100, 1) if stats['saves'] > 0 else 0.0
    
    # Analyze rebound outcomes
    if 'prev_event_id' in all_rebounds.columns and 'event_id' in goalie_saves.columns:
        goalie_save_ids = set(goalie_saves['event_id'].astype(str).tolist())
        goalie_rebounds = all_rebounds[all_rebounds['prev_event_id'].astype(str).isin(goalie_save_ids)]
    else:
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
    
    total_rebounds = (stats['rebounds_team_recovered'] + stats['rebounds_opp_recovered'] + 
                     stats['rebounds_shot_generated'] + stats['rebounds_flurry_generated'])
    stats['rebound_control_rate'] = round(stats['rebounds_team_recovered'] / total_rebounds * 100, 1) if total_rebounds > 0 else 100.0
    stats['rebound_danger_rate'] = round((stats['rebounds_shot_generated'] + stats['rebounds_flurry_generated']) / total_rebounds * 100, 1) if total_rebounds > 0 else 0.0
    
    # Second chance analysis
    stats['second_chance_shots_against'] = stats['rebounds_shot_generated'] + stats['rebounds_flurry_generated']
    stats['second_chance_goals_against'] = 0  # Would need sequence analysis
    stats['second_chance_sv_pct'] = 100.0 if stats['second_chance_shots_against'] == 0 else round((stats['second_chance_shots_against'] - stats['second_chance_goals_against']) / stats['second_chance_shots_against'] * 100, 1)
    stats['dangerous_rebound_pct'] = stats['rebound_danger_rate']
    
    return stats


def calculate_goalie_period_splits(
    goalie_saves: pd.DataFrame,
    goalie_goals_against: pd.DataFrame
) -> Dict:
    """
    Calculate period-by-period statistics.
    
    Args:
        goalie_saves: DataFrame of save events
        goalie_goals_against: DataFrame of goal events
        
    Returns:
        Dict with period split stats (p1_saves, p2_saves, etc.)
    """
    stats = {}
    
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
    
    active_periods = {p: sv for p, sv in period_sv_pcts.items() if period_sas[p] > 0}
    if active_periods:
        stats['best_period'] = max(active_periods, key=active_periods.get)
        stats['worst_period'] = min(active_periods, key=active_periods.get)
        sv_pct_values = list(active_periods.values())
        stats['period_consistency'] = round(np.std(sv_pct_values), 2) if len(sv_pct_values) > 1 else 0.0
    else:
        stats['best_period'] = stats['worst_period'] = 0
        stats['period_consistency'] = 0.0
    
    return stats


def calculate_goalie_time_buckets(
    detailed_saves: pd.DataFrame,
    goalie_goals_against: pd.DataFrame
) -> Dict:
    """
    Calculate time bucket / clutch statistics.
    
    Args:
        detailed_saves: DataFrame of save events with time_bucket_id
        goalie_goals_against: DataFrame of goal events
        
    Returns:
        Dict with time bucket stats
    """
    stats = {}
    
    if 'time_bucket_id' in detailed_saves.columns:
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
    
    return stats


def calculate_goalie_shot_context(
    detailed_saves: pd.DataFrame,
    goalie_goals_against: pd.DataFrame,
    stats: Dict
) -> Dict:
    """
    Calculate shot context statistics (rush vs set play).
    
    Args:
        detailed_saves: DataFrame of save events with time_since_zone_entry
        goalie_goals_against: DataFrame of goal events
        stats: Existing stats dict (will be updated)
        
    Returns:
        Dict with shot context stats
    """
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
    
    if 'time_since_zone_entry' in goalie_goals_against.columns:
        ga_tsze = goalie_goals_against['time_since_zone_entry'].fillna(999)
        stats['rush_goals_against'] = len(goalie_goals_against[ga_tsze < 5])
        stats['quick_attack_ga'] = len(goalie_goals_against[(ga_tsze >= 5) & (ga_tsze < 10)])
        stats['set_play_ga'] = len(goalie_goals_against[ga_tsze >= 10])
    else:
        stats['rush_goals_against'] = 0
        stats['quick_attack_ga'] = 0
        stats['set_play_ga'] = 0
    
    # SV% by context
    rush_sa = stats['rush_saves'] + stats['rush_goals_against']
    quick_sa = stats['quick_attack_saves'] + stats['quick_attack_ga']
    set_sa = stats['set_play_saves'] + stats['set_play_ga']
    
    stats['rush_sv_pct'] = round(stats['rush_saves'] / rush_sa * 100, 1) if rush_sa > 0 else 100.0
    stats['quick_attack_sv_pct'] = round(stats['quick_attack_saves'] / quick_sa * 100, 1) if quick_sa > 0 else 100.0
    stats['set_play_sv_pct'] = round(stats['set_play_saves'] / set_sa * 100, 1) if set_sa > 0 else 100.0
    
    stats['rush_pct_of_shots'] = round((stats['rush_saves'] + stats['rush_goals_against']) / stats['shots_against'] * 100, 1) if stats['shots_against'] > 0 else 0.0
    stats['transition_defense_rating'] = round(stats['rush_sv_pct'] - stats['set_play_sv_pct'], 1)
    
    return stats


def calculate_goalie_pressure_handling(
    detailed_saves: pd.DataFrame,
    goalie_goals_against: pd.DataFrame,
    stats: Dict
) -> Dict:
    """
    Calculate pressure / sequence handling statistics.
    
    Args:
        detailed_saves: DataFrame of save events with sequence_shot_count
        goalie_goals_against: DataFrame of goal events
        stats: Existing stats dict (will be updated)
        
    Returns:
        Dict with pressure handling stats
    """
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
    
    stats['sequence_survival_rate'] = round((stats['saves'] - stats['goals_against']) / stats['saves'] * 100, 1) if stats['saves'] > 0 else 100.0
    stats['pressure_handling_index'] = round((stats['multi_shot_sv_pct'] + stats['sustained_pressure_sv_pct']) / 2, 1)
    
    return stats


def calculate_goalie_quality_indicators(stats: Dict) -> Dict:
    """
    Calculate quality indicators (quality start, GSAx, etc.).
    
    Args:
        stats: Existing stats dict (will be updated)
        
    Returns:
        Dict with quality indicator stats
    """
    stats['is_quality_start'] = 1 if (stats['save_pct'] >= 91.7 or stats['goals_against'] <= 2) else 0
    stats['is_bad_start'] = 1 if stats['save_pct'] < 85.0 else 0
    
    # GSAx
    expected = stats['shots_against'] * (1 - LEAGUE_AVG_SV_PCT / 100)
    stats['expected_goals_against'] = round(expected, 2)
    stats['goals_saved_above_avg'] = round(expected - stats['goals_against'], 2)
    
    return stats


def calculate_goalie_composites(stats: Dict) -> Dict:
    """
    Calculate advanced composite ratings.
    
    Args:
        stats: Existing stats dict (will be updated)
        
    Returns:
        Dict with composite rating stats
    """
    # Goalie Game Score
    shutout_bonus = 2.0 if stats['goals_against'] == 0 else 0.0
    stats['goalie_game_score'] = round(stats['saves'] * 0.1 - stats['goals_against'] * 0.75 + shutout_bonus + stats.get('hd_saves', 0) * 0.2, 2)
    
    # Simple xG model
    rush_xg = stats.get('rush_saves', 0) * 0.15 + stats.get('rush_goals_against', 0) * 1.0
    set_xg = stats.get('set_play_saves', 0) * 0.08 + stats.get('set_play_ga', 0) * 1.0
    hd_xg = stats.get('hd_shots_against', 0) * 0.25
    stats['goalie_gax'] = round(rush_xg + set_xg + hd_xg * 0.5, 2)
    stats['goalie_gsax'] = round(stats['goalie_gax'] - stats['goals_against'], 2)
    
    # Clutch rating
    stats['clutch_rating'] = round((stats.get('p3_sv_pct', 0) * 0.4 + stats.get('late_period_sv_pct', 0) * 0.3 + stats.get('final_minute_sv_pct', 0) * 0.3), 1)
    
    # Consistency rating
    stats['consistency_rating'] = round(100 - stats.get('period_consistency', 0) * 2, 1)
    
    # Pressure rating
    stats['pressure_rating'] = stats.get('pressure_handling_index', 0)
    
    # Rebound rating
    stats['rebound_rating'] = round(stats.get('freeze_pct', 0) * 0.4 + stats.get('rebound_control_rate', 0) * 0.4 + (100 - stats.get('rebound_danger_rate', 0)) * 0.2, 1)
    
    # Positioning rating
    controlled_saves = stats.get('saves_glove', 0) + stats.get('saves_blocker', 0) + stats.get('saves_chest', 0)
    stats['positioning_rating'] = round(controlled_saves / stats['saves'] * 100, 1) if stats['saves'] > 0 else 50.0
    
    # Overall game rating
    raw_rating = (stats['save_pct'] - 80) / 4
    raw_rating += stats.get('goalie_gsax', 0) * 0.5
    raw_rating += shutout_bonus * 0.5
    stats['overall_game_rating'] = round(max(1, min(10, raw_rating + 5)), 1)
    
    # Win probability added
    stats['win_probability_added'] = round(stats.get('goals_saved_above_avg', 0) * 0.05, 3)
    
    return stats


def calculate_goalie_war(stats: dict) -> dict:
    """
    Calculate goalie-specific WAR (Wins Above Replacement).
    
    Args:
        stats: Dict with goalie statistics
        
    Returns:
        Dict with WAR components and total WAR
    """
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
