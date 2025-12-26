-- =============================================================================
-- INTERMEDIATE: TRANSFORM GAME TRACKING DATA WITH STANDARDIZED KEYS
-- =============================================================================
-- Game ID is substituted as :game_id by Python
-- 
-- KEY FORMAT STANDARD:
--   All keys follow pattern: {PREFIX}{GAME_ID:05d}{INDEX:05d}
--   Total: 12 characters
--   
--   Prefixes:
--     EV = Event
--     SH = Shift
--     EP = Event Player
--     GP = Game Player
--     SQ = Sequence
--     PL = Play
--     LK = Linked Event
--     BS = Box Score
-- =============================================================================

-- INT_EVENTS
-- Primary Key: event_key (EV prefix)
-- Foreign Keys: shift_key, linked_event_key, game_id
DROP TABLE IF EXISTS int_events_:game_id;

CREATE TABLE int_events_:game_id AS
SELECT
    CAST(event_index AS INTEGER) AS event_index,
    'EV' || printf('%05d', :game_id) || printf('%05d', CAST(event_index AS INTEGER)) AS event_key,
    CAST(shift_index AS INTEGER) AS shift_index,
    'SH' || printf('%05d', :game_id) || printf('%05d', CAST(COALESCE(shift_index, 0) AS INTEGER)) AS shift_key,
    CAST(linked_event_index AS INTEGER) AS linked_event_index,
    CASE 
        WHEN linked_event_index IS NOT NULL AND linked_event_index > 0 
        THEN 'LK' || printf('%05d', :game_id) || printf('%05d', CAST(linked_event_index AS INTEGER))
        ELSE NULL 
    END AS linked_event_key,
    CAST(sequence_index AS INTEGER) AS sequence_index,
    CASE 
        WHEN sequence_index IS NOT NULL 
        THEN 'SQ' || printf('%05d', :game_id) || printf('%05d', CAST(sequence_index AS INTEGER))
        ELSE NULL 
    END AS sequence_key,
    CAST(play_index AS INTEGER) AS play_index,
    CASE 
        WHEN play_index IS NOT NULL 
        THEN 'PL' || printf('%05d', :game_id) || printf('%05d', CAST(play_index AS INTEGER))
        ELSE NULL 
    END AS play_key,
    Type AS event_type,
    event_detail,
    event_detail_2,
    event_successful,
    CAST(period AS INTEGER) AS period,
    event_start_min,
    event_start_sec,
    CAST(time_start_total_seconds AS INTEGER) AS time_total_seconds,
    duration,
    event_team_zone,
    :game_id AS game_id,
    datetime('now') AS _processed_timestamp
FROM stg_events_:game_id
WHERE event_index IS NOT NULL
GROUP BY event_index;

-- Create index on primary key
CREATE UNIQUE INDEX IF NOT EXISTS idx_int_events_:game_id_pk 
    ON int_events_:game_id(event_key);
CREATE INDEX IF NOT EXISTS idx_int_events_:game_id_idx 
    ON int_events_:game_id(event_index);

-- INT_EVENT_PLAYERS
-- Primary Key: event_player_key (EP prefix)
-- Foreign Keys: event_key, player_game_key
DROP TABLE IF EXISTS int_event_players_:game_id;

CREATE TABLE int_event_players_:game_id AS
SELECT
    CAST(event_index AS INTEGER) AS event_index,
    'EV' || printf('%05d', :game_id) || printf('%05d', CAST(event_index AS INTEGER)) AS event_key,
    CAST(player_game_number AS INTEGER) AS player_game_number,
    player_id,
    player_team,
    'GP' || printf('%05d', :game_id) || printf('%05d', CAST(player_game_number AS INTEGER)) AS player_game_key,
    player_role,
    play_detail1,
    play_detail_2,
    play_detail_successful,
    CASE WHEN player_role = 'event_team_player_1' THEN 1 ELSE 0 END AS is_primary_player,
    CASE WHEN player_role LIKE 'event_team%' THEN 1 ELSE 0 END AS is_event_team,
    'EP' || printf('%05d', :game_id) || printf('%05d', ROW_NUMBER() OVER (ORDER BY event_index, player_game_number)) AS event_player_key,
    :game_id AS game_id,
    datetime('now') AS _processed_timestamp
