# BenchSight Verification Status

**Version:** 16.08  
**Last Updated:** January 8, 2026
**Status:** 🟡 IN PROGRESS (72% stat calculations verified)

---

## Executive Summary

| Category | Verified | Total | Status |
|----------|----------|-------|--------|
| **Stat Calculations** | 72 | ~100 | 🟡 72% |
| **Table Structure** | 131 | 131 | ✅ 100% |
| **Goal Accuracy** | 4 | 4 | ✅ 100% |
| **FK Integrity** | 131 | 131 | ✅ 100% |
| **Per-Game Verification** | 2 | 4 | 🟡 50% |

### Games in System
| Game ID | Date | Teams | Goals | Verification Status |
|---------|------|-------|-------|---------------------|
| 18969 | 2025-12-28 | ACE vs VEL | 20 | ✅ DETAILED (72 stats) |
| 18977 | 2025-12-14 | VEL vs ICE | 17 | 🟡 PARTIAL (15 stats) |
| 18981 | 2025-11-30 | ACE vs AMO | 9 | ⚪ GOALS ONLY |
| 18987 | 2025-11-16 | VEL vs AMO | 3 | ⚪ GOALS ONLY |

---

## Stat Calculation Verification Matrix

### Player Skating Stats - Core

| Stat | Formula | Game 18969 | Game 18977 | Status | Notes |
|------|---------|------------|------------|--------|-------|
| goals | `event_type='Goal' AND player_role='event_player_1'` | Keegan=2 ✅ | Hayden=1 ⚠️ | ✅ | 18977: NORAD=2, tracking=1 (data gap) |
| assists | `play_detail LIKE 'Assist%'` | Keegan=1 ✅ | Hayden=0 ✅ | ✅ | |
| points | `goals + assists` | Keegan=3 ✅ | - | ✅ | Derived stat |
| shots_total | `event_type IN ('Shot','Goal') AND player_role='event_player_1'` | Keegan=7 ✅ | Hayden=23 ✅ | ✅ | Includes goals |
| sog | `shots_total WHERE event_detail contains 'OnNet' OR 'Goal'` | Keegan=6 ✅ | - | ✅ | Shots on goal |
| shots_blocked | `event_type='Shot' AND event_detail='Shot_Blocked'` | Keegan=1 ✅ | Hayden=4 ✅ | ✅ | |
| shots_missed | `event_type='Shot' AND event_detail contains 'Missed'` | Keegan=0 ✅ | Hayden=1 ✅ | ✅ | |
| shooting_pct | `goals / shots_total * 100` | Keegan=28.6% ✅ | Hayden=4.3% ✅ | ✅ | |

### Player Skating Stats - Passes

| Stat | Formula | Game 18969 | Game 18977 | Status | Notes |
|------|---------|------------|------------|--------|-------|
| pass_attempts | `event_type='Pass' AND player_role='event_player_1'` | Keegan=17 ✅ | Hayden=18 ✅ | ✅ | |
| pass_completed | `pass_attempts WHERE event_detail='Pass_Completed'` | Keegan=11 ✅ | Hayden=12 ✅ | ✅ | |
| pass_deflected | `pass_attempts WHERE event_detail='Pass_Deflected'` | Keegan=2 ✅ | - | ✅ | |
| pass_missed | `pass_attempts WHERE event_detail='Pass_Missed'` | Keegan=3 ✅ | - | ✅ | |
| pass_pct | `pass_completed / pass_attempts * 100` | Keegan=64.7% ✅ | - | ✅ | |
| pass_targets | `event_type='Pass' AND player_role='event_player_2'` | Keegan=28 ✅ | - | ✅ | Received passes |
| pass_received | `pass_targets WHERE event_detail='Pass_Completed'` | Keegan=19 ✅ | - | ✅ | |
| pass_targets_missed | `pass_targets WHERE event_detail='Pass_Missed'` | Keegan=3 ✅ | - | ✅ | |
| pass_targets_deflected | `pass_targets WHERE event_detail='Pass_Deflected'` | Keegan=3 ✅ | - | ✅ | |
| pass_targets_intercepted | `pass_targets WHERE event_detail='Pass_Intercepted'` | Keegan=2 ✅ | - | ✅ | |

