-- =============================================================================
-- POSTGRESQL: CREATE STAGE TABLES
-- =============================================================================
-- File: src/sql/postgres/stage/create_stage_tables.sql
--
-- PURPOSE:
--     Create all stage (raw) tables for BLB data.
--     Stage tables preserve original data with minimal transformation.
--
-- NAMING: All tables prefixed with stg_
-- =============================================================================

-- Create schema if not exists
-- WHY: Organize tables by pipeline layer
CREATE SCHEMA IF NOT EXISTS stage;

-- =============================================================================
-- DIMENSION TABLES
-- =============================================================================

-- STG_DIM_PLAYER: Raw player master data
DROP TABLE IF EXISTS stage.stg_dim_player CASCADE;
CREATE TABLE stage.stg_dim_player (
    player_id               VARCHAR(50) PRIMARY KEY,
    player_first_name       VARCHAR(100),
    player_last_name        VARCHAR(100),
    player_full_name        VARCHAR(200),
    player_primary_position VARCHAR(10),
    current_skill_rating    DECIMAL(3,1),
    player_hand             VARCHAR(10),
    birth_year              INTEGER,
    player_gender           VARCHAR(10),
    highest_beer_league     VARCHAR(50),
    player_rating_ly        DECIMAL(3,1),
    player_notes            TEXT,
    player_leadership       VARCHAR(50),
    player_norad            BOOLEAN,
    player_csaha            BOOLEAN,
    player_norad_primary_number INTEGER,
    player_csah_primary_number  INTEGER,
    player_norad_current_team   VARCHAR(100),
    player_csah_current_team    VARCHAR(100),
    player_norad_current_team_id VARCHAR(50),
    player_csah_current_team_id  VARCHAR(50),
    other_url               VARCHAR(500),
    player_url              VARCHAR(500),
    player_image            VARCHAR(500),
    random_player_first_name VARCHAR(100),
    random_player_last_name  VARCHAR(100),
    random_player_full_name  VARCHAR(200),
    _load_timestamp         TIMESTAMP DEFAULT NOW(),
    _source_file            VARCHAR(255)
);

-- STG_DIM_TEAM: Raw team reference data
DROP TABLE IF EXISTS stage.stg_dim_team CASCADE;
CREATE TABLE stage.stg_dim_team (
    team_id                 VARCHAR(50) PRIMARY KEY,
    team_name               VARCHAR(100),
    long_team_name          VARCHAR(200),
    team_cd                 VARCHAR(10),
    norad_team              BOOLEAN,
    csah_team               BOOLEAN,
    league_id               VARCHAR(50),
    league                  VARCHAR(50),
    team_color1             VARCHAR(50),
    team_color2             VARCHAR(50),
    team_color3             VARCHAR(50),
    team_color4             VARCHAR(50),
    team_logo               VARCHAR(500),
    team_url                VARCHAR(500),
    _load_timestamp         TIMESTAMP DEFAULT NOW(),
    _source_file            VARCHAR(255)
);

-- STG_DIM_LEAGUE: League reference
DROP TABLE IF EXISTS stage.stg_dim_league CASCADE;
CREATE TABLE stage.stg_dim_league (
    league_id               VARCHAR(50) PRIMARY KEY,
    league_name             VARCHAR(100),
    league_abbreviation     VARCHAR(20),
    _load_timestamp         TIMESTAMP DEFAULT NOW(),
    _source_file            VARCHAR(255)
);

-- STG_DIM_SEASON: Season reference
DROP TABLE IF EXISTS stage.stg_dim_season CASCADE;
CREATE TABLE stage.stg_dim_season (
    season_id               VARCHAR(50) PRIMARY KEY,
    season_name             VARCHAR(100),
    season_start_date       DATE,
    season_end_date         DATE,
    league_id               VARCHAR(50),
    is_current              BOOLEAN,
    season_type             VARCHAR(50),
    num_games               INTEGER,
    playoff_rounds          INTEGER,
    _load_timestamp         TIMESTAMP DEFAULT NOW(),
    _source_file            VARCHAR(255)
);

