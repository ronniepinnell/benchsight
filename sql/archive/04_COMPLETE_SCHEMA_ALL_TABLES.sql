-- ============================================================
-- BENCHSIGHT COMPLETE SCHEMA - ALL 96 TABLES
-- Auto-generated from CSV files with proper quoting
-- ============================================================
--
-- IMPORTANT: This creates ALL data tables from the CSV files.
-- Run this in Supabase SQL Editor.
--
-- Note: Column names starting with numbers (like 2on1_rushes)
-- are properly quoted to work with PostgreSQL.
-- ============================================================

-- Drop all tables (reverse dependency order)
DROP TABLE IF EXISTS qa_suspicious_stats CASCADE;
DROP TABLE IF EXISTS fact_wowy CASCADE;
DROP TABLE IF EXISTS fact_video CASCADE;
DROP TABLE IF EXISTS fact_team_zone_time CASCADE;
DROP TABLE IF EXISTS fact_team_standings_snapshot CASCADE;
DROP TABLE IF EXISTS fact_team_game_stats CASCADE;
DROP TABLE IF EXISTS fact_suspicious_stats CASCADE;
DROP TABLE IF EXISTS fact_shot_xy CASCADE;
DROP TABLE IF EXISTS fact_shot_danger CASCADE;
DROP TABLE IF EXISTS fact_shifts_tracking CASCADE;
DROP TABLE IF EXISTS fact_shifts_player CASCADE;
DROP TABLE IF EXISTS fact_shifts_long CASCADE;
DROP TABLE IF EXISTS fact_shifts CASCADE;
DROP TABLE IF EXISTS fact_shift_quality_logical CASCADE;
DROP TABLE IF EXISTS fact_shift_quality CASCADE;
DROP TABLE IF EXISTS fact_shift_players CASCADE;
DROP TABLE IF EXISTS fact_sequences CASCADE;
DROP TABLE IF EXISTS fact_scoring_chances CASCADE;
DROP TABLE IF EXISTS fact_rush_events CASCADE;
DROP TABLE IF EXISTS fact_registration CASCADE;
DROP TABLE IF EXISTS fact_puck_xy_wide CASCADE;
DROP TABLE IF EXISTS fact_puck_xy_long CASCADE;
DROP TABLE IF EXISTS fact_possession_time CASCADE;
DROP TABLE IF EXISTS fact_plays CASCADE;
DROP TABLE IF EXISTS fact_playergames CASCADE;
DROP TABLE IF EXISTS fact_player_xy_wide CASCADE;
DROP TABLE IF EXISTS fact_player_xy_long CASCADE;
DROP TABLE IF EXISTS fact_player_stats_long CASCADE;
DROP TABLE IF EXISTS fact_player_period_stats CASCADE;
DROP TABLE IF EXISTS fact_player_pair_stats CASCADE;
DROP TABLE IF EXISTS fact_player_micro_stats CASCADE;
DROP TABLE IF EXISTS fact_player_game_stats CASCADE;
DROP TABLE IF EXISTS fact_player_game_position CASCADE;
DROP TABLE IF EXISTS fact_player_event_chains CASCADE;
DROP TABLE IF EXISTS fact_player_boxscore_all CASCADE;
DROP TABLE IF EXISTS fact_matchup_summary CASCADE;
DROP TABLE IF EXISTS fact_linked_events CASCADE;
DROP TABLE IF EXISTS fact_line_combos CASCADE;
DROP TABLE IF EXISTS fact_league_leaders_snapshot CASCADE;
DROP TABLE IF EXISTS fact_leadership CASCADE;
DROP TABLE IF EXISTS fact_head_to_head CASCADE;
DROP TABLE IF EXISTS fact_h2h CASCADE;
DROP TABLE IF EXISTS fact_goalie_game_stats CASCADE;
DROP TABLE IF EXISTS fact_gameroster CASCADE;
DROP TABLE IF EXISTS fact_game_status CASCADE;
DROP TABLE IF EXISTS fact_events_tracking CASCADE;
DROP TABLE IF EXISTS fact_events_player CASCADE;
DROP TABLE IF EXISTS fact_events_long CASCADE;
DROP TABLE IF EXISTS fact_events CASCADE;
DROP TABLE IF EXISTS fact_event_chains CASCADE;
DROP TABLE IF EXISTS fact_draft CASCADE;
DROP TABLE IF EXISTS fact_cycle_events CASCADE;
DROP TABLE IF EXISTS dim_zone_exit_type CASCADE;
DROP TABLE IF EXISTS dim_zone_entry_type CASCADE;
DROP TABLE IF EXISTS dim_zone CASCADE;
DROP TABLE IF EXISTS dim_venue CASCADE;
DROP TABLE IF EXISTS dim_turnover_type CASCADE;
DROP TABLE IF EXISTS dim_turnover_quality CASCADE;
DROP TABLE IF EXISTS dim_terminology_mapping CASCADE;
DROP TABLE IF EXISTS dim_team CASCADE;
DROP TABLE IF EXISTS dim_takeaway_type CASCADE;
DROP TABLE IF EXISTS dim_success CASCADE;
DROP TABLE IF EXISTS dim_strength CASCADE;
DROP TABLE IF EXISTS dim_stoppage_type CASCADE;
DROP TABLE IF EXISTS dim_stat_type CASCADE;
DROP TABLE IF EXISTS dim_stat_category CASCADE;
DROP TABLE IF EXISTS dim_stat CASCADE;
DROP TABLE IF EXISTS dim_situation CASCADE;
DROP TABLE IF EXISTS dim_shot_type CASCADE;
DROP TABLE IF EXISTS dim_shift_stop_type CASCADE;
DROP TABLE IF EXISTS dim_shift_start_type CASCADE;
DROP TABLE IF EXISTS dim_shift_slot CASCADE;
DROP TABLE IF EXISTS dim_season CASCADE;
DROP TABLE IF EXISTS dim_schedule CASCADE;
DROP TABLE IF EXISTS dim_rinkcoordzones CASCADE;
DROP TABLE IF EXISTS dim_rinkboxcoord CASCADE;
DROP TABLE IF EXISTS dim_rink_coord CASCADE;
DROP TABLE IF EXISTS dim_randomnames CASCADE;
DROP TABLE IF EXISTS dim_position CASCADE;
DROP TABLE IF EXISTS dim_playerurlref CASCADE;
DROP TABLE IF EXISTS dim_player_role CASCADE;
DROP TABLE IF EXISTS dim_player CASCADE;
DROP TABLE IF EXISTS dim_play_detail_2 CASCADE;
DROP TABLE IF EXISTS dim_play_detail CASCADE;
DROP TABLE IF EXISTS dim_period CASCADE;
DROP TABLE IF EXISTS dim_pass_type CASCADE;
DROP TABLE IF EXISTS dim_net_location CASCADE;
DROP TABLE IF EXISTS dim_micro_stat CASCADE;
DROP TABLE IF EXISTS dim_league CASCADE;
DROP TABLE IF EXISTS dim_giveaway_type CASCADE;
DROP TABLE IF EXISTS dim_event_type CASCADE;
DROP TABLE IF EXISTS dim_event_detail_2 CASCADE;
DROP TABLE IF EXISTS dim_event_detail CASCADE;
DROP TABLE IF EXISTS dim_danger_zone CASCADE;
DROP TABLE IF EXISTS dim_composite_rating CASCADE;
DROP TABLE IF EXISTS dim_comparison_type CASCADE;

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

-- dim_comparison_type: 5 columns
CREATE TABLE dim_comparison_type (
    comparison_type_id TEXT PRIMARY KEY,
    comparison_type_code TEXT,
    comparison_type_name TEXT,
    description TEXT,
    analysis_scope TEXT
);

-- dim_composite_rating: 6 columns
CREATE TABLE dim_composite_rating (
    rating_id TEXT PRIMARY KEY,
    rating_code TEXT,
    rating_name TEXT,
    description TEXT,
    scale_min INTEGER,
    scale_max INTEGER
);

-- dim_danger_zone: 5 columns
CREATE TABLE dim_danger_zone (
    danger_zone_id TEXT PRIMARY KEY,
    danger_zone_code TEXT,
    danger_zone_name TEXT,
    xg_base DECIMAL,
    description TEXT
);

-- dim_event_detail: 3 columns
CREATE TABLE dim_event_detail (
    event_detail_id TEXT PRIMARY KEY,
    event_detail_code TEXT,
    event_detail_name TEXT
);

-- dim_event_detail_2: 6 columns
CREATE TABLE dim_event_detail_2 (
    event_detail_2_id TEXT PRIMARY KEY,
    event_detail_2_code TEXT,
    event_detail_2_name TEXT,
    is_secondary_action TEXT,
    context_type TEXT,
    description TEXT
);

-- dim_event_type: 3 columns
CREATE TABLE dim_event_type (
    event_type_id TEXT PRIMARY KEY,
    event_type_code TEXT,
    event_type_name TEXT
);

-- dim_giveaway_type: 8 columns
CREATE TABLE dim_giveaway_type (
    giveaway_type_id TEXT PRIMARY KEY,
    giveaway_type_code TEXT,
    giveaway_type_name TEXT,
    danger_level TEXT,
    xga_impact DECIMAL,
    turnover_quality TEXT,
    zone_context TEXT,
    description TEXT
);

-- dim_league: 2 columns
CREATE TABLE dim_league (
    league_id TEXT PRIMARY KEY,
    league TEXT
);

-- dim_micro_stat: 4 columns
CREATE TABLE dim_micro_stat (
    micro_stat_id TEXT PRIMARY KEY,
    stat_code TEXT,
    stat_name TEXT,
    category TEXT
);

-- dim_net_location: 5 columns
CREATE TABLE dim_net_location (
    net_location_id TEXT PRIMARY KEY,
    net_location_code TEXT,
    net_location_name TEXT,
    x_pct DECIMAL,
    y_pct DECIMAL
);

-- dim_pass_type: 8 columns
CREATE TABLE dim_pass_type (
    pass_type_id TEXT PRIMARY KEY,
    pass_type_code TEXT,
    pass_type_name TEXT,
    expected_completion_rate DECIMAL,
    danger_value DECIMAL,
    xa_modifier DECIMAL,
    description TEXT,
    skill_required TEXT
);

-- dim_period: 7 columns
CREATE TABLE dim_period (
    period_id TEXT PRIMARY KEY,
    period_number INTEGER,
    period_name TEXT,
    period_type TEXT,
    duration_seconds INTEGER,
    intensity_multiplier DECIMAL,
    description TEXT
);

-- dim_play_detail: 6 columns
CREATE TABLE dim_play_detail (
    play_detail_id TEXT PRIMARY KEY,
    play_detail_code TEXT,
    play_detail_name TEXT,
    play_category TEXT,
    skill_level TEXT,
    description TEXT
);

-- dim_play_detail_2: 5 columns
CREATE TABLE dim_play_detail_2 (
    play_detail_2_id TEXT PRIMARY KEY,
    play_detail_2_code TEXT,
    play_detail_2_name TEXT,
    is_secondary_play TEXT,
    description TEXT
);

-- dim_player: 28 columns
CREATE TABLE dim_player (
    "index" INTEGER,
    player_first_name TEXT,
    player_last_name TEXT,
    player_full_name TEXT,
    player_id TEXT PRIMARY KEY,
    player_primary_position TEXT,
    current_skill_rating INTEGER,
    player_hand DECIMAL,
    birth_year DECIMAL,
    player_gender TEXT,
    highest_beer_league TEXT,
    player_rating_ly INTEGER,
    player_notes TEXT,
    player_leadership TEXT,
    player_norad TEXT,
    player_csaha DECIMAL,
    player_norad_primary_number DECIMAL,
    player_csah_primary_number DECIMAL,
    player_norad_current_team TEXT,
    player_csah_current_team DECIMAL,
    player_norad_current_team_id TEXT,
    player_csah_current_team_id TEXT,
    other_url TEXT,
    player_url TEXT,
    player_image TEXT,
    random_player_first_name TEXT,
    random_player_last_name TEXT,
    random_player_full_name TEXT
);

-- dim_player_role: 6 columns
CREATE TABLE dim_player_role (
    role_id TEXT PRIMARY KEY,
    role_code TEXT,
    role_name TEXT,
    role_type TEXT,
    sort_order INTEGER,
    potential_values TEXT
);

