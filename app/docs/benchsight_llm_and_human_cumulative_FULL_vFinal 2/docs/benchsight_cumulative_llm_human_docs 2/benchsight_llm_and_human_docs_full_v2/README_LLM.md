# BenchSight / BLB Project – LLM Master Guide

You (the LLM) are being given a repository + this documentation bundle. Your job,
when a user asks for help, is to:

1. **Understand the project context** – a hockey analytics + tracking system
   combining manual tracking, XY coordinates, video alignment, and rich stats.
2. **Respect the existing architecture** – staging → intermediate → mart,
   with modular Python + SQL code, Power BI, and future ML/computer-vision work.
3. **Use this document as your *table of contents* for the rest of the bundle.**

The user may work with other LLMs as well, so your answers should be clear,
well-documented, and consistent with the design described here.

---

## 1. Repository Overview (High-Level Mental Model)

The full project (outside this zip) is structured roughly as:

- `src/`
  - `stage/` – Python + SQL to load BLB_Tables (dims/facts) and game
    tracking Excel into **Postgres staging**.
  - `intermediate/` – transformations from staging to intermediate
    “model-ready” tables (events_long, shifts_long, chains, etc.).
  - `mart/` – transformations to **datamart** star/snowflake tables
    used by Power BI and dashboards.
  - `tracker/` – web UI / app logic for live game tracking
    (events, shifts, XY clicks, video alignment).
  - `ml/` – notebooks and helpers for xG and microstat-based ML models.
- `sql/`
  - DDL + DML scripts for each layer (stage / intermediate / mart).
- `data/`
  - `raw/` – BLB_Tables.xlsx + per-game tracking folders (18969, etc.).
  - `stage/` – optional exports from Postgres staging (for debugging).
  - `output/` – **final datamart CSVs** for Power BI + external tools.
- `docs/`
  - Project overview, architecture diagrams, schema diagrams,
    Power BI notes, ML ideas, stats catalog, etc.

This zip adds **two documentation tracks**:

- `docs_llm/` – written for *you* (the LLM).
- `docs_human/` – written for humans (coaches, analysts, devs).

You should always start with `docs_llm/llm_repo_guide.md` and
`docs_llm/stats_catalog.csv` + `docs_llm/table_catalog.csv` when answering
questions.

---

## 2. Files in This Bundle (for the LLM)

### 2.1. Top-Level

- `README_LLM.md` (this file)
- `README_HUMAN.md` (high-level explanation for humans)
- `docs_llm/` – LLM-focused docs
- `docs_human/` – human-focused docs

### 2.2. `docs_llm/` Contents

- `llm_repo_guide.md`
  - Detailed description of repo layout, naming conventions, pipeline steps,
    how staging / intermediate / mart fit together, and where to plug in new code.
- `stats_catalog.csv`
  - **Master catalog of stats & microstats**.
  - Columns:
    - `stat_id` – stable ID, e.g. `XG_SHOT`, `MICRO_PASS_COMPLETION`.
    - `name` – human-friendly label.
    - `level` – player / team / line / goalie / game / sequence / play.
    - `category` – boxscore / xG / microstat / chain / rating / video / composite.
    - `definition`, `formula_pseudocode`.
    - `required_tables`, `required_columns`.
    - `implemented` (yes/no/planned).
    - `notes`.
- `table_catalog.csv`
  - Catalog of **all key tables** used in the datamart / project.
  - Columns include `table_name`, `layer`, `grain`, `primary_key`,
    `foreign_keys`, `source`, `description`, `important_notes`.
- `powerbi_measures_example.dax`
  - Example DAX measures for Power BI pages (boxscore, game summary,
    microstats, xG, on-ice metrics).
- `flows_and_schemas.md`
  - Mermaid-style diagrams + textual descriptions for:
    - End-to-end pipeline (raw → stage → intermediate → mart → BI/ML).
    - Star/snowflake schema for datamart.
    - Event/shift/chain relationships.
- `ml_ideas.md`
  - Concrete ML ideas, features, labels, and how to use tables + stats
    to build models (xG, player comp, line matchup models, etc.).

### 2.3. `docs_human/` Contents

These mirror the LLM docs but are written in a more conversational,
non-technical style. If a user asks for “plain English” explanations,
you can summarize from these sources.

---

## 3. How You Should Work with This Project

When the user asks for help, follow this pattern:

1. **Identify the scope.** Is the question about:
   - ETL, staging, intermediate, or mart code?
   - Stats/microstats or formulas?
   - Power BI / dashboards / DAX?
   - Tracker UI, XY data, or video alignment?
   - ML / computer vision / BenchSight commercial ideas?
2. **Consult the relevant docs in `docs_llm/`.**
   - For schema questions → `table_catalog.csv` + `flows_and_schemas.md`.
   - For stats → `stats_catalog.csv`.
   - For BI / measures → `powerbi_measures_example.dax`.
   - For ML ideas → `ml_ideas.md`.
3. **Respect naming conventions.**
   - Use stat IDs and table names as defined in the catalogs.
   - Do NOT invent conflicting names; if you propose something new,
     mark it as “proposed” and align with existing patterns.
4. **When generating code:**
   - Assume existing Python/SQL folders already contain core ETL.
   - Add **new** modules or SQL files in a way that “plugs into” the
     orchestrator (single main .py runner) rather than rewriting everything.
   - Add comments that explain *why* as much as *what*.
5. **When generating Power BI content:**
   - Use the fact/dim structure described in `flows_and_schemas.md`,
     and measure patterns in `powerbi_measures_example.dax`.
   - Clearly state filter context and grain assumptions.
6. **When refining the tracker / UI:**
   - Preserve the Excel tracking logic (dependent dropdowns, event / shift
     rules, linked events, countdown clock, etc.).
   - Ensure final stored tables still look like the expected `events_long` /
     `shifts_long` etc, so they feed the same mart pipeline.

---

## 4. What to Do If Something Is Missing

If the user asks for something that is not fully covered by these docs:

1. Use the patterns here to **propose a consistent design**.
2. Clearly label it as:
   - `Extension of existing design` or
   - `New proposed feature`.
3. Suggest where in the repo it should live (`src/mart/...`, `sql/mart/...`,
   `docs/...`, etc.) and how it affects stats/tables.

The user cares a lot about:
- Learning from the project (clear comments, explanations).
- Reusability (modular code, clean schemas).
- Being able to explain the system to recruiters, coaches, and future users.
- Eventually commercializing this as “BenchSight”.

Your answers should help them move toward those goals.

---

## Inspiration Sources

A curated list of inspiration sites (analytics blogs, NHL Edge, microstat projects,
and visualization galleries) is stored in:

- `docs_llm/benchsight_inspiration_links.csv`

Use this file to understand the aesthetic and analytical benchmarks BenchSight is
aiming for. Each row explains what we like about a site and how BenchSight plans
to emulate or extend those ideas.
