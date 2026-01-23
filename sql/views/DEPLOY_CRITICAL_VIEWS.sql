-- ============================================================================
-- CRITICAL VIEWS - Minimum views required for core dashboard pages
-- Run this in Supabase SQL Editor to fix 500 errors on:
--   /norad/standings, /norad/teams, /norad/players, /norad/goalies, /norad/leaders
-- ============================================================================

-- Drop existing views first (required when changing column types)
DROP VIEW IF EXISTS v_standings_current CASCADE;
DROP VIEW IF EXISTS v_standings_all_seasons CASCADE;
DROP VIEW IF EXISTS v_summary_league CASCADE;
DROP VIEW IF EXISTS v_rankings_players_current CASCADE;
DROP VIEW IF EXISTS v_rankings_goalies_current CASCADE;
DROP VIEW IF EXISTS v_leaderboard_points CASCADE;
DROP VIEW IF EXISTS v_leaderboard_goalie_wins CASCADE;
DROP VIEW IF EXISTS v_leaderboard_goalie_gaa CASCADE;

-- 1. v_standings_current (used by Standings, Teams pages)
CREATE OR REPLACE VIEW v_standings_current AS
WITH latest_season AS (
    SELECT season_id FROM fact_team_season_stats_basic
    WHERE game_type = 'All'
    ORDER BY season DESC LIMIT 1
)
SELECT
    t.team_id,
    t.team_name,
    t.season,
    t.season_id,
    t.game_type,
    t.games_played,
    t.wins,
    t.losses,
    t.ties,
    t.points,
    t.goals_for,
    t.goals_against,
    t.goal_diff,
    t.goals_for_per_game,
    t.goals_against_per_game,
    t.win_pct,
    RANK() OVER (ORDER BY t.points DESC, t.wins DESC, t.goal_diff DESC) as standing
FROM fact_team_season_stats_basic t
JOIN latest_season ls ON t.season_id = ls.season_id
WHERE t.game_type = 'All'
ORDER BY t.points DESC, t.wins DESC, t.goal_diff DESC;

-- 2. v_standings_all_seasons (used by Players page season filter)
CREATE OR REPLACE VIEW v_standings_all_seasons AS
SELECT
    team_id,
    team_name,
    season,
    season_id,
    game_type,
    games_played,
    wins,
    losses,
    ties,
    points,
    goals_for,
    goals_against,
    goal_diff,
    win_pct,
    RANK() OVER (PARTITION BY season_id ORDER BY points DESC, wins DESC, goal_diff DESC) as standing
FROM fact_team_season_stats_basic
WHERE game_type = 'All'
ORDER BY season DESC, points DESC;

-- 3. v_summary_league (used by Standings page stats cards)
CREATE OR REPLACE VIEW v_summary_league AS
WITH latest_season AS (
    SELECT season_id, season FROM fact_player_season_stats_basic
    ORDER BY season DESC LIMIT 1
)
SELECT
    ls.season_id,
    ls.season,
    COUNT(DISTINCT p.player_id) as total_players,
    COUNT(DISTINCT p.team_id) as total_teams,
    (SELECT COUNT(*) FROM dim_schedule WHERE season_id = ls.season_id AND home_total_goals IS NOT NULL) as total_games,
    SUM(p.goals) as total_goals,
    SUM(p.assists) as total_assists,
    SUM(p.points) as total_points,
    SUM(p.pim) as total_pim,
    ROUND(AVG(p.goals_per_game)::numeric, 2) as avg_goals_per_game,
    ROUND(AVG(p.points_per_game)::numeric, 2) as avg_points_per_game,
    MAX(p.goals) as max_goals,
    MAX(p.points) as max_points
FROM fact_player_season_stats_basic p
JOIN latest_season ls ON p.season_id = ls.season_id
GROUP BY ls.season_id, ls.season;

-- 4. v_rankings_players_current (used by Players page)
-- Note: Player stats don't have game_type='All', so we aggregate Regular+Playoffs
CREATE OR REPLACE VIEW v_rankings_players_current AS
WITH latest_season AS (
    SELECT season_id FROM fact_player_season_stats_basic
    ORDER BY season DESC LIMIT 1
),
aggregated AS (
    SELECT
        p.player_id,
        p.player_name,
        p.team_id,
        p.team_name,
        p.position,
        p.season_id,
        SUM(p.games_played) as games_played,
        SUM(p.goals) as goals,
        SUM(p.assists) as assists,
        SUM(p.points) as points,
        SUM(p.pim) as pim,
        ROUND(SUM(p.points)::numeric / NULLIF(SUM(p.games_played), 0), 2) as points_per_game,
        ROUND(SUM(p.goals)::numeric / NULLIF(SUM(p.games_played), 0), 2) as goals_per_game
    FROM fact_player_season_stats_basic p
    JOIN latest_season ls ON p.season_id = ls.season_id
    GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.position, p.season_id
)
SELECT
    a.*,
    RANK() OVER (ORDER BY a.points DESC) as points_rank,
    RANK() OVER (ORDER BY a.goals DESC) as goals_rank,
    RANK() OVER (ORDER BY a.assists DESC) as assists_rank,
    RANK() OVER (ORDER BY a.points_per_game DESC) as ppg_rank
FROM aggregated a
WHERE a.games_played >= 1
ORDER BY a.points DESC;

