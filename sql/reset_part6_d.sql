CREATE TABLE public."fact_player_stats_long" (
    "player_game_key" TEXT,
    "game_id" BIGINT,
    "player_id" TEXT,
    "stat_code" TEXT,
    "stat_value" DOUBLE PRECISION,
    "stat_long_key" TEXT,
    "_export_timestamp" TEXT,
    "player_name" TEXT
);



CREATE TABLE public."fact_player_trends" (
    "player_trend_key" TEXT,
    "player_id" TEXT,
    "game_id" BIGINT,
    "game_number" BIGINT,
    "points" DOUBLE PRECISION,
    "cumulative_points" DOUBLE PRECISION,
    "rolling_avg_points" DOUBLE PRECISION,
    "goals" DOUBLE PRECISION,
    "cumulative_goals" DOUBLE PRECISION,
    "toi_minutes" DOUBLE PRECISION,
    "trend_direction" TEXT
);



CREATE TABLE public."fact_player_xy_long" (
    "player_xy_key" TEXT,
    "event_id" TEXT,
    "game_id" BIGINT,
    "player_id" TEXT,
    "player_name" TEXT,
    "player_role" TEXT,
    "is_event_team" BOOLEAN,
    "point_number" BIGINT,
    "x" DOUBLE PRECISION,
    "y" DOUBLE PRECISION,
    "is_start" BIGINT,
    "is_stop" BIGINT,
    "distance_to_net" DOUBLE PRECISION,
    "angle_to_net" DOUBLE PRECISION,
    "_export_timestamp" TEXT
);



CREATE TABLE public."fact_player_xy_wide" (
    "player_xy_key" TEXT,
    "event_id" TEXT,
    "game_id" BIGINT,
    "player_id" TEXT,
    "player_name" TEXT,
    "player_role" TEXT,
    "is_event_team" BOOLEAN,
    "point_count" BIGINT,
    "x_1" DOUBLE PRECISION,
    "y_1" DOUBLE PRECISION,
    "x_2" DOUBLE PRECISION,
    "y_2" DOUBLE PRECISION,
    "x_3" DOUBLE PRECISION,
    "y_3" DOUBLE PRECISION,
    "x_4" DOUBLE PRECISION,
    "y_4" DOUBLE PRECISION,
    "x_5" DOUBLE PRECISION,
    "y_5" DOUBLE PRECISION,
    "x_6" DOUBLE PRECISION,
    "y_6" DOUBLE PRECISION,
    "x_7" DOUBLE PRECISION,
    "y_7" DOUBLE PRECISION,
    "x_8" DOUBLE PRECISION,
    "y_8" DOUBLE PRECISION,
    "x_9" DOUBLE PRECISION,
    "y_9" DOUBLE PRECISION,
    "x_10" DOUBLE PRECISION,
    "y_10" DOUBLE PRECISION,
    "x_start" DOUBLE PRECISION,
    "y_start" DOUBLE PRECISION,
    "x_end" DOUBLE PRECISION,
    "y_end" DOUBLE PRECISION,
    "distance_traveled" DOUBLE PRECISION,
    "distance_to_net_start" DOUBLE PRECISION,
    "distance_to_net_end" DOUBLE PRECISION,
    "_export_timestamp" TEXT
);



CREATE TABLE public."fact_playergames" (
    "player_id" TEXT,
    "game_id" BIGINT,
    "playergame_key" TEXT,
    "_export_timestamp" TEXT,
    "player_name" TEXT
);

