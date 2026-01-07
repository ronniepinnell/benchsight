-- FIX: Allow public inserts on ALL tables
-- Run this in Supabase SQL Editor

-- Dimension tables - add insert policies
CREATE POLICY "Public insert" ON dim_player FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_team FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_schedule FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_season FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_league FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_rinkboxcoord FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_rinkcoordzones FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_video FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_event_type FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_event_detail FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_play_detail FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_strength FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_situation FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_position FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_zone FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_period FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_venue FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_shot_type FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_pass_type FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_shift_type FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_skill_tier FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_player_role FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_danger_zone FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON dim_time_bucket FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON fact_gameroster FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON fact_playergames FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON fact_box_score_tracking FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON fact_events_long FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON fact_linked_events_tracking FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON fact_sequences_tracking FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert" ON fact_plays_tracking FOR INSERT WITH CHECK (true);
