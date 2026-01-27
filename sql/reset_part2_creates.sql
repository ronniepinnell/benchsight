CREATE TABLE public."dim_assist_type" (
    "assist_type_id" TEXT,
    "assist_type_code" TEXT,
    "assist_type_name" TEXT,
    "points_value" BIGINT,
    "description" TEXT
);


CREATE TABLE public."dim_comparison_type" (
    "comparison_type_id" TEXT,
    "comparison_type_code" TEXT,
    "comparison_type_name" TEXT,
    "description" TEXT,
    "analysis_scope" TEXT
);


CREATE TABLE public."dim_competition_tier" (
    "competition_tier_id" TEXT,
    "tier_name" TEXT,
    "min_rating" DOUBLE PRECISION,
    "max_rating" DOUBLE PRECISION
);


CREATE TABLE public."dim_composite_rating" (
    "rating_id" TEXT,
    "rating_code" TEXT,
    "rating_name" TEXT,
    "description" TEXT,
    "scale_min" BIGINT,
    "scale_max" BIGINT
);


CREATE TABLE public."dim_danger_level" (
    "danger_level_id" TEXT,
    "danger_level_code" TEXT,
    "danger_level_name" TEXT,
    "xg_multiplier" DOUBLE PRECISION
);


CREATE TABLE public."dim_danger_zone" (
    "danger_zone_id" TEXT,
    "danger_zone_code" TEXT,
    "danger_zone_name" TEXT,
    "xg_base" DOUBLE PRECISION,
    "description" TEXT
);


CREATE TABLE public."dim_event_detail" (
    "event_detail_id" TEXT,
    "event_detail_code" TEXT,
    "event_detail_name" TEXT,
    "event_type" TEXT,
    "category" TEXT,
    "description" TEXT,
    "is_shot_on_goal" BOOLEAN,
    "is_goal" BOOLEAN,
    "is_miss" BOOLEAN,
    "is_block" BOOLEAN,
    "danger_potential" TEXT
);


CREATE TABLE public."dim_event_detail_2" (
    "event_detail_2_id" TEXT,
    "event_detail_2_code" TEXT,
    "event_detail_2_name" TEXT,
    "event_type" TEXT,
    "event_type_macro" TEXT,
    "category" TEXT,
    "description" TEXT,
    "is_shot_on_goal" BOOLEAN,
    "is_goal" BOOLEAN,
    "is_miss" BOOLEAN,
    "is_block" BOOLEAN,
    "danger_potential" TEXT
);


CREATE TABLE public."dim_event_type" (
    "event_type_id" TEXT,
    "event_type_code" TEXT,
    "event_type_name" TEXT,
    "event_category" TEXT,
    "description" TEXT,
    "is_corsi" BOOLEAN,
    "is_fenwick" BOOLEAN
);


CREATE TABLE public."dim_game_state" (
    "game_state_id" TEXT,
    "game_state_code" TEXT,
    "game_state_name" TEXT,
    "goal_diff_min" BIGINT,
    "goal_diff_max" BIGINT,
    "description" TEXT
);


CREATE TABLE public."dim_giveaway_type" (
    "giveaway_type_id" TEXT,
    "giveaway_type_code" TEXT,
    "giveaway_type_name" TEXT,
    "is_bad" BOOLEAN
);


CREATE TABLE public."dim_highlight_category" (
    "highlight_category_id" TEXT,
    "highlight_category_code" TEXT,
    "highlight_category_name" TEXT,
    "description" TEXT,
    "priority" BIGINT,
    "icon" TEXT
);


CREATE TABLE public."dim_league" (
    "league_id" TEXT,
    "league" TEXT
);


CREATE TABLE public."dim_micro_stat" (
    "micro_stat_id" TEXT,
    "stat_code" TEXT,
    "stat_name" TEXT,
    "category" TEXT
);


CREATE TABLE public."dim_net_location" (
    "net_location_id" TEXT,
    "net_location_code" TEXT,
    "net_location_name" TEXT,
    "x_pct" DOUBLE PRECISION,
    "y_pct" DOUBLE PRECISION
);


CREATE TABLE public."dim_pass_outcome" (
    "pass_outcome_id" TEXT,
    "pass_outcome_code" TEXT,
    "pass_outcome_name" TEXT,
    "is_successful" BOOLEAN
);


CREATE TABLE public."dim_pass_type" (
    "pass_type_id" TEXT,
    "pass_type_code" TEXT,
    "pass_type_name" TEXT,
    "description" TEXT
);


CREATE TABLE public."dim_period" (
    "period_id" TEXT,
    "period_number" BIGINT,
    "period_name" TEXT,
    "period_type" TEXT,
    "period_minutes" BIGINT
);


CREATE TABLE public."dim_play_detail" (
    "play_detail_id" TEXT,
    "play_detail_code" TEXT,
    "play_detail_name" TEXT,
    "play_category" TEXT,
    "skill_level" TEXT,
    "description" TEXT
);


CREATE TABLE public."dim_play_detail_2" (
    "play_detail_2_id" TEXT,
    "play_detail_2_code" TEXT,
    "play_detail_2_name" TEXT,
    "play_category" TEXT,
    "skill_level" TEXT,
    "description" TEXT
);