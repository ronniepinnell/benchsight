-- ============================================================================
-- ML PREDICTIONS VIEWS
-- Pre-computed ML model results stored in database
-- Created: 2026-01-15
-- Purpose: Fast access to ML predictions without real-time inference
-- ============================================================================

-- ============================================================================
-- SECTION 1: GAME OUTCOME PREDICTIONS
-- ============================================================================

-- Game outcome predictions (pre-computed before each game)
CREATE OR REPLACE VIEW v_ml_game_predictions AS
SELECT 
    s.game_id,
    s.date,
    s.season_id,
    s.season,
    s.home_team_id,
    s.home_team_name,
    s.away_team_id,
    s.away_team_name,
    
    -- Predictions
    COALESCE(p.home_win_probability, 0.5) as home_win_probability,
    COALESCE(p.away_win_probability, 0.5) as away_win_probability,
    COALESCE(p.predicted_home_goals, 0) as predicted_home_goals,
    COALESCE(p.predicted_away_goals, 0) as predicted_away_goals,
    COALESCE(p.predicted_total_goals, 0) as predicted_total_goals,
    COALESCE(p.over_under_line, 0) as over_under_line,
    COALESCE(p.over_probability, 0.5) as over_probability,
    COALESCE(p.under_probability, 0.5) as under_probability,
    
    -- Confidence & Factors
    COALESCE(p.prediction_confidence, 0) as prediction_confidence,
    COALESCE(p.key_factors, '') as key_factors,
    COALESCE(p.model_version, '1.0.0') as model_version,
    COALESCE(p.predicted_at, NOW()) as predicted_at,
    
    -- Actual Results (for validation)
    s.home_total_goals as actual_home_goals,
    s.away_total_goals as actual_away_goals,
    CASE 
        WHEN s.home_total_goals > s.away_total_goals THEN 'Home'
        WHEN s.away_total_goals > s.home_total_goals THEN 'Away'
        ELSE 'Tie'
    END as actual_winner,
    
    -- Prediction Accuracy (if game completed)
    CASE 
        WHEN s.home_total_goals IS NOT NULL AND s.away_total_goals IS NOT NULL THEN
            CASE 
                WHEN (s.home_total_goals > s.away_total_goals AND p.home_win_probability > 0.5) OR
                     (s.away_total_goals > s.home_total_goals AND p.away_win_probability > 0.5) OR
                     (s.home_total_goals = s.away_total_goals AND p.home_win_probability BETWEEN 0.45 AND 0.55)
                THEN true
                ELSE false
            END
        ELSE NULL
    END as prediction_correct
    
FROM dim_schedule s
LEFT JOIN ml_game_predictions p ON s.game_id = p.game_id
WHERE s.date >= CURRENT_DATE - INTERVAL '30 days'  -- Last 30 days + future
ORDER BY s.date DESC, s.game_id DESC;

-- ============================================================================
-- SECTION 2: PLAYER SEASON PROJECTIONS
-- ============================================================================

-- Player season projections (updated daily)
CREATE OR REPLACE VIEW v_ml_player_season_projections AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    
    -- Current Stats
    p.games_played as current_games_played,
    p.goals as current_goals,
    p.assists as current_assists,
    p.points as current_points,
    p.war as current_war,
    p.gar_total as current_gar,
    
    -- Projected Stats
    COALESCE(ml.projected_games_played, p.games_played) as projected_games_played,
    COALESCE(ml.projected_goals, p.goals) as projected_goals,
    COALESCE(ml.projected_assists, p.assists) as projected_assists,
    COALESCE(ml.projected_points, p.points) as projected_points,
    COALESCE(ml.projected_war, p.war) as projected_war,
    COALESCE(ml.projected_gar, p.gar_total) as projected_gar,
    
    -- Remaining Projections
    COALESCE(ml.projected_goals, p.goals) - p.goals as goals_remaining,
    COALESCE(ml.projected_assists, p.assists) - p.assists as assists_remaining,
    COALESCE(ml.projected_points, p.points) - p.points as points_remaining,
    COALESCE(ml.projected_war, p.war) - p.war as war_remaining,
    
    -- Milestone Probabilities
    COALESCE(ml.probability_50_goals, 0) as probability_50_goals,
    COALESCE(ml.probability_100_points, 0) as probability_100_points,
    COALESCE(ml.probability_hat_trick, 0) as probability_hat_trick,
    
    -- Confidence Intervals
    COALESCE(ml.goals_lower_bound, ml.projected_goals * 0.9) as goals_lower_bound,
    COALESCE(ml.goals_upper_bound, ml.projected_goals * 1.1) as goals_upper_bound,
    COALESCE(ml.points_lower_bound, ml.projected_points * 0.9) as points_lower_bound,
    COALESCE(ml.points_upper_bound, ml.projected_points * 1.1) as points_upper_bound,
    
    -- Percentile Projections
    COALESCE(ml.projected_goals_percentile, 50) as projected_goals_percentile,
    COALESCE(ml.projected_points_percentile, 50) as projected_points_percentile,
    COALESCE(ml.projected_war_percentile, 50) as projected_war_percentile,
    
    -- Model Info
    COALESCE(ml.model_version, '1.0.0') as model_version,
    COALESCE(ml.projected_at, NOW()) as projected_at,
    COALESCE(ml.prediction_confidence, 0) as prediction_confidence
    
