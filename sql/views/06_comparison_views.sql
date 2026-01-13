-- ============================================================================
-- COMPARISON VIEWS - Player/Team comparison helpers
-- ============================================================================

-- Player Season Stats (for side-by-side comparison)
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

-- Goalie Comparison View
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

-- Advanced Goalie Comparison (from tracking)
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

-- Team Comparison View
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
    team_goals,
    team_assists,
    unique_players as roster_size
FROM v_summary_team_season
ORDER BY season_id DESC, team_name;

-- Player vs League Average
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

-- Head-to-Head Player Comparison (same team)
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
