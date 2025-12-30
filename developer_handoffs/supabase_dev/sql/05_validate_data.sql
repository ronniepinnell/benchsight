-- BenchSight Data Validation Queries
-- Run after loading data to verify integrity

-- ============================================
-- ROW COUNT VALIDATION
-- ============================================

-- Get row counts for all tables
SELECT 'dim_player' as table_name, COUNT(*) as row_count FROM dim_player
UNION ALL SELECT 'dim_team', COUNT(*) FROM dim_team
UNION ALL SELECT 'dim_schedule', COUNT(*) FROM dim_schedule
UNION ALL SELECT 'fact_shifts', COUNT(*) FROM fact_shifts
UNION ALL SELECT 'fact_events', COUNT(*) FROM fact_events
UNION ALL SELECT 'fact_events_player', COUNT(*) FROM fact_events_player
UNION ALL SELECT 'fact_shifts_player', COUNT(*) FROM fact_shifts_player
UNION ALL SELECT 'fact_player_game_stats', COUNT(*) FROM fact_player_game_stats
UNION ALL SELECT 'fact_team_game_stats', COUNT(*) FROM fact_team_game_stats
UNION ALL SELECT 'fact_goalie_game_stats', COUNT(*) FROM fact_goalie_game_stats
UNION ALL SELECT 'fact_h2h', COUNT(*) FROM fact_h2h
UNION ALL SELECT 'fact_wowy', COUNT(*) FROM fact_wowy
ORDER BY table_name;

-- ============================================
-- PRIMARY KEY DUPLICATE CHECK
-- ============================================

-- Check for duplicate event keys
SELECT event_key, COUNT(*) as cnt
FROM fact_events
GROUP BY event_key
HAVING COUNT(*) > 1;

-- Check for duplicate player stats keys
SELECT player_game_key, COUNT(*) as cnt
FROM fact_player_game_stats
GROUP BY player_game_key
HAVING COUNT(*) > 1;

-- Check for duplicate shift keys
SELECT shift_key, COUNT(*) as cnt
FROM fact_shifts
GROUP BY shift_key
HAVING COUNT(*) > 1;

-- ============================================
-- FOREIGN KEY VALIDATION
-- ============================================

-- Events referencing non-existent games
SELECT DISTINCT e.game_id
FROM fact_events e
LEFT JOIN dim_schedule s ON e.game_id = s.game_id
WHERE s.game_id IS NULL;

-- Events referencing non-existent shifts
SELECT DISTINCT e.shift_key
FROM fact_events e
LEFT JOIN fact_shifts s ON e.shift_key = s.shift_key
WHERE e.shift_key IS NOT NULL AND s.shift_key IS NULL;

-- Player stats referencing non-existent players
SELECT DISTINCT p.player_id
FROM fact_player_game_stats p
LEFT JOIN dim_player d ON p.player_id = d.player_id
WHERE d.player_id IS NULL;

-- ============================================
-- DATA RANGE VALIDATION
-- ============================================

-- Check percentage values are 0-100 (or null)
SELECT 'shooting_pct' as column_name, MIN(shooting_pct), MAX(shooting_pct)
FROM fact_player_game_stats
WHERE shooting_pct IS NOT NULL
UNION ALL
SELECT 'fo_pct', MIN(fo_pct), MAX(fo_pct)
FROM fact_player_game_stats
WHERE fo_pct IS NOT NULL
UNION ALL
SELECT 'pass_pct', MIN(pass_pct), MAX(pass_pct)
FROM fact_player_game_stats
WHERE pass_pct IS NOT NULL;

-- Check save_pct is 0-1 (decimal format)
SELECT MIN(save_pct), MAX(save_pct)
FROM fact_goalie_game_stats
WHERE save_pct IS NOT NULL;

-- Check period values are valid (1-4)
SELECT DISTINCT period
FROM fact_events
ORDER BY period;

-- Check for negative stats (should not exist)
SELECT 'Negative goals' as issue, COUNT(*)
FROM fact_player_game_stats WHERE goals < 0
UNION ALL
SELECT 'Negative assists', COUNT(*)
FROM fact_player_game_stats WHERE assists < 0
UNION ALL
SELECT 'Negative shots', COUNT(*)
FROM fact_player_game_stats WHERE shots < 0;

-- ============================================
-- BUSINESS LOGIC VALIDATION
-- ============================================

-- Points should equal goals + assists
SELECT player_game_key, goals, assists, points
FROM fact_player_game_stats
WHERE points != (goals + assists);

-- Team goals should match schedule
SELECT s.game_id, s.home_score, s.away_score,
       h.goals as home_calc, a.goals as away_calc
FROM dim_schedule s
JOIN fact_team_game_stats h ON s.game_id = h.game_id AND h.venue = 'Home'
JOIN fact_team_game_stats a ON s.game_id = a.game_id AND a.venue = 'Away'
WHERE s.home_score != h.goals OR s.away_score != a.goals;

-- FO wins + losses should be roughly equal league-wide
SELECT SUM(fo_wins) as total_wins, SUM(fo_losses) as total_losses
FROM fact_player_game_stats;

-- ============================================
-- SAMPLE DATA QUERIES (Test functionality)
-- ============================================

-- Top 10 scorers
SELECT player_name, 
       SUM(goals) as goals,
       SUM(assists) as assists,
       SUM(points) as points
FROM fact_player_game_stats
GROUP BY player_name
ORDER BY points DESC
LIMIT 10;

-- Team standings
SELECT 
    CASE 
        WHEN home_score > away_score THEN home_team 
        ELSE away_team 
    END as winner,
    COUNT(*) as wins
FROM dim_schedule
WHERE status = 'Final'
GROUP BY winner
ORDER BY wins DESC;

-- Goalie stats
SELECT player_name, team_name,
       SUM(saves) as saves,
       SUM(goals_against) as ga,
       ROUND(SUM(saves)::numeric / NULLIF(SUM(shots_against), 0), 3) as save_pct
FROM fact_goalie_game_stats
GROUP BY player_name, team_name
ORDER BY save_pct DESC;

-- ============================================
-- END OF VALIDATION
-- ============================================
