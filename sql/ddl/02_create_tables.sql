-- =============================================================================
-- HOCKEY ANALYTICS - TABLE DEFINITIONS
-- =============================================================================
-- File: sql/ddl/02_create_tables.sql
--
-- PURPOSE:
--   Create all tables in the hockey_mart schema.
--   Uses a star/snowflake schema design for analytics.
--
-- TABLE CATEGORIES:
--   1. DIMENSION TABLES (dim_*): Descriptive attributes
--   2. FACT TABLES (fact_*): Measurable events and metrics
--   3. BRIDGE TABLES: Many-to-many relationships
--
-- NAMING CONVENTIONS:
--   - dim_: Dimension tables
--   - fact_: Fact tables
--   - _key: Surrogate keys (composite: game_id + local_id)
--   - _id: Natural/business keys
-- =============================================================================

SET search_path TO hockey_mart;

-- =============================================================================
-- DIMENSION TABLES
-- =============================================================================

-- dim_player: Master player dimension
CREATE TABLE IF NOT EXISTS dim_player (
    player_id VARCHAR(20) PRIMARY KEY,
    player_first_name VARCHAR(100),
    player_last_name VARCHAR(100),
    player_full_name VARCHAR(200),
    display_name VARCHAR(200),
    player_primary_position VARCHAR(20),
    current_skill_rating DECIMAL(3,1),
    player_hand VARCHAR(10),
    birth_year INTEGER,
    player_gender CHAR(1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dim_player IS 'Master player dimension with persistent player attributes';
COMMENT ON COLUMN dim_player.player_id IS 'Business key (e.g., P100001)';
COMMENT ON COLUMN dim_player.current_skill_rating IS 'Player skill rating (2-6, 6 is best)';

-- dim_team: Team dimension
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

COMMENT ON TABLE dim_team IS 'Team master data';

-- dim_season: Season dimension
CREATE TABLE IF NOT EXISTS dim_season (
    season_id VARCHAR(20) PRIMARY KEY,
    season VARCHAR(20),
    session CHAR(1),
    league_id VARCHAR(10),
    league VARCHAR(50),
    start_date DATE
);

-- dim_schedule: Game schedule (enhanced dim_game)
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
    playoff_round VARCHAR(50),
    last_period_type VARCHAR(20),
    home_total_goals INTEGER,
    away_total_goals INTEGER,
    video_id VARCHAR(50),
    video_url TEXT
);

-- dim_rink_zones: Rink zone coordinates for shot analysis
CREATE TABLE IF NOT EXISTS dim_rink_zones (
    zone_id VARCHAR(10) PRIMARY KEY,
    zone_id_rev VARCHAR(10),
    x_min DECIMAL(6,2),
    x_max DECIMAL(6,2),
    y_min DECIMAL(6,2),
    y_max DECIMAL(6,2),
    x_description VARCHAR(50),
    y_description VARCHAR(50),
    danger VARCHAR(10),
    slot VARCHAR(50),
    zone VARCHAR(20),
    side VARCHAR(20),
    dotside VARCHAR(50),
    depth VARCHAR(50)
);

COMMENT ON TABLE dim_rink_zones IS 'Rink coordinate zones for shot location analysis';

-- dim_game_players: Game-specific player dimension
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
    skill_rating DECIMAL(3,1),
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id)
);

COMMENT ON TABLE dim_game_players IS 'Players participating in each game with game-specific attributes';
COMMENT ON COLUMN dim_game_players.player_game_key IS 'Composite key: game_id_player_number';

-- =============================================================================
-- FACT TABLES
-- =============================================================================

