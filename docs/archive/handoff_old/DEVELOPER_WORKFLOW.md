# BenchSight Developer Workflow & Timeline (4 Roles)

## Overview

This document provides the recommended approach for developing BenchSight across **four workstreams**: 
1. **Supabase** - Database deployment
2. **Portal** - Admin UI for ETL and management
3. **Tracker** - Game data entry
4. **Dashboard** - Analytics visualization

---

## Complete Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           BENCHSIGHT DATA FLOW                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

                                    ┌──────────┐
                                    │  PORTAL  │
                                    │ (Admin)  │
                                    └────┬─────┘
                                         │
         Run ETL, Upload/Download, Validate, Monitor
                                         │
                                         ▼
┌─────────────┐              ┌────────────────────┐              ┌─────────────┐
│   TRACKER   │ ──WRITE────► │     SUPABASE       │ ◄──READ───── │  DASHBOARD  │
│ (Data Entry)│              │    PostgreSQL      │              │ (Analytics) │
└─────────────┘              │                    │              └─────────────┘
      │                      │  ┌──────────────┐  │                     │
      │                      │  │ fact_events  │  │                     │
      │                      │  │ fact_shifts  │  │                     │
      │                      │  │ fact_*_stats │  │                     │
      │                      │  │ dim_*        │  │                     │
      │                      │  └──────────────┘  │                     │
      │                      └────────────────────┘                     │
      │                               │                                 │
      │                               │                                 │
      └───────────────────────────────┼─────────────────────────────────┘
                                      │
                              ┌───────┴───────┐
                              │   ETL PYTHON  │
                              │   SCRIPTS     │
                              │ (via Portal)  │
                              └───────────────┘
```

---

## Dependency Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  SUPABASE   │ ──► │   PORTAL    │ ──► │   TRACKER   │ ──► │  DASHBOARD  │
│ (Foundation)│     │(Admin Tools)│     │ (Data Entry)│     │  (Display)  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                   │
      ▼                   ▼                   ▼                   ▼
 Tables exist        Can run ETL         Can write to DB    Can read stats
 Schema deployed     Manage tables       Events flow thru   Users see value
 APIs available      View logs           ETL validated      Analytics work
```

**Key Dependencies:**
- **Supabase** must be done first - everything depends on it
- **Portal** should come second - needed to run ETL and validate
- **Tracker** and **Dashboard** can run in parallel after Portal MVP
- **Dashboard** benefits from Tracker data but can work with existing data

---

## Recommended Approach: 4-Phase Development

### Phase 1: Supabase Foundation (Week 1)
**Single chat session | BLOCKING**

| Day | Task |
|-----|------|
| 1-2 | Create all 12 tables with proper types |
| 2-3 | Load existing CSV data from ETL |
| 3-4 | Add indexes, validate FK relationships |
| 4-5 | Test queries, document connection strings |

**Supabase is "done" when:**
- [ ] All 12 tables exist
- [ ] Existing data loaded
- [ ] Indexes created
- [ ] Test queries work
- [ ] Connection documented

---

### Phase 2: Portal MVP (Week 2)
**Single chat session | Important for automation**

| Day | Task |
|-----|------|
| 1-2 | Backend: FastAPI with script execution |
| 2-3 | Backend: WebSocket log streaming |
| 3-4 | Frontend: ETL control panel |
| 4-5 | Frontend: Table viewer + validation display |

**Portal MVP is "done" when:**
- [ ] Can run ETL from UI
- [ ] See real-time log output
- [ ] View table row counts
- [ ] See validation results

---

### Phase 3: Tracker + Dashboard in Parallel (Weeks 3-4)
**Two separate parallel chats**

```
TRACKER CHAT                    DASHBOARD CHAT
─────────────                   ──────────────
Week 3:                         Week 3:
├─ Fix roster loading           ├─ Build standings page
├─ Fix game dropdown            ├─ Build leaders page
├─ Fix event ordering           ├─ Set up Supabase client
├─ Implement Supabase writes    ├─ Team overview
│                               │
Week 4:                         Week 4:
├─ Add edit/delete              ├─ Player stats
├─ Test event → DB flow         ├─ Game summary
├─ Validate ETL results         ├─ Goalie stats
└─ Polish UI                    └─ Mobile responsive
```

---

### Phase 4: Integration & Advanced (Week 5+)
**Combined or separate chats**

| Task | Owner |
|------|-------|
| Track game → see in dashboard | Tracker + Dashboard |
| Portal runs post-game ETL | Portal |
| XY coordinate capture | Tracker |
| Advanced analytics (H2H, WOWY) | Dashboard |
| Automated ETL scheduling | Portal |

---

## Chat Strategy for 4 Roles

### Overview
| Phase | Chats | Focus |
|-------|-------|-------|
| **Week 1** | 1 (Supabase) | Database foundation |
| **Week 2** | 1 (Portal) | Admin automation |
| **Weeks 3-4** | 2 parallel (Tracker + Dashboard) | Features |
| **Week 5+** | 1-2 (Integration) | Connect & polish |

### Why Separate Chats
- **Supabase:** SQL-focused, schema design
- **Portal:** Python backend, React frontend
- **Tracker:** HTML/JS, event logic, game tracking
- **Dashboard:** React/Vue, visualization, queries

