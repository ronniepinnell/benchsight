-- ================================================================
-- BenchSight Staging Tables
-- These tables receive writes from Tracker before ETL processing
-- ================================================================

-- Drop if exists (for clean rebuilds)
DROP TABLE IF EXISTS staging_events CASCADE;
DROP TABLE IF EXISTS staging_shifts CASCADE;
DROP TABLE IF EXISTS etl_queue CASCADE;
DROP TABLE IF EXISTS load_history CASCADE;

-- ================================================================
-- STAGING_EVENTS: Raw event writes from Tracker
-- ================================================================
CREATE TABLE staging_events (
    -- Primary key
    event_key VARCHAR(50) PRIMARY KEY,
    
    -- Core identifiers
    game_id INTEGER NOT NULL,
    event_index INTEGER NOT NULL,
    period INTEGER,
    
    -- Timing
    event_start_seconds INTEGER,
    event_end_seconds INTEGER,
    event_start_min INTEGER,
    event_start_sec INTEGER,
    
    -- Event classification
    event_type VARCHAR(50),
    event_detail VARCHAR(100),
    event_detail_2 VARCHAR(100),
    event_successful CHAR(1),  -- 's' or 'u'
    
    -- Play details
    play_detail1 VARCHAR(100),
    play_detail2 VARCHAR(100),
    event_team_zone VARCHAR(20),
    
    -- Players (jersey numbers)
    event_team_player_1 INTEGER,  -- PRIMARY - gets stat credit
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
    
    -- Relationships
    shift_index INTEGER,
    linked_event_index INTEGER,
    sequence_index INTEGER,
    play_index INTEGER,
    
    -- XY coordinates (for future)
    puck_x DECIMAL(8,2),
    puck_y DECIMAL(8,2),
    
    -- Teams
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    team_venue VARCHAR(10),  -- 'Home' or 'Away'
    
    -- Video sync
    running_video_time INTEGER,
    
    -- Processing status
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(50) DEFAULT 'tracker'
);

-- Indexes for staging_events
CREATE INDEX idx_staging_events_game ON staging_events(game_id);
CREATE INDEX idx_staging_events_processed ON staging_events(processed);
CREATE INDEX idx_staging_events_period ON staging_events(period);
CREATE INDEX idx_staging_events_type ON staging_events(event_type);

-- ================================================================
-- STAGING_SHIFTS: Raw shift writes from Tracker
-- ================================================================
CREATE TABLE staging_shifts (
    -- Primary key
    shift_key VARCHAR(50) PRIMARY KEY,
    
    -- Core identifiers
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
    
    -- Home players (jersey numbers)
    home_forward_1 INTEGER,
    home_forward_2 INTEGER,
    home_forward_3 INTEGER,
    home_defense_1 INTEGER,
    home_defense_2 INTEGER,
    home_xtra INTEGER,
    home_goalie INTEGER,
    
    -- Away players (jersey numbers)
    away_forward_1 INTEGER,
    away_forward_2 INTEGER,
    away_forward_3 INTEGER,
    away_defense_1 INTEGER,
    away_defense_2 INTEGER,
    away_xtra INTEGER,
    away_goalie INTEGER,
    
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
    
    -- Score at shift
    home_goals INTEGER DEFAULT 0,
    away_goals INTEGER DEFAULT 0,
    
    -- Processing status
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(50) DEFAULT 'tracker'
);

-- Indexes for staging_shifts
CREATE INDEX idx_staging_shifts_game ON staging_shifts(game_id);
CREATE INDEX idx_staging_shifts_processed ON staging_shifts(processed);
CREATE INDEX idx_staging_shifts_period ON staging_shifts(period);

-- ================================================================
-- ETL_QUEUE: Queue for async ETL processing
-- ================================================================
CREATE TABLE etl_queue (
    id SERIAL PRIMARY KEY,
    
    -- What to process
    game_id INTEGER,
    operation VARCHAR(50) NOT NULL,  -- 'process_game', 'full_etl', 'reprocess', etc.
    tables TEXT[],  -- Specific tables to process, NULL = all
    
    -- Processing options
    replace_existing BOOLEAN DEFAULT TRUE,
    validate_after BOOLEAN DEFAULT TRUE,
    
    -- Priority and status
    priority INTEGER DEFAULT 5,  -- 1-10, higher = more urgent
    status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, completed, failed
    
    -- Timing
    requested_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Results
    rows_processed INTEGER,
    error_message TEXT,
    output_log TEXT,
    
    -- Audit
    requested_by VARCHAR(50),
    processed_by VARCHAR(50)
);

-- Indexes for etl_queue
CREATE INDEX idx_etl_queue_status ON etl_queue(status);
CREATE INDEX idx_etl_queue_priority ON etl_queue(priority DESC, requested_at);
CREATE INDEX idx_etl_queue_game ON etl_queue(game_id);

-- ================================================================
-- LOAD_HISTORY: Audit trail for all data loading operations
-- ================================================================
CREATE TABLE load_history (
    id SERIAL PRIMARY KEY,
    
    -- What was loaded
    table_name VARCHAR(50),
    category VARCHAR(50),  -- 'dims', 'facts', 'all', etc.
    game_id INTEGER,
    
    -- Operation details
    operation VARCHAR(20) NOT NULL,  -- 'replace', 'append', 'upsert', 'delete'
    source VARCHAR(50),  -- 'csv', 'api', 'etl', 'portal'
    
    -- Results
    rows_before INTEGER,
    rows_affected INTEGER,
    rows_after INTEGER,
    
    -- Timing
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    
    -- Status
    status VARCHAR(20) DEFAULT 'started',  -- started, completed, failed
    error_message TEXT,
    
    -- Audit
    initiated_by VARCHAR(50) DEFAULT 'system',
    ip_address VARCHAR(45),
    notes TEXT
);

-- Indexes for load_history
CREATE INDEX idx_load_history_table ON load_history(table_name);
CREATE INDEX idx_load_history_status ON load_history(status);
CREATE INDEX idx_load_history_started ON load_history(started_at DESC);

-- ================================================================
-- TRIGGER: Auto-update updated_at timestamp
-- ================================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER staging_events_updated
    BEFORE UPDATE ON staging_events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER staging_shifts_updated
    BEFORE UPDATE ON staging_shifts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ================================================================
-- COMMENTS
-- ================================================================
COMMENT ON TABLE staging_events IS 'Raw event data from Tracker before ETL processing';
COMMENT ON TABLE staging_shifts IS 'Raw shift data from Tracker before ETL processing';
COMMENT ON TABLE etl_queue IS 'Queue for async ETL processing requests';
COMMENT ON TABLE load_history IS 'Audit log of all data loading operations';

COMMENT ON COLUMN staging_events.event_team_player_1 IS 'PRIMARY ACTOR - this player gets stat credit';
COMMENT ON COLUMN staging_events.processed IS 'Set to TRUE after ETL processes this event';
COMMENT ON COLUMN etl_queue.priority IS 'Processing priority 1-10, higher = more urgent';
