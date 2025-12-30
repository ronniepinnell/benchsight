# Complete Table Reference (98 Tables)

## Summary

| Category | Count | Description |
|----------|-------|-------------|
| Dimensions | 44 | Reference/lookup tables |
| Facts | 51 | Transactional/metric tables |
| QA | 1 | Quality assurance |
| Video | 2 | Video highlights (NEW) |
| **Total** | **98** | |

---

## Dimensions (44 Tables)

### Core Entities
| Table | PK | Rows | Description |
|-------|-----|------|-------------|
| `dim_player` | player_id | 337 | Player master data |
| `dim_team` | team_id | 26 | Team master data |
| `dim_schedule` | game_id | 562 | Game schedule |
| `dim_season` | season_id | varies | Season definitions |
| `dim_league` | league_id | varies | League info |
| `dim_venue` | venue_id | varies | Venue info |

### Event Classification
| Table | PK | Description |
|-------|-----|-------------|
| `dim_event_type` | event_type_id | Event types (Shot, Pass, Goal, etc.) |
| `dim_event_detail` | event_detail_id | Event details (Wrist Shot, etc.) |
| `dim_event_detail_2` | event_detail_2_id | Secondary details |
| `dim_play_detail` | play_detail_id | Play details |
| `dim_play_detail_2` | play_detail_2_id | Secondary play details |

### Player/Position
| Table | PK | Description |
|-------|-----|-------------|
| `dim_position` | position_id | Positions (C, LW, RW, D, G) |
| `dim_player_role` | player_role_id | Player roles |
| `dim_shift_slot` | shift_slot_id | Shift slots |

### Stats Metadata
| Table | PK | Description |
|-------|-----|-------------|
| `dim_stat` | stat_id | Stat definitions |
| `dim_stat_type` | stat_type_id | Stat types |
| `dim_stat_category` | stat_category_id | Stat categories |
| `dim_micro_stat` | micro_stat_id | Micro stat definitions |

### Zones/Coordinates
| Table | PK | Description |
|-------|-----|-------------|
| `dim_zone` | zone_id | Zones (DZ, NZ, OZ) |
| `dim_danger_zone` | danger_zone_id | Danger zones |
| `dim_rink_coord` | coord_id | Rink coordinates |
| `dim_rinkboxcoord` | box_id | Rink box coordinates |
| `dim_rinkcoordzones` | zone_coord_id | Coordinate zones |

### Action Types
| Table | PK | Description |
|-------|-----|-------------|
| `dim_shot_type` | shot_type_id | Shot types |
| `dim_pass_type` | pass_type_id | Pass types |
| `dim_giveaway_type` | giveaway_type_id | Giveaway types |
| `dim_takeaway_type` | takeaway_type_id | Takeaway types |
| `dim_turnover_type` | turnover_type_id | Turnover types |
| `dim_turnover_quality` | turnover_quality_id | Turnover quality |

### Shift Types
| Table | PK | Description |
|-------|-----|-------------|
| `dim_shift_start_type` | start_type_id | How shifts start |
| `dim_shift_stop_type` | stop_type_id | How shifts end |

### Zone Transitions
| Table | PK | Description |
|-------|-----|-------------|
| `dim_zone_entry_type` | entry_type_id | Zone entry types |
| `dim_zone_exit_type` | exit_type_id | Zone exit types |

### Game State
| Table | PK | Description |
|-------|-----|-------------|
| `dim_period` | period_id | Periods (1, 2, 3, OT, SO) |
| `dim_strength` | strength_id | Game strength (EV, PP, PK) |
| `dim_situation` | situation_id | Game situations |
| `dim_success` | success_id | Success codes (s, u) |
| `dim_net_location` | net_location_id | Net locations |
| `dim_stoppage_type` | stoppage_type_id | Stoppage types |

### Reference/Mapping
| Table | PK | Description |
|-------|-----|-------------|
| `dim_comparison_type` | comparison_type_id | Comparison types |
| `dim_composite_rating` | rating_id | Rating definitions |
| `dim_terminology_mapping` | mapping_id | Term mappings |
| `dim_playerurlref` | player_id | Player URL references |
| `dim_randomnames` | id | Random names |

### Video (NEW)
| Table | PK | Description |
|-------|-----|-------------|
| `dim_highlight_type` | highlight_type_id | Highlight types (goal, save, hit, etc.) |

---

## Facts (51 Tables)

### Core Events
| Table | PK | Columns | Description |
|-------|-----|---------|-------------|
| `fact_events` | event_key | 50+ | Main event table (wide format) |
| `fact_events_long` | event_long_key | 20+ | Events in long format |
| `fact_events_player` | event_player_key | 15+ | Player-event associations |
| `fact_events_tracking` | tracking_key | 20+ | Event tracking details |

