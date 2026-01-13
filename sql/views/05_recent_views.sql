-- ============================================================================
-- RECENT VIEWS - Latest games, recent performance
-- ============================================================================

-- Recent Games (last 20)
CREATE OR REPLACE VIEW v_recent_games AS
SELECT 
    game_id,
    date,
    season,
    home_team_name,
    away_team_name,
    home_total_goals,
    away_total_goals,
    home_total_goals || '-' || away_total_goals as score,
    CASE 
        WHEN home_total_goals > away_total_goals THEN home_team_name
        WHEN away_total_goals > home_total_goals THEN away_team_name
        ELSE 'Tie'
    END as winner,
    ABS(home_total_goals - away_total_goals) as goal_diff
FROM dim_schedule
WHERE home_total_goals IS NOT NULL
ORDER BY date DESC
LIMIT 20;

-- Recent Player Performances (from tracked games)
CREATE OR REPLACE VIEW v_recent_player_games AS
SELECT 
    pg.game_id,
    pg.player_id,
    pg.player_name,
    pg.team_name,
    pg.position,
    s.date,
    pg.goals,
    pg.assists,
    pg.points,
    pg.shots,
    pg.sog,
    pg.toi,
    pg.game_score
FROM fact_player_game_stats pg
JOIN dim_schedule s ON pg.game_id = s.game_id
ORDER BY s.date DESC, pg.points DESC;

-- Recent Goalie Performances
CREATE OR REPLACE VIEW v_recent_goalie_games AS
SELECT 
    gg.game_id,
    gg.player_id,
    gg.player_name,
    gg.team_name,
    gg.venue,
    s.date,
    gg.saves,
    gg.goals_against,
    gg.shots_against,
    gg.save_pct,
    gg.is_quality_start,
    gg.overall_game_rating,
    gg.goalie_war
FROM fact_goalie_game_stats gg
JOIN dim_schedule s ON gg.game_id = s.game_id
ORDER BY s.date DESC;

-- Hot Players (last 5 games performance) - placeholder for tracked data
CREATE OR REPLACE VIEW v_recent_hot_players AS
SELECT 
    player_id,
    player_name,
    team_name,
    COUNT(*) as games,
    SUM(goals) as goals,
    SUM(assists) as assists,
    SUM(points) as points,
    ROUND(AVG(game_score)::numeric, 2) as avg_game_score
FROM fact_player_game_stats
GROUP BY player_id, player_name, team_name
HAVING COUNT(*) >= 2
ORDER BY SUM(points) DESC, AVG(game_score) DESC
LIMIT 10;

-- Recent High-Scoring Games
CREATE OR REPLACE VIEW v_recent_high_scoring AS
SELECT 
    game_id,
    date,
    home_team_name,
    away_team_name,
    home_total_goals,
    away_total_goals,
    (home_total_goals + away_total_goals) as total_goals,
    home_total_goals || '-' || away_total_goals as score
FROM dim_schedule
WHERE home_total_goals IS NOT NULL
ORDER BY (home_total_goals + away_total_goals) DESC
LIMIT 20;

-- Team Recent Form (from schedule - last 5 results per team)
CREATE OR REPLACE VIEW v_recent_team_form AS
WITH team_games AS (
    SELECT 
        home_team_name as team_name,
        date,
        CASE WHEN home_total_goals > away_total_goals THEN 'W' 
             WHEN home_total_goals < away_total_goals THEN 'L'
             ELSE 'T' END as result,
        home_total_goals as gf,
        away_total_goals as ga
    FROM dim_schedule WHERE home_total_goals IS NOT NULL
    UNION ALL
    SELECT 
        away_team_name as team_name,
        date,
        CASE WHEN away_total_goals > home_total_goals THEN 'W' 
             WHEN away_total_goals < home_total_goals THEN 'L'
             ELSE 'T' END as result,
        away_total_goals as gf,
        home_total_goals as ga
    FROM dim_schedule WHERE home_total_goals IS NOT NULL
),
ranked AS (
    SELECT 
        team_name,
        date,
        result,
        gf,
        ga,
        ROW_NUMBER() OVER (PARTITION BY team_name ORDER BY date DESC) as game_num
    FROM team_games
)
SELECT 
    team_name,
    STRING_AGG(result, '' ORDER BY game_num) as last_5_form,
    SUM(CASE WHEN result = 'W' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN result = 'L' THEN 1 ELSE 0 END) as losses,
    SUM(gf) as goals_for,
    SUM(ga) as goals_against
FROM ranked
WHERE game_num <= 5
GROUP BY team_name
ORDER BY wins DESC;
