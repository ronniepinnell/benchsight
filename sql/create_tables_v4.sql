-- BENCHSIGHT v4.0.0 - CREATE TABLES
-- Generated automatically from output data

CREATE TABLE IF NOT EXISTS dim_danger_zone (
    danger_zone_id TEXT,
    danger_zone_code TEXT,
    danger_zone_name TEXT,
    xg_multiplier TEXT
);

CREATE TABLE IF NOT EXISTS dim_game_players_tracking (
    In cell B3 TEXT,
    game_id TEXT
);

CREATE TABLE IF NOT EXISTS dim_league (
    league_id TEXT,
    league TEXT
);

CREATE TABLE IF NOT EXISTS dim_period (
    period_id TEXT,
    period_code TEXT,
    period_name TEXT,
    period_type TEXT
);

CREATE TABLE IF NOT EXISTS dim_player (
    player_first_name TEXT,
    player_last_name TEXT,
    player_full_name TEXT,
    player_id TEXT,
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
    role_id TEXT,
    role_code TEXT,
    role_name TEXT,
    role_type TEXT
);

CREATE TABLE IF NOT EXISTS dim_playerurlref (
    n_player_url TEXT,
    player_full_name TEXT,
    n_player_id_2 TEXT
);

CREATE TABLE IF NOT EXISTS dim_position (
    position_id TEXT,
    position_code TEXT,
    position_name TEXT
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
    box_id TEXT,
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
    game_id TEXT,
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
    season_id TEXT,
    season TEXT,
    session TEXT,
    norad TEXT,
    csah TEXT,
    league_id TEXT,
    league TEXT,
    start_date TEXT
);

