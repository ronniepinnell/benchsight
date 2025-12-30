# BenchSight

**Hockey Analytics Platform for NORAD Recreational Hockey League**

NHL-level analytics for rec hockey: 317 stats per player, video highlights, beautiful dashboards.

---

## 🚦 Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| ETL Pipeline | ✅ Working | 9 games, 125K rows |
| CSV Outputs | ✅ Complete | 98 tables generated |
| Supabase Schema | ⚠️ **NEEDS WORK** | 18 tables have schema mismatches |
| Dashboard | 📋 Prototype | HTML only, needs React |
| Tracker | 📋 Prototype | HTML only, needs React |
| Portal | 📋 Prototype | HTML only, needs React |
| Video Highlights | 📋 Spec'd | SQL ready, not implemented |

### ⚠️ BLOCKING ISSUE: Supabase Schema Mismatches

Before ANY frontend work begins, the Supabase schema must be fixed. See `docs/SUPABASE_SCHEMA_ISSUES.md` for details.

---

## 👥 Role-Based Quick Start

### Who Should Work on This First?

```
1. SUPABASE/BACKEND DEV (or Sr. Engineer)  ← START HERE
   Fix schema mismatches, get all 98 tables loading
   
2. CODE REVIEW / SR. ENGINEER
   Review ETL code, add tests, harden loader
   
3. TRACKER DEV
   Build React tracker (needs working Supabase + video tables)
   
4. DASHBOARD DEV  
   Build React dashboard (needs working Supabase)
   
5. PORTAL DEV
   Build admin portal (can parallel with Dashboard)
   
6. PRODUCT MANAGER
   Oversee timeline, priorities, stakeholders
```

---

## 📚 Documentation by Role

### 🔧 Supabase/Backend Developer
**Priority: CRITICAL - Do this first**

| Order | Document | Purpose | Time |
|-------|----------|---------|------|
| 1 | `docs/SUPABASE_SCHEMA_ISSUES.md` | **18 tables need fixing** | 30 min read |
| 2 | `developer_handoffs/supabase_dev/README.md` | Full handoff | 1 hr |
| 3 | `sql/01_CREATE_ALL_TABLES.sql` | Schema definitions | Reference |
| 4 | `sql/04_VIDEO_HIGHLIGHTS.sql` | Video tables to add | 15 min |
| 5 | `scripts/bulletproof_loader.py` | Understand loader | 30 min |

**Goal**: All 98 tables loading successfully with `--load missing` showing 0 failures.

---

### 🔍 Senior Engineer / Code Review
**Priority: HIGH - After Supabase is stable**

| Order | Document | Purpose | Time |
|-------|----------|---------|------|
| 1 | `developer_handoffs/code_review/README.md` | Overview | 10 min |
| 2 | `developer_handoffs/code_review/CODE_REVIEW_HANDOFF.md` | Full context | 1 hr |
| 3 | `developer_handoffs/code_review/TECHNICAL_DIAGRAMS.md` | Architecture | 30 min |
| 4 | `developer_handoffs/code_review/CODE_REVIEW_CHECKLIST.md` | Work through this | 2-4 hrs |
| 5 | `scripts/bulletproof_loader.py` | Review & harden | 2 hrs |
| 6 | `src/main.py` | Refactor candidate | 2 hrs |

**Goal**: Production-ready code with 80%+ test coverage, proper error handling.

---

### 📝 Tracker Developer
**Priority: MEDIUM - After Supabase + Video tables ready**

| Order | Document | Purpose | Time |
|-------|----------|---------|------|
| 1 | `developer_handoffs/tracker_dev/README.md` | Overview | 10 min |
| 2 | `docs/TRACKER_DATA_FORMAT.md` | **CRITICAL** - Exact columns/formats | 1 hr |
| 3 | `docs/SUPABASE_INTEGRATION_GUIDE.md` | How to read/write | 30 min |
| 4 | `docs/WIREFRAMES_AND_PAGES.md` | UI specifications | 30 min |
| 5 | `docs/VIDEO_HIGHLIGHTS_SPEC.md` | Highlight feature | 30 min |
| 6 | `tracker/tracker_v19.html` | Current prototype | Reference |

**Goal**: React app that writes events, shifts, XY coords, and video highlights to Supabase.

**Depends on**: 
- ✅ Supabase schema fixed
- ✅ Video highlight tables created (`dim_highlight_type`, `fact_video_highlights`)
- ✅ `fact_events` has highlight columns added

---

### 📊 Dashboard Developer
**Priority: MEDIUM - After Supabase stable**

| Order | Document | Purpose | Time |
|-------|----------|---------|------|
| 1 | `developer_handoffs/dashboard_dev/README.md` | Overview | 10 min |
| 2 | `docs/WIREFRAMES_AND_PAGES.md` | UI specifications | 30 min |
| 3 | `docs/SUPABASE_INTEGRATION_GUIDE.md` | How to query | 30 min |
| 4 | `docs/STATS_REFERENCE_COMPLETE.md` | All 317 stats explained | Reference |
| 5 | `dashboard/dashboard.html` | Current prototype | Reference |

**Goal**: React app displaying player stats, game box scores, leaderboards, highlights.

**Depends on**: 
- ✅ Supabase schema fixed
- ✅ Core fact tables populated (fact_player_game_stats, fact_events, etc.)

