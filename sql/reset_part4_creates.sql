
CREATE TABLE public."dim_stat_category" (
    "stat_category_id" TEXT,
    "category_code" TEXT,
    "category_name" TEXT,
    "description" TEXT
);


CREATE TABLE public."dim_stat_type" (
    "stat_id" TEXT,
    "stat_name" TEXT,
    "stat_category" TEXT,
    "stat_level" TEXT,
    "computable_now" BOOLEAN,
    "description" TEXT
);


CREATE TABLE public."dim_stoppage_type" (
    "stoppage_type_id" TEXT,
    "stoppage_type_code" TEXT,
    "stoppage_type_name" TEXT
);


CREATE TABLE public."dim_strength" (
    "strength_id" TEXT,
    "strength_code" TEXT,
    "strength_name" TEXT,
    "situation_type" TEXT,
    "xg_multiplier" DOUBLE PRECISION,
    "description" TEXT,
    "avg_toi_pct" DOUBLE PRECISION
);


CREATE TABLE public."dim_success" (
    "success_id" TEXT,
    "success_code" TEXT,
    "success_name" TEXT,
    "is_successful" TEXT
);


CREATE TABLE public."dim_takeaway_type" (
    "takeaway_type_id" TEXT,
    "takeaway_type_code" TEXT,
    "takeaway_type_name" TEXT
);


CREATE TABLE public."dim_team" (
    "team_name" TEXT,
    "team_id" TEXT,
    "norad_team" TEXT,
    "league_id" TEXT,
    "league" TEXT,
    "long_team_name" TEXT,
    "team_cd" TEXT,
    "team_color1" TEXT,
    "team_color2" TEXT,
    "team_color3" TEXT,
    "team_color4" TEXT,
    "team_logo" TEXT,
    "team_url" TEXT
);


CREATE TABLE public."dim_terminology_mapping" (
    "dimension" TEXT,
    "old_value" TEXT,
    "new_value" TEXT,
    "match_type" TEXT
);


CREATE TABLE public."dim_time_bucket" (
    "time_bucket_id" TEXT,
    "time_bucket_code" TEXT,
    "time_bucket_name" TEXT,
    "minute_start" BIGINT,
    "minute_end" BIGINT,
    "description" TEXT
);


CREATE TABLE public."dim_turnover_quality" (
    "turnover_quality_id" TEXT,
    "turnover_quality_code" TEXT,
    "turnover_quality_name" TEXT,
    "description" TEXT,
    "counts_against" BOOLEAN
);


CREATE TABLE public."dim_turnover_type" (
    "turnover_type_id" TEXT,
    "turnover_type_code" TEXT,
    "turnover_type_name" TEXT,
    "category" TEXT,
    "quality" TEXT,
    "weight" DOUBLE PRECISION,
    "description" TEXT,
    "zone_context" TEXT,
    "zone_danger_multiplier" DOUBLE PRECISION,
    "old_equiv" TEXT
);


CREATE TABLE public."dim_venue" (
    "venue_id" TEXT,
    "venue_code" TEXT,
    "venue_name" TEXT,
    "venue_abbrev" TEXT
);


CREATE TABLE public."dim_video_type" (
    "video_type_id" TEXT,
    "video_type_code" TEXT,
    "video_type_name" TEXT,
    "description" TEXT,
    "is_primary" BOOLEAN,
    "sort_order" BIGINT,
    "use_for_highlights" BOOLEAN
);


CREATE TABLE public."dim_zone" (
    "zone_id" TEXT,
    "zone_code" TEXT,
    "zone_name" TEXT,
    "zone_abbrev" TEXT
);


CREATE TABLE public."dim_zone_entry_type" (
    "zone_entry_type_id" TEXT,
    "zone_entry_type_code" TEXT,
    "zone_entry_type_name" TEXT,
    "is_controlled" BOOLEAN
);


CREATE TABLE public."dim_zone_exit_type" (
    "zone_exit_type_id" TEXT,
    "zone_exit_type_code" TEXT,
    "zone_exit_type_name" TEXT,
    "is_controlled" BOOLEAN
);


CREATE TABLE public."dim_zone_outcome" (
    "zone_outcome_id" TEXT,
    "zone_outcome_code" TEXT,
    "zone_outcome_name" TEXT,
    "is_controlled" BOOLEAN,
    "zone_type" TEXT
);


