-- =============================================================================
-- POSTGRESQL: DATAMART LAYER
-- =============================================================================
-- File: src/sql/postgres/datamart/create_datamart_tables.sql
--
-- PURPOSE:
--     Create final analytical tables optimized for Power BI.
--     These are the tables end users will query.
--
-- NAMING: No prefix (final tables)
-- =============================================================================

-- Create schema
CREATE SCHEMA IF NOT EXISTS datamart;

-- =============================================================================
-- DIMENSION TABLES (from intermediate, cleaned for analytics)
-- =============================================================================

-- DIM_PLAYER: Final player dimension
DROP TABLE IF EXISTS datamart.dim_player CASCADE;

CREATE TABLE datamart.dim_player AS
SELECT 
    player_id,
    player_full_name,
    display_name,
    player_first_name,
    player_last_name,
    primary_position,
    skill_rating,
    player_hand,
    birth_year,
    approx_age,
    is_norad,
    is_csaha,
    norad_team_id,
    csaha_team_id,
    player_url,
    player_image,
    _processed_timestamp
FROM intermediate.int_dim_player;

CREATE INDEX IF NOT EXISTS idx_dm_player_id ON datamart.dim_player(player_id);
CREATE INDEX IF NOT EXISTS idx_dm_player_skill ON datamart.dim_player(skill_rating);
CREATE INDEX IF NOT EXISTS idx_dm_player_position ON datamart.dim_player(primary_position);

-- DIM_TEAM: Final team dimension
DROP TABLE IF EXISTS datamart.dim_team CASCADE;

CREATE TABLE datamart.dim_team AS
SELECT * FROM intermediate.int_dim_team;

CREATE INDEX IF NOT EXISTS idx_dm_team_id ON datamart.dim_team(team_id);

-- DIM_LEAGUE: Final league dimension
DROP TABLE IF EXISTS datamart.dim_league CASCADE;

CREATE TABLE datamart.dim_league AS
SELECT * FROM intermediate.int_dim_league;

-- DIM_SEASON: Final season dimension
DROP TABLE IF EXISTS datamart.dim_season CASCADE;

CREATE TABLE datamart.dim_season AS
SELECT * FROM intermediate.int_dim_season;

-- DIM_SCHEDULE: Final schedule/game dimension
DROP TABLE IF EXISTS datamart.dim_schedule CASCADE;

CREATE TABLE datamart.dim_schedule AS
SELECT * FROM intermediate.int_dim_schedule;

CREATE INDEX IF NOT EXISTS idx_dm_schedule_game ON datamart.dim_schedule(game_id);
CREATE INDEX IF NOT EXISTS idx_dm_schedule_date ON datamart.dim_schedule(game_date);

-- DIM_RANDOMNAMES: Anonymization lookup
DROP TABLE IF EXISTS datamart.dim_randomnames CASCADE;

CREATE TABLE datamart.dim_randomnames AS
SELECT * FROM intermediate.int_dim_randomnames;

-- DIM_PLAYERURLREF: Player URL references
DROP TABLE IF EXISTS datamart.dim_playerurlref CASCADE;

CREATE TABLE datamart.dim_playerurlref AS
SELECT * FROM intermediate.int_dim_playerurlref;

-- DIM_RINKBOXCOORD: Rink coordinate boxes
DROP TABLE IF EXISTS datamart.dim_rinkboxcoord CASCADE;

CREATE TABLE datamart.dim_rinkboxcoord AS
SELECT * FROM intermediate.int_dim_rinkboxcoord;

-- DIM_RINKCOORDZONES: Rink zones
DROP TABLE IF EXISTS datamart.dim_rinkcoordzones CASCADE;

CREATE TABLE datamart.dim_rinkcoordzones AS
SELECT * FROM intermediate.int_dim_rinkcoordzones;

-- DIM_VIDEO: Video metadata
DROP TABLE IF EXISTS datamart.dim_video CASCADE;

CREATE TABLE datamart.dim_video AS
SELECT * FROM intermediate.int_dim_video;

CREATE INDEX IF NOT EXISTS idx_dm_video_game ON datamart.dim_video(game_id);

-- =============================================================================
-- STATIC DIMENSION TABLES
-- =============================================================================

-- DIM_PERIOD: Period reference
DROP TABLE IF EXISTS datamart.dim_period CASCADE;

