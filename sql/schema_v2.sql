-- BenchSight Schema v2
-- Properly typed based on actual data analysis
-- Run in Supabase SQL Editor

-- =============================================================================
-- DROP EXISTING TABLES
-- =============================================================================
DROP TABLE IF EXISTS fact_playergames CASCADE;
DROP TABLE IF EXISTS fact_draft CASCADE;
DROP TABLE IF EXISTS fact_registration CASCADE;
DROP TABLE IF EXISTS fact_leadership CASCADE;
DROP TABLE IF EXISTS fact_gameroster CASCADE;
DROP TABLE IF EXISTS dim_schedule CASCADE;
DROP TABLE IF EXISTS dim_season CASCADE;
DROP TABLE IF EXISTS dim_league CASCADE;
DROP TABLE IF EXISTS dim_team CASCADE;
DROP TABLE IF EXISTS dim_player CASCADE;
DROP TABLE IF EXISTS dim_rinkcoordzones CASCADE;
DROP TABLE IF EXISTS dim_rinkboxcoord CASCADE;
DROP TABLE IF EXISTS dim_playerurlref CASCADE;
DROP TABLE IF EXISTS dim_randomnames CASCADE;

-- =============================================================================
-- DIMENSION TABLES
-- =============================================================================

-- dim_league
CREATE TABLE dim_league (
    league_id TEXT PRIMARY KEY,
    league TEXT NOT NULL
);

-- dim_season
CREATE TABLE dim_season (
    season_id TEXT PRIMARY KEY,
    season INTEGER NOT NULL,
    session TEXT,
    norad BOOLEAN DEFAULT FALSE,
    csah BOOLEAN DEFAULT FALSE,
    league_id TEXT REFERENCES dim_league(league_id),
    league TEXT,
    start_date DATE
);

-- dim_team
CREATE TABLE dim_team (
    team_id TEXT PRIMARY KEY,
    team_name TEXT NOT NULL,
    norad_team BOOLEAN DEFAULT FALSE,
    csah_team BOOLEAN DEFAULT FALSE,
    league_id TEXT REFERENCES dim_league(league_id),
    league TEXT,
    long_team_name TEXT,
    team_cd TEXT,
    team_color1 TEXT,
    team_color2 TEXT,
    team_color3 TEXT,
    team_color4 TEXT,
    team_logo TEXT,
    team_url TEXT
);

-- dim_player
CREATE TABLE dim_player (
    player_id TEXT PRIMARY KEY,
    player_first_name TEXT NOT NULL,
    player_last_name TEXT NOT NULL,
    player_full_name TEXT NOT NULL,
    player_primary_position TEXT,
    current_skill_rating INTEGER,
    player_hand TEXT,
    birth_year INTEGER,
    player_gender TEXT,
    highest_beer_league TEXT,
    player_rating_ly INTEGER,
    player_notes TEXT,
    player_leadership TEXT,
    player_norad BOOLEAN DEFAULT FALSE,
    player_csaha BOOLEAN DEFAULT FALSE,
    player_norad_primary_number TEXT,
    player_csah_primary_number TEXT,
    player_norad_current_team TEXT,
    player_csah_current_team TEXT,
    player_norad_current_team_id TEXT,
    player_csah_current_team_id TEXT,
    other_url TEXT,
    player_url TEXT,
    player_image TEXT,
    random_player_first_name TEXT,
    random_player_last_name TEXT,
    random_player_full_name TEXT
);

