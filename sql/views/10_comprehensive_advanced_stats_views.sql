-- ============================================================================
-- COMPREHENSIVE ADVANCED STATS VIEWS
-- Complete views for all micro/macro/advanced stats in all situations
-- Created: 2026-01-15
-- Purpose: Efficient, flexible, in-depth dashboard stats
-- ============================================================================

-- ============================================================================
-- SECTION 1: PLAYER SEASON STATS - COMPREHENSIVE (All Situations)
-- ============================================================================

-- Base comprehensive player season stats view (aggregates all game-level stats)
CREATE OR REPLACE VIEW v_player_season_comprehensive AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    p.game_type,
    COUNT(DISTINCT p.game_id) as games_played,
    
    -- Core Stats
    SUM(COALESCE(p.goals, 0)) as goals,
    SUM(COALESCE(p.primary_assists, 0)) as primary_assists,
    SUM(COALESCE(p.secondary_assists, 0)) as secondary_assists,
    SUM(COALESCE(p.assists, 0)) as assists,
    SUM(COALESCE(p.points, 0)) as points,
    SUM(COALESCE(p.pim, 0)) as pim,
    
    -- Shots
    SUM(COALESCE(p.shots, p.sog, 0)) as shots,
    SUM(COALESCE(p.sog, p.shots_on_goal, 0)) as shots_on_goal,
    SUM(COALESCE(p.shots_blocked, 0)) as shots_blocked,
    SUM(COALESCE(p.shots_missed, 0)) as shots_missed,
    CASE 
        WHEN SUM(COALESCE(p.sog, p.shots_on_goal, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.goals, 0))::numeric / SUM(COALESCE(p.sog, p.shots_on_goal, 0)) * 100, 2)
        ELSE 0 
    END as shooting_pct,
    
    -- TOI
    SUM(COALESCE(p.toi_seconds, 0)) as toi_seconds,
    ROUND(SUM(COALESCE(p.toi_seconds, 0))::numeric / 60, 2) as toi_minutes,
    SUM(COALESCE(p.shift_count, p.shifts, 0)) as shifts,
    CASE 
        WHEN SUM(COALESCE(p.shift_count, p.shifts, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.toi_seconds, 0))::numeric / SUM(COALESCE(p.shift_count, p.shifts, 0)), 2)
        ELSE 0 
    END as avg_shift_length,
    
    -- Faceoffs
    SUM(COALESCE(p.fo_wins, 0)) as fo_wins,
    SUM(COALESCE(p.fo_losses, 0)) as fo_losses,
    SUM(COALESCE(p.fo_total, p.fo_wins + p.fo_losses, 0)) as fo_total,
    CASE 
        WHEN SUM(COALESCE(p.fo_total, p.fo_wins + p.fo_losses, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.fo_wins, 0))::numeric / SUM(COALESCE(p.fo_total, p.fo_wins + p.fo_losses, 0)) * 100, 2)
        ELSE 0 
    END as fo_pct,
    
    -- Physical
    SUM(COALESCE(p.hits, 0)) as hits,
    SUM(COALESCE(p.blocks, 0)) as blocks,
    
    -- Possession Metrics
    SUM(COALESCE(p.corsi_for, p.cf, 0)) as corsi_for,
    SUM(COALESCE(p.corsi_against, p.ca, 0)) as corsi_against,
    CASE 
        WHEN SUM(COALESCE(p.corsi_for, p.cf, 0)) + SUM(COALESCE(p.corsi_against, p.ca, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.corsi_for, p.cf, 0))::numeric / 
                   (SUM(COALESCE(p.corsi_for, p.cf, 0)) + SUM(COALESCE(p.corsi_against, p.ca, 0))) * 100, 2)
        ELSE 0 
    END as cf_pct,
    SUM(COALESCE(p.fenwick_for, p.ff, 0)) as fenwick_for,
    SUM(COALESCE(p.fenwick_against, p.fa, 0)) as fenwick_against,
    CASE 
        WHEN SUM(COALESCE(p.fenwick_for, p.ff, 0)) + SUM(COALESCE(p.fenwick_against, p.fa, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.fenwick_for, p.ff, 0))::numeric / 
                   (SUM(COALESCE(p.fenwick_for, p.ff, 0)) + SUM(COALESCE(p.fenwick_against, p.fa, 0))) * 100, 2)
        ELSE 0 
    END as ff_pct,
    
    -- Expected Goals
    SUM(COALESCE(p.xg_for, p.xg, p.expected_goals, 0)) as xg_total,
    SUM(COALESCE(p.goals, 0)) as goals_actual,
    ROUND(SUM(COALESCE(p.goals, 0))::numeric - SUM(COALESCE(p.xg_for, p.xg, p.expected_goals, 0))::numeric, 2) as goals_above_xg,
    CASE 
        WHEN SUM(COALESCE(p.shots, p.sog, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.xg_for, p.xg, p.expected_goals, 0))::numeric / SUM(COALESCE(p.shots, p.sog, 0)), 3)
        ELSE 0 
    END as xg_per_shot,
    CASE 
        WHEN SUM(COALESCE(p.xg_for, p.xg, p.expected_goals, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.goals, 0))::numeric / SUM(COALESCE(p.xg_for, p.xg, p.expected_goals, 0)), 2)
        ELSE 0 
    END as finishing_rate,
    
    -- Zone Play
    SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) as zone_entries,
    SUM(COALESCE(p.zone_entries_successful, p.zone_ent_successful, 0)) as zone_entries_successful,
    SUM(COALESCE(p.zone_entry_controlled, p.zone_ent_controlled, 0)) as zone_entry_controlled,
    CASE 
        WHEN SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.zone_entry_controlled, p.zone_ent_controlled, 0))::numeric / 
                   SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) * 100, 2)
        ELSE 0 
    END as controlled_entry_pct,
    SUM(COALESCE(p.zone_exits, p.zone_ext, 0)) as zone_exits,
    SUM(COALESCE(p.zone_exits_successful, p.zone_ext_successful, 0)) as zone_exits_successful,
    SUM(COALESCE(p.zone_exit_controlled, p.zone_ext_controlled, 0)) as zone_exit_controlled,
    CASE 
        WHEN SUM(COALESCE(p.zone_exits, p.zone_ext, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.zone_exit_controlled, p.zone_ext_controlled, 0))::numeric / 
                   SUM(COALESCE(p.zone_exits, p.zone_ext, 0)) * 100, 2)
        ELSE 0 
    END as controlled_exit_pct,
    
    -- Rush Stats
    SUM(COALESCE(p.rush_shots, 0)) as rush_shots,
    SUM(COALESCE(p.rush_goals, 0)) as rush_goals,
    SUM(COALESCE(p.rush_assists, 0)) as rush_assists,
    SUM(COALESCE(p.rush_points, 0)) as rush_points,
    CASE 
        WHEN SUM(COALESCE(p.rush_shots, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.rush_goals, 0))::numeric / SUM(COALESCE(p.rush_shots, 0)) * 100, 2)
        ELSE 0 
    END as rush_shooting_pct,
    SUM(COALESCE(p.rush_involvement, 0)) as rush_involvement,
    
    -- Micro Stats (Offensive)
    SUM(COALESCE(p.dekes, 0)) as dekes,
    SUM(COALESCE(p.dekes_successful, 0)) as dekes_successful,
    CASE 
        WHEN SUM(COALESCE(p.dekes, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.dekes_successful, 0))::numeric / SUM(COALESCE(p.dekes, 0)) * 100, 2)
        ELSE 0 
    END as deke_success_rate,
    SUM(COALESCE(p.drives_total, p.drives_middle + p.drives_wide + p.drives_corner, 0)) as drives_total,
    SUM(COALESCE(p.drives_middle, 0)) as drives_middle,
    SUM(COALESCE(p.drives_wide, 0)) as drives_wide,
    SUM(COALESCE(p.drives_corner, 0)) as drives_corner,
    SUM(COALESCE(p.cutbacks, 0)) as cutbacks,
    SUM(COALESCE(p.delays, 0)) as delays,
    SUM(COALESCE(p.crash_net, 0)) as crash_net,
    SUM(COALESCE(p.screens, 0)) as screens,
    SUM(COALESCE(p.give_and_go, 0)) as give_and_go,
    SUM(COALESCE(p.second_touch, 0)) as second_touch,
    SUM(COALESCE(p.cycles, 0)) as cycles,
    SUM(COALESCE(p.one_timers, 0)) as one_timers,
    
    -- Micro Stats (Defensive)
    SUM(COALESCE(p.poke_checks, 0)) as poke_checks,
    SUM(COALESCE(p.stick_checks, 0)) as stick_checks,
    SUM(COALESCE(p.backchecks, 0)) as backchecks,
    SUM(COALESCE(p.forechecks, 0)) as forechecks,
    SUM(COALESCE(p.zone_entry_denials, 0)) as zone_entry_denials,
    SUM(COALESCE(p.loose_puck_wins, 0)) as loose_puck_wins,
    SUM(COALESCE(p.puck_recoveries, 0)) as puck_recoveries,
    SUM(COALESCE(p.puck_battles_total, 0)) as puck_battles_total,
    SUM(COALESCE(p.puck_battles_won, 0)) as puck_battles_won,
    CASE 
        WHEN SUM(COALESCE(p.puck_battles_total, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.puck_battles_won, 0))::numeric / SUM(COALESCE(p.puck_battles_total, 0)) * 100, 2)
        ELSE 0 
    END as puck_battle_win_pct,
    
    -- Passing
    SUM(COALESCE(p.pass_attempts, p.passes_attempted, 0)) as pass_attempts,
    SUM(COALESCE(p.pass_completed, p.passes_completed, 0)) as pass_completed,
    CASE 
        WHEN SUM(COALESCE(p.pass_attempts, p.passes_attempted, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.pass_completed, p.passes_completed, 0))::numeric / 
                   SUM(COALESCE(p.pass_attempts, p.passes_attempted, 0)) * 100, 2)
        ELSE 0 
    END as pass_completion_pct,
    SUM(COALESCE(p.shot_assists, 0)) as shot_assists,
    SUM(COALESCE(p.passes_royal_road, 0)) as royal_road_passes,
    SUM(COALESCE(p.passes_cross_ice, 0)) as cross_ice_passes,
    SUM(COALESCE(p.passes_slot, 0)) as slot_passes,
    SUM(COALESCE(p.passes_behind_net, 0)) as behind_net_passes,
    SUM(COALESCE(p.passes_breakout, 0)) as breakout_passes,
    
    -- Shot Types
    SUM(COALESCE(p.shots_wrist, 0)) as shots_wrist,
    SUM(COALESCE(p.shots_snap, 0)) as shots_snap,
    SUM(COALESCE(p.shots_slap, 0)) as shots_slap,
    SUM(COALESCE(p.shots_backhand, 0)) as shots_backhand,
    SUM(COALESCE(p.shots_one_timer, 0)) as shots_one_timer,
    SUM(COALESCE(p.shots_tip, 0)) as shots_tip,
    SUM(COALESCE(p.shots_deflection, 0)) as shots_deflection,
    SUM(COALESCE(p.goals_one_timer, 0)) as goals_one_timer,
    SUM(COALESCE(p.goals_wrist, 0)) as goals_wrist,
    SUM(COALESCE(p.goals_tip, 0)) as goals_tip,
    
    -- Danger Zone Stats
    SUM(COALESCE(p.shots_high_danger, p.hd_shots, 0)) as shots_high_danger,
    SUM(COALESCE(p.shots_medium_danger, p.md_shots, 0)) as shots_medium_danger,
    SUM(COALESCE(p.shots_low_danger, p.ld_shots, 0)) as shots_low_danger,
    SUM(COALESCE(p.goals_high_danger, p.hd_goals, 0)) as goals_high_danger,
    SUM(COALESCE(p.goals_medium_danger, p.md_goals, 0)) as goals_medium_danger,
    SUM(COALESCE(p.goals_low_danger, p.ld_goals, 0)) as goals_low_danger,
    CASE 
        WHEN SUM(COALESCE(p.shots_high_danger, p.hd_shots, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.goals_high_danger, p.hd_goals, 0))::numeric / 
                   SUM(COALESCE(p.shots_high_danger, p.hd_shots, 0)) * 100, 2)
        ELSE 0 
    END as hd_shooting_pct,
    
    -- Turnovers
    SUM(COALESCE(p.giveaways, 0)) as giveaways,
    SUM(COALESCE(p.takeaways, 0)) as takeaways,
    SUM(COALESCE(p.bad_giveaways, 0)) as bad_giveaways,
    ROUND(SUM(COALESCE(p.takeaways, 0))::numeric - SUM(COALESCE(p.giveaways, 0))::numeric, 0) as turnover_diff,
    
    -- Plus/Minus & Event-Based Stats
    SUM(COALESCE(p.plus_minus, p.plus_minus_ev, 0)) as plus_minus,
    SUM(COALESCE(p.plus_ev, 0)) as plus_ev,
    SUM(COALESCE(p.minus_ev, 0)) as minus_ev,
    SUM(COALESCE(p.goals_for, p.gf, 0)) as goals_for,
    SUM(COALESCE(p.goals_against, p.ga, 0)) as goals_against,
    CASE 
        WHEN SUM(COALESCE(p.goals_for, p.gf, 0)) + SUM(COALESCE(p.goals_against, p.ga, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.goals_for, p.gf, 0))::numeric / 
                   (SUM(COALESCE(p.goals_for, p.gf, 0)) + SUM(COALESCE(p.goals_against, p.ga, 0))) * 100, 2)
        ELSE 0 
    END as gf_pct,
    
    -- Advanced Metrics (from game stats - these are pre-calculated)
    AVG(COALESCE(p.war, 0)) as avg_war,
    SUM(COALESCE(p.war, 0)) as war_total,
    AVG(COALESCE(p.gar_total, p.gar, 0)) as avg_gar,
    SUM(COALESCE(p.gar_total, p.gar, 0)) as gar_total,
    AVG(COALESCE(p.game_score, 0)) as avg_game_score,
    AVG(COALESCE(p.player_rating, p.skill_rating, 0)) as avg_rating,
    
    -- Per-60 Rates
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.goals, 0))::numeric * 3600 / SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as goals_per_60,
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.assists, 0))::numeric * 3600 / SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as assists_per_60,
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.points, 0))::numeric * 3600 / SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as points_per_60,
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.sog, p.shots_on_goal, 0))::numeric * 3600 / SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as shots_per_60,
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.xg_for, p.xg, 0))::numeric * 3600 / SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as xg_per_60,
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.corsi_for, p.cf, 0))::numeric * 3600 / SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as corsi_per_60,
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.fenwick_for, p.ff, 0))::numeric * 3600 / SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as fenwick_per_60
    
