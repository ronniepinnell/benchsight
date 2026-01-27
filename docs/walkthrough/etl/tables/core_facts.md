# tables/core_facts.py Deep Dive

**Builds core fact tables: player/team/goalie game stats**

Last Updated: 2026-01-21  
Version: 2.00

---

## Purpose
`src/tables/core_facts.py` constructs core fact tables (fact_player_game_stats, fact_team_game_stats, fact_goalie_game_stats) and applies many advanced metrics (xG, WAR/GAR, competition tiers, linemates, time buckets, rebounds, etc.).

---

## What It Does
- Aggregates event/shift data into game-level stats for players, teams, goalies.
- Applies xG, WAR/GAR weights, rebound/second-chance, pressure, sequences.
- Adds names to tables, drops all-null columns, writes to CSV.

---

## Flow (Conceptual)
```mermaid
flowchart TD
    Events[fact_events (+ derived flags)] --> CoreFacts
    Shifts[fact_shifts/fact_shift_players] --> CoreFacts
    Schedule[dim_schedule/dim_season] --> CoreFacts
    CoreFacts --> PlayerGame[fact_player_game_stats]
    CoreFacts --> TeamGame[fact_team_game_stats]
    CoreFacts --> GoalieGame[fact_goalie_game_stats]
```

---

## Key Elements
- **Goal detection:** uses `is_goal_scored` helper (ensure aligned with calculations/goals.py).
- **WAR/GAR weights:** configured at top; applied to offensive/defensive contributions.
- **xG modifiers:** base rates and situational modifiers (rush, rebound, one-timer, etc.).
- **Linemate/time bucket/rebound/pressure analytics:** enrich player stats.
- **Name enrichment:** adds player/team names before saving; removes all-null columns.

---

## Dependencies
- Requires upstream event/shift tables with derived flags (is_goal, is_corsi, etc.).
- Uses `drop_all_null_columns` from `base_etl`.
- Assumes dim tables exist for names (dim_player, dim_team) when adding names.

---

## Good / Risks / Next
- **Good:** Rich feature set; consolidates many analytics into core facts; name enrichment + null cleanup.
- **Risks:** Large/complex; may diverge from canonical metric helpers (ensure goal/xG logic stays synced); performance risk if heavy row-wise ops; depends on upstream flags being correct.
- **Next:** Audit alignment with `src/calculations/*`; modularize heavy sections; add targeted tests for WAR/xG/pressure components.

---

## Changing Safely
- Keep goal/xG/WAR logic consistent with calculations modules.
- Add/adjust tests when changing weights or modifiers.
- Avoid re-implementing filters inline; pull from calculations helpers where possible.
