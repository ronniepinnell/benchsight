-- =============================================================================
-- INTERMEDIATE: TRANSFORM BLB TABLES  
-- =============================================================================
-- All tables include _processed_timestamp and _updated_timestamp

-- INT_DIM_PLAYER
DROP TABLE IF EXISTS int_dim_player;

CREATE TABLE int_dim_player AS
SELECT
    player_id,
    COALESCE(player_full_name, 'Unknown') AS player_full_name,
    COALESCE(random_player_full_name, player_full_name) AS display_name,
    UPPER(COALESCE(player_primary_position, 'F')) AS primary_position,
    CAST(COALESCE(current_skill_rating, 4.0) AS REAL) AS skill_rating,
    player_hand,
    birth_year,
    datetime('now') AS _processed_timestamp,
    datetime('now') AS _updated_timestamp
FROM stg_dim_player
WHERE player_id IS NOT NULL;

-- INT_DIM_TEAM
DROP TABLE IF EXISTS int_dim_team;

CREATE TABLE int_dim_team AS
SELECT
    team_id,
    COALESCE(team_name, 'Unknown') AS team_name,
    COALESCE(team_cd, SUBSTR(team_name, 1, 3)) AS team_abbr,
    long_team_name,
    league,
    team_color1,
    team_color2,
    datetime('now') AS _processed_timestamp,
    datetime('now') AS _updated_timestamp
FROM stg_dim_team
WHERE team_id IS NOT NULL;

-- INT_DIM_SCHEDULE
DROP TABLE IF EXISTS int_dim_schedule;

CREATE TABLE int_dim_schedule AS
SELECT
    game_id,
    home_team_name AS home_team,
    away_team_name AS away_team,
    home_team_id,
    away_team_id,
    date AS game_date,
    season_id,
    game_type,
    playoff_round,
    CAST(COALESCE(home_total_goals, 0) AS INTEGER) AS home_score,
    CAST(COALESCE(away_total_goals, 0) AS INTEGER) AS away_score,
    CASE 
        WHEN COALESCE(home_total_goals, 0) > COALESCE(away_total_goals, 0) THEN home_team_name
        WHEN COALESCE(away_total_goals, 0) > COALESCE(home_total_goals, 0) THEN away_team_name
        ELSE 'TIE'
    END AS winner,
    video_id,
    video_url,
    datetime('now') AS _processed_timestamp,
    datetime('now') AS _updated_timestamp
FROM stg_dim_schedule
WHERE game_id IS NOT NULL;

-- INT_FACT_GAMEROSTER
DROP TABLE IF EXISTS int_fact_gameroster;

CREATE TABLE int_fact_gameroster AS
SELECT
    gr.game_id,
    gr.player_id,
    gr.player_game_number,
    gr.player_full_name,
    COALESCE(p.display_name, gr.player_full_name) AS display_name,
    gr.team_name,
    gr.opp_team_name,
    gr.team_venue,
    gr.player_position,
    CAST(COALESCE(gr.goals, 0) AS INTEGER) AS goals,
    CAST(COALESCE(gr.assist, 0) AS INTEGER) AS assists,
    CAST(COALESCE(gr.goals, 0) + COALESCE(gr.assist, 0) AS INTEGER) AS points,
    CAST(COALESCE(gr.pim, 0) AS INTEGER) AS penalty_minutes,
    CAST(COALESCE(gr.goals_against, 0) AS INTEGER) AS goals_against,
    CAST(COALESCE(p.skill_rating, 4.0) AS REAL) AS skill_rating,
    gr.game_id || '_' || gr.player_game_number AS player_game_key,
    datetime('now') AS _processed_timestamp,
    datetime('now') AS _updated_timestamp
FROM stg_fact_gameroster gr
LEFT JOIN int_dim_player p ON gr.player_id = p.player_id
WHERE gr.game_id IS NOT NULL AND gr.player_game_number IS NOT NULL;

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_int_gameroster_game ON int_fact_gameroster(game_id);
CREATE INDEX IF NOT EXISTS idx_int_gameroster_player ON int_fact_gameroster(player_id);
CREATE INDEX IF NOT EXISTS idx_int_player_id ON int_dim_player(player_id);
CREATE INDEX IF NOT EXISTS idx_int_schedule_game ON int_dim_schedule(game_id);
CREATE INDEX IF NOT EXISTS idx_int_team_id ON int_dim_team(team_id);
