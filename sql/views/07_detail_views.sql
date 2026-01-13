-- ============================================================================
-- DETAIL VIEWS - Detailed breakdowns and drill-downs
-- ============================================================================

-- Player Game Log (all games for a player)
CREATE OR REPLACE VIEW v_detail_player_game_log AS
SELECT 
    pg.player_id,
    pg.player_name,
    pg.team_name,
    pg.game_id,
    s.date,
    s.home_team_name || ' vs ' || s.away_team_name as matchup,
    pg.goals,
    pg.assists,
    pg.points,
    pg.shots,
    pg.sog,
    pg.pim,
    pg.toi,
    pg.plus_minus,
    pg.game_score
FROM fact_player_game_stats pg
JOIN dim_schedule s ON pg.game_id = s.game_id
ORDER BY pg.player_id, s.date DESC;

-- Goalie Game Log
CREATE OR REPLACE VIEW v_detail_goalie_game_log AS
SELECT 
    gg.player_id,
    gg.player_name,
    gg.team_name,
    gg.game_id,
    s.date,
    s.home_team_name || ' vs ' || s.away_team_name as matchup,
    gg.venue,
    gg.saves,
    gg.goals_against,
    gg.shots_against,
    gg.save_pct,
    gg.hd_save_pct,
    gg.is_quality_start,
    gg.overall_game_rating,
    gg.goalie_war
FROM fact_goalie_game_stats gg
JOIN dim_schedule s ON gg.game_id = s.game_id
ORDER BY gg.player_id, s.date DESC;

-- Team Game Log
CREATE OR REPLACE VIEW v_detail_team_game_log AS
SELECT 
    tg.team_id,
    tg.team_name,
    tg.game_id,
    s.date,
    CASE 
        WHEN tg.team_name = s.home_team_name THEN 'vs ' || s.away_team_name
        ELSE '@ ' || s.home_team_name
    END as opponent,
    tg.goals,
    tg.assists,
    tg.points,
    tg.shots,
    tg.sog,
    tg.pim,
    CASE 
        WHEN tg.team_name = s.home_team_name AND s.home_total_goals > s.away_total_goals THEN 'W'
        WHEN tg.team_name = s.away_team_name AND s.away_total_goals > s.home_total_goals THEN 'W'
        ELSE 'L'
    END as result
FROM fact_team_game_stats tg
JOIN dim_schedule s ON tg.game_id = s.game_id
ORDER BY tg.team_id, s.date DESC;

-- Player Period Splits (from tracking)
CREATE OR REPLACE VIEW v_detail_player_periods AS
SELECT 
    player_id,
    player_name,
    team_name,
    game_id,
    p1_goals,
    p2_goals,
    p3_goals,
    p1_assists,
    p2_assists,
    p3_assists,
    p1_shots,
    p2_shots,
    p3_shots,
    p1_toi,
    p2_toi,
    p3_toi
FROM fact_player_game_stats
WHERE game_id != 99999;

-- Goalie Period Performance
CREATE OR REPLACE VIEW v_detail_goalie_periods AS
SELECT 
    player_id,
    player_name,
    team_name,
    game_id,
    p1_saves,
    p1_goals_against,
    p1_sv_pct,
    p2_saves,
    p2_goals_against,
    p2_sv_pct,
    p3_saves,
    p3_goals_against,
    p3_sv_pct,
    best_period,
    worst_period,
    period_consistency
FROM fact_goalie_game_stats;

-- Goalie Shot Context Breakdown
CREATE OR REPLACE VIEW v_detail_goalie_shot_context AS
SELECT 
    player_id,
    player_name,
    team_name,
    game_id,
    rush_saves,
    rush_goals_against,
    rush_sv_pct,
    quick_attack_saves,
    quick_attack_ga,
    quick_attack_sv_pct,
    set_play_saves,
    set_play_ga,
    set_play_sv_pct,
    rush_pct_of_shots,
    transition_defense_rating
FROM fact_goalie_game_stats;

-- Goalie Pressure Handling
CREATE OR REPLACE VIEW v_detail_goalie_pressure AS
SELECT 
    player_id,
    player_name,
    team_name,
    game_id,
    single_shot_saves,
    multi_shot_saves,
    multi_shot_sv_pct,
    sustained_pressure_saves,
    sustained_pressure_sv_pct,
    max_sequence_faced,
    avg_sequence_length,
    sequence_survival_rate,
    pressure_handling_index
FROM fact_goalie_game_stats;

-- Player vs Opponent History
CREATE OR REPLACE VIEW v_detail_player_vs_opponent AS
SELECT 
    pg.player_id,
    pg.player_name,
    pg.team_name,
    CASE 
        WHEN pg.team_name = s.home_team_name THEN s.away_team_name
        ELSE s.home_team_name
    END as opponent,
    COUNT(*) as games_vs,
    SUM(pg.goals) as total_goals,
    SUM(pg.assists) as total_assists,
    SUM(pg.points) as total_points,
    ROUND(AVG(pg.points)::numeric, 2) as avg_points_vs
FROM fact_player_game_stats pg
JOIN dim_schedule s ON pg.game_id = s.game_id
GROUP BY pg.player_id, pg.player_name, pg.team_name,
         CASE 
            WHEN pg.team_name = s.home_team_name THEN s.away_team_name
            ELSE s.home_team_name
         END
ORDER BY pg.player_name, total_points DESC;

-- Schedule Detail with Rosters
CREATE OR REPLACE VIEW v_detail_game_roster AS
SELECT 
    s.game_id,
    s.date,
    s.home_team_name,
    s.away_team_name,
    r.player_id,
    r.player_full_name,
    r.player_position,
    r.team_name,
    r.team_venue,
    r.goals,
    r.assist,
    r.points,
    r.pim
FROM dim_schedule s
JOIN fact_gameroster r ON s.game_id = r.game_id
ORDER BY s.date DESC, r.team_venue, r.points DESC;
