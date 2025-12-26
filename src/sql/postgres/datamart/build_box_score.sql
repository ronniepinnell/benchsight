-- =============================================================================
-- POSTGRESQL: BUILD BOX SCORE
-- =============================================================================
-- File: src/sql/postgres/datamart/build_box_score.sql
--
-- PURPOSE:
--     Build comprehensive box score from intermediate tables.
--     Aggregates all stats per player per game.
--
-- GAME ID:
--     Replace :game_id with actual game ID before execution.
-- =============================================================================

-- =============================================================================
-- STEP 1: Base player list from game roster
-- =============================================================================

DROP TABLE IF EXISTS _tmp_box_base_:game_id;

CREATE TABLE _tmp_box_base_:game_id AS
SELECT
    player_game_key,
    player_game_number,
    player_id,
    player_full_name,
    display_name,
    player_team,
    player_venue,
    position,
    skill_rating,
    game_id
FROM intermediate.int_game_players_:game_id;

-- =============================================================================
-- STEP 2: Scoring statistics
-- =============================================================================

DROP TABLE IF EXISTS _tmp_scoring_:game_id;

CREATE TABLE _tmp_scoring_:game_id AS
SELECT
    ep.player_game_number,
    
    -- Goals: primary player on Goal_Scored events
    SUM(CASE 
        WHEN ep.is_primary_player = 1 AND e.event_detail = 'Goal_Scored' 
        THEN 1 ELSE 0 
    END) AS goals,
    
    -- Primary assists
    SUM(CASE WHEN ep.play_detail1 = 'AssistPrimary' THEN 1 ELSE 0 END) AS assists_primary,
    
    -- Secondary assists
    SUM(CASE WHEN ep.play_detail1 = 'AssistSecondary' THEN 1 ELSE 0 END) AS assists_secondary

FROM intermediate.int_event_players_:game_id ep
JOIN intermediate.int_events_:game_id e ON ep.event_index = e.event_index
GROUP BY ep.player_game_number;

-- =============================================================================
-- STEP 3: Shooting statistics
-- =============================================================================

DROP TABLE IF EXISTS _tmp_shooting_:game_id;

CREATE TABLE _tmp_shooting_:game_id AS
SELECT
    ep.player_game_number,
    
    -- All shots
    SUM(CASE 
        WHEN ep.is_primary_player = 1 AND e.event_type = 'Shot' 
        THEN 1 ELSE 0 
    END) AS shots,
    
    -- Shots on goal (saved or scored)
    SUM(CASE 
        WHEN ep.is_primary_player = 1 
         AND e.event_detail IN ('Shot_OnNetSaved', 'Shot_Goal', 'Goal_Scored')
        THEN 1 ELSE 0 
    END) AS shots_on_goal

FROM intermediate.int_event_players_:game_id ep
JOIN intermediate.int_events_:game_id e ON ep.event_index = e.event_index
GROUP BY ep.player_game_number;

-- =============================================================================
-- STEP 4: Passing statistics
-- =============================================================================

DROP TABLE IF EXISTS _tmp_passing_:game_id;

CREATE TABLE _tmp_passing_:game_id AS
SELECT
    ep.player_game_number,
    
    -- Total passes
    SUM(CASE 
        WHEN ep.is_primary_player = 1 AND e.event_type = 'Pass' 
        THEN 1 ELSE 0 
    END) AS passes,
    
    -- Completed passes
    SUM(CASE 
        WHEN ep.is_primary_player = 1 AND e.event_detail = 'Pass_Completed'
        THEN 1 ELSE 0 
    END) AS passes_completed

FROM intermediate.int_event_players_:game_id ep
JOIN intermediate.int_events_:game_id e ON ep.event_index = e.event_index
GROUP BY ep.player_game_number;

-- =============================================================================
-- STEP 5: Turnover statistics
-- =============================================================================

DROP TABLE IF EXISTS _tmp_turnovers_:game_id;

CREATE TABLE _tmp_turnovers_:game_id AS
SELECT
    ep.player_game_number,
    
    -- Giveaways (bad)
    SUM(CASE 
        WHEN ep.is_primary_player = 1 AND e.event_detail = 'Turnover_Giveaway'
        THEN 1 ELSE 0 
    END) AS giveaways,
    
    -- Takeaways (good)
    SUM(CASE 
        WHEN ep.is_primary_player = 1 AND e.event_detail = 'Turnover_Takeaway'
        THEN 1 ELSE 0 
    END) AS takeaways

FROM intermediate.int_event_players_:game_id ep
JOIN intermediate.int_events_:game_id e ON ep.event_index = e.event_index
GROUP BY ep.player_game_number;

-- =============================================================================
-- STEP 6: Faceoff statistics
-- =============================================================================

DROP TABLE IF EXISTS _tmp_faceoffs_:game_id;

CREATE TABLE _tmp_faceoffs_:game_id AS
SELECT
    ep.player_game_number,
    
    -- Total faceoffs taken
    SUM(CASE 
        WHEN ep.is_primary_player = 1 AND e.event_type = 'Faceoff'
        THEN 1 ELSE 0 
    END) AS faceoffs,
    
    -- Faceoff wins
    SUM(CASE 
        WHEN ep.is_primary_player = 1 
         AND e.event_type = 'Faceoff' 
         AND e.event_successful = 's'
        THEN 1 ELSE 0 
    END) AS faceoff_wins

FROM intermediate.int_event_players_:game_id ep
JOIN intermediate.int_events_:game_id e ON ep.event_index = e.event_index
GROUP BY ep.player_game_number;

