# BenchSight v6.1 - Complete Handoff Documentation

## Project Overview

**BenchSight** is a comprehensive hockey analytics platform for the NORAD recreational hockey league. It processes tracking data from games, integrates with dimensional tables stored in Excel files, and supports advanced analytics including video URL integration with multiple camera angles.

### Key Components
- **Data Source**: BLB_Tables.xlsx (master data) + individual game tracking files
- **Database**: Supabase (PostgreSQL) at https://uuaowslhpgyiudmbvqze.supabase.co
- **ETL Pipeline**: Python-based processing from Excel → CSV → Supabase
- **Output**: Dimensional model with 39 dimension tables and 19 fact tables

### Tracked Games (Complete Data)
| Game ID | Events | Sequences | Plays | Goals |
|---------|--------|-----------|-------|-------|
| 18969 | 1,595 | ~268 | ~741 | 7 |
| 18977 | 1,362 | ~271 | ~538 | 5 |
| 18981 | 1,297 | ~260 | ~771 | 3 |
| 18987 | 1,579 | ~277 | ~682 | 1 |
| **Total** | **5,833** | **~1,076** | **~2,732** | **16** |

### Incomplete Games (Excluded from Advanced Stats)
- 18965, 18991, 19032 (mostly NaN event types)

---

## What's Done ✅

### 1. Database Schema (58 tables)
- **39 Dimension tables**: All reference data (players, teams, events, zones, etc.)
- **19 Fact tables**: Transactional data (events, shifts, stats, etc.)
- **Key format**: 12-character keys like `EV1896901000`, `SH1896900001`
- **FK coverage**: All fact tables have FK columns to dimensions

### 2. Core Fact Tables (WITH PROPER PK/FK)
| Table | Rows | PK Format | FK Columns | Description |
|-------|------|-----------|------------|-------------|
| fact_events | 5,831 | EV{game}{index} | 12 FKs | One row per event (wide) |
| fact_events_player | 11,181 | EP{game}{index} | 14 FKs | One row per player per event (long) |
| fact_shifts | 398 | SH{game}{index} | 15 FKs | One row per shift (wide) |
| fact_shifts_player | 4,626 | SP{game}{index} | 4 FKs | One row per player per shift (long) |
| fact_sequences | 1,088 | SQ{game}{index} | 1 FK | Possession chain summaries |
| fact_plays | 2,714 | PL{game}{index} | 2 FKs | Single-zone play summaries |
| fact_player_game_stats | 107 | PG{game}{index} | 2 FKs | Per-game stats (tracked games) |
| fact_goalie_game_stats | - | GG{game}{index} | 2 FKs | Goalie stats |
| fact_team_game_stats | 8 | TG{game}{index} | 1 FK | Team totals per game |

### Key Format Standard
All keys are 12 characters: `{PREFIX}{GAME_ID:05d}{INDEX:05d}`
- EV = Event, EP = Event Player, SH = Shift, SP = Shift Player
- SQ = Sequence, PL = Play, PG = Player Game, TG = Team Game

### FK Columns Present
Every column referencing a dimension has a corresponding `_id` FK column:
- `Type` → `event_type_id`
- `event_detail` → `event_detail_id`
- `period` → `period_id`
- `home_forward_1` → `home_forward_1_id`
- etc.

### 3. Sequence/Play Logic (CORRECTED)

**SEQUENCE** = Possession chain from turnover to turnover
- **Starts on**: Turnover (giveaway/takeaway), Faceoff, Stoppage
- **Ends on**: Goal (goal is last event), next turnover/faceoff/stoppage
- **Use case**: "How often does player X turn it over → opponent scores?"
- **Average**: ~5.4 events per sequence

**PLAY** = Single zone + single team possession
- **Starts on**: Zone change (entry/exit), possession change
- **Use case**: Analyze entry-to-shot patterns

**Generator**: `src/sequence_play_generator.py` (built, tested, ready to integrate)

### 4. Logical Shift Logic
| Column | Definition |
|--------|------------|
| logical_shift_number | Increments on shift_index gap OR period change |
| shift_segment | Segment within logical shift (1, 2, 3...) |
| cumulative_shift_duration | Running total within logical shift |
| playing_duration | shift_duration - stoppage_time |
| running_toi | Running total across ALL shifts |

### 5. Dimension Tables with Context
- dim_stat (83 rows) - Microstat definitions with formulas
- dim_net_location (15 rows) - Net target zones (5-hole, glove, blocker)
- dim_turnover_type (21 rows) - Good/bad/neutral with weights
- dim_terminology_mapping (84 rows) - Old term → new term mapping

### 6. Schema Documentation
- `docs/BenchSight_Schema_v6.1_Complete.xlsx` (15 sheets)
- All table definitions with PK/FK/data types
- Sequence/play trigger rules
- Logical shift logic definitions
- Rush/cycle detection rules

---

## What's Missing ❌

### 1. Missing Tables (5)
| Table | Purpose | Priority |
|-------|---------|----------|
| fact_event_chains | Entry→Shot→Goal timing for xG | High |
| fact_team_zone_time | Zone time per team per game | Medium |
| fact_h2h | Head-to-head player stats (X vs Y) | Medium |
| fact_wowy | With/without you analysis | Medium |
| fact_line_vs_line | Line combination matchups | Low |

