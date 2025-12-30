-- ================================================================
-- BenchSight Master SQL Operations
-- Complete schema management for Supabase PostgreSQL
-- 
-- USAGE: Run sections as needed, not the entire file at once
-- ================================================================

-- ████████████████████████████████████████████████████████████████
-- SECTION 1: SCHEMA MANAGEMENT
-- ████████████████████████████████████████████████████████████████

-- ================================================================
-- 1A: CREATE SCHEMA (Optional - Supabase uses 'public' by default)
-- ================================================================
-- CREATE SCHEMA IF NOT EXISTS benchsight;
-- SET search_path TO benchsight, public;

-- ================================================================
-- 1B: DROP ENTIRE SCHEMA (DANGER - Deletes everything!)
-- ================================================================
-- Uncomment to execute:
/*
DROP SCHEMA IF EXISTS benchsight CASCADE;
CREATE SCHEMA benchsight;
*/

-- ████████████████████████████████████████████████████████████████
-- SECTION 2: DROP ALL TABLES (Reverse dependency order)
-- ████████████████████████████████████████████████████████████████

-- ================================================================
-- 2A: DROP ALL - Safest order (handles FK dependencies)
-- ================================================================
-- Admin/Staging tables first
DROP TABLE IF EXISTS load_history CASCADE;
DROP TABLE IF EXISTS etl_queue CASCADE;
DROP TABLE IF EXISTS staging_shifts CASCADE;
DROP TABLE IF EXISTS staging_events CASCADE;

-- Analytics facts
DROP TABLE IF EXISTS fact_wowy CASCADE;
DROP TABLE IF EXISTS fact_h2h CASCADE;

-- Stats facts
DROP TABLE IF EXISTS fact_goalie_game_stats CASCADE;
DROP TABLE IF EXISTS fact_team_game_stats CASCADE;
DROP TABLE IF EXISTS fact_player_game_stats CASCADE;

-- Long format facts
DROP TABLE IF EXISTS fact_shifts_player CASCADE;
DROP TABLE IF EXISTS fact_events_player CASCADE;

-- Core facts
DROP TABLE IF EXISTS fact_events CASCADE;
DROP TABLE IF EXISTS fact_shifts CASCADE;

-- Dimensions last
DROP TABLE IF EXISTS dim_schedule CASCADE;
DROP TABLE IF EXISTS dim_team CASCADE;
DROP TABLE IF EXISTS dim_player CASCADE;

-- ================================================================
-- 2B: DROP ALL - Quick version (CASCADE handles dependencies)
-- ================================================================
/*
DROP TABLE IF EXISTS 
    load_history, etl_queue, staging_shifts, staging_events,
    fact_wowy, fact_h2h, 
    fact_goalie_game_stats, fact_team_game_stats, fact_player_game_stats,
    fact_shifts_player, fact_events_player, fact_events, fact_shifts,
    dim_schedule, dim_team, dim_player
CASCADE;
*/

-- ████████████████████████████████████████████████████████████████
-- SECTION 3: CREATE DIMENSION TABLES
-- ████████████████████████████████████████████████████████████████

