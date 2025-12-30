-- BenchSight Data Validation Queries
-- Run after loading all data to verify integrity

-- ============================================
-- 1. ROW COUNT VALIDATION
-- ============================================

SELECT 'Row Count Validation' as section;

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

-- Expected counts (from CSV analysis):
-- dim_player: 337
-- dim_team: 26
-- dim_schedule: 562
-- fact_shifts: 672
-- fact_events: 5833
-- fact_events_player: 11635
-- fact_shifts_player: 4626
-- fact_player_game_stats: 107
-- fact_team_game_stats: 8
-- fact_goalie_game_stats: 8
-- fact_h2h: 684
-- fact_wowy: 641

-- ============================================
-- 2. PRIMARY KEY DUPLICATE CHECK
-- ============================================

SELECT 'Primary Key Duplicates Check' as section;

-- Check for duplicate primary keys in each table
SELECT 'fact_events' as tbl, event_key, COUNT(*) as cnt
FROM fact_events GROUP BY event_key HAVING COUNT(*) > 1
UNION ALL
SELECT 'fact_shifts', shift_key, COUNT(*)
FROM fact_shifts GROUP BY shift_key HAVING COUNT(*) > 1
UNION ALL
SELECT 'fact_player_game_stats', player_game_key, COUNT(*)
FROM fact_player_game_stats GROUP BY player_game_key HAVING COUNT(*) > 1
UNION ALL
SELECT 'fact_team_game_stats', team_game_key, COUNT(*)
FROM fact_team_game_stats GROUP BY team_game_key HAVING COUNT(*) > 1
UNION ALL
SELECT 'fact_h2h', h2h_key, COUNT(*)
FROM fact_h2h GROUP BY h2h_key HAVING COUNT(*) > 1
UNION ALL
SELECT 'fact_wowy', wowy_key, COUNT(*)
FROM fact_wowy GROUP BY wowy_key HAVING COUNT(*) > 1;

-- ============================================
-- 3. FOREIGN KEY VALIDATION
-- ============================================

SELECT 'Foreign Key Validation' as section;

-- Events referencing non-existent games
SELECT 'fact_events -> dim_schedule' as relationship, COUNT(*) as orphan_count
FROM fact_events e
LEFT JOIN dim_schedule s ON e.game_id = s.game_id
WHERE s.game_id IS NULL

UNION ALL

-- Events referencing non-existent shifts
SELECT 'fact_events -> fact_shifts', COUNT(*)
FROM fact_events e
LEFT JOIN fact_shifts s ON e.shift_key = s.shift_key
WHERE e.shift_key IS NOT NULL AND s.shift_key IS NULL

UNION ALL

-- Events_player referencing non-existent players
SELECT 'fact_events_player -> dim_player', COUNT(*)
FROM fact_events_player ep
LEFT JOIN dim_player p ON ep.player_id = p.player_id
WHERE ep.player_id IS NOT NULL AND p.player_id IS NULL

UNION ALL

-- Player stats referencing non-existent players
SELECT 'fact_player_game_stats -> dim_player', COUNT(*)
FROM fact_player_game_stats ps
LEFT JOIN dim_player p ON ps.player_id = p.player_id
WHERE p.player_id IS NULL

UNION ALL

-- Team stats referencing non-existent teams
SELECT 'fact_team_game_stats -> dim_team', COUNT(*)
FROM fact_team_game_stats ts
LEFT JOIN dim_team t ON ts.team_id = t.team_id
WHERE ts.team_id IS NOT NULL AND t.team_id IS NULL;

-- ============================================
-- 4. DATA RANGE VALIDATION
-- ============================================

SELECT 'Data Range Validation' as section;

-- Check percentage values are reasonable (0-100 for most, 0-1 for some)
SELECT 'shooting_pct range' as metric, 
       MIN(shooting_pct) as min_val, 
       MAX(shooting_pct) as max_val,
       AVG(shooting_pct) as avg_val