-- 5. v_rankings_goalies_current (used by Goalies page)
-- Note: Aggregates Regular+Playoffs per goalie
CREATE OR REPLACE VIEW v_rankings_goalies_current AS
WITH latest_season AS (
    SELECT season_id FROM fact_goalie_season_stats_basic
    ORDER BY season DESC LIMIT 1
),
aggregated AS (
    SELECT
        g.player_id,
        g.player_name,
        g.team_name,
        g.season_id,
        SUM(g.games_played) as games_played,
        SUM(g.wins) as wins,
        SUM(g.losses) as losses,
        SUM(g.ties) as ties,
        SUM(g.goals_against) as goals_against,
        ROUND(SUM(g.goals_against)::numeric / NULLIF(SUM(g.games_played), 0), 2) as gaa,
        SUM(g.shutouts) as shutouts,
        ROUND(SUM(g.shutouts)::numeric / NULLIF(SUM(g.games_played), 0) * 100, 1) as shutout_pct,
        ROUND(SUM(g.wins)::numeric / NULLIF(SUM(g.games_played), 0) * 100, 1) as win_pct
    FROM fact_goalie_season_stats_basic g
    JOIN latest_season ls ON g.season_id = ls.season_id
    GROUP BY g.player_id, g.player_name, g.team_name, g.season_id
)
SELECT
    a.*,
    RANK() OVER (ORDER BY a.wins DESC) as wins_rank,
    RANK() OVER (ORDER BY a.gaa ASC) as gaa_rank,
    RANK() OVER (ORDER BY a.win_pct DESC) as win_pct_rank,
    RANK() OVER (ORDER BY a.shutouts DESC) as shutout_rank
FROM aggregated a
WHERE a.games_played >= 1
ORDER BY a.wins DESC;

-- 6. v_leaderboard_points (used by Leaders page)
-- Note: Aggregates Regular+Playoffs per player per season
CREATE OR REPLACE VIEW v_leaderboard_points AS
WITH aggregated AS (
    SELECT
        player_id,
        player_name,
        team_name,
        season,
        season_id,
        'All' as game_type,
        SUM(games_played) as games_played,
        SUM(goals) as goals,
        SUM(assists) as assists,
        SUM(points) as points,
        ROUND(SUM(points)::numeric / NULLIF(SUM(games_played), 0), 2) as points_per_game
    FROM fact_player_season_stats_basic
    GROUP BY player_id, player_name, team_name, season, season_id
)
SELECT
    a.*,
    RANK() OVER (PARTITION BY a.season_id ORDER BY a.points DESC) as season_rank,
    RANK() OVER (ORDER BY a.points DESC) as overall_rank
FROM aggregated a
WHERE a.games_played >= 1
ORDER BY a.points DESC;

-- 7. v_leaderboard_goalie_wins (used by Leaders, Goalies pages)
-- Note: Aggregates Regular+Playoffs per goalie per season
CREATE OR REPLACE VIEW v_leaderboard_goalie_wins AS
WITH aggregated AS (
    SELECT
        player_id,
        player_name,
        team_name,
        season,
        season_id,
        'All' as game_type,
        SUM(games_played) as games_played,
        SUM(wins) as wins,
        SUM(losses) as losses,
        SUM(ties) as ties,
        ROUND(SUM(wins)::numeric / NULLIF(SUM(games_played), 0) * 100, 1) as win_pct,
        ROUND(SUM(goals_against)::numeric / NULLIF(SUM(games_played), 0), 2) as gaa
    FROM fact_goalie_season_stats_basic
    GROUP BY player_id, player_name, team_name, season, season_id
)
SELECT
    a.*,
    RANK() OVER (PARTITION BY a.season_id ORDER BY a.wins DESC) as season_rank
FROM aggregated a
WHERE a.games_played >= 1
ORDER BY a.wins DESC;

-- 8. v_leaderboard_goalie_gaa (used by Leaders, Goalies pages)
-- Note: Aggregates Regular+Playoffs per goalie per season
CREATE OR REPLACE VIEW v_leaderboard_goalie_gaa AS
WITH aggregated AS (
    SELECT
        player_id,
        player_name,
        team_name,
        season,
        season_id,
        'All' as game_type,
        SUM(games_played) as games_played,
        ROUND(SUM(goals_against)::numeric / NULLIF(SUM(games_played), 0), 2) as gaa,
        SUM(goals_against) as goals_against,
        SUM(wins) as wins,
        SUM(losses) as losses,
        SUM(ties) as ties,
        ROUND(SUM(wins)::numeric / NULLIF(SUM(games_played), 0) * 100, 1) as win_pct,
        SUM(shutouts) as shutouts,
        ROUND(SUM(shutouts)::numeric / NULLIF(SUM(games_played), 0) * 100, 1) as shutout_pct
    FROM fact_goalie_season_stats_basic
    GROUP BY player_id, player_name, team_name, season, season_id
)
SELECT
    a.*,
    RANK() OVER (PARTITION BY a.season_id ORDER BY a.gaa ASC) as season_rank
FROM aggregated a
WHERE a.games_played >= 3
ORDER BY a.gaa ASC;

-- ============================================================================
-- Verification: Run these queries to confirm views work
-- ============================================================================
-- SELECT COUNT(*) FROM v_standings_current;
-- SELECT COUNT(*) FROM v_standings_all_seasons;
-- SELECT COUNT(*) FROM v_summary_league;
-- SELECT COUNT(*) FROM v_rankings_players_current;
-- SELECT COUNT(*) FROM v_rankings_goalies_current;
-- SELECT COUNT(*) FROM v_leaderboard_points;
-- SELECT COUNT(*) FROM v_leaderboard_goalie_wins;
-- SELECT COUNT(*) FROM v_leaderboard_goalie_gaa;
