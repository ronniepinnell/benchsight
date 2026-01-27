# calculations/ Deep Dive

**Where metric formulas live (single source of truth)**

Last Updated: 2026-01-21  
Version: 2.00

---

## Purpose
`src/calculations/` contains functions for metrics (goals, Corsi/Fenwick, xG, WAR/GAR, QoC/QoT, etc.). All downstream tables should use these helpers to avoid logic drift.

---

## What It Does
- Defines reusable filters and derived columns.
- Encapsulates stat logic so tables/components don’t re-implement formulas.
- Provides a stable interface for new metrics.

---

## Key Files to Read
- `goals.py` — canonical goal filter (use everywhere).
- `corsi.py` — shot attempts logic.
- `xg.py` (or equivalent) — expected goals calculation.
- Other metric modules (WAR/GAR, QoC/QoT, danger levels) as present.

---

## Flow (Conceptual)
1) Receive base facts (events/shifts).
2) Apply filters and compute derived columns (per-event or per-player/team).
3) Return enriched DataFrames or helper functions used by table builders.

---

## Why It Matters
- Prevents inconsistent metrics across tables/UI.
- Central place to optimize/benchmark metric performance.

---

## Dependencies
- pandas/NumPy for vectorized math
- Upstream schemas from `data_loader` and `base_etl`

---

## Good / Risks / Next
- **Good:** Centralized formulas reduce drift; easier to audit metrics.
- **Risks:** Performance if row-wise operations are used; duplication if builders bypass helpers; missing tests for new metrics.
- **Next:** Ensure all tables use these helpers; vectorize heavy calculations; add tests for each metric function.

---

## Deep Dives
- `walkthrough/etl/calculations/goals.md`
- `walkthrough/etl/calculations/corsi.md`
- `walkthrough/etl/calculations/ratings.md`
- `walkthrough/etl/calculations/goalie_calculations.md`
- `walkthrough/etl/calculations/time.md`

---

## How to Read
1) Start with `goals.py` to lock in the goal filter.
2) Read Corsi/xG modules to see input expectations (columns).
3) Check how outputs are consumed in `tables/*` or `base_etl.py`.

---

## Changing Safely
- Add/modify metrics here, then wire into tables.
- Add unit tests per metric (inputs → expected outputs).
- Avoid inline re-implementation of formulas elsewhere.*** End Patch Silently***
