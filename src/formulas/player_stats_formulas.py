"""
Player Stats Formulas

Centralized formula definitions for fact_player_game_stats.

To update a formula, simply modify the definition here - no code changes needed!
"""

import pandas as pd
import numpy as np
from src.calculations import calculate_cf_pct, calculate_ff_pct, calculate_per_60_rate


# =============================================================================
# FORMULA DEFINITIONS
# =============================================================================

PLAYER_STATS_FORMULAS = {
    # ========================================================================
    # PERCENTAGE FORMULAS
    # ========================================================================
    
    'shooting_pct': {
        'type': 'percentage',
        'function': lambda df: (df['goals'] / df['sog'] * 100).where(df['sog'] > 0, 0.0),
        'description': 'Shooting percentage (goals / shots on goal)',
        'dependencies': ['goals', 'sog'],
    },
    
    'pass_pct': {
        'type': 'percentage',
        'function': lambda df: (df['pass_completed'] / df['pass_attempts'] * 100).where(df['pass_attempts'] > 0, 0.0),
        'description': 'Pass completion percentage',
        'dependencies': ['pass_completed', 'pass_attempts'],
    },
    
    'fo_pct': {
        'type': 'percentage',
        'function': lambda df: (df['fo_wins'] / (df['fo_wins'] + df['fo_losses']) * 100).where(
            (df['fo_wins'] + df['fo_losses']) > 0, 0.0
        ),
        'description': 'Faceoff win percentage',
        'dependencies': ['fo_wins', 'fo_losses'],
    },
    
    'cf_pct': {
        'type': 'percentage',
        'function': lambda df: pd.Series([
            calculate_cf_pct(cf, ca) if pd.notna(cf) and pd.notna(ca) else None
            for cf, ca in zip(df['cf'], df['ca'])
        ]),
        'description': 'Corsi For percentage',
        'dependencies': ['cf', 'ca'],
    },
    
    'ff_pct': {
        'type': 'percentage',
        'function': lambda df: pd.Series([
            calculate_ff_pct(ff, fa) if pd.notna(ff) and pd.notna(fa) else None
            for ff, fa in zip(df['ff'], df['fa'])
        ]),
        'description': 'Fenwick For percentage',
        'dependencies': ['ff', 'fa'],
    },
    
    'zone_entry_success_pct': {
        'type': 'percentage',
        'function': lambda df: (df['zone_entries_successful'] / df['zone_entries'] * 100).where(
            df['zone_entries'] > 0, 0.0
        ),
        'description': 'Zone entry success percentage',
        'dependencies': ['zone_entries_successful', 'zone_entries'],
    },
    
    'zone_exit_success_pct': {
        'type': 'percentage',
        'function': lambda df: (df['zone_exits_successful'] / df['zone_exits'] * 100).where(
            df['zone_exits'] > 0, 0.0
        ),
        'description': 'Zone exit success percentage',
        'dependencies': ['zone_exits_successful', 'zone_exits'],
    },
    
    # ========================================================================
    # PER-60 RATE FORMULAS
    # ========================================================================
    
    'goals_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            calculate_per_60_rate(g, toi) if pd.notna(toi) else None
            for g, toi in zip(df['goals'], df['toi_minutes'])
        ]),
        'description': 'Goals per 60 minutes',
        'dependencies': ['goals', 'toi_minutes'],
    },
    
    'assists_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            calculate_per_60_rate(a, toi) if pd.notna(toi) else None
            for a, toi in zip(df['assists'], df['toi_minutes'])
        ]),
        'description': 'Assists per 60 minutes',
        'dependencies': ['assists', 'toi_minutes'],
    },
    
    'points_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            calculate_per_60_rate(p, toi) if pd.notna(toi) else None
            for p, toi in zip(df['points'], df['toi_minutes'])
        ]),
        'description': 'Points per 60 minutes',
        'dependencies': ['points', 'toi_minutes'],
    },
    
    'shots_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            calculate_per_60_rate(s, toi) if pd.notna(toi) else None
            for s, toi in zip(df['shots'], df['toi_minutes'])
        ]),
        'description': 'Shots per 60 minutes',
        'dependencies': ['shots', 'toi_minutes'],
    },
    
    'sog_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            calculate_per_60_rate(sog, toi) if pd.notna(toi) else None
            for sog, toi in zip(df['sog'], df['toi_minutes'])
        ]),
        'description': 'Shots on goal per 60 minutes',
        'dependencies': ['sog', 'toi_minutes'],
    },
    
    'cf_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            calculate_per_60_rate(cf, toi) if pd.notna(toi) else None
            for cf, toi in zip(df['cf'], df['toi_minutes'])
        ]),
        'description': 'Corsi For per 60 minutes',
        'dependencies': ['cf', 'toi_minutes'],
    },
    
    'ca_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            calculate_per_60_rate(ca, toi) if pd.notna(toi) else None
            for ca, toi in zip(df['ca'], df['toi_minutes'])
        ]),
        'description': 'Corsi Against per 60 minutes',
        'dependencies': ['ca', 'toi_minutes'],
    },
    
    # Micro stats per-60 rates
    'dekes_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            calculate_per_60_rate(d, toi) if pd.notna(toi) else None
            for d, toi in zip(df.get('dekes', pd.Series([0]*len(df))), df['toi_minutes'])
        ]),
        'description': 'Dekes per 60 minutes',
        'dependencies': ['dekes', 'toi_minutes'],
    },
    
    'forechecks_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            calculate_per_60_rate(fc, toi) if pd.notna(toi) else None
            for fc, toi in zip(df.get('forechecks', pd.Series([0]*len(df))), df['toi_minutes'])
        ]),
        'description': 'Forechecks per 60 minutes',
        'dependencies': ['forechecks', 'toi_minutes'],
    },
    
    'backchecks_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            calculate_per_60_rate(bc, toi) if pd.notna(toi) else None
            for bc, toi in zip(df.get('backchecks', pd.Series([0]*len(df))), df['toi_minutes'])
        ]),
        'description': 'Backchecks per 60 minutes',
        'dependencies': ['backchecks', 'toi_minutes'],
    },
    
    'puck_battles_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            calculate_per_60_rate(pb, toi) if pd.notna(toi) else None
            for pb, toi in zip(df.get('puck_battles_total', pd.Series([0]*len(df))), df['toi_minutes'])
        ]),
        'description': 'Puck battles per 60 minutes',
        'dependencies': ['puck_battles_total', 'toi_minutes'],
    },
    
    'cycles_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            calculate_per_60_rate(c, toi) if pd.notna(toi) else None
            for c, toi in zip(df.get('cycles', pd.Series([0]*len(df))), df['toi_minutes'])
        ]),
        'description': 'Cycles per 60 minutes',
        'dependencies': ['cycles', 'toi_minutes'],
    },
    
    'screens_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            calculate_per_60_rate(s, toi) if pd.notna(toi) else None
            for s, toi in zip(df.get('screens', pd.Series([0]*len(df))), df['toi_minutes'])
        ]),
        'description': 'Screens per 60 minutes',
        'dependencies': ['screens', 'toi_minutes'],
    },
    
    'poke_checks_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            calculate_per_60_rate(pc, toi) if pd.notna(toi) else None
            for pc, toi in zip(df.get('poke_checks', pd.Series([0]*len(df))), df['toi_minutes'])
        ]),
        'description': 'Poke checks per 60 minutes',
        'dependencies': ['poke_checks', 'toi_minutes'],
    },
    
    'faceoffs_wdbe_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            calculate_per_60_rate(wdbe, toi) if pd.notna(toi) else None
            for wdbe, toi in zip(df.get('faceoffs_wdbe_value', pd.Series([0.0]*len(df))), df['toi_minutes'])
        ]),
        'description': 'WDBE faceoff value per 60 minutes',
        'dependencies': ['faceoffs_wdbe_value', 'toi_minutes'],
    },
    
    # Possession time per-60 rates (convert seconds to minutes, then calculate per-60)
    'possession_time_offensive_zone_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            (po / 60.0 / toi * 60.0) if pd.notna(toi) and toi > 0 else 0.0
            for po, toi in zip(df.get('possession_time_offensive_zone', pd.Series([0]*len(df))), df['toi_minutes'])
        ]),
        'description': 'Possession time in offensive zone per 60 minutes (minutes)',
        'dependencies': ['possession_time_offensive_zone', 'toi_minutes'],
    },
    
    'possession_time_defensive_zone_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            (pd / 60.0 / toi * 60.0) if pd.notna(toi) and toi > 0 else 0.0
            for pd, toi in zip(df.get('possession_time_defensive_zone', pd.Series([0]*len(df))), df['toi_minutes'])
        ]),
        'description': 'Possession time in defensive zone per 60 minutes (minutes)',
        'dependencies': ['possession_time_defensive_zone', 'toi_minutes'],
    },
    
    'possession_time_neutral_zone_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            (pn / 60.0 / toi * 60.0) if pd.notna(toi) and toi > 0 else 0.0
            for pn, toi in zip(df.get('possession_time_neutral_zone', pd.Series([0]*len(df))), df['toi_minutes'])
        ]),
        'description': 'Possession time in neutral zone per 60 minutes (minutes)',
        'dependencies': ['possession_time_neutral_zone', 'toi_minutes'],
    },
    
    'possession_time_total_per_60': {
        'type': 'rate',
        'function': lambda df: pd.Series([
            (pt / 60.0 / toi * 60.0) if pd.notna(toi) and toi > 0 else 0.0
            for pt, toi in zip(df.get('possession_time_total', pd.Series([0]*len(df))), df['toi_minutes'])
        ]),
        'description': 'Total possession time per 60 minutes (minutes)',
        'dependencies': ['possession_time_total', 'toi_minutes'],
    },
    
    # ========================================================================
    # RATIO FORMULAS
    # ========================================================================
    
    'avg_shift_length': {
        'type': 'ratio',
        'function': lambda df: (df['toi_seconds'] / df['shifts'] / 60).where(df['shifts'] > 0, 0.0),
        'description': 'Average shift length in minutes',
        'dependencies': ['toi_seconds', 'shifts'],
    },
    
    'toi_minutes': {
        'type': 'ratio',
        'function': lambda df: df['toi_seconds'] / 60.0,
        'description': 'Time on ice in minutes',
        'dependencies': ['toi_seconds'],
    },
    
    # ========================================================================
    # SUM FORMULAS
    # ========================================================================
    
    'points': {
        'type': 'sum',
        'function': lambda df: df['goals'] + df['assists'],
        'description': 'Total points (goals + assists)',
        'dependencies': ['goals', 'assists'],
    },
    
    'assists': {
        'type': 'sum',
        'function': lambda df: df['primary_assists'] + df['secondary_assists'],
        'description': 'Total assists (primary + secondary)',
        'dependencies': ['primary_assists', 'secondary_assists'],
    },
    
    'shots': {
        'type': 'sum',
        'function': lambda df: df['sog'] + df['shots_blocked'] + df['shots_missed'],
        'description': 'Total shot attempts (SOG + blocked + missed)',
        'dependencies': ['sog', 'shots_blocked', 'shots_missed'],
    },
    
    'turnovers': {
        'type': 'sum',
        'function': lambda df: df['giveaways'] + df['takeaways'],
        'description': 'Total turnovers (giveaways + takeaways)',
        'dependencies': ['giveaways', 'takeaways'],
    },
    
    # ========================================================================
    # DIFFERENCE FORMULAS
    # ========================================================================
    
    'plus_minus': {
        'type': 'difference',
        'function': lambda df: df['plus_total'] - df['minus_total'],
        'description': 'Plus/minus (goals for - goals against)',
        'dependencies': ['plus_total', 'minus_total'],
    },
    
    'corsi_diff': {
        'type': 'difference',
        'function': lambda df: df['cf'] - df['ca'],
        'description': 'Corsi differential',
        'dependencies': ['cf', 'ca'],
    },
    
    'fenwick_diff': {
        'type': 'difference',
        'function': lambda df: df['ff'] - df['fa'],
        'description': 'Fenwick differential',
        'dependencies': ['ff', 'fa'],
    },
}


