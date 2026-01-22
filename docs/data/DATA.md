# BenchSight Data Reference

**Complete data lineage, table manifest, and data structure reference**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This document provides complete reference for all data tables in BenchSight, including their sources, lineage, structure, and relationships.

**Current Table Count:** 132 tables (verified 2026-01-15)  
**Expected Minimum:** 138 tables (per `run_etl.py` EXPECTED_TABLE_COUNT)  
**Documented Range:** 132-139 tables (varies by ETL version and data availability)  
**Source Categories:** BLB Tables, Tracking Files, Calculated, Static Reference, QA

**Note:** Current count (132) is below expected minimum (138). This may be due to conditional table creation based on data availability or version differences. See [DOCUMENTATION_VERIFICATION_SUMMARY.md](../DOCUMENTATION_VERIFICATION_SUMMARY.md) for details.

**Related Documentation:**
- [DATA_DICTIONARY.md](DATA_DICTIONARY.md) - **NEW** Comprehensive data dictionary with column-level details, calculations, and sources
- [SCHEMA_ERD.md](SCHEMA_ERD.md) - **NEW** Visual Entity-Relationship Diagrams of the database schema
- [SCHEMA_SCALABILITY_DESIGN.md](SCHEMA_SCALABILITY_DESIGN.md) - **NEW** Multi-tenant schema design and scalability patterns
- [CALCULATION_FLOWS.md](CALCULATION_FLOWS.md) - **NEW** Visual calculation flow diagrams (xG, WAR/GAR, Corsi)

---

## Table of Contents

