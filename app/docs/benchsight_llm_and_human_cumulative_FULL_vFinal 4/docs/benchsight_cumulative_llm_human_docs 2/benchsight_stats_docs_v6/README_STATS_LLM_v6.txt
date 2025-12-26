BENCHSIGHT STATS CATALOG - LLM README (v6)
=========================================

You are a code- and analytics-focused assistant helping the user evolve a hockey analytics platform called BenchSight.

This folder contains **the master stats catalog** and several historical variants. Always treat:

    benchsight_stats_catalog_master_ultimate.csv

as the **source of truth** for:
    - which stats exist,
    - how they are defined,
    - whether they are currently computable with the user's data,
    - what additional data would be required in the future.

FILE OVERVIEW
-------------

1) benchsight_stats_catalog_master_ultimate.csv
   * Canonical, merged catalog.
   * Columns (high level; see header row for full names):
       - stat_id: Stable identifier (e.g. "CF_ALL", "XG_SHOT").
       - name: Human-readable name ("Corsi For (all situations)").
       - short_name: Abbreviated label for scorecards / tables.
       - level: "game", "season", "player-game", "player-season", "line", "team-game", etc.
       - category: Buckets like "shot volume", "expected goals", "transition", "microstats", "goalie".
       - description: Plain-English explanation of the stat.
       - formula_or_logic: Conceptual definition (what counts in the numerator / denominator).
       - primary_data_sources: Which tables the stat pulls from (e.g. "fact_events_long", "fact_shifts_player", "dim_players").
       - filter_context: How the stat is usually sliced (e.g. "5v5 only, score-tied").
       - computable_with_current_tracking: "yes"/"no"/"partial" based on the user's current Beer League Beauties tracking.
       - computable_from_blb_tracking_only: Whether you can compute it with only the manually tracked games (no external league feed).
       - implementable_from_league_boxscore_only: Whether a simplified version is possible using league boxscore + rosters only.
       - implementation_status: Free-text implementation note ("MVP", "backlog", "needs xG model", etc.).
       - example_boxscore_display: Example label/format for showing this stat in a player or team card.
       - example_dax_measure_name: Suggested DAX measure name when implementing in Power BI.
       - example_sql_cte_name: Suggested CTE or view name for SQL pipelines.
       - extra_data_needed: Additional fields required to compute the full "ideal" version (e.g. full XY, tracking, puck speed).
       - how_to_read: Coaching / fan-friendly explanation of how to interpret the metric.
       - example_usage: Notes on practical use cases (scouting, coaching, lineup decisions).
       - llm_notes: Hints to you (the LLM) about edge-cases, simplifying assumptions, and fallback approximations.
       - notes: Misc implementation or conceptual notes.

2) benchsight_stats_catalog_extended.csv, benchsight_stats_catalog_v4.csv, ...
   * Older versions and source catalogs.
   * They have been fully merged into the master.
   * You only need to open them if you want historical context; do **not**
     treat them as authoritative for column names or content.

HOW TO USE THIS CATALOG
-----------------------

When the user asks for:
  * A new stat definition,
  * A DAX or SQL implementation,
  * A description of "what stats exist",
  * A plan for future data collection or ML features,

ALWAYS:
  1. Load benchsight_stats_catalog_master_ultimate.csv.
  2. Locate the relevant `stat_id` row(s).
  3. Use:
       - `formula_or_logic`
       - `primary_data_sources`
       - `filter_context`
       - `computable_with_current_tracking`
       - `implementation_status`
     to guide your answer and code.

If a stat's `computable_with_current_tracking` is "no" or "partial":
  - Respect that.
  - Use `extra_data_needed` and `llm_notes` to explain what is missing.
  - Offer approximations only if explicitly reasonable based on that text.

WHEN DESIGNING NEW STATS
------------------------

If the user wants to add a *brand new* metric that is not present:

  1. Propose a `stat_id` that fits the existing naming pattern.
  2. Propose values for each key column (description, formula_or_logic, etc.).
  3. Clearly distinguish between:
       - What can be computed with current Beer League Beauties tracking,
       - What would require extra data (e.g. full player tracking, puck speed).

INTERACTION WITH TABLE CATALOGS
-------------------------------

There are separate table catalogs (not in this folder) that describe:
  - fact_* tables in the datamart
  - dim_* tables
  - tracker/raw tables

When you see `primary_data_sources` like:
  - "fact_events_long"
  - "fact_events_wide"
  - "fact_shifts_player"
  - "dim_players"
  - "dim_games"

you should:
  - look up those tables in the table catalog,
  - use the column descriptions there to write correct SQL / DAX.

REMINDERS
---------

* The user has *both* manually tracked games and league-provided boxscores.
* Many advanced stats (xG, microstats, transition metrics) are only
  defined for manually tracked games.
* Boxscore-only games should still get simpler aggregates (G, A, SOG, TOI)
  and approximate advanced metrics where feasible; the catalog will tell you
  which ones.