-- dim_schedule
CREATE TABLE dim_schedule (
    game_id INTEGER PRIMARY KEY,
    season INTEGER,
    season_id TEXT REFERENCES dim_season(season_id),
    game_url TEXT,
    home_team_game_id TEXT,
    away_team_game_id TEXT,
    game_date DATE,
    game_time TIME,
    home_team_name TEXT,
    away_team_name TEXT,
    home_team_id TEXT REFERENCES dim_team(team_id),
    away_team_id TEXT REFERENCES dim_team(team_id),
    head_to_head_id TEXT,
    game_type TEXT,
    playoff_round TEXT,
    last_period_type TEXT,
    period_length INTERVAL,
    ot_period_length INTERVAL,
    shootout_rounds INTEGER DEFAULT 0,
    home_total_goals INTEGER DEFAULT 0,
    away_total_goals INTEGER DEFAULT 0,
    home_team_period1_goals INTEGER,
    home_team_period2_goals INTEGER,
    home_team_period3_goals INTEGER,
    home_team_periodot_goals INTEGER,
    away_team_period1_goals INTEGER,
    away_team_period2_goals INTEGER,
    away_team_period3_goals INTEGER,
    away_team_periodot_goals INTEGER,
    home_team_seeding INTEGER,
    away_team_seeding INTEGER,
    home_team_w INTEGER DEFAULT 0,
    home_team_l INTEGER DEFAULT 0,
    home_team_t INTEGER DEFAULT 0,
    home_team_pts INTEGER DEFAULT 0,
    away_team_w INTEGER DEFAULT 0,
    away_team_l INTEGER DEFAULT 0,
    away_team_t INTEGER DEFAULT 0,
    away_team_pts INTEGER DEFAULT 0,
    video_id TEXT,
    video_start_time TEXT,
    video_end_time TEXT,
    video_title TEXT,
    video_url TEXT
);

-- dim_rinkboxcoord
CREATE TABLE dim_rinkboxcoord (
    box_id TEXT PRIMARY KEY,
    box_id_rev TEXT,
    x_min REAL,
    x_max REAL,
    y_min REAL,
    y_max REAL,
    area REAL,
    x_description TEXT,
    y_description TEXT,
    danger TEXT,
    zone TEXT,
    side TEXT
);

-- dim_rinkcoordzones
CREATE TABLE dim_rinkcoordzones (
    id SERIAL PRIMARY KEY,
    box_id TEXT,
    box_id_rev TEXT,
    x_min REAL,
    x_max REAL,
    y_min REAL,
    y_max REAL,
    y_description TEXT,
    x_description TEXT,
    danger TEXT,
    slot TEXT,
    zone TEXT,
    side TEXT,
    dotside TEXT,
    depth TEXT
);

-- dim_playerurlref
CREATE TABLE dim_playerurlref (
    id SERIAL PRIMARY KEY,
    n_player_url TEXT,
    player_full_name TEXT,
    n_player_id_2 TEXT
);

-- dim_randomnames
CREATE TABLE dim_randomnames (
    id SERIAL PRIMARY KEY,
    random_full_name TEXT,
    random_first_name TEXT,
    random_last_name TEXT,
    gender TEXT,
    name_used BOOLEAN DEFAULT FALSE
);

-- =============================================================================
-- FACT TABLES
-- =============================================================================

-- fact_gameroster
CREATE TABLE fact_gameroster (
    key TEXT PRIMARY KEY,
    game_id INTEGER REFERENCES dim_schedule(game_id),
    team_game_id TEXT,
    opp_team_game_id TEXT,
    player_game_id TEXT,
    team_venue TEXT,
    team_name TEXT,
    opp_team_name TEXT,
    player_game_number INTEGER,
    n_player_url TEXT,
    player_position TEXT,
    games_played INTEGER DEFAULT 1,
    goals INTEGER DEFAULT 0,
    assist INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    pim INTEGER DEFAULT 0,
    shutouts INTEGER DEFAULT 0,
    team_id TEXT REFERENCES dim_team(team_id),
    opp_team_id TEXT,
    player_full_name TEXT,
    player_id TEXT REFERENCES dim_player(player_id),
    game_date DATE,
    season INTEGER,
    sub BOOLEAN DEFAULT FALSE,
    current_team TEXT,
    skill_rating INTEGER
);

-- fact_leadership
CREATE TABLE fact_leadership (
    id SERIAL PRIMARY KEY,
    player_full_name TEXT,
    player_id TEXT REFERENCES dim_player(player_id),
    leadership TEXT,
    skill_rating INTEGER,
    n_player_url TEXT,
    team_name TEXT,
    team_id TEXT REFERENCES dim_team(team_id),
    season INTEGER,
    season_id TEXT REFERENCES dim_season(season_id)
);

