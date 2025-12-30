# BenchSight Data Dictionary

**Generated:** 2025-12-30 14:19

**Total Tables:** 96 (44 dimensions, 51 facts, 1 QA)

---

## Quick Reference

| Category | Tables | Description |
|----------|--------|-------------|
| dim_* | 44 | Dimension/lookup tables |
| fact_* | 51 | Fact/transactional tables |
| qa_* | 1 | Quality assurance tables |

## Table of Contents

### Dimensions
- [dim_comparison_type](#dim-comparison-type)
- [dim_composite_rating](#dim-composite-rating)
- [dim_danger_zone](#dim-danger-zone)
- [dim_event_detail](#dim-event-detail)
- [dim_event_detail_2](#dim-event-detail-2)
- [dim_event_type](#dim-event-type)
- [dim_giveaway_type](#dim-giveaway-type)
- [dim_league](#dim-league)
- [dim_micro_stat](#dim-micro-stat)
- [dim_net_location](#dim-net-location)
- [dim_pass_type](#dim-pass-type)
- [dim_period](#dim-period)
- [dim_play_detail](#dim-play-detail)
- [dim_play_detail_2](#dim-play-detail-2)
- [dim_player](#dim-player)
- [dim_player_role](#dim-player-role)
- [dim_playerurlref](#dim-playerurlref)
- [dim_position](#dim-position)
- [dim_randomnames](#dim-randomnames)
- [dim_rink_coord](#dim-rink-coord)
- [dim_rinkboxcoord](#dim-rinkboxcoord)
- [dim_rinkcoordzones](#dim-rinkcoordzones)
- [dim_schedule](#dim-schedule)
- [dim_season](#dim-season)
- [dim_shift_slot](#dim-shift-slot)
- [dim_shift_start_type](#dim-shift-start-type)
- [dim_shift_stop_type](#dim-shift-stop-type)
- [dim_shot_type](#dim-shot-type)
- [dim_situation](#dim-situation)
- [dim_stat](#dim-stat)
- [dim_stat_category](#dim-stat-category)
- [dim_stat_type](#dim-stat-type)
- [dim_stoppage_type](#dim-stoppage-type)
- [dim_strength](#dim-strength)
- [dim_success](#dim-success)
- [dim_takeaway_type](#dim-takeaway-type)
- [dim_team](#dim-team)
- [dim_terminology_mapping](#dim-terminology-mapping)
- [dim_turnover_quality](#dim-turnover-quality)
- [dim_turnover_type](#dim-turnover-type)
- [dim_venue](#dim-venue)
- [dim_zone](#dim-zone)
- [dim_zone_entry_type](#dim-zone-entry-type)
- [dim_zone_exit_type](#dim-zone-exit-type)

### Facts
- [fact_cycle_events](#fact-cycle-events)
- [fact_draft](#fact-draft)
- [fact_event_chains](#fact-event-chains)
- [fact_events](#fact-events)
- [fact_events_long](#fact-events-long)
- [fact_events_player](#fact-events-player)
- [fact_events_tracking](#fact-events-tracking)
- [fact_game_status](#fact-game-status)
- [fact_gameroster](#fact-gameroster)
- [fact_goalie_game_stats](#fact-goalie-game-stats)
- [fact_h2h](#fact-h2h)
- [fact_head_to_head](#fact-head-to-head)
- [fact_leadership](#fact-leadership)
- [fact_league_leaders_snapshot](#fact-league-leaders-snapshot)
- [fact_line_combos](#fact-line-combos)
- [fact_linked_events](#fact-linked-events)
- [fact_matchup_summary](#fact-matchup-summary)
- [fact_player_boxscore_all](#fact-player-boxscore-all)
- [fact_player_event_chains](#fact-player-event-chains)
- [fact_player_game_position](#fact-player-game-position)
- [fact_player_game_stats](#fact-player-game-stats)
- [fact_player_micro_stats](#fact-player-micro-stats)
- [fact_player_pair_stats](#fact-player-pair-stats)
- [fact_player_period_stats](#fact-player-period-stats)
- [fact_player_stats_long](#fact-player-stats-long)
- [fact_player_xy_long](#fact-player-xy-long)
- [fact_player_xy_wide](#fact-player-xy-wide)
- [fact_playergames](#fact-playergames)
- [fact_plays](#fact-plays)
- [fact_possession_time](#fact-possession-time)
- [fact_puck_xy_long](#fact-puck-xy-long)
- [fact_puck_xy_wide](#fact-puck-xy-wide)
- [fact_registration](#fact-registration)
- [fact_rush_events](#fact-rush-events)
- [fact_scoring_chances](#fact-scoring-chances)
- [fact_sequences](#fact-sequences)
- [fact_shift_players](#fact-shift-players)
- [fact_shift_quality](#fact-shift-quality)
- [fact_shift_quality_logical](#fact-shift-quality-logical)
- [fact_shifts](#fact-shifts)
- [fact_shifts_long](#fact-shifts-long)
- [fact_shifts_player](#fact-shifts-player)
- [fact_shifts_tracking](#fact-shifts-tracking)
- [fact_shot_danger](#fact-shot-danger)
- [fact_shot_xy](#fact-shot-xy)
- [fact_suspicious_stats](#fact-suspicious-stats)
- [fact_team_game_stats](#fact-team-game-stats)
- [fact_team_standings_snapshot](#fact-team-standings-snapshot)
- [fact_team_zone_time](#fact-team-zone-time)
- [fact_video](#fact-video)
- [fact_wowy](#fact-wowy)

### QA
- [qa_suspicious_stats](#qa-suspicious-stats)

---

## Dimension Tables

### dim_comparison_type
**Rows:** 6 | **Columns:** 5

| Column | Type | Notes |
|--------|------|-------|
| comparison_type_id | TEXT | Foreign key reference |
| comparison_type_code | TEXT |  |
| comparison_type_name | TEXT |  |
| description | TEXT |  |
| analysis_scope | TEXT |  |

### dim_composite_rating
**Rows:** 8 | **Columns:** 6

| Column | Type | Notes |
|--------|------|-------|
| rating_id | TEXT | Foreign key reference |
| rating_code | NUMERIC |  |
| rating_name | NUMERIC |  |
| description | TEXT |  |
| scale_min | TEXT |  |
| scale_max | TEXT |  |

### dim_danger_zone
**Rows:** 4 | **Columns:** 5

| Column | Type | Notes |
|--------|------|-------|
| danger_zone_id | TEXT | Foreign key reference |
| danger_zone_code | TEXT |  |
| danger_zone_name | TEXT |  |
| xg_base | TEXT |  |
| description | TEXT |  |

### dim_event_detail
**Rows:** 59 | **Columns:** 3

| Column | Type | Notes |
|--------|------|-------|
| event_detail_id | TEXT | Foreign key reference |
| event_detail_code | TEXT |  |
| event_detail_name | TEXT |  |

### dim_event_detail_2
**Rows:** 97 | **Columns:** 6

| Column | Type | Notes |
|--------|------|-------|
| event_detail_2_id | TEXT | Foreign key reference |
| event_detail_2_code | TEXT |  |
| event_detail_2_name | TEXT |  |
| is_secondary_action | BOOLEAN |  |
| context_type | TEXT |  |
| description | TEXT |  |

### dim_event_type
_Types of tracked events (Shot, Pass, etc.)_

**Rows:** 20 | **Columns:** 3

| Column | Type | Notes |
|--------|------|-------|
| event_type_id | TEXT | Foreign key reference |
| event_type_code | TEXT |  |
| event_type_name | TEXT |  |

### dim_giveaway_type
**Rows:** 12 | **Columns:** 8

| Column | Type | Notes |
|--------|------|-------|
| giveaway_type_id | TEXT | Foreign key reference |
| giveaway_type_code | TEXT |  |
| giveaway_type_name | TEXT |  |
| danger_level | TEXT |  |
| xga_impact | TEXT |  |
| turnover_quality | TEXT |  |
| zone_context | TEXT |  |
| description | TEXT |  |

### dim_league
**Rows:** 2 | **Columns:** 2

| Column | Type | Notes |
|--------|------|-------|
| league_id | TEXT | Foreign key reference |
| league | TEXT |  |

### dim_micro_stat
**Rows:** 22 | **Columns:** 4

| Column | Type | Notes |
|--------|------|-------|
| micro_stat_id | TEXT | Foreign key reference |
| stat_code | TEXT |  |
| stat_name | TEXT |  |
| category | TEXT |  |

### dim_net_location
**Rows:** 10 | **Columns:** 5

| Column | Type | Notes |
|--------|------|-------|
| net_location_id | TEXT | Foreign key reference |
| net_location_code | TEXT |  |
| net_location_name | TEXT |  |
| x_pct | NUMERIC |  |
| y_pct | NUMERIC |  |

### dim_pass_type
**Rows:** 16 | **Columns:** 8

| Column | Type | Notes |
|--------|------|-------|
| pass_type_id | TEXT | Foreign key reference |
| pass_type_code | TEXT |  |
| pass_type_name | TEXT |  |
| expected_completion_rate | TEXT |  |
| danger_value | TEXT |  |
| xa_modifier | TEXT |  |
| description | TEXT |  |
| skill_required | TEXT |  |

### dim_period
_Game periods (1, 2, 3, OT)_

**Rows:** 5 | **Columns:** 7

| Column | Type | Notes |
|--------|------|-------|
| period_id | TEXT | Foreign key reference |
| period_number | INTEGER |  |
| period_name | TEXT |  |
| period_type | TEXT |  |
| duration_seconds | INTEGER |  |
| intensity_multiplier | TEXT |  |
| description | TEXT |  |

### dim_play_detail
**Rows:** 154 | **Columns:** 6

| Column | Type | Notes |
|--------|------|-------|
| play_detail_id | TEXT | Foreign key reference |
| play_detail_code | TEXT |  |
| play_detail_name | TEXT |  |
| play_category | TEXT |  |
| skill_level | TEXT |  |
| description | TEXT |  |

### dim_play_detail_2
**Rows:** 62 | **Columns:** 5

| Column | Type | Notes |
|--------|------|-------|
| play_detail_2_id | TEXT | Foreign key reference |
| play_detail_2_code | TEXT |  |
| play_detail_2_name | TEXT |  |
| is_secondary_play | BOOLEAN |  |
| description | TEXT |  |

### dim_player
_All players in the league with biographical info_

**Rows:** 337 | **Columns:** 28

| Column | Type | Notes |
|--------|------|-------|
| index | INTEGER |  |
| player_first_name | TEXT |  |
| player_last_name | TEXT |  |
| player_full_name | TEXT |  |
| player_id | TEXT | Foreign key reference |
| player_primary_position | TEXT |  |
| current_skill_rating | NUMERIC |  |
| player_hand | TEXT |  |
| birth_year | TEXT |  |
| player_gender | TEXT |  |
| highest_beer_league | TEXT |  |
| player_rating_ly | NUMERIC |  |
| player_notes | TEXT |  |
| player_leadership | TEXT |  |
| player_norad | TEXT |  |
| player_csaha | TEXT |  |
| player_norad_primary_number | INTEGER |  |
| player_csah_primary_number | INTEGER |  |
| player_norad_current_team | TEXT |  |
| player_csah_current_team | TEXT |  |
| player_norad_current_team_id | TEXT | Foreign key reference |
| player_csah_current_team_id | TEXT | Foreign key reference |
| other_url | TEXT |  |
| player_url | TEXT |  |
| player_image | TEXT |  |
| random_player_first_name | TEXT |  |
| random_player_last_name | TEXT |  |
| random_player_full_name | TEXT |  |

### dim_player_role
**Rows:** 14 | **Columns:** 6

| Column | Type | Notes |
|--------|------|-------|
| role_id | TEXT | Foreign key reference |
| role_code | TEXT |  |
| role_name | TEXT |  |
| role_type | TEXT |  |
| sort_order | TEXT |  |
| potential_values | TEXT |  |

### dim_playerurlref
**Rows:** 548 | **Columns:** 3

| Column | Type | Notes |
|--------|------|-------|
| n_player_url | TEXT |  |
| player_full_name | TEXT |  |
| n_player_id_2 | TEXT |  |

### dim_position
_Player positions (Forward, Defense, Goalie)_

**Rows:** 7 | **Columns:** 4

| Column | Type | Notes |
|--------|------|-------|
| position_id | TEXT | Foreign key reference |
| position_code | TEXT |  |
| position_name | TEXT |  |
| position_type | TEXT |  |

### dim_randomnames
**Rows:** 486 | **Columns:** 5

| Column | Type | Notes |
|--------|------|-------|
| random_full_name | TEXT |  |
| random_first_name | TEXT |  |
| random_last_name | TEXT |  |
| gender | TEXT |  |
| name_used | TEXT |  |

### dim_rink_coord
**Rows:** 19 | **Columns:** 7

| Column | Type | Notes |
|--------|------|-------|
| rink_coord_id | TEXT | Foreign key reference |
| rink_coord_code | TEXT |  |
| rink_coord_name | TEXT |  |
| x_min | TEXT |  |
| x_max | TEXT |  |
| y_min | TEXT |  |
| y_max | TEXT |  |

### dim_rinkboxcoord
**Rows:** 50 | **Columns:** 12

| Column | Type | Notes |
|--------|------|-------|
| box_id | TEXT | Foreign key reference |
| box_id_rev | TEXT |  |
| x_min | TEXT |  |
| x_max | TEXT |  |
| y_min | TEXT |  |
| y_max | TEXT |  |
| area | TEXT |  |
| x_description | TEXT |  |
| y_description | TEXT |  |
| danger | TEXT |  |
| zone | TEXT |  |
| side | TEXT |  |

### dim_rinkcoordzones
**Rows:** 198 | **Columns:** 14

| Column | Type | Notes |
|--------|------|-------|
| box_id | TEXT | Foreign key reference |
| box_id_rev | TEXT |  |
| x_min | TEXT |  |
| x_max | TEXT |  |
| y_min | TEXT |  |
| y_max | TEXT |  |
| y_description | TEXT |  |
| x_description | TEXT |  |
| danger | TEXT |  |
| slot | TEXT |  |
| zone | TEXT |  |
| side | TEXT |  |
| dotside | TEXT |  |
| depth | TEXT |  |

### dim_schedule
_Game schedule with dates, teams, scores_

**Rows:** 562 | **Columns:** 44

| Column | Type | Notes |
|--------|------|-------|
| game_id | TEXT | Foreign key reference |
| season | TEXT |  |
| season_id | TEXT | Foreign key reference |
| game_url | TEXT |  |
| home_team_game_id | TEXT | Foreign key reference |
| away_team_game_id | TEXT | Foreign key reference |
| date | TIMESTAMP |  |
| game_time | TEXT |  |
| home_team_name | TEXT |  |
| away_team_name | TEXT |  |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |
| head_to_head_id | TEXT | Foreign key reference |
| game_type | TEXT |  |
| playoff_round | TEXT |  |
| last_period_type | TEXT |  |
| period_length | TEXT |  |
| ot_period_length | TEXT |  |
| shootout_rounds | TEXT |  |
| home_total_goals | INTEGER |  |
| away_total_goals | INTEGER |  |
| home_team_period1_goals | INTEGER |  |
| home_team_period2_goals | INTEGER |  |
| home_team_period3_goals | INTEGER |  |
| home_team_periodOT_goals | INTEGER |  |
| away_team_period1_goals | INTEGER |  |
| away_team_period2_goals | INTEGER |  |
| away_team_period3_goals | INTEGER |  |
| away_team_periodOT_goals | INTEGER |  |
| home_team_seeding | TEXT |  |
| away_team_seeding | TEXT |  |
| home_team_w | TEXT |  |
| home_team_l | TEXT |  |
| home_team_t | TEXT |  |
| home_team_pts | TEXT |  |
| away_team_w | TEXT |  |
| away_team_l | TEXT |  |
| away_team_t | TEXT |  |
| away_team_pts | TEXT |  |
| video_id | TEXT | Foreign key reference |
| video_start_time | TEXT |  |
| video_end_time | TEXT |  |
| video_title | TEXT |  |
| video_url | TEXT |  |

### dim_season
_Season definitions_

**Rows:** 9 | **Columns:** 9

| Column | Type | Notes |
|--------|------|-------|
| index | INTEGER |  |
| season_id | TEXT | Foreign key reference |
| season | TEXT |  |
| session | TEXT |  |
| norad | TEXT |  |
| csah | TEXT |  |
| league_id | TEXT | Foreign key reference |
| league | TEXT |  |
| start_date | TIMESTAMP |  |

### dim_shift_slot
**Rows:** 7 | **Columns:** 3

| Column | Type | Notes |
|--------|------|-------|
| slot_id | TEXT | Foreign key reference |
| slot_code | TEXT |  |
| slot_name | TEXT |  |

### dim_shift_start_type
**Rows:** 9 | **Columns:** 7

| Column | Type | Notes |
|--------|------|-------|
| shift_start_type_id | TEXT | Foreign key reference |
| shift_start_type_code | TEXT |  |
| shift_start_type_name | TEXT |  |
| start_category | TEXT |  |
| description | TEXT |  |
| energy_factor | TEXT |  |
| old_equiv | TEXT |  |

### dim_shift_stop_type
**Rows:** 28 | **Columns:** 9

| Column | Type | Notes |
|--------|------|-------|
| shift_stop_type_id | TEXT | Foreign key reference |
| shift_stop_type_code | TEXT |  |
| shift_stop_type_name | TEXT |  |
| stop_category | TEXT |  |
| description | TEXT |  |
| shift_value_modifier | TEXT |  |
| old_equiv | TEXT |  |
| table | TEXT |  |
| type | TEXT |  |

### dim_shot_type
**Rows:** 14 | **Columns:** 10

| Column | Type | Notes |
|--------|------|-------|
| shot_type_id | TEXT | Foreign key reference |
| shot_type_code | TEXT |  |
| shot_type_name | TEXT |  |
| is_goal | BOOLEAN |  |
| xg_modifier | TEXT |  |
| accuracy_rating | NUMERIC |  |
| power_rating | NUMERIC |  |
| deception_rating | NUMERIC |  |
| typical_distance | TEXT |  |
| description | TEXT |  |

### dim_situation
**Rows:** 5 | **Columns:** 3

| Column | Type | Notes |
|--------|------|-------|
| situation_id | TEXT | Foreign key reference |
| situation_code | TEXT |  |
| situation_name | TEXT |  |

### dim_stat
**Rows:** 83 | **Columns:** 12

| Column | Type | Notes |
|--------|------|-------|
| stat_id | TEXT | Foreign key reference |
| stat_code | TEXT |  |
| stat_name | TEXT |  |
| category | TEXT |  |
| description | TEXT |  |
| formula | TEXT |  |
| player_role | TEXT |  |
| computable_now | TEXT |  |
| benchmark_elite | TEXT |  |
| nhl_avg_per_game | NUMERIC |  |
| nhl_elite_threshold | TEXT |  |
| nhl_min_threshold | TEXT |  |

### dim_stat_category
**Rows:** 13 | **Columns:** 4

| Column | Type | Notes |
|--------|------|-------|
| stat_category_id | TEXT | Foreign key reference |
| category_code | TEXT |  |
| category_name | TEXT |  |
| description | TEXT |  |

### dim_stat_type
**Rows:** 57 | **Columns:** 6

| Column | Type | Notes |
|--------|------|-------|
| stat_id | TEXT | Foreign key reference |
| stat_name | TEXT |  |
| stat_category | TEXT |  |
| stat_level | TEXT |  |
| computable_now | TEXT |  |
| description | TEXT |  |

### dim_stoppage_type
**Rows:** 10 | **Columns:** 5

| Column | Type | Notes |
|--------|------|-------|
| stoppage_type_id | TEXT | Foreign key reference |
| stoppage_type_code | TEXT |  |
| stoppage_type_name | TEXT |  |
| stoppage_category | TEXT |  |
| description | TEXT |  |

### dim_strength
**Rows:** 18 | **Columns:** 7

| Column | Type | Notes |
|--------|------|-------|
| strength_id | TEXT | Foreign key reference |
| strength_code | TEXT |  |
| strength_name | TEXT |  |
| situation_type | TEXT |  |
| xg_multiplier | TEXT |  |
| description | TEXT |  |
| avg_toi_pct | NUMERIC |  |

### dim_success
**Rows:** 2 | **Columns:** 4

| Column | Type | Notes |
|--------|------|-------|
| success_id | TEXT | Foreign key reference |
| success_code | TEXT |  |
| success_name | TEXT |  |
| potential_values | TEXT |  |

### dim_takeaway_type
**Rows:** 10 | **Columns:** 8

| Column | Type | Notes |
|--------|------|-------|
| takeaway_type_id | TEXT | Foreign key reference |
| takeaway_type_code | TEXT |  |
| takeaway_type_name | TEXT |  |
| skill_level | TEXT |  |
| xgf_impact | TEXT |  |
| value_weight | TEXT |  |
| transition_potential | TEXT |  |
| description | TEXT |  |

### dim_team
_All teams with team details_

**Rows:** 26 | **Columns:** 15

| Column | Type | Notes |
|--------|------|-------|
| index | INTEGER |  |
| team_name | TEXT |  |
| team_id | TEXT | Foreign key reference |
| norad_team | TEXT |  |
| csah_team | TEXT |  |
| league_id | TEXT | Foreign key reference |
| league | TEXT |  |
| long_team_name | TEXT |  |
| team_cd | TEXT |  |
| team_color1 | TEXT |  |
| team_color2 | TEXT |  |
| team_color3 | TEXT |  |
| team_color4 | TEXT |  |
| team_logo | TEXT |  |
| team_url | TEXT |  |

### dim_terminology_mapping
**Rows:** 84 | **Columns:** 4

| Column | Type | Notes |
|--------|------|-------|
| dimension | TEXT |  |
| old_value | TEXT |  |
| new_value | TEXT |  |
| match_type | TEXT |  |

### dim_turnover_quality
**Rows:** 3 | **Columns:** 5

| Column | Type | Notes |
|--------|------|-------|
| turnover_quality_id | TEXT | Foreign key reference |
| turnover_quality_code | TEXT |  |
| turnover_quality_name | TEXT |  |
| description | TEXT |  |
| counts_against | INTEGER |  |

### dim_turnover_type
**Rows:** 21 | **Columns:** 9

| Column | Type | Notes |
|--------|------|-------|
| turnover_type_id | TEXT | Foreign key reference |
| turnover_type_code | TEXT |  |
| turnover_type_name | TEXT |  |
| category | TEXT |  |
| quality | TEXT |  |
| weight | TEXT |  |
| description | TEXT |  |
| zone_context | TEXT |  |
| zone_danger_multiplier | TEXT |  |

### dim_venue
**Rows:** 2 | **Columns:** 4

| Column | Type | Notes |
|--------|------|-------|
| venue_id | TEXT | Foreign key reference |
| venue_code | TEXT |  |
| venue_name | TEXT |  |
| venue_abbrev | TEXT |  |

### dim_zone
_Rink zones (Offensive, Neutral, Defensive)_

**Rows:** 3 | **Columns:** 4

| Column | Type | Notes |
|--------|------|-------|
| zone_id | TEXT | Foreign key reference |
| zone_code | TEXT |  |
| zone_name | TEXT |  |
| zone_abbrev | TEXT |  |

### dim_zone_entry_type
**Rows:** 11 | **Columns:** 9

| Column | Type | Notes |
|--------|------|-------|
| zone_entry_type_id | TEXT | Foreign key reference |
| zone_entry_type_code | TEXT |  |
| zone_entry_type_name | TEXT |  |
| control_level | TEXT |  |
| fenwick_per_entry | TEXT |  |
| shot_multiplier | TEXT |  |
| goal_prob_multiplier | TEXT |  |
| description | TEXT |  |
| expected_success_rate | TEXT |  |

### dim_zone_exit_type
**Rows:** 10 | **Columns:** 8

| Column | Type | Notes |
|--------|------|-------|
| zone_exit_type_id | TEXT | Foreign key reference |
| zone_exit_type_code | TEXT |  |
| zone_exit_type_name | TEXT |  |
| control_level | TEXT |  |
| leads_to_entry_pct | NUMERIC |  |
| possession_retained_pct | NUMERIC |  |
| offensive_value_weight | TEXT |  |
| description | TEXT |  |

## Fact Tables

### fact_cycle_events
**Rows:** 9 | **Columns:** 7

| Column | Type | Notes |
|--------|------|-------|
| game_id | TEXT | Foreign key reference |
| cycle_start_event_index | INTEGER |  |
| cycle_end_event_index | INTEGER |  |
| pass_count | INTEGER |  |
| is_cycle | BOOLEAN |  |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |

### fact_draft
**Rows:** 160 | **Columns:** 15

| Column | Type | Notes |
|--------|------|-------|
| team_id | TEXT | Foreign key reference |
| skill_rating | NUMERIC |  |
| round | TEXT |  |
| player_full_name | TEXT |  |
| player_id | TEXT | Foreign key reference |
| team_name | TEXT |  |
| restricted | TEXT |  |
| overall_draft_round | TEXT |  |
| overall_draft_position | TEXT |  |
| unrestricted_draft_position | TEXT |  |
| season | TEXT |  |
| season_id | TEXT | Foreign key reference |
| league | TEXT |  |
| player_draft_id | TEXT | Foreign key reference |
| league_id | TEXT | Foreign key reference |

### fact_event_chains
**Rows:** 295 | **Columns:** 15

| Column | Type | Notes |
|--------|------|-------|
| chain_id | TEXT | Foreign key reference |
| game_id | TEXT | Foreign key reference |
| entry_event_index | INTEGER |  |
| shot_event_index | INTEGER |  |
| events_to_shot | TEXT |  |
| entry_type | TEXT |  |
| shot_result | TEXT |  |
| is_goal | BOOLEAN |  |
| zone | TEXT |  |
| sequence_id | TEXT | Foreign key reference |
| zone_id | TEXT | Foreign key reference |
| zone_entry_type_id | TEXT | Foreign key reference |
| shot_result_type_id | TEXT | Foreign key reference |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |

### fact_events
_All tracked game events_

**Rows:** 5,833 | **Columns:** 54

| Column | Type | Notes |
|--------|------|-------|
| event_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| period | TEXT |  |
| event_index | INTEGER |  |
| linked_event_index | INTEGER |  |
| sequence_index | INTEGER |  |
| play_index | INTEGER |  |
| event_type | TEXT |  |
| tracking_event_index | INTEGER |  |
| event_start_min | TEXT |  |
| event_start_sec | TEXT |  |
| event_end_min | TEXT |  |
| event_end_sec | TEXT |  |
| role_abrev | TEXT |  |
| event_team_zone | TEXT |  |
| home_team_zone | TEXT |  |
| away_team_zone | TEXT |  |
| team_venue | TEXT |  |
| team_venue_abv | TEXT |  |
| side_of_puck | TEXT |  |
| play_detail1 | TEXT |  |
| play_detail_2 | TEXT |  |
| play_detail_successful | TEXT |  |
| pressured_pressurer | TEXT |  |
| zone_change_index | INTEGER |  |
| home_team | TEXT |  |
| away_team | TEXT |  |
| Type | TEXT |  |
| event_detail | TEXT |  |
| event_detail_2 | TEXT |  |
| event_successful | TEXT |  |
| shift_index | INTEGER |  |
| duration | INTEGER |  |
| time_start_total_seconds | TEXT |  |
| time_end_total_seconds | TEXT |  |
| running_intermission_duration | INTEGER |  |
| period_start_total_running_seconds | TEXT |  |
| running_video_time | TEXT |  |
| event_running_start | TEXT |  |
| event_running_end | TEXT |  |
| period_id | TEXT | Foreign key reference |
| venue_id | TEXT | Foreign key reference |
| event_type_id | TEXT | Foreign key reference |
| event_detail_id | TEXT | Foreign key reference |
| event_detail_2_id | TEXT | Foreign key reference |
| success_id | TEXT | Foreign key reference |
| play_detail_success_id | TEXT | Foreign key reference |
| zone_id | TEXT | Foreign key reference |
| play_detail_id | TEXT | Foreign key reference |
| play_detail_2_id | TEXT | Foreign key reference |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |
| shift_key | TEXT | Primary key |
| empty_net_goal | TEXT |  |

### fact_events_long
**Rows:** 11,136 | **Columns:** 32

| Column | Type | Notes |
|--------|------|-------|
| event_player_key | TEXT | Primary key |
| event_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| player_id | TEXT | Foreign key reference |
| player_name | TEXT |  |
| event_index | INTEGER |  |
| player_role | TEXT |  |
| role_number | INTEGER |  |
| event_type | TEXT |  |
| player_game_number | INTEGER |  |
| player_team | TEXT |  |
| period | TEXT |  |
| event_detail | TEXT |  |
| event_detail_2 | TEXT |  |
| event_successful | TEXT |  |
| play_detail1 | TEXT |  |
| play_detail_2 | TEXT |  |
| play_detail_successful | TEXT |  |
| team_venue | TEXT |  |
| side_of_puck | TEXT |  |
| play_detail | TEXT |  |
| period_id | TEXT | Foreign key reference |
| venue_id | TEXT | Foreign key reference |
| event_type_id | TEXT | Foreign key reference |
| event_detail_id | TEXT | Foreign key reference |
| event_detail_2_id | TEXT | Foreign key reference |
| success_id | TEXT | Foreign key reference |
| play_detail_success_id | TEXT | Foreign key reference |
| play_detail_id | TEXT | Foreign key reference |
| play_detail_2_id | TEXT | Foreign key reference |
| role_id | TEXT | Foreign key reference |
| player_team_id | TEXT | Foreign key reference |

### fact_events_player
_Events with player attribution_

**Rows:** 11,635 | **Columns:** 63

| Column | Type | Notes |
|--------|------|-------|
| event_player_key | TEXT | Primary key |
| event_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| player_id | TEXT | Foreign key reference |
| event_index | INTEGER |  |
| player_role | TEXT |  |
| role_number | INTEGER |  |
| period | TEXT |  |
| event_type | TEXT |  |
| player_game_number | INTEGER |  |
| linked_event_index | INTEGER |  |
| tracking_event_index | INTEGER |  |
| event_start_min | TEXT |  |
| event_start_sec | TEXT |  |
| event_end_min | TEXT |  |
| event_end_sec | TEXT |  |
| role_abrev | TEXT |  |
| event_team_zone | TEXT |  |
| home_team_zone | TEXT |  |
| away_team_zone | TEXT |  |
| team_venue | TEXT |  |
| team_venue_abv | TEXT |  |
| side_of_puck | TEXT |  |
| sequence_index | INTEGER |  |
| play_index | INTEGER |  |
| play_detail1 | TEXT |  |
| play_detail_2 | TEXT |  |
| play_detail_successful | TEXT |  |
| pressured_pressurer | TEXT |  |
| zone_change_index | INTEGER |  |
| home_team | TEXT |  |
| away_team | TEXT |  |
| Type | TEXT |  |
| event_detail | TEXT |  |
| event_detail_2 | TEXT |  |
| event_successful | TEXT |  |
| shift_index | INTEGER |  |
| duration | INTEGER |  |
| time_start_total_seconds | TEXT |  |
| time_end_total_seconds | TEXT |  |
| running_intermission_duration | INTEGER |  |
| period_start_total_running_seconds | TEXT |  |
| running_video_time | TEXT |  |
| event_running_start | TEXT |  |
| event_running_end | TEXT |  |
| player_team | TEXT |  |
| player_name | TEXT |  |
| play_detail | TEXT |  |
| period_id | TEXT | Foreign key reference |
| venue_id | TEXT | Foreign key reference |
| event_type_id | TEXT | Foreign key reference |
| event_detail_id | TEXT | Foreign key reference |
| event_detail_2_id | TEXT | Foreign key reference |
| success_id | TEXT | Foreign key reference |
| play_detail_success_id | TEXT | Foreign key reference |
| zone_id | TEXT | Foreign key reference |
| play_detail_id | TEXT | Foreign key reference |
| play_detail_2_id | TEXT | Foreign key reference |
| role_id | TEXT | Foreign key reference |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |
| player_team_id | TEXT | Foreign key reference |
| shift_key | TEXT | Primary key |

### fact_events_tracking
**Rows:** 11,918 | **Columns:** 46

| Column | Type | Notes |
|--------|------|-------|
| event_tracking_key | TEXT | Primary key |
| event_key | TEXT | Primary key |
| event_id | TEXT | Foreign key reference |
| game_id | TEXT | Foreign key reference |
| event_index | INTEGER |  |
| player_id | TEXT | Foreign key reference |
| player_game_number | INTEGER |  |
| period | TEXT |  |
| linked_event_index | INTEGER |  |
| tracking_event_index | INTEGER |  |
| event_start_min | TEXT |  |
| event_start_sec | TEXT |  |
| event_end_min | TEXT |  |
| event_end_sec | TEXT |  |
| role_abrev | TEXT |  |
| event_team_zone | TEXT |  |
| home_team_zone | TEXT |  |
| away_team_zone | TEXT |  |
| team_venue | TEXT |  |
| team_venue_abv | TEXT |  |
| side_of_puck | TEXT |  |
| sequence_index | INTEGER |  |
| play_index | INTEGER |  |
| play_detail1 | TEXT |  |
| play_detail_2 | TEXT |  |
| play_detail_successful | TEXT |  |
| pressured_pressurer | TEXT |  |
| zone_change_index | INTEGER |  |
| home_team | TEXT |  |
| away_team | TEXT |  |
| Type | TEXT |  |
| event_detail | TEXT |  |
| event_detail_2 | TEXT |  |
| event_successful | TEXT |  |
| shift_index | INTEGER |  |
| duration | INTEGER |  |
| time_start_total_seconds | TEXT |  |
| time_end_total_seconds | TEXT |  |
| running_intermission_duration | INTEGER |  |
| period_start_total_running_seconds | TEXT |  |
| running_video_time | TEXT |  |
| event_running_start | TEXT |  |
| event_running_end | TEXT |  |
| player_role | TEXT |  |
| role_number | INTEGER |  |
| player_team | TEXT |  |

### fact_game_status
**Rows:** 562 | **Columns:** 24

| Column | Type | Notes |
|--------|------|-------|
| game_id | TEXT | Foreign key reference |
| game_date | TIMESTAMP |  |
| home_team | TEXT |  |
| away_team | TEXT |  |
| official_home_goals | INTEGER |  |
| official_away_goals | INTEGER |  |
| official_total_goals | INTEGER |  |
| game_url | TEXT |  |
| tracking_status | TEXT |  |
| tracking_pct | NUMERIC |  |
| events_row_count | INTEGER |  |
| shifts_row_count | INTEGER |  |
| player_id_fill_pct | NUMERIC |  |
| goal_events | TEXT |  |
| periods_covered | TEXT |  |
| tracking_start_period | TEXT |  |
| tracking_start_time | TEXT |  |
| tracking_end_period | TEXT |  |
| tracking_end_time | TEXT |  |
| is_loaded | BOOLEAN |  |
| goals_in_stats | INTEGER |  |
| goal_match | TEXT |  |
| player_count | INTEGER |  |
| issues | TEXT |  |

### fact_gameroster
_Game rosters_

**Rows:** 14,471 | **Columns:** 29

| Column | Type | Notes |
|--------|------|-------|
| game_id | TEXT | Foreign key reference |
| team_game_id | TEXT | Foreign key reference |
| opp_team_game_id | TEXT | Foreign key reference |
| player_game_id | TEXT | Foreign key reference |
| team_venue | TEXT |  |
| team_name | TEXT |  |
| opp_team_name | TEXT |  |
| player_game_number | INTEGER |  |
| n_player_url | TEXT |  |
| player_position | TEXT |  |
| games_played | TEXT |  |
| goals | INTEGER |  |
| assist | TEXT |  |
| goals_against | INTEGER |  |
| pim | TEXT |  |
| shutouts | TEXT |  |
| team_id | TEXT | Foreign key reference |
| opp_team_id | TEXT | Foreign key reference |
| key | TEXT |  |
| player_full_name | TEXT |  |
| player_id | TEXT | Foreign key reference |
| date | TIMESTAMP |  |
| season | TEXT |  |
| sub | TEXT |  |
| current_team | TEXT |  |
| skill_rating | NUMERIC |  |
| venue_id | TEXT | Foreign key reference |
| position_id | TEXT | Foreign key reference |
| season_id | TEXT | Foreign key reference |

### fact_goalie_game_stats
**Rows:** 8 | **Columns:** 19

| Column | Type | Notes |
|--------|------|-------|
| goalie_game_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| player_id | TEXT | Foreign key reference |
| player_name | TEXT |  |
| team_name | TEXT |  |
| saves | TEXT |  |
| goals_against | INTEGER |  |
| shots_against | INTEGER |  |
| save_pct | NUMERIC |  |
| toi_seconds | TEXT |  |
| empty_net_ga | TEXT |  |
| saves_rebound | TEXT |  |
| saves_freeze | TEXT |  |
| saves_glove | TEXT |  |
| saves_blocker | TEXT |  |
| saves_left_pad | TEXT |  |
| saves_right_pad | TEXT |  |
| rebound_control_pct | NUMERIC |  |
| total_save_events | TEXT |  |

### fact_h2h
_Head-to-head player matchup stats_

**Rows:** 684 | **Columns:** 24

| Column | Type | Notes |
|--------|------|-------|
| game_id | TEXT | Foreign key reference |
| player_1_id | TEXT | Foreign key reference |
| player_2_id | TEXT | Foreign key reference |
| shifts_together | TEXT |  |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |
| toi_together | TEXT |  |
| goals_for | INTEGER |  |
| goals_against | INTEGER |  |
| plus_minus | TEXT |  |
| corsi_for | TEXT |  |
| corsi_against | TEXT |  |
| cf_pct | NUMERIC |  |
| fenwick_for | TEXT |  |
| fenwick_against | TEXT |  |
| ff_pct | NUMERIC |  |
| xgf | TEXT |  |
| xga | TEXT |  |
| xg_diff | TEXT |  |
| shots_for | INTEGER |  |
| shots_against | INTEGER |  |
| h2h_key | TEXT | Primary key |
| player_1_name | TEXT |  |
| player_2_name | TEXT |  |

### fact_head_to_head
**Rows:** 572 | **Columns:** 16

| Column | Type | Notes |
|--------|------|-------|
| game_id | TEXT | Foreign key reference |
| player_1_id | TEXT | Foreign key reference |
| player_1_name | TEXT |  |
| player_1_rating | NUMERIC |  |
| player_1_venue | TEXT |  |
| player_2_id | TEXT | Foreign key reference |
| player_2_name | TEXT |  |
| player_2_rating | NUMERIC |  |
| player_2_venue | TEXT |  |
| shifts_against | TEXT |  |
| toi_against_seconds | TEXT |  |
| rating_diff | NUMERIC |  |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |
| player_1_venue_id | TEXT | Foreign key reference |
| player_2_venue_id | TEXT | Foreign key reference |

### fact_leadership
**Rows:** 28 | **Columns:** 9

| Column | Type | Notes |
|--------|------|-------|
| player_full_name | TEXT |  |
| player_id | TEXT | Foreign key reference |
| leadership | TEXT |  |
| skill_rating | NUMERIC |  |
| n_player_url | TEXT |  |
| team_name | TEXT |  |
| team_id | TEXT | Foreign key reference |
| season | TEXT |  |
| season_id | TEXT | Foreign key reference |

### fact_league_leaders_snapshot
**Rows:** 14,473 | **Columns:** 13

| Column | Type | Notes |
|--------|------|-------|
| game_id | TEXT | Foreign key reference |
| date | TIMESTAMP |  |
| player_id | TEXT | Foreign key reference |
| player_name | TEXT |  |
| team_name | TEXT |  |
| gp | TEXT |  |
| goals | INTEGER |  |
| assists | INTEGER |  |
| pts | TEXT |  |
| pim | TEXT |  |
| gpg | TEXT |  |
| ppg | TEXT |  |
| team_id | TEXT | Foreign key reference |

### fact_line_combos
_Line combination statistics_

**Rows:** 332 | **Columns:** 40

| Column | Type | Notes |
|--------|------|-------|
| line_combo_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| venue | TEXT |  |
| forward_combo | TEXT |  |
| defense_combo | TEXT |  |
| shifts | TEXT |  |
| toi_together | TEXT |  |
| goals_for | INTEGER |  |
| goals_against | INTEGER |  |
| plus_minus | TEXT |  |
| corsi_for | TEXT |  |
| corsi_against | TEXT |  |
| xgf | TEXT |  |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |
| venue_id | TEXT | Foreign key reference |
| team_id | TEXT | Foreign key reference |
| fenwick_for | TEXT |  |
| fenwick_against | TEXT |  |
| ff_pct | NUMERIC |  |
| xg_against | TEXT |  |
| xg_diff | TEXT |  |
| xg_pct | NUMERIC |  |
| zone_entries | TEXT |  |
| zone_exits | TEXT |  |
| controlled_entry_pct | NUMERIC |  |
| giveaways | TEXT |  |
| takeaways | TEXT |  |
| turnover_diff | TEXT |  |
| avg_player_rating | NUMERIC |  |
| opp_avg_rating | NUMERIC |  |
| rating_diff | NUMERIC |  |
| pdo | TEXT |  |
| sh_pct | NUMERIC |  |
| sv_pct | NUMERIC |  |
| goals_per_60 | INTEGER |  |
| goals_against_per_60 | INTEGER |  |
| cf_per_60 | TEXT |  |
| ca_per_60 | TEXT |  |
| team_name | TEXT |  |

### fact_linked_events
**Rows:** 473 | **Columns:** 48

| Column | Type | Notes |
|--------|------|-------|
| linked_event_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| primary_event_index | INTEGER |  |
| event_count | INTEGER |  |
| event_1_index | INTEGER |  |
| event_1_type | TEXT |  |
| event_1_detail | TEXT |  |
| event_1_player_id | TEXT | Foreign key reference |
| event_2_index | INTEGER |  |
| event_2_type | TEXT |  |
| event_2_detail | TEXT |  |
| event_2_player_id | TEXT | Foreign key reference |
| event_3_index | INTEGER |  |
| event_3_type | TEXT |  |
| event_3_detail | TEXT |  |
| event_3_player_id | TEXT | Foreign key reference |
| event_4_index | INTEGER |  |
| event_4_type | TEXT |  |
| event_4_detail | TEXT |  |
| event_4_player_id | TEXT | Foreign key reference |
| event_5_index | INTEGER |  |
| event_5_type | TEXT |  |
| event_5_detail | TEXT |  |
| event_5_player_id | TEXT | Foreign key reference |
| event_1_key | TEXT | Primary key |
| event_2_key | TEXT | Primary key |
| event_3_key | TEXT | Primary key |
| event_4_key | TEXT | Primary key |
| event_5_key | TEXT | Primary key |
| team_venue | TEXT |  |
| team_id | TEXT | Foreign key reference |
| play_chain | TEXT |  |
| event_chain_indices | TEXT |  |
| venue_id | TEXT | Foreign key reference |
| video_time_start | TEXT |  |
| video_time_end | TEXT |  |
| event_1_type_id | TEXT | Foreign key reference |
| event_2_type_id | TEXT | Foreign key reference |
| event_3_type_id | TEXT | Foreign key reference |
| event_4_type_id | TEXT | Foreign key reference |
| event_5_type_id | TEXT | Foreign key reference |
| event_1_detail_id | TEXT | Foreign key reference |
| event_2_detail_id | TEXT | Foreign key reference |
| event_3_detail_id | TEXT | Foreign key reference |
| event_4_detail_id | TEXT | Foreign key reference |
| event_5_detail_id | TEXT | Foreign key reference |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |

### fact_matchup_summary
**Rows:** 684 | **Columns:** 29

| Column | Type | Notes |
|--------|------|-------|
| game_id | TEXT | Foreign key reference |
| player_1_id | TEXT | Foreign key reference |
| player_2_id | TEXT | Foreign key reference |
| shifts_together | TEXT |  |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |
| toi_together | TEXT |  |
| goals_for | INTEGER |  |
| goals_against | INTEGER |  |
| plus_minus | TEXT |  |
| corsi_for | TEXT |  |
| corsi_against | TEXT |  |
| cf_pct | NUMERIC |  |
| fenwick_for | TEXT |  |
| fenwick_against | TEXT |  |
| ff_pct | NUMERIC |  |
| xgf | TEXT |  |
| xga | TEXT |  |
| xg_diff | TEXT |  |
| shots_for | INTEGER |  |
| shots_against | INTEGER |  |
| p1_shifts_without_p2 | TEXT |  |
| p2_shifts_without_p1 | TEXT |  |
| cf_pct_together | NUMERIC |  |
| cf_pct_apart | NUMERIC |  |
| cf_pct_delta | NUMERIC |  |
| matchup_key | TEXT | Primary key |
| synergy_score | TEXT |  |
| is_positive_synergy | BOOLEAN |  |

### fact_player_boxscore_all
**Rows:** 14,473 | **Columns:** 23

| Column | Type | Notes |
|--------|------|-------|
| game_id | TEXT | Foreign key reference |
| player_id | TEXT | Foreign key reference |
| player_name | TEXT |  |
| player_number | INTEGER |  |
| player_position | TEXT |  |
| team_venue | TEXT |  |
| team_name | TEXT |  |
| team_id | TEXT | Foreign key reference |
| opp_team_name | TEXT |  |
| date | TIMESTAMP |  |
| season | TEXT |  |
| gp | TEXT |  |
| g | TEXT |  |
| a | TEXT |  |
| pts | TEXT |  |
| ga | TEXT |  |
| pim | TEXT |  |
| so | TEXT |  |
| skill_rating | NUMERIC |  |
| venue_id | TEXT | Foreign key reference |
| position_id | TEXT | Foreign key reference |
| season_id | TEXT | Foreign key reference |
| opp_team_id | TEXT | Foreign key reference |

### fact_player_event_chains
**Rows:** 5,831 | **Columns:** 22

| Column | Type | Notes |
|--------|------|-------|
| event_chain_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| event_index | INTEGER |  |
| event_key | TEXT | Primary key |
| event_type | TEXT |  |
| period | TEXT |  |
| home_player_count | INTEGER |  |
| away_player_count | INTEGER |  |
| home_player_1 | TEXT |  |
| home_player_2 | TEXT |  |
| home_player_3 | TEXT |  |
| away_player_1 | TEXT |  |
| away_player_2 | TEXT |  |
| away_player_3 | TEXT |  |
| home_players | TEXT |  |
| away_players | TEXT |  |
| running_video_time | TEXT |  |
| event_running_start | TEXT |  |
| period_id | TEXT | Foreign key reference |
| event_type_id | TEXT | Foreign key reference |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |

### fact_player_game_position
**Rows:** 105 | **Columns:** 10

| Column | Type | Notes |
|--------|------|-------|
| player_position_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| player_id | TEXT | Foreign key reference |
| logical_shifts | TEXT |  |
| dominant_position | TEXT |  |
| dominant_position_pct | NUMERIC |  |
| forward_shifts | TEXT |  |
| defense_shifts | TEXT |  |
| goalie_shifts | TEXT |  |
| player_name | TEXT |  |

### fact_player_game_stats
_Player statistics per game_

**Rows:** 107 | **Columns:** 317

| Column | Type | Notes |
|--------|------|-------|
| player_game_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| player_id | TEXT | Foreign key reference |
| player_name | TEXT |  |
| goals | INTEGER |  |
| assists | INTEGER |  |
| points | INTEGER |  |
| shots | INTEGER |  |
| sog | TEXT |  |
| shots_blocked | INTEGER |  |
| shots_missed | INTEGER |  |
| shooting_pct | NUMERIC |  |
| pass_attempts | TEXT |  |
| pass_completed | TEXT |  |
| pass_pct | NUMERIC |  |
| fo_wins | TEXT |  |
| fo_losses | TEXT |  |
| fo_total | TEXT |  |
| fo_pct | NUMERIC |  |
| zone_entries | TEXT |  |
| zone_exits | TEXT |  |
| giveaways | TEXT |  |
| takeaways | TEXT |  |
| toi_seconds | TEXT |  |
| toi_minutes | TEXT |  |
| playing_toi_seconds | TEXT |  |
| playing_toi_minutes | TEXT |  |
| stoppage_seconds | TEXT |  |
| shift_count | INTEGER |  |
| logical_shifts | TEXT |  |
| avg_shift | NUMERIC |  |
| avg_playing_shift | NUMERIC |  |
| goals_per_60 | INTEGER |  |
| assists_per_60 | INTEGER |  |
| points_per_60 | INTEGER |  |
| shots_per_60 | INTEGER |  |
| goals_per_60_playing | INTEGER |  |
| assists_per_60_playing | INTEGER |  |
| points_per_60_playing | INTEGER |  |
| shots_per_60_playing | INTEGER |  |
| blocks | TEXT |  |
| hits | TEXT |  |
| puck_battles | TEXT |  |
| puck_battle_wins | TEXT |  |
| retrievals | TEXT |  |
| corsi_for | TEXT |  |
| corsi_against | TEXT |  |
| fenwick_for | TEXT |  |
| fenwick_against | TEXT |  |
| cf_pct | NUMERIC |  |
| ff_pct | NUMERIC |  |
| opp_avg_rating | NUMERIC |  |
| skill_diff | TEXT |  |
| plus_ev | TEXT |  |
| minus_ev | TEXT |  |
| plus_minus_ev | TEXT |  |
| plus_total | TEXT |  |
| minus_total | TEXT |  |
| plus_minus_total | TEXT |  |
| plus_en_adj | TEXT |  |
| minus_en_adj | TEXT |  |
| plus_minus_en_adj | TEXT |  |
| player_rating | NUMERIC |  |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |
| chips | TEXT |  |
| breakout_rush_attempts | TEXT |  |
| zone_keepins | TEXT |  |
| dekes_successful | TEXT |  |
| breakout_clear_attempts | TEXT |  |
| beat_middle | TEXT |  |
| beat_wide | TEXT |  |
| zone_exit_denials | TEXT |  |
| breakouts | TEXT |  |
| passes_missed_target | TEXT |  |
| drives_corner | TEXT |  |
| tip_attempts | TEXT |  |
| cutbacks | TEXT |  |
| drives_middle | TEXT |  |
| pass_for_tip | TEXT |  |
| poke_checks | TEXT |  |
| stick_checks | TEXT |  |
| got_beat_middle | TEXT |  |
| crash_net | TEXT |  |
| cycle_plays | TEXT |  |
| ceded_exits | TEXT |  |
| reverse_passes | TEXT |  |
| deke_attempts | TEXT |  |
| breakout_pass_attempts | TEXT |  |
| backchecks | TEXT |  |
| separate_from_puck | TEXT |  |
| rebound_recoveries | TEXT |  |
| block_attempts | TEXT |  |
| drives_net | TEXT |  |
| ceded_entries | TEXT |  |
| puck_retrievals | TEXT |  |
| passes_intercepted | TEXT |  |
| stopped_deke | TEXT |  |
| dump_and_chase | TEXT |  |
| def_pass_deflected | TEXT |  |
| loose_puck_wins | TEXT |  |
| drives_wide | TEXT |  |
| puck_recoveries | TEXT |  |
| def_pass_intercepted | TEXT |  |
| screens | TEXT |  |
| front_of_net | TEXT |  |
| secondary_assists | INTEGER |  |
| in_lane | TEXT |  |
| quick_ups | TEXT |  |
| second_touches | TEXT |  |
| delays | TEXT |  |
| loose_puck_losses | TEXT |  |
| turnover_recoveries | TEXT |  |
| dump_recoveries | TEXT |  |
| pressures | TEXT |  |
| contains | TEXT |  |
| forechecks | TEXT |  |
| give_and_go | TEXT |  |
| passes_deflected | TEXT |  |
| lost_puck | TEXT |  |
| force_wide | TEXT |  |
| man_on_man | TEXT |  |
| dekes_beat_defender | TEXT |  |
| box_outs | TEXT |  |
| primary_assists | INTEGER |  |
| got_beat_wide | TEXT |  |
| zone_entry_denials | TEXT |  |
| surf_plays | TEXT |  |
| blocked_shots_play | INTEGER |  |
| drives_middle_success | TEXT |  |
| drives_wide_success | TEXT |  |
| drives_corner_success | TEXT |  |
| zone_entry_denials_success | TEXT |  |
| breakouts_success | TEXT |  |
| zone_entry_carry | TEXT |  |
| zone_entry_pass | TEXT |  |
| zone_entry_dump | TEXT |  |
| zone_exit_carry | TEXT |  |
| zone_exit_pass | TEXT |  |
| zone_exit_dump | TEXT |  |
| zone_exit_clear | TEXT |  |
| zone_entries_controlled | TEXT |  |
| zone_entries_uncontrolled | TEXT |  |
| zone_entry_success_rate | TEXT |  |
| zone_entry_control_pct | NUMERIC |  |
| zone_exits_controlled | TEXT |  |
| zone_exits_uncontrolled | TEXT |  |
| zone_exit_success_rate | TEXT |  |
| zone_exit_control_pct | NUMERIC |  |
| def_shots_against | INTEGER |  |
| def_goals_against | INTEGER |  |
| def_entries_allowed | TEXT |  |
| def_exits_denied | TEXT |  |
| def_times_beat_deke | TEXT |  |
| def_times_beat_speed | TEXT |  |
| def_times_beat_total | TEXT |  |
| def_takeaways | TEXT |  |
| def_forced_turnovers | TEXT |  |
| def_zone_clears | TEXT |  |
| def_blocked_shots | INTEGER |  |
| def_interceptions | TEXT |  |
| def_stick_checks | TEXT |  |
| def_poke_checks | TEXT |  |
| def_body_checks | TEXT |  |
| def_coverage_assignments | TEXT |  |
| def_battles_won | TEXT |  |
| def_battles_lost | TEXT |  |
| giveaways_bad | TEXT |  |
| giveaways_neutral | TEXT |  |
| giveaways_good | TEXT |  |
| turnover_diff_adjusted | TEXT |  |
| turnovers_oz | TEXT |  |
| turnovers_nz | TEXT |  |
| turnovers_dz | TEXT |  |
| giveaway_rate_per_60 | TEXT |  |
| takeaway_rate_per_60 | TEXT |  |
| goals_rating_adj | NUMERIC |  |
| assists_rating_adj | NUMERIC |  |
| points_rating_adj | NUMERIC |  |
| plus_minus_rating_adj | NUMERIC |  |
| cf_pct_rating_adj | NUMERIC |  |
| qoc_rating | NUMERIC |  |
| qot_rating | NUMERIC |  |
| expected_vs_rating | NUMERIC |  |
| xg_for | TEXT |  |
| xg_against | TEXT |  |
| xg_diff | TEXT |  |
| xg_pct | NUMERIC |  |
| goals_above_expected | INTEGER |  |
| shots_high_danger | INTEGER |  |
| shots_medium_danger | INTEGER |  |
| shots_low_danger | INTEGER |  |
| scoring_chances | TEXT |  |
| high_danger_chances | TEXT |  |
| xg_per_shot | TEXT |  |
| shot_quality_avg | NUMERIC |  |
| offensive_rating | NUMERIC |  |
| defensive_rating | NUMERIC |  |
| hustle_rating | NUMERIC |  |
| playmaking_rating | NUMERIC |  |
| shooting_rating | NUMERIC |  |
| physical_rating | NUMERIC |  |
| impact_score | TEXT |  |
| war_estimate | TEXT |  |
| avg_shift_too_long | NUMERIC |  |
| shift_length_warning | TEXT |  |
| fatigue_indicator | TEXT |  |
| sub_equity_score | TEXT |  |
| toi_vs_team_avg | NUMERIC |  |
| period_3_dropoff | TEXT |  |
| late_game_performance | TEXT |  |
| on_ice_sh_pct | NUMERIC |  |
| on_ice_sv_pct | NUMERIC |  |
| pdo | TEXT |  |
| pdo_5v5 | TEXT |  |
| fo_wins_oz | TEXT |  |
| fo_wins_nz | TEXT |  |
| fo_wins_dz | TEXT |  |
| fo_losses_oz | TEXT |  |
| fo_losses_nz | TEXT |  |
| fo_losses_dz | TEXT |  |
| fo_pct_oz | NUMERIC |  |
| fo_pct_nz | NUMERIC |  |
| fo_pct_dz | NUMERIC |  |
| zone_starts_oz_pct | NUMERIC |  |
| zone_starts_dz_pct | NUMERIC |  |
| game_score | TEXT |  |
| game_score_per_60 | TEXT |  |
| game_score_rating | NUMERIC |  |
| effective_game_rating | NUMERIC |  |
| rating_performance_delta | NUMERIC |  |
| playing_above_rating | NUMERIC |  |
| playing_below_rating | NUMERIC |  |
| playing_at_rating | NUMERIC |  |
| performance_tier | TEXT |  |
| performance_index | INTEGER |  |
| shots_successful | INTEGER |  |
| shots_unsuccessful | INTEGER |  |
| passes_successful | TEXT |  |
| passes_unsuccessful | TEXT |  |
| plays_successful | TEXT |  |
| plays_unsuccessful | TEXT |  |
| entries_successful | TEXT |  |
| entries_unsuccessful | TEXT |  |
| exits_successful | TEXT |  |
| exits_unsuccessful | TEXT |  |
| total_successful_plays | TEXT |  |
| total_unsuccessful_plays | TEXT |  |
| overall_success_rate | TEXT |  |
| shot_success_rate | TEXT |  |
| pass_success_rate | TEXT |  |
| play_success_rate | TEXT |  |
| times_pass_target | TEXT |  |
| passes_received_successful | TEXT |  |
| passes_received_unsuccessful | TEXT |  |
| pass_reception_rate | TEXT |  |
| times_target_oz | TEXT |  |
| times_target_nz | TEXT |  |
| times_target_dz | TEXT |  |
| slot_passes_received | TEXT |  |
| cross_ice_passes_received | TEXT |  |
| odd_man_rushes | TEXT |  |
| odd_man_rush_goals | INTEGER |  |
| odd_man_rush_shots | INTEGER |  |
| breakaway_attempts | TEXT |  |
| breakaway_goals | INTEGER |  |
| 2on1_rushes | TEXT |  |
| 3on2_rushes | TEXT |  |
| 2on0_rushes | TEXT |  |
| rush_entries | TEXT |  |
| rush_shots | INTEGER |  |
| rush_goals | INTEGER |  |
| counter_attacks | INTEGER |  |
| transition_plays | TEXT |  |
| times_targeted_by_opp | TEXT |  |
| times_targeted_shots | INTEGER |  |
| times_targeted_entries | TEXT |  |
| times_targeted_passes | TEXT |  |
| times_targeted_as_defender | TEXT |  |
| defensive_assignments | TEXT |  |
| times_attacked | TEXT |  |
| times_attacked_successfully | TEXT |  |
| times_attacked_unsuccessfully | TEXT |  |
| defensive_success_rate | TEXT |  |
| times_ep3 | TEXT |  |
| times_ep4 | TEXT |  |
| times_ep5 | TEXT |  |
| times_opp2 | TEXT |  |
| times_opp3 | TEXT |  |
| times_opp4 | TEXT |  |
| total_on_ice_events | TEXT |  |
| puck_touches_estimated | TEXT |  |
| involvement_rate | TEXT |  |
| support_plays | TEXT |  |
| goals_leading | INTEGER |  |
| goals_trailing | INTEGER |  |
| goals_tied | INTEGER |  |
| shots_leading | INTEGER |  |
| shots_trailing | INTEGER |  |
| shots_tied | INTEGER |  |
| first_period_points | INTEGER |  |
| second_period_points | INTEGER |  |
| third_period_points | INTEGER |  |
| first_period_shots | INTEGER |  |
| second_period_shots | INTEGER |  |
| third_period_shots | INTEGER |  |
| clutch_goals | INTEGER |  |
| empty_net_goals_for | INTEGER |  |
| shorthanded_goals | INTEGER |  |
| offensive_contribution | TEXT |  |
| defensive_contribution | TEXT |  |
| two_way_rating | NUMERIC |  |
| puck_possession_index | INTEGER |  |
| danger_creation_rate | TEXT |  |
| efficiency_score | TEXT |  |
| clutch_factor | TEXT |  |
| complete_player_score | TEXT |  |

### fact_player_micro_stats
**Rows:** 212 | **Columns:** 6

| Column | Type | Notes |
|--------|------|-------|
| micro_stat_key | TEXT | Primary key |
| player_game_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| player_id | TEXT | Foreign key reference |
| micro_stat | TEXT |  |
| count | INTEGER |  |

### fact_player_pair_stats
**Rows:** 475 | **Columns:** 12

| Column | Type | Notes |
|--------|------|-------|
| game_id | TEXT | Foreign key reference |
| player_1_id | TEXT | Foreign key reference |
| player_1_name | TEXT |  |
| player_1_rating | NUMERIC |  |
| player_2_id | TEXT | Foreign key reference |
| player_2_name | TEXT |  |
| player_2_rating | NUMERIC |  |
| shifts_together | TEXT |  |
| toi_together_seconds | TEXT |  |
| combined_rating | NUMERIC |  |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |

### fact_player_period_stats
**Rows:** 321 | **Columns:** 10

| Column | Type | Notes |
|--------|------|-------|
| player_period_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| player_id | TEXT | Foreign key reference |
| period | TEXT |  |
| events | TEXT |  |
| shots | INTEGER |  |
| goals | INTEGER |  |
| passes | TEXT |  |
| turnovers | TEXT |  |
| period_id | TEXT | Foreign key reference |

### fact_player_stats_long
**Rows:** 7,026 | **Columns:** 6

| Column | Type | Notes |
|--------|------|-------|
| player_stat_key | TEXT | Primary key |
| player_game_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| player_id | TEXT | Foreign key reference |
| stat_name | TEXT |  |
| stat_value | TEXT |  |

### fact_player_xy_long
**Rows:** 0 | **Columns:** 16

| Column | Type | Notes |
|--------|------|-------|
| player_xy_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| event_index | INTEGER |  |
| event_key | TEXT | Primary key |
| player_id | TEXT | Foreign key reference |
| player_key | TEXT | Primary key |
| team_id | TEXT | Foreign key reference |
| team_venue | TEXT |  |
| point_number | INTEGER |  |
| x | TEXT |  |
| y | TEXT |  |
| timestamp | TEXT |  |
| rink_coord_id | TEXT | Foreign key reference |
| rink_coord_id_home | TEXT |  |
| rink_coord_id_away | TEXT |  |
| venue_id | TEXT | Foreign key reference |

### fact_player_xy_wide
**Rows:** 0 | **Columns:** 50

| Column | Type | Notes |
|--------|------|-------|
| player_xy_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| event_index | INTEGER |  |
| event_key | TEXT | Primary key |
| player_id | TEXT | Foreign key reference |
| player_key | TEXT | Primary key |
| team_id | TEXT | Foreign key reference |
| team_venue | TEXT |  |
| point_count | INTEGER |  |
| x_1 | TEXT |  |
| y_1 | TEXT |  |
| timestamp_1 | TEXT |  |
| rink_coord_id_1 | TEXT |  |
| x_2 | TEXT |  |
| y_2 | TEXT |  |
| timestamp_2 | TEXT |  |
| rink_coord_id_2 | TEXT |  |
| x_3 | TEXT |  |
| y_3 | TEXT |  |
| timestamp_3 | TEXT |  |
| rink_coord_id_3 | TEXT |  |
| x_4 | TEXT |  |
| y_4 | TEXT |  |
| timestamp_4 | TEXT |  |
| rink_coord_id_4 | TEXT |  |
| x_5 | TEXT |  |
| y_5 | TEXT |  |
| timestamp_5 | TEXT |  |
| rink_coord_id_5 | TEXT |  |
| x_6 | TEXT |  |
| y_6 | TEXT |  |
| timestamp_6 | TEXT |  |
| rink_coord_id_6 | TEXT |  |
| x_7 | TEXT |  |
| y_7 | TEXT |  |
| timestamp_7 | TEXT |  |
| rink_coord_id_7 | TEXT |  |
| x_8 | TEXT |  |
| y_8 | TEXT |  |
| timestamp_8 | TEXT |  |
| rink_coord_id_8 | TEXT |  |
| x_9 | TEXT |  |
| y_9 | TEXT |  |
| timestamp_9 | TEXT |  |
| rink_coord_id_9 | TEXT |  |
| x_10 | TEXT |  |
| y_10 | TEXT |  |
| timestamp_10 | TEXT |  |
| rink_coord_id_10 | TEXT |  |
| venue_id | TEXT | Foreign key reference |

### fact_playergames
**Rows:** 3,010 | **Columns:** 25

| Column | Type | Notes |
|--------|------|-------|
| ID | TEXT |  |
| Date | TIMESTAMP |  |
| Type | TEXT |  |
| Team | TEXT |  |
| Opp | TEXT |  |
| # | TEXT |  |
| Player | TEXT |  |
| Position | TEXT |  |
| GP | TEXT |  |
| G | TEXT |  |
| A | TEXT |  |
| GA | TEXT |  |
| PIM | TEXT |  |
| SO | TEXT |  |
| Rank | TEXT |  |
| ID2 | TEXT |  |
| ID3 | TEXT |  |
| Season | TEXT |  |
| SeasonPlayerID | TEXT |  |
| player_game_id | TEXT | Foreign key reference |
| event_type_id | TEXT | Foreign key reference |
| position_id | TEXT | Foreign key reference |
| team_id | TEXT | Foreign key reference |
| opp_team_id | TEXT | Foreign key reference |
| season_id | TEXT | Foreign key reference |

### fact_plays
**Rows:** 2,714 | **Columns:** 25

| Column | Type | Notes |
|--------|------|-------|
| play_id | TEXT | Foreign key reference |
| game_id | TEXT | Foreign key reference |
| sequence_id | TEXT | Foreign key reference |
| play_index | INTEGER |  |
| first_event | TEXT |  |
| last_event | TEXT |  |
| event_count | INTEGER |  |
| sequence_index | INTEGER |  |
| team | TEXT |  |
| zone | TEXT |  |
| has_shot | BOOLEAN |  |
| start_seconds | TEXT |  |
| end_seconds | TEXT |  |
| duration_seconds | INTEGER |  |
| play_key | TEXT | Primary key |
| zone_id | TEXT | Foreign key reference |
| team_id | TEXT | Foreign key reference |
| first_event_key | TEXT | Primary key |
| last_event_key | TEXT | Primary key |
| play_chain | TEXT |  |
| event_chain_indices | TEXT |  |
| video_time_start | TEXT |  |
| video_time_end | TEXT |  |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |

### fact_possession_time
**Rows:** 107 | **Columns:** 14

| Column | Type | Notes |
|--------|------|-------|
| possession_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| player_id | TEXT | Foreign key reference |
| venue | TEXT |  |
| zone_entries | TEXT |  |
| zone_exits | TEXT |  |
| ozone_entries | TEXT |  |
| dzone_entries | TEXT |  |
| possession_events | TEXT |  |
| estimated_possession_seconds | TEXT |  |
| venue_id | TEXT | Foreign key reference |
| team_id | TEXT | Foreign key reference |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |

### fact_puck_xy_long
**Rows:** 0 | **Columns:** 12

| Column | Type | Notes |
|--------|------|-------|
| puck_xy_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| event_index | INTEGER |  |
| event_key | TEXT | Primary key |
| point_number | INTEGER |  |
| x | TEXT |  |
| y | TEXT |  |
| z | TEXT |  |
| timestamp | TEXT |  |
| rink_coord_id | TEXT | Foreign key reference |
| rink_coord_id_home | TEXT |  |
| rink_coord_id_away | TEXT |  |

### fact_puck_xy_wide
**Rows:** 0 | **Columns:** 55

| Column | Type | Notes |
|--------|------|-------|
| puck_xy_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| event_index | INTEGER |  |
| event_key | TEXT | Primary key |
| point_count | INTEGER |  |
| x_1 | TEXT |  |
| y_1 | TEXT |  |
| z_1 | TEXT |  |
| timestamp_1 | TEXT |  |
| rink_coord_id_1 | TEXT |  |
| x_2 | TEXT |  |
| y_2 | TEXT |  |
| z_2 | TEXT |  |
| timestamp_2 | TEXT |  |
| rink_coord_id_2 | TEXT |  |
| x_3 | TEXT |  |
| y_3 | TEXT |  |
| z_3 | TEXT |  |
| timestamp_3 | TEXT |  |
| rink_coord_id_3 | TEXT |  |
| x_4 | TEXT |  |
| y_4 | TEXT |  |
| z_4 | TEXT |  |
| timestamp_4 | TEXT |  |
| rink_coord_id_4 | TEXT |  |
| x_5 | TEXT |  |
| y_5 | TEXT |  |
| z_5 | TEXT |  |
| timestamp_5 | TEXT |  |
| rink_coord_id_5 | TEXT |  |
| x_6 | TEXT |  |
| y_6 | TEXT |  |
| z_6 | TEXT |  |
| timestamp_6 | TEXT |  |
| rink_coord_id_6 | TEXT |  |
| x_7 | TEXT |  |
| y_7 | TEXT |  |
| z_7 | TEXT |  |
| timestamp_7 | TEXT |  |
| rink_coord_id_7 | TEXT |  |
| x_8 | TEXT |  |
| y_8 | TEXT |  |
| z_8 | TEXT |  |
| timestamp_8 | TEXT |  |
| rink_coord_id_8 | TEXT |  |
| x_9 | TEXT |  |
| y_9 | TEXT |  |
| z_9 | TEXT |  |
| timestamp_9 | TEXT |  |
| rink_coord_id_9 | TEXT |  |
| x_10 | TEXT |  |
| y_10 | TEXT |  |
| z_10 | TEXT |  |
| timestamp_10 | TEXT |  |
| rink_coord_id_10 | TEXT |  |

### fact_registration
_Player registration data_

**Rows:** 190 | **Columns:** 19

| Column | Type | Notes |
|--------|------|-------|
| player_full_name | TEXT |  |
| player_id | TEXT | Foreign key reference |
| season_id | TEXT | Foreign key reference |
| season | TEXT |  |
| restricted | TEXT |  |
| email | TEXT |  |
| position | TEXT |  |
| norad_experience | TEXT |  |
| CAF | TEXT |  |
| highest_beer_league_played | TEXT |  |
| skill_rating | NUMERIC |  |
| age | TEXT |  |
| referred_by | TEXT |  |
| notes | TEXT |  |
| sub_yn | TEXT |  |
| drafted_team_name | TEXT |  |
| drafted_team_id | TEXT | Foreign key reference |
| player_season_registration_id | TEXT | Foreign key reference |
| position_id | TEXT | Foreign key reference |

### fact_rush_events
**Rows:** 199 | **Columns:** 12

| Column | Type | Notes |
|--------|------|-------|
| game_id | TEXT | Foreign key reference |
| entry_event_index | INTEGER |  |
| shot_event_index | INTEGER |  |
| events_to_shot | TEXT |  |
| is_rush | BOOLEAN |  |
| rush_type | TEXT |  |
| is_goal | BOOLEAN |  |
| entry_type | TEXT |  |
| zone_entry_type_id | TEXT | Foreign key reference |
| rush_type_id | TEXT | Foreign key reference |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |

### fact_scoring_chances
**Rows:** 451 | **Columns:** 14

| Column | Type | Notes |
|--------|------|-------|
| scoring_chance_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| event_index | INTEGER |  |
| period | TEXT |  |
| is_goal | BOOLEAN |  |
| danger_level | TEXT |  |
| is_rebound | BOOLEAN |  |
| is_rush | BOOLEAN |  |
| is_odd_man | BOOLEAN |  |
| event_detail | TEXT |  |
| event_detail_2 | TEXT |  |
| period_id | TEXT | Foreign key reference |
| event_detail_id | TEXT | Foreign key reference |
| event_detail_2_id | TEXT | Foreign key reference |

### fact_sequences
**Rows:** 1,088 | **Columns:** 28

| Column | Type | Notes |
|--------|------|-------|
| sequence_id | TEXT | Foreign key reference |
| game_id | TEXT | Foreign key reference |
| sequence_index | INTEGER |  |
| first_event | TEXT |  |
| last_event | TEXT |  |
| event_count | INTEGER |  |
| start_team | TEXT |  |
| end_team | TEXT |  |
| start_zone | TEXT |  |
| end_zone | TEXT |  |
| has_goal | BOOLEAN |  |
| start_seconds | TEXT |  |
| end_seconds | TEXT |  |
| duration_seconds | INTEGER |  |
| sequence_key | TEXT | Primary key |
| first_event_key | TEXT | Primary key |
| last_event_key | TEXT | Primary key |
| start_zone_id | TEXT | Foreign key reference |
| end_zone_id | TEXT | Foreign key reference |
| video_time_start | TEXT |  |
| play_chain | TEXT |  |
| event_chain_indices | TEXT |  |
| team_id | TEXT | Foreign key reference |
| video_time_end | TEXT |  |
| start_team_id | TEXT | Foreign key reference |
| end_team_id | TEXT | Foreign key reference |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |

### fact_shift_players
**Rows:** 5,513 | **Columns:** 9

| Column | Type | Notes |
|--------|------|-------|
| shift_player_id | TEXT | Foreign key reference |
| shift_id | TEXT | Foreign key reference |
| game_id | TEXT | Foreign key reference |
| shift_index | INTEGER |  |
| player_game_number | INTEGER |  |
| player_id | TEXT | Foreign key reference |
| venue | TEXT |  |
| position | TEXT |  |
| period | TEXT |  |

### fact_shift_quality
**Rows:** 4,626 | **Columns:** 13

| Column | Type | Notes |
|--------|------|-------|
| shift_quality_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| player_id | TEXT | Foreign key reference |
| shift_index | INTEGER |  |
| shift_duration | INTEGER |  |
| shift_quality | TEXT |  |
| quality_score | TEXT |  |
| period | TEXT |  |
| strength | TEXT |  |
| situation | TEXT |  |
| period_id | TEXT | Foreign key reference |
| strength_id | TEXT | Foreign key reference |
| situation_id | TEXT | Foreign key reference |

### fact_shift_quality_logical
**Rows:** 105 | **Columns:** 10

| Column | Type | Notes |
|--------|------|-------|
| player_game_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| player_id | TEXT | Foreign key reference |
| player_name | TEXT |  |
| logical_shifts | TEXT |  |
| toi_seconds | TEXT |  |
| avg_logical_shift | NUMERIC |  |
| points_per_shift | INTEGER |  |
| shots_per_shift | INTEGER |  |
| shift_quality_score | TEXT |  |

### fact_shifts
_All player shifts_

**Rows:** 672 | **Columns:** 63

| Column | Type | Notes |
|--------|------|-------|
| shift_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| shift_index | INTEGER |  |
| Period | TEXT |  |
| shift_start_min | TEXT |  |
| shift_start_sec | TEXT |  |
| shift_end_min | TEXT |  |
| shift_end_sec | TEXT |  |
| shift_start_type | TEXT |  |
| shift_stop_type | TEXT |  |
| home_forward_1 | TEXT |  |
| home_forward_2 | TEXT |  |
| home_forward_3 | TEXT |  |
| home_defense_1 | TEXT |  |
| home_defense_2 | TEXT |  |
| home_xtra | TEXT |  |
| home_goalie | TEXT |  |
| away_forward_1 | TEXT |  |
| away_forward_2 | TEXT |  |
| away_forward_3 | TEXT |  |
| away_defense_1 | TEXT |  |
| away_defense_2 | TEXT |  |
| away_xtra | TEXT |  |
| away_goalie | TEXT |  |
| stoppage_time | TEXT |  |
| home_ozone_start | TEXT |  |
| home_ozone_end | TEXT |  |
| home_dzone_start | TEXT |  |
| home_dzone_end | TEXT |  |
| home_nzone_start | TEXT |  |
| home_nzone_end | TEXT |  |
| home_team | TEXT |  |
| away_team | TEXT |  |
| shift_start_total_seconds | TEXT |  |
| shift_end_total_seconds | TEXT |  |
| shift_duration | INTEGER |  |
| home_team_strength | TEXT |  |
| away_team_strength | TEXT |  |
| home_team_en | TEXT |  |
| away_team_en | TEXT |  |
| home_team_pk | TEXT |  |
| home_team_pp | TEXT |  |
| away_team_pp | TEXT |  |
| away_team_pk | TEXT |  |
| situation | TEXT |  |
| strength | TEXT |  |
| home_goals | INTEGER |  |
| away_goals | INTEGER |  |
| home_team_plus | TEXT |  |
| home_team_minus | TEXT |  |
| away_team_plus | TEXT |  |
| away_team_minus | TEXT |  |
| period_start_total_running_seconds | TEXT |  |
| running_video_time | TEXT |  |
| shift_start_running_time | TEXT |  |
| shift_end_running_time | TEXT |  |
| strength_id | TEXT | Foreign key reference |
| situation_id | TEXT | Foreign key reference |
| shift_start_type_id | TEXT | Foreign key reference |
| shift_stop_type_id | TEXT | Foreign key reference |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |
| period_id | TEXT | Foreign key reference |

### fact_shifts_long
**Rows:** 4,336 | **Columns:** 28

| Column | Type | Notes |
|--------|------|-------|
| shift_player_key | TEXT | Primary key |
| shift_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| shift_index | INTEGER |  |
| player_number | INTEGER |  |
| player_id | TEXT | Foreign key reference |
| player_name | TEXT |  |
| venue | TEXT |  |
| slot | TEXT |  |
| period | TEXT |  |
| shift_duration | INTEGER |  |
| playing_duration | INTEGER |  |
| situation | TEXT |  |
| strength | TEXT |  |
| stoppage_time | TEXT |  |
| pm_plus_ev | TEXT |  |
| pm_minus_ev | TEXT |  |
| goal_for | TEXT |  |
| goal_against | TEXT |  |
| team_en | TEXT |  |
| opp_en | TEXT |  |
| logical_shift_number | INTEGER |  |
| period_id | TEXT | Foreign key reference |
| venue_id | TEXT | Foreign key reference |
| strength_id | TEXT | Foreign key reference |
| situation_id | TEXT | Foreign key reference |
| slot_id | TEXT | Foreign key reference |
| team_id | TEXT | Foreign key reference |

### fact_shifts_player
**Rows:** 4,626 | **Columns:** 35

| Column | Type | Notes |
|--------|------|-------|
| shift_player_key | TEXT | Primary key |
| shift_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| shift_index | INTEGER |  |
| player_number | INTEGER |  |
| venue | TEXT |  |
| slot | TEXT |  |
| period | TEXT |  |
| shift_duration | INTEGER |  |
| situation | TEXT |  |
| strength | TEXT |  |
| stoppage_time | TEXT |  |
| pm_plus_ev | TEXT |  |
| pm_minus_ev | TEXT |  |
| goal_for | TEXT |  |
| goal_against | TEXT |  |
| team_en | TEXT |  |
| opp_en | TEXT |  |
| team_pp | TEXT |  |
| team_pk | TEXT |  |
| player_id | TEXT | Foreign key reference |
| player_name | TEXT |  |
| logical_shift_number | INTEGER |  |
| shift_segment | TEXT |  |
| cumulative_shift_duration | INTEGER |  |
| running_toi | TEXT |  |
| playing_duration | INTEGER |  |
| running_playing_toi | TEXT |  |
| period_id | TEXT | Foreign key reference |
| venue_id | TEXT | Foreign key reference |
| strength_id | TEXT | Foreign key reference |
| situation_id | TEXT | Foreign key reference |
| slot_id | TEXT | Foreign key reference |
| team_id | TEXT | Foreign key reference |
| team_name | TEXT |  |

### fact_shifts_tracking
**Rows:** 476 | **Columns:** 58

| Column | Type | Notes |
|--------|------|-------|
| shift_tracking_key | TEXT | Primary key |
| shift_key | TEXT | Primary key |
| shift_id | TEXT | Foreign key reference |
| game_id | TEXT | Foreign key reference |
| shift_index | INTEGER |  |
| Period | TEXT |  |
| shift_start_min | TEXT |  |
| shift_start_sec | TEXT |  |
| shift_end_min | TEXT |  |
| shift_end_sec | TEXT |  |
| shift_start_type | TEXT |  |
| shift_stop_type | TEXT |  |
| home_forward_1 | TEXT |  |
| home_forward_2 | TEXT |  |
| home_forward_3 | TEXT |  |
| home_defense_1 | TEXT |  |
| home_defense_2 | TEXT |  |
| home_xtra | TEXT |  |
| home_goalie | TEXT |  |
| away_forward_1 | TEXT |  |
| away_forward_2 | TEXT |  |
| away_forward_3 | TEXT |  |
| away_defense_1 | TEXT |  |
| away_defense_2 | TEXT |  |
| away_xtra | TEXT |  |
| away_goalie | TEXT |  |
| stoppage_time | TEXT |  |
| home_ozone_start | TEXT |  |
| home_ozone_end | TEXT |  |
| home_dzone_start | TEXT |  |
| home_dzone_end | TEXT |  |
| home_nzone_start | TEXT |  |
| home_nzone_end | TEXT |  |
| home_team | TEXT |  |
| away_team | TEXT |  |
| shift_start_total_seconds | TEXT |  |
| shift_end_total_seconds | TEXT |  |
| shift_duration | INTEGER |  |
| home_team_strength | TEXT |  |
| away_team_strength | TEXT |  |
| home_team_en | TEXT |  |
| away_team_en | TEXT |  |
| home_team_pk | TEXT |  |
| home_team_pp | TEXT |  |
| away_team_pp | TEXT |  |
| away_team_pk | TEXT |  |
| situation | TEXT |  |
| strength | TEXT |  |
| home_goals | INTEGER |  |
| away_goals | INTEGER |  |
| home_team_plus | TEXT |  |
| home_team_minus | TEXT |  |
| away_team_plus | TEXT |  |
| away_team_minus | TEXT |  |
| period_start_total_running_seconds | TEXT |  |
| running_video_time | TEXT |  |
| shift_start_running_time | TEXT |  |
| shift_end_running_time | TEXT |  |

### fact_shot_danger
**Rows:** 435 | **Columns:** 10

| Column | Type | Notes |
|--------|------|-------|
| shot_danger_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| event_index | INTEGER |  |
| danger_zone | TEXT |  |
| xg | TEXT |  |
| shot_distance | TEXT |  |
| shot_angle | TEXT |  |
| is_rebound | BOOLEAN |  |
| is_rush | BOOLEAN |  |
| is_one_timer | BOOLEAN |  |

### fact_shot_xy
**Rows:** 0 | **Columns:** 31

| Column | Type | Notes |
|--------|------|-------|
| shot_xy_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| event_index | INTEGER |  |
| event_key | TEXT | Primary key |
| player_id | TEXT | Foreign key reference |
| player_key | TEXT | Primary key |
| team_id | TEXT | Foreign key reference |
| team_venue | TEXT |  |
| period | TEXT |  |
| period_id | TEXT | Foreign key reference |
| shot_x | TEXT |  |
| shot_y | TEXT |  |
| shot_rink_coord_id | TEXT | Foreign key reference |
| shot_rink_coord_id_home | TEXT |  |
| shot_rink_coord_id_away | TEXT |  |
| shot_distance | TEXT |  |
| shot_angle | TEXT |  |
| target_x | TEXT |  |
| target_y | TEXT |  |
| net_location_id | TEXT | Foreign key reference |
| shot_type | TEXT |  |
| shot_result | TEXT |  |
| is_goal | BOOLEAN |  |
| is_on_net | BOOLEAN |  |
| strength_id | TEXT | Foreign key reference |
| goalie_player_id | TEXT | Foreign key reference |
| xg | TEXT |  |
| running_video_time | TEXT |  |
| venue_id | TEXT | Foreign key reference |
| shot_type_id | TEXT | Foreign key reference |
| shot_result_type_id | TEXT | Foreign key reference |

### fact_suspicious_stats
**Rows:** 18 | **Columns:** 14

| Column | Type | Notes |
|--------|------|-------|
| game_id | TEXT | Foreign key reference |
| player_id | TEXT | Foreign key reference |
| player_name | TEXT |  |
| position | TEXT |  |
| stat_name | TEXT |  |
| stat_value | TEXT |  |
| threshold | TEXT |  |
| threshold_direction | TEXT |  |
| flag_type | TEXT |  |
| severity | TEXT |  |
| category | TEXT |  |
| note | TEXT |  |
| resolved | TEXT |  |
| created_at | TIMESTAMP |  |

### fact_team_game_stats
_Team statistics per game_

**Rows:** 8 | **Columns:** 52

| Column | Type | Notes |
|--------|------|-------|
| team_game_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| venue | TEXT |  |
| goals | INTEGER |  |
| shots | INTEGER |  |
| fo_wins | TEXT |  |
| giveaways | TEXT |  |
| takeaways | TEXT |  |
| zone_entries | TEXT |  |
| zone_exits | TEXT |  |
| pass_attempts | TEXT |  |
| pass_completed | TEXT |  |
| fo_losses | TEXT |  |
| sog | TEXT |  |
| fo_total | TEXT |  |
| fo_pct | NUMERIC |  |
| pass_pct | NUMERIC |  |
| shooting_pct | NUMERIC |  |
| venue_id | TEXT | Foreign key reference |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |
| team_id | TEXT | Foreign key reference |
| total_shots | INTEGER |  |
| total_sog | TEXT |  |
| total_passes | TEXT |  |
| total_pass_completed | TEXT |  |
| team_pass_pct | NUMERIC |  |
| total_zone_entries | TEXT |  |
| total_zone_exits | TEXT |  |
| controlled_entries | TEXT |  |
| controlled_exits | TEXT |  |
| entry_control_pct | NUMERIC |  |
| total_giveaways | TEXT |  |
| total_takeaways | TEXT |  |
| turnover_diff | TEXT |  |
| total_blocks | TEXT |  |
| total_hits | TEXT |  |
| total_fo_wins | TEXT |  |
| total_fo_losses | TEXT |  |
| corsi_for | TEXT |  |
| corsi_against | TEXT |  |
| cf_pct | NUMERIC |  |
| xg_for | TEXT |  |
| xg_against | TEXT |  |
| xg_diff | TEXT |  |
| avg_player_rating | NUMERIC |  |
| total_dekes | TEXT |  |
| total_screens | TEXT |  |
| offensive_rating_avg | NUMERIC |  |
| defensive_rating_avg | NUMERIC |  |
| hustle_rating_avg | NUMERIC |  |
| team_name | TEXT |  |

### fact_team_standings_snapshot
**Rows:** 1,124 | **Columns:** 14

| Column | Type | Notes |
|--------|------|-------|
| game_id | TEXT | Foreign key reference |
| date | TIMESTAMP |  |
| team_name | TEXT |  |
| games_played | TEXT |  |
| wins | TEXT |  |
| losses | TEXT |  |
| ties | TEXT |  |
| points | INTEGER |  |
| goals_for | INTEGER |  |
| goals_against | INTEGER |  |
| goal_diff | TEXT |  |
| gaa | TEXT |  |
| gpg | TEXT |  |
| team_id | TEXT | Foreign key reference |

### fact_team_zone_time
**Rows:** 8 | **Columns:** 18

| Column | Type | Notes |
|--------|------|-------|
| zone_time_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| venue | TEXT |  |
| ozone_events | TEXT |  |
| dzone_events | TEXT |  |
| nzone_events | TEXT |  |
| total_events | TEXT |  |
| ozone_pct | NUMERIC |  |
| dzone_pct | NUMERIC |  |
| nzone_pct | NUMERIC |  |
| venue_id | TEXT | Foreign key reference |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |
| team_id | TEXT | Foreign key reference |
| oz_dominance | TEXT |  |
| dz_pressure | TEXT |  |
| territorial_index | INTEGER |  |
| team_name | TEXT |  |

### fact_video
_Video links for games_

**Rows:** 10 | **Columns:** 15

| Column | Type | Notes |
|--------|------|-------|
| video_key | TEXT | Primary key |
| game_id | TEXT | Foreign key reference |
| Index | INTEGER |  |
| Key | TEXT |  |
| Game_ID | TEXT | Foreign key reference |
| Video_Type | TEXT |  |
| Video_Category | TEXT |  |
| Url_1 | TEXT |  |
| Url_2 | TEXT |  |
| Url_3 | TEXT |  |
| Url_4 | TEXT |  |
| Video_ID | TEXT | Foreign key reference |
| Extension | TEXT |  |
| Embed_Url | TEXT |  |
| Description | TEXT |  |

### fact_wowy
_With Or Without You analysis_

**Rows:** 641 | **Columns:** 28

| Column | Type | Notes |
|--------|------|-------|
| game_id | TEXT | Foreign key reference |
| player_1_id | TEXT | Foreign key reference |
| player_2_id | TEXT | Foreign key reference |
| venue | TEXT |  |
| shifts_together | TEXT |  |
| p1_shifts_without_p2 | TEXT |  |
| p2_shifts_without_p1 | TEXT |  |
| p1_logical_shifts | TEXT |  |
| p2_logical_shifts | TEXT |  |
| venue_id | TEXT | Foreign key reference |
| home_team_id | TEXT | Foreign key reference |
| away_team_id | TEXT | Foreign key reference |
| toi_together | TEXT |  |
| toi_apart | TEXT |  |
| gf_pct_together | NUMERIC |  |
| gf_pct_apart | NUMERIC |  |
| gf_pct_delta | NUMERIC |  |
| cf_pct_together | NUMERIC |  |
| cf_pct_apart | NUMERIC |  |
| cf_pct_delta | NUMERIC |  |
| xgf_pct_together | NUMERIC |  |
| xgf_pct_apart | NUMERIC |  |
| xgf_pct_delta | NUMERIC |  |
| relative_corsi | TEXT |  |
| relative_fenwick | TEXT |  |
| wowy_key | TEXT | Primary key |
| player_1_name | TEXT |  |
| player_2_name | TEXT |  |

## QA Tables

### qa_suspicious_stats
**Rows:** 22 | **Columns:** 11

| Column | Type | Notes |
|--------|------|-------|
| timestamp | TEXT |  |
| game_id | TEXT | Foreign key reference |
| player_id | TEXT | Foreign key reference |
| player_name | TEXT |  |
| category | TEXT |  |
| stat | TEXT |  |
| value | TEXT |  |
| expected | TEXT |  |
| severity | TEXT |  |
| note | TEXT |  |
| resolved | TEXT |  |
