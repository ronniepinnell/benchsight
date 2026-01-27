-- BenchSight Schema Migration
-- Generated: 2026-01-26 15:21:08.931328
-- ALTER statements: 402
-- CREATE statements: 8

-- ============================================
-- PART 1: ADD MISSING COLUMNS
-- ============================================

ALTER TABLE public."dim_schedule" ADD COLUMN IF NOT EXISTS "away_team_periodOT_goals" BIGINT;
ALTER TABLE public."dim_schedule" ADD COLUMN IF NOT EXISTS "home_team_periodOT_goals" DOUBLE PRECISION;
ALTER TABLE public."dim_schedule" ADD COLUMN IF NOT EXISTS "include" BOOLEAN;
ALTER TABLE public."dim_schedule" ADD COLUMN IF NOT EXISTS "schedule_type" TEXT;
ALTER TABLE public."fact_breakouts" ADD COLUMN IF NOT EXISTS "breakout_successful" TEXT;
ALTER TABLE public."fact_breakouts" ADD COLUMN IF NOT EXISTS "puck_x_start" DOUBLE PRECISION;
ALTER TABLE public."fact_breakouts" ADD COLUMN IF NOT EXISTS "puck_y_start" DOUBLE PRECISION;
ALTER TABLE public."fact_event_chains" ADD COLUMN IF NOT EXISTS "event_2_detail" TEXT;
ALTER TABLE public."fact_event_chains" ADD COLUMN IF NOT EXISTS "event_2_player_id" TEXT;
ALTER TABLE public."fact_event_chains" ADD COLUMN IF NOT EXISTS "event_2_type" TEXT;
ALTER TABLE public."fact_event_chains" ADD COLUMN IF NOT EXISTS "event_3_detail" TEXT;
ALTER TABLE public."fact_event_chains" ADD COLUMN IF NOT EXISTS "event_3_player_id" TEXT;
ALTER TABLE public."fact_event_chains" ADD COLUMN IF NOT EXISTS "event_3_type" TEXT;
ALTER TABLE public."fact_event_chains" ADD COLUMN IF NOT EXISTS "event_4_detail" TEXT;
ALTER TABLE public."fact_event_chains" ADD COLUMN IF NOT EXISTS "event_4_player_id" TEXT;
ALTER TABLE public."fact_event_chains" ADD COLUMN IF NOT EXISTS "event_4_type" TEXT;
ALTER TABLE public."fact_event_chains" ADD COLUMN IF NOT EXISTS "event_5_player_id" TEXT;
ALTER TABLE public."fact_event_chains" ADD COLUMN IF NOT EXISTS "event_5_type" TEXT;
ALTER TABLE public."fact_event_players" ADD COLUMN IF NOT EXISTS "play_detail1_s" TEXT;
ALTER TABLE public."fact_event_players" ADD COLUMN IF NOT EXISTS "play_detail2_s" TEXT;
ALTER TABLE public."fact_faceoffs" ADD COLUMN IF NOT EXISTS "pressured_pressurer" DOUBLE PRECISION;
ALTER TABLE public."fact_faceoffs" ADD COLUMN IF NOT EXISTS "puck_x_start" DOUBLE PRECISION;
ALTER TABLE public."fact_faceoffs" ADD COLUMN IF NOT EXISTS "puck_y_start" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "away_team" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "away_team_zone" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "consecutive_team_events" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "cycle_key" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "danger_level" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "danger_level_id" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "duration" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_detail_2" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_detail_2_id" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_end_min" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_end_sec" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_player_1_id_x" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_player_1_id_y" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_player_1_name_x" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_player_1_name_y" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_player_1_toi" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_player_2_id_x" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_player_2_id_y" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_player_2_name_x" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_player_2_name_y" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_player_2_toi" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_player_ids" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_running_end" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_running_start" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_start_min" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_start_sec" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_successful" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_team_avg_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_team_zone" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_type" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_type_id" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "event_zone_id" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "events_since_faceoff" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "events_since_last_goal" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "events_since_last_sog" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "events_since_possession_change" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "events_since_zone_entry" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "events_to_next_goal" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "events_to_next_sog" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "goalie_name" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "goalie_player_id" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "goalie_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "home_team" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "home_team_zone" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_bad_giveaway" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_blocked_shot" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_carried_entry" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_carried_exit" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_controlled_entry" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_controlled_exit" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_corsi" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_cycle" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_deflected" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_faceoff" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_fenwick" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_giveaway" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_goal" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_high_danger" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_highlight" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_missed_shot" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_penalty" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_pre_shot_event" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_pressured" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_rebound" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_rush" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_rush_calculated" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_save" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_scoring_chance" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_sequence_first" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_sequence_last" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_shot_assist" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_sog" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_takeaway" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_tipped" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_turnover" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_zone_entry" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "is_zone_exit" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "led_to_goal" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "led_to_sog" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "linked_event_key" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "linked_event_segment_number" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "next_event_detail" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "next_event_id" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "next_event_same_team" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "next_event_team" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "next_event_type" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "next_sog_result" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "opp_on_ice_toi_avg" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "opp_on_ice_toi_max" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "opp_on_ice_toi_min" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "opp_player_1_id_x" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "opp_player_1_id_y" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "opp_player_1_name_x" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "opp_player_1_name_y" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "opp_player_1_toi" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "opp_player_2_toi" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "opp_player_ids" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "opp_team_avg_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "period_start_total_running_seconds" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "play_detail1" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "play_detail_successful" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "play_key" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "play_segment_number" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "player_game_number" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "player_name" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "player_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "player_role" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "player_team" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "position_id" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "pressured_pressurer" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "prev_event_detail" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "prev_event_id" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "prev_event_same_team" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "prev_event_team" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "prev_event_type" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "rating_vs_opp" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "role_abrev" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "role_number" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "running_intermission_duration" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "running_video_time" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "scoring_chance_key" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "sequence_duration" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "sequence_event_num" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "sequence_has_goal" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "sequence_has_sog" BIGINT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "sequence_key" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "sequence_segment_number" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "sequence_shot_count" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "sequence_total_events" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "shift_id" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "shift_key" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "shooter_name" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "shooter_player_id" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "shooter_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "side_of_puck" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "team_on_ice_toi_avg" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "team_on_ice_toi_max" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "team_on_ice_toi_min" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "team_venue" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_bucket_id" TEXT;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_from_last_event" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_from_last_goal_against" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_from_last_goal_for" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_from_last_stoppage" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_since_faceoff" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_since_last_goal" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_since_last_sog" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_since_possession_change" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_since_prev" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_since_zone_entry" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_since_zone_exit" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_to_next" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_to_next_event" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_to_next_goal" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_to_next_goal_against" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_to_next_goal_for" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_to_next_sog" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "time_to_next_stoppage" DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS "tracking_event_key" TEXT;
ALTER TABLE public."fact_linked_events" ADD COLUMN IF NOT EXISTS "event_2_detail" TEXT;
ALTER TABLE public."fact_linked_events" ADD COLUMN IF NOT EXISTS "event_2_player_id" TEXT;
ALTER TABLE public."fact_linked_events" ADD COLUMN IF NOT EXISTS "event_2_type" TEXT;
ALTER TABLE public."fact_linked_events" ADD COLUMN IF NOT EXISTS "event_3_detail" TEXT;
ALTER TABLE public."fact_linked_events" ADD COLUMN IF NOT EXISTS "event_3_player_id" TEXT;
ALTER TABLE public."fact_linked_events" ADD COLUMN IF NOT EXISTS "event_3_type" TEXT;
ALTER TABLE public."fact_linked_events" ADD COLUMN IF NOT EXISTS "event_4_detail" TEXT;
ALTER TABLE public."fact_linked_events" ADD COLUMN IF NOT EXISTS "event_4_player_id" TEXT;
ALTER TABLE public."fact_linked_events" ADD COLUMN IF NOT EXISTS "event_4_type" TEXT;
ALTER TABLE public."fact_linked_events" ADD COLUMN IF NOT EXISTS "event_5_player_id" TEXT;
ALTER TABLE public."fact_linked_events" ADD COLUMN IF NOT EXISTS "event_5_type" TEXT;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "backcheck_intensity_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "backcheck_intensity_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "backcheck_intensity_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "controlled_exits_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "controlled_exits_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "controlled_exits_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "forecheck_intensity_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "forecheck_intensity_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "forecheck_intensity_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "micro_def_zone_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "micro_def_zone_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "micro_def_zone_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "micro_neutral_zone_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "micro_neutral_zone_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "micro_neutral_zone_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "micro_off_zone_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "micro_off_zone_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "micro_off_zone_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "play_success_rate_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "play_success_rate_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "play_success_rate_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "plays_successful_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "plays_successful_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "plays_successful_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "plays_unsuccessful_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "plays_unsuccessful_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "plays_unsuccessful_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "puck_battles_lost_total_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "puck_battles_lost_total_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "puck_battles_lost_total_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "puck_battles_total_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "puck_battles_total_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "puck_battles_total_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "transition_quality_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "transition_quality_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_boxscore_all" ADD COLUMN IF NOT EXISTS "transition_quality_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "backcheck_intensity_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "backcheck_intensity_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "backcheck_intensity_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "controlled_exits_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "controlled_exits_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "controlled_exits_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "forecheck_intensity_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "forecheck_intensity_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "forecheck_intensity_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "micro_def_zone_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "micro_def_zone_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "micro_def_zone_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "micro_neutral_zone_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "micro_neutral_zone_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "micro_neutral_zone_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "micro_off_zone_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "micro_off_zone_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "micro_off_zone_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "play_success_rate_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "play_success_rate_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "play_success_rate_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "plays_successful_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "plays_successful_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "plays_successful_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "plays_unsuccessful_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "plays_unsuccessful_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "plays_unsuccessful_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "puck_battles_lost_total_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "puck_battles_lost_total_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "puck_battles_lost_total_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "puck_battles_total_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "puck_battles_total_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "puck_battles_total_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "transition_quality_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "transition_quality_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_game_stats" ADD COLUMN IF NOT EXISTS "transition_quality_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "backcheck_intensity_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "backcheck_intensity_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "backcheck_intensity_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "controlled_exits_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "controlled_exits_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "controlled_exits_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "forecheck_intensity_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "forecheck_intensity_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "forecheck_intensity_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "micro_def_zone_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "micro_def_zone_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "micro_def_zone_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "micro_neutral_zone_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "micro_neutral_zone_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "micro_neutral_zone_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "micro_off_zone_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "micro_off_zone_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "micro_off_zone_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "play_success_rate_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "play_success_rate_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "play_success_rate_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "plays_successful_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "plays_successful_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "plays_successful_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "plays_unsuccessful_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "plays_unsuccessful_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "plays_unsuccessful_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "puck_battles_lost_total_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "puck_battles_lost_total_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "puck_battles_lost_total_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "puck_battles_total_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "puck_battles_total_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "puck_battles_total_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "transition_quality_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "transition_quality_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_position_splits" ADD COLUMN IF NOT EXISTS "transition_quality_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "backcheck_intensity_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "backcheck_intensity_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "backcheck_intensity_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "controlled_exits_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "controlled_exits_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "controlled_exits_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "forecheck_intensity_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "forecheck_intensity_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "forecheck_intensity_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "micro_def_zone_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "micro_def_zone_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "micro_def_zone_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "micro_neutral_zone_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "micro_neutral_zone_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "micro_neutral_zone_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "micro_off_zone_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "micro_off_zone_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "micro_off_zone_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "play_success_rate_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "play_success_rate_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "play_success_rate_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "plays_successful_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "plays_successful_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "plays_successful_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "plays_unsuccessful_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "plays_unsuccessful_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "plays_unsuccessful_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "puck_battles_lost_total_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "puck_battles_lost_total_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "puck_battles_lost_total_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "puck_battles_total_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "puck_battles_total_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "puck_battles_total_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "transition_quality_success_rate" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "transition_quality_successful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_season_stats" ADD COLUMN IF NOT EXISTS "transition_quality_unsuccessful" DOUBLE PRECISION;
ALTER TABLE public."fact_player_xy_long" ADD COLUMN IF NOT EXISTS "angle_to_net" DOUBLE PRECISION;
ALTER TABLE public."fact_player_xy_long" ADD COLUMN IF NOT EXISTS "distance_to_net" DOUBLE PRECISION;
ALTER TABLE public."fact_player_xy_long" ADD COLUMN IF NOT EXISTS "is_event_team" BOOLEAN;
ALTER TABLE public."fact_player_xy_long" ADD COLUMN IF NOT EXISTS "point_number" BIGINT;
ALTER TABLE public."fact_puck_xy_long" ADD COLUMN IF NOT EXISTS "angle_to_net" DOUBLE PRECISION;
ALTER TABLE public."fact_puck_xy_long" ADD COLUMN IF NOT EXISTS "distance_to_net" DOUBLE PRECISION;
ALTER TABLE public."fact_puck_xy_long" ADD COLUMN IF NOT EXISTS "point_number" BIGINT;
ALTER TABLE public."fact_registration" ADD COLUMN IF NOT EXISTS "CAF" TEXT;
ALTER TABLE public."fact_saves" ADD COLUMN IF NOT EXISTS "pressured_pressurer" DOUBLE PRECISION;
ALTER TABLE public."fact_saves" ADD COLUMN IF NOT EXISTS "puck_x_start" DOUBLE PRECISION;
ALTER TABLE public."fact_saves" ADD COLUMN IF NOT EXISTS "puck_y_start" DOUBLE PRECISION;
ALTER TABLE public."fact_scoring_chances" ADD COLUMN IF NOT EXISTS "shot_angle" DOUBLE PRECISION;
ALTER TABLE public."fact_scoring_chances" ADD COLUMN IF NOT EXISTS "shot_distance" DOUBLE PRECISION;
ALTER TABLE public."fact_shift_players" ADD COLUMN IF NOT EXISTS "away_avg_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_shift_players" ADD COLUMN IF NOT EXISTS "away_fo_won" DOUBLE PRECISION;
ALTER TABLE public."fact_shift_players" ADD COLUMN IF NOT EXISTS "away_max_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_shift_players" ADD COLUMN IF NOT EXISTS "away_min_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_shift_players" ADD COLUMN IF NOT EXISTS "home_avg_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_shift_players" ADD COLUMN IF NOT EXISTS "home_fo_won" DOUBLE PRECISION;
ALTER TABLE public."fact_shift_players" ADD COLUMN IF NOT EXISTS "home_max_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_shift_players" ADD COLUMN IF NOT EXISTS "home_min_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_shift_players" ADD COLUMN IF NOT EXISTS "rating_differential" DOUBLE PRECISION;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "away_avg_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "away_defense_1_id" TEXT;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "away_defense_2_id" TEXT;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "away_fo_won" DOUBLE PRECISION;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "away_forward_1_id" TEXT;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "away_forward_2_id" TEXT;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "away_forward_3_id" TEXT;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "away_goalie_id" TEXT;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "away_max_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "away_min_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "away_xtra_id" BIGINT;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "home_avg_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "home_defense_1_id" TEXT;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "home_defense_2_id" TEXT;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "home_fo_won" DOUBLE PRECISION;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "home_forward_1_id" TEXT;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "home_forward_2_id" TEXT;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "home_forward_3_id" TEXT;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "home_goalie_id" TEXT;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "home_max_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "home_min_rating" DOUBLE PRECISION;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "home_xtra_id" BIGINT;
ALTER TABLE public."fact_shifts" ADD COLUMN IF NOT EXISTS "rating_differential" DOUBLE PRECISION;
ALTER TABLE public."fact_shot_danger" ADD COLUMN IF NOT EXISTS "shot_angle" DOUBLE PRECISION;
ALTER TABLE public."fact_shot_danger" ADD COLUMN IF NOT EXISTS "shot_distance" DOUBLE PRECISION;
ALTER TABLE public."fact_special_teams_summary" ADD COLUMN IF NOT EXISTS "games_played" BIGINT;
ALTER TABLE public."fact_special_teams_summary" ADD COLUMN IF NOT EXISTS "team_id" TEXT;
ALTER TABLE public."fact_special_teams_summary" ADD COLUMN IF NOT EXISTS "total_cf_pct" DOUBLE PRECISION;
ALTER TABLE public."fact_special_teams_summary" ADD COLUMN IF NOT EXISTS "total_corsi_against" BIGINT;
ALTER TABLE public."fact_special_teams_summary" ADD COLUMN IF NOT EXISTS "total_corsi_for" BIGINT;
ALTER TABLE public."fact_special_teams_summary" ADD COLUMN IF NOT EXISTS "total_xg_for" DOUBLE PRECISION;
ALTER TABLE public."fact_suspicious_stats" ADD COLUMN IF NOT EXISTS "game_id" BIGINT;
ALTER TABLE public."fact_suspicious_stats" ADD COLUMN IF NOT EXISTS "resolved" BOOLEAN;
ALTER TABLE public."fact_suspicious_stats" ADD COLUMN IF NOT EXISTS "threshold" BIGINT;
ALTER TABLE public."fact_suspicious_stats" ADD COLUMN IF NOT EXISTS "threshold_direction" TEXT;
ALTER TABLE public."fact_turnovers_detailed" ADD COLUMN IF NOT EXISTS "puck_x_start" DOUBLE PRECISION;
ALTER TABLE public."fact_turnovers_detailed" ADD COLUMN IF NOT EXISTS "puck_y_start" DOUBLE PRECISION;
ALTER TABLE public."fact_zone_entries" ADD COLUMN IF NOT EXISTS "entry_successful" TEXT;
ALTER TABLE public."fact_zone_entries" ADD COLUMN IF NOT EXISTS "puck_x_start" DOUBLE PRECISION;
ALTER TABLE public."fact_zone_entries" ADD COLUMN IF NOT EXISTS "puck_y_start" DOUBLE PRECISION;
ALTER TABLE public."fact_zone_exits" ADD COLUMN IF NOT EXISTS "exit_successful" TEXT;
ALTER TABLE public."fact_zone_exits" ADD COLUMN IF NOT EXISTS "puck_x_start" DOUBLE PRECISION;
ALTER TABLE public."fact_zone_exits" ADD COLUMN IF NOT EXISTS "puck_y_start" DOUBLE PRECISION;

