-- ============================================================================
-- TRACKING ADVANCED VIEWS - Micro-stats from tracking data
-- ============================================================================

-- Event Type Summary
CREATE OR REPLACE VIEW v_tracking_event_summary AS
SELECT 
    game_id,
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT player_id) as unique_players
FROM fact_events
WHERE game_id != 99999
GROUP BY game_id, event_type
ORDER BY game_id, event_count DESC;

-- Shot Location Summary (when XY available)
CREATE OR REPLACE VIEW v_tracking_shot_locations AS
SELECT 
    game_id,
    danger_zone,
    COUNT(*) as shot_count,
    COUNT(DISTINCT player_id) as shooters
FROM fact_shot_event
WHERE game_id IS NOT NULL
GROUP BY game_id, danger_zone
ORDER BY game_id, shot_count DESC;

-- Zone Entry Success Rate by Type
CREATE OR REPLACE VIEW v_tracking_zone_entries AS
SELECT 
    z.game_id,
    z.zone_entry_type_id,
    zet.zone_entry_type_name,
    COUNT(*) as attempts,
    SUM(CASE WHEN z.is_successful = 1 THEN 1 ELSE 0 END) as successful,
    ROUND(SUM(CASE WHEN z.is_successful = 1 THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 1) as success_rate
FROM fact_zone_entries z
LEFT JOIN dim_zone_entry_type zet ON z.zone_entry_type_id = zet.zone_entry_type_id
WHERE z.game_id != 99999
GROUP BY z.game_id, z.zone_entry_type_id, zet.zone_entry_type_name
ORDER BY z.game_id, attempts DESC;

-- Player Micro Stats Summary
CREATE OR REPLACE VIEW v_tracking_player_micro AS
SELECT 
    ms.player_id,
    ms.player_name,
    ms.game_id,
    ms.zone_entries,
    ms.zone_exits,
    ms.carried_entries,
    ms.dump_ins,
    ms.successful_entries,
    ms.takeaways,
    ms.giveaways,
    ms.hits_given,
    ms.hits_taken,
    ms.blocks,
    ms.shot_attempts
FROM fact_player_micro_stats ms
WHERE ms.game_id != 99999;

-- Faceoff Summary by Player
CREATE OR REPLACE VIEW v_tracking_faceoffs AS
SELECT 
    player_id,
    game_id,
    COUNT(*) as total_faceoffs,
    SUM(CASE WHEN is_win = 1 THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN is_win = 0 THEN 1 ELSE 0 END) as losses,
    ROUND(SUM(CASE WHEN is_win = 1 THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(*), 0) * 100, 1) as fo_pct
FROM fact_faceoffs
WHERE game_id != 99999
GROUP BY player_id, game_id
ORDER BY total_faceoffs DESC;

-- Scoring Chances Summary
CREATE OR REPLACE VIEW v_tracking_scoring_chances AS
SELECT 
    game_id,
    team_name,
    COUNT(*) as total_chances,
    SUM(CASE WHEN is_goal = 1 THEN 1 ELSE 0 END) as converted,
    ROUND(SUM(CASE WHEN is_goal = 1 THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(*), 0) * 100, 1) as conversion_rate
FROM fact_scoring_chances
WHERE game_id != 99999
GROUP BY game_id, team_name
ORDER BY game_id, total_chances DESC;

-- Shift Quality Summary
CREATE OR REPLACE VIEW v_tracking_shift_quality AS
SELECT 
    player_id,
    game_id,
    COUNT(*) as total_shifts,
    ROUND(AVG(shift_duration)::numeric, 1) as avg_shift_duration,
    ROUND(AVG(shift_quality_score)::numeric, 2) as avg_shift_quality,
    SUM(scoring_chances_for) as total_chances_for,
    SUM(scoring_chances_against) as total_chances_against
FROM fact_shift_quality
WHERE game_id != 99999
GROUP BY player_id, game_id
ORDER BY avg_shift_quality DESC;

-- Save Type Breakdown
CREATE OR REPLACE VIEW v_tracking_save_types AS
SELECT 
    goalie_id as player_id,
    game_id,
    save_type,
    COUNT(*) as save_count
FROM fact_saves
WHERE game_id != 99999
GROUP BY goalie_id, game_id, save_type
ORDER BY game_id, save_count DESC;
