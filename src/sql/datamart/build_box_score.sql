-- =============================================================================
-- DATAMART: BUILD BOX SCORE
-- =============================================================================
-- Creates temporary box score table for game :game_id
-- =============================================================================

-- BASE: Start with all players in the game
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
FROM int_game_players_:game_id;

-- SCORING STATS
DROP TABLE IF EXISTS _tmp_scoring_:game_id;

CREATE TABLE _tmp_scoring_:game_id AS
SELECT
    ep.player_game_number,
    SUM(CASE WHEN ep.is_primary_player = 1 AND e.event_detail = 'Goal_Scored' THEN 1 ELSE 0 END) AS goals,
    SUM(CASE WHEN ep.play_detail1 = 'AssistPrimary' THEN 1 ELSE 0 END) AS assists_primary,
    SUM(CASE WHEN ep.play_detail1 = 'AssistSecondary' THEN 1 ELSE 0 END) AS assists_secondary
FROM int_event_players_:game_id ep
JOIN int_events_:game_id e ON ep.event_index = e.event_index
GROUP BY ep.player_game_number;

-- SHOOTING STATS
DROP TABLE IF EXISTS _tmp_shooting_:game_id;

CREATE TABLE _tmp_shooting_:game_id AS
SELECT
    ep.player_game_number,
    SUM(CASE WHEN ep.is_primary_player = 1 AND e.event_type = 'Shot' THEN 1 ELSE 0 END) AS shots,
    SUM(CASE WHEN ep.is_primary_player = 1 AND e.event_detail IN ('Shot_OnNetSaved', 'Shot_Goal') THEN 1 ELSE 0 END) AS shots_on_goal
FROM int_event_players_:game_id ep
JOIN int_events_:game_id e ON ep.event_index = e.event_index
GROUP BY ep.player_game_number;

-- PASSING STATS
DROP TABLE IF EXISTS _tmp_passing_:game_id;

CREATE TABLE _tmp_passing_:game_id AS
SELECT
    ep.player_game_number,
    SUM(CASE WHEN ep.is_primary_player = 1 AND e.event_type = 'Pass' THEN 1 ELSE 0 END) AS passes,
    SUM(CASE WHEN ep.is_primary_player = 1 AND e.event_detail = 'Pass_Completed' THEN 1 ELSE 0 END) AS passes_completed
FROM int_event_players_:game_id ep
JOIN int_events_:game_id e ON ep.event_index = e.event_index
GROUP BY ep.player_game_number;

-- TURNOVER STATS
DROP TABLE IF EXISTS _tmp_turnovers_:game_id;

CREATE TABLE _tmp_turnovers_:game_id AS
SELECT
    ep.player_game_number,
    SUM(CASE WHEN ep.is_primary_player = 1 AND e.event_detail = 'Turnover_Giveaway' THEN 1 ELSE 0 END) AS giveaways,
    SUM(CASE WHEN ep.is_primary_player = 1 AND e.event_detail = 'Turnover_Takeaway' THEN 1 ELSE 0 END) AS takeaways
FROM int_event_players_:game_id ep
JOIN int_events_:game_id e ON ep.event_index = e.event_index
GROUP BY ep.player_game_number;

-- FACEOFF STATS
DROP TABLE IF EXISTS _tmp_faceoffs_:game_id;

CREATE TABLE _tmp_faceoffs_:game_id AS
SELECT
    ep.player_game_number,
    SUM(CASE WHEN ep.is_primary_player = 1 AND e.event_type = 'Faceoff' THEN 1 ELSE 0 END) AS faceoffs,
    SUM(CASE WHEN ep.is_primary_player = 1 AND e.event_type = 'Faceoff' AND e.event_successful = 's' THEN 1 ELSE 0 END) AS faceoff_wins
FROM int_event_players_:game_id ep
JOIN int_events_:game_id e ON ep.event_index = e.event_index
GROUP BY ep.player_game_number;

-- MICRO-STATS (deduplicated by linked_event_index)
DROP TABLE IF EXISTS _tmp_microstats_:game_id;

