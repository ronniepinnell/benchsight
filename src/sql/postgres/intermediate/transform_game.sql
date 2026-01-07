-- =============================================================================
-- POSTGRESQL: TRANSFORM GAME TRACKING DATA
-- =============================================================================
-- File: src/sql/postgres/intermediate/transform_game.sql
--
-- PURPOSE:
--     Transform game tracking data from stage to intermediate layer.
--     Game ID is passed as parameter :game_id
--
-- USAGE:
--     Replace :game_id with actual game ID before execution.
-- =============================================================================

-- =============================================================================
-- INT_EVENTS: Deduplicated events with composite keys
-- =============================================================================
-- WHY: Events table has multiple rows per event (one per player involved).
--      We need a deduplicated event table for aggregations.

DROP TABLE IF EXISTS intermediate.int_events_:game_id CASCADE;

CREATE TABLE intermediate.int_events_:game_id AS
SELECT DISTINCT ON (event_index)
    event_index,
    -- Create composite key: game_id + event_index
    ':game_id' || '_' || event_index::TEXT AS event_key,
    
    -- Shift reference
    shift_index,
    ':game_id' || '_' || shift_index::TEXT AS shift_key,
    
    -- Linked events for deduplication
    linked_event_index,
    sequence_index,
    play_index,
    
    -- Event classification
    "Type" AS event_type,
    event_detail,
    event_detail_2,
    event_successful,
    
    -- Timing
    period,
    event_start_min,
    event_start_sec,
    time_start_total_seconds AS time_total_seconds,
    duration,
    
    -- Location
    event_team_zone,
    
    -- Game reference
    :game_id AS game_id,
    
    -- Metadata
    NOW() AS _processed_timestamp

FROM stage.stg_events_:game_id
WHERE event_index IS NOT NULL
ORDER BY event_index;

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_int_events_:game_id_idx 
    ON intermediate.int_events_:game_id(event_index);

-- =============================================================================
-- INT_EVENT_PLAYERS: Player involvement in events
-- =============================================================================
-- WHY: Track which players were involved in each event and their roles.
--      One row per player per event.

DROP TABLE IF EXISTS intermediate.int_event_players_:game_id CASCADE;

CREATE TABLE intermediate.int_event_players_:game_id AS
SELECT
    event_index,
    ':game_id' || '_' || event_index::TEXT AS event_key,
    
    -- Player identification
    player_game_number,
    player_id,
    player_team,
    ':game_id' || '_' || player_game_number::TEXT AS player_game_key,
    
    -- Role in event
    player_role,
    
    -- Play details (passes, assists, etc.)
    play_detail1,
    play_detail_2,
    play_detail_successful,
    
    -- Derived flags
    -- WHY: Quick filtering for primary player analysis
    CASE WHEN player_role = 'event_team_player_1' THEN 1 ELSE 0 END AS is_primary_player,
    CASE WHEN player_role LIKE 'event_team%' THEN 1 ELSE 0 END AS is_event_team,
    
    -- Composite key for this specific player-event
    ':game_id' || '_' || event_index::TEXT || '_' || player_game_number::TEXT AS event_player_key,
    
    -- Game reference
    :game_id AS game_id,
    
    NOW() AS _processed_timestamp

FROM stage.stg_events_:game_id
WHERE player_game_number IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_int_ep_:game_id_event 
    ON intermediate.int_event_players_:game_id(event_index);
CREATE INDEX IF NOT EXISTS idx_int_ep_:game_id_player 
    ON intermediate.int_event_players_:game_id(player_game_number);

-- =============================================================================
-- INT_SHIFTS: Cleaned shift data with strength info
-- =============================================================================
-- WHY: Shifts define time periods and which players were on ice.
--      Essential for TOI calculation and contextual analysis.

DROP TABLE IF EXISTS intermediate.int_shifts_:game_id CASCADE;

CREATE TABLE intermediate.int_shifts_:game_id AS
SELECT
    shift_index,
    ':game_id' || '_' || shift_index::TEXT AS shift_key,
    
    -- Period
    "Period" AS period,
    
    -- Timing
    shift_start_total_seconds,
    shift_end_total_seconds,
    shift_duration,
    
    -- Shift type
    shift_start_type,
    shift_stop_type,
    
    -- Strength situation
    situation,
    strength,
    COALESCE(home_team_strength, 5)::INTEGER AS home_strength,
    COALESCE(away_team_strength, 5)::INTEGER AS away_strength,
    
    -- Score state during shift
    COALESCE(home_goals, 0)::INTEGER AS home_goals,
    COALESCE(away_goals, 0)::INTEGER AS away_goals,
    
    -- Plus/minus events during shift
    COALESCE(home_team_plus, 0)::INTEGER AS home_plus,
    COALESCE(home_team_minus, 0)::INTEGER AS home_minus,
    COALESCE(away_team_plus, 0)::INTEGER AS away_plus,
    COALESCE(away_team_minus, 0)::INTEGER AS away_minus,
    
    -- Players on ice (home)
    home_forward_1,
    home_forward_2,
    home_forward_3,
    home_defense_1,
    home_defense_2,
    home_goalie,
    
    -- Players on ice (away)
    away_forward_1,
    away_forward_2,
    away_forward_3,
    away_defense_1,
    away_defense_2,
    away_goalie,
    
    -- Game reference
    :game_id AS game_id,
    
    NOW() AS _processed_timestamp

FROM stage.stg_shifts_:game_id
WHERE shift_index IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_int_shifts_:game_id_idx 
    ON intermediate.int_shifts_:game_id(shift_index);

-- =============================================================================
-- INT_GAME_PLAYERS: Players in this game from roster
-- =============================================================================
-- WHY: Quick reference for all players participating in this specific game.
--      Enriched with skill ratings from player dimension.

DROP TABLE IF EXISTS intermediate.int_game_players_:game_id CASCADE;

CREATE TABLE intermediate.int_game_players_:game_id AS
SELECT
    gr.player_game_number,
    gr.player_id,
    gr.player_game_key,
    gr.player_full_name,
    gr.display_name,
    gr.team_name AS player_team,
    gr.team_venue AS player_venue,
    gr.player_position AS position,
    gr.skill_rating,
    :game_id AS game_id,
    NOW() AS _processed_timestamp

FROM intermediate.int_fact_gameroster gr
WHERE gr.game_id = :game_id;

CREATE INDEX IF NOT EXISTS idx_int_gp_:game_id_num 
    ON intermediate.int_game_players_:game_id(player_game_number);
