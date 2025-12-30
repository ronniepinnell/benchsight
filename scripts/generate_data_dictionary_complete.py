#!/usr/bin/env python3
"""
BenchSight Complete Data Dictionary Generator
==============================================

Creates comprehensive data dictionaries for ALL tables including:
- Column name, data type, description
- Source type: EXPLICIT (raw tracking) | CALCULATED (ETL) | LOOKUP (FK join) | DERIVED (from other calcs)
- Calculation formula (exact SQL/Python logic)
- Filter context (what filters/WHERE clauses apply)
- Tolerance thresholds for validation flagging
- depends_on: What source columns/tables feed this column
- used_by: What downstream calculations use this column

Output: data/output/data_dictionary/ folder with CSV files for Supabase mart

Author: BenchSight
Date: December 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

OUTPUT_DIR = Path('data/output')
DICT_DIR = OUTPUT_DIR / 'data_dictionary'
DICT_DIR.mkdir(exist_ok=True)


# =============================================================================
# FACT_EVENTS - The Source of Truth for All Event Data
# =============================================================================
def create_fact_events_dict():
    """Wide format events - one row per event with all players."""
    columns = [
        # Keys
        {'column': 'event_key', 'type': 'VARCHAR(20)', 'nullable': 'NO', 
         'description': 'Primary key for event',
         'source': 'CALCULATED', 'formula': "f'EV{game_id}{event_index:05d}'", 
         'filter_context': 'Per event',
         'tolerance': None, 'depends_on': 'game_id, event_index', 
         'used_by': 'fact_events_player.event_key, fact_linked_events.event_key'},
        
        {'column': 'game_id', 'type': 'INT', 'nullable': 'NO',
         'description': 'Game identifier from filename',
         'source': 'EXPLICIT', 'formula': 'Extracted from tracking filename (e.g., Game_18969_...xlsx → 18969)',
         'filter_context': None, 'tolerance': None, 
         'depends_on': 'tracking filename', 'used_by': 'All game-level aggregations'},
        
        {'column': 'event_index', 'type': 'INT', 'nullable': 'NO',
         'description': 'Sequential event number within game',
         'source': 'EXPLICIT', 'formula': 'From tracking: event_index column',
         'filter_context': None, 'tolerance': '1 to ~1500 per game',
         'depends_on': 'tracking data', 'used_by': 'event_key, event ordering'},
        
        {'column': 'shift_index', 'type': 'INT', 'nullable': 'YES',
         'description': 'Current shift number when event occurred',
         'source': 'EXPLICIT', 'formula': 'From tracking: shift_index column',
         'filter_context': None, 'tolerance': '1 to ~170 per game',
         'depends_on': 'tracking data', 'used_by': 'shift_key, linking events to shifts'},
        
        {'column': 'shift_key', 'type': 'VARCHAR(20)', 'nullable': 'YES',
         'description': 'Foreign key to fact_shifts',
         'source': 'CALCULATED', 'formula': "f'SH{game_id}{shift_index:05d}'",
         'filter_context': None, 'tolerance': None,
         'depends_on': 'game_id, shift_index', 'used_by': 'Shift-event joins'},
        
        # Time
        {'column': 'period', 'type': 'INT', 'nullable': 'NO',
         'description': 'Period number (1, 2, 3, OT)',
         'source': 'EXPLICIT', 'formula': 'From tracking: period_ column',
         'filter_context': None, 'tolerance': '1-4',
         'depends_on': 'tracking data', 'used_by': 'Period-level aggregations'},
        
        {'column': 'event_start_total_seconds', 'type': 'INT', 'nullable': 'YES',
         'description': 'Event start time in total game seconds',
         'source': 'CALCULATED', 'formula': '(period-1)*900 + event_start_min*60 + event_start_sec',
         'filter_context': None, 'tolerance': '0-2700+',
         'depends_on': 'period, event_start_min, event_start_sec', 'used_by': 'Event ordering, time-based filtering'},
        
        # Event Classification
        {'column': 'event_type', 'type': 'VARCHAR(30)', 'nullable': 'NO',
         'description': 'Primary event type classification',
         'source': 'EXPLICIT', 'formula': 'From tracking: event_type_ or Type column',
         'filter_context': None, 'tolerance': 'Must be in dim_event_type',
         'depends_on': 'tracking data', 
         'used_by': 'ALL stat calculations - Shot, Goal, Faceoff, Pass, Turnover, Zone_Entry_Exit, Save, etc.'},
        
        {'column': 'event_detail', 'type': 'VARCHAR(50)', 'nullable': 'YES',
         'description': 'Detailed event outcome/result',
         'source': 'EXPLICIT', 'formula': 'From tracking: event_detail_ column',
         'filter_context': None, 'tolerance': 'Must be in dim_event_detail',
         'depends_on': 'tracking data',
         'used_by': 'SOG (Shot_OnNetSaved, Shot_Goal), save type (Save_Freeze, Save_Rebound), turnover type'},
        
        {'column': 'event_detail_2', 'type': 'VARCHAR(50)', 'nullable': 'YES',
         'description': 'Secondary event detail (zone entry type, save location)',
         'source': 'EXPLICIT', 'formula': 'From tracking: event_detail_2_ column',
         'filter_context': None, 'tolerance': 'Must be in dim_event_detail_2',
         'depends_on': 'tracking data',
         'used_by': 'Zone entry type (ZoneEntry-Rush/Pass/Dump), goalie save location (Glove/Blocker/Pad)'},
        
        {'column': 'event_successful', 'type': 'VARCHAR(1)', 'nullable': 'YES',
         'description': 'Success indicator: s=success, u=unsuccessful',
         'source': 'EXPLICIT', 'formula': 'From tracking: event_successful_ column',
         'filter_context': None, 'tolerance': 's or u only',
         'depends_on': 'tracking data',
         'used_by': 'Pass completion (s=completed), shot results'},
        
        # Player columns (wide format - up to 12 players per event)
        {'column': 'event_team_player_1', 'type': 'INT', 'nullable': 'YES',
         'description': 'Primary actor jersey number (CRITICAL: gets stat credit)',
         'source': 'EXPLICIT', 'formula': 'From tracking: event_team_player_1 column',
         'filter_context': None, 'tolerance': '1-99',
         'depends_on': 'tracking data',
         'used_by': 'ALL primary stats - shots, goals, faceoff wins, passes, zone entries'},
        
        {'column': 'opp_team_player_1', 'type': 'INT', 'nullable': 'YES',
         'description': 'Primary opponent actor jersey number',
         'source': 'EXPLICIT', 'formula': 'From tracking: opp_team_player_1 column',
         'filter_context': None, 'tolerance': '1-99',
         'depends_on': 'tracking data',
         'used_by': 'Faceoff losses (this is the loser), opponent stats'},
        
        # Linked events
        {'column': 'linked_event_index', 'type': 'INT', 'nullable': 'YES',
         'description': 'Links to related event (e.g., assist linked to goal)',
         'source': 'EXPLICIT', 'formula': 'From tracking: linked_event_index column',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'tracking data',
         'used_by': 'Assist attribution, shot-save chains, fact_linked_events'},
        
        # Empty net flag
        {'column': 'empty_net_goal', 'type': 'BOOLEAN', 'nullable': 'YES',
         'description': 'Flag if goal scored on empty net',
         'source': 'CALCULATED', 'formula': 'True if event_type=Goal AND opposing goalie was pulled (shift.team_en=1 or goalie isna)',
         'filter_context': 'Goal events only',
         'tolerance': None,
         'depends_on': 'event_type, fact_shifts.home_team_en/away_team_en',
         'used_by': 'Goalie GA (exclude EN), team stats'},
    ]
    return pd.DataFrame(columns)


# =============================================================================
# FACT_EVENTS_PLAYER - Long Format (One Row Per Player Per Event)
# =============================================================================
def create_fact_events_player_dict():
    """Long format - one row per player involvement in an event."""
    columns = [
        {'column': 'event_player_key', 'type': 'VARCHAR(20)', 'nullable': 'NO',
         'description': 'Primary key for player-event combination',
         'source': 'CALCULATED', 'formula': "f'EP{game_id}{row_number:05d}' where row_number is sequential across all events",
         'filter_context': 'Per player per event',
         'tolerance': None, 'depends_on': 'game_id, row order', 'used_by': None},
        
        {'column': 'event_key', 'type': 'VARCHAR(20)', 'nullable': 'NO',
         'description': 'Foreign key to fact_events',
         'source': 'CALCULATED', 'formula': "f'EV{game_id}{event_index:05d}'",
         'filter_context': None, 'tolerance': None,
         'depends_on': 'game_id, event_index', 'used_by': 'fact_events join'},
        
        {'column': 'game_id', 'type': 'INT', 'nullable': 'NO',
         'description': 'Game identifier',
         'source': 'EXPLICIT', 'formula': 'From parent event',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'fact_events.game_id', 'used_by': 'All game aggregations'},
        
        {'column': 'event_index', 'type': 'INT', 'nullable': 'NO',
         'description': 'Event sequence number',
         'source': 'EXPLICIT', 'formula': 'From parent event',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'fact_events.event_index', 'used_by': 'event_key'},
        
        {'column': 'player_id', 'type': 'VARCHAR(10)', 'nullable': 'YES',
         'description': 'Player identifier (P100xxx format)',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.player_id WHERE game_id matches AND player_game_number = jersey_number',
         'filter_context': None, 'tolerance': 'Must exist in fact_gameroster',
         'depends_on': 'player_game_number, fact_gameroster', 'used_by': 'All player stats'},
        
        {'column': 'player_game_number', 'type': 'INT', 'nullable': 'YES',
         'description': 'Player jersey number from tracking',
         'source': 'EXPLICIT', 'formula': 'From tracking: event_team_player_N or opp_team_player_N column value',
         'filter_context': None, 'tolerance': '1-99',
         'depends_on': 'tracking data', 'used_by': 'player_id lookup'},
        
        {'column': 'player_name', 'type': 'VARCHAR(100)', 'nullable': 'YES',
         'description': 'Player full name',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.player_full_name WHERE player_id matches',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'player_id, fact_gameroster', 'used_by': 'Display only'},
        
        {'column': 'player_team', 'type': 'VARCHAR(50)', 'nullable': 'YES',
         'description': 'Team name player belongs to',
         'source': 'DERIVED', 'formula': 'team_ prefix (home/away) converted to team name via roster lookup',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'tracking team_ column, fact_gameroster', 'used_by': 'Team-level aggregations'},
        
        {'column': 'player_role', 'type': 'VARCHAR(30)', 'nullable': 'NO',
         'description': '*** CRITICAL *** Player role determines stat attribution',
         'source': 'EXPLICIT', 'formula': 'From tracking: role_abrev_ column (event_team_player_1, event_team_player_2, opp_team_player_1, etc.)',
         'filter_context': None, 'tolerance': 'Must be in dim_player_role',
         'depends_on': 'tracking data',
         'used_by': '''CRITICAL FOR ALL STATS:
- event_team_player_1 = PRIMARY ACTOR (gets shot/goal/faceoff win/pass credit)
- opp_team_player_1 = OPPONENT ACTOR (gets faceoff loss, defensive event)
- Other roles = on-ice but not primary actor'''},
        
        {'column': 'event_type', 'type': 'VARCHAR(30)', 'nullable': 'NO',
         'description': 'Type of event (from parent)',
         'source': 'EXPLICIT', 'formula': 'From fact_events.event_type',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'fact_events.event_type',
         'used_by': 'Stat type determination (Shot→shots, Goal→goals, etc.)'},
        
        {'column': 'event_detail', 'type': 'VARCHAR(50)', 'nullable': 'YES',
         'description': 'Detailed event outcome',
         'source': 'EXPLICIT', 'formula': 'From fact_events.event_detail',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'fact_events.event_detail',
         'used_by': 'SOG filter (Shot_OnNetSaved, Shot_Goal), turnover type (Giveaway_*, Takeaway_*)'},
        
        {'column': 'event_detail_2', 'type': 'VARCHAR(50)', 'nullable': 'YES',
         'description': 'Secondary event detail',
         'source': 'EXPLICIT', 'formula': 'From fact_events.event_detail_2',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'fact_events.event_detail_2',
         'used_by': 'Zone entry type classification, save location classification'},
        
        {'column': 'event_successful', 'type': 'VARCHAR(1)', 'nullable': 'YES',
         'description': 'Success indicator (s/u)',
         'source': 'EXPLICIT', 'formula': 'From fact_events.event_successful',
         'filter_context': None, 'tolerance': 's or u',
         'depends_on': 'fact_events.event_successful',
         'used_by': 'Pass completion (event_successful="s" AND event_type="Pass")'},
        
        {'column': 'play_detail1', 'type': 'VARCHAR(50)', 'nullable': 'YES',
         'description': '*** CRITICAL FOR ASSISTS ***',
         'source': 'EXPLICIT', 'formula': 'From tracking: play_detail1_ column',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'tracking data',
         'used_by': '''ASSIST DETECTION:
- "AssistPrimary" = Primary assist (1st assist on goal)
- "AssistSecondary" = Secondary assist (2nd assist on goal)
- linked_event_index connects to the Goal event'''},
        
        {'column': 'linked_event_index', 'type': 'INT', 'nullable': 'YES',
         'description': 'Links this event to another (assists→goal)',
         'source': 'EXPLICIT', 'formula': 'From tracking: linked_event_index column',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'tracking data',
         'used_by': 'Assist-goal linking, shot-save chains'},
        
        {'column': 'shift_index', 'type': 'INT', 'nullable': 'YES',
         'description': 'Current shift number',
         'source': 'EXPLICIT', 'formula': 'From fact_events.shift_index',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'fact_events.shift_index', 'used_by': 'On-ice player tracking'},
    ]
    return pd.DataFrame(columns)


# =============================================================================
# FACT_SHIFTS - One Row Per Shift
# =============================================================================
def create_fact_shifts_dict():
    """Shift-level data with on-ice players."""
    columns = [
        {'column': 'shift_key', 'type': 'VARCHAR(20)', 'nullable': 'NO',
         'description': 'Primary key for shift',
         'source': 'CALCULATED', 'formula': "f'SH{game_id}{shift_index:05d}'",
         'filter_context': 'Per shift',
         'tolerance': None, 'depends_on': 'game_id, shift_index', 
         'used_by': 'fact_shifts_player.shift_key, fact_events.shift_key'},
        
        {'column': 'game_id', 'type': 'INT', 'nullable': 'NO',
         'description': 'Game identifier',
         'source': 'EXPLICIT', 'formula': 'From tracking filename',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'tracking filename', 'used_by': 'All calculations'},
        
        {'column': 'shift_index', 'type': 'INT', 'nullable': 'NO',
         'description': 'Shift sequence number in game',
         'source': 'EXPLICIT', 'formula': 'From tracking: shift_index column',
         'filter_context': None, 'tolerance': '1-170 per game',
         'depends_on': 'tracking data', 'used_by': 'shift_key'},
        
        {'column': 'period', 'type': 'INT', 'nullable': 'NO',
         'description': 'Period number',
         'source': 'EXPLICIT', 'formula': 'From tracking: period column',
         'filter_context': None, 'tolerance': '1-4',
         'depends_on': 'tracking data', 'used_by': 'Period stats'},
        
        {'column': 'shift_start_total_seconds', 'type': 'INT', 'nullable': 'NO',
         'description': 'Shift start in total game seconds',
         'source': 'CALCULATED', 'formula': '(period-1)*900 + shift_start_min*60 + shift_start_sec',
         'filter_context': None, 'tolerance': '0-2700+',
         'depends_on': 'period, shift_start_min, shift_start_sec', 
         'used_by': 'TOI calculation, shift duration'},
        
        {'column': 'shift_end_total_seconds', 'type': 'INT', 'nullable': 'NO',
         'description': 'Shift end in total game seconds',
         'source': 'CALCULATED', 'formula': '(period-1)*900 + shift_end_min*60 + shift_end_sec',
         'filter_context': None, 'tolerance': '0-2700+',
         'depends_on': 'period, shift_end_min, shift_end_sec', 
         'used_by': 'TOI calculation, shift duration'},
        
        {'column': 'shift_duration_seconds', 'type': 'INT', 'nullable': 'NO',
         'description': 'Shift length in seconds',
         'source': 'CALCULATED', 'formula': 'shift_end_total_seconds - shift_start_total_seconds',
         'filter_context': None, 'tolerance': '5-180 seconds typical',
         'depends_on': 'shift_start_total_seconds, shift_end_total_seconds', 
         'used_by': 'Player TOI, avg_shift'},
        
        {'column': 'home_team_en', 'type': 'BOOLEAN', 'nullable': 'YES',
         'description': 'Home team empty net flag (goalie pulled)',
         'source': 'EXPLICIT', 'formula': 'From tracking: home_team_en column (1=goalie pulled)',
         'filter_context': None, 'tolerance': '0 or 1',
         'depends_on': 'tracking data', 
         'used_by': 'Empty net goal detection for away team scoring'},
        
        {'column': 'away_team_en', 'type': 'BOOLEAN', 'nullable': 'YES',
         'description': 'Away team empty net flag (goalie pulled)',
         'source': 'EXPLICIT', 'formula': 'From tracking: away_team_en column (1=goalie pulled)',
         'filter_context': None, 'tolerance': '0 or 1',
         'depends_on': 'tracking data', 
         'used_by': 'Empty net goal detection for home team scoring'},
        
        # On-ice players (home_1 through home_6, away_1 through away_6)
        {'column': 'home_1 to home_6', 'type': 'INT', 'nullable': 'YES',
         'description': 'Home team players on ice (jersey numbers)',
         'source': 'EXPLICIT', 'formula': 'From tracking: home_1 through home_6 columns',
         'filter_context': None, 'tolerance': '1-99 or null',
         'depends_on': 'tracking data', 
         'used_by': 'fact_shifts_player, H2H, WOWY calculations'},
        
        {'column': 'away_1 to away_6', 'type': 'INT', 'nullable': 'YES',
         'description': 'Away team players on ice (jersey numbers)',
         'source': 'EXPLICIT', 'formula': 'From tracking: away_1 through away_6 columns',
         'filter_context': None, 'tolerance': '1-99 or null',
         'depends_on': 'tracking data', 
         'used_by': 'fact_shifts_player, H2H, WOWY calculations'},
    ]
    return pd.DataFrame(columns)


# =============================================================================
# FACT_PLAYER_GAME_STATS - Aggregated Player Stats Per Game
# =============================================================================
def create_fact_player_game_stats_dict():
    """Player-level aggregated statistics per game."""
    columns = [
        # Keys
        {'column': 'player_game_key', 'type': 'VARCHAR(20)', 'nullable': 'NO',
         'description': 'Primary key',
         'source': 'CALCULATED', 'formula': "f'PG{game_id}{player_sequence:05d}'",
         'filter_context': 'Per player per game',
         'tolerance': None, 'depends_on': 'game_id', 'used_by': None},
        
        {'column': 'game_id', 'type': 'INT', 'nullable': 'NO',
         'description': 'Game identifier',
         'source': 'EXPLICIT', 'formula': 'From source data',
         'filter_context': None, 'tolerance': None,
         'depends_on': None, 'used_by': 'All aggregations'},
        
        {'column': 'player_id', 'type': 'VARCHAR(10)', 'nullable': 'NO',
         'description': 'Player identifier',
         'source': 'LOOKUP', 'formula': 'From fact_gameroster',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'fact_gameroster', 'used_by': 'All player stats'},
        
        {'column': 'player_name', 'type': 'VARCHAR(100)', 'nullable': 'YES',
         'description': 'Player full name',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.player_full_name',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'player_id', 'used_by': 'Display'},
        
        {'column': 'team_name', 'type': 'VARCHAR(50)', 'nullable': 'YES',
         'description': 'Team name',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.team_name',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'player_id, game_id', 'used_by': 'Team aggregations'},
        
        # Goals/Assists
        {'column': 'goals', 'type': 'INT', 'nullable': 'NO',
         'description': 'Goals scored',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Goal" 
  - player_role = "event_team_player_1"
  - player_id matches''',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1, event_type=Goal',
         'tolerance': '0-5 per game, FLAG if >5',
         'depends_on': 'fact_events_player.event_type, player_role', 
         'used_by': 'points, shooting_pct, team goals'},
        
        {'column': 'assists', 'type': 'INT', 'nullable': 'NO',
         'description': 'Total assists (primary + secondary)',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - play_detail1 CONTAINS "Assist" (AssistPrimary OR AssistSecondary)
  - player_id matches''',
         'filter_context': 'player_id, game_id, play_detail1 LIKE "%Assist%"',
         'tolerance': '0-5 per game, FLAG if >5',
         'depends_on': 'fact_events_player.play_detail1', 
         'used_by': 'points'},
        
        {'column': 'points', 'type': 'INT', 'nullable': 'NO',
         'description': 'Total points',
         'source': 'CALCULATED', 'formula': 'goals + assists',
         'filter_context': 'Same row',
         'tolerance': '0-8 per game',
         'depends_on': 'goals, assists', 'used_by': 'points_per_60'},
        
        # Shots
        {'column': 'shots', 'type': 'INT', 'nullable': 'NO',
         'description': 'Shot attempts (Corsi - all shot attempts)',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Shot"
  - player_role = "event_team_player_1"''',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1, event_type=Shot',
         'tolerance': '0-30 per player, FLAG if >30',
         'depends_on': 'fact_events_player', 
         'used_by': 'shooting_pct, cf, team shots'},
        
        {'column': 'shots_on_goal', 'type': 'INT', 'nullable': 'NO',
         'description': 'Shots on goal (reached goalie)',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Shot"
  - player_role = "event_team_player_1"
  - event_detail IN ("Shot_OnNetSaved", "Shot_Goal", "Shot_TippedOnNetSaved", "Shot_DeflectedOnNetSaved", "Shot_OnNetTippedGoal")''',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1, event_detail filter for on-net',
         'tolerance': '0-20 per player',
         'depends_on': 'fact_events_player.event_detail', 
         'used_by': 'shooting_pct'},
        
        {'column': 'shooting_pct', 'type': 'DECIMAL(5,2)', 'nullable': 'YES',
         'description': 'Shooting percentage',
         'source': 'CALCULATED', 'formula': 'ROUND(goals / shots_on_goal * 100, 1) IF shots_on_goal > 0 ELSE 0',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 5-25%, FLAG if >50%',
         'depends_on': 'goals, shots_on_goal', 'used_by': None},
        
        # Shifts/TOI
        {'column': 'shift_count', 'type': 'INT', 'nullable': 'NO',
         'description': 'Raw shift count (includes micro-shifts from line changes)',
         'source': 'CALCULATED', 
         'formula': 'COUNT(fact_shifts_player) WHERE player_id matches',
         'filter_context': 'player_id, game_id',
         'tolerance': '20-100, WARNING if outside',
         'depends_on': 'fact_shifts_player', 'used_by': None},
        
        {'column': 'logical_shifts', 'type': 'INT', 'nullable': 'NO',
         'description': 'Logical shift count (continuous on-ice periods)',
         'source': 'CALCULATED', 
         'formula': '''COUNT of continuous on-ice periods:
  1. Sort shifts by start time
  2. Group consecutive shifts with <10sec gap
  3. Count resulting groups''',
         'filter_context': 'player_id, game_id, gap threshold <10 seconds',
         'tolerance': '5-20, typical 10-14, FLAG if <5 or >20',
         'depends_on': 'fact_shifts_player sorted by time', 
         'used_by': 'avg_shift, points_per_shift'},
        
        {'column': 'toi_seconds', 'type': 'INT', 'nullable': 'NO',
         'description': 'Time on ice in seconds',
         'source': 'CALCULATED', 
         'formula': 'SUM(shift_duration_seconds) for all player shifts',
         'filter_context': 'player_id, game_id',
         'tolerance': '300-1500 seconds, FLAG if outside',
         'depends_on': 'fact_shifts_player.shift_duration_seconds', 
         'used_by': 'toi_formatted, per_60 calculations, avg_shift'},
        
        {'column': 'avg_shift', 'type': 'DECIMAL(6,2)', 'nullable': 'YES',
         'description': 'Average shift length in seconds',
         'source': 'CALCULATED', 'formula': 'toi_seconds / logical_shifts',
         'filter_context': 'Same row',
         'tolerance': '30-180 seconds, FLAG if outside',
         'depends_on': 'toi_seconds, logical_shifts', 'used_by': None},
        
        # Faceoffs
        {'column': 'fo_wins', 'type': 'INT', 'nullable': 'NO',
         'description': 'Faceoff wins',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Faceoff"
  - player_role = "event_team_player_1" (event_team_player_1 = WINNER)''',
         'filter_context': 'player_id, game_id, event_type=Faceoff, player_role=event_team_player_1',
         'tolerance': '0-25 per player',
         'depends_on': 'fact_events_player', 'used_by': 'fo_pct, team fo_wins'},
        
        {'column': 'fo_losses', 'type': 'INT', 'nullable': 'NO',
         'description': 'Faceoff losses',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Faceoff"
  - player_role = "opp_team_player_1" (opp_team_player_1 = LOSER)''',
         'filter_context': 'player_id, game_id, event_type=Faceoff, player_role=opp_team_player_1',
         'tolerance': '0-25 per player',
         'depends_on': 'fact_events_player', 'used_by': 'fo_pct, team fo_losses'},
        
        {'column': 'fo_pct', 'type': 'DECIMAL(5,2)', 'nullable': 'YES',
         'description': 'Faceoff win percentage',
         'source': 'CALCULATED', 'formula': 'ROUND(fo_wins / (fo_wins + fo_losses) * 100, 1) IF (fo_wins + fo_losses) > 0 ELSE NULL',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 40-60%, FLAG if outside',
         'depends_on': 'fo_wins, fo_losses', 'used_by': None},
        
        # Zone Entry
        {'column': 'zone_entries', 'type': 'INT', 'nullable': 'NO',
         'description': 'Total zone entries',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Zone_Entry_Exit"
  - event_detail CONTAINS "Entry"
  - player_role = "event_team_player_1"''',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1, event_detail filter',
         'tolerance': '0-20 per player, FLAG if >20',
         'depends_on': 'fact_events_player.event_detail', 
         'used_by': 'zone_entry_control_pct'},
        
        {'column': 'zone_entry_carry', 'type': 'INT', 'nullable': 'NO',
         'description': 'Zone entries with puck carry (controlled rush)',
         'source': 'CALCULATED', 
         'formula': 'COUNT WHERE event_detail_2 = "ZoneEntry-Rush"',
         'filter_context': 'Same as zone_entries + event_detail_2 filter',
         'tolerance': '0-15',
         'depends_on': 'fact_events_player.event_detail_2', 
         'used_by': 'zone_entries_controlled'},
        
        {'column': 'zone_entry_pass', 'type': 'INT', 'nullable': 'NO',
         'description': 'Zone entries via pass',
         'source': 'CALCULATED', 
         'formula': 'COUNT WHERE event_detail_2 = "ZoneEntry-Pass"',
         'filter_context': 'Same as zone_entries + event_detail_2 filter',
         'tolerance': '0-10',
         'depends_on': 'fact_events_player.event_detail_2', 
         'used_by': 'zone_entries_controlled'},
        
        {'column': 'zone_entry_dump', 'type': 'INT', 'nullable': 'NO',
         'description': 'Zone entries via dump/chip (uncontrolled)',
         'source': 'CALCULATED', 
         'formula': 'COUNT WHERE event_detail_2 IN ("ZoneEntry-DumpIn", "ZoneEntry-Chip")',
         'filter_context': 'Same as zone_entries + event_detail_2 filter',
         'tolerance': '0-10',
         'depends_on': 'fact_events_player.event_detail_2', 'used_by': None},
        
        {'column': 'zone_entries_controlled', 'type': 'INT', 'nullable': 'NO',
         'description': 'Controlled zone entries (carry + pass)',
         'source': 'CALCULATED', 'formula': 'zone_entry_carry + zone_entry_pass',
         'filter_context': 'Same row',
         'tolerance': '0-20',
         'depends_on': 'zone_entry_carry, zone_entry_pass', 
         'used_by': 'zone_entry_control_pct'},
        
        {'column': 'zone_entry_control_pct', 'type': 'DECIMAL(5,2)', 'nullable': 'YES',
         'description': 'Zone entry control percentage',
         'source': 'CALCULATED', 'formula': 'ROUND(zone_entries_controlled / zone_entries * 100, 1) IF zone_entries > 0 ELSE NULL',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 30-70%, FLAG if outside 0-100',
         'depends_on': 'zone_entries_controlled, zone_entries', 'used_by': None},
        
        # Passes
        {'column': 'pass_attempts', 'type': 'INT', 'nullable': 'NO',
         'description': 'Pass attempts',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Pass"
  - player_role = "event_team_player_1"''',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1, event_type=Pass',
         'tolerance': '10-80 per player',
         'depends_on': 'fact_events_player', 'used_by': 'pass_pct'},
        
        {'column': 'pass_completed', 'type': 'INT', 'nullable': 'NO',
         'description': 'Completed passes',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Pass"
  - player_role = "event_team_player_1"
  - event_successful = "s"''',
         'filter_context': 'Same as pass_attempts + event_successful="s"',
         'tolerance': '5-70 per player',
         'depends_on': 'fact_events_player.event_successful', 
         'used_by': 'pass_pct'},
        
        {'column': 'pass_pct', 'type': 'DECIMAL(5,2)', 'nullable': 'YES',
         'description': 'Pass completion percentage',
         'source': 'CALCULATED', 'formula': 'ROUND(pass_completed / pass_attempts * 100, 1) IF pass_attempts > 0 ELSE NULL',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 50-80%, FLAG if 0% with >10 attempts',
         'depends_on': 'pass_completed, pass_attempts', 'used_by': None},
        
        # Turnovers
        {'column': 'giveaways', 'type': 'INT', 'nullable': 'NO',
         'description': 'Giveaways (lost puck possession)',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Turnover"
  - event_detail CONTAINS "Giveaway"
  - player_role = "event_team_player_1"''',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1, event_detail filter',
         'tolerance': '0-15 per player',
         'depends_on': 'fact_events_player.event_detail', 
         'used_by': 'turnover_diff'},
        
        {'column': 'takeaways', 'type': 'INT', 'nullable': 'NO',
         'description': 'Takeaways (gained puck possession)',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Turnover"
  - event_detail CONTAINS "Takeaway"
  - player_role = "event_team_player_1"''',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1, event_detail filter',
         'tolerance': '0-10 per player',
         'depends_on': 'fact_events_player.event_detail', 
         'used_by': 'turnover_diff'},
    ]
    return pd.DataFrame(columns)


# =============================================================================
# FACT_TEAM_GAME_STATS - Team-Level Aggregated Stats
# =============================================================================
def create_fact_team_game_stats_dict():
    """Team-level aggregated statistics per game."""
    columns = [
        {'column': 'team_game_key', 'type': 'VARCHAR(20)', 'nullable': 'NO',
         'description': 'Primary key',
         'source': 'CALCULATED', 'formula': "f'TG{game_id}{team_sequence:05d}'",
         'filter_context': 'Per team per game (2 rows per game)',
         'tolerance': None, 'depends_on': 'game_id', 'used_by': None},
        
        {'column': 'game_id', 'type': 'INT', 'nullable': 'NO',
         'description': 'Game identifier',
         'source': 'EXPLICIT', 'formula': 'From source data',
         'filter_context': None, 'tolerance': None,
         'depends_on': None, 'used_by': 'Joins'},
        
        {'column': 'team_id', 'type': 'VARCHAR(10)', 'nullable': 'NO',
         'description': 'Team identifier',
         'source': 'LOOKUP', 'formula': 'From fact_gameroster.team_id',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'fact_gameroster', 'used_by': 'dim_team join'},
        
        {'column': 'team_name', 'type': 'VARCHAR(50)', 'nullable': 'NO',
         'description': 'Team name',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.team_name',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'team_id', 'used_by': 'Display, event filtering'},
        
        {'column': 'venue', 'type': 'VARCHAR(10)', 'nullable': 'NO',
         'description': 'Home or Away',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.team_venue',
         'filter_context': None, 'tolerance': 'Home or Away',
         'depends_on': 'fact_gameroster', 'used_by': 'Home/Away splits'},
        
        {'column': 'goals', 'type': 'INT', 'nullable': 'NO',
         'description': 'Team goals scored',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Goal"
  - player_team = team_name
  - player_role = "event_team_player_1"''',
         'filter_context': 'game_id, team_name, player_role=event_team_player_1',
         'tolerance': '0-15, VALIDATE vs dim_schedule (official score)',
         'depends_on': 'fact_events_player', 'used_by': 'shooting_pct, win/loss'},
        
        {'column': 'shots', 'type': 'INT', 'nullable': 'NO',
         'description': 'Team shot attempts (CORSI FOR)',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Shot"
  - player_team = team_name
  - player_role = "event_team_player_1"''',
         'filter_context': 'game_id, team_name, player_role=event_team_player_1, event_type=Shot',
         'tolerance': '40-100 per game, typical 50-70',
         'depends_on': 'fact_events_player', 'used_by': 'corsi_for, shooting_pct'},
        
        {'column': 'sog', 'type': 'INT', 'nullable': 'NO',
         'description': 'Team shots on goal',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Shot"
  - player_team = team_name  
  - player_role = "event_team_player_1"
  - event_detail IN ("Shot_OnNetSaved", "Shot_Goal", "Shot_TippedOnNetSaved", "Shot_DeflectedOnNetSaved")''',
         'filter_context': 'Same as shots + event_detail filter for on-net shots',
         'tolerance': '20-50 per game, typical 25-40',
         'depends_on': 'fact_events_player.event_detail', 'used_by': 'shooting_pct'},
        
        {'column': 'fo_wins', 'type': 'INT', 'nullable': 'NO',
         'description': 'Team faceoff wins',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Faceoff"
  - player_team = team_name
  - player_role = "event_team_player_1" (winner)''',
         'filter_context': 'game_id, team_name, player_role=event_team_player_1, event_type=Faceoff',
         'tolerance': '15-40 per game',
         'depends_on': 'fact_events_player', 'used_by': 'fo_pct'},
        
        {'column': 'fo_losses', 'type': 'INT', 'nullable': 'NO',
         'description': 'Team faceoff losses',
         'source': 'CALCULATED', 
         'formula': 'Total game faceoffs - fo_wins (since faceoffs are symmetric)',
         'filter_context': 'Same game, opposite team wins',
         'tolerance': '15-40 per game, fo_wins + fo_losses = fo_total',
         'depends_on': 'fo_wins, total faceoffs', 'used_by': 'fo_pct'},
        
        {'column': 'fo_total', 'type': 'INT', 'nullable': 'NO',
         'description': 'Total faceoffs in game',
         'source': 'CALCULATED', 'formula': 'fo_wins + fo_losses',
         'filter_context': 'Same row',
         'tolerance': '35-60 per game, same for both teams',
         'depends_on': 'fo_wins, fo_losses', 'used_by': 'fo_pct'},
        
        {'column': 'fo_pct', 'type': 'DECIMAL(5,2)', 'nullable': 'NO',
         'description': 'Faceoff win percentage',
         'source': 'CALCULATED', 'formula': 'ROUND(fo_wins / fo_total * 100, 1)',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 40-60%, sum of both teams = 100%',
         'depends_on': 'fo_wins, fo_total', 'used_by': None},
        
        {'column': 'pass_attempts', 'type': 'INT', 'nullable': 'NO',
         'description': 'Team pass attempts',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Pass"
  - player_team = team_name
  - player_role = "event_team_player_1"''',
         'filter_context': 'game_id, team_name, player_role=event_team_player_1',
         'tolerance': '100-300 per game',
         'depends_on': 'fact_events_player', 'used_by': 'pass_pct'},
        
        {'column': 'pass_completed', 'type': 'INT', 'nullable': 'NO',
         'description': 'Team completed passes',
         'source': 'CALCULATED', 
         'formula': 'Same as pass_attempts + event_successful = "s"',
         'filter_context': 'Same as pass_attempts + event_successful filter',
         'tolerance': '50-250 per game, <=pass_attempts',
         'depends_on': 'fact_events_player.event_successful', 'used_by': 'pass_pct'},
        
        {'column': 'pass_pct', 'type': 'DECIMAL(5,2)', 'nullable': 'NO',
         'description': 'Team pass completion percentage',
         'source': 'CALCULATED', 'formula': 'ROUND(pass_completed / pass_attempts * 100, 1) IF pass_attempts > 0 ELSE 0',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 55-75%, FLAG if 0% with attempts>50',
         'depends_on': 'pass_completed, pass_attempts', 'used_by': None},
        
        {'column': 'giveaways', 'type': 'INT', 'nullable': 'NO',
         'description': 'Team giveaways',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Turnover"
  - event_detail CONTAINS "Giveaway"
  - player_team = team_name
  - player_role = "event_team_player_1"''',
         'filter_context': 'game_id, team_name, player_role=event_team_player_1, event_detail filter',
         'tolerance': '30-100 per game',
         'depends_on': 'fact_events_player.event_detail', 'used_by': 'turnover_diff'},
        
        {'column': 'takeaways', 'type': 'INT', 'nullable': 'NO',
         'description': 'Team takeaways',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Turnover"
  - event_detail CONTAINS "Takeaway"
  - player_team = team_name
  - player_role = "event_team_player_1"''',
         'filter_context': 'game_id, team_name, player_role=event_team_player_1, event_detail filter',
         'tolerance': '10-40 per game',
         'depends_on': 'fact_events_player.event_detail', 'used_by': 'turnover_diff'},
        
        {'column': 'shooting_pct', 'type': 'DECIMAL(5,2)', 'nullable': 'NO',
         'description': 'Team shooting percentage',
         'source': 'CALCULATED', 'formula': 'ROUND(goals / sog * 100, 1) IF sog > 0 ELSE 0',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 5-15%',
         'depends_on': 'goals, sog', 'used_by': None},
    ]
    return pd.DataFrame(columns)


# =============================================================================
# FACT_GOALIE_GAME_STATS - Goalie Statistics
# =============================================================================
def create_fact_goalie_game_stats_dict():
    """Goalie-level statistics per game."""
    columns = [
        {'column': 'goalie_game_key', 'type': 'VARCHAR(20)', 'nullable': 'NO',
         'description': 'Primary key',
         'source': 'CALCULATED', 'formula': "f'GK{game_id}{goalie_sequence:05d}'",
         'filter_context': 'Per goalie per game (2 per game)',
         'tolerance': 'Exactly 2 per tracked game', 'depends_on': 'game_id', 'used_by': None},
        
        {'column': 'game_id', 'type': 'INT', 'nullable': 'NO',
         'description': 'Game identifier',
         'source': 'EXPLICIT', 'formula': 'From source data',
         'filter_context': None, 'tolerance': None,
         'depends_on': None, 'used_by': 'Joins'},
        
        {'column': 'player_id', 'type': 'VARCHAR(10)', 'nullable': 'NO',
         'description': 'Goalie player identifier',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.player_id WHERE player_position="Goalie"',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'fact_gameroster', 'used_by': 'dim_player join'},
        
        {'column': 'player_name', 'type': 'VARCHAR(100)', 'nullable': 'NO',
         'description': 'Goalie name',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.player_full_name',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'player_id', 'used_by': 'Display'},
        
        {'column': 'team_name', 'type': 'VARCHAR(50)', 'nullable': 'NO',
         'description': 'Team name',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.team_name',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'player_id', 'used_by': 'Team aggregations'},
        
        {'column': 'saves', 'type': 'INT', 'nullable': 'NO',
         'description': 'Total saves',
         'source': 'CALCULATED', 'formula': 'shots_against - goals_against (BLB data) OR from tracking save events',
         'filter_context': 'Goalie team',
         'tolerance': '10-50 per game, typical 20-35',
         'depends_on': 'shots_against, goals_against OR fact_events_player Save events', 
         'used_by': 'save_pct'},
        
        {'column': 'goals_against', 'type': 'INT', 'nullable': 'NO',
         'description': 'Goals allowed (excludes empty net if tracked)',
         'source': 'CALCULATED', 'formula': 'Opponent goals when goalie on ice (from dim_schedule or tracking)',
         'filter_context': 'Opponent goals, goalie on ice',
         'tolerance': '0-10 per game, typical 2-5',
         'depends_on': 'dim_schedule.score OR fact_events Goal events', 
         'used_by': 'save_pct, gaa'},
        
        {'column': 'shots_against', 'type': 'INT', 'nullable': 'NO',
         'description': 'Shots faced',
         'source': 'CALCULATED', 'formula': 'saves + goals_against',
         'filter_context': 'Same row',
         'tolerance': '15-55 per game, typical 25-40',
         'depends_on': 'saves, goals_against', 'used_by': 'save_pct'},
        
        {'column': 'save_pct', 'type': 'DECIMAL(5,2)', 'nullable': 'NO',
         'description': 'Save percentage',
         'source': 'CALCULATED', 'formula': 'ROUND(saves / shots_against * 100, 1)',
         'filter_context': 'Same row',
         'tolerance': '70-100%, typical 85-95%, FLAG if <70%',
         'depends_on': 'saves, shots_against', 'used_by': None},
        
        {'column': 'toi_seconds', 'type': 'INT', 'nullable': 'NO',
         'description': 'Time on ice in seconds',
         'source': 'CALCULATED', 'formula': 'Game length (2700 for 45min) - empty_net_time',
         'filter_context': 'Full game minus pulled time',
         'tolerance': '2400-2700 seconds',
         'depends_on': 'Game duration, empty net time', 'used_by': 'GAA calculation'},
        
        {'column': 'empty_net_ga', 'type': 'INT', 'nullable': 'NO',
         'description': 'Goals against when pulled (informational)',
         'source': 'CALCULATED', 'formula': 'COUNT opponent goals WHERE goalie pulled (home/away_team_en = 1)',
         'filter_context': 'Opponent goals when shift.team_en = 1',
         'tolerance': '0-3',
         'depends_on': 'fact_events.empty_net_goal, fact_shifts', 'used_by': 'Adjusted GA stats'},
        
        # Microstats
        {'column': 'saves_rebound', 'type': 'INT', 'nullable': 'NO',
         'description': 'Saves resulting in rebound',
         'source': 'CALCULATED', 
         'formula': '''COUNT(fact_events_player) WHERE:
  - event_type = "Save"
  - player_team = goalie_team
  - event_detail CONTAINS "Rebound"''',
         'filter_context': 'Team save events with Rebound in event_detail',
         'tolerance': '10-60 per game',
         'depends_on': 'fact_events_player.event_detail', 'used_by': 'rebound_control_pct'},
        
        {'column': 'saves_freeze', 'type': 'INT', 'nullable': 'NO',
         'description': 'Saves where goalie froze puck',
         'source': 'CALCULATED', 
         'formula': 'COUNT WHERE event_detail CONTAINS "Freeze"',
         'filter_context': 'Team save events with Freeze in event_detail',
         'tolerance': '10-40 per game',
         'depends_on': 'fact_events_player.event_detail', 'used_by': 'rebound_control_pct'},
        
        {'column': 'saves_glove', 'type': 'INT', 'nullable': 'NO',
         'description': 'Glove saves',
         'source': 'CALCULATED', 
         'formula': 'COUNT WHERE event_detail_2 CONTAINS "Glove"',
         'filter_context': 'Team save events with Glove in event_detail_2',
         'tolerance': '5-30 per game',
         'depends_on': 'fact_events_player.event_detail_2', 'used_by': None},
        
        {'column': 'saves_blocker', 'type': 'INT', 'nullable': 'NO',
         'description': 'Blocker saves',
         'source': 'CALCULATED', 
         'formula': 'COUNT WHERE event_detail_2 CONTAINS "Blocker"',
         'filter_context': 'Team save events with Blocker in event_detail_2',
         'tolerance': '2-20 per game',
         'depends_on': 'fact_events_player.event_detail_2', 'used_by': None},
        
        {'column': 'saves_left_pad', 'type': 'INT', 'nullable': 'NO',
         'description': 'Left pad saves',
         'source': 'CALCULATED', 
         'formula': 'COUNT WHERE event_detail_2 CONTAINS "LeftPad"',
         'filter_context': 'Team save events with LeftPad in event_detail_2',
         'tolerance': '5-30 per game',
         'depends_on': 'fact_events_player.event_detail_2', 'used_by': None},
        
        {'column': 'saves_right_pad', 'type': 'INT', 'nullable': 'NO',
         'description': 'Right pad saves',
         'source': 'CALCULATED', 
         'formula': 'COUNT WHERE event_detail_2 CONTAINS "RightPad"',
         'filter_context': 'Team save events with RightPad in event_detail_2',
         'tolerance': '5-30 per game',
         'depends_on': 'fact_events_player.event_detail_2', 'used_by': None},
        
        {'column': 'rebound_control_pct', 'type': 'DECIMAL(5,2)', 'nullable': 'YES',
         'description': 'Rebound control rate (freeze percentage)',
         'source': 'CALCULATED', 'formula': 'ROUND(saves_freeze / (saves_freeze + saves_rebound) * 100, 1)',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 25-45%',
         'depends_on': 'saves_freeze, saves_rebound', 'used_by': None},
        
        {'column': 'total_save_events', 'type': 'INT', 'nullable': 'YES',
         'description': 'Total save events from tracking (for reference)',
         'source': 'CALCULATED', 
         'formula': 'COUNT(fact_events_player) WHERE event_type="Save" AND player_team=goalie_team',
         'filter_context': 'All team save events',
         'tolerance': 'Compare to saves column',
         'depends_on': 'fact_events_player', 'used_by': 'Validation'},
    ]
    return pd.DataFrame(columns)


# =============================================================================
# FACT_H2H - Head to Head Player Stats
# =============================================================================
def create_fact_h2h_dict():
    """Head-to-head player matchup statistics."""
    columns = [
        {'column': 'h2h_key', 'type': 'VARCHAR(20)', 'nullable': 'NO',
         'description': 'Primary key',
         'source': 'CALCULATED', 'formula': "f'HH{game_id}{pair_sequence:05d}'",
         'filter_context': 'Per opponent pair per game',
         'tolerance': None, 'depends_on': 'game_id', 'used_by': None},
        
        {'column': 'game_id', 'type': 'INT', 'nullable': 'NO',
         'description': 'Game identifier',
         'source': 'EXPLICIT', 'formula': 'From source',
         'filter_context': None, 'tolerance': None,
         'depends_on': None, 'used_by': 'Joins'},
        
        {'column': 'player_1_id', 'type': 'VARCHAR(10)', 'nullable': 'NO',
         'description': 'First player in matchup',
         'source': 'DERIVED', 'formula': 'From shifts where players on ice together on OPPOSITE teams',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'fact_shifts_player', 'used_by': 'dim_player join'},
        
        {'column': 'player_1_name', 'type': 'VARCHAR(100)', 'nullable': 'YES',
         'description': 'First player name',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.player_full_name',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'player_1_id', 'used_by': 'Display'},
        
        {'column': 'player_1_team', 'type': 'VARCHAR(50)', 'nullable': 'YES',
         'description': 'First player team',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.team_name',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'player_1_id', 'used_by': 'Stats attribution'},
        
        {'column': 'player_2_id', 'type': 'VARCHAR(10)', 'nullable': 'NO',
         'description': 'Second player (opponent) in matchup',
         'source': 'DERIVED', 'formula': 'Opponent player on ice same time',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'fact_shifts_player', 'used_by': 'dim_player join'},
        
        {'column': 'player_2_name', 'type': 'VARCHAR(100)', 'nullable': 'YES',
         'description': 'Second player name',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.player_full_name',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'player_2_id', 'used_by': 'Display'},
        
        {'column': 'player_2_team', 'type': 'VARCHAR(50)', 'nullable': 'YES',
         'description': 'Second player team (opponent)',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.team_name',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'player_2_id', 'used_by': 'Stats attribution'},
        
        {'column': 'shifts_together', 'type': 'INT', 'nullable': 'NO',
         'description': 'Number of shifts both players on ice',
         'source': 'CALCULATED', 
         'formula': 'COUNT(shifts) WHERE p1 on ice AND p2 on ice AND p1.team != p2.team',
         'filter_context': 'Shifts where both on ice, opposite teams',
         'tolerance': '1-50',
         'depends_on': 'fact_shifts_player', 'used_by': 'Time/event filtering'},
        
        {'column': 'toi_together', 'type': 'INT', 'nullable': 'YES',
         'description': 'Time on ice together in seconds',
         'source': 'CALCULATED', 
         'formula': 'SUM(shift_duration) for shifts_together',
         'filter_context': 'Same as shifts_together',
         'tolerance': '10-600 seconds',
         'depends_on': 'fact_shifts.shift_duration_seconds', 'used_by': 'Per-60 calculations'},
        
        {'column': 'gf', 'type': 'INT', 'nullable': 'NO',
         'description': 'Goals for (by player_1 team when both on ice)',
         'source': 'CALCULATED', 
         'formula': 'COUNT goals by p1 team during shifts_together',
         'filter_context': 'p1 team goals during shared ice time',
         'tolerance': '0-5',
         'depends_on': 'fact_events_player Goal events, shifts_together', 'used_by': 'gf_pct'},
        
        {'column': 'ga', 'type': 'INT', 'nullable': 'NO',
         'description': 'Goals against (by player_2 team when both on ice)',
         'source': 'CALCULATED', 
         'formula': 'COUNT goals by p2 team during shifts_together',
         'filter_context': 'p2 team goals during shared ice time',
         'tolerance': '0-5',
         'depends_on': 'fact_events_player Goal events, shifts_together', 'used_by': 'gf_pct'},
        
        {'column': 'cf', 'type': 'INT', 'nullable': 'NO',
         'description': 'Corsi for (shot attempts by p1 team)',
         'source': 'CALCULATED', 
         'formula': 'COUNT shot attempts by p1 team during shifts_together',
         'filter_context': 'p1 team shots during shared ice time',
         'tolerance': '0-30',
         'depends_on': 'fact_events_player Shot events, shifts_together', 'used_by': 'cf_pct'},
        
        {'column': 'ca', 'type': 'INT', 'nullable': 'NO',
         'description': 'Corsi against (shot attempts by p2 team)',
         'source': 'CALCULATED', 
         'formula': 'COUNT shot attempts by p2 team during shifts_together',
         'filter_context': 'p2 team shots during shared ice time',
         'tolerance': '0-30',
         'depends_on': 'fact_events_player Shot events, shifts_together', 'used_by': 'cf_pct'},
        
        {'column': 'cf_pct', 'type': 'DECIMAL(5,2)', 'nullable': 'YES',
         'description': 'Corsi for percentage',
         'source': 'CALCULATED', 'formula': 'ROUND(cf / (cf + ca) * 100, 1) IF (cf + ca) > 0 ELSE NULL',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 40-60%',
         'depends_on': 'cf, ca', 'used_by': None},
        
        {'column': 'xgf', 'type': 'DECIMAL(5,2)', 'nullable': 'YES',
         'description': 'Expected goals for',
         'source': 'CALCULATED', 'formula': 'SUM(shot xG values) for p1 team during shifts_together',
         'filter_context': 'p1 team shots during shared ice time',
         'tolerance': '0-3',
         'depends_on': 'xG model, fact_events_player', 'used_by': 'xgf_pct'},
        
        {'column': 'xga', 'type': 'DECIMAL(5,2)', 'nullable': 'YES',
         'description': 'Expected goals against',
         'source': 'CALCULATED', 'formula': 'SUM(shot xG values) for p2 team during shifts_together',
         'filter_context': 'p2 team shots during shared ice time',
         'tolerance': '0-3',
         'depends_on': 'xG model, fact_events_player', 'used_by': 'xgf_pct'},
    ]
    return pd.DataFrame(columns)


# =============================================================================
# FACT_WOWY - With Or Without You Stats
# =============================================================================
def create_fact_wowy_dict():
    """With-or-without-you (teammate impact) statistics."""
    columns = [
        {'column': 'wowy_key', 'type': 'VARCHAR(20)', 'nullable': 'NO',
         'description': 'Primary key',
         'source': 'CALCULATED', 'formula': "f'WY{game_id}{pair_sequence:05d}'",
         'filter_context': 'Per teammate pair per game',
         'tolerance': None, 'depends_on': 'game_id', 'used_by': None},
        
        {'column': 'game_id', 'type': 'INT', 'nullable': 'NO',
         'description': 'Game identifier',
         'source': 'EXPLICIT', 'formula': 'From source',
         'filter_context': None, 'tolerance': None,
         'depends_on': None, 'used_by': 'Joins'},
        
        {'column': 'player_1_id', 'type': 'VARCHAR(10)', 'nullable': 'NO',
         'description': 'Primary player',
         'source': 'DERIVED', 'formula': 'From shifts analysis',
         'filter_context': None, 'tolerance': None,
         'depends_on': 'fact_shifts_player', 'used_by': 'Analysis'},
        
        {'column': 'player_2_id', 'type': 'VARCHAR(10)', 'nullable': 'NO',
         'description': 'Teammate',
         'source': 'DERIVED', 'formula': 'Same team player on ice together',
         'filter_context': 'Same team as player_1',
         'tolerance': None,
         'depends_on': 'fact_shifts_player', 'used_by': 'Analysis'},
        
        {'column': 'shifts_with', 'type': 'INT', 'nullable': 'NO',
         'description': 'Shifts with player_2 on ice',
         'source': 'CALCULATED', 
         'formula': 'COUNT(shifts) WHERE p1 on ice AND p2 on ice AND same team',
         'filter_context': 'Same team, both on ice',
         'tolerance': '1-50',
         'depends_on': 'fact_shifts_player', 'used_by': 'cf_with, etc.'},
        
        {'column': 'shifts_without', 'type': 'INT', 'nullable': 'NO',
         'description': 'Shifts without player_2 on ice',
         'source': 'CALCULATED', 
         'formula': 'COUNT(shifts) WHERE p1 on ice AND p2 NOT on ice',
         'filter_context': 'p1 on ice, p2 not on ice',
         'tolerance': '1-50',
         'depends_on': 'fact_shifts_player', 'used_by': 'cf_without, etc.'},
        
        {'column': 'cf_with', 'type': 'INT', 'nullable': 'NO',
         'description': 'Corsi for when playing with teammate',
         'source': 'CALCULATED', 
         'formula': 'Shot attempts by team during shifts_with',
         'filter_context': 'Team shots during shifts_with',
         'tolerance': '0-30',
         'depends_on': 'fact_events_player, shifts_with', 'used_by': 'cf_pct_with'},
        
        {'column': 'ca_with', 'type': 'INT', 'nullable': 'NO',
         'description': 'Corsi against when playing with teammate',
         'source': 'CALCULATED', 
         'formula': 'Opponent shot attempts during shifts_with',
         'filter_context': 'Opponent shots during shifts_with',
         'tolerance': '0-30',
         'depends_on': 'fact_events_player, shifts_with', 'used_by': 'cf_pct_with'},
        
        {'column': 'cf_without', 'type': 'INT', 'nullable': 'NO',
         'description': 'Corsi for when playing without teammate',
         'source': 'CALCULATED', 
         'formula': 'Shot attempts by team during shifts_without',
         'filter_context': 'Team shots during shifts_without',
         'tolerance': '0-30',
         'depends_on': 'fact_events_player, shifts_without', 'used_by': 'cf_pct_without'},
        
        {'column': 'ca_without', 'type': 'INT', 'nullable': 'NO',
         'description': 'Corsi against when playing without teammate',
         'source': 'CALCULATED', 
         'formula': 'Opponent shot attempts during shifts_without',
         'filter_context': 'Opponent shots during shifts_without',
         'tolerance': '0-30',
         'depends_on': 'fact_events_player, shifts_without', 'used_by': 'cf_pct_without'},
        
        {'column': 'cf_pct_with', 'type': 'DECIMAL(5,2)', 'nullable': 'YES',
         'description': 'CF% when playing together',
         'source': 'CALCULATED', 'formula': 'ROUND(cf_with / (cf_with + ca_with) * 100, 1)',
         'filter_context': 'Same row',
         'tolerance': '0-100%',
         'depends_on': 'cf_with, ca_with', 'used_by': 'cf_pct_diff'},
        
        {'column': 'cf_pct_without', 'type': 'DECIMAL(5,2)', 'nullable': 'YES',
         'description': 'CF% when playing apart',
         'source': 'CALCULATED', 'formula': 'ROUND(cf_without / (cf_without + ca_without) * 100, 1)',
         'filter_context': 'Same row',
         'tolerance': '0-100%',
         'depends_on': 'cf_without, ca_without', 'used_by': 'cf_pct_diff'},
        
        {'column': 'cf_pct_diff', 'type': 'DECIMAL(5,2)', 'nullable': 'YES',
         'description': 'CF% difference (with - without) - teammate impact',
         'source': 'CALCULATED', 'formula': 'cf_pct_with - cf_pct_without',
         'filter_context': 'Same row',
         'tolerance': '-50 to +50, typical -15 to +15',
         'depends_on': 'cf_pct_with, cf_pct_without', 'used_by': 'Teammate impact analysis'},
    ]
    return pd.DataFrame(columns)


# =============================================================================
# VALIDATION THRESHOLDS TABLE
# =============================================================================
def create_validation_thresholds():
    """Master validation thresholds for stat flagging."""
    thresholds = [
        # === PERCENTAGES ===
        {'stat_name': 'zone_entry_control_pct', 'stat_level': 'player', 
         'min_allowed': 0, 'max_allowed': 100, 'typical_min': 30, 'typical_max': 70,
         'severity': 'ERROR', 'description': 'Zone entry control %', 
         'validation_rule': 'Must be 0-100, FLAG if outside typical range'},
        
        {'stat_name': 'fo_pct', 'stat_level': 'player',
         'min_allowed': 0, 'max_allowed': 100, 'typical_min': 40, 'typical_max': 60,
         'severity': 'ERROR', 'description': 'Faceoff win %',
         'validation_rule': 'Must be 0-100'},
        
        {'stat_name': 'pass_pct', 'stat_level': 'player',
         'min_allowed': 0, 'max_allowed': 100, 'typical_min': 50, 'typical_max': 80,
         'severity': 'WARNING', 'description': 'Pass completion %',
         'validation_rule': 'FLAG if 0% with >10 attempts (tracking issue)'},
        
        {'stat_name': 'shooting_pct', 'stat_level': 'player',
         'min_allowed': 0, 'max_allowed': 100, 'typical_min': 5, 'typical_max': 30,
         'severity': 'WARNING', 'description': 'Shooting %',
         'validation_rule': 'FLAG if >50% (statistical anomaly)'},
        
        {'stat_name': 'save_pct', 'stat_level': 'goalie',
         'min_allowed': 0, 'max_allowed': 100, 'typical_min': 80, 'typical_max': 98,
         'severity': 'ERROR', 'description': 'Goalie save %',
         'validation_rule': 'FLAG if <70% (data issue likely)'},
        
        {'stat_name': 'cf_pct', 'stat_level': 'player',
         'min_allowed': 0, 'max_allowed': 100, 'typical_min': 40, 'typical_max': 60,
         'severity': 'WARNING', 'description': 'Corsi for %',
         'validation_rule': 'Must be 0-100'},
        
        # === TEAM PER GAME COUNTS ===
        {'stat_name': 'team_shots', 'stat_level': 'team',
         'min_allowed': 20, 'max_allowed': 120, 'typical_min': 40, 'typical_max': 80,
         'severity': 'WARNING', 'description': 'Team shots (Corsi) per game',
         'validation_rule': '40-80 typical, represents all shot attempts'},
        
        {'stat_name': 'team_sog', 'stat_level': 'team',
         'min_allowed': 10, 'max_allowed': 70, 'typical_min': 20, 'typical_max': 45,
         'severity': 'WARNING', 'description': 'Team SOG per game',
         'validation_rule': 'Should be < shots (Corsi)'},
        
        {'stat_name': 'team_goals', 'stat_level': 'team',
         'min_allowed': 0, 'max_allowed': 20, 'typical_min': 2, 'typical_max': 8,
         'severity': 'ERROR', 'description': 'Team goals per game',
         'validation_rule': 'MUST match dim_schedule official score'},
        
        {'stat_name': 'team_faceoffs', 'stat_level': 'team',
         'min_allowed': 25, 'max_allowed': 80, 'typical_min': 35, 'typical_max': 55,
         'severity': 'WARNING', 'description': 'Total faceoffs per game',
         'validation_rule': 'Both teams should have same fo_total'},
        
        {'stat_name': 'team_passes', 'stat_level': 'team',
         'min_allowed': 50, 'max_allowed': 350, 'typical_min': 100, 'typical_max': 200,
         'severity': 'WARNING', 'description': 'Team passes per game',
         'validation_rule': 'FLAG if pass_completed = 0 (tracking issue)'},
        
        # === PLAYER PER GAME COUNTS ===
        {'stat_name': 'player_shots', 'stat_level': 'player',
         'min_allowed': 0, 'max_allowed': 35, 'typical_min': 0, 'typical_max': 15,
         'severity': 'WARNING', 'description': 'Player shots per game',
         'validation_rule': 'FLAG if >30 (outlier)'},
        
        {'stat_name': 'player_goals', 'stat_level': 'player',
         'min_allowed': 0, 'max_allowed': 6, 'typical_min': 0, 'typical_max': 2,
         'severity': 'ERROR', 'description': 'Player goals per game',
         'validation_rule': 'VALIDATE against BLB records'},
        
        {'stat_name': 'player_assists', 'stat_level': 'player',
         'min_allowed': 0, 'max_allowed': 6, 'typical_min': 0, 'typical_max': 2,
         'severity': 'WARNING', 'description': 'Player assists per game',
         'validation_rule': 'Compare to BLB, may be under-tracked'},
        
        {'stat_name': 'player_zone_entries', 'stat_level': 'player',
         'min_allowed': 0, 'max_allowed': 25, 'typical_min': 0, 'typical_max': 12,
         'severity': 'ERROR', 'description': 'Player zone entries per game',
         'validation_rule': 'FLAG if >20'},
        
        {'stat_name': 'logical_shifts', 'stat_level': 'player',
         'min_allowed': 3, 'max_allowed': 25, 'typical_min': 8, 'typical_max': 16,
         'severity': 'WARNING', 'description': 'Logical shifts per player',
         'validation_rule': 'FLAG if outside 5-20 range'},
        
        # === TIME STATS ===
        {'stat_name': 'toi_seconds', 'stat_level': 'player',
         'min_allowed': 0, 'max_allowed': 3600, 'typical_min': 300, 'typical_max': 1500,
         'severity': 'WARNING', 'description': 'TOI in seconds',
         'validation_rule': 'Max = game length'},
        
        {'stat_name': 'avg_shift_seconds', 'stat_level': 'player',
         'min_allowed': 20, 'max_allowed': 300, 'typical_min': 45, 'typical_max': 120,
         'severity': 'WARNING', 'description': 'Average shift length',
         'validation_rule': 'FLAG if <30 or >180'},
        
        # === GOALIE STATS ===
        {'stat_name': 'goalie_saves', 'stat_level': 'goalie',
         'min_allowed': 5, 'max_allowed': 60, 'typical_min': 15, 'typical_max': 40,
         'severity': 'WARNING', 'description': 'Goalie saves per game',
         'validation_rule': 'Validate against shots_against - goals_against'},
        
        {'stat_name': 'goalie_ga', 'stat_level': 'goalie',
         'min_allowed': 0, 'max_allowed': 12, 'typical_min': 1, 'typical_max': 5,
         'severity': 'WARNING', 'description': 'Goals against per game',
         'validation_rule': 'MUST match opponent score from dim_schedule'},
        
        {'stat_name': 'goalies_per_game', 'stat_level': 'game',
         'min_allowed': 2, 'max_allowed': 2, 'typical_min': 2, 'typical_max': 2,
         'severity': 'ERROR', 'description': 'Goalies per tracked game',
         'validation_rule': 'MUST be exactly 2 per game'},
        
        # === STRUCTURAL ===
        {'stat_name': 'events_per_game', 'stat_level': 'game',
         'min_allowed': 500, 'max_allowed': 2000, 'typical_min': 1000, 'typical_max': 1500,
         'severity': 'WARNING', 'description': 'Events per tracked game',
         'validation_rule': 'FLAG if <500 (incomplete tracking)'},
        
        {'stat_name': 'shifts_per_game', 'stat_level': 'game',
         'min_allowed': 100, 'max_allowed': 300, 'typical_min': 140, 'typical_max': 200,
         'severity': 'WARNING', 'description': 'Shifts per game',
         'validation_rule': 'FLAG if <100'},
    ]
    return pd.DataFrame(thresholds)


# =============================================================================
# MAIN - GENERATE ALL DICTIONARIES
# =============================================================================
def main():
    """Generate all data dictionaries."""
    print("=" * 70)
    print("GENERATING COMPREHENSIVE DATA DICTIONARIES")
    print("=" * 70)
    
    generators = {
        'dd_fact_events': create_fact_events_dict,
        'dd_fact_events_player': create_fact_events_player_dict,
        'dd_fact_shifts': create_fact_shifts_dict,
        'dd_fact_player_game_stats': create_fact_player_game_stats_dict,
        'dd_fact_team_game_stats': create_fact_team_game_stats_dict,
        'dd_fact_goalie_game_stats': create_fact_goalie_game_stats_dict,
        'dd_fact_h2h': create_fact_h2h_dict,
        'dd_fact_wowy': create_fact_wowy_dict,
        'dd_validation_thresholds': create_validation_thresholds,
    }
    
    for name, func in generators.items():
        df = func()
        path = DICT_DIR / f'{name}.csv'
        df.to_csv(path, index=False)
        print(f"  ✅ {name}.csv ({len(df)} entries)")
    
    # Create master column inventory
    print("\n" + "=" * 70)
    print("CREATING MASTER COLUMN INVENTORY")
    print("=" * 70)
    
    fact_files = list(OUTPUT_DIR.glob('fact_*.csv'))
    
    master_rows = []
    for f in sorted(fact_files):
        if 'data_dictionary' in str(f):
            continue
        try:
            df = pd.read_csv(f, nrows=5)  # Just need columns
            table_name = f.stem
            for col in df.columns:
                dtype = str(df[col].dtype)
                sample = str(df[col].dropna().iloc[0])[:50] if len(df[col].dropna()) > 0 else None
                
                # Determine source type
                if 'key' in col.lower() and col != 'shift_key':
                    source = 'CALCULATED'
                elif col.endswith('_id'):
                    source = 'LOOKUP' if col != 'game_id' else 'EXPLICIT'
                elif col.endswith('_name'):
                    source = 'LOOKUP'
                elif col.endswith('_pct') or col.endswith('_diff'):
                    source = 'CALCULATED'
                elif 'total' in col or 'count' in col or col.startswith('avg_'):
                    source = 'CALCULATED'
                else:
                    source = 'EXPLICIT/CALCULATED'  # Needs manual review
                
                master_rows.append({
                    'table_name': table_name,
                    'column_name': col,
                    'data_type': dtype,
                    'source_type': source,
                    'is_primary_key': 'key' in col.lower() and col.endswith('_key'),
                    'is_foreign_key': col.endswith('_key') and not col.endswith(f'{table_name.replace("fact_", "")}_key'),
                    'is_lookup': col.endswith('_id') or col.endswith('_name'),
                    'sample_value': sample,
                })
        except Exception as e:
            print(f"  ⚠️ Error with {f.name}: {e}")
    
    master_df = pd.DataFrame(master_rows)
    master_df.to_csv(DICT_DIR / 'dd_master_column_inventory.csv', index=False)
    print(f"  ✅ dd_master_column_inventory.csv ({len(master_df)} columns across all tables)")
    
    # Summary stats
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Data dictionary files: {len(generators) + 1}")
    print(f"  Total columns documented: {len(master_df)}")
    print(f"  Tables covered: {master_df['table_name'].nunique()}")
    print(f"\n  Output directory: {DICT_DIR}")
    print("=" * 70)


if __name__ == '__main__':
    main()