FROM fact_player_game_stats p
WHERE p.game_type = 'All' OR p.game_type IS NULL
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season, p.game_type
HAVING COUNT(DISTINCT p.game_id) >= 1;

-- ============================================================================
-- SECTION 2: SITUATIONAL SPLITS - 5v5, PP, PK, EN
-- ============================================================================

-- Player stats by strength (5v5, PP, PK, EN)
CREATE OR REPLACE VIEW v_player_stats_by_strength AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    '5v5' as strength,
    COUNT(DISTINCT p.game_id) as games_played,
    SUM(COALESCE(p.ev_toi_seconds, p.toi_5v5, 0)) as toi_seconds,
    SUM(COALESCE(p.ev_goals, p.goals_5v5, 0)) as goals,
    SUM(COALESCE(p.ev_assists, 0)) as assists,
    SUM(COALESCE(p.ev_points, p.ev_goals + p.ev_assists, 0)) as points,
    SUM(COALESCE(p.ev_shots, 0)) as shots,
    SUM(COALESCE(p.ev_cf, p.ev_corsi_for, 0)) as corsi_for,
    SUM(COALESCE(p.ev_ca, p.ev_corsi_against, 0)) as corsi_against,
    CASE 
        WHEN SUM(COALESCE(p.ev_cf, p.ev_corsi_for, 0)) + SUM(COALESCE(p.ev_ca, p.ev_corsi_against, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.ev_cf, p.ev_corsi_for, 0))::numeric / 
                   (SUM(COALESCE(p.ev_cf, p.ev_corsi_for, 0)) + SUM(COALESCE(p.ev_ca, p.ev_corsi_against, 0))) * 100, 2)
        ELSE 0 
    END as cf_pct,
    SUM(COALESCE(p.ev_gf, p.ev_goals_for, 0)) as goals_for,
    SUM(COALESCE(p.ev_ga, p.ev_goals_against, 0)) as goals_against
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season

UNION ALL

SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    'PP' as strength,
    COUNT(DISTINCT p.game_id) as games_played,
    SUM(COALESCE(p.pp_toi_seconds, p.toi_pp, 0)) as toi_seconds,
    SUM(COALESCE(p.pp_goals, 0)) as goals,
    SUM(COALESCE(p.pp_assists, 0)) as assists,
    SUM(COALESCE(p.pp_points, p.pp_goals + p.pp_assists, 0)) as points,
    SUM(COALESCE(p.pp_shots, 0)) as shots,
    SUM(COALESCE(p.pp_cf, p.pp_corsi_for, 0)) as corsi_for,
    SUM(COALESCE(p.pp_ca, p.pp_corsi_against, 0)) as corsi_against,
    CASE 
        WHEN SUM(COALESCE(p.pp_cf, p.pp_corsi_for, 0)) + SUM(COALESCE(p.pp_ca, p.pp_corsi_against, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.pp_cf, p.pp_corsi_for, 0))::numeric / 
                   (SUM(COALESCE(p.pp_cf, p.pp_corsi_for, 0)) + SUM(COALESCE(p.pp_ca, p.pp_corsi_against, 0))) * 100, 2)
        ELSE 0 
    END as cf_pct,
    SUM(COALESCE(p.pp_gf, p.pp_goals_for, 0)) as goals_for,
    SUM(COALESCE(p.pp_ga, p.pp_goals_against, 0)) as goals_against
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season

UNION ALL

SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    'PK' as strength,
    COUNT(DISTINCT p.game_id) as games_played,
    SUM(COALESCE(p.pk_toi_seconds, p.toi_pk, 0)) as toi_seconds,
    SUM(COALESCE(p.pk_goals, 0)) as goals,
    SUM(COALESCE(p.pk_assists, 0)) as assists,
    SUM(COALESCE(p.pk_points, p.pk_goals + p.pk_assists, 0)) as points,
    SUM(COALESCE(p.pk_shots, 0)) as shots,
    SUM(COALESCE(p.pk_cf, p.pk_corsi_for, 0)) as corsi_for,
    SUM(COALESCE(p.pk_ca, p.pk_corsi_against, 0)) as corsi_against,
    CASE 
        WHEN SUM(COALESCE(p.pk_cf, p.pk_corsi_for, 0)) + SUM(COALESCE(p.pk_ca, p.pk_corsi_against, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.pk_cf, p.pk_corsi_for, 0))::numeric / 
                   (SUM(COALESCE(p.pk_cf, p.pk_corsi_for, 0)) + SUM(COALESCE(p.pk_ca, p.pk_corsi_against, 0))) * 100, 2)
        ELSE 0 
    END as cf_pct,
    SUM(COALESCE(p.pk_gf, p.pk_goals_for, 0)) as goals_for,
    SUM(COALESCE(p.pk_ga, p.pk_goals_against, 0)) as goals_against
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season;

-- ============================================================================
-- SECTION 3: PERIOD SPLITS
-- ============================================================================

-- Player stats by period
CREATE OR REPLACE VIEW v_player_stats_by_period AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    'P1' as period,
    COUNT(DISTINCT p.game_id) as games_played,
    SUM(COALESCE(p.p1_toi_seconds, 0)) as toi_seconds,
    SUM(COALESCE(p.p1_goals, 0)) as goals,
    SUM(COALESCE(p.p1_assists, 0)) as assists,
    SUM(COALESCE(p.p1_points, p.p1_goals + p.p1_assists, 0)) as points,
    SUM(COALESCE(p.p1_shots, 0)) as shots
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season

UNION ALL

SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    'P2' as period,
    COUNT(DISTINCT p.game_id) as games_played,
    SUM(COALESCE(p.p2_toi_seconds, 0)) as toi_seconds,
    SUM(COALESCE(p.p2_goals, 0)) as goals,
    SUM(COALESCE(p.p2_assists, 0)) as assists,
    SUM(COALESCE(p.p2_points, p.p2_goals + p.p2_assists, 0)) as points,
    SUM(COALESCE(p.p2_shots, 0)) as shots
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season

UNION ALL

SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    'P3' as period,
    COUNT(DISTINCT p.game_id) as games_played,
    SUM(COALESCE(p.p3_toi_seconds, 0)) as toi_seconds,
    SUM(COALESCE(p.p3_goals, 0)) as goals,
    SUM(COALESCE(p.p3_assists, 0)) as assists,
    SUM(COALESCE(p.p3_points, p.p3_goals + p.p3_assists, 0)) as points,
    SUM(COALESCE(p.p3_shots, 0)) as shots
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season;

-- ============================================================================
-- SECTION 4: GAME STATE SPLITS (Leading, Trailing, Tied)
-- ============================================================================

-- Player stats by game state
CREATE OR REPLACE VIEW v_player_stats_by_game_state AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    'Leading' as game_state,
    COUNT(DISTINCT p.game_id) as games_played,
    SUM(COALESCE(p.leading_toi, 0)) as toi_seconds,
    SUM(COALESCE(p.leading_goals, 0)) as goals,
    AVG(COALESCE(p.leading_cf_pct, 0)) as avg_cf_pct
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season

UNION ALL

SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    'Trailing' as game_state,
    COUNT(DISTINCT p.game_id) as games_played,
    SUM(COALESCE(p.trailing_toi, 0)) as toi_seconds,
    SUM(COALESCE(p.trailing_goals, 0)) as goals,
    AVG(COALESCE(p.trailing_cf_pct, 0)) as avg_cf_pct
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season

UNION ALL

SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    'Tied' as game_state,
    COUNT(DISTINCT p.game_id) as games_played,
    SUM(COALESCE(p.tied_toi, 0)) as toi_seconds,
    SUM(COALESCE(p.tied_goals, 0)) as goals,
    AVG(COALESCE(p.tied_cf_pct, 0)) as avg_cf_pct
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season;

-- ============================================================================
-- SECTION 5: COMPETITION TIER SPLITS
-- ============================================================================

-- Player stats vs competition tier (Elite, Good, Average, Weak)
CREATE OR REPLACE VIEW v_player_stats_by_competition_tier AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    'Elite' as competition_tier,
    COUNT(DISTINCT p.game_id) as games_played,
    SUM(COALESCE(p.vs_elite_toi, 0)) as toi_seconds,
    SUM(COALESCE(p.vs_elite_gf, 0)) as goals_for,
    SUM(COALESCE(p.vs_elite_ga, 0)) as goals_against,
    AVG(COALESCE(p.vs_elite_cf_pct, 0)) as avg_cf_pct
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season

UNION ALL

SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    'Good' as competition_tier,
    COUNT(DISTINCT p.game_id) as games_played,
    SUM(COALESCE(p.vs_good_toi, 0)) as toi_seconds,
    SUM(COALESCE(p.vs_good_gf, 0)) as goals_for,
    SUM(COALESCE(p.vs_good_ga, 0)) as goals_against,
    AVG(COALESCE(p.vs_good_cf_pct, 0)) as avg_cf_pct
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season

UNION ALL

SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    'Average' as competition_tier,
    COUNT(DISTINCT p.game_id) as games_played,
    SUM(COALESCE(p.vs_avg_toi, 0)) as toi_seconds,
    SUM(COALESCE(p.vs_avg_gf, 0)) as goals_for,
    SUM(COALESCE(p.vs_avg_ga, 0)) as goals_against,
    AVG(COALESCE(p.vs_avg_cf_pct, 0)) as avg_cf_pct
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season

UNION ALL

SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    'Weak' as competition_tier,
    COUNT(DISTINCT p.game_id) as games_played,
    SUM(COALESCE(p.vs_weak_toi, 0)) as toi_seconds,
    SUM(COALESCE(p.vs_weak_gf, 0)) as goals_for,
    SUM(COALESCE(p.vs_weak_ga, 0)) as goals_against,
    AVG(COALESCE(p.vs_weak_cf_pct, 0)) as avg_cf_pct
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season;

-- ============================================================================
-- SECTION 6: MICRO STATS WITH SUCCESS RATES
-- ============================================================================

