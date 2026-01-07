#!/usr/bin/env python3
"""
Generate Enhanced Table Documentation HTML
Creates detailed documentation for each table with:
- Table description, purpose, source module
- Column descriptions, context, calculations, types
"""

import os
import pandas as pd
from datetime import datetime

OUTPUT_DIR = 'data/output'
HTML_DIR = 'docs/html/tables'

# =============================================================================
# TABLE METADATA
# =============================================================================
TABLE_META = {
    'fact_events': {
        'description': 'Core event table - one row per unique event in the game.',
        'purpose': 'Central fact table linking all game events with players, teams, and outcomes.',
        'source_module': 'src/core/base_etl.py:create_derived_tables() line 775',
        'logic': 'Groups fact_events_tracking by event_id, taking first row after sorting by event_type priority (Goal > Shot > Faceoff > Pass > Possession). This ensures goals are captured correctly.',
        'key_rules': 'Goals counted via event_type="Goal" AND event_detail="Goal_Scored". Shot_Goal is the shot, not the goal.',
    },
    'fact_events_tracking': {
        'description': 'Tracking-level event data - one row per player-event combination.',
        'purpose': 'Links events to individual players with their specific roles.',
        'source_module': 'src/core/base_etl.py:load_tracking_data() line 541',
        'logic': 'Raw tracking data loaded from game Excel files, enhanced with FKs and player IDs.',
        'key_rules': 'event_player_1 = primary player (scorer, shooter, passer). player_role indicates role type.',
    },
    'fact_tracking': {
        'description': 'Location and timing data for tracking points.',
        'purpose': 'XY coordinate data for shot charts and heat maps.',
        'source_module': 'src/core/base_etl.py:create_derived_tables() line 823',
        'logic': 'Unique tracking events grouped by tracking_event_key.',
    },
    'fact_shifts': {
        'description': 'Player shift data - when players are on the ice.',
        'purpose': 'Track ice time, line combinations, and shift patterns.',
        'source_module': 'src/core/base_etl.py:create_derived_tables()',
        'logic': 'Shift start/end times with player assignments.',
    },
    'fact_shifts_tracking': {
        'description': 'Detailed shift tracking with all players on ice.',
        'purpose': 'Links shifts to events and tracks all players present.',
        'source_module': 'src/core/base_etl.py:create_derived_tables()',
        'logic': 'Shift data with event associations.',
    },
    'fact_gameroster': {
        'description': 'Game roster - players participating in each game.',
        'purpose': 'Links players to games with jersey numbers and positions.',
        'source_module': 'src/core/base_etl.py:enhance_gameroster() line 337',
        'logic': 'Loaded from roster.json files in each game folder.',
    },
    'fact_plays': {
        'description': 'Play sequences - connected series of events.',
        'purpose': 'Group related events into offensive/defensive plays.',
        'source_module': 'src/core/base_etl.py:create_derived_tables()',
        'logic': 'Events grouped by play_key.',
    },
    'fact_sequences': {
        'description': 'Event sequences - chronological event chains.',
        'purpose': 'Track event ordering within possessions.',
        'source_module': 'src/core/base_etl.py:create_derived_tables()',
        'logic': 'Events grouped by sequence_key.',
    },
    'fact_faceoffs': {
        'description': 'Faceoff events with win/loss outcomes.',
        'purpose': 'Analyze faceoff performance by player, zone, opponent.',
        'source_module': 'src/core/base_etl.py:create_derived_tables()',
        'logic': 'Filtered from fact_events where event_type="Faceoff".',
    },
    'fact_penalties': {
        'description': 'Penalty events with type and duration.',
        'purpose': 'Track penalty minutes, types, and situations.',
        'source_module': 'src/core/base_etl.py:create_derived_tables()',
        'logic': 'Filtered from fact_events where event_type="Penalty".',
    },
    'fact_saves': {
        'description': 'Goalie save events.',
        'purpose': 'Track saves by goalie, shot type, danger level.',
        'source_module': 'src/core/base_etl.py:create_derived_tables()',
        'logic': 'Filtered from fact_events where is_save=1.',
    },
    'fact_rushes': {
        'description': 'Rush events - fast breaks and odd-man rushes.',
        'purpose': 'Analyze rush opportunities and outcomes.',
        'source_module': 'src/core/base_etl.py:create_derived_tables()',
        'logic': 'Filtered from fact_events where is_rush=1.',
    },
    'fact_breakouts': {
        'description': 'Breakout events from defensive zone.',
        'purpose': 'Analyze transition play from defense.',
        'source_module': 'src/core/base_etl.py:create_derived_tables()',
        'logic': 'Filtered from fact_events where is_breakout=1.',
    },
    'fact_zone_entries': {
        'description': 'Offensive zone entry events.',
        'purpose': 'Analyze zone entry methods (carry, dump, pass).',
        'source_module': 'src/core/base_etl.py:create_derived_tables()',
        'logic': 'Filtered from fact_events where is_zone_entry=1.',
    },
    'fact_zone_exits': {
        'description': 'Defensive zone exit events.',
        'purpose': 'Analyze zone exit methods and success rates.',
        'source_module': 'src/core/base_etl.py:create_derived_tables()',
        'logic': 'Filtered from fact_events where is_zone_exit=1.',
    },
    'fact_turnovers_detailed': {
        'description': 'Turnover events with context.',
        'purpose': 'Analyze giveaways and takeaways in detail.',
        'source_module': 'src/core/base_etl.py:create_derived_tables()',
        'logic': 'Filtered from fact_events where is_turnover=1.',
    },
    'fact_high_danger_chances': {
        'description': 'High-danger scoring chances.',
        'purpose': 'Track dangerous scoring opportunities.',
        'source_module': 'src/core/base_etl.py:create_derived_tables()',
        'logic': 'Filtered from fact_events where is_high_danger=1.',
    },
    'fact_scoring_chances_detailed': {
        'description': 'All scoring chances with danger level.',
        'purpose': 'Comprehensive scoring chance analysis.',
        'source_module': 'src/core/base_etl.py:create_derived_tables()',
        'logic': 'Filtered from fact_events where is_scoring_chance=1.',
    },
    'fact_cycle_events': {
        'description': 'Cycling events in offensive zone.',
        'purpose': 'Analyze puck cycling and sustained pressure.',
        'source_module': 'src/core/base_etl.py:create_derived_tables()',
        'logic': 'Filtered from fact_events where is_cycle=1.',
    },
    'fact_player_game_position': {
        'description': 'Player positions by game.',
        'purpose': 'Track position assignments per game.',
        'source_module': 'src/advanced/extended_tables.py',
        'logic': 'Derived from gameroster position data.',
    },
    'fact_game_status': {
        'description': 'Game processing status and completeness.',
        'purpose': 'QA tracking for data completeness.',
        'source_module': 'src/advanced/extended_tables.py',
        'logic': 'Generated during ETL to track processing status.',
    },
    'fact_shift_players': {
        'description': 'Players on ice during each shift.',
        'purpose': 'Track line combinations and matchups.',
        'source_module': 'src/core/base_etl.py:create_derived_tables()',
        'logic': 'Derived from shift data.',
    },
    'fact_draft': {
        'description': 'Draft information from BLB tables.',
        'purpose': 'Track player draft history.',
        'source_module': 'src/core/base_etl.py:load_blb_tables() line 420',
        'logic': 'Loaded from BLB_Tables.xlsx Draft sheet.',
    },
    'fact_registration': {
        'description': 'Player registration data.',
        'purpose': 'Track player registrations and eligibility.',
        'source_module': 'src/core/base_etl.py:load_blb_tables()',
        'logic': 'Loaded from BLB_Tables.xlsx Registration sheet.',
    },
    'fact_leadership': {
        'description': 'Team leadership assignments.',
        'purpose': 'Track captains and alternates.',
        'source_module': 'src/core/base_etl.py:load_blb_tables()',
        'logic': 'Loaded from BLB_Tables.xlsx Leadership sheet.',
    },
    'fact_season_summary': {
        'description': 'Season summary statistics.',
        'purpose': 'Aggregate season-level stats.',
        'source_module': 'src/core/base_etl.py',
        'logic': 'Aggregated from game data.',
    },
    'dim_player': {
        'description': 'Player dimension - master player list.',
        'purpose': 'Central player reference with ratings and attributes.',
        'source_module': 'src/core/base_etl.py:load_blb_tables()',
        'logic': 'Loaded from BLB_Tables.xlsx Player sheet. player_id format: P_LASTNAME_N',
    },
    'dim_team': {
        'description': 'Team dimension - all teams.',
        'purpose': 'Team reference with abbreviations and names.',
        'source_module': 'src/core/base_etl.py:load_blb_tables()',
        'logic': 'Loaded from BLB_Tables.xlsx Team sheet.',
    },
    'dim_season': {
        'description': 'Season dimension - season definitions.',
        'purpose': 'Define season boundaries and names.',
        'source_module': 'src/core/base_etl.py:load_blb_tables()',
        'logic': 'Loaded from BLB_Tables.xlsx Season sheet.',
    },
    'dim_schedule': {
        'description': 'Game schedule dimension.',
        'purpose': 'Game schedule with dates, teams, venues.',
        'source_module': 'src/core/base_etl.py:load_blb_tables()',
        'logic': 'Loaded from BLB_Tables.xlsx Schedule sheet.',
    },
    'dim_venue': {
        'description': 'Venue/rink dimension.',
        'purpose': 'Rink locations and attributes.',
        'source_module': 'src/core/base_etl.py:create_reference_tables() line 942',
        'logic': 'Distinct venues from schedule data.',
    },
    'dim_period': {
        'description': 'Period dimension (1, 2, 3, OT).',
        'purpose': 'Period reference for joins.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Static reference table.',
    },
    'dim_event_type': {
        'description': 'Event type dimension (Goal, Shot, Pass, etc.).',
        'purpose': 'Classify event types.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Distinct event types from tracking data.',
    },
    'dim_event_detail': {
        'description': 'Event detail dimension (Goal_Scored, Shot_Goal, etc.).',
        'purpose': 'Detailed event classification.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Distinct event details from tracking data. CRITICAL: Goal_Scored = goal, Shot_Goal = shot that led to goal.',
    },
    'dim_event_detail_2': {
        'description': 'Secondary event detail dimension.',
        'purpose': 'Additional event context.',
        'source_module': 'src/core/base_etl.py:_create_dim_event_detail_2() line 1115',
        'logic': 'Secondary details like pass type, shot location.',
    },
    'dim_play_detail': {
        'description': 'Play detail dimension.',
        'purpose': 'Play-level detail classification.',
        'source_module': 'src/core/base_etl.py:_create_dim_play_detail() line 1259',
        'logic': 'Standardized play details.',
    },
    'dim_play_detail_2': {
        'description': 'Secondary play detail dimension.',
        'purpose': 'Additional play context.',
        'source_module': 'src/core/base_etl.py:_create_dim_play_detail_2() line 1326',
        'logic': 'Secondary play details.',
    },
    'dim_position': {
        'description': 'Position dimension (C, LW, RW, D, G).',
        'purpose': 'Player position reference.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Static position reference.',
    },
    'dim_zone': {
        'description': 'Zone dimension (Offensive, Defensive, Neutral).',
        'purpose': 'Rink zone reference.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Static zone reference.',
    },
    'dim_zone_entry_type': {
        'description': 'Zone entry type dimension (Carry, Dump, Pass).',
        'purpose': 'Classify zone entry methods.',
        'source_module': 'src/core/base_etl.py:_create_dim_zone_entry_type() line 1146',
        'logic': 'Distinct zone entry types.',
    },
    'dim_zone_exit_type': {
        'description': 'Zone exit type dimension (Carry, Pass, Clear).',
        'purpose': 'Classify zone exit methods.',
        'source_module': 'src/core/base_etl.py:_create_dim_zone_exit_type() line 1166',
        'logic': 'Distinct zone exit types.',
    },
    'dim_stoppage_type': {
        'description': 'Stoppage type dimension (Icing, Offside, etc.).',
        'purpose': 'Classify game stoppages.',
        'source_module': 'src/core/base_etl.py:_create_dim_stoppage_type() line 1186',
        'logic': 'Distinct stoppage types.',
    },
    'dim_giveaway_type': {
        'description': 'Giveaway type dimension.',
        'purpose': 'Classify giveaway causes.',
        'source_module': 'src/core/base_etl.py:_create_dim_giveaway_type() line 1207',
        'logic': 'Distinct giveaway types.',
    },
    'dim_takeaway_type': {
        'description': 'Takeaway type dimension.',
        'purpose': 'Classify takeaway methods.',
        'source_module': 'src/core/base_etl.py:_create_dim_takeaway_type() line 1228',
        'logic': 'Distinct takeaway types.',
    },
    'dim_shot_type': {
        'description': 'Shot type dimension (Wrist, Slap, Snap, etc.).',
        'purpose': 'Classify shot types.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Distinct shot types.',
    },
    'dim_pass_type': {
        'description': 'Pass type dimension.',
        'purpose': 'Classify pass types.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Distinct pass types.',
    },
    'dim_success': {
        'description': 'Success dimension (Successful, Failed).',
        'purpose': 'Binary success indicator.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Static reference.',
    },
    'dim_situation': {
        'description': 'Situation dimension (5v5, PP, PK, etc.).',
        'purpose': 'Game situation context.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Distinct strength situations.',
    },
    'dim_danger_level': {
        'description': 'Danger level dimension (Low, Medium, High).',
        'purpose': 'Scoring chance danger classification.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Static reference with xG multipliers.',
    },
    'dim_shift_start_type': {
        'description': 'Shift start type (On-the-fly, Stoppage).',
        'purpose': 'Classify how shifts begin.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Distinct shift start types.',
    },
    'dim_shift_stop_type': {
        'description': 'Shift end type (On-the-fly, Whistle, Period End).',
        'purpose': 'Classify how shifts end.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Distinct shift end types.',
    },
    'dim_shift_duration': {
        'description': 'Shift duration buckets.',
        'purpose': 'Categorize shift lengths.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Duration buckets (Short, Normal, Long).',
    },
    'dim_shift_quality_tier': {
        'description': 'Shift quality tier dimension.',
        'purpose': 'Rate shift performance.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Quality ratings based on events.',
    },
    'dim_time_bucket': {
        'description': 'Time bucket dimension (period minutes).',
        'purpose': 'Time-based aggregation.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Minute buckets within periods.',
    },
    'dim_game_state': {
        'description': 'Game state dimension (Tied, Leading, Trailing).',
        'purpose': 'Score situation context.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Static reference.',
    },
    'dim_player_role': {
        'description': 'Player role dimension (Shooter, Passer, Blocker, etc.).',
        'purpose': 'Event role classification.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Distinct player roles from tracking data.',
    },
    'dim_assist_type': {
        'description': 'Assist type dimension (Primary, Secondary).',
        'purpose': 'Classify assist types.',
        'source_module': 'src/core/base_etl.py:create_reference_tables()',
        'logic': 'Static reference.',
    },
    'dim_league': {
        'description': 'League dimension.',
        'purpose': 'League reference (NORAD).',
        'source_module': 'src/core/base_etl.py:load_blb_tables()',
        'logic': 'Loaded from BLB.',
    },
    'dim_playerurlref': {
        'description': 'Player URL reference for noradhockey.com.',
        'purpose': 'Link players to external URLs.',
        'source_module': 'src/core/base_etl.py:load_blb_tables()',
        'logic': 'Player URL mappings.',
    },
    'dim_randomnames': {
        'description': 'Random name mappings for anonymization.',
        'purpose': 'Privacy protection.',
        'source_module': 'src/core/base_etl.py:load_blb_tables()',
        'logic': 'Name mapping table.',
    },
    'qa_goal_accuracy': {
        'description': 'QA table comparing goals to noradhockey.com.',
        'purpose': 'Validate goal counts match official records.',
        'source_module': 'src/qa/build_qa_facts.py',
        'logic': 'Compares ETL goal counts to official game results.',
    },
    'qa_data_completeness': {
        'description': 'QA table tracking data completeness.',
        'purpose': 'Monitor data quality metrics.',
        'source_module': 'src/qa/build_qa_facts.py',
        'logic': 'Calculates null percentages and coverage.',
    },
}

