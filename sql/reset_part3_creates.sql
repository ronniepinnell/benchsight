
CREATE TABLE public."dim_player" (
    "player_first_name" TEXT,
    "player_last_name" TEXT,
    "player_full_name" TEXT,
    "player_id" TEXT,
    "player_primary_position" TEXT,
    "current_skill_rating" BIGINT,
    "birth_year" DOUBLE PRECISION,
    "player_gender" TEXT,
    "highest_beer_league" TEXT,
    "player_rating_ly" BIGINT,
    "player_leadership" TEXT,
    "player_norad" TEXT,
    "player_norad_current_team" TEXT,
    "player_norad_current_team_id" TEXT,
    "other_url" TEXT,
    "player_url" TEXT,
    "player_image" TEXT,
    "random_player_first_name" TEXT,
    "random_player_last_name" TEXT,
    "random_player_full_name" TEXT
);


CREATE TABLE public."dim_player_role" (
    "role_id" TEXT,
    "role_code" TEXT,
    "role_name" TEXT,
    "role_type" TEXT,
    "sort_order" BIGINT
);


CREATE TABLE public."dim_playerurlref" (
    "n_player_url" TEXT,
    "player_full_name" TEXT,
    "n_player_id_2" TEXT
);


CREATE TABLE public."dim_position" (
    "position_id" TEXT,
    "position_code" TEXT,
    "position_name" TEXT,
    "position_type" TEXT
);


CREATE TABLE public."dim_randomnames" (
    "random_full_name" TEXT,
    "random_first_name" TEXT,
    "random_last_name" TEXT,
    "gender" TEXT,
    "name_used" TEXT
);


CREATE TABLE public."dim_rating" (
    "rating_id" TEXT,
    "rating_value" BIGINT,
    "rating_name" TEXT
);


CREATE TABLE public."dim_rating_matchup" (
    "matchup_id" TEXT,
    "matchup_name" TEXT,
    "min_diff" DOUBLE PRECISION,
    "max_diff" DOUBLE PRECISION
);


CREATE TABLE public."dim_rink_zone" (
    "rink_zone_id" TEXT,
    "zone_code" TEXT,
    "zone_name" TEXT,
    "granularity" TEXT,
    "x_min" BIGINT,
    "x_max" BIGINT,
    "y_min" DOUBLE PRECISION,
    "y_max" DOUBLE PRECISION,
    "zone" TEXT,
    "danger" TEXT,
    "side" TEXT,
    "x_description" TEXT,
    "y_description" TEXT
);


CREATE TABLE public."dim_save_outcome" (
    "save_outcome_id" TEXT,
    "save_outcome_code" TEXT,
    "save_outcome_name" TEXT,
    "causes_stoppage" BOOLEAN
);


CREATE TABLE public."dim_schedule" (
    "game_id" BIGINT,
    "season" BIGINT,
    "season_id" TEXT,
    "game_url" TEXT,
    "date" TEXT,
    "game_time" DOUBLE PRECISION,
    "home_team_name" TEXT,
    "away_team_name" TEXT,
    "home_team_id" TEXT,
    "away_team_id" TEXT,
    "head_to_head_id" TEXT,
    "game_type" TEXT,
    "playoff_round" TEXT,
    "last_period_type" TEXT,
    "period_length" TEXT,
    "ot_period_length" TEXT,
    "shootout_rounds" BIGINT,
    "schedule_type" TEXT,
    "include" BOOLEAN,
    "home_total_goals" BIGINT,
    "away_total_goals" BIGINT,
    "home_team_period1_goals" BIGINT,
    "home_team_period2_goals" BIGINT,
    "home_team_period3_goals" BIGINT,
    "home_team_periodOT_goals" DOUBLE PRECISION,
    "away_team_period1_goals" BIGINT,
    "away_team_period2_goals" BIGINT,
    "away_team_period3_goals" BIGINT,
    "away_team_periodOT_goals" BIGINT,
    "home_team_seeding" DOUBLE PRECISION,
    "away_team_seeding" DOUBLE PRECISION,
    "home_team_w" BIGINT,
    "home_team_l" BIGINT,
    "home_team_t" BIGINT,
    "home_team_pts" BIGINT,
    "away_team_w" BIGINT,
    "away_team_l" BIGINT,
    "away_team_t" BIGINT,
    "away_team_pts" BIGINT
);


CREATE TABLE public."dim_season" (
    "season_id" TEXT,
    "season" BIGINT,
    "session" TEXT,
    "norad" TEXT,
    "csah" TEXT,
    "league_id" TEXT,
    "league" TEXT,
    "start_date" TEXT,
    "season_display" TEXT
);


CREATE TABLE public."dim_shift_duration" (
    "shift_duration_id" TEXT,
    "duration_bucket" TEXT,
    "min_seconds" BIGINT,
    "max_seconds" BIGINT,
    "description" TEXT,
    "fatigue_level" TEXT,
    "typical_scenario" TEXT
);


CREATE TABLE public."dim_shift_quality_tier" (
    "tier_id" TEXT,
    "tier_code" TEXT,
    "tier_name" TEXT,
    "score_min" BIGINT,
    "score_max" BIGINT,
    "description" TEXT
);


CREATE TABLE public."dim_shift_slot" (
    "slot_id" TEXT,
    "slot_code" TEXT,
    "slot_name" TEXT
);


CREATE TABLE public."dim_shift_start_type" (
    "shift_start_type_id" TEXT,
    "shift_start_type_name" TEXT
);


CREATE TABLE public."dim_shift_stop_type" (
    "shift_stop_type_id" TEXT,
    "shift_stop_type_name" TEXT
);


CREATE TABLE public."dim_shot_outcome" (
    "shot_outcome_id" TEXT,
    "shot_outcome_code" TEXT,
    "shot_outcome_name" TEXT,
    "is_goal" BOOLEAN,
    "is_save" BOOLEAN,
    "is_block" BOOLEAN,
    "is_miss" BOOLEAN,
    "xg_multiplier" DOUBLE PRECISION
);


CREATE TABLE public."dim_shot_type" (
    "shot_type_id" TEXT,
    "shot_type_code" TEXT,
    "shot_type_name" TEXT,
    "description" TEXT
);


CREATE TABLE public."dim_situation" (
    "situation_id" TEXT,
    "situation_name" TEXT
);


CREATE TABLE public."dim_stat" (
    "stat_id" TEXT,
    "stat_code" TEXT,
    "stat_name" TEXT,
    "category" TEXT,
    "description" TEXT,
    "formula" TEXT,
    "player_role" TEXT,
    "computable_now" BOOLEAN,
    "benchmark_elite" DOUBLE PRECISION,
    "nhl_avg_per_game" DOUBLE PRECISION,
    "nhl_elite_threshold" DOUBLE PRECISION,
    "nhl_min_threshold" BIGINT
);