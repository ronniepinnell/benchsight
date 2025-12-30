
# BenchSight – Repository Overview & MVP Run Guide

This document is meant to be a **single, clear entrypoint** for both humans and LLMs to understand how the BenchSight project hangs together and how to run a minimal end‑to‑end MVP.

---

## 1. What BenchSight Is

BenchSight is a **hockey analytics platform** designed to take:

- **Static league/team/player data** (BLB tables),
- **Per‑game tracking data** (events, shifts, x/y coordinates, shots, video timing),
- And produce **clean, analysis‑ready tables** in a hockey‑flavored data mart for:

- Beer league / rec teams (game reports, player scorecards),
- Scouting‑style microstats (entries, exits, passing sequences, matchups),
- Long‑term career tracking and ML (player comps, xG, style clustering),
- Future: computer‑vision‑driven tracking and NHL‑style analytics.

It combines:

- A **data model** (dims/facts, chains),
- An **ETL pipeline** (Python + SQL, stage → mart),
- A **tracker UI concept** (replacing Excel forms),
- **BI layers** (Power BI + Python dashboards),
- And a **commercial framing** (“BenchSight”) for potential productization.

---

## 2. High‑Level Repo Layout (Conceptual)

Folders may be named slightly differently in your local repo, but conceptually you have:

- `README.md` (top‑level)  
  Short description, quickstart, repo map.

- `README_LLM.md`  
  Same idea but targeted at LLMs: where to find schema, stats, tables, ETL, BI, ML docs.

- `docs/` – **Documentation hub**
  - `MASTER_DOCUMENTATION.md` – Overall system description and narrative.
  - `MASTER_HANDOFF.md` – “If you’re inheriting this project, start here.”
  - `SCHEMA.md` – Table‑by‑table schema explanations.
  - `schema_diagram.mermaid` / `schema_er_diagram.png` – ER/Star diagrams.
  - `benchsight_tables_catalog.csv` – Canonical list of dim/fact tables.
  - `benchsight_stats_catalog_master_ultimate.csv` – Canonical list of stats & microstats.
  - `BenchSight_Data_Dictionary.csv` – Column‑level dictionary for key tables.
  - `BenchSight_Status_README.md` – What’s MVP vs WIP vs future.
  - `benchsight_feature_backlog_and_roadmap.txt` – Feature backlog & roadmap.
  - `INSPIRATION_AND_RESEARCH.md` – Links & notes from other hockey stats sites.
  - `ml_ideas.md` – ML use‑cases and modeling ideas.
  - `POWERBI_GUIDE.md` – Star schema & report layout ideas for Power BI.
  - Additional architecture & flow diagrams (PNG/SVG/Mermaid/HTML).

- `src/` – **Python package**
  - `main.py` – Orchestrator / user entrypoint.
  - `config/` – Config helpers for DB, paths, modes.
  - `io/` – Utilities to read/write Excel, CSV, database tables.
  - `staging/` – Load BLB static tables and raw tracking into stage schema.
  - `intermediate/` – Transformations long ↔ wide, chains, ratings, microstats.
  - `mart/` – Final mart‑ready table builders.
  - `tracker/` – Tracker UI / API scaffolding (present or planned).
  - `logging_utils/` – Logging and simple run diagnostics.

- `sql/` – **Postgres DDL/DML**
  - `stage_schema.sql` – Base stage tables for BLB and raw tracking.
  - `mart_schema.sql` – Dim/fact create scripts.
  - `mart_populate.sql` – Insert/select scripts building mart tables from stage/intermediate.
  - `chains.sql` – Sequence/play/linked chains and derived chain tables.
  - `boxscore.sql` – Aggregations into player/game/team boxscores.

- `data/`
  - `raw/`
    - `BLB_Tables.xlsx` – BLB dim/fact seed tables.
    - `tracking/` – One folder per game with tracking Excel files.
  - `output/`
    - **All mart tables as CSVs**, appended across all processed games.

- `dashboard/`
  - Dash/Flask app scaffolding:
    - Game summary page,
    - Player card page,
    - Line combo & matchup page,
    - Microstats page.

- `powerbi/`
  - `.pbix` files, DAX measures, relationship screenshots and schemas for:
    - Game summary,
    - Player scorecards,
    - Line combos & matchup,
    - Season‑over‑season team/player trends.

- `tests/`
  - Unit tests & data quality checks:
    - Schema conformance,
    - Key uniqueness,
    - Basic stat sanity (shots, goals, TOI match boxscore).

---

## 3. Coherent Story – What’s Strong

Across the docs and code, BenchSight already has:

