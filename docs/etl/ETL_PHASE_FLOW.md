# ETL Phase Flow

**Complete documentation of the BenchSight ETL pipeline phase flow.**

Last Updated: 2026-01-22

---

## Overview

The BenchSight ETL pipeline processes game tracking data through 11 main phases, creating 139 tables (50 dimensions, 81 facts, 8 QA). Each phase builds upon previous phases, with clear data dependencies.

---

## Phase Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    ETL PIPELINE FLOW                         │
└─────────────────────────────────────────────────────────────┘

Phase 1: BASE ETL
├── Load BLB Tables (Excel)
├── Build Player Lookup
└── Load Tracking Data (JSON/Excel)
    └── Creates: fact_events, fact_event_players, fact_shifts, fact_shift_players

Phase 3B: STATIC DIMENSION TABLES
└── Creates: dim_player, dim_team, dim_league, dim_season, dim_schedule, etc.
    (55 dimension tables)

Phase 4: CORE PLAYER STATS
├── Player Game Stats
├── Team Game Stats
└── Creates: fact_player_game_stats, fact_team_game_stats

Phase 4B: SHIFT ANALYTICS
├── Head-to-Head (H2H)
├── With or Without You (WOWY)
├── Line Combinations
└── Creates: fact_h2h, fact_wowy, fact_line_combos

Phase 4C: REMAINING FACT TABLES
└── Creates: Various fact tables (goalie stats, etc.)

Phase 4D: EVENT ANALYTICS
├── Rush Events
├── Shot Chains
└── Creates: fact_rush_events, fact_shot_chains

Phase 4E: SHOT CHAINS
└── Creates: fact_shot_chains (detailed)

Phase 5: FOREIGN KEYS & ADDITIONAL TABLES
└── Adds foreign keys to all tables

Phase 6: EXTENDED TABLES
└── Creates: Extended analytics tables

Phase 7: POST PROCESSING
└── Post-processing enhancements

Phase 8: EVENT TIME CONTEXT
└── Time-based context enhancements

Phase 9: QA TABLES
└── Creates: qa_game_status, qa_table_counts, etc.

Phase 10: V11 ENHANCEMENTS
└── Version 11 specific enhancements

Phase 10B: XY TABLES & SPATIAL ANALYTICS
└── Creates: XY coordinate tables

