-- ============================================================
-- BENCHSIGHT - CREATE ALL TABLES
-- ============================================================
-- Auto-generated from CSV files
-- Tables: 39 dimensions, 19 facts
-- ============================================================

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_comparison_type (
    comparison_type_id TEXT,
    comparison_type_code TEXT,
    comparison_type_name TEXT,
    description TEXT,
    analysis_scope TEXT
);

CREATE TABLE IF NOT EXISTS dim_event_detail (
    event_detail_id TEXT,
    event_detail_code TEXT,
    event_detail_name TEXT,
    parent_event_type TEXT,
    is_success BOOLEAN,
    xg_modifier DOUBLE PRECISION,
    analytics_category TEXT
);

CREATE TABLE IF NOT EXISTS dim_event_detail_2 (
    event_detail_2_id TEXT,
    event_detail_2_code TEXT,
    event_detail_2_name TEXT,
    is_secondary_action BOOLEAN,
    context_type TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS dim_event_type (
    event_type_id TEXT,
    event_type_code TEXT,
    event_type_name TEXT,
    event_category TEXT,
    analytics_weight DOUBLE PRECISION,
    description TEXT,
    is_scoring_play BOOLEAN,
    is_possession_play BOOLEAN,
    is_zone_play BOOLEAN,
    is_goalie_play BOOLEAN,
    expected_success_rate DOUBLE PRECISION,
    nhl_benchmark TEXT
);

CREATE TABLE IF NOT EXISTS dim_giveaway_type (
    giveaway_type_id TEXT,
    giveaway_type_code TEXT,
    giveaway_type_name TEXT,
    danger_level TEXT,
    xga_impact DOUBLE PRECISION,
    turnover_quality TEXT,
    zone_context TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS dim_league (
    league_id TEXT,
    league TEXT
);

CREATE TABLE IF NOT EXISTS dim_net_location (
    net_location_id TEXT,
    net_location_code TEXT,
    net_location_name TEXT,
    description TEXT,
    height_zone TEXT,
    side_zone TEXT,
    x_coord_inches BIGINT,
    y_coord_inches BIGINT,
    avg_save_pct DOUBLE PRECISION,
    scoring_difficulty TEXT,
    xg_bonus DOUBLE PRECISION,
    goalie_weakness_rank BIGINT
);

CREATE TABLE IF NOT EXISTS dim_pass_type (
    pass_type_id TEXT,
    pass_type_code TEXT,
    pass_type_name TEXT,
    expected_completion_rate DOUBLE PRECISION,
    danger_value DOUBLE PRECISION,
    xa_modifier DOUBLE PRECISION,
    description TEXT,
    skill_required TEXT
);

CREATE TABLE IF NOT EXISTS dim_period (
    period_id TEXT,
    period_number TEXT,
    period_name TEXT,
    period_type TEXT,
    duration_seconds BIGINT,
    intensity_multiplier DOUBLE PRECISION,
    description TEXT
);

CREATE TABLE IF NOT EXISTS dim_play_detail (
    play_detail_id TEXT,
    play_detail_code TEXT,
    play_detail_name TEXT,
    play_category TEXT,
    skill_level TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS dim_play_detail_2 (
    play_detail_2_id TEXT,
    play_detail_2_code TEXT,
    play_detail_2_name TEXT,
    is_secondary_play BOOLEAN,
    description TEXT
);

CREATE TABLE IF NOT EXISTS dim_player (
    "index" BIGINT,
    player_first_name TEXT,
    player_last_name TEXT,
    player_full_name TEXT,
    player_id TEXT,
    player_primary_position TEXT,
    current_skill_rating BIGINT,
    player_hand DOUBLE PRECISION,
    birth_year DOUBLE PRECISION,
    player_gender TEXT,
    highest_beer_league TEXT,
    player_rating_ly BIGINT,
    player_notes DOUBLE PRECISION,
    player_leadership TEXT,
    player_norad TEXT,
    player_csaha DOUBLE PRECISION,
    player_norad_primary_number DOUBLE PRECISION,
    player_csah_primary_number DOUBLE PRECISION,
    player_norad_current_team TEXT,
    player_csah_current_team DOUBLE PRECISION,
    player_norad_current_team_id TEXT,
    player_csah_current_team_id TEXT,
    other_url DOUBLE PRECISION,
    player_url TEXT,
    player_image TEXT,
    random_player_first_name TEXT,
    random_player_last_name TEXT,
    random_player_full_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_player_role (
    role_id TEXT,
    role_code TEXT,
    role_name TEXT,
    role_type TEXT,
    sort_order BIGINT
);

CREATE TABLE IF NOT EXISTS dim_playerurlref (
    n_player_url TEXT,
    player_full_name TEXT,
    n_player_id_2 TEXT
);

CREATE TABLE IF NOT EXISTS dim_position (
    position_id TEXT,
    position_code TEXT,
    position_name TEXT,
    position_type TEXT
);

CREATE TABLE IF NOT EXISTS dim_randomnames (
    random_full_name TEXT,
    random_first_name TEXT,
    random_last_name TEXT,
    gender TEXT,
    name_used TEXT
);

CREATE TABLE IF NOT EXISTS dim_rinkboxcoord (
    box_id TEXT,
    box_id_rev TEXT,
    x_min DOUBLE PRECISION,
    x_max DOUBLE PRECISION,
    y_min DOUBLE PRECISION,
    y_max DOUBLE PRECISION,
    area DOUBLE PRECISION,
    x_description TEXT,
    y_description TEXT,
    danger TEXT,
    zone TEXT,
    side TEXT
);

CREATE TABLE IF NOT EXISTS dim_rinkcoordzones (
    box_id TEXT,
    box_id_rev TEXT,
    x_min DOUBLE PRECISION,
    x_max DOUBLE PRECISION,
    y_min DOUBLE PRECISION,
    y_max DOUBLE PRECISION,
    y_description TEXT,
    x_description TEXT,
    danger TEXT,
    slot TEXT,
    zone TEXT,
    side TEXT,
    dotside TEXT,
    depth TEXT
);

CREATE TABLE IF NOT EXISTS dim_schedule (
    game_id TEXT,
    season BIGINT,
    season_id TEXT,
    game_url TEXT,
    home_team_game_id TEXT,
    away_team_game_id TEXT,
    date TIMESTAMP,
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
    shootout_rounds BIGINT,
    home_total_goals BIGINT,
    away_total_goals BIGINT,
    home_team_period1_goals DOUBLE PRECISION,
    home_team_period2_goals DOUBLE PRECISION,
    home_team_period3_goals DOUBLE PRECISION,
    home_team_periodOT_goals DOUBLE PRECISION,
    away_team_period1_goals DOUBLE PRECISION,
    away_team_period2_goals DOUBLE PRECISION,
    away_team_period3_goals DOUBLE PRECISION,
    away_team_periodOT_goals DOUBLE PRECISION,
    home_team_seeding DOUBLE PRECISION,
    away_team_seeding DOUBLE PRECISION,
    home_team_w BIGINT,
    home_team_l BIGINT,
    home_team_t BIGINT,
    home_team_pts BIGINT,
    away_team_w BIGINT,
    away_team_l BIGINT,
    away_team_t BIGINT,
    away_team_pts BIGINT,
    video_id TEXT,
    video_start_time DOUBLE PRECISION,
    video_end_time DOUBLE PRECISION,
    video_title DOUBLE PRECISION,
    video_url DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS dim_season (
    "index" BIGINT,
    season_id TEXT,
    season BIGINT,
    session TEXT,
    norad TEXT,
    csah TEXT,
    league_id TEXT,
    league TEXT,
    start_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_shift_slot (
    slot_id TEXT,
    slot_code TEXT,
    slot_name TEXT,
    slot_type TEXT,
    sort_order BIGINT
);

CREATE TABLE IF NOT EXISTS dim_shift_start_type (
    shift_start_type_id TEXT,
    shift_start_type_code TEXT,
    shift_start_type_name TEXT,
    start_category TEXT,
    description TEXT,
    energy_factor DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS dim_shift_stop_type (
    shift_stop_type_id TEXT,
    shift_stop_type_code TEXT,
    shift_stop_type_name TEXT,
    stop_category TEXT,
    description TEXT,
    shift_value_modifier DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS dim_shot_type (
    shot_type_id TEXT,
    shot_type_code TEXT,
    shot_type_name TEXT,
    is_goal BOOLEAN,
    xg_modifier DOUBLE PRECISION,
    accuracy_rating DOUBLE PRECISION,
    power_rating DOUBLE PRECISION,
    deception_rating DOUBLE PRECISION,
    typical_distance TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS dim_situation (
    situation_id TEXT,
    situation_code TEXT,
    situation_name TEXT,
    score_state TEXT,
    xg_modifier DOUBLE PRECISION,
    description TEXT,
    strategy_mode TEXT
);

CREATE TABLE IF NOT EXISTS dim_stat (
    stat_id TEXT,
    stat_code TEXT,
    stat_name TEXT,
    category TEXT,
    description TEXT,
    formula TEXT,
    player_role TEXT,
    computable_now TEXT,
    benchmark_elite DOUBLE PRECISION,
    nhl_avg_per_game TEXT,
    nhl_elite_threshold TEXT,
    nhl_min_threshold TEXT
);

CREATE TABLE IF NOT EXISTS dim_stat_type (
    stat_id TEXT,
    stat_name TEXT,
    stat_category TEXT,
    stat_level TEXT,
    computable_now TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS dim_stoppage_type (
    stoppage_type_id TEXT,
    stoppage_type_code TEXT,
    stoppage_type_name TEXT,
    stoppage_category TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS dim_strength (
    strength_id TEXT,
    strength_code TEXT,
    strength_name TEXT,
    situation_type TEXT,
    xg_multiplier DOUBLE PRECISION,
    description TEXT,
    avg_toi_pct DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS dim_success (
    success_id TEXT,
    success_code TEXT,
    success_name TEXT,
    success_value BIGINT
);

CREATE TABLE IF NOT EXISTS dim_takeaway_type (
    takeaway_type_id TEXT,
    takeaway_type_code TEXT,
    takeaway_type_name TEXT,
    skill_level TEXT,
    xgf_impact DOUBLE PRECISION,
    value_weight DOUBLE PRECISION,
    transition_potential TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS dim_team (
    "index" BIGINT,
    team_name TEXT,
    team_id TEXT,
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

CREATE TABLE IF NOT EXISTS dim_terminology_mapping (
    dimension TEXT,
    old_value TEXT,
    new_value TEXT,
    match_type TEXT
);

CREATE TABLE IF NOT EXISTS dim_turnover_quality (
    turnover_quality_id TEXT,
    turnover_quality_code TEXT,
    turnover_quality_name TEXT,
    description TEXT,
    counts_against BOOLEAN
);

CREATE TABLE IF NOT EXISTS dim_turnover_type (
    turnover_type_id TEXT,
    turnover_type_code TEXT,
    turnover_type_name TEXT,
    category TEXT,
    quality TEXT,
    weight DOUBLE PRECISION,
    description TEXT,
    zone_context TEXT,
    zone_danger_multiplier DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS dim_venue (
    venue_id TEXT,
    venue_code TEXT,
    venue_name TEXT,
    venue_abbrev TEXT
);

CREATE TABLE IF NOT EXISTS dim_zone (
    zone_id TEXT,
    zone_code TEXT,
    zone_name TEXT,
    zone_abbrev TEXT
);

CREATE TABLE IF NOT EXISTS dim_zone_entry_type (
    zone_entry_type_id TEXT,
    zone_entry_type_code TEXT,
    zone_entry_type_name TEXT,
    control_level TEXT,
    fenwick_per_entry DOUBLE PRECISION,
    shot_multiplier DOUBLE PRECISION,
    goal_prob_multiplier DOUBLE PRECISION,
    description TEXT,
    expected_success_rate DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS dim_zone_exit_type (
    zone_exit_type_id TEXT,
    zone_exit_type_code TEXT,
    zone_exit_type_name TEXT,
    control_level TEXT,
    leads_to_entry_pct DOUBLE PRECISION,
    possession_retained_pct DOUBLE PRECISION,
    offensive_value_weight DOUBLE PRECISION,
    description TEXT
);


-- ============================================================
-- FACT TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_draft (
    team_id TEXT,
    skill_rating BIGINT,
    round BIGINT,
    player_full_name TEXT,
    player_id TEXT,
    team_name TEXT,
    restricted BOOLEAN,
    overall_draft_round BIGINT,
    overall_draft_position BIGINT,
    unrestricted_draft_position BIGINT,
    season BIGINT,
    season_id TEXT,
    league TEXT,
    player_draft_id TEXT
);

CREATE TABLE IF NOT EXISTS fact_events (
    event_index_flag_ DOUBLE PRECISION,
    sequence_index_flag_ TEXT,
    play_index_flag_ TEXT,
    linked_event_index_flag_ TEXT,
    event_start_min_ DOUBLE PRECISION,
    event_start_sec_ DOUBLE PRECISION,
    event_end_min_ DOUBLE PRECISION,
    event_end_sec_ DOUBLE PRECISION,
    player_game_number_ DOUBLE PRECISION,
    event_team_zone_ TEXT,
    event_type_ TEXT,
    event_detail_ TEXT,
    event_detail_2_ TEXT,
    event_successful_ TEXT,
    play_detail1_ TEXT,
    play_detail2_ TEXT,
    play_detail_successful_ TEXT,
    pressured_pressurer_ DOUBLE PRECISION,
    event_index_ DOUBLE PRECISION,
    linked_event_index_ DOUBLE PRECISION,
    sequence_index_ DOUBLE PRECISION,
    play_index_ DOUBLE PRECISION,
    team_ TEXT,
    player_game_number DOUBLE PRECISION,
    role_abrev_binary_ TEXT,
    period DOUBLE PRECISION,
    event_index DOUBLE PRECISION,
    linked_event_index DOUBLE PRECISION,
    tracking_event_index DOUBLE PRECISION,
    event_start_min DOUBLE PRECISION,
    event_start_sec DOUBLE PRECISION,
    event_end_min DOUBLE PRECISION,
    event_end_sec DOUBLE PRECISION,
    role_abrev TEXT,
    event_team_zone2_ TEXT,
    event_team_zone TEXT,
    home_team_zone_ TEXT,
    away_team_zone_ TEXT,
    team_venue_ TEXT,
    team_venue_abv_ TEXT,
    home_team_zone TEXT,
    away_team_zone TEXT,
    team_venue TEXT,
    team_venue_abv TEXT,
    side_of_puck TEXT,
    sequence_index DOUBLE PRECISION,
    play_index DOUBLE PRECISION,
    play_detail1 TEXT,
    play_detail_2 TEXT,
    play_detail_successful TEXT,
    pressured_pressurer DOUBLE PRECISION,
    zone_change_index DOUBLE PRECISION,
    game_id TEXT,
    home_team TEXT,
    away_team TEXT,
    "Type" TEXT,
    event_detail TEXT,
    event_detail_2 TEXT,
    event_successful TEXT,
    shift_index DOUBLE PRECISION,
    duration DOUBLE PRECISION,
    time_start_total_seconds DOUBLE PRECISION,
    time_end_total_seconds DOUBLE PRECISION,
    running_intermission_duration DOUBLE PRECISION,
    period_start_total_running_seconds DOUBLE PRECISION,
    running_video_time DOUBLE PRECISION,
    event_running_start DOUBLE PRECISION,
    event_running_end DOUBLE PRECISION,
    player_role TEXT,
    role_number DOUBLE PRECISION,
    player_id TEXT,
    player_team TEXT,
    player_num_dup_ DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS fact_events_player (
    event_index_flag_ DOUBLE PRECISION,
    sequence_index_flag_ TEXT,
    play_index_flag_ TEXT,
    linked_event_index_flag_ TEXT,
    event_start_min_ DOUBLE PRECISION,
    event_start_sec_ DOUBLE PRECISION,
    event_end_min_ DOUBLE PRECISION,
    event_end_sec_ DOUBLE PRECISION,
    player_game_number_ DOUBLE PRECISION,
    event_team_zone_ TEXT,
    event_type_ TEXT,
    event_detail_ TEXT,
    event_detail_2_ TEXT,
    event_successful_ TEXT,
    play_detail1_ TEXT,
    play_detail2_ TEXT,
    play_detail_successful_ TEXT,
    pressured_pressurer_ DOUBLE PRECISION,
    event_index_ DOUBLE PRECISION,
    linked_event_index_ DOUBLE PRECISION,
    sequence_index_ DOUBLE PRECISION,
    play_index_ DOUBLE PRECISION,
    team_ TEXT,
    player_game_number DOUBLE PRECISION,
    role_abrev_binary_ TEXT,
    period DOUBLE PRECISION,
    event_index DOUBLE PRECISION,
    linked_event_index DOUBLE PRECISION,
    tracking_event_index DOUBLE PRECISION,
    event_start_min DOUBLE PRECISION,
    event_start_sec DOUBLE PRECISION,
    event_end_min DOUBLE PRECISION,
    event_end_sec DOUBLE PRECISION,
    role_abrev TEXT,
    event_team_zone2_ TEXT,
    event_team_zone TEXT,
    home_team_zone_ TEXT,
    away_team_zone_ TEXT,
    team_venue_ TEXT,
    team_venue_abv_ TEXT,
    home_team_zone TEXT,
    away_team_zone TEXT,
    team_venue TEXT,
    team_venue_abv TEXT,
    side_of_puck TEXT,
    sequence_index DOUBLE PRECISION,
    play_index DOUBLE PRECISION,
    play_detail1 TEXT,
    play_detail_2 TEXT,
    play_detail_successful TEXT,
    pressured_pressurer DOUBLE PRECISION,
    zone_change_index DOUBLE PRECISION,
    game_id TEXT,
    home_team TEXT,
    away_team TEXT,
    "Type" TEXT,
    event_detail TEXT,
    event_detail_2 TEXT,
    event_successful TEXT,
    shift_index DOUBLE PRECISION,
    duration DOUBLE PRECISION,
    time_start_total_seconds DOUBLE PRECISION,
    time_end_total_seconds DOUBLE PRECISION,
    running_intermission_duration DOUBLE PRECISION,
    period_start_total_running_seconds DOUBLE PRECISION,
    running_video_time DOUBLE PRECISION,
    event_running_start DOUBLE PRECISION,
    event_running_end DOUBLE PRECISION,
    player_role TEXT,
    role_number DOUBLE PRECISION,
    player_id TEXT,
    player_team TEXT,
    player_num_dup_ DOUBLE PRECISION,
    event_type TEXT,
    event_detail_raw TEXT,
    event_detail_2_raw TEXT,
    event_successful_raw TEXT,
    play_detail_1_raw TEXT,
    play_detail_2_raw TEXT,
    player_name TEXT,
    play_detail TEXT
);

CREATE TABLE IF NOT EXISTS fact_gameroster (
    game_id TEXT,
    team_game_id TEXT,
    opp_team_game_id TEXT,
    player_game_id TEXT,
    team_venue TEXT,
    team_name TEXT,
    opp_team_name TEXT,
    player_game_number DOUBLE PRECISION,
    n_player_url TEXT,
    player_position TEXT,
    games_played BIGINT,
    goals BIGINT,
    assist BIGINT,
    goals_against BIGINT,
    pim BIGINT,
    shutouts DOUBLE PRECISION,
    team_id TEXT,
    opp_team_id TEXT,
    "key" TEXT,
    player_full_name TEXT,
    player_id TEXT,
    date TIMESTAMP,
    season BIGINT,
    sub DOUBLE PRECISION,
    current_team TEXT,
    skill_rating BIGINT
);

CREATE TABLE IF NOT EXISTS fact_goalie_game_stats (
    game_id TEXT,
    player_id TEXT,
    player_name TEXT,
    saves BIGINT,
    goals_against BIGINT,
    toi_minutes DOUBLE PRECISION,
    shots_faced BIGINT,
    save_pct DOUBLE PRECISION,
    gaa DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS fact_head_to_head (
    game_id TEXT,
    player_1_id TEXT,
    player_1_name TEXT,
    player_1_rating DOUBLE PRECISION,
    player_1_venue TEXT,
    player_2_id TEXT,
    player_2_name TEXT,
    player_2_rating DOUBLE PRECISION,
    player_2_venue TEXT,
    shifts_against BIGINT,
    toi_against_seconds BIGINT,
    rating_diff DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS fact_leadership (
    player_full_name TEXT,
    player_id TEXT,
    leadership TEXT,
    skill_rating BIGINT,
    n_player_url TEXT,
    team_name TEXT,
    team_id TEXT,
    season BIGINT,
    season_id TEXT
);

CREATE TABLE IF NOT EXISTS fact_league_leaders_snapshot (
    game_id TEXT,
    date TIMESTAMP,
    player_id TEXT,
    player_name TEXT,
    team_name TEXT,
    gp BIGINT,
    goals BIGINT,
    assists BIGINT,
    pts BIGINT,
    pim BIGINT,
    gpg DOUBLE PRECISION,
    ppg DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS fact_player_boxscore_all (
    game_id TEXT,
    player_id TEXT,
    player_name TEXT,
    player_number DOUBLE PRECISION,
    player_position TEXT,
    team_venue TEXT,
    team_name TEXT,
    team_id TEXT,
    opp_team_name TEXT,
    date TIMESTAMP,
    season BIGINT,
    gp BIGINT,
    g BIGINT,
    a BIGINT,
    pts BIGINT,
    ga BIGINT,
    pim BIGINT,
    so BIGINT,
    skill_rating BIGINT
);

CREATE TABLE IF NOT EXISTS fact_player_game_stats (
    goals BIGINT,
    assists BIGINT,
    points BIGINT,
    shots BIGINT,
    sog BIGINT,
    shots_blocked BIGINT,
    shots_missed BIGINT,
    shooting_pct DOUBLE PRECISION,
    pass_attempts BIGINT,
    pass_completed BIGINT,
    pass_pct DOUBLE PRECISION,
    fo_wins BIGINT,
    fo_losses BIGINT,
    fo_total BIGINT,
    fo_pct DOUBLE PRECISION,
    zone_entries BIGINT,
    zone_exits BIGINT,
    giveaways BIGINT,
    takeaways BIGINT,
    toi_seconds DOUBLE PRECISION,
    toi_minutes DOUBLE PRECISION,
    shift_count BIGINT,
    logical_shifts BIGINT,
    avg_shift DOUBLE PRECISION,
    game_id TEXT,
    player_id TEXT,
    player_name TEXT
);

CREATE TABLE IF NOT EXISTS fact_player_pair_stats (
    game_id TEXT,
    player_1_id TEXT,
    player_1_name TEXT,
    player_1_rating DOUBLE PRECISION,
    player_2_id TEXT,
    player_2_name TEXT,
    player_2_rating DOUBLE PRECISION,
    shifts_together BIGINT,
    toi_together_seconds BIGINT,
    combined_rating DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS fact_playergames (
    ID TEXT,
    Date TIMESTAMP,
    "Type" TEXT,
    Team TEXT,
    Opp TEXT,
    "#" BIGINT,
    Player TEXT,
    Position TEXT,
    GP BIGINT,
    G BIGINT,
    A BIGINT,
    GA BIGINT,
    PIM BIGINT,
    SO BIGINT,
    Rank BIGINT,
    ID2 TEXT,
    ID3 TEXT,
    Season TEXT,
    SeasonPlayerID TEXT,
    player_game_id TEXT
);

CREATE TABLE IF NOT EXISTS fact_plays (
    game_id TEXT,
    play_id TEXT,
    event_count BIGINT,
    shots BIGINT,
    goals BIGINT,
    passes BIGINT,
    duration_seconds DOUBLE PRECISION,
    zone TEXT,
    resulted_in_goal BIGINT,
    resulted_in_shot BIGINT
);

CREATE TABLE IF NOT EXISTS fact_registration (
    player_full_name TEXT,
    player_id TEXT,
    season_id TEXT,
    season BIGINT,
    restricted TEXT,
    email TEXT,
    position TEXT,
    norad_experience BIGINT,
    CAF TEXT,
    highest_beer_league_played TEXT,
    skill_rating BIGINT,
    age BIGINT,
    referred_by TEXT,
    notes TEXT,
    sub_yn TEXT,
    drafted_team_name TEXT,
    drafted_team_id TEXT,
    player_season_registration_id TEXT
);

CREATE TABLE IF NOT EXISTS fact_sequences (
    game_id TEXT,
    sequence_id TEXT,
    event_count BIGINT,
    shots BIGINT,
    goals BIGINT,
    passes BIGINT,
    turnovers BIGINT,
    zone_entries BIGINT,
    duration_seconds DOUBLE PRECISION,
    start_zone TEXT,
    end_zone TEXT,
    zones_visited BIGINT,
    resulted_in_goal BIGINT,
    resulted_in_shot BIGINT
);

CREATE TABLE IF NOT EXISTS fact_shifts (
    game_id TEXT,
    shift_index BIGINT,
    period DOUBLE PRECISION,
    shift_start_seconds DOUBLE PRECISION,
    shift_end_seconds DOUBLE PRECISION,
    shift_duration DOUBLE PRECISION,
    shift_start_type TEXT,
    shift_stop_type TEXT,
    situation TEXT,
    strength TEXT,
    home_goals DOUBLE PRECISION,
    away_goals DOUBLE PRECISION,
    home_ozone_start DOUBLE PRECISION,
    home_ozone_end DOUBLE PRECISION,
    home_dzone_start DOUBLE PRECISION,
    home_dzone_end DOUBLE PRECISION,
    home_nzone_start DOUBLE PRECISION,
    home_nzone_end DOUBLE PRECISION,
    home_team TEXT,
    away_team TEXT,
    home_forward_1_id TEXT,
    home_forward_1_name TEXT,
    home_forward_1_number DOUBLE PRECISION,
    home_forward_2_id TEXT,
    home_forward_2_name TEXT,
    home_forward_2_number DOUBLE PRECISION,
    home_forward_3_id TEXT,
    home_forward_3_name TEXT,
    home_forward_3_number DOUBLE PRECISION,
    home_defense_1_id TEXT,
    home_defense_1_name TEXT,
    home_defense_1_number DOUBLE PRECISION,
    home_defense_2_id TEXT,
    home_defense_2_name TEXT,
    home_defense_2_number DOUBLE PRECISION,
    home_goalie_id TEXT,
    home_goalie_name TEXT,
    home_goalie_number BIGINT,
    home_xtra_id TEXT,
    home_xtra_name DOUBLE PRECISION,
    home_xtra_number DOUBLE PRECISION,
    away_forward_1_id TEXT,
    away_forward_1_name TEXT,
    away_forward_1_number DOUBLE PRECISION,
    away_forward_2_id TEXT,
    away_forward_2_name TEXT,
    away_forward_2_number DOUBLE PRECISION,
    away_forward_3_id TEXT,
    away_forward_3_name TEXT,
    away_forward_3_number DOUBLE PRECISION,
    away_defense_1_id TEXT,
    away_defense_1_name TEXT,
    away_defense_1_number DOUBLE PRECISION,
    away_defense_2_id TEXT,
    away_defense_2_name TEXT,
    away_defense_2_number DOUBLE PRECISION,
    away_goalie_id TEXT,
    away_goalie_name TEXT,
    away_goalie_number BIGINT,
    away_xtra_id TEXT,
    away_xtra_name DOUBLE PRECISION,
    away_xtra_number DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS fact_shifts_player (
    game_id TEXT,
    shift_index BIGINT,
    player_number BIGINT,
    venue TEXT,
    slot TEXT,
    period DOUBLE PRECISION,
    shift_duration DOUBLE PRECISION,
    situation TEXT,
    strength TEXT,
    stoppage_time DOUBLE PRECISION,
    player_id TEXT,
    player_name TEXT,
    logical_shift_number BIGINT,
    shift_segment BIGINT,
    cumulative_shift_duration DOUBLE PRECISION,
    running_toi DOUBLE PRECISION,
    playing_duration DOUBLE PRECISION,
    running_playing_toi DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS fact_team_game_stats (
    game_id TEXT,
    team_name TEXT,
    team_venue TEXT,
    goals_for BIGINT,
    goals_against BIGINT,
    assists BIGINT,
    sog BIGINT,
    shots_total BIGINT,
    pass_att BIGINT,
    pass_comp BIGINT,
    pass_pct BIGINT,
    giveaways BIGINT,
    takeaways BIGINT,
    to_diff BIGINT,
    zone_entries BIGINT,
    zone_exits BIGINT,
    fow BIGINT,
    fol BIGINT,
    fo_pct BIGINT,
    puck_recoveries BIGINT,
    puck_retrievals BIGINT,
    total_toi_minutes DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS fact_team_standings_snapshot (
    game_id TEXT,
    date TIMESTAMP,
    team_name TEXT,
    games_played BIGINT,
    wins BIGINT,
    losses BIGINT,
    ties BIGINT,
    points BIGINT,
    goals_for BIGINT,
    goals_against BIGINT,
    goal_diff BIGINT,
    gaa DOUBLE PRECISION,
    gpg DOUBLE PRECISION
);
