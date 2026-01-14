-- Script to explore available player statistics
-- Run these queries in Supabase SQL Editor to understand what stats are available

-- ============================================
-- 1. See all columns in fact_player_game_stats
-- ============================================
SELECT 
  column_name, 
  data_type,
  is_nullable
FROM information_schema.columns 
WHERE table_name = 'fact_player_game_stats'
ORDER BY ordinal_position;

-- ============================================
-- 2. Get sample data for a specific player
-- ============================================
SELECT * 
FROM fact_player_game_stats 
WHERE player_id = 'P100001' 
ORDER BY game_id DESC
LIMIT 5;

-- ============================================
-- 3. Check data availability for key stats
-- ============================================
SELECT 
  COUNT(*) as total_records,
  COUNT(DISTINCT player_id) as unique_players,
  COUNT(goals) as has_goals,
  COUNT(assists) as has_assists,
  COUNT(primary_assists) as has_primary_assists,
  COUNT(secondary_assists) as has_secondary_assists,
  COUNT(corsi_for) as has_corsi,
  COUNT(fenwick_for) as has_fenwick,
  COUNT(war) as has_war,
  COUNT(gar) as has_gar,
  COUNT(zone_entries) as has_zone_entries,
  COUNT(pass_attempts) as has_passing,
  COUNT(toi_seconds) as has_toi,
  COUNT(plus_minus_ev) as has_plus_minus_ev
FROM fact_player_game_stats;

-- ============================================
-- 4. Check data quality - verify calculations
-- ============================================
-- Check if assists = primary + secondary
SELECT 
  player_id,
  game_id,
  assists,
  primary_assists,
  secondary_assists,
  (primary_assists + secondary_assists) as calculated_assists,
  assists - (primary_assists + secondary_assists) as difference
FROM fact_player_game_stats
WHERE assists != (primary_assists + secondary_assists)
LIMIT 10;

-- Check if points = goals + assists
SELECT 
  player_id,
  game_id,
  goals,
  assists,
  points,
  (goals + assists) as calculated_points,
  points - (goals + assists) as difference
FROM fact_player_game_stats
WHERE points != (goals + assists)
LIMIT 10;

-- ============================================
-- 5. Find stats with good data coverage
-- ============================================
SELECT 
  'goals' as stat_name,
  COUNT(*) as total,
  COUNT(goals) as has_data,
  ROUND(100.0 * COUNT(goals) / COUNT(*), 2) as pct_coverage,
  AVG(goals) as avg_value,
  MAX(goals) as max_value
FROM fact_player_game_stats
UNION ALL
SELECT 
  'primary_assists',
  COUNT(*),
  COUNT(primary_assists),
  ROUND(100.0 * COUNT(primary_assists) / COUNT(*), 2),
  AVG(primary_assists),
  MAX(primary_assists)
FROM fact_player_game_stats
UNION ALL
SELECT 
  'corsi_for',
  COUNT(*),
  COUNT(corsi_for),
  ROUND(100.0 * COUNT(corsi_for) / COUNT(*), 2),
  AVG(corsi_for),
  MAX(corsi_for)
FROM fact_player_game_stats
UNION ALL
SELECT 
  'zone_entries',
  COUNT(*),
  COUNT(zone_entries),
  ROUND(100.0 * COUNT(zone_entries) / COUNT(*), 2),
  AVG(zone_entries),
  MAX(zone_entries)
FROM fact_player_game_stats
UNION ALL
SELECT 
  'pass_attempts',
  COUNT(*),
  COUNT(pass_attempts),
  ROUND(100.0 * COUNT(pass_attempts) / COUNT(*), 2),
  AVG(pass_attempts),
  MAX(pass_attempts)
FROM fact_player_game_stats
UNION ALL
SELECT 
  'plus_minus_ev',
  COUNT(*),
  COUNT(plus_minus_ev),
  ROUND(100.0 * COUNT(plus_minus_ev) / COUNT(*), 2),
  AVG(plus_minus_ev),
  MAX(plus_minus_ev)
FROM fact_player_game_stats
ORDER BY pct_coverage DESC;

-- ============================================
-- 6. See what stats are in season aggregates
-- ============================================
SELECT column_name, data_type
FROM information_schema.columns 
WHERE table_name = 'fact_player_season_stats_basic'
ORDER BY ordinal_position;

-- ============================================
-- 7. Compare game-level vs season-level stats
-- ============================================
-- This shows what's available at each level
SELECT 
  'Game Level' as level,
  COUNT(DISTINCT column_name) as unique_stats
FROM information_schema.columns 
WHERE table_name = 'fact_player_game_stats'
UNION ALL
SELECT 
  'Season Level',
  COUNT(DISTINCT column_name)
FROM information_schema.columns 
WHERE table_name = 'fact_player_season_stats_basic';

-- ============================================
-- 8. Find players with complete data
-- ============================================
-- Good for testing - find players with lots of stats populated
SELECT 
  player_id,
  COUNT(*) as games,
  COUNT(goals) as games_with_goals,
  COUNT(corsi_for) as games_with_corsi,
  COUNT(zone_entries) as games_with_zone_entries,
  COUNT(pass_attempts) as games_with_passing,
  COUNT(war) as games_with_war,
  SUM(goals) as total_goals,
  SUM(points) as total_points,
  AVG(cf_pct) as avg_cf_pct,
  AVG(war) as avg_war
FROM fact_player_game_stats
GROUP BY player_id
HAVING COUNT(*) >= 10
  AND COUNT(corsi_for) > 0
  AND COUNT(zone_entries) > 0
ORDER BY total_points DESC
LIMIT 20;