CREATE TABLE datamart.dim_period (
    period_id       INTEGER PRIMARY KEY,
    period_name     VARCHAR(50),
    period_abbr     VARCHAR(10),
    is_overtime     BOOLEAN DEFAULT FALSE,
    is_shootout     BOOLEAN DEFAULT FALSE,
    sort_order      INTEGER
);

INSERT INTO datamart.dim_period VALUES
    (1, 'First Period', '1st', FALSE, FALSE, 1),
    (2, 'Second Period', '2nd', FALSE, FALSE, 2),
    (3, 'Third Period', '3rd', FALSE, FALSE, 3),
    (4, 'Overtime', 'OT', TRUE, FALSE, 4),
    (5, 'Shootout', 'SO', FALSE, TRUE, 5);

-- DIM_EVENT_TYPE: Event type reference
DROP TABLE IF EXISTS datamart.dim_event_type CASCADE;

CREATE TABLE datamart.dim_event_type (
    event_type      VARCHAR(50) PRIMARY KEY,
    event_category  VARCHAR(50),
    is_shot         BOOLEAN DEFAULT FALSE,
    is_possession   BOOLEAN DEFAULT FALSE,
    is_turnover     BOOLEAN DEFAULT FALSE,
    is_penalty      BOOLEAN DEFAULT FALSE,
    sort_order      INTEGER
);

INSERT INTO datamart.dim_event_type VALUES
    ('Shot', 'Offense', TRUE, TRUE, FALSE, FALSE, 1),
    ('Pass', 'Offense', FALSE, TRUE, FALSE, FALSE, 2),
    ('Turnover', 'Defense', FALSE, FALSE, TRUE, FALSE, 3),
    ('Faceoff', 'Neutral', FALSE, FALSE, FALSE, FALSE, 4),
    ('Zone_Entry_Exit', 'Transition', FALSE, TRUE, FALSE, FALSE, 5),
    ('Save', 'Goaltending', FALSE, FALSE, FALSE, FALSE, 6),
    ('Penalty', 'Discipline', FALSE, FALSE, FALSE, TRUE, 7),
    ('Hit', 'Physical', FALSE, FALSE, FALSE, FALSE, 8),
    ('Block', 'Defense', FALSE, FALSE, FALSE, FALSE, 9);

-- DIM_STRENGTH: Game strength situations
DROP TABLE IF EXISTS datamart.dim_strength CASCADE;

CREATE TABLE datamart.dim_strength (
    strength        VARCHAR(10) PRIMARY KEY,
    home_players    INTEGER,
    away_players    INTEGER,
    is_even         BOOLEAN DEFAULT FALSE,
    is_powerplay    BOOLEAN DEFAULT FALSE,
    is_shorthanded  BOOLEAN DEFAULT FALSE,
    description     VARCHAR(100)
);

INSERT INTO datamart.dim_strength VALUES
    ('5v5', 5, 5, TRUE, FALSE, FALSE, 'Even Strength'),
    ('5v4', 5, 4, FALSE, TRUE, FALSE, 'Home Power Play'),
    ('4v5', 4, 5, FALSE, FALSE, TRUE, 'Home Shorthanded'),
    ('5v3', 5, 3, FALSE, TRUE, FALSE, 'Home 5-on-3 Power Play'),
    ('3v5', 3, 5, FALSE, FALSE, TRUE, 'Home 3-on-5 Shorthanded'),
    ('4v4', 4, 4, TRUE, FALSE, FALSE, '4-on-4'),
    ('4v3', 4, 3, FALSE, TRUE, FALSE, 'Home 4-on-3 Power Play'),
    ('3v4', 3, 4, FALSE, FALSE, TRUE, 'Home 3-on-4 Shorthanded'),
    ('3v3', 3, 3, TRUE, FALSE, FALSE, '3-on-3 Overtime');

-- DIM_POSITION: Position reference
DROP TABLE IF EXISTS datamart.dim_position CASCADE;

CREATE TABLE datamart.dim_position (
    position_code   VARCHAR(5) PRIMARY KEY,
    position_name   VARCHAR(50),
    position_type   VARCHAR(20),
    is_forward      BOOLEAN DEFAULT FALSE,
    is_defense      BOOLEAN DEFAULT FALSE,
    is_goalie       BOOLEAN DEFAULT FALSE
);

