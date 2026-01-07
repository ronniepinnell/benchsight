-- ============================================================
-- BENCHSIGHT - SUPABASE STAGING TABLES
-- ============================================================
-- 
-- Run this SQL in your Supabase SQL Editor to create the staging
-- tables needed for the ETL to read from Supabase instead of Excel.
--
-- These tables mirror the structure of:
--   - BLB_Tables.xlsx sheets
--   - {game_id}_tracking.xlsx events/shifts sheets
--
-- After creating tables, populate them with your data, then run:
--   python etl.py --source supabase
--
-- ============================================================

-- ============================================================
-- BLB DIMENSION TABLES (from BLB_Tables.xlsx)
-- ============================================================

CREATE TABLE IF NOT EXISTS stage_dim_player (
    player_id TEXT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT,
    email TEXT,
    current_skill_rating INTEGER,
    player_rating_ly INTEGER,
    position TEXT,
    shoots TEXT,
    birthdate TEXT,
    height TEXT,
    weight TEXT,
    hometown TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stage_dim_team (
    team_id TEXT PRIMARY KEY,
    team_name TEXT,
    team_name_short TEXT,
    team_abbreviation TEXT,
    league_id TEXT,
    division TEXT,
    conference TEXT,
    home_arena TEXT,
    primary_color TEXT,
    secondary_color TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stage_dim_league (
    league_id TEXT PRIMARY KEY,
    league_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stage_dim_season (
    season_id TEXT PRIMARY KEY,
    season_name TEXT,
    season_year TEXT,
    start_date TEXT,
    end_date TEXT,
    league_id TEXT,
    is_current BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stage_dim_schedule (
    game_id TEXT PRIMARY KEY,
    season_id TEXT,
    game_date TEXT,
    game_time TEXT,
    home_team TEXT,
    away_team TEXT,
    home_team_id TEXT,
    away_team_id TEXT,
    venue TEXT,
    game_type TEXT,
    home_score INTEGER,
    away_score INTEGER,
    game_status TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stage_dim_playerurlref (
    player_id TEXT,
    url_type TEXT,
    url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stage_dim_rinkboxcoord (
    coord_id TEXT PRIMARY KEY,
    x_min NUMERIC,
    x_max NUMERIC,
    y_min NUMERIC,
    y_max NUMERIC,
    zone_name TEXT,
    zone_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stage_dim_rinkcoordzones (
    zone_id TEXT PRIMARY KEY,
    zone_name TEXT,
    zone_type TEXT,
    x_center NUMERIC,
    y_center NUMERIC,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stage_dim_randomnames (
    id SERIAL PRIMARY KEY,
    random_name TEXT,
    name_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- BLB FACT TABLES (from BLB_Tables.xlsx)
-- ============================================================

CREATE TABLE IF NOT EXISTS stage_fact_gameroster (
    player_game_id TEXT PRIMARY KEY,
    game_id TEXT,
    player_id TEXT,
    team_name TEXT,
    team_id TEXT,
    player_game_number TEXT,
    position TEXT,
    is_starter BOOLEAN,
    is_captain BOOLEAN,
    is_alternate BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gameroster_game ON stage_fact_gameroster(game_id);
CREATE INDEX IF NOT EXISTS idx_gameroster_player ON stage_fact_gameroster(player_id);

CREATE TABLE IF NOT EXISTS stage_fact_leadership (
    id SERIAL PRIMARY KEY,
    player_id TEXT,
    team_id TEXT,
    season_id TEXT,
    role TEXT,
    start_date TEXT,
    end_date TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stage_fact_registration (
    player_season_registration_id TEXT PRIMARY KEY,
    player_id TEXT,
    season_id TEXT,
    team_id TEXT,
    registration_date TEXT,
    position TEXT,
    jersey_number TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stage_fact_draft (
    player_draft_id TEXT PRIMARY KEY,
    player_id TEXT,
    season_id TEXT,
    draft_round INTEGER,
    draft_pick INTEGER,
    team_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stage_fact_playergames (
    player_game_id TEXT PRIMARY KEY,
    game_id TEXT,
    player_id TEXT,
    team_id TEXT,
    goals INTEGER,
    assists INTEGER,
    points INTEGER,
    plus_minus INTEGER,
    pim INTEGER,
    shots INTEGER,
    hits INTEGER,
    blocks INTEGER,
    faceoff_wins INTEGER,
    faceoff_losses INTEGER,
    toi_seconds INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_playergames_game ON stage_fact_playergames(game_id);
CREATE INDEX IF NOT EXISTS idx_playergames_player ON stage_fact_playergames(player_id);

-- ============================================================
-- TRACKING TABLES (from {game_id}_tracking.xlsx)
-- ============================================================

CREATE TABLE IF NOT EXISTS stage_events_tracking (
    id SERIAL PRIMARY KEY,
    game_id TEXT NOT NULL,
    tracking_event_index TEXT,
    period TEXT,
    event_start_min TEXT,
    event_start_sec TEXT,
    event_end_min TEXT,
    event_end_sec TEXT,
    "Type" TEXT,  -- Event type (quoted because Type is reserved)
    event_detail TEXT,
    event_detail_2 TEXT,
    event_successful TEXT,
    player_game_number TEXT,
    team_venue TEXT,
    team_venue_abv TEXT,
    role_abrev TEXT,
    event_team_zone TEXT,
    home_team_zone TEXT,
    away_team_zone TEXT,
    side_of_puck TEXT,
    sequence_index TEXT,
    play_index TEXT,
    play_detail1 TEXT,
    play_detail_2 TEXT,
    play_detail_successful TEXT,
    pressured_pressurer TEXT,
    zone_change_index TEXT,
    linked_event_index TEXT,
    shift_index TEXT,
    home_team TEXT,
    away_team TEXT,
    duration TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_game ON stage_events_tracking(game_id);
CREATE INDEX IF NOT EXISTS idx_events_tracking_idx ON stage_events_tracking(tracking_event_index);

CREATE TABLE IF NOT EXISTS stage_shifts_tracking (
    id SERIAL PRIMARY KEY,
    game_id TEXT NOT NULL,
    shift_index TEXT,
    "Period" TEXT,  -- Period (quoted for consistency)
    shift_start_type TEXT,
    shift_stop_type TEXT,
    shift_start_min TEXT,
    shift_start_sec TEXT,
    shift_end_min TEXT,
    shift_end_sec TEXT,
    home_team TEXT,
    away_team TEXT,
    home_forward_1 TEXT,
    home_forward_2 TEXT,
    home_forward_3 TEXT,
    home_defense_1 TEXT,
    home_defense_2 TEXT,
    home_goalie TEXT,
    away_forward_1 TEXT,
    away_forward_2 TEXT,
    away_forward_3 TEXT,
    away_defense_1 TEXT,
    away_defense_2 TEXT,
    away_goalie TEXT,
    strength TEXT,
    situation TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_shifts_game ON stage_shifts_tracking(game_id);
CREATE INDEX IF NOT EXISTS idx_shifts_idx ON stage_shifts_tracking(shift_index);

-- ============================================================
-- HELPER VIEWS
-- ============================================================

-- View to see available games with tracking data
CREATE OR REPLACE VIEW v_available_games AS
SELECT DISTINCT game_id, 
       COUNT(*) as event_count,
       MIN(created_at) as first_loaded
FROM stage_events_tracking
GROUP BY game_id
ORDER BY game_id;

-- View to check data completeness
CREATE OR REPLACE VIEW v_stage_data_summary AS
SELECT 
    'stage_dim_player' as table_name, COUNT(*) as row_count FROM stage_dim_player
UNION ALL SELECT 'stage_dim_team', COUNT(*) FROM stage_dim_team
UNION ALL SELECT 'stage_dim_league', COUNT(*) FROM stage_dim_league
UNION ALL SELECT 'stage_dim_season', COUNT(*) FROM stage_dim_season
UNION ALL SELECT 'stage_dim_schedule', COUNT(*) FROM stage_dim_schedule
UNION ALL SELECT 'stage_fact_gameroster', COUNT(*) FROM stage_fact_gameroster
UNION ALL SELECT 'stage_fact_playergames', COUNT(*) FROM stage_fact_playergames
UNION ALL SELECT 'stage_events_tracking', COUNT(*) FROM stage_events_tracking
UNION ALL SELECT 'stage_shifts_tracking', COUNT(*) FROM stage_shifts_tracking
ORDER BY table_name;

-- ============================================================
-- ROW LEVEL SECURITY (optional, enable as needed)
-- ============================================================

-- Enable RLS on all tables
-- ALTER TABLE stage_dim_player ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE stage_events_tracking ENABLE ROW LEVEL SECURITY;
-- etc.

-- ============================================================
-- USAGE NOTES
-- ============================================================
-- 
-- 1. Run this script in your Supabase SQL Editor
-- 
-- 2. Populate the tables:
--    - Import from CSV using Supabase Dashboard
--    - Or use the Python scripts to upload
--    - Or use pg_dump/pg_restore from your local DB
--
-- 3. Test with:
--    python etl.py --source supabase --discover-games
--
-- 4. Run full ETL:
--    python etl.py --source supabase
--
-- ============================================================