- A clear **domain story**: beer league → microstats → scouting → NHL‑style analytics.
- A serious **metric layer**: the stats catalog covers:
  - Corsi, Fenwick, xG‑style constructs,
  - Entry/exit success,
  - Passing chains,
  - Rating‑aware context (opponent quality, teammate quality),
  - Matchups and line vs line effects.
- A realistic **data model**:
  - `dim_player`, `dim_team`, `dim_game`, `dim_season`, `dim_date`, etc.
  - `fact_events_long`, `fact_events_wide`,
  - `fact_shifts_logical_player`, `fact_shifts_line`,
  - `fact_boxscore_player`, `fact_boxscore_team`,
  - `fact_sequence_chain`, `fact_play_chain`, `fact_linked_chain`,
  - `fact_xY_event_locations`, `fact_shot_locations`.
- Thoughtful **ETL / architecture docs**:
  - Stage → intermediate → mart,
  - How chains and rating context are layered,
  - How microstats roll up into boxscores.

This is the kind of structure a real team could extend, not a throwaway experiment.

---

## 4. Known Weaknesses / Risks

1. **Doc sprawl & redundancy**
   - Multiple overlapping docs (older generations) exist.
   - Not all of them clearly say which ones are canonical vs outdated.

2. **Slight drift between docs & code**
   - Some advanced stats and chains are described in docs but only partially implemented.
   - Tracker UI is conceptually specified, but the production‑ready implementation is still a WIP.

3. **Cognitive load**
   - The project has grown to include:
     - BLB static tables,
     - Manual + UI tracker,
     - X/Y and shot data,
     - Chain logic,
     - Rating‑aware context,
     - Commercial framing + NHL comparators.
   - Without a clear MVP path, it can be overwhelming.

These are all fixable with better entrypoints and a strict MVP run story.

---

## 5. Recommended Improvements (Bullet‑Pointed)

### 5.1 Canonical entrypoint for humans

- A concise **root README** that:
  - Explains BenchSight in 3–4 plain‑English paragraphs.
  - Lists the most important directories and what they’re for.
  - Tells a new person **which 3–5 docs to read first**.

### 5.2 Canonical entrypoint for LLMs

- A tightened `README_LLM.md` that:
  - Points explicitly to:
    - `docs/SCHEMA.md`
    - `docs/schema_diagram.mermaid` or `.png`
    - `docs/benchsight_tables_catalog.csv`
    - `docs/benchsight_stats_catalog_master_ultimate.csv`
    - `docs/BenchSight_Status_README.md`
    - `docs/benchsight_feature_backlog_and_roadmap.txt`
  - Explains how to use them:
    - Stats catalog → formulas and required tables.
    - Tables catalog + schema → how to join tables and where columns live.
    - Backlog → what’s MVP vs future.

### 5.3 Mark archive vs current docs

- Keep these at the root of `docs/` as **canonical**:
  - `MASTER_DOCUMENTATION.md`
  - `SCHEMA.md`
  - `STATS_DICTIONARY.md`
  - `benchsight_stats_catalog_master_ultimate.csv`
  - `benchsight_tables_catalog.csv`
  - `BenchSight_Data_Dictionary.csv`
  - `BenchSight_Status_README.md`
  - `benchsight_feature_backlog_and_roadmap.txt`
- Move older or superseded docs to `docs/archive/` and mark at the top:
  - “**Status: Archived. Superseded by `<X>`**”.

### 5.4 Tight ETL run story

- One orchestrator: `src/main.py`:
  - Reads config.
  - Asks the user (or reads flags):
    - Refresh BLB static tables? (Y/N)
    - Which game_ids to ingest from `data/raw/tracking/`?
    - Rebuild stage+mart? (Y/N)
    - Export mart tables to `data/output/` as CSV? (Y/N)
- One doc: `docs/ETL_RUN_GUIDE.md`:
  - Local setup (Python env, Postgres DSN, config file).
  - Exact command to run (e.g., `python -m src.main`).
  - Where to look for outputs (`data/output/fact_*`, `dim_*` CSVs).

### 5.5 Concrete examples

- At least one **event chain** example:
  - Map a multi‑step rush / cycle into events, chains, boxscore.
- At least one **shift‑level microstat** example:
  - Show entries/exits, passes, shots, and how they populate shift and boxscore tables.
- At least one **boxscore line** example:
  - For a single player in a game: show where each stat comes from.

### 5.6 Known doc ↔ code drift section

In `MASTER_DOCUMENTATION.md` or `BenchSight_Status_README.md`, clearly list:

