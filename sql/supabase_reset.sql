-- ============================================================================
-- BENCHSIGHT SUPABASE RESET SCRIPT
-- Run this to completely reset the database and start fresh
-- ============================================================================

-- ============================================================================
-- STEP 1: DROP ALL EXISTING TABLES (in reverse dependency order)
-- ============================================================================

-- Drop fact tables first (they reference dims)
DROP TABLE IF EXISTS public.fact_player_game_stats CASCADE;
DROP TABLE IF EXISTS public.fact_goalie_game_stats CASCADE;
DROP TABLE IF EXISTS public.fact_team_game_stats CASCADE;
DROP TABLE IF EXISTS public.fact_events_player CASCADE;
DROP TABLE IF EXISTS public.fact_events CASCADE;
DROP TABLE IF EXISTS public.fact_shifts_player CASCADE;
DROP TABLE IF EXISTS public.fact_shifts CASCADE;
DROP TABLE IF EXISTS public.fact_gameroster CASCADE;
DROP TABLE IF EXISTS public.fact_playergames CASCADE;
DROP TABLE IF EXISTS public.fact_sequences CASCADE;
DROP TABLE IF EXISTS public.fact_plays CASCADE;
DROP TABLE IF EXISTS public.fact_draft CASCADE;
DROP TABLE IF EXISTS public.fact_registration CASCADE;
DROP TABLE IF EXISTS public.fact_leadership CASCADE;
DROP TABLE IF EXISTS public.fact_head_to_head CASCADE;
DROP TABLE IF EXISTS public.fact_player_pair_stats CASCADE;
DROP TABLE IF EXISTS public.fact_player_boxscore_all CASCADE;
DROP TABLE IF EXISTS public.fact_league_leaders_snapshot CASCADE;
DROP TABLE IF EXISTS public.fact_team_standings_snapshot CASCADE;

-- Drop dimension tables
DROP TABLE IF EXISTS public.dim_player CASCADE;
DROP TABLE IF EXISTS public.dim_team CASCADE;
DROP TABLE IF EXISTS public.dim_league CASCADE;
DROP TABLE IF EXISTS public.dim_season CASCADE;
DROP TABLE IF EXISTS public.dim_schedule CASCADE;
DROP TABLE IF EXISTS public.dim_position CASCADE;
DROP TABLE IF EXISTS public.dim_venue CASCADE;
DROP TABLE IF EXISTS public.dim_zone CASCADE;
DROP TABLE IF EXISTS public.dim_period CASCADE;
DROP TABLE IF EXISTS public.dim_event_type CASCADE;
DROP TABLE IF EXISTS public.dim_event_detail CASCADE;
DROP TABLE IF EXISTS public.dim_event_detail_2 CASCADE;
DROP TABLE IF EXISTS public.dim_play_detail CASCADE;
DROP TABLE IF EXISTS public.dim_play_detail_2 CASCADE;
DROP TABLE IF EXISTS public.dim_player_role CASCADE;
DROP TABLE IF EXISTS public.dim_situation CASCADE;
DROP TABLE IF EXISTS public.dim_strength CASCADE;
DROP TABLE IF EXISTS public.dim_shift_slot CASCADE;
DROP TABLE IF EXISTS public.dim_shift_start_type CASCADE;
DROP TABLE IF EXISTS public.dim_shift_stop_type CASCADE;
DROP TABLE IF EXISTS public.dim_stoppage_type CASCADE;
DROP TABLE IF EXISTS public.dim_zone_entry_type CASCADE;
DROP TABLE IF EXISTS public.dim_zone_exit_type CASCADE;
DROP TABLE IF EXISTS public.dim_shot_type CASCADE;
DROP TABLE IF EXISTS public.dim_pass_type CASCADE;
DROP TABLE IF EXISTS public.dim_giveaway_type CASCADE;
DROP TABLE IF EXISTS public.dim_takeaway_type CASCADE;
DROP TABLE IF EXISTS public.dim_turnover_type CASCADE;
DROP TABLE IF EXISTS public.dim_turnover_quality CASCADE;
DROP TABLE IF EXISTS public.dim_comparison_type CASCADE;
DROP TABLE IF EXISTS public.dim_net_location CASCADE;
DROP TABLE IF EXISTS public.dim_stat CASCADE;
DROP TABLE IF EXISTS public.dim_stat_type CASCADE;
DROP TABLE IF EXISTS public.dim_success CASCADE;
DROP TABLE IF EXISTS public.dim_playerurlref CASCADE;
DROP TABLE IF EXISTS public.dim_rinkboxcoord CASCADE;
DROP TABLE IF EXISTS public.dim_rinkcoordzones CASCADE;
DROP TABLE IF EXISTS public.dim_randomnames CASCADE;
DROP TABLE IF EXISTS public.dim_terminology_mapping CASCADE;

-- ============================================================================
-- STEP 2: CREATE DIMENSION TABLES
-- ============================================================================