-- Comprehensive micro stats view with success rates
CREATE OR REPLACE VIEW v_player_micro_stats_comprehensive AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    
    -- Deke Stats
    SUM(COALESCE(p.dekes, 0)) as dekes_attempted,
    SUM(COALESCE(p.dekes_successful, 0)) as dekes_successful,
    CASE 
        WHEN SUM(COALESCE(p.dekes, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.dekes_successful, 0))::numeric / SUM(COALESCE(p.dekes, 0)) * 100, 2)
        ELSE 0 
    END as deke_success_rate,
    
    -- Drive Stats
    SUM(COALESCE(p.drives_total, p.drives_middle + p.drives_wide + p.drives_corner, 0)) as drives_attempted,
    SUM(COALESCE(p.drives_successful, 0)) as drives_successful,
    SUM(COALESCE(p.drives_middle, 0)) as drives_middle,
    SUM(COALESCE(p.drives_wide, 0)) as drives_wide,
    SUM(COALESCE(p.drives_corner, 0)) as drives_corner,
    CASE 
        WHEN SUM(COALESCE(p.drives_total, p.drives_middle + p.drives_wide + p.drives_corner, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.drives_successful, 0))::numeric / 
                   SUM(COALESCE(p.drives_total, p.drives_middle + p.drives_wide + p.drives_corner, 0)) * 100, 2)
        ELSE 0 
    END as drive_success_rate,
    
    -- Zone Entry Stats
    SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) as zone_entries_attempted,
    SUM(COALESCE(p.zone_entry_controlled, p.zone_ent_controlled, 0)) as zone_entries_controlled,
    SUM(COALESCE(p.zone_entries_successful, p.zone_ent_successful, 0)) as zone_entries_successful,
    CASE 
        WHEN SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.zone_entry_controlled, p.zone_ent_controlled, 0))::numeric / 
                   SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) * 100, 2)
        ELSE 0 
    END as controlled_entry_rate,
    CASE 
        WHEN SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.zone_entries_successful, p.zone_ent_successful, 0))::numeric / 
                   SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) * 100, 2)
        ELSE 0 
    END as zone_entry_success_rate,
    
    -- Zone Exit Stats
    SUM(COALESCE(p.zone_exits, p.zone_ext, 0)) as zone_exits_attempted,
    SUM(COALESCE(p.zone_exit_controlled, p.zone_ext_controlled, 0)) as zone_exits_controlled,
    SUM(COALESCE(p.zone_exits_successful, p.zone_ext_successful, 0)) as zone_exits_successful,
    CASE 
        WHEN SUM(COALESCE(p.zone_exits, p.zone_ext, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.zone_exit_controlled, p.zone_ext_controlled, 0))::numeric / 
                   SUM(COALESCE(p.zone_exits, p.zone_ext, 0)) * 100, 2)
        ELSE 0 
    END as controlled_exit_rate,
    CASE 
        WHEN SUM(COALESCE(p.zone_exits, p.zone_ext, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.zone_exits_successful, p.zone_ext_successful, 0))::numeric / 
                   SUM(COALESCE(p.zone_exits, p.zone_ext, 0)) * 100, 2)
        ELSE 0 
    END as zone_exit_success_rate,
    
    -- Defensive Micro Stats
    SUM(COALESCE(p.poke_checks, 0)) as poke_checks,
    SUM(COALESCE(p.stick_checks, 0)) as stick_checks,
    SUM(COALESCE(p.zone_entry_denials, 0)) as zone_entry_denials,
    
    -- Puck Battle Stats
    SUM(COALESCE(p.puck_battles_total, 0)) as puck_battles_total,
    SUM(COALESCE(p.puck_battles_won, 0)) as puck_battles_won,
    SUM(COALESCE(p.loose_puck_wins, 0)) as loose_puck_wins,
    SUM(COALESCE(p.puck_recoveries, 0)) as puck_recoveries,
    CASE 
        WHEN SUM(COALESCE(p.puck_battles_total, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.puck_battles_won, 0))::numeric / SUM(COALESCE(p.puck_battles_total, 0)) * 100, 2)
        ELSE 0 
    END as puck_battle_win_rate,
    
    -- Playmaking Stats
    SUM(COALESCE(p.shot_assists, 0)) as shot_assists,
    SUM(COALESCE(p.goal_creating_actions, 0)) as goal_creating_actions,
    SUM(COALESCE(p.pre_shot_touches, 0)) as pre_shot_touches,
    
    -- Pressure Stats
    SUM(COALESCE(p.plays_under_pressure, 0)) as plays_under_pressure,
    SUM(COALESCE(p.pressure_success_count, 0)) as pressure_success_count,
    CASE 
        WHEN SUM(COALESCE(p.plays_under_pressure, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.pressure_success_count, 0))::numeric / 
                   SUM(COALESCE(p.plays_under_pressure, 0)) * 100, 2)
        ELSE 0 
    END as pressure_success_rate,
    AVG(COALESCE(p.poise_index, 0)) as avg_poise_index,
    
    -- Other Micro Stats
    SUM(COALESCE(p.cutbacks, 0)) as cutbacks,
    SUM(COALESCE(p.delays, 0)) as delays,
    SUM(COALESCE(p.crash_net, 0)) as crash_net_attempts,
    SUM(COALESCE(p.screens, 0)) as screens,
    SUM(COALESCE(p.give_and_go, 0)) as give_and_go,
    SUM(COALESCE(p.second_touch, 0)) as second_touch,
    SUM(COALESCE(p.cycles, 0)) as cycles,
    SUM(COALESCE(p.one_timers, 0)) as one_timers,
    SUM(COALESCE(p.backchecks, 0)) as backchecks,
    SUM(COALESCE(p.forechecks, 0)) as forechecks,
    
    -- Overall Play Success
    SUM(COALESCE(p.plays_successful, 0)) as plays_successful,
    SUM(COALESCE(p.plays_unsuccessful, 0)) as plays_unsuccessful,
    CASE 
        WHEN SUM(COALESCE(p.plays_successful, 0)) + SUM(COALESCE(p.plays_unsuccessful, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.plays_successful, 0))::numeric / 
                   (SUM(COALESCE(p.plays_successful, 0)) + SUM(COALESCE(p.plays_unsuccessful, 0))) * 100, 2)
        ELSE 0 
    END as overall_play_success_rate,
    
    COUNT(DISTINCT p.game_id) as games_played
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season;

-- ============================================================================
-- SECTION 7: ADVANCED METRICS (WAR, GAR, xG) - DETAILED
-- ============================================================================

-- Advanced metrics with component breakdowns
CREATE OR REPLACE VIEW v_player_advanced_metrics AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    COUNT(DISTINCT p.game_id) as games_played,
    
    -- WAR/GAR Components
    SUM(COALESCE(p.gar_offense, 0)) as gar_offense,
    SUM(COALESCE(p.gar_defense, 0)) as gar_defense,
    SUM(COALESCE(p.gar_possession, 0)) as gar_possession,
    SUM(COALESCE(p.gar_transition, 0)) as gar_transition,
    SUM(COALESCE(p.gar_poise, 0)) as gar_poise,
    SUM(COALESCE(p.gar_total, p.gar, 0)) as gar_total,
    AVG(COALESCE(p.war, 0)) as avg_war,
    SUM(COALESCE(p.war, 0)) as war_total,
    AVG(COALESCE(p.war_pace, 0)) as avg_war_pace,
    
    -- xG Metrics
    SUM(COALESCE(p.xg_for, p.xg, p.expected_goals, 0)) as xg_total,
    SUM(COALESCE(p.goals, 0)) as goals_actual,
    ROUND(SUM(COALESCE(p.goals, 0))::numeric - SUM(COALESCE(p.xg_for, p.xg, p.expected_goals, 0))::numeric, 2) as goals_above_xg,
    AVG(COALESCE(p.xg_per_shot, 0)) as avg_xg_per_shot,
    AVG(COALESCE(p.finishing_rate, p.finishing_skill, 0)) as avg_finishing_rate,
    
    -- Game Score Components
    AVG(COALESCE(p.game_score, 0)) as avg_game_score,
    AVG(COALESCE(p.gs_scoring, 0)) as avg_gs_scoring,
    AVG(COALESCE(p.gs_shots, 0)) as avg_gs_shots,
    AVG(COALESCE(p.gs_playmaking, 0)) as avg_gs_playmaking,
    AVG(COALESCE(p.gs_defense, 0)) as avg_gs_defense,
    AVG(COALESCE(p.gs_hustle, 0)) as avg_gs_hustle,
    AVG(COALESCE(p.offensive_game_score, 0)) as avg_offensive_gs,
    AVG(COALESCE(p.defensive_game_score, 0)) as avg_defensive_gs,
    
    -- Rating Metrics
    AVG(COALESCE(p.player_rating, p.skill_rating, 0)) as avg_rating,
    AVG(COALESCE(p.opp_avg_rating, 0)) as avg_qoc_rating,
    AVG(COALESCE(p.team_avg_rating, 0)) as avg_qot_rating,
    AVG(COALESCE(p.calculated_rating, 0)) as avg_calculated_rating,
    AVG(COALESCE(p.rating_delta, 0)) as avg_rating_delta,
    AVG(COALESCE(p.performance_index, 0)) as avg_performance_index,
    
    -- Relative Stats
    AVG(COALESCE(p.cf_pct_rel, p.corsi_pct_rel, 0)) as avg_cf_pct_rel,
    AVG(COALESCE(p.ff_pct_rel, p.fenwick_pct_rel, 0)) as avg_ff_pct_rel,
    AVG(COALESCE(p.gf_pct_rel, 0)) as avg_gf_pct_rel,
    
    -- Rankings (calculated)
    RANK() OVER (PARTITION BY p.season_id ORDER BY SUM(COALESCE(p.gar_total, p.gar, 0)) DESC) as gar_rank,
    RANK() OVER (PARTITION BY p.season_id ORDER BY AVG(COALESCE(p.war, 0)) DESC) as war_rank,
    RANK() OVER (PARTITION BY p.season_id ORDER BY SUM(COALESCE(p.goals, 0))::numeric - 
                 SUM(COALESCE(p.xg_for, p.xg, 0))::numeric DESC) as g_minus_xg_rank
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season;

-- ============================================================================
-- SECTION 8: GOALIE COMPREHENSIVE STATS
-- ============================================================================

-- Comprehensive goalie season stats
CREATE OR REPLACE VIEW v_goalie_season_comprehensive AS
SELECT 
    g.player_id,
    g.player_name,
    g.team_id,
    g.team_name,
    g.season_id,
    g.season,
    COUNT(DISTINCT g.game_id) as games_played,
    
    -- Core Stats
    SUM(COALESCE(g.saves, 0)) as saves,
    SUM(COALESCE(g.goals_against, 0)) as goals_against,
    SUM(COALESCE(g.shots_against, g.saves + g.goals_against, 0)) as shots_against,
    CASE 
        WHEN SUM(COALESCE(g.shots_against, g.saves + g.goals_against, 0)) > 0 
        THEN ROUND(SUM(COALESCE(g.saves, 0))::numeric / 
                   SUM(COALESCE(g.shots_against, g.saves + g.goals_against, 0)) * 100, 2)
        ELSE 0 
    END as save_pct,
    
    -- Save Types
    SUM(COALESCE(g.saves_butterfly, 0)) as saves_butterfly,
    SUM(COALESCE(g.saves_pad, 0)) as saves_pad,
    SUM(COALESCE(g.saves_glove, 0)) as saves_glove,
    SUM(COALESCE(g.saves_blocker, 0)) as saves_blocker,
    SUM(COALESCE(g.saves_chest, 0)) as saves_chest,
    SUM(COALESCE(g.saves_stick, 0)) as saves_stick,
    SUM(COALESCE(g.saves_scramble, 0)) as saves_scramble,
    
    -- High Danger Stats
    SUM(COALESCE(g.hd_shots_against, 0)) as hd_shots_against,
    SUM(COALESCE(g.hd_goals_against, 0)) as hd_goals_against,
    SUM(COALESCE(g.hd_saves, 0)) as hd_saves,
    CASE 
        WHEN SUM(COALESCE(g.hd_shots_against, 0)) > 0 
        THEN ROUND(SUM(COALESCE(g.hd_saves, 0))::numeric / SUM(COALESCE(g.hd_shots_against, 0)) * 100, 2)
        ELSE 0 
    END as hd_save_pct,
    
    -- Rebound Control
    SUM(COALESCE(g.saves_freeze, 0)) as saves_freeze,
    SUM(COALESCE(g.saves_rebound, 0)) as saves_rebound,
    CASE 
        WHEN SUM(COALESCE(g.saves, 0)) > 0 
        THEN ROUND(SUM(COALESCE(g.saves_freeze, 0))::numeric / SUM(COALESCE(g.saves, 0)) * 100, 2)
        ELSE 0 
    END as freeze_pct,
    CASE 
        WHEN SUM(COALESCE(g.saves, 0)) > 0 
        THEN ROUND(SUM(COALESCE(g.saves_rebound, 0))::numeric / SUM(COALESCE(g.saves, 0)) * 100, 2)
        ELSE 0 
    END as rebound_rate,
    
    -- Period Splits (averaged)
    AVG(COALESCE(g.p1_sv_pct, 0)) as avg_p1_sv_pct,
    AVG(COALESCE(g.p2_sv_pct, 0)) as avg_p2_sv_pct,
    AVG(COALESCE(g.p3_sv_pct, 0)) as avg_p3_sv_pct,
    AVG(COALESCE(g.final_minute_sv_pct, 0)) as avg_clutch_sv_pct,
    
    -- Shot Context
    SUM(COALESCE(g.rush_saves, 0)) as rush_saves,
    SUM(COALESCE(g.quick_attack_saves, 0)) as quick_attack_saves,
    SUM(COALESCE(g.set_play_saves, 0)) as set_play_saves,
    AVG(COALESCE(g.rush_sv_pct, 0)) as avg_rush_sv_pct,
    AVG(COALESCE(g.transition_defense_rating, 0)) as avg_transition_defense_rating,
    
    -- Pressure/Sequence
    SUM(COALESCE(g.single_shot_saves, 0)) as single_shot_saves,
    SUM(COALESCE(g.multi_shot_saves, 0)) as multi_shot_saves,
    SUM(COALESCE(g.sustained_pressure_saves, 0)) as sustained_pressure_saves,
    AVG(COALESCE(g.pressure_handling_index, 0)) as avg_pressure_handling_index,
    AVG(COALESCE(g.sequence_survival_rate, 0)) as avg_sequence_survival_rate,
    
    -- Advanced Metrics
    SUM(COALESCE(g.goals_saved_above_avg, g.gsaa, 0)) as gsaa_total,
    AVG(COALESCE(g.goals_saved_above_avg, g.gsaa, 0)) as avg_gsaa,
    SUM(COALESCE(g.is_quality_start, 0)) as quality_starts,
    SUM(COALESCE(g.is_bad_start, 0)) as bad_starts,
    CASE 
        WHEN COUNT(DISTINCT g.game_id) > 0 
        THEN ROUND(SUM(COALESCE(g.is_quality_start, 0))::numeric / COUNT(DISTINCT g.game_id) * 100, 2)
        ELSE 0 
    END as quality_start_pct,
    
    -- Goalie WAR/GAR
    SUM(COALESCE(g.goalie_gar_gsaa, 0)) as gar_gsaa,
    SUM(COALESCE(g.goalie_gar_hd_bonus, 0)) as gar_hd_bonus,
    SUM(COALESCE(g.goalie_gar_qs_bonus, 0)) as gar_qs_bonus,
    SUM(COALESCE(g.goalie_gar_rebound, 0)) as gar_rebound,
    SUM(COALESCE(g.goalie_gar_total, 0)) as gar_total,
    AVG(COALESCE(g.goalie_war, 0)) as avg_war,
    SUM(COALESCE(g.goalie_war, 0)) as war_total,
    AVG(COALESCE(g.goalie_war_pace, 0)) as avg_war_pace,
    
    -- Composite Ratings
    AVG(COALESCE(g.clutch_rating, 0)) as avg_clutch_rating,
    AVG(COALESCE(g.consistency_rating, 0)) as avg_consistency_rating,
    AVG(COALESCE(g.rebound_rating, 0)) as avg_rebound_rating,
    AVG(COALESCE(g.positioning_rating, 0)) as avg_positioning_rating,
    AVG(COALESCE(g.overall_game_rating, 0)) as avg_overall_rating,
    
    -- Rankings
    RANK() OVER (PARTITION BY g.season_id ORDER BY AVG(COALESCE(g.save_pct, 0)) DESC) as sv_pct_rank,
    RANK() OVER (PARTITION BY g.season_id ORDER BY AVG(COALESCE(g.goals_saved_above_avg, g.gsaa, 0)) DESC) as gsaa_rank,
    RANK() OVER (PARTITION BY g.season_id ORDER BY AVG(COALESCE(g.goalie_war, 0)) DESC) as war_rank