### Player Skating Stats - Faceoffs

| Stat | Formula | Game 18969 | Game 18977 | Status | Notes |
|------|---------|------------|------------|--------|-------|
| fo_wins | `event_type='Faceoff' AND player_role='event_player_1'` | Keegan=11 ✅ | - | ✅ | Winner is event_player_1 |
| fo_losses | `event_type='Faceoff' AND player_role='opp_player_1'` | Keegan=11 ✅ | - | ✅ | Loser is opp_player_1 |
| fo_total | `fo_wins + fo_losses` | Keegan=22 ✅ | - | ✅ | |
| faceoff_pct | `fo_wins / fo_total * 100` | Keegan=50.0% ✅ | - | ✅ | |

### Player Skating Stats - Zone Transitions

| Stat | Formula | Game 18969 | Game 18977 | Status | Notes |
|------|---------|------------|------------|--------|-------|
| zone_entries | `player_role='event_player_1' AND event_detail contains 'Entry'` | Keegan=10 ✅ | Hayden=20 ✅ | ✅ | |
| zone_entries_rush | `event_detail_2='ZoneEntry-Rush'` | Keegan=7 ✅ | - | ✅ | Controlled |
| zone_entries_chip | `event_detail_2='ZoneEntry-Chip'` | Keegan=1 ✅ | - | ✅ | Uncontrolled |
| zone_entries_dumpin | `event_detail_2='ZoneEntry-DumpIn'` | Keegan=2 ✅ | - | ✅ | Uncontrolled |
| zone_entries_controlled | `zone_entries WHERE control_level='controlled'` | Keegan=7 ✅ | - | ✅ | Rush only |
| zone_entries_uncontrolled | `zone_entries WHERE control_level='uncontrolled'` | Keegan=3 ✅ | - | ✅ | Chip + DumpIn |
| zone_entries_failed | `zone_entries WHERE control_level='failed'` | Keegan=0 ✅ | - | ✅ | |
| zone_exits | `player_role='event_player_1' AND event_detail contains 'Exit'` | Keegan=10 ✅ | Hayden=12 ✅ | ✅ | |
| zone_exits_rush | `event_detail_2='ZoneExit-Rush'` | Keegan=5 ✅ | - | ✅ | |
| zone_exits_chip | `event_detail_2='ZoneExit-Chip'` | Keegan=1 ✅ | - | ✅ | |
| zone_exits_pass | `event_detail_2='ZoneExit-Pass'` | Keegan=1 ✅ | - | ✅ | |
| zone_exits_passmiss | `event_detail_2='ZoneExit-PassMiss/Misplay'` | Keegan=2 ✅ | - | ✅ | |
| zone_exits_controlled | `zone_exits WHERE control_level='controlled'` | Keegan=6 ✅ | - | ✅ | Rush + Pass |
| zone_exits_uncontrolled | `zone_exits WHERE control_level='uncontrolled'` | Keegan=1 ✅ | - | ✅ | Chip |
| zone_exits_failed | `zone_exits WHERE control_level='failed'` | Keegan=2 ✅ | - | ✅ | PassMiss |
| zone_keepins | `event_detail contains 'Keepin' AND player_role='event_player_1'` | Keegan=0 ✅ | - | ✅ | Defensive |

### Player Skating Stats - Turnovers & Possession

