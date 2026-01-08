# New Chat Guide - Parallel Development

**Version:** 17.00  
**Date:** January 8, 2026

---

## 🚀 Immediate Next Steps for New Chat

### Option A: Continue Tracker Bug Fixes (Quick Wins)

**Start prompt:**
```
I'm continuing BenchSight tracker development. Here's the current state:
- Version: 17.00
- Location: ui/tracker/index.html

Please read:
1. LLM_REQUIREMENTS.md
2. docs/HONEST_ASSESSMENT.md
3. docs/TODO.md

Fix the following priority issues:
1. Add "Save As" file picker for local saves
2. Fix score verification loading
3. Add validation warnings for impossible events
```

**Files to read:**
- `LLM_REQUIREMENTS.md`
- `docs/TODO.md`
- `ui/tracker/index.html` (lines 6500-6600 for keyboard handling)

---

### Option B: Start React Rebuild (Parallel Development)

**Start prompt:**
```
I'm starting the BenchSight React rebuild while the MVP tracker continues in use.

Please read:
1. docs/STRATEGIC_PLAN.md (full architecture and component breakdown)
2. LLM_REQUIREMENTS.md (critical data rules)

Create the initial monorepo structure:
- apps/tracker (Next.js)
- apps/dashboard (Next.js)  
- apps/portal (Next.js)
- packages/ui (shared components)
- packages/types (TypeScript types)
- packages/api (Supabase client)
```

**Files to read:**
- `docs/STRATEGIC_PLAN.md` - Complete architecture
- `docs/TRACKER_ETL_SPECIFICATION.md` - Export format (for compatibility)

**First tasks:**
1. Create monorepo scaffold with Turborepo
2. Set up Next.js 14 with TypeScript
3. Create shared types from current tracker state
4. Build RinkVisualization component first

---

### Option C: Build Admin Portal

**Start prompt:**
```
I'm building the BenchSight admin portal for ETL automation.

Please read:
1. docs/STRATEGIC_PLAN.md (Phase 3)
2. docs/html/prototypes/admin_portal_preview.html

Build a portal that:
1. Lists all games from dim_schedule
2. Shows tracking status (tracked/not tracked)
3. Has "Run ETL" button that triggers pipeline
4. Shows ETL run history and status
```

**Files to read:**
- `docs/STRATEGIC_PLAN.md` - Portal architecture
- `docs/html/prototypes/admin_portal_preview.html` - UI prototype

---

### Option D: Dashboard Development

**Start prompt:**
```
I'm building the public BenchSight dashboard.

Please read:
1. docs/STRATEGIC_PLAN.md (Phase 4)
2. docs/html/dashboard/ - existing prototypes

Create a dashboard that:
1. Shows league standings
2. Player stats with filtering
3. Team comparisons
4. Game summaries
```

**Files to read:**
- `docs/html/dashboard/` - All prototypes
- `docs/STAT_DICTIONARY.md` - Available statistics

---

### Option E: ETL Testing & Validation

**Start prompt:**
```
I'm building comprehensive ETL tests for BenchSight.

Please read:
1. docs/TRACKER_ETL_SPECIFICATION.md
2. src/ directory structure

Create tests that:
1. Validate tracker export format
2. Verify goal counts match official records
3. Check all 111+ tables are populated correctly
4. Compare stats against noradhockey.com
```

**Files to read:**
- `docs/TRACKER_ETL_SPECIFICATION.md` - Export format
- `scripts/run_tests.py` - Existing test framework

---

## 📋 Critical Rules for All Chats

### Goal Counting (NEVER CHANGE)
```sql
-- THE ONLY WAY TO COUNT GOALS
WHERE event_type = 'Goal' AND event_detail = 'Goal_Scored'
```

### Verified Data
- **17 total goals** across 4 games
- **4 games:** 18969, 18977, 18981, 18987
- **All verified** against noradhockey.com

### Export Format
- Events: LONG format (one row per player per event)
- Shifts: WIDE format (one row per shift)
- XY: Separate sheet

### Supabase Filters
- `dim_event_detail`: Filter by `event_type_name`
- `dim_event_detail_2`: Filter by code prefix (e.g., "ZoneEntry_")
- `dim_play_detail`: Filter by `category`

---

## 📁 Key File Locations

| Purpose | Location |
|---------|----------|
| Main requirements | `LLM_REQUIREMENTS.md` |
| Strategic plan | `docs/STRATEGIC_PLAN.md` |
| Current issues | `docs/TODO.md` |
| Honest assessment | `docs/HONEST_ASSESSMENT.md` |
| Tracker | `ui/tracker/index.html` |
| Dashboard protos | `docs/html/dashboard/` |
| Portal proto | `docs/html/prototypes/admin_portal_preview.html` |
| ETL spec | `docs/TRACKER_ETL_SPECIFICATION.md` |
| Data dictionary | `docs/DATA_DICTIONARY.md` |
| HTML doc portal | `docs/html/index.html` |

---

## 🔄 Parallel Development Strategy

### What Ronnie is doing:
- Using MVP tracker v16.08 to log backlog games
- Export data to Excel
- Will run ETL when games are tracked

### What Claude can do in parallel:
1. **React rebuild** - Build new tracker without breaking MVP
2. **Portal** - Build ETL automation
3. **Dashboard** - Build public stats display
4. **Tests** - Build validation framework

### Coordination:
- MVP tracker export format is FIXED (don't change it)
- New React tracker must export SAME format
- All work feeds into SAME Supabase database
- ETL pipeline is SHARED

---

## ⚠️ What NOT to Do

1. **Don't change MVP tracker export format** - ETL depends on it
2. **Don't modify goal counting logic** - It's verified correct
3. **Don't delete existing prototypes** - They're reference implementations
4. **Don't start from scratch** - Build on existing foundation

---

*This guide ensures continuity across chat sessions while enabling parallel development.*