FROM fact_goalie_game_stats g
GROUP BY g.player_id, g.player_name, g.team_id, g.team_name, g.season_id, g.season
HAVING COUNT(DISTINCT g.game_id) >= 1;

-- ============================================================================
-- SECTION 9: MATERIALIZED VIEWS - EXPENSIVE AGGREGATIONS
-- ============================================================================

-- Materialized view for player career totals (expensive operation)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_player_career_totals AS
SELECT 
    p.player_id,
    p.player_name,
    COUNT(DISTINCT p.season_id) as seasons_played,
    COUNT(DISTINCT p.game_id) as career_games_played,
    
    -- Career Totals
    SUM(COALESCE(p.goals, 0)) as career_goals,
    SUM(COALESCE(p.assists, 0)) as career_assists,
    SUM(COALESCE(p.points, 0)) as career_points,
    SUM(COALESCE(p.pim, 0)) as career_pim,
    SUM(COALESCE(p.toi_seconds, 0)) as career_toi_seconds,
    
    -- Career Advanced
    SUM(COALESCE(p.war, 0)) as career_war,
    SUM(COALESCE(p.gar_total, p.gar, 0)) as career_gar,
    AVG(COALESCE(p.war, 0)) as avg_seasonal_war,
    MAX(COALESCE(p.war, 0)) as peak_war_season,
    
    -- Career Percentiles (requires subquery for calculation)
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY COALESCE(p.war, 0)) as p90_war,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY COALESCE(p.war, 0)) as median_war,
    
    -- Career Rates
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.points, 0))::numeric * 3600 / SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as career_points_per_60,
    
    -- Best Season
    (SELECT season_id 
     FROM fact_player_game_stats 
     WHERE player_id = p.player_id 
     GROUP BY season_id 
     ORDER BY SUM(COALESCE(war, 0)) DESC 
     LIMIT 1) as best_season_id
    
FROM fact_player_game_stats p
GROUP BY p.player_id, p.player_name;

-- Create index on materialized view
CREATE INDEX IF NOT EXISTS idx_mv_player_career_totals_player_id 
ON mv_player_career_totals(player_id);

-- Materialized view for player vs opponent stats (very expensive)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_player_vs_opponent AS
SELECT 
    p.player_id,
    p.player_name,
    o.team_id as opponent_team_id,
    o.team_name as opponent_team_name,
    p.season_id,
    p.season,
    COUNT(DISTINCT p.game_id) as games_vs_opponent,
    
    -- Stats vs this opponent
    SUM(COALESCE(p.goals, 0)) as goals_vs_opponent,
    SUM(COALESCE(p.assists, 0)) as assists_vs_opponent,
    SUM(COALESCE(p.points, 0)) as points_vs_opponent,
    AVG(COALESCE(p.points, 0)) as avg_points_vs_opponent,
    SUM(CASE WHEN COALESCE(p.points, 0) >= 2 THEN 1 ELSE 0 END) as multi_point_games,
    
    -- Advanced vs opponent
    AVG(COALESCE(p.war, 0)) as avg_war_vs_opponent,
    AVG(COALESCE(p.cf_pct, 0)) as avg_cf_pct_vs_opponent,
    SUM(COALESCE(p.goals, 0))::numeric - SUM(COALESCE(p.xg_for, p.xg, 0))::numeric as goals_above_xg_vs_opponent
    
FROM fact_player_game_stats p
JOIN dim_schedule s ON p.game_id = s.game_id
JOIN dim_team o ON (
    (s.home_team_id = o.team_id AND p.team_venue != 'Home') OR
    (s.away_team_id = o.team_id AND p.team_venue = 'Home')
)
WHERE p.player_id != '' AND o.team_id IS NOT NULL
GROUP BY p.player_id, p.player_name, o.team_id, o.team_name, p.season_id, p.season;

-- Create indexes on materialized view
CREATE INDEX IF NOT EXISTS idx_mv_player_vs_opponent_player_id 
ON mv_player_vs_opponent(player_id);
CREATE INDEX IF NOT EXISTS idx_mv_player_vs_opponent_opponent 
ON mv_player_vs_opponent(opponent_team_id);

-- Materialized view for rolling averages (last 10/20 games)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_player_rolling_stats AS
WITH ranked_games AS (
    SELECT 
        p.*,
        ROW_NUMBER() OVER (PARTITION BY p.player_id, p.season_id ORDER BY s.date DESC, s.game_id DESC) as game_rank
    FROM fact_player_game_stats p
    JOIN dim_schedule s ON p.game_id = s.game_id
    WHERE (p.game_type = 'All' OR p.game_type IS NULL)
)
SELECT 
    p.player_id,
    p.player_name,
    p.season_id,
    p.season,
    
    -- Last 10 Games
    COUNT(DISTINCT CASE WHEN p.game_rank <= 10 THEN p.game_id END) as games_last_10,
    SUM(CASE WHEN p.game_rank <= 10 THEN COALESCE(p.points, 0) ELSE 0 END) as points_last_10,
    AVG(CASE WHEN p.game_rank <= 10 THEN COALESCE(p.points, 0) ELSE NULL END) as avg_points_last_10,
    AVG(CASE WHEN p.game_rank <= 10 THEN COALESCE(p.war, 0) ELSE NULL END) as avg_war_last_10,
    AVG(CASE WHEN p.game_rank <= 10 THEN COALESCE(p.cf_pct, 0) ELSE NULL END) as avg_cf_pct_last_10,
    
    -- Last 20 Games
    COUNT(DISTINCT CASE WHEN p.game_rank <= 20 THEN p.game_id END) as games_last_20,
    SUM(CASE WHEN p.game_rank <= 20 THEN COALESCE(p.points, 0) ELSE 0 END) as points_last_20,
    AVG(CASE WHEN p.game_rank <= 20 THEN COALESCE(p.points, 0) ELSE NULL END) as avg_points_last_20,
    AVG(CASE WHEN p.game_rank <= 20 THEN COALESCE(p.war, 0) ELSE NULL END) as avg_war_last_20,
    AVG(CASE WHEN p.game_rank <= 20 THEN COALESCE(p.cf_pct, 0) ELSE NULL END) as avg_cf_pct_last_20
    
FROM ranked_games p
GROUP BY p.player_id, p.player_name, p.season_id, p.season;

-- Create index on materialized view
CREATE INDEX IF NOT EXISTS idx_mv_player_rolling_stats_player_id 
ON mv_player_rolling_stats(player_id);

-- ============================================================================
-- SECTION 10: LEAGUE PERCENTILES (For Comparisons)
-- ============================================================================

-- League percentiles for all key stats (by season)
CREATE OR REPLACE VIEW v_player_league_percentiles AS
WITH league_stats AS (
    SELECT 
        p.season_id,
        p.player_id,
        p.games_played,
        p.points,
        p.goals,
        p.assists,
        p.war,
        p.gar_total,
        p.cf_pct,
        p.goals_above_xg,
        p.points_per_60,
        p.goals_per_60
    FROM fact_player_season_stats_basic p
    WHERE p.game_type = 'All' AND p.games_played >= 5
)
SELECT 
    p.player_id,
    p.season_id,
    p.games_played,
    p.points,
    PERCENT_RANK() OVER (PARTITION BY p.season_id ORDER BY p.points DESC) * 100 as points_percentile,
    p.goals,
    PERCENT_RANK() OVER (PARTITION BY p.season_id ORDER BY p.goals DESC) * 100 as goals_percentile,
    p.assists,
    PERCENT_RANK() OVER (PARTITION BY p.season_id ORDER BY p.assists DESC) * 100 as assists_percentile,
    p.war,
    PERCENT_RANK() OVER (PARTITION BY p.season_id ORDER BY p.war DESC) * 100 as war_percentile,
    p.gar_total,
    PERCENT_RANK() OVER (PARTITION BY p.season_id ORDER BY p.gar_total DESC) * 100 as gar_percentile,
    p.cf_pct,
    PERCENT_RANK() OVER (PARTITION BY p.season_id ORDER BY p.cf_pct DESC) * 100 as cf_pct_percentile,
    p.goals_above_xg,
    PERCENT_RANK() OVER (PARTITION BY p.season_id ORDER BY p.goals_above_xg DESC) * 100 as g_minus_xg_percentile,
    p.points_per_60,
    PERCENT_RANK() OVER (PARTITION BY p.season_id ORDER BY p.points_per_60 DESC) * 100 as pp60_percentile
FROM league_stats p;

-- ============================================================================
-- SECTION 11: COMBINED SITUATIONAL VIEWS (Multi-Dimensional)
-- ============================================================================

-- Player stats by strength AND period (comprehensive situational breakdown)
CREATE OR REPLACE VIEW v_player_stats_strength_period AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    '5v5-P1' as situation,
    COUNT(DISTINCT p.game_id) as games_played,
    SUM(COALESCE(p.ev_toi_seconds, 0) * CASE WHEN EXISTS (
        SELECT 1 FROM fact_shifts s 
        WHERE s.game_id = p.game_id AND s.period = 1
    ) THEN 0.33 ELSE 0 END) as toi_estimate,
    SUM(COALESCE(p.p1_goals, 0) * CASE WHEN COALESCE(p.ev_goals, 0) > 0 THEN 
        COALESCE(p.ev_goals, 0) / NULLIF(p.goals, 1) ELSE 1 END) as goals_estimate
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season;

-- Note: For true strength+period combinations, you'd need shift-level data
-- This is a simplified version. For full implementation, join with fact_shifts.

-- ============================================================================
-- SECTION 12: TEAM COMPREHENSIVE STATS
-- ============================================================================