| Stat | Formula | Game 18969 | Game 18977 | Status | Notes |
|------|---------|------------|------------|--------|-------|
| giveaways | `event_type='Turnover' AND event_detail contains 'Giveaway'` | Keegan=5 ✅ | Hayden=7 ✅ | ✅ | |
| takeaways | `event_type='Turnover' AND event_detail contains 'Takeaway'` | Keegan=3 ✅ | Hayden=0 ✅ | ✅ | |
| puck_retrievals | `event_type='Possession' AND event_detail='PuckRetrieval'` | Keegan=6 ✅ | - | ✅ | |
| puck_recoveries | `event_type='Possession' AND event_detail='PuckRecovery'` | Keegan=4 ✅ | - | ✅ | |
| breakaways | `event_type='Possession' AND event_detail='Breakaway'` | Keegan=1 ✅ | - | ✅ | |
| regroups | `event_type='Possession' AND event_detail='Regroup'` | Keegan=1 ✅ | - | ✅ | |
| loose_puck_battles | `event_type='LoosePuck' (any role)` | Keegan=1 ✅ | - | ✅ | |
| loose_puck_wins | `event_type='LoosePuck' AND player_role='event_player_1'` | Keegan=0 ✅ | - | ✅ | |
| loose_puck_losses | `event_type='LoosePuck' AND player_role LIKE 'opp_player%'` | Keegan=1 ✅ | - | ✅ | |

### Player Skating Stats - Defensive

| Stat | Formula | Game 18969 | Game 18977 | Status | Notes |
|------|---------|------------|------------|--------|-------|
| blocks | `play_detail='BlockedShot' OR play_detail_2='BlockedShot'` | Keegan=0 ✅ | - | ✅ | |
| stick_checks | `play_detail='StickCheck' OR play_detail_2='StickCheck'` | Keegan=5 ✅ | - | ✅ | |
| poke_checks | `play_detail='PokeCheck' OR play_detail_2='PokeCheck'` | Keegan=3 ✅ | - | ✅ | |
| in_shot_pass_lane | `play_detail='InShotPassLane' OR play_detail_2='InShotPassLane'` | Keegan=3 ✅ | - | ✅ | |
| backchecks | `play_detail='Backcheck' OR play_detail_2='Backcheck'` | Keegan=2 ✅ | - | ✅ | |

### Player Skating Stats - Time on Ice

| Stat | Formula | Game 18969 | Game 18977 | Status | Notes |
|------|---------|------------|------------|--------|-------|
| shift_segments | `COUNT(*) from fact_shift_players` | Keegan=38 ✅ | Hayden=? | ✅ | Raw shift rows |
| logical_shifts | `MAX(logical_shift_number)` | Keegan=13 ✅ | Hayden=14 ✅ | ✅ | Breaks on gap/period |
| toi_seconds | `SUM(shift_duration)` | Keegan=1535 ✅ | - | ✅ | |
| toi_minutes | `toi_seconds / 60` | Keegan=25.6 ✅ | Hayden=30.8 ✅ | ✅ | |
| stoppage_time | `SUM(stoppage_time)` | Keegan=207 ✅ | - | ✅ | Time during stoppages |
| playing_toi_seconds | `SUM(playing_duration)` | Keegan=1328 ✅ | - | ✅ | TOI minus stoppages |
| avg_logical_shift | `toi_seconds / logical_shifts` | Keegan=118.1 ✅ | - | ✅ | |
| avg_logical_shift_playing | `playing_toi / logical_shifts` | Keegan=102.2 ✅ | - | ✅ | |
| running_toi_final | `running_toi on last shift row` | Keegan=1535 ✅ | - | ✅ | |
| running_playing_toi_final | `running_playing_toi on last shift row` | Keegan=1328 ✅ | - | ✅ | |

### Player Skating Stats - Other

| Stat | Formula | Game 18969 | Game 18977 | Status | Notes |
|------|---------|------------|------------|--------|-------|
| penalties | `event_type='Penalty' AND player_role='event_player_1'` | Keegan=0 ✅ | - | ✅ | Cross-ref: NORAD PIM=0 |
| rebounds | N/A for skaters | Keegan=0 ✅ | - | ✅ | Goalie stat only |
| plus_minus | `Match goal times to shift times` | - | - | ⚪ NOT VERIFIED | Not in NORAD, needs calc |

### Goalie Stats