### Core Shifts
| Table | PK | Description |
|-------|-----|-------------|
| `fact_shifts` | shift_key | Main shift table |
| `fact_shifts_long` | shift_long_key | Shifts in long format |
| `fact_shifts_player` | shift_player_key | Player-shift associations |
| `fact_shifts_tracking` | shift_tracking_key | Shift tracking |

### Player Stats
| Table | PK | Columns | Description |
|-------|-----|---------|-------------|
| `fact_player_game_stats` | player_game_key | **317** | Main player stats |
| `fact_player_period_stats` | player_period_key | 100+ | Per-period stats |
| `fact_player_stats_long` | stat_long_key | 10+ | Stats in long format |
| `fact_player_micro_stats` | micro_stat_key | 70+ | Micro statistics |
| `fact_player_boxscore_all` | boxscore_key | 50+ | Boxscore data |
| `fact_player_game_position` | position_key | 15+ | Position by game |
| `fact_playergames` | playergame_key | 20+ | Player-game bridge |

### Team Stats
| Table | PK | Description |
|-------|-----|-------------|
| `fact_team_game_stats` | team_game_key | Team-level stats |

### Goalie Stats
| Table | PK | Description |
|-------|-----|-------------|
| `fact_goalie_game_stats` | goalie_game_key | Goalie statistics |

### Analytics - Matchups
| Table | PK | Description |
|-------|-----|-------------|
| `fact_h2h` | h2h_key | Head-to-head (opponents) |
| `fact_wowy` | wowy_key | With-or-without-you (teammates) |
| `fact_head_to_head` | matchup_key | Matchup summary |
| `fact_line_combos` | combo_key | Line combinations |
| `fact_matchup_summary` | summary_key | Matchup aggregates |
| `fact_player_pair_stats` | pair_key | Player pair stats |

### Analytics - Shifts
| Table | PK | Description |
|-------|-----|-------------|
| `fact_shift_quality` | quality_key | Shift quality metrics |
| `fact_shift_quality_logical` | logical_quality_key | Logical shift quality |
| `fact_shift_players` | shift_players_key | Players per shift |

### Analytics - Zones
| Table | PK | Description |
|-------|-----|-------------|
| `fact_cycle_events` | cycle_key | Cycle plays |
| `fact_rush_events` | rush_key | Rush plays |
| `fact_possession_time` | possession_key | Zone possession |
| `fact_team_zone_time` | zone_time_key | Team zone time |
| `fact_scoring_chances` | chance_key | Scoring chances |
| `fact_shot_danger` | shot_danger_key | Shot danger |

### XY Tracking
| Table | PK | Description |
|-------|-----|-------------|
| `fact_player_xy_long` | xy_long_key | Player XY (long) |
| `fact_player_xy_wide` | xy_wide_key | Player XY (wide) |
| `fact_puck_xy_long` | puck_xy_key | Puck XY (long) |
| `fact_puck_xy_wide` | puck_wide_key | Puck XY (wide) |
| `fact_shot_xy` | shot_xy_key | Shot locations |

### Event Chains
| Table | PK | Description |
|-------|-----|-------------|
| `fact_linked_events` | link_key | Linked events |
| `fact_event_chains` | chain_key | Event chains |
| `fact_player_event_chains` | player_chain_key | Player chains |

### Other
| Table | PK | Description |
|-------|-----|-------------|
| `fact_plays` | play_key | Play sequences |
| `fact_sequences` | sequence_key | Sequences |
| `fact_video` | video_key | Video references |
| `fact_draft` | draft_key | Draft data |
| `fact_registration` | registration_key | Registrations |
| `fact_leadership` | leadership_key | Leadership |
| `fact_gameroster` | roster_key | Game rosters |

### Snapshots
| Table | PK | Description |
|-------|-----|-------------|
| `fact_league_leaders_snapshot` | leader_key | Leaderboards |
| `fact_team_standings_snapshot` | standing_key | Standings |
| `fact_game_status` | game_id | Game processing status |
| `fact_suspicious_stats` | suspicious_key | Suspicious stats |

### Video (NEW)
| Table | PK | Description |
|-------|-----|-------------|
| `fact_video_highlights` | highlight_key | Video clips |

---

## QA Tables (1)

| Table | PK | Description |
|-------|-----|-------------|
| `qa_suspicious_stats` | qa_key | Data quality tracking |

---

## Primary Key Formats

| Pattern | Example | Used By |
|---------|---------|---------|
| `{game_id}_{index}` | `18969_1` | fact_events |
| `{game_id}_{player_id}_{index}` | `18969_123_1` | fact_shifts |
| `{game_id}_{player_id}` | `18969_123` | fact_player_game_stats |
| `{game_id}_{team_id}` | `18969_5` | fact_team_game_stats |
| Single integer | `123` | Most dimension tables |
