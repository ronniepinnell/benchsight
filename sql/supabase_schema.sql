-- BENCHSIGHT SUPABASE SCHEMA
-- 15 tables matching CSV output exactly
-- Run this in Supabase SQL Editor

-- =====================
-- DIMENSION TABLES
-- =====================

CREATE TABLE dim_player (
  index int,
  player_first_name text,
  player_last_name text,
  player_full_name text,
  player_id text PRIMARY KEY,
  player_primary_position text,
  current_skill_rating float,
  player_hand text,
  birth_year int,
  player_gender text,
  highest_beer_league text,
  player_rating_ly float,
  player_notes text,
  player_leadership text,
  player_norad text,
  player_csaha text,
  player_norad_primary_number text,
  player_csah_primary_number text,
  player_norad_current_team text,
  player_csah_current_team text,
  player_norad_current_team_id text,
  player_csah_current_team_id text,
  other_url text,
  player_url text,
  player_image text,
  random_player_first_name text,
  random_player_last_name text,
  random_player_full_name text
);

CREATE TABLE dim_team (
  index int,
  team_name text,
  team_id text PRIMARY KEY,
  norad_team text,
  csah_team text,
  league_id text,
  league text,
  long_team_name text,
  team_cd text,
  team_color1 text,
  team_color2 text,
  team_color3 text,
  team_color4 text,
  team_logo text,
  team_url text
);

CREATE TABLE dim_schedule (
  index int,
  game_id int PRIMARY KEY,
  season text,
  season_id text,
  game_url text,
  home_team_game_id text,
  away_team_game_id text,
  date date,
  game_time text,
  home_team_name text,
  away_team_name text,
  home_team_id text,
  away_team_id text,
  head_to_head_id text,
  game_type text,
  playoff_round text,
  last_period_type text,
  period_length int,
  ot_period_length int,
  shootout_rounds int,
  home_total_goals int,
  away_total_goals int,
  home_team_period1_goals int,
  home_team_period2_goals int,
  home_team_period3_goals int,
  home_team_periodOT_goals int,
  away_team_period1_goals int,
  away_team_period2_goals int,
  away_team_period3_goals int,
  away_team_periodOT_goals int,
  home_team_seeding int,
  away_team_seeding int,
  home_team_w int,
  home_team_l int,
  home_team_t int,
  home_team_pts int,
  away_team_w int,
  away_team_l int,
  away_team_t int,
  away_team_pts int,
  video_id text,
  video_start_time text,
  video_end_time text,
  video_title text,
  video_url text
);

CREATE TABLE dim_season (
  index int,
  season_id text PRIMARY KEY,
  season text,
  session text,
  norad text,
  csah text,
  league_id text,
  league text,
  start_date date
);

CREATE TABLE dim_league (
  index int,
  league_id text PRIMARY KEY,
  league text
);

CREATE TABLE dim_rinkboxcoord (
  box_id int PRIMARY KEY,
  box_id_rev int,
  x_min float,
  x_max float,
  y_min float,
  y_max float,
  area float,
  x_description text,
  y_description text,
  danger text,
  zone text,
  side text
);

CREATE TABLE dim_rinkcoordzones (
  id serial PRIMARY KEY,
  box_id int,
  box_id_rev int,
  x_min float,
  x_max float,
  y_min float,
  y_max float,
  y_description text,
  x_description text,
  danger text,
  slot text,
  zone text,
  side text,
  dotside text,
  depth text
);

CREATE TABLE dim_video (
  id serial PRIMARY KEY,
  index int,
  key text,
  game_id int,
  video_type text,
  video_category text,
  url_1 text,
  url_2 text,
  url_3 text,
  url_4 text,
  video_id text,
  extension text,
  embed_url text,
  description text,
  _source_file text
);

-- =====================
-- FACT TABLES
-- =====================

CREATE TABLE fact_gameroster (
  id serial PRIMARY KEY,
  index int,
  game_id int,
  team_game_id text,
  opp_team_game_id text,
  player_game_id text,
  team_venue text,
  team_name text,
  opp_team_name text,
  player_game_number text,
  n_player_url text,
  player_position text,
  games_played int,
  goals int,
  assist int,
  goals_against int,
  pim int,
  shutouts int,
  team_id text,
  opp_team_id text,
  key text,
  player_full_name text,
  player_id text,
  date date,
  season text,
  sub text,
  current_team text,
  skill_rating float
);

CREATE TABLE fact_events_tracking (
  id serial PRIMARY KEY,
  game_id int,
  event_index int,
  shift_index int,
  linked_event_index int,
  sequence_index int,
  play_index int,
  period int,
  type text,
  event_detail text,
  event_detail_2 text,
  event_successful text,
  event_team_zone text,
  team_venue text,
  player_game_number text,
  player_role text,
  event_start_min int,
  event_start_sec int,
  event_end_min int,
  event_end_sec int,
  time_start_total_seconds int,
  time_end_total_seconds int,
  duration int,
  play_detail1 text,
  play_detail_2 text,
  play_detail_successful text,
  pressured_pressurer text,
  home_team text,
  away_team text,
  _source_file text,
  _export_timestamp timestamp
);

