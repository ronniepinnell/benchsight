-- =============================================================================
-- POSTGRESQL: INTERMEDIATE LAYER TRANSFORMATIONS
-- =============================================================================
-- File: src/sql/postgres/intermediate/transform_all_blb.sql
--
-- PURPOSE:
--     Transform ALL BLB tables from stage to intermediate layer.
--     Clean, standardize, and enrich the data.
--
-- TRANSFORMATIONS:
--     - Standardize column names (lowercase)
--     - Cast data types appropriately
--     - Handle NULL values with COALESCE
--     - Add derived/computed columns
--     - Create business keys
-- =============================================================================

-- Create schema
CREATE SCHEMA IF NOT EXISTS intermediate;

-- =============================================================================
-- INT_DIM_PLAYER: Cleaned player dimension
-- =============================================================================
-- WHY: Central player reference with standardized skill ratings

DROP TABLE IF EXISTS intermediate.int_dim_player CASCADE;

CREATE TABLE intermediate.int_dim_player AS
SELECT
    -- Primary key
    player_id,
    
    -- Names
    COALESCE(player_full_name, 'Unknown Player') AS player_full_name,
    COALESCE(random_player_full_name, player_full_name, 'Unknown') AS display_name,
    player_first_name,
    player_last_name,
    
    -- Position: standardize to uppercase
    UPPER(COALESCE(player_primary_position, 'F')) AS primary_position,
    
    -- Skill rating: default to 4.0 (average) if missing
    COALESCE(current_skill_rating, 4.0)::DECIMAL(3,1) AS skill_rating,
    
    -- Physical attributes
    player_hand,
    birth_year,
    -- Calculate approximate age
    EXTRACT(YEAR FROM CURRENT_DATE) - birth_year AS approx_age,
    
    -- League affiliations
    COALESCE(player_norad, FALSE) AS is_norad,
    COALESCE(player_csaha, FALSE) AS is_csaha,
    player_norad_current_team_id AS norad_team_id,
    player_csah_current_team_id AS csaha_team_id,
    
    -- URLs for lookup
    player_url,
    player_image,
    
    -- Metadata
    NOW() AS _processed_timestamp
    
FROM stage.stg_dim_player
WHERE player_id IS NOT NULL;

-- Index for lookups
CREATE INDEX IF NOT EXISTS idx_int_player_id ON intermediate.int_dim_player(player_id);
CREATE INDEX IF NOT EXISTS idx_int_player_skill ON intermediate.int_dim_player(skill_rating);

-- =============================================================================
-- INT_DIM_TEAM: Cleaned team dimension
-- =============================================================================

DROP TABLE IF EXISTS intermediate.int_dim_team CASCADE;

CREATE TABLE intermediate.int_dim_team AS
SELECT
    team_id,
    COALESCE(team_name, 'Unknown Team') AS team_name,
    COALESCE(long_team_name, team_name) AS long_team_name,
    COALESCE(team_cd, SUBSTRING(team_name, 1, 3)) AS team_abbr,
    league,
    league_id,
    COALESCE(norad_team, FALSE) AS is_norad,
    COALESCE(csah_team, FALSE) AS is_csaha,
    team_color1 AS primary_color,
    team_color2 AS secondary_color,
    team_logo,
    team_url,
    NOW() AS _processed_timestamp
    
FROM stage.stg_dim_team
WHERE team_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_int_team_id ON intermediate.int_dim_team(team_id);

-- =============================================================================
-- INT_DIM_LEAGUE: League reference
-- =============================================================================

DROP TABLE IF EXISTS intermediate.int_dim_league CASCADE;

CREATE TABLE intermediate.int_dim_league AS
SELECT
    league_id,
    COALESCE(league_name, 'Unknown League') AS league_name,
    COALESCE(league_abbreviation, SUBSTRING(league_name, 1, 5)) AS league_abbr,
    NOW() AS _processed_timestamp
    
FROM stage.stg_dim_league
WHERE league_id IS NOT NULL;

-- =============================================================================
-- INT_DIM_SEASON: Season reference with computed fields
-- =============================================================================

DROP TABLE IF EXISTS intermediate.int_dim_season CASCADE;

CREATE TABLE intermediate.int_dim_season AS
SELECT
    season_id,
    COALESCE(season_name, season_id) AS season_name,
    season_start_date,
    season_end_date,
    -- Calculate season duration in days
    COALESCE(season_end_date - season_start_date, 0) AS season_duration_days,
    league_id,
    COALESCE(is_current, FALSE) AS is_current,
    season_type,
    COALESCE(num_games, 0) AS num_games,
    COALESCE(playoff_rounds, 0) AS playoff_rounds,
    NOW() AS _processed_timestamp
    