CREATE TABLE IF NOT EXISTS dim_team (
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

CREATE TABLE IF NOT EXISTS dim_venue (
    venue_id TEXT,
    venue_code TEXT,
    venue_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_zone (
    zone_id TEXT,
    zone_code TEXT,
    zone_name TEXT
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
    player_draft_id TEXT
);

CREATE TABLE IF NOT EXISTS fact_event_players_tracking (
    event_id TEXT,
    game_id TEXT,
    event_index TEXT,
    player_game_number TEXT,
    player_role TEXT,
    role_number TEXT,
    player_team TEXT,
    play_detail1 TEXT,
    play_detail_2 TEXT,
    play_detail_successful TEXT
);

CREATE TABLE IF NOT EXISTS fact_events (
    event_id TEXT,
    game_id TEXT,
    event_index TEXT,
    period TEXT,
    event_type TEXT,
    detail_1 TEXT,
    detail_2 TEXT,
    success TEXT,
    zone TEXT,
    shift_index TEXT,
    linked_event_index TEXT,
    home_team TEXT,
    away_team TEXT,
    duration TEXT,
    event_start_min TEXT,
    event_start_sec TEXT,
    event_end_min TEXT,
    event_end_sec TEXT
);

CREATE TABLE IF NOT EXISTS fact_events_long (
    event_id TEXT,
    game_id TEXT,
    event_index TEXT,
    period TEXT,
    event_type TEXT,
    player_number TEXT,
    player_role TEXT,
    role_number TEXT,
    player_team TEXT,
    play_detail1 TEXT,
    play_detail_2 TEXT,
    player_id TEXT
);

CREATE TABLE IF NOT EXISTS fact_events_tracking (
    event_id TEXT,
    game_id TEXT,
    event_index TEXT,
    event_index_flag_ TEXT,
    sequence_index_flag_ TEXT,
    play_index_flag_ TEXT,
    linked_event_index_flag_ TEXT,
    event_start_min_ TEXT,
    event_start_sec_ TEXT,
    event_end_min_ TEXT,
    event_end_sec_ TEXT,
    player_game_number_ TEXT,
    event_team_zone_ TEXT,
    event_type_ TEXT,
    event_detail_ TEXT,
    event_detail_2_ TEXT,
    event_successful_ TEXT,
    play_detail1_ TEXT,
    play_detail2_ TEXT,
    play_detail_successful_ TEXT,
    pressured_pressurer_ TEXT,
    event_index_ TEXT,
    linked_event_index_ TEXT,
    sequence_index_ TEXT,
    play_index_ TEXT,
    team_ TEXT,
    player_game_number TEXT,
    role_abrev_binary_ TEXT,
    period TEXT,
    linked_event_index TEXT,
    tracking_event_index TEXT,
    event_start_min TEXT,
    event_start_sec TEXT,
    event_end_min TEXT,
    event_end_sec TEXT,
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
    sequence_index TEXT,
    play_index TEXT,
    play_detail1 TEXT,
    play_detail_2 TEXT,
    play_detail_successful TEXT,
    pressured_pressurer TEXT,
    zone_change_index TEXT,
    home_team TEXT,
    away_team TEXT,
    Type TEXT,
    event_detail TEXT,
    event_detail_2 TEXT,
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
    player_id TEXT,
    player_team TEXT,
    player_num_dup_ TEXT
);

CREATE TABLE IF NOT EXISTS fact_gameroster (
    game_id TEXT,
    team_game_id TEXT,
    opp_team_game_id TEXT,
    player_game_id TEXT,
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

CREATE TABLE IF NOT EXISTS fact_playergames (
    player_game_id TEXT,
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
    SeasonPlayerID TEXT
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
    player_season_registration_id TEXT
);

CREATE TABLE IF NOT EXISTS fact_shift_players_tracking (
    shift_id TEXT,
    game_id TEXT,
    shift_index TEXT,
    player_game_number TEXT,
    position_slot TEXT,
    player_id TEXT
);

CREATE TABLE IF NOT EXISTS fact_shifts (
    shift_id TEXT,
    game_id TEXT,
    shift_index TEXT,
    period TEXT,
    start_type TEXT,
    stop_type TEXT,
    shift_start_min TEXT,
    shift_start_sec TEXT,
    shift_end_min TEXT,
    shift_end_sec TEXT,
    home_f1 TEXT,
    home_f2 TEXT,
    home_f3 TEXT,
    home_d1 TEXT,
    home_d2 TEXT,
    home_g TEXT,
    away_f1 TEXT,
    away_f2 TEXT,
    away_f3 TEXT,
    away_d1 TEXT,
    away_d2 TEXT,
    away_g TEXT
);

CREATE TABLE IF NOT EXISTS fact_shifts_tracking (
    shift_id TEXT,
    game_id TEXT,
    shift_index TEXT,
    Period TEXT,
    shift_start_min TEXT,
    shift_start_sec TEXT,
    shift_end_min TEXT,
    shift_end_sec TEXT,
    shift_start_type TEXT,
    shift_stop_type TEXT,
    home_forward_1 TEXT,
    home_forward_2 TEXT,
    home_forward_3 TEXT,
    home_defense_1 TEXT,
    home_defense_2 TEXT,
    home_xtra TEXT,
    home_goalie TEXT,
    away_forward_1 TEXT,
    away_forward_2 TEXT,
    away_forward_3 TEXT,
    away_defense_1 TEXT,
    away_defense_2 TEXT,
    away_xtra TEXT,
    away_goalie TEXT,
    stoppage_time TEXT,
    home_ozone_start TEXT,
    home_ozone_end TEXT,
    home_dzone_start TEXT,
    home_dzone_end TEXT,
    home_nzone_start TEXT,
    home_nzone_end TEXT,
    home_team TEXT,
    away_team TEXT,
    shift_start_total_seconds TEXT,
    shift_end_total_seconds TEXT,
    shift_duration TEXT,
    home_team_strength TEXT,
    away_team_strength TEXT,
    home_team_en TEXT,
    away_team_en TEXT,
    home_team_pk TEXT,
    home_team_pp TEXT,
    away_team_pp TEXT,
    away_team_pk TEXT,
    situation TEXT,
    strength TEXT,
    home_goals TEXT,
    away_goals TEXT,
    home_team_plus TEXT,
    home_team_minus TEXT,
    away_team_plus TEXT,
    away_team_minus TEXT,
    period_start_total_running_seconds TEXT,
    running_video_time TEXT,
    shift_start_running_time TEXT,
    shift_end_running_time TEXT
);