---

### ⚙️ Portal Developer
**Priority: LOW - Can parallel with Dashboard**

| Order | Document | Purpose | Time |
|-------|----------|---------|------|
| 1 | `developer_handoffs/portal_dev/README.md` | Overview | 10 min |
| 2 | `docs/WIREFRAMES_AND_PAGES.md` | UI specifications | 30 min |
| 3 | `docs/SUPABASE_INTEGRATION_GUIDE.md` | CRUD operations | 30 min |
| 4 | `portal/` | Current prototypes | Reference |

**Goal**: Admin portal for teams, players, schedules, registrations.

---

### 📋 Product Manager
**Priority: ONGOING**

| Order | Document | Purpose | Time |
|-------|----------|---------|------|
| 1 | `developer_handoffs/product_manager/QUICK_REFERENCE.md` | 2-min overview | 5 min |
| 2 | `developer_handoffs/product_manager/PRODUCT_MANAGER_HANDOFF.md` | Full strategy | 1 hr |
| 3 | `docs/HONEST_ASSESSMENT.md` | What works, what doesn't | 15 min |
| 4 | `docs/SUPABASE_SCHEMA_ISSUES.md` | Current blockers | 10 min |

**Goal**: Understand status, manage timeline, coordinate handoffs.

---

### 🔬 ETL/Data Engineer
**Priority: AS NEEDED**

| Order | Document | Purpose | Time |
|-------|----------|---------|------|
| 1 | `developer_handoffs/etl_dev/README.md` | Overview | 10 min |
| 2 | `docs/ETL_DATA_ENGINEER_HANDOFF.md` | Full handoff | 1 hr |
| 3 | `docs/STATS_REFERENCE_COMPLETE.md` | All stats formulas | Reference |
| 4 | `src/main.py`, `src/pipeline/` | Core ETL code | As needed |

**Goal**: Maintain ETL, add new stats, process new games.

---

## 🗺️ Recommended Work Order

```
PHASE 0: FIX BLOCKING ISSUES (1-2 days)
├── Supabase Dev: Fix 18 schema mismatches
├── Supabase Dev: Add video highlight tables
├── Supabase Dev: Verify all 98 tables load
└── Milestone: `bulletproof_loader.py --load all` = 0 failures

PHASE 1: CODE HARDENING (1 week)
├── Sr. Engineer: Review bulletproof_loader.py
├── Sr. Engineer: Add integration tests
├── Sr. Engineer: Refactor src/main.py
└── Milestone: 80% test coverage, CI pipeline

PHASE 2: TRACKER MVP (2-3 weeks)
├── Tracker Dev: Build React app
├── Tracker Dev: Event entry UI
├── Tracker Dev: Shift tracking
├── Tracker Dev: Video highlight clipping
└── Milestone: Can track a full game

PHASE 3: DASHBOARD MVP (2-3 weeks, can parallel)
├── Dashboard Dev: Build React app
├── Dashboard Dev: Player profiles
├── Dashboard Dev: Game box scores
├── Dashboard Dev: Leaderboards
└── Milestone: Players can view their stats

PHASE 4: PORTAL & POLISH (2-3 weeks)
├── Portal Dev: Admin tools
├── All: Bug fixes, polish
└── Milestone: Full system operational
```

---

## 🔑 Key Commands

```bash
# Check what's loaded in Supabase
python scripts/bulletproof_loader.py --status

# Load missing tables
python scripts/bulletproof_loader.py --load missing

# Run ETL for a game
./run_etl.sh --game 18969

# Run tests
python -m pytest tests/ -v
```

---

## 📁 Project Structure

```
benchsight/
├── README.md                    ← YOU ARE HERE
├── developer_handoffs/          ← Role-specific packages
│   ├── code_review/            
│   ├── dashboard_dev/          
│   ├── etl_dev/                
│   ├── portal_dev/             
│   ├── product_manager/        
│   ├── supabase_dev/           
│   └── tracker_dev/            
├── docs/                        ← All documentation
│   ├── SUPABASE_SCHEMA_ISSUES.md  ← CURRENT BLOCKERS
│   ├── TRACKER_DATA_FORMAT.md     ← Tracker column specs
│   ├── WIREFRAMES_AND_PAGES.md    ← UI designs
│   └── ...
├── sql/                         ← Database schemas
├── scripts/                     ← Utility scripts
├── src/                         ← ETL source code
├── tests/                       ← Test suite
├── data/                        ← Data files
├── dashboard/                   ← Dashboard prototype
├── tracker/                     ← Tracker prototype
└── portal/                      ← Portal prototype
```

---

## ❓ Questions?

| Question | Who to Ask |
|----------|------------|
| Product direction, priorities | Product Manager |
| Schema issues, Supabase | Supabase Dev |
| ETL bugs, data issues | ETL/Data Engineer |
| Code quality, architecture | Sr. Engineer |
| Stats formulas, calculations | ETL/Data Engineer |


---

## 📋 Complete Table List

See `docs/TABLE_REFERENCE_COMPLETE.md` for all 98 tables with:
- Primary keys
- Row counts
- Descriptions
- Column counts

### Quick Count

| Category | Tables |
|----------|--------|
| Dimensions | 44 |
| Facts | 51 |
| QA | 1 |
| Video (new) | 2 |
| **Total** | **98** |
