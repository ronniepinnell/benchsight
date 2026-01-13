-- ============================================================================
-- BENCHSIGHT VIEWS - AUTO-GENERATED DEPLOY SCRIPT
-- Generated: 2026-01-13T07:37:11.687900
-- Total Views: 59
-- ============================================================================

-- Run this script in Supabase SQL Editor to deploy all views


-- === 01_leaderboard_views.sql ===

CREATE OR REPLACE VIEW v_leaderboard_points AS
SELECT 
    player_id,
    player_name,
    team_name,
    season,
    season_id,
    game_type,
    games_played,
    goals,
    assists,
    points,
    points_per_game,
    RANK() OVER (PARTITION BY season_id ORDER BY points DESC) as season_rank,
    RANK() OVER (ORDER BY points DESC) as overall_rank
FROM fact_player_season_stats_basic
WHERE game_type = 'All' AND games_played >= 1
ORDER BY points DESC;

CREATE OR REPLACE VIEW v_leaderboard_points_by_game_type AS
SELECT 
    player_id,
    player_name,
    team_name,
    season,
    season_id,
    game_type,
    games_played,
    goals,
    assists,
    points,
    points_per_game,
    RANK() OVER (PARTITION BY season_id, game_type ORDER BY points DESC) as rank
FROM fact_player_season_stats_basic
WHERE games_played >= 1
ORDER BY game_type, points DESC;

CREATE OR REPLACE VIEW v_leaderboard_goals AS
SELECT 
    player_id,
    player_name,
    team_name,
    season,
    season_id,
    game_type,
    games_played,
    goals,
    goals_per_game,
    RANK() OVER (PARTITION BY season_id ORDER BY goals DESC) as season_rank
FROM fact_player_season_stats_basic
WHERE game_type = 'All' AND games_played >= 1
ORDER BY goals DESC;

CREATE OR REPLACE VIEW v_leaderboard_assists AS
SELECT 
    player_id,
    player_name,
    team_name,
    season,
    season_id,
    game_type,
    games_played,
    assists,
    assists_per_game,
    RANK() OVER (PARTITION BY season_id ORDER BY assists DESC) as season_rank
FROM fact_player_season_stats_basic
WHERE game_type = 'All' AND games_played >= 1
ORDER BY assists DESC;

CREATE OR REPLACE VIEW v_leaderboard_ppg AS
SELECT 
    player_id,
    player_name,
    team_name,
    season,
    season_id,
    game_type,
    games_played,
    points,
    points_per_game,
    RANK() OVER (PARTITION BY season_id ORDER BY points_per_game DESC) as season_rank
FROM fact_player_season_stats_basic
WHERE game_type = 'All' AND games_played >= 5
ORDER BY points_per_game DESC;

CREATE OR REPLACE VIEW v_leaderboard_pim AS
SELECT 
    player_id,
    player_name,
    team_name,
    season,
    season_id,
    game_type,
    games_played,
    pim,
    pim_per_game,
    RANK() OVER (PARTITION BY season_id ORDER BY pim DESC) as season_rank
FROM fact_player_season_stats_basic
WHERE game_type = 'All' AND games_played >= 1
ORDER BY pim DESC;

CREATE OR REPLACE VIEW v_leaderboard_career_points AS
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
    points_per_game,
    RANK() OVER (ORDER BY career_points DESC) as rank
FROM fact_player_career_stats_basic
WHERE career_games >= 1
ORDER BY career_points DESC;

CREATE OR REPLACE VIEW v_leaderboard_goalie_wins AS
SELECT 
    player_id,
    player_name,
    team_name,
    season,
    season_id,
    game_type,
    games_played,
    wins,
    losses,
    ties,
    win_pct,
    gaa,
    RANK() OVER (PARTITION BY season_id ORDER BY wins DESC) as season_rank
FROM fact_goalie_season_stats_basic
WHERE game_type = 'All' AND games_played >= 1
ORDER BY wins DESC;

