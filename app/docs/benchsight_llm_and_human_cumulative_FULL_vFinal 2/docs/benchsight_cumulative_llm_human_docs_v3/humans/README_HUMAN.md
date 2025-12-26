# BenchSight / Beer League Beauties – Human README (Docs Bundle)

This folder is a **documentation-only snapshot** meant for:
- You (Ronnie) as the project owner.
- Other developers, analysts, or coaches.
- LLMs that will help you extend the project.

It does **not** contain all the source code or data, but it describes how everything fits together.

## What’s Inside

- `etl/etl_flow.png`
  - A simple visual showing the main layers:
    Raw Tracker → Stage → Mart → Features → Apps (Power BI & Dash).

- `roadmap/roadmap_and_checklist.md`
  - Short-, medium-, and long-term implementation steps.
  - Helps you prioritize: teammates seeing value quickly, resume, then commercial viability.

- `stats/benchsight_stats_catalog_master.csv`
  - A merged catalog of advanced stats and microstats we’ve discussed.
  - Use this as your single source of truth when defining measures in Power BI or Python.

- `tables/benchsight_table_catalog_master.csv`
  - A high-level data dictionary of the most important mart tables.
  - Tells you: grain, layer, and purpose so you know which table to use for which visual.

- `inspirations/benchsight_inspiration_links.csv`
  - Key sites (Evolving-Hockey, MoneyPuck, Natural Stat Trick, All Three Zones, NHL Edge).
  - Each row explains what we’re borrowing conceptually (xG style, microstats, tracking, etc.).

## How This Relates to the Full Project

- The **full project repo** includes:
  - `src/` with Python ETL and tracker code.
  - `sql/` with stage → mart DDL/DML.
  - `data/` with example outputs (mart tables as CSV for Power BI).
  - `docs/` which this bundle is designed to live inside.

- This documentation bundle is designed so that:
  - A human can glance at the roadmap and ETL flow and remember how things hang together.
  - An LLM can read the LLM README and the CSV catalogs to generate consistent code/queries.

## How to Use This Bundle

1. **As a developer or analyst**
   - Start with `roadmap/roadmap_and_checklist.md` to decide what to tackle next.
   - Use the table catalog to wire up new Power BI visuals or write SQL against the mart.
   - Use the stats catalog to ensure your metric implementations match the agreed definitions.

2. **When onboarding another LLM**
   - Upload this ZIP.
   - Tell it to start with `LLM/README_LLM.md`.
   - Mention that code and data live in your separate BLB/BenchSight repo.

3. **When explaining the project to a coach / non-technical teammate**
   - Use the ETL diagram + a few example visuals (from Power BI or Dash).
   - Describe the system as:
     > “A tool that turns manually tracked and league-provided data into NHL-style advanced stats, player cards, and line matchup insights.”

As we extend the project, you can keep regenerating this bundle so it stays in sync with the code and database.
