# BenchSight Project Summary & Roadmap

**Comprehensive Overview of Vision, Current State, and Path Forward**

Last Updated: 2026-01-13  
Based on: ROADMAP.md (v24.4), STRATEGIC_ROADMAP.md (v29.0), DASHBOARD_ANALYTICS_VISION.md (v1.0)

---

## 🎯 Vision Statement

**Build a full-stack hockey analytics platform that:**
1. **Makes game tracking fast and easy** - Reduces tracking time from 8 hours to 1 hour
2. **Provides comprehensive analytics** - Advanced stats for players, teams, and leagues
3. **Automates tracking through ML/CV** - Computer vision for play detection and event recognition
4. **Scales to commercial SaaS** - Multi-tenant platform for junior hockey teams

**Target Users:**
- Junior hockey teams and leagues
- Coaches and team managers
- Players and parents
- Analysts and scouts

---

## 📊 Current State Assessment

### ✅ What Exists (Strong Foundation)

#### 1. **ETL Pipeline** (85% Complete - Phase 0.75)
- **Status:** Production-ready, validated
- **Output:** 139 tables (50 dimensions, 81 facts, 8 QA)
- **Data Quality:** Core tables validated, goal counting accurate
- **Performance:** ~80 seconds for 4 games
- **Location:** Python-based ETL system
- **Key Features:**
  - Comprehensive stats (317 columns for players, 128 for goalies)
  - Advanced metrics (Corsi, Fenwick, xG, WAR/GAR, QoC/QoT)
  - 30 pre-aggregated views for dashboard consumption
  - Validation framework

**What's Missing:**
- Web API to trigger ETL
- Performance optimization (vectorization needed)
- Code refactoring (base_etl.py is 4,400 lines - needs modularization)

#### 2. **Tracker Application** (70% Complete)
- **Status:** Functional prototype (v23.5)
- **Location:** `ui/tracker/tracker_index_v23.5.html`
- **Features:**
  - Video playback support (multiple angles)
  - Event tracking (shots, goals, passes, faceoffs, etc.)
  - XY positioning on rink
  - Shift tracking
  - Export to Excel
  - Comprehensive event types

**What's Missing:**
- Integration with full stack (standalone HTML)
- Authentication/user management
- Cloud persistence (local storage only)
- Real-time sync
- ML/CV integration

#### 3. **Dashboard** (50% Complete)
- **Status:** Foundation built, needs content
- **Location:** `ui/dashboard/` (Next.js 14, TypeScript, Tailwind, Supabase)
- **Features:**
  - Connected to Supabase
  - Basic pages (standings, leaderboards, players, teams)
  - Design system and component library
  - Prototype workflow

**What's Missing:**
- Many pages are placeholders
- Limited visualizations (charts, graphs, shot maps)
- User authentication
- Production deployment
- Advanced analytics pages (per DASHBOARD_ANALYTICS_VISION.md)

#### 4. **Admin Portal** (10% Complete)
- **Status:** UI mockup only
- **Location:** `ui/portal/index.html`
- **Features:**
  - Modern UI design (dark theme, cyberpunk aesthetic)
  - ETL control interface mockup
  - Game management UI mockup
  - Data browser mockup

**What's Missing:**
- **NO BACKEND** - Just HTML/CSS/JS
- **NO ETL API** - Can't actually trigger ETL
- **NO AUTHENTICATION** - No user management
- **NO REAL FUNCTIONALITY** - All buttons are placeholders

#### 5. **ML/CV Integration** (0% Complete)
- **Status:** Not started
- **Needs:**
  - Video processing pipeline
  - Object detection (puck, players, net)
  - Play recognition (shots, goals, passes)
  - Automated event detection
  - Integration with tracker

---

## 🗺️ Roadmap Overview

### Two Roadmap Perspectives

The project has **two complementary roadmaps**:

1. **ROADMAP.md (v24.4)** - Detailed technical phases (0-5)
   - Currently at **Phase 0.75: Stats Expansion** (85% complete)
   - Focus: Technical debt, data completeness, MVP preparation

2. **STRATEGIC_ROADMAP.md (v29.0)** - 16-week commercial launch plan
   - Focus: Integration, deployment, ML/CV, commercialization
   - Phases: Integration → Dashboard → ML/CV → Commercial

### Current Phase: **Phase 0.75 - Stats Expansion** (85% Complete)

