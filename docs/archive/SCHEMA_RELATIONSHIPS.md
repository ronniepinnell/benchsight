# BenchSight Schema Relationships

## Primary Key → Foreign Key Mappings

### Core Entity Relationships

| Parent Table | PK | Child Table | FK |
|--------------|-------|-------------|-------|
| dim_player | player_id | fact_player_game_stats | player_id |
| dim_player | player_id | fact_events_player | player_id |
| dim_player | player_id | fact_shifts | player_id |
| dim_player | player_id | fact_shifts_player | player_id |
| dim_player | player_id | fact_h2h | player_1_id, player_2_id |
| dim_player | player_id | fact_wowy | player_1_id, player_2_id |
| dim_player | player_id | fact_goalie_game_stats | player_id |
| dim_player | player_id | fact_shot_xy | player_id |
| dim_team | team_id | dim_player | team_id |
| dim_team | team_id | fact_team_game_stats | team_id |
| dim_team | team_id | fact_player_game_stats | team_id |
| dim_team | team_id | fact_line_combos | team_id |
| dim_venue | venue_id | fact_events | venue_id |
| dim_venue | venue_id | fact_player_game_stats | venue_id |
| dim_period | period_id | fact_events | period_id |
| dim_period | period_id | fact_player_period_stats | period_id |
| dim_zone | zone_id | fact_events | event_team_zone |
| dim_event_type | event_type_id | fact_events | event_type |
| dim_event_detail | event_detail_id | fact_events | event_detail |
| dim_strength | strength_id | fact_events | strength_id |
| dim_position | position_id | dim_player | position_id |
| dim_season | season_id | dim_schedule | season_id |
| dim_rink_coord | rink_coord_id | fact_shot_xy | shot_rink_coord_id |

### XY Coordinate Relationships

| Dimension | Purpose | Columns Used |
|-----------|---------|--------------|
| dim_rink_coord | 12 simple zones | x_min, x_max, y_min, y_max |
| dim_rinkcoordzones | 84 detailed zones with danger | x_min, x_max, y_min, y_max, danger |
| dim_rinkboxcoord | 24 box zones | x_min, x_max, y_min, y_max, danger |

### Usage Pattern for XY → Danger Zone:
```sql
SELECT e.*, z.danger, z.zone, z.side
FROM fact_shot_xy e
JOIN dim_rinkcoordzones z
  ON e.shot_x BETWEEN z.x_min AND z.x_max
 AND e.shot_y BETWEEN z.y_min AND z.y_max
```

---

## Table Categories

### Dimension Tables (44)

| Category | Tables | Purpose |
|----------|--------|---------|
| **Core Entities** | dim_player, dim_team, dim_venue, dim_season | Main business entities |
| **Event Classification** | dim_event_type, dim_event_detail, dim_event_detail_2 | Event categorization |
| **Play Details** | dim_play_detail, dim_play_detail_2 | Play-level categorization |
| **Locations** | dim_zone, dim_rink_coord, dim_rinkcoordzones, dim_rinkboxcoord | Rink geography |
| **Game State** | dim_period, dim_strength, dim_situation | Context dimensions |
| **Actions** | dim_shot_type, dim_pass_type, dim_turnover_type | Action classification |
| **Reference** | dim_stat, dim_stat_type, dim_stat_category | Stats metadata |

### Fact Tables (44)

| Category | Tables | Purpose |
|----------|--------|---------|
| **Core Stats** | fact_player_game_stats, fact_team_game_stats, fact_goalie_game_stats | Box scores |
| **Events** | fact_events, fact_events_player, fact_events_long | Play-by-play |
| **Shifts** | fact_shifts, fact_shifts_player, fact_shifts_long | Ice time tracking |
| **Pairings** | fact_h2h, fact_wowy, fact_line_combos, fact_player_pair_stats | Player combinations |
| **XY Data** | fact_shot_xy, fact_player_xy_wide, fact_player_xy_long, fact_puck_xy_wide | Coordinates |
| **Sequences** | fact_sequences, fact_plays, fact_event_chains, fact_linked_events | Event chains |
| **Advanced** | fact_possession_time, fact_scoring_chances, fact_shot_danger | Analytics |

---

## FK Population Status

| Table | FK Columns | Fill Rate |
|-------|------------|-----------|
| fact_player_game_stats | 5 | 100% |
| fact_events_player | 3 | 95% |
| fact_shifts_player | 2 | 100% |
| fact_h2h | 4 | 100% |
| fact_wowy | 4 | 100% |
| fact_line_combos | 3 | 85% |
| fact_shot_xy | 3 | 0% (no XY data yet) |

---

## Cardinality Summary

| Relationship | Type | Description |
|--------------|------|-------------|
| player → player_game_stats | 1:N | One player, many games |
| team → player | 1:N | One team, many players |
| game → events | 1:N | One game, many events |
| event → events_player | 1:N | One event, up to 10 players |
| player_1 → h2h → player_2 | N:M | Many-to-many pairings |
| rink_zone → shot_xy | 1:N | One zone, many shots |