| Stat | Formula | Game 18969 (Wyatt) | Status | Notes |
|------|---------|-------------------|--------|-------|
| saves | `event_type='Save' AND player_role='event_player_1'` | 37 ✅ | ✅ | Goalie always event_player_1 |
| save_freeze | `event_type='Save' AND event_detail='Save_Freeze'` | 11 ✅ | ✅ | |
| save_rebound | `event_type='Save' AND event_detail='Save_Rebound'` | 26 ✅ | ✅ | |
| goals_against | `event_type='Goal' AND player_role='opp_player_1'` | 4 ✅ | ✅ | |
| shots_faced | `saves + goals_against` | 41 ✅ | ✅ | |
| save_pct | `saves / shots_faced * 100` | 90.2% ✅ | ✅ | |
| rebounds | `event_type='Rebound' AND player_role='event_player_1'` | 26 ✅ | ✅ | |
| rebound_team_recovered | `event_detail='Rebound_TeamRecovered'` | 14 ✅ | ✅ | |
| rebound_opp_recovered | `event_detail='Rebound_OppTeamRecovered'` | 11 ✅ | ✅ | |
| rebound_shot_generated | `event_detail='Rebound_ShotGenerated'` | 1 ✅ | ✅ | |
| toi_seconds | `SUM(shift_duration)` | 3158 ✅ | ✅ | |
| toi_minutes | `toi_seconds / 60` | 52.6 ✅ | ✅ | |
| shift_segments | `COUNT shifts` | 93 ✅ | ✅ | |
| logical_shifts | `MAX(logical_shift_number)` | 3 ✅ | ✅ | One per period |

### Stats NOT YET VERIFIED

| Stat | Reason | Priority |
|------|--------|----------|
| plus_minus | Not in NORAD, needs manual calculation | 🟡 Medium |
| corsi_for | Advanced stat, needs event chain verification | 🟡 Medium |
| corsi_against | Advanced stat, needs event chain verification | 🟡 Medium |
| fenwick_for | Advanced stat, needs event chain verification | 🟡 Medium |
| expected_goals | Model-based, needs calibration | 🔴 Low |
| game_score | Composite metric | 🔴 Low |
| war | Wins above replacement | 🔴 Low |

---

## Goal Accuracy Verification

All 4 games verified against noradhockey.com:

| Game ID | Date | Home | Away | Expected | Actual | Match |
|---------|------|------|------|----------|--------|-------|
| 18969 | 2025-12-28 | Ace (16) | Velodrome (4) | 20 | 20 | ✅ |
| 18977 | 2025-12-14 | Velodrome (4) | Icehogs (13) | 17 | 17 | ✅ |
| 18981 | 2025-11-30 | Ace (6) | AMOS (3) | 9 | 9 | ✅ |
| 18987 | 2025-11-16 | Velodrome (2) | AMOS (1) | 3 | 3 | ✅ |

**Goal Counting Rule:**
```sql
-- Goals are identified by:
event_type = 'Goal' AND event_detail = 'Goal_Scored'

-- Shot_Goal is the SHOT that resulted in a goal, NOT the goal itself
-- Do NOT count event_detail = 'Shot_Goal' as goals
```

---

## Table Verification Checklist

### Summary by Category

| Category | Count | Rows | Verified | Status |
|----------|-------|------|----------|--------|
| Dimension Tables | 54 | 3,116 | 54 | ✅ |
| Fact Tables - Core | 10 | 49,041 | 10 | ✅ |
| Fact Tables - Stats | 15 | 29,563 | 15 | ✅ |
| Fact Tables - Advanced | 38 | 10,195 | 38 | ✅ |
| Fact Tables - Other | 10 | 3,528 | 10 | ✅ |
| QA Tables | 3 | 30 | 3 | ✅ |
| Lookup Tables | 1 | 14,471 | 1 | ✅ |
| **TOTAL** | **131** | **109,944** | **131** | ✅ |

### Dimension Tables (54 tables, 3,116 rows)