FROM fact_player_season_stats_basic p
LEFT JOIN ml_player_projections ml 
    ON p.player_id = ml.player_id 
    AND p.season_id = ml.season_id
WHERE p.game_type = 'All'
ORDER BY COALESCE(ml.projected_points, p.points) DESC;

-- ============================================================================
-- SECTION 3: PLAYER SIMILARITY & COMPARISONS
-- ============================================================================

-- Similar players (pre-computed similarity scores)
CREATE OR REPLACE VIEW v_ml_similar_players AS
SELECT 
    p1.player_id as player_id,
    p1.player_name as player_name,
    p2.player_id as similar_player_id,
    p2.player_name as similar_player_name,
    s.similarity_score,
    s.rank as similarity_rank,
    
    -- Key Similarities
    s.similar_stats as similar_stats,  -- JSON array of similar stat names
    s.different_stats as different_stats,  -- JSON array of different stat names
    
    -- Comparison Stats
    p1.points as player_points,
    p2.points as similar_player_points,
    p1.goals as player_goals,
    p2.goals as similar_player_goals,
    p1.war as player_war,
    p2.war as similar_player_war,
    
    -- Model Info
    s.model_version,
    s.computed_at
    
FROM ml_player_similarity s
JOIN dim_player p1 ON s.player_id = p1.player_id
JOIN dim_player p2 ON s.similar_player_id = p2.player_id
WHERE s.similarity_score >= 70  -- Only show high similarity matches
ORDER BY s.player_id, s.similarity_score DESC;

-- Player archetype classification
CREATE OR REPLACE VIEW v_ml_player_archetypes AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    
    -- Archetype Classification
    COALESCE(a.primary_archetype, 'Unknown') as primary_archetype,
    COALESCE(a.secondary_archetype, 'None') as secondary_archetype,
    COALESCE(a.archetype_confidence, 0) as archetype_confidence,
    
    -- Archetype Scores (0-100)
    COALESCE(a.elite_scorer_score, 0) as elite_scorer_score,
    COALESCE(a.playmaker_score, 0) as playmaker_score,
    COALESCE(a.two_way_score, 0) as two_way_score,
    COALESCE(a.defensive_specialist_score, 0) as defensive_specialist_score,
    COALESCE(a.power_forward_score, 0) as power_forward_score,
    COALESCE(a.speedster_score, 0) as speedster_score,
    COALESCE(a.clutch_performer_score, 0) as clutch_performer_score,
    
    -- Model Info
    a.model_version,
    a.classified_at
    
FROM fact_player_season_stats_basic p
LEFT JOIN ml_player_archetypes a 
    ON p.player_id = a.player_id 
    AND p.season_id = a.season_id
WHERE p.game_type = 'All'
ORDER BY p.points DESC;

-- ============================================================================
-- SECTION 4: LINE CHEMISTRY
-- ============================================================================