CREATE TABLE public."fact_assists" (
    "event_id" TEXT,
    "game_id" BIGINT,
    "player_id" TEXT,
    "player_game_number" DOUBLE PRECISION,
    "sequence_key" TEXT,
    "play_key" TEXT,
    "shift_key" TEXT,
    "linked_event_key" DOUBLE PRECISION,
    "tracking_event_key" TEXT,
    "zone_change_key" TEXT,
    "period_id" TEXT,
    "event_type_id" TEXT,
    "event_detail_id" TEXT,
    "event_detail_2_id" TEXT,
    "event_success_id" TEXT,
    "home_team_id" TEXT,
    "away_team_id" TEXT,
    "player_team_id" TEXT,
    "player_role_id" TEXT,
    "play_detail_id" TEXT,
    "play_detail_2_id" TEXT,
    "play_success_id" TEXT,
    "event_type" TEXT,
    "period" BIGINT,
    "assist_to_goal_index" DOUBLE PRECISION,
    "assist_primary_event_index" DOUBLE PRECISION,
    "assist_secondary_event_index" DOUBLE PRECISION,
    "home_team" TEXT,
    "away_team" TEXT,
    "strength" TEXT,
    "event_team_zone" TEXT,
    "event_start_min" DOUBLE PRECISION,
    "event_start_sec" DOUBLE PRECISION,
    "event_end_min" DOUBLE PRECISION,
    "event_end_sec" DOUBLE PRECISION,
    "event_type_code" TEXT,
    "event_detail_code" TEXT,
    "event_detail_2_code" TEXT,
    "event_detail" TEXT,
    "event_detail_2" TEXT,
    "event_successful" TEXT,
    "time_start_total_seconds" BIGINT,
    "time_end_total_seconds" BIGINT,
    "duration" BIGINT,
    "period_start_total_running_seconds" BIGINT,
    "running_video_time" BIGINT,
    "event_running_start" BIGINT,
    "event_running_end" BIGINT,
    "running_intermission_duration" BIGINT,
    "is_highlight" BIGINT,
    "puck_x_start" DOUBLE PRECISION,
    "puck_y_start" DOUBLE PRECISION,
    "puck_x_start_adjusted" DOUBLE PRECISION,
    "puck_y_start_adjusted" DOUBLE PRECISION,
    "puck_x_stop" DOUBLE PRECISION,
    "puck_y_stop" DOUBLE PRECISION,
    "puck_x_stop_adjusted" DOUBLE PRECISION,
    "puck_y_stop_adjusted" DOUBLE PRECISION,
    "is_xy_adjusted" DOUBLE PRECISION,
    "needs_xy_adjustment" DOUBLE PRECISION,
    "role_abrev_binary" TEXT,
    "player_role" TEXT,
    "player_name" TEXT,
    "play_detail1" TEXT,
    "play_detail_2" TEXT,
    "play_detail_successful" TEXT,
    "pressured_pressurer" DOUBLE PRECISION,
    "side_of_puck" TEXT,
    "player_x_start" DOUBLE PRECISION,
    "player_y_start" DOUBLE PRECISION,
    "player_x_start_adjusted" DOUBLE PRECISION,
    "player_y_start_adjusted" DOUBLE PRECISION,
    "player_x_stop" DOUBLE PRECISION,
    "player_y_stop" DOUBLE PRECISION,
    "player_x_stop_adjusted" DOUBLE PRECISION,
    "player_y_stop_adjusted" DOUBLE PRECISION,
    "net_x" DOUBLE PRECISION,
    "net_y" DOUBLE PRECISION,
    "team_venue" TEXT,
    "player_team" TEXT,
    "home_team_zone" TEXT,
    "away_team_zone" TEXT,
    "play_detail1_s" TEXT,
    "play_detail2_s" TEXT,
    "is_goal" BIGINT,
    "shift_id" TEXT,
    "position_id" DOUBLE PRECISION,
    "shot_type_id" TEXT,
    "pass_type_id" TEXT,
    "time_bucket_id" TEXT,
    "strength_id" TEXT,
    "player_rating" DOUBLE PRECISION,
    "cycle_key" TEXT,
    "is_cycle" BIGINT,
    "time_to_next_event" DOUBLE PRECISION,
    "time_from_last_event" DOUBLE PRECISION,
    "time_to_next_goal_for" DOUBLE PRECISION,
    "time_to_next_goal_against" DOUBLE PRECISION,
    "time_from_last_goal_for" DOUBLE PRECISION,
    "time_from_last_goal_against" DOUBLE PRECISION,
    "time_to_next_stoppage" DOUBLE PRECISION,
    "time_from_last_stoppage" DOUBLE PRECISION,
    "player_toi" DOUBLE PRECISION,
    "team_on_ice_toi_avg" DOUBLE PRECISION,
    "team_on_ice_toi_min" DOUBLE PRECISION,
    "team_on_ice_toi_max" DOUBLE PRECISION,
    "opp_on_ice_toi_avg" DOUBLE PRECISION,
    "opp_on_ice_toi_min" DOUBLE PRECISION,
    "opp_on_ice_toi_max" DOUBLE PRECISION,
    "event_team_avg_rating" DOUBLE PRECISION,
    "opp_team_avg_rating" DOUBLE PRECISION,
    "rating_vs_opp" DOUBLE PRECISION,
    "assist_type" TEXT,
    "assist_key" TEXT,
    "_export_timestamp" TEXT
);


