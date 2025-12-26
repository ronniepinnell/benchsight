# BenchSight – LLM README (How to Use This Bundle)

You are an LLM assisting with the **BenchSight / Beer League Beauties** project: a modular
hockey analytics system built from manual tracking + public NHL data.

This ZIP contains:
- **stats/**: `benchsight_stats_catalog_master.csv` → canonical advanced & microstat catalog
- **tables/**: `benchsight_table_catalog_master.csv` → key fact/dim tables & their purpose
- **etl/**: `etl_flow.png` → visual ETL overview from tracker to data mart to apps
- **roadmap/**: `roadmap_and_checklist.md` → short-, mid-, long-term plan & checklists
- **inspirations/**: `benchsight_inspiration_links.csv` → external sites and how they influence design
- **LLM/** & **humans/**: space for more narrative docs and guides in the full project

## Your Goals as an LLM

When the user provides this bundle, you should be able to:

1. **Answer architecture questions**
   - Explain how raw tracker data flows through stage → mart → dashboards.
   - Suggest schema changes and new tables consistent with the table catalog.

2. **Help design new stats and features**
   - Use `stats/benchsight_stats_catalog_master.csv` to understand current metrics.
   - Propose new microstats compatible with existing grains (event, shift, chain, boxscore).

3. **Assist with Power BI, Dash, and ML**
   - Use table grain descriptions to recommend DAX, visual designs, or model feature sets.
   - Ensure all new ideas respect existing keys (player_id, game_id, event_id, chain_id, etc.).

4. **Stay aligned with inspiration sources**
   - `inspirations/` describes sites like Evolving-Hockey, MoneyPuck, All Three Zones, etc.
   - Your suggestions should "feel" similar in depth and rigor while staying feasible for this project.

## How to Navigate

- Start with `etl/etl_flow.png` to understand the big picture.
- Then read `roadmap/roadmap_and_checklist.md` to know what exists vs planned.
- Use `tables/benchsight_table_catalog_master.csv` to anchor any schema-related reasoning.
- Use `stats/benchsight_stats_catalog_master.csv` for stat definitions and formula hints.
- Use `inspirations/benchsight_inspiration_links.csv` when the user asks for new ideas or references.

## Important Constraints

- Tracking logic and column semantics should follow the original Excel trackers and the UI tracker spec.
- Events happen on a **countdown clock**, not count-up.
- Linked, sequence, and play chains must respect the project's definitions.
- Ratings from `dim_player` are important for rating-aware stats; preserve them where possible.

When in doubt, explain your assumptions clearly so the user can validate them.
