# BenchSight Data Lineage

**Complete mapping of where each table comes from, how it's built, and what logic drives it.**

Generated: 2026-01-10

---

## Table of Contents
1. [Overview](#overview)
2. [Source Categories](#source-categories)
3. [BLB_Tables Direct Loads](#1-blb_tables-direct-loads)
4. [Tracking File Processing](#2-tracking-file-processing)
5. [Derived/Calculated Tables](#3-derivedcalculated-tables)
6. [Static Reference Tables](#4-static-reference-tables)
7. [QA Tables](#5-qa-tables)
8. [ETL Phase Summary](#etl-phase-summary)
9. [Dependency Graph](#dependency-graph)

---

## Overview

| Category | Count | Description |
|----------|-------|-------------|
| BLB_Tables Direct | 17 | Loaded directly from Excel sheets |
| Tracking Derived | ~25 | Built from game tracking files |
| Calculated/Aggregated | ~40 | Computed from other tables |
| Static Reference | ~45 | Hardcoded constants or generated |
| QA Tables | 4 | Data quality checks |
| **TOTAL** | **132** | |

---

## Source Categories

### Source Type Legend
| Code | Meaning | Example |
|------|---------|---------|
| 📊 BLB | Direct load from BLB_Tables.xlsx sheet | dim_player |
| 🎮 TRK | Derived from tracking Excel files | fact_events |
| 🧮 CALC | Calculated from other tables | fact_player_game_stats |
| 📌 STATIC | Hardcoded constants | dim_period |
| 🔍 QA | Quality assurance checks | qa_goal_verification |

---

## 1. BLB_Tables Direct Loads

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

## 2. Tracking File Processing

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

## 3. Derived/Calculated Tables

**Source:** Other fact tables + aggregation logic
**ETL Phase:** Phase 6-9

### Player Statistics

| Table | Source Tables | Aggregation | Code Location |
|-------|---------------|-------------|---------------|
| fact_player_game_stats | fact_events, fact_shifts | Per-game player stats | v11_enhancements.py |
| fact_player_season_stats | fact_player_game_stats | Seasonal rollup | v11_enhancements.py |
| fact_player_career_stats | fact_player_season_stats | Career totals | v11_enhancements.py |
| fact_player_period_stats | fact_events | Per-period breakdown | v11_enhancements.py |
| fact_player_situation_stats | fact_events | By game situation (5v5, PP, PK) | v11_enhancements.py |

### Team Statistics

| Table | Source Tables | Aggregation |
|-------|---------------|-------------|
| fact_team_game_stats | fact_player_game_stats | Team totals per game |
| fact_team_season_stats | fact_team_game_stats | Season team totals |

### Game-Level Tables

| Table | Source Tables | Purpose |
|-------|---------------|---------|
| fact_game_summary | Multiple fact tables | Complete game summary |
| fact_game_flow | fact_events | Score progression |
| fact_game_status | Multiple | Tracking completion status |

### Matchup/Comparison Tables

| Table | Source Tables | Purpose |
|-------|---------------|---------|
| fact_player_matchups | fact_events | Head-to-head player stats |
| fact_player_matchups_xy | fact_events + XY | Spatial matchup data |
| fact_line_matchups | fact_shifts | Line combination stats |

### XY/Spatial Tables

| Table | Source | Purpose | Code |
|-------|--------|---------|------|
| fact_puck_xy_wide | fact_events | Puck position (wide format) | xy_tables.py |
| fact_puck_xy_long | fact_events | Puck position (long format) | xy_tables.py |
| fact_player_xy_wide | fact_events | Player positions (wide) | xy_tables.py |
| fact_player_xy_long | fact_events | Player positions (long) | xy_tables.py |
| fact_player_puck_proximity | fact_events | Distance calculations | xy_tables.py |
| fact_shot_event | fact_events | Shot-specific XY | xy_tables.py |
| fact_shot_players | fact_events | Players on ice for shots | xy_tables.py |

---

## 4. Static Reference Tables

**Source:** Hardcoded in ETL
**ETL Phase:** Phase 5 (`build_reference_dimensions()`)
**Code:** `src/core/base_etl.py` lines 1450-1600

| Table | Rows | Logic | Purpose |
|-------|------|-------|---------|
| dim_period | 5 | Hardcoded P1-P5 | Period definitions |
| dim_venue | 2 | Home/Away | Venue codes |
| dim_position | 4 | F/D/G/X | Position codes |
| dim_zone | 3 | O/N/D | Zone codes |
| dim_player_role | 15 | Hardcoded roles | Event player roles (shooter, passer, etc.) |
| dim_success | 3 | s/u/n | Success outcome codes |
| dim_shot_type | ~10 | From dimensions.py | Shot type codes |
| dim_pass_type | ~8 | From dimensions.py | Pass type codes |
| dim_strength | ~6 | 5v5, PP, PK, etc. | Game strength states |
| dim_situation | ~10 | Even, PP, PK variants | Game situations |
| dim_danger_level | 3 | Low/Medium/High | Scoring chance danger |
| dim_danger_zone | 6 | Slot, high slot, etc. | Ice danger zones |

### Dynamically Generated Reference Tables

| Table | Source | Logic |
|-------|--------|-------|
| dim_zone_entry_type | fact_events | Unique zone entry types from tracking |
| dim_zone_exit_type | fact_events | Unique zone exit types from tracking |
| dim_stoppage_type | fact_events | Unique stoppage types from tracking |
| dim_giveaway_type | fact_events | Unique giveaway types from tracking |
| dim_takeaway_type | fact_events | Unique takeaway types from tracking |
| dim_shift_start_type | fact_shifts | Shift start types |
| dim_shift_stop_type | fact_shifts | Shift stop types |

---

## 5. QA Tables

**Source:** Validation checks on other tables
**ETL Phase:** Phase 9 (Validation)

| Table | Purpose | Logic |
|-------|---------|-------|
| qa_goal_verification | Verify goal counts match | Compare fact_events goals to official |
| qa_data_completeness | Check for missing data | NULL counts, required fields |
| qa_suspicious_stats | Flag anomalies | Outlier detection |
| qa_foreign_key_check | Validate relationships | FK integrity checks |

---

## ETL Phase Summary

| Phase | Name | Tables Created | Code |
|-------|------|----------------|------|
| 1 | Load BLB_Tables | 17 | base_etl.py:864-936 |
| 2 | Build Player Lookup | 0 (helper) | base_etl.py:942-998 |
| 3 | Process Tracking Files | 5 | base_etl.py:1000-1200 |
| 4 | Build Fact Tables | 15 | base_etl.py:1200-1400 |
| 5 | Build Reference Dims | 25 | base_etl.py:1450-1880 |
| 6 | Build Sequences/Plays | 2 | base_etl.py:2800-3000 |
| 7 | Build Derived Facts | 15 | base_etl.py:3100-3300 |
| 8 | V11 Enhancements | 30 | v11_enhancements.py |
| 9 | Validation/QA | 4 | base_etl.py:3900-4000 |
| 10 | XY Tables | 8 | xy_tables.py |

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
```
Goals = event_type='Goal' AND event_detail='Goal_Scored'
```
- `Shot_Goal` is the SHOT, not the goal
- `event_player_1` = goal scorer
- `event_player_2` = primary assist
- `event_player_3` = secondary assist

### Player Identification
```python
# Player lookup key
key = (game_id, team_name, jersey_number)
# Returns: player_id
```

### Time on Ice (TOI)
- Calculated from fact_shifts
- Propagated to event tables via shift joins
- Units: seconds (convert to MM:SS for display)

---

## File Locations

| Component | Path |
|-----------|------|
| Main ETL | `src/core/base_etl.py` |
| V11 Enhancements | `src/core/v11_enhancements.py` |
| XY Tables | `src/core/xy_tables.py` |
| Dimensions Constants | `src/models/dimensions.py` |
| Output CSVs | `data/output/*.csv` |
| Raw BLB | `data/raw/BLB_Tables.xlsx` |
| Raw Tracking | `data/raw/{game_id}_tracking.xlsx` |

---

## Validation Checklist

Before validating each table, verify:

1. [ ] **Source identified** - Know where data comes from
2. [ ] **Row count matches** - Compare to source if applicable
3. [ ] **Key columns present** - Primary/foreign keys exist
4. [ ] **Business rules applied** - Logic matches documentation
5. [ ] **No data loss** - All source records accounted for

---

*Last updated: 2026-01-10*
