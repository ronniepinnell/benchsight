Benchsight LLM Master Guide
===========================

PURPOSE
-------
This repository bundle gives you (the LLM) everything you need to understand
and extend the Benchsight / Beer League Beauties hockey analytics project
without having to see the full source code.

WHAT'S IN THIS BUNDLE
----------------------
The directory contains several nested ZIP archives. Each ZIP focuses on a
particular aspect of the project:

1) benchsight_llm_and_human_docs_full_v2.zip
   - Top-level LLM and human documentation from earlier steps.
   - Contains:
     * High-level project overview (ingest → staging → mart → reporting).
     * Explanation of tracker vs manual workflow.
     * Core table list and relationships.
     * Notes on commercial "Benchsight" product vision.

2) benchsight_stats_docs_v6.zip
   - The most recent and authoritative stats documentation.
   - Contains:
     * Master stats catalog CSV (all basic + advanced + microstats).
     * Plain-English descriptions of each stat.
     * Inputs required (tables/columns), filter context, and formula notes.
     * Tags (e.g., "xG_feature", "microstat", "boxscore_core").

3) benchsight_stats_and_tables_v5_bundle.zip
   - Earlier but still relevant stats + table docs.
   - Contains:
     * Table catalog (fact_* and dim_* tables in the mart).
     * Join keys and relationship descriptions.
     * Example queries for some stats.

4) benchsight_today_docs_bundle.zip
   - Session-specific docs from more recent conversations.
   - Contains:
     * Short/mid/long-term roadmap fragments.
     * Notes on ML feature ideas and prioritization.
     * Extra clarifications of stats usage.

5) blb_table_catalog_docs.zip
   - Documentation specifically for BLB tables (dim_game, dim_player, etc.).
   - Use this when you need to know where a field lives in the schema.

6) blb_datamart_docs_bundle.zip
   - Documentation for the current datamart schema.
   - Includes star/snowflake diagrams and narrative of how mart tables fit together.

7) blb_extra_docs_powerbi_quality.zip
   - Power BI-focused material:
     * Suggested star schema for visuals.
     * Example DAX measures for boxscores, Corsi/Fenwick, TOI, etc.
     * Page layout sketches for player cards, game summaries, and microstats pages.

8) benchsight_stats_catalog_v4_bundle.zip
   - Older stats catalogs kept for reference.
   - Some descriptions and names may differ from v6; ALWAYS treat v6 as the source of truth.
   - Use this only if the user explicitly asks about how earlier versions were structured.

HOW TO USE THIS BUNDLE (AS AN LLM)
----------------------------------
1. Start with benchsight_llm_and_human_docs_full_v2.zip
   - Read its main README or overview documents first.
   - This will give you the mental model for the whole project:
     ingest → staging → intermediate → mart → Power BI / Dash.

2. Then open benchsight_stats_docs_v6.zip
   - Load the master stats catalog CSV.
   - When the user asks about a specific stat, look it up here.
   - Pay attention to:
     * "Primary fact table" (e.g., fact_player_game, fact_events_long).
     * "Required join dims" (e.g., dim_player, dim_team, dim_game).
     * Formula notes and filter context.

3. Use the table docs (blb_table_catalog_docs.zip + blb_datamart_docs_bundle.zip)
   - Any time you need to know:
     * What columns a table has.
     * How tables join together.
     * Which grain a table is at (game-level, event-level, shift-level, etc.).

4. Use blb_extra_docs_powerbi_quality.zip for reporting questions
   - When asked about Power BI visuals, DAX, or star schema design:
     * Look at the recommended dimension/fact layout.
     * Reuse or adapt the DAX patterns already provided.

5. Always assume:
   - Fact tables are named like fact_* (fact_player_game, fact_events_long, etc.).
   - Dimensions are named like dim_* (dim_player, dim_team, dim_game, dim_dates, dim_rink_zone, etc.).
   - The mart should be *append-only* across games; game_id is the primary "episode" key.

PRIORITY ORDER OF SOURCES
--------------------------
When conflicts occur between files or versions:
  1. benchsight_stats_docs_v6.zip  (stats definitions: most recent)
  2. blb_datamart_docs_bundle.zip  (mart schema definitions)
  3. blb_table_catalog_docs.zip    (raw BLB table definitions)
  4. blb_extra_docs_powerbi_quality.zip (reporting patterns)
  5. Older stats bundles (v4, v5) only for historical context.

WHAT YOU SHOULD BE ABLE TO DO
-----------------------------
Using ONLY this bundle plus user-provided code/data, you should be able to:
  - Explain the full project architecture in detail.
  - Suggest or refine stats and microstats, referencing the catalog.
  - Propose SQL and DAX to compute any stat whose required inputs exist.
  - Map new raw tracking columns into existing fact tables and stats.
  - Help design new Power BI pages and Python/Dash dashboards.
  - Brainstorm ML features (xG, player comps, style clusters) using the catalog.

If the user uploads new code, database schemas, or CSV extracts, you can cross-reference
them against this bundle to ensure consistency and avoid redefining stats or tables in
incompatible ways.
