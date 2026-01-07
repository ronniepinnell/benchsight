-- ============================================================
-- BENCHSIGHT - DROP ALL TABLES
-- ============================================================
-- Run this FIRST when resetting the database
-- This drops all tables in the correct order (facts before dims)
-- ============================================================

-- Disable RLS temporarily for cleanup
ALTER TABLE IF EXISTS fact_events_player DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS fact_shifts_player DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS fact_player_game_stats DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS fact_goalie_game_stats DISABLE ROW LEVEL SECURITY;

-- ============================================================
-- DROP FACT TABLES (order matters for foreign keys)
-- ============================================================

DROP TABLE IF EXISTS fact_events_player CASCADE;
DROP TABLE IF EXISTS fact_events CASCADE;
DROP TABLE IF EXISTS fact_shifts_player CASCADE;
DROP TABLE IF EXISTS fact_shifts CASCADE;
DROP TABLE IF EXISTS fact_player_game_stats CASCADE;
DROP TABLE IF EXISTS fact_goalie_game_stats CASCADE;
DROP TABLE IF EXISTS fact_team_game_stats CASCADE;
DROP TABLE IF EXISTS fact_gameroster CASCADE;
DROP TABLE IF EXISTS fact_player_boxscore_all CASCADE;
DROP TABLE IF EXISTS fact_sequences CASCADE;
DROP TABLE IF EXISTS fact_plays CASCADE;
DROP TABLE IF EXISTS fact_playergames CASCADE;
DROP TABLE IF EXISTS fact_registration CASCADE;
DROP TABLE IF EXISTS fact_leadership CASCADE;
DROP TABLE IF EXISTS fact_draft CASCADE;
DROP TABLE IF EXISTS fact_head_to_head CASCADE;
DROP TABLE IF EXISTS fact_player_pair_stats CASCADE;
DROP TABLE IF EXISTS fact_team_standings_snapshot CASCADE;
DROP TABLE IF EXISTS fact_league_leaders_snapshot CASCADE;

-- ============================================================
-- DROP DIMENSION TABLES
-- ============================================================

DROP TABLE IF EXISTS dim_player CASCADE;
DROP TABLE IF EXISTS dim_team CASCADE;
DROP TABLE IF EXISTS dim_season CASCADE;
DROP TABLE IF EXISTS dim_schedule CASCADE;
DROP TABLE IF EXISTS dim_league CASCADE;
DROP TABLE IF EXISTS dim_position CASCADE;
DROP TABLE IF EXISTS dim_venue CASCADE;
DROP TABLE IF EXISTS dim_period CASCADE;
DROP TABLE IF EXISTS dim_event_type CASCADE;
DROP TABLE IF EXISTS dim_event_detail CASCADE;
DROP TABLE IF EXISTS dim_event_detail_2 CASCADE;
DROP TABLE IF EXISTS dim_play_detail CASCADE;
DROP TABLE IF EXISTS dim_play_detail_2 CASCADE;
DROP TABLE IF EXISTS dim_zone CASCADE;
DROP TABLE IF EXISTS dim_zone_entry_type CASCADE;
DROP TABLE IF EXISTS dim_zone_exit_type CASCADE;
DROP TABLE IF EXISTS dim_shot_type CASCADE;
DROP TABLE IF EXISTS dim_pass_type CASCADE;
DROP TABLE IF EXISTS dim_giveaway_type CASCADE;
DROP TABLE IF EXISTS dim_takeaway_type CASCADE;
DROP TABLE IF EXISTS dim_turnover_type CASCADE;
DROP TABLE IF EXISTS dim_turnover_quality CASCADE;
DROP TABLE IF EXISTS dim_success CASCADE;
DROP TABLE IF EXISTS dim_strength CASCADE;
DROP TABLE IF EXISTS dim_situation CASCADE;
DROP TABLE IF EXISTS dim_player_role CASCADE;
DROP TABLE IF EXISTS dim_shift_slot CASCADE;
DROP TABLE IF EXISTS dim_shift_start_type CASCADE;
DROP TABLE IF EXISTS dim_shift_stop_type CASCADE;
DROP TABLE IF EXISTS dim_stoppage_type CASCADE;
DROP TABLE IF EXISTS dim_net_location CASCADE;
DROP TABLE IF EXISTS dim_comparison_type CASCADE;
DROP TABLE IF EXISTS dim_stat CASCADE;
DROP TABLE IF EXISTS dim_stat_type CASCADE;
DROP TABLE IF EXISTS dim_terminology_mapping CASCADE;
DROP TABLE IF EXISTS dim_rinkboxcoord CASCADE;
DROP TABLE IF EXISTS dim_rinkcoordzones CASCADE;
DROP TABLE IF EXISTS dim_playerurlref CASCADE;
DROP TABLE IF EXISTS dim_randomnames CASCADE;

-- ============================================================
-- DONE
-- ============================================================
-- All tables dropped. Run 01_create_tables.sql next.