CREATE TABLE fact_shifts_tracking (
  id serial PRIMARY KEY,
  game_id int,
  shift_index int,
  period int,
  shift_start_min int,
  shift_start_sec int,
  shift_end_min int,
  shift_end_sec int,
  shift_start_total_seconds int,
  shift_end_total_seconds int,
  shift_duration int,
  shift_start_type text,
  shift_stop_type text,
  situation text,
  strength text,
  home_team_strength int,
  away_team_strength int,
  home_goals int,
  away_goals int,
  home_forward_1 text,
  home_forward_2 text,
  home_forward_3 text,
  home_defense_1 text,
  home_defense_2 text,
  home_goalie text,
  home_xtra text,
  away_forward_1 text,
  away_forward_2 text,
  away_forward_3 text,
  away_defense_1 text,
  away_defense_2 text,
  away_goalie text,
  away_xtra text,
  home_team text,
  away_team text,
  _source_file text,
  _export_timestamp timestamp
);

CREATE TABLE fact_playergames (
  id serial PRIMARY KEY,
  orig_id text,
  date date,
  type text,
  team text,
  opp text,
  player_number text,
  player text,
  position text,
  gp int,
  g int,
  a int,
  ga int,
  pim int,
  so int,
  rank int,
  id2 text,
  id3 text,
  season text,
  season_player_id text
);

CREATE TABLE fact_box_score_tracking (
  id serial PRIMARY KEY,
  player_game_key text,
  player_game_number text,
  player_id text,
  player_team text,
  player_venue text,
  skill_rating float,
  position text,
  player_full_name text,
  display_name text,
  game_id int,
  toi_seconds int,
  plus_minus int,
  shifts int,
  toi_formatted text,
  goals int,
  assists_primary int,
  assists_secondary int,
  assists int,
  points int,
  shots int,
  shots_on_goal int,
  shooting_pct float,
  passes int,
  passes_completed int,
  pass_pct float,
  times_pass_target int,
  giveaways int,
  takeaways int,
  turnover_differential int,
  faceoffs int,
  faceoff_wins int,
  faceoff_pct float,
  zone_entries int,
  zone_exits int,
  stick_checks int,
  poke_checks int,
  blocked_shots_play int,
  backchecks int,
  in_shot_pass_lane int,
  separate_from_puck int,
  zone_entry_denials int,
  zone_exit_denials int,
  take_away int,
  dekes int,
  dekes_successful int,
  screens int,
  dump_and_chase int,
  tip int,
  one_timer int,
  puck_recovery int,
  board_battle_win int,
  board_battle_loss int,
  second_touch int,
  pass_intercepted int,
  drives int,
  drives_successful int,
  breakouts int,
  saves int,
  avg_opp_skill_faced float,
  skill_vs_opponents float,
  goals_per_60 float,
  assists_per_60 float,
  points_per_60 float,
  shots_per_60 float,
  is_tracked boolean
);

CREATE TABLE fact_event_coordinates (
  id serial PRIMARY KEY,
  event_id text,
  game_id int,
  entity_type text,
  entity_slot int,
  sequence int,
  x float,
  y float,
  _export_timestamp timestamp
);

-- =====================
-- INDEXES FOR PERFORMANCE
-- =====================

CREATE INDEX idx_events_game ON fact_events_tracking(game_id);
CREATE INDEX idx_events_period ON fact_events_tracking(period);
CREATE INDEX idx_shifts_game ON fact_shifts_tracking(game_id);
CREATE INDEX idx_gameroster_game ON fact_gameroster(game_id);
CREATE INDEX idx_gameroster_player ON fact_gameroster(player_id);
CREATE INDEX idx_playergames_player ON fact_playergames(player);
CREATE INDEX idx_coords_event ON fact_event_coordinates(event_id);
CREATE INDEX idx_coords_game ON fact_event_coordinates(game_id);
CREATE INDEX idx_video_game ON dim_video(game_id);

-- =====================
-- ROW LEVEL SECURITY (disable for now)
-- =====================

ALTER TABLE dim_player ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_team ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_schedule ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_season ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_league ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_rinkboxcoord ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_rinkcoordzones ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_video ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_gameroster ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_events_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_shifts_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_playergames ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_box_score_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_event_coordinates ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "Public read" ON dim_player FOR SELECT USING (true);
CREATE POLICY "Public read" ON dim_team FOR SELECT USING (true);
CREATE POLICY "Public read" ON dim_schedule FOR SELECT USING (true);
CREATE POLICY "Public read" ON dim_season FOR SELECT USING (true);
CREATE POLICY "Public read" ON dim_league FOR SELECT USING (true);
CREATE POLICY "Public read" ON dim_rinkboxcoord FOR SELECT USING (true);
CREATE POLICY "Public read" ON dim_rinkcoordzones FOR SELECT USING (true);
CREATE POLICY "Public read" ON dim_video FOR SELECT USING (true);
CREATE POLICY "Public read" ON fact_gameroster FOR SELECT USING (true);
CREATE POLICY "Public read" ON fact_events_tracking FOR SELECT USING (true);
CREATE POLICY "Public read" ON fact_shifts_tracking FOR SELECT USING (true);
CREATE POLICY "Public read" ON fact_playergames FOR SELECT USING (true);
CREATE POLICY "Public read" ON fact_box_score_tracking FOR SELECT USING (true);
CREATE POLICY "Public read" ON fact_event_coordinates FOR SELECT USING (true);

-- Allow public write for tracker
CREATE POLICY "Public insert" ON fact_events_tracking FOR INSERT WITH CHECK (true);
CREATE POLICY "Public update" ON fact_events_tracking FOR UPDATE USING (true);
CREATE POLICY "Public insert" ON fact_shifts_tracking FOR INSERT WITH CHECK (true);
CREATE POLICY "Public update" ON fact_shifts_tracking FOR UPDATE USING (true);
CREATE POLICY "Public insert" ON fact_event_coordinates FOR INSERT WITH CHECK (true);
CREATE POLICY "Public update" ON fact_event_coordinates FOR UPDATE USING (true);