-- Team comprehensive stats with all advanced metrics
CREATE OR REPLACE VIEW v_team_season_comprehensive AS
SELECT 
    t.team_id,
    t.team_name,
    t.season_id,
    t.season,
    t.game_type,
    t.games_played,
    t.wins,
    t.losses,
    t.ties,
    t.points,
    t.goals_for,
    t.goals_against,
    t.goal_diff,
    t.goals_for_per_game,
    t.goals_against_per_game,
    t.win_pct,
    
    -- Advanced Team Metrics (aggregated from players)
    COALESCE(
        (SELECT AVG(p.war) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id 
           AND p.season_id = t.season_id 
           AND (p.game_type = t.game_type OR t.game_type = 'All')
         GROUP BY p.team_id),
        0
    ) as avg_team_war,
    
    COALESCE(
        (SELECT SUM(p.gar_total) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id 
           AND p.season_id = t.season_id 
           AND (p.game_type = t.game_type OR t.game_type = 'All')
         GROUP BY p.team_id),
        0
    ) as total_team_gar,
    
    COALESCE(
        (SELECT AVG(p.cf_pct) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id 
           AND p.season_id = t.season_id 
           AND (p.game_type = t.game_type OR t.game_type = 'All')
         GROUP BY p.team_id),
        50.0
    ) as avg_team_cf_pct,
    
    -- Team Micro Stats Aggregation
    COALESCE(
        (SELECT AVG(p.controlled_entry_pct) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id 
           AND p.season_id = t.season_id 
           AND (p.game_type = t.game_type OR t.game_type = 'All')
           AND p.zone_entries > 0
         GROUP BY p.team_id),
        0
    ) as avg_team_controlled_entry_pct
    
FROM fact_team_season_stats_basic t
WHERE t.games_played >= 1;

-- ============================================================================
-- SECTION 13: PASSING ANALYSIS
-- ============================================================================

-- Comprehensive passing stats
CREATE OR REPLACE VIEW v_player_passing_comprehensive AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    COUNT(DISTINCT p.game_id) as games_played,
    
    -- Pass Totals
    SUM(COALESCE(p.pass_attempts, p.passes_attempted, 0)) as pass_attempts,
    SUM(COALESCE(p.pass_completed, p.passes_completed, 0)) as pass_completed,
    CASE 
        WHEN SUM(COALESCE(p.pass_attempts, p.passes_attempted, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.pass_completed, p.passes_completed, 0))::numeric / 
                   SUM(COALESCE(p.pass_attempts, p.passes_attempted, 0)) * 100, 2)
        ELSE 0 
    END as pass_completion_pct,
    
    -- Pass Types
    SUM(COALESCE(p.passes_forehand, 0)) as passes_forehand,
    SUM(COALESCE(p.passes_backhand, 0)) as passes_backhand,
    SUM(COALESCE(p.passes_stretch, 0)) as passes_stretch,
    SUM(COALESCE(p.passes_bank, 0)) as passes_bank,
    SUM(COALESCE(p.passes_rim, 0)) as passes_rim,
    SUM(COALESCE(p.passes_drop, 0)) as passes_drop,
    SUM(COALESCE(p.passes_lob, 0)) as passes_lob,
    SUM(COALESCE(p.passes_one_touch, 0)) as passes_one_touch,
    SUM(COALESCE(p.creative_passes, 0)) as creative_passes,
    
    -- Advanced Passing
    SUM(COALESCE(p.shot_assists, 0)) as shot_assists,
    SUM(COALESCE(p.goal_creating_actions, 0)) as goal_creating_actions,
    SUM(COALESCE(p.passes_royal_road, 0)) as royal_road_passes,
    SUM(COALESCE(p.passes_cross_ice, 0)) as cross_ice_passes,
    SUM(COALESCE(p.passes_slot, 0)) as slot_passes,
    SUM(COALESCE(p.passes_behind_net, 0)) as behind_net_passes,
    SUM(COALESCE(p.passes_breakout, 0)) as breakout_passes,
    
    -- Pass Rates
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.pass_attempts, p.passes_attempted, 0))::numeric * 3600 / 
                   SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as pass_attempts_per_60,
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.shot_assists, 0))::numeric * 3600 / 
                   SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as shot_assists_per_60
    
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season;

-- ============================================================================
-- SECTION 14: SHOT TYPE ANALYSIS
-- ============================================================================

-- Comprehensive shot type breakdown
CREATE OR REPLACE VIEW v_player_shot_types_comprehensive AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    COUNT(DISTINCT p.game_id) as games_played,
    
    -- Shot Types
    SUM(COALESCE(p.shots_wrist, 0)) as shots_wrist,
    SUM(COALESCE(p.shots_snap, 0)) as shots_snap,
    SUM(COALESCE(p.shots_slap, 0)) as shots_slap,
    SUM(COALESCE(p.shots_backhand, 0)) as shots_backhand,
    SUM(COALESCE(p.shots_one_timer, 0)) as shots_one_timer,
    SUM(COALESCE(p.shots_tip, 0)) as shots_tip,
    SUM(COALESCE(p.shots_deflection, 0)) as shots_deflection,
    SUM(COALESCE(p.shots_wraparound, 0)) as shots_wraparound,
    
    -- Goals by Type
    SUM(COALESCE(p.goals_wrist, 0)) as goals_wrist,
    SUM(COALESCE(p.goals_one_timer, 0)) as goals_one_timer,
    SUM(COALESCE(p.goals_tip, 0)) as goals_tip,
    SUM(COALESCE(p.goals_backhand, 0)) as goals_backhand,
    
    -- Conversion Rates
    CASE 
        WHEN SUM(COALESCE(p.shots_wrist, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.goals_wrist, 0))::numeric / SUM(COALESCE(p.shots_wrist, 0)) * 100, 2)
        ELSE 0 
    END as wrist_shot_pct,
    CASE 
        WHEN SUM(COALESCE(p.shots_one_timer, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.goals_one_timer, 0))::numeric / SUM(COALESCE(p.shots_one_timer, 0)) * 100, 2)
        ELSE 0 
    END as one_timer_pct,
    CASE 
        WHEN SUM(COALESCE(p.shots_tip, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.goals_tip, 0))::numeric / SUM(COALESCE(p.shots_tip, 0)) * 100, 2)
        ELSE 0 
    END as tip_shot_pct,
    
    -- Primary Shot Type
    CASE 
        WHEN SUM(COALESCE(p.shots_one_timer, 0)) >= GREATEST(
            COALESCE(SUM(p.shots_wrist), 0),
            COALESCE(SUM(p.shots_snap), 0),
            COALESCE(SUM(p.shots_slap), 0)
        ) THEN 'One-Timer'
        WHEN SUM(COALESCE(p.shots_wrist, 0)) >= GREATEST(
            COALESCE(SUM(p.shots_snap), 0),
            COALESCE(SUM(p.shots_slap), 0)
        ) THEN 'Wrist'
        WHEN SUM(COALESCE(p.shots_snap, 0)) >= COALESCE(SUM(p.shots_slap), 0) THEN 'Snap'
        ELSE 'Slap'
    END as primary_shot_type
    
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season;

-- ============================================================================
-- SECTION 15: IMPROVEMENTS FOR CURRENT DASHBOARD
-- ============================================================================

-- Enhanced standings with advanced metrics
CREATE OR REPLACE VIEW v_standings_enhanced AS
SELECT 
    s.*,
    -- Add advanced team metrics
    COALESCE(
        (SELECT AVG(p.cf_pct) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = s.team_id 
           AND p.season_id = s.season_id
         GROUP BY p.team_id),
        50.0
    ) as team_cf_pct,
    COALESCE(
        (SELECT SUM(p.gar_total) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = s.team_id 
           AND p.season_id = s.season_id
         GROUP BY p.team_id),
        0
    ) as team_gar
FROM v_standings_current s;

-- Player rankings with percentiles (enhanced)
CREATE OR REPLACE VIEW v_rankings_players_enhanced AS
SELECT 
    r.*,
    p.points_percentile,
    p.goals_percentile,
    p.assists_percentile,
    p.war_percentile,
    p.gar_percentile,
    p.cf_pct_percentile
FROM v_rankings_players_current r
LEFT JOIN v_player_league_percentiles p 
    ON r.player_id = p.player_id 
    AND r.season_id = p.season_id;

-- Game roster with all stats (improves boxscores)
CREATE OR REPLACE VIEW v_game_roster_comprehensive AS
SELECT 
    r.*,
    -- Add player stats
    COALESCE(p.goals, 0) as goals,
    COALESCE(p.assists, 0) as assists,
    COALESCE(p.points, 0) as points,
    COALESCE(p.toi_seconds, 0) as toi_seconds,
    COALESCE(p.plus_minus, 0) as plus_minus,
    COALESCE(p.shots, p.sog, 0) as shots,
    COALESCE(p.war, 0) as war,
    COALESCE(p.game_score, 0) as game_score
FROM fact_gameroster r
LEFT JOIN fact_player_game_stats p 
    ON r.game_id = p.game_id 
    AND r.player_id = p.player_id;

-- ============================================================================
-- SECTION 16: GOALIE SITUATIONAL SPLITS
-- ============================================================================

-- Goalie stats by strength (5v5, PP, PK)
CREATE OR REPLACE VIEW v_goalie_stats_by_strength AS
-- Note: Goalie stats don't have explicit strength splits in fact_goalie_game_stats
-- This would need to be calculated from shift data or estimated
-- Placeholder view structure for future implementation
SELECT 
    g.player_id,
    g.player_name,
    g.team_id,
    g.team_name,
    g.season_id,
    g.season,
    'All' as strength,
    COUNT(DISTINCT g.game_id) as games_played,
    SUM(COALESCE(g.saves, 0)) as saves,
    SUM(COALESCE(g.goals_against, 0)) as goals_against,
    SUM(COALESCE(g.shots_against, g.saves + g.goals_against, 0)) as shots_against,
    CASE 
        WHEN SUM(COALESCE(g.shots_against, g.saves + g.goals_against, 0)) > 0 
        THEN ROUND(SUM(COALESCE(g.saves, 0))::numeric / 
                   SUM(COALESCE(g.shots_against, g.saves + g.goals_against, 0)) * 100, 2)
        ELSE 0 
    END as save_pct
FROM fact_goalie_game_stats g
GROUP BY g.player_id, g.player_name, g.team_id, g.team_name, g.season_id, g.season;

-- Goalie stats by period (aggregated)
CREATE OR REPLACE VIEW v_goalie_stats_by_period AS
SELECT 
    g.player_id,
    g.player_name,
    g.team_id,
    g.team_name,
    g.season_id,
    g.season,
    'P1' as period,
    COUNT(DISTINCT g.game_id) as games_played,
    SUM(COALESCE(g.p1_saves, 0)) as saves,
    SUM(COALESCE(g.p1_goals_against, 0)) as goals_against,
    SUM(COALESCE(g.p1_shots_against, 0)) as shots_against,
    AVG(COALESCE(g.p1_sv_pct, 0)) as avg_sv_pct
FROM fact_goalie_game_stats g
GROUP BY g.player_id, g.player_name, g.team_id, g.team_name, g.season_id, g.season

UNION ALL

SELECT 
    g.player_id,
    g.player_name,
    g.team_id,
    g.team_name,
    g.season_id,
    g.season,
    'P2' as period,
    COUNT(DISTINCT g.game_id) as games_played,
    SUM(COALESCE(g.p2_saves, 0)) as saves,
    SUM(COALESCE(g.p2_goals_against, 0)) as goals_against,
    SUM(COALESCE(g.p2_shots_against, 0)) as shots_against,
    AVG(COALESCE(g.p2_sv_pct, 0)) as avg_sv_pct
FROM fact_goalie_game_stats g
GROUP BY g.player_id, g.player_name, g.team_id, g.team_name, g.season_id, g.season

UNION ALL

SELECT 
    g.player_id,
    g.player_name,
    g.team_id,
    g.team_name,
    g.season_id,
    g.season,
    'P3' as period,
    COUNT(DISTINCT g.game_id) as games_played,
    SUM(COALESCE(g.p3_saves, 0)) as saves,
    SUM(COALESCE(g.p3_goals_against, 0)) as goals_against,
    SUM(COALESCE(g.p3_shots_against, 0)) as shots_against,
    AVG(COALESCE(g.p3_sv_pct, 0)) as avg_sv_pct
FROM fact_goalie_game_stats g
GROUP BY g.player_id, g.player_name, g.team_id, g.team_name, g.season_id, g.season;

-- ============================================================================
-- SECTION 17: TEAM SITUATIONAL SPLITS
-- ============================================================================

