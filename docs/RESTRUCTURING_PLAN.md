# BenchSight Project Restructuring Plan

## Project Paths

### Primary Working Directory (to be fixed)
```
/Users/ronniepinnell/Documents/Documents - Ronnie's MacBook Pro - 1/Programming_HD/Hockey/Benchsight/git/benchsight
```

### Current Issue
- Documents location is missing `.git` directory and tracker HTML files
- Dropbox has complete copy: `/Users/ronniepinnell/Dropbox/PROGRAMMING/Hockey/Benchsight/git/benchsight`

### Resolution (Phase 0, Step 1)
Re-clone or sync the repository to fix the Documents location

---

## Git Strategy: Use `develop` Branch
**Why develop branch (not new repo):**
- Production stays safe on `main`
- Easy to merge when ready
- Vercel auto-deploys `develop` to dev environment
- Can always abandon branch if needed
- Maintains full git history

**Workflow:**
```bash
# Create develop branch from main
git checkout -b develop

# All restructuring work happens on develop
# Production (main) remains untouched

# When ready, merge to main via PR
git checkout main
git merge develop
```

---

## Executive Summary

This plan restructures BenchSight from a working prototype into a sustainable, well-documented hockey analytics platform. The project consists of:

- **ETL Pipeline**: Python (84 files, 138+ tables) - needs performance optimization and refactoring
- **Dashboard**: Next.js skeleton (1 component) - needs full implementation
- **Tracker**: HTML-based (backup location) - convert to Next.js (then optionally Rust)
- **Portal**: Admin interface for ETL management and team/coach administration

---

## Phase 0: Foundation Setup (1-2 days)

### 0.1 Environment Setup
- [ ] Verify Supabase `develop` branch configuration
- [ ] Verify Vercel `benchsight-dev` project setup
- [ ] Test `./scripts/switch_env.sh dev` works correctly

### 0.2 Environment Naming Standardization
Standardize on `dev` (not sandbox/develop):

**Files to modify:**
- `scripts/switch_env.sh` - update to prefer `dev`
- `scripts/deploy_to_dev.sh` - change `sandbox` to `dev`
- `config/config_local.develop.ini` → rename to `config_local.dev.ini`

### 0.3 Claude Rules File
**Create:** `.claude/settings.json`
```json
{
  "projectRules": [
    "Use vectorized pandas operations, never .iterrows()",
    "Max 300 lines per function, max 1000 lines per file",
    "All new dashboard components use server components by default",
    "Follow existing key generation patterns in key_utils.py"
  ]
}
```

---

## Phase 1: Documentation Consolidation (3-5 days)

### 1.1 Documentation Inventory
Current state: 60+ markdown files scattered across:
- `docs/` (21 files)
- `ui/dashboard/` (7 files)
- `docs/archive/` (version-specific)
- `docs/troubleshooting/` (11 files)

### 1.2 New Documentation Structure
**Create consolidated docs:**

```
docs/
├── README.md                    # Project overview
├── MASTER_ROADMAP.md           # Complete project roadmap
├── PROJECT_RULES.md            # Coding standards, conventions
├── SETUP_GUIDE.md              # Consolidated setup guide
├── DATA_DICTIONARY.md          # Keep existing (excellent)
├── ETL_DOCUMENTATION.md        # ETL flow and execution
├── DASHBOARD_ROADMAP.md        # Dashboard implementation plan
├── TRACKER_DOCUMENTATION.md    # Tracker logic (from HTML)
├── PORTAL_DESIGN.md            # Portal requirements
├── DEPLOYMENT_GUIDE.md         # Consolidated deployment
└── archive/                    # Old version-specific docs
```

### 1.3 Consolidation Tasks
1. Merge `COMPLETE_SETUP_GUIDE.md`, `DEV_ENVIRONMENT_SETUP.md`, `DEV_SANDBOX_SETUP.md`, `SUPABASE_BRANCHING.md` → `SETUP_GUIDE.md`
2. Move `ui/dashboard/*.md` files to `docs/`
3. Archive `docs/archive/AGENT_HANDOFF_V29.x.md` files
4. Create `MASTER_ROADMAP.md` from existing roadmap fragments

---

## Phase 2: Code Documentation (5-7 days)

### 2.1 ETL Documentation
**Create:** `docs/ETL_DOCUMENTATION.md`

Document the 11-phase ETL pipeline:
```
Phase 1: Load BLB Tables (base_etl.py:load_blb_tables)
Phase 2: Build Player Lookup
Phase 3: Load Tracking Data
Phase 3B: Static Dimensions (58 dim_* tables)
Phase 4: Core Player Stats (fact_player_game_stats)
Phase 4B: Shift Analytics (fact_h2h, fact_wowy)
Phase 4C-D: Remaining Facts
Phase 5-11: Advanced Analytics, QA, XY coords
```

