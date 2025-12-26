-- BenchSight Hockey Analytics
-- Complete PostgreSQL Schema
-- Generated: December 26, 2025

-- ============================================
-- DROP EXISTING TABLES (for clean rebuild)
-- ============================================
DROP SCHEMA IF EXISTS benchsight CASCADE;
CREATE SCHEMA benchsight;
SET search_path TO benchsight;

-- ============================================
-- DIMENSION TABLES
-- ============================================

-- Player dimension
CREATE TABLE dim_player (
    player_id VARCHAR(20) PRIMARY KEY,
    player_first_name VARCHAR(100),
    player_last_name VARCHAR(100),
    player_full_name VARCHAR(200),
    player_primary_position VARCHAR(20),
    current_skill_rating DECIMAL(3,1),
    player_hand VARCHAR(10),
    birth_year INTEGER,
    player_gender CHAR(1),
    highest_beer_league VARCHAR(50),
    player_rating_ly DECIMAL(3,1),
    player_notes TEXT,
    player_leadership VARCHAR(10),
    player_norad CHAR(1),
    player_csaha CHAR(1),
    player_norad_primary_number INTEGER,
    player_csah_primary_number INTEGER,
    player_norad_current_team VARCHAR(50),
    player_csah_current_team VARCHAR(50),
    player_norad_current_team_id VARCHAR(20),
    player_csah_current_team_id VARCHAR(20),
    player_url VARCHAR(500),
    player_image VARCHAR(500),
    random_player_first_name VARCHAR(100),
    random_player_last_name VARCHAR(100),
    random_player_full_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Team dimension
CREATE TABLE dim_team (
    team_id VARCHAR(20) PRIMARY KEY,
    team_name VARCHAR(100),
    long_team_name VARCHAR(200),
    team_cd VARCHAR(10),
    norad_team CHAR(1),
    csah_team CHAR(1),
    league_id VARCHAR(20),
    league VARCHAR(50),
    team_color1 VARCHAR(20),
    team_color2 VARCHAR(20),
    team_color3 VARCHAR(20),
    team_color4 VARCHAR(20),
    team_logo VARCHAR(500),
    team_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Season dimension
CREATE TABLE dim_season (
    season_id VARCHAR(20) PRIMARY KEY,
    season VARCHAR(20),
    session VARCHAR(50),
    norad CHAR(1),
    csah CHAR(1),
    league_id VARCHAR(20),
    league VARCHAR(50),
    start_date DATE,
    end_date DATE
);

-- League dimension
CREATE TABLE dim_league (
    league_id VARCHAR(20) PRIMARY KEY,
    league VARCHAR(50)
);

-- Date dimension
CREATE TABLE dim_dates (
    date_key INTEGER PRIMARY KEY,
    date DATE UNIQUE,
    day INTEGER,
    day_suffix VARCHAR(5),
    weekday INTEGER,
    weekday_name VARCHAR(20),
    weekday_name_short VARCHAR(5),
    weekday_name_first_letter CHAR(1),
    day_of_month INTEGER,
    day_of_year INTEGER,
    week_of_month INTEGER,
    week_of_year INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    month_name_short VARCHAR(5),
    month_name_first_letter CHAR(1),
    quarter INTEGER,
    quarter_name VARCHAR(10),
    year INTEGER,
    yearmo INTEGER,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);

-- Game/Schedule dimension
CREATE TABLE dim_game (
    game_id INTEGER PRIMARY KEY,
    season VARCHAR(20),
    season_id VARCHAR(20),
    game_url VARCHAR(500),
    date DATE,
    game_time TIME,
    home_team_id VARCHAR(20),
    away_team_id VARCHAR(20),
    home_team_name VARCHAR(100),
    away_team_name VARCHAR(100),
    home_total_goals INTEGER,
    away_total_goals INTEGER,
    home_team_period1_goals INTEGER,
    home_team_period2_goals INTEGER,
    home_team_period3_goals INTEGER,
    home_team_periodOT_goals INTEGER,
    away_team_period1_goals INTEGER,
    away_team_period2_goals INTEGER,
    away_team_period3_goals INTEGER,
    away_team_periodOT_goals INTEGER,
    game_type VARCHAR(20),
    playoff_round VARCHAR(50),
    last_period_type VARCHAR(20),
    period_length INTERVAL,
    ot_period_length INTERVAL,
    video_id VARCHAR(100),
    video_url VARCHAR(500),
    video_start_time INTEGER,
    video_end_time INTEGER,
    video_title VARCHAR(500),
    FOREIGN KEY (home_team_id) REFERENCES dim_team(team_id),
    FOREIGN KEY (away_team_id) REFERENCES dim_team(team_id),
    FOREIGN KEY (season_id) REFERENCES dim_season(season_id)
);

-- Rink coordinate zones
CREATE TABLE dim_rinkzone (
    zone_id INTEGER PRIMARY KEY,
    zone_id_rev INTEGER,
    x_min DECIMAL(10,2),
    x_max DECIMAL(10,2),
    y_min DECIMAL(10,2),
    y_max DECIMAL(10,2),
    x_description VARCHAR(100),
    y_description VARCHAR(100),
    zone_name VARCHAR(50),
    area DECIMAL(10,2)
);

-- Event type reference
CREATE TABLE dim_event_type (
    event_type_id SERIAL PRIMARY KEY,
    event_type VARCHAR(50),
    event_category VARCHAR(50),
    is_shot BOOLEAN DEFAULT FALSE,
    is_goal BOOLEAN DEFAULT FALSE,
    is_corsi BOOLEAN DEFAULT FALSE,
    is_fenwick BOOLEAN DEFAULT FALSE,
    description TEXT
);

-- Random names for privacy mode
CREATE TABLE dim_random_names (
    random_name_id SERIAL PRIMARY KEY,
    random_full_name VARCHAR(200),
    random_first_name VARCHAR(100),
    random_last_name VARCHAR(100),
    gender CHAR(1),
    name_used BOOLEAN DEFAULT FALSE
);

-- ============================================
-- FACT TABLES
-- ============================================

-- Game roster fact
CREATE TABLE fact_game_roster (
    roster_id SERIAL PRIMARY KEY,
    game_id INTEGER,
    team_id VARCHAR(20),
    player_id VARCHAR(20),
    jersey_number INTEGER,
    position VARCHAR(20),
    is_starter BOOLEAN,
    is_captain BOOLEAN,
    is_alternate BOOLEAN,
    FOREIGN KEY (game_id) REFERENCES dim_game(game_id),
    FOREIGN KEY (team_id) REFERENCES dim_team(team_id),
    FOREIGN KEY (player_id) REFERENCES dim_player(player_id)
);

-- Play-by-play fact (main event table)
CREATE TABLE fact_playbyplay (
    event_id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL,
    period INTEGER,
    sequence_index INTEGER,
    play_index INTEGER,
    event_index INTEGER,
    
    -- Time
    event_start_running_sec DECIMAL(10,2),
    event_end_running_sec DECIMAL(10,2),
    event_duration_sec DECIMAL(10,2),
    clock_time_min INTEGER,
    clock_time_sec INTEGER,
    
    -- Event details
    event_type VARCHAR(50),
    event_detail_1 VARCHAR(100),
    event_detail_2 VARCHAR(100),
    event_successful BOOLEAN,
    play_detail_1 VARCHAR(100),
    play_detail_2 VARCHAR(100),
    play_detail_successful BOOLEAN,
    
    -- Players
    event_player_1_id VARCHAR(20),
    event_player_1_number INTEGER,
    event_player_2_id VARCHAR(20),
    event_player_2_number INTEGER,
    
    -- Teams
    event_team_id VARCHAR(20),
    event_zone VARCHAR(10),
    
    -- Flags
    event_category VARCHAR(50),
    is_goal BOOLEAN DEFAULT FALSE,
    is_shot BOOLEAN DEFAULT FALSE,
    is_save BOOLEAN DEFAULT FALSE,
    is_turnover BOOLEAN DEFAULT FALSE,
    is_zone_entry BOOLEAN DEFAULT FALSE,
    is_zone_exit BOOLEAN DEFAULT FALSE,
    is_true_giveaway BOOLEAN DEFAULT FALSE,
    is_takeaway BOOLEAN DEFAULT FALSE,
    is_faceoff BOOLEAN DEFAULT FALSE,
    
    -- XY coordinates
    x_coord DECIMAL(10,2),
    y_coord DECIMAL(10,2),
    x_coord_net DECIMAL(10,2),
    y_coord_net DECIMAL(10,2),
    
    -- Video
    video_timestamp_sec INTEGER,
    
    -- Linked events
    linked_event_id INTEGER,
    
    -- Metadata
    etl_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_layer VARCHAR(20),
    
    FOREIGN KEY (game_id) REFERENCES dim_game(game_id),
    FOREIGN KEY (event_team_id) REFERENCES dim_team(team_id),
    FOREIGN KEY (event_player_1_id) REFERENCES dim_player(player_id),
    FOREIGN KEY (event_player_2_id) REFERENCES dim_player(player_id)
);

-- Shifts fact
CREATE TABLE fact_shifts (
    shift_id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL,
    period INTEGER,
    shift_index INTEGER,
    
    -- Time
    shift_start_running_sec DECIMAL(10,2),
    shift_end_running_sec DECIMAL(10,2),
    shift_duration_sec DECIMAL(10,2),
    
    -- Team & strength
    team_id VARCHAR(20),
    strength VARCHAR(10),  -- '5v5', '5v4', '4v5', etc.
    
    -- On-ice players (positions)
    center_id VARCHAR(20),
    left_wing_id VARCHAR(20),
    right_wing_id VARCHAR(20),
    left_defense_id VARCHAR(20),
    right_defense_id VARCHAR(20),
    goalie_id VARCHAR(20),
    
    -- Ratings context
    avg_team_rating DECIMAL(3,1),
    avg_opp_rating DECIMAL(3,1),
    rating_differential DECIMAL(3,1),
    
    -- Metadata
    etl_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (game_id) REFERENCES dim_game(game_id),
    FOREIGN KEY (team_id) REFERENCES dim_team(team_id)
);

-- Player shifts (individual player on-ice time)
CREATE TABLE fact_player_shifts (
    player_shift_id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL,
    shift_id INTEGER,
    player_id VARCHAR(20),
    period INTEGER,
    
    -- Time
    shift_start_running_sec DECIMAL(10,2),
    shift_end_running_sec DECIMAL(10,2),
    shift_duration_sec DECIMAL(10,2),
    
    -- Position during shift
    position VARCHAR(20),
    
    -- Rating context
    player_rating DECIMAL(3,1),
    avg_teammate_rating DECIMAL(3,1),
    avg_opponent_rating DECIMAL(3,1),
    
    FOREIGN KEY (game_id) REFERENCES dim_game(game_id),
    FOREIGN KEY (shift_id) REFERENCES fact_shifts(shift_id),
    FOREIGN KEY (player_id) REFERENCES dim_player(player_id)
);

-- Video timestamps fact
CREATE TABLE fact_video_times (
    video_time_id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL,
    event_type VARCHAR(50),
    event_description VARCHAR(200),
    period INTEGER,
    game_time_min INTEGER,
    game_time_sec INTEGER,
    video_timestamp_sec INTEGER,
    video_url VARCHAR(500),
    camera_angle VARCHAR(50),
    notes TEXT,
    
    FOREIGN KEY (game_id) REFERENCES dim_game(game_id)
);

-- XY event locations fact
CREATE TABLE fact_event_xy (
    xy_id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL,
    event_id INTEGER,
    
    -- Rink coordinates
    x_coord DECIMAL(10,2),
    y_coord DECIMAL(10,2),
    zone_id INTEGER,
    
    -- Net coordinates (for shots)
    x_coord_net DECIMAL(10,2),
    y_coord_net DECIMAL(10,2),
    
    -- Calculated
    distance_to_net DECIMAL(10,2),
    angle_to_net DECIMAL(10,2),
    
    FOREIGN KEY (game_id) REFERENCES dim_game(game_id),
    FOREIGN KEY (event_id) REFERENCES fact_playbyplay(event_id),
    FOREIGN KEY (zone_id) REFERENCES dim_rinkzone(zone_id)
);

-- XY puck tracking fact (for CV data)
CREATE TABLE fact_puck_tracking (
    tracking_id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL,
    frame_number INTEGER,
    timestamp_sec DECIMAL(10,3),
    
    x_coord DECIMAL(10,2),
    y_coord DECIMAL(10,2),
    
    confidence DECIMAL(5,4),
    source VARCHAR(20),  -- 'manual', 'cv', 'interpolated'
    
    FOREIGN KEY (game_id) REFERENCES dim_game(game_id)
);

-- Missing data log fact
CREATE TABLE fact_missing_data_log (
    log_id SERIAL PRIMARY KEY,
    game_id INTEGER,
    log_type VARCHAR(50),  -- 'missing_event', 'missing_shift', 'missing_video', etc.
    entity_type VARCHAR(50),
    entity_id VARCHAR(50),
    description TEXT,
    severity VARCHAR(20),  -- 'warning', 'error', 'info'
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP
);

-- Player game statistics (aggregated)
CREATE TABLE fact_player_game_stats (
    stat_id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL,
    player_id VARCHAR(20) NOT NULL,
    team_id VARCHAR(20),
    
    -- Basic stats
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    primary_assists INTEGER DEFAULT 0,
    secondary_assists INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    shots INTEGER DEFAULT 0,
    shots_on_goal INTEGER DEFAULT 0,
    
    -- Time on ice
    toi_seconds DECIMAL(10,2) DEFAULT 0,
    toi_minutes DECIMAL(10,2) DEFAULT 0,
    shifts INTEGER DEFAULT 0,
    avg_shift_length_sec DECIMAL(10,2) DEFAULT 0,
    
    -- Advanced stats
    corsi_for INTEGER DEFAULT 0,
    corsi_against INTEGER DEFAULT 0,
    corsi_pct DECIMAL(5,2),
    fenwick_for INTEGER DEFAULT 0,
    fenwick_against INTEGER DEFAULT 0,
    fenwick_pct DECIMAL(5,2),
    
    -- Micro stats
    zone_entries INTEGER DEFAULT 0,
    zone_entries_successful INTEGER DEFAULT 0,
    zone_entry_success_pct DECIMAL(5,2),
    controlled_entries INTEGER DEFAULT 0,
    dump_entries INTEGER DEFAULT 0,
    zone_exits INTEGER DEFAULT 0,
    zone_exits_successful INTEGER DEFAULT 0,
    controlled_exits INTEGER DEFAULT 0,
    
    passes INTEGER DEFAULT 0,
    passes_successful INTEGER DEFAULT 0,
    pass_completion_pct DECIMAL(5,2),
    
    true_giveaways INTEGER DEFAULT 0,
    takeaways INTEGER DEFAULT 0,
    
    -- Possession
    possession_time_sec DECIMAL(10,2) DEFAULT 0,
    possession_events INTEGER DEFAULT 0,
    
    -- Rating context
    avg_opponent_rating DECIMAL(3,1),
    avg_teammate_rating DECIMAL(3,1),
    quality_of_competition DECIMAL(3,1),
    
    -- Plus/minus
    plus_minus INTEGER DEFAULT 0,
    goals_for INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    
    FOREIGN KEY (game_id) REFERENCES dim_game(game_id),
    FOREIGN KEY (player_id) REFERENCES dim_player(player_id),
    FOREIGN KEY (team_id) REFERENCES dim_team(team_id)
);

-- Team game statistics (aggregated)
CREATE TABLE fact_team_game_stats (
    stat_id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL,
    team_id VARCHAR(20) NOT NULL,
    
    -- Score
    goals_for INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    
    -- Shots
    shots_for INTEGER DEFAULT 0,
    shots_against INTEGER DEFAULT 0,
    shots_on_goal_for INTEGER DEFAULT 0,
    shots_on_goal_against INTEGER DEFAULT 0,
    
    -- Corsi/Fenwick
    corsi_for INTEGER DEFAULT 0,
    corsi_against INTEGER DEFAULT 0,
    corsi_pct DECIMAL(5,2),
    fenwick_for INTEGER DEFAULT 0,
    fenwick_against INTEGER DEFAULT 0,
    fenwick_pct DECIMAL(5,2),
    
    -- Zone play
    zone_entries INTEGER DEFAULT 0,
    zone_entries_against INTEGER DEFAULT 0,
    controlled_entry_pct DECIMAL(5,2),
    zone_exits INTEGER DEFAULT 0,
    zone_exits_against INTEGER DEFAULT 0,
    
    -- Possession
    possession_time_sec DECIMAL(10,2),
    possession_pct DECIMAL(5,2),
    
    -- Special teams
    power_play_opportunities INTEGER DEFAULT 0,
    power_play_goals INTEGER DEFAULT 0,
    power_play_pct DECIMAL(5,2),
    penalty_kill_opportunities INTEGER DEFAULT 0,
    penalty_kill_goals_against INTEGER DEFAULT 0,
    penalty_kill_pct DECIMAL(5,2),
    
    -- Faceoffs
    faceoffs_won INTEGER DEFAULT 0,
    faceoffs_lost INTEGER DEFAULT 0,
    faceoff_pct DECIMAL(5,2),
    
    FOREIGN KEY (game_id) REFERENCES dim_game(game_id),
    FOREIGN KEY (team_id) REFERENCES dim_team(team_id)
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_playbyplay_game ON fact_playbyplay(game_id);
CREATE INDEX idx_playbyplay_type ON fact_playbyplay(event_type);
CREATE INDEX idx_playbyplay_sequence ON fact_playbyplay(game_id, sequence_index);
CREATE INDEX idx_shifts_game ON fact_shifts(game_id);
CREATE INDEX idx_player_shifts_game ON fact_player_shifts(game_id);
CREATE INDEX idx_player_shifts_player ON fact_player_shifts(player_id);
CREATE INDEX idx_player_stats_game ON fact_player_game_stats(game_id);
CREATE INDEX idx_player_stats_player ON fact_player_game_stats(player_id);
CREATE INDEX idx_team_stats_game ON fact_team_game_stats(game_id);
CREATE INDEX idx_video_game ON fact_video_times(game_id);
CREATE INDEX idx_event_xy_event ON fact_event_xy(event_id);

-- ============================================
-- VIEWS
-- ============================================

-- Current game summary view
CREATE VIEW vw_game_summary AS
SELECT 
    g.game_id,
    g.date,
    g.home_team_name,
    g.away_team_name,
    g.home_total_goals,
    g.away_total_goals,
    g.video_url,
    COALESCE(ts_home.shots_for, 0) as home_shots,
    COALESCE(ts_away.shots_for, 0) as away_shots
FROM dim_game g
LEFT JOIN fact_team_game_stats ts_home 
    ON g.game_id = ts_home.game_id AND g.home_team_id = ts_home.team_id
LEFT JOIN fact_team_game_stats ts_away 
    ON g.game_id = ts_away.game_id AND g.away_team_id = ts_away.team_id;

-- Player career stats view
CREATE VIEW vw_player_career_stats AS
SELECT 
    p.player_id,
    p.player_full_name,
    p.current_skill_rating,
    p.player_image,
    COUNT(DISTINCT pgs.game_id) as games_played,
    SUM(pgs.goals) as total_goals,
    SUM(pgs.assists) as total_assists,
    SUM(pgs.points) as total_points,
    AVG(pgs.corsi_pct) as avg_corsi_pct,
    SUM(pgs.toi_minutes) as total_toi_minutes
FROM dim_player p
LEFT JOIN fact_player_game_stats pgs ON p.player_id = pgs.player_id
GROUP BY p.player_id, p.player_full_name, p.current_skill_rating, p.player_image;

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON SCHEMA benchsight IS 'BenchSight Hockey Analytics - Complete data warehouse';
COMMENT ON TABLE fact_playbyplay IS 'Main play-by-play event fact table with all tracked events';
COMMENT ON TABLE fact_player_game_stats IS 'Aggregated player statistics per game including advanced and micro stats';
COMMENT ON COLUMN fact_player_game_stats.true_giveaways IS 'Only player-caused turnovers (excludes dumps)';
COMMENT ON COLUMN fact_shifts.rating_differential IS 'Team avg rating minus opponent avg rating for shift context';
