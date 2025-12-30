-- ================================================================
-- BenchSight Quick Operations
-- Common operations for day-to-day database management
-- ================================================================

-- ================================================================
-- OPERATION 1: CHECK STATUS
-- Run this first to see current state
-- ================================================================
SELECT '=== TABLE ROW COUNTS ===' as info;
SELECT * FROM get_all_table_counts();

SELECT '=== TRACKED GAMES ===' as info;
SELECT * FROM get_games_status();

-- ================================================================
-- OPERATION 2: DROP ALL TABLES (DANGER!)
-- Uncomment to execute
-- ================================================================
/*
DROP TABLE IF EXISTS load_history, etl_queue, staging_shifts, staging_events,
    fact_wowy, fact_h2h, fact_goalie_game_stats, fact_team_game_stats, 
    fact_player_game_stats, fact_shifts_player, fact_events_player, 
    fact_events, fact_shifts, dim_schedule, dim_team, dim_player CASCADE;
DROP FUNCTION IF EXISTS get_all_table_counts, delete_game_data, truncate_all_facts, get_games_status CASCADE;
*/

-- ================================================================
-- OPERATION 3: TRUNCATE ALL FACTS (Keep dimensions)
-- Uncomment to execute
-- ================================================================
/*
SELECT truncate_all_facts();
*/

-- ================================================================
-- OPERATION 4: DELETE SINGLE GAME
-- Replace 18969 with your game_id
-- ================================================================
/*
SELECT delete_game_data(18969);
*/

-- ================================================================
-- OPERATION 5: VALIDATE DATA QUALITY
-- ================================================================
SELECT '=== VALIDATION CHECKS ===' as info;

-- Check for duplicate primary keys
SELECT 'Duplicate check: dim_player' as check_name, 
       COUNT(*) - COUNT(DISTINCT player_id) as duplicates 
FROM dim_player;

SELECT 'Duplicate check: fact_events' as check_name,
       COUNT(*) - COUNT(DISTINCT event_key) as duplicates
FROM fact_events;

-- Check for orphaned records
SELECT 'Orphaned events (no schedule)' as check_name, COUNT(*) as count
FROM fact_events e
LEFT JOIN dim_schedule s ON e.game_id = s.game_id
WHERE s.game_id IS NULL;

SELECT 'Orphaned player stats (no player)' as check_name, COUNT(*) as count
FROM fact_player_game_stats ps
LEFT JOIN dim_player p ON ps.player_id = p.player_id
WHERE p.player_id IS NULL;

-- Check percentage ranges
SELECT 'Invalid shooting_pct' as check_name, COUNT(*) as count
FROM fact_player_game_stats
WHERE shooting_pct IS NOT NULL AND (shooting_pct < 0 OR shooting_pct > 100);

-- Check business logic
SELECT 'Points != Goals + Assists' as check_name, COUNT(*) as count
FROM fact_player_game_stats
WHERE points != goals + assists;

-- ================================================================
-- OPERATION 6: GET SAMPLE DATA
-- ================================================================
SELECT '=== SAMPLE: Top Scorers ===' as info;
SELECT player_full_name, team_name, goals, assists, points
FROM fact_player_game_stats
ORDER BY points DESC
LIMIT 10;

SELECT '=== SAMPLE: Recent Events ===' as info;
SELECT game_id, event_index, event_type, event_detail, event_team_player_1
FROM fact_events
ORDER BY game_id DESC, event_index DESC
LIMIT 10;

-- ================================================================
-- OPERATION 7: ADD FOREIGN KEYS (Run after data load)
-- ================================================================
/*
-- Uncomment each as needed

ALTER TABLE fact_shifts 
    ADD CONSTRAINT fk_shifts_schedule 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id) ON DELETE SET NULL;

ALTER TABLE fact_events 
    ADD CONSTRAINT fk_events_schedule 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id) ON DELETE SET NULL;

ALTER TABLE fact_player_game_stats 
    ADD CONSTRAINT fk_playerstats_player 
    FOREIGN KEY (player_id) REFERENCES dim_player(player_id) ON DELETE SET NULL;

ALTER TABLE fact_player_game_stats 
    ADD CONSTRAINT fk_playerstats_schedule 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id) ON DELETE SET NULL;
*/

-- ================================================================
-- OPERATION 8: REMOVE FOREIGN KEYS (For flexible loading)
-- ================================================================
/*
ALTER TABLE fact_shifts DROP CONSTRAINT IF EXISTS fk_shifts_schedule;
ALTER TABLE fact_events DROP CONSTRAINT IF EXISTS fk_events_schedule;
ALTER TABLE fact_events DROP CONSTRAINT IF EXISTS fk_events_shift;
ALTER TABLE fact_player_game_stats DROP CONSTRAINT IF EXISTS fk_playerstats_player;
ALTER TABLE fact_player_game_stats DROP CONSTRAINT IF EXISTS fk_playerstats_schedule;
-- Add more as needed...
*/

-- ================================================================
-- OPERATION 9: RESET SEQUENCES (After truncate)
-- ================================================================
/*
ALTER SEQUENCE fact_events_player_id_seq RESTART WITH 1;
ALTER SEQUENCE fact_shifts_player_id_seq RESTART WITH 1;
ALTER SEQUENCE etl_queue_id_seq RESTART WITH 1;
ALTER SEQUENCE load_history_id_seq RESTART WITH 1;
*/

-- ================================================================
-- OPERATION 10: EXPORT TO CSV
-- Run from psql: \copy (SELECT * FROM table) TO 'file.csv' CSV HEADER
-- ================================================================
/*
-- Example:
\copy (SELECT * FROM dim_player) TO '/tmp/dim_player_export.csv' CSV HEADER;
\copy (SELECT * FROM fact_player_game_stats) TO '/tmp/fact_player_game_stats_export.csv' CSV HEADER;
*/

-- ================================================================
-- OPERATION 11: IMPORT FROM CSV
-- Run from psql: \copy table FROM 'file.csv' CSV HEADER
-- ================================================================
/*
-- Example (load in order!):
\copy dim_player FROM '/path/to/dim_player.csv' CSV HEADER;
\copy dim_team FROM '/path/to/dim_team.csv' CSV HEADER;
\copy dim_schedule FROM '/path/to/dim_schedule.csv' CSV HEADER;
\copy fact_shifts FROM '/path/to/fact_shifts.csv' CSV HEADER;
\copy fact_events FROM '/path/to/fact_events.csv' CSV HEADER;
-- Continue for all tables...
*/

-- ================================================================
-- END OF QUICK OPERATIONS
-- ================================================================