CREATE OR REPLACE VIEW v_leaderboard_goalie_wins_by_game_type AS
SELECT 
    player_id,
    player_name,
    team_name,
    season,
    season_id,
    game_type,
    games_played,
    wins,
    losses,
    ties,
    win_pct,
    gaa,
    RANK() OVER (PARTITION BY season_id, game_type ORDER BY wins DESC) as rank
FROM fact_goalie_season_stats_basic
WHERE games_played >= 1
ORDER BY game_type, wins DESC;

CREATE OR REPLACE VIEW v_leaderboard_goalie_gaa AS
SELECT 
    player_id,
    player_name,
    team_name,
    season,
    season_id,
    game_type,
    games_played,
    gaa,
    goals_against,
    wins,
    losses,
    ties,
    win_pct,
    RANK() OVER (PARTITION BY season_id ORDER BY gaa ASC) as season_rank
FROM fact_goalie_season_stats_basic
WHERE game_type = 'All' AND games_played >= 5
ORDER BY gaa ASC;

CREATE OR REPLACE VIEW v_leaderboard_goalie_record AS
SELECT 
    player_id,
    player_name,
    team_name,
    season,
    season_id,
    game_type,
    games_played,
    wins,
    losses,
    ties,
    (wins || '-' || losses || '-' || ties) as record,
    win_pct,
    gaa,
    shutouts,
    RANK() OVER (PARTITION BY season_id ORDER BY wins DESC, gaa ASC) as season_rank
FROM fact_goalie_season_stats_basic
WHERE game_type = 'All' AND games_played >= 1
ORDER BY wins DESC, gaa ASC;


-- === 02_standings_views.sql ===

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


-- === 03_rankings_views.sql ===

CREATE OR REPLACE VIEW v_rankings_players_current AS
WITH latest_season AS (
    SELECT season_id FROM fact_player_season_stats_basic 
    ORDER BY season DESC LIMIT 1
)
SELECT 
    p.player_id,
    p.player_name,
    p.team_name,
    p.position,
    p.games_played,
    p.goals,
    p.assists,
    p.points,
    p.pim,
    p.points_per_game,
    p.goals_per_game,
    RANK() OVER (ORDER BY p.points DESC) as points_rank,
    RANK() OVER (ORDER BY p.goals DESC) as goals_rank,
    RANK() OVER (ORDER BY p.assists DESC) as assists_rank,
    RANK() OVER (ORDER BY p.points_per_game DESC) as ppg_rank
FROM fact_player_season_stats_basic p
JOIN latest_season ls ON p.season_id = ls.season_id
WHERE p.games_played >= 1
ORDER BY p.points DESC;

CREATE OR REPLACE VIEW v_rankings_goalies_current AS
WITH latest_season AS (
    SELECT season_id FROM fact_goalie_season_stats_basic 
    ORDER BY season DESC LIMIT 1
)
SELECT 
    g.player_id,
    g.player_name,
    g.team_name,
    g.games_played,
    g.wins,
    g.losses,
    g.goals_against,
    g.gaa,
    g.shutouts,
    g.win_pct,
    RANK() OVER (ORDER BY g.wins DESC) as wins_rank,
    RANK() OVER (ORDER BY g.gaa ASC) as gaa_rank,
    RANK() OVER (ORDER BY g.win_pct DESC) as win_pct_rank,
    RANK() OVER (ORDER BY g.shutouts DESC) as shutout_rank
FROM fact_goalie_season_stats_basic g
JOIN latest_season ls ON g.season_id = ls.season_id
WHERE g.games_played >= 1
ORDER BY g.wins DESC;

CREATE OR REPLACE VIEW v_rankings_goalies_advanced AS
SELECT 
    player_id,
    player_name,
    team_name,
    games_played,
    saves,
    goals_against,
    save_pct,
    rush_sv_pct,
    set_play_sv_pct,
    rebound_control_rate,
    quality_start_pct,
    season_war,
    RANK() OVER (ORDER BY save_pct DESC) as sv_pct_rank,
    RANK() OVER (ORDER BY rush_sv_pct DESC) as rush_sv_rank,
    RANK() OVER (ORDER BY rebound_control_rate DESC) as rebound_rank,
    RANK() OVER (ORDER BY season_war DESC) as war_rank
