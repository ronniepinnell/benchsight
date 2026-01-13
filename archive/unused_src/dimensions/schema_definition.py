#!/usr/bin/env python3
"""
BenchSight Schema Definition - SINGLE SOURCE OF TRUTH
Generated from actual Supabase schema query.

This file defines exactly what columns exist in each table.
All ETL, validation, and tests reference this file.
"""

# =============================================================================
# SCHEMA DEFINITION - Matches Supabase exactly
# =============================================================================

SCHEMA = {
    'dim_danger_zone': [
        'danger_zone_id', 'danger_zone_code', 'danger_zone_name', 'description',
        'xg_multiplier', 'x_min', 'x_max', 'y_min', 'y_max'
    ],
    
    'dim_event_detail': [
        'event_detail_id', 'event_detail', 'event_type', 'category',
        'is_shot_on_goal', 'is_goal', 'is_miss', 'is_block', 'is_giveaway',
        'is_takeaway', 'is_controlled', 'is_success', 'danger_potential', 'description'
    ],
    
    'dim_event_detail_2': [
        'event_detail_2_id', 'event_detail_2', 'event_type_dependency',
        'event_detail_dependency', 'subcategory', 'description'
    ],
    
    'dim_event_type': [
        'event_type_id', 'event_type', 'event_category', 'description',
        'is_shot', 'is_pass', 'is_possession', 'is_turnover', 'is_penalty',
        'is_faceoff', 'is_zone_play', 'is_stoppage', 'is_save', 'is_hit',
        'is_rebound', 'credits_event_player_1', 'credits_opp_player_1',
        'affects_toi_playing', 'sort_order'
    ],
    
    'dim_game_players_tracking': [
        'game_id', 'player_game_number', 'player_id', 'player_full_name',
        'player_team', 'player_venue', 'position', 'skill_rating',
        'player_game_key', 'display_name'
    ],
    
    'dim_league': ['league_id', 'league'],
    
    'dim_net_location': [
        'net_location_id', 'net_location_code', 'net_location_name',
        'net_location_short', 'vertical_zone', 'horizontal_zone', 'description',
        'difficulty_score', 'goalie_weakness_common', 'x_min', 'x_max',
        'y_min', 'y_max', 'display_order'
    ],
    
    'dim_pass_type': [
        'pass_type_id', 'pass_type', 'description', 'difficulty_rating',
        'danger_potential', 'is_slot_pass', 'is_cross_ice'
    ],
    
    'dim_period': [
        'period_id', 'period_name', 'period_abbr', 'is_overtime',
        'is_shootout', 'sort_order'
    ],
    
    'dim_play_detail': [
        'play_detail_id', 'play_detail', 'play_category', 'play_type',
        'is_offensive', 'is_defensive', 'is_transition', 'is_recovery',
        'credits_player', 'description'
    ],
    
    'dim_player': [
        'player_id', 'player_first_name', 'player_last_name', 'player_full_name',
        'player_primary_position', 'current_skill_rating', 'player_hand',
        'birth_year', 'player_gender', 'highest_beer_league', 'player_rating_ly',
        'player_notes', 'player_leadership', 'player_norad', 'player_csaha',
        'player_norad_primary_number', 'player_csah_primary_number',
        'player_norad_current_team', 'player_csah_current_team',
        'player_norad_current_team_id', 'player_csah_current_team_id',
        'other_url', 'player_url', 'player_image', 'random_player_first_name',
        'random_player_last_name', 'random_player_full_name'
    ],
    
    'dim_player_role': [
        'player_role_id', 'role_name', 'role_code', 'role_type', 'description'
    ],
    
    'dim_playerurlref': [
        'player_id', 'n_player_url', 'league', 'player_full_name', 'n_player_id_2'
    ],
    
    'dim_position': [
        'position_id', 'position_name', 'position_code', 'is_forward',
        'is_defense', 'is_goalie', 'is_skater'
    ],
    
    'dim_rink_zone': [
        'rink_zone_id', 'zone_code', 'zone_name', 'granularity',
        'x_min', 'x_max', 'y_min', 'y_max', 'zone', 'danger', 'side',
        'x_description', 'y_description'
    ],
    
    'dim_schedule': [
        'game_id', 'season', 'season_id', 'game_url', 'home_team_game_id',
        'away_team_game_id', 'game_date', 'game_time', 'home_team_name',
        'away_team_name', 'home_team_id', 'away_team_id', 'head_to_head_id',
        'game_type', 'playoff_round', 'last_period_type', 'period_length',
        'ot_period_length', 'shootout_rounds', 'home_total_goals', 'away_total_goals',
        'home_team_period1_goals', 'home_team_period2_goals', 'home_team_period3_goals',
        'home_team_periodot_goals', 'away_team_period1_goals', 'away_team_period2_goals',
        'away_team_period3_goals', 'away_team_periodot_goals', 'home_team_seeding',
        'away_team_seeding', 'home_team_w', 'home_team_l', 'home_team_t',
        'home_team_pts', 'away_team_w', 'away_team_l', 'away_team_t', 'away_team_pts',
        'video_id', 'video_url', 'video_start_time', 'video_end_time', 'video_title'
    ],
    
    'dim_season': [
        'season_id', 'season', 'session', 'norad', 'csah', 'league_id',
        'league', 'start_date'
    ],
    
    'dim_shift_type': [
        'shift_type_id', 'shift_type', 'description'
    ],
    
    'dim_shot_type': [
        'shot_type_id', 'shot_type', 'shot_type_short', 'description',
        'difficulty_rating', 'is_one_timer', 'is_dangerous', 'avg_sh_pct'
    ],
    
    'dim_situation': [
        'situation_id', 'situation_name', 'situation_code', 'description',
        'is_even_strength', 'is_power_play', 'is_penalty_kill'
    ],
    
    'dim_skill_tier': [
        'skill_tier_id', 'tier_id', 'tier_name', 'min_rating', 'max_rating', 'description'
    ],
    
    'dim_stat': [
        'stat_id', 'stat_name', 'stat_abbrev', 'stat_short', 'category',
        'subcategory', 'description', 'formula', 'data_source', 'player_role',
        'level', 'requires_toi', 'requires_goals', 'requires_shots', 'requires_xg',
        'requires_xy', 'higher_is_better', 'benchmark_poor', 'benchmark_avg',
        'benchmark_good', 'benchmark_elite', 'display_order', 'status'
    ],
    
    'dim_strength': [
        'strength_id', 'strength', 'description', 'home_players', 'away_players',
        'is_even', 'is_powerplay', 'is_shorthanded'
    ],
    
    'dim_team': [
        'team_id', 'team_name', 'norad_team', 'csah_team', 'league_id', 'league',
        'long_team_name', 'team_cd', 'team_color1', 'team_color2', 'team_color3',
        'team_color4', 'team_logo', 'team_url'
    ],
    
    'dim_time_bucket': [
        'time_bucket_id', 'bucket_name', 'period_start_min', 'period_end_min', 'description'
    ],
    
    'dim_turnover_type': [
        'turnover_type_id', 'turnover_type', 'turnover_category', 'description',
        'is_giveaway', 'is_takeaway', 'is_bad_turnover', 'is_neutral_turnover',
        'is_forced', 'penalty_weight'
    ],
    
    'dim_venue': [
        'venue_id', 'venue_name', 'venue_code', 'is_home', 'is_away'
    ],
    
    'dim_video': [
        'video_id', 'game_id', 'video_url', 'video_title', 'video_platform',
        'video_duration_seconds', 'period_1_start', 'period_2_start',
        'period_3_start', 'ot_start', 'upload_date', 'video_quality'
    ],
    
    'dim_zone': [
        'zone_id', 'zone_name', 'zone_code', 'is_offensive', 'is_defensive', 'is_neutral'
    ],
    
    # Fact tables
    'fact_box_score_tracking': None,  # Flexible - accept all columns
    
    'fact_draft': [
        'player_draft_id', 'season_id', 'season', 'league', 'team_id', 'team_name',
        'player_id', 'player_full_name', 'round', 'pick', 'overall_draft_round',
        'overall_draft_position', 'unrestricted_draft_position', 'restricted',
        'skill_rating'
    ],
    
    'fact_event_players_tracking': [
        'event_player_key', 'event_key', 'game_id', 'event_index', 'player_game_number',
        'player_game_key', 'player_id', 'player_role', 'role_number', 'player_team',
        'team_venue', 'is_event_team', 'is_opp_team', 'is_primary_player',
        'play_detail1', 'play_detail_2', 'play_detail_successful', 'skill_rating'
    ],
    
    'fact_events_long': [
        'game_id', 'event_index', 'event_type', 'period', 'zone', 'team',
        'success', 'detail_1', 'detail_2', 'shift_index', 'player_number',
        'player_role', 'video_time', 'clock_start_seconds', 'clock_end_seconds'
    ],
    
    'fact_event_players': [
        'event_key', 'game_id', 'event_index', 'shift_index', 'linked_event_index',
        'sequence_index', 'play_index', 'period', 'event_type', 'event_detail',
        'event_detail_2', 'event_successful', 'event_team_zone', 'team_venue',
        'time_start_total_seconds', 'time_end_total_seconds', 'duration',
        'play_detail1', 'play_detail_2', 'play_detail_successful',
        'pressured_pressurer', 'home_team', 'away_team'
    ],
    
    'fact_gameroster': [
        'roster_key', 'game_id', 'team_game_id', 'opp_team_game_id', 'player_game_id',
        'team_venue', 'team_name', 'opp_team_name', 'player_game_number',
        'n_player_url', 'player_position', 'games_played', 'goals', 'assist',
        'goals_against', 'pim', 'shutouts', 'team_id', 'opp_team_id',
        'player_full_name', 'player_id', 'game_date', 'season', 'sub',
        'current_team', 'skill_rating'
    ],
    
    'fact_leadership': [
        'leadership_key', 'season_id', 'season', 'team_id', 'team_name',
        'player_id', 'player_full_name', 'n_player_url', 'leadership', 'skill_rating'
    ],
    
    'fact_linked_events_tracking': None,  # Flexible
    
    'fact_playergames': [
        'game_type_id', 'game_date', 'game_type', 'team', 'opp', 'jersey_number',
        'player', 'position', 'gp', 'goals', 'assists', 'goals_against', 'pim',
        'shutouts', 'skill_rank', 'id2', 'id3', 'season', 'season_player_id'
    ],
    
    'fact_plays_tracking': None,  # Flexible
    
    'fact_registration': [
        'player_season_registration_id', 'season_id', 'season', 'player_id',
        'player_full_name', 'email', 'age', 'highest_beer_league_played',
        'norad_experience', 'referred_by', 'caf', 'restricted', 'sub_yn',
        'drafted_team_id', 'drafted_team_name', 'skill_rating', 'jersey_number', 'position'
    ],
    
    'fact_sequences_tracking': None,  # Flexible
    'fact_shift_players_tracking': None,  # Flexible
    
    'fact_shifts': [
        'shift_key', 'game_id', 'shift_index', 'period', 'Period',
        'shift_start_min', 'shift_start_sec', 'shift_end_min', 'shift_end_sec',
        'shift_start_total_seconds', 'shift_end_total_seconds', 'shift_duration',
        'shift_start_type', 'shift_stop_type', 'home_team', 'away_team',
        'home_forward_1', 'home_forward_2', 'home_forward_3', 'home_defense_1',
        'home_defense_2', 'home_xtra', 'home_goalie', 'away_forward_1',
        'away_forward_2', 'away_forward_3', 'away_defense_1', 'away_defense_2',
        'away_xtra', 'away_goalie', 'home_team_strength', 'away_team_strength',
        'situation', 'strength', 'home_goals', 'away_goals'
    ],
}