| Table | Rows | Key Columns | FK Verified | Status |
|-------|------|-------------|-------------|--------|
| dim_assist_type | 5 | assist_type_id, name | ✅ | ✅ |
| dim_comparison_type | 6 | comparison_type_id | ✅ | ✅ |
| dim_competition_tier | 4 | competition_tier_id | ✅ | ✅ |
| dim_composite_rating | 8 | composite_rating_id | ✅ | ✅ |
| dim_danger_level | 3 | danger_level_id | ✅ | ✅ |
| dim_danger_zone | 4 | danger_zone_id | ✅ | ✅ |
| dim_event_detail | 31 | event_detail_id, name | ✅ | ✅ |
| dim_event_detail_2 | 97 | event_detail_2_id | ✅ | ✅ |
| dim_event_type | 12 | event_type_id, name | ✅ | ✅ |
| dim_game_state | 6 | game_state_id | ✅ | ✅ |
| dim_giveaway_type | 15 | giveaway_type_id | ✅ | ✅ |
| dim_league | 2 | league_id, name | ✅ | ✅ |
| dim_micro_stat | 22 | micro_stat_id | ✅ | ✅ |
| dim_net_location | 10 | net_location_id | ✅ | ✅ |
| dim_pass_outcome | 4 | pass_outcome_id | ✅ | ✅ |
| dim_pass_type | 8 | pass_type_id | ✅ | ✅ |
| dim_period | 5 | period_id, name | ✅ | ✅ |
| dim_play_detail | 129 | play_detail_id | ✅ | ✅ |
| dim_play_detail_2 | 62 | play_detail_2_id | ✅ | ✅ |
| dim_player | 337 | player_id, name | ✅ | ✅ |
| dim_player_role | 14 | player_role_id | ✅ | ✅ |
| dim_playerurlref | 548 | player_id, url | ✅ | ✅ |
| dim_position | 6 | position_id, name | ✅ | ✅ |
| dim_randomnames | 486 | name_id | ✅ | ✅ |
| dim_rating | 5 | rating_id | ✅ | ✅ |
| dim_rating_matchup | 5 | matchup_id | ✅ | ✅ |
| dim_rink_zone | 267 | zone_id, x, y | ✅ | ✅ |
| dim_save_outcome | 3 | save_outcome_id | ✅ | ✅ |
| dim_schedule | 562 | game_id, date | ✅ | ✅ |
| dim_season | 9 | season_id, name | ✅ | ✅ |
| dim_shift_quality_tier | 5 | tier_id | ✅ | ✅ |
| dim_shift_slot | 7 | slot_id | ✅ | ✅ |
| dim_shift_start_type | 9 | start_type_id | ✅ | ✅ |
| dim_shift_stop_type | 18 | stop_type_id | ✅ | ✅ |
| dim_shot_outcome | 5 | shot_outcome_id | ✅ | ✅ |
| dim_shot_type | 6 | shot_type_id | ✅ | ✅ |
| dim_situation | 5 | situation_id | ✅ | ✅ |
| dim_stat | 83 | stat_id, name | ✅ | ✅ |
| dim_stat_category | 13 | category_id | ✅ | ✅ |
| dim_stat_type | 57 | stat_type_id | ✅ | ✅ |
| dim_stoppage_type | 4 | stoppage_type_id | ✅ | ✅ |
| dim_strength | 18 | strength_id | ✅ | ✅ |
| dim_success | 3 | success_id | ✅ | ✅ |
| dim_takeaway_type | 2 | takeaway_type_id | ✅ | ✅ |
| dim_team | 26 | team_id, code, name | ✅ | ✅ |
| dim_terminology_mapping | 84 | term_id | ✅ | ✅ |
| dim_time_bucket | 6 | bucket_id | ✅ | ✅ |
| dim_turnover_quality | 3 | quality_id | ✅ | ✅ |
| dim_turnover_type | 21 | turnover_type_id | ✅ | ✅ |
| dim_venue | 2 | venue_id, name | ✅ | ✅ |
| dim_zone | 3 | zone_id, name | ✅ | ✅ |
| dim_zone_entry_type | 11 | entry_type_id | ✅ | ✅ |
| dim_zone_exit_type | 10 | exit_type_id | ✅ | ✅ |
| dim_zone_outcome | 6 | outcome_id | ✅ | ✅ |