-- STG_DIM_SCHEDULE: Game schedule
DROP TABLE IF EXISTS stage.stg_dim_schedule CASCADE;
CREATE TABLE stage.stg_dim_schedule (
    game_id                 INTEGER PRIMARY KEY,
    season                  VARCHAR(50),
    season_id               VARCHAR(50),
    game_url                VARCHAR(500),
    home_team_game_id       VARCHAR(50),
    away_team_game_id       VARCHAR(50),
    game_date               DATE,
    game_time               TIME,
    home_team_name          VARCHAR(100),
    away_team_name          VARCHAR(100),
    home_team_id            VARCHAR(50),
    away_team_id            VARCHAR(50),
    head_to_head_id         VARCHAR(100),
    game_type               VARCHAR(50),
    playoff_round           VARCHAR(50),
    last_period_type        VARCHAR(50),
    period_length           INTERVAL,
    ot_period_length        INTERVAL,
    shootout_rounds         INTEGER,
    home_total_goals        INTEGER,
    away_total_goals        INTEGER,
    home_team_period1_goals INTEGER,
    home_team_period2_goals INTEGER,
    home_team_period3_goals INTEGER,
    home_team_periodot_goals INTEGER,
    away_team_period1_goals INTEGER,
    away_team_period2_goals INTEGER,
    away_team_period3_goals INTEGER,
    away_team_periodot_goals INTEGER,
    home_team_seeding       INTEGER,
    away_team_seeding       INTEGER,
    home_team_w             INTEGER,
    home_team_l             INTEGER,
    home_team_t             INTEGER,
    home_team_pts           INTEGER,
    away_team_w             INTEGER,
    away_team_l             INTEGER,
    away_team_t             INTEGER,
    away_team_pts           INTEGER,
    video_id                VARCHAR(100),
    video_start_time        VARCHAR(50),
    video_end_time          VARCHAR(50),
    video_title             VARCHAR(500),
    video_url               VARCHAR(500),
    _load_timestamp         TIMESTAMP DEFAULT NOW(),
    _source_file            VARCHAR(255)
);

-- STG_DIM_RANDOMNAMES: Anonymization lookup
DROP TABLE IF EXISTS stage.stg_dim_randomnames CASCADE;
CREATE TABLE stage.stg_dim_randomnames (
    id                      SERIAL PRIMARY KEY,
    random_first_name       VARCHAR(100),
    random_last_name        VARCHAR(100),
    random_full_name        VARCHAR(200),
    gender                  VARCHAR(10),
    nationality             VARCHAR(50),
    used                    BOOLEAN DEFAULT FALSE,
    _load_timestamp         TIMESTAMP DEFAULT NOW(),
    _source_file            VARCHAR(255)
);

-- STG_DIM_PLAYERURLREF: Player URL references
DROP TABLE IF EXISTS stage.stg_dim_playerurlref CASCADE;
CREATE TABLE stage.stg_dim_playerurlref (
    id                      SERIAL PRIMARY KEY,
    player_id               VARCHAR(50),
    url_type                VARCHAR(50),
    url                     VARCHAR(500),
    is_primary              BOOLEAN,
    source_league           VARCHAR(50),
    _load_timestamp         TIMESTAMP DEFAULT NOW(),
    _source_file            VARCHAR(255)
);

-- STG_DIM_RINKBOXCOORD: Rink box coordinates
DROP TABLE IF EXISTS stage.stg_dim_rinkboxcoord CASCADE;
CREATE TABLE stage.stg_dim_rinkboxcoord (
    box_id                  SERIAL PRIMARY KEY,
    box_name                VARCHAR(100),
    x_min                   DECIMAL(10,2),
    x_max                   DECIMAL(10,2),
    y_min                   DECIMAL(10,2),
    y_max                   DECIMAL(10,2),
    zone                    VARCHAR(50),
    is_slot                 BOOLEAN,
    is_crease               BOOLEAN,
    is_high_danger          BOOLEAN,
    description             TEXT,
    _load_timestamp         TIMESTAMP DEFAULT NOW(),
    _source_file            VARCHAR(255)
);

