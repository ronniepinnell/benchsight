# BenchSight / BLB Repo – Human-Friendly Guide

This is a **plain English** tour of how your project is organized and how
the pieces fit together.

You don’t need to memorize all of it – think of it as a map you can come
back to when you’re lost.

---

## 1. Big Picture

You’re building a system that can:

1. **Track hockey games** (events, shifts, XY locations, video).
2. **Turn that tracking into data** (tables).
3. **Turn that data into insight** (stats, charts, ML models).

There are three main layers of data:

1. **Raw** – Excel files and CSVs exactly as you or the league produce them.
2. **Staging / Intermediate** – cleaned & transformed tables in Postgres.
3. **Datamart** – clean “fact” and “dimension” tables designed for
   Power BI, dashboards, and ML.

The tracker UI (web app) is a more user-friendly version of your current
Excel tracking sheet.

---

## 2. What the Folders Mean (Conceptually)

In your repo (outside this zip), you’ll see folders like:

- `src/`
  - Code that moves and transforms data:
    - `stage/` – load Excel → Postgres staging.
    - `intermediate/` – long/wide transforms, chains, rating context.
    - `mart/` – final datamart tables.
    - `tracker/` – web UI for tracking games.
    - `ml/` – notebooks and scripts for advanced models.
- `sql/`
  - SQL scripts that define and populate tables in each layer.
- `data/`
  - `raw/` – your BLB_Tables and per-game folders (e.g., 18969).
  - `output/` – CSVs of datamart tables to feed Power BI.
- `docs/`
  - Project documentation, diagrams, stat definitions, notes, etc.

The **single orchestrator .py file** ties everything together by asking
you (via prompts) what you want to do:

- Ingest BLB_Tables?
- Ingest new games?
- Run full pipeline to datamart?
- Launch tracker UI?
- Export CSVs for Power BI?

---

## 3. Stats & Tables

Two very important files in `docs_llm/` (and summarized in `docs_human/`):

- `stats_catalog.csv` – list of all stats and microstats
  (what they mean and how to compute them).
- `table_catalog.csv` – list of all key tables:
  - What each table represents.
  - Grain (one row = what?).
  - Keys and relationships.
  - Which layer (stage / intermediate / mart).

If you’re ever unsure which table to use in Power BI or a notebook,
`table_catalog.csv` is the place to look.

If you’re wondering “how do we define controlled zone entry?” or
“what exactly is Corsi here?”, check `stats_catalog.csv` and the
human summary of it.

---

## 4. How You Might Work Day-to-Day

Here’s an example workflow for you as an analyst / builder:

1. **Track a game** using the Excel tracker or the web tracker UI.
2. **Run the orchestrator .py file** and choose:
   - “Ingest BLB tables (if updated).”
   - “Ingest tracking for game X.”
   - “Run transforms → datamart.”
   - “Export datamart CSVs to `data/output`.”
3. **Open Power BI** and refresh from those CSVs.
4. Explore pages like:
   - Game summary.
   - Player boxscore & microstats.
   - Line combos & matchups.
   - xG charts.
5. For deeper analysis, open a **Python notebook** in `ml/` and:
   - Load datamart tables.
   - Build or tweak ML models.
   - Generate custom visuals.

---

## 5. Where to Look for More Detail

Inside `docs_human/`:

- `human_stats_catalog_summary.md` – explains stats in words.
- `human_flows_and_schemas.md` – shows diagrams of data flow and schema.
- `human_powerbi_guide.md` – ideas for Power BI pages, including what tables
  to use and which measures to build.

Use these like reference chapters in a book. You don’t have to read them
all in one sitting – just open the one that matches what you’re working on.

The matching LLM docs in `docs_llm/` tell AI assistants the exact same story,
but in a more structured way to help them write code that fits your design.
