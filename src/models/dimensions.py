"""
=============================================================================
DIMENSION TABLE DEFINITIONS
=============================================================================
File: src/models/dimensions.py

PURPOSE:
    Define and generate all dimension tables for the hockey analytics
    data mart. These provide lookup/reference data for fact tables.

DIMENSION TABLES CREATED:
    1. dim_period         - Game periods (1, 2, 3, OT, SO)
    2. dim_event_type     - Event type master (Shot, Pass, Faceoff, etc.)
    3. dim_event_detail   - Event detail master with categorization
    4. dim_play_detail    - Play detail master (micro-stats categories)
    5. dim_shot_type      - Shot types (Wrist, Slap, Snap, etc.)
    6. dim_pass_type      - Pass types (Forehand, Backhand, Saucer, etc.)
    7. dim_zone           - Rink zones (offensive, defensive, neutral)
    8. dim_strength       - Strength situations (5v5, 5v4, 4v5, etc.)
    9. dim_situation      - Game situations (even, pp, pk, en)
    10. dim_position      - Player positions
    11. dim_player_role   - Event player roles
    12. dim_shift_type    - Shift start/stop types
    13. dim_venue         - Home/Away
    14. dim_time_bucket   - Time buckets for period analysis
    15. dim_danger_zone   - Shot danger zones (high/medium/low)

WHY DIMENSION TABLES?
    - Consistent lookups across all fact tables
    - Enable Power BI slicers and filters
    - Reduce data redundancy
    - Provide descriptive attributes for codes
    - Support data quality validation

USAGE:
    from src.models.dimensions import DimensionBuilder
    builder = DimensionBuilder()
    all_dims = builder.build_all()
    
    # Or build from actual data
    dims = builder.build_from_data(events_df, shifts_df)

=============================================================================
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass

# =============================================================================
# STATIC DIMENSION DATA
# =============================================================================
# These are predefined lookup values that don't change

PERIODS = [
    {'period_id': 'P01', 'period_number': 1, 'period_name': '1st Period', 'period_type': 'regulation', 'period_minutes': 18, 'sort_order': 1},
    {'period_id': 'P02', 'period_number': 2, 'period_name': '2nd Period', 'period_type': 'regulation', 'period_minutes': 18, 'sort_order': 2},
    {'period_id': 'P03', 'period_number': 3, 'period_name': '3rd Period', 'period_type': 'regulation', 'period_minutes': 18, 'sort_order': 3},
    {'period_id': 'P04', 'period_number': 4, 'period_name': 'Overtime', 'period_type': 'overtime', 'period_minutes': 5, 'sort_order': 4},
    {'period_id': 'P05', 'period_number': 5, 'period_name': 'Shootout', 'period_type': 'shootout', 'period_minutes': 0, 'sort_order': 5},
]

EVENT_TYPES = [
    {'event_type_id': 1, 'event_type': 'Shot', 'event_category': 'offensive', 'description': 'Shot attempt on goal', 'is_corsi': True, 'is_fenwick': True},
    {'event_type_id': 2, 'event_type': 'Save', 'event_category': 'goaltending', 'description': 'Goalie save', 'is_corsi': False, 'is_fenwick': False},
    {'event_type_id': 3, 'event_type': 'Pass', 'event_category': 'playmaking', 'description': 'Pass attempt', 'is_corsi': False, 'is_fenwick': False},
    {'event_type_id': 4, 'event_type': 'Faceoff', 'event_category': 'faceoff', 'description': 'Faceoff', 'is_corsi': False, 'is_fenwick': False},
    {'event_type_id': 5, 'event_type': 'Turnover', 'event_category': 'turnover', 'description': 'Puck turnover', 'is_corsi': False, 'is_fenwick': False},
    {'event_type_id': 6, 'event_type': 'Zone_Entry_Exit', 'event_category': 'transition', 'description': 'Zone entry or exit', 'is_corsi': False, 'is_fenwick': False},
    {'event_type_id': 7, 'event_type': 'Possession', 'event_category': 'possession', 'description': 'Puck possession', 'is_corsi': False, 'is_fenwick': False},
    {'event_type_id': 8, 'event_type': 'Penalty', 'event_category': 'penalty', 'description': 'Penalty taken/drawn', 'is_corsi': False, 'is_fenwick': False},
    {'event_type_id': 9, 'event_type': 'Hit', 'event_category': 'physical', 'description': 'Body check', 'is_corsi': False, 'is_fenwick': False},
    {'event_type_id': 10, 'event_type': 'Block', 'event_category': 'defensive', 'description': 'Shot block', 'is_corsi': True, 'is_fenwick': False},
    {'event_type_id': 11, 'event_type': 'Stoppage', 'event_category': 'stoppage', 'description': 'Play stoppage', 'is_corsi': False, 'is_fenwick': False},
    {'event_type_id': 12, 'event_type': 'Goal', 'event_category': 'scoring', 'description': 'Goal scored', 'is_corsi': True, 'is_fenwick': True},
]

EVENT_DETAILS = [
    # Shots
    {'event_detail_id': 1, 'event_detail': 'Shot_OnNetSaved', 'event_type': 'Shot', 'category': 'shot_on_goal', 'is_shot_on_goal': True, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': 'medium'},
    {'event_detail_id': 2, 'event_detail': 'Shot_Goal', 'event_type': 'Shot', 'category': 'goal', 'is_shot_on_goal': True, 'is_goal': True, 'is_miss': False, 'is_block': False, 'danger_potential': 'high'},
    {'event_detail_id': 3, 'event_detail': 'Goal_Scored', 'event_type': 'Shot', 'category': 'goal', 'is_shot_on_goal': True, 'is_goal': True, 'is_miss': False, 'is_block': False, 'danger_potential': 'high'},
    {'event_detail_id': 4, 'event_detail': 'Shot_Missed', 'event_type': 'Shot', 'category': 'missed_shot', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': True, 'is_block': False, 'danger_potential': 'low'},
    {'event_detail_id': 5, 'event_detail': 'Shot_MissedWide', 'event_type': 'Shot', 'category': 'missed_shot', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': True, 'is_block': False, 'danger_potential': 'low'},
    {'event_detail_id': 6, 'event_detail': 'Shot_MissedHigh', 'event_type': 'Shot', 'category': 'missed_shot', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': True, 'is_block': False, 'danger_potential': 'low'},
    {'event_detail_id': 7, 'event_detail': 'Shot_HitPost', 'event_type': 'Shot', 'category': 'missed_shot', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': True, 'is_block': False, 'danger_potential': 'high'},
    {'event_detail_id': 8, 'event_detail': 'Shot_Blocked', 'event_type': 'Shot', 'category': 'blocked_shot', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': True, 'danger_potential': 'medium'},
    {'event_detail_id': 9, 'event_detail': 'Shot_TippedOnNetSaved', 'event_type': 'Shot', 'category': 'shot_on_goal', 'is_shot_on_goal': True, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': 'high'},
    {'event_detail_id': 10, 'event_detail': 'Shot_DeflectedOnNetSaved', 'event_type': 'Shot', 'category': 'shot_on_goal', 'is_shot_on_goal': True, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': 'high'},
    # Passes
    {'event_detail_id': 20, 'event_detail': 'Pass_Completed', 'event_type': 'Pass', 'category': 'completed_pass', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 21, 'event_detail': 'Pass_Missed', 'event_type': 'Pass', 'category': 'failed_pass', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 22, 'event_detail': 'Pass_Intercepted', 'event_type': 'Pass', 'category': 'failed_pass', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    # Turnovers
    {'event_detail_id': 30, 'event_detail': 'Turnover_Giveaway', 'event_type': 'Turnover', 'category': 'giveaway', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 31, 'event_detail': 'Turnover_Takeaway', 'event_type': 'Turnover', 'category': 'takeaway', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 32, 'event_detail': 'Turnover_BadPass', 'event_type': 'Turnover', 'category': 'giveaway', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 33, 'event_detail': 'Turnover_LostPuck', 'event_type': 'Turnover', 'category': 'giveaway', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    # Zone entries/exits
    {'event_detail_id': 40, 'event_detail': 'Zone_Entry_Carry', 'event_type': 'Zone_Entry_Exit', 'category': 'controlled_entry', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 41, 'event_detail': 'Zone_Entry_Pass', 'event_type': 'Zone_Entry_Exit', 'category': 'controlled_entry', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 42, 'event_detail': 'Zone_Entry_Dump', 'event_type': 'Zone_Entry_Exit', 'category': 'uncontrolled_entry', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 43, 'event_detail': 'Zone_Entry_Failed', 'event_type': 'Zone_Entry_Exit', 'category': 'failed_entry', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 44, 'event_detail': 'Zone_Exit_Carry', 'event_type': 'Zone_Entry_Exit', 'category': 'controlled_exit', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 45, 'event_detail': 'Zone_Exit_Pass', 'event_type': 'Zone_Entry_Exit', 'category': 'controlled_exit', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 46, 'event_detail': 'Zone_Exit_Clear', 'event_type': 'Zone_Entry_Exit', 'category': 'uncontrolled_exit', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    # Saves
    {'event_detail_id': 50, 'event_detail': 'Save_Blocker', 'event_type': 'Save', 'category': 'save', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 51, 'event_detail': 'Save_Glove', 'event_type': 'Save', 'category': 'save', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 52, 'event_detail': 'Save_Pad', 'event_type': 'Save', 'category': 'save', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 53, 'event_detail': 'Save_Stick', 'event_type': 'Save', 'category': 'save', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 54, 'event_detail': 'Save_Body', 'event_type': 'Save', 'category': 'save', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 55, 'event_detail': 'Save_Rebound', 'event_type': 'Save', 'category': 'save', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
    {'event_detail_id': 56, 'event_detail': 'Save_Freeze', 'event_type': 'Save', 'category': 'save', 'is_shot_on_goal': False, 'is_goal': False, 'is_miss': False, 'is_block': False, 'danger_potential': None},
]

PLAY_DETAILS = [
    # Assists
    {'play_detail_id': 1, 'play_detail': 'AssistPrimary', 'play_category': 'scoring', 'play_type': 'offensive', 'description': 'Primary assist on goal', 'points_value': 1},
    {'play_detail_id': 2, 'play_detail': 'AssistSecondary', 'play_category': 'scoring', 'play_type': 'offensive', 'description': 'Secondary assist on goal', 'points_value': 1},
    # Defensive plays
    {'play_detail_id': 10, 'play_detail': 'StickCheck', 'play_category': 'defense', 'play_type': 'defensive', 'description': 'Stick check to disrupt opponent', 'points_value': 0},
    {'play_detail_id': 11, 'play_detail': 'PokeCheck', 'play_category': 'defense', 'play_type': 'defensive', 'description': 'Poke check to steal puck', 'points_value': 0},
    {'play_detail_id': 12, 'play_detail': 'BlockedShot', 'play_category': 'defense', 'play_type': 'defensive', 'description': 'Blocked an opponent shot', 'points_value': 0},
    {'play_detail_id': 13, 'play_detail': 'InShotPassLane', 'play_category': 'defense', 'play_type': 'defensive', 'description': 'Positioned in shot/pass lane', 'points_value': 0},
    {'play_detail_id': 14, 'play_detail': 'SeparateFromPuck', 'play_category': 'defense', 'play_type': 'defensive', 'description': 'Separated opponent from puck', 'points_value': 0},
    {'play_detail_id': 15, 'play_detail': 'Backcheck', 'play_category': 'defense', 'play_type': 'defensive', 'description': 'Backcheck effort', 'points_value': 0},
    {'play_detail_id': 16, 'play_detail': 'ZoneEntryDenial', 'play_category': 'defense', 'play_type': 'defensive', 'description': 'Denied zone entry', 'points_value': 0},
    {'play_detail_id': 17, 'play_detail': 'ZoneExitDenial', 'play_category': 'defense', 'play_type': 'defensive', 'description': 'Denied zone exit', 'points_value': 0},
    {'play_detail_id': 18, 'play_detail': 'TakeAway', 'play_category': 'defense', 'play_type': 'defensive', 'description': 'Took puck from opponent', 'points_value': 0},
    # Offensive plays
    {'play_detail_id': 20, 'play_detail': 'Deke', 'play_category': 'offense', 'play_type': 'offensive', 'description': 'Deke attempt', 'points_value': 0},
    {'play_detail_id': 21, 'play_detail': 'BeatDeke', 'play_category': 'offense', 'play_type': 'offensive', 'description': 'Successfully beat defender with deke', 'points_value': 0},
    {'play_detail_id': 22, 'play_detail': 'Screen', 'play_category': 'offense', 'play_type': 'offensive', 'description': 'Screen on goalie', 'points_value': 0},
    {'play_detail_id': 23, 'play_detail': 'DumpAndChase', 'play_category': 'offense', 'play_type': 'offensive', 'description': 'Dump and chase play', 'points_value': 0},
    {'play_detail_id': 24, 'play_detail': 'Tip', 'play_category': 'offense', 'play_type': 'offensive', 'description': 'Tip/deflection attempt', 'points_value': 0},
    {'play_detail_id': 25, 'play_detail': 'OneTimer', 'play_category': 'offense', 'play_type': 'offensive', 'description': 'One-timer shot', 'points_value': 0},
    # Drives
    {'play_detail_id': 30, 'play_detail': 'DriveMiddle', 'play_category': 'drive', 'play_type': 'offensive', 'description': 'Drive to middle', 'points_value': 0},
    {'play_detail_id': 31, 'play_detail': 'DriveWide', 'play_category': 'drive', 'play_type': 'offensive', 'description': 'Drive wide', 'points_value': 0},
    {'play_detail_id': 32, 'play_detail': 'DriveCorner', 'play_category': 'drive', 'play_type': 'offensive', 'description': 'Drive to corner', 'points_value': 0},
    {'play_detail_id': 33, 'play_detail': 'DriveNetMiddle', 'play_category': 'drive', 'play_type': 'offensive', 'description': 'Drive to net front', 'points_value': 0},
    {'play_detail_id': 34, 'play_detail': 'BeatMiddle', 'play_category': 'drive', 'play_type': 'offensive', 'description': 'Beat defender to middle', 'points_value': 0},
    {'play_detail_id': 35, 'play_detail': 'BeatWide', 'play_category': 'drive', 'play_type': 'offensive', 'description': 'Beat defender wide', 'points_value': 0},
    # Breakouts
    {'play_detail_id': 40, 'play_detail': 'Breakout', 'play_category': 'transition', 'play_type': 'transition', 'description': 'Breakout play', 'points_value': 0},
    {'play_detail_id': 41, 'play_detail': 'AttemptedBreakOutPass', 'play_category': 'transition', 'play_type': 'transition', 'description': 'Attempted breakout pass', 'points_value': 0},
    {'play_detail_id': 42, 'play_detail': 'AttemptedBreakOutRush', 'play_category': 'transition', 'play_type': 'transition', 'description': 'Attempted breakout rush', 'points_value': 0},
    # Recoveries
    {'play_detail_id': 50, 'play_detail': 'PuckRecovery', 'play_category': 'recovery', 'play_type': 'neutral', 'description': 'Recovered loose puck', 'points_value': 0},
    {'play_detail_id': 51, 'play_detail': 'BoardBattleWin', 'play_category': 'recovery', 'play_type': 'neutral', 'description': 'Won board battle', 'points_value': 0},
    {'play_detail_id': 52, 'play_detail': 'BoardBattleLoss', 'play_category': 'recovery', 'play_type': 'neutral', 'description': 'Lost board battle', 'points_value': 0},
    # Additional offensive plays
    {'play_detail_id': 60, 'play_detail': 'CrashNet', 'play_category': 'offense', 'play_type': 'offensive', 'description': 'Crash the net', 'points_value': 0},
    {'play_detail_id': 61, 'play_detail': 'Cycle', 'play_category': 'offense', 'play_type': 'offensive', 'description': 'Cycle play in offensive zone', 'points_value': 0},
    {'play_detail_id': 62, 'play_detail': 'Forecheck', 'play_category': 'offense', 'play_type': 'offensive', 'description': 'Forecheck pressure', 'points_value': 0},
    {'play_detail_id': 63, 'play_detail': 'QuickUp', 'play_category': 'offense', 'play_type': 'offensive', 'description': 'Quick up pass', 'points_value': 0},
    {'play_detail_id': 64, 'play_detail': 'Reverse', 'play_category': 'offense', 'play_type': 'offensive', 'description': 'Reverse play direction', 'points_value': 0},
    # Additional defensive plays
    {'play_detail_id': 70, 'play_detail': 'Pressure', 'play_category': 'defense', 'play_type': 'defensive', 'description': 'Defensive pressure on puck carrier', 'points_value': 0},
    {'play_detail_id': 71, 'play_detail': 'Contain', 'play_category': 'defense', 'play_type': 'defensive', 'description': 'Contain opponent positioning', 'points_value': 0},
    {'play_detail_id': 72, 'play_detail': 'Surf', 'play_category': 'defense', 'play_type': 'defensive', 'description': 'Surf/shadow defensive positioning', 'points_value': 0},
]

SHOT_TYPES = [
    {'shot_type_id': 1, 'shot_type': 'Wrist', 'shot_type_full': 'Wrist Shot', 'description': 'Quick release from wrist', 'avg_velocity': 'medium', 'avg_accuracy': 'high'},
    {'shot_type_id': 2, 'shot_type': 'Slap', 'shot_type_full': 'Slap Shot', 'description': 'Wind-up power shot', 'avg_velocity': 'high', 'avg_accuracy': 'low'},
    {'shot_type_id': 3, 'shot_type': 'Snap', 'shot_type_full': 'Snap Shot', 'description': 'Quick snap release', 'avg_velocity': 'medium-high', 'avg_accuracy': 'medium'},
    {'shot_type_id': 4, 'shot_type': 'Backhand', 'shot_type_full': 'Backhand Shot', 'description': 'Shot from backhand', 'avg_velocity': 'low', 'avg_accuracy': 'medium'},
    {'shot_type_id': 5, 'shot_type': 'Tip', 'shot_type_full': 'Tip/Deflection', 'description': 'Redirected shot', 'avg_velocity': 'varies', 'avg_accuracy': 'low'},
    {'shot_type_id': 6, 'shot_type': 'Wrap', 'shot_type_full': 'Wraparound', 'description': 'Wraparound attempt', 'avg_velocity': 'low', 'avg_accuracy': 'low'},
]

PASS_TYPES = [
    {'pass_type_id': 1, 'pass_type': 'Forehand', 'description': 'Standard forehand pass'},
    {'pass_type_id': 2, 'pass_type': 'Backhand', 'description': 'Backhand pass'},
    {'pass_type_id': 3, 'pass_type': 'Saucer', 'description': 'Saucer pass (airborne)'},
    {'pass_type_id': 4, 'pass_type': 'Bank', 'description': 'Bank pass off boards'},
    {'pass_type_id': 5, 'pass_type': 'Drop', 'description': 'Drop pass'},
    {'pass_type_id': 6, 'pass_type': 'OneTouch', 'description': 'One-touch pass'},
    {'pass_type_id': 7, 'pass_type': 'CrossIce', 'description': 'Cross-ice pass'},
    {'pass_type_id': 8, 'pass_type': 'Stretch', 'description': 'Long stretch pass'},
]

ZONES = [
    {'zone_id': 'OZ', 'zone_name': 'Offensive Zone', 'zone_type': 'attacking', 'description': 'Attacking zone (opponent goal)', 'sort_order': 1},
    {'zone_id': 'NZ', 'zone_name': 'Neutral Zone', 'zone_type': 'neutral', 'description': 'Center ice between blue lines', 'sort_order': 2},
    {'zone_id': 'DZ', 'zone_name': 'Defensive Zone', 'zone_type': 'defending', 'description': 'Defending zone (own goal)', 'sort_order': 3},
]

STRENGTHS = [
    {'strength_id': '5v5', 'strength_name': '5 on 5', 'home_skaters': 5, 'away_skaters': 5, 'situation_type': 'even', 'is_special_teams': False, 'sort_order': 1},
    {'strength_id': '5v4', 'strength_name': '5 on 4', 'home_skaters': 5, 'away_skaters': 4, 'situation_type': 'home_pp', 'is_special_teams': True, 'sort_order': 2},
    {'strength_id': '4v5', 'strength_name': '4 on 5', 'home_skaters': 4, 'away_skaters': 5, 'situation_type': 'away_pp', 'is_special_teams': True, 'sort_order': 3},
    {'strength_id': '5v3', 'strength_name': '5 on 3', 'home_skaters': 5, 'away_skaters': 3, 'situation_type': 'home_pp', 'is_special_teams': True, 'sort_order': 4},
    {'strength_id': '3v5', 'strength_name': '3 on 5', 'home_skaters': 3, 'away_skaters': 5, 'situation_type': 'away_pp', 'is_special_teams': True, 'sort_order': 5},
    {'strength_id': '4v4', 'strength_name': '4 on 4', 'home_skaters': 4, 'away_skaters': 4, 'situation_type': 'even', 'is_special_teams': False, 'sort_order': 6},
    {'strength_id': '3v3', 'strength_name': '3 on 3', 'home_skaters': 3, 'away_skaters': 3, 'situation_type': 'even', 'is_special_teams': False, 'sort_order': 7},
    {'strength_id': '4v3', 'strength_name': '4 on 3', 'home_skaters': 4, 'away_skaters': 3, 'situation_type': 'home_pp', 'is_special_teams': True, 'sort_order': 8},
    {'strength_id': '3v4', 'strength_name': '3 on 4', 'home_skaters': 3, 'away_skaters': 4, 'situation_type': 'away_pp', 'is_special_teams': True, 'sort_order': 9},
    {'strength_id': '6v5', 'strength_name': '6 on 5 (EN)', 'home_skaters': 6, 'away_skaters': 5, 'situation_type': 'home_en', 'is_special_teams': True, 'sort_order': 10},
    {'strength_id': '5v6', 'strength_name': '5 on 6 (EN)', 'home_skaters': 5, 'away_skaters': 6, 'situation_type': 'away_en', 'is_special_teams': True, 'sort_order': 11},
]

SITUATIONS = [
    {'situation_id': 'even', 'situation_name': 'Even Strength', 'description': 'Equal number of skaters', 'is_power_play': False, 'is_penalty_kill': False, 'is_empty_net': False},
    {'situation_id': 'pp', 'situation_name': 'Power Play', 'description': 'Man advantage', 'is_power_play': True, 'is_penalty_kill': False, 'is_empty_net': False},
    {'situation_id': 'pk', 'situation_name': 'Penalty Kill', 'description': 'Short-handed', 'is_power_play': False, 'is_penalty_kill': True, 'is_empty_net': False},
    {'situation_id': 'en', 'situation_name': 'Empty Net', 'description': 'Goalie pulled', 'is_power_play': False, 'is_penalty_kill': False, 'is_empty_net': True},
    {'situation_id': 'pp_en', 'situation_name': 'Power Play + Empty Net', 'description': 'PP with goalie pulled', 'is_power_play': True, 'is_penalty_kill': False, 'is_empty_net': True},
]

POSITIONS = [
    {'position_id': 'F', 'position_name': 'Forward', 'position_full': 'Forward', 'position_category': 'skater', 'typical_count': 3, 'sort_order': 1},
    {'position_id': 'C', 'position_name': 'Center', 'position_full': 'Center', 'position_category': 'skater', 'typical_count': 1, 'sort_order': 2},
    {'position_id': 'LW', 'position_name': 'Left Wing', 'position_full': 'Left Wing', 'position_category': 'skater', 'typical_count': 1, 'sort_order': 3},
    {'position_id': 'RW', 'position_name': 'Right Wing', 'position_full': 'Right Wing', 'position_category': 'skater', 'typical_count': 1, 'sort_order': 4},
    {'position_id': 'D', 'position_name': 'Defense', 'position_full': 'Defenseman', 'position_category': 'skater', 'typical_count': 2, 'sort_order': 5},
    {'position_id': 'LD', 'position_name': 'Left Defense', 'position_full': 'Left Defenseman', 'position_category': 'skater', 'typical_count': 1, 'sort_order': 6},
    {'position_id': 'RD', 'position_name': 'Right Defense', 'position_full': 'Right Defenseman', 'position_category': 'skater', 'typical_count': 1, 'sort_order': 7},
    {'position_id': 'G', 'position_name': 'Goalie', 'position_full': 'Goaltender', 'position_category': 'goalie', 'typical_count': 1, 'sort_order': 8},
]

PLAYER_ROLES = [
    {'role_id': 1, 'role_code': 'event_team_player_1', 'role_name': 'Primary Event Player', 'role_type': 'event_team', 'description': 'Main player executing the event'},
    {'role_id': 2, 'role_code': 'event_team_player_2', 'role_name': 'Secondary Event Player', 'role_type': 'event_team', 'description': 'Supporting player (e.g., pass receiver)'},
    {'role_id': 3, 'role_code': 'event_team_player_3', 'role_name': 'Tertiary Event Player', 'role_type': 'event_team', 'description': 'Third player involved'},
    {'role_id': 4, 'role_code': 'opp_team_player_1', 'role_name': 'Primary Opponent', 'role_type': 'opp_team', 'description': 'Main opposing player'},
    {'role_id': 5, 'role_code': 'opp_team_player_2', 'role_name': 'Secondary Opponent', 'role_type': 'opp_team', 'description': 'Supporting opposing player'},
    {'role_id': 6, 'role_code': 'opp_team_goalie', 'role_name': 'Opposing Goalie', 'role_type': 'opp_team', 'description': 'Opposing goaltender'},
    {'role_id': 7, 'role_code': 'event_team_goalie', 'role_name': 'Event Team Goalie', 'role_type': 'event_team', 'description': 'Event team goaltender'},
]

SHIFT_TYPES = [
    {'shift_type_id': 1, 'shift_type': 'faceoff', 'shift_type_name': 'Faceoff Start', 'description': 'Shift started with faceoff'},
    {'shift_type_id': 2, 'shift_type': 'on_the_fly', 'shift_type_name': 'On The Fly', 'description': 'Line change during play'},
    {'shift_type_id': 3, 'shift_type': 'stoppage', 'shift_type_name': 'Stoppage', 'description': 'Shift ended at whistle'},
    {'shift_type_id': 4, 'shift_type': 'period_end', 'shift_type_name': 'Period End', 'description': 'Period ended'},
    {'shift_type_id': 5, 'shift_type': 'goal', 'shift_type_name': 'Goal', 'description': 'Shift ended with goal'},
    {'shift_type_id': 6, 'shift_type': 'penalty', 'shift_type_name': 'Penalty', 'description': 'Penalty called'},
]

VENUES = [
    {'venue_id': 'home', 'venue_name': 'Home', 'description': 'Home team'},
    {'venue_id': 'away', 'venue_name': 'Away', 'description': 'Away/Visiting team'},
]

TIME_BUCKETS = [
    {'time_bucket_id': 1, 'bucket_name': '0-5 min', 'period_start_min': 0, 'period_end_min': 5, 'description': 'First 5 minutes of period'},
    {'time_bucket_id': 2, 'bucket_name': '5-10 min', 'period_start_min': 5, 'period_end_min': 10, 'description': 'Minutes 5-10 of period'},
    {'time_bucket_id': 3, 'bucket_name': '10-15 min', 'period_start_min': 10, 'period_end_min': 15, 'description': 'Minutes 10-15 of period'},
    {'time_bucket_id': 4, 'bucket_name': '15-20 min', 'period_start_min': 15, 'period_end_min': 20, 'description': 'Last 5 minutes of period'},
]

DANGER_ZONES = [
    {'danger_zone_id': 'HD', 'danger_zone_name': 'High Danger', 'xg_base': 0.15, 'description': 'Slot area, high scoring probability', 'distance_max_ft': 20},
    {'danger_zone_id': 'MD', 'danger_zone_name': 'Medium Danger', 'xg_base': 0.07, 'description': 'Circles and mid-slot', 'distance_max_ft': 35},
    {'danger_zone_id': 'LD', 'danger_zone_name': 'Low Danger', 'xg_base': 0.025, 'description': 'Perimeter shots', 'distance_max_ft': 999},
]


# =============================================================================
# DIMENSION BUILDER CLASS
# =============================================================================

class DimensionBuilder:
    """
    Build all dimension tables for the hockey analytics data mart.
    
    This class creates both static dimensions (predefined values) and
    dynamic dimensions (extracted from actual game data).
    
    Attributes:
        dimensions: Dictionary of built dimension DataFrames
    """
    
    def __init__(self):
        """Initialize the dimension builder."""
        self.dimensions = {}
    
    def build_all_static(self) -> Dict[str, pd.DataFrame]:
        """
        Build all static (predefined) dimension tables.
        
        Returns:
            Dictionary mapping dimension name to DataFrame
        """
        self.dimensions['dim_period'] = pd.DataFrame(PERIODS)
        self.dimensions['dim_event_type'] = pd.DataFrame(EVENT_TYPES)
        self.dimensions['dim_event_detail'] = pd.DataFrame(EVENT_DETAILS)
        self.dimensions['dim_play_detail'] = pd.DataFrame(PLAY_DETAILS)
        self.dimensions['dim_shot_type'] = pd.DataFrame(SHOT_TYPES)
        self.dimensions['dim_pass_type'] = pd.DataFrame(PASS_TYPES)
        self.dimensions['dim_zone'] = pd.DataFrame(ZONES)
        self.dimensions['dim_strength'] = pd.DataFrame(STRENGTHS)
        self.dimensions['dim_situation'] = pd.DataFrame(SITUATIONS)
        self.dimensions['dim_position'] = pd.DataFrame(POSITIONS)
        self.dimensions['dim_player_role'] = pd.DataFrame(PLAYER_ROLES)
        self.dimensions['dim_shift_type'] = pd.DataFrame(SHIFT_TYPES)
        self.dimensions['dim_venue'] = pd.DataFrame(VENUES)
        self.dimensions['dim_time_bucket'] = pd.DataFrame(TIME_BUCKETS)
        self.dimensions['dim_danger_zone'] = pd.DataFrame(DANGER_ZONES)
        
        return self.dimensions
    
    def build_from_data(self, events_df: pd.DataFrame = None, 
                        shifts_df: pd.DataFrame = None) -> Dict[str, pd.DataFrame]:
        """
        Build dimension tables from actual game data.
        
        This extracts unique values from game data and merges with
        static dimensions to ensure completeness.
        
        Args:
            events_df: Events DataFrame
            shifts_df: Shifts DataFrame
        
        Returns:
            Dictionary of dimension DataFrames
        """
        # Start with static dimensions
        self.build_all_static()
        
        # Enrich from data if provided
        if events_df is not None:
            self._enrich_from_events(events_df)
        
        if shifts_df is not None:
            self._enrich_from_shifts(shifts_df)
        
        return self.dimensions
    
    def _enrich_from_events(self, events_df: pd.DataFrame):
        """Add any event types/details found in data but not in static list."""
        # Check for new event types
        if 'Type' in events_df.columns:
            existing_types = set(self.dimensions['dim_event_type']['event_type'].str.lower())
            data_types = set(events_df['Type'].dropna().unique())
            
            new_types = []
            max_id = self.dimensions['dim_event_type']['event_type_id'].max()
            
            for t in data_types:
                if t.lower() not in existing_types:
                    max_id += 1
                    new_types.append({
                        'event_type_id': max_id,
                        'event_type': t,
                        'event_category': 'other',
                        'description': f'Event type from data: {t}',
                        'is_corsi': False,
                        'is_fenwick': False
                    })
            
            if new_types:
                self.dimensions['dim_event_type'] = pd.concat([
                    self.dimensions['dim_event_type'],
                    pd.DataFrame(new_types)
                ], ignore_index=True)
        
        # Check for new event details
        if 'event_detail' in events_df.columns:
            existing_details = set(self.dimensions['dim_event_detail']['event_detail'].str.lower())
            data_details = set(events_df['event_detail'].dropna().unique())
            
            new_details = []
            max_id = self.dimensions['dim_event_detail']['event_detail_id'].max()
            
            for d in data_details:
                if d.lower() not in existing_details:
                    max_id += 1
                    new_details.append({
                        'event_detail_id': max_id,
                        'event_detail': d,
                        'event_type': 'Unknown',
                        'category': 'other',
                        'is_shot_on_goal': False,
                        'is_goal': 'Goal' in d,
                        'is_miss': 'Miss' in d,
                        'is_block': 'Block' in d,
                        'danger_potential': None
                    })
            
            if new_details:
                self.dimensions['dim_event_detail'] = pd.concat([
                    self.dimensions['dim_event_detail'],
                    pd.DataFrame(new_details)
                ], ignore_index=True)
        
        # Check for new play details
        if 'play_detail1' in events_df.columns:
            existing_plays = set(self.dimensions['dim_play_detail']['play_detail'].str.lower())
            data_plays = set(events_df['play_detail1'].dropna().unique())
            
            new_plays = []
            max_id = self.dimensions['dim_play_detail']['play_detail_id'].max()
            
            for p in data_plays:
                if p.lower() not in existing_plays:
                    max_id += 1
                    new_plays.append({
                        'play_detail_id': max_id,
                        'play_detail': p,
                        'play_category': 'other',
                        'play_type': 'unknown',
                        'description': f'Play detail from data: {p}',
                        'points_value': 0
                    })
            
            if new_plays:
                self.dimensions['dim_play_detail'] = pd.concat([
                    self.dimensions['dim_play_detail'],
                    pd.DataFrame(new_plays)
                ], ignore_index=True)
    
    def _enrich_from_shifts(self, shifts_df: pd.DataFrame):
        """Add any strength/situation values found in data."""
        if 'strength' in shifts_df.columns:
            existing = set(self.dimensions['dim_strength']['strength_id'].str.lower())
            data_strengths = set(shifts_df['strength'].dropna().unique())
            
            new_strengths = []
            max_order = self.dimensions['dim_strength']['sort_order'].max()
            
            for s in data_strengths:
                if str(s).lower() not in existing:
                    max_order += 1
                    new_strengths.append({
                        'strength_id': str(s),
                        'strength_name': str(s),
                        'home_skaters': None,
                        'away_skaters': None,
                        'situation_type': 'unknown',
                        'is_special_teams': False,
                        'sort_order': max_order
                    })
            
            if new_strengths:
                self.dimensions['dim_strength'] = pd.concat([
                    self.dimensions['dim_strength'],
                    pd.DataFrame(new_strengths)
                ], ignore_index=True)
    
    def get_dimension(self, name: str) -> pd.DataFrame:
        """Get a specific dimension table."""
        return self.dimensions.get(name, pd.DataFrame())


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_all_dimensions(events_df: pd.DataFrame = None,
                         shifts_df: pd.DataFrame = None) -> Dict[str, pd.DataFrame]:
    """
    Convenience function to create all dimension tables.
    
    Args:
        events_df: Optional events data to enrich dimensions
        shifts_df: Optional shifts data to enrich dimensions
    
    Returns:
        Dictionary of all dimension DataFrames
    """
    builder = DimensionBuilder()
    return builder.build_from_data(events_df, shifts_df)
