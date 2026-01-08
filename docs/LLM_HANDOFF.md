# BenchSight LLM Handoff Document

**Version:** 16.08  
**Date:** January 8, 2026  
**Status:** Production ETL + Tracker v16.08

---

## 🚨 CRITICAL: Read First

1. **Goals are counted ONE way:** `event_type='Goal' AND event_detail='Goal_Scored'`
2. **17 total goals** across 4 games - this is IMMUTABLE and verified
3. **111+ tables** in the data warehouse
4. **ALWAYS read** `LLM_REQUIREMENTS.md` before making changes
5. **Read** `docs/STRATEGIC_PLAN.md` for rebuild roadmap

---

## 📊 Current State

### Platform Components
| Component | Status | Version | Location |
|-----------|--------|---------|----------|
| ETL Pipeline | ✅ Production | 14.21 | src/ |
| Tracker UI | 🟡 Beta | 16.08 | ui/tracker/index.html |
| Dashboard | 🔴 Planned | - | docs/html/dashboard/ |
| Portal | 🔴 Planned | - | - |
| API | 🔴 Planned | - | - |

### Tables
- **Total:** 111+ tables
- **Dimensions:** 50+ (dim_*)
- **Facts:** 50+ (fact_*)
- **QA:** 5+ (qa_*)

### Games Tracked
| Game ID | Goals | Home | Away | Status |
|---------|-------|------|------|--------|
| 18969 | 7 | Velodrome | AMOS | ✅ Verified |
| 18977 | 6 | Velodrome | Ace | ✅ Verified |
| 18981 | 3 | Velodrome | Rusty | ✅ Verified |
| 18987 | 1 | Velodrome | Rusty | ✅ Verified |

---

## 🎮 Tracker v16.08

### Location
- **Primary:** `ui/tracker/index.html`
- **Standalone:** Can be used as single HTML file

### Key Features
- Full event types with Supabase-driven dropdowns
- XY coordinates (center-relative, 0,0 = center ice)
- Event details from dim_event_detail (filtered by event_type_name)
- Event details 2 from dim_event_detail_2 (filtered by code prefix)
- Play details from dim_play_detail/dim_play_detail_2
- Shift tracking with player slots
- Linked events (shot → rebound → goal chains)
- Auto-calc for success and pressure
- Team colors/logos from dim_team

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| 1-6 | Select Event Player 1-6 |
| Ctrl+1-6 | Select Opponent Player 1-6 (may conflict with browser) |
| ` (backtick) | Switch to Puck XY mode |
| H / A | Home / Away team |
| Tab | Toggle Puck/Player mode |
| F/S/P/G/T/Z | Event type hotkeys |
| Enter | Log event |
| L | Log shift |

### Known Issues
- Ctrl+1-6 conflicts with browser tab switching
- Shift edit modal dropdown mismatch
- No video integration yet

---

## 📚 Key Documents

### Essential (Read in Order)
1. `LLM_REQUIREMENTS.md` - Critical rules
2. `docs/STRATEGIC_PLAN.md` - Full rebuild roadmap
3. `docs/HONEST_ASSESSMENT.md` - Current limitations
4. `docs/TODO.md` - Known issues
5. `CHANGELOG.md` - Version history

### Technical
- `docs/TRACKER_ETL_SPECIFICATION.md` - Export format
- `docs/SUPABASE_SETUP_GUIDE.md` - Database setup
- `docs/DATA_DICTIONARY.md` - Table/column reference

### Navigation
- `docs/html/index.html` - Master documentation portal

---

## 🔧 Recent Changes

### v16.08 (Current)
- Fixed event_detail_2 dropdown (code prefix filter)
- Added STRATEGIC_PLAN.md with full rebuild roadmap
- Updated all documentation to v16.08
- Created comprehensive HTML index

### v16.07
- Fixed 1-6 keyboard shortcuts
- Added backtick for puck mode
- Added auto-calc buttons for success/pressure
- Smaller XY markers with click-through

### v16.06
- Event details from dim_event_detail
- Center-relative XY coordinates
- Play details from Supabase

---

## 🚀 Next Steps for New Chat

### If Continuing Tracker Development
1. Read `LLM_REQUIREMENTS.md`
2. Read `docs/HONEST_ASSESSMENT.md` for limitations
3. Read `docs/TODO.md` for known issues
4. Test tracker at `ui/tracker/index.html`

### If Starting React Rebuild
1. Read `docs/STRATEGIC_PLAN.md` for architecture
2. Set up Next.js monorepo
3. Start with RinkVisualization component
4. Follow component breakdown in strategic plan

### If Working on ETL
1. Read `docs/TRACKER_ETL_SPECIFICATION.md`
2. Run existing tests with `python scripts/run_tests.py`
3. Verify goals with `qa_goal_accuracy` table

### If Working on Dashboard/Portal
1. Read `docs/STRATEGIC_PLAN.md` Phase 3-4
2. Review prototypes in `docs/html/prototypes/`
3. Consider hosting options (Vercel recommended)

---

## 🔑 Critical Reminders

### Goal Counting (IMMUTABLE)
```sql
-- THE ONLY WAY TO COUNT GOALS
SELECT * FROM fact_events 
WHERE event_type = 'Goal' 
AND event_detail = 'Goal_Scored';
```

### Export Format
- Events: LONG format (one row per player per event)
- Shifts: WIDE format (one row per shift)
- XY: Separate sheet (up to 10 points per player/puck)

### Supabase Tables
- dim_event_detail: Filter by event_type_name
- dim_event_detail_2: Filter by code prefix (e.g., "ZoneEntry_")
- dim_play_detail: Filter by category
- dim_play_detail_2: Filter by detail_1 value

---

*Last verified: January 8, 2026*