FROM fact_goalie_season_stats
WHERE games_played >= 1
ORDER BY save_pct DESC;

CREATE OR REPLACE VIEW v_rankings_career AS
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
    points_per_game,
    RANK() OVER (ORDER BY career_points DESC) as points_rank,
    RANK() OVER (ORDER BY career_goals DESC) as goals_rank,
    RANK() OVER (ORDER BY career_games DESC) as games_rank,
    RANK() OVER (ORDER BY points_per_game DESC) as ppg_rank
FROM fact_player_career_stats_basic
WHERE career_games >= 5
ORDER BY career_points DESC;

CREATE OR REPLACE VIEW v_rankings_goalies_career AS
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
    RANK() OVER (ORDER BY career_wins DESC) as wins_rank,
    RANK() OVER (ORDER BY career_gaa ASC) as gaa_rank,
    RANK() OVER (ORDER BY career_shutouts DESC) as shutout_rank
FROM fact_goalie_career_stats_basic
WHERE career_games >= 3
ORDER BY career_wins DESC;

CREATE OR REPLACE VIEW v_rankings_by_position AS
SELECT 
    player_id,
    player_name,
    team_name,
    position,
    season_id,
    games_played,
    goals,
    assists,
    points,
    points_per_game,
    RANK() OVER (PARTITION BY position, season_id ORDER BY points DESC) as position_rank,
    RANK() OVER (PARTITION BY season_id ORDER BY points DESC) as overall_rank
FROM fact_player_season_stats_basic
WHERE games_played >= 1
ORDER BY season_id DESC, position, points DESC;


-- === 04_summary_views.sql ===

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

CREATE OR REPLACE VIEW v_summary_team_season AS
SELECT 
    t.team_id,
    t.team_name,
    t.season_id,
    t.season,
    t.games_played,
    t.wins,
    t.losses,
    t.ties,
    t.points,
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
         t.games_played, t.wins, t.losses, t.ties, t.points,t.win_pct,
         t.goals_for, t.goals_against, t.goal_diff,
         t.goals_for_per_game, t.goals_against_per_game
ORDER BY t.season DESC, t.wins DESC;

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


-- === 05_recent_views.sql ===

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
    pg.toi_minutes,
    pg.game_score
FROM fact_player_game_stats pg
JOIN dim_schedule s ON pg.game_id = s.game_id
ORDER BY s.date DESC, pg.points DESC;

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


-- === 06_comparison_views.sql ===

CREATE OR REPLACE VIEW v_compare_players AS
SELECT 
    player_id,
    player_name,
    team_name,
    position,
    season_id,
    season,
    games_played,
    goals,
    assists,
    points,
    pim,
    goals_per_game,
    assists_per_game,
    points_per_game,
    pim_per_game
FROM fact_player_season_stats_basic
ORDER BY season_id DESC, player_name;

CREATE OR REPLACE VIEW v_compare_goalies AS
SELECT 
    player_id,
    player_name,
    team_name,
    season_id,
    season,
    games_played,
    wins,
    losses,
    goals_against,
    gaa,
    shutouts,
    win_pct,
    shutout_pct
FROM fact_goalie_season_stats_basic
ORDER BY season_id DESC, player_name;

CREATE OR REPLACE VIEW v_compare_goalies_advanced AS
SELECT 
    player_id,
    player_name,
    team_name,
    games_played,
    saves,
    goals_against,
    shots_against,
    save_pct,
    rush_sv_pct,
    set_play_sv_pct,
    rebound_control_rate,
    quality_start_pct,
    season_war
FROM fact_goalie_season_stats
ORDER BY player_name;

CREATE OR REPLACE VIEW v_compare_teams AS
SELECT 
    team_id,
    team_name,
    season_id,
    season,
    games_played,
    wins,
    losses,
    points,
    win_pct,
    goals_for,
    goals_against,
    goal_diff,
    goals_for_per_game,
    goals_against_per_game,
    team_total_goals,
    team_total_assists,
    roster_size