Include:
- Module-by-module documentation
- Data flow diagrams
- Key function references with line numbers
- Table dependency order

### 2.2 Tracker Logic Documentation (CRITICAL)
**Create:** `docs/TRACKER_DOCUMENTATION.md`

**Source:** User will provide path to backup HTML tracker file

Document ALL logic before conversion:
- State management (game state, event state)
- Event types and codes (complete mapping)
- Keyboard shortcuts
- UI/UX flows
- Player selection logic
- Shift management
- Export format (Excel schema)
- Validation rules

### 2.3 Dashboard Architecture
**Create:** `docs/DASHBOARD_ROADMAP.md`

Current state:
- 1 component: `PlayByPlayTimeline.tsx` (430 lines)
- package.json: only 2 dependencies

Target architecture and page list.

---

## Phase 3: ETL Cleanup & Refactoring (3-4 weeks)

### 3.1 Performance Optimization
**Priority:** Replace `.iterrows()` with vectorized operations

Found: 233 instances of `.iterrows()` (10-100x slower than vectorized)

**High-priority files:**
- `src/tables/remaining_facts.py` - multiple instances
- `src/core/base_etl.py` - critical path
- `src/tables/core_facts.py` - frequent calls

**Pattern to apply:**
```python
# BEFORE (slow):
for _, row in df.iterrows():
    result = (row['period'] - 1) * 900

# AFTER (fast):
result = (df['period'] - 1).clip(lower=0) * 900
```

### 3.2 base_etl.py Refactoring
**Current:** 5,599 lines, 40+ functions

**Target structure:**
```
src/core/
├── base_etl.py          # Orchestrator only (~500 lines)
├── data_loader.py       # load_blb_tables(), load_tracking_data()
├── event_enhancer.py    # enhance_event_tables()
├── shift_enhancer.py    # enhance_shift_tables()
├── table_creator.py     # create_derived_tables()
├── key_utils.py         # (keep existing)
├── table_writer.py      # (keep existing)
└── safe_csv.py          # (keep existing)
```

### 3.3 Table Verification
- Compare 138+ documented tables vs actual Supabase tables
- Identify orphan/unused tables
- Verify schema matches DATA_DICTIONARY
- Document any dev/prod schema differences

---

## Phase 4: Dashboard Development (4-6 weeks)

### 4.1 Foundation Setup (Week 1)
**Update:** `ui/dashboard/package.json`

Add dependencies:
```json
{
  "@supabase/supabase-js": "^2.x",
  "@supabase/ssr": "^0.x",
  "lucide-react": "^0.x",
  "recharts": "^2.x",
  "clsx": "^2.x",
  "class-variance-authority": "^0.x",
  "tailwind-merge": "^2.x"
}
```

**Create:**
- `lib/supabase/client.ts` - Browser client
- `lib/supabase/server.ts` - Server client
- `components/layout/Sidebar.tsx`
- `components/layout/Topbar.tsx`
- `lib/utils.ts` - Utility functions

### 4.2 Core Pages (Weeks 2-4)
**Priority order:**
1. `/standings` - Team standings
2. `/leaders` - Statistical leaders
3. `/players` - Player directory
4. `/players/[id]` - Player profile
5. `/teams` - Team directory
6. `/teams/[id]` - Team profile
7. `/games` - Game list
8. `/games/[id]` - Game detail (uses existing PlayByPlayTimeline)

### 4.3 Component Library (Weeks 5-6)
**Create reusable components:**
- `SortableTable.tsx` - Generic sortable table
- `StatCard.tsx` - Stat display card
- `PlayerCard.tsx` - Player summary
- `TeamLogo.tsx` - Team logo display
- Chart components (RadarChart, TrendChart, ShotMap)

---

## Phase 5: Tracker Conversion (6-8 weeks)

### 5.1 Technology
**Approach:** Start with Next.js + TypeScript, add Rust/WASM later if needed

Benefits:
- Same stack as dashboard
- Shared component library
- Shared Supabase integration
- Can add Rust calculation engine later for performance

### 5.2 Component Architecture
```
ui/tracker/src/
├── app/
│   ├── page.tsx                    # Main tracker page
│   └── layout.tsx
├── components/
│   ├── EventForm/
│   │   ├── EventTypeGrid.tsx       # Event type selection
│   │   ├── PlayerSelect.tsx        # Player selection
│   │   ├── LocationPicker.tsx      # Rink location
│   │   └── EventForm.tsx
│   ├── ShiftPanel/
│   │   ├── ShiftList.tsx
│   │   ├── ShiftEditor.tsx
│   │   └── ShiftPanel.tsx
│   ├── GameState/
│   │   ├── ScoreBoard.tsx
│   │   ├── PeriodClock.tsx
│   │   └── GameState.tsx
│   └── RinkDisplay/
│       ├── Rink.tsx                # SVG rink
│       └── EventMarkers.tsx
├── lib/
│   └── tracker/
│       ├── state.ts                # Zustand store
│       ├── types.ts                # TypeScript types
│       ├── calculations.ts
│       └── export.ts               # Excel export
└── hooks/
    ├── useGameState.ts
    ├── useKeyboardShortcuts.ts
    └── useAutoSave.ts
```