-- dim_playerurlref: 3 columns
CREATE TABLE dim_playerurlref (
    n_player_url TEXT PRIMARY KEY,
    player_full_name TEXT,
    n_player_id_2 TEXT
);

-- dim_position: 4 columns
CREATE TABLE dim_position (
    position_id TEXT PRIMARY KEY,
    position_code TEXT,
    position_name TEXT,
    position_type TEXT
);

-- dim_randomnames: 5 columns
CREATE TABLE dim_randomnames (
    random_full_name TEXT PRIMARY KEY,
    random_first_name TEXT,
    random_last_name TEXT,
    gender TEXT,
    name_used TEXT
);

-- dim_rink_coord: 7 columns
CREATE TABLE dim_rink_coord (
    rink_coord_id TEXT PRIMARY KEY,
    rink_coord_code TEXT,
    rink_coord_name TEXT,
    x_min INTEGER,
    x_max INTEGER,
    y_min INTEGER,
    y_max INTEGER
);

-- dim_rinkboxcoord: 12 columns
CREATE TABLE dim_rinkboxcoord (
    box_id TEXT PRIMARY KEY,
    box_id_rev TEXT,
    x_min DECIMAL,
    x_max DECIMAL,
    y_min DECIMAL,
    y_max DECIMAL,
    area DECIMAL,
    x_description TEXT,
    y_description TEXT,
    danger TEXT,
    zone TEXT,
    side TEXT
);

-- dim_rinkcoordzones: 14 columns
CREATE TABLE dim_rinkcoordzones (
    box_id TEXT PRIMARY KEY,
    box_id_rev TEXT,
    x_min DECIMAL,
    x_max DECIMAL,
    y_min DECIMAL,
    y_max DECIMAL,
    y_description TEXT,
    x_description TEXT,
    danger TEXT,
    slot TEXT,
    zone TEXT,
    side TEXT,
    dotside TEXT,
    depth TEXT
);

-- dim_schedule: 44 columns
CREATE TABLE dim_schedule (
    game_id TEXT PRIMARY KEY,
    season INTEGER,
    season_id TEXT,
    game_url TEXT,
    home_team_game_id TEXT,
    away_team_game_id TEXT,
    date DATE,
    game_time TEXT,
    home_team_name TEXT,
    away_team_name TEXT,
    home_team_id TEXT,
    away_team_id TEXT,
    head_to_head_id TEXT,
    game_type TEXT,
    playoff_round TEXT,
    last_period_type TEXT,
    period_length TEXT,
    ot_period_length TEXT,
    shootout_rounds INTEGER,
    home_total_goals INTEGER,
    away_total_goals INTEGER,
    home_team_period1_goals DECIMAL,
    home_team_period2_goals DECIMAL,
    home_team_period3_goals DECIMAL,
    home_team_periodOT_goals DECIMAL,
    away_team_period1_goals DECIMAL,
    away_team_period2_goals DECIMAL,
    away_team_period3_goals DECIMAL,
    away_team_periodOT_goals DECIMAL,
    home_team_seeding DECIMAL,
    away_team_seeding DECIMAL,
    home_team_w INTEGER,
    home_team_l INTEGER,
    home_team_t INTEGER,
    home_team_pts INTEGER,
    away_team_w INTEGER,
    away_team_l INTEGER,
    away_team_t INTEGER,
    away_team_pts INTEGER,
    video_id TEXT,
    video_start_time DECIMAL,
    video_end_time DECIMAL,
    video_title DECIMAL,
    video_url TEXT
);

-- dim_season: 9 columns
CREATE TABLE dim_season (
    "index" INTEGER,
    season_id TEXT PRIMARY KEY,
    season INTEGER,
    "session" TEXT,
    norad TEXT,
    csah TEXT,
    league_id TEXT,
    league TEXT,
    start_date TEXT
);

-- dim_shift_slot: 3 columns
CREATE TABLE dim_shift_slot (
    slot_id TEXT PRIMARY KEY,
    slot_code TEXT,
    slot_name TEXT
);

-- dim_shift_start_type: 7 columns
CREATE TABLE dim_shift_start_type (
    shift_start_type_id TEXT PRIMARY KEY,
    shift_start_type_code TEXT,
    shift_start_type_name TEXT,
    start_category TEXT,
    description TEXT,
    energy_factor DECIMAL,
    old_equiv TEXT
);

-- dim_shift_stop_type: 9 columns
CREATE TABLE dim_shift_stop_type (
    shift_stop_type_id TEXT PRIMARY KEY,
    shift_stop_type_code TEXT,
    shift_stop_type_name TEXT,
    stop_category TEXT,
    description TEXT,
    shift_value_modifier DECIMAL,
    old_equiv TEXT,
    "table" TEXT,
    type TEXT
);

-- dim_shot_type: 10 columns
CREATE TABLE dim_shot_type (
    shot_type_id TEXT PRIMARY KEY,
    shot_type_code TEXT,
    shot_type_name TEXT,
    is_goal INTEGER,
    xg_modifier DECIMAL,
    accuracy_rating DECIMAL,
    power_rating DECIMAL,
    deception_rating DECIMAL,
    typical_distance TEXT,
    description TEXT
);

-- dim_situation: 3 columns
CREATE TABLE dim_situation (
    situation_id TEXT PRIMARY KEY,
    situation_code TEXT,
    situation_name TEXT
);

-- dim_stat: 12 columns
CREATE TABLE dim_stat (
    stat_id TEXT PRIMARY KEY,
    stat_code TEXT,
    stat_name TEXT,
    category TEXT,
    description TEXT,
    formula TEXT,
    player_role TEXT,
    computable_now TEXT,
    benchmark_elite DECIMAL,
    nhl_avg_per_game DECIMAL,
    nhl_elite_threshold DECIMAL,
    nhl_min_threshold DECIMAL
);

-- dim_stat_category: 4 columns
CREATE TABLE dim_stat_category (
    stat_category_id TEXT PRIMARY KEY,
    category_code TEXT,
    category_name TEXT,
    description TEXT
);

-- dim_stat_type: 6 columns
CREATE TABLE dim_stat_type (
    stat_id TEXT PRIMARY KEY,
    stat_name TEXT,
    stat_category TEXT,
    stat_level TEXT,
    computable_now TEXT,
    description TEXT
);

-- dim_stoppage_type: 5 columns
CREATE TABLE dim_stoppage_type (
    stoppage_type_id TEXT PRIMARY KEY,
    stoppage_type_code TEXT,
    stoppage_type_name TEXT,
    stoppage_category TEXT,
    description TEXT
);

-- dim_strength: 7 columns
CREATE TABLE dim_strength (
    strength_id TEXT PRIMARY KEY,
    strength_code TEXT,
    strength_name TEXT,
    situation_type TEXT,
    xg_multiplier DECIMAL,
    description TEXT,
    avg_toi_pct DECIMAL
);

-- dim_success: 4 columns
CREATE TABLE dim_success (
    success_id TEXT PRIMARY KEY,
    success_code TEXT,
    success_name TEXT,
    potential_values TEXT
);

-- dim_takeaway_type: 8 columns
CREATE TABLE dim_takeaway_type (
    takeaway_type_id TEXT PRIMARY KEY,
    takeaway_type_code TEXT,
    takeaway_type_name TEXT,
    skill_level TEXT,
    xgf_impact DECIMAL,
    value_weight DECIMAL,
    transition_potential TEXT,
    description TEXT
);

