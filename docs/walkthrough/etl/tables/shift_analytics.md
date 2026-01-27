# tables/shift_analytics.py Deep Dive

**Shift-level analytics: H2H, WOWY, line combos, shift quality**

Last Updated: 2026-01-21  
Version: 2.00

---

## Purpose
`src/tables/shift_analytics.py` builds shift-level analytics tables to analyze combinations and matchups.

---

## What It Does
- Adds player/team names; drops all-null columns.
- Builds:
  - `fact_h2h` (head-to-head players on ice together)
  - `fact_wowy` (with/without you analysis)
  - `fact_line_combos` (line combinations)
  - `fact_shift_quality`, `fact_shift_quality_logical`
- Uses `fact_shift_players`, `dim_schedule`, `dim_player`, `dim_team`.

---

## Flow (Conceptual)
```mermaid
flowchart TD
    ShiftPlayers[fact_shift_players] --> H2H[fact_h2h/wowy/line_combos]
    H2H --> Quality[fact_shift_quality(_logical)]
```

---

## Dependencies
- fact_shift_players (with logical_shift_number)
- dim_player, dim_team for names
- dim_schedule for season context

---

## Good / Risks / Next
- **Good:** Central place for shift matchup analytics; name enrichment; null cleanup.
- **Risks:** Depends on correct logical_shift_number; heavy combinations can be expensive; schema drift risk if shift_players changes.
- **Next:** Add tests for H2H/WOWY correctness; optimize grouping/combination steps; validate logical_shift_number presence.

---

## Changing Safely
- Validate required columns (logical_shift_number, venue, players).
- Add tests for new combination logic or quality scoring changes.