**Completed:**
- ✓ Advanced goalie stats (39→128 columns)
- ✓ Macro stats tables (8 new tables)
- ✓ View layer (30 views for dashboard)
- ✓ 139 ETL tables, validated

**Remaining:**
- ☐ Performance optimization (vectorization)
- ☐ base_etl.py refactoring

---

## 🎯 Strategic Roadmap (16-Week Plan)

### Phase 1: Integration & Automation (Weeks 1-4)
**Goal:** Make existing components work together seamlessly

**Key Tasks:**
- **Week 1-2: ETL API**
  - Build FastAPI backend (`api/` directory)
  - REST endpoints: `/api/etl/trigger`, `/api/etl/status`, `/api/games`
  - Job queue (Celery or async queue)
  - Integration with existing ETL

- **Week 2-3: Admin Portal Backend**
  - Connect UI to ETL API
  - Game management (list, create, update, delete)
  - Basic authentication (password protection)

- **Week 3-4: Tracker Integration**
  - Cloud persistence (Supabase)
  - Authentication
  - Auto-save functionality
  - Real-time sync (future)

**Success Criteria:**
- [ ] Track game → Click "Run ETL" → See stats in dashboard (< 5 min)
- [ ] Admin portal fully functional
- [ ] Tracker saves to cloud automatically
- [ ] End-to-end workflow works

---

### Phase 2: Dashboard & Polish (Weeks 5-8)
**Goal:** Production-ready public dashboard

**Key Tasks:**
- **Week 5-6: Complete Dashboard Pages**
  - Leaderboards (points, goals, assists, advanced metrics)
  - Player profiles (career stats, game log, trends, charts)
  - Team pages (roster, season stats, head-to-head, schedule)
  - Game pages (box score, scoring summary, shot chart, play-by-play)
  - Visualizations (Recharts, shot maps, performance trends)

- **Week 6-7: Authentication & Roles**
  - Supabase Auth integration
  - Role-based access (public, admin, scorer, team manager)
  - Protected routes

- **Week 7-8: Deployment**
  - Vercel deployment (dashboard)
  - Railway/Render deployment (API)
  - Domain setup
  - Monitoring (Sentry, analytics)

**Success Criteria:**
- [ ] Dashboard live and public
- [ ] All pages functional
- [ ] Authentication working
- [ ] Fast, responsive, polished

---

### Phase 3: ML/CV Foundation (Weeks 9-12)
**Goal:** Automated tracking foundation

**Key Tasks:**
- **Week 9-10: Video Processing Pipeline**
  - Video storage (Cloudflare R2 or AWS S3)
  - Frame extraction
  - Basic object detection (puck, players, net)

- **Week 10-11: Play Detection**
  - Shot detection
  - Goal detection
  - Pass detection
  - Event classification

- **Week 11-12: ML Integration**
  - ML suggestions in tracker
  - Human verification workflow
  - Confidence scoring
  - Learning from corrections

**Success Criteria:**
- [ ] ML detects 80%+ of shots correctly
- [ ] Tracking time reduced by 50%
- [ ] Human verification smooth
- [ ] System learns from corrections

---

### Phase 4: Commercialization (Weeks 13-16)
**Goal:** Multi-tenant SaaS ready for customers

**Key Tasks:**
- **Week 13-14: Multi-Tenancy**
  - League isolation (row-level security)
  - Tenant management UI
  - Data segregation

- **Week 14-15: Advanced Features**
  - Advanced analytics
  - Team management
  - Communication (email, in-app messaging)

- **Week 15-16: Launch Prep**
  - Documentation (user guides, API docs)
  - Onboarding flow
  - Support system
  - Marketing materials

**Success Criteria:**
- [ ] 3+ leagues using system
- [ ] Paying customers
- [ ] System stable at scale
- [ ] Support system functional

---

## 📋 Detailed Roadmap (ROADMAP.md Phases)

### Phase 0: Foundation ✓ (COMPLETE)
- ETL pipeline (52 tables)
- Validation framework
- Documentation

### Phase 0.5: Data Validation ✓ (COMPLETE)
- All Tier 1 tables validated
- Goal counting verified (17 goals match source)
- Venue mapping verified

### Phase 0.75: Stats Expansion ← **CURRENT** (85% Complete)
**Goal:** Comprehensive stats before building dashboard