FROM stage.stg_dim_season
WHERE season_id IS NOT NULL;

-- =============================================================================
-- INT_DIM_SCHEDULE: Game schedule with derived fields
-- =============================================================================

DROP TABLE IF EXISTS intermediate.int_dim_schedule CASCADE;

CREATE TABLE intermediate.int_dim_schedule AS
SELECT
    game_id,
    season_id,
    season,
    
    -- Teams
    home_team_name AS home_team,
    away_team_name AS away_team,
    home_team_id,
    away_team_id,
    
    -- Date/time
    game_date,
    game_time,
    -- Extract date parts for filtering
    EXTRACT(YEAR FROM game_date)::INTEGER AS game_year,
    EXTRACT(MONTH FROM game_date)::INTEGER AS game_month,
    EXTRACT(DOW FROM game_date)::INTEGER AS day_of_week,
    
    -- Game type
    game_type,
    playoff_round,
    
    -- Scores
    COALESCE(home_total_goals, 0)::INTEGER AS home_score,
    COALESCE(away_total_goals, 0)::INTEGER AS away_score,
    COALESCE(home_total_goals, 0) - COALESCE(away_total_goals, 0) AS goal_differential,
    
    -- Winner calculation
    CASE 
        WHEN home_total_goals > away_total_goals THEN home_team_name
        WHEN away_total_goals > home_total_goals THEN away_team_name
        ELSE 'TIE'
    END AS winner,
    
    CASE 
        WHEN home_total_goals > away_total_goals THEN 'home'
        WHEN away_total_goals > home_total_goals THEN 'away'
        ELSE 'tie'
    END AS winner_venue,
    
    -- Period scores
    home_team_period1_goals,
    home_team_period2_goals,
    home_team_period3_goals,
    away_team_period1_goals,
    away_team_period2_goals,
    away_team_period3_goals,
    
    -- Overtime indicator
    last_period_type,
    CASE WHEN last_period_type = 'Overtime' THEN TRUE ELSE FALSE END AS went_to_overtime,
    
    -- Video info
    video_id,
    video_url,
    
    -- URLs
    game_url,
    
    NOW() AS _processed_timestamp
    
FROM stage.stg_dim_schedule
WHERE game_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_int_schedule_game ON intermediate.int_dim_schedule(game_id);
CREATE INDEX IF NOT EXISTS idx_int_schedule_date ON intermediate.int_dim_schedule(game_date);
CREATE INDEX IF NOT EXISTS idx_int_schedule_season ON intermediate.int_dim_schedule(season_id);

-- =============================================================================
-- INT_DIM_RANDOMNAMES: Anonymization lookup
-- =============================================================================

DROP TABLE IF EXISTS intermediate.int_dim_randomnames CASCADE;

CREATE TABLE intermediate.int_dim_randomnames AS
SELECT
    id AS random_name_id,
    random_first_name,
    random_last_name,
    random_full_name,
    gender,
    nationality,
    COALESCE(used, FALSE) AS is_used,
    NOW() AS _processed_timestamp
    
FROM stage.stg_dim_randomnames;

-- =============================================================================
-- INT_DIM_PLAYERURLREF: Player URL references
-- =============================================================================

DROP TABLE IF EXISTS intermediate.int_dim_playerurlref CASCADE;

CREATE TABLE intermediate.int_dim_playerurlref AS
SELECT
    id AS url_ref_id,
    player_id,
    url_type,
    url,
    COALESCE(is_primary, FALSE) AS is_primary,
    source_league,
    NOW() AS _processed_timestamp
    
FROM stage.stg_dim_playerurlref
WHERE player_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_int_urlref_player ON intermediate.int_dim_playerurlref(player_id);

-- =============================================================================
-- INT_DIM_RINKBOXCOORD: Rink coordinate boxes
-- =============================================================================

DROP TABLE IF EXISTS intermediate.int_dim_rinkboxcoord CASCADE;

CREATE TABLE intermediate.int_dim_rinkboxcoord AS
SELECT
    box_id,
    box_name,
    x_min,
    x_max,
    y_min,
    y_max,
    -- Calculate box center
    (x_min + x_max) / 2 AS x_center,
    (y_min + y_max) / 2 AS y_center,
    -- Calculate box area
    (x_max - x_min) * (y_max - y_min) AS box_area,
    zone,
    COALESCE(is_slot, FALSE) AS is_slot,
    COALESCE(is_crease, FALSE) AS is_crease,
    COALESCE(is_high_danger, FALSE) AS is_high_danger,
    description,
    NOW() AS _processed_timestamp
    
