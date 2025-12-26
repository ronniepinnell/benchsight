BenchSight / Beer League Beauties – Human README
================================================

What this folder is
-------------------
This folder collects the *documentation side* of the BenchSight / BLB project:
  • Stat and microstat catalogs
  • Table/datamart catalogs
  • Power BI and dashboard design notes
  • Roadmaps and feature backlogs
  • LLM-specific guidance (so AI helpers can use all of this effectively)

If you’re a human trying to understand or extend the project, start here.

Key files to know about
-----------------------
1) stats/benchsight_stats_catalog_master_ultimate.csv
   - Master list of every stat/microstat we’ve designed so far.
   - For each stat you get:
       * ID (BSxx), name, short label
       * Level (event, shift, game, season, player, team, line, goalie)
       * Category (shot quality, transition, forecheck, etc.)
       * Plain-English description
       * Implementation-oriented logic / formula
       * Required and optional input data
       * Notes on filter context and data sources
       * Whether it can be computed from league box scores only
       * Implementation status and extra data needed

   Use this when:
     - You want to know what “Corsi For” or a microstat actually means here.
     - You’re wiring up a new measure in SQL, Python, or DAX.
     - You’re designing new visuals (player cards, team dashboards, etc.).

2) Table and Datamart Catalogs
   - Found in subfolders unpacked from:
       * blb_table_catalog_docs
       * blb_datamart_docs_bundle
   - These describe:
       * All dimension and fact tables in the BLB mart
       * Column names and types
       * Keys and relationships
       * Which parts of the pipeline produce them (stage → intermediate → mart)

   Use these when:
     - You want to understand the data model behind the stats.
     - You’re adding a new table or modifying an existing one.
     - You’re building Power BI models or ML pipelines.

3) Power BI / Dashboard Design Notes
   - Found in subfolders unpacked from:
       * blb_extra_docs_powerbi_quality.zip
       * benchsight_today_docs_bundle.zip
       * benchsight_llm_and_human_docs_full.zip
   - These include:
       * Example report layouts (game summary, player card, line combos, microstats)
       * Suggested star schemas and relationships
       * Example DAX measures and patterns

   Use these when:
     - You’re building out the actual reports in Power BI.
     - You want ideas for dashboards in Dash/Streamlit/Render.
     - You want to understand how advanced stats show up visually.

4) LLM README (README_FOR_LLM.txt)
   - This explains to AI assistants how to navigate all of this,
     which is handy if you plan to “pair program” with an LLM.

How this ties back to the code project
--------------------------------------
The code side of the project (the repo with src/, sql/, data/, etc.) does the following:
  1. Ingests BLB_Tables (fairly static dims/facts from your league sheets).
  2. Ingests game tracking folders (shifts, events, XY, shots, video times).
  3. Runs a staged ETL:
       - Stage: raw to cleaned, one-to-one with sources.
       - Intermediate: wide/long transformations, event/shift logic, ratings context.
       - Mart: reporting-ready fact/dim tables for Power BI + ML.
  4. Optionally runs tracker UI flows (web UI for in-game/retro tracking).
  5. Exports CSVs of the mart tables for Power BI on Windows/Parallels.

This documentation bundle describes *what* those tables and stats represent,
and how everything is supposed to fit together conceptually.

Roadmap & commercial ideas
--------------------------
Within the stats and docs bundles you’ll also find:
  • Short / mid / long-term goals for:
      - Beer league teammates (usable dashboards)
      - Portfolio / resume (solid case study)
      - Commercial BenchSight product (junior to pro)
  • How advanced pieces (computer vision, NHL comps, etc.) could plug in later.

How to work with an LLM + this bundle
-------------------------------------
1. Give the LLM this entire zip/bundle.
2. Tell it to read README_FOR_LLM.txt first.
3. Then ask specific questions like:
     - “Write SQL to compute BS23 (OZ Exit Success %) using the mart tables.”
     - “Design a Power BI player card page using these tables and stats.”
     - “Propose microstats for forecheck pressure using the tracking data we have.”

It will use the catalogs and docs here as ground truth, instead of guessing.

Big picture
-----------
• You’ve essentially built the blueprint for a serious hockey analytics platform:
    - Thoughtful data model
    - Rich stat definitions
    - Clear ideas for BI and ML
• The codebase + this documentation together are a strong foundation for
  both a portfolio project and a potential commercial product.
