# Gap Analysis - BenchSight ETL

## Legend
- ✅ Complete and validated
- ⚠️ Partial/needs work
- ❌ Not started or broken
- 🔲 Schema only, no data

## Core ETL Pipeline

| Component | Status | Notes |
|-----------|--------|-------|
| Event extraction | ✅ | 11,635 events from 4 games |
| Shift extraction | ✅ | 4,626 shifts with durations |
| Player dimension | ✅ | Loaded from BLB |
| Team dimension | ✅ | Loaded from BLB |
| Schedule dimension | ✅ | Game metadata |
| Video URL linking | ✅ | YouTube multi-angle URLs |

## Calculated Stats

| Stat | Status | Notes |
|------|--------|-------|
| Plus/Minus (Traditional) | ✅ | Validated vs noradhockey.com |
| Plus/Minus (All Situations) | ✅ | Includes PP/PK |
| Plus/Minus (EN Adjusted) | ⚠️ | Works but no EN goals in test data |
| Goals/Assists | ✅ | Per-game and totals |
| TOI | ✅ | By player, by game |
| Shifts count | ✅ | Logical shift counts |
| Corsi | ⚠️ | Calculated but not validated |
| xG | ⚠️ | Simplified model, needs refinement |

## Derived Tables

| Table | Status | Rows | Issues |
|-------|--------|------|--------|
| fact_sequences | ✅ | 1,088 | Play chains complete |
| fact_plays | ✅ | 2,714 | Play chains complete |
| fact_rush_events | ✅ | 199 | All FKs populated |
| fact_cycle_events | ⚠️ | 9 | Only game 18969 has data |
| fact_linked_events | ✅ | 473 | Play chains + venue_id |
| fact_h2h | ⚠️ | 684 | Stats need validation |
| fact_wowy | ⚠️ | 641 | Stats need validation |
| fact_line_combos | ❌ | 332 | Stats were broken, removed |
| fact_goalie_game_stats | ✅ | 8 | Per-game goalie stats |
| fact_possession_time | ⚠️ | 107 | Zone dependency |

## XY Coordinate Tables

| Table | Status | Notes |
|-------|--------|-------|
| fact_player_xy_long | 🔲 | Schema ready, 15 columns |
| fact_player_xy_wide | 🔲 | Schema ready, 49 columns |
| fact_puck_xy_long | 🔲 | Schema ready, 12 columns |
| fact_puck_xy_wide | 🔲 | Schema ready, 55 columns |
| fact_shot_xy | 🔲 | Schema ready, 28 columns |
| dim_net_location | ✅ | 10 target zones |
| dim_rink_coord | ✅ | 19 rink zones |

## Foreign Key Fill Rates

| Table | Key FKs | Fill Rate |
|-------|---------|-----------|
| fact_events_player | event_type_id, team_id, period_id | >95% |
| fact_events_player | zone_id | 38% (source data issue) |
| fact_events_player | success_id | 20% (only some events) |
| fact_shifts_player | All 6 FKs | 100% |
| fact_sequences | first/last_event_key, team_id | 100% |
| fact_plays | first/last_event_key, team_id | 100% |
| fact_linked_events | venue_id | 99.7% |

## Infrastructure

| Component | Status | Notes |
|-----------|--------|-------|
| Supabase schema | ❌ | Not deployed |
| PostgreSQL DDL | ⚠️ | In sql/ but not tested |
| Power BI model | ⚠️ | Sample measures exist |
| Incremental load | ❌ | Full rebuild only |
| Error handling | ⚠️ | Basic try/except |
| Logging | ⚠️ | Print statements mostly |
| Unit tests | ❌ | Only integration validations |

## Data Quality

| Metric | Game 18969 | Game 18977 | Game 18981 | Game 18987 |
|--------|------------|------------|------------|------------|
| event_team_zone | 86.8% | 0% | 41.4% | 11.5% |
| event_detail | 82% | 82% | 82% | 82% |
| success_id | 20% | 20% | 20% | 20% |
| Cycles detected | 9 | 0 | 0 | 0 |

## Gaps to Close (Priority Order)

### P0 - Critical
1. **Line combo stats**: Recalculate correctly
2. **Supabase deployment**: Get data into production DB

### P1 - Important
3. **XY data population**: When coordinate data available
4. **More test games**: Expand beyond 4 games
5. **Zone data investigation**: Why is tracking inconsistent?

### P2 - Nice to Have
6. **Unit tests**: For individual transforms
7. **Incremental processing**: Don't rebuild everything
8. **Better logging**: Structured logging with levels
9. **xG model refinement**: Use actual shot location data