FROM v_summary_team_season
ORDER BY season_id DESC, team_name;

CREATE OR REPLACE VIEW v_compare_player_vs_league AS
WITH league_avg AS (
    SELECT 
        season_id,
        ROUND(AVG(goals_per_game)::numeric, 2) as league_avg_gpg,
        ROUND(AVG(assists_per_game)::numeric, 2) as league_avg_apg,
        ROUND(AVG(points_per_game)::numeric, 2) as league_avg_ppg
    FROM fact_player_season_stats_basic
    WHERE games_played >= 5
    GROUP BY season_id
)
SELECT 
    p.player_id,
    p.player_name,
    p.team_name,
    p.season_id,
    p.games_played,
    p.goals_per_game,
    la.league_avg_gpg,
    ROUND((p.goals_per_game - la.league_avg_gpg)::numeric, 2) as gpg_vs_avg,
    p.points_per_game,
    la.league_avg_ppg,
    ROUND((p.points_per_game - la.league_avg_ppg)::numeric, 2) as ppg_vs_avg,
    CASE 
        WHEN p.points_per_game > la.league_avg_ppg * 2.0 THEN 'Elite'
        WHEN p.points_per_game > la.league_avg_ppg THEN 'Above Average'
        WHEN p.points_per_game > la.league_avg_ppg * 0.3 THEN 'Average'
        ELSE 'Below Average'
    END as performance_tier
FROM fact_player_season_stats_basic p
JOIN league_avg la ON p.season_id = la.season_id
WHERE p.games_played >= 5
ORDER BY p.points_per_game DESC;

CREATE OR REPLACE VIEW v_compare_teammates AS
SELECT 
    p1.team_name,
    p1.season_id,
    p1.player_name as player1,
    p2.player_name as player2,
    p1.points as p1_points,
    p2.points as p2_points,
    p1.goals as p1_goals,
    p2.goals as p2_goals,
    p1.games_played as p1_gp,
    p2.games_played as p2_gp
FROM fact_player_season_stats_basic p1
JOIN fact_player_season_stats_basic p2 
    ON p1.team_id = p2.team_id 
    AND p1.season_id = p2.season_id
    AND p1.player_id < p2.player_id
WHERE p1.games_played >= 5 AND p2.games_played >= 5
ORDER BY p1.team_name, p1.points + p2.points DESC;


-- === 07_detail_views.sql ===

CREATE OR REPLACE VIEW v_detail_player_game_log AS
SELECT 
    pg.player_id,
    pg.player_name,
    pg.team_name,
    pg.game_id,
    s.date,
    s.home_team_name || ' vs ' || s.away_team_name as matchup,
    pg.goals,
    pg.assists,
    pg.points,
    pg.shots,
    pg.sog,
    pg.toi_minutes,
    pg.plus_minus_total,
    pg.game_score
FROM fact_player_game_stats pg
JOIN dim_schedule s ON pg.game_id = s.game_id
ORDER BY pg.player_id, s.date DESC;

CREATE OR REPLACE VIEW v_detail_goalie_game_log AS
SELECT 
    gg.player_id,
    gg.player_name,
    gg.team_name,
    gg.game_id,
    s.date,
    s.home_team_name || ' vs ' || s.away_team_name as matchup,
    gg.venue,
    gg.saves,
    gg.goals_against,
    gg.shots_against,
    gg.save_pct,
    gg.hd_save_pct,
    gg.is_quality_start,
    gg.overall_game_rating,
    gg.goalie_war
FROM fact_goalie_game_stats gg
JOIN dim_schedule s ON gg.game_id = s.game_id
ORDER BY gg.player_id, s.date DESC;

CREATE OR REPLACE VIEW v_detail_team_game_log AS
SELECT 
    tg.team_id,
    tg.team_name,
    tg.game_id,
    s.date,
    CASE 
        WHEN tg.team_name = s.home_team_name THEN 'vs ' || s.away_team_name
        ELSE '@ ' || s.home_team_name
    END as opponent,
    tg.goals,
    tg.assists,
    tg.points,
    tg.shots,
    tg.sog,
    CASE 
        WHEN tg.team_name = s.home_team_name AND s.home_total_goals > s.away_total_goals THEN 'W'
        WHEN tg.team_name = s.away_team_name AND s.away_total_goals > s.home_total_goals THEN 'W'
        ELSE 'L'
    END as result