-- fact_shifts: Shift-level data
CREATE TABLE IF NOT EXISTS fact_shifts (
    shift_key VARCHAR(30) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    shift_index INTEGER NOT NULL,
    period INTEGER,
    shift_start_total_seconds INTEGER,
    shift_end_total_seconds INTEGER,
    shift_duration INTEGER,
    shift_start_type VARCHAR(50),
    shift_stop_type VARCHAR(50),
    situation VARCHAR(20),
    strength VARCHAR(20),
    home_team_strength INTEGER,
    away_team_strength INTEGER,
    home_goals INTEGER,
    away_goals INTEGER,
    home_team_plus INTEGER,
    home_team_minus INTEGER,
    away_team_plus INTEGER,
    away_team_minus INTEGER,
    -- Skill aggregates
    home_skill_avg DECIMAL(4,2),
    away_skill_avg DECIMAL(4,2),
    skill_differential DECIMAL(4,2),
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id)
);

COMMENT ON TABLE fact_shifts IS 'Game shifts with team-level aggregates';

-- fact_shift_players: Player-shift bridge table
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
    skill_rating DECIMAL(3,1),
    FOREIGN KEY (shift_key) REFERENCES fact_shifts(shift_key),
    FOREIGN KEY (player_game_key) REFERENCES dim_game_players(player_game_key)
);

COMMENT ON TABLE fact_shift_players IS 'Players on ice for each shift';

-- fact_events: Event-level data
CREATE TABLE IF NOT EXISTS fact_events (
    event_key VARCHAR(30) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    event_index INTEGER NOT NULL,
    shift_key VARCHAR(30),
    shift_index INTEGER,
    event_type VARCHAR(50),
    event_detail VARCHAR(100),
    event_detail_2 VARCHAR(100),
    event_successful CHAR(1),
    period INTEGER,
    time_start_total_seconds INTEGER,
    time_end_total_seconds INTEGER,
    duration INTEGER,
    event_team VARCHAR(100),
    event_team_zone VARCHAR(10),
    -- Skill context
    event_player_1_skill DECIMAL(3,1),
    opp_player_1_skill DECIMAL(3,1),
    player_skill_differential DECIMAL(3,1),
    -- Chain references
    linked_event_index INTEGER,
    sequence_index INTEGER,
    play_index INTEGER,
    -- ML features
    prev_event_type VARCHAR(50),
    next_event_type VARCHAR(50),
    time_since_prev INTEGER,
    is_goal INTEGER,
    is_goal_sequence INTEGER,
    events_to_next_goal INTEGER,
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id),
    FOREIGN KEY (shift_key) REFERENCES fact_shifts(shift_key)
);

COMMENT ON TABLE fact_events IS 'Game events with skill context and ML features';

-- fact_event_players: Player-event bridge table
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
    play_detail_successful CHAR(1),
    is_primary_player INTEGER,
    is_event_team INTEGER,
    is_opp_team INTEGER,
    skill_rating DECIMAL(3,1),
    FOREIGN KEY (event_key) REFERENCES fact_events(event_key),
    FOREIGN KEY (player_game_key) REFERENCES dim_game_players(player_game_key)
);

COMMENT ON TABLE fact_event_players IS 'Players involved in each event with role details';

