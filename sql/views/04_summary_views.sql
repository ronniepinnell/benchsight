-- ============================================================================
-- SUMMARY VIEWS - Aggregated totals (replace ETL snapshot tables)
-- ============================================================================

-- League Summary (replaces fact_season_summary)
CREATE OR REPLACE VIEW v_summary_league AS
SELECT 
    season_id,
    season,
    COUNT(DISTINCT player_id) as total_players,
    COUNT(DISTINCT team_id) as total_teams,
    SUM(games_played) as total_player_games,
    SUM(goals) as total_goals,
    SUM(assists) as total_assists,
    SUM(points) as total_points,
    SUM(pim) as total_pim,
    ROUND(AVG(goals_per_game)::numeric, 2) as avg_goals_per_game,
    ROUND(AVG(points_per_game)::numeric, 2) as avg_points_per_game,
    MAX(goals) as max_goals,
    MAX(points) as max_points
FROM fact_player_season_stats_basic
GROUP BY season_id, season
ORDER BY season DESC;

-- Team Season Summary
CREATE OR REPLACE VIEW v_summary_team_season AS
SELECT 
    t.team_id,
    t.team_name,
    t.season_id,
    t.season,
    t.games_played,
    t.wins,
    t.losses,
    t.win_pct,
    t.goals_for,
    t.goals_against,
    t.goal_diff,
    t.goals_for_per_game,
    t.goals_against_per_game,
    -- Add roster stats
    COUNT(DISTINCT p.player_id) as roster_size,
    SUM(p.goals) as team_total_goals,
    SUM(p.assists) as team_total_assists,
    MAX(p.points) as top_scorer_points
FROM fact_team_season_stats_basic t
LEFT JOIN fact_player_season_stats_basic p 
    ON t.team_id = p.team_id AND t.season_id = p.season_id
GROUP BY t.team_id, t.team_name, t.season_id, t.season, 
         t.games_played, t.wins, t.losses, t.win_pct,
         t.goals_for, t.goals_against, t.goal_diff,
         t.goals_for_per_game, t.goals_against_per_game
ORDER BY t.season DESC, t.wins DESC;

-- Player Career Summary (replaces fact_player_career_stats)
CREATE OR REPLACE VIEW v_summary_player_career AS
SELECT 
    player_id,
    player_name,
    current_team,
    position,
    seasons_played,
    career_games,
    career_goals,
    career_assists,
    career_points,
    career_pim,
    goals_per_game,
    assists_per_game,
    points_per_game,
    pim_per_game,
    -- Milestones
    CASE WHEN career_goals >= 100 THEN true ELSE false END as century_goals,
    CASE WHEN career_points >= 200 THEN true ELSE false END as bicentennial_points,
    CASE WHEN career_games >= 100 THEN true ELSE false END as hundred_games
FROM fact_player_career_stats_basic
ORDER BY career_points DESC;

-- Goalie Career Summary
CREATE OR REPLACE VIEW v_summary_goalie_career AS
SELECT 
    player_id,
    player_name,
    current_team,
    seasons_played,
    career_games,
    career_wins,
    career_losses,
    career_goals_against,
    career_gaa,
    career_shutouts,
    career_win_pct,
    career_shutout_pct,
    CASE WHEN career_wins >= 50 THEN true ELSE false END as fifty_wins,
    CASE WHEN career_shutouts >= 10 THEN true ELSE false END as ten_shutouts
FROM fact_goalie_career_stats_basic
ORDER BY career_wins DESC;

-- Game Day Summary (for a specific game)
CREATE OR REPLACE VIEW v_summary_game AS
SELECT 
    s.game_id,
    s.date,
    s.home_team_name,
    s.away_team_name,
    s.home_total_goals,
    s.away_total_goals,
    CASE 
        WHEN s.home_total_goals > s.away_total_goals THEN s.home_team_name
        ELSE s.away_team_name 
    END as winner,
    s.home_team_period1_goals || '-' || s.away_team_period1_goals as p1_score,
    s.home_team_period2_goals || '-' || s.away_team_period2_goals as p2_score,
    s.home_team_period3_goals || '-' || s.away_team_period3_goals as p3_score
FROM dim_schedule s
WHERE s.home_total_goals IS NOT NULL
ORDER BY s.date DESC;

-- Position Summary by Season
CREATE OR REPLACE VIEW v_summary_by_position AS
SELECT 
    season_id,
    season,
    position,
    COUNT(DISTINCT player_id) as player_count,
    SUM(games_played) as total_games,
    SUM(goals) as total_goals,
    SUM(assists) as total_assists,
    SUM(points) as total_points,
    ROUND(AVG(goals_per_game)::numeric, 2) as avg_goals_per_game,
    ROUND(AVG(points_per_game)::numeric, 2) as avg_points_per_game
FROM fact_player_season_stats_basic
GROUP BY season_id, season, position
ORDER BY season DESC, position;