**Completed:**
- ✓ Advanced goalie stats (128 columns)
- ✓ Macro stats tables
- ✓ View layer (30 views)

**Remaining:**
- ☐ Performance optimization
- ☐ base_etl.py refactoring

### Phase 1: MVP (Weeks 1-2)
**Goal:** Working system end-to-end

**Tasks:**
- Create `raw_events` and `raw_shifts` tables
- Tracker "Publish to Supabase" functionality
- ETL `--source supabase` flag
- Basic dashboard HTML

### Phase 2: Alpha (Weeks 3-4)
**Goal:** Deployable, shareable prototype

**Tasks:**
- Deploy to Vercel (frontend)
- Deploy ETL to Railway (backend API)
- Domain setup
- Supabase Auth
- Admin "Run ETL" button

### Phase 3: Beta (Weeks 5-8)
**Goal:** Multi-user, polished, feedback-ready

**Features:**
- User management
- Game management
- Player profiles
- Team pages
- Leaderboards
- Charts/visualizations
- Auto-save tracker

### Phase 4: Commercial (Weeks 9-12)
**Goal:** Ready for paying customers

**Features:**
- Multi-tenancy (league isolation)
- Self-service signup
- Stripe integration
- Error monitoring
- Mobile responsive

### Phase 5: Growth (Ongoing)
**Future Features:**
- Mobile app
- Video integration (LiveBarn, GameSheet)
- AI insights
- API access
- White-label options

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    BENCHSIGHT PLATFORM                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Tracker    │  │   Dashboard  │  │ Admin Portal │     │
│  │  (HTML/JS)   │  │  (Next.js)   │  │  (HTML/JS)   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            │                                │
│                  ┌─────────▼─────────┐                      │
│                  │   REST API (FastAPI)                      │
│                  │   - ETL endpoints                         │
│                  │   - Game management                       │
│                  │   - Authentication                        │
│                  └─────────┬─────────┘                      │
│                            │                                │
│                  ┌─────────▼─────────┐                      │
│                  │     Supabase      │                      │
│                  │   - PostgreSQL    │                      │
│                  │   - 139 tables    │                      │
│                  │   - 30 views      │                      │
│                  │   - Auth          │                      │
│                  └─────────┬─────────┘                      │
│                            │                                │
│                  ┌─────────▼─────────┐                      │
│                  │   Python ETL      │                      │
│                  │   - 139 tables    │                      │
│                  │   - Validation    │                      │
│                  └───────────────────┘                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Future: ML/CV Service (separate deployment)
- Video processing
- Object detection
- Play recognition
- Integration via API
```

---

## 🎨 Dashboard Vision (Per DASHBOARD_ANALYTICS_VISION.md)

**Comprehensive dashboard utilizing ALL 139 tables + 30 views:**

### Pages to Build (50+ pages)

**Players:**
- Player Directory
- Player Profile (individual)
- Player Comparison (2+ players)
- Player Search & Filters
- Player Trends

**Goalies:**
- Goalie Directory
- Goalie Profile
- Goalie Comparison
- Goalie Advanced Metrics
- Goalie Performance Trends

**Teams:**
- Team Directory
- Team Profile
- Team Comparison
- Team Line Combinations
- Team Zone Time Analysis
- Team Matchups (H2H)

**Games:**
- Game Center (Live)
- Game Recap
- Game Boxscore
- Play-by-Play
- Shift Charts
- Shot Maps
- Game Analytics

**Analytics:**
- Advanced Metrics Hub
- xG Analysis
- WAR/GAR Leaders
- RAPM Analysis (future)
- Micro Stats Explorer
- Zone Entry/Exit Analysis
- Rush Analysis
- Faceoff Analysis

---

## ⚠️ Critical Technical Debt

### High Priority (Before Scaling)

1. **base_etl.py is 4,400 lines** - Needs modularization
   - Break into: `calculations/`, `builders/`, `core/`
   - Impact: Maintainability, onboarding

2. **Performance issues** - Iterrows/apply patterns everywhere
   - Solution: Vectorized operations
   - Impact: 4 games = fine, 100 games = hours

3. **No unit tests** - Zero test coverage
   - Impact: No confidence in changes
   - Solution: Test critical calculations

4. **Magic numbers everywhere** - Undocumented constants
   - Solution: Config file with documented constants

5. **Duplicate calculation logic** - Goal counting in 4+ places
   - Solution: Single source of truth

### Medium Priority (Before Phase 2)

6. **Empty placeholder tables** - 19 tables with 0 rows
7. **No FK validation** - Manual fixes only
8. **No logging** - Hard to debug
9. **Code refactoring** - Split large files

---

## 💰 Pricing Model (Future)

| Tier | Price | Includes |
|------|-------|----------|
| **Free** | $0 | 1 season, 10 games, 2 users |
| **Basic** | $19/mo | 2 seasons, 50 games, 10 users |
| **Pro** | $49/mo | Unlimited |
| **Enterprise** | Custom | Multi-league, API access |

---

## 🛠️ Technology Stack

### Current
- **Frontend (Dashboard):** Next.js 14, TypeScript, Tailwind CSS, Supabase
- **Frontend (Tracker/Portal):** HTML, CSS, JavaScript (vanilla)
- **Backend (ETL):** Python (pandas, numpy)
- **Database:** Supabase (PostgreSQL)
- **Storage:** Local files (tracking data)

### Planned
- **Backend API:** FastAPI (Python)
- **Job Queue:** Celery + Redis (or simple async queue)
- **Hosting:** Vercel (frontend), Railway/Render (API)
- **ML/CV:** PyTorch/TensorFlow, YOLO, OpenCV
- **Video Storage:** Cloudflare R2 or AWS S3
- **Payments:** Stripe
- **Monitoring:** Sentry, Vercel Analytics

---

## 📈 Success Metrics

### Phase 1 (Integration)
- ETL trigger time: < 30 seconds
- End-to-end workflow: < 5 minutes
- Admin portal uptime: > 99%

### Phase 2 (Dashboard)
- Dashboard load time: < 2 seconds
- All core pages functional
- User satisfaction: Survey

### Phase 3 (ML/CV)
- ML accuracy: > 80% for shots
- Tracking time reduction: > 50%
- Human verification rate: < 20%

### Phase 4 (Commercial)
- Active leagues: 3+
- Paying customers: 5+
- System uptime: > 99.9%
- Customer satisfaction: > 4/5

---

## 🚀 Immediate Next Steps

### This Week
1. **Complete Phase 0.75**
   - Performance optimization (vectorization)
   - base_etl.py refactoring planning

2. **Start Phase 1 Planning**
   - Decide on API framework (FastAPI recommended)
   - Set up API project structure
   - Create first endpoint (health check)

### Next Week
1. **Build ETL API**
   - ETL trigger endpoint
   - Status endpoints
   - Test end-to-end workflow

2. **Connect Admin Portal**
   - Replace mock functions with real API calls
   - Test ETL triggering from UI

---

## 📚 Key Documents Reference

| Document | Purpose | Status |
|----------|---------|--------|
| [ROADMAP.md](docs/ROADMAP.md) | Detailed technical phases (0-5) | v24.4 |
| [STRATEGIC_ROADMAP.md](docs/STRATEGIC_ROADMAP.md) | 16-week commercial plan | v29.0 |
| [DASHBOARD_ANALYTICS_VISION.md](docs/DASHBOARD_ANALYTICS_VISION.md) | Comprehensive dashboard strategy | v1.0 |
| [STRATEGIC_ASSESSMENT.md](docs/STRATEGIC_ASSESSMENT.md) | Current state analysis | v29.0 |
| [TODO.md](docs/TODO.md) | Current tasks and priorities | Updated weekly |

---

## 🎯 Summary

**Current State:** ~60% of way to end goal
- **Strong:** ETL pipeline, tracker prototype, dashboard foundation
- **Weak:** Admin portal (UI only), ML/CV (not started), integration (missing)

**Next Steps:**
1. Complete Phase 0.75 (performance + refactoring)
2. Build ETL API (Phase 1, Weeks 1-2)
3. Connect Admin Portal to backend (Phase 1, Weeks 2-3)
4. Deploy and polish Dashboard (Phase 2, Weeks 5-8)

**Timeline:** 16 weeks to commercial launch (per STRATEGIC_ROADMAP.md)

**Vision:** Full-stack hockey analytics platform that automates game tracking and provides comprehensive analytics for junior hockey teams, scaling to commercial SaaS.

---

*Last Updated: 2026-01-13*  
*Next Review: After Phase 0.75 completion*