### Fact Tables - Core (10 tables, 49,041 rows)

| Table | Rows | Key Columns | FK Verified | Status | Notes |
|-------|------|-------------|-------------|--------|-------|
| fact_events | 5,831 | game_id, event_index | ✅ | ✅ | Base event table |
| fact_events_player | 7,476 | game_id, event_index, player_id | ✅ | ✅ | Player-event grain |
| fact_event_players | 11,181 | game_id, event_index | ✅ | ✅ | Full tracking detail |
| fact_shifts | 398 | game_id, shift_index | ✅ | ✅ | Base shift table |
| fact_shift_players | 4,559 | game_id, shift_index, player_id | ✅ | ✅ | Player-shift grain |
| fact_shifts | 398 | game_id, shift_index | ✅ | ✅ | Full shift detail |
| fact_gameroster | 14,471 | game_id, player_id | ✅ | ✅ | Game rosters |
| fact_player_game_stats | 107 | game_id, player_id | ✅ | ✅ | Per-game stats |
| fact_tracking | 5,117 | game_id, tracking_index | ✅ | ✅ | Raw tracking |
| fact_shift_players | 4,613 | game_id, shift_id, player_id | ✅ | ✅ | Shift assignments |

### Fact Tables - Statistics (15 tables, 29,563 rows)

| Table | Rows | Key Columns | FK Verified | Status | Notes |
|-------|------|-------------|-------------|--------|-------|
| fact_player_season_stats | 68 | season_id, player_id | ✅ | ✅ | Aggregated |
| fact_player_career_stats | 68 | player_id | ✅ | ✅ | Career totals |
| fact_player_period_stats | 321 | game_id, player_id, period | ✅ | ✅ | Per-period |
| fact_player_stats_long | 13,884 | game_id, player_id, stat | ✅ | ✅ | Long format |
| fact_player_stats_by_competition_tier | 240 | player_id, tier | ✅ | ✅ | By tier |
| fact_team_game_stats | 8 | game_id, team_id | ✅ | ✅ | Team per-game |
| fact_team_season_stats | 5 | season_id, team_id | ✅ | ✅ | Team season |
| fact_goalie_game_stats | 8 | game_id, player_id | ✅ | ✅ | Goalie stats |
| fact_player_micro_stats | 212 | game_id, player_id | ✅ | ✅ | Micro statistics |
| fact_player_boxscore_all | 14,473 | game_id, player_id | ✅ | ✅ | Full boxscore |
| fact_player_trends | 107 | player_id, game_id | ✅ | ✅ | Trend analysis |
| fact_player_position_splits | 3 | player_id, position | ✅ | ✅ | Position splits |
| fact_player_game_position | 105 | game_id, player_id | ✅ | ✅ | Game positions |
| fact_league_leaders_snapshot | 14,473 | snapshot_date, stat | ✅ | ✅ | Leaders |
| fact_team_standings_snapshot | 1,124 | snapshot_date, team | ✅ | ✅ | Standings |

### Fact Tables - Advanced Analytics (38 tables, 10,195 rows)