-- STG_DIM_RINKCOORDZONES: Rink coordinate zones
DROP TABLE IF EXISTS stage.stg_dim_rinkcoordzones CASCADE;
CREATE TABLE stage.stg_dim_rinkcoordzones (
    zone_id                 SERIAL PRIMARY KEY,
    zone_name               VARCHAR(100),
    zone_type               VARCHAR(50),
    x_coord                 DECIMAL(10,2),
    y_coord                 DECIMAL(10,2),
    x_min                   DECIMAL(10,2),
    x_max                   DECIMAL(10,2),
    y_min                   DECIMAL(10,2),
    y_max                   DECIMAL(10,2),
    is_offensive            BOOLEAN,
    is_defensive            BOOLEAN,
    is_neutral              BOOLEAN,
    danger_level            INTEGER,
    _load_timestamp         TIMESTAMP DEFAULT NOW(),
    _source_file            VARCHAR(255)
);

-- =============================================================================
-- FACT TABLES
-- =============================================================================

-- STG_FACT_GAMEROSTER: Player-game participation
DROP TABLE IF EXISTS stage.stg_fact_gameroster CASCADE;
CREATE TABLE stage.stg_fact_gameroster (
    id                      SERIAL PRIMARY KEY,
    game_id                 INTEGER NOT NULL,
    team_game_id            VARCHAR(50),
    opp_team_game_id        VARCHAR(50),
    player_game_id          VARCHAR(100),
    team_venue              VARCHAR(10),
    team_name               VARCHAR(100),
    opp_team_name           VARCHAR(100),
    player_game_number      INTEGER,
    n_player_url            VARCHAR(500),
    player_position         VARCHAR(10),
    games_played            INTEGER,
    goals                   INTEGER,
    assists                 INTEGER,
    goals_against           INTEGER,
    penalty_minutes         INTEGER,
    shutouts                INTEGER,
    team_id                 VARCHAR(50),
    opp_team_id             VARCHAR(50),
    roster_key              VARCHAR(100),
    player_full_name        VARCHAR(200),
    player_id               VARCHAR(50),
    game_date               DATE,
    season                  VARCHAR(50),
    is_sub                  BOOLEAN,
    current_team            VARCHAR(100),
    skill_rating            DECIMAL(3,1),
    _load_timestamp         TIMESTAMP DEFAULT NOW(),
    _source_file            VARCHAR(255)
);

-- STG_FACT_LEADERSHIP: Team leadership
DROP TABLE IF EXISTS stage.stg_fact_leadership CASCADE;
CREATE TABLE stage.stg_fact_leadership (
    id                      SERIAL PRIMARY KEY,
    player_id               VARCHAR(50),
    team_id                 VARCHAR(50),
    season_id               VARCHAR(50),
    leadership_role         VARCHAR(50),
    start_date              DATE,
    end_date                DATE,
    is_current              BOOLEAN,
    appointed_by            VARCHAR(100),
    notes                   TEXT,
    _load_timestamp         TIMESTAMP DEFAULT NOW(),
    _source_file            VARCHAR(255)
);

-- STG_FACT_REGISTRATION: Player registrations
DROP TABLE IF EXISTS stage.stg_fact_registration CASCADE;
CREATE TABLE stage.stg_fact_registration (
    id                      SERIAL PRIMARY KEY,
    player_id               VARCHAR(50),
    team_id                 VARCHAR(50),
    season_id               VARCHAR(50),
    registration_date       DATE,
    registration_type       VARCHAR(50),
    registration_status     VARCHAR(50),
    jersey_number           INTEGER,
    is_captain              BOOLEAN,
    is_alternate            BOOLEAN,
    is_goalie               BOOLEAN,
    fee_paid                DECIMAL(10,2),
    payment_status          VARCHAR(50),
    waiver_signed           BOOLEAN,
    emergency_contact       VARCHAR(200),
    notes                   TEXT,
    _load_timestamp         TIMESTAMP DEFAULT NOW(),
    _source_file            VARCHAR(255)
);