FROM stage.stg_dim_rinkboxcoord;

-- =============================================================================
-- INT_DIM_RINKCOORDZONES: Rink zones
-- =============================================================================

DROP TABLE IF EXISTS intermediate.int_dim_rinkcoordzones CASCADE;

CREATE TABLE intermediate.int_dim_rinkcoordzones AS
SELECT
    zone_id,
    zone_name,
    zone_type,
    x_coord,
    y_coord,
    x_min,
    x_max,
    y_min,
    y_max,
    COALESCE(is_offensive, FALSE) AS is_offensive,
    COALESCE(is_defensive, FALSE) AS is_defensive,
    COALESCE(is_neutral, FALSE) AS is_neutral,
    COALESCE(danger_level, 0) AS danger_level,
    NOW() AS _processed_timestamp
    
FROM stage.stg_dim_rinkcoordzones;

-- =============================================================================
-- INT_DIM_VIDEO: Video metadata
-- =============================================================================

DROP TABLE IF EXISTS intermediate.int_dim_video CASCADE;

CREATE TABLE intermediate.int_dim_video AS
SELECT
    id AS video_row_id,
    video_key,
    game_id,
    video_type,
    video_category,
    -- Coalesce URLs to find primary
    COALESCE(url_1, url_2, url_3, url_4) AS primary_url,
    url_1,
    url_2,
    url_3,
    url_4,
    video_id,
    extension,
    embed_url,
    description,
    NOW() AS _processed_timestamp
    
FROM stage.stg_dim_video;

CREATE INDEX IF NOT EXISTS idx_int_video_game ON intermediate.int_dim_video(game_id);

-- =============================================================================
-- FACT TABLES
-- =============================================================================

-- INT_FACT_GAMEROSTER: Enriched game roster
DROP TABLE IF EXISTS intermediate.int_fact_gameroster CASCADE;

CREATE TABLE intermediate.int_fact_gameroster AS
SELECT
    -- Keys
    gr.game_id,
    gr.player_id,
    gr.player_game_number,
    -- Create composite key
    gr.game_id::TEXT || '_' || gr.player_game_number::TEXT AS player_game_key,
    
    -- Player info
    gr.player_full_name,
    COALESCE(p.display_name, gr.player_full_name) AS display_name,
    gr.team_name,
    gr.opp_team_name,
    gr.team_venue,
    gr.player_position,
    
    -- Stats with defaults
    COALESCE(gr.goals, 0)::INTEGER AS goals,
    COALESCE(gr.assists, 0)::INTEGER AS assists,
    COALESCE(gr.goals, 0) + COALESCE(gr.assists, 0) AS points,
    COALESCE(gr.penalty_minutes, 0)::INTEGER AS penalty_minutes,
    COALESCE(gr.goals_against, 0)::INTEGER AS goals_against,
    COALESCE(gr.shutouts, 0)::INTEGER AS shutouts,
    
    -- Enriched skill rating from player dimension
    COALESCE(p.skill_rating, 4.0)::DECIMAL(3,1) AS skill_rating,
    
    -- Position from player dimension
    COALESCE(p.primary_position, gr.player_position) AS primary_position,
    
    -- Game context from schedule
    s.game_date,
    s.season_id,
    s.game_type,
    
    -- Team IDs
    gr.team_id,
    gr.opp_team_id,
    
    -- Flags
    COALESCE(gr.is_sub, FALSE) AS is_sub,
    
    NOW() AS _processed_timestamp
    
FROM stage.stg_fact_gameroster gr
LEFT JOIN intermediate.int_dim_player p ON gr.player_id = p.player_id
LEFT JOIN intermediate.int_dim_schedule s ON gr.game_id = s.game_id
WHERE gr.game_id IS NOT NULL 
  AND gr.player_game_number IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_int_gameroster_game ON intermediate.int_fact_gameroster(game_id);
CREATE INDEX IF NOT EXISTS idx_int_gameroster_player ON intermediate.int_fact_gameroster(player_id);
CREATE INDEX IF NOT EXISTS idx_int_gameroster_key ON intermediate.int_fact_gameroster(player_game_key);

-- =============================================================================
-- INT_FACT_LEADERSHIP: Team leadership
-- =============================================================================

DROP TABLE IF EXISTS intermediate.int_fact_leadership CASCADE;