CREATE TABLE _tmp_microstats_:game_id AS
SELECT
    ep.player_game_number,
    COUNT(DISTINCT CASE WHEN ep.play_detail1 = 'StickCheck' THEN COALESCE(e.linked_event_index, e.event_index || '_s') END) AS stick_checks,
    COUNT(DISTINCT CASE WHEN ep.play_detail1 = 'PokeCheck' THEN COALESCE(e.linked_event_index, e.event_index || '_s') END) AS poke_checks,
    COUNT(DISTINCT CASE WHEN ep.play_detail1 = 'BlockedShot' THEN COALESCE(e.linked_event_index, e.event_index || '_s') END) AS blocked_shots,
    COUNT(DISTINCT CASE WHEN ep.play_detail1 = 'Backcheck' THEN COALESCE(e.linked_event_index, e.event_index || '_s') END) AS backchecks,
    COUNT(DISTINCT CASE WHEN ep.play_detail1 = 'Deke' THEN COALESCE(e.linked_event_index, e.event_index || '_s') END) AS dekes,
    COUNT(DISTINCT CASE WHEN ep.play_detail1 = 'PuckRecovery' THEN COALESCE(e.linked_event_index, e.event_index || '_s') END) AS puck_recoveries
FROM int_event_players_:game_id ep
JOIN int_events_:game_id e ON ep.event_index = e.event_index
GROUP BY ep.player_game_number;

-- COMBINE INTO BOX SCORE
DROP TABLE IF EXISTS _tmp_box_score_:game_id;

CREATE TABLE _tmp_box_score_:game_id AS
SELECT
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
    
    COALESCE(sc.goals, 0) AS goals,
    COALESCE(sc.assists_primary, 0) AS assists_primary,
    COALESCE(sc.assists_secondary, 0) AS assists_secondary,
    COALESCE(sc.assists_primary, 0) + COALESCE(sc.assists_secondary, 0) AS assists,
    COALESCE(sc.goals, 0) + COALESCE(sc.assists_primary, 0) + COALESCE(sc.assists_secondary, 0) AS points,
    
    COALESCE(sh.shots, 0) AS shots,
    COALESCE(sh.shots_on_goal, 0) AS shots_on_goal,
    
    COALESCE(p.passes, 0) AS passes,
    COALESCE(p.passes_completed, 0) AS passes_completed,
    
    COALESCE(t.giveaways, 0) AS giveaways,
    COALESCE(t.takeaways, 0) AS takeaways,
    
    COALESCE(f.faceoffs, 0) AS faceoffs,
    COALESCE(f.faceoff_wins, 0) AS faceoff_wins,
    
    COALESCE(m.stick_checks, 0) AS stick_checks,
    COALESCE(m.poke_checks, 0) AS poke_checks,
    COALESCE(m.blocked_shots, 0) AS blocked_shots,
    COALESCE(m.backchecks, 0) AS backchecks,
    COALESCE(m.dekes, 0) AS dekes,
    COALESCE(m.puck_recoveries, 0) AS puck_recoveries,
    
    1 AS is_tracked,
    datetime('now') AS _processed_timestamp

FROM _tmp_box_base_:game_id b
LEFT JOIN _tmp_scoring_:game_id sc ON b.player_game_number = sc.player_game_number
LEFT JOIN _tmp_shooting_:game_id sh ON b.player_game_number = sh.player_game_number
LEFT JOIN _tmp_passing_:game_id p ON b.player_game_number = p.player_game_number
LEFT JOIN _tmp_turnovers_:game_id t ON b.player_game_number = t.player_game_number
LEFT JOIN _tmp_faceoffs_:game_id f ON b.player_game_number = f.player_game_number
LEFT JOIN _tmp_microstats_:game_id m ON b.player_game_number = m.player_game_number;

-- CLEANUP TEMP TABLES
DROP TABLE IF EXISTS _tmp_box_base_:game_id;
DROP TABLE IF EXISTS _tmp_scoring_:game_id;
DROP TABLE IF EXISTS _tmp_shooting_:game_id;
DROP TABLE IF EXISTS _tmp_passing_:game_id;
DROP TABLE IF EXISTS _tmp_turnovers_:game_id;
DROP TABLE IF EXISTS _tmp_faceoffs_:game_id;
DROP TABLE IF EXISTS _tmp_microstats_:game_id;
