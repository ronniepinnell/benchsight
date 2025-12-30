-- ============================================================================
-- SCHEMA FIX: Correct column type mismatches
-- Run this in Supabase SQL Editor BEFORE deploying data
-- Run each block separately if errors occur
-- ============================================================================

-- BLOCK 1: dim_period - period_number has "OT", "SO"
ALTER TABLE dim_period ALTER COLUMN period_number TYPE TEXT USING period_number::TEXT;

-- BLOCK 2: dim_stat - benchmark columns have "10%", "15%", etc
ALTER TABLE dim_stat ALTER COLUMN nhl_avg_per_game TYPE TEXT USING nhl_avg_per_game::TEXT;
ALTER TABLE dim_stat ALTER COLUMN nhl_elite_threshold TYPE TEXT USING nhl_elite_threshold::TEXT;
ALTER TABLE dim_stat ALTER COLUMN nhl_min_threshold TYPE TEXT USING nhl_min_threshold::TEXT;

-- BLOCK 3: fact_gameroster - player_game_number has "FA", sub has "True" 
ALTER TABLE fact_gameroster ALTER COLUMN player_game_number TYPE TEXT USING player_game_number::TEXT;
ALTER TABLE fact_gameroster ALTER COLUMN sub TYPE TEXT USING sub::TEXT;

-- BLOCK 4: fact_player_boxscore_all - player_number has "FA"
ALTER TABLE fact_player_boxscore_all ALTER COLUMN player_number TYPE TEXT USING player_number::TEXT;

-- BLOCK 5: fact_registration - norad_experience has "10+"
ALTER TABLE fact_registration ALTER COLUMN norad_experience TYPE TEXT USING norad_experience::TEXT;

-- BLOCK 6: fact_plays - event_chain_indices has "1001,1002,1003"
ALTER TABLE fact_plays ALTER COLUMN event_chain_indices TYPE TEXT USING event_chain_indices::TEXT;

-- BLOCK 7: fact_sequences - event_chain_indices has comma-separated values
ALTER TABLE fact_sequences ALTER COLUMN event_chain_indices TYPE TEXT USING event_chain_indices::TEXT;

-- BLOCK 8: fact_game_status - is_loaded is boolean stored as text
ALTER TABLE fact_game_status ALTER COLUMN is_loaded TYPE TEXT USING is_loaded::TEXT;
ALTER TABLE fact_game_status ALTER COLUMN goal_match TYPE TEXT USING goal_match::TEXT;

-- BLOCK 9: fact_linked_events - event type columns have "Faceoff"
ALTER TABLE fact_linked_events ALTER COLUMN event_1_type TYPE TEXT USING event_1_type::TEXT;
ALTER TABLE fact_linked_events ALTER COLUMN event_2_type TYPE TEXT USING event_2_type::TEXT;
ALTER TABLE fact_linked_events ALTER COLUMN event_3_type TYPE TEXT USING event_3_type::TEXT;
ALTER TABLE fact_linked_events ALTER COLUMN event_4_type TYPE TEXT USING event_4_type::TEXT;
ALTER TABLE fact_linked_events ALTER COLUMN event_5_type TYPE TEXT USING event_5_type::TEXT;

-- BLOCK 10: fact_player_stats_long - stat_value has decimals
ALTER TABLE fact_player_stats_long ALTER COLUMN stat_value TYPE TEXT USING stat_value::TEXT;