1. [Source Summary](#source-summary)
2. [BLB Tables (Direct Loads)](#blb-tables-direct-loads)
3. [Tracking Tables](#tracking-tables)
4. [Static Reference Tables](#static-reference-tables)
5. [Calculated/Derived Tables](#calculatedderived-tables)
6. [QA Tables](#qa-tables)
7. [ETL Phase Summary](#etl-phase-summary)
8. [Dependency Graph](#dependency-graph)
9. [Critical Business Rules](#critical-business-rules)
10. [Table Manifest](#table-manifest)

---

## Source Summary

| Source | Count | Description |
|--------|-------|-------------|
| 📊 BLB | 16-17 | Direct from BLB_Tables.xlsx |
| 🎮 TRK | 5 | From tracking Excel files |
| 📌 STATIC | 19-25 | Hardcoded constants |
| 🧮 CALC | 84+ | Calculated/derived |
| 🔍 QA | 4 | Validation tables |
| **TOTAL** | **132-139** | |

### Source Type Legend

| Code | Meaning | Example |
|------|---------|---------|
| 📊 BLB | Direct load from BLB_Tables.xlsx sheet | dim_player |
| 🎮 TRK | Derived from tracking Excel files | fact_events |
| 🧮 CALC | Calculated from other tables | fact_player_game_stats |
| 📌 STATIC | Hardcoded constants | dim_period |
| 🔍 QA | Quality assurance checks | qa_goal_verification |

---

## BLB Tables (Direct Loads)

**Source:** `data/raw/BLB_Tables.xlsx`  
**ETL Phase:** Phase 1 (`load_blb_tables()`)  
**Code:** `src/core/base_etl.py` lines 864-936

| Table | Sheet Name | Rows | Cols | Primary Key | Notes |
|-------|------------|------|------|-------------|-------|
| dim_player | dim_player | 337 | 28 | player_id | Master player list |
| dim_team | dim_team | 26 | 15 | team_id | Team definitions |
| dim_league | dim_league | 2 | 3 | league_id | NORAD, CSAH |
| dim_season | dim_season | 9 | 9 | season_id | Season definitions |
| dim_schedule | dim_schedule | 567 | 45 | game_id | All scheduled games |
| dim_playerurlref | dim_playerurlref | 550 | 6 | - | Player URL references |
| dim_randomnames | dim_randomnames | 486 | 6 | - | Random name generator |
| dim_event_type | dim_event_type | 23 | 7 | event_type_id | Event type codes |
| dim_event_detail | dim_event_detail | 49 | 11 | event_detail_id | Event detail codes |
| dim_event_detail_2 | dim_event_detail_2 | 176 | 12 | event_detail_2_id | Secondary event details |
| dim_play_detail | dim_play_detail | 111 | 6 | play_detail_id | Play detail codes |
| dim_play_detail_2 | dim_play_detail_2 | 111 | 6 | play_detail_2_id | Secondary play details |
| fact_gameroster | fact_gameroster | 14,597 | 27 | (game_id, player_id) | Game rosters with stats |
| fact_leadership | fact_leadership | 28 | 10 | - | Team leadership |
| fact_registration | fact_registration | 191 | 19 | player_season_registration_id | Season registrations |
| fact_draft | fact_draft | 160 | 15 | player_draft_id | Draft records |

### BLB Sheets NOT Loaded (intentionally skipped)

| Sheet | Reason |
|-------|--------|
| dim_rinkboxcoord | Loaded separately or unused |
| dim_rinkcoordzones | Loaded separately or unused |
| Fact_PlayerGames | Redundant with fact_gameroster |

---

## Tracking Tables

**Source:** `data/raw/{game_id}_tracking.xlsx` (events + shifts sheets)  
**ETL Phase:** Phase 3 (`process_tracking_files()`)  
**Code:** `src/core/base_etl.py` lines 1000-1200

### Core Tracking Tables

| Table | Source | Logic | Rows | Primary Key |
|-------|--------|-------|------|-------------|
| fact_events | tracking.xlsx → events sheet | Raw events, cleaned and standardized | ~5,800 | event_id |
| fact_shifts | tracking.xlsx → shifts sheet | Player shift data | ~400 | shift_id |
| fact_event_players | fact_events expanded | One row per event-player combo | ~11,000 | event_player_id |
| fact_shift_players | fact_shifts expanded | One row per shift-player combo | ~2,000 | shift_player_id |
| fact_tracking | fact_events + metadata | Tracking summary per game | 4 | game_id |

### Event-Derived Tables

| Table | Source | Filter/Logic | Code Location |
|-------|--------|--------------|---------------|
| fact_scoring_chances | fact_events | event_type IN (Shot, Goal) with danger zones | base_etl.py:3183 |
| fact_scoring_chances_detailed | fact_events | Extended scoring chance metrics | base_etl.py:3183 |
| fact_high_danger_chances | fact_scoring_chances | danger_level = 'high' | base_etl.py:3189 |
| fact_shots | fact_events | event_type = 'Shot' | calculated |
| fact_goals | fact_events | event_type = 'Goal' AND event_detail = 'Goal_Scored' | calculated |
| fact_saves | fact_events | event_type = 'Shot' AND outcome = 'saved' | base_etl.py:3195 |
| fact_rushes | fact_events | event_type = 'Rush' | base_etl.py:3142 |
| fact_breakouts | fact_events | event_type = 'Breakout' | base_etl.py:3164 |
| fact_zone_entries | fact_events | event_type = 'Zone_Entry_Exit' with entry logic | base_etl.py:3171 |
| fact_zone_exits | fact_events | event_type = 'Zone_Entry_Exit' with exit logic | base_etl.py:3178 |
| fact_faceoffs | fact_events | event_type = 'Faceoff' | base_etl.py:3208 |
| fact_penalties | fact_events | event_type = 'Penalty' | base_etl.py:3214 |
| fact_turnovers_detailed | fact_events | event_type IN (Giveaway, Takeaway) | base_etl.py:3201 |

### Sequence/Play Tables

| Table | Source | Logic | Code Location |
|-------|--------|-------|---------------|
| fact_sequences | fact_events | Linked event sequences | base_etl.py:2876 |
| fact_plays | fact_sequences | Play-level aggregations | base_etl.py:2981 |

---

## Static Reference Tables

**Source:** Hardcoded in ETL  
**ETL Phase:** Phase 3B (`create_all_dimension_tables()`)  
**Code:** `src/tables/dimension_tables.py`

| Table | Rows | Cols | Notes |
|-------|------|------|-------|
| dim_danger_level | 3 | 4 | Low/Medium/High |
| dim_giveaway_type | 16 | 3 | Giveaway types |
| dim_pass_type | 8 | 4 | Pass type codes |
| dim_period | 5 | 5 | Period definitions (P1-P5) |
| dim_player_role | 14 | 5 | Event player roles |
| dim_position | 6 | 4 | Position codes (F/D/G/X) |
| dim_shift_duration | 5 | 7 | Shift duration buckets |
| dim_shift_start_type | 9 | 2 | How shift started |
| dim_shift_stop_type | 18 | 2 | How shift ended |
| dim_shot_type | 6 | 4 | Shot type codes |
| dim_situation | 4 | 2 | Game situations |
| dim_stoppage_type | 4 | 3 | Stoppage types |
| dim_strength | 18 | 7 | Game strength states |
| dim_success | 3 | 4 | Success outcome codes |
| dim_takeaway_type | 2 | 3 | Takeaway types |
| dim_venue | 2 | 4 | Home/Away |
| dim_zone | 3 | 4 | Zone codes (O/N/D) |
| dim_zone_entry_type | 12 | 3 | Zone entry types |
| dim_zone_exit_type | 10 | 3 | Zone exit types |

### Dynamically Generated Reference Tables

| Table | Source | Logic |
|-------|--------|-------|
| dim_comparison_type | Calculated | Comparison types for analytics |
| dim_competition_tier | Calculated | Competition tier levels |
| dim_composite_rating | Calculated | Composite rating levels |
| dim_danger_zone | Calculated | Ice danger zones |
| dim_game_state | Calculated | Game state definitions |
| dim_micro_stat | Calculated | Micro stat definitions |
| dim_net_location | Calculated | Net location codes |
| dim_pass_outcome | Calculated | Pass outcome types |
| dim_rating | Calculated | Rating levels |
| dim_rating_matchup | Calculated | Rating matchup types |
| dim_rink_zone | Calculated | Rink zone grid (201 zones) |
| dim_save_outcome | Calculated | Save outcome types |
| dim_shift_quality_tier | Calculated | Shift quality tiers |
| dim_shift_slot | Calculated | Shift slot positions |
| dim_shot_outcome | Calculated | Shot outcome types |
| dim_stat | Calculated | Stat definitions |
| dim_stat_category | Calculated | Stat category groupings |
| dim_stat_type | Calculated | Stat type classifications |
| dim_terminology_mapping | Calculated | Terminology mappings |
| dim_time_bucket | Calculated | Time bucket definitions |
| dim_turnover_quality | Calculated | Turnover quality levels |
| dim_turnover_type | Calculated | Turnover type classifications |
| dim_zone_outcome | Calculated | Zone outcome types |
| dim_video_type | Calculated | Video type definitions |
| dim_highlight_category | Calculated | Highlight category types |

---

## Calculated/Derived Tables

**Source:** Other fact tables + aggregation logic  
**ETL Phase:** Phase 4-10

### Player Statistics

| Table | Source Tables | Aggregation | Code Location |
|-------|---------------|-------------|---------------|
| fact_player_game_stats | fact_events, fact_shifts | Per-game player stats | core_facts.py |
| fact_player_season_stats | fact_player_game_stats | Seasonal rollup | core_facts.py |
| fact_player_career_stats | fact_player_season_stats | Career totals | core_facts.py |
| fact_player_period_stats | fact_events | Per-period breakdown | core_facts.py |
| fact_player_situation_stats | fact_events | By game situation (5v5, PP, PK) | core_facts.py |
| fact_player_micro_stats | fact_events | Micro statistics | core_facts.py |
| fact_player_pair_stats | fact_events, fact_shifts | Player pair statistics | shift_analytics.py |
| fact_player_stats_by_competition_tier | fact_player_game_stats | By competition tier | remaining_facts.py |
| fact_player_stats_long | fact_player_game_stats | Long format stats | remaining_facts.py |
| fact_player_trends | fact_player_game_stats | Player trends | remaining_facts.py |
| fact_player_boxscore_all | fact_player_game_stats | Boxscore format | remaining_facts.py |
| fact_player_game_position | fact_events | Position by game | remaining_facts.py |
| fact_player_position_splits | fact_player_game_stats | Position splits | remaining_facts.py |
| fact_player_qoc_summary | fact_events | Quality of competition | remaining_facts.py |
| fact_player_event_chains | fact_events | Event chain statistics | event_analytics.py |

### Team Statistics

| Table | Source Tables | Aggregation |
|-------|---------------|-------------|
| fact_team_game_stats | fact_player_game_stats | Team totals per game |
| fact_team_season_stats | fact_team_game_stats | Season team totals |
| fact_team_standings_snapshot | fact_team_season_stats | Standings snapshot |
| fact_team_zone_time | fact_events | Zone time by team |

### Goalie Statistics

| Table | Source Tables | Aggregation |
|-------|---------------|-------------|
| fact_goalie_game_stats | fact_events, fact_saves | Per-game goalie stats |

### Matchup/Comparison Tables

| Table | Source Tables | Purpose |
|-------|---------------|---------|
| fact_player_matchups | fact_events | Head-to-head player stats |
| fact_player_matchups_xy | fact_events + XY | Spatial matchup data |
| fact_line_matchups | fact_shifts | Line combination stats |
| fact_h2h | fact_events | Head-to-head records |
| fact_head_to_head | fact_events | Head-to-head detailed |
| fact_matchup_performance | fact_events | Matchup performance metrics |
| fact_matchup_summary | fact_events | Matchup summary |
| fact_wowy | fact_events, fact_shifts | With or Without You stats |

### Shift Analytics

| Table | Source Tables | Purpose |
|-------|---------------|---------|
| fact_shift_quality | fact_shifts | Shift quality metrics |
| fact_shift_quality_logical | fact_shifts | Shift quality logical tiers |
| fact_line_combos | fact_shifts | Line combination statistics |

### XY/Spatial Tables

| Table | Source | Purpose | Code |
|-------|--------|---------|------|
| fact_puck_xy_wide | fact_events | Puck position (wide format) | xy_table_builder.py |
| fact_puck_xy_long | fact_events | Puck position (long format) | xy_table_builder.py |
| fact_player_xy_wide | fact_events | Player positions (wide) | xy_table_builder.py |
| fact_player_xy_long | fact_events | Player positions (long) | xy_table_builder.py |
| fact_player_puck_proximity | fact_events | Distance calculations | xy_table_builder.py |
| fact_shot_event | fact_events | Shot-specific XY | xy_table_builder.py |
| fact_shot_players | fact_events | Players on ice for shots | xy_table_builder.py |
| fact_shot_xy | fact_events | Shot XY coordinates | xy_table_builder.py |

### Game-Level Tables

| Table | Source Tables | Purpose |
|-------|---------------|---------|
| fact_game_status | Multiple fact tables | Game tracking completion status |
| fact_season_summary | Multiple | Season summary |
| fact_period_momentum | fact_events | Period momentum |
| fact_special_teams_summary | fact_events | Special teams summary |
| fact_league_leaders_snapshot | fact_player_season_stats | League leaders snapshot |

### Event Analytics

| Table | Source Tables | Purpose |
|-------|---------------|---------|
| fact_event_chains | fact_events | Event chain sequences |
| fact_sequences | fact_events | Linked event sequences |
| fact_plays | fact_sequences | Play-level aggregations |

### Lookup Tables

| Table | Source | Purpose |
|-------|--------|---------|
| lookup_player_game_rating | fact_player_game_stats | Player game ratings |
| fact_playergames | fact_gameroster | Player games lookup |

### Macro Statistics

| Table | Source | Purpose |
|-------|--------|---------|
| fact_suspicious_stats | fact_player_game_stats | Suspicious stat flags |

---

## QA Tables

**Source:** Validation checks on other tables  
**ETL Phase:** Phase 9 (Validation)  
**Code:** `src/qa/build_qa_facts.py`

| Table | Purpose | Logic |
|-------|---------|-------|
| qa_goal_verification | Verify goal counts match | Compare fact_events goals to official |
| qa_data_completeness | Check for missing data | NULL counts, required fields |
| qa_suspicious_stats | Flag anomalies | Outlier detection |
| qa_foreign_key_check | Validate relationships | FK integrity checks |
| qa_goal_accuracy | Goal accuracy verification | Goal count validation |
| qa_scorer_comparison | Scorer comparison | Scorer validation |

---

## ETL Phase Summary

| Phase | Name | Tables Created | Code |
|-------|------|----------------|------|
| 1 | Base ETL (BLB + Tracking) | ~22 | base_etl.py |
| 3B | Static Dimension Tables | ~25 | dimension_tables.py |
| 4 | Core Player Stats | ~15 | core_facts.py |
| 4B | Shift Analytics | ~10 | shift_analytics.py |
| 4C | Remaining Fact Tables | ~30 | remaining_facts.py |
| 4D | Event Analytics | ~10 | event_analytics.py |
| 4E | Shot Chains | ~2 | shot_chain_builder.py |
| 5 | Foreign Keys & Additional | ~5 | add_all_fkeys.py |
| 6 | Extended Tables | ~10 | extended_tables.py |
| 7 | Post Processing | ~5 | post_etl_processor.py |
| 8 | Event Time Context | ~5 | event_time_context.py |
| 9 | QA Tables | ~4 | build_qa_facts.py |
| 10 | V11 Enhancements | ~5 | v11_enhancements.py |
| 10B | XY Tables | ~8 | xy_table_builder.py |
| 11 | Macro Stats | ~5 | macro_stats.py |

**Total:** 132-139 tables (varies by ETL version and data availability)

---

## Dependency Graph

```
BLB_Tables.xlsx
├── dim_player ──────────────────────┐
├── dim_team ────────────────────────┤
├── dim_schedule ────────────────────┼──► fact_gameroster (enhanced)
├── dim_season ──────────────────────┤
├── dim_event_type ──────────────────┤
├── dim_event_detail ────────────────┤
├── dim_play_detail ─────────────────┘
│
Tracking Files ({game_id}_tracking.xlsx)
├── events sheet ──► fact_events ──┬──► fact_event_players
│                                  ├──► fact_scoring_chances
│                                  ├──► fact_shots, fact_goals
│                                  ├──► fact_rushes, fact_breakouts
│                                  ├──► fact_zone_entries/exits
│                                  ├──► fact_faceoffs, fact_penalties
│                                  └──► fact_sequences ──► fact_plays
│
├── shifts sheet ──► fact_shifts ──┬──► fact_shift_players
│                                  └──► TOI calculations
│
Aggregations
├── fact_events + fact_shifts ──► fact_player_game_stats
│                              ├──► fact_player_season_stats
│                              └──► fact_player_career_stats
│
├── fact_player_game_stats ──► fact_team_game_stats
│                           └──► fact_team_season_stats
│
└── Multiple tables ──► fact_game_summary
                     └──► QA tables
```

---

## Critical Business Rules

### Goal Counting

**CRITICAL RULE:**
```
Goals = event_type='Goal' AND event_detail='Goal_Scored'
```

**Important Notes:**
- `Shot_Goal` is the SHOT, not the goal
- `event_player_1` = goal scorer
- `event_player_2` = primary assist
- `event_player_3` = secondary assist
- Must match official goal count from game rosters

### Player Identification

```python
# Player lookup key
key = (game_id, team_name, jersey_number)
# Returns: player_id
```

### Time on Ice (TOI)

- Calculated from `fact_shifts`
- Propagated to event tables via shift joins
- Units: seconds (convert to MM:SS for display)

### Foreign Key Relationships

**Key Relationships:**
- `fact_events.game_id` → `dim_schedule.game_id`
- `fact_events.event_player_1` → `dim_player.player_id`
- `fact_shifts.player_id` → `dim_player.player_id`
- `fact_shifts.game_id` → `dim_schedule.game_id`
- `fact_events.shift_id` → `fact_shifts.shift_id` (when available)

---

## Table Manifest

### Complete Table List by Category

**BLB Tables (16):**
- dim_event_detail, dim_event_detail_2, dim_event_type, dim_league
- dim_play_detail, dim_play_detail_2, dim_player, dim_playerurlref
- dim_randomnames, dim_schedule, dim_season, dim_team
- fact_draft, fact_gameroster, fact_leadership, fact_registration

**Tracking Tables (5):**
- fact_event_players, fact_events, fact_shift_players, fact_shifts, fact_tracking

**Static Reference Tables (19-25):**
- dim_danger_level, dim_giveaway_type, dim_pass_type, dim_period
- dim_player_role, dim_position, dim_shift_duration, dim_shift_start_type
- dim_shift_stop_type, dim_shot_type, dim_situation, dim_stoppage_type
- dim_strength, dim_success, dim_takeaway_type, dim_venue, dim_zone
- dim_zone_entry_type, dim_zone_exit_type
- Plus dynamically generated reference tables (see Static Reference section)

**Calculated Tables (84+):**
- Player stats: fact_player_game_stats, fact_player_season_stats, fact_player_career_stats, etc.
- Team stats: fact_team_game_stats, fact_team_season_stats
- Goalie stats: fact_goalie_game_stats
- Matchups: fact_player_matchups, fact_h2h, fact_wowy, etc.
- Shift analytics: fact_shift_quality, fact_line_combos
- XY/Spatial: fact_puck_xy_wide, fact_player_xy_wide, etc.
- Event analytics: fact_sequences, fact_plays, fact_event_chains
- Game-level: fact_game_status, fact_season_summary
- Lookups: lookup_player_game_rating, fact_playergames

**QA Tables (4-6):**
- qa_goal_verification, qa_data_completeness, qa_suspicious_stats
- qa_foreign_key_check, qa_goal_accuracy, qa_scorer_comparison

---

## File Locations

| Component | Path |
|-----------|------|
| Main ETL | `src/core/base_etl.py` |
| Dimension Tables | `src/tables/dimension_tables.py` |
| Core Facts | `src/tables/core_facts.py` |
| Shift Analytics | `src/tables/shift_analytics.py` |
| Remaining Facts | `src/tables/remaining_facts.py` |
| Event Analytics | `src/tables/event_analytics.py` |
| XY Tables | `src/xy/xy_table_builder.py` |
| Extended Tables | `src/advanced/extended_tables.py` |
| V11 Enhancements | `src/advanced/v11_enhancements.py` |
| QA Tables | `src/qa/build_qa_facts.py` |
| Macro Stats | `src/tables/macro_stats.py` |
| Dimensions Constants | `src/models/dimensions.py` |
| Output CSVs | `data/output/*.csv` |
| Raw BLB | `data/raw/BLB_Tables.xlsx` |
| Raw Tracking | `data/raw/games/{game_id}/{game_id}_tracking.xlsx` |

---

## Validation Checklist

Before validating each table, verify:

1. [ ] **Source identified** - Know where data comes from
2. [ ] **Row count matches** - Compare to source if applicable
3. [ ] **Key columns present** - Primary/foreign keys exist
4. [ ] **Business rules applied** - Logic matches documentation
5. [ ] **No data loss** - All source records accounted for
6. [ ] **Goal count verified** - Goals match official count
7. [ ] **Foreign keys valid** - All FKs reference existing records
8. [ ] **Data types correct** - Columns have correct types
9. [ ] **No duplicates** - Unique constraints satisfied
10. [ ] **Calculations verified** - Derived fields calculated correctly

---

## Related Documentation

- [ETL.md](../etl/ETL.md) - ETL process documentation
- [ETL_ARCHITECTURE.md](../etl/ETL_ARCHITECTURE.md) - ETL architecture
- [ETL_DATA_FLOW.md](../etl/ETL_DATA_FLOW.md) - Data flow documentation

---

*Last Updated: 2026-01-15*