-- Team stats by strength (5v5, PP, PK)
CREATE OR REPLACE VIEW v_team_stats_by_strength AS
SELECT 
    t.team_id,
    t.team_name,
    t.season_id,
    t.season,
    '5v5' as strength,
    t.games_played,
    -- Aggregate from player stats for this team
    COALESCE(
        (SELECT SUM(p.ev_goals) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id AND p.season_id = t.season_id
         GROUP BY p.team_id),
        t.goals_for
    ) as goals_for_estimated,
    COALESCE(
        (SELECT AVG(p.ev_cf_pct) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id AND p.season_id = t.season_id
         GROUP BY p.team_id),
        50.0
    ) as avg_cf_pct
FROM fact_team_season_stats_basic t
WHERE t.game_type = 'All'

UNION ALL

SELECT 
    t.team_id,
    t.team_name,
    t.season_id,
    t.season,
    'PP' as strength,
    t.games_played,
    COALESCE(
        (SELECT SUM(p.pp_goals) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id AND p.season_id = t.season_id
         GROUP BY p.team_id),
        0
    ) as goals_for_estimated,
    COALESCE(
        (SELECT AVG(p.pp_cf_pct) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id AND p.season_id = t.season_id
         GROUP BY p.team_id),
        50.0
    ) as avg_cf_pct
FROM fact_team_season_stats_basic t
WHERE t.game_type = 'All'

UNION ALL

SELECT 
    t.team_id,
    t.team_name,
    t.season_id,
    t.season,
    'PK' as strength,
    t.games_played,
    COALESCE(
        (SELECT SUM(p.pk_goals) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id AND p.season_id = t.season_id
         GROUP BY p.team_id),
        0
    ) as goals_for_estimated,
    COALESCE(
        (SELECT AVG(p.pk_cf_pct) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id AND p.season_id = t.season_id
         GROUP BY p.team_id),
        50.0
    ) as avg_cf_pct
FROM fact_team_season_stats_basic t
WHERE t.game_type = 'All';

-- ============================================================================
-- SECTION 18: ON-ICE COMBINATIONS (Who's On Ice Together)
-- ============================================================================

-- Player linemate stats (who they play with most)
CREATE OR REPLACE VIEW v_player_linemates AS
SELECT 
    sp1.player_id as player_id,
    sp1.player_name as player_name,
    sp2.player_id as linemate_id,
    sp2.player_name as linemate_name,
    COUNT(DISTINCT sp1.shift_id) as shifts_together,
    SUM(sp1.shift_duration) as toi_together_seconds,
    ROUND(SUM(sp1.shift_duration)::numeric / 60, 2) as toi_together_minutes,
    AVG(sp1.cf_pct) as avg_cf_pct_together,
    SUM(COALESCE(sp1.gf, 0)) as goals_for_together,
    SUM(COALESCE(sp1.ga, 0)) as goals_against_together
FROM fact_shift_players sp1
JOIN fact_shift_players sp2 
    ON sp1.shift_id = sp2.shift_id 
    AND sp1.player_id != sp2.player_id
    AND sp1.venue = sp2.venue
WHERE sp1.player_id != ''
GROUP BY sp1.player_id, sp1.player_name, sp2.player_id, sp2.player_name
HAVING COUNT(DISTINCT sp1.shift_id) >= 5
ORDER BY sp1.player_id, toi_together_seconds DESC;

-- ============================================================================
-- SECTION 19: RUSH ANALYSIS - COMPREHENSIVE
-- ============================================================================

-- Rush stats comprehensive (offensive and defensive)
CREATE OR REPLACE VIEW v_player_rush_comprehensive AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    COUNT(DISTINCT p.game_id) as games_played,
    
    -- Offensive Rush Stats
    SUM(COALESCE(p.rush_shots, 0)) as rush_shots,
    SUM(COALESCE(p.rush_goals, 0)) as rush_goals,
    SUM(COALESCE(p.rush_assists, 0)) as rush_assists,
    SUM(COALESCE(p.rush_points, 0)) as rush_points,
    CASE 
        WHEN SUM(COALESCE(p.rush_shots, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.rush_goals, 0))::numeric / SUM(COALESCE(p.rush_shots, 0)) * 100, 2)
        ELSE 0 
    END as rush_shooting_pct,
    SUM(COALESCE(p.rush_involvement, 0)) as rush_involvement,
    SUM(COALESCE(p.rush_primary, 0)) as rush_as_primary,
    SUM(COALESCE(p.rush_support, 0)) as rush_as_support,
    
    -- Rush Success Metrics
    SUM(COALESCE(p.rush_off_success, 0)) as rush_off_success,
    CASE 
        WHEN SUM(COALESCE(p.rush_involvement, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.rush_off_success, 0))::numeric / 
                   SUM(COALESCE(p.rush_involvement, 0)) * 100, 2)
        ELSE 0 
    END as rush_off_success_pct,
    SUM(COALESCE(p.rush_off_shot_generated, 0)) as rush_shots_generated,
    SUM(COALESCE(p.rush_off_goal_generated, 0)) as rush_goals_generated,
    
    -- Defensive Rush Stats
    SUM(COALESCE(p.rush_primary_def, 0)) as rush_def_as_primary,
    SUM(COALESCE(p.rush_def_support, 0)) as rush_def_as_support,
    SUM(COALESCE(p.rush_def_involvement, 0)) as rush_def_involvement,
    SUM(COALESCE(p.rush_def_success, 0)) as rush_def_success,
    CASE 
        WHEN SUM(COALESCE(p.rush_def_involvement, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.rush_def_success, 0))::numeric / 
                   SUM(COALESCE(p.rush_def_involvement, 0)) * 100, 2)
        ELSE 0 
    END as rush_def_success_pct,
    SUM(COALESCE(p.rush_def_ga, 0)) as rush_goals_against,
    
    -- Calculated Rush Stats (stricter definition)
    SUM(COALESCE(p.rush_calc_off, 0)) as rush_calc_offensive,
    SUM(COALESCE(p.rush_calc_def, 0)) as rush_calc_defensive,
    SUM(COALESCE(p.rush_calc_off_goal, 0)) as rush_calc_goals,
    SUM(COALESCE(p.rush_calc_def_ga, 0)) as rush_calc_ga
    
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season;

-- ============================================================================
-- SECTION 20: ZONE PLAY - ENTRY/EXIT ANALYSIS
-- ============================================================================

-- Zone entry/exit comprehensive analysis
CREATE OR REPLACE VIEW v_player_zone_play_comprehensive AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    COUNT(DISTINCT p.game_id) as games_played,
    
    -- Zone Entry Totals
    SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) as zone_entries_total,
    SUM(COALESCE(p.zone_entry_controlled, p.zone_ent_controlled, 0)) as zone_entries_controlled,
    SUM(COALESCE(p.zone_entry_uncontrolled, 0)) as zone_entries_uncontrolled,
    SUM(COALESCE(p.zone_entries_successful, p.zone_ent_successful, 0)) as zone_entries_successful,
    
    -- Zone Entry Rates
    CASE 
        WHEN SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.zone_entry_controlled, p.zone_ent_controlled, 0))::numeric / 
                   SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) * 100, 2)
        ELSE 0 
    END as controlled_entry_rate,
    CASE 
        WHEN SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.zone_entries_successful, p.zone_ent_successful, 0))::numeric / 
                   SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) * 100, 2)
        ELSE 0 
    END as entry_success_rate,
    
    -- Zone Entry → Shot/Goal Conversion
    SUM(COALESCE(p.zone_ent_shot_generated, 0)) as entries_led_to_shot,
    SUM(COALESCE(p.zone_ent_controlled_shot, 0)) as controlled_entries_led_to_shot,
    SUM(COALESCE(p.zone_ent_goal_generated, 0)) as entries_led_to_goal,
    SUM(COALESCE(p.zone_ent_controlled_goal, 0)) as controlled_entries_led_to_goal,
    CASE 
        WHEN SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.zone_ent_shot_generated, 0))::numeric / 
                   SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) * 100, 2)
        ELSE 0 
    END as entry_to_shot_rate,
    CASE 
        WHEN SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.zone_ent_goal_generated, 0))::numeric / 
                   SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) * 100, 2)
        ELSE 0 
    END as entry_to_goal_rate,
    
    -- Zone Exit Totals
    SUM(COALESCE(p.zone_exits, p.zone_ext, 0)) as zone_exits_total,
    SUM(COALESCE(p.zone_exit_controlled, p.zone_ext_controlled, 0)) as zone_exits_controlled,
    SUM(COALESCE(p.zone_exit_uncontrolled, 0)) as zone_exits_uncontrolled,
    SUM(COALESCE(p.zone_exits_successful, p.zone_ext_successful, 0)) as zone_exits_successful,
    
    -- Zone Exit Rates
    CASE 
        WHEN SUM(COALESCE(p.zone_exits, p.zone_ext, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.zone_exit_controlled, p.zone_ext_controlled, 0))::numeric / 
                   SUM(COALESCE(p.zone_exits, p.zone_ext, 0)) * 100, 2)
        ELSE 0 
    END as controlled_exit_rate,
    CASE 
        WHEN SUM(COALESCE(p.zone_exits, p.zone_ext, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.zone_exits_successful, p.zone_ext_successful, 0))::numeric / 
                   SUM(COALESCE(p.zone_exits, p.zone_ext, 0)) * 100, 2)
        ELSE 0 
    END as exit_success_rate,
    
    -- Zone Entry Denials (Defensive)
    SUM(COALESCE(p.zone_entry_denials, 0)) as zone_entry_denials,
    
    -- Per-60 Rates
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.zone_entries, p.zone_ent, 0))::numeric * 3600 / 
                   SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as zone_entries_per_60,
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.zone_exits, p.zone_ext, 0))::numeric * 3600 / 
                   SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as zone_exits_per_60
    
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season;

-- ============================================================================
-- SECTION 21: PLAYMAKING & SHOT ASSISTS
-- ============================================================================

-- Comprehensive playmaking stats
CREATE OR REPLACE VIEW v_player_playmaking_comprehensive AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    COUNT(DISTINCT p.game_id) as games_played,
    
    -- Shot Assists
    SUM(COALESCE(p.shot_assists, 0)) as shot_assists,
    SUM(COALESCE(p.goal_creating_actions, 0)) as goal_creating_actions,
    SUM(COALESCE(p.pre_shot_touches, 0)) as pre_shot_touches,
    
    -- Pass Types Leading to Shots
    SUM(COALESCE(p.passes_royal_road, 0)) as royal_road_passes,
    SUM(COALESCE(p.passes_cross_ice, 0)) as cross_ice_passes,
    SUM(COALESCE(p.passes_slot, 0)) as slot_passes,
    SUM(COALESCE(p.passes_behind_net, 0)) as behind_net_passes,
    SUM(COALESCE(p.passes_breakout, 0)) as breakout_passes,
    
    -- Sequence Involvement
    SUM(COALESCE(p.sequences_involved, 0)) as sequences_involved,
    SUM(COALESCE(p.sog_sequences, 0)) as sequences_led_to_shot,
    SUM(COALESCE(p.goal_sequences, 0)) as sequences_led_to_goal,
    CASE 
        WHEN SUM(COALESCE(p.sequences_involved, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.sog_sequences, 0))::numeric / 
                   SUM(COALESCE(p.sequences_involved, 0)) * 100, 2)
        ELSE 0 
    END as sequence_to_shot_rate,
    CASE 
        WHEN SUM(COALESCE(p.sequences_involved, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.goal_sequences, 0))::numeric / 
                   SUM(COALESCE(p.sequences_involved, 0)) * 100, 2)
        ELSE 0 
    END as sequence_to_goal_rate,
    
    -- Playmaking Index
    AVG(COALESCE(p.playmaking_index, 0)) as avg_playmaking_index,
    
    -- Per-60 Rates
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.shot_assists, 0))::numeric * 3600 / 
                   SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as shot_assists_per_60
    
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season;

-- ============================================================================
-- SECTION 22: PRESSURE & POISE METRICS
-- ============================================================================