-- dim_team: 15 columns
CREATE TABLE dim_team (
    "index" INTEGER,
    team_name TEXT,
    team_id TEXT PRIMARY KEY,
    norad_team TEXT,
    csah_team TEXT,
    league_id TEXT,
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

-- dim_terminology_mapping: 4 columns
CREATE TABLE dim_terminology_mapping (
    dimension TEXT PRIMARY KEY,
    old_value TEXT,
    new_value TEXT,
    match_type TEXT
);

-- dim_turnover_quality: 5 columns
CREATE TABLE dim_turnover_quality (
    turnover_quality_id TEXT PRIMARY KEY,
    turnover_quality_code TEXT,
    turnover_quality_name TEXT,
    description TEXT,
    counts_against BOOLEAN
);

-- dim_turnover_type: 9 columns
CREATE TABLE dim_turnover_type (
    turnover_type_id TEXT PRIMARY KEY,
    turnover_type_code TEXT,
    turnover_type_name TEXT,
    category TEXT,
    quality TEXT,
    weight DECIMAL,
    description TEXT,
    zone_context TEXT,
    zone_danger_multiplier DECIMAL
);

-- dim_venue: 4 columns
CREATE TABLE dim_venue (
    venue_id TEXT PRIMARY KEY,
    venue_code TEXT,
    venue_name TEXT,
    venue_abbrev TEXT
);

-- dim_zone: 4 columns
CREATE TABLE dim_zone (
    zone_id TEXT PRIMARY KEY,
    zone_code TEXT,
    zone_name TEXT,
    zone_abbrev TEXT
);

-- dim_zone_entry_type: 9 columns
CREATE TABLE dim_zone_entry_type (
    zone_entry_type_id TEXT PRIMARY KEY,
    zone_entry_type_code TEXT,
    zone_entry_type_name TEXT,
    control_level TEXT,
    fenwick_per_entry DECIMAL,
    shot_multiplier DECIMAL,
    goal_prob_multiplier DECIMAL,
    description TEXT,
    expected_success_rate DECIMAL
);

-- dim_zone_exit_type: 8 columns
CREATE TABLE dim_zone_exit_type (
    zone_exit_type_id TEXT PRIMARY KEY,
    zone_exit_type_code TEXT,
    zone_exit_type_name TEXT,
    control_level TEXT,
    leads_to_entry_pct DECIMAL,
    possession_retained_pct DECIMAL,
    offensive_value_weight DECIMAL,
    description TEXT
);

-- ============================================================
-- FACT TABLES
-- ============================================================

-- fact_cycle_events: 7 columns
CREATE TABLE fact_cycle_events (
    game_id TEXT PRIMARY KEY,
    cycle_start_event_index INTEGER,
    cycle_end_event_index INTEGER,
    pass_count INTEGER,
    is_cycle BOOLEAN,
    home_team_id TEXT,
    away_team_id TEXT
);

-- fact_draft: 15 columns
CREATE TABLE fact_draft (
    team_id TEXT PRIMARY KEY,
    skill_rating INTEGER,
    round INTEGER,
    player_full_name TEXT,
    player_id TEXT,
    team_name TEXT,
    restricted BOOLEAN,
    overall_draft_round INTEGER,
    overall_draft_position INTEGER,
    unrestricted_draft_position INTEGER,
    season INTEGER,
    season_id TEXT,
    league TEXT,
    player_draft_id TEXT,
    league_id TEXT
);
CREATE INDEX idx_fact_draft_player_id ON fact_draft(player_id);

-- fact_event_chains: 15 columns
CREATE TABLE fact_event_chains (
    chain_id TEXT PRIMARY KEY,
    game_id TEXT,
    entry_event_index INTEGER,
    shot_event_index INTEGER,
    events_to_shot INTEGER,
    entry_type TEXT,
    shot_result TEXT,
    is_goal BOOLEAN,
    zone TEXT,
    sequence_id TEXT,
    zone_id TEXT,
    zone_entry_type_id TEXT,
    shot_result_type_id TEXT,
    home_team_id TEXT,
    away_team_id TEXT
);
CREATE INDEX idx_fact_event_chains_game_id ON fact_event_chains(game_id);

-- fact_events: 54 columns
CREATE TABLE fact_events (
    event_key TEXT PRIMARY KEY,
    game_id TEXT,
    period DECIMAL,
    event_index DECIMAL,
    linked_event_index DECIMAL,
    sequence_index DECIMAL,
    play_index DECIMAL,
    event_type TEXT,
    tracking_event_index DECIMAL,
    event_start_min DECIMAL,
    event_start_sec DECIMAL,
    event_end_min DECIMAL,
    event_end_sec DECIMAL,
    role_abrev TEXT,
    event_team_zone TEXT,
    home_team_zone TEXT,
    away_team_zone TEXT,
    team_venue TEXT,
    team_venue_abv TEXT,
    side_of_puck TEXT,
    play_detail1 TEXT,
    play_detail_2 TEXT,
    play_detail_successful TEXT,
    pressured_pressurer DECIMAL,
    zone_change_index DECIMAL,
    home_team TEXT,
    away_team TEXT,
    Type TEXT,
    event_detail TEXT,
    event_detail_2 TEXT,
    event_successful TEXT,
    shift_index DECIMAL,
    duration DECIMAL,
    time_start_total_seconds DECIMAL,
    time_end_total_seconds DECIMAL,
    running_intermission_duration DECIMAL,
    period_start_total_running_seconds DECIMAL,
    running_video_time DECIMAL,
    event_running_start DECIMAL,
    event_running_end DECIMAL,
    period_id TEXT,
    venue_id TEXT,
    event_type_id TEXT,
    event_detail_id TEXT,
    event_detail_2_id TEXT,
    success_id TEXT,
    play_detail_success_id TEXT,
    zone_id TEXT,
    play_detail_id TEXT,
    play_detail_2_id TEXT,
    home_team_id TEXT,
    away_team_id TEXT,
    shift_key TEXT,
    empty_net_goal INTEGER
);
CREATE INDEX idx_fact_events_game_id ON fact_events(game_id);

-- fact_events_long: 32 columns
CREATE TABLE fact_events_long (
    event_player_key TEXT PRIMARY KEY,
    event_key TEXT,
    game_id TEXT,
    player_id TEXT,
    player_name TEXT,
    event_index DECIMAL,
    player_role TEXT,
    role_number DECIMAL,
    event_type TEXT,
    player_game_number DECIMAL,
    player_team TEXT,
    period DECIMAL,
    event_detail TEXT,
    event_detail_2 TEXT,
    event_successful DECIMAL,
    play_detail1 DECIMAL,
    play_detail_2 DECIMAL,
    play_detail_successful DECIMAL,
    team_venue TEXT,
    side_of_puck TEXT,
    play_detail DECIMAL,
    period_id TEXT,
    venue_id TEXT,
    event_type_id TEXT,
    event_detail_id TEXT,
    event_detail_2_id TEXT,
    success_id TEXT,
    play_detail_success_id TEXT,
    play_detail_id TEXT,
    play_detail_2_id TEXT,
    role_id TEXT,
    player_team_id TEXT
);
CREATE INDEX idx_fact_events_long_game_id ON fact_events_long(game_id);
CREATE INDEX idx_fact_events_long_player_id ON fact_events_long(player_id);

-- fact_events_player: 63 columns
CREATE TABLE fact_events_player (
    event_player_key TEXT PRIMARY KEY,
    event_key TEXT,
    game_id TEXT,
    player_id TEXT,
    event_index DECIMAL,
    player_role TEXT,
    role_number DECIMAL,
    period DECIMAL,
    event_type TEXT,
    player_game_number DECIMAL,
    linked_event_index DECIMAL,
    tracking_event_index DECIMAL,
    event_start_min DECIMAL,
    event_start_sec DECIMAL,
    event_end_min DECIMAL,
    event_end_sec DECIMAL,
    role_abrev TEXT,
    event_team_zone TEXT,
    home_team_zone TEXT,
    away_team_zone TEXT,
    team_venue TEXT,
    team_venue_abv TEXT,
    side_of_puck TEXT,
    sequence_index DECIMAL,
    play_index DECIMAL,
    play_detail1 TEXT,
    play_detail_2 TEXT,
    play_detail_successful TEXT,
    pressured_pressurer DECIMAL,
    zone_change_index DECIMAL,
    home_team TEXT,
    away_team TEXT,
    Type TEXT,
    event_detail TEXT,
    event_detail_2 TEXT,
    event_successful TEXT,
    shift_index DECIMAL,
    duration DECIMAL,
    time_start_total_seconds DECIMAL,
    time_end_total_seconds DECIMAL,
    running_intermission_duration DECIMAL,
    period_start_total_running_seconds DECIMAL,
    running_video_time DECIMAL,
    event_running_start DECIMAL,
    event_running_end DECIMAL,
    player_team TEXT,
    player_name TEXT,
    play_detail TEXT,
    period_id TEXT,
    venue_id TEXT,
    event_type_id TEXT,
    event_detail_id TEXT,
    event_detail_2_id TEXT,
    success_id TEXT,
    play_detail_success_id TEXT,
    zone_id TEXT,
    play_detail_id TEXT,
    play_detail_2_id TEXT,
    role_id TEXT,
    home_team_id TEXT,
    away_team_id TEXT,
    player_team_id TEXT,
    shift_key TEXT
);
CREATE INDEX idx_fact_events_player_game_id ON fact_events_player(game_id);
CREATE INDEX idx_fact_events_player_player_id ON fact_events_player(player_id);

-- fact_events_tracking: 46 columns
CREATE TABLE fact_events_tracking (
    event_tracking_key TEXT PRIMARY KEY,
    event_key TEXT,
    event_id TEXT,
    game_id TEXT,
    event_index INTEGER,
    player_id TEXT,
    player_game_number DECIMAL,
    period INTEGER,
    linked_event_index DECIMAL,
    tracking_event_index INTEGER,
    event_start_min DECIMAL,
    event_start_sec DECIMAL,
    event_end_min DECIMAL,
    event_end_sec DECIMAL,
    role_abrev TEXT,
    event_team_zone TEXT,
    home_team_zone TEXT,
    away_team_zone TEXT,
    team_venue TEXT,
    team_venue_abv TEXT,
    side_of_puck TEXT,
    sequence_index DECIMAL,
    play_index DECIMAL,
    play_detail1 TEXT,
    play_detail_2 TEXT,
    play_detail_successful TEXT,
    pressured_pressurer DECIMAL,
    zone_change_index DECIMAL,
    home_team TEXT,
    away_team TEXT,
    Type TEXT,
    event_detail TEXT,
    event_detail_2 TEXT,
    event_successful TEXT,
    shift_index DECIMAL,
    duration DECIMAL,
    time_start_total_seconds DECIMAL,
    time_end_total_seconds DECIMAL,
    running_intermission_duration DECIMAL,
    period_start_total_running_seconds DECIMAL,
    running_video_time DECIMAL,
    event_running_start DECIMAL,
    event_running_end DECIMAL,
    player_role TEXT,
    role_number DECIMAL,
    player_team TEXT
);
CREATE INDEX idx_fact_events_tracking_game_id ON fact_events_tracking(game_id);
CREATE INDEX idx_fact_events_tracking_player_id ON fact_events_tracking(player_id);

-- fact_game_status: 24 columns
CREATE TABLE fact_game_status (
    game_id TEXT PRIMARY KEY,
    game_date DATE,
    home_team TEXT,
    away_team TEXT,
    official_home_goals INTEGER,
    official_away_goals INTEGER,
    official_total_goals INTEGER,
    game_url TEXT,
    tracking_status TEXT,
    tracking_pct DECIMAL,
    events_row_count INTEGER,
    shifts_row_count INTEGER,
    player_id_fill_pct DECIMAL,
    goal_events INTEGER,
    periods_covered DECIMAL,
    tracking_start_period DECIMAL,
    tracking_start_time DECIMAL,
    tracking_end_period DECIMAL,
    tracking_end_time DECIMAL,
    is_loaded BOOLEAN,
    goals_in_stats INTEGER,
    goal_match DECIMAL,
    player_count INTEGER,
    issues TEXT
);

-- fact_gameroster: 29 columns
CREATE TABLE fact_gameroster (
    game_id TEXT PRIMARY KEY,
    team_game_id TEXT,
    opp_team_game_id TEXT,
    player_game_id TEXT,
    team_venue TEXT,
    team_name TEXT,
    opp_team_name TEXT,
    player_game_number DECIMAL,
    n_player_url TEXT,
    player_position TEXT,
    games_played INTEGER,
    goals DECIMAL,
    assist DECIMAL,
    goals_against DECIMAL,
    pim DECIMAL,
    shutouts DECIMAL,
    team_id TEXT,
    opp_team_id TEXT,
    key TEXT,
    player_full_name TEXT,
    player_id TEXT,
    date DATE,
    season INTEGER,
    sub DECIMAL,
    current_team TEXT,
    skill_rating INTEGER,
    venue_id TEXT,
    position_id TEXT,
    season_id TEXT
);
CREATE INDEX idx_fact_gameroster_player_id ON fact_gameroster(player_id);
CREATE INDEX idx_fact_gameroster_team_id ON fact_gameroster(team_id);

-- fact_goalie_game_stats: 19 columns
CREATE TABLE fact_goalie_game_stats (
    goalie_game_key TEXT PRIMARY KEY,
    game_id TEXT,
    player_id TEXT,
    player_name TEXT,
    team_name TEXT,
    saves INTEGER,
    goals_against INTEGER,
    shots_against INTEGER,
    save_pct DECIMAL,
    toi_seconds INTEGER,
    empty_net_ga INTEGER,
    saves_rebound DECIMAL,
    saves_freeze DECIMAL,
    saves_glove DECIMAL,
    saves_blocker DECIMAL,
    saves_left_pad DECIMAL,
    saves_right_pad DECIMAL,
    rebound_control_pct DECIMAL,
    total_save_events DECIMAL
);
CREATE INDEX idx_fact_goalie_game_stats_game_id ON fact_goalie_game_stats(game_id);
CREATE INDEX idx_fact_goalie_game_stats_player_id ON fact_goalie_game_stats(player_id);

-- fact_h2h: 24 columns
CREATE TABLE fact_h2h (
    game_id TEXT,
    player_1_id TEXT,
    player_2_id TEXT,
    shifts_together INTEGER,
    home_team_id TEXT,
    away_team_id TEXT,
    toi_together DECIMAL,
    goals_for DECIMAL,
    goals_against DECIMAL,
    plus_minus DECIMAL,
    corsi_for DECIMAL,
    corsi_against DECIMAL,
    cf_pct DECIMAL,
    fenwick_for DECIMAL,
    fenwick_against DECIMAL,
    ff_pct DECIMAL,
    xgf DECIMAL,
    xga DECIMAL,
    xg_diff DECIMAL,
    shots_for DECIMAL,
    shots_against DECIMAL,
    h2h_key TEXT PRIMARY KEY,
    player_1_name TEXT,
    player_2_name TEXT
);
CREATE INDEX idx_fact_h2h_game_id ON fact_h2h(game_id);

-- fact_head_to_head: 16 columns
CREATE TABLE fact_head_to_head (
    game_id TEXT PRIMARY KEY,
    player_1_id TEXT,
    player_1_name TEXT,
    player_1_rating DECIMAL,
    player_1_venue TEXT,
    player_2_id TEXT,
    player_2_name TEXT,
    player_2_rating DECIMAL,
    player_2_venue TEXT,
    shifts_against INTEGER,
    toi_against_seconds INTEGER,
    rating_diff DECIMAL,
    home_team_id TEXT,
    away_team_id TEXT,
    player_1_venue_id TEXT,
    player_2_venue_id TEXT
);

-- fact_leadership: 9 columns
CREATE TABLE fact_leadership (
    player_full_name TEXT,
    player_id TEXT PRIMARY KEY,
    leadership TEXT,
    skill_rating INTEGER,
    n_player_url TEXT,
    team_name TEXT,
    team_id TEXT,
    season INTEGER,
    season_id TEXT
);
CREATE INDEX idx_fact_leadership_team_id ON fact_leadership(team_id);

-- fact_league_leaders_snapshot: 13 columns
CREATE TABLE fact_league_leaders_snapshot (
    game_id TEXT PRIMARY KEY,
    date DATE,
    player_id TEXT,
    player_name TEXT,
    team_name TEXT,
    gp INTEGER,
    goals INTEGER,
    assists INTEGER,
    pts INTEGER,
    pim INTEGER,
    gpg DECIMAL,
    ppg DECIMAL,
    team_id TEXT
);
CREATE INDEX idx_fact_league_leaders_snapshot_player_id ON fact_league_leaders_snapshot(player_id);
CREATE INDEX idx_fact_league_leaders_snapshot_team_id ON fact_league_leaders_snapshot(team_id);

-- fact_line_combos: 40 columns
CREATE TABLE fact_line_combos (
    line_combo_key TEXT PRIMARY KEY,
    game_id TEXT,
    venue TEXT,
    forward_combo TEXT,
    defense_combo TEXT,
    shifts INTEGER,
    toi_together INTEGER,
    goals_for INTEGER,
    goals_against INTEGER,
    plus_minus INTEGER,
    corsi_for INTEGER,
    corsi_against INTEGER,
    xgf DECIMAL,
    home_team_id TEXT,
    away_team_id TEXT,
    venue_id TEXT,
    team_id TEXT,
    fenwick_for DECIMAL,
    fenwick_against DECIMAL,
    ff_pct DECIMAL,
    xg_against DECIMAL,
    xg_diff DECIMAL,
    xg_pct DECIMAL,
    zone_entries DECIMAL,
    zone_exits DECIMAL,
    controlled_entry_pct DECIMAL,
    giveaways DECIMAL,
    takeaways DECIMAL,
    turnover_diff DECIMAL,
    avg_player_rating DECIMAL,
    opp_avg_rating DECIMAL,
    rating_diff DECIMAL,
    pdo DECIMAL,
    sh_pct DECIMAL,
    sv_pct DECIMAL,
    goals_per_60 DECIMAL,
    goals_against_per_60 DECIMAL,
    cf_per_60 DECIMAL,
    ca_per_60 DECIMAL,
    team_name TEXT
);
CREATE INDEX idx_fact_line_combos_game_id ON fact_line_combos(game_id);
CREATE INDEX idx_fact_line_combos_team_id ON fact_line_combos(team_id);

-- fact_linked_events: 48 columns
CREATE TABLE fact_linked_events (
    linked_event_key TEXT PRIMARY KEY,
    game_id TEXT,
    primary_event_index INTEGER,
    event_count INTEGER,
    event_1_index DECIMAL,
    event_1_type TEXT,
    event_1_detail TEXT,
    event_1_player_id TEXT,
    event_2_index DECIMAL,
    event_2_type TEXT,
    event_2_detail TEXT,
    event_2_player_id TEXT,
    event_3_index DECIMAL,
    event_3_type TEXT,
    event_3_detail TEXT,
    event_3_player_id TEXT,
    event_4_index DECIMAL,
    event_4_type TEXT,
    event_4_detail TEXT,
    event_4_player_id TEXT,
    event_5_index DECIMAL,
    event_5_type DECIMAL,
    event_5_detail DECIMAL,
    event_5_player_id TEXT,
    event_1_key TEXT,
    event_2_key TEXT,
    event_3_key TEXT,
    event_4_key TEXT,
    event_5_key TEXT,
    team_venue DECIMAL,
    team_id TEXT,
    play_chain TEXT,
    event_chain_indices TEXT,
    venue_id TEXT,
    video_time_start DECIMAL,
    video_time_end DECIMAL,
    event_1_type_id TEXT,
    event_2_type_id TEXT,
    event_3_type_id TEXT,
    event_4_type_id TEXT,
    event_5_type_id TEXT,
    event_1_detail_id TEXT,
    event_2_detail_id TEXT,
    event_3_detail_id TEXT,
    event_4_detail_id TEXT,
    event_5_detail_id TEXT,
    home_team_id TEXT,
    away_team_id TEXT
);
CREATE INDEX idx_fact_linked_events_game_id ON fact_linked_events(game_id);
CREATE INDEX idx_fact_linked_events_team_id ON fact_linked_events(team_id);

-- fact_matchup_summary: 29 columns
CREATE TABLE fact_matchup_summary (
    game_id TEXT PRIMARY KEY,
    player_1_id TEXT,
    player_2_id TEXT,
    shifts_together INTEGER,
    home_team_id TEXT,
    away_team_id TEXT,
    toi_together DECIMAL,
    goals_for DECIMAL,
    goals_against DECIMAL,
    plus_minus DECIMAL,
    corsi_for DECIMAL,
    corsi_against DECIMAL,
    cf_pct DECIMAL,
    fenwick_for DECIMAL,
    fenwick_against DECIMAL,
    ff_pct DECIMAL,
    xgf DECIMAL,
    xga DECIMAL,
    xg_diff DECIMAL,
    shots_for DECIMAL,
    shots_against DECIMAL,
    p1_shifts_without_p2 DECIMAL,
    p2_shifts_without_p1 DECIMAL,
    cf_pct_together DECIMAL,
    cf_pct_apart DECIMAL,
    cf_pct_delta DECIMAL,
    matchup_key TEXT,
    synergy_score DECIMAL,
    is_positive_synergy INTEGER
);

-- fact_player_boxscore_all: 23 columns
CREATE TABLE fact_player_boxscore_all (
    game_id TEXT PRIMARY KEY,
    player_id TEXT,
    player_name TEXT,
    player_number DECIMAL,
    player_position TEXT,
    team_venue TEXT,
    team_name TEXT,
    team_id TEXT,
    opp_team_name TEXT,
    date DATE,
    season INTEGER,
    gp INTEGER,
    g INTEGER,
    a INTEGER,
    pts INTEGER,
    ga INTEGER,
    pim INTEGER,
    so INTEGER,
    skill_rating INTEGER,
    venue_id TEXT,
    position_id TEXT,
    season_id TEXT,
    opp_team_id TEXT
);
CREATE INDEX idx_fact_player_boxscore_all_player_id ON fact_player_boxscore_all(player_id);
CREATE INDEX idx_fact_player_boxscore_all_team_id ON fact_player_boxscore_all(team_id);

-- fact_player_event_chains: 22 columns
CREATE TABLE fact_player_event_chains (
    event_chain_key TEXT PRIMARY KEY,
    game_id TEXT,
    event_index DECIMAL,
    event_key TEXT,
    event_type TEXT,
    period DECIMAL,
    home_player_count INTEGER,
    away_player_count INTEGER,
    home_player_1 TEXT,
    home_player_2 TEXT,
    home_player_3 TEXT,
    away_player_1 TEXT,
    away_player_2 TEXT,
    away_player_3 TEXT,
    home_players TEXT,
    away_players TEXT,
    running_video_time DECIMAL,
    event_running_start DECIMAL,
    period_id TEXT,
    event_type_id TEXT,
    home_team_id TEXT,
    away_team_id TEXT
);
CREATE INDEX idx_fact_player_event_chains_game_id ON fact_player_event_chains(game_id);

-- fact_player_game_position: 10 columns
CREATE TABLE fact_player_game_position (
    player_position_key TEXT PRIMARY KEY,
    game_id TEXT,
    player_id TEXT,
    logical_shifts INTEGER,
    dominant_position TEXT,
    dominant_position_pct DECIMAL,
    forward_shifts INTEGER,
    defense_shifts INTEGER,
    goalie_shifts INTEGER,
    player_name TEXT
);
CREATE INDEX idx_fact_player_game_position_game_id ON fact_player_game_position(game_id);
CREATE INDEX idx_fact_player_game_position_player_id ON fact_player_game_position(player_id);

-- fact_player_game_stats: 317 columns
CREATE TABLE fact_player_game_stats (
    player_game_key TEXT PRIMARY KEY,
    game_id TEXT,
    player_id TEXT,
    player_name TEXT,
    goals INTEGER,
    assists INTEGER,
    points INTEGER,
    shots INTEGER,
    sog INTEGER,
    shots_blocked INTEGER,
    shots_missed INTEGER,
    shooting_pct DECIMAL,
    pass_attempts INTEGER,
    pass_completed INTEGER,
    pass_pct DECIMAL,
    fo_wins INTEGER,
    fo_losses INTEGER,
    fo_total INTEGER,
    fo_pct DECIMAL,
    zone_entries INTEGER,
    zone_exits INTEGER,
    giveaways INTEGER,
    takeaways INTEGER,
    toi_seconds DECIMAL,
    toi_minutes DECIMAL,
    playing_toi_seconds DECIMAL,
    playing_toi_minutes DECIMAL,
    stoppage_seconds DECIMAL,
    shift_count INTEGER,
    logical_shifts INTEGER,
    avg_shift DECIMAL,
    avg_playing_shift DECIMAL,
    goals_per_60 DECIMAL,
    assists_per_60 DECIMAL,
    points_per_60 DECIMAL,
    shots_per_60 DECIMAL,
    goals_per_60_playing DECIMAL,
    assists_per_60_playing DECIMAL,
    points_per_60_playing DECIMAL,
    shots_per_60_playing DECIMAL,
    blocks INTEGER,
    hits INTEGER,
    puck_battles INTEGER,
    puck_battle_wins INTEGER,
    retrievals INTEGER,
    corsi_for INTEGER,
    corsi_against INTEGER,
    fenwick_for INTEGER,
    fenwick_against INTEGER,
    cf_pct DECIMAL,
    ff_pct DECIMAL,
    opp_avg_rating DECIMAL,
    skill_diff DECIMAL,
    plus_ev INTEGER,
    minus_ev INTEGER,
    plus_minus_ev INTEGER,
    plus_total INTEGER,
    minus_total INTEGER,
    plus_minus_total INTEGER,
    plus_en_adj INTEGER,
    minus_en_adj INTEGER,
    plus_minus_en_adj INTEGER,
    player_rating DECIMAL,
    home_team_id TEXT,
    away_team_id TEXT,
    chips INTEGER,
    breakout_rush_attempts INTEGER,
    zone_keepins INTEGER,
    dekes_successful INTEGER,
    breakout_clear_attempts INTEGER,
    beat_middle INTEGER,
    beat_wide INTEGER,
    zone_exit_denials INTEGER,
    breakouts INTEGER,
    passes_missed_target INTEGER,
    drives_corner INTEGER,
    tip_attempts INTEGER,
    cutbacks INTEGER,
    drives_middle INTEGER,
    pass_for_tip INTEGER,
    poke_checks INTEGER,
    stick_checks INTEGER,
    got_beat_middle INTEGER,
    crash_net INTEGER,
    cycle_plays INTEGER,
    ceded_exits INTEGER,
    reverse_passes INTEGER,
    deke_attempts INTEGER,
    breakout_pass_attempts INTEGER,
    backchecks INTEGER,
    separate_from_puck INTEGER,
    rebound_recoveries INTEGER,
    block_attempts INTEGER,
    drives_net INTEGER,
    ceded_entries INTEGER,
    puck_retrievals INTEGER,
    passes_intercepted INTEGER,
    stopped_deke INTEGER,
    dump_and_chase INTEGER,
    def_pass_deflected INTEGER,
    loose_puck_wins INTEGER,
    drives_wide INTEGER,
    puck_recoveries INTEGER,
    def_pass_intercepted INTEGER,
    screens INTEGER,
    front_of_net INTEGER,
    secondary_assists INTEGER,
    in_lane INTEGER,
    quick_ups INTEGER,
    second_touches INTEGER,
    delays INTEGER,
    loose_puck_losses INTEGER,
    turnover_recoveries INTEGER,
    dump_recoveries INTEGER,
    pressures INTEGER,
    contains INTEGER,
    forechecks INTEGER,
    give_and_go INTEGER,
    passes_deflected INTEGER,
    lost_puck INTEGER,
    force_wide INTEGER,
    man_on_man INTEGER,
    dekes_beat_defender INTEGER,
    box_outs INTEGER,
    primary_assists INTEGER,
    got_beat_wide INTEGER,
    zone_entry_denials INTEGER,
    surf_plays INTEGER,
    blocked_shots_play INTEGER,
    drives_middle_success INTEGER,
    drives_wide_success INTEGER,
    drives_corner_success INTEGER,
    zone_entry_denials_success INTEGER,
    breakouts_success INTEGER,
    zone_entry_carry DECIMAL,
    zone_entry_pass DECIMAL,
    zone_entry_dump DECIMAL,
    zone_exit_carry DECIMAL,
    zone_exit_pass DECIMAL,
    zone_exit_dump DECIMAL,
    zone_exit_clear DECIMAL,
    zone_entries_controlled DECIMAL,
    zone_entries_uncontrolled DECIMAL,
    zone_entry_success_rate DECIMAL,
    zone_entry_control_pct DECIMAL,
    zone_exits_controlled DECIMAL,
    zone_exits_uncontrolled DECIMAL,
    zone_exit_success_rate DECIMAL,
    zone_exit_control_pct DECIMAL,
    def_shots_against INTEGER,
    def_goals_against INTEGER,
    def_entries_allowed INTEGER,
    def_exits_denied INTEGER,
    def_times_beat_deke INTEGER,
    def_times_beat_speed INTEGER,
    def_times_beat_total INTEGER,
    def_takeaways INTEGER,
    def_forced_turnovers INTEGER,
    def_zone_clears INTEGER,
    def_blocked_shots INTEGER,
    def_interceptions INTEGER,
    def_stick_checks INTEGER,
    def_poke_checks INTEGER,
    def_body_checks INTEGER,
    def_coverage_assignments INTEGER,
    def_battles_won INTEGER,
    def_battles_lost INTEGER,
    giveaways_bad DECIMAL,
    giveaways_neutral DECIMAL,
    giveaways_good DECIMAL,
    turnover_diff_adjusted DECIMAL,
    turnovers_oz DECIMAL,
    turnovers_nz DECIMAL,
    turnovers_dz DECIMAL,
    giveaway_rate_per_60 DECIMAL,
    takeaway_rate_per_60 DECIMAL,
    goals_rating_adj DECIMAL,
    assists_rating_adj DECIMAL,
    points_rating_adj DECIMAL,
    plus_minus_rating_adj DECIMAL,
    cf_pct_rating_adj DECIMAL,
    qoc_rating DECIMAL,
    qot_rating DECIMAL,
    expected_vs_rating DECIMAL,
    xg_for DECIMAL,
    xg_against DECIMAL,
    xg_diff DECIMAL,
    xg_pct DECIMAL,
    goals_above_expected DECIMAL,
    shots_high_danger DECIMAL,
    shots_medium_danger DECIMAL,
    shots_low_danger DECIMAL,
    scoring_chances DECIMAL,
    high_danger_chances DECIMAL,
    xg_per_shot DECIMAL,
    shot_quality_avg DECIMAL,
    offensive_rating DECIMAL,
    defensive_rating DECIMAL,
    hustle_rating DECIMAL,
    playmaking_rating DECIMAL,
    shooting_rating DECIMAL,
    physical_rating DECIMAL,
    impact_score DECIMAL,
    war_estimate DECIMAL,
    avg_shift_too_long DECIMAL,
    shift_length_warning DECIMAL,
    fatigue_indicator DECIMAL,
    sub_equity_score DECIMAL,
    toi_vs_team_avg DECIMAL,
    period_3_dropoff DECIMAL,
    late_game_performance DECIMAL,
    on_ice_sh_pct DECIMAL,
    on_ice_sv_pct DECIMAL,
    pdo DECIMAL,
    pdo_5v5 DECIMAL,
    fo_wins_oz DECIMAL,
    fo_wins_nz DECIMAL,
    fo_wins_dz DECIMAL,
    fo_losses_oz DECIMAL,
    fo_losses_nz DECIMAL,
    fo_losses_dz DECIMAL,
    fo_pct_oz DECIMAL,
    fo_pct_nz DECIMAL,
    fo_pct_dz DECIMAL,
    zone_starts_oz_pct DECIMAL,
    zone_starts_dz_pct DECIMAL,
    game_score DECIMAL,
    game_score_per_60 DECIMAL,
    game_score_rating DECIMAL,
    effective_game_rating DECIMAL,
    rating_performance_delta DECIMAL,
    playing_above_rating INTEGER,
    playing_below_rating INTEGER,
    playing_at_rating INTEGER,
    performance_tier TEXT,
    performance_index DECIMAL,
    shots_successful DECIMAL,
    shots_unsuccessful DECIMAL,
    passes_successful DECIMAL,
    passes_unsuccessful DECIMAL,
    plays_successful DECIMAL,
    plays_unsuccessful DECIMAL,
    entries_successful DECIMAL,
    entries_unsuccessful DECIMAL,
    exits_successful DECIMAL,
    exits_unsuccessful DECIMAL,
    total_successful_plays DECIMAL,
    total_unsuccessful_plays DECIMAL,
    overall_success_rate DECIMAL,
    shot_success_rate DECIMAL,
    pass_success_rate DECIMAL,
    play_success_rate DECIMAL,
    times_pass_target DECIMAL,
    passes_received_successful DECIMAL,
    passes_received_unsuccessful DECIMAL,
    pass_reception_rate DECIMAL,
    times_target_oz DECIMAL,
    times_target_nz DECIMAL,
    times_target_dz DECIMAL,
    slot_passes_received DECIMAL,
    cross_ice_passes_received DECIMAL,
    odd_man_rushes INTEGER,
    odd_man_rush_goals INTEGER,
    odd_man_rush_shots INTEGER,
    breakaway_attempts INTEGER,
    breakaway_goals INTEGER,
    "2on1_rushes" INTEGER,
    "3on2_rushes" INTEGER,
    "2on0_rushes" INTEGER,
    rush_entries INTEGER,
    rush_shots INTEGER,
    rush_goals INTEGER,
    counter_attacks INTEGER,
    transition_plays INTEGER,
    times_targeted_by_opp DECIMAL,
    times_targeted_shots DECIMAL,
    times_targeted_entries DECIMAL,
    times_targeted_passes DECIMAL,
    times_targeted_as_defender DECIMAL,
    defensive_assignments DECIMAL,
    times_attacked DECIMAL,
    times_attacked_successfully DECIMAL,
    times_attacked_unsuccessfully DECIMAL,
    defensive_success_rate DECIMAL,
    times_ep3 DECIMAL,
    times_ep4 DECIMAL,
    times_ep5 DECIMAL,
    times_opp2 DECIMAL,
    times_opp3 DECIMAL,
    times_opp4 DECIMAL,
    total_on_ice_events DECIMAL,
    puck_touches_estimated DECIMAL,
    involvement_rate DECIMAL,
    support_plays DECIMAL,
    goals_leading INTEGER,
    goals_trailing INTEGER,
    goals_tied INTEGER,
    shots_leading INTEGER,
    shots_trailing INTEGER,
    shots_tied INTEGER,
    first_period_points INTEGER,
    second_period_points INTEGER,
    third_period_points INTEGER,
    first_period_shots INTEGER,
    second_period_shots INTEGER,
    third_period_shots INTEGER,
    clutch_goals INTEGER,
    empty_net_goals_for INTEGER,
    shorthanded_goals INTEGER,
    offensive_contribution DECIMAL,
    defensive_contribution DECIMAL,
    two_way_rating DECIMAL,
    puck_possession_index DECIMAL,
    danger_creation_rate DECIMAL,
    efficiency_score DECIMAL,
    clutch_factor DECIMAL,
    complete_player_score DECIMAL
);
CREATE INDEX idx_fact_player_game_stats_game_id ON fact_player_game_stats(game_id);
CREATE INDEX idx_fact_player_game_stats_player_id ON fact_player_game_stats(player_id);

-- fact_player_micro_stats: 6 columns
CREATE TABLE fact_player_micro_stats (
    micro_stat_key TEXT PRIMARY KEY,
    player_game_key TEXT,
    game_id TEXT,
    player_id TEXT,
    micro_stat TEXT,
    count INTEGER
);
CREATE INDEX idx_fact_player_micro_stats_game_id ON fact_player_micro_stats(game_id);
CREATE INDEX idx_fact_player_micro_stats_player_id ON fact_player_micro_stats(player_id);

-- fact_player_pair_stats: 12 columns
CREATE TABLE fact_player_pair_stats (
    game_id TEXT PRIMARY KEY,
    player_1_id TEXT,
    player_1_name TEXT,
    player_1_rating DECIMAL,
    player_2_id TEXT,
    player_2_name TEXT,
    player_2_rating DECIMAL,
    shifts_together INTEGER,
    toi_together_seconds INTEGER,
    combined_rating DECIMAL,
    home_team_id TEXT,
    away_team_id TEXT
);

-- fact_player_period_stats: 10 columns
CREATE TABLE fact_player_period_stats (
    player_period_key TEXT PRIMARY KEY,
    game_id TEXT,
    player_id TEXT,
    period INTEGER,
    events INTEGER,
    shots INTEGER,
    goals INTEGER,
    passes INTEGER,
    turnovers INTEGER,
    period_id TEXT
);
CREATE INDEX idx_fact_player_period_stats_game_id ON fact_player_period_stats(game_id);
CREATE INDEX idx_fact_player_period_stats_player_id ON fact_player_period_stats(player_id);

-- fact_player_stats_long: 6 columns
CREATE TABLE fact_player_stats_long (
    player_stat_key TEXT PRIMARY KEY,
    player_game_key TEXT,
    game_id TEXT,
    player_id TEXT,
    stat_name TEXT,
    stat_value INTEGER
);
CREATE INDEX idx_fact_player_stats_long_game_id ON fact_player_stats_long(game_id);
CREATE INDEX idx_fact_player_stats_long_player_id ON fact_player_stats_long(player_id);

-- fact_player_xy_long: 16 columns
CREATE TABLE fact_player_xy_long (
    player_xy_key TEXT PRIMARY KEY,
    game_id TEXT,
    event_index TEXT,
    event_key TEXT,
    player_id TEXT,
    player_key TEXT,
    team_id TEXT,
    team_venue TEXT,
    point_number TEXT,
    x TEXT,
    y TEXT,
    timestamp TIMESTAMPTZ,
    rink_coord_id TEXT,
    rink_coord_id_home TEXT,
    rink_coord_id_away TEXT,
    venue_id TEXT
);
CREATE INDEX idx_fact_player_xy_long_game_id ON fact_player_xy_long(game_id);
CREATE INDEX idx_fact_player_xy_long_player_id ON fact_player_xy_long(player_id);
CREATE INDEX idx_fact_player_xy_long_team_id ON fact_player_xy_long(team_id);

-- fact_player_xy_wide: 50 columns
CREATE TABLE fact_player_xy_wide (
    player_xy_key TEXT PRIMARY KEY,
    game_id TEXT,
    event_index TEXT,
    event_key TEXT,
    player_id TEXT,
    player_key TEXT,
    team_id TEXT,
    team_venue TEXT,
    point_count TEXT,
    x_1 TEXT,
    y_1 TEXT,
    timestamp_1 TIMESTAMPTZ,
    rink_coord_id_1 TEXT,
    x_2 TEXT,
    y_2 TEXT,
    timestamp_2 TIMESTAMPTZ,
    rink_coord_id_2 TEXT,
    x_3 TEXT,
    y_3 TEXT,
    timestamp_3 TIMESTAMPTZ,
    rink_coord_id_3 TEXT,
    x_4 TEXT,
    y_4 TEXT,
    timestamp_4 TIMESTAMPTZ,
    rink_coord_id_4 TEXT,
    x_5 TEXT,
    y_5 TEXT,
    timestamp_5 TIMESTAMPTZ,
    rink_coord_id_5 TEXT,
    x_6 TEXT,
    y_6 TEXT,
    timestamp_6 TIMESTAMPTZ,
    rink_coord_id_6 TEXT,
    x_7 TEXT,
    y_7 TEXT,
    timestamp_7 TIMESTAMPTZ,
    rink_coord_id_7 TEXT,
    x_8 TEXT,
    y_8 TEXT,
    timestamp_8 TIMESTAMPTZ,
    rink_coord_id_8 TEXT,
    x_9 TEXT,
    y_9 TEXT,
    timestamp_9 TIMESTAMPTZ,
    rink_coord_id_9 TEXT,
    x_10 TEXT,
    y_10 TEXT,
    timestamp_10 TIMESTAMPTZ,
    rink_coord_id_10 TEXT,
    venue_id TEXT
);
CREATE INDEX idx_fact_player_xy_wide_game_id ON fact_player_xy_wide(game_id);
CREATE INDEX idx_fact_player_xy_wide_player_id ON fact_player_xy_wide(player_id);
CREATE INDEX idx_fact_player_xy_wide_team_id ON fact_player_xy_wide(team_id);

-- fact_playergames: 25 columns
CREATE TABLE fact_playergames (
    ID TEXT,
    Date DATE,
    Type TEXT,
    Team TEXT,
    Opp TEXT,
    "#" INTEGER,
    Player TEXT,
    Position TEXT,
    GP INTEGER,
    G INTEGER,
    A INTEGER,
    GA INTEGER,
    PIM INTEGER,
    SO INTEGER,
    Rank DECIMAL,
    ID2 TEXT,
    ID3 TEXT,
    Season TEXT,
    SeasonPlayerID TEXT,
    player_game_id TEXT PRIMARY KEY,
    event_type_id TEXT,
    position_id TEXT,
    team_id TEXT,
    opp_team_id TEXT,
    season_id TEXT
);
CREATE INDEX idx_fact_playergames_team_id ON fact_playergames(team_id);

-- fact_plays: 25 columns
CREATE TABLE fact_plays (
    play_id TEXT PRIMARY KEY,
    game_id TEXT,
    sequence_id TEXT,
    play_index INTEGER,
    first_event DECIMAL,
    last_event DECIMAL,
    event_count INTEGER,
    sequence_index INTEGER,
    team TEXT,
    zone TEXT,
    has_shot BOOLEAN,
    start_seconds DECIMAL,
    end_seconds DECIMAL,
    duration_seconds DECIMAL,
    play_key TEXT,
    zone_id TEXT,
    team_id TEXT,
    first_event_key TEXT,
    last_event_key TEXT,
    play_chain TEXT,
    event_chain_indices INTEGER,
    video_time_start DECIMAL,
    video_time_end DECIMAL,
    home_team_id TEXT,
    away_team_id TEXT
);
CREATE INDEX idx_fact_plays_game_id ON fact_plays(game_id);
CREATE INDEX idx_fact_plays_team_id ON fact_plays(team_id);

-- fact_possession_time: 14 columns
CREATE TABLE fact_possession_time (
    possession_key TEXT PRIMARY KEY,
    game_id TEXT,
    player_id TEXT,
    venue TEXT,
    zone_entries INTEGER,
    zone_exits INTEGER,
    ozone_entries INTEGER,
    dzone_entries INTEGER,
    possession_events INTEGER,
    estimated_possession_seconds DECIMAL,
    venue_id TEXT,
    team_id TEXT,
    home_team_id TEXT,
    away_team_id TEXT
);
CREATE INDEX idx_fact_possession_time_game_id ON fact_possession_time(game_id);
CREATE INDEX idx_fact_possession_time_player_id ON fact_possession_time(player_id);
CREATE INDEX idx_fact_possession_time_team_id ON fact_possession_time(team_id);

-- fact_puck_xy_long: 12 columns
CREATE TABLE fact_puck_xy_long (
    puck_xy_key TEXT PRIMARY KEY,
    game_id TEXT,
    event_index TEXT,
    event_key TEXT,
    point_number TEXT,
    x TEXT,
    y TEXT,
    z TEXT,
    timestamp TIMESTAMPTZ,
    rink_coord_id TEXT,
    rink_coord_id_home TEXT,
    rink_coord_id_away TEXT
);
CREATE INDEX idx_fact_puck_xy_long_game_id ON fact_puck_xy_long(game_id);

-- fact_puck_xy_wide: 55 columns
CREATE TABLE fact_puck_xy_wide (
    puck_xy_key TEXT PRIMARY KEY,
    game_id TEXT,
    event_index TEXT,
    event_key TEXT,
    point_count TEXT,
    x_1 TEXT,
    y_1 TEXT,
    z_1 TEXT,
    timestamp_1 TIMESTAMPTZ,
    rink_coord_id_1 TEXT,
    x_2 TEXT,
    y_2 TEXT,
    z_2 TEXT,
    timestamp_2 TIMESTAMPTZ,
    rink_coord_id_2 TEXT,
    x_3 TEXT,
    y_3 TEXT,
    z_3 TEXT,
    timestamp_3 TIMESTAMPTZ,
    rink_coord_id_3 TEXT,
    x_4 TEXT,
    y_4 TEXT,
    z_4 TEXT,
    timestamp_4 TIMESTAMPTZ,
    rink_coord_id_4 TEXT,
    x_5 TEXT,
    y_5 TEXT,
    z_5 TEXT,
    timestamp_5 TIMESTAMPTZ,
    rink_coord_id_5 TEXT,
    x_6 TEXT,
    y_6 TEXT,
    z_6 TEXT,
    timestamp_6 TIMESTAMPTZ,
    rink_coord_id_6 TEXT,
    x_7 TEXT,
    y_7 TEXT,
    z_7 TEXT,
    timestamp_7 TIMESTAMPTZ,
    rink_coord_id_7 TEXT,
    x_8 TEXT,
    y_8 TEXT,
    z_8 TEXT,
    timestamp_8 TIMESTAMPTZ,
    rink_coord_id_8 TEXT,
    x_9 TEXT,
    y_9 TEXT,
    z_9 TEXT,
    timestamp_9 TIMESTAMPTZ,
    rink_coord_id_9 TEXT,
    x_10 TEXT,
    y_10 TEXT,
    z_10 TEXT,
    timestamp_10 TIMESTAMPTZ,
    rink_coord_id_10 TEXT
);
CREATE INDEX idx_fact_puck_xy_wide_game_id ON fact_puck_xy_wide(game_id);

-- fact_registration: 19 columns
CREATE TABLE fact_registration (
    player_full_name TEXT,
    player_id TEXT PRIMARY KEY,
    season_id TEXT,
    season INTEGER,
    restricted TEXT,
    email TEXT,
    position TEXT,
    norad_experience INTEGER,
    CAF TEXT,
    highest_beer_league_played TEXT,
    skill_rating INTEGER,
    age INTEGER,
    referred_by TEXT,
    notes TEXT,
    sub_yn TEXT,
    drafted_team_name TEXT,
    drafted_team_id TEXT,
    player_season_registration_id TEXT,
    position_id TEXT
);

-- fact_rush_events: 12 columns
CREATE TABLE fact_rush_events (
    game_id TEXT PRIMARY KEY,
    entry_event_index INTEGER,
    shot_event_index INTEGER,
    events_to_shot INTEGER,
    is_rush BOOLEAN,
    rush_type TEXT,
    is_goal BOOLEAN,
    entry_type TEXT,
    zone_entry_type_id TEXT,
    rush_type_id TEXT,
    home_team_id TEXT,
    away_team_id TEXT
);

-- fact_scoring_chances: 14 columns
CREATE TABLE fact_scoring_chances (
    scoring_chance_key TEXT PRIMARY KEY,
    game_id TEXT,
    event_index DECIMAL,
    period DECIMAL,
    is_goal INTEGER,
    danger_level TEXT,
    is_rebound INTEGER,
    is_rush INTEGER,
    is_odd_man INTEGER,
    event_detail TEXT,
    event_detail_2 TEXT,
    period_id TEXT,
    event_detail_id TEXT,
    event_detail_2_id TEXT
);
CREATE INDEX idx_fact_scoring_chances_game_id ON fact_scoring_chances(game_id);

-- fact_sequences: 28 columns
CREATE TABLE fact_sequences (
    sequence_id TEXT PRIMARY KEY,
    game_id TEXT,
    sequence_index INTEGER,
    first_event DECIMAL,
    last_event DECIMAL,
    event_count INTEGER,
    start_team TEXT,
    end_team TEXT,
    start_zone TEXT,
    end_zone TEXT,
    has_goal BOOLEAN,
    start_seconds DECIMAL,
    end_seconds DECIMAL,
    duration_seconds DECIMAL,
    sequence_key TEXT,
    first_event_key TEXT,
    last_event_key TEXT,
    start_zone_id TEXT,
    end_zone_id TEXT,
    video_time_start DECIMAL,
    play_chain TEXT,
    event_chain_indices INTEGER,
    team_id TEXT,
    video_time_end DECIMAL,
    start_team_id TEXT,
    end_team_id TEXT,
    home_team_id TEXT,
    away_team_id TEXT
);
CREATE INDEX idx_fact_sequences_game_id ON fact_sequences(game_id);
CREATE INDEX idx_fact_sequences_team_id ON fact_sequences(team_id);

-- fact_shift_players: 9 columns
CREATE TABLE fact_shift_players (
    shift_player_id TEXT PRIMARY KEY,
    shift_id TEXT,
    game_id TEXT,
    shift_index INTEGER,
    player_game_number INTEGER,
    player_id TEXT,
    venue TEXT,
    position TEXT,
    period INTEGER
);
CREATE INDEX idx_fact_shift_players_game_id ON fact_shift_players(game_id);
CREATE INDEX idx_fact_shift_players_player_id ON fact_shift_players(player_id);

-- fact_shift_quality: 13 columns
CREATE TABLE fact_shift_quality (
    shift_quality_key TEXT PRIMARY KEY,
    game_id TEXT,
    player_id TEXT,
    shift_index INTEGER,
    shift_duration DECIMAL,
    shift_quality TEXT,
    quality_score INTEGER,
    period DECIMAL,
    strength TEXT,
    situation TEXT,
    period_id TEXT,
    strength_id TEXT,
    situation_id TEXT
);
CREATE INDEX idx_fact_shift_quality_game_id ON fact_shift_quality(game_id);
CREATE INDEX idx_fact_shift_quality_player_id ON fact_shift_quality(player_id);

-- fact_shift_quality_logical: 10 columns
CREATE TABLE fact_shift_quality_logical (
    player_game_key TEXT PRIMARY KEY,
    game_id TEXT,
    player_id TEXT,
    player_name TEXT,
    logical_shifts INTEGER,
    toi_seconds DECIMAL,
    avg_logical_shift DECIMAL,
    points_per_shift DECIMAL,
    shots_per_shift DECIMAL,
    shift_quality_score DECIMAL
);
CREATE INDEX idx_fact_shift_quality_logical_game_id ON fact_shift_quality_logical(game_id);
CREATE INDEX idx_fact_shift_quality_logical_player_id ON fact_shift_quality_logical(player_id);

-- fact_shifts: 63 columns
CREATE TABLE fact_shifts (
    shift_key TEXT PRIMARY KEY,
    game_id TEXT,
    shift_index INTEGER,
    Period DECIMAL,
    shift_start_min DECIMAL,
    shift_start_sec DECIMAL,
    shift_end_min DECIMAL,
    shift_end_sec DECIMAL,
    shift_start_type TEXT,
    shift_stop_type TEXT,
    home_forward_1 DECIMAL,
    home_forward_2 DECIMAL,
    home_forward_3 DECIMAL,
    home_defense_1 DECIMAL,
    home_defense_2 DECIMAL,
    home_xtra DECIMAL,
    home_goalie DECIMAL,
    away_forward_1 DECIMAL,
    away_forward_2 DECIMAL,
    away_forward_3 DECIMAL,
    away_defense_1 DECIMAL,
    away_defense_2 DECIMAL,
    away_xtra DECIMAL,
    away_goalie DECIMAL,
    stoppage_time DECIMAL,
    home_ozone_start DECIMAL,
    home_ozone_end DECIMAL,
    home_dzone_start DECIMAL,
    home_dzone_end DECIMAL,
    home_nzone_start DECIMAL,
    home_nzone_end DECIMAL,
    home_team TEXT,
    away_team TEXT,
    shift_start_total_seconds DECIMAL,
    shift_end_total_seconds DECIMAL,
    shift_duration DECIMAL,
    home_team_strength DECIMAL,
    away_team_strength DECIMAL,
    home_team_en DECIMAL,
    away_team_en DECIMAL,
    home_team_pk DECIMAL,
    home_team_pp DECIMAL,
    away_team_pp DECIMAL,
    away_team_pk DECIMAL,
    situation TEXT,
    strength TEXT,
    home_goals DECIMAL,
    away_goals DECIMAL,
    home_team_plus DECIMAL,
    home_team_minus DECIMAL,
    away_team_plus DECIMAL,
    away_team_minus DECIMAL,
    period_start_total_running_seconds DECIMAL,
    running_video_time DECIMAL,
    shift_start_running_time DECIMAL,
    shift_end_running_time DECIMAL,
    strength_id TEXT,
    situation_id TEXT,
    shift_start_type_id TEXT,
    shift_stop_type_id TEXT,
    home_team_id TEXT,
    away_team_id TEXT,
    period_id TEXT
);
CREATE INDEX idx_fact_shifts_game_id ON fact_shifts(game_id);

-- fact_shifts_long: 28 columns
CREATE TABLE fact_shifts_long (
    shift_player_key TEXT PRIMARY KEY,
    shift_key TEXT,
    game_id TEXT,
    shift_index INTEGER,
    player_number INTEGER,
    player_id TEXT,
    player_name TEXT,
    venue TEXT,
    slot TEXT,
    period DECIMAL,
    shift_duration DECIMAL,
    playing_duration DECIMAL,
    situation TEXT,
    strength TEXT,
    stoppage_time DECIMAL,
    pm_plus_ev DECIMAL,
    pm_minus_ev DECIMAL,
    goal_for INTEGER,
    goal_against INTEGER,
    team_en DECIMAL,
    opp_en DECIMAL,
    logical_shift_number INTEGER,
    period_id TEXT,
    venue_id TEXT,
    strength_id TEXT,
    situation_id TEXT,
    slot_id TEXT,
    team_id TEXT
);
CREATE INDEX idx_fact_shifts_long_game_id ON fact_shifts_long(game_id);
CREATE INDEX idx_fact_shifts_long_player_id ON fact_shifts_long(player_id);
CREATE INDEX idx_fact_shifts_long_team_id ON fact_shifts_long(team_id);

-- fact_shifts_player: 35 columns
CREATE TABLE fact_shifts_player (
    shift_player_key TEXT PRIMARY KEY,
    shift_key TEXT,
    game_id TEXT,
    shift_index INTEGER,
    player_number INTEGER,
    venue TEXT,
    slot TEXT,
    period DECIMAL,
    shift_duration DECIMAL,
    situation TEXT,
    strength TEXT,
    stoppage_time DECIMAL,
    pm_plus_ev DECIMAL,
    pm_minus_ev DECIMAL,
    goal_for INTEGER,
    goal_against INTEGER,
    team_en DECIMAL,
    opp_en DECIMAL,
    team_pp DECIMAL,
    team_pk DECIMAL,
    player_id TEXT,
    player_name TEXT,
    logical_shift_number INTEGER,
    shift_segment INTEGER,
    cumulative_shift_duration DECIMAL,
    running_toi DECIMAL,
    playing_duration DECIMAL,
    running_playing_toi DECIMAL,
    period_id TEXT,
    venue_id TEXT,
    strength_id TEXT,
    situation_id TEXT,
    slot_id TEXT,
    team_id TEXT,
    team_name TEXT
);
CREATE INDEX idx_fact_shifts_player_game_id ON fact_shifts_player(game_id);
CREATE INDEX idx_fact_shifts_player_player_id ON fact_shifts_player(player_id);
CREATE INDEX idx_fact_shifts_player_team_id ON fact_shifts_player(team_id);

-- fact_shifts_tracking: 58 columns
CREATE TABLE fact_shifts_tracking (
    shift_tracking_key TEXT PRIMARY KEY,
    shift_key TEXT,
    shift_id TEXT,
    game_id TEXT,
    shift_index INTEGER,
    Period DECIMAL,
    shift_start_min DECIMAL,
    shift_start_sec DECIMAL,
    shift_end_min DECIMAL,
    shift_end_sec DECIMAL,
    shift_start_type TEXT,
    shift_stop_type TEXT,
    home_forward_1 DECIMAL,
    home_forward_2 DECIMAL,
    home_forward_3 DECIMAL,
    home_defense_1 DECIMAL,
    home_defense_2 DECIMAL,
    home_xtra DECIMAL,
    home_goalie DECIMAL,
    away_forward_1 DECIMAL,
    away_forward_2 DECIMAL,
    away_forward_3 DECIMAL,
    away_defense_1 DECIMAL,
    away_defense_2 DECIMAL,
    away_xtra DECIMAL,
    away_goalie DECIMAL,
    stoppage_time DECIMAL,
    home_ozone_start DECIMAL,
    home_ozone_end DECIMAL,
    home_dzone_start DECIMAL,
    home_dzone_end DECIMAL,
    home_nzone_start DECIMAL,
    home_nzone_end DECIMAL,
    home_team TEXT,
    away_team TEXT,
    shift_start_total_seconds DECIMAL,
    shift_end_total_seconds DECIMAL,
    shift_duration DECIMAL,
    home_team_strength DECIMAL,
    away_team_strength DECIMAL,
    home_team_en DECIMAL,
    away_team_en DECIMAL,
    home_team_pk DECIMAL,
    home_team_pp DECIMAL,
    away_team_pp DECIMAL,
    away_team_pk DECIMAL,
    situation TEXT,
    strength TEXT,
    home_goals DECIMAL,
    away_goals DECIMAL,
    home_team_plus DECIMAL,
    home_team_minus DECIMAL,
    away_team_plus DECIMAL,
    away_team_minus DECIMAL,
    period_start_total_running_seconds DECIMAL,
    running_video_time DECIMAL,
    shift_start_running_time DECIMAL,
    shift_end_running_time DECIMAL
);
CREATE INDEX idx_fact_shifts_tracking_game_id ON fact_shifts_tracking(game_id);

-- fact_shot_danger: 10 columns
CREATE TABLE fact_shot_danger (
    shot_danger_key TEXT PRIMARY KEY,
    game_id TEXT,
    event_index DECIMAL,
    danger_zone TEXT,
    xg DECIMAL,
    shot_distance DECIMAL,
    shot_angle DECIMAL,
    is_rebound INTEGER,
    is_rush INTEGER,
    is_one_timer INTEGER
);
CREATE INDEX idx_fact_shot_danger_game_id ON fact_shot_danger(game_id);

-- fact_shot_xy: 31 columns
CREATE TABLE fact_shot_xy (
    shot_xy_key TEXT PRIMARY KEY,
    game_id TEXT,
    event_index TEXT,
    event_key TEXT,
    player_id TEXT,
    player_key TEXT,
    team_id TEXT,
    team_venue TEXT,
    period TEXT,
    period_id TEXT,
    shot_x TEXT,
    shot_y TEXT,
    shot_rink_coord_id TEXT,
    shot_rink_coord_id_home TEXT,
    shot_rink_coord_id_away TEXT,
    shot_distance TEXT,
    shot_angle TEXT,
    target_x TEXT,
    target_y TEXT,
    net_location_id TEXT,
    shot_type TEXT,
    shot_result TEXT,
    is_goal TEXT,
    is_on_net TEXT,
    strength_id TEXT,
    goalie_player_id TEXT,
    xg TEXT,
    running_video_time TEXT,
    venue_id TEXT,
    shot_type_id TEXT,
    shot_result_type_id TEXT
);
CREATE INDEX idx_fact_shot_xy_game_id ON fact_shot_xy(game_id);
CREATE INDEX idx_fact_shot_xy_player_id ON fact_shot_xy(player_id);
CREATE INDEX idx_fact_shot_xy_team_id ON fact_shot_xy(team_id);

-- fact_suspicious_stats: 14 columns
CREATE TABLE fact_suspicious_stats (
    game_id TEXT PRIMARY KEY,
    player_id TEXT,
    player_name TEXT,
    position TEXT,
    stat_name TEXT,
    stat_value DECIMAL,
    threshold INTEGER,
    threshold_direction TEXT,
    flag_type TEXT,
    severity TEXT,
    category TEXT,
    note TEXT,
    resolved BOOLEAN,
    created_at TIMESTAMPTZ
);
CREATE INDEX idx_fact_suspicious_stats_player_id ON fact_suspicious_stats(player_id);

-- fact_team_game_stats: 52 columns
CREATE TABLE fact_team_game_stats (
    team_game_key TEXT PRIMARY KEY,
    game_id TEXT,
    venue TEXT,
    goals INTEGER,
    shots INTEGER,
    fo_wins INTEGER,
    giveaways INTEGER,
    takeaways INTEGER,
    zone_entries INTEGER,
    zone_exits INTEGER,
    pass_attempts INTEGER,
    pass_completed INTEGER,
    fo_losses INTEGER,
    sog INTEGER,
    fo_total INTEGER,
    fo_pct DECIMAL,
    pass_pct DECIMAL,
    shooting_pct DECIMAL,
    venue_id TEXT,
    home_team_id TEXT,
    away_team_id TEXT,
    team_id TEXT,
    total_shots DECIMAL,
    total_sog DECIMAL,
    total_passes DECIMAL,
    total_pass_completed DECIMAL,
    team_pass_pct DECIMAL,
    total_zone_entries DECIMAL,
    total_zone_exits DECIMAL,
    controlled_entries DECIMAL,
    controlled_exits DECIMAL,
    entry_control_pct DECIMAL,
    total_giveaways DECIMAL,
    total_takeaways DECIMAL,
    turnover_diff DECIMAL,
    total_blocks DECIMAL,
    total_hits DECIMAL,
    total_fo_wins DECIMAL,
    total_fo_losses DECIMAL,
    corsi_for DECIMAL,
    corsi_against DECIMAL,
    cf_pct DECIMAL,
    xg_for DECIMAL,
    xg_against DECIMAL,
    xg_diff DECIMAL,
    avg_player_rating DECIMAL,
    total_dekes DECIMAL,
    total_screens DECIMAL,
    offensive_rating_avg DECIMAL,
    defensive_rating_avg DECIMAL,
    hustle_rating_avg DECIMAL,
    team_name TEXT
);
CREATE INDEX idx_fact_team_game_stats_game_id ON fact_team_game_stats(game_id);
CREATE INDEX idx_fact_team_game_stats_team_id ON fact_team_game_stats(team_id);

-- fact_team_standings_snapshot: 14 columns
CREATE TABLE fact_team_standings_snapshot (
    game_id TEXT PRIMARY KEY,
    date DATE,
    team_name TEXT,
    games_played INTEGER,
    wins INTEGER,
    losses INTEGER,
    ties INTEGER,
    points INTEGER,
    goals_for INTEGER,
    goals_against INTEGER,
    goal_diff INTEGER,
    gaa DECIMAL,
    gpg DECIMAL,
    team_id TEXT
);
CREATE INDEX idx_fact_team_standings_snapshot_team_id ON fact_team_standings_snapshot(team_id);

-- fact_team_zone_time: 18 columns
CREATE TABLE fact_team_zone_time (
    zone_time_key TEXT PRIMARY KEY,
    game_id TEXT,
    venue TEXT,
    ozone_events INTEGER,
    dzone_events INTEGER,
    nzone_events INTEGER,
    total_events INTEGER,
    ozone_pct DECIMAL,
    dzone_pct DECIMAL,
    nzone_pct DECIMAL,
    venue_id TEXT,
    home_team_id TEXT,
    away_team_id TEXT,
    team_id TEXT,
    oz_dominance DECIMAL,
    dz_pressure DECIMAL,
    territorial_index DECIMAL,
    team_name TEXT
);
CREATE INDEX idx_fact_team_zone_time_game_id ON fact_team_zone_time(game_id);
CREATE INDEX idx_fact_team_zone_time_team_id ON fact_team_zone_time(team_id);

-- fact_video: 15 columns
CREATE TABLE fact_video (
    video_key TEXT PRIMARY KEY,
    game_id TEXT,
    "Index" INTEGER,
    Key TEXT,
    Game_ID TEXT,
    Video_Type TEXT,
    Video_Category TEXT,
    Url_1 TEXT,
    Url_2 DECIMAL,
    Url_3 DECIMAL,
    Url_4 DECIMAL,
    Video_ID TEXT,
    Extension TEXT,
    Embed_Url TEXT,
    Description TEXT
);
CREATE INDEX idx_fact_video_game_id ON fact_video(game_id);

-- fact_wowy: 28 columns
CREATE TABLE fact_wowy (
    game_id TEXT,
    player_1_id TEXT,
    player_2_id TEXT,
    venue TEXT,
    shifts_together INTEGER,
    p1_shifts_without_p2 INTEGER,
    p2_shifts_without_p1 INTEGER,
    p1_logical_shifts INTEGER,
    p2_logical_shifts INTEGER,
    venue_id TEXT,
    home_team_id TEXT,
    away_team_id TEXT,
    toi_together DECIMAL,
    toi_apart DECIMAL,
    gf_pct_together DECIMAL,
    gf_pct_apart DECIMAL,
    gf_pct_delta DECIMAL,
    cf_pct_together DECIMAL,
    cf_pct_apart DECIMAL,
    cf_pct_delta DECIMAL,
    xgf_pct_together DECIMAL,
    xgf_pct_apart DECIMAL,
    xgf_pct_delta DECIMAL,
    relative_corsi DECIMAL,
    relative_fenwick DECIMAL,
    wowy_key TEXT PRIMARY KEY,
    player_1_name TEXT,
    player_2_name TEXT
);
CREATE INDEX idx_fact_wowy_game_id ON fact_wowy(game_id);

-- ============================================================
-- OTHER TABLES
-- ============================================================

-- qa_suspicious_stats: 11 columns
CREATE TABLE qa_suspicious_stats (
    timestamp TIMESTAMPTZ,
    game_id TEXT PRIMARY KEY,
    player_id TEXT,
    player_name TEXT,
    category TEXT,
    stat TEXT,
    value DECIMAL,
    expected TEXT,
    severity TEXT,
    note TEXT,
    resolved BOOLEAN
);
CREATE INDEX idx_qa_suspicious_stats_player_id ON qa_suspicious_stats(player_id);

-- ============================================================
-- HELPER FUNCTIONS
-- ============================================================

-- Get row counts for all tables
CREATE OR REPLACE FUNCTION get_all_table_counts()
RETURNS TABLE(table_name TEXT, row_count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT 'dim_comparison_type'::TEXT, COUNT(*)::BIGINT FROM dim_comparison_type UNION ALL
    SELECT 'dim_composite_rating'::TEXT, COUNT(*)::BIGINT FROM dim_composite_rating UNION ALL
    SELECT 'dim_danger_zone'::TEXT, COUNT(*)::BIGINT FROM dim_danger_zone UNION ALL
    SELECT 'dim_event_detail'::TEXT, COUNT(*)::BIGINT FROM dim_event_detail UNION ALL
    SELECT 'dim_event_detail_2'::TEXT, COUNT(*)::BIGINT FROM dim_event_detail_2 UNION ALL
    SELECT 'dim_event_type'::TEXT, COUNT(*)::BIGINT FROM dim_event_type UNION ALL
    SELECT 'dim_giveaway_type'::TEXT, COUNT(*)::BIGINT FROM dim_giveaway_type UNION ALL
    SELECT 'dim_league'::TEXT, COUNT(*)::BIGINT FROM dim_league UNION ALL
    SELECT 'dim_micro_stat'::TEXT, COUNT(*)::BIGINT FROM dim_micro_stat UNION ALL
    SELECT 'dim_net_location'::TEXT, COUNT(*)::BIGINT FROM dim_net_location UNION ALL
    SELECT 'dim_pass_type'::TEXT, COUNT(*)::BIGINT FROM dim_pass_type UNION ALL
    SELECT 'dim_period'::TEXT, COUNT(*)::BIGINT FROM dim_period UNION ALL
    SELECT 'dim_play_detail'::TEXT, COUNT(*)::BIGINT FROM dim_play_detail UNION ALL
    SELECT 'dim_play_detail_2'::TEXT, COUNT(*)::BIGINT FROM dim_play_detail_2 UNION ALL
    SELECT 'dim_player'::TEXT, COUNT(*)::BIGINT FROM dim_player UNION ALL
    SELECT 'dim_player_role'::TEXT, COUNT(*)::BIGINT FROM dim_player_role UNION ALL
    SELECT 'dim_playerurlref'::TEXT, COUNT(*)::BIGINT FROM dim_playerurlref UNION ALL
    SELECT 'dim_position'::TEXT, COUNT(*)::BIGINT FROM dim_position UNION ALL
    SELECT 'dim_randomnames'::TEXT, COUNT(*)::BIGINT FROM dim_randomnames UNION ALL
    SELECT 'dim_rink_coord'::TEXT, COUNT(*)::BIGINT FROM dim_rink_coord UNION ALL
    SELECT 'dim_rinkboxcoord'::TEXT, COUNT(*)::BIGINT FROM dim_rinkboxcoord UNION ALL
    SELECT 'dim_rinkcoordzones'::TEXT, COUNT(*)::BIGINT FROM dim_rinkcoordzones UNION ALL
    SELECT 'dim_schedule'::TEXT, COUNT(*)::BIGINT FROM dim_schedule UNION ALL
    SELECT 'dim_season'::TEXT, COUNT(*)::BIGINT FROM dim_season UNION ALL
    SELECT 'dim_shift_slot'::TEXT, COUNT(*)::BIGINT FROM dim_shift_slot UNION ALL
    SELECT 'dim_shift_start_type'::TEXT, COUNT(*)::BIGINT FROM dim_shift_start_type UNION ALL
    SELECT 'dim_shift_stop_type'::TEXT, COUNT(*)::BIGINT FROM dim_shift_stop_type UNION ALL
    SELECT 'dim_shot_type'::TEXT, COUNT(*)::BIGINT FROM dim_shot_type UNION ALL
    SELECT 'dim_situation'::TEXT, COUNT(*)::BIGINT FROM dim_situation UNION ALL
    SELECT 'dim_stat'::TEXT, COUNT(*)::BIGINT FROM dim_stat UNION ALL
    SELECT 'dim_stat_category'::TEXT, COUNT(*)::BIGINT FROM dim_stat_category UNION ALL
    SELECT 'dim_stat_type'::TEXT, COUNT(*)::BIGINT FROM dim_stat_type UNION ALL
    SELECT 'dim_stoppage_type'::TEXT, COUNT(*)::BIGINT FROM dim_stoppage_type UNION ALL
    SELECT 'dim_strength'::TEXT, COUNT(*)::BIGINT FROM dim_strength UNION ALL
    SELECT 'dim_success'::TEXT, COUNT(*)::BIGINT FROM dim_success UNION ALL
    SELECT 'dim_takeaway_type'::TEXT, COUNT(*)::BIGINT FROM dim_takeaway_type UNION ALL
    SELECT 'dim_team'::TEXT, COUNT(*)::BIGINT FROM dim_team UNION ALL
    SELECT 'dim_terminology_mapping'::TEXT, COUNT(*)::BIGINT FROM dim_terminology_mapping UNION ALL
    SELECT 'dim_turnover_quality'::TEXT, COUNT(*)::BIGINT FROM dim_turnover_quality UNION ALL
    SELECT 'dim_turnover_type'::TEXT, COUNT(*)::BIGINT FROM dim_turnover_type UNION ALL
    SELECT 'dim_venue'::TEXT, COUNT(*)::BIGINT FROM dim_venue UNION ALL
    SELECT 'dim_zone'::TEXT, COUNT(*)::BIGINT FROM dim_zone UNION ALL
    SELECT 'dim_zone_entry_type'::TEXT, COUNT(*)::BIGINT FROM dim_zone_entry_type UNION ALL
    SELECT 'dim_zone_exit_type'::TEXT, COUNT(*)::BIGINT FROM dim_zone_exit_type UNION ALL
    SELECT 'fact_cycle_events'::TEXT, COUNT(*)::BIGINT FROM fact_cycle_events UNION ALL
    SELECT 'fact_draft'::TEXT, COUNT(*)::BIGINT FROM fact_draft UNION ALL
    SELECT 'fact_event_chains'::TEXT, COUNT(*)::BIGINT FROM fact_event_chains UNION ALL
    SELECT 'fact_events'::TEXT, COUNT(*)::BIGINT FROM fact_events UNION ALL
    SELECT 'fact_events_long'::TEXT, COUNT(*)::BIGINT FROM fact_events_long UNION ALL
    SELECT 'fact_events_player'::TEXT, COUNT(*)::BIGINT FROM fact_events_player UNION ALL
    SELECT 'fact_events_tracking'::TEXT, COUNT(*)::BIGINT FROM fact_events_tracking UNION ALL
    SELECT 'fact_game_status'::TEXT, COUNT(*)::BIGINT FROM fact_game_status UNION ALL
    SELECT 'fact_gameroster'::TEXT, COUNT(*)::BIGINT FROM fact_gameroster UNION ALL
    SELECT 'fact_goalie_game_stats'::TEXT, COUNT(*)::BIGINT FROM fact_goalie_game_stats UNION ALL
    SELECT 'fact_h2h'::TEXT, COUNT(*)::BIGINT FROM fact_h2h UNION ALL
    SELECT 'fact_head_to_head'::TEXT, COUNT(*)::BIGINT FROM fact_head_to_head UNION ALL
    SELECT 'fact_leadership'::TEXT, COUNT(*)::BIGINT FROM fact_leadership UNION ALL
    SELECT 'fact_league_leaders_snapshot'::TEXT, COUNT(*)::BIGINT FROM fact_league_leaders_snapshot UNION ALL
    SELECT 'fact_line_combos'::TEXT, COUNT(*)::BIGINT FROM fact_line_combos UNION ALL
    SELECT 'fact_linked_events'::TEXT, COUNT(*)::BIGINT FROM fact_linked_events UNION ALL
    SELECT 'fact_matchup_summary'::TEXT, COUNT(*)::BIGINT FROM fact_matchup_summary UNION ALL
    SELECT 'fact_player_boxscore_all'::TEXT, COUNT(*)::BIGINT FROM fact_player_boxscore_all UNION ALL
    SELECT 'fact_player_event_chains'::TEXT, COUNT(*)::BIGINT FROM fact_player_event_chains UNION ALL
    SELECT 'fact_player_game_position'::TEXT, COUNT(*)::BIGINT FROM fact_player_game_position UNION ALL
    SELECT 'fact_player_game_stats'::TEXT, COUNT(*)::BIGINT FROM fact_player_game_stats UNION ALL
    SELECT 'fact_player_micro_stats'::TEXT, COUNT(*)::BIGINT FROM fact_player_micro_stats UNION ALL
    SELECT 'fact_player_pair_stats'::TEXT, COUNT(*)::BIGINT FROM fact_player_pair_stats UNION ALL
    SELECT 'fact_player_period_stats'::TEXT, COUNT(*)::BIGINT FROM fact_player_period_stats UNION ALL
    SELECT 'fact_player_stats_long'::TEXT, COUNT(*)::BIGINT FROM fact_player_stats_long UNION ALL
    SELECT 'fact_player_xy_long'::TEXT, COUNT(*)::BIGINT FROM fact_player_xy_long UNION ALL
    SELECT 'fact_player_xy_wide'::TEXT, COUNT(*)::BIGINT FROM fact_player_xy_wide UNION ALL
    SELECT 'fact_playergames'::TEXT, COUNT(*)::BIGINT FROM fact_playergames UNION ALL
    SELECT 'fact_plays'::TEXT, COUNT(*)::BIGINT FROM fact_plays UNION ALL
    SELECT 'fact_possession_time'::TEXT, COUNT(*)::BIGINT FROM fact_possession_time UNION ALL
    SELECT 'fact_puck_xy_long'::TEXT, COUNT(*)::BIGINT FROM fact_puck_xy_long UNION ALL
    SELECT 'fact_puck_xy_wide'::TEXT, COUNT(*)::BIGINT FROM fact_puck_xy_wide UNION ALL
    SELECT 'fact_registration'::TEXT, COUNT(*)::BIGINT FROM fact_registration UNION ALL
    SELECT 'fact_rush_events'::TEXT, COUNT(*)::BIGINT FROM fact_rush_events UNION ALL
    SELECT 'fact_scoring_chances'::TEXT, COUNT(*)::BIGINT FROM fact_scoring_chances UNION ALL
    SELECT 'fact_sequences'::TEXT, COUNT(*)::BIGINT FROM fact_sequences UNION ALL
    SELECT 'fact_shift_players'::TEXT, COUNT(*)::BIGINT FROM fact_shift_players UNION ALL
    SELECT 'fact_shift_quality'::TEXT, COUNT(*)::BIGINT FROM fact_shift_quality UNION ALL
    SELECT 'fact_shift_quality_logical'::TEXT, COUNT(*)::BIGINT FROM fact_shift_quality_logical UNION ALL
    SELECT 'fact_shifts'::TEXT, COUNT(*)::BIGINT FROM fact_shifts UNION ALL
    SELECT 'fact_shifts_long'::TEXT, COUNT(*)::BIGINT FROM fact_shifts_long UNION ALL
    SELECT 'fact_shifts_player'::TEXT, COUNT(*)::BIGINT FROM fact_shifts_player UNION ALL
    SELECT 'fact_shifts_tracking'::TEXT, COUNT(*)::BIGINT FROM fact_shifts_tracking UNION ALL
    SELECT 'fact_shot_danger'::TEXT, COUNT(*)::BIGINT FROM fact_shot_danger UNION ALL
    SELECT 'fact_shot_xy'::TEXT, COUNT(*)::BIGINT FROM fact_shot_xy UNION ALL
    SELECT 'fact_suspicious_stats'::TEXT, COUNT(*)::BIGINT FROM fact_suspicious_stats UNION ALL
    SELECT 'fact_team_game_stats'::TEXT, COUNT(*)::BIGINT FROM fact_team_game_stats UNION ALL
    SELECT 'fact_team_standings_snapshot'::TEXT, COUNT(*)::BIGINT FROM fact_team_standings_snapshot UNION ALL
    SELECT 'fact_team_zone_time'::TEXT, COUNT(*)::BIGINT FROM fact_team_zone_time UNION ALL
    SELECT 'fact_video'::TEXT, COUNT(*)::BIGINT FROM fact_video UNION ALL
    SELECT 'fact_wowy'::TEXT, COUNT(*)::BIGINT FROM fact_wowy UNION ALL
    SELECT 'qa_suspicious_stats'::TEXT, COUNT(*)::BIGINT FROM qa_suspicious_stats;
END;
$$ LANGUAGE plpgsql;