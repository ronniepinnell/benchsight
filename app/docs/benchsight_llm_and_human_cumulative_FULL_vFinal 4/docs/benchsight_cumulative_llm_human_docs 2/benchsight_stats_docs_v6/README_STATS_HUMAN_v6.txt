BenchSight Stats Catalog (v6) – Human Overview
==============================================

This folder contains the **master list of all stats and microstats** that the BenchSight
project cares about, along with how they are defined, what data they need, and how they
should be implemented in SQL / Power BI / Python.

Key file:
    * benchsight_stats_catalog_master_ultimate.csv

Use that as the single source of truth. Every row is one stat (e.g. "Corsi For", "Controlled Zone Entries", "xG per 60").

Columns you will care about most:
    * stat_id:
        - Stable identifier across code, SQL, DAX, and docs.
        - Example: CF_ALL, CF_5V5, XG_SHOT, OZ_ENTRY_CONTROLLED.
    * name:
        - Human-readable label ("Corsi For (all situations)").
    * short_name:
        - Abbreviated label for scorecards ("CF", "xG/60").
    * level:
        - What grain this stat is calculated at:
          "player-game", "player-season", "team-game", "line", "goalie-game", etc.
    * category:
        - Grouping bucket for dashboards:
          "shot volume", "chance quality", "transition", "microstats", "goalie", "PK", etc.
    * description:
        - Plain-English explanation you can show to coaches or in documentation.
    * formula_or_logic:
        - How the stat is calculated conceptually (what "counts" in numerator/denominator).
    * primary_data_sources:
        - Which datamart tables the stat comes from (fact_events_long, fact_shifts_player, dim_players, etc.).
    * filter_context:
        - Typical slice for this stat (5v5 only, score tied, all situations, PP, PK, etc.).
    * computable_with_current_tracking:
        - Whether the full "ideal" version is computable with the current manually tracked data.
    * computable_from_blb_tracking_only:
        - Whether you can compute it using **only** your Beer League Beauties manual tracking (no external league feed).
    * implementable_from_league_boxscore_only:
        - Whether a rough approximation is possible using a standard league boxscore + rosters.
    * implementation_status:
        - Rough status ("MVP", "backlog", "needs xG model", etc.).
    * extra_data_needed:
        - If the stat is not fully computable yet, this tells you what you'd need (full tracking, puck speed, etc.).
    * how_to_read:
        - Short "how to interpret this" text for non-technical readers.
    * example_boxscore_display, example_dax_measure_name, example_sql_cte_name:
        - Concrete suggestions for how to name and display this stat in dashboards and code.
    * llm_notes, notes:
        - Internal notes for yourself and LLMs about tricky parts, edge cases, or shortcuts.

If you are:
    * Building Power BI:
        - filter the catalog by `level` and `category` to design pages (player card, team game summary, line combos, etc.).
        - use `example_dax_measure_name` and `formula_or_logic` as starting points.
    * Extending SQL / Python:
        - start from `primary_data_sources` and `formula_or_logic`.
        - consider `computable_with_current_tracking` before promising a stat.
    * Planning future tracking / data collection:
        - sort/filter by `extra_data_needed` and `implementation_status`.

The LLM-oriented README (README_STATS_LLM_v6.txt) explains how to use this catalog
from an AI assistant's point of view. If you are collaborating with an LLM,
share this folder and that file so it can quickly understand the landscape
of metrics in the BenchSight project.