# =============================================================================
# COLUMN METADATA - DEEP CONTEXT
# =============================================================================
COLUMN_META = {
    # =========================================================================
    # PRIMARY KEYS AND IDENTIFIERS
    # =========================================================================
    'event_id': {
        'desc': 'Unique event identifier (PK)',
        'context': 'Format: EV{game_id}{event_index:05d}. Example: EV1896901000. One event_id per unique game event (goal, shot, faceoff, etc). Multiple tracking rows may share the same event_id if multiple players involved.',
        'calc': 'format_key("EV", game_id, event_index) in key_utils.py:79',
        'type': 'Derived'
    },
    'game_id': {
        'desc': 'Game identifier from noradhockey.com',
        'context': 'Numeric ID from league website URL. Example: 18969. Links to dim_schedule.game_id. Used as prefix in all composite keys.',
        'calc': 'Extracted from tracking file directory name (data/raw/games/{game_id}/)',
        'type': 'Explicit'
    },
    'player_id': {
        'desc': 'Unique player identifier',
        'context': 'Format: P_LASTNAME_N where N is disambiguation number (1,2,3...). Example: P_SMITH_1. Matches across games. Linked via gameroster player_game_number + team.',
        'calc': 'link_player_ids() in base_etl.py:738 - looks up (game_id, team, jersey_number) in player_lookup',
        'type': 'Derived'
    },
    'team_id': {
        'desc': 'Team identifier FK',
        'context': 'Links to dim_team. Format matches team abbreviation (e.g., "TEAM1"). Used for both home_team_id and away_team_id.',
        'calc': 'Lookup on team name/code in add_all_fkeys.py',
        'type': 'FK'
    },
    'season_id': {
        'desc': 'Season identifier',
        'context': 'Format: NORAD_YYYY_SS (e.g., NORAD_2024_FA for Fall 2024). Links to dim_season.',
        'calc': 'Derived from game date via schedule lookup',
        'type': 'Derived'
    },
    'tracking_event_key': {
        'desc': 'Tracking-level event key',
        'context': 'Format: TV{game_id}{tracking_event_index:05d}. One per row in fact_events_tracking. May differ from event_id for zone entries where tracking splits events.',
        'calc': 'format_key("TV", game_id, tracking_event_index) in key_utils.py:89',
        'type': 'Derived'
    },
    
    # =========================================================================
    # PLAYER ROLE COLUMNS - CRITICAL CONTEXT
    # =========================================================================
    'player_role': {
        'desc': 'Player role in the event',
        'context': '''CRITICAL MAPPING:
• event_player_1 = PRIMARY player (shooter on shot, scorer on goal, winner on faceoff, passer on pass)
• event_player_2 = SECONDARY player (primary assist on goal, receiver on pass)
• event_player_3 = TERTIARY player (secondary assist on goal)
• event_player_4/5/6 = Additional players on ice for event team
• event_goalie = Goalie for event team
• opp_player_1 = PRIMARY opposing player (goalie on shot, loser on faceoff, defender on rush)
• opp_player_2/3/4/5/6 = Other opposing players on ice
• opp_goalie = Opposing goalie''',
        'calc': 'From tracking spreadsheet, normalized via normalize_player_role() to remove "_team_" suffix',
        'type': 'Explicit'
    },
    'event_player_ids': {
        'desc': 'Pipe-separated player_ids for event team',
        'context': 'Aggregated from all tracking rows where player_role starts with "event_". Example: "P_SMITH_1|P_JONES_2|P_BROWN_1". Order matches role number.',
        'calc': 'add_player_id_columns() in key_utils.py:266 - groups by event_id, joins player_ids with "|"',
        'type': 'Derived'
    },
    'opp_player_ids': {
        'desc': 'Pipe-separated player_ids for opposing team',
        'context': 'Aggregated from all tracking rows where player_role starts with "opp_". Example: "P_WHITE_1|P_BLACK_1".',
        'calc': 'add_player_id_columns() in key_utils.py:266 - groups by event_id, joins player_ids with "|"',
        'type': 'Derived'
    },
    'player_game_number': {
        'desc': 'Jersey number in this game',
        'context': 'Used with team_venue to lookup player_id from gameroster. Example: "17", "99".',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    
    # =========================================================================
    # PERIOD AND TIME COLUMNS
    # =========================================================================
    'period': {
        'desc': 'Period number',
        'context': 'Values: 1, 2, 3 (regulation), 4 (OT). From tracking spreadsheet.',
        'calc': 'Direct from tracking data',
        'type': 'Explicit'
    },
    'period_id': {
        'desc': 'FK to dim_period',
        'context': 'Format: P{period}. Example: P1, P2, P3, POT. Links to dim_period for period attributes.',
        'calc': 'Lookup on period value in add_all_fkeys.py',
        'type': 'FK'
    },
    'event_start_min': {
        'desc': 'Event start minute within period',
        'context': 'Minutes elapsed since period start. Range: 0-20 (or 0-5 for OT). Combined with event_start_sec for exact time.',
        'calc': 'From tracking spreadsheet time columns',
        'type': 'Explicit'
    },
    'event_start_sec': {
        'desc': 'Event start second within minute',
        'context': 'Seconds 0-59. Combined with event_start_min for period time.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'event_end_min': {
        'desc': 'Event end minute (for duration events)',
        'context': 'Only populated for events with duration (shifts, possessions). Null for instantaneous events (shots, faceoffs).',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'event_end_sec': {
        'desc': 'Event end second within minute',
        'context': 'Only populated when event_end_min is populated.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'running_video_time': {
        'desc': 'Running video timestamp in seconds',
        'context': 'Continuous time from video start, used for video syncing. From {game_id}_video_times.xlsx.',
        'calc': 'From video times file, mapped to events',
        'type': 'Explicit'
    },
    'event_running_start': {
        'desc': 'Running time at event start (total seconds)',
        'context': 'Continuous seconds from game start, ignoring intermissions. Period 1 minute 5:30 = 330 seconds.',
        'calc': '(period-1) * 1200 + event_start_min * 60 + event_start_sec',
        'type': 'Calculated'
    },
    'event_running_end': {
        'desc': 'Running time at event end (total seconds)',
        'context': 'Continuous seconds from game start at event end.',
        'calc': '(period-1) * 1200 + event_end_min * 60 + event_end_sec',
        'type': 'Calculated'
    },
    'duration': {
        'desc': 'Event duration in seconds',
        'context': 'Seconds between event start and end. Only for duration-based events (shifts, possessions).',
        'calc': 'event_running_end - event_running_start',
        'type': 'Calculated'
    },
    
    # =========================================================================
    # EVENT TYPE COLUMNS - CRITICAL FOR GOAL COUNTING
    # =========================================================================
    'event_type': {
        'desc': 'Primary event type',
        'context': '''Values: Goal, Shot, Pass, Faceoff, Possession, Save, Penalty, Stoppage, ZoneEntry, ZoneExit, Giveaway, Takeaway, Hit, Block, etc.
CRITICAL: Goals are counted where event_type="Goal" AND event_detail="Goal_Scored"''',
        'calc': 'From tracking spreadsheet "Type" column, renamed via rename_standard_columns()',
        'type': 'Explicit'
    },
    'event_type_id': {
        'desc': 'FK to dim_event_type',
        'context': 'Lookup key for dim_event_type attributes. Format: ET_{event_type}.',
        'calc': 'Lookup on event_type in add_all_fkeys.py',
        'type': 'FK'
    },
    'event_detail': {
        'desc': 'Detailed event classification',
        'context': '''CRITICAL DISTINCTIONS:
• Goal_Scored = THE GOAL EVENT (count these for goals)
• Shot_Goal = The shot that resulted in a goal (count as shot, NOT as goal)
• Shot_Miss = Shot that missed the net
• Shot_Blocked = Shot that was blocked
• Shot_Saved = Shot that was saved
• Pass_Complete, Pass_Incomplete = Pass outcomes
• Faceoff_Won, Faceoff_Lost = Faceoff outcomes''',
        'calc': 'From tracking spreadsheet "detail_1" column, normalized',
        'type': 'Explicit'
    },
    'event_detail_id': {
        'desc': 'FK to dim_event_detail',
        'context': 'Links to dim_event_detail for attributes like is_shot_on_goal, is_goal, danger_potential.',
        'calc': 'Lookup on event_detail in add_all_fkeys.py',
        'type': 'FK'
    },
    'event_detail_2': {
        'desc': 'Secondary event detail',
        'context': 'Additional classification. Examples: shot type (Wrist, Slap), pass type, zone entry type (Carry, Dump).',
        'calc': 'From tracking spreadsheet "detail_2" column',
        'type': 'Explicit'
    },
    'event_detail_2_id': {
        'desc': 'FK to dim_event_detail_2',
        'context': 'Lookup for secondary detail attributes.',
        'calc': 'Lookup on event_detail_2 in add_all_fkeys.py',
        'type': 'FK'
    },
    'event_successful': {
        'desc': 'Success indicator',
        'context': 'Values: "Successful", "Failed", null. For passes, shots, zone entries, etc.',
        'calc': 'From tracking spreadsheet "success" column',
        'type': 'Explicit'
    },
    'success_id': {
        'desc': 'FK to dim_success',
        'context': 'Links to dim_success (1=Successful, 0=Failed).',
        'calc': 'Lookup on event_successful in add_all_fkeys.py',
        'type': 'FK'
    },
    
    # =========================================================================
    # ZONE COLUMNS
    # =========================================================================
    'event_team_zone': {
        'desc': 'Zone relative to event team',
        'context': '''Zone where event occurred from perspective of primary event player:
• O (Offensive) = Event team is attacking
• D (Defensive) = Event team is defending
• N (Neutral) = Neutral zone
Example: A shot is always in O zone for shooter, D zone for goalie.''',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'event_zone_id': {
        'desc': 'FK to dim_zone',
        'context': 'Links to dim_zone for zone attributes. Format: Z_{O|D|N}.',
        'calc': 'Lookup on event_team_zone in add_all_fkeys.py',
        'type': 'FK'
    },
    'home_team_zone': {
        'desc': 'Zone from home team perspective',
        'context': 'Always shows zone from home team POV regardless of which team had the event. For coordinate normalization.',
        'calc': 'If player is home: same as event_team_zone. If away: inverted (O↔D).',
        'type': 'Calculated'
    },
    'home_zone_id': {
        'desc': 'FK to dim_zone for home team zone',
        'context': 'Zone ID from home team perspective.',
        'calc': 'Lookup on home_team_zone',
        'type': 'FK'
    },
    'away_team_zone': {
        'desc': 'Zone from away team perspective',
        'context': 'Always shows zone from away team POV. Inverse of home_team_zone.',
        'calc': 'If player is away: same as event_team_zone. If home: inverted.',
        'type': 'Calculated'
    },
    'away_zone_id': {
        'desc': 'FK to dim_zone for away team zone',
        'context': 'Zone ID from away team perspective.',
        'calc': 'Lookup on away_team_zone',
        'type': 'FK'
    },
    
    # =========================================================================
    # PLAYER AND TEAM COLUMNS
    # =========================================================================
    'player_name': {
        'desc': 'Player full name',
        'context': 'Original name from tracking spreadsheet. May have variations - use player_id for consistent matching.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'position_id': {
        'desc': 'FK to dim_position',
        'context': 'Player position from gameroster: C (Center), LW (Left Wing), RW (Right Wing), D (Defense), G (Goalie).',
        'calc': 'Lookup from fact_gameroster based on player_id and game_id',
        'type': 'FK'
    },
    'home_team': {
        'desc': 'Home team code',
        'context': 'Team abbreviation for home team. From tracking spreadsheet, validated against BLB schedule.',
        'calc': 'From tracking, corrected via correct_venue_from_schedule() using BLB as authoritative',
        'type': 'Explicit'
    },
    'home_team_id': {
        'desc': 'FK to dim_team for home team',
        'context': 'Links to dim_team for team attributes (name, logo, division).',
        'calc': 'Lookup on home_team in add_all_fkeys.py',
        'type': 'FK'
    },
    'away_team': {
        'desc': 'Away team code',
        'context': 'Team abbreviation for away team. From tracking spreadsheet, validated against BLB.',
        'calc': 'From tracking, corrected via correct_venue_from_schedule()',
        'type': 'Explicit'
    },
    'away_team_id': {
        'desc': 'FK to dim_team for away team',
        'context': 'Links to dim_team for away team attributes.',
        'calc': 'Lookup on away_team in add_all_fkeys.py',
        'type': 'FK'
    },
    'player_team': {
        'desc': 'Team of the primary event player',
        'context': 'Which team the event_player_1 plays for. Matches either home_team or away_team.',
        'calc': 'Derived from player_id lookup to gameroster, or from team_venue + home/away teams',
        'type': 'Derived'
    },
    'player_team_id': {
        'desc': 'FK to dim_team for player team',
        'context': 'Links to dim_team for the primary player\'s team.',
        'calc': 'Lookup on player_team in add_all_fkeys.py',
        'type': 'FK'
    },
    'team_venue': {
        'desc': 'Venue status of primary player\'s team',
        'context': 'Values: "Home" or "Away". Indicates whether event_player_1 plays for home or away team.',
        'calc': 'If player_team == home_team: "Home", else "Away"',
        'type': 'Calculated'
    },
    'team_venue_id': {
        'desc': 'FK to venue status dimension',
        'context': 'Numeric ID for team_venue. 1=Home, 2=Away.',
        'calc': 'Lookup on team_venue',
        'type': 'FK'
    },
    
    # =========================================================================
    # TIME ON ICE (TOI) COLUMNS - Added by event_time_context.py
    # =========================================================================
    'event_player_1_toi': {
        'desc': 'Time on ice for event_player_1 at event time',
        'context': 'Cumulative TOI in seconds for the primary player (shooter/scorer/passer) when this event occurred.',
        'calc': 'From shift data: sum of shift durations for player up to event time',
        'type': 'Calculated'
    },
    'event_player_2_toi': {
        'desc': 'Time on ice for event_player_2 at event time',
        'context': 'Cumulative TOI for secondary player (assist, receiver) when event occurred.',
        'calc': 'From shift data: sum of shift durations for player up to event time',
        'type': 'Calculated'
    },
    'event_player_3_toi': {
        'desc': 'Time on ice for event_player_3 at event time',
        'context': 'Cumulative TOI for tertiary player (secondary assist) when event occurred.',
        'calc': 'From shift data: sum of shift durations for player up to event time',
        'type': 'Calculated'
    },
    'event_player_4_toi': {
        'desc': 'Time on ice for event_player_4 at event time',
        'context': 'Cumulative TOI for 4th event team player on ice.',
        'calc': 'From shift data',
        'type': 'Calculated'
    },
    'event_player_5_toi': {
        'desc': 'Time on ice for event_player_5 at event time',
        'context': 'Cumulative TOI for 5th event team player on ice.',
        'calc': 'From shift data',
        'type': 'Calculated'
    },
    'event_player_6_toi': {
        'desc': 'Time on ice for event_player_6 at event time',
        'context': 'Cumulative TOI for 6th event team player on ice (extra attacker).',
        'calc': 'From shift data',
        'type': 'Calculated'
    },
    'opp_player_1_toi': {
        'desc': 'Time on ice for opp_player_1 at event time',
        'context': 'Cumulative TOI for primary opposing player (goalie on shot, defender on rush).',
        'calc': 'From shift data: sum of shift durations for player up to event time',
        'type': 'Calculated'
    },
    'opp_player_2_toi': {
        'desc': 'Time on ice for opp_player_2 at event time',
        'context': 'Cumulative TOI for secondary opposing player.',
        'calc': 'From shift data',
        'type': 'Calculated'
    },
    'opp_player_3_toi': {
        'desc': 'Time on ice for opp_player_3 at event time',
        'context': 'Cumulative TOI for 3rd opposing player on ice.',
        'calc': 'From shift data',
        'type': 'Calculated'
    },
    'opp_player_4_toi': {
        'desc': 'Time on ice for opp_player_4 at event time',
        'context': 'Cumulative TOI for 4th opposing player on ice.',
        'calc': 'From shift data',
        'type': 'Calculated'
    },
    'opp_player_5_toi': {
        'desc': 'Time on ice for opp_player_5 at event time',
        'context': 'Cumulative TOI for 5th opposing player on ice.',
        'calc': 'From shift data',
        'type': 'Calculated'
    },
    'opp_player_6_toi': {
        'desc': 'Time on ice for opp_player_6 at event time',
        'context': 'Cumulative TOI for 6th opposing player on ice.',
        'calc': 'From shift data',
        'type': 'Calculated'
    },
    'player_toi': {
        'desc': 'Time on ice for primary player at event time',
        'context': 'Same as event_player_1_toi. Cumulative TOI for primary player when event occurred.',
        'calc': 'From shift data',
        'type': 'Calculated'
    },
    'team_on_ice_toi_avg': {
        'desc': 'Average TOI of event team players on ice',
        'context': 'Average cumulative TOI across all event team players on ice at event time. Indicates line freshness.',
        'calc': 'AVG(event_player_1_toi, event_player_2_toi, ...)',
        'type': 'Calculated'
    },
    'team_on_ice_toi_min': {
        'desc': 'Minimum TOI among event team players on ice',
        'context': 'Lowest cumulative TOI among event team players. Indicates freshest player on ice.',
        'calc': 'MIN(event_player_1_toi, event_player_2_toi, ...)',
        'type': 'Calculated'
    },
    'team_on_ice_toi_max': {
        'desc': 'Maximum TOI among event team players on ice',
        'context': 'Highest cumulative TOI among event team players. Indicates most tired player on ice.',
        'calc': 'MAX(event_player_1_toi, event_player_2_toi, ...)',
        'type': 'Calculated'
    },
    'opp_on_ice_toi_avg': {
        'desc': 'Average TOI of opposing team players on ice',
        'context': 'Average cumulative TOI across all opposing players on ice. Indicates opponent line freshness.',
        'calc': 'AVG(opp_player_1_toi, opp_player_2_toi, ...)',
        'type': 'Calculated'
    },
    'opp_on_ice_toi_min': {
        'desc': 'Minimum TOI among opposing team players on ice',
        'context': 'Lowest cumulative TOI among opposing players.',
        'calc': 'MIN(opp_player_1_toi, opp_player_2_toi, ...)',
        'type': 'Calculated'
    },
    'opp_on_ice_toi_max': {
        'desc': 'Maximum TOI among opposing team players on ice',
        'context': 'Highest cumulative TOI among opposing players.',
        'calc': 'MAX(opp_player_1_toi, opp_player_2_toi, ...)',
        'type': 'Calculated'
    },
    
    # =========================================================================
    # SHIFT TABLE COLUMNS
    # =========================================================================
    'shift_id': {
        'desc': 'Unique shift identifier (PK)',
        'context': 'Format: SH{game_id}{shift_index:05d}. Example: SH1896900001. One shift_id per line change.',
        'calc': 'format_key("SH", game_id, shift_index) in key_utils.py:84',
        'type': 'Derived'
    },
    'shift_index': {
        'desc': 'Sequential shift number within game',
        'context': 'Increments with each line change. Used to generate shift_id.',
        'calc': 'From tracking spreadsheet shifts sheet',
        'type': 'Explicit'
    },
    'shift_start_min': {
        'desc': 'Shift start minute within period',
        'context': 'When players came onto ice. Minutes 0-20.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'shift_start_sec': {
        'desc': 'Shift start second within minute',
        'context': 'Seconds 0-59.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'shift_end_min': {
        'desc': 'Shift end minute within period',
        'context': 'When players left ice.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'shift_end_sec': {
        'desc': 'Shift end second within minute',
        'context': 'Seconds 0-59.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'shift_start_total_seconds': {
        'desc': 'Running time at shift start',
        'context': 'Total seconds from game start when shift began.',
        'calc': '(period-1) * 1200 + shift_start_min * 60 + shift_start_sec',
        'type': 'Calculated'
    },
    'shift_end_total_seconds': {
        'desc': 'Running time at shift end',
        'context': 'Total seconds from game start when shift ended.',
        'calc': '(period-1) * 1200 + shift_end_min * 60 + shift_end_sec',
        'type': 'Calculated'
    },
    'shift_duration': {
        'desc': 'Shift length in seconds',
        'context': 'How long this unit was on ice. Normal shifts ~45-60 seconds.',
        'calc': 'shift_end_total_seconds - shift_start_total_seconds',
        'type': 'Calculated'
    },
    'shift_start_type': {
        'desc': 'How shift began',
        'context': 'Values: "Stoppage" (after whistle), "On_the_fly" (line change during play).',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'shift_stop_type': {
        'desc': 'How shift ended',
        'context': 'Values: "Stoppage", "On_the_fly", "Period_End", "Game_End".',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'home_forward_1': {
        'desc': 'Home team forward 1 jersey number',
        'context': 'Jersey number of first forward. Use with gameroster to get player_id.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'home_forward_2': {
        'desc': 'Home team forward 2 jersey number',
        'context': 'Jersey number of second forward.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'home_forward_3': {
        'desc': 'Home team forward 3 jersey number',
        'context': 'Jersey number of third forward.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'home_defense_1': {
        'desc': 'Home team defenseman 1 jersey number',
        'context': 'Jersey number of first defenseman.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'home_defense_2': {
        'desc': 'Home team defenseman 2 jersey number',
        'context': 'Jersey number of second defenseman.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'home_xtra': {
        'desc': 'Home team extra attacker jersey number',
        'context': 'Only populated when pulling goalie for extra attacker.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'home_goalie': {
        'desc': 'Home team goalie jersey number',
        'context': 'Null if goalie pulled.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'away_forward_1': {
        'desc': 'Away team forward 1 jersey number',
        'context': 'Jersey number of first away forward.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'away_forward_2': {
        'desc': 'Away team forward 2 jersey number',
        'context': 'Jersey number of second away forward.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'away_forward_3': {
        'desc': 'Away team forward 3 jersey number',
        'context': 'Jersey number of third away forward.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'away_defense_1': {
        'desc': 'Away team defenseman 1 jersey number',
        'context': 'Jersey number of first away defenseman.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'away_defense_2': {
        'desc': 'Away team defenseman 2 jersey number',
        'context': 'Jersey number of second away defenseman.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'away_xtra': {
        'desc': 'Away team extra attacker jersey number',
        'context': 'Only populated when pulling goalie.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'away_goalie': {
        'desc': 'Away team goalie jersey number',
        'context': 'Null if goalie pulled.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'home_team_strength': {
        'desc': 'Number of home skaters on ice',
        'context': 'Count of home skaters (not including goalie). 5=full strength, 4=PK, 6=extra attacker.',
        'calc': 'COUNT(home_forward_1..3, home_defense_1..2, home_xtra if not null)',
        'type': 'Calculated'
    },
    'away_team_strength': {
        'desc': 'Number of away skaters on ice',
        'context': 'Count of away skaters.',
        'calc': 'COUNT(away_forward_1..3, away_defense_1..2, away_xtra if not null)',
        'type': 'Calculated'
    },
    'home_team_en': {
        'desc': 'Home team empty net indicator',
        'context': '1 if home goalie pulled (empty net).',
        'calc': 'home_goalie IS NULL',
        'type': 'Calculated'
    },
    'away_team_en': {
        'desc': 'Away team empty net indicator',
        'context': '1 if away goalie pulled.',
        'calc': 'away_goalie IS NULL',
        'type': 'Calculated'
    },
    'home_team_pp': {
        'desc': 'Home team power play indicator',
        'context': '1 if home team has more skaters (power play).',
        'calc': 'home_team_strength > away_team_strength',
        'type': 'Calculated'
    },
    'home_team_pk': {
        'desc': 'Home team penalty kill indicator',
        'context': '1 if home team has fewer skaters (penalty kill).',
        'calc': 'home_team_strength < away_team_strength',
        'type': 'Calculated'
    },
    'away_team_pp': {
        'desc': 'Away team power play indicator',
        'context': '1 if away team has more skaters.',
        'calc': 'away_team_strength > home_team_strength',
        'type': 'Calculated'
    },
    'away_team_pk': {
        'desc': 'Away team penalty kill indicator',
        'context': '1 if away team has fewer skaters.',
        'calc': 'away_team_strength < home_team_strength',
        'type': 'Calculated'
    },
    'situation': {
        'desc': 'Game situation description',
        'context': 'Text description: "5v5", "5v4", "4v5", "5v3", "4v4", "3v3", "6v5", etc.',
        'calc': 'f"{home_team_strength}v{away_team_strength}"',
        'type': 'Calculated'
    },
    'strength': {
        'desc': 'Strength situation code',
        'context': 'Similar to situation. Used for FK lookup.',
        'calc': 'From situation',
        'type': 'Calculated'
    },
    'home_goals': {
        'desc': 'Home team goals at shift start',
        'context': 'Running score for home team when shift began.',
        'calc': 'Cumulative count of home goals up to shift_start_total_seconds',
        'type': 'Calculated'
    },
    'away_goals': {
        'desc': 'Away team goals at shift start',
        'context': 'Running score for away team when shift began.',
        'calc': 'Cumulative count of away goals up to shift_start_total_seconds',
        'type': 'Calculated'
    },
    'home_team_plus': {
        'desc': 'Goals for home during shift',
        'context': 'Number of goals scored by home team during this shift.',
        'calc': 'COUNT goals where is_goal=1 AND player_team=home_team AND within shift time',
        'type': 'Calculated'
    },
    'home_team_minus': {
        'desc': 'Goals against home during shift',
        'context': 'Number of goals scored against home team during this shift.',
        'calc': 'COUNT goals where is_goal=1 AND player_team=away_team AND within shift time',
        'type': 'Calculated'
    },
    
    # =========================================================================
    # TRACKING-SPECIFIC COLUMNS
    # =========================================================================
    'event_player_key': {
        'desc': 'Unique player-event combination key',
        'context': 'Format: EP{game_id}{event_index:05d}_{player_role}. One row per player per event.',
        'calc': 'event_id + "_" + player_role',
        'type': 'Derived'
    },
    'event_index': {
        'desc': 'Sequential event number within game',
        'context': 'Numeric index used to generate event_id. Increments per event.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'zone_change_key': {
        'desc': 'Zone change identifier',
        'context': 'Format: ZC{game_id}{zone_change_index:05d}. Links zone entry/exit events.',
        'calc': 'format_key("ZC", game_id, zone_change_index)',
        'type': 'Derived'
    },
    'event_success_id': {
        'desc': 'FK to dim_success (alternate name)',
        'context': 'Same as success_id. Links to dim_success.',
        'calc': 'Lookup on event_successful',
        'type': 'FK'
    },
    'play_detail_id': {
        'desc': 'FK to dim_play_detail',
        'context': 'Links to dim_play_detail for standardized play characteristics.',
        'calc': 'Lookup on play_detail1',
        'type': 'FK'
    },
    'play_detail_2_id': {
        'desc': 'FK to dim_play_detail_2',
        'context': 'Links to dim_play_detail_2 for secondary play characteristics.',
        'calc': 'Lookup on play_detail_2',
        'type': 'FK'
    },
    'play_detail_2': {
        'desc': 'Secondary play detail string',
        'context': 'Additional play characteristics. Same format as play_detail1.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'play_success_id': {
        'desc': 'FK to dim_success for play outcome',
        'context': 'Success status of the overall play.',
        'calc': 'Lookup on play_detail_successful',
        'type': 'FK'
    },
    'play_detail_successful': {
        'desc': 'Play success indicator',
        'context': 'Values: "Successful", "Failed". Whether the play achieved its objective.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'side_of_puck': {
        'desc': 'Player position relative to puck',
        'context': 'Values: "Strong", "Weak", "Front", "Behind". Positional context.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'player_role_id': {
        'desc': 'FK to dim_player_role',
        'context': 'Links to dim_player_role for role attributes.',
        'calc': 'Lookup on player_role in add_all_fkeys.py',
        'type': 'FK'
    },
    
    # =========================================================================
    # ZONE TIME COLUMNS (from shifts)
    # =========================================================================
    'home_ozone_start': {
        'desc': 'Home offensive zone time at shift start',
        'context': 'Cumulative seconds home team spent in offensive zone before this shift.',
        'calc': 'Running sum of OZ time',
        'type': 'Calculated'
    },
    'home_ozone_end': {
        'desc': 'Home offensive zone time at shift end',
        'context': 'Cumulative OZ time after shift.',
        'calc': 'home_ozone_start + OZ time during shift',
        'type': 'Calculated'
    },
    'home_dzone_start': {
        'desc': 'Home defensive zone time at shift start',
        'context': 'Cumulative seconds home team spent in defensive zone.',
        'calc': 'Running sum of DZ time',
        'type': 'Calculated'
    },
    'home_dzone_end': {
        'desc': 'Home defensive zone time at shift end',
        'context': 'Cumulative DZ time after shift.',
        'calc': 'home_dzone_start + DZ time during shift',
        'type': 'Calculated'
    },
    'home_nzone_start': {
        'desc': 'Home neutral zone time at shift start',
        'context': 'Cumulative seconds home team spent in neutral zone.',
        'calc': 'Running sum of NZ time',
        'type': 'Calculated'
    },
    'home_nzone_end': {
        'desc': 'Home neutral zone time at shift end',
        'context': 'Cumulative NZ time after shift.',
        'calc': 'home_nzone_start + NZ time during shift',
        'type': 'Calculated'
    },
    'stoppage_time': {
        'desc': 'Time in stoppage during shift',
        'context': 'Seconds of play stoppage (icing, offside, etc.) during this shift.',
        'calc': 'Sum of stoppage event durations within shift',
        'type': 'Calculated'
    },
    
    # =========================================================================
    # DIMENSION TABLE COLUMNS - dim_player
    # =========================================================================
    'player_first_name': {
        'desc': 'Player first name',
        'context': 'Legal first name from BLB registration.',
        'calc': 'From BLB_Tables.xlsx Player sheet',
        'type': 'Explicit'
    },
    'player_last_name': {
        'desc': 'Player last name',
        'context': 'Legal last name from BLB registration.',
        'calc': 'From BLB_Tables.xlsx Player sheet',
        'type': 'Explicit'
    },
    'player_full_name': {
        'desc': 'Player full name',
        'context': 'Concatenation of first and last name.',
        'calc': 'player_first_name + " " + player_last_name',
        'type': 'Derived'
    },
    'player_primary_position': {
        'desc': 'Primary playing position',
        'context': 'Values: C (Center), LW (Left Wing), RW (Right Wing), D (Defense), G (Goalie).',
        'calc': 'From BLB_Tables.xlsx Player sheet',
        'type': 'Explicit'
    },
    'current_skill_rating': {
        'desc': 'Current skill rating (1-10)',
        'context': 'BLB skill rating. 1=beginner, 10=expert. Used for competition tier.',
        'calc': 'From BLB_Tables.xlsx Player sheet',
        'type': 'Explicit'
    },
    'player_hand': {
        'desc': 'Shooting hand',
        'context': 'Values: L (Left), R (Right).',
        'calc': 'From BLB_Tables.xlsx Player sheet',
        'type': 'Explicit'
    },
    'birth_year': {
        'desc': 'Player birth year',
        'context': 'Four-digit year. Used for age calculations.',
        'calc': 'From BLB_Tables.xlsx Player sheet',
        'type': 'Explicit'
    },
    'player_gender': {
        'desc': 'Player gender',
        'context': 'Values: M (Male), F (Female).',
        'calc': 'From BLB_Tables.xlsx Player sheet',
        'type': 'Explicit'
    },
    'highest_beer_league': {
        'desc': 'Highest league level played',
        'context': 'Historical highest league tier.',
        'calc': 'From BLB_Tables.xlsx Player sheet',
        'type': 'Explicit'
    },
    'player_rating_ly': {
        'desc': 'Player rating last year',
        'context': 'Previous season skill rating for comparison.',
        'calc': 'From BLB_Tables.xlsx Player sheet',
        'type': 'Explicit'
    },
    'player_notes': {
        'desc': 'Admin notes about player',
        'context': 'Free-text notes from BLB admin.',
        'calc': 'From BLB_Tables.xlsx Player sheet',
        'type': 'Explicit'
    },
    'player_leadership': {
        'desc': 'Leadership role',
        'context': 'Values: C (Captain), A (Alternate), blank.',
        'calc': 'From BLB_Tables.xlsx Player sheet',
        'type': 'Explicit'
    },
    'player_norad': {
        'desc': 'NORAD league URL identifier',
        'context': 'Player ID on noradhockey.com website.',
        'calc': 'From BLB_Tables.xlsx Player sheet',
        'type': 'Explicit'
    },
    'player_url': {
        'desc': 'Full URL to player profile',
        'context': 'Direct link to noradhockey.com player page.',
        'calc': '"https://www.noradhockey.com/player/" + player_norad',
        'type': 'Derived'
    },
    'random_player_first_name': {
        'desc': 'Anonymized first name',
        'context': 'Random name for privacy protection in public displays.',
        'calc': 'Random selection from name list',
        'type': 'Derived'
    },
    'random_player_last_name': {
        'desc': 'Anonymized last name',
        'context': 'Random name for privacy protection.',
        'calc': 'Random selection from name list',
        'type': 'Derived'
    },
    'random_player_full_name': {
        'desc': 'Anonymized full name',
        'context': 'Concatenation of random first and last names.',
        'calc': 'random_player_first_name + " " + random_player_last_name',
        'type': 'Derived'
    },
    
    # =========================================================================
    # DIMENSION TABLE COLUMNS - dim_team
    # =========================================================================
    'team_name': {
        'desc': 'Full team name',
        'context': 'Official team name (e.g., "Blue Blazers").',
        'calc': 'From BLB_Tables.xlsx Team sheet',
        'type': 'Explicit'
    },
    'team_short_name': {
        'desc': 'Short team name',
        'context': 'Abbreviated name for display.',
        'calc': 'From BLB_Tables.xlsx Team sheet',
        'type': 'Explicit'
    },
    'team_code': {
        'desc': 'Team abbreviation code',
        'context': '3-4 letter code used in tracking data.',
        'calc': 'From BLB_Tables.xlsx Team sheet',
        'type': 'Explicit'
    },
    'team_division': {
        'desc': 'Team division',
        'context': 'Division assignment (e.g., "A", "B", "C").',
        'calc': 'From BLB_Tables.xlsx Team sheet',
        'type': 'Explicit'
    },
    
    # =========================================================================
    # GAMEROSTER COLUMNS
    # =========================================================================
    'jersey_number': {
        'desc': 'Player jersey number for game',
        'context': 'Number worn by player in this specific game.',
        'calc': 'From roster.json in game folder',
        'type': 'Explicit'
    },
    'roster_position': {
        'desc': 'Position on game roster',
        'context': 'Position assigned for this game: F, D, G.',
        'calc': 'From roster.json',
        'type': 'Explicit'
    },
    'starting_lineup': {
        'desc': 'Starting lineup indicator',
        'context': '1 if player started the game.',
        'calc': 'From roster.json',
        'type': 'Explicit'
    },
    'scratched': {
        'desc': 'Scratch indicator',
        'context': '1 if player was on roster but did not play.',
        'calc': 'From roster.json',
        'type': 'Explicit'
    },
    
    # =========================================================================
    # QA TABLE COLUMNS
    # =========================================================================
    'expected_home_goals': {
        'desc': 'Expected home goals from noradhockey.com',
        'context': 'Official game result home score for validation.',
        'calc': 'Scraped from noradhockey.com game page',
        'type': 'Explicit'
    },
    'expected_away_goals': {
        'desc': 'Expected away goals from noradhockey.com',
        'context': 'Official game result away score for validation.',
        'calc': 'Scraped from noradhockey.com game page',
        'type': 'Explicit'
    },
    'actual_home_goals': {
        'desc': 'Home goals counted by ETL',
        'context': 'Goals counted from tracking data for home team.',
        'calc': 'COUNT where is_goal=1 AND player_team=home_team',
        'type': 'Calculated'
    },
    'actual_away_goals': {
        'desc': 'Away goals counted by ETL',
        'context': 'Goals counted from tracking data for away team.',
        'calc': 'COUNT where is_goal=1 AND player_team=away_team',
        'type': 'Calculated'
    },
    'home_goal_match': {
        'desc': 'Home goals match indicator',
        'context': '1 if actual_home_goals == expected_home_goals.',
        'calc': 'actual_home_goals == expected_home_goals',
        'type': 'Calculated'
    },
    'away_goal_match': {
        'desc': 'Away goals match indicator',
        'context': '1 if actual_away_goals == expected_away_goals.',
        'calc': 'actual_away_goals == expected_away_goals',
        'type': 'Calculated'
    },
    'verification_status': {
        'desc': 'Overall verification status',
        'context': 'Values: "PASS", "FAIL". PASS if both home and away match.',
        'calc': 'IF home_goal_match AND away_goal_match THEN "PASS" ELSE "FAIL"',
        'type': 'Calculated'
    },
    
    # =========================================================================
    # COMPOSITE KEY COLUMNS
    # =========================================================================
    'sequence_key': {
        'desc': 'Sequence identifier',
        'context': 'Format: SQ{game_id}{sequence_index:05d}. Groups consecutive events into sequences. New sequence starts on possession change or stoppage.',
        'calc': 'generate_sequence_key() in key_utils.py:99 - format_key("SQ", game_id, sequence_index)',
        'type': 'Derived'
    },
    'play_key': {
        'desc': 'Play identifier',
        'context': 'Format: PL{game_id}{play_index:05d}. Groups events into offensive/defensive plays. Subset of sequence.',
        'calc': 'generate_play_key() in key_utils.py:104 - format_key("PL", game_id, play_index)',
        'type': 'Derived'
    },
    'event_chain_key': {
        'desc': 'Event chain identifier',
        'context': 'Links causally related events. Example: shot → save → rebound shot → goal all share same chain.',
        'calc': 'generate_event_chain_key() in base_etl.py based on linked events and time proximity',
        'type': 'Derived'
    },
    'shift_key': {
        'desc': 'Shift identifier',
        'context': 'Format: SH{game_id}{shift_index:05d}. Links event to the shift it occurred during. FK to fact_shifts.',
        'calc': 'generate_shift_key() in key_utils.py:109',
        'type': 'Derived'
    },
    'linked_event_key': {
        'desc': 'Link to causally related event',
        'context': 'Format: LV{game_id}{linked_event_index:05d}. Points to specific related event (e.g., goal links to its shot).',
        'calc': 'generate_linked_event_key() in key_utils.py:94',
        'type': 'Derived'
    },
    'scoring_chance_key': {
        'desc': 'Scoring chance identifier',
        'context': 'Groups events that constitute a single scoring chance. Multiple shots in quick succession = one chance.',
        'calc': 'Generated for is_scoring_chance=1 events based on time/location proximity',
        'type': 'Derived'
    },
    'cycle_key': {
        'desc': 'Offensive zone cycle identifier',
        'context': 'Groups events during sustained offensive zone pressure (cycling the puck).',
        'calc': 'Generated for is_cycle=1 events',
        'type': 'Derived'
    },
    
    # =========================================================================
    # BOOLEAN FLAGS - CALCULATED FROM EVENT DATA
    # =========================================================================
    'is_rush': {
        'desc': 'Rush indicator (odd-man or fast break)',
        'context': '1 if event is part of a rush attack. Rushes are fast breaks with numerical advantage.',
        'calc': 'play_detail contains "Rush" OR event tagged as rush in tracking',
        'type': 'Calculated'
    },
    'is_rebound': {
        'desc': 'Rebound shot indicator',
        'context': '1 if shot is a rebound from previous save. High danger opportunity.',
        'calc': 'play_detail contains "Rebound" OR shot within 3 seconds of previous save',
        'type': 'Calculated'
    },
    'is_breakout': {
        'desc': 'Breakout play indicator',
        'context': '1 if event starts a breakout from defensive zone.',
        'calc': 'play_detail contains "Breakout" OR first event after DZ possession',
        'type': 'Calculated'
    },
    'is_zone_entry': {
        'desc': 'Zone entry indicator',
        'context': '1 if event is an offensive zone entry (crossing blue line).',
        'calc': 'event_type == "ZoneEntry"',
        'type': 'Calculated'
    },
    'is_zone_exit': {
        'desc': 'Zone exit indicator',
        'context': '1 if event is a defensive zone exit.',
        'calc': 'event_type == "ZoneExit"',
        'type': 'Calculated'
    },
    'is_shot': {
        'desc': 'Shot indicator (any type)',
        'context': '1 if event is any shot type (goal, save, miss, block).',
        'calc': 'event_type == "Shot" OR event_detail in (Shot_Goal, Shot_Saved, Shot_Miss, Shot_Blocked)',
        'type': 'Calculated'
    },
    'is_goal': {
        'desc': 'Goal indicator',
        'context': '''⚠️ CRITICAL: 1 ONLY for actual goals.
Formula: event_type=="Goal" AND event_detail=="Goal_Scored" AND player_role=="event_player_1"
Shot_Goal is the SHOT, not the goal. Only the scorer (event_player_1) gets is_goal=1.''',
        'calc': '(event_type == "Goal") & (event_detail == "Goal_Scored") & (player_role == "event_player_1") in base_etl.py:657',
        'type': 'Calculated'
    },
    'is_save': {
        'desc': 'Save indicator',
        'context': '1 if goalie made a save on this event.',
        'calc': 'event_type == "Save" OR (player_role == "opp_goalie" AND is_shot == 1)',
        'type': 'Calculated'
    },
    'is_turnover': {
        'desc': 'Turnover indicator',
        'context': '1 if possession changed teams via giveaway or takeaway.',
        'calc': 'is_giveaway == 1 OR is_takeaway == 1',
        'type': 'Calculated'
    },
    'is_giveaway': {
        'desc': 'Giveaway indicator',
        'context': '1 if team lost possession through error (bad pass, lost handle).',
        'calc': 'event_type == "Giveaway"',
        'type': 'Calculated'
    },
    'is_takeaway': {
        'desc': 'Takeaway indicator',
        'context': '1 if team gained possession through defensive effort.',
        'calc': 'event_type == "Takeaway"',
        'type': 'Calculated'
    },
    'is_faceoff': {
        'desc': 'Faceoff indicator',
        'context': '1 if event is a faceoff.',
        'calc': 'event_type == "Faceoff"',
        'type': 'Calculated'
    },
    'is_penalty': {
        'desc': 'Penalty indicator',
        'context': '1 if a penalty was called.',
        'calc': 'event_type == "Penalty"',
        'type': 'Calculated'
    },
    'is_blocked_shot': {
        'desc': 'Blocked shot indicator',
        'context': '1 if shot was blocked by a defender (not goalie).',
        'calc': 'event_detail contains "Blocked" OR event_detail == "Shot_Blocked"',
        'type': 'Calculated'
    },
    'is_missed_shot': {
        'desc': 'Missed shot indicator',
        'context': '1 if shot missed the net entirely.',
        'calc': 'event_detail == "Shot_Miss"',
        'type': 'Calculated'
    },
    'is_deflected': {
        'desc': 'Deflection indicator',
        'context': '1 if shot was deflected (tip-in attempt).',
        'calc': 'event_detail contains "Deflect" OR play_detail contains "Deflect"',
        'type': 'Calculated'
    },
    'is_sog': {
        'desc': 'Shot on goal indicator',
        'context': '1 if shot reached the goalie (saved or goal). Excludes blocks and misses.',
        'calc': 'is_shot == 1 AND is_blocked_shot == 0 AND is_missed_shot == 0',
        'type': 'Calculated'
    },
    'is_cycle': {
        'desc': 'Cycle play indicator',
        'context': '1 if event is part of offensive zone cycle (sustained possession in OZ).',
        'calc': 'cycle_key IS NOT NULL OR play_detail contains "Cycle"',
        'type': 'Calculated'
    },
    'is_scoring_chance': {
        'desc': 'Scoring chance indicator',
        'context': '1 if event is a quality scoring opportunity. Based on location, shot type, preceding events.',
        'calc': 'danger_level IS NOT NULL OR shot from slot/crease area',
        'type': 'Calculated'
    },
    'is_high_danger': {
        'desc': 'High danger chance indicator',
        'context': '1 if scoring chance is high danger (slot, rebound, rush, 2-on-1, etc.).',
        'calc': 'danger_level == "High" OR xG > threshold',
        'type': 'Calculated'
    },
    'is_pressured': {
        'desc': 'Pressure indicator',
        'context': '1 if player was under pressure when making play.',
        'calc': 'pressured_pressurer IS NOT NULL OR play_detail contains "Pressured"',
        'type': 'Calculated'
    },
    
    # =========================================================================
    # OUTCOME FK COLUMNS
    # =========================================================================
    'shot_outcome_id': {
        'desc': 'FK to dim_shot_outcome',
        'context': 'Shot result classification: Goal, Save, Block, Miss, Deflected. Only populated for shot events.',
        'calc': 'Lookup based on event_detail and is_goal/is_save/is_blocked',
        'type': 'FK'
    },
    'pass_outcome_id': {
        'desc': 'FK to dim_pass_outcome',
        'context': 'Pass result: Complete, Incomplete, Intercepted. Only populated for pass events.',
        'calc': 'Lookup based on event_successful and event_detail',
        'type': 'FK'
    },
    'save_outcome_id': {
        'desc': 'FK to dim_save_outcome',
        'context': 'Save result: Controlled (freeze), Rebound, Deflected Away. Only populated for saves.',
        'calc': 'Lookup based on save characteristics',
        'type': 'FK'
    },
    'zone_outcome_id': {
        'desc': 'FK to dim_zone_outcome',
        'context': 'Zone entry result: Maintained (kept possession), Lost (turnover), Shot (got shot off).',
        'calc': 'Lookup based on events following zone entry',
        'type': 'FK'
    },
    'zone_entry_type_id': {
        'desc': 'FK to dim_zone_entry_type',
        'context': 'Zone entry method: Carry (controlled), Dump (chip in), Pass (pass to teammate). Links to dim_zone_entry_type.',
        'calc': 'Lookup on event_detail_2 for zone entries',
        'type': 'FK'
    },
    'zone_exit_type_id': {
        'desc': 'FK to dim_zone_exit_type',
        'context': 'Zone exit method: Carry, Pass, Clear (dump out), Chip. Links to dim_zone_exit_type.',
        'calc': 'Lookup on event_detail_2 for zone exits',
        'type': 'FK'
    },
    'stoppage_type_id': {
        'desc': 'FK to dim_stoppage_type',
        'context': 'Stoppage cause: Icing, Offside, Puck_Out_Of_Play, Penalty, etc.',
        'calc': 'Lookup on event_detail for stoppages',
        'type': 'FK'
    },
    'giveaway_type_id': {
        'desc': 'FK to dim_giveaway_type',
        'context': 'Giveaway cause: Bad_Pass, Lost_Puck, Turnover, Failed_Clear, etc.',
        'calc': 'Lookup on event_detail for giveaways',
        'type': 'FK'
    },
    'takeaway_type_id': {
        'desc': 'FK to dim_takeaway_type',
        'context': 'Takeaway method: Stick_Check, Interception, Forced_Error, etc.',
        'calc': 'Lookup on event_detail for takeaways',
        'type': 'FK'
    },
    'turnover_type_id': {
        'desc': 'FK to dim_turnover_type',
        'context': 'Combined giveaway/takeaway classification. Links to dim_turnover_type.',
        'calc': 'Lookup combining giveaway and takeaway types',
        'type': 'FK'
    },
    'pass_type_id': {
        'desc': 'FK to dim_pass_type',
        'context': 'Pass type: Direct (tape-to-tape), Saucer, Bank, Backhand, etc.',
        'calc': 'Lookup on event_detail_2 for passes',
        'type': 'FK'
    },
    'shot_type_id': {
        'desc': 'FK to dim_shot_type',
        'context': 'Shot type: Wrist, Slap, Snap, Backhand, Tip, One_Timer.',
        'calc': 'Lookup on event_detail_2 for shots',
        'type': 'FK'
    },
    
    # =========================================================================
    # CONTEXT FK COLUMNS
    # =========================================================================
    'time_bucket_id': {
        'desc': 'FK to dim_time_bucket',
        'context': 'Minute bucket within period for time-based analysis. Buckets: 0-4, 5-9, 10-14, 15-20.',
        'calc': 'floor(event_start_min / 5) mapped to dim_time_bucket',
        'type': 'FK'
    },
    'strength_id': {
        'desc': 'FK to dim_strength (situation)',
        'context': 'Game situation when event occurred: 5v5 (even), 5v4 (PP), 4v5 (PK), 5v3, 4v4, 3v3, etc.',
        'calc': 'From shift data - count of players on ice for each team',
        'type': 'FK'
    },
    'danger_level': {
        'desc': 'Danger level text',
        'context': 'Scoring chance danger: Low, Medium, High. Based on shot location, type, preceding events.',
        'calc': 'Calculated from xG model or location rules',
        'type': 'Calculated'
    },
    'danger_level_id': {
        'desc': 'FK to dim_danger_level',
        'context': 'Links to dim_danger_level for xG multipliers and attributes.',
        'calc': 'Lookup on danger_level',
        'type': 'FK'
    },
    'game_state_id': {
        'desc': 'FK to dim_game_state',
        'context': 'Score situation: Tied, Leading_1, Leading_2, Leading_3+, Trailing_1, Trailing_2, Trailing_3+.',
        'calc': 'Based on running score at event time',
        'type': 'FK'
    },
    'competition_tier_id': {
        'desc': 'FK to dim_competition_tier',
        'context': 'Skill level context based on player ratings involved in event.',
        'calc': 'Based on average player ratings in event',
        'type': 'FK'
    },
    'turnover_quality_id': {
        'desc': 'FK to dim_turnover_quality',
        'context': 'Turnover quality: Forced (defensive play), Unforced (error).',
        'calc': 'Lookup based on takeaway presence',
        'type': 'FK'
    },
    
    # =========================================================================
    # TIME CONTEXT COLUMNS (Event Spacing)
    # =========================================================================
    'time_to_next_event': {
        'desc': 'Seconds until next event',
        'context': 'Time gap to following event. Useful for pace analysis.',
        'calc': 'next_row.event_running_start - this_row.event_running_end',
        'type': 'Calculated'
    },
    'time_from_last_event': {
        'desc': 'Seconds since last event',
        'context': 'Time gap from previous event.',
        'calc': 'this_row.event_running_start - prev_row.event_running_end',
        'type': 'Calculated'
    },
    'time_to_next_goal_for': {
        'desc': 'Seconds until next goal for team',
        'context': 'Time until this player\'s team scores again. NULL if no more goals.',
        'calc': 'Window function: next goal by player_team after this event',
        'type': 'Calculated'
    },
    'time_to_next_goal_against': {
        'desc': 'Seconds until next goal against',
        'context': 'Time until opponent scores. NULL if no more goals against.',
        'calc': 'Window function: next goal by opponent after this event',
        'type': 'Calculated'
    },
    'time_from_last_goal_for': {
        'desc': 'Seconds since last goal for team',
        'context': 'Time since this player\'s team last scored. NULL if first goal.',
        'calc': 'Window function: time since prev goal by player_team',
        'type': 'Calculated'
    },
    'time_from_last_goal_against': {
        'desc': 'Seconds since last goal against',
        'context': 'Time since opponent last scored.',
        'calc': 'Window function: time since prev goal by opponent',
        'type': 'Calculated'
    },
    'time_to_next_stoppage': {
        'desc': 'Seconds until next stoppage',
        'context': 'Time until play stops (whistle). Useful for sustained pressure analysis.',
        'calc': 'Window function: time to next is_stoppage=1 event',
        'type': 'Calculated'
    },
    'time_from_last_stoppage': {
        'desc': 'Seconds since last stoppage',
        'context': 'Time since last whistle. Long time = sustained play.',
        'calc': 'Window function: time from prev is_stoppage=1 event',
        'type': 'Calculated'
    },
    
    # =========================================================================
    # PLAY DETAIL COLUMNS
    # =========================================================================
    'play_detail1': {
        'desc': 'Primary play detail string',
        'context': '''Describes play characteristics. Common values:
• Rush, Rush_2on1, Rush_3on2 = Odd-man rush
• Rebound = Shot off rebound
• Cycle = Cycling play
• Breakout = Starting breakout
• Pressured = Under defensive pressure
• Screen = Goalie screened
Can contain pipe-separated multiple values.''',
        'calc': 'From tracking spreadsheet, standardized via standardize_play_details()',
        'type': 'Explicit'
    },
    'play_detail2': {
        'desc': 'Secondary play detail string',
        'context': 'Additional play characteristics. Same format as play_detail1.',
        'calc': 'From tracking spreadsheet',
        'type': 'Explicit'
    },
    'pressured_pressurer': {
        'desc': 'Player ID applying pressure',
        'context': 'When is_pressured=1, this contains the opponent player_id who applied pressure.',
        'calc': 'From tracking spreadsheet, linked to player_id',
        'type': 'Explicit'
    },
}

def get_column_info(col_name):
    """Get column metadata, with defaults for unknown columns."""
    if col_name in COLUMN_META:
        return COLUMN_META[col_name]
    
    # Generate defaults based on naming patterns
    info = {'desc': col_name.replace('_', ' ').title(), 'context': '', 'calc': '', 'type': 'Unknown'}
    
    if col_name.endswith('_id'):
        base = col_name[:-3]
        info['desc'] = f'FK to dim_{base}'
        info['type'] = 'FK'
        info['calc'] = 'Lookup'
    elif col_name.startswith('is_'):
        info['desc'] = f'{col_name[3:].replace("_", " ").title()} indicator'
        info['type'] = 'Calculated'
        info['calc'] = 'Boolean flag'
    elif col_name.endswith('_key'):
        info['desc'] = f'{col_name[:-4].replace("_", " ").title()} key'
        info['type'] = 'Derived'
    elif col_name.startswith('time_'):
        info['desc'] = col_name.replace('_', ' ').title()
        info['type'] = 'Calculated'
        info['context'] = 'Time-based calculation'
    
    return info


def generate_table_html(table_name, df, out_dir):
    """Generate enhanced HTML documentation for a table."""
    
    meta = TABLE_META.get(table_name, {
        'description': f'{table_name} table',
        'purpose': 'Data table',
        'source_module': 'Unknown',
        'logic': 'See source code',
    })
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{table_name} - BenchSight v12.03</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1800px; margin: 0 auto; }}
        h1 {{ color: #1a1a2e; margin-bottom: 5px; }}
        h2 {{ color: #4a4e69; margin-top: 30px; border-bottom: 2px solid #4a4e69; padding-bottom: 5px; }}
        h3 {{ color: #22223b; margin-top: 20px; }}
        .back-link {{ color: #4a4e69; text-decoration: none; }}
        .back-link:hover {{ text-decoration: underline; }}
        .meta {{ background: #e8e8e8; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .description {{ background: #f0f7ff; border-left: 4px solid #0066cc; padding: 15px; margin: 15px 0; }}
        .critical {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 15px 0; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 13px; vertical-align: top; }}
        th {{ background: #4a4e69; color: white; position: sticky; top: 0; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        tr:hover {{ background: #f0f0f0; }}
        .type-explicit {{ background: #d4edda; color: #155724; padding: 2px 6px; border-radius: 3px; font-size: 11px; }}
        .type-calculated {{ background: #cce5ff; color: #004085; padding: 2px 6px; border-radius: 3px; font-size: 11px; }}
        .type-derived {{ background: #e2d5f1; color: #4a235a; padding: 2px 6px; border-radius: 3px; font-size: 11px; }}
        .type-fk {{ background: #ffeeba; color: #856404; padding: 2px 6px; border-radius: 3px; font-size: 11px; }}
        .type-unknown {{ background: #e9ecef; color: #495057; padding: 2px 6px; border-radius: 3px; font-size: 11px; }}
        code {{ background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-family: monospace; font-size: 12px; }}
        .null-high {{ color: #dc3545; font-weight: bold; }}
        .null-medium {{ color: #fd7e14; }}
        .null-low {{ color: #28a745; }}
        footer {{ margin-top: 40px; padding: 20px; text-align: center; color: #888; font-size: 12px; }}
        .scrollable {{ overflow-x: auto; max-height: 600px; overflow-y: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <p><a href="../index.html" class="back-link">← Back to Index</a></p>
        <h1>{table_name}</h1>
        
        <div class="meta">
            <strong>Rows:</strong> {len(df):,} | 
            <strong>Columns:</strong> {len(df.columns)} |
            <strong>Last Updated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")} |
            <strong>Version:</strong> 12.03
        </div>
        
        <div class="card">
            <h2>Table Overview</h2>
            <div class="description">
                <strong>Description:</strong> {meta.get('description', 'No description available.')}
            </div>
            <p><strong>Purpose:</strong> {meta.get('purpose', 'N/A')}</p>
            <p><strong>Source Module:</strong> <code>{meta.get('source_module', 'Unknown')}</code></p>
            <p><strong>Logic:</strong> {meta.get('logic', 'See source code.')}</p>
'''
    
    # Add key rules if present
    if meta.get('key_rules'):
        html += f'''
            <div class="critical">
                <strong>⚠️ Key Rules:</strong> {meta['key_rules']}
            </div>
'''
    
    html += '''
        </div>
        
        <div class="card">
            <h2>Column Documentation</h2>
            <p><strong>Legend:</strong> 
                <span class="type-explicit">Explicit</span> = From raw data |
                <span class="type-calculated">Calculated</span> = Formula-based |
                <span class="type-derived">Derived</span> = Generated key/aggregate |
                <span class="type-fk">FK</span> = Foreign key lookup
            </p>
            <div class="scrollable">
                <table>
                    <tr>
                        <th style="min-width:150px">Column</th>
                        <th style="min-width:80px">Data Type</th>
                        <th style="min-width:250px">Description</th>
                        <th style="min-width:200px">Context / Mapping</th>
                        <th style="min-width:200px">Calculation / Formula</th>
                        <th style="min-width:70px">Type</th>
                        <th style="min-width:60px">Non-Null</th>
                        <th style="min-width:50px">Null %</th>
                    </tr>
'''
    
    for col in df.columns:
        info = get_column_info(col)
        dtype = str(df[col].dtype)
        non_null = df[col].notna().sum()
        null_pct = (df[col].isna().sum() / len(df)) * 100 if len(df) > 0 else 0
        
        # Color code null percentage
        if null_pct > 80:
            null_class = 'null-high'
        elif null_pct > 50:
            null_class = 'null-medium'
        else:
            null_class = 'null-low'
        
        type_class = f"type-{info['type'].lower()}"
        
        html += f'''                    <tr>
                        <td><code>{col}</code></td>
                        <td>{dtype}</td>
                        <td>{info['desc']}</td>
                        <td>{info['context']}</td>
                        <td>{info['calc']}</td>
                        <td><span class="{type_class}">{info['type']}</span></td>
                        <td>{non_null:,}</td>
                        <td class="{null_class}">{null_pct:.1f}%</td>
                    </tr>
'''
    
    html += '''                </table>
            </div>
        </div>
'''
    
    # Add sample data
    html += '''
        <div class="card">
            <h2>Sample Data (First 10 Rows)</h2>
            <div class="scrollable">
'''
    
    sample_html = df.head(10).to_html(index=False, classes='data-table', border=1, na_rep='NULL')
    html += sample_html
    
    html += '''
            </div>
        </div>
        
        <footer>
            BenchSight v12.03 | Generated ''' + datetime.now().strftime("%Y-%m-%d %H:%M") + '''
        </footer>
    </div>
</body>
</html>
'''
    
    # Write file
    out_path = os.path.join(out_dir, f'{table_name}.html')
    with open(out_path, 'w') as f:
        f.write(html)
    
    return out_path


def main():
    """Generate enhanced documentation for all tables."""
    
    os.makedirs(HTML_DIR, exist_ok=True)
    
    # Get all CSV files
    csv_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.csv')]
    
    print(f"Generating enhanced documentation for {len(csv_files)} tables...")
    
    for csv_file in sorted(csv_files):
        table_name = csv_file.replace('.csv', '')
        csv_path = os.path.join(OUTPUT_DIR, csv_file)
        
        try:
            df = pd.read_csv(csv_path, nrows=1000)  # Read sample for speed
            full_df = pd.read_csv(csv_path)  # Read full for stats
            
            # Use full_df for stats but sample for preview
            out_path = generate_table_html(table_name, full_df, HTML_DIR)
            print(f"  ✓ {table_name}: {len(full_df):,} rows, {len(full_df.columns)} cols")
        except Exception as e:
            print(f"  ✗ {table_name}: {e}")
    
    print(f"\nDone! HTML files written to {HTML_DIR}/")


if __name__ == '__main__':
    main()
