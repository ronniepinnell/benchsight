-- ============================================================================
-- BENCHSIGHT: DROP ALL TABLES (Complete Teardown)
-- ============================================================================
-- This script drops ALL BenchSight tables from Supabase.
-- Run this before a full rebuild or to completely reset the database.
--
-- WARNING: This is destructive! All data will be lost.
--
-- Usage:
--   1. Connect to Supabase SQL Editor
--   2. Copy and paste this entire script
--   3. Execute
--   4. Verify tables are dropped
-- ============================================================================

-- Disable triggers during drop
SET session_replication_role = 'replica';

-- ============================================================================
-- DROP QA TABLES (no dependencies)
-- ============================================================================
DROP TABLE IF EXISTS fact_suspicious_stats CASCADE;
DROP TABLE IF EXISTS fact_game_status CASCADE;
DROP TABLE IF EXISTS fact_player_game_position CASCADE;

-- ============================================================================
-- DROP FACT TABLES (depend on dims)
-- ============================================================================
DROP TABLE IF EXISTS fact_player_game_stats CASCADE;
DROP TABLE IF EXISTS fact_events CASCADE;
DROP TABLE IF EXISTS fact_events_player CASCADE;
DROP TABLE IF EXISTS fact_events_long CASCADE;
DROP TABLE IF EXISTS fact_events_tracking CASCADE;
DROP TABLE IF EXISTS fact_shifts CASCADE;
DROP TABLE IF EXISTS fact_shifts_player CASCADE;
DROP TABLE IF EXISTS fact_shift_players CASCADE;
DROP TABLE IF EXISTS fact_gameroster CASCADE;
DROP TABLE IF EXISTS fact_goalie_game_stats CASCADE;
DROP TABLE IF EXISTS fact_team_game_stats CASCADE;
DROP TABLE IF EXISTS fact_h2h CASCADE;
DROP TABLE IF EXISTS fact_wowy CASCADE;
DROP TABLE IF EXISTS fact_line_combos CASCADE;
DROP TABLE IF EXISTS fact_event_chains CASCADE;
DROP TABLE IF EXISTS fact_team_zone_time CASCADE;
DROP TABLE IF EXISTS fact_rush_events CASCADE;
DROP TABLE IF EXISTS fact_cycle_events CASCADE;
DROP TABLE IF EXISTS fact_possession_time CASCADE;
DROP TABLE IF EXISTS fact_shift_quality CASCADE;
DROP TABLE IF EXISTS fact_matchup_summary CASCADE;
DROP TABLE IF EXISTS fact_leadership CASCADE;
DROP TABLE IF EXISTS fact_registration CASCADE;
DROP TABLE IF EXISTS fact_draft CASCADE;
DROP TABLE IF EXISTS fact_playergames CASCADE;

-- ============================================================================
-- DROP DIMENSION TABLES
-- ============================================================================
DROP TABLE IF EXISTS dim_player CASCADE;
DROP TABLE IF EXISTS dim_team CASCADE;
DROP TABLE IF EXISTS dim_schedule CASCADE;
DROP TABLE IF EXISTS dim_league CASCADE;
DROP TABLE IF EXISTS dim_season CASCADE;
DROP TABLE IF EXISTS dim_position CASCADE;
DROP TABLE IF EXISTS dim_venue CASCADE;
DROP TABLE IF EXISTS dim_period CASCADE;
DROP TABLE IF EXISTS dim_player_role CASCADE;
DROP TABLE IF EXISTS dim_playerurlref CASCADE;
DROP TABLE IF EXISTS dim_rinkboxcoord CASCADE;
DROP TABLE IF EXISTS dim_rinkcoordzones CASCADE;
DROP TABLE IF EXISTS dim_randomnames CASCADE;
DROP TABLE IF EXISTS dim_composite_rating CASCADE;
DROP TABLE IF EXISTS dim_stat_type CASCADE;
DROP TABLE IF EXISTS dim_situation CASCADE;
DROP TABLE IF EXISTS dim_strength CASCADE;
DROP TABLE IF EXISTS dim_event_type CASCADE;
DROP TABLE IF EXISTS dim_rink_coord CASCADE;
DROP TABLE IF EXISTS dim_shot_type CASCADE;
DROP TABLE IF EXISTS dim_pass_type CASCADE;
DROP TABLE IF EXISTS dim_turnover_type CASCADE;
DROP TABLE IF EXISTS dim_giveaway_type CASCADE;
DROP TABLE IF EXISTS dim_takeaway_type CASCADE;
DROP TABLE IF EXISTS dim_zone CASCADE;

-- ============================================================================
-- DROP VIEWS (if any)
-- ============================================================================
DROP VIEW IF EXISTS vw_player_season_stats CASCADE;
DROP VIEW IF EXISTS vw_team_standings CASCADE;
DROP VIEW IF EXISTS vw_recent_games CASCADE;
DROP VIEW IF EXISTS vw_top_scorers CASCADE;
DROP VIEW IF EXISTS vw_goalie_stats CASCADE;

-- ============================================================================
-- DROP FUNCTIONS (if any)
-- ============================================================================
DROP FUNCTION IF EXISTS get_player_stats(text);
DROP FUNCTION IF EXISTS get_game_summary(integer);
DROP FUNCTION IF EXISTS calculate_standings();

-- Re-enable triggers
SET session_replication_role = 'origin';

-- ============================================================================
-- VERIFICATION: Show remaining tables
-- ============================================================================
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Expected output: No BenchSight tables should remain