CREATE TABLE public."fact_breakouts" (
    "event_id" TEXT,
    "game_id" BIGINT,
    "period" BIGINT,
    "period_id" TEXT,
    "event_type" TEXT,
    "event_type_id" TEXT,
    "event_detail" TEXT,
    "event_detail_id" TEXT,
    "event_detail_2" TEXT,
    "event_detail_2_id" TEXT,
    "event_team_zone" TEXT,
    "event_zone_id" TEXT,
    "sequence_key" TEXT,
    "play_key" TEXT,
    "tracking_event_key" TEXT,
    "shift_key" TEXT,
    "linked_event_key" DOUBLE PRECISION,
    "home_team" TEXT,
    "home_team_id" TEXT,
    "away_team" TEXT,
    "away_team_id" TEXT,
    "duration" BIGINT,
    "event_player_ids" TEXT,
    "opp_player_ids" TEXT,
    "event_start_min" DOUBLE PRECISION,
    "event_start_sec" DOUBLE PRECISION,
    "event_end_min" DOUBLE PRECISION,
    "event_end_sec" DOUBLE PRECISION,
    "time_start_total_seconds" BIGINT,
    "time_end_total_seconds" BIGINT,
    "event_running_start" BIGINT,
    "event_running_end" BIGINT,
    "running_video_time" BIGINT,
    "period_start_total_running_seconds" BIGINT,
    "running_intermission_duration" BIGINT,
    "team_venue" TEXT,
    "player_team" TEXT,
    "home_team_zone" TEXT,
    "away_team_zone" TEXT,
    "player_role" TEXT,
    "side_of_puck" TEXT,
    "role_number" BIGINT,
    "role_abrev" TEXT,
    "player_game_number" DOUBLE PRECISION,
    "strength" TEXT,
    "play_detail1" TEXT,
    "play_detail_2" TEXT,
    "pressured_pressurer" DOUBLE PRECISION,
    "puck_x_start" DOUBLE PRECISION,
    "puck_y_start" DOUBLE PRECISION,
    "is_goal" BIGINT,
    "is_highlight" BIGINT,
    "event_player_1_id_x" DOUBLE PRECISION,
    "event_player_1_name_x" DOUBLE PRECISION,
    "event_player_2_id_x" DOUBLE PRECISION,
    "event_player_2_name_x" DOUBLE PRECISION,
    "opp_player_1_id_x" DOUBLE PRECISION,
    "opp_player_1_name_x" DOUBLE PRECISION,
    "event_player_1_id_y" TEXT,
    "event_player_1_name_y" TEXT,
    "event_player_2_id_y" TEXT,
    "event_player_2_name_y" TEXT,
    "opp_player_1_id_y" TEXT,
    "opp_player_1_name_y" TEXT,
    "strength_id" TEXT,
    "shift_id" TEXT,
    "player_name" TEXT,
    "position_id" DOUBLE PRECISION,
    "zone_entry_type_id" DOUBLE PRECISION,
    "zone_exit_type_id" TEXT,
    "time_bucket_id" TEXT,
    "player_rating" DOUBLE PRECISION,
    "cycle_key" DOUBLE PRECISION,
    "is_cycle" BIGINT,
    "is_rebound" BIGINT,
    "is_zone_entry" BIGINT,
    "is_zone_exit" BIGINT,
    "is_controlled_entry" BIGINT,
    "is_carried_entry" BIGINT,
    "is_controlled_exit" BIGINT,
    "is_carried_exit" BIGINT,
    "is_rush" BIGINT,
    "is_save" BIGINT,
    "is_sog" BIGINT,
    "is_turnover" BIGINT,
    "is_giveaway" BIGINT,
    "is_bad_giveaway" BIGINT,
    "is_takeaway" BIGINT,
    "is_faceoff" BIGINT,
    "is_penalty" BIGINT,
    "is_blocked_shot" BIGINT,
    "is_missed_shot" BIGINT,
    "is_deflected" BIGINT,
    "is_tipped" BIGINT,
    "is_corsi" BIGINT,
    "is_fenwick" BIGINT,
    "zone_outcome_id" TEXT,
    "is_scoring_chance" BIGINT,
    "is_high_danger" BIGINT,
    "is_pressured" BIGINT,
    "danger_level" DOUBLE PRECISION,
    "danger_level_id" DOUBLE PRECISION,
    "scoring_chance_key" DOUBLE PRECISION,
    "prev_event_id" TEXT,
    "prev_event_type" TEXT,
    "prev_event_detail" TEXT,
    "prev_event_team" TEXT,
    "prev_event_same_team" BIGINT,
    "next_event_id" TEXT,
    "next_event_type" TEXT,
    "next_event_detail" TEXT,
    "next_event_team" TEXT,
    "next_event_same_team" BIGINT,
    "time_since_prev" DOUBLE PRECISION,
    "time_to_next" DOUBLE PRECISION,
    "time_to_next_sog" DOUBLE PRECISION,
    "time_since_last_sog" DOUBLE PRECISION,
    "events_to_next_sog" DOUBLE PRECISION,
    "events_since_last_sog" DOUBLE PRECISION,
    "next_sog_result" TEXT,
    "led_to_sog" BIGINT,
    "is_pre_shot_event" BIGINT,
    "is_shot_assist" BIGINT,
    "time_to_next_goal" DOUBLE PRECISION,
    "time_since_last_goal" DOUBLE PRECISION,
    "events_to_next_goal" DOUBLE PRECISION,
    "events_since_last_goal" DOUBLE PRECISION,
    "led_to_goal" BIGINT,
    "time_since_zone_entry" DOUBLE PRECISION,
    "events_since_zone_entry" DOUBLE PRECISION,
    "time_since_zone_exit" DOUBLE PRECISION,
    "sequence_event_num" DOUBLE PRECISION,
    "sequence_total_events" DOUBLE PRECISION,
    "sequence_duration" DOUBLE PRECISION,
    "is_sequence_first" BIGINT,
    "is_sequence_last" BIGINT,
    "sequence_has_sog" BIGINT,
    "sequence_has_goal" BIGINT,
    "sequence_shot_count" DOUBLE PRECISION,
    "consecutive_team_events" BIGINT,
    "time_since_possession_change" DOUBLE PRECISION,
    "events_since_possession_change" DOUBLE PRECISION,
    "time_since_faceoff" DOUBLE PRECISION,
    "events_since_faceoff" DOUBLE PRECISION,
    "is_rush_calculated" BIGINT,
    "play_segment_number" DOUBLE PRECISION,
    "sequence_segment_number" DOUBLE PRECISION,
    "linked_event_segment_number" DOUBLE PRECISION,
    "breakout_key" TEXT,
    "breakout_successful" TEXT,
    "time_to_next_event" DOUBLE PRECISION,
    "time_from_last_event" DOUBLE PRECISION,
    "time_to_next_goal_for" DOUBLE PRECISION,
    "time_to_next_goal_against" DOUBLE PRECISION,
    "time_from_last_goal_for" DOUBLE PRECISION,
    "time_from_last_goal_against" DOUBLE PRECISION,
    "time_to_next_stoppage" DOUBLE PRECISION,
    "time_from_last_stoppage" DOUBLE PRECISION,
    "event_player_1_toi" DOUBLE PRECISION,
    "event_player_2_toi" DOUBLE PRECISION,
    "event_player_3_toi" DOUBLE PRECISION,
    "event_player_4_toi" DOUBLE PRECISION,
    "opp_player_1_toi" DOUBLE PRECISION,
    "opp_player_2_toi" DOUBLE PRECISION,
    "team_on_ice_toi_avg" DOUBLE PRECISION,
    "team_on_ice_toi_min" DOUBLE PRECISION,
    "team_on_ice_toi_max" DOUBLE PRECISION,
    "opp_on_ice_toi_avg" DOUBLE PRECISION,
    "opp_on_ice_toi_min" DOUBLE PRECISION,
    "opp_on_ice_toi_max" DOUBLE PRECISION
);


CREATE TABLE public."fact_cycle_events" (
    "cycle_key" TEXT,
    "game_id" BIGINT,
    "team_id" TEXT,
    "team_name" TEXT,
    "home_team_id" TEXT,
    "away_team_id" TEXT,
    "pass_count" BIGINT,
    "event_count" BIGINT,
    "player_count" BIGINT,
    "start_event_id" TEXT,
    "end_event_id" TEXT,
    "start_time" BIGINT,
    "end_time" BIGINT,
    "duration_seconds" BIGINT,
    "ended_with" TEXT,
    "ended_with_shot" BIGINT,
    "ended_with_goal" BIGINT,
    "event_ids" TEXT,
    "player_ids" TEXT,
    "period" BIGINT,
    "period_id" TEXT
);