# Tables that don't exist in Supabase (skip during upload)
SKIP_TABLES = ['dim_randomnames']

# Primary keys for each table (for upsert operations)
PRIMARY_KEYS = {
    'dim_danger_zone': 'danger_zone_id',
    'dim_event_detail': 'event_detail_id',
    'dim_event_detail_2': 'event_detail_2_id',
    'dim_event_type': 'event_type_id',
    'dim_game_players_tracking': 'player_game_key',
    'dim_league': 'league_id',
    'dim_net_location': 'net_location_id',
    'dim_pass_type': 'pass_type_id',
    'dim_period': 'period_id',
    'dim_play_detail': 'play_detail_id',
    'dim_player': 'player_id',
    'dim_player_role': 'player_role_id',
    'dim_playerurlref': 'player_id',
    'dim_position': 'position_id',
    'dim_rink_zone': 'rink_zone_id',
    'dim_schedule': 'game_id',
    'dim_season': 'season_id',
    'dim_shift_type': 'shift_type_id',
    'dim_shot_type': 'shot_type_id',
    'dim_situation': 'situation_id',
    'dim_skill_tier': 'skill_tier_id',
    'dim_stat': 'stat_id',
    'dim_strength': 'strength_id',
    'dim_team': 'team_id',
    'dim_time_bucket': 'time_bucket_id',
    'dim_turnover_type': 'turnover_type_id',
    'dim_venue': 'venue_id',
    'dim_video': 'video_id',
    'dim_zone': 'zone_id',
    'fact_box_score_tracking': None,
    'fact_draft': 'player_draft_id',
    'fact_event_players_tracking': 'event_player_key',
    'fact_events_long': None,
    'fact_event_players': 'event_key',
    'fact_gameroster': 'roster_key',
    'fact_leadership': 'leadership_key',
    'fact_linked_events_tracking': None,
    'fact_playergames': 'season_player_id',
    'fact_plays_tracking': None,
    'fact_registration': 'player_season_registration_id',
    'fact_sequences_tracking': None,
    'fact_shift_players_tracking': None,
    'fact_shifts': 'shift_key',
}


def get_table_columns(table_name: str) -> list:
    """Get valid columns for a table. Returns None if table accepts all columns."""
    return SCHEMA.get(table_name)


def is_valid_column(table_name: str, column_name: str) -> bool:
    """Check if a column exists in the schema for a table."""
    cols = SCHEMA.get(table_name)
    if cols is None:  # Flexible table
        return True
    return column_name in cols


def filter_to_schema(table_name: str, columns: list) -> list:
    """Filter a list of columns to only those in the schema."""
    schema_cols = SCHEMA.get(table_name)
    if schema_cols is None:
        return columns  # Accept all
    return [c for c in columns if c in schema_cols]


def get_missing_columns(table_name: str, columns: list) -> list:
    """Get columns that are in schema but not in the provided list."""
    schema_cols = SCHEMA.get(table_name)
    if schema_cols is None:
        return []
    return [c for c in schema_cols if c not in columns]


def get_extra_columns(table_name: str, columns: list) -> list:
    """Get columns that are in data but not in schema (will be dropped)."""
    schema_cols = SCHEMA.get(table_name)
    if schema_cols is None:
        return []
    return [c for c in columns if c not in schema_cols]