FROM fact_team_game_stats tg
JOIN dim_schedule s ON tg.game_id = s.game_id
ORDER BY tg.team_id, s.date DESC;

CREATE OR REPLACE VIEW v_detail_player_periods AS
SELECT 
    player_id,
    player_name,
    team_name,
    game_id,
    p1_goals,
    p2_goals,
    p3_goals,
    p1_assists,
    p2_assists,
    p3_assists,
    p1_shots,
    p2_shots,
    p3_shots,
    p1_toi_seconds,
    p2_toi_seconds,
    p3_toi_seconds
FROM fact_player_game_stats
WHERE game_id != 99999;

CREATE OR REPLACE VIEW v_detail_goalie_periods AS
SELECT 
    player_id,
    player_name,
    team_name,
    game_id,
    p1_saves,
    p1_goals_against,
    p1_sv_pct,
    p2_saves,
    p2_goals_against,
    p2_sv_pct,
    p3_saves,
    p3_goals_against,
    p3_sv_pct,
    best_period,
    worst_period,
    period_consistency
FROM fact_goalie_game_stats;

CREATE OR REPLACE VIEW v_detail_goalie_shot_context AS
SELECT 
    player_id,
    player_name,
    team_name,
    game_id,
    rush_saves,
    rush_goals_against,
    rush_sv_pct,
    quick_attack_saves,
    quick_attack_ga,
    quick_attack_sv_pct,
    set_play_saves,
    set_play_ga,
    set_play_sv_pct,
    rush_pct_of_shots,
    transition_defense_rating
FROM fact_goalie_game_stats;

CREATE OR REPLACE VIEW v_detail_goalie_pressure AS
SELECT 
    player_id,
    player_name,
    team_name,
    game_id,
    single_shot_saves,
    multi_shot_saves,
    multi_shot_sv_pct,
    sustained_pressure_saves,
    sustained_pressure_sv_pct,
    max_sequence_faced,
    avg_sequence_length,
    sequence_survival_rate,
    pressure_handling_index
FROM fact_goalie_game_stats;

CREATE OR REPLACE VIEW v_detail_player_vs_opponent AS
SELECT 
    pg.player_id,
    pg.player_name,
    pg.team_name,
    CASE 
        WHEN pg.team_name = s.home_team_name THEN s.away_team_name
        ELSE s.home_team_name
    END as opponent,
    COUNT(*) as games_vs,
    SUM(pg.goals) as total_goals,
    SUM(pg.assists) as total_assists,
    SUM(pg.points) as total_points,
    ROUND(AVG(pg.points)::numeric, 2) as avg_points_vs
FROM fact_player_game_stats pg
JOIN dim_schedule s ON pg.game_id = s.game_id
GROUP BY pg.player_id, pg.player_name, pg.team_name,
         CASE 
            WHEN pg.team_name = s.home_team_name THEN s.away_team_name
            ELSE s.home_team_name
         END
ORDER BY pg.player_name, total_points DESC;

CREATE OR REPLACE VIEW v_detail_game_roster AS
SELECT 
    s.game_id,
    s.date,
    s.home_team_name,
    s.away_team_name,
    r.player_id,
    r.player_full_name,
    r.player_position,
    r.team_name,
    r.team_venue,
    r.goals,
    r.assist,
    r.points,
    r.pim
FROM dim_schedule s
JOIN fact_gameroster r ON s.game_id = r.game_id
ORDER BY s.date DESC, r.team_venue, r.points DESC;


-- === 08_tracking_advanced_views.sql ===

CREATE OR REPLACE VIEW v_tracking_event_summary AS
SELECT 
    game_id,
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT player_id) as unique_players
FROM fact_event_players
WHERE game_id != 99999
GROUP BY game_id, event_type
ORDER BY game_id, event_count DESC;

