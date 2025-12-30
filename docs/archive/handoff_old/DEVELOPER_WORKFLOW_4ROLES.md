# BenchSight Developer Workflow - 4 Roles

## Overview

BenchSight development involves 4 distinct workstreams. This document provides the recommended approach for coordinating all four.

---

## The Four Roles

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        BENCHSIGHT DEVELOPMENT ROLES                           │
└──────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  SUPABASE   │    │   PORTAL    │    │   TRACKER   │    │  DASHBOARD  │
│    DEV      │    │    DEV      │    │     DEV     │    │     DEV     │
├─────────────┤    ├─────────────┤    ├─────────────┤    ├─────────────┤
│ Database    │    │ Admin UI    │    │ Game entry  │    │ Stats       │
│ Schema      │    │ ETL control │    │ Event track │    │ Display     │
│ Tables      │    │ Monitoring  │    │ Write to DB │    │ Read from   │
│ APIs        │    │ Uploads     │    │             │    │ DB          │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       │ FOUNDATION       │ ORCHESTRATION    │ DATA INPUT       │ DATA OUTPUT
       │                  │                  │                  │
       └──────────────────┴──────────────────┴──────────────────┘
                                   │
                           ┌───────▼───────┐
                           │   SUPABASE    │
                           │   DATABASE    │
                           └───────────────┘
```

---

## Dependency Map

```
                        ┌─────────────┐
                        │  SUPABASE   │  ◄── MUST BE FIRST
                        │   (Week 1)  │
                        └──────┬──────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │   PORTAL    │     │   TRACKER   │     │  DASHBOARD  │
    │  (Week 2-3) │     │  (Week 2-3) │     │  (Week 2-3) │
    └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
           │                   │                   │
           │ needs DB to       │ needs DB to       │ needs DB to
           │ monitor/manage    │ write events      │ read stats
           │                   │                   │
           └───────────────────┴───────────────────┘
                               │
                        ┌──────▼──────┐
                        │ INTEGRATION │
                        │  (Week 4)   │
                        └─────────────┘
```

**Key Insight:** 
- Supabase is blocking for ALL other roles
- Portal, Tracker, Dashboard can run in PARALLEL after Supabase
- Portal enables easier ETL/monitoring but isn't blocking for Tracker/Dashboard

---

## Recommended Timeline

### Week 1: Foundation (Supabase Only)

```
SUPABASE DEV
├── Mon-Tue: Create all 12 tables with DDL
├── Wed: Load existing CSV data
├── Thu: Validate data, fix FK issues
└── Fri: Create indexes, test queries, HANDOFF

Deliverable: Working database with data loaded
Checkpoint: Dashboard dev can query, Tracker dev can write
```

### Week 2-3: Parallel Development

```
                 WEEK 2                           WEEK 3
                 ──────                           ──────

PORTAL DEV       ┌─────────────────────┐         ┌─────────────────────┐
                 │ Set up FastAPI      │         │ File upload         │
                 │ ETL run endpoint    │         │ Validation dashboard│
                 │ Table viewer        │         │ Real-time logs      │
                 └─────────────────────┘         └─────────────────────┘

TRACKER DEV      ┌─────────────────────┐         ┌─────────────────────┐
                 │ Fix roster loading  │         │ Add edit/delete     │
                 │ Fix game dropdown   │         │ Test Supabase writes│
                 │ Fix event ordering  │         │ Validate ETL flow   │
                 └─────────────────────┘         └─────────────────────┘

DASHBOARD DEV    ┌─────────────────────┐         ┌─────────────────────┐
                 │ Standings page      │         │ Team overview       │
                 │ Leaders page        │         │ Player stats        │
                 │ Supabase client     │         │ Game summary        │
                 └─────────────────────┘         └─────────────────────┘

Friday Syncs: Check integration points work
```

### Week 4: Integration

```
ALL DEVS
├── Mon-Tue: End-to-end testing
│   └── Track game → ETL (via Portal) → Dashboard shows stats
├── Wed: Bug fixes
├── Thu: Polish
└── Fri: Demo / Deploy

Integration Tests:
□ Tracker writes event → appears in Portal table viewer
□ Portal runs ETL → Dashboard shows updated stats
□ New game uploaded → Full flow works
□ Validation catches errors → Portal displays them
```

---

## Chat Strategy

### Use Separate Chats (Recommended)

```
CHAT 1: Supabase Dev
└── Use: developer_handoffs/supabase_dev/NEXT_PROMPT.md

CHAT 2: Portal Dev
└── Use: developer_handoffs/portal_dev/NEXT_PROMPT.md

CHAT 3: Tracker Dev
└── Use: developer_handoffs/tracker_dev/NEXT_PROMPT.md

CHAT 4: Dashboard Dev
└── Use: developer_handoffs/dashboard_dev/NEXT_PROMPT.md
```

**Why separate:**
- Each role has different context needs
- Easier to hand off to different people
- Less context pollution
- Can work in parallel without conflicts

### If Solo (One Person)

Cycle through chats based on dependencies:

```
Week 1:
├── Day 1-2: Supabase chat - create tables
├── Day 3: Supabase chat - load data
├── Day 4-5: Supabase chat - validate, indexes

Week 2:
├── Day 1: Portal chat - backend setup
├── Day 2: Tracker chat - fix roster
├── Day 3: Dashboard chat - standings
├── Day 4: Portal chat - table viewer
├── Day 5: Tracker chat - event ordering

Week 3:
├── Day 1: Dashboard chat - player stats
├── Day 2: Portal chat - ETL control
├── Day 3: Tracker chat - Supabase writes
├── Day 4: Dashboard chat - game summary
├── Day 5: Integration testing (any chat)
```

---

## Role Responsibilities

### Supabase Dev
```
CREATES:
├── All database tables (DDL)
├── Indexes for performance
├── Foreign key constraints
├── Staging tables for tracker writes

