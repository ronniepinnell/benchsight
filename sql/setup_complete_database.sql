-- =============================================================================
-- BENCHSIGHT COMPLETE POSTGRESQL SETUP
-- =============================================================================
-- File: sql/setup_complete_database.sql
-- 
-- PURPOSE:
--   Single script to set up the complete BenchSight database from scratch.
--   Creates database, schemas, all tables, indexes, and sample data loader.
--
-- USAGE:
--   1. Connect as postgres superuser:
--      psql -U postgres
--
--   2. Run this script:
--      \i sql/setup_complete_database.sql
--
--   OR from command line:
--      psql -U postgres -f sql/setup_complete_database.sql
--
-- SCHEMAS:
--   staging       - Raw data loaded from Excel/CSV files
--   intermediate  - Transformed/enriched data  
--   hockey_mart   - Final analytics-ready tables
--
-- =============================================================================

-- =============================================================================
-- STEP 1: CREATE DATABASE
-- =============================================================================
-- Run this block separately if the database doesn't exist

-- \c postgres
-- DROP DATABASE IF EXISTS benchsight;
-- CREATE DATABASE benchsight;
-- \c benchsight

-- =============================================================================
-- STEP 2: CREATE SCHEMAS
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS staging;
COMMENT ON SCHEMA staging IS 'Raw data loaded directly from source files (Excel, CSV)';

CREATE SCHEMA IF NOT EXISTS intermediate;
COMMENT ON SCHEMA intermediate IS 'Transformed and enriched data before final modeling';

CREATE SCHEMA IF NOT EXISTS hockey_mart;
COMMENT ON SCHEMA hockey_mart IS 'Final star schema for analytics, dashboards, and ML';

-- =============================================================================
-- STEP 3: STAGING TABLES (stg_*)
-- =============================================================================
-- These tables hold raw data exactly as loaded from source files

SET search_path TO staging;