-- STG_FACT_DRAFT: Draft picks
DROP TABLE IF EXISTS stage.stg_fact_draft CASCADE;
CREATE TABLE stage.stg_fact_draft (
    id                      SERIAL PRIMARY KEY,
    draft_id                VARCHAR(50),
    season_id               VARCHAR(50),
    round_number            INTEGER,
    pick_number             INTEGER,
    overall_pick            INTEGER,
    team_id                 VARCHAR(50),
    player_id               VARCHAR(50),
    player_name             VARCHAR(200),
    position                VARCHAR(10),
    skill_rating            DECIMAL(3,1),
    draft_order             INTEGER,
    is_keeper               BOOLEAN,
    notes                   TEXT,
    _load_timestamp         TIMESTAMP DEFAULT NOW(),
    _source_file            VARCHAR(255)
);

-- STG_FACT_PLAYERGAMES: Aggregated player stats
DROP TABLE IF EXISTS stage.stg_fact_playergames CASCADE;
CREATE TABLE stage.stg_fact_playergames (
    id                      SERIAL PRIMARY KEY,
    player_id               VARCHAR(50),
    season_id               VARCHAR(50),
    team_id                 VARCHAR(50),
    games_played            INTEGER,
    goals                   INTEGER,
    assists                 INTEGER,
    points                  INTEGER,
    penalty_minutes         INTEGER,
    goals_against           DECIMAL(5,2),
    saves                   INTEGER,
    save_percentage         DECIMAL(5,3),
    shutouts                INTEGER,
    wins                    INTEGER,
    losses                  INTEGER,
    ties                    INTEGER,
    plus_minus              INTEGER,
    points_per_game         DECIMAL(5,2),
    _load_timestamp         TIMESTAMP DEFAULT NOW(),
    _source_file            VARCHAR(255)
);

-- =============================================================================
-- VIDEO TIMES TABLE
-- =============================================================================

DROP TABLE IF EXISTS stage.stg_dim_video CASCADE;
CREATE TABLE stage.stg_dim_video (
    id                      SERIAL PRIMARY KEY,
    video_key               VARCHAR(100),
    game_id                 INTEGER,
    video_type              VARCHAR(50),
    video_category          VARCHAR(50),
    url_1                   VARCHAR(500),
    url_2                   VARCHAR(500),
    url_3                   VARCHAR(500),
    url_4                   VARCHAR(500),
    video_id                VARCHAR(100),
    extension               VARCHAR(20),
    embed_url               VARCHAR(500),
    description             TEXT,
    _load_timestamp         TIMESTAMP DEFAULT NOW(),
    _source_file            VARCHAR(255)
);

-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_stg_gameroster_game ON stage.stg_fact_gameroster(game_id);
CREATE INDEX IF NOT EXISTS idx_stg_gameroster_player ON stage.stg_fact_gameroster(player_id);
CREATE INDEX IF NOT EXISTS idx_stg_schedule_date ON stage.stg_dim_schedule(game_date);
CREATE INDEX IF NOT EXISTS idx_stg_schedule_season ON stage.stg_dim_schedule(season_id);
CREATE INDEX IF NOT EXISTS idx_stg_video_game ON stage.stg_dim_video(game_id);

-- =============================================================================
-- METADATA TABLE
-- =============================================================================

DROP TABLE IF EXISTS stage._etl_metadata CASCADE;
CREATE TABLE stage._etl_metadata (
    id                      SERIAL PRIMARY KEY,
    table_name              VARCHAR(100) NOT NULL,
    load_timestamp          TIMESTAMP DEFAULT NOW(),
    row_count               INTEGER,
    source_file             VARCHAR(255),
    load_type               VARCHAR(50),
    status                  VARCHAR(50),
    error_message           TEXT,
    duration_seconds        DECIMAL(10,2)
);