-- Players
CREATE TABLE public.dim_player (
    player_id TEXT PRIMARY KEY,
    player_full_name TEXT,
    first_name TEXT,
    last_name TEXT,
    current_team TEXT,
    position TEXT,
    skill_rating NUMERIC,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Teams
CREATE TABLE public.dim_team (
    team_id TEXT PRIMARY KEY,
    team_name TEXT,
    team_abbrev TEXT,
    league_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- League
CREATE TABLE public.dim_league (
    league_id TEXT PRIMARY KEY,
    league_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Season
CREATE TABLE public.dim_season (
    season_id TEXT PRIMARY KEY,
    season_name TEXT,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Schedule
CREATE TABLE public.dim_schedule (
    game_id TEXT PRIMARY KEY,
    date DATE,
    time TEXT,
    home_team TEXT,
    away_team TEXT,
    home_score INTEGER,
    away_score INTEGER,
    season TEXT,
    status TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Position
CREATE TABLE public.dim_position (
    position_id TEXT PRIMARY KEY,
    position_name TEXT,
    position_abbrev TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Venue
CREATE TABLE public.dim_venue (
    venue_id TEXT PRIMARY KEY,
    venue_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Zone
CREATE TABLE public.dim_zone (
    zone_id TEXT PRIMARY KEY,
    zone_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Period
CREATE TABLE public.dim_period (
    period_id TEXT PRIMARY KEY,
    period_name TEXT,
    period_number INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Event Type
CREATE TABLE public.dim_event_type (
    event_type_id TEXT PRIMARY KEY,
    event_type_name TEXT,
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Event Detail
CREATE TABLE public.dim_event_detail (
    event_detail_id TEXT PRIMARY KEY,
    event_detail_name TEXT,
    event_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Event Detail 2
CREATE TABLE public.dim_event_detail_2 (
    event_detail_2_id TEXT PRIMARY KEY,
    event_detail_2_name TEXT,
    event_type TEXT,
    control_level TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Play Detail
CREATE TABLE public.dim_play_detail (
    play_detail_id TEXT PRIMARY KEY,
    play_detail_name TEXT,
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Player Role
CREATE TABLE public.dim_player_role (
    player_role_id TEXT PRIMARY KEY,
    player_role_name TEXT,
    team_type TEXT,
    role_number INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Situation
CREATE TABLE public.dim_situation (
    situation_id TEXT PRIMARY KEY,
    situation_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Strength
CREATE TABLE public.dim_strength (
    strength_id TEXT PRIMARY KEY,
    strength_name TEXT,
    home_skaters INTEGER,
    away_skaters INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Shift Slot
CREATE TABLE public.dim_shift_slot (
    slot_id TEXT PRIMARY KEY,
    slot_name TEXT,
    position_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Zone Entry Type
CREATE TABLE public.dim_zone_entry_type (
    zone_entry_type_id SERIAL PRIMARY KEY,
    zone_entry_type_code TEXT,
    zone_entry_type_name TEXT,
    control_level TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Zone Exit Type
CREATE TABLE public.dim_zone_exit_type (
    zone_exit_type_id SERIAL PRIMARY KEY,
    zone_exit_type_code TEXT,
    zone_exit_type_name TEXT,
    control_level TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- STEP 3: CREATE FACT TABLES
-- ============================================================================

-- Game Roster (from NORAD)
CREATE TABLE public.fact_gameroster (
    player_game_id TEXT PRIMARY KEY,
    game_id TEXT,
    player_id TEXT,
    player_full_name TEXT,
    team_id TEXT,
    team_name TEXT,
    team_venue TEXT,
    player_position TEXT,
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    pim INTEGER DEFAULT 0,
    plus_minus INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Events (base - one row per event)
CREATE TABLE public.fact_events (
    event_id TEXT PRIMARY KEY,
    game_id TEXT,
    event_index INTEGER,
    period INTEGER,
    event_type TEXT,
    event_detail TEXT,
    event_detail_2 TEXT,
    event_team TEXT,
    event_zone TEXT,
    event_successful TEXT,
    shift_index INTEGER,
    sequence_index INTEGER,
    play_index INTEGER,
    linked_event_id TEXT,
    time_start_seconds NUMERIC,
    time_end_seconds NUMERIC,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Events Player (one row per player per event)
CREATE TABLE public.fact_events_player (
    event_player_id TEXT PRIMARY KEY,
    game_id TEXT,
    event_index NUMERIC,
    player_id TEXT,
    player_name TEXT,
    player_role TEXT,
    role_number TEXT,
    player_team TEXT,
    team_venue TEXT,
    period TEXT,
    event_type TEXT,
    event_detail TEXT,
    event_detail_2 TEXT,
    event_successful TEXT,
    play_detail TEXT,
    play_detail_2 TEXT,
    event_start_seconds NUMERIC,
    event_end_seconds NUMERIC,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Shifts Player (one row per player per shift)
CREATE TABLE public.fact_shifts_player (
    shift_player_id TEXT PRIMARY KEY,
    game_id INTEGER,
    shift_index INTEGER,
    player_id TEXT,
    player_name TEXT,
    player_number INTEGER,
    venue TEXT,
    slot TEXT,
    period INTEGER,
    shift_duration NUMERIC,
    situation TEXT,
    strength TEXT,
    logical_shift_number INTEGER,
    shift_segment INTEGER,
    cumulative_shift_duration NUMERIC,
    stoppage_time NUMERIC,
    playing_duration NUMERIC,
    cumulative_playing_duration NUMERIC,
    running_toi NUMERIC,
    running_playing_toi NUMERIC,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Player Game Stats (aggregated per player per game)
CREATE TABLE public.fact_player_game_stats (
    player_game_stat_id TEXT PRIMARY KEY,
    game_id TEXT,
    player_id TEXT,
    player_name TEXT,
    -- Scoring
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    -- Shots
    shots INTEGER DEFAULT 0,
    sog INTEGER DEFAULT 0,
    shots_blocked INTEGER DEFAULT 0,
    shots_missed INTEGER DEFAULT 0,
    shooting_pct NUMERIC DEFAULT 0,
    -- Passing
    pass_attempts INTEGER DEFAULT 0,
    pass_completed INTEGER DEFAULT 0,
    pass_pct NUMERIC DEFAULT 0,
    -- Faceoffs
    fo_wins INTEGER DEFAULT 0,
    fo_losses INTEGER DEFAULT 0,
    fo_total INTEGER DEFAULT 0,
    fo_pct NUMERIC DEFAULT 0,
    -- Zone
    zone_entries INTEGER DEFAULT 0,
    zone_exits INTEGER DEFAULT 0,
    -- Turnovers
    giveaways INTEGER DEFAULT 0,
    takeaways INTEGER DEFAULT 0,
    -- TOI
    toi_seconds NUMERIC DEFAULT 0,
    toi_minutes NUMERIC DEFAULT 0,
    shift_count INTEGER DEFAULT 0,
    logical_shifts INTEGER DEFAULT 0,
    avg_shift NUMERIC DEFAULT 0,
    -- Plus/Minus
    plus_es INTEGER DEFAULT 0,
    minus_es INTEGER DEFAULT 0,
    plus_minus_es INTEGER DEFAULT 0,
    plus_all INTEGER DEFAULT 0,
    minus_all INTEGER DEFAULT 0,
    plus_minus_all INTEGER DEFAULT 0,
    -- Corsi/Fenwick
    corsi_for INTEGER DEFAULT 0,
    corsi_against INTEGER DEFAULT 0,
    corsi INTEGER DEFAULT 0,
    corsi_pct NUMERIC DEFAULT 0,
    fenwick_for INTEGER DEFAULT 0,
    fenwick_against INTEGER DEFAULT 0,
    fenwick INTEGER DEFAULT 0,
    fenwick_pct NUMERIC DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Goalie Game Stats
CREATE TABLE public.fact_goalie_game_stats (
    goalie_game_stat_id TEXT PRIMARY KEY,
    game_id TEXT,
    player_id TEXT,
    player_name TEXT,
    saves INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    shots_faced INTEGER DEFAULT 0,
    save_pct NUMERIC DEFAULT 0,
    gaa NUMERIC DEFAULT 0,
    toi_minutes NUMERIC DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Team Game Stats
CREATE TABLE public.fact_team_game_stats (
    team_game_stat_id TEXT PRIMARY KEY,
    game_id TEXT,
    team_id TEXT,
    team_name TEXT,
    goals_for INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    shots_for INTEGER DEFAULT 0,
    shots_against INTEGER DEFAULT 0,
    pp_goals INTEGER DEFAULT 0,
    pk_goals_against INTEGER DEFAULT 0,
    faceoff_wins INTEGER DEFAULT 0,
    faceoff_total INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- STEP 4: CREATE INDEXES
-- ============================================================================

CREATE INDEX idx_events_game ON public.fact_events(game_id);
CREATE INDEX idx_events_type ON public.fact_events(event_type);
CREATE INDEX idx_events_player_game ON public.fact_events_player(game_id);
CREATE INDEX idx_events_player_player ON public.fact_events_player(player_id);
CREATE INDEX idx_events_player_type ON public.fact_events_player(event_type);
CREATE INDEX idx_shifts_game ON public.fact_shifts_player(game_id);
CREATE INDEX idx_shifts_player ON public.fact_shifts_player(player_id);
CREATE INDEX idx_gameroster_game ON public.fact_gameroster(game_id);
CREATE INDEX idx_gameroster_player ON public.fact_gameroster(player_id);
CREATE INDEX idx_player_stats_game ON public.fact_player_game_stats(game_id);
CREATE INDEX idx_player_stats_player ON public.fact_player_game_stats(player_id);

-- ============================================================================
-- STEP 5: DISABLE RLS (for development)
-- ============================================================================

ALTER TABLE public.dim_player ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dim_team ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fact_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fact_events_player ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fact_shifts_player ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fact_gameroster ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fact_player_game_stats ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access
CREATE POLICY "Allow public read" ON public.dim_player FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON public.dim_team FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON public.fact_events FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON public.fact_events_player FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON public.fact_shifts_player FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON public.fact_gameroster FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON public.fact_player_game_stats FOR SELECT USING (true);

-- ============================================================================
-- DONE! Now run the Python upload script to populate data.
-- ============================================================================
