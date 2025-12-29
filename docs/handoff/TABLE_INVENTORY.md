# Table Inventory

## Dimension Tables

| Table | Rows | Columns | Primary Key |
|-------|------|---------|-------------|
| dim_comparison_type | 6 | 5 | comparison_type_id |
| dim_event_detail | 59 | 3 | event_detail_id |
| dim_event_detail_2 | 97 | 6 | event_detail_2_id |
| dim_event_type | 20 | 3 | event_type_id |
| dim_giveaway_type | 12 | 8 | giveaway_type_id |
| dim_league | 2 | 2 | league_id |
| dim_net_location | 10 | 5 | net_location_id |
| dim_pass_type | 16 | 8 | pass_type_id |
| dim_period | 5 | 7 | period_id |
| dim_play_detail | 154 | 6 | play_detail_id |
| dim_play_detail_2 | 62 | 5 | play_detail_2_id |
| dim_player | 337 | 28 | index |
| dim_player_role | 14 | 5 | role_id |
| dim_playerurlref | 548 | 3 | n_player_url |
| dim_position | 7 | 4 | position_id |
| dim_randomnames | 486 | 5 | random_full_name |
| dim_rink_coord | 19 | 7 | rink_coord_id |
| dim_rinkboxcoord | 50 | 12 | box_id |
| dim_rinkcoordzones | 198 | 14 | box_id |
| dim_schedule | 562 | 44 | game_id |
| dim_season | 9 | 9 | index |
| dim_shift_slot | 7 | 3 | slot_id |
| dim_shift_start_type | 5 | 6 | shift_start_type_id |
| dim_shift_stop_type | 8 | 6 | shift_stop_type_id |
| dim_shot_type | 14 | 10 | shot_type_id |
| dim_situation | 5 | 3 | situation_id |
| dim_stat | 83 | 12 | stat_id |
| dim_stat_type | 57 | 6 | stat_id |
| dim_stoppage_type | 10 | 5 | stoppage_type_id |
| dim_strength | 17 | 7 | strength_id |
| dim_success | 6 | 3 | success_id |
| dim_takeaway_type | 10 | 8 | takeaway_type_id |
| dim_team | 26 | 15 | index |
| dim_terminology_mapping | 84 | 4 | dimension |
| dim_turnover_quality | 3 | 5 | turnover_quality_id |
| dim_turnover_type | 21 | 9 | turnover_type_id |
| dim_venue | 2 | 4 | venue_id |
| dim_zone | 3 | 4 | zone_id |
| dim_zone_entry_type | 11 | 9 | zone_entry_type_id |
| dim_zone_exit_type | 10 | 8 | zone_exit_type_id |

## Fact Tables

| Table | Rows | Columns | Primary Key |
|-------|------|---------|-------------|
| fact_cycle_events | 9 | 14 | game_id |
| fact_draft | 160 | 14 | team_id |
| fact_event_chains | 295 | 11 | chain_id |
| fact_events | 5,833 | 40 | event_key |
| fact_events_long | 11,136 | 21 | event_player_key |
| fact_events_player | 11,635 | 60 | event_player_key |
| fact_gameroster | 14,471 | 26 | game_id |
| fact_goalie_game_stats | 8 | 18 | goalie_game_key |
| fact_h2h | 684 | 13 | game_id |
| fact_head_to_head | 572 | 14 | game_id |
| fact_leadership | 28 | 9 | player_full_name |
| fact_league_leaders_snapshot | 14,473 | 12 | game_id |
| fact_line_combos | 332 | 8 | game_id |
| fact_linked_events | 473 | 36 | linked_event_key |
| fact_player_boxscore_all | 14,473 | 19 | game_id |
| fact_player_event_chains | 5,831 | 18 | event_chain_key |
| fact_player_game_stats | 107 | 67 | player_game_key |
| fact_player_pair_stats | 475 | 10 | game_id |
| fact_player_xy_long | 0 | 15 | player_xy_key |
| fact_player_xy_wide | 0 | 49 | player_xy_key |
| fact_playergames | 3,010 | 20 | ID |
| fact_plays | 2,714 | 23 | play_id |
| fact_possession_time | 107 | 12 | possession_key |
| fact_puck_xy_long | 0 | 12 | puck_xy_key |
| fact_puck_xy_wide | 0 | 55 | puck_xy_key |
| fact_registration | 190 | 18 | player_full_name |
| fact_rush_events | 199 | 18 | game_id |
| fact_sequences | 1,088 | 24 | sequence_id |
| fact_shifts | 672 | 56 | shift_key |
| fact_shifts_long | 4,336 | 22 | shift_player_key |
| fact_shifts_player | 4,626 | 37 | shift_player_key |
| fact_shot_xy | 0 | 28 | shot_xy_key |
| fact_team_game_stats | 8 | 18 | team_game_key |
| fact_team_standings_snapshot | 1,124 | 13 | game_id |
| fact_team_zone_time | 8 | 10 | zone_time_key |
| fact_video | 10 | 15 | video_key |
| fact_wowy | 641 | 19 | game_id |
