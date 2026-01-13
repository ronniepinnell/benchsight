# BenchSight Data Dictionary (Full)

**Auto-generated:** 2026-01-10 02:41
**Tables:** 131
**Version:** 21.4

---

## Quick Links

### Core Tables
- [fact_events](#fact_events)
- [fact_gameroster](#fact_gameroster)
- [fact_player_season_stats](#fact_player_season_stats)
- [dim_player](#dim_player)
- [dim_team](#dim_team)
- [dim_game](#dim_game)

---

## Column Type Legend

| Type | Meaning | Example |
|------|---------|---------|
| **Explicit** | Direct from raw/source data | event_type, period |
| **Calculated** | Formula-based derivation | points = goals + assists |
| **Derived** | Generated keys/aggregates | player_game_key |
| **FK** | Foreign key lookup | player_id → dim_player |
| **Unknown** | Needs investigation | - |

---

## Critical Business Rules

### Goal Counting (CANONICAL)
```sql
-- THE ONLY WAY TO COUNT GOALS:
WHERE event_type = 'Goal' AND event_detail = 'Goal_Scored'

-- Shot_Goal is the SHOT, not the goal!
```

### Player Attribution
```
event_player_1 = Primary player (scorer, shooter)
event_player_2 = Primary assist / secondary player
event_player_3 = Secondary assist
```

---


## dim_assist_type

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 5 |
| **Columns** | 5 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| assist_type_id | object | - |  |  | Unknown | 5 | 0.0% | No |
| assist_type_code | object | - |  |  | Unknown | 5 | 0.0% | No |
| assist_type_name | object | - |  |  | Unknown | 5 | 0.0% | No |
| points_value | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| description | object | - |  |  | Unknown | 5 | 0.0% | No |

---

## dim_comparison_type

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 6 |
| **Columns** | 5 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| comparison_type_id | object | - |  |  | Unknown | 6 | 0.0% | No |
| comparison_type_code | object | - |  |  | Unknown | 6 | 0.0% | No |
| comparison_type_name | object | - |  |  | Unknown | 6 | 0.0% | No |
| description | object | - |  |  | Unknown | 6 | 0.0% | No |
| analysis_scope | object | - |  |  | Unknown | 6 | 0.0% | No |

---

## dim_competition_tier

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 4 |
| **Columns** | 4 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| competition_tier_id | object | - |  |  | Unknown | 4 | 0.0% | No |
| tier_name | object | - |  |  | Unknown | 4 | 0.0% | No |
| min_rating | float64 | - |  |  | Unknown | 4 | 0.0% | No |
| max_rating | float64 | - |  |  | Unknown | 4 | 0.0% | No |

---

## dim_composite_rating

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 8 |
| **Columns** | 6 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| rating_id | object | - |  |  | Unknown | 8 | 0.0% | No |
| rating_code | object | - |  |  | Unknown | 8 | 0.0% | No |
| rating_name | object | - |  |  | Unknown | 8 | 0.0% | No |
| description | object | - |  |  | Unknown | 8 | 0.0% | No |
| scale_min | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| scale_max | int64 | - |  |  | Unknown | 8 | 0.0% | No |

---

## dim_danger_level

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 3 |
| **Columns** | 4 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| danger_level_id | object | - |  |  | Unknown | 3 | 0.0% | No |
| danger_level_code | object | - |  |  | Unknown | 3 | 0.0% | No |
| danger_level_name | object | - |  |  | Unknown | 3 | 0.0% | No |
| xg_multiplier | float64 | - |  |  | Unknown | 3 | 0.0% | No |

---

## dim_danger_zone

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 4 |
| **Columns** | 5 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| danger_zone_id | object | - |  |  | Unknown | 4 | 0.0% | No |
| danger_zone_code | object | - |  |  | Unknown | 4 | 0.0% | No |
| danger_zone_name | object | - |  |  | Unknown | 4 | 0.0% | No |
| xg_base | float64 | - |  |  | Unknown | 4 | 0.0% | No |
| description | object | - |  |  | Unknown | 4 | 0.0% | No |

---

## dim_event_detail

| Property | Value |
|----------|-------|
| **Description** | Event detail code reference |
| **Purpose** | Lookup table for event_detail values. |
| **Source Module** | `src/etl/processors/dim_processor.py:create_dim_event_detail()` |
| **Logic** | Distinct event_detail values from fact_events |
| **Grain** | One row per event detail |
| **Rows** | 31 |
| **Columns** | 10 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| event_detail_id | object | - |  |  | Unknown | 31 | 0.0% | No |
| event_detail_code | object | - |  |  | Unknown | 31 | 0.0% | No |
| event_detail_name | object | - |  |  | Unknown | 31 | 0.0% | No |
| event_type | object | Type of event | Values: Shot, Goal, Pass, Faceoff, Hit, etc. |  | Explicit | 31 | 0.0% | No |
| category | object | - |  |  | Unknown | 31 | 0.0% | No |
| is_shot_on_goal | bool | - |  |  | Unknown | 31 | 0.0% | No |
| is_goal | bool | - |  |  | Unknown | 31 | 0.0% | No |
| is_miss | bool | - |  |  | Unknown | 31 | 0.0% | No |
| is_block | bool | - |  |  | Unknown | 31 | 0.0% | No |
| danger_potential | object | - |  |  | Unknown | 10 | 67.7% | No |

---

## dim_event_detail_2

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 102 |
| **Columns** | 4 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| event_detail_2_id | object | - |  |  | Unknown | 102 | 0.0% | No |
| event_detail_2_code | object | - |  |  | Unknown | 102 | 0.0% | No |
| event_detail_2_name | object | - |  |  | Unknown | 102 | 0.0% | No |
| category | object | - |  |  | Unknown | 102 | 0.0% | No |

---

## dim_event_type

| Property | Value |
|----------|-------|
| **Description** | Event type code reference |
| **Purpose** | Lookup table for event_type values. |
| **Source Module** | `src/etl/processors/dim_processor.py:create_dim_event_type()` |
| **Logic** | Distinct event_type values from fact_events |
| **Grain** | One row per event type |
| **Rows** | 12 |
| **Columns** | 7 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| event_type_id | object | - |  |  | Unknown | 12 | 0.0% | No |
| event_type_code | object | - |  |  | Unknown | 12 | 0.0% | No |
| event_type_name | object | - |  |  | Unknown | 12 | 0.0% | No |
| event_category | object | - |  |  | Unknown | 12 | 0.0% | No |
| description | object | - |  |  | Unknown | 12 | 0.0% | No |
| is_corsi | bool | - |  |  | Unknown | 12 | 0.0% | No |
| is_fenwick | bool | - |  |  | Unknown | 12 | 0.0% | No |

---

## dim_game_state

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 6 |
| **Columns** | 6 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| game_state_id | object | - |  |  | Unknown | 6 | 0.0% | No |
| game_state_code | object | - |  |  | Unknown | 6 | 0.0% | No |
| game_state_name | object | - |  |  | Unknown | 6 | 0.0% | No |
| goal_diff_min | int64 | - |  |  | Unknown | 6 | 0.0% | No |
| goal_diff_max | int64 | - |  |  | Unknown | 6 | 0.0% | No |
| description | object | - |  |  | Unknown | 6 | 0.0% | No |

---

## dim_giveaway_type

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 16 |
| **Columns** | 3 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| giveaway_type_id | object | - |  |  | Unknown | 16 | 0.0% | No |
| giveaway_type_code | object | - |  |  | Unknown | 16 | 0.0% | No |
| giveaway_type_name | object | - |  |  | Unknown | 16 | 0.0% | No |

---

## dim_league

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 2 |
| **Columns** | 2 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| league_id | object | - |  |  | Unknown | 2 | 0.0% | No |
| league | object | - |  |  | Unknown | 2 | 0.0% | No |

---

## dim_micro_stat

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 22 |
| **Columns** | 4 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| micro_stat_id | object | - |  |  | Unknown | 22 | 0.0% | No |
| stat_code | object | - |  |  | Unknown | 22 | 0.0% | No |
| stat_name | object | - |  |  | Unknown | 22 | 0.0% | No |
| category | object | - |  |  | Unknown | 22 | 0.0% | No |

---

## dim_net_location

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 10 |
| **Columns** | 5 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| net_location_id | object | - |  |  | Unknown | 10 | 0.0% | No |
| net_location_code | object | - |  |  | Unknown | 10 | 0.0% | No |
| net_location_name | object | - |  |  | Unknown | 10 | 0.0% | No |
| x_pct | float64 | - |  |  | Unknown | 10 | 0.0% | No |
| y_pct | float64 | - |  |  | Unknown | 10 | 0.0% | No |

---

## dim_pass_outcome

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 4 |
| **Columns** | 4 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| pass_outcome_id | object | - |  |  | Unknown | 4 | 0.0% | No |
| pass_outcome_code | object | - |  |  | Unknown | 4 | 0.0% | No |
| pass_outcome_name | object | - |  |  | Unknown | 4 | 0.0% | No |
| is_successful | bool | - |  |  | Unknown | 4 | 0.0% | No |

---

## dim_pass_type

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 8 |
| **Columns** | 4 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| pass_type_id | object | - |  |  | Unknown | 8 | 0.0% | No |
| pass_type_code | object | - |  |  | Unknown | 8 | 0.0% | No |
| pass_type_name | object | - |  |  | Unknown | 8 | 0.0% | No |
| description | object | - |  |  | Unknown | 8 | 0.0% | No |

---

## dim_period

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 5 |
| **Columns** | 5 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| period_id | object | - |  |  | Unknown | 5 | 0.0% | No |
| period_number | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| period_name | object | - |  |  | Unknown | 5 | 0.0% | No |
| period_type | object | - |  |  | Unknown | 5 | 0.0% | No |
| period_minutes | int64 | - |  |  | Unknown | 5 | 0.0% | No |

---

## dim_play_detail

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 133 |
| **Columns** | 6 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| play_detail_id | object | - |  |  | Unknown | 133 | 0.0% | No |
| play_detail_code | object | - |  |  | Unknown | 133 | 0.0% | No |
| play_detail_name | object | - |  |  | Unknown | 133 | 0.0% | No |
| play_category | object | - |  |  | Unknown | 133 | 0.0% | No |
| skill_level | object | - |  |  | Unknown | 133 | 0.0% | No |
| description | object | - |  |  | Unknown | 133 | 0.0% | No |

---

## dim_play_detail_2

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 62 |
| **Columns** | 6 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| play_detail_2_id | object | - |  |  | Unknown | 62 | 0.0% | No |
| play_detail_2_code | object | - |  |  | Unknown | 62 | 0.0% | No |
| play_detail_2_name | object | - |  |  | Unknown | 62 | 0.0% | No |
| play_category | object | - |  |  | Unknown | 62 | 0.0% | No |
| skill_level | object | - |  |  | Unknown | 62 | 0.0% | No |
| description | object | - |  |  | Unknown | 62 | 0.0% | No |

---

## dim_player

| Property | Value |
|----------|-------|
| **Description** | Player master reference data |
| **Purpose** | Central player lookup. All player FKs reference this. |
| **Source Module** | `src/etl/processors/dim_processor.py:create_dim_player()` |
| **Logic** | Deduplicated from registration + roster data |
| **Grain** | One row per unique player |
| **Rows** | 337 |
| **Columns** | 27 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| player_first_name | object | - |  |  | Unknown | 337 | 0.0% | No |
| player_last_name | object | - |  |  | Unknown | 337 | 0.0% | No |
| player_full_name | object | - |  |  | Unknown | 337 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 337 | 0.0% | No |
| player_primary_position | object | - |  |  | Unknown | 337 | 0.0% | No |
| current_skill_rating | int64 | - |  |  | Unknown | 337 | 0.0% | No |
| player_hand | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| birth_year | float64 | - |  |  | Unknown | 190 | 43.6% | No |
| player_gender | object | - |  |  | Unknown | 337 | 0.0% | No |
| highest_beer_league | object | - |  |  | Unknown | 172 | 49.0% | No |
| player_rating_ly | int64 | - |  |  | Unknown | 337 | 0.0% | No |
| player_notes | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_leadership | object | - |  |  | Unknown | 28 | 91.7% | No |
| player_norad | object | - |  |  | Unknown | 337 | 0.0% | No |
| player_csaha | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_norad_primary_number | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_csah_primary_number | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_norad_current_team | object | - |  |  | Unknown | 337 | 0.0% | No |
| player_csah_current_team | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_norad_current_team_id | object | - |  |  | Unknown | 337 | 0.0% | No |
| player_csah_current_team_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| other_url | object | - |  |  | Unknown | 13 | 96.1% | No |
| player_url | object | - |  |  | Unknown | 320 | 5.0% | No |
| player_image | object | - |  |  | Unknown | 337 | 0.0% | No |
| random_player_first_name | object | - |  |  | Unknown | 337 | 0.0% | No |
| random_player_last_name | object | - |  |  | Unknown | 337 | 0.0% | No |
| random_player_full_name | object | - |  |  | Unknown | 337 | 0.0% | No |

---

## dim_player_role

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 14 |
| **Columns** | 5 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| role_id | object | - |  |  | Unknown | 14 | 0.0% | No |
| role_code | object | - |  |  | Unknown | 14 | 0.0% | No |
| role_name | object | - |  |  | Unknown | 14 | 0.0% | No |
| role_type | object | - |  |  | Unknown | 14 | 0.0% | No |
| sort_order | int64 | - |  |  | Unknown | 14 | 0.0% | No |

---

## dim_playerurlref

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 548 |
| **Columns** | 3 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| n_player_url | object | - |  |  | Unknown | 548 | 0.0% | No |
| player_full_name | object | - |  |  | Unknown | 548 | 0.0% | No |
| n_player_id_2 | object | - |  |  | Unknown | 548 | 0.0% | No |

---

## dim_position

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 6 |
| **Columns** | 4 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| position_id | object | - |  |  | Unknown | 6 | 0.0% | No |
| position_code | object | - |  |  | Unknown | 6 | 0.0% | No |
| position_name | object | - |  |  | Unknown | 6 | 0.0% | No |
| position_type | object | - |  |  | Unknown | 6 | 0.0% | No |

---

## dim_randomnames

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 486 |
| **Columns** | 5 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| random_full_name | object | - |  |  | Unknown | 486 | 0.0% | No |
| random_first_name | object | - |  |  | Unknown | 486 | 0.0% | No |
| random_last_name | object | - |  |  | Unknown | 486 | 0.0% | No |
| gender | object | - |  |  | Unknown | 486 | 0.0% | No |
| name_used | object | - |  |  | Unknown | 486 | 0.0% | No |

---

## dim_rating

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 5 |
| **Columns** | 3 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| rating_id | object | - |  |  | Unknown | 5 | 0.0% | No |
| rating_value | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| rating_name | object | - |  |  | Unknown | 5 | 0.0% | No |

---

## dim_rating_matchup

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 5 |
| **Columns** | 4 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| matchup_id | object | - |  |  | Unknown | 5 | 0.0% | No |
| matchup_name | object | - |  |  | Unknown | 5 | 0.0% | No |
| min_diff | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| max_diff | float64 | - |  |  | Unknown | 5 | 0.0% | No |

---

## dim_rink_zone

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 201 |
| **Columns** | 13 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| rink_zone_id | object | - |  |  | Unknown | 201 | 0.0% | No |
| zone_code | object | - |  |  | Unknown | 201 | 0.0% | No |
| zone_name | object | - |  |  | Unknown | 201 | 0.0% | No |
| granularity | object | - |  |  | Unknown | 201 | 0.0% | No |
| x_min | int64 | - |  |  | Unknown | 201 | 0.0% | No |
| x_max | int64 | - |  |  | Unknown | 201 | 0.0% | No |
| y_min | float64 | - |  |  | Unknown | 201 | 0.0% | No |
| y_max | float64 | - |  |  | Unknown | 201 | 0.0% | No |
| zone | object | - |  |  | Unknown | 201 | 0.0% | No |
| danger | object | - |  |  | Unknown | 201 | 0.0% | No |
| side | object | - |  |  | Unknown | 201 | 0.0% | No |
| x_description | object | - |  |  | Unknown | 192 | 4.5% | No |
| y_description | object | - |  |  | Unknown | 192 | 4.5% | No |

---

## dim_save_outcome

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 3 |
| **Columns** | 4 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| save_outcome_id | object | - |  |  | Unknown | 3 | 0.0% | No |
| save_outcome_code | object | - |  |  | Unknown | 3 | 0.0% | No |
| save_outcome_name | object | - |  |  | Unknown | 3 | 0.0% | No |
| causes_stoppage | bool | - |  |  | Unknown | 3 | 0.0% | No |

---

## dim_schedule

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 563 |
| **Columns** | 44 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 563 | 0.0% | No |
| season | float64 | - |  |  | Unknown | 562 | 0.2% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 562 | 0.2% | No |
| game_url | object | - |  |  | Unknown | 563 | 0.0% | No |
| home_team_game_id | object | - |  |  | Unknown | 562 | 0.2% | No |
| away_team_game_id | object | - |  |  | Unknown | 562 | 0.2% | No |
| date | object | - |  |  | Unknown | 562 | 0.2% | No |
| game_time | object | - |  |  | Unknown | 81 | 85.6% | No |
| home_team_name | object | - |  |  | Unknown | 563 | 0.0% | No |
| away_team_name | object | - |  |  | Unknown | 563 | 0.0% | No |
| home_team_id | object | - |  |  | Unknown | 562 | 0.2% | No |
| away_team_id | object | - |  |  | Unknown | 562 | 0.2% | No |
| head_to_head_id | object | - |  |  | Unknown | 562 | 0.2% | No |
| game_type | object | - |  |  | Unknown | 562 | 0.2% | No |
| playoff_round | object | - |  |  | Unknown | 54 | 90.4% | No |
| last_period_type | object | - |  |  | Unknown | 562 | 0.2% | No |
| period_length | object | - |  |  | Unknown | 562 | 0.2% | No |
| ot_period_length | object | - |  |  | Unknown | 561 | 0.4% | No |
| shootout_rounds | float64 | - |  |  | Unknown | 121 | 78.5% | No |
| home_total_goals | int64 | - |  |  | Unknown | 563 | 0.0% | No |
| away_total_goals | int64 | - |  |  | Unknown | 563 | 0.0% | No |
| home_team_period1_goals | float64 | - |  |  | Unknown | 360 | 36.1% | No |
| home_team_period2_goals | float64 | - |  |  | Unknown | 361 | 35.9% | No |
| home_team_period3_goals | float64 | - |  |  | Unknown | 358 | 36.4% | No |
| home_team_periodOT_goals | float64 | - |  |  | Unknown | 128 | 77.3% | No |
| away_team_period1_goals | float64 | - |  |  | Unknown | 362 | 35.7% | No |
| away_team_period2_goals | float64 | - |  |  | Unknown | 347 | 38.4% | No |
| away_team_period3_goals | float64 | - |  |  | Unknown | 355 | 36.9% | No |
| away_team_periodOT_goals | float64 | - |  |  | Unknown | 127 | 77.4% | No |
| home_team_seeding | float64 | - |  |  | Unknown | 40 | 92.9% | No |
| away_team_seeding | float64 | - |  |  | Unknown | 40 | 92.9% | No |
| home_team_w | float64 | - |  |  | Unknown | 562 | 0.2% | No |
| home_team_l | float64 | - |  |  | Unknown | 562 | 0.2% | No |
| home_team_t | float64 | - |  |  | Unknown | 562 | 0.2% | No |
| home_team_pts | float64 | - |  |  | Unknown | 562 | 0.2% | No |
| away_team_w | float64 | - |  |  | Unknown | 562 | 0.2% | No |
| away_team_l | float64 | - |  |  | Unknown | 562 | 0.2% | No |
| away_team_t | float64 | - |  |  | Unknown | 562 | 0.2% | No |
| away_team_pts | float64 | - |  |  | Unknown | 562 | 0.2% | No |
| video_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| video_start_time | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| video_end_time | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| video_title | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| video_url | float64 | - |  |  | Unknown | 0 | 100.0% | No |

---

## dim_season

| Property | Value |
|----------|-------|
| **Description** | Season definitions |
| **Purpose** | Season lookup and date ranges. |
| **Source Module** | `src/etl/processors/dim_processor.py:create_dim_season()` |
| **Logic** | Extracted from schedule data |
| **Grain** | One row per season |
| **Rows** | 9 |
| **Columns** | 8 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 9 | 0.0% | No |
| season | int64 | - |  |  | Unknown | 9 | 0.0% | No |
| session | object | - |  |  | Unknown | 9 | 0.0% | No |
| norad | object | - |  |  | Unknown | 9 | 0.0% | No |
| csah | object | - |  |  | Unknown | 9 | 0.0% | No |
| league_id | object | - |  |  | Unknown | 9 | 0.0% | No |
| league | object | - |  |  | Unknown | 9 | 0.0% | No |
| start_date | object | - |  |  | Unknown | 9 | 0.0% | No |

---

## dim_shift_duration

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 5 |
| **Columns** | 7 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| shift_duration_id | object | - |  |  | Unknown | 5 | 0.0% | No |
| duration_bucket | object | - |  |  | Unknown | 5 | 0.0% | No |
| min_seconds | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| max_seconds | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| description | object | - |  |  | Unknown | 5 | 0.0% | No |
| fatigue_level | object | - |  |  | Unknown | 5 | 0.0% | No |
| typical_scenario | object | - |  |  | Unknown | 5 | 0.0% | No |

---

## dim_shift_quality_tier

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 5 |
| **Columns** | 6 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| tier_id | object | - |  |  | Unknown | 5 | 0.0% | No |
| tier_code | object | - |  |  | Unknown | 5 | 0.0% | No |
| tier_name | object | - |  |  | Unknown | 5 | 0.0% | No |
| score_min | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| score_max | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| description | object | - |  |  | Unknown | 5 | 0.0% | No |

---

## dim_shift_slot

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 7 |
| **Columns** | 3 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| slot_id | object | - |  |  | Unknown | 7 | 0.0% | No |
| slot_code | object | - |  |  | Unknown | 7 | 0.0% | No |
| slot_name | object | - |  |  | Unknown | 7 | 0.0% | No |

---

## dim_shift_start_type

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 9 |
| **Columns** | 2 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| shift_start_type_id | object | - |  |  | Unknown | 9 | 0.0% | No |
| shift_start_type_name | object | - |  |  | Unknown | 9 | 0.0% | No |

---

## dim_shift_stop_type

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 18 |
| **Columns** | 2 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| shift_stop_type_id | object | - |  |  | Unknown | 18 | 0.0% | No |
| shift_stop_type_name | object | - |  |  | Unknown | 18 | 0.0% | No |

---

## dim_shot_outcome

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 5 |
| **Columns** | 8 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| shot_outcome_id | object | - |  |  | Unknown | 5 | 0.0% | No |
| shot_outcome_code | object | - |  |  | Unknown | 5 | 0.0% | No |
| shot_outcome_name | object | - |  |  | Unknown | 5 | 0.0% | No |
| is_goal | bool | - |  |  | Unknown | 5 | 0.0% | No |
| is_save | bool | - |  |  | Unknown | 5 | 0.0% | No |
| is_block | bool | - |  |  | Unknown | 5 | 0.0% | No |
| is_miss | bool | - |  |  | Unknown | 5 | 0.0% | No |
| xg_multiplier | float64 | - |  |  | Unknown | 5 | 0.0% | No |

---

## dim_shot_type

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 6 |
| **Columns** | 4 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| shot_type_id | object | - |  |  | Unknown | 6 | 0.0% | No |
| shot_type_code | object | - |  |  | Unknown | 6 | 0.0% | No |
| shot_type_name | object | - |  |  | Unknown | 6 | 0.0% | No |
| description | object | - |  |  | Unknown | 6 | 0.0% | No |

---

## dim_situation

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 4 |
| **Columns** | 2 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| situation_id | object | - |  |  | Unknown | 4 | 0.0% | No |
| situation_name | object | - |  |  | Unknown | 4 | 0.0% | No |

---

## dim_stat

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 39 |
| **Columns** | 12 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| stat_id | object | - |  |  | Unknown | 39 | 0.0% | No |
| stat_code | object | - |  |  | Unknown | 39 | 0.0% | No |
| stat_name | object | - |  |  | Unknown | 39 | 0.0% | No |
| category | object | - |  |  | Unknown | 39 | 0.0% | No |
| description | object | - |  |  | Unknown | 39 | 0.0% | No |
| formula | object | - |  |  | Unknown | 39 | 0.0% | No |
| player_role | object | - |  |  | Unknown | 39 | 0.0% | No |
| computable_now | bool | - |  |  | Unknown | 39 | 0.0% | No |
| benchmark_elite | float64 | - |  |  | Unknown | 39 | 0.0% | No |
| nhl_avg_per_game | float64 | - |  |  | Unknown | 39 | 0.0% | No |
| nhl_elite_threshold | float64 | - |  |  | Unknown | 39 | 0.0% | No |
| nhl_min_threshold | int64 | - |  |  | Unknown | 39 | 0.0% | No |

---

## dim_stat_category

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 13 |
| **Columns** | 4 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| stat_category_id | object | - |  |  | Unknown | 13 | 0.0% | No |
| category_code | object | - |  |  | Unknown | 13 | 0.0% | No |
| category_name | object | - |  |  | Unknown | 13 | 0.0% | No |
| description | object | - |  |  | Unknown | 13 | 0.0% | No |

---

## dim_stat_type

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 8 |
| **Columns** | 6 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| stat_id | object | - |  |  | Unknown | 8 | 0.0% | No |
| stat_name | object | - |  |  | Unknown | 8 | 0.0% | No |
| stat_category | object | - |  |  | Unknown | 8 | 0.0% | No |
| stat_level | object | - |  |  | Unknown | 8 | 0.0% | No |
| computable_now | bool | - |  |  | Unknown | 8 | 0.0% | No |
| description | object | - |  |  | Unknown | 8 | 0.0% | No |

---

## dim_stoppage_type

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 4 |
| **Columns** | 3 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| stoppage_type_id | object | - |  |  | Unknown | 4 | 0.0% | No |
| stoppage_type_code | object | - |  |  | Unknown | 4 | 0.0% | No |
| stoppage_type_name | object | - |  |  | Unknown | 4 | 0.0% | No |

---

## dim_strength

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 18 |
| **Columns** | 7 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| strength_id | object | - |  |  | Unknown | 18 | 0.0% | No |
| strength_code | object | - |  |  | Unknown | 18 | 0.0% | No |
| strength_name | object | - |  |  | Unknown | 18 | 0.0% | No |
| situation_type | object | - |  |  | Unknown | 18 | 0.0% | No |
| xg_multiplier | float64 | - |  |  | Unknown | 18 | 0.0% | No |
| description | object | - |  |  | Unknown | 18 | 0.0% | No |
| avg_toi_pct | float64 | - |  |  | Unknown | 18 | 0.0% | No |

---

## dim_success

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 3 |
| **Columns** | 4 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| success_id | object | - |  |  | Unknown | 3 | 0.0% | No |
| success_code | object | - |  |  | Unknown | 3 | 0.0% | No |
| success_name | object | - |  |  | Unknown | 3 | 0.0% | No |
| is_successful | object | - |  |  | Unknown | 2 | 33.3% | No |

---

## dim_takeaway_type

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 2 |
| **Columns** | 3 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| takeaway_type_id | object | - |  |  | Unknown | 2 | 0.0% | No |
| takeaway_type_code | object | - |  |  | Unknown | 2 | 0.0% | No |
| takeaway_type_name | object | - |  |  | Unknown | 2 | 0.0% | No |

---

## dim_team

| Property | Value |
|----------|-------|
| **Description** | Team master reference data |
| **Purpose** | Central team lookup. All team FKs reference this. |
| **Source Module** | `src/etl/processors/dim_processor.py:create_dim_team()` |
| **Logic** | Extracted from schedule + roster data |
| **Grain** | One row per unique team |
| **Rows** | 26 |
| **Columns** | 14 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| team_name | object | - |  |  | Unknown | 26 | 0.0% | No |
| team_id | object | Team identifier | FK to dim_team.team_id | From roster or event data | FK | 26 | 0.0% | No |
| norad_team | object | - |  |  | Unknown | 26 | 0.0% | No |
| csah_team | object | - |  |  | Unknown | 26 | 0.0% | No |
| league_id | object | - |  |  | Unknown | 26 | 0.0% | No |
| league | object | - |  |  | Unknown | 26 | 0.0% | No |
| long_team_name | object | - |  |  | Unknown | 26 | 0.0% | No |
| team_cd | object | - |  |  | Unknown | 26 | 0.0% | No |
| team_color1 | object | - |  |  | Unknown | 26 | 0.0% | No |
| team_color2 | object | - |  |  | Unknown | 26 | 0.0% | No |
| team_color3 | object | - |  |  | Unknown | 23 | 11.5% | No |
| team_color4 | object | - |  |  | Unknown | 2 | 92.3% | No |
| team_logo | object | - |  |  | Unknown | 26 | 0.0% | No |
| team_url | object | - |  |  | Unknown | 26 | 0.0% | No |

---

## dim_terminology_mapping

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 23 |
| **Columns** | 4 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| dimension | object | - |  |  | Unknown | 23 | 0.0% | No |
| old_value | object | - |  |  | Unknown | 23 | 0.0% | No |
| new_value | object | - |  |  | Unknown | 23 | 0.0% | No |
| match_type | object | - |  |  | Unknown | 23 | 0.0% | No |

---

## dim_time_bucket

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 6 |
| **Columns** | 6 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| time_bucket_id | object | - |  |  | Unknown | 6 | 0.0% | No |
| time_bucket_code | object | - |  |  | Unknown | 6 | 0.0% | No |
| time_bucket_name | object | - |  |  | Unknown | 6 | 0.0% | No |
| minute_start | int64 | - |  |  | Unknown | 6 | 0.0% | No |
| minute_end | int64 | - |  |  | Unknown | 6 | 0.0% | No |
| description | object | - |  |  | Unknown | 6 | 0.0% | No |

---

## dim_turnover_quality

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 3 |
| **Columns** | 5 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| turnover_quality_id | object | - |  |  | Unknown | 3 | 0.0% | No |
| turnover_quality_code | object | - |  |  | Unknown | 3 | 0.0% | No |
| turnover_quality_name | object | - |  |  | Unknown | 3 | 0.0% | No |
| description | object | - |  |  | Unknown | 3 | 0.0% | No |
| counts_against | bool | - |  |  | Unknown | 3 | 0.0% | No |

---

## dim_turnover_type

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 12 |
| **Columns** | 10 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| turnover_type_id | object | - |  |  | Unknown | 12 | 0.0% | No |
| turnover_type_code | object | - |  |  | Unknown | 12 | 0.0% | No |
| turnover_type_name | object | - |  |  | Unknown | 12 | 0.0% | No |
| category | object | - |  |  | Unknown | 12 | 0.0% | No |
| quality | object | - |  |  | Unknown | 12 | 0.0% | No |
| weight | float64 | - |  |  | Unknown | 12 | 0.0% | No |
| description | object | - |  |  | Unknown | 12 | 0.0% | No |
| zone_context | object | - |  |  | Unknown | 12 | 0.0% | No |
| zone_danger_multiplier | float64 | - |  |  | Unknown | 12 | 0.0% | No |
| old_equiv | object | - |  |  | Unknown | 12 | 0.0% | No |

---

## dim_venue

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 2 |
| **Columns** | 4 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| venue_id | object | - |  |  | Unknown | 2 | 0.0% | No |
| venue_code | object | - |  |  | Unknown | 2 | 0.0% | No |
| venue_name | object | - |  |  | Unknown | 2 | 0.0% | No |
| venue_abbrev | object | - |  |  | Unknown | 2 | 0.0% | No |

---

## dim_zone

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 3 |
| **Columns** | 4 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| zone_id | object | - |  |  | Unknown | 3 | 0.0% | No |
| zone_code | object | - |  |  | Unknown | 3 | 0.0% | No |
| zone_name | object | - |  |  | Unknown | 3 | 0.0% | No |
| zone_abbrev | object | - |  |  | Unknown | 3 | 0.0% | No |

---

## dim_zone_entry_type

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 12 |
| **Columns** | 3 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| zone_entry_type_id | object | - |  |  | Unknown | 12 | 0.0% | No |
| zone_entry_type_code | object | - |  |  | Unknown | 12 | 0.0% | No |
| zone_entry_type_name | object | - |  |  | Unknown | 12 | 0.0% | No |

---

## dim_zone_exit_type

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 10 |
| **Columns** | 3 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| zone_exit_type_id | object | - |  |  | Unknown | 10 | 0.0% | No |
| zone_exit_type_code | object | - |  |  | Unknown | 10 | 0.0% | No |
| zone_exit_type_name | object | - |  |  | Unknown | 10 | 0.0% | No |

---

## dim_zone_outcome

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 6 |
| **Columns** | 5 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| zone_outcome_id | object | - |  |  | Unknown | 6 | 0.0% | No |
| zone_outcome_code | object | - |  |  | Unknown | 6 | 0.0% | No |
| zone_outcome_name | object | - |  |  | Unknown | 6 | 0.0% | No |
| is_controlled | bool | - |  |  | Unknown | 6 | 0.0% | No |
| zone_type | object | - |  |  | Unknown | 6 | 0.0% | No |

---

## fact_breakouts

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 476 |
| **Columns** | 122 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 476 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 476 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 476 | 0.0% | No |
| event_type | object | Type of event | Values: Shot, Goal, Pass, Faceoff, Hit, etc. |  | Explicit | 476 | 0.0% | No |
| event_type_id | object | - |  |  | Unknown | 476 | 0.0% | No |
| event_detail | object | Detail/subtype of event | Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc. |  | Explicit | 476 | 0.0% | No |
| event_detail_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_detail_2 | object | - |  |  | Unknown | 475 | 0.2% | No |
| event_detail_2_id | object | - |  |  | Unknown | 475 | 0.2% | No |
| event_successful | object | - |  |  | Unknown | 229 | 51.9% | No |
| success_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_team_zone | object | - |  |  | Unknown | 476 | 0.0% | No |
| event_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| sequence_key | object | - |  |  | Unknown | 476 | 0.0% | No |
| play_key | object | - |  |  | Unknown | 476 | 0.0% | No |
| event_chain_key | object | - |  |  | Unknown | 476 | 0.0% | No |
| tracking_event_key | object | - |  |  | Unknown | 476 | 0.0% | No |
| home_team | object | - |  |  | Unknown | 476 | 0.0% | No |
| home_team_id | object | - |  |  | Unknown | 476 | 0.0% | No |
| away_team | object | - |  |  | Unknown | 476 | 0.0% | No |
| away_team_id | object | - |  |  | Unknown | 476 | 0.0% | No |
| duration | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| event_player_ids | object | - |  |  | Unknown | 468 | 1.7% | No |
| opp_player_ids | object | - |  |  | Unknown | 155 | 67.4% | No |
| event_start_min | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| event_start_sec | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| event_end_min | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| event_end_sec | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| time_start_total_seconds | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| time_end_total_seconds | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| event_running_start | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| event_running_end | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| running_video_time | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| period_start_total_running_seconds | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| running_intermission_duration | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| team_venue | object | - |  |  | Unknown | 476 | 0.0% | No |
| team_venue_abv | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_team | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_team_zone | object | - |  |  | Unknown | 476 | 0.0% | No |
| away_team_zone | object | - |  |  | Unknown | 476 | 0.0% | No |
| player_role | object | - |  |  | Unknown | 473 | 0.6% | No |
| side_of_puck | object | - |  |  | Unknown | 473 | 0.6% | No |
| role_number | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| role_abrev | object | - |  |  | Unknown | 473 | 0.6% | No |
| player_game_number | float64 | - |  |  | Unknown | 473 | 0.6% | No |
| strength | object | - |  |  | Unknown | 476 | 0.0% | No |
| play_detail1 | object | - |  |  | Unknown | 75 | 84.2% | No |
| play_detail_2 | object | - |  |  | Unknown | 12 | 97.5% | No |
| play_detail_successful | object | - |  |  | Unknown | 77 | 83.8% | No |
| pressured_pressurer | float64 | - |  |  | Unknown | 52 | 89.1% | No |
| is_goal | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_highlight | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 470 | 1.3% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 476 | 0.0% | No |
| position_id | float64 | - |  |  | Unknown | 470 | 1.3% | No |
| shot_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_entry_type_id | object | - |  |  | Unknown | 5 | 98.9% | No |
| zone_exit_type_id | object | - |  |  | Unknown | 470 | 1.3% | No |
| stoppage_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| giveaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| takeaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| turnover_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| time_bucket_id | object | - |  |  | Unknown | 476 | 0.0% | No |
| strength_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_rating | float64 | - |  |  | Unknown | 470 | 1.3% | No |
| is_rush | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_rebound | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_cycle | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_breakout | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_zone_entry | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_zone_exit | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_shot | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_save | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_turnover | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_giveaway | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_takeaway | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_faceoff | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_penalty | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_blocked_shot | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_missed_shot | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_deflected | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_sog | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| shot_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| save_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_outcome_id | object | - |  |  | Unknown | 476 | 0.0% | No |
| is_scoring_chance | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_high_danger | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| is_pressured | int64 | - |  |  | Unknown | 476 | 0.0% | No |
| danger_level | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| danger_level_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| scoring_chance_key | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| breakout_key | object | - |  |  | Unknown | 476 | 0.0% | No |
| breakout_successful | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| time_to_next_event | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| time_from_last_event | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| time_to_next_goal_for | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| time_to_next_goal_against | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| time_from_last_goal_for | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| time_from_last_goal_against | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| time_to_next_stoppage | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| time_from_last_stoppage | float64 | - |  |  | Unknown | 476 | 0.0% | No |
| event_player_1_toi | float64 | - |  |  | Unknown | 468 | 1.7% | No |
| event_player_2_toi | float64 | - |  |  | Unknown | 158 | 66.8% | No |
| event_player_3_toi | float64 | - |  |  | Unknown | 2 | 99.6% | No |
| event_player_4_toi | float64 | - |  |  | Unknown | 1 | 99.8% | No |
| event_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_1_toi | float64 | - |  |  | Unknown | 155 | 67.4% | No |
| opp_player_2_toi | float64 | - |  |  | Unknown | 14 | 97.1% | No |
| opp_player_3_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_4_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| team_on_ice_toi_avg | float64 | - |  |  | Unknown | 468 | 1.7% | No |
| team_on_ice_toi_min | float64 | - |  |  | Unknown | 468 | 1.7% | No |
| team_on_ice_toi_max | float64 | - |  |  | Unknown | 468 | 1.7% | No |
| opp_on_ice_toi_avg | float64 | - |  |  | Unknown | 155 | 67.4% | No |
| opp_on_ice_toi_min | float64 | - |  |  | Unknown | 155 | 67.4% | No |
| opp_on_ice_toi_max | float64 | - |  |  | Unknown | 155 | 67.4% | No |

---

## fact_draft

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 160 |
| **Columns** | 14 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| team_id | object | Team identifier | FK to dim_team.team_id | From roster or event data | FK | 160 | 0.0% | No |
| skill_rating | int64 | - |  |  | Unknown | 160 | 0.0% | No |
| round | int64 | - |  |  | Unknown | 160 | 0.0% | No |
| player_full_name | object | - |  |  | Unknown | 160 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 160 | 0.0% | No |
| team_name | object | - |  |  | Unknown | 160 | 0.0% | No |
| restricted | bool | - |  |  | Unknown | 160 | 0.0% | No |
| overall_draft_round | int64 | - |  |  | Unknown | 160 | 0.0% | No |
| overall_draft_position | int64 | - |  |  | Unknown | 160 | 0.0% | No |
| unrestricted_draft_position | int64 | - |  |  | Unknown | 160 | 0.0% | No |
| season | int64 | - |  |  | Unknown | 160 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 160 | 0.0% | No |
| league | object | - |  |  | Unknown | 160 | 0.0% | No |
| player_draft_id | object | - |  |  | Unknown | 160 | 0.0% | No |

---

## fact_event_chains

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 11,155 |
| **Columns** | 9 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| chain_key | object | - |  |  | Unknown | 11,155 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 11,155 | 0.0% | No |
| chain_id | int64 | - |  |  | Unknown | 11,155 | 0.0% | No |
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 11,155 | 0.0% | No |
| event_type | object | Type of event | Values: Shot, Goal, Pass, Faceoff, Hit, etc. |  | Explicit | 11,155 | 0.0% | No |
| event_detail | object | Detail/subtype of event | Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc. |  | Explicit | 9,546 | 14.4% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 10,978 | 1.6% | No |
| sequence_position | int64 | - |  |  | Unknown | 11,155 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 11,155 | 0.0% | No |

---

## fact_event_players

| Property | Value |
|----------|-------|
| **Description** | Bridge table linking events to players with their roles |
| **Purpose** | Enable player-level stats from events. Query goals/assists/shots by player. |
| **Source Module** | `src/core/base_etl.py:create_event_players()` |
| **Logic** | Unpivots event_player_1 through event_player_6 from fact_events into rows |
| **Grain** | One row per player per event |
| **Rows** | 11,155 |
| **Columns** | 153 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| event_player_key | object | - |  |  | Unknown | 11,155 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 11,155 | 0.0% | No |
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 11,155 | 0.0% | No |
| event_index | int64 | - |  |  | Unknown | 11,155 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 10,978 | 1.6% | No |
| player_role | object | - |  |  | Unknown | 11,132 | 0.2% | No |
| player_game_number | float64 | - |  |  | Unknown | 11,132 | 0.2% | No |
| sequence_key | object | - |  |  | Unknown | 11,153 | 0.0% | No |
| play_key | object | - |  |  | Unknown | 11,153 | 0.0% | No |
| event_chain_key | object | - |  |  | Unknown | 11,155 | 0.0% | No |
| tracking_event_key | object | - |  |  | Unknown | 11,155 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 11,155 | 0.0% | No |
| event_type_id | object | - |  |  | Unknown | 10,657 | 4.5% | No |
| event_detail_id | object | - |  |  | Unknown | 5,120 | 54.1% | No |
| event_detail_2_id | object | - |  |  | Unknown | 8,019 | 28.1% | No |
| event_success_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| away_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_team_id | object | - |  |  | Unknown | 11,155 | 0.0% | No |
| away_team_id | object | - |  |  | Unknown | 11,155 | 0.0% | No |
| player_team_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| team_venue_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_role_id | object | - |  |  | Unknown | 11,132 | 0.2% | No |
| play_detail_id | object | - |  |  | Unknown | 1,531 | 86.3% | No |
| play_detail_2_id | object | - |  |  | Unknown | 193 | 98.3% | No |
| play_success_id | object | - |  |  | Unknown | 1,694 | 84.8% | No |
| event_index_flag | int64 | - |  |  | Unknown | 11,155 | 0.0% | No |
| sequence_index_flag | float64 | - |  |  | Unknown | 26 | 99.8% | No |
| play_index_flag | float64 | - |  |  | Unknown | 19 | 99.8% | No |
| linked_event_index_flag | float64 | - |  |  | Unknown | 2,438 | 78.1% | No |
| event_type | object | Type of event | Values: Shot, Goal, Pass, Faceoff, Hit, etc. |  | Explicit | 11,155 | 0.0% | No |
| team | object | - |  |  | Unknown | 11,155 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 11,155 | 0.0% | No |
| home_team | object | - |  |  | Unknown | 11,155 | 0.0% | No |
| away_team | object | - |  |  | Unknown | 11,155 | 0.0% | No |
| strength | object | - |  |  | Unknown | 11,155 | 0.0% | No |
| event_team_zone | object | - |  |  | Unknown | 11,155 | 0.0% | No |
| event_start_min | float64 | - |  |  | Unknown | 11,150 | 0.0% | No |
| event_start_sec | float64 | - |  |  | Unknown | 11,150 | 0.0% | No |
| event_end_min | float64 | - |  |  | Unknown | 11,150 | 0.0% | No |
| event_end_sec | float64 | - |  |  | Unknown | 11,150 | 0.0% | No |
| event_detail | object | Detail/subtype of event | Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc. |  | Explicit | 9,546 | 14.4% | No |
| event_detail_2 | object | - |  |  | Unknown | 8,019 | 28.1% | No |
| event_successful | object | - |  |  | Unknown | 3,367 | 69.8% | No |
| is_highlight | int64 | - |  |  | Unknown | 11,155 | 0.0% | No |
| Type | object | - |  |  | Unknown | 11,155 | 0.0% | No |
| puck_x_1 | float64 | - |  |  | Unknown | 5 | 100.0% | No |
| puck_y_1 | float64 | - |  |  | Unknown | 5 | 100.0% | No |
| puck_x_2 | float64 | - |  |  | Unknown | 5 | 100.0% | No |
| puck_y_2 | float64 | - |  |  | Unknown | 5 | 100.0% | No |
| role_abrev_binary | object | - |  |  | Unknown | 11,132 | 0.2% | No |
| player_name | object | - |  |  | Unknown | 10,978 | 1.6% | No |
| play_detail2 | object | - |  |  | Unknown | 193 | 98.3% | No |
| play_detail1 | object | - |  |  | Unknown | 2,312 | 79.3% | No |
| play_detail_2 | object | - |  |  | Unknown | 193 | 98.3% | No |
| play_detail_successful | object | - |  |  | Unknown | 1,697 | 84.8% | No |
| pressured_pressurer | float64 | - |  |  | Unknown | 2,195 | 80.3% | No |
| side_of_puck | object | - |  |  | Unknown | 11,132 | 0.2% | No |
| player_x_1 | float64 | - |  |  | Unknown | 5 | 100.0% | No |
| player_y_1 | float64 | - |  |  | Unknown | 5 | 100.0% | No |
| puck_x_3 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| puck_y_3 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| puck_x_4 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| puck_y_4 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| puck_x_5 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| puck_y_5 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| puck_x_6 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| puck_y_6 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| puck_x_7 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| puck_y_7 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| puck_x_8 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| puck_y_8 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| puck_x_9 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| puck_y_9 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| puck_x_10 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| puck_y_10 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_x_2 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_y_2 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_x_3 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_y_3 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_x_4 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_y_4 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_x_5 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_y_5 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_x_6 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_y_6 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_x_7 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_y_7 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_x_8 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_y_8 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_x_9 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_y_9 | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| player_x_10 | float64 | - |  |  | Unknown | 1 | 100.0% | No |
| player_y_10 | float64 | - |  |  | Unknown | 1 | 100.0% | No |
| net_x | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| net_y | float64 | - |  |  | Unknown | 2 | 100.0% | No |
| time_start_total_seconds | float64 | - |  |  | Unknown | 11,150 | 0.0% | No |
| time_end_total_seconds | float64 | - |  |  | Unknown | 11,150 | 0.0% | No |
| duration | float64 | - |  |  | Unknown | 11,150 | 0.0% | No |
| event_running_start | float64 | - |  |  | Unknown | 11,150 | 0.0% | No |
| event_running_end | float64 | - |  |  | Unknown | 11,150 | 0.0% | No |
| period_start_total_running_seconds | int64 | - |  |  | Unknown | 11,155 | 0.0% | No |
| running_video_time | float64 | - |  |  | Unknown | 11,150 | 0.0% | No |
| running_intermission_duration | int64 | - |  |  | Unknown | 11,155 | 0.0% | No |
| team_venue | object | - |  |  | Unknown | 11,155 | 0.0% | No |
| player_team | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_team_zone | object | - |  |  | Unknown | 11,155 | 0.0% | No |
| away_team_zone | object | - |  |  | Unknown | 11,155 | 0.0% | No |
| is_goal | int64 | - |  |  | Unknown | 11,155 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 11,155 | 0.0% | No |
| position_id | float64 | - |  |  | Unknown | 10,978 | 1.6% | No |
| shot_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_entry_type_id | object | - |  |  | Unknown | 1,327 | 88.1% | No |
| zone_exit_type_id | object | - |  |  | Unknown | 828 | 92.6% | No |
| stoppage_type_id | object | - |  |  | Unknown | 168 | 98.5% | No |
| giveaway_type_id | object | - |  |  | Unknown | 1,017 | 90.9% | No |
| takeaway_type_id | object | - |  |  | Unknown | 279 | 97.5% | No |
| turnover_type_id | object | - |  |  | Unknown | 1,296 | 88.4% | No |
| pass_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| time_bucket_id | object | - |  |  | Unknown | 11,150 | 0.0% | No |
| strength_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_rating | float64 | - |  |  | Unknown | 10,978 | 1.6% | No |
| time_to_next_event | float64 | - |  |  | Unknown | 11,150 | 0.0% | No |
| time_from_last_event | float64 | - |  |  | Unknown | 11,150 | 0.0% | No |
| time_to_next_goal_for | float64 | - |  |  | Unknown | 11,155 | 0.0% | No |
| time_to_next_goal_against | float64 | - |  |  | Unknown | 11,155 | 0.0% | No |
| time_from_last_goal_for | float64 | - |  |  | Unknown | 11,155 | 0.0% | No |
| time_from_last_goal_against | float64 | - |  |  | Unknown | 11,155 | 0.0% | No |
| time_to_next_stoppage | float64 | - |  |  | Unknown | 11,155 | 0.0% | No |
| time_from_last_stoppage | float64 | - |  |  | Unknown | 11,155 | 0.0% | No |
| event_player_1_toi | float64 | - |  |  | Unknown | 7,492 | 32.8% | No |
| opp_player_1_toi | float64 | - |  |  | Unknown | 3,486 | 68.7% | No |
| event_player_2_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_2_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_player_3_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_3_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_player_4_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_4_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_toi | float64 | - |  |  | Unknown | 10,978 | 1.6% | No |
| team_on_ice_toi_avg | float64 | - |  |  | Unknown | 7,492 | 32.8% | No |
| team_on_ice_toi_min | float64 | - |  |  | Unknown | 7,492 | 32.8% | No |
| team_on_ice_toi_max | float64 | - |  |  | Unknown | 7,492 | 32.8% | No |
| opp_on_ice_toi_avg | float64 | - |  |  | Unknown | 3,486 | 68.7% | No |
| opp_on_ice_toi_min | float64 | - |  |  | Unknown | 3,486 | 68.7% | No |
| opp_on_ice_toi_max | float64 | - |  |  | Unknown | 3,486 | 68.7% | No |
| event_team_avg_rating | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_team_avg_rating | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| rating_vs_opp | float64 | - |  |  | Unknown | 0 | 100.0% | No |

---

## fact_events

| Property | Value |
|----------|-------|
| **Description** | Raw event-level game tracking data - SOURCE OF TRUTH |
| **Purpose** | Store every tracked event. All other tables derive from this. |
| **Source Module** | `src/etl/processors/events_processor.py:process()` |
| **Logic** | Direct load from tracking spreadsheet with standardization |
| **Grain** | One row per tracked event |
| **Rows** | 5,823 |
| **Columns** | 124 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 5,823 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 5,823 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| event_type | object | Type of event | Values: Shot, Goal, Pass, Faceoff, Hit, etc. |  | Explicit | 5,823 | 0.0% | No |
| event_type_id | object | - |  |  | Unknown | 5,420 | 6.9% | No |
| event_detail | object | Detail/subtype of event | Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc. |  | Explicit | 4,710 | 19.1% | No |
| event_detail_id | object | - |  |  | Unknown | 2,311 | 60.3% | No |
| event_detail_2 | object | - |  |  | Unknown | 3,763 | 35.4% | No |
| event_detail_2_id | object | - |  |  | Unknown | 3,763 | 35.4% | No |
| event_successful | object | - |  |  | Unknown | 1,568 | 73.1% | No |
| success_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_team_zone | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| event_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| sequence_key | object | - |  |  | Unknown | 5,821 | 0.0% | No |
| play_key | object | - |  |  | Unknown | 5,821 | 0.0% | No |
| event_chain_key | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| tracking_event_key | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| home_team | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| home_team_id | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| away_team | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| away_team_id | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| duration | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| event_player_ids | object | - |  |  | Unknown | 5,741 | 1.4% | No |
| opp_player_ids | object | - |  |  | Unknown | 2,842 | 51.2% | No |
| event_start_min | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| event_start_sec | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| event_end_min | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| event_end_sec | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| time_start_total_seconds | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| time_end_total_seconds | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| event_running_start | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| event_running_end | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| running_video_time | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| period_start_total_running_seconds | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| running_intermission_duration | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| team_venue | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| team_venue_abv | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_team | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_team_zone | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| away_team_zone | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| player_role | object | - |  |  | Unknown | 5,800 | 0.4% | No |
| side_of_puck | object | - |  |  | Unknown | 5,800 | 0.4% | No |
| role_number | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| role_abrev | object | - |  |  | Unknown | 5,800 | 0.4% | No |
| player_game_number | float64 | - |  |  | Unknown | 5,800 | 0.4% | No |
| strength | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| play_detail1 | object | - |  |  | Unknown | 1,403 | 75.9% | No |
| play_detail_2 | object | - |  |  | Unknown | 187 | 96.8% | No |
| play_detail_successful | object | - |  |  | Unknown | 1,420 | 75.6% | No |
| pressured_pressurer | float64 | - |  |  | Unknown | 964 | 83.4% | No |
| is_goal | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_highlight | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 5,762 | 1.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 5,823 | 0.0% | No |
| position_id | float64 | - |  |  | Unknown | 5,762 | 1.0% | No |
| shot_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_entry_type_id | object | - |  |  | Unknown | 510 | 91.2% | No |
| zone_exit_type_id | object | - |  |  | Unknown | 483 | 91.7% | No |
| stoppage_type_id | object | - |  |  | Unknown | 162 | 97.2% | No |
| giveaway_type_id | object | - |  |  | Unknown | 602 | 89.7% | No |
| takeaway_type_id | object | - |  |  | Unknown | 133 | 97.7% | No |
| turnover_type_id | object | - |  |  | Unknown | 735 | 87.4% | No |
| pass_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| time_bucket_id | object | - |  |  | Unknown | 5,818 | 0.1% | No |
| strength_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_rating | float64 | - |  |  | Unknown | 5,762 | 1.0% | No |
| is_rush | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_rebound | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_cycle | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_breakout | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_zone_entry | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_zone_exit | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_shot | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_save | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_turnover | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_giveaway | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_takeaway | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_faceoff | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_penalty | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_blocked_shot | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_missed_shot | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_deflected | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_sog | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| shot_outcome_id | object | - |  |  | Unknown | 451 | 92.3% | No |
| pass_outcome_id | object | - |  |  | Unknown | 1,016 | 82.6% | No |
| save_outcome_id | object | - |  |  | Unknown | 213 | 96.3% | No |
| zone_outcome_id | object | - |  |  | Unknown | 1,134 | 80.5% | No |
| is_scoring_chance | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_high_danger | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| is_pressured | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| danger_level | object | - |  |  | Unknown | 451 | 92.3% | No |
| danger_level_id | object | - |  |  | Unknown | 451 | 92.3% | No |
| scoring_chance_key | object | - |  |  | Unknown | 451 | 92.3% | No |
| time_to_next_event | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| time_from_last_event | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| time_to_next_goal_for | float64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| time_to_next_goal_against | float64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| time_from_last_goal_for | float64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| time_from_last_goal_against | float64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| time_to_next_stoppage | float64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| time_from_last_stoppage | float64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| event_player_1_toi | float64 | - |  |  | Unknown | 5,741 | 1.4% | No |
| opp_player_1_toi | float64 | - |  |  | Unknown | 2,842 | 51.2% | No |
| event_player_2_toi | float64 | - |  |  | Unknown | 1,660 | 71.5% | No |
| opp_player_2_toi | float64 | - |  |  | Unknown | 542 | 90.7% | No |
| event_player_3_toi | float64 | - |  |  | Unknown | 55 | 99.1% | No |
| opp_player_3_toi | float64 | - |  |  | Unknown | 89 | 98.5% | No |
| event_player_4_toi | float64 | - |  |  | Unknown | 11 | 99.8% | No |
| opp_player_4_toi | float64 | - |  |  | Unknown | 10 | 99.8% | No |
| event_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_5_toi | float64 | - |  |  | Unknown | 1 | 100.0% | No |
| event_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| team_on_ice_toi_avg | float64 | - |  |  | Unknown | 5,741 | 1.4% | No |
| team_on_ice_toi_min | float64 | - |  |  | Unknown | 5,741 | 1.4% | No |
| team_on_ice_toi_max | float64 | - |  |  | Unknown | 5,741 | 1.4% | No |
| opp_on_ice_toi_avg | float64 | - |  |  | Unknown | 2,842 | 51.2% | No |
| opp_on_ice_toi_min | float64 | - |  |  | Unknown | 2,842 | 51.2% | No |
| opp_on_ice_toi_max | float64 | - |  |  | Unknown | 2,842 | 51.2% | No |
| event_team_avg_rating | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_team_avg_rating | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| rating_vs_opp | float64 | - |  |  | Unknown | 0 | 100.0% | No |

---

## fact_faceoffs

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 169 |
| **Columns** | 122 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 169 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 169 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 169 | 0.0% | No |
| event_type | object | Type of event | Values: Shot, Goal, Pass, Faceoff, Hit, etc. |  | Explicit | 169 | 0.0% | No |
| event_type_id | object | - |  |  | Unknown | 169 | 0.0% | No |
| event_detail | object | Detail/subtype of event | Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc. |  | Explicit | 167 | 1.2% | No |
| event_detail_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_detail_2 | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_detail_2_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_successful | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| success_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_team_zone | object | - |  |  | Unknown | 169 | 0.0% | No |
| event_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| sequence_key | object | - |  |  | Unknown | 169 | 0.0% | No |
| play_key | object | - |  |  | Unknown | 169 | 0.0% | No |
| event_chain_key | object | - |  |  | Unknown | 169 | 0.0% | No |
| tracking_event_key | object | - |  |  | Unknown | 169 | 0.0% | No |
| home_team | object | - |  |  | Unknown | 169 | 0.0% | No |
| home_team_id | object | - |  |  | Unknown | 169 | 0.0% | No |
| away_team | object | - |  |  | Unknown | 169 | 0.0% | No |
| away_team_id | object | - |  |  | Unknown | 169 | 0.0% | No |
| duration | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| event_player_ids | object | - |  |  | Unknown | 169 | 0.0% | No |
| opp_player_ids | object | - |  |  | Unknown | 165 | 2.4% | No |
| event_start_min | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| event_start_sec | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| event_end_min | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| event_end_sec | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| time_start_total_seconds | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| time_end_total_seconds | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| event_running_start | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| event_running_end | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| running_video_time | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| period_start_total_running_seconds | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| running_intermission_duration | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| team_venue | object | - |  |  | Unknown | 169 | 0.0% | No |
| team_venue_abv | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_team | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_team_zone | object | - |  |  | Unknown | 169 | 0.0% | No |
| away_team_zone | object | - |  |  | Unknown | 169 | 0.0% | No |
| player_role | object | - |  |  | Unknown | 169 | 0.0% | No |
| side_of_puck | object | - |  |  | Unknown | 169 | 0.0% | No |
| role_number | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| role_abrev | object | - |  |  | Unknown | 169 | 0.0% | No |
| player_game_number | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| strength | object | - |  |  | Unknown | 169 | 0.0% | No |
| play_detail1 | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| play_detail_2 | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| play_detail_successful | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pressured_pressurer | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| is_goal | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_highlight | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 169 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 169 | 0.0% | No |
| position_id | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| shot_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_entry_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_exit_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| stoppage_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| giveaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| takeaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| turnover_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| time_bucket_id | object | - |  |  | Unknown | 169 | 0.0% | No |
| strength_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_rating | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_rush | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_rebound | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_cycle | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_breakout | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_zone_entry | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_zone_exit | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_shot | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_save | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_turnover | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_giveaway | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_takeaway | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_faceoff | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_penalty | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_blocked_shot | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_missed_shot | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_deflected | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_sog | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| shot_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| save_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| is_scoring_chance | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_high_danger | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| is_pressured | int64 | - |  |  | Unknown | 169 | 0.0% | No |
| danger_level | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| danger_level_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| scoring_chance_key | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| faceoff_key | object | - |  |  | Unknown | 169 | 0.0% | No |
| faceoff_type | object | - |  |  | Unknown | 169 | 0.0% | No |
| time_to_next_event | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| time_from_last_event | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| time_to_next_goal_for | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| time_to_next_goal_against | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| time_from_last_goal_for | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| time_from_last_goal_against | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| time_to_next_stoppage | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| time_from_last_stoppage | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| event_player_1_toi | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| event_player_2_toi | float64 | - |  |  | Unknown | 99 | 41.4% | No |
| event_player_3_toi | float64 | - |  |  | Unknown | 2 | 98.8% | No |
| event_player_4_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_1_toi | float64 | - |  |  | Unknown | 165 | 2.4% | No |
| opp_player_2_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_3_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_4_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| team_on_ice_toi_avg | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| team_on_ice_toi_min | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| team_on_ice_toi_max | float64 | - |  |  | Unknown | 169 | 0.0% | No |
| opp_on_ice_toi_avg | float64 | - |  |  | Unknown | 165 | 2.4% | No |
| opp_on_ice_toi_min | float64 | - |  |  | Unknown | 165 | 2.4% | No |
| opp_on_ice_toi_max | float64 | - |  |  | Unknown | 165 | 2.4% | No |

---

## fact_gameroster

| Property | Value |
|----------|-------|
| **Description** | Player statistics aggregated per game |
| **Purpose** | Game-level player boxscore. Used for game summaries. |
| **Source Module** | `src/etl/processors/gameroster_processor.py:process()` |
| **Logic** | Aggregate goals/assists/points from fact_events grouped by game_id + player_id |
| **Grain** | One row per player per game |
| **Rows** | 14,471 |
| **Columns** | 24 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 14,471 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 14,471 | 0.0% | No |
| team_id | object | Team identifier | FK to dim_team.team_id | From roster or event data | FK | 14,471 | 0.0% | No |
| opp_team_id | object | - |  |  | Unknown | 14,471 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 13,097 | 9.5% | No |
| venue_id | object | - |  |  | Unknown | 14,471 | 0.0% | No |
| position_id | object | - |  |  | Unknown | 14,469 | 0.0% | No |
| team_name | object | - |  |  | Unknown | 14,471 | 0.0% | No |
| opp_team_name | object | - |  |  | Unknown | 14,471 | 0.0% | No |
| team_venue | object | - |  |  | Unknown | 14,471 | 0.0% | No |
| date | object | - |  |  | Unknown | 14,471 | 0.0% | No |
| season | int64 | - |  |  | Unknown | 14,471 | 0.0% | No |
| player_full_name | object | - |  |  | Unknown | 14,471 | 0.0% | No |
| player_game_number | object | - |  |  | Unknown | 14,193 | 1.9% | No |
| player_position | object | - |  |  | Unknown | 14,469 | 0.0% | No |
| goals | float64 | Goals scored |  | COUNT(*) WHERE event_type='Goal' AND event_detail='Goal_Scored' | Calculated | 14,471 | 0.0% | No |
| assist | float64 | - |  |  | Unknown | 14,471 | 0.0% | No |
| points | float64 | Total points |  | goals + assists | Calculated | 14,471 | 0.0% | No |
| goals_against | float64 | - |  |  | Unknown | 14,471 | 0.0% | No |
| pim | float64 | - |  |  | Unknown | 14,471 | 0.0% | No |
| shutouts | float64 | - |  |  | Unknown | 14,471 | 0.0% | No |
| games_played | float64 | Number of games played |  | COUNT(DISTINCT game_id) | Calculated | 14,471 | 0.0% | No |
| sub | float64 | - |  |  | Unknown | 72 | 99.5% | No |
| current_team | object | - |  |  | Unknown | 14,471 | 0.0% | No |

---

## fact_goalie_game_stats

| Property | Value |
|----------|-------|
| **Description** | Goalie-specific statistics per game |
| **Purpose** | Goalie boxscore with saves, goals against, save percentage. |
| **Source Module** | `src/etl/processors/goalie_processor.py:process()` |
| **Logic** | Filter goalies from roster, calculate saves from shots faced minus goals against |
| **Grain** | One row per goalie per game |
| **Rows** | 8 |
| **Columns** | 16 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| goalie_game_key | object | - |  |  | Unknown | 8 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 8 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 8 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 8 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 8 | 0.0% | No |
| team_name | object | - |  |  | Unknown | 8 | 0.0% | No |
| team_id | object | Team identifier | FK to dim_team.team_id | From roster or event data | FK | 8 | 0.0% | No |
| saves | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| goals_against | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| shots_against | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| save_pct | float64 | - |  |  | Unknown | 8 | 0.0% | No |
| saves_rebound | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| saves_freeze | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| saves_glove | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| saves_blocker | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| saves_pad | int64 | - |  |  | Unknown | 8 | 0.0% | No |

---

## fact_h2h

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 621 |
| **Columns** | 14 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| h2h_key | object | - |  |  | Unknown | 621 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 621 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 621 | 0.0% | No |
| player_1_id | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| player_2_id | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| venue | object | - |  |  | Unknown | 621 | 0.0% | No |
| shifts_together | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| toi_together | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| goals_for | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| goals_against | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| plus_minus | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| corsi_for | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| corsi_against | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| cf_pct | float64 | - |  |  | Unknown | 621 | 0.0% | No |

---

## fact_head_to_head

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 621 |
| **Columns** | 15 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| head_to_head_key | object | - |  |  | Unknown | 621 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 621 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 621 | 0.0% | No |
| player_1_id | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| player_2_id | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| venue | object | - |  |  | Unknown | 621 | 0.0% | No |
| shifts_together | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| toi_together | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| goals_for | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| goals_against | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| plus_minus | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| corsi_for | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| corsi_against | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| cf_pct | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 621 | 0.0% | No |

---

## fact_high_danger_chances

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 31 |
| **Columns** | 95 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 31 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 31 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 31 | 0.0% | No |
| event_type | object | Type of event | Values: Shot, Goal, Pass, Faceoff, Hit, etc. |  | Explicit | 31 | 0.0% | No |
| event_type_id | object | - |  |  | Unknown | 31 | 0.0% | No |
| event_detail | object | Detail/subtype of event | Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc. |  | Explicit | 31 | 0.0% | No |
| event_detail_id | object | - |  |  | Unknown | 31 | 0.0% | No |
| event_detail_2 | object | - |  |  | Unknown | 31 | 0.0% | No |
| event_detail_2_id | object | - |  |  | Unknown | 31 | 0.0% | No |
| event_successful | object | - |  |  | Unknown | 14 | 54.8% | No |
| success_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_team_zone | object | - |  |  | Unknown | 31 | 0.0% | No |
| event_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| sequence_key | object | - |  |  | Unknown | 31 | 0.0% | No |
| play_key | object | - |  |  | Unknown | 31 | 0.0% | No |
| event_chain_key | object | - |  |  | Unknown | 31 | 0.0% | No |
| tracking_event_key | object | - |  |  | Unknown | 31 | 0.0% | No |
| home_team | object | - |  |  | Unknown | 31 | 0.0% | No |
| home_team_id | object | - |  |  | Unknown | 31 | 0.0% | No |
| away_team | object | - |  |  | Unknown | 31 | 0.0% | No |
| away_team_id | object | - |  |  | Unknown | 31 | 0.0% | No |
| duration | float64 | - |  |  | Unknown | 31 | 0.0% | No |
| event_player_ids | object | - |  |  | Unknown | 31 | 0.0% | No |
| opp_player_ids | object | - |  |  | Unknown | 27 | 12.9% | No |
| event_start_min | float64 | - |  |  | Unknown | 31 | 0.0% | No |
| event_start_sec | float64 | - |  |  | Unknown | 31 | 0.0% | No |
| event_end_min | float64 | - |  |  | Unknown | 31 | 0.0% | No |
| event_end_sec | float64 | - |  |  | Unknown | 31 | 0.0% | No |
| time_start_total_seconds | float64 | - |  |  | Unknown | 31 | 0.0% | No |
| time_end_total_seconds | float64 | - |  |  | Unknown | 31 | 0.0% | No |
| event_running_start | float64 | - |  |  | Unknown | 31 | 0.0% | No |
| event_running_end | float64 | - |  |  | Unknown | 31 | 0.0% | No |
| running_video_time | float64 | - |  |  | Unknown | 31 | 0.0% | No |
| period_start_total_running_seconds | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| running_intermission_duration | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| team_venue | object | - |  |  | Unknown | 31 | 0.0% | No |
| team_venue_abv | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_team | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_team_zone | object | - |  |  | Unknown | 31 | 0.0% | No |
| away_team_zone | object | - |  |  | Unknown | 31 | 0.0% | No |
| player_role | object | - |  |  | Unknown | 31 | 0.0% | No |
| side_of_puck | object | - |  |  | Unknown | 31 | 0.0% | No |
| role_number | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| role_abrev | object | - |  |  | Unknown | 31 | 0.0% | No |
| player_game_number | float64 | - |  |  | Unknown | 31 | 0.0% | No |
| strength | object | - |  |  | Unknown | 31 | 0.0% | No |
| play_detail1 | object | - |  |  | Unknown | 2 | 93.5% | No |
| play_detail_2 | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| play_detail_successful | object | - |  |  | Unknown | 3 | 90.3% | No |
| pressured_pressurer | float64 | - |  |  | Unknown | 4 | 87.1% | No |
| is_goal | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_highlight | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 31 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 31 | 0.0% | No |
| position_id | float64 | - |  |  | Unknown | 31 | 0.0% | No |
| shot_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_entry_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_exit_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| stoppage_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| giveaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| takeaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| turnover_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| time_bucket_id | object | - |  |  | Unknown | 31 | 0.0% | No |
| strength_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_rating | float64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_rush | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_rebound | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_cycle | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_breakout | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_zone_entry | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_zone_exit | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_shot | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_save | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_turnover | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_giveaway | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_takeaway | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_faceoff | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_penalty | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_blocked_shot | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_missed_shot | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_deflected | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_sog | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| shot_outcome_id | object | - |  |  | Unknown | 31 | 0.0% | No |
| pass_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| save_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| is_scoring_chance | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_high_danger | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| is_pressured | int64 | - |  |  | Unknown | 31 | 0.0% | No |
| danger_level | object | - |  |  | Unknown | 31 | 0.0% | No |
| danger_level_id | object | - |  |  | Unknown | 31 | 0.0% | No |
| scoring_chance_key | object | - |  |  | Unknown | 31 | 0.0% | No |
| high_danger_key | object | - |  |  | Unknown | 31 | 0.0% | No |

---

## fact_leadership

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 28 |
| **Columns** | 9 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| player_full_name | object | - |  |  | Unknown | 28 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 28 | 0.0% | No |
| leadership | object | - |  |  | Unknown | 28 | 0.0% | No |
| skill_rating | int64 | - |  |  | Unknown | 28 | 0.0% | No |
| n_player_url | object | - |  |  | Unknown | 28 | 0.0% | No |
| team_name | object | - |  |  | Unknown | 28 | 0.0% | No |
| team_id | object | Team identifier | FK to dim_team.team_id | From roster or event data | FK | 28 | 0.0% | No |
| season | int64 | - |  |  | Unknown | 28 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 28 | 0.0% | No |

---

## fact_league_leaders_snapshot

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 20 |
| **Columns** | 8 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| leader_key | object | - |  |  | Unknown | 20 | 0.0% | No |
| category | object | - |  |  | Unknown | 20 | 0.0% | No |
| rank | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 20 | 0.0% | No |
| value | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| games_played | int64 | Number of games played |  | COUNT(DISTINCT game_id) | Calculated | 20 | 0.0% | No |
| snapshot_date | object | - |  |  | Unknown | 20 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 20 | 0.0% | No |

---

## fact_line_combos

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 199 |
| **Columns** | 13 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| line_combo_key | object | - |  |  | Unknown | 199 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 199 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 199 | 0.0% | No |
| venue | object | - |  |  | Unknown | 199 | 0.0% | No |
| combo_type | object | - |  |  | Unknown | 199 | 0.0% | No |
| forward_combo | object | - |  |  | Unknown | 142 | 28.6% | No |
| defense_combo | object | - |  |  | Unknown | 57 | 71.4% | No |
| shifts | int64 | - |  |  | Unknown | 199 | 0.0% | No |
| toi_together | float64 | - |  |  | Unknown | 199 | 0.0% | No |
| goals_for | int64 | - |  |  | Unknown | 199 | 0.0% | No |
| goals_against | int64 | - |  |  | Unknown | 199 | 0.0% | No |
| corsi_for | int64 | - |  |  | Unknown | 199 | 0.0% | No |
| corsi_against | int64 | - |  |  | Unknown | 199 | 0.0% | No |

---

## fact_matchup_performance

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 621 |
| **Columns** | 33 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| h2h_key | object | - |  |  | Unknown | 621 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 621 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 621 | 0.0% | No |
| player_1_id | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| player_2_id | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| venue | object | - |  |  | Unknown | 621 | 0.0% | No |
| shifts_together | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| toi_together | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| goals_for | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| goals_against | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| plus_minus | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| corsi_for | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| corsi_against | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| cf_pct | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| wowy_key | object | - |  |  | Unknown | 621 | 0.0% | No |
| season_id_wowy | object | - |  |  | Unknown | 621 | 0.0% | No |
| venue_wowy | object | - |  |  | Unknown | 621 | 0.0% | No |
| shifts_together_wowy | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| toi_together_wowy | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| p1_shifts_without_p2 | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| p2_shifts_without_p1 | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| toi_apart | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| toi_p1_without_p2 | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| toi_p2_without_p1 | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| cf_pct_together | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| cf_pct_apart | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| cf_pct_delta | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| gf_pct_together | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| gf_pct_apart | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| gf_pct_delta | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| relative_corsi | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| performance_key | object | - |  |  | Unknown | 621 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 621 | 0.0% | No |

---

## fact_matchup_summary

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 621 |
| **Columns** | 16 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| h2h_key | object | - |  |  | Unknown | 621 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 621 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 621 | 0.0% | No |
| player_1_id | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| player_2_id | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| venue | object | - |  |  | Unknown | 621 | 0.0% | No |
| shifts_together | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| toi_together | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| goals_for | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| goals_against | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| plus_minus | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| corsi_for | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| corsi_against | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| cf_pct | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| matchup_key | object | - |  |  | Unknown | 621 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 621 | 0.0% | No |

---

## fact_penalties

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 20 |
| **Columns** | 95 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 20 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 20 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 20 | 0.0% | No |
| event_type | object | Type of event | Values: Shot, Goal, Pass, Faceoff, Hit, etc. |  | Explicit | 20 | 0.0% | No |
| event_type_id | object | - |  |  | Unknown | 20 | 0.0% | No |
| event_detail | object | Detail/subtype of event | Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc. |  | Explicit | 20 | 0.0% | No |
| event_detail_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_detail_2 | object | - |  |  | Unknown | 11 | 45.0% | No |
| event_detail_2_id | object | - |  |  | Unknown | 11 | 45.0% | No |
| event_successful | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| success_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_team_zone | object | - |  |  | Unknown | 20 | 0.0% | No |
| event_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| sequence_key | object | - |  |  | Unknown | 20 | 0.0% | No |
| play_key | object | - |  |  | Unknown | 20 | 0.0% | No |
| event_chain_key | object | - |  |  | Unknown | 20 | 0.0% | No |
| tracking_event_key | object | - |  |  | Unknown | 20 | 0.0% | No |
| home_team | object | - |  |  | Unknown | 20 | 0.0% | No |
| home_team_id | object | - |  |  | Unknown | 20 | 0.0% | No |
| away_team | object | - |  |  | Unknown | 20 | 0.0% | No |
| away_team_id | object | - |  |  | Unknown | 20 | 0.0% | No |
| duration | float64 | - |  |  | Unknown | 20 | 0.0% | No |
| event_player_ids | object | - |  |  | Unknown | 20 | 0.0% | No |
| opp_player_ids | object | - |  |  | Unknown | 13 | 35.0% | No |
| event_start_min | float64 | - |  |  | Unknown | 20 | 0.0% | No |
| event_start_sec | float64 | - |  |  | Unknown | 20 | 0.0% | No |
| event_end_min | float64 | - |  |  | Unknown | 20 | 0.0% | No |
| event_end_sec | float64 | - |  |  | Unknown | 20 | 0.0% | No |
| time_start_total_seconds | float64 | - |  |  | Unknown | 20 | 0.0% | No |
| time_end_total_seconds | float64 | - |  |  | Unknown | 20 | 0.0% | No |
| event_running_start | float64 | - |  |  | Unknown | 20 | 0.0% | No |
| event_running_end | float64 | - |  |  | Unknown | 20 | 0.0% | No |
| running_video_time | float64 | - |  |  | Unknown | 20 | 0.0% | No |
| period_start_total_running_seconds | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| running_intermission_duration | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| team_venue | object | - |  |  | Unknown | 20 | 0.0% | No |
| team_venue_abv | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_team | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_team_zone | object | - |  |  | Unknown | 20 | 0.0% | No |
| away_team_zone | object | - |  |  | Unknown | 20 | 0.0% | No |
| player_role | object | - |  |  | Unknown | 20 | 0.0% | No |
| side_of_puck | object | - |  |  | Unknown | 20 | 0.0% | No |
| role_number | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| role_abrev | object | - |  |  | Unknown | 20 | 0.0% | No |
| player_game_number | float64 | - |  |  | Unknown | 20 | 0.0% | No |
| strength | object | - |  |  | Unknown | 20 | 0.0% | No |
| play_detail1 | object | - |  |  | Unknown | 1 | 95.0% | No |
| play_detail_2 | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| play_detail_successful | object | - |  |  | Unknown | 1 | 95.0% | No |
| pressured_pressurer | float64 | - |  |  | Unknown | 2 | 90.0% | No |
| is_goal | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_highlight | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 20 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 20 | 0.0% | No |
| position_id | float64 | - |  |  | Unknown | 20 | 0.0% | No |
| shot_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_entry_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_exit_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| stoppage_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| giveaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| takeaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| turnover_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| time_bucket_id | object | - |  |  | Unknown | 20 | 0.0% | No |
| strength_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_rating | float64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_rush | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_rebound | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_cycle | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_breakout | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_zone_entry | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_zone_exit | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_shot | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_save | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_turnover | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_giveaway | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_takeaway | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_faceoff | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_penalty | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_blocked_shot | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_missed_shot | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_deflected | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_sog | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| shot_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| save_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| is_scoring_chance | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_high_danger | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| is_pressured | int64 | - |  |  | Unknown | 20 | 0.0% | No |
| danger_level | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| danger_level_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| scoring_chance_key | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| penalty_key | object | - |  |  | Unknown | 20 | 0.0% | No |

---

## fact_period_momentum

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 24 |
| **Columns** | 9 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| momentum_key | object | - |  |  | Unknown | 24 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 24 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 24 | 0.0% | No |
| venue | object | - |  |  | Unknown | 24 | 0.0% | No |
| shots | int64 | - |  |  | Unknown | 24 | 0.0% | No |
| goals | int64 | Goals scored |  | COUNT(*) WHERE event_type='Goal' AND event_detail='Goal_Scored' | Calculated | 24 | 0.0% | No |
| corsi_events | int64 | - |  |  | Unknown | 24 | 0.0% | No |
| momentum_score | float64 | - |  |  | Unknown | 24 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 24 | 0.0% | No |

---

## fact_player_boxscore_all

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 105 |
| **Columns** | 71 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| player_game_key | object | - |  |  | Unknown | 105 | 0.0% | No |
| player_game_id | object | - |  |  | Unknown | 105 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 105 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 105 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 105 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 105 | 0.0% | No |
| team_id | object | Team identifier | FK to dim_team.team_id | From roster or event data | FK | 105 | 0.0% | No |
| team_name | object | - |  |  | Unknown | 105 | 0.0% | No |
| position | object | - |  |  | Unknown | 105 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 105 | 0.0% | No |
| goals | int64 | Goals scored |  | COUNT(*) WHERE event_type='Goal' AND event_detail='Goal_Scored' | Calculated | 105 | 0.0% | No |
| primary_assists | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| secondary_assists | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| assists | int64 | Assists (primary + secondary) |  | COUNT(*) WHERE player is event_player_2 or event_player_3 on goal events | Calculated | 105 | 0.0% | No |
| points | int64 | Total points |  | goals + assists | Calculated | 105 | 0.0% | No |
| shots | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| sog | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| shots_blocked | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| shots_missed | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| shooting_pct | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| pass_attempts | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| pass_completed | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| pass_pct | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| fo_total | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| fo_wins | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| fo_losses | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| fo_pct | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| zone_entries | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| zone_exits | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| controlled_entries | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| controlled_entry_pct | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| controlled_exits | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| controlled_exit_pct | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| giveaways | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| takeaways | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| turnover_diff | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| blocks | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| hits | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| screens | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| tips | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| one_timers | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| dekes | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| backchecks | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| forechecks | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| puck_recoveries | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| stick_checks | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| poke_checks | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| toi_seconds | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| toi_minutes | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| shift_count | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| avg_shift | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| plus_ev | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| minus_ev | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| plus_minus_ev | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| corsi_for | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| corsi_against | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| cf_pct | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| player_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| opp_avg_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| rating_diff | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| goals_per_60 | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| assists_per_60 | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| points_per_60 | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| shots_per_60 | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| sog_per_60 | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| offensive_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| defensive_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| two_way_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| hustle_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| game_score | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| boxscore_key | object | - |  |  | Unknown | 105 | 0.0% | No |

---

## fact_player_career_stats

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 67 |
| **Columns** | 65 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 67 | 0.0% | No |
| goals | int64 | Goals scored |  | COUNT(*) WHERE event_type='Goal' AND event_detail='Goal_Scored' | Calculated | 67 | 0.0% | No |
| primary_assists | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| secondary_assists | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| assists | int64 | Assists (primary + secondary) |  | COUNT(*) WHERE player is event_player_2 or event_player_3 on goal events | Calculated | 67 | 0.0% | No |
| points | int64 | Total points |  | goals + assists | Calculated | 67 | 0.0% | No |
| shots | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| sog | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| shots_blocked | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| shots_missed | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| shooting_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| pass_attempts | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| pass_completed | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| pass_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| fo_total | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| fo_wins | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| fo_losses | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| fo_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| zone_entries | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| zone_exits | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| controlled_entries | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| controlled_entry_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| controlled_exits | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| controlled_exit_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| giveaways | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| takeaways | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| turnover_diff | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| blocks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| hits | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| screens | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| tips | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| one_timers | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| dekes | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| backchecks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| forechecks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| puck_recoveries | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| stick_checks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| poke_checks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| toi_seconds | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| toi_minutes | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| shift_count | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| avg_shift | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| plus_ev | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| minus_ev | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| plus_minus_ev | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| corsi_for | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| corsi_against | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| cf_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| player_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| opp_avg_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| rating_diff | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| goals_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| assists_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| points_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| shots_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| sog_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| offensive_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| defensive_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| two_way_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| hustle_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| game_score | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| games_played | int64 | Number of games played |  | COUNT(DISTINCT game_id) | Calculated | 67 | 0.0% | No |
| seasons_played | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| player_career_key | object | - |  |  | Unknown | 67 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 67 | 0.0% | No |

---

## fact_player_event_chains

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 105 |
| **Columns** | 6 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 105 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 105 | 0.0% | No |
| chains_involved | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| events_in_chains | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| player_chain_key | object | - |  |  | Unknown | 105 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 105 | 0.0% | No |

---

## fact_player_game_position

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 105 |
| **Columns** | 8 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 105 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 105 | 0.0% | No |
| total_shifts | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| dominant_position | object | - |  |  | Unknown | 105 | 0.0% | No |
| dominant_position_pct | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| forward_shifts | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| defense_shifts | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| goalie_shifts | int64 | - |  |  | Unknown | 105 | 0.0% | No |

---

## fact_player_game_stats

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 105 |
| **Columns** | 70 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| player_game_key | object | - |  |  | Unknown | 105 | 0.0% | No |
| player_game_id | object | - |  |  | Unknown | 105 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 105 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 105 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 105 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 105 | 0.0% | No |
| team_id | object | Team identifier | FK to dim_team.team_id | From roster or event data | FK | 105 | 0.0% | No |
| team_name | object | - |  |  | Unknown | 105 | 0.0% | No |
| position | object | - |  |  | Unknown | 105 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 105 | 0.0% | No |
| goals | int64 | Goals scored |  | COUNT(*) WHERE event_type='Goal' AND event_detail='Goal_Scored' | Calculated | 105 | 0.0% | No |
| primary_assists | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| secondary_assists | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| assists | int64 | Assists (primary + secondary) |  | COUNT(*) WHERE player is event_player_2 or event_player_3 on goal events | Calculated | 105 | 0.0% | No |
| points | int64 | Total points |  | goals + assists | Calculated | 105 | 0.0% | No |
| shots | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| sog | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| shots_blocked | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| shots_missed | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| shooting_pct | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| pass_attempts | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| pass_completed | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| pass_pct | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| fo_total | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| fo_wins | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| fo_losses | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| fo_pct | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| zone_entries | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| zone_exits | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| controlled_entries | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| controlled_entry_pct | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| controlled_exits | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| controlled_exit_pct | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| giveaways | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| takeaways | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| turnover_diff | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| blocks | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| hits | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| screens | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| tips | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| one_timers | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| dekes | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| backchecks | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| forechecks | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| puck_recoveries | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| stick_checks | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| poke_checks | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| toi_seconds | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| toi_minutes | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| shift_count | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| avg_shift | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| plus_ev | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| minus_ev | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| plus_minus_ev | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| corsi_for | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| corsi_against | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| cf_pct | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| player_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| opp_avg_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| rating_diff | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| goals_per_60 | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| assists_per_60 | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| points_per_60 | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| shots_per_60 | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| sog_per_60 | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| offensive_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| defensive_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| two_way_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| hustle_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| game_score | float64 | - |  |  | Unknown | 105 | 0.0% | No |

---

## fact_player_matchups_xy

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 2 |
| **Columns** | 23 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| matchup_key | object | - |  |  | Unknown | 2 | 0.0% | No |
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 2 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 2 | 0.0% | No |
| event_player_id | object | - |  |  | Unknown | 2 | 0.0% | No |
| event_player_name | object | - |  |  | Unknown | 2 | 0.0% | No |
| event_player_role | object | - |  |  | Unknown | 2 | 0.0% | No |
| event_player_x_start | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| event_player_y_start | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| event_player_x_end | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| event_player_y_end | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| opp_player_id | object | - |  |  | Unknown | 2 | 0.0% | No |
| opp_player_name | object | - |  |  | Unknown | 2 | 0.0% | No |
| opp_player_role | object | - |  |  | Unknown | 2 | 0.0% | No |
| opp_player_x_start | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| opp_player_y_start | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| opp_player_x_end | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| opp_player_y_end | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| distance_start | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| distance_end | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| distance_change | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| is_closing | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| gap_rating | object | - |  |  | Unknown | 2 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 2 | 0.0% | No |

---

## fact_player_micro_stats

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 105 |
| **Columns** | 12 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| micro_stats_key | object | - |  |  | Unknown | 105 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 105 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 105 | 0.0% | No |
| screens | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| tips | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| one_timers | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| dekes | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| rebounds | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| backchecks | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| forechecks | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| board_battles | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 105 | 0.0% | No |

---

## fact_player_pair_stats

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 621 |
| **Columns** | 16 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| h2h_key | object | - |  |  | Unknown | 621 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 621 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 621 | 0.0% | No |
| player_1_id | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| player_2_id | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| venue | object | - |  |  | Unknown | 621 | 0.0% | No |
| shifts_together | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| toi_together | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| goals_for | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| goals_against | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| plus_minus | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| corsi_for | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| corsi_against | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| cf_pct | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| pair_key | object | - |  |  | Unknown | 621 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 621 | 0.0% | No |

---

## fact_player_period_stats

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 315 |
| **Columns** | 9 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| player_period_key | object | - |  |  | Unknown | 315 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 315 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 315 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 315 | 0.0% | No |
| goals | int64 | Goals scored |  | COUNT(*) WHERE event_type='Goal' AND event_detail='Goal_Scored' | Calculated | 315 | 0.0% | No |
| shots | int64 | - |  |  | Unknown | 315 | 0.0% | No |
| passes | int64 | - |  |  | Unknown | 315 | 0.0% | No |
| toi_seconds | int64 | - |  |  | Unknown | 315 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 315 | 0.0% | No |

---

## fact_player_position_splits

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 67 |
| **Columns** | 65 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 67 | 0.0% | No |
| position | object | - |  |  | Unknown | 67 | 0.0% | No |
| goals | int64 | Goals scored |  | COUNT(*) WHERE event_type='Goal' AND event_detail='Goal_Scored' | Calculated | 67 | 0.0% | No |
| primary_assists | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| secondary_assists | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| assists | int64 | Assists (primary + secondary) |  | COUNT(*) WHERE player is event_player_2 or event_player_3 on goal events | Calculated | 67 | 0.0% | No |
| points | int64 | Total points |  | goals + assists | Calculated | 67 | 0.0% | No |
| shots | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| sog | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| shots_blocked | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| shots_missed | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| shooting_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| pass_attempts | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| pass_completed | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| pass_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| fo_total | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| fo_wins | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| fo_losses | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| fo_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| zone_entries | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| zone_exits | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| controlled_entries | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| controlled_entry_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| controlled_exits | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| controlled_exit_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| giveaways | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| takeaways | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| turnover_diff | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| blocks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| hits | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| screens | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| tips | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| one_timers | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| dekes | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| backchecks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| forechecks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| puck_recoveries | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| stick_checks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| poke_checks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| toi_seconds | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| toi_minutes | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| shift_count | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| avg_shift | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| plus_ev | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| minus_ev | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| plus_minus_ev | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| corsi_for | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| corsi_against | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| cf_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| player_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| opp_avg_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| rating_diff | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| goals_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| assists_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| points_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| shots_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| sog_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| offensive_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| defensive_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| two_way_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| hustle_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| game_score | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| games_at_position | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| split_key | object | - |  |  | Unknown | 67 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 67 | 0.0% | No |

---

## fact_player_puck_proximity

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 5 |
| **Columns** | 15 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| proximity_key | object | - |  |  | Unknown | 5 | 0.0% | No |
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 5 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 5 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 5 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 5 | 0.0% | No |
| player_role | object | - |  |  | Unknown | 5 | 0.0% | No |
| is_event_team | bool | - |  |  | Unknown | 5 | 0.0% | No |
| player_x | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| player_y | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| puck_x | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| puck_y | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| distance_to_puck | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| is_puck_carrier | bool | - |  |  | Unknown | 5 | 0.0% | No |
| is_pressuring | bool | - |  |  | Unknown | 5 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 5 | 0.0% | No |

---

## fact_player_qoc_summary

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 105 |
| **Columns** | 8 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| qoc_key | object | - |  |  | Unknown | 105 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 105 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 105 | 0.0% | No |
| avg_opp_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| avg_own_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| rating_diff | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| shifts_tracked | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 105 | 0.0% | No |

---

## fact_player_season_stats

| Property | Value |
|----------|-------|
| **Description** | Player statistics aggregated per season |
| **Purpose** | Season leaderboards, player profiles, historical comparison. |
| **Source Module** | `src/etl/processors/player_stats_processor.py:process()` |
| **Logic** | Sum of game stats from fact_gameroster grouped by player_id + season_id |
| **Grain** | One row per player per season |
| **Rows** | 67 |
| **Columns** | 65 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 67 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 67 | 0.0% | No |
| goals | int64 | Goals scored |  | COUNT(*) WHERE event_type='Goal' AND event_detail='Goal_Scored' | Calculated | 67 | 0.0% | No |
| primary_assists | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| secondary_assists | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| assists | int64 | Assists (primary + secondary) |  | COUNT(*) WHERE player is event_player_2 or event_player_3 on goal events | Calculated | 67 | 0.0% | No |
| points | int64 | Total points |  | goals + assists | Calculated | 67 | 0.0% | No |
| shots | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| sog | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| shots_blocked | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| shots_missed | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| shooting_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| pass_attempts | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| pass_completed | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| pass_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| fo_total | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| fo_wins | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| fo_losses | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| fo_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| zone_entries | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| zone_exits | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| controlled_entries | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| controlled_entry_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| controlled_exits | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| controlled_exit_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| giveaways | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| takeaways | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| turnover_diff | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| blocks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| hits | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| screens | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| tips | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| one_timers | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| dekes | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| backchecks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| forechecks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| puck_recoveries | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| stick_checks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| poke_checks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| toi_seconds | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| toi_minutes | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| shift_count | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| avg_shift | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| plus_ev | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| minus_ev | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| plus_minus_ev | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| corsi_for | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| corsi_against | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| cf_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| player_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| opp_avg_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| rating_diff | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| goals_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| assists_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| points_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| shots_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| sog_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| offensive_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| defensive_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| two_way_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| hustle_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| game_score | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| games_played | int64 | Number of games played |  | COUNT(DISTINCT game_id) | Calculated | 67 | 0.0% | No |
| player_season_key | object | - |  |  | Unknown | 67 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 67 | 0.0% | No |

---

## fact_player_stats_by_competition_tier

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 67 |
| **Columns** | 65 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 67 | 0.0% | No |
| competition_tier | object | - |  |  | Unknown | 67 | 0.0% | No |
| goals | int64 | Goals scored |  | COUNT(*) WHERE event_type='Goal' AND event_detail='Goal_Scored' | Calculated | 67 | 0.0% | No |
| primary_assists | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| secondary_assists | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| assists | int64 | Assists (primary + secondary) |  | COUNT(*) WHERE player is event_player_2 or event_player_3 on goal events | Calculated | 67 | 0.0% | No |
| points | int64 | Total points |  | goals + assists | Calculated | 67 | 0.0% | No |
| shots | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| sog | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| shots_blocked | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| shots_missed | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| shooting_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| pass_attempts | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| pass_completed | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| pass_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| fo_total | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| fo_wins | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| fo_losses | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| fo_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| zone_entries | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| zone_exits | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| controlled_entries | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| controlled_entry_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| controlled_exits | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| controlled_exit_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| giveaways | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| takeaways | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| turnover_diff | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| blocks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| hits | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| screens | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| tips | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| one_timers | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| dekes | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| backchecks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| forechecks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| puck_recoveries | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| stick_checks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| poke_checks | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| toi_seconds | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| toi_minutes | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| shift_count | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| avg_shift | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| plus_ev | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| minus_ev | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| plus_minus_ev | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| corsi_for | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| corsi_against | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| cf_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| player_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| opp_avg_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| rating_diff | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| goals_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| assists_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| points_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| shots_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| sog_per_60 | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| offensive_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| defensive_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| two_way_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| hustle_rating | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| game_score | float64 | - |  |  | Unknown | 67 | 0.0% | No |
| games_vs_tier | int64 | - |  |  | Unknown | 67 | 0.0% | No |
| tier_key | object | - |  |  | Unknown | 67 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 67 | 0.0% | No |

---

## fact_player_stats_long

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 1,155 |
| **Columns** | 7 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| player_game_key | object | - |  |  | Unknown | 1,155 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 1,155 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 1,155 | 0.0% | No |
| stat_code | object | - |  |  | Unknown | 1,155 | 0.0% | No |
| stat_value | float64 | - |  |  | Unknown | 1,155 | 0.0% | No |
| stat_long_key | object | - |  |  | Unknown | 1,155 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 1,155 | 0.0% | No |

---

## fact_player_trends

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 54 |
| **Columns** | 8 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| trend_key | object | - |  |  | Unknown | 54 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 54 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 54 | 0.0% | No |
| game_date | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| points_3g_avg | float64 | - |  |  | Unknown | 54 | 0.0% | No |
| goals_3g_avg | float64 | - |  |  | Unknown | 54 | 0.0% | No |
| trend_direction | object | - |  |  | Unknown | 54 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 54 | 0.0% | No |

---

## fact_player_xy_long

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 22 |
| **Columns** | 13 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| player_xy_key | object | - |  |  | Unknown | 22 | 0.0% | No |
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 22 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 22 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 22 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 22 | 0.0% | No |
| player_role | object | - |  |  | Unknown | 22 | 0.0% | No |
| is_event_team | bool | - |  |  | Unknown | 22 | 0.0% | No |
| point_number | int64 | - |  |  | Unknown | 22 | 0.0% | No |
| x | float64 | - |  |  | Unknown | 22 | 0.0% | No |
| y | float64 | - |  |  | Unknown | 22 | 0.0% | No |
| distance_to_net | float64 | - |  |  | Unknown | 22 | 0.0% | No |
| angle_to_net | float64 | - |  |  | Unknown | 9 | 59.1% | No |
| _export_timestamp | object | - |  |  | Unknown | 22 | 0.0% | No |

---

## fact_player_xy_wide

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 5 |
| **Columns** | 37 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| player_xy_key | object | - |  |  | Unknown | 5 | 0.0% | No |
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 5 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 5 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 5 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 5 | 0.0% | No |
| player_role | object | - |  |  | Unknown | 5 | 0.0% | No |
| team_id | float64 | Team identifier | FK to dim_team.team_id | From roster or event data | FK | 0 | 100.0% | No |
| is_event_team | bool | - |  |  | Unknown | 5 | 0.0% | No |
| point_count | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| x_1 | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| y_1 | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| x_2 | float64 | - |  |  | Unknown | 2 | 60.0% | No |
| y_2 | float64 | - |  |  | Unknown | 2 | 60.0% | No |
| x_3 | float64 | - |  |  | Unknown | 2 | 60.0% | No |
| y_3 | float64 | - |  |  | Unknown | 2 | 60.0% | No |
| x_4 | float64 | - |  |  | Unknown | 2 | 60.0% | No |
| y_4 | float64 | - |  |  | Unknown | 2 | 60.0% | No |
| x_5 | float64 | - |  |  | Unknown | 2 | 60.0% | No |
| y_5 | float64 | - |  |  | Unknown | 2 | 60.0% | No |
| x_6 | float64 | - |  |  | Unknown | 2 | 60.0% | No |
| y_6 | float64 | - |  |  | Unknown | 2 | 60.0% | No |
| x_7 | float64 | - |  |  | Unknown | 2 | 60.0% | No |
| y_7 | float64 | - |  |  | Unknown | 2 | 60.0% | No |
| x_8 | float64 | - |  |  | Unknown | 2 | 60.0% | No |
| y_8 | float64 | - |  |  | Unknown | 2 | 60.0% | No |
| x_9 | float64 | - |  |  | Unknown | 2 | 60.0% | No |
| y_9 | float64 | - |  |  | Unknown | 2 | 60.0% | No |
| x_10 | float64 | - |  |  | Unknown | 1 | 80.0% | No |
| y_10 | float64 | - |  |  | Unknown | 1 | 80.0% | No |
| x_start | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| y_start | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| x_end | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| y_end | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| distance_traveled | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| distance_to_net_start | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| distance_to_net_end | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 5 | 0.0% | No |

---

## fact_playergames

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 14,471 |
| **Columns** | 4 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 14,471 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 14,471 | 0.0% | No |
| playergame_key | object | - |  |  | Unknown | 14,471 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 14,471 | 0.0% | No |

---

## fact_plays

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 2,202 |
| **Columns** | 39 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| play_key | object | - |  |  | Unknown | 2,202 | 0.0% | No |
| play_id | object | - |  |  | Unknown | 2,202 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 2,202 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 2,202 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 2,202 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 2,202 | 0.0% | No |
| sequence_key | object | - |  |  | Unknown | 2,202 | 0.0% | No |
| first_event_key | object | - |  |  | Unknown | 2,202 | 0.0% | No |
| last_event_key | object | - |  |  | Unknown | 2,202 | 0.0% | No |
| event_count | int64 | - |  |  | Unknown | 2,202 | 0.0% | No |
| start_min | float64 | - |  |  | Unknown | 2,199 | 0.1% | No |
| start_sec | float64 | - |  |  | Unknown | 2,199 | 0.1% | No |
| duration_seconds | float64 | - |  |  | Unknown | 2,202 | 0.0% | No |
| video_time_start | float64 | - |  |  | Unknown | 2,199 | 0.1% | No |
| video_time_end | float64 | - |  |  | Unknown | 2,201 | 0.0% | No |
| time_bucket_id | object | - |  |  | Unknown | 2,199 | 0.1% | No |
| strength_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_team | object | - |  |  | Unknown | 2,202 | 0.0% | No |
| home_team_id | object | - |  |  | Unknown | 2,202 | 0.0% | No |
| away_team | object | - |  |  | Unknown | 2,202 | 0.0% | No |
| away_team_id | object | - |  |  | Unknown | 2,202 | 0.0% | No |
| start_zone | object | - |  |  | Unknown | 2,202 | 0.0% | No |
| end_zone | object | - |  |  | Unknown | 2,202 | 0.0% | No |
| start_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| end_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_types | object | - |  |  | Unknown | 2,202 | 0.0% | No |
| has_goal | bool | - |  |  | Unknown | 2,202 | 0.0% | No |
| goal_count | int64 | - |  |  | Unknown | 2,202 | 0.0% | No |
| has_shot | bool | - |  |  | Unknown | 2,202 | 0.0% | No |
| shot_count | int64 | - |  |  | Unknown | 2,202 | 0.0% | No |
| zone_entry_count | int64 | - |  |  | Unknown | 2,202 | 0.0% | No |
| zone_exit_count | int64 | - |  |  | Unknown | 2,202 | 0.0% | No |
| pass_count | int64 | - |  |  | Unknown | 2,202 | 0.0% | No |
| pass_success_count | int64 | - |  |  | Unknown | 2,202 | 0.0% | No |
| turnover_count | int64 | - |  |  | Unknown | 2,202 | 0.0% | No |
| giveaway_count | int64 | - |  |  | Unknown | 2,202 | 0.0% | No |
| takeaway_count | int64 | - |  |  | Unknown | 2,202 | 0.0% | No |
| unique_player_count | int64 | - |  |  | Unknown | 2,202 | 0.0% | No |
| player_ids | object | - |  |  | Unknown | 2,181 | 1.0% | No |

---

## fact_possession_time

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 105 |
| **Columns** | 11 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| possession_key | object | - |  |  | Unknown | 105 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 105 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 105 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 105 | 0.0% | No |
| zone_entries | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| zone_exits | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| ozone_entries | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| dzone_entries | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| possession_events | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| estimated_possession_seconds | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| venue | object | - |  |  | Unknown | 105 | 0.0% | No |

---

## fact_puck_xy_long

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 12 |
| **Columns** | 9 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| puck_xy_key | object | - |  |  | Unknown | 12 | 0.0% | No |
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 12 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 12 | 0.0% | No |
| point_number | int64 | - |  |  | Unknown | 12 | 0.0% | No |
| x | float64 | - |  |  | Unknown | 12 | 0.0% | No |
| y | float64 | - |  |  | Unknown | 12 | 0.0% | No |
| distance_to_net | float64 | - |  |  | Unknown | 12 | 0.0% | No |
| angle_to_net | float64 | - |  |  | Unknown | 3 | 75.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 12 | 0.0% | No |

---

## fact_puck_xy_wide

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 2 |
| **Columns** | 33 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| puck_xy_key | object | - |  |  | Unknown | 2 | 0.0% | No |
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 2 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 2 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 2 | 0.0% | No |
| event_type | object | Type of event | Values: Shot, Goal, Pass, Faceoff, Hit, etc. |  | Explicit | 2 | 0.0% | No |
| event_detail | object | Detail/subtype of event | Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc. |  | Explicit | 2 | 0.0% | No |
| point_count | int64 | - |  |  | Unknown | 2 | 0.0% | No |
| x_1 | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| y_1 | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| x_2 | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| y_2 | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| x_3 | float64 | - |  |  | Unknown | 1 | 50.0% | No |
| y_3 | float64 | - |  |  | Unknown | 1 | 50.0% | No |
| x_4 | float64 | - |  |  | Unknown | 1 | 50.0% | No |
| y_4 | float64 | - |  |  | Unknown | 1 | 50.0% | No |
| x_5 | float64 | - |  |  | Unknown | 1 | 50.0% | No |
| y_5 | float64 | - |  |  | Unknown | 1 | 50.0% | No |
| x_6 | float64 | - |  |  | Unknown | 1 | 50.0% | No |
| y_6 | float64 | - |  |  | Unknown | 1 | 50.0% | No |
| x_7 | float64 | - |  |  | Unknown | 1 | 50.0% | No |
| y_7 | float64 | - |  |  | Unknown | 1 | 50.0% | No |
| x_8 | float64 | - |  |  | Unknown | 1 | 50.0% | No |
| y_8 | float64 | - |  |  | Unknown | 1 | 50.0% | No |
| x_9 | float64 | - |  |  | Unknown | 1 | 50.0% | No |
| y_9 | float64 | - |  |  | Unknown | 1 | 50.0% | No |
| x_10 | float64 | - |  |  | Unknown | 1 | 50.0% | No |
| y_10 | float64 | - |  |  | Unknown | 1 | 50.0% | No |
| x_start | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| y_start | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| x_end | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| y_end | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| distance_traveled | float64 | - |  |  | Unknown | 2 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 2 | 0.0% | No |

---

## fact_registration

| Property | Value |
|----------|-------|
| **Description** | Player season registration data |
| **Purpose** | Track player registration, draft status, skill ratings. |
| **Source Module** | `src/etl/processors/registration_processor.py:process()` |
| **Logic** | Direct load from registration spreadsheet |
| **Grain** | One row per player per season registration |
| **Rows** | 190 |
| **Columns** | 18 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| player_full_name | object | - |  |  | Unknown | 190 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 190 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 190 | 0.0% | No |
| season | int64 | - |  |  | Unknown | 190 | 0.0% | No |
| restricted | object | - |  |  | Unknown | 190 | 0.0% | No |
| email | object | - |  |  | Unknown | 190 | 0.0% | No |
| position | object | - |  |  | Unknown | 190 | 0.0% | No |
| norad_experience | object | - |  |  | Unknown | 190 | 0.0% | No |
| CAF | object | - |  |  | Unknown | 190 | 0.0% | No |
| highest_beer_league_played | object | - |  |  | Unknown | 172 | 9.5% | No |
| skill_rating | int64 | - |  |  | Unknown | 190 | 0.0% | No |
| age | int64 | - |  |  | Unknown | 190 | 0.0% | No |
| referred_by | object | - |  |  | Unknown | 189 | 0.5% | No |
| notes | object | - |  |  | Unknown | 10 | 94.7% | No |
| sub_yn | object | - |  |  | Unknown | 190 | 0.0% | No |
| drafted_team_name | object | - |  |  | Unknown | 190 | 0.0% | No |
| drafted_team_id | object | - |  |  | Unknown | 190 | 0.0% | No |
| player_season_registration_id | object | - |  |  | Unknown | 190 | 0.0% | No |

---

## fact_rush_events

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 206 |
| **Columns** | 9 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 206 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 206 | 0.0% | No |
| entry_event_index | object | - |  |  | Unknown | 206 | 0.0% | No |
| shot_event_index | object | - |  |  | Unknown | 206 | 0.0% | No |
| events_to_shot | int64 | - |  |  | Unknown | 206 | 0.0% | No |
| is_rush | bool | - |  |  | Unknown | 206 | 0.0% | No |
| entry_type | object | - |  |  | Unknown | 206 | 0.0% | No |
| rush_type | object | - |  |  | Unknown | 206 | 0.0% | No |
| is_goal | bool | - |  |  | Unknown | 206 | 0.0% | No |

---

## fact_rushes

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 421 |
| **Columns** | 122 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 421 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 421 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 421 | 0.0% | No |
| event_type | object | Type of event | Values: Shot, Goal, Pass, Faceoff, Hit, etc. |  | Explicit | 421 | 0.0% | No |
| event_type_id | object | - |  |  | Unknown | 421 | 0.0% | No |
| event_detail | object | Detail/subtype of event | Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc. |  | Explicit | 421 | 0.0% | No |
| event_detail_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_detail_2 | object | - |  |  | Unknown | 421 | 0.0% | No |
| event_detail_2_id | object | - |  |  | Unknown | 421 | 0.0% | No |
| event_successful | object | - |  |  | Unknown | 242 | 42.5% | No |
| success_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_team_zone | object | - |  |  | Unknown | 421 | 0.0% | No |
| event_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| sequence_key | object | - |  |  | Unknown | 421 | 0.0% | No |
| play_key | object | - |  |  | Unknown | 421 | 0.0% | No |
| event_chain_key | object | - |  |  | Unknown | 421 | 0.0% | No |
| tracking_event_key | object | - |  |  | Unknown | 421 | 0.0% | No |
| home_team | object | - |  |  | Unknown | 421 | 0.0% | No |
| home_team_id | object | - |  |  | Unknown | 421 | 0.0% | No |
| away_team | object | - |  |  | Unknown | 421 | 0.0% | No |
| away_team_id | object | - |  |  | Unknown | 421 | 0.0% | No |
| duration | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| event_player_ids | object | - |  |  | Unknown | 418 | 0.7% | No |
| opp_player_ids | object | - |  |  | Unknown | 305 | 27.6% | No |
| event_start_min | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| event_start_sec | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| event_end_min | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| event_end_sec | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| time_start_total_seconds | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| time_end_total_seconds | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| event_running_start | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| event_running_end | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| running_video_time | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| period_start_total_running_seconds | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| running_intermission_duration | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| team_venue | object | - |  |  | Unknown | 421 | 0.0% | No |
| team_venue_abv | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_team | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_team_zone | object | - |  |  | Unknown | 421 | 0.0% | No |
| away_team_zone | object | - |  |  | Unknown | 421 | 0.0% | No |
| player_role | object | - |  |  | Unknown | 421 | 0.0% | No |
| side_of_puck | object | - |  |  | Unknown | 421 | 0.0% | No |
| role_number | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| role_abrev | object | - |  |  | Unknown | 421 | 0.0% | No |
| player_game_number | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| strength | object | - |  |  | Unknown | 421 | 0.0% | No |
| play_detail1 | object | - |  |  | Unknown | 104 | 75.3% | No |
| play_detail_2 | object | - |  |  | Unknown | 24 | 94.3% | No |
| play_detail_successful | object | - |  |  | Unknown | 91 | 78.4% | No |
| pressured_pressurer | float64 | - |  |  | Unknown | 110 | 73.9% | No |
| is_goal | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_highlight | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 421 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 421 | 0.0% | No |
| position_id | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| shot_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_entry_type_id | object | - |  |  | Unknown | 277 | 34.2% | No |
| zone_exit_type_id | object | - |  |  | Unknown | 144 | 65.8% | No |
| stoppage_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| giveaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| takeaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| turnover_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| time_bucket_id | object | - |  |  | Unknown | 421 | 0.0% | No |
| strength_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_rating | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_rush | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_rebound | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_cycle | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_breakout | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_zone_entry | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_zone_exit | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_shot | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_save | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_turnover | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_giveaway | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_takeaway | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_faceoff | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_penalty | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_blocked_shot | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_missed_shot | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_deflected | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_sog | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| shot_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| save_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_outcome_id | object | - |  |  | Unknown | 421 | 0.0% | No |
| is_scoring_chance | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_high_danger | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| is_pressured | int64 | - |  |  | Unknown | 421 | 0.0% | No |
| danger_level | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| danger_level_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| scoring_chance_key | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| rush_key | object | - |  |  | Unknown | 421 | 0.0% | No |
| rush_outcome | object | - |  |  | Unknown | 421 | 0.0% | No |
| time_to_next_event | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| time_from_last_event | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| time_to_next_goal_for | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| time_to_next_goal_against | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| time_from_last_goal_for | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| time_from_last_goal_against | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| time_to_next_stoppage | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| time_from_last_stoppage | float64 | - |  |  | Unknown | 421 | 0.0% | No |
| event_player_1_toi | float64 | - |  |  | Unknown | 418 | 0.7% | No |
| event_player_2_toi | float64 | - |  |  | Unknown | 119 | 71.7% | No |
| event_player_3_toi | float64 | - |  |  | Unknown | 30 | 92.9% | No |
| event_player_4_toi | float64 | - |  |  | Unknown | 3 | 99.3% | No |
| event_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_1_toi | float64 | - |  |  | Unknown | 305 | 27.6% | No |
| opp_player_2_toi | float64 | - |  |  | Unknown | 172 | 59.1% | No |
| opp_player_3_toi | float64 | - |  |  | Unknown | 63 | 85.0% | No |
| opp_player_4_toi | float64 | - |  |  | Unknown | 7 | 98.3% | No |
| opp_player_5_toi | float64 | - |  |  | Unknown | 1 | 99.8% | No |
| opp_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| team_on_ice_toi_avg | float64 | - |  |  | Unknown | 418 | 0.7% | No |
| team_on_ice_toi_min | float64 | - |  |  | Unknown | 418 | 0.7% | No |
| team_on_ice_toi_max | float64 | - |  |  | Unknown | 418 | 0.7% | No |
| opp_on_ice_toi_avg | float64 | - |  |  | Unknown | 305 | 27.6% | No |
| opp_on_ice_toi_min | float64 | - |  |  | Unknown | 305 | 27.6% | No |
| opp_on_ice_toi_max | float64 | - |  |  | Unknown | 305 | 27.6% | No |

---

## fact_saves

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 213 |
| **Columns** | 121 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 213 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 213 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 213 | 0.0% | No |
| event_type | object | Type of event | Values: Shot, Goal, Pass, Faceoff, Hit, etc. |  | Explicit | 213 | 0.0% | No |
| event_type_id | object | - |  |  | Unknown | 213 | 0.0% | No |
| event_detail | object | Detail/subtype of event | Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc. |  | Explicit | 213 | 0.0% | No |
| event_detail_id | object | - |  |  | Unknown | 212 | 0.5% | No |
| event_detail_2 | object | - |  |  | Unknown | 213 | 0.0% | No |
| event_detail_2_id | object | - |  |  | Unknown | 213 | 0.0% | No |
| event_successful | object | - |  |  | Unknown | 3 | 98.6% | No |
| success_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_team_zone | object | - |  |  | Unknown | 213 | 0.0% | No |
| event_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| sequence_key | object | - |  |  | Unknown | 213 | 0.0% | No |
| play_key | object | - |  |  | Unknown | 213 | 0.0% | No |
| event_chain_key | object | - |  |  | Unknown | 213 | 0.0% | No |
| tracking_event_key | object | - |  |  | Unknown | 213 | 0.0% | No |
| home_team | object | - |  |  | Unknown | 213 | 0.0% | No |
| home_team_id | object | - |  |  | Unknown | 213 | 0.0% | No |
| away_team | object | - |  |  | Unknown | 213 | 0.0% | No |
| away_team_id | object | - |  |  | Unknown | 213 | 0.0% | No |
| duration | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| event_player_ids | object | - |  |  | Unknown | 213 | 0.0% | No |
| opp_player_ids | object | - |  |  | Unknown | 210 | 1.4% | No |
| event_start_min | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| event_start_sec | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| event_end_min | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| event_end_sec | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| time_start_total_seconds | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| time_end_total_seconds | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| event_running_start | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| event_running_end | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| running_video_time | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| period_start_total_running_seconds | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| running_intermission_duration | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| team_venue | object | - |  |  | Unknown | 213 | 0.0% | No |
| team_venue_abv | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_team | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_team_zone | object | - |  |  | Unknown | 213 | 0.0% | No |
| away_team_zone | object | - |  |  | Unknown | 213 | 0.0% | No |
| player_role | object | - |  |  | Unknown | 213 | 0.0% | No |
| side_of_puck | object | - |  |  | Unknown | 213 | 0.0% | No |
| role_number | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| role_abrev | object | - |  |  | Unknown | 213 | 0.0% | No |
| player_game_number | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| strength | object | - |  |  | Unknown | 213 | 0.0% | No |
| play_detail1 | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| play_detail_2 | object | - |  |  | Unknown | 2 | 99.1% | No |
| play_detail_successful | object | - |  |  | Unknown | 5 | 97.7% | No |
| pressured_pressurer | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| is_goal | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_highlight | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 213 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 213 | 0.0% | No |
| position_id | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| shot_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_entry_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_exit_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| stoppage_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| giveaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| takeaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| turnover_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| time_bucket_id | object | - |  |  | Unknown | 213 | 0.0% | No |
| strength_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_rating | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_rush | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_rebound | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_cycle | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_breakout | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_zone_entry | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_zone_exit | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_shot | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_save | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_turnover | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_giveaway | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_takeaway | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_faceoff | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_penalty | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_blocked_shot | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_missed_shot | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_deflected | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_sog | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| shot_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| save_outcome_id | object | - |  |  | Unknown | 213 | 0.0% | No |
| zone_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| is_scoring_chance | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_high_danger | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| is_pressured | int64 | - |  |  | Unknown | 213 | 0.0% | No |
| danger_level | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| danger_level_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| scoring_chance_key | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| save_key | object | - |  |  | Unknown | 213 | 0.0% | No |
| time_to_next_event | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| time_from_last_event | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| time_to_next_goal_for | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| time_to_next_goal_against | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| time_from_last_goal_for | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| time_from_last_goal_against | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| time_to_next_stoppage | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| time_from_last_stoppage | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| event_player_1_toi | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| event_player_2_toi | float64 | - |  |  | Unknown | 90 | 57.7% | No |
| event_player_3_toi | float64 | - |  |  | Unknown | 7 | 96.7% | No |
| event_player_4_toi | float64 | - |  |  | Unknown | 2 | 99.1% | No |
| event_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_1_toi | float64 | - |  |  | Unknown | 210 | 1.4% | No |
| opp_player_2_toi | float64 | - |  |  | Unknown | 26 | 87.8% | No |
| opp_player_3_toi | float64 | - |  |  | Unknown | 3 | 98.6% | No |
| opp_player_4_toi | float64 | - |  |  | Unknown | 1 | 99.5% | No |
| opp_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| team_on_ice_toi_avg | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| team_on_ice_toi_min | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| team_on_ice_toi_max | float64 | - |  |  | Unknown | 213 | 0.0% | No |
| opp_on_ice_toi_avg | float64 | - |  |  | Unknown | 210 | 1.4% | No |
| opp_on_ice_toi_min | float64 | - |  |  | Unknown | 210 | 1.4% | No |
| opp_on_ice_toi_max | float64 | - |  |  | Unknown | 210 | 1.4% | No |

---

## fact_scoring_chances

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 451 |
| **Columns** | 39 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| scoring_chance_key | object | - |  |  | Unknown | 451 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 451 | 0.0% | No |
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 451 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 451 | 0.0% | No |
| is_goal | bool | - |  |  | Unknown | 451 | 0.0% | No |
| event_detail | object | Detail/subtype of event | Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc. |  | Explicit | 451 | 0.0% | No |
| event_detail_2 | object | - |  |  | Unknown | 434 | 3.8% | No |
| danger_level | object | - |  |  | Unknown | 451 | 0.0% | No |
| is_rush | bool | - |  |  | Unknown | 451 | 0.0% | No |
| is_rebound | bool | - |  |  | Unknown | 451 | 0.0% | No |
| is_odd_man | bool | - |  |  | Unknown | 451 | 0.0% | No |
| shot_type | object | - |  |  | Unknown | 434 | 3.8% | No |
| time_to_next_event | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| time_from_last_event | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| time_to_next_goal_for | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| time_to_next_goal_against | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| time_from_last_goal_for | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| time_from_last_goal_against | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| time_to_next_stoppage | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| time_from_last_stoppage | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| event_player_1_toi | float64 | - |  |  | Unknown | 448 | 0.7% | No |
| event_player_2_toi | float64 | - |  |  | Unknown | 48 | 89.4% | No |
| event_player_3_toi | float64 | - |  |  | Unknown | 3 | 99.3% | No |
| event_player_4_toi | float64 | - |  |  | Unknown | 1 | 99.8% | No |
| event_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_1_toi | float64 | - |  |  | Unknown | 396 | 12.2% | No |
| opp_player_2_toi | float64 | - |  |  | Unknown | 118 | 73.8% | No |
| opp_player_3_toi | float64 | - |  |  | Unknown | 9 | 98.0% | No |
| opp_player_4_toi | float64 | - |  |  | Unknown | 1 | 99.8% | No |
| opp_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| team_on_ice_toi_avg | float64 | - |  |  | Unknown | 448 | 0.7% | No |
| team_on_ice_toi_min | float64 | - |  |  | Unknown | 448 | 0.7% | No |
| team_on_ice_toi_max | float64 | - |  |  | Unknown | 448 | 0.7% | No |
| opp_on_ice_toi_avg | float64 | - |  |  | Unknown | 396 | 12.2% | No |
| opp_on_ice_toi_min | float64 | - |  |  | Unknown | 396 | 12.2% | No |
| opp_on_ice_toi_max | float64 | - |  |  | Unknown | 396 | 12.2% | No |

---

## fact_scoring_chances_detailed

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 451 |
| **Columns** | 120 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 451 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 451 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 451 | 0.0% | No |
| event_type | object | Type of event | Values: Shot, Goal, Pass, Faceoff, Hit, etc. |  | Explicit | 451 | 0.0% | No |
| event_type_id | object | - |  |  | Unknown | 451 | 0.0% | No |
| event_detail | object | Detail/subtype of event | Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc. |  | Explicit | 451 | 0.0% | No |
| event_detail_id | object | - |  |  | Unknown | 433 | 4.0% | No |
| event_detail_2 | object | - |  |  | Unknown | 434 | 3.8% | No |
| event_detail_2_id | object | - |  |  | Unknown | 434 | 3.8% | No |
| event_successful | object | - |  |  | Unknown | 151 | 66.5% | No |
| success_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_team_zone | object | - |  |  | Unknown | 451 | 0.0% | No |
| event_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| sequence_key | object | - |  |  | Unknown | 451 | 0.0% | No |
| play_key | object | - |  |  | Unknown | 451 | 0.0% | No |
| event_chain_key | object | - |  |  | Unknown | 451 | 0.0% | No |
| tracking_event_key | object | - |  |  | Unknown | 451 | 0.0% | No |
| home_team | object | - |  |  | Unknown | 451 | 0.0% | No |
| home_team_id | object | - |  |  | Unknown | 451 | 0.0% | No |
| away_team | object | - |  |  | Unknown | 451 | 0.0% | No |
| away_team_id | object | - |  |  | Unknown | 451 | 0.0% | No |
| duration | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| event_player_ids | object | - |  |  | Unknown | 448 | 0.7% | No |
| opp_player_ids | object | - |  |  | Unknown | 396 | 12.2% | No |
| event_start_min | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| event_start_sec | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| event_end_min | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| event_end_sec | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| time_start_total_seconds | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| time_end_total_seconds | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| event_running_start | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| event_running_end | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| running_video_time | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| period_start_total_running_seconds | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| running_intermission_duration | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| team_venue | object | - |  |  | Unknown | 451 | 0.0% | No |
| team_venue_abv | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_team | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_team_zone | object | - |  |  | Unknown | 451 | 0.0% | No |
| away_team_zone | object | - |  |  | Unknown | 451 | 0.0% | No |
| player_role | object | - |  |  | Unknown | 451 | 0.0% | No |
| side_of_puck | object | - |  |  | Unknown | 451 | 0.0% | No |
| role_number | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| role_abrev | object | - |  |  | Unknown | 451 | 0.0% | No |
| player_game_number | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| strength | object | - |  |  | Unknown | 451 | 0.0% | No |
| play_detail1 | object | - |  |  | Unknown | 19 | 95.8% | No |
| play_detail_2 | object | - |  |  | Unknown | 12 | 97.3% | No |
| play_detail_successful | object | - |  |  | Unknown | 66 | 85.4% | No |
| pressured_pressurer | float64 | - |  |  | Unknown | 81 | 82.0% | No |
| is_goal | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_highlight | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 451 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 451 | 0.0% | No |
| position_id | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| shot_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_entry_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_exit_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| stoppage_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| giveaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| takeaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| turnover_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| time_bucket_id | object | - |  |  | Unknown | 451 | 0.0% | No |
| strength_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_rating | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_rush | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_rebound | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_cycle | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_breakout | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_zone_entry | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_zone_exit | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_shot | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_save | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_turnover | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_giveaway | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_takeaway | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_faceoff | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_penalty | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_blocked_shot | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_missed_shot | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_deflected | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_sog | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| shot_outcome_id | object | - |  |  | Unknown | 451 | 0.0% | No |
| pass_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| save_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| is_scoring_chance | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_high_danger | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_pressured | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| danger_level | object | - |  |  | Unknown | 451 | 0.0% | No |
| danger_level_id | object | - |  |  | Unknown | 451 | 0.0% | No |
| scoring_chance_key | object | - |  |  | Unknown | 451 | 0.0% | No |
| time_to_next_event | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| time_from_last_event | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| time_to_next_goal_for | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| time_to_next_goal_against | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| time_from_last_goal_for | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| time_from_last_goal_against | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| time_to_next_stoppage | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| time_from_last_stoppage | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| event_player_1_toi | float64 | - |  |  | Unknown | 448 | 0.7% | No |
| event_player_2_toi | float64 | - |  |  | Unknown | 48 | 89.4% | No |
| event_player_3_toi | float64 | - |  |  | Unknown | 3 | 99.3% | No |
| event_player_4_toi | float64 | - |  |  | Unknown | 1 | 99.8% | No |
| event_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_1_toi | float64 | - |  |  | Unknown | 396 | 12.2% | No |
| opp_player_2_toi | float64 | - |  |  | Unknown | 118 | 73.8% | No |
| opp_player_3_toi | float64 | - |  |  | Unknown | 9 | 98.0% | No |
| opp_player_4_toi | float64 | - |  |  | Unknown | 1 | 99.8% | No |
| opp_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| team_on_ice_toi_avg | float64 | - |  |  | Unknown | 448 | 0.7% | No |
| team_on_ice_toi_min | float64 | - |  |  | Unknown | 448 | 0.7% | No |
| team_on_ice_toi_max | float64 | - |  |  | Unknown | 448 | 0.7% | No |
| opp_on_ice_toi_avg | float64 | - |  |  | Unknown | 396 | 12.2% | No |
| opp_on_ice_toi_min | float64 | - |  |  | Unknown | 396 | 12.2% | No |
| opp_on_ice_toi_max | float64 | - |  |  | Unknown | 396 | 12.2% | No |

---

## fact_season_summary

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 1 |
| **Columns** | 10 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| season_summary_key | object | - |  |  | Unknown | 1 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 1 | 0.0% | No |
| games_tracked | int64 | - |  |  | Unknown | 1 | 0.0% | No |
| total_goals | int64 | - |  |  | Unknown | 1 | 0.0% | No |
| total_players | int64 | - |  |  | Unknown | 1 | 0.0% | No |
| avg_goals_per_game | float64 | - |  |  | Unknown | 1 | 0.0% | No |
| total_assists | int64 | - |  |  | Unknown | 1 | 0.0% | No |
| total_shots | int64 | - |  |  | Unknown | 1 | 0.0% | No |
| total_sog | int64 | - |  |  | Unknown | 1 | 0.0% | No |
| created_at | object | - |  |  | Unknown | 1 | 0.0% | No |

---

## fact_sequences

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 521 |
| **Columns** | 38 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| sequence_key | object | - |  |  | Unknown | 521 | 0.0% | No |
| sequence_id | object | - |  |  | Unknown | 521 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 521 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 521 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 521 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 521 | 0.0% | No |
| first_event_key | object | - |  |  | Unknown | 521 | 0.0% | No |
| last_event_key | object | - |  |  | Unknown | 521 | 0.0% | No |
| event_count | int64 | - |  |  | Unknown | 521 | 0.0% | No |
| start_min | float64 | - |  |  | Unknown | 518 | 0.6% | No |
| start_sec | float64 | - |  |  | Unknown | 518 | 0.6% | No |
| duration_seconds | float64 | - |  |  | Unknown | 521 | 0.0% | No |
| video_time_start | float64 | - |  |  | Unknown | 518 | 0.6% | No |
| video_time_end | float64 | - |  |  | Unknown | 520 | 0.2% | No |
| time_bucket_id | object | - |  |  | Unknown | 518 | 0.6% | No |
| strength_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_team | object | - |  |  | Unknown | 521 | 0.0% | No |
| home_team_id | object | - |  |  | Unknown | 521 | 0.0% | No |
| away_team | object | - |  |  | Unknown | 521 | 0.0% | No |
| away_team_id | object | - |  |  | Unknown | 521 | 0.0% | No |
| start_zone | object | - |  |  | Unknown | 521 | 0.0% | No |
| end_zone | object | - |  |  | Unknown | 521 | 0.0% | No |
| start_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| end_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_types | object | - |  |  | Unknown | 521 | 0.0% | No |
| has_goal | bool | - |  |  | Unknown | 521 | 0.0% | No |
| goal_count | int64 | - |  |  | Unknown | 521 | 0.0% | No |
| shot_count | int64 | - |  |  | Unknown | 521 | 0.0% | No |
| zone_entry_count | int64 | - |  |  | Unknown | 521 | 0.0% | No |
| zone_exit_count | int64 | - |  |  | Unknown | 521 | 0.0% | No |
| pass_count | int64 | - |  |  | Unknown | 521 | 0.0% | No |
| pass_success_count | int64 | - |  |  | Unknown | 521 | 0.0% | No |
| pass_success_rate | float64 | - |  |  | Unknown | 225 | 56.8% | No |
| turnover_count | int64 | - |  |  | Unknown | 521 | 0.0% | No |
| giveaway_count | int64 | - |  |  | Unknown | 521 | 0.0% | No |
| takeaway_count | int64 | - |  |  | Unknown | 521 | 0.0% | No |
| unique_player_count | int64 | - |  |  | Unknown | 521 | 0.0% | No |
| player_ids | object | - |  |  | Unknown | 521 | 0.0% | No |

---

## fact_shift_players

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 4,613 |
| **Columns** | 85 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| shift_player_id | object | - |  |  | Unknown | 4,613 | 0.0% | No |
| shift_id | object | - |  |  | Unknown | 4,613 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 4,613 | 0.0% | No |
| shift_index | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| player_game_number | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 4,551 | 1.3% | No |
| venue | object | - |  |  | Unknown | 4,613 | 0.0% | No |
| position | object | - |  |  | Unknown | 4,613 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| shift_duration | float64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| shift_start_total_seconds | float64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| shift_end_total_seconds | float64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| stoppage_time | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| playing_time | float64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| running_toi_game | float64 | - |  |  | Unknown | 4,551 | 1.3% | No |
| logical_shift_number | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| shift_segment | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| is_first_segment | bool | - |  |  | Unknown | 4,613 | 0.0% | No |
| is_last_segment | bool | - |  |  | Unknown | 4,613 | 0.0% | No |
| logical_shift_duration | float64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| gf | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| ga | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| pm | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| gf_ev | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| ga_ev | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| gf_pp | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| ga_pp | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| gf_pk | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| ga_pk | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| pm_ev | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| cf | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| ca | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| cf_pct | float64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| ff | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| fa | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| ff_pct | float64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| sf | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| sa | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| shot_diff | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| zone_entries | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| zone_exits | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| giveaways | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| takeaways | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| fo_won | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| fo_lost | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| situation | object | - |  |  | Unknown | 4,613 | 0.0% | No |
| situation_id | object | - |  |  | Unknown | 4,613 | 0.0% | No |
| strength | object | - |  |  | Unknown | 4,613 | 0.0% | No |
| strength_id | object | - |  |  | Unknown | 4,613 | 0.0% | No |
| start_zone | object | - |  |  | Unknown | 4,552 | 1.3% | No |
| end_zone | object | - |  |  | Unknown | 4,552 | 1.3% | No |
| player_rating | float64 | - |  |  | Unknown | 4,551 | 1.3% | No |
| team_avg_rating | float64 | - |  |  | Unknown | 4,611 | 0.0% | No |
| opp_avg_rating | float64 | - |  |  | Unknown | 4,611 | 0.0% | No |
| rating_differential | float64 | - |  |  | Unknown | 4,611 | 0.0% | No |
| qoc_rating | float64 | - |  |  | Unknown | 4,611 | 0.0% | No |
| qot_rating | float64 | - |  |  | Unknown | 4,611 | 0.0% | No |
| competition_tier_id | object | - |  |  | Unknown | 4,611 | 0.0% | No |
| opp_multiplier | float64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| player_rating_diff | float64 | - |  |  | Unknown | 4,549 | 1.4% | No |
| expected_cf_pct | float64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| cf_pct_vs_expected | float64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| performance | object | - |  |  | Unknown | 4,613 | 0.0% | No |
| cf_adj | float64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| ca_adj | float64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| cf_pct_adj | float64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| team_id | object | Team identifier | FK to dim_team.team_id | From roster or event data | FK | 4,613 | 0.0% | No |
| opp_team_id | object | - |  |  | Unknown | 4,613 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 4,613 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 4,613 | 0.0% | No |
| scf | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| sca | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| hdf | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| hda | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| event_count | int64 | - |  |  | Unknown | 4,613 | 0.0% | No |
| home_avg_rating | float64 | - |  |  | Unknown | 4,611 | 0.0% | No |
| away_avg_rating | float64 | - |  |  | Unknown | 4,611 | 0.0% | No |
| home_min_rating | float64 | - |  |  | Unknown | 4,611 | 0.0% | No |
| away_min_rating | float64 | - |  |  | Unknown | 4,611 | 0.0% | No |
| home_max_rating | float64 | - |  |  | Unknown | 4,611 | 0.0% | No |
| away_max_rating | float64 | - |  |  | Unknown | 4,611 | 0.0% | No |
| home_rating_advantage | bool | - |  |  | Unknown | 4,613 | 0.0% | No |
| home_team_id | object | - |  |  | Unknown | 4,613 | 0.0% | No |
| away_team_id | object | - |  |  | Unknown | 4,613 | 0.0% | No |
| shift_duration_id | object | - |  |  | Unknown | 4,613 | 0.0% | No |

---

## fact_shift_quality

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 4,551 |
| **Columns** | 9 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| shift_quality_key | object | - |  |  | Unknown | 4,551 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 4,551 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 4,551 | 0.0% | No |
| shift_index | int64 | - |  |  | Unknown | 4,551 | 0.0% | No |
| shift_duration | float64 | - |  |  | Unknown | 4,551 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 4,551 | 0.0% | No |
| quality_score | float64 | - |  |  | Unknown | 4,551 | 0.0% | No |
| shift_quality | object | - |  |  | Unknown | 4,551 | 0.0% | No |
| strength | object | - |  |  | Unknown | 4,551 | 0.0% | No |

---

## fact_shift_quality_logical

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 105 |
| **Columns** | 19 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 105 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 105 | 0.0% | No |
| logical_shifts | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| toi_seconds | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| avg_quality_score | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 105 | 0.0% | No |
| player_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| avg_opp_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| gf_all | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| ga_all | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| cf | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| ca | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| pm_all | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| toi_minutes | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| cf_pct | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| qoc | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| expected_pm | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| pm_vs_expected | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| performance | object | - |  |  | Unknown | 105 | 0.0% | No |

---

## fact_shifts

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 399 |
| **Columns** | 132 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| shift_id | object | - |  |  | Unknown | 399 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 399 | 0.0% | No |
| shift_index | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| shift_start_type | object | - |  |  | Unknown | 399 | 0.0% | No |
| shift_stop_type | object | - |  |  | Unknown | 130 | 67.4% | No |
| shift_start_min | float64 | - |  |  | Unknown | 392 | 1.8% | No |
| shift_start_sec | float64 | - |  |  | Unknown | 392 | 1.8% | No |
| shift_end_min | float64 | - |  |  | Unknown | 388 | 2.8% | No |
| shift_end_sec | float64 | - |  |  | Unknown | 388 | 2.8% | No |
| home_team | object | - |  |  | Unknown | 399 | 0.0% | No |
| away_team | object | - |  |  | Unknown | 399 | 0.0% | No |
| home_forward_1 | float64 | - |  |  | Unknown | 388 | 2.8% | No |
| home_forward_2 | float64 | - |  |  | Unknown | 383 | 4.0% | No |
| home_forward_3 | float64 | - |  |  | Unknown | 382 | 4.3% | No |
| home_defense_1 | float64 | - |  |  | Unknown | 388 | 2.8% | No |
| home_defense_2 | float64 | - |  |  | Unknown | 388 | 2.8% | No |
| home_xtra | float64 | - |  |  | Unknown | 2 | 99.5% | No |
| home_goalie | float64 | - |  |  | Unknown | 387 | 3.0% | No |
| away_forward_1 | float64 | - |  |  | Unknown | 388 | 2.8% | No |
| away_forward_2 | float64 | - |  |  | Unknown | 388 | 2.8% | No |
| away_forward_3 | float64 | - |  |  | Unknown | 362 | 9.3% | No |
| away_defense_1 | float64 | - |  |  | Unknown | 388 | 2.8% | No |
| away_defense_2 | float64 | - |  |  | Unknown | 388 | 2.8% | No |
| away_xtra | float64 | - |  |  | Unknown | 5 | 98.7% | No |
| away_goalie | float64 | - |  |  | Unknown | 383 | 4.0% | No |
| shift_duration | float64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_team_strength | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_team_strength | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_team_en | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_team_en | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_team_pk | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_team_pp | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_team_pp | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_team_pk | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| situation | object | - |  |  | Unknown | 399 | 0.0% | No |
| strength | object | - |  |  | Unknown | 399 | 0.0% | No |
| home_goals | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_goals | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| stoppage_time | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| shift_start_total_seconds | float64 | - |  |  | Unknown | 399 | 0.0% | No |
| shift_end_total_seconds | float64 | - |  |  | Unknown | 399 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 399 | 0.0% | No |
| home_team_id | object | - |  |  | Unknown | 399 | 0.0% | No |
| away_team_id | object | - |  |  | Unknown | 399 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 399 | 0.0% | No |
| time_bucket_id | object | - |  |  | Unknown | 392 | 1.8% | No |
| strength_id | object | - |  |  | Unknown | 399 | 0.0% | No |
| shift_start_type_derived | object | - |  |  | Unknown | 399 | 0.0% | No |
| shift_stop_type_derived | object | - |  |  | Unknown | 399 | 0.0% | No |
| start_zone | object | - |  |  | Unknown | 390 | 2.3% | No |
| end_zone | object | - |  |  | Unknown | 390 | 2.3% | No |
| start_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| end_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_forward_1_id | object | - |  |  | Unknown | 384 | 3.8% | No |
| home_forward_2_id | object | - |  |  | Unknown | 383 | 4.0% | No |
| home_forward_3_id | object | - |  |  | Unknown | 382 | 4.3% | No |
| home_defense_1_id | object | - |  |  | Unknown | 379 | 5.0% | No |
| home_defense_2_id | object | - |  |  | Unknown | 356 | 10.8% | No |
| home_xtra_id | object | - |  |  | Unknown | 2 | 99.5% | No |
| home_goalie_id | object | - |  |  | Unknown | 387 | 3.0% | No |
| away_forward_1_id | object | - |  |  | Unknown | 388 | 2.8% | No |
| away_forward_2_id | object | - |  |  | Unknown | 388 | 2.8% | No |
| away_forward_3_id | object | - |  |  | Unknown | 362 | 9.3% | No |
| away_defense_1_id | object | - |  |  | Unknown | 377 | 5.5% | No |
| away_defense_2_id | object | - |  |  | Unknown | 382 | 4.3% | No |
| away_xtra_id | object | - |  |  | Unknown | 5 | 98.7% | No |
| away_goalie_id | object | - |  |  | Unknown | 383 | 4.0% | No |
| home_avg_rating | float64 | - |  |  | Unknown | 388 | 2.8% | No |
| home_min_rating | float64 | - |  |  | Unknown | 388 | 2.8% | No |
| home_max_rating | float64 | - |  |  | Unknown | 388 | 2.8% | No |
| away_avg_rating | float64 | - |  |  | Unknown | 388 | 2.8% | No |
| away_min_rating | float64 | - |  |  | Unknown | 388 | 2.8% | No |
| away_max_rating | float64 | - |  |  | Unknown | 388 | 2.8% | No |
| rating_differential | float64 | - |  |  | Unknown | 388 | 2.8% | No |
| home_rating_advantage | bool | - |  |  | Unknown | 399 | 0.0% | No |
| home_gf_all | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_ga_all | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_gf_all | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_ga_all | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_gf_ev | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_ga_ev | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_gf_ev | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_ga_ev | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_gf_nen | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_ga_nen | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_gf_nen | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_ga_nen | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_gf_pp | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_ga_pp | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_gf_pp | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_ga_pp | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_gf_pk | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_ga_pk | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_gf_pk | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_ga_pk | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_pm_all | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_pm_all | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_pm_ev | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_pm_ev | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_pm_nen | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_pm_nen | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_pm_pp | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_pm_pp | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| home_pm_pk | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| away_pm_pk | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| sf | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| sa | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| shot_diff | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| cf | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| ca | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| cf_pct | float64 | - |  |  | Unknown | 399 | 0.0% | No |
| ff | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| fa | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| ff_pct | float64 | - |  |  | Unknown | 399 | 0.0% | No |
| scf | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| sca | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| hdf | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| hda | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| zone_entries | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| zone_exits | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| giveaways | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| takeaways | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| fo_won | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| fo_lost | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| fo_pct | float64 | - |  |  | Unknown | 399 | 0.0% | No |
| event_count | int64 | - |  |  | Unknown | 399 | 0.0% | No |
| shift_start_type_id | object | - |  |  | Unknown | 399 | 0.0% | No |
| shift_stop_type_id | object | - |  |  | Unknown | 399 | 0.0% | No |
| situation_id | object | - |  |  | Unknown | 399 | 0.0% | No |
| shift_key | object | - |  |  | Unknown | 399 | 0.0% | No |
| shift_duration_id | object | - |  |  | Unknown | 399 | 0.0% | No |

---

## fact_shot_danger

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 451 |
| **Columns** | 11 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| shot_danger_key | object | - |  |  | Unknown | 451 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 451 | 0.0% | No |
| event_index | object | - |  |  | Unknown | 451 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 451 | 0.0% | No |
| danger_zone | object | - |  |  | Unknown | 451 | 0.0% | No |
| xg | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_rebound | bool | - |  |  | Unknown | 451 | 0.0% | No |
| is_rush | bool | - |  |  | Unknown | 451 | 0.0% | No |
| is_one_timer | bool | - |  |  | Unknown | 451 | 0.0% | No |
| shot_distance | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| shot_angle | float64 | - |  |  | Unknown | 0 | 100.0% | No |

---

## fact_shot_event

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 451 |
| **Columns** | 23 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| shot_event_key | object | - |  |  | Unknown | 451 | 0.0% | No |
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 451 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 451 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| event_type | object | Type of event | Values: Shot, Goal, Pass, Faceoff, Hit, etc. |  | Explicit | 451 | 0.0% | No |
| event_detail | object | Detail/subtype of event | Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc. |  | Explicit | 451 | 0.0% | No |
| is_goal | bool | - |  |  | Unknown | 451 | 0.0% | No |
| shooter_player_id | object | - |  |  | Unknown | 446 | 1.1% | No |
| shooter_name | object | - |  |  | Unknown | 446 | 1.1% | No |
| shooter_team_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| shot_x | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| shot_y | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| shot_distance | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| shot_angle | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| friendly_screen_score | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| own_team_screen_score | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| total_screen_score | float64 | - |  |  | Unknown | 451 | 0.0% | No |
| screen_count | int64 | - |  |  | Unknown | 451 | 0.0% | No |
| is_screened | bool | - |  |  | Unknown | 451 | 0.0% | No |
| net_target_x | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| net_target_y | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| net_location_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 451 | 0.0% | No |

---

## fact_shot_players

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 1,036 |
| **Columns** | 23 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| shot_player_key | object | - |  |  | Unknown | 1,036 | 0.0% | No |
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 1,036 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 1,036 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 1,025 | 1.1% | No |
| player_name | object | - |  |  | Unknown | 1,025 | 1.1% | No |
| player_role | object | - |  |  | Unknown | 1,036 | 0.0% | No |
| is_shooter_team | bool | - |  |  | Unknown | 1,036 | 0.0% | No |
| is_shooter | bool | - |  |  | Unknown | 1,036 | 0.0% | No |
| player_x | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_y | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| distance_to_shooter | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| distance_to_puck | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| distance_to_net | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| is_in_vision_cone | bool | - |  |  | Unknown | 1,036 | 0.0% | No |
| is_in_puck_path | bool | - |  |  | Unknown | 1,036 | 0.0% | No |
| distance_to_goalie | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| distance_to_shot_path | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| angular_coverage_degrees | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| distance_factor | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| screen_score | float64 | - |  |  | Unknown | 1,036 | 0.0% | No |
| is_screening | bool | - |  |  | Unknown | 1,036 | 0.0% | No |
| screen_type | object | - |  |  | Unknown | 1,036 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 1,036 | 0.0% | No |

---

## fact_shot_xy

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 0 |
| **Columns** | 12 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| shot_xy_key | object | - |  |  | Unknown | 0 | 0% | No |
| game_id | object | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 0 | 0% | No |
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 0 | 0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 0 | 0% | No |
| shot_x | object | - |  |  | Unknown | 0 | 0% | No |
| shot_y | object | - |  |  | Unknown | 0 | 0% | No |
| target_x | object | - |  |  | Unknown | 0 | 0% | No |
| target_y | object | - |  |  | Unknown | 0 | 0% | No |
| distance | object | - |  |  | Unknown | 0 | 0% | No |
| angle | object | - |  |  | Unknown | 0 | 0% | No |
| danger_zone | object | - |  |  | Unknown | 0 | 0% | No |
| _export_timestamp | object | - |  |  | Unknown | 0 | 0% | No |

---

## fact_special_teams_summary

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 105 |
| **Columns** | 9 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| special_teams_key | object | - |  |  | Unknown | 105 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 105 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 105 | 0.0% | No |
| pp_toi | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| pk_toi | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| ev_toi | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| pp_shifts | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| pk_shifts | int64 | - |  |  | Unknown | 105 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 105 | 0.0% | No |

---

## fact_suspicious_stats

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 7 |
| **Columns** | 8 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| suspicious_key | object | - |  |  | Unknown | 7 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 7 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 7 | 0.0% | No |
| flags | object | - |  |  | Unknown | 7 | 0.0% | No |
| goals | int64 | Goals scored |  | COUNT(*) WHERE event_type='Goal' AND event_detail='Goal_Scored' | Calculated | 7 | 0.0% | No |
| shots | int64 | - |  |  | Unknown | 7 | 0.0% | No |
| toi_minutes | float64 | - |  |  | Unknown | 7 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 7 | 0.0% | No |

---

## fact_team_game_stats

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 8 |
| **Columns** | 39 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| team_game_key | object | - |  |  | Unknown | 8 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 8 | 0.0% | No |
| team_id | object | Team identifier | FK to dim_team.team_id | From roster or event data | FK | 8 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 8 | 0.0% | No |
| team_name | object | - |  |  | Unknown | 8 | 0.0% | No |
| goals | int64 | Goals scored |  | COUNT(*) WHERE event_type='Goal' AND event_detail='Goal_Scored' | Calculated | 8 | 0.0% | No |
| assists | int64 | Assists (primary + secondary) |  | COUNT(*) WHERE player is event_player_2 or event_player_3 on goal events | Calculated | 8 | 0.0% | No |
| points | int64 | Total points |  | goals + assists | Calculated | 8 | 0.0% | No |
| shots | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| sog | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| shots_blocked | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| shots_missed | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| pass_attempts | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| pass_completed | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| fo_wins | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| fo_losses | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| fo_total | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| zone_entries | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| zone_exits | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| controlled_entries | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| controlled_exits | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| giveaways | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| takeaways | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| blocks | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| hits | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| toi_seconds | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| corsi_for | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| corsi_against | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| plus_ev | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| minus_ev | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| shooting_pct | float64 | - |  |  | Unknown | 8 | 0.0% | No |
| pass_pct | float64 | - |  |  | Unknown | 8 | 0.0% | No |
| fo_pct | float64 | - |  |  | Unknown | 8 | 0.0% | No |
| controlled_entry_pct | float64 | - |  |  | Unknown | 8 | 0.0% | No |
| turnover_diff | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| cf_pct | float64 | - |  |  | Unknown | 8 | 0.0% | No |
| plus_minus | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| avg_player_rating | float64 | - |  |  | Unknown | 8 | 0.0% | No |
| total_game_score | float64 | - |  |  | Unknown | 8 | 0.0% | No |

---

## fact_team_season_stats

| Property | Value |
|----------|-------|
| **Description** | Team statistics aggregated per season |
| **Purpose** | Team standings, team comparison, season summaries. |
| **Source Module** | `src/etl/processors/team_stats_processor.py:process()` |
| **Logic** | Aggregate from fact_events + fact_gameroster grouped by team_id + season_id |
| **Grain** | One row per team per season |
| **Rows** | 5 |
| **Columns** | 39 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| team_id | object | Team identifier | FK to dim_team.team_id | From roster or event data | FK | 5 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 5 | 0.0% | No |
| goals | int64 | Goals scored |  | COUNT(*) WHERE event_type='Goal' AND event_detail='Goal_Scored' | Calculated | 5 | 0.0% | No |
| assists | int64 | Assists (primary + secondary) |  | COUNT(*) WHERE player is event_player_2 or event_player_3 on goal events | Calculated | 5 | 0.0% | No |
| points | int64 | Total points |  | goals + assists | Calculated | 5 | 0.0% | No |
| shots | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| sog | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| shots_blocked | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| shots_missed | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| pass_attempts | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| pass_completed | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| fo_wins | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| fo_losses | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| fo_total | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| zone_entries | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| zone_exits | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| controlled_entries | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| controlled_exits | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| giveaways | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| takeaways | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| blocks | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| hits | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| toi_seconds | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| corsi_for | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| corsi_against | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| plus_ev | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| minus_ev | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| shooting_pct | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| pass_pct | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| fo_pct | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| controlled_entry_pct | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| turnover_diff | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| cf_pct | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| plus_minus | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| avg_player_rating | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| total_game_score | float64 | - |  |  | Unknown | 5 | 0.0% | No |
| games_played | int64 | Number of games played |  | COUNT(DISTINCT game_id) | Calculated | 5 | 0.0% | No |
| team_season_key | object | - |  |  | Unknown | 5 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 5 | 0.0% | No |

---

## fact_team_standings_snapshot

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 5 |
| **Columns** | 10 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| standings_key | object | - |  |  | Unknown | 5 | 0.0% | No |
| team_id | object | Team identifier | FK to dim_team.team_id | From roster or event data | FK | 5 | 0.0% | No |
| games_played | int64 | Number of games played |  | COUNT(DISTINCT game_id) | Calculated | 5 | 0.0% | No |
| wins | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| losses | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| points | int64 | Total points |  | goals + assists | Calculated | 5 | 0.0% | No |
| goals_for | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| goals_against | int64 | - |  |  | Unknown | 5 | 0.0% | No |
| snapshot_date | object | - |  |  | Unknown | 5 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 5 | 0.0% | No |

---

## fact_team_zone_time

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 8 |
| **Columns** | 8 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| zone_time_key | object | - |  |  | Unknown | 8 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 8 | 0.0% | No |
| venue | object | - |  |  | Unknown | 8 | 0.0% | No |
| offensive_zone_events | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| neutral_zone_events | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| defensive_zone_events | int64 | - |  |  | Unknown | 8 | 0.0% | No |
| oz_pct | float64 | - |  |  | Unknown | 8 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 8 | 0.0% | No |

---

## fact_tracking

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 5,823 |
| **Columns** | 25 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| tracking_event_key | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 5,823 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 5,823 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| event_start_min | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| event_start_sec | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| event_end_min | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| event_end_sec | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| time_start_total_seconds | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| time_end_total_seconds | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| running_video_time | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| event_running_start | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| event_running_end | float64 | - |  |  | Unknown | 5,818 | 0.1% | No |
| event_team_zone | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| event_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_team_zone | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| home_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| away_team_zone | object | - |  |  | Unknown | 5,823 | 0.0% | No |
| away_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| x_coord | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| y_coord | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| rink_zone | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 5,823 | 0.0% | No |
| time_bucket_id | object | - |  |  | Unknown | 5,818 | 0.1% | No |
| strength_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |

---

## fact_turnovers_detailed

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 744 |
| **Columns** | 95 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 744 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 744 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 744 | 0.0% | No |
| event_type | object | Type of event | Values: Shot, Goal, Pass, Faceoff, Hit, etc. |  | Explicit | 744 | 0.0% | No |
| event_type_id | object | - |  |  | Unknown | 744 | 0.0% | No |
| event_detail | object | Detail/subtype of event | Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc. |  | Explicit | 735 | 1.2% | No |
| event_detail_id | object | - |  |  | Unknown | 735 | 1.2% | No |
| event_detail_2 | object | - |  |  | Unknown | 734 | 1.3% | No |
| event_detail_2_id | object | - |  |  | Unknown | 734 | 1.3% | No |
| event_successful | object | - |  |  | Unknown | 63 | 91.5% | No |
| success_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_team_zone | object | - |  |  | Unknown | 744 | 0.0% | No |
| event_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| sequence_key | object | - |  |  | Unknown | 744 | 0.0% | No |
| play_key | object | - |  |  | Unknown | 744 | 0.0% | No |
| event_chain_key | object | - |  |  | Unknown | 744 | 0.0% | No |
| tracking_event_key | object | - |  |  | Unknown | 744 | 0.0% | No |
| home_team | object | - |  |  | Unknown | 744 | 0.0% | No |
| home_team_id | object | - |  |  | Unknown | 744 | 0.0% | No |
| away_team | object | - |  |  | Unknown | 744 | 0.0% | No |
| away_team_id | object | - |  |  | Unknown | 744 | 0.0% | No |
| duration | float64 | - |  |  | Unknown | 744 | 0.0% | No |
| event_player_ids | object | - |  |  | Unknown | 727 | 2.3% | No |
| opp_player_ids | object | - |  |  | Unknown | 390 | 47.6% | No |
| event_start_min | float64 | - |  |  | Unknown | 744 | 0.0% | No |
| event_start_sec | float64 | - |  |  | Unknown | 744 | 0.0% | No |
| event_end_min | float64 | - |  |  | Unknown | 744 | 0.0% | No |
| event_end_sec | float64 | - |  |  | Unknown | 744 | 0.0% | No |
| time_start_total_seconds | float64 | - |  |  | Unknown | 744 | 0.0% | No |
| time_end_total_seconds | float64 | - |  |  | Unknown | 744 | 0.0% | No |
| event_running_start | float64 | - |  |  | Unknown | 744 | 0.0% | No |
| event_running_end | float64 | - |  |  | Unknown | 744 | 0.0% | No |
| running_video_time | float64 | - |  |  | Unknown | 744 | 0.0% | No |
| period_start_total_running_seconds | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| running_intermission_duration | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| team_venue | object | - |  |  | Unknown | 744 | 0.0% | No |
| team_venue_abv | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_team | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_team_zone | object | - |  |  | Unknown | 744 | 0.0% | No |
| away_team_zone | object | - |  |  | Unknown | 744 | 0.0% | No |
| player_role | object | - |  |  | Unknown | 744 | 0.0% | No |
| side_of_puck | object | - |  |  | Unknown | 744 | 0.0% | No |
| role_number | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| role_abrev | object | - |  |  | Unknown | 744 | 0.0% | No |
| player_game_number | float64 | - |  |  | Unknown | 744 | 0.0% | No |
| strength | object | - |  |  | Unknown | 744 | 0.0% | No |
| play_detail1 | object | - |  |  | Unknown | 181 | 75.7% | No |
| play_detail_2 | object | - |  |  | Unknown | 24 | 96.8% | No |
| play_detail_successful | object | - |  |  | Unknown | 195 | 73.8% | No |
| pressured_pressurer | float64 | - |  |  | Unknown | 151 | 79.7% | No |
| is_goal | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_highlight | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 735 | 1.2% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 744 | 0.0% | No |
| position_id | float64 | - |  |  | Unknown | 735 | 1.2% | No |
| shot_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_entry_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_exit_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| stoppage_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| giveaway_type_id | object | - |  |  | Unknown | 602 | 19.1% | No |
| takeaway_type_id | object | - |  |  | Unknown | 133 | 82.1% | No |
| turnover_type_id | object | - |  |  | Unknown | 735 | 1.2% | No |
| pass_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| time_bucket_id | object | - |  |  | Unknown | 744 | 0.0% | No |
| strength_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_rating | float64 | - |  |  | Unknown | 735 | 1.2% | No |
| is_rush | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_rebound | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_cycle | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_breakout | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_zone_entry | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_zone_exit | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_shot | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_save | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_turnover | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_giveaway | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_takeaway | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_faceoff | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_penalty | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_blocked_shot | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_missed_shot | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_deflected | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_sog | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| shot_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| save_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| is_scoring_chance | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_high_danger | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| is_pressured | int64 | - |  |  | Unknown | 744 | 0.0% | No |
| danger_level | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| danger_level_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| scoring_chance_key | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| turnover_key_new | object | - |  |  | Unknown | 744 | 0.0% | No |

---

## fact_video

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 0 |
| **Columns** | 8 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| video_key | object | - |  |  | Unknown | 0 | 0% | No |
| game_id | object | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 0 | 0% | No |
| video_url | object | - |  |  | Unknown | 0 | 0% | No |
| duration_seconds | object | - |  |  | Unknown | 0 | 0% | No |
| period_1_start | object | - |  |  | Unknown | 0 | 0% | No |
| period_2_start | object | - |  |  | Unknown | 0 | 0% | No |
| period_3_start | object | - |  |  | Unknown | 0 | 0% | No |
| _export_timestamp | object | - |  |  | Unknown | 0 | 0% | No |

---

## fact_wowy

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 621 |
| **Columns** | 20 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| wowy_key | object | - |  |  | Unknown | 621 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 621 | 0.0% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 621 | 0.0% | No |
| player_1_id | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| player_2_id | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| venue | object | - |  |  | Unknown | 621 | 0.0% | No |
| shifts_together | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| toi_together | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| p1_shifts_without_p2 | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| p2_shifts_without_p1 | int64 | - |  |  | Unknown | 621 | 0.0% | No |
| toi_apart | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| toi_p1_without_p2 | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| toi_p2_without_p1 | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| cf_pct_together | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| cf_pct_apart | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| cf_pct_delta | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| gf_pct_together | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| gf_pct_apart | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| gf_pct_delta | float64 | - |  |  | Unknown | 621 | 0.0% | No |
| relative_corsi | float64 | - |  |  | Unknown | 621 | 0.0% | No |

---

## fact_zone_entries

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 510 |
| **Columns** | 122 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 510 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 510 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 510 | 0.0% | No |
| event_type | object | Type of event | Values: Shot, Goal, Pass, Faceoff, Hit, etc. |  | Explicit | 510 | 0.0% | No |
| event_type_id | object | - |  |  | Unknown | 510 | 0.0% | No |
| event_detail | object | Detail/subtype of event | Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc. |  | Explicit | 510 | 0.0% | No |
| event_detail_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_detail_2 | object | - |  |  | Unknown | 510 | 0.0% | No |
| event_detail_2_id | object | - |  |  | Unknown | 510 | 0.0% | No |
| event_successful | object | - |  |  | Unknown | 218 | 57.3% | No |
| success_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_team_zone | object | - |  |  | Unknown | 510 | 0.0% | No |
| event_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| sequence_key | object | - |  |  | Unknown | 510 | 0.0% | No |
| play_key | object | - |  |  | Unknown | 510 | 0.0% | No |
| event_chain_key | object | - |  |  | Unknown | 510 | 0.0% | No |
| tracking_event_key | object | - |  |  | Unknown | 510 | 0.0% | No |
| home_team | object | - |  |  | Unknown | 510 | 0.0% | No |
| home_team_id | object | - |  |  | Unknown | 510 | 0.0% | No |
| away_team | object | - |  |  | Unknown | 510 | 0.0% | No |
| away_team_id | object | - |  |  | Unknown | 510 | 0.0% | No |
| duration | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| event_player_ids | object | - |  |  | Unknown | 506 | 0.8% | No |
| opp_player_ids | object | - |  |  | Unknown | 337 | 33.9% | No |
| event_start_min | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| event_start_sec | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| event_end_min | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| event_end_sec | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| time_start_total_seconds | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| time_end_total_seconds | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| event_running_start | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| event_running_end | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| running_video_time | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| period_start_total_running_seconds | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| running_intermission_duration | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| team_venue | object | - |  |  | Unknown | 510 | 0.0% | No |
| team_venue_abv | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_team | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_team_zone | object | - |  |  | Unknown | 510 | 0.0% | No |
| away_team_zone | object | - |  |  | Unknown | 510 | 0.0% | No |
| player_role | object | - |  |  | Unknown | 510 | 0.0% | No |
| side_of_puck | object | - |  |  | Unknown | 510 | 0.0% | No |
| role_number | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| role_abrev | object | - |  |  | Unknown | 510 | 0.0% | No |
| player_game_number | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| strength | object | - |  |  | Unknown | 510 | 0.0% | No |
| play_detail1 | object | - |  |  | Unknown | 130 | 74.5% | No |
| play_detail_2 | object | - |  |  | Unknown | 27 | 94.7% | No |
| play_detail_successful | object | - |  |  | Unknown | 117 | 77.1% | No |
| pressured_pressurer | float64 | - |  |  | Unknown | 120 | 76.5% | No |
| is_goal | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_highlight | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 508 | 0.4% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 510 | 0.0% | No |
| position_id | float64 | - |  |  | Unknown | 508 | 0.4% | No |
| shot_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_entry_type_id | object | - |  |  | Unknown | 510 | 0.0% | No |
| zone_exit_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| stoppage_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| giveaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| takeaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| turnover_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| time_bucket_id | object | - |  |  | Unknown | 510 | 0.0% | No |
| strength_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_rating | float64 | - |  |  | Unknown | 508 | 0.4% | No |
| is_rush | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_rebound | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_cycle | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_breakout | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_zone_entry | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_zone_exit | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_shot | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_save | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_turnover | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_giveaway | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_takeaway | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_faceoff | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_penalty | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_blocked_shot | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_missed_shot | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_deflected | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_sog | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| shot_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| save_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_outcome_id | object | - |  |  | Unknown | 510 | 0.0% | No |
| is_scoring_chance | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_high_danger | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| is_pressured | int64 | - |  |  | Unknown | 510 | 0.0% | No |
| danger_level | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| danger_level_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| scoring_chance_key | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_entry_key | object | - |  |  | Unknown | 510 | 0.0% | No |
| entry_method | object | - |  |  | Unknown | 510 | 0.0% | No |
| time_to_next_event | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| time_from_last_event | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| time_to_next_goal_for | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| time_to_next_goal_against | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| time_from_last_goal_for | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| time_from_last_goal_against | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| time_to_next_stoppage | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| time_from_last_stoppage | float64 | - |  |  | Unknown | 510 | 0.0% | No |
| event_player_1_toi | float64 | - |  |  | Unknown | 506 | 0.8% | No |
| event_player_2_toi | float64 | - |  |  | Unknown | 171 | 66.5% | No |
| event_player_3_toi | float64 | - |  |  | Unknown | 31 | 93.9% | No |
| event_player_4_toi | float64 | - |  |  | Unknown | 4 | 99.2% | No |
| event_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_1_toi | float64 | - |  |  | Unknown | 337 | 33.9% | No |
| opp_player_2_toi | float64 | - |  |  | Unknown | 178 | 65.1% | No |
| opp_player_3_toi | float64 | - |  |  | Unknown | 65 | 87.3% | No |
| opp_player_4_toi | float64 | - |  |  | Unknown | 7 | 98.6% | No |
| opp_player_5_toi | float64 | - |  |  | Unknown | 1 | 99.8% | No |
| opp_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| team_on_ice_toi_avg | float64 | - |  |  | Unknown | 506 | 0.8% | No |
| team_on_ice_toi_min | float64 | - |  |  | Unknown | 506 | 0.8% | No |
| team_on_ice_toi_max | float64 | - |  |  | Unknown | 506 | 0.8% | No |
| opp_on_ice_toi_avg | float64 | - |  |  | Unknown | 337 | 33.9% | No |
| opp_on_ice_toi_min | float64 | - |  |  | Unknown | 337 | 33.9% | No |
| opp_on_ice_toi_max | float64 | - |  |  | Unknown | 337 | 33.9% | No |

---

## fact_zone_entry_summary

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 100 |
| **Columns** | 9 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| zone_entry_key | object | - |  |  | Unknown | 100 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 100 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 100 | 0.0% | No |
| total_entries | int64 | - |  |  | Unknown | 100 | 0.0% | No |
| controlled_entries | int64 | - |  |  | Unknown | 100 | 0.0% | No |
| dump_entries | int64 | - |  |  | Unknown | 100 | 0.0% | No |
| failed_entries | int64 | - |  |  | Unknown | 100 | 0.0% | No |
| entry_success_rate | float64 | - |  |  | Unknown | 100 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 100 | 0.0% | No |

---

## fact_zone_exit_summary

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 100 |
| **Columns** | 9 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| zone_exit_key | object | - |  |  | Unknown | 100 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 100 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 100 | 0.0% | No |
| total_exits | int64 | - |  |  | Unknown | 100 | 0.0% | No |
| controlled_exits | int64 | - |  |  | Unknown | 100 | 0.0% | No |
| clear_exits | int64 | - |  |  | Unknown | 100 | 0.0% | No |
| failed_exits | int64 | - |  |  | Unknown | 100 | 0.0% | No |
| exit_success_rate | float64 | - |  |  | Unknown | 100 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 100 | 0.0% | No |

---

## fact_zone_exits

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 488 |
| **Columns** | 122 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| event_id | object | Unique event identifier |  | Generated sequence per game | Derived | 488 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 488 | 0.0% | No |
| period | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| period_id | object | - |  |  | Unknown | 488 | 0.0% | No |
| event_type | object | Type of event | Values: Shot, Goal, Pass, Faceoff, Hit, etc. |  | Explicit | 488 | 0.0% | No |
| event_type_id | object | - |  |  | Unknown | 488 | 0.0% | No |
| event_detail | object | Detail/subtype of event | Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc. |  | Explicit | 488 | 0.0% | No |
| event_detail_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_detail_2 | object | - |  |  | Unknown | 487 | 0.2% | No |
| event_detail_2_id | object | - |  |  | Unknown | 487 | 0.2% | No |
| event_successful | object | - |  |  | Unknown | 229 | 53.1% | No |
| success_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_team_zone | object | - |  |  | Unknown | 488 | 0.0% | No |
| event_zone_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| sequence_key | object | - |  |  | Unknown | 488 | 0.0% | No |
| play_key | object | - |  |  | Unknown | 488 | 0.0% | No |
| event_chain_key | object | - |  |  | Unknown | 488 | 0.0% | No |
| tracking_event_key | object | - |  |  | Unknown | 488 | 0.0% | No |
| home_team | object | - |  |  | Unknown | 488 | 0.0% | No |
| home_team_id | object | - |  |  | Unknown | 488 | 0.0% | No |
| away_team | object | - |  |  | Unknown | 488 | 0.0% | No |
| away_team_id | object | - |  |  | Unknown | 488 | 0.0% | No |
| duration | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| event_player_ids | object | - |  |  | Unknown | 480 | 1.6% | No |
| opp_player_ids | object | - |  |  | Unknown | 162 | 66.8% | No |
| event_start_min | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| event_start_sec | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| event_end_min | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| event_end_sec | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| time_start_total_seconds | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| time_end_total_seconds | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| event_running_start | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| event_running_end | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| running_video_time | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| period_start_total_running_seconds | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| running_intermission_duration | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| team_venue | object | - |  |  | Unknown | 488 | 0.0% | No |
| team_venue_abv | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_team | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| home_team_zone | object | - |  |  | Unknown | 488 | 0.0% | No |
| away_team_zone | object | - |  |  | Unknown | 488 | 0.0% | No |
| player_role | object | - |  |  | Unknown | 485 | 0.6% | No |
| side_of_puck | object | - |  |  | Unknown | 485 | 0.6% | No |
| role_number | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| role_abrev | object | - |  |  | Unknown | 485 | 0.6% | No |
| player_game_number | float64 | - |  |  | Unknown | 485 | 0.6% | No |
| strength | object | - |  |  | Unknown | 488 | 0.0% | No |
| play_detail1 | object | - |  |  | Unknown | 83 | 83.0% | No |
| play_detail_2 | object | - |  |  | Unknown | 13 | 97.3% | No |
| play_detail_successful | object | - |  |  | Unknown | 85 | 82.6% | No |
| pressured_pressurer | float64 | - |  |  | Unknown | 58 | 88.1% | No |
| is_goal | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_highlight | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| player_name | object | - |  |  | Unknown | 482 | 1.2% | No |
| season_id | object | Season identifier | FK to dim_season.season_id | From schedule data | FK | 488 | 0.0% | No |
| position_id | float64 | - |  |  | Unknown | 482 | 1.2% | No |
| shot_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_entry_type_id | object | - |  |  | Unknown | 5 | 99.0% | No |
| zone_exit_type_id | object | - |  |  | Unknown | 482 | 1.2% | No |
| stoppage_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| giveaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| takeaway_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| turnover_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_type_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| time_bucket_id | object | - |  |  | Unknown | 488 | 0.0% | No |
| strength_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| player_rating | float64 | - |  |  | Unknown | 482 | 1.2% | No |
| is_rush | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_rebound | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_cycle | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_breakout | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_zone_entry | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_zone_exit | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_shot | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_save | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_turnover | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_giveaway | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_takeaway | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_faceoff | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_penalty | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_blocked_shot | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_missed_shot | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_deflected | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_sog | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| shot_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| pass_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| save_outcome_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_outcome_id | object | - |  |  | Unknown | 488 | 0.0% | No |
| is_scoring_chance | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_high_danger | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| is_pressured | int64 | - |  |  | Unknown | 488 | 0.0% | No |
| danger_level | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| danger_level_id | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| scoring_chance_key | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| zone_exit_key | object | - |  |  | Unknown | 488 | 0.0% | No |
| exit_method | object | - |  |  | Unknown | 488 | 0.0% | No |
| time_to_next_event | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| time_from_last_event | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| time_to_next_goal_for | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| time_to_next_goal_against | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| time_from_last_goal_for | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| time_from_last_goal_against | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| time_to_next_stoppage | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| time_from_last_stoppage | float64 | - |  |  | Unknown | 488 | 0.0% | No |
| event_player_1_toi | float64 | - |  |  | Unknown | 480 | 1.6% | No |
| event_player_2_toi | float64 | - |  |  | Unknown | 160 | 67.2% | No |
| event_player_3_toi | float64 | - |  |  | Unknown | 2 | 99.6% | No |
| event_player_4_toi | float64 | - |  |  | Unknown | 1 | 99.8% | No |
| event_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| event_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_1_toi | float64 | - |  |  | Unknown | 162 | 66.8% | No |
| opp_player_2_toi | float64 | - |  |  | Unknown | 15 | 96.9% | No |
| opp_player_3_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_4_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_5_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| opp_player_6_toi | float64 | - |  |  | Unknown | 0 | 100.0% | No |
| team_on_ice_toi_avg | float64 | - |  |  | Unknown | 480 | 1.6% | No |
| team_on_ice_toi_min | float64 | - |  |  | Unknown | 480 | 1.6% | No |
| team_on_ice_toi_max | float64 | - |  |  | Unknown | 480 | 1.6% | No |
| opp_on_ice_toi_avg | float64 | - |  |  | Unknown | 162 | 66.8% | No |
| opp_on_ice_toi_min | float64 | - |  |  | Unknown | 162 | 66.8% | No |
| opp_on_ice_toi_max | float64 | - |  |  | Unknown | 162 | 66.8% | No |

---

## lookup_player_game_rating

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 105 |
| **Columns** | 6 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 105 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 105 | 0.0% | No |
| avg_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| avg_opp_rating | float64 | - |  |  | Unknown | 105 | 0.0% | No |
| lookup_key | object | - |  |  | Unknown | 105 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 105 | 0.0% | No |

---

## qa_data_completeness

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 4 |
| **Columns** | 7 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| qa_key | object | - |  |  | Unknown | 4 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 4 | 0.0% | No |
| has_events | bool | - |  |  | Unknown | 4 | 0.0% | No |
| has_shifts | bool | - |  |  | Unknown | 4 | 0.0% | No |
| has_rosters | bool | - |  |  | Unknown | 4 | 0.0% | No |
| is_complete | bool | - |  |  | Unknown | 4 | 0.0% | No |
| check_date | object | - |  |  | Unknown | 4 | 0.0% | No |

---

## qa_goal_accuracy

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 4 |
| **Columns** | 10 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| qa_key | object | - |  |  | Unknown | 4 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 4 | 0.0% | No |
| game_date | object | - |  |  | Unknown | 4 | 0.0% | No |
| home_team | object | - |  |  | Unknown | 4 | 0.0% | No |
| away_team | object | - |  |  | Unknown | 4 | 0.0% | No |
| expected_goals | int64 | - |  |  | Unknown | 4 | 0.0% | No |
| actual_goals | int64 | - |  |  | Unknown | 4 | 0.0% | No |
| match | bool | - |  |  | Unknown | 4 | 0.0% | No |
| difference | int64 | - |  |  | Unknown | 4 | 0.0% | No |
| check_date | object | - |  |  | Unknown | 4 | 0.0% | No |

---

## qa_scorer_comparison

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 4 |
| **Columns** | 8 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| comparison_key | object | - |  |  | Unknown | 4 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 4 | 0.0% | No |
| metric | object | - |  |  | Unknown | 4 | 0.0% | No |
| events_value | int64 | - |  |  | Unknown | 4 | 0.0% | No |
| stats_value | int64 | - |  |  | Unknown | 4 | 0.0% | No |
| match | bool | - |  |  | Unknown | 4 | 0.0% | No |
| difference | int64 | - |  |  | Unknown | 4 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 4 | 0.0% | No |

---

## qa_suspicious_stats

| Property | Value |
|----------|-------|
| **Description** | No description |
| **Purpose** | - |
| **Source Module** | `Unknown` |
| **Logic** | - |
| **Grain** | - |
| **Rows** | 7 |
| **Columns** | 8 |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
| suspicious_key | object | - |  |  | Unknown | 7 | 0.0% | No |
| game_id | int64 | Game identifier | FK to dim_game.game_id | From schedule or tracking data | FK | 7 | 0.0% | No |
| player_id | object | Player identifier | FK to dim_player.player_id. Format P######. | Lookup from player name in dim_player | FK | 7 | 0.0% | No |
| flags | object | - |  |  | Unknown | 7 | 0.0% | No |
| goals | int64 | Goals scored |  | COUNT(*) WHERE event_type='Goal' AND event_detail='Goal_Scored' | Calculated | 7 | 0.0% | No |
| shots | int64 | - |  |  | Unknown | 7 | 0.0% | No |
| toi_minutes | float64 | - |  |  | Unknown | 7 | 0.0% | No |
| _export_timestamp | object | - |  |  | Unknown | 7 | 0.0% | No |

---
