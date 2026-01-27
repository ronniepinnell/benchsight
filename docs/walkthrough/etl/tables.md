# tables/ Deep Dive

**Building fact/dim/QA tables from raw and enriched data**

Last Updated: 2026-01-21  
Version: 2.00

---

## Purpose
`src/tables/` modules construct the actual tables (fact_events, fact_shifts, dimensions, derived facts, QA tables) that become CSVs and are uploaded to Supabase.

---

## What It Does
- Takes ingested/enriched DataFrames (events, shifts, players, teams).
- Applies calculations (from `calculations/`) to add derived fields.
- Builds fact/dim tables (players, teams, games, events, shifts).
- Builds QA tables (goal verification, FK checks, null checks).
- Produces DataFrames ready for output.

---

## Flow (Conceptual)
1) Inputs: normalized DataFrames (events, shifts, players, teams) from `base_etl`.
2) Apply metric helpers (Corsi, xG, QoC/QoT, etc.).
3) Build tables by grouping/aggregating to the desired grain (event, shift, player-game, player-season, team-season, etc.).
4) Build QA tables to validate counts and relationships.

---

## Why It Matters
- Defines the shape of your data model and what the dashboard consumes.
- Enforces the business logic layer between raw events and analytics views.

---

## Dependencies
- `calculations/*` for metrics
- Upstream DataFrames from `base_etl.py`
- Validation expectations in `validate.py` and tests

---

## Good / Risks / Next
- **Good:** Modular separation from the orchestrator; central place to shape tables.
- **Risks:** Re-aggregation from already aggregated inputs; bypassing calculation helpers; schema drift vs. dashboard/SQL views.
- **Next:** Keep table builders thin and focused; ensure every metric comes from `calculations/`; add tests for new table schemas.

---

## How to Read
1) Identify which builder creates which table(s).
2) Note the input columns and grouping keys.
3) Check for use of calculation helpers vs inline formulas.
4) See how outputs are named and returned to `base_etl`.

---

## Changing Safely
- Derive from raw facts (or well-defined intermediates), not from already aggregated tables.
- Add or update tests for schema and key metrics when tables change.
- Document any new tables/columns for downstream consumers (SQL views, dashboard).

---

## Deep Dives
- walkthrough/etl/tables/core_facts.md
- walkthrough/etl/tables/dimension_tables.md
- walkthrough/etl/tables/event_analytics.md
- walkthrough/etl/tables/remaining_facts.md
- walkthrough/etl/tables/shift_analytics.md