### 2. Missing Columns in fact_events_player (11)
```
sequence_id, play_id, sequence_index_auto, play_index_auto,
is_rush, rush_type, is_cycle, chain_id,
turnover_quality_id, caused_by_turnover, sequence_result
```

### 3. Missing Stats in fact_player_game_stats (9)
```
shifts, shots_on_goal (SOG), faceoffs_won (FOW), faceoffs_lost (FOL),
corsi_for (CF), corsi_against (CA), plus_es, plus_all, goals_per_60 (G/60)
```

### 4. Missing Logic
- Rush detection (zone entry → shot within N events)
- Cycle detection (3+ consecutive o-zone passes)
- Event chain timing (entry→shot→goal)
- Skill differential (player rating vs opponent rating)
- Defender targets (from opp_player_1)
- Pass targets (from event_player_2)

---

## Build Plan

### PHASE 1: Sequence/Play Integration (CRITICAL)
1. Integrate `sequence_play_generator.py` into main ETL
2. Add sequence_id, play_id to fact_events and fact_events_player
3. Generate fact_sequences and fact_plays from real tracking data
4. Verify counts: ~1,076 sequences, ~2,732 plays across 4 games

### PHASE 2: Stats Completion
1. Add 9 missing stats to fact_player_game_stats
2. Implement rush detection (entry → shot)
3. Implement cycle detection (3+ o-zone passes)
4. Validate goals against NORAD website

### PHASE 3: Advanced Tables
1. fact_event_chains (entry→shot→goal timing)
2. fact_team_zone_time (ozone, dzone, nzone time)
3. fact_h2h, fact_wowy, fact_line_vs_line

### PHASE 4: Rating Context
1. Add skill differential columns
2. Track line rating vs opponent line rating
3. Context for "goal vs 4.5 line is different than goal vs 5.5 line"

---

## Key Rules & Definitions

### Player Role Attribution
| Role | Description | Stats Credited |
|------|-------------|----------------|
| event_player_1 | Primary player (shooter, passer) | Goals, shots, passes, turnovers |
| event_player_2 | Secondary player (pass target) | Assists, pass_received |
| opp_player_1 | Primary defender | Defender_targets, entry_denied |

### Success Flags
- `s` = successful
- `u` = unsuccessful
- blank = ignore

### Turnover Quality
| Quality | Description | Counts Against |
|---------|-------------|----------------|
| BAD | Player error (misplay, bad pass) | Yes |
| NEUTRAL | Normal play (shot blocked, battle lost) | No |
| GOOD | Intentional (dump, clear) | No |

### Plus/Minus Categories
| Stat | Description |
|------|-------------|
| plus_es / minus_es | Even strength only |
| plus_all / minus_all | All situations |
| plus_en / minus_en | Empty net goals |

---

## File Structure

```
benchsight_merged/
├── data/
│   ├── raw/
│   │   ├── BLB_Tables.xlsx          # Master data source
│   │   └── games/                    # Individual game tracking
│   │       ├── 18969/18969_tracking.xlsx
│   │       ├── 18977/18977_tracking.xlsx
│   │       ├── 18981/18981_tracking.xlsx
│   │       └── 18987/18987_tracking.xlsx
│   └── output/                       # 58 CSV files (dims + facts)
├── docs/
│   ├── HANDOFF.md                    # This file
│   ├── GAP_ANALYSIS.md               # What's missing
│   ├── SESSION_SUMMARY.md            # Latest chat summary
│   ├── BenchSight_Schema_v6.1_Complete.xlsx
│   └── schemas/                      # Additional schema docs
├── src/
│   ├── sequence_play_generator.py   # Sequence/play auto-generation
│   ├── etl_pipeline.py              # Main ETL
│   └── ...
├── config/
│   └── supabase_schema.json
└── sql/
    └── setup_supabase.sql
```

---

## Quick Start for New Chat

1. **Context**: "I'm continuing BenchSight development. Review docs/HANDOFF.md"
2. **Current state**: 58 tables built, sequence/play logic ready to integrate
3. **Next action**: Phase 1 - Integrate sequence_play_generator.py into ETL
4. **Validation**: Compare goals to NORAD website

---

## Supabase Connection

```
URL: https://uuaowslhpgyiudmbvqze.supabase.co
Schema: public
Tables: 58 (39 dims, 19 facts)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v6.1 | 2024-12-28 | Sequence/play logic corrected, schema Excel created |
| v6.0 | 2024-12-28 | Previous conversation merged, gaps identified |
| v5.5 | 2024-12-28 | Validation framework, 115 stats validated |

---

## Contact / Notes

- **User**: Ronnie (SQL Server expert)
- **Preferences**: Complete solutions, iterative refinement, comprehensive documentation
- **Key frustration**: Features being removed between versions - ALWAYS add, never subtract
- **Delivery checklist**: Run scripts/verify_delivery.py, include ALL files, verify goals match NORAD
