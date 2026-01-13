-- ============================================================================
-- LEADERBOARD VIEWS - Top N players for key statistics
-- v29.0: Added game_type filter (defaults to 'All'), added ties to goalie views
-- ============================================================================

-- Points Leaders (all seasons, combined game types)
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

-- Points Leaders - By Game Type (filterable)
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

-- Goals Leaders
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

-- Assists Leaders
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

-- Points Per Game Leaders (min 5 games)
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

-- PIM Leaders
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

-- Career Points Leaders
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

-- Goalie Wins Leaders
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

-- Goalie Wins Leaders - By Game Type
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

-- Goalie GAA Leaders (min 5 games, lower is better)
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

-- Goalie Record Summary (W-L-T)
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
