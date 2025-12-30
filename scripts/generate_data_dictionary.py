#!/usr/bin/env python3
"""
BenchSight Data Dictionary Generator
=====================================

Creates comprehensive data dictionaries for all tables including:
- Column name, type, description
- Source type (EXPLICIT from tracking vs CALCULATED in ETL)
- Calculation formula and filter context
- Tolerance thresholds for validation
- Dependencies (cascading fields)

Output: data/output/data_dictionary/ folder with CSV files for Supabase

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
# TOLERANCE DEFINITIONS
# =============================================================================
TOLERANCES = {
    # Percentages
    'pct_columns': {
        'min': 0,
        'max': 100,
        'flag_if_outside': True,
        'severity': 'ERROR',
    },
    # Counts per game
    'shots_per_game': {'min': 20, 'max': 100, 'typical': '40-70'},
    'sog_per_game': {'min': 10, 'max': 60, 'typical': '20-40'},
    'goals_per_game': {'min': 0, 'max': 15, 'typical': '3-8'},
    'faceoffs_per_game': {'min': 20, 'max': 80, 'typical': '35-50'},
    'passes_per_game': {'min': 50, 'max': 250, 'typical': '100-180'},
    
    # Per player
    'shots_per_player': {'min': 0, 'max': 30, 'flag_above': 30},
    'goals_per_player': {'min': 0, 'max': 5, 'flag_above': 5},
    'assists_per_player': {'min': 0, 'max': 5, 'flag_above': 5},
    'logical_shifts': {'min': 5, 'max': 20, 'typical': '10-14'},
    'zone_entries_per_player': {'min': 0, 'max': 20, 'flag_above': 20},
    
    # Goalie
    'save_pct': {'min': 70, 'max': 100, 'typical': '85-95'},
    'gaa': {'min': 0, 'max': 10, 'typical': '2-5'},
    
    # Time
    'toi_seconds': {'min': 0, 'max': 3600, 'typical': '600-1200'},
    'avg_shift_seconds': {'min': 30, 'max': 300, 'typical': '60-120'},
}


def create_fact_player_game_stats_dict():
    """Create data dictionary for fact_player_game_stats."""
    
    # Core columns with metadata
    columns = [
        # Primary Key
        {'column': 'player_game_key', 'type': 'VARCHAR(20)', 'description': 'Primary key - unique identifier for player-game combination',
         'source': 'CALCULATED', 'formula': 'PG{game_id}{5-digit sequential}', 'filter_context': 'Per player per game',
         'tolerance': None, 'depends_on': 'game_id', 'used_by': None},
        
        # Foreign Keys
        {'column': 'game_id', 'type': 'INT', 'description': 'Game identifier',
         'source': 'EXPLICIT', 'formula': 'From tracking file name', 'filter_context': None,
         'tolerance': None, 'depends_on': None, 'used_by': 'All game-level calculations'},
        
        {'column': 'player_id', 'type': 'VARCHAR(10)', 'description': 'Player identifier',
         'source': 'EXPLICIT', 'formula': 'From fact_gameroster via player_game_number lookup', 'filter_context': None,
         'tolerance': None, 'depends_on': 'fact_gameroster', 'used_by': 'All player-level calculations'},
        
        {'column': 'player_name', 'type': 'VARCHAR(100)', 'description': 'Player full name',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.player_full_name WHERE player_id matches', 'filter_context': None,
         'tolerance': None, 'depends_on': 'player_id', 'used_by': 'Display only'},
        
        {'column': 'team_name', 'type': 'VARCHAR(50)', 'description': 'Team name',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.team_name WHERE player_id and game_id match', 'filter_context': None,
         'tolerance': None, 'depends_on': 'player_id, game_id', 'used_by': 'Team aggregations'},
        
        # Core Stats - Goals
        {'column': 'goals', 'type': 'INT', 'description': 'Goals scored',
         'source': 'CALCULATED', 'formula': 'COUNT(fact_events_player WHERE event_type="Goal" AND player_role="event_team_player_1")',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1',
         'tolerance': '0-5 per game, flag >5', 'depends_on': 'fact_events_player', 
         'used_by': 'points, shooting_pct, team goals'},
        
        {'column': 'assists', 'type': 'INT', 'description': 'Assists (primary + secondary)',
         'source': 'CALCULATED', 'formula': 'COUNT(fact_events_player WHERE play_detail1 CONTAINS "Assist")',
         'filter_context': 'player_id, game_id',
         'tolerance': '0-5 per game', 'depends_on': 'fact_events_player.play_detail1', 
         'used_by': 'points'},
        
        {'column': 'points', 'type': 'INT', 'description': 'Total points (goals + assists)',
         'source': 'CALCULATED', 'formula': 'goals + assists',
         'filter_context': 'Same row',
         'tolerance': '0-8 per game', 'depends_on': 'goals, assists', 
         'used_by': 'points_per_60'},
        
        # Shots
        {'column': 'shots', 'type': 'INT', 'description': 'Shot attempts (Corsi - all shots)',
         'source': 'CALCULATED', 'formula': 'COUNT(fact_events_player WHERE event_type="Shot" AND player_role="event_team_player_1")',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1',
         'tolerance': '0-30 per player', 'depends_on': 'fact_events_player', 
         'used_by': 'shooting_pct, cf'},
        
        {'column': 'shots_on_goal', 'type': 'INT', 'description': 'Shots on goal (Fenwick subset)',
         'source': 'CALCULATED', 'formula': 'COUNT(fact_events_player WHERE event_type="Shot" AND event_detail IN ("Shot_OnNetSaved","Shot_Goal",...) AND player_role="event_team_player_1")',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1, event_detail filter',
         'tolerance': '0-20 per player', 'depends_on': 'fact_events_player.event_detail', 
         'used_by': 'shooting_pct'},
        
        {'column': 'shooting_pct', 'type': 'DECIMAL(5,2)', 'description': 'Shooting percentage',
         'source': 'CALCULATED', 'formula': 'goals / shots_on_goal * 100',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 5-20%', 'depends_on': 'goals, shots_on_goal', 
         'used_by': None},
        
        # Shifts/TOI
        {'column': 'shift_count', 'type': 'INT', 'description': 'Raw shift count from tracking (micro-shifts)',
         'source': 'CALCULATED', 'formula': 'COUNT(fact_shifts_player WHERE player_id matches)',
         'filter_context': 'player_id, game_id',
         'tolerance': '20-100', 'depends_on': 'fact_shifts_player', 
         'used_by': None},
        
        {'column': 'logical_shifts', 'type': 'INT', 'description': 'Logical shifts (continuous on-ice periods)',
         'source': 'CALCULATED', 'formula': 'COUNT(DISTINCT continuous on-ice periods) - derived from shift start/end analysis',
         'filter_context': 'player_id, game_id, grouped by continuous presence',
         'tolerance': '5-20, typical 10-14', 'depends_on': 'fact_shifts_player', 
         'used_by': 'avg_shift, points_per_shift, fact_player_game_position'},
        
        {'column': 'toi_seconds', 'type': 'INT', 'description': 'Time on ice in seconds',
         'source': 'CALCULATED', 'formula': 'SUM(shift_end_total_seconds - shift_start_total_seconds) for player shifts',
         'filter_context': 'player_id, game_id',
         'tolerance': '300-1500 seconds', 'depends_on': 'fact_shifts', 
         'used_by': 'toi_formatted, per_60 calculations'},
        
        {'column': 'avg_shift', 'type': 'DECIMAL(6,2)', 'description': 'Average shift length in seconds',
         'source': 'CALCULATED', 'formula': 'toi_seconds / logical_shifts',
         'filter_context': 'Same row',
         'tolerance': '30-180 seconds', 'depends_on': 'toi_seconds, logical_shifts', 
         'used_by': None},
        
        # Zone Entry/Exit
        {'column': 'zone_entries', 'type': 'INT', 'description': 'Total zone entries',
         'source': 'CALCULATED', 'formula': 'COUNT(fact_events_player WHERE event_type="Zone_Entry_Exit" AND event_detail CONTAINS "Entry" AND player_role="event_team_player_1")',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1',
         'tolerance': '0-20 per player', 'depends_on': 'fact_events_player', 
         'used_by': 'zone_entry_control_pct'},
        
        {'column': 'zone_entry_carry', 'type': 'INT', 'description': 'Zone entries with puck control (carry/rush)',
         'source': 'CALCULATED', 'formula': 'COUNT WHERE event_detail_2="ZoneEntry-Rush"',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1',
         'tolerance': '0-15', 'depends_on': 'fact_events_player.event_detail_2', 
         'used_by': 'zone_entries_controlled'},
        
        {'column': 'zone_entry_pass', 'type': 'INT', 'description': 'Zone entries via pass',
         'source': 'CALCULATED', 'formula': 'COUNT WHERE event_detail_2="ZoneEntry-Pass"',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1',
         'tolerance': '0-10', 'depends_on': 'fact_events_player.event_detail_2', 
         'used_by': 'zone_entries_controlled'},
        
        {'column': 'zone_entry_dump', 'type': 'INT', 'description': 'Zone entries via dump/chip',
         'source': 'CALCULATED', 'formula': 'COUNT WHERE event_detail_2 IN ("ZoneEntry-DumpIn","ZoneEntry-Chip")',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1',
         'tolerance': '0-10', 'depends_on': 'fact_events_player.event_detail_2', 
         'used_by': None},
        
        {'column': 'zone_entries_controlled', 'type': 'INT', 'description': 'Controlled zone entries (carry + pass)',
         'source': 'CALCULATED', 'formula': 'zone_entry_carry + zone_entry_pass',
         'filter_context': 'Same row',
         'tolerance': '0-20', 'depends_on': 'zone_entry_carry, zone_entry_pass', 
         'used_by': 'zone_entry_control_pct'},
        
        {'column': 'zone_entry_control_pct', 'type': 'DECIMAL(5,2)', 'description': 'Zone entry control percentage',
         'source': 'CALCULATED', 'formula': 'zone_entries_controlled / zone_entries * 100',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 30-70%', 'depends_on': 'zone_entries_controlled, zone_entries', 
         'used_by': None},
        
        # Faceoffs
        {'column': 'fo_wins', 'type': 'INT', 'description': 'Faceoff wins',
         'source': 'CALCULATED', 'formula': 'COUNT(fact_events_player WHERE event_type="Faceoff" AND player_role="event_team_player_1")',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1 (winner)',
         'tolerance': '0-25', 'depends_on': 'fact_events_player', 
         'used_by': 'fo_pct, team fo_wins'},
        
        {'column': 'fo_losses', 'type': 'INT', 'description': 'Faceoff losses',
         'source': 'CALCULATED', 'formula': 'COUNT(fact_events_player WHERE event_type="Faceoff" AND player_role="opp_team_player_1")',
         'filter_context': 'player_id, game_id, player_role=opp_team_player_1 (loser)',
         'tolerance': '0-25', 'depends_on': 'fact_events_player', 
         'used_by': 'fo_pct, team fo_losses'},
        
        {'column': 'fo_pct', 'type': 'DECIMAL(5,2)', 'description': 'Faceoff win percentage',
         'source': 'CALCULATED', 'formula': 'fo_wins / (fo_wins + fo_losses) * 100',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 40-60%', 'depends_on': 'fo_wins, fo_losses', 
         'used_by': None},
        
        # Passes
        {'column': 'pass_attempts', 'type': 'INT', 'description': 'Pass attempts',
         'source': 'CALCULATED', 'formula': 'COUNT(fact_events_player WHERE event_type="Pass" AND player_role="event_team_player_1")',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1',
         'tolerance': '10-80', 'depends_on': 'fact_events_player', 
         'used_by': 'pass_pct'},
        
        {'column': 'pass_completed', 'type': 'INT', 'description': 'Completed passes',
         'source': 'CALCULATED', 'formula': 'COUNT(fact_events_player WHERE event_type="Pass" AND event_successful="s" AND player_role="event_team_player_1")',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1, event_successful="s"',
         'tolerance': '5-70', 'depends_on': 'fact_events_player.event_successful', 
         'used_by': 'pass_pct'},
        
        {'column': 'pass_pct', 'type': 'DECIMAL(5,2)', 'description': 'Pass completion percentage',
         'source': 'CALCULATED', 'formula': 'pass_completed / pass_attempts * 100',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 50-80%', 'depends_on': 'pass_completed, pass_attempts', 
         'used_by': None},
        
        # Turnovers
        {'column': 'giveaways', 'type': 'INT', 'description': 'Giveaways (lost possession)',
         'source': 'CALCULATED', 'formula': 'COUNT(fact_events_player WHERE event_type="Turnover" AND event_detail CONTAINS "Giveaway" AND player_role="event_team_player_1")',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1',
         'tolerance': '0-15', 'depends_on': 'fact_events_player.event_detail', 
         'used_by': 'turnover_diff'},
        
        {'column': 'takeaways', 'type': 'INT', 'description': 'Takeaways (gained possession)',
         'source': 'CALCULATED', 'formula': 'COUNT(fact_events_player WHERE event_type="Turnover" AND event_detail CONTAINS "Takeaway" AND player_role="event_team_player_1")',
         'filter_context': 'player_id, game_id, player_role=event_team_player_1',
         'tolerance': '0-10', 'depends_on': 'fact_events_player.event_detail', 
         'used_by': 'turnover_diff'},
    ]
    
    return pd.DataFrame(columns)


def create_fact_team_game_stats_dict():
    """Create data dictionary for fact_team_game_stats."""
    
    columns = [
        {'column': 'team_game_key', 'type': 'VARCHAR(20)', 'description': 'Primary key',
         'source': 'CALCULATED', 'formula': 'TG{game_id}{5-digit sequential}', 'filter_context': 'Per team per game',
         'tolerance': None, 'depends_on': 'game_id', 'used_by': None},
        
        {'column': 'game_id', 'type': 'INT', 'description': 'Game identifier',
         'source': 'EXPLICIT', 'formula': 'From tracking file', 'filter_context': None,
         'tolerance': None, 'depends_on': None, 'used_by': 'All calculations'},
        
        {'column': 'team_id', 'type': 'VARCHAR(10)', 'description': 'Team identifier',
         'source': 'LOOKUP', 'formula': 'From fact_gameroster', 'filter_context': None,
         'tolerance': None, 'depends_on': 'fact_gameroster', 'used_by': 'All team calculations'},
        
        {'column': 'team_name', 'type': 'VARCHAR(50)', 'description': 'Team name',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.team_name', 'filter_context': None,
         'tolerance': None, 'depends_on': 'team_id', 'used_by': 'Display'},
        
        {'column': 'venue', 'type': 'VARCHAR(10)', 'description': 'Home/Away',
         'source': 'EXPLICIT', 'formula': 'From fact_gameroster.team_venue', 'filter_context': None,
         'tolerance': None, 'depends_on': 'fact_gameroster', 'used_by': None},
        
        {'column': 'goals', 'type': 'INT', 'description': 'Team goals scored',
         'source': 'CALCULATED', 'formula': 'SUM(fact_player_game_stats.goals) WHERE team matches OR COUNT(fact_events_player WHERE event_type="Goal" AND player_team=team_name AND player_role="event_team_player_1")',
         'filter_context': 'All players on team, event_team_player_1 only',
         'tolerance': '0-15, validate vs dim_schedule', 'depends_on': 'fact_events_player', 
         'used_by': 'shooting_pct, win/loss determination'},
        
        {'column': 'shots', 'type': 'INT', 'description': 'Team shot attempts (Corsi For)',
         'source': 'CALCULATED', 'formula': 'COUNT(fact_events_player WHERE event_type="Shot" AND player_team=team_name AND player_role="event_team_player_1")',
         'filter_context': 'All team players, event_team_player_1 only',
         'tolerance': '40-100 per game', 'depends_on': 'fact_events_player', 
         'used_by': 'shooting_pct, corsi_for'},
        
        {'column': 'sog', 'type': 'INT', 'description': 'Team shots on goal',
         'source': 'CALCULATED', 'formula': 'COUNT WHERE event_detail IN (Shot_OnNetSaved, Shot_Goal, Shot_TippedOnNetSaved, Shot_DeflectedOnNetSaved)',
         'filter_context': 'All team players, event_team_player_1, event_detail filter',
         'tolerance': '20-50 per game', 'depends_on': 'fact_events_player.event_detail', 
         'used_by': 'shooting_pct'},
        
        {'column': 'fo_wins', 'type': 'INT', 'description': 'Team faceoff wins',
         'source': 'CALCULATED', 'formula': 'COUNT(fact_events_player WHERE event_type="Faceoff" AND player_team=team_name AND player_role="event_team_player_1")',
         'filter_context': 'Team players where player_role=event_team_player_1 (faceoff winner)',
         'tolerance': '15-40 per game', 'depends_on': 'fact_events_player', 
         'used_by': 'fo_pct'},
        
        {'column': 'fo_losses', 'type': 'INT', 'description': 'Team faceoff losses',
         'source': 'CALCULATED', 'formula': 'total_game_faceoffs - fo_wins',
         'filter_context': 'Total faceoffs in game minus team wins',
         'tolerance': '15-40 per game', 'depends_on': 'fo_wins, total faceoffs', 
         'used_by': 'fo_pct'},
        
        {'column': 'fo_total', 'type': 'INT', 'description': 'Total faceoffs in game',
         'source': 'CALCULATED', 'formula': 'fo_wins + fo_losses OR COUNT(DISTINCT faceoff events)',
         'filter_context': 'Game level',
         'tolerance': '35-60 per game', 'depends_on': 'fo_wins, fo_losses', 
         'used_by': 'fo_pct'},
        
        {'column': 'fo_pct', 'type': 'DECIMAL(5,2)', 'description': 'Faceoff win percentage',
         'source': 'CALCULATED', 'formula': 'fo_wins / fo_total * 100',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 40-60%', 'depends_on': 'fo_wins, fo_total', 
         'used_by': None},
        
        {'column': 'pass_attempts', 'type': 'INT', 'description': 'Team pass attempts',
         'source': 'CALCULATED', 'formula': 'COUNT(fact_events_player WHERE event_type="Pass" AND player_team=team_name AND player_role="event_team_player_1")',
         'filter_context': 'Team players, event_team_player_1',
         'tolerance': '100-300 per game', 'depends_on': 'fact_events_player', 
         'used_by': 'pass_pct'},
        
        {'column': 'pass_completed', 'type': 'INT', 'description': 'Team completed passes',
         'source': 'CALCULATED', 'formula': 'COUNT WHERE event_successful="s"',
         'filter_context': 'Team players, event_team_player_1, event_successful="s"',
         'tolerance': '50-250 per game', 'depends_on': 'fact_events_player.event_successful', 
         'used_by': 'pass_pct'},
        
        {'column': 'pass_pct', 'type': 'DECIMAL(5,2)', 'description': 'Team pass completion percentage',
         'source': 'CALCULATED', 'formula': 'pass_completed / pass_attempts * 100',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 55-75%', 'depends_on': 'pass_completed, pass_attempts', 
         'used_by': None},
        
        {'column': 'giveaways', 'type': 'INT', 'description': 'Team giveaways',
         'source': 'CALCULATED', 'formula': 'COUNT WHERE event_detail CONTAINS "Giveaway"',
         'filter_context': 'Team players, event_team_player_1, event_detail filter',
         'tolerance': '30-100 per game', 'depends_on': 'fact_events_player.event_detail', 
         'used_by': 'turnover_diff'},
        
        {'column': 'takeaways', 'type': 'INT', 'description': 'Team takeaways',
         'source': 'CALCULATED', 'formula': 'COUNT WHERE event_detail CONTAINS "Takeaway"',
         'filter_context': 'Team players, event_team_player_1, event_detail filter',
         'tolerance': '10-40 per game', 'depends_on': 'fact_events_player.event_detail', 
         'used_by': 'turnover_diff'},
        
        {'column': 'shooting_pct', 'type': 'DECIMAL(5,2)', 'description': 'Team shooting percentage',
         'source': 'CALCULATED', 'formula': 'goals / sog * 100',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 5-15%', 'depends_on': 'goals, sog', 
         'used_by': None},
    ]
    
    return pd.DataFrame(columns)


def create_fact_goalie_game_stats_dict():
    """Create data dictionary for fact_goalie_game_stats."""
    
    columns = [
        {'column': 'goalie_game_key', 'type': 'VARCHAR(20)', 'description': 'Primary key',
         'source': 'CALCULATED', 'formula': 'GK{game_id}{5-digit sequential}', 'filter_context': 'Per goalie per game',
         'tolerance': None, 'depends_on': 'game_id', 'used_by': None},
        
        {'column': 'game_id', 'type': 'INT', 'description': 'Game identifier',
         'source': 'EXPLICIT', 'formula': 'From tracking file', 'filter_context': None,
         'tolerance': None, 'depends_on': None, 'used_by': 'All calculations'},
        
        {'column': 'player_id', 'type': 'VARCHAR(10)', 'description': 'Goalie player identifier',
         'source': 'LOOKUP', 'formula': 'fact_gameroster WHERE player_position="Goalie"', 'filter_context': None,
         'tolerance': None, 'depends_on': 'fact_gameroster', 'used_by': None},
        
        {'column': 'player_name', 'type': 'VARCHAR(100)', 'description': 'Goalie name',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.player_full_name', 'filter_context': None,
         'tolerance': None, 'depends_on': 'player_id', 'used_by': 'Display'},
        
        {'column': 'team_name', 'type': 'VARCHAR(50)', 'description': 'Team name',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.team_name', 'filter_context': None,
         'tolerance': None, 'depends_on': 'player_id', 'used_by': None},
        
        {'column': 'saves', 'type': 'INT', 'description': 'Total saves',
         'source': 'CALCULATED', 'formula': 'shots_against - goals_against (from BLB) OR COUNT(Save events for team)',
         'filter_context': 'Goalie team save events',
         'tolerance': '10-50 per game', 'depends_on': 'shots_against, goals_against', 
         'used_by': 'save_pct'},
        
        {'column': 'goals_against', 'type': 'INT', 'description': 'Goals allowed (excludes empty net if flagged)',
         'source': 'CALCULATED', 'formula': 'Opponent goals when goalie on ice',
         'filter_context': 'Opponent goals during goalie shifts',
         'tolerance': '0-10 per game', 'depends_on': 'opponent Goal events, shift data', 
         'used_by': 'save_pct, gaa'},
        
        {'column': 'shots_against', 'type': 'INT', 'description': 'Shots faced',
         'source': 'CALCULATED', 'formula': 'saves + goals_against',
         'filter_context': 'Same row',
         'tolerance': '15-55 per game', 'depends_on': 'saves, goals_against', 
         'used_by': 'save_pct'},
        
        {'column': 'save_pct', 'type': 'DECIMAL(5,2)', 'description': 'Save percentage',
         'source': 'CALCULATED', 'formula': 'saves / shots_against * 100',
         'filter_context': 'Same row',
         'tolerance': '70-100%, typical 85-95%', 'depends_on': 'saves, shots_against', 
         'used_by': None},
        
        {'column': 'toi_seconds', 'type': 'INT', 'description': 'Time on ice in seconds',
         'source': 'CALCULATED', 'formula': 'SUM(shift duration) for goalie OR game_length - empty_net_time',
         'filter_context': 'Goalie shifts',
         'tolerance': '2400-3600 (40-60 min)', 'depends_on': 'fact_shifts', 
         'used_by': 'gaa'},
        
        {'column': 'empty_net_ga', 'type': 'INT', 'description': 'Goals against during empty net (informational)',
         'source': 'CALCULATED', 'formula': 'COUNT opponent goals when goalie pulled',
         'filter_context': 'Goals when home/away_team_en=1',
         'tolerance': '0-3', 'depends_on': 'fact_events.empty_net_goal, fact_shifts', 
         'used_by': 'Adjusted GA calculations'},
        
        # Microstats
        {'column': 'saves_rebound', 'type': 'INT', 'description': 'Saves resulting in rebound',
         'source': 'CALCULATED', 'formula': 'COUNT(Save events WHERE event_detail CONTAINS "Rebound")',
         'filter_context': 'Team save events, event_detail filter',
         'tolerance': '10-60', 'depends_on': 'fact_events_player.event_detail', 
         'used_by': 'rebound_control_pct'},
        
        {'column': 'saves_freeze', 'type': 'INT', 'description': 'Saves where goalie froze puck',
         'source': 'CALCULATED', 'formula': 'COUNT(Save events WHERE event_detail CONTAINS "Freeze")',
         'filter_context': 'Team save events, event_detail filter',
         'tolerance': '10-40', 'depends_on': 'fact_events_player.event_detail', 
         'used_by': 'rebound_control_pct'},
        
        {'column': 'saves_glove', 'type': 'INT', 'description': 'Glove saves',
         'source': 'CALCULATED', 'formula': 'COUNT WHERE event_detail_2 CONTAINS "Glove"',
         'filter_context': 'Team save events, event_detail_2 filter',
         'tolerance': '5-30', 'depends_on': 'fact_events_player.event_detail_2', 
         'used_by': None},
        
        {'column': 'saves_blocker', 'type': 'INT', 'description': 'Blocker saves',
         'source': 'CALCULATED', 'formula': 'COUNT WHERE event_detail_2 CONTAINS "Blocker"',
         'filter_context': 'Team save events, event_detail_2 filter',
         'tolerance': '2-20', 'depends_on': 'fact_events_player.event_detail_2', 
         'used_by': None},
        
        {'column': 'saves_left_pad', 'type': 'INT', 'description': 'Left pad saves',
         'source': 'CALCULATED', 'formula': 'COUNT WHERE event_detail_2 CONTAINS "LeftPad"',
         'filter_context': 'Team save events, event_detail_2 filter',
         'tolerance': '5-30', 'depends_on': 'fact_events_player.event_detail_2', 
         'used_by': None},
        
        {'column': 'saves_right_pad', 'type': 'INT', 'description': 'Right pad saves',
         'source': 'CALCULATED', 'formula': 'COUNT WHERE event_detail_2 CONTAINS "RightPad"',
         'filter_context': 'Team save events, event_detail_2 filter',
         'tolerance': '5-30', 'depends_on': 'fact_events_player.event_detail_2', 
         'used_by': None},
        
        {'column': 'rebound_control_pct', 'type': 'DECIMAL(5,2)', 'description': 'Rebound control rate (freeze %)',
         'source': 'CALCULATED', 'formula': 'saves_freeze / (saves_freeze + saves_rebound) * 100',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 25-45%', 'depends_on': 'saves_freeze, saves_rebound', 
         'used_by': None},
    ]
    
    return pd.DataFrame(columns)


def create_fact_events_player_dict():
    """Create data dictionary for fact_events_player."""
    
    columns = [
        {'column': 'event_player_key', 'type': 'VARCHAR(20)', 'description': 'Primary key',
         'source': 'CALCULATED', 'formula': 'EP{game_id}{5-digit sequential}', 'filter_context': 'Per event-player row',
         'tolerance': None, 'depends_on': 'game_id', 'used_by': None},
        
        {'column': 'event_key', 'type': 'VARCHAR(20)', 'description': 'Foreign key to fact_events',
         'source': 'CALCULATED', 'formula': 'EV{game_id}{5-digit event_index}', 'filter_context': None,
         'tolerance': None, 'depends_on': 'game_id, event_index', 'used_by': 'fact_events join'},
        
        {'column': 'game_id', 'type': 'INT', 'description': 'Game identifier',
         'source': 'EXPLICIT', 'formula': 'From tracking file', 'filter_context': None,
         'tolerance': None, 'depends_on': None, 'used_by': 'All calculations'},
        
        {'column': 'event_index', 'type': 'INT', 'description': 'Event sequence number in game',
         'source': 'EXPLICIT', 'formula': 'From tracking: event_index column', 'filter_context': None,
         'tolerance': None, 'depends_on': None, 'used_by': 'event_key'},
        
        {'column': 'player_id', 'type': 'VARCHAR(10)', 'description': 'Player identifier',
         'source': 'LOOKUP', 'formula': 'fact_gameroster lookup by player_game_number', 'filter_context': None,
         'tolerance': None, 'depends_on': 'player_game_number, fact_gameroster', 'used_by': 'All player stats'},
        
        {'column': 'player_name', 'type': 'VARCHAR(100)', 'description': 'Player name',
         'source': 'LOOKUP', 'formula': 'fact_gameroster.player_full_name', 'filter_context': None,
         'tolerance': None, 'depends_on': 'player_id', 'used_by': 'Display'},
        
        {'column': 'player_team', 'type': 'VARCHAR(50)', 'description': 'Player team name',
         'source': 'EXPLICIT', 'formula': 'From tracking: team_ column transformed to team name', 'filter_context': None,
         'tolerance': None, 'depends_on': 'tracking data', 'used_by': 'Team aggregations'},
        
        {'column': 'player_role', 'type': 'VARCHAR(30)', 'description': 'Player role in event (CRITICAL for stat attribution)',
         'source': 'EXPLICIT', 'formula': 'From tracking: role_abrev_ column (event_team_player_1, opp_team_player_1, etc.)',
         'filter_context': None,
         'tolerance': None, 'depends_on': 'tracking data', 
         'used_by': 'ALL STAT CALCULATIONS - event_team_player_1 gets credit'},
        
        {'column': 'event_type', 'type': 'VARCHAR(30)', 'description': 'Type of event',
         'source': 'EXPLICIT', 'formula': 'From tracking: event_type_ or Type column',
         'filter_context': None,
         'tolerance': None, 'depends_on': 'tracking data', 
         'used_by': 'All stat calculations (Shot, Goal, Faceoff, Pass, Turnover, etc.)'},
        
        {'column': 'event_detail', 'type': 'VARCHAR(50)', 'description': 'Detailed event outcome',
         'source': 'EXPLICIT', 'formula': 'From tracking: event_detail_ column',
         'filter_context': None,
         'tolerance': None, 'depends_on': 'tracking data', 
         'used_by': 'SOG calc (Shot_OnNetSaved, Shot_Goal), turnover type (Giveaway/Takeaway)'},
        
        {'column': 'event_detail_2', 'type': 'VARCHAR(50)', 'description': 'Secondary event detail',
         'source': 'EXPLICIT', 'formula': 'From tracking: event_detail_2_ column',
         'filter_context': None,
         'tolerance': None, 'depends_on': 'tracking data', 
         'used_by': 'Zone entry type (ZoneEntry-Rush/Pass/Dump), goalie save location'},
        
        {'column': 'event_successful', 'type': 'VARCHAR(1)', 'description': 'Success indicator (s/u)',
         'source': 'EXPLICIT', 'formula': 'From tracking: event_successful_ column',
         'filter_context': None,
         'tolerance': None, 'depends_on': 'tracking data', 
         'used_by': 'Pass completion, faceoff result'},
        
        {'column': 'play_detail1', 'type': 'VARCHAR(50)', 'description': 'Play-specific detail (CRITICAL for assists)',
         'source': 'EXPLICIT', 'formula': 'From tracking: play_detail1_ column',
         'filter_context': None,
         'tolerance': None, 'depends_on': 'tracking data', 
         'used_by': 'Assists (AssistPrimary, AssistSecondary)'},
        
        {'column': 'shift_index', 'type': 'INT', 'description': 'Current shift number',
         'source': 'EXPLICIT', 'formula': 'From tracking: shift_index column',
         'filter_context': None,
         'tolerance': None, 'depends_on': 'tracking data', 
         'used_by': 'shift_key, linking events to shifts'},
        
        {'column': 'shift_key', 'type': 'VARCHAR(20)', 'description': 'Foreign key to fact_shifts',
         'source': 'CALCULATED', 'formula': 'SH{game_id}{5-digit shift_index}',
         'filter_context': None,
         'tolerance': None, 'depends_on': 'game_id, shift_index', 
         'used_by': 'fact_shifts join'},
    ]
    
    return pd.DataFrame(columns)


def create_fact_h2h_dict():
    """Create data dictionary for fact_h2h."""
    
    columns = [
        {'column': 'h2h_key', 'type': 'VARCHAR(20)', 'description': 'Primary key',
         'source': 'CALCULATED', 'formula': 'HH{game_id}{5-digit sequential}', 'filter_context': 'Per player pair per game',
         'tolerance': None, 'depends_on': 'game_id', 'used_by': None},
        
        {'column': 'game_id', 'type': 'INT', 'description': 'Game identifier',
         'source': 'EXPLICIT', 'formula': 'From parent data', 'filter_context': None,
         'tolerance': None, 'depends_on': None, 'used_by': 'All calculations'},
        
        {'column': 'player_1_id', 'type': 'VARCHAR(10)', 'description': 'First player in pair',
         'source': 'DERIVED', 'formula': 'From player pairs on ice together', 'filter_context': None,
         'tolerance': None, 'depends_on': 'fact_shifts_player', 'used_by': None},
        
        {'column': 'player_2_id', 'type': 'VARCHAR(10)', 'description': 'Second player in pair (opponent)',
         'source': 'DERIVED', 'formula': 'From player pairs on ice together', 'filter_context': None,
         'tolerance': None, 'depends_on': 'fact_shifts_player', 'used_by': None},
        
        {'column': 'player_1_name', 'type': 'VARCHAR(100)', 'description': 'First player name',
         'source': 'LOOKUP', 'formula': 'fact_gameroster lookup', 'filter_context': None,
         'tolerance': None, 'depends_on': 'player_1_id', 'used_by': 'Display'},
        
        {'column': 'player_2_name', 'type': 'VARCHAR(100)', 'description': 'Second player name',
         'source': 'LOOKUP', 'formula': 'fact_gameroster lookup', 'filter_context': None,
         'tolerance': None, 'depends_on': 'player_2_id', 'used_by': 'Display'},
        
        {'column': 'shifts_together', 'type': 'INT', 'description': 'Shifts where both players on ice',
         'source': 'CALCULATED', 'formula': 'COUNT(shifts WHERE p1 on ice AND p2 on ice)',
         'filter_context': 'Both players present in shift',
         'tolerance': '1-50', 'depends_on': 'fact_shifts_player', 'used_by': 'Pair analysis'},
        
        {'column': 'goals_for', 'type': 'INT', 'description': 'Goals by player_1 team when both on ice',
         'source': 'CALCULATED', 'formula': 'Goals by p1 team during shifts_together',
         'filter_context': 'p1 team goals during shared shifts',
         'tolerance': '0-5', 'depends_on': 'fact_events_player, shifts', 'used_by': 'gf_pct'},
        
        {'column': 'goals_against', 'type': 'INT', 'description': 'Goals against player_1 team when both on ice',
         'source': 'CALCULATED', 'formula': 'Goals by p2 team during shifts_together',
         'filter_context': 'p2 team goals during shared shifts',
         'tolerance': '0-5', 'depends_on': 'fact_events_player, shifts', 'used_by': 'gf_pct'},
        
        {'column': 'cf', 'type': 'INT', 'description': 'Corsi for (shot attempts by p1 team)',
         'source': 'CALCULATED', 'formula': 'Shot attempts by p1 team during shifts_together',
         'filter_context': 'p1 team shots during shared shifts',
         'tolerance': '0-30', 'depends_on': 'fact_events_player', 'used_by': 'cf_pct'},
        
        {'column': 'ca', 'type': 'INT', 'description': 'Corsi against (shot attempts by p2 team)',
         'source': 'CALCULATED', 'formula': 'Shot attempts by p2 team during shifts_together',
         'filter_context': 'p2 team shots during shared shifts',
         'tolerance': '0-30', 'depends_on': 'fact_events_player', 'used_by': 'cf_pct'},
        
        {'column': 'cf_pct', 'type': 'DECIMAL(5,2)', 'description': 'Corsi for percentage',
         'source': 'CALCULATED', 'formula': 'cf / (cf + ca) * 100',
         'filter_context': 'Same row',
         'tolerance': '0-100%, typical 40-60%', 'depends_on': 'cf, ca', 'used_by': None},
    ]
    
    return pd.DataFrame(columns)


def create_validation_thresholds():
    """Create validation thresholds table."""
    
    thresholds = [
        # Percentages
        {'stat_name': 'zone_entry_control_pct', 'min': 0, 'max': 100, 'typical_min': 30, 'typical_max': 70, 'severity': 'ERROR', 'description': 'Zone entry control %'},
        {'stat_name': 'fo_pct', 'min': 0, 'max': 100, 'typical_min': 40, 'typical_max': 60, 'severity': 'ERROR', 'description': 'Faceoff win %'},
        {'stat_name': 'pass_pct', 'min': 0, 'max': 100, 'typical_min': 50, 'typical_max': 80, 'severity': 'ERROR', 'description': 'Pass completion %'},
        {'stat_name': 'shooting_pct', 'min': 0, 'max': 100, 'typical_min': 5, 'typical_max': 25, 'severity': 'WARNING', 'description': 'Shooting %'},
        {'stat_name': 'save_pct', 'min': 0, 'max': 100, 'typical_min': 80, 'typical_max': 98, 'severity': 'ERROR', 'description': 'Goalie save %'},
        {'stat_name': 'cf_pct', 'min': 0, 'max': 100, 'typical_min': 40, 'typical_max': 60, 'severity': 'WARNING', 'description': 'Corsi for %'},
        
        # Per game counts
        {'stat_name': 'team_shots', 'min': 20, 'max': 120, 'typical_min': 40, 'typical_max': 80, 'severity': 'WARNING', 'description': 'Team shots per game'},
        {'stat_name': 'team_sog', 'min': 10, 'max': 70, 'typical_min': 20, 'typical_max': 45, 'severity': 'WARNING', 'description': 'Team SOG per game'},
        {'stat_name': 'team_goals', 'min': 0, 'max': 20, 'typical_min': 2, 'typical_max': 8, 'severity': 'ERROR', 'description': 'Team goals per game'},
        {'stat_name': 'team_faceoffs', 'min': 25, 'max': 80, 'typical_min': 35, 'typical_max': 55, 'severity': 'WARNING', 'description': 'Faceoffs per game'},
        {'stat_name': 'team_passes', 'min': 50, 'max': 350, 'typical_min': 100, 'typical_max': 200, 'severity': 'WARNING', 'description': 'Passes per game'},
        
        # Per player counts
        {'stat_name': 'player_shots', 'min': 0, 'max': 35, 'typical_min': 0, 'typical_max': 15, 'severity': 'WARNING', 'description': 'Player shots per game'},
        {'stat_name': 'player_goals', 'min': 0, 'max': 6, 'typical_min': 0, 'typical_max': 2, 'severity': 'ERROR', 'description': 'Player goals per game'},
        {'stat_name': 'player_assists', 'min': 0, 'max': 6, 'typical_min': 0, 'typical_max': 2, 'severity': 'ERROR', 'description': 'Player assists per game'},
        {'stat_name': 'player_zone_entries', 'min': 0, 'max': 25, 'typical_min': 0, 'typical_max': 12, 'severity': 'ERROR', 'description': 'Player zone entries per game'},
        {'stat_name': 'logical_shifts', 'min': 3, 'max': 25, 'typical_min': 8, 'typical_max': 16, 'severity': 'WARNING', 'description': 'Logical shifts per player'},
        
        # Time
        {'stat_name': 'toi_seconds', 'min': 0, 'max': 3600, 'typical_min': 300, 'typical_max': 1500, 'severity': 'WARNING', 'description': 'TOI in seconds'},
        {'stat_name': 'avg_shift_seconds', 'min': 20, 'max': 300, 'typical_min': 45, 'typical_max': 120, 'severity': 'WARNING', 'description': 'Average shift length'},
        
        # Goalie
        {'stat_name': 'goalie_saves', 'min': 5, 'max': 60, 'typical_min': 15, 'typical_max': 40, 'severity': 'WARNING', 'description': 'Goalie saves per game'},
        {'stat_name': 'goalie_ga', 'min': 0, 'max': 12, 'typical_min': 1, 'typical_max': 5, 'severity': 'WARNING', 'description': 'Goals against per game'},
        {'stat_name': 'goalies_per_game', 'min': 2, 'max': 2, 'typical_min': 2, 'typical_max': 2, 'severity': 'ERROR', 'description': 'Must be exactly 2 goalies'},
    ]
    
    return pd.DataFrame(thresholds)


def main():
    """Generate all data dictionaries."""
    print("=" * 60)
    print("GENERATING DATA DICTIONARIES")
    print("=" * 60)
    
    # Create dictionaries
    dicts = {
        'dd_fact_player_game_stats': create_fact_player_game_stats_dict(),
        'dd_fact_team_game_stats': create_fact_team_game_stats_dict(),
        'dd_fact_goalie_game_stats': create_fact_goalie_game_stats_dict(),
        'dd_fact_events_player': create_fact_events_player_dict(),
        'dd_fact_h2h': create_fact_h2h_dict(),
        'dd_validation_thresholds': create_validation_thresholds(),
    }
    
    # Save to CSV
    for name, df in dicts.items():
        path = DICT_DIR / f'{name}.csv'
        df.to_csv(path, index=False)
        print(f"  ✅ Created {name}.csv ({len(df)} rows)")
    
    # Create master file with all tables
    print("\n" + "=" * 60)
    print("CREATING MASTER DATA DICTIONARY")
    print("=" * 60)
    
    # Load all fact tables and create minimal dictionary
    fact_files = [f for f in OUTPUT_DIR.glob('fact_*.csv')]
    
    master_rows = []
    for f in fact_files:
        try:
            df = pd.read_csv(f)
            table_name = f.stem
            for col in df.columns:
                dtype = str(df[col].dtype)
                master_rows.append({
                    'table_name': table_name,
                    'column_name': col,
                    'data_type': dtype,
                    'is_key': 'key' in col.lower(),
                    'is_id': col.endswith('_id'),
                    'sample_value': str(df[col].dropna().iloc[0])[:50] if len(df[col].dropna()) > 0 else None,
                })
        except Exception as e:
            print(f"  ⚠️ Error with {f.name}: {e}")
    
    master_df = pd.DataFrame(master_rows)
    master_df.to_csv(DICT_DIR / 'dd_master_all_columns.csv', index=False)
    print(f"  ✅ Created dd_master_all_columns.csv ({len(master_df)} columns)")
    
    print("\n" + "=" * 60)
    print(f"Data dictionaries saved to: {DICT_DIR}")
    print("=" * 60)


if __name__ == '__main__':
    main()
