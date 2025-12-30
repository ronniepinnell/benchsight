# FK Population Summary Report
Generated: 2025-12-29 17:58

## Dimension Tables with Mapping Support

| Dimension | Primary Key | Mapping Columns | Notes |
|-----------|-------------|-----------------|-------|
| dim_success | success_id | success_code, potential_values | s,S,1 → Successful |
| dim_shift_start_type | shift_start_type_id | code, name, old_equiv | OtherFaceoff, GameStart, etc |
| dim_shift_stop_type | shift_stop_type_id | code, name, old_equiv | Home Goal, Away Icing, etc |
| dim_player_role | role_id | code, name, potential_values | event_team_player_X mappings |
| dim_event_type | event_type_id | code, name | Shot, Pass, Goal, etc |
| dim_event_detail | event_detail_id | code, name | Shot_OnNet, Pass_Complete, etc |
| dim_zone | zone_id | code, name, abbrev | O, D, N |
| dim_period | period_id | number, name | 1, 2, 3, OT |
| dim_venue | venue_id | code, name | home, away |
| dim_strength | strength_id | code, name | 5v5, 5v4, 4v5, etc |
| dim_situation | situation_id | code, name | Full Strength, PP, PK, EN |
| dim_position | position_id | code, name | F, D, G |
| dim_team | team_id | team_name, norad_team | All NORAD teams |

## FK Fill Rate Summary by Table


### fact_draft (160 rows)
| FK Column | Fill Rate |
|-----------|----------|
| player_draft_id | 100.0% ✓ |
| season_id | 100.0% ✓ |
| team_id | 100.0% ✓ |

### fact_event_chains (295 rows)
| FK Column | Fill Rate |
|-----------|----------|
| chain_id | 100.0% ✓ |
| sequence_id | 0.7%  |
| shot_result_type_id | 0.0%  |
| zone_entry_type_id | 72.2% ~ |
| zone_id | 50.8% ~ |

### fact_events (5,833 rows)
| FK Column | Fill Rate |
|-----------|----------|
| away_team_id | 99.9% ✓ |
| event_detail_2_id | 47.8%  |
| event_detail_id | 80.7% ~ |
| event_type_id | 99.8% ✓ |
| home_team_id | 99.9% ✓ |
| period_id | 100.0% ✓ |
| play_detail_2_id | 2.3%  |
| play_detail_id | 24.2%  |
| play_detail_success_id | 21.5%  |
| success_id | 18.8%  |
| venue_id | 99.6% ✓ |
| zone_id | 38.3%  |

### fact_events_long (11,136 rows)
| FK Column | Fill Rate |
|-----------|----------|
| event_detail_2_id | 53.0% ~ |
| event_detail_id | 85.5% ~ |
| event_type_id | 99.8% ✓ |
| period_id | 100.0% ✓ |
| play_detail_2_id | 1.7%  |
| play_detail_id | 20.8%  |
| play_detail_success_id | 15.3%  |
| role_id | 100.0% ✓ |
| success_id | 20.7%  |
| venue_id | 99.9% ✓ |

### fact_events_player (11,635 rows)
| FK Column | Fill Rate |
|-----------|----------|
| away_team_id | 96.1% ✓ |
| event_detail_2_id | 50.8% ~ |
| event_detail_id | 82.1% ~ |
| event_type_id | 95.9% ✓ |
| home_team_id | 96.1% ✓ |
| period_id | 96.1% ✓ |
| play_detail_2_id | 1.7%  |
| play_detail_id | 20.0%  |
| play_detail_success_id | 14.6%  |
| role_id | 95.9% ✓ |
| success_id | 19.8%  |
| venue_id | 95.8% ✓ |
| zone_id | 38.5%  |

### fact_gameroster (14,471 rows)
| FK Column | Fill Rate |
|-----------|----------|
| opp_team_game_id | 100.0% ✓ |
| opp_team_id | 100.0% ✓ |
| player_game_id | 100.0% ✓ |
| position_id | 100.0% ✓ |
| season_id | 90.7% ✓ |
| team_game_id | 100.0% ✓ |
| team_id | 100.0% ✓ |
| venue_id | 100.0% ✓ |

### fact_goalie_game_stats (4 rows)
| FK Column | Fill Rate |
|-----------|----------|
| away_team_id | 100.0% ✓ |
| home_team_id | 100.0% ✓ |

### fact_h2h (684 rows)
| FK Column | Fill Rate |
|-----------|----------|
| away_team_id | 100.0% ✓ |
| home_team_id | 100.0% ✓ |
| player_1_id | 100.0% ✓ |
| player_2_id | 100.0% ✓ |

### fact_head_to_head (572 rows)
| FK Column | Fill Rate |
|-----------|----------|
| away_team_id | 100.0% ✓ |
| home_team_id | 100.0% ✓ |
| player_1_id | 100.0% ✓ |
| player_2_id | 100.0% ✓ |

### fact_leadership (28 rows)
| FK Column | Fill Rate |
|-----------|----------|
| season_id | 100.0% ✓ |
| team_id | 100.0% ✓ |