CREATE TABLE intermediate.int_fact_leadership AS
SELECT
    id AS leadership_id,
    player_id,
    team_id,
    season_id,
    leadership_role,
    start_date,
    end_date,
    COALESCE(is_current, FALSE) AS is_current,
    appointed_by,
    notes,
    -- Enriched fields
    p.display_name AS player_name,
    t.team_name,
    NOW() AS _processed_timestamp
    
FROM stage.stg_fact_leadership l
LEFT JOIN intermediate.int_dim_player p ON l.player_id = p.player_id
LEFT JOIN intermediate.int_dim_team t ON l.team_id = t.team_id;

-- =============================================================================
-- INT_FACT_REGISTRATION: Player registrations
-- =============================================================================

DROP TABLE IF EXISTS intermediate.int_fact_registration CASCADE;

CREATE TABLE intermediate.int_fact_registration AS
SELECT
    id AS registration_id,
    player_id,
    team_id,
    season_id,
    registration_date,
    registration_type,
    registration_status,
    jersey_number,
    COALESCE(is_captain, FALSE) AS is_captain,
    COALESCE(is_alternate, FALSE) AS is_alternate,
    COALESCE(is_goalie, FALSE) AS is_goalie,
    COALESCE(fee_paid, 0)::DECIMAL(10,2) AS fee_paid,
    payment_status,
    COALESCE(waiver_signed, FALSE) AS waiver_signed,
    -- Enriched
    p.display_name AS player_name,
    p.skill_rating,
    t.team_name,
    NOW() AS _processed_timestamp
    
FROM stage.stg_fact_registration r
LEFT JOIN intermediate.int_dim_player p ON r.player_id = p.player_id
LEFT JOIN intermediate.int_dim_team t ON r.team_id = t.team_id;

-- =============================================================================
-- INT_FACT_DRAFT: Draft picks
-- =============================================================================

DROP TABLE IF EXISTS intermediate.int_fact_draft CASCADE;

CREATE TABLE intermediate.int_fact_draft AS
SELECT
    id AS draft_pick_id,
    draft_id,
    season_id,
    round_number,
    pick_number,
    overall_pick,
    team_id,
    player_id,
    player_name,
    position,
    COALESCE(d.skill_rating, p.skill_rating, 4.0)::DECIMAL(3,1) AS skill_rating,
    draft_order,
    COALESCE(is_keeper, FALSE) AS is_keeper,
    notes,
    -- Enriched
    t.team_name,
    p.display_name,
    NOW() AS _processed_timestamp
    
FROM stage.stg_fact_draft d
LEFT JOIN intermediate.int_dim_player p ON d.player_id = p.player_id
LEFT JOIN intermediate.int_dim_team t ON d.team_id = t.team_id;

-- =============================================================================
-- INT_FACT_PLAYERGAMES: Season aggregates
-- =============================================================================

DROP TABLE IF EXISTS intermediate.int_fact_playergames CASCADE;

CREATE TABLE intermediate.int_fact_playergames AS
SELECT
    id AS player_season_id,
    player_id,
    season_id,
    team_id,
    COALESCE(games_played, 0) AS games_played,
    COALESCE(goals, 0) AS goals,
    COALESCE(assists, 0) AS assists,
    COALESCE(points, goals + assists, 0) AS points,
    COALESCE(penalty_minutes, 0) AS penalty_minutes,
    goals_against,
    saves,
    save_percentage,
    COALESCE(shutouts, 0) AS shutouts,
    COALESCE(wins, 0) AS wins,
    COALESCE(losses, 0) AS losses,
    COALESCE(ties, 0) AS ties,
    plus_minus,
    -- Calculate per-game rates
    CASE WHEN games_played > 0 
         THEN ROUND(points::DECIMAL / games_played, 2)
         ELSE 0 
    END AS points_per_game,
    CASE WHEN games_played > 0 
         THEN ROUND(goals::DECIMAL / games_played, 2)
         ELSE 0 
    END AS goals_per_game,
    -- Enriched
    p.display_name AS player_name,
    p.skill_rating,
    p.primary_position,
    t.team_name,
    NOW() AS _processed_timestamp
    
FROM stage.stg_fact_playergames pg
LEFT JOIN intermediate.int_dim_player p ON pg.player_id = p.player_id
LEFT JOIN intermediate.int_dim_team t ON pg.team_id = t.team_id;

CREATE INDEX IF NOT EXISTS idx_int_playergames_player ON intermediate.int_fact_playergames(player_id);
CREATE INDEX IF NOT EXISTS idx_int_playergames_season ON intermediate.int_fact_playergames(season_id);