FROM stg_events_:game_id
WHERE player_game_number IS NOT NULL;

-- Create index on primary key
CREATE UNIQUE INDEX IF NOT EXISTS idx_int_ep_:game_id_pk 
    ON int_event_players_:game_id(event_player_key);
CREATE INDEX IF NOT EXISTS idx_int_ep_:game_id_event 
    ON int_event_players_:game_id(event_key);

-- INT_SHIFTS
-- Primary Key: shift_key (SH prefix)
-- Foreign Keys: game_id, strength
DROP TABLE IF EXISTS int_shifts_:game_id;

CREATE TABLE int_shifts_:game_id AS
SELECT
    CAST(shift_index AS INTEGER) AS shift_index,
    'SH' || printf('%05d', :game_id) || printf('%05d', CAST(shift_index AS INTEGER)) AS shift_key,
    CAST(Period AS INTEGER) AS period,
    shift_start_total_seconds,
    shift_end_total_seconds,
    shift_duration,
    shift_start_type,
    shift_stop_type,
    situation,
    strength,
    CAST(COALESCE(home_team_strength, 5) AS INTEGER) AS home_strength,
    CAST(COALESCE(away_team_strength, 5) AS INTEGER) AS away_strength,
    CAST(COALESCE(home_goals, 0) AS INTEGER) AS home_goals,
    CAST(COALESCE(away_goals, 0) AS INTEGER) AS away_goals,
    CAST(COALESCE(home_team_plus, 0) AS INTEGER) AS home_plus,
    CAST(COALESCE(home_team_minus, 0) AS INTEGER) AS home_minus,
    CAST(COALESCE(away_team_plus, 0) AS INTEGER) AS away_plus,
    CAST(COALESCE(away_team_minus, 0) AS INTEGER) AS away_minus,
    CAST(home_forward_1 AS INTEGER) AS home_forward_1,
    CAST(home_forward_2 AS INTEGER) AS home_forward_2,
    CAST(home_forward_3 AS INTEGER) AS home_forward_3,
    CAST(home_defense_1 AS INTEGER) AS home_defense_1,
    CAST(home_defense_2 AS INTEGER) AS home_defense_2,
    CAST(home_goalie AS INTEGER) AS home_goalie,
    CAST(away_forward_1 AS INTEGER) AS away_forward_1,
    CAST(away_forward_2 AS INTEGER) AS away_forward_2,
    CAST(away_forward_3 AS INTEGER) AS away_forward_3,
    CAST(away_defense_1 AS INTEGER) AS away_defense_1,
    CAST(away_defense_2 AS INTEGER) AS away_defense_2,
    CAST(away_goalie AS INTEGER) AS away_goalie,
    :game_id AS game_id,
    datetime('now') AS _processed_timestamp
FROM stg_shifts_:game_id
WHERE shift_index IS NOT NULL;

-- Create index on primary key
CREATE UNIQUE INDEX IF NOT EXISTS idx_int_shifts_:game_id_pk 
    ON int_shifts_:game_id(shift_key);
CREATE INDEX IF NOT EXISTS idx_int_shifts_:game_id_idx 
    ON int_shifts_:game_id(shift_index);

-- INT_GAME_PLAYERS (from gameroster)
-- Primary Key: player_game_key (GP prefix)
-- Foreign Keys: player_id, game_id
DROP TABLE IF EXISTS int_game_players_:game_id;

CREATE TABLE int_game_players_:game_id AS
SELECT
    CAST(player_game_number AS TEXT) AS player_game_number,
    player_id,
    'GP' || printf('%05d', :game_id) || printf('%05d', CAST(player_game_number AS INTEGER)) AS player_game_key,
    player_full_name,
    display_name,
    team_name AS player_team,
    team_venue AS player_venue,
    player_position AS position,
    skill_rating,
    :game_id AS game_id,
    datetime('now') AS _processed_timestamp
FROM int_fact_gameroster
WHERE game_id = :game_id;

-- Create index on primary key
CREATE UNIQUE INDEX IF NOT EXISTS idx_int_gp_:game_id_pk 
    ON int_game_players_:game_id(player_game_key);
CREATE INDEX IF NOT EXISTS idx_int_gp_:game_id_player 
    ON int_game_players_:game_id(player_id);