-- fact_registration
CREATE TABLE fact_registration (
    player_season_registration_id TEXT PRIMARY KEY,
    player_full_name TEXT,
    player_id TEXT REFERENCES dim_player(player_id),
    season_id TEXT REFERENCES dim_season(season_id),
    season INTEGER,
    restricted BOOLEAN DEFAULT FALSE,
    email TEXT,
    position TEXT,
    norad_experience TEXT,
    caf BOOLEAN DEFAULT FALSE,
    highest_beer_league_played TEXT,
    skill_rating INTEGER,
    age INTEGER,
    referred_by TEXT,
    notes TEXT,
    sub_yn BOOLEAN DEFAULT FALSE,
    drafted_team_name TEXT,
    drafted_team_id TEXT REFERENCES dim_team(team_id)
);

-- fact_draft
CREATE TABLE fact_draft (
    player_draft_id TEXT PRIMARY KEY,
    team_id TEXT REFERENCES dim_team(team_id),
    skill_rating INTEGER,
    round INTEGER,
    player_full_name TEXT,
    player_id TEXT REFERENCES dim_player(player_id),
    team_name TEXT,
    restricted BOOLEAN DEFAULT FALSE,
    overall_draft_round INTEGER,
    overall_draft_position INTEGER,
    unrestricted_draft_position INTEGER,
    season INTEGER,
    season_id TEXT REFERENCES dim_season(season_id),
    league TEXT
);

-- fact_playergames
CREATE TABLE fact_playergames (
    id SERIAL PRIMARY KEY,
    game_type_id TEXT,
    game_date DATE,
    game_type TEXT,
    team TEXT,
    opp TEXT,
    jersey_number INTEGER,
    player TEXT,
    position TEXT,
    gp INTEGER DEFAULT 1,
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    pim INTEGER DEFAULT 0,
    shutouts INTEGER DEFAULT 0,
    skill_rank INTEGER,
    id2 TEXT,
    id3 TEXT,
    season TEXT,
    season_player_id TEXT
);

-- =============================================================================
-- ENABLE ROW LEVEL SECURITY
-- =============================================================================
ALTER TABLE dim_league ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_season ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_team ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_player ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_schedule ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_rinkboxcoord ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_rinkcoordzones ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_playerurlref ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_randomnames ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_gameroster ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_leadership ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_registration ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_draft ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_playergames ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- CREATE POLICIES (Public read/write for anon key)
-- =============================================================================
CREATE POLICY "public_all" ON dim_league FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "public_all" ON dim_season FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "public_all" ON dim_team FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "public_all" ON dim_player FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "public_all" ON dim_schedule FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "public_all" ON dim_rinkboxcoord FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "public_all" ON dim_rinkcoordzones FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "public_all" ON dim_playerurlref FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "public_all" ON dim_randomnames FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "public_all" ON fact_gameroster FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "public_all" ON fact_leadership FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "public_all" ON fact_registration FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "public_all" ON fact_draft FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "public_all" ON fact_playergames FOR ALL USING (true) WITH CHECK (true);

-- =============================================================================
-- CREATE INDEXES
-- =============================================================================
CREATE INDEX idx_schedule_season ON dim_schedule(season_id);
CREATE INDEX idx_schedule_home_team ON dim_schedule(home_team_id);
CREATE INDEX idx_schedule_away_team ON dim_schedule(away_team_id);
CREATE INDEX idx_schedule_date ON dim_schedule(game_date);
CREATE INDEX idx_gameroster_game ON fact_gameroster(game_id);
CREATE INDEX idx_gameroster_player ON fact_gameroster(player_id);
CREATE INDEX idx_gameroster_team ON fact_gameroster(team_id);
CREATE INDEX idx_player_team ON dim_player(player_norad_current_team_id);

SELECT 'Schema v2 created successfully!' as status;