-- Line chemistry scores (pre-computed for common line combinations)
CREATE OR REPLACE VIEW v_ml_line_chemistry AS
SELECT 
    l.line_id,
    l.player1_id,
    p1.player_name as player1_name,
    l.player2_id,
    p2.player_name as player2_name,
    l.player3_id,
    p3.player_name as player3_name,
    l.team_id,
    t.team_name,
    l.season_id,
    l.season,
    
    -- Chemistry Scores
    l.chemistry_score,  -- Overall chemistry (0-100)
    l.offensive_chemistry,  -- Offensive compatibility
    l.defensive_chemistry,  -- Defensive compatibility
    l.transition_chemistry,  -- Transition play compatibility
    
    -- Expected Performance Together
    l.expected_goals_together,
    l.expected_cf_pct_together,
    l.expected_xg_together,
    
    -- Historical Performance
    l.games_together,
    l.toi_together_seconds,
    l.actual_goals_together,
    l.actual_cf_pct_together,
    
    -- Optimal Deployment
    l.optimal_strength,  -- '5v5', 'PP', 'PK', 'All'
    l.optimal_game_state,  -- 'Leading', 'Trailing', 'Tied', 'All'
    
    -- Model Info
    l.model_version,
    l.computed_at
    
FROM ml_line_chemistry l
LEFT JOIN dim_player p1 ON l.player1_id = p1.player_id
LEFT JOIN dim_player p2 ON l.player2_id = p2.player_id
LEFT JOIN dim_player p3 ON l.player3_id = p3.player_id
LEFT JOIN dim_team t ON l.team_id = t.team_id
WHERE l.chemistry_score >= 60  -- Only show good chemistry
ORDER BY l.chemistry_score DESC;

-- ============================================================================
-- SECTION 5: GOALIE PREDICTIONS
-- ============================================================================

-- Goalie performance predictions
CREATE OR REPLACE VIEW v_ml_goalie_predictions AS
SELECT 
    g.player_id,
    g.player_name,
    g.team_id,
    g.team_name,
    g.season_id,
    g.season,
    
    -- Current Stats
    g.games_played as current_games_played,
    g.save_pct as current_save_pct,
    g.gaa as current_gaa,
    g.wins as current_wins,
    
    -- Projected Stats
    COALESCE(ml.projected_games_played, g.games_played) as projected_games_played,
    COALESCE(ml.projected_save_pct, g.save_pct) as projected_save_pct,
    COALESCE(ml.projected_gaa, g.gaa) as projected_gaa,
    COALESCE(ml.projected_wins, g.wins) as projected_wins,
    COALESCE(ml.projected_shutouts, 0) as projected_shutouts,
    
    -- Probabilities
    COALESCE(ml.probability_quality_start, 0) as probability_quality_start,
    COALESCE(ml.probability_shutout, 0) as probability_shutout,
    COALESCE(ml.probability_30_saves, 0) as probability_30_saves,
    
    -- Next Game Prediction
    COALESCE(ml.next_game_save_pct, g.save_pct) as next_game_save_pct,
    COALESCE(ml.next_game_gaa, g.gaa) as next_game_gaa,
    COALESCE(ml.next_game_win_probability, 0.5) as next_game_win_probability,
    
    -- Model Info
    ml.model_version,
    ml.projected_at
    
FROM fact_goalie_season_stats_basic g
LEFT JOIN ml_goalie_predictions ml 
    ON g.player_id = ml.player_id 
    AND g.season_id = ml.season_id
ORDER BY COALESCE(ml.projected_save_pct, g.save_pct) DESC;

-- ============================================================================
-- SECTION 6: TEAM PREDICTIONS
-- ============================================================================