- Tracker UI features specified but not fully implemented.
- CV / real‑time / xG items that are currently design‑only.
- Stats that are defined in the catalog but not yet fully wired end‑to‑end.

---

## 6. Strict MVP Run Path (0–1 Month)

This is a pragmatic “minimum slice” of BenchSight that:

- Works end‑to‑end,
- Produces real outputs for your team,
- And is impressive enough for resume / portfolio purposes.

### 6.1 MVP scope

**Goal:**  
Given BLB static tables + multiple tracked games, build:

- A clean **data mart** with:

  - Core dims: `dim_player`, `dim_team`, `dim_game`, `dim_date`, `dim_season`.
  - Core facts:
    - `fact_events_wide` (one row per event + context),
    - `fact_shifts_player_logical` (one row per logical shift per player),
    - `fact_boxscore_player_game` (one row per player per game),
    - `fact_game_tracking_status` (what’s logged for each game).

- Export those facts & dims as CSVs in `data/output/`.
- Build **one Power BI report** and **one Python/Dash view** that both show:
  - Game summary page.
  - Player game scorecards.
  - Line combo / matchup overview.
  - A few core microstats (entries, exits, CF/FF, TOI, primary assists, etc.).

No CV, no NHL comps yet – just rock‑solid tracking analytics for your own games.

### 6.2 MVP run steps – conceptual

1. **Configure environment**
   - Create a Python venv.
   - Install dependencies (`requirements.txt`).
   - Ensure you have a Postgres instance (local, Docker, or cloud).
   - Configure connection in `config.ini` or `.env`:
     - Host, port, DB name, user, password.
   - Set data paths to:
     - `data/raw/BLB_Tables.xlsx`
     - `data/raw/tracking/` (per‑game folders)
     - `data/output/` (for exports).

2. **Run `python -m src.main` (or `python src/main.py`)**
   - Main script should:
     1. Load BLB static tables to stage (optional “refresh all BLB” step).
     2. Scan `data/raw/tracking/` for tracking workbooks.
     3. For each selected game_id:
        - Parse events & shifts sheets into stage tables.
        - Run validation / data‑quality checks.
     4. Build intermediate tables:
        - Long ↔ wide for events & shifts.
        - Player logical shifts.
        - Rating context joins.
        - Basic chains (linked, sequence, play) at MVP level.
     5. Build mart tables:
        - All core dims.
        - `fact_events_wide`.
        - `fact_shifts_player_logical`.
        - `fact_boxscore_player_game`.
        - `fact_game_tracking_status`.
     6. Export mart tables to CSV in `data/output/`.

3. **Open Power BI**
   - Connect to `data/output/` folder as a folder source.
   - Use relationships as documented in `SCHEMA.md` and the ER diagram.
   - Start with one PBIX:
     - Page 1: Game overview.
     - Page 2: Player scorecards.
     - Page 3: Line combos & matchups.

4. **Optional: Run Dash dashboard**
   - `python -m dashboard.app`.
   - Use same CSVs as data source (or query Postgres directly).
   - Mirror the three main pages from Power BI.

### 6.3 MVP deliverables checklist

- [ ] **Code:** `src/main.py` orchestrator is runnable and documented.
- [ ] **DB:** Stage & mart schemas created in Postgres.
- [ ] **Data:** Multiple games processed from tracking Excel → mart tables.
- [ ] **Exports:** All key dim & fact tables exported to `data/output/` as CSV.
- [ ] **Docs:**
  - [ ] `README.md` explains how to run MVP.
  - [ ] `README_LLM.md` points LLMs to canonical docs.
  - [ ] `SCHEMA.md` + schema diagram kept in sync with actual tables.
  - [ ] `benchsight_stats_catalog_master_ultimate.csv` has a clear “MVP stats” flag.
- [ ] **BI:** One Power BI report with:
  - [ ] Game overview,
  - [ ] Player scorecards,
  - [ ] Line/line matchup view.
- [ ] **Status:** `BenchSight_Status_README.md` clearly separates:
  - MVP features (done),
  - Short‑term backlog (0–3 months),
  - Longer‑term (NHL comps, CV, real‑time, etc.).

---

## 7. How to Use This Doc

- As a **human**:  
  Treat this as the “orientation doc” – it tells you where to look and what to run first.

- As an **LLM**:  
  Use this as a pointer map:
  - When asked about schemas → open `docs/SCHEMA.md` and the tables catalog.
  - When asked about stats/microstats → open `benchsight_stats_catalog_master_ultimate.csv`.
  - When asked about how to run the project → use the MVP run path above.
  - When asked about future work → consult `benchsight_feature_backlog_and_roadmap.txt`.