VALIDATES:
├── Data loaded correctly
├── No FK violations
├── Queries return expected results

HANDS OFF:
├── Connection strings to all other devs
├── Table schemas documented
└── Sample queries that work
```

### Portal Dev
```
CREATES:
├── Admin web interface
├── Backend API for script execution
├── ETL control panel
├── Table viewer/editor
├── Validation dashboard
├── File upload handlers
├── Health monitoring

ENABLES:
├── Non-technical ETL execution
├── Data browsing without SQL
├── Easy validation checks
└── System monitoring
```

### Tracker Dev
```
CREATES:
├── Game tracking interface
├── Event entry forms
├── Shift management
├── Supabase write functions
├── XY coordinate capture (future)

WRITES TO:
├── staging_events (or fact_events)
├── staging_shifts (or fact_shifts)

MUST UNDERSTAND:
├── Event types and validation
├── Player role logic (event_team_player_1 = stat credit)
├── Primary key generation
└── Linked event patterns
```

### Dashboard Dev
```
CREATES:
├── League standings
├── Player stats pages
├── Team analytics
├── Game summaries
├── Goalie stats
├── Advanced analytics (H2H, WOWY)

READS FROM:
├── fact_player_game_stats
├── fact_team_game_stats
├── fact_goalie_game_stats
├── fact_events (for timeline)
├── dim_* tables

MUST UNDERSTAND:
├── Stat calculations
├── Supabase query patterns
└── Mobile responsiveness
```

---

## Data Flow (Full Picture)

```
┌─────────────┐
│   TRACKER   │
│  (HTML/JS)  │
└──────┬──────┘
       │ WRITES (real-time)
       │
       ▼
┌─────────────────────┐
│  staging_events     │◄─── Tracker writes here
│  staging_shifts     │
└──────────┬──────────┘
           │
           │ PORTAL triggers
           ▼
┌─────────────────────┐
│    ETL PIPELINE     │
│  (Python scripts)   │
│                     │
│  etl.py             │
│  fix_data_integrity │
│  fix_final_data     │
│  etl_validation     │
└──────────┬──────────┘
           │ TRANSFORMS
           ▼
┌─────────────────────┐
│    FACT TABLES      │
│                     │
│  fact_events        │
│  fact_player_stats  │
│  fact_team_stats    │
│  fact_goalie_stats  │
│  fact_h2h           │
│  fact_wowy          │
└──────────┬──────────┘
           │ READS
           ▼
┌─────────────────────┐
│     DASHBOARD       │
│    (React/Vue)      │
└─────────────────────┘

┌─────────────────────┐
│       PORTAL        │  ◄── Monitors/controls everything
│    (Admin UI)       │
└─────────────────────┘
```

---

## Handoff Package Locations

```
developer_handoffs/
├── DEVELOPER_WORKFLOW_4ROLES.md    ← THIS FILE
├── SUPABASE_WRITE_STRATEGY.md      ← Data flow architecture
│
├── supabase_dev/
│   ├── README.md                   ← Start here
│   ├── NEXT_PROMPT.md              ← Copy-paste prompt
│   ├── sql/                        ← DDL scripts
│   ├── docs/                       ← Schema, rules
│   └── data_dictionary/            ← Column defs
│
├── portal_dev/
│   ├── README.md                   ← Start here
│   ├── NEXT_PROMPT.md              ← Copy-paste prompt
│   └── docs/                       ← Requirements
│
├── tracker_dev/
│   ├── README.md                   ← Start here
│   ├── NEXT_PROMPT.md              ← Copy-paste prompt
│   ├── tracker_v19.html            ← Current tracker
│   ├── docs/                       ← Event logic guide
│   └── data_dictionary/            ← Column defs
│
└── dashboard_dev/
    ├── README.md                   ← Start here
    ├── NEXT_PROMPT.md              ← Copy-paste prompt
    ├── docs/                       ← Dashboard specs
    └── data_dictionary/            ← Column defs
```

---

## Success Milestones

### Week 1 ✅
- [ ] Supabase: 12 tables created
- [ ] Supabase: All CSV data loaded
- [ ] Supabase: Indexes created
- [ ] Supabase: Test queries work

### Week 2 ✅
- [ ] Portal: ETL run endpoint works
- [ ] Portal: Table viewer displays data
- [ ] Tracker: Roster loads reliably
- [ ] Tracker: Games appear in dropdown
- [ ] Dashboard: Standings page live
- [ ] Dashboard: Leaders page live

### Week 3 ✅
- [ ] Portal: File upload works
- [ ] Portal: Validation dashboard
- [ ] Tracker: Edit/delete works
- [ ] Tracker: Writes to Supabase
- [ ] Dashboard: Player/Team pages
- [ ] Dashboard: Game summary

### Week 4 ✅
- [ ] Full end-to-end flow works
- [ ] Track → ETL → Display verified
- [ ] No critical bugs
- [ ] Ready for production use

---

## Quick Start Commands

**Start Supabase Work:**
```
Open new chat
Copy: developer_handoffs/supabase_dev/NEXT_PROMPT.md
```

**Start Portal Work (after Supabase):**
```
Open new chat
Copy: developer_handoffs/portal_dev/NEXT_PROMPT.md
```

**Start Tracker Work (after Supabase):**
```
Open new chat
Copy: developer_handoffs/tracker_dev/NEXT_PROMPT.md
```

**Start Dashboard Work (after Supabase):**
```
Open new chat
Copy: developer_handoffs/dashboard_dev/NEXT_PROMPT.md
```

---

*Document Version: 2.0 | Last Updated: December 2024*