Phase 11: MACRO STATS
└── Creates: Season/career aggregations
```

---

## Phase Details

### Phase 1: BASE ETL (BLB + Tracking + Derived Tables)

**Entry Point:** `src/core/base_etl.py::main()`

**Sub-phases:**
1. **Phase 1.1:** Load BLB Tables from Excel
2. **Phase 1.2:** Build Player Lookup
3. **Phase 1.3:** Load Tracking Data (events, shifts)
4. **Phase 1.4:** Create Derived Tables

**Output Tables:**
- `fact_events` - All game events
- `fact_event_players` - Players involved in events
- `fact_shifts` - Player shifts
- `fact_shift_players` - Players in shifts

**Dependencies:** None (reads from `data/raw/`)

**Key Functions:**
- `load_blb_tables()` - Loads Excel BLB tables
- `build_player_lookup()` - Creates player lookup
- `load_tracking_data()` - Loads game tracking files
- `build_fact_events()` - Creates event tables
- `build_fact_shifts()` - Creates shift tables

---

### Phase 3B: STATIC DIMENSION TABLES

**Entry Point:** `src/tables/dimension_tables.py::create_all_dimension_tables()`

**Description:** Creates all static dimension/reference tables that don't depend on game data.

**Output Tables:**
- `dim_player` - Player master data
- `dim_team` - Team master data
- `dim_league` - League master data
- `dim_season` - Season master data
- `dim_schedule` - Game schedule
- Plus 50+ other dimension tables

**Dependencies:** Phase 1 (for player/team data from BLB)

**Key Functions:**
- `create_dim_player()` - Player dimension
- `create_dim_team()` - Team dimension
- `create_dim_schedule()` - Schedule dimension
- Plus functions for each dimension table

---

### Phase 4: CORE PLAYER STATS

**Entry Point:** `src/tables/core_facts.py::create_all_core_facts()`

**Description:** Creates core player and team statistics tables.

**Output Tables:**
- `fact_player_game_stats` - Player stats per game
- `fact_team_game_stats` - Team stats per game

**Dependencies:** Phase 1 (events, shifts), Phase 3B (dimensions)

**Key Functions:**
- `create_fact_player_game_stats()` - Aggregates player stats
- `create_fact_team_game_stats()` - Aggregates team stats

---

### Phase 4B: SHIFT ANALYTICS

**Entry Point:** `src/tables/shift_analytics.py::create_all_shift_analytics()`

**Description:** Creates shift-based analytics (H2H, WOWY, line combinations).

**Output Tables:**
- `fact_h2h` - Head-to-head player matchups
- `fact_wowy` - With or without you analytics
- `fact_line_combos` - Line combination statistics

**Dependencies:** Phase 1 (shifts), Phase 3B (dimensions)

---

### Phase 4C: REMAINING FACT TABLES

**Entry Point:** `src/tables/remaining_facts.py::build_remaining_tables()`

**Description:** Creates remaining fact tables not covered in other phases.

**Output Tables:** Various fact tables (goalie stats, etc.)

**Dependencies:** Phase 1, Phase 3B, Phase 4

---

### Phase 4D: EVENT ANALYTICS

**Entry Point:** `src/tables/event_analytics.py::create_all_event_analytics()`

**Description:** Creates event-based analytics (rushes, shot chains).

**Output Tables:**
- `fact_rush_events` - Rush event analysis
- `fact_shot_chains` - Shot chain sequences

**Dependencies:** Phase 1 (events), Phase 3B (dimensions)

---

### Phase 4E: SHOT CHAINS

**Entry Point:** `src/chains/shot_chain_builder.py::build_shot_chains()`

**Description:** Builds detailed shot chain sequences.

**Output Tables:**
- `fact_shot_chains` - Detailed shot chain data

**Dependencies:** Phase 1 (events), Phase 4D

---

### Phase 5: FOREIGN KEYS & ADDITIONAL TABLES

**Entry Point:** `src/core/add_all_fkeys.py::main()`

**Description:** Adds foreign key columns to all tables for referential integrity.

**Output:** Modifies existing tables (adds FK columns)

**Dependencies:** All previous phases

**Key Functions:**
- `add_all_fkeys()` - Adds foreign keys to all tables

---

### Phase 6: EXTENDED TABLES

**Entry Point:** `src/advanced/extended_tables.py::create_extended_tables()`

**Description:** Creates extended analytics tables.

**Dependencies:** All previous phases

---

### Phase 7: POST PROCESSING

**Entry Point:** `src/etl/post_etl_processor.py::main()`

**Description:** Post-processing enhancements and cleanup.

**Dependencies:** All previous phases

---

### Phase 8: EVENT TIME CONTEXT

**Entry Point:** `src/advanced/event_time_context.py::enhance_event_tables()`

**Description:** Adds time-based context to event tables.

**Dependencies:** Phase 1 (events)

---

### Phase 9: QA TABLES

**Entry Point:** `src/qa/build_qa_facts.py::main()`

**Description:** Creates quality assurance tables for validation.

**Output Tables:**
- `qa_game_status` - Game processing status
- `qa_table_counts` - Table row counts
- Other QA tables

**Dependencies:** All previous phases

---

### Phase 10: V11 ENHANCEMENTS

**Entry Point:** `src/advanced/v11_enhancements.py::run_all_enhancements()`

**Description:** Version 11 specific enhancements.

**Dependencies:** Phase 9 (uses qa_game_status)

---

### Phase 10B: XY TABLES & SPATIAL ANALYTICS

**Entry Point:** `src/xy/xy_table_builder.py::build_all_xy_tables()`

**Description:** Creates XY coordinate and spatial analytics tables.

**Dependencies:** Phase 1 (events with XY data)

---

### Phase 11: MACRO STATS

**Entry Point:** `src/tables/macro_stats.py::create_all_macro_stats()`

**Description:** Creates season and career aggregation tables.

**Output Tables:**
- Season-level aggregations
- Career-level aggregations

**Dependencies:** All previous phases

---

## Data Dependencies

### Critical Dependencies

1. **Phase 1 → All Phases:** Base event and shift data required for all analytics
2. **Phase 3B → Phase 4+:** Dimension tables required for foreign keys
3. **Phase 4 → Phase 4B+:** Core stats required for advanced analytics
4. **Phase 9 → Phase 10:** QA tables used by V11 enhancements

### Table Generation Order

Tables must be generated in phase order due to foreign key dependencies:

```
Phase 1 → Phase 3B → Phase 4 → Phase 4B → Phase 4C → Phase 4D → Phase 4E → 
Phase 5 → Phase 6 → Phase 7 → Phase 8 → Phase 9 → Phase 10 → Phase 10B → Phase 11
```

---

## Entry Points

### Primary Entry Point

**`run_etl.py`** - Single source of truth for ETL execution

```bash
python run_etl.py              # Full ETL
python run_etl.py --wipe       # Clean slate + full ETL
python run_etl.py --debug      # Debug mode with PostgreSQL
```

### Phase-Specific Entry Points

Each phase can be run individually (for debugging):

```python
# Phase 1
from src.core.base_etl import main as run_base_etl
run_base_etl()

# Phase 3B
from src.tables.dimension_tables import create_all_dimension_tables
create_all_dimension_tables()

# Phase 4
from src.tables.core_facts import create_all_core_facts
create_all_core_facts()
```

---

## Exit Points

Each phase writes tables to `data/output/` as CSV files. The final phase (Phase 11) completes the ETL pipeline.

**Output Location:** `data/output/*.csv`

**Total Tables:** 139 (50 dimensions, 81 facts, 8 QA)

---

## Error Handling

- Each phase catches exceptions and logs errors
- Failed phases prevent subsequent phases from running (where dependencies exist)
- Error messages logged to console and `logs/etl_v5.log`

---

## Performance

- **Full ETL Runtime:** ~80 seconds for 4 games
- **Phase 1:** ~30 seconds (data loading)
- **Phase 3B:** ~5 seconds (static tables)
- **Phase 4-11:** ~45 seconds (calculations and analytics)

---

## Related Documentation

- [ETL Data Flow](ETL_DATA_FLOW.md) - Detailed data flow diagrams
- [Core Modules](CORE_MODULES.md) - Function-level documentation
- [Code Walkthrough](CODE_WALKTHROUGH.md) - Step-by-step code walkthrough
- [Table Registry](../../data/TABLE_REGISTRY.md) - Complete table documentation