FROM fact_player_game_stats
WHERE shooting_pct IS NOT NULL
UNION ALL
SELECT 'fo_pct range', MIN(fo_pct), MAX(fo_pct), AVG(fo_pct)
FROM fact_player_game_stats
WHERE fo_pct IS NOT NULL
UNION ALL
SELECT 'pass_pct range', MIN(pass_pct), MAX(pass_pct), AVG(pass_pct)
FROM fact_player_game_stats
WHERE pass_pct IS NOT NULL
UNION ALL
SELECT 'save_pct range', MIN(save_pct), MAX(save_pct), AVG(save_pct)
FROM fact_goalie_game_stats
WHERE save_pct IS NOT NULL;

-- Check for negative counts (should not exist)
SELECT 'Negative value check' as section;

SELECT 'Negative goals' as issue, COUNT(*) as count
FROM fact_player_game_stats WHERE goals < 0
UNION ALL
SELECT 'Negative assists', COUNT(*)
FROM fact_player_game_stats WHERE assists < 0
UNION ALL
SELECT 'Negative shots', COUNT(*)
FROM fact_player_game_stats WHERE shots < 0
UNION ALL
SELECT 'Negative saves', COUNT(*)
FROM fact_goalie_game_stats WHERE saves < 0;

-- ============================================
-- 5. BUSINESS LOGIC VALIDATION
-- ============================================

SELECT 'Business Logic Validation' as section;

-- Points should equal goals + assists
SELECT 'Points mismatch' as issue, 
       player_game_key, 
       goals, 
       assists, 
       points,
       (goals + assists) as expected_points
FROM fact_player_game_stats
WHERE points != (goals + assists)
LIMIT 10;

-- Games in fact tables should exist in schedule
SELECT 'Untracked games in events' as check_name, COUNT(DISTINCT e.game_id) as count
FROM fact_events e
WHERE e.game_id NOT IN (SELECT game_id FROM dim_schedule);

-- ============================================
-- 6. DATA SUMMARY
-- ============================================

SELECT 'Data Summary' as section;

-- Games with tracking data
SELECT 'Games with event tracking' as metric, COUNT(DISTINCT game_id) as count
FROM fact_events
UNION ALL
SELECT 'Games with shift data', COUNT(DISTINCT game_id) FROM fact_shifts
UNION ALL
SELECT 'Games with player stats', COUNT(DISTINCT game_id) FROM fact_player_game_stats
UNION ALL
SELECT 'Total games in schedule', COUNT(*) FROM dim_schedule;

-- Events per game
SELECT 'Events per game' as metric,
       MIN(cnt) as min_events,
       MAX(cnt) as max_events,
       ROUND(AVG(cnt), 0) as avg_events
FROM (SELECT game_id, COUNT(*) as cnt FROM fact_events GROUP BY game_id) sub;

-- ============================================
-- 7. SAMPLE QUERIES (Test functionality)
-- ============================================

-- Top 10 scorers across all games
SELECT 'Top 10 Scorers' as query;
SELECT player_name, 
       SUM(goals) as goals,
       SUM(assists) as assists,
       SUM(points) as points,
       COUNT(*) as games_played
FROM fact_player_game_stats
GROUP BY player_name
ORDER BY points DESC
LIMIT 10;

-- Goalie stats
SELECT 'Goalie Stats' as query;
SELECT player_name, 
       team_name,
       SUM(saves) as total_saves,
       SUM(goals_against) as total_ga,
       SUM(shots_against) as total_sa,
       ROUND(SUM(saves)::numeric / NULLIF(SUM(shots_against), 0), 3) as overall_sv_pct
FROM fact_goalie_game_stats
GROUP BY player_name, team_name
ORDER BY overall_sv_pct DESC;

-- Team performance by game
SELECT 'Team Performance' as query;
SELECT s.game_id,
       s.date,
       ts.team_name,
       ts.venue,
       ts.goals,
       ts.shots,
       ts.shooting_pct
FROM fact_team_game_stats ts
JOIN dim_schedule s ON ts.game_id = s.game_id
ORDER BY s.date DESC, s.game_id;

-- ============================================
-- END OF VALIDATION
-- ============================================