-- Team playoff probability and championship odds
CREATE OR REPLACE VIEW v_ml_team_predictions AS
SELECT 
    t.team_id,
    t.team_name,
    t.season_id,
    t.season,
    
    -- Current Standings
    t.games_played,
    t.wins,
    t.losses,
    t.points,
    t.goal_diff,
    
    -- Playoff Predictions
    COALESCE(ml.playoff_probability, 0) as playoff_probability,
    COALESCE(ml.seed_probability_1, 0) as seed_probability_1,
    COALESCE(ml.seed_probability_2, 0) as seed_probability_2,
    COALESCE(ml.seed_probability_3, 0) as seed_probability_3,
    COALESCE(ml.seed_probability_4, 0) as seed_probability_4,
    COALESCE(ml.most_likely_seed, 0) as most_likely_seed,
    
    -- Championship Predictions
    COALESCE(ml.championship_probability, 0) as championship_probability,
    COALESCE(ml.conference_final_probability, 0) as conference_final_probability,
    COALESCE(ml.round1_win_probability, 0) as round1_win_probability,
    COALESCE(ml.round2_win_probability, 0) as round2_win_probability,
    
    -- Projected Final Standings
    COALESCE(ml.projected_wins, t.wins) as projected_wins,
    COALESCE(ml.projected_points, t.points) as projected_points,
    COALESCE(ml.projected_goal_diff, t.goal_diff) as projected_goal_diff,
    
    -- Strength of Schedule
    COALESCE(ml.remaining_sos_difficulty, 0) as remaining_sos_difficulty,  -- 0-100, higher = harder
    COALESCE(ml.games_remaining, 0) as games_remaining,
    
    -- Model Info
    ml.model_version,
    ml.projected_at
    
FROM fact_team_season_stats_basic t
LEFT JOIN ml_team_predictions ml 
    ON t.team_id = ml.team_id 
    AND t.season_id = ml.season_id
WHERE t.game_type = 'All'
ORDER BY COALESCE(ml.championship_probability, 0) DESC, t.points DESC;

-- ============================================================================
-- SECTION 7: BREAKOUT PLAYER DETECTION
-- ============================================================================

-- Players likely to break out (updated weekly)
CREATE OR REPLACE VIEW v_ml_breakout_players AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    
    -- Current Stats
    p.games_played,
    p.goals,
    p.assists,
    p.points,
    p.war,
    
    -- Breakout Metrics
    COALESCE(b.breakout_probability, 0) as breakout_probability,  -- 0-100
    COALESCE(b.breakout_timeline_weeks, 0) as breakout_timeline_weeks,
    COALESCE(b.expected_improvement_pct, 0) as expected_improvement_pct,
    
    -- Underlying Indicators
    COALESCE(b.xg_trend, 0) as xg_trend,  -- Improving xG
    COALESCE(b.cf_pct_trend, 0) as cf_pct_trend,  -- Improving CF%
    COALESCE(b.toi_trend, 0) as toi_trend,  -- Increasing TOI
    COALESCE(b.shot_quality_trend, 0) as shot_quality_trend,  -- Better shot locations
    
    -- Projected Breakout Stats
    COALESCE(b.projected_goals_after_breakout, p.goals) as projected_goals_after_breakout,
    COALESCE(b.projected_points_after_breakout, p.points) as projected_points_after_breakout,
    
    -- Model Info
    b.model_version,
    b.detected_at
    
FROM fact_player_season_stats_basic p
LEFT JOIN ml_breakout_players b 
    ON p.player_id = b.player_id 
    AND p.season_id = b.season_id
WHERE p.game_type = 'All'
  AND COALESCE(b.breakout_probability, 0) >= 50  -- Only show likely breakouts
ORDER BY b.breakout_probability DESC, p.points ASC;  -- Lower current points = bigger breakout potential

-- ============================================================================
-- SECTION 8: INJURY RISK ASSESSMENT
-- ============================================================================

-- Player injury risk scores (updated daily)
CREATE OR REPLACE VIEW v_ml_injury_risk AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    
    -- Injury Risk
    COALESCE(i.injury_risk_score, 0) as injury_risk_score,  -- 0-100, higher = more risk
    COALESCE(i.risk_category, 'Low') as risk_category,  -- 'Low', 'Medium', 'High', 'Critical'
    COALESCE(i.most_likely_injury_type, 'Unknown') as most_likely_injury_type,
    
    -- Risk Factors
    COALESCE(i.age_risk_factor, 0) as age_risk_factor,
    COALESCE(i.games_played_risk_factor, 0) as games_played_risk_factor,
    COALESCE(i.toi_risk_factor, 0) as toi_risk_factor,
    COALESCE(i.physical_play_risk_factor, 0) as physical_play_risk_factor,
    COALESCE(i.injury_history_risk_factor, 0) as injury_history_risk_factor,
    COALESCE(i.fatigue_risk_factor, 0) as fatigue_risk_factor,
    
    -- Recommendations
    COALESCE(i.recommended_rest_days, 0) as recommended_rest_days,
    COALESCE(i.load_management_suggestion, '') as load_management_suggestion,
    
    -- Model Info
    i.model_version,
    i.assessed_at
    
