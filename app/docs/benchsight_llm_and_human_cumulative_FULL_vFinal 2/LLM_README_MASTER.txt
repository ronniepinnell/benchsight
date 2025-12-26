BenchSight / BLB – Master LLM README
====================================

You are reading the **master entrypoint** for all BenchSight + Beer League Beauties
documentation that the user has provided.

High-level project idea
-----------------------
BenchSight is an end-to-end hockey analytics and tracking project:
- Takes **manual + UI tracker** inputs for shifts, events, and XY coordinates.
- Normalizes them into **Postgres + CSV data marts**.
- Powers **Power BI dashboards** and **Python/Plotly Dash web UIs**.
- Long-term: extends to NHL-scale data (MoneyPuck/NHL API), ML/xG models,
  player similarity, and commercial products for junior → pro teams.

How this bundle is organized
----------------------------
Root of this zip:
- `LLM_README_MASTER.txt` (this file): where to look & how to think.
- `docs/` – narrative documentation, diagrams, schemas, roadmaps, how-to guides.
- `catalogs/` – machine-readable CSV catalogs (stats, tables) the LLM should use first.

Inside `docs/` you will find:
- `benchsight_cumulative_llm_human_docs 2/` and `benchsight_cumulative_llm_human_docs_v3/`:
  Earlier comprehensive doc bundles – design, schemas, ETL notes, Power BI notes.
- `nhl_resources/` and related files:
  Notes on NHL data sources, xG resources, and BLB↔NHL alignment.
- `stats_and_tables/` (or similarly-named subfolder):
  Human-readable descriptions of stats, tables, and ETL flows.
- Any `*_roadmap*` or `*_timeline*` documents:
  Implementation plan split into **now / 0–1 month / mid-term / long-term**.
- `misc_zips/`:
  Some earlier nested bundles preserved intact for reference.

Inside `catalogs/` you will find:
- `benchsight_stats_catalog_master_ultimate.csv`
    The *single source of truth* for stat & microstat definitions.
- `benchsight_mart_table_catalog.csv` (or similarly named)
    Table-level catalog for BLB datamart (name, grain, primary keys, foreign keys).
- `benchsight_tables_catalog.csv` / `benchsight_stats_catalog_master.csv`
    Older versions kept for lineage – prefer the *_ultimate versions when in doubt.

How to use this as an LLM
-------------------------
1. **Start here**: skim this file to understand the goal.
2. Then open `catalogs/benchsight_stats_catalog_master_ultimate.csv` and
   `catalogs/benchsight_mart_table_catalog.csv` to ground yourself in stats & tables.
3. Use the text docs under `docs/` to answer questions like:
   - “What does this table represent?”
   - “How does data flow from tracker → staging → mart → dashboard?”
   - “What are the short/mid/long term goals?”
4. When generating new code or logic:
   - Reuse existing names, keys, and stats from the catalogs whenever possible.
   - If you invent a new stat, describe it in the *same structure* as the catalog.
5. Respect **grains & relationships**:
   - Facts: game, shift, event, player-shift, event-chain, xG, etc.
   - Dims: player, team, game, season, rink zones, dates, etc.
6. For NHL/BLB hybrid work:
   - Look in docs for `nhl_` prefixed files and the BLB↔NHL mapping notes.
   - Keep BLB schema but map NHL columns into it with a clear ETL layer.

Human usage notes
-----------------
Humans reading this bundle should:
- Start with any `HUMAN_README*.md` inside `docs/` for a friendlier overview.
- Use the catalog CSVs as “data dictionaries” when building SQL, Power BI, or ML.
- Treat this zip as **documentation only** – actual source code, SQL, and data
  live in the main BLB / BenchSight repository and database.

If you need to add new docs:
- Add them under `docs/` with clear names and short intros.
- Update or extend the catalogs under `catalogs/` rather than overwriting blindly.

This file is intentionally high-level – it should give both LLMs and humans
a clear map of where other information lives, and what each group of files
is roughly about.