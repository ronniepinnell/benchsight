# BenchSight Table Inventory

Last Updated: 2026-01-12
Version: 24.3

**Total Tables:** 121

## Dimension Tables

| Table | Rows | Columns |
|-------|------|--------|
| dim_comparison_type | 6 | 5 |
| dim_competition_tier | 4 | 4 |
| dim_composite_rating | 8 | 6 |
| dim_danger_level | 3 | 4 |
| dim_danger_zone | 4 | 5 |
| dim_event_detail | 55 | 11 |
| dim_event_detail_2 | 176 | 12 |
| dim_event_type | 23 | 7 |
| dim_giveaway_type | 13 | 4 |
| dim_league | 2 | 2 |
| dim_micro_stat | 22 | 4 |
| dim_net_location | 10 | 5 |
| dim_pass_outcome | 4 | 4 |
| dim_pass_type | 8 | 4 |
| dim_period | 5 | 5 |
| dim_play_detail | 111 | 6 |
| dim_play_detail_2 | 111 | 6 |
| dim_player | 337 | 20 |
| dim_player_role | 14 | 5 |
| dim_playerurlref | 550 | 3 |
| dim_position | 6 | 4 |
| dim_randomnames | 486 | 5 |
| dim_rating | 5 | 3 |
| dim_rating_matchup | 5 | 4 |
| dim_rink_zone | 201 | 13 |
| dim_save_outcome | 3 | 4 |
| dim_schedule | 567 | 37 |
| dim_season | 9 | 8 |
| dim_shift_slot | 7 | 3 |
| dim_shift_start_type | 9 | 2 |
| dim_shift_stop_type | 18 | 2 |
| dim_shot_outcome | 5 | 8 |
| dim_shot_type | 6 | 4 |
| dim_situation | 4 | 2 |
| dim_stat | 39 | 12 |
| dim_stat_category | 13 | 4 |
| dim_stat_type | 8 | 6 |
| dim_stoppage_type | 4 | 3 |
| dim_strength | 18 | 7 |
| dim_success | 3 | 4 |
| dim_takeaway_type | 8 | 3 |
| dim_team | 17 | 13 |
| dim_terminology_mapping | 23 | 4 |
| dim_turnover_quality | 3 | 5 |
| dim_turnover_type | 12 | 10 |
| dim_venue | 2 | 4 |
| dim_zone | 3 | 4 |
| dim_zone_entry_type | 13 | 4 |
| dim_zone_exit_type | 12 | 4 |
| dim_zone_outcome | 6 | 5 |

**Dimension Tables:** 50

## Fact Tables

| Table | Rows | Columns |
|-------|------|--------|
| fact_breakouts | 476 | 142 |
| fact_cycle_events | 39 | 22 |
| fact_draft | 160 | 14 |
| fact_event_chains | 5,823 | 7 |
| fact_event_players | 11,155 | 110 |
| fact_events | 5,823 | 140 |
| fact_faceoffs | 169 | 142 |
| fact_gameroster | 14,597 | 24 |
| fact_goalie_game_stats | 8 | 17 |
| fact_h2h | 621 | 14 |
| fact_head_to_head | 621 | 15 |
| fact_high_danger_chances | 23 | 141 |
| fact_leadership | 28 | 9 |
| fact_line_combos | 199 | 13 |
| fact_linked_events | 5,823 | 7 |
| fact_matchup_performance | 621 | 33 |
| fact_matchup_summary | 621 | 16 |
| fact_penalties | 11 | 141 |
| fact_period_momentum | 24 | 9 |
| fact_player_career_stats | 0 | 5 |
| fact_player_event_chains | 0 | 6 |
| fact_player_game_position | 107 | 8 |
| fact_player_game_stats | 107 | 70 |
| fact_player_micro_stats | 107 | 12 |
| fact_player_pair_stats | 621 | 16 |
| fact_player_period_stats | 321 | 9 |
| fact_player_qoc_summary | 107 | 8 |
| fact_player_xy_long | 0 | 9 |
| fact_player_xy_wide | 0 | 28 |
| fact_playergames | 14,597 | 4 |
| fact_plays | 2,202 | 39 |
| fact_possession_time | 107 | 11 |
| fact_puck_xy_long | 0 | 8 |
| fact_puck_xy_wide | 0 | 8 |
| fact_registration | 190 | 18 |
| fact_rush_events | 206 | 9 |
| fact_rushes | 421 | 142 |
| fact_saves | 213 | 141 |
| fact_scoring_chances | 451 | 15 |
| fact_scoring_chances_detailed | 247 | 140 |
| fact_sequences | 521 | 38 |
| fact_shift_players | 4,613 | 86 |
| fact_shift_quality | 4,609 | 9 |
| fact_shift_quality_logical | 107 | 19 |
| fact_shifts | 399 | 137 |
| fact_shot_danger | 451 | 11 |
| fact_shot_xy | 0 | 12 |
| fact_special_teams_summary | 107 | 9 |
| fact_team_game_stats | 8 | 39 |
| fact_team_zone_time | 8 | 8 |
| fact_tracking | 5,823 | 22 |
| fact_turnovers_detailed | 744 | 141 |
| fact_video | 0 | 8 |
| fact_wowy | 621 | 20 |
| fact_zone_entries | 495 | 142 |
| fact_zone_entry_summary | 102 | 9 |
| fact_zone_exit_summary | 102 | 9 |
| fact_zone_exits | 476 | 142 |

**Fact Tables:** 58

## Other Tables

| Table | Rows | Columns |
|-------|------|--------|
| lookup_player_game_rating | 107 | 6 |

**Other Tables:** 1

**Total Rows:** 89,120