FROM fact_player_season_stats_basic p
LEFT JOIN ml_injury_risk i 
    ON p.player_id = i.player_id 
    AND p.season_id = i.season_id
WHERE p.game_type = 'All'
ORDER BY i.injury_risk_score DESC;

-- ============================================================================
-- SECTION 9: REAL-TIME GAME PREDICTIONS (For Live Games)
-- ============================================================================

-- Real-time win probability (updated during live games)
CREATE OR REPLACE VIEW v_ml_live_game_predictions AS
SELECT 
    s.game_id,
    s.date,
    s.home_team_id,
    s.home_team_name,
    s.away_team_id,
    s.away_team_name,
    s.home_total_goals,
    s.away_total_goals,
    
    -- Current Game State
    COALESCE(l.current_period, 1) as current_period,
    COALESCE(l.time_remaining_seconds, 0) as time_remaining_seconds,
    COALESCE(l.home_win_probability, 0.5) as home_win_probability,
    COALESCE(l.away_win_probability, 0.5) as away_win_probability,
    
    -- Next Goal Predictions
    COALESCE(l.next_goal_home_probability, 0.5) as next_goal_home_probability,
    COALESCE(l.next_goal_away_probability, 0.5) as next_goal_away_probability,
    COALESCE(l.next_goal_time_expected, 0) as next_goal_time_expected,  -- seconds until next goal
    
    -- Top Scorer Candidates
    COALESCE(l.top_scorer_candidates, '[]'::jsonb) as top_scorer_candidates,  -- JSON array of {player_id, probability}
    
    -- Momentum
    COALESCE(l.momentum_score, 0) as momentum_score,  -- -100 to +100
    COALESCE(l.momentum_team, '') as momentum_team,  -- 'Home' or 'Away'
    
    -- Comeback Probability
    COALESCE(l.comeback_probability, 0) as comeback_probability,  -- Probability trailing team wins
    
    -- Model Info
    l.model_version,
    l.updated_at
    
FROM dim_schedule s
LEFT JOIN ml_live_game_predictions l ON s.game_id = l.game_id
WHERE s.date >= CURRENT_DATE - INTERVAL '1 day'  -- Today's games
  AND s.home_total_goals IS NULL  -- Game not finished
ORDER BY s.date DESC, s.game_id DESC;

-- ============================================================================
-- SECTION 10: MATERIALIZED VIEWS (For Performance)
-- ============================================================================

-- Materialized view for player projections (refresh daily)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_ml_player_projections_summary AS
SELECT 
    player_id,
    player_name,
    season_id,
    projected_points,
    projected_goals,
    projected_war,
    projected_points_percentile,
    probability_50_goals,
    probability_100_points
FROM v_ml_player_season_projections
WHERE projected_points IS NOT NULL
ORDER BY projected_points DESC;

-- Create index
CREATE INDEX IF NOT EXISTS idx_mv_ml_player_projections_player_id 
ON mv_ml_player_projections_summary(player_id);

-- Materialized view for game predictions (refresh before each game day)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_ml_upcoming_game_predictions AS
SELECT 
    game_id,
    date,
    home_team_name,
    away_team_name,
    home_win_probability,
    away_win_probability,
    predicted_home_goals,
    predicted_away_goals,
    prediction_confidence
FROM v_ml_game_predictions
WHERE date >= CURRENT_DATE
  AND date <= CURRENT_DATE + INTERVAL '7 days'  -- Next 7 days
ORDER BY date ASC, game_id ASC;

-- Create index
CREATE INDEX IF NOT EXISTS idx_mv_ml_upcoming_game_predictions_date 
ON mv_ml_upcoming_game_predictions(date);

-- ============================================================================
-- REFRESH MATERIALIZED VIEWS (Run after ML jobs)
-- ============================================================================

-- Uncomment and run after ML prediction jobs:
-- REFRESH MATERIALIZED VIEW mv_ml_player_projections_summary;
-- REFRESH MATERIALIZED VIEW mv_ml_upcoming_game_predictions;