-- ================================================================
-- 3A: DIM_PLAYER (337 rows, 28 columns)
-- ================================================================
CREATE TABLE IF NOT EXISTS dim_player (
    player_id VARCHAR(20) PRIMARY KEY,
    player_full_name VARCHAR(200),
    player_first_name VARCHAR(100),
    player_last_name VARCHAR(100),
    player_name VARCHAR(200),
    jersey_number INTEGER,
    team_id VARCHAR(20),
    team_name VARCHAR(100),
    player_primary_position VARCHAR(50),
    position_category VARCHAR(20),
    is_goalie BOOLEAN DEFAULT FALSE,
    is_skater BOOLEAN DEFAULT TRUE,
    height_inches INTEGER,
    weight_lbs INTEGER,
    birth_date DATE,
    birth_city VARCHAR(100),
    birth_state VARCHAR(50),
    birth_country VARCHAR(50),
    shoots VARCHAR(10),
    catches VARCHAR(10),
    rookie_year INTEGER,
    draft_year INTEGER,
    draft_round INTEGER,
    draft_pick INTEGER,
    profile_url TEXT,
    photo_url TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- 3B: DIM_TEAM (26 rows, 15 columns)
-- ================================================================
CREATE TABLE IF NOT EXISTS dim_team (
    team_id VARCHAR(20) PRIMARY KEY,
    team_name VARCHAR(100),
    team_short_name VARCHAR(50),
    team_abbreviation VARCHAR(10),
    division VARCHAR(50),
    conference VARCHAR(50),
    league_id VARCHAR(20),
    league_name VARCHAR(100),
    season_id VARCHAR(20),
    arena_name VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(50),
    primary_color VARCHAR(20),
    secondary_color VARCHAR(20),
    logo_url TEXT
);

-- ================================================================
-- 3C: DIM_SCHEDULE (562 rows, 44 columns - Historical league data)
-- ================================================================
CREATE TABLE IF NOT EXISTS dim_schedule (
    game_id INTEGER PRIMARY KEY,
    season_id VARCHAR(20),
    league_id VARCHAR(20),
    game_type VARCHAR(20),
    game_number INTEGER,
    date DATE,
    time TIME,
    day_of_week VARCHAR(15),
    venue VARCHAR(100),
    
    -- Teams
    home_team_id VARCHAR(20),
    home_team_name VARCHAR(100),
    away_team_id VARCHAR(20),
    away_team_name VARCHAR(100),
    
    -- Final scores
    home_total_goals INTEGER,
    away_total_goals INTEGER,
    home_regulation_goals INTEGER,
    away_regulation_goals INTEGER,
    
    -- Period scores
    home_p1_goals INTEGER,
    away_p1_goals INTEGER,
    home_p2_goals INTEGER,
    away_p2_goals INTEGER,
    home_p3_goals INTEGER,
    away_p3_goals INTEGER,
    home_ot_goals INTEGER,
    away_ot_goals INTEGER,
    home_so_goals INTEGER,
    away_so_goals INTEGER,
    
    -- Game result
    winner VARCHAR(100),
    loser VARCHAR(100),
    winning_team_id VARCHAR(20),
    game_decided_by VARCHAR(20),
    went_to_ot BOOLEAN DEFAULT FALSE,
    went_to_so BOOLEAN DEFAULT FALSE,
    
    -- Tracking status
    is_tracked BOOLEAN DEFAULT FALSE,
    tracking_status VARCHAR(50),
    tracking_file_path TEXT,
    events_count INTEGER,
    shifts_count INTEGER,
    
    -- Video
    video_url_1 TEXT,
    video_url_2 TEXT,
    video_start_offset INTEGER,
    
    -- Metadata
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ████████████████████████████████████████████████████████████████
-- SECTION 4: CREATE CORE FACT TABLES
-- ████████████████████████████████████████████████████████████████

-- ================================================================
-- 4A: FACT_SHIFTS (672 rows, 63 columns)
-- ================================================================
CREATE TABLE IF NOT EXISTS fact_shifts (
    shift_key VARCHAR(50) PRIMARY KEY,  -- S{game_id}{shift_index:05d}
    game_id INTEGER NOT NULL,
    shift_index INTEGER NOT NULL,
    period INTEGER,
    
    -- Timing
    shift_start_seconds INTEGER,
    shift_end_seconds INTEGER,
    shift_duration INTEGER,
    shift_start_min INTEGER,
    shift_start_sec INTEGER,
    shift_end_min INTEGER,
    shift_end_sec INTEGER,
    
    -- Shift boundaries
    shift_start_type VARCHAR(50),
    shift_stop_type VARCHAR(100),
    
    -- Home players (player_id references)
    home_forward_1 VARCHAR(20),
    home_forward_2 VARCHAR(20),
    home_forward_3 VARCHAR(20),
    home_defense_1 VARCHAR(20),
    home_defense_2 VARCHAR(20),
    home_xtra VARCHAR(20),
    home_goalie VARCHAR(20),
    
    -- Away players (player_id references)
    away_forward_1 VARCHAR(20),
    away_forward_2 VARCHAR(20),
    away_forward_3 VARCHAR(20),
    away_defense_1 VARCHAR(20),
    away_defense_2 VARCHAR(20),
    away_xtra VARCHAR(20),
    away_goalie VARCHAR(20),
    
    -- Strength situation
    home_team_strength INTEGER DEFAULT 5,
    away_team_strength INTEGER DEFAULT 5,
    home_team_en BOOLEAN DEFAULT FALSE,
    away_team_en BOOLEAN DEFAULT FALSE,
    situation VARCHAR(50),
    strength VARCHAR(10),
    
    -- Teams
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    home_team_id VARCHAR(20),
    away_team_id VARCHAR(20),
    
    -- Score at shift
    home_goals INTEGER DEFAULT 0,
    away_goals INTEGER DEFAULT 0,
    goal_diff INTEGER,
    
    -- Shift statistics
    events_in_shift INTEGER DEFAULT 0,
    shots_in_shift INTEGER DEFAULT 0,
    goals_in_shift INTEGER DEFAULT 0,
    
    -- Corsi/Fenwick for shift
    home_corsi INTEGER DEFAULT 0,
    away_corsi INTEGER DEFAULT 0,
    home_fenwick INTEGER DEFAULT 0,
    away_fenwick INTEGER DEFAULT 0,
    
    -- Zone time in shift
    home_ozone_seconds INTEGER DEFAULT 0,
    home_dzone_seconds INTEGER DEFAULT 0,
    home_nzone_seconds INTEGER DEFAULT 0,
    away_ozone_seconds INTEGER DEFAULT 0,
    away_dzone_seconds INTEGER DEFAULT 0,
    away_nzone_seconds INTEGER DEFAULT 0,
    
    -- Video sync
    video_start_time INTEGER,
    video_end_time INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- 4B: FACT_EVENTS (5,833 rows, 54 columns)
-- ================================================================
CREATE TABLE IF NOT EXISTS fact_events (
    event_key VARCHAR(50) PRIMARY KEY,  -- E{game_id}{event_index:05d}
    game_id INTEGER NOT NULL,
    event_index INTEGER NOT NULL,
    period INTEGER,
    
    -- Timing
    event_start_seconds INTEGER,
    event_end_seconds INTEGER,
    event_start_min INTEGER,
    event_start_sec INTEGER,
    event_duration INTEGER,
    
    -- Event classification
    event_type VARCHAR(50),
    event_detail VARCHAR(100),
    event_detail_2 VARCHAR(100),
    event_successful CHAR(1),  -- 's' or 'u'
    
    -- Play context
    sequence_index INTEGER,
    play_index INTEGER,
    play_detail1 VARCHAR(100),
    play_detail2 VARCHAR(100),
    
    -- Zone
    event_team_zone VARCHAR(20),
    
    -- Shift reference
    shift_key VARCHAR(50),
    shift_index INTEGER,
    
    -- Event linking
    linked_event_index INTEGER,
    linked_event_key VARCHAR(50),
    
    -- Teams
    event_team VARCHAR(100),
    event_team_id VARCHAR(20),
    team_venue VARCHAR(10),  -- 'Home' or 'Away'
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    
    -- Primary player (gets stat credit)
    event_team_player_1 VARCHAR(20),
    
    -- Supporting players on event team
    event_team_player_2 VARCHAR(20),
    event_team_player_3 VARCHAR(20),
    event_team_player_4 VARCHAR(20),
    event_team_player_5 VARCHAR(20),
    event_team_player_6 VARCHAR(20),
    
    -- Opponent players
    opp_team_player_1 VARCHAR(20),
    opp_team_player_2 VARCHAR(20),
    opp_team_player_3 VARCHAR(20),
    opp_team_player_4 VARCHAR(20),
    opp_team_player_5 VARCHAR(20),
    opp_team_player_6 VARCHAR(20),
    
    -- Score at event
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    
    -- XY coordinates
    puck_x DECIMAL(8,2),
    puck_y DECIMAL(8,2),
    
    -- Video sync
    running_video_time INTEGER,
    video_url TEXT,
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- 4C: FACT_EVENTS_PLAYER (11,635 rows - Long format)
-- ================================================================
CREATE TABLE IF NOT EXISTS fact_events_player (
    id SERIAL PRIMARY KEY,
    event_key VARCHAR(50) NOT NULL,
    game_id INTEGER NOT NULL,
    event_index INTEGER NOT NULL,
    player_id VARCHAR(20) NOT NULL,
    player_role VARCHAR(50),  -- 'event_team_player_1', 'opp_team_player_1', etc.
    is_primary_actor BOOLEAN DEFAULT FALSE,
    team_venue VARCHAR(10),
    period INTEGER,
    event_type VARCHAR(50),
    event_detail VARCHAR(100),
    event_successful CHAR(1),
    shift_key VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(event_key, player_id, player_role)
);

-- ================================================================
-- 4D: FACT_SHIFTS_PLAYER (4,626 rows - Long format)
-- ================================================================
CREATE TABLE IF NOT EXISTS fact_shifts_player (
    id SERIAL PRIMARY KEY,
    shift_key VARCHAR(50) NOT NULL,
    game_id INTEGER NOT NULL,
    shift_index INTEGER NOT NULL,
    player_id VARCHAR(20) NOT NULL,
    player_role VARCHAR(50),  -- 'home_forward_1', 'away_goalie', etc.
    team_venue VARCHAR(10),
    position_slot VARCHAR(20),
    period INTEGER,
    shift_duration INTEGER,
    situation VARCHAR(50),
    strength VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(shift_key, player_id)
);

-- ████████████████████████████████████████████████████████████████
-- SECTION 5: CREATE STATS FACT TABLES
-- ████████████████████████████████████████████████████████████████

-- ================================================================
-- 5A: FACT_PLAYER_GAME_STATS (107 rows, 317 columns!)
-- This is generated dynamically - see generate_sql.py
-- Key columns shown below, full table has 317 columns
-- ================================================================
CREATE TABLE IF NOT EXISTS fact_player_game_stats (
    player_game_key VARCHAR(50) PRIMARY KEY,  -- PG{game_id}{player_id}
    game_id INTEGER NOT NULL,
    player_id VARCHAR(20) NOT NULL,
    player_full_name VARCHAR(200),
    team_id VARCHAR(20),
    team_name VARCHAR(100),
    team_venue VARCHAR(10),
    player_primary_position VARCHAR(50),
    is_goalie BOOLEAN DEFAULT FALSE,
    
    -- Core stats
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    plus_minus INTEGER DEFAULT 0,
    
    -- Shots
    shots INTEGER DEFAULT 0,
    shots_on_goal INTEGER DEFAULT 0,
    shots_blocked INTEGER DEFAULT 0,
    shots_missed INTEGER DEFAULT 0,
    shooting_pct DECIMAL(10,4),
    
    -- TOI
    toi_seconds INTEGER DEFAULT 0,
    toi_minutes DECIMAL(10,2),
    shifts INTEGER DEFAULT 0,
    avg_shift_length DECIMAL(10,2),
    
    -- Faceoffs
    fo_taken INTEGER DEFAULT 0,
    fo_wins INTEGER DEFAULT 0,
    fo_losses INTEGER DEFAULT 0,
    fo_pct DECIMAL(10,4),
    
    -- Physical
    hits INTEGER DEFAULT 0,
    hits_taken INTEGER DEFAULT 0,
    blocks INTEGER DEFAULT 0,
    
    -- Possession
    giveaways INTEGER DEFAULT 0,
    takeaways INTEGER DEFAULT 0,
    turnovers INTEGER DEFAULT 0,
    
    -- Zone entries/exits
    zone_entries INTEGER DEFAULT 0,
    zone_entries_successful INTEGER DEFAULT 0,
    zone_exits INTEGER DEFAULT 0,
    zone_exits_successful INTEGER DEFAULT 0,
    
    -- Corsi/Fenwick
    cf INTEGER DEFAULT 0,
    ca INTEGER DEFAULT 0,
    cf_pct DECIMAL(10,4),
    ff INTEGER DEFAULT 0,
    fa INTEGER DEFAULT 0,
    ff_pct DECIMAL(10,4),
    
    -- Per 60 stats (sample - full table has many more)
    goals_per_60 DECIMAL(10,4),
    assists_per_60 DECIMAL(10,4),
    points_per_60 DECIMAL(10,4),
    shots_per_60 DECIMAL(10,4),
    
    -- Situational (5v5, PP, PK, etc.)
    toi_5v5 INTEGER DEFAULT 0,
    goals_5v5 INTEGER DEFAULT 0,
    toi_pp INTEGER DEFAULT 0,
    goals_pp INTEGER DEFAULT 0,
    toi_pk INTEGER DEFAULT 0,
    goals_pk INTEGER DEFAULT 0,
    
    -- NOTE: Full table has 317 columns
    -- Run generate_sql.py to create complete table from CSV
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- 5B: FACT_TEAM_GAME_STATS (8 rows, 52 columns)
-- ================================================================
CREATE TABLE IF NOT EXISTS fact_team_game_stats (
    team_game_key VARCHAR(50) PRIMARY KEY,  -- TG{game_id}{team_id}
    game_id INTEGER NOT NULL,
    team_id VARCHAR(20) NOT NULL,
    team_name VARCHAR(100),
    team_venue VARCHAR(10),
    opponent_id VARCHAR(20),
    opponent_name VARCHAR(100),
    
    -- Result
    goals_for INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    result CHAR(1),  -- 'W', 'L', 'T'
    
    -- Shots
    shots_for INTEGER DEFAULT 0,
    shots_against INTEGER DEFAULT 0,
    shots_on_goal_for INTEGER DEFAULT 0,
    shots_on_goal_against INTEGER DEFAULT 0,
    
    -- Corsi/Fenwick
    cf INTEGER DEFAULT 0,
    ca INTEGER DEFAULT 0,
    cf_pct DECIMAL(10,4),
    ff INTEGER DEFAULT 0,
    fa INTEGER DEFAULT 0,
    ff_pct DECIMAL(10,4),
    
    -- Special teams
    pp_goals INTEGER DEFAULT 0,
    pp_opportunities INTEGER DEFAULT 0,
    pp_pct DECIMAL(10,4),
    pk_goals_against INTEGER DEFAULT 0,
    pk_opportunities INTEGER DEFAULT 0,
    pk_pct DECIMAL(10,4),
    
    -- Faceoffs
    fo_wins INTEGER DEFAULT 0,
    fo_taken INTEGER DEFAULT 0,
    fo_pct DECIMAL(10,4),
    
    -- Physical
    hits INTEGER DEFAULT 0,
    blocks INTEGER DEFAULT 0,
    pim INTEGER DEFAULT 0,
    
    -- Zone time
    ozone_time INTEGER DEFAULT 0,
    dzone_time INTEGER DEFAULT 0,
    nzone_time INTEGER DEFAULT 0,
    ozone_pct DECIMAL(10,4),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- 5C: FACT_GOALIE_GAME_STATS (8 rows, 19 columns)
-- ================================================================
CREATE TABLE IF NOT EXISTS fact_goalie_game_stats (
    goalie_game_key VARCHAR(50) PRIMARY KEY,  -- GG{game_id}{player_id}
    game_id INTEGER NOT NULL,
    player_id VARCHAR(20) NOT NULL,
    player_full_name VARCHAR(200),
    team_id VARCHAR(20),
    team_name VARCHAR(100),
    team_venue VARCHAR(10),
    
    -- Core stats
    shots_against INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    save_pct DECIMAL(10,4),
    
    -- Result
    result CHAR(1),  -- 'W', 'L'
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    
    -- TOI
    toi_seconds INTEGER DEFAULT 0,
    toi_minutes DECIMAL(10,2),
    
    -- By period
    saves_p1 INTEGER DEFAULT 0,
    saves_p2 INTEGER DEFAULT 0,
    saves_p3 INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- ████████████████████████████████████████████████████████████████
-- SECTION 6: CREATE ANALYTICS FACT TABLES
-- ████████████████████████████████████████████████████████████████

-- ================================================================
-- 6A: FACT_H2H - Head to Head (684 rows, 24 columns)
-- ================================================================
CREATE TABLE IF NOT EXISTS fact_h2h (
    h2h_key VARCHAR(50) PRIMARY KEY,  -- H2H{game_id}{player1_id}{player2_id}
    game_id INTEGER NOT NULL,
    player_1_id VARCHAR(20) NOT NULL,
    player_1_name VARCHAR(200),
    player_2_id VARCHAR(20) NOT NULL,
    player_2_name VARCHAR(200),
    same_team BOOLEAN,
    
    -- Time together
    toi_together INTEGER DEFAULT 0,
    shifts_together INTEGER DEFAULT 0,
    
    -- Stats when together
    goals_for INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    cf INTEGER DEFAULT 0,
    ca INTEGER DEFAULT 0,
    cf_pct DECIMAL(10,4),
    ff INTEGER DEFAULT 0,
    fa INTEGER DEFAULT 0,
    ff_pct DECIMAL(10,4),
    
    -- Zone stats
    ozone_starts INTEGER DEFAULT 0,
    dzone_starts INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- 6B: FACT_WOWY - With Or Without You (641 rows, 28 columns)
-- ================================================================
CREATE TABLE IF NOT EXISTS fact_wowy (
    wowy_key VARCHAR(50) PRIMARY KEY,  -- WOWY{game_id}{player1_id}{player2_id}
    game_id INTEGER NOT NULL,
    player_1_id VARCHAR(20) NOT NULL,
    player_1_name VARCHAR(200),
    player_2_id VARCHAR(20) NOT NULL,
    player_2_name VARCHAR(200),
    
    -- With partner
    toi_with INTEGER DEFAULT 0,
    cf_with INTEGER DEFAULT 0,
    ca_with INTEGER DEFAULT 0,
    cf_pct_with DECIMAL(10,4),
    gf_with INTEGER DEFAULT 0,
    ga_with INTEGER DEFAULT 0,
    
    -- Without partner
    toi_without INTEGER DEFAULT 0,
    cf_without INTEGER DEFAULT 0,
    ca_without INTEGER DEFAULT 0,
    cf_pct_without DECIMAL(10,4),
    gf_without INTEGER DEFAULT 0,
    ga_without INTEGER DEFAULT 0,
    
    -- Differentials
    cf_pct_diff DECIMAL(10,4),
    gf_pct_diff DECIMAL(10,4),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- ████████████████████████████████████████████████████████████████
-- SECTION 7: CREATE STAGING & ADMIN TABLES
-- ████████████████████████████████████████████████████████████████

-- ================================================================
-- 7A: STAGING_EVENTS (Tracker writes here)
-- ================================================================
CREATE TABLE IF NOT EXISTS staging_events (
    event_key VARCHAR(50) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    event_index INTEGER NOT NULL,
    period INTEGER,
    event_start_seconds INTEGER,
    event_end_seconds INTEGER,
    event_type VARCHAR(50),
    event_detail VARCHAR(100),
    event_detail_2 VARCHAR(100),
    event_successful CHAR(1),
    event_team_player_1 INTEGER,  -- Jersey number from tracker
    event_team_player_2 INTEGER,
    event_team_player_3 INTEGER,
    event_team_player_4 INTEGER,
    event_team_player_5 INTEGER,
    event_team_player_6 INTEGER,
    opp_team_player_1 INTEGER,
    opp_team_player_2 INTEGER,
    opp_team_player_3 INTEGER,
    opp_team_player_4 INTEGER,
    opp_team_player_5 INTEGER,
    opp_team_player_6 INTEGER,
    shift_index INTEGER,
    linked_event_index INTEGER,
    play_detail1 VARCHAR(100),
    play_detail2 VARCHAR(100),
    event_team_zone VARCHAR(20),
    puck_x DECIMAL(8,2),
    puck_y DECIMAL(8,2),
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- 7B: STAGING_SHIFTS (Tracker writes here)
-- ================================================================
CREATE TABLE IF NOT EXISTS staging_shifts (
    shift_key VARCHAR(50) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    shift_index INTEGER NOT NULL,
    period INTEGER,
    shift_start_seconds INTEGER,
    shift_end_seconds INTEGER,
    shift_duration INTEGER,
    shift_start_type VARCHAR(50),
    shift_stop_type VARCHAR(100),
    home_forward_1 INTEGER,
    home_forward_2 INTEGER,
    home_forward_3 INTEGER,
    home_defense_1 INTEGER,
    home_defense_2 INTEGER,
    home_xtra INTEGER,
    home_goalie INTEGER,
    away_forward_1 INTEGER,
    away_forward_2 INTEGER,
    away_forward_3 INTEGER,
    away_defense_1 INTEGER,
    away_defense_2 INTEGER,
    away_xtra INTEGER,
    away_goalie INTEGER,
    home_team_strength INTEGER DEFAULT 5,
    away_team_strength INTEGER DEFAULT 5,
    situation VARCHAR(50),
    strength VARCHAR(10),
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- 7C: ETL_QUEUE (Async processing queue)
-- ================================================================
CREATE TABLE IF NOT EXISTS etl_queue (
    id SERIAL PRIMARY KEY,
    game_id INTEGER,
    operation VARCHAR(50) NOT NULL,
    tables TEXT[],
    priority INTEGER DEFAULT 5,
    status VARCHAR(20) DEFAULT 'pending',
    requested_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    rows_processed INTEGER,
    error_message TEXT,
    requested_by VARCHAR(50),
    processed_by VARCHAR(50)
);

-- ================================================================
-- 7D: LOAD_HISTORY (Audit trail)
-- ================================================================
CREATE TABLE IF NOT EXISTS load_history (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50),
    category VARCHAR(50),
    game_id INTEGER,
    operation VARCHAR(20) NOT NULL,
    source VARCHAR(50),
    rows_before INTEGER,
    rows_affected INTEGER,
    rows_after INTEGER,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    status VARCHAR(20) DEFAULT 'started',
    error_message TEXT,
    initiated_by VARCHAR(50) DEFAULT 'system',
    notes TEXT
);

-- ████████████████████████████████████████████████████████████████
-- SECTION 8: CREATE INDEXES
-- ████████████████████████████████████████████████████████████████

-- Dimension indexes
CREATE INDEX IF NOT EXISTS idx_dim_player_team ON dim_player(team_id);
CREATE INDEX IF NOT EXISTS idx_dim_player_name ON dim_player(player_full_name);
CREATE INDEX IF NOT EXISTS idx_dim_player_position ON dim_player(player_primary_position);
CREATE INDEX IF NOT EXISTS idx_dim_schedule_date ON dim_schedule(date);
CREATE INDEX IF NOT EXISTS idx_dim_schedule_teams ON dim_schedule(home_team_id, away_team_id);

-- Core fact indexes
CREATE INDEX IF NOT EXISTS idx_fact_shifts_game ON fact_shifts(game_id);
CREATE INDEX IF NOT EXISTS idx_fact_shifts_period ON fact_shifts(period);
CREATE INDEX IF NOT EXISTS idx_fact_events_game ON fact_events(game_id);
CREATE INDEX IF NOT EXISTS idx_fact_events_period ON fact_events(period);
CREATE INDEX IF NOT EXISTS idx_fact_events_type ON fact_events(event_type);
CREATE INDEX IF NOT EXISTS idx_fact_events_shift ON fact_events(shift_key);
CREATE INDEX IF NOT EXISTS idx_fact_events_player_event ON fact_events_player(event_key);
CREATE INDEX IF NOT EXISTS idx_fact_events_player_player ON fact_events_player(player_id);
CREATE INDEX IF NOT EXISTS idx_fact_events_player_game ON fact_events_player(game_id);
CREATE INDEX IF NOT EXISTS idx_fact_shifts_player_shift ON fact_shifts_player(shift_key);
CREATE INDEX IF NOT EXISTS idx_fact_shifts_player_player ON fact_shifts_player(player_id);
CREATE INDEX IF NOT EXISTS idx_fact_shifts_player_game ON fact_shifts_player(game_id);

-- Stats fact indexes
CREATE INDEX IF NOT EXISTS idx_fact_player_stats_game ON fact_player_game_stats(game_id);
CREATE INDEX IF NOT EXISTS idx_fact_player_stats_player ON fact_player_game_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_fact_player_stats_team ON fact_player_game_stats(team_id);
CREATE INDEX IF NOT EXISTS idx_fact_team_stats_game ON fact_team_game_stats(game_id);
CREATE INDEX IF NOT EXISTS idx_fact_team_stats_team ON fact_team_game_stats(team_id);
CREATE INDEX IF NOT EXISTS idx_fact_goalie_stats_game ON fact_goalie_game_stats(game_id);
CREATE INDEX IF NOT EXISTS idx_fact_goalie_stats_player ON fact_goalie_game_stats(player_id);

-- Analytics fact indexes
CREATE INDEX IF NOT EXISTS idx_fact_h2h_game ON fact_h2h(game_id);
CREATE INDEX IF NOT EXISTS idx_fact_h2h_player1 ON fact_h2h(player_1_id);
CREATE INDEX IF NOT EXISTS idx_fact_h2h_player2 ON fact_h2h(player_2_id);
CREATE INDEX IF NOT EXISTS idx_fact_wowy_game ON fact_wowy(game_id);
CREATE INDEX IF NOT EXISTS idx_fact_wowy_player1 ON fact_wowy(player_1_id);
CREATE INDEX IF NOT EXISTS idx_fact_wowy_player2 ON fact_wowy(player_2_id);

-- Staging/Admin indexes
CREATE INDEX IF NOT EXISTS idx_staging_events_game ON staging_events(game_id);
CREATE INDEX IF NOT EXISTS idx_staging_events_processed ON staging_events(processed);
CREATE INDEX IF NOT EXISTS idx_staging_shifts_game ON staging_shifts(game_id);
CREATE INDEX IF NOT EXISTS idx_staging_shifts_processed ON staging_shifts(processed);
CREATE INDEX IF NOT EXISTS idx_etl_queue_status ON etl_queue(status);
CREATE INDEX IF NOT EXISTS idx_etl_queue_priority ON etl_queue(priority DESC, requested_at);
CREATE INDEX IF NOT EXISTS idx_load_history_table ON load_history(table_name);
CREATE INDEX IF NOT EXISTS idx_load_history_status ON load_history(status);

-- ████████████████████████████████████████████████████████████████
-- SECTION 9: ADD FOREIGN KEYS (Run AFTER data is loaded)
-- ████████████████████████████████████████████████████████████████

-- NOTE: Run these AFTER loading data to avoid constraint violations
-- Use ON DELETE SET NULL for flexibility

/*
-- Fact tables → Dimensions
ALTER TABLE fact_shifts ADD CONSTRAINT fk_shifts_schedule 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id) ON DELETE SET NULL;

ALTER TABLE fact_events ADD CONSTRAINT fk_events_schedule 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id) ON DELETE SET NULL;
ALTER TABLE fact_events ADD CONSTRAINT fk_events_shift 
    FOREIGN KEY (shift_key) REFERENCES fact_shifts(shift_key) ON DELETE SET NULL;

ALTER TABLE fact_events_player ADD CONSTRAINT fk_eventsplayer_event 
    FOREIGN KEY (event_key) REFERENCES fact_events(event_key) ON DELETE CASCADE;
ALTER TABLE fact_events_player ADD CONSTRAINT fk_eventsplayer_player 
    FOREIGN KEY (player_id) REFERENCES dim_player(player_id) ON DELETE SET NULL;

ALTER TABLE fact_shifts_player ADD CONSTRAINT fk_shiftsplayer_shift 
    FOREIGN KEY (shift_key) REFERENCES fact_shifts(shift_key) ON DELETE CASCADE;
ALTER TABLE fact_shifts_player ADD CONSTRAINT fk_shiftsplayer_player 
    FOREIGN KEY (player_id) REFERENCES dim_player(player_id) ON DELETE SET NULL;

ALTER TABLE fact_player_game_stats ADD CONSTRAINT fk_playerstats_player 
    FOREIGN KEY (player_id) REFERENCES dim_player(player_id) ON DELETE SET NULL;
ALTER TABLE fact_player_game_stats ADD CONSTRAINT fk_playerstats_schedule 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id) ON DELETE SET NULL;

ALTER TABLE fact_team_game_stats ADD CONSTRAINT fk_teamstats_team 
    FOREIGN KEY (team_id) REFERENCES dim_team(team_id) ON DELETE SET NULL;
ALTER TABLE fact_team_game_stats ADD CONSTRAINT fk_teamstats_schedule 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id) ON DELETE SET NULL;

ALTER TABLE fact_goalie_game_stats ADD CONSTRAINT fk_goaliestats_player 
    FOREIGN KEY (player_id) REFERENCES dim_player(player_id) ON DELETE SET NULL;
ALTER TABLE fact_goalie_game_stats ADD CONSTRAINT fk_goaliestats_schedule 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id) ON DELETE SET NULL;

ALTER TABLE fact_h2h ADD CONSTRAINT fk_h2h_player1 
    FOREIGN KEY (player_1_id) REFERENCES dim_player(player_id) ON DELETE SET NULL;
ALTER TABLE fact_h2h ADD CONSTRAINT fk_h2h_player2 
    FOREIGN KEY (player_2_id) REFERENCES dim_player(player_id) ON DELETE SET NULL;
ALTER TABLE fact_h2h ADD CONSTRAINT fk_h2h_schedule 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id) ON DELETE SET NULL;

ALTER TABLE fact_wowy ADD CONSTRAINT fk_wowy_player1 
    FOREIGN KEY (player_1_id) REFERENCES dim_player(player_id) ON DELETE SET NULL;
ALTER TABLE fact_wowy ADD CONSTRAINT fk_wowy_player2 
    FOREIGN KEY (player_2_id) REFERENCES dim_player(player_id) ON DELETE SET NULL;
ALTER TABLE fact_wowy ADD CONSTRAINT fk_wowy_schedule 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id) ON DELETE SET NULL;
*/

-- ████████████████████████████████████████████████████████████████
-- SECTION 10: UTILITY FUNCTIONS
-- ████████████████████████████████████████████████████████████████

-- ================================================================
-- 10A: Get all table row counts
-- ================================================================
CREATE OR REPLACE FUNCTION get_all_table_counts()
RETURNS TABLE(table_name TEXT, row_count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT 'dim_player'::TEXT, COUNT(*)::BIGINT FROM dim_player
    UNION ALL SELECT 'dim_team', COUNT(*) FROM dim_team
    UNION ALL SELECT 'dim_schedule', COUNT(*) FROM dim_schedule
    UNION ALL SELECT 'fact_shifts', COUNT(*) FROM fact_shifts
    UNION ALL SELECT 'fact_events', COUNT(*) FROM fact_events
    UNION ALL SELECT 'fact_events_player', COUNT(*) FROM fact_events_player
    UNION ALL SELECT 'fact_shifts_player', COUNT(*) FROM fact_shifts_player
    UNION ALL SELECT 'fact_player_game_stats', COUNT(*) FROM fact_player_game_stats
    UNION ALL SELECT 'fact_team_game_stats', COUNT(*) FROM fact_team_game_stats
    UNION ALL SELECT 'fact_goalie_game_stats', COUNT(*) FROM fact_goalie_game_stats
    UNION ALL SELECT 'fact_h2h', COUNT(*) FROM fact_h2h
    UNION ALL SELECT 'fact_wowy', COUNT(*) FROM fact_wowy
    UNION ALL SELECT 'staging_events', COUNT(*) FROM staging_events
    UNION ALL SELECT 'staging_shifts', COUNT(*) FROM staging_shifts
    UNION ALL SELECT 'etl_queue', COUNT(*) FROM etl_queue
    UNION ALL SELECT 'load_history', COUNT(*) FROM load_history
    ORDER BY 1;
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- 10B: Delete all data for a specific game
-- ================================================================
CREATE OR REPLACE FUNCTION delete_game_data(p_game_id INTEGER)
RETURNS JSON AS $$
DECLARE
    v_total INTEGER := 0;
    v_count INTEGER;
BEGIN
    DELETE FROM fact_wowy WHERE game_id = p_game_id; GET DIAGNOSTICS v_count = ROW_COUNT; v_total := v_total + v_count;
    DELETE FROM fact_h2h WHERE game_id = p_game_id; GET DIAGNOSTICS v_count = ROW_COUNT; v_total := v_total + v_count;
    DELETE FROM fact_goalie_game_stats WHERE game_id = p_game_id; GET DIAGNOSTICS v_count = ROW_COUNT; v_total := v_total + v_count;
    DELETE FROM fact_team_game_stats WHERE game_id = p_game_id; GET DIAGNOSTICS v_count = ROW_COUNT; v_total := v_total + v_count;
    DELETE FROM fact_player_game_stats WHERE game_id = p_game_id; GET DIAGNOSTICS v_count = ROW_COUNT; v_total := v_total + v_count;
    DELETE FROM fact_shifts_player WHERE game_id = p_game_id; GET DIAGNOSTICS v_count = ROW_COUNT; v_total := v_total + v_count;
    DELETE FROM fact_events_player WHERE game_id = p_game_id; GET DIAGNOSTICS v_count = ROW_COUNT; v_total := v_total + v_count;
    DELETE FROM fact_events WHERE game_id = p_game_id; GET DIAGNOSTICS v_count = ROW_COUNT; v_total := v_total + v_count;
    DELETE FROM fact_shifts WHERE game_id = p_game_id; GET DIAGNOSTICS v_count = ROW_COUNT; v_total := v_total + v_count;
    DELETE FROM staging_events WHERE game_id = p_game_id; GET DIAGNOSTICS v_count = ROW_COUNT; v_total := v_total + v_count;
    DELETE FROM staging_shifts WHERE game_id = p_game_id; GET DIAGNOSTICS v_count = ROW_COUNT; v_total := v_total + v_count;
    
    RETURN json_build_object('success', true, 'game_id', p_game_id, 'rows_deleted', v_total);
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- 10C: Truncate all fact tables (keep dimensions)
-- ================================================================
CREATE OR REPLACE FUNCTION truncate_all_facts()
RETURNS JSON AS $$
BEGIN
    TRUNCATE TABLE fact_wowy, fact_h2h, 
                   fact_goalie_game_stats, fact_team_game_stats, fact_player_game_stats,
                   fact_shifts_player, fact_events_player, fact_events, fact_shifts,
                   staging_events, staging_shifts CASCADE;
    RETURN json_build_object('success', true, 'message', 'All fact tables truncated');
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- 10D: Get games with tracking status
-- ================================================================
CREATE OR REPLACE FUNCTION get_games_status()
RETURNS TABLE(
    game_id INTEGER,
    game_date DATE,
    matchup TEXT,
    events_count BIGINT,
    shifts_count BIGINT,
    has_stats BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.game_id,
        s.date,
        s.home_team_name || ' vs ' || s.away_team_name,
        COALESCE(e.cnt, 0)::BIGINT,
        COALESCE(sh.cnt, 0)::BIGINT,
        COALESCE(ps.cnt, 0) > 0
    FROM dim_schedule s
    LEFT JOIN (SELECT game_id, COUNT(*) as cnt FROM fact_events GROUP BY game_id) e ON s.game_id = e.game_id
    LEFT JOIN (SELECT game_id, COUNT(*) as cnt FROM fact_shifts GROUP BY game_id) sh ON s.game_id = sh.game_id
    LEFT JOIN (SELECT game_id, COUNT(*) as cnt FROM fact_player_game_stats GROUP BY game_id) ps ON s.game_id = ps.game_id
    WHERE s.is_tracked = TRUE OR COALESCE(e.cnt, 0) > 0
    ORDER BY s.date DESC;
END;
$$ LANGUAGE plpgsql;

-- ████████████████████████████████████████████████████████████████
-- SECTION 11: VALIDATION QUERIES
-- ████████████████████████████████████████████████████████████████

-- Run these after loading to verify data quality

-- 11A: Check row counts
SELECT * FROM get_all_table_counts();

-- 11B: Check for orphaned foreign keys
/*
SELECT 'fact_events orphans' as check_name, COUNT(*) as orphan_count
FROM fact_events e 
LEFT JOIN dim_schedule s ON e.game_id = s.game_id 
WHERE s.game_id IS NULL;

SELECT 'fact_player_game_stats orphans' as check_name, COUNT(*) as orphan_count
FROM fact_player_game_stats ps 
LEFT JOIN dim_player p ON ps.player_id = p.player_id 
WHERE p.player_id IS NULL;
*/

-- 11C: Check percentage ranges
/*
SELECT 'Invalid shooting_pct' as check_name, COUNT(*) as invalid_count
FROM fact_player_game_stats 
WHERE shooting_pct < 0 OR shooting_pct > 100;

SELECT 'Invalid cf_pct' as check_name, COUNT(*) as invalid_count
FROM fact_player_game_stats 
WHERE cf_pct < 0 OR cf_pct > 100;
*/

-- 11D: Business logic validation
/*
SELECT 'Points != Goals + Assists' as check_name, COUNT(*) as invalid_count
FROM fact_player_game_stats 
WHERE points != goals + assists;
*/

-- ████████████████████████████████████████████████████████████████
-- END OF MASTER SQL OPERATIONS FILE
-- ████████████████████████████████████████████████████████████████
