BenchSight Stats Catalog v4 – README
====================================

This bundle contains:
  * benchsight_stats_catalog_v4.csv  – machine-readable table of stats/microstats.
  * benchsight_stats_catalog_v4.md   – human-readable explanation + table.
  * benchsight_stats_catalog_v4_README.txt – this file.

How to use (for humans and LLMs)
--------------------------------
1. Open the CSV or Markdown and locate the stat of interest by StatID or Name.
2. Read the Description and FormulaConcept to understand what is measured.
3. Check PrimaryInputs to see which tables/columns are required in the BLB/BenchSight model.
4. Look at ComputableNow:
     - now_manual_tracking  → can be computed today with your tracked games.
     - now_boxscore_only    → can be computed with league boxscore-only data.
     - needs_xy             → requires consistent rink XY coordinates per event/shot.
     - needs_tracking       → requires per-frame tracking (NHL Edge / vision models).
     - needs_video_ml       → requires computer vision detection of events/actions.
5. If ComputableNow is not “now_*”, read ExtraDataNeeded for what must be added.
6. LLMNotes gives hints for how to explain or group stats in a report.

Extending the catalog
---------------------
- Add new rows for new stats as you expand the data model.
- Try to keep StatID stable once you publish it so Power BI / dashboards can rely on it.
- You can create filtered variants (e.g., EV-only, PP-only) by copying a row and changing
  FilterContext and Name (e.g., CF_5V5, CF_PP).

Suggested folder location
-------------------------
Place these files under something like:
    /docs/stats/benchsight_stats_catalog_v4.*
and reference them from your main project documentation.