Different mental models, different contexts.

---

## Detailed Timeline

```
WEEK 1: SUPABASE ════════════════════════════════════════════════════
├── Mon-Tue: Create tables (run DDL scripts)
├── Wed: Load data (dims first, then facts)
├── Thu: Add indexes, validate FKs
└── Fri: Test queries, document, handoff

WEEK 2: PORTAL ══════════════════════════════════════════════════════
├── Mon: Set up FastAPI backend
├── Tue: Script execution + log streaming
├── Wed: Frontend - ETL control panel
├── Thu: Frontend - Table viewer
└── Fri: Validation display, test full flow

WEEK 3: TRACKER + DASHBOARD (PARALLEL) ══════════════════════════════
│
├── TRACKER:
│   ├── Mon: Debug roster loading
│   ├── Tue: Fix game dropdown
│   ├── Wed: Fix event ordering
│   ├── Thu: Implement Supabase writes
│   └── Fri: Test event flow
│
└── DASHBOARD:
    ├── Mon: Supabase client setup
    ├── Tue: Standings page
    ├── Wed: Leaders page
    ├── Thu: Team overview
    └── Fri: Player stats (start)

WEEK 4: TRACKER + DASHBOARD (CONTINUE) ══════════════════════════════
│
├── TRACKER:
│   ├── Mon-Tue: Edit/delete functionality
│   ├── Wed: Polish UI
│   ├── Thu: Run ETL via Portal
│   └── Fri: Full integration test
│
└── DASHBOARD:
    ├── Mon: Player stats (finish)
    ├── Tue: Game summary
    ├── Wed: Goalie stats
    ├── Thu: Mobile responsive
    └── Fri: Integration test

WEEK 5: INTEGRATION ═════════════════════════════════════════════════
├── Mon-Wed: End-to-end testing
│   └── Track game → Portal ETL → Dashboard shows stats
├── Thu: Bug fixes
└── Fri: Demo / Deploy
```

---

## Quick Start for Each Role

### Supabase Developer
```
1. Read: developer_handoffs/supabase_dev/README.md
2. Run: sql/01_create_tables.sql
3. Load: CSVs from data/output/
4. Validate: sql/05_validate_data.sql
```

### Portal Developer
```
1. Read: developer_handoffs/portal_dev/README.md
2. Build: FastAPI backend with subprocess execution
3. Build: Frontend with WebSocket log viewer
4. Test: Run ETL, view tables
```

### Tracker Developer
```
1. Read: developer_handoffs/tracker_dev/README.md
2. Fix: Roster loading, game dropdown
3. Implement: Supabase writes
4. Test: Event → DB → ETL → Stats
```

### Dashboard Developer
```
1. Read: developer_handoffs/dashboard_dev/README.md
2. Connect: Supabase client
3. Build: Standings → Leaders → Team → Player → Game
4. Test: Data displays correctly
```

---

## Handoff Package Locations

```
developer_handoffs/
├── DEVELOPER_WORKFLOW.md        ← This file (workflow for all)
│
├── supabase_dev/
│   ├── README.md               ← Start here
│   ├── NEXT_PROMPT.md          ← Copy-paste prompt
│   ├── sql/                    ← DDL scripts
│   ├── docs/                   ← Schema, rules
│   └── data_dictionary/        ← Column definitions
│
├── portal_dev/
│   ├── README.md               ← Start here
│   ├── NEXT_PROMPT.md          ← Copy-paste prompt
│   ├── docs/                   ← Architecture, API specs
│   └── templates/              ← UI mockups
│
├── tracker_dev/
│   ├── README.md               ← Start here
│   ├── NEXT_PROMPT.md          ← Copy-paste prompt
│   ├── tracker_v19.html        ← Current tracker
│   ├── docs/                   ← Event logic guide
│   └── data_dictionary/        ← Column definitions
│
└── dashboard_dev/
    ├── README.md               ← Start here
    ├── NEXT_PROMPT.md          ← Copy-paste prompt
    ├── docs/                   ← Dashboard specs
    └── data_dictionary/        ← Column definitions
```

---

## Success Milestones

### Week 1 Complete (Supabase)
- [ ] 12 tables created
- [ ] Data loaded, validated
- [ ] Indexes created
- [ ] Queries work

### Week 2 Complete (Portal)
- [ ] ETL runs from UI
- [ ] Logs stream in real-time
- [ ] Tables viewable
- [ ] Validation results display

### Week 3 Complete (Parallel Start)
- [ ] Tracker: Roster + dropdown fixed
- [ ] Tracker: Events write to Supabase
- [ ] Dashboard: Standings + leaders work
- [ ] Dashboard: Team overview works

### Week 4 Complete (Parallel Continue)
- [ ] Tracker: Edit/delete works
- [ ] Tracker: Full event flow tested
- [ ] Dashboard: All pages complete
- [ ] Dashboard: Mobile responsive

### Week 5 Complete (Integration)
- [ ] End-to-end flow works
- [ ] All components communicate
- [ ] No critical bugs
- [ ] Ready for real use

---

*Document Version: 2.0 | Updated: December 2024 | Now includes Portal role*
