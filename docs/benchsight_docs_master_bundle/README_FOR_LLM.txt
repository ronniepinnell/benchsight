BenchSight / BLB Project – LLM Master README
===========================================

PURPOSE
-------
This repository snapshot contains documentation, stats catalogs, table catalogs,
schemas, Power BI notes, and project descriptions for the Beer League Beauties /
BenchSight hockey analytics project. You (the LLM) should read this file first,
then follow the pointers below to find detailed resources.

1. STATS CATALOG (MASTER)
-------------------------
File: stats/benchsight_stats_catalog_master_ultimate.csv

• This is the single, authoritative catalog of all stats and microstats discussed so far.
• Columns include:
    - stat_id (BSxx style ids)
    - name, short_name
    - level (event / shift / game / season / player / team / line / goalie)
    - category (e.g., "Shot Quality", "Transition", "Microstat")
    - description (plain-English definition)
    - formula_or_logic (implementation-friendly description)
    - formula_concept (earlier conceptual wording)
    - inputs_core / inputs_optional (what data is required / nice-to-have)
    - filter_context_notes (how to group/aggregate, common filters)
    - primary_data_sources (which tables feed the stat)
    - requires_detailed_tracking (Y/N – whether manual tracking is needed)
    - feasible_from_league_boxscore_only (Y/N)
    - implementation_status ("now" / "needs_xy" / "needs_vision" / etc.)
    - extra_data_needed, example_usage, notes, llm_notes

• When asked to compute or explain any stat, first look it up by stat_id or name
  in this CSV. Use description + formula_or_logic + inputs_core to design SQL,
  Python, or DAX implementations, always cross-checking with table catalogs.

2. TABLE / DATAMART CATALOGS
----------------------------
Look under folders extracted from:
  - blb_table_catalog_docs
  - blb_datamart_docs_bundle

Typical files (names may vary slightly):
  - table_catalog.csv / table_catalog.xlsx
  - datamart_tables.xlsx

These describe:
  • All core fact / dimension tables in the BLB / BenchSight mart
  • Column names, meanings, keys, and relationships
  • Which stage each table lives in (stage / intermediate / mart)
  • Which stats or features each table supports

When designing queries or models, use:
  • Stats catalog → "what to compute"
  • Table catalog → "where the data lives and how to join it"

3. POWER BI / REPORTING DOCS
----------------------------
Look under folders extracted from:
  - blb_extra_docs_powerbi_quality.zip
  - benchsight_today_docs_bundle.zip
  - benchsight_llm_and_human_docs_full.zip

You will find:
  • Suggested Power BI star schema layouts
  • Example report/page designs:
      - Game summary (ESPN/NHL-style)
      - Player cards (NHL Edge-style)
      - Line combo & matchup views
      - Microstat dashboards
  • Example DAX measures:
      - Game-level aggregates
      - On-ice vs off-ice splits
      - With/without-you (“WOWY”) patterns
      - Rolling season metrics

Use these to:
  • Propose additional DAX measures consistent with existing patterns.
  • Maintain relationship diagrams when adding new tables.
  • Explain how a new stat would appear in visualizations.

4. LLM-SPECIFIC GUIDANCE
------------------------
When answering questions or generating code about this project, you should:

  1) Start from the stats catalog:
     • Identify the stat(s) involved.
     • Copy constraints (level, filters, inputs_core) into your reasoning.

  2) Cross-check with table/catalog docs:
     • Confirm which fact/dim tables hold needed columns.
     • Confirm primary/foreign keys and grain (event vs shift vs game).

  3) Respect tracking vs non-tracking data:
     • If requires_detailed_tracking == "Y" and the user says tracking is missing,
       you must say the stat cannot be computed fully and describe approximations.

  4) Align language with documentation:
     • When naming new stats or measures, try to follow the BSxx id pattern and
       naming conventions already in the catalog.

  5) Keep output implementation ready:
     • For SQL: specify schema.table names and key joins when possible.
     • For Python: assume pandas DataFrames matching the mart table schemas.
     • For DAX: always mention the filter context / intended visual usage.

5. HUMAN-FACING DOCS
--------------------
A separate file, README_FOR_HUMANS.txt, gives a narrative overview for human readers:
  • Project vision and goals (BenchSight as a commercial and portfolio project)
  • High-level architecture (stage → intermediate → mart → BI / ML)
  • How game tracking and BLB tables flow into the datamart
  • What exists now vs. short/mid/long-term roadmap

You can safely quote or summarize that content when explaining the project to users.

6. INSPIRATION LINKS
--------------------
Within this bundle you will also find:
  • A CSV listing external inspiration URLs (Evolving-Hockey, JFresh, NHL Edge, etc.)
  • Notes on what we are trying to emulate from each site (visuals, stats, UX).

Use these when:
  • Designing new visuals or storytelling formats.
  • Proposing microstats similar to public analytics work.
  • Explaining how BenchSight/BLB could evolve commercially.

7. HOW TO USE THIS BUNDLE
-------------------------
• For any question about:
    - “What does stat X mean?” → stats/benchsight_stats_catalog_master_ultimate.csv
    - “Which table has column Y?” → table/datamart catalogs
    - “How should reports look?” → Power BI / dashboard docs and screenshots
    - “What is the roadmap?” → roadmap / backlog sections in human docs

• Always keep answers consistent with this documentation, and if assumptions
  are needed (e.g., future computer vision tracking), clearly label them as such.

Consult all folders and the benchsight_master_doc as well as the hockey analytics pdf.