--CREATE OR REPLACE VIEW v_tracking_shot_locations AS
--SELECT 
    --game_id,
    --danger_zone,
    --COUNT(*) as shot_count,
    --COUNT(DISTINCT player_id) as shooters
--FROM fact_shot_event
--WHERE game_id IS NOT NULL
--GROUP BY game_id, danger_zone
--ORDER BY game_id, shot_count DESC;

--CREATE OR REPLACE VIEW v_tracking_zone_entries AS
--SELECT 
    --z.game_id,
    --z.zone_entry_type_id,
    --zet.zone_entry_type_name,
    --COUNT(*) as attempts,
    --SUM(CASE WHEN z.is_successful = 1 THEN 1 ELSE 0 END) as successful,
    --ROUND(SUM(CASE WHEN z.is_successful = 1 THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 1) as success_rate
--FROM fact_zone_entries z
--LEFT JOIN dim_zone_entry_type zet ON z.zone_entry_type_id = zet.zone_entry_type_id
--WHERE z.game_id != 99999
--GROUP BY z.game_id, z.zone_entry_type_id, zet.zone_entry_type_name
--ORDER BY z.game_id, attempts DESC;

--CREATE OR REPLACE VIEW v_tracking_player_micro AS
--SELECT 
    --ms.player_id,
    --ms.player_name,
    --ms.game_id,
    --ms.zone_entries,
    --ms.zone_exits,
    --ms.carried_entries,
    --ms.dump_ins,
    --ms.successful_entries,
    --ms.takeaways,
    --ms.giveaways,
    --ms.hits_given,
    --ms.hits_taken,
    --ms.blocks,
    --ms.shot_attempts
--FROM fact_player_micro_stats ms
--WHERE ms.game_id != 99999;

--CREATE OR REPLACE VIEW v_tracking_faceoffs AS
--SELECT 
   -- player_id,
    --game_id,
   -- COUNT(*) as total_faceoffs,
    --SUM(CASE WHEN is_win = 1 THEN 1 ELSE 0 END) as wins,
    --SUM(CASE WHEN is_win = 0 THEN 1 ELSE 0 END) as losses,
    --ROUND(SUM(CASE WHEN is_win = 1 THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(*), 0) * 100, 1) as fo_pct
--FROM fact_faceoffs
--WHERE game_id != 99999
--GROUP BY player_id, game_id
--ORDER BY total_faceoffs DESC;

--CREATE OR REPLACE VIEW v_tracking_scoring_chances AS
--SELECT 
   -- game_id,
   -- team_name,
   -- COUNT(*) as total_chances,
   -- SUM(CASE WHEN is_goal = 1 THEN 1 ELSE 0 END) as converted,
   -- ROUND(SUM(CASE WHEN is_goal = 1 THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(*), 0) * 100, 1) as conversion_rate
--FROM fact_scoring_chances
--WHERE game_id != 99999
--GROUP BY game_id, team_name
--ORDER BY game_id, total_chances DESC;

--CREATE OR REPLACE VIEW v_tracking_shift_quality AS
--SELECT 
   -- player_id,
   -- game_id,
   -- COUNT(*) as total_shifts,
   -- ROUND(AVG(shift_duration)::numeric, 1) as avg_shift_duration,
   -- ROUND(AVG(shift_quality_score)::numeric, 2) as avg_shift_quality,
    --SUM(scoring_chances_for) as total_chances_for,
    --SUM(scoring_chances_against) as total_chances_against
--FROM fact_shift_quality
--WHERE game_id != 99999
--GROUP BY player_id, game_id
--ORDER BY avg_shift_quality DESC;

--CREATE OR REPLACE VIEW v_tracking_save_types AS
--SELECT 
   -- goalie_id as player_id,
   -- game_id,
   -- save_type,
   -- COUNT(*) as save_count
--FROM fact_saves
--WHERE game_id != 99999
--GROUP BY goalie_id, game_id, save_type
--ORDER BY game_id, save_count DESC;