### 5.3 Migration Strategy
1. **Parallel Development** (2 weeks) - Build alongside HTML
2. **Feature Parity** (3 weeks) - Match all HTML functionality
3. **Enhanced Features** (2 weeks) - Real-time sync, improved UX
4. **Cutover** (1 week) - Testing, archive HTML

---

## Phase 6: Portal Development (After Phase 4.1)

### 6.1 Portal Purpose
Admin interface for:
- Running ETL pipelines
- Managing data
- Future: Team logins, roster management, coach tools

### 6.2 Architecture
```
ui/portal/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   └── register/
│   ├── (admin)/
│   │   ├── etl/                    # ETL management
│   │   │   ├── run/                # Run ETL
│   │   │   └── status/             # ETL status
│   │   ├── tables/                 # Table management
│   │   └── settings/               # System settings
│   └── (team)/                     # Future: team features
│       ├── roster/
│       ├── schedule/
│       └── settings/
└── components/
    ├── etl/
    │   ├── ETLRunner.tsx
    │   └── ETLStatus.tsx
    └── admin/
```

### 6.3 Features
**Phase 1 (MVP):**
- ETL execution UI
- Table status/counts
- Data verification tools

**Phase 2 (Future):**
- Team authentication
- Roster management
- Coach dashboards

---

## Critical Files Reference

| File | Purpose | Phase |
|------|---------|-------|
| `docs/DATA_DICTIONARY_COMPLETE.md` | Schema reference | All |
| `docs/COMPREHENSIVE_CODE_REVIEW.md` | Issues reference | 3 |
| `src/core/base_etl.py` | Main refactor target | 3 |
| `scripts/switch_env.sh` | Environment fix | 0 |
| `ui/dashboard/package.json` | Dependency updates | 4 |
| [Tracker HTML - path TBD] | Logic extraction | 2, 5 |

---

## Verification Checklist

### Phase 0 Verification
- [ ] `./scripts/switch_env.sh dev` works
- [ ] Supabase develop branch accessible
- [ ] Vercel dev deployment works

### Phase 1 Verification
- [ ] Single source of truth for each doc topic
- [ ] All outdated docs archived
- [ ] Master docs created

### Phase 2 Verification
- [ ] ETL flow documented with all 11 phases
- [ ] Tracker logic 100% documented
- [ ] Dashboard architecture defined

### Phase 3 Verification
- [ ] 50%+ reduction in iterrows
- [ ] base_etl.py < 500 lines
- [ ] ETL output unchanged (compare before/after)

### Phase 4 Verification
- [ ] `npm run dev` works
- [ ] All core pages render
- [ ] Supabase data loads correctly

### Phase 5 Verification
- [ ] Feature parity with HTML tracker
- [ ] Export format identical
- [ ] All keyboard shortcuts work

---

## Timeline Summary

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 0 | 1-2 days | None |
| Phase 1 | 3-5 days | Phase 0 |
| Phase 2 | 5-7 days | Phase 1 partial |
| Phase 3 | 3-4 weeks | Phase 2.1 |
| Phase 4 | 4-6 weeks | Phase 2.3 |
| Phase 5 | 6-8 weeks | Phase 2.2 |
| Phase 6 | TBD | Phase 4.1 |

**Total: 4-6 months**

---

## Next Steps (Ready to Start)

**Primary Location:**
`/Users/ronniepinnell/Documents/Documents - Ronnie's MacBook Pro - 1/Programming_HD/Hockey/Benchsight/git/benchsight`

**First Actions (Phase 0):**
1. **Fix repository** - Copy `.git` folder and missing files from Dropbox to Documents:
   ```bash
   # Copy .git directory
   cp -r "/Users/ronniepinnell/Dropbox/PROGRAMMING/Hockey/Benchsight/git/benchsight/.git" \
         "/Users/ronniepinnell/Documents/Documents - Ronnie's MacBook Pro - 1/Programming_HD/Hockey/Benchsight/git/benchsight/"

   # Copy tracker files
   cp -r "/Users/ronniepinnell/Dropbox/PROGRAMMING/Hockey/Benchsight/git/benchsight/ui/tracker/"* \
         "/Users/ronniepinnell/Documents/Documents - Ronnie's MacBook Pro - 1/Programming_HD/Hockey/Benchsight/git/benchsight/ui/tracker/"
   ```
2. Switch to `develop` branch
3. Verify tracker file exists: `ui/tracker/tracker_index_v23.5.html`
4. Standardize environment naming (dev vs sandbox)
5. Create `.claude/settings.json` with project rules
6. Verify Supabase and Vercel dev environments
