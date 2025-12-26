Benchsight / Beer League Beauties
Master Documentation Bundle (Human-Friendly)
===========================================

What this is
------------
This folder is a *docs-only* bundle meant to sit alongside your main
Benchsight/BLB code repository. It does NOT contain the Python/SQL project,
but it DOES contain:

  - Stats catalogs (all basic + advanced + microstats)
  - Table catalogs / schema descriptions
  - Power BI notes, measures, and layout ideas
  - High-level architecture and roadmap notes
  - A matching "LLM master" guide so you can plug the same bundle into ChatGPT,
    Claude, Gemini, etc. and get consistent help.

How to use this as a human
--------------------------
1. Start with:
     benchsight_llm_and_human_docs_full_v2.zip
   Inside, look for a top-level README or overview doc.
   That gives you the big-picture story:
     - Where raw tracking & BLB_Tables data come from
     - How staging / intermediate / mart layers work
     - How the tracker app fits in
     - How Power BI and future Dash/Render dashboards sit on top

2. Next, open:
     benchsight_stats_docs_v6.zip
   This is the "stats bible":
     - One master CSV with one row per stat.
     - Columns include: name, category, description, inputs, formula notes,
       filter context, tags (e.g., xG_feature, microstat, boxscore_core).
     - Use this whenever you wonder:
         "Do we already have this metric defined?
          What is the official formula?
          Which tables/columns does it use?"

3. Use the table/catalog bundles:
     blb_table_catalog_docs.zip
     blb_datamart_docs_bundle.zip
   These describe:
     - What each table in the datamart contains.
     - Which columns are keys vs measures vs flags.
     - How tables relate (star/snowflake diagrams).
   This is what you reference when building new SQL or Power BI models.

4. For reporting / dashboard ideas:
     blb_extra_docs_powerbi_quality.zip
   Inside you'll find:
     - Suggested Power BI star schema diagrams.
     - Example DAX for:
         * Player boxscore pages
         * Game summaries (ESPN/NHL style)
         * Line-combo and matchup views
         * Microstats / tracking overlays
     - Layout sketches and notes on visual design.

5. For "today-only" or session-specific notes:
     benchsight_today_docs_bundle.zip
   Use this when you want to remember what we decided in specific sessions
   (e.g., how to prioritize features, or how to prepare the project for your resume).

How this ties back to the code repo
-----------------------------------
In your main repo, you should have something like:

  /src          → Python + SQL orchestration, ETL, tracker app
  /sql          → Mart/intermediate DDL + transforms
  /data         → Raw BLB_Tables + tracking game folders
  /output       → Datamart CSV exports for Power BI
  /docs         → This bundle (or a copy of it)

When you (or an LLM) are working on the code, you can always jump back here to:

  - Check if a column already exists for a concept.
  - Verify the stat formula and intended grain.
  - Confirm which table is supposed to be the "official" source
    for something (e.g., game-level vs event-level Corsi).

If you're onboarding a coach, analyst, or developer, you can give them this bundle
and say:
  "Read the top-level README, then the stats catalog README, then the table docs.
   After that, open the main project repo and you'll know what everything is."

And if you're talking to an LLM, you can upload this bundle and say:
  "Everything you need to know about the data model and stats is in here.
   Ask me questions if anything is ambiguous, but please stay consistent with
   these definitions."