-- fact_box_score: Pre-aggregated player statistics
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
    toi_seconds INTEGER,
    toi_formatted VARCHAR(10),
    shifts INTEGER,
    plus_minus INTEGER,
    -- Scoring
    goals INTEGER,
    assists INTEGER,
    assists_primary INTEGER,
    assists_secondary INTEGER,
    points INTEGER,
    -- Shooting
    shots INTEGER,
    shots_on_goal INTEGER,
    shots_missed INTEGER,
    shots_blocked INTEGER,
    shooting_pct DECIMAL(5,1),
    shots_successful INTEGER,
    shots_unsuccessful INTEGER,
    -- Passing
    passes INTEGER,
    passes_completed INTEGER,
    passes_failed INTEGER,
    pass_pct DECIMAL(5,1),
    times_pass_target INTEGER,
    -- Turnovers
    giveaways INTEGER,
    takeaways INTEGER,
    turnover_differential INTEGER,
    -- Faceoffs
    faceoffs INTEGER,
    faceoff_wins INTEGER,
    faceoff_pct DECIMAL(5,1),
    -- Zone play
    zone_entries INTEGER,
    zone_entries_successful INTEGER,
    zone_exits INTEGER,
    zone_entry_targets INTEGER,
    -- Possession
    possessions INTEGER,
    possession_time INTEGER,
    -- Micro-stats
    stick_checks INTEGER,
    poke_checks INTEGER,
    blocked_shots_play INTEGER,
    in_shot_pass_lane INTEGER,
    separate_from_puck INTEGER,
    backchecks INTEGER,
    zone_entry_denials INTEGER,
    zone_exit_denials INTEGER,
    dekes INTEGER,
    dekes_successful INTEGER,
    screens INTEGER,
    dump_and_chase INTEGER,
    drives INTEGER,
    drives_successful INTEGER,
    breakouts INTEGER,
    puck_recoveries INTEGER,
    -- Goalie stats
    saves INTEGER,
    goals_against INTEGER,
    save_pct DECIMAL(5,1),
    -- Skill context
    avg_opp_skill_faced DECIMAL(4,2),
    skill_vs_opponents DECIMAL(4,2),
    -- Per-60 rates
    goals_per_60 DECIMAL(5,2),
    assists_per_60 DECIMAL(5,2),
    points_per_60 DECIMAL(5,2),
    shots_per_60 DECIMAL(5,2),
    shots_on_goal_per_60 DECIMAL(5,2),
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id),
    FOREIGN KEY (player_game_key) REFERENCES dim_game_players(player_game_key)
);

COMMENT ON TABLE fact_box_score IS 'Comprehensive player statistics with advanced metrics';

-- fact_linked_events: Shot→Save→Rebound chains
CREATE TABLE IF NOT EXISTS fact_linked_events (
    chain_id VARCHAR(40) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    linked_event_index INTEGER NOT NULL,
    first_event INTEGER,
    last_event INTEGER,
    event_count INTEGER,
    chain_type VARCHAR(30),
    event_types TEXT,
    event_details TEXT,
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id)
);

-- fact_sequences: Possession sequence chains
CREATE TABLE IF NOT EXISTS fact_sequences (
    sequence_key VARCHAR(40) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    sequence_index INTEGER NOT NULL,
    first_event INTEGER,
    last_event INTEGER,
    event_count INTEGER,
    shift_index INTEGER,
    event_types TEXT,
    event_details TEXT,
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id)
);

-- fact_plays: Play-level chains
CREATE TABLE IF NOT EXISTS fact_plays (
    play_key VARCHAR(40) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    play_index INTEGER NOT NULL,
    first_event INTEGER,
    last_event INTEGER,
    event_count INTEGER,
    event_types TEXT,
    event_details TEXT,
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id)
);

-- fact_gameroster: Game rosters (from BLB)
CREATE TABLE IF NOT EXISTS fact_gameroster (
    roster_key VARCHAR(50) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    team_game_id VARCHAR(30),
    player_game_id VARCHAR(30),
    team_venue VARCHAR(10),
    team_name VARCHAR(100),
    opp_team_name VARCHAR(100),
    player_game_number INTEGER,
    player_position VARCHAR(20),
    games_played INTEGER,
    goals INTEGER,
    assists INTEGER,
    goals_against INTEGER,
    pim INTEGER,
    player_full_name VARCHAR(200),
    player_id VARCHAR(20),
    game_date DATE,
    season VARCHAR(20),
    skill_rating DECIMAL(3,1),
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id)
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_shifts_game ON fact_shifts(game_id);
CREATE INDEX IF NOT EXISTS idx_shift_players_shift ON fact_shift_players(shift_key);
CREATE INDEX IF NOT EXISTS idx_shift_players_player ON fact_shift_players(player_game_key);
CREATE INDEX IF NOT EXISTS idx_events_game ON fact_events(game_id);
CREATE INDEX IF NOT EXISTS idx_events_shift ON fact_events(shift_key);
CREATE INDEX IF NOT EXISTS idx_event_players_event ON fact_event_players(event_key);
CREATE INDEX IF NOT EXISTS idx_event_players_player ON fact_event_players(player_game_key);
CREATE INDEX IF NOT EXISTS idx_box_score_game ON fact_box_score(game_id);