-- Comprehensive pressure handling stats
CREATE OR REPLACE VIEW v_player_pressure_comprehensive AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    COUNT(DISTINCT p.game_id) as games_played,
    
    -- Pressure Events
    SUM(COALESCE(p.plays_under_pressure, 0)) as plays_under_pressure,
    SUM(COALESCE(p.plays_not_pressured, 0)) as plays_not_pressured,
    CASE 
        WHEN SUM(COALESCE(p.plays_under_pressure, 0)) + SUM(COALESCE(p.plays_not_pressured, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.plays_under_pressure, 0))::numeric / 
                   (SUM(COALESCE(p.plays_under_pressure, 0)) + SUM(COALESCE(p.plays_not_pressured, 0))) * 100, 2)
        ELSE 0 
    END as pressure_rate,
    
    -- Pressure Success
    SUM(COALESCE(p.pressure_success_count, 0)) as pressure_success_count,
    CASE 
        WHEN SUM(COALESCE(p.plays_under_pressure, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.pressure_success_count, 0))::numeric / 
                   SUM(COALESCE(p.plays_under_pressure, 0)) * 100, 2)
        ELSE 0 
    END as pressure_success_rate,
    
    -- Unpressured Success (for comparison)
    CASE 
        WHEN SUM(COALESCE(p.plays_not_pressured, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.plays_successful, 0))::numeric - 
                   SUM(COALESCE(p.pressure_success_count, 0))::numeric / 
                   SUM(COALESCE(p.plays_not_pressured, 0)) * 100, 2)
        ELSE 0 
    END as unpressured_success_rate,
    
    -- Pressure Differential (how much success drops under pressure)
    CASE 
        WHEN SUM(COALESCE(p.plays_not_pressured, 0)) > 0 AND SUM(COALESCE(p.plays_under_pressure, 0)) > 0 
        THEN ROUND(
            (SUM(COALESCE(p.plays_successful, 0))::numeric - 
             SUM(COALESCE(p.pressure_success_count, 0))::numeric) / 
            SUM(COALESCE(p.plays_not_pressured, 0)) * 100 -
            SUM(COALESCE(p.pressure_success_count, 0))::numeric / 
            SUM(COALESCE(p.plays_under_pressure, 0)) * 100,
            2
        )
        ELSE 0 
    END as pressure_differential,
    
    -- Pressure Giveaways
    SUM(COALESCE(p.pressure_giveaways, 0)) as pressure_giveaways,
    
    -- Poise Index
    AVG(COALESCE(p.poise_index, 0)) as avg_poise_index
    
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season;

-- ============================================================================
-- SECTION 23: MATERIALIZED VIEW - PLAYER CAREER BY SITUATION
-- ============================================================================

-- Materialized view for player career stats by situation (very expensive)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_player_career_by_situation AS
SELECT 
    p.player_id,
    p.player_name,
    COUNT(DISTINCT p.season_id) as seasons_played,
    COUNT(DISTINCT p.game_id) as career_games,
    
    -- Career Totals (All Situations)
    SUM(COALESCE(p.goals, 0)) as career_goals,
    SUM(COALESCE(p.assists, 0)) as career_assists,
    SUM(COALESCE(p.points, 0)) as career_points,
    SUM(COALESCE(p.war, 0)) as career_war,
    SUM(COALESCE(p.gar_total, p.gar, 0)) as career_gar,
    
    -- 5v5 Career
    SUM(COALESCE(p.ev_goals, p.goals_5v5, 0)) as career_ev_goals,
    SUM(COALESCE(p.ev_points, 0)) as career_ev_points,
    AVG(COALESCE(p.ev_cf_pct, 0)) as career_ev_cf_pct,
    
    -- PP Career
    SUM(COALESCE(p.pp_goals, 0)) as career_pp_goals,
    SUM(COALESCE(p.pp_points, 0)) as career_pp_points,
    
    -- PK Career
    SUM(COALESCE(p.pk_goals, 0)) as career_pk_goals,
    AVG(COALESCE(p.pk_cf_pct, 0)) as career_pk_cf_pct,
    
    -- Period Career
    SUM(COALESCE(p.p1_goals, 0)) as career_p1_goals,
    SUM(COALESCE(p.p2_goals, 0)) as career_p2_goals,
    SUM(COALESCE(p.p3_goals, 0)) as career_p3_goals,
    AVG(COALESCE(p.p3_clutch_diff, 0)) as avg_p3_clutch_diff
    
FROM fact_player_game_stats p
GROUP BY p.player_id, p.player_name;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_mv_player_career_by_situation_player_id 
ON mv_player_career_by_situation(player_id);

-- ============================================================================
-- SECTION 24: TEAM ADVANCED STATS (From Player Aggregation)
-- ============================================================================

-- Team advanced stats aggregated from players
CREATE OR REPLACE VIEW v_team_advanced_stats AS
SELECT 
    t.team_id,
    t.team_name,
    t.season_id,
    t.season,
    t.games_played,
    t.wins,
    t.losses,
    t.ties,
    t.points,
    
    -- Team Advanced Metrics (from players)
    COALESCE(
        (SELECT AVG(p.cf_pct) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id AND p.season_id = t.season_id
         GROUP BY p.team_id),
        50.0
    ) as team_cf_pct,
    COALESCE(
        (SELECT AVG(p.ff_pct) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id AND p.season_id = t.season_id
         GROUP BY p.team_id),
        50.0
    ) as team_ff_pct,
    COALESCE(
        (SELECT SUM(p.gar_total) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id AND p.season_id = t.season_id
         GROUP BY p.team_id),
        0
    ) as team_gar_total,
    COALESCE(
        (SELECT AVG(p.war) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id AND p.season_id = t.season_id
         GROUP BY p.team_id),
        0
    ) as team_avg_war,
    
    -- Team Micro Stats
    COALESCE(
        (SELECT AVG(p.controlled_entry_pct) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id AND p.season_id = t.season_id
           AND p.zone_entries > 0
         GROUP BY p.team_id),
        0
    ) as team_controlled_entry_pct,
    COALESCE(
        (SELECT SUM(p.rush_points) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id AND p.season_id = t.season_id
         GROUP BY p.team_id),
        0
    ) as team_rush_points,
    
    -- Team xG
    COALESCE(
        (SELECT SUM(p.xg_for) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id AND p.season_id = t.season_id
         GROUP BY p.team_id),
        0
    ) as team_xg_total,
    COALESCE(
        (SELECT SUM(p.goals) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id AND p.season_id = t.season_id
         GROUP BY p.team_id),
        t.goals_for
    ) as team_goals_actual,
    COALESCE(
        (SELECT SUM(p.goals) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id AND p.season_id = t.season_id
         GROUP BY p.team_id),
        t.goals_for
    )::numeric - COALESCE(
        (SELECT SUM(p.xg_for) 
         FROM fact_player_game_stats p 
         WHERE p.team_id = t.team_id AND p.season_id = t.season_id
         GROUP BY p.team_id),
        0
    )::numeric as team_goals_above_xg
    
FROM fact_team_season_stats_basic t
WHERE t.game_type = 'All';

-- ============================================================================
-- SECTION 25: DASHBOARD PERFORMANCE IMPROVEMENTS
-- ============================================================================

-- View to replace JavaScript aggregation in player page (possession stats)
CREATE OR REPLACE VIEW v_player_possession_aggregated AS
SELECT 
    p.player_id,
    p.season_id,
    COUNT(DISTINCT p.game_id) as games,
    SUM(COALESCE(p.corsi_for, p.cf, 0)) as cf,
    SUM(COALESCE(p.corsi_against, p.ca, 0)) as ca,
    SUM(COALESCE(p.fenwick_for, p.ff, 0)) as ff,
    SUM(COALESCE(p.fenwick_against, p.fa, 0)) as fa,
    SUM(COALESCE(p.xg_for, p.xg, 0)) as xg,
    SUM(COALESCE(p.goals, 0)) as goals,
    SUM(COALESCE(p.goals_for, p.gf, 0)) as goals_for,
    SUM(COALESCE(p.goals_against, p.ga, 0)) as goals_against,
    SUM(COALESCE(p.plus_ev, 0)) as plus_ev,
    SUM(COALESCE(p.minus_ev, 0)) as minus_ev,
    SUM(COALESCE(p.plus_minus_ev, 0)) as plus_minus_ev,
    AVG(COALESCE(p.cf_pct_rel, 0)) as avg_cf_pct_rel,
    AVG(COALESCE(p.ff_pct_rel, 0)) as avg_ff_pct_rel,
    CASE 
        WHEN SUM(COALESCE(p.corsi_for, p.cf, 0)) + SUM(COALESCE(p.corsi_against, p.ca, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.corsi_for, p.cf, 0))::numeric / 
                   (SUM(COALESCE(p.corsi_for, p.cf, 0)) + SUM(COALESCE(p.corsi_against, p.ca, 0))) * 100, 2)
        ELSE 0 
    END as cf_pct,
    CASE 
        WHEN SUM(COALESCE(p.fenwick_for, p.ff, 0)) + SUM(COALESCE(p.fenwick_against, p.fa, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.fenwick_for, p.ff, 0))::numeric / 
                   (SUM(COALESCE(p.fenwick_for, p.ff, 0)) + SUM(COALESCE(p.fenwick_against, p.fa, 0))) * 100, 2)
        ELSE 0 
    END as ff_pct,
    CASE 
        WHEN SUM(COALESCE(p.goals_for, p.gf, 0)) + SUM(COALESCE(p.goals_against, p.ga, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.goals_for, p.gf, 0))::numeric / 
                   (SUM(COALESCE(p.goals_for, p.gf, 0)) + SUM(COALESCE(p.goals_against, p.ga, 0))) * 100, 2)
        ELSE 0 
    END as gf_pct,
    ROUND(SUM(COALESCE(p.goals, 0))::numeric - SUM(COALESCE(p.xg_for, p.xg, 0))::numeric, 2) as xg_diff
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.season_id;

-- View to replace JavaScript aggregation in player page (zone stats)
CREATE OR REPLACE VIEW v_player_zone_aggregated AS
SELECT 
    p.player_id,
    p.season_id,
    SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) as ze,
    SUM(COALESCE(p.zone_entries_successful, p.zone_ent_successful, 0)) as ze_success,
    SUM(COALESCE(p.zone_entry_controlled, p.zone_ent_controlled, 0)) as ze_controlled,
    SUM(COALESCE(p.zone_exits, p.zone_ext, 0)) as zx,
    SUM(COALESCE(p.zone_exits_successful, p.zone_ext_successful, 0)) as zx_success,
    SUM(COALESCE(p.zone_exit_controlled, p.zone_ext_controlled, 0)) as zx_controlled,
    CASE 
        WHEN SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.zone_entries_successful, p.zone_ent_successful, 0))::numeric / 
                   SUM(COALESCE(p.zone_entries, p.zone_ent, 0)) * 100, 2)
        ELSE 0 
    END as ze_pct,
    CASE 
        WHEN SUM(COALESCE(p.zone_exits, p.zone_ext, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.zone_exits_successful, p.zone_ext_successful, 0))::numeric / 
                   SUM(COALESCE(p.zone_exits, p.zone_ext, 0)) * 100, 2)
        ELSE 0 
    END as zx_pct
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.season_id;

-- View to replace JavaScript aggregation in player page (WAR/GAR)
CREATE OR REPLACE VIEW v_player_war_gar_aggregated AS
SELECT 
    p.player_id,
    p.season_id,
    COUNT(DISTINCT p.game_id) as games,
    SUM(COALESCE(p.gar_total, p.gar, 0)) as total_gar,
    AVG(COALESCE(p.war, 0)) as avg_war,
    AVG(COALESCE(p.game_score, 0)) as avg_game_score,
    AVG(COALESCE(p.player_rating, 0)) as avg_rating,
    AVG(COALESCE(p.performance_index, 0)) as avg_performance_index,
    AVG(COALESCE(p.adjusted_rating, 0)) as avg_adjusted_rating
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.season_id;

-- View to replace JavaScript aggregation in player page (physical stats)
CREATE OR REPLACE VIEW v_player_physical_aggregated AS
SELECT 
    p.player_id,
    p.season_id,
    SUM(COALESCE(p.hits, 0)) as hits,
    SUM(COALESCE(p.blocks, 0)) as blocks,
    SUM(COALESCE(p.takeaways, 0)) as takeaways,
    SUM(COALESCE(p.giveaways, 0)) as giveaways,
    SUM(COALESCE(p.bad_giveaways, 0)) as bad_giveaways,
    SUM(COALESCE(p.takeaways, 0))::numeric - SUM(COALESCE(p.giveaways, 0))::numeric as turnover_diff
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.season_id;

-- View to replace JavaScript aggregation in player page (shooting stats)
CREATE OR REPLACE VIEW v_player_shooting_aggregated AS
SELECT 
    p.player_id,
    p.season_id,
    SUM(COALESCE(p.shots, p.sog, 0)) as shots,
    SUM(COALESCE(p.sog, p.shots_on_goal, 0)) as shots_on_goal,
    SUM(COALESCE(p.goals, 0)) as goals,
    CASE 
        WHEN SUM(COALESCE(p.sog, p.shots_on_goal, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.goals, 0))::numeric / 
                   SUM(COALESCE(p.sog, p.shots_on_goal, 0)) * 100, 2)
        ELSE 0 
    END as shooting_pct,
    AVG(COALESCE(p.shooting_pct, 0)) as avg_shooting_pct
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.season_id;