INSERT INTO datamart.dim_position VALUES
    ('C', 'Center', 'Forward', TRUE, FALSE, FALSE),
    ('LW', 'Left Wing', 'Forward', TRUE, FALSE, FALSE),
    ('RW', 'Right Wing', 'Forward', TRUE, FALSE, FALSE),
    ('F', 'Forward', 'Forward', TRUE, FALSE, FALSE),
    ('D', 'Defense', 'Defense', FALSE, TRUE, FALSE),
    ('LD', 'Left Defense', 'Defense', FALSE, TRUE, FALSE),
    ('RD', 'Right Defense', 'Defense', FALSE, TRUE, FALSE),
    ('G', 'Goalie', 'Goalie', FALSE, FALSE, TRUE);

-- DIM_SKILL_TIER: Skill rating tiers
DROP TABLE IF EXISTS datamart.dim_skill_tier CASCADE;

CREATE TABLE datamart.dim_skill_tier (
    tier_id         INTEGER PRIMARY KEY,
    tier_name       VARCHAR(50),
    min_rating      DECIMAL(3,1),
    max_rating      DECIMAL(3,1),
    description     VARCHAR(200)
);

INSERT INTO datamart.dim_skill_tier VALUES
    (1, 'Elite', 5.5, 6.0, 'Top-tier players with exceptional skills'),
    (2, 'Advanced', 4.5, 5.4, 'Strong players with high-level abilities'),
    (3, 'Intermediate', 3.5, 4.4, 'Average skilled players'),
    (4, 'Developing', 2.5, 3.4, 'Players still building skills'),
    (5, 'Beginner', 2.0, 2.4, 'New players learning the game');

-- =============================================================================
-- FACT TABLES
-- =============================================================================

-- FACT_GAMEROSTER: Base game roster facts (from BLB)
DROP TABLE IF EXISTS datamart.fact_gameroster CASCADE;

CREATE TABLE datamart.fact_gameroster AS
SELECT * FROM intermediate.int_fact_gameroster;

CREATE INDEX IF NOT EXISTS idx_dm_gameroster_game ON datamart.fact_gameroster(game_id);
CREATE INDEX IF NOT EXISTS idx_dm_gameroster_player ON datamart.fact_gameroster(player_id);

-- FACT_LEADERSHIP: Leadership facts
DROP TABLE IF EXISTS datamart.fact_leadership CASCADE;

CREATE TABLE datamart.fact_leadership AS
SELECT * FROM intermediate.int_fact_leadership;

-- FACT_REGISTRATION: Registration facts
DROP TABLE IF EXISTS datamart.fact_registration CASCADE;

CREATE TABLE datamart.fact_registration AS
SELECT * FROM intermediate.int_fact_registration;

-- FACT_DRAFT: Draft facts
DROP TABLE IF EXISTS datamart.fact_draft CASCADE;

CREATE TABLE datamart.fact_draft AS
SELECT * FROM intermediate.int_fact_draft;

-- FACT_PLAYERGAMES: Season aggregate facts
DROP TABLE IF EXISTS datamart.fact_playergames CASCADE;

CREATE TABLE datamart.fact_playergames AS
SELECT * FROM intermediate.int_fact_playergames;

CREATE INDEX IF NOT EXISTS idx_dm_playergames_player ON datamart.fact_playergames(player_id);
CREATE INDEX IF NOT EXISTS idx_dm_playergames_season ON datamart.fact_playergames(season_id);

-- =============================================================================
-- TRACKING FACT TABLES (populated by game processing)
-- =============================================================================

-- FACT_BOX_SCORE: Comprehensive player-game statistics
DROP TABLE IF EXISTS datamart.fact_box_score CASCADE;

