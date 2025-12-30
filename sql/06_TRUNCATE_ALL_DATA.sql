-- ============================================================
-- TRUNCATE ALL DATA TABLES
-- ============================================================
-- Run this to clear ALL data from tables before reloading
-- This keeps the table structures but removes all rows
-- ============================================================

-- Disable FK checks temporarily
SET session_replication_role = 'replica';

-- Truncate all fact tables first (they reference dims)
TRUNCATE TABLE fact_wowy CASCADE;
TRUNCATE TABLE fact_video CASCADE;
TRUNCATE TABLE fact_team_zone_time CASCADE;
TRUNCATE TABLE fact_team_standings_snapshot CASCADE;
TRUNCATE TABLE fact_team_game_stats CASCADE;
TRUNCATE TABLE fact_suspicious_stats CASCADE;
TRUNCATE TABLE fact_shot_xy CASCADE;
TRUNCATE TABLE fact_shot_danger CASCADE;
TRUNCATE TABLE fact_shifts_tracking CASCADE;
TRUNCATE TABLE fact_shifts_player CASCADE;
TRUNCATE TABLE fact_shifts_long CASCADE;
TRUNCATE TABLE fact_shifts CASCADE;
TRUNCATE TABLE fact_shift_quality_logical CASCADE;
TRUNCATE TABLE fact_shift_quality CASCADE;
TRUNCATE TABLE fact_shift_players CASCADE;
TRUNCATE TABLE fact_sequences CASCADE;
TRUNCATE TABLE fact_scoring_chances CASCADE;
TRUNCATE TABLE fact_rush_events CASCADE;
TRUNCATE TABLE fact_registration CASCADE;
TRUNCATE TABLE fact_puck_xy_wide CASCADE;
TRUNCATE TABLE fact_puck_xy_long CASCADE;
TRUNCATE TABLE fact_possession_time CASCADE;
TRUNCATE TABLE fact_plays CASCADE;
TRUNCATE TABLE fact_playergames CASCADE;
TRUNCATE TABLE fact_player_xy_wide CASCADE;
TRUNCATE TABLE fact_player_xy_long CASCADE;
TRUNCATE TABLE fact_player_stats_long CASCADE;
TRUNCATE TABLE fact_player_period_stats CASCADE;
TRUNCATE TABLE fact_player_pair_stats CASCADE;
TRUNCATE TABLE fact_player_micro_stats CASCADE;
TRUNCATE TABLE fact_player_game_stats CASCADE;
TRUNCATE TABLE fact_player_game_position CASCADE;
TRUNCATE TABLE fact_player_event_chains CASCADE;
TRUNCATE TABLE fact_player_boxscore_all CASCADE;
TRUNCATE TABLE fact_matchup_summary CASCADE;
TRUNCATE TABLE fact_linked_events CASCADE;
TRUNCATE TABLE fact_line_combos CASCADE;
TRUNCATE TABLE fact_league_leaders_snapshot CASCADE;
TRUNCATE TABLE fact_leadership CASCADE;
TRUNCATE TABLE fact_head_to_head CASCADE;
TRUNCATE TABLE fact_h2h CASCADE;
TRUNCATE TABLE fact_goalie_game_stats CASCADE;
TRUNCATE TABLE fact_gameroster CASCADE;
TRUNCATE TABLE fact_game_status CASCADE;
TRUNCATE TABLE fact_events_tracking CASCADE;
TRUNCATE TABLE fact_events_player CASCADE;
TRUNCATE TABLE fact_events_long CASCADE;
TRUNCATE TABLE fact_events CASCADE;
TRUNCATE TABLE fact_event_chains CASCADE;
TRUNCATE TABLE fact_draft CASCADE;
TRUNCATE TABLE fact_cycle_events CASCADE;

-- Truncate dimension tables
TRUNCATE TABLE dim_zone_exit_type CASCADE;
TRUNCATE TABLE dim_zone_entry_type CASCADE;
TRUNCATE TABLE dim_zone CASCADE;
TRUNCATE TABLE dim_venue CASCADE;
TRUNCATE TABLE dim_turnover_type CASCADE;
TRUNCATE TABLE dim_turnover_quality CASCADE;
TRUNCATE TABLE dim_terminology_mapping CASCADE;
TRUNCATE TABLE dim_team CASCADE;
TRUNCATE TABLE dim_takeaway_type CASCADE;
TRUNCATE TABLE dim_success CASCADE;
TRUNCATE TABLE dim_strength CASCADE;
TRUNCATE TABLE dim_stoppage_type CASCADE;
TRUNCATE TABLE dim_stat_type CASCADE;
TRUNCATE TABLE dim_stat_category CASCADE;
TRUNCATE TABLE dim_stat CASCADE;
TRUNCATE TABLE dim_situation CASCADE;
TRUNCATE TABLE dim_shot_type CASCADE;
TRUNCATE TABLE dim_shift_stop_type CASCADE;
TRUNCATE TABLE dim_shift_start_type CASCADE;
TRUNCATE TABLE dim_shift_slot CASCADE;
TRUNCATE TABLE dim_season CASCADE;
TRUNCATE TABLE dim_schedule CASCADE;
TRUNCATE TABLE dim_rinkcoordzones CASCADE;
TRUNCATE TABLE dim_rinkboxcoord CASCADE;
TRUNCATE TABLE dim_rink_coord CASCADE;
TRUNCATE TABLE dim_randomnames CASCADE;
TRUNCATE TABLE dim_position CASCADE;
TRUNCATE TABLE dim_playerurlref CASCADE;
TRUNCATE TABLE dim_player_role CASCADE;
TRUNCATE TABLE dim_player CASCADE;
TRUNCATE TABLE dim_play_detail_2 CASCADE;
TRUNCATE TABLE dim_play_detail CASCADE;
TRUNCATE TABLE dim_period CASCADE;
TRUNCATE TABLE dim_pass_type CASCADE;
TRUNCATE TABLE dim_net_location CASCADE;
TRUNCATE TABLE dim_micro_stat CASCADE;
TRUNCATE TABLE dim_league CASCADE;
TRUNCATE TABLE dim_giveaway_type CASCADE;
TRUNCATE TABLE dim_event_type CASCADE;
TRUNCATE TABLE dim_event_detail_2 CASCADE;
TRUNCATE TABLE dim_event_detail CASCADE;
TRUNCATE TABLE dim_danger_zone CASCADE;
TRUNCATE TABLE dim_composite_rating CASCADE;
TRUNCATE TABLE dim_comparison_type CASCADE;

-- Truncate other tables
TRUNCATE TABLE qa_suspicious_stats CASCADE;

-- Re-enable FK checks
SET session_replication_role = 'origin';

-- Show confirmation
SELECT 'All data tables truncated' as status;
