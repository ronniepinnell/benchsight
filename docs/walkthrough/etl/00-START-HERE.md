# BenchSight Code Walkthrough

**A comprehensive guide to understanding the BenchSight codebase**

---

## Welcome

This documentation will help you understand how the entire BenchSight system works - from raw game tracking data to the analytics dashboard. It's designed for someone with intermediate Python/SQL knowledge who wants to truly understand the code before modifying or rebuilding it.

**What You'll Learn:**
- How to read and navigate a large codebase
- Why architectural decisions were made
- How data flows through the system
- What each module does and why
- Good patterns to follow and technical debt to avoid

---

## Reading Order

Read these files **in order** - each builds on the previous:

### Phase 1: Foundation (Start Here)
| # | File | Time | What You'll Learn |
|---|------|------|-------------------|
| 1 | [01-mental-models.md](01-mental-models.md) | 30 min | How to read large codebases; data flow thinking |
| 2 | [02-system-map.md](02-system-map.md) | 20 min | The five systems; navigation cheat sheet |

### Phase 2: ETL Deep Dive (Core Understanding)
| # | File | Time | What You'll Learn |
|---|------|------|-------------------|
| 3 | [03-etl-overview.md](03-etl-overview.md) | 25 min | Why ETL exists; design decisions |
| 4 | [04-etl-architecture.md](04-etl-architecture.md) | 40 min | Module organization; the 11 phases |
| 5 | [05-etl-code-walkthrough.md](05-etl-code-walkthrough.md) | 60 min | Annotated code; follow a goal through the system |
| 6 | [06-etl-patterns.md](06-etl-patterns.md) | 25 min | Good/bad patterns; technical debt |

### Phase 3: Data Model
| # | File | Time | What You'll Learn |
|---|------|------|-------------------|
| 7 | [07-data-model.md](07-data-model.md) | 30 min | Star schema; 139 tables explained |
| 8 | [08-critical-tables.md](08-critical-tables.md) | 45 min | fact_events, fact_player_game_stats column-by-column |
| 9 | [09-calculations.md](09-calculations.md) | 40 min | xG, WAR/GAR, Corsi, Fenwick formulas |

### Phase 4: Frontend & Integration
| # | File | Time | What You'll Learn |
|---|------|------|-------------------|
| 10 | [10-dashboard.md](10-dashboard.md) | 30 min | Next.js overview; query patterns |
| 11 | [11-api.md](11-api.md) | 20 min | FastAPI structure |
| 12 | [12-tracker.md](12-tracker.md) | 20 min | Game tracking; export format |
| 13 | [13-integration.md](13-integration.md) | 25 min | Complete data flow; system boundaries |
| 14 | [14-making-changes.md](14-making-changes.md) | 20 min | How to add stats, tables, debug |

### Reference
| File | Purpose |
|------|---------|
| [appendix-glossary.md](appendix-glossary.md) | Hockey terms, technical terms, BenchSight-specific terms |

**Total Time:** ~7 hours for complete walkthrough

---

## Prerequisites

Before starting, you should:

1. **Have basic Python knowledge:**
   - Functions, classes, decorators
   - pandas DataFrames (read/filter/group/join)
   - File I/O (CSV, Excel)

2. **Have basic SQL knowledge:**
   - SELECT, WHERE, JOIN, GROUP BY
   - Primary/foreign keys
   - Aggregations (SUM, COUNT, AVG)

3. **Have the code checked out:**
   ```bash
   git clone <repo-url>
   cd benchsight
   ```

4. **Have a text editor ready:**
   - VS Code recommended
   - Open the repo root so you can follow along

---

## Quick Reference

### "I need to change X, where do I look?"

| Task | Go To |
|------|-------|
| Change how goals are counted | `src/calculations/goals.py` |
| Add a new stat to player stats | `src/builders/player_stats.py` |
| Change xG calculation | `src/calculations/xg.py` or `config/formulas.json` |
| Add a new dashboard page | `ui/dashboard/src/app/norad/` |
| Add a new API endpoint | `api/routes/` |
| Change a dimension table | `src/tables/dimension_tables.py` |
| Debug ETL | `run_etl.py` → `src/core/base_etl.py` |
| Find table column definitions | `docs/data/DATA_DICTIONARY.md` |

### Key Files (Read These First)

| File | Lines | Why It Matters |
|------|-------|----------------|
| `run_etl.py` | ~150 | Entry point - how ETL starts |
| `src/core/base_etl.py` | ~1,065 | ETL orchestrator - controls everything |
| `src/core/etl_phases/` | ~4,700 | Modular phase implementations |
| `src/calculations/goals.py` | ~135 | Critical business rule - goal counting |
| `src/builders/player_stats.py` | ~800 | Creates fact_player_game_stats (317 columns) |
| `config/formulas.json` | ~200 | Formula definitions (xG, GAR weights) |

### The Five Systems

```
┌─────────────────────────────────────────────────────────────────┐
│                         BENCHSIGHT                               │
├─────────┬─────────┬─────────┬─────────┬─────────────────────────┤
│ TRACKER │   ETL   │   DB    │   API   │       DASHBOARD         │
│  (Input)│(Transform│ (Store) │ (Access)│       (Display)         │
│         │         │         │         │                         │
│ HTML/JS │ Python  │Supabase │ FastAPI │ Next.js/React           │
│         │ pandas  │PostgreSQL│        │ TypeScript              │
└─────────┴─────────┴─────────┴─────────┴─────────────────────────┘
     ↓         ↓         ↓         ↓              ↓
  Game     139 CSV    Cloud      REST        Analytics
  events   tables     hosted   endpoints     charts
```

---

## How to Use This Documentation

### Active Reading

1. **Open the code alongside the docs**
   - When we reference `src/core/base_etl.py:956`, open that file and go to line 956
   - Follow along in your editor

2. **Run the code as you read**
   ```bash
   # Run ETL to see it in action
   ./benchsight.sh etl run --wipe

   # Check output tables
   ls data/output/*.csv | head -20
   ```

3. **Ask "why" constantly**
   - Why does this function exist?
   - Why is this a separate file?
   - Why this data structure?

### Annotations

Throughout the docs, you'll see:

| Symbol | Meaning |
|--------|---------|
| ✅ | Good pattern - learn from this |
| ⚠️ | Technical debt - understand but improve |
| 🔑 | Critical concept - must understand |
| 💡 | Insight - deeper understanding |
| 📍 | Code location reference |

---

## Getting Help

- **Project Documentation:** `docs/MASTER_INDEX.md`
- **Data Dictionary:** `docs/data/DATA_DICTIONARY.md`
- **ETL Flow:** `docs/etl/CODE_FLOW_ETL.md`

---

*Last Updated: 2026-01-21*
