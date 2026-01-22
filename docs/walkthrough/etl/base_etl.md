# base_etl.py Deep Dive

**Phase-by-phase guide to the ETL orchestrator**

Last Updated: 2026-01-21  
Version: 2.00

---

## Purpose
`src/core/base_etl.py` is the main ETL orchestrator. It sequences loading, transformations, calculations, QA, and output/upload. Almost every table and metric flows through here.

---

## Call Flow (Detailed)

```mermaid
flowchart TD
    CLI[run_etl.py] --> MAIN
    MAIN --> DISCOVER[discover_games]
    MAIN --> LOADBLB[load_blb_tables (data_loader.py)]
    MAIN --> PLAYERLOOKUP[build_player_lookup (data_loader.py)]
    MAIN --> LOADTRK[load_tracking_data (data_loader.py)]
    MAIN --> REFS[create_reference_tables]
    MAIN --> DERIVED1[create_derived_tables]
    MAIN --> ENH_EVT[enhance_event_tables]
    MAIN --> ENH_DER_EVT[enhance_derived_event_tables]
    MAIN --> FLAGS[enhance_events_with_flags]
    MAIN --> SEQ[create_fact_sequences]
    MAIN --> PLAYS[create_fact_plays]
    MAIN --> DERIVED2[create_derived_event_tables]
    MAIN --> SHIFT_ENH[enhance_shift_tables (shift_enhancer.py)]
    MAIN --> SHIFT_PLAYERS[enhance_shift_players (shift_enhancer.py)]
    MAIN --> ROSTER_UPD[update_roster_positions_from_shifts (shift_enhancer.py)]
    MAIN --> VALIDATE[validate_all]
    VALIDATE --> QA[QA tables + CSV reads]

    %% Optional paths
    MAIN -.-> SAFECSV[safe_csv (if available)]
    MAIN -.-> TABLESTORE[table_store (if available)]
    MAIN -.-> STDPLAY[standardize_play_details (imported)]
```

- **Optional modules:** `safe_csv` and `table_store` are used only if import succeeds. `standardize_play_details` is imported but not always invoked in main flow.

---

## How to Navigate the File
- **Scan the phase functions first.** They usually follow the order: load → preprocess → build facts/dims → calculations → aggregates → QA → output/upload.
- **Identify the shared context/state.** Look for DataFrames passed between phases (events, shifts, players, teams).
- **Find the goal filter.** Ensure all goal-related derivations rely on the canonical filter (event_type == 'Goal' AND event_detail == 'Goal_Scored').
- **Trace CSV/output writers.** See how tables get written to `data/output/` and how upload is triggered.

---

## Phase Outline (Typical)
1) **Load Inputs**
   - Calls `data_loader.py` to ingest BLB Excel sheets + tracking Excel (events/shifts).
   - Normalizes columns and enforces uniqueness on keys.
2) **Build Core Dims/Facts**
   - Player/team/season/schedule dims
   - `fact_events`, `fact_shifts`, expansion tables (`fact_event_players`, `fact_shift_players`)
3) **Apply Calculations**
   - Corsi/Fenwick, xG, QoC/QoT, WAR/GAR, scoring chances, danger levels
   - Uses helpers in `src/calculations/*`
4) **Derived Tables / Aggregations**
   - Player, goalie, team season/game stats
   - Leaderboards, standings, situational splits
5) **QA Tables**
   - Goal verification, FK/relationship checks, null checks
6) **Output**
   - Write CSVs to `data/output/`
   - Optional upload to Supabase (triggered later)
7) **Validation**
   - Often calls `validate.py` or internal checks to assert counts and schema

---

## What Each Section Does (Conceptual)
- **Loader calls:** Establish the raw DataFrames; if counts or schemas are off, everything downstream breaks.
- **Core facts/dims:** Build canonical tables that everything else derives from (events/shifts/players/teams).
- **Calculations:** Add derived columns; must stay in sync with `src/calculations/*` to avoid logic drift.
- **Aggregations:** Roll up by player/team/game/season; avoid re-aggregating already aggregated tables.
- **QA:** Create QA tables to catch double counting and missing data (goal verification, FK checks).
- **Output/upload:** Final persistence; ensure no partial writes on failure.

---

## Dependencies
- **Ingestion:** `src/core/data_loader.py`
- **Metrics:** `src/calculations/*`
- **Tables:** `src/tables/*`
- **Validation:** `validate.py`, QA tables, pytest suite (`tests/`)
- **Config/flags:** CLI arguments from `run_etl.py` (games, wipe, upload)

---

## Key Invariants to Protect
- Goal counting: `event_type == 'Goal' AND event_detail == 'Goal_Scored'`
- Unique keys: `event_id`, `shift_id`, `player_id`, `game_id`
- Aggregations are derived from raw facts (not from already aggregated tables)
- One tracking file per game; no duplicate events/shifts

---

## Good / Risks / Next
- **Good:** Comprehensive pipeline; strong metrics coverage; QA/validation hooks exist.
- **Risks:** File is large/monolithic; pandas performance bottlenecks (row-wise ops); high coupling makes refactors risky; schema drift from tracker/BLB inputs.
- **Next:** Modularize into smaller orchestrators (load, build, calculate, qa); vectorize hot paths; add profiling; keep validation up to date with new metrics.

---

## How to Read It (Suggested Order)
1) Skim the top-level `main()`/entry function to see arguments and phase order.
2) Identify each phase function and note inputs/outputs (DataFrame names).
3) Track where calculations are applied (ensure they come from `src/calculations/*`).
4) Find QA/table write steps and how failures are handled.
5) Cross-check with `validate.py` and key tests to understand enforced contracts.

---

## Making Changes Safely
- Isolate new logic in helper modules (don’t grow `base_etl.py` more).
- Reuse calculation helpers; don’t duplicate filters (especially for goals).
- Add/adjust validations and tests when changing schemas or metrics.
- Benchmark/optimize after functional changes (vectorize, avoid `.iterrows()`).
