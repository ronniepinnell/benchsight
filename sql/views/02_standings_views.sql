-- ============================================================================
-- STANDINGS VIEWS - Team standings and rankings
-- v29.0: Added ties column, game_type filter (defaults to 'All')
-- ============================================================================

-- Current Season Standings (most recent season, all game types combined)
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

-- Current Season Standings - Regular Season Only
CREATE OR REPLACE VIEW v_standings_current_regular AS
WITH latest_season AS (
    SELECT season_id FROM fact_team_season_stats_basic 
    WHERE game_type = 'Regular'
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
WHERE t.game_type = 'Regular'
ORDER BY t.points DESC, t.wins DESC, t.goal_diff DESC;

-- Current Season Standings - Playoffs Only
CREATE OR REPLACE VIEW v_standings_current_playoffs AS
WITH latest_season AS (
    SELECT season_id FROM fact_team_season_stats_basic 
    WHERE game_type = 'Playoffs'
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
WHERE t.game_type = 'Playoffs'
ORDER BY t.points DESC, t.wins DESC, t.goal_diff DESC;

-- All Seasons Standings (game_type = 'All' for combined stats)
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

-- All Seasons Standings - By Game Type (filterable)
CREATE OR REPLACE VIEW v_standings_by_game_type AS
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
    RANK() OVER (PARTITION BY season_id, game_type ORDER BY points DESC, wins DESC, goal_diff DESC) as standing
FROM fact_team_season_stats_basic
ORDER BY season DESC, game_type, points DESC;

-- Team Historical Performance (all-time, aggregated across seasons)
CREATE OR REPLACE VIEW v_standings_team_history AS
SELECT 
    team_id,
    team_name,
    COUNT(DISTINCT season_id) as seasons,
    SUM(games_played) as total_games,
    SUM(wins) as total_wins,
    SUM(losses) as total_losses,
    SUM(ties) as total_ties,
    SUM(points) as total_points,
    SUM(goals_for) as total_gf,
    SUM(goals_against) as total_ga,
    ROUND(SUM(wins)::numeric / NULLIF(SUM(games_played), 0) * 100, 1) as all_time_win_pct,
    ROUND(SUM(goals_for)::numeric / NULLIF(SUM(games_played), 0), 2) as all_time_gf_per_game
FROM fact_team_season_stats_basic
WHERE game_type = 'All'
GROUP BY team_id, team_name
ORDER BY total_points DESC;

-- Head-to-Head Records (from schedule)
CREATE OR REPLACE VIEW v_standings_h2h AS
SELECT 
    home_team_name as team1,
    away_team_name as team2,
    COUNT(*) as games_played,
    SUM(CASE WHEN home_total_goals > away_total_goals THEN 1 ELSE 0 END) as team1_wins,
    SUM(CASE WHEN away_total_goals > home_total_goals THEN 1 ELSE 0 END) as team2_wins,
    SUM(CASE WHEN home_total_goals = away_total_goals THEN 1 ELSE 0 END) as ties,
    SUM(home_total_goals) as team1_goals,
    SUM(away_total_goals) as team2_goals
FROM dim_schedule
WHERE home_total_goals IS NOT NULL
GROUP BY home_team_name, away_team_name
HAVING COUNT(*) > 0
ORDER BY games_played DESC;
