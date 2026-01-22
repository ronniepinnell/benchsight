# data_loader.py Deep Dive

**How BLB and tracking files are ingested**

Last Updated: 2026-01-21  
Version: 2.00

---

## Purpose
`src/core/data_loader.py` centralizes reading and normalizing raw inputs (BLB Excel sheets and tracking Excel files). Everything downstream assumes these DataFrames are correct and keyed properly.

---

## What It Does
- Reads BLB Excel (`BLB_Tables.xlsx`) and tracking Excel files (events/shifts).
- Normalizes column names and data types.
- Enforces presence of required columns.
- Ensures uniqueness for key IDs (players, teams, games, events, shifts).
- Returns DataFrames to the orchestrator (`base_etl.py`).

---

## Flow
```mermaid
flowchart TD
    DL_START[run_etl/main] --> PATHS[Resolve paths]
    PATHS --> BLB[Load BLB_Tables.xlsx]
    PATHS --> TRK[Load tracking *.xlsx (events/shifts)]
    BLB --> NORM[Normalize columns/types]
    TRK --> NORM
    NORM --> VALIDATE[Required columns + unique keys]
    VALIDATE --> RETURN[Return DataFrames to base_etl]
```

1) Resolve BLB + tracking paths.
2) Load Excel sheets into DataFrames.
3) Normalize column names (lowercase, underscores) and types.
4) Validate required columns, non-null keys, uniqueness.
5) Return DataFrames to `base_etl.py`.

---

## Why It Matters
- If column names/types are off here, every downstream table/calculation breaks.
- Single ingestion point prevents duplicated IO logic and schema drift.

---

## Dependencies
- pandas (Excel reading, DataFrame manipulation)
- Filesystem paths/config (passed from CLI/run_etl)
- Tracker export schema and BLB sheet schema

---

## Good / Risks / Next
- **Good:** Central ingestion; explicit schema touchpoint.
- **Risks:** Input schema drift (tracker export or BLB changes); performance on large Excel; silent column mismatches if validation is weak.
- **Next:** Strengthen required-column checks; add small fixtures/tests for loader; log/count anomalies; cache or parallelize if Excel becomes large.

---

## How to Read
1) Look at required column lists for BLB and tracking.
2) See how paths are resolved and how sheets are named.
3) Check normalization (rename/drop) and uniqueness enforcement.
4) Note what gets returned (which DataFrames) to `base_etl.py`.

---

## Changing Safely
- Keep tracker/BLB schema in sync with any column changes.
- Add tests for new required columns or transformations.
- Fail fast on missing/duplicate key columns.*** End Patch Silently***
