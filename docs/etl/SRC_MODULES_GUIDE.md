# BenchSight Source Modules Guide

**Complete guide to all src/ modules - where to update code, what each module does, and the data flow**

Last Updated: 2026-01-21
Version: 2.00

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [ETL Execution Flow](#etl-execution-flow)
3. [Module Directory](#module-directory)
4. [Core Modules](#core-modules)
5. [Table Builders](#table-builders)
6. [Calculations & Formulas](#calculations--formulas)
7. [Advanced Features](#advanced-features)
8. [Utilities & Support](#utilities--support)
9. [Where to Update Code](#where-to-update-code)
10. [Data Flow Diagrams](#data-flow-diagrams)

---

## Overview

The BenchSight codebase is organized into logical modules that follow the ETL pipeline pattern:

```
run_etl.py (Entry Point)
    ↓
src/core/base_etl.py (Phase 1-3: Base ETL)
    ↓
src/tables/ (Phase 4: Table Builders)
    ↓
src/advanced/ (Phase 6-10: Advanced Features)
    ↓
data/output/*.csv (139 tables)
```

**Total Modules:** 50+ Python files across 15 directories

---

## ETL Execution Flow

The ETL runs in 11 phases (see `run_etl.py`):

| Phase | Name | Module(s) | Tables Created |
|-------|------|-----------|----------------|
| 1 | Base ETL | `src/core/base_etl.py` | ~52 core tables |
| 3B | Dimension Tables | `src/tables/dimension_tables.py` | ~25 dim tables |
| 4 | Core Player Stats | `src/tables/core_facts.py` | 3 core fact tables |
| 4B | Shift Analytics | `src/tables/shift_analytics.py` | 5 shift tables |
| 4C | Remaining Facts | `src/tables/remaining_facts.py` | ~34 fact tables |
| 4D | Event Analytics | `src/tables/event_analytics.py` | 5 event tables |
| 4E | Shot Chains | `src/chains/shot_chain_builder.py` | 2 chain tables |
| 5 | Foreign Keys | `src/core/add_all_fkeys.py` | Adds FK columns |
| 6 | Extended Tables | `src/advanced/extended_tables.py` | ~10 extended tables |
| 7 | Post Processing | `src/etl/post_etl_processor.py` | Post-processing |
| 8 | Event Time Context | `src/advanced/event_time_context.py` | Context columns |
| 9 | QA Tables | `src/qa/build_qa_facts.py` | 4 QA tables |
| 10 | V11 Enhancements | `src/advanced/v11_enhancements.py` | ~30 enhancement tables |
| 10B | XY Tables | `src/xy/xy_table_builder.py` | 8 XY tables |
| 11 | Macro Stats | `src/tables/macro_stats.py` | 8 season/career tables |

**Total: 139 tables**

---

## Module Directory

### Core ETL Modules

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `src/core/` | Core ETL engine, utilities | `base_etl.py`, `key_utils.py`, `table_writer.py` |
| `src/tables/` | Table builders | `core_facts.py`, `dimension_tables.py`, `remaining_facts.py` |
| `src/builders/` | Modular table builders | `events.py`, `shifts.py` |
| `src/calculations/` | Calculation functions | `goals.py`, `corsi.py`, `ratings.py`, `time.py` |
| `src/formulas/` | Formula management | `formula_applier.py`, `registry.py` |

### Advanced Features

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `src/advanced/` | Advanced analytics | `v11_enhancements.py`, `extended_tables.py`, `event_time_context.py` |
| `src/chains/` | Event chain analysis | `shot_chain_builder.py` |
| `src/xy/` | Spatial analytics | `xy_table_builder.py`, `xy_tables.py` |

### Support Modules

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `src/utils/` | Utilities | `key_parser.py`, `game_type_aggregator.py` |
| `src/transformation/` | Data transformation | `standardize_play_details.py` |
| `src/qa/` | Quality assurance | `build_qa_facts.py` |
| `src/etl/` | ETL support | `post_etl_processor.py` |
| `src/models/` | Data models | `dimensions.py`, `master_dims.py` |

### External Integration

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `src/supabase/` | Supabase integration | `supabase_manager.py` |
| `src/norad/` | NORAD data integration | `norad_verifier.py`, `norad_schedule.py` |
| `src/ingestion/` | Data ingestion | `supabase_source.py` |
| `src/data_quality/` | Data cleaning | `cleaner.py` |

---

## Core Modules

### `src/core/base_etl.py` ⭐ **MAIN ETL ENGINE**

**Purpose:** Main ETL orchestrator - loads raw data, creates core tables, manages the pipeline

**Key Functions:**
- `main()` - Entry point, orchestrates all phases
- `load_blb_tables()` - Loads master dimension data from BLB_Tables.xlsx
- `load_tracking_data()` - Loads game tracking files
- `create_reference_tables()` - Creates dimension tables
- `create_derived_tables()` - Creates fact tables from tracking data
- `enhance_events_with_flags()` - Adds is_goal, is_sog, is_corsi flags
- `create_fact_sequences()` - Creates event sequences
- `create_fact_plays()` - Creates play chains

**Tables Created:** ~52 tables (fact_events, fact_shifts, fact_event_players, dim_*, etc.)

**Dependencies:**
- `src/builders/events.py` - Uses `build_fact_events()`
- `src/builders/shifts.py` - Uses `build_fact_shifts()`
- `src/core/key_utils.py` - Key generation
- `src/core/table_writer.py` - Table output

**Where to Update:**
- **Add new core tables:** Add functions in `create_derived_tables()`
- **Change data loading:** Modify `load_blb_tables()` or `load_tracking_data()`
- **Add event flags:** Update `enhance_events_with_flags()`
- **Change key generation:** Update `src/core/key_utils.py`

**Data Flow:**
```
BLB_Tables.xlsx → load_blb_tables() → dim_* tables
Game tracking files → load_tracking_data() → fact_events, fact_shifts
fact_events → enhance_events_with_flags() → fact_events (with flags)
fact_events → create_fact_sequences() → fact_sequences
```

---

### `src/core/key_utils.py`

**Purpose:** Centralized key generation utilities

**Key Functions:**
- `format_key()` - Format keys consistently
- `generate_event_id()` - Generate event IDs
- `generate_shift_id()` - Generate shift IDs
- `add_all_keys()` - Add keys to all tables

**Where to Update:**
- **Change key format:** Modify key generation functions
- **Add new key types:** Add new functions here

---

### `src/core/table_writer.py`

**Purpose:** Centralized table output management (CSV + optional Supabase)

**Key Functions:**
- `save_output_table()` - Save table to CSV
- `enable_supabase()` - Enable Supabase upload
- `disable_supabase()` - Disable Supabase upload

**Where to Update:**
- **Change output format:** Modify `save_output_table()`
- **Add new output targets:** Extend this module

---

### `src/core/add_all_fkeys.py`

**Purpose:** Adds foreign key columns to all tables

**Key Functions:**
- `main()` - Adds FKs to all tables

**Where to Update:**
- **Add new FK relationships:** Add mappings in this file

---

## Table Builders

### `src/tables/core_facts.py` ⭐ **CORE STATS**

**Purpose:** Creates the 3 core fact tables with comprehensive stats

**Key Functions:**
- `create_fact_player_game_stats()` - **444 columns** per player per game
- `create_fact_team_game_stats()` - Team-level game stats
- `create_fact_goalie_game_stats()` - **128 columns** per goalie per game

**Tables Created:**
- `fact_player_game_stats` (444 columns)
- `fact_team_game_stats`
- `fact_goalie_game_stats` (128 columns)

**Dependencies:**
- `src/calculations/` - Uses calculation functions
- `src/formulas/formula_applier.py` - Applies formulas
- `src/builders/` - Uses builders for events/shifts

**Where to Update:**
- **Add new player stats:** Add calculation functions, then call in `create_fact_player_game_stats()`
- **Change formulas:** Update `config/formulas.json` or `src/formulas/`
- **Add new goalie stats:** Modify `create_fact_goalie_game_stats()`

**Data Flow:**
```
fact_event_players + fact_shifts + fact_shift_players
    ↓
calculate_*_stats() functions
    ↓
apply_player_stats_formulas()
    ↓
fact_player_game_stats
```

---

### `src/tables/dimension_tables.py`

**Purpose:** Creates static dimension tables (lookup/reference data)

**Key Functions:**
- `create_all_dimension_tables()` - Creates all dim tables
- `create_dim_*()` - Individual dimension table creators

**Tables Created:** ~25 dimension tables (dim_player, dim_team, dim_event_type, etc.)

**Where to Update:**
- **Add new dimension:** Add `create_dim_*()` function
- **Change dimension logic:** Modify existing `create_dim_*()` functions

---

### `src/tables/remaining_facts.py`

**Purpose:** Creates additional fact tables (period stats, micro stats, etc.)

**Key Functions:**
- `build_remaining_tables()` - Builds all remaining tables
- `create_fact_player_period_stats()` - Period-level stats
- `create_fact_player_micro_stats()` - Micro-statistics
- `create_fact_zone_entry_summary()` - Zone entry analytics
- `create_fact_player_season_stats()` - Season aggregations

**Tables Created:** ~34 fact tables

**Where to Update:**
- **Add new fact table:** Add `create_fact_*()` function, add to `build_remaining_tables()`

---

### `src/tables/shift_analytics.py`

**Purpose:** Shift-level analytics (H2H, WOWY, line combinations)

**Key Functions:**
- `create_all_shift_analytics()` - Creates all shift analytics
- `create_fact_h2h()` - Head-to-head matchups
- `create_fact_wowy()` - With/without you analysis
- `create_fact_line_combos()` - Line combination stats
- `create_fact_shift_quality()` - Shift quality metrics

**Tables Created:** 5 shift analytics tables

**Where to Update:**
- **Add new shift metric:** Add function, call in `create_all_shift_analytics()`

---

### `src/tables/event_analytics.py`

**Purpose:** Event-level analytics (scoring chances, shot danger, rushes)

**Key Functions:**
- `create_all_event_analytics()` - Creates all event analytics
- `create_fact_scoring_chances()` - Scoring chance events
- `create_fact_shot_danger()` - Shot danger analysis
- `create_fact_rush_events()` - Rush event analysis
- `create_fact_linked_events()` - Linked event chains

**Tables Created:** 5 event analytics tables

**Where to Update:**
- **Add new event metric:** Add function, call in `create_all_event_analytics()`

---

### `src/tables/macro_stats.py`

**Purpose:** Season and career aggregations

**Key Functions:**
- `create_all_macro_stats()` - Creates all macro stats
- `create_fact_player_season_stats_basic()` - Basic season stats
- `create_fact_player_career_stats_basic()` - Basic career stats
- `create_fact_team_season_stats_basic()` - Team season stats
- `create_fact_goalie_season_stats()` - Goalie season stats

**Tables Created:** 8 season/career tables

**Where to Update:**
- **Add new aggregation:** Add function, call in `create_all_macro_stats()`

---

## Calculations & Formulas

### `src/calculations/` ⭐ **CALCULATION FUNCTIONS**

**Purpose:** Pure calculation functions (testable, reusable)

**Modules:**
- `goals.py` - Goal counting functions
- `corsi.py` - Corsi/Fenwick calculations
- `ratings.py` - Player rating calculations
- `time.py` - Time on ice calculations

**Key Functions:**
- `filter_goals()` - Filter events to goals only
- `calculate_cf_pct()` - Calculate Corsi percentage
- `calculate_team_ratings()` - Calculate team ratings
- `calculate_per_60_rate()` - Calculate per-60 rates

**Where to Update:**
- **Add new calculation:** Create function in appropriate module
- **Change calculation logic:** Modify existing functions
- **Add tests:** Add to `tests/test_calculations.py`

**Usage:**
```python
from src.calculations import filter_goals, calculate_cf_pct

goals = filter_goals(events_df)
cf_pct = calculate_cf_pct(cf=10, ca=5)  # Returns 66.67
```

---

### `src/formulas/` ⭐ **FORMULA MANAGEMENT**

**Purpose:** JSON-based formula management system

**Key Files:**
- `formula_applier.py` - Applies formulas to dataframes
- `registry.py` - Formula registry
- `player_stats_formulas.py` - Player stats formulas
- `config/formulas.json` - Formula definitions (JSON)

**Key Functions:**
- `apply_player_stats_formulas()` - Applies all formulas to player stats
- `get_formula()` - Gets formula from registry

**Where to Update:**
- **Add new formula:** Add to `config/formulas.json`
- **Change formula:** Update `config/formulas.json`
- **Add formula group:** Update `registry.py`

**Example Formula (JSON):**
```json
{
  "name": "goals_per_60",
  "formula": "goals / toi_minutes * 60",
  "group": "core_formulas"
}
```

---

### `src/builders/` ⭐ **MODULAR BUILDERS**

**Purpose:** Modular table building functions (extracted from base_etl.py)

**Modules:**
- `events.py` - Event table builder
- `shifts.py` - Shift table builder

**Key Functions:**
- `build_fact_events()` - Builds fact_events table
- `build_fact_shifts()` - Builds fact_shifts table

**Where to Update:**
- **Change event building logic:** Modify `build_fact_events()`
- **Change shift building logic:** Modify `build_fact_shifts()`
- **Add new builder:** Create new module in `src/builders/`

---

## Advanced Features

### `src/advanced/v11_enhancements.py`

**Purpose:** V11 feature enhancements (30+ tables)

**Key Functions:**
- `run_all_enhancements()` - Runs all enhancements
- Creates various enhancement tables

**Tables Created:** ~30 enhancement tables

**Where to Update:**
- **Add new enhancement:** Add function, call in `run_all_enhancements()`

---

### `src/advanced/extended_tables.py`

**Purpose:** Extended analytics tables

**Key Functions:**
- `create_extended_tables()` - Creates extended tables
- `create_fact_player_career_stats()` - Career stats
- `create_fact_zone_entry_summary()` - Zone entry summary

**Tables Created:** ~10 extended tables

**Where to Update:**
- **Add new extended table:** Add function, call in `create_extended_tables()`

---

### `src/advanced/event_time_context.py`

**Purpose:** Adds time-based context to events

**Key Functions:**
- `enhance_event_tables()` - Adds time context columns

**Where to Update:**
- **Add new time context:** Modify `enhance_event_tables()`

---

### `src/chains/shot_chain_builder.py`

**Purpose:** Zone entry → shot chain analysis

**Key Functions:**
- `build_shot_chains()` - Builds shot chain tables

**Tables Created:** 2 chain tables

**Where to Update:**
- **Change chain logic:** Modify `build_shot_chains()`

---

### `src/xy/xy_table_builder.py`

**Purpose:** XY coordinate and spatial analytics

**Key Functions:**
- `build_all_xy_tables()` - Builds all XY tables

**Tables Created:** 8 XY tables

**Where to Update:**
- **Add new spatial metric:** Add function, call in `build_all_xy_tables()`

---

## Utilities & Support

### `src/utils/key_parser.py`

**Purpose:** Key parsing utilities

**Key Functions:**
- `parse_shift_key()` - Parse shift keys
- `make_shift_key()` - Make shift keys

**Where to Update:**
- **Change key parsing:** Modify parsing functions

---

### `src/utils/game_type_aggregator.py`

**Purpose:** Game type aggregation (Regular/Playoffs/All)

**Key Functions:**
- Aggregates stats by game type

**Where to Update:**
- **Change aggregation logic:** Modify this file

---

### `src/transformation/standardize_play_details.py`

**Purpose:** Standardizes play detail codes

**Key Functions:**
- `standardize_tracking_data()` - Standardizes tracking data

**Where to Update:**
- **Add standardization rule:** Add to standardization logic

---

### `src/qa/build_qa_facts.py`

**Purpose:** Quality assurance validation tables

**Key Functions:**
- `main()` - Creates QA tables

**Tables Created:** 4 QA tables

**Where to Update:**
- **Add new QA check:** Add function, call in `main()`

---

### `src/etl/post_etl_processor.py`

**Purpose:** Post-ETL processing

**Key Functions:**
- `main()` - Post-processing tasks

**Where to Update:**
- **Add post-processing:** Add to `main()`

---

## Where to Update Code

### Adding a New Statistic

1. **If it's a calculation:**
   - Add function to `src/calculations/` (appropriate module)
   - Add test to `tests/test_calculations.py`
   - Use in table builder

2. **If it's a formula:**
   - Add to `config/formulas.json`
   - Formulas auto-applied via `formula_applier.py`

3. **If it's a new column in fact_player_game_stats:**
   - Add calculation function in `src/tables/core_facts.py`
   - Call in `create_fact_player_game_stats()`
   - Or add formula to `config/formulas.json`

### Adding a New Table

1. **Create builder function:**
   - Add `create_fact_*()` or `create_dim_*()` function
   - Place in appropriate `src/tables/` module

2. **Add to ETL flow:**
   - Add call in appropriate phase in `run_etl.py`
   - Or add to module's `create_all_*()` function

3. **Update documentation:**
   - Add to `docs/DATA_DICTIONARY.md`
   - Update `scripts/generate_data_dictionary.py` metadata

### Changing Data Loading

1. **Change BLB loading:**
   - Modify `src/core/base_etl.py:load_blb_tables()`

2. **Change tracking loading:**
   - Modify `src/core/base_etl.py:load_tracking_data()`

3. **Change game discovery:**
   - Modify `src/core/base_etl.py:discover_games()`

### Changing Key Generation

1. **Change key format:**
   - Modify `src/core/key_utils.py`

2. **Change key parsing:**
   - Modify `src/utils/key_parser.py`

### Adding Event Flags

1. **Add new flag:**
   - Add logic to `src/core/base_etl.py:enhance_events_with_flags()`
   - Update `docs/DATA_DICTIONARY.md` with flag definition

---

## Data Flow Diagrams

### Overall ETL Flow

```
run_etl.py
    ↓
Phase 1: Base ETL (base_etl.py)
    ├── Load BLB_Tables.xlsx → dim_* tables
    ├── Load tracking files → fact_events, fact_shifts
    └── Create derived tables
    ↓
Phase 3B: Dimension Tables (dimension_tables.py)
    └── Create static dim_* tables
    ↓
Phase 4: Core Stats (core_facts.py)
    ├── fact_player_game_stats (444 cols)
    ├── fact_team_game_stats
    └── fact_goalie_game_stats (128 cols)
    ↓
Phase 4B-4E: Analytics Tables
    ├── shift_analytics.py → H2H, WOWY, line combos
    ├── remaining_facts.py → Period stats, micro stats
    ├── event_analytics.py → Scoring chances, rushes
    └── shot_chain_builder.py → Shot chains
    ↓
Phase 5-11: Advanced Features
    ├── Foreign keys
    ├── Extended tables
    ├── Event time context
    ├── QA tables
    ├── V11 enhancements
    ├── XY tables
    └── Macro stats
    ↓
data/output/*.csv (139 tables)
```

### fact_player_game_stats Creation Flow

```
fact_event_players (events by player)
    +
fact_shifts (shift data)
    +
fact_shift_players (player shift stats)
    ↓
For each player-game:
    ├── calculate_core_stats() → goals, assists, shots
    ├── calculate_corsi_stats() → CF, CA, CF%
    ├── calculate_strength_splits() → EV/PP/PK stats
    ├── calculate_shot_type_stats() → Wrist, slap, etc.
    ├── calculate_pass_stats() → Pass types
    ├── calculate_rush_stats() → Rush metrics
    ├── calculate_pressure_stats() → Pressure performance
    ├── calculate_competition_tier_stats() → QoC metrics
    ├── calculate_game_state_stats() → Leading/trailing
    ├── calculate_linemate_stats() → Linemate analysis
    ├── calculate_time_bucket_stats() → Early/late period
    ├── calculate_rebound_stats() → Rebound metrics
    ├── calculate_game_score() → Game score
    ├── calculate_war_stats() → WAR/GAR
    └── calculate_performance_vs_rating() → Rating analysis
    ↓
apply_player_stats_formulas() → Per-60 rates, percentages
    ↓
fact_player_game_stats (444 columns)
```

### Calculation Function Flow

```
Raw Data
    ↓
src/calculations/goals.py
    ├── filter_goals() → Goals only
    ├── is_goal_scored() → Goal check
    └── count_goals_for_player() → Goal count
    ↓
src/calculations/corsi.py
    ├── is_corsi_event() → Corsi check
    ├── is_fenwick_event() → Fenwick check
    └── calculate_cf_pct() → CF%
    ↓
src/calculations/ratings.py
    ├── calculate_team_ratings() → Team ratings
    └── calculate_expected_cf_pct() → Expected CF%
    ↓
src/calculations/time.py
    ├── calculate_toi_minutes() → TOI conversion
    └── calculate_per_60_rate() → Per-60 rates
    ↓
Used in table builders
```

---

## Quick Reference

### Most Common Updates

| Task | File to Edit |
|------|--------------|
| Add new player stat | `src/tables/core_facts.py` → `create_fact_player_game_stats()` |
| Add new calculation | `src/calculations/` → appropriate module |
| Add new formula | `config/formulas.json` |
| Add new table | `src/tables/` → appropriate module |
| Change event flags | `src/core/base_etl.py` → `enhance_events_with_flags()` |
| Change key format | `src/core/key_utils.py` |
| Change data loading | `src/core/base_etl.py` → `load_*()` functions |
| Add new dimension | `src/tables/dimension_tables.py` |

### Module Import Patterns

```python
# Calculations
from src.calculations import filter_goals, calculate_cf_pct

# Builders
from src.builders import build_fact_events, build_fact_shifts

# Formulas
from src.formulas.formula_applier import apply_player_stats_formulas

# Key utilities
from src.core.key_utils import generate_event_id, format_key

# Table writer
from src.core.table_writer import save_output_table
```

---

## Maintenance Notes

### When Adding New Code

1. **Follow existing patterns** - Look at similar functions
2. **Add docstrings** - Document what the function does
3. **Update this guide** - Add new modules/functions here
4. **Update data dictionary** - Add table/column metadata
5. **Add tests** - For calculation functions, add unit tests

### Code Organization Principles

1. **Single Responsibility** - Each module has one clear purpose
2. **Reusability** - Calculation functions are pure and reusable
3. **Testability** - Functions can be tested in isolation
4. **Documentation** - Code is self-documenting with docstrings

---

*Last updated: 2026-01-13*
