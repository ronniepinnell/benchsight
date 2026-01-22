# Core ETL Modules Documentation

**Function-level documentation for core ETL modules.**

Last Updated: 2026-01-22

---

## Overview

This document provides detailed documentation for the core ETL modules, including function signatures, data flow, dependencies, and examples.

---

## Module: `src/core/base_etl.py`

**Purpose:** Main ETL orchestrator for Phase 1 (BLB data loading, tracking data processing, derived tables).

### Key Functions

#### `main() -> None`
Main entry point for base ETL execution.

**Flow:**
1. Load BLB tables from Excel
2. Build player lookup
3. Load tracking data
4. Create derived tables
5. Validate output

**Dependencies:** None (reads from `data/raw/`)

**Output:** Creates `fact_events`, `fact_event_players`, `fact_shifts`, `fact_shift_players`

---

## Module: `src/core/table_writer.py`

**Purpose:** Centralized table writing with Supabase integration.

### Key Functions

#### `save_output_table(df: pd.DataFrame, name: str, output_dir: Path) -> None`
Saves DataFrame to CSV and optionally to Supabase.

**Parameters:**
- `df`: DataFrame to save
- `name`: Table name (without .csv extension)
- `output_dir`: Output directory path

**Dependencies:** `src/core/safe_csv.py` for CSV writing

---

## Module: `src/core/key_utils.py`

**Purpose:** Key generation and formatting utilities.

### Key Functions

#### `format_key(prefix: str, *parts: str) -> str`
Formats a composite key in {XX}{ID}{5D} format.

**Example:**
```python
format_key("EV", "18969", "123")  # Returns "EV18969123"
```

#### `generate_event_id(game_id: str, event_index: int) -> str`
Generates event_id key.

**Format:** `EV{game_id}{event_index:05d}`

---

## Module: `src/tables/dimension_tables.py`

**Purpose:** Creates all static dimension tables.

### Key Functions

#### `create_all_dimension_tables() -> None`
Creates all 55+ dimension tables.

**Tables Created:**
- `dim_player`
- `dim_team`
- `dim_league`
- `dim_season`
- `dim_schedule`
- Plus 50+ other dimension tables

**Dependencies:** Phase 1 (for player/team data)

---

## Module: `src/tables/core_facts.py`

**Purpose:** Creates core player and team statistics tables.

### Key Functions

#### `create_all_core_facts() -> None`
Creates core fact tables.

**Tables Created:**
- `fact_player_game_stats`
- `fact_team_game_stats`

**Dependencies:** Phase 1 (events, shifts), Phase 3B (dimensions)

---

## Module: `src/core/add_all_fkeys.py`

**Purpose:** Adds foreign key columns to all tables.

### Key Functions

#### `main() -> None`
Adds foreign keys to all tables.

**Process:**
1. Load all tables
2. Identify FK relationships
3. Add FK columns
4. Save updated tables

**Dependencies:** All previous phases

---

## Module: `src/core/etl_phases/`

**Purpose:** Modularized ETL phase functions.

### Sub-modules

#### `event_enhancers.py`
- `enhance_event_tables()` - Adds FKs and derived columns to events
- `enhance_events_with_flags()` - Adds flags (is_goal, etc.)

#### `shift_enhancers.py`
- `enhance_shift_tables()` - Adds FKs and derived columns to shifts
- `enhance_shift_players()` - Enhances shift player data

#### `reference_tables.py`
- `create_reference_tables()` - Creates reference/lookup tables

#### `validation.py`
- `validate_all()` - Comprehensive validation

---

## Data Flow Examples

### Goal Counting Flow

```
fact_events (raw)
    ↓
Filter: event_type == 'Goal' AND event_detail == 'Goal_Scored'
    ↓
Count per player_id, game_id
    ↓
fact_player_game_stats.goals
```

### Foreign Key Addition Flow

```
fact_events (without FK)
    ↓
Load dim_player
    ↓
Merge on player_id
    ↓
Add dim_player.player_key column
    ↓
fact_events (with FK)
```

---

## Related Documentation

- [ETL Phase Flow](ETL_PHASE_FLOW.md) - Phase overview
- [Code Walkthrough](CODE_WALKTHROUGH.md) - Step-by-step guide