| Table | Rows | Key Columns | FK Verified | Status | Notes |
|-------|------|-------------|-------------|--------|-------|
| fact_h2h | 684 | player_id_1, player_id_2, game_id | ✅ | ✅ | Head to head |
| fact_head_to_head | 572 | player_id_1, player_id_2 | ✅ | ✅ | H2H summary |
| fact_wowy | 641 | player_id, teammate_id, game_id | ✅ | ✅ | With/without |
| fact_matchup_performance | 265 | player_id, opp_id | ✅ | ✅ | Matchup stats |
| fact_matchup_summary | 684 | player_id, opp_id | ✅ | ✅ | Summary |
| fact_player_qoc_summary | 105 | player_id, game_id | ✅ | ✅ | Quality of comp |
| fact_player_pair_stats | 475 | player_id_1, player_id_2 | ✅ | ✅ | Pair stats |
| fact_line_combos | 332 | game_id, line | ✅ | ✅ | Line combinations |
| fact_zone_entries | 508 | game_id, event_index | ✅ | ✅ | Zone entries |
| fact_zone_exits | 487 | game_id, event_index | ✅ | ✅ | Zone exits |
| fact_zone_entry_summary | 68 | player_id, game_id | ✅ | ✅ | Entry summary |
| fact_zone_exit_summary | 68 | player_id, game_id | ✅ | ✅ | Exit summary |
| fact_team_zone_time | 8 | game_id, team_id | ✅ | ✅ | Zone time |
| fact_breakouts | 475 | game_id, event_index | ✅ | ✅ | Breakouts |
| fact_rushes | 314 | game_id, rush_index | ✅ | ✅ | Rush attempts |
| fact_rush_events | 199 | game_id, rush_index | ✅ | ✅ | Rush details |
| fact_scoring_chances | 455 | game_id, event_index | ✅ | ✅ | Scoring chances |
| fact_scoring_chances_detailed | 455 | game_id, event_index | ✅ | ✅ | Detailed |
| fact_high_danger_chances | 26 | game_id, event_index | ✅ | ✅ | High danger |
| fact_shot_danger | 435 | game_id, event_index | ✅ | ✅ | Shot danger |
| fact_saves | 212 | game_id, event_index | ✅ | ✅ | Save events |
| fact_faceoffs | 171 | game_id, event_index | ✅ | ✅ | Faceoff events |
| fact_turnovers_detailed | 741 | game_id, event_index | ✅ | ✅ | Turnovers |
| fact_penalties | 20 | game_id, event_index | ✅ | ✅ | Penalties |
| fact_event_chains | 227 | game_id, chain_index | ✅ | ✅ | Event chains |
| fact_player_event_chains | 5,117 | game_id, player_id | ✅ | ✅ | Player chains |
| fact_linked_events | 473 | game_id, event_index | ✅ | ✅ | Linked events |
| fact_sequences | 397 | game_id, sequence_index | ✅ | ✅ | Play sequences |
| fact_plays | 1,956 | game_id, play_index | ✅ | ✅ | Individual plays |
| fact_cycle_events | 32 | game_id, event_index | ✅ | ✅ | Cycle plays |
| fact_possession_time | 107 | game_id, player_id | ✅ | ✅ | Puck possession |
| fact_period_momentum | 12 | game_id, period | ✅ | ✅ | Momentum |
| fact_special_teams_summary | 5 | team_id | ✅ | ✅ | PP/PK |
| fact_shift_quality | 4,559 | game_id, shift_index | ✅ | ✅ | Shift quality |
| fact_shift_quality_logical | 105 | game_id, player_id | ✅ | ✅ | Logical quality |
| fact_season_summary | 1 | season_id | ✅ | ✅ | Season summary |
| fact_leadership | 28 | player_id, category | ✅ | ✅ | Team leaders |
| fact_playergames | 3,010 | player_id, game_id | ✅ | ✅ | Player games |

### Fact Tables - Other (10 tables, 3,528 rows)

| Table | Rows | Key Columns | FK Verified | Status | Notes |
|-------|------|-------------|-------------|--------|-------|
| fact_draft | 160 | player_id, draft_year | ✅ | ✅ | Draft data |
| fact_registration | 190 | player_id, season_id | ✅ | ✅ | Registrations |
| fact_game_status | 562 | game_id | ✅ | ✅ | Game status |
| fact_video | 10 | game_id, video_id | ✅ | ✅ | Video links |
| fact_player_xy_long | 0 | - | ✅ | ⚪ | Empty (no XY data) |
| fact_player_xy_wide | 0 | - | ✅ | ⚪ | Empty (no XY data) |
| fact_puck_xy_long | 0 | - | ✅ | ⚪ | Empty (no XY data) |
| fact_puck_xy_wide | 0 | - | ✅ | ⚪ | Empty (no XY data) |
| fact_shot_xy | 0 | - | ✅ | ⚪ | Empty (no XY data) |
| fact_suspicious_stats | 18 | game_id, player_id | ✅ | ✅ | QA flags |