-- stg_players: Raw player data from BLB_Tables
CREATE TABLE IF NOT EXISTS stg_players (
    player_id VARCHAR(20),
    player_first_name VARCHAR(100),
    player_last_name VARCHAR(100),
    player_full_name VARCHAR(200),
    display_name VARCHAR(200),
    player_primary_position VARCHAR(20),
    current_skill_rating DECIMAL(3,1),
    player_hand VARCHAR(10),
    birth_year INTEGER,
    player_gender CHAR(1),
    _source_file VARCHAR(200),
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- stg_teams: Raw team data
CREATE TABLE IF NOT EXISTS stg_teams (
    team_id VARCHAR(20),
    team_name VARCHAR(100),
    long_team_name VARCHAR(200),
    team_cd VARCHAR(10),
    team_color1 VARCHAR(20),
    team_color2 VARCHAR(20),
    league_id VARCHAR(10),
    league VARCHAR(50),
    _source_file VARCHAR(200),
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- stg_schedule: Raw schedule data
CREATE TABLE IF NOT EXISTS stg_schedule (
    game_id INTEGER,
    season VARCHAR(20),
    season_id VARCHAR(20),
    game_date DATE,
    game_time TIME,
    home_team_name VARCHAR(100),
    away_team_name VARCHAR(100),
    home_team_id VARCHAR(20),
    away_team_id VARCHAR(20),
    home_total_goals INTEGER,
    away_total_goals INTEGER,
    video_id VARCHAR(50),
    video_url TEXT,
    _source_file VARCHAR(200),
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- stg_game_rosters: Raw game roster data
CREATE TABLE IF NOT EXISTS stg_game_rosters (
    game_id INTEGER,
    team_venue VARCHAR(10),
    team_name VARCHAR(100),
    player_game_number INTEGER,
    player_position VARCHAR(20),
    player_full_name VARCHAR(200),
    player_id VARCHAR(20),
    skill_rating DECIMAL(3,1),
    _source_file VARCHAR(200),
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- stg_events: Raw tracking events
CREATE TABLE IF NOT EXISTS stg_events (
    game_id INTEGER,
    event_index INTEGER,
    event_type VARCHAR(50),
    event_detail VARCHAR(100),
    event_detail_2 VARCHAR(100),
    event_successful INTEGER,
    period INTEGER,
    clock_start VARCHAR(20),
    clock_end VARCHAR(20),
    clock_start_seconds INTEGER,
    clock_end_seconds INTEGER,
    event_team VARCHAR(10),
    event_team_zone VARCHAR(10),
    shift_index INTEGER,
    player_number INTEGER,
    player_role VARCHAR(30),
    video_time DECIMAL(10,2),
    x_coord DECIMAL(6,2),
    y_coord DECIMAL(6,2),
    _source_file VARCHAR(200),
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- stg_shifts: Raw shift data
CREATE TABLE IF NOT EXISTS stg_shifts (
    game_id INTEGER,
    shift_index INTEGER,
    period INTEGER,
    start_seconds INTEGER,
    end_seconds INTEGER,
    duration_seconds INTEGER,
    start_type VARCHAR(50),
    stop_type VARCHAR(50),
    home_f1 INTEGER,
    home_f2 INTEGER,
    home_f3 INTEGER,
    home_d1 INTEGER,
    home_d2 INTEGER,
    home_g INTEGER,
    home_x INTEGER,
    away_f1 INTEGER,
    away_f2 INTEGER,
    away_f3 INTEGER,
    away_d1 INTEGER,
    away_d2 INTEGER,
    away_g INTEGER,
    away_x INTEGER,
    _source_file VARCHAR(200),
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- STEP 4: INTERMEDIATE TABLES (int_*)
-- =============================================================================
-- These tables contain transformed/enriched data

SET search_path TO intermediate;

-- int_events_enriched: Events with player/team info joined
CREATE TABLE IF NOT EXISTS int_events_enriched (
    game_id INTEGER,
    event_index INTEGER,
    event_key VARCHAR(30),
    shift_key VARCHAR(30),
    event_type VARCHAR(50),
    event_detail VARCHAR(100),
    event_detail_2 VARCHAR(100),
    event_successful INTEGER,
    period INTEGER,
    time_start_seconds INTEGER,
    time_end_seconds INTEGER,
    duration INTEGER,
    event_team VARCHAR(10),
    event_team_zone VARCHAR(10),
    player_number INTEGER,
    player_role VARCHAR(30),
    player_id VARCHAR(20),
    player_name VARCHAR(200),
    player_skill DECIMAL(3,1),
    player_position VARCHAR(20),
    team_name VARCHAR(100),
    -- Previous/next event context
    prev_event_type VARCHAR(50),
    next_event_type VARCHAR(50),
    time_since_prev INTEGER,
    -- XY coordinates
    x_coord DECIMAL(6,2),
    y_coord DECIMAL(6,2),
    zone_id VARCHAR(10),
    danger_zone VARCHAR(10),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- int_shifts_enriched: Shifts with player roster details
CREATE TABLE IF NOT EXISTS int_shifts_enriched (
    game_id INTEGER,
    shift_index INTEGER,
    shift_key VARCHAR(30),
    period INTEGER,
    start_seconds INTEGER,
    end_seconds INTEGER,
    duration_seconds INTEGER,
    start_type VARCHAR(50),
    stop_type VARCHAR(50),
    situation VARCHAR(20),
    strength VARCHAR(20),
    home_strength INTEGER,
    away_strength INTEGER,
    home_skill_avg DECIMAL(4,2),
    away_skill_avg DECIMAL(4,2),
    skill_differential DECIMAL(4,2),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- STEP 5: DATAMART TABLES (dim_*, fact_*)
-- =============================================================================
-- Final star schema for analytics

SET search_path TO hockey_mart;

-- -------------------------------------------------------------------------
-- DIMENSION TABLES
-- -------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_player (
    player_id VARCHAR(20) PRIMARY KEY,
    player_first_name VARCHAR(100),
    player_last_name VARCHAR(100),
    player_full_name VARCHAR(200),
    display_name VARCHAR(200),
    primary_position VARCHAR(20),
    skill_rating DECIMAL(3,1),
    player_hand VARCHAR(10),
    birth_year INTEGER,
    player_gender CHAR(1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_team (
    team_id VARCHAR(20) PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    long_team_name VARCHAR(200),
    team_cd VARCHAR(10),
    team_color1 VARCHAR(20),
    team_color2 VARCHAR(20),
    league_id VARCHAR(10),
    league VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS dim_season (
    season_id VARCHAR(20) PRIMARY KEY,
    season VARCHAR(20),
    session CHAR(1),
    league_id VARCHAR(10),
    league VARCHAR(50),
    start_date DATE
);

CREATE TABLE IF NOT EXISTS dim_schedule (
    game_id INTEGER PRIMARY KEY,
    game_key VARCHAR(20) UNIQUE,
    season VARCHAR(20),
    season_id VARCHAR(20),
    game_date DATE,
    game_time TIME,
    home_team_name VARCHAR(100),
    away_team_name VARCHAR(100),
    home_team_id VARCHAR(20),
    away_team_id VARCHAR(20),
    game_type VARCHAR(50),
    home_total_goals INTEGER,
    away_total_goals INTEGER,
    video_id VARCHAR(50),
    video_url TEXT
);

CREATE TABLE IF NOT EXISTS dim_game_players (
    player_game_key VARCHAR(30) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    player_game_number INTEGER NOT NULL,
    player_id VARCHAR(20),
    player_full_name VARCHAR(200),
    display_name VARCHAR(200),
    player_team VARCHAR(100),
    player_venue VARCHAR(10),
    position VARCHAR(20),
    skill_rating DECIMAL(3,1)
);

CREATE TABLE IF NOT EXISTS dim_period (
    period_id INTEGER PRIMARY KEY,
    period_name VARCHAR(20),
    period_type VARCHAR(20)
);

INSERT INTO dim_period VALUES (1, '1st Period', 'regulation') ON CONFLICT DO NOTHING;
INSERT INTO dim_period VALUES (2, '2nd Period', 'regulation') ON CONFLICT DO NOTHING;
INSERT INTO dim_period VALUES (3, '3rd Period', 'regulation') ON CONFLICT DO NOTHING;
INSERT INTO dim_period VALUES (4, 'OT', 'overtime') ON CONFLICT DO NOTHING;
INSERT INTO dim_period VALUES (5, 'SO', 'shootout') ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS dim_event_type (
    event_type_id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) UNIQUE,
    event_category VARCHAR(30),
    is_shot INTEGER,
    is_scoring_chance INTEGER
);

INSERT INTO dim_event_type (event_type, event_category, is_shot, is_scoring_chance) VALUES
    ('Shot', 'shooting', 1, 1),
    ('Pass', 'possession', 0, 0),
    ('Faceoff', 'possession', 0, 0),
    ('ZoneEntry', 'transition', 0, 0),
    ('ZoneExit', 'transition', 0, 0),
    ('Turnover', 'possession', 0, 0),
    ('Takeaway', 'possession', 0, 0),
    ('Block', 'defensive', 0, 0),
    ('Save', 'goaltending', 0, 0),
    ('Goal', 'scoring', 1, 1),
    ('Penalty', 'discipline', 0, 0),
    ('Hit', 'physical', 0, 0),
    ('GameStart', 'game', 0, 0),
    ('GameEnd', 'game', 0, 0),
    ('PeriodStart', 'game', 0, 0),
    ('PeriodEnd', 'game', 0, 0)
ON CONFLICT (event_type) DO NOTHING;

CREATE TABLE IF NOT EXISTS dim_zone (
    zone_id VARCHAR(10) PRIMARY KEY,
    zone_name VARCHAR(30),
    zone_type VARCHAR(20)
);

INSERT INTO dim_zone VALUES ('OZ', 'Offensive Zone', 'offensive') ON CONFLICT DO NOTHING;
INSERT INTO dim_zone VALUES ('NZ', 'Neutral Zone', 'neutral') ON CONFLICT DO NOTHING;
INSERT INTO dim_zone VALUES ('DZ', 'Defensive Zone', 'defensive') ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS dim_rink_zones (
    zone_id VARCHAR(10) PRIMARY KEY,
    x_min DECIMAL(6,2),
    x_max DECIMAL(6,2),
    y_min DECIMAL(6,2),
    y_max DECIMAL(6,2),
    danger VARCHAR(10),
    slot VARCHAR(50),
    zone VARCHAR(20),
    side VARCHAR(20)
);

-- -------------------------------------------------------------------------
-- FACT TABLES
-- -------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_shifts (
    shift_key VARCHAR(30) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    shift_index INTEGER NOT NULL,
    period INTEGER,
    shift_start_seconds INTEGER,
    shift_end_seconds INTEGER,
    shift_duration INTEGER,
    shift_start_type VARCHAR(50),
    shift_stop_type VARCHAR(50),
    situation VARCHAR(20),
    strength VARCHAR(20),
    home_strength INTEGER,
    away_strength INTEGER,
    home_goals INTEGER,
    away_goals INTEGER,
    home_skill_avg DECIMAL(4,2),
    away_skill_avg DECIMAL(4,2),
    skill_differential DECIMAL(4,2)
);

CREATE TABLE IF NOT EXISTS fact_shift_players (
    shift_player_key VARCHAR(40) PRIMARY KEY,
    shift_key VARCHAR(30) NOT NULL,
    player_game_key VARCHAR(30) NOT NULL,
    game_id INTEGER NOT NULL,
    shift_index INTEGER NOT NULL,
    player_game_number INTEGER NOT NULL,
    position_slot VARCHAR(30),
    position_type VARCHAR(20),
    player_venue VARCHAR(10),
    shift_duration INTEGER,
    plus_minus INTEGER,
    skill_rating DECIMAL(3,1)
);

CREATE TABLE IF NOT EXISTS fact_events (
    event_key VARCHAR(30) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    event_index INTEGER NOT NULL,
    shift_key VARCHAR(30),
    shift_index INTEGER,
    event_type VARCHAR(50),
    event_detail VARCHAR(100),
    event_detail_2 VARCHAR(100),
    event_successful INTEGER,
    period INTEGER,
    time_start_seconds INTEGER,
    time_end_seconds INTEGER,
    duration INTEGER,
    event_team VARCHAR(100),
    event_team_zone VARCHAR(10),
    event_player_1_skill DECIMAL(3,1),
    linked_event_index INTEGER,
    sequence_index INTEGER,
    play_index INTEGER,
    prev_event_type VARCHAR(50),
    next_event_type VARCHAR(50),
    is_goal INTEGER,
    x_coord DECIMAL(6,2),
    y_coord DECIMAL(6,2)
);

CREATE TABLE IF NOT EXISTS fact_event_players (
    event_player_key VARCHAR(50) PRIMARY KEY,
    event_key VARCHAR(30) NOT NULL,
    player_game_key VARCHAR(30) NOT NULL,
    game_id INTEGER NOT NULL,
    event_index INTEGER NOT NULL,
    player_game_number INTEGER NOT NULL,
    player_role VARCHAR(30),
    role_number INTEGER,
    play_detail1 VARCHAR(100),
    play_detail_2 VARCHAR(100),
    play_detail_successful INTEGER,
    is_primary_player INTEGER,
    skill_rating DECIMAL(3,1)
);

CREATE TABLE IF NOT EXISTS fact_box_score (
    player_game_key VARCHAR(30) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    player_game_number INTEGER NOT NULL,
    player_id VARCHAR(20),
    player_team VARCHAR(100),
    player_venue VARCHAR(10),
    position VARCHAR(20),
    skill_rating DECIMAL(3,1),
    -- Ice time
    toi_seconds INTEGER DEFAULT 0,
    shifts INTEGER DEFAULT 0,
    plus_minus INTEGER DEFAULT 0,
    -- Scoring
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    -- Shooting
    shots INTEGER DEFAULT 0,
    shots_on_goal INTEGER DEFAULT 0,
    shooting_pct DECIMAL(5,1),
    -- Passing
    passes INTEGER DEFAULT 0,
    passes_completed INTEGER DEFAULT 0,
    pass_pct DECIMAL(5,1),
    -- Faceoffs
    faceoffs INTEGER DEFAULT 0,
    faceoff_wins INTEGER DEFAULT 0,
    faceoff_pct DECIMAL(5,1),
    -- Zone play
    zone_entries INTEGER DEFAULT 0,
    zone_exits INTEGER DEFAULT 0,
    -- Possession
    takeaways INTEGER DEFAULT 0,
    giveaways INTEGER DEFAULT 0,
    -- Per-60 rates
    goals_per_60 DECIMAL(5,2),
    points_per_60 DECIMAL(5,2),
    shots_per_60 DECIMAL(5,2)
);

CREATE TABLE IF NOT EXISTS fact_gameroster (
    roster_key VARCHAR(50) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    team_venue VARCHAR(10),
    team_name VARCHAR(100),
    player_game_number INTEGER,
    player_position VARCHAR(20),
    player_full_name VARCHAR(200),
    player_id VARCHAR(20),
    skill_rating DECIMAL(3,1)
);

-- =============================================================================
-- STEP 6: CREATE INDEXES
-- =============================================================================

-- Staging indexes
CREATE INDEX IF NOT EXISTS idx_stg_events_game ON staging.stg_events(game_id);
CREATE INDEX IF NOT EXISTS idx_stg_shifts_game ON staging.stg_shifts(game_id);

-- Datamart indexes
CREATE INDEX IF NOT EXISTS idx_shifts_game ON hockey_mart.fact_shifts(game_id);
CREATE INDEX IF NOT EXISTS idx_events_game ON hockey_mart.fact_events(game_id);
CREATE INDEX IF NOT EXISTS idx_events_shift ON hockey_mart.fact_events(shift_key);
CREATE INDEX IF NOT EXISTS idx_event_players_event ON hockey_mart.fact_event_players(event_key);
CREATE INDEX IF NOT EXISTS idx_event_players_player ON hockey_mart.fact_event_players(player_game_key);
CREATE INDEX IF NOT EXISTS idx_box_score_game ON hockey_mart.fact_box_score(game_id);
CREATE INDEX IF NOT EXISTS idx_game_players_game ON hockey_mart.dim_game_players(game_id);

-- =============================================================================
-- STEP 7: HELPER FUNCTIONS
-- =============================================================================

-- Function to truncate all staging tables
CREATE OR REPLACE FUNCTION staging.truncate_all_staging()
RETURNS void AS $$
BEGIN
    TRUNCATE staging.stg_players;
    TRUNCATE staging.stg_teams;
    TRUNCATE staging.stg_schedule;
    TRUNCATE staging.stg_game_rosters;
    TRUNCATE staging.stg_events;
    TRUNCATE staging.stg_shifts;
END;
$$ LANGUAGE plpgsql;

-- Function to get game summary
CREATE OR REPLACE FUNCTION hockey_mart.get_game_summary(p_game_id INTEGER)
RETURNS TABLE (
    game_id INTEGER,
    game_date DATE,
    home_team VARCHAR,
    away_team VARCHAR,
    home_goals INTEGER,
    away_goals INTEGER,
    total_events BIGINT,
    total_shifts BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.game_id,
        s.game_date,
        s.home_team_name,
        s.away_team_name,
        s.home_total_goals,
        s.away_total_goals,
        COUNT(DISTINCT e.event_key) as total_events,
        COUNT(DISTINCT sh.shift_key) as total_shifts
    FROM hockey_mart.dim_schedule s
    LEFT JOIN hockey_mart.fact_events e ON s.game_id = e.game_id
    LEFT JOIN hockey_mart.fact_shifts sh ON s.game_id = sh.game_id
    WHERE s.game_id = p_game_id
    GROUP BY s.game_id, s.game_date, s.home_team_name, s.away_team_name,
             s.home_total_goals, s.away_total_goals;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- STEP 8: GRANT PERMISSIONS (uncomment and adjust as needed)
-- =============================================================================

-- CREATE ROLE benchsight_user LOGIN PASSWORD 'your_password';
-- GRANT USAGE ON SCHEMA staging TO benchsight_user;
-- GRANT USAGE ON SCHEMA intermediate TO benchsight_user;
-- GRANT USAGE ON SCHEMA hockey_mart TO benchsight_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA staging TO benchsight_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA intermediate TO benchsight_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA hockey_mart TO benchsight_user;

-- =============================================================================
-- COMPLETE!
-- =============================================================================

-- Verify setup
SELECT 'SETUP COMPLETE!' as status;
SELECT schemaname, count(*) as table_count 
FROM pg_tables 
WHERE schemaname IN ('staging', 'intermediate', 'hockey_mart')
GROUP BY schemaname
ORDER BY schemaname;
