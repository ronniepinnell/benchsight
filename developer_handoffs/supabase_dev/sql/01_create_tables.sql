-- BenchSight Database Schema
-- Run this script to create all tables in Supabase
-- Order matters due to foreign key dependencies

-- ============================================
-- DIMENSION TABLES (No dependencies)
-- ============================================

-- dim_player: Player master data
CREATE TABLE IF NOT EXISTS dim_player (
    player_id VARCHAR(20) PRIMARY KEY,
    player_name VARCHAR(100),
    jersey_number INTEGER,
    position VARCHAR(20),
    team_id VARCHAR(20),
    shoots VARCHAR(5),
    created_at TIMESTAMP DEFAULT NOW()
);

-- dim_team: Team master data
CREATE TABLE IF NOT EXISTS dim_team (
    team_id VARCHAR(20) PRIMARY KEY,
    team_name VARCHAR(100),
    team_abbrev VARCHAR(10),
    division VARCHAR(50),
    conference VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- dim_schedule: Game schedule
CREATE TABLE IF NOT EXISTS dim_schedule (
    game_id INTEGER PRIMARY KEY,
    game_date DATE,
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    home_team_id VARCHAR(20),
    away_team_id VARCHAR(20),
    home_score INTEGER,
    away_score INTEGER,
    venue VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Final',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- FACT TABLES (With dependencies)
-- ============================================

-- fact_shifts: Shift data (depends on dim_schedule)
CREATE TABLE IF NOT EXISTS fact_shifts (
    shift_key VARCHAR(20) PRIMARY KEY,
    game_id INTEGER REFERENCES dim_schedule(game_id),
    shift_index INTEGER,
    period INTEGER,
    shift_start_seconds INTEGER,
    shift_end_seconds INTEGER,
    shift_duration INTEGER,
    shift_start_type VARCHAR(50),
    shift_stop_type VARCHAR(100),
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    home_1 INTEGER,
    home_2 INTEGER,
    home_3 INTEGER,
    home_4 INTEGER,
    home_5 INTEGER,
    home_6 INTEGER,
    away_1 INTEGER,
    away_2 INTEGER,
    away_3 INTEGER,
    away_4 INTEGER,
    away_5 INTEGER,
    away_6 INTEGER,
    home_goalie INTEGER,
    away_goalie INTEGER,
    home_team_strength INTEGER DEFAULT 5,
    away_team_strength INTEGER DEFAULT 5,
    home_team_en BOOLEAN DEFAULT FALSE,
    away_team_en BOOLEAN DEFAULT FALSE,
    situation VARCHAR(50),
    strength VARCHAR(10),
    home_goals INTEGER DEFAULT 0,
    away_goals INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- fact_events: Wide format events (depends on dim_schedule, fact_shifts)
CREATE TABLE IF NOT EXISTS fact_events (
    event_key VARCHAR(20) PRIMARY KEY,
    game_id INTEGER REFERENCES dim_schedule(game_id),
    shift_key VARCHAR(20) REFERENCES fact_shifts(shift_key),
    event_index INTEGER,
    tracking_event_index INTEGER,
    period INTEGER,
    event_start_seconds INTEGER,
    event_end_seconds INTEGER,
    event_type VARCHAR(50),
    event_detail VARCHAR(100),
    event_detail_2 VARCHAR(100),
    event_successful CHAR(1),
    play_detail1 VARCHAR(100),
    play_detail2 VARCHAR(100),
    event_team_zone VARCHAR(20),
    home_team_zone VARCHAR(20),
    away_team_zone VARCHAR(20),
    team_venue VARCHAR(10),
    sequence_index INTEGER,
    play_index INTEGER,
    linked_event_index INTEGER,
    zone_change_index INTEGER,
    event_team_player_1 INTEGER,
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
    event_team_player_1_id VARCHAR(20),
    opp_team_player_1_id VARCHAR(20),
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    empty_net_goal BOOLEAN DEFAULT FALSE,
    running_video_time INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- fact_events_player: Long format events (depends on fact_events, dim_player)
CREATE TABLE IF NOT EXISTS fact_events_player (
    event_player_key VARCHAR(30) PRIMARY KEY,
    event_key VARCHAR(20) REFERENCES fact_events(event_key),
    game_id INTEGER REFERENCES dim_schedule(game_id),
    player_id VARCHAR(20) REFERENCES dim_player(player_id),
    player_name VARCHAR(100),
    player_team VARCHAR(100),
    player_role VARCHAR(30),
    role_number INTEGER,
    event_index INTEGER,
    period INTEGER,
    event_type VARCHAR(50),
    event_detail VARCHAR(100),
    event_detail_2 VARCHAR(100),
    event_successful CHAR(1),
    play_detail1 VARCHAR(100),
    linked_event_index INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- fact_shifts_player: Player-shift assignments
CREATE TABLE IF NOT EXISTS fact_shifts_player (
    shift_player_key VARCHAR(30) PRIMARY KEY,
    shift_key VARCHAR(20) REFERENCES fact_shifts(shift_key),
    game_id INTEGER REFERENCES dim_schedule(game_id),
    player_id VARCHAR(20) REFERENCES dim_player(player_id),
    player_name VARCHAR(100),
    team_name VARCHAR(100),
    position_slot VARCHAR(20),
    is_goalie BOOLEAN DEFAULT FALSE,
    shift_index INTEGER,
    shift_duration INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- fact_player_game_stats: Player aggregations (29 columns)
CREATE TABLE IF NOT EXISTS fact_player_game_stats (
    player_game_key VARCHAR(30) PRIMARY KEY,
    game_id INTEGER REFERENCES dim_schedule(game_id),
    player_id VARCHAR(20) REFERENCES dim_player(player_id),
    player_name VARCHAR(100),
    team_id VARCHAR(20),
    team_name VARCHAR(100),
    jersey_number INTEGER,
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    shots INTEGER DEFAULT 0,
    sog INTEGER DEFAULT 0,
    shooting_pct DECIMAL(5,2),
    fo_wins INTEGER DEFAULT 0,
    fo_losses INTEGER DEFAULT 0,
    fo_pct DECIMAL(5,2),
    zone_entries INTEGER DEFAULT 0,
    zone_entries_controlled INTEGER DEFAULT 0,
    zone_entry_control_pct DECIMAL(5,2),
    pass_attempts INTEGER DEFAULT 0,
    pass_completed INTEGER DEFAULT 0,
    pass_pct DECIMAL(5,2),
    giveaways INTEGER DEFAULT 0,
    takeaways INTEGER DEFAULT 0,
    shift_count INTEGER DEFAULT 0,
    logical_shifts INTEGER DEFAULT 0,
    toi_seconds INTEGER DEFAULT 0,
    avg_shift_seconds DECIMAL(6,2),
    plus_minus INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- fact_team_game_stats: Team aggregations (18 columns)
CREATE TABLE IF NOT EXISTS fact_team_game_stats (
    team_game_key VARCHAR(30) PRIMARY KEY,
    game_id INTEGER REFERENCES dim_schedule(game_id),
    team_id VARCHAR(20) REFERENCES dim_team(team_id),
    team_name VARCHAR(100),
    venue VARCHAR(10),
    goals INTEGER DEFAULT 0,
    shots INTEGER DEFAULT 0,
    sog INTEGER DEFAULT 0,
    shooting_pct DECIMAL(5,2),
    fo_wins INTEGER DEFAULT 0,
    fo_losses INTEGER DEFAULT 0,
    fo_pct DECIMAL(5,2),
    pass_attempts INTEGER DEFAULT 0,
    pass_completed INTEGER DEFAULT 0,
    pass_pct DECIMAL(5,2),
    giveaways INTEGER DEFAULT 0,
    takeaways INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- fact_goalie_game_stats: Goalie stats with microstats (19 columns)
CREATE TABLE IF NOT EXISTS fact_goalie_game_stats (
    goalie_game_key VARCHAR(30) PRIMARY KEY,
    game_id INTEGER REFERENCES dim_schedule(game_id),
    player_id VARCHAR(20) REFERENCES dim_player(player_id),
    player_name VARCHAR(100),
    team_name VARCHAR(100),
    jersey_number INTEGER,
    saves INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    shots_against INTEGER DEFAULT 0,
    save_pct DECIMAL(5,3),
    toi_seconds INTEGER DEFAULT 0,
    empty_net_ga INTEGER DEFAULT 0,
    saves_rebound INTEGER DEFAULT 0,
    saves_freeze INTEGER DEFAULT 0,
    saves_glove INTEGER DEFAULT 0,
    saves_blocker INTEGER DEFAULT 0,
    saves_left_pad INTEGER DEFAULT 0,
    saves_right_pad INTEGER DEFAULT 0,
    rebound_control_pct DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- fact_h2h: Head-to-head matchups
CREATE TABLE IF NOT EXISTS fact_h2h (
    h2h_key VARCHAR(50) PRIMARY KEY,
    game_id INTEGER REFERENCES dim_schedule(game_id),
    player_1_id VARCHAR(20) REFERENCES dim_player(player_id),
    player_2_id VARCHAR(20) REFERENCES dim_player(player_id),
    player_1_name VARCHAR(100),
    player_2_name VARCHAR(100),
    player_1_team VARCHAR(100),
    player_2_team VARCHAR(100),
    shifts_together INTEGER DEFAULT 0,
    toi_together INTEGER DEFAULT 0,
    gf INTEGER DEFAULT 0,
    ga INTEGER DEFAULT 0,
    cf INTEGER DEFAULT 0,
    ca INTEGER DEFAULT 0,
    cf_pct DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- fact_wowy: With-or-without-you analysis
CREATE TABLE IF NOT EXISTS fact_wowy (
    wowy_key VARCHAR(50) PRIMARY KEY,
    game_id INTEGER REFERENCES dim_schedule(game_id),
    player_1_id VARCHAR(20) REFERENCES dim_player(player_id),
    player_2_id VARCHAR(20) REFERENCES dim_player(player_id),
    player_1_name VARCHAR(100),
    player_2_name VARCHAR(100),
    team_name VARCHAR(100),
    shifts_with INTEGER DEFAULT 0,
    shifts_without INTEGER DEFAULT 0,
    toi_with INTEGER DEFAULT 0,
    toi_without INTEGER DEFAULT 0,
    cf_with INTEGER DEFAULT 0,
    ca_with INTEGER DEFAULT 0,
    cf_without INTEGER DEFAULT 0,
    ca_without INTEGER DEFAULT 0,
    cf_pct_with DECIMAL(5,2),
    cf_pct_without DECIMAL(5,2),
    cf_pct_diff DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXES for query performance
-- ============================================

CREATE INDEX IF NOT EXISTS idx_events_game ON fact_events(game_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON fact_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_period ON fact_events(period);
CREATE INDEX IF NOT EXISTS idx_events_player_player ON fact_events_player(player_id);
CREATE INDEX IF NOT EXISTS idx_events_player_game ON fact_events_player(game_id);
CREATE INDEX IF NOT EXISTS idx_shifts_game ON fact_shifts(game_id);
CREATE INDEX IF NOT EXISTS idx_shifts_player_player ON fact_shifts_player(player_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_game ON fact_player_game_stats(game_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_player ON fact_player_game_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_team_stats_game ON fact_team_game_stats(game_id);
CREATE INDEX IF NOT EXISTS idx_team_stats_team ON fact_team_game_stats(team_id);
CREATE INDEX IF NOT EXISTS idx_goalie_stats_game ON fact_goalie_game_stats(game_id);
CREATE INDEX IF NOT EXISTS idx_goalie_stats_player ON fact_goalie_game_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_h2h_game ON fact_h2h(game_id);
CREATE INDEX IF NOT EXISTS idx_h2h_player1 ON fact_h2h(player_1_id);
CREATE INDEX IF NOT EXISTS idx_h2h_player2 ON fact_h2h(player_2_id);
CREATE INDEX IF NOT EXISTS idx_wowy_game ON fact_wowy(game_id);
CREATE INDEX IF NOT EXISTS idx_wowy_player1 ON fact_wowy(player_1_id);

-- ============================================
-- END OF SCHEMA
-- ============================================