# =============================================================================
# FORMULA GROUPS (for easy application)
# =============================================================================

FORMULA_GROUPS = {
    'all_percentages': [
        'shooting_pct', 'pass_pct', 'fo_pct', 'cf_pct', 'ff_pct',
        'zone_entry_success_pct', 'zone_exit_success_pct'
    ],
    
    'all_per_60': [
        'goals_per_60', 'assists_per_60', 'points_per_60', 'shots_per_60',
        'sog_per_60', 'cf_per_60', 'ca_per_60',
        'dekes_per_60', 'forechecks_per_60', 'backchecks_per_60',
        'puck_battles_per_60', 'cycles_per_60', 'screens_per_60', 'poke_checks_per_60',
        'possession_time_offensive_zone_per_60', 'possession_time_defensive_zone_per_60',
        'possession_time_neutral_zone_per_60', 'possession_time_total_per_60',
        'faceoffs_wdbe_per_60'
    ],
    
    'all_ratios': [
        'avg_shift_length', 'toi_minutes'
    ],
    
    'all_sums': [
        'points', 'assists', 'shots', 'turnovers'
    ],
    
    'all_differences': [
        'plus_minus', 'corsi_diff', 'fenwick_diff'
    ],
    
    'core_formulas': [
        'shooting_pct', 'cf_pct', 'ff_pct', 'goals_per_60', 'points_per_60',
        'points', 'assists', 'plus_minus'
    ],
}