CREATE TABLE datamart.fact_box_score (
    player_game_key     VARCHAR(100) PRIMARY KEY,
    player_game_number  INTEGER,
    player_id           VARCHAR(50),
    player_full_name    VARCHAR(200),
    display_name        VARCHAR(200),
    player_team         VARCHAR(100),
    player_venue        VARCHAR(10),
    position            VARCHAR(10),
    skill_rating        DECIMAL(3,1),
    game_id             INTEGER,
    
    -- Scoring
    goals               INTEGER DEFAULT 0,
    assists_primary     INTEGER DEFAULT 0,
    assists_secondary   INTEGER DEFAULT 0,
    assists             INTEGER DEFAULT 0,
    points              INTEGER DEFAULT 0,
    
    -- Shooting
    shots               INTEGER DEFAULT 0,
    shots_on_goal       INTEGER DEFAULT 0,
    shooting_pct        DECIMAL(5,1),
    
    -- Passing
    passes              INTEGER DEFAULT 0,
    passes_completed    INTEGER DEFAULT 0,
    pass_pct            DECIMAL(5,1),
    
    -- Turnovers
    giveaways           INTEGER DEFAULT 0,
    takeaways           INTEGER DEFAULT 0,
    turnover_diff       INTEGER DEFAULT 0,
    
    -- Faceoffs
    faceoffs            INTEGER DEFAULT 0,
    faceoff_wins        INTEGER DEFAULT 0,
    faceoff_pct         DECIMAL(5,1),
    
    -- Micro-stats
    stick_checks        INTEGER DEFAULT 0,
    poke_checks         INTEGER DEFAULT 0,
    blocked_shots       INTEGER DEFAULT 0,
    backchecks          INTEGER DEFAULT 0,
    dekes               INTEGER DEFAULT 0,
    puck_recoveries     INTEGER DEFAULT 0,
    
    -- Time on ice
    toi_seconds         INTEGER DEFAULT 0,
    toi_formatted       VARCHAR(10),
    shifts              INTEGER DEFAULT 0,
    plus_minus          INTEGER DEFAULT 0,
    
    -- Per-60 rates
    goals_per_60        DECIMAL(5,2) DEFAULT 0,
    assists_per_60      DECIMAL(5,2) DEFAULT 0,
    points_per_60       DECIMAL(5,2) DEFAULT 0,
    shots_per_60        DECIMAL(5,2) DEFAULT 0,
    
    -- Flags
    is_tracked          BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    _processed_timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dm_boxscore_game ON datamart.fact_box_score(game_id);
CREATE INDEX IF NOT EXISTS idx_dm_boxscore_player ON datamart.fact_box_score(player_id);

-- FACT_EVENTS: Event-level tracking data
DROP TABLE IF EXISTS datamart.fact_events CASCADE;

CREATE TABLE datamart.fact_events (
    event_key           VARCHAR(100) PRIMARY KEY,
    event_index         INTEGER,
    shift_key           VARCHAR(100),
    game_id             INTEGER,
    
    -- Event details
    event_type          VARCHAR(50),
    event_detail        VARCHAR(100),
    event_detail_2      VARCHAR(100),
    event_successful    VARCHAR(10),
    
    -- Timing
    period              INTEGER,
    event_start_min     INTEGER,
    event_start_sec     INTEGER,
    time_total_seconds  INTEGER,
    duration            DECIMAL(5,2),
    
    -- Location
    event_team_zone     VARCHAR(20),
    
    -- Links
    linked_event_index  INTEGER,
    sequence_index      INTEGER,
    play_index          INTEGER,
    
    -- Metadata
    _processed_timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dm_events_game ON datamart.fact_events(game_id);
CREATE INDEX IF NOT EXISTS idx_dm_events_type ON datamart.fact_events(event_type);
CREATE INDEX IF NOT EXISTS idx_dm_events_period ON datamart.fact_events(period);

-- FACT_SHIFTS: Shift-level data
DROP TABLE IF EXISTS datamart.fact_shifts CASCADE;

CREATE TABLE datamart.fact_shifts (
    shift_key               VARCHAR(100) PRIMARY KEY,
    shift_index             INTEGER,
    game_id                 INTEGER,
    
    -- Timing
    period                  INTEGER,
    shift_start_seconds     INTEGER,
    shift_end_seconds       INTEGER,
    shift_duration          INTEGER,
    
    -- Type
    shift_start_type        VARCHAR(50),
    shift_stop_type         VARCHAR(50),
    
    -- Strength
    situation               VARCHAR(20),
    strength                VARCHAR(10),
    home_strength           INTEGER,
    away_strength           INTEGER,
    
    -- Score state
    home_goals              INTEGER,
    away_goals              INTEGER,
    
    -- Plus/minus events
    home_plus               INTEGER DEFAULT 0,
    home_minus              INTEGER DEFAULT 0,
    away_plus               INTEGER DEFAULT 0,
    away_minus              INTEGER DEFAULT 0,
    
    -- Metadata
    _processed_timestamp    TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dm_shifts_game ON datamart.fact_shifts(game_id);
CREATE INDEX IF NOT EXISTS idx_dm_shifts_strength ON datamart.fact_shifts(strength);
