# BenchSight / BLB Project – Human-Facing Overview

This document is for **you** (a human analyst / developer / coach) who wants
to understand what this project is, how it’s structured, and how to use
the documentation bundle in this zip.

The short version:

- You have a **hockey tracking + analytics project**.
- You track games by hand (events + shifts), add XY coordinates and video.
- A pipeline turns that into rich stats + datamart tables.
- Power BI and Python dashboards sit on top of that data.
- This zip contains documentation that helps both **humans** and **LLMs**
  understand and extend the project.

---

## 1. What’s in This Zip?

Top-level:

- `README_LLM.md` – instructions for AI assistants.
- `README_HUMAN.md` – this file.
- `docs_llm/` – same concepts as `docs_human/`, but written as a reference
  for large language models.
- `docs_human/` – explanations and diagrams for people.

You already have the **full project repo** elsewhere (code + SQL + data).
This zip focuses on explanations, schemas, and stat definitions.

---

## 2. How the Project is Organized (Mentally)

At a high level, think of four layers:

1. **Raw**
   - Excel workbooks (BLB_Tables, 18969_tracking, etc.).
   - Game folders with tracking sheets, XY CSVs, shots CSVs, video times.
2. **Staging (Postgres)**
   - Tables that directly mirror the raw files (cleaned + normalized).
   - Still pretty close to the original layout.
3. **Intermediate / Model Layer**
   - Event long/wide tables.
   - Shift long/wide with logical shifts and TOI.
   - Chain / sequence / play tables.
   - Rating-context expansions.
4. **Datamart**
   - Fact and dimension tables designed for:
     - Power BI (star/snowflake schema).
     - Python dashboards (Dash/Streamlit).
     - ML models (xG, microstats, player comp).

The tracker UI is another important piece:

- It aims to **replace or complement** the manual Excel tracker.
- It should eventually support:
  - Event logging with dependent dropdowns (type, detail_1, detail_2).
  - Shift logging.
  - XY click capture for rink and net.
  - Video-aligned timestamps (so you can click and watch a play).

---

## 3. What’s in `docs_human/`?

- `human_repo_guide.md`
  - Walks through the repo structure and explains what each part does.
- `human_stats_catalog_summary.md`
  - Narrative summary of the stats catalog (what they mean, where they come from).
- `human_powerbi_guide.md`
  - Ideas for report pages, DAX measures, and how to connect to the datamart.
- `human_flows_and_schemas.md`
  - Diagrams (in text and Mermaid syntax) showing:
    - ETL flow from raw → stage → intermediate → mart → BI/ML.
    - Datamart star/snowflake schema.
    - Event / shift / chain relationships.
- `human_ml_ideas.md`
  - Suggestions for future ML models and how they’d use the data.

These are meant to be **skimmed and referenced** – not read all at once.

---

## 4. How to Use This with an LLM

When you work with an AI assistant:

1. Upload your **code/data repo** as usual (or reference it from GitHub).
2. Upload this **documentation zip** as well.
3. Tell the LLM something like:

   > “Please start by reading `README_LLM.md` inside the docs zip, then use
   > `stats_catalog.csv` and `table_catalog.csv` when you propose changes.”

4. Ask focused questions, for example:
   - “Help me write SQL to compute xG per shift using fact_events and xy tables.”
   - “Design DAX for a line-combo impact visual using these tables.”
   - “Refactor the tracker UI so entering a shot + XY is as few clicks as possible.”

Because the LLM has this **consistent view** of stats, tables, and flow,
its answers should be much more aligned with your long-term design.

---

## 5. Where to Go Next

Here’s a good order to explore:

1. `docs_human/human_repo_guide.md` – big-picture tour.
2. `docs_human/human_flows_and_schemas.md` – see the pipeline & schema shapes.
3. `docs_llm/stats_catalog.csv` – scroll and get a sense of all the stats.
4. `docs_llm/table_catalog.csv` – see the tables and their grains.
5. `docs_human/human_powerbi_guide.md` – think about what you want to build first.

Then you can go back to your repo and connect the dots to actual code & data.

---

## Inspiration Sources

A curated list of inspiration sites (analytics blogs, NHL Edge, microstat projects,
and visualization galleries) lives in the project under:

- `docs_llm/benchsight_inspiration_links.csv`

Open that CSV in Excel/Power BI to see, for each site:
- The URL
- What we like about it
- How BenchSight aims to use or extend those ideas