-- View to replace JavaScript aggregation in player page (per-60 stats)
CREATE OR REPLACE VIEW v_player_per60_aggregated AS
SELECT 
    p.player_id,
    p.season_id,
    SUM(COALESCE(p.toi_seconds, 0)) as toi_seconds,
    SUM(COALESCE(p.goals, 0)) as goals,
    SUM(COALESCE(p.assists, 0)) as assists,
    SUM(COALESCE(p.points, 0)) as points,
    SUM(COALESCE(p.sog, p.shots_on_goal, 0)) as shots,
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.goals, 0))::numeric * 3600 / SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as goals_per_60,
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.assists, 0))::numeric * 3600 / SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as assists_per_60,
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.points, 0))::numeric * 3600 / SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as points_per_60,
    CASE 
        WHEN SUM(COALESCE(p.toi_seconds, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.sog, p.shots_on_goal, 0))::numeric * 3600 / SUM(COALESCE(p.toi_seconds, 0)), 2)
        ELSE 0 
    END as shots_per_60
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.season_id;

-- View to replace JavaScript aggregation in player page (faceoff stats)
CREATE OR REPLACE VIEW v_player_faceoff_aggregated AS
SELECT 
    p.player_id,
    p.season_id,
    SUM(COALESCE(p.fo_wins, 0)) as fo_wins,
    SUM(COALESCE(p.fo_losses, 0)) as fo_losses,
    SUM(COALESCE(p.fo_total, p.fo_wins + p.fo_losses, 0)) as fo_total,
    CASE 
        WHEN SUM(COALESCE(p.fo_total, p.fo_wins + p.fo_losses, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.fo_wins, 0))::numeric / 
                   SUM(COALESCE(p.fo_total, p.fo_wins + p.fo_losses, 0)) * 100, 2)
        ELSE 0 
    END as fo_pct,
    CASE 
        WHEN COUNT(DISTINCT p.game_id) > 0 
        THEN ROUND(SUM(COALESCE(p.fo_wins, 0))::numeric / COUNT(DISTINCT p.game_id), 2)
        ELSE 0 
    END as fo_wins_per_game
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.season_id;

-- View to replace JavaScript aggregation in player page (passing stats)
CREATE OR REPLACE VIEW v_player_passing_aggregated AS
SELECT 
    p.player_id,
    p.season_id,
    SUM(COALESCE(p.pass_attempts, p.passes_attempted, 0)) as pass_attempts,
    SUM(COALESCE(p.pass_completed, p.passes_completed, 0)) as pass_completed,
    CASE 
        WHEN SUM(COALESCE(p.pass_attempts, p.passes_attempted, 0)) > 0 
        THEN ROUND(SUM(COALESCE(p.pass_completed, p.passes_completed, 0))::numeric / 
                   SUM(COALESCE(p.pass_attempts, p.passes_attempted, 0)) * 100, 2)
        ELSE 0 
    END as pass_completion_pct,
    CASE 
        WHEN COUNT(DISTINCT p.game_id) > 0 
        THEN ROUND(SUM(COALESCE(p.pass_attempts, p.passes_attempted, 0))::numeric / COUNT(DISTINCT p.game_id), 2)
        ELSE 0 
    END as pass_attempts_per_game
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.season_id;

-- View to replace JavaScript aggregation in player page (situational stats)
CREATE OR REPLACE VIEW v_player_situational_aggregated AS
SELECT 
    p.player_id,
    p.season_id,
    SUM(COALESCE(p.ev_toi_seconds, p.toi_5v5, 0)) as toi_5v5,
    SUM(COALESCE(p.ev_goals, p.goals_5v5, 0)) as goals_5v5,
    SUM(COALESCE(p.pp_toi_seconds, p.toi_pp, 0)) as toi_pp,
    SUM(COALESCE(p.pp_goals, 0)) as goals_pp,
    SUM(COALESCE(p.pk_toi_seconds, p.toi_pk, 0)) as toi_pk,
    SUM(COALESCE(p.pk_goals, 0)) as goals_pk
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.season_id;

-- ============================================================================
-- SECTION 26: GAME-LEVEL AGGREGATIONS (For Game Pages)
-- ============================================================================

-- Game comprehensive stats (aggregated from players)
CREATE OR REPLACE VIEW v_game_comprehensive_stats AS
SELECT 
    s.game_id,
    s.season_id,
    s.date,
    s.home_team_id,
    s.home_team_name,
    s.away_team_id,
    s.away_team_name,
    s.home_total_goals,
    s.away_total_goals,
    
    -- Home Team Aggregates
    COALESCE(
        (SELECT SUM(p.goals) 
         FROM fact_player_game_stats p 
         WHERE p.game_id = s.game_id AND p.team_id = s.home_team_id),
        0
    ) as home_goals_from_stats,
    COALESCE(
        (SELECT AVG(p.cf_pct) 
         FROM fact_player_game_stats p 
         WHERE p.game_id = s.game_id AND p.team_id = s.home_team_id),
        50.0
    ) as home_avg_cf_pct,
    COALESCE(
        (SELECT SUM(p.war) 
         FROM fact_player_game_stats p 
         WHERE p.game_id = s.game_id AND p.team_id = s.home_team_id),
        0
    ) as home_total_war,
    
    -- Away Team Aggregates
    COALESCE(
        (SELECT SUM(p.goals) 
         FROM fact_player_game_stats p 
         WHERE p.game_id = s.game_id AND p.team_id = s.away_team_id),
        0
    ) as away_goals_from_stats,
    COALESCE(
        (SELECT AVG(p.cf_pct) 
         FROM fact_player_game_stats p 
         WHERE p.game_id = s.game_id AND p.team_id = s.away_team_id),
        50.0
    ) as away_avg_cf_pct,
    COALESCE(
        (SELECT SUM(p.war) 
         FROM fact_player_game_stats p 
         WHERE p.game_id = s.game_id AND p.team_id = s.away_team_id),
        0
    ) as away_total_war
    
FROM dim_schedule s
WHERE s.home_total_goals IS NOT NULL;

-- ============================================================================
-- SECTION 27: ROLLING AVERAGES & TRENDS
-- ============================================================================

-- Rolling averages view (last N games)
CREATE OR REPLACE VIEW v_player_rolling_averages AS
WITH ranked_games AS (
    SELECT 
        p.*,
        s.date,
        ROW_NUMBER() OVER (PARTITION BY p.player_id, p.season_id ORDER BY s.date DESC, s.game_id DESC) as game_rank
    FROM fact_player_game_stats p
    JOIN dim_schedule s ON p.game_id = s.game_id
    WHERE (p.game_type = 'All' OR p.game_type IS NULL)
)
SELECT 
    p.player_id,
    p.player_name,
    p.season_id,
    p.season,
    
    -- Last 5 Games
    COUNT(DISTINCT CASE WHEN p.game_rank <= 5 THEN p.game_id END) as games_last_5,
    SUM(CASE WHEN p.game_rank <= 5 THEN COALESCE(p.points, 0) ELSE 0 END) as points_last_5,
    AVG(CASE WHEN p.game_rank <= 5 THEN COALESCE(p.points, 0) ELSE NULL END) as avg_points_last_5,
    AVG(CASE WHEN p.game_rank <= 5 THEN COALESCE(p.war, 0) ELSE NULL END) as avg_war_last_5,
    AVG(CASE WHEN p.game_rank <= 5 THEN COALESCE(p.cf_pct, 0) ELSE NULL END) as avg_cf_pct_last_5,
    
    -- Last 10 Games
    COUNT(DISTINCT CASE WHEN p.game_rank <= 10 THEN p.game_id END) as games_last_10,
    SUM(CASE WHEN p.game_rank <= 10 THEN COALESCE(p.points, 0) ELSE 0 END) as points_last_10,
    AVG(CASE WHEN p.game_rank <= 10 THEN COALESCE(p.points, 0) ELSE NULL END) as avg_points_last_10,
    AVG(CASE WHEN p.game_rank <= 10 THEN COALESCE(p.war, 0) ELSE NULL END) as avg_war_last_10,
    AVG(CASE WHEN p.game_rank <= 10 THEN COALESCE(p.cf_pct, 0) ELSE NULL END) as avg_cf_pct_last_10,
    
    -- Last 20 Games
    COUNT(DISTINCT CASE WHEN p.game_rank <= 20 THEN p.game_id END) as games_last_20,
    SUM(CASE WHEN p.game_rank <= 20 THEN COALESCE(p.points, 0) ELSE 0 END) as points_last_20,
    AVG(CASE WHEN p.game_rank <= 20 THEN COALESCE(p.points, 0) ELSE NULL END) as avg_points_last_20,
    AVG(CASE WHEN p.game_rank <= 20 THEN COALESCE(p.war, 0) ELSE NULL END) as avg_war_last_20,
    AVG(CASE WHEN p.game_rank <= 20 THEN COALESCE(p.cf_pct, 0) ELSE NULL END) as avg_cf_pct_last_20
    
FROM ranked_games p
GROUP BY p.player_id, p.player_name, p.season_id, p.season;

-- ============================================================================
-- SECTION 28: MULTI-SEASON COMPARISONS
-- ============================================================================

-- Player stats across all seasons (for comparisons)
CREATE OR REPLACE VIEW v_player_all_seasons AS
SELECT 
    p.player_id,
    p.player_name,
    p.season_id,
    p.season,
    COUNT(DISTINCT p.game_id) as games_played,
    SUM(COALESCE(p.goals, 0)) as goals,
    SUM(COALESCE(p.assists, 0)) as assists,
    SUM(COALESCE(p.points, 0)) as points,
    AVG(COALESCE(p.war, 0)) as avg_war,
    SUM(COALESCE(p.war, 0)) as total_war,
    AVG(COALESCE(p.gar_total, p.gar, 0)) as avg_gar,
    SUM(COALESCE(p.gar_total, p.gar, 0)) as total_gar,
    AVG(COALESCE(p.cf_pct, 0)) as avg_cf_pct,
    AVG(COALESCE(p.game_score, 0)) as avg_game_score,
    RANK() OVER (PARTITION BY p.season_id ORDER BY SUM(COALESCE(p.points, 0)) DESC) as points_rank,
    RANK() OVER (PARTITION BY p.season_id ORDER BY AVG(COALESCE(p.war, 0)) DESC) as war_rank
FROM fact_player_game_stats p
WHERE (p.game_type = 'All' OR p.game_type IS NULL)
GROUP BY p.player_id, p.player_name, p.season_id, p.season
ORDER BY p.season_id DESC, SUM(COALESCE(p.points, 0)) DESC;

-- ============================================================================
-- SECTION 29: COMBINED SITUATIONAL VIEWS (Multi-Dimensional Filters)
-- ============================================================================

-- Player stats filtered by multiple dimensions (for flexible querying)
-- This view allows filtering by any combination of: season, team, strength, period, game_state, competition_tier
CREATE OR REPLACE VIEW v_player_stats_flexible AS
SELECT 
    p.player_id,
    p.player_name,
    p.team_id,
    p.team_name,
    p.season_id,
    p.season,
    s.game_type,
    COUNT(DISTINCT p.game_id) as games_played,
    
    -- Core Stats
    SUM(COALESCE(p.goals, 0)) as goals,
    SUM(COALESCE(p.assists, 0)) as assists,
    SUM(COALESCE(p.points, 0)) as points,
    
    -- Strength-specific (if filtering by strength)
    SUM(COALESCE(p.ev_goals, 0)) as ev_goals,
    SUM(COALESCE(p.pp_goals, 0)) as pp_goals,
    SUM(COALESCE(p.pk_goals, 0)) as pk_goals,
    
    -- Period-specific (if filtering by period)
    SUM(COALESCE(p.p1_goals, 0)) as p1_goals,
    SUM(COALESCE(p.p2_goals, 0)) as p2_goals,
    SUM(COALESCE(p.p3_goals, 0)) as p3_goals,
    
    -- Advanced
    SUM(COALESCE(p.war, 0)) as war_total,
    AVG(COALESCE(p.war, 0)) as avg_war,
    SUM(COALESCE(p.gar_total, p.gar, 0)) as gar_total,
    AVG(COALESCE(p.cf_pct, 0)) as avg_cf_pct
    
FROM fact_player_game_stats p
JOIN dim_schedule s ON p.game_id = s.game_id
WHERE (p.game_type = 'All' OR p.game_type IS NULL OR p.game_type = s.game_type)
GROUP BY p.player_id, p.player_name, p.team_id, p.team_name, p.season_id, p.season, s.game_type;

-- ============================================================================
-- SECTION 30: REFRESH MATERIALIZED VIEWS (Run after ETL)
-- ============================================================================

-- Uncomment and run after each ETL to refresh materialized views:
-- REFRESH MATERIALIZED VIEW mv_player_career_totals;
-- REFRESH MATERIALIZED VIEW mv_player_vs_opponent;
-- REFRESH MATERIALIZED VIEW mv_player_rolling_stats;
-- REFRESH MATERIALIZED VIEW mv_player_career_by_situation;

-- ============================================================================
-- END OF COMPREHENSIVE ADVANCED STATS VIEWS
-- ============================================================================
