-- BENCHSIGHT v5.3.0 - CREATE TABLES
-- Key Format: {PREFIX}{GAME_ID:05d}{INDEX:05d} = 12 characters (facts)
-- Key Format: {PREFIX}{INDEX:04d} = 6 characters (dimensions)
-- Tables: 38 dimensions, 13 facts

CREATE TABLE IF NOT EXISTS dim_event_detail (
    event_detail_id TEXT PRIMARY KEY,
    event_detail_code TEXT,
    event_detail_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_event_detail_2 (
    event_detail_2_id TEXT PRIMARY KEY,
    event_detail_2_code TEXT,
    event_detail_2_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_event_type (
    event_type_id TEXT PRIMARY KEY,
    event_type_code TEXT,
    event_type_name TEXT,
    event_category TEXT
);

CREATE TABLE IF NOT EXISTS dim_giveaway_type (
    giveaway_type_id TEXT PRIMARY KEY,
    giveaway_type_code TEXT,
    giveaway_type_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_league (
    league_id TEXT PRIMARY KEY,
    league TEXT
);

CREATE TABLE IF NOT EXISTS dim_net_location (
    net_location_id TEXT PRIMARY KEY,
    net_location_code TEXT,
    net_location_name TEXT,
    description TEXT,
    height_zone TEXT,
    side_zone TEXT
);

CREATE TABLE IF NOT EXISTS dim_pass_type (
    pass_type_id TEXT PRIMARY KEY,
    pass_type_code TEXT,
    pass_type_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_period (
    period_id TEXT PRIMARY KEY,
    period_number TEXT,
    period_name TEXT,
    period_type TEXT,
    period_minutes TEXT
);

CREATE TABLE IF NOT EXISTS dim_play_detail (
    play_detail_id TEXT PRIMARY KEY,
    play_detail_code TEXT,
    play_detail_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_play_detail_2 (
    play_detail_2_id TEXT PRIMARY KEY,
    play_detail_2_code TEXT,
    play_detail_2_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_player (
    player_first_name TEXT,
    player_last_name TEXT,
    player_full_name TEXT,
    player_id TEXT PRIMARY KEY,
    player_primary_position TEXT,
    current_skill_rating TEXT,
    player_hand TEXT,
    birth_year TEXT,
    player_gender TEXT,
    highest_beer_league TEXT,
    player_rating_ly TEXT,
    player_notes TEXT,
    player_leadership TEXT,
    player_norad TEXT,
    player_csaha TEXT,
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

CREATE TABLE IF NOT EXISTS dim_player_role (
    role_id TEXT PRIMARY KEY,
    role_code TEXT,
    role_name TEXT,
    role_type TEXT,
    sort_order TEXT
);

CREATE TABLE IF NOT EXISTS dim_playerurlref (
    n_player_url TEXT,
    player_full_name TEXT,
    n_player_id_2 TEXT
);

CREATE TABLE IF NOT EXISTS dim_position (
    position_id TEXT PRIMARY KEY,
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
    box_id TEXT PRIMARY KEY,
    box_id_rev TEXT,
    x_min TEXT,
    x_max TEXT,
    y_min TEXT,
    y_max TEXT,
    area TEXT,
    x_description TEXT,
    y_description TEXT,
    danger TEXT,
    zone TEXT,
    side TEXT
);

CREATE TABLE IF NOT EXISTS dim_rinkcoordzones (
    box_id TEXT PRIMARY KEY,
    box_id_rev TEXT,
    x_min TEXT,
    x_max TEXT,
    y_min TEXT,
    y_max TEXT,
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
    game_id TEXT PRIMARY KEY,
    season TEXT,
    season_id TEXT,
    game_url TEXT,
    home_team_game_id TEXT,
    away_team_game_id TEXT,
    date TEXT,
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
    shootout_rounds TEXT,
    home_total_goals TEXT,
    away_total_goals TEXT,
    home_team_period1_goals TEXT,
    home_team_period2_goals TEXT,
    home_team_period3_goals TEXT,
    home_team_periodOT_goals TEXT,
    away_team_period1_goals TEXT,
    away_team_period2_goals TEXT,
    away_team_period3_goals TEXT,
    away_team_periodOT_goals TEXT,
    home_team_seeding TEXT,
    away_team_seeding TEXT,
    home_team_w TEXT,
    home_team_l TEXT,
    home_team_t TEXT,
    home_team_pts TEXT,
    away_team_w TEXT,
    away_team_l TEXT,
    away_team_t TEXT,
    away_team_pts TEXT,
    video_id TEXT,
    video_start_time TEXT,
    video_end_time TEXT,
    video_title TEXT,
    video_url TEXT
);

CREATE TABLE IF NOT EXISTS dim_season (
    season_id TEXT PRIMARY KEY,
    season TEXT,
    session TEXT,
    norad TEXT,
    csah TEXT,
    league_id TEXT,
    league TEXT,
    start_date TEXT
);

CREATE TABLE IF NOT EXISTS dim_shift_slot (
    slot_id TEXT PRIMARY KEY,
    slot_code TEXT,
    slot_name TEXT,
    slot_type TEXT,
    sort_order TEXT
);

CREATE TABLE IF NOT EXISTS dim_shift_start_type (
    shift_start_type_id TEXT PRIMARY KEY,
    shift_start_type_code TEXT,
    shift_start_type_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_shift_stop_type (
    shift_stop_type_id TEXT PRIMARY KEY,
    shift_stop_type_code TEXT,
    shift_stop_type_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_shot_type (
    shot_type_id TEXT PRIMARY KEY,
    shot_type_code TEXT,
    shot_type_name TEXT,
    is_goal TEXT
);

CREATE TABLE IF NOT EXISTS dim_situation (
    situation_id TEXT PRIMARY KEY,
    situation_code TEXT,
    situation_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_stat (
    stat_id TEXT PRIMARY KEY,
    stat_code TEXT,
    stat_name TEXT,
    category TEXT,
    description TEXT,
    formula TEXT,
    player_role TEXT,
    computable_now TEXT,
    benchmark_elite TEXT
);

CREATE TABLE IF NOT EXISTS dim_stat_type (
    stat_id TEXT PRIMARY KEY,
    stat_name TEXT,
    stat_category TEXT,
    stat_level TEXT,
    computable_now TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS dim_stoppage_type (
    stoppage_type_id TEXT PRIMARY KEY,
    stoppage_type_code TEXT,
    stoppage_type_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_strength (
    strength_id TEXT PRIMARY KEY,
    strength_code TEXT,
    strength_base TEXT,
    is_empty_net TEXT,
    home_empty_net TEXT,
    away_empty_net TEXT
);

CREATE TABLE IF NOT EXISTS dim_success (
    success_id TEXT PRIMARY KEY,
    success_code TEXT,
    success_name TEXT,
    success_value TEXT
);

CREATE TABLE IF NOT EXISTS dim_takeaway_type (
    takeaway_type_id TEXT PRIMARY KEY,
    takeaway_type_code TEXT,
    takeaway_type_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_team (
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

CREATE TABLE IF NOT EXISTS dim_terminology_mapping (
    dimension TEXT,
    old_value TEXT,
    new_value TEXT,
    match_type TEXT
);

CREATE TABLE IF NOT EXISTS dim_turnover_quality (
    turnover_quality_id TEXT PRIMARY KEY,
    turnover_quality_code TEXT,
    turnover_quality_name TEXT,
    description TEXT,
    counts_against TEXT
);

CREATE TABLE IF NOT EXISTS dim_turnover_type (
    turnover_type_id TEXT PRIMARY KEY,
    turnover_type_code TEXT,
    turnover_type_name TEXT,
    category TEXT,
    quality TEXT,
    weight TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS dim_venue (
    venue_id TEXT PRIMARY KEY,
    venue_code TEXT,
    venue_name TEXT,
    venue_abbrev TEXT
);

CREATE TABLE IF NOT EXISTS dim_zone (
    zone_id TEXT PRIMARY KEY,
    zone_code TEXT,
    zone_name TEXT,
    zone_abbrev TEXT
);

CREATE TABLE IF NOT EXISTS dim_zone_entry_type (
    zone_entry_type_id TEXT PRIMARY KEY,
    zone_entry_type_code TEXT,
    zone_entry_type_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_zone_exit_type (
    zone_exit_type_id TEXT PRIMARY KEY,
    zone_exit_type_code TEXT,
    zone_exit_type_name TEXT
);

CREATE TABLE IF NOT EXISTS fact_draft (
    team_id TEXT,
    skill_rating TEXT,
    round TEXT,
    player_full_name TEXT,
    player_id TEXT,
    team_name TEXT,
    restricted TEXT,
    overall_draft_round TEXT,
    overall_draft_position TEXT,
    unrestricted_draft_position TEXT,
    season TEXT,
    season_id TEXT,
    league TEXT,
    player_draft_id TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS fact_events (
    event_id TEXT PRIMARY KEY,
    game_id TEXT,
    event_index TEXT,
    shift_index TEXT,
    linked_event_index TEXT,
    duration TEXT,
    period_id TEXT,
    event_type_id TEXT,
    event_detail_id TEXT,
    event_detail_2_id TEXT,
    success_id TEXT,
    zone_id TEXT,
    home_team_id TEXT,
    away_team_id TEXT
);

CREATE TABLE IF NOT EXISTS fact_events_long (
    event_player_id TEXT PRIMARY KEY,
    event_id TEXT,
    game_id TEXT,
    event_index TEXT,
    player_game_number TEXT,
    player_id TEXT,
    player_role TEXT,
    player_team TEXT,
    period_id TEXT,
    event_type_id TEXT,
    event_detail_id TEXT,
    event_detail_2_id TEXT,
    play_detail_id TEXT,
    play_detail_2_id TEXT,
    zone_id TEXT,
    success_id TEXT
);

CREATE TABLE IF NOT EXISTS fact_events_tracking (
    event_id TEXT PRIMARY KEY,
    game_id TEXT,
    event_index TEXT,
    player_id TEXT,
    player_game_number TEXT,
    period TEXT,
    linked_event_index TEXT,
    tracking_event_index TEXT,
    event_start_min TEXT,
    event_start_sec TEXT,
    event_end_min TEXT,
    event_end_sec TEXT,
    role_abrev TEXT,
    home_team_zone TEXT,
    away_team_zone TEXT,
    team_venue TEXT,
    team_venue_abv TEXT,
    side_of_puck TEXT,
    sequence_index TEXT,
    play_index TEXT,
    pressured_pressurer TEXT,
    zone_change_index TEXT,
    event_successful TEXT,
    shift_index TEXT,
    duration TEXT,
    time_start_total_seconds TEXT,
    time_end_total_seconds TEXT,
    running_intermission_duration TEXT,
    period_start_total_running_seconds TEXT,
    running_video_time TEXT,
    event_running_start TEXT,
    event_running_end TEXT,
    player_role TEXT,
    role_number TEXT,
    event_type_id TEXT,
    event_detail_id TEXT,
    event_detail_2_id TEXT,
    play_detail_id TEXT,
    play_detail_2_id TEXT,
    zone_id TEXT,
    success_id TEXT,
    period_id TEXT,
    shot_type_id TEXT,
    pass_type_id TEXT,
    giveaway_type_id TEXT,
    takeaway_type_id TEXT,
    zone_entry_type_id TEXT,
    zone_exit_type_id TEXT,
    stoppage_type_id TEXT,
    home_team_id TEXT,
    away_team_id TEXT,
    player_team_id TEXT,
    sequence_id TEXT,
    play_id TEXT,
    linked_event_id TEXT,
    turnover_quality_id TEXT
);

CREATE TABLE IF NOT EXISTS fact_gameroster (
    game_id TEXT,
    team_game_id TEXT,
    opp_team_game_id TEXT,
    player_game_id TEXT PRIMARY KEY,
    team_venue TEXT,
    team_name TEXT,
    opp_team_name TEXT,
    player_game_number TEXT,
    n_player_url TEXT,
    player_position TEXT,
    games_played TEXT,
    goals TEXT,
    assist TEXT,
    goals_against TEXT,
    pim TEXT,
    shutouts TEXT,
    team_id TEXT,
    opp_team_id TEXT,
    key TEXT,
    player_full_name TEXT,
    player_id TEXT,
    date TEXT,
    season TEXT,
    sub TEXT,
    current_team TEXT,
    skill_rating TEXT
);

CREATE TABLE IF NOT EXISTS fact_goalie_game_stats (
    goalie_game_stat_id TEXT PRIMARY KEY,
    game_id TEXT,
    player_id TEXT,
    team_venue TEXT,
    sa TEXT,
    ga TEXT,
    sv TEXT,
    sv_pct TEXT,
    toi_seconds TEXT,
    sv_wrist TEXT,
    sv_slap TEXT,
    sv_snap TEXT,
    sv_backhand TEXT,
    sv_glove TEXT,
    sv_blocker TEXT,
    sv_pad TEXT,
    sv_5hole TEXT,
    sv_pct_pp TEXT,
    sv_pct_pk TEXT,
    sv_pct_breakaway TEXT,
    sv_pct_odd_man TEXT,
    rebound_pct TEXT,
    freeze_pct TEXT,
    first_save_pct TEXT,
    gsae TEXT,
    hd_sv_pct TEXT,
    sv_pct_slot TEXT,
    quality_start TEXT,
    gaa TEXT
);

CREATE TABLE IF NOT EXISTS fact_leadership (
    player_full_name TEXT,
    player_id TEXT,
    leadership TEXT,
    skill_rating TEXT,
    n_player_url TEXT,
    team_name TEXT,
    team_id TEXT,
    season TEXT,
    season_id TEXT
);

CREATE TABLE IF NOT EXISTS fact_player_game_stats (
    player_game_stat_id TEXT PRIMARY KEY,
    game_id TEXT,
    player_id TEXT,
    team_venue TEXT,
    position TEXT,
    g TEXT,
    a TEXT,
    a1 TEXT,
    a2 TEXT,
    pts TEXT,
    sog TEXT,
    sh_pct TEXT,
    toi_seconds TEXT,
    toi_playing_seconds TEXT,
    shifts TEXT,
    avg_shift_length TEXT,
    pass_att TEXT,
    pass_comp TEXT,
    pass_pct TEXT,
    give TEXT,
    give_bad TEXT,
    take TEXT,
    to_diff TEXT,
    zone_entry TEXT,
    zone_entry_controlled TEXT,
    zone_exit TEXT,
    zone_exit_controlled TEXT,
    fow TEXT,
    fol TEXT,
    fo_pct TEXT,
    cf TEXT,
    ca TEXT,
    cf_pct TEXT,
    ff TEXT,
    fa TEXT,
    ff_pct TEXT,
    xg TEXT,
    xga TEXT,
    hdcf TEXT,
    hdca TEXT,
    deke TEXT,
    screen TEXT,
    one_timer TEXT,
    rebound_att TEXT,
    blk TEXT,
    hit TEXT,
    stick_check TEXT,
    poke_check TEXT,
    backcheck TEXT,
    g_60 TEXT,
    sog_60 TEXT,
    pts_60 TEXT,
    plus_minus TEXT,
    pim TEXT,
    pen_taken TEXT,
    pen_drawn TEXT,
    skill_diff TEXT,
    pts_vs_higher TEXT
);

CREATE TABLE IF NOT EXISTS fact_playergames (
    ID TEXT,
    Date TEXT,
    Type TEXT,
    Team TEXT,
    Opp TEXT,
    # TEXT,
    Player TEXT,
    Position TEXT,
    GP TEXT,
    G TEXT,
    A TEXT,
    GA TEXT,
    PIM TEXT,
    SO TEXT,
    Rank TEXT,
    ID2 TEXT,
    ID3 TEXT,
    Season TEXT,
    SeasonPlayerID TEXT,
    player_game_id TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS fact_registration (
    player_full_name TEXT,
    player_id TEXT,
    season_id TEXT,
    season TEXT,
    restricted TEXT,
    email TEXT,
    position TEXT,
    norad_experience TEXT,
    CAF TEXT,
    highest_beer_league_played TEXT,
    skill_rating TEXT,
    age TEXT,
    referred_by TEXT,
    notes TEXT,
    sub_yn TEXT,
    drafted_team_name TEXT,
    drafted_team_id TEXT,
    player_season_registration_id TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS fact_shifts (
    shift_id TEXT PRIMARY KEY,
    game_id TEXT,
    shift_index TEXT,
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
    period_id TEXT
);

CREATE TABLE IF NOT EXISTS fact_shifts_long (
    shift_player_id TEXT PRIMARY KEY,
    shift_id TEXT,
    game_id TEXT,
    shift_index TEXT,
    player_game_number TEXT,
    player_id TEXT,
    slot_id TEXT,
    venue_id TEXT,
    period_id TEXT
);

CREATE TABLE IF NOT EXISTS fact_shifts_tracking (
    shift_id TEXT PRIMARY KEY,
    game_id TEXT,
    shift_index TEXT,
    shift_start_min TEXT,
    shift_start_sec TEXT,
    shift_end_min TEXT,
    shift_end_sec TEXT,
    stoppage_time TEXT,
    home_ozone_start TEXT,
    home_ozone_end TEXT,
    home_dzone_start TEXT,
    home_dzone_end TEXT,
    home_nzone_start TEXT,
    home_nzone_end TEXT,
    shift_start_total_seconds TEXT,
    shift_end_total_seconds TEXT,
    shift_duration TEXT,
    home_team_strength TEXT,
    away_team_strength TEXT,
    home_goals TEXT,
    away_goals TEXT,
    home_team_plus TEXT,
    home_team_minus TEXT,
    away_team_plus TEXT,
    away_team_minus TEXT,
    period_start_total_running_seconds TEXT,
    running_video_time TEXT,
    shift_start_running_time TEXT,
    shift_end_running_time TEXT,
    shift_start_type_id TEXT,
    shift_stop_type_id TEXT,
    situation_id TEXT,
    period_id TEXT,
    home_team_id TEXT,
    away_team_id TEXT,
    strength_id TEXT,
    home_forward_1_id TEXT,
    home_forward_2_id TEXT,
    home_forward_3_id TEXT,
    home_defense_1_id TEXT,
    home_defense_2_id TEXT,
    home_xtra_id TEXT,
    home_goalie_id TEXT,
    away_forward_1_id TEXT,
    away_forward_2_id TEXT,
    away_forward_3_id TEXT,
    away_defense_1_id TEXT,
    away_defense_2_id TEXT,
    away_xtra_id TEXT,
    away_goalie_id TEXT
);
