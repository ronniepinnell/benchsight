-- ============================================================================
-- RANKINGS VIEWS - Full player/goalie rankings with multiple stats
-- ============================================================================

-- Complete Player Rankings (current season)
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

-- Complete Goalie Rankings (current season) 
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

-- Advanced Goalie Rankings (from tracking)
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

-- Career Rankings
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

-- Goalie Career Rankings
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

-- Position-Specific Rankings (Forwards vs Defense)
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
