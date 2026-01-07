-- BenchSight Supabase Schema
-- Generated: 2026-01-07 18:57
-- Tables: 59
--
-- To apply:
--   1. Go to Supabase SQL Editor
--   2. Paste this entire file
--   3. Run

-- ============================================================
-- DROP EXISTING TABLES (for clean rebuild)
-- ============================================================
-- Uncomment the following line to drop all tables first:
-- DROP SCHEMA public CASCADE; CREATE SCHEMA public;


-- ============================================================
-- DIMENSION TABLES (33)
-- ============================================================

CREATE TABLE IF NOT EXISTS "dim_assist_type" (
    "assist_type_id" TEXT,
    "assist_type_code" VARCHAR(100),
    "assist_type_name" VARCHAR(100),
    "points_value" INTEGER,
    "description" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_danger_level" (
    "danger_level_id" TEXT,
    "danger_level_code" VARCHAR(100),
    "danger_level_name" VARCHAR(100),
    "xg_multiplier" DECIMAL(12,4)
);

-- Lookup table for event subtypes
CREATE TABLE IF NOT EXISTS "dim_event_detail" (
    "event_detail_id" TEXT,
    "event_detail_code" VARCHAR(100),
    "event_detail_name" VARCHAR(100),
    "event_type" VARCHAR(100),
    "category" VARCHAR(100),
    "is_shot_on_goal" BOOLEAN,
    "is_goal" BOOLEAN,
    "is_miss" BOOLEAN,
    "is_block" BOOLEAN,
    "danger_potential" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_dim_event_detail_event_type ON "dim_event_detail" ("event_type");

CREATE TABLE IF NOT EXISTS "dim_event_detail_2" (
    "event_detail_2_id" TEXT,
    "event_detail_2_code" VARCHAR(100),
    "event_detail_2_name" VARCHAR(100),
    "category" VARCHAR(100)
);

-- Lookup table for event types
CREATE TABLE IF NOT EXISTS "dim_event_type" (
    "event_type_id" TEXT,
    "event_type_code" VARCHAR(100),
    "event_type_name" VARCHAR(100),
    "event_category" VARCHAR(100),
    "description" VARCHAR(100),
    "is_corsi" BOOLEAN,
    "is_fenwick" BOOLEAN
);

CREATE TABLE IF NOT EXISTS "dim_game_state" (
    "game_state_id" TEXT,
    "game_state_code" VARCHAR(100),
    "game_state_name" VARCHAR(100),
    "goal_diff_min" INTEGER,
    "goal_diff_max" INTEGER,
    "description" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_giveaway_type" (
    "giveaway_type_id" TEXT,
    "giveaway_type_code" VARCHAR(100),
    "giveaway_type_name" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_league" (
    "league_id" TEXT,
    "league" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_pass_type" (
    "pass_type_id" TEXT,
    "pass_type_code" VARCHAR(100),
    "pass_type_name" VARCHAR(100),
    "description" VARCHAR(100)
);

-- Game periods
CREATE TABLE IF NOT EXISTS "dim_period" (
    "period_id" TEXT,
    "period_number" INTEGER,
    "period_name" VARCHAR(100),
    "period_type" VARCHAR(100),
    "period_minutes" INTEGER
);

CREATE TABLE IF NOT EXISTS "dim_play_detail" (
    "play_detail_id" TEXT,
    "play_detail_code" VARCHAR(100),
    "play_detail_name" VARCHAR(100),
    "play_category" VARCHAR(100),
    "skill_level" VARCHAR(100),
    "description" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_play_detail_2" (
    "play_detail_2_id" TEXT,
    "play_detail_2_code" VARCHAR(100),
    "play_detail_2_name" VARCHAR(100),
    "play_category" VARCHAR(100),
    "skill_level" VARCHAR(100),
    "description" VARCHAR(100)
);

-- Player master data - names, positions, profile info
CREATE TABLE IF NOT EXISTS "dim_player" (
    "player_first_name" VARCHAR(100),
    "player_last_name" VARCHAR(100),
    "player_full_name" VARCHAR(100),
    "player_id" TEXT,
    "player_primary_position" VARCHAR(100),
    "current_skill_rating" INTEGER,
    "player_hand" INTEGER,
    "birth_year" INTEGER,
    "player_gender" VARCHAR(100),
    "highest_beer_league" VARCHAR(500),
    "player_rating_ly" INTEGER,
    "player_notes" INTEGER,
    "player_leadership" VARCHAR(100),
    "player_norad" VARCHAR(100),
    "player_csaha" INTEGER,
    "player_norad_primary_number" INTEGER,
    "player_csah_primary_number" INTEGER,
    "player_norad_current_team" VARCHAR(100),
    "player_csah_current_team" INTEGER,
    "player_norad_current_team_id" TEXT,
    "player_csah_current_team_id" BIGINT,
    "other_url" VARCHAR(500),
    "player_url" VARCHAR(500),
    "player_image" VARCHAR(500),
    "random_player_first_name" VARCHAR(100),
    "random_player_last_name" VARCHAR(100),
    "random_player_full_name" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_dim_player_player_id ON "dim_player" ("player_id");

CREATE TABLE IF NOT EXISTS "dim_player_role" (
    "role_id" TEXT,
    "role_code" VARCHAR(100),
    "role_name" VARCHAR(100),
    "role_type" VARCHAR(100),
    "sort_order" INTEGER
);

CREATE TABLE IF NOT EXISTS "dim_playerurlref" (
    "n_player_url" VARCHAR(100),
    "player_full_name" VARCHAR(100),
    "n_player_id_2" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_position" (
    "position_id" TEXT,
    "position_code" VARCHAR(100),
    "position_name" VARCHAR(100),
    "position_type" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_randomnames" (
    "random_full_name" VARCHAR(100),
    "random_first_name" VARCHAR(100),
    "random_last_name" VARCHAR(100),
    "gender" VARCHAR(100),
    "name_used" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_schedule" (
    "game_id" BIGINT,
    "season" INTEGER,
    "season_id" TEXT,
    "game_url" VARCHAR(500),
    "home_team_game_id" TEXT,
    "away_team_game_id" TEXT,
    "date" VARCHAR(100),
    "game_time" VARCHAR(100),
    "home_team_name" VARCHAR(100),
    "away_team_name" VARCHAR(100),
    "home_team_id" TEXT,
    "away_team_id" TEXT,
    "head_to_head_id" TEXT,
    "game_type" VARCHAR(100),
    "playoff_round" VARCHAR(100),
    "last_period_type" VARCHAR(100),
    "period_length" VARCHAR(100),
    "ot_period_length" VARCHAR(100),
    "shootout_rounds" INTEGER,
    "home_total_goals" INTEGER,
    "away_total_goals" INTEGER,
    "home_team_period1_goals" INTEGER,
    "home_team_period2_goals" INTEGER,
    "home_team_period3_goals" INTEGER,
    "home_team_periodOT_goals" INTEGER,
    "away_team_period1_goals" INTEGER,
    "away_team_period2_goals" INTEGER,
    "away_team_period3_goals" INTEGER,
    "away_team_periodOT_goals" INTEGER,
    "home_team_seeding" INTEGER,
    "away_team_seeding" INTEGER,
    "home_team_w" INTEGER,
    "home_team_l" INTEGER,
    "home_team_t" INTEGER,
    "home_team_pts" INTEGER,
    "away_team_w" INTEGER,
    "away_team_l" INTEGER,
    "away_team_t" INTEGER,
    "away_team_pts" INTEGER,
    "video_id" BIGINT,
    "video_start_time" INTEGER,
    "video_end_time" INTEGER,
    "video_title" INTEGER,
    "video_url" INTEGER
);

CREATE INDEX IF NOT EXISTS idx_dim_schedule_game_id ON "dim_schedule" ("game_id");

CREATE TABLE IF NOT EXISTS "dim_season" (
    "season_id" TEXT,
    "season" INTEGER,
    "session" VARCHAR(100),
    "norad" VARCHAR(100),
    "csah" VARCHAR(100),
    "league_id" TEXT,
    "league" VARCHAR(100),
    "start_date" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_shift_quality_tier" (
    "tier_id" TEXT,
    "tier_code" VARCHAR(100),
    "tier_name" VARCHAR(100),
    "score_min" INTEGER,
    "score_max" INTEGER,
    "description" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_shift_start_type" (
    "shift_start_type_id" TEXT,
    "shift_start_type_name" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_shift_stop_type" (
    "shift_stop_type_id" TEXT,
    "shift_stop_type_name" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_shot_type" (
    "shot_type_id" TEXT,
    "shot_type_code" VARCHAR(100),
    "shot_type_name" VARCHAR(100),
    "description" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_situation" (
    "situation_id" TEXT,
    "situation_name" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_stoppage_type" (
    "stoppage_type_id" TEXT,
    "stoppage_type_code" VARCHAR(100),
    "stoppage_type_name" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_success" (
    "success_id" TEXT,
    "success_code" VARCHAR(100),
    "success_name" VARCHAR(100),
    "is_successful" BOOLEAN
);

CREATE TABLE IF NOT EXISTS "dim_takeaway_type" (
    "takeaway_type_id" TEXT,
    "takeaway_type_code" VARCHAR(100),
    "takeaway_type_name" VARCHAR(100)
);

-- Team master data
CREATE TABLE IF NOT EXISTS "dim_team" (
    "team_name" VARCHAR(100),
    "team_id" TEXT,
    "norad_team" VARCHAR(100),
    "csah_team" VARCHAR(100),
    "league_id" TEXT,
    "league" VARCHAR(100),
    "long_team_name" VARCHAR(100),
    "team_cd" VARCHAR(100),
    "team_color1" VARCHAR(100),
    "team_color2" VARCHAR(100),
    "team_color3" VARCHAR(100),
    "team_color4" VARCHAR(100),
    "team_logo" TEXT,
    "team_url" VARCHAR(500)
);

CREATE INDEX IF NOT EXISTS idx_dim_team_team_id ON "dim_team" ("team_id");

CREATE TABLE IF NOT EXISTS "dim_time_bucket" (
    "time_bucket_id" TEXT,
    "time_bucket_code" VARCHAR(100),
    "time_bucket_name" VARCHAR(100),
    "minute_start" INTEGER,
    "minute_end" INTEGER,
    "description" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_venue" (
    "venue_id" TEXT,
    "venue_code" VARCHAR(100),
    "venue_name" VARCHAR(100),
    "venue_abbrev" VARCHAR(100)
);

-- Ice zones
CREATE TABLE IF NOT EXISTS "dim_zone" (
    "zone_id" TEXT,
    "zone_code" VARCHAR(100),
    "zone_name" VARCHAR(100),
    "zone_abbrev" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_zone_entry_type" (
    "zone_entry_type_id" TEXT,
    "zone_entry_type_code" VARCHAR(100),
    "zone_entry_type_name" VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "dim_zone_exit_type" (
    "zone_exit_type_id" TEXT,
    "zone_exit_type_code" VARCHAR(100),
    "zone_exit_type_name" VARCHAR(100)
);


-- ============================================================
-- FACT TABLES (24)
-- ============================================================

CREATE TABLE IF NOT EXISTS "fact_breakouts" (
    "event_id" TEXT,
    "game_id" BIGINT,
    "period" INTEGER,
    "period_id" TEXT,
    "event_type" VARCHAR(100),
    "event_type_id" TEXT,
    "event_detail" VARCHAR(100),
    "event_detail_id" BIGINT,
    "event_detail_2" VARCHAR(100),
    "event_detail_2_id" TEXT,
    "event_successful" VARCHAR(100),
    "success_id" TEXT,
    "event_team_zone" VARCHAR(100),
    "event_zone_id" TEXT,
    "sequence_key" VARCHAR(100),
    "play_key" VARCHAR(100),
    "event_chain_key" VARCHAR(100),
    "tracking_event_key" VARCHAR(100),
    "shift_key" VARCHAR(100),
    "linked_event_key" VARCHAR(100),
    "home_team" VARCHAR(100),
    "home_team_id" TEXT,
    "away_team" VARCHAR(100),
    "away_team_id" TEXT,
    "duration" INTEGER,
    "event_player_ids" VARCHAR(100),
    "opp_player_ids" VARCHAR(100),
    "player_name" VARCHAR(100),
    "season_id" TEXT,
    "position_id" BIGINT,
    "shot_type_id" BIGINT,
    "zone_entry_type_id" TEXT,
    "zone_exit_type_id" TEXT,
    "stoppage_type_id" BIGINT,
    "giveaway_type_id" TEXT,
    "takeaway_type_id" BIGINT,
    "turnover_type_id" TEXT,
    "pass_type_id" BIGINT,
    "time_bucket_id" TEXT,
    "strength_id" TEXT,
    "cycle_key" INTEGER,
    "is_cycle" BOOLEAN,
    "event_start_min" INTEGER,
    "event_start_sec" INTEGER,
    "event_end_min" INTEGER,
    "event_end_sec" INTEGER,
    "running_video_time" INTEGER,
    "event_running_start" INTEGER,
    "event_running_end" INTEGER,
    "play_detail1" VARCHAR(100),
    "is_rush" BOOLEAN,
    "is_rebound" BOOLEAN,
    "is_breakout" BOOLEAN,
    "is_zone_entry" BOOLEAN,
    "is_zone_exit" BOOLEAN,
    "is_shot" BOOLEAN,
    "is_goal" BOOLEAN,
    "is_save" BOOLEAN,
    "is_turnover" BOOLEAN,
    "is_giveaway" BOOLEAN,
    "is_takeaway" BOOLEAN,
    "is_faceoff" BOOLEAN,
    "is_penalty" BOOLEAN,
    "is_blocked_shot" BOOLEAN,
    "is_missed_shot" BOOLEAN,
    "is_deflected" BOOLEAN,
    "is_sog" BOOLEAN,
    "shot_outcome_id" BIGINT,
    "pass_outcome_id" BIGINT,
    "save_outcome_id" BIGINT,
    "zone_outcome_id" TEXT,
    "is_scoring_chance" BOOLEAN,
    "is_high_danger" BOOLEAN,
    "pressured_pressurer" INTEGER,
    "is_pressured" BOOLEAN,
    "danger_level" INTEGER,
    "danger_level_id" BIGINT,
    "scoring_chance_key" INTEGER,
    "breakout_key" VARCHAR(100),
    "breakout_successful" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_fact_breakouts_game_id ON "fact_breakouts" ("game_id");
CREATE INDEX IF NOT EXISTS idx_fact_breakouts_event_type ON "fact_breakouts" ("event_type");

CREATE TABLE IF NOT EXISTS "fact_cycle_events" (
    "cycle_key" VARCHAR(100),
    "game_id" BIGINT,
    "season_id" TEXT,
    "team_id" TEXT,
    "team_name" VARCHAR(100),
    "home_team_id" TEXT,
    "away_team_id" TEXT,
    "pass_count" INTEGER,
    "event_count" INTEGER,
    "player_count" INTEGER,
    "start_event_id" TEXT,
    "end_event_id" TEXT,
    "start_time" INTEGER,
    "end_time" INTEGER,
    "duration_seconds" INTEGER,
    "ended_with" VARCHAR(100),
    "ended_with_shot" INTEGER,
    "ended_with_goal" INTEGER,
    "event_ids" VARCHAR(500),
    "player_ids" VARCHAR(100),
    "period" INTEGER,
    "period_id" TEXT
);

CREATE INDEX IF NOT EXISTS idx_fact_cycle_events_game_id ON "fact_cycle_events" ("game_id");
CREATE INDEX IF NOT EXISTS idx_fact_cycle_events_team_id ON "fact_cycle_events" ("team_id");

CREATE TABLE IF NOT EXISTS "fact_draft" (
    "team_id" TEXT,
    "skill_rating" INTEGER,
    "round" INTEGER,
    "player_full_name" VARCHAR(100),
    "player_id" TEXT,
    "team_name" VARCHAR(100),
    "restricted" BOOLEAN,
    "overall_draft_round" INTEGER,
    "overall_draft_position" INTEGER,
    "unrestricted_draft_position" INTEGER,
    "season" INTEGER,
    "season_id" TEXT,
    "league" VARCHAR(100),
    "player_draft_id" TEXT
);

CREATE INDEX IF NOT EXISTS idx_fact_draft_player_id ON "fact_draft" ("player_id");
CREATE INDEX IF NOT EXISTS idx_fact_draft_team_id ON "fact_draft" ("team_id");

-- Bridge table linking events to players with their roles
CREATE TABLE IF NOT EXISTS "fact_event_players" (
    "event_id" TEXT,
    "game_id" BIGINT,
    "player_id" TEXT,
    "player_game_number" INTEGER,
    "sequence_key" VARCHAR(100),
    "play_key" VARCHAR(100),
    "shift_key" VARCHAR(100),
    "linked_event_key" VARCHAR(100),
    "event_chain_key" VARCHAR(100),
    "tracking_event_key" VARCHAR(100),
    "zone_change_key" VARCHAR(100),
    "period_id" TEXT,
    "home_team_id" TEXT,
    "away_team_id" TEXT,
    "player_team_id" TEXT,
    "period" INTEGER,
    "event_start_min" INTEGER,
    "event_start_sec" INTEGER,
    "event_end_min" INTEGER,
    "event_end_sec" INTEGER,
    "event_team_zone" VARCHAR(100),
    "home_team_zone" VARCHAR(100),
    "away_team_zone" VARCHAR(100),
    "team_venue" VARCHAR(100),
    "side_of_puck" VARCHAR(100),
    "play_detail1" VARCHAR(100),
    "play_detail_2" VARCHAR(100),
    "play_detail_successful" VARCHAR(100),
    "pressured_pressurer" INTEGER,
    "home_team" VARCHAR(100),
    "away_team" VARCHAR(100),
    "event_type" VARCHAR(100),
    "event_detail" VARCHAR(100),
    "event_detail_2" VARCHAR(100),
    "event_successful" VARCHAR(100),
    "duration" INTEGER,
    "time_start_total_seconds" INTEGER,
    "time_end_total_seconds" INTEGER,
    "running_intermission_duration" INTEGER,
    "period_start_total_running_seconds" INTEGER,
    "running_video_time" INTEGER,
    "event_running_start" INTEGER,
    "event_running_end" INTEGER,
    "player_role" VARCHAR(100),
    "player_team" VARCHAR(100),
    "is_goal" BOOLEAN,
    "player_name" VARCHAR(100),
    "season_id" TEXT,
    "position_id" BIGINT,
    "shot_type_id" BIGINT,
    "zone_entry_type_id" TEXT,
    "zone_exit_type_id" TEXT,
    "stoppage_type_id" TEXT,
    "giveaway_type_id" TEXT,
    "takeaway_type_id" TEXT,
    "turnover_type_id" TEXT,
    "pass_type_id" BIGINT,
    "time_bucket_id" TEXT,
    "strength_id" TEXT,
    "cycle_key" VARCHAR(100),
    "is_cycle" BOOLEAN
);

CREATE INDEX IF NOT EXISTS idx_fact_event_players_game_id ON "fact_event_players" ("game_id");
CREATE INDEX IF NOT EXISTS idx_fact_event_players_player_id ON "fact_event_players" ("player_id");
CREATE INDEX IF NOT EXISTS idx_fact_event_players_event_type ON "fact_event_players" ("event_type");

-- Core event table - every tracked event from game video
CREATE TABLE IF NOT EXISTS "fact_events" (
    "event_id" TEXT,
    "game_id" BIGINT,
    "period" INTEGER,
    "period_id" TEXT,
    "event_type" VARCHAR(100),
    "event_type_id" TEXT,
    "event_detail" VARCHAR(100),
    "event_detail_id" TEXT,
    "event_detail_2" VARCHAR(100),
    "event_detail_2_id" TEXT,
    "event_successful" VARCHAR(100),
    "success_id" TEXT,
    "event_team_zone" VARCHAR(100),
    "event_zone_id" TEXT,
    "sequence_key" VARCHAR(100),
    "play_key" VARCHAR(100),
    "event_chain_key" VARCHAR(100),
    "tracking_event_key" VARCHAR(100),
    "shift_key" VARCHAR(100),
    "linked_event_key" VARCHAR(100),
    "home_team" VARCHAR(100),
    "home_team_id" TEXT,
    "away_team" VARCHAR(100),
    "away_team_id" TEXT,
    "duration" INTEGER,
    "event_player_ids" VARCHAR(100),
    "opp_player_ids" VARCHAR(100),
    "player_name" VARCHAR(100),
    "season_id" TEXT,
    "position_id" BIGINT,
    "shot_type_id" BIGINT,
    "zone_entry_type_id" TEXT,
    "zone_exit_type_id" TEXT,
    "stoppage_type_id" TEXT,
    "giveaway_type_id" TEXT,
    "takeaway_type_id" TEXT,
    "turnover_type_id" TEXT,
    "pass_type_id" BIGINT,
    "time_bucket_id" TEXT,
    "strength_id" TEXT,
    "cycle_key" VARCHAR(100),
    "is_cycle" BOOLEAN,
    "event_start_min" INTEGER,
    "event_start_sec" INTEGER,
    "event_end_min" INTEGER,
    "event_end_sec" INTEGER,
    "running_video_time" INTEGER,
    "event_running_start" INTEGER,
    "event_running_end" INTEGER,
    "play_detail1" VARCHAR(100),
    "is_rush" BOOLEAN,
    "is_rebound" BOOLEAN,
    "is_breakout" BOOLEAN,
    "is_zone_entry" BOOLEAN,
    "is_zone_exit" BOOLEAN,
    "is_shot" BOOLEAN,
    "is_goal" BOOLEAN,
    "is_save" BOOLEAN,
    "is_turnover" BOOLEAN,
    "is_giveaway" BOOLEAN,
    "is_takeaway" BOOLEAN,
    "is_faceoff" BOOLEAN,
    "is_penalty" BOOLEAN,
    "is_blocked_shot" BOOLEAN,
    "is_missed_shot" BOOLEAN,
    "is_deflected" BOOLEAN,
    "is_sog" BOOLEAN,
    "shot_outcome_id" TEXT,
    "pass_outcome_id" TEXT,
    "save_outcome_id" TEXT,
    "zone_outcome_id" TEXT,
    "is_scoring_chance" BOOLEAN,
    "is_high_danger" BOOLEAN,
    "pressured_pressurer" INTEGER,
    "is_pressured" BOOLEAN,
    "danger_level" VARCHAR(100),
    "danger_level_id" TEXT,
    "scoring_chance_key" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_fact_events_game_id ON "fact_events" ("game_id");
CREATE INDEX IF NOT EXISTS idx_fact_events_event_type ON "fact_events" ("event_type");

-- Faceoff events with win/loss tracking
CREATE TABLE IF NOT EXISTS "fact_faceoffs" (
    "event_id" TEXT,
    "game_id" BIGINT,
    "period" INTEGER,
    "period_id" TEXT,
    "event_type" VARCHAR(100),
    "event_type_id" TEXT,
    "event_detail" VARCHAR(100),
    "event_detail_id" BIGINT,
    "event_detail_2" VARCHAR(100),
    "event_detail_2_id" TEXT,
    "event_successful" INTEGER,
    "success_id" BIGINT,
    "event_team_zone" VARCHAR(100),
    "event_zone_id" TEXT,
    "sequence_key" VARCHAR(100),
    "play_key" VARCHAR(100),
    "event_chain_key" VARCHAR(100),
    "tracking_event_key" VARCHAR(100),
    "shift_key" VARCHAR(100),
    "linked_event_key" VARCHAR(100),
    "home_team" VARCHAR(100),
    "home_team_id" TEXT,
    "away_team" VARCHAR(100),
    "away_team_id" TEXT,
    "duration" INTEGER,
    "event_player_ids" VARCHAR(100),
    "opp_player_ids" VARCHAR(100),
    "player_name" VARCHAR(100),
    "season_id" TEXT,
    "position_id" BIGINT,
    "shot_type_id" BIGINT,
    "zone_entry_type_id" BIGINT,
    "zone_exit_type_id" TEXT,
    "stoppage_type_id" BIGINT,
    "giveaway_type_id" BIGINT,
    "takeaway_type_id" BIGINT,
    "turnover_type_id" BIGINT,
    "pass_type_id" BIGINT,
    "time_bucket_id" TEXT,
    "strength_id" TEXT,
    "cycle_key" INTEGER,
    "is_cycle" BOOLEAN,
    "event_start_min" INTEGER,
    "event_start_sec" INTEGER,
    "event_end_min" INTEGER,
    "event_end_sec" INTEGER,
    "running_video_time" INTEGER,
    "event_running_start" INTEGER,
    "event_running_end" INTEGER,
    "play_detail1" INTEGER,
    "is_rush" BOOLEAN,
    "is_rebound" BOOLEAN,
    "is_breakout" BOOLEAN,
    "is_zone_entry" BOOLEAN,
    "is_zone_exit" BOOLEAN,
    "is_shot" BOOLEAN,
    "is_goal" BOOLEAN,
    "is_save" BOOLEAN,
    "is_turnover" BOOLEAN,
    "is_giveaway" BOOLEAN,
    "is_takeaway" BOOLEAN,
    "is_faceoff" BOOLEAN,
    "is_penalty" BOOLEAN,
    "is_blocked_shot" BOOLEAN,
    "is_missed_shot" BOOLEAN,
    "is_deflected" BOOLEAN,
    "is_sog" BOOLEAN,
    "shot_outcome_id" BIGINT,
    "pass_outcome_id" BIGINT,
    "save_outcome_id" BIGINT,
    "zone_outcome_id" BIGINT,
    "is_scoring_chance" BOOLEAN,
    "is_high_danger" BOOLEAN,
    "pressured_pressurer" INTEGER,
    "is_pressured" BOOLEAN,
    "danger_level" INTEGER,
    "danger_level_id" BIGINT,
    "scoring_chance_key" INTEGER,
    "faceoff_key" VARCHAR(100),
    "faceoff_type" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_fact_faceoffs_game_id ON "fact_faceoffs" ("game_id");
CREATE INDEX IF NOT EXISTS idx_fact_faceoffs_event_type ON "fact_faceoffs" ("event_type");

-- Players who appeared in each game with their jersey/position
CREATE TABLE IF NOT EXISTS "fact_gameroster" (
    "game_id" BIGINT,
    "player_id" TEXT,
    "team_id" TEXT,
    "opp_team_id" TEXT,
    "season_id" TEXT,
    "venue_id" TEXT,
    "position_id" TEXT,
    "team_name" VARCHAR(100),
    "opp_team_name" VARCHAR(100),
    "team_venue" VARCHAR(100),
    "date" VARCHAR(100),
    "season" INTEGER,
    "player_full_name" VARCHAR(100),
    "player_game_number" VARCHAR(100),
    "player_position" VARCHAR(100),
    "goals" INTEGER,
    "assist" INTEGER,
    "points" INTEGER,
    "goals_against" INTEGER,
    "pim" INTEGER,
    "shutouts" INTEGER,
    "games_played" INTEGER,
    "sub" VARCHAR(100),
    "current_team" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_fact_gameroster_game_id ON "fact_gameroster" ("game_id");
CREATE INDEX IF NOT EXISTS idx_fact_gameroster_player_id ON "fact_gameroster" ("player_id");
CREATE INDEX IF NOT EXISTS idx_fact_gameroster_team_id ON "fact_gameroster" ("team_id");

CREATE TABLE IF NOT EXISTS "fact_high_danger_chances" (
    "event_id" TEXT,
    "game_id" BIGINT,
    "period" INTEGER,
    "period_id" TEXT,
    "event_type" VARCHAR(100),
    "event_type_id" TEXT,
    "event_detail" VARCHAR(100),
    "event_detail_id" TEXT,
    "event_detail_2" VARCHAR(100),
    "event_detail_2_id" TEXT,
    "event_successful" VARCHAR(100),
    "success_id" TEXT,
    "event_team_zone" VARCHAR(100),
    "event_zone_id" TEXT,
    "sequence_key" VARCHAR(100),
    "play_key" VARCHAR(100),
    "event_chain_key" VARCHAR(100),
    "tracking_event_key" VARCHAR(100),
    "shift_key" VARCHAR(100),
    "linked_event_key" VARCHAR(100),
    "home_team" VARCHAR(100),
    "home_team_id" TEXT,
    "away_team" VARCHAR(100),
    "away_team_id" TEXT,
    "duration" INTEGER,
    "event_player_ids" VARCHAR(100),
    "opp_player_ids" VARCHAR(100),
    "player_name" VARCHAR(100),
    "season_id" TEXT,
    "position_id" BIGINT,
    "shot_type_id" BIGINT,
    "zone_entry_type_id" BIGINT,
    "zone_exit_type_id" BIGINT,
    "stoppage_type_id" BIGINT,
    "giveaway_type_id" BIGINT,
    "takeaway_type_id" BIGINT,
    "turnover_type_id" BIGINT,
    "pass_type_id" BIGINT,
    "time_bucket_id" TEXT,
    "strength_id" TEXT,
    "cycle_key" VARCHAR(100),
    "is_cycle" BOOLEAN,
    "event_start_min" INTEGER,
    "event_start_sec" INTEGER,
    "event_end_min" INTEGER,
    "event_end_sec" INTEGER,
    "running_video_time" INTEGER,
    "event_running_start" INTEGER,
    "event_running_end" INTEGER,
    "play_detail1" VARCHAR(100),
    "is_rush" BOOLEAN,
    "is_rebound" BOOLEAN,
    "is_breakout" BOOLEAN,
    "is_zone_entry" BOOLEAN,
    "is_zone_exit" BOOLEAN,
    "is_shot" BOOLEAN,
    "is_goal" BOOLEAN,
    "is_save" BOOLEAN,
    "is_turnover" BOOLEAN,
    "is_giveaway" BOOLEAN,
    "is_takeaway" BOOLEAN,
    "is_faceoff" BOOLEAN,
    "is_penalty" BOOLEAN,
    "is_blocked_shot" BOOLEAN,
    "is_missed_shot" BOOLEAN,
    "is_deflected" BOOLEAN,
    "is_sog" BOOLEAN,
    "shot_outcome_id" TEXT,
    "pass_outcome_id" BIGINT,
    "save_outcome_id" BIGINT,
    "zone_outcome_id" BIGINT,
    "is_scoring_chance" BOOLEAN,
    "is_high_danger" BOOLEAN,
    "pressured_pressurer" INTEGER,
    "is_pressured" BOOLEAN,
    "danger_level" VARCHAR(100),
    "danger_level_id" TEXT,
    "scoring_chance_key" VARCHAR(100),
    "high_danger_key" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_fact_high_danger_chances_game_id ON "fact_high_danger_chances" ("game_id");
CREATE INDEX IF NOT EXISTS idx_fact_high_danger_chances_event_type ON "fact_high_danger_chances" ("event_type");

CREATE TABLE IF NOT EXISTS "fact_leadership" (
    "player_full_name" VARCHAR(100),
    "player_id" TEXT,
    "leadership" VARCHAR(100),
    "skill_rating" INTEGER,
    "n_player_url" VARCHAR(100),
    "team_name" VARCHAR(100),
    "team_id" TEXT,
    "season" INTEGER,
    "season_id" TEXT
);

CREATE INDEX IF NOT EXISTS idx_fact_leadership_player_id ON "fact_leadership" ("player_id");
CREATE INDEX IF NOT EXISTS idx_fact_leadership_team_id ON "fact_leadership" ("team_id");

-- Penalty events
CREATE TABLE IF NOT EXISTS "fact_penalties" (
    "event_id" TEXT,
    "game_id" BIGINT,
    "period" INTEGER,
    "period_id" TEXT,
    "event_type" VARCHAR(100),
    "event_type_id" TEXT,
    "event_detail" VARCHAR(100),
    "event_detail_id" BIGINT,
    "event_detail_2" VARCHAR(100),
    "event_detail_2_id" TEXT,
    "event_successful" INTEGER,
    "success_id" BIGINT,
    "event_team_zone" VARCHAR(100),
    "event_zone_id" TEXT,
    "sequence_key" VARCHAR(100),
    "play_key" VARCHAR(100),
    "event_chain_key" VARCHAR(100),
    "tracking_event_key" VARCHAR(100),
    "shift_key" VARCHAR(100),
    "linked_event_key" VARCHAR(100),
    "home_team" VARCHAR(100),
    "home_team_id" TEXT,
    "away_team" VARCHAR(100),
    "away_team_id" TEXT,
    "duration" INTEGER,
    "event_player_ids" VARCHAR(100),
    "opp_player_ids" VARCHAR(100),
    "player_name" VARCHAR(100),
    "season_id" TEXT,
    "position_id" BIGINT,
    "shot_type_id" BIGINT,
    "zone_entry_type_id" BIGINT,
    "zone_exit_type_id" BIGINT,
    "stoppage_type_id" BIGINT,
    "giveaway_type_id" BIGINT,
    "takeaway_type_id" BIGINT,
    "turnover_type_id" BIGINT,
    "pass_type_id" BIGINT,
    "time_bucket_id" TEXT,
    "strength_id" TEXT,
    "cycle_key" INTEGER,
    "is_cycle" BOOLEAN,
    "event_start_min" INTEGER,
    "event_start_sec" INTEGER,
    "event_end_min" INTEGER,
    "event_end_sec" INTEGER,
    "running_video_time" INTEGER,
    "event_running_start" INTEGER,
    "event_running_end" INTEGER,
    "play_detail1" VARCHAR(100),
    "is_rush" BOOLEAN,
    "is_rebound" BOOLEAN,
    "is_breakout" BOOLEAN,
    "is_zone_entry" BOOLEAN,
    "is_zone_exit" BOOLEAN,
    "is_shot" BOOLEAN,
    "is_goal" BOOLEAN,
    "is_save" BOOLEAN,
    "is_turnover" BOOLEAN,
    "is_giveaway" BOOLEAN,
    "is_takeaway" BOOLEAN,
    "is_faceoff" BOOLEAN,
    "is_penalty" BOOLEAN,
    "is_blocked_shot" BOOLEAN,
    "is_missed_shot" BOOLEAN,
    "is_deflected" BOOLEAN,
    "is_sog" BOOLEAN,
    "shot_outcome_id" BIGINT,
    "pass_outcome_id" BIGINT,
    "save_outcome_id" BIGINT,
    "zone_outcome_id" BIGINT,
    "is_scoring_chance" BOOLEAN,
    "is_high_danger" BOOLEAN,
    "pressured_pressurer" INTEGER,
    "is_pressured" BOOLEAN,
    "danger_level" INTEGER,
    "danger_level_id" BIGINT,
    "scoring_chance_key" INTEGER,
    "penalty_key" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_fact_penalties_game_id ON "fact_penalties" ("game_id");
CREATE INDEX IF NOT EXISTS idx_fact_penalties_event_type ON "fact_penalties" ("event_type");

CREATE TABLE IF NOT EXISTS "fact_player_game_position" (
    "game_id" BIGINT,
    "player_id" TEXT,
    "total_shifts" INTEGER,
    "dominant_position" VARCHAR(100),
    "dominant_position_pct" DECIMAL(10,4),
    "forward_shifts" INTEGER,
    "defense_shifts" INTEGER,
    "goalie_shifts" INTEGER
);

CREATE INDEX IF NOT EXISTS idx_fact_player_game_position_game_id ON "fact_player_game_position" ("game_id");
CREATE INDEX IF NOT EXISTS idx_fact_player_game_position_player_id ON "fact_player_game_position" ("player_id");

CREATE TABLE IF NOT EXISTS "fact_plays" (
    "play_key" VARCHAR(100),
    "play_id" TEXT,
    "game_id" BIGINT,
    "season_id" TEXT,
    "period" INTEGER,
    "period_id" TEXT,
    "sequence_key" VARCHAR(100),
    "first_event_key" VARCHAR(100),
    "last_event_key" VARCHAR(100),
    "event_count" INTEGER,
    "start_min" INTEGER,
    "start_sec" INTEGER,
    "duration_seconds" INTEGER,
    "video_time_start" INTEGER,
    "video_time_end" INTEGER,
    "time_bucket_id" TEXT,
    "strength_id" TEXT,
    "home_team" VARCHAR(100),
    "home_team_id" TEXT,
    "away_team" VARCHAR(100),
    "away_team_id" TEXT,
    "start_zone" VARCHAR(100),
    "end_zone" VARCHAR(100),
    "start_zone_id" TEXT,
    "end_zone_id" TEXT,
    "event_types" VARCHAR(500),
    "has_goal" BOOLEAN,
    "goal_count" INTEGER,
    "has_shot" BOOLEAN,
    "shot_count" INTEGER,
    "zone_entry_count" INTEGER,
    "zone_exit_count" INTEGER,
    "pass_count" INTEGER,
    "pass_success_count" INTEGER,
    "turnover_count" INTEGER,
    "giveaway_count" INTEGER,
    "takeaway_count" INTEGER,
    "unique_player_count" INTEGER,
    "player_ids" VARCHAR(500)
);

CREATE INDEX IF NOT EXISTS idx_fact_plays_game_id ON "fact_plays" ("game_id");

CREATE TABLE IF NOT EXISTS "fact_registration" (
    "player_full_name" VARCHAR(100),
    "player_id" TEXT,
    "season_id" TEXT,
    "season" INTEGER,
    "restricted" VARCHAR(100),
    "email" VARCHAR(100),
    "position" VARCHAR(100),
    "norad_experience" VARCHAR(100),
    "CAF" VARCHAR(100),
    "highest_beer_league_played" VARCHAR(500),
    "skill_rating" INTEGER,
    "age" INTEGER,
    "referred_by" VARCHAR(100),
    "notes" VARCHAR(500),
    "sub_yn" VARCHAR(100),
    "drafted_team_name" VARCHAR(100),
    "drafted_team_id" TEXT,
    "player_season_registration_id" TEXT
);

CREATE INDEX IF NOT EXISTS idx_fact_registration_player_id ON "fact_registration" ("player_id");

CREATE TABLE IF NOT EXISTS "fact_rushes" (
    "event_id" TEXT,
    "game_id" BIGINT,
    "period" INTEGER,
    "period_id" TEXT,
    "event_type" VARCHAR(100),
    "event_type_id" TEXT,
    "event_detail" VARCHAR(100),
    "event_detail_id" BIGINT,
    "event_detail_2" VARCHAR(100),
    "event_detail_2_id" TEXT,
    "event_successful" VARCHAR(100),
    "success_id" TEXT,
    "event_team_zone" VARCHAR(100),
    "event_zone_id" TEXT,
    "sequence_key" VARCHAR(100),
    "play_key" VARCHAR(100),
    "event_chain_key" VARCHAR(100),
    "tracking_event_key" VARCHAR(100),
    "shift_key" VARCHAR(100),
    "linked_event_key" VARCHAR(100),
    "home_team" VARCHAR(100),
    "home_team_id" TEXT,
    "away_team" VARCHAR(100),
    "away_team_id" TEXT,
    "duration" INTEGER,
    "event_player_ids" VARCHAR(100),
    "opp_player_ids" VARCHAR(100),
    "player_name" VARCHAR(100),
    "season_id" TEXT,
    "position_id" BIGINT,
    "shot_type_id" BIGINT,
    "zone_entry_type_id" TEXT,
    "zone_exit_type_id" TEXT,
    "stoppage_type_id" BIGINT,
    "giveaway_type_id" BIGINT,
    "takeaway_type_id" BIGINT,
    "turnover_type_id" BIGINT,
    "pass_type_id" BIGINT,
    "time_bucket_id" TEXT,
    "strength_id" TEXT,
    "cycle_key" VARCHAR(100),
    "is_cycle" BOOLEAN,
    "event_start_min" INTEGER,
    "event_start_sec" INTEGER,
    "event_end_min" INTEGER,
    "event_end_sec" INTEGER,
    "running_video_time" INTEGER,
    "event_running_start" INTEGER,
    "event_running_end" INTEGER,
    "play_detail1" VARCHAR(100),
    "is_rush" BOOLEAN,
    "is_rebound" BOOLEAN,
    "is_breakout" BOOLEAN,
    "is_zone_entry" BOOLEAN,
    "is_zone_exit" BOOLEAN,
    "is_shot" BOOLEAN,
    "is_goal" BOOLEAN,
    "is_save" BOOLEAN,
    "is_turnover" BOOLEAN,
    "is_giveaway" BOOLEAN,
    "is_takeaway" BOOLEAN,
    "is_faceoff" BOOLEAN,
    "is_penalty" BOOLEAN,
    "is_blocked_shot" BOOLEAN,
    "is_missed_shot" BOOLEAN,
    "is_deflected" BOOLEAN,
    "is_sog" BOOLEAN,
    "shot_outcome_id" BIGINT,
    "pass_outcome_id" BIGINT,
    "save_outcome_id" BIGINT,
    "zone_outcome_id" TEXT,
    "is_scoring_chance" BOOLEAN,
    "is_high_danger" BOOLEAN,
    "pressured_pressurer" INTEGER,
    "is_pressured" BOOLEAN,
    "danger_level" INTEGER,
    "danger_level_id" BIGINT,
    "scoring_chance_key" INTEGER,
    "rush_key" VARCHAR(100),
    "rush_outcome" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_fact_rushes_game_id ON "fact_rushes" ("game_id");
CREATE INDEX IF NOT EXISTS idx_fact_rushes_event_type ON "fact_rushes" ("event_type");

-- Save events by goaltenders
CREATE TABLE IF NOT EXISTS "fact_saves" (
    "event_id" TEXT,
    "game_id" BIGINT,
    "period" INTEGER,
    "period_id" TEXT,
    "event_type" VARCHAR(100),
    "event_type_id" TEXT,
    "event_detail" VARCHAR(100),
    "event_detail_id" TEXT,
    "event_detail_2" VARCHAR(100),
    "event_detail_2_id" TEXT,
    "event_successful" INTEGER,
    "success_id" BIGINT,
    "event_team_zone" VARCHAR(100),
    "event_zone_id" TEXT,
    "sequence_key" VARCHAR(100),
    "play_key" VARCHAR(100),
    "event_chain_key" VARCHAR(100),
    "tracking_event_key" VARCHAR(100),
    "shift_key" VARCHAR(100),
    "linked_event_key" VARCHAR(100),
    "home_team" VARCHAR(100),
    "home_team_id" TEXT,
    "away_team" VARCHAR(100),
    "away_team_id" TEXT,
    "duration" INTEGER,
    "event_player_ids" VARCHAR(100),
    "opp_player_ids" VARCHAR(100),
    "player_name" VARCHAR(100),
    "season_id" TEXT,
    "position_id" BIGINT,
    "shot_type_id" BIGINT,
    "zone_entry_type_id" BIGINT,
    "zone_exit_type_id" BIGINT,
    "stoppage_type_id" BIGINT,
    "giveaway_type_id" BIGINT,
    "takeaway_type_id" BIGINT,
    "turnover_type_id" BIGINT,
    "pass_type_id" BIGINT,
    "time_bucket_id" TEXT,
    "strength_id" TEXT,
    "cycle_key" INTEGER,
    "is_cycle" BOOLEAN,
    "event_start_min" INTEGER,
    "event_start_sec" INTEGER,
    "event_end_min" INTEGER,
    "event_end_sec" INTEGER,
    "running_video_time" INTEGER,
    "event_running_start" INTEGER,
    "event_running_end" INTEGER,
    "play_detail1" INTEGER,
    "is_rush" BOOLEAN,
    "is_rebound" BOOLEAN,
    "is_breakout" BOOLEAN,
    "is_zone_entry" BOOLEAN,
    "is_zone_exit" BOOLEAN,
    "is_shot" BOOLEAN,
    "is_goal" BOOLEAN,
    "is_save" BOOLEAN,
    "is_turnover" BOOLEAN,
    "is_giveaway" BOOLEAN,
    "is_takeaway" BOOLEAN,
    "is_faceoff" BOOLEAN,
    "is_penalty" BOOLEAN,
    "is_blocked_shot" BOOLEAN,
    "is_missed_shot" BOOLEAN,
    "is_deflected" BOOLEAN,
    "is_sog" BOOLEAN,
    "shot_outcome_id" BIGINT,
    "pass_outcome_id" BIGINT,
    "save_outcome_id" TEXT,
    "zone_outcome_id" BIGINT,
    "is_scoring_chance" BOOLEAN,
    "is_high_danger" BOOLEAN,
    "pressured_pressurer" INTEGER,
    "is_pressured" BOOLEAN,
    "danger_level" INTEGER,
    "danger_level_id" BIGINT,
    "scoring_chance_key" INTEGER,
    "save_key" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_fact_saves_game_id ON "fact_saves" ("game_id");
CREATE INDEX IF NOT EXISTS idx_fact_saves_event_type ON "fact_saves" ("event_type");

CREATE TABLE IF NOT EXISTS "fact_scoring_chances_detailed" (
    "event_id" TEXT,
    "game_id" BIGINT,
    "period" INTEGER,
    "period_id" TEXT,
    "event_type" VARCHAR(100),
    "event_type_id" TEXT,
    "event_detail" VARCHAR(100),
    "event_detail_id" TEXT,
    "event_detail_2" VARCHAR(100),
    "event_detail_2_id" TEXT,
    "event_successful" VARCHAR(100),
    "success_id" TEXT,
    "event_team_zone" VARCHAR(100),
    "event_zone_id" TEXT,
    "sequence_key" VARCHAR(100),
    "play_key" VARCHAR(100),
    "event_chain_key" VARCHAR(100),
    "tracking_event_key" VARCHAR(100),
    "shift_key" VARCHAR(100),
    "linked_event_key" VARCHAR(100),
    "home_team" VARCHAR(100),
    "home_team_id" TEXT,
    "away_team" VARCHAR(100),
    "away_team_id" TEXT,
    "duration" INTEGER,
    "event_player_ids" VARCHAR(100),
    "opp_player_ids" VARCHAR(100),
    "player_name" VARCHAR(100),
    "season_id" TEXT,
    "position_id" BIGINT,
    "shot_type_id" BIGINT,
    "zone_entry_type_id" BIGINT,
    "zone_exit_type_id" BIGINT,
    "stoppage_type_id" TEXT,
    "giveaway_type_id" TEXT,
    "takeaway_type_id" BIGINT,
    "turnover_type_id" TEXT,
    "pass_type_id" BIGINT,
    "time_bucket_id" TEXT,
    "strength_id" TEXT,
    "cycle_key" VARCHAR(100),
    "is_cycle" BOOLEAN,
    "event_start_min" INTEGER,
    "event_start_sec" INTEGER,
    "event_end_min" INTEGER,
    "event_end_sec" INTEGER,
    "running_video_time" INTEGER,
    "event_running_start" INTEGER,
    "event_running_end" INTEGER,
    "play_detail1" VARCHAR(100),
    "is_rush" BOOLEAN,
    "is_rebound" BOOLEAN,
    "is_breakout" BOOLEAN,
    "is_zone_entry" BOOLEAN,
    "is_zone_exit" BOOLEAN,
    "is_shot" BOOLEAN,
    "is_goal" BOOLEAN,
    "is_save" BOOLEAN,
    "is_turnover" BOOLEAN,
    "is_giveaway" BOOLEAN,
    "is_takeaway" BOOLEAN,
    "is_faceoff" BOOLEAN,
    "is_penalty" BOOLEAN,
    "is_blocked_shot" BOOLEAN,
    "is_missed_shot" BOOLEAN,
    "is_deflected" BOOLEAN,
    "is_sog" BOOLEAN,
    "shot_outcome_id" TEXT,
    "pass_outcome_id" BIGINT,
    "save_outcome_id" BIGINT,
    "zone_outcome_id" BIGINT,
    "is_scoring_chance" BOOLEAN,
    "is_high_danger" BOOLEAN,
    "pressured_pressurer" INTEGER,
    "is_pressured" BOOLEAN,
    "danger_level" VARCHAR(100),
    "danger_level_id" TEXT,
    "scoring_chance_key" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_fact_scoring_chances_detailed_game_id ON "fact_scoring_chances_detailed" ("game_id");
CREATE INDEX IF NOT EXISTS idx_fact_scoring_chances_detailed_event_type ON "fact_scoring_chances_detailed" ("event_type");

CREATE TABLE IF NOT EXISTS "fact_season_summary" (
    "season_summary_key" VARCHAR(100),
    "season_id" TEXT,
    "games_tracked" INTEGER,
    "total_goals" INTEGER,
    "total_players" INTEGER,
    "avg_goals_per_game" INTEGER,
    "created_at" TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS "fact_sequences" (
    "sequence_key" VARCHAR(100),
    "sequence_id" TEXT,
    "game_id" BIGINT,
    "season_id" TEXT,
    "period" INTEGER,
    "period_id" TEXT,
    "first_event_key" VARCHAR(100),
    "last_event_key" VARCHAR(100),
    "event_count" INTEGER,
    "start_min" INTEGER,
    "start_sec" INTEGER,
    "duration_seconds" INTEGER,
    "video_time_start" INTEGER,
    "video_time_end" INTEGER,
    "time_bucket_id" TEXT,
    "strength_id" TEXT,
    "home_team" VARCHAR(100),
    "home_team_id" TEXT,
    "away_team" VARCHAR(100),
    "away_team_id" TEXT,
    "start_zone" VARCHAR(100),
    "end_zone" VARCHAR(100),
    "start_zone_id" TEXT,
    "end_zone_id" TEXT,
    "event_types" TEXT,
    "has_goal" BOOLEAN,
    "goal_count" INTEGER,
    "shot_count" INTEGER,
    "zone_entry_count" INTEGER,
    "zone_exit_count" INTEGER,
    "pass_count" INTEGER,
    "pass_success_count" INTEGER,
    "pass_success_rate" DECIMAL(10,4),
    "turnover_count" INTEGER,
    "giveaway_count" INTEGER,
    "takeaway_count" INTEGER,
    "unique_player_count" INTEGER,
    "player_ids" VARCHAR(500)
);

CREATE INDEX IF NOT EXISTS idx_fact_sequences_game_id ON "fact_sequences" ("game_id");

-- Bridge table linking shifts to players
CREATE TABLE IF NOT EXISTS "fact_shift_players" (
    "shift_player_id" TEXT,
    "shift_id" TEXT,
    "game_id" BIGINT,
    "shift_index" INTEGER,
    "player_game_number" INTEGER,
    "player_id" TEXT,
    "venue" VARCHAR(100),
    "position" VARCHAR(100),
    "period" INTEGER
);

CREATE INDEX IF NOT EXISTS idx_fact_shift_players_game_id ON "fact_shift_players" ("game_id");
CREATE INDEX IF NOT EXISTS idx_fact_shift_players_player_id ON "fact_shift_players" ("player_id");

-- Raw shift data - when players entered/exited ice
CREATE TABLE IF NOT EXISTS "fact_shifts" (
    "shift_id" TEXT,
    "game_id" BIGINT,
    "shift_index" INTEGER,
    "period" INTEGER,
    "shift_start_type" VARCHAR(100),
    "shift_stop_type" VARCHAR(100),
    "shift_start_min" INTEGER,
    "shift_start_sec" DECIMAL(12,4),
    "shift_end_min" INTEGER,
    "shift_end_sec" DECIMAL(12,4),
    "home_team" VARCHAR(100),
    "away_team" VARCHAR(100),
    "home_forward_1" INTEGER,
    "home_forward_2" INTEGER,
    "home_forward_3" INTEGER,
    "home_defense_1" INTEGER,
    "home_defense_2" INTEGER,
    "home_xtra" DECIMAL(12,4),
    "home_goalie" INTEGER,
    "away_forward_1" INTEGER,
    "away_forward_2" INTEGER,
    "away_forward_3" INTEGER,
    "away_defense_1" INTEGER,
    "away_defense_2" INTEGER,
    "away_xtra" INTEGER,
    "away_goalie" INTEGER,
    "shift_start_total_seconds" DECIMAL(12,4),
    "shift_end_total_seconds" DECIMAL(12,4),
    "shift_duration" INTEGER,
    "home_team_strength" INTEGER,
    "away_team_strength" INTEGER,
    "home_team_en" INTEGER,
    "away_team_en" INTEGER,
    "home_team_pk" INTEGER,
    "home_team_pp" INTEGER,
    "away_team_pp" INTEGER,
    "away_team_pk" INTEGER,
    "situation" VARCHAR(100),
    "strength" VARCHAR(100),
    "home_goals" INTEGER,
    "away_goals" INTEGER,
    "stoppage_time" INTEGER,
    "home_ozone_start" INTEGER,
    "home_ozone_end" INTEGER,
    "home_dzone_start" INTEGER,
    "home_dzone_end" INTEGER,
    "home_nzone_start" INTEGER,
    "home_nzone_end" INTEGER,
    "period_id" TEXT,
    "home_team_id" TEXT,
    "away_team_id" TEXT,
    "season_id" TEXT,
    "time_bucket_id" TEXT,
    "strength_id" TEXT,
    "shift_start_type_derived" VARCHAR(100),
    "shift_stop_type_derived" VARCHAR(100),
    "start_zone" VARCHAR(100),
    "end_zone" VARCHAR(100),
    "start_zone_id" BIGINT,
    "end_zone_id" BIGINT,
    "home_forward_1_id" TEXT,
    "home_forward_2_id" TEXT,
    "home_forward_3_id" TEXT,
    "home_defense_1_id" TEXT,
    "home_defense_2_id" TEXT,
    "home_xtra_id" TEXT,
    "home_goalie_id" TEXT,
    "away_forward_1_id" TEXT,
    "away_forward_2_id" TEXT,
    "away_forward_3_id" TEXT,
    "away_defense_1_id" TEXT,
    "away_defense_2_id" TEXT,
    "away_xtra_id" TEXT,
    "away_goalie_id" TEXT,
    "home_gf_all" INTEGER,
    "home_ga_all" INTEGER,
    "away_gf_all" INTEGER,
    "away_ga_all" INTEGER,
    "home_gf_ev" INTEGER,
    "home_ga_ev" INTEGER,
    "away_gf_ev" INTEGER,
    "away_ga_ev" INTEGER,
    "home_gf_nen" INTEGER,
    "home_ga_nen" INTEGER,
    "away_gf_nen" INTEGER,
    "away_ga_nen" INTEGER,
    "home_gf_pp" INTEGER,
    "home_ga_pp" INTEGER,
    "away_gf_pp" INTEGER,
    "away_ga_pp" INTEGER,
    "home_gf_pk" INTEGER,
    "home_ga_pk" INTEGER,
    "away_gf_pk" INTEGER,
    "away_ga_pk" INTEGER,
    "home_pm_all" INTEGER,
    "away_pm_all" INTEGER,
    "home_pm_ev" INTEGER,
    "away_pm_ev" INTEGER,
    "home_pm_nen" INTEGER,
    "away_pm_nen" INTEGER,
    "home_pm_pp" INTEGER,
    "away_pm_pp" INTEGER,
    "home_pm_pk" INTEGER,
    "away_pm_pk" INTEGER,
    "sf" INTEGER,
    "sa" INTEGER,
    "shot_diff" INTEGER,
    "cf" INTEGER,
    "ca" INTEGER,
    "cf_pct" DECIMAL(10,4),
    "ff" INTEGER,
    "fa" INTEGER,
    "ff_pct" DECIMAL(10,4),
    "scf" INTEGER,
    "sca" INTEGER,
    "hdf" INTEGER,
    "hda" INTEGER,
    "zone_entries" INTEGER,
    "zone_exits" INTEGER,
    "giveaways" INTEGER,
    "takeaways" INTEGER,
    "fo_won" INTEGER,
    "fo_lost" INTEGER,
    "fo_pct" DECIMAL(10,4),
    "event_count" INTEGER,
    "shift_start_type_id" TEXT,
    "shift_stop_type_id" TEXT,
    "situation_id" TEXT,
    "shift_key" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_fact_shifts_game_id ON "fact_shifts" ("game_id");

CREATE TABLE IF NOT EXISTS "fact_tracking" (
    "tracking_event_key" VARCHAR(100),
    "game_id" BIGINT,
    "period" INTEGER,
    "period_id" TEXT,
    "event_start_min" INTEGER,
    "event_start_sec" INTEGER,
    "event_end_min" INTEGER,
    "event_end_sec" INTEGER,
    "time_start_total_seconds" INTEGER,
    "time_end_total_seconds" INTEGER,
    "running_video_time" INTEGER,
    "event_running_start" INTEGER,
    "event_running_end" INTEGER,
    "event_team_zone" VARCHAR(100),
    "home_team_zone" VARCHAR(100),
    "away_team_zone" VARCHAR(100),
    "x_coord" DECIMAL(8,2),
    "y_coord" DECIMAL(8,2),
    "rink_zone" INTEGER,
    "season_id" TEXT,
    "time_bucket_id" TEXT,
    "strength_id" TEXT
);

CREATE INDEX IF NOT EXISTS idx_fact_tracking_game_id ON "fact_tracking" ("game_id");

CREATE TABLE IF NOT EXISTS "fact_turnovers_detailed" (
    "event_id" TEXT,
    "game_id" BIGINT,
    "period" INTEGER,
    "period_id" TEXT,
    "event_type" VARCHAR(100),
    "event_type_id" TEXT,
    "event_detail" VARCHAR(100),
    "event_detail_id" TEXT,
    "event_detail_2" VARCHAR(100),
    "event_detail_2_id" TEXT,
    "event_successful" VARCHAR(100),
    "success_id" TEXT,
    "event_team_zone" VARCHAR(100),
    "event_zone_id" TEXT,
    "sequence_key" VARCHAR(100),
    "play_key" VARCHAR(100),
    "event_chain_key" VARCHAR(100),
    "tracking_event_key" VARCHAR(100),
    "shift_key" VARCHAR(100),
    "linked_event_key" VARCHAR(100),
    "home_team" VARCHAR(100),
    "home_team_id" TEXT,
    "away_team" VARCHAR(100),
    "away_team_id" TEXT,
    "duration" INTEGER,
    "event_player_ids" VARCHAR(100),
    "opp_player_ids" VARCHAR(100),
    "player_name" VARCHAR(100),
    "season_id" TEXT,
    "position_id" BIGINT,
    "shot_type_id" BIGINT,
    "zone_entry_type_id" TEXT,
    "zone_exit_type_id" BIGINT,
    "stoppage_type_id" TEXT,
    "giveaway_type_id" TEXT,
    "takeaway_type_id" TEXT,
    "turnover_type_id" TEXT,
    "pass_type_id" BIGINT,
    "time_bucket_id" TEXT,
    "strength_id" TEXT,
    "cycle_key" INTEGER,
    "is_cycle" BOOLEAN,
    "event_start_min" INTEGER,
    "event_start_sec" INTEGER,
    "event_end_min" INTEGER,
    "event_end_sec" INTEGER,
    "running_video_time" INTEGER,
    "event_running_start" INTEGER,
    "event_running_end" INTEGER,
    "play_detail1" VARCHAR(100),
    "is_rush" BOOLEAN,
    "is_rebound" BOOLEAN,
    "is_breakout" BOOLEAN,
    "is_zone_entry" BOOLEAN,
    "is_zone_exit" BOOLEAN,
    "is_shot" BOOLEAN,
    "is_goal" BOOLEAN,
    "is_save" BOOLEAN,
    "is_turnover" BOOLEAN,
    "is_giveaway" BOOLEAN,
    "is_takeaway" BOOLEAN,
    "is_faceoff" BOOLEAN,
    "is_penalty" BOOLEAN,
    "is_blocked_shot" BOOLEAN,
    "is_missed_shot" BOOLEAN,
    "is_deflected" BOOLEAN,
    "is_sog" BOOLEAN,
    "shot_outcome_id" BIGINT,
    "pass_outcome_id" BIGINT,
    "save_outcome_id" BIGINT,
    "zone_outcome_id" BIGINT,
    "is_scoring_chance" BOOLEAN,
    "is_high_danger" BOOLEAN,
    "pressured_pressurer" INTEGER,
    "is_pressured" BOOLEAN,
    "danger_level" INTEGER,
    "danger_level_id" BIGINT,
    "scoring_chance_key" INTEGER,
    "turnover_key_new" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_fact_turnovers_detailed_game_id ON "fact_turnovers_detailed" ("game_id");
CREATE INDEX IF NOT EXISTS idx_fact_turnovers_detailed_event_type ON "fact_turnovers_detailed" ("event_type");

CREATE TABLE IF NOT EXISTS "fact_zone_entries" (
    "event_id" TEXT,
    "game_id" BIGINT,
    "period" INTEGER,
    "period_id" TEXT,
    "event_type" VARCHAR(100),
    "event_type_id" TEXT,
    "event_detail" VARCHAR(100),
    "event_detail_id" TEXT,
    "event_detail_2" VARCHAR(100),
    "event_detail_2_id" TEXT,
    "event_successful" VARCHAR(100),
    "success_id" TEXT,
    "event_team_zone" VARCHAR(100),
    "event_zone_id" TEXT,
    "sequence_key" VARCHAR(100),
    "play_key" VARCHAR(100),
    "event_chain_key" VARCHAR(100),
    "tracking_event_key" VARCHAR(100),
    "shift_key" VARCHAR(100),
    "linked_event_key" VARCHAR(100),
    "home_team" VARCHAR(100),
    "home_team_id" TEXT,
    "away_team" VARCHAR(100),
    "away_team_id" TEXT,
    "duration" INTEGER,
    "event_player_ids" VARCHAR(100),
    "opp_player_ids" VARCHAR(100),
    "player_name" VARCHAR(100),
    "season_id" TEXT,
    "position_id" BIGINT,
    "shot_type_id" BIGINT,
    "zone_entry_type_id" TEXT,
    "zone_exit_type_id" TEXT,
    "stoppage_type_id" BIGINT,
    "giveaway_type_id" TEXT,
    "takeaway_type_id" BIGINT,
    "turnover_type_id" TEXT,
    "pass_type_id" BIGINT,
    "time_bucket_id" TEXT,
    "strength_id" TEXT,
    "cycle_key" VARCHAR(100),
    "is_cycle" BOOLEAN,
    "event_start_min" INTEGER,
    "event_start_sec" INTEGER,
    "event_end_min" INTEGER,
    "event_end_sec" INTEGER,
    "running_video_time" INTEGER,
    "event_running_start" INTEGER,
    "event_running_end" INTEGER,
    "play_detail1" VARCHAR(100),
    "is_rush" BOOLEAN,
    "is_rebound" BOOLEAN,
    "is_breakout" BOOLEAN,
    "is_zone_entry" BOOLEAN,
    "is_zone_exit" BOOLEAN,
    "is_shot" BOOLEAN,
    "is_goal" BOOLEAN,
    "is_save" BOOLEAN,
    "is_turnover" BOOLEAN,
    "is_giveaway" BOOLEAN,
    "is_takeaway" BOOLEAN,
    "is_faceoff" BOOLEAN,
    "is_penalty" BOOLEAN,
    "is_blocked_shot" BOOLEAN,
    "is_missed_shot" BOOLEAN,
    "is_deflected" BOOLEAN,
    "is_sog" BOOLEAN,
    "shot_outcome_id" BIGINT,
    "pass_outcome_id" BIGINT,
    "save_outcome_id" BIGINT,
    "zone_outcome_id" TEXT,
    "is_scoring_chance" BOOLEAN,
    "is_high_danger" BOOLEAN,
    "pressured_pressurer" INTEGER,
    "is_pressured" BOOLEAN,
    "danger_level" INTEGER,
    "danger_level_id" BIGINT,
    "scoring_chance_key" INTEGER,
    "zone_entry_key" VARCHAR(100),
    "entry_method" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_fact_zone_entries_game_id ON "fact_zone_entries" ("game_id");
CREATE INDEX IF NOT EXISTS idx_fact_zone_entries_event_type ON "fact_zone_entries" ("event_type");

CREATE TABLE IF NOT EXISTS "fact_zone_exits" (
    "event_id" TEXT,
    "game_id" BIGINT,
    "period" INTEGER,
    "period_id" TEXT,
    "event_type" VARCHAR(100),
    "event_type_id" TEXT,
    "event_detail" VARCHAR(100),
    "event_detail_id" BIGINT,
    "event_detail_2" VARCHAR(100),
    "event_detail_2_id" TEXT,
    "event_successful" VARCHAR(100),
    "success_id" TEXT,
    "event_team_zone" VARCHAR(100),
    "event_zone_id" TEXT,
    "sequence_key" VARCHAR(100),
    "play_key" VARCHAR(100),
    "event_chain_key" VARCHAR(100),
    "tracking_event_key" VARCHAR(100),
    "shift_key" VARCHAR(100),
    "linked_event_key" VARCHAR(100),
    "home_team" VARCHAR(100),
    "home_team_id" TEXT,
    "away_team" VARCHAR(100),
    "away_team_id" TEXT,
    "duration" INTEGER,
    "event_player_ids" VARCHAR(100),
    "opp_player_ids" VARCHAR(100),
    "player_name" VARCHAR(100),
    "season_id" TEXT,
    "position_id" BIGINT,
    "shot_type_id" BIGINT,
    "zone_entry_type_id" TEXT,
    "zone_exit_type_id" TEXT,
    "stoppage_type_id" BIGINT,
    "giveaway_type_id" TEXT,
    "takeaway_type_id" BIGINT,
    "turnover_type_id" TEXT,
    "pass_type_id" BIGINT,
    "time_bucket_id" TEXT,
    "strength_id" TEXT,
    "cycle_key" INTEGER,
    "is_cycle" BOOLEAN,
    "event_start_min" INTEGER,
    "event_start_sec" INTEGER,
    "event_end_min" INTEGER,
    "event_end_sec" INTEGER,
    "running_video_time" INTEGER,
    "event_running_start" INTEGER,
    "event_running_end" INTEGER,
    "play_detail1" VARCHAR(100),
    "is_rush" BOOLEAN,
    "is_rebound" BOOLEAN,
    "is_breakout" BOOLEAN,
    "is_zone_entry" BOOLEAN,
    "is_zone_exit" BOOLEAN,
    "is_shot" BOOLEAN,
    "is_goal" BOOLEAN,
    "is_save" BOOLEAN,
    "is_turnover" BOOLEAN,
    "is_giveaway" BOOLEAN,
    "is_takeaway" BOOLEAN,
    "is_faceoff" BOOLEAN,
    "is_penalty" BOOLEAN,
    "is_blocked_shot" BOOLEAN,
    "is_missed_shot" BOOLEAN,
    "is_deflected" BOOLEAN,
    "is_sog" BOOLEAN,
    "shot_outcome_id" BIGINT,
    "pass_outcome_id" BIGINT,
    "save_outcome_id" BIGINT,
    "zone_outcome_id" TEXT,
    "is_scoring_chance" BOOLEAN,
    "is_high_danger" BOOLEAN,
    "pressured_pressurer" INTEGER,
    "is_pressured" BOOLEAN,
    "danger_level" INTEGER,
    "danger_level_id" BIGINT,
    "scoring_chance_key" INTEGER,
    "zone_exit_key" VARCHAR(100),
    "exit_method" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_fact_zone_exits_game_id ON "fact_zone_exits" ("game_id");
CREATE INDEX IF NOT EXISTS idx_fact_zone_exits_event_type ON "fact_zone_exits" ("event_type");


-- ============================================================
-- QA TABLES (2)
-- ============================================================

-- Quality assurance - checks for missing data
CREATE TABLE IF NOT EXISTS "qa_data_completeness" (
    "qa_key" VARCHAR(100),
    "game_id" BIGINT,
    "has_events" BOOLEAN,
    "has_shifts" BOOLEAN,
    "has_rosters" BOOLEAN,
    "is_complete" BOOLEAN,
    "check_date" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_qa_data_completeness_game_id ON "qa_data_completeness" ("game_id");

-- Quality assurance - verifies goal counts match official records
CREATE TABLE IF NOT EXISTS "qa_goal_accuracy" (
    "qa_key" VARCHAR(100),
    "game_id" BIGINT,
    "game_date" VARCHAR(100),
    "home_team" VARCHAR(100),
    "away_team" VARCHAR(100),
    "expected_goals" INTEGER,
    "actual_goals" INTEGER,
    "match" BOOLEAN,
    "difference" INTEGER,
    "check_date" VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_qa_goal_accuracy_game_id ON "qa_goal_accuracy" ("game_id");


-- ============================================================
-- USEFUL VIEWS
-- ============================================================

-- Goals with scorer and assists
CREATE OR REPLACE VIEW v_goals AS
SELECT 
    e.game_id,
    e.period,
    e.event_id,
    e.player_name as scorer,
    e.event_detail,
    e.event_team_zone as zone
FROM fact_events e
WHERE e.event_type = 'Goal' 
  AND e.event_detail = 'Goal_Scored';

-- Player game stats summary
CREATE OR REPLACE VIEW v_player_game_summary AS
SELECT 
    ep.game_id,
    ep.player_id,
    ep.player_name,
    COUNT(*) FILTER (WHERE ep.event_type = 'Goal' AND ep.player_role = 'event_player_1') as goals,
    COUNT(*) FILTER (WHERE ep.event_type = 'Goal' AND ep.player_role = 'event_player_2') as primary_assists,
    COUNT(*) FILTER (WHERE ep.event_type = 'Goal' AND ep.player_role = 'event_player_3') as secondary_assists,
    COUNT(*) FILTER (WHERE ep.event_type = 'Shot' AND ep.player_role = 'event_player_1') as shots
FROM fact_event_players ep
GROUP BY ep.game_id, ep.player_id, ep.player_name;

-- Game summary
CREATE OR REPLACE VIEW v_game_summary AS
SELECT 
    e.game_id,
    e.home_team,
    e.away_team,
    COUNT(*) FILTER (WHERE e.event_type = 'Goal' AND e.event_detail = 'Goal_Scored') as total_goals,
    COUNT(*) FILTER (WHERE e.event_type = 'Shot') as total_shots,
    COUNT(DISTINCT e.period) as periods_played
FROM fact_events e
GROUP BY e.game_id, e.home_team, e.away_team;