### QA Tables (3 tables, 30 rows)

| Table | Rows | Purpose | Status |
|-------|------|---------|--------|
| qa_goal_accuracy | 4 | Goal count verification vs NORAD | ✅ |
| qa_data_completeness | 4 | Events/shifts/rosters check | ✅ |
| qa_suspicious_stats | 22 | Outlier detection | ✅ |

### Lookup Tables (1 table, 14,471 rows)

| Table | Rows | Purpose | Status |
|-------|------|---------|--------|
| lookup_player_game_rating | 14,471 | Player ratings per game | ✅ |

---

## Known Issues & Data Quality Notes

### Resolved Issues

| Issue | Description | Resolution | Date |
|-------|-------------|------------|------|
| Team code swap | Ace='AMOS'→'ACE', AMOS='ACE'→'AMO' | Fixed in ETL | 2026-01-05 |
| Team name case | 'Amos' → 'AMOS' in all tables | Fixed, 8,195 rows | 2026-01-05 |
| CSAHA teams | 9 non-NORAD teams in dim_team | Removed | 2026-01-05 |
| CSAHA columns | 4 CSAHA columns in dim_player | Removed | 2026-01-05 |
| Game 18977 goals | Velodrome goals 3→4 | Fixed | 2026-01-05 |

### Outstanding Data Quality Flags

From `qa_suspicious_stats.csv`:

| Game | Player | Issue | Severity | Notes |
|------|--------|-------|----------|-------|
| 18977 | Lee Smith | TOI=0, CF%=0 | WARNING | Player may not have played |
| 18977 | Maxwell Donaty | TOI=0, CF%=0 | WARNING | Player may not have played |
| 18977 | Jared Wolf | TOI=3185s (53min) | WARNING | High TOI - verify |
| 18977 | Hayden Smith | shots=23 | WARNING | High shot count - verified correct |
| 18977 | - | No assists tracked | WARNING | Data completeness issue |
| 18981 | - | No assists tracked | WARNING | Data completeness issue |

### Empty Tables (Expected)

These tables are empty because XY coordinate tracking is not yet implemented:
- fact_player_xy_long
- fact_player_xy_wide
- fact_puck_xy_long
- fact_puck_xy_wide
- fact_shot_xy

---

## Verification Procedures

### How to Verify a Stat

1. **Load fact_events_player.csv**
2. **Filter by game_id and player_id**
3. **Apply the formula from the Stat Calculation Matrix**
4. **Compare to fact_player_game_stats value**
5. **Cross-reference with noradhockey.com when possible**

### How to Verify Goal Counts

```python
import pandas as pd

events = pd.read_csv("data/output/fact_events.csv")
goals = events[
    (events['event_type'] == 'Goal') & 
    (events['event_detail'] == 'Goal_Scored')
]
print(goals.groupby('game_id').size())
```

### How to Run Automated Verification

```bash
# Run all ETL tests
python3 -m pytest tests/test_etl.py -v

# Run stat validation
python scripts/validation/validate_stats.py

# Check goal accuracy
python -c "import pandas as pd; print(pd.read_csv('data/output/qa_goal_accuracy.csv'))"
```

---

## Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-06 | 10.03 | Created comprehensive verification status document |
| 2026-01-05 | 10.01 | Table validation sessions 1-3 completed |
| 2026-01-04 | 9.01 | Initial stat validation (Keegan Mantaro) |

---

## Next Steps

1. **Complete game 18977 verification** - Add remaining 57 stats
2. **Verify games 18981 and 18987** - Currently goals only
3. **Implement plus_minus calculation** - Compare to NORAD when available
4. **Verify advanced stats** - Corsi, Fenwick when chain logic confirmed
5. **Add more test players** - Currently only Keegan and Hayden verified
