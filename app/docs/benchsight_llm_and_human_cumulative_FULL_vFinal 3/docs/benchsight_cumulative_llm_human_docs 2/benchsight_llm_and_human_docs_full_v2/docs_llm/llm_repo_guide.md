# LLM Repo Guide – BenchSight / BLB Project

This guide tells you, the LLM, how the main repository is structured,
what each part is for, and how to reason about changes.

The actual code lives in the user’s repo; this file describes how to
navigate it conceptually.

---

## 1. High-Level Folder Structure

You can assume something like this (names may vary slightly):

- `src/`
  - `stage/`
  - `intermediate/`
  - `mart/`
  - `tracker/`
  - `ml/`
  - `utils/`
- `sql/`
  - `stage/`
  - `intermediate/`
  - `mart/`
- `data/`
  - `raw/`
  - `output/`
- `docs/`

### 1.1. `src/stage/`

**Purpose:** Load raw Excel (BLB_Tables + game tracking files) into Postgres.

Typical components:

- `stage_load.py` – logic to load one game and the master BLB workbook.
- `stage_batch.py` – loops over all game folders.
- `util_sql_merge.py` – generic MERGE-based upsert logic.
- Orchestrators that can:
  - Load **only** games, **only** master, or both.
  - Filter by `game_id` or component (events, shifts, xy, video).

**Your job:** When user asks to change staging, preserve:

- Column normalization (lowercase snake_case).
- Natural keys for incremental merging:
  - Events: `(game_id, event_index)`.
  - Shifts: `(game_id, shift_index, team_side, player_number)`.
  - XY: `(game_id, linked_event_id, player_number[, team])` etc.

### 1.2. `src/intermediate/`

**Purpose:** Transform staging tables into modeling-friendly structures.

Typical tables here:

- `events_long` / `events_wide`.
- `shifts_long` / `shifts_logical` (with cumulative shift numbers).
- `chains_sequence_play` and similar tables (sequence_index, play_index, linked_event_id).
- Rating context tables (min/max/avg line ratings, matchup contexts).

**Your job:**

- Implement complex hockey logic here (goal chains, zone entry sequences,
  counter-rush, etc.) in **SQL** or Python+SQL.
- Keep each script **idempotent** (drop/recreate derived tables or use MERGE).
- Make sure outputs align with the table definitions in `table_catalog.csv`.

### 1.3. `src/mart/`

**Purpose:** Build the **datamart** for BI & ML.

This is where we:

- Create fact tables:
  - `fact_events`
  - `fact_shifts`
  - `fact_boxscore_player`
  - `fact_xg_shots`
  - `fact_sequences`
  - `fact_plays`
- Create dimension tables:
  - `dim_players`
  - `dim_teams`
  - `dim_games`
  - `dim_dates` (from BLB_Tables)
  - `dim_zones`, `dim_event_types`, etc.

**Your job:**

- Maintain the **grain** of each fact table as described in `table_catalog.csv`.
- Ensure keys follow the naming scheme (e.g. `event_id`, `shift_id`)
  and map back to `(game_id, event_index, ...)` as needed.
- Add new stats as **columns** in appropriate fact tables, not random new tables.

### 1.4. `src/tracker/`

**Purpose:** Provide a UI to track games with:

- Event logging (type/detail, players, success flags).
- Shift logging (on-ice players, strengths, start/end times).
- XY capture for rink/net.
- Video-linked timestamps (YouTube URLs with `?t=` seconds).

This may use Flask, Dash, or another web stack.

**Your job:**

- Honor the Excel tracker **business rules** (see human docs & BLB tracking files).
- Ensure the tracker writes to staging-compatible tables or a special `tracker_*` schema.
- Keep UI workflow efficient: few clicks, minimal typing, defaults from context.

### 1.5. `src/ml/`

**Purpose:** Experiments and future pipelines for ML:

- xG models using XY + context features.
- Player comps using microstats & ratings.
- Line matchup models, etc.

**Your job:**

- Base ML feature extraction on the **datamart** tables, not raw staging.
- Document features in terms of stats catalog IDs.

### 1.6. `sql/`

Mirrors the Python structure. For example:

- `sql/stage/*.sql` – staging tables & merges.
- `sql/intermediate/*.sql` – long/wide, chains, rating context transforms.
- `sql/mart/*.sql` – fact/dim creation & population.

Use these as canonical definitions of table shapes.

---

## 2. Table & Stat Catalogs

Before making any deep changes, always load:

- `docs_llm/table_catalog.csv`
- `docs_llm/stats_catalog.csv`

Use these to:

- Know which tables already exist and what their grains are.
- Know which stats are already defined and how.

If you invent new tables or stats, suggest rows to add to these catalogs.

---

## 3. How to Help with Common Tasks

### 3.1. “Add a new advanced stat”

1. Identify its level (player/team/line/game/sequence).
2. Find appropriate fact table in `table_catalog.csv`.
3. Express its formula in terms of existing columns/stats in `stats_catalog.csv`.
4. Propose:
   - A new column in the fact table (SQL).
   - DAX measures if needed for Power BI.
   - Optional: new stat row in `stats_catalog.csv` with `implemented=planned`.

### 3.2. “Fix a bug in the tracker output”

1. Compare expected outputs (based on BLB tracking Excel format) vs.
   current staging/intermediate tables.
2. Identify which layer is wrong:
   - Tracker UI → Stage mapping.
   - Stage → Intermediate transforms.
3. Suggest changes so that final `events_long`, `shifts_long` etc.
   match the expected 18969-style tracking outputs.

### 3.3. “Extend event chains / sequences / plays”

1. Review rules in human docs + stats catalog (look for chain/sequence stats).
2. Propose SQL CTEs that:
   - Order events by game_id, period, running time.
   - Flag possession changes and zone changes.
   - Define sequence_id, play_id, counter_rush_id as appropriate.

### 3.4. “Design new Power BI visuals”

1. Identify the fact table(s) involved.
2. Use DAX patterns from `powerbi_measures_example.dax`.
3. Ensure measures respect grain and filter context.

---

## 4. Style & Quality Expectations

- Always explain *why* your suggestion fits the architecture.
- Use comments liberally in code examples.
- Keep table and column names consistent and descriptive.
- When in doubt, bias toward making the user’s life easier as an analyst:
  - Fewer joins, clear naming, reusable metrics.

This project is meant to be both a learning playground and a foundation
for a potentially commercial product (BenchSight), so clarity matters.