-- ============================================
-- PART 2: CREATE MISSING TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS public."fact_assists" (
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
    "position_id" BIGINT,
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

CREATE TABLE IF NOT EXISTS public."fact_goal_assists" (
    "goal_assist_key" TEXT,
    "game_id" BIGINT,
    "goal_event_id" TEXT,
    "goal_event_index" BIGINT,
    "period" BIGINT,
    "time_minutes" BIGINT,
    "time_seconds" BIGINT,
    "time_total_seconds" BIGINT,
    "scorer_player_id" TEXT,
    "scorer_player_name" TEXT,
    "scorer_team_id" TEXT,
    "scorer_team_name" TEXT,
    "primary_assist_player_id" TEXT,
    "primary_assist_player_name" TEXT,
    "primary_assist_event_id" TEXT,
    "secondary_assist_player_id" TEXT,
    "secondary_assist_player_name" TEXT,
    "secondary_assist_event_id" TEXT,
    "strength" TEXT,
    "shot_type" TEXT,
    "assist_count" BIGINT,
    "is_unassisted" BOOLEAN,
    "is_powerplay_goal" BOOLEAN,
    "is_shorthanded_goal" BOOLEAN,
    "is_empty_net" BOOLEAN,
    "is_game_winner" BOOLEAN,
    "home_team_id" TEXT,
    "away_team_id" TEXT,
    "home_team_name" TEXT,
    "away_team_name" TEXT,
    "video_url" TEXT,
    "running_video_time" BIGINT,
    "_export_timestamp" TEXT
);

CREATE TABLE IF NOT EXISTS public."fact_period_momentum" (
    "momentum_key" TEXT,
    "game_id" BIGINT,
    "period" BIGINT,
    "events_count" BIGINT,
    "goals" BIGINT,
    "shots" BIGINT,
    "passes" BIGINT
);

CREATE TABLE IF NOT EXISTS public."fact_player_xy_wide" (
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

CREATE TABLE IF NOT EXISTS public."fact_puck_xy_wide" (
    "puck_xy_key" TEXT,
    "event_id" TEXT,
    "game_id" BIGINT,
    "period" BIGINT,
    "event_type" TEXT,
    "event_detail" TEXT,
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
    "_export_timestamp" TEXT
);

CREATE TABLE IF NOT EXISTS public."fact_shot_event" (
    "shot_event_key" TEXT,
    "event_id" TEXT,
    "game_id" BIGINT,
    "period" BIGINT,
    "event_type" TEXT,
    "event_detail" TEXT,
    "is_goal" BOOLEAN,
    "shooter_player_id" TEXT,
    "shooter_name" TEXT,
    "shot_x" DOUBLE PRECISION,
    "shot_y" DOUBLE PRECISION,
    "shot_distance" DOUBLE PRECISION,
    "shot_angle" DOUBLE PRECISION,
    "friendly_screen_score" DOUBLE PRECISION,
    "own_team_screen_score" DOUBLE PRECISION,
    "total_screen_score" DOUBLE PRECISION,
    "screen_count" BIGINT,
    "is_screened" BOOLEAN,
    "net_target_x" DOUBLE PRECISION,
    "net_target_y" DOUBLE PRECISION,
    "net_location_id" BIGINT,
    "_export_timestamp" TEXT
);

CREATE TABLE IF NOT EXISTS public."fact_shot_players" (
    "shot_player_key" TEXT,
    "event_id" TEXT,
    "game_id" BIGINT,
    "player_id" TEXT,
    "player_name" TEXT,
    "player_role" TEXT,
    "is_shooter_team" BOOLEAN,
    "is_shooter" BOOLEAN,
    "player_x" DOUBLE PRECISION,
    "player_y" DOUBLE PRECISION,
    "is_in_vision_cone" BOOLEAN,
    "is_in_puck_path" BOOLEAN,
    "screen_score" DOUBLE PRECISION,
    "is_screening" BOOLEAN,
    "screen_type" TEXT,
    "_export_timestamp" TEXT
);

CREATE TABLE IF NOT EXISTS public."fact_shots" (
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
    "event_successful" TEXT,
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
    "play_detail_successful" TEXT,
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
    "position_id" BIGINT,
    "shot_type_id" TEXT,
    "time_bucket_id" TEXT,
    "player_rating" DOUBLE PRECISION,
    "cycle_key" TEXT,
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
    "shooter_player_id" TEXT,
    "shooter_name" TEXT,
    "shooter_rating" DOUBLE PRECISION,
    "shot_blocker_player_id" TEXT,
    "shot_blocker_name" TEXT,
    "shot_blocker_rating" DOUBLE PRECISION,
    "goalie_player_id" TEXT,
    "goalie_name" TEXT,
    "goalie_rating" DOUBLE PRECISION,
    "is_missed_shot" BIGINT,
    "is_deflected" BIGINT,
    "is_tipped" BIGINT,
    "is_corsi" BIGINT,
    "is_fenwick" BIGINT,
    "shot_outcome_id" TEXT,
    "is_scoring_chance" BIGINT,
    "is_high_danger" BIGINT,
    "is_pressured" BIGINT,
    "danger_level" TEXT,
    "danger_level_id" TEXT,
    "scoring_chance_key" TEXT,
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
    "time_to_next_event" DOUBLE PRECISION,
    "time_from_last_event" DOUBLE PRECISION,
    "time_to_next_goal_for" DOUBLE PRECISION,
    "time_to_next_goal_against" DOUBLE PRECISION,
    "time_from_last_goal_for" DOUBLE PRECISION,
    "time_from_last_goal_against" DOUBLE PRECISION,
    "time_to_next_stoppage" DOUBLE PRECISION,
    "time_from_last_stoppage" DOUBLE PRECISION,
    "event_player_1_toi" DOUBLE PRECISION,
    "opp_player_1_toi" DOUBLE PRECISION,
    "event_player_2_toi" DOUBLE PRECISION,
    "opp_player_2_toi" DOUBLE PRECISION,
    "event_player_3_toi" DOUBLE PRECISION,
    "opp_player_3_toi" DOUBLE PRECISION,
    "event_player_4_toi" DOUBLE PRECISION,
    "opp_player_4_toi" DOUBLE PRECISION,
    "team_on_ice_toi_avg" DOUBLE PRECISION,
    "team_on_ice_toi_min" DOUBLE PRECISION,
    "team_on_ice_toi_max" DOUBLE PRECISION,
    "opp_on_ice_toi_avg" DOUBLE PRECISION,
    "opp_on_ice_toi_min" DOUBLE PRECISION,
    "opp_on_ice_toi_max" DOUBLE PRECISION,
    "event_team_avg_rating" DOUBLE PRECISION,
    "opp_team_avg_rating" DOUBLE PRECISION,
    "rating_vs_opp" DOUBLE PRECISION,
    "shot_key" TEXT,
    "_export_timestamp" TEXT
);

