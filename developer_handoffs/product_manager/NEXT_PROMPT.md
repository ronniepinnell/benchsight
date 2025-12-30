# BenchSight Product Manager - Session Prompt

Copy and paste this prompt to start your session:

---

I'm the Product Manager for BenchSight, a hockey analytics platform for the NORAD recreational hockey league.

## Project Overview

- **Total Tables:** 98 (44 dimensions + 51 facts + 1 QA + 2 video)
- **Player Stats:** 317 columns per player per game
- **Total Columns:** 1,909 across all tables
- **Games Processed:** 9 currently, ~125K rows
- **Tests:** 290 passing

## Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| ETL Pipeline | ✅ Working | Processes games → 98 CSV files |
| CSV Outputs | ✅ Complete | All tables generated |
| Supabase Schema | ⚠️ **BLOCKING** | 18 tables need fixes |
| Dashboard | 📋 HTML Prototype | Needs React build |
| Tracker | 📋 HTML Prototype | Needs React build |
| Portal | 📋 HTML Prototype | Needs React build |
| Video Highlights | 📋 Spec'd | SQL ready, not implemented |
| Mobile App | ❌ Not Started | Phase 5 |

## Blocking Issue

**18 tables have schema mismatches.** Frontend work is blocked until Supabase Dev fixes this. See `docs/SUPABASE_SCHEMA_ISSUES.md`.

## Work Order

1. **Supabase Dev** - Fix 18 tables (1-2 days) ← CURRENT BLOCKER
2. **Sr. Engineer** - Code review, add tests (1 week)
3. **Tracker Dev** - Build React app (2-3 weeks)
4. **Dashboard Dev** - Build React app (2-3 weeks, can parallel)
5. **Portal Dev** - Admin tools (2-3 weeks, can parallel)
6. **Mobile** - Future phase

## Key Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Tables | 98 | 98 |
| Player stats/game | 317 | 317 |
| Games processed | 9 | 100+ |
| Test coverage | ~60% | 80%+ |
| Supabase tables loading | 80/98 | 98/98 |

## Key Documentation

- Quick reference: `developer_handoffs/product_manager/QUICK_REFERENCE.md`
- Full handoff: `developer_handoffs/product_manager/PRODUCT_MANAGER_HANDOFF.md`
- What works/doesn't: `docs/HONEST_ASSESSMENT.md`
- Current blockers: `docs/SUPABASE_SCHEMA_ISSUES.md`

## My Specific Request

[DESCRIBE YOUR REQUEST]

## Complete Table Reference

See `docs/TABLE_REFERENCE_COMPLETE.md` for all 98 tables:
- 44 dimension tables
- 51 fact tables  
- 1 QA table
- 2 video tables (pending)

Key tables by app:
- **Dashboard reads:** fact_player_game_stats (317 cols), fact_events, fact_team_game_stats, all dims
- **Tracker writes:** fact_events, fact_shifts, fact_video_highlights
- **Portal manages:** All dim_* tables, fact_gameroster, fact_registration