-- =============================================================================
-- STEP 7: Micro-stats (deduplicated by linked_event_index)
-- =============================================================================
-- WHY COUNT DISTINCT: Some play details appear on multiple rows for same play.
--                     Use linked_event_index to deduplicate.

DROP TABLE IF EXISTS _tmp_microstats_:game_id;

CREATE TABLE _tmp_microstats_:game_id AS
SELECT
    ep.player_game_number,
    
    -- Stick checks
    COUNT(DISTINCT CASE 
        WHEN ep.play_detail1 = 'StickCheck' 
        THEN COALESCE(e.linked_event_index::TEXT, e.event_index::TEXT || '_s')
    END) AS stick_checks,
    
    -- Poke checks
    COUNT(DISTINCT CASE 
        WHEN ep.play_detail1 = 'PokeCheck'
        THEN COALESCE(e.linked_event_index::TEXT, e.event_index::TEXT || '_p')
    END) AS poke_checks,
    
    -- Blocked shots
    COUNT(DISTINCT CASE 
        WHEN ep.play_detail1 = 'BlockedShot'
        THEN COALESCE(e.linked_event_index::TEXT, e.event_index::TEXT || '_b')
    END) AS blocked_shots,
    
    -- Backchecks
    COUNT(DISTINCT CASE 
        WHEN ep.play_detail1 = 'Backcheck'
        THEN COALESCE(e.linked_event_index::TEXT, e.event_index::TEXT || '_bc')
    END) AS backchecks,
    
    -- Dekes
    COUNT(DISTINCT CASE 
        WHEN ep.play_detail1 = 'Deke'
        THEN COALESCE(e.linked_event_index::TEXT, e.event_index::TEXT || '_d')
    END) AS dekes,
    
    -- Puck recoveries
    COUNT(DISTINCT CASE 
        WHEN ep.play_detail1 = 'PuckRecovery'
        THEN COALESCE(e.linked_event_index::TEXT, e.event_index::TEXT || '_pr')
    END) AS puck_recoveries

FROM intermediate.int_event_players_:game_id ep
JOIN intermediate.int_events_:game_id e ON ep.event_index = e.event_index
GROUP BY ep.player_game_number;

-- =============================================================================
-- STEP 8: Combine all stats into box score
-- =============================================================================

DROP TABLE IF EXISTS _tmp_box_score_:game_id;

CREATE TABLE _tmp_box_score_:game_id AS
SELECT
    -- Player identification
    b.player_game_key,
    b.player_game_number,
    b.player_id,
    b.player_full_name,
    b.display_name,
    b.player_team,
    b.player_venue,
    b.position,
    b.skill_rating,
    b.game_id,
    
    -- Scoring
    COALESCE(sc.goals, 0) AS goals,
    COALESCE(sc.assists_primary, 0) AS assists_primary,
    COALESCE(sc.assists_secondary, 0) AS assists_secondary,
    COALESCE(sc.assists_primary, 0) + COALESCE(sc.assists_secondary, 0) AS assists,
    COALESCE(sc.goals, 0) + COALESCE(sc.assists_primary, 0) + COALESCE(sc.assists_secondary, 0) AS points,
    
    -- Shooting
    COALESCE(sh.shots, 0) AS shots,
    COALESCE(sh.shots_on_goal, 0) AS shots_on_goal,
    
    -- Passing
    COALESCE(p.passes, 0) AS passes,
    COALESCE(p.passes_completed, 0) AS passes_completed,
    
    -- Turnovers
    COALESCE(t.giveaways, 0) AS giveaways,
    COALESCE(t.takeaways, 0) AS takeaways,
    
    -- Faceoffs
    COALESCE(f.faceoffs, 0) AS faceoffs,
    COALESCE(f.faceoff_wins, 0) AS faceoff_wins,
    
    -- Micro-stats
    COALESCE(m.stick_checks, 0) AS stick_checks,
    COALESCE(m.poke_checks, 0) AS poke_checks,
    COALESCE(m.blocked_shots, 0) AS blocked_shots,
    COALESCE(m.backchecks, 0) AS backchecks,
    COALESCE(m.dekes, 0) AS dekes,
    COALESCE(m.puck_recoveries, 0) AS puck_recoveries,
    
    -- Flag for tracked games
    TRUE AS is_tracked,
    
    -- Metadata
    NOW() AS _processed_timestamp

FROM _tmp_box_base_:game_id b
LEFT JOIN _tmp_scoring_:game_id sc ON b.player_game_number = sc.player_game_number
LEFT JOIN _tmp_shooting_:game_id sh ON b.player_game_number = sh.player_game_number
LEFT JOIN _tmp_passing_:game_id p ON b.player_game_number = p.player_game_number
LEFT JOIN _tmp_turnovers_:game_id t ON b.player_game_number = t.player_game_number
LEFT JOIN _tmp_faceoffs_:game_id f ON b.player_game_number = f.player_game_number
LEFT JOIN _tmp_microstats_:game_id m ON b.player_game_number = m.player_game_number;

-- =============================================================================
-- STEP 9: Cleanup temporary tables
-- =============================================================================

DROP TABLE IF EXISTS _tmp_box_base_:game_id;
DROP TABLE IF EXISTS _tmp_scoring_:game_id;
DROP TABLE IF EXISTS _tmp_shooting_:game_id;
DROP TABLE IF EXISTS _tmp_passing_:game_id;
DROP TABLE IF EXISTS _tmp_turnovers_:game_id;
DROP TABLE IF EXISTS _tmp_faceoffs_:game_id;
DROP TABLE IF EXISTS _tmp_microstats_:game_id;