### fact_league_leaders_snapshot (14,473 rows)
| FK Column | Fill Rate |
|-----------|----------|
| team_id | 100.0% ✓ |

### fact_line_combos (332 rows)
| FK Column | Fill Rate |
|-----------|----------|
| away_team_id | 100.0% ✓ |
| home_team_id | 100.0% ✓ |
| venue_id | 100.0% ✓ |

### fact_linked_events (473 rows)
| FK Column | Fill Rate |
|-----------|----------|
| event_1_player_id | 100.0% ✓ |
| event_2_player_id | 100.0% ✓ |
| event_3_player_id | 40.0%  |
| event_4_player_id | 12.5%  |
| event_5_player_id | 0.6%  |
| team_id | 100.0% ✓ |
| venue_id | 99.8% ✓ |

### fact_player_boxscore_all (14,473 rows)
| FK Column | Fill Rate |
|-----------|----------|
| opp_team_id | 100.0% ✓ |
| position_id | 100.0% ✓ |
| season_id | 90.7% ✓ |
| team_id | 100.0% ✓ |
| venue_id | 100.0% ✓ |

### fact_player_event_chains (5,831 rows)
| FK Column | Fill Rate |
|-----------|----------|
| event_type_id | 99.8% ✓ |
| period_id | 100.0% ✓ |

### fact_player_game_stats (107 rows)
| FK Column | Fill Rate |
|-----------|----------|
| away_team_id | 100.0% ✓ |
| home_team_id | 100.0% ✓ |

### fact_player_pair_stats (475 rows)
| FK Column | Fill Rate |
|-----------|----------|
| player_1_id | 100.0% ✓ |
| player_2_id | 100.0% ✓ |

### fact_playergames (3,010 rows)
| FK Column | Fill Rate |
|-----------|----------|
| player_game_id | 100.0% ✓ |

### fact_plays (2,714 rows)
| FK Column | Fill Rate |
|-----------|----------|
| play_id | 100.0% ✓ |
| sequence_id | 100.0% ✓ |
| team_id | 100.0% ✓ |
| zone_id | 46.2%  |

### fact_possession_time (107 rows)
| FK Column | Fill Rate |
|-----------|----------|
| team_id | 100.0% ✓ |
| venue_id | 100.0% ✓ |

### fact_registration (190 rows)
| FK Column | Fill Rate |
|-----------|----------|
| drafted_team_id | 100.0% ✓ |
| player_season_registration_id | 100.0% ✓ |
| position_id | 100.0% ✓ |
| season_id | 100.0% ✓ |

### fact_rush_events (199 rows)
| FK Column | Fill Rate |
|-----------|----------|
| zone_entry_type_id | 72.4% ~ |

### fact_sequences (1,088 rows)
| FK Column | Fill Rate |
|-----------|----------|
| end_zone_id | 47.6%  |
| sequence_id | 100.0% ✓ |
| start_zone_id | 47.6%  |
| team_id | 100.0% ✓ |

### fact_shifts (672 rows)
| FK Column | Fill Rate |
|-----------|----------|
| away_team_id | 60.1% ~ |
| home_team_id | 59.7% ~ |
| shift_start_type_id | 25.4%  |
| shift_stop_type_id | 24.4%  |
| situation_id | 58.9% ~ |
| strength_id | 59.1% ~ |

### fact_shifts_long (4,336 rows)
| FK Column | Fill Rate |
|-----------|----------|
| period_id | 100.0% ✓ |
| situation_id | 80.6% ~ |
| slot_id | 100.0% ✓ |
| strength_id | 80.7% ~ |
| venue_id | 100.0% ✓ |

### fact_shifts_player (4,626 rows)
| FK Column | Fill Rate |
|-----------|----------|
| period_id | 100.0% ✓ |
| situation_id | 100.0% ✓ |
| slot_id | 100.0% ✓ |
| strength_id | 100.0% ✓ |
| venue_id | 100.0% ✓ |

### fact_team_game_stats (8 rows)
| FK Column | Fill Rate |
|-----------|----------|
| away_team_id | 100.0% ✓ |
| home_team_id | 100.0% ✓ |
| team_id | 0.0%  |
| venue_id | 100.0% ✓ |

### fact_team_standings_snapshot (1,124 rows)
| FK Column | Fill Rate |
|-----------|----------|
| team_id | 100.0% ✓ |

### fact_team_zone_time (8 rows)
| FK Column | Fill Rate |
|-----------|----------|
| venue_id | 100.0% ✓ |

### fact_wowy (641 rows)
| FK Column | Fill Rate |
|-----------|----------|
| away_team_id | 100.0% ✓ |
| home_team_id | 100.0% ✓ |
| player_1_id | 100.0% ✓ |
| player_2_id | 100.0% ✓ |
| venue_id | 100.0% ✓ |

## Legend
- ✓ = Excellent (>90%)
- ~ = Good (50-90%)
- (blank) = Limited by source data (<50%)

## Notes
Low fill rates (<50%) typically indicate missing data in source tracking files, not ETL bugs.
The zone_id fill rate varies significantly by game (18969: 87%, others: 0-